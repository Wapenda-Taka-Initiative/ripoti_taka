from app import db
from .permission import Permission


class Role(db.Model):
    __tablename__ = "role"
    roleId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    users = db.relationship("User", backref="role", lazy="dynamic")

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            "Guest": [Permission.VISIT],
            "Member": [Permission.VISIT, Permission.MEMBER],
            "Administrator": [
                Permission.VISIT,
                Permission.MODERATE,
                Permission.MEMBER,
                Permission.ADMIN,
            ],
        }

        default_role = "Guest"

        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)

            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)

            role.default = role.name == default_role
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return f"<Role(roleId={self.roleId}, name='{self.name}')>"
