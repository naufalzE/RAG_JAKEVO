# Harness Evaluasi RAG JAKEVO

Paket ini menambahkan harness pengujian ke proyek `chatbotv2` tanpa mengubah modul chatbot yang sudah ada.

## Isi paket

- `uji_harness/evaluasi_rag.py` — runner evaluasi yang memakai retriever, neighbor expansion, context builder, prompt, dan generator asli dari proyek JAKEVO.
- `uji_harness/golden_dataset.json` — 100 query, ground truth, kategori, serta referensi dokumen sumber dari workbook yang diberikan.
- `uji_harness/requirements-harness.txt` — dependensi yang dibutuhkan untuk menjalankan harness.
- `uji_harness/hasil/` — lokasi otomatis untuk menyimpan CSV, JSON per pertanyaan, dan ringkasan agregat.

## Cara memasang

1. Ekstrak folder `uji_harness` dari paket ini ke direktori utama `chatbotv2`, sejajar dengan folder `core`, `retrieval`, `storage`, dan `llm`.
2. Jangan hapus atau menimpa `.env` milik proyek Anda. Harness membaca konfigurasi generator dari `.env` yang sudah ada.
3. Dari terminal, masuk ke direktori utama `chatbotv2`.
4. Pasang dependensi bila belum tersedia:

   ```bash
   pip install -r uji_harness/requirements-harness.txt
   ```

## Konfigurasi LLM Judge

Harness memakai judge terpisah yang dapat dikonfigurasi dengan variabel berikut di `.env`:

```env
# Pilih gemini atau deepseek
JUDGE_PROVIDER=
JUDGE_MODEL=
JUDGE_API_KEY=
JUDGE_BASE_URL=
JUDGE_TIMEOUT=90
```

- `JUDGE_API_KEY` opsional jika Anda ingin memakai API key provider yang sama; bila kosong, harness mencoba `GEMINI_API_KEY` atau `DEEPSEEK_API_KEY` sesuai provider.
- `JUDGE_MODEL` sebaiknya diisi dengan nama model judge yang berbeda dari model generator agar evaluasi lebih independen. Pastikan nama model tersedia pada akun/API Anda. Jika dikosongkan, harness memakai model default dari provider yang dipilih.
- `JUDGE_BASE_URL` hanya diperlukan untuk endpoint DeepSeek yang berbeda dari default.
- Jika tidak mengisi `JUDGE_PROVIDER`, harness berusaha memilih provider yang berbeda dari generator (Gemini atau DeepSeek) bila API key-nya tersedia. Jika hanya satu provider tersedia, provider itu digunakan.
- Jika generator dan judge memakai provider/model yang sama, harness akan memberi peringatan. Skor tetap dapat dihitung, tetapi potensi bias penilaian lebih besar.

Jangan menaruh API key ke file kode atau membagikan `.env`.

## Jalankan bertahap

### 1. Uji kecil dulu (5 soal)

```bash
python uji_harness/evaluasi_rag.py --mode full --limit 5 --topk 10 --jumlah-chunk 3 --jumlah-tetangga 1
```

### 2. Evaluasi seluruh 100 soal

```bash
python uji_harness/evaluasi_rag.py --mode full --topk 10 --jumlah-chunk 3 --jumlah-tetangga 1
```

### 3. Uji retrieval saja

```bash
python uji_harness/evaluasi_rag.py --mode retrieval --topk 10 --jumlah-chunk 3 --jumlah-tetangga 1
```

Mode `retrieval` tidak memanggil generator. LLM Judge hanya menilai `context_relevance`, sementara `Hit@k` dan `MRR` dihitung dari kecocokan file sumber acuan dengan metadata chunk yang ditemukan.

### 4. Jalankan ID tertentu

```bash
python uji_harness/evaluasi_rag.py --mode full --ids 1,2,45,87
```

### 5. Jalankan tanpa LLM Judge

```bash
python uji_harness/evaluasi_rag.py --mode full --limit 5 --skip-judge
```

