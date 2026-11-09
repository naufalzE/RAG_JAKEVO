import React, { useState, useEffect } from 'react';
import {
  FileText,
  ScanText,
  Sparkles,
  Scissors,
  Cpu,
  Database,
  MessageSquare,
  Filter,
  Binary,
  Search,
  Layers,
  Bot,
  CheckCircle2,
  Play,
  Square,
  ArrowRight
} from 'lucide-react';
import { ARCHITECTURE_STEPS, ArchitectureStep } from '../data/jakevoData';
import { soundFX } from '../utils/sound';

const STEP_ICONS: Record<string, React.ReactNode> = {
  'ing-1': <FileText className="w-5 h-5" />,
  'ing-2': <ScanText className="w-5 h-5" />,
  'ing-3': <Sparkles className="w-5 h-5" />,
  'ing-4': <Scissors className="w-5 h-5" />,
  'ing-5': <Cpu className="w-5 h-5" />,
  'ing-6': <Database className="w-5 h-5" />,
  'qry-1': <MessageSquare className="w-5 h-5" />,
  'qry-2': <Filter className="w-5 h-5" />,
  'qry-3': <Binary className="w-5 h-5" />,
  'qry-4': <Search className="w-5 h-5" />,
  'qry-5': <Layers className="w-5 h-5" />,
  'qry-6': <Bot className="w-5 h-5" />,
  'qry-7': <CheckCircle2 className="w-5 h-5" />
};

