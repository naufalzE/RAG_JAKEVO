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
from core.logger import get_logger

logger = get_logger("ingestion")


def main():
    # 1. Mencari seluruh PDF dan berkas web di foldernya masing-masing
    daftar_pdf = daftar_file_pdf()
    daftar_web = daftar_file_web()

    if not daftar_pdf and not daftar_web:
        logger.error(
            f"Tidak ada PDF ({FOLDER_DOKUMEN}) maupun file web ({FOLDER_DOKUMEN_WEB}) yang ditemukan."
        )
        return

    logger.info(
        f"[Ingestion] Memulai proses ingesti. PDF: {len(daftar_pdf)} berkas, Web: {len(daftar_web)} berkas."
    )

    # 2. Memuat model embedding
    logger.info(f"[Ingestion] Memuat model embedding: {NAMA_MODEL_EMBEDDING}")
    model = muat_model(NAMA_MODEL_EMBEDDING)

    # 3. Membentuk seluruh chunk dari SEMUA PDF dan SEMUA berkas web
    chunks = []

    for path in daftar_pdf:
        logger.info(f"=== MEMPROSES PDF: {path.name} ===")
        chunk_dokumen = proses_dokumen(path)
        logger.info(f"Chunk dari {path.name}: {len(chunk_dokumen)}")
        chunks.extend(chunk_dokumen)

    for path in daftar_web:
        logger.info(f"=== MEMPROSES WEB: {path.name} ===")
        try:
            chunk_halaman = proses_dokumen(path)
        except BerkasWebTidakValid as galat:
            logger.error(f"[Ingestion Gagal] {galat}")
            raise SystemExit(1) from galat

        logger.info(f"Chunk dari {path.name}: {len(chunk_halaman)}")
        chunks.extend(chunk_halaman)

    logger.info(f"Total chunk seluruh dokumen: {len(chunks)}")

    # 4. Memvalidasi keunikan ID chunk antar dokumen
    cek_keunikan_id(chunks)

    # 5. Mengubah teks chunk menjadi embedding
    logger.info("Membuat vektor embedding...")
    vektor = buat_embedding(chunks, model)
    logger.info(f"Shape embedding: {vektor.shape}")

    # 6. Membuka collection ChromaDB
    collection = buka_collection()

    # 7. Menyimpan chunk terbaru terlebih dahulu (upsert)
    logger.info("Menyimpan chunk ke ChromaDB (upsert)...")
    simpan_ke_chroma(collection, chunks, vektor)

    # 8. Mencari ID basi yang tidak ada dalam chunk terbaru
    id_basi = cari_id_basi(collection, chunks)

    # 9. Menghapus ID basi
    jumlah_dihapus = hapus_id_basi(collection, id_basi)
    logger.info(f"ID basi dibersihkan: {jumlah_dihapus}")

    # 10. Memeriksa hasil akhir
    total_tersimpan = collection.count()
    logger.info(f"[Ingestion Sukses] Total data tersimpan di ChromaDB: {total_tersimpan}")


if __name__ == "__main__":
    main()
