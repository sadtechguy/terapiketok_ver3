from datetime import date, timedelta
from flask_wtf import FlaskForm
from .models import Adminuser
from wtforms import StringField, IntegerField, SubmitField, PasswordField, BooleanField, TextAreaField, DateField, TimeField, FieldList, FormField, SelectField
from wtforms.validators import DataRequired, InputRequired, Length, ValidationError, NumberRange

class LoginForm(FlaskForm):
    username = StringField(label='Nama', validators=[DataRequired()])
    phone = StringField(label='Nomer HP', validators=[DataRequired()])
    submit = SubmitField(label='Login')

class AddCustomerManualForm(FlaskForm):
    username = StringField(label='Nama', validators=[DataRequired()])
    phone = StringField(label='HP', validators=[DataRequired()])
    submit = SubmitField(label='Submit')

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
    number_of_batches = IntegerField(validators=[InputRequired(), NumberRange(min=1, max=10)], render_kw={"placeholder": "jumlah shift"})
    batch1 = StringField(validators=[InputRequired(), Length(min=7, max=16)], render_kw={"placeholder": "Batch 1"})
    batch2 = StringField(validators=[InputRequired(), Length(min=7, max=16)], render_kw={"placeholder": "Batch 2"})
    batch3 = StringField(validators=[InputRequired(), Length(min=7, max=16)], render_kw={"placeholder": "Batch 3"})
    batch4 = StringField(validators=[InputRequired(), Length(min=7, max=16)], render_kw={"placeholder": "Batch 4"})
    batch5 = StringField(validators=[InputRequired(), Length(min=7, max=16)], render_kw={"placeholder": "Batch 5"})
    
    submit = SubmitField("SUBMIT")
class DefaultBatchForm2(FlaskForm):
    capacity = IntegerField(validators=[InputRequired()], render_kw={"placeholder": "capacity/shift"})
    booking_limit = IntegerField(validators=[InputRequired()], render_kw={"placeholder": "limit per HP"})
    number_of_batches = IntegerField(validators=[InputRequired(), NumberRange(min=1, max=10)], render_kw={"placeholder": "jumlah shift"})
    batch1_start = StringField(validators=[InputRequired(), Length(min=5, max=8)], render_kw={"placeholder": "start"})
    batch1_end = StringField(validators=[InputRequired(), Length(min=5, max=8)], render_kw={"placeholder": "end"})
    batch2_start = StringField(validators=[InputRequired(), Length(min=5, max=8)], render_kw={"placeholder": "start"})
    batch2_end = StringField(validators=[InputRequired(), Length(min=5, max=8)], render_kw={"placeholder": "end"})
    batch3_start = StringField(validators=[InputRequired(), Length(min=5, max=8)], render_kw={"placeholder": "start"})
    batch3_end = StringField(validators=[InputRequired(), Length(min=5, max=8)], render_kw={"placeholder": "end"})
    batch4_start = StringField(validators=[InputRequired(), Length(min=5, max=8)], render_kw={"placeholder": "start"})
    batch4_end = StringField(validators=[InputRequired(), Length(min=5, max=8)], render_kw={"placeholder": "end"})
    batch5_start = StringField(validators=[InputRequired(), Length(min=5, max=8)], render_kw={"placeholder": "start"})
    batch5_end = StringField(validators=[InputRequired(), Length(min=5, max=8)], render_kw={"placeholder": "end"})
    
    submit = SubmitField("SUBMIT")

class OpeningMessageForm(FlaskForm):
    text_message = TextAreaField(validators=[Length(min=2, max=500)], render_kw={"placeholder": "write message here"})
    is_active = BooleanField('Active', default=True)
    submit = SubmitField("SUBMIT")

class NewBatchForm(FlaskForm):
    start_time = TimeField(format="%H:%M", validators=[InputRequired()])
    end_time = TimeField(format="%H:%M", validators=[InputRequired()])
    capacity = IntegerField(validators=[InputRequired(), NumberRange(min=1, max=40)])

class MultipleBatchesForm(FlaskForm):
    batches = FieldList(FormField(NewBatchForm), min_entries=0)
    submit = SubmitField(label='Submit!')

class NewDateForm(FlaskForm):
    batch_date = DateField("Tanggal", format="%Y-%m-%d", validators=[InputRequired()], default=date.today() + timedelta(days=1))
    batches = IntegerField("Jumlah Shift",validators=[InputRequired(), NumberRange(min=1, max=10)])
    submit = SubmitField(label='Submit!')

class ChangeStatusForm(FlaskForm):
    status_option = SelectField('Change status', choices=[
        ('open_all', 'open (all in same date)'),
        ('open_shift', 'open (this shift only)'),
        ('closed', 'closed'),
    ])
    submit = SubmitField('Submit')


class DeleteBatchesForm(FlaskForm):
    batch_checkboxes = BooleanField('Delete', default=False)
    fixed_value = StringField(render_kw={'readonly': True})
    
class MultipleDeleteForm(FlaskForm):
    batches = FieldList(FormField(DeleteBatchesForm), min_entries=0)
    submit = SubmitField(label='Delete')

class ConfirmDeleteForm(FlaskForm):
    confirm = BooleanField('Confirm Deletion', default=False)
    submit = SubmitField('Delete')
    
