/**
 * Background Beams Component (Aceternity UI)
 */
'use client';

import React from 'react';
import { motion } from 'framer-motion';

export const BackgroundBeams = () => {
  const beams = Array.from({ length: 20 });

  return (
    <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
      {beams.map((_, index) => (
        <motion.div
          key={index}
          className="absolute h-full w-px bg-linear-to-b from-transparent via-white to-transparent"
          style={{
            left: `${(index / beams.length) * 100}%`,
            opacity: 0.1,
          }}
          animate={{
            opacity: [0.05, 0.2, 0.05],
            scaleY: [0.5, 1, 0.5],
          }}
          transition={{
            duration: Math.random() * 3 + 2,
            repeat: Infinity,
            delay: Math.random() * 2,
            ease: 'easeInOut',
          }}
        />
      ))}
      
      {/* Radial gradient overlay */}
      <div className="absolute inset-0 bg-gradient-radial from-transparent via-black/50 to-black" />
    </div>
  );
};
