import React from 'react';

export const SkeletonLoader = ({ width = '100%', height = 20, circle = false, className = '' }) => (
  <div
    className={`animate-pulse ${className}`}
    style={{
      width,
      height,
      borderRadius: circle ? '50%' : 8,
      background: 'linear-gradient(90deg, #111D2E 25%, #1A2A40 50%, #111D2E 75%)',
      backgroundSize: '200% 100%',
      animation: 'shimmer 1.5s infinite',
    }}
  />
);