Mode ini masih memanggil generator pada `--mode full`, tetapi tidak menghitung skor RAG Triad.

## Apa yang diukur?

### Retrieval

- `source_hit_at_k`: apakah file sumber acuan muncul di Top-k semantic retrieval.
- `source_hit_in_context`: apakah file sumber acuan masuk ke konteks setelah ekspansi tetangga.
- `source_rank`: posisi pertama chunk dari file sumber acuan.
- `source_reciprocal_rank`: nilai 1/rank, atau 0 bila sumber tidak ditemukan.
- Metrik source hit/MRR hanya dihitung untuk soal dengan satu sumber eksplisit. Ringkasan memisahkan source hit seluruh soal dari source hit pada soal yang file acuannya memang sudah ada di indeks, sehingga dokumen yang belum diindeks tidak disalahartikan sebagai kegagalan ranking. Soal lintas 10 layanan dinilai melalui context relevance dan LLM Judge, bukan dipaksa mempunyai satu file sumber.

### RAG Triad + correctness tambahan

- `context_relevance`: konteks retrieval relevan dengan pertanyaan atau tidak.
- `faithfulness`: klaim jawaban didukung konteks atau mengandung halusinasi.
- `answer_relevance`: jawaban langsung menjawab kebutuhan pertanyaan atau tidak.
- `answer_correctness`: kesesuaian jawaban dengan ground truth. Ini metrik tambahan di luar RAG Triad.

Skor berada di rentang 0.0–1.0. Skor otomatis adalah indikator, bukan pengganti audit manusia. Periksa terutama item dengan faithfulness/correctness rendah dan semua kasus error.

## File hasil

Setiap eksekusi membuat tiga file di `uji_harness/hasil/`:

- `hasil_harness_<timestamp>.csv` — tabel yang mudah dibuka di Excel; memuat pertanyaan, sumber, konteks retrieval, jawaban, skor, dan error.
- `hasil_harness_<timestamp>.json` — hasil per soal dalam format terstruktur.
- `hasil_harness_<timestamp>_ringkasan.json` — rata-rata metrik, source hit rate, MRR, cakupan indeks, model generator dan judge.

Harness menyimpan checkpoint setelah setiap soal. Jika batch terhenti, hasil soal yang selesai tetap tersedia.

## Penting: cakupan indeks pada snapshot proyek yang diberikan

Golden Dataset merujuk 10 berkas layanan web. Snapshot ChromaDB di ZIP yang diperiksa berisi 122 chunk dari `data.pdf` dan 3 file web berikut:

- `PM1_KETERANGAN_BELUM_MEMILIKI_RUMAH.txt`
- `PM1_PERKAWINAN_BAWAH_UMUR.txt`
- `PM1_PERKAWINAN_PERTAMA.txt`

Dengan demikian, tujuh file layanan lain belum ada di indeks snapshot tersebut. Harness akan menampilkan daftar file acuan yang belum ditemukan sebelum evaluasi. Untuk memperoleh evaluasi yang representatif bagi seluruh 100 soal, masukkan 10 file `.txt` layanan yang menjadi sumber Golden Dataset ke `dokumen_web/`, lalu jalankan proses indexing proyek (`python main.py`) sebelum menjalankan batch penuh. Jangan jalankan indexing sebelum file layanan sumber tersedia.

## Catatan interpretasi

- `context_relevance` yang tinggi tidak otomatis berarti jawaban benar.
- `faithfulness` tinggi dengan `answer_correctness` rendah berarti jawaban konsisten dengan konteks yang salah/tidak lengkap; periksa retrieval atau kelengkapan sumber.
- `answer_relevance` tinggi tetapi `faithfulness` rendah berarti jawaban menjawab pertanyaan tetapi berisiko mengarang.
- `source_hit_at_k` rendah dengan file acuan tidak ada di indeks adalah masalah cakupan/indexing, bukan murni ranking retriever.
- Untuk laporan akhir, audit manual sampel skor tinggi/rendah dan soal guardrail.
