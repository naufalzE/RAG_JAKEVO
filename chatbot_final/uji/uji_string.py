import chromadb

import _bootstrap  # noqa: F401  (menyiapkan sys.path ke folder chatbotv2)

from database import hapus_id_basi

client = chromadb.Client()
col = client.get_or_create_collection("uji_string")
col.upsert(
    ids=["a", "b", "c"],
    documents=["teks a", "teks b", "teks c"],
    embeddings=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
)

# Uji 1: string harus ditolak dengan TypeError, collection tidak berubah.
# Dugaan: TypeError muncul, ID tersisa tetap a, b, c.
try:
    hapus_id_basi(col, "abc")
except TypeError as e:
    print("Uji 1 TypeError:", e)
else:
    raise AssertionError("String seharusnya memicu TypeError")

print("Sisa di collection:", sorted(col.get()["ids"]))
assert sorted(col.get()["ids"]) == ["a", "b", "c"]

# Uji 2: input yang benar tetap jalan.
# Dugaan: kembali 1, sisa a dan b.
hasil = hapus_id_basi(col, ["c"])
print("Uji 2:", hasil, sorted(col.get()["ids"]))
assert hasil == 1
assert sorted(col.get()["ids"]) == ["a", "b"]

print("Semua uji lulus.")