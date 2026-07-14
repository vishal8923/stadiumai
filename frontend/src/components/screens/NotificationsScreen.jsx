import React from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, AlertTriangle, Trophy, Bus, Siren, Check, ChevronRight } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { useNotifications } from '@/hooks/useNotifications';

const NOTIFICATION_ICONS = {
  crowd: { icon: AlertTriangle, color: '#FF3D00', bg: 'rgba(255, 61, 0, 0.1)' },
  match: { icon: Trophy, color: '#FFD700', bg: 'rgba(255, 215, 0, 0.1)' },
  transport: { icon: Bus, color: '#00B4D8', bg: 'rgba(0, 180, 216, 0.1)' },
  emergency: { icon: Siren, color: '#FF3D00', bg: 'rgba(255, 61, 0, 0.2)' },
};

export const NotificationsScreen = () => {
  const goBack = useAppStore((s) => s.goBack);
  const markNotificationRead = useAppStore((s) => s.markNotificationRead);
  const markAllRead = useAppStore((s) => s.markAllRead);
  const notifications = useAppStore((s) => s.notifications);

  const getIconConfig = (type) => NOTIFICATION_ICONS[type] || NOTIFICATION_ICONS.match;

  return (
    <div className="h-full flex flex-col" style={{ background: '#0A1628' }}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3">
        <div className="flex items-center gap-3">
          <button
            onClick={goBack}
            className="w-10 h-10 rounded-full flex items-center justify-center cursor-pointer"
            style={{ background: '#111D2E', boxShadow: '4px 4px 8px #050A10, -4px -4px 8px #1A2A40' }}
          >
            <ArrowLeft size={20} color="#F0F4F8" />
          </button>
          <h1 className="text-h1 text-stadium-text font-semibold">Notifications</h1>
        </div>
        <motion.button
          whileTap={{ scale: 0.9 }}
          onClick={markAllRead}
          className="w-10 h-10 rounded-full flex items-center justify-center cursor-pointer"
          style={{ background: '#FFD700', boxShadow: '4px 4px 8px #050A10, -4px -4px 8px #1A2A40' }}
        >
          <Check size={18} color="#0A1628" />
        </motion.button>
      </div>

      {/* Notifications List */}
      <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-3">
        {notifications.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center opacity-50">
            <Check size={48} color="#4A5D75" />
            <p className="text-stadium-text-secondary mt-4">All caught up!</p>
          </div>
        )}

        {/* Today */}
        {notifications.length > 0 && (
          <>
            <p className="text-stadium-text-secondary text-xs font-semibold uppercase tracking-wider">Today</p>
            {notifications.map((notif) => {
              const config = getIconConfig(notif.type);
              const Icon = config.icon;
              return (
                <motion.div
                  key={notif.id}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => markNotificationRead(notif.id)}
                  className="relative flex items-start gap-3 p-4 rounded-neo-button cursor-pointer"
                  style={{
                    background: notif.type === 'emergency' ? 'rgba(255, 61, 0, 0.08)' : '#111D2E',
                    boxShadow: '8px 8px 16px #050A10, -8px -8px 16px #1A2A40',
                    borderLeft: `3px solid ${config.color}`,
                  }}
                >
                  {!notif.read && (
                    <div
                      className="absolute top-3 right-3 w-2.5 h-2.5 rounded-full"
                      style={{ background: '#FFD700' }}
                    />
                  )}
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
                    style={{ background: config.bg }}
                  >
                    <Icon size={18} color={config.color} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-stadium-text font-medium text-sm">{notif.title}</p>
                    <p className="text-stadium-text-secondary text-xs mt-0.5">{notif.message}</p>
                    <p className="text-stadium-text-tertiary text-[10px] mt-1">
                      {new Date(notif.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                  <ChevronRight size={16} color="#4A5D75" className="flex-shrink-0 mt-1" />
                </motion.div>
              );
            })}
          </>
        )}
      </div>
    </div>
  );
};
