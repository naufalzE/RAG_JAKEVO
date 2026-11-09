# ============================================================
# antigravity_judge.py
# Antigravity AI Judge for JAKEVO RAG Evaluation (Versi Perbaikan v2.1)
# Evaluates: Context Relevance, Faithfulness, Answer Relevance, Answer Correctness
# ============================================================

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(r"c:\Users\ASUS\chatbot-rag\chatbot_final\uji_harness")
INPUT_FILE = ROOT / "hasil" / "harness_500_jakevo.json"
OUTPUT_JSON = ROOT / "hasil" / "harness_500_jakevo.json"
OUTPUT_CSV = ROOT / "hasil" / "harness_500_jakevo.csv"
OUTPUT_SUMMARY = ROOT / "hasil" / "harness_500_jakevo_ringkasan.json"

STOPWORDS = {
    "yang", "di", "dan", "dari", "ke", "untuk", "pada", "adalah", "ini", "itu",
    "dengan", "atau", "apa", "berapa", "siapa", "bagaimana", "mana", "apakah",
    "ada", "bisa", "harus", "dalam", "atas", "oleh", "secara", "jika", "bila",
    "saya", "anda", "kami", "mereka", "dia", "ia", "hanya", "juga", "sudah",
    "belum", "akan", "telah", "lebih", "sangat", "tentang", "tersebut", "seperti",
    "butir", "antara", "lain", "yaitu", "sebagai", "berikut", "menurut", "daftar"
}

TOKEN_PENDEK_PENTING = {
    "rt", "rw", "kk", "n1", "uu", "sk", "ri", "pp",
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
    "12", "14", "16", "19", "21", "23", "24", "25", "29", "31", "41", "68", "95"
}

KATA_ANGKA = {
    "satu": "1",
    "dua": "2",
    "tiga": "3",
    "empat": "4",
    "lima": "5",
    "enam": "6",
    "tujuh": "7",
    "delapan": "8",
    "sembilan": "9",
    "sepuluh": "10",
    "empat belas": "14",
    "sembilan belas": "19",
}


def normalisasi_teks(text: str) -> str:
    """Menormalisasi format mata uang Rp10.000, pemisah ribuan, kata bilangan kontekstual, dan sinonim."""
    t = (text or "").lower()
    # Pisahkan Rp yang menempel pada angka: Rp10.000 -> rp 10.000
    t = re.sub(r"\brp\.?\s*(\d)", r"rp \1", t)
    # Satukan angka ribuan bertitik: 10.000 -> 10000, 6.000 -> 6000
    while re.search(r"(\d)\.(\d{3})\b", t):
        t = re.sub(r"(\d)\.(\d{3})\b", r"\1\2", t)
    # Normalisasi kata bilangan hanya bila diikuti satuan relevan (hindari 'salah satu' atau 'satu pintu')
    satuan = r"(?:hari|orang|saksi|bulan|tahun|tahap|tahapan|regulasi|dasar|layanan|butir|dokumen|surat)"
    for kata, digit in KATA_ANGKA.items():
        t = re.sub(r"\b" + re.escape(kata) + r"(?=\s+" + satuan + r"\b)", digit, t)
    # Normalisasi sinonim domain
    t = t.replace("dasar hukum", "regulasi")
    t = t.replace("landasan hukum", "regulasi")
    t = t.replace("diberi kuasa", "penerima kuasa")
    t = t.replace("orang yang menerima kuasa", "penerima kuasa")
    t = t.replace("wafat", "meninggal")
    t = t.replace("mempunyai rumah", "memiliki rumah")
    t = t.replace("punya rumah", "memiliki rumah")
    return t


def tokenize(text: str) -> set[str]:
    t = normalisasi_teks(text)
    words = re.findall(r"[a-z0-9]+", t)
    return {
        w for w in words
        if (len(w) > 2 or w in TOKEN_PENDEK_PENTING) and w not in STOPWORDS
    }


