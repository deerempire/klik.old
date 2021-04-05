from flask import Blueprint, session, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Clicks, Users, Memberships
from .methods import find_matches
from datetime import timedelta, datetime
from sqlalchemy import and_, func, desc
import threading

import time
from . import db
import json
import requests
from random import randrange

views = Blueprint('views', __name__)
views.secret_key = "gabino4ever"
views.permanent_session_lifetime = timedelta(seconds=30)
temp_pass = "temp"



@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    people = []
    rere = []
    known_people = []
    people_count = []

    matches, sLi = find_matches(current_user)


    ## Who clicked? ##
    received = Clicks.query.filter_by(receiver=current_user.username).all()
    for r in received:
        rere.append(r.sender)

    rows = len(received)
    print(received)
    sent = Clicks.query.filter_by(sender=current_user.username).all()
    random_people = Clicks.query.filter(and_(Clicks.receiver != current_user.username, Clicks.confirmed != 0)).filter(Clicks.sender.notin_(rere)).all()

    print("randoms:")
    print(random_people)

    ### People Suggestions ###
    comm_prob = randrange(100)
    print(comm_prob)
    if comm_prob < 25:
        chosen = randrange(len(received))
        received = received[chosen:chosen+1] #select one random person from the received list
        received = received + random_people #add it to a list of unknown, random people
    else:
        received = random_people

    for r in received:
        people.append(r.sender)

    for s in sent:
        known_people.append(s.receiver)

    for kp in known_people:
        print("LINE 50")
        count = Clicks.query.filter_by(receiver=kp).count()
        people_count.append(str(count))

    people = list(set(people) - set(known_people))
    people = set(people)  # take distinct names

    if current_user.username in people:
        people.remove(current_user.username)

    ### Click Counter ###

    new_rows = click_counter(rows)

    ### Sending a Click ###

    if request.method == 'POST':
        click = request.form.get('click')
        click = click.lower()
        if click in sLi:  # returns True or False
            flash("You already klik'd " + str(click) + ".", category='error')
        elif current_user.username == click:
            flash("You can't klik yourself!", category='error')
        elif len(click) < 2:
            flash("This can't be right.", category='error')
        else:
            new_click = Clicks(receiver=click, sender=current_user.username, confirmed=True)
            db.session.add(new_click)
            db.session.commit()
            matches, sLi = find_matches(current_user)
            flash('Klik sent to ' + str(click) + "!", category='success')

    return render_template("home.html", user=current_user, rows=new_rows, matches=matches, people=people, count=people_count)


@views.route('/forget-me', methods=['POST'])
def forget_me():
    if request.method == 'POST':
        usr = request.form.get('forget')
    session.pop('guest', None)
    return redirect(f"/{usr}")

@views.route('/search-user', methods=['POST'])
def search_user():
    if request.method == 'POST':
        usr = request.form.get('search')
    return redirect(f"/{usr}")


@views.route('/delete-click', methods=['GET','POST'])
def delete_click():
    click = json.loads(request.data)
    clickId = click['clickId']
    click = Clicks.query.get(clickId)
    if click and click.sender == current_user.username:
        db.session.delete(click)
        db.session.commit()
        flash('Klik removed!', category='success')
    return jsonify({})


