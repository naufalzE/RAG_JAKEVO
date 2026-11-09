# ============================================================
# chunking/chunk_teks.py
# Proses pembentukan chunk dari teks di luar tabel.
# ============================================================

import re
from pathlib import Path
import pdfplumber

from core.config import MAKS_KARAKTER_CHUNK, kode_dokumen
from core.models import Chunk


# ============================================================
# 1. DATA MANUAL DIAGRAM ALUR IMB HALAMAN 8
# ============================================================

ALUR_IMB_HALAMAN_8 = [
    (
        "Alur Proses IMB | Langkah 1 dari 13 | "
        "Aktor: Pemohon. Tindakan: Mengajukan Izin."
    ),
    (
        "Alur Proses IMB | Langkah 2 dari 13 | "
        "Aktor: Teknis Administrasi. "
        "Tindakan: Verifikasi Berkas dan Mengkonsep Surat Tugas."
    ),
    (
        "Alur Proses IMB | Langkah 3 dari 13 | "
        "Aktor: Kepala Unit. "
        "Tindakan: Verifikasi Berkas dan Menyetujui Surat Tugas."
    ),
    (
        "Alur Proses IMB | Langkah 4 dari 13 | "
        "Aktor: Teknis Lapangan. "
        "Tindakan: Melakukan peninjauan lapangan."
    ),
    (
        "Alur Proses IMB | Langkah 5 dari 13 | "
        "Aktor: Teknis Pemeriksa. "
        "Tindakan: Melakukan pemeriksaan teknis, verifikasi "
        "berkas, dan menyusun draft NPR."
    ),
    (
        "Alur Proses IMB | Langkah 6 dari 13 | "
        "Aktor: Kepala Unit. "
        "Tindakan: Menyetujui draft NPR dan mengirimkan "
        "ke pemohon."
    ),
    (
        "Alur Proses IMB | Langkah 7 dari 13 | "
        "Aktor: Pemohon. Tindakan: Menyetujui NPR."
    ),
    (
        "Alur Proses IMB | Langkah 8 dari 13 | "
        "Aktor: Teknis Pemeriksa. "
        "Tindakan: Mencetak SKRD & SSRD dan mengirimkan "
        "ke pemohon."
    ),
    (
        "Alur Proses IMB | Langkah 9 dari 13 | "
        "Aktor: Pemohon. "
        "Tindakan: Mengunggah bukti bayar SKRD & SSRD."
    ),
    (
        "Alur Proses IMB | Langkah 10 dari 13 | "
        "Aktor: Teknis Pemeriksa. "
        "Tindakan: Mengkonfirmasi pembayaran retribusi "
        "dan mengirim konsep SK Izin."
    ),
    (
        "Alur Proses IMB | Langkah 11 dari 13 | "
        "Aktor: Kepala Unit. "
        "Tindakan: Menyetujui SK Izin dan GPA yang fix."
    ),
    (
        "Alur Proses IMB | Langkah 12 dari 13 | "
        "Aktor: Kepala TU. "
        "Tindakan: Mengunggah papan proyek sementara "
        "dan mengirimkan output IMB."
    ),
    (
        "Alur Proses IMB | Langkah 13 dari 13 | "
        "Aktor: Pemohon. Tindakan: Mendapatkan output IMB."
    ),
]


def buat_rangkaian_alur(daftar_langkah):
    """
    Membentuk satu chunk yang berisi seluruh urutan Alur IMB.
    """
    daftar_bagian = []
    pola_awalan = r"^Alur Proses IMB \| Langkah \d+ dari 13 \| "

    for nomor, teks_langkah in enumerate(daftar_langkah, start=1):
        isi_langkah = re.sub(pola_awalan, "", teks_langkah).strip()
        daftar_bagian.append(f"{nomor}. {isi_langkah}")

    rangkaian = (
        "Rangkaian lengkap Alur Proses IMB "
        "(Izin Mendirikan Bangunan): "
        + " ".join(daftar_bagian)
    )

    rangkaian = rangkaian.replace("mengirimkanke pemohon", "mengirimkan ke pemohon")
    rangkaian = re.sub(r"\s+", " ", rangkaian).strip()
    return rangkaian


RANGKAIAN_ALUR_IMB_HALAMAN_8 = buat_rangkaian_alur(ALUR_IMB_HALAMAN_8)

CATATAN_ALUR_IMB_HALAMAN_8 = (
    "Catatan Alur Proses IMB: Kemungkinan akan ada komunikasi "
    "dengan pemohon (Butuh Perbaikan / Butuh Perbaikan Berkas) "
    "pada bagian ini."
)


def teks_di_luar_tabel(path, nomor):
    """Mengambil teks di luar area tabel pada halaman PDF tertentu."""
    with pdfplumber.open(path) as pdf:
        halaman = pdf.pages[nomor - 1]
        tables = halaman.find_tables()
        page_tanpa_tabel = halaman

        for table in tables:
            page_tanpa_tabel = page_tanpa_tabel.outside_bbox(table.bbox)

        teks = page_tanpa_tabel.extract_text() or ""

    teks = re.sub(r"Halaman\s+\d+\s+dari\s+\d+", "", teks)
    return teks.strip()


