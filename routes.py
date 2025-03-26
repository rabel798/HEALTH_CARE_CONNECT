import os
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from sqlalchemy import desc
from app import app, db
from models import Patient, Appointment, MedicalRecord, Payment, Review, Admin
from forms import AppointmentForm, PaymentForm, ReviewForm, AdminLoginForm

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
    
    if form.validate_on_submit():
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
    
    # Default available slots (9 AM to 5 PM with 30-minute intervals)
    all_slots = [
        "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
        "12:00", "12:30", "14:00", "14:30", "15:00", "15:30",
        "16:00", "16:30", "17:00"
    ]
    
    # If no date provided, return all slots
    if not selected_date:
        return jsonify(all_slots)
    
    try:
        # Convert selected_date string to date object
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        
        # Get all appointments for the selected date
        booked_appointments = Appointment.query.filter_by(appointment_date=selected_date).all()
        
        # Get the booked time slots
        booked_slots = [appt.appointment_time.strftime('%H:%M') for appt in booked_appointments]
        
        # Filter out booked slots
        available_slots = [slot for slot in all_slots if slot not in booked_slots]
        
        return jsonify(available_slots)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
