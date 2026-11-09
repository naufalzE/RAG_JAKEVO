# ============================================================
# chunking/chunk_tabel.py
# Proses pembentukan chunk dari tabel PDF.
# ============================================================

from pathlib import Path
import pdfplumber

from core.config import kode_dokumen
from core.models import Chunk


def bersihkan_sel(nilai):
    """Membersihkan isi satu sel tabel menjadi teks satu baris."""
    teks = str(nilai or "")
    teks = teks.replace("\n", " ")
    teks = " ".join(teks.split())
    return teks


def normalisasi_header(nama):
    """Menormalkan nama kolom agar mudah dicocokkan."""
    nama = bersihkan_sel(nama).upper()
    return "".join(
        karakter for karakter in nama if karakter.isalnum()
    )


def lihat_tabel(path_dokumen, nomor):
    """Mengambil semua tabel dari halaman PDF tertentu."""
    with pdfplumber.open(path_dokumen) as pdf:
        if nomor < 1 or nomor > len(pdf.pages):
            raise ValueError(
                f"Nomor halaman {nomor} tidak valid. "
                f"PDF memiliki {len(pdf.pages)} halaman."
            )
        hasil = pdf.pages[nomor - 1].extract_tables()

    print(f"Halaman {nomor}: {len(hasil)} tabel terdeteksi")
    return hasil


def baris_ke_teks(header, baris, abaikan_header=None):
    """Mengubah satu baris tabel menjadi teks."""
    hasil = []
    jumlah_kolom = max(len(header), len(baris))
    abaikan = {"NO", "NOMOR"}

    if abaikan_header:
        abaikan.update(
            normalisasi_header(nama)
            for nama in abaikan_header
        )

    for indeks in range(jumlah_kolom):
        if indeks < len(header):
            nama_kolom = bersihkan_sel(header[indeks])
        else:
            nama_kolom = ""

        if normalisasi_header(nama_kolom) in abaikan:
            continue

        if indeks < len(baris):
            isi_sel = bersihkan_sel(baris[indeks])
        else:
            isi_sel = ""

        if not nama_kolom:
            nama_kolom = f"Kolom {indeks + 1}"

        hasil.append(f"{nama_kolom}: {isi_sel}")

    return " | ".join(hasil)


def judul_baris(header, baris):
    """Mengambil nilai dari kolom LABEL STATUS."""
    for indeks, nama_kolom in enumerate(header):
        if normalisasi_header(nama_kolom) == "LABELSTATUS":
            if indeks < len(baris):
                return bersihkan_sel(baris[indeks])
            return ""
    return ""


def halaman_bertabel(path):
    """Mencari halaman yang memiliki tabel dengan minimal tiga baris."""
    hasil = []
    with pdfplumber.open(path) as pdf:
        for nomor, halaman in enumerate(pdf.pages, start=1):
            daftar_tabel = halaman.extract_tables()
            jumlah = sum(
                1
                for tabel in daftar_tabel
                if tabel and len(tabel) >= 3
            )
            if jumlah > 0:
                hasil.append((nomor, jumlah))
    return hasil


def ambil_nomor(daftar_halaman):
    """Mengambil nomor halaman dari hasil halaman_bertabel()."""
    return [nomor for nomor, _ in daftar_halaman]


def kumpulkan_chunk_tabel(
    path_dokumen,
    daftar_nomor,
    kode="",
    nama_file="",
):
    """Membentuk satu chunk untuk setiap baris data tabel."""
    kode = kode or kode_dokumen(path_dokumen)
    if not nama_file:
        nama_file = Path(path_dokumen).name

    chunks = []

    for nomor in daftar_nomor:
        daftar_tabel = lihat_tabel(path_dokumen, nomor)

        for indeks_tabel, tabel in enumerate(daftar_tabel, start=1):
            if not tabel or not tabel[0]:
                continue

            header = tabel[0]
            if not any(bersihkan_sel(sel) for sel in header):
                continue

            for indeks_baris, baris in enumerate(tabel[1:], start=1):
                if not any(bersihkan_sel(sel) for sel in baris):
                    continue

                judul = judul_baris(header, baris)

                if judul:
                    teks_asli = baris_ke_teks(
                        header,
                        baris,
                        abaikan_header={"LABEL STATUS"},
                    )
                    if teks_asli:
                        teks_chunk = f"{judul} | {teks_asli}"
                    else:
                        teks_chunk = judul
                else:
                    teks_chunk = baris_ke_teks(header, baris)

                if not teks_chunk.strip():
                    continue

                chunk_id = (
                    f"{kode}-TBL-P{nomor:03d}"
                    f"-T{indeks_tabel:03d}"
                    f"-R{indeks_baris:03d}"
                )

                chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        teks=teks_chunk,
                        page=nomor,
                        jenis="tabel",
                        dokumen=kode,
                        nama_file=nama_file,
                    )
                )

    return chunks
