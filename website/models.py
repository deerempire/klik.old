import time
import urllib

from flask import current_app, request

from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import jwt
from urllib.parse import urlparse, parse_qs, urlencode


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    temppass = db.Column(db.String(150))
    username = db.Column(db.String(150), unique=True)
    creation_date = db.Column(db.DateTime(timezone=True), default=func.now())
    clicks = db.relationship('Clicks')
    messages = db.relationship('Messages')
    member = db.relationship('Memberships')

    @property
    def login_jwt(self):
        """ returns a JWT which allows the current userId to login

        the JWT is short lived (LOGIN_URL_EXPIRES_IN seconds) """
        return jwt.encode(
            {
                "userId": self.id,
                "username": self.username,
                "action": 'login',
                "iss": request.base_url,
                "iat": int(time.time()),
                "exp": int(time.time()) + current_app.config["LOGIN_URL_EXPIRES_IN"],
            },
            current_app.config["SECRET_KEY"],
            algorithm=current_app.config["LOGIN_JWT_ALGORITHM"],
        )

    @property
    def login_url(self):
        """ returns a login url, with the login JWT token as argument """
        return "%s%s?%s" % (
            request.host_url.strip('/'),  # domain of the app
            current_app.config["LOGIN_URL"],  # login with jwt endpoint
            urllib.parse.urlencode({'loginToken': self.login_jwt}))  # jwt as arg

    def validate_login_jwt(self, token: str):
        """ check if the jwt should allow current user to log in """
        try:
            data = jwt.decode(
                token, current_app.secret_key, algorithms=[current_app.config["LOGIN_JWT_ALGORITHM"]]
            )
        except jwt.exceptions.ExpiredSignatureError:
            raise
        except jwt.exceptions.InvalidTokenError:
            return False

        try:
            if data['userId'] != self.id:
                return False
        except KeyError:
            return False

        try:
            if data['action'] != 'login':
                return False
        except KeyError:
            return False

        return True

    @classmethod
    def from_token(cls, token: str):
        """ retrieve the user object from the JWT (no verification) """
        try:
            data = jwt.decode(
                token,
                algorithms=[current_app.config["LOGIN_JWT_ALGORITHM"]],
                options={"verify_signature": False}
            )
        except jwt.exceptions.DecodeError:
            return None

        try:
            return cls.query.filter(cls.id == data['userId']).one_or_none()
        except KeyError:
            return None


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
