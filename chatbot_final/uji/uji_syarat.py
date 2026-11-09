# ============================================================
# uji_syarat.py
# Membuktikan (atau membantah) bahwa chatbot gagal menangani
# SYARAT ketika beberapa layanan punya butir yang sama.
#
# Dua tingkat uji:
#   UJI 1 (retrieval, tanpa LLM, gratis) :
#       python uji/uji_syarat.py
#   UJI 2 (jawaban LLM, memakai kuota API):
#       python uji/uji_syarat.py --llm
#
# Skrip ini hanya MENGUKUR. Tidak ada perbaikan di sini.
# Penilaian otomatis bersifat heuristik: baca juga file
# hasil_uji_syarat.txt dan cek jawaban dengan mata sendiri.
# ============================================================

import re
import sys
from pathlib import Path

import _bootstrap  # noqa: F401  (menyiapkan sys.path ke folder chatbotv2)

from scraping.baca_web import baca_halaman_web
from core.config import NAMA_MODEL_EMBEDDING, kode_dokumen, FOLDER_DOKUMEN_WEB
from storage.database import buka_collection
from storage.embedding import muat_model
from retrieval.tetangga import retriever_dengan_tetangga, urutkan_id_chunk_teks

# ------------------------------------------------------------
# DUGAAN KAMU (isi SEBELUM menjalankan, satu-dua kalimat).
# Contoh bentuk: "Pertanyaan X akan gagal di bagian ..., karena ..."
# ------------------------------------------------------------
DUGAAN = ""

# Konfigurasi sama dengan pengujian saat ini di tanya_jawab.py.
TOPK = 10
JUMLAH_CHUNK = 3
JUMLAH_TETANGGA = 1

# Butir dianggap "terwakili" di jawaban bila sedikitnya sekian
# persen kata bermakna dari butir itu muncul di jawaban.
AMBANG_TERWAKILI = 0.7

BASE_DIR = Path(__file__).resolve().parent
FILE_HASIL = BASE_DIR / "hasil_uji_syarat.txt"

FOLDER = Path(FOLDER_DOKUMEN_WEB)
LAYANAN = {
    "bawah_umur": FOLDER / "PM1_PERKAWINAN_BAWAH_UMUR.txt",
    "pertama": FOLDER / "PM1_PERKAWINAN_PERTAMA.txt",
    "rumah": FOLDER / "PM1_KETERANGAN_BELUM_MEMILIKI_RUMAH.txt",
}

# (pertanyaan, layanan yang seharusnya dijawab)
SOAL = [
    ("Apa saja syarat surat pengantar perkawinan di bawah umur?",
     ["bawah_umur"]),
    ("Kalau umur saya belum cukup untuk menikah, berkas apa yang harus disiapkan?",
     ["bawah_umur"]),
    ("Apa saja syarat surat pengantar perkawinan pertama?",
     ["pertama"]),
    ("Saya mau menikah pertama kali, dokumen apa saja yang harus saya siapkan?",
     ["pertama"]),
    ("Apa saja syarat surat keterangan belum memiliki rumah?",
     ["rumah"]),
    ("Saya belum punya rumah dan butuh surat keterangannya, syaratnya apa?",
     ["rumah"]),
    # Ambigu: pengguna tidak menyebut jenis perkawinan.
    ("Apa saja syarat surat pengantar perkawinan?",
     ["bawah_umur", "pertama"]),
]


# ============================================================
# DATA ACUAN (kebenaran dasar diambil dari file .txt, bukan ditulis tangan)
# ============================================================

def muat_acuan():
    """
    Untuk apa : membangun kebenaran dasar tiap layanan dari file asli.
    Input     : tidak ada (memakai LAYANAN di atas).
    Output    : dict nama_layanan -> {
                  "id_syarat": chunk_id SYARAT layanan itu,
                  "butir"    : list teks semua butir syarat,
                  "unik"     : list butir yang TIDAK ada di layanan lain,
                }
    """
    semua = {
        nama: [b["teks"] for b in baca_halaman_web(str(path))["syarat"]]
        for nama, path in LAYANAN.items()
    }

    acuan = {}
    for nama, butir in semua.items():
        lain = set()
        for nama_lain, butir_lain in semua.items():
            if nama_lain != nama:
                lain |= set(butir_lain)

        acuan[nama] = {
            "id_syarat": f"{kode_dokumen(LAYANAN[nama])}-WEB-SYARAT",
            "butir": butir,
            "unik": [b for b in butir if b not in lain],
        }

    return acuan


