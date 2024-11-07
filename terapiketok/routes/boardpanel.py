import datetime, uuid
from flask import Blueprint, render_template_string, render_template, request, redirect, url_for, session, flash
from flask_login import login_user, LoginManager, login_required, logout_user,current_user
from flask_bcrypt import Bcrypt
from ..models import Adminuser, Default_batch, Opening_message
from ..forms import RegisterForm, LoginAdminForm, DefaultBatchForm, OpeningMessageForm
from terapiketok import app, bcrypt, db

from ..services.database import add_default_batch, update_default_batch, update_opening_message

boardpanel_bp = Blueprint('boardpanel', __name__, template_folder="../templates/boardpanel")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "boardpanel.adminlogin_page"

@login_manager.user_loader
def load_user(user_id):
    return Adminuser.query.get(int(user_id))

@boardpanel_bp.before_request
def before_request():
    if current_user.is_authenticated:
        session.permanent = True  # Ensure session cookie is permanent
        db.session.refresh(current_user)  # Refresh user object from database
        session['user_id'] = current_user.user_id  # Update session data

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
            new_user = Adminuser(username=username, hashed_password=hashed_password)
            try:
                db.session.add(new_user)
                db.session.commit()
                flash("Registration successful!", category="success")
                return redirect(url_for("boardpanel.adminlogin_page"))
            except Exception as e:
                flash("Registration failed", category="danger")
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
    session.clear() # clear all session
    return redirect(url_for("boardpanel.adminlogin_page"))

@boardpanel_bp.route('/boardpanel', methods=['GET', 'POST'])
@login_required
def boardpanel_page():
    text_header = "DASHBOARD"
    return render_template('boardpanel.html', text_header=text_header)

@boardpanel_bp.route('/batches')
def batch_page():
    text_header = "Available Batches"
    return render_template('batches.html', text_header=text_header)

@boardpanel_bp.route('/newdate', methods=['GET', 'POST'])
@login_required
def newdate_page():
    text_header = "create new date"
    return render_template('newdate.html', text_header=text_header)

@boardpanel_bp.route('/default', methods=['GET', 'POST'])
@login_required
def default_page():
    return render_template('default.html')

@boardpanel_bp.route('/defaultbatch', methods=['GET', 'POST'])
@login_required
def defaultbatch_page():
    form = DefaultBatchForm()

    default_set = Default_batch.query.filter_by(default_batch_id=1).first()
    
    if form.validate_on_submit():
        schedules = [form.batch1.data, form.batch2.data, form.batch3.data, form.batch4.data, form.batch5.data]
        
        count = update_default_batch(form.capacity.data, form.booking_limit.data, form.number_of_batches.data, schedules)
        if count > 0:
            flash("Default updated successfully", category="success")    
        else:
            flash("Failed to updated", category="warning")
            
        return redirect(url_for("boardpanel.boardpanel_page"))
            
    
    return render_template('defaultbatch.html', form=form, default_set=default_set)

@boardpanel_bp.route('/defaultmessage', methods=['GET', 'POST'])
@login_required
def defaultmessage_page():
    opening_message = Opening_message.query.filter_by(message_id=1).first()
    message = {"opening": opening_message.text_message}
    form = OpeningMessageForm(text_message=message['opening'])

    
    if form.validate_on_submit():
        count = update_opening_message(form.text_message.data, form.is_active.data)
        if count > 0:
            flash("Opening message updated successfully", category="success")    
        else:
            flash("Failed to updated", category="warning")
            
        return redirect(url_for("boardpanel.boardpanel_page"))
            
    print(opening_message)
    return render_template('openingmessage.html', form=form, opening_message=opening_message)