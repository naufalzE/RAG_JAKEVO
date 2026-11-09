# ============================================================
# tanya_jawab.py
# Pipeline: pertanyaan -> retriever + tetangga -> prompt -> LLM
# ============================================================

import sys
from pathlib import Path

# Pastikan chatbotv2 ada di sys.path saat dijalankan langsung
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from llm.llm import info_llm, panggil_llm
from retrieval.tetangga import (
    retriever_dengan_tetangga,
    urutkan_id_chunk_teks,
)
from retrieval.konteks import format_sumber, susun_konteks
from llm.prompt import bangun_prompt
from core.config import (
    PESAN_GAGAL,
    PREFIKS_TIDAK_ADA,
)
from core.guardrail import guardrail_default

__all__ = [
    "susun_konteks",
    "format_sumber",
    "bangun_prompt",
    "jawab",
]


def jawab(
    pertanyaan,
    collection,
    model,
    urut,
    topk=5,
    jumlah_chunk=3,
    jumlah_tetangga=2,
    debug=False,
):
    """
    Alur:
    1. Mengambil chunk relevan.
    2. Memperluas hasil dengan chunk tetangga.
    3. Menyusun konteks.
    4. Membangun prompt.
    5. Memanggil LLM.
    6. Mengembalikan jawaban dan sumber.

    Parameter:
        pertanyaan:
            Pertanyaan pengguna.
        collection:
            Collection ChromaDB.
        model:
            Model embedding untuk retriever.
        urut:
            ID chunk teks yang sudah diurutkan berdasarkan
            urutan dokumen.
        topk:
            Jumlah hasil pencarian semantik utama.
        jumlah_chunk:
            Banyak hasil retrieval teratas yang diperluas.
        jumlah_tetangga:
            Jumlah chunk berikutnya untuk setiap hasil terpilih.
        debug:
            Bila True, konteks yang dikirim ke LLM dicetak ke terminal.

    Return:
        Tuple (jawaban, sumber).
    """

    # 0. INPUT GUARDRAIL
    cek_input = guardrail_default.periksa_input(pertanyaan)
    if not cek_input.lolos:
        if debug:
            print(f"\n[GUARDRAIL DITOLAK] Alasan: {cek_input.alasan}")
        return cek_input.pesan_penolakan, []

    # 1. RETRIEVAL + TETANGGA
    hasil = retriever_dengan_tetangga(
        collection=collection,
        model=model,
        pertanyaan=pertanyaan,
        urut=urut,
        topk=topk,
        jumlah_chunk=jumlah_chunk,
        jumlah_tetangga=jumlah_tetangga,
    )

    # 2. SUSUN KONTEKS
    konteks = susun_konteks(hasil)

    if debug:
        print("\n=== DEBUG KONTEKS ===")
        print(konteks)

    # 3. BANGUN PROMPT
    prompt_llm = bangun_prompt(
        pertanyaan=pertanyaan,
        konteks=konteks,
    )

    if debug:
        print("\nSedang memproses jawaban dengan LLM...", flush=True)

    # 4. PANGGIL LLM
    jawaban_llm = panggil_llm(prompt_llm)

    # 5. PERIKSA HASIL
    if jawaban_llm is None:
        return PESAN_GAGAL, []

    jawaban_llm = str(jawaban_llm).strip()

    if not jawaban_llm:
        return PESAN_GAGAL, []

    if jawaban_llm.startswith(PREFIKS_TIDAK_ADA):
        return jawaban_llm, []

    # 6. OUTPUT GUARDRAIL (Sanitasi & Format)
    jawaban_llm = guardrail_default.periksa_output(jawaban_llm)

    return jawaban_llm, hasil


if __name__ == "__main__":
    from storage.database import buka_collection
    from storage.embedding import muat_model

    collection = buka_collection()
    model = muat_model()
    urut = urutkan_id_chunk_teks(collection)

    print("LLM aktif:", info_llm())
    print("Chatbot JAKEVO. Ketik 'keluar' untuk berhenti.")

    while True:
        pertanyaan = input("\nPertanyaan: ").strip()

        if not pertanyaan:
            continue

        if pertanyaan.lower() in {"keluar", "exit", "quit"}:
            break

        jawaban_llm, sumber = jawab(
            pertanyaan=pertanyaan,
            collection=collection,
            model=model,
            urut=urut,
            topk=10,
            jumlah_chunk=3,
            jumlah_tetangga=1,
            debug=True,
        )

        print("\nJawaban:")
        print(jawaban_llm)

        print(
            "\nSumber:",
            format_sumber(sumber) or "tidak ada",
        )