# ============================================================
# PEMBANTU PENILAIAN
# ============================================================

def kata_bermakna(teks):
    """
    Untuk apa : mengambil kata penting (>= 4 huruf) dari sebuah teks.
    Input     : teks (str).
    Output    : set kata huruf kecil tanpa tanda baca.
    """
    kata = re.findall(r"[a-z0-9]+", teks.lower())
    return {k for k in kata if len(k) >= 4}


def skor_butir(butir, jawaban):
    """
    Untuk apa : mengukur seberapa jauh satu butir muncul di jawaban.
    Input     : butir (str), jawaban (str).
    Output    : float 0..1 (porsi kata bermakna butir yang ada di jawaban).
    """
    kata = kata_bermakna(butir)
    if not kata:
        return 0.0
    return len(kata & kata_bermakna(jawaban)) / len(kata)


def layanan_dari_id(chunk_id, acuan):
    """
    Untuk apa : mengetahui chunk SYARAT milik layanan mana.
    Input     : chunk_id (str), acuan (dict dari muat_acuan).
    Output    : nama layanan, atau None bila bukan chunk SYARAT web.
    """
    for nama, data in acuan.items():
        if chunk_id == data["id_syarat"]:
            return nama
    return None


# ============================================================
# UJI 1: RETRIEVAL
# ============================================================

def uji_retrieval(pertanyaan, dituju, acuan, collection, model, urut):
    """
    Untuk apa : memeriksa chunk SYARAT layanan mana yang masuk konteks.
    Input     : pertanyaan, daftar layanan yang dituju, acuan,
                collection, model, urutan chunk teks.
    Output    : dict hasil:
                  peringkat   : {layanan: peringkat chunk SYARAT di top-k
                                 retriever, atau None bila tidak masuk}
                  jarak       : {layanan: distance, atau None}
                  di_konteks  : layanan yang chunk SYARAT-nya ada di
                                 konteks akhir (termasuk tetangga)
                  salah_masuk : layanan di luar yang dituju yang SYARAT-nya
                                 ikut masuk konteks
                  hilang      : layanan dituju yang SYARAT-nya TIDAK masuk
    """
    hasil = retriever_dengan_tetangga(
        collection, model, pertanyaan, urut,
        topk=TOPK,
        jumlah_chunk=JUMLAH_CHUNK,
        jumlah_tetangga=JUMLAH_TETANGGA,
    )

    peringkat = {nama: None for nama in acuan}
    jarak = {nama: None for nama in acuan}
    di_konteks = set()

    for urutan, chunk in enumerate(hasil, start=1):
        nama = layanan_dari_id(chunk["chunk_id"], acuan)
        if nama is None:
            continue
        di_konteks.add(nama)
        # Peringkat hanya berarti untuk hasil asli retriever (ada distance).
        if chunk["distance"] is not None and peringkat[nama] is None:
            peringkat[nama] = urutan
            jarak[nama] = chunk["distance"]

    return {
        "peringkat": peringkat,
        "jarak": jarak,
        "di_konteks": sorted(di_konteks),
        "salah_masuk": sorted(di_konteks - set(dituju)),
        "hilang": sorted(set(dituju) - di_konteks),
        "id_konteks": [c["chunk_id"] for c in hasil],
    }


# ============================================================
# UJI 2: JAWABAN LLM
# ============================================================

