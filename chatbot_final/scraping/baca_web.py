# ============================================================
# scraping/baca_web.py
# Membaca satu file .txt layanan (hasil scraping) dan memecahnya
# menjadi bagian terstruktur.
#
# INPUT:
#   dokumen_web/<KODE>.txt
#
# OUTPUT (dict dengan 10 kunci):
#   judul         : judul halaman
#   url           : URL sumber
#   tanggal_ambil : waktu pengambilan (UTC)
#   info          : dict {label: nilai} dari blok atas halaman
#   syarat        : list {"no", "teks", "template"}
#                   "template" bernilai True bila butir itu
#                   bertanda "Template Unduh Disini".
#   alur          : list {"no", "tahap", "pelaksana", "uraian"}
#   hukum         : list {"jenis", "status", "berlaku", "nama"}
#   tautan        : list {"label", "url"}
#   pasangan      : list {"no_butir", "label", "url"} hasil
#                   pasangkan_tautan(data).
#   peringatan    : list catatan masalah yang ditemukan. List
#                   kosong berarti hasil bacaan bersih.
# ============================================================

import re
import sys
from pathlib import Path
from urllib.parse import unquote


class BerkasWebTidakValid(ValueError):
    """
    Berkas layanan ditolak karena strukturnya tidak sesuai.
    """


# Penanda bagian
PENANDA_ISI = "=== ISI HALAMAN ==="
PENANDA_SYARAT = "Persyaratan"
PENANDA_ALUR = "Alur Proses"
PENANDA_HUKUM = "Dasar Hukum"
PENANDA_TAUTAN = "=== TAUTAN LAMPIRAN / TEMPLATE ==="

PENANDA_WAJIB = (
    PENANDA_SYARAT,
    PENANDA_ALUR,
    PENANDA_HUKUM,
)

MIN_BUTIR_SYARAT = 2
MIN_LANGKAH_ALUR = 1

LABEL_INFO = (
    "Tipe Perizinan",
    "Tipe Pengajuan",
    "Estimasi Waktu Pelayanan",
    "Biaya Retribusi",
)

BARIS_DILEWATI = {
    "Masuk",
    "Ajukan Permohonan",
    "Konsultasi"
}

PENANDA_TEMPLATE = (
    "template unduh disini",
    "download disini",
    "unduh disini",
    "template unduh",
    "download template",
    "unduh template",
)

POLA_JUMLAH_REGULASI = re.compile(
    r"^(\d+)\s+regulasi$", re.IGNORECASE
)

POLA_NOMOR_TAUTAN = re.compile(r"^\d+\.\s*(.*)$")

POLA_NAMA_HASH = re.compile(r"^[0-9a-f]{16,}$", re.IGNORECASE)

PANJANG_LABEL = 60


def _cari_baris(baris, penanda, mulai=0):
    """Mencari indeks baris yang PERSIS sama dengan penanda."""
    target = penanda.casefold()
    for i in range(max(mulai, 0), len(baris)):
        if baris[i].casefold() == target:
            return i
    return -1


def _potong(baris, awal, akhir):
    """Mengambil isi bagian di antara dua penanda."""
    if awal < 0:
        return []
    if akhir < 0:
        akhir = len(baris)
    return baris[awal + 1:akhir]


def _nomor_baru(teks, nomor_terakhir, satuan, peringatan):
    """Memutuskan apakah baris angka membuka butir/langkah baru."""
    if not teks.isdigit():
        return None

    angka = int(teks)

    if nomor_terakhir is None:
        if angka == 1:
            return angka

        peringatan.append(
            f"angka {angka} muncul sebelum {satuan} pertama; "
            f"dianggap bagian isi, bukan nomor {satuan}."
        )
        return None

    if angka == nomor_terakhir + 1:
        return angka

    peringatan.append(
        f"angka {angka} setelah {satuan} {nomor_terakhir} tidak "
        f"berurutan; dianggap bagian isi {satuan} {nomor_terakhir}."
    )
    return None


def _nilai_header(baris, awalan):
    """Mengambil nilai baris header seperti 'JUDUL: ...'."""
    for teks in baris:
        if teks.upper().startswith(awalan):
            return teks[len(awalan):].strip()
    return ""


