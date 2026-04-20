class OrganizationInUseException(Exception):
    def __init__(self, departments=0, users=0):
        self.departments = departments
        self.users = users

        message = "Cannot delete organization because it has:"

        if departments:
            message += f"\n• {departments} department(s)"

        if users:
            message += f"\n• {users} user(s)"

        message += " are associated."

        super().__init__(message)

class DepartmentInUseException(Exception):
    def __init__(self, users=0):
        self.users = users

        message = "Cannot delete department because it has:"

        if users:
            message += f"\n• {users} user(s)"

        message += " are associated."

        super().__init__(message)

class UserHasRolesException(Exception):
    def __init__(self, roles_count: int):
        self.roles_count = roles_count
        super().__init__(
            f"Cannot delete user because it has {roles_count} role(s) assigned."
        )

class UserEmailAlreadyExistsException(Exception):
    def __init__(self, email):
        super().__init__(f"User with email '{email}' already exists.")
        self.email = email