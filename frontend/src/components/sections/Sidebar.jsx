import React from 'react';
import { useAppStore } from '@/store/appStore';
import { 
  Home, 
  Map, 
  Brain, 
  Ticket, 
  User, 
  Leaf, 
  AlertTriangle, 
  Bus, 
  LayoutDashboard, 
  Bell 
} from 'lucide-react';

const SIDEBAR_ITEMS = [
  { id: 'home', label: 'Home Dashboard', icon: Home, screen: 'home' },
  { id: 'map', label: 'Stadium Map', icon: Map, screen: 'map' },
  { id: 'chat', label: 'AI Concierge', icon: Brain, screen: 'chat', isAI: true },
  { id: 'match', label: 'Live Match', icon: Ticket, screen: 'match' },
  { id: 'accessibility', label: 'Accessibility', icon: User, screen: 'accessibility' },
  { id: 'sustainability', label: 'Sustainability', icon: Leaf, screen: 'sustainability' },
  { id: 'transport', label: 'Metro & Shuttles', icon: Bus, screen: 'transport' },
  { id: 'incident', label: 'Report Incident', icon: AlertTriangle, screen: 'incident' },
  { id: 'dashboard', label: 'Operations Panel', icon: LayoutDashboard, screen: 'dashboard' },
  { id: 'notifications', label: 'Notifications', icon: Bell, screen: 'notifications' }
];

export const Sidebar = () => {
  const currentScreen = useAppStore((s) => s.currentScreen);
  const navigateTo = useAppStore((s) => s.navigateTo);
  const unreadCount = useAppStore((s) => s.unreadCount);
  const ticketInfo = useAppStore((s) => s.ticketInfo);
  const accessibility = useAppStore((s) => s.accessibility);

  const hasActiveAccessibility = Object.values(accessibility).some(v => v === true);

  return (
    <div 
      className="flex flex-col h-full w-full py-6 px-4 select-none"
      style={{
        background: 'rgba(255, 255, 255, 0.8)',
        backdropFilter: 'blur(12px)',
        borderRight: '1px solid rgba(26, 36, 47, 0.08)'
      }}
    >
      {/* Brand Header */}
      <div className="flex items-center gap-3 px-3 mb-8 cursor-pointer" onClick={() => navigateTo('home')}>
        <span className="text-2xl">🏟️</span>
        <div>
          <h2 className="font-bold text-lg leading-tight text-[#1A242F] tracking-wide">StadiumAI</h2>
          <p className="text-[10px] uppercase font-semibold text-[#DAA520] tracking-wider">FIFA 2026 Concierge</p>
        </div>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 space-y-1.5 overflow-y-auto pr-1">
        {SIDEBAR_ITEMS.map((item) => {
          const isActive = currentScreen === item.screen;
          const Icon = item.icon;

          return (
            <button
              key={item.id}
              onClick={() => navigateTo(item.screen)}
              className="w-full flex items-center justify-between px-3.5 py-3 rounded-xl transition-all duration-200 cursor-pointer text-left group"
              style={{
                background: isActive 
                  ? 'rgba(218, 165, 32, 0.09)' 
                  : 'transparent',
                color: isActive 
                  ? '#DAA520' 
                  : item.isAI ? '#06B6D4' : '#5A6B7C',
                borderLeft: isActive 
                  ? '3px solid #DAA520' 
                  : '3px solid transparent',
              }}
            >
              <div className="flex items-center gap-3">
                <Icon 
                  size={18} 
                  className={`transition-transform duration-200 group-hover:scale-110 ${
                    isActive ? 'stroke-[2.5px]' : 'stroke-[1.5px]'
                  }`}
                  color={isActive ? '#DAA520' : item.isAI ? '#06B6D4' : '#5A6B7C'}
                />
                <span className={`text-sm font-medium ${isActive ? 'font-semibold' : 'text-[#5A6B7C]'}`}>
                  {item.label}
                </span>
              </div>

              {/* Badges */}
              {item.id === 'notifications' && unreadCount > 0 && (
                <span className="flex items-center justify-center min-w-5 h-5 px-1 rounded-full text-[9px] font-bold text-white bg-[#EF4444]">
                  {unreadCount}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* User Details Footer */}
      <div 
        className="mt-6 p-4 rounded-2xl flex flex-col gap-2"
        style={{
          background: 'rgba(26, 36, 47, 0.03)',
          border: '1px solid rgba(26, 36, 47, 0.05)'
        }}
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-[#DAA520]/15 flex items-center justify-center font-bold text-xs text-[#DAA520]">
            A
          </div>
          <div>
            <p className="text-xs font-bold text-[#1A242F]">Alex M.</p>
            <p className="text-[9px] text-[#5A6B7C] uppercase tracking-wide">Fan Session</p>
          </div>
        </div>
        
        {/* Seat details */}
        {(ticketInfo.section || ticketInfo.gate) && (
          <div className="text-[10px] text-[#5A6B7C] border-t border-dashed border-gray-200 pt-2 mt-1">
            <span className="font-semibold text-[#1A242F]">Seat:</span> Sec {ticketInfo.section || '-'}, Row {ticketInfo.row || '-'} • Gate {ticketInfo.gate || '-'}
          </div>
        )}

        {hasActiveAccessibility && (
          <div className="flex items-center gap-1.5 mt-0.5">
            <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse"></span>
            <span className="text-[9px] font-semibold text-[#10B981] uppercase tracking-wider">Accessibility Active</span>
          </div>
        )}
      </div>
    </div>
  );
};
