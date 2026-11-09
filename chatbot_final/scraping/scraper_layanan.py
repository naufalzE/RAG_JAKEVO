# ============================================================
# scraping/scraper_layanan.py
# Mengambil halaman layanan JAKEVO lalu menyimpannya sebagai teks.
# Belum memasukkan data ke ChromaDB.
#
# Output:
#   dokumen_web/<KODE>.txt     -> teks layanan, bahan chunking
#   arsip_scraping/<KODE>.json -> metadata, teks, tautan lampiran
#
# Contoh:
#   python scraping/scraper_layanan.py              # PM1_PERKAWINAN_PERTAMA
#   python scraping/scraper_layanan.py bawah_umur   # PM1_PERKAWINAN_BAWAH_UMUR
# ============================================================

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

# Pastikan folder chatbotv2 ada di sys.path
FOLDER_CHATBOTV2 = Path(__file__).resolve().parent.parent
if str(FOLDER_CHATBOTV2) not in sys.path:
    sys.path.insert(0, str(FOLDER_CHATBOTV2))

import requests
from bs4 import BeautifulSoup

from core.config import FOLDER_ARSIP_SCRAPING, FOLDER_DOKUMEN_WEB

# Daftar layanan yang sudah dipetakan.
# Kunci = argumen CLI, "kode" = nama dasar file hasil.
LAYANAN = {
    "pertama": {
        "kode": "PM1_PERKAWINAN_PERTAMA",
        "url": (
            "https://jakevo.jakarta.go.id/perizinan/perizinan-nonperizinan/"
            "PM1-LurahCamat-SURAT-PENGANTAR-PERKAWINAN-PERTAMA-%28UMUM%29-"
            "633f84c475d8bc9ad9"
        ),
    },
    "bawah_umur": {
        "kode": "PM1_PERKAWINAN_BAWAH_UMUR",
        "url": (
            "https://jakevo.jakarta.go.id/perizinan/perizinan-nonperizinan/"
            "PM1-LurahCamat-SURAT-PENGANTAR-PERKAWINAN-DI-BAWAH-UMUR-"
            "(DIBAWAH-USIA-19-TAHUN)-633f84ac413d4a37f5"
        ),
    },
    "rumah": {
        "kode": "PM1_KETERANGAN_BELUM_MEMILIKI_RUMAH",
        "url": (
            "https://jakevo.jakarta.go.id/perizinan/perizinan-nonperizinan/"
            "PELAYANAN-ADMINISTRASI-PTSP-KELURAHAN-SURAT-PENGANTAR-KPR-"
            "(KETERANGAN-BELUM-MEMILIKI-RUMAH)-5e72737ba606160da8"
        ),
    },
    "sktm": {
        "kode": "PM1_SURAT_KETERANGAN_TIDAK_MAMPU",
        "url": (
            "https://jakevo.jakarta.go.id/perizinan/perizinan-nonperizinan/"
            "PELAYANAN-ADMINISTRASI-PTSP-KELURAHAN-SURAT-KETERANGAN-TIDAK-MAMPU-5e72715f6f89fde132"
        ),
    },
    "tanah_makam": {
        "kode": "IZIN_PENGGUNAAN_TANAH_MAKAM",
        "url": (
            "https://jakevo.jakarta.go.id/perizinan/perizinan-nonperizinan/"
            "IZIN-PENGGUNAAN-TANAH-MAKAM-(MAKAM-BARUPERPANJANGANTUMPANGAN)-5c05fe31d9b69f64b5"
        ),
    },
    "dispensasi_nikah": {
        "kode": "PM1_SURAT_DISPENSASI_PERKAWINAN",
        "url": (
            "https://jakevo.jakarta.go.id/perizinan/perizinan-nonperizinan/"
            "PM1-LurahCamat-SURAT-DISPENSASI-PERKAWINAN-633f84bb86cfb7444c"
        ),
    },
    "sip_dokter": {
        "kode": "SURAT_IZIN_PRAKTIK_DOKTER",
        "url": (
            "https://jakevo.jakarta.go.id/perizinan/perizinan-nonperizinan/"
            "SURAT-IZIN-PRAKTIK-DOKTER-(DOKTER-UMUM-PERORANGAN)-67aea76626d1984bf5"
        ),
    },
    "pemotongan_ternak": {
        "kode": "IZIN_USAHA_PEMOTONGAN_TERNAK",
        "url": (
            "https://jakevo.jakarta.go.id/perizinan/perizinan-nonperizinan/"
            "IZIN-USAHA-PEMOTONGAN-TERNAK-5c131edf24ab822ddd"
        ),
    },
    "jasa_pemakaman": {
        "kode": "IZIN_USAHA_JASA_PELAYANAN_PEMAKAMAN",
        "url": (
            "https://jakevo.jakarta.go.id/perizinan/perizinan-nonperizinan/"
            "IZIN-USAHA-JASA-PELAYANAN-PEMAKAMAN-5ba89f7e22140c976a"
        ),
    },
    "angkutan_kebersihan": {
        "kode": "IZIN_USAHA_ANGKUTAN_KEBERSIHAN",
        "url": (
            "https://jakevo.jakarta.go.id/perizinan/perizinan-nonperizinan/"
            "IZIN-USAHA-PELAYANAN-ANGKUTAN-DI-BIDANG-KEBERSIHAN-5c08adeeab3fc59e2c"
        ),
    },
}

