import datetime
from flask import Blueprint, render_template_string, render_template
from ..services.database import fetch_available_batch

home_bp = Blueprint('home', __name__, template_folder="../templates/home")

@home_bp.route('/')
@home_bp.route('/home')
def home_page():
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

    return render_template('home.html', batches=clean_batches)