export const RagArchitectureVisualizer: React.FC = () => {
  const [activePipeline, setActivePipeline] = useState<'all' | 'ingestion' | 'query'>('all');
  const [selectedStep, setSelectedStep] = useState<ArchitectureStep>(ARCHITECTURE_STEPS[0]);
  const [isSimulating, setIsSimulating] = useState(false);

  const ingestionSteps = ARCHITECTURE_STEPS.filter(s => s.pipeline === 'ingestion');
  const querySteps = ARCHITECTURE_STEPS.filter(s => s.pipeline === 'query');

  useEffect(() => {
    if (!isSimulating) return;

    const currentPool =
      activePipeline === 'ingestion'
        ? ingestionSteps
        : activePipeline === 'query'
        ? querySteps
        : ARCHITECTURE_STEPS;

    const timer = setInterval(() => {
      setSelectedStep(prev => {
        const idx = currentPool.findIndex(item => item.id === prev.id);
        const nextIdx = (idx + 1) % currentPool.length;
        soundFX.playHover();
        return currentPool[nextIdx];
      });
    }, 1800);

    return () => clearInterval(timer);
  }, [isSimulating, activePipeline]);

  const handleSelectNode = (step: ArchitectureStep) => {
    setIsSimulating(false);
    soundFX.playSelect();
    setSelectedStep(step);
  };

  const toggleSimulation = () => {
    soundFX.playSelect();
    setIsSimulating(prev => !prev);
  };

  return (
    <div className="space-y-8">
      {/* Pipeline Filter & Auto-Walk Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-[#18181B] border-2 border-white p-4 p5-shadow-red">
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => {
              soundFX.playSelect();
              setActivePipeline('all');
            }}
            className={`px-4 py-2 font-p5-display text-base tracking-wider border transition-all cursor-pointer whitespace-nowrap shrink-0 transform -skew-x-6 ${
              activePipeline === 'all'
                ? 'bg-[#E60012] text-white border-white p5-shadow-white'
                : 'bg-[#111111] text-zinc-300 border-zinc-700 hover:border-white'
            }`}
          >
            <span className="inline-block transform skew-x-6">SEMUA ALUR (13 KOMPONEN)</span>
          </button>

          <button
            type="button"
            onClick={() => {
              soundFX.playSelect();
              setActivePipeline('ingestion');
              setSelectedStep(ingestionSteps[0]);
            }}
            className={`px-4 py-2 font-p5-display text-base tracking-wider border transition-all cursor-pointer whitespace-nowrap shrink-0 transform -skew-x-6 ${
              activePipeline === 'ingestion'
                ? 'bg-white text-[#111111] border-[#E60012] p5-shadow-red'
                : 'bg-[#111111] text-zinc-300 border-zinc-700 hover:border-white'
            }`}
          >
            <span className="inline-block transform skew-x-6">01. DOCUMENT INGESTION (6 TAHAP)</span>
          </button>

          <button
            type="button"
            onClick={() => {
              soundFX.playSelect();
              setActivePipeline('query');
              setSelectedStep(querySteps[0]);
            }}
            className={`px-4 py-2 font-p5-display text-base tracking-wider border transition-all cursor-pointer whitespace-nowrap shrink-0 transform -skew-x-6 ${
              activePipeline === 'query'
                ? 'bg-[#E60012] text-white border-white p5-shadow-white'
                : 'bg-[#111111] text-zinc-300 border-zinc-700 hover:border-white'
            }`}
          >
            <span className="inline-block transform skew-x-6">02. QUESTION PROCESSING (7 TAHAP)</span>
          </button>
        </div>

        <button
          type="button"
          onClick={toggleSimulation}
          className="p5-btn-secondary px-4 py-2 text-sm whitespace-nowrap shrink-0"
        >
          <span className="p5-unskew flex items-center gap-2">
            {isSimulating ? <Square className="w-4 h-4 text-[#E60012]" /> : <Play className="w-4 h-4 text-[#E60012]" />}
            <span>{isSimulating ? 'HENTIKAN ANIMASI ALUR' : 'JALANKAN SIMULASI ALUR'}</span>
          </span>
        </button>
      </div>

      {/* Interactive Diagram Grid + Detail Inspector Split */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* LEFT COLUMN (7 cols): Interactive Pipeline Nodes */}
        <div className="lg:col-span-7 space-y-8">
          {/* PIPELINE A: DOCUMENT INGESTION */}
          {(activePipeline === 'all' || activePipeline === 'ingestion') && (
            <div className="bg-[#161616] border-2 border-white p-5 sm:p-6 p5-shadow-white">
              <div className="flex flex-wrap items-center justify-between gap-2 pb-4 mb-5 border-b border-zinc-800">
                <div>
                  <span className="text-xs font-p5-mono text-zinc-400 uppercase tracking-widest">
                    OFFLINE INDEXING PIPELINE
                  </span>
                  <h3 className="font-p5-display text-2xl sm:text-3xl text-white tracking-wide mt-0.5">
                    PHASE A: DOCUMENT INGESTION
                  </h3>
                </div>
                <span className="text-xs text-zinc-300 font-semibold">
                  Klik setiap blok untuk melihat detail fungsi
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3.5">
                {ingestionSteps.map((step, index) => {
                  const isSelected = selectedStep.id === step.id;
                  return (
                    <button
                      key={step.id}
                      type="button"
                      onClick={() => handleSelectNode(step)}
                      className={`text-left p-4 border-2 transition-all relative group cursor-pointer ${
                        isSelected
                          ? 'bg-white text-[#111111] border-[#E60012] p5-shadow-red -translate-y-1'
                          : 'bg-[#111111] text-white border-zinc-700 hover:border-white'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span
                          className={`font-p5-display text-lg px-2 py-0.5 leading-none ${
                            isSelected ? 'bg-[#111111] text-white' : 'bg-zinc-800 text-zinc-200'
                          }`}
                        >
                          0{step.stepNumber}
                        </span>
                        <div className={isSelected ? 'text-[#E60012]' : 'text-zinc-400 group-hover:text-white'}>
                          {STEP_ICONS[step.id]}
                        </div>
                      </div>

                      <div className="font-p5-display text-xl tracking-wide leading-tight mb-1">
                        {step.title}
                      </div>
                      <div className={`text-xs line-clamp-1 ${isSelected ? 'text-zinc-700 font-medium' : 'text-zinc-400'}`}>
                        {step.subtitle}
                      </div>

                      {index < ingestionSteps.length - 1 && (
                        <ArrowRight
                          className={`w-3.5 h-3.5 absolute bottom-3 right-3 ${
                            isSelected ? 'text-[#E60012]' : 'text-zinc-600'
                          }`}
                        />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* PIPELINE B: QUESTION PROCESSING */}
          {(activePipeline === 'all' || activePipeline === 'query') && (
            <div className="bg-[#161616] border-2 border-[#E60012] p-5 sm:p-6 p5-shadow-red">
              <div className="flex flex-wrap items-center justify-between gap-2 pb-4 mb-5 border-b border-zinc-800">
                <div>
                  <span className="text-xs font-p5-mono text-[#E60012] uppercase tracking-widest">
                    ONLINE INFERENCE PIPELINE
                  </span>
                  <h3 className="font-p5-display text-2xl sm:text-3xl text-white tracking-wide mt-0.5">
                    PHASE B: QUESTION PROCESSING
                  </h3>
                </div>
                <span className="text-xs text-zinc-300 font-semibold">
                  Alur Real-Time Saat Pengguna Bertanya
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3.5">
                {querySteps.map((step, index) => {
                  const isSelected = selectedStep.id === step.id;
                  return (
                    <button
                      key={step.id}
                      type="button"
                      onClick={() => handleSelectNode(step)}
                      className={`text-left p-4 border-2 transition-all relative group cursor-pointer ${
                        step.stepNumber === 7 ? 'sm:col-span-2 md:col-span-3' : ''
                      } ${
                        isSelected
                          ? 'bg-[#E60012] text-white border-white p5-shadow-white -translate-y-1'
                          : 'bg-[#111111] text-white border-zinc-700 hover:border-[#E60012]'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span
                          className={`font-p5-display text-lg px-2 py-0.5 leading-none ${
                            isSelected ? 'bg-[#111111] text-white' : 'bg-[#E60012] text-white'
                          }`}
                        >
                          0{step.stepNumber}
                        </span>
                        <div className={isSelected ? 'text-white' : 'text-[#E60012]'}>
                          {STEP_ICONS[step.id]}
                        </div>
                      </div>

                      <div className="font-p5-display text-xl tracking-wide leading-tight mb-1">
                        {step.title}
                      </div>
                      <div className={`text-xs ${isSelected ? 'text-white/90 font-medium' : 'text-zinc-400'}`}>
                        {step.subtitle}
                      </div>

                      {index < querySteps.length - 1 && (
                        <ArrowRight
                          className={`w-3.5 h-3.5 absolute bottom-3 right-3 ${
                            isSelected ? 'text-white' : 'text-zinc-600'
                          }`}
                        />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* RIGHT COLUMN (5 cols): Active Component Detail Dossier */}
        <div className="lg:col-span-5 lg:sticky lg:top-24">
          <div className="bg-[#1A1A1A] border-2 border-white p-6 p5-shadow-lg-red relative overflow-hidden">
            {/* Diagonal Top Ribbon */}
            <div className="flex items-center justify-between gap-2 pb-4 mb-4 border-b-2 border-[#E60012]">
              <div>
                <div className="text-xs font-p5-mono uppercase tracking-widest text-[#E60012]">
                  {selectedStep.pipeline === 'ingestion'
                    ? `DOCUMENT INGESTION · STEP 0${selectedStep.stepNumber}/06`
                    : `QUESTION PROCESSING · STEP 0${selectedStep.stepNumber}/07`}
                </div>
                <h4 className="font-p5-display text-3xl sm:text-4xl text-white tracking-wide mt-1">
                  {selectedStep.title}
                </h4>
                <p className="text-sm text-zinc-400 font-medium">{selectedStep.subtitle}</p>
              </div>
              <div className="w-12 h-12 bg-[#E60012] text-white border-2 border-white flex items-center justify-center shrink-0 transform -rotate-6 p5-shadow-black">
                {STEP_ICONS[selectedStep.id]}
              </div>
            </div>

            {/* Detailed Explanation */}
            <div className="space-y-4">
              <div>
                <h5 className="font-p5-display text-lg text-white tracking-wider mb-1">
                  FUNGSI KOMPONEN
                </h5>
                <p className="text-sm text-zinc-200 leading-relaxed">{selectedStep.description}</p>
              </div>

              <div className="bg-[#111111] border border-zinc-700 p-3.5">
                <h5 className="font-p5-display text-base text-[#E60012] tracking-wider mb-1">
                  PERAN DALAM ARSITEKTUR RAG JAKEVO
                </h5>
                <p className="text-xs sm:text-sm text-zinc-300 leading-relaxed">
                  {selectedStep.technicalRole}
                </p>
              </div>

              {/* Input -> Output Flow */}
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-[#111111] border border-zinc-800 p-3">
                  <span className="text-[11px] font-p5-mono text-zinc-400 uppercase block">
                    INPUT STAGE
                  </span>
                  <span className="text-xs sm:text-sm font-bold text-white mt-0.5 block">
                    {selectedStep.inputLabel}
                  </span>
                </div>
                <div className="bg-[#111111] border border-[#E60012] p-3">
                  <span className="text-[11px] font-p5-mono text-[#E60012] uppercase block">
                    OUTPUT STAGE
                  </span>
                  <span className="text-xs sm:text-sm font-bold text-white mt-0.5 block">
                    {selectedStep.outputLabel}
                  </span>
                </div>
              </div>

              {/* Sample Payload Preview */}
              <div className="bg-[#111111] border border-zinc-700 p-3.5">
                <span className="text-[11px] font-p5-mono text-zinc-400 uppercase block mb-1.5">
                  CONTOH REPRESENTASI DATA PADA TAHAP INI:
                </span>
                <pre className="font-p5-mono text-xs text-zinc-200 whitespace-pre-wrap break-words leading-relaxed">
                  {selectedStep.sampleData}
                </pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
