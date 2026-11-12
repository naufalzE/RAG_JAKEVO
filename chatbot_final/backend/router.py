# ============================================================
# backend/router.py
# Router API FastAPI untuk endpoint tanya jawab RAG & Frontend
# ============================================================

import re
import html
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends
from backend.schemas import (
    TanyaRequest,
    TanyaResponse,
    StatusResponse,
    ChatRequest,
    ChatResponse,
    MatchedDoc,
)
from backend.service import RAGService
from backend.handover_manager import HandoverManager, is_handover_intent
from core.logger import get_logger

logger = get_logger("router")

router = APIRouter(prefix="/rag", tags=["Chatbot RAG JAKEVO"])


def get_rag_service() -> RAGService:
    service = RAGService.get_instance()
    service.pastikan_siap()
    return service


def label_dari_url(url: str) -> str:
    """Mengambil nama dokumen spesifik dari URL agar tombol jelas dan tidak membingungkan."""
    nama_file = url.rstrip("/").split("/")[-1]
    nama_bersih = re.sub(r"\.(docx|pdf|doc|xlsx)$", "", nama_file, flags=re.IGNORECASE)
    nama_bersih = nama_bersih.replace("_", " ").replace("-", " ").strip()

    # Jika nama file berupa kode hash/acak di server upload
    if len(nama_bersih) > 20 and re.match(r"^[0-9a-fA-F]+$", nama_bersih):
        return "Unduh Formulir Template"

    # Pemetaan singkatan atau istilah umum
    nama_bersih = re.sub(r"\brt\s+rw\b", "RT/RW", nama_bersih, flags=re.IGNORECASE)
    return f"Unduh {nama_bersih.title()}"


def format_link(content: str) -> str:
    """Mengubah URL panjang menjadi tautan spesifik dokumen yang interaktif dan rapi."""
    url_pattern = re.compile(r"(?:(?:-&gt;|->)\s*)?(https?://[^\s<>\"'\)]+)")

    def _sub(m):
        url = m.group(1).rstrip(".,;")
        label = label_dari_url(url)
        return (
            f'<div style="margin-top: 4px; text-indent: 0;">'
            f'<a href="{url}" target="_blank" rel="noopener noreferrer" '
            f'class="jakevo-link-btn" '
            f'title="Klik untuk mengunduh {label} ({url})">'
            f'&#128196; {label} (Klik disini &nearr;)'
            f'</a></div>'
        )

    return url_pattern.sub(_sub, content)


