import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, AlertTriangle, Users, MessageSquare, Clock, TrendingUp } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { useCrowdPolling } from '@/hooks/useCrowdPolling';
import { api } from '@/utils/api';
import { getDensityColor } from '@/utils/formatters';

const SEVERITY_CONFIG = {
  critical: { color: '#EF4444', bg: 'rgba(239, 68, 68, 0.12)' },
  high: { color: '#F59E0B', bg: 'rgba(245, 158, 11, 0.12)' },
  medium: { color: '#F59E0B', bg: 'rgba(245, 158, 11, 0.12)' },
  low: { color: '#10B981', bg: 'rgba(16, 185, 129, 0.12)' },
};

const STATUS_CONFIG = {
  reported: { color: '#5A6B7C', bg: 'rgba(90, 107, 124, 0.12)' },
  dispatched: { color: '#06B6D4', bg: 'rgba(6, 182, 212, 0.12)' },
  resolved: { color: '#10B981', bg: 'rgba(16, 185, 129, 0.12)' },
};

export const DashboardScreen = () => {
  const goBack = useAppStore((s) => s.goBack);
  const crowdData = useAppStore((s) => s.crowdData);
  const [incidents, setIncidents] = useState([]);
  const [stats, setStats] = useState({ activeIncidents: 12, crowdLevel: 'Medium', aiQueries: 1247, avgResponse: 1.2 });
  const [filter, setFilter] = useState('all');

  useCrowdPolling(30000);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const res = await api.get('/api/v1/admin/dashboard');
        setStats(res.data);
      } catch {
        setStats({ activeIncidents: 12, crowdLevel: 'Medium', aiQueries: 1247, avgResponse: 1.2 });
      }
    };
    fetchDashboard();
  }, []);

  useEffect(() => {
    const fetchIncidents = async () => {
      try {
        const res = await api.get('/api/v1/admin/incidents');
        setIncidents(res.data.incidents || []);
      } catch {
        setIncidents([
          { id: 'INC-001', type: 'medical', location: 'Gate C', severity: 'high', status: 'dispatched', assigned: 'Team A', time: '2 min ago' },
          { id: 'INC-002', type: 'security', location: 'Section 12', severity: 'medium', status: 'reported', assigned: '-', time: '5 min ago' },
          { id: 'INC-003', type: 'crowd', location: 'Food Court N', severity: 'critical', status: 'dispatched', assigned: 'Team B', time: '1 min ago' },
          { id: 'INC-004', type: 'medical', location: 'Gate A', severity: 'low', status: 'resolved', assigned: 'Team A', time: '15 min ago' },
          { id: 'INC-005', type: 'infrastructure', location: 'Restroom 2', severity: 'medium', status: 'reported', assigned: '-', time: '8 min ago' },
        ]);
      }
    };
    fetchIncidents();
  }, []);

  const filteredIncidents = filter === 'all' ? incidents : incidents.filter((i) => i.status === filter);

  const statCards = [
    { label: 'Active Incidents', value: stats.activeIncidents, icon: AlertTriangle, color: stats.activeIncidents > 5 ? '#EF4444' : '#10B981' },
    { label: 'Crowd Status', value: stats.crowdLevel, icon: Users, color: '#DAA520' },
    { label: 'Today AI Queries', value: stats.aiQueries_today || stats.aiQueries?.toLocaleString(), icon: MessageSquare, color: '#06B6D4' },
    { label: 'Avg Dispatch Wait', value: `${stats.avg_response_time || stats.avgResponse}m`, icon: Clock, color: '#10B981' },
  ];

  return (
    <div className="h-full flex flex-col overflow-hidden" style={{ background: '#F8F5EF' }}>
      
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
        <div>
          <h1 className="text-xl text-[#1A242F] font-bold tracking-tight">Operations Dashboard</h1>
          <p className="text-[10px] text-[#5A6B7C] uppercase font-bold tracking-wider mt-0.5">Admin Management Control</p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
        <div className="max-w-7xl mx-auto space-y-6">

          {/* Stats Row: 4 Columns on md/lg */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {statCards.map((card) => {
              const Icon = card.icon;
              return (
                <div
                  key={card.label}
                  className="p-5 rounded-2xl glass-card flex flex-col justify-between"
                  style={{ background: 'rgba(255, 255, 255, 0.95)' }}
                >
                  <div className="w-9 h-9 rounded-full flex items-center justify-center bg-gray-50 border border-gray-100 mb-4">
                    <Icon size={18} color={card.color} />
                  </div>
                  <div>
                    <p className="text-2xl font-black tracking-tight" style={{ color: card.color }}>{card.value}</p>
                    <p className="text-[#5A6B7C] text-xs font-semibold mt-1 uppercase tracking-wider">{card.label}</p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Dashboard Main Grid: Split Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Left 2/3: Active Incidents Table */}
            <div className="lg:col-span-2 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-base text-[#1A242F] font-bold tracking-tight">Operations Incidents</h2>
                  <p className="text-[10px] text-[#5A6B7C] uppercase tracking-wide">Real-time safety and medical reports</p>
                </div>
                
                <select
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                  className="bg-white text-[#5A6B7C] text-xs px-3 py-1.5 rounded-xl cursor-pointer outline-none border border-gray-200 shadow-sm"
                  aria-label="Filter incidents by status"
                >
                  <option value="all">All Incidents</option>
                  <option value="reported">Reported</option>
                  <option value="dispatched">Dispatched</option>
                  <option value="resolved">Resolved</option>
                </select>
              </div>

              <div className="space-y-3">
                {filteredIncidents.length === 0 ? (
                  <div className="p-8 text-center text-[#5A6B7C] text-sm bg-white/50 rounded-2xl border border-dashed border-gray-300">
                    No matching incidents found.
                  </div>
                ) : (
                  filteredIncidents.map((inc) => {
                    const sev = SEVERITY_CONFIG[inc.severity] || SEVERITY_CONFIG.medium;
                    const stat = STATUS_CONFIG[inc.status] || STATUS_CONFIG.reported;
                    return (
                      <motion.div
                        key={inc.id}
                        whileHover={{ scale: 1.005 }}
                        className="p-4 rounded-2xl glass-card flex items-center justify-between"
                        style={{ background: 'rgba(255, 255, 255, 0.95)' }}
                      >
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] text-[#5A6B7C] font-mono tracking-wider font-bold">{inc.id}</span>
                            <span
                              className="px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider"
                              style={{ background: sev.bg, color: sev.color }}
                            >
                              {inc.severity}
                            </span>
                          </div>
                          <p className="text-[#1A242F] font-bold text-sm capitalize">{inc.type} Report at {inc.location}</p>
                          <div className="flex items-center gap-3 text-[11px] text-[#5A6B7C] pt-0.5">
                            <span>Officer Assigned: <strong className="text-gray-700">{inc.assigned || 'None'}</strong></span>
                            <span>•</span>
                            <span>{inc.time}</span>
                          </div>
                        </div>

                        <span
                          className="px-2.5 py-1 rounded-xl text-[10px] font-extrabold uppercase tracking-widest"
                          style={{ background: stat.bg, color: stat.color }}
                        >
                          {inc.status}
                        </span>
                      </motion.div>
                    );
                  })
                )}
              </div>
            </div>

            {/* Right 1/3: Crowd Heatmap Preview */}
            <div className="space-y-4">
              <div>
                <h2 className="text-base text-[#1A242F] font-bold tracking-tight">Live Zone Congestion</h2>
                <p className="text-[10px] text-[#5A6B7C] uppercase tracking-wide">Stadium sector crowd breakdowns</p>
              </div>

              <div
                className="p-5 rounded-3xl glass-card space-y-4"
                style={{ background: 'rgba(255, 255, 255, 0.95)' }}
              >
                <div className="space-y-2.5">
                  {crowdData?.zones?.slice(0, 8).map((zone) => {
                    const pct = Math.round(zone.current_density * 100);
                    return (
                      <div key={zone.zone_id} className="space-y-1">
                        <div className="flex items-center justify-between text-xs font-semibold">
                          <span className="capitalize text-[#1A242F]">{zone.zone_id.replace('_', ' ')}</span>
                          <span style={{ color: getDensityColor(zone.density) }}>{pct}%</span>
                        </div>
                        <div className="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
                          <div 
                            className="h-full rounded-full" 
                            style={{ 
                              width: `${pct}%`,
                              backgroundColor: getDensityColor(zone.density) 
                            }} 
                          />
                        </div>
                      </div>
                    );
                  }) || (
                    <p className="text-[#5A6B7C] text-xs">Awaiting crowd metrics...</p>
                  )}
                </div>

                <div
                  className="p-3 rounded-2xl flex items-center gap-2 border border-[#EF4444]/10 bg-[#EF4444]/5"
                >
                  <TrendingUp size={16} color="#EF4444" />
                  <p className="text-[#EF4444] text-[11px] font-semibold leading-snug">Gate C predicted to hit critical volume in 10 minutes</p>
                </div>
              </div>
            </div>

          </div>

        </div>
      </div>
    </div>
  );
};
