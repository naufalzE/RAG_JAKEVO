# ============================================================
# backend/handover_manager.py
# Pengelola Sesi & Live Agent Handover (Eskalasi ke Staf CS)
# ============================================================

import re
import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from fastapi import WebSocket

from core.logger import get_logger

logger = get_logger("handover")

# Pola frasa yang menandakan pengguna ingin berbicara dengan staf manusia
REGEX_HANDOVER_INTENT = re.compile(
    r"\b(?:"
    r"hubungi\s+(?:cs|staf|petugas|admin|operator|manusia)|"
    r"bicara\s+(?:dengan\s+)?(?:cs|staf|petugas|orang|manusia|operator)|"
    r"ngomong\s+(?:sama\s+)?(?:cs|staf|petugas|orang|manusia)|"
    r"panggil\s+(?:cs|staf|petugas|operator)|"
    r"sambungkan\s+(?:ke\s+)?(?:cs|staf|petugas|operator)|"
    r"bantuan\s+(?:staf|petugas|manusia|cs)|"
    r"customer\s*service|"
    r"live\s*agent|"
    r"operator\s*ptsp|"
    r"admin\s*ptsp|"
    r"mau\s+(?:ke\s+)?petugas|"
    r"tolong\s+cs"
    r")\b",
    re.IGNORECASE,
)


def is_handover_intent(text: str) -> bool:
    """Mendeteksi apakah pertanyaan pengguna adalah permintaan eskalasi ke staf CS."""
    if not text:
        return False
    return bool(REGEX_HANDOVER_INTENT.search(text.strip()))


