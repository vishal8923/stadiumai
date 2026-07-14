import React from 'react';

export const Badge = ({ children, color = '#FFD700', bgOpacity = 0.15, textColor = null, className = '', size = 'sm' }) => {
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-[10px]',
    md: 'px-3 py-1 text-xs',
    lg: 'px-4 py-1.5 text-sm',
  };

  return (
    <span
      className={`inline-flex items-center justify-center rounded-full font-inter font-semibold ${sizeClasses[size]} ${className}`}
      style={{
        backgroundColor: `${color}${Math.round(bgOpacity * 255).toString(16).padStart(2, '0')}`,
        color: textColor || color,
      }}
    >
      {children}
    </span>
  );
};
