
# ============================================================
# bandingkan_distance.py
# Membandingkan relevansi embedding pertanyaan dengan chunk
# jawaban yang benar dan chunk yang berada di peringkat pertama.
# Jalankan (dari folder chatbotv2): python uji/bandingkan_distance.py
# ============================================================

import torch

from _bootstrap import cari_banyak_id_nyata

from database import buka_collection
from embedding import muat_model


PERTANYAAN = "Isian apa yang perlu diinput pemohon?"

# Ditulis tanpa awalan dokumen. Akan diterjemahkan ke chunk_id
# nyata oleh cari_banyak_id_nyata().
ID_CHUNK_TARGET = [
    "TXT-P018-C001",
    "TBL-P004-T001-R002",
]


def main():
    # --------------------------------------------------------
    # 1. MEMUAT MODEL DAN DATABASE
    # --------------------------------------------------------

    collection = buka_collection()
    model = muat_model()

    print("Pertanyaan:", PERTANYAAN)
    print("Total data ChromaDB:", collection.count())

    # --------------------------------------------------------
    # 2. MEMBUAT EMBEDDING PERTANYAAN
    # --------------------------------------------------------

    query = model.encode(
        ["query: " + PERTANYAAN],
        normalize_embeddings=True,
        convert_to_tensor=True,
    )

    # --------------------------------------------------------
    # 3. MENAMPILKAN 10 HASIL RETRIEVAL TERATAS
    # --------------------------------------------------------

    hasil = collection.query(
        query_embeddings=query.cpu().tolist(),
        n_results=10,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    print("\n=== PERINGKAT 10 TERATAS ===")

    for i, chunk_id in enumerate(hasil["ids"][0]):
        metadata = hasil["metadatas"][0][i] or {}
        distance = hasil["distances"][0][i]

        print(f"\nPeringkat : {i + 1}")
        print(f"Chunk ID  : {chunk_id}")
        print(f"Halaman   : {metadata.get('page')}")
        print(f"Distance  : {distance}")
        print(f"Teks      : {hasil['documents'][0][i]}")

    # --------------------------------------------------------
    # 4. MENGAMBIL EMBEDDING CHUNK TARGET
    # --------------------------------------------------------

    id_target = cari_banyak_id_nyata(
        collection,
        ID_CHUNK_TARGET,
    )

    if not id_target:
        print(
            "\nTidak ada chunk target yang ditemukan. "
            "Jalankan ulang 'python main.py' bila database belum dibangun."
        )
        return

    target = collection.get(
        ids=id_target,
        include=[
            "documents",
            "metadatas",
            "embeddings",
        ],
    )

    if not target["ids"]:
        print("\nTidak ada chunk target yang ditemukan.")
        return

    # --------------------------------------------------------
    # 5. MEMBANDINGKAN COSINE SIMILARITY
    # --------------------------------------------------------

    print("\n\n=== PERBANDINGAN CHUNK TARGET ===")

    for i, chunk_id in enumerate(target["ids"]):
        metadata = target["metadatas"][i] or {}

        # Samakan tipe data kedua vektor menjadi float32.
        vektor_chunk = torch.as_tensor(
            target["embeddings"][i],
            dtype=torch.float32,
        ).unsqueeze(0)

        vektor_query = query.to(
            device="cpu",
            dtype=torch.float32,
        )

        similarity = model.similarity(
            vektor_query,
            vektor_chunk,
        ).item()

        print("\n" + "=" * 60)
        print("ID                :", chunk_id)
        print("Halaman           :", metadata.get("page"))
        print(f"Cosine similarity : {similarity:.6f}")
        print("Teks              :", target["documents"][i])

    print("\nCatatan:")
    print("- Cosine similarity yang lebih tinggi menunjukkan")
    print("  arah vektor yang lebih mirip.")
    print("- Distance ChromaDB dan similarity perlu dibaca")
    print("  sesuai metrik yang digunakan oleh collection.")


if __name__ == "__main__":
    main()
