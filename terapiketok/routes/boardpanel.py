import datetime, uuid
from flask import Blueprint, render_template_string, render_template, request, redirect, url_for, session, flash
from flask_login import login_user, LoginManager, login_required, logout_user,current_user
from flask_bcrypt import Bcrypt
from ..models import Adminuser, Default_batch, Opening_message, Workingdays, Batches, Booking_tickets
from ..forms import RegisterForm, LoginAdminForm, DefaultBatchForm2, OpeningMessageForm, NewBatchForm, MultipleBatchesForm, NewDateForm, ChangeStatusForm, AddCustomerManualForm, CloseTicketButton, DeleteBatchesForm, MultipleDeleteForm, ConfirmDeleteForm
from ..services.data_processing import format_date_str, format_default_batch_time, get_queue_number
from terapiketok import app, bcrypt, db

from ..services.database import add_default_batch, update_default_batch, update_default_batch2, update_opening_message, add_new_batch, update_batch_status_by_batch, update_batch_status_by_date, add_customer_manually, fetct_queue_number, fetch_available_date_to_edit, update_and_add_new_batch, fetch_max_shifts, delete_batch_by_date_scheduleid, delete_batch_by_id
from ..services.database_renew import DatabaseProcess

boardpanel_bp = Blueprint('boardpanel', __name__, template_folder="../templates/boardpanel")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "boardpanel.adminlogin_page"
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return Adminuser.query.get(int(user_id))

@boardpanel_bp.before_request
def before_request():
    if current_user.is_authenticated:
        session.permanent = True  # Ensure session cookie is permanent
        db.session.refresh(current_user)  # Refresh user object from database
        session['user_id'] = current_user.user_id  # Update session data

@boardpanel_bp.route('/adminregister', methods=['GET', 'POST'])
def adminregister_page():
    text_header = "register"
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        if password == confirm_password:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = Adminuser(username=username, hashed_password=hashed_password)
            try:
                db.session.add(new_user)
                db.session.commit()
                flash("Registration successful!", category="success")
                return redirect(url_for("boardpanel.adminlogin_page"))
            except Exception as e:
                flash("Registration failed", category="danger")
        else:
            flash("password not match", category="danger")
    
    print(form.errors)

    return render_template('adminregister.html', text_header=text_header, form=form)

@boardpanel_bp.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin_page():
    text_header = "login"
    form = LoginAdminForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = Adminuser.query.filter_by(username=username).first()
        if user:
            if bcrypt.check_password_hash(user.hashed_password, password):
                
                login_user(user)
                return redirect(url_for('boardpanel.boardpanel_page'))

    return render_template('adminlogin.html', text_header=text_header, form=form)

@boardpanel_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout_page():
    logout_user()
    session.clear() # clear all session
    return redirect(url_for("boardpanel.adminlogin_page"))

@boardpanel_bp.route('/boardpanel', methods=['GET', 'POST'])
@login_required
def boardpanel_page():
    today = datetime.date.today()
    text_header = 'Dashboard'
    
    batches = Batches.query.filter(Batches.batch_date >= today).order_by(Batches.batch_date.asc(), Batches.schedule_id.asc()).all()

    return render_template('boardpanel.html', text_header=text_header, batches=batches)

@boardpanel_bp.route('/batches')
def batch_page():
    text_header = "Available Batches"
    return render_template('batches.html', text_header=text_header)

@boardpanel_bp.route('/newdate', methods=['GET', 'POST'])
@login_required
def newdate_page():
    form = NewDateForm()

    if form.validate_on_submit():
        session["target_batch_num"] = form.batches.data
        session["target_batch_date"] = form.batch_date.data
        return redirect(url_for('boardpanel.newbatch_page'))

    default_set = Default_batch.query.filter_by(default_batch_id=1).first()
    batches = default_set.number_of_batches
    new_date = datetime.date.today() + datetime.timedelta(days=1)
    
    return render_template('newdate.html', form=form, batches=batches, new_date=new_date)

