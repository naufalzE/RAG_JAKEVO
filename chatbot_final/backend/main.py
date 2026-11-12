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

# Lokasi folder frontend jic-assistant & admin
FOLDER_BACKEND = Path(__file__).resolve().parent
FOLDER_FRONTEND = FOLDER_BACKEND.parent / "frontend" / "jic-assistant"
if not FOLDER_FRONTEND.exists():
    FOLDER_FRONTEND = FOLDER_BACKEND.parent.parent / "frontend" / "jic-assistant"

FOLDER_ADMIN = FOLDER_BACKEND.parent / "frontend" / "admin"
if not FOLDER_ADMIN.exists():
    FOLDER_ADMIN = FOLDER_BACKEND.parent.parent / "frontend" / "admin"


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

# 3. Endpoint WebSocket untuk Live Agent Handover
from fastapi import WebSocket, WebSocketDisconnect
from backend.handover_manager import HandoverManager

@app.websocket("/ws/chat/{session_id}")
async def ws_chat_client(websocket: WebSocket, session_id: str):
    """Kanal WebSocket real-time untuk pemohon/warga."""
    await websocket.accept()
    mgr = HandoverManager.get_instance()
    mgr.register_client_ws(session_id, websocket)
    try:
        session = mgr.get_or_create_session(session_id)
        await websocket.send_json({
            "event": "session_state",
            "data": session.to_summary()
        })
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            if action == "request_handover":
                reason = data.get("reason", "Permintaan Pengguna via Tombol Bantuan")
                session = mgr.request_handover(session_id, reason=reason)
                await mgr.broadcast_to_admins("handover_requested", session.to_detail())
                await websocket.send_json({
                    "event": "handover_status",
                    "data": {"status": "WAITING_STAFF", "message": "Menghubungkan ke staf pelayanan..."}
                })
            elif action == "ping":
                await websocket.send_json({"event": "pong"})
    except WebSocketDisconnect:
        mgr.unregister_client_ws(session_id, websocket)
    except Exception as e:
        logger.warning(f"[WS Chat Error] {session_id}: {e}")
        mgr.unregister_client_ws(session_id, websocket)


@app.websocket("/ws/admin")
async def ws_admin(websocket: WebSocket):
    """Kanal WebSocket real-time untuk Dashboard Staf CS (Admin)."""
    await websocket.accept()
    mgr = HandoverManager.get_instance()
    await mgr.register_admin_ws(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "takeover":
                session_id = data.get("session_id")
                staff_name = data.get("staff_name", "Petugas PTSP")
                if session_id:
                    session = mgr.assign_staff(session_id, staff_name=staff_name)
                    await mgr.send_to_client(session_id, "staff_joined", {
                        "staff_name": staff_name,
                        "message": f"Petugas pelayanan ({staff_name}) telah bergabung dalam obrolan."
                    })
                    await mgr.broadcast_to_admins("session_updated", session.to_detail())

            elif action == "send_message":
                session_id = data.get("session_id")
                text = data.get("text", "").strip()
                staff_name = data.get("staff_name", "Petugas PTSP")
                if session_id and text:
                    msg = mgr.add_message(session_id, sender="staff", text=text, meta={"staff_name": staff_name})
                    await mgr.send_to_client(session_id, "staff_message", {
                        "staff_name": staff_name,
                        "text": text,
                        "timestamp": msg["timestamp"]
                    })
                    session = mgr.get_or_create_session(session_id)
                    await mgr.broadcast_to_admins("message_added", {
                        "session_id": session_id,
                        "message": msg,
                        "session": session.to_summary()
                    })

            elif action == "resolve":
                session_id = data.get("session_id")
                if session_id:
                    session = mgr.resolve_session(session_id)
                    await mgr.send_to_client(session_id, "session_resolved", {
                        "message": "Sesi bantuan staf telah selesai. Chatbot JAKEVO kembali siap membantu."
                    })
                    await mgr.broadcast_to_admins("session_updated", session.to_detail())

            elif action == "get_session":
                session_id = data.get("session_id")
                detail = mgr.get_session_detail(session_id)
                await websocket.send_json({"event": "session_detail", "data": detail})

    except WebSocketDisconnect:
        mgr.unregister_admin_ws(websocket)
    except Exception as e:
        logger.warning(f"[WS Admin Error]: {e}")
        mgr.unregister_admin_ws(websocket)


from fastapi.responses import RedirectResponse

# 4. Sajikan frontend Admin & JIC Assistant
if FOLDER_ADMIN.exists():
    @app.get("/admin", include_in_schema=False)
    async def redirect_admin():
        return RedirectResponse(url="/admin/")

    app.mount("/admin", StaticFiles(directory=str(FOLDER_ADMIN), html=True), name="admin")

if FOLDER_FRONTEND.exists():
    app.mount("/", StaticFiles(directory=str(FOLDER_FRONTEND), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
