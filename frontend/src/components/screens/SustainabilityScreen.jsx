import { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Camera, Leaf, Navigation, Recycle, Trash2 } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { useNetworkStatus } from '@/hooks/useNetworkStatus';
import { NeoButton } from '@/components/ui/NeoButton';
import { NeoInput } from '@/components/ui/NeoInput';
import { api } from '@/utils/api';
import { addPendingAction } from '@/utils/offlineDB';

export const SustainabilityScreen = () => {
  const goBack = useAppStore((s) => s.goBack);
  const { isOnline } = useNetworkStatus();
  const [item, setItem] = useState('');
  const [result, setResult] = useState(null);
  const [carbonSaved, setCarbonSaved] = useState(2.4);

  const classifyWaste = async () => {
    if (!item.trim()) return;

    const mockResult = {
      item: item.charAt(0).toUpperCase() + item.slice(1),
      bin: item.toLowerCase().includes('plastic') || item.toLowerCase().includes('paper')
        ? { type: 'Recycling', color: '#00B4D8', icon: Recycle }
        : item.toLowerCase().includes('food') || item.toLowerCase().includes('organic')
        ? { type: 'Compost', color: '#00C853', icon: Leaf }
        : { type: 'General Waste', color: '#8B9DB8', icon: Trash2 },
      nearest: '15m ahead, near Food Court North',
      co2: 0.05,
      tip: item.toLowerCase().includes('plastic')
        ? 'Remove any food residue, rinse if possible'
        : 'Make sure item is clean before disposing',
    };

    if (isOnline) {
      try {
        const res = await api.post('/api/v1/sustainability/waste', { item_description: item });
        const mappedResult = {
          item: item.charAt(0).toUpperCase() + item.slice(1),
          bin: {
            type: res.data.bin_type,
            color: res.data.bin_type.includes('Recycling')
              ? '#00B4D8'
              : res.data.bin_type.includes('Compost')
              ? '#00C853'
              : '#8B9DB8',
          },
          nearest: res.data.bin_location,
          co2: 0.05,
          tip: res.data.disposal_tip,
        };
        setResult(mappedResult);
      } catch {
        setResult(mockResult);
      }
    } else {
      await addPendingAction({ type: 'waste_classification', payload: { item } });
      setResult(mockResult);
    }

    setCarbonSaved((c) => c + mockResult.co2);
  };

  const transportData = [
    { mode: 'Shuttle', carbon: 0.3, color: '#00C853' },
    { mode: 'Metro', carbon: 0.1, color: '#00B4D8' },
    { mode: 'Taxi', carbon: 1.2, color: '#FF9800' },
    { mode: 'Walking', carbon: 0, color: '#8B9DB8' },
  ];

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
        <h1 className="text-h1 text-stadium-text font-semibold">Sustainability</h1>
      </div>

      <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-4">
        {/* Waste Scanner */}
        <div
          className="p-5 rounded-neo-card"
          style={{ background: '#111D2E', boxShadow: '8px 8px 16px #050A10, -8px -8px 16px #1A2A40' }}
        >
          <h2 className="text-h2 text-stadium-text font-semibold mb-4">Waste Classifier</h2>

          {/* Camera Frame */}
          <div
            className="aspect-video rounded-neo-input flex items-center justify-center mb-4 relative overflow-hidden"
            style={{
              background: '#070F1A',
              boxShadow: 'inset 6px 6px 12px #050A10, inset -6px -6px 12px #1A2A40',
              border: '2px dashed #4A5D75',
            }}
          >
            <div className="text-center">
              <Camera size={32} color="#4A5D75" className="mx-auto mb-2" />
              <p className="text-stadium-text-secondary text-xs">Camera placeholder</p>
            </div>
            {/* Crosshair */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="w-8 h-8 border-2 border-stadium-text-tertiary border-dashed rounded-sm" />
            </div>
          </div>

          <NeoInput
            value={item}
            onChange={(e) => setItem(e.target.value)}
            placeholder="Describe the item... (e.g. plastic cup)"
            className="mb-3"
          />
          <NeoButton fullWidth onClick={classifyWaste} disabled={!item.trim()}>
            Classify Waste
          </NeoButton>
        </div>

        {/* Result Card */}
        {result && (
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="p-4 rounded-neo-card"
            style={{ background: '#111D2E', boxShadow: '8px 8px 16px #050A10, -8px -8px 16px #1A2A40' }}
          >
            <p className="text-stadium-text font-semibold">{result.item}</p>
            <span
              className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold mt-2"
              style={{ background: `${result.bin.color}22`, color: result.bin.color }}
            >
              {result.bin.type}
            </span>
            <p className="text-stadium-text-secondary text-xs mt-2 flex items-center gap-1">
              <Navigation size={10} />
              {result.nearest}
            </p>
            <p className="text-stadium-green text-xs font-medium mt-2">
              You saved {result.co2}kg CO2!
            </p>
            <p className="text-stadium-text-tertiary text-xs mt-1">{result.tip}</p>
          </motion.div>
        )}

        {/* Carbon Tracker */}
        <div
          className="p-5 rounded-neo-card"
          style={{ background: '#111D2E', boxShadow: '8px 8px 16px #050A10, -8px -8px 16px #1A2A40' }}
        >
          <h2 className="text-h2 text-stadium-text font-semibold mb-1">Carbon Tracker</h2>
          <p className="text-stadium-text-secondary text-xs mb-4">Today's impact</p>
          <p className="text-score text-stadium-gold font-bold">{carbonSaved.toFixed(1)} kg</p>
          <p className="text-stadium-green text-xs mb-4">CO2 saved today</p>

          <div className="space-y-3">
            {transportData.map((t) => (
              <div key={t.mode}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-stadium-text-secondary">{t.mode}</span>
                  <span style={{ color: t.color }}>{t.carbon}kg CO2</span>
                </div>
                <div className="h-2 rounded-full overflow-hidden" style={{ background: '#070F1A' }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(t.carbon / 1.5) * 100}%` }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className="h-full rounded-full"
                    style={{ background: t.color }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
