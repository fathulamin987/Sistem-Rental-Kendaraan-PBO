"""
POLA 4 - STATE (Behavioral)   | Buku: Bab 3, subbab G

Masalah  : status rental ("Berjalan", "Selesai") dulunya hanya string yang bisa
           diubah bebas lewat form edit, sehingga rental "Selesai" bisa
           dikembalikan lagi ke "Berjalan" dan data kendaraan jadi tidak sinkron.
Solusi   : setiap status adalah kelas. Perilaku (boleh selesai? boleh batal?
           boleh diedit?) ditentukan oleh state saat ini.

Alur status yang diizinkan:
        Berjalan --selesaikan()--> Selesai
        Berjalan --batalkan()----> Dibatalkan
        Selesai / Dibatalkan = status akhir (tidak bisa berubah lagi)

Pemetaan artefak UML -> kode:
    State         -> RentalState (abstract)
    ConcreteState -> BerjalanState, SelesaiState, DibatalkanState
    Context       -> RentalContext (membungkus objek Rental)
    Client        -> RentalFacade.kembalikan() / batalkan()
"""
from abc import ABC, abstractmethod


class RentalState(ABC):
    nama = ""

    @abstractmethod
    def selesaikan(self, context):
        pass

    @abstractmethod
    def batalkan(self, context):
        pass

    def boleh_diedit(self):
        return False


class BerjalanState(RentalState):
    nama = "Berjalan"

    def selesaikan(self, context):
        context.set_state(SelesaiState())

    def batalkan(self, context):
        context.set_state(DibatalkanState())

    def boleh_diedit(self):
        return True


class SelesaiState(RentalState):
    nama = "Selesai"

    def selesaikan(self, context):
        raise ValueError("Rental sudah selesai.")

    def batalkan(self, context):
        raise ValueError("Rental yang sudah selesai tidak dapat dibatalkan.")


class DibatalkanState(RentalState):
    nama = "Dibatalkan"

    def selesaikan(self, context):
        raise ValueError("Rental yang dibatalkan tidak dapat diselesaikan.")

    def batalkan(self, context):
        raise ValueError("Rental sudah dibatalkan.")


_STATES = {s.nama: s for s in (BerjalanState(), SelesaiState(), DibatalkanState())}


class RentalContext:
    def __init__(self, rental):
        self.rental = rental
        self.state = _STATES.get(rental.status, BerjalanState())

    def set_state(self, state: RentalState):
        self.state = state
        self.rental.status = state.nama

    def selesaikan(self):
        self.state.selesaikan(self)

    def batalkan(self):
        self.state.batalkan(self)

    def boleh_diedit(self):
        return self.state.boleh_diedit()


def boleh_diedit(status):
    return _STATES.get(status, DibatalkanState()).boleh_diedit()
