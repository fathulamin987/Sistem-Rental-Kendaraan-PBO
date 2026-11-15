"""
POLA 5 - FACADE (Structural)   | Buku: Bab 2, subbab 5, Listing 2.5

Masalah  : proses "sewa" dan "kembali" melibatkan banyak langkah sekaligus:
           validasi -> hitung harga -> ubah status kendaraan -> simpan rental
           -> hitung denda -> catat log. Di app.py versi lama semua langkah itu
           ditulis langsung di dalam route (panjang, berulang, rawan salah).
Solusi   : RentalFacade menyediakan satu pintu sederhana (sewa, kembalikan,
           bayar, batalkan, ringkasan). Route Flask cukup memanggil 1 method.

Pemetaan artefak UML -> kode:
    Client     -> app.py (route Flask)
    Facade     -> RentalFacade
    Subsystems -> storage, Factory (patterns/factory.py), Strategy
                  (patterns/strategy.py), State (patterns/state.py),
                  ActivityLogger (patterns/singleton_logger.py), models/*
"""
from datetime import date, timedelta

from models.denda import Denda
from models.pembayaran import Pembayaran
from models.pengembalian import Pengembalian
from models.rental import Rental
from patterns.factory import get_creator, semua_creator
from patterns.singleton_logger import ActivityLogger
from patterns.state import RentalContext, boleh_diedit
from patterns.strategy import (
    HargaContext,
    get_denda_strategy,
    get_harga_strategy,
    get_kerusakan_strategy,
    get_pembayaran_strategy,
)
from storage import baca_data, buat_id, simpan_data


def _tanggal(teks, nama="Tanggal"):
    try:
        return date.fromisoformat(teks)
    except (ValueError, TypeError):
        raise ValueError(f"{nama} tidak valid (gunakan format YYYY-MM-DD).")


def _rp(nilai):
    """Format rupiah Indonesia: 1500000 -> 'Rp 1.500.000'."""
    return f"Rp {int(nilai):,}".replace(",", ".")


