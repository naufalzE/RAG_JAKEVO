export interface KnowledgeDocument {
  id: string;
  topic: string;
  question: string;
  keywords: string[];
  sourceDoc: string;
  docType: 'PDF' | 'SOP' | 'WEB-SYARAT' | 'REGULASI';
  page: string;
  contextSnippet: string;
  answer: string;
}

export interface RagResult {
  query: string;
  tokens: string[];
  isRelevant: boolean;
  score: number;
  matchedDoc: {
    id: string;
    topic: string;
    sourceDoc: string;
    docType?: string;
    page?: string;
  } | null;
  matchedKeywords: string[];
  contextSnippet: string;
  finalAnswer: string;
  sourceMode?: 'FASTAPI_BACKEND' | 'STATIC_SIMULATION';
}

export interface ArchitectureStep {
  id: string;
  stepNumber: number;
  pipeline: 'ingestion' | 'query';
  title: string;
  subtitle: string;
  description: string;
  technicalRole: string;
  inputLabel: string;
  outputLabel: string;
  sampleData: string;
}

export interface TechStackItem {
  id: string;
  name: string;
  category: string;
  description: string;
  systemRole: string;
  specDetail: string;
}

export interface EvaluationMetricItem {
  id: string;
  name: string;
  shortCode: string;
  formula: string;
  description: string;
  howItWorks: string;
  placeholderValue: string;
  visualExample: {
    query: string;
    topK: { rank: number; docId: string; isRelevant: boolean; similarity: string }[];
    calculationNote: string;
  };
}

