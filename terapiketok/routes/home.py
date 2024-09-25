import datetime
from flask import Blueprint, render_template_string, render_template

home_bp = Blueprint('home', __name__, template_folder="../templates/home")

@home_bp.route('/')
@home_bp.route('/home')
def home_page():
    batches = [(datetime.date(2024, 10, 23), 'Rabu', 1, 'Sesi 1', datetime.time(11, 0), datetime.time(13, 0), 20, 0, 'PENDING'), (datetime.date(2024, 10, 22), 'Selasa', 2, 'Sesi 2', datetime.time(15, 0), datetime.time(17, 0), 20, 0, 'OPEN'), (datetime.date(2024, 10, 22), 'Selasa', 1, 'Sesi 1', datetime.time(11, 0), datetime.time(15, 0), 20, 0, 'OPEN')]
    clean_batches = []
    for b_date, b_day, s_id, s_name, b_start, b_end, limit, available, status in batches:
        if status == "OPEN":
            bgcolor = 'success'
        else:
            bgcolor = "danger"
        clean_batches.append((b_date.strftime('%d-%m-%Y'), b_day, s_id, s_name, b_start.strftime('%H:%M'), b_end.strftime('%H:%M'), status, bgcolor))


    return render_template('home.html', batches=clean_batches)