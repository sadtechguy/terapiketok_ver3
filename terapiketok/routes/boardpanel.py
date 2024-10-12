import datetime, uuid
from flask import Blueprint, render_template_string, render_template, request, redirect, url_for, session, flash

boardpanel_bp = Blueprint('boardpanel', __name__, template_folder="../templates/boardpanel")

@boardpanel_bp.route('/boardpanel', methods=['GET', 'POST'])
def boardpanel_page():
    text_header = "DASHBOARD"
    return render_template('boardpanel.html', text_header=text_header)