export const KNOWLEDGE_BASE: KnowledgeDocument[] = [
  {
    id: 'DOC-JAKEVO-001',
    topic: 'Alamat Kantor DPMPTSP',
    question: 'Di mana alamat kantor DPMPTSP?',
    keywords: [
      'alamat', 'kantor', 'lokasi', 'gedung', 'dimana', 'di mana', 'mpp',
      'kuningan', 'rasuna said', 'setiabudi', 'dki', 'jakarta', 'kontak',
      'telepon', 'email', 'lantai', 'kunjungi', 'jam buka', 'operasional', 'datang',
      'dpmptsp', 'ptsp'
    ],
    sourceDoc: 'Profil, Alamat Kantor, dan Layanan Informasi DPMPTSP Provinsi DKI Jakarta',
    docType: 'SOP',
    page: 'Halaman 4–6',
    contextSnippet:
      'Gedung Mal Pelayanan Publik (MPP) Provinsi DKI Jakarta Lantai 5, Jl. H.R. Rasuna Said Kav. C-22, Karet Kuningan, Setiabudi, Jakarta Selatan 12920. Jam operasional: Senin–Jumat 07.30–16.00 WIB.',
    answer: `
      <p>Kantor <strong>Dinas Penanaman Modal dan Pelayanan Terpadu Satu Pintu (DPMPTSP) Provinsi DKI Jakarta</strong> berlokasi di:</p>
      <p><strong>Gedung Mal Pelayanan Publik (MPP) Provinsi DKI Jakarta, Lantai 5</strong><br>
      Jl. H.R. Rasuna Said Kav. C-22, RT.02 / RW.05, Karet Kuningan, Setiabudi, Jakarta Selatan 12920.</p>
      <p><strong>Jam Operasional Pelayanan:</strong><br>
      • Senin – Kamis: 07.30 – 16.00 WIB<br>
      • Jumat: 07.30 – 16.30 WIB (Istirahat 11.30 – 13.00 WIB)<br>
      • Portal daring JAKEVO (<a href="https://jakevo.jakarta.go.id" target="_blank" rel="noopener noreferrer">jakevo.jakarta.go.id</a>) aktif 24 jam setiap hari.</p>
      <p><strong>Kontak Resmi:</strong><br>
      • Call Center Tanya PTSP: <strong>1500-164</strong> / (021) 1500164<br>
      • Email: dpmptsp@jakarta.go.id</p>
    `
  },
  {
    id: 'PANDUAN_JAKEVO_PEMOHON-PDF',
    topic: 'Alur Pengajuan Izin di JAKEVO',
    question: 'Bagaimana alur pengajuan izin di JAKEVO?',
    keywords: [
      'alur', 'pengajuan', 'izin', 'jakevo', 'cara', 'daftar', 'prosedur',
      'langkah', 'tahapan', 'online', 'berkas', 'verifikasi', 'pemohon', 'akun'
    ],
    sourceDoc: 'Buku Panduan Penggunaan Portal Perizinan JAKEVO bagi Pemohon',
    docType: 'PDF',
    page: 'Halaman 12–18',
    contextSnippet:
      'Alur pengajuan perizinan di JAKEVO: (1) Login/Registrasi akun di jakevo.jakarta.go.id dengan NIK/NPWP, (2) Pilih jenis layanan izin/non-izin, (3) Isi formulir elektronik & unggah dokumen persyaratan PDF, (4) Verifikasi administrasi & teknis oleh petugas PTSP, (5) Penerbitan output izin elektronik bertanda tangan digital (BSrE).',
    answer: `
      <p>Berikut adalah <strong>Alur Pengajuan Perizinan Daring melalui JAKEVO</strong>:</p>
      <ol>
        <li><strong>Registrasi &amp; Login Akun:</strong> Akses portal <a href="https://jakevo.jakarta.go.id" target="_blank" rel="noopener noreferrer">jakevo.jakarta.go.id</a> dan masuk menggunakan akun pemohon (NIK KTP dan NPWP).</li>
        <li><strong>Pilih Jenis Perizinan:</strong> Gunakan fitur pencarian layanan sesuai tingkat kewenangan (Kelurahan, Kecamatan, Kota, atau Provinsi).</li>
        <li><strong>Pengisian Formulir &amp; Unggah Berkas:</strong> Lengkapi data permohonan dan unggah hasil pindai (scan) dokumen persyaratan asli dalam format PDF/JPG.</li>
        <li><strong>Verifikasi Petugas PTSP:</strong> Petugas Front Office &amp; Tim Teknis memeriksa kelengkapan dokumen serta kesesuaian tata ruang/teknis.</li>
        <li><strong>Penerbitan SK/Izin Digital:</strong> Apabila disetujui, dokumen izin resmi diterbitkan secara elektronik lengkap dengan tanda tangan digital tersertifikasi BSrE BSSN dan dapat diunduh langsung.</li>
      </ol>
    `
  },
  {
    id: 'PM1_SKTM_KELURAHAN-WEB-SYARAT',
    topic: 'Syarat Surat Keterangan Tidak Mampu (SKTM)',
    question: 'Apa saja syarat Surat Keterangan Tidak Mampu (SKTM)?',
    keywords: [
      'sktm', 'tidak mampu', 'miskin', 'keringanan', 'biaya', 'sekolah',
      'rumah sakit', 'kelurahan', 'pengantar', 'rt', 'rw', 'pm1', 'bantuan'
    ],
    sourceDoc: 'Standar Operasional Prosedur Layanan Pengantar PM1 Kelurahan — SKTM',
    docType: 'WEB-SYARAT',
    page: 'Halaman 2',
    contextSnippet:
      'Persyaratan Surat Pengantar/Keterangan Tidak Mampu (SKTM): Surat Pengantar RT/RW, KTP-el pemohon, Kartu Keluarga (KK), Surat Pernyataan Tidak Mampu bermeterai, dan foto kondisi rumah tempat tinggal.',
    answer: `
      <p>Untuk mengajukan <strong>Surat Keterangan Tidak Mampu (SKTM) / Pengantar PM1 Kelurahan</strong> melalui JAKEVO, siapkan dokumen persyaratan berikut:</p>
      <ul>
        <li><strong>Surat Pengantar RT/RW</strong> setempat sesuai domisili KTP.</li>
        <li><strong>KTP Elektronik (KTP-el)</strong> asli pemohon (unggah hasil scan).</li>
        <li><strong>Kartu Keluarga (KK)</strong> asli.</li>
        <li><strong>Surat Pernyataan Tidak Mampu</strong> yang ditandatangani pemohon di atas meterai Rp10.000.</li>
        <li><strong>Foto Rumah Tempat Tinggal</strong> (tampak depan dan ruang dalam).</li>
        <li>Dokumen pendukung tujuan pengajuan (misal: surat keterangan dari sekolah/universitas atau rujukan rumah sakit).</li>
      </ul>
      <p><strong>Waktu Penyelesaian:</strong> 1 Hari Kerja sejak berkas dinyatakan lengkap (Bebas Biaya / Gratis Rp0).</p>
    `
  },
  {
    id: 'PM1_PERKAWINAN_PERTAMA-WEB-SYARAT',
    topic: 'Surat Pengantar Perkawinan Pertama (PM1)',
    question: 'Apa syarat surat pengantar perkawinan pertama?',
    keywords: [
      'perkawinan', 'nikah', 'menikah', 'pertama', 'pengantar', 'n1', 'n2', 'n4',
      'kua', 'catatan sipil', 'calon', 'pengantin', 'pasangan', 'pm1', 'kelurahan'
    ],
    sourceDoc: 'SOP Pelayanan Surat Pengantar Perkawinan Pertama (Model N1–N4) Kelurahan DKI Jakarta',
    docType: 'WEB-SYARAT',
    page: 'Halaman 1–3',
    contextSnippet:
      'Syarat Surat Pengantar Perkawinan Pertama (PM1): Pengantar RT/RW, KTP-el & KK calon pengantin, KTP-el kedua orang tua, Akta Kelahiran, Surat Pernyataan Belum Pernah Menikah bermeterai, dan pasfoto latar biru/merah.',
    answer: `
      <p>Persyaratan pengajuan <strong>Surat Pengantar Perkawinan Pertama (PM1 Kelurahan)</strong> di JAKEVO meliputi:</p>
      <ul>
        <li><strong>Surat Pengantar RT/RW</strong> sesuai domisili KTP.</li>
        <li><strong>KTP-el dan Kartu Keluarga (KK)</strong> calon mempelai.</li>
        <li><strong>KTP-el Kedua Orang Tua</strong> kandung.</li>
        <li><strong>Akta Kelahiran</strong> atau Ijazah terakhir calon mempelai.</li>
        <li><strong>Surat Pernyataan Belum Pernah Menikah (Jejaka/Perawan)</strong> di atas meterai Rp10.000 diketahui 2 orang saksi di luar keluarga.</li>
        <li><strong>Sertifikat Layak Kawin / Elsimil</strong> dari Puskesmas Kecamatan setempat.</li>
        <li><strong>Pasfoto ukuran 2x3 dan 3x4</strong> (latar belakang biru atau merah).</li>
      </ul>
    `
  },
  {
    id: 'PM1_KETERANGAN_BELUM_MEMILIKI_RUMAH-WEB-SYARAT',
    topic: 'Surat Keterangan Belum Memiliki Rumah (PM1)',
    question: 'Apa syarat surat keterangan belum memiliki rumah?',
    keywords: [
      'belum memiliki rumah', 'rumah', 'kpr', 'subsidi', 'flpp', 'hunian',
      'rusun', 'dp nol', 'keterangan rumah', 'pm1'
    ],
    sourceDoc: 'SOP Layanan Surat Pengantar Keterangan Belum Memiliki Rumah (PM1 Kelurahan)',
    docType: 'WEB-SYARAT',
    page: 'Halaman 1–2',
    contextSnippet:
      'Persyaratan Surat Keterangan Belum Memiliki Rumah: Surat Pengantar RT/RW, KTP-el pemohon (dan pasangan jika sudah menikah), Kartu Keluarga (KK), NPWP, dan Surat Pernyataan Belum Memiliki Rumah bermeterai Rp10.000.',
    answer: `
      <p>Untuk mengurus <strong>Surat Keterangan Belum Memiliki Rumah (PM1)</strong> guna keperluan KPR Subsidi / Rusunawa melalui JAKEVO, berikut persyaratannya:</p>
      <ul>
        <li><strong>Surat Pengantar RT/RW</strong> domisili setempat.</li>
        <li><strong>KTP-el Pemohon</strong> (serta KTP-el pasangan apabila sudah menikah).</li>
        <li><strong>Kartu Keluarga (KK)</strong> asli.</li>
        <li><strong>NPWP Pribadi</strong> pemohon.</li>
        <li><strong>Surat Pernyataan Belum Memiliki Rumah</strong> yang ditandatangani di atas meterai Rp10.000 dan diketahui Ketua RT/RW.</li>
      </ul>
      <p><strong>Biaya Retribusi:</strong> Gratis (Rp0) · <strong>Estimasi Penyelesaian:</strong> 1 Hari Kerja.</p>
    `
  },
  {
    id: 'IZIN_TANAH_MAKAM-SOP-006',
    topic: 'Syarat Izin Penggunaan Tanah Makam (IPTM)',
    question: 'Apa saja syarat izin penggunaan tanah makam?',
    keywords: [
      'makam', 'tanah makam', 'iptm', 'pemakaman', 'tpu', 'perpanjangan makam',
      'jenazah', 'meninggal', 'kematian', 'kuburan', 'tumpang'
    ],
    sourceDoc: 'SOP Pelayanan Izin Penggunaan Tanah Makam (IPTM Baru, Tumpang & Perpanjangan)',
    docType: 'SOP',
    page: 'Halaman 7–9',
    contextSnippet:
      'Syarat Izin Penggunaan Tanah Makam (IPTM): KTP-el dan KK ahli waris/pemohon, KTP-el jenazah, Surat Keterangan Kematian dari Rumah Sakit/Puskesmas dan Kelurahan, serta Surat Pengantar TPU dari Dinas Pertamanan dan Hutan Kota.',
    answer: `
      <p>Persyaratan pengajuan <strong>Izin Penggunaan Tanah Makam (IPTM)</strong> melalui JAKEVO meliputi:</p>
      <ul>
        <li><strong>KTP-el dan Kartu Keluarga (KK)</strong> ahli waris / penanggung jawab.</li>
        <li><strong>Identitas Almarhum/Almarhumah</strong> (KTP-el / KK / Akta Kelahiran).</li>
        <li><strong>Surat Keterangan Pemeriksaan Mayat / Kematian</strong> dari Rumah Sakit atau Puskesmas.</li>
        <li><strong>Surat Keterangan Kematian</strong> dari Kelurahan setempat.</li>
        <li><strong>Surat Pengantar Lokasi Petak Makam (TPU)</strong> dari Pengelola TPU Dinas Pertamanan dan Hutan Kota.</li>
        <li>Khusus <em>Makam Tumpang / Perpanjangan</em>: Melampirkan IPTM asli masa berlaku sebelumnya dan Surat Pernyataan Persetujuan Ahli Waris.</li>
      </ul>
    `
  },
  {
    id: 'SIP_DOKTER_NAKES-SOP-007',
    topic: 'Syarat Surat Izin Praktik (SIP) Dokter',
    question: 'Apa saja syarat surat izin praktik dokter?',
    keywords: [
      'dokter', 'sip', 'surat izin praktik', 'tenaga medis', 'kesehatan',
      'str', 'klinik', 'apoteker', 'perawat', 'bidan', 'fasyankes', 'praktik'
    ],
    sourceDoc: 'Panduan Perizinan Tenaga Medis & Kesehatan — Surat Izin Praktik (SIP) Dokter di JAKEVO',
    docType: 'REGULASI',
    page: 'Halaman 14–19',
    contextSnippet:
      'Persyaratan Surat Izin Praktik (SIP) Dokter: KTP-el, STR (Surat Tanda Registrasi) aktif dari Konsil Kedokteran Indonesia (KKI) / SatuSehat SDMK, Ijazah Profesi Dokter, Surat Keterangan Tempat Praktik dari Fasyankes, dan Bukti Kecukupan SKP.',
    answer: `
      <p>Dokumen persyaratan pengajuan <strong>Surat Izin Praktik (SIP) Dokter Umum / Spesialis / Gigi</strong> pada portal JAKEVO adalah:</p>
      <ol>
        <li><strong>KTP Elektronik (KTP-el)</strong> dan NPWP Pemohon.</li>
        <li><strong>Surat Tanda Registrasi (STR)</strong> yang masih berlaku / STR Seumur Hidup yang terverifikasi pada portal SatuSehat SDMK Kemenkes.</li>
        <li><strong>Ijazah Pendidikan Profesi</strong> Dokter / Dokter Gigi / Dokter Spesialis.</li>
        <li><strong>Surat Keterangan Tempat Praktik</strong> dari pimpinan Fasilitas Pelayanan Kesehatan (Rumah Sakit / Klinik) atau izin operasional klinik mandiri.</li>
        <li><strong>Pernyataan Kecukupan SKP</strong> (Satuan Kredit Profesi) untuk perpanjangan SIP ke-2/ke-3.</li>
        <li><strong>Pasfoto formal terbaru</strong> ukuran 4x6 berlatar belakang merah.</li>
      </ol>
    `
  },
  {
    id: 'DOC-PTSP-005',
    topic: 'Eskalasi Petugas PTSP & Matriks RBAC',
    question: 'Bagaimana alur izin JAKEVO dan eskalasi ke petugas?',
    keywords: [
      'eskalasi', 'petugas', 'role', 'akses', 'hak akses', 'rbac',
      'oss', 'konsultasi', 'bantuan', 'loket', 'front office', 'tiket'
    ],
    sourceDoc: 'Panduan Integrasi JAKEVO & Matriks Hak Akses RBAC DPMPTSP DKI Jakarta',
    docType: 'SOP',
    page: 'Halaman 21–24',
    contextSnippet:
      'Pengguna Publik dapat bertanya syarat izin via Chatbot RAG. Jika butuh konsultasi lanjutan, chatbot mengeskalasikan percakapan ke Petugas Layanan PTSP (Role 2) via Call Center 1500-164 atau loket Mal Pelayanan Publik.',
    answer: `
      <p>Sistem informasi perizinan <strong>JAKEVO</strong> menerapkan tata kelola layanan berlapis:</p>
      <ul>
        <li><strong>Lapis 1 — Konsultasi Mandiri Chatbot RAG:</strong> Menjawab kueri persyaratan dokumen, prosedur pengajuan, dan lokasi layanan secara instan 24/7 berdasarkan dokumen SOP resmi.</li>
        <li><strong>Lapis 2 — Eskalasi Petugas Front Office PTSP:</strong> Apabila kueri bersifat kasuistik atau memerlukan pemeriksaan berkas spesifik, pemohon diarahkan ke <strong>Call Center 1500-164</strong>, fitur Live Chat/Video Call Tanya PTSP, atau loket konsultasi Mal Pelayanan Publik Lt. 5.</li>
        <li><strong>Lapis 3 — Tim Teknis &amp; Administrator Knowledge Base:</strong> Memperbarui korpus dokumen PDF dan memantau akurasi retrieval vector database.</li>
      </ul>
    `
  }
];

