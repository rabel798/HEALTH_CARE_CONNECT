import os
import logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from config import config

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

# Load config
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize extensions with app
db.init_app(app)
csrf.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'patient_login'
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"

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

# Register error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Import routes after app is created to avoid circular imports
from routes import *

# Create database tables and default accounts
with app.app_context():
    db.create_all()
    
    # Create doctor account for Dr. Richa if it doesn't exist
    from models import Doctor, Assistant, Admin
    from datetime import date
    
    try:
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
            doctor.set_password('admin123')  # default password
            db.session.add(doctor)
            db.session.commit()
            print('Default doctor account created for Dr. Richa')
        
        # Create assistant account
        assistant = Assistant.query.filter_by(username='assistant').first()
        if not assistant:
            assistant = Assistant(
                username='assistant',
                email='assistant@eyeclinic.com',
                full_name='Clinic Assistant',
                mobile_number='9876543211',
                position='Clinic Receptionist',
                joining_date=date.today()
            )
            assistant.set_password('assistant123')  # should be changed after first login
            db.session.add(assistant)
            db.session.commit()
            print('Default assistant account created')
    except Exception as e:
        db.session.rollback()
        print(f'Error creating default accounts: {str(e)}')
    
    # Keep admin account for backward compatibility
    admin = Admin.query.filter_by(username='richa').first()
    if not admin:
        admin = Admin(
            username='richa',
            email='admin@eyeclinic.com'
        )
        admin.set_password('admin123')  # should be changed after first login
        db.session.add(admin)
        print('Default admin account created for backward compatibility')
    
    try:
        db.session.commit()
        print('Default accounts created successfully')
    except Exception as e:
        db.session.rollback()
        print(f'Error creating default accounts: {str(e)}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)