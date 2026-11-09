# ============================================================
# evaluasi_batch.py
# Evaluasi batch retrieval + jawaban LLM untuk soal JAKEVO.
#
# INPUT:
#   Utama: workbook Excel (.xlsx) dengan kolom Pertanyaan dan Jawaban,
#   atau Soal_Jawaban_JAKEVO.csv bila tersedia.
#   Letakkan file soal di folder yang sama dengan script ini.
#
# OUTPUT:
#   hasil_evaluasi_batch.csv
#
# PENTING:
#   Script ini tidak memanggil fungsi jawab() agar eksperimen
#   penambahan chunk IDM manual di tanya_jawab.py tidak ikut
#   memengaruhi hasil evaluasi baseline.
# ============================================================

import csv
import time
from pathlib import Path

import _bootstrap  # noqa: F401  (menyiapkan sys.path ke folder chatbotv2)

from database import buka_collection
from embedding import muat_model
from tetangga import retriever_dengan_tetangga, urutkan_id_chunk_teks
from llm import panggil_llm
from tanya_jawab import susun_konteks, bangun_prompt


# Folder script ini (chatbotv2/uji). File soal dan hasil evaluasi
# disimpan di folder yang sama.
BASE_DIR = Path(__file__).resolve().parent
FILE_SOAL = BASE_DIR / "Soal_Jawaban_JAKEVO.csv"
FILE_HASIL = BASE_DIR / "hasil_evaluasi_batch.csv"

# Konfigurasi dibuat sama seperti baseline chatbot saat ini.
TOPK = 10
JUMLAH_CHUNK = 3
JUMLAH_TETANGGA = 1
JEDA_ANTAR_SOAL_DETIK = 1.0

# None = jalankan semua soal.
# Untuk uji coba kecil, ubah menjadi 5 atau 10 terlebih dahulu.
BATAS_SOAL = None


def normalisasi_nama_kolom(nama):
    """Menyederhanakan nama kolom untuk pencarian yang toleran."""
    return " ".join(str(nama or "").strip().lower().split())


def ambil_kolom(baris, *nama_alternatif, default=""):
    """Ambil nilai dari beberapa kemungkinan nama kolom."""
    indeks = {
        normalisasi_nama_kolom(kunci): nilai
        for kunci, nilai in baris.items()
    }

    for nama in nama_alternatif:
        kunci = normalisasi_nama_kolom(nama)
        if kunci in indeks and indeks[kunci] is not None:
            return str(indeks[kunci]).strip()

    return default


def cari_file_excel_soal(folder):
    """Cari workbook Excel yang memiliki kolom Pertanyaan dan Jawaban."""
    kandidat = []
    ekstensi = ("*.xlsx", "*.xlsm")

    for pola in ekstensi:
        for path in folder.glob(pola):
            if path.name.startswith("~$") or path.name == FILE_HASIL.name:
                continue

            try:
                from openpyxl import load_workbook
            except ImportError as error:
                raise ImportError(
                    "Untuk membaca soal Excel (.xlsx), pasang dependensi dengan:\n"
                    "python -m pip install openpyxl\n"
                    "Atau simpan workbook sebagai CSV UTF-8."
                ) from error

            try:
                workbook = load_workbook(path, read_only=True, data_only=True)
                cocok = False
                for sheet in workbook.worksheets:
                    rows = sheet.iter_rows(values_only=True)
                    header = next(rows, None)
                    if not header:
                        continue
                    nama_kolom = {normalisasi_nama_kolom(v) for v in header if v is not None}
                    if "pertanyaan" in nama_kolom and "jawaban" in nama_kolom:
                        cocok = True
                        break
                workbook.close()
                if cocok:
                    kandidat.append(path)
            except Exception:
                # Abaikan workbook yang tidak bisa dibaca; lanjutkan mencari.
                continue

    if not kandidat:
        return None

    # Prioritaskan nama workbook benchmark yang pernah digunakan dalam proyek.
    prioritas = [
        "Soal_Jawaban_JAKEVO_100_Revisi_Mirip_Panduan.xlsx",
        "Soal_Jawaban_JAKEVO_100_Final.xlsx",
        "Soal_Jawaban_JAKEVO.xlsx",
    ]
    nama_kandidat = {path.name.lower(): path for path in kandidat}
    for nama in prioritas:
        if nama.lower() in nama_kandidat:
            return nama_kandidat[nama.lower()]

    if len(kandidat) == 1:
        return kandidat[0]

    daftar = "\n".join(f"- {path.name}" for path in kandidat)
    raise FileNotFoundError(
        "Ditemukan beberapa workbook dengan kolom Pertanyaan dan Jawaban.\n"
        f"Letakkan hanya workbook soal yang ingin dipakai di folder ini, atau sesuaikan nama pada daftar prioritas di fungsi cari_file_excel_soal().\n{daftar}"
    )


