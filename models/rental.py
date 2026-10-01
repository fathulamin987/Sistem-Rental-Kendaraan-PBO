class Rental:

    def __init__(
        self,
        id,
        customer_id,
        kendaraan_id,
        tanggal_sewa,
        lama_sewa,
        total_biaya,
        status="Berjalan"
    ):

        if lama_sewa <= 0:
            raise ValueError(
                "Lama sewa harus lebih dari 0."
            )

        if total_biaya <= 0:
            raise ValueError(
                "Total biaya harus lebih dari 0."
            )

        self.id = id
        self.customer_id = customer_id
        self.kendaraan_id = kendaraan_id
        self.tanggal_sewa = tanggal_sewa
        self.lama_sewa = lama_sewa
        self.total_biaya = total_biaya
        self.status = status

    def selesai(self):

        if self.status != "Berjalan":
            raise ValueError(
                "Rental sudah selesai."
            )

        self.status = "Selesai"

        if self.status != "Selesai":
            raise ValueError(
                "Rental gagal diselesaikan."
            )

    def get_data(self):

        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "kendaraan_id": self.kendaraan_id,
            "tanggal_sewa": self.tanggal_sewa,
            "lama_sewa": self.lama_sewa,
            "total_biaya": self.total_biaya,
            "status": self.status
        }