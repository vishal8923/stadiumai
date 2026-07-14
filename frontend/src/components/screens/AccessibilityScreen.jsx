import React from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Accessibility, Toilet, Hand, Globe } from 'lucide-react';
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
    { icon: Globe, label: 'Sign Language Services', color: '#FFD700', screen: 'chat' },
  ];

  return (
    <div className="h-full flex flex-col" style={{ background: '#0A1628' }}>
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3">
        <button
          onClick={goBack}
          className="w-10 h-10 rounded-full flex items-center justify-center cursor-pointer"
          style={{ background: '#111D2E', boxShadow: '4px 4px 8px #050A10, -4px -4px 8px #1A2A40' }}
        >
          <ArrowLeft size={20} color="#F0F4F8" />
        </button>
        <h1 className="text-h1 text-stadium-text font-semibold">Accessibility</h1>
      </div>

      <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-4">
        {/* Toggles */}
        {ACCESSIBILITY_OPTIONS.map((opt) => (
          <motion.div
            key={opt.id}
            whileTap={{ scale: 0.99 }}
            className="flex items-center justify-between p-4 rounded-neo-button"
            style={{
              background: '#111D2E',
              boxShadow: '8px 8px 16px #050A10, -8px -8px 16px #1A2A40',
            }}
          >
            <div className="flex-1 mr-4">
              <p className="text-stadium-text font-medium text-sm">{opt.label}</p>
              <p className="text-stadium-text-secondary text-xs mt-0.5">{opt.description}</p>
            </div>
            <NeoToggle
              enabled={accessibility[opt.id]}
              onToggle={() => toggleAccessibility(opt.id)}
            />
          </motion.div>
        ))}

        {/* Live Preview */}
        <div
          className="p-4 rounded-neo-card mt-4"
          style={{ background: '#070F1A', boxShadow: 'inset 6px 6px 12px #050A10, inset -6px -6px 12px #1A2A40' }}
        >
          <p className="text-stadium-text-secondary text-xs mb-3">Live Preview</p>
          <div
            className="p-3 rounded-neo-input"
            style={{
              background: accessibility.highContrast ? '#000' : '#111D2E',
              border: accessibility.highContrast ? '2px solid #fff' : 'none',
              fontSize: accessibility.largeText ? '16px' : '14px',
            }}
          >
            <p style={{ color: accessibility.highContrast ? '#fff' : '#F0F4F8' }}>
              This is how text will appear
            </p>
          </div>
        </div>

        {/* Quick Actions */}
        <h2 className="text-h2 text-stadium-text font-semibold mt-4">Quick Actions</h2>
        {quickActions.map((action) => {
          const Icon = action.icon;
          return (
            <motion.button
              key={action.label}
              whileTap={{ scale: 0.98 }}
              onClick={() => navigateTo(action.screen)}
              className="w-full flex items-center gap-4 p-4 rounded-neo-button cursor-pointer"
              style={{
                background: '#111D2E',
                boxShadow: '8px 8px 16px #050A10, -8px -8px 16px #1A2A40',
              }}
            >
              <div
                className="w-10 h-10 rounded-full flex items-center justify-center"
                style={{ background: '#070F1A' }}
              >
                <Icon size={20} color={action.color} />
              </div>
              <span className="text-stadium-text font-medium text-sm">{action.label}</span>
            </motion.button>
          );
        })}
      </div>
    </div>
  );
};
