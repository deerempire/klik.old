from flask import Blueprint, session, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Clicks, Users, Memberships
from .methods import find_matches, get_insta
from datetime import timedelta
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
    known_people = []
    people_count = []
    matches, sLi = find_matches(current_user)


    ### Queries ###
    rows = Clicks.query.filter_by(receiver=current_user.username).count()
    sent = Clicks.query.filter_by(sender=current_user.username).all()
    random_people = Clicks.query.filter(Clicks.receiver != current_user.username and Clicks.confirmed != 0).limit(30).all()

    ### People Suggestions ###
    comm_prob = randrange(30)

    if comm_prob < 5:
        received = Clicks.query.filter_by(receiver=current_user.username).limit(5).all()
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
    if rows < 10:
        new_rows = "00000" + str(rows)
    elif 10 < rows < 100:
        new_rows = "0000" + str(rows)
    elif 100 < rows < 1000:
        new_rows = "000" + str(rows)
    elif 1000 < rows < 10000:
        new_rows = "00" + str(rows)
    elif 10000 < rows < 100000:
        new_rows = "0" + str(rows)
    else:
        new_rows = str(rows)

    ### Sending a Click ###
    if request.method == 'POST':
        click = request.form.get('click')
        r = requests.get("http://www.instagram.com/" + str(click))

        if click in sLi:  # returns True or False
            flash("You already klik'd " + str(click) + ".", category='error')
        elif current_user.username == click:
            flash("You can't klik yourself!", category='error')
        elif r.status_code == 404:
            flash("Instagram user doesn't exist!", category='error')
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
    session.pop('guest', None)

    return redirect(url_for("views.home"))


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
    # rows= 29995
    if rows < 10:
        new_rows = "00000" + str(rows)
    elif 10 < rows < 100:
        new_rows = "0000" + str(rows)
    elif 100 < rows < 1000:
        new_rows = "000" + str(rows)
    elif 1000 < rows < 10000:
        new_rows = "00" + str(rows)
    elif 10000 < rows < 100000:
        new_rows = "0" + str(rows)
    else:
        new_rows = str(rows)

    if "guest" in session:
        sender = session["guest"]
        print("There's sender in session.")

    else:
        sender = None
        print("No sender in session.")

    if current_user.is_authenticated and usr == current_user.username:
        return redirect(url_for("views.home"))

    ### User Profile Photo ###

    r = requests.get("http://www.instagram.com/" + str(usr))
    print("STATUS $$$$$$$$$$$")
    print(r.status_code)
    time.sleep(0.5)
    if r.status_code == 500:
        photo = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT4gsPA0tTcRaIyay32GDKYlX0GCABN0BzMYw&usqp=CAU"
    print("NEW STATUS $$$$$$$$$$$")
    print(r.status_code)
    ### Sending a Click ###
    if request.method == 'POST':
        receiver = usr
        received = []
        r = requests.get("http://www.instagram.com/" + str(sender))

        sender = request.form.get('guest')

        session.permanent = True
        session['guest'] = sender

        if r.status_code == 404:
            flash("This Instagram user doesn't exist!", category='error')
        elif sender == receiver:
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
            else:
                print("but he is not authenticated")
                flash("This user is already registered. Please sign in!", category='error')
                return redirect(url_for("auth.login"))

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

    return render_template("page.html", usr=usr, rows=new_rows, user=current_user, guest=sender)


@views.route("/<usr>/<sendr>", methods=['GET', 'POST'])
def share(usr, sendr):

   return render_template("share.html", usr=usr, sender=sendr, user=current_user)


@views.route("/<usr>/<sendr>/create", methods=['GET', 'POST'])
def create(usr, sendr):
    return render_template("share.html", usr=usr, sendr=sendr, user=current_user)
