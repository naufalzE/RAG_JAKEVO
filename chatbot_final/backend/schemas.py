# ============================================================
# backend/schemas.py
# Skema Pydantic untuk request dan response API
# ============================================================

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class TanyaRequest(BaseModel):
    pertanyaan: str = Field(
        ...,
        description="Pertanyaan yang diajukan pengguna terkait layanan JAKEVO",
        example="Apa saja syarat surat pengantar perkawinan pertama?",
    )
    topk: int = Field(
        default=10,
        description="Banyaknya chunk teratas dari pencarian semantik vektor",
        ge=1,
        le=30,
    )
    jumlah_chunk: int = Field(
        default=3,
        description="Jumlah chunk utama yang diperluas dengan tetangga",
        ge=1,
        le=10,
    )
    jumlah_tetangga: int = Field(
        default=1,
        description="Jumlah tetangga berikutnya untuk memperkaya konteks",
        ge=0,
        le=5,
    )
    debug: bool = Field(
        default=False,
        description="Tampilkan log konteks di console server",
    )


class TanyaResponse(BaseModel):
    pertanyaan: str
    jawaban: str
    sumber_teks: str
    chunks: List[Dict[str, Any]] = []
    guardrail_lolos: bool = True
    guardrail_alasan: Optional[str] = None


class StatusResponse(BaseModel):
    status: str
    llm: str
    model_embedding: str
    total_chunk_db: int

class ChunkSumber(BaseModel):
    chunk_id: str
    file: Optional[str] = None
    tipe: Optional[str] = None
    distance: Optional[float] = None

# --- Model untuk integrasi Frontend JIC Assistant ---

class ChatRequest(BaseModel):
    message: Optional[str] = Field(None, description="Teks pesan dari frontend")
    pertanyaan: Optional[str] = Field(None, description="Alias pertanyaan")
    topk: int = Field(default=10, ge=1, le=30)
    jumlah_chunk: int = Field(default=3, ge=1, le=10)
    jumlah_tetangga: int = Field(default=1, ge=0, le=5)
    debug: bool = False

    def get_query(self) -> str:
        return (self.message or self.pertanyaan or "").strip()


class MatchedDoc(BaseModel):
    id: str
    topic: str
    sourceDoc: str


class ChatResponse(BaseModel):
    query: str
    tokens: List[str] = []
    isRelevant: bool
    score: int
    matchedDoc: Optional[MatchedDoc] = None
    matchedKeywords: List[str] = []
    contextSnippet: str
    finalAnswer: str
    rawAnswer: str
    sumber: str
    guardrail_lolos: bool = True
    guardrail_alasan: Optional[str] = None
