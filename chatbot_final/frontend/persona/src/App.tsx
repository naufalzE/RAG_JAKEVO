import React, { useState } from 'react';
import { motion } from 'motion/react';
import {
  BookOpen,
  FileSearch,
  Sparkles,
  ShieldCheck,
  AlertOctagon,
  Zap,
  Database,
  Cpu,
  Binary,
  Layers,
  Bot,
  FileText,
  Code2,
  Volume2,
  VolumeX,
  MessageSquare,
  ArrowUpRight,
  ChevronRight,
  X,
  Play,
  Users
} from 'lucide-react';
import { PersonaChatbot } from './components/PersonaChatbot';
import { RagArchitectureVisualizer } from './components/RagArchitectureVisualizer';
import { EvaluationSection } from './components/EvaluationSection';
import { OpeningAnimation } from './components/OpeningAnimation';
import { CoopCreatorsSection } from './components/CoopCreatorsSection';
import { TECH_STACK_ITEMS, KNOWLEDGE_BASE } from './data/jakevoData';
import { soundFX } from './utils/sound';

const TECH_ICONS: Record<string, React.ReactNode> = {
  'tech-python': <Code2 className="w-6 h-6" />,
  'tech-chromadb': <Database className="w-6 h-6" />,
  'tech-sentence-transformers': <Cpu className="w-6 h-6" />,
  'tech-minilm': <Binary className="w-6 h-6" />,
  'tech-rag': <Layers className="w-6 h-6" />,
  'tech-llm': <Bot className="w-6 h-6" />,
  'tech-pdf': <FileText className="w-6 h-6" />
};