const STOP_WORDS = new Set([
  'di', 'ke', 'dari', 'yang', 'dan', 'atau', 'adalah', 'ini', 'itu', 'ada',
  'pada', 'untuk', 'dengan', 'saya', 'kamu', 'dia', 'mereka', 'kita',
  'apa', 'siapa', 'mengapa', 'bagaimana', 'kapan', 'mana', 'saja', 'tolong',
  'mohon', 'bisa', 'kah', 'dong', 'sih', 'nya', 'apakah', 'cara', 'syarat'
]);

export function runRagPipeline(rawQuery: string): RagResult {
  const cleanedQuery = rawQuery.toLowerCase().replace(/[^\w\s]/gi, ' ').trim();
  const allTokens = cleanedQuery.split(/\s+/).filter(t => t.length > 1);
  const queryTokens = allTokens.filter(token => !STOP_WORDS.has(token));
  const effectiveTokens = queryTokens.length > 0 ? queryTokens : allTokens;

  let bestDoc: KnowledgeDocument | null = null;
  let highestScore = 0;
  let matchedKeywordsList: string[] = [];

  KNOWLEDGE_BASE.forEach(doc => {
    let score = 0;
    const matchedInThisDoc: string[] = [];

    effectiveTokens.forEach(token => {
      doc.keywords.forEach(kw => {
        if (kw === token || (token.length >= 3 && (kw.includes(token) || token.includes(kw)))) {
          score += 18;
          if (!matchedInThisDoc.includes(kw)) {
            matchedInThisDoc.push(kw);
          }
        }
      });

      if (doc.question.toLowerCase().includes(token) || doc.topic.toLowerCase().includes(token)) {
        score += 12;
      }

      if (doc.contextSnippet.toLowerCase().includes(token)) {
        score += 6;
      }
    });

    const normalizedScore = Math.min(Math.round(score), 98);

    if (normalizedScore > highestScore) {
      highestScore = normalizedScore;
      bestDoc = doc;
      matchedKeywordsList = matchedInThisDoc;
    }
  });

  const THRESHOLD = 15;
  const isRelevant = bestDoc !== null && highestScore >= THRESHOLD;

  let contextAugmented = '';
  let finalAnswerHtml = '';

  if (isRelevant && bestDoc) {
    const matched = bestDoc as KnowledgeDocument;
    contextAugmented = `Konteks diambil dari [${matched.id}] (${matched.docType} · ${matched.page}) "${matched.topic}": "${matched.contextSnippet}"`;
    finalAnswerHtml = matched.answer;
  } else {
    contextAugmented =
      'Tidak ada dokumen dalam basis pengetahuan yang melampaui ambang batas kemiripan vektor minimum (skor < 15%). Guardrail diaktifkan.';
    finalAnswerHtml = `
      <p>Mohon maaf, informasi mengenai pertanyaan tersebut belum ditemukan pada korpus dokumen SOP JAKEVO yang terindeks saat ini.</p>
      <p>Silakan gunakan kata kunci atau pilih topik layanan administrasi berikut:</p>
      <ul>
        <li><strong>Di mana alamat kantor DPMPTSP?</strong></li>
        <li><strong>Bagaimana alur pengajuan izin di JAKEVO?</strong></li>
        <li><strong>Apa saja syarat Surat Keterangan Tidak Mampu (SKTM)?</strong></li>
        <li><strong>Apa syarat surat pengantar perkawinan pertama?</strong></li>
        <li><strong>Apa saja syarat izin penggunaan tanah makam?</strong></li>
        <li><strong>Apa saja syarat surat izin praktik dokter?</strong></li>
      </ul>
    `;
  }

  return {
    query: rawQuery,
    tokens: effectiveTokens,
    isRelevant,
    score: highestScore,
    matchedDoc: isRelevant && bestDoc
      ? {
          id: (bestDoc as KnowledgeDocument).id,
          topic: (bestDoc as KnowledgeDocument).topic,
          sourceDoc: (bestDoc as KnowledgeDocument).sourceDoc,
          docType: (bestDoc as KnowledgeDocument).docType,
          page: (bestDoc as KnowledgeDocument).page
        }
      : null,
    matchedKeywords: matchedKeywordsList,
    contextSnippet: contextAugmented,
    finalAnswer: finalAnswerHtml,
    sourceMode: 'STATIC_SIMULATION'
  };
}

