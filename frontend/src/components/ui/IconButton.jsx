import { motion } from 'framer-motion';

export const IconButton = ({ icon, onClick, size = 40, active = false, badge = null, className = '', ariaLabel }) => (
  <motion.button
    whileTap={{ scale: 0.9 }}
    onClick={onClick}
    aria-label={ariaLabel}
    className={`relative flex items-center justify-center rounded-full cursor-pointer ${className}`}
    style={{
      width: size,
      height: size,
      background: '#111D2E',
      boxShadow: active
        ? '0 0 20px rgba(0, 180, 216, 0.3), 8px 8px 16px #050A10, -8px -8px 16px #1A2A40'
        : '8px 8px 16px #050A10, -8px -8px 16px #1A2A40',
      border: active ? '2px solid #FFD700' : '2px solid transparent',
    }}
  >
    {icon}
    {badge !== null && (
      <span
        className="absolute -top-1 -right-1 flex items-center justify-center rounded-full text-[9px] font-bold"
        style={{
          width: 16,
          height: 16,
          background: '#FF3D00',
          color: '#FFFFFF',
        }}
      >
        {badge}
      </span>
    )}
  </motion.button>
);
