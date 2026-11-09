import chromadb

import _bootstrap  # noqa: F401  (menyiapkan sys.path ke folder chatbotv2)

from database import cari_id_basi
from models import Chunk

client = chromadb.Client()  # di memori, hilang saat skrip selesai
col = client.get_or_create_collection("uji")


def buat_chunk(id_):
    return Chunk(chunk_id=id_, teks="teks " + id_, page=1, jenis="teks")


# Langkah 1: simpan 3 chunk lama
lama = [buat_chunk("a"), buat_chunk("b"), buat_chunk("c")]
col.upsert(
    ids=[c.chunk_id for c in lama],
    documents=[c.teks for c in lama],
    embeddings=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],  # vektor mainan 3 dimensi
)

# ------------------------------------------------------------
# Uji 1: daftar baru hanya berisi a dan b -> "c" basi
# Dugaan: ["c"]
# ------------------------------------------------------------
baru = [buat_chunk("a"), buat_chunk("b")]
hasil_1 = cari_id_basi(col, baru)
print("Uji 1:", hasil_1)
assert hasil_1 == ["c"], f"Dugaan ['c'], hasil {hasil_1}"

# ------------------------------------------------------------
# Uji 2: daftar baru sama persis dengan isi collection
# Dugaan: tidak ada ID basi -> []
# ------------------------------------------------------------
hasil_2 = cari_id_basi(col, lama)
print("Uji 2:", hasil_2)
assert hasil_2 == [], f"Dugaan [], hasil {hasil_2}"

# ------------------------------------------------------------
# Uji 3: semua chunk hilang -> semua ID di collection basi
# Dugaan: ["a", "b", "c"] (urut karena sorted)
# ------------------------------------------------------------
hasil_3 = cari_id_basi(col, [])
print("Uji 3:", hasil_3)
assert hasil_3 == ["a", "b", "c"], f"Dugaan ['a', 'b', 'c'], hasil {hasil_3}"

# ------------------------------------------------------------
# Uji 4: delete(ids=[]) TIDAK boleh dipanggil
# ChromaDB melempar ValueError, bukan menghapus 0 baris.
# Dugaan: ValueError "Expected IDs to be a non-empty list..."
# ------------------------------------------------------------
try:
    col.delete(ids=[])
except ValueError as e:
    print("Uji 4 (delete list kosong):", e)
else:
    raise AssertionError("delete(ids=[]) seharusnya melempar ValueError")

# Jumlah data tidak berubah: delete dengan list kosong gagal
assert col.count() == 3, f"Jumlah data berubah: {col.count()}"
print("Jumlah data:", col.count())

# ------------------------------------------------------------
# Kesimpulan: hapus hanya jika daftar ID basi tidak kosong
# ------------------------------------------------------------
id_basi = cari_id_basi(col, baru)
if id_basi:
    col.delete(ids=id_basi)

print("Sisa ID di collection:", sorted(col.get()["ids"]))
assert sorted(col.get()["ids"]) == ["a", "b"]

print("Semua uji lulus.")