class User:

    def __init__(self, id, nama, username, password):
        self.id = id
        self.nama = nama
        self.username = username
        self.__password = password

    def login(self, username, password):
        return self.username == username and self.__password == password

    def get_data(self):
        return {
            "id": self.id,
            "nama": self.nama,
            "username": self.username,
            "password": self.__password
        }