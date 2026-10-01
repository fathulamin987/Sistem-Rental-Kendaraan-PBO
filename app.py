from flask import Flask, render_template, request, redirect, url_for

from models.customer import Customer
from models.admin import Admin
from models.mobil import Mobil
from models.motor import Motor
from models.rental import Rental
from models.pembayaran import Pembayaran
from models.pengembalian import Pengembalian
from models.denda import Denda

from storage import baca_data, simpan_data

app = Flask(__name__)


# ==================================================
# CUSTOM JINJA FILTER (FORMAT RUPIAH: Rp 160.000)
# ==================================================

@app.template_filter('rupiah')
def rupiah_filter(value):
    try:
        return f"Rp {int(value):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "Rp 0"


# ==================================================
# BERANDA
# ==================================================

@app.route("/")
def index():
    customers = baca_data("customers.json")
    mobil = baca_data("mobil.json")
    motor = baca_data("motor.json")
    rentals = baca_data("rentals.json")
    pembayaran = baca_data("pembayaran.json")

    kendaraan = mobil + motor

    return render_template(
        "index.html",
        customers=customers,
        kendaraan=kendaraan,
        rentals=rentals,
        pembayaran=pembayaran
    )


# ==================================================
# CUSTOMER (CRUD)
# ==================================================

@app.route("/customer")
def customer():
    customers = baca_data("customers.json")
    return render_template("customer.html", customers=customers)


@app.route("/customer/tambah", methods=["POST"])
def tambah_customer():
    customers = baca_data("customers.json")
    customer = Customer(
        "C" + str(len(customers) + 1).zfill(3),
        request.form["nama"],
        request.form["username"],
        request.form["password"],
        request.form["no_ktp"],
        request.form["no_hp"]
    )
    customers.append(customer.get_data())
    simpan_data("customers.json", customers)
    return redirect(url_for("customer"))


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
    return redirect(url_for("customer"))


@app.route("/customer/hapus/<id>")
def hapus_customer(id):
    customers = baca_data("customers.json")
    customers = [item for item in customers if item["id"] != id]
    simpan_data("customers.json", customers)
    return redirect(url_for("customer"))


# ==================================================
# KENDARAAN (CRUD)
# ==================================================

@app.route("/kendaraan")
def kendaraan():
    mobil = baca_data("mobil.json")
    motor = baca_data("motor.json")
    return render_template("kendaraan.html", kendaraan=mobil + motor)


@app.route("/kendaraan/tambah", methods=["POST"])
def tambah_kendaraan():
    jenis = request.form.get("jenis")
    merk = request.form.get("merk")
    nomor_plat = request.form.get("nomor_plat")
    harga_sewa = float(request.form.get("harga_sewa", 0))

    try:
        if jenis == "Mobil":
            mobil_data = baca_data("mobil.json")
            jumlah_kursi = int(request.form.get("jumlah_kursi", 0))
            mobil = Mobil(
                "M" + str(len(mobil_data) + 1).zfill(3),
                nomor_plat,
                merk,
                harga_sewa,
                jumlah_kursi
            )
            mobil_data.append(mobil.get_data())
            simpan_data("mobil.json", mobil_data)
        elif jenis == "Motor":
            motor_data = baca_data("motor.json")
            kapasitas_mesin = int(request.form.get("kapasitas_mesin", 0))
            motor = Motor(
                "MT" + str(len(motor_data) + 1).zfill(3),
                nomor_plat,
                merk,
                harga_sewa,
                kapasitas_mesin
            )
            motor_data.append(motor.get_data())
            simpan_data("motor.json", motor_data)
    except ValueError as error:
        return str(error)

    return redirect(url_for("kendaraan"))


@app.route("/kendaraan/edit/<id>", methods=["POST"])
def edit_kendaraan(id):
    mobil_data = baca_data("mobil.json")
    motor_data = baca_data("motor.json")

    is_mobil = id.startswith("M") and not id.startswith("MT")

    if is_mobil:
        for item in mobil_data:
            if item["id"] == id:
                item["merk"] = request.form["merk"]
                item["nomor_plat"] = request.form["nomor_plat"]
                item["harga_sewa"] = float(request.form["harga_sewa"])
                item["jumlah_kursi"] = int(request.form.get("jumlah_kursi", item.get("jumlah_kursi", 4)))
                break
        simpan_data("mobil.json", mobil_data)
    else:
        for item in motor_data:
            if item["id"] == id:
                item["merk"] = request.form["merk"]
                item["nomor_plat"] = request.form["nomor_plat"]
                item["harga_sewa"] = float(request.form["harga_sewa"])
                item["kapasitas_mesin"] = int(request.form.get("kapasitas_mesin", item.get("kapasitas_mesin", 125)))
                break
        simpan_data("motor.json", motor_data)

    return redirect(url_for("kendaraan"))


