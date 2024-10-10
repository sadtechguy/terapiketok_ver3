from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, TimeField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField(label='Nama', validators=[DataRequired()])
    phone = StringField(label='Nomer HP', validators=[DataRequired()])
    submit = SubmitField(label='Login')