def baca_soal(path):
    """Membaca soal dari CSV atau Excel. CSV diprioritaskan jika tersedia."""
    if path.exists():
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            contoh = file.read(4096)
            file.seek(0)

            try:
                dialek = csv.Sniffer().sniff(contoh, delimiters=",;\t")
            except csv.Error:
                dialek = csv.excel

            reader = csv.DictReader(file, dialect=dialek)
            soal = []

            for nomor_baris, baris in enumerate(reader, start=2):
                pertanyaan = ambil_kolom(baris, "Pertanyaan", "Question")
                if not pertanyaan:
                    continue

                soal.append({
                    "no": ambil_kolom(baris, "No", "Nomor", default=str(len(soal) + 1)),
                    "kategori": ambil_kolom(baris, "Kategori", "Category"),
                    "halaman_acuan": ambil_kolom(
                        baris, "Halaman (PDF)", "Halaman PDF", "Halaman", "Page"
                    ),
                    "pertanyaan": pertanyaan,
                    "jawaban_acuan": ambil_kolom(
                        baris, "Jawaban", "Jawaban Acuan", "Answer"
                    ),
                    "baris_sumber": nomor_baris,
                })

        if not soal:
            raise ValueError(
                f"Tidak ada pertanyaan yang terbaca dari {path.name}. "
                "Pastikan CSV memiliki kolom 'Pertanyaan'."
            )

        return soal, path

    # Jika CSV default tidak tersedia, cari workbook Excel secara otomatis.
    path_excel = cari_file_excel_soal(path.parent)
    if path_excel is None:
        raise FileNotFoundError(
            f"File CSV tidak ditemukan: {path}\n"
            "Saya juga tidak menemukan workbook Excel (.xlsx/.xlsm) yang memiliki "
            "kolom 'Pertanyaan' dan 'Jawaban'. Letakkan file Excel soal di folder "
            "yang sama dengan evaluasi_batch.py, atau ekspor menjadi CSV UTF-8."
        )

    try:
        from openpyxl import load_workbook
    except ImportError as error:
        raise ImportError(
            "Workbook Excel ditemukan, tetapi library openpyxl belum tersedia.\n"
            "Jalankan: python -m pip install openpyxl"
        ) from error

    workbook = load_workbook(path_excel, read_only=True, data_only=True)
    soal = []
    sheet_terpilih = None

    try:
        for sheet in workbook.worksheets:
            values = sheet.iter_rows(values_only=True)
            header = next(values, None)
            if not header:
                continue

            nama_header = [str(v).strip() if v is not None else "" for v in header]
            header_normal = {normalisasi_nama_kolom(v) for v in nama_header}
            if "pertanyaan" not in header_normal or "jawaban" not in header_normal:
                continue

            sheet_terpilih = sheet.title
            indeks_header = {
                normalisasi_nama_kolom(nama): i
                for i, nama in enumerate(nama_header)
                if nama
            }

            def nilai(row, *alternatif, default=""):
                for nama in alternatif:
                    idx = indeks_header.get(normalisasi_nama_kolom(nama))
                    if idx is not None and idx < len(row) and row[idx] is not None:
                        return str(row[idx]).strip()
                return default

            for nomor_baris, row in enumerate(values, start=2):
                pertanyaan = nilai(row, "Pertanyaan", "Question")
                if not pertanyaan:
                    continue

                soal.append({
                    "no": nilai(row, "No", "Nomor", default=str(len(soal) + 1)),
                    "kategori": nilai(row, "Kategori", "Category"),
                    "halaman_acuan": nilai(
                        row, "Halaman (PDF)", "Halaman PDF", "Halaman", "Page"
                    ),
                    "pertanyaan": pertanyaan,
                    "jawaban_acuan": nilai(row, "Jawaban", "Jawaban Acuan", "Answer"),
                    "baris_sumber": nomor_baris,
                })

            if soal:
                break
    finally:
        workbook.close()

    if not soal:
        raise ValueError(
            f"Workbook {path_excel.name} tidak memiliki baris pertanyaan yang terbaca."
        )

    print(f"Workbook Excel : {path_excel.name}")
    print(f"Sheet soal     : {sheet_terpilih}")
    return soal, path_excel


def halaman_ke_int(nilai):
    """Ubah halaman seperti '34' atau '34.0' menjadi int; selain itu None."""
    try:
        return int(float(str(nilai).strip()))
    except (TypeError, ValueError):
        return None


def ringkas_chunk(hasil):
    """Buat ringkasan ID, halaman, jenis, dan distance dari hasil retrieval."""
    daftar = []
    halaman = set()

    for chunk in hasil:
        metadata = chunk.get("metadata") or {}
        page = metadata.get("page")
        if page is not None:
            halaman.add(str(page))

        distance = chunk.get("distance")
        if isinstance(distance, (int, float)):
            distance_text = f"{distance:.6f}"
        else:
            distance_text = "tetangga"

        daftar.append(
            f"{chunk.get('chunk_id', '')}"
            f" [halaman={page}; jenis={metadata.get('jenis')}; distance={distance_text}]"
        )

    return " | ".join(daftar), ", ".join(sorted(halaman, key=lambda x: int(x) if x.isdigit() else x))


