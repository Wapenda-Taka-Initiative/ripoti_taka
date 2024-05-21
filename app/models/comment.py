from app import db

from datetime import datetime


class Comment(db.Model):
    __tablename__ = "comment"
    commentId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text)
    dateCreated = db.Column(db.DateTime, default=datetime.utcnow)
    lastUpdated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    reportId = db.Column(db.Integer, db.ForeignKey("report.reportId"))

    report = db.relationship("Report", backref="comments")

    def __repr__(self):
        return (
            f"<Comment(commentId={self.commentId}, content='{self.content}')>"
        )