def text_to_html(text: str) -> str:
    """Mengubah format jawaban teks menjadi elemen HTML untuk frontend UI."""
    if not text:
        return ""

    # Normalisasi nomor yang menempel dalam satu paragraf (misal: "Persyaratan: 1. A; 2. B; 3. C")
    # Hanya pecah angka 1-99 yang didahului titik dua (:) atau titik koma (;) agar kode pos (12920.) tidak ikut terpecah
    text = re.sub(r"([;:])\s*([1-9]\d?)\.\s+", r"\1\n\2. ", text)
    # Berikan jeda baris baru sebelum judul layanan (misal: "PM1 Lurah/Camat...")
    text = re.sub(r"(?:\n|^)((?:PM1|IZIN|SURAT\s+IZIN)\s+[^\n]+)", r"\n\n\1\n", text)

    lines = text.strip().split("\n")
    html_lines = []
    in_list = False
    seen_list_items = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Bersihkan tanda panah gantung di ujung baris sebelum link
        stripped = re.sub(r"\s*(?:->|-&gt;)\s*$", "", stripped)

        # Cek butir bernomor "1. ..." atau "1) ..."
        match_num = re.match(r"^(\d+)[\.\)]\s+(.*)", stripped)
        # Cek butir tanda hubung "- ..." atau "• ..."
        match_bullet = re.match(r"^[-*•]\s+(.*)", stripped)
        # Cek apakah baris ini berisi tautan / lanjutan template dari butir sebelumnya
        is_link_continuation = bool(
            re.search(r"https?://\S+", stripped, re.IGNORECASE)
            or re.match(r"^(?:tautan\s+template|butir\s+\d+)", stripped, re.IGNORECASE)
        )
        # Cek apakah baris ini adalah judul layanan / dokumen / sub-bagian baru
        is_section_header = bool(
            re.match(r"^(?:\*\*|\#\#\s*)?(?:PM1|IZIN\s+|SURAT\s+IZIN|Layanan\s+|Ketentuan\s+)", stripped, re.IGNORECASE)
            or (seen_list_items and not match_num and not match_bullet and not is_link_continuation and stripped.endswith(":"))
        )

        if match_num:
            num = int(match_num.group(1))
            in_list = True
            seen_list_items = True
            escaped = html.escape(match_num.group(2))
            formatted_bold = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
            content = format_link(formatted_bold)
            html_lines.append(
                f"<div style='margin: 0 0 4px 0; padding-left: 22px; text-indent: -22px;'>"
                f"<strong>{num}.</strong> {content}</div>"
            )
        elif in_list and is_link_continuation and html_lines and html_lines[-1].endswith("</div>"):
            escaped = html.escape(stripped)
            formatted_bold = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
            content = format_link(formatted_bold)
            html_lines[-1] = html_lines[-1][:-6] + f"{content}</div>"
        elif match_bullet:
            in_list = False
            escaped = html.escape(match_bullet.group(1))
            formatted_bold = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
            content = format_link(formatted_bold)
            html_lines.append(f"<p style='margin: 0 0 4px 0;'>• {content}</p>")
        elif is_section_header or (in_list and not match_num and not is_link_continuation):
            in_list = False
            clean_title = stripped.strip("*# ")
            escaped = html.escape(clean_title)
            formatted_bold = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
            content = format_link(formatted_bold)
            if seen_list_items:
                html_lines.append(
                    f"<div class='jakevo-doc-title' style='margin: 14px 0 6px 0; padding-top: 8px; border-top: 1px dashed rgba(250, 204, 21, 0.4); font-weight: 700; color: #FACC15;'>{content}</div>"
                )
            else:
                html_lines.append(
                    f"<div class='jakevo-doc-title' style='margin: 8px 0 6px 0; font-weight: 700; color: #FACC15;'>{content}</div>"
                )
        else:
            in_list = False
            escaped = html.escape(stripped)
            formatted_bold = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
            content = format_link(formatted_bold)
            html_lines.append(f"<p style='margin: 0 0 6px 0;'>{content}</p>")

    return "\n".join(html_lines)


