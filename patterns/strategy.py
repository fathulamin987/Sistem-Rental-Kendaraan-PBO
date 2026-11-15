"""
POLA 3 - STRATEGY (Behavioral)   | Buku: Bab 3, subbab E, Listing 3.3

Masalah  : aturan harga, denda, dan biaya pembayaran berbeda-beda dan bisa
           bertambah. Jika ditulis dengan if/elif di satu fungsi, kode sulit
           dirawat dan tiap aturan baru mengubah kode lama.
Solusi   : tiap aturan jadi kelas terpisah dengan antarmuka sama, dipilih saat
           runtime. Ada 3 keluarga strategi:

    1) HargaStrategy       : paket harga sewa (Reguler / Member / Mingguan)
    2) DendaStrategy       : tarif denda telat per jenis kendaraan
    3) KerusakanStrategy   : biaya kerusakan menurut kondisi saat dikembalikan
    4) PembayaranStrategy  : biaya admin per metode bayar

Pemetaan artefak UML -> kode (contoh keluarga Harga):
    Strategy         -> HargaStrategy (abstract)
    ConcreteStrategy -> HargaReguler, HargaMember, HargaMingguan
    Context          -> HargaContext
    Client           -> RentalFacade.sewa()  (memilih strategi dari form)
"""
from abc import ABC, abstractmethod


# ======================= 1. HARGA SEWA =======================
class HargaStrategy(ABC):
    kode = ""
    label = ""

    @abstractmethod
    def hitung(self, biaya_dasar, lama_sewa):
        """Kembalikan total biaya setelah aturan strategi diterapkan."""

    def keterangan(self):
        return self.label


class HargaReguler(HargaStrategy):
    kode, label = "reguler", "Reguler (tanpa diskon)"

    def hitung(self, biaya_dasar, lama_sewa):
        return biaya_dasar


class HargaMember(HargaStrategy):
    kode, label = "member", "Member (diskon 5%)"

    def hitung(self, biaya_dasar, lama_sewa):
        return biaya_dasar * 0.95


class HargaMingguan(HargaStrategy):
    kode, label = "mingguan", "Mingguan (diskon 10% jika sewa >= 7 hari)"

    def hitung(self, biaya_dasar, lama_sewa):
        return biaya_dasar * 0.90 if lama_sewa >= 7 else biaya_dasar


class HargaContext:
    def __init__(self, strategy: HargaStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: HargaStrategy):
        self.strategy = strategy

    def hitung_total(self, kendaraan, lama_sewa):
        # hitung_biaya() = polimorfisme Kendaraan (Mobil/Motor)
        dasar = kendaraan.hitung_biaya(lama_sewa)
        return round(self.strategy.hitung(dasar, lama_sewa))


_HARGA = {s.kode: s for s in (HargaReguler(), HargaMember(), HargaMingguan())}


def get_harga_strategy(kode):
    return _HARGA.get(kode, _HARGA["reguler"])


def daftar_harga_strategy():
    return list(_HARGA.values())


# ======================= 2. DENDA KETERLAMBATAN =======================
class DendaStrategy(ABC):
    @abstractmethod
    def tarif_per_hari(self):
        pass

    def hitung(self, hari_terlambat):
        return hari_terlambat * self.tarif_per_hari()


class DendaMobil(DendaStrategy):
    def tarif_per_hari(self):
        return 100000


class DendaMotor(DendaStrategy):
    def tarif_per_hari(self):
        return 30000


_DENDA = {"Mobil": DendaMobil(), "Motor": DendaMotor()}


def get_denda_strategy(jenis):
    return _DENDA[jenis]


# ======================= 3. BIAYA KERUSAKAN =======================
class KerusakanStrategy(ABC):
    @abstractmethod
    def hitung(self, total_biaya):
        pass


class KondisiBaik(KerusakanStrategy):
    def hitung(self, total_biaya):
        return 0


class KondisiRusakRingan(KerusakanStrategy):
    def hitung(self, total_biaya):
        return round(total_biaya * 0.10)


class KondisiRusakBerat(KerusakanStrategy):
    def hitung(self, total_biaya):
        return round(total_biaya * 0.30)


_KERUSAKAN = {
    "Baik": KondisiBaik(),
    "Rusak Ringan": KondisiRusakRingan(),
    "Rusak Berat": KondisiRusakBerat(),
}


def get_kerusakan_strategy(kondisi):
    try:
        return _KERUSAKAN[kondisi]
    except KeyError:
        raise ValueError("Kondisi kendaraan tidak valid.")


# ======================= 4. BIAYA ADMIN METODE BAYAR =======================
class PembayaranStrategy(ABC):
    @abstractmethod
    def biaya_admin(self, jumlah):
        pass


class BayarCash(PembayaranStrategy):
    def biaya_admin(self, jumlah):
        return 0


class BayarTransfer(PembayaranStrategy):
    def biaya_admin(self, jumlah):
        return 2500


class BayarEWallet(PembayaranStrategy):
    def biaya_admin(self, jumlah):
        return round(jumlah * 0.007)  # 0,7%


_BAYAR = {"Cash": BayarCash(), "Transfer": BayarTransfer(), "E-Wallet": BayarEWallet()}


def get_pembayaran_strategy(metode):
    try:
        return _BAYAR[metode]
    except KeyError:
        raise ValueError("Metode pembayaran tidak valid.")
