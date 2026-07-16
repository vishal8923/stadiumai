import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Bus, Train, Car, Footprints, Clock, Leaf } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { api } from '@/utils/api';
import { MOCK_TRANSPORT_OPTIONS } from '@/utils/constants';

const MODE_ICONS = { shuttle: Bus, metro: Train, taxi: Car, walking: Footprints, parking: Car };

export const TransportScreen = () => {
  const goBack = useAppStore((s) => s.goBack);
  const [options, setOptions] = useState([]);
  const [matchEndCountdown, setMatchEndCountdown] = useState(12);

  useEffect(() => {
    const fetchTransport = async () => {
      try {
        const res = await api.get('/api/v1/transport?location=current');
        setOptions(res.data.options || []);
      } catch {
        setOptions(MOCK_TRANSPORT_OPTIONS);
      }
    };
    fetchTransport();

    const timer = setInterval(() => {
      setMatchEndCountdown((c) => Math.max(0, c - 1));
    }, 60000);
    return () => clearInterval(timer);
  }, []);

  const displayOptions = options.length > 0 ? options : MOCK_TRANSPORT_OPTIONS;

  return (
    <div className="h-full flex flex-col" style={{ background: '#0A1628' }}>
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3">
        <button
          onClick={goBack}
          className="w-10 h-10 rounded-full flex items-center justify-center cursor-pointer"
          style={{ background: '#111D2E', boxShadow: '4px 4px 8px #050A10, -4px -4px 8px #1A2A40' }}
          aria-label="Go back"
        >
          <ArrowLeft size={20} color="#F0F4F8" />
        </button>
        <h1 className="text-h1 text-stadium-text font-semibold">Transport</h1>
      </div>

      <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-4">
        {/* Match Status Card */}
        <div
          className="p-5 rounded-neo-card"
          style={{ background: '#111D2E', boxShadow: '8px 8px 16px #050A10, -8px -8px 16px #1A2A40' }}
        >
          <p className="text-stadium-text-secondary text-sm mb-1">Match ends in</p>
          <p className="text-score text-stadium-gold font-bold">{matchEndCountdown} min</p>
          <div className="flex items-center gap-2 mt-3">
            {['A', 'B', 'C', 'D'].map((gate) => {
              const densities = { A: 0.45, B: 0.85, C: 0.92, D: 0.3 };
              const d = densities[gate];
              const color = d < 0.4 ? '#00C853' : d < 0.7 ? '#FFC107' : '#FF3D00';
              return (
                <div key={gate} className="flex-1">
                  <div className="flex items-end gap-1 h-8">
                    <div className="w-full rounded-sm" style={{ height: `${d * 100}%`, background: color, opacity: 0.6 }} />
                  </div>
                  <p className="text-stadium-text-tertiary text-[10px] text-center mt-1">{gate}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Smart Suggestion */}
        <div
          className="p-4 rounded-neo-input flex items-center gap-3"
          style={{
            background: '#070F1A',
            boxShadow: 'inset 6px 6px 12px #050A10, inset -6px -6px 12px #1A2A40',
            borderLeft: '4px solid #00B4D8',
          }}
        >
          <Clock size={20} color="#00B4D8" />
          <p className="text-stadium-text text-sm">Wait 15 min post-match, save 20 min in traffic</p>
        </div>

        {/* Transport Options */}
        <h2 className="text-h2 text-stadium-text font-semibold">Options</h2>
        {displayOptions.map((opt, i) => {
          const Icon = MODE_ICONS[opt.mode] || Car;
          const isRecommended = i === 0;
          return (
            <motion.div
              key={opt.id}
              whileTap={{ scale: 0.98 }}
              className="relative p-4 rounded-neo-button cursor-pointer"
              style={{
                background: '#111D2E',
                boxShadow: '8px 8px 16px #050A10, -8px -8px 16px #1A2A40',
                borderLeft: isRecommended ? '4px solid #FFD700' : '4px solid transparent',
              }}
            >
              {isRecommended && (
                <span
                  className="absolute -top-2 left-3 px-2 py-0.5 rounded-full text-[9px] font-bold"
                  style={{ background: '#FFD700', color: '#0A1628' }}
                >
                  RECOMMENDED
                </span>
              )}
              <div className="flex items-center gap-4">
                <div
                  className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0"
                  style={{ background: '#070F1A', boxShadow: 'inset 4px 4px 8px #050A10, inset -4px -4px 8px #1A2A40' }}
                >
                  <Icon size={22} color="#00B4D8" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-stadium-text font-medium text-sm">{opt.name}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-stadium-gold font-semibold text-sm">{opt.eta} min</span>
                    <span
                      className="text-[10px] px-1.5 py-0.5 rounded-full"
                      style={{
                        background: opt.status === 'on_time' ? 'rgba(0, 200, 83, 0.15)' : opt.status === 'crowded' ? 'rgba(255, 152, 0, 0.15)' : 'rgba(0, 180, 216, 0.15)',
                        color: opt.status === 'on_time' ? '#00C853' : opt.status === 'crowded' ? '#FF9800' : '#00B4D8',
                      }}
                    >
                      {opt.status.replace('_', ' ')}
                    </span>
                  </div>
                </div>
                <div className="text-right flex-shrink-0">
                  <p className="text-stadium-text-secondary text-xs">{opt.distance}m walk</p>
                  {opt.carbon_saved > 0 && (
                    <span className="flex items-center gap-1 text-[10px] text-stadium-green mt-1">
                      <Leaf size={10} />
                      {opt.carbon_saved}kg CO2
                    </span>
                  )}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};