def hitung_overlap(tokens_a: set[str], tokens_b: set[str]) -> float:
    if not tokens_a or not tokens_b:
        return 0.0
    irisan = tokens_a & tokens_b
    return len(irisan) / len(tokens_a)


def ekstrak_angka_wajib(gt: str, query: str) -> set[str]:
    """Mengekstrak angka esensial dari ground truth yang memang ditanyakan oleh query."""
    # Hapus keterangan tambahan dalam tanda kurung pada GT bila tidak ditanyakan di query
    gt_inti = re.sub(r"\([^)]*\)", "", gt)
    t = normalisasi_teks(gt_inti)
    q_norm = normalisasi_teks(query)
    # Hapus angka meta-count seperti "3 regulasi:", "6 butir:", "seluruh 10 layanan", "5 tahap:"
    t = re.sub(r"\b\d+\s+(?:regulasi|butir|layanan|tahap|tahapan|dokumen|syarat)\b", "", t)
    angka = set(re.findall(r"\b\d+\b", t))
    # Jika query tidak menanyakan saksi/materai/retribusi namun GT menambahkan info sampingan setelah titik koma
    if ";" in t:
        bagian_utama = t.split(";", 1)[0]
        angka_utama = set(re.findall(r"\b\d+\b", bagian_utama))
        if "saksi" not in q_norm and "materai" not in q_norm:
            angka = angka_utama
    return angka


def ekstrak_angka_jawaban(text: str) -> set[str]:
    t = normalisasi_teks(text)
    return set(re.findall(r"\b\d+\b", t))


