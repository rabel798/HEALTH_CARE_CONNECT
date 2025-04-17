import os
import logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
csrf = CSRFProtect()
login_manager = LoginManager()

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.environ.get('GMAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('GMAIL_APP_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('GMAIL_USERNAME')

# Razorpay configuration 
app.config['RAZORPAY_KEY_ID'] = os.environ.get('RAZORPAY_KEY_ID', 'your_razorpay_key_id')
app.config['RAZORPAY_KEY_SECRET'] = os.environ.get('RAZORPAY_KEY_SECRET', 'your_razorpay_secret_key')

if not app.config['RAZORPAY_KEY_ID'] or not app.config['RAZORPAY_KEY_SECRET']:
    print("Warning: Razorpay keys not configured. Please set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in Secrets")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///drricha.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions with app
db.init_app(app)
csrf.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'patient_login'

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import Doctor, Assistant, Admin, Patient
    try:
        if user_id.startswith('doctor_'):
            return Doctor.query.get(int(user_id.split('_')[1]))
        elif user_id.startswith('assistant_'):
            return Assistant.query.get(int(user_id.split('_')[1]))
        elif user_id.startswith('admin_'):
            return Admin.query.get(int(user_id.split('_')[1]))
        else:
            return Patient.query.get(int(user_id))
    except (ValueError, AttributeError):
        return None

# Import routes after app is created
from routes import *

# Create database tables
with app.app_context():
    db.create_all()

    # Create default accounts
    from models import Doctor, Assistant
    from datetime import date

    # Create doctor account
    doctor = Doctor.query.filter_by(username='drricha').first()
    if not doctor:
        doctor = Doctor(
            username='drricha',
            email='drricha@eyeclinic.com',
            full_name='Dr. Richa Sharma',
            mobile_number='9876543210',
            qualifications='MBBS, MS, FPOS',
            specialization='Ophthalmology, Pediatric Eye Care'
        )
        doctor.set_password('admin123')
        db.session.add(doctor)
        print('Default doctor account created')

    # Create optometrist account
    assistant = Assistant.query.filter_by(username='assistant').first()
    if not assistant:
        assistant = Assistant(
            username='assistant',
            email='assistant@eyeclinic.com',
            full_name='Clinic Optometrist',
            mobile_number='9876543211',
            position='Optometrist',
            joining_date=date.today()
        )
        assistant.set_password('assistant123')
        db.session.add(assistant)
        print('Default optometrist account created')

    try:
        db.session.commit()
        print('Default accounts created successfully')
    except Exception as e:
        db.session.rollback()
        print(f'Error creating default accounts: {str(e)}')

# Register error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)