def main():
    soal, file_soal_dipakai = baca_soal(FILE_SOAL)

    if BATAS_SOAL is not None:
        soal = soal[:BATAS_SOAL]

    print("=" * 68)
    print("EVALUASI BATCH CHATBOT JAKEVO")
    print("=" * 68)
    print(f"File soal          : {file_soal_dipakai.name}")
    print(f"Jumlah pertanyaan  : {len(soal)}")
    print(f"Top-k              : {TOPK}")
    print(f"Jumlah hasil yang diperluas: {JUMLAH_CHUNK}")
    print(f"Jumlah tetangga berikutnya: {JUMLAH_TETANGGA}")
    print(f"File hasil         : {FILE_HASIL.name}")
    print("Catatan: jawaban tidak dinilai otomatis; evaluasi kebenaran dilakukan setelah hasil dikumpulkan.")
    print("=" * 68)

    # Muat resource sekali saja, bukan per pertanyaan.
    collection = buka_collection()
    model = muat_model()
    urut = urutkan_id_chunk_teks(collection)

    kolom_hasil = [
        "No", "Kategori", "Halaman_Acuan_PDF", "Pertanyaan", "Jawaban_Acuan",
        "Jumlah_Chunk", "Chunk_ID_Halaman_Distance", "Halaman_Retrieved",
        "Halaman_Acuan_Masuk_Hasil", "Jawaban_LLM", "Status_API",
        "Penilaian_Manual", "Catatan_Manual",
    ]

    # Tulis header dahulu dan simpan setiap baris segera, supaya hasil
    # yang sudah selesai tidak hilang jika terjadi rate limit / gangguan.
    with FILE_HASIL.open("w", encoding="utf-8-sig", newline="") as file_hasil:
        writer = csv.DictWriter(file_hasil, fieldnames=kolom_hasil)
        writer.writeheader()
        file_hasil.flush()

        for urutan, item in enumerate(soal, start=1):
            pertanyaan = item["pertanyaan"]
            halaman_acuan_int = halaman_ke_int(item["halaman_acuan"])

            print(f"\n[{urutan}/{len(soal)}] Soal {item['no']}: {pertanyaan}")

            hasil = []
            jawaban = ""
            status_api = "OK"
            catatan_error = ""

            try:
                # Baseline normal: tidak menambahkan chunk IDM secara manual.
                hasil = retriever_dengan_tetangga(
                    collection,
                    model,
                    pertanyaan,
                    urut,
                    topk=TOPK,
                    jumlah_chunk=JUMLAH_CHUNK,
                    jumlah_tetangga=JUMLAH_TETANGGA,
                )

                konteks = susun_konteks(hasil)
                prompt = bangun_prompt(pertanyaan, konteks)
                hasil_llm = panggil_llm(prompt)

                if hasil_llm is None:
                    jawaban = ""
                    status_api = "GAGAL_LLM"
                    catatan_error = "panggil_llm mengembalikan None; cek log API di terminal."
                else:
                    jawaban = str(hasil_llm).strip()

            except Exception as error:
                status_api = "ERROR_PIPELINE"
                catatan_error = f"{type(error).__name__}: {error}"

            daftar_chunk, halaman_retrieved = ringkas_chunk(hasil)
            halaman_retrieved_int = {
                halaman_ke_int(p) for p in halaman_retrieved.split(",") if p.strip()
            }

            if halaman_acuan_int is None:
                halaman_acuan_masuk = "TIDAK_DIKETAHUI"
            else:
                halaman_acuan_masuk = (
                    "YA" if halaman_acuan_int in halaman_retrieved_int else "TIDAK"
                )

            writer.writerow({
                "No": item["no"],
                "Kategori": item["kategori"],
                "Halaman_Acuan_PDF": item["halaman_acuan"],
                "Pertanyaan": pertanyaan,
                "Jawaban_Acuan": item["jawaban_acuan"],
                "Jumlah_Chunk": len(hasil),
                "Chunk_ID_Halaman_Distance": daftar_chunk,
                "Halaman_Retrieved": halaman_retrieved,
                "Halaman_Acuan_Masuk_Hasil": halaman_acuan_masuk,
                "Jawaban_LLM": jawaban,
                "Status_API": status_api,
                "Penilaian_Manual": "",
                "Catatan_Manual": catatan_error,
            })
            file_hasil.flush()

            print(f"  Status API           : {status_api}")
            print(f"  Jumlah chunk         : {len(hasil)}")
            print(f"  Halaman acuan diambil: {halaman_acuan_masuk}")
            print(f"  Jawaban              : {jawaban[:240] if jawaban else '[kosong / gagal]'}")

            if urutan < len(soal) and JEDA_ANTAR_SOAL_DETIK > 0:
                time.sleep(JEDA_ANTAR_SOAL_DETIK)

    print("\n" + "=" * 68)
    print("EVALUASI SELESAI")
    print(f"Hasil disimpan ke: {FILE_HASIL}")
    print("Buka CSV hasil dengan Excel, lalu isi Penilaian_Manual:")
    print("BENAR / PARSIAL / TIDAK DITEMUKAN / SALAH / TIDAK DIDUKUNG / ERROR")
    print("Catatan: Halaman_Acuan_Masuk_Hasil hanya indikator awal, bukan bukti final relevansi.")
    print("=" * 68)


if __name__ == "__main__":
    main()
