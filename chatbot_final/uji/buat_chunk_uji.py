import _bootstrap  # noqa: F401  (menyiapkan sys.path ke folder chatbotv2)

from database import buka_collection

collection = buka_collection()
id_uji = "UJI-BASI-001"

collection.upsert(
    ids=[id_uji],
    documents=["Chunk buatan untuk menguji penghapusan ID basi."],
    metadatas=[{"page": 999, "jenis": "uji"}],
    embeddings=[[0.1] * 384],
)

print("Jumlah data:", collection.count())
print("Chunk uji ada:", id_uji in collection.get()["ids"])