export default function App() {
  const [showIntroOverlay, setShowIntroOverlay] = useState(true);
  const [isMuted, setIsMuted] = useState(false);
  const [isPopupChatOpen, setIsPopupChatOpen] = useState(false);
  const [externalChatQuery, setExternalChatQuery] = useState<string | null>(null);
  const [selectedTechId, setSelectedTechId] = useState<string>(TECH_STACK_ITEMS[0].id);

  const handleToggleMute = () => {
    const nextMuted = !isMuted;
    setIsMuted(nextMuted);
    soundFX.setMuted(nextMuted);
    if (!nextMuted) {
      soundFX.playSelect();
    }
  };

  const handleAskInDemo = (question: string, openPopup = false) => {
    soundFX.playSelect();
    setExternalChatQuery(question);
    if (openPopup) {
      setIsPopupChatOpen(true);
    } else {
      const demoSection = document.getElementById('chatbot-demo');
      if (demoSection) {
        demoSection.scrollIntoView({ behavior: 'smooth' });
      }
    }
  };

  const scrollToSection = (sectionId: string) => {
    soundFX.playSelect();
    const el = document.getElementById(sectionId);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const activeTech =
    TECH_STACK_ITEMS.find(t => t.id === selectedTechId) || TECH_STACK_ITEMS[0];

  return (
    <div className="min-h-screen bg-[#111111] text-white relative selection:bg-[#E60012] selection:text-white">
      {/* =====================================================================
          PERSONA 5 ROYAL MULTI-STAGE OPENING ANIMATION OVERLAY
          ===================================================================== */}
      <OpeningAnimation
        isVisible={showIntroOverlay}
        onComplete={() => setShowIntroOverlay(false)}
      />

      {/* =====================================================================
          TOP NAVIGATION BAR (Strict 3-Zone Contract)
          ===================================================================== */}
      <header className="sticky top-0 z-40 bg-[#111111]/95 backdrop-blur-md border-b-2 border-[#E60012]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-8">
          {/* Zone 1: Single Brand Wordmark */}
          <a
            href="#home"
            onClick={() => soundFX.playHover()}
            className="font-p5-display text-3xl tracking-wider text-white hover:text-[#E60012] transition-colors whitespace-nowrap shrink-0"
          >
            JAKEVO
          </a>

          {/* Zone 2: 5 Concise Single-Line Navigation Links */}
          <nav className="hidden md:flex items-center gap-7 text-sm font-bold text-zinc-300">
            <a
              href="#about"
              onMouseEnter={() => soundFX.playHover()}
              className="hover:text-white hover:underline decoration-[#E60012] decoration-2 underline-offset-4 transition-colors whitespace-nowrap shrink-0"
            >
              About
            </a>
            <a
              href="#how-it-works"
              onMouseEnter={() => soundFX.playHover()}
              className="hover:text-white hover:underline decoration-[#E60012] decoration-2 underline-offset-4 transition-colors whitespace-nowrap shrink-0"
            >
              Architecture
            </a>
            <a
              href="#tech-stack"
              onMouseEnter={() => soundFX.playHover()}
              className="hover:text-white hover:underline decoration-[#E60012] decoration-2 underline-offset-4 transition-colors whitespace-nowrap shrink-0"
            >
              Tech Stack
            </a>
            <a
              href="#evaluation"
              onMouseEnter={() => soundFX.playHover()}
              className="hover:text-white hover:underline decoration-[#E60012] decoration-2 underline-offset-4 transition-colors whitespace-nowrap shrink-0"
            >
              Evaluation
            </a>
            <a
              href="#coop-creators"
              onMouseEnter={() => soundFX.playHover()}
              className="hover:text-white hover:underline decoration-[#E60012] decoration-2 underline-offset-4 transition-colors whitespace-nowrap shrink-0"
            >
              Co-Op Team
            </a>
          </nav>

          {/* Zone 3: 1 Primary Action Button */}
          <div className="flex items-center shrink-0">
            <button
              type="button"
              onClick={() => scrollToSection('chatbot-demo')}
              className="p5-btn-primary px-4 py-1.5 text-base whitespace-nowrap shrink-0"
            >
              <span className="p5-unskew">TRY CHATBOT DEMO</span>
            </button>
          </div>
        </div>
      </header>

      {/* =====================================================================
          SECTION 1 – INTRO / HOME
          ===================================================================== */}
      <section
        id="home"
        className="relative overflow-hidden py-16 sm:py-24 lg:py-28 p5-halftone-bg border-b-4 border-white"
      >
        {/* Dynamic Asymmetric Red Diagonal Slash Backdrop */}
        <div
          className="absolute -top-24 -right-24 w-[520px] h-[520px] bg-[#E60012]/15 transform rotate-12 pointer-events-none"
          aria-hidden="true"
        />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-12 items-stretch">
            {/* Left Column: Hero Statement */}
            <motion.div
              initial={{ opacity: 0, x: -24 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.45 }}
              className="lg:col-span-7 flex flex-col justify-center space-y-6"
            >
              {/* Unboxed Metadata Kicker */}
              <div className="flex flex-wrap items-center gap-2 text-xs sm:text-sm font-p5-mono text-zinc-300">
                <span className="text-[#E60012] font-bold">RAG PRODUCT SHOWCASE</span>
                <span aria-hidden="true">·</span>
                <span>DPMPTSP ADMINISTRATIVE KNOWLEDGE SYSTEM</span>
                <span aria-hidden="true">·</span>
                <span>CHROMA VECTOR ENGINE</span>
              </div>

              {/* Brand Name & Headline */}
              <div className="space-y-2">
                <div className="inline-block bg-[#E60012] text-white font-p5-display text-2xl sm:text-3xl px-4 py-1 border-2 border-white transform -skew-x-6 p5-shadow-white mb-2">
                  <span className="inline-block transform skew-x-6">JAKEVO RAG CHATBOT</span>
                </div>

                <h1
                  className="font-p5-display text-white tracking-tight leading-[0.95]"
                  style={{ fontSize: 'clamp(2.75rem, 5.5vw, 4.75rem)', textWrap: 'balance' }}
                >
                  INFORMATION IS YOUR{' '}
                  <span className="text-[#E60012] underline decoration-white decoration-4">
                    POWER.
                  </span>
                </h1>

                <p className="font-p5-display text-2xl sm:text-3xl text-zinc-200 tracking-wide pt-1">
                  An Intelligent Document-Based Chatbot
                </p>
              </div>

              {/* Concise Product Description */}
              <p className="text-base sm:text-lg text-zinc-300 leading-relaxed max-w-2xl">
                <strong>JAKEVO</strong> merupakan asisten cerdas berbasis{' '}
                <em>Retrieval-Augmented Generation (RAG)</em> yang dirancang untuk membantu pengguna mendapatkan informasi akurat mengenai syarat dokumen dan prosedur pelayanan administrasi langsung dari korpus dokumen resmi.
              </p>

              {/* Primary CTA & Interactive Controls */}
              <div className="flex flex-wrap items-center gap-3.5 pt-2">
                <button
                  type="button"
                  onClick={() => scrollToSection('about')}
                  className="p5-btn-primary px-6 py-3.5 text-xl whitespace-nowrap shrink-0"
                >
                  <span className="p5-unskew flex items-center gap-2">
                    <span>EXPLORE JAKEVO</span>
                    <ChevronRight className="w-5 h-5" />
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() => scrollToSection('coop-creators')}
                  className="p5-btn-secondary px-5 py-3.5 text-lg whitespace-nowrap shrink-0"
                >
                  <span className="p5-unskew flex items-center gap-2">
                    <Users className="w-4 h-4 text-[#E60012]" />
                    <span>IDENTITAS TIM CO-OP</span>
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    soundFX.playTransition();
                    setShowIntroOverlay(true);
                  }}
                  className="px-3.5 py-3 bg-[#1A1A1A] border border-zinc-700 hover:border-white text-xs font-p5-mono text-zinc-300 hover:text-white flex items-center gap-1.5 transition-colors cursor-pointer whitespace-nowrap shrink-0"
                  title="Putar Ulang Animasi Pembuka Persona 5"
                >
                  <Play className="w-3.5 h-3.5 text-[#E60012]" />
                  <span>REPLAY INTRO</span>
                </button>

                <button
                  type="button"
                  onClick={handleToggleMute}
                  className="px-3.5 py-3 bg-[#1A1A1A] border border-zinc-700 hover:border-white text-xs font-p5-mono text-zinc-300 hover:text-white flex items-center gap-1.5 transition-colors cursor-pointer whitespace-nowrap shrink-0"
                  title={isMuted ? 'Aktifkan Efek Suara Menu UI' : 'Bisukan Efek Suara Menu UI'}
                >
                  {isMuted ? (
                    <>
                      <VolumeX className="w-4 h-4 text-zinc-400" />
                      <span>SFX: MUTED</span>
                    </>
                  ) : (
                    <>
                      <Volume2 className="w-4 h-4 text-[#E60012]" />
                      <span>SFX: ACTIVE</span>
                    </>
                  )}
                </button>
              </div>
            </motion.div>

            {/* Right Column: Persona 5 Interactive Command Preview Dossier */}
            <motion.div
              initial={{ opacity: 0, x: 24 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.45, delay: 0.1 }}
              className="lg:col-span-5 flex flex-col justify-between bg-[#18181B] border-2 border-white p-6 p5-shadow-lg-red relative"
            >
              <div className="space-y-4">
                <div className="flex items-center justify-between border-b-2 border-[#E60012] pb-3">
                  <div>
                    <span className="text-xs font-p5-mono text-[#E60012] block">
                      INTERACTIVE SYSTEM PREVIEW
                    </span>
                    <h2 className="font-p5-display text-2xl text-white tracking-wide">
                      GROUNDED DOCUMENT RETRIEVAL
                    </h2>
                  </div>
                  <span className="font-p5-mono text-xs text-zinc-400">RAG PIPELINE</span>
                </div>

                {/* Simulated Dialogue Preview */}
                <div className="space-y-3 bg-[#111111] border border-zinc-800 p-4">
                  <div className="bg-[#E60012] text-white border border-white p-3 text-xs sm:text-sm font-semibold ml-6 transform -rotate-1">
                    "Apa saja syarat mengurus Surat Keterangan Tidak Mampu (SKTM) di kelurahan?"
                  </div>

                  <div className="bg-[#1A1A1A] border border-white p-3.5 text-xs sm:text-sm text-zinc-200 space-y-2">
                    <div className="font-p5-mono text-[11px] text-[#E60012] font-bold">
                      SOURCE: PM1_SKTM_KELURAHAN-WEB-SYARAT · HAL. 2
                    </div>
                    <p className="leading-relaxed">
                      Syarat meliputi: Surat Pengantar RT/RW, KTP-el pemohon, Kartu Keluarga (KK), Surat Pernyataan Tidak Mampu bermeterai, dan foto kondisi rumah.
                    </p>
                  </div>
                </div>

                {/* Quick Interactive Question Triggers */}
                <div className="space-y-2 pt-1">
                  <div className="text-xs font-p5-mono text-zinc-400 uppercase">
                    KLIK UNTUK MENGUJI PERTANYAAN DI CHATBOT:
                  </div>
                  <div className="grid grid-cols-1 gap-2">
                    <button
                      type="button"
                      onClick={() => handleAskInDemo('Bagaimana alur pengajuan izin di JAKEVO?')}
                      className="w-full text-left px-3.5 py-2.5 bg-[#111111] hover:bg-[#E60012] text-zinc-200 hover:text-white border border-zinc-700 hover:border-white text-xs font-semibold flex items-center justify-between transition-colors cursor-pointer"
                    >
                      <span>"Bagaimana alur pengajuan izin di JAKEVO?"</span>
                      <ArrowUpRight className="w-4 h-4 shrink-0" />
                    </button>
                    <button
                      type="button"
                      onClick={() => handleAskInDemo('Di mana alamat kantor DPMPTSP?')}
                      className="w-full text-left px-3.5 py-2.5 bg-[#111111] hover:bg-[#E60012] text-zinc-200 hover:text-white border border-zinc-700 hover:border-white text-xs font-semibold flex items-center justify-between transition-colors cursor-pointer"
                    >
                      <span>"Di mana alamat kantor DPMPTSP?"</span>
                      <ArrowUpRight className="w-4 h-4 shrink-0" />
                    </button>
                  </div>
                </div>
              </div>

              <div className="mt-5 pt-3 border-t border-zinc-800 flex items-center justify-between text-xs text-zinc-400 font-p5-mono">
                <span>EMBEDDING: MiniLM-L12-v2</span>
                <span>VECTOR DB: ChromaDB</span>
              </div>
            </motion.div>
          </div>

          {/* Full-Width Key Architectural Specs Strip Below Hero Split */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-12">
            <div className="bg-[#161616] border-2 border-white p-4 p5-shadow-red">
              <div className="font-p5-mono text-xs text-zinc-400">ARCHITECTURE PARADIGM</div>
              <div className="font-p5-display text-2xl sm:text-3xl text-white mt-1">
                RAG SYSTEM
              </div>
              <div className="text-xs text-zinc-400 mt-0.5">
                Retrieval-Augmented Generation
              </div>
            </div>

            <div className="bg-[#161616] border-2 border-white p-4 p5-shadow-red">
              <div className="font-p5-mono text-xs text-zinc-400">VECTOR DATABASE</div>
              <div className="font-p5-display text-2xl sm:text-3xl text-white mt-1">
                CHROMADB
              </div>
              <div className="text-xs text-zinc-400 mt-0.5">
                Semantic Document Chunk Storage
              </div>
            </div>

            <div className="bg-[#161616] border-2 border-white p-4 p5-shadow-red">
              <div className="font-p5-mono text-xs text-zinc-400">MULTILINGUAL EMBEDDING</div>
              <div className="font-p5-display text-2xl sm:text-3xl text-[#E60012] mt-1">
                384 DIMENSIONS
              </div>
              <div className="text-xs text-zinc-400 mt-0.5">
                paraphrase-multilingual-MiniLM-L12-v2
              </div>
            </div>

            <div className="bg-[#161616] border-2 border-white p-4 p5-shadow-red">
              <div className="font-p5-mono text-xs text-zinc-400">DEVELOPMENT SQUAD</div>
              <div className="font-p5-display text-2xl sm:text-3xl text-white mt-1">
                2 CO-OP CREATORS
              </div>
              <div className="text-xs text-zinc-400 mt-0.5">
                AI RAG Backend × Persona UI Frontend
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* =====================================================================
          SECTION 2 – ABOUT JAKEVO
          ===================================================================== */}
      <section id="about" className="py-20 sm:py-24 bg-[#141414] border-b-4 border-[#E60012]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
          {/* Section Header */}
          <div className="max-w-3xl space-y-3">
            <div className="text-xs font-p5-mono text-[#E60012] uppercase tracking-widest">
              01. SYSTEM IDENTITY &amp; PURPOSE
            </div>
            <h2 className="font-p5-display text-4xl sm:text-5xl text-white tracking-wide">
              APA ITU JAKEVO CHATBOT?
            </h2>
            <p className="text-base text-zinc-300 leading-relaxed">
              JAKEVO adalah asisten percakapan berbasis dokumen yang menjembatani masyarakat dengan ribuan baris aturan prosedur dan syarat pelayanan administrasi secara instan, terstruktur, dan berbasis bukti dokumen.
            </p>
          </div>

          {/* 4 Core Pillars of JAKEVO (Asymmetric Bento Grid) */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
            {/* Pillar 1 (7 cols) */}
            <div className="md:col-span-7 bg-[#1A1A1A] border-2 border-white p-6 sm:p-8 p5-card-interactive p5-shadow-red flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-p5-display text-xl text-[#E60012]">
                    01. RETRIEVAL-AUGMENTED GENERATION (RAG)
                  </span>
                  <Sparkles className="w-6 h-6 text-[#E60012]" />
                </div>
                <h3 className="font-p5-display text-3xl text-white tracking-wide">
                  CHATBOT BERBASIS ARSITEKTUR RAG
                </h3>
                <p className="text-sm sm:text-base text-zinc-300 leading-relaxed">
                  Berbeda dari chatbot konvensional yang mengandalkan skrip statis kaku atau model bahasa murni yang rentan mengarang bebas (halusinasi), JAKEVO menggabungkan mesin pencarian vektor (retrieval) dengan pemrosesan bahasa alami (generation).
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-zinc-800 text-xs font-p5-mono text-zinc-400">
                ALUR UTAMA: RETRIEVE RELEVANT CHUNKS → CONSTRUCT CONTEXT → GENERATE ANSWER
              </div>
            </div>

            {/* Pillar 2 (5 cols) */}
            <div className="md:col-span-5 bg-[#E60012] text-white border-2 border-white p-6 sm:p-8 p5-card-interactive p5-shadow-white flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-p5-display text-xl text-white/90">
                    02. DOCUMENT KNOWLEDGE SOURCE
                  </span>
                  <BookOpen className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-p5-display text-3xl text-white tracking-wide">
                  DOKUMEN RESMI SEBAGAI SUMBER PENGETAHUAN
                </h3>
                <p className="text-sm sm:text-base text-white/95 leading-relaxed">
                  Seluruh basis pengetahuan JAKEVO diekstrak langsung dari dokumen PDF panduan pelayanan, daftar persyaratan izin (PM1, IPTM, SIP), dan standar operasional prosedur resmi.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-white/30 text-xs font-p5-mono text-white">
                SOURCE FORMAT: PDF DOCUMENTS &amp; OFFICIAL SOP
              </div>
            </div>

            {/* Pillar 3 (5 cols) */}
            <div className="md:col-span-5 bg-[#1A1A1A] border-2 border-white p-6 sm:p-8 p5-card-interactive p5-shadow-white flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-p5-display text-xl text-[#E60012]">
                    03. PUBLIC SERVICE NAVIGATION
                  </span>
                  <FileSearch className="w-6 h-6 text-[#E60012]" />
                </div>
                <h3 className="font-p5-display text-3xl text-white tracking-wide">
                  MEMBANTU AKSES INFORMASI ADMINISTRASI
                </h3>
                <p className="text-sm sm:text-base text-zinc-300 leading-relaxed">
                  Memudahkan pemohon menemukan syarat berkas, tahapan pengajuan daring, hingga lokasi dan jam layanan kantor tanpa harus membuka puluhan halaman dokumen satu per satu.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-zinc-800 text-xs font-p5-mono text-zinc-400">
                FOKUS: SYARAT BERKAS · PROSEDUR · PANDUAN LAYANAN
              </div>
            </div>

            {/* Pillar 4 (7 cols) */}
            <div className="md:col-span-7 bg-[#1A1A1A] border-2 border-white p-6 sm:p-8 p5-card-interactive p5-shadow-red flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-p5-display text-xl text-[#E60012]">
                    04. CONTEXT-GROUNDED SYNTHESIS
                  </span>
                  <ShieldCheck className="w-6 h-6 text-[#E60012]" />
                </div>
                <h3 className="font-p5-display text-3xl text-white tracking-wide">
                  JAWABAN BERDASARKAN KONTEKS DOKUMEN YANG DITEMUKAN
                </h3>
                <p className="text-sm sm:text-base text-zinc-300 leading-relaxed">
                  Sistem menyusun jawaban semata-mata berdasarkan potongan konteks dokumen yang memiliki kemiripan semantik tertinggi dengan pertanyaan pengguna, lengkap dengan sitasi dokumen sumbernya.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-zinc-800 text-xs font-p5-mono text-zinc-400">
                VERIFIKASI: SITASI DOKUMEN &amp; HALAMAN PADA SETIAP JAWABAN
              </div>
            </div>
          </div>

          {/* Interactive Sample Document Corpus Preview */}
          <div className="bg-[#111111] border-2 border-white p-6 p5-shadow-red">
            <div className="flex flex-wrap items-center justify-between gap-2 pb-4 mb-5 border-b border-zinc-800">
              <div>
                <h3 className="font-p5-display text-2xl text-white tracking-wide">
                  CONTOH KORPUS DOKUMEN PELAYANAN YANG TERINDEKS
                </h3>
                <p className="text-xs sm:text-sm text-zinc-400">
                  Klik tombol "Uji Kueri Ini" pada dokumen mana pun untuk langsung menguji respons chatbot
                </p>
              </div>
              <span className="font-p5-mono text-xs text-[#E60012]">
                {KNOWLEDGE_BASE.length} SAMPEL DOKUMEN SOP AKTIF
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {KNOWLEDGE_BASE.slice(0, 4).map(doc => (
                <div
                  key={doc.id}
                  className="bg-[#18181B] border border-zinc-700 p-4 flex flex-col justify-between space-y-3"
                >
                  <div className="space-y-1.5">
                    <div className="text-[11px] font-p5-mono text-[#E60012] font-bold truncate">
                      {doc.id}
                    </div>
                    <h4 className="font-p5-display text-xl text-white leading-tight">
                      {doc.topic}
                    </h4>
                    <p className="text-xs text-zinc-400 line-clamp-2">{doc.sourceDoc}</p>
                  </div>

                  <div className="pt-2 border-t border-zinc-800 flex items-center justify-between gap-2">
                    <span className="font-p5-mono text-[11px] text-zinc-400">
                      {doc.docType} · {doc.page}
                    </span>
                    <button
                      type="button"
                      onClick={() => handleAskInDemo(doc.question)}
                      className="text-xs font-bold text-white hover:text-[#E60012] flex items-center gap-1 cursor-pointer whitespace-nowrap shrink-0"
                    >
                      <span>Uji Kueri Ini</span>
                      <ArrowUpRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* =====================================================================
          SECTION 3 – PROBLEM & SOLUTION
          ===================================================================== */}
      <section
        id="problem-solution"
        className="py-20 sm:py-24 bg-[#111111] p5-diagonal-stripes border-b-4 border-white"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
          <div className="max-w-3xl space-y-3">
            <div className="text-xs font-p5-mono text-[#E60012] uppercase tracking-widest">
              02. CHALLENGE VS RAG INTERVENTION
            </div>
            <h2 className="font-p5-display text-4xl sm:text-5xl text-white tracking-wide">
              MASALAH &amp; SOLUSI JAKEVO
            </h2>
            <p className="text-base text-zinc-300 leading-relaxed">
              Mengapa pencarian informasi pelayanan administrasi secara manual membutuhkan transformasi menuju pendekatan berbasis Retrieval-Augmented Generation.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
            {/* LEFT: THE PROBLEM (6 cols) */}
            <div className="lg:col-span-6 bg-[#18181B] border-2 border-zinc-600 p-6 sm:p-8 p5-shadow-white flex flex-col justify-between">
              <div className="space-y-6">
                <div className="flex items-center justify-between border-b-2 border-zinc-700 pb-4">
                  <div>
                    <span className="text-xs font-p5-mono text-zinc-400 uppercase">
                      KONDISI KONVENSIONAL
                    </span>
                    <h3 className="font-p5-display text-3xl sm:text-4xl text-white tracking-wide mt-0.5">
                      THE PROBLEM: MANUAL SEARCH
                    </h3>
                  </div>
                  <div className="w-12 h-12 bg-zinc-800 border-2 border-white flex items-center justify-center text-zinc-200">
                    <AlertOctagon className="w-6 h-6" />
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="bg-[#111111] border border-zinc-800 p-4">
                    <div className="font-p5-display text-xl text-white tracking-wide">
                      01. Kesulitan Mencari Informasi dalam Dokumen Panjang
                    </div>
                    <p className="text-xs sm:text-sm text-zinc-400 mt-1 leading-relaxed">
                      Buku panduan dan dokumen regulasi pelayanan sering kali terdiri dari puluhan hingga ratusan halaman teknis yang padat.
                    </p>
                  </div>

                  <div className="bg-[#111111] border border-zinc-800 p-4">
                    <div className="font-p5-display text-xl text-white tracking-wide">
                      02. Informasi Pelayanan Tersebar di Banyak Dokumen
                    </div>
                    <p className="text-xs sm:text-sm text-zinc-400 mt-1 leading-relaxed">
                      Syarat administrasi untuk layanan kelurahan, kecamatan, hingga perizinan profesi tersimpan dalam berkas dokumen yang terpisah-pisah.
                    </p>
                  </div>

                  <div className="bg-[#111111] border border-zinc-800 p-4">
                    <div className="font-p5-display text-xl text-white tracking-wide">
                      03. Pengguna Harus Membaca Dokumen Secara Manual
                    </div>
                    <p className="text-xs sm:text-sm text-zinc-400 mt-1 leading-relaxed">
                      Masyarakat harus mengunduh, membuka, dan memindai isi dokumen secara manual untuk menemukan satu poin persyaratan spesifik.
                    </p>
                  </div>

                  <div className="bg-[#111111] border border-zinc-800 p-4">
                    <div className="font-p5-display text-xl text-white tracking-wide">
                      04. Pencarian Informasi Membutuhkan Waktu
                    </div>
                    <p className="text-xs sm:text-sm text-zinc-400 mt-1 leading-relaxed">
                      Proses pencarian manual memakan waktu lama dan berisiko menyebabkan salah paham terhadap persyaratan berkas.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* RIGHT: THE SOLUTION (6 cols) */}
            <div className="lg:col-span-6 bg-[#1A1A1A] border-2 border-[#E60012] p-6 sm:p-8 p5-shadow-lg-red flex flex-col justify-between">
              <div className="space-y-6">
                <div className="flex items-center justify-between border-b-2 border-[#E60012] pb-4">
                  <div>
                    <span className="text-xs font-p5-mono text-[#E60012] uppercase">
                      PENDEKATAN INTELLIGENT RAG
                    </span>
                    <h3 className="font-p5-display text-3xl sm:text-4xl text-white tracking-wide mt-0.5">
                      THE SOLUTION: JAKEVO RAG
                    </h3>
                  </div>
                  <div className="w-12 h-12 bg-[#E60012] border-2 border-white flex items-center justify-center text-white transform -rotate-3">
                    <Zap className="w-6 h-6" />
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="bg-[#111111] border border-zinc-700 p-4">
                    <div className="font-p5-display text-xl text-[#E60012] tracking-wide">
                      01. Pengguna Cukup Mengajukan Pertanyaan
                    </div>
                    <p className="text-xs sm:text-sm text-zinc-200 mt-1 leading-relaxed">
                      Pengguna langsung mengetik pertanyaan dalam bahasa alami (contoh: <em>"Apa syarat mengurus SKTM?"</em>) tanpa perlu tahu di file mana aturan itu berada.
                    </p>
                  </div>

                  <div className="bg-[#111111] border border-zinc-700 p-4">
                    <div className="font-p5-display text-xl text-[#E60012] tracking-wide">
                      02. Sistem Mencari Informasi Relevan dari Dokumen
                    </div>
                    <p className="text-xs sm:text-sm text-zinc-200 mt-1 leading-relaxed">
                      Mesin vector retrieval secara otomatis menelusuri seluruh potongan dokumen di ChromaDB untuk menemukan bagian yang paling relevan.
                    </p>
                  </div>

                  <div className="bg-[#111111] border border-zinc-700 p-4">
                    <div className="font-p5-display text-xl text-[#E60012] tracking-wide">
                      03. Informasi Disusun Menjadi Konteks Terstruktur
                    </div>
                    <p className="text-xs sm:text-sm text-zinc-200 mt-1 leading-relaxed">
                      Potongan teks dokumen terbaik yang ditemukan digabungkan menjadi paket konteks yang presisi beserta metadata sumbernya.
                    </p>
                  </div>

                  <div className="bg-[#111111] border border-zinc-700 p-4">
                    <div className="font-p5-display text-xl text-[#E60012] tracking-wide">
                      04. LLM Menghasilkan Jawaban Berdasarkan Konteks Tersebut
                    </div>
                    <p className="text-xs sm:text-sm text-zinc-200 mt-1 leading-relaxed">
                      Large Language Model menyintesis jawaban yang mudah dipahami pengguna dengan tetap berpegang teguh pada konteks dokumen yang diberikan.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* =====================================================================
          SECTION 4 – HOW IT WORKS (INTERACTIVE RAG ARCHITECTURE)
          ===================================================================== */}
      <section
        id="how-it-works"
        className="py-20 sm:py-24 bg-[#141414] border-b-4 border-[#E60012]"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
          <div className="max-w-3xl space-y-3">
            <div className="text-xs font-p5-mono text-[#E60012] uppercase tracking-widest">
              03. INTERACTIVE RAG PIPELINE BLUEPRINT
            </div>
            <h2 className="font-p5-display text-4xl sm:text-5xl text-white tracking-wide">
              HOW IT WORKS: ARSITEKTUR SISTEM RAG
            </h2>
            <p className="text-base text-zinc-300 leading-relaxed">
              Sistem JAKEVO terbagi menjadi dua alur kerja utama: <strong>Document Ingestion</strong> (pemrosesan dokumen PDF ke ChromaDB) dan <strong>Question Processing</strong> (pencarian vektor hingga generasi jawaban). Klik setiap komponen di bawah ini untuk mempelajari cara kerjanya.
            </p>
          </div>

          <RagArchitectureVisualizer />
        </div>
      </section>

      {/* =====================================================================
          SECTION 5 – TECHNOLOGY STACK
          ===================================================================== */}
      <section
        id="tech-stack"
        className="py-20 sm:py-24 bg-[#111111] p5-halftone-bg border-b-4 border-white"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
          <div className="max-w-3xl space-y-3">
            <div className="text-xs font-p5-mono text-[#E60012] uppercase tracking-widest">
              04. VERIFIED CORE STACK
            </div>
            <h2 className="font-p5-display text-4xl sm:text-5xl text-white tracking-wide">
              TECHNOLOGY STACK JAKEVO
            </h2>
            <p className="text-base text-zinc-300 leading-relaxed">
              Komponen teknologi terkonfirmasi yang membangun fondasi ekstraksi dokumen, representasi vektor multibahasa, penyimpanan ChromaDB, dan generasi jawaban berbasis RAG.
            </p>
          </div>

          {/* Interactive Tech Stack Grid + Active Spotlight */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* 7 Confirmed Tech Stack Cards */}
            <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-4">
              {TECH_STACK_ITEMS.map((tech, index) => {
                const isSelected = tech.id === selectedTechId;
                return (
                  <button
                    key={tech.id}
                    type="button"
                    onClick={() => {
                      soundFX.playSelect();
                      setSelectedTechId(tech.id);
                    }}
                    className={`text-left p-5 border-2 transition-all cursor-pointer ${
                      index === TECH_STACK_ITEMS.length - 1 ? 'sm:col-span-2' : ''
                    } ${
                      isSelected
                        ? 'bg-[#E60012] text-white border-white p5-shadow-white -translate-y-1'
                        : 'bg-[#18181B] text-white border-zinc-700 hover:border-white'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2 mb-3">
                      <span className="font-p5-mono text-xs uppercase tracking-wider opacity-90">
                        {tech.category}
                      </span>
                      <div className={isSelected ? 'text-white' : 'text-[#E60012]'}>
                        {TECH_ICONS[tech.id]}
                      </div>
                    </div>

                    <h3 className="font-p5-display text-2xl tracking-wide leading-tight mb-1.5 break-words">
                      {tech.name}
                    </h3>
                    <p className={`text-xs leading-relaxed ${isSelected ? 'text-white/90' : 'text-zinc-400'}`}>
                      {tech.description}
                    </p>
                  </button>
                );
              })}
            </div>

            {/* Active Tech Role Dossier */}
            <div className="lg:col-span-5 lg:sticky lg:top-24 bg-[#18181B] border-2 border-white p-6 sm:p-7 p5-shadow-lg-red space-y-5">
              <div className="flex items-center justify-between gap-3 pb-4 border-b-2 border-[#E60012]">
                <div>
                  <span className="text-xs font-p5-mono text-[#E60012] uppercase tracking-widest">
                    SYSTEM ROLE SPECIFICATION
                  </span>
                  <h3 className="font-p5-display text-3xl text-white tracking-wide mt-1 break-words">
                    {activeTech.name}
                  </h3>
                </div>
                <div className="w-12 h-12 bg-[#111111] border-2 border-white text-[#E60012] flex items-center justify-center shrink-0">
                  {TECH_ICONS[activeTech.id]}
                </div>
              </div>

              <div className="space-y-2">
                <div className="text-xs font-p5-mono text-zinc-400 uppercase">
                  DESKRIPSI TEKNOLOGI
                </div>
                <p className="text-sm text-zinc-200 leading-relaxed">{activeTech.description}</p>
              </div>

              <div className="bg-[#111111] border border-zinc-700 p-4 space-y-1.5">
                <div className="text-xs font-p5-mono text-[#E60012] uppercase font-bold">
                  PERAN SPESIFIK DALAM SISTEM JAKEVO
                </div>
                <p className="text-sm text-white leading-relaxed">{activeTech.systemRole}</p>
              </div>

              <div className="pt-2 flex items-center justify-between text-xs font-p5-mono text-zinc-400 border-t border-zinc-800">
                <span>SPESIFIKASI:</span>
                <span className="text-white font-semibold">{activeTech.specDetail}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* =====================================================================
          SECTION 6 – CHATBOT DEMONSTRATION
          ===================================================================== */}
      <section
        id="chatbot-demo"
        className="py-20 sm:py-24 bg-[#141414] border-b-4 border-[#E60012]"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
          <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6">
            <div className="max-w-3xl space-y-3">
              <div className="text-xs font-p5-mono text-[#E60012] uppercase tracking-widest">
                05. INTERACTIVE RAG TERMINAL
              </div>
              <h2 className="font-p5-display text-4xl sm:text-5xl text-white tracking-wide">
                CHATBOT DEMONSTRATION: SIMULASI JAKEVO
              </h2>
              <p className="text-base text-zinc-300 leading-relaxed">
                Uji langsung kemampuan pencarian dokumen dan penyusunan jawaban JAKEVO. Komponen ini siap terhubung ke endpoint FastAPI lokal (<code>http://127.0.0.1:8000/api/chat</code>) dan secara otomatis menyediakan simulasi percakapan berbasis korpus SOP apabila server API backend belum dijalankan.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3 shrink-0">
              <button
                type="button"
                onClick={() => {
                  soundFX.playSelect();
                  setIsPopupChatOpen(true);
                }}
                className="p5-btn-secondary px-4 py-2.5 text-sm whitespace-nowrap shrink-0"
              >
                <span className="p5-unskew flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-[#E60012]" />
                  <span>BUKA DALAM MODE POP-UP WIDGET</span>
                </span>
              </button>
            </div>
          </div>

          {/* Embedded Full-Width Persona 5 Chatbot */}
          <PersonaChatbot
            mode="embedded"
            externalQuery={externalChatQuery}
            onExternalQueryHandled={() => setExternalChatQuery(null)}
          />
        </div>
      </section>

      {/* =====================================================================
          SECTION 7 – RETRIEVAL & EVALUATION
          ===================================================================== */}
      <section
        id="evaluation"
        className="py-20 sm:py-24 bg-[#111111] border-b-4 border-white"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
          <div className="max-w-3xl space-y-3">
            <div className="text-xs font-p5-mono text-[#E60012] uppercase tracking-widest">
              06. SYSTEM QUALITY &amp; BENCHMARK FRAMEWORK
            </div>
            <h2 className="font-p5-display text-4xl sm:text-5xl text-white tracking-wide">
              RETRIEVAL &amp; EVALUATION METRICS
            </h2>
            <p className="text-base text-zinc-300 leading-relaxed">
              Bagaimana kualitas temu kembali informasi (retrieval) pada JAKEVO diukur menggunakan metrik evaluasi standar: <strong>Hit@K</strong>, <strong>Recall@K</strong>, <strong>Mean Reciprocal Rank (MRR)</strong>, <strong>Retrieval Accuracy</strong>, serta analisis kesalahan retrieval.
            </p>
          </div>

          <EvaluationSection />
        </div>
      </section>

      {/* =====================================================================
          SECTION 7.5 – CO-OP CREATORS IDENTITY (2 PEMBUAT KANAN-KIRI)
          ===================================================================== */}
      <section
        id="coop-creators"
        className="py-20 sm:py-24 bg-[#141414] p5-diagonal-stripes border-b-4 border-[#E60012]"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
          <div className="max-w-3xl space-y-3">
            <div className="text-xs font-p5-mono text-[#E60012] uppercase tracking-widest">
              07. CO-OP PARTY MEMBERS // IDENTITAS TIM PEMBUAT
            </div>
            <h2 className="font-p5-display text-4xl sm:text-5xl text-white tracking-wide">
              CO-OP MODE: IDENTITAS TIM PENGEMBANG
            </h2>
            <p className="text-base text-zinc-300 leading-relaxed">
              Kolaborasi dua pengembang dalam mode <strong>Co-Op Tag-Team</strong> (Kiri &amp; Kanan) yang menggabungkan rekayasa sistem <em>Retrieval-Augmented Generation</em> dengan desain antarmuka interaktif bergaya Persona 5 Royal. Anda dapat mengganti foto profil dan menyesuaikan data identitas langsung melalui tombol <strong>Edit Identitas &amp; Foto</strong>.
            </p>
          </div>

          <CoopCreatorsSection />
        </div>
      </section>

      {/* =====================================================================
          SECTION 8 – CLOSING
          ===================================================================== */}
      <section className="py-24 sm:py-28 bg-[#E60012] p5-red-stripes text-white relative overflow-hidden border-b-4 border-white">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center space-y-8">
          <div className="inline-block bg-[#111111] text-white font-p5-mono text-xs uppercase tracking-widest px-4 py-1.5 border-2 border-white transform -skew-x-6">
            <span className="inline-block transform skew-x-6">
              JAKEVO RAG SHOWCASE SUMMARY
            </span>
          </div>

          <h2
            className="font-p5-display text-white tracking-tight leading-[0.95] drop-shadow-[4px_4px_0px_#111111]"
            style={{ fontSize: 'clamp(2.5rem, 5.5vw, 4.75rem)', textWrap: 'balance' }}
          >
            "THE RIGHT INFORMATION. AT THE RIGHT TIME."
          </h2>

          <p className="text-base sm:text-lg text-white/95 max-w-2xl mx-auto leading-relaxed font-medium bg-[#111111]/90 border-2 border-white p-5 p5-shadow-black">
            Dengan menggabungkan ekstraksi dokumen PDF, model embedding multibahasa <strong>paraphrase-multilingual-MiniLM-L12-v2</strong>, basis data vektor <strong>ChromaDB</strong>, dan sintesis <strong>LLM</strong>, JAKEVO menghadirkan akses informasi prosedur pelayanan administrasi yang cepat, transparan, dan selalu berakar pada dokumen sumber.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
            <button
              type="button"
              onClick={() => scrollToSection('chatbot-demo')}
              className="px-8 py-4 bg-[#111111] text-white hover:bg-white hover:text-[#111111] font-p5-display text-2xl tracking-wider border-2 border-white p5-shadow-white transition-all transform -skew-x-8 cursor-pointer"
            >
              <span className="inline-block transform skew-x-8">
                KEMBALI KE DEMONSTRASI CHATBOT ↑
              </span>
            </button>

            <button
              type="button"
              onClick={() => {
                soundFX.playSelect();
                setIsPopupChatOpen(true);
              }}
              className="px-6 py-4 bg-white text-[#111111] hover:bg-[#111111] hover:text-white font-p5-display text-xl tracking-wider border-2 border-[#111111] p5-shadow-black transition-all transform -skew-x-8 cursor-pointer"
            >
              <span className="inline-block transform skew-x-8">
                BUKA WIDGET CHATBOT
              </span>
            </button>
          </div>
        </div>
      </section>

      {/* =====================================================================
          QUIET FOOTER
          ===================================================================== */}
      <footer className="bg-[#111111] text-zinc-400 py-10 px-4 sm:px-6 lg:px-8 text-xs">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="font-p5-display text-xl text-white tracking-wider">JAKEVO</span>
            <span>·</span>
            <span>Intelligent Document-Based RAG Chatbot Showcase</span>
          </div>

          <div className="flex flex-wrap items-center gap-5">
            <a href="#home" className="hover:text-white transition-colors">
              Home
            </a>
            <a href="#about" className="hover:text-white transition-colors">
              About
            </a>
            <a href="#how-it-works" className="hover:text-white transition-colors">
              Architecture
            </a>
            <a href="#chatbot-demo" className="hover:text-white transition-colors">
              Demo
            </a>
            <a href="#coop-creators" className="hover:text-white transition-colors">
              Co-Op Team
            </a>
          </div>
        </div>
      </footer>

      {/* =====================================================================
          FLOATING PERSONA 5 CHATBOT WIDGET & POPUP MODAL
          ===================================================================== */}
      <PersonaChatbot
        mode="popup"
        isOpen={isPopupChatOpen}
        onClose={() => setIsPopupChatOpen(false)}
      />

      <button
        type="button"
        onClick={() => {
          soundFX.playSelect();
          setIsPopupChatOpen(prev => !prev);
        }}
        className="fixed bottom-5 right-5 z-40 bg-[#E60012] hover:bg-white text-white hover:text-[#111111] border-2 border-white px-4 py-2.5 p5-shadow-white flex items-center gap-2.5 transition-all transform -skew-x-6 cursor-pointer"
        aria-label="Buka atau Tutup Widget Chatbot JAKEVO"
      >
        <div className="transform skew-x-6 flex items-center gap-2">
          {isPopupChatOpen ? (
            <>
              <X className="w-5 h-5" />
              <span className="font-p5-display text-lg tracking-wider">TUTUP CHATBOT</span>
            </>
          ) : (
            <>
              <MessageSquare className="w-5 h-5" />
              <span className="font-p5-display text-lg tracking-wider">TANYA JAKEVO BOT</span>
            </>
          )}
        </div>
      </button>
    </div>
  );
}
