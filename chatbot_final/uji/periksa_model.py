
from _bootstrap import cari_id_nyata

from config import NAMA_MODEL_EMBEDDING
from embedding import muat_model
from database import buka_collection

print("Model dari config:", NAMA_MODEL_EMBEDDING)

model = muat_model()
print("Dimensi embedding model:", model.get_sentence_embedding_dimension())

collection = buka_collection()
print("Jumlah data ChromaDB:", collection.count())

# ID gaya lama (tanpa awalan dokumen) diterjemahkan ke ID nyata
# yang tersimpan di ChromaDB.
id_target = cari_id_nyata(collection, "TXT-P018-C001")
print("ID target ditemukan:", id_target)

if not id_target:
    print(
        "Chunk target tidak ditemukan. "
        "Jalankan ulang 'python main.py' untuk membangun ulang database."
    )
    raise SystemExit(1)

hasil = collection.get(
    ids=id_target,
    include=["documents", "metadatas", "embeddings"],
)

print("Chunk ditemukan:", len(hasil["ids"]))

if hasil["ids"]:
    print("ID:", hasil["ids"][0])
    print("Metadata:", hasil["metadatas"][0])
    print("Teks:", hasil["documents"][0])
    print("Dimensi embedding tersimpan:", len(hasil["embeddings"][0]))
