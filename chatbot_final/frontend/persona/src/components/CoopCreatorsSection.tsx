import React, { useState, useEffect } from 'react';
import {
  Camera,
  Edit3,
  Check,
  RotateCcw,
  Sparkles,
  Swords,
  Shield,
  Cpu,
  Layout,
  Building2,
  GraduationCap,
  Calendar
} from 'lucide-react';
import { soundFX } from '../utils/sound';

export interface CreatorProfile {
  id: 'p1' | 'p2';
  playerTag: string;
  codename: string;
  arcana: string;
  name: string;
  nim: string;
  university: string;
  major: string;
  roleTitle: string;
  focusDescription: string;
  photoUrl: string | null;
  skills: { label: string; power: string }[];
}

export interface InstitutionInfo {
  agency: string;
  unit: string;
  fieldSupervisor: string;
  academicSupervisor: string;
  period: string;
}

const DEFAULT_CREATORS: [CreatorProfile, CreatorProfile] = [
  {
    id: 'p1',
    playerTag: 'PLAYER 01 // LEFT WING',
    codename: 'ORACLE OF ARCHIVES',
    arcana: 'CONFIDANT RANK MAX · AI & RAG LEAD',
    name: '[Nama Pembuat 1]',
    nim: '[NIM Pembuat 1]',
    university: '[Nama Universitas / Kampus]',
    major: 'Teknik Informatika / Ilmu Komputer',
    roleTitle: 'AI Engineer & RAG Pipeline Architect',
    focusDescription:
      'Merancang pipeline ekstraksi dokumen PDF, strategi chunking, enkoding vektor paraphrase-multilingual-MiniLM-L12-v2, indeksasi ChromaDB, serta evaluasi retrieval.',
    photoUrl: null,
    skills: [
      { label: 'ChromaDB Vector Retrieval', power: 'SEVERE' },
      { label: 'Multilingual Embedding (384-d)', power: 'HEAVY' },
      { label: 'PDF Ingestion & Data Cleaning', power: 'HEAVY' },
      { label: 'FastAPI Backend Integration', power: 'MAX' }
    ]
  },
  {
    id: 'p2',
    playerTag: 'PLAYER 02 // RIGHT WING',
    codename: 'PHANTOM STYLIST',
    arcana: 'CONFIDANT RANK MAX · UI/UX & WEB LEAD',
    name: '[Nama Pembuat 2]',
    nim: '[NIM Pembuat 2]',
    university: '[Nama Universitas / Kampus]',
    major: 'Teknik Informatika / Sistem Informasi',
    roleTitle: 'Frontend Architect & Interactive UI Designer',
    focusDescription:
      'Membangun antarmuka showcase bergaya Persona 5 Royal, visualisasi interaktif arsitektur RAG, animasi transisi, serta komponen simulasi dan widget chatbot.',
    photoUrl: null,
    skills: [
      { label: 'Persona 5 Royal UI System', power: 'SEVERE' },
      { label: 'Interactive RAG Visualization', power: 'HEAVY' },
      { label: 'Chatbot Interface & Telemetry', power: 'MAX' },
      { label: 'Responsive Motion Architecture', power: 'HEAVY' }
    ]
  }
];

const DEFAULT_INSTITUTION: InstitutionInfo = {
  agency: 'DPMPTSP Provinsi DKI Jakarta',
  unit: 'Sistem Perizinan Terpadu JAKEVO · Mal Pelayanan Publik Lt. 5',
  fieldSupervisor: '[Nama Pembimbing Instansi]',
  academicSupervisor: '[Nama Dosen Pembimbing]',
  period: '2026 · Proyek Pengembangan Chatbot RAG JAKEVO'
};

const STORAGE_KEY_CREATORS = 'jakevo_p5_coop_creators_v1';
const STORAGE_KEY_INST = 'jakevo_p5_coop_inst_v1';