def bersihkan_teks(teks):
    """Menghapus deretan titik panjang dan merapikan spasi."""
    teks = re.sub(r"\.{3,}", " ", teks)
    teks = re.sub(r"\s+", " ", teks)
    return teks.strip()


def halaman_tidak_relevan(teks):
    """True jika halaman diawali judul yang ingin dilewati."""
    teks_awal = teks.strip().lower()
    judul_yang_dilewati = ("daftar isi", "daftar gambar")
    return any(teks_awal.startswith(judul) for judul in judul_yang_dilewati)


def pisah_kalimat(teks):
    """Memisahkan teks berdasarkan whitespace setelah . ! atau ?."""
    teks = re.sub(r"\n+", " ", teks).strip()
    if not teks:
        return []
    return re.split(r"(?<=[.!?])\s+", teks)


def gabung_kalimat(kalimat, maks_karakter=500):
    """Menggabungkan kalimat selama batas karakter terpenuhi."""
    if maks_karakter < 1:
        raise ValueError("maks_karakter harus minimal 1")

    simpan = []
    sementara = ""

    for k in kalimat:
        k = k.strip()
        if not k:
            continue

        if len(k) > maks_karakter:
            if sementara:
                simpan.append(sementara)
                sementara = ""

            for kata in k.split():
                if len(kata) > maks_karakter:
                    if sementara:
                        simpan.append(sementara)
                        sementara = ""

                    for awal in range(0, len(kata), maks_karakter):
                        simpan.append(kata[awal:awal + maks_karakter])

                elif not sementara:
                    sementara = kata

                elif len(sementara) + 1 + len(kata) <= maks_karakter:
                    sementara += " " + kata

                else:
                    simpan.append(sementara)
                    sementara = kata

            continue

        if not sementara:
            sementara = k
        elif len(sementara) + 1 + len(k) <= maks_karakter:
            sementara += " " + k
        else:
            simpan.append(sementara)
            sementara = k

    if sementara:
        simpan.append(sementara)

    return simpan


def halaman_adalah_diagram_alur_imb(path, nomor):
    """
    Memastikan override manual hanya diterapkan pada halaman 8
    yang benar-benar memuat diagram Alur Proses IMB.
    """
    if nomor != 8:
        return False

    with pdfplumber.open(path) as pdf:
        if len(pdf.pages) < nomor:
            return False
        teks = pdf.pages[nomor - 1].extract_text() or ""

    teks_normal = re.sub(r"\s+", " ", teks.lower()).strip()
    penanda = (
        "gambar 2 alur proses imb",
        "gpa yang fix",
        "mendapatkan output imb",
    )
    return all(item in teks_normal for item in penanda)


def chunk_teks_dokumen(
    path,
    kode="",
    nama_file="",
    maks_karakter=MAKS_KARAKTER_CHUNK,
):
    """Membentuk chunk teks dari seluruh halaman PDF."""
    kode = kode or kode_dokumen(path)
    nama_file = nama_file or Path(path).name

    hasil = []
    with pdfplumber.open(path) as pdf:
        jumlah_halaman = len(pdf.pages)

    print("\n=== DIAGNOSTIK PEMBENTUKAN CHUNK TEKS ===")
    print("Dokumen:", nama_file, "| Kode:", kode)

    for nomor in range(1, jumlah_halaman + 1):
        if halaman_adalah_diagram_alur_imb(path, nomor):
            daftar_chunk = (
                ALUR_IMB_HALAMAN_8
                + [
                    buat_rangkaian_alur(ALUR_IMB_HALAMAN_8),
                    CATATAN_ALUR_IMB_HALAMAN_8,
                ]
            )
            print(
                f"Halaman {nomor:02d} | "
                f"OVERRIDE ALUR IMB TERVERIFIKASI: "
                f"{len(daftar_chunk)} chunk terstruktur"
            )
        else:
            teks = teks_di_luar_tabel(path, nomor)
            teks = bersihkan_teks(teks)

            if halaman_tidak_relevan(teks):
                print(f"Halaman {nomor:02d} | DILEWATI: halaman tidak relevan")
                continue

            if not teks:
                print(f"Halaman {nomor:02d} | DILEWATI: teks kosong")
                continue

            kalimat = pisah_kalimat(teks)
            daftar_chunk = gabung_kalimat(
                kalimat,
                maks_karakter=maks_karakter,
            )

        for indeks, teks_chunk in enumerate(daftar_chunk, start=1):
            if not teks_chunk.strip():
                continue

            chunk_id = f"{kode}-TXT-P{nomor:03d}-C{indeks:03d}"
            hasil.append(
                Chunk(
                    chunk_id=chunk_id,
                    teks=teks_chunk,
                    page=nomor,
                    jenis="teks",
                    dokumen=kode,
                    nama_file=nama_file,
                )
            )

    print("\n=== TOTAL HASIL CHUNK TEKS ===")
    print("Total chunk teks:", len(hasil))
    return hasil