export const ARCHITECTURE_STEPS: ArchitectureStep[] = [
  // DOCUMENT INGESTION PIPELINE (1 - 6)
  {
    id: 'ing-1',
    stepNumber: 1,
    pipeline: 'ingestion',
    title: 'PDF Documents',
    subtitle: 'Raw Knowledge Corpus',
    description:
      'Kumpulan dokumen resmi pelayanan administrasi seperti buku panduan JAKEVO, standar operasional prosedur (SOP) perizinan DPMPTSP, dan daftar persyaratan layanan.',
    technicalRole: 'Sumber pengetahuan utama (ground truth) yang menjadi batas informasi sistem agar chatbot hanya menjawab berdasarkan regulasi resmi.',
    inputLabel: 'Berkas Dokumen Resmi',
    outputLabel: 'Raw PDF Binary Stream',
    sampleData: 'PANDUAN_JAKEVO_PEMOHON.pdf, SOP_PM1_KELURAHAN.pdf, REGULASI_SIP_NAKES.pdf'
  },
  {
    id: 'ing-2',
    stepNumber: 2,
    pipeline: 'ingestion',
    title: 'Text Extraction',
    subtitle: 'Document Parsing Engine',
    description:
      'Proses membaca struktur halaman PDF dan mengekstrak teks mentah beserta metadata nomor halaman dan judul dokumen.',
    technicalRole: 'Mengubah format dokumen non-terstruktur (PDF) menjadi representasi string teks yang dapat diolah secara programatik di Python.',
    inputLabel: 'File PDF Multi-Halaman',
    outputLabel: 'Raw Text + Page Metadata',
    sampleData: '{"doc": "PANDUAN_JAKEVO.pdf", "page": 12, "raw_text": "Alur pengajuan perizinan di JAKEVO..."}'
  },
  {
    id: 'ing-3',
    stepNumber: 3,
    pipeline: 'ingestion',
    title: 'Data Cleaning',
    subtitle: 'Text Normalization & Sanitization',
    description:
      'Membersihkan karakter artefak hasil ekstraksi PDF, menghapus header/footer berulang, menormalisasi spasi kosong, dan merapikan struktur poin persyaratan.',
    technicalRole: 'Mencegah noise karakter merusak kualitas representasi vektor (embedding) saat proses indeksasi.',
    inputLabel: 'Unstructured Extracted Text',
    outputLabel: 'Normalized Clean Text',
    sampleData: '"Syarat SKTM: 1. Surat Pengantar RT/RW 2. KTP-el Pemohon 3. Kartu Keluarga (KK)..."'
  },
  {
    id: 'ing-4',
    stepNumber: 4,
    pipeline: 'ingestion',
    title: 'Chunking',
    subtitle: 'Semantic Segment Splitting',
    description:
      'Memecah teks dokumen panjang menjadi potongan-potongan (chunks) berukuran terukur dengan overlap antar-segmen agar konteks kalimat tidak terputus.',
    technicalRole: 'Memastikan setiap segmen informasi fokus pada satu prosedur atau syarat spesifik sehingga pengambilan konteks menjadi presisi.',
    inputLabel: 'Clean Full Document Text',
    outputLabel: 'Document Chunks + Metadata',
    sampleData: 'Chunk #042 (250 tokens, overlap 40): "[PM1_SKTM] Persyaratan Surat Keterangan Tidak Mampu..."'
  },
  {
    id: 'ing-5',
    stepNumber: 5,
    pipeline: 'ingestion',
    title: 'Embedding',
    subtitle: 'Multilingual Dense Vectorization',
    description:
      'Mengonversi setiap potongan teks (chunk) menjadi vektor numerik berdimensi 384 menggunakan model Sentence Transformers paraphrase-multilingual-MiniLM-L12-v2.',
    technicalRole: 'Memetakan makna semantik teks bahasa Indonesia ke dalam ruang vektor multidimensi.',
    inputLabel: 'Text Chunk String',
    outputLabel: 'Dense Vector (384-d Float Array)',
    sampleData: '[-0.0418, 0.1294, 0.0882, -0.2105, ..., 0.0641] (Dimensi: 384)'
  },
  {
    id: 'ing-6',
    stepNumber: 6,
    pipeline: 'ingestion',
    title: 'ChromaDB Vector Database',
    subtitle: 'Persistent Vector Index Storage',
    description:
      'Menyimpan vektor embedding beserta teks chunk asli dan metadata dokumen (ID dokumen, nama file, halaman) ke dalam koleksi ChromaDB.',
    technicalRole: 'Menyediakan indeks pencarian kemiripan vektor (vector similarity search) berkecepatan tinggi saat pengguna mengajukan pertanyaan.',
    inputLabel: 'Embeddings + Chunks + Metadata',
    outputLabel: 'Indexed Vector Collection',
    sampleData: 'Collection: "jakevo_sop_docs" | Distance Metric: Cosine Similarity'
  },

  // QUESTION PROCESSING PIPELINE (1 - 7)
  {
    id: 'qry-1',
    stepNumber: 1,
    pipeline: 'query',
    title: 'User Question',
    subtitle: 'Natural Language Inquiry',
    description:
      'Pengguna mengajukan pertanyaan dalam bahasa sehari-hari mengenai syarat dokumen atau prosedur layanan administrasi di JAKEVO.',
    technicalRole: 'Titik masuk (entry point) interaksi pada antarmuka chatbot.',
    inputLabel: 'Input Pengguna',
    outputLabel: 'Raw Query String',
    sampleData: '"Apa saja syarat mengurus Surat Keterangan Tidak Mampu di kelurahan?"'
  },
  {
    id: 'qry-2',
    stepNumber: 2,
    pipeline: 'query',
    title: 'Query Processing',
    subtitle: 'Input Sanitization & Tokenization',
    description:
      'Menormalisasi teks pertanyaan pengguna, menghapus karakter tidak relevan, dan menyiapkan kueri bersih untuk proses enkoding vektor.',
    technicalRole: 'Menjaga konsistensi format teks kueri dengan format teks dokumen yang telah dibersihkan saat ingestion.',
    inputLabel: 'Raw Query String',
    outputLabel: 'Normalized Query',
    sampleData: '"syarat mengurus surat keterangan tidak mampu sktm di kelurahan"'
  },
  {
    id: 'qry-3',
    stepNumber: 3,
    pipeline: 'query',
    title: 'Embedding Query',
    subtitle: 'Query Vector Encoding',
    description:
      'Mengubah pertanyaan pengguna menjadi vektor berdimensi 384 menggunakan model embedding yang sama persis (paraphrase-multilingual-MiniLM-L12-v2).',
    technicalRole: 'Menempatkan pertanyaan pengguna di ruang vektor yang sama dengan koleksi dokumen SOP agar jaraknya dapat dihitung.',
    inputLabel: 'Normalized Query',
    outputLabel: 'Query Vector (384-d)',
    sampleData: '[-0.0392, 0.1310, 0.0845, -0.1988, ..., 0.0599]'
  },
  {
    id: 'qry-4',
    stepNumber: 4,
    pipeline: 'query',
    title: 'Vector Retrieval',
    subtitle: 'Top-K Similarity Search',
    description:
      'Mencari Top-K potongan dokumen (chunks) di dalam ChromaDB yang memiliki nilai kemiripan tertinggi terhadap vektor pertanyaan.',
    technicalRole: 'Menyaring hanya segmen dokumen SOP yang paling relevan dengan pertanyaan pengguna.',
    inputLabel: 'Query Vector (384-d)',
    outputLabel: 'Top-K Ranked Document Chunks',
    sampleData: 'Top-1: PM1_SKTM_KELURAHAN (Score: 0.89) | Top-2: PANDUAN_JAKEVO (Score: 0.74)'
  },
  {
    id: 'qry-5',
    stepNumber: 5,
    pipeline: 'query',
    title: 'Context Construction',
    subtitle: 'Grounded Prompt Assembly',
    description:
      'Menggabungkan potongan dokumen hasil retrieval beserta instruksi sistem (system prompt) dan pertanyaan pengguna menjadi satu paket konteks terstruktur.',
    technicalRole: 'Membatasi ruang gerak LLM agar merumuskan jawaban semata-mata dari fakta dokumen yang ditemukan.',
    inputLabel: 'Top-K Chunks + User Query',
    outputLabel: 'Augmented Grounded Prompt',
    sampleData: 'System: Jawab hanya berdasarkan konteks berikut.\nContext: [PM1_SKTM_KELURAHAN...]\nQuestion: Apa syarat SKTM?'
  },
  {
    id: 'qry-6',
    stepNumber: 6,
    pipeline: 'query',
    title: 'LLM Generation',
    subtitle: 'Context-Grounded Synthesis',
    description:
      'Large Language Model membaca konteks dokumen yang diberikan dan menyusun jawaban yang terstruktur, sopan, dan mudah dipahami pengguna.',
    technicalRole: 'Menerjemahkan potongan teks teknis SOP menjadi penjelasan layanan yang jelas tanpa mengarang informasi di luar dokumen.',
    inputLabel: 'Augmented Grounded Prompt',
    outputLabel: 'Synthesized Response Text',
    sampleData: 'Menyusun daftar poin persyaratan SKTM beserta informasi estimasi waktu layanan.'
  },
  {
    id: 'qry-7',
    stepNumber: 7,
    pipeline: 'query',
    title: 'Final Answer',
    subtitle: 'Verified Answer + Source Citation',
    description:
      'Menampilkan jawaban akhir kepada pengguna di antarmuka chatbot lengkap dengan referensi nama dokumen sumber dan halaman terkait.',
    technicalRole: 'Memberikan transparansi dan kepastian informasi sehingga pengguna dapat memverifikasi sumber aturan secara langsung.',
    inputLabel: 'Synthesized Response + Metadata',
    outputLabel: 'UI Chat Bubble & Source Card',
    sampleData: 'Jawaban Persyaratan SKTM + Sitasi: [PM1_SKTM_KELURAHAN-WEB-SYARAT · Hal. 2]'
  }
];

