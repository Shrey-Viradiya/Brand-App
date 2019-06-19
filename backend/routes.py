from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from backend import app,bcrypt
from backend.models import User
from backend.forms import LoginForm


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
    return render_template('login.html')

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



