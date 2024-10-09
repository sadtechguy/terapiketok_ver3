import datetime
from flask import Blueprint, render_template_string, render_template, request, redirect, url_for
from ..services.database import fetch_available_batch
from ..services.data_processing import authenticate_user

home_bp = Blueprint('home', __name__, template_folder="../templates/home")

@home_bp.route('/')
@home_bp.route('/home', methods=['GET', 'POST'])
def home_page():
    text_header = "Harap masukkan nama dan nomor HP"

    if request.method == 'POST':
        username = request.form['username']
        phone = request.form['phone']

        if authenticate_user(username, phone):
            # Redirect to the home page after successful login
            return redirect(url_for('.register_page', username=username, phone=phone))
    return render_template('home.html', text_header=text_header)

@home_bp.route('/register')
def register_page():
    username = request.args.get('username')
    phone = request.args.get('phone')

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

        left_side_class = "bgActive" if status == "OPEN" else "bgNonActive"
        middle_side_class = "text-dark" if status =="OPEN" else "white-transparent"
        right_side_class = "success" if status == "OPEN" else "danger"

        clean_batches.append(
            (batch_date, batch_day, schedule_id, schedule_name, start_hour, end_hour, status,
              left_side_class, middle_side_class, right_side_class)
        )

    return render_template('register.html', batches=clean_batches, text_header=text_header)
