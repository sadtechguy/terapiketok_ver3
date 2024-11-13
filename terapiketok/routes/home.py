import datetime, uuid
from flask import Blueprint, render_template_string, render_template, request, redirect, url_for, session, flash
from ..services.database import fetch_available_batch, create_booking, fetct_queue_number
from ..services.data_processing import authenticate_user, get_queue_number
from ..forms import LoginForm, ConfirmationForm, CloseTicketButton
from ..models import Batches, Booking_tickets

home_bp = Blueprint('home', __name__, template_folder="../templates/home")

@home_bp.route('/', methods=['GET', 'POST'])
@home_bp.route('/home', methods=['GET', 'POST'])
def home_page():
    text_header = "Harap masukkan nama dan nomor HP"
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        phone = form.phone.data

        if authenticate_user(username, phone):
            # Redirect to the home page after successful login
            session["username"] = username
            session["phone"] = phone
            return redirect(url_for('.register_page'))
    return render_template('home.html', form=form, text_header=text_header)

@home_bp.route('/register', methods=['GET', 'POST'])
def register_page():
    username = session.get("username")
    phone = session.get("phone")

    if authenticate_user(username, phone) == False:
        return redirect(url_for('.home_page'))

    text_header = f"Selamat datang, {username}"
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    
    batches = fetch_available_batch(tomorrow)
    clean_batches = []
    for batch in batches:
        batch_date = batch[0].strftime('%d-%m-%Y')
        batch_day = batch[1]
        schedule_id = batch[2]
        schedule_name = batch[3]
        start_hour = batch[4].strftime('%H:%M')
        end_hour = batch[5].strftime('%H:%M')
        status = batch[8]
        batch_id = batch[9]

        print(batch)

        classes = {
            "OPEN": ("bgActive", "text-dark", "success"),
            "CLOSED": ("bgNonActive", "white-transparent", "danger")
        }
        left_side_class, middle_side_class, right_side_class = classes.get(status, ("bgNonActive", "white-transparent", "danger"))

        clean_batches.append(
            (batch_date, batch_day, schedule_id, schedule_name, start_hour, end_hour, status,
              left_side_class, middle_side_class, right_side_class, batch_id)
        )

    return render_template('register.html', batches=clean_batches, text_header=text_header)


@home_bp.route('/confirmation/<int:batch_id>', methods=['GET', 'POST'])
def confirmation_page(batch_id):
    username = session.get("username")
    phone = session.get("phone")
    
    batch = Batches.query.get(batch_id)
    
    if batch is None:
         return redirect(url_for('.register_page'))
    
    form = ConfirmationForm()

    if form.validate_on_submit():
        appointment_date = batch.batch_date
        
        # Version 4 (randomly generated)
        ticket_uid = uuid.uuid4()
        status, message = create_booking(batch_id, username, phone, appointment_date, ticket_uid)
        if status:
            session["ticket"] = ticket_uid
            flash(message, category="success")
            return redirect(url_for('.ticket_page'))
        else:
            flash(message, category="danger")
            return redirect(url_for('.register_page'))
    
    return render_template('confirmation.html', batch=batch, username=username, phone=phone, form=form)

@home_bp.route('/ticket', methods=['GET', 'POST'])
def ticket_page():
    form = CloseTicketButton()
    if form.validate_on_submit():
        return redirect(url_for('.register_page'))
    
    ticket_uid = session.get("ticket")
    if ticket_uid:
        ticket = Booking_tickets.query.get(ticket_uid)
        list_queue = fetct_queue_number(ticket.batch_id)
        queue_number = get_queue_number(list_queue, ticket_uid)
        if queue_number == -1:
            queue_number = "XX"
    else:
        flash(f"Tidak dapat Tiket. Mohon maaf", category="danger")
        return redirect(url_for(".register_page"))
    return render_template('ticket.html', ticket=ticket, queue_number=queue_number, form=form)


