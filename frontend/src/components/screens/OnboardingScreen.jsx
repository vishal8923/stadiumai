import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MapPin, Check } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { LANGUAGES, ACCESSIBILITY_OPTIONS } from '@/utils/constants';
import { NeoButton } from '@/components/ui/NeoButton';
import { NeoInput } from '@/components/ui/NeoInput';
import { NeoToggle } from '@/components/ui/NeoToggle';
import { api } from '@/utils/api';

export const OnboardingScreen = () => {
  const [step, setStep] = useState(0);
  const [selectedLang, setSelectedLang] = useState('en');
  const [access, setAccess] = useState({
    voiceMode: false, highContrast: false, wheelchair: false, hearingAssistance: false,
  });
  const [ticket, setTicket] = useState({ section: '', row: '', gate: '' });
  const [permissions, setPermissions] = useState({ mic: null, location: null });
  const setUserId = useAppStore((s) => s.setUserId);
  const setLanguage = useAppStore((s) => s.setLanguage);
  const setTicketInfo = useAppStore((s) => s.setTicketInfo);
  const navigateTo = useAppStore((s) => s.navigateTo);
  const setAccessibility = useAppStore((s) => s.setAccessibility);

  const createSession = async () => {
    try {
      const res = await api.post('/api/v1/users/session', {
        language: selectedLang,
        accessibility: access,
        ticket_info: ticket,
      });
      setUserId(res.data.user_id);
    } catch {
      setUserId(`user_${Date.now()}`);
    }
    setLanguage(selectedLang);
    setTicketInfo(ticket);
    setAccessibility({ ...access, largeText: false, screenReader: false });
    navigateTo('home');
  };

  const handlePermission = (type, granted) => {
    setPermissions((p) => ({ ...p, [type]: granted }));
  };

  const steps = ['Language', 'Accessibility', 'Ticket', 'Permissions'];

  return (
    <motion.div
      className="h-full flex flex-col px-6 py-8"
      style={{ background: '#0A1628' }}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      {/* Step Indicator */}
      <div className="flex items-center justify-center gap-2 mb-8" role="group" aria-label="Onboarding steps">
        {steps.map((label, i) => (
          <div
            key={i}
            className="rounded-full transition-all"
            role="progressbar"
            aria-label={`Step ${i + 1}: ${label}`}
            aria-valuenow={step >= i ? 100 : 0}
            aria-valuemin={0}
            aria-valuemax={100}
            style={{
              width: step === i ? 24 : 8,
              height: 8,
              background: step >= i ? '#FFD700' : '#4A5D75',
              borderRadius: 4,
            }}
          />
        ))}
      </div>

      <AnimatePresence mode="wait">
        {/* Step 1: Language */}
        {step === 0 && (
          <motion.div
            key="lang"
            initial={{ x: 50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -50, opacity: 0 }}
            className="flex-1 flex flex-col min-h-0"
          >
            <h2 className="text-h1 text-stadium-text font-semibold mb-2 text-center">Select Language</h2>
            <p className="text-body text-stadium-text-secondary mb-6 text-center">Choose your preferred language</p>
            <div className="flex-1 overflow-y-auto space-y-3">
              {LANGUAGES.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => setSelectedLang(lang.code)}
                  className="w-full flex items-center gap-4 p-4 rounded-neo-input transition-all cursor-pointer"
                  style={{
                    background: selectedLang === lang.code ? '#111D2E' : '#0A1628',
                    boxShadow: selectedLang === lang.code
                      ? 'inset 6px 6px 12px #050A10, inset -6px -6px 12px #1A2A40'
                      : '8px 8px 16px #050A10, -8px -8px 16px #1A2A40',
                    border: selectedLang === lang.code ? '2px solid #FFD700' : '2px solid transparent',
                  }}
                >
                  <span className="text-2xl">{lang.flag}</span>
                  <div className="text-left">
                    <p className="text-stadium-text font-medium">{lang.name}</p>
                    <p className="text-stadium-text-tertiary text-xs">{lang.greeting}</p>
                  </div>
                  {selectedLang === lang.code && (
                    <div className="ml-auto w-6 h-6 rounded-full bg-stadium-gold flex items-center justify-center">
                      <Check size={14} color="#0A1628" strokeWidth={3} />
                    </div>
                  )}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        {/* Step 2: Accessibility */}
        {step === 1 && (
          <motion.div
            key="access"
            initial={{ x: 50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -50, opacity: 0 }}
            className="flex-1 flex flex-col min-h-0"
          >
            <h2 className="text-h1 text-stadium-text font-semibold mb-2 text-center">Accessibility</h2>
            <p className="text-body text-stadium-text-secondary mb-6 text-center">Customize your experience</p>
            <div className="flex-1 space-y-4">
              {ACCESSIBILITY_OPTIONS.slice(0, 4).map((opt) => (
                <div
                  key={opt.id}
                  className="flex items-center justify-between p-4 rounded-neo-input"
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
                    enabled={access[opt.id]}
                    onToggle={() => setAccess((a) => ({ ...a, [opt.id]: !a[opt.id] }))}
                    ariaLabel={opt.label}
                  />
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Step 3: Ticket Info */}
        {step === 2 && (
          <motion.div
            key="ticket"
            initial={{ x: 50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -50, opacity: 0 }}
            className="flex-1 flex flex-col min-h-0"
          >
            <h2 className="text-h1 text-stadium-text font-semibold mb-2 text-center">Ticket Info</h2>
            <p className="text-body text-stadium-text-secondary mb-6 text-center">Enter your seat details (optional)</p>
            <div className="flex-1 space-y-4">
              <div>
                <label className="text-stadium-text-secondary text-xs mb-2 block">Section</label>
                <NeoInput
                  value={ticket.section}
                  onChange={(e) => setTicket((t) => ({ ...t, section: e.target.value }))}
                  placeholder="e.g. 12B"
                />
              </div>
              <div>
                <label className="text-stadium-text-secondary text-xs mb-2 block">Row</label>
                <NeoInput
                  value={ticket.row}
                  onChange={(e) => setTicket((t) => ({ ...t, row: e.target.value }))}
                  placeholder="e.g. 5"
                />
              </div>
              <div>
                <label className="text-stadium-text-secondary text-xs mb-2 block">Gate</label>
                <NeoInput
                  value={ticket.gate}
                  onChange={(e) => setTicket((t) => ({ ...t, gate: e.target.value }))}
                  placeholder="e.g. A"
                />
              </div>
            </div>
            <button
              onClick={() => setStep(3)}
              className="mt-4 text-stadium-text-secondary text-sm underline cursor-pointer"
              aria-label="Skip ticket info step"
            >
              Skip this step
            </button>
          </motion.div>
        )}

        {/* Step 4: Permissions */}
        {step === 3 && (
          <motion.div
            key="perms"
            initial={{ x: 50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -50, opacity: 0 }}
            className="flex-1 flex flex-col min-h-0"
          >
            <h2 className="text-h1 text-stadium-text font-semibold mb-2 text-center">Permissions</h2>
            <p className="text-body text-stadium-text-secondary mb-6 text-center">Allow access for better experience</p>
            <div className="flex-1 space-y-4">
              {/* Microphone */}
              <div
                className="p-4 rounded-neo-card"
                style={{ background: '#111D2E', boxShadow: '8px 8px 16px #050A10, -8px -8px 16px #1A2A40' }}
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ background: '#070F1A' }}>
                    <Mic size={20} color="#00B4D8" />
                  </div>
                  <div>
                    <p className="text-stadium-text font-medium">Microphone</p>
                    <p className="text-stadium-text-secondary text-xs">For voice commands & chat</p>
                  </div>
                </div>
                {permissions.mic === null ? (
                  <div className="flex gap-2">
                    <NeoButton size="sm" variant="raised" color="blue" fullWidth onClick={() => handlePermission('mic', true)}>Allow</NeoButton>
                    <NeoButton size="sm" variant="pressed" color="surface" fullWidth onClick={() => handlePermission('mic', false)}>Deny</NeoButton>
                  </div>
                ) : (
                  <p className={`text-sm ${permissions.mic ? 'text-stadium-green' : 'text-stadium-text-secondary'}`}>
                    {permissions.mic ? '✓ Allowed' : 'Denied'}
                  </p>
                )}
              </div>

              {/* Location */}
              <div
                className="p-4 rounded-neo-card"
                style={{ background: '#111D2E', boxShadow: '8px 8px 16px #050A10, -8px -8px 16px #1A2A40' }}
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ background: '#070F1A' }}>
                    <MapPin size={20} color="#00C853" />
                  </div>
                  <div>
                    <p className="text-stadium-text font-medium">Location</p>
                    <p className="text-stadium-text-secondary text-xs">For navigation & crowd info</p>
                  </div>
                </div>
                {permissions.location === null ? (
                  <div className="flex gap-2">
                    <NeoButton size="sm" variant="raised" color="green" fullWidth onClick={() => handlePermission('location', true)}>Allow</NeoButton>
                    <NeoButton size="sm" variant="pressed" color="surface" fullWidth onClick={() => handlePermission('location', false)}>Deny</NeoButton>
                  </div>
                ) : (
                  <p className={`text-sm ${permissions.location ? 'text-stadium-green' : 'text-stadium-text-secondary'}`}>
                    {permissions.location ? '✓ Allowed' : 'Denied'}
                  </p>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Navigation Buttons */}
      <div className="mt-6 flex-shrink-0">
        {step < 3 ? (
          <NeoButton fullWidth onClick={() => setStep(step + 1)}>
            Next
          </NeoButton>
        ) : (
          <NeoButton fullWidth color="gold" onClick={createSession}>
            Get Started
          </NeoButton>
        )}
      </div>
    </motion.div>
  );
};
