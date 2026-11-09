import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  RotateCcw,
  Maximize2,
  Minimize2,
  X,
  FileText,
  Sparkles,
  Copy,
  Check,
  ChevronLeft,
  ChevronRight,
  SlidersHorizontal,
  BookOpen,
  Search,
  MessageSquare,
  AlertCircle
} from 'lucide-react';
import { runRagPipeline, RagResult } from '../data/jakevoData';
import { soundFX } from '../utils/sound';

export interface ChatMessageItem {
  id: string;
  sender: 'user' | 'bot';
  text: string;
  timestamp: string;
  ragResult?: RagResult;
}

const QUICK_QUESTIONS = [
  'Di mana alamat kantor DPMPTSP?',
  'Bagaimana alur pengajuan izin di JAKEVO?',
  'Apa saja syarat Surat Keterangan Tidak Mampu (SKTM)?',
  'Apa syarat surat pengantar perkawinan pertama?',
  'Apa syarat surat keterangan belum memiliki rumah?',
  'Apa saja syarat izin penggunaan tanah makam?',
  'Apa saja syarat surat izin praktik dokter?',
  'Bagaimana alur izin JAKEVO dan eskalasi ke petugas?'
];

function getFormattedTime(): string {
  const now = new Date();
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  return `${hours}.${minutes}`;
}

function getDocLabelFromUrl(url: string): string {
  if (!url) return 'Unduh Dokumen';
  const filename =
    url
      .split('/')
      .pop()
      ?.replace(/\.(docx|pdf|doc|xlsx)$/i, '')
      .replace(/[_-]/g, ' ')
      .trim() || 'Dokumen';
  if (filename.length > 20 && /^[0-9a-fA-F]+$/.test(filename)) {
    return 'Unduh Formulir Template';
  }
  return 'Unduh ' + filename.replace(/\b\w/g, l => l.toUpperCase());
}

