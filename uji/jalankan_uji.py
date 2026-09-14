# -*- coding: utf-8 -*-
"""Mencocokkan keluaran program dengan tabel acuan hitungan tangan.

Jalankan dari akar repositori:

    python uji/jalankan_uji.py

Acuannya berkas uji/kasus.txt, yang diisi tanpa menjalankan program. Skrip ini
hanya membandingkan; ia tidak memperbaiki apa pun. Bila ada selisih, yang
ditampilkan adalah nilai acuan dan nilai program berdampingan, supaya jelas
mana yang perlu ditelusuri.
"""

import os
import sys

# Modul inti berada di folder induk, jadi folder itu ditambahkan ke jalur impor.
AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, AKAR)

from tokenizer import GalatSintaksis                       # noqa: E402
from parser import urai, kumpulkan_variabel                # noqa: E402
from evaluator import tabel, kolom_akhir                   # noqa: E402
from klasifikasi import golongkan, periksa_argumen         # noqa: E402

BERKAS_KASUS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "kasus.txt")


class Hitungan:
    def __init__(self):
        self.lulus = 0
        self.gagal = 0
        self.pesan = []

    def benar(self):
        self.lulus += 1

    def salah(self, keterangan):
        self.gagal += 1
        self.pesan.append(keterangan)


def _huruf(kolom):
    return "".join("T" if n else "F" for n in kolom)


def uji_tabel(baris, hitung):
    """Memeriksa satu baris berjenis tabel: ekspresi, kolom akhir, golongan."""
    bagian = baris.split()
    # Golongan dan kolom acuan ada di dua ruas terakhir; sisanya ekspresi,
    # sebab ekspresi boleh memuat spasi.
    golongan_acuan = bagian[-1]
    kolom_acuan = bagian[-2]
    ekspresi = " ".join(bagian[:-2])

    try:
        pohon = urai(ekspresi)
    except GalatSintaksis as g:
        hitung.salah(f"{ekspresi!r} seharusnya sah, tetapi ditolak: {g.pesan}")
        return

    variabel = kumpulkan_variabel(pohon)
    _, isi = tabel(pohon, variabel)
    kolom_program = _huruf(kolom_akhir(isi))
    golongan_program = golongkan(kolom_akhir(isi))

    if kolom_program != kolom_acuan:
        hitung.salah(f"{ekspresi!r} kolom akhir berbeda\n"
                     f"        acuan   : {kolom_acuan}\n"
                     f"        program : {kolom_program}")
        return

    if golongan_program != golongan_acuan:
        hitung.salah(f"{ekspresi!r} golongan berbeda\n"
                     f"        acuan   : {golongan_acuan}\n"
                     f"        program : {golongan_program}")
        return

    hitung.benar()


def uji_argumen(baris, hitung):
    """Memeriksa satu baris berjenis argumen."""
    bagian = baris.rsplit(None, 1)
    status_acuan = bagian[1]
    badan = bagian[0]

    if "|-" not in badan:
        hitung.salah(f"baris argumen tanpa tanda |- : {baris!r}")
        return

    ruas_premis, ruas_konklusi = badan.split("|-", 1)
    teks_premis = [t.strip() for t in ruas_premis.split(";") if t.strip()]

    try:
        premis = [urai(t) for t in teks_premis]
        konklusi = urai(ruas_konklusi.strip())
    except GalatSintaksis as g:
        hitung.salah(f"{badan!r} seharusnya sah, tetapi ditolak: {g.pesan}")
        return

    hasil = periksa_argumen(premis, konklusi)
    status_program = "valid" if hasil.valid else "tidakvalid"

    if status_program != status_acuan:
        keterangan = (f"{badan.strip()!r} status berbeda\n"
                      f"        acuan   : {status_acuan}\n"
                      f"        program : {status_program}")
        if hasil.baris_penjatuh:
            nilai = ", ".join(f"{k}={'T' if v else 'F'}"
                              for k, v in sorted(hasil.baris_penjatuh.items()))
            keterangan += f"\n        baris penjatuh menurut program: {nilai}"
        hitung.salah(keterangan)
        return

    hitung.benar()


def uji_galat(baris, hitung):
    """Memeriksa bahwa masukan salah benar-benar ditolak."""
    ekspresi = baris.strip()
    try:
        urai(ekspresi)
    except GalatSintaksis:
        hitung.benar()
        return
    hitung.salah(f"{ekspresi!r} seharusnya ditolak, tetapi diterima program")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

    if not os.path.exists(BERKAS_KASUS):
        print(f"berkas kasus tidak ditemukan: {BERKAS_KASUS}")
        return 1

    hitung = Hitungan()

    with open(BERKAS_KASUS, encoding="utf-8") as f:
        for nomor, baris_mentah in enumerate(f, 1):
            baris = baris_mentah.strip()
            if not baris or baris.startswith("#"):
                continue

            kata, _, sisa = baris.partition(" ")
            kata = kata.lower()

            if kata == "tabel":
                uji_tabel(sisa.strip(), hitung)
            elif kata == "argumen":
                uji_argumen(sisa.strip(), hitung)
            elif kata == "galat":
                # Baris "galat" tanpa isi menguji ekspresi kosong.
                uji_galat(sisa, hitung)
            else:
                hitung.salah(f"baris {nomor}: jenis {kata!r} tidak dikenali")

    total = hitung.lulus + hitung.gagal
    print(f"Kasus uji dijalankan : {total}")
    print(f"Cocok dengan acuan   : {hitung.lulus}")
    print(f"Selisih              : {hitung.gagal}")

    if hitung.pesan:
        print()
        print("Selisih yang perlu ditelusuri:")
        for p in hitung.pesan:
            print(f"  - {p}")
        return 1

    print()
    print("Seluruh kasus uji cocok dengan tabel acuan hitungan tangan.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
