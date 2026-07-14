import React, { forwardRef } from 'react';

export const NeoInput = forwardRef(({
  value,
  onChange,
  placeholder = '',
  type = 'text',
  className = '',
  disabled = false,
  multiline = false,
  rows = 4,
  ...props
}, ref) => {
  const baseClasses = `w-full px-4 py-3 font-inter text-sm text-stadium-text placeholder-stadium-text-secondary rounded-neo-input outline-none transition-all ${className}`;
  const style = {
    background: '#070F1A',
    boxShadow: 'inset 6px 6px 12px #050A10, inset -6px -6px 12px #1A2A40',
    border: 'none',
  };

  if (multiline) {
    return (
      <textarea
        ref={ref}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        rows={rows}
        className={`${baseClasses} resize-none`}
        style={style}
        {...props}
      />
    );
  }

  return (
    <input
      ref={ref}
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      disabled={disabled}
      className={baseClasses}
      style={style}
      {...props}
    />
  );
});

NeoInput.displayName = 'NeoInput';
