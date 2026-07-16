import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { WifiOff, Wifi, Loader2 } from 'lucide-react';

export const OfflineBanner = ({ isOnline, isSyncing, pendingCount }) => {
  // Track whether we've been offline so we only show "Back Online" after a real transition
  const wasOffline = useRef(false);
  const [showBackOnline, setShowBackOnline] = useState(false);

  useEffect(() => {
    if (!isOnline) {
      // Mark that we went offline
      wasOffline.current = true;
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setShowBackOnline(false);
    } else if (isOnline && wasOffline.current && !isSyncing && pendingCount === 0) {
      // We just came back online after being offline, and syncing is done
       
      setShowBackOnline(true);
      wasOffline.current = false;

      // Auto-dismiss after 3 seconds
      const timer = setTimeout(() => {
        setShowBackOnline(false);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [isOnline, isSyncing, pendingCount]);

  return (
    <AnimatePresence>
      {!isOnline && (
        <motion.div
          initial={{ y: -60, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -60, opacity: 0 }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
          className="fixed top-0 left-0 right-0 z-[100] px-4 py-3"
          style={{
            background: 'linear-gradient(135deg, #FF3D00 0%, #FF6B35 100%)',
            boxShadow: '0 4px 20px rgba(255, 61, 0, 0.4)',
          }}
          role="alert"
        >
          <div className="flex items-center justify-between max-w-lg mx-auto">
            <div className="flex items-center gap-3">
              <WifiOff size={20} className="text-white" />
              <span className="text-white font-medium text-sm">Offline Mode — Using cached data</span>
            </div>
            {pendingCount > 0 && (
              <span className="text-white/80 text-xs">{pendingCount} pending</span>
            )}
          </div>
        </motion.div>
      )}
      {isOnline && isSyncing && (
        <motion.div
          initial={{ y: -60, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -60, opacity: 0 }}
          className="fixed top-0 left-0 right-0 z-[100] px-4 py-3"
          style={{
            background: 'linear-gradient(135deg, #00C853 0%, #00E676 100%)',
            boxShadow: '0 4px 20px rgba(0, 200, 83, 0.4)',
          }}
        >
          <div className="flex items-center justify-center gap-3">
            <Loader2 size={18} className="text-white animate-spin" />
            <span className="text-white font-medium text-sm">Syncing {pendingCount} items...</span>
          </div>
        </motion.div>
      )}
      {showBackOnline && (
        <motion.div
          initial={{ y: -60, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -60, opacity: 0 }}
          className="fixed top-0 left-0 right-0 z-[100] px-4 py-3"
          style={{
            background: 'linear-gradient(135deg, #00C853 0%, #00E676 100%)',
            boxShadow: '0 4px 20px rgba(0, 200, 83, 0.4)',
          }}
        >
          <div className="flex items-center justify-center gap-3">
            <Wifi size={18} className="text-white" />
            <span className="text-white font-medium text-sm">Back Online — All synced!</span>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
