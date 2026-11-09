# ============================================================
# llm/llm_kesalahan.py
# Definisi kelas pengecualian (exception) pemanggilan LLM.
# ============================================================


class KesalahanLLM(Exception):
    """Galat sementara saat memanggil LLM (layak dicoba ulang)."""
    pass


class KesalahanPermanen(Exception):
    """Galat fatal saat memanggil LLM (tidak perlu dicoba ulang)."""
    pass
