import _bootstrap  # noqa: F401  (menyiapkan sys.path ke folder chatbotv2)

from database import buka_collection

collection = buka_collection()
id_uji = "UJI-BASI-001"

print("ID", id_uji, "ada:", id_uji in collection.get()["ids"])
print("Jumlah data:", collection.count())