@boardpanel_bp.route('/newbatch', methods=['GET', 'POST'])
@login_required
def newbatch_page():
    form = MultipleBatchesForm()

    target_batch_num = session.get("target_batch_num")
    target_batch_date_str = session.get("target_batch_date")
    if target_batch_date_str:
        # print(type(target_batch_date_str))
        formatted_date = format_date_str(target_batch_date_str)
        
    default_set = Default_batch.query.filter_by(default_batch_id=1).first()

    if form.validate_on_submit():
        def get_day_id(date_str):
            day_num = datetime.datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z").weekday()
            day_data = Workingdays.query.filter_by(day_num=day_num).first()
            return day_data.day_id

        for index, batch_form in enumerate(form.batches):
            schedule_id = index+1
            batch_date = formatted_date
            start_time = batch_form.start_time.data
            end_time = batch_form.end_time.data
            max_tickets = batch_form.capacity.data
            day_id = get_day_id(target_batch_date_str)

            count = add_new_batch(day_id, schedule_id, batch_date, start_time, end_time, max_tickets)
            if count > 0:
                flash(f"Add New Date on {formatted_date}", category="success")    
            else:
                flash("Failed to updated", category="warning")

        return redirect(url_for('boardpanel.boardpanel_page'))
    
    for num in range(target_batch_num):
        cur_batch_attr_start =f"batch{num+1}_start"
        cur_batch_attr_end =f"batch{num+1}_end"
        start_time = getattr(default_set, cur_batch_attr_start)
        end_time = getattr(default_set, cur_batch_attr_end)
        
        batch_form = NewBatchForm(
            start_time = start_time,
            end_time = end_time,
            capacity = default_set.capacity
        )
        form.batches.append_entry(batch_form.data)
    
    return render_template('newbatch.html', form=form, batches=target_batch_num, new_date=formatted_date, default_set=default_set, enumerate=enumerate)

@boardpanel_bp.route('/editoption/<action>', methods=['GET', 'POST'])
@login_required
def editoption_page(action):
    next_action = "delete"
    if action == "delete":
        next_action = "edit"
    today = datetime.date.today()
    start_date = datetime.date(year=2024, month=1, day=1)
    dates_to_edit = fetch_available_date_to_edit(start_date)

    return render_template('editoption.html', head_text=action, next_action=next_action, dates=dates_to_edit)

@boardpanel_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_page():
    form = MultipleBatchesForm()

    batch_date = request.args.get('batch_date')
    num_batch = int(request.args.get('num_batch'))
    day_id = request.args.get('day_id')

    batches = Batches.query.filter_by(batch_date=batch_date).order_by(Batches.batch_date.asc(), Batches.schedule_id.asc()).all()
    max_shifts = fetch_max_shifts()
    if num_batch > max_shifts:
        num_batch = max_shifts

    if form.validate_on_submit():
        schedule_id_to_keep = []
        for index, batch_form in enumerate(form.batches):
            schedule_id = index+1
            batch_date = batch_date
            start_time = batch_form.start_time.data
            end_time = batch_form.end_time.data
            max_tickets = batch_form.capacity.data
            day_id = day_id

            count = update_and_add_new_batch(day_id, schedule_id, batch_date, start_time, end_time, max_tickets)
            schedule_id_to_keep.append(schedule_id)
            if count > 0:
                flash(f"Add New Date on {batch_date}", category="success")    
            else:
                flash("Failed to updated", category="warning")

        
        for batch in batches:
            curr_schedule = batch.schedule_id
            if curr_schedule not in schedule_id_to_keep:
                status = delete_batch_by_date_scheduleid(batch_date, curr_schedule)
                if status:
                    flash(f"Success delete shift-{curr_schedule} in {batch_date}", category="success")
                else:
                    flash(f"Failed delete shift-{curr_schedule} in {batch_date}", category="warning")
                    
        return redirect(url_for('boardpanel.boardpanel_page'))

    for batch in batches:
        batch_form = NewBatchForm(
            start_time = batch.start_time,
            end_time = batch.end_time,
            capacity = batch.max_tickets
        )
        form.batches.append_entry(batch_form.data)
    
    if num_batch > len(batches) and num_batch <= max_shifts:
        default_set = Default_batch.query.filter_by(default_batch_id=1).first()
        
        for num in range(len(batches), num_batch):
            cur_batch_attr_start =f"batch{num+1}_start"
            cur_batch_attr_end =f"batch{num+1}_end"
            start_time = getattr(default_set, cur_batch_attr_start, datetime.time(0, 0))
            end_time = getattr(default_set, cur_batch_attr_end, datetime.time(0, 0))
            
            batch_form = NewBatchForm(
                start_time = start_time,
                end_time = end_time,
                capacity = default_set.capacity
            )
            form.batches.append_entry(batch_form.data)
    elif num_batch < len(batches) and num_batch <= max_shifts:
        for num in range(len(batches)-num_batch):
            form.batches.pop_entry()

    return render_template('edit.html', form=form, batches=batches, new_date=batch_date, enumerate=enumerate, num_batch=num_batch, day_id=day_id)

