# -*- coding: utf-8 -*-
"""Simulator tabel kebenaran dan verifikator argumen.

Berkas ini satu-satunya yang mengetahui tentang terminal. Modul tokenizer.py
sampai klasifikasi.py tidak memuat satu pun perintah cetak, sehingga tampilan
lain dapat ditambahkan tanpa mengubah logikanya.

Cara menjalankan:

    python simulator.py tabel "(p -> q) & ~q"
    python simulator.py argumen --premis "p -> q" --premis "~q" --konklusi "~p"

Tambahkan --ascii apabila terminal tidak dapat menampilkan lambang logika.
"""

import argparse
import sys

from tokenizer import GalatSintaksis
from parser import urai, kumpulkan_variabel, tulis
from evaluator import tabel, kolom_akhir
from klasifikasi import (golongkan, keterangan_golongan, periksa_argumen,
                         bentuk_implikasi_gabungan)

# Padanan ASCII untuk terminal yang tidak dapat menampilkan lambang logika.
# Terminal Windows bawaan memakai penyandian cp1252 yang tidak memuat ∧, ∨,
# dan ⊕, sehingga program akan berhenti dengan galat bila lambang itu dicetak
# apa adanya.
PADANAN_ASCII = {
    "¬": "~", "∧": "&", "∨": "|", "⊕": "xor", "→": "->", "↔": "<->",
    "₁": "1", "ₙ": "n", "…": "...",
}


def _siapkan_keluaran():
    """Mencoba menyalakan UTF-8 pada keluaran baku.

    Mengembalikan True bila lambang logika dapat dicetak. Python 3.7 ke atas
    menyediakan reconfigure; bila gagal, program beralih ke mode ASCII.
    """
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        return True
    except (AttributeError, OSError):
        return _sanggup_lambang()


def _sanggup_lambang():
    penyandian = getattr(sys.stdout, "encoding", None) or "ascii"
    try:
        "¬∧∨⊕→↔".encode(penyandian)
        return True
    except (UnicodeEncodeError, LookupError):
        return False


def _ascii(teks):
    for lambang, padanan in PADANAN_ASCII.items():
        teks = teks.replace(lambang, padanan)
    return teks


class Penulis:
    """Pencetak yang menyesuaikan diri dengan kemampuan terminal."""

    def __init__(self, pakai_lambang):
        self.pakai_lambang = pakai_lambang

    def olah(self, teks):
        return teks if self.pakai_lambang else _ascii(teks)

    def cetak(self, teks=""):
        print(self.olah(teks))


def cetak_tabel(tulis_ke, judul, baris):
    """Mencetak tabel kebenaran dengan garis pembatas dari karakter biasa.

    Garis memakai tanda +, -, dan |, bukan karakter penggambar kotak, supaya
    tabel tetap rapi pada terminal apa pun dan pada rekaman video.
    """
    judul = [tulis_ke.olah(j) for j in judul]
    isi = [["T" if n else "F" for n in b] for b in baris]

    lebar = [max(len(judul[i]), 1) for i in range(len(judul))]

    pembatas = "+" + "+".join("-" * (l + 2) for l in lebar) + "+"

    tulis_ke.cetak(pembatas)
    tulis_ke.cetak("| " + " | ".join(j.center(lebar[i])
                                     for i, j in enumerate(judul)) + " |")
    tulis_ke.cetak(pembatas)
    for b in isi:
        tulis_ke.cetak("| " + " | ".join(n.center(lebar[i])
                                         for i, n in enumerate(b)) + " |")
    tulis_ke.cetak(pembatas)


def cetak_galat(tulis_ke, teks_asli, galat):
    """Mencetak pesan galat beserta penunjuk letak kesalahannya."""
    tulis_ke.cetak("Masukan ditolak.")
    tulis_ke.cetak()
    tulis_ke.cetak(f"    {teks_asli}")
    # Penunjuk dipasang tepat di bawah huruf yang menyebabkan penolakan.
    tulis_ke.cetak("    " + " " * galat.posisi + "^")
    tulis_ke.cetak()
    tulis_ke.cetak(f"Kolom {galat.posisi + 1}: {galat.pesan}")


