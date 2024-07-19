from app import db


class ReportCategory(db.Model):
    """
    Model representing a report-category relationship.
    """

    __tablename__ = "reportCategory"

    reportCategoryId = db.Column(
        db.Integer, autoincrement=True, primary_key=True
    )
    reportId = db.Column(
        db.Integer, db.ForeignKey("report.reportId"), nullable=False
    )
    categoryId = db.Column(
        db.Integer, db.ForeignKey("category.categoryId"), nullable=False
    )

    report = db.relationship("Report", back_populates="reportCategories")
    category = db.relationship("Category", back_populates="reportCategories")

    def __repr__(self):
        return f"ReportCategory(reportCategoryId={self.reportCategoryId})"

    @classmethod
    def create(cls, details={}):
        """
        Create a new report-category relationship.
        """
        report_category = ReportCategory(
            reportId=details.get("reportId"),
            categoryId=details.get("categoryId"),
        )
        db.session.add(report_category)
        db.session.commit()
        return report_category

    def delete(self):
        """
        Delete the report-category relationship.
        """
        db.session.delete(self)
        db.session.commit()

    def updateDetails(self, details={}):
        """
        Update the details of the report-category relationship.
        """
        self.reportId = details.get("reportId", self.reportId)
        self.categoryId = details.get("categoryId", self.categoryId)

        db.session.commit()
        return self
