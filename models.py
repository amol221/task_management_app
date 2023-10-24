from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, username, password, _id=None):
        self.id = _id
        self.username = username
        self.password = password

class Task:
    def __init__(self, title, description, user_id, _id=None):
        self.id = _id
        self.title = title
        self.description = description
        self.user_id = user_id

