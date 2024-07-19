from app import db
from datetime import datetime


class Report(db.Model):
    """
    Model representing a report.
    """

    __tablename__ = "report"

    reportId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    userId = db.Column(
        db.Integer, db.ForeignKey("user.userId"), nullable=False
    )
    locationAddress = db.Column(db.String(255))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    wasteType = db.Column(db.String(255))
    description = db.Column(db.Text)
    severityLevel = db.Column(db.String(255))
    periodOfOccurrence = db.Column(db.String(255))
    status = db.Column(db.Enum("Pending", "Verified", "Assigned", "Resolved"))
    dateCreated = db.Column(db.DateTime, default=datetime.utcnow)
    lastUpdated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user = db.relationship("User", back_populates="reports")
    reportAssignments = db.relationship(
        "ReportAssignment",
        back_populates="report",
        cascade="all, delete-orphan",
    )
    comments = db.relationship(
        "Comment",
        back_populates="report",
        cascade="all, delete-orphan",
    )
    reportCategories = db.relationship(
        "ReportCategory", back_populates="report", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"Report(reportId={self.reportId}, status='{self.status}')"

    @classmethod
    def create(cls, details={}):
        """
        Create a new report.
        """
        report = Report(
            userId=details.get("userId"),
            locationAddress=details.get("locationAddress"),
            latitude=details.get("latitude"),
            longitude=details.get("longitude"),
            wasteType=details.get("wasteType"),
            description=details.get("description"),
            severityLevel=details.get("severityLevel"),
            periodOfOccurrence=details.get("periodOfOccurrence"),
            status=details.get("status", "pending"),
        )
        db.session.add(report)
        db.session.commit()
        return report

    def delete(self):
        """
        Delete the report.
        """
        db.session.delete(self)
        db.session.commit()

    def updateDetails(self, details={}):
        """
        Update the details of the report.
        """
        self.locationAddress = details.get(
            "locationAddress", self.locationAddress
        )
        self.latitude = details.get("latitude", self.latitude)
        self.longitude = details.get("longitude", self.longitude)
        self.wasteType = details.get("wasteType", self.wasteType)
        self.description = details.get("description", self.description)
        self.severityLevel = details.get("severityLevel", self.severityLevel)
        self.periodOfOccurrence = details.get(
            "periodOfOccurrence", self.periodOfOccurrence
        )
        self.status = details.get("status", self.status)

        db.session.commit()
        return self

    def assignCategory(self, categoryId):
        """
        Assigns a category to the report instance.

        :param categoryId: int - Category ID for Category to be assigned to
            instance.

        :return report_category: ReportCategory - Newly created
            category assignment instance.
        """
        from .report_category import ReportCategory

        details = {
            "categoryId": categoryId,
            "reportId": self.reportId,
        }
        report_category = ReportCategory.create(details)

        return report_category
