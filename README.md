# JAKEVO RAG Chatbot & Retrieval Pipeline

> Sistem Chatbot Berbasis **Retrieval-Augmented Generation (RAG)** untuk Layanan Perizinan & Pelayanan Terpadu Satu Pintu (**DPMPTSP DKI Jakarta - JAKEVO**).

---

## 📌 Daftar Isi
1. [Gambaran Umum](#-gambaran-umum)
2. [Fitur Utama](#-fitur-utama)
3. [Teknologi yang Digunakan](#-teknologi-yang-digunakan)
4. [Struktur Direktori](#-struktur-direktori)
5. [Arsitektur & Alur Kerja](#-arsitektur--alur-kerja)
6. [Instalasi & Persiapan](#-instalasi--persiapan)
7. [Konfigurasi Lingkungan (.env)](#-konfigurasi-lingkungan-env)
8. [Panduan Penggunaan](#-panduan-penggunaan)
   - [1. Ingesti Data ke Vector DB](#1-ingesti-data-ke-vector-db)
   - [2. Testing Tanya Jawab via Terminal (CLI)](#2-testing-tanya-jawab-via-terminal-cli)
   - [3. Menjalankan Backend API (FastAPI)](#3-menjalankan-backend-api-fastapi)
   - [4. Menjalankan Frontend UI](#4-menjalankan-frontend-ui)
9. [Sistem Keamanan & Guardrail](#-sistem-keamanan--guardrail)
10. [Evaluasi & Benchmark (Uji Harness)](#-evaluasi--benchmark-uji-harness)

---

## 📖 Gambaran Umum

**JAKEVO RAG Chatbot** adalah asisten virtual pintar yang dirancang untuk menjawab pertanyaan masyarakat dan pemohon izin seputar petunjuk teknis, syarat administrasi, alur permohonan, dan informasi kantor DPMPTSP DKI Jakarta secara akurat, cepat, dan berbasis dokumen resmi.

Sistem ini memecahkan masalah halusinasi LLM konvensional dengan membatasi jawaban model hanya berdasarkan dokumen pedoman PDF resmi dan arsip web layanan JAKEVO yang telah divektorisasi ke dalam **ChromaDB**.

---

## ✨ Fitur Utama

- **Hybrid Retrieval Cerdas**:
  - Deteksi dokumen target otomatis berdasarkan kata kunci spesifik perizinan (*dictionary mapping*).
  - Vektorisasi semantik menggunakan model multibahasa canggih (*Dense Retrieval*).
  - **Ekspansi Tetangga (*Neighbor Chunk Expansion*)**: Menarik potongan teks sebelum dan sesudah chunk yang relevan agar konteks utuh dan tidak terpotong.
- **Multi-layer Guardrail Security**:
  - *Input Guardrail*: Menangkal serangan *Prompt Injection*, kata-kata kasar (*toxic/SARA*), dan pertanyaan di luar domain (*Out-of-Scope*).
  - *Context Guardrail*: Mendeteksi jika dokumen tidak memiliki informasi relevan untuk mencegah halusinasi.
  - *Output Guardrail*: Sensor otomatis (*PII Masking*) untuk data sensitif seperti NIK, nomor ponsel, dan email.
- **Dukungan Multi-LLM Provider**:
  - Google Gemini (`gemini-3.8-flash`, dsb.)
  - DeepSeek (`deepseek-chat`)
  - Xiaomi MiMO (`mimo-v1`)
- **Sitasi Sumber Transparan**: Setiap jawaban dilengkapi rujukan nama berkas dan nomor halaman/chunk dokumen acuan.
- **Testing & Evaluasi Terintegrasi**: Dilengkapi dataset emas (*Golden Dataset*) dan alat benchmarking akurasi otomatis.

---

## 🛠 Teknologi yang Digunakan

| Komponen | Teknologi |
|---|---|
| **Bahasa Pemrograman** | Python >= 3.10, TypeScript / JavaScript |
| **Vector Database** | [ChromaDB](https://www.trychroma.com/) (Persistent) |
| **Embedding Model** | `intfloat/multilingual-e5-small` via [Sentence-Transformers](https://sbert.net/) & PyTorch |
| **LLM Provider** | Google GenAI SDK, DeepSeek API, Xiaomi MiMO API, HTTPX |
| **Parsing Dokumen** | `pdfplumber` (PDF), `BeautifulSoup4` (HTML/Web Text) |
| **Backend API** | [FastAPI](https://fastapi.tiangolo.com/), Uvicorn, Pydantic v2 |
| **Frontend UI** | React, Vite, TailwindCSS, Framer Motion (`persona`, `jic-assistant`) |
| **Evaluasi** | Pandas, OpenPyXL, JSON Golden Datasets |

---

## 📁 Struktur Direktori

```text
chatbot_rag/
├── requirements.txt            # Dependensi utama Python
├── FLOWCHART.md                # Dokumentasi diagram alur Mermaid
├── README.md                   # Dokumentasi proyek (berkas ini)
└── chatbot_final/              # Sumber kode inti aplikasi
    ├── .env                    # Variabel lingkungan & API keys
    ├── main.py                 # Script Ingesti Data (PDF/Web -> ChromaDB)
    ├── tanya_jawab.py          # Script CLI untuk interaksi tanya-jawab langsung
    │
    ├── backend/                # Server REST API
    │   ├── main.py             # Entrypoint FastAPI & middleware
    │   ├── router.py           # Endpoint API (/api/chat, /rag/tanya, dll.)
    │   ├── schemas.py          # Pydantic schema request & response
    │   └── service.py          # Business logic singleton RAGService
    │
    ├── chunking/               # Pemecahan Dokumen
    │   ├── chunker.py          # Logika pemecah teks PDF dan web
    │   └── perata_tabel.py     # Format ekstraksi data tabel
    │
    ├── core/                   # Modul Inti & Utilitas
    │   ├── config.py           # Konfigurasi Pydantic Settings
    │   ├── guardrail.py        # Validasi keamanan multi-layer
    │   └── utils.py            # Validasi ID chunk, sanitasi, dll.
    │
    ├── dokumen/                # Folder sumber berkas PDF resmi
    ├── dokumen_web/            # Folder sumber dokumen teks web (.txt)
    ├── chroma_db/              # Direktori penyimpanan vektor ChromaDB
    │
    ├── storage/                # Penyimpanan & Vektor
    │   ├── database.py         # Interaksi ChromaDB (upsert, purge id basi)
    │   └── embedding.py        # Loading model Sentence-Transformers
    │
    ├── retrieval/              # Pencarian Dokumen Relevan
    │   ├── retriever.py        # Algoritma similarity & pencarian Top-K
    │   ├── kamus.py            # Mapping kata kunci dan dokumen target
    │   ├── tetangga.py         # Neighbor expansion untuk kesinambungan konteks
    │   └── konteks.py          # Penyusunan teks konteks & sitasi sumber
    │
    ├── llm/                    # Integrasi Model Bahasa
    │   ├── llm.py              # Façade pemilihan provider LLM
    │   ├── gemini_llm.py       # Adapter Google Gemini
    │   ├── deepseek_llm.py     # Adapter DeepSeek
    │   ├── mimo_llm.py         # Adapter MiMO
    │   └── prompt.py           # Template prompt & system instruction
    │
    ├── frontend/               # Antarmuka Pengguna
    │   ├── persona/            # UI Web Interaktif (React / Vite)
    │   ├── jic-assistant/      # UI Web Alternatif
    │   └── widget/             # Komponen widget embed
    │
    └── uji_harness/            # Kerangka Evaluasi & Benchmarking
        ├── evaluasi_rag.py     # Script pengujian akurasi otomatis
        ├── golden_dataset.json # Kumpulan soal uji standar (Ground Truth)
        └── antigravity_judge.py# Evaluator performa RAG
```

---

## 🔄 Arsitektur & Alur Kerja

Secara ringkas, sistem bekerja dalam dua siklus:

1. **Ingesti Dokumen (Offline Processing)**:
   $$\text{PDF / Web} \longrightarrow \text{Chunking \& Metadata} \longrightarrow \text{Embedding (e5-small)} \longrightarrow \text{ChromaDB}$$
2. **Inference / RAG Tanya-Jawab (Runtime Processing)**:
   $$\text{Pertanyaan} \xrightarrow{\text{Input Guardrail}} \text{Kamus / Deteksi Target} \xrightarrow{\text{Top-K + Tetangga}} \text{Prompt Builder} \xrightarrow{\text{LLM}} \xrightarrow{\text{Output Guardrail}} \text{Jawaban + Sitasi}$$

> 💡 *Diagram flowchart Mermaid lengkap beserta penjelasan decision tree dapat dilihat pada berkas [FLOWCHART.md](file:///c:/Users/Advan/Documents/chatbot_rag/FLOWCHART.md).*

---

## 🚀 Instalasi & Persiapan

### 1. Prasyarat Sistem
- Python versi **3.10** ke atas
- Node.js (opsional, jika ingin mengompilasi frontend React)

### 2. Pasang Virtual Environment & Dependensi
Buka terminal PowerShell di folder proyek:

```powershell
cd c:\Users\Advan\Documents\chatbot_rag

# Buat virtual environment jika belum ada
python -m venv venv

# Aktifkan virtual environment
.\venv\Scripts\Activate.ps1

# Pasang dependensi
pip install -r requirements.txt
```

---

## ⚙️ Konfigurasi Lingkungan (`.env`)

Buat atau edit berkas `chatbot_final/.env` dengan konfigurasi API key yang Anda miliki:

```env
# Pemilihan Penyedia LLM: 'gemini', 'deepseek', atau 'mimo'
LLM_PROVIDER=gemini

# Google Gemini API
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-3.8-flash

# DeepSeek API (Opsional)
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Xiaomi MiMO API (Opsional)
MIMO_API_KEY=
MIMO_MODEL=mimo-v1
MIMO_BASE_URL=https://token-plan-sgp.xiaomimimo.com/v1

# Timeout panggilan LLM (detik)
LLM_TIMEOUT=60
```

---

## 💻 Panduan Penggunaan

### 1. Ingesti Data ke Vector DB
Sebelum menjalankan chatbot pertama kali atau setiap kali ada pembaruan dokumen PDF/Web:

```powershell
cd chatbot_final
python main.py
```
*Proses ini akan membaca seluruh dokumen di folder `dokumen/` dan `dokumen_web/`, memecah teks, meng-generate vektor embedding, menyimpannya ke folder `chroma_db/`, serta menghapus chunk basi.*

### 2. Testing Tanya Jawab via Terminal (CLI)
Untuk mencoba tanya jawab langsung di terminal tanpa menjalankan backend:

```powershell
cd chatbot_final
python tanya_jawab.py
```
Anda dapat mengetik pertanyaan seputar layanan izin JAKEVO secara interaktif.

### 3. Menjalankan Backend API (FastAPI)
Untuk menjalankan server API REST:

```powershell
cd chatbot_final
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
Akses dokumentasi interaktif Swagger UI di browser:
👉 **`http://localhost:8000/docs`**

Endpoint utama:
- `POST /api/chat` : Endpoint standar untuk UI frontend.
- `POST /rag/tanya` : Endpoint RAG dengan metadata sitasi detail.
- `GET /rag/status` : Memeriksa kesiapan model dan jumlah koleksi ChromaDB.

### 4. Menjalankan Frontend UI
Masuk ke salah satu folder frontend (misalnya `persona`):

```powershell
cd chatbot_final/frontend/persona
npm install
npm run dev
```
Buka URL lokal yang muncul (biasanya `http://localhost:5173`) untuk menggunakan antarmuka percakapan interaktif.

---

## 🛡️ Sistem Keamanan & Guardrail

Modul [`core/guardrail.py`](file:///c:/Users/Advan/Documents/chatbot_rag/chatbot_final/core/guardrail.py) memastikan aplikasi aman digunakan publik:

1. **Input Guardrail**:
   - Menolak input < 3 karakter atau > 800 karakter.
   - Deteksi pola *jailbreak* (misal: `"abaikan instruksi sebelumnya"`, `"act as"`, `"bypass filter"`).
   - Deteksi kata kasar, provokasi, dan kata-kata terlarang.
   - Deteksi pertanyaan di luar cakupan layanan (*Out-of-Scope*).
2. **Context Guardrail**:
   - Memastikan potongan dokumen yang diambil memiliki tingkat kemiripan relevan yang memadai.
3. **Output Guardrail**:
   - Regex otomatis untuk menyamarkan (*masking*) NIK 16 digit, nomor telepon/WhatsApp, dan alamat email agar data pribadi masyarakat terlindungi.

---

## 📊 Evaluasi & Benchmark (Uji Harness)

Proyek ini menyertakan *testing harness* di dalam folder `chatbot_final/uji_harness/`:

```powershell
cd chatbot_final/uji_harness
python evaluasi_rag.py
```

Alat evaluasi ini menggunakan:
- **`golden_dataset.json`**: Ratusan pasang pertanyaan dan kunci jawaban standar.
- **Metrik Evaluasi**: Context Relevance, Faithfulness (keabsahan fakta), dan Answer Correctness.
- Menghasilkan laporan evaluasi berkala dalam format CSV dan JSON.
