import React, { useState } from 'react';
import {
  Target,
  BarChart3,
  Award,
  CheckSquare,
  AlertTriangle,
  Sliders,
  CheckCircle2,
  XCircle
} from 'lucide-react';
import {
  EVALUATION_METRICS,
  RETRIEVAL_ERROR_CATEGORIES,
  EvaluationMetricItem
} from '../data/jakevoData';
import { soundFX } from '../utils/sound';

const METRIC_ICONS: Record<string, React.ReactNode> = {
  'eval-hit-k': <Target className="w-5 h-5" />,
  'eval-recall-k': <BarChart3 className="w-5 h-5" />,
  'eval-mrr': <Award className="w-5 h-5" />,
  'eval-accuracy': <CheckSquare className="w-5 h-5" />
};

export const EvaluationSection: React.FC = () => {
  const [selectedMetric, setSelectedMetric] = useState<EvaluationMetricItem>(EVALUATION_METRICS[0]);
  // Interactive simulator state: rank position of relevant document (1, 2, 3, or 0 for Miss)
  const [simulatedRank, setSimulatedRank] = useState<1 | 2 | 3 | 0>(1);

  const simulatedHitAt3 = simulatedRank > 0 ? '1 (HIT)' : '0 (MISS)';
  const simulatedMrr =
    simulatedRank === 1
      ? '1 / 1 = 1.000'
      : simulatedRank === 2
      ? '1 / 2 = 0.500'
      : simulatedRank === 3
      ? '1 / 3 = 0.333'
      : '0.000 (Tidak ditemukan di Top-3)';
  const simulatedRecallAt3 =
    simulatedRank > 0
      ? '1 / 1 = 1.00 (100% dari 1 target dokumen relevan)'
      : '0 / 1 = 0.00 (0% dokumen relevan terambil)';

  return (
    <div className="space-y-12">
      {/* Notice Banner: Placeholder Honesty */}
      <div className="bg-[#18181B] border-2 border-white p-4 sm:p-5 p5-shadow-red flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="font-p5-display text-lg text-[#E60012] tracking-wider">
            METODOLOGI EVALUASI KUALITAS RETRIEVAL
          </div>
          <p className="text-xs sm:text-sm text-zinc-300 leading-relaxed">
            Bagian ini menjelaskan metrik standar yang digunakan untuk menguji performa pencarian dokumen pada sistem RAG JAKEVO. Nilai hasil evaluasi aktual ditampilkan sebagai placeholder hingga pengujian dataset final selesai dilakukan.
          </p>
        </div>
        <div className="px-3.5 py-2 bg-[#111111] border border-zinc-700 font-p5-mono text-xs text-zinc-300 whitespace-nowrap shrink-0">
          STATUS DATA: PLACEHOLDER (BELUM DIKLAIM)
        </div>
      </div>

      {/* 4 Evaluation Metric Selector Cards + Interactive Explanation Split */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left: 4 Metric Cards */}
        <div className="lg:col-span-5 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-4">
          {EVALUATION_METRICS.map((metric, idx) => {
            const isSelected = selectedMetric.id === metric.id;
            return (
              <button
                key={metric.id}
                type="button"
                onClick={() => {
                  soundFX.playSelect();
                  setSelectedMetric(metric);
                }}
                className={`text-left p-5 border-2 transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-[#E60012] text-white border-white p5-shadow-white -translate-y-0.5'
                    : 'bg-[#161616] text-white border-zinc-700 hover:border-white'
                }`}
              >
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="font-p5-mono text-xs uppercase tracking-widest opacity-90">
                    0{idx + 1}. {metric.shortCode}
                  </span>
                  <div className={isSelected ? 'text-white' : 'text-[#E60012]'}>
                    {METRIC_ICONS[metric.id]}
                  </div>
                </div>
                <h3 className="font-p5-display text-2xl tracking-wide leading-tight mb-1.5">
                  {metric.name}
                </h3>
                <p className={`text-xs leading-relaxed ${isSelected ? 'text-white/90' : 'text-zinc-400'}`}>
                  {metric.description}
                </p>
                <div className="mt-3 pt-2.5 border-t border-white/20 flex items-center justify-between text-xs font-p5-mono">
                  <span>Skor Pengujian:</span>
                  <span className="font-bold">{metric.placeholderValue}</span>
                </div>
              </button>
            );
          })}
        </div>

        {/* Right: Detailed Formula & Interactive Rank Simulator */}
        <div className="lg:col-span-7 space-y-6">
          {/* Selected Metric Breakdown Card */}
          <div className="bg-[#161616] border-2 border-white p-6 p5-shadow-red space-y-5">
            <div className="flex flex-wrap items-center justify-between gap-2 pb-4 border-b border-zinc-800">
              <div>
                <span className="text-xs font-p5-mono text-[#E60012] uppercase tracking-widest">
                  SPESIFIKASI METRIK EVALUASI
                </span>
                <h4 className="font-p5-display text-3xl sm:text-4xl text-white tracking-wide mt-0.5">
                  {selectedMetric.name}
                </h4>
              </div>
              <div className="bg-[#111111] border border-zinc-700 px-3 py-1.5 font-p5-mono text-xs text-zinc-300">
                Hasil Aktual: {selectedMetric.placeholderValue}
              </div>
            </div>

            {/* Mathematical Formula */}
            <div className="bg-[#111111] border border-zinc-700 p-4">
              <span className="text-xs font-p5-mono text-zinc-400 uppercase block mb-1">
                FORMULASI MATEMATIS:
              </span>
              <div className="font-p5-mono text-sm sm:text-base text-white font-bold">
                {selectedMetric.formula}
              </div>
            </div>

            <div className="space-y-2">
              <h5 className="font-p5-display text-xl text-white tracking-wide">
                CARA PENILAIAN SISTEM
              </h5>
              <p className="text-sm text-zinc-300 leading-relaxed">{selectedMetric.howItWorks}</p>
            </div>

            {/* Visual Rank Inspection */}
            <div className="bg-[#111111] border border-zinc-800 p-4 space-y-3">
              <div className="text-xs font-p5-mono text-zinc-400">
                ILUSTRASI KONSEP PADA KUERI: <strong className="text-white">"{selectedMetric.visualExample.query}"</strong>
              </div>

              <div className="space-y-2">
                {selectedMetric.visualExample.topK.map(item => (
                  <div
                    key={item.rank}
                    className={`flex items-center justify-between gap-3 p-2.5 border text-xs ${
                      item.isRelevant
                        ? 'bg-[#E60012]/15 border-[#E60012] text-white'
                        : 'bg-[#18181B] border-zinc-800 text-zinc-400'
                    }`}
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <span className="font-p5-display text-base px-2 py-0.5 bg-[#111111] border border-zinc-700 text-white shrink-0">
                        RANK #{item.rank}
                      </span>
                      <span className="font-p5-mono truncate">{item.docId}</span>
                    </div>
                    <span className="font-p5-mono text-xs shrink-0 font-semibold">
                      {item.isRelevant ? '✓ RELEVAN' : 'NON-TARGET'}
                    </span>
                  </div>
                ))}
              </div>

              <p className="text-xs text-zinc-300 pt-1">{selectedMetric.visualExample.calculationNote}</p>
            </div>
          </div>

          {/* Interactive Top-K Rank Calculator (Allows user to experiment with how Hit@K, Recall@K, and MRR work) */}
          <div className="bg-[#1A1A1A] border-2 border-[#E60012] p-6 p5-shadow-white space-y-4">
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <Sliders className="w-5 h-5 text-[#E60012]" />
                <h4 className="font-p5-display text-2xl text-white tracking-wide">
                  SIMULATOR INTERAKTIF PERHITUNGAN METRIK (TOP-K = 3)
                </h4>
              </div>
              <span className="text-xs font-p5-mono text-zinc-400">Simulasi Edukatif</span>
            </div>

            <p className="text-xs sm:text-sm text-zinc-300">
              Klik posisi peringkat tempat dokumen SOP yang relevan muncul untuk melihat bagaimana <strong>Hit@3</strong>, <strong>Recall@3</strong>, dan <strong>MRR</strong> dihitung pada satu kueri uji:
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
              {([1, 2, 3, 0] as const).map(pos => (
                <button
                  key={pos}
                  type="button"
                  onClick={() => {
                    soundFX.playSelect();
                    setSimulatedRank(pos);
                  }}
                  className={`p-3 border-2 font-p5-display text-lg tracking-wider transition-all cursor-pointer ${
                    simulatedRank === pos
                      ? 'bg-white text-[#111111] border-[#E60012] p5-shadow-red'
                      : 'bg-[#111111] text-white border-zinc-700 hover:border-white'
                  }`}
                >
                  {pos === 0 ? 'TIDAK MUNCUL (MISS)' : `MUNCUL DI RANK #${pos}`}
                </button>
              ))}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
              <div className="bg-[#111111] border border-zinc-700 p-3">
                <span className="text-[11px] font-p5-mono text-zinc-400 block">SIMULASI HIT@3</span>
                <div className="font-p5-mono text-sm font-bold text-white mt-1 flex items-center gap-1.5">
                  {simulatedRank > 0 ? (
                    <CheckCircle2 className="w-4 h-4 text-[#E60012]" />
                  ) : (
                    <XCircle className="w-4 h-4 text-zinc-500" />
                  )}
                  <span>{simulatedHitAt3}</span>
                </div>
              </div>

              <div className="bg-[#111111] border border-zinc-700 p-3">
                <span className="text-[11px] font-p5-mono text-zinc-400 block">SIMULASI MRR (1/RANK)</span>
                <div className="font-p5-mono text-sm font-bold text-white mt-1">{simulatedMrr}</div>
              </div>

              <div className="bg-[#111111] border border-zinc-700 p-3">
                <span className="text-[11px] font-p5-mono text-zinc-400 block">SIMULASI RECALL@3</span>
                <div className="font-p5-mono text-xs font-bold text-white mt-1">{simulatedRecallAt3}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Retrieval Error Analysis Breakdown */}
      <div className="bg-[#161616] border-2 border-white p-6 sm:p-8 p5-shadow-red">
        <div className="flex flex-wrap items-center justify-between gap-2 pb-4 mb-6 border-b border-zinc-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#E60012] text-white border-2 border-white flex items-center justify-center transform -rotate-3">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-p5-display text-2xl sm:text-3xl text-white tracking-wide">
                ANALISIS KESALAHAN RETRIEVAL (RETRIEVAL ERROR ANALYSIS)
              </h3>
              <p className="text-xs sm:text-sm text-zinc-400">
                Identifikasi potensi kegagalan pengambilan konteks dokumen dan strategi mitigasinya
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {RETRIEVAL_ERROR_CATEGORIES.map((err, index) => (
            <div
              key={err.id}
              className="bg-[#111111] border border-zinc-700 p-5 flex flex-col justify-between space-y-4"
            >
              <div className="space-y-2">
                <div className="font-p5-mono text-xs text-[#E60012] font-bold">
                  KATEGORI ANALISIS 0{index + 1}
                </div>
                <h4 className="font-p5-display text-2xl text-white tracking-wide">{err.title}</h4>
                <p className="text-xs sm:text-sm text-zinc-300 leading-relaxed">{err.description}</p>
              </div>

              <div className="pt-3 border-t border-zinc-800">
                <span className="text-[11px] font-p5-mono text-zinc-400 uppercase block mb-1">
                  PENDEKATAN EVALUASI &amp; PERBAIKAN:
                </span>
                <p className="text-xs text-white font-medium leading-relaxed">{err.mitigation}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
