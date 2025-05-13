from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, FloatField, SelectField, IntegerField, MultipleFileField, SubmitField,DateTimeField
from wtforms.validators import DataRequired, NumberRange, Email

class PropertyForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    property_type = SelectField('Property Type', choices=[
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('land', 'Land'),
        ('commercial', 'Commercial')
    ], validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('for_sale', 'For Sale'),
        ('for_rent', 'For Rent'),
        ('sold', 'Sold'),
        ('rented', 'Rented')
    ], validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    latitude = FloatField('Latitude')
    longitude = FloatField('Longitude')
    bedrooms = IntegerField('Bedrooms', validators=[NumberRange(min=0)])
    bathrooms = IntegerField('Bathrooms', validators=[NumberRange(min=0)])
    area = FloatField('Area (sq ft)', validators=[DataRequired(), NumberRange(min=0)])
    images = MultipleFileField('Images', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    submit = SubmitField('Add Property')

class ContactAgentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone')
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')

class ViewingForm(FlaskForm):
    preferred_date = DateTimeField('Preferred Viewing Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    alternate_date = DateTimeField('Alternate Viewing Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    notes = TextAreaField('Additional Notes')
    submit = SubmitField('Schedule Viewing')