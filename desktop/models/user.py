class User:
    def __init__(self, account, password, gender):
        self.account = account
        self.password = password
        self.gender = gender
        self.last_room = None