LAYANAN_BAWAAN = "pertama"


def path_hasil(kode_layanan):
    """Path .txt (dokumen_web) dan .json (arsip_scraping) satu layanan."""
    return (
        Path(FOLDER_DOKUMEN_WEB) / f"{kode_layanan}.txt",
        Path(FOLDER_ARSIP_SCRAPING) / f"{kode_layanan}.json",
    )


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0 Safari/537.36"
    ),
    "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
}


def rapikan_baris(teks: str) -> list[str]:
    """Rapikan hasil ekstraksi menjadi daftar baris nonkosong."""
    hasil = []
    baris_sebelumnya = None

    for baris in teks.splitlines():
        baris = re.sub(r"\s+", " ", baris).strip()
        if not baris:
            continue
        # Buang duplikasi baris yang bersebelahan saja.
        if baris == baris_sebelumnya:
            continue
        hasil.append(baris)
        baris_sebelumnya = baris

    return hasil


def ambil_wadah_konten(soup: BeautifulSoup):
    """Pilih elemen utama jika tersedia; selain itu gunakan body."""
    wadah = soup.find("main")
    if wadah is None:
        wadah = soup.find(id="__next") or soup.find(id="root")
    if wadah is None:
        wadah = soup.body or soup
    return wadah


def ambil_tautan_lampiran(wadah, url_dasar: str) -> list[dict]:
    """Ambil tautan yang tampak seperti template atau file unduhan."""
    hasil = []
    sudah_ada = set()
    pola_teks = re.compile(
        r"template|unduh|download|lampiran|formulir|surat pernyataan|surat kuasa",
        re.IGNORECASE,
    )
    ekstensi_file = re.compile(
        r"\.(pdf|doc|docx|xls|xlsx|odt|rtf)(?:$|[?#])",
        re.IGNORECASE,
    )

    for a in wadah.find_all("a", href=True):
        href = a.get("href", "").strip()
        teks = re.sub(r"\s+", " ", a.get_text(" ", strip=True))
        url_lengkap = urljoin(url_dasar, href)

        if not href or href.startswith(("javascript:", "mailto:", "tel:")):
            continue

        if not (pola_teks.search(teks) or ekstensi_file.search(url_lengkap)):
            continue

        if url_lengkap in sudah_ada:
            continue
        sudah_ada.add(url_lengkap)

        hasil.append({
            "teks_tautan": teks or "(tautan tanpa teks)",
            "url": url_lengkap,
            "kemungkinan_file": bool(ekstensi_file.search(url_lengkap)),
        })

    return hasil