export const TECH_STACK_ITEMS: TechStackItem[] = [
  {
    id: 'tech-python',
    name: 'Python',
    category: 'Core Language & Backend Runtime',
    description:
      'Bahasa pemrograman utama yang menjalankan seluruh pipeline pemrosesan dokumen, ekstraksi teks, komputasi vektor, hingga orkestrasi API.',
    systemRole: 'Menghubungkan modul ekstraksi PDF, model embedding, basis data vektor ChromaDB, dan layanan API backend.',
    specDetail: 'Python 3.x Ecosystem'
  },
  {
    id: 'tech-chromadb',
    name: 'ChromaDB',
    category: 'Vector Database',
    description:
      'Basis data vektor khusus untuk menyimpan hasil embedding potongan dokumen (chunks) beserta metadata sumber dan menjalankan pencarian kemiripan.',
    systemRole: 'Menyimpan koleksi vektor dokumen SOP JAKEVO dan mengeksekusi kueri Top-K retrieval berdasarkan kedekatan vektor.',
    specDetail: 'Persistent Vector Store & Metadata Filtering'
  },
  {
    id: 'tech-sentence-transformers',
    name: 'Sentence Transformers',
    category: 'Embedding Framework',
    description:
      'Framework Python untuk menghasilkan dense vector representations pada level kalimat dan paragraf secara efisien.',
    systemRole: 'Memuat dan menjalankan model embedding lokal untuk mengubah potongan dokumen maupun kueri pengguna menjadi vektor.',
    specDetail: 'HuggingFace / PyTorch SentenceEmbeddings'
  },
  {
    id: 'tech-minilm',
    name: 'paraphrase-multilingual-MiniLM-L12-v2',
    category: 'Multilingual Embedding Model',
    description:
      'Model embedding multibahasa yang memetakan kalimat dan paragraf ke dalam ruang vektor berdimensi 384 untuk pencarian semantik lintas variasi kalimat.',
    systemRole: 'Menangkap kemiripan makna pertanyaan pengguna berbahasa Indonesia meskipun kata yang digunakan berbeda dari teks kaku di SOP.',
    specDetail: '384-Dimensional Dense Vector Space'
  },
  {
    id: 'tech-rag',
    name: 'Retrieval-Augmented Generation (RAG)',
    category: 'System Architecture Pattern',
    description:
      'Paradigma arsitektur yang mengombinasikan sistem temu kembali informasi (information retrieval) dari dokumen otoritatif dengan kemampuan sintesis bahasa.',
    systemRole: 'Memastikan setiap jawaban chatbot didasarkan pada konteks dokumen pelayanan administrasi yang ditemukan, bukan hafalan bebas model.',
    specDetail: 'Retrieve → Augment → Generate Workflow'
  },
  {
    id: 'tech-llm',
    name: 'Large Language Model (LLM)',
    category: 'Natural Language Synthesis',
    description:
      'Model bahasa besar yang bertugas membaca potongan konteks dokumen hasil retrieval dan menyusunnya menjadi jawaban percakapan yang rapi.',
    systemRole: 'Merangkum dan memformat prosedur serta persyaratan dokumen menjadi poin-poin yang mudah dibaca oleh masyarakat.',
    specDetail: 'Context-Constrained Response Generation'
  },
  {
    id: 'tech-pdf',
    name: 'PDF Processing',
    category: 'Document Ingestion & Parsing',
    description:
      'Komponen pembacaan dan ekstraksi teks dari berkas dokumen PDF pelayanan administrasi menjadi teks terstruktur siap olah.',
    systemRole: 'Mengekstrak isi halaman dokumen panduan dan SOP PDF sebelum masuk ke tahap data cleaning dan chunking.',
    specDetail: 'Page-Level Text & Metadata Extraction'
  }
];

