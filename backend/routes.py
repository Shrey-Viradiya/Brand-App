from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_wtf import FlaskForm
from backend import app,bcrypt,db,mail
from backend.models import User, RequestID
from backend.forms import LoginForm, RegistrationForm, PermissionForm,RequestAccount
from flask_mail import Message
import os


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html',title = 'About')

@app.route("/team")
def team():
    return render_template('team.html',title = 'Team')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

def send_credential(user,form):
    msg = Message('Account Creation Request',
                  sender='shreyviradiya@gmail.com',
                  recipients=[user.email])
    msg.body = f'''
Your Credentials:

Email ID: {user.email}
Username: {user.username}
Password: {form.password.data}
'''
    mail.send(msg)

@app.route("/register/<token>", methods=['GET', 'POST'])
def register(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    req_id = RequestID.verify_request_token(token)
    if req_id is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('request_account'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=req_id.email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        send_database()
        send_credential(user,form)
        flash('Account has been created! Credentials are sent to user by email! User is now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/survey")
def survey():
    return render_template('survey.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def send_request_email(req_id):
    token = req_id.get_request_token()
    msg = Message('Account Creation Success',
                  sender='shreyviradiya@gmail.com',
                  recipients=['shreyviradiya@gmail.com'])
    msg.body = f'''
A person with email id {req_id.email} has requested an account.


To create an account, visit the following link:
{url_for('register', token=token, _external=True)}

If you do not want this request to complete then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route("/request_account", methods=['GET', 'POST'])
def request_account():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestAccount()
    if form.validate_on_submit():
        req_id = RequestID(email = form.email.data)
        db.session.add(req_id)
        db.session.commit()
        send_request_email(req_id)
        flash('An email has been sent to admin to create account. You will be informed if your request is accepted', 'info')
        return redirect(url_for('login'))
    return render_template('requestaccount.html', title='Reset Password', form=form)

def send_database():
    msg = Message('Database Change', sender = 'nobody@test.com', recipients = ['shreyviradiya@gmail.com'])
    msg.body = "Find the updated database below"
    fp = app.open_resource("site.db")
    msg.attach('site.db','database/db',fp.read())
    fp.close()
    mail.send(msg)