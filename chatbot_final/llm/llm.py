# ============================================================
# llm/llm.py
# Satu pintu pemanggilan LLM (Facade).
# ============================================================

import time

from core.config import settings, PROVIDER_DIDUKUNG
from llm.llm_kesalahan import KesalahanLLM, KesalahanPermanen

__all__ = [
    "KesalahanLLM",
    "KesalahanPermanen",
    "info_llm",
    "panggil_llm",
]


def info_llm() -> str:
    """Ringkasan penyedia dan model aktif, untuk log."""
    try:
        return f"{settings.penyedia} / {settings.model_aktif()}"
    except ValueError as error:
        return str(error)


def _panggil_gemini(prompt: str) -> str:
    """Membungkus adapter Gemini."""
    from llm.gemini_llm import panggil_gemini
    return panggil_gemini(prompt)


def _panggil_deepseek(prompt: str) -> str:
    """Membungkus adapter DeepSeek."""
    from llm.deepseek_llm import panggil_deepseek
    return panggil_deepseek(prompt)


def _panggil_mimo(prompt: str) -> str:
    """Membungkus adapter MiMO."""
    from llm.mimo_llm import panggil_mimo
    return panggil_mimo(prompt)


def panggil_llm(prompt, maks_percobaan=3, jeda_detik=2):
    """
    Mengirim prompt ke penyedia LLM yang dipilih di .env.

    INPUT:
        prompt        : String prompt dari bangun_prompt.
        maks_percobaan: Jumlah maksimal percobaan untuk error sementara.
        jeda_detik    : Jeda dasar antar percobaan, dalam detik.

    OUTPUT:
        String jawaban, atau None jika gagal.
    """
    try:
        penyedia = settings.penyedia
        settings.model_aktif()
    except ValueError as error:
        print(f"[LLM] {error}")
        return None

    if penyedia == "deepseek":
        fungsi = _panggil_deepseek
    elif penyedia == "gemini":
        fungsi = _panggil_gemini
    elif penyedia == "mimo":
        fungsi = _panggil_mimo
    else:
        print(
            f"[LLM] LLM_PROVIDER '{penyedia}' tidak dikenal. "
            f"Pilih: {', '.join(PROVIDER_DIDUKUNG)}."
        )
        return None

    for percobaan in range(1, maks_percobaan + 1):
        try:
            return fungsi(prompt)

        except KesalahanPermanen as error:
            print(f"[LLM] {penyedia} gagal permanen: {error}")
            return None

        except KesalahanLLM as error:
            print(f"[LLM] Percobaan {percobaan} gagal: {error}")
            if percobaan < maks_percobaan:
                time.sleep(jeda_detik * percobaan)

    return None


if __name__ == "__main__":
    print("Penyedia/model :", info_llm())
    print("Batas waktu    :", settings.LLM_TIMEOUT, "detik")
    print("Kunci terbaca  :", bool(settings.kunci_aktif()))

    mulai = time.time()
    jawaban = panggil_llm("Balas satu kata: OK")
    durasi = time.time() - mulai

    print(f"Durasi         : {durasi:.1f} detik")
    print("Jawaban        :", jawaban if jawaban else "(gagal)")
