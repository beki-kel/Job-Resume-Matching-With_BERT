/**
 * Shimmer loading component
 */
'use client';

import { cn } from '@/lib/utils';

interface ShimmerProps {
  className?: string;
  count?: number;
}

export const Shimmer = ({ className, count = 1 }: ShimmerProps) => {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={cn(
            'animate-pulse rounded-2xl bg-gradient-to-r from-white/5 via-white/10 to-white/5',
            'bg-[length:200%_100%] animate-shimmer',
            className
          )}
        />
      ))}
    </>
  );
};

export const CardShimmer = () => (
  <div className="glass-card p-6 space-y-4">
    <Shimmer className="h-6 w-3/4" />
    <Shimmer className="h-4 w-full" />
    <Shimmer className="h-4 w-5/6" />
    <div className="flex gap-2 mt-4">
      <Shimmer className="h-8 w-20" />
      <Shimmer className="h-8 w-24" />
    </div>
  </div>
);

export const JobCardShimmer = () => (
  <div className="glass-card p-6 space-y-4">
    <div className="flex justify-between items-start">
      <Shimmer className="h-6 w-2/3" />
      <Shimmer className="h-8 w-16 rounded-full" />
    </div>
    <Shimmer className="h-4 w-1/4" />
    <Shimmer className="h-20 w-full" />
    <div className="flex gap-2">
      <Shimmer className="h-6 w-24" />
      <Shimmer className="h-6 w-32" />
    </div>
  </div>
);
