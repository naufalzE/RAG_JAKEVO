# ============================================================
# storage/database.py
# Koneksi ChromaDB dan penyimpanan chunk beserta embedding.
# ============================================================

import json
import chromadb

from core.config import NAMA_COLLECTION, PATH_CHROMA


def _metadata_chunk(chunk):
    """
    Menyusun metadata satu chunk untuk ChromaDB.
    ChromaDB hanya menerima nilai metadata berupa str, int, float, atau bool.
    """
    return {
        "page": int(chunk.page),
        "jenis": chunk.jenis,
        "dokumen": chunk.dokumen or "",
        "nama_file": chunk.nama_file or "",
        "url": chunk.url or "",
        "judul": chunk.judul or "",
        "pasangan": json.dumps(
            chunk.pasangan or [],
            ensure_ascii=False,
        ),
    }


def buka_collection():
    """Membuka database ChromaDB dan membuat/mengambil collection."""
    client = chromadb.PersistentClient(path=PATH_CHROMA)

    return client.get_or_create_collection(
        name=NAMA_COLLECTION,
        metadata={"hnsw:space": "cosine"}
    )


def simpan_ke_chroma(collection, chunks, vektor):
    """
    Menyimpan ID, teks, embedding, dan metadata setiap chunk
    ke ChromaDB dengan upsert.
    """
    collection.upsert(
        ids=[chunk.chunk_id for chunk in chunks],
        documents=[chunk.teks for chunk in chunks],
        embeddings=vektor.tolist(),
        metadatas=[
            _metadata_chunk(chunk)
            for chunk in chunks
        ]
    )


def cari_id_basi(collection, chunks):
    """
    Mencari ID yang masih tersimpan di ChromaDB tetapi sudah tidak
    ada pada daftar chunk terbaru.
    """
    id_tersimpan = set(collection.get()["ids"])
    id_terbaru = {chunk.chunk_id for chunk in chunks}

    return sorted(id_tersimpan - id_terbaru)


def hapus_id_basi(collection, id_basi):
    """
    Menghapus ID basi dari collection ChromaDB.
    """
    if isinstance(id_basi, str):
        raise TypeError(
            "id_basi harus berupa list atau set ID, bukan string tunggal."
        )

    id_basi = list(id_basi)

    if not id_basi:
        return 0

    collection.delete(ids=id_basi)
    return len(id_basi)
