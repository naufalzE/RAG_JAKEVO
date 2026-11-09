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

      id: "DOC-JAKEVO-001",

      topic: "Alamat Kantor DPMPTSP",

      question: "Di mana alamat kantor DPMPTSP?",

      keywords: [

        "alamat", "kantor", "lokasi", "gedung", "dimana", "di mana", "mpp", 

        "kuningan", "rasuna said", "setiabudi", "dki", "jakarta", "kontak", 

        "telepon", "email", "lantai", "kunjungi", "jam buka", "operasional", "datang",

        "dpmptsp", "ptsp"

      ],

      sourceDoc: "Profil, Alamat Kantor, dan Layanan Informasi DPMPTSP Provinsi DKI Jakarta",

      contextSnippet: "Gedung Mal Pelayanan Publik (MPP) Provinsi DKI Jakarta Lantai 5, Jl. H.R. Rasuna Said Kav. C-22, Karet Kuningan, Setiabudi, Jakarta Selatan 12920. Jam operasional: Senin-Jumat 07.30-16.00 WIB.",

      answer: `

        <p>Kantor <strong>Dinas Penanaman Modal dan Pelayanan Terpadu Satu Pintu (DPMPTSP) Provinsi DKI Jakarta</strong> berlokasi di:</p>

        <p>📍 <strong>Gedung Mal Pelayanan Publik (MPP) Provinsi DKI Jakarta, Lantai 5</strong><br>

        Jl. H.R. Rasuna Said Kav. C-22, RT.02 / RW.05, Karet Kuningan, Setiabudi, Jakarta Selatan 12920.</p>

        

        <p>⏰ <strong>Jam Operasional Pelayanan:</strong><br>

        • Senin – Kamis: 07.30 – 16.00 WIB<br>

        • Jumat: 07.30 – 16.30 WIB (Istirahat 11.30 – 13.00 WIB)<br>

        • Layanan portal daring JAKEVO (jakevo.jakarta.go.id) aktif 24 jam setiap hari.</p>

        

        <p>📞 <strong>Kontak & Saluran Layanan Resmi:</strong><br>

        • <strong>Call Center PTSP:</strong> 1500-164 atau (021) 1500164<br>

        • <strong>Telepon Kantor:</strong> (021) 5200300<br>

        • <strong>Email:</strong> dpmptsp@jakarta.go.id / pengaduandpmptsp@jakarta.go.id<br>

        • <strong>Portal Resmi:</strong> <a href="https://pelayanan.jakarta.go.id" target="_blank" rel="noopener noreferrer" style="color:#1F4FD8; text-decoration: underline; font-weight: 600;">pelayanan.jakarta.go.id</a> dan <a href="https://jakevo.jakarta.go.id" target="_blank" rel="noopener noreferrer" style="color:#1F4FD8; text-decoration: underline; font-weight: 600;">jakevo.jakarta.go.id</a></p>

      `

    },

    {

      id: "DOC-JAKEVO-002",

      topic: "Sektor Proyek Investasi",

      question: "Sektor proyek apa saja yang tersedia?",

      keywords: [

        "sektor", "proyek", "tersedia", "investasi", "bidang", "transportasi", 

        "infrastruktur", "hijau", "properti", "kesehatan", "pariwisata", 

        "teknologi", "energi", "terbarukan", "transit", "tod", "mrt", "lrt", 

        "itf", "sampah", "katalog", "peluang", "unggulan"

      ],

      sourceDoc: "Katalog Proyek Investasi Siap Tawar (Investment Ready Projects) JAKEVO 2024",

      contextSnippet: "Katalog sektor prioritas investasi: Transportasi Berkelanjutan (TOD MRT/LRT), Pengolahan Sampah Menjadi Energi (ITF), Revitalisasi Urban Kota Tua, Digital & Smart City, dan Wisata Kepulauan Seribu.",

      answer: `

        <p>Jakarta Investment Centre (JAKEVO) menawarkan berbagai sektor proyek investasi strategis yang siap ditawarkan (<em>Investment Ready Projects</em>):</p>

        

        <ol>

          <li>🚆 <strong>Infrastruktur & Transportasi Berkelanjutan:</strong> Pengembangan kawasan berorientasi transit (<em>TOD</em>) MRT & LRT Jakarta serta simpul interkoneksi antarmoda.</li>

          <li>🌱 <strong>Ekonomi Hijau & Pengelolaan Lingkungan:</strong> Fasilitas Pengolahan Sampah Menjadi Energi (ITF), panel surya (PLTS), dan efisiensi air bersih.</li>

          <li>🏙️ <strong>Properti, Urban Regeneration & Kawasan Khusus:</strong> Revitalisasi cagar budaya Kota Tua Jakarta dan kawasan komersial ramah lingkungan.</li>

          <li>💻 <strong>Digital Infrastructure & Smart City:</strong> Sarana Jaringan Utilitas Terpadu (SJUT) dan ekosistem data center ramah lingkungan.</li>

          <li>🏥 <strong>Kesehatan & Pariwisata Bahari:</strong> Fasilitas kesehatan rujukan berstandar global dan ekowisata Kepulauan Seribu.</li>

        </ol>

        <p style="font-size: 0.8rem; color: #64748B; font-style: italic; margin-top: 6px;">(Data contoh/dummy simulasi frontend RAG)</p>

      `

    },

    {

      id: "DOC-JAKEVO-003",

      topic: "Profil JAKEVO",

      question: "Apa itu JAKEVO?",

      keywords: [

        "apa", "itu", "jakevo", "jakarta", "evolution", "perizinan", "profil", "tentang", 

        "tugas", "fungsi", "peran", "dpmptsp", "investor", "perizinan", "fasilitasi", 

        "pengertian", "definisi", "bantuan", "tujuan"

      ],

      sourceDoc: "Buku Panduan Layanan Terpadu Satu Pintu & JAKEVO DPMPTSP DKI Jakarta",

      contextSnippet: "Jakarta Investment Centre (JAKEVO) adalah unit inisiatif strategis di bawah DPMPTSP Provinsi DKI Jakarta yang berfungsi sebagai one-stop investment hub untuk memfasilitasi dan mendampingi investor.",

      answer: `

        <p><strong>Jakarta Investment Centre (JAKEVO)</strong> adalah inisiatif strategis Pemerintah Provinsi DKI Jakarta di bawah naungan <strong>Dinas Penanaman Modal dan Pelayanan Terpadu Satu Pintu (DPMPTSP)</strong>.</p>

        

        <p>JAKEVO berfungsi sebagai <em>One-Stop Investment Hub</em> dengan peran utama:</p>

        <ul>

          <li><strong>Promosi Peluang Investasi:</strong> Menyajikan informasi komprehensif potensi proyek DKI Jakarta bagi investor domestik (PMDN) & asing (PMA).</li>

          <li><strong>Pendampingan End-to-End:</strong> Mendampingi pelaku usaha dari tahap pra-investasi, perizinan JAKEVO, hingga operasional bisnis.</li>

          <li><strong>Fasilitasi & Debottlenecking:</strong> Mengurai hambatan birokrasi, regulasi, dan perizinan bisnis lintas dinas.</li>

          <li><strong>Forum Investasi:</strong> Menyelenggarakan forum tahunan berskala global <em>Jakarta Investment Forum (JIF)</em>.</li>

        </ul>

        <p style="font-size: 0.8rem; color: #64748B; font-style: italic; margin-top: 6px;">(Data contoh/dummy simulasi frontend RAG)</p>

      `

    },

    {

      id: "DOC-JAKEVO-004",

      topic: "Data Realisasi Investasi",

      question: "Data realisasi investasi",

      keywords: [

        "data", "realisasi", "investasi", "angka", "statistik", "capaian", 

        "pma", "pmdn", "triliun", "kuartal", "target", "tahun", "pertumbuhan", 

        "peringkat", "kinerja", "rekap", "laporan", "nilai"

      ],

      sourceDoc: "Laporan Realisasi Penanaman Modal (PMA & PMDN) DPMPTSP DKI Jakarta",

      contextSnippet: "Realisasi investasi DKI Jakarta mencapai Rp 165,3 Triliun (104,2% dari target tahunan). PMDN sebesar Rp 89,2 Triliun dan PMA sebesar Rp 76,1 Triliun (USD 5,1 Miliar).",

      answer: `

        <p>Berikut ringkasan <strong>Data Realisasi Investasi DKI Jakarta</strong> (data simulasi resmi DPMPTSP):</p>

        

        <p>📊 <strong>Capaian Realisasi Investasi:</strong></p>

        <ul>

          <li><strong>Total Realisasi:</strong> <strong>Rp 165,3 Triliun</strong> (104,2% dari target tahunan Rp 158,6 Triliun)</li>

          <li><strong>PMDN (Modal Dalam Negeri):</strong> Rp 89,2 Triliun (53,9%)</li>

          <li><strong>PMA (Modal Asing):</strong> USD 5,1 Miliar / setara Rp 76,1 Triliun (46,1%)</li>

        </ul>

        

        <p>🏆 <strong>3 Sektor Kontributor Terbesar:</strong></p>

        <ol>

          <li>Transportasi, Pergudangan & Telekomunikasi (Rp 42,8 T)</li>

          <li>Jasa Lainnya, Perhotelan & Restoran (Rp 31,5 T)</li>

          <li>Perumahan, Kawasan Industri & Perkantoran (Rp 28,4 T)</li>

        </ol>

        <p>DKI Jakarta secara konsisten menduduki peringkat #1 tujuan investasi nasional di Indonesia.</p>

        <p style="font-size: 0.8rem; color: #64748B; font-style: italic; margin-top: 6px;">(Data contoh/dummy simulasi frontend RAG)</p>

      `

    },

    {

      id: "DOC-PTSP-005",

      topic: "Perizinan JAKEVO & Eskalasi Petugas PTSP",

      question: "Bagaimana alur izin JAKEVO dan eskalasi ke petugas?",

      keywords: [

        "jakevo", "izin", "perizinan", "eskalasi", "petugas", "ptsp", "role", 

        "akses", "hak akses", "rbac", "syarat", "oss", "login", "konsultasi"

      ],

      sourceDoc: "Panduan Integrasi JAKEVO & Matriks Hak Akses RBAC DPMPTSP DKI Jakarta",

      contextSnippet: "Pengguna Publik dapat bertanya syarat izin via Chatbot RAG. Jika butuh konsultasi lanjutan, chatbot dapat mengeskalasikan percakapan ke Petugas Layanan PTSP (Role 2) via Call Center 1500-164 atau Mal Pelayanan Publik.",

      answer: `

        <p>Perizinan investasi DKI Jakarta terintegrasi pada sistem digital <strong>JAKEVO</strong> (<em>jakevo.jakarta.go.id</em>) dan OSS Nasional.</p>

        

        <p>🛡️ <strong>Alur Layanan & Eskalasi (Role-Based Access):</strong></p>

        <ul>

          <li><strong>Pengguna Publik (Role 1):</strong> Konsultasi mandiri anonim terkait syarat, estimasi waktu, dan dasar hukum izin.</li>

          <li><strong>Petugas Layanan PTSP (Role 2):</strong> Menerima tiket eskalasi kasus yang belum terjawab otomatis, memverifikasi berkas, dan memandu pemohon.</li>

          <li><strong>Bantuan Langsung:</strong> Hubungi Call Center PTSP <strong>1500-164</strong> atau kunjungi loket konsultasi Lantai 5 Mal Pelayanan Publik.</li>

        </ul>

        <p style="font-size: 0.8rem; color: #64748B; font-style: italic; margin-top: 6px;">(Data contoh/dummy simulasi frontend RAG)</p>

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

     4. PREVIEW UPLOAD FOTO MAHASISWA 1 & 2

     ========================================================================== */

  function setupPhotoUpload(inputId, imgId) {

    const inputEl = document.getElementById(inputId);

    const imgEl = document.getElementById(imgId);

    if (inputEl && imgEl) {

      inputEl.addEventListener('change', (e) => {

        const file = e.target.files[0];

        if (file) {

          const reader = new FileReader();

          reader.onload = (event) => {

            imgEl.src = event.target.result;

          };

          reader.readAsDataURL(file);

        }

      });

    }

  }



  setupPhotoUpload('studentPhotoInput1', 'studentPhotoImg1');

  setupPhotoUpload('studentPhotoInput2', 'studentPhotoImg2');



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

          <li><strong>Di mana alamat kantor DPMPTSP?</strong></li>

          <li><strong>Sektor proyek apa saja yang tersedia?</strong></li>

          <li><strong>Apa itu JAKEVO?</strong></li>

          <li><strong>Data realisasi investasi</strong></li>

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

        <svg class="betawi-avatar-svg" viewBox="0 0 100 100" width="75" height="75" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Avatar Pasangan Betawi JAKEVO">

          <defs>

            <linearGradient id="avatarOrangeGradDynamic" x1="0%" y1="0%" x2="100%" y2="100%">

              <stop offset="0%" stop-color="#FFA229"/>

              <stop offset="100%" stop-color="#E26D00"/>

            </linearGradient>

          </defs>

          <rect width="100" height="100" rx="18" fill="url(#avatarOrangeGradDynamic)"/>

          <circle cx="50" cy="20" r="3.5" fill="#FFF275" opacity="0.9"/>

          <path d="M50 13 L51.5 19.5 L58 20 L51.5 20.5 L50 27 L48.5 20.5 L42 20 L48.5 19.5 Z" fill="#FFF9C4" opacity="0.75"/>



          <!-- Abang Betawi -->

          <path d="M12 94 C12 77 22 71 35 71 C43 71 48 75 50 81 C44 86 36 94 36 94 Z" fill="#FFFFFF"/>

          <path d="M26 67 C32 67 38 71 40 77 C36 83 32 94 32 94 L24 94 C24 87 22 77 26 67 Z" fill="#DC2626"/>

          <path d="M27 74 L37 76 M26 81 L35 83 M25 88 L33 90" stroke="#FEF08A" stroke-width="1.3" stroke-linecap="round"/>

          <rect x="29" y="59" width="10" height="11" rx="4" fill="#F8C798"/>

          <ellipse cx="34" cy="49" rx="13" ry="14" fill="#FCD3AD"/>

          <path d="M20 43 C20 31 26 29 34 29 C42 29 48 31 48 43 Z" fill="#1E293B"/>

          <path d="M20 41 L48 41" stroke="#FBBF24" stroke-width="0.8" opacity="0.8"/>

          <path d="M25 45 Q29 43 32 45" stroke="#334155" stroke-width="1.3" fill="none" stroke-linecap="round"/>

          <path d="M37 45 Q40 43 43 45" stroke="#334155" stroke-width="1.3" fill="none" stroke-linecap="round"/>

          <circle cx="28" cy="48" r="1.6" fill="#0F172A"/>

          <circle cx="39" cy="48" r="1.6" fill="#0F172A"/>

          <path d="M34 49 L33 52 L35 52" stroke="#D97706" stroke-width="1" fill="none" stroke-linecap="round"/>

          <path d="M30 54 Q34 58 38 54" stroke="#B45309" stroke-width="1.4" fill="none" stroke-linecap="round"/>

          <circle cx="25" cy="51" r="2.5" fill="#FCA5A5" opacity="0.65"/>

          <circle cx="42" cy="51" r="2.5" fill="#FCA5A5" opacity="0.65"/>



          <!-- None Betawi -->

          <path d="M50 81 C52 75 57 71 65 71 C78 71 88 77 88 94 L64 94 C64 94 56 86 50 81 Z" fill="#0284C7"/>

          <path d="M60 71 L66 83 L72 71" fill="#38BDF8"/>

          <circle cx="66" cy="77" r="1.8" fill="#FBBF24"/>

          <circle cx="66" cy="82" r="1.5" fill="#FBBF24"/>

          <path d="M72 73 C76 79 82 85 85 94 L77 94 C74 88 70 82 68 75 Z" fill="#F59E0B"/>

          <rect x="61" y="59" width="10" height="11" rx="4" fill="#F8C798"/>

          <ellipse cx="66" cy="49" rx="13" ry="14" fill="#FCD3AD"/>

          <ellipse cx="66" cy="37" rx="14" ry="10" fill="#1E293B"/>

          <circle cx="56" cy="34" r="2.2" fill="#FEF08A"/>

          <circle cx="66" cy="31" r="2.7" fill="#FBBF24"/>

          <circle cx="76" cy="34" r="2.2" fill="#FEF08A"/>

          <circle cx="54" cy="39" r="1.6" fill="#FFFFFF"/>

          <circle cx="53" cy="43" r="1.6" fill="#FFFFFF"/>

          <circle cx="53" cy="47" r="1.6" fill="#FFFFFF"/>

          <path d="M57 45 Q60 43 63 45" stroke="#334155" stroke-width="1.3" fill="none" stroke-linecap="round"/>

          <path d="M69 45 Q72 43 75 45" stroke="#334155" stroke-width="1.3" fill="none" stroke-linecap="round"/>

          <circle cx="60" cy="48" r="1.6" fill="#0F172A"/>

          <circle cx="72" cy="48" r="1.6" fill="#0F172A"/>

          <path d="M62 46 L63 45 M74 46 L75 45" stroke="#0F172A" stroke-width="0.9"/>

          <circle cx="66" cy="51" r="0.8" fill="#D97706"/>

          <path d="M62 54 Q66 58 70 54" stroke="#E11D48" stroke-width="1.5" fill="none" stroke-linecap="round"/>

          <circle cx="57" cy="52" r="2.5" fill="#FDA4AF" opacity="0.75"/>

          <circle cx="75" cy="52" r="2.5" fill="#FDA4AF" opacity="0.75"/>

        </svg>

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

              <span class="step-title">Query Diterima:</span>

              <span class="step-meta">"${escapeHtml(ragResult.query)}" [${ragResult.tokens.length} token dianalisis]</span>

            </div>

          </div>

          <div class="rag-step-item">

            <span class="step-num-badge">2</span>

            <div>

              <span class="step-title">Retrieval Dokumen:</span>

              <span class="step-meta">${escapeHtml(matchedDocTitle)}</span>

              <span class="score-badge ${scoreBadgeClass}">Skor: ${ragResult.score}%</span>

              <div style="margin-top: 3px;">${keywordsPillsHtml}</div>

            </div>

          </div>

          <div class="rag-step-item">

            <span class="step-num-badge">3</span>

            <div>

              <span class="step-title">Augmentasi Konteks:</span>

              <span class="step-meta">${escapeHtml(ragResult.contextSnippet)}</span>

            </div>

          </div>

          <div class="rag-step-item">

            <span class="step-num-badge">4</span>

            <div>

              <span class="step-title">Generasi Jawaban:</span>

              <span class="step-meta">${ragResult.isRelevant ? 'Respons resmi disintesis dari dokumen DPMPTSP' : 'Fallback: Menampilkan panduan 4 topik utama'}</span>

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