@app.route("/kendaraan/hapus/<id>")
def hapus_kendaraan(id):
    mobil_data = baca_data("mobil.json")
    motor_data = baca_data("motor.json")

    mobil_data = [m for m in mobil_data if m["id"] != id]
    motor_data = [m for m in motor_data if m["id"] != id]

    simpan_data("mobil.json", mobil_data)
    simpan_data("motor.json", motor_data)

    return redirect(url_for("kendaraan"))


# ==================================================
# RENTAL (CRUD)
# ==================================================

@app.route("/rental")
def rental():
    customers = baca_data("customers.json")
    mobil = baca_data("mobil.json")
    motor = baca_data("motor.json")
    rentals = baca_data("rentals.json")
    return render_template("rental.html", customers=customers, kendaraan=mobil + motor, rentals=rentals)


@app.route("/rental/tambah", methods=["POST"])
def tambah_rental():
    mobil_data = baca_data("mobil.json")
    motor_data = baca_data("motor.json")
    rentals = baca_data("rentals.json")

    jenis = request.form["jenis"]
    kendaraan_id = request.form["kendaraan_id"]
    lama_sewa = int(request.form["lama_sewa"])
    kendaraan = None

    if jenis == "Mobil":
        for data in mobil_data:
            if data["id"] == kendaraan_id:
                kendaraan = Mobil(data["id"], data["nomor_plat"], data["merk"], data["harga_sewa"], data["jumlah_kursi"], data["tersedia"])
                break
    else:
        for data in motor_data:
            if data["id"] == kendaraan_id:
                kendaraan = Motor(data["id"], data["nomor_plat"], data["merk"], data["harga_sewa"], data["kapasitas_mesin"], data["tersedia"])
                break

    if kendaraan is None:
        return "Kendaraan tidak ditemukan."

    try:
        total = kendaraan.hitung_biaya(lama_sewa)
        kendaraan.sewa()

        rental = Rental(
            "R" + str(len(rentals) + 1).zfill(3),
            request.form["customer_id"],
            kendaraan_id,
            request.form["tanggal_sewa"],
            lama_sewa,
            total
        )

        rentals.append(rental.get_data())
        simpan_data("rentals.json", rentals)

        if jenis == "Mobil":
            for data in mobil_data:
                if data["id"] == kendaraan_id:
                    data["tersedia"] = False
            simpan_data("mobil.json", mobil_data)
        else:
            for data in motor_data:
                if data["id"] == kendaraan_id:
                    data["tersedia"] = False
            simpan_data("motor.json", motor_data)

        return redirect(url_for("rental"))

    except ValueError as error:
        return str(error)


@app.route("/rental/edit/<id>", methods=["POST"])
def edit_rental(id):
    rentals = baca_data("rentals.json")
    for item in rentals:
        if item["id"] == id:
            item["tanggal_sewa"] = request.form["tanggal_sewa"]
            item["lama_sewa"] = int(request.form["lama_sewa"])
            item["status"] = request.form["status"]
            break
    simpan_data("rentals.json", rentals)
    return redirect(url_for("rental"))


@app.route("/rental/hapus/<id>")
def hapus_rental(id):
    rentals = baca_data("rentals.json")
    rentals = [r for r in rentals if r["id"] != id]
    simpan_data("rentals.json", rentals)
    return redirect(url_for("rental"))


# ==================================================
# PEMBAYARAN (CRUD)
# ==================================================

@app.route("/pembayaran")
def pembayaran():
    rentals = baca_data("rentals.json")
    pembayaran_data = baca_data("pembayaran.json")
    return render_template("pembayaran.html", rentals=rentals, pembayaran=pembayaran_data)


@app.route("/pembayaran/tambah", methods=["POST"])
def tambah_pembayaran():
    pembayaran_data = baca_data("pembayaran.json")
    try:
        pembayaran = Pembayaran(
            "P" + str(len(pembayaran_data) + 1).zfill(3),
            request.form["rental_id"],
            float(request.form["jumlah"]),
            request.form["metode"]
        )
        pembayaran.bayar()
        pembayaran_data.append(pembayaran.get_data())
        simpan_data("pembayaran.json", pembayaran_data)
    except ValueError as error:
        return str(error)

    return redirect(url_for("pembayaran"))


