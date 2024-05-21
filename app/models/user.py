import logging

import flask
import hashlib
from flask import url_for
from datetime import datetime
from flask_login import UserMixin
from flask_login import AnonymousUserMixin
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer

from app import login_manager
from app import db
from utilities.email import send_email


@login_manager.user_loader
def load_user(user_id):
    """
    Queries the database for a record of currently logged in user
    Returns User object containing info about logged in user
    """
    return User.query.get(int(user_id))


class AnonymousUser(AnonymousUserMixin):
    def can(self, permission):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


class User(UserMixin, db.Model):
    __tablename__ = "user"
    userId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstName = db.Column(db.String(30))
    middleName = db.Column(db.String(30))
    lastName = db.Column(db.String(30))

    userName = db.Column(db.String(50), unique=True, nullable=False)
    emailAddress = db.Column(db.String(100), nullable=False)
    passwordHash = db.Column(db.String(100), nullable=False)

    phoneNumber = db.Column(db.String(20))
    gender = db.Column(db.String(8), default="Female", nullable=False)
    locationAddress = db.Column(db.String(255), default="Nairobi West")

    about_me = db.Column(db.String(140))
    avatar_hash = db.Column(db.String(32))
    pointsAcquired = db.Column(db.Integer, default=0)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    dateCreated = db.Column(db.DateTime, default=datetime.utcnow)
    lastUpdated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    imageUrl = db.Column(db.String(200))
    confirmed = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)

    # relationships
    roleId = db.Column(db.Integer, db.ForeignKey("role.roleId"))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.pointsAcquired is None:
            self.pointsAcquired = 5

        # Assign default role to user
        if self.role is None:
            from .role import Role

            if (
                self.emailAddress
                == flask.current_app.config["ADMINISTRATOR_EMAIL"]
            ):
                self.role = Role.query.filter_by(name="Administrator").first()

            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

        # Generate avatar hash
        if self.emailAddress is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    def __repr__(self):
        return (
            f"<User(userId={self.userId}, userName='{self.userName}',"
            + f"emailAddress='{self.emailAddress}')>"
        )

    def get_id(self):
        return self.userId

    def gravatar_hash(self):
        return hashlib.md5(
            self.emailAddress.lower().encode("utf-8")
        ).hexdigest()

    def gravatar(self, size=100, default="identicon", rating="g"):
        url = "https://secure.gravatar.com/avatar"
        hash = self.avatar_hash or self.gravatar_hash()
        return "{url}/{hash}?s={size}&d={default}&r={rating}".format(
            url=url, hash=hash, size=size, default=default, rating=rating
        )

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.passwordHash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.passwordHash, password)

    @staticmethod
    def reset_password(token, new_password):
        """
        Reset user password.

        :param new_password: str - the new password.

        :return: bool - True if the password reset is successful, False
            otherwise.
        """
        serializer = Serializer(flask.current_app.config["SECRET_KEY"])
        try:
            data = serializer.loads(token.encode("utf-8"))

        except Exception:
            return False

        user = User.query.get(data.get("reset"))
        if user is None:
            return False

        user.password = new_password
        db.session.add(user)
        db.session.commit()

        return True

    def generateConfirmationToken(self):
        """
        Generate a confirmation token.

        This method generates a token for confirming the user's email address.

        :return: str - The confirmation token.
        """
        serializer = Serializer(flask.current_app.config["SECRET_KEY"])
        return serializer.dumps(self.emailAddress)

    def confirm(self, token, expiration=3600):
        """
        Uses a token to confirm the users's email address.

        :param token: str - Contains user's email address within it.
        :param expiration: int - Determines the validity of the provided token.

        :return: bool - True if confirmation is successful, False otherwise.
        """
        serializer = Serializer(flask.current_app.config["SECRET_KEY"])

        try:
            data = serializer.loads(token, max_age=expiration)

        except Exception:
            return False

        # Ensure that the link is not corrupted
        if data != self.emailAddress:
            return False

        # Update confirm status
        self.confirmed = True
        db.session.commit()

        return True

    def sendPasswordResetEmail(self):
        """
        Send password reset email to the user.
        """
        token = self.generateConfirmationToken()
        reset_link = url_for(
            "authentication.user_password_reset",
            token=token,
            _scheme="http",
            _external=True,
        )

        subject = "Password Reset Request"
        send_email(
            [self.emailAddress],
            subject,
            "email/password_reset",
            user=self,
            reset_link=reset_link,
        )

    def sendConfirmationEmail(self):
        """
        Send confirmation email to the user.
        """
        token = self.generateConfirmationToken()
        print(token)
        confirmation_link = url_for(
            "authentication.confirm",
            token=token,
            _scheme="http",
            _external=True,
        )
        print(confirmation_link)
        subject = "Email Confirmation"
        send_email(
            [self.emailAddress],
            subject,
            "email/confirm_account",
            user=self,
            confirmation_link=confirmation_link,
        )

    @staticmethod
    def confirmPasswordResetToken(token, expiration=3600):
        """
        Validate password request link provided.
        """
        serializer = Serializer(flask.current_app.config["SECRET_KEY"])

        try:
            data = serializer.loads(token, max_age=expiration)
            user = User.query.filter_by(emailAddress=data).first()

            return user

        except Exception as e:
            logging.error(
                f"An error occured while loading the token: {str(e)}"
            )
            return None

    @staticmethod
    def resetPassword(token, new_password, expiration=3600):
        """
        Reset user's password.

        :param token: str - the token for password reset.
        :param new_password: str - the new password.
        """
        serializer = Serializer(flask.current_app.config["SECRET_KEY"])
        try:
            data = serializer.loads(token, expiration)

        except Exception:
            return False

        user = User.query.filter_by(emailAddress=data).first()
        if user is None:
            return False

        user.password = new_password
        db.session.add(user)
        db.session.commit()

        return True
