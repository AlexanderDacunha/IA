from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Progress, Problems
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user



auth = Blueprint('auth', __name__)

# Page view to house all the login functionality of my app.
@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Differentiates a login attempt from a register attempt by the length of the form. 
    if request.method == "POST" and request.form.get('action') == "login":
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash(f'Logged in successfully', 'success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password', 'error')
        else:
            flash('Username does not exist', 'error')

        return redirect(url_for("auth.login"))



    elif request.method == "POST" and request.form.get('action') == "signup":
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password1')
        confirmPassword = request.form.get('password2')

        user = User.query.filter_by(email=email).first()

        if user:
            flash("email is already in use", 'error')

        elif (username is None) or len(username) < 1:
            flash('Must input a Username', 'error')

        elif (email is None) or len(email) < 4:
            flash('Email must be longer than 3 characters.', 'error')

        elif password != confirmPassword:
            flash('Passwords Must Match', 'error')
        
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password, method='pbkdf2:sha256'), role="Admin")
            
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user, remember=True)

            flash("Account created!", 'success')
            return redirect(url_for('views.home'))

        
    return render_template('login.html', user=current_user)

# Adds a way for the user to logout of my app.
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Successfully logged out", 'success')
    return redirect(url_for('auth.login'))


