from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    temppass = db.Column(db.String(150))
    username = db.Column(db.String(150), unique=True)
    creation_date = db.Column(db.DateTime(timezone=True), default=func.now())
    clicks = db.relationship('Clicks')
    messages = db.relationship('Messages')
    member = db.relationship('Memberships')


class Clicks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(150), db.ForeignKey('users.username'))
    receiver = db.Column(db.String(150))
    creation_date = db.Column(db.DateTime(timezone=True), default=func.now())
    confirmed = db.Column(db.Boolean)


class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000))
    username = db.Column(db.String(150), db.ForeignKey('users.username'))


class Memberships(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), db.ForeignKey('users.username'))
    start_date = db.Column(db.DateTime(timezone=True), default=func.now())
    end_date = db.Column(db.DateTime(timezone=True))
    type = db.Column(db.String(150))
