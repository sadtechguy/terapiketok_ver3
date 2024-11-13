import datetime
from flask_login import UserMixin
from terapiketok import db

class Batches(db.Model):
    batch_id = db.Column(db.Integer, primary_key=True)
    day_id = db.Column(db.String(2), db.ForeignKey('workingdays.day_id'))
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.schedule_id'))
    batch_date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    max_tickets = db.Column(db.Integer)
    current_tickets = db.Column(db.Integer)
    status = db.Column(db.String(20))

    # Relationship with the schedule table
    workingdays = db.relationship('Workingdays', backref='batches') # Define relationship
    schedule = db.relationship('Schedule', backref='batches') # Define relationship

class Schedule(db.Model):
    schedule_id = db.Column(db.Integer, primary_key=True)
    schedule_name = db.Column(db.String(20))

class Workingdays(db.Model):
    day_id = db.Column(db.String(2), primary_key=True)
    day_name_ina = db.Column(db.String(7))
    day_num = db.Column(db.Integer)
class Booking_tickets(db.Model):
    ticket_uid = db.Column(db.UUID, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.batch_id'))
    customer_name = db.Column(db.String(50))
    phone = db.Column(db.String(30))
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime)

    # Relationship with the schedule table
    batches = db.relationship('Batches', backref='booking_tickets')

class Adminuser(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    hashed_password = db.Column(db.String(128), nullable=False)

    def get_id(self):
        return str(self.user_id)  # Use the user_id field as the unique identifier
    
class Default_batch(db.Model):
    default_batch_id = db.Column(db.Integer, primary_key=True)
    capacity = db.Column(db.Integer)
    booking_limit = db.Column(db.Integer, nullable=False)
    number_of_batches = db.Column(db.Integer, nullable=False)
    batch1_start = db.Column(db.Integer)
    batch1_end = db.Column(db.Integer)
    batch2_start = db.Column(db.Integer)
    batch2_end = db.Column(db.Integer)
    batch3_start = db.Column(db.Integer)
    batch3_end = db.Column(db.Integer)
    batch4_start = db.Column(db.Integer)
    batch4_end = db.Column(db.Integer)
    batch5_start = db.Column(db.Integer)
    batch5_end = db.Column(db.Integer)

class Opening_message(db.Model):
    message_id = db.Column(db.Integer, primary_key=True)
    text_message = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)






