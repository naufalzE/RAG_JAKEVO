import _bootstrap  # noqa: F401
from pathlib import Path
from scraping.baca_web import baca_halaman_web
from core.config import NAMA_MODEL_EMBEDDING
from storage.database import buka_collection
from storage.embedding import muat_model
from retrieval.retriever import retriever

FOLDER_WEB = Path(_bootstrap.FOLDER_PROYEK) / "dokumen_web"
BAWAH_UMUR = FOLDER_WEB / "PM1_PERKAWINAN_BAWAH_UMUR.txt"
PERTAMA = FOLDER_WEB / "PM1_PERKAWINAN_PERTAMA.txt"


def uji_tumpang_tindih():
    """Menghitung berapa butir syarat yang identik di dua dokumen."""
    a = {b["teks"] for b in baca_halaman_web(BAWAH_UMUR)["syarat"]}
    b = {x["teks"] for x in baca_halaman_web(PERTAMA)["syarat"]}
    sama = a & b
    kecil = min(len(a), len(b))

    print(f"Butir bawah_umur: {len(a)} | pertama: {len(b)} | identik: {len(sama)}")
    print(f"Identik dari dokumen yang lebih kecil: {len(sama) / kecil:.0%}")
    for teks in sorted(sama):
        print("  -", teks[:70])


def uji_retrieval(pertanyaan, collection, model, topk=5):
    """Melihat chunk apa yang diambil untuk satu pertanyaan."""
    print("\nPertanyaan:", pertanyaan)
    for i, h in enumerate(retriever(collection, model, pertanyaan, topk), 1):
        print(f"{i}. {h['chunk_id']}  jarak={h['distance']:.3f}")


if __name__ == "__main__":
    print("=== UJI 1: TUMPANG TINDIH ===")
    uji_tumpang_tindih()

    collection = buka_collection()
    model = muat_model(NAMA_MODEL_EMBEDDING)

    print("\n=== UJI 2: PERTANYAAN SATU LAYANAN ===")
    uji_retrieval("apa syarat surat pengantar perkawinan pertama", collection, model)
