class User:
    def __init__(self, user_id, username, role, campus=None):
        self._user_id = user_id
        self._username = username
        self._role = role
        self._campus = campus

    def get_id(self):
        return self._user_id

    def get_username(self):
        return self._username

    def get_role(self):
        return self._role

    def get_campus(self):
        return self._campus

class Lecturer(User):
    def __init__(self, user_id, username, campus):
        super().__init__(user_id, username, "lecturer", campus)

class CampusAdmin(User):
    def __init__(self, user_id, username, campus):
        super().__init__(user_id, username, "admin", campus)

class SystemOperator(User):
    def __init__(self, user_id, username):
        super().__init__(user_id, username, "operator", None)