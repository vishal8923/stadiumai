import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Compass, 
  Globe, 
  Users, 
  ShieldAlert, 
  Brain, 
  Clock, 
  Bus, 
  Leaf, 
  AlertTriangle, 
  Activity, 
  ChevronRight
} from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { useCrowdPolling } from '@/hooks/useCrowdPolling';
import { Header } from '@/components/sections/Header';
import { AnimatedOrb } from '@/components/ui/AnimatedOrb';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { containerVariants, itemVariants } from '@/utils/animations';
import { api } from '@/utils/api';
import { MOCK_MATCH_DATA } from '@/utils/constants';

const QUICK_ACTIONS = [
  { id: 'navigate', icon: Compass, color: '#00B4D8', label: 'Seat Navigation', sublabel: 'Fastest seat routes', screen: 'map' },
  { id: 'translate', icon: Globe, color: '#DAA520', label: 'Gemini Translator', sublabel: 'Over 50+ languages', screen: 'chat' },
  { id: 'crowd', icon: Users, color: '#10B981', label: 'Crowd Status', sublabel: 'Live density updates', screen: 'map' },
  { id: 'report', icon: ShieldAlert, color: '#EF4444', label: 'Report Incident', sublabel: 'Immediate safety help', screen: 'incident' },
];

const getTeamFlag = (teamName) => {
  if (!teamName) return '🏳️';
  const name = teamName.toUpperCase();
  if (name.includes('USA') || name.includes('UNITED STATES')) return '🇺🇸';
  if (name.includes('BRA') || name.includes('BRAZIL')) return '🇧🇷';
  if (name.includes('MEX') || name.includes('MEXICO')) return '🇲🇽';
  if (name.includes('CAN') || name.includes('CANADA')) return '🇨🇦';
  if (name.includes('ARG') || name.includes('ARGENTINA')) return '🇦🇷';
  if (name.includes('FRA') || name.includes('FRANCE')) return '🇫🇷';
  if (name.includes('GER') || name.includes('GERMANY')) return '🇩🇪';
  if (name.includes('ENG') || name.includes('ENGLAND')) return '🏴󠁧󠁢󠁥󠁮󠁧󠁿';
  if (name.includes('ESP') || name.includes('SPAIN')) return '🇪🇸';
  if (name.includes('ITA') || name.includes('ITALY')) return '🇮🇹';
  return '🏳️';
};

