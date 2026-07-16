import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Accessibility, Eye, Navigation } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { useCrowdPolling } from '@/hooks/useCrowdPolling';
import { getDensityColor } from '@/utils/formatters';
import { AMENITIES } from '@/utils/constants';

const STADIUM_SECTIONS = Array.from({ length: 32 }, (_, i) => ({
  id: `section_${i + 1}`,
  name: `Sec ${i + 1}`,
  angle: (i / 32) * Math.PI * 2,
}));

export const MapScreen = () => {
  const goBack = useAppStore((s) => s.goBack);
  const navigateTo = useAppStore((s) => s.navigateTo);
  const crowdData = useAppStore((s) => s.crowdData);
  const [layer, setLayer] = useState('crowd');
  const [wheelchairMode, setWheelchairMode] = useState(false);
  const [crowdAvoid, setCrowdAvoid] = useState(false);
  const [selectedZone, setSelectedZone] = useState(null);

  useCrowdPolling(30000);

  const getZoneDensity = useCallback((zoneId) => {
    if (!crowdData?.zones) return 0.3;
    const zone = crowdData.zones.find((z) => z.zone_id === zoneId);
    return zone?.density ?? 0.3;
  }, [crowdData]);

  const getZoneLevel = useCallback((zoneId) => {
    if (!crowdData?.zones) return 'low';
    const zone = crowdData.zones.find((z) => z.zone_id === zoneId);
    return zone?.level || 'low';
  }, [crowdData]);

  const renderStadiumSVG = () => {
    const cx = 200;
    const cy = 200;
    const rx = 160;
    const ry = 120;

    return (
      <svg
        viewBox="0 0 400 400"
        preserveAspectRatio="xMidYMid meet"
        style={{ width: '100%', height: '100%', display: 'block' }}
        aria-label="Stadium Map"
      >
        {/* Stadium outline */}
        <ellipse cx={cx} cy={cy} rx={rx + 20} ry={ry + 20} fill="#070F1A" stroke="#1A2A40" strokeWidth="2" />
        <ellipse cx={cx} cy={cy} rx={rx} ry={ry} fill="#0A1628" stroke="#4A5D75" strokeWidth="1" />

        {/* Sections */}
        {STADIUM_SECTIONS.map((sec, i) => {
          const startAngle = sec.angle - Math.PI / 32;
          const endAngle = sec.angle + Math.PI / 32;
          const density = getZoneDensity(sec.id);
          const level = getZoneLevel(sec.id);
          const color = layer === 'crowd' ? getDensityColor(density) : '#1A2A40';
          const opacity = layer === 'crowd' ? (0.2 + density * 0.5) : 0.1;

          const x1 = cx + Math.cos(startAngle) * (rx - 40);
          const y1 = cy + Math.sin(startAngle) * (ry - 40);
          const x2 = cx + Math.cos(endAngle) * (rx - 40);
          const y2 = cy + Math.sin(endAngle) * (ry - 40);
          const x3 = cx + Math.cos(endAngle) * (rx - 80);
          const y3 = cy + Math.sin(endAngle) * (ry - 80);
          const x4 = cx + Math.cos(startAngle) * (rx - 80);
          const y4 = cy + Math.sin(startAngle) * (ry - 80);

          const isCritical = level === 'critical';

          return (
            <g
              key={sec.id}
              onClick={() => setSelectedZone(sec)}
              onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setSelectedZone(sec); } }}
              className="cursor-pointer"
              tabIndex={0}
              role="button"
              aria-label={`Section ${i + 1}, density level: ${level}`}
            >
              <polygon
                points={`${x1},${y1} ${x2},${y2} ${x3},${y3} ${x4},${y4}`}
                fill={color}
                fillOpacity={opacity}
                stroke="#1A2A40"
                strokeWidth="0.5"
              >
                {isCritical && (
                  <animate attributeName="fill-opacity" values="0.5;0.8;0.5" dur="1s" repeatCount="indefinite" />
                )}
              </polygon>
              <text
                x={cx + Math.cos(sec.angle) * (rx - 60)}
                y={cy + Math.sin(sec.angle) * (ry - 60)}
                fill="#8B9DB8"
                fontSize="6"
                textAnchor="middle"
                dominantBaseline="middle"
              >
                {i + 1}
              </text>
            </g>
          );
        })}

        {/* Gates */}
        {['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'].map((gate, i) => {
          const angle = (i / 8) * Math.PI * 2 - Math.PI / 2;
          const x = cx + Math.cos(angle) * (rx + 10);
          const y = cy + Math.sin(angle) * (ry + 10);
          return (
            <g key={`gate_${gate}`}>
              <circle cx={x} cy={y} r="8" fill="#FFD700" fillOpacity="0.3" stroke="#FFD700" strokeWidth="1" />
              <text x={x} y={y} fill="#FFD700" fontSize="8" textAnchor="middle" dominantBaseline="middle" fontWeight="bold">
                {gate}
              </text>
            </g>
          );
        })}

        {/* Amenities */}
        {layer === 'amenities' && AMENITIES.map((amenity) => (
          <g key={amenity.id}>
            <circle
              cx={(amenity.x / 100) * 400}
              cy={(amenity.y / 100) * 400}
              r="6"
              fill="#00B4D8"
              fillOpacity="0.5"
            />
            <text
              x={(amenity.x / 100) * 400}
              y={(amenity.y / 100) * 400 + 12}
              fill="#8B9DB8"
              fontSize="5"
              textAnchor="middle"
            >
              {amenity.name}
            </text>
          </g>
        ))}

        {/* User location dot */}
        <circle cx={cx} cy={cy + 40} r="6" fill="#00B4D8">
          <animate attributeName="r" values="6;10;6" dur="2s" repeatCount="indefinite" />
          <animate attributeName="fill-opacity" values="1;0.5;1" dur="2s" repeatCount="indefinite" />
        </circle>
        <circle cx={cx} cy={cy + 40} r="3" fill="#00B4D8" />

        {/* Field */}
        <ellipse cx={cx} cy={cy} rx={rx - 90} ry={ry - 55} fill="#0D3B1A" stroke="#1A5C28" strokeWidth="1" opacity="0.8" />
        <text x={cx} y={cy} fill="#1A5C28" fontSize="10" textAnchor="middle" dominantBaseline="middle" fontWeight="bold" opacity="0.5">
          FIELD
        </text>
      </svg>
    );
  };

  return (
    <div className="h-full flex flex-col" style={{ background: '#0A1628' }}>
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3 shrink-0">
        <button
          onClick={goBack}
          className="w-10 h-10 rounded-full flex items-center justify-center cursor-pointer shrink-0"
          style={{ background: '#111D2E', boxShadow: '4px 4px 8px #050A10, -4px -4px 8px #1A2A40' }}
          aria-label="Go back"
        >
          <ArrowLeft size={20} color="#F0F4F8" />
        </button>
        <h1 className="text-lg text-white font-semibold">Stadium Map</h1>
      </div>

      {/* Map Container — flex-1 + min-h-0 ensures it never grows beyond available space */}
      <div className="flex-1 min-h-0 px-4">
        <div
          className="w-full h-full rounded-2xl overflow-hidden p-3"
          style={{ background: '#111D2E', boxShadow: '8px 8px 16px #050A10, -8px -8px 16px #1A2A40' }}
        >
          {/* Aspect-ratio wrapper: keeps stadium square on all sizes */}
          <div className="w-full h-full flex items-center justify-center">
            <div
              style={{
                width: '100%',
                maxWidth: '100%',
                aspectRatio: '1 / 1',
                maxHeight: '100%',
              }}
            >
              {renderStadiumSVG()}
            </div>
          </div>
        </div>
      </div>

      {/* Legend */}
      {layer === 'crowd' && (
        <div className="px-4 py-2 shrink-0 flex items-center justify-center gap-3">
          {[
            { color: '#00C853', label: 'Low' },
            { color: '#FFC107', label: 'Med' },
            { color: '#FF9800', label: 'High' },
            { color: '#FF3D00', label: 'Critical' },
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-sm" style={{ background: item.color, opacity: 0.7 }} />
              <span style={{ color: '#8B9DB8', fontSize: 10 }}>{item.label}</span>
            </div>
          ))}
        </div>
      )}

      {/* Zone selected tooltip */}
      {selectedZone && (
        <div className="px-4 shrink-0">
          <div
            className="w-full px-4 py-2 rounded-xl flex items-center justify-between"
            style={{ background: '#111D2E' }}
          >
            <span style={{ color: '#FFD700', fontSize: 13, fontWeight: 600 }}>
              Section {selectedZone.name}
            </span>
            <button onClick={() => setSelectedZone(null)} style={{ color: '#8B9DB8', fontSize: 11 }} aria-label="Dismiss zone selection">
              ✕ Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Floating Controls */}
      <div className="px-4 pb-4 pt-2 space-y-3 shrink-0">
        {/* Layer Toggle */}
        <div className="flex gap-2">
          {['crowd', 'amenities', 'routes'].map((l) => (
            <button
              key={l}
              onClick={() => setLayer(l)}
              className="flex-1 py-2 rounded-xl text-xs font-medium capitalize cursor-pointer transition-all"
              style={{
                background: layer === l ? '#111D2E' : '#0A1628',
                boxShadow: layer === l
                  ? 'inset 4px 4px 8px #050A10, inset -4px -4px 8px #1A2A40'
                  : '4px 4px 8px #050A10, -4px -4px 8px #1A2A40',
                color: layer === l ? '#FFD700' : '#8B9DB8',
              }}
              aria-label={`${l.charAt(0).toUpperCase() + l.slice(1)} layer`}
              aria-pressed={layer === l}
            >
              {l}
            </button>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2">
          <motion.button
            whileTap={{ scale: 0.98 }}
            onClick={() => navigateTo('navigation')}
            className="flex-1 py-3 rounded-xl flex items-center justify-center gap-2 cursor-pointer"
            style={{ background: '#FFD700', color: '#0A1628', fontWeight: 600, fontSize: 14 }}
            aria-label="Navigate to destination"
          >
            <Navigation size={18} />
            Navigate to...
          </motion.button>
          <motion.button
            whileTap={{ scale: 0.9 }}
            onClick={() => setWheelchairMode(!wheelchairMode)}
            className="w-12 h-12 rounded-full flex items-center justify-center cursor-pointer shrink-0"
            style={{
              background: wheelchairMode ? '#00B4D8' : '#111D2E',
              boxShadow: '4px 4px 8px #050A10, -4px -4px 8px #1A2A40',
            }}
            aria-label={`Wheelchair routing: ${wheelchairMode ? 'enabled' : 'disabled'}`}
            aria-pressed={wheelchairMode}
          >
            <Accessibility size={20} color={wheelchairMode ? '#FFFFFF' : '#8B9DB8'} />
          </motion.button>
          <motion.button
            whileTap={{ scale: 0.9 }}
            onClick={() => setCrowdAvoid(!crowdAvoid)}
            className="w-12 h-12 rounded-full flex items-center justify-center cursor-pointer shrink-0"
            style={{
              background: crowdAvoid ? '#00C853' : '#111D2E',
              boxShadow: '4px 4px 8px #050A10, -4px -4px 8px #1A2A40',
            }}
            aria-label={`Crowd avoidance: ${crowdAvoid ? 'enabled' : 'disabled'}`}
            aria-pressed={crowdAvoid}
          >
            <Eye size={20} color={crowdAvoid ? '#FFFFFF' : '#8B9DB8'} />
          </motion.button>
        </div>
      </div>
    </div>
  );
};
