
import _bootstrap  # noqa: F401  (menyiapkan sys.path ke folder chatbotv2)

from database import buka_collection


def main():
    # Membuka collection yang digunakan chatbot.
    collection = buka_collection()

    print("Total data dalam ChromaDB:", collection.count())

    # Memeriksa semua chunk dengan metadata page = 18.
    hasil = collection.get(
        where={"page": 8},
        include=["documents", "metadatas"],
    )

    daftar_id = hasil["ids"]
    daftar_teks = hasil["documents"]
    daftar_metadata = hasil["metadatas"]

    print("Jumlah chunk halaman 8:", len(daftar_id))

    if not daftar_id:
        print("Belum ditemukan chunk dengan metadata halaman 18.")
        return

    for i, chunk_id in enumerate(daftar_id):
        print("\n" + "=" * 50)
        print("ID       :", chunk_id)
        print("Metadata :", daftar_metadata[i])
        print("Teks     :", daftar_teks[i])


if __name__ == "__main__":
    main()
