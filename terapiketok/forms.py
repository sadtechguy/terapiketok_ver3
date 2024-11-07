from flask_wtf import FlaskForm
from .models import Adminuser
from wtforms import StringField, IntegerField, DateField, TimeField, SubmitField, PasswordField
from wtforms.validators import DataRequired, InputRequired, Length, ValidationError

class LoginForm(FlaskForm):
    username = StringField(label='Nama', validators=[DataRequired()])
    phone = StringField(label='Nomer HP', validators=[DataRequired()])
    submit = SubmitField(label='Login')

class ConfirmationForm(FlaskForm):
    submit = SubmitField(label='YES')

class CloseTicketButton(FlaskForm):
    submit = SubmitField(label='CLOSE')

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = Adminuser.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("That username already exists. Choose another username")
        
class LoginAdminForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

class DefaultBatchForm(FlaskForm):
    capacity = IntegerField(validators=[InputRequired()], render_kw={"placeholder": "capacity/shift"})
    booking_limit = IntegerField(validators=[InputRequired()], render_kw={"placeholder": "limit per HP"})
    number_of_batches = IntegerField(validators=[InputRequired()], render_kw={"placeholder": "jumlah shift"})
    batch1 = StringField(validators=[InputRequired(), Length(min=7, max=16)], render_kw={"placeholder": "Batch 1"})
    batch2 = StringField(validators=[InputRequired(), Length(min=7, max=16)], render_kw={"placeholder": "Batch 2"})
    batch3 = StringField(validators=[InputRequired(), Length(min=7, max=16)], render_kw={"placeholder": "Batch 3"})
    batch4 = StringField(validators=[InputRequired(), Length(min=7, max=16)], render_kw={"placeholder": "Batch 4"})
    batch5 = StringField(validators=[InputRequired(), Length(min=7, max=16)], render_kw={"placeholder": "Batch 5"})
    
    submit = SubmitField("SUBMIT")