export function formatUrlsToClickable(htmlText: string): string {
  if (!htmlText) return '';
  if (htmlText.includes('<a ') || htmlText.includes('class="jakevo-link')) {
    return htmlText;
  }
  const cleaned = htmlText.replace(/(?:-&gt;|->)\s*(?=<p|<a|<\/li|<\/p|<br|$)/gi, '');
  const urlPattern = /(?:(?:-&gt;|->)\s*)?(https?:\/\/[^\s<>"')]+)/gi;
  return cleaned.replace(urlPattern, (_match, url: string) => {
    const cleanUrl = url.replace(/[.,;]+$/, '');
    const label = getDocLabelFromUrl(cleanUrl);
    return `<a href="${cleanUrl}" target="_blank" rel="noopener noreferrer" class="jakevo-link-btn" title="Unduh ${label}: ${cleanUrl}">📄 ${label} (Klik disini ↗)</a>`;
  });
}

const INITIAL_BOT_MESSAGE: ChatMessageItem = {
  id: 'init-msg-1',
  sender: 'bot',
  text: 'Halo! Saya JAKEVO Assistant.',
  timestamp: getFormattedTime(),
  ragResult: {
    query: 'Inisialisasi Sistem',
    tokens: ['jakevo', 'dpmptsp', 'sop'],
    isRelevant: true,
    score: 100,
    matchedDoc: {
      id: 'DOC-INIT-000',
      topic: 'Panduan Layanan Informasi Administrasi JAKEVO',
      sourceDoc: 'SOP Layanan Informasi Investasi & Panduan PTSP DKI Jakarta',
      docType: 'SOP',
      page: 'Halaman 1'
    },
    matchedKeywords: ['jakevo', 'perizinan', 'dpmptsp'],
    contextSnippet:
      'JAKEVO adalah chatbot berbasis Retrieval-Augmented Generation (RAG) yang membantu pengguna menemukan informasi dokumen dan prosedur pelayanan administrasi DPMPTSP Provinsi DKI Jakarta.',
    finalAnswer: `<p>Halo! Saya <strong>JAKEVO</strong> — asisten berbasis <em>Retrieval-Augmented Generation (RAG)</em> untuk layanan informasi dokumen dan prosedur administrasi.</p><p>Silakan pilih topik pertanyaan cepat di atas atau ketik pertanyaan Anda mengenai syarat dokumen, alur pengajuan izin JAKEVO, maupun lokasi layanan DPMPTSP DKI Jakarta.</p>`,
    sourceMode: 'STATIC_SIMULATION'
  }
};

interface PersonaChatbotProps {
  mode: 'embedded' | 'popup';
  isOpen?: boolean;
  onClose?: () => void;
  externalQuery?: string | null;
  onExternalQueryHandled?: () => void;
}

export const PersonaChatbot: React.FC<PersonaChatbotProps> = ({
  mode,
  isOpen = true,
  onClose,
  externalQuery,
  onExternalQueryHandled
}) => {
  const [messages, setMessages] = useState<ChatMessageItem[]>([INITIAL_BOT_MESSAGE]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showRagInspector, setShowRagInspector] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [apiEndpoint, setApiEndpoint] = useState('http://127.0.0.1:8000/api/chat');
  const [showApiConfig, setShowApiConfig] = useState(false);
  const [connectionState, setConnectionState] = useState<'STANDBY' | 'FASTAPI_CONNECTED' | 'SIMULATION_FALLBACK'>('STANDBY');

  const chatScrollRef = useRef<HTMLDivElement>(null);
  const chipsScrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTo({
        top: chatScrollRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  useEffect(() => {
    if (externalQuery && externalQuery.trim().length > 0) {
      handleSendMessage(externalQuery);
      if (onExternalQueryHandled) {
        onExternalQueryHandled();
      }
    }
  }, [externalQuery]);

  const handleSendMessage = async (rawText: string) => {
    const text = rawText.trim();
    if (!text || isLoading) return;

    soundFX.playSelect();

    const userMsg: ChatMessageItem = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text,
      timestamp: getFormattedTime()
    };

    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: text })
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }

      const backendResult = await response.json();
      setConnectionState('FASTAPI_CONNECTED');

      const normalizedResult: RagResult = {
        query: backendResult.query || text,
        tokens: Array.isArray(backendResult.tokens) ? backendResult.tokens : text.split(/\s+/),
        isRelevant: Boolean(backendResult.isRelevant),
        score: typeof backendResult.score === 'number' ? backendResult.score : 0,
        matchedDoc: backendResult.matchedDoc
          ? {
              id: backendResult.matchedDoc.id || 'DOC-RAG',
              topic: backendResult.matchedDoc.topic || 'Dokumen Layanan JAKEVO',
              sourceDoc:
                backendResult.matchedDoc.sourceDoc ||
                backendResult.matchedDoc.topic ||
                'Korpus Dokumen Resmi DPMPTSP',
              docType: backendResult.matchedDoc.docType || 'PDF / SOP',
              page: backendResult.matchedDoc.page || 'Terindeks ChromaDB'
            }
          : null,
        matchedKeywords: Array.isArray(backendResult.matchedKeywords) ? backendResult.matchedKeywords : [],
        contextSnippet: backendResult.contextSnippet || 'Konteks diambil langsung dari ChromaDB Backend.',
        finalAnswer: backendResult.finalAnswer || '<p>Respons diterima dari server backend.</p>',
        sourceMode: 'FASTAPI_BACKEND'
      };

      const botMsg: ChatMessageItem = {
        id: `bot-${Date.now()}`,
        sender: 'bot',
        text: normalizedResult.finalAnswer,
        timestamp: getFormattedTime(),
        ragResult: normalizedResult
      };

      setMessages(prev => [...prev, botMsg]);
    } catch {
      // Fallback to static/local simulation if FastAPI backend is not running
      setConnectionState('SIMULATION_FALLBACK');
      await new Promise(resolve => setTimeout(resolve, 650));
      const localResult = runRagPipeline(text);

      const botMsg: ChatMessageItem = {
        id: `bot-${Date.now()}`,
        sender: 'bot',
        text: localResult.finalAnswer,
        timestamp: getFormattedTime(),
        ragResult: localResult
      };

      setMessages(prev => [...prev, botMsg]);
    } finally {
      setIsLoading(false);
      setTimeout(() => {
        inputRef.current?.focus();
      }, 60);
    }
  };

  const handleResetChat = () => {
    soundFX.playTransition();
    setMessages([
      {
        ...INITIAL_BOT_MESSAGE,
        id: `init-${Date.now()}`,
        timestamp: getFormattedTime()
      }
    ]);
  };

  const handleCopyMessage = (msgId: string, htmlContent: string) => {
    soundFX.playHover();
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = htmlContent;
    const plainText = tempDiv.innerText || tempDiv.textContent || '';
    navigator.clipboard.writeText(plainText).then(() => {
      setCopiedId(msgId);
      setTimeout(() => setCopiedId(null), 2000);
    });
  };

  const scrollChips = (dir: 'left' | 'right') => {
    soundFX.playHover();
    if (chipsScrollRef.current) {
      chipsScrollRef.current.scrollBy({
        left: dir === 'left' ? -220 : 220,
        behavior: 'smooth'
      });
    }
  };

  if (mode === 'popup' && !isOpen) {
    return null;
  }

  const containerClasses =
    mode === 'popup'
      ? isFullscreen
        ? 'fixed inset-0 z-50 bg-[#111111] border-4 border-[#E60012] flex flex-col overflow-hidden'
        : 'fixed bottom-24 right-4 sm:right-7 z-50 w-[calc(100vw-2rem)] sm:w-[450px] h-[640px] max-h-[calc(100vh-7.5rem)] bg-[#111111] border-2 border-white p5-shadow-lg-red flex flex-col overflow-hidden'
      : 'w-full bg-[#111111] border-2 border-white p5-shadow-lg-red flex flex-col overflow-hidden h-[700px]';

  return (
    <div className={containerClasses} role="region" aria-label="JAKEVO Persona 5 RAG Chatbot">
      {/* A. HEADER — PERSONA 5 CRIMSON COMMAND BAR */}
      <div className="p5-red-stripes border-b-2 border-white px-4 py-3 flex items-center justify-between gap-3 shrink-0">
        <div className="flex items-center gap-3 min-w-0">
          {/* Phantom Mask / Chatbot Emblem */}
          <div className="w-10 h-10 bg-[#111111] border-2 border-white flex items-center justify-center shrink-0 transform -rotate-3 p5-shadow-black">
            <MessageSquare className="w-5 h-5 text-[#E60012]" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="font-p5-display text-xl sm:text-2xl text-white tracking-wider leading-none truncate">
                JAKEVO RAG TERMINAL
              </h3>
            </div>
            <div className="flex items-center gap-2 text-xs text-white/90 font-medium mt-0.5">
              <span>
                {connectionState === 'FASTAPI_CONNECTED'
                  ? 'FastAPI Backend Connected'
                  : connectionState === 'SIMULATION_FALLBACK'
                  ? 'Mode Simulasi Statis (API Lokal Offline)'
                  : 'Siap Menerima Kueri Dokumen'}
              </span>
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-1.5 shrink-0">
          <button
            type="button"
            onClick={() => {
              soundFX.playHover();
              setShowApiConfig(prev => !prev);
            }}
            className="px-2.5 py-1.5 bg-[#111111] text-white border border-white text-xs font-bold hover:bg-white hover:text-[#111111] transition-colors flex items-center gap-1 cursor-pointer whitespace-nowrap shrink-0"
            title="Konfigurasi Endpoint API Backend FastAPI"
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">API</span>
          </button>

          {mode === 'popup' && (
            <button
              type="button"
              onClick={() => {
                soundFX.playSelect();
                setIsFullscreen(prev => !prev);
              }}
              className="px-2.5 py-1.5 bg-[#111111] text-white border border-white text-xs font-bold hover:bg-white hover:text-[#111111] transition-colors flex items-center gap-1 cursor-pointer whitespace-nowrap shrink-0"
              title="Beralih Mode Layar Penuh"
            >
              {isFullscreen ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
              <span className="hidden sm:inline">{isFullscreen ? 'Keluar' : 'Penuh'}</span>
            </button>
          )}

          <button
            type="button"
            onClick={handleResetChat}
            className="p-1.5 bg-[#111111] text-white border border-white hover:bg-white hover:text-[#111111] transition-colors cursor-pointer shrink-0"
            title="Reset Percakapan"
            aria-label="Reset Percakapan"
          >
            <RotateCcw className="w-4 h-4" />
          </button>

          {mode === 'popup' && onClose && (
            <button
              type="button"
              onClick={() => {
                soundFX.playSelect();
                setIsFullscreen(false);
                onClose();
              }}
              className="p-1.5 bg-[#111111] text-white border border-white hover:bg-white hover:text-[#E60012] transition-colors cursor-pointer shrink-0"
              title="Tutup Chatbot"
              aria-label="Tutup Chatbot"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* OPTIONAL API ENDPOINT DRAWER (Honors Backend Integration Requirement) */}
      {showApiConfig && (
        <div className="bg-[#1A1A1A] border-b-2 border-[#E60012] px-4 py-2.5 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2 shrink-0">
          <div className="flex items-center gap-2 text-zinc-300">
            <AlertCircle className="w-4 h-4 text-[#E60012] shrink-0" />
            <span>Endpoint FastAPI (`POST /api/chat`):</span>
          </div>
          <div className="flex items-center gap-2 flex-1 max-w-md">
            <input
              type="text"
              value={apiEndpoint}
              onChange={e => setApiEndpoint(e.target.value)}
              className="w-full bg-[#111111] border border-zinc-600 px-2.5 py-1 text-white font-p5-mono text-xs focus:border-[#E60012] focus:outline-none"
              placeholder="http://127.0.0.1:8000/api/chat"
            />
          </div>
        </div>
      )}

      {/* B. QUICK QUESTION BAR — HORIZONTAL SLIDER */}
      <div className="bg-[#18181B] border-b border-zinc-800 px-4 py-2.5 shrink-0">
        <div className="flex items-center justify-between mb-1.5">
          <div className="flex items-center gap-2 text-xs">
            <span className="font-p5-display text-sm tracking-wider text-[#E60012]">QUICK INTEL</span>
            <span className="text-zinc-400">·</span>
            <span className="text-zinc-400">Pilih contoh kueri prosedur administrasi</span>
          </div>
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => scrollChips('left')}
              className="w-6 h-6 bg-[#111111] border border-zinc-700 text-white flex items-center justify-center hover:border-[#E60012] hover:bg-[#E60012] transition-colors cursor-pointer"
              aria-label="Geser pertanyaan ke kiri"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => scrollChips('right')}
              className="w-6 h-6 bg-[#111111] border border-zinc-700 text-white flex items-center justify-center hover:border-[#E60012] hover:bg-[#E60012] transition-colors cursor-pointer"
              aria-label="Geser pertanyaan ke kanan"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        <div
          ref={chipsScrollRef}
          className="flex items-center gap-2 overflow-x-auto no-scrollbar pb-1"
          style={{ scrollbarWidth: 'none' }}
        >
          {QUICK_QUESTIONS.map((q, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSendMessage(q)}
              className="px-3 py-1.5 bg-[#111111] hover:bg-[#E60012] text-zinc-200 hover:text-white border border-zinc-700 hover:border-white text-xs font-semibold transition-all whitespace-nowrap shrink-0 cursor-pointer transform -skew-x-6"
            >
              <span className="inline-block transform skew-x-6">{q}</span>
            </button>
          ))}
        </div>
      </div>

      {/* C. CHAT CONVERSATION STREAM */}
      <div
        ref={chatScrollRef}
        className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-5 p5-halftone-white bg-[#111111]"
      >
        {messages.map(msg => {
          if (msg.sender === 'user') {
            return (
              <div key={msg.id} className="flex justify-end">
                <div className="max-w-[85%] sm:max-w-[78%] bg-[#E60012] text-white border-2 border-white px-4 py-3 p5-shadow-white transform -rotate-1">
                  <div className="text-xs font-p5-display tracking-wider text-white/90 mb-1">
                    USER INQUIRY · {msg.timestamp}
                  </div>
                  <p className="text-sm sm:text-base font-semibold leading-relaxed">{msg.text}</p>
                </div>
              </div>
            );
          }

          const rag = msg.ragResult;
          return (
            <div key={msg.id} className="flex items-start gap-3">
              {/* Persona 5 Stylized Bot Avatar */}
              <div className="w-10 h-10 bg-white text-[#111111] border-2 border-[#E60012] flex flex-col items-center justify-center shrink-0 font-p5-display text-sm leading-none transform rotate-2 p5-shadow-red select-none">
                <span className="text-[#E60012] text-[10px]">RAG</span>
                <span className="font-black text-base">JKV</span>
              </div>

              <div className="flex-1 min-w-0 space-y-2.5">
                {/* Main Bot Dialogue Box */}
                <div className="bg-[#1A1A1A] border-2 border-white p-4 p5-shadow-red">
                  {/* Dialogue Header */}
                  <div className="flex flex-wrap items-center justify-between gap-2 pb-2 mb-2.5 border-b border-zinc-800 text-xs">
                    <div className="flex items-center gap-2">
                      <span className="font-p5-display text-base tracking-wide text-white">
                        JAKEVO ASSISTANT
                      </span>
                      <span className="text-zinc-500">·</span>
                      <span className="text-zinc-400">
                        {rag?.sourceMode === 'FASTAPI_BACKEND'
                          ? 'Live FastAPI Response'
                          : 'Static Simulation Mode'}
                      </span>
                    </div>
                    <span className="text-zinc-400 font-p5-mono">{msg.timestamp}</span>
                  </div>

                  {/* Answer Body */}
                  <div
                    className="p5-chat-prose text-sm text-zinc-200 leading-relaxed"
                    dangerouslySetInnerHTML={{
                      __html: formatUrlsToClickable(rag ? rag.finalAnswer : msg.text)
                    }}
                  />

                  {/* Source Document Reference Card (Required by Section 6: Source, Page & Doc Type) */}
                  {rag && (
                    <div className="mt-4 bg-[#111111] border border-zinc-700 p-3">
                      <div className="flex items-center justify-between gap-2 text-xs text-zinc-400 mb-1.5">
                        <span className="font-p5-display text-sm text-[#E60012] tracking-wider flex items-center gap-1.5">
                          <BookOpen className="w-3.5 h-3.5" />
                          SOURCE DOCUMENT REFERENCE
                        </span>
                        <span className="font-p5-mono text-zinc-300">
                          {rag.matchedDoc?.docType || 'DOKUMEN'} · {rag.matchedDoc?.page || 'Halaman Terindeks'}
                        </span>
                      </div>

                      {rag.isRelevant && rag.matchedDoc ? (
                        <div className="space-y-1">
                          <div className="text-xs font-p5-mono text-white font-semibold">
                            ID: {rag.matchedDoc.id}
                          </div>
                          <div className="text-xs text-zinc-300">{rag.matchedDoc.sourceDoc}</div>
                        </div>
                      ) : (
                        <div className="text-xs text-zinc-400">
                          DEFAULT-FALLBACK · Kueri berada di bawah ambang batas kemiripan dokumen (&lt; 15%).
                        </div>
                      )}
                    </div>
                  )}

                  {/* Footer Actions */}
                  <div className="mt-3 pt-2 border-t border-zinc-800/80 flex items-center justify-between text-xs text-zinc-400">
                    <span>Konteks Dokumen Terverifikasi</span>
                    <button
                      type="button"
                      onClick={() => handleCopyMessage(msg.id, rag ? rag.finalAnswer : msg.text)}
                      className="inline-flex items-center gap-1 text-zinc-300 hover:text-white transition-colors cursor-pointer"
                    >
                      {copiedId === msg.id ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-[#E60012]" />
                          <span className="text-white font-semibold">Tersalin</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5" />
                          <span>Salin Jawaban</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {/* RAG Pipeline Inspector Box */}
                {showRagInspector && rag && (
                  <div className="bg-[#141414] border border-zinc-800 p-3.5 text-xs space-y-2.5">
                    <div className="flex items-center justify-between">
                      <span className="font-p5-display text-sm tracking-wider text-white flex items-center gap-1.5">
                        <Sparkles className="w-3.5 h-3.5 text-[#E60012]" />
                        RAG RETRIEVAL TELEMETRY
                      </span>
                      <span className="font-p5-mono text-zinc-400">
                        Relevance Score: <strong className="text-white">{rag.score}%</strong>
                      </span>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full h-1.5 bg-zinc-800 overflow-hidden">
                      <div
                        className="h-full bg-[#E60012] transition-all duration-300"
                        style={{ width: `${Math.max(rag.score, 6)}%` }}
                      />
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1 text-zinc-300">
                      <div className="bg-[#111111] p-2 border border-zinc-800/90">
                        <div className="text-[11px] text-zinc-400 uppercase font-semibold">
                          1. Query Tokens ({rag.tokens.length})
                        </div>
                        <div className="font-p5-mono text-xs text-white truncate mt-0.5">
                          {rag.tokens.length > 0 ? rag.tokens.join(', ') : '-'}
                        </div>
                      </div>

                      <div className="bg-[#111111] p-2 border border-zinc-800/90">
                        <div className="text-[11px] text-zinc-400 uppercase font-semibold">
                          2. Matched Keywords
                        </div>
                        <div className="font-p5-mono text-xs text-white truncate mt-0.5">
                          {rag.matchedKeywords.length > 0
                            ? rag.matchedKeywords.join(', ')
                            : 'Tidak ada kata kunci spesifik'}
                        </div>
                      </div>
                    </div>

                    <div className="bg-[#111111] p-2 border border-zinc-800/90 text-zinc-300">
                      <span className="text-[11px] text-zinc-400 uppercase font-semibold block">
                        3. Context Snippet Injected to LLM:
                      </span>
                      <p className="text-xs text-zinc-300 mt-0.5 line-clamp-2">{rag.contextSnippet}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Loading Animation */}
        {isLoading && (
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#E60012] text-white border-2 border-white flex items-center justify-center font-p5-display text-sm animate-bounce">
              ...
            </div>
            <div className="bg-[#1A1A1A] border-2 border-white px-4 py-3 p5-shadow-red">
              <div className="flex items-center gap-2 text-xs font-p5-display tracking-wider text-[#E60012]">
                <FileText className="w-4 h-4 animate-spin" />
                <span>MENGEKSTRAK KONTEKS DOKUMEN CHROMADB...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* D. INPUT COMMAND BAR */}
      <div className="bg-[#161616] border-t-2 border-white p-3.5 shrink-0">
        <form
          onSubmit={e => {
            e.preventDefault();
            handleSendMessage(inputValue);
          }}
          className="flex items-center gap-2"
        >
          <div className="relative flex-1 flex items-center bg-[#111111] border-2 border-white focus-within:border-[#E60012] px-3 py-2">
            <Search className="w-4 h-4 text-zinc-400 mr-2 shrink-0" />
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              disabled={isLoading}
              placeholder="Tanyakan syarat dokumen atau prosedur layanan JAKEVO..."
              className="w-full bg-transparent text-sm text-white placeholder-zinc-500 focus:outline-none"
              aria-label="Tulis pertanyaan Anda seputar layanan JAKEVO"
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="p5-btn-primary px-5 py-2.5 text-base disabled:opacity-50"
          >
            <span className="p5-unskew flex items-center gap-1.5">
              <span>KIRIM</span>
              <Send className="w-4 h-4" />
            </span>
          </button>
        </form>

        <div className="flex flex-wrap items-center justify-between gap-2 mt-2.5 text-xs text-zinc-400">
          <label className="inline-flex items-center gap-2 cursor-pointer select-none hover:text-white transition-colors">
            <input
              type="checkbox"
              checked={showRagInspector}
              onChange={e => {
                soundFX.playHover();
                setShowRagInspector(e.target.checked);
              }}
              className="accent-[#E60012] w-3.5 h-3.5 cursor-pointer"
            />
            <span>Tampilkan inspektor proses RAG (Retrieval &amp; Konteks)</span>
          </label>

          <span className="text-[11px] text-zinc-400">
            Terhubung otomatis ke FastAPI jika aktif · Fallback simulasi statis tersedia
          </span>
        </div>
      </div>
    </div>
  );
};
