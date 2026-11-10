# ============================================================
# core/logger.py
# Sistem Logging Sentral & Audit Trail untuk RAG JAKEVO
# ============================================================

import os
import json
import uuid
import logging
import threading
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Dict, Any, List

from core.config import settings

# Inisialisasi folder log
LOG_DIR = Path(settings.LOG_DIR)
LOG_DIR.mkdir(parents=True, exist_ok=True)

FILE_APP_LOG = LOG_DIR / "app.log"
FILE_ERROR_LOG = LOG_DIR / "error.log"
FILE_AUDIT_LOG = LOG_DIR / "chat_audit.jsonl"

# Thread lock untuk memastikan penulisan JSONL aman pada konkurensi FastAPI
_audit_lock = threading.Lock()

# Format teks standar log sistem
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_configured = False


def _setup_root_logging():
    """Mengonfigurasi handler global untuk console dan file log rotasi."""
    global _configured
    if _configured:
        return

    level_str = getattr(settings, "LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_str, logging.INFO)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # 1. Handler Console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # 2. Handler File Semua Log (app.log - rotasi 10MB x 5 file cadangan)
    app_file_handler = RotatingFileHandler(
        FILE_APP_LOG,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    app_file_handler.setLevel(level)
    app_file_handler.setFormatter(formatter)

    # 3. Handler File Khusus Error (error.log - rotasi 10MB x 5 file cadangan)
    error_file_handler = RotatingFileHandler(
        FILE_ERROR_LOG,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)

    root_logger = logging.getLogger("jakevo")
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(app_file_handler)
    root_logger.addHandler(error_file_handler)

    # Cegah propagation berulang ke root bawaan python
    root_logger.propagate = False

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Mengambil logger terspesifikasi di bawah namespace 'jakevo'.
    Contoh: get_logger('backend.service') -> 'jakevo.backend.service'
    """
    if not _configured:
        _setup_root_logging()

    if name.startswith("jakevo.") or name == "jakevo":
        return logging.getLogger(name)
    return logging.getLogger(f"jakevo.{name}")


logger = get_logger("system")


def catat_audit_chat(
    pertanyaan: str,
    jawaban: str,
    sumber: Optional[List[Dict[str, Any]]] = None,
    durasi_detik: float = 0.0,
    guardrail_status: Optional[Dict[str, Any]] = None,
    endpoint: str = "api",
    llm_info: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Mencatat satu interaksi percakapan lengkap ke dalam file chat_audit.jsonl
    untuk keperluan analisis, audit performa, kepatuhan guardrail, dan evaluasi RAG.

    Returns:
        log_id (str): ID unik transaksi percakapan (UUID).
    """
    if not getattr(settings, "ENABLE_AUDIT_LOG", True):
        return ""

    log_id = str(uuid.uuid4())
    record = {
        "id": log_id,
        "timestamp": datetime.now().isoformat(),
        "endpoint": endpoint,
        "llm": llm_info or "unknown",
        "durasi_detik": round(float(durasi_detik), 3),
        "pertanyaan": pertanyaan,
        "jawaban": jawaban,
        "guardrail": guardrail_status or {"lolos": True, "alasan": None},
        "jumlah_sumber": len(sumber) if sumber else 0,
        "sumber": sumber or [],
        "metadata": metadata or {},
    }

    try:
        baris_json = json.dumps(record, ensure_ascii=False)
        with _audit_lock:
            with open(FILE_AUDIT_LOG, mode="a", encoding="utf-8") as f:
                f.write(baris_json + "\n")
    except Exception as e:
        logger.error(f"Gagal menulis chat audit log: {e}", exc_info=True)

    return log_id
