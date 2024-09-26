import datetime
from flask import Blueprint, render_template_string, render_template

home_bp = Blueprint('home', __name__, template_folder="../templates/home")

@home_bp.route('/')
@home_bp.route('/home')
def home_page():
    batches = [(datetime.date(2024, 10, 23), 'Rabu', 1, 'Sesi 1', datetime.time(11, 0), datetime.time(13, 0), 20, 0, 'PENDING'), (datetime.date(2024, 10, 22), 'Selasa', 2, 'Sesi 2', datetime.time(15, 0), datetime.time(17, 0), 20, 0, 'OPEN'), (datetime.date(2024, 10, 22), 'Selasa', 1, 'Sesi 1', datetime.time(11, 0), datetime.time(15, 0), 20, 0, 'OPEN')]
    clean_batches = []
    for batch in batches:
        batch_date = batch[0].strftime('%d-%m-%Y')
        batch_day = batch[1]
        schedule_id = batch[2]
        schedule_name = batch[3]
        start_hour = batch[4]
        end_hour = batch[5]
        status = batch[8]

        left_side_class = "bg-dark" if status == "OPEN" else "black-transparent"
        middle_side_class = "text-dark" if status =="OPEN" else "white-transparent"
        right_side_class = "success" if status == "OPEN" else "danger"

        clean_batches.append(
            (batch_date, batch_day, schedule_id, schedule_name, start_hour, end_hour, status,
              left_side_class, middle_side_class, right_side_class)
        )

    return render_template('home.html', batches=clean_batches)