@boardpanel_bp.route('/delete', methods=['GET', 'POST'])
@login_required
def delete_page():

    batch_date_str = request.args.get('batch_date')
    batch_date = datetime.datetime.strptime(batch_date_str, "%Y-%m-%d")
    num_batch = int(request.args.get('num_batch'))
    day_ina_name = request.args.get('day_ina_name')
    default_check = request.args.get('default_check')
    
    batches = Batches.query.filter_by(batch_date=batch_date).order_by(Batches.batch_date.asc(), Batches.schedule_id.asc()).all()
    
    form = MultipleDeleteForm()

    if form.validate_on_submit():
        batchid_with_tickets = []
        for batch_form in form.batches:
            if batch_form.batch_checkboxes.data:
                try:
                    # result = delete_batch_by_id(batch_form.fixed_value.data)
                    batch_id = batch_form.fixed_value.data
                    dp = DatabaseProcess()
                    result = dp.delete_batch_by_id(batch_id)
                    if result == 0:
                        flash(f"Success delete batchID {batch_id} in date {batch_date}", category="success")
                    elif result > 0:
                        batchid_with_tickets.append(batch_id)
                    else:
                        flash(f"FAILED delete batchID {batch_id} in date {batch_date}", category="warning")
                except Exception as e:
                    flash(f"DELETE failed: {e}", category="danger")
        
        if len(batchid_with_tickets) > 0:
            batch_ids_str = ','.join(map(str, batchid_with_tickets)) # can not send a list
            
            return redirect(url_for('boardpanel.confirm_delete_batch_with_tickets', batch_ids_str=batch_ids_str))
        return redirect(url_for('.boardpanel_page'))

    options = []
    for batch in batches:
        batch_form = DeleteBatchesForm()
        if default_check == 'True':
            # Set the default value of the checkbox to True
            batch_form.batch_checkboxes.data = True
        options.append((batch.batch_id, f"shift-{batch.schedule_id}", batch.start_time, batch.end_time, batch.current_tickets, batch.max_tickets, batch.status))
        form.batches.append_entry(batch_form.data)
    
    return render_template('delete.html', form=form, options=options, batches=batches, batch_date=batch_date, num_batch=num_batch, day_ina_name=day_ina_name, enumerate=enumerate)

@boardpanel_bp.route('/deletecorfirmation', methods=['GET', 'POST'])
@login_required
def confirm_delete_batch_with_tickets():
    batch_ids_str = request.args.get('batch_ids_str')
    batch_ids = batch_ids_str.split(',')
    curr_batch_id = batch_ids.pop(0)
    curr_batch_info = Batches.query.filter_by(batch_id=curr_batch_id).first()

    form = ConfirmDeleteForm()

    if form.validate_on_submit():
        if form.confirm.data:

            dp = DatabaseProcess()
            result = dp.delete_batch_by_id_with_tickets(curr_batch_id)
            if result:
                flash(f"Success delete shift-{curr_batch_info.schedule_id} and {curr_batch_info.current_tickets} tickets", category="success")
            else:
                flash(f"Failed delete batchID {curr_batch_id}", category="warning")
            
            if len(batch_ids) > 0:
                batch_ids_str = ','.join(map(str, batch_ids))
                return redirect(url_for('boardpanel.confirm_delete_batch_with_tickets', batch_ids_str=batch_ids_str))
            else:
                return redirect(url_for('.boardpanel_page'))
    
    return render_template('confirm_delete_batch.html', form=form, batch_id=curr_batch_id, shift=curr_batch_info.schedule_id, tickets=curr_batch_info.current_tickets)

@boardpanel_bp.route('/batchdetail/<batch_id>', methods=['GET', 'POST'])
@login_required
def batchdetail_page(batch_id):
    curr_batch = Batches.query.filter_by(batch_id=batch_id).first()
    curr_batch_id = curr_batch.batch_id
    curr_date = curr_batch.batch_date
    batches = Batches.query.filter(Batches.batch_date == curr_date).order_by(Batches.batch_date.asc(), Batches.schedule_id.asc()).all()
    tickets = Booking_tickets.query.filter_by(batch_id=curr_batch_id).all()
    form = ChangeStatusForm()

    if form.validate_on_submit():
        option = form.status_option.data
        status = None
        result_status = None
        message = None
        if option == "open_shift":
            status = "OPEN"
            result_status, message = update_batch_status_by_batch(curr_batch_id, status)
        elif option == "open_all":
            status = "OPEN"
            result_status, message = update_batch_status_by_date(curr_date, status)
        else:
            status = "CLOSED"
            result_status, message = update_batch_status_by_batch(curr_batch_id, status)
        
        if result_status:
            flash(message, category="success")
        else:
            flash(message, category="warning")
        return redirect(url_for("boardpanel.batchdetail_page", batch_id=curr_batch_id))
        

    return render_template('batchdetail.html', batch=curr_batch, batches=batches, tickets=tickets, enumerate=enumerate, form=form)