def uji_jawaban(pertanyaan, dituju, acuan, collection, model, urut):
    """
    Untuk apa : menilai isi jawaban LLM terhadap butir syarat asli.
    Input     : pertanyaan, layanan dituju, acuan, collection, model, urut.
    Output    : dict hasil:
                  jawaban     : teks jawaban LLM
                  lengkap     : {layanan dituju: (terwakili, total)} semua butir
                  unik_hilang : butir khas layanan dituju yang tidak muncul
                  kontaminasi : butir khas layanan LAIN yang muncul di jawaban
    """
    from tanya_jawab import jawab

    jawaban, _ = jawab(
        pertanyaan=pertanyaan,
        collection=collection,
        model=model,
        urut=urut,
        topk=TOPK,
        jumlah_chunk=JUMLAH_CHUNK,
        jumlah_tetangga=JUMLAH_TETANGGA,
        debug=False,
    )

    lengkap = {}
    unik_hilang = []
    for nama in dituju:
        butir = acuan[nama]["butir"]
        ada = [b for b in butir if skor_butir(b, jawaban) >= AMBANG_TERWAKILI]
        lengkap[nama] = (len(ada), len(butir))
        for b in acuan[nama]["unik"]:
            if skor_butir(b, jawaban) < AMBANG_TERWAKILI:
                unik_hilang.append(f"{nama}: {b[:70]}")

    kontaminasi = []
    for nama, data in acuan.items():
        if nama in dituju:
            continue
        for b in data["unik"]:
            if skor_butir(b, jawaban) >= AMBANG_TERWAKILI:
                kontaminasi.append(f"{nama}: {b[:70]}")

    return {
        "jawaban": jawaban,
        "lengkap": lengkap,
        "unik_hilang": unik_hilang,
        "kontaminasi": kontaminasi,
    }


# ============================================================
# PROGRAM UTAMA
# ============================================================

def main():
    pakai_llm = "--llm" in sys.argv

    print("DUGAAN:", DUGAAN or "(belum diisi: tulis dulu di variabel DUGAAN)")

    acuan = muat_acuan()
    print("\n=== ACUAN ===")
    for nama, data in acuan.items():
        print(
            f"{nama}: {len(data['butir'])} butir, "
            f"{len(data['unik'])} khas | id: {data['id_syarat']}"
        )

    collection = buka_collection()
    ada = collection.get(ids=[d["id_syarat"] for d in acuan.values()])["ids"]
    if len(ada) != len(acuan):
        print("\nPERINGATAN: chunk SYARAT tidak lengkap di database:", ada)
        print("Periksa format chunk_id (jalankan main.py ulang?).")
        return

    model = muat_model(NAMA_MODEL_EMBEDDING)
    urut = urutkan_id_chunk_teks(collection)

    laporan = []
    gagal_retrieval = 0
    gagal_jawaban = 0

    for pertanyaan, dituju in SOAL:
        r = uji_retrieval(pertanyaan, dituju, acuan, collection, model, urut)

        status = "OK"
        if r["salah_masuk"] or r["hilang"]:
            status = "MASALAH"
            gagal_retrieval += 1

        baris = [
            f"\nPERTANYAAN: {pertanyaan}",
            f"  dituju      : {dituju}",
            f"  peringkat   : {r['peringkat']}",
            f"  jarak       : { {k: (round(v, 3) if v is not None else None) for k, v in r['jarak'].items()} }",
            f"  salah masuk : {r['salah_masuk']}",
            f"  hilang      : {r['hilang']}",
            f"  [UJI 1] {status}",
        ]

        if pakai_llm:
            j = uji_jawaban(pertanyaan, dituju, acuan, collection, model, urut)
            masalah = bool(j["unik_hilang"] or j["kontaminasi"])
            if masalah:
                gagal_jawaban += 1
            baris += [
                f"  butir terwakili : {j['lengkap']}",
                f"  butir khas hilang: {j['unik_hilang']}",
                f"  kontaminasi      : {j['kontaminasi']}",
                f"  [UJI 2] {'MASALAH' if masalah else 'OK'}",
                "  --- jawaban ---",
                j["jawaban"],
            ]

        print("\n".join(baris))
        laporan.append("\n".join(baris))

    ringkas = (
        f"\n=== RINGKASAN ===\n"
        f"UJI 1 (retrieval): {gagal_retrieval} dari {len(SOAL)} soal bermasalah"
    )
    if pakai_llm:
        ringkas += (
            f"\nUJI 2 (jawaban) : {gagal_jawaban} dari {len(SOAL)} soal bermasalah"
        )
    print(ringkas)

    FILE_HASIL.write_text(
        f"DUGAAN: {DUGAAN}\n" + "\n".join(laporan) + ringkas,
        encoding="utf-8",
    )
    print(f"\nHasil lengkap disimpan di {FILE_HASIL}")


if __name__ == "__main__":
    main()
