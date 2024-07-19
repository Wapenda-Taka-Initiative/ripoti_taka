from app import db
from datetime import datetime


class Comment(db.Model):
    """
    Model representing a comment.
    """

    __tablename__ = "comment"

    commentId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    content = db.Column(db.Text)
    userId = db.Column(
        db.Integer, db.ForeignKey("user.userId"), nullable=False
    )
    reportId = db.Column(
        db.Integer, db.ForeignKey("report.reportId"), nullable=False
    )
    dateCreated = db.Column(db.DateTime, default=datetime.utcnow)
    lastUpdated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user = db.relationship("User", back_populates="comments")
    report = db.relationship("Report", back_populates="comments")

    def __repr__(self):
        return f"Comment(commentId={self.commentId}, userId={self.userId})"

    @classmethod
    def create(cls, details={}):
        """
        Create a new comment.
        """
        comment = Comment(
            content=details.get("content"),
            userId=details.get("userId"),
            reportId=details.get("reportId"),
        )
        db.session.add(comment)
        db.session.commit()
        return comment

    def delete(self):
        """
        Delete the comment.
        """
        db.session.delete(self)
        db.session.commit()

    def updateDetails(self, details={}):
        """
        Update the details of the comment.
        """
        self.content = details.get("content", self.content)
        self.reportId = details.get("reportId", self.reportId)
        self.userId = details.get("userId", self.userId)

        db.session.commit()
        return self