def perintah_tabel(argumen, tulis_ke):
    teks = argumen.ekspresi
    try:
        pohon = urai(teks)
    except GalatSintaksis as g:
        cetak_galat(tulis_ke, teks, g)
        return 1

    variabel = kumpulkan_variabel(pohon)
    if not variabel:
        tulis_ke.cetak("Ekspresi tidak memuat variabel proposisional.")
        return 1

    judul, baris = tabel(pohon, variabel)

    tulis_ke.cetak(f"Ekspresi : {tulis(pohon)}")
    tulis_ke.cetak(f"Variabel : {', '.join(variabel)}  "
                   f"({len(variabel)} variabel, {len(baris)} baris)")
    tulis_ke.cetak()
    cetak_tabel(tulis_ke, judul, baris)
    tulis_ke.cetak()

    golongan = golongkan(kolom_akhir(baris))
    tulis_ke.cetak(f"Golongan : {golongan} "
                   f"({keterangan_golongan(golongan)})")
    return 0


def perintah_argumen(argumen, tulis_ke):
    try:
        premis = [urai(t) for t in argumen.premis]
        konklusi = urai(argumen.konklusi)
    except GalatSintaksis as g:
        # Teks yang gagal dicari ulang supaya penunjuk letak menempel pada
        # premis atau konklusi yang benar, bukan pada premis pertama.
        semua = list(argumen.premis) + [argumen.konklusi]
        teks_gagal = next((t for t in semua if _gagal(t)), semua[0])
        cetak_galat(tulis_ke, teks_gagal, g)
        return 1

    hasil = periksa_argumen(premis, konklusi)

    for i, p in enumerate(premis, 1):
        tulis_ke.cetak(f"Premis {i} : {tulis(p)}")
    tulis_ke.cetak(f"Konklusi : {tulis(konklusi)}")
    tulis_ke.cetak(f"Rumusan  : {bentuk_implikasi_gabungan(premis, konklusi)}")
    tulis_ke.cetak()

    # Tabel memuat kolom tiap premis dan kolom konklusi, supaya pembaca dapat
    # memeriksa sendiri baris mana yang menentukan.
    variabel = hasil.variabel
    from evaluator import baris_kombinasi, nilai
    judul = list(variabel) + [f"P{i}" for i in range(1, len(premis) + 1)] + ["K"]
    baris = []
    for penetapan in baris_kombinasi(variabel):
        isi = [penetapan[v] for v in variabel]
        isi += [nilai(p, penetapan) for p in premis]
        isi.append(nilai(konklusi, penetapan))
        baris.append(isi)
    cetak_tabel(tulis_ke, judul, baris)
    tulis_ke.cetak()
    tulis_ke.cetak("Keterangan: P1..Pn kolom premis, K kolom konklusi.")
    tulis_ke.cetak()

    if hasil.valid:
        tulis_ke.cetak("Status   : argumen VALID")
        tulis_ke.cetak("Alasan   : tidak ada baris yang membuat seluruh premis "
                       "benar sementara konklusi salah.")
    else:
        nilai_baris = ", ".join(
            f"{v} = {'T' if hasil.baris_penjatuh[v] else 'F'}"
            for v in variabel)
        tulis_ke.cetak("Status   : argumen TIDAK VALID")
        tulis_ke.cetak(f"Alasan   : pada baris {nilai_baris} seluruh premis "
                       "bernilai benar tetapi konklusi bernilai salah.")
    return 0


def _gagal(teks):
    try:
        urai(teks)
        return False
    except GalatSintaksis:
        return True


def bangun_pembaca():
    pembaca = argparse.ArgumentParser(
        prog="simulator.py",
        description="Simulator tabel kebenaran dan verifikator argumen "
                    "logika proposisional.")
    pembaca.add_argument("--ascii", action="store_true",
                         help="cetak lambang logika sebagai padanan ASCII")

    sub = pembaca.add_subparsers(dest="perintah", required=True)

    p_tabel = sub.add_parser(
        "tabel", help="menyusun tabel kebenaran satu ekspresi")
    p_tabel.add_argument("ekspresi",
                         help='contoh: "(p -> q) & ~q"')

    p_arg = sub.add_parser(
        "argumen", help="memeriksa validitas sebuah argumen")
    p_arg.add_argument("--premis", action="append", required=True,
                       metavar="EKSPRESI",
                       help="boleh diulang untuk beberapa premis")
    p_arg.add_argument("--konklusi", required=True, metavar="EKSPRESI")

    return pembaca


def main(argv=None):
    sanggup = _siapkan_keluaran()
    pembaca = bangun_pembaca()
    argumen = pembaca.parse_args(argv)

    tulis_ke = Penulis(sanggup and not argumen.ascii)

    if argumen.perintah == "tabel":
        return perintah_tabel(argumen, tulis_ke)
    return perintah_argumen(argumen, tulis_ke)


if __name__ == "__main__":
    sys.exit(main())
