# ============================================================
# backend/router.py
# Router API FastAPI untuk endpoint tanya jawab RAG & Frontend
# ============================================================

import re
import html
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
        # Cek apakah baris ini adalah judul layanan / sub-bagian baru
        is_section_header = bool(
            re.match(r"^(?:PM1|IZIN\s+|SURAT\s+IZIN|Layanan\s+)", stripped, re.IGNORECASE)
            or (seen_list_items and not match_num and not match_bullet and not is_link_continuation and stripped.endswith(":"))
        )

        if match_num:
            num = int(match_num.group(1))
            in_list = True
            seen_list_items = True
            content = format_link(html.escape(match_num.group(2)))
            html_lines.append(
                f"<div style='margin: 0 0 4px 0; padding-left: 22px; text-indent: -22px;'>"
                f"<strong>{num}.</strong> {content}</div>"
            )
        elif in_list and is_link_continuation and html_lines and html_lines[-1].endswith("</div>"):
            content = format_link(html.escape(stripped))
            html_lines[-1] = html_lines[-1][:-6] + f"{content}</div>"
        elif match_bullet:
            in_list = False
            content = format_link(html.escape(match_bullet.group(1)))
            html_lines.append(f"<p style='margin: 0 0 4px 0;'>• {content}</p>")
        elif is_section_header or (in_list and not match_num and not is_link_continuation):
            in_list = False
            content = format_link(html.escape(stripped))
            if seen_list_items:
                html_lines.append(
                    f"<div style='margin: 12px 0 6px 0; padding-top: 8px; border-top: 1px dashed #CBD5E1; font-weight: 700; color: #0F172A;'>{content}</div>"
                )
            else:
                html_lines.append(
                    f"<div style='margin: 8px 0 6px 0; font-weight: 700; color: #0F172A;'>{content}</div>"
                )
        else:
            in_list = False
            content = format_link(html.escape(stripped))
            html_lines.append(f"<p style='margin: 0 0 6px 0;'>{content}</p>")

    return "\n".join(html_lines)


@router.post("/chat", response_model=ChatResponse, summary="Endpoint Chat Terintegrasi Frontend JIC Assistant")
async def chat_endpoint(
    payload: ChatRequest,
    service: RAGService = Depends(get_rag_service),
):
    """
    Endpoint khusus yang format responsnya disesuaikan 100% dengan
    desain UI/UX frontend JIC Assistant (Inspector RAG, Score Bar, Step-by-Step, & Sumber).
    """
    query = payload.get_query()
    if not query:
        raise HTTPException(status_code=400, detail="Pertanyaan/pesan tidak boleh kosong.")

    tokens = [k for k in re.findall(r"[a-zA-Z0-9]+", query.lower()) if len(k) >= 3]

    try:
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
            return ChatResponse(
                query=query,
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

        return ChatResponse(
            query=query,
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
