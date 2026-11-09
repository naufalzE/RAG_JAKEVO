# ============================================================
# uji_idm.py
# Cek chunk yang memuat "IDM" dan peringkatnya di hasil retriever.
# Jalankan (dari folder chatbotv2): python uji/uji_idm.py
# ============================================================

import _bootstrap  # noqa: F401  (menyiapkan sys.path ke folder chatbotv2)

from database import buka_collection
from embedding import muat_model
from retriever import retriever


def main():
    # 1. Buka collection dan model (pola sama seperti uji_peringkat.py).
    collection = buka_collection()
    model = muat_model()

    # 2. Cari chunk yang memuat teks "IDM".
    hasil_idm = collection.get(where_document={"$contains": "IDM"})

    id_idm = hasil_idm["ids"]

    print("=== CHUNK YANG MEMUAT 'IDM' ===")
    print("ids:", id_idm)
    for id_chunk, teks in zip(hasil_idm["ids"], hasil_idm["documents"]):
        print(f"\n--- {id_chunk} ---")
        print(teks)

    # 3. Jalankan soal 3 dan lihat peringkat chunk IDM.
    pertanyaan = "Kenapa preview SK izin tidak terlihat?"

    hasil = retriever(collection, model, pertanyaan, topk=97)

    print("\n=== PERINGKAT CHUNK IDM ===")
    print(f"Pertanyaan: {pertanyaan}")
    print(f"Jumlah hasil: {len(hasil)}")

    kumpulan_id_idm = set(id_idm)
    ditemukan = False

    for nomor, chunk in enumerate(hasil, start=1):
        if chunk["chunk_id"] in kumpulan_id_idm:
            ditemukan = True
            print(
                f"peringkat={nomor} "
                f"| chunk_id={chunk['chunk_id']} "
                f"| distance={chunk['distance']}"
            )

    if not ditemukan:
        print("Tidak ada chunk IDM di dalam top-97.")


if __name__ == "__main__":
    main()