from app import db
from datetime import datetime


class ReportResolution(db.Model):
    """
    Model representing a report resolution.
    """

    __tablename__ = "reportResolution"

    reportResolutionId = db.Column(
        db.Integer, autoincrement=True, primary_key=True
    )
    severityLevel = db.Column(db.Enum("high", "moderate", "low"))
    initialSituationDescription = db.Column(db.Text, nullable=False)
    stepsTaken = db.Column(db.Text, nullable=False)
    recommendations = db.Column(db.Text, nullable=False)
    potentialCauses = db.Column(db.Text, nullable=False)
    manPowerDetails = db.Column(db.Text, nullable=False)
    financialCosts = db.Column(db.Text, nullable=False)
    dateCompleted = db.Column(db.Date, nullable=False)
    dateCreated = db.Column(db.DateTime, default=datetime.utcnow)
    lastUpdated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    reportAssignments = db.relationship(
        "ReportAssignment",
        back_populates="reportResolution",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"ReportResolution(reportResolutionId={self.reportResolutionId}, "
            + f"severityLevel='{self.severityLevel}')"
        )

    @classmethod
    def create(cls, details={}):
        """
        Create a new report resolution.
        """
        report_resolution = ReportResolution(
            severityLevel=details.get("severityLevel"),
            initialSituationDescription=details.get(
                "initialSituationDescription"
            ),
            stepsTaken=details.get("stepsTaken"),
            recommendations=details.get("recommendations"),
            potentialCauses=details.get("potentialCauses"),
            manPowerDetails=details.get("manPowerDetails"),
            financialCosts=details.get("financialCosts"),
            dateCompleted=details.get("dateCompleted"),
        )
        db.session.add(report_resolution)
        db.session.commit()
        return report_resolution

    def delete(self):
        """
        Delete the report resolution.
        """
        db.session.delete(self)
        db.session.commit()

    def updateDetails(self, details={}):
        """
        Update the details of the report resolution.
        """
        self.severityLevel = details.get("severityLevel", self.severityLevel)
        self.initialSituationDescription = details.get(
            "initialSituationDescription", self.initialSituationDescription
        )
        self.stepsTaken = details.get("stepsTaken", self.stepsTaken)
        self.recommendations = details.get(
            "recommendations", self.recommendations
        )
        self.potentialCauses = details.get(
            "potentialCauses", self.potentialCauses
        )
        self.manPowerDetails = details.get(
            "manPowerDetails", self.manPowerDetails
        )
        self.financialCosts = details.get(
            "financialCosts", self.financialCosts
        )
        self.dateCompleted = details.get("dateCompleted", self.dateCompleted)

        db.session.commit()
        return self
