from sms import db, app, bcrypt
from sqlalchemy import Time, Date, DateTime, Enum
import enum

class Employee(db.Model):
    __tablename__ = 'Employee'
    id = db.Column(db.Integer(), primary_key = True)
    name = db.Column(db.String(length = 30), nullable = False)
    role = db.Column(db.String(length = 50), nullable = False)
    department = db.Column(db.String(length = 40), nullable = False)
    shift_assignments = db.relationship("ShiftAssignment", backref = "employee", lazy = True)

class Shifts(db.Model):
    __tablename__ = 'Shifts'
    id = db.Column(db.Integer(), primary_key = True)
    name = db.Column(db.String(length=10), nullable = False)
    start_time = db.Column(Time, nullable = False)
    end_time = db.Column(Time, nullable = False)

class ShiftAssignment(db.Model):
    __tablename__ = 'Shift_Assignment'
    id = db.Column(db.Integer(), primary_key = True)
    employee_id = db.Column(db.Integer(), db.ForeignKey('Employee.id'), nullable  = False)
    date =db.Column(Date, nullable = False)
    shift_id = db.Column(db.Integer(), db.ForeignKey('Shifts.id'), nullable = False)

class AttendanceLogType(enum.Enum):
    entry = "entry"
    exit = "exit"

class AttendanceLog(db.Model):
    __tablename__ = 'Attendance_log'
    id = db.Column(db.Integer(), primary_key = True)
    employee_id = db.Column(db.Integer(), db.ForeignKey('Employee.id'), nullable = False)
    timestamp = db.Column(DateTime, nullable = False)
    type = db.Column(Enum(AttendanceLogType), nullable = False)

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer(), primary_key = True)
    username = db.Column(db.String(length = 35), unique = True, nullable = False)
    password = db.Column(db.String(length =255), nullable = False)

    def set_password(self, plaintext_password):
        self.password = bcrypt.generate_password_hash(plaintext_password).decode('utf-8')
        
    def check_password(self, plaintext_password):
        return bcrypt.check_password_hash(self.password, plaintext_password)
    
with app.app_context():
    db.create_all()