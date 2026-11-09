# ============================================================
# llm/deepseek_llm.py
# Adapter DeepSeek lewat endpoint chat/completions (OpenAI compatible).
# ============================================================

import httpx

from core.config import settings
from llm.llm_kesalahan import KesalahanLLM, KesalahanPermanen


def panggil_deepseek(prompt: str) -> str:
    """Mengirim prompt ke DeepSeek lewat endpoint chat/completions."""
    kunci = settings.kunci_aktif()

    if not kunci:
        raise KesalahanPermanen(
            "DEEPSEEK_API_KEY (atau LLM_API_KEY) belum diisi di chatbotv2/.env"
        )

    url = (
        settings.DEEPSEEK_BASE_URL.rstrip("/")
        + "/chat/completions"
    )

    payload = {
        "model": settings.model_aktif(),
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "stream": False,
    }

    headers = {
        "Authorization": f"Bearer {kunci}",
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(
            timeout=settings.LLM_TIMEOUT
        ) as client:
            respons = client.post(url, json=payload, headers=headers)

    except httpx.TimeoutException as error:
        raise KesalahanLLM(
            "DeepSeek tidak merespons dalam "
            f"{settings.LLM_TIMEOUT} detik."
        ) from error

    except httpx.HTTPError as error:
        raise KesalahanLLM(
            f"Koneksi ke DeepSeek gagal: {error}"
        ) from error

    if respons.status_code in (401, 402, 403, 404, 422):
        raise KesalahanPermanen(
            f"DeepSeek menolak permintaan "
            f"(kode {respons.status_code}): {respons.text[:300]}"
        )

    if respons.status_code >= 400:
        raise KesalahanLLM(
            f"DeepSeek gagal (kode {respons.status_code}): "
            f"{respons.text[:300]}"
        )

    try:
        teks = respons.json()["choices"][0]["message"]["content"]

    except (KeyError, IndexError, TypeError, ValueError) as error:
        raise KesalahanLLM(
            "Format jawaban DeepSeek tidak dikenali: "
            f"{respons.text[:300]}"
        ) from error

    teks = (teks or "").strip()

    if not teks:
        raise KesalahanLLM("DeepSeek mengembalikan jawaban kosong.")

    return teks
