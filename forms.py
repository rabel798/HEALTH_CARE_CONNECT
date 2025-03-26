from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, DateField, TimeField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional

class AppointmentForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=100)])
    mobile_number = StringField('Mobile Number', validators=[DataRequired(), Length(min=10, max=15)])
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

class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = StringField('Password', validators=[DataRequired(), Length(min=8, max=128)])
    submit = SubmitField('Login')
