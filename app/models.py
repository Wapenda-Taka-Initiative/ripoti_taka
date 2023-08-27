from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Role(db.Model):
    __tablename__ = 'role'
    roleId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Role(roleId={self.roleId}, name='{self.name}')>"


class User(db.Model):
    __tablename__ = 'user'
    userId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userName = db.Column(db.String(50), unique=True, nullable=False)
    emailAddress = db.Column(db.String(100), nullable=False)
    passwordHash = db.Column(db.String(100), nullable=False)
    dateCreated = db.Column(db.DateTime, default=datetime.utcnow)
    lastUpdated = db.Column(db.DateTime, default=datetime.utcnow, 
            onupdate=datetime.utcnow)
    imageUrl = db.Column(db.String(200))
    roleId = db.Column(db.Integer, db.ForeignKey('role.roleId'))

    role = db.relationship('Role', backref='users')

    def __repr__(self):
        return f"<User(userId={self.userId}, userName='{self.userName}', emailAddress='{self.emailAddress}')>"


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
    dateAssigned = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='user_rewards')
    reward = db.relationship('Reward', backref='user_rewards')

    def __repr__(self):
        return f"<User_Reward(userRewardId={self.userRewardId}, userId={self.userId}, rewardId={self.rewardId})>"


class Category(db.Model):
    __tablename__ = 'category'
    categoryId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))

    def __repr__(self):
        return f"<Category(categoryId={self.categoryId}, name='{self.name}')>"


class Report(db.Model):
    __tablename__ = 'report'
    reportId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dateCreated = db.Column(db.DateTime, default=datetime.utcnow)
    lastUpdated = db.Column(db.DateTime, default=datetime.utcnow, 
            onupdate=datetime.utcnow)
    moderated = db.Column(db.Boolean, default=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    description = db.Column(db.Text)
    categoryId = db.Column(db.Integer, db.ForeignKey('category.categoryId'))
    isResolved = db.Column(db.Boolean, default=False)

    category = db.relationship('Category', backref='reports')

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
