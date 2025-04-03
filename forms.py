from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, DateField, TimeField, SelectField, SubmitField, PasswordField, HiddenField, DecimalField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, EqualTo

class AppointmentForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=100)])
    mobile_number = StringField('Mobile Number', validators=[DataRequired(), Length(min=10, max=15)])
    consultation_fee = IntegerField('Consultation Fee', validators=[Optional()], default=500)
    email = StringField('Email', validators=[Optional(), Email(), Length(max=100)])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=1, max=120)])
    appointment_date = DateField('Appointment Date', validators=[DataRequired()])
    appointment_time = TimeField('Appointment Time', validators=[DataRequired()])
    primary_issue = TextAreaField('Primary Eye Issue', validators=[Optional(), Length(max=500)])
    referral_info = StringField('Referral Information (if any)', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Book Appointment')

class PaymentForm(FlaskForm):
    payment_method = SelectField('Payment Method', choices=[
        ('upi', 'UPI'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('cash', 'Cash')
    ], validators=[DataRequired()])
    submit = SubmitField('Proceed to Payment')

class ReviewForm(FlaskForm):
    patient_name = StringField('Your Name', validators=[DataRequired(), Length(min=3, max=100)])
    rating = SelectField('Rating', choices=[('5', '5 - Excellent'), ('4', '4 - Very Good'), ('3', '3 - Good'), ('2', '2 - Fair'), ('1', '1 - Poor')], validators=[DataRequired()])
    review_text = TextAreaField('Your Review', validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField('Submit Review')

class DoctorLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=128)])
    submit = SubmitField('Login')

class AssistantLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=128)])
    submit = SubmitField('Login')

class SalaryForm(FlaskForm):
    amount = StringField('Salary Amount', validators=[DataRequired()])
    payment_date = DateField('Payment Date', validators=[DataRequired()])
    payment_method = SelectField('Payment Method', choices=[
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('stripe', 'Stripe'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    description = TextAreaField('Description/Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Process Salary Payment')

# Keep for backward compatibility
class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=128)])
    submit = SubmitField('Login')

class PatientLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=128)])
    submit = SubmitField('Login')

class PatientRegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=100)])
    mobile_number = StringField('Mobile Number', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=1, max=120)])
    primary_issue = TextAreaField('Primary Eye Issue', validators=[Optional(), Length(max=500)])
    consultation_fee = DecimalField('Consultation Fee', validators=[Optional()], default=500.00)
    payment_method = SelectField('Payment Method', choices=[('cash', 'Cash'), ('gpay', 'Google Pay')], validators=[Optional()])
    password = PasswordField('Password', validators=[Optional(), Length(min=8, max=128)])
    submit = SubmitField('Add Patient')

class OTPVerificationForm(FlaskForm):
    email = HiddenField('Email')
    otp = StringField('OTP Code', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verify OTP')

class PrescriptionForm(FlaskForm):
    diagnosis = TextAreaField('Diagnosis', validators=[DataRequired()])
    left_eye_findings = TextAreaField('Left Eye Findings', validators=[Optional()])
    right_eye_findings = TextAreaField('Right Eye Findings', validators=[Optional()])
    prescribed_medications = TextAreaField('Prescribed Medications', validators=[Optional()])
    prescribed_eyewear = TextAreaField('Prescribed Eyewear', validators=[Optional()])
    follow_up_instructions = TextAreaField('Follow-up Instructions', validators=[Optional()])
    next_appointment_recommendation = StringField('Next Appointment', validators=[Optional()])
    submit = SubmitField('Save Prescription')
