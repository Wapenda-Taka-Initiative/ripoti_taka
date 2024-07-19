from app import db
from datetime import datetime


class ReportAssignment(db.Model):
    """
    Model representing a report assignment.
    """

    __tablename__ = "reportAssignment"

    reportAssignmentId = db.Column(
        db.Integer, autoincrement=True, primary_key=True
    )
    reportResolutionId = db.Column(
        db.Integer,
        db.ForeignKey("reportResolution.reportResolutionId"),
    )
    reportId = db.Column(
        db.Integer, db.ForeignKey("report.reportId"), nullable=False
    )
    handlerId = db.Column(
        db.Integer, db.ForeignKey("handler.handlerId"), nullable=False
    )
    estimatedCompletionDate = db.Column(db.Date)
    status = db.Column(db.Enum("Assigned", "In Progress", "Completed"))
    dateCompleted = db.Column(db.Date)
    dateCreated = db.Column(db.DateTime, default=datetime.utcnow)
    lastUpdated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    reportResolution = db.relationship(
        "ReportResolution", back_populates="reportAssignments"
    )
    report = db.relationship("Report", back_populates="reportAssignments")
    handler = db.relationship("Handler", back_populates="reportAssignments")

    def __repr__(self):
        return (
            "ReportAssignment(reportAssignmentId="
            + f"{self.reportAssignmentId}, status='{self.status}')"
        )

    @classmethod
    def create(cls, details={}):
        """
        Create a new report assignment.
        """
        report_assignment = ReportAssignment(
            reportResolutionId=details.get("reportResolutionId"),
            reportId=details.get("reportId"),
            handlerId=details.get("handlerId"),
            estimatedCompletionDate=details.get("estimatedCompletionDate"),
            status=details.get("status"),
            dateCompleted=details.get("dateCompleted"),
        )
        db.session.add(report_assignment)
        db.session.commit()
        return report_assignment

    def delete(self):
        """
        Delete the report assignment.
        """
        db.session.delete(self)
        db.session.commit()

    def updateDetails(self, details={}):
        """
        Update the details of the report assignment.
        """
        self.reportResolutionId = details.get(
            "reportResolutionId", self.reportResolutionId
        )
        self.reportId = details.get("reportId", self.reportId)
        self.handlerId = details.get("handlerId", self.handlerId)
        self.estimatedCompletionDate = details.get(
            "estimatedCompletionDate", self.estimatedCompletionDate
        )
        self.status = details.get("status", self.status)
        self.dateCompleted = details.get("dateCompleted", self.dateCompleted)

        db.session.commit()
        return self
