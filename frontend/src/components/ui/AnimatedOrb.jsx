import React from 'react';
import { motion } from 'framer-motion';
import { Brain } from 'lucide-react';

export const AnimatedOrb = ({
  size = 180,
  icon: Icon = Brain,
  iconSize = 64,
  iconColor = '#F0F4F8',
  className = '',
  onClick,
}) => (
  <motion.div
    className={`relative flex items-center justify-center cursor-pointer ${className}`}
    style={{ width: size, height: size }}
    animate={{ scale: [1, 1.03, 1] }}
    transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
    onClick={onClick}
  >
    {/* Outer ring with gradient */}
    <div
      className="absolute inset-0 rounded-full"
      style={{
        padding: 4,
        background: 'linear-gradient(135deg, #FFD700 0%, #00B4D8 50%, #FFD700 100%)',
        animation: 'spin 6s linear infinite',
      }}
    >
      <div
        className="w-full h-full rounded-full"
        style={{ background: '#111D2E' }}
      />
    </div>

    {/* Glow effect */}
    <div
      className="absolute inset-0 rounded-full"
      style={{
        boxShadow: '0 0 20px rgba(0, 180, 216, 0.3), 8px 8px 16px #050A10, -8px -8px 16px #1A2A40',
      }}
    />

    {/* Inner circle with gradient */}
    <div
      className="relative rounded-full flex items-center justify-center"
      style={{
        width: size - 16,
        height: size - 16,
        background: 'radial-gradient(circle at 50% 50%, rgba(0, 180, 216, 0.2) 0%, #111D2E 70%)',
      }}
    >
      <Icon size={iconSize} color={iconColor} />
    </div>

    {/* Status dot */}
    <div
      className="absolute flex items-center gap-1.5"
      style={{ bottom: -20, left: '50%', transform: 'translateX(-50%)', whiteSpace: 'nowrap' }}
    >
      <motion.div
        className="rounded-full"
        style={{ width: 8, height: 8, background: '#00C853' }}
        animate={{ scale: [1, 1.2, 1] }}
        transition={{ duration: 1.5, repeat: Infinity }}
      />
      <span className="text-xs font-medium text-stadium-text-secondary">AI Online</span>
    </div>
  </motion.div>
);
