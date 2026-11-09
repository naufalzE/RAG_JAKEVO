# ============================================================
# chunking/chunk_pdf.py
# Khusus bertanggung jawab memproses dokumen PDF.
# ============================================================

from pathlib import Path
import pdfplumber

from chunking.chunk_tabel import (
    ambil_nomor,
    halaman_bertabel,
    kumpulkan_chunk_tabel,
)
from chunking.chunk_teks import chunk_teks_dokumen
from core.config import kode_dokumen


def muat_dokumen(path_dokumen):
    """
    Membaca teks setiap halaman PDF dan melewati halaman kosong.

    OUTPUT:
        List tuple (nomor_halaman, teks).
    """
    semua_halaman = []

    with pdfplumber.open(path_dokumen) as pdf:
        for nomor, halaman in enumerate(pdf.pages, start=1):
            teks = halaman.extract_text()

            if not teks or not teks.strip():
                continue

            semua_halaman.append((nomor, teks))

    return semua_halaman


def semua_chunk(path):
    """
    1. Mencari halaman yang memiliki tabel.
    2. Membentuk chunk tabel.
    3. Membentuk chunk teks.
    4. Menggabungkan dan mengurutkan berdasarkan halaman
       (tabel diletakkan sebelum teks jika halamannya sama).

    OUTPUT:
        List objek Chunk yang sudah diurutkan.
    """
    kode = kode_dokumen(path)
    nama_file = Path(path).name

    daftar_halaman_tabel = halaman_bertabel(path)
    nomor_halaman_tabel = ambil_nomor(daftar_halaman_tabel)

    chunks_tabel = kumpulkan_chunk_tabel(
        path,
        nomor_halaman_tabel,
        kode=kode,
        nama_file=nama_file,
    )

    chunks_teks = chunk_teks_dokumen(
        path,
        kode=kode,
        nama_file=nama_file,
    )

    hasil = chunks_tabel + chunks_teks

    hasil.sort(
        key=lambda chunk: (
            chunk.page,
            0 if chunk.jenis == "tabel" else 1
        )
    )

    return hasil
