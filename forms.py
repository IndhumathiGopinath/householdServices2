from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, FloatField, IntegerField, DateField, TimeField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('customer', 'Customer'), ('professional', 'Service Professional')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class CustomerProfileForm(FlaskForm):
    address = StringField('Address', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    pin_code = StringField('PIN Code', validators=[DataRequired(), Length(min=5, max=10)])
    submit = SubmitField('Save Profile')

class ProfessionalProfileForm(FlaskForm):
    service_id = SelectField('Service Type', coerce=int, validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    experience = IntegerField('Experience (years)', validators=[DataRequired()])
    hourly_rate = FloatField('Hourly Rate ($)', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    pin_code = StringField('PIN Code', validators=[DataRequired(), Length(min=5, max=10)])
    certificate_name = StringField('Certificate Name', validators=[DataRequired()])
    certificate_file = FileField('Upload Certificate', validators=[
        FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'Only PDF and image files are allowed')
    ])
    submit = SubmitField('Save Profile')
    
    def __init__(self, *args, **kwargs):
        super(ProfessionalProfileForm, self).__init__(*args, **kwargs)
        # If it's a new profile (not an edit), require the certificate file
        if not kwargs.get('obj'):
            self.certificate_file.validators.append(FileRequired())

class ServiceForm(FlaskForm):
    name = StringField('Service Name', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Description', validators=[DataRequired()])
    base_price = FloatField('Base Price ($)', validators=[DataRequired()])
    time_required = IntegerField('Time Required (minutes)', validators=[DataRequired()])
    is_active = BooleanField('Active')
    submit = SubmitField('Save Service')

class ServiceRequestForm(FlaskForm):
    service_id = SelectField('Service Type', coerce=int, validators=[DataRequired()])
    scheduled_date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    scheduled_time = TimeField('Time', validators=[DataRequired()], format='%H:%M')
    address = StringField('Address', validators=[DataRequired()])
    pin_code = StringField('PIN Code', validators=[DataRequired(), Length(min=5, max=10)])
    description = TextAreaField('Description')
    submit = SubmitField('Book Service')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')], coerce=int, validators=[DataRequired()])
    comment = TextAreaField('Comment')
    submit = SubmitField('Submit Review')
