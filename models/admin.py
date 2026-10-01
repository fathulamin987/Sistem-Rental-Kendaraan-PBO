from models.user import User


class Admin(User):

    def __init__(
        self,
        id,
        nama,
        username,
        password
    ):
        super().__init__(
            id,
            nama,
            username,
            password
        )

    def kelola_data(self):
        return "Admin mengelola data rental."

    def get_data(self):

        data = super().get_data()

        data["role"] = "Admin"

        return data