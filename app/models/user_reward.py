from app import db
from datetime import datetime


class UserReward(db.Model):
    __tablename__ = "user_reward"
    userRewardId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey("user.userId"))
    rewardId = db.Column(db.Integer, db.ForeignKey("reward.rewardId"))
    dateAssigned = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    isAssigned = db.Column(db.Boolean, default=False)

    user = db.relationship("User", backref="user_rewards")
    reward = db.relationship("Reward", backref="user_rewards")

    def __repr__(self):
        return (
            f"<User_Reward(userRewardId={self.userRewardId},"
            + f" userId={self.userId}, rewardId={self.rewardId})>"
        )
