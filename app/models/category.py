from app import db


class Category(db.Model):
    __tablename__ = "category"
    categoryId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f"<Category(categoryId={self.categoryId}, name='{self.name}')>"