@views.route("/<usr>", methods=['GET', 'POST'])
def userPage(usr):

    ### Click Counter###
    rows = Clicks.query.filter_by(receiver=usr).count()
    new_rows = click_counter(rows)

    show = 1
    click_id = 0

    if "guest" in session:
        sender = session["guest"]
        print("There's a guest in session.")
    else:
        sender = None
        print("No guest in session.")

    if current_user.is_authenticated:
        if usr == current_user.username:
            return redirect(url_for("views.home"))
        else:
            sent = Clicks.query.filter_by(sender=current_user.username).all()
            for s in sent:
                if s.receiver == usr:
                    click_id = s.id
                    show = 0


    ### Sending a Click ###
    if request.method == 'POST':
        receiver = usr.lower()
        received = []

        sender = request.form.get('guest')
        sender.lower()

        session.permanent = True
        session['guest'] = sender

        if sender == receiver:
            flash("Really?", category='error')
        elif len(sender) < 2:
            flash("Really?", category='error')

        elif Users.query.filter_by(username=sender).first():

            clicks = Clicks.query.filter_by(sender=sender).all()
            for c in clicks:
                received.append(c.receiver)

            if current_user.is_authenticated:
                print("he is  authenticated")
                if receiver in received:
                    flash("auth Already klikd by this user!", category='error')
                else:
                    new_click = Clicks(receiver=receiver, sender=current_user.username, confirmed=True)
                    db.session.add(new_click)
                    db.session.commit()
                    flash('Klik sent to ' + str(receiver) + "!", category='success')
                    return redirect(f"/{usr}")
            else:
                date_ = Users.query.filter_by(username=sender, creation_date=Users.creation_date).first()
                creation_date = date_.creation_date
                time_left = datetime.now() - creation_date
                if time_left.days > 3:
                    print("but he is not authenticated")
                    flash(f"Trial over. This user has been registered since {creation_date}.", category='error')
                    return redirect(url_for("auth.login"))
                elif receiver not in received:
                    new_click = Clicks(receiver=receiver, sender=sender, confirmed=False)
                    db.session.add(new_click)
                    db.session.commit()
                    flash('Klik sent to ' + str(receiver) + "!", category='success')
                    return redirect(f"/{usr}")
                else:
                    flash(f"Already klik'd {receiver}!", category='error')


        else:
            new_click = Clicks(receiver=receiver, sender=sender, confirmed=False)
            new_user = Users(username=sender, temppass=temp_pass)
            new_member = Memberships(type="Guest", username=sender)
            db.session.add(new_member)
            db.session.add(new_user)
            db.session.add(new_click)
            db.session.commit()
            flash('Klik sent to ' + str(receiver) + "!", category='success')
            return redirect(url_for("views.share", usr=usr, sendr=sender))

    return render_template("page.html", usr=usr.lower(), rows=new_rows, user=current_user, guest=sender, show = show, click_id = click_id)


@views.route("/x/x/welcome", methods=['GET'])
def welcome():
    ## Top Ten ##
    top_ten_today = Clicks.query.with_entities(Clicks.receiver, func.count(Clicks.receiver)).group_by(Clicks.receiver).all()
    top = sorted(top_ten_today, key=lambda x: x[1], reverse=True)
    top_ten = top[0:11]  # select top eleven
    tt = []
    i = 1

    for previous, current in zip(top, top[1:]):
        if previous[1] == current[1]:
            l = list(previous)
            if i == 1:
                l.append("🥇")
            if i == 2:
                l.append("🥈")
            if i == 3:
                l.append("🥉")
            l.append(i)
            tt.append(l)
        elif previous[1] != current[1]:
            l = list(previous)
            if i == 1:
                l.append("🥇")
            if i == 2:
                l.append("🥈")
            if i == 3:
                l.append("🥉")
            l.append(i)
            tt.append(l)
            i += 1
            if i == 11:
                break

    return render_template("welcome.html", top=tt, user=current_user)

@views.route("/<usr>/<sendr>", methods=['GET', 'POST'])
def share(usr, sendr):

   return render_template("share.html", usr=usr, sender=sendr, user=current_user)


@views.route("/<usr>/<sendr>/create", methods=['GET', 'POST'])
def create(usr, sendr):
    return render_template("share.html", usr=usr, sendr=sendr, user=current_user)

def click_counter(rows):

    if rows < 10:
        new_rows = "00000" + str(rows)
    elif 10 <= rows < 100:
        new_rows = "0000" + str(rows)
    elif 100 < rows < 1000:
        new_rows = "000" + str(rows)
    elif 1000 < rows < 10000:
        new_rows = "00" + str(rows)
    elif 10000 < rows < 100000:
        new_rows = "0" + str(rows)
    else:
        new_rows = str(rows)

    return new_rows