export const CoopCreatorsSection: React.FC = () => {
  const [creators, setCreators] = useState<[CreatorProfile, CreatorProfile]>(DEFAULT_CREATORS);
  const [institution, setInstitution] = useState<InstitutionInfo>(DEFAULT_INSTITUTION);
  const [isEditing, setIsEditing] = useState(false);
  const [activeSynergy, setActiveSynergy] = useState(false);

  // Load saved profile data from localStorage
  useEffect(() => {
    try {
      const savedCreators = localStorage.getItem(STORAGE_KEY_CREATORS);
      if (savedCreators) {
        const parsed = JSON.parse(savedCreators);
        if (Array.isArray(parsed) && parsed.length === 2) {
          setCreators([parsed[0], parsed[1]]);
        }
      }
      const savedInst = localStorage.getItem(STORAGE_KEY_INST);
      if (savedInst) {
        setInstitution(JSON.parse(savedInst));
      }
    } catch {
      // Ignore storage errors
    }
  }, []);

  const saveToStorage = (
    updatedCreators: [CreatorProfile, CreatorProfile],
    updatedInst: InstitutionInfo
  ) => {
    try {
      localStorage.setItem(STORAGE_KEY_CREATORS, JSON.stringify(updatedCreators));
      localStorage.setItem(STORAGE_KEY_INST, JSON.stringify(updatedInst));
    } catch {
      // Ignore storage quota errors
    }
  };

  const handlePhotoUpload = (index: 0 | 1, e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    soundFX.playSelect();
    const reader = new FileReader();
    reader.onload = event => {
      const dataUrl = event.target?.result as string;
      const next: [CreatorProfile, CreatorProfile] = [{ ...creators[0] }, { ...creators[1] }];
      next[index].photoUrl = dataUrl;
      setCreators(next);
      saveToStorage(next, institution);
    };
    reader.readAsDataURL(file);
  };

  const handleFieldChange = (
    index: 0 | 1,
    field: keyof CreatorProfile,
    value: string
  ) => {
    const next: [CreatorProfile, CreatorProfile] = [{ ...creators[0] }, { ...creators[1] }];
    (next[index] as unknown as Record<string, unknown>)[field] = value;
    setCreators(next);
    saveToStorage(next, institution);
  };

  const handleInstChange = (field: keyof InstitutionInfo, value: string) => {
    const next = { ...institution, [field]: value };
    setInstitution(next);
    saveToStorage(creators, next);
  };

  const handleResetDefaults = () => {
    soundFX.playTransition();
    setCreators(DEFAULT_CREATORS);
    setInstitution(DEFAULT_INSTITUTION);
    localStorage.removeItem(STORAGE_KEY_CREATORS);
    localStorage.removeItem(STORAGE_KEY_INST);
  };

  const renderPhantomAvatarSvg = (playerIndex: 0 | 1) => {
    const isP1 = playerIndex === 0;
    return (
      <svg
        viewBox="0 0 120 140"
        className="w-full h-full object-cover"
        xmlns="http://www.w3.org/2000/svg"
        role="img"
        aria-label={isP1 ? 'Avatar Player 1' : 'Avatar Player 2'}
      >
        <rect width="120" height="140" fill={isP1 ? '#E60012' : '#111111'} />
        {/* Diagonal Comic Stripes */}
        <path
          d="M-20 20 L140 -10 L140 35 L-20 65 Z"
          fill={isP1 ? '#111111' : '#E60012'}
          opacity="0.85"
        />
        <path
          d="M-20 95 L140 65 L140 100 L-20 130 Z"
          fill="#FFFFFF"
          opacity="0.18"
        />
        {/* Stylized Silhouette Shoulders & Head */}
        <path
          d="M15 140 C18 104 36 94 60 94 C84 94 102 104 105 140 Z"
          fill="#111111"
          stroke="#FFFFFF"
          strokeWidth="3"
        />
        <circle
          cx="60"
          cy="54"
          r="24"
          fill="#111111"
          stroke="#FFFFFF"
          strokeWidth="3"
        />
        {/* Stylized Domino Mask */}
        <path
          d="M36 48 L56 52 L60 46 L64 52 L84 48 L79 61 L64 59 L60 54 L56 59 L41 61 Z"
          fill="#FFFFFF"
          stroke="#E60012"
          strokeWidth="1.5"
        />
        <polygon points="44,53 53,54 49,57" fill="#E60012" />
        <polygon points="76,53 67,54 71,57" fill="#E60012" />
        {/* Player Number Stamp */}
        <text
          x="10"
          y="26"
          fill="#FFFFFF"
          fontFamily="Barlow Condensed, sans-serif"
          fontWeight="900"
          fontStyle="italic"
          fontSize="22"
        >
          {isP1 ? 'P1' : 'P2'}
        </text>
      </svg>
    );
  };

  return (
    <div className="space-y-10">
      {/* Top Action Bar: Co-Op Banner & Edit Toggle */}
      <div className="bg-[#18181B] border-2 border-white p-4 sm:p-5 p5-shadow-red flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 bg-[#E60012] text-white border-2 border-white flex items-center justify-center transform -rotate-3 p5-shadow-black shrink-0">
            <Swords className="w-6 h-6" />
          </div>
          <div>
            <div className="font-p5-mono text-xs text-[#E60012] uppercase tracking-widest">
              CONFIDANT TAG-TEAM // CO-OP MODE
            </div>
            <h3 className="font-p5-display text-2xl sm:text-3xl text-white tracking-wide">
              DUAL OPERATIVES: BACKEND RAG × FRONTEND PERSONA
            </h3>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <button
            type="button"
            onClick={() => {
              soundFX.playSelect();
              setActiveSynergy(prev => !prev);
            }}
            className={`px-4 py-2 font-p5-display text-base tracking-wider border-2 transition-all cursor-pointer transform -skew-x-6 ${
              activeSynergy
                ? 'bg-white text-[#111111] border-[#E60012] p5-shadow-red'
                : 'bg-[#111111] text-white border-white hover:bg-[#E60012]'
            }`}
          >
            <span className="inline-block transform skew-x-6 flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-[#E60012]" />
              <span>{activeSynergy ? 'HIDE CO-OP SYNERGY' : 'TRIGGER SHOWTIME SYNERGY'}</span>
            </span>
          </button>

          <button
            type="button"
            onClick={() => {
              soundFX.playSelect();
              setIsEditing(prev => !prev);
            }}
            className="p5-btn-primary px-4 py-2 text-base"
          >
            <span className="p5-unskew flex items-center gap-1.5">
              {isEditing ? (
                <>
                  <Check className="w-4 h-4" />
                  <span>SELESAI EDIT</span>
                </>
              ) : (
                <>
                  <Edit3 className="w-4 h-4" />
                  <span>EDIT IDENTITAS &amp; FOTO</span>
                </>
              )}
            </span>
          </button>

          {isEditing && (
            <button
              type="button"
              onClick={handleResetDefaults}
              className="px-3 py-2 bg-[#111111] text-zinc-300 hover:text-white border border-zinc-700 hover:border-white text-xs font-p5-mono flex items-center gap-1 cursor-pointer"
              title="Kembalikan ke Placeholder Awal"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          )}
        </div>
      </div>

      {/* Optional Co-Op Showtime Combination Banner */}
      {activeSynergy && (
        <div className="bg-[#E60012] p5-red-stripes border-4 border-white p-6 p5-shadow-lg-white relative overflow-hidden">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center text-center md:text-left">
            <div className="bg-[#111111] border-2 border-white p-4 transform -rotate-1">
              <div className="font-p5-mono text-xs text-[#E60012] font-bold">
                PLAYER 01 CONTRIBUTION
              </div>
              <div className="font-p5-display text-2xl text-white mt-0.5">
                PYTHON + CHROMADB + MINILM-L12
              </div>
              <p className="text-xs text-zinc-300 mt-1">
                Mengekstrak dokumen PDF SOP menjadi vektor 384-dimensi dan menyediakan API retrieval akurat.
              </p>
            </div>

            <div className="flex flex-col items-center justify-center">
              <div className="bg-white text-[#111111] border-4 border-[#111111] px-6 py-2 font-p5-display text-3xl sm:text-4xl tracking-wider transform -skew-x-12 p5-shadow-black">
                <span className="inline-block transform skew-x-12">SHOWTIME!!</span>
              </div>
              <span className="font-p5-mono text-xs text-white font-bold mt-2 uppercase tracking-widest">
                FULL-STACK RAG INTEGRATION
              </span>
            </div>

            <div className="bg-[#111111] border-2 border-white p-4 transform rotate-1">
              <div className="font-p5-mono text-xs text-[#E60012] font-bold">
                PLAYER 02 CONTRIBUTION
              </div>
              <div className="font-p5-display text-2xl text-white mt-0.5">
                PERSONA 5 UI + INTERACTIVE DEMO
              </div>
              <p className="text-xs text-zinc-300 mt-1">
                Menyajikan visualisasi pipeline interaktif dan terminal chatbot yang terhubung langsung ke backend.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* =====================================================================
          LEFT VS RIGHT CO-OP SPLIT CARDS (PLAYER 1 LEFT, PLAYER 2 RIGHT)
          ===================================================================== */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch relative">
        {creators.map((creator, idx) => {
          const isP1 = idx === 0;
          const playerIndex = idx as 0 | 1;
          const fileInputId = `creator-photo-upload-${creator.id}`;

          return (
            <div
              key={creator.id}
              className={`lg:col-span-6 border-2 p-6 sm:p-7 flex flex-col justify-between relative transition-transform ${
                isP1
                  ? 'bg-[#161616] border-white p5-shadow-lg-red'
                  : 'bg-[#1A1A1A] border-[#E60012] p5-shadow-lg-white'
              }`}
            >
              {/* Top Co-Op Wing Header */}
              <div>
                <div className="flex flex-wrap items-center justify-between gap-2 pb-4 mb-5 border-b-2 border-zinc-800">
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-3 py-1 font-p5-display text-lg tracking-wider border ${
                        isP1
                          ? 'bg-[#E60012] text-white border-white'
                          : 'bg-white text-[#111111] border-[#E60012]'
                      }`}
                    >
                      {creator.playerTag}
                    </span>
                  </div>
                  <span className="font-p5-mono text-xs text-zinc-400 font-bold">
                    {creator.arcana}
                  </span>
                </div>

                {/* Profile Body: Portrait + Identity Details */}
                <div className="grid grid-cols-1 sm:grid-cols-12 gap-5 items-start">
                  {/* Left Portrait Column (4 cols) */}
                  <div className="sm:col-span-4 flex flex-col items-center">
                    <div
                      className={`w-36 h-44 border-2 relative overflow-hidden group ${
                        isP1
                          ? 'border-white p5-shadow-red transform -rotate-2'
                          : 'border-[#E60012] p5-shadow-white transform rotate-2'
                      }`}
                    >
                      {creator.photoUrl ? (
                        <img
                          src={creator.photoUrl}
                          alt={creator.name}
                          referrerPolicy="no-referrer"
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        renderPhantomAvatarSvg(playerIndex)
                      )}

                      {/* Photo Upload Trigger */}
                      <label
                        htmlFor={fileInputId}
                        onClick={() => soundFX.playHover()}
                        className="absolute bottom-2 right-2 w-9 h-9 bg-[#E60012] hover:bg-white text-white hover:text-[#111111] border-2 border-white flex items-center justify-center cursor-pointer transition-colors shadow-md"
                        title={`Unggah / Ganti Foto ${isP1 ? 'Pembuat 1' : 'Pembuat 2'}`}
                      >
                        <Camera className="w-4 h-4" />
                      </label>
                      <input
                        id={fileInputId}
                        type="file"
                        accept="image/*"
                        onChange={e => handlePhotoUpload(playerIndex, e)}
                        className="hidden"
                      />
                    </div>

                    <div className="mt-3 text-center">
                      <span className="font-p5-display text-sm tracking-widest text-[#E60012] block">
                        CODENAME: {creator.codename}
                      </span>
                      <label
                        htmlFor={fileInputId}
                        className="text-[11px] font-p5-mono text-zinc-400 hover:text-white underline cursor-pointer mt-0.5 inline-block"
                      >
                        Klik ikon kamera untuk ganti foto
                      </label>
                    </div>
                  </div>

                  {/* Right Details Column (8 cols) */}
                  <div className="sm:col-span-8 space-y-3">
                    {isEditing ? (
                      <div className="space-y-2.5 bg-[#111111] border border-zinc-700 p-3.5">
                        <div>
                          <label className="text-[10px] font-p5-mono text-zinc-400 uppercase block">
                            Nama Lengkap Pembuat {idx + 1}
                          </label>
                          <input
                            type="text"
                            value={creator.name}
                            onChange={e => handleFieldChange(playerIndex, 'name', e.target.value)}
                            className="w-full bg-[#18181B] border border-zinc-600 px-2.5 py-1 text-sm text-white font-bold focus:border-[#E60012] focus:outline-none mt-0.5"
                          />
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          <div>
                            <label className="text-[10px] font-p5-mono text-zinc-400 uppercase block">
                              NIM / ID
                            </label>
                            <input
                              type="text"
                              value={creator.nim}
                              onChange={e => handleFieldChange(playerIndex, 'nim', e.target.value)}
                              className="w-full bg-[#18181B] border border-zinc-600 px-2.5 py-1 text-xs text-white font-p5-mono focus:border-[#E60012] focus:outline-none mt-0.5"
                            />
                          </div>
                          <div>
                            <label className="text-[10px] font-p5-mono text-zinc-400 uppercase block">
                              Codename P5
                            </label>
                            <input
                              type="text"
                              value={creator.codename}
                              onChange={e =>
                                handleFieldChange(playerIndex, 'codename', e.target.value)
                              }
                              className="w-full bg-[#18181B] border border-zinc-600 px-2.5 py-1 text-xs text-white font-p5-mono focus:border-[#E60012] focus:outline-none mt-0.5"
                            />
                          </div>
                        </div>
                        <div>
                          <label className="text-[10px] font-p5-mono text-zinc-400 uppercase block">
                            Universitas / Institusi
                          </label>
                          <input
                            type="text"
                            value={creator.university}
                            onChange={e =>
                              handleFieldChange(playerIndex, 'university', e.target.value)
                            }
                            className="w-full bg-[#18181B] border border-zinc-600 px-2.5 py-1 text-xs text-white focus:border-[#E60012] focus:outline-none mt-0.5"
                          />
                        </div>
                        <div>
                          <label className="text-[10px] font-p5-mono text-zinc-400 uppercase block">
                            Peran Spesialis Co-Op
                          </label>
                          <input
                            type="text"
                            value={creator.roleTitle}
                            onChange={e =>
                              handleFieldChange(playerIndex, 'roleTitle', e.target.value)
                            }
                            className="w-full bg-[#18181B] border border-zinc-600 px-2.5 py-1 text-xs text-white focus:border-[#E60012] focus:outline-none mt-0.5"
                          />
                        </div>
                      </div>
                    ) : (
                      <>
                        <div>
                          <h4 className="font-p5-display text-3xl sm:text-4xl text-white tracking-wide leading-none">
                            {creator.name}
                          </h4>
                          <div className="flex flex-wrap items-center gap-2 text-xs font-p5-mono text-zinc-300 mt-1.5">
                            <span className="text-[#E60012] font-bold">NIM: {creator.nim}</span>
                            <span>·</span>
                            <span>{creator.university}</span>
                          </div>
                          <div className="text-xs text-zinc-400 mt-0.5">{creator.major}</div>
                        </div>

                        <div className="bg-[#111111] border border-zinc-700 p-3">
                          <div className="text-[11px] font-p5-mono text-[#E60012] uppercase font-bold flex items-center gap-1.5">
                            {isP1 ? <Cpu className="w-3.5 h-3.5" /> : <Layout className="w-3.5 h-3.5" />}
                            <span>SPESIALISASI CO-OP: {creator.roleTitle}</span>
                          </div>
                          <p className="text-xs text-zinc-300 mt-1 leading-relaxed">
                            {creator.focusDescription}
                          </p>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </div>

              {/* Bottom Persona 5 Skill Loadout Grid */}
              <div className="mt-6 pt-4 border-t border-zinc-800">
                <div className="flex items-center justify-between text-xs font-p5-mono text-zinc-400 mb-2.5">
                  <span className="flex items-center gap-1.5 text-white font-bold">
                    <Shield className="w-3.5 h-3.5 text-[#E60012]" />
                    <span>EQUIPPED TECHNICAL SKILLS</span>
                  </span>
                  <span>PARTY SLOT 0{idx + 1}</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {creator.skills.map((sk, sIdx) => (
                    <div
                      key={sIdx}
                      className="bg-[#111111] border border-zinc-700 px-3 py-2 flex items-center justify-between gap-2 text-xs"
                    >
                      <span className="font-semibold text-zinc-200 truncate">{sk.label}</span>
                      <span className="font-p5-display text-sm text-[#E60012] shrink-0">
                        {sk.power}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* =====================================================================
          INSTITUTION & SUPERVISOR DOSSIER BAR
          ===================================================================== */}
      <div className="bg-[#161616] border-2 border-white p-5 sm:p-6 p5-shadow-red">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Col 1: Instansi */}
          <div className="space-y-1.5">
            <div className="flex items-center gap-2 text-xs font-p5-mono text-[#E60012] font-bold uppercase">
              <Building2 className="w-4 h-4" />
              <span>INSTANSI &amp; LOKASI PROYEK</span>
            </div>
            {isEditing ? (
              <div className="space-y-2 pt-1">
                <input
                  type="text"
                  value={institution.agency}
                  onChange={e => handleInstChange('agency', e.target.value)}
                  className="w-full bg-[#111111] border border-zinc-600 px-2.5 py-1 text-xs text-white"
                />
                <input
                  type="text"
                  value={institution.unit}
                  onChange={e => handleInstChange('unit', e.target.value)}
                  className="w-full bg-[#111111] border border-zinc-600 px-2.5 py-1 text-xs text-zinc-300"
                />
              </div>
            ) : (
              <>
                <div className="font-p5-display text-2xl text-white tracking-wide">
                  {institution.agency}
                </div>
                <p className="text-xs text-zinc-300 leading-relaxed">{institution.unit}</p>
              </>
            )}
          </div>

          {/* Col 2: Pembimbing */}
          <div className="space-y-1.5 md:border-l md:border-zinc-800 md:pl-6">
            <div className="flex items-center gap-2 text-xs font-p5-mono text-[#E60012] font-bold uppercase">
              <GraduationCap className="w-4 h-4" />
              <span>PEMBIMBING PELAKSANA</span>
            </div>
            {isEditing ? (
              <div className="space-y-2 pt-1">
                <input
                  type="text"
                  value={institution.fieldSupervisor}
                  onChange={e => handleInstChange('fieldSupervisor', e.target.value)}
                  placeholder="Pembimbing Instansi"
                  className="w-full bg-[#111111] border border-zinc-600 px-2.5 py-1 text-xs text-white"
                />
                <input
                  type="text"
                  value={institution.academicSupervisor}
                  onChange={e => handleInstChange('academicSupervisor', e.target.value)}
                  placeholder="Dosen Pembimbing"
                  className="w-full bg-[#111111] border border-zinc-600 px-2.5 py-1 text-xs text-zinc-300"
                />
              </div>
            ) : (
              <div className="space-y-1 text-xs text-zinc-300 pt-0.5">
                <div>
                  Pembimbing Lapangan: <strong className="text-white">{institution.fieldSupervisor}</strong>
                </div>
                <div>
                  Dosen Pembimbing: <strong className="text-white">{institution.academicSupervisor}</strong>
                </div>
              </div>
            )}
          </div>

          {/* Col 3: Periode */}
          <div className="space-y-1.5 md:border-l md:border-zinc-800 md:pl-6">
            <div className="flex items-center gap-2 text-xs font-p5-mono text-[#E60012] font-bold uppercase">
              <Calendar className="w-4 h-4" />
              <span>PERIODE &amp; STATUS SISTEM</span>
            </div>
            {isEditing ? (
              <div className="pt-1">
                <input
                  type="text"
                  value={institution.period}
                  onChange={e => handleInstChange('period', e.target.value)}
                  className="w-full bg-[#111111] border border-zinc-600 px-2.5 py-1 text-xs text-white"
                />
              </div>
            ) : (
              <>
                <div className="font-p5-display text-xl text-white tracking-wide">
                  {institution.period}
                </div>
                <p className="text-xs text-zinc-400">
                  Mode Co-Op: Kolaborasi Pengembangan Backend RAG &amp; Frontend Interaktif
                </p>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
