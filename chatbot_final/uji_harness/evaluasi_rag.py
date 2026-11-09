# ============================================================
# Harness Evaluasi RAG JAKEVO
# Menguji retrieval, RAG Triad, dan answer correctness.
# Jalankan dari root proyek chatbotv2:
#   python uji_harness/evaluasi_rag.py --mode full
# ============================================================

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


# Pastikan folder proyek chatbotv2 ada di sys.path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DATASET_PATH = Path(__file__).resolve().parent / "golden_dataset_500.json"
OUTPUT_DIR = Path(__file__).resolve().parent / "hasil"


def baca_env_manual(nama: str, default: str | None = None) -> str | None:
    """Membaca variabel dari environment atau .env tanpa mencetak nilainya."""
    nilai = os.environ.get(nama)
    if nilai is not None and nilai.strip():
        return nilai.strip().strip('"').strip("'")

    path_env = PROJECT_ROOT / ".env"
    if not path_env.is_file():
        return default

    for baris in path_env.read_text(encoding="utf-8").splitlines():
        baris = baris.strip()
        if not baris or baris.startswith("#") or "=" not in baris:
            continue
        kunci, isi = baris.split("=", 1)
        if kunci.strip() == nama:
            isi = isi.strip()
            if " #" in isi:
                isi = isi.split(" #", 1)[0].rstrip()
            return isi.strip('"').strip("'") or default

    return default


def muat_dataset(path: Path = DATASET_PATH) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Golden Dataset tidak ditemukan: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError("Golden Dataset harus berupa list JSON yang tidak kosong.")

    wajib = {"id", "query", "ground_truth", "category", "source_reference"}
    for nomor, item in enumerate(data, start=1):
        kurang = wajib - set(item)
        if kurang:
            raise ValueError(f"Baris dataset {nomor} kehilangan kolom: {sorted(kurang)}")
        if not str(item.get("query", "")).strip():
            raise ValueError(f"Query kosong pada item ID {item.get('id')}")
        if not str(item.get("ground_truth", "")).strip():
            raise ValueError(f"Ground truth kosong pada item ID {item.get('id')}")

    return data


def nama_file_metadata(metadata: dict[str, Any]) -> str:
    nama = (metadata or {}).get("nama_file") or ""
    if nama:
        return Path(str(nama)).name.lower()
    kode = (metadata or {}).get("dokumen") or ""
    return str(kode).lower()


def nama_sumber_expected(nama: str) -> str:
    return Path(str(nama)).name.strip().lower()


def sumber_cocok(metadata: dict[str, Any], expected_sources: list[str]) -> bool:
    actual = nama_file_metadata(metadata)
    if not actual:
        return False

    for expected in expected_sources:
        expected_name = nama_sumber_expected(expected)
        expected_stem = Path(expected_name).stem
        if actual == expected_name or actual == expected_stem:
            return True
    return False


def ringkas_sumber(chunks: list[dict[str, Any]]) -> list[str]:
    hasil: list[str] = []
    for chunk in chunks:
        metadata = chunk.get("metadata") or {}
        nama = (metadata.get("nama_file") or "").strip()
        if not nama:
            nama = (metadata.get("dokumen") or "").strip()
        if nama and nama not in hasil:
            hasil.append(nama)
    return hasil


def metrik_sumber(
    item: dict[str, Any],
    hasil_topk: list[dict[str, Any]],
    hasil_konteks: list[dict[str, Any]],
) -> dict[str, Any]:
    """Metrik berbasis sumber acuan; tidak memaksakan sumber untuk corpus/di luar cakupan."""
    scope = item.get("source_scope", "none")
    expected = item.get("expected_sources") or []

    if scope != "single_source" or not expected:
        return {
            "expected_source_in_index": None,
            "source_hit_at_k": None,
            "source_hit_in_context": None,
            "source_rank": None,
            "source_reciprocal_rank": None,
        }

    rank = None
    for posisi, chunk in enumerate(hasil_topk, start=1):
        if sumber_cocok(chunk.get("metadata") or {}, expected):
            rank = posisi
            break

    hit_context = any(
        sumber_cocok(chunk.get("metadata") or {}, expected)
        for chunk in hasil_konteks
    )

    return {
        "expected_source_in_index": None,  # diisi setelah cakupan indeks diperiksa
        "source_hit_at_k": rank is not None,
        "source_hit_in_context": hit_context,
        "source_rank": rank,
        "source_reciprocal_rank": (1.0 / rank) if rank else 0.0,
    }


