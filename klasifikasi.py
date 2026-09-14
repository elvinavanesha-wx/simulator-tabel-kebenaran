# -*- coding: utf-8 -*-
"""Menggolongkan ekspresi dan memeriksa validitas argumen.

Dua fungsi wajib terakhir pada dokumen milestone dikerjakan di sini. Keduanya
membaca hasil yang sudah dihitung evaluator.py, jadi berkas ini tidak menghitung
ulang nilai apa pun.
"""

from evaluator import baris_kombinasi, nilai
from parser import kumpulkan_variabel, tulis

TAUTOLOGI = "tautologi"
KONTRADIKSI = "kontradiksi"
KONTINGENSI = "kontingensi"


def golongkan(kolom):
    """Menggolongkan ekspresi dari kolom nilai akhirnya.

    Tautologi bila seluruh baris benar, kontradiksi bila seluruh baris salah,
    kontingensi bila kolom memuat sekurang-kurangnya satu benar dan satu salah.
    """
    if not kolom:
        raise ValueError("kolom nilai kosong")
    if all(kolom):
        return TAUTOLOGI
    if not any(kolom):
        return KONTRADIKSI
    return KONTINGENSI


def keterangan_golongan(golongan):
    """Kalimat penjelas untuk tiap golongan, dipakai pada keluaran program."""
    return {
        TAUTOLOGI: "seluruh baris bernilai benar",
        KONTRADIKSI: "seluruh baris bernilai salah",
        KONTINGENSI: "ada baris benar dan ada baris salah",
    }[golongan]


class HasilArgumen:
    """Hasil pemeriksaan sebuah argumen.

    Bila argumen tidak valid, baris_penjatuh memuat penetapan nilai variabel
    yang membuat seluruh premis benar tetapi konklusi salah. Satu baris semacam
    itu sudah cukup untuk menjatuhkan argumen, dan menampilkannya lebih berguna
    bagi pengguna daripada sekadar kata "tidak valid".
    """

    def __init__(self, valid, variabel, baris_penjatuh=None):
        self.valid = valid
        self.variabel = variabel
        self.baris_penjatuh = baris_penjatuh


def periksa_argumen(premis, konklusi):
    """Memeriksa apakah argumen valid.

    Argumen valid apabila tidak ada satu pun baris yang membuat seluruh premis
    benar sementara konklusinya salah. Pemeriksaan berhenti pada baris pertama
    yang menjatuhkan argumen, sebab satu baris sudah menentukan.
    """
    if not premis:
        raise ValueError("argumen memerlukan sekurang-kurangnya satu premis")

    nama = set()
    for p in premis:
        nama.update(kumpulkan_variabel(p))
    nama.update(kumpulkan_variabel(konklusi))
    variabel = sorted(nama)

    for penetapan in baris_kombinasi(variabel):
        semua_premis_benar = all(nilai(p, penetapan) for p in premis)
        if semua_premis_benar and not nilai(konklusi, penetapan):
            return HasilArgumen(False, variabel, dict(penetapan))

    return HasilArgumen(True, variabel)


def bentuk_implikasi_gabungan(premis, konklusi):
    """Menuliskan rumusan setara: (premis₁ ∧ … ∧ premisₙ) → konklusi.

    Rumusan ini disebut pada Bagian 2 dokumen milestone. Program memakainya
    sebagai keterangan pada keluaran, bukan sebagai cara menghitung, sebab
    memeriksa baris per baris lebih mudah dijelaskan kepada pembaca.
    """
    kiri = " ∧ ".join(_bungkus(p) for p in premis)
    return f"({kiri}) → {_bungkus(konklusi)}"


def _bungkus(pohon):
    """Memberi kurung pada ekspresi majemuk supaya gabungannya tidak salah baca."""
    teks = tulis(pohon)
    return teks if pohon.jenis == "var" or teks.startswith("¬") else f"({teks})"
