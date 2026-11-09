import chromadb

import _bootstrap  # noqa: F401  (menyiapkan sys.path ke folder chatbotv2)

from database import hapus_id_basi

client = chromadb.Client()
col = client.get_or_create_collection("uji_hapus")

col.upsert(
    ids=["a", "b", "c"],
    documents=["teks a", "teks b", "teks c"],
    embeddings=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
)

# Uji 1: hapus ["c"] -> kembali 1, sisa a dan b
hasil_1 = hapus_id_basi(col, ["c"])
print("Uji 1:", hasil_1, sorted(col.get()["ids"]))
assert hasil_1 == 1
assert sorted(col.get()["ids"]) == ["a", "b"]

# Uji 2: list kosong -> kembali 0, tidak error, isi tetap 2
hasil_2 = hapus_id_basi(col, [])
print("Uji 2:", hasil_2, col.count())
assert hasil_2 == 0
assert col.count() == 2

# Uji 3: input set -> kembali 1, sisa a
hasil_3 = hapus_id_basi(col, {"b"})
print("Uji 3:", hasil_3, sorted(col.get()["ids"]))
assert hasil_3 == 1
assert sorted(col.get()["ids"]) == ["a"]

print("Uji 1-3 lulus.")

# Uji 4: salah pakai, string dikirim sebagai ganti list.
# Tanpa assert: amati sendiri apa yang terjadi.
col.upsert(
    ids=["id-panjang"],
    documents=["teks panjang"],
    embeddings=[[1, 1, 0]],
)
hasil_4 = hapus_id_basi(col, "id-panjang")
print("Uji 4 nilai kembali:", hasil_4)
print("Uji 4 isi collection:", sorted(col.get()["ids"]))