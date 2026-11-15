import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def baca_data(nama_file):
    path = os.path.join(DATA_DIR, nama_file)

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def simpan_data(nama_file, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, nama_file)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def buat_id(prefix, items):
    """ID berikutnya berdasarkan nomor TERBESAR (bukan len()+1),
    sehingga tidak bentrok setelah ada data yang dihapus."""
    pola = re.compile(r"^" + re.escape(prefix) + r"(\d+)$")
    nomor = [int(m.group(1)) for i in items if (m := pola.match(i["id"]))]
    return prefix + str(max(nomor, default=0) + 1).zfill(3)