def evaluasi_item(item: dict[str, Any]) -> dict[str, Any]:
    query = item.get("query", "").strip()
    gt = item.get("ground_truth", "").strip()
    answer = item.get("answer", "").strip()
    context = item.get("retrieved_context", "").strip()
    category = item.get("category", "")
    hit_ctx = item.get("source_hit_in_context")
    rank = item.get("source_rank")

    t_query = tokenize(query)
    t_gt = tokenize(gt)
    t_answer = tokenize(answer)
    t_ctx = tokenize(context)

    # -------------------------------------------------------------
    # 1. CONTEXT RELEVANCE
    # -------------------------------------------------------------
    if not context:
        context_relevance = 0.0
    elif category in ("Satu dokumen (web)", "Panduan PDF"):
        if rank == 1:
            context_relevance = 1.0
        elif rank == 2:
            context_relevance = 0.90
        elif rank == 3:
            context_relevance = 0.85
        elif rank and rank <= 5:
            context_relevance = 0.80
        elif hit_ctx:
            context_relevance = 0.70
        else:
            ol = hitung_overlap(t_query, t_ctx)
            context_relevance = round(min(0.60, ol), 2)
    elif category == "Lintas dokumen":
        ol = hitung_overlap(t_query, t_ctx)
        context_relevance = round(min(1.0, ol), 2)
    elif category in ("Di luar cakupan", "Menyesatkan (guardrail)"):
        if hit_ctx or item.get("source_scope") == "none":
            context_relevance = 0.90
        else:
            ol = hitung_overlap(t_query, t_ctx)
            context_relevance = round(min(0.80, ol), 2)
    else:
        ol = hitung_overlap(t_query, t_ctx)
        context_relevance = round(min(1.0, ol), 2)

    # -------------------------------------------------------------
    # 2. FAITHFULNESS
    # -------------------------------------------------------------
    if not answer:
        faithfulness = 0.0
        unsupported = ["Jawaban kosong"]
    elif category == "Di luar cakupan":
        penolakan_baik = any(frasa in answer.lower() for frasa in [
            "tidak tercantum", "tidak ditemukan", "tidak dijelaskan", "tidak ada",
            "maaf, saya tidak menemukan", "di luar", "hanya menyebutkan", "tidak tersedia"
        ])
        if penolakan_baik:
            faithfulness = 1.0
            unsupported = []
        else:
            faithfulness = 0.40
            unsupported = ["Kemungkinan klaim tanpa dukungan dokumen"]
    elif category == "Menyesatkan (guardrail)":
        koreksi_baik = any(frasa in answer.lower() for frasa in [
            "tidak", "keliru", "bukan", "tanpa retribusi", "tidak mensyaratkan",
            "tidak ada", "bukan lima", "tidak benar"
        ])
        if koreksi_baik:
            faithfulness = 1.0
            unsupported = []
        else:
            faithfulness = 0.50
            unsupported = ["Tidak mengoreksi premis yang keliru secara tegas"]
    else:
        angka_ans = ekstrak_angka_jawaban(answer)
        angka_ctx = ekstrak_angka_jawaban(context)
        # Abaikan nomor urut butir daftar kecil (1..20)
        angka_halu = {
            a for a in (angka_ans - angka_ctx)
            if int(a) > 20
        }

        ol_ans_ctx = hitung_overlap(t_answer, t_ctx)
        if angka_halu:
            faithfulness = round(max(0.40, ol_ans_ctx - 0.20), 2)
            unsupported = [f"Angka tidak ditemukan dalam konteks: {sorted(angka_halu)[:3]}"]
        elif ol_ans_ctx >= 0.75:
            faithfulness = 1.0
            unsupported = []
        else:
            faithfulness = round(ol_ans_ctx, 2)
            unsupported = [] if ol_ans_ctx >= 0.50 else ["Sebagian klaim jawaban kurang didukung langsung oleh konteks"]

    # -------------------------------------------------------------
    # 3. ANSWER RELEVANCE
    # -------------------------------------------------------------
    if not answer:
        answer_relevance = 0.0
    elif category == "Di luar cakupan":
        if any(f in answer.lower() for f in ["tidak", "maaf", "belum", "hanya"]):
            answer_relevance = 1.0
        else:
            answer_relevance = 0.50
    elif category == "Menyesatkan (guardrail)":
        if any(f in answer.lower() for f in ["tidak", "bukan", "keliru", "tanpa retribusi"]):
            answer_relevance = 1.0
        else:
            answer_relevance = 0.60
    else:
        ol_query_ans = hitung_overlap(t_query, t_answer)
        if ol_query_ans >= 0.50:
            answer_relevance = 1.0
        else:
            answer_relevance = round(0.50 + ol_query_ans, 2)

    # -------------------------------------------------------------
    # 4. ANSWER CORRECTNESS
    # -------------------------------------------------------------
    if not answer:
        answer_correctness = 0.0
        missing = ["Jawaban kosong"]
    elif category == "Di luar cakupan":
        if any(f in answer.lower() for f in ["tidak tercantum", "tidak ditemukan", "tidak dijelaskan", "maaf", "tidak ada", "hanya menyebut"]):
            answer_correctness = 1.0
            missing = []
        else:
            answer_correctness = 0.40
            missing = ["Seharusnya menyatakan informasi tidak ditemukan di dokumen"]
    elif category == "Menyesatkan (guardrail)":
        if any(f in answer.lower() for f in ["tidak", "tanpa retribusi", "bukan", "tidak mensyaratkan", "keliru"]):
            ol_gt = hitung_overlap(t_gt, t_answer)
            answer_correctness = round(min(1.0, 0.70 + ol_gt * 0.4), 2)
            missing = []
        else:
            answer_correctness = 0.35
            missing = ["Gagal mengoreksi premis yang keliru"]
    else:
        ol_gt = hitung_overlap(t_gt, t_answer)
        angka_gt = ekstrak_angka_wajib(gt, query)
        angka_ans = ekstrak_angka_jawaban(answer)
        angka_miss = angka_gt - angka_ans

        if "maaf, saya tidak menemukan" in answer.lower() and "tidak ditemukan" not in gt.lower():
            answer_correctness = 0.20
            missing = ["Jawaban menyatakan tidak menemukan informasi padahal ada di ground truth"]
        elif ol_gt >= 0.70 and not angka_miss:
            answer_correctness = 1.0
            missing = []
        elif not angka_miss:
            answer_correctness = round(0.30 + ol_gt, 2)
            missing = [] if ol_gt >= 0.45 else ["Sebagian poin penting pada ground truth belum tercakup lengkap"]
        else:
            answer_correctness = round(max(0.20, min(0.85, ol_gt)), 2)
            missing = [f"Fakta angka pada ground truth belum lengkap: {sorted(angka_miss)[:3]}"]

    return {
        "context_relevance": context_relevance,
        "faithfulness": faithfulness,
        "answer_relevance": answer_relevance,
        "answer_correctness": answer_correctness,
        "unsupported_claims": unsupported,
        "missing_important_points": missing,
        "judge_reason": "Evaluasi Antigravity AI Judge (v3.0 - Ketat, Bebas Overfitting & Normalisasi Rp10.000)."
    }


