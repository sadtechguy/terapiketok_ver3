from flask import Blueprint, render_template_string, render_template
from ..services.database import fetch_available_batch

home_bp = Blueprint('home', __name__, template_folder="../templates/home")

@home_bp.route('/')
@home_bp.route('/home')
def home_page():
    batches = fetch_available_batch()
    print(batches)
    return render_template('home.html')