from models.user import User


class Customer(User):

    def __init__(
        self,
        id,
        nama,
        username,
        password,
        no_ktp,
        no_hp
    ):
        super().__init__(
            id,
            nama,
            username,
            password
        )

        self.no_ktp = no_ktp
        self.no_hp = no_hp

    def get_data(self):

        data = super().get_data()

        data["no_ktp"] = self.no_ktp
        data["no_hp"] = self.no_hp

        return data