export const HomeScreen = () => {
  const navigateTo = useAppStore((s) => s.navigateTo);
  const crowdData = useAppStore((s) => s.crowdData);
  const setMatchData = useAppStore((s) => s.setMatchData);
  const matchData = useAppStore((s) => s.matchData);

  const [adminDashboard, setAdminDashboard] = useState(null);
  const [elevatorAccess, setElevatorAccess] = useState(null);
  const [transitOptions, setTransitOptions] = useState(null);

  useCrowdPolling(30000);

  useEffect(() => {
    const fetchMatch = async () => {
      try {
        const res = await api.get('/api/v1/match/current');
        setMatchData(res.data);
      } catch {
        setMatchData(MOCK_MATCH_DATA);
      }
    };
    fetchMatch();
    const timer = setInterval(fetchMatch, 30000);
    return () => clearInterval(timer);
    }, [setMatchData]);

  useEffect(() => {
    const fetchExtraData = async () => {
      try {
        const adminRes = await api.get('/api/v1/admin/dashboard');
        setAdminDashboard(adminRes.data);
      } catch (e) {
        console.error("Error fetching admin dashboard", e);
      }
      try {
        const accRes = await api.get('/api/v1/accessibility/elevator');
        setElevatorAccess(accRes.data);
      } catch (e) {
        console.error("Error fetching accessibility services", e);
      }
      try {
        const transRes = await api.get('/api/v1/transport?location=gate_a');
        setTransitOptions(transRes.data);
      } catch (e) {
        console.error("Error fetching transit details", e);
      }
    };
    fetchExtraData();
    const interval = setInterval(fetchExtraData, 30000);
    return () => clearInterval(interval);
    }, []);

  const match = matchData || MOCK_MATCH_DATA;
  const zones = crowdData?.zones || [];
  
  // Computed Occupancy based on real zone densities
  const avgDensity = zones.length > 0 
    ? zones.reduce((acc, z) => acc + z.current_density, 0) / zones.length 
    : 0.65;
  const occupancyPercentage = Math.round(avgDensity * 100);

  // Active incidents & Alerts from backend
  const activeAlerts = adminDashboard?.alerts || [
    { id: "alert_1", title: "Crowd Congestion", message: "Heavy bottleneck building up at Gate B.", severity: "warning" }
  ];

  // AI recommendations based on density
  const getAIRecommendations = () => {
    const criticalZones = zones.filter(z => z.level === 'critical' || z.level === 'high');
    const recs = [];
    if (criticalZones.length > 0) {
      recs.push(`Avoid ${criticalZones[0].zone_id.replace('_', ' ')}: high density detected.`);
      recs.push(`Consider using alternate corridor navigation routing.`);
    } else {
      recs.push("All gates are flowing smoothly. Safe travels!");
    }
    if (elevatorAccess?.wait_time_minutes > 5) {
      recs.push(`Elevator wait times are currently ${elevatorAccess.wait_time_minutes}m. Ramps might be faster.`);
    }
    return recs;
  };

  const aiRecs = getAIRecommendations();

  return (
    <motion.div
      className="h-full flex flex-col overflow-hidden"
      style={{ background: '#F8F5EF' }}
      variants={containerVariants}
      initial="hidden"
      animate="show"
    >
      <motion.div variants={itemVariants}>
        <Header />
      </motion.div>

      <div className="flex-1 overflow-y-auto px-6 pb-12 pt-2">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* LEFT 2/3 COLUMN */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Live Match Hero Card */}
            {match && (
              <motion.div
                variants={itemVariants}
                className="p-6 rounded-3xl glass-card cursor-pointer relative overflow-hidden"
                style={{
                  background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(253, 250, 242, 0.92))',
                }}
                whileHover={{ scale: 1.005 }}
                onClick={() => navigateTo('match')}
              >
                <div className="absolute top-0 left-0 w-2 h-full bg-[#EF4444]" />
                
                <div className="flex items-center justify-between mb-4 pl-2">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#EF4444] animate-ping" />
                    <span className="text-[10px] font-bold text-[#EF4444] uppercase tracking-wider">LIVE BROADCAST</span>
                  </div>
                  <span className="text-xs text-[#5A6B7C] font-semibold">{match.stadium || 'MetLife Stadium'}</span>
                </div>

                <div className="flex items-center justify-around py-4">
                  <div className="flex flex-col items-center gap-2 w-1/3 text-center">
                    <span className="text-5xl filter drop-shadow">{getTeamFlag(match.team_a)}</span>
                    <span className="text-[#1A242F] font-bold text-base tracking-wide">{match.team_a || 'USA'}</span>
                  </div>

                  <div className="flex flex-col items-center justify-center w-1/3">
                    <span className="text-4xl font-extrabold text-[#1A242F] tracking-wider">
                      {match.score_a ?? 2} — {match.score_b ?? 1}
                    </span>
                    <div className="mt-2 px-2.5 py-0.5 rounded-full bg-[#EF4444]/10 text-[#EF4444] font-bold text-xs">
                      {match.status === 'live' ? '72:14' : 'Final'}
                    </div>
                  </div>

                  <div className="flex flex-col items-center gap-2 w-1/3 text-center">
                    <span className="text-5xl filter drop-shadow">{getTeamFlag(match.team_b)}</span>
                    <span className="text-[#1A242F] font-bold text-base tracking-wide">{match.team_b || 'BRA'}</span>
                  </div>
                </div>

                {/* Match Stats Mini Grid */}
                {match.stats && (
                  <div className="grid grid-cols-3 gap-2 py-3 px-4 rounded-xl bg-gray-50/50 border border-gray-100 text-center mt-3">
                    <div>
                      <p className="text-[10px] uppercase font-bold text-[#5A6B7C]">Possession</p>
                      <p className="text-sm font-extrabold text-[#1A242F]">{match.stats.possession_a || 52}% - {match.stats.possession_b || 48}%</p>
                    </div>
                    <div>
                      <p className="text-[10px] uppercase font-bold text-[#5A6B7C]">Shots (On Goal)</p>
                      <p className="text-sm font-extrabold text-[#1A242F]">{match.stats.shots_a || 8} - {match.stats.shots_b || 5}</p>
                    </div>
                    <div>
                      <p className="text-[10px] uppercase font-bold text-[#5A6B7C]">Fouls</p>
                      <p className="text-sm font-extrabold text-[#1A242F]">{match.stats.fouls_a || 11} - {match.stats.fouls_b || 9}</p>
                    </div>
                  </div>
                )}

                {/* Match Timeline Preview */}
                {match.timeline && match.timeline.length > 0 && (
                  <div className="mt-4 border-t border-gray-100/80 pt-4 pl-2">
                    <p className="text-[10px] uppercase font-bold text-[#5A6B7C] mb-2 tracking-wider flex items-center gap-1.5">
                      <Activity size={12} className="text-[#EF4444]" /> Match Highlights
                    </p>
                    <div className="space-y-1.5">
                      {match.timeline.slice(-2).map((evt, idx) => (
                        <div key={idx} className="flex items-center justify-between text-xs text-[#5A6B7C]">
                          <span>⚽ {evt.player} ({evt.team})</span>
                          <span className="font-semibold text-gray-800">{evt.minute}'</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            )}

            {/* Quick Actions Grid */}
            <motion.div variants={itemVariants} className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {QUICK_ACTIONS.map((action) => {
                const Icon = action.icon;
                return (
                  <motion.button
                    key={action.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => navigateTo(action.screen)}
                    className="relative flex flex-col justify-between p-5 rounded-2xl cursor-pointer aspect-square text-left glass-card"
                    style={{
                      background: 'rgba(255, 255, 255, 0.95)',
                    }}
                  >
                    {action.id === 'crowd' && (
                      <span className="absolute top-3 right-3 px-2 py-0.5 rounded-full text-[9px] font-bold text-white bg-[#EF4444]">
                        LIVE
                      </span>
                    )}
                    <div
                      className="w-10 h-10 rounded-full flex items-center justify-center bg-[#F8F5EF]"
                      style={{
                        border: '1px solid rgba(26, 36, 47, 0.05)',
                      }}
                    >
                      <Icon size={20} color={action.color} />
                    </div>
                    <div>
                      <p className="text-[#1A242F] font-bold text-sm leading-tight">{action.label}</p>
                      <p className="text-[#5A6B7C] text-[11px] mt-0.5 leading-snug">{action.sublabel}</p>
                    </div>
                  </motion.button>
                );
              })}
            </motion.div>

            {/* Crowd Overview & Stadium Heatmap Preview */}
            <motion.div
              variants={itemVariants}
              className="p-6 rounded-3xl glass-card flex flex-col md:flex-row gap-6 items-center"
            >
              {/* Heatmap graph visualization */}
              <div className="w-full md:w-1/2">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-bold text-sm text-[#1A242F] tracking-wide">Stadium Crowd Map</h3>
                  <span className="px-2 py-0.5 rounded bg-[#10B981]/10 text-[#10B981] text-[9px] font-extrabold tracking-wider uppercase">Live Analytics</span>
                </div>
                <div className="aspect-[4/3] w-full rounded-2xl bg-gray-100/50 border border-gray-200/60 overflow-hidden relative flex items-center justify-center p-4">
                  <svg viewBox="0 0 200 150" className="w-full h-full opacity-90">
                    <ellipse cx="100" cy="75" rx="80" ry="55" fill="none" stroke="#E5E7EB" strokeWidth="6" />
                    {/* Ring segment mock mapping to show density visually */}
                    {zones.slice(0, 8).map((zone, idx) => {
                      const angle = (idx / 8) * Math.PI * 2;
                      const x = 100 + Math.cos(angle) * 70;
                      const y = 75 + Math.sin(angle) * 45;
                      const color = zone.level === 'critical' ? '#EF4444' : zone.level === 'high' ? '#F59E0B' : '#10B981';
                      return (
                        <g key={zone.zone_id}>
                          <circle cx={x} cy={y} r="8" fill={color} fillOpacity="0.8" className="animate-pulse" />
                          <circle cx={x} cy={y} r="12" fill="none" stroke={color} strokeWidth="1.5" opacity="0.4" />
                        </g>
                      );
                    })}
                    <rect x="65" y="55" width="70" height="40" rx="4" fill="#EBE6D9" opacity="0.6" />
                    <text x="100" y="79" fill="#1A242F" fontSize="8" fontWeight="bold" textAnchor="middle">FIELD</text>
                  </svg>
                </div>
              </div>

              {/* Status List of specific Gates */}
              <div className="w-full md:w-1/2 space-y-3.5">
                <div>
                  <h4 className="font-bold text-xs uppercase tracking-wider text-[#5A6B7C] mb-2">Gate Entry Status</h4>
                  <div className="space-y-2">
                    {zones.filter(z => z.zone_id.includes('gate')).slice(0, 3).map((gate) => {
                      const density = Math.round(gate.current_density * 100);
                      const color = gate.level === 'critical' ? '#EF4444' : gate.level === 'high' ? '#F59E0B' : '#10B981';
                      return (
                        <div key={gate.zone_id} className="flex items-center justify-between text-xs py-1">
                          <span className="capitalize font-semibold text-[#1A242F]">{gate.zone_id.replace('_', ' ')}</span>
                          <div className="flex items-center gap-3">
                            <span className="text-[10px] font-bold text-gray-500">{density}% density</span>
                            <span 
                              className="w-2 h-2 rounded-full" 
                              style={{ backgroundColor: color }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div className="pt-3 border-t border-gray-100">
                  <h4 className="font-bold text-xs uppercase tracking-wider text-[#5A6B7C] mb-1.5">Concourses Density</h4>
                  <div className="flex flex-wrap gap-2">
                    {zones.filter(z => z.zone_id.includes('concourse')).slice(0, 4).map((concourse) => {
                      const color = concourse.level === 'critical' ? 'bg-[#EF4444]/10 text-[#EF4444]' : concourse.level === 'high' ? 'bg-[#F59E0B]/10 text-[#F59E0B]' : 'bg-[#10B981]/10 text-[#10B981]';
                      return (
                        <span key={concourse.zone_id} className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase ${color}`}>
                          {concourse.zone_id.replace('zone_', '').replace('_', ' ')}
                        </span>
                      );
                    })}
                  </div>
                </div>
              </div>
            </motion.div>

          </div>

          {/* RIGHT 1/3 SIDEBAR COLUMN */}
          <div className="space-y-6">
            
            {/* AI Assistant Concierge Card */}
            <motion.div
              variants={itemVariants}
              className="p-6 rounded-3xl text-white relative overflow-hidden"
              style={{
                background: 'linear-gradient(135deg, #0A1628, #111D2E)',
                boxShadow: '0 12px 30px rgba(10, 22, 40, 0.15)'
              }}
            >
              {/* Cyan overlay to represent AI theme */}
              <div className="absolute top-0 right-0 w-24 h-24 bg-[#06B6D4] rounded-full blur-3xl opacity-25 -mr-8 -mt-8" />
              
              <div className="flex items-center gap-2.5 mb-4">
                <Brain size={20} className="text-[#06B6D4]" />
                <h3 className="font-bold text-sm tracking-wide">StadiumAI Concierge</h3>
              </div>

              {/* Animated Orb Widget */}
              <div className="flex flex-col items-center py-3">
                <AnimatedOrb size={100} onClick={() => navigateTo('chat')} />
                <button 
                  onClick={() => navigateTo('chat')}
                  className="mt-4 px-4 py-2 bg-[#06B6D4] hover:bg-[#06B6D4]/90 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer"
                  aria-label="Ask AI Assistant"
                >
                  Ask AI Assistant <ChevronRight size={14} />
                </button>
              </div>

              {/* AI Quick Recommendations Panel */}
              <div className="mt-4 border-t border-gray-700/50 pt-4">
                <p className="text-[9px] uppercase font-bold text-gray-400 tracking-wider mb-2">Live AI Guidance</p>
                <div className="space-y-2">
                  {aiRecs.map((rec, idx) => (
                    <div key={idx} className="flex gap-2 text-xs text-gray-300">
                      <span className="text-[#06B6D4] font-bold">•</span>
                      <p className="leading-snug">{rec}</p>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>

            {/* Stadium Occupancy Card */}
            <motion.div
              variants={itemVariants}
              className="p-6 rounded-3xl glass-card"
            >
              <div className="flex items-center gap-2 mb-3">
                <Activity size={18} className="text-[#DAA520]" />
                <h3 className="font-bold text-sm text-[#1A242F] tracking-wide">Live Stadium Capacity</h3>
              </div>
              <div className="flex items-center justify-between gap-4">
                <div className="flex-1">
                  <span className="text-3xl font-extrabold text-[#1A242F] tracking-tight">{occupancyPercentage}%</span>
                  <p className="text-[#5A6B7C] text-[11px] mt-0.5">Approx. {Math.round(82000 * avgDensity).toLocaleString()} / 82,000 seats</p>
                </div>
                <div className="w-14 h-14">
                  <svg viewBox="0 0 36 36" className="w-full h-full">
                    <path
                      className="text-gray-100"
                      strokeWidth="3.5"
                      stroke="currentColor"
                      fill="none"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <path
                      className="text-[#DAA520]"
                      strokeWidth="3.5"
                      strokeDasharray={`${occupancyPercentage}, 100`}
                      strokeLinecap="round"
                      stroke="currentColor"
                      fill="none"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                  </svg>
                </div>
              </div>
              <div className="mt-3">
                <ProgressBar progress={occupancyPercentage} color="#DAA520" height={4} />
              </div>
            </motion.div>

            {/* Queue Waiting Time Card */}
            {elevatorAccess && (
              <motion.div
                variants={itemVariants}
                className="p-6 rounded-3xl glass-card"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Clock size={18} className="text-[#10B981]" />
                    <h3 className="font-bold text-sm text-[#1A242F] tracking-wide">Queue Waiting Times</h3>
                  </div>
                  <span className="px-2 py-0.5 rounded bg-[#10B981]/15 text-[#10B981] text-[9px] font-extrabold uppercase tracking-wide">Elevators</span>
                </div>
                
                <div className="space-y-3">
                  {elevatorAccess.services?.slice(0, 3).map((item) => (
                    <div key={item.id} className="flex items-center justify-between text-xs">
                      <div>
                        <p className="font-semibold text-[#1A242F]">{item.location}</p>
                        <p className="text-[9px] text-[#5A6B7C] uppercase tracking-wide mt-0.5">{item.status}</p>
                      </div>
                      <span className={`font-bold px-2 py-1 rounded-lg ${
                        item.wait_time_minutes > 5 ? 'bg-red-50 text-red-600' : 'bg-[#10B981]/10 text-[#10B981]'
                      }`}>
                        {item.wait_time_minutes} min
                      </span>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Transportation Schedules Widget */}
            {transitOptions && (
              <motion.div
                variants={itemVariants}
                className="p-6 rounded-3xl glass-card"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Bus size={18} className="text-[#00B4D8]" />
                    <h3 className="font-bold text-sm text-[#1A242F] tracking-wide">Transit & Shuttles</h3>
                  </div>
                  <span className="text-[9px] text-[#5A6B7C] font-bold uppercase tracking-wider">{transitOptions.traffic_level || 'Normal'} Traffic</span>
                </div>

                <div className="space-y-3">
                  {transitOptions.options?.slice(0, 2).map((opt) => (
                    <div key={opt.id} className="p-2.5 rounded-xl bg-gray-50 border border-gray-100 flex items-center justify-between text-xs">
                      <div>
                        <p className="font-bold capitalize text-[#1A242F]">{opt.mode} — {opt.destination}</p>
                        <p className="text-[10px] text-[#5A6B7C] mt-0.5">{opt.details}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-extrabold text-[#00B4D8]">{opt.eta_minutes} min</p>
                        <p className="text-[9px] text-gray-400 font-semibold uppercase">ETA</p>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Recent Safety Alerts Widget */}
            <motion.div
              variants={itemVariants}
              className="p-6 rounded-3xl glass-card"
            >
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle size={18} className="text-[#F59E0B]" />
                <h3 className="font-bold text-sm text-[#1A242F] tracking-wide">Operations Alerts</h3>
              </div>
              <div className="space-y-3">
                {activeAlerts.map((alert) => {
                  const isWarning = alert.severity === 'warning' || alert.severity === 'critical';
                  const border = isWarning ? 'border-l-4 border-[#EF4444]' : 'border-l-4 border-[#00B4D8]';
                  const bg = isWarning ? 'bg-[#EF4444]/5' : 'bg-[#00B4D8]/5';
                  return (
                    <div key={alert.id} className={`p-3 rounded-xl ${bg} ${border} text-xs`}>
                      <p className="font-bold text-[#1A242F]">{alert.title}</p>
                      <p className="text-[#5A6B7C] text-[11px] mt-1 leading-relaxed">{alert.message}</p>
                    </div>
                  );
                })}
              </div>
            </motion.div>

            {/* Sustainability Widget */}
            <motion.div
              variants={itemVariants}
              className="p-6 rounded-3xl glass-card"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Leaf size={18} className="text-[#10B981]" />
                  <h3 className="font-bold text-sm text-[#1A242F] tracking-wide">Eco-Waste Disposal</h3>
                </div>
                <span className="text-[9px] text-[#10B981] font-bold uppercase tracking-wider">World Cup Green</span>
              </div>
              <p className="text-[#5A6B7C] text-xs leading-relaxed mb-3">
                Dispose of cups in Green Compost, bottles in Blue Recycling, and food items in Landfill bins.
              </p>
              <button 
                onClick={() => navigateTo('sustainability')}
                className="w-full py-2.5 bg-[#10B981]/10 text-[#10B981] hover:bg-[#10B981]/15 rounded-xl text-xs font-bold transition-colors cursor-pointer"
                aria-label="Scan waste with AI camera"
              >
                Scan Waste with AI Camera
              </button>
            </motion.div>

          </div>

        </div>
      </div>
    </motion.div>
  );
};
