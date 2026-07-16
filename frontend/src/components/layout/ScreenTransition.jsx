import { motion, AnimatePresence } from 'framer-motion';

export const ScreenTransition = ({ children, screenKey }) => (
  <AnimatePresence mode="wait">
    <motion.div
      key={screenKey}
      initial={{ x: '100%', opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: '-100%', opacity: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="h-full w-full"
    >
      {children}
    </motion.div>
  </AnimatePresence>
);
