# -*- coding: utf-8 -*-
"""Menyusun daftar token menjadi pohon sintaksis.

Metodenya recursive descent: satu fungsi untuk tiap tingkat keutamaan, masing
masing memanggil tingkat yang lebih kuat di bawahnya. Susunan fungsi pada berkas
ini sengaja dibuat sejajar dengan tabel keutamaan pada Bagian 4 dokumen
milestone, supaya keduanya mudah dicocokkan:

    1 (kuat)   ¬     negasi              _satuan
    2          ∧     konjungsi           _konjungsi
    3          ∨     disjungsi           _disjungsi
    4          ⊕     disjungsi eksklusif _xor
    5          →     implikasi           _implikasi     (asosiatif kanan)
    6 (lemah)  ↔     biimplikasi         _biimplikasi

Tanda kurung selalu mengalahkan tabel di atas.
"""

from tokenizer import (BUKA, TUTUP, VARIABEL, OPERATOR, GalatSintaksis,
                       NEGASI, KONJUNGSI, DISJUNGSI, XOR, IMPLIKASI,
                       BIIMPLIKASI, pecah)


class Simpul:
    """Simpul pohon sintaksis.

    Simpul variabel memakai jenis "var" dan menyimpan namanya. Simpul operator
    memakai lambang operator sebagai jenis, dengan satu anak untuk negasi dan
    dua anak untuk operator lain.
    """

    def __init__(self, jenis, nama=None, kiri=None, kanan=None):
        self.jenis = jenis
        self.nama = nama
        self.kiri = kiri
        self.kanan = kanan

    def __repr__(self):
        if self.jenis == "var":
            return f"Var({self.nama})"
        if self.kanan is None:
            return f"({self.jenis} {self.kiri!r})"
        return f"({self.kiri!r} {self.jenis} {self.kanan!r})"


class _Pembaca:
    """Penunjuk baca pada daftar token."""

    def __init__(self, token, teks):
        self.token = token
        self.teks = teks
        self.i = 0

    def kini(self):
        return self.token[self.i] if self.i < len(self.token) else None

    def maju(self):
        t = self.kini()
        self.i += 1
        return t

    def akhir_teks(self):
        """Posisi tepat sesudah huruf terakhir, untuk pesan galat."""
        return len(self.teks)


def urai(teks):
    """Mengubah teks ekspresi menjadi pohon sintaksis."""
    token = pecah(teks)
    if not token:
        raise GalatSintaksis("ekspresi kosong", 0)

    baca = _Pembaca(token, teks)
    pohon = _biimplikasi(baca)

    sisa = baca.kini()
    if sisa is not None:
        if sisa.jenis == TUTUP:
            raise GalatSintaksis("tanda tutup kurung tidak ada pasangannya",
                                 sisa.posisi)
        raise GalatSintaksis(
            f"{sisa.nilai!r} tidak diharapkan di sini; "
            "operator kurang di antara dua bagian", sisa.posisi)

    return pohon


def _biimplikasi(baca):
    kiri = _implikasi(baca)
    while _operator_kini(baca) == BIIMPLIKASI:
        baca.maju()
        kanan = _implikasi(baca)
        kiri = Simpul(BIIMPLIKASI, kiri=kiri, kanan=kanan)
    return kiri


def _implikasi(baca):
    kiri = _xor(baca)
    if _operator_kini(baca) == IMPLIKASI:
        baca.maju()
        # Rekursi ke fungsi yang sama, bukan pengulangan, sebab implikasi
        # bersifat asosiatif kanan: p → q → r dibaca p → (q → r).
        kanan = _implikasi(baca)
        return Simpul(IMPLIKASI, kiri=kiri, kanan=kanan)
    return kiri


def _xor(baca):
    kiri = _disjungsi(baca)
    while _operator_kini(baca) == XOR:
        baca.maju()
        kanan = _disjungsi(baca)
        kiri = Simpul(XOR, kiri=kiri, kanan=kanan)
    return kiri


def _disjungsi(baca):
    kiri = _konjungsi(baca)
    while _operator_kini(baca) == DISJUNGSI:
        baca.maju()
        kanan = _konjungsi(baca)
        kiri = Simpul(DISJUNGSI, kiri=kiri, kanan=kanan)
    return kiri


def _konjungsi(baca):
    kiri = _satuan(baca)
    while _operator_kini(baca) == KONJUNGSI:
        baca.maju()
        kanan = _satuan(baca)
        kiri = Simpul(KONJUNGSI, kiri=kiri, kanan=kanan)
    return kiri


def _satuan(baca):
    """Membaca negasi, tanda kurung, atau variabel."""
    t = baca.kini()

    if t is None:
        raise GalatSintaksis("ekspresi terpotong; bagian kanan operator belum "
                             "ditulis", baca.akhir_teks())

    if t.jenis == OPERATOR and t.nilai == NEGASI:
        baca.maju()
        # Negasi dapat bertumpuk, misalnya ¬¬p, jadi ia memanggil dirinya.
        return Simpul(NEGASI, kiri=_satuan(baca))

    if t.jenis == OPERATOR:
        raise GalatSintaksis(
            f"operator {t.nilai!r} muncul tanpa bagian kiri", t.posisi)

    if t.jenis == BUKA:
        baca.maju()
        isi = _biimplikasi(baca)
        tutup = baca.kini()
        if tutup is None or tutup.jenis != TUTUP:
            raise GalatSintaksis("tanda tutup kurung belum ditulis",
                                 t.posisi)
        baca.maju()
        return isi

    if t.jenis == TUTUP:
        raise GalatSintaksis("tanda tutup kurung muncul terlalu awal",
                             t.posisi)

    baca.maju()
    return Simpul("var", nama=t.nilai)


def _operator_kini(baca):
    t = baca.kini()
    return t.nilai if t is not None and t.jenis == OPERATOR else None


def kumpulkan_variabel(pohon):
    """Mendaftar nama variabel unik, diurutkan supaya kolom tabel tetap."""
    nama = set()

    def telusuri(s):
        if s is None:
            return
        if s.jenis == "var":
            nama.add(s.nama)
            return
        telusuri(s.kiri)
        telusuri(s.kanan)

    telusuri(pohon)
    return sorted(nama)


def tulis(pohon):
    """Menulis ulang pohon menjadi teks berlambang baku.

    Tanda kurung hanya dipasang bila diperlukan, sehingga judul kolom pada tabel
    kebenaran tidak dipenuhi kurung yang tidak perlu.
    """
    return _tulis(pohon, 99)


# Angka keutamaan tiap operator. Makin kecil makin kuat, sejalan dengan tabel
# pada dokumen milestone.
_KUAT = {NEGASI: 1, KONJUNGSI: 2, DISJUNGSI: 3, XOR: 4, IMPLIKASI: 5,
         BIIMPLIKASI: 6}


def _tulis(s, batas):
    if s.jenis == "var":
        return s.nama

    if s.jenis == NEGASI:
        return NEGASI + _tulis(s.kiri, _KUAT[NEGASI])

    kuat = _KUAT[s.jenis]
    kiri = _tulis(s.kiri, kuat)
    # Implikasi asosiatif kanan, jadi anak kanannya boleh sekuat dirinya tanpa
    # perlu kurung; operator lain tidak.
    batas_kanan = kuat if s.jenis == IMPLIKASI else kuat - 1
    kanan = _tulis(s.kanan, batas_kanan)
    teks = f"{kiri} {s.jenis} {kanan}"
    return f"({teks})" if kuat > batas else teks
