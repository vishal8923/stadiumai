import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Volume2, VolumeX, Navigation } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { useVoice } from '@/hooks/useVoice';
import { ProgressBar } from '@/components/ui/ProgressBar';

const NAV_STEPS = [
  { instruction: 'Turn left at Concourse 1', next: 'Then take elevator to Level 2', distance: '150m', progress: 20 },
  { instruction: 'Take elevator to Level 2', next: 'Walk straight to Section 12', distance: '100m', progress: 45 },
  { instruction: 'Walk straight to Section 12', next: 'Your seat is on the right', distance: '120m', progress: 70 },
  { instruction: 'Your seat is on the right', next: 'Arrived at destination', distance: '80m', progress: 90 },
];

export const NavigationScreen = () => {
  const goBack = useAppStore((s) => s.goBack);
  const ticketInfo = useAppStore((s) => s.ticketInfo);
  const [step, setStep] = useState(0);
  const [voiceOn, setVoiceOn] = useState(false);
  const [eta, setEta] = useState(8);
  const { speak } = useVoice();

  const currentStep = NAV_STEPS[Math.min(step, NAV_STEPS.length - 1)];

  useEffect(() => {
    const timer = setInterval(() => {
      setStep((s) => Math.min(s + 1, NAV_STEPS.length - 1));
      setEta((e) => Math.max(1, e - 2));
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (voiceOn) {
      speak(currentStep.instruction);
    }
  }, [step, voiceOn, speak, currentStep.instruction]);

  return (
    <div className="h-full flex flex-col" style={{ background: '#0A1628' }}>
      {/* Top Bar */}
      <div className="px-4 pt-4 pb-2">
        <div className="flex items-center gap-3 mb-4">
          <button
            onClick={goBack}
            className="w-10 h-10 rounded-full flex items-center justify-center cursor-pointer"
            style={{ background: '#111D2E', boxShadow: '4px 4px 8px #050A10, -4px -4px 8px #1A2A40' }}
            aria-label="Go back"
          >
            <ArrowLeft size={20} color="#F0F4F8" />
          </button>
          <div>
            <p className="text-stadium-text-secondary text-xs">Destination</p>
            <h1 className="text-h1 text-stadium-text font-semibold">
              {ticketInfo.section ? `Section ${ticketInfo.section}` : 'Section 12B'}
            </h1>
          </div>
          <button
            onClick={() => setVoiceOn(!voiceOn)}
            className="ml-auto w-10 h-10 rounded-full flex items-center justify-center cursor-pointer"
            style={{ background: '#111D2E', boxShadow: '4px 4px 8px #050A10, -4px -4px 8px #1A2A40' }}
            aria-label={voiceOn ? 'Disable voice guidance' : 'Enable voice guidance'}
            aria-pressed={voiceOn}
          >
            {voiceOn ? <Volume2 size={18} color="#00B4D8" /> : <VolumeX size={18} color="#8B9DB8" />}
          </button>
        </div>

        <div className="flex items-baseline gap-3">
          <span className="text-score text-stadium-gold font-bold">{eta} min</span>
          <span className="text-stadium-text-secondary text-sm">{currentStep.distance} remaining</span>
        </div>
      </div>

      {/* Main Direction */}
      <div className="flex-1 flex flex-col items-center justify-center px-8">
        {/* Direction Arrow */}
        <motion.div
          key={step}
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="mb-8"
          style={{
            filter: 'drop-shadow(0 0 20px rgba(0, 180, 216, 0.4))',
          }}
        >
          <Navigation size={120} color="#00B4D8" strokeWidth={1.5} />
        </motion.div>

        {/* Instruction */}
        <motion.div
          key={`text-${step}`}
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="text-center"
        >
          <h2 className="text-xl font-semibold text-stadium-text mb-2">
            {currentStep.instruction}
          </h2>
          <p className="text-stadium-text-secondary text-sm">
            {currentStep.next}
          </p>
        </motion.div>

        {/* Progress */}
        <div className="w-full mt-8">
          <ProgressBar progress={currentStep.progress} color="#FFD700" height={6} />
          <div className="flex justify-between mt-2">
            <span className="text-stadium-text-tertiary text-xs">Start</span>
            <span className="text-stadium-text-tertiary text-xs">{currentStep.progress}%</span>
            <span className="text-stadium-text-tertiary text-xs">Destination</span>
          </div>
        </div>
      </div>

      {/* Mini Map */}
      <div className="px-4 pb-4">
        <div
          className="h-[160px] rounded-neo-card overflow-hidden p-3"
          style={{ background: '#111D2E', boxShadow: '8px 8px 16px #050A10, -8px -8px 16px #1A2A40' }}
        >
          <svg viewBox="0 0 300 100" className="w-full h-full">
            <rect width="300" height="100" fill="#070F1A" rx="8" />
            {/* Simplified route */}
            <path
              d="M 40 80 Q 100 20 150 50 T 260 30"
              fill="none"
              stroke="#00B4D8"
              strokeWidth="3"
              strokeDasharray="8 4"
              opacity="0.6"
            >
              <animate attributeName="stroke-dashoffset" from="0" to="-12" dur="1s" repeatCount="indefinite" />
            </path>
            {/* User dot */}
            <circle cx={40 + (step / NAV_STEPS.length) * 200} cy={50} r="5" fill="#00B4D8">
              <animate attributeName="r" values="5;7;5" dur="2s" repeatCount="indefinite" />
            </circle>
            {/* Destination */}
            <circle cx="260" cy="30" r="6" fill="#FFD700" opacity="0.8" />
          </svg>
        </div>
      </div>
    </div>
  );
};