@boardpanel_bp.route('/addmanual', methods=['GET', 'POST'])
@login_required
def addmanual_page():
    today = datetime.date.today()
    
    batches = Batches.query.filter(Batches.batch_date >= today).order_by(Batches.batch_date.asc(), Batches.schedule_id.asc()).all()

    return render_template('addmanual.html', batches=batches)


@boardpanel_bp.route('/batch_to_add/<batch_id>', methods=['GET', 'POST'])
@login_required
def batch_to_add_page(batch_id):
    batch = Batches.query.filter_by(batch_id=batch_id).first()
    form = AddCustomerManualForm()

    if form.validate_on_submit():
        ticket_uid = uuid.uuid4()
        username = form.username.data
        phone = form.phone.data
        batch_date = batch.batch_date
        status, message = add_customer_manually(batch_id, username, phone, batch_date, ticket_uid)

        if status:
            session["ticket"] = ticket_uid
            flash(message, category="success")
            return redirect(url_for('.ticketmanual_page'))
        else:
            flash(message, category="danger")
            return redirect(url_for('.boardpanel_page'))

    return render_template('batch_to_add.html', batch=batch, form=form)

@boardpanel_bp.route('/ticketmanual', methods=['GET', 'POST'])
def ticketmanual_page():
    form = CloseTicketButton()
    if form.validate_on_submit():
        return redirect(url_for('.boardpanel_page'))
    
    ticket_uid = session.get("ticket")
    if not ticket_uid:
        flash(f"Tidak dapat Tiket. Mohon maaf", category="danger")
        return redirect(url_for(".boardpanel_page"))
    
    ticket = Booking_tickets.query.get(ticket_uid)
    # Check if the ticket has been used
    if ticket.used:
        flash("This ticket has already been used.", "warning")
        return redirect(url_for('.boardpanel_page'))
    
    # Mark the ticket as used
    ticket.used = True
    db.session.commit()
    session.pop('ticket', None) # erase session ticket

    list_queue = fetct_queue_number(ticket.batch_id)
    queue_number = get_queue_number(list_queue, ticket_uid)
    if queue_number == -1:
        queue_number = "XX"
    
    return render_template('ticket.html', ticket=ticket, queue_number=queue_number, form=form)

@boardpanel_bp.route('/default', methods=['GET', 'POST'])
@login_required
def default_page():
    return render_template('default.html')


@boardpanel_bp.route('/defaultbatch', methods=['GET', 'POST'])
@login_required
def defaultbatch_page():
    form = DefaultBatchForm2()

    default_set = Default_batch.query.filter_by(default_batch_id=1).first()
    default_set = format_default_batch_time(default_set)
    
    if form.validate_on_submit():
        query = f"capacity = %s, booking_limit = %s, number_of_batches = %s, batch1_start = %s, batch1_end = %s, batch2_start = %s, batch2_end = %s, batch3_start = %s, batch3_end = %s, batch4_start = %s, batch4_end = %s, batch5_start = %s, batch5_end = %s"
        values = (form.capacity.data, form.booking_limit.data, form.number_of_batches.data, form.batch1_start.data, form.batch1_end.data, form.batch2_start.data, form.batch2_end.data, form.batch3_start.data, form.batch3_end.data, form.batch4_start.data, form.batch4_end.data, form.batch5_start.data, form.batch5_end.data)
        count = update_default_batch2(query, values)
        if count > 0:
            flash("Default updated successfully", category="success")    
        else:
            flash("Failed to updated", category="warning")
            
        return redirect(url_for("boardpanel.boardpanel_page"))
            
    
    return render_template('defaultbatch.html', form=form, default_set=default_set)

@boardpanel_bp.route('/defaultmessage', methods=['GET', 'POST'])
@login_required
def defaultmessage_page():
    opening_message = Opening_message.query.filter_by(message_id=1).first()
    message = {"opening": opening_message.text_message}
    form = OpeningMessageForm(text_message=message['opening'])

    
    if form.validate_on_submit():
        count = update_opening_message(form.text_message.data, form.is_active.data)
        if count > 0:
            flash("Opening message updated successfully", category="success")    
        else:
            flash("Failed to updated", category="warning")
            
        return redirect(url_for("boardpanel.boardpanel_page"))
            
    print(opening_message)
    return render_template('openingmessage.html', form=form, opening_message=opening_message)