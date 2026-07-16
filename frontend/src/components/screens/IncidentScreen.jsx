import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, HeartPulse, Shield, Flame, UserX, Wrench, CheckCircle, Copy } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { useNetworkStatus } from '@/hooks/useNetworkStatus';
import { NeoButton } from '@/components/ui/NeoButton';
import { NeoInput } from '@/components/ui/NeoInput';
import { api } from '@/utils/api';
import { addPendingAction } from '@/utils/offlineDB';

const INCIDENT_TYPES = [
  { id: 'medical', label: 'Medical', icon: HeartPulse, color: '#FF3D00' },
  { id: 'security', label: 'Security', icon: Shield, color: '#FFD700' },
  { id: 'fire', label: 'Fire', icon: Flame, color: '#FF3D00' },
  { id: 'lost', label: 'Lost Person', icon: UserX, color: '#00B4D8' },
  { id: 'infrastructure', label: 'Infrastructure', icon: Wrench, color: '#8B9DB8' },
];

const SEVERITY_LEVELS = [
  { value: 1, label: 'Low', color: '#00C853' },
  { value: 2, label: 'Medium', color: '#FFC107' },
  { value: 3, label: 'High', color: '#FF9800' },
  { value: 4, label: 'Critical', color: '#FF3D00' },
];

