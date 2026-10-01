from abc import ABC, abstractmethod


class Kendaraan(ABC):

    def __init__(
        self,
        id,
        nomor_plat,
        merk,
        harga_sewa,
        tersedia=True
    ):

        if nomor_plat == "":
            raise ValueError("Nomor plat harus diisi.")

        if harga_sewa <= 0:
            raise ValueError("Harga sewa harus lebih dari 0.")

        self.id = id
        self.nomor_plat = nomor_plat
        self.merk = merk
        self.__harga_sewa = harga_sewa
        self.tersedia = tersedia

    def get_harga_sewa(self):
        return self.__harga_sewa

    def set_harga_sewa(self, harga):

        if harga <= 0:
            raise ValueError(
                "Harga sewa harus lebih dari 0."
            )

        self.__harga_sewa = harga

    @abstractmethod
    def hitung_biaya(self, lama_sewa):
        pass

    @abstractmethod
    def get_jenis(self):
        pass

    def sewa(self):

        if not self.tersedia:
            raise ValueError(
                "Kendaraan sedang disewa."
            )

        self.tersedia = False

    def kembalikan(self):

        self.tersedia = True

    def get_data(self):

        return {
            "id": self.id,
            "nomor_plat": self.nomor_plat,
            "merk": self.merk,
            "harga_sewa": self.__harga_sewa,
            "tersedia": self.tersedia,
            "jenis": self.get_jenis()
        }