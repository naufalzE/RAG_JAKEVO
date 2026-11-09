# ============================================================
# tes.py
# Uji retrieval: peringkat chunk target untuk tiap pertanyaan.
# Jalankan (dari folder chatbotv2): python uji/tes.py
# ============================================================

from _bootstrap import cocok_id

from config import NAMA_MODEL_EMBEDDING
from database import buka_collection
from embedding import muat_model
from retriever import retriever

TOPK = 10

SOAL = [
    {
        "pertanyaan": "Izin saya ditolak, saya harus ngapain",
        "target": "TXT-P036-C002",
        "kategori": "ada",
    },
    {
        "pertanyaan": "Saya sudah kirim berkas, sekarang statusnya diajukan. Itu artinya apa?",
        "target": "TBL-P004-T001-R005",
        "kategori": "ada",
    },
    {
        "pertanyaan": "ISI SENDIRI: pertanyaan ketiga yang jawabannya ada",
        "target": "ISI-ID-CHUNK",   # lihat Excel hasil simpan_chunk_excel
        "kategori": "ada",
    },
    {
        "pertanyaan": "Resep nasi goreng",
        "target": None,
        "kategori": "tidak ada",
    },
    {
        "pertanyaan": "Apa itu SIUP?",
        "target": None,
        "kategori": "tidak ada",
    },
    {
        "pertanyaan": "Berapa biaya yang harus saya bayar untuk mengurus izin?",
        "target": None,
        "kategori": "perlu diperiksa",
    },
]


def peringkat_target(hasil, target):
    """
    Mencari peringkat chunk target di hasil retrieval.

    INPUT:
        hasil  : List dictionary dari retriever().
        target : chunk_id yang dicari (None bila tidak ada).

    OUTPUT:
        Peringkat (int, mulai 1), atau None bila target
        tidak ada atau tidak ditemukan di hasil.

    Catatan:
        Perbandingan memakai cocok_id() agar ID tanpa awalan
        dokumen (misalnya TXT-P036-C002) tetap dikenali
        walaupun chunk_id sekarang berawalan kode dokumen.
    """
    if target is None:
        return None

    for nomor, chunk in enumerate(hasil, start=1):
        if cocok_id(chunk["chunk_id"], target):
            return nomor

    return None


if __name__ == "__main__":
    collection = buka_collection()
    model = muat_model(NAMA_MODEL_EMBEDDING)

    for nomor, soal in enumerate(SOAL, start=1):
        hasil = retriever(collection, model, soal["pertanyaan"], topk=TOPK)
        peringkat = peringkat_target(hasil, soal["target"])
        jarak_top1 = hasil[0]["distance"]

        print(
            f"{nomor}. [{soal['kategori']}] "
            f"peringkat target: {peringkat if peringkat else '-'} | "
            f"jarak top-1: {jarak_top1:.3f} | {soal['pertanyaan']}"
        )