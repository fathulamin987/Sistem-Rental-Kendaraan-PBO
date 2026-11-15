"""
POLA 1 - SINGLETON (Creational)   | Buku: Bab 1, Listing 1.1

Masalah  : setiap aksi penting (sewa, bayar, kembali, batal) perlu dicatat ke
           SATU log yang sama. Jika tiap modul membuat logger sendiri, catatan
           terpecah-pecah dan bisa saling menimpa saat menulis file.
Solusi   : ActivityLogger hanya boleh punya satu instance (lihat __new__).

Pemetaan artefak UML -> kode:
    Singleton -> class ActivityLogger  (_instance + __new__ = getInstance)
    Client    -> RentalFacade, app.py  (memanggil ActivityLogger().log(...))
"""
from datetime import datetime

from storage import baca_data, simpan_data

NAMA_FILE = "log.json"
BATAS_LOG = 200  # simpan maksimal 200 catatan terakhir


class ActivityLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def log(self, aksi, detail=""):
        data = baca_data(NAMA_FILE)
        data.append({
            "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "aksi": aksi,
            "detail": detail,
        })
        simpan_data(NAMA_FILE, data[-BATAS_LOG:])

    def terbaru(self, limit=50):
        return list(reversed(baca_data(NAMA_FILE)))[:limit]
