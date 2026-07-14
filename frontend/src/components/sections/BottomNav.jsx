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
      className="fixed bottom-0 left-0 right-0 z-50 flex items-center justify-around px-2 safe-area-bottom lg:hidden"
      style={{
        height: 80,
        background: 'rgba(255, 255, 255, 0.92)',
        backdropFilter: 'blur(16px)',
        borderTop: '1px solid rgba(26, 36, 47, 0.08)',
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
                background: '#DAA520',
                boxShadow: '0 0 20px rgba(218, 165, 32, 0.4), 4px 4px 8px rgba(0, 0, 0, 0.06)',
              }}
            >
              <Mic size={24} color="#FFFFFF" />
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
              color={isActive ? '#DAA520' : '#8B9DB8'}
              strokeWidth={isActive ? 2.5 : 1.5}
            />
            {isActive && (
              <motion.div
                layoutId="navIndicator"
                className="w-1.5 h-1.5 rounded-full"
                style={{ background: '#DAA520' }}
              />
            )}
          </motion.button>
        );
      })}
    </nav>
  );
};
