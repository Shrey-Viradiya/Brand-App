import os
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from backend.models import User, Month

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class PermissionForm(FlaskForm):
    master_password=PasswordField('Master Password',validators=[DataRequired()])
    submit = SubmitField('Proceed')

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Account')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class RequestAccount(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Account')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    content = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')

class AddQuestion(FlaskForm):
    question = TextAreaField('Question', validators=[DataRequired()])
    options = StringField('Options', validators=[DataRequired()])
    answer = StringField('Answer', validators=[DataRequired()])
    lst = Month.query.filter_by(id = Month.id).all()
    choices = [(month.id, month.month) for month in lst]
    month = SelectField('Month', choices= choices, coerce = int)
    submit = SubmitField('Add Question')

class CreateMonth(FlaskForm):
    month = StringField('Month', validators=[DataRequired()])
    pr_sub = StringField('Primary Subject', validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Create Month')

    def validate_month(self, month):
        mon = Month.query.filter_by(month = month.data).first()
        if mon:
            raise ValidationError('That month is already declared. Please choose a different one.')