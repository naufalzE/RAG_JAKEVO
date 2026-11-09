# ============================================================
# retrieval/tetangga.py
# Memperluas hasil retriever dengan chunk teks berikutnya
# agar konteks tidak terputus di tengah jalan.
# ============================================================

import re
from retrieval.kamus import CHUNK_IKHTISAR_DATA_PDF
from retrieval.retriever import retriever

POLA_ID_CHUNK = re.compile(
    r"^(?P<dokumen>[A-Z0-9_]+)-TXT-P(?P<halaman>\d+)-C(?P<chunk>\d+)$"
)

POLA_ID_WEB = re.compile(
    r"^(?P<dokumen>[A-Z0-9_]+)-WEB-(?P<bagian>INFO|SYARAT|ALUR|HUKUM)$"
)

URUTAN_BAGIAN_WEB = {
    "INFO": 1,
    "SYARAT": 2,
    "ALUR": 3,
    "HUKUM": 4,
}


def _kunci_urut_chunk(id_chunk):
    """Menghasilkan tuple kunci pengurutan untuk ID chunk teks maupun web."""
    cocok_txt = POLA_ID_CHUNK.match(id_chunk)
    if cocok_txt:
        return (
            0,
            cocok_txt.group("dokumen"),
            int(cocok_txt.group("halaman")),
            int(cocok_txt.group("chunk")),
        )

    cocok_web = POLA_ID_WEB.match(id_chunk)
    if cocok_web:
        return (
            1,
            cocok_web.group("dokumen"),
            0,
            URUTAN_BAGIAN_WEB.get(cocok_web.group("bagian"), 99),
        )

    return None


def _kode_dokumen_chunk(id_chunk):
    """Mengambil kode dokumen dari ID chunk teks atau web."""
    cocok_txt = POLA_ID_CHUNK.match(id_chunk)
    if cocok_txt:
        return cocok_txt.group("dokumen")

    cocok_web = POLA_ID_WEB.match(id_chunk)
    if cocok_web:
        return cocok_web.group("dokumen")

    return None


def urutkan_id_chunk_teks(collection):
    """
    Mengambil ID chunk teks dan web dari ChromaDB dan mengurutkan berdasarkan
    kode dokumen, nomor halaman, serta nomor chunk/bagian.
    """
    data = collection.get(include=["metadatas"])
    daftar_id_chunk = data["ids"]
    daftar_chunk_bernomor = []

    for id_chunk in daftar_id_chunk:
        kunci = _kunci_urut_chunk(id_chunk)
        if kunci is None:
            continue
        daftar_chunk_bernomor.append((kunci, id_chunk))

    daftar_chunk_bernomor.sort(key=lambda item: item[0])
    return [id_chunk for _, id_chunk in daftar_chunk_bernomor]


def kelompokkan_per_dokumen(urut):
    """
    Mengelompokkan ID chunk teks dan web menurut kode dokumen.
    """
    hasil = {}
    for id_chunk in urut:
        kode = _kode_dokumen_chunk(id_chunk)
        if not kode:
            continue
        hasil.setdefault(kode, []).append(id_chunk)

    return hasil