def _parse_info(baris):
    """Membaca blok informasi di atas halaman."""
    info = {}
    for i, teks in enumerate(baris):
        if teks not in LABEL_INFO:
            continue

        if teks in ("Tipe Perizinan", "Tipe Pengajuan"):
            j = i + 1
            nilai = []
            while (
                j < len(baris)
                and baris[j] not in LABEL_INFO
                and baris[j] not in ("Persyaratan", "Alur Proses")
            ):
                item = baris[j].strip()
                if item and not item.casefold().startswith("pilih "):
                    nilai.append(item)
                j += 1
            if nilai:
                info[teks] = ", ".join(nilai)
        else:
            j = i + 1
            while j < len(baris) and (
                not baris[j] or baris[j].casefold().startswith("pilih ")
            ):
                j += 1
            if j < len(baris):
                info[teks] = baris[j]

    return info


def _parse_syarat(baris, peringatan):
    """Membaca daftar persyaratan."""
    syarat = []
    nomor = None
    kumpulan = []
    ada_template = False

    def simpan():
        if nomor is None:
            return

        if not kumpulan:
            peringatan.append(
                f"butir {nomor} tidak berisi teks; butir dilewati."
            )
            return

        syarat.append({
            "no": nomor,
            "teks": " ".join(kumpulan),
            "template": ada_template,
        })

    for teks in baris:
        if not teks or teks in BARIS_DILEWATI:
            continue

        if teks.casefold() in PENANDA_TEMPLATE:
            if nomor is not None:
                ada_template = True
            continue

        baru = _nomor_baru(teks, nomor, "butir", peringatan)

        if baru is not None:
            simpan()

            if nomor is None and kumpulan:
                peringatan.append(
                    f"{len(kumpulan)} baris sebelum butir pertama diabaikan."
                )

            nomor = baru
            kumpulan = []
            ada_template = False
            continue

        kumpulan.append(teks)

    simpan()
    return syarat


def _parse_alur(baris, peringatan):
    """Membaca alur proses."""
    alur = []
    nomor = None
    kumpulan = []

    def simpan():
        if nomor is None:
            return

        if not kumpulan:
            peringatan.append(
                f"langkah {nomor} tidak berisi teks; langkah dilewati."
            )
            return

        langkah = {
            "no": nomor,
            "tahap": kumpulan[0],
            "pelaksana": "",
            "uraian": "",
        }

        if len(kumpulan) >= 3:
            langkah["pelaksana"] = kumpulan[1]
            langkah["uraian"] = " ".join(kumpulan[2:])
        elif len(kumpulan) == 2:
            langkah["uraian"] = kumpulan[1]

        alur.append(langkah)

    for teks in baris:
        if not teks or teks in BARIS_DILEWATI:
            continue

        baru = _nomor_baru(teks, nomor, "langkah", peringatan)

        if baru is not None:
            simpan()

            if nomor is None and kumpulan:
                peringatan.append(
                    f"{len(kumpulan)} baris sebelum langkah pertama diabaikan."
                )

            nomor = baru
            kumpulan = []
            continue

        kumpulan.append(teks)

    simpan()
    return alur


def _parse_hukum(baris):
    """Membaca dasar hukum."""
    regulasi = []
    isi = [
        teks
        for teks in baris
        if teks
        and teks not in BARIS_DILEWATI
        and not POLA_JUMLAH_REGULASI.match(teks)
    ]

    i = 0
    while i + 3 < len(isi):
        if isi[i + 2].casefold().startswith("berlaku"):
            regulasi.append({
                "jenis": isi[i],
                "status": isi[i + 1],
                "berlaku": isi[i + 2][len("Berlaku"):].strip(),
                "nama": isi[i + 3],
            })
            i += 4
        else:
            i += 1

    return regulasi


def _klaim_jumlah_regulasi(baris):
    """Mengambil angka dari baris 'N regulasi'."""
    for teks in baris:
        cocok = POLA_JUMLAH_REGULASI.match(teks)
        if cocok:
            return int(cocok.group(1))
    return None


def _parse_tautan(baris):
    """Membaca tautan lampiran/template."""
    tautan = []
    label = ""

    for teks in baris:
        if not teks:
            continue

        cocok = POLA_NOMOR_TAUTAN.match(teks)
        if cocok:
            label = cocok.group(1).strip()
            continue

        if teks.casefold().startswith(("http://", "https://")):
            tautan.append({"label": label, "url": teks})
            label = ""
            continue

    return tautan


