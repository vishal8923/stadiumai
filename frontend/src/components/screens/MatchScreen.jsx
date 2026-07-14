import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Clock, Target, Activity } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { api } from '@/utils/api';
import { MOCK_MATCH_DATA } from '@/utils/constants';
import { ProgressBar } from '@/components/ui/ProgressBar';

const TABS = ['Live', 'Lineups', 'Stats', 'Timeline'];

export const MatchScreen = () => {
  const goBack = useAppStore((s) => s.goBack);
  const matchData = useAppStore((s) => s.matchData);
  const setMatchData = useAppStore((s) => s.setMatchData);
  const [activeTab, setActiveTab] = useState('Live');
  const [time, setTime] = useState({ min: 72, sec: 14 });

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
  }, []);

  useEffect(() => {
    const timer = setInterval(() => {
      setTime((t) => {
        let { min, sec } = t;
        sec++;
        if (sec >= 60) { sec = 0; min++; }
        return { min, sec };
      });
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const match = matchData || MOCK_MATCH_DATA;

  const lineups = {
    home: [
      { name: 'Turner', pos: 'GK', num: 1 },
      { name: 'Dest', pos: 'DF', num: 2 },
      { name: 'Ream', pos: 'DF', num: 3 },
      { name: 'Robinson', pos: 'DF', num: 5 },
      { name: 'Musah', pos: 'MF', num: 6 },
      { name: 'McKennie', pos: 'MF', num: 8 },
      { name: 'Pulisic', pos: 'FW', num: 10 },
      { name: 'Weah', pos: 'FW', num: 21 },
    ],
    away: [
      { name: 'Alisson', pos: 'GK', num: 1 },
      { name: 'Militao', pos: 'DF', num: 3 },
      { name: 'Marquinhos', pos: 'DF', num: 4 },
      { name: 'Casemiro', pos: 'MF', num: 5 },
      { name: 'Neymar', pos: 'FW', num: 10 },
      { name: 'Vinicius', pos: 'FW', num: 20 },
      { name: 'Rodrygo', pos: 'FW', num: 21 },
      { name: 'Paqueta', pos: 'MF', num: 7 },
    ],
  };

  const stats = match.stats || MOCK_MATCH_DATA.stats;

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
        <h1 className="text-h1 text-stadium-text font-semibold">Match</h1>
      </div>

      {/* Scoreboard */}
      <div
        className="mx-4 p-5 rounded-neo-card mb-4"
        style={{ background: '#111D2E', boxShadow: '8px 8px 16px #050A10, -8px -8px 16px #1A2A40' }}
      >
        <div className="flex items-center justify-between">
          <div className="flex flex-col items-center gap-1">
            <span className="text-4xl">{match.home_team?.flag || '🇺🇸'}</span>
            <span className="text-stadium-text font-semibold text-sm">{match.home_team?.name || 'USA'}</span>
          </div>
          <div className="flex flex-col items-center">
            <span className="text-score text-stadium-gold font-bold">
              {match.home_team?.score ?? 2} - {match.away_team?.score ?? 1}
            </span>
            <div className="flex items-center gap-1 mt-1">
              <span className="w-2 h-2 rounded-full bg-stadium-red animate-pulse" />
              <span className="text-stadium-text-secondary text-sm font-mono">
                {String(time.min).padStart(2, '0')}:{String(time.sec).padStart(2, '0')}
              </span>
            </div>
          </div>
          <div className="flex flex-col items-center gap-1">
            <span className="text-4xl">{match.away_team?.flag || '🇧🇷'}</span>
            <span className="text-stadium-text font-semibold text-sm">{match.away_team?.name || 'BRA'}</span>
          </div>
        </div>

        {/* Possession Bar */}
        <div className="mt-4">
          <div className="flex justify-between text-xs text-stadium-text-secondary mb-1">
            <span>Possession</span>
          </div>
          <div className="h-3 rounded-full overflow-hidden flex">
            <div className="h-full bg-stadium-blue flex items-center justify-center" style={{ width: `${match.possession?.home ?? 55}%` }}>
              <span className="text-[9px] text-white font-bold">{match.possession?.home ?? 55}%</span>
            </div>
            <div className="h-full bg-stadium-green flex items-center justify-center" style={{ width: `${match.possession?.away ?? 45}%` }}>
              <span className="text-[9px] text-white font-bold">{match.possession?.away ?? 45}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex px-4 mb-4">
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className="flex-1 py-2 text-sm font-medium text-center cursor-pointer transition-all"
            style={{
              color: activeTab === tab ? '#FFD700' : '#4A5D75',
              borderBottom: activeTab === tab ? '2px solid #FFD700' : '2px solid transparent',
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto px-4 pb-4">
        <AnimatePresence mode="wait">
          {activeTab === 'Live' && (
            <motion.div key="live" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-3">
              {match.events?.map((event, i) => (
                <div
                  key={i}
                  className="flex items-start gap-3 p-3 rounded-neo-input"
                  style={{ background: '#111D2E', boxShadow: '4px 4px 8px #050A10, -4px -4px 8px #1A2A40' }}
                >
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
                    style={{ background: '#070F1A' }}
                  >
                    {event.type === 'goal' && <Target size={16} color="#FFD700" />}
                    {event.type === 'yellow' && <div className="w-3 h-4 bg-yellow-400 rounded-sm" />}
                    {event.type === 'red' && <div className="w-3 h-4 bg-red-500 rounded-sm" />}
                    {event.type === 'substitution' && <Activity size={16} color="#00B4D8" />}
                    {event.type === 'halftime' && <Clock size={16} color="#8B9DB8" />}
                  </div>
                  <div>
                    <p className="text-stadium-text-secondary text-xs">{event.time}</p>
                    <p className="text-stadium-text text-sm">{event.description}</p>
                  </div>
                </div>
              ))}
            </motion.div>
          )}

          {activeTab === 'Lineups' && (
            <motion.div key="lineups" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="grid grid-cols-2 gap-4">
              {['home', 'away'].map((side) => (
                <div key={side}>
                  <p className="text-stadium-text-secondary text-xs font-semibold mb-2 uppercase">{side}</p>
                  <div className="space-y-2">
                    {lineups[side].map((player) => (
                      <div
                        key={player.num}
                        className="flex items-center gap-2 p-2 rounded-neo-input"
                        style={{ background: '#111D2E', boxShadow: '4px 4px 8px #050A10, -4px -4px 8px #1A2A40' }}
                      >
                        <span className="text-stadium-gold font-bold text-sm w-6">{player.num}</span>
                        <div>
                          <p className="text-stadium-text text-xs font-medium">{player.name}</p>
                          <p className="text-stadium-text-tertiary text-[10px]">{player.pos}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </motion.div>
          )}

          {activeTab === 'Stats' && (
            <motion.div key="stats" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-4">
              {Object.entries(stats).map(([key, val]) => (
                <div key={key}>
                  <div className="flex justify-between text-xs text-stadium-text-secondary mb-1 capitalize">
                    <span>{val.home}</span>
                    <span>{key}</span>
                    <span>{val.away}</span>
                  </div>
                  <div className="h-4 rounded-full overflow-hidden flex">
                    <div
                      className="h-full bg-stadium-blue flex items-center justify-end pr-1"
                      style={{ width: `${(val.home / (val.home + val.away)) * 100}%` }}
                    />
                    <div
                      className="h-full bg-stadium-green"
                      style={{ width: `${(val.away / (val.home + val.away)) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </motion.div>
          )}

          {activeTab === 'Timeline' && (
            <motion.div key="timeline" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="relative pl-4">
              <div className="absolute left-4 top-0 bottom-0 w-0.5" style={{ background: '#1A2A40' }} />
              {match.events?.map((event, i) => (
                <div key={i} className="relative pb-4 pl-6">
                  <div
                    className="absolute left-[11px] w-3 h-3 rounded-full"
                    style={{
                      background: event.type === 'goal' ? '#FFD700' : event.type === 'yellow' ? '#FFC107' : '#4A5D75',
                      top: 4,
                    }}
                  />
                  <p className="text-stadium-text-secondary text-xs">{event.time}</p>
                  <p className="text-stadium-text text-sm">{event.description}</p>
                </div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};
