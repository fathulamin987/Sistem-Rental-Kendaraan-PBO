class Pengembalian:

    def __init__(
        self,
        id,
        rental_id,
        tanggal_kembali,
        kondisi
    ):

        if tanggal_kembali == "":
            raise ValueError(
                "Tanggal pengembalian harus diisi."
            )

        self.id = id
        self.rental_id = rental_id
        self.tanggal_kembali = tanggal_kembali
        self.kondisi = kondisi

    def proses(self):

        if self.kondisi == "":
            raise ValueError(
                "Kondisi kendaraan harus diisi."
            )

        return "Pengembalian berhasil diproses."

    def get_data(self):

        return {
            "id": self.id,
            "rental_id": self.rental_id,
            "tanggal_kembali": self.tanggal_kembali,
            "kondisi": self.kondisi
        }