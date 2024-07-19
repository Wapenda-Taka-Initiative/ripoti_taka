from app import db


class Category(db.Model):
    """
    Model representing a category.
    """

    __tablename__ = "category"

    categoryId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    reportCategories = db.relationship(
        "ReportCategory",
        back_populates="category",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"Category(categoryId={self.categoryId}, name='{self.name}')"

    @classmethod
    def create(cls, details={}):
        """
        Create a new category.
        """
        category = Category(
            name=details.get("name"),
            description=details.get("description"),
        )
        db.session.add(category)
        db.session.commit()
        return category

    def delete(self):
        """
        Delete the category.
        """
        db.session.delete(self)
        db.session.commit()

    def updateDetails(self, details={}):
        """
        Update the details of the category.
        """
        self.name = details.get("name", self.name)
        self.description = details.get("description", self.description)

        db.session.commit()
        return self
