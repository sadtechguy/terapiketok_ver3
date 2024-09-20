from flask import Blueprint, render_template_string, render_template

home_bp = Blueprint('home', __name__, template_folder="../templates/home")

@home_bp.route('/')
@home_bp.route('/home')
def home_page():
    return render_template('home.html')