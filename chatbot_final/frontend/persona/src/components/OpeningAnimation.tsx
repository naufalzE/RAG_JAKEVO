import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Sparkles, Users, Database, FastForward, Play } from 'lucide-react';
import { soundFX } from '../utils/sound';

interface OpeningAnimationProps {
  isVisible: boolean;
  onComplete: () => void;
}

export const OpeningAnimation: React.FC<OpeningAnimationProps> = ({
  isVisible,
  onComplete
}) => {
  const [stage, setStage] = useState<0 | 1 | 2>(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!isVisible) {
      setStage(0);
      setProgress(0);
      return;
    }

    // Progress bar counter
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 2;
      });
    }, 65);

    // Stage transitions
    const t1 = setTimeout(() => {
      soundFX.playHover();
      setStage(1);
    }, 1100);

    const t2 = setTimeout(() => {
      soundFX.playTransition();
      setStage(2);
    }, 2300);

    return () => {
      clearInterval(interval);
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, [isVisible]);

  const handleEnter = () => {
    soundFX.playSelect();
    onComplete();
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          key="p5-cinematic-intro"
          initial={{ opacity: 1 }}
          exit={{
            opacity: 0,
            scale: 1.06,
            transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] }
          }}
          className="fixed inset-0 z-50 bg-[#111111] flex flex-col justify-between overflow-hidden select-none"
        >
          {/* BACKGROUND DIAGONAL SLASHES & HALFTONE */}
          <div className="absolute inset-0 p5-halftone-bg opacity-70 pointer-events-none" />

          {/* Animated Top-Left to Bottom-Right Crimson Slash */}
          <motion.div
            initial={{ x: '-100%', skewY: -12 }}
            animate={{ x: '0%', skewY: -12 }}
            transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
            className="absolute top-1/4 -left-20 -right-20 h-44 sm:h-60 bg-[#E60012] border-y-4 border-white pointer-events-none"
          />

          {/* Secondary Black & White Counter Slash */}
          <motion.div
            initial={{ x: '100%', skewY: 8 }}
            animate={{ x: '0%', skewY: 8 }}
            transition={{ duration: 0.6, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
            className="absolute bottom-1/4 -left-20 -right-20 h-20 sm:h-28 bg-white border-y-4 border-[#111111] pointer-events-none"
          />

          {/* TOP HUD BAR */}
          <div className="relative z-20 max-w-7xl w-full mx-auto px-6 pt-6 flex items-center justify-between">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-[#111111] border-2 border-white px-4 py-1.5 p5-shadow-red transform -skew-x-6"
            >
              <span className="inline-block transform skew-x-6 font-p5-mono text-xs text-white font-bold tracking-widest">
                SYSTEM BOOT // RAG PROTOCOL
              </span>
            </motion.div>

            <button
              type="button"
              onClick={handleEnter}
              className="px-4 py-1.5 bg-[#111111] hover:bg-white text-white hover:text-[#111111] border-2 border-white font-p5-display text-base tracking-wider transition-colors flex items-center gap-1.5 cursor-pointer p5-shadow-red"
            >
              <span>SKIP INTRO</span>
              <FastForward className="w-4 h-4" />
            </button>
          </div>

          {/* CENTER STAGE: MULTI-PHASE PERSONA 5 OPENING */}
          <div className="relative z-20 flex-1 flex items-center justify-center px-4">
            <div className="max-w-3xl w-full">
              {/* STAGE 0: INITIALIZING KNOWLEDGE BASE */}
              {stage === 0 && (
                <motion.div
                  key="stage-0"
                  initial={{ scale: 0.8, opacity: 0, rotate: -4 }}
                  animate={{ scale: 1, opacity: 1, rotate: -2 }}
                  exit={{ scale: 1.1, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="bg-[#111111] border-4 border-white p-8 sm:p-10 p5-shadow-lg-white text-center mx-auto max-w-xl"
                >
                  <div className="inline-flex items-center gap-2 bg-[#E60012] text-white px-3 py-1 font-p5-mono text-xs font-bold mb-3 border border-white">
                    <Database className="w-4 h-4 animate-spin" />
                    <span>PHASE 01 // VECTOR INDEXING</span>
                  </div>
                  <h2 className="font-p5-display text-5xl sm:text-6xl text-white tracking-wide leading-none">
                    LOADING CHROMADB ARCHIVE...
                  </h2>
                  <p className="font-p5-mono text-xs sm:text-sm text-zinc-300 mt-3">
                    paraphrase-multilingual-MiniLM-L12-v2 · 384 Dimensions
                  </p>
                </motion.div>
              )}

              {/* STAGE 1: CO-OP 2 PLAYERS DETECTED */}
              {stage === 1 && (
                <motion.div
                  key="stage-1"
                  initial={{ x: 80, opacity: 0, skewX: -8 }}
                  animate={{ x: 0, opacity: 1, skewX: -4 }}
                  exit={{ x: -80, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="bg-[#111111] border-4 border-white p-8 sm:p-10 p5-shadow-lg-red text-center mx-auto max-w-2xl"
                >
                  <div className="inline-flex items-center gap-2 bg-white text-[#111111] px-3 py-1 font-p5-mono text-xs font-bold mb-3 border-2 border-[#E60012]">
                    <Users className="w-4 h-4 text-[#E60012]" />
                    <span>PHASE 02 // CO-OP TAG TEAM</span>
                  </div>
                  <h2 className="font-p5-display text-5xl sm:text-6xl text-[#E60012] tracking-wide leading-none">
                    2 CREATORS LINKED IN CO-OP MODE!
                  </h2>
                  <p className="font-p5-display text-2xl text-white tracking-wider mt-2">
                    AI RAG ENGINEER × FRONTEND SHOWCASE ARCHITECT
                  </p>
                </motion.div>
              )}

              {/* STAGE 2: MAIN CALLING CARD & START TRIGGER */}
              {stage === 2 && (
                <motion.div
                  key="stage-2"
                  initial={{ scale: 0.75, opacity: 0, rotate: -3 }}
                  animate={{ scale: 1, opacity: 1, rotate: -1 }}
                  transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                  className="bg-[#111111] border-4 border-white p-7 sm:p-10 p5-shadow-lg-white text-center relative"
                >
                  {/* Corner Calling Card Badge */}
                  <div className="absolute -top-5 left-6 bg-[#E60012] text-white border-2 border-white px-4 py-1 font-p5-display text-lg tracking-wider transform -rotate-3 p5-shadow-black">
                    CALLING CARD // PRODUCT SHOWCASE
                  </div>

                  <div className="flex items-center justify-center gap-2 text-xs font-p5-mono text-zinc-300 mb-2 pt-2">
                    <Sparkles className="w-4 h-4 text-[#E60012]" />
                    <span>RETRIEVAL-AUGMENTED GENERATION SYSTEM</span>
                  </div>

                  <h1 className="font-p5-display text-6xl sm:text-8xl text-white tracking-tight leading-none">
                    JAKEVO
                  </h1>

                  <div className="inline-block bg-[#E60012] text-white font-p5-display text-2xl sm:text-3xl px-5 py-1 border-2 border-white transform -skew-x-6 mt-3">
                    <span className="inline-block transform skew-x-6">
                      INFORMATION IS YOUR POWER
                    </span>
                  </div>

                  <p className="text-sm sm:text-base text-zinc-300 max-w-lg mx-auto mt-4 leading-relaxed">
                    Asisten Cerdas Berbasis Dokumen untuk Informasi Persyaratan &amp; Prosedur Pelayanan Administrasi.
                  </p>

                  <div className="mt-7 flex flex-col sm:flex-row items-center justify-center gap-4">
                    <button
                      type="button"
                      onClick={handleEnter}
                      className="p5-btn-primary px-9 py-4 text-2xl sm:text-3xl animate-pulse"
                    >
                      <span className="p5-unskew flex items-center gap-2.5">
                        <Play className="w-6 h-6 fill-current" />
                        <span>MASUK KE WEBSITE JAKEVO</span>
                      </span>
                    </button>
                  </div>
                </motion.div>
              )}
            </div>
          </div>

          {/* BOTTOM LOADING BAR HUD */}
          <div className="relative z-20 max-w-7xl w-full mx-auto px-6 pb-8">
            <div className="bg-[#111111] border-2 border-white p-4 p5-shadow-red">
              <div className="flex items-center justify-between text-xs font-p5-mono mb-2">
                <span className="text-white font-bold">
                  {progress < 100
                    ? 'SYNCHRONIZING RAG PIPELINE & CO-OP DATA...'
                    : 'SYSTEM READY — CLICK "MASUK KE WEBSITE JAKEVO"'}
                </span>
                <span className="text-[#E60012] font-bold">{progress}%</span>
              </div>
              <div className="w-full h-3 bg-zinc-900 border border-zinc-700 overflow-hidden">
                <div
                  className="h-full bg-[#E60012] transition-all duration-100"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
