import { motion } from 'framer-motion';
import { ArrowLeft, Toilet, Hand, Globe } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { useAccessibility } from '@/hooks/useAccessibility';
import { NeoToggle } from '@/components/ui/NeoToggle';
import { ACCESSIBILITY_OPTIONS } from '@/utils/constants';

export const AccessibilityScreen = () => {
  const goBack = useAppStore((s) => s.goBack);
  const navigateTo = useAppStore((s) => s.navigateTo);
  const accessibility = useAppStore((s) => s.accessibility);
  const toggleAccessibility = useAppStore((s) => s.toggleAccessibility);
  useAccessibility();

  const quickActions = [
    { icon: Toilet, label: 'Find Accessible Restroom', color: '#00B4D8', screen: 'map' },
    { icon: Hand, label: 'Request Wheelchair Assistance', color: '#00C853', screen: 'incident' },
    { icon: Globe, label: 'Sign Language Services', color: '#DAA520', screen: 'chat' },
  ];

  return (
    <div className="h-full flex flex-col" style={{ background: 'var(--bg-base)' }}>
      {/* Header */}
      <div className="flex items-center gap-3 px-6 py-4 border-b border-gray-100 bg-white/60 backdrop-blur-md">
        <button
          onClick={goBack}
          className="w-10 h-10 rounded-full flex items-center justify-center cursor-pointer transition-colors"
          style={{ background: 'rgba(255, 255, 255, 0.8)', border: '1px solid rgba(26, 36, 47, 0.08)' }}
          aria-label="Go back"
        >
          <ArrowLeft size={20} color="#1A242F" />
        </button>
        <h1 className="text-xl text-[#1A242F] font-bold tracking-tight">Accessibility Settings</h1>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6 max-w-2xl w-full mx-auto">
        {/* Toggles */}
        <div className="space-y-4">
          {ACCESSIBILITY_OPTIONS.map((opt) => (
            <motion.div
              key={opt.id}
              whileHover={{ scale: 1.005 }}
              className="flex items-center justify-between p-5 rounded-2xl glass-card"
            >
              <div className="flex-1 mr-4">
                <p className="text-[#1A242F] font-bold text-sm leading-tight">{opt.label}</p>
                <p className="text-[#5A6B7C] text-xs mt-1 leading-snug">{opt.description}</p>
              </div>
              <NeoToggle
                enabled={accessibility[opt.id]}
                onToggle={() => toggleAccessibility(opt.id)}
                ariaLabel={opt.label}
              />
            </motion.div>
          ))}
        </div>

        {/* Live Preview */}
        <div
          className="p-5 rounded-2xl border border-gray-200/60 bg-gray-100/50"
        >
          <p className="text-[#5A6B7C] text-[10px] font-bold uppercase tracking-wider mb-3">Live Accessibility Preview</p>
          <div
            className="p-4 rounded-xl shadow-inner transition-all duration-200"
            style={{
              background: accessibility.highContrast ? '#000' : 'rgba(255, 255, 255, 0.95)',
              border: accessibility.highContrast ? '2px solid #fff' : '1px solid rgba(26, 36, 47, 0.08)',
              fontSize: accessibility.largeText ? '17px' : '14px',
            }}
          >
            <p style={{ color: accessibility.highContrast ? '#fff' : '#1A242F', fontWeight: accessibility.highContrast ? 'bold' : 'normal' }}>
              This is how notifications and guidelines will be rendered.
            </p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="space-y-3">
          <h2 className="text-sm uppercase tracking-wider text-[#5A6B7C] font-bold mt-2">Quick Actions</h2>
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <motion.button
                key={action.label}
                whileHover={{ scale: 1.005 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => navigateTo(action.screen)}
                className="w-full flex items-center gap-4 p-4 rounded-2xl cursor-pointer text-left glass-card"
                aria-label={action.label}
              >
                <div
                  className="w-10 h-10 rounded-full flex items-center justify-center bg-gray-50 border border-gray-100"
                >
                  <Icon size={20} color={action.color} />
                </div>
                <span className="text-[#1A242F] font-bold text-sm">{action.label}</span>
              </motion.button>
            );
          })}
        </div>
      </div>
    </div>
  );
};
