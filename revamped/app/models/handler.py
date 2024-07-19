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


class AnonymousHandler(flask_login.AnonymousUserMixin):
    def can(self, permission):
        """Ensures anonymous handler can never do action on the system"""
        return False

    def is_administrator(self):
        """
        Ensures anonymous handler can never perform an administrative action
        """
        return False


login_manager.anonymous_user = AnonymousHandler


class Handler(flask_login.UserMixin, db.Model):
    """
    Model representing a handler.
    """

    __tablename__ = "handler"

    handlerId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    handlerType = db.Column(db.String(255), nullable=False)
    passwordHash = db.Column(db.String(255))
    resourceAvailability = db.Column(db.Text)
    emailAddress = db.Column(db.String(255), nullable=False, unique=True)
    avatarHash = db.Column(db.String(255))
    phoneNumber = db.Column(db.String(255), nullable=False)
    isConfirmed = db.Column(db.Boolean, default=False)
    isApproved = db.Column(db.Boolean, default=False)
    dateCreated = db.Column(db.DateTime, default=datetime.utcnow)
    lastUpdated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    imageUrl = db.Column(db.String(255))

    reportAssignments = db.relationship(
        "ReportAssignment",
        back_populates="handler",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"Handler(handlerId={self.handlerId}, name='{self.name}', "
            + f"isApproved={self.isApproved})"
        )

    @classmethod
    def registerAccount(cls, details={}):
        """
        Create a new handler.
        """
        handler = Handler(
            name=details.get("name"),
            handlerType=details.get("handlerType"),
            resourceAvailability=details.get("resourceAvailability"),
            emailAddress=details.get("emailAddress"),
            phoneNumber=details.get("phoneNumber"),
            imageUrl=details.get("imageUrl"),
            password=details.get("password"),
        )
        db.session.add(handler)
        db.session.commit()
        return handler

    def delete(self):
        """
        Delete the handler.
        """
        db.session.delete(self)
        db.session.commit()

    def updateDetails(self, details={}):
        """
        Update the details of the handler.
        """
        self.name = details.get("name", self.name)
        self.handlerType = details.get("handlerType", self.handlerType)
        self.resourceAvailability = details.get(
            "resourceAvailability", self.resourceAvailability
        )
        self.emailAddress = details.get("emailAddress", self.emailAddress)
        self.phoneNumber = details.get("phoneNumber", self.phoneNumber)
        self.imageUrl = details.get("imageUrl", self.imageUrl)

        db.session.commit()
        return self

    def get_id(self):
        """
        Inherited HandlerMixin class method used to retrieve handler id for
            Flask-Login
        """
        return self.handlerId

    def login(self, details={}):
        """
        Authenticates the handler and logs them in when provided passsword is
            valid.

        :param details: dict - Contains password and remember_me boolean
            variable

        :return: tuple - Contains the return status and return message.
        """
        # Set handler type session variable
        flask.session.permanent = True
        flask.session["user_type"] = "handler"

        if self.verifyPassword(details.get("password", "")):
            flask_login.login_user(self, details.get("remember_me", False))
            return (1, "Login Successful")

        return (0, "Invalid password")

    def logout(self):
        """
        Terminate active handler session.

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
        Update the handler's last seen timestamp.

        :return: None
        """
        self.lastSeen = None
        db.session.commit()

    def getOffline(self):
        """
        Update the handler's last seen timestamp.

        :return: None
        """
        self.lastSeen = datetime.utcnow()
        db.session.commit()

    @hybrid_property
    def isOnline(self):
        """
        Check whether handler is online.

        :return: bool - True if handler is online, False otherwise.
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

    def updateProfileImage(self, image, folder):
        """
        Update handler's profile image.

        :param image: FileStorage - the image file to be uploaded.
        :param folder: str - the folder in which the image will be stored.

        :return self: Handler - the updated Handler instance.
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
        Deletes handler's profile image.

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
        Generate a Gravatar Url for the handler.

        This method generates a Gravatar Url for the handler based on
            their email address.

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
        Check whether a handler has a specific permission.

        :param permission: str - the permission to be checked.

        :return: bool - True if the handler has the specified permission,
            False otherwise.
        """
        role = Role.query.get(self.roleId)
        return role is not None and role.hasPermission(permission)

    def isAdministrator(self):
        """
        Check if the handler has administrator privileges.

        :return: bool - True if the handler has administrator privileges,
            False otherwise.
        """
        return self.can(Permission.ADMIN)

    def acceptHandling(self, report=None):
        """ """
        from .report_assignment import ReportAssignment

        details = {
            "reportId": report.reportId,
            "handlerId": self.handlerId,
        }
        report_assignment = ReportAssignment.create(details)

        report.status = "Assigned"
        db.session.add(report)
        db.session.commit()

        return report_assignment

    def registerSkill(self, details={}):
        """
        Registers a new skill.

        :param details: dict - Contains details used to instantiate
            the Skill object.

        :return skill: Skill - The newly created Skill instance.
        """
        # Check whether handler had the required permission
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
        # Check whether handler had the required permission
        ################################################
        #                UNDER CONSTRUCTION            #
        ################################################
        from .subject import Subject

        # Register new subject
        subject = Subject.create(details)
        return subject

    def deactivateHandler(self, handler=None):
        """
        Deactivates the given handler.

        :param handler: Handler - the handler to be deactivated.

        :return handler: Handler - the deactivated handler.
        """
        # Check whether handler had the required permission
        ################################################
        #                UNDER CONSTRUCTION            #
        ################################################
        if not handler:
            return

        handler.isActive = False
        db.session.commit()

        return handler

    def activateHandler(self, handler=None):
        """
        Activates the given handler.

        :param handler: Handler - the handler to be activated.

        :return handler: Handler - the activated handler.
        """
        if not handler:
            return

        handler.isActive = True
        db.session.commit()

        return handler

    def updatePhoneNumber(self, phoneNumber=None):
        """
        Update phone number.

        :param phoneNumber: str - the new phoneNumber to be saved.

        :return self: Handler - the updated Handler instance.
        """
        if not phoneNumber:
            return "Valid phone number must be provided", False

        self.phoneNumber = phoneNumber
        db.session.add(self)
        db.session.commit()

        return self

    def updatePassword(self, current_password, new_password):
        """
        Updates handler's password.

        :param current_password: str - Handler's current password.
        :param new_password: str - Handler's new password.

        :return self: Handler - the updated Handler instance.
        """
        if self.verifyPassword(current_password):
            self.password = new_password
            db.session.commit()

            return self

    def updateEmailAddress(self, emailAddress=None):
        """
        Update handler's email address.

        :param emailAddress: str - the new emailAddress to be saved.

        :return self: Handler - the updated Handler instance.
        """
        if not emailAddress:
            return "Valid email address must be provided", False

        existing_handler = Handler.query.filter_by(
            emailAddress=emailAddress
        ).first()
        if existing_handler and existing_handler.handlerId != self.handlerId:
            return "Handler already exists", False

        self.emailAddress = emailAddress
        self.isConfirmed = False

        db.session.add(self)
        db.session.commit()

        # send confirmation email to handler
        self.sendConfirmationEmail()

        return self

    def sendConfirmationEmail(self):
        """
        Send confirmation email to the handler.
        """
        token = self.generateConfirmationToken()
        confirmation_link = url_for(
            "accounts.handler_confirm",
            token=token,
            handler_id=self.handlerId,
            _scheme="https",
            _external=True,
        )

        subject = "Confirm Your Email Address Update"
        send_email(
            [self.emailAddress],
            subject,
            "email/email_confirmation",
            handlername=f"{self.firstName} {self.middleName} {self.lastName}",
            confirmation_link=confirmation_link,
        )

    def sendPasswordResetEmail(self):
        """
        Send password reset email to the handler.
        """
        token = self.generateConfirmationToken()
        reset_link = url_for(
            "accounts.handler_password_reset",
            token=token,
            _scheme="https",
            _external=True,
        )

        subject = "Password Reset Request"
        send_email(
            [self.emailAddress],
            subject,
            "email/password_reset",
            handler=self,
            reset_link=reset_link,
        )

    def generateConfirmationToken(self):
        """
        Generate a confirmation token.

        This method generates a token for confirming the handler's
            email address.

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
            handler = Handler.query.filter_by(emailAddress=data).first()

            return handler

        except Exception as e:
            logging.error(
                f"An error occured while loading the token: {str(e)}"
            )
            return None

    @staticmethod
    def resetPassword(token, new_password):
        """
        Reset handler's password.

        :param token: str - the token for password reset.
        :param new_password: str - the new password.
        """
        serializer = Serializer(flask.current_app.config["SECRET_KEY"])
        try:
            data = serializer.loads(token.encode("utf-8"))

        except Exception:
            return False

        handler = Handler.query.filter_by(emailAddress=data).first()
        if handler is None:
            return False

        handler.password = new_password
        db.session.add(handler)
        db.session.commit()

        return True
