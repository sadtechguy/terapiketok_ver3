import datetime
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
class Booking_tickets(db.Model):
    ticket_uid = db.Column(db.UUID, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.batch_id'))
    customer_name = db.Column(db.String(50))
    phone = db.Column(db.String(30))
    created_at = db.Column(db.DateTime)

    # Relationship with the schedule table
    batches = db.relationship('Batches', backref='booking_tickets')


