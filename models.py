from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    age = db.Column(db.Integer, nullable=False)
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    
    def __repr__(self):
        return f'<Patient {self.full_name}>'

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    primary_issue = db.Column(db.Text, nullable=True)
    referral_info = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Appointment {self.id} for Patient {self.patient_id}>'

class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    appointment = db.relationship('Appointment', backref='medical_record', uselist=False)
    
    # Optometrist Review
    left_eye_assessment = db.Column(db.Text, nullable=True)
    right_eye_assessment = db.Column(db.Text, nullable=True)
    
    # Doctor Review
    doctor_notes = db.Column(db.Text, nullable=True)
    left_eye_findings = db.Column(db.Text, nullable=True)
    right_eye_findings = db.Column(db.Text, nullable=True)
    additional_remarks = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<MedicalRecord {self.id} for Appointment {self.appointment_id}>'

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    appointment = db.relationship('Appointment', backref='payment', uselist=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)  # upi, credit_card, debit_card, cash
    transaction_id = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Payment {self.id} for Appointment {self.appointment_id}>'

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=True)
    patient = db.relationship('Patient', backref='reviews')
    patient_name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Review {self.id} by {self.patient_name}>'

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Admin {self.username}>'