export const EVALUATION_METRICS: EvaluationMetricItem[] = [
  {
    id: 'eval-hit-k',
    name: 'Hit@K (Hit Rate at K)',
    shortCode: 'HIT@K',
    formula: 'Hit@K = (1 / |Q|) × Σ I(Rank_q ≤ K)',
    description:
      'Mengukur proporsi pertanyaan uji di mana setidaknya terdapat satu potongan dokumen (chunk) yang relevan di dalam daftar Top-K hasil retrieval.',
    howItWorks:
      'Bernilai 1 (Hit) untuk sebuah pertanyaan apabila dokumen sumber yang benar berhasil muncul di urutan 1 hingga K, dan bernilai 0 (Miss) jika tidak muncul di Top-K.',
    placeholderValue: '[MENUNGGU DATA UJI AKTUAL]',
    visualExample: {
      query: 'Apa saja syarat mengurus SKTM di kelurahan?',
      topK: [
        { rank: 1, docId: 'DOC-JAKEVO-001 (Alamat Kantor)', isRelevant: false, similarity: 'Simulasi' },
        { rank: 2, docId: 'PM1_SKTM_KELURAHAN (Syarat SKTM)', isRelevant: true, similarity: 'Target Ditemukan' },
        { rank: 3, docId: 'PANDUAN_JAKEVO_PEMOHON (Alur Umum)', isRelevant: false, similarity: 'Simulasi' }
      ],
      calculationNote: 'Pada contoh K=3 di atas, dokumen relevan ditemukan pada Rank #2 → Status: HIT (1).'
    }
  },
  {
    id: 'eval-recall-k',
    name: 'Recall@K',
    shortCode: 'RECALL@K',
    formula: 'Recall@K = |Relevant_Retrieved@K| / |Total_Relevant_Docs|',
    description:
      'Mengukur seberapa lengkap sistem berhasil mengambil seluruh potongan dokumen relevan yang seharusnya ditemukan untuk menjawab suatu pertanyaan.',
    howItWorks:
      'Membandingkan jumlah chunk relevan yang berhasil masuk dalam Top-K terhadap total seluruh chunk relevan yang ada di dalam basis data untuk pertanyaan tersebut.',
    placeholderValue: '[MENUNGGU DATA UJI AKTUAL]',
    visualExample: {
      query: 'Bagaimana prosedur dan syarat lengkap izin praktik dokter?',
      topK: [
        { rank: 1, docId: 'SIP_DOKTER_CHUNK_01 (Syarat Berkas STR & KTP)', isRelevant: true, similarity: 'Relevan 1/2' },
        { rank: 2, docId: 'PANDUAN_JAKEVO_CHUNK_04 (Cara Login Akun)', isRelevant: false, similarity: 'Non-Target' },
        { rank: 3, docId: 'SIP_DOKTER_CHUNK_02 (Ketentuan SKP & Klinik)', isRelevant: true, similarity: 'Relevan 2/2' }
      ],
      calculationNote: 'Ilustrasi konsep: Jika total chunk relevan di database adalah 2 dan keduanya terambil di Top-3, maka kelengkapan konteks tercapai.'
    }
  },
  {
    id: 'eval-mrr',
    name: 'Mean Reciprocal Rank (MRR)',
    shortCode: 'MRR',
    formula: 'MRR = (1 / |Q|) × Σ (1 / Rank_first_relevant)',
    description:
      'Mengevaluasi seberapa tinggi posisi peringkat dokumen relevan pertama yang berhasil ditempatkan oleh sistem retrieval.',
    howItWorks:
      'Jika dokumen yang benar berada di peringkat 1, skor resiprokalnya adalah 1/1 = 1.00. Jika di peringkat 2, skornya 1/2 = 0.50. Jika di peringkat 3, skornya 1/3 = 0.33.',
    placeholderValue: '[MENUNGGU DATA UJI AKTUAL]',
    visualExample: {
      query: 'Di mana lokasi kantor DPMPTSP DKI Jakarta?',
      topK: [
        { rank: 1, docId: 'DOC-JAKEVO-001 (Lokasi MPP Lt. 5 Setiabudi)', isRelevant: true, similarity: 'RR = 1/1' },
        { rank: 2, docId: 'DOC-PTSP-005 (Eskalasi Layanan)', isRelevant: false, similarity: '-' },
        { rank: 3, docId: 'PANDUAN_JAKEVO_PEMOHON', isRelevant: false, similarity: '-' }
      ],
      calculationNote: 'Ilustrasi konsep: Dokumen relevan pertama muncul di Rank #1 memberikan Reciprocal Rank (RR) = 1/1.'
    }
  },
  {
    id: 'eval-accuracy',
    name: 'Retrieval Accuracy',
    shortCode: 'ACCURACY',
    formula: 'Accuracy = Correct_Retrievals / Total_Evaluated_Queries',
    description:
      'Mengukur ketepatan keseluruhan sistem dalam memetakan pertanyaan pengguna ke dokumen prosedur administrasi yang tepat.',
    howItWorks:
      'Menghitung rasio kueri pengujian yang berhasil mengambil konteks dokumen yang tepat dibandingkan dengan total seluruh skenario kueri pengujian.',
    placeholderValue: '[MENUNGGU DATA UJI AKTUAL]',
    visualExample: {
      query: 'Evaluasi Kumpulan Pertanyaan Uji (Test Set)',
      topK: [
        { rank: 1, docId: 'Kueri Spesifik Layanan Kelurahan (PM1)', isRelevant: true, similarity: 'Terpetakan' },
        { rank: 2, docId: 'Kueri Alur Penggunaan Aplikasi JAKEVO', isRelevant: true, similarity: 'Terpetakan' },
        { rank: 3, docId: 'Kueri Istilah Singkatan / Ambiguitas Layanan', isRelevant: false, similarity: 'Perlu Analisis' }
      ],
      calculationNote: 'Metrik aktual akan diisi setelah pengujian kumpulan pertanyaan (test dataset) selesai dijalankan.'
    }
  }
];