export const IncidentScreen = () => {
  const goBack = useAppStore((s) => s.goBack);
  const { isOnline } = useNetworkStatus();
  const [step, setStep] = useState(0);
  const [type, setType] = useState(null);
  const [location, setLocation] = useState('Concourse 1, Gate A');
  const [description, setDescription] = useState('');
  const [severity, setSeverity] = useState(2);
  const [incidentId, setIncidentId] = useState(null);

  const submitIncident = async () => {
    const payload = {
      type,
      location,
      description,
      severity,
      timestamp: new Date().toISOString(),
    };

    if (isOnline) {
      try {
        const res = await api.post('/api/v1/incidents', payload);
        setIncidentId(res.data.incident_id || `INC-${Date.now()}`);
      } catch {
        setIncidentId(`INC-${Date.now()}`);
      }
    } else {
      await addPendingAction({ type: 'incident', payload });
      setIncidentId(`INC-${Date.now()}-PENDING`);
    }
    setStep(2);
  };

  return (
    <div className="h-full flex flex-col" style={{ background: '#0A1628' }}>
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3">
        <button
          onClick={step === 0 ? goBack : () => setStep(step - 1)}
          className="w-10 h-10 rounded-full flex items-center justify-center cursor-pointer"
          style={{ background: '#111D2E', boxShadow: '4px 4px 8px #050A10, -4px -4px 8px #1A2A40' }}
          aria-label={step === 0 ? 'Go back' : 'Previous step'}
        >
          <ArrowLeft size={20} color="#F0F4F8" />
        </button>
        <h1 className="text-h1 text-stadium-text font-semibold">Report Incident</h1>
      </div>

      {/* Step Indicator */}
      <div className="flex items-center justify-center gap-2 px-4 mb-4">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="rounded-full transition-all"
            style={{
              width: step === i ? 24 : 8,
              height: 8,
              background: step >= i ? '#FFD700' : '#4A5D75',
            }}
          />
        ))}
      </div>

      <div className="flex-1 overflow-y-auto px-4 pb-4">
        <AnimatePresence mode="wait">
          {/* Step 1: Select Type */}
          {step === 0 && (
            <motion.div
              key="type"
              initial={{ x: 50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -50, opacity: 0 }}
            >
              <h2 className="text-h2 text-stadium-text font-semibold mb-4">What type of incident?</h2>
              <div className="grid grid-cols-2 gap-3">
                {INCIDENT_TYPES.map((inc) => {
                  const Icon = inc.icon;
                  return (
                    <motion.button
                      key={inc.id}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setType(inc.id)}
                      className="flex flex-col items-center justify-center gap-3 p-5 rounded-neo-button cursor-pointer aspect-square"
                      style={{
                        background: '#111D2E',
                        boxShadow: type === inc.id
                          ? 'inset 6px 6px 12px #050A10, inset -6px -6px 12px #1A2A40'
                          : '8px 8px 16px #050A10, -8px -8px 16px #1A2A40',
                        border: type === inc.id ? `2px solid ${inc.color}` : '2px solid transparent',
                      }}
                    >
                      <Icon size={40} color={inc.color} />
                      <span className="text-stadium-text font-medium text-sm">{inc.label}</span>
                    </motion.button>
                  );
                })}
              </div>
              <div className="mt-6">
                <NeoButton fullWidth disabled={!type} onClick={() => setStep(1)}>
                  Next
                </NeoButton>
              </div>
            </motion.div>
          )}

          {/* Step 2: Details */}
          {step === 1 && (
            <motion.div
              key="details"
              initial={{ x: 50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -50, opacity: 0 }}
              className="space-y-5"
            >
              <div>
                <label className="text-stadium-text-secondary text-xs mb-2 block">Location</label>
                <NeoInput value={location} onChange={(e) => setLocation(e.target.value)} />
              </div>

              <div>
                <label className="text-stadium-text-secondary text-xs mb-2 block">Description</label>
                <NeoInput
                  multiline
                  rows={4}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe the incident..."
                />
              </div>

              <div>
                <label className="text-stadium-text-secondary text-xs mb-2 block">Severity</label>
                <div className="flex items-center gap-2">
                  <input
                    type="range"
                    min="1"
                    max="4"
                    value={severity}
                    onChange={(e) => setSeverity(Number(e.target.value))}
                    className="flex-1 accent-stadium-gold"
                    aria-label={`Severity level: ${SEVERITY_LEVELS.find(l => l.value === severity)?.label || 'Medium'}`}
                    aria-valuemin={1}
                    aria-valuemax={4}
                    aria-valuenow={severity}
                  />
                </div>
                <div className="flex justify-between mt-1">
                  {SEVERITY_LEVELS.map((level) => (
                    <span
                      key={level.value}
                      className="text-xs"
                      style={{ color: severity === level.value ? level.color : '#4A5D75' }}
                    >
                      {level.label}
                    </span>
                  ))}
                </div>
              </div>

              <NeoButton
                fullWidth
                color="red"
                disabled={!description.trim()}
                onClick={submitIncident}
              >
                Submit Report
              </NeoButton>

              {!isOnline && (
                <p className="text-stadium-text-secondary text-xs text-center">
                  You are offline. This report will be queued and synced when you are back online.
                </p>
              )}
            </motion.div>
          )}

          {/* Step 3: Confirmation */}
          {step === 2 && (
            <motion.div
              key="confirm"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="flex flex-col items-center text-center pt-8"
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: 'spring' }}
              >
                <CheckCircle size={64} color="#00C853" />
              </motion.div>

              <h2 className="text-h1 text-stadium-text font-semibold mt-6 mb-2">Incident Reported</h2>

              <div className="flex items-center gap-2 mt-4 mb-2">
                <span
                  className="font-mono text-lg font-bold px-4 py-2 rounded-neo-input"
                  style={{ background: '#070F1A', color: '#FFD700' }}
                >
                  {incidentId}
                </span>
                <button
                  onClick={() => navigator.clipboard?.writeText(incidentId)}
                  className="w-10 h-10 rounded-full flex items-center justify-center cursor-pointer"
                  style={{ background: '#111D2E', boxShadow: '4px 4px 8px #050A10, -4px -4px 8px #1A2A40' }}
                  aria-label="Copy incident ID"
                >
                  <Copy size={16} color="#8B9DB8" />
                </button>
              </div>

              <span
                className="px-3 py-1 rounded-full text-xs font-semibold mt-2"
                style={{ background: 'rgba(0, 200, 83, 0.15)', color: '#00C853' }}
              >
                Reported
              </span>

              <p className="text-stadium-text-secondary text-sm mt-4">
                Nearest team: 3 min away
              </p>

              <div className="w-full mt-8 space-y-3">
                <NeoButton fullWidth onClick={goBack}>
                  Track Incident
                </NeoButton>
                <NeoButton fullWidth variant="pressed" color="surface" onClick={() => { setStep(0); setType(null); setDescription(''); }}>
                  Report Another
                </NeoButton>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};
