# ============================================================
# backend/main.py
# Inisialisasi aplikasi FastAPI, CORS, dan penyajian Frontend JIC
# ============================================================

from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.router import router as rag_router, chat_endpoint
from backend.service import RAGService

# Lokasi folder frontend jic-assistant
FOLDER_BACKEND = Path(__file__).resolve().parent
FOLDER_FRONTEND = FOLDER_BACKEND.parent / "frontend" / "jic-assistant"
if not FOLDER_FRONTEND.exists():
    FOLDER_FRONTEND = FOLDER_BACKEND.parent.parent / "frontend" / "jic-assistant"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n--- [BACKEND] Memulai Server FastAPI RAG JAKEVO ---")
    try:
        service = RAGService.get_instance()
        service.initialize()
    except Exception as e:
        print(f"[BACKEND WARNING] Inisialisasi service ditunda: {e}")

    yield

    print("--- [BACKEND] Menghentikan Server FastAPI ---")


app = FastAPI(
    title="JAKEVO Assistant RAG API",
    description="Backend API untuk Chatbot Retrieval-Augmented Generation (RAG) Layanan JAKEVO DPMPTSP DKI Jakarta",
    version="1.0.0",
    lifespan=lifespan,
)

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
