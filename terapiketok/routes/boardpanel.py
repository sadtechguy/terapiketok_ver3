import datetime, uuid
from flask import Blueprint, render_template_string, render_template, request, redirect, url_for, session, flash
from flask_login import login_user, LoginManager, login_required, logout_user,current_user
from flask_bcrypt import Bcrypt
from ..models import Adminuser, Default_batch, Opening_message, Workingdays, Batches
from ..forms import RegisterForm, LoginAdminForm, DefaultBatchForm2, OpeningMessageForm, NewBatchForm, MultipleBatchesForm, NewDateForm
from ..services.data_processing import format_date_str, format_default_batch_time
from terapiketok import app, bcrypt, db

from ..services.database import add_default_batch, update_default_batch, update_default_batch2, update_opening_message, add_new_batch

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
    
    batches = Batches.query.filter(Batches.batch_date >= today).all()

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