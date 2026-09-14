# -*- coding: utf-8 -*-
"""Memecah teks ekspresi logika menjadi daftar token.

Modul ini tidak mengetahui apa pun tentang terminal maupun tabel kebenaran.
Tugasnya satu: mengubah teks menjadi urutan token, atau menolak teks itu dengan
keterangan letak kesalahannya.

Pemetaan lambang mengikuti Bagian 4 dokumen milestone. Lambang asli (¬ ∧ ∨ ⊕
→ ↔) diterima, begitu pula padanan yang dapat ditik pada papan tik biasa.
"""

# Jenis token. Dipakai parser sebagai penanda, bukan untuk ditampilkan.
VARIABEL = "VARIABEL"
OPERATOR = "OPERATOR"
BUKA = "BUKA"
TUTUP = "TUTUP"

# Lambang baku tiap operator. Nilai inilah yang dipakai pada keluaran, apa pun
# bentuk yang ditik pengguna.
NEGASI = "¬"
KONJUNGSI = "∧"
DISJUNGSI = "∨"
XOR = "⊕"
IMPLIKASI = "→"
BIIMPLIKASI = "↔"

# Padanan yang terdiri atas tanda baca. Diurutkan dari yang paling panjang,
# sebab "<->" harus dicoba sebelum "<" dan "->" sebelum "-".
PADANAN_TANDA = [
    ("<->", BIIMPLIKASI),
    ("<=>", BIIMPLIKASI),
    ("->", IMPLIKASI),
    ("=>", IMPLIKASI),
    ("/\\", KONJUNGSI),
    ("\\/", DISJUNGSI),
    ("~", NEGASI),
    ("!", NEGASI),
    ("&", KONJUNGSI),
    ("|", DISJUNGSI),
]

# Padanan berupa kata. Kata ini hanya dikenali bila berdiri sendiri, sehingga
# variabel bernama "nor" atau "android" tidak ikut terpecah.
PADANAN_KATA = {
    "not": NEGASI,
    "and": KONJUNGSI,
    "or": DISJUNGSI,
    "xor": XOR,
}

OPERATOR_SAH = {NEGASI, KONJUNGSI, DISJUNGSI, XOR, IMPLIKASI, BIIMPLIKASI}


class GalatSintaksis(Exception):
    """Kesalahan pada teks masukan, lengkap dengan letak kolomnya.

    Atribut posisi dihitung mulai dari nol dan menunjuk ke huruf yang
    menyebabkan penolakan. Modul simulator memakainya untuk menggambar tanda
    penunjuk di bawah teks yang salah.
    """

    def __init__(self, pesan, posisi):
        super().__init__(pesan)
        self.pesan = pesan
        self.posisi = posisi


class Token:
    """Satu satuan terkecil hasil pemecahan teks."""

    def __init__(self, jenis, nilai, posisi):
        self.jenis = jenis
        self.nilai = nilai
        self.posisi = posisi

    def __repr__(self):
        return f"Token({self.jenis}, {self.nilai!r}, {self.posisi})"

    def __eq__(self, lain):
        # Dipakai berkas uji supaya dua token dapat dibandingkan langsung.
        return (isinstance(lain, Token)
                and self.jenis == lain.jenis
                and self.nilai == lain.nilai
                and self.posisi == lain.posisi)


def _awal_nama(c):
    return c.isalpha() or c == "_"


def _lanjutan_nama(c):
    return c.isalnum() or c == "_"


def pecah(teks):
    """Mengubah teks menjadi daftar Token.

    Menimbulkan GalatSintaksis bila menemukan huruf yang tidak dikenali.
    """
    hasil = []
    i = 0
    panjang = len(teks)

    while i < panjang:
        c = teks[i]

        if c.isspace():
            i += 1
            continue

        if c == "(":
            hasil.append(Token(BUKA, "(", i))
            i += 1
            continue

        if c == ")":
            hasil.append(Token(TUTUP, ")", i))
            i += 1
            continue

        # Tanda ^ ditolak dengan sengaja. Pada bahasa C, Java, dan Python tanda
        # itu berarti disjungsi eksklusif, sedangkan pada notasi logika ia lazim
        # dibaca konjungsi. Menerimanya berarti memilih satu tafsir dan
        # menyesatkan pembaca yang terbiasa dengan tafsir yang lain.
        if c == "^":
            raise GalatSintaksis(
                "tanda ^ tidak dipakai; tulis & atau and untuk konjungsi, "
                "atau xor untuk disjungsi eksklusif", i)

        if c in OPERATOR_SAH:
            hasil.append(Token(OPERATOR, c, i))
            i += 1
            continue

        cocok = _cocokkan_tanda(teks, i)
        if cocok is not None:
            lambang, panjang_cocok = cocok
            hasil.append(Token(OPERATOR, lambang, i))
            i += panjang_cocok
            continue

        if _awal_nama(c):
            j = i
            while j < panjang and _lanjutan_nama(teks[j]):
                j += 1
            kata = teks[i:j]
            # Kata operator diperiksa setelah nama diambil utuh, supaya "nor"
            # tidak terbaca sebagai "n" diikuti "or".
            lambang = PADANAN_KATA.get(kata.lower())
            if lambang is not None:
                hasil.append(Token(OPERATOR, lambang, i))
            else:
                hasil.append(Token(VARIABEL, kata, i))
            i = j
            continue

        if c.isdigit():
            raise GalatSintaksis(
                f"angka {c!r} tidak dapat menjadi nama variabel; "
                "nama variabel diawali huruf", i)

        raise GalatSintaksis(f"huruf {c!r} tidak dikenali", i)

    return hasil


def _cocokkan_tanda(teks, i):
    """Mencocokkan padanan bertanda baca pada posisi i.

    Mengembalikan pasangan (lambang, panjang) atau None.
    """
    for bentuk, lambang in PADANAN_TANDA:
        if teks.startswith(bentuk, i):
            return lambang, len(bentuk)
    return None