def ambil_satu_layanan(url: str) -> dict:
    """Unduh satu halaman HTML dan ambil teks serta tautan lampirannya."""
    respons = requests.get(url, headers=HEADERS, timeout=40)
    respons.raise_for_status()

    tipe_konten = respons.headers.get("Content-Type", "")
    if "text/html" not in tipe_konten.lower():
        raise ValueError(
            f"URL tidak mengembalikan HTML. Content-Type: {tipe_konten}"
        )

    soup = BeautifulSoup(respons.text, "html.parser")
    wadah = ambil_wadah_konten(soup)

    # Singkirkan elemen yang bukan isi utama halaman.
    for tag in wadah.select("script, style, noscript, svg, nav, footer"):
        tag.decompose()

    judul_tag = soup.find("h1") or soup.find("title")
    judul = (
        re.sub(r"\s+", " ", judul_tag.get_text(" ", strip=True))
        if judul_tag else "Judul tidak ditemukan"
    )

    baris = rapikan_baris(wadah.get_text("\n", strip=True))
    teks_halaman = "\n".join(baris)

    # Deteksi indikasi konten tidak dirender di HTML awal.
    indikator = (
        "persyaratan",
        "alur proses",
        "dasar hukum",
        "biaya retribusi",
    )
    teks_lower = teks_halaman.lower()
    bagian_terdeteksi = [k for k in indikator if k in teks_lower]

    tautan_lampiran = ambil_tautan_lampiran(wadah, url)

    hasil = {
        "source_type": "webpage",
        "source_url": url,
        "final_url": respons.url,
        "nama_dokumen": judul,
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "http_status": respons.status_code,
        "content_type": tipe_konten,
        "bagian_terdeteksi": bagian_terdeteksi,
        "teks_halaman": teks_halaman,
        "tautan_lampiran": tautan_lampiran,
    }

    if not teks_halaman.strip():
        raise ValueError("Teks halaman kosong setelah ekstraksi HTML.")

    return hasil


def siapkan_folder_hasil(*folder) -> list[Path]:
    """Pastikan seluruh folder tujuan ada, lalu kembalikan path absolutnya."""
    hasil = []
    for item in folder:
        path = Path(item)
        path.mkdir(parents=True, exist_ok=True)
        hasil.append(path.resolve())
    return hasil


def proses_satu_layanan(nama_layanan: str):
    if nama_layanan not in LAYANAN:
        print("Layanan tidak dikenal:", nama_layanan)
        print("Pilihan:", ", ".join(LAYANAN))
        return False

    layanan = LAYANAN[nama_layanan]
    url = layanan["url"]
    path_txt, path_json = path_hasil(layanan["kode"])

    print(f"\n[{nama_layanan}] Mengambil layanan: {layanan['kode']}")
    print("URL:", url)

    folder_web, folder_arsip = siapkan_folder_hasil(
        path_txt.parent,
        path_json.parent,
    )

    try:
        data = ambil_satu_layanan(url)
    except requests.RequestException as exc:
        print(f"Gagal mengakses {nama_layanan}:", exc)
        return False
    except Exception as exc:
        print(f"Ekstraksi {nama_layanan} gagal:", exc)
        return False

    path_json.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    bagian_txt = [
        f"JUDUL: {data['nama_dokumen']}",
        f"URL: {data['source_url']}",
        f"Diambil (UTC): {data['fetched_at_utc']}",
        "",
        "=== ISI HALAMAN ===",
        data["teks_halaman"],
        "",
        "=== TAUTAN LAMPIRAN / TEMPLATE ===",
    ]

    if data["tautan_lampiran"]:
        for nomor, item in enumerate(data["tautan_lampiran"], start=1):
            bagian_txt.append(f"{nomor}. {item['teks_tautan']}")
            bagian_txt.append(f"   {item['url']}")
    else:
        bagian_txt.append("Tidak ditemukan tautan yang cocok dengan filter.")

    path_txt.write_text("\n".join(bagian_txt), encoding="utf-8")

    print(f"[OK] Berhasil disimpan: {path_txt.name} ({len(data['teks_halaman'])} karakter, {len(data['tautan_lampiran'])} lampiran)")
    return True


def main():
    target = (
        sys.argv[1].strip().lower()
        if len(sys.argv) > 1
        else LAYANAN_BAWAAN
    )

    if target in ("all", "semua"):
        print(f"Memulai scraping untuk seluruh {len(LAYANAN)} layanan JAKEVO...")
        sukses = 0
        for nama in LAYANAN:
            if proses_satu_layanan(nama):
                sukses += 1
        print(f"\nSelesai! Berhasil mengambil {sukses}/{len(LAYANAN)} layanan.")
        print("Jalankan 'python main.py' untuk memperbarui ChromaDB dengan data baru.")
    else:
        proses_satu_layanan(target)


if __name__ == "__main__":
    main()
