from flask import Flask, render_template, request, redirect, url_for, flash

from models.customer import Customer
from patterns.facade import RentalFacade
from patterns.singleton_logger import ActivityLogger
from patterns.strategy import daftar_harga_strategy
from storage import baca_data, simpan_data, buat_id

app = Flask(__name__)
app.secret_key = "rental-pbo-secret"   # dibutuhkan flash(); ganti untuk produksi

facade = RentalFacade()      # FACADE: satu pintu ke seluruh logika rental
logger = ActivityLogger()    # SINGLETON: satu logger bersama (selalu instance yang sama)


@app.template_filter('rupiah')
def rupiah_filter(value):
    try:
        return f"Rp {int(value):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "Rp 0"


def kembali(endpoint, pesan=None, kategori="success"):
    if pesan:
        flash(pesan, kategori)
    return redirect(url_for(endpoint))


# ==================== BERANDA ====================
@app.route("/")
def index():
    kendaraan = facade.daftar_kendaraan()
    return render_template(
        "index.html",
        customers=baca_data("customers.json"),
        kendaraan=kendaraan,
        rentals=baca_data("rentals.json"),
        pembayaran=baca_data("pembayaran.json"),
        stat=facade.ringkasan(),
    )


# ==================== CUSTOMER ====================
@app.route("/customer")
def customer():
    return render_template("customer.html", customers=baca_data("customers.json"))


@app.route("/customer/tambah", methods=["POST"])
def tambah_customer():
    customers = baca_data("customers.json")
    try:
        if any(c["username"].lower() == request.form["username"].strip().lower()
               for c in customers):
            raise ValueError("Username sudah dipakai.")
        if not request.form["nama"].strip():
            raise ValueError("Nama harus diisi.")
        baru = Customer(buat_id("C", customers), request.form["nama"].strip(),
                        request.form["username"].strip(), request.form["password"],
                        request.form["no_ktp"].strip(), request.form["no_hp"].strip())
    except ValueError as error:
        return kembali("customer", str(error), "error")
    customers.append(baru.get_data())
    simpan_data("customers.json", customers)
    logger.log("CUSTOMER_TAMBAH", f"{baru.id} {baru.nama}")
    return kembali("customer", "Customer berhasil ditambahkan.")


@app.route("/customer/edit/<id>", methods=["POST"])
def edit_customer(id):
    customers = baca_data("customers.json")
    for item in customers:
        if item["id"] == id:
            item["nama"] = request.form["nama"]
            item["username"] = request.form["username"]
            item["no_ktp"] = request.form["no_ktp"]
            item["no_hp"] = request.form["no_hp"]
            break
    simpan_data("customers.json", customers)
    logger.log("CUSTOMER_EDIT", id)
    return kembali("customer", "Data customer diperbarui.")


@app.route("/customer/hapus/<id>")
def hapus_customer(id):
    if any(r["customer_id"] == id and r["status"] == "Berjalan"
           for r in baca_data("rentals.json")):
        return kembali("customer", "Customer masih memiliki rental berjalan.", "error")
    simpan_data("customers.json",
                [c for c in baca_data("customers.json") if c["id"] != id])
    logger.log("CUSTOMER_HAPUS", id)
    return kembali("customer", "Customer dihapus.")


# ==================== KENDARAAN ====================
@app.route("/kendaraan")
def kendaraan():
    return render_template("kendaraan.html", kendaraan=facade.daftar_kendaraan())


@app.route("/kendaraan/tambah", methods=["POST"])
def tambah_kendaraan():
    jenis = request.form.get("jenis")
    kunci = "jumlah_kursi" if jenis == "Mobil" else "kapasitas_mesin"
    try:
        facade.tambah_kendaraan(
            jenis, request.form.get("merk", ""), request.form.get("nomor_plat", ""),
            float(request.form.get("harga_sewa", 0)), int(request.form.get(kunci, 0)))
    except ValueError as error:
        return kembali("kendaraan", str(error), "error")
    return kembali("kendaraan", "Kendaraan berhasil ditambahkan.")


@app.route("/kendaraan/edit/<id>", methods=["POST"])
def edit_kendaraan(id):
    kunci = "jumlah_kursi" if id.startswith("M") and not id.startswith("MT") else "kapasitas_mesin"
    try:
        facade.edit_kendaraan(
            id, request.form["merk"], request.form["nomor_plat"],
            float(request.form["harga_sewa"]), int(request.form.get(kunci, 0)))
    except ValueError as error:
        return kembali("kendaraan", str(error), "error")
    return kembali("kendaraan", "Kendaraan diperbarui.")


@app.route("/kendaraan/hapus/<id>")
def hapus_kendaraan(id):
    try:
        facade.hapus_kendaraan(id)
    except ValueError as error:
        return kembali("kendaraan", str(error), "error")
    return kembali("kendaraan", "Kendaraan dihapus.")


# ==================== RENTAL ====================
@app.route("/rental")
def rental():
    return render_template(
        "rental.html",
        customers=baca_data("customers.json"),
        kendaraan=facade.daftar_kendaraan(),
        rentals=facade.daftar_rental(),
        paket=daftar_harga_strategy(),
    )