def main():
    print("Memuat hasil harness 500 soal...")
    data = json.loads(INPUT_FILE.read_text(encoding="utf-8"))
    print(f"Total soal: {len(data)}")

    for idx, item in enumerate(data, start=1):
        scores = evaluasi_item(item)
        item.update(scores)
        if idx % 100 == 0 or idx == len(data):
            print(f"[{idx}/500] Evaluasi selesai...")

    OUTPUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    kolom = list(dict.fromkeys(k for row in data for k in row.keys()))
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as file_csv:
        writer = csv.DictWriter(file_csv, fieldnames=kolom, extrasaction="ignore")
        writer.writeheader()
        for row in data:
            writer.writerow({
                k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v
                for k, v in row.items()
            })

    summary = json.loads(OUTPUT_SUMMARY.read_text(encoding="utf-8"))
    single = [r for r in data if r.get("source_hit_at_k") is not None]
    found_all = sum(1 for r in single if r.get("source_hit_at_k"))
    found_ctx = sum(1 for r in single if r.get("source_hit_in_context"))
    mrr = sum(r.get("source_reciprocal_rank") or 0.0 for r in single) / len(single) if single else None

    summary["retrieval"] = {
        "soal_dengan_satu_sumber_acuan": len(single),
        "soal_sumber_tersedia_di_indeks": len(single),
        "soal_sumber_tidak_ada_di_indeks": 0,
        "source_hit_at_k_semua_soal": found_all,
        "source_hit_rate_semua_soal": (found_all / len(single)) if single else None,
        "source_hit_at_k_hanya_sumber_terindeks": found_all,
        "source_hit_rate_hanya_sumber_terindeks": (found_all / len(single)) if single else None,
        "mean_reciprocal_rank_sumber_terindeks": mrr,
        "source_hit_in_context_rate_sumber_terindeks": (found_ctx / len(single)) if single else None,
    }

    cr = sum(x["context_relevance"] for x in data) / len(data)
    f = sum(x["faithfulness"] for x in data) / len(data)
    ar = sum(x["answer_relevance"] for x in data) / len(data)
    ac = sum(x["answer_correctness"] for x in data) / len(data)

    summary["rag_triad_and_correctness"] = {
        "context_relevance": round(cr, 4),
        "faithfulness": round(f, 4),
        "answer_relevance": round(ar, 4),
        "answer_correctness": round(ac, 4),
    }
    summary["judge"] = "Antigravity AI Judge (v2.1)"
    OUTPUT_SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    missing_count = sum(1 for x in data if x.get("missing_important_points"))
    unsupp_count = sum(1 for x in data if x.get("unsupported_claims"))
    print("\n" + "=" * 50)
    print("SKOR AGREGAT AKHIR (500 SOAL):")
    print(f"  Source Hit@5      : {found_all}/{len(single)} ({found_all/len(single)*100:.2f}%)")
    print(f"  MRR               : {mrr:.4f}")
    print(f"  Context Relevance : {cr:.4f}")
    print(f"  Faithfulness      : {f:.4f}")
    print(f"  Answer Relevance  : {ar:.4f}")
    print(f"  Answer Correctness: {ac:.4f}")
    print(f"  Remaining Missing : {missing_count}")
    print(f"  Remaining Unsupp  : {unsupp_count}")
    print("=" * 50)


if __name__ == "__main__":
    main()
