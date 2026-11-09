# ============================================================
# chunking/chunk_web.py
# Khusus bertanggung jawab memproses teks hasil scraping web.
# ============================================================

from pathlib import Path

from scraping.baca_web import baca_halaman_web
from core.config import kode_dokumen
from core.models import Chunk


def teks_info(data):
    judul = data["judul"]
    info = data["info"]

    teks_detail = ", ".join(
        f"{kunci}: {nilai}"
        for kunci, nilai in info.items()
    )

    teks = f"{judul}, {teks_detail}"
    return teks


def teks_syarat(data):
    judul = data["judul"]
    syarat = data["syarat"]

    daftar_butir = []

    for butir in syarat:
        teks_butir = f"{butir['no']}. {butir['teks']}"

        if butir["template"]:
            teks_butir += " (template unduh)"

        daftar_butir.append(teks_butir)

    if not daftar_butir:
        return f"{judul}, Persyaratan: -"

    teks = f"{judul}, Persyaratan: " + "; ".join(daftar_butir)
    return teks


def teks_alur(data):
    judul = data["judul"]
    alur = data["alur"]

    daftar_langkah = []

    for langkah in alur:
        bagian = [f"{langkah['no']}. {langkah['tahap']}"]

        if langkah["pelaksana"]:
            bagian.append(f"Pelaksana: {langkah['pelaksana']}")

        if langkah["uraian"]:
            bagian.append(langkah["uraian"])

        daftar_langkah.append(" | ".join(bagian))

    if not daftar_langkah:
        return f"{judul}, Alur Proses: -"

    teks = f"{judul}, Alur Proses: " + "; ".join(daftar_langkah)
    return teks


def teks_hukum(data):
    judul = data["judul"]
    hukum = data["hukum"]

    daftar_hukum = []

    for peraturan in hukum:
        bagian = []

        if peraturan["jenis"]:
            bagian.append(peraturan["jenis"])
        if peraturan["status"]:
            bagian.append(peraturan["status"])
        if peraturan["berlaku"]:
            bagian.append(f"Berlaku {peraturan['berlaku']}")
        if peraturan["nama"]:
            bagian.append(peraturan["nama"])

        daftar_hukum.append(" | ".join(bagian))

    if not daftar_hukum:
        return f"{judul}, Dasar Hukum: -"

    teks = f"{judul}, Dasar Hukum: " + "; ".join(daftar_hukum)
    return teks


BAGIAN_WEB = (
    ("INFO", teks_info),
    ("SYARAT", teks_syarat),
    ("ALUR", teks_alur),
    ("HUKUM", teks_hukum),
)


def susun_chunk_web(path):
    """
    Membaca satu berkas .txt layanan lalu menyusun objek Chunk.
    Hasilnya satu chunk untuk tiap bagian (INFO, SYARAT, ALUR, HUKUM).
    """
    data = baca_halaman_web(path)

    kode = kode_dokumen(path)
    nama_file = Path(path).name
    judul = data.get("judul") or ""
    url = data.get("url") or ""
    pasangan = data.get("pasangan") or []
    hasil = []

    for bagian, fungsi_teks in BAGIAN_WEB:
        teks = fungsi_teks(data)

        if not teks.strip():
            continue

        hasil.append(
            Chunk(
                chunk_id=f"{kode}-WEB-{bagian}",
                teks=teks,
                page=0,
                jenis="web",
                dokumen=kode,
                nama_file=nama_file,
                url=url,
                judul=judul,
                pasangan=list(pasangan) if bagian == "SYARAT" else [],
            )
        )

    return hasil
