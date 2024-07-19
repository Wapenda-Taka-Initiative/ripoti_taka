import os
import logging
from datetime import datetime


import flask
import flask_login
from flask import url_for
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from sqlalchemy.ext.hybrid import hybrid_property
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer


from .role import Role
from .permission import Permission
from app import db
from app import login_manager
from utilities.file_saver import save_image
from utilities.file_saver import is_allowed_file
from utilities.securities import get_gravatar_hash
from utilities.email import send_email


class AnonymousUser(flask_login.AnonymousUserMixin):
    def can(self, permission):
        """Ensures anonymous user can never do action on the system"""
        return False

    def is_administrator(self):
        """Ensures anonymous user can never perform an administrative action"""
        return False


login_manager.anonymous_user = AnonymousUser


class User(flask_login.UserMixin, db.Model):
    """
    Model representing a user.
    """

    __tablename__ = "user"

    userId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    emailAddress = db.Column(db.String(255), nullable=False, unique=True)
    passwordHash = db.Column(db.String(255))
    username = db.Column(db.String(255), nullable=False)
    phoneNumber = db.Column(db.String(255), nullable=False)
    isConfirmed = db.Column(db.Boolean, default=False)
    isActive = db.Column(db.Boolean, default=False)
    avatarHash = db.Column(db.String(255))
    lastSeen = db.Column(db.DateTime)
    imageUrl = db.Column(db.String(255))
    dateCreated = db.Column(db.DateTime, default=datetime.utcnow)
    lastUpdated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Foreign Keys
    roleId = db.Column(
        db.Integer, db.ForeignKey("role.roleId"), nullable=False
    )

    # Back references
    role = db.relationship("Role", back_populates="users")
    reports = db.relationship(
        "Report", back_populates="user", cascade="all, delete-orphan"
    )
    comments = db.relationship(
        "Comment", back_populates="user", cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

        # Assign default role to user
        if self.roleId is None:
            if (
                self.emailAddress
                == flask.current_app.config["ADMINISTRATOR_MAIL"]
            ):
                role = Role.query.filter_by(title="Administrator").first()

            else:
                role = Role.query.filter_by(default=True).first()

            # Initialize role Id
            self.roleId = role.roleId

        # Generate avatar hash
        if self.emailAddress is not None and self.avatarHash is None:
            self.avatarHash = get_gravatar_hash(self.emailAddress)

    def __repr__(self):
        return (
            f"User(userId={self.userId}, username='{self.username}', "
            + f"isActive={self.isActive})"
        )

    @classmethod
    def registerAccount(cls, details={}):
        """
        Create a new user.
        """
        user = cls(
            emailAddress=details.get("emailAddress"),
            password=details.get("password"),
            username=details.get("username"),
            phoneNumber=details.get("phoneNumber"),
            imageUrl=details.get("imageUrl"),
        )
        db.session.add(user)
        db.session.commit()
        return user

    def delete(self):
        """
        Delete the user.
        """
        db.session.delete(self)
        db.session.commit()

    def updateDetails(self, details={}):
        """
        Update the details of the user.
        """
        self.emailAddress = details.get("emailAddress", self.emailAddress)
        self.passwordHash = details.get("passwordHash", self.passwordHash)
        self.username = details.get("username", self.username)
        self.phoneNumber = details.get("phoneNumber", self.phoneNumber)
        self.imageUrl = details.get("imageUrl", self.imageUrl)

        db.session.commit()
        return self

    def get_id(self):
        """
        Inherited UserMixin class method used to retrieve user id for
            Flask-Login
        """
        return self.userId

    def login(self, details={}):
        """
        Authenticates the user and logs them in when provided passsword is
            valid.

        :param details: dict - Contains password and remember_me boolean
            variable

        :return: tuple - Contains the return status and return message.
        """
        # Set user type session variable
        flask.session.permanent = True
        flask.session["user_type"] = "user"

        if self.verifyPassword(details.get("password", "")):
            flask_login.login_user(self, details.get("remember_me", False))
            return (1, "Login Successful")

        return (0, "Invalid password")

    def logout(self):
        """
        Terminate active user session.

        :return: tuple - Contains return status and return message.
        """
        flask_login.logout_user()
        return (1, "Logout successful")

    def verifyPassword(self, password):
        """
        Verify whether the provided password matches the hashed password.

        :param password: str - The password to be verified.

        :return: bool - True if the password is verified, False otherwise
        """
        return check_password_hash(self.passwordHash, password)

    @property
    def password(self):
        """
        Raise an AttributeError since the password is private only
        """
        raise AttributeError("password is not a readable attribute")

    def getOnline(self):
        """
        Update the user's last seen timestamp.

        :return: None
        """
        self.lastSeen = None
        db.session.commit()

    def getOffline(self):
        """
        Update the user's last seen timestamp.

        :return: None
        """
        self.lastSeen = datetime.utcnow()
        db.session.commit()

    @hybrid_property
    def isOnline(self):
        """
        Check whether user is online.

        :return: bool - True if user is online, False otherwise.
        """
        if not self.lastSeen:
            return False

        return True

    @password.setter
    def password(self, password):
        """
        Hash the client's password
        """
        self.passwordHash = generate_password_hash(password)

    def confirm(self, token, expiration=3600):
        """
        Confirm user's email.

        :return: bool - True if confirmation is successful, False otherwise.
        """
        from .role import Role

        serializer = Serializer(flask.current_app.config["SECRET_KEY"])

        try:
            data = serializer.loads(token, max_age=expiration)

        except Exception:
            return False

        # Ensure the link is not corrupted
        if data != self.userId:
            return False

        # Update confirm status
        self.isConfirmed = True

        # Update member status to member
        current_role = Role.query.filter_by(title="Guest").first()
        role = Role.query.filter_by(title="Member").first()
        if role and current_role and current_role.roleId == self.roleId:
            self.roleId = role.roleId

        db.session.add(self)
        db.session.commit()

        return True

    def updateProfileImage(self, image, folder):
        """
        Update user's profile image.

        :param image: FileStorage - the image file to be uploaded.
        :param folder: str - the folder in which the image will be stored.

        :return self: User - the updated User instance.
        """
        if not is_allowed_file(image):
            return (40, "Invalid Image")

        # Delete current image file from the file system
        if self.imageUrl:
            file_path = os.path.join(folder, self.imageUrl)
            os.remove(file_path)

        # Save image on file system
        saved_filename = save_image(image, folder)

        # Save filename in database
        self.imageUrl = saved_filename
        db.session.add(self)
        db.session.commit()

        return self

    def deleteProfileImage(self, folder):
        """
        Deletes user's profile image.

        :param folder: str - the folder in which the image will be stored.
        """
        # Delete actual file from the file system
        file_path = os.path.join(folder, self.imageUrl)
        os.remove(file_path)

        # Update the same on the database
        self.imageUrl = None
        db.session.add(self)
        db.session.commit()

    def getGravatar(self, size=100, default="identicon", rating="g"):
        """
        Generate a Gravatar Url for the user.

        This method generates a Gravatar Url for the user based on their email
        address.

        :param size: int - The size of the Gravatar image.
        :param default: str - The default image to be displayed if no
            Gravatar is found.
        :param rating: str - The content rating for the image.

        :return: str - The Gravatar Url.
        """
        url = "https://secure.gravatar.com/avatar"

        # Generate avatar hash if it does not exist
        if not self.avatarHash:
            self.avatarHash = get_gravatar_hash(self.emailAddress)

        # Retrieve it for usage
        hash = self.avatarHash
        return "{url}/{hash}?s={size}&d={default}&r={rating}".format(
            url=url, hash=hash, size=size, default=default, rating=rating
        )

    def can(self, permission):
        """
        Check whether a user has a specific permission.

        :param permission: str - the permission to be checked.

        :return: bool - True if the user has the specified permission,
            False otherwise.
        """
        role = Role.query.get(self.roleId)
        return role is not None and role.hasPermission(permission)

    def isAdministrator(self):
        """
        Check if the user has administrator privileges.

        :return: bool - True if the user has administrator privileges,
            False otherwise.
        """
        return self.can(Permission.ADMIN)

    def registerSkill(self, details={}):
        """
        Registers a new skill.

        :param details: dict - Contains details used to instantiate
            the Skill object.

        :return skill: Skill - The newly created Skill instance.
        """
        # Check whether user had the required permission
        ################################################
        #                UNDER CONSTRUCTION            #
        ################################################
        from .expert_details import Skill

        # Register new skill
        skill = Skill.register(details)
        return skill

    def registerSubject(self, details={}):
        """
        Registers a new subject.

        :param details: dict - Contains details used to instantiate
            the Subject object.

        :return subject: Subject - The newly created Subject instance.
        """
        # Check whether user had the required permission
        ################################################
        #                UNDER CONSTRUCTION            #
        ################################################
        from .subject import Subject

        # Register new subject
        subject = Subject.create(details)
        return subject

    def registerCategory(self, details={}):
        """
        Registers a new category for a particular subject.

        :param details: dict - Contains details used to instantiate the
            Category object.

        :return category: Category - The newly created Category instance
        """
        # Check whether user had the required permission
        ################################################
        #                UNDER CONSTRUCTION            #
        ################################################
        from .category import Category

        # Register new category
        category = Category.create(details)
        return category

    def registerPenalty(self, details={}):
        """
        Registers a new penalty for a particular subject.

        :param details: dict - Contains details used to instantiate the
            Penalty object.

        :return penalty: Penalty - The newly created Penalty instance
        """
        # Check whether user had the required permission
        ################################################
        #                UNDER CONSTRUCTION            #
        ################################################
        from .penalty import Penalty

        # Register new penalty
        penalty = Penalty.create(details)
        return penalty

    def deactivateUser(self, user=None):
        """
        Deactivates the given user.

        :param user: User - the user to be deactivated.

        :return user: User - the deactivated user.
        """
        # Check whether user had the required permission
        ################################################
        #                UNDER CONSTRUCTION            #
        ################################################
        if not user:
            return

        user.isActive = False
        db.session.commit()

        return user

    def activateUser(self, user=None):
        """
        Activates the given user.

        :param user: User - the user to be activated.

        :return user: User - the activated user.
        """
        if not user:
            return

        user.isActive = True
        db.session.commit()

        return user

    def deaccelerateSubmission(self):
        """ """
        return

    def banishExpert(self, expert):
        """ """
        if not self.can(Permission.BANISH_EXPERT):
            return

        expert.banish()
        db.session.commit()

        return

    def updatePhoneNumber(self, phoneNumber=None):
        """
        Update phone number.

        :param phoneNumber: str - the new phoneNumber to be saved.

        :return self: User - the updated User instance.
        """
        if not phoneNumber:
            return "Valid phone number must be provided", False

        self.phoneNumber = phoneNumber
        db.session.add(self)
        db.session.commit()

        return self

    def updatePassword(self, current_password, new_password):
        """
        Updates user's password.

        :param current_password: str - User's current password.
        :param new_password: str - User's new password.

        :return self: User - the updated User instance.
        """
        if self.verifyPassword(current_password):
            self.password = new_password
            db.session.commit()

            return self

    def updateEmailAddress(self, emailAddress=None):
        """
        Update user's email address.

        :param emailAddress: str - the new emailAddress to be saved.

        :return self: User - the updated User instance.
        """
        if not emailAddress:
            return "Valid email address must be provided", False

        existing_user = User.query.filter_by(emailAddress=emailAddress).first()
        if existing_user and existing_user.userId != self.userId:
            return "User already exists", False

        self.emailAddress = emailAddress
        self.isConfirmed = False

        db.session.add(self)
        db.session.commit()

        # send confirmation email to user
        self.sendConfirmationEmail()

        return self

    def sendConfirmationEmail(self):
        """
        Send confirmation email to the user.
        """
        token = self.generateConfirmationToken()
        confirmation_link = url_for(
            "accounts.user_confirm",
            token=token,
            user_id=self.userId,
            _scheme="https",
            _external=True,
        )

        subject = "Confirm Your Email Address Update"
        send_email(
            [self.emailAddress],
            subject,
            "email/email_confirmation",
            username=f"{self.firstName} {self.middleName} {self.lastName}",
            confirmation_link=confirmation_link,
        )

    def sendPasswordResetEmail(self):
        """
        Send password reset email to the user.
        """
        token = self.generateConfirmationToken()
        reset_link = url_for(
            "accounts.user_password_reset",
            token=token,
            _scheme="https",
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

    def generateConfirmationToken(self):
        """
        Generate a confirmation token.

        This method generates a token for confirming the user's email address.

        :return: str - The confirmation token.
        """
        serializer = Serializer(flask.current_app.config["SECRET_KEY"])
        return serializer.dumps(self.emailAddress)

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
    def resetPassword(token, new_password):
        """
        Reset user's password.

        :param token: str - the token for password reset.
        :param new_password: str - the new password.
        """
        serializer = Serializer(flask.current_app.config["SECRET_KEY"])
        try:
            data = serializer.loads(token.encode("utf-8"))

        except Exception:
            return False

        user = User.query.filter_by(emailAddress=data).first()
        if user is None:
            return False

        user.password = new_password
        db.session.add(user)
        db.session.commit()

        return True

    def makePayment(self, order, payment_details={}):
        """
        Make a payment for an order.
        """
        # TODO: Some logging

        payment = order.makePayment(payment_details)

        return payment
