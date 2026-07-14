import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, AlertTriangle, Users, MessageSquare, Clock, ChevronDown, Check, TrendingUp } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { useCrowdPolling } from '@/hooks/useCrowdPolling';
import { api } from '@/utils/api';
import { getDensityColor } from '@/utils/formatters';

const SEVERITY_CONFIG = {
  critical: { color: '#FF3D00', bg: 'rgba(255, 61, 0, 0.15)' },
  high: { color: '#FF9800', bg: 'rgba(255, 152, 0, 0.15)' },
  medium: { color: '#FFC107', bg: 'rgba(255, 193, 7, 0.15)' },
  low: { color: '#00C853', bg: 'rgba(0, 200, 83, 0.15)' },
};

const STATUS_CONFIG = {
  reported: { color: '#8B9DB8', bg: 'rgba(139, 157, 184, 0.15)' },
  dispatched: { color: '#00B4D8', bg: 'rgba(0, 180, 216, 0.15)' },
  resolved: { color: '#00C853', bg: 'rgba(0, 200, 83, 0.15)' },
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
    { label: 'Active Incidents', value: stats.activeIncidents, icon: AlertTriangle, color: stats.activeIncidents > 5 ? '#FF3D00' : '#00C853' },
    { label: 'Crowd Level', value: stats.crowdLevel, icon: Users, color: '#FFD700' },
    { label: 'AI Queries', value: stats.aiQueries?.toLocaleString(), icon: MessageSquare, color: '#00B4D8' },
    { label: 'Avg Response', value: `${stats.avgResponse}s`, icon: Clock, color: '#00C853' },
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
        <h1 className="text-h1 text-stadium-text font-semibold">Dashboard</h1>
      </div>

      <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-4">
        {/* Stats Row */}
        <div className="grid grid-cols-2 gap-3">
          {statCards.map((card) => {
            const Icon = card.icon;
            return (
              <div
                key={card.label}
                className="p-4 rounded-neo-button"
                style={{ background: '#111D2E', boxShadow: '8px 8px 16px #050A10, -8px -8px 16px #1A2A40' }}
              >
                <Icon size={20} color={card.color} className="mb-2" />
                <p className="text-xl font-bold" style={{ color: card.color }}>{card.value}</p>
                <p className="text-stadium-text-secondary text-xs">{card.label}</p>
              </div>
            );
          })}
        </div>

        {/* Crowd Heatmap Preview */}
        <div
          className="p-4 rounded-neo-card"
          style={{ background: '#111D2E', boxShadow: '8px 8px 16px #050A10, -8px -8px 16px #1A2A40' }}
        >
          <h2 className="text-h2 text-stadium-text font-semibold mb-3">Crowd Overview</h2>
          <div className="flex flex-wrap gap-2">
            {crowdData?.zones?.slice(0, 12).map((zone) => (
              <div
                key={zone.zone_id}
                className="px-2 py-1 rounded text-[10px] font-medium"
                style={{
                  background: `${getDensityColor(zone.density)}22`,
                  color: getDensityColor(zone.density),
                }}
              >
                {zone.zone_id.replace('_', ' ')}
              </div>
            )) || (
              <p className="text-stadium-text-secondary text-xs">Loading crowd data...</p>
            )}
          </div>
          <div
            className="mt-3 p-2 rounded-neo-input flex items-center gap-2"
            style={{ background: '#070F1A', borderLeft: '3px solid #FF3D00' }}
          >
            <TrendingUp size={14} color="#FF3D00" />
            <p className="text-stadium-text-secondary text-xs">Gate C will be critical in 10 min</p>
          </div>
        </div>

        {/* Incidents Table */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-h2 text-stadium-text font-semibold">Incidents</h2>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="bg-stadium-surface text-stadium-text-secondary text-xs px-2 py-1 rounded cursor-pointer outline-none"
              style={{ boxShadow: 'inset 3px 3px 6px #050A10, inset -3px -3px 6px #1A2A40' }}
            >
              <option value="all">All</option>
              <option value="reported">Reported</option>
              <option value="dispatched">Dispatched</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>

          <div className="space-y-2">
            {filteredIncidents.map((inc) => {
              const sev = SEVERITY_CONFIG[inc.severity] || SEVERITY_CONFIG.medium;
              const stat = STATUS_CONFIG[inc.status] || STATUS_CONFIG.reported;
              return (
                <motion.div
                  key={inc.id}
                  whileTap={{ scale: 0.99 }}
                  className="p-3 rounded-neo-input"
                  style={{ background: '#111D2E', boxShadow: '4px 4px 8px #050A10, -4px -4px 8px #1A2A40' }}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-stadium-text-tertiary text-xs font-mono">{inc.id}</span>
                    <div className="flex gap-1">
                      <span
                        className="px-1.5 py-0.5 rounded text-[9px] font-semibold"
                        style={{ background: sev.bg, color: sev.color }}
                      >
                        {inc.severity}
                      </span>
                      <span
                        className="px-1.5 py-0.5 rounded text-[9px] font-semibold"
                        style={{ background: stat.bg, color: stat.color }}
                      >
                        {inc.status}
                      </span>
                    </div>
                  </div>
                  <p className="text-stadium-text text-sm capitalize">{inc.type} — {inc.location}</p>
                  <div className="flex items-center justify-between mt-1">
                    <p className="text-stadium-text-tertiary text-xs">Assigned: {inc.assigned}</p>
                    <p className="text-stadium-text-tertiary text-xs">{inc.time}</p>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
