# Holdout 50 — Chatbot JAKEVO

- Jumlah pertanyaan: 50 (ID 501–550)
- Kategori: {'Satu dokumen (web)': 15, 'Panduan PDF': 2, 'Lintas dokumen': 10, 'Ambigu (perlu klarifikasi)': 7, 'Menyesatkan (guardrail)': 9, 'Di luar cakupan': 7}
- Maksimum kemiripan leksikal TF-IDF terhadap 500 pertanyaan lama: 0.3646
- Pertanyaan memakai skenario, pertanyaan gabungan, klarifikasi, premis keliru, dan batas kemampuan chatbot.

## Pemisahan untuk mencegah data leakage
1. Masukkan hanya `holdout_50_jakevo_queries_only.json` ke proses inferensi/harness sebagai input model. File ini hanya memuat `id` dan `query`.
2. Simpan `holdout_50_jakevo_answer_key.json` terpisah. Jangan masukkan `ground_truth`, `expected_sources`, atau nama sumber ke prompt chatbot.
3. `holdout_50_jakevo_gold_dataset.json` adalah file gabungan untuk evaluator/harness. Gunakan hanya kolom `query` ketika memanggil chatbot; gunakan kolom lain setelah jawaban dihasilkan untuk evaluasi.
4. Jangan tambahkan pertanyaan holdout atau kunci jawabannya ke ChromaDB, prompt sistem, few-shot examples, atau data tuning. Pertahankan sebagai data uji yang belum dilihat.
5. Jangan memakai nilai holdout untuk mengubah retrieval/prompt lalu melaporkan hasil pada set yang sama sebagai evaluasi final. Setelah perbaikan, gunakan set evaluasi baru.

## Batas audit
Pemeriksaan kemiripan menggunakan TF-IDF n-gram terhadap kolom `query` dari `harness_500_jakevo.json`. Itu membantu menyaring kemiripan redaksi, tetapi tidak membuktikan bahwa tidak ada overlap semantik sama sekali. Sejumlah soal memang menguji kembali fakta sumber yang sama melalui skenario komposit untuk menguji generalisasi, bukan mengukur pengetahuan baru. Audit manual tetap disarankan.