def cakupan_indeks(collection) -> dict[str, Any]:
    data = collection.get(include=["metadatas"])
    counts: Counter[str] = Counter()
    for metadata in data.get("metadatas", []) or []:
        nama = (metadata or {}).get("nama_file") or ""
        if nama:
            counts[Path(str(nama)).name] += 1

    return {
        "jumlah_chunk": collection.count(),
        "jumlah_dokumen": len(counts),
        "chunk_per_dokumen": dict(sorted(counts.items())),
        "nama_file_terindeks": sorted(counts),
    }


def daftar_sumber_diharapkan(dataset: list[dict[str, Any]]) -> list[str]:
    daftar: set[str] = set()
    for item in dataset:
        if item.get("source_scope") == "single_source":
            daftar.update(item.get("expected_sources") or [])
        elif item.get("source_scope") == "service_corpus":
            daftar.update(
                (item.get("context_reference") or {}).get("files", [])
            )
    return sorted(daftar, key=str.lower)


def hitung_cakupan_sumber(
    dataset: list[dict[str, Any]],
    coverage: dict[str, Any],
) -> dict[str, Any]:
    indexed = {nama.lower() for nama in coverage["nama_file_terindeks"]}
    expected = daftar_sumber_diharapkan(dataset)
    present = [nama for nama in expected if nama.lower() in indexed]
    missing = [nama for nama in expected if nama.lower() not in indexed]
    return {
        "expected_files": len(expected),
        "indexed_files": len(present),
        "missing_files": len(missing),
        "present": present,
        "missing": missing,
    }


