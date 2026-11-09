# ============================================================
# chunking/chunker.py
# Gerbang Satu Atap (Façade) pemotongan dokumen (PDF & Web).
# ============================================================

from pathlib import Path

from chunking.chunk_pdf import semua_chunk as chunk_pdf_semua
from chunking.chunk_web import susun_chunk_web


def proses_dokumen(path):
    """
    Fungsi cerdas pemotong dokumen:
    - Jika berkas berakhiran .pdf -> dipotong dengan chunk_pdf.
    - Jika berkas berakhiran .txt -> dipotong dengan chunk_web.
    - Selain itu melempar ValueError.

    INPUT:
        path: str atau Path ke file dokumen.

    OUTPUT:
        List objek Chunk.
    """
    path_obj = Path(path)
    ekstensi = path_obj.suffix.lower()

    if ekstensi == ".pdf":
        return chunk_pdf_semua(path_obj)
    elif ekstensi == ".txt":
        return susun_chunk_web(path_obj)
    else:
        raise ValueError(
            f"Format file '{ekstensi}' tidak didukung oleh proses_dokumen. "
            "Gunakan file .pdf atau .txt."
        )


def semua_chunk(path):
    """
    Alias / nama cadangan pemanggil lama untuk mempertahankan kompatibilitas.
    Meneruskan pemanggilan ke proses_dokumen(path).
    """
    return proses_dokumen(path)
