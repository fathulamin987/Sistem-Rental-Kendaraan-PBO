from models.kendaraan import Kendaraan


class Mobil(Kendaraan):

    def __init__(
        self,
        id,
        nomor_plat,
        merk,
        harga_sewa,
        jumlah_kursi,
        tersedia=True
    ):

        super().__init__(
            id,
            nomor_plat,
            merk,
            harga_sewa,
            tersedia
        )

        if jumlah_kursi <= 0:
            raise ValueError(
                "Jumlah kursi harus lebih dari 0."
            )

        self.jumlah_kursi = jumlah_kursi

    def hitung_biaya(self, lama_sewa):

        if lama_sewa <= 0:
            raise ValueError(
                "Lama sewa harus lebih dari 0."
            )

        return self.get_harga_sewa() * lama_sewa

    def get_jenis(self):
        return "Mobil"

    def get_data(self):

        data = super().get_data()

        data["jumlah_kursi"] = self.jumlah_kursi

        return data