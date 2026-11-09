# ============================================================
# core/utils.py
# Validasi chunk dan ekspor ke Excel.
# ============================================================

from collections import Counter
import pandas as pd


def cek_keunikan_id(chunks):
    """
    Memeriksa apakah ada chunk_id yang berulang.

    OUTPUT:
        True jika semua ID unik, False jika ada duplikat.
    """
    hitung_id = Counter(chunk.chunk_id for chunk in chunks)

    duplikat = [
        chunk_id
        for chunk_id, jumlah in hitung_id.items()
        if jumlah > 1
    ]

    if duplikat:
        print("ID duplikat ditemukan:", duplikat)
        return False

    print("Semua chunk_id unik.")
    return True


def simpan_chunk_excel(chunks, nama_file="hasil_semua_chunk.xlsx"):
    """
    Menyimpan seluruh chunk (ID, halaman, jenis, teks) ke file Excel.

    OUTPUT:
        DataFrame yang disimpan.
    """
    data = [
        {
            "chunk_id": chunk.chunk_id,
            "page": chunk.page,
            "jenis": chunk.jenis,
            "teks": chunk.teks
        }
        for chunk in chunks
    ]

    df = pd.DataFrame(
        data,
        columns=["chunk_id", "page", "jenis", "teks"]
    )

    df.to_excel(nama_file, index=False, sheet_name="Semua Chunk")

    print(f"File Excel berhasil disimpan: {nama_file}")
    print(f"Jumlah baris data: {len(df)}")

    return df
