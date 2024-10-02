# app/models.py

from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Employee(UserMixin, db.Model):
    __tablename__ = 'employee'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    notifications = db.relationship('Notification', backref='employee', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    # Removed the notifications relationship

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    date = db.Column(db.Date, nullable=False)
    check_in_time = db.Column(db.DateTime)
    check_out_time = db.Column(db.DateTime)
    late_check_in_requested = db.Column(db.Boolean, default=False)
    late_check_in_approved = db.Column(db.Boolean, default=False)

    employee = db.relationship('Employee', backref=db.backref('attendances', lazy=True))

class LeaveRequest(db.Model):
    __tablename__ = 'leave_request'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(500))
    status = db.Column(db.String(50), default='Pending')

    employee = db.relationship('Employee', backref=db.backref('leave_requests', lazy=True))

class Notification(db.Model):
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    message = db.Column(db.String(500))
    date = db.Column(db.DateTime, nullable=False)
