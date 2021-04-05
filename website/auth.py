import jwt
from flask import Flask, Blueprint, session, render_template, request, flash, redirect, url_for
from .models import Users
#from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import requests
import logging as log

auth = Blueprint('auth', __name__)


@auth.route('/x/enter', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        temp_pass = request.form.get('temp_pass')
        user = Users.query.filter_by(username=user_name).first()
        if user:
            if user.temppass == temp_pass:
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                session["guest"] = user_name
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect pass, try again.', category='error')
        else:
            flash('User does not exist.', category='error')
    else:
        return render_template("enter.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('guest', None)
    session.pop('sender', None)
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        temp_pass = request.form.get('temp_pass')
        user = Users.query.filter_by(username=user_name).first()
        r = requests.get("http://www.wwu.de/" + str(user_name))
        if user:
            flash('Username already exists. Try login instead.', category='error')
        elif r.status_code == 404:
            flash("There is no WWU user with this name.", category='error')
        else:
            new_user = Users(username=user_name, temppass=temp_pass)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)


"""
logic for password-less login
"""


def send_login_url(user: Users):
    """ placeholder for sending the url to the user (through phone, email, etc.) """
    # todo: fill this function and remove the prints
    print("User %s is attempting to log in:" % user)
    print("    LOGIN URL: %s" % user.login_url)
    print("...the previous URL would have been sent to the user.")


@auth.route('/x/login', methods=['GET', 'POST'])
def login_password_less():
    """ main login page to request a login URL """
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        user = Users.query.filter_by(username=user_name).first()
        if user:
            send_login_url(user)
            flash('We have sent you a URL. Click it to log in!', category='success')
        else:
            flash('User does not exist.', category='error')

    return render_template("login_password_less.html", user=current_user)


@auth.route('/x/login-with-token', methods=['GET'])
def login_password_less_exchange_jwt():
    """ password-less login endpoint; logs in the user if the url is correct """
    try:
        token = request.args['loginToken']
    except KeyError:
        flash('Invalid url (no token found).', category='error')
        return render_template("login_password_less.html", user=current_user)

    user: Users = Users.from_token(token)  # find user for the current token

    if not user:
        flash('Invalid url (user not found).', category='error')
        return render_template("login_password_less.html", user=current_user)

    # check if the token is valid for the current user
    try:
        if not user.validate_login_jwt(token):
            flash('Invalid url (token does not grant login action for this user).', category='error')
            return render_template("login_password_less.html", user=current_user)
    except jwt.exceptions.ExpiredSignatureError:
        flash('Your url has expired; request it again.', category='error')
        return render_template("login_password_less.html", user=current_user)

    # log user in
    flash('Logged in successfully!', category='success')
    login_user(user, remember=True)
    return redirect(url_for('views.home'))


""" 
logic for password-less sign-up
"""


@auth.route('/x/sign-up', methods=['GET', 'POST'])
def sign_up_password_less():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        email = request.form.get('email')  # todo or phone or whatever you will use to send the urls
        user = Users.query.filter_by(username=user_name).first()

        if user:
            flash('Username already exists. Try login instead.', category='error')
            return render_template("sign_up_password_less.html", user=current_user)

        # check if it is a valid instagram username
        r = requests.get("http://www.instagram.com/" + str(user_name))
        if r.status_code == 404:
            flash("There is no instagram user with this name.", category='error')
            return render_template("sign_up_password_less.html", user=current_user)

        new_user = Users()
        new_user.username = user_name
        # new_user.email = email
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        flash('Account created!', category='success')
        return redirect(url_for('views.home'))

    return render_template("sign_up_password_less.html", user=current_user)
