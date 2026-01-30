/**
 * Main Application Page
 */
'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MagicStar, ArrowLeft } from 'iconsax-react';
import { FileUpload } from '@/components/features/FileUpload';
import { ResumeAnalysis } from '@/components/features/ResumeAnalysis';
import { JobMatches } from '@/components/features/JobMatches';
import { AuroraBackground } from '@/components/ui/AuroraBackground';
import { useResumeProcessor } from '@/lib/hooks/useResumeProcessor';
import { AppStep } from '@/lib/types';
import { CardShimmer } from '@/components/ui/Shimmer';

export default function Home() {
  const [currentStep, setCurrentStep] = useState<AppStep>('upload');
  const {
    isProcessing,
    isMatching,
    error,
    analysis,
    matches,
    processResume,
    matchJobs,
    reset,
  } = useResumeProcessor();

  const handleFileSelect = async (file: File) => {
    try {
      await processResume(file);
      setCurrentStep('analysis');
    } catch (err) {
      console.error('Error processing resume:', err);
    }
  };

  const handleContinueToMatches = async () => {
    if (!analysis) return;

    try {
      await matchJobs(analysis.cleaned_for_matching, {
        threshold: 0.57,
        maxResults: 20,
      });
      setCurrentStep('matches');
    } catch (err) {
      console.error('Error matching jobs:', err);
    }
  };

  const handleReset = () => {
    reset();
    setCurrentStep('upload');
  };

  return (
    <main className="relative min-h-screen p-4 md:p-8">
      {/* Aurora Background */}
      <AuroraBackground />

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-7xl mx-auto mb-12"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl glass-card icon-glow">
                <MagicStar size={24} variant="Bold" color="#ffffff" />
              </div>
              <div>
                <h1 className="text-2xl md:text-3xl font-bold gradient-text">
                  JobMatch AI
                </h1>
                <p className="text-sm text-white/60">
                  AI-Powered Resume-Job Matching
                </p>
              </div>
            </div>

            {currentStep !== 'upload' && (
              <motion.button
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                onClick={handleReset}
                className="glass-button px-4 py-2 flex items-center gap-2 text-sm"
              >
                <ArrowLeft size={16} color="#ffffff" />
                Start Over
              </motion.button>
            )}
          </div>

          {/* Progress Steps */}
          <div className="mt-8 flex items-center justify-center gap-2">
            {(['upload', 'analysis', 'matches'] as AppStep[]).map((step, index) => (
              <div key={step} className="flex items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-all ${
                    currentStep === step
                      ? 'glass-card glow scale-110'
                      : index < ['upload', 'analysis', 'matches'].indexOf(currentStep)
                      ? 'bg-white/20'
                      : 'bg-white/5'
                  }`}
                >
                  {index + 1}
                </div>
                {index < 2 && (
                  <div
                    className={`w-12 md:w-24 h-0.5 transition-all ${
                      index < ['upload', 'analysis', 'matches'].indexOf(currentStep)
                        ? 'bg-white/20'
                        : 'bg-white/5'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </motion.header>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto">
          <AnimatePresence mode="wait">
            {/* Upload Step */}
            {currentStep === 'upload' && (
              <motion.div
                key="upload"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <FileUpload
                  onFileSelect={handleFileSelect}
                  isProcessing={isProcessing}
                />

                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-4 max-w-2xl mx-auto p-4 rounded-lg glass-card border-red-500/50 text-red-400 text-center"
                  >
                    {error}
                  </motion.div>
                )}
              </motion.div>
            )}

            {/* Analysis Step */}
            {currentStep === 'analysis' && (
              <motion.div
                key="analysis"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                {isMatching ? (
                  <div className="max-w-4xl mx-auto space-y-4">
                    <CardShimmer />
                    <div className="text-center">
                      <p className="text-white/60">
                        Finding matching jobs...
                      </p>
                    </div>
                  </div>
                ) : analysis ? (
                  <ResumeAnalysis
                    analysis={analysis}
                    onContinue={handleContinueToMatches}
                  />
                ) : null}
              </motion.div>
            )}

            {/* Matches Step */}
            {currentStep === 'matches' && (
              <motion.div
                key="matches"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                {matches && <JobMatches matches={matches} isLoading={isMatching} />}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="max-w-7xl mx-auto mt-16 text-center text-sm text-white/40"
        >

        </motion.footer>
      </div>
    </main>
  );
}
