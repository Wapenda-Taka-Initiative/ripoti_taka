import hashlib
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import TimedJSONWebSignatureSerializer
from flask_login import AnonymousUserMixin, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from . import db, login_manager


class Permission:
    VISIT = 1
    MEMBER = 2
    MODERATE = 4
    ADMIN = 8


@login_manager.user_loader
def load_user(user_id):
    """
    Queries the database for a record of currently logged in user
    Returns User object containing info about logged in user
    """
    return User.query.get(int(user_id))


class Role(db.Model):
    __tablename__ = 'role'
    roleId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    default = db.Column(db.Boolean, default = False, index = True)
    permissions = db.Column(db.Integer)

    users = db.relationship('User', backref = 'role', lazy = 'dynamic')


    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0


    @staticmethod
    def insert_roles():
        roles = {
                'Guest' : [Permission.VISIT],
                'Member' : [Permission.VISIT, Permission.MEMBER],
                'Administrator' : [Permission.VISIT, Permission.MODERATE, 
                    Permission.MEMBER, Permission.ADMIN]
                }

        default_role = 'Guest'

        for r in roles:
            role = Role.query.filter_by(name = r).first()
            if role in None:
                role = Role(name = r)

            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)

            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()


    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm


    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm


    def reset_permissions(self):
        self.permissions = 0


    def has_permission(self, perm):
        return self.permissions & perm == perm


    def __repr__(self):
        return f"<Role(roleId={self.roleId}, name='{self.name}')>"


class Anonymous_User(AnonymousUserMixin):
    def can(self, permission):
        return False


    def is_administrator(self):
        return False


login_manager.anonymous_user = Anonymous_User


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    userId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstName = db.Column(db.String(30))
    middleName = db.Column(db.String(30))
    lastName = db.Column(db.String(30))

    userName = db.Column(db.String(50), unique = True, nullable = False)
    emailAddress = db.Column(db.String(100), nullable=False)
    passwordHash = db.Column(db.String(100), nullable=False)
    
    phoneNumber = db.Column(db.String(20))
    gender = db.Column(db.String(8), default = "Female", nullable = False)
    locationAddress = db.Column(db.String(255), default = "Nairobi West")

    about_me = db.Column(db.String(140))
    avatar_hash = db.Column(db.String(32))
    pointsAcquired = db.Column(db.Integer, default = 0)
    last_seen = db.Column(db.DateTime, default = datetime.utcnow)

    dateCreated = db.Column(db.DateTime, default=datetime.utcnow)
    lastUpdated = db.Column(db.DateTime, default=datetime.utcnow, 
            onupdate=datetime.utcnow)
    
    imageUrl = db.Column(db.String(200))
    confirmed = db.Column(db.Boolean, default = False)
    active = db.Column(db.Boolean, default = True)

    # relationships
    roleId = db.Column(db.Integer, db.ForeignKey('role.roleId'))
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.pointsAcquired is None:
            self.pointsAcquired = 5

        # Assign default role to user
        if self.role is None:
            if self.emailAddress == current_app.config['ADMINISTRATOR_EMAIL']:
                self.role = Role.query.filter_by(name = 'Administrator').first()

            if self.role is None:
                self.role = Role.query.filter_by(defualt = True).first()

        # Generate avatar hash
        if self.emailAddress is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()


    def __repr__(self):
        return f"<User(userId={self.userId}, userName='{self.userName}', emailAddress='{self.emailAddress}')>"

    
    def get_id(self):
        return self.userId

    
    def gravatar_hash(self):
        return hashlib.md5(self.emailAddress.lower().encode('utf-8')).hexdigest()


    def gravatar(self, size = 100, default = 'identicon', rating = 'g'):
        url = 'https://secure.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        return "{url}/{hash}?s={size}&d={default}&r={rating}".format(url = url,
                hash = hash, size = size, default = default, rating = rating)


    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")


    @password.setter
    def password(self, password):
        self.passwordHash = generate_password_hash(password)


    def confirm():
        serializer = Serializer(flask.current_app.config['SECRET_KEY'])
        try:
            data = serializer.loads(token.encode('utf-8'))
        except:
            return False

        if data.get('confirm' != self.userId):
            return False

        self.confirmed = True
        db.session.add(self)
        return True


    def verify_password(self, password):
        return check_password_hash(self.passwordHash, password)


    def get_reset_credential_token(self, expiration = 3600):
        serializer = Serializer(flask.current_app.config['SECRET_KEY'], 
                expiration)
        return s.dumps({'reset': self.userId}).decode('utf-8')


    def change_email(self, token):
        serializer = Serializer(flask.current_app.config['SECRET_KEY'])
        try:
            data = serializer.loads(token.encode('utf-8'))
        except:
            return False

        new_email = data.get('new_email')
        if new_email is None:
            return False

        if self.query.filter_by(emailAddress = new_email).first() is not None:
            return False

        self.emailAddress = new_email
        self.avatar_hash = self.gravatar_hash()
        db.session.add(self)
        return True


    @staticmethod
    def reset_password(token, new_password):
        serializer = Serializer(flask.current_app.config['SECRET_KEY'])
        try:
            data = serializer.loads(token.encode('utf-8'))
        except:
            return False

        user = User.query.get(data.get('reset'))
        if user is None:
            return False

        user.password = new_password
        db.session.add(user)
        return True


    @staticmethod
    def verify_reset_credential_token(token):
        try:
            id = jwt.decode(token, flask.current_app.config['SECRET_KEY'], 
                    algorithms = ['HS256'])['reset_credential']
        except:
            return
        
        return User.query.get(id)
    

    def generate_confirmation_token(self, expiration = 3600):
        s = serializer(flask.current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm' : self.userId}).decode('utf-8')


    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)


    def confirm(self, token):
        s = serializer(flask.current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False

        if data.get('confirm') != self.userId:
            return False

        self.confirmed = True
        db.session.add(self)

        return True


class Reward(db.Model):
    __tablename__ = 'reward'
    rewardId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    pointsRequired = db.Column(db.Integer)

    def __repr__(self):
        return f"<Reward(rewardId={self.rewardId}, name='{self.name}', pointsRequired={self.pointsRequired})>"


class User_Reward(db.Model):
    __tablename__ = 'user_reward'
    userRewardId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.userId'))
    rewardId = db.Column(db.Integer, db.ForeignKey('reward.rewardId'))
    dateAssigned = db.Column(db.DateTime, default=datetime.utcnow, 
            onupdate = datetime.utcnow)
    isAssigned = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref='user_rewards')
    reward = db.relationship('Reward', backref='user_rewards')

    def __repr__(self):
        return f"<User_Reward(userRewardId={self.userRewardId}, userId={self.userId}, rewardId={self.rewardId})>"


