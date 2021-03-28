from .models import Clicks, Users
import requests
import json


def get_insta(username):
    url = "https://instagram40.p.rapidapi.com/account-info"

    querystring = {"username": username}

    headers = {
        'x-rapidapi-key': "53afb6313dmsh97077653d6f5a32p1f5d92jsnbf69e24ddeb6",
        'x-rapidapi-host': "instagram40.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    person = response.text
    person_dict = json.loads(person)

    return person_dict["profile_pic_url_hd"]


def find_matches(user):
    received = Clicks.query.filter_by(receiver=user.username).all()
    sent = Clicks.query.filter_by(sender=user.username).all()
    matches = []
    li = []
    sLi = []
    for r in received:
        username = r.sender
        user = Users.query.filter_by(username=username).first()
        li.append(user.username)
    for s in sent:
        sLi.append(s.receiver)
        if s.receiver in li:
            matches.append(s.receiver)
            print("Matched with " + str(s.receiver))
    return matches, sLi


#def message_updater:

