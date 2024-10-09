import datetime
from flask import Blueprint, render_template_string, render_template, request, redirect, url_for, session
from ..services.database import fetch_available_batch
from ..services.data_processing import authenticate_user
from ..forms import LoginForm

home_bp = Blueprint('home', __name__, template_folder="../templates/home")

@home_bp.route('/', methods=['GET', 'POST'])
@home_bp.route('/home', methods=['GET', 'POST'])
def home_page():
    text_header = "Harap masukkan nama dan nomor HP"
    form = LoginForm()

    if form.validate_on_submit():
        # username = request.form['username']
        # phone = request.form['phone']

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
    batches = fetch_available_batch()
    clean_batches = []
    for batch in batches:
        batch_date = batch[0].strftime('%d-%m-%Y')
        batch_day = batch[1]
        schedule_id = batch[2]
        schedule_name = batch[3]
        start_hour = batch[4]
        end_hour = batch[5]
        status = batch[8]

        classes = {
            "OPEN": ("bgActive", "text-dark", "success"),
            "CLOSED": ("bgNonActive", "white-transparent", "danger")
        }
        left_side_class, middle_side_class, right_side_class = classes.get(status, ("bgNonActive", "white-transparent", "danger"))

        clean_batches.append(
            (batch_date, batch_day, schedule_id, schedule_name, start_hour, end_hour, status,
              left_side_class, middle_side_class, right_side_class)
        )

    return render_template('register.html', batches=clean_batches, text_header=text_header)