class RentalFacade:

    def __init__(self):
        self.logger = ActivityLogger()  # Singleton

    # ------------------------------------------------------------ helper
    def _cari_kendaraan(self, kendaraan_id):
        """Cari di semua jenis kendaraan -> (creator, objek Kendaraan)."""
        for creator in semua_creator():
            for row in baca_data(creator.nama_file):
                if row["id"] == kendaraan_id:
                    return creator, creator.dari_dict(row)
        raise ValueError("Kendaraan tidak ditemukan.")

    def _set_tersedia(self, kendaraan_id, nilai):
        for creator in semua_creator():
            data = baca_data(creator.nama_file)
            for row in data:
                if row["id"] == kendaraan_id:
                    row["tersedia"] = nilai
                    simpan_data(creator.nama_file, data)
                    return

    def _cari_rental(self, rental_id):
        rentals = baca_data("rentals.json")
        for row in rentals:
            if row["id"] == rental_id:
                return rentals, row
        raise ValueError("Transaksi rental tidak ditemukan.")

    @staticmethod
    def jatuh_tempo(row):
        return _tanggal(row["tanggal_sewa"]) + timedelta(days=int(row["lama_sewa"]))

    # ------------------------------------------------------------ kendaraan
    def daftar_kendaraan(self):
        hasil = []
        for creator in semua_creator():
            hasil += baca_data(creator.nama_file)
        return hasil

    def tambah_kendaraan(self, jenis, merk, nomor_plat, harga_sewa, ekstra):
        creator = get_creator(jenis)  # FACTORY METHOD
        if any(k["nomor_plat"].lower() == nomor_plat.strip().lower()
               for k in self.daftar_kendaraan()):
            raise ValueError("Nomor plat sudah terdaftar.")
        data = baca_data(creator.nama_file)
        kendaraan = creator.buat(buat_id(creator.prefix_id, data),
                                 nomor_plat.strip(), merk.strip(), harga_sewa, ekstra)
        data.append(kendaraan.get_data())
        simpan_data(creator.nama_file, data)
        self.logger.log("KENDARAAN_TAMBAH", f"{kendaraan.id} {merk} ({nomor_plat})")
        return kendaraan

    def edit_kendaraan(self, kendaraan_id, merk, nomor_plat, harga_sewa, ekstra):
        creator, _ = self._cari_kendaraan(kendaraan_id)
        data = baca_data(creator.nama_file)
        for row in data:
            if row["id"] == kendaraan_id:
                # membuat ulang objek = ikut memakai validasi di model
                baru = creator.buat(kendaraan_id, nomor_plat.strip(), merk.strip(),
                                    harga_sewa, ekstra, row["tersedia"])
                row.update(baru.get_data())
        simpan_data(creator.nama_file, data)
        self.logger.log("KENDARAAN_EDIT", kendaraan_id)

    def hapus_kendaraan(self, kendaraan_id):
        creator, kendaraan = self._cari_kendaraan(kendaraan_id)
        if not kendaraan.tersedia:
            raise ValueError("Kendaraan sedang disewa, tidak dapat dihapus.")
        data = [k for k in baca_data(creator.nama_file) if k["id"] != kendaraan_id]
        simpan_data(creator.nama_file, data)
        self.logger.log("KENDARAAN_HAPUS", kendaraan_id)

    # ------------------------------------------------------------ tagihan
    def tagihan(self, rental_id):
        _, row = self._cari_rental(rental_id)
        denda = sum(d["jumlah_denda"] for d in baca_data("denda.json")
                    if d["rental_id"] == rental_id)
        terbayar = sum(p["jumlah"] for p in baca_data("pembayaran.json")
                       if p["rental_id"] == rental_id and p["status"] == "Lunas")
        total = row["total_biaya"] + denda
        sisa = max(0, total - terbayar)
        if sisa == 0:
            status = "Lunas"
        elif terbayar > 0:
            status = "Sebagian"
        else:
            status = "Belum Bayar"
        return {"total_biaya": row["total_biaya"], "total_denda": denda,
                "total_tagihan": total, "terbayar": terbayar,
                "sisa": sisa, "status_bayar": status}

    # ------------------------------------------------------------ rental
    def sewa(self, customer_id, kendaraan_id, tanggal_sewa, lama_sewa, paket="reguler"):
        customers = baca_data("customers.json")
        if not any(c["id"] == customer_id for c in customers):
            raise ValueError("Customer tidak ditemukan.")
        _tanggal(tanggal_sewa, "Tanggal sewa")

        creator, kendaraan = self._cari_kendaraan(kendaraan_id)
        strategy = get_harga_strategy(paket)                          # STRATEGY
        total = HargaContext(strategy).hitung_total(kendaraan, lama_sewa)
        kendaraan.sewa()  # ValueError jika sedang disewa

        rentals = baca_data("rentals.json")
        rental = Rental(buat_id("R", rentals), customer_id, kendaraan_id,
                        tanggal_sewa, lama_sewa, total, paket=strategy.kode)
        rentals.append(rental.get_data())
        simpan_data("rentals.json", rentals)
        self._set_tersedia(kendaraan_id, False)
        self.logger.log("RENTAL_BARU",
                        f"{rental.id}: {customer_id} sewa {kendaraan_id} "
                        f"{lama_sewa} hari ({strategy.kode}) = {_rp(total)}")
        return rental

    def edit_rental(self, rental_id, tanggal_sewa, lama_sewa):
        rentals, row = self._cari_rental(rental_id)
        if not boleh_diedit(row["status"]):                           # STATE
            raise ValueError("Hanya rental berstatus Berjalan yang dapat diedit.")
        _tanggal(tanggal_sewa, "Tanggal sewa")
        _, kendaraan = self._cari_kendaraan(row["kendaraan_id"])
        total = HargaContext(get_harga_strategy(row.get("paket", "reguler"))
                             ).hitung_total(kendaraan, lama_sewa)
        row.update(tanggal_sewa=tanggal_sewa, lama_sewa=lama_sewa, total_biaya=total)
        simpan_data("rentals.json", rentals)
        self.logger.log("RENTAL_EDIT", f"{rental_id}: {lama_sewa} hari, {_rp(total)}")

    def batalkan(self, rental_id):
        rentals, row = self._cari_rental(rental_id)
        rental = Rental(**row)
        RentalContext(rental).batalkan()                              # STATE
        row["status"] = rental.status
        simpan_data("rentals.json", rentals)
        self._set_tersedia(row["kendaraan_id"], True)
        self.logger.log("RENTAL_BATAL", rental_id)

    def hapus_rental(self, rental_id):
        rentals, row = self._cari_rental(rental_id)
        if row["status"] == "Berjalan":
            self._set_tersedia(row["kendaraan_id"], True)
        simpan_data("rentals.json", [r for r in rentals if r["id"] != rental_id])
        for nama in ("pembayaran.json", "pengembalian.json", "denda.json"):
            simpan_data(nama, [x for x in baca_data(nama) if x["rental_id"] != rental_id])
        self.logger.log("RENTAL_HAPUS", rental_id)

    def daftar_rental(self):
        """Data rental yang sudah dilengkapi nama, jatuh tempo, dan tagihan."""
        nama_cust = {c["id"]: c["nama"] for c in baca_data("customers.json")}
        label_kend = {k["id"]: f'{k["merk"]} ({k["nomor_plat"]})'
                      for k in self.daftar_kendaraan()}
        hasil = []
        for row in baca_data("rentals.json"):
            item = dict(row)
            jt = self.jatuh_tempo(row)
            item.update(
                customer_nama=nama_cust.get(row["customer_id"], "-"),
                kendaraan_label=label_kend.get(row["kendaraan_id"], "-"),
                jatuh_tempo=jt.isoformat(),
                paket_label=get_harga_strategy(row.get("paket", "reguler")).kode.title(),
                boleh_diedit=boleh_diedit(row["status"]),
                terlambat=(row["status"] == "Berjalan" and date.today() > jt),
            )
            item.update(self.tagihan(row["id"]))
            hasil.append(item)
        return hasil

    # ------------------------------------------------------------ pengembalian
    def kembalikan(self, rental_id, tanggal_kembali, kondisi):
        rentals, row = self._cari_rental(rental_id)
        tgl_kembali = _tanggal(tanggal_kembali, "Tanggal kembali")
        if tgl_kembali < _tanggal(row["tanggal_sewa"]):
            raise ValueError("Tanggal kembali tidak boleh sebelum tanggal sewa.")

        rental = Rental(**row)
        RentalContext(rental).selesaikan()                            # STATE

        creator, _ = self._cari_kendaraan(row["kendaraan_id"])
        hari_telat = max(0, (tgl_kembali - self.jatuh_tempo(row)).days)
        denda_telat = get_denda_strategy(creator.jenis).hitung(hari_telat)      # STRATEGY
        denda_rusak = get_kerusakan_strategy(kondisi).hitung(row["total_biaya"])  # STRATEGY

        daftar_pengembalian = baca_data("pengembalian.json")
        pengembalian = Pengembalian(buat_id("PG", daftar_pengembalian),
                                    rental_id, tanggal_kembali, kondisi)
        pengembalian.proses()
        daftar_pengembalian.append(pengembalian.get_data())
        simpan_data("pengembalian.json", daftar_pengembalian)

        denda = None
        if denda_telat + denda_rusak > 0:
            daftar_denda = baca_data("denda.json")
            ket = []
            if hari_telat:
                ket.append(f"Telat {hari_telat} hari: {_rp(denda_telat)}")
            if denda_rusak:
                ket.append(f"{kondisi}: {_rp(denda_rusak)}")
            denda = Denda(buat_id("D", daftar_denda), rental_id, hari_telat,
                          denda_telat + denda_rusak, "; ".join(ket))
            daftar_denda.append(denda.get_data())
            simpan_data("denda.json", daftar_denda)

        row["status"] = rental.status
        simpan_data("rentals.json", rentals)
        self._set_tersedia(row["kendaraan_id"], True)
        self.logger.log("PENGEMBALIAN",
                        f"{rental_id}: kondisi {kondisi}, telat {hari_telat} hari, "
                        f"denda {_rp(denda.jumlah_denda if denda else 0)}")
        return pengembalian, denda

    # ------------------------------------------------------------ pembayaran
    def bayar(self, rental_id, jumlah, metode):
        _, row = self._cari_rental(rental_id)
        if row["status"] == "Dibatalkan":
            raise ValueError("Rental sudah dibatalkan, tidak dapat dibayar.")
        sisa = self.tagihan(rental_id)["sisa"]
        if sisa <= 0:
            raise ValueError("Tagihan rental ini sudah lunas.")
        if jumlah > sisa:
            raise ValueError(f"Jumlah melebihi sisa tagihan ({_rp(sisa)}).")
        admin = get_pembayaran_strategy(metode).biaya_admin(jumlah)   # STRATEGY

        daftar = baca_data("pembayaran.json")
        pembayaran = Pembayaran(buat_id("P", daftar), rental_id, jumlah, metode,
                                biaya_admin=admin)
        pembayaran.bayar()
        daftar.append(pembayaran.get_data())
        simpan_data("pembayaran.json", daftar)
        self.logger.log("PEMBAYARAN",
                        f"{rental_id}: {_rp(jumlah)} via {metode} (admin {_rp(admin)})")
        return pembayaran

    # ------------------------------------------------------------ dashboard
    def ringkasan(self):
        rentals = self.daftar_rental()
        kendaraan = self.daftar_kendaraan()
        aktif = [r for r in rentals if r["status"] == "Berjalan"]
        return {
            "pendapatan": sum(p["jumlah"] for p in baca_data("pembayaran.json")
                              if p["status"] == "Lunas"),
            "piutang": sum(r["sisa"] for r in rentals if r["status"] != "Dibatalkan"),
            "rental_aktif": len(aktif),
            "rental_terlambat": sum(1 for r in aktif if r["terlambat"]),
            "kendaraan_tersedia": sum(1 for k in kendaraan if k["tersedia"]),
            "total_denda": sum(d["jumlah_denda"] for d in baca_data("denda.json")),
        }
