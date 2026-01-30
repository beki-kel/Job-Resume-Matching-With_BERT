/**
 * Job Matches Display Component
 */
'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ExportSquare, Location, Calendar, TrendUp, Filter } from 'iconsax-react';
import { JobMatch, MatchResponse } from '@/lib/types';
import { formatScore, getScoreColor, getScoreLabel, formatDate, truncateText } from '@/lib/utils';
import { JobCardShimmer } from '../ui/Shimmer';

interface JobMatchesProps {
  matches: MatchResponse;
  isLoading?: boolean;
}

export const JobMatches = ({ matches, isLoading }: JobMatchesProps) => {
  const [filter, setFilter] = useState<'all' | 'excellent' | 'good'>('all');
  const [expandedJob, setExpandedJob] = useState<number | null>(null);

  const filteredMatches = matches.matches.filter((match) => {
    if (filter === 'excellent') return match.score >= 0.7;
    if (filter === 'good') return match.score >= 0.57 && match.score < 0.7;
    return true;
  });

  if (isLoading) {
    return (
      <div className="w-full max-w-6xl mx-auto space-y-4">
        <JobCardShimmer />
        <JobCardShimmer />
        <JobCardShimmer />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="w-full max-w-6xl mx-auto space-y-6"
    >
      {/* Header */}
      <div className="glass-card p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold mb-2">
              Found {matches.total_matches} Matching Jobs
            </h2>
            <p className="text-white/60 text-sm">
              Analyzed {matches.total_jobs_scraped} jobs in {matches.processing_time_seconds}s
            </p>
          </div>

          {/* Filter */}
          <div className="flex gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                filter === 'all'
                  ? 'glass-card glow'
                  : 'bg-white/5 border border-white/10 hover:bg-white/10'
              }`}
            >
              All ({matches.total_matches})
            </button>
            <button
              onClick={() => setFilter('excellent')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                filter === 'excellent'
                  ? 'glass-card glow'
                  : 'bg-white/5 border border-white/10 hover:bg-white/10'
              }`}
            >
              Excellent (70%+)
            </button>
            <button
              onClick={() => setFilter('good')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                filter === 'good'
                  ? 'glass-card glow'
                  : 'bg-white/5 border border-white/10 hover:bg-white/10'
              }`}
            >
              Good (57-70%)
            </button>
          </div>
        </div>
      </div>

      {/* Job Cards */}
      <div className="space-y-4">
        <AnimatePresence mode="popLayout">
          {filteredMatches.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="glass-card p-12 text-center"
            >
              <Filter size={48} color="#666666" />
              <p className="text-white/60">No jobs match this filter</p>
            </motion.div>
          ) : (
            filteredMatches.map((match, index) => (
              <JobCard
                key={index}
                match={match}
                index={index}
                isExpanded={expandedJob === index}
                onToggle={() => setExpandedJob(expandedJob === index ? null : index)}
              />
            ))
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

interface JobCardProps {
  match: JobMatch;
  index: number;
  isExpanded: boolean;
  onToggle: () => void;
}

const JobCard = ({ match, index, isExpanded, onToggle }: JobCardProps) => {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ delay: index * 0.05 }}
      className="glass-card p-6 hover:scale-[1.01] transition-transform cursor-pointer"
      onClick={onToggle}
    >
      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
        <div className="flex-1">
          {/* Title & Score */}
          <div className="flex items-start justify-between gap-4 mb-3">
            <h3 className="text-xl font-semibold flex-1">
              {match.title}
            </h3>
            <div className={`score-badge ${getScoreColor(match.score)}`}>
              {formatScore(match.score)}
            </div>
          </div>

          {/* Meta Info */}
          <div className="flex flex-wrap gap-4 text-sm text-white/60 mb-4">
            <div className="flex items-center gap-1.5">
              <Location size={16} variant="Bold" color="#ffffff" />
              <span>{match.source_channel}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Calendar size={16} variant="Bold" color="#ffffff" />
              <span>{formatDate(match.scraped_at)}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <TrendUp size={16} variant="Bold" color="#ffffff" />
              <span>{getScoreLabel(match.score)}</span>
            </div>
          </div>

          {/* Job Description Preview */}
          <p className="text-white/80 text-sm mb-4">
            {isExpanded ? match.job_text : truncateText(match.job_text, 200)}
          </p>

          {/* Explanation */}
          {match.explanation && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: isExpanded ? 1 : 0, height: isExpanded ? 'auto' : 0 }}
              className="overflow-hidden"
            >
              <div className="p-4 rounded-lg glass-card mb-4">
                <p className="text-sm text-white font-medium mb-2">
                  Why this matches:
                </p>
                <p className="text-sm text-white/80">
                  {match.explanation}
                </p>
              </div>
            </motion.div>
          )}

          {/* Actions */}
          <div className="flex gap-3">
            <a
              href={match.message_link}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="glass-button px-4 py-2 text-sm font-medium flex items-center gap-2"
            >
              View on Telegram
              <ExportSquare size={16} variant="Bold" color="#ffffff" />
            </a>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onToggle();
              }}
              className="px-4 py-2 text-sm text-white/60 hover:text-white transition-colors"
            >
              {isExpanded ? 'Show Less' : 'Show More'}
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