@router.post("/chat", response_model=ChatResponse, summary="Endpoint Chat Terintegrasi Frontend JIC Assistant")
async def chat_endpoint(
    payload: ChatRequest,
    service: RAGService = Depends(get_rag_service),
):
    """
    Endpoint khusus yang format responsnya disesuaikan 100% dengan
    desain UI/UX frontend JIC Assistant dan terintegrasi dengan Live Agent Handover.
    """
    query = payload.get_query()
    if not query:
        raise HTTPException(status_code=400, detail="Pertanyaan/pesan tidak boleh kosong.")

    tokens = [k for k in re.findall(r"[a-zA-Z0-9]+", query.lower()) if len(k) >= 3]

    handover_mgr = HandoverManager.get_instance()
    session = handover_mgr.get_or_create_session(payload.session_id)
    session_id = session.session_id

    # 1. Catat pesan pemohon ke riwayat percakapan sesi
    user_msg = handover_mgr.add_message(session_id, sender="user", text=query)
    await handover_mgr.broadcast_to_admins("user_message", {
        "session_id": session_id,
        "message": user_msg,
        "session": session.to_summary()
    })

    try:
        # 2. Jika sesi sedang aktif diambil alih oleh Staf CS
        if session.status == "STAFF_ACTIVE":
            staff_title = session.staff_name or "Petugas PTSP"
            ack_html = (
                f"<div style='background:rgba(34,197,94,0.1); border-left:4px solid #22C55E; padding:10px 14px; border-radius:6px; color:#86EFAC;'>"
                f"<strong>👨‍💼 Terhubung dengan {html.escape(staff_title)}:</strong><br>"
                f"Pesan Anda telah diteruskan langsung ke layar petugas. Mohon tunggu balasan petugas sejenak."
                f"</div>"
            )
            return ChatResponse(
                query=query,
                session_id=session_id,
                handover_status="STAFF_ACTIVE",
                staff_name=session.staff_name,
                tokens=tokens,
                isRelevant=True,
                score=100,
                matchedDoc=MatchedDoc(id="LIVE-AGENT", topic="Pelayanan Langsung Petugas PTSP", sourceDoc="Staf Petugas DPMPTSP"),
                matchedKeywords=[],
                contextSnippet=f"Sesi percakapan diambil alih oleh {staff_title}.",
                finalAnswer=ack_html,
                rawAnswer="Pesan diteruskan ke petugas.",
                sumber=f"Petugas Pelayanan: {staff_title}",
                guardrail_lolos=True,
                guardrail_alasan=None,
                rerank_info="Eskalasi Human-in-the-Loop Aktif (Live Agent Handover)",
            )

        # 3. Jika pemohon sedang menunggu dalam antrean staf
        if session.status == "WAITING_STAFF" and not payload.is_handover_request:
            waiting_html = (
                f"<div style='background:rgba(245,158,11,0.12); border-left:4px solid #F59E0B; padding:10px 14px; border-radius:6px; color:#FDE68A;'>"
                f"<strong>⏳ Sedang dalam Antrean Staf CS:</strong><br>"
                f"Pesan Anda telah ditambahkan. Petugas pelayanan kami akan segera bergabung dan membalas pesan Anda."
                f"</div>"
            )
            return ChatResponse(
                query=query,
                session_id=session_id,
                handover_status="WAITING_STAFF",
                tokens=tokens,
                isRelevant=True,
                score=50,
                matchedDoc=None,
                matchedKeywords=[],
                contextSnippet="Pemohon berada dalam antrean bantuan staf CS.",
                finalAnswer=waiting_html,
                rawAnswer="Menunggu petugas.",
                sumber="Antrean Bantuan Staf",
                guardrail_lolos=True,
                guardrail_alasan=None,
                rerank_info="Antrean Eskalasi Staf",
            )

        # 4. Deteksi apakah pesan ini memicu Handover ke CS (kata kunci atau tombol klik)
        if payload.is_handover_request or is_handover_intent(query):
            session = handover_mgr.request_handover(session_id, reason=f"Permintaan pemohon: '{query}'")
            await handover_mgr.broadcast_to_admins("handover_requested", session.to_detail())

            escalation_text = (
                "Permintaan bantuan Anda telah kami terima. "
                "Saya sedang menyambungkan Anda dengan Petugas Pelayanan DPMPTSP. "
                "Mohon tunggu sejenak, petugas kami akan segera bergabung dalam obrolan ini..."
            )
            bot_msg = handover_mgr.add_message(session_id, sender="bot", text=escalation_text)
            escalation_html = f"""
            <div style="background:rgba(247,148,29,0.15); border-left:4px solid #F7941D; padding:12px 14px; border-radius:6px; color:#FDE047;">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                    <span style="font-size:1.2rem;">👨‍💼</span>
                    <strong style="color:#FFFFFF;">Menghubungkan ke Petugas Pelayanan PTSP...</strong>
                </div>
                <p style="margin:0 0 8px 0; color:#E2E8F0;">{escalation_text}</p>
                <div style="display:inline-flex; align-items:center; gap:6px; font-size:0.75rem; background:rgba(247,148,29,0.25); color:#FCD34D; padding:3px 8px; border-radius:12px;">
                    <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#F59E0B;"></span>
                    Menunggu respon staf di dashboard...
                </div>
            </div>
            """
            return ChatResponse(
                query=query,
                session_id=session_id,
                handover_status="WAITING_STAFF",
                tokens=tokens,
                isRelevant=True,
                score=100,
                matchedDoc=None,
                matchedKeywords=[],
                contextSnippet="Permintaan eskalasi staf berhasil dikirim ke antrean dashboard.",
                finalAnswer=escalation_html,
                rawAnswer=escalation_text,
                sumber="Sistem Antrean Layanan Staf",
                guardrail_lolos=True,
                guardrail_alasan=None,
                rerank_info="Deteksi Intent Eskalasi CS -> Mengirim Notifikasi ke Staf",
            )

        # 5. Jalankan Pipeline RAG Normal (BOT_ACTIVE)
        jawaban, sumber_teks, chunks, lolos, alasan = service.tanya(
            pertanyaan=query,
            topk=payload.topk,
            jumlah_chunk=payload.jumlah_chunk,
            jumlah_tetangga=payload.jumlah_tetangga,
            debug=payload.debug,
            endpoint="/api/chat",
        )

        # Kasus Guardrail Mencegat Pertanyaan
        if not lolos:
            final_html = f"""
            <div style="background:#FEF2F2; border-left:4px solid #DC2626; padding:10px 14px; border-radius:6px; color:#991B1B;">
                <strong>🛡️ Pemberitahuan Keamanan:</strong><br>
                {html.escape(jawaban)}
            </div>
            """
            handover_mgr.add_message(session_id, sender="bot", text=jawaban, meta={"guardrail": False, "alasan": alasan})
            return ChatResponse(
                query=query,
                session_id=session_id,
                handover_status="BOT_ACTIVE",
                tokens=tokens,
                isRelevant=False,
                score=0,
                matchedDoc=None,
                matchedKeywords=[],
                contextSnippet=f"Dicegat oleh Guardrail Sistem: {alasan}",
                finalAnswer=final_html,
                rawAnswer=jawaban,
                sumber="Guardrail Keamanan",
                guardrail_lolos=False,
                guardrail_alasan=alasan,
            )

        # Kasus Lolos Guardrail: Analisis Dokumen RAG
        is_relevant = bool(chunks)
        matched_doc = None
        matched_keywords = []
        context_snippet = "Tidak ada dokumen relevan."
        score = 85 if is_relevant else 10

        if is_relevant and len(chunks) > 0:
            top_chunk = chunks[0]
            chunk_id = top_chunk.get("chunk_id", "DOC-JAKEVO")
            file_name = top_chunk.get("file", "Dokumen Layanan JAKEVO")

            dist = top_chunk.get("distance")
            if dist is not None:
                score = max(15, min(99, int((1.0 - (dist / 1.5)) * 100)))

            matched_doc = MatchedDoc(
                id=chunk_id,
                topic=str(file_name).replace(".txt", "").replace(".pdf", "").replace("_", " "),
                sourceDoc=f"{file_name} (Basis Data Resmi JAKEVO)",
            )
            context_snippet = top_chunk.get("teks", "")
            matched_keywords = [t for t in tokens if t in context_snippet.lower()][:5]

        final_html = text_to_html(jawaban)

        # Jika skor relevansi rendah atau informasi tidak ditemukan di dokumen,
        # berikan tombol opsi eskalasi ke staf CS
        is_low_relevance = score < 45 or not is_relevant or "tidak menemukan informasi" in jawaban.lower()
        if is_low_relevance:
            final_html += """
            <div style="margin-top: 14px; padding: 10px 12px; background: rgba(30, 41, 59, 0.7); border: 1px dashed rgba(247, 148, 29, 0.5); border-radius: 8px;">
                <p style="margin: 0 0 6px 0; font-size: 0.8rem; color: #cbd5e1;">Informasi yang dicari belum lengkap atau butuh konfirmasi langsung?</p>
                <button type="button" class="btn-request-cs-handover" onclick="window.requestHandoverToCS && window.requestHandoverToCS('Bantuan dokumen tidak ditemukan')" style="background: linear-gradient(135deg, #F7941D 0%, #EA580C 100%); color: #FFFFFF; border: none; border-radius: 6px; padding: 6px 12px; font-weight: 700; font-size: 0.76rem; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 2px 6px rgba(247,148,29,0.3);">
                    👨‍💼 Sambungkan ke Petugas PTSP
                </button>
            </div>
            """

        # Simpan ke riwayat sesi dan broadcast ke dashboard admin
        handover_mgr.add_message(
            session_id,
            sender="bot",
            text=jawaban,
            meta={
                "score": score,
                "sumber": sumber_teks,
                "is_relevant": is_relevant,
                "doc_id": matched_doc.id if matched_doc else "DEFAULT-FALLBACK",
                "doc_source": matched_doc.sourceDoc if matched_doc else "Knowledge Base Umum JAKEVO DKI Jakarta",
                "html": text_to_html(jawaban),
            },
        )
        await handover_mgr.broadcast_to_admins("bot_reply", {
            "session_id": session_id,
            "session": session.to_summary()
        })

        return ChatResponse(
            query=query,
            session_id=session_id,
            handover_status="BOT_ACTIVE",
            tokens=tokens,
            isRelevant=is_relevant,
            score=score,
            matchedDoc=matched_doc,
            matchedKeywords=matched_keywords,
            contextSnippet=context_snippet[:250] + ("..." if len(context_snippet) > 250 else ""),
            finalAnswer=final_html,
            rawAnswer=jawaban,
            sumber=sumber_teks,
            guardrail_lolos=True,
            guardrail_alasan=None,
            rerank_info="Hybrid Reranking: Vektor dense ChromaDB dipadukan dengan pemeringkatan leksikal & intent SOP (Top-K)",
        )

    except Exception as e:
        logger.exception(f"Terjadi kesalahan di /api/chat: {e}")
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan di server RAG: {str(e)}")


