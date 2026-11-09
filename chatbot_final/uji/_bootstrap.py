# ============================================================
# uji/_bootstrap.py
# Berkas bantuan untuk SEMUA skrip uji di folder uji/.
# ============================================================

import sys
import importlib
from pathlib import Path

FOLDER_UJI = Path(__file__).resolve().parent
FOLDER_PROYEK = FOLDER_UJI.parent

if str(FOLDER_PROYEK) not in sys.path:
    sys.path.insert(0, str(FOLDER_PROYEK))


class _LegacyAliasFinder:
    """
    Lazy finder: mengarahkan impor modul gaya lama (mis. 'from config import ...')
    ke modul baru (mis. 'core.config') hanya saat dibutuhkan, tanpa membebani
    waktu startup dan terlindungi dari rekursi.
    """
    _BUSY = set()
    _MAPPING = {
        "config": "core.config",
        "models": "core.models",
        "utils": "core.utils",
        "database": "storage.database",
        "embedding": "storage.embedding",
        "retriever": "retrieval.retriever",
        "tetangga": "retrieval.tetangga",
        "konteks": "retrieval.konteks",
        "chunker": "chunking.chunker",
        "chunk_pdf": "chunking.chunk_pdf",
        "chunk_teks": "chunking.chunk_teks",
        "chunk_tabel": "chunking.chunk_tabel",
        "chunk_web": "chunking.chunk_web",
        "baca_web": "scraping.baca_web",
        "scraper_layanan": "scraping.scraper_layanan",
        "ambil_satu_layanan": "scraping.scraper_layanan",
        "prompt": "llm.prompt",
        "gemini_llm": "llm.gemini_llm",
        "deepseek_llm": "llm.deepseek_llm",
        "llm_kesalahan": "llm.llm_kesalahan",
    }

    def find_spec(self, fullname, path, target=None):
        if fullname in self._BUSY or fullname not in self._MAPPING:
            return None

        self._BUSY.add(fullname)
        try:
            target_name = self._MAPPING[fullname]
            mod = importlib.import_module(target_name)
            sys.modules[fullname] = mod
            return getattr(mod, "__spec__", None)
        except Exception:
            return None
        finally:
            self._BUSY.discard(fullname)


if not any(isinstance(finder, _LegacyAliasFinder) for finder in sys.meta_path):
    sys.meta_path.insert(0, _LegacyAliasFinder())


def cocok_id(id_chunk, id_target):
    """
    Memeriksa apakah sebuah chunk_id cocok dengan ID target.
    """
    if not id_chunk or not id_target:
        return False

    return (
        id_chunk == id_target
        or id_chunk.endswith("-" + id_target)
    )


def cari_id_nyata(collection, id_target):
    """
    Mencari chunk_id sebenarnya di ChromaDB dari target gaya lama.
    """
    semua_id = collection.get()["ids"]

    return [
        id_chunk
        for id_chunk in semua_id
        if cocok_id(id_chunk, id_target)
    ]


def cari_banyak_id_nyata(collection, daftar_target):
    """
    Versi cari_id_nyata() untuk beberapa target sekaligus.
    """
    hasil = []
    for id_target in daftar_target:
        ditemukan = cari_id_nyata(collection, id_target)
        if not ditemukan:
            print(f"[peringatan] ID target tidak ditemukan: {id_target}")
            continue
        hasil.extend(ditemukan)
    return hasil
