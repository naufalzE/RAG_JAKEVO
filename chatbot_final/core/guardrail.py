# ============================================================
# core/guardrail.py
# Sistem Keamanan & Validasi (Guardrail) Chatbot RAG JAKEVO
# Meliputi: Input Guardrail, Context Guardrail, dan Output Guardrail
# ============================================================

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any


@dataclass
class GuardrailResult:
    lolos: bool
    alasan: Optional[str] = None
    pesan_penolakan: Optional[str] = None
    kategori: Optional[str] = None  # injection, toxic, oos, empty, length, dll.


class Guardrail:
    """
    Guardrail multi-layer untuk Chatbot JAKEVO:
    1. Input Guardrail:
       - Validasi panjang teks & sanitasi
       - Deteksi prompt injection & jailbreak
       - Deteksi ujaran kasar / toxic / SARA
       - Deteksi Out-of-Scope (pertanyaan di luar izin/layanan publik)
    2. Context Guardrail:
       - Memvalidasi apakah konteks dari ChromaDB cukup relevan
    3. Output Guardrail:
       - Masking Data Pribadi (PII: NIK, No HP, Email)
       - Pembersihan format markdown yang tidak diinginkan
    """

    # Batasan karakter
    PANJANG_MINIMAL = 3
    PANJANG_MAKSIMAL = 800

    # Pola Prompt Injection & Jailbreak (Indonesian & English)
    POLA_INJECTION = [
        r"abaikan\s+(semua\s+)?(instruksi|perintah|aturan)",
        r"ignore\s+(all\s+)?(previous\s+)?(instructions|prompts|rules)",
        r"(tampilkan|bocorkan|sebutkan)\s+(system\s+prompt|prompt\s+asli|instruksi\s+rahasia)",
        r"(show|reveal|display|print)\s+(system\s+prompt|initial\s+prompt)",
        r"kamu\s+sekarang\s+adalah",
        r"you\s+are\s+now\s+(a|an)?",
        r"act\s+as\s+",
        r"mode\s+pengembang|developer\s+mode",
        r"jailbreak|dan\s+mode|do\s+anything\s+now",
        r"bypass\s+(filter|restriction|keamanan)",
        r"lupakan\s+(semua\s+)?aturan",
        r"pretend\s+you\s+are",
    ]

    # Kata kasar / Toxic / SARA
    KATA_KASAR = [
        r"\banjing\b", r"\bbabi\b", r"\bbangsat\b", r"\bkontol\b", r"\bmemek\b",
        r"\bngentot\b", r"\bgoblok\b", r"\btolol\b", r"\bbego\b", r"\bkampret\b",
        r"\bjancuk\b", r"\basu\b", r"\bbajingan\b", r"\btetek\b", r"\bperek\b"
    ]

    # Indikator Out of Scope (Permintaan koding, resep, hiburan murni)
    POLA_OUT_OF_SCOPE = [
        r"(buatkan|tulis(kan)?|bikin(kan)?)\s+.*(kode|script|kodingan|program|fungsi)\b",
        r"(buatkan|tulis(kan)?|bikin(kan)?)\s+(aplikasi|game|web(site)?)\s+(dengan|menggunakan|pakai)\b",
        r"write\s+(a\s+)?(python|javascript|code|script|program)",
        r"resep\s+(membuat|masak|makanan|kue|minuman)",
        r"lirik\s+lagu",
        r"chord\s+gitar",
        r"cerita\s+lucu|dongeng|lelucon",
    ]

    # Pola PII (Data Pribadi) untuk disamarkan pada output
    POLA_NIK = r"\b([0-9]{6})[0-9]{6}([0-9]{4})\b"  # 16 digit NIK
    POLA_HP = r"\b(08[0-9]{2}|(\+62)8[0-9]{2})[0-9]{4,8}\b"  # No HP Indonesia
    POLA_EMAIL = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"

    def __init__(
        self,
        aktifkan_injection_check: bool = True,
        aktifkan_toxic_check: bool = True,
        aktifkan_oos_check: bool = True,
        aktifkan_pii_masking: bool = True,
    ):
        self.aktifkan_injection_check = aktifkan_injection_check
        self.aktifkan_toxic_check = aktifkan_toxic_check
        self.aktifkan_oos_check = aktifkan_oos_check
        self.aktifkan_pii_masking = aktifkan_pii_masking

        # Kompilasi regex untuk performa cepat
        self._regex_injection = [
            re.compile(p, re.IGNORECASE) for p in self.POLA_INJECTION
        ]
        self._regex_toxic = [
            re.compile(p, re.IGNORECASE) for p in self.KATA_KASAR
        ]
        self._regex_oos = [
            re.compile(p, re.IGNORECASE) for p in self.POLA_OUT_OF_SCOPE
        ]

    # ============================================================
    # 1. INPUT GUARDRAIL
    # ============================================================

    def periksa_input(self, teks: str) -> GuardrailResult:
        """
        Memvalidasi pertanyaan pengguna sebelum diproses oleh sistem.
        """
        if not teks or not teks.strip():
            return GuardrailResult(
                lolos=False,
                alasan="Input kosong",
                kategori="empty",
                pesan_penolakan="Pertanyaan tidak boleh kosong. Silakan ketik pertanyaan Anda.",
            )

        teks_bersih = teks.strip()

        # Cek batas panjang
        if len(teks_bersih) < self.PANJANG_MINIMAL:
            return GuardrailResult(
                lolos=False,
                alasan="Input terlalu pendek",
                kategori="length_min",
                pesan_penolakan="Pertanyaan terlalu pendek. Mohon berikan pertanyaan yang lebih spesifik terkait layanan JAKEVO.",
            )

        if len(teks_bersih) > self.PANJANG_MAKSIMAL:
            return GuardrailResult(
                lolos=False,
                alasan="Input melebihi batas maksimal",
                kategori="length_max",
                pesan_penolakan=f"Pertanyaan terlalu panjang (maksimal {self.PANJANG_MAKSIMAL} karakter). Mohon persingkat pertanyaan Anda.",
            )

        # Cek Prompt Injection / Jailbreak
        if self.aktifkan_injection_check:
            for rgx in self._regex_injection:
                if rgx.search(teks_bersih):
                    return GuardrailResult(
                        lolos=False,
                        alasan="Terdeteksi upaya manipulasi instruksi (Prompt Injection)",
                        kategori="prompt_injection",
                        pesan_penolakan="Maaf, pertanyaan Anda mengandung instruksi sistem yang tidak diizinkan. Silakan tanyakan hal seputar layanan publik atau izin JAKEVO.",
                    )

        # Cek Kata Kasar / Ujaran Kebencian
        if self.aktifkan_toxic_check:
            for rgx in self._regex_toxic:
                if rgx.search(teks_bersih):
                    return GuardrailResult(
                        lolos=False,
                        alasan="Terdeteksi kata kasar / tidak pantas",
                        kategori="toxic",
                        pesan_penolakan="Mohon gunakan bahasa yang sopan dan santun saat mengajukan pertanyaan pada layanan publik ini.",
                    )

        # Cek Out of Scope (OOS)
        if self.aktifkan_oos_check:
            for rgx in self._regex_oos:
                if rgx.search(teks_bersih):
                    return GuardrailResult(
                        lolos=False,
                        alasan="Pertanyaan di luar cakupan (Out of Scope)",
                        kategori="out_of_scope",
                        pesan_penolakan="Maaf, saya adalah asisten resmi layanan JAKEVO (administrasi kependudukan dan perizinan DKI Jakarta). Saya tidak dapat melayani permintaan di luar topik tersebut.",
                    )

        return GuardrailResult(lolos=True)

    # ============================================================
    # 2. CONTEXT GUARDRAIL
    # ============================================================

    def periksa_konteks(
        self,
        hasil_retrieval: List[Dict[str, Any]],
        ambang_jarak_maksimal: float = 1.6,
    ) -> GuardrailResult:
        """
        Memvalidasi apakah chunk retrieval memiliki relevansi yang cukup.
        Jika hasil kosong atau jarak embedding terlalu jauh, hentikan sebelum memanggil LLM.
        """
        if not hasil_retrieval:
            return GuardrailResult(
                lolos=False,
                alasan="Tidak ada dokumen relevan yang ditemukan di basis data",
                kategori="no_context",
                pesan_penolakan="Maaf, informasi mengenai hal tersebut tidak ditemukan dalam dokumen panduan layanan JAKEVO.",
            )

        # Periksa jarak terdekat (paling relevan)
        jarak_terdekat = None
        for chunk in hasil_retrieval:
            dist = chunk.get("distance")
            if dist is not None:
                if jarak_terdekat is None or dist < jarak_terdekat:
                    jarak_terdekat = dist

        # Jika jarak terdekat melebihi ambang batas toleransi, anggap tidak relevan
        if jarak_terdekat is not None and jarak_terdekat > ambang_jarak_maksimal:
            return GuardrailResult(
                lolos=False,
                alasan=f"Tingkat relevansi dokumen terlalu rendah (jarak={jarak_terdekat:.3f})",
                kategori="low_relevance",
                pesan_penolakan="Maaf, dokumen yang tersedia tidak cukup relevan untuk menjawab pertanyaan tersebut.",
            )

        return GuardrailResult(lolos=True)

    # ============================================================
    # 3. OUTPUT GUARDRAIL
    # ============================================================

    def periksa_output(self, jawaban: str) -> str:
        """
        Membersihkan output dari LLM:
        - Pembersihan format markdown berlebihan
        - Masking PII (NIK, nomor telepon, email)
        """
        if not jawaban:
            return ""

        hasil = jawaban

        # 1. Bersihkan format markdown jika ada (sesuai SOP prompt)
        hasil = re.sub(r"\*\*([^*]+)\*\*", r'"\1"', hasil)  # **tebal** -> "tebal"
        hasil = re.sub(r"^\s*#+\s*", "", hasil, flags=re.MULTILINE)  # hilangkan heading #

        # 2. Masking PII setelah markdown dibersihkan (agar asteris tidak bentrok)
        if self.aktifkan_pii_masking:
            # Mask NIK: tampilkan 6 digit awal, samarkan 6 digit tengah, tampilkan 4 digit akhir
            hasil = re.sub(self.POLA_NIK, r"\1******\2", hasil)
            # Mask Nomor HP
            hasil = re.sub(self.POLA_HP, r"[NOMOR HP DISAMARKAN]", hasil)
            # Mask Email
            hasil = re.sub(self.POLA_EMAIL, r"[EMAIL DISAMARKAN]", hasil)

        return hasil.strip()


# Instance singleton default
guardrail_default = Guardrail()
