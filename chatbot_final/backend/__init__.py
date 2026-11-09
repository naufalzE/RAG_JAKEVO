# ============================================================
# backend/__init__.py
# Inisialisasi package backend dan memastikan sys.path
# ============================================================

import sys
from pathlib import Path

# Pastikan folder chatbotv2 ada di sys.path
FOLDER_BACKEND = Path(__file__).resolve().parent
FOLDER_PROYEK = FOLDER_BACKEND.parent

if str(FOLDER_PROYEK) not in sys.path:
    sys.path.insert(0, str(FOLDER_PROYEK))
