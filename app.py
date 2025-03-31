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

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///drricha.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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
    # Check if it's an admin or patient based on the ID format
    if user_id.startswith('admin_'):
        admin_id = int(user_id.split('_')[1])
        from models import Admin
        return Admin.query.get(admin_id)
    else:
        from models import Patient
        return Patient.query.get(int(user_id))

# Import routes after app is created to avoid circular imports
from routes import *

# Create database tables
with app.app_context():
    db.create_all()
    
    # Create admin account for Dr. Richa if it doesn't exist
    from models import Admin
    admin = Admin.query.filter_by(username='dr.richa').first()
    if not admin:
        admin = Admin(
            username='richa',
            email='drricha@eyeclinic.com'
        )
        admin.set_password('richaisgreat'), should be changed after first login
        db.session.add(admin)
        try:
            db.session.commit()
            print('Default admin account created for Dr. Richa')
        except Exception as e:
            db.session.rollback()
            print(f'Error creating admin account: {str(e)}')

# Register error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
