import os
import random
import string
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy import desc
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
from app import app, db
from models import Patient, Appointment, MedicalRecord, Payment, Review, Admin, OTP, Doctor, Assistant, Salary
from forms import (
    AppointmentForm, PaymentForm, ReviewForm, AdminLoginForm,
    PatientLoginForm, PatientRegistrationForm, OTPVerificationForm,
    PrescriptionForm, DoctorLoginForm, AssistantLoginForm, SalaryForm
)

# Add context processor to make current datetime available to all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.route('/')
def index():
    """Home page route"""
    # Fetch 3 most recent approved reviews
    recent_reviews = Review.query.filter_by(is_approved=True).order_by(desc(Review.created_at)).limit(3).all()
    return render_template('index.html', reviews=recent_reviews)

@app.route('/services')
def services():
    """Services page route"""
    return render_template('services.html')

@app.route('/location')
def location():
    """Location page route"""
    return render_template('location.html')

@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    """Reviews page route with submission form"""
    form = ReviewForm()

    if form.validate_on_submit():
        # Create new review (unapproved by default)
        new_review = Review(
            patient_name=form.patient_name.data,
            rating=int(form.rating.data),
            review_text=form.review_text.data,
            is_approved=False  # Requires admin approval
        )
        db.session.add(new_review)
        try:
            db.session.commit()
            flash('Thank you for your review! It will be displayed after approval.', 'success')
            return redirect(url_for('reviews'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting review: {str(e)}', 'danger')

    # Get all approved reviews
    approved_reviews = Review.query.filter_by(is_approved=True).order_by(desc(Review.created_at)).all()
    return render_template('reviews.html', reviews=approved_reviews, form=form)

@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    """Appointment booking page route"""
    form = AppointmentForm()

    # If the user is logged in, pre-fill the form
    if current_user.is_authenticated and isinstance(current_user, Patient):
        if request.method == 'GET':
            form.full_name.data = current_user.full_name
            form.mobile_number.data = current_user.mobile_number
            form.email.data = current_user.email
            form.age.data = current_user.age

    if form.validate_on_submit():
        if current_user.is_authenticated and isinstance(current_user, Patient):
            # Use the logged in patient
            patient = current_user
        else:
            # Check if patient exists by mobile number
            patient = Patient.query.filter_by(mobile_number=form.mobile_number.data).first()

            # If patient doesn't exist, create new patient
            if not patient:
                patient = Patient(
                    full_name=form.full_name.data,
                    mobile_number=form.mobile_number.data,
                    email=form.email.data,
                    age=form.age.data
                )
                db.session.add(patient)
                db.session.flush()  # To get the patient ID before commit

        # Create new appointment
        new_appointment = Appointment(
            patient_id=patient.id,
            appointment_date=form.appointment_date.data,
            appointment_time=form.appointment_time.data,
            primary_issue=form.primary_issue.data,
            referral_info=form.referral_info.data,
            status='scheduled'
        )
        db.session.add(new_appointment)

        try:
            db.session.commit()
            # Store appointment ID in session for payment process
            session['appointment_id'] = new_appointment.id
            flash('Appointment booked successfully!', 'success')
            return redirect(url_for('payment'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error booking appointment: {str(e)}', 'danger')

    # Pass default date (tomorrow) and available time slots to the template
    tomorrow = datetime.now() + timedelta(days=1)
    default_date = tomorrow.strftime('%Y-%m-%d')

    return render_template('appointment.html', form=form, default_date=default_date)

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    """Payment processing page route"""
    # Check if there's an appointment in session
    appointment_id = session.get('appointment_id')
    if not appointment_id:
        flash('No active appointment found', 'warning')
        return redirect(url_for('appointment'))

    # Get appointment details
    appointment = Appointment.query.get_or_404(appointment_id)

    form = PaymentForm()
    if form.validate_on_submit():
        # Create payment record
        consultation_fee = 500.00  # Default consultation fee
        new_payment = Payment(
            appointment_id=appointment_id,
            amount=consultation_fee,
            payment_method=form.payment_method.data,
            transaction_id=f"TR{datetime.now().strftime('%Y%m%d%H%M%S')}",
            status='completed'  # For demo, automatically mark as completed
        )
        db.session.add(new_payment)

        try:
            db.session.commit()
            # Clear appointment from session
            session.pop('appointment_id', None)
            flash('Payment completed successfully!', 'success')
            return redirect(url_for('success'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing payment: {str(e)}', 'danger')

    return render_template('payment.html', form=form, appointment=appointment)

@app.route('/success')
def success():
    """Success page after completing appointment and payment"""
    return render_template('success.html')

# API route for checking available time slots
@app.route('/api/available-slots', methods=['GET'])
def available_slots():
    selected_date = request.args.get('date')

    # If no date provided, return empty list
    if not selected_date:
        return jsonify([])

    try:
        # Convert selected_date string to date object
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

        # Check if the selected date is Sunday (weekday 6)
        is_sunday = selected_date.weekday() == 6

        # Define available slots based on day of week
        if is_sunday:
            # Sunday slots (10 AM to 1 PM with 30-minute intervals)
            all_slots = [
                "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00"
            ]
        else:
            # Monday to Saturday slots (6 PM to 9 PM with 30-minute intervals)
            all_slots = [
                "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00"
            ]

        # Get all appointments for the selected date
        booked_appointments = Appointment.query.filter_by(appointment_date=selected_date).all()

        # Get the booked time slots
        booked_slots = [appt.appointment_time.strftime('%H:%M') for appt in booked_appointments]

        # Filter out booked slots
        available_slots = [slot for slot in all_slots if slot not in booked_slots]

        return jsonify(available_slots)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Patient Authentication Routes
@app.route('/patient/register', methods=['GET', 'POST'])
def patient_register():
    """Patient registration route"""
    # If already logged in, redirect to patient dashboard
    if current_user.is_authenticated:
        return redirect(url_for('patient_dashboard'))

    form = PatientRegistrationForm()
    if form.validate_on_submit():
        # Check if email or mobile already exists
        existing_patient = Patient.query.filter(
            (Patient.email == form.email.data) | 
            (Patient.mobile_number == form.mobile_number.data)
        ).first()

        if existing_patient:
            flash('A patient with this email or mobile number already exists.', 'danger')
            return redirect(url_for('patient_register'))

        # Generate 6-digit OTP
        otp_code = ''.join(random.choices(string.digits, k=6))

        # Set expiry time (30 minutes)
        expires_at = datetime.utcnow() + timedelta(minutes=30)

        # Store OTP in database
        new_otp = OTP(
            email=form.email.data,
            otp_code=otp_code,
            expires_at=expires_at
        )
        db.session.add(new_otp)

        try:
            db.session.commit()

            # Store registration data in session for later use
            session['registration_data'] = {
                'full_name': form.full_name.data,
                'mobile_number': form.mobile_number.data,
                'email': form.email.data,
                'age': form.age.data,
                'password': form.password.data
            }

            # In a real app, we would send the OTP via email here
            # For testing, we'll flash it
            flash(f'For testing: Your OTP is {otp_code}', 'info')

            # Redirect to OTP verification page
            return redirect(url_for('verify_otp', email=form.email.data))

        except Exception as e:
            db.session.rollback()
            flash(f'Registration error: {str(e)}', 'danger')

    return render_template('patient/register.html', form=form)


@app.route('/patient/verify-otp/<email>', methods=['GET', 'POST'])
def verify_otp(email):
    """OTP verification route"""
    # If already logged in, redirect to patient dashboard
    if current_user.is_authenticated:
        return redirect(url_for('patient_dashboard'))

    # Check if we have registration data
    if 'registration_data' not in session:
        flash('Registration session expired. Please register again.', 'warning')
        return redirect(url_for('patient_register'))

    form = OTPVerificationForm()
    form.email.data = email

    if form.validate_on_submit():
        # Find the most recent OTP for this email
        otp_record = OTP.query.filter_by(
            email=email,
            is_verified=False
        ).order_by(desc(OTP.created_at)).first()

        if not otp_record:
            flash('OTP record not found or already verified. Please request a new OTP.', 'danger')
            return redirect(url_for('patient_register'))

        if otp_record.is_expired():
            flash('OTP has expired. Please request a new OTP.', 'danger')
            return redirect(url_for('patient_register'))

        if otp_record.otp_code != form.otp.data:
            flash('Invalid OTP. Please try again.', 'danger')
            return redirect(url_for('verify_otp', email=email))

        # OTP verified, create patient account
        registration_data = session['registration_data']
        new_patient = Patient(
            full_name=registration_data['full_name'],
            mobile_number=registration_data['mobile_number'],
            email=registration_data['email'],
            age=registration_data['age'],
            is_registered=True
        )
        new_patient.set_password(registration_data['password'])

        # Mark OTP as verified
        otp_record.is_verified = True

        db.session.add(new_patient)

        try:
            db.session.commit()

            # Clear session data
            session.pop('registration_data', None)

            # Log in the user
            login_user(new_patient)

            flash('Registration successful!', 'success')
            return redirect(url_for('patient_dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {str(e)}', 'danger')

    return render_template('patient/verify_otp.html', form=form, email=email)


@app.route('/patient/gmail-login', methods=['GET', 'POST'])
def patient_gmail_login():
    """Patient Gmail OTP login route"""
    # If already logged in, redirect to patient dashboard
    if current_user.is_authenticated:
        return redirect(url_for('patient_dashboard'))

    # Create a simple form to collect email for OTP
    class GmailLoginForm(FlaskForm):
        email = StringField('Email Address', validators=[DataRequired(), Email()])
        submit = SubmitField('Send OTP')

    form = GmailLoginForm()

    if form.validate_on_submit():
        email = form.email.data

        # Check if patient exists with this email
        patient = Patient.query.filter_by(email=email).first()

        if not patient:
            # Create a non-registered patient record with email only
            patient = Patient(
                full_name="Gmail User",  # Will be updated after login
                mobile_number="0000000000",  # Will be updated after login
                email=email,
                age=1,  # Will be updated after login
                is_registered=False
            )
            db.session.add(patient)
            db.session.flush()

        # Generate 6-digit OTP
        otp_code = ''.join(random.choices(string.digits, k=6))

        # Set expiry time (30 minutes)
        expires_at = datetime.utcnow() + timedelta(minutes=30)

        # Store OTP in database
        new_otp = OTP(
            email=email,
            otp_code=otp_code,
            expires_at=expires_at
        )
        db.session.add(new_otp)

        try:
            db.session.commit()

            # In a real app, we would send the OTP via email here
            # For testing, we'll flash it
            flash(f'For testing: Your OTP is {otp_code}', 'info')

            # Redirect to OTP verification page
            return redirect(url_for('verify_login_otp', email=email))

        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template('patient/gmail_login.html', form=form)


@app.route('/patient/verify-login-otp/<email>', methods=['GET', 'POST'])
def verify_login_otp(email):
    """Verify OTP for Gmail login"""
    # If already logged in, redirect to patient dashboard
    if current_user.is_authenticated:
        return redirect(url_for('patient_dashboard'))

    form = OTPVerificationForm()
    form.email.data = email

    if form.validate_on_submit():
        # Find the most recent OTP for this email
        otp_record = OTP.query.filter_by(
            email=email,
            is_verified=False
        ).order_by(desc(OTP.created_at)).first()

        if not otp_record:
            flash('OTP record not found or already verified. Please request a new OTP.', 'danger')
            return redirect(url_for('patient_gmail_login'))

        if otp_record.is_expired():
            flash('OTP has expired. Please request a new OTP.', 'danger')
            return redirect(url_for('patient_gmail_login'))

        # Check if OTP matches
        if otp_record.otp_code != form.otp.data:
            flash('Invalid OTP. Please try again.', 'danger')
            return redirect(url_for('verify_login_otp', email=email))

        # Mark OTP as verified
        otp_record.is_verified = True

        # Find the patient with this email
        patient = Patient.query.filter_by(email=email).first()

        if not patient:
            flash('Patient record not found.', 'danger')
            return redirect(url_for('patient_gmail_login'))

        # Login the patient
        login_user(patient)

        try:
            db.session.commit()

            # If this is the patient's first login with Gmail,
            # they might need to complete their profile
            if not patient.is_registered:
                flash('Please complete your profile information.', 'info')
                # Here we would ideally redirect to a profile completion page
                # For now, we'll just go to the dashboard

            return redirect(url_for('patient_dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error verifying OTP: {str(e)}', 'danger')

    return render_template('patient/verify_login_otp.html', form=form, email=email)


@app.route('/patient/login', methods=['GET', 'POST'])
def patient_login():
    """Patient login route"""
    # If already logged in, redirect to patient dashboard
    if current_user.is_authenticated:
        return redirect(url_for('patient_dashboard'))

    form = PatientLoginForm()
    if form.validate_on_submit():
        patient = Patient.query.filter_by(email=form.email.data).first()

        # Check if patient exists and password is correct
        if patient and patient.is_registered and patient.check_password(form.password.data):
            login_user(patient)

            # Get next page from query parameter, if any
            next_page = request.args.get('next')

            # Redirect to patient dashboard or next page
            return redirect(next_page or url_for('patient_dashboard'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('patient/login.html', form=form)


@app.route('/patient/logout')
@login_required
def patient_logout():
    """Patient logout route"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


@app.route('/patient/dashboard')
@login_required
def patient_dashboard():
    """Patient dashboard route"""
    # Get patient's appointments
    appointments = Appointment.query.filter_by(patient_id=current_user.id).order_by(desc(Appointment.appointment_date), desc(Appointment.appointment_time)).all()

    return render_template('patient/dashboard.html', appointments=appointments)


@app.route('/patient/appointments')
@login_required
def patient_appointments():
    """Patient appointments history route"""
    # Get patient's appointments
    appointments = Appointment.query.filter_by(patient_id=current_user.id).order_by(desc(Appointment.appointment_date)).all()

    return render_template('patient/appointments.html', appointments=appointments)


@app.route('/patient/medical-records')
@login_required
def patient_medical_records():
    """Patient medical records route"""
    # Get patient's appointments with medical records
    appointments = (
        db.session.query(Appointment)
        .join(MedicalRecord, Appointment.id == MedicalRecord.appointment_id)
        .filter(Appointment.patient_id == current_user.id)
        .order_by(desc(Appointment.appointment_date))
        .all()
    )

    return render_template('patient/medical_records.html', appointments=appointments)


# Authentication Selection Route
@app.route('/auth/selection')
def auth_selection():
    """Authentication selection route for choosing between staff and patient login"""
    return render_template('auth/selection.html')


# Doctor Authentication Routes
@app.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    """Doctor login route"""
    form = DoctorLoginForm()
    
    if form.validate_on_submit():
        # Since we had two versions of the username (drricha and dr.richa) we need to check both
        username = form.username.data.replace('.', '').lower()  # Normalize the input
        
        # First try direct match
        doctor = Doctor.query.filter_by(username=form.username.data).first()
        
        # If not found, try with a more flexible approach
        if not doctor:
            doctors = Doctor.query.all()
            for doc in doctors:
                # Normalize the stored username by removing dots
                normalized_username = doc.username.replace('.', '').lower()
                if normalized_username == username:
                    doctor = doc
                    break
        
        if doctor and doctor.check_password(form.password.data):
            login_user(doctor)
            flash('Welcome back, Dr. Richa!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            if form.username.data == "drricha" or form.username.data == "dr.richa":
                # Show more helpful message for doctor login
                flash('Doctor login failed. Please try username "dr.richa" with password "admin123"', 'danger')
            else:
                flash('Invalid credentials. Please check your username and password.', 'danger')
    
    return render_template('doctor/login.html', form=form)


@app.route('/doctor/logout')
@login_required
def doctor_logout():
    """Doctor logout route"""
    if current_user.is_authenticated and isinstance(current_user, Doctor):
        logout_user()
        flash('You have been logged out.', 'info')

    return redirect(url_for('auth_selection'))


# Assistant Authentication Routes
@app.route('/assistant/login', methods=['GET', 'POST'])
def assistant_login():
    """Assistant login route"""
    # If already logged in as assistant, redirect to dashboard
    if current_user.is_authenticated and isinstance(current_user, Assistant):
        return redirect(url_for('assistant_dashboard'))

    form = AssistantLoginForm()
    if form.validate_on_submit():
        # Find assistant with this username
        assistant = Assistant.query.filter_by(username=form.username.data).first()

        if assistant and assistant.check_password(form.password.data):
            login_user(assistant)
            flash('Login successful! Welcome, ' + assistant.full_name, 'success')
            return redirect(url_for('assistant_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('assistant/login.html', form=form)


@app.route('/assistant/logout')
@login_required
def assistant_logout():
    """Assistant logout route"""
    if current_user.is_authenticated and isinstance(current_user, Assistant):
        logout_user()
        flash('You have been logged out.', 'info')

    return redirect(url_for('auth_selection'))


@app.route('/assistant/dashboard')
@login_required
def assistant_dashboard():
    """Assistant dashboard route"""
    # Ensure user is an assistant
    if not isinstance(current_user, Assistant):
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))

    try:
        # Get all patients
        all_patients = db.session.query(
            Patient.id, 
            Patient.full_name, 
            Patient.mobile_number, 
            Patient.email, 
            Patient.age, 
            Patient.is_registered
        ).all()

        # Get today's appointments
        today = datetime.now().date()
        today_appointments = Appointment.query.filter_by(appointment_date=today).all()

        # Get all appointments
        all_appointments = Appointment.query.order_by(desc(Appointment.appointment_date)).all()

        # Get upcoming appointments
        upcoming_appointments = Appointment.query.filter(
            Appointment.appointment_date >= today,
            Appointment.status == 'scheduled'
        ).count()

        # Get total appointments
        total_appointments = Appointment.query.count()

        # Get total patients
        total_patients = Patient.query.count()

        # Get salary records for current assistant
        salary_records = Salary.query.filter_by(assistant_id=current_user.id).order_by(desc(Salary.payment_date)).all()
    except Exception as e:
        flash(f'Error loading dashboard data: {str(e)}', 'danger')
        return redirect(url_for('index'))

    return render_template(
        'assistant/dashboard.html',
        all_patients=all_patients,
        today_appointments=today_appointments,
        all_appointments=all_appointments,
        upcoming_appointments=upcoming_appointments,
        total_appointments=total_appointments,
        total_patients=total_patients,
        salary_records=salary_records
    )


# Admin/Doctor Authentication Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login route"""
    # Check if user is already logged in as admin
    if current_user.is_authenticated and isinstance(current_user, Admin):
        return redirect(url_for('admin_dashboard'))

    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()

        # Check if admin exists and password is correct
        if admin and admin.check_password(form.password.data):
            login_user(admin)

            # Redirect to admin dashboard
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('admin/login.html', form=form)


@app.route('/admin/logout')
@login_required
def admin_logout():
    """Admin logout route"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin/Doctor dashboard route"""
    # Ensure only admins or assistants can access this page
    if not (isinstance(current_user, Admin) or isinstance(current_user, Assistant)):
        flash('Access denied. Staff privileges required.', 'danger')
        return redirect(url_for('index'))

    # Get counts for dashboard
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    upcoming_appointments = Appointment.query.filter(
        Appointment.appointment_date >= datetime.now().date(),
        Appointment.status == 'scheduled'
    ).count()
    pending_reviews = Review.query.filter_by(is_approved=False).count()

    # Today's appointments
    today_appointments = Appointment.query.filter(
        Appointment.appointment_date == datetime.now().date(),
        Appointment.status == 'scheduled'
    ).order_by(Appointment.appointment_time).all()

    return render_template('admin/dashboard.html', 
                          total_patients=total_patients,
                          total_appointments=total_appointments,
                          upcoming_appointments=upcoming_appointments,
                          pending_reviews=pending_reviews,
                          today_appointments=today_appointments)


@app.route('/admin/appointments')
@login_required
def admin_appointments():
    """Admin appointments management route"""
    # Ensure only admins or assistants can access this page
    if not (isinstance(current_user, Admin) or isinstance(current_user, Assistant)):
        flash('Access denied. Staff privileges required.', 'danger')
        return redirect(url_for('index'))

    # Get all appointments
    appointments = Appointment.query.order_by(desc(Appointment.appointment_date), desc(Appointment.appointment_time)).all()

    return render_template('admin/appointments.html', appointments=appointments)


@app.route('/admin/patients')
@login_required
def admin_patients():
    """Admin patients management route"""
    # Ensure only admins or assistants can access this page
    if not (isinstance(current_user, Admin) or isinstance(current_user, Assistant)):
        flash('Access denied. Staff privileges required.', 'danger')
        return redirect(url_for('index'))

    # Get all patients
    patients = Patient.query.order_by(Patient.full_name).all()

    return render_template('admin/patients.html', patients=patients)


@app.route('/admin/patient/<int:patient_id>')
@login_required
def admin_patient_view(patient_id):
    """Admin patient view route"""
    # Ensure only admins or assistants can access this page
    if not (isinstance(current_user, Admin) or isinstance(current_user, Assistant)):
        flash('Access denied. Staff privileges required.', 'danger')
        return redirect(url_for('index'))

    # Get patient details
    patient = Patient.query.get_or_404(patient_id)

    # Get patient's appointments and medical records
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(desc(Appointment.appointment_date)).all()

    return render_template('admin/patient_view.html', patient=patient, appointments=appointments)


@app.route('/admin/appointment/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def admin_appointment_view(appointment_id):
    """Admin appointment view route"""
    # Ensure only admins or assistants can access this page
    if not (isinstance(current_user, Admin) or isinstance(current_user, Assistant)):
        flash('Access denied. Staff privileges required.', 'danger')
        return redirect(url_for('index'))

    # Get appointment details
    appointment = Appointment.query.get_or_404(appointment_id)

    # Handle POST requests for updating appointment status
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'complete':
            appointment.status = 'completed'
            message = "Your appointment has been completed. Thank you for visiting Dr. Richa's Eye Clinic."
            
            try:
                db.session.commit()
                
                # Send email notification if patient has email
                if appointment.patient.email:
                    subject = f"Appointment {appointment.status.title()} - Dr. Richa's Eye Clinic"
                    send_email_notification(appointment.patient.email, subject, message)
                    
                flash('Appointment marked as completed.', 'success')
                return redirect(url_for('admin_appointment_view', appointment_id=appointment_id))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating appointment: {str(e)}', 'danger')
                
        elif action == 'cancel':
            appointment.status = 'cancelled'
            message = "Your appointment has been cancelled. Please contact us if you need to reschedule."
            
            try:
                db.session.commit()
                
                # Send email notification if patient has email
                if appointment.patient.email:
                    subject = f"Appointment {appointment.status.title()} - Dr. Richa's Eye Clinic"
                    send_email_notification(appointment.patient.email, subject, message)
                    
                flash('Appointment has been cancelled.', 'warning')
                return redirect(url_for('admin_appointment_view', appointment_id=appointment_id))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating appointment: {str(e)}', 'danger')

    # Get medical record if it exists
    medical_record = MedicalRecord.query.filter_by(appointment_id=appointment_id).first()
    has_medical_record = medical_record is not None

    return render_template('admin/appointment_view.html', 
                           appointment=appointment, 
                           medical_record=medical_record, 
                           has_medical_record=has_medical_record)


@app.route('/admin/prescription/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def admin_add_prescription(appointment_id):
    """Admin add/edit prescription route"""
    # Ensure only admins or assistants can access this page
    if not (isinstance(current_user, Admin) or isinstance(current_user, Assistant)):
        flash('Access denied. Staff privileges required.', 'danger')
        return redirect(url_for('index'))

    # Get appointment details
    appointment = Appointment.query.get_or_404(appointment_id)

    # Get or create medical record
    medical_record = MedicalRecord.query.filter_by(appointment_id=appointment_id).first()
    is_edit = medical_record is not None

    if not medical_record:
        medical_record = MedicalRecord(appointment_id=appointment_id)
        db.session.add(medical_record)
        db.session.flush()

    form = PrescriptionForm(obj=medical_record)

    if form.validate_on_submit():
        # Update medical record with form data
        form.populate_obj(medical_record)

        # Update appointment status to completed
        appointment.status = 'completed'

        try:
            db.session.commit()
            if is_edit:
                flash('Prescription updated successfully!', 'success')
            else:
                flash('Prescription added successfully!', 'success')
            return redirect(url_for('admin_appointment_view', appointment_id=appointment_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving prescription: {str(e)}', 'danger')

    return render_template('admin/add_prescription.html', form=form, appointment=appointment, is_edit=is_edit)


@app.route('/admin/reviews')
@login_required
def admin_reviews():
    """Admin reviews management route"""
    # Ensure only admins or assistants can access this page
    if not (isinstance(current_user, Admin) or isinstance(current_user, Assistant)):
        flash('Access denied. Staff privileges required.', 'danger')
        return redirect(url_for('index'))

    # Get pending reviews
    pending_reviews = Review.query.filter_by(is_approved=False).order_by(desc(Review.created_at)).all()

    # Get approved reviews
    approved_reviews = Review.query.filter_by(is_approved=True).order_by(desc(Review.created_at)).all()

    return render_template('admin/reviews.html', pending_reviews=pending_reviews, approved_reviews=approved_reviews)


@app.route('/admin/review/approve/<int:review_id>', methods=['POST'])
@login_required
def admin_approve_review(review_id):
    """Admin approve review route"""
    # Ensure only admins or assistants can access this page
    if not (isinstance(current_user, Admin) or isinstance(current_user, Assistant)):
        flash('Access denied. Staff privileges required.', 'danger')
        return redirect(url_for('index'))

    # Get review
    review = Review.query.get_or_404(review_id)

    # Approve review
    review.is_approved = True

    try:
        db.session.commit()
        flash('Review approved!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error approving review: {str(e)}', 'danger')

    return redirect(url_for('admin_reviews'))
def send_email_notification(to_email, subject, message):
    try:
        # Email configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "your-clinic-email@gmail.com"  # Update this
        sender_password = "your-app-password"  # Update this

        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

@app.route('/assistant/add-patient', methods=['GET', 'POST'])
@login_required
def assistant_add_patient():
    if not isinstance(current_user, Assistant):
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    form = PatientRegistrationForm()
    if form.validate_on_submit():
        new_patient = Patient(
            full_name=form.full_name.data,
            mobile_number=form.mobile_number.data,
            email=form.email.data,
            age=form.age.data,
            is_registered=False
        )
        db.session.add(new_patient)
        try:
            db.session.commit()
            flash('Patient added successfully!', 'success')
            return redirect(url_for('assistant_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding patient: {str(e)}', 'danger')

    return render_template('assistant/add_patient.html', form=form)