# --- Endpoint Otentikasi & Manajemen Handover untuk Dashboard Admin ---

ADMIN_ACCOUNTS = {
    "admin1": {
        "password": "admin321",
        "staff_name": "Petugas Pelayanan 1 (admin1)",
        "role": "Petugas CS Senior",
    },
    "admin2": {
        "password": "admin123",
        "staff_name": "Petugas Pelayanan 2 (admin2)",
        "role": "Petugas CS Pelayanan",
    },
}


class AdminLoginPayload(BaseModel):
    username: str
    password: str


@router.post("/handover/login", summary="Login Otentikasi Petugas Admin CS")
async def admin_login(payload: AdminLoginPayload):
    uid = payload.username.strip().lower()
    pw = payload.password.strip()
    account = ADMIN_ACCOUNTS.get(uid)
    if not account or account["password"] != pw:
        logger.warning(f"[Admin Auth] Percobaan login gagal untuk ID: '{uid}'")
        raise HTTPException(status_code=401, detail="ID Petugas atau Kata Sandi salah.")

    logger.info(f"[Admin Auth] Petugas '{uid}' ({account['staff_name']}) berhasil login.")
    return {
        "status": "ok",
        "username": uid,
        "staff_name": account["staff_name"],
        "role": account["role"],
    }


