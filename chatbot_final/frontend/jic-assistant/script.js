/**

 * ==============================================================================

 * SCRIPT JS - JAKEVO ASSISTANT (PORTFOLIO EDITION)

 * Integrasi Lengkap: RAG Pipeline Simulator, Interactive Portfolio & Chatbot Widget

 * ==============================================================================

 */



document.addEventListener('DOMContentLoaded', () => {



  /* ==========================================================================

     1. KNOWLEDGE BASE RESMI JAKEVO & SIMULASI RAG (DUMMY DATA TERVERIFIKASI)

     ========================================================================== */

  const KNOWLEDGE_BASE = [
    {
      id: "DOC-ALAMAT-DPMPTSP",
      topic: "Alamat & Kontak Kantor DPMPTSP",
      question: "Di mana alamat kantor DPMPTSP?",
      keywords: [
        "alamat", "kantor", "lokasi", "gedung", "dimana", "di mana", "mpp", 
        "kuningan", "rasuna said", "setiabudi", "dki", "jakarta", "kontak", 
        "telepon", "email", "lantai", "kunjungi", "jam buka", "operasional", "datang",
        "dpmptsp", "ptsp"
      ],
      sourceDoc: "ALAMAT_DAN_PROFIL_DPMPTSP.pdf (DPMPTSP Provinsi DKI Jakarta)",
      contextSnippet: "Gedung Mal Pelayanan Publik (MPP) Provinsi DKI Jakarta Lantai 5, Jl. H.R. Rasuna Said Kav. C-22, Karet Kuningan, Setiabudi, Jakarta Selatan 12920. Jam operasional: Senin-Kamis 07.30-16.00 WIB, Jumat 07.30-16.30 WIB.",
      answer: `
        <p>Kantor <strong>Dinas Penanaman Modal dan Pelayanan Terpadu Satu Pintu (DPMPTSP) Provinsi DKI Jakarta</strong> berlokasi di:</p>
        <p>📍 <strong>Gedung Mal Pelayanan Publik (MPP) Provinsi DKI Jakarta, Lantai 5</strong><br>
        Jl. H.R. Rasuna Said Kav. C-22, RT.02 / RW.05, Karet Kuningan, Setiabudi, Jakarta Selatan 12920.</p>
        <p>⏰ <strong>Jam Operasional Layanan:</strong><br>
        • Senin – Kamis: 07.30 – 16.00 WIB<br>
        • Jumat: 07.30 – 16.30 WIB (Istirahat 11.30 – 13.00 WIB)<br>
        • Portal JAKEVO (<em>jakevo.jakarta.go.id</em>) dapat diakses mandiri 24 jam setiap hari.</p>
        <p>📞 <strong>Kontak Resmi:</strong><br>
        • <strong>Call Center PTSP:</strong> 1500-164 atau (021) 1500164<br>
        • <strong>Telepon:</strong> (021) 5200300<br>
        • <strong>Email:</strong> dpmptsp@jakarta.go.id / pengaduandpmptsp@jakarta.go.id</p>
      `
    },
    {
      id: "DOC-ALUR-JAKEVO",
      topic: "Alur Permohonan Izin JAKEVO",
      question: "Bagaimana alur pengajuan izin di JAKEVO?",
      keywords: [
        "alur", "proses", "pengajuan", "izin", "tahapan", "cara", "daftar", "langkah",
        "jakevo", "permohonan", "buat izin", "unggah", "upload", "status", "revisi", "perbaikan"
      ],
      sourceDoc: "data.pdf (Petunjuk Penggunaan Aplikasi JAKEVO untuk Pemohon)",
      contextSnippet: "Alur pengajuan perizinan JAKEVO: 1. Registrasi Akun dan Login di jakevo.jakarta.go.id; 2. Pilih menu Buat Permohonan Baru; 3. Isi formulir perizinan dan unggah dokumen persyaratan; 4. Verifikasi administrasi oleh Petugas PTSP; 5. Penetapan izin dengan tanda tangan elektronik; 6. Izin Terbit siap diunduh.",
      answer: `
        <p>Berikut tahapan resmi <strong>Alur Pengajuan Izin di Aplikasi JAKEVO</strong> (<em>jakevo.jakarta.go.id</em>):</p>
        <ol>
          <li><strong>Pendaftaran &amp; Login Akun:</strong> Masuk ke portal JAKEVO, lengkapi profil pemohon (perorangan atau badan usaha).</li>
          <li><strong>Buat Permohonan Baru:</strong> Pilih menu perizinan yang diinginkan (misal: PM1 Kelurahan, SIP Dokter, IPTM Makam, dsb.).</li>
          <li><strong>Unggah Dokumen Persyaratan:</strong> Unggah scan berkas dokumen asli (PDF/JPG) sesuai persyaratan izin yang dipilih.</li>
          <li><strong>Verifikasi Administrasi Petugas PTSP:</strong> Petugas memvalidasi berkas. Jika ada kekurangan, status berubah menjadi <em>Butuh Perbaikan</em> dan pemohon dapat mengunggah revisi.</li>
          <li><strong>Penetapan &amp; Tanda Tangan Elektronik:</strong> Penandatanganan draf izin secara digital oleh Kepala Kantor atau Pejabat berwenang.</li>
          <li><strong>Izin Terbit:</strong> Dokumen resmi diterbitkan dengan barcode QR-code verifikasi dan dapat langsung diunduh secara mandiri.</li>
        </ol>
      `
    },
    {
      id: "DOC-PROFIL-JAKEVO",
      topic: "Definisi & Peran JAKEVO",
      question: "Apa itu JAKEVO?",
      keywords: [
        "apa", "itu", "jakevo", "jakarta", "evolution", "perizinan", "profil", "tentang", 
        "fungsi", "peran", "dpmptsp", "pengertian", "definisi", "portal", "website"
      ],
      sourceDoc: "data.pdf & ALAMAT_DAN_PROFIL_DPMPTSP.pdf",
      contextSnippet: "JAKEVO (Jakarta Evolution) adalah sistem aplikasi pelayanan perizinan dan non-perizinan digital terpadu satu pintu milik Pemerintah Provinsi DKI Jakarta di bawah pengelolaan DPMPTSP Provinsi DKI Jakarta.",
      answer: `
        <p><strong>JAKEVO (Jakarta Evolution)</strong> adalah sistem pelayanan perizinan dan non-perizinan daring resmi milik <strong>Pemerintah Provinsi DKI Jakarta</strong> yang dikelola oleh <strong>DPMPTSP DKI Jakarta</strong>.</p>
        <p>Melalui portal <a href="https://jakevo.jakarta.go.id" target="_blank" rel="noopener noreferrer" style="color:#60a5fa; text-decoration: underline;">jakevo.jakarta.go.id</a>, warga dan pelaku usaha dapat:</p>
        <ul>
          <li>Mengajukan perizinan perorangan (Pelayanan Administrasi Kelurahan PM1, SKTM, Belum Rumah, dsb.).</li>
          <li>Mengajukan perizinan tenaga medis (Surat Izin Praktik Dokter / SIP Dokter).</li>
          <li>Mengajukan perizinan sektor lingkungan &amp; pemakaman (Izin Tanah Makam / IPTM, Angkutan Kebersihan).</li>
          <li>Memantau status berkas secara <em>real-time</em> tanpa perlu datang langsung ke loket kantor fisik.</li>
        </ul>
      `
    },
    {
      id: "DOC-PM1-RUMAH",
      topic: "Surat Keterangan Belum Memiliki Rumah (KPR)",
      question: "Apa syarat surat keterangan belum memiliki rumah?",
      keywords: [
        "rumah", "belum", "memiliki", "kpr", "pm1", "kelurahan", "syarat", "persyaratan",
        "perumahan", "surat belum punya rumah", "keterangan belum rumah"
      ],
      sourceDoc: "PM1_KETERANGAN_BELUM_MEMILIKI_RUMAH.txt (Layanan Administrasi PTSP Kelurahan)",
      contextSnippet: "Persyaratan Surat Keterangan Belum Memiliki Rumah (PM1 - KPR): 1. Identitas Pemohon (KTP/KITAS); 2. Surat Pernyataan Pengganti RT/RW; 3. Surat Pernyataan di atas kertas bermaterai Rp 10.000 bahwa belum mempunyai rumah; 4. Surat kuasa bermaterai jika dikuasakan. Estimasi 1 hari kerja, tanpa retribusi (gratis).",
      answer: `
        <p>Berdasarkan dokumen resmi PTSP Kelurahan, persyaratan <strong>Surat Keterangan Belum Memiliki Rumah (PM1 - KPR)</strong> meliputi:</p>
        <ol>
          <li><strong>Identitas Pemohon:</strong> Scan KTP Pemohon asli (atau KITAS/Paspor untuk WNA).</li>
          <li><strong>Surat Pengantar RT/RW:</strong> Surat pengantar keterangan dari RT dan RW setempat.</li>
          <li><strong>Surat Pernyataan Belum Memiliki Rumah:</strong> Surat pernyataan di atas kertas bermaterai Rp 10.000 yang menyatakan pemohon belum memiliki rumah.</li>
          <li><strong>Surat Kuasa (Bila Dikuasakan):</strong> Surat kuasa bermaterai Rp 10.000 beserta scan KTP pihak yang diberi kuasa.</li>
        </ol>
        <p>⏱️ <strong>Estimasi Waktu:</strong> 1 Hari Kerja<br>
        💰 <strong>Biaya Retribusi:</strong> <strong>Rp 0 (Tanpa Retribusi / Gratis)</strong></p>
      `
    },
    {
      id: "DOC-PM1-SKTM",
      topic: "Surat Keterangan Tidak Mampu (SKTM)",
      question: "Apa saja syarat Surat Keterangan Tidak Mampu (SKTM)?",
      keywords: [
        "sktm", "tidak mampu", "surat tidak mampu", "miskin", "bantuan", "sekolah", "kjp",
        "kip", "beasiswa", "pengobatan", "kelurahan", "pm1", "syarat sktm"
      ],
      sourceDoc: "PM1_SURAT_KETERANGAN_TIDAK_MAMPU.txt (Layanan Administrasi PTSP Kelurahan)",
      contextSnippet: "Persyaratan Surat Keterangan Tidak Mampu (SKTM - PM1): 1. Surat Pengantar RT/RW; 2. Surat Pernyataan Tidak Mampu bermaterai Rp 10.000; 3. Scan KTP dan Kartu Keluarga (KK) Pemohon. Estimasi 1 hari kerja, tanpa retribusi.",
      answer: `
        <p>Persyaratan resmi permohonan <strong>Surat Keterangan Tidak Mampu (SKTM - PM1)</strong> di PTSP Kelurahan:</p>
        <ol>
          <li><strong>Surat Pengantar RT/RW:</strong> Pengantar dari pengurus RT dan RW tempat domisili.</li>
          <li><strong>Surat Pernyataan Tidak Mampu:</strong> Surat pernyataan kondisi ekonomi keluarga di atas kertas bermaterai Rp 10.000.</li>
          <li><strong>Identitas Kependudukan:</strong> Scan asli Kartu Tanda Penduduk (KTP) dan Kartu Keluarga (KK) pemohon DKI Jakarta.</li>
        </ol>
        <p>⏱️ <strong>Estimasi Waktu Pelayanan:</strong> 1 Hari Kerja<br>
        💰 <strong>Biaya Retribusi:</strong> <strong>Gratis (Rp 0)</strong></p>
      `
    },
    {
      id: "DOC-SIP-DOKTER",
      topic: "Surat Izin Praktik Dokter (SIP Dokter)",
      question: "Apa saja syarat surat izin praktik dokter?",
      keywords: [
        "sip", "dokter", "praktik", "izin praktik", "str", "kki", "idi", "klinik",
        "rumah sakit", "faskes", "syarat sip", "medis"
      ],
      sourceDoc: "SURAT_IZIN_PRAKTIK_DOKTER.txt (Layanan Perizinan Kesehatan DPMPTSP DKI)",
      contextSnippet: "Persyaratan Surat Izin Praktik Dokter: 1. Surat Tanda Registrasi (STR) dokter yang diterbitkan oleh KKI dan masih berlaku; 2. Surat Rekomendasi dari Organisasi Profesi (IDI) di wilayah tempat praktik; 3. Surat persetujuan/keterangan dari pimpinan fasilitas pelayanan kesehatan; 4. Pasfoto berwarna terbaru.",
      answer: `
        <p>Persyaratan permohonan <strong>Surat Izin Praktik Dokter (SIP Dokter)</strong> di Provinsi DKI Jakarta:</p>
        <ol>
          <li><strong>Surat Tanda Registrasi (STR):</strong> Scan asli STR dokter dari Konsil Kedokteran Indonesia (KKI) yang masih berlaku.</li>
          <li><strong>Rekomendasi Organisasi Profesi:</strong> Surat rekomendasi dari Ikatan Dokter Indonesia (IDI) cabang setempat di wilayah DKI Jakarta.</li>
          <li><strong>Surat Keterangan Fasilitas Praktik:</strong> Surat persetujuan/pernyataan dari pimpinan faskes (Klinik / RS / Puskesmas) tempat dokter berpraktik.</li>
          <li><strong>Identitas &amp; Pasfoto:</strong> Scan KTP pemohon dan pasfoto formal terbaru berwarna.</li>
        </ol>
      `
    },
    {
      id: "DOC-PM1-NIKAH",
      topic: "Surat Pengantar Perkawinan (Pertama & Bawah Umur)",
      question: "Apa syarat surat pengantar perkawinan?",
      keywords: [
        "nikah", "kawin", "perkawinan", "pertama", "bawah umur", "dispensasi", "layak kawin",
        "kua", "puskesmas", "pengadilan", "syarat nikah", "pm1 perkawinan"
      ],
      sourceDoc: "PM1_PERKAWINAN_PERTAMA.txt & PM1_PERKAWINAN_BAWAH_UMUR.txt",
      contextSnippet: "Surat Pengantar Perkawinan Pertama memerlukan Sertifikat Layak Kawin dari Puskesmas. Perkawinan di Bawah Umur (< 19 tahun) memerlukan Surat Izin/Dispensasi dari Pengadilan Agama atau Pengadilan Negeri dan KTP/KK orang tua.",
      answer: `
        <p>Persyaratan <strong>Surat Pengantar Perkawinan (PM1 Kelurahan)</strong> terbagi atas dua kategori:</p>
        <p>💍 <strong>1. Perkawinan Pertama:</strong></p>
        <ul>
          <li>Scan asli <strong>Sertifikat Layak Kawin</strong> pemohon dari Puskesmas Kecamatan setempat.</li>
          <li>Surat Pengantar RT/RW, scan KTP, KK, dan akta kelahiran pemohon.</li>
        </ul>
        <p>📜 <strong>2. Perkawinan di Bawah Umur (&lt; 19 Tahun):</strong></p>
        <ul>
          <li><strong>Surat Izin Menikah / Dispensasi:</strong> Dari Pengadilan Agama (Islam) atau Pengadilan Negeri (non-Islam).</li>
          <li>Scan asli KTP dan Kartu Keluarga (KK) orang tua kandung pemohon.</li>
          <li>Surat Pengantar RT/RW dan identitas pemohon.</li>
        </ul>
        <p>Layanan diselesaikan dalam 1 hari kerja tanpa retribusi (gratis).</p>
      `
    },
    {
      id: "DOC-IPTM-MAKAM",
      topic: "Izin Penggunaan Tanah Makam (IPTM)",
      question: "Apa saja syarat izin penggunaan tanah makam?",
      keywords: [
        "makam", "tanah makam", "iptm", "pemakaman", "tpu", "tumpangan", "jenazah",
        "kematian", "syarat makam"
      ],
      sourceDoc: "IZIN_PENGGUNAAN_TANAH_MAKAM.txt (Layanan Pemakaman DPMPTSP DKI)",
      contextSnippet: "Persyaratan Izin Penggunaan Tanah Makam (IPTM): Surat Keterangan Pemeriksaan Jenazah / Kematian dari RS/Puskesmas/Kelurahan, KTP/KK pemohon atau ahli waris, KTP/KK jenazah, dan surat persetujuan tumpangan jika makam tumpangan.",
      answer: `
        <p>Persyaratan permohonan <strong>Izin Penggunaan Tanah Makam (IPTM)</strong> di TPU DKI Jakarta:</p>
        <ol>
          <li><strong>Surat Keterangan Kematian:</strong> Scan asli surat pemeriksaan jenazah / kematian dari RS, Puskesmas, atau Kelurahan setempat.</li>
          <li><strong>Identitas Pemohon / Ahli Waris:</strong> Scan KTP dan Kartu Keluarga (KK) ahli waris yang bertanggung jawab.</li>
          <li><strong>Identitas Jenazah:</strong> Scan KTP dan KK almarhum/almarhumah yang dimakamkan.</li>
          <li><strong>Untuk Makam Tumpangan:</strong> Surat persetujuan bermaterai dari keluarga/ahli waris pemilik makam terdahulu.</li>
        </ol>
      `
    }
  ];



  /* ==========================================================================

     2. ELEMEN DOM UTAMA & INISIALISASI

     ========================================================================== */

  const spinner = document.getElementById('spinner');

  const mainNavbar = document.getElementById('mainNavbar');

  const backToTopBtn = document.getElementById('backToTopBtn');



  const jicChatbotCard = document.getElementById('jicChatbotCard');

  const toggleFullScreenBtn = document.getElementById('toggleFullScreenBtn');

  const minimizeChatBtn = document.getElementById('minimizeChatBtn');

  const resetChatBtn = document.getElementById('resetChatBtn');

  const floatingChatBtn = document.getElementById('floatingChatBtn');

  

  const chatMessages = document.getElementById('chatMessages');

  const chatArea = document.getElementById('chatArea');

  const chatForm = document.getElementById('chatForm');

  const userInput = document.getElementById('userInput');

  const sendBtn = document.getElementById('sendBtn');

  const ragToggleCheckbox = document.getElementById('ragToggleCheckbox');

  const initialTimeEl = document.getElementById('initialTime');

  const quickChips = document.querySelectorAll('.chip-btn');



  /* ==========================================================================

     3. PRELOADER & NAVBAR SCROLL

     ========================================================================== */

  const hideSpinner = () => {

    if (spinner) {

      spinner.classList.add('hide');

      setTimeout(() => {

        spinner.style.display = 'none';

      }, 400);

    }

  };



  if (document.readyState === 'complete') {

    hideSpinner();

  } else {

    window.addEventListener('load', hideSpinner);

    setTimeout(hideSpinner, 1000);

  }



  // Navbar scroll shadow

  window.addEventListener('scroll', () => {

    if (window.scrollY > 40) {

      mainNavbar.classList.add('navbar-scrolled');

    } else {

      mainNavbar.classList.remove('navbar-scrolled');

    }



    if (backToTopBtn) {

      if (window.scrollY > 350) {

        backToTopBtn.classList.add('active');

      } else {

        backToTopBtn.classList.remove('active');

      }

    }

  });



  // Smooth scroll Back-to-Top

  if (backToTopBtn) {

    backToTopBtn.addEventListener('click', (e) => {

      e.preventDefault();

      window.scrollTo({ top: 0, behavior: 'smooth' });

    });

  }



  // Auto-close navbar on click in mobile

  const navLinks = document.querySelectorAll('.portfolio-navbar .nav-link');

  const navCollapse = document.getElementById('portfolioNavContent');

  navLinks.forEach(link => {

    link.addEventListener('click', () => {

      if (window.innerWidth < 992 && navCollapse && navCollapse.classList.contains('show')) {

        const bsCollapse = bootstrap.Collapse.getInstance(navCollapse);

        if (bsCollapse) bsCollapse.hide();

      }

    });

  });



  /* ==========================================================================

     4. PROFIL MAHASISWA (FIXED CODED ASSETS)

     ========================================================================== */

  // Foto dan data identitas mahasiswa PKL dikunci langsung pada kode HTML/CSS.



  /* ==========================================================================

     5. KONTROL POP-UP CHATBOT (BUKA / TUTUP / TOGGLE)

     ========================================================================== */

  let isChatbotOpen = false;



  function openChatbot() {

    isChatbotOpen = true;

    document.body.classList.add('chatbot-is-active');

    if (jicChatbotCard) {

      jicChatbotCard.classList.add('is-open');

      jicChatbotCard.setAttribute('aria-hidden', 'false');

    }

    

    // Perbarui Tombol Floating Bubble

    if (floatingChatBtn) {

      floatingChatBtn.classList.add('is-chat-open');

      const label = document.getElementById('floatingBtnLabel');

      const sub = document.getElementById('floatingBtnSub');

      if (label) label.textContent = 'Tutup Chatbot';

      if (sub) sub.textContent = 'Klik untuk Menutup';

      floatingChatBtn.setAttribute('title', 'Tutup Chatbot JAKEVO Assistant');

    }



    setTimeout(() => {

      if (userInput) userInput.focus();

      scrollToBottom();

    }, 280);

  }



  function closeChatbot() {

    isChatbotOpen = false;

    document.body.classList.remove('chatbot-is-active');

    if (jicChatbotCard) {

      jicChatbotCard.classList.remove('is-open');

      jicChatbotCard.classList.remove('fullscreen-chat-mode');

      jicChatbotCard.setAttribute('aria-hidden', 'true');

      document.body.style.overflow = '';

      const fsLabel = toggleFullScreenBtn ? toggleFullScreenBtn.querySelector('.btn-fs-label') : null;

      if (fsLabel) fsLabel.textContent = "Penuh";

    }



    // Kembalikan Tombol Floating Bubble

    if (floatingChatBtn) {

      floatingChatBtn.classList.remove('is-chat-open');

      const label = document.getElementById('floatingBtnLabel');

      const sub = document.getElementById('floatingBtnSub');

      if (label) label.textContent = 'Buka Chatbot';

      if (sub) sub.textContent = 'JAKEVO Assistant Online';

      floatingChatBtn.setAttribute('title', 'Buka Chatbot JAKEVO Assistant');

    }

  }



  function toggleChatbot() {

    if (isChatbotOpen) {

      closeChatbot();

    } else {

      openChatbot();

    }

  }



  // Triggers untuk membuka/menutup Chatbot

  if (floatingChatBtn) {

    floatingChatBtn.addEventListener('click', (e) => {

      e.preventDefault();

      toggleChatbot();

    });

  }



  const triggerButtons = [

    document.getElementById('openChatNavBtn'),

    document.getElementById('scrollChatHeroBtn'),

    document.getElementById('triggerChatFromCard'),

    document.getElementById('openChatDemoStudioBtn'),

    document.getElementById('footerChatBtn')

  ];



  triggerButtons.forEach(btn => {

    if (btn) {

      btn.addEventListener('click', (e) => {

        e.preventDefault();

        openChatbot();

      });

    }

  });



  if (minimizeChatBtn) {

    minimizeChatBtn.addEventListener('click', (e) => {

      e.preventDefault();

      closeChatbot();

    });

  }



  // Keyboard shortcut ESC

  document.addEventListener('keydown', (e) => {

    if (e.key === 'Escape' && isChatbotOpen) {

      closeChatbot();

    }

  });



  // Toggle Full Screen Mode

  if (toggleFullScreenBtn && jicChatbotCard) {

    toggleFullScreenBtn.addEventListener('click', () => {

      if (!isChatbotOpen) {

        openChatbot();

      }

      const isFullscreen = jicChatbotCard.classList.toggle('fullscreen-chat-mode');

      const label = toggleFullScreenBtn.querySelector('.btn-fs-label');

      if (isFullscreen) {

        if (label) label.textContent = "Keluar";

        document.body.style.overflow = 'hidden';

      } else {

        if (label) label.textContent = "Penuh";

        document.body.style.overflow = '';

      }

      scrollToBottom();

    });

  }



  // Reset Percakapan

  if (resetChatBtn) {

    resetChatBtn.addEventListener('click', () => {

      if (confirm('Apakah Anda ingin memulai ulang percakapan dengan JAKEVO Assistant?')) {

        chatMessages.innerHTML = `

          <div class="chat-message bot-message">

            ${getBetawiAvatarHtml()}

            <div class="message-content-wrapper">

              <div class="bot-bubble modern-bot-bubble">

                <div class="bubble-header">

                  <div class="bot-label-group">

                    <span class="bot-label">✨ Chatbot JAKEVO</span>

                    <span class="ai-verified-badge">Resmi DPMPTSP</span>

                  </div>

                </div>

                <div class="bubble-body">

                  <p>Percakapan telah direset. Silakan pilih salah satu pertanyaan cepat di atas atau ketik pertanyaan seputar investasi dan perizinan Jakarta Anda.</p>

                </div>

                

                <div class="rag-source-citation">

                  <div class="source-header-row">

                    <span class="source-icon">📚</span>

                    <span class="source-label-text">Sumber Dokumen RAG:</span>

                  </div>

                  <div class="source-content-box">

                    <span class="source-doc-id">DOC-INIT-000</span>

                    <span class="source-doc-name">SOP Layanan Informasi Investasi &amp; Panduan PTSP DKI Jakarta</span>

                    <span class="source-verified-tag">✓ Terverifikasi DPMPTSP</span>

                  </div>

                </div>



                <div class="bubble-footer">

                  <span class="message-time">${getFormattedTime()}</span>

                </div>

              </div>

            </div>

          </div>

        `;

        scrollToBottom();

      }

    });

  }



  // Tombol Topik Khusus di Kartu / Studio Demo

  document.querySelectorAll('.btn-ask-topic').forEach(btn => {

    btn.addEventListener('click', (e) => {

      e.preventDefault();

      if (!isChatbotOpen) {

        openChatbot();

      }

      const askQuery = btn.getAttribute('data-ask');

      if (askQuery) {

        setTimeout(() => {

          handleSendMessage(askQuery);

        }, 320);

      }

    });

  });



  /* ==========================================================================

     6. FORMAT JAM LOKAL

     ========================================================================== */

  function getFormattedTime() {

    const now = new Date();

    const hours = String(now.getHours()).padStart(2, '0');

    const minutes = String(now.getMinutes()).padStart(2, '0');

    return `${hours}.${minutes}`;

  }



  if (initialTimeEl) {

    initialTimeEl.textContent = getFormattedTime();

  }



  /* ==========================================================================

     7. CHECKBOX KONTROL TAMPILAN PROSES RAG

     ========================================================================== */

  function updateRagVisibility() {

    if (ragToggleCheckbox && ragToggleCheckbox.checked) {

      document.body.classList.remove('hide-rag-process');

    } else {

      document.body.classList.add('hide-rag-process');

    }

  }



  if (ragToggleCheckbox) {

    ragToggleCheckbox.addEventListener('change', updateRagVisibility);

    updateRagVisibility();

  }



  /* ==========================================================================

     8. PIPELINE RAG (RETRIEVAL-AUGMENTED GENERATION ENGINE)

     ========================================================================== */

  const STOP_WORDS = new Set([

    "di", "ke", "dari", "yang", "dan", "atau", "adalah", "ini", "itu", "ada", 

    "pada", "untuk", "dengan", "saya", "kamu", "dia", "mereka", "kita", 

    "apa", "siapa", "mengapa", "bagaimana", "kapan", "mana", "saja", "tolong",

    "mohon", "bisa", "kah", "dong", "sih", "nya", "apakah"

  ]);



  function runRagPipeline(rawQuery) {

    // 1. Analisis & Normalisasi Query

    const cleanedQuery = rawQuery.toLowerCase().replace(/[^\w\s]/gi, ' ').trim();

    const queryTokens = cleanedQuery

      .split(/\s+/)

      .filter(token => token.length > 1 && !STOP_WORDS.has(token));



    // 2. Retrieval & Scoring

    let bestDoc = null;

    let highestScore = 0;

    let matchedKeywordsList = [];



    KNOWLEDGE_BASE.forEach(doc => {

      let score = 0;

      let matchedInThisDoc = [];



      queryTokens.forEach(token => {

        doc.keywords.forEach(kw => {

          if (kw === token || (token.length >= 4 && (kw.includes(token) || token.includes(kw)))) {

            score += 15;

            if (!matchedInThisDoc.includes(kw)) {

              matchedInThisDoc.push(kw);

            }

          }

        });



        if (doc.question.toLowerCase().includes(token) || doc.topic.toLowerCase().includes(token)) {

          score += 10;

        }



        if (doc.contextSnippet.toLowerCase().includes(token)) {

          score += 5;

        }

      });



      const normalizedScore = Math.min(Math.round(score), 100);



      if (normalizedScore > highestScore) {

        highestScore = normalizedScore;

        bestDoc = doc;

        matchedKeywordsList = matchedInThisDoc;

      }

    });



    const THRESHOLD = 15;

    const isRelevant = bestDoc !== null && highestScore >= THRESHOLD;



    // 3. Augmentasi Konteks

    let contextAugmented = "";

    if (isRelevant) {

      contextAugmented = `Konteks diambil dari [${bestDoc.id}] "${bestDoc.topic}": "${bestDoc.contextSnippet}"`;

    } else {

      contextAugmented = "Tidak ada dokumen dalam basis pengetahuan yang melampaui ambang batas relevansi minimum (skor < 15%).";

    }



    // 4. Generasi Jawaban

    let finalAnswerHtml = "";

    if (isRelevant) {

      finalAnswerHtml = bestDoc.answer;

    } else {

      finalAnswerHtml = `

        <p>Mohon maaf, informasi mengenai pertanyaan tersebut belum tersedia pada basis pengetahuan SOP JAKEVO saat ini.</p>

        <p>Silakan mencoba pertanyaan seputar 4 topik utama:</p>

        <ul>

          <li><strong>Apa syarat surat pengantar belum memiliki rumah (PM1)?</strong></li>

          <li><strong>Bagaimana alur izin penggunaan tanah makam (IPTM)?</strong></li>

          <li><strong>Apa saja syarat izin angkutan kebersihan?</strong></li>

          <li><strong>Di mana alamat kantor DPMPTSP Provinsi DKI Jakarta?</strong></li>

        </ul>

        <p style="font-size: 0.8rem; color: #64748B; font-style: italic; margin-top: 6px;">(Data contoh/dummy simulasi frontend RAG)</p>

      `;

    }



    return {

      query: rawQuery,

      tokens: queryTokens,

      isRelevant: isRelevant,

      score: highestScore,

      matchedDoc: isRelevant ? bestDoc : null,

      matchedKeywords: matchedKeywordsList,

      contextSnippet: contextAugmented,

      finalAnswer: finalAnswerHtml

    };

  }



  /* ==========================================================================

     9. AVATAR SVG KARAKTER PASANGAN ADAT BETAWI

     ========================================================================== */

  function getBetawiAvatarHtml() {
    return `
      <div class="bot-avatar-wrapper modern-avatar-wrapper" title="Avatar JAKEVO Assistant - Karakter Adat Betawi">
        <img src="img/logo-chatbot.jpg" alt="Avatar Maskot Betawi JAKEVO" class="betawi-avatar-img">
      </div>
    `;
  }



  /* ==========================================================================

     10. AUTO-SCROLL CHAT

     ========================================================================== */

  function scrollToBottom() {

    if (chatArea) {

      chatArea.scrollTo({

        top: chatArea.scrollHeight,

        behavior: 'smooth'

      });

    }

  }



  /* ==========================================================================

     11. TAMPILKAN PESAN PENGGUNA

     ========================================================================== */

  function appendUserMessage(text) {

    const userMsgDiv = document.createElement('div');

    userMsgDiv.className = 'chat-message user-message';

    userMsgDiv.innerHTML = `

      <div class="user-bubble">

        <div class="user-text">${escapeHtml(text)}</div>

        <div class="bubble-footer">

          <span class="message-time" style="color: rgba(255,255,255,0.85);">${getFormattedTime()}</span>

        </div>

      </div>

    `;

    chatMessages.appendChild(userMsgDiv);

    scrollToBottom();

  }



  /* ==========================================================================

     12. INDIKATOR MENGETIK BOT

     ========================================================================== */

  function showTypingIndicator() {

    const typingDiv = document.createElement('div');

    typingDiv.className = 'typing-indicator-row';

    typingDiv.id = 'typingIndicator';

    typingDiv.innerHTML = `

      ${getBetawiAvatarHtml()}

      <div class="typing-bubble">

        <span class="typing-dot"></span>

        <span class="typing-dot"></span>

        <span class="typing-dot"></span>

        <span class="typing-label-text">JAKEVO Assistant sedang menganalisis dokumen SOP...</span>

      </div>

    `;

    chatMessages.appendChild(typingDiv);

    scrollToBottom();

  }



  function hideTypingIndicator() {

    const typingEl = document.getElementById('typingIndicator');

    if (typingEl) {

      typingEl.remove();

    }

  }



  /* ==========================================================================

     13. TAMPILKAN PESAN BOT & INSPEKTOR RAG

     ========================================================================== */

  function getDocLabelFromUrl(url) {

    if (!url) return 'Unduh Dokumen';

    const filename = url.split('/').pop().replace(/\.(docx|pdf|doc|xlsx)$/i, '').replace(/[_-]/g, ' ').trim();

    if (filename.length > 20 && /^[0-9a-fA-F]+$/.test(filename)) {

      return 'Unduh Formulir Template';

    }

    return 'Unduh ' + filename.replace(/\b\w/g, l => l.toUpperCase());

  }



  function formatUrlsToClickable(htmlText) {

    if (!htmlText) return '';

    // Normalisasi penomoran yang menempel pada teks (misal: 1. A; 2. B; 3. C)
    if (!htmlText.includes('<ol') && !htmlText.includes('<li')) {
      htmlText = htmlText.replace(/([;:])\s*([1-9]\d?)\.\s+/g, '\n. ');
      htmlText = htmlText.replace(/(?:\n|^)(PM1\s+[^:\n]+:\s*)/gi, '\n\n\n');
    }

    // Jika backend sudah memformat tautan ke tag <a>, jangan manipulasi lagi

    if (htmlText.includes('<a ') || htmlText.includes('class="jakevo-link')) {

      return htmlText;

    }

    // Bersihkan tanda panah gantung sebelum tautan

    let text = htmlText.replace(/(?:-&gt;|->)\s*(?=<p|<a|<\/li|<\/p|<br|$)/gi, '');

    const urlPattern = /(?:(?:-&gt;|->)\s*)?(https?:\/\/[^\s<>"'\)]+)/gi;

    return text.replace(urlPattern, (match, url) => {

      const cleanUrl = url.replace(/[.,;]+$/, '');

      const label = getDocLabelFromUrl(cleanUrl);

      return `<a href="${cleanUrl}" target="_blank" rel="noopener noreferrer" class="jakevo-link-btn" title="Unduh ${label}: ${cleanUrl}">&#128196; ${label} (Klik disini &nearr;)</a>`;

    });

  }



  function appendBotMessage(ragResult) {

    const botMsgDiv = document.createElement('div');

    botMsgDiv.className = 'chat-message bot-message';



    const matchedDocTitle = ragResult.matchedDoc ? `${ragResult.matchedDoc.id} - ${ragResult.matchedDoc.topic}` : "Tidak ditemukan dokumen cocok";

    const scoreBadgeClass = ragResult.score >= 50 ? '' : 'low';



    let keywordsPillsHtml = "";

    if (ragResult.matchedKeywords && ragResult.matchedKeywords.length > 0) {

      keywordsPillsHtml = ragResult.matchedKeywords.map(k => `<span class="keyword-tag-pill">${escapeHtml(k)}</span>`).join(' ');

    } else {

      keywordsPillsHtml = `<span style="color:#94A3B8; font-size:0.72rem;">(tidak ada kata kunci spesifik)</span>`;

    }



    // 1. Kotak Penjelasan RAG Pipeline

    const ragBoxHtml = `

      <div class="rag-inspector-card">

        <div class="rag-header">

          <span class="rag-header-title">

            🔍 Pipeline RAG (Retrieval-Augmented Generation)

          </span>

          <span class="rag-badge">Knowledge Base Demo</span>

        </div>



        <div class="rag-score-bar-wrap" title="Skor Relevansi: ${ragResult.score}%">

          <div class="rag-score-bar-fill" style="width: ${ragResult.score}%;"></div>

        </div>



        <div class="rag-step-list">

          <div class="rag-step-item">

            <span class="step-num-badge">1</span>

            <div>

              <span class="step-title">Query Diterima &amp; Guardrail:</span>

              <span class="step-meta">"${escapeHtml(ragResult.query)}" [${ragResult.tokens.length} token dianalisis, Status Guardrail: Lolos]</span>

            </div>

          </div>

          <div class="rag-step-item">

            <span class="step-num-badge">2</span>

            <div>

              <span class="step-title">Dense Semantic Retrieval:</span>

              <span class="step-meta">${escapeHtml(matchedDocTitle)}</span>

              <span class="score-badge ${scoreBadgeClass}">Kandidat Vektor Top-K</span>

              <div style="margin-top: 3px;">${keywordsPillsHtml}</div>

            </div>

          </div>

          <div class="rag-step-item">

            <span class="step-num-badge">3</span>

            <div>

              <span class="step-title">Hybrid Reranking:</span>

              <span class="step-meta">${ragResult.rerank_info ? escapeHtml(ragResult.rerank_info) : 'Penyaringan &amp; pembobotan leksikal token dengan prioritas intent SOP.'}</span>

              <span class="score-badge ${scoreBadgeClass}">Skor Re-ranked: ${ragResult.score}%</span>

            </div>

          </div>

          <div class="rag-step-item">

            <span class="step-num-badge">4</span>

            <div>

              <span class="step-title">Augmentasi Konteks (Neighbor Expansion):</span>

              <span class="step-meta">${escapeHtml(ragResult.contextSnippet)}</span>

            </div>

          </div>

          <div class="rag-step-item">

            <span class="step-num-badge">5</span>

            <div>

              <span class="step-title">Generasi Jawaban &amp; Output Guard:</span>

              <span class="step-meta">${ragResult.isRelevant ? 'Respons resmi disintesis dari dokumen DPMPTSP (PII Masking aktif)' : 'Fallback: Menampilkan panduan layanan SOP'}</span>

            </div>

          </div>

        </div>

      </div>

    `;



    // 2. Kotak Sumber Dokumen RAG

    let sourceCitationHtml = "";

    if (ragResult.isRelevant && ragResult.matchedDoc) {

      sourceCitationHtml = `

        <div class="rag-source-citation">

          <div class="source-header-row">

            <span class="source-icon">📚</span>

            <span class="source-label-text">Sumber Dokumen RAG Resmi:</span>

          </div>

          <div class="source-content-box">

            <span class="source-doc-id">${ragResult.matchedDoc.id}</span>

            <span class="source-doc-name">${escapeHtml(ragResult.matchedDoc.sourceDoc)}</span>

            <span class="source-verified-tag">✓ Terverifikasi DPMPTSP</span>

          </div>

        </div>

      `;

    } else {

      sourceCitationHtml = `

        <div class="rag-source-citation" style="border-left-color: #94A3B8;">

          <div class="source-header-row">

            <span class="source-icon">ℹ️</span>

            <span class="source-label-text">Sumber Referensi:</span>

          </div>

          <div class="source-content-box">

            <span class="source-doc-id" style="background:#F1F5F9; color:#475569; border-color:#CBD5E1;">DEFAULT-FALLBACK</span>

            <span class="source-doc-name">Knowledge Base Umum JAKEVO DKI Jakarta (Ambang batas relevansi &lt; 15%)</span>

          </div>

        </div>

      `;

    }



    botMsgDiv.innerHTML = `

      ${getBetawiAvatarHtml()}

      <div class="message-content-wrapper">

        <div class="bot-bubble modern-bot-bubble">

          <div class="bubble-header">

            <div class="bot-label-group">

              <span class="bot-label">✨ Chatbot JAKEVO</span>

              <span class="ai-verified-badge">Resmi DPMPTSP</span>

            </div>

          </div>

          <div class="bubble-body">${formatUrlsToClickable(ragResult.finalAnswer)}</div>

          

          ${sourceCitationHtml}



          <div class="bubble-footer">

            <button type="button" class="btn-copy-msg" title="Salin Jawaban">

              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">

                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>

                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>

              </svg>

              <span>Salin</span>

            </button>

            <span class="message-time">${getFormattedTime()}</span>

          </div>

        </div>

        ${ragBoxHtml}

      </div>

    `;



    // Pasang tombol salin jawaban

    const copyBtn = botMsgDiv.querySelector('.btn-copy-msg');

    if (copyBtn) {

      copyBtn.addEventListener('click', () => {

        const textToCopy = botMsgDiv.querySelector('.bubble-body').innerText;

        navigator.clipboard.writeText(textToCopy).then(() => {

          copyBtn.innerHTML = `

            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">

              <polyline points="20 6 9 17 4 12"></polyline>

            </svg>

            <span style="color:#10B981; font-weight:700;">Tersalin!</span>

          `;

          setTimeout(() => {

            copyBtn.innerHTML = `

              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">

                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>

                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>

              </svg>

              <span>Salin</span>

            `;

          }, 2000);

        });

      });

    }



    chatMessages.appendChild(botMsgDiv);

    scrollToBottom();

  }



  /* ==========================================================================

     14. HANDLER PENGIRIMAN PESAN (TERHUBUNG KE BACKEND FASTAPI)

     ========================================================================== */

  const API_ENDPOINT = "http://127.0.0.1:8000/api/chat";



  async function handleSendMessage(messageText) {

    const text = messageText.trim();

    if (!text) return;



    if (userInput) {

      userInput.value = '';

      userInput.disabled = true;

    }

    if (sendBtn) sendBtn.disabled = true;



    // 1. Tambah pesan user

    appendUserMessage(text);



    // 2. Indikator mengetik

    showTypingIndicator();



    try {

      // 3. Panggil API Backend RAG Asli (FastAPI + ChromaDB + Guardrail)

      const response = await fetch(API_ENDPOINT, {

        method: "POST",

        headers: {

          "Content-Type": "application/json"

        },

        body: JSON.stringify({ message: text })

      });



      if (!response.ok) {

        throw new Error(`HTTP error ${response.status}`);

      }



      const ragResult = await response.json();

      hideTypingIndicator();

      appendBotMessage(ragResult);



    } catch (err) {

      console.warn("Backend FastAPI tidak aktif atau galat, menggunakan simulasi lokal:", err);

      // Fallback cadangan jika backend belum dijalankan

      setTimeout(() => {

        const ragResult = runRagPipeline(text);

        hideTypingIndicator();

        appendBotMessage(ragResult);

      }, 500);

    } finally {

      if (userInput) {

        userInput.disabled = false;

        userInput.focus();

      }

      if (sendBtn) sendBtn.disabled = false;

    }

  }



  if (chatForm) {

    chatForm.addEventListener('submit', (e) => {

      e.preventDefault();

      if (userInput) {

        handleSendMessage(userInput.value);

      }

    });

  }



  quickChips.forEach(chip => {

    chip.addEventListener('click', () => {

      const query = chip.getAttribute('data-query');

      if (query) {

        handleSendMessage(query);

      }

    });

  });



  /* ==========================================================================

     15. SLIDER PERTANYAAN CEPAT HORIZONTAL

     ========================================================================== */

  const quickChipsSlider = document.getElementById('quickChipsSlider');

  const scrollChipsLeft = document.getElementById('scrollChipsLeft');

  const scrollChipsRight = document.getElementById('scrollChipsRight');



  if (quickChipsSlider && scrollChipsLeft && scrollChipsRight) {

    scrollChipsLeft.addEventListener('click', () => {

      quickChipsSlider.scrollBy({ left: -160, behavior: 'smooth' });

    });



    scrollChipsRight.addEventListener('click', () => {

      quickChipsSlider.scrollBy({ left: 160, behavior: 'smooth' });

    });



    quickChipsSlider.addEventListener('wheel', (e) => {

      if (e.deltaY !== 0) {

        e.preventDefault();

        quickChipsSlider.scrollLeft += e.deltaY;

      }

    }, { passive: false });

  }



  /* ==========================================================================

     16. HELPER ESCAPE HTML

     ========================================================================== */

  function escapeHtml(str) {

    if (!str) return '';

    return str

      .replace(/&/g, "&amp;")

      .replace(/</g, "&lt;")

      .replace(/>/g, "&gt;")

      .replace(/"/g, "&quot;")

      .replace(/'/g, "&#039;");

  }

});

