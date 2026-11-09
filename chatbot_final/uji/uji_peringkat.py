# ============================================================
# uji_peringkat.py
# Uji peringkat hasil retriever (tanpa menyentuh kode utama).
# Jalankan (dari folder chatbotv2): python uji/uji_peringkat.py
# ============================================================

import _bootstrap  # noqa: F401  (menyiapkan sys.path ke folder chatbotv2)

from database import buka_collection
from embedding import muat_model
from tetangga import retriever_dengan_tetangga, urutkan_id_chunk_teks


def main():
    # 1. Buka collection dan model.
    collection = buka_collection()
    model = muat_model()

    # 2. Hitung urutan id chunk teks sekali saja.
    urut = urutkan_id_chunk_teks(collection)

    # 3. Cari chunk relevan beserta tetangganya.
    pertanyaan = "Kenapa SK izin saya tidak muncul di layar?"
    hasil = retriever_dengan_tetangga(
        collection, model, pertanyaan, urut,
        topk=5
    )

    # 4. Cetak peringkat tiap chunk.
    print(f"Pertanyaan: {pertanyaan}")
    print(f"Jumlah hasil: {len(hasil)}\n")

    for nomor, chunk in enumerate(hasil, start=1):
        halaman = chunk["metadata"].get("page")
        distance = chunk["distance"]
        print(
            f"{nomor}. chunk_id={chunk['chunk_id']} "
            f"| halaman={halaman} "
            f"| distance={distance}"
        )


if __name__ == "__main__":
    main()
