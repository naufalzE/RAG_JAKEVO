# ============================================================
# main.py
# Titik masuk: PDF + berkas web -> chunk -> embedding -> ChromaDB.
# Jalankan dengan: python main.py
# ============================================================

import sys
from pathlib import Path

# Pastikan chatbotv2 ada di sys.path saat dijalankan langsung
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from chunking.chunker import proses_dokumen
from scraping.baca_web import BerkasWebTidakValid
from core.config import (
    FOLDER_DOKUMEN,
    FOLDER_DOKUMEN_WEB,
    NAMA_MODEL_EMBEDDING,
    daftar_file_pdf,
    daftar_file_web,
)
from storage.database import (
    buka_collection,
    simpan_ke_chroma,
    cari_id_basi,
    hapus_id_basi,
)
from storage.embedding import buat_embedding, muat_model
from core.utils import cek_keunikan_id


def main():
    # 1. Mencari seluruh PDF dan berkas web di foldernya masing-masing
    daftar_pdf = daftar_file_pdf()
    daftar_web = daftar_file_web()

    if not daftar_pdf and not daftar_web:
        print("Folder PDF:", FOLDER_DOKUMEN)
        print("Folder web:", FOLDER_DOKUMEN_WEB)
        print(
            "Tidak ada file PDF maupun berkas web (.txt) yang "
            "ditemukan. Letakkan dokumen di salah satu folder "
            "tersebut lalu jalankan ulang."
        )
        return

    print("Folder PDF    :", FOLDER_DOKUMEN)
    print("Jumlah PDF    :", len(daftar_pdf))
    print("Folder web    :", FOLDER_DOKUMEN_WEB)
    print("Jumlah web    :", len(daftar_web))

    # 2. Memuat model embedding
    model = muat_model(NAMA_MODEL_EMBEDDING)

    # 3. Membentuk seluruh chunk dari SEMUA PDF dan SEMUA berkas web
    # menggunakan façade cerdas proses_dokumen
    chunks = []

    for path in daftar_pdf:
        print(f"\n=== MEMPROSES PDF: {path.name} ===")
        chunk_dokumen = proses_dokumen(path)
        print(f"Chunk dari {path.name}:", len(chunk_dokumen))
        chunks.extend(chunk_dokumen)

    for path in daftar_web:
        print(f"\n=== MEMPROSES WEB: {path.name} ===")
        try:
            chunk_halaman = proses_dokumen(path)
        except BerkasWebTidakValid as galat:
            print("[gagal]", galat)
            print("Proses dibatalkan; ChromaDB tidak diubah.")
            raise SystemExit(1) from galat

        print(f"Chunk dari {path.name}:", len(chunk_halaman))
        chunks.extend(chunk_halaman)

    print("\nTotal chunk seluruh dokumen:", len(chunks))

    # 4. Memvalidasi keunikan ID chunk antar dokumen
    cek_keunikan_id(chunks)

    # 5. Mengubah teks chunk menjadi embedding
    vektor = buat_embedding(chunks, model)
    print("Shape embedding:", vektor.shape)

    # 6. Membuka collection ChromaDB
    collection = buka_collection()

    # 7. Menyimpan chunk terbaru terlebih dahulu (upsert)
    simpan_ke_chroma(collection, chunks, vektor)

    # 8. Mencari ID basi yang tidak ada dalam chunk terbaru
    id_basi = cari_id_basi(collection, chunks)

    # 9. Menghapus ID basi
    jumlah_dihapus = hapus_id_basi(collection, id_basi)
    print("ID basi dihapus:", jumlah_dihapus)

    # 10. Memeriksa hasil akhir
    print("Total chunk terbaru:", len(chunks))
    print("Jumlah data tersimpan:", collection.count())


if __name__ == "__main__":
    main()
