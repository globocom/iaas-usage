class User:

    def __init__(self, username, name, picture):
        self.id = username
        self.username = username
        self.name = name
        self.authenticated = True
        self.active = True
        self.anonymous = False
        self.roles = []
        self.picture = picture

    def is_active(self):
        return self.is_active

    def is_authenticated(self):
        return self.is_authenticated

    def is_anonymous(self):
        return self.is_anonymous

    def get_id(self):
        return self.id
