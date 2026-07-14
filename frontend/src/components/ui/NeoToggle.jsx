import React from 'react';
import { motion } from 'framer-motion';

export const NeoToggle = ({ enabled, onToggle, size = 'md', activeColor = '#00C853' }) => {
  const sizeMap = {
    sm: { w: 40, h: 22, thumb: 16 },
    md: { w: 52, h: 28, thumb: 22 },
    lg: { w: 64, h: 34, thumb: 28 },
  };
  const s = sizeMap[size] || sizeMap.md;

  return (
    <motion.button
      onClick={onToggle}
      className="relative flex-shrink-0 cursor-pointer"
      style={{
        width: s.w,
        height: s.h,
        borderRadius: s.h / 2,
        background: enabled ? activeColor : '#070F1A',
        boxShadow: enabled
          ? `inset 3px 3px 6px #050A10, inset -3px -3px 6px ${activeColor}66`
          : 'inset 3px 3px 6px #050A10, inset -3px -3px 6px #1A2A40',
        border: 'none',
        outline: 'none',
        transition: 'background 0.3s ease',
      }}
      whileTap={{ scale: 0.95 }}
      role="switch"
      aria-checked={enabled}
    >
      <motion.div
        animate={{ x: enabled ? s.w - s.thumb - 3 : 3 }}
        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
        style={{
          width: s.thumb,
          height: s.thumb,
          borderRadius: '50%',
          background: enabled ? '#FFFFFF' : '#4A5D75',
          boxShadow: enabled
            ? '0 2px 8px rgba(0,0,0,0.3)'
            : 'inset 2px 2px 4px #050A10, inset -2px -2px 4px #1A2A40',
          position: 'absolute',
          top: (s.h - s.thumb) / 2,
        }}
      />
    </motion.button>
  );
};
