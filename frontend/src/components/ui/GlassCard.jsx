import React from 'react';
import { motion } from 'framer-motion';

export const GlassCard = ({ children, className = '', onClick, style = {}, whileTap = { scale: 0.98 } }) => (
  <motion.div
    whileTap={onClick ? whileTap : undefined}
    onClick={onClick}
    className={`rounded-neo-card p-5 ${onClick ? 'cursor-pointer' : ''} ${className}`}
    style={{
      background: '#111D2E',
      boxShadow: '8px 8px 16px #050A10, -8px -8px 16px #1A2A40',
      ...style,
    }}
  >
    {children}
  </motion.div>
);
