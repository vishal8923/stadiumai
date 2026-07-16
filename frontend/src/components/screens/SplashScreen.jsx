import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useAppStore } from '@/store/appStore';
import { ProgressBar } from '@/components/ui/ProgressBar';

export const SplashScreen = () => {
  const navigateTo = useAppStore((s) => s.navigateTo);
  const userId = useAppStore((s) => s.userId);
  const [progress, setProgress] = useState(0);
  const [dots, setDots] = useState('');

  useEffect(() => {
    const progressTimer = setInterval(() => {
      setProgress((p) => Math.min(100, p + 2));
    }, 40);

    const dotsTimer = setInterval(() => {
      setDots((d) => (d.length >= 3 ? '' : d + '.'));
    }, 500);

    const redirectTimer = setTimeout(() => {
      if (userId) {
        navigateTo('home');
      } else {
        navigateTo('onboarding');
      }
    }, 2500);

    return () => {
      clearInterval(progressTimer);
      clearInterval(dotsTimer);
      clearTimeout(redirectTimer);
    };
  }, [navigateTo, userId]);

  return (
    <motion.div
      className="h-full w-full flex flex-col items-center justify-center px-8"
      style={{ background: '#0A1628' }}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* AI Orb */}
      <motion.div
        className="relative flex items-center justify-center mb-8"
        style={{ width: 220, height: 220 }}
        animate={{ scale: [1, 1.03, 1] }}
        transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
      >
        <div
          className="absolute inset-0 rounded-full"
          style={{
            padding: 4,
            background: 'linear-gradient(135deg, #FFD700 0%, #00B4D8 50%, #FFD700 100%)',
          }}
        >
          <div className="w-full h-full rounded-full" style={{ background: '#111D2E' }} />
        </div>
        <div
          className="absolute inset-0 rounded-full"
          style={{
            boxShadow: '0 0 30px rgba(0, 180, 216, 0.4), 8px 8px 16px #050A10, -8px -8px 16px #1A2A40',
          }}
        />
        <div
          className="relative rounded-full flex items-center justify-center"
          style={{
            width: 200,
            height: 200,
            background: 'radial-gradient(circle at 50% 50%, rgba(0, 180, 216, 0.25) 0%, #111D2E 70%)',
          }}
        >
          <span className="text-6xl font-bold text-stadium-text">AI</span>
        </div>
      </motion.div>

      {/* Loading Text */}
      <p className="text-stadium-text-secondary font-inter text-body mb-8">
        Initializing Stadium AI{dots}
      </p>

      {/* Progress Bar */}
      <div className="w-full max-w-xs">
        <ProgressBar progress={progress} color="#FFD700" height={6} />
      </div>
    </motion.div>
  );
};