@app.route("/rental/tambah", methods=["POST"])
def tambah_rental():
    try:
        r = facade.sewa(
            request.form["customer_id"], request.form["kendaraan_id"],
            request.form["tanggal_sewa"], int(request.form["lama_sewa"]),
            request.form.get("paket", "reguler"))
    except ValueError as error:
        return kembali("rental", str(error), "error")
    return kembali("rental", f"Rental {r.id} dibuat. Total {rupiah_filter(r.total_biaya)}.")


@app.route("/rental/edit/<id>", methods=["POST"])
def edit_rental(id):
    try:
        facade.edit_rental(id, request.form["tanggal_sewa"], int(request.form["lama_sewa"]))
    except ValueError as error:
        return kembali("rental", str(error), "error")
    return kembali("rental", "Rental diperbarui.")


@app.route("/rental/batal/<id>")
def batal_rental(id):
    try:
        facade.batalkan(id)
    except ValueError as error:
        return kembali("rental", str(error), "error")
    return kembali("rental", "Rental dibatalkan, kendaraan tersedia kembali.")


@app.route("/rental/hapus/<id>")
def hapus_rental(id):
    try:
        facade.hapus_rental(id)
    except ValueError as error:
        return kembali("rental", str(error), "error")
    return kembali("rental", "Rental dihapus.")


# ==================== PEMBAYARAN ====================
@app.route("/pembayaran")
def pembayaran():
    return render_template("pembayaran.html", rentals=facade.daftar_rental(),
                           pembayaran=baca_data("pembayaran.json"))


@app.route("/pembayaran/tambah", methods=["POST"])
def tambah_pembayaran():
    try:
        facade.bayar(request.form["rental_id"], float(request.form["jumlah"]),
                     request.form["metode"])
    except ValueError as error:
        return kembali("pembayaran", str(error), "error")
    return kembali("pembayaran", "Pembayaran berhasil dicatat.")


@app.route("/pembayaran/edit/<id>", methods=["POST"])
def edit_pembayaran(id):
    data = baca_data("pembayaran.json")
    try:
        jumlah = float(request.form["jumlah"])
        if jumlah <= 0:
            raise ValueError("Jumlah pembayaran harus lebih dari 0.")
    except ValueError as error:
        return kembali("pembayaran", str(error), "error")
    for item in data:
        if item["id"] == id:
            item["jumlah"] = jumlah
            item["metode"] = request.form["metode"]
            item["status"] = request.form["status"]
            break
    simpan_data("pembayaran.json", data)
    logger.log("PEMBAYARAN_EDIT", id)
    return kembali("pembayaran", "Pembayaran diperbarui.")


@app.route("/pembayaran/hapus/<id>")
def hapus_pembayaran(id):
    simpan_data("pembayaran.json",
                [p for p in baca_data("pembayaran.json") if p["id"] != id])
    logger.log("PEMBAYARAN_HAPUS", id)
    return kembali("pembayaran", "Pembayaran dihapus.")


# ==================== PENGEMBALIAN & DENDA ====================
@app.route("/pengembalian")
def pengembalian():
    return render_template("pengembalian.html", rentals=facade.daftar_rental(),
                           pengembalian=baca_data("pengembalian.json"),
                           denda=baca_data("denda.json"))


@app.route("/pengembalian/tambah", methods=["POST"])
def tambah_pengembalian():
    try:
        _, denda = facade.kembalikan(request.form["rental_id"],
                                     request.form["tanggal_kembali"], request.form["kondisi"])
    except ValueError as error:
        return kembali("pengembalian", str(error), "error")
    if denda:
        return kembali("pengembalian",
                       f"Pengembalian diproses. Denda otomatis: {rupiah_filter(denda.jumlah_denda)}.",
                       "warning")
    return kembali("pengembalian", "Pengembalian diproses tanpa denda.")


@app.route("/pengembalian/edit/<id>", methods=["POST"])
def edit_pengembalian(id):
    data = baca_data("pengembalian.json")
    for item in data:
        if item["id"] == id:
            item["tanggal_kembali"] = request.form["tanggal_kembali"]
            item["kondisi"] = request.form["kondisi"]
            break
    simpan_data("pengembalian.json", data)
    logger.log("PENGEMBALIAN_EDIT", id)
    return kembali("pengembalian", "Data pengembalian diperbarui.")


@app.route("/pengembalian/hapus/<id>")
def hapus_pengembalian(id):
    simpan_data("pengembalian.json",
                [p for p in baca_data("pengembalian.json") if p["id"] != id])
    logger.log("PENGEMBALIAN_HAPUS", id)
    return kembali("pengembalian", "Riwayat pengembalian dihapus.")


@app.route("/denda/hapus/<id>")
def hapus_denda(id):
    simpan_data("denda.json", [d for d in baca_data("denda.json") if d["id"] != id])
    logger.log("DENDA_HAPUS", id)
    return kembali("pengembalian", "Denda dihapus.")


# ==================== LOG AKTIVITAS ====================
@app.route("/log")
def log_aktivitas():
    return render_template("log.html", logs=logger.terbaru(100))


if __name__ == "__main__":
    app.run(debug=True)
