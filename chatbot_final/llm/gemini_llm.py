# ============================================================
# llm/gemini_llm.py
# Adapter Google Gemini memakai SDK google-genai.
# ============================================================

from google import genai
from google.genai import errors as genai_errors

from core.config import settings
from llm.llm_kesalahan import KesalahanLLM, KesalahanPermanen

MILIDETIK = 1000


def panggil_gemini(prompt: str) -> str:
    """Mengirim prompt ke Gemini memakai generate_content."""
    kunci = settings.kunci_aktif()

    if not kunci:
        raise KesalahanPermanen(
            "GEMINI_API_KEY (atau LLM_API_KEY) belum diisi di chatbotv2/.env"
        )

    client = genai.Client(
        api_key=kunci,
        http_options={
            "timeout": settings.LLM_TIMEOUT * MILIDETIK,
        },
    )

    try:
        hasil = client.models.generate_content(
            model=settings.model_aktif(),
            contents=prompt,
            config={
                "temperature": 0.1,
            },
        )

    except genai_errors.ClientError as error:
        kode = getattr(error, "code", None)

        if kode in (400, 401, 403, 404):
            raise KesalahanPermanen(
                f"Gemini menolak permintaan (kode {kode}): {error}"
            ) from error

        raise KesalahanLLM(
            f"Gemini gagal (kode {kode}): {error}"
        ) from error

    except genai_errors.ServerError as error:
        raise KesalahanLLM(
            f"Gemini gagal di sisi server: {error}"
        ) from error

    except Exception as error:
        raise KesalahanLLM(f"Gemini gagal: {error}") from error

    teks = (getattr(hasil, "text", None) or "").strip()

    if not teks:
        raise KesalahanLLM("Gemini mengembalikan jawaban kosong.")

    return teks
