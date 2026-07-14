export const pageVariants = {
  initial: { x: '100%', opacity: 0 },
  animate: { x: 0, opacity: 1, transition: { duration: 0.3, ease: 'easeOut' } },
  exit: { x: '-100%', opacity: 0, transition: { duration: 0.2, ease: 'easeIn' } },
};

export const pageFadeVariants = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: { duration: 0.3 } },
  exit: { opacity: 0, transition: { duration: 0.2 } },
};

export const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

export const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  show: { y: 0, opacity: 1, transition: { duration: 0.4, ease: 'easeOut' } },
};

export const orbVariants = {
  animate: {
    scale: [1, 1.03, 1],
    transition: { duration: 4, repeat: Infinity, ease: 'easeInOut' },
  },
};

export const pulseVariants = {
  animate: {
    scale: [1, 1.2, 1],
    transition: { duration: 1.5, repeat: Infinity },
  },
};

export const tapScale = {
  whileTap: { scale: 0.98 },
  transition: { duration: 0.2 },
};

export const slideUpVariants = {
  hidden: { y: 60, opacity: 0 },
  visible: { y: 0, opacity: 1, transition: { duration: 0.4, ease: 'easeOut' } },
};

export const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.1 },
  },
};

export const staggerItem = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: { duration: 0.35, ease: 'easeOut' },
  },
};

export const fadeIn = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.3 } },
};

export const scaleIn = {
  hidden: { scale: 0.9, opacity: 0 },
  visible: { scale: 1, opacity: 1, transition: { duration: 0.3 } },
};

export const navItemVariants = {
  inactive: { scale: 1 },
  active: { scale: 1.1, transition: { duration: 0.2 } },
};
