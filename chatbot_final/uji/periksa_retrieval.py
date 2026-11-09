
import _bootstrap  # noqa: F401  (menyiapkan sys.path ke folder chatbotv2)

from database import buka_collection
from embedding import muat_model
from retriever import retriever

pertanyaan = "Isian apa yang perlu diinput pemohon?"

collection = buka_collection()
model = muat_model()

hasil = retriever(
    collection,
    model,
    pertanyaan,
    topk=10,
)

print("Pertanyaan:", pertanyaan)
print("Jumlah hasil:", len(hasil))

for nomor, chunk in enumerate(hasil, start=1):
    metadata = chunk.get("metadata") or {}

    print("\n" + "=" * 60)
    print("Peringkat :", nomor)
    print("Chunk ID  :", chunk.get("chunk_id"))
    print("Halaman   :", metadata.get("page"))
    print("Distance  :", chunk.get("distance"))
    print("Teks      :", chunk.get("teks"))
