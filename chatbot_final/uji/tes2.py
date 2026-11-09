import _bootstrap  # noqa: F401
from pathlib import Path
from pprint import pprint
from scraping.baca_web import baca_halaman_web

file_target = Path(_bootstrap.FOLDER_PROYEK) / "dokumen_web" / "PM1_PERKAWINAN_BAWAH_UMUR.txt"
data = baca_halaman_web(file_target)

print(type(data))
print(list(data.keys()))
print()

pprint(data["info"])
pprint(data["syarat"][2])
