import _bootstrap  # noqa: F401
import glob
from pathlib import Path
from scraping.baca_web import baca_halaman_web
from chunking.chunk_web import teks_hukum

folder_web = Path(_bootstrap.FOLDER_PROYEK) / "dokumen_web"

for path in sorted(folder_web.glob("*.txt")):
    data = baca_halaman_web(path)
    teks = teks_hukum(data)
    print(teks)
    print(len(teks), "karakter")
    print("==================================")