class LLMJudge:
    """LLM judge terpisah; mendukung Gemini dan DeepSeek."""

    def __init__(self) -> None:
        self.provider = (baca_env_manual("JUDGE_PROVIDER") or "").lower().strip()
        if not self.provider:
            generator_provider = (
                baca_env_manual("LLM_PROVIDER")
                or baca_env_manual("PROVIDER_LLM", "gemini")
                or "gemini"
            ).lower()
            # Utamakan provider berbeda dari generator bila API key tersedia.
            if generator_provider != "gemini" and baca_env_manual("GEMINI_API_KEY"):
                self.provider = "gemini"
            elif generator_provider != "deepseek" and baca_env_manual("DEEPSEEK_API_KEY"):
                self.provider = "deepseek"
            elif baca_env_manual("GEMINI_API_KEY"):
                self.provider = "gemini"
            elif baca_env_manual("DEEPSEEK_API_KEY"):
                self.provider = "deepseek"
            else:
                self.provider = generator_provider

        self.api_key = baca_env_manual("JUDGE_API_KEY")
        if not self.api_key:
            if self.provider == "gemini":
                self.api_key = baca_env_manual("GEMINI_API_KEY") or baca_env_manual("GOOGLE_API_KEY")
            elif self.provider == "deepseek":
                self.api_key = baca_env_manual("DEEPSEEK_API_KEY") or baca_env_manual("LLM_API_KEY")

        if self.provider == "gemini":
            self.model_name = baca_env_manual("JUDGE_MODEL") or baca_env_manual("GEMINI_MODEL", "gemini-2.5-flash")
            if not self.api_key:
                raise RuntimeError("API key Judge Gemini tidak ditemukan. Isi JUDGE_API_KEY atau GEMINI_API_KEY di .env.")
            try:
                from google import genai
            except ImportError as error:
                raise RuntimeError("Paket google-genai belum terpasang. Jalankan pip install -r uji_harness/requirements-harness.txt.") from error
            self.client = genai.Client(api_key=self.api_key)
            self.http_client = None

        elif self.provider == "deepseek":
            self.model_name = baca_env_manual("JUDGE_MODEL") or baca_env_manual("DEEPSEEK_MODEL", "deepseek-chat")
            if not self.api_key:
                raise RuntimeError("API key Judge DeepSeek tidak ditemukan. Isi JUDGE_API_KEY atau DEEPSEEK_API_KEY di .env.")
            try:
                import httpx
            except ImportError as error:
                raise RuntimeError("Paket httpx belum terpasang. Jalankan pip install -r uji_harness/requirements-harness.txt.") from error
            self.base_url = (baca_env_manual("JUDGE_BASE_URL") or baca_env_manual("DEEPSEEK_BASE_URL") or "https://api.deepseek.com").rstrip("/")
            self.http_client = httpx.Client(timeout=float(baca_env_manual("JUDGE_TIMEOUT", "90")))
            self.client = None
        else:
            raise ValueError("JUDGE_PROVIDER hanya mendukung 'gemini' atau 'deepseek'.")

        self.timeout = int(baca_env_manual("JUDGE_TIMEOUT", "90") or 90)

    def _generate(self, prompt: str) -> str:
        last_error = None
        for attempt in range(4):
            try:
                if self.provider == "gemini":
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                    )
                    return (getattr(response, "text", None) or "").strip()

                response = self.http_client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model_name,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0,
                        "response_format": {"type": "json_object"},
                        "stream": False,
                    },
                )
                response.raise_for_status()
                return str(response.json()["choices"][0]["message"]["content"]).strip()
            except Exception as e:
                last_error = e
                if attempt < 3:
                    time.sleep(2 * (attempt + 1))
        raise last_error

    @staticmethod
    def _parse_json(teks: str) -> dict[str, Any]:
        teks = teks.strip()
        teks = re.sub(r"^```(?:json)?\s*", "", teks, flags=re.IGNORECASE)
        teks = re.sub(r"\s*```$", "", teks)
        try:
            data = json.loads(teks)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", teks, flags=re.DOTALL)
            if not match:
                raise ValueError(f"Respons Judge bukan JSON: {teks[:300]}")
            data = json.loads(match.group(0))
        if not isinstance(data, dict):
            raise ValueError("JSON Judge harus berupa object.")
        return data

    @staticmethod
    def _normalisasi_skor(value: Any) -> float | None:
        if value is None or value == "N/A":
            return None
        try:
            skor = float(value)
        except (TypeError, ValueError):
            return None
        return max(0.0, min(1.0, skor))

    def nilai(
        self,
        query: str,
        context: str,
        answer: str | None,
        ground_truth: str,
        category: str,
    ) -> dict[str, Any]:
        if answer is None:
            instruksi_mode = "MODE RETRIEVAL-ONLY: nilai hanya context_relevance. Isi metrik lain dengan null."
        else:
            instruksi_mode = "MODE FULL: nilai keempat metrik yang diminta."

        prompt = f"""Anda adalah evaluator independen untuk sistem Retrieval-Augmented Generation (RAG) berbahasa Indonesia.
Tugas Anda adalah memberi skor objektif dari 0.0 sampai 1.0. Jangan memberi nilai tinggi hanya karena jawaban terdengar lancar.

DEFINISI METRIK:
1. context_relevance: seberapa banyak konteks yang diambil retriever benar-benar relevan dan berguna untuk menjawab query. Nilai 1 berarti konteks sangat relevan; 0 berarti tidak ada konteks berguna.
2. faithfulness: seberapa jauh semua klaim faktual dalam jawaban didukung oleh konteks yang diberikan. Turunkan skor untuk klaim tanpa dukungan, angka/nama/URL yang dikarang, atau kontradiksi. Jawaban penolakan yang tepat dan tidak mengarang dapat bernilai tinggi.
3. answer_relevance: apakah jawaban secara langsung menjawab maksud query, tidak berputar-putar, dan memberi tingkat rincian yang sesuai. Untuk pertanyaan di luar cakupan, penolakan yang tepat tetap relevan.
4. answer_correctness: kesesuaian substansi jawaban dengan ground truth. Makna yang setara boleh diberi nilai tinggi; fakta penting yang hilang atau salah harus menurunkan skor.

ATURAN KHUSUS DATASET:
- Kategori 'Di luar cakupan': jawaban ideal menyatakan informasi tidak tersedia dan tidak mengarang. Jangan menghukum jawaban karena tidak memberi detail yang memang tidak ada.
- Kategori 'Menyesatkan (guardrail)': jawaban ideal mengoreksi premis yang keliru atau menyatakan informasi tidak ditemukan. Jangan ikut membenarkan premis yang salah.
- Kategori lain: bandingkan isi jawaban dengan ground truth dan konteks, bukan kesamaan kata secara kaku.
- Jangan menganggap suatu klaim benar hanya karena ada di ground truth; faithfulness hanya menilai dukungan dari konteks.
- Jika konteks kosong, context_relevance = 0.0. Jika jawaban kosong, faithfulness dan answer_relevance = 0.0 serta answer_correctness = 0.0 pada MODE FULL.

{instruksi_mode}

QUERY:
{query}

KATEGORI:
{category}

GROUND TRUTH:
{ground_truth}

RETRIEVED CONTEXT:
{context if context.strip() else '[KONTEKS KOSONG]'}

JAWABAN CHATBOT:
{answer if answer is not None else '[TIDAK ADA: MODE RETRIEVAL-ONLY]'}

KELUARKAN JSON SAH SAJA, TANPA MARKDOWN, DENGAN FORMAT PERSIS:
{{
  "context_relevance": 0.0,
  "faithfulness": null,
  "answer_relevance": null,
  "answer_correctness": null,
  "unsupported_claims": [],
  "missing_important_points": [],
  "reason": "alasan singkat dalam Bahasa Indonesia"
}}
Gunakan angka 0.0-1.0. Jangan keluarkan skor sebagai persen.
"""

        teks = self._generate(prompt)
        raw = self._parse_json(teks)
        hasil = {
            "context_relevance": self._normalisasi_skor(raw.get("context_relevance")),
            "faithfulness": self._normalisasi_skor(raw.get("faithfulness")),
            "answer_relevance": self._normalisasi_skor(raw.get("answer_relevance")),
            "answer_correctness": self._normalisasi_skor(raw.get("answer_correctness")),
            "unsupported_claims": raw.get("unsupported_claims") or [],
            "missing_important_points": raw.get("missing_important_points") or [],
            "judge_reason": str(raw.get("reason", "")).strip(),
        }
        return hasil

    def close(self) -> None:
        if self.http_client is not None:
            self.http_client.close()


