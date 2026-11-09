# ============================================================
# buat_data_web.py
# Membuat ulang berkas uji regresi di uji/data_web/.
#
# Sumber: dokumen_web/*.txt (hasil scraping asli).
#
# Hasil:
#   asli_bawah_umur.txt  salinan apa adanya
#   asli_pertama.txt     salinan apa adanya
#   asli_rumah.txt       salinan apa adanya
#   c1_tanpa_alur.txt    baris penanda "Alur Proses" dihapus
#   c2_angka_nyasar.txt  angka "2" disisipkan di tengah butir 9
#   c3_tanpa_tautan.txt  isi bagian tautan diganti satu baris
#
# PENGAMAN: berkas sumber divalidasi dulu dengan baca_web.
# Bila ada yang gagal divalidasi (mis. hasil scraping rusak),
# skrip berhenti dan cadangan lama TIDAK ditimpa.
#
# Jalankan dari folder chatbotv2:
#     python uji/buat_data_web.py
# ============================================================

import shutil
import sys
from pathlib import Path

import _bootstrap  # noqa: F401  (menambah chatbotv2 ke sys.path)

from baca_web import BerkasWebTidakValid, baca_halaman_web

FOLDER_UJI = Path(__file__).resolve().parent
FOLDER_PROYEK = FOLDER_UJI.parent
FOLDER_SUMBER = FOLDER_PROYEK / "dokumen_web"
FOLDER_DATA = FOLDER_UJI / "data_web"

SUMBER_BAWAH_UMUR = FOLDER_SUMBER / "PM1_PERKAWINAN_BAWAH_UMUR.txt"
SUMBER_PERTAMA = FOLDER_SUMBER / "PM1_PERKAWINAN_PERTAMA.txt"
SUMBER_RUMAH = FOLDER_SUMBER / "PM1_KETERANGAN_BELUM_MEMILIKI_RUMAH.txt"

# Pasangan nama berkas sumber -> nama cadangan di data_web.
CADANGAN = (
    (SUMBER_BAWAH_UMUR, "asli_bawah_umur.txt"),
    (SUMBER_PERTAMA, "asli_pertama.txt"),
    (SUMBER_RUMAH, "asli_rumah.txt"),
)

PENANDA_ALUR = "Alur Proses"
PENANDA_TAUTAN = "=== TAUTAN LAMPIRAN / TEMPLATE ==="
PESAN_TANPA_TAUTAN = "Tidak ditemukan tautan yang cocok dengan filter."

AWAL_BUTIR_9 = "Scan asli KTP dan KK orang tua pemohon"
TENGAH_BUTIR_9 = "Surat Keterangan Kematian"


def baca_baris(path):
    """Membaca berkas sebagai daftar baris tanpa baris baru."""

    return path.read_text(encoding="utf-8").splitlines()


def tulis(path, baris):
    """Menulis daftar baris menjadi berkas teks."""

    path.write_text("\n".join(baris), encoding="utf-8")


def buat_c1(baris):
    """C1: hapus baris penanda "Alur Proses" saja."""

    hasil = list(baris)
    hasil.remove(PENANDA_ALUR)

    return hasil


def buat_c2(baris):
    """
    C2: pecah butir 9 dan sisipkan baris "2" di tengahnya.

    Ini meniru angka biasa (bukan nomor butir) yang terbaca
    sebagai baris tersendiri.
    """

    hasil = []

    for teks in baris:
        if teks.startswith(AWAL_BUTIR_9) and TENGAH_BUTIR_9 in teks:
            kepala, ekor = teks.split(TENGAH_BUTIR_9, 1)
            hasil.append(kepala.rstrip())
            hasil.append("2")
            hasil.append(TENGAH_BUTIR_9 + ekor)
            continue

        hasil.append(teks)

    return hasil


def buat_c3(baris):
    """C3: pertahankan penanda tautan, ganti isinya satu baris."""

    posisi = baris.index(PENANDA_TAUTAN)

    return baris[:posisi + 1] + [PESAN_TANPA_TAUTAN]


def pastikan_sumber_valid():
    """
    Memastikan semua berkas sumber lolos validasi baca_web.

    Tanpa pemeriksaan ini, hasil scraping yang rusak akan
    menimpa cadangan yang masih baik, sehingga kasus uji asli
    ikut hilang.
    """

    rusak = []

    for path, nama in CADANGAN:
        if not path.is_file():
            sys.exit(f"Berkas sumber tidak ditemukan: {path}")

        try:
            baca_halaman_web(path)
        except BerkasWebTidakValid as galat:
            rusak.append(f"  {nama} <- {galat}")

    if rusak:
        sys.exit(
            "Berkas sumber gagal divalidasi; cadangan tidak "
            "ditimpa:\n" + "\n".join(rusak)
        )


def main():
    pastikan_sumber_valid()

    FOLDER_DATA.mkdir(parents=True, exist_ok=True)

    for path, nama in CADANGAN:
        shutil.copyfile(path, FOLDER_DATA / nama)

    bawah = baca_baris(SUMBER_BAWAH_UMUR)

    tulis(FOLDER_DATA / "c1_tanpa_alur.txt", buat_c1(bawah))
    tulis(FOLDER_DATA / "c2_angka_nyasar.txt", buat_c2(bawah))
    tulis(FOLDER_DATA / "c3_tanpa_tautan.txt", buat_c3(bawah))

    print("Berkas uji di:", FOLDER_DATA)

    for path in sorted(FOLDER_DATA.glob("*.txt")):
        print(f"  {path.name:24} {path.stat().st_size:6} byte")


if __name__ == "__main__":
    main()
