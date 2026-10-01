class Pembayaran:

    def __init__(
        self,
        id,
        rental_id,
        jumlah,
        metode,
        status="Belum Lunas"
    ):

        if jumlah <= 0:
            raise ValueError(
                "Jumlah pembayaran harus lebih dari 0."
            )

        self.id = id
        self.rental_id = rental_id
        self.jumlah = jumlah
        self.metode = metode
        self.status = status

    def bayar(self):

        if self.jumlah <= 0:
            raise ValueError(
                "Jumlah pembayaran tidak valid."
            )

        self.status = "Lunas"

        if self.status != "Lunas":
            raise ValueError(
                "Pembayaran gagal."
            )

    def get_data(self):

        return {
            "id": self.id,
            "rental_id": self.rental_id,
            "jumlah": self.jumlah,
            "metode": self.metode,
            "status": self.status
        }