from app import db


class Reward(db.Model):
    __tablename__ = "reward"
    rewardId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    pointsRequired = db.Column(db.Integer)

    def __repr__(self):
        return (
            f"<Reward(rewardId={self.rewardId}, name='{self.name}',"
            + f" pointsRequired={self.pointsRequired})>"
        )