def _pastikan_penanda(indeks, penanda, path):
    if indeks >= 0:
        return

    raise BerkasWebTidakValid(
        f"{path.name}: penanda bagian '{penanda}' tidak ditemukan. "
        "Berkas ditolak karena struktur halaman berubah."
    )


def _pastikan_isi(data, path, potong_hukum):
    jumlah_syarat = len(data["syarat"])
    jumlah_alur = len(data["alur"])

    if jumlah_syarat < MIN_BUTIR_SYARAT:
        raise BerkasWebTidakValid(
            f"{path.name}: hanya {jumlah_syarat} butir persyaratan "
            f"terbaca (minimal {MIN_BUTIR_SYARAT}). "
            "Periksa format nomor butir pada berkas."
        )

    if jumlah_alur < MIN_LANGKAH_ALUR:
        raise BerkasWebTidakValid(
            f"{path.name}: tidak ada langkah alur yang terbaca "
            f"(minimal {MIN_LANGKAH_ALUR})."
        )

    klaim = _klaim_jumlah_regulasi(potong_hukum)

    if klaim is not None and klaim != len(data["hukum"]):
        raise BerkasWebTidakValid(
            f"{path.name}: baris jumlah regulasi menyebut {klaim}, "
            f"tetapi {len(data['hukum'])} regulasi berhasil dibaca."
        )


def _label_dari_url(url):
    """Membuat label dari nama berkas pada URL."""
    nama = str(url or "").strip()
    nama = nama.split("?", 1)[0].split("#", 1)[0]
    nama = nama.rsplit("/", 1)[-1]
    nama = unquote(nama)
    nama = Path(nama).stem
    nama = nama.replace("_", " ").strip()

    if nama and not POLA_NAMA_HASH.match(nama.replace(" ", "")):
        return nama

    return ""


def _potong_teks(teks, batas=PANJANG_LABEL):
    """Memotong teks panjang di batas kata terdekat."""
    teks = " ".join(str(teks or "").split())
    if len(teks) <= batas:
        return teks
    potong = teks[:batas].rsplit(" ", 1)[0].rstrip(",;:/.")
    return potong + "..."


def _label_pasangan(butir, tautan):
    """Menentukan label yang ditampilkan untuk satu pasangan."""
    label = _label_dari_url(tautan.get("url", ""))
    if label:
        return label

    label = _potong_teks(butir.get("teks", ""))
    if label:
        return label

    return _potong_teks(tautan.get("label", "")) or "Template"


def _catat_peringatan(data, pesan):
    daftar = data.setdefault("peringatan", [])
    if pesan not in daftar:
        daftar.append(pesan)


def pasangkan_tautan(data):
    """
    Memasangkan setiap butir persyaratan ber-template dengan tautan templatenya.
    """
    butir_template = sorted(
        (butir for butir in data.get("syarat", []) if butir.get("template")),
        key=lambda butir: butir["no"],
    )
    daftar_tautan = data.get("tautan", [])

    judul = data.get("judul", "(judul tidak diketahui)")
    jumlah_butir = len(butir_template)
    jumlah_tautan = len(daftar_tautan)

    if not jumlah_butir and not jumlah_tautan:
        return []

    if not jumlah_butir:
        _catat_peringatan(
            data,
            f"ada {jumlah_tautan} tautan tetapi tidak ada butir "
            f"ber-template pada layanan: {judul}. "
            "Pasangan tautan tidak dibuat.",
        )
        return []

    if not jumlah_tautan:
        _catat_peringatan(
            data,
            f"ada {jumlah_butir} butir ber-template tetapi tidak "
            f"ada tautan pada layanan: {judul}. "
            "Pasangan tautan tidak dibuat.",
        )
        return []

    if jumlah_butir != jumlah_tautan:
        _catat_peringatan(
            data,
            f"jumlah butir ber-template ({jumlah_butir}) tidak sama "
            f"dengan jumlah tautan ({jumlah_tautan}) pada layanan: "
            f"{judul}. Pasangan tautan tidak dibuat.",
        )
        return []

    return [
        {
            "no_butir": butir["no"],
            "label": _label_pasangan(butir, tautan),
            "url": tautan["url"],
        }
        for butir, tautan in zip(butir_template, daftar_tautan)
    ]


