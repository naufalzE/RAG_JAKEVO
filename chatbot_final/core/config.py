# ============================================================
# core/config.py
# Ruang kendali sentral konfigurasi aplikasi.
# ============================================================

import re
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory menunjuk ke folder chatbotv2
BASE_DIR = Path(__file__).resolve().parent.parent

PROVIDER_DIDUKUNG = ("gemini", "deepseek", "mimo")


class Settings(BaseSettings):
    # --------------------------------------------------------
    # Pemilihan penyedia LLM.
    # Di .env cukup tulis: LLM_PROVIDER=gemini  atau  deepseek
    # --------------------------------------------------------
    LLM_PROVIDER: str = Field(
        default="gemini",
        validation_alias=AliasChoices("LLM_PROVIDER", "PROVIDER_LLM"),
    )

    # Kunci API per penyedia
    GEMINI_API_KEY: str | None = Field(
        default=None,
        validation_alias=AliasChoices("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    )
    DEEPSEEK_API_KEY: str | None = Field(
        default=None,
        validation_alias=AliasChoices("DEEPSEEK_API_KEY"),
    )
    MIMO_API_KEY: str | None = Field(
        default=None,
        validation_alias=AliasChoices("MIMO_API_KEY"),
    )
    # Cadangan bila kunci khusus penyedia belum diisi
    LLM_API_KEY: str | None = Field(
        default=None,
        validation_alias=AliasChoices("LLM_API_KEY"),
    )

    # Model per penyedia
    GEMINI_MODEL: str = Field(
        default="gemini-3.8-flash",
        validation_alias=AliasChoices("GEMINI_MODEL", "NAMA_MODEL_LLM"),
    )
    DEEPSEEK_MODEL: str = Field(
        default="deepseek-chat",
        validation_alias=AliasChoices("DEEPSEEK_MODEL"),
    )
    DEEPSEEK_BASE_URL: str = Field(
        default="https://api.deepseek.com",
        validation_alias=AliasChoices(
            "DEEPSEEK_BASE_URL", "DEEPSEEK_API_BASE"
        ),
    )
    MIMO_MODEL: str = Field(
        default="mimo-v1",
        validation_alias=AliasChoices("MIMO_MODEL"),
    )
    MIMO_BASE_URL: str = Field(
        default="https://token-plan-sgp.xiaomimimo.com/v1",
        validation_alias=AliasChoices(
            "MIMO_BASE_URL", "MIMO_API_BASE"
        ),
    )
    # Batas waktu satu panggilan LLM, dalam detik.
    LLM_TIMEOUT: int = Field(
        default=60,
        validation_alias=AliasChoices("LLM_TIMEOUT", "LLM_TIMEOUT_DETIK"),
    )

    NAMA_MODEL_EMBEDDING: str = Field(
        default="intfloat/multilingual-e5-small",
        validation_alias=AliasChoices("EMBEDDING_MODEL", "NAMA_MODEL_EMBEDDING"),
    )
    # Folder tempat dokumen PDF sumber disimpan.
    FOLDER_DOKUMEN: str = Field(
        default=str(BASE_DIR / "dokumen"),
        validation_alias=AliasChoices("FOLDER_DOKUMEN"),
    )
    # Folder teks layanan hasil scraping web (*.txt), terpisah dari PDF.
    FOLDER_DOKUMEN_WEB: str = Field(
        default=str(BASE_DIR / "dokumen_web"),
        validation_alias=AliasChoices("FOLDER_DOKUMEN_WEB"),
    )
    # Folder arsip: JSON mentah dan percobaan scraping lama.
    FOLDER_ARSIP_SCRAPING: str = Field(
        default=str(BASE_DIR / "arsip_scraping"),
        validation_alias=AliasChoices("FOLDER_ARSIP_SCRAPING"),
    )
    PATH_CHROMA: str = Field(
        default=str(BASE_DIR / "chroma_db"),
        validation_alias=AliasChoices("VECTOR_DB_PATH", "PATH_CHROMA"),
    )
    NAMA_COLLECTION: str = "akevo"
    MAKS_KARAKTER_CHUNK: int = 500
    AWALAN_CHUNK_TABEL: str = "Informasi status proses permohonan izin JAKEVO."
    NAMA_DOKUMEN: str = "Petunjuk Penggunaan JAKEVO untuk Pemohon"
    PESAN_GAGAL: str = "Maaf, layanan jawaban sedang bermasalah. Silakan coba lagi sebentar lagi."
    PREFIKS_TIDAK_ADA: str = "Maaf, saya tidak menemukan informasi tersebut"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",   # selalu chatbotv2/.env, apa pun CWD-nya
        env_file_encoding="utf-8",
        extra="ignore",               # APP_NAMA/TIMEOUT tidak bikin error
    )

    @property
    def penyedia(self) -> str:
        """Nama penyedia LLM yang aktif, sudah dinormalisasi."""
        return self.LLM_PROVIDER.strip().lower()

    def model_aktif(self) -> str:
        """Nama model milik penyedia yang sedang dipakai."""
        penyedia = self.penyedia

        if penyedia == "gemini":
            return self.GEMINI_MODEL
        if penyedia == "deepseek":
            return self.DEEPSEEK_MODEL
        if penyedia == "mimo":
            return self.MIMO_MODEL

        raise ValueError(
            f"LLM_PROVIDER '{self.LLM_PROVIDER}' tidak dikenal. "
            f"Pilih salah satu: {', '.join(PROVIDER_DIDUKUNG)}."
        )

    def kunci_aktif(self) -> str | None:
        """Kunci API penyedia aktif, dengan LLM_API_KEY sebagai cadangan."""
        if self.penyedia == "deepseek":
            return self.DEEPSEEK_API_KEY or self.LLM_API_KEY
        if self.penyedia == "mimo":
            return self.MIMO_API_KEY or self.LLM_API_KEY
        return self.GEMINI_API_KEY or self.LLM_API_KEY


settings = Settings()


def _model_aktif_aman() -> str:
    """Nilai NAMA_MODEL_LLM tanpa menggagalkan import bila provider salah."""
    try:
        return settings.model_aktif()
    except ValueError:
        return settings.GEMINI_MODEL


# Export level modul supaya `from core.config import X` tetap mudah diakses
NAMA_MODEL_LLM = _model_aktif_aman()
NAMA_MODEL_EMBEDDING = settings.NAMA_MODEL_EMBEDDING
LLM_PROVIDER = settings.penyedia
LLM_TIMEOUT = settings.LLM_TIMEOUT
GEMINI_API_KEY = settings.GEMINI_API_KEY
DEEPSEEK_API_KEY = settings.DEEPSEEK_API_KEY
MIMO_API_KEY = settings.MIMO_API_KEY
MIMO_MODEL = settings.MIMO_MODEL
MIMO_BASE_URL = settings.MIMO_BASE_URL
LLM_API_KEY = settings.kunci_aktif()
PATH_CHROMA = settings.PATH_CHROMA
NAMA_COLLECTION = settings.NAMA_COLLECTION
MAKS_KARAKTER_CHUNK = settings.MAKS_KARAKTER_CHUNK
AWALAN_CHUNK_TABEL = settings.AWALAN_CHUNK_TABEL
NAMA_DOKUMEN = settings.NAMA_DOKUMEN
PESAN_GAGAL = settings.PESAN_GAGAL
PREFIKS_TIDAK_ADA = settings.PREFIKS_TIDAK_ADA

FOLDER_DOKUMEN = settings.FOLDER_DOKUMEN
FOLDER_DOKUMEN_WEB = settings.FOLDER_DOKUMEN_WEB
FOLDER_ARSIP_SCRAPING = settings.FOLDER_ARSIP_SCRAPING


def kode_dokumen(path) -> str:
    """
    Membuat kode dokumen dari nama file PDF atau web.

    Contoh:
        data.pdf                 -> DATA
        Petunjuk JAKEVO 2024.pdf -> PETUNJUK_JAKEVO_2024
    """
    nama = Path(path).stem.upper()
    kode = re.sub(r"[^A-Z0-9]+", "_", nama).strip("_")
    return kode or "DOKUMEN"


def daftar_file_pdf(folder=None) -> list[Path]:
    """Mengambil seluruh file PDF di folder dokumen, terurut menurut nama."""
    folder = Path(folder or FOLDER_DOKUMEN)
    if not folder.is_dir():
        return []
    return sorted(folder.glob("*.pdf"))


def daftar_file_web(folder=None) -> list[Path]:
    """Mengambil seluruh berkas .txt layanan di folder dokumen web."""
    folder = Path(folder or FOLDER_DOKUMEN_WEB)
    if not folder.is_dir():
        return []
    return sorted(folder.glob("*.txt"))
