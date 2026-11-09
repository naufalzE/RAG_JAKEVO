# ============================================================
# core/models.py
# Struktur data chunk.
# ============================================================

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class Chunk:
    """
    Menyimpan satu potongan informasi dari dokumen.

    Attributes:
        chunk_id  : Identitas unik chunk.
        teks      : Isi teks chunk.
        page      : Nomor halaman asal chunk (0 untuk chunk web).
        jenis     : Sumber chunk, yaitu teks, tabel, atau web.
        dokumen   : Kode dokumen asal (dari nama file), dipakai
                    sebagai awalan chunk_id.
        nama_file : Nama file asal, dipakai untuk label sumber.
        url       : Alamat halaman sumber layanan. Hanya diisi
                    untuk chunk web; chunk PDF memakai "".
        judul     : Judul layanan pada halaman sumber. Hanya
                    diisi untuk chunk web.
        pasangan  : Daftar dict {"no_butir", "label", "url"}
                    yang memasangkan butir persyaratan dengan
                    tautan templatenya. Hanya diisi untuk chunk
                    web bagian SYARAT, karena di situlah butir
                    persyaratan berada.
    """

    chunk_id: str
    teks: str
    page: int
    jenis: Literal["teks", "tabel", "web"]
    dokumen: str = ""
    nama_file: str = ""
    url: str = ""
    judul: str = ""
    pasangan: list[dict] = field(default_factory=list)
