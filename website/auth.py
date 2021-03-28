from flask import Flask, Blueprint, session, render_template, request, flash, redirect, url_for
from .models import Users
#from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import requests

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
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect pass, try again.', category='error')
        else:
            flash('User does not exist.', category='error')

    return render_template("enter.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('guest', None)
    session.pop('sender', None)
    print(session)
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        temp_pass = request.form.get('temp_pass')
        user = Users.query.filter_by(username=user_name).first()
        r = requests.get("http://www.instagram.com/" + str(user_name))
        if user:
            flash('Username already exists. Try login instead.', category='error')
        elif r.status_code == 404:
            flash("There is no instagram user with this name.", category='error')
        else:
            new_user = Users(username=user_name, temppass=temp_pass)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

