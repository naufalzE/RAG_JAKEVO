# ============================================================
# backend/service.py
# Business logic / Service layer untuk pipeline RAG + Guardrail
# ============================================================

import sys
import time
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any

# Pastikan import proyek berjalan
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.config import NAMA_MODEL_EMBEDDING
from core.guardrail import Guardrail, guardrail_default
from core.logger import get_logger, catat_audit_chat
from storage.database import buka_collection
from storage.embedding import muat_model
from retrieval.tetangga import urutkan_id_chunk_teks
from retrieval.konteks import format_sumber
from llm.llm import info_llm
from tanya_jawab import jawab

logger = get_logger("service")


class RAGService:
    """
    Service singleton untuk mengelola koneksi database ChromaDB,
    model embedding, guardrail keamanan, dan eksekusi tanya jawab RAG.
    """

    _instance: Optional["RAGService"] = None

    def __init__(self, guardrail: Optional[Guardrail] = None):
        self.collection = None
        self.model = None
        self.urut: List[str] = []
        self._is_ready: bool = False
        self.guardrail = guardrail or guardrail_default

    @classmethod
    def get_instance(cls) -> "RAGService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initialize(self):
        """Memuat database ChromaDB dan model embedding ke memori."""
        if self._is_ready:
            return

        logger.info("[RAGService] Membuka collection ChromaDB...")
        self.collection = buka_collection()

        logger.info(f"[RAGService] Memuat model embedding ({NAMA_MODEL_EMBEDDING})...")
        self.model = muat_model(NAMA_MODEL_EMBEDDING)

        logger.info("[RAGService] Mengurutkan urutan chunk teks...")
        self.urut = urutkan_id_chunk_teks(self.collection)

        self._is_ready = True
        logger.info(
            f"[RAGService] Inisialisasi selesai! Total chunk terurut: {len(self.urut)}, LLM: {info_llm()}"
        )

    def pastikan_siap(self):
        """Lazy load jika belum diinisialisasi."""
        if not self._is_ready:
            self.initialize()

    def tanya(
        self,
        pertanyaan: str,
        topk: int = 10,
        jumlah_chunk: int = 3,
        jumlah_tetangga: int = 1,
        debug: bool = False,
        endpoint: str = "api",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, str, List[Dict[str, Any]], bool, Optional[str]]:
        """
        Menjalankan proses tanya jawab dengan proteksi Guardrail multi-layer
        dan pencatatan audit trail percakapan otomatis.

        Returns:
            Tuple[jawaban, sumber_teks, daftar_chunk_sumber, guardrail_lolos, guardrail_alasan]
        """
        waktu_mulai = time.time()

        # --- LAYER 1: INPUT GUARDRAIL ---
        cek_input = self.guardrail.periksa_input(pertanyaan)
        if not cek_input.lolos:
            durasi = time.time() - waktu_mulai
            logger.warning(
                f"[GUARDRAIL BLOCKED] Alasan: '{cek_input.alasan}' | Query: '{pertanyaan[:80]}'"
            )
            catat_audit_chat(
                pertanyaan=pertanyaan,
                jawaban=cek_input.pesan_penolakan,
                sumber=[],
                durasi_detik=durasi,
                guardrail_status={
                    "lolos": False,
                    "alasan": cek_input.alasan,
                    "kategori": cek_input.kategori,
                },
                endpoint=endpoint,
                llm_info=info_llm(),
                metadata=metadata,
            )
            return (
                cek_input.pesan_penolakan,
                "Guardrail Keamanan Sistem",
                [],
                False,
                cek_input.alasan,
            )

        self.pastikan_siap()

        logger.info(f"[RAG Query] '{pertanyaan[:80]}' (topk={topk})")

        # Eksekusi RAG
        jawaban_llm, hasil_retrieval = jawab(
            pertanyaan=pertanyaan,
            collection=self.collection,
            model=self.model,
            urut=self.urut,
            topk=topk,
            jumlah_chunk=jumlah_chunk,
            jumlah_tetangga=jumlah_tetangga,
            debug=debug,
        )

        # --- LAYER 2: OUTPUT GUARDRAIL (Sanitasi PII & Format) ---
        jawaban_bersih = self.guardrail.periksa_output(jawaban_llm)

        sumber_str = format_sumber(hasil_retrieval) or "Tidak ada sumber relevan."

        # Format list chunk untuk response JSON terstruktur
        chunks_info = []
        for c in hasil_retrieval:
            meta = c.get("metadata", {})
            chunks_info.append({
                "chunk_id": c.get("chunk_id"),
                "file": meta.get("file"),
                "tipe": meta.get("tipe"),
                "distance": c.get("distance"),
                "teks": c.get("teks", "")[:200] + "..." if len(c.get("teks", "")) > 200 else c.get("teks", ""),
            })

        durasi_total = time.time() - waktu_mulai
        logger.info(
            f"[RAG Selesai] Durasi: {durasi_total:.2f}s | Chunk: {len(chunks_info)} | Endpoint: {endpoint}"
        )

        # Simpan jejak audit percakapan
        catat_audit_chat(
            pertanyaan=pertanyaan,
            jawaban=jawaban_bersih,
            sumber=chunks_info,
            durasi_detik=durasi_total,
            guardrail_status={"lolos": True, "alasan": None},
            endpoint=endpoint,
            llm_info=info_llm(),
            metadata=metadata,
        )

        return jawaban_bersih, sumber_str, chunks_info, True, None

    def get_status(self) -> Dict[str, Any]:
        """Mengambil informasi status service dan database."""
        total_data = 0
        if self.collection is not None:
            try:
                total_data = self.collection.count()
            except Exception:
                total_data = len(self.urut)

        return {
            "status": "ready" if self._is_ready else "not_initialized",
            "llm": info_llm(),
            "model_embedding": NAMA_MODEL_EMBEDDING,
            "total_chunk_db": total_data,
        }
