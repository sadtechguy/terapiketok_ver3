import datetime, uuid
from flask import Blueprint, render_template_string, render_template, request, redirect, url_for, session, flash
from flask_login import login_user, LoginManager, login_required, logout_user,current_user
from flask_bcrypt import Bcrypt
from ..models import Adminuser
from ..forms import RegisterForm, LoginAdminForm
from terapiketok import app, bcrypt, db

from ..services.database import add_new_admin

boardpanel_bp = Blueprint('boardpanel', __name__, template_folder="../templates/boardpanel")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "boardpanel.adminlogin_page"

@login_manager.user_loader
def load_user(user_id):
    return Adminuser.query.get(int(user_id))

@boardpanel_bp.route('/boardpanel', methods=['GET', 'POST'])
@login_required
def boardpanel_page():
    text_header = "DASHBOARD"
    return render_template('boardpanel.html', text_header=text_header)

@boardpanel_bp.route('/batches')
def batch_page():
    text_header = "Available Batches"
    return render_template('batches.html', text_header=text_header)

@boardpanel_bp.route('/adminregister', methods=['GET', 'POST'])
def adminregister_page():
    text_header = "register"
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        if password == confirm_password:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            added_user_count = add_new_admin(username, hashed_password)
            # new_user = Adminuser(username=username, hashed_password=hashed_password)
            # db.session.add(new_user)
            # db.session.commit()

            if added_user_count == 1:
                flash("Registration successful!", category="success")
                return redirect(url_for("boardpanel.adminlogin_page"))
            else:
                flash("An error occurred during registration. Please try again.", category="danger")
        else:
            flash("password not match", category="danger")
    
    print(form.errors)

    return render_template('adminregister.html', text_header=text_header, form=form)

@boardpanel_bp.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin_page():
    text_header = "login"
    form = LoginAdminForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = Adminuser.query.filter_by(username=username).first()
        if user:
            if bcrypt.check_password_hash(user.hashed_password, password):
                
                login_user(user)
                return redirect(url_for('boardpanel.boardpanel_page'))

    return render_template('adminlogin.html', text_header=text_header, form=form)

@boardpanel_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout_page():
    logout_user()
    return redirect(url_for("boardpanel.adminlogin_page"))