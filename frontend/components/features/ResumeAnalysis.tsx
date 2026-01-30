/**
 * Resume Analysis Display Component
 */
'use client';

import { motion } from 'framer-motion';
import { TickCircle, InfoCircle, Award, Briefcase, TrendUp } from 'iconsax-react';
import { ResumeAnalysis as ResumeAnalysisType } from '@/lib/types';

interface ResumeAnalysisProps {
  analysis: ResumeAnalysisType;
  onContinue: () => void;
}

export const ResumeAnalysis = ({ analysis, onContinue }: ResumeAnalysisProps) => {
  const getScoreColor = (score: number) => {
    return 'from-white/30 to-white/10';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 8) return 'Excellent';
    if (score >= 6) return 'Good';
    if (score >= 4) return 'Fair';
    return 'Needs Work';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-4xl mx-auto space-y-6"
    >
      {/* Score Card */}
      <div className="glass-card p-8 text-center">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', delay: 0.2 }}
          className="inline-block"
        >
          <div className={`w-32 h-32 rounded-full bg-linear-to-br ${getScoreColor(analysis.score)} p-1 mx-auto mb-4 glow`}>
            <div className="w-full h-full rounded-full glass-card backdrop-blur-xl flex items-center justify-center">
              <div className="text-center">
                <div className="text-4xl font-bold">{analysis.score}</div>
                <div className="text-sm text-white/60">/ 10</div>
              </div>
            </div>
          </div>
        </motion.div>

        <h2 className="text-2xl font-semibold mb-2">
          {getScoreLabel(analysis.score)} Resume
        </h2>
        <p className="text-white/60">
          Your resume has been analyzed by our AI
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Strengths */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg glass-card">
              <TickCircle size={20} variant="Bold" color="#ffffff" />
            </div>
            <h3 className="text-lg font-semibold">Strengths</h3>
          </div>
          <ul className="space-y-2">
            {analysis.strengths.map((strength, index) => (
              <motion.li
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + index * 0.1 }}
                className="flex items-start gap-2 text-sm text-white/80"
              >
                <span className="text-white mt-0.5">•</span>
                <span>{strength}</span>
              </motion.li>
            ))}
          </ul>
        </motion.div>

        {/* Improvements */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg glass-card">
              <TrendUp size={20} variant="Bold" color="#ffffff" />
            </div>
            <h3 className="text-lg font-semibold">Areas to Improve</h3>
          </div>
          <ul className="space-y-2">
            {analysis.improvements.map((improvement, index) => (
              <motion.li
                key={index}
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + index * 0.1 }}
                className="flex items-start gap-2 text-sm text-white/80"
              >
                <span className="text-white/60 mt-0.5">•</span>
                <span>{improvement}</span>
              </motion.li>
            ))}
          </ul>
        </motion.div>
      </div>

      {/* Skills & Experience */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Key Skills */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-card p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg glass-card">
              <Award size={20} variant="Bold" color="#ffffff" />
            </div>
            <h3 className="text-lg font-semibold">Key Skills</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {analysis.key_skills.map((skill, index) => (
              <motion.span
                key={index}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.6 + index * 0.05 }}
                className="px-3 py-1.5 rounded-lg glass-card text-sm font-medium"
              >
                {skill}
              </motion.span>
            ))}
          </div>
        </motion.div>

        {/* Experience */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-card p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg glass-card">
              <Briefcase size={20} variant="Bold" color="#ffffff" />
            </div>
            <h3 className="text-lg font-semibold">Experience</h3>
          </div>
          <div className="text-3xl font-bold gradient-text">
            {analysis.experience_years}
          </div>
          <p className="text-sm text-white/60 mt-1">Years of experience</p>
        </motion.div>
      </div>

      {/* Continue Button */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.7 }}
        className="flex justify-center pt-4"
      >
        <button
          onClick={onContinue}
          className="glass-button px-8 py-4 text-lg font-semibold hover:scale-105 transition-transform"
        >
          Find Matching Jobs →
        </button>
      </motion.div>
    </motion.div>
  );
};
