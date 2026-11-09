import _bootstrap  # noqa: F401
from pathlib import Path

from scraping.baca_web import _label_dari_url, baca_halaman_web, pasangkan_tautan

print("--- LABEL DARI URL ---")
for url in (
    "https://jakevo.jakarta.go.id/documents/Surat_Kuasa.docx",
    "https://jakevo.jakarta.go.id/documents/Formulir%20A.pdf",
    "https://jakevo.jakarta.go.id/documents/Surat%20Pernyataan_(Baru).docx",
    "https://jakevo.jakarta.go.id/documents/Formulir_A.pdf?x=1#hal2",
    "https://jcdn.jakarta.go.id/a/b/surat_pengganti_pengantar_RT_RW_3.docx",
    "https://jcdn.jakarta.go.id/a/b/2026030969ae2fa2b3b1cce1e621c.docx",
    "",
):
    print(f"{url!r} -> {_label_dari_url(url)!r}")

print()
print("Catatan: hasil kosong berarti nama berkas tidak")
print("bermakna (mis. hash), sehingga label diambil dari")
print("teks butir persyaratan oleh pasangkan_tautan().")

print()
print("--- PASANGAN PER DOKUMEN ---")
folder_web = Path(_bootstrap.FOLDER_PROYEK) / "dokumen_web"
for path in sorted(folder_web.glob("*.txt")):
    print("===", path.name, "===")

    try:
        data = baca_halaman_web(path)
    except ValueError as galat:
        print("[ditolak]", galat)
        print()
        continue

    for item in data["pasangan"]:
        print(f"butir {item['no_butir']} -> {item['label']} | {item['url']}")

    for pesan in data["peringatan"]:
        print("[peringatan]", pesan)

    print()