export const RETRIEVAL_ERROR_CATEGORIES = [
  {
    id: 'err-1',
    code: 'ERR-01',
    title: 'Terminology & Acronym Mismatch',
    description:
      'Pengguna menggunakan singkatan lokal atau istilah sehari-hari yang tidak tertulis secara eksplisit di dalam teks formal dokumen SOP.',
    mitigation: 'Penambahan sinonim kata kunci administrasi dan pengayaan metadata pada setiap chunk dokumen.'
  },
  {
    id: 'err-2',
    code: 'err-2',
    title: 'Chunk Boundary Fragmentation',
    description:
      'Daftar persyaratan yang panjang terpotong di tengah-tengah pergantian halaman PDF atau batas ukuran chunk sehingga konteks terpisah.',
    mitigation: 'Penyesuaian ukuran chunk overlap dan pemisahan segmen berdasarkan struktur heading prosedur.'
  },
  {
    id: 'err-3',
    code: 'err-3',
    title: 'Overlapping Administrative Procedures',
    description:
      'Beberapa dokumen layanan memiliki syarat dasar yang sangat mirip (misal: KTP, KK, Pengantar RT/RW) sehingga kemiripan vektor antar-dokumen berdekatan.',
    mitigation: 'Menyertakan judul spesifik layanan di setiap awal potongan teks (chunk header prefixing) sebelum proses embedding.'
  }
];
