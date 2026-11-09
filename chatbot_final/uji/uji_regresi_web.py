# ============================================================
# uji_regresi_web.py
# Tes regresi baca_web.py atas lima berkas uji.
#
# Dua dokumen asli harus terbaca persis seperti sebelumnya:
#   asli_bawah_umur.txt -> 9 syarat, 4 alur, 3 hukum, 2 tautan
#   asli_pertama.txt    -> 10 syarat, 4 alur, 4 hukum, 2 tautan
#   asli_rumah.txt      -> 5 syarat, 4 alur, 4 hukum, 2 tautan
#                          (tautannya bernama hash di URL)
#
# Tiga berkas rusak menguji kebijakan penolakan:
#   c1_tanpa_alur.txt   -> ditolak (ValueError)
#   c2_angka_nyasar.txt -> 9 butir utuh + 1 peringatan
#   c3_tanpa_tautan.txt -> pasangan kosong + 1 peringatan
#
# Jalankan dari folder chatbotv2:
#     python uji/uji_regresi_web.py
#
# Keluar dengan kode 1 bila ada pemeriksaan yang gagal.
# ============================================================

import sys
from pathlib import Path

import _bootstrap  # noqa: F401  (menambah chatbotv2 ke sys.path)

from baca_web import BerkasWebTidakValid, baca_halaman_web

FOLDER_DATA = Path(__file__).resolve().parent / "data_web"
GAGAL = []


def periksa(nama, syarat, pesan):
    """Mencatat satu pemeriksaan dan mencetak hasilnya."""

    tanda = "OK   " if syarat else "GAGAL"
    print(f"[{tanda}] {nama}: {pesan}")

    if not syarat:
        GAGAL.append(f"{nama}: {pesan}")


def baca(nama):
    """Mengembalikan (data, galat); data None bila berkas ditolak."""

    try:
        return baca_halaman_web(FOLDER_DATA / nama), None
    except ValueError as galat:
        return None, galat


def uji_asli(nama, harap):
    """Dokumen asli tidak boleh berubah hasilnya."""

    data, galat = baca(nama)

    if galat is not None:
        periksa(nama, False, f"ditolak: {galat}")
        return

    hasil = (
        len(data["syarat"]),
        len(data["alur"]),
        len(data["hukum"]),
        len(data["tautan"]),
    )

    periksa(nama, hasil == harap, f"hasil {hasil}, diharapkan {harap}")
    periksa(
        nama,
        len(data["pasangan"]) == 2,
        f"{len(data['pasangan'])} pasangan, diharapkan 2",
    )
    periksa(nama, data["peringatan"] == [], f"peringatan {data['peringatan']}")


def uji_c1():
    """C1: penanda hilang harus ditolak, bukan diisi sampai EOF."""

    data, galat = baca("c1_tanpa_alur.txt")

    periksa(
        "C1",
        isinstance(galat, BerkasWebTidakValid),
        f"galat {type(galat).__name__}, diharapkan BerkasWebTidakValid",
    )
    periksa(
        "C1",
        "Alur Proses" in str(galat),
        f"pesan: {galat}",
    )
    periksa("C1", data is None, "tidak ada data yang dikembalikan")


def uji_c2():
    """C2: angka nyasar tidak boleh membuka butir baru."""

    data, galat = baca("c2_angka_nyasar.txt")

    if galat is not None:
        periksa("C2", False, f"ditolak: {galat}")
        return

    nomor = [butir["no"] for butir in data["syarat"]]
    periksa("C2", nomor == list(range(1, 10)), f"nomor {nomor}")

    teks = data["syarat"][-1]["teks"] if data["syarat"] else ""
    periksa(
        "C2",
        "Surat Keterangan Kematian" in teks,
        "butir 9 memuat 'Surat Keterangan Kematian'",
    )
    periksa("C2", len(data["alur"]) == 4, f"alur {len(data['alur'])}")
    periksa(
        "C2",
        len(data["pasangan"]) == 2,
        f"{len(data['pasangan'])} pasangan, diharapkan 2",
    )
    periksa(
        "C2",
        len(data["peringatan"]) == 1,
        f"peringatan {data['peringatan']}",
    )


def uji_c3():
    """C3: butir ber-template tanpa tautan harus diperingatkan."""

    data, galat = baca("c3_tanpa_tautan.txt")

    if galat is not None:
        periksa("C3", False, f"ditolak: {galat}")
        return

    periksa("C3", data["tautan"] == [], f"tautan {data['tautan']}")
    periksa("C3", data["pasangan"] == [], f"pasangan {data['pasangan']}")
    periksa(
        "C3",
        len(data["syarat"]) == 9,
        f"syarat {len(data['syarat'])}, diharapkan 9",
    )
    periksa(
        "C3",
        len(data["peringatan"]) == 1,
        f"peringatan {data['peringatan']}",
    )


def uji_label_hash():
    """
    Sebagian URL memakai nama berkas berbentuk hash. Label
    pasangan harus tetap bermakna, bukan menampilkan hash.
    """

    data, galat = baca("asli_rumah.txt")

    if galat is not None:
        periksa("label", False, f"ditolak: {galat}")
        return

    label = {
        item["no_butir"]: item["label"] for item in data["pasangan"]
    }

    periksa(
        "label",
        label.get(2) == "surat pengganti pengantar RT RW 3",
        f"butir 2: {label.get(2)!r}",
    )
    periksa(
        "label",
        "2026030969ae2fa2b3b1cce1e621c" not in label.get(3, "x"),
        f"butir 3 tidak memakai nama hash: {label.get(3)!r}",
    )
    periksa(
        "label",
        "Surat Pernyataan" in label.get(3, ""),
        f"butir 3 diambil dari teks butir: {label.get(3)!r}",
    )


def main():
    if not FOLDER_DATA.is_dir():
        sys.exit(
            f"Folder {FOLDER_DATA} belum ada. "
            "Jalankan dulu: python uji/buat_data_web.py"
        )

    print("=== DOKUMEN ASLI ===")
    uji_asli("asli_bawah_umur.txt", (9, 4, 3, 2))
    uji_asli("asli_pertama.txt", (10, 4, 4, 2))
    uji_asli("asli_rumah.txt", (5, 4, 4, 2))

    print("\n=== LABEL TAUTAN ===")
    uji_label_hash()

    print("\n=== KASUS TEPI ===")
    uji_c1()
    uji_c2()
    uji_c3()

    print()

    if GAGAL:
        print(f"HASIL: {len(GAGAL)} pemeriksaan GAGAL")

        for pesan in GAGAL:
            print(f"  - {pesan}")

        sys.exit(1)

    print("HASIL: semua pemeriksaan lolos.")


if __name__ == "__main__":
    main()
