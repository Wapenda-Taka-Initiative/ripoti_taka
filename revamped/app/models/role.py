from app import db


class Role(db.Model):
    """
    Model representing a role.
    """

    __tablename__ = "role"

    roleId = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    default = db.Column(db.Boolean, default=False)
    permissions = db.Column(db.BigInteger, default=0)

    # Back references
    users = db.relationship("User", back_populates="role")

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return f"Role(roleId = {self.roleId}, title = '{self.title}')"

    @staticmethod
    def insert_roles():
        """ """
        # Avoid circular imports
        from .permission import Permission

        # Assigning permissions to roles
        roles = {
            "Guest": [Permission.VISIT],
            "Reporter": [Permission.VISIT, Permission.MEMBER],
            "Administrator": [
                Permission.VISIT,
                Permission.MODERATE,
                Permission.MEMBER,
                Permission.ADMIN,
            ],
        }
        default_role = "Guest"

        for r in roles:
            role = Role.query.filter_by(title=r).first()
            if role is None:
                role = Role(title=r)

            role.resetPermissions()
            for perm in roles[r]:
                role.addPermission(perm)

            role.default = role.title == default_role
            db.session.add(role)

        db.session.commit()

    @classmethod
    def create(cls, details={}):
        """
        Create a new role.

        :param details: dict - a dictionary of role details to be saved.

        :return role: Role - the newly created Role instance.
        """
        role = Role(
            title=details.get("title"),
            description=details.get("description"),
        )

        db.session.add(role)
        db.session.commit()

        return role

    def delete(self):
        """
        Delete the role.
        """
        db.session.delete(self)
        db.session.commit()

    def updateDetails(self, details={}):
        """
        Update details of the role.

        :param details: dict - a dictionary of up to date role details.

        :return self: Role - the updated Role instance.
        """
        self.title = details.get("title")
        self.description = details.get("description")

        db.session.add(self)
        db.session.commit()

        return self

    def deactivate(self):
        """
        Deactivate a role.
        """
        if self.isActive:
            self.isActive = False

            db.session.add(self)
            db.session.commit()

        return self

    def addPermission(self, permission):
        """
        Add a permission to the role.

        :param permission: int - The permission to the added.
        """
        if not self.hasPermission(permission):
            self.permissions += permission

    def removePermission(self, permission):
        """
        Remove a permission from the role.

        :param permission: int - The permision to be removed.
        """
        if self.hasPermission(permission):
            self.permissions -= permission

    def resetPermissions(self):
        """
        Reset permissions of the role.
        """
        self.permissions = 0

    def hasPermission(self, permission):
        """
        Check if the role has a specific permission.

        :param permission: int - The permission to be checked.

        :return: bool - True if the role has the specified permission, False
            otherwise.
        """
        return self.permissions & permission == permission

    def getDetails(self):
        """
        Return role details.

        :return details: dict - a dictionary containing details of the Role
            instance.
        """
        details = {
            "roleId": self.roleId,
            "title": self.title,
            "description": self.description,
            "permissions": self.permissions,
            "isDefault": self.default,
            "usersCount": self.users.count(),
        }

        return details
