from app import db


class Status(db.Model):
    __tablename__ = "status"
    statusId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))

    def __repr__(self):
        return f"<Status(statusId={self.statusId}, name='{self.name}')>"
