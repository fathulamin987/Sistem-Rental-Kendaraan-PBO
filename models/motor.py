from models.kendaraan import Kendaraan


class Motor(Kendaraan):

    def __init__(
        self,
        id,
        nomor_plat,
        merk,
        harga_sewa,
        kapasitas_mesin,
        tersedia=True
    ):

        super().__init__(
            id,
            nomor_plat,
            merk,
            harga_sewa,
            tersedia
        )

        if kapasitas_mesin <= 0:
            raise ValueError(
                "Kapasitas mesin harus lebih dari 0."
            )

        self.kapasitas_mesin = kapasitas_mesin

    def hitung_biaya(self, lama_sewa):

        if lama_sewa <= 0:
            raise ValueError(
                "Lama sewa harus lebih dari 0."
            )

        return self.get_harga_sewa() * lama_sewa

    def get_jenis(self):
        return "Motor"

    def get_data(self):

        data = super().get_data()

        data["kapasitas_mesin"] = self.kapasitas_mesin

        return data