@app.route("/pembayaran/edit/<id>", methods=["POST"])
def edit_pembayaran(id):
    pembayaran_data = baca_data("pembayaran.json")
    for item in pembayaran_data:
        if item["id"] == id:
            item["jumlah"] = float(request.form["jumlah"])
            item["metode"] = request.form["metode"]
            item["status"] = request.form["status"]
            break
    simpan_data("pembayaran.json", pembayaran_data)
    return redirect(url_for("pembayaran"))


@app.route("/pembayaran/hapus/<id>")
def hapus_pembayaran(id):
    pembayaran_data = baca_data("pembayaran.json")
    pembayaran_data = [p for p in pembayaran_data if p["id"] != id]
    simpan_data("pembayaran.json", pembayaran_data)
    return redirect(url_for("pembayaran"))


# ==================================================
# PENGEMBALIAN & DENDA (CRUD)
# ==================================================

@app.route("/pengembalian")
def pengembalian():
    rentals = baca_data("rentals.json")
    pengembalian_data = baca_data("pengembalian.json")
    denda_data = baca_data("denda.json")
    return render_template("pengembalian.html", rentals=rentals, pengembalian=pengembalian_data, denda=denda_data)


@app.route("/pengembalian/tambah", methods=["POST"])
def tambah_pengembalian():
    pengembalian_data = baca_data("pengembalian.json")
    rental_data = baca_data("rentals.json")
    mobil_data = baca_data("mobil.json")
    motor_data = baca_data("motor.json")

    try:
        pengembalian = Pengembalian(
            "PG" + str(len(pengembalian_data) + 1).zfill(3),
            request.form["rental_id"],
            request.form["tanggal_kembali"],
            request.form["kondisi"]
        )
        pengembalian.proses()
        pengembalian_data.append(pengembalian.get_data())
        simpan_data("pengembalian.json", pengembalian_data)

        rental_id = request.form["rental_id"]
        kendaraan_id = None

        for rental in rental_data:
            if rental["id"] == rental_id:
                kendaraan_id = rental["kendaraan_id"]
                rental["status"] = "Selesai"

        simpan_data("rentals.json", rental_data)

        for kendaraan in mobil_data:
            if kendaraan["id"] == kendaraan_id:
                kendaraan["tersedia"] = True

        for kendaraan in motor_data:
            if kendaraan["id"] == kendaraan_id:
                kendaraan["tersedia"] = True

        simpan_data("mobil.json", mobil_data)
        simpan_data("motor.json", motor_data)

    except ValueError as error:
        return str(error)

    return redirect(url_for("pengembalian"))


@app.route("/pengembalian/edit/<id>", methods=["POST"])
def edit_pengembalian(id):
    pengembalian_data = baca_data("pengembalian.json")
    for item in pengembalian_data:
        if item["id"] == id:
            item["tanggal_kembali"] = request.form["tanggal_kembali"]
            item["kondisi"] = request.form["kondisi"]
            break
    simpan_data("pengembalian.json", pengembalian_data)
    return redirect(url_for("pengembalian"))


@app.route("/pengembalian/hapus/<id>")
def hapus_pengembalian(id):
    pengembalian_data = baca_data("pengembalian.json")
    pengembalian_data = [p for p in pengembalian_data if p["id"] != id]
    simpan_data("pengembalian.json", pengembalian_data)
    return redirect(url_for("pengembalian"))


@app.route("/denda/tambah", methods=["POST"])
def tambah_denda():
    denda_data = baca_data("denda.json")
    try:
        denda = Denda(
            "D" + str(len(denda_data) + 1).zfill(3),
            request.form["rental_id"],
            int(request.form["hari_terlambat"])
        )
        denda.hitung()
        denda_data.append(denda.get_data())
        simpan_data("denda.json", denda_data)
    except ValueError as error:
        return str(error)

    return redirect(url_for("pengembalian"))


@app.route("/denda/hapus/<id>")
def hapus_denda(id):
    denda_data = baca_data("denda.json")
    denda_data = [d for d in denda_data if d["id"] != id]
    simpan_data("denda.json", denda_data)
    return redirect(url_for("pengembalian"))


if __name__ == "__main__":
    app.run(debug=True)