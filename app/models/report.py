from datetime import datetime

from app import db


class Report(db.Model):
    __tablename__ = "report"
    reportId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    location = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    moderated = db.Column(db.Boolean, default=False)
    isResolved = db.Column(db.Boolean, default=False)
    dateCreated = db.Column(db.DateTime, default=datetime.utcnow)
    lastUpdated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    categoryId = db.Column(db.Integer, db.ForeignKey("category.categoryId"))
    userId = db.Column(db.Integer, db.ForeignKey("user.userId"))
    category = db.relationship("Category", backref="reports")
    user = db.relationship("User", backref="users")

    def __repr__(self):
        return (
            f"<Report(reportId={self.reportId}, description='"
            + f"{self.description}')>"
        )