def baca_halaman_web(path):
    """
    Membaca satu file .txt layanan dan memecahnya per bagian.
    """
    path = Path(path)
    teks = path.read_text(encoding="utf-8")
    baris = [b.strip() for b in teks.splitlines()]

    i_isi = _cari_baris(baris, PENANDA_ISI)

    indeks = {}
    awal = i_isi

    for penanda in PENANDA_WAJIB:
        posisi = _cari_baris(baris, penanda, awal + 1)
        _pastikan_penanda(posisi, penanda, path)
        indeks[penanda] = posisi
        awal = posisi

    i_syarat = indeks[PENANDA_SYARAT]
    i_alur = indeks[PENANDA_ALUR]
    i_hukum = indeks[PENANDA_HUKUM]

    i_tautan = _cari_baris(baris, PENANDA_TAUTAN, i_hukum + 1)

    peringatan = []
    potong_hukum = _potong(baris, i_hukum, i_tautan)

    data = {
        "judul": _nilai_header(baris, "JUDUL:"),
        "url": _nilai_header(baris, "URL:"),
        "tanggal_ambil": _nilai_header(baris, "DIAMBIL (UTC):"),
        "info": _parse_info(_potong(baris, i_isi, i_syarat)),
        "syarat": _parse_syarat(
            _potong(baris, i_syarat, i_alur), peringatan
        ),
        "alur": _parse_alur(
            _potong(baris, i_alur, i_hukum), peringatan
        ),
        "hukum": _parse_hukum(potong_hukum),
        "tautan": _parse_tautan(_potong(baris, i_tautan, -1)),
        "pasangan": [],
        "peringatan": peringatan,
    }

    _pastikan_isi(data, path, potong_hukum)
    data["pasangan"] = pasangkan_tautan(data)

    return data


def tampilkan(data):
    """Mencetak ringkasan hasil pembacaan ke terminal."""
    print("Judul         :", data["judul"])
    print("URL           :", data["url"])
    print("Tanggal ambil :", data["tanggal_ambil"])
    print("Info          :", len(data["info"]), "butir")
    print("Syarat        :", len(data["syarat"]), "butir")
    print("Alur          :", len(data["alur"]), "langkah")
    print("Dasar hukum   :", len(data["hukum"]), "regulasi")
    print("Tautan        :", len(data["tautan"]), "pasang")
    print("Peringatan    :", len(data["peringatan"]), "catatan")

    print("\n--- INFO ---")
    for label, nilai in data["info"].items():
        print(f"{label}: {nilai}")

    nomor_terpasang = {
        item["no_butir"] for item in data.get("pasangan") or []
    }

    print("\n--- SYARAT ---")
    for butir in data["syarat"]:
        tanda = " [template]" if butir["no"] in nomor_terpasang else ""
        print(f"{butir['no']}. {butir['teks']}{tanda}")

    print("\n--- ALUR ---")
    for langkah in data["alur"]:
        print(
            f"{langkah['no']}. {langkah['tahap']} "
            f"[{langkah['pelaksana']}] {langkah['uraian']}"
        )

    print("\n--- DASAR HUKUM ---")
    for regulasi in data["hukum"]:
        print(f"- {regulasi['nama']} ({regulasi['berlaku']})")

    print("\n--- TAUTAN ---")
    for tautan in data["tautan"]:
        print(f"- {tautan['label']}: {tautan['url']}")

    print("\n--- TAUTAN BERPASANGAN ---")
    pasangan = data.get("pasangan")
    if pasangan is None:
        pasangan = pasangkan_tautan(data)

    if not pasangan:
        print("- (tidak ada pasangan)")
    else:
        for item in pasangan:
            print(f"- butir {item['no_butir']}: {item['label']}")
            print(f"  {item['url']}")

    print("\n--- PERINGATAN ---")
    if not data["peringatan"]:
        print("- (tidak ada)")
        return

    for pesan in data["peringatan"]:
        print(f"- {pesan}")


def main():
    if len(sys.argv) < 2:
        print("Pemakaian: python scraping/baca_web.py <file.txt>")
        return

    path = Path(sys.argv[1])
    if not path.is_file():
        print("File tidak ditemukan:", path)
        return

    try:
        data = baca_halaman_web(path)
    except BerkasWebTidakValid as galat:
        sys.exit(f"[gagal] {galat}")

    tampilkan(data)


if __name__ == "__main__":
    main()
