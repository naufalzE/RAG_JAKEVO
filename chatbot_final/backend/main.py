# ============================================================
# backend/main.py
# Inisialisasi aplikasi FastAPI, CORS, dan penyajian Frontend JIC
# ============================================================

from pathlib import Path
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.router import router as rag_router, chat_endpoint
from backend.service import RAGService
from core.logger import get_logger

logger = get_logger("backend")

# Lokasi folder frontend jic-assistant
FOLDER_BACKEND = Path(__file__).resolve().parent
FOLDER_FRONTEND = FOLDER_BACKEND.parent / "frontend" / "jic-assistant"
if not FOLDER_FRONTEND.exists():
    FOLDER_FRONTEND = FOLDER_BACKEND.parent.parent / "frontend" / "jic-assistant"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("--- [BACKEND] Memulai Server FastAPI RAG JAKEVO ---")
    try:
        service = RAGService.get_instance()
        service.initialize()
    except Exception as e:
        logger.warning(f"[BACKEND WARNING] Inisialisasi service ditunda: {e}")

    yield

    logger.info("--- [BACKEND] Menghentikan Server FastAPI ---")


app = FastAPI(
    title="JAKEVO Assistant RAG API",
    description="Backend API untuk Chatbot Retrieval-Augmented Generation (RAG) Layanan JAKEVO DPMPTSP DKI Jakarta",
    version="1.0.0",
    lifespan=lifespan,
)

# Middleware untuk mencatat latensi dan status setiap HTTP request
@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    method = request.method
    path = request.url.path

    try:
        response = await call_next(request)
        process_time_ms = (time.time() - start_time) * 1000
        # Catat request API ke dalam logger
        if path.startswith(("/api", "/rag")):
            logger.info(
                f"[HTTP] {method} {path} | Status: {response.status_code} | "
                f"Durasi: {process_time_ms:.1f}ms | IP: {client_ip}"
            )
        return response
    except Exception as exc:
        process_time_ms = (time.time() - start_time) * 1000
        logger.error(
            f"[HTTP ERROR] {method} {path} | Gagal setelah {process_time_ms:.1f}ms | "
            f"IP: {client_ip} | Galat: {exc}",
            exc_info=True,
        )
        raise exc

# Setup CORS agar bisa diakses oleh frontend dari domain atau port mana pun
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Daftarkan router API RAG (/rag/tanya, /rag/chat, /rag/status)
app.include_router(rag_router)

# 2. Daftarkan endpoint langsung /api/chat untuk frontend JAKEVO Assistant
app.add_api_route(
    "/api/chat",
    chat_endpoint,
    methods=["POST"],
    tags=["Frontend JAKEVO Assistant"],
    summary="Endpoint Chat Utama Frontend JAKEVO",
)

# 3. Sajikan langsung frontend JIC Assistant di web server
if FOLDER_FRONTEND.exists():
    app.mount("/", StaticFiles(directory=str(FOLDER_FRONTEND), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
