# ============================================================
# storage/embedding.py
# Memuat model embedding dan membuat vektor dari chunk.
# ============================================================

from sentence_transformers import SentenceTransformer

from core.config import NAMA_MODEL_EMBEDDING


def muat_model(nama_model=NAMA_MODEL_EMBEDDING):
    """Memuat model SentenceTransformer."""
    return SentenceTransformer(nama_model)


def buat_embedding(chunks, model):
    """
    Mengubah teks seluruh chunk menjadi vektor dalam satu panggilan encode.

    OUTPUT:
        Array berbentuk (jumlah_chunk, dimensi_vektor).
        Baris ke-i adalah vektor milik chunks[i].
    """
    daftar_teks = [
        "passage: " + chunk.teks
        for chunk in chunks
    ]

    return model.encode(daftar_teks, normalize_embeddings=True)
