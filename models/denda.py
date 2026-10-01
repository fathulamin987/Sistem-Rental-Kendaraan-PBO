class Denda:

    def __init__(
        self,
        id,
        rental_id,
        hari_terlambat,
        jumlah_denda=0
    ):

        if hari_terlambat < 0:
            raise ValueError(
                "Hari terlambat tidak boleh negatif."
            )

        self.id = id
        self.rental_id = rental_id
        self.hari_terlambat = hari_terlambat
        self.jumlah_denda = jumlah_denda

    def hitung(self, tarif_per_hari=50000):

        if self.hari_terlambat < 0:
            raise ValueError(
                "Hari terlambat tidak valid."
            )

        self.jumlah_denda = (
            self.hari_terlambat * tarif_per_hari
        )

        return self.jumlah_denda

    def get_data(self):

        return {
            "id": self.id,
            "rental_id": self.rental_id,
            "hari_terlambat": self.hari_terlambat,
            "jumlah_denda": self.jumlah_denda
        }