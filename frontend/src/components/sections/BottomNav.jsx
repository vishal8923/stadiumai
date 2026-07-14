import React from 'react';
import { motion } from 'framer-motion';
import { Home, Map, Mic, Ticket, User } from 'lucide-react';
import { useAppStore } from '@/store/appStore';

const NAV_ITEMS = [
  { id: 'home', label: 'Home', icon: Home, screen: 'home' },
  { id: 'map', label: 'Map', icon: Map, screen: 'map' },
  { id: 'chat', label: 'AI Chat', icon: Mic, screen: 'chat', isCenter: true },
  { id: 'match', label: 'Ticket', icon: Ticket, screen: 'match' },
  { id: 'profile', label: 'User', icon: User, screen: 'accessibility' },
];

export const BottomNav = () => {
  const currentScreen = useAppStore((s) => s.currentScreen);
  const navigateTo = useAppStore((s) => s.navigateTo);

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-50 flex items-center justify-around px-2 safe-area-bottom"
      style={{
        height: 80,
        background: '#0A1628',
        borderTop: '1px solid #1A2A40',
      }}
    >
      {NAV_ITEMS.map((item) => {
        const isActive = currentScreen === item.screen;
        const Icon = item.icon;

        if (item.isCenter) {
          return (
            <motion.button
              key={item.id}
              whileTap={{ scale: 0.9 }}
              onClick={() => navigateTo(item.screen)}
              className="flex items-center justify-center rounded-full -mt-6 cursor-pointer"
              style={{
                width: 56,
                height: 56,
                background: '#FFD700',
                boxShadow: '0 0 20px rgba(255, 215, 0, 0.4), 4px 4px 8px #050A10, -4px -4px 8px #1A2A40',
              }}
            >
              <Mic size={24} color="#0A1628" />
            </motion.button>
          );
        }

        return (
          <motion.button
            key={item.id}
            whileTap={{ scale: 0.9 }}
            onClick={() => navigateTo(item.screen)}
            className="flex flex-col items-center justify-center gap-1 py-2 px-3 cursor-pointer"
            style={{ minWidth: 60 }}
          >
            <Icon
              size={22}
              color={isActive ? '#FFD700' : '#4A5D75'}
              strokeWidth={isActive ? 2.5 : 1.5}
            />
            {isActive && (
              <motion.div
                layoutId="navIndicator"
                className="w-1 h-1 rounded-full"
                style={{ background: '#FFD700' }}
              />
            )}
          </motion.button>
        );
      })}
    </nav>
  );
};