class ChatSession:
    """Representasi satu sesi percakapan pemohon."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        # Status: BOT_ACTIVE, WAITING_STAFF, STAFF_ACTIVE, RESOLVED
        self.status = "BOT_ACTIVE"
        self.staff_name: Optional[str] = None
        self.handover_reason: Optional[str] = None
        self.messages: List[Dict[str, Any]] = []
        self.client_ws: Optional[WebSocket] = None

    def to_summary(self) -> Dict[str, Any]:
        last_msg = self.messages[-1] if self.messages else None
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
            "staff_name": self.staff_name,
            "handover_reason": self.handover_reason,
            "total_messages": len(self.messages),
            "last_message": last_msg["text"] if last_msg else "",
            "last_sender": last_msg["sender"] if last_msg else "",
            "last_timestamp": last_msg["timestamp"] if last_msg else self.updated_at,
        }

    def to_detail(self) -> Dict[str, Any]:
        res = self.to_summary()
        res["messages"] = self.messages
        return res


class HandoverManager:
    """Pengelola terpusat sesi obrolan dan WebSocket Live Agent Handover."""

    _instance: Optional["HandoverManager"] = None

    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
        self.admin_websockets: Set[WebSocket] = set()

    @classmethod
    def get_instance(cls) -> "HandoverManager":
        if cls._instance is None:
            cls._instance = HandoverManager()
        return cls._instance

    def get_or_create_session(self, session_id: Optional[str] = None) -> ChatSession:
        if not session_id:
            session_id = f"pemohon_{uuid.uuid4().hex[:8]}"

        if session_id not in self.sessions:
            logger.info(f"[Handover] Membuat sesi baru: {session_id}")
            self.sessions[session_id] = ChatSession(session_id)
        return self.sessions[session_id]

    def add_message(
        self,
        session_id: str,
        sender: str,  # 'user', 'bot', 'staff', 'system'
        text: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        session = self.get_or_create_session(session_id)
        session.updated_at = datetime.now().isoformat()
        msg_obj = {
            "id": f"msg_{uuid.uuid4().hex[:8]}",
            "sender": sender,
            "text": text,
            "timestamp": session.updated_at,
            "meta": meta or {},
        }
        session.messages.append(msg_obj)
        return msg_obj

    def request_handover(self, session_id: str, reason: str = "Permintaan Pengguna") -> ChatSession:
        session = self.get_or_create_session(session_id)
        session.status = "WAITING_STAFF"
        session.handover_reason = reason
        session.updated_at = datetime.now().isoformat()

        # Tambahkan catatan sistem di riwayat chat
        self.add_message(
            session_id=session_id,
            sender="system",
            text=f"🔔 Pemohon meminta eskalasi bantuan ke Staf CS (Alasan: {reason}).",
            meta={"type": "handover_alert"},
        )
        logger.info(f"[Handover] Sesi {session_id} masuk status WAITING_STAFF (Alasan: {reason})")
        return session

    def assign_staff(self, session_id: str, staff_name: str = "Petugas PTSP") -> ChatSession:
        session = self.get_or_create_session(session_id)
        session.status = "STAFF_ACTIVE"
        session.staff_name = staff_name
        session.updated_at = datetime.now().isoformat()

        self.add_message(
            session_id=session_id,
            sender="system",
            text=f"👨‍💼 Percakapan telah diambil alih oleh {staff_name}.",
            meta={"type": "staff_assigned", "staff_name": staff_name},
        )
        logger.info(f"[Handover] Sesi {session_id} diambil alih oleh {staff_name}")
        return session

    def resolve_session(self, session_id: str) -> ChatSession:
        session = self.get_or_create_session(session_id)
        session.status = "BOT_ACTIVE"
        session.staff_name = None
        session.handover_reason = None
        session.updated_at = datetime.now().isoformat()

        self.add_message(
            session_id=session_id,
            sender="system",
            text="✅ Sesi bantuan staf telah selesai. Chatbot JAKEVO kembali siap membantu.",
            meta={"type": "session_resolved"},
        )
        logger.info(f"[Handover] Sesi {session_id} diselesaikan dan dikembalikan ke BOT_ACTIVE")
        return session

    # --- Manajemen Koneksi WebSocket ---

    async def register_admin_ws(self, ws: WebSocket):
        self.admin_websockets.add(ws)
        logger.info(f"[Handover WS] Admin terhubung. Total admin aktif: {len(self.admin_websockets)}")
        # Kirimkan daftar sesi saat ini ke admin yang baru tersambung
        await ws.send_json({
            "event": "init_sessions",
            "sessions": self.get_all_sessions_summary(),
        })

    def unregister_admin_ws(self, ws: WebSocket):
        self.admin_websockets.discard(ws)
        logger.info(f"[Handover WS] Admin terputus. Total admin aktif: {len(self.admin_websockets)}")

    def register_client_ws(self, session_id: str, ws: WebSocket):
        session = self.get_or_create_session(session_id)
        session.client_ws = ws
        logger.info(f"[Handover WS] Client {session_id} terhubung ke WebSocket.")

    def unregister_client_ws(self, session_id: str, ws: WebSocket):
        if session_id in self.sessions and self.sessions[session_id].client_ws == ws:
            self.sessions[session_id].client_ws = None
            logger.info(f"[Handover WS] Client {session_id} terputus dari WebSocket.")

    async def broadcast_to_admins(self, event: str, data: Any):
        """Kirim event ke seluruh dashboard admin yang sedang membuka web."""
        if not self.admin_websockets:
            return

        payload = {"event": event, "data": data}
        dead_sockets = set()
        for ws in self.admin_websockets:
            try:
                await ws.send_json(payload)
            except Exception as e:
                logger.warning(f"[Handover WS] Gagal broadcast ke admin: {e}")
                dead_sockets.add(ws)

        for ws in dead_sockets:
            self.admin_websockets.discard(ws)

    async def send_to_client(self, session_id: str, event: str, data: Any):
        """Kirim pesan/event langsung ke browser pemohon tertentu."""
        session = self.sessions.get(session_id)
        if not session or not session.client_ws:
            return

        try:
            await session.client_ws.send_json({"event": event, "data": data})
        except Exception as e:
            logger.warning(f"[Handover WS] Gagal kirim ke client {session_id}: {e}")
            session.client_ws = None

    def get_all_sessions_summary(self) -> List[Dict[str, Any]]:
        return [
            s.to_summary()
            for s in sorted(
                self.sessions.values(),
                key=lambda x: x.updated_at,
                reverse=True,
            )
        ]

    def get_session_detail(self, session_id: str) -> Optional[Dict[str, Any]]:
        s = self.sessions.get(session_id)
        return s.to_detail() if s else None
