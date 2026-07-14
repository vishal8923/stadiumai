import React from 'react';
import { motion } from 'framer-motion';

export const VoiceWaveform = ({ isActive, barCount = 5, color = '#00B4D8' }) => {
  return (
    <div className="flex items-center justify-center gap-1" style={{ height: 40 }}>
      {Array.from({ length: barCount }).map((_, i) => (
        <motion.div
          key={i}
          animate={isActive ? {
            height: [8, 16 + Math.random() * 16, 8],
          } : { height: 8 }}
          transition={{
            duration: 0.4,
            repeat: Infinity,
            repeatType: 'reverse',
            delay: i * 0.05,
            ease: 'easeInOut',
          }}
          style={{
            width: 4,
            borderRadius: 2,
            background: color,
          }}
        />
      ))}
    </div>
  );
};
