import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { Compass, Globe, Users, ShieldAlert, MapPin } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { useCrowdPolling } from '@/hooks/useCrowdPolling';
import { Header } from '@/components/sections/Header';
import { AnimatedOrb } from '@/components/ui/AnimatedOrb';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { containerVariants, itemVariants } from '@/utils/animations';
import { api } from '@/utils/api';
import { MOCK_MATCH_DATA } from '@/utils/constants';

const QUICK_ACTIONS = [
  { id: 'navigate', icon: Compass, color: '#00B4D8', label: 'Navigate', sublabel: 'To your seat', screen: 'map' },
  { id: 'translate', icon: Globe, color: '#FFD700', label: 'Translate', sublabel: '50+ languages', screen: 'chat' },
  { id: 'crowd', icon: Users, color: '#00C853', label: 'Crowd Status', sublabel: 'Live density map', screen: 'map' },
  { id: 'report', icon: ShieldAlert, color: '#FF3D00', label: 'Report Issue', sublabel: 'Help & safety', screen: 'incident' },
];

export const HomeScreen = () => {
  const navigateTo = useAppStore((s) => s.navigateTo);
  const crowdData = useAppStore((s) => s.crowdData);
  const setMatchData = useAppStore((s) => s.setMatchData);
  const matchData = useAppStore((s) => s.matchData);

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
  }, []);

  const match = matchData || MOCK_MATCH_DATA;
  const hasCriticalZone = crowdData?.zones?.some((z) => z.level === 'critical' || z.level === 'high');
  const criticalZone = crowdData?.zones?.find((z) => z.level === 'critical');

  return (
    <motion.div
      className="h-full flex flex-col overflow-hidden"
      style={{ background: '#0A1628' }}
      variants={containerVariants}
      initial="hidden"
      animate="show"
    >
      <motion.div variants={itemVariants}>
        <Header />
      </motion.div>

      <div className="flex-1 overflow-y-auto pb-20 px-4">
        {/* AI Companion Orb */}
        <motion.div variants={itemVariants} className="flex flex-col items-center py-6">
          <AnimatedOrb size={180} onClick={() => navigateTo('chat')} />
          <p className="text-stadium-text-secondary text-xs font-medium mt-6">Tap to ask StadiumAI</p>
        </motion.div>

        {/* Quick Action Grid */}
        <motion.div variants={itemVariants} className="grid grid-cols-2 gap-4 mb-4">
          {QUICK_ACTIONS.map((action) => {
            const Icon = action.icon;
            return (
              <motion.button
                key={action.id}
                whileTap={{ scale: 0.98 }}
                onClick={() => navigateTo(action.screen)}
                className="relative flex flex-col justify-between p-5 rounded-neo-button cursor-pointer aspect-square"
                style={{
                  background: '#111D2E',
                  boxShadow: '8px 8px 16px #050A10, -8px -8px 16px #1A2A40',
                }}
              >
                {action.id === 'crowd' && (
                  <span
                    className="absolute top-3 right-3 px-2 py-0.5 rounded-full text-[9px] font-bold text-white"
                    style={{ background: '#FF3D00' }}
                  >
                    LIVE
                  </span>
                )}
                <div
                  className="w-10 h-10 rounded-full flex items-center justify-center"
                  style={{
                    background: '#070F1A',
                    boxShadow: 'inset 4px 4px 8px #050A10, inset -4px -4px 8px #1A2A40',
                  }}
                >
                  <Icon size={20} color={action.color} />
                </div>
                <div>
                  <p className="text-stadium-text font-semibold text-sm">{action.label}</p>
                  <p className="text-stadium-text-secondary text-xs">{action.sublabel}</p>
                </div>
              </motion.button>
            );
          })}
        </motion.div>

        {/* Live Match Card */}
        {match && (
          <motion.div
            variants={itemVariants}
            className="mb-4 p-5 rounded-neo-card cursor-pointer"
            style={{
              background: '#111D2E',
              boxShadow: '8px 8px 16px #050A10, -8px -8px 16px #1A2A40',
            }}
            whileTap={{ scale: 0.98 }}
            onClick={() => navigateTo('match')}
          >
            <div className="flex items-center gap-2 mb-3">
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold text-white" style={{ background: '#FF3D00' }}>
                LIVE MATCH
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex flex-col items-center gap-1">
                <span className="text-3xl">{match.home_team?.flag || '🇺🇸'}</span>
                <span className="text-stadium-text font-semibold text-sm">{match.home_team?.name || 'USA'}</span>
              </div>
              <div className="flex flex-col items-center">
                <span className="text-score text-stadium-gold font-bold">
                  {match.home_team?.score ?? 2} - {match.away_team?.score ?? 1}
                </span>
                <span className="text-stadium-text-secondary text-sm font-medium mt-1">
                  {match.minute != null ? `${String(match.minute).padStart(2, '0')}:${String(match.second ?? 0).padStart(2, '0')}` : '72:14'}
                </span>
              </div>
              <div className="flex flex-col items-center gap-1">
                <span className="text-3xl">{match.away_team?.flag || '🇧🇷'}</span>
                <span className="text-stadium-text font-semibold text-sm">{match.away_team?.name || 'BRA'}</span>
              </div>
            </div>
            <div className="mt-3">
              <ProgressBar
                progress={match.minute != null ? (match.minute / 90) * 100 : 80}
                color="#FFD700"
                height={4}
              />
            </div>
            <p className="text-stadium-text-tertiary text-xs mt-2 text-center">
              {match.stadium || 'MetLife Stadium'} • Section {match.venue || '12B'}
            </p>
          </motion.div>
        )}

        {/* Crowd Alert Banner */}
        {hasCriticalZone && (
          <motion.div
            variants={itemVariants}
            whileTap={{ scale: 0.98 }}
            className="mb-4 p-4 rounded-neo-input flex items-center gap-3 cursor-pointer"
            style={{
              background: '#070F1A',
              boxShadow: 'inset 6px 6px 12px #050A10, inset -6px -6px 12px #1A2A40',
              borderLeft: '4px solid #FF3D00',
            }}
            onClick={() => navigateTo('map')}
          >
            <ShieldAlert size={24} color="#FF3D00" />
            <div className="flex-1">
              <p className="text-stadium-text font-medium text-sm">
                {criticalZone
                  ? `${criticalZone.zone_id.replace('_', ' ').toUpperCase()} is ${criticalZone.level}. Use alternate route.`
                  : 'Some areas are crowded. Check the map for better routes.'}
              </p>
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};
