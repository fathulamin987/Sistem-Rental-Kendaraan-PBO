import json
import os


def baca_data(nama_file):
    path = os.path.join("data", nama_file)

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def simpan_data(nama_file, data):
    path = os.path.join("data", nama_file)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)