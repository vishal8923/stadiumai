import { motion } from 'framer-motion';

export const NeoButton = ({
  children,
  onClick,
  variant = 'raised',
  color = 'gold',
  size = 'md',
  fullWidth = false,
  disabled = false,
  className = '',
  icon = null,
  type = 'button',
}) => {
  const colorMap = {
    gold: { bg: '#FFD700', text: '#0A1628' },
    blue: { bg: '#00B4D8', text: '#0A1628' },
    green: { bg: '#00C853', text: '#0A1628' },
    red: { bg: '#FF3D00', text: '#FFFFFF' },
    surface: { bg: '#111D2E', text: '#F0F4F8' },
  };

  const sizeMap = {
    sm: 'px-4 py-2 text-xs rounded-neo-button',
    md: 'px-6 py-3 text-sm rounded-neo-button',
    lg: 'px-8 py-4 text-base rounded-neo-button',
  };

  const c = colorMap[color] || colorMap.gold;
  const shadow = variant === 'pressed'
    ? 'inset 6px 6px 12px #050A10, inset -6px -6px 12px #1A2A40'
    : '8px 8px 16px #050A10, -8px -8px 16px #1A2A40';

  return (
    <motion.button
      type={type}
      whileTap={disabled ? {} : { scale: 0.96 }}
      whileHover={disabled ? {} : { scale: 1.02 }}
      onClick={onClick}
      disabled={disabled}
      className={`font-inter font-semibold flex items-center justify-center gap-2 transition-all ${sizeMap[size]} ${fullWidth ? 'w-full' : ''} ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'} ${className}`}
      style={{
        background: c.bg,
        color: c.text,
        boxShadow: shadow,
        border: 'none',
        outline: 'none',
      }}
    >
      {icon}
      {children}
    </motion.button>
  );
};