def cari_id_tetangga(
    hasil,
    urut,
    jumlah_chunk=3,
    jumlah_tetangga=2,
):
    """
    Mengambil sampai `jumlah_tetangga` chunk teks berikutnya untuk setiap
    chunk pada `hasil[:jumlah_chunk]`, serta memperluas chunk layanan web
    secara kontekstual (antar-bagian pada layanan tunggal atau lintas layanan
    pada pertanyaan lintas dokumen).
    """
    if jumlah_chunk < 0:
        raise ValueError("jumlah_chunk tidak boleh negatif.")
    if jumlah_tetangga < 0:
        raise ValueError("jumlah_tetangga tidak boleh negatif.")
    if not urut or jumlah_chunk == 0 or jumlah_tetangga == 0:
        return []

    urut_per_dokumen = kelompokkan_per_dokumen(urut)

    posisi_per_id = {}
    for daftar_id in urut_per_dokumen.values():
        for posisi, id_chunk in enumerate(daftar_id):
            posisi_per_id[id_chunk] = (daftar_id, posisi)

    id_awal = {chunk["chunk_id"] for chunk in hasil}
    id_tetangga = set()

    # Analisis distribusi dokumen web di dalam hasil
    hitung_dok_web = {}
    hitung_bagian_web = {}
    for chunk in hasil:
        cocok_web = POLA_ID_WEB.match(chunk["chunk_id"])
        if cocok_web:
            dok_w = cocok_web.group("dokumen")
            bag_w = cocok_web.group("bagian")
            hitung_dok_web[dok_w] = hitung_dok_web.get(dok_w, 0) + 1
            hitung_bagian_web[bag_w] = hitung_bagian_web.get(bag_w, 0) + 1

    # Mode lintas layanan web apabila terdapat >= 3 layanan web berbeda di hasil
    mode_lintas_web = len(hitung_dok_web) >= 3

    if mode_lintas_web and hitung_bagian_web:
        # Ambil bagian web yang paling dominan di hasil teratas
        bagian_utama = max(
            hitung_bagian_web.items(),
            key=lambda item: item[1],
        )[0]
        for kode_dok, daftar_id in urut_per_dokumen.items():
            if not daftar_id or not POLA_ID_WEB.match(daftar_id[0]):
                continue
            id_calon = f"{kode_dok}-WEB-{bagian_utama}"
            if id_calon in posisi_per_id and id_calon not in id_awal:
                id_tetangga.add(id_calon)

    # Tentukan dokumen web yang boleh diperluas antar-bagian (maks 2 layanan fokus)
    dok_web_fokus = set()
    if not mode_lintas_web and hitung_dok_web:
        dok_banyak = {d for d, jml in hitung_dok_web.items() if jml >= 2}
        if dok_banyak:
            dok_web_fokus = dok_banyak
        else:
            for chunk in hasil[:2]:
                cocok_w = POLA_ID_WEB.match(chunk["chunk_id"])
                if cocok_w:
                    dok_web_fokus.add(cocok_w.group("dokumen"))

    # Periksa apakah ini mode ringkasan buku panduan data.pdf
    adalah_ikhtisar_data = all(
        c in id_awal for c in CHUNK_IKHTISAR_DATA_PDF[:3]
    )
    batas_chunk = len(hasil) if adalah_ikhtisar_data else jumlah_chunk

    for chunk in hasil[:batas_chunk]:
        cid = chunk["chunk_id"]
        data_posisi = posisi_per_id.get(cid)
        if data_posisi is None:
            continue

        daftar_id, posisi = data_posisi
        cocok_web = POLA_ID_WEB.match(cid)

        if cocok_web:
            if not mode_lintas_web and cocok_web.group("dokumen") in dok_web_fokus:
                for id_calon in daftar_id:
                    if id_calon not in id_awal:
                        id_tetangga.add(id_calon)
            continue

        for offset in range(1, jumlah_tetangga + 1):
            posisi_tetangga = posisi + offset
            if posisi_tetangga >= len(daftar_id):
                break

            id_calon = daftar_id[posisi_tetangga]
            if id_calon not in id_awal:
                id_tetangga.add(id_calon)

    if adalah_ikhtisar_data:
        for id_ekstra in (
            "DATA-TXT-P023-C001",
            "DATA-TXT-P024-C001",
            "DATA-TXT-P029-C002",
            "DATA-TXT-P033-C001",
        ):
            if id_ekstra in posisi_per_id and id_ekstra not in id_awal:
                id_tetangga.add(id_ekstra)

    return sorted(
        id_tetangga,
        key=lambda id_chunk: (
            posisi_per_id[id_chunk][0][0],
            posisi_per_id[id_chunk][1],
        ),
    )


def ambil_chunk_tetangga(collection, id_tetangga):
    """
    Mengambil teks dan metadata tetangga dari ChromaDB.
    """
    if not id_tetangga:
        return []

    hasil = collection.get(
        ids=id_tetangga,
        include=["documents", "metadatas"],
    )

    data_per_id = {}
    for id_chunk, teks, metadata in zip(
        hasil["ids"], hasil["documents"], hasil["metadatas"]
    ):
        data_per_id[id_chunk] = {
            "chunk_id": id_chunk,
            "teks": teks or "",
            "metadata": metadata or {},
            "distance": None,
        }

    return [
        data_per_id[id_chunk]
        for id_chunk in id_tetangga
        if id_chunk in data_per_id
    ]


def retriever_dengan_tetangga(
    collection,
    model,
    pertanyaan,
    urut,
    topk=5,
    jumlah_chunk=3,
    jumlah_tetangga=2,
):
    """
    Mengambil top-k hasil retrieval, lalu memperluas `jumlah_chunk`
    hasil teratas dengan `jumlah_tetangga` chunk teks berikutnya.
    """
    hasil = retriever(
        collection,
        model,
        pertanyaan,
        topk=topk,
    )

    id_tetangga = cari_id_tetangga(
        hasil,
        urut,
        jumlah_chunk=jumlah_chunk,
        jumlah_tetangga=jumlah_tetangga,
    )

    chunk_tetangga = ambil_chunk_tetangga(
        collection,
        id_tetangga,
    )

    return hasil + chunk_tetangga
