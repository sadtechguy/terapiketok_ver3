import datetime, uuid
from flask import Blueprint, render_template_string, render_template, request, redirect, url_for, session, flash
from ..models import Adminuser

boardpanel_bp = Blueprint('boardpanel', __name__, template_folder="../templates/boardpanel")

@boardpanel_bp.route('/boardpanel', methods=['GET', 'POST'])
def boardpanel_page():
    text_header = "DASHBOARD"
    return render_template('boardpanel.html', text_header=text_header)

@boardpanel_bp.route('/batches')
def batch_page():
    text_header = "Available Batches"
    return render_template('batches.html', text_header=text_header)