@router.get("/handover/sessions", summary="Daftar Sesi Percakapan Aktif untuk Admin")
async def get_handover_sessions():
    mgr = HandoverManager.get_instance()
    return mgr.get_all_sessions_summary()


@router.get("/handover/session/{session_id}", summary="Detail Sesi Percakapan untuk Admin")
async def get_handover_session_detail(session_id: str):
    mgr = HandoverManager.get_instance()
    detail = mgr.get_session_detail(session_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Sesi tidak ditemukan.")
    return detail


class TakeoverPayload(BaseModel):
    session_id: str
    staff_name: str = "Petugas PTSP"


@router.post("/handover/takeover", summary="Staf Mengambil Alih Sesi Percakapan")
async def takeover_session(payload: TakeoverPayload):
    mgr = HandoverManager.get_instance()
    session = mgr.assign_staff(payload.session_id, staff_name=payload.staff_name)
    await mgr.send_to_client(payload.session_id, "staff_joined", {
        "staff_name": payload.staff_name,
        "message": f"Petugas pelayanan ({payload.staff_name}) telah bergabung dalam obrolan."
    })
    await mgr.broadcast_to_admins("session_updated", session.to_detail())
    return {"status": "ok", "session": session.to_summary()}


class StaffReplyPayload(BaseModel):
    session_id: str
    message: str
    staff_name: str = "Petugas PTSP"


@router.post("/handover/reply", summary="Kirim Pesan Staf ke Pemohon")
async def staff_reply(payload: StaffReplyPayload):
    mgr = HandoverManager.get_instance()
    text = payload.message.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Pesan staf tidak boleh kosong.")

    msg = mgr.add_message(payload.session_id, sender="staff", text=text, meta={"staff_name": payload.staff_name})
    await mgr.send_to_client(payload.session_id, "staff_message", {
        "staff_name": payload.staff_name,
        "text": text,
        "timestamp": msg["timestamp"]
    })
    session = mgr.get_or_create_session(payload.session_id)
    await mgr.broadcast_to_admins("message_added", {
        "session_id": payload.session_id,
        "message": msg,
        "session": session.to_summary()
    })
    return {"status": "ok", "message": msg}


class ResolvePayload(BaseModel):
    session_id: str


@router.post("/handover/resolve", summary="Selesaikan Sesi dan Kembalikan ke Bot")
async def resolve_session(payload: ResolvePayload):
    mgr = HandoverManager.get_instance()
    session = mgr.resolve_session(payload.session_id)
    await mgr.send_to_client(payload.session_id, "session_resolved", {
        "message": "Sesi bantuan staf telah selesai. Chatbot JAKEVO kembali siap membantu."
    })
    await mgr.broadcast_to_admins("session_updated", session.to_detail())
    return {"status": "ok", "session": session.to_summary()}


@router.post("/tanya", response_model=TanyaResponse, summary="Tanya Jawab RAG (Standar)")
@router.post("/ask", response_model=TanyaResponse, summary="Alias endpoint Tanya Jawab")
async def tanya_jawab_endpoint(
    payload: TanyaRequest,
    service: RAGService = Depends(get_rag_service),
):
    try:
        jawaban, sumber_teks, chunks, lolos, alasan = service.tanya(
            pertanyaan=payload.pertanyaan,
            topk=payload.topk,
            jumlah_chunk=payload.jumlah_chunk,
            jumlah_tetangga=payload.jumlah_tetangga,
            debug=payload.debug,
            endpoint="/rag/tanya",
        )
        return TanyaResponse(
            pertanyaan=payload.pertanyaan,
            jawaban=jawaban,
            sumber_teks=sumber_teks,
            chunks=chunks,
            guardrail_lolos=lolos,
            guardrail_alasan=alasan,
        )
    except Exception as e:
        logger.exception(f"Terjadi kesalahan di /rag/tanya: {e}")
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan saat memproses pertanyaan: {str(e)}")


@router.get("/status", response_model=StatusResponse, summary="Cek status chatbot & ChromaDB")
async def status_endpoint(
    service: RAGService = Depends(get_rag_service),
):
    info = service.get_status()
    return StatusResponse(
        status=info["status"],
        llm=info["llm"],
        model_embedding=info["model_embedding"],
        total_chunk_db=info["total_chunk_db"],
    )
