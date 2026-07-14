import React from 'react';

export const ProgressBar = ({ progress = 0, color = '#FFD700', trackColor = '#070F1A', height = 4, className = '' }) => (
  <div
    className={`w-full overflow-hidden ${className}`}
    style={{ height, background: trackColor, borderRadius: height / 2 }}
  >
    <div
      className="h-full transition-all duration-500 ease-out"
      style={{
        width: `${Math.min(100, Math.max(0, progress))}%`,
        background: color,
        borderRadius: height / 2,
      }}
    />
  </div>
);
