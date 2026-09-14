# -*- coding: utf-8 -*-
"""Menghitung nilai pohon sintaksis untuk setiap baris tabel kebenaran.

Modul ini menyiapkan dua hal: daftar kombinasi nilai kebenaran untuk n variabel,
dan nilai tiap subekspresi pada setiap kombinasi itu. Kolom subekspresi disebut
kolom bantu pada dokumen milestone; gunanya supaya pengguna dapat menelusuri
asal nilai pada kolom terakhir.
"""

from itertools import product

from parser import tulis
from tokenizer import (NEGASI, KONJUNGSI, DISJUNGSI, XOR, IMPLIKASI,
                       BIIMPLIKASI)


def baris_kombinasi(variabel):
    """Menyusun 2ⁿ kombinasi nilai kebenaran untuk daftar variabel.

    Urutannya dimulai dari seluruh benar, sesuai kebiasaan penulisan tabel
    kebenaran pada buku teks: TT, TF, FT, FF untuk dua variabel.
    """
    return [dict(zip(variabel, nilai))
            for nilai in product([True, False], repeat=len(variabel))]


def nilai(pohon, penetapan):
    """Menghitung nilai satu pohon pada satu penetapan nilai variabel."""
    j = pohon.jenis

    if j == "var":
        return penetapan[pohon.nama]

    if j == NEGASI:
        return not nilai(pohon.kiri, penetapan)

    kiri = nilai(pohon.kiri, penetapan)
    kanan = nilai(pohon.kanan, penetapan)

    if j == KONJUNGSI:
        return kiri and kanan
    if j == DISJUNGSI:
        return kiri or kanan
    if j == XOR:
        return kiri != kanan
    if j == IMPLIKASI:
        # Implikasi hanya salah bila premisnya benar dan konklusinya salah.
        return (not kiri) or kanan
    if j == BIIMPLIKASI:
        return kiri == kanan

    raise ValueError(f"operator tidak dikenali: {j}")


def subekspresi(pohon):
    """Mendaftar subekspresi majemuk, dari yang terkecil ke yang terbesar.

    Variabel tunggal tidak ikut, sebab sudah punya kolomnya sendiri. Pohon utuh
    ikut, sebagai kolom terakhir. Daftar ini yang menjadi kolom bantu.
    """
    urutan = []
    terlihat = set()

    def telusuri(s):
        if s is None or s.jenis == "var":
            return
        telusuri(s.kiri)
        telusuri(s.kanan)
        kunci = tulis(s)
        # Subekspresi yang sama, misalnya ¬q pada (p → ¬q) ∧ ¬q, cukup satu
        # kolom. Perbandingannya memakai bentuk tulisannya, bukan alamat
        # simpulnya, sebab dua simpul berbeda dapat berisi hal yang sama.
        if kunci not in terlihat:
            terlihat.add(kunci)
            urutan.append(s)

    telusuri(pohon)
    return urutan


def tabel(pohon, variabel):
    """Menyusun tabel kebenaran lengkap.

    Mengembalikan pasangan (judul, baris). Judul berisi nama variabel diikuti
    tulisan tiap kolom bantu. Setiap baris berisi nilai benar-salah dengan
    urutan yang sama seperti judulnya.
    """
    kolom = subekspresi(pohon)
    judul = list(variabel) + [tulis(s) for s in kolom]

    baris = []
    for penetapan in baris_kombinasi(variabel):
        isi = [penetapan[v] for v in variabel]
        isi += [nilai(s, penetapan) for s in kolom]
        baris.append(isi)

    return judul, baris


def kolom_akhir(baris):
    """Mengambil kolom paling kanan, yaitu nilai ekspresi utuh per baris."""
    return [b[-1] for b in baris]
