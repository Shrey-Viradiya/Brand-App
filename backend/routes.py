from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_wtf import FlaskForm
from backend import app,bcrypt,db,mail
from backend.models import User, RequestID, Month, Question
from backend.forms import LoginForm, RegistrationForm, PermissionForm,RequestAccount,ContactForm,AddQuestion,CreateMonth
from flask_mail import Message
import os

#Static Routes

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

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    form= ContactForm()
    if form.validate_on_submit():
        msg = Message('Contact Request',
                  sender='shreyviradiya@gmail.com',
                  recipients=['shreyviradiya@gmail.com'])
        msg.body = f'''
        {form.name.data} (email id: {form.email.data}) has contacted you with message:

        __MESSAGE START__

        {form.content.data}

        __MESSAGE END__
        '''
        mail.send(msg)
    return render_template('contact.html',title='Contact Us', form=form)

#Dynamic Routes

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



@app.route("/survey")
def survey():
    return render_template('survey.html')


@app.route("/request_account", methods=['GET', 'POST'])
def request_account():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestAccount()
    clear_data()
    if form.validate_on_submit():
        req_id = RequestID(email = form.email.data)
        db.session.add(req_id)
        db.session.commit()
        send_request_email(req_id)
        flash('An email has been sent to admin to create account. You will be informed if your request is accepted', 'info')
        return redirect(url_for('login'))
    return render_template('requestaccount.html', title='Reset Password', form=form)


#Utilities

def send_database():
    msg = Message('Database Change', sender = 'nobody@test.com', recipients = ['shreyviradiya@gmail.com'])
    msg.body = "Find the updated database below"
    fp = app.open_resource("site.db")
    msg.attach('site.db','database/db',fp.read())
    fp.close()
    mail.send(msg)

def clear_data():
    for req in RequestID.query.all():
        db.session.delete(req)
        db.session.commit()

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




# Errors

@app.errorhandler(404)
def error_404(error):
    return render_template('404.html'), 404

@app.errorhandler(403)
def error_403(error):
    return render_template('403.html'), 403

@app.errorhandler(500)
def error_500(error):
    return render_template('500.html'), 500.


# Test Routes

# @app.route("/test")
# def test():
#     return render_template('500.html')


# Under Construction

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html',title = 'Dashboard')

@app.route("/createmonth", methods=['GET', 'POST'])
@login_required
def createmonth():
    form = CreateMonth()
    if form.validate_on_submit():
        month = Month(month = form.month.data , primary_subject = form.pr_sub.data, comment = form.comment.data)
        db.session.add(month)
        db.session.commit()
        flash('Month is created successfully!','success')
        return redirect(url_for('dashboard'))
    return render_template('createmonth.html',title = 'Dashboard',form=form)

@app.route("/addquestion", methods=['GET', 'POST'])
@login_required
def addquestion():
    form = AddQuestion()
    if form.validate_on_submit():
        question = Question(question = form.question.data , options = form.options.data, answer = form.answer.data, month_id= form.month.data)
        db.session.add(question)
        db.session.commit()
        flash('Question is Added successfully!','success')
        return redirect(url_for('dashboard'))
    return render_template('addquestion.html',title = 'Dashboard',form=form)