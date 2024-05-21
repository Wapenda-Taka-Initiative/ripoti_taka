from datetime import datetime

from app import db


class ReportStatus(db.Model):
    __tablename__ = "report_status"
    reportStatusId = db.Column(
        db.Integer, primary_key=True, autoincrement=True
    )
    reportId = db.Column(db.Integer, db.ForeignKey("report.reportId"))
    statusId = db.Column(db.Integer, db.ForeignKey("status.statusId"))
    dateCreated = db.Column(db.DateTime, default=datetime.utcnow)

    report = db.relationship("Report", backref="report_statuses")
    status = db.relationship("Status", backref="report_statuses")

    def __repr__(self):
        return (
            f"<Report_Status(reportStatusId={self.reportStatusId}, "
            + f"reportId={self.reportId}, statusId={self.statusId})>"
        )
