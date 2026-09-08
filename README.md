# simulator-tabel-kebenaran

Simulator tabel kebenaran dan verifikator argumen, PJBL-1 Matematika Diskrit,
Kelompok 5 ex-1mphn3n.

Program membaca ekspresi logika proposisional, menyusun tabel kebenarannya,
menggolongkan ekspresi tersebut, dan memeriksa apakah sebuah argumen valid.
Proyek dikerjakan sampai Pertemuan 4 pada Program Studi Ilmu Komputer,
Universitas Bina Bangsa Getsempena.

## Program yang dibutuhkan

Python 3.11 atau versi yang lebih baru. Tidak ada pustaka pihak ketiga yang perlu
dipasang: program hanya memakai pustaka standar Python, sehingga tidak
memerlukan sambungan internet dan tidak memerlukan lingkungan virtual.

### Menyusun tabel kebenaran

    python simulator.py tabel "(p -> q) & ~q"

Output:

    Ekspresi : (p → q) ∧ ¬q
    Variabel : p, q  (2 variabel, 4 baris)

    +---+---+-------+----+--------------+
    | p | q | p → q | ¬q | (p → q) ∧ ¬q |
    +---+---+-------+----+--------------+
    | T | T |   T   | F  |      F       |
    | T | F |   F   | T  |      F       |
    | F | T |   T   | F  |      F       |
    | F | F |   T   | T  |      T       |
    +---+---+-------+----+--------------+

    Golongan : kontingensi (ada baris benar dan ada baris salah)

Selain kolom variabel dan kolom hasil akhir, program menampilkan kolom bantu
untuk tiap subekspresi, agar asal nilai pada kolom terakhir dapat ditelusuri.

### Memeriksa validitas argumen

    python simulator.py argumen --premis "p -> q" --premis "~q" --konklusi "~p"

Pilihan `--premis` boleh diulang sebanyak premis yang ada. Program mencetak
tabel dengan kolom P1 sampai Pn untuk premis dan kolom K untuk konklusi, lalu
menyatakan argumen valid atau tidak.

Apabila argumen tidak valid, program menyebut baris yang menjatuhkannya:

    Status   : argumen TIDAK VALID
    Alasan   : pada baris p = F, q = T seluruh premis bernilai benar tetapi
               konklusi bernilai salah.

### Bila lambang logika tidak muncul

Terminal Windows bawaan memakai penyandian yang tidak memuat lambang ∧, ∨, dan
⊕. Program berusaha menyalakan UTF-8 sendiri, tetapi bila lambangnya tetap
kacau, tambahkan `--ascii`:

    python simulator.py --ascii tabel "p xor q"

## Cara menulis ekspresi

Lambang logika dapat ditulis memakai padanan yang tersedia pada papan tik.
Keluaran program tetap memakai lambang aslinya.

| Operator | Lambang | Dapat ditik sebagai |
| --- | --- | --- |
| Negasi | ¬ | `~` atau `!` atau `not` |
| Konjungsi | ∧ | `&` atau `/\` atau `and` |
| Disjungsi | ∨ | `\|` atau `\/` atau `or` |
| Disjungsi eksklusif | ⊕ | `xor` |
| Implikasi | → | `->` atau `=>` |
| Biimplikasi | ↔ | `<->` atau `<=>` |

Nama variabel diawali huruf dan boleh lebih dari satu huruf, misalnya `hujan`
dan `basah`.

Tanda `^` sengaja ditolak. Pada bahasa C, Java, dan Python tanda itu berarti
disjungsi eksklusif, sedangkan pada notasi logika ia lazim dibaca konjungsi.
Menerimanya berarti memilih satu tafsir dan menyesatkan pembaca yang terbiasa
dengan tafsir yang lain.

### Keutamaan operator

Dari yang paling kuat ke yang paling lemah:

| Keutamaan | Operator | Contoh penafsiran |
| --- | --- | --- |
| 1 (kuat) | ¬ | `~p & q` menjadi `(~p) & q` |
| 2 | ∧ | `p \| q & r` menjadi `p \| (q & r)` |
| 3 | ∨ | `p xor q \| r` menjadi `p xor (q \| r)` |
| 4 | ⊕ | `p -> q xor r` menjadi `p -> (q xor r)` |
| 5 | → | `p & q -> r` menjadi `(p & q) -> r` |
| 6 (lemah) | ↔ | `p -> q <-> r` menjadi `(p -> q) <-> r` |

Tanda kurung selalu mengalahkan tabel di atas. Implikasi bersifat asosiatif
kanan, sehingga `p -> q -> r` dibaca `p -> (q -> r)`.

Pada ekspresi yang mencampur ∨ dan ⊕, tulislah tanda kurung secara tegas supaya
maksudnya tidak bergantung pada tabel keutamaan.

## Menjalankan kasus uji

    python uji/jalankan_uji.py

Perintah ini membandingkan keluaran program dengan tabel acuan pada
`uji/kasus.txt`, yaitu 38 kasus yang dihitung dengan tangan tanpa menjalankan
program. Bila ada selisih, nilai acuan dan nilai program ditampilkan
berdampingan.

Selisih berarti salah satu di antara keduanya keliru, dan wajib ditelusuri
sebelum pekerjaan dilanjutkan. Pemeriksaan ini pernah menemukan kekeliruan pada
tabel acuan, bukan pada program, yaitu pada baris keenam ekspresi
`(p -> q) & (q -> r)`. Pada baris itu p → q bernilai benar karena premisnya
salah, tetapi q → r bernilai salah, sehingga konjungsinya salah.

## Susunan berkas

    simulator.py      membaca perintah, memanggil modul lain, mencetak hasil
    tokenizer.py      memecah teks menjadi token
    parser.py         menyusun token menjadi pohon sintaksis
    evaluator.py      menghitung nilai pohon untuk setiap baris
    klasifikasi.py    menggolongkan ekspresi dan memeriksa validitas argumen
    uji/              kasus uji beserta tabel acuan hitungan tangan
    dokumen/          dokumen milestone dan laporan akhir

Pembagian ini memisahkan dua tanggung jawab: `simulator.py` hanya mengurus
tampilan (membaca perintah, mencetak hasil), sedangkan keempat modul lainnya
hanya mengurus logika. Antarmuka baris perintah hanyalah satu pemanggil; modul
`tokenizer.py` sampai `klasifikasi.py` tetap dapat dipakai antarmuka lain tanpa
ditulis ulang. Yang berubah ketika antarmuka ditambah hanyalah cara hasil
disajikan, bukan cara hasil dihitung.

## Pembagian peran

| Peran | Nama |
| --- | --- |
| Ketua Kelompok | Reva Sahira |
| Koordinator Teknis | Fachrul Razi Al Bahri |
| Koordinator Pengujian | M. Farhan |
| Koordinator Dokumentasi | Embun Ikhwana |
| Koordinator Presentasi | Najwa Salmi |
| Anggota Tim Teknis | Ulfi Ufrijal |

## Git/code notice

Aturan yang berlaku: kode yang belum berjalan tidak digabungkan ke cabang utama,
dan setiap berkas serahan dibaca sekurang-kurangnya satu anggota lain sebelum
diunggah.