def rata_rata(hasil: list[dict[str, Any]], kunci: str) -> float | None:
    nilai = [item.get(kunci) for item in hasil if isinstance(item.get(kunci), (int, float))]
    if not nilai:
        return None
    return sum(nilai) / len(nilai)


def simpan_hasil(
    hasil: list[dict[str, Any]],
    json_path: Path,
    csv_path: Path,
) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(hasil, ensure_ascii=False, indent=2), encoding="utf-8")

    if not hasil:
        return
    kolom = list(dict.fromkeys(k for row in hasil for k in row.keys()))
    with csv_path.open("w", encoding="utf-8-sig", newline="") as file_csv:
        writer = csv.DictWriter(file_csv, fieldnames=kolom, extrasaction="ignore")
        writer.writeheader()
        for row in hasil:
            writer.writerow({
                k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v
                for k, v in row.items()
            })


def buat_ringkasan(
    hasil: list[dict[str, Any]],
    index_coverage: dict[str, Any],
    file_coverage: dict[str, Any],
    generator_info: str,
    judge_info: str,
    mode: str,
) -> dict[str, Any]:
    jumlah = len(hasil)
    single = [r for r in hasil if r.get("source_hit_at_k") is not None]
    indexed_single = [r for r in single if r.get("expected_source_in_index") is True]
    missing_index_single = [r for r in single if r.get("expected_source_in_index") is False]
    found_all = sum(1 for r in single if r.get("source_hit_at_k"))
    found_indexed = sum(1 for r in indexed_single if r.get("source_hit_at_k"))
    status = Counter(r.get("status", "UNKNOWN") for r in hasil)

    return {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "mode": mode,
        "jumlah_soal_dijalankan": jumlah,
        "status_per_soal": dict(status),
        "retrieval": {
            "soal_dengan_satu_sumber_acuan": len(single),
            "soal_sumber_tersedia_di_indeks": len(indexed_single),
            "soal_sumber_tidak_ada_di_indeks": len(missing_index_single),
            "source_hit_at_k_semua_soal": found_all,
            "source_hit_rate_semua_soal": (found_all / len(single)) if single else None,
            "source_hit_at_k_hanya_sumber_terindeks": found_indexed,
            "source_hit_rate_hanya_sumber_terindeks": (found_indexed / len(indexed_single)) if indexed_single else None,
            "mean_reciprocal_rank_sumber_terindeks": rata_rata(indexed_single, "source_reciprocal_rank"),
            "source_hit_in_context_rate_sumber_terindeks": (
                sum(1 for r in indexed_single if r.get("source_hit_in_context")) / len(indexed_single)
            ) if indexed_single else None,
        },
        "rag_triad_and_correctness": {
            "context_relevance": rata_rata(hasil, "context_relevance"),
            "faithfulness": rata_rata(hasil, "faithfulness"),
            "answer_relevance": rata_rata(hasil, "answer_relevance"),
            "answer_correctness": rata_rata(hasil, "answer_correctness"),
        },
        "index_coverage": index_coverage,
        "expected_source_coverage": file_coverage,
        "generator": generator_info,
        "judge": judge_info,
        "catatan": [
            "Source Hit@k/MRR hanya dihitung untuk soal dengan satu file sumber yang eksplisit.",
            "Untuk soal lintas layanan, relevansi konteks dinilai oleh LLM judge; source hit tunggal tidak dipaksakan.",
            "Nilai LLM-as-a-Judge adalah estimasi otomatis dan sebaiknya diaudit manual pada sampel.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluasi retrieval dan RAG Triad untuk chatbot JAKEVO."
    )
    parser.add_argument("--mode", choices=["retrieval", "full"], default="full",
                        help="retrieval: hanya retrieval + context relevance; full: retrieval + jawaban LLM + semua metrik.")
    parser.add_argument("--dataset", type=str, default=str(DATASET_PATH), help="Path ke file dataset JSON (default: golden_dataset_500.json).")
    parser.add_argument("--topk", type=int, default=5, help="Jumlah chunk hasil semantic search (default: 5).")
    parser.add_argument("--jumlah-chunk", type=int, default=3, help="Jumlah hasil teratas yang diperluas (default: 3).")
    parser.add_argument("--jumlah-tetangga", type=int, default=1, help="Jumlah chunk tetangga per hasil terpilih (default: 1).")
    parser.add_argument("--limit", type=int, default=0, help="Batasi jumlah soal; 0 berarti semua soal.")
    parser.add_argument("--start-id", type=int, default=1, help="ID soal pertama yang dijalankan.")
    parser.add_argument("--end-id", type=int, default=500, help="ID soal terakhir yang dijalankan.")
    parser.add_argument("--ids", type=str, default="", help="ID tertentu, pisahkan koma. Contoh: 1,2,45,87.")
    parser.add_argument("--resume", action="store_true", help="Lanjutkan dari checkpoint file hasil yang sudah ada.")
    parser.add_argument("--skip-judge", action="store_true", help="Lewati LLM judge (skor triad tidak dihitung).")
    parser.add_argument("--delay", type=float, default=0.2, help="Jeda antar-soal dalam detik (default: 0.2).")
    parser.add_argument("--output-prefix", type=str, default="", help="Awalan nama file hasil. Default memakai timestamp.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.topk < 1 or args.jumlah_chunk < 0 or args.jumlah_tetangga < 0:
        raise ValueError("topk harus >=1; jumlah-chunk dan jumlah-tetangga tidak boleh negatif.")

    dataset_path = Path(args.dataset)
    dataset = muat_dataset(dataset_path)
    if args.ids.strip():
        id_pilihan = {int(x.strip()) for x in args.ids.split(",") if x.strip()}
        dataset = [x for x in dataset if int(x["id"]) in id_pilihan]
    else:
        dataset = [
            x for x in dataset
            if args.start_id <= int(x["id"]) <= args.end_id
        ]
    if args.limit > 0:
        dataset = dataset[:args.limit]
    if not dataset:
        raise ValueError("Tidak ada soal yang cocok dengan filter ID/limit.")

    # Import setelah validasi argumen agar --help/dataset-check tidak bergantung model.
    from core.config import settings
    from llm.llm import info_llm, panggil_llm
    from llm.prompt import bangun_prompt
    from retrieval.konteks import susun_konteks, format_sumber
    from retrieval.retriever import retriever
    from retrieval.tetangga import (
        ambil_chunk_tetangga,
        cari_id_tetangga,
        urutkan_id_chunk_teks,
    )
    from storage.database import buka_collection
    from storage.embedding import muat_model

    print("=" * 72)
    print("HARNESS EVALUASI RAG JAKEVO")
    print("Mode                  :", args.mode)
    print("Soal                  :", len(dataset))
    print("Konfigurasi retrieval :", f"topk={args.topk}, jumlah_chunk={args.jumlah_chunk}, tetangga={args.jumlah_tetangga}")
    print("Generator             :", info_llm())

    collection = buka_collection()
    index_coverage = cakupan_indeks(collection)
    file_coverage = hitung_cakupan_sumber(dataset, index_coverage)
    print("Chunk dalam indeks    :", index_coverage["jumlah_chunk"])
    print("Dokumen dalam indeks  :", index_coverage["jumlah_dokumen"])
    print("Sumber acuan terindeks:", f"{file_coverage['indexed_files']}/{file_coverage['expected_files']}")
    if file_coverage["missing"]:
        print("PERINGATAN: file sumber berikut belum ada di indeks:")
        for nama in file_coverage["missing"]:
            print("  -", nama)

    print("Memuat model embedding ...")
    model = muat_model()
    urut = urutkan_id_chunk_teks(collection)

    judge = None
    if not args.skip_judge:
        try:
            judge = LLMJudge()
            judge_info = f"{judge.provider} / {judge.model_name}"
            generator_lower = info_llm().lower()
            if judge_info.lower() in generator_lower:
                print("PERINGATAN: generator dan judge memakai provider/model yang sama; interpretasikan skor dengan hati-hati.")
        except Exception as error:
            raise RuntimeError(
                "LLM judge belum dapat diinisialisasi. Periksa JUDGE_PROVIDER, JUDGE_MODEL, dan API key di .env. "
                "Gunakan --skip-judge untuk menguji retrieval/generator tanpa penilaian otomatis. "
                f"Detail: {error}"
            ) from error
    else:
        judge_info = "disabled"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = args.output_prefix.strip() or f"hasil_harness_{timestamp}"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / f"{prefix}.json"
    csv_path = OUTPUT_DIR / f"{prefix}.csv"
    summary_path = OUTPUT_DIR / f"{prefix}_ringkasan.json"

    hasil_semua: list[dict[str, Any]] = []
    sudah_selesai_ids: set[int] = set()
    if args.resume and json_path.is_file():
        try:
            isi_lama = json.loads(json_path.read_text(encoding="utf-8"))
            if isinstance(isi_lama, list):
                hasil_semua = isi_lama
                sudah_selesai_ids = {int(x["id"]) for x in hasil_semua if "id" in x}
                print(f"Checkpoint ditemukan: memuat {len(hasil_semua)} hasil sebelumnya.")
        except Exception as err:
            print(f"Gagal membaca checkpoint lama ({err}), mulai dari awal.")

    jumlah_total = len(dataset)
    awal = time.time()

    try:
        for posisi, item in enumerate(dataset, start=1):
            item_id = int(item["id"])
            if item_id in sudah_selesai_ids:
                print(f"[{posisi}/{jumlah_total}] ID {item_id}: dilewati (sudah ada di checkpoint).", flush=True)
                continue
            query = str(item["query"]).strip()
            ground_truth = str(item["ground_truth"]).strip()
            category = str(item.get("category", ""))
            status = "OK"
            error_retrieval = ""
            error_generation = ""
            error_judge = ""
            jawaban: str | None = None
            context = ""
            hasil_topk: list[dict[str, Any]] = []
            hasil_konteks: list[dict[str, Any]] = []
            judge_result: dict[str, Any] = {}
            durasi_retrieval = 0.0
            durasi_generation = 0.0
            durasi_judge = 0.0

            print(f"[{posisi}/{jumlah_total}] ID {item_id}: {query[:90]}", flush=True)

            try:
                t0 = time.time()
                hasil_topk = retriever(
                    collection=collection,
                    model=model,
                    pertanyaan=query,
                    topk=args.topk,
                )
                id_tetangga = cari_id_tetangga(
                    hasil=hasil_topk,
                    urut=urut,
                    jumlah_chunk=args.jumlah_chunk,
                    jumlah_tetangga=args.jumlah_tetangga,
                )
                hasil_konteks = hasil_topk + ambil_chunk_tetangga(
                    collection=collection,
                    id_tetangga=id_tetangga,
                )
                context = susun_konteks(hasil_konteks)
                durasi_retrieval = time.time() - t0
            except Exception as error:
                status = "RETRIEVAL_ERROR"
                error_retrieval = f"{type(error).__name__}: {error}"

            if args.mode == "full" and status == "OK":
                try:
                    t0 = time.time()
                    prompt = bangun_prompt(pertanyaan=query, konteks=context)
                    jawaban = panggil_llm(prompt)
                    durasi_generation = time.time() - t0
                    if not jawaban:
                        status = "GENERATION_ERROR"
                        error_generation = "Generator mengembalikan jawaban kosong/None."
                    else:
                        jawaban = str(jawaban).strip()
                except Exception as error:
                    status = "GENERATION_ERROR"
                    error_generation = f"{type(error).__name__}: {error}"

            if judge is not None and status != "RETRIEVAL_ERROR":
                try:
                    t0 = time.time()
                    judge_result = judge.nilai(
                        query=query,
                        context=context,
                        answer=(jawaban if jawaban is not None else "") if args.mode == "full" else None,
                        ground_truth=ground_truth,
                        category=category,
                    )
                    durasi_judge = time.time() - t0
                except Exception as error:
                    error_judge = f"{type(error).__name__}: {error}"

            metrik = metrik_sumber(item, hasil_topk, hasil_konteks)
            if metrik["expected_source_in_index"] is None and item.get("source_scope") == "single_source":
                expected = {nama.lower() for nama in item.get("expected_sources", [])}
                indexed = {nama.lower() for nama in index_coverage["nama_file_terindeks"]}
                metrik["expected_source_in_index"] = any(n in indexed for n in expected)

            row = {
                "id": item_id,
                "query": query,
                "category": category,
                "source_reference": item.get("source_reference", ""),
                "source_scope": item.get("source_scope", ""),
                "expected_sources": item.get("expected_sources", []),
                "status": status,
                "expected_source_in_index": metrik["expected_source_in_index"],
                "source_hit_at_k": metrik["source_hit_at_k"],
                "source_hit_in_context": metrik["source_hit_in_context"],
                "source_rank": metrik["source_rank"],
                "source_reciprocal_rank": metrik["source_reciprocal_rank"],
                "jumlah_chunk_topk": len(hasil_topk),
                "jumlah_chunk_konteks": len(hasil_konteks),
                "retrieved_sources_topk": ringkas_sumber(hasil_topk),
                "retrieved_sources_context": ringkas_sumber(hasil_konteks),
                "retrieved_chunk_ids": [c.get("chunk_id") for c in hasil_konteks],
                "retrieved_context": context,
                "answer": jawaban or "",
                "ground_truth": ground_truth,
                "context_relevance": judge_result.get("context_relevance"),
                "faithfulness": judge_result.get("faithfulness"),
                "answer_relevance": judge_result.get("answer_relevance"),
                "answer_correctness": judge_result.get("answer_correctness"),
                "unsupported_claims": judge_result.get("unsupported_claims", []),
                "missing_important_points": judge_result.get("missing_important_points", []),
                "judge_reason": judge_result.get("judge_reason", ""),
                "error_retrieval": error_retrieval,
                "error_generation": error_generation,
                "error_judge": error_judge,
                "duration_retrieval_seconds": round(durasi_retrieval, 3),
                "duration_generation_seconds": round(durasi_generation, 3),
                "duration_judge_seconds": round(durasi_judge, 3),
                "sources_for_user": format_sumber(hasil_konteks),
            }
            hasil_semua.append(row)

            # Checkpoint setelah setiap soal agar hasil tidak hilang jika batch terputus.
            simpan_hasil(hasil_semua, json_path, csv_path)
            if judge_result:
                score = judge_result.get("context_relevance")
                score_txt = f"context_relevance={score:.2f}" if isinstance(score, (int, float)) else "judge selesai"
            elif error_judge:
                score_txt = "judge error"
            else:
                score_txt = "tanpa judge"
            print(f"    status={status}; chunk={len(hasil_konteks)}; {score_txt}", flush=True)

            if args.delay > 0 and posisi < jumlah_total:
                time.sleep(args.delay)

    finally:
        if judge is not None:
            judge.close()

    ringkasan = buat_ringkasan(
        hasil=hasil_semua,
        index_coverage=index_coverage,
        file_coverage=file_coverage,
        generator_info=info_llm(),
        judge_info=judge_info,
        mode=args.mode,
    )
    ringkasan["durasi_total_seconds"] = round(time.time() - awal, 2)
    summary_path.write_text(json.dumps(ringkasan, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + "=" * 72)
    print("HASIL HARNESS")
    print("Soal selesai               :", len(hasil_semua))
    print("Source Hit@k (semua)       :", ringkasan["retrieval"]["source_hit_at_k_semua_soal"], "/", ringkasan["retrieval"]["soal_dengan_satu_sumber_acuan"])
    print("Source Hit@k (terindeks)   :", ringkasan["retrieval"]["source_hit_at_k_hanya_sumber_terindeks"], "/", ringkasan["retrieval"]["soal_sumber_tersedia_di_indeks"])
    print("MRR sumber (terindeks)     :", ringkasan["retrieval"]["mean_reciprocal_rank_sumber_terindeks"])
    for metrik, nilai in ringkasan["rag_triad_and_correctness"].items():
        print(f"{metrik:24}: {nilai if nilai is not None else 'N/A'}")
    print("\nFile hasil:")
    print("CSV      :", csv_path)
    print("JSON     :", json_path)
    print("Ringkasan:", summary_path)
    print("Total durasi:", ringkasan["durasi_total_seconds"], "detik")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nEvaluasi dihentikan. Checkpoint hasil per-soal yang sudah selesai tetap tersimpan.")
        raise SystemExit(130)
