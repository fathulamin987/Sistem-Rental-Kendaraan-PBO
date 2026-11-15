"""
POLA 2 - FACTORY METHOD (Creational)   | Buku: Bab 1, Listing 1.2

Masalah  : di app.py versi lama, membuat objek kendaraan selalu diulang dengan
           if jenis == "Mobil": ... else: ... (di tambah kendaraan & tambah
           rental). Menambah jenis baru (mis. Bus) berarti mengubah banyak tempat.
Solusi   : tiap jenis kendaraan punya Creator sendiri. Client cukup memanggil
           get_creator(jenis) tanpa tahu kelas konkretnya (Open/Closed Principle).

Pemetaan artefak UML -> kode:
    Product          -> Kendaraan (models/kendaraan.py, abstract)
    ConcreteProduct  -> Mobil, Motor
    Creator          -> KendaraanCreator (abstract, ada factory method buat())
    ConcreteCreator  -> MobilCreator, MotorCreator
    Client           -> RentalFacade, app.py
"""
from abc import ABC, abstractmethod

from models.kendaraan import Kendaraan
from models.mobil import Mobil
from models.motor import Motor


class KendaraanCreator(ABC):
    jenis = ""
    nama_file = ""
    prefix_id = ""

    @abstractmethod
    def buat(self, id, nomor_plat, merk, harga_sewa, ekstra, tersedia=True) -> Kendaraan:
        """FACTORY METHOD: subclass menentukan kelas konkret yang dibuat."""

    def dari_dict(self, data) -> Kendaraan:
        """Rekonstruksi objek dari baris JSON."""
        return self.buat(
            data["id"], data["nomor_plat"], data["merk"], data["harga_sewa"],
            data[self.kunci_ekstra], data.get("tersedia", True),
        )

    kunci_ekstra = ""


class MobilCreator(KendaraanCreator):
    jenis = "Mobil"
    nama_file = "mobil.json"
    prefix_id = "M"
    kunci_ekstra = "jumlah_kursi"

    def buat(self, id, nomor_plat, merk, harga_sewa, ekstra, tersedia=True):
        return Mobil(id, nomor_plat, merk, harga_sewa, ekstra, tersedia)


class MotorCreator(KendaraanCreator):
    jenis = "Motor"
    nama_file = "motor.json"
    prefix_id = "MT"
    kunci_ekstra = "kapasitas_mesin"

    def buat(self, id, nomor_plat, merk, harga_sewa, ekstra, tersedia=True):
        return Motor(id, nomor_plat, merk, harga_sewa, ekstra, tersedia)


_CREATORS = {c.jenis: c for c in (MobilCreator(), MotorCreator())}


def get_creator(jenis) -> KendaraanCreator:
    try:
        return _CREATORS[jenis]
    except KeyError:
        raise ValueError(f"Jenis kendaraan '{jenis}' tidak dikenal.")


def semua_creator():
    return list(_CREATORS.values())