class Category(db.Model):
    __tablename__ = 'category'
    categoryId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable = False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f"<Category(categoryId={self.categoryId}, name='{self.name}')>"


class Report(db.Model):
    __tablename__ = 'report'
    reportId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    location = db.Column(db.String(255), nullable = False, index = True)
    description = db.Column(db.Text, nullable = False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    moderated = db.Column(db.Boolean, default=False)
    isResolved = db.Column(db.Boolean, default=False)
    dateCreated = db.Column(db.DateTime, default=datetime.utcnow)
    lastUpdated = db.Column(db.DateTime, default=datetime.utcnow, 
            onupdate=datetime.utcnow)

    categoryId = db.Column(db.Integer, db.ForeignKey('category.categoryId'))
    userId = db.Column(db.Integer, db.ForeignKey('user.userId'))
    category = db.relationship('Category', backref='reports')
    user = db.relationship('User', backref='users')

    def __repr__(self):
        return f"<Report(reportId={self.reportId}, description='{self.description}')>"


class Comment(db.Model):
    __tablename__ = 'comment'
    commentId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text)
    dateCreated = db.Column(db.DateTime, default=datetime.utcnow)
    lastUpdated = db.Column(db.DateTime, default=datetime.utcnow, 
            onupdate=datetime.utcnow)
    reportId = db.Column(db.Integer, db.ForeignKey('report.reportId'))

    report = db.relationship('Report', backref='comments')

    def __repr__(self):
        return f"<Comment(commentId={self.commentId}, content='{self.content}')>"


class Status(db.Model):
    __tablename__ = 'status'
    statusId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))

    def __repr__(self):
        return f"<Status(statusId={self.statusId}, name='{self.name}')>"


class Report_Status(db.Model):
    __tablename__ = 'report_status'
    reportStatusId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reportId = db.Column(db.Integer, db.ForeignKey('report.reportId'))
    statusId = db.Column(db.Integer, db.ForeignKey('status.statusId'))
    dateCreated = db.Column(db.DateTime, default=datetime.utcnow)

    report = db.relationship('Report', backref='report_statuses')
    status = db.relationship('Status', backref='report_statuses')

    def __repr__(self):
        return f"<Report_Status(reportStatusId={self.reportStatusId}, reportId={self.reportId}, statusId={self.statusId})>"
