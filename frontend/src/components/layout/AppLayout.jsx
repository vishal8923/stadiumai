import React, { useEffect } from 'react';
import { useAppStore } from '@/store/appStore';
import { useNetworkStatus } from '@/hooks/useNetworkStatus';
import { useAccessibility } from '@/hooks/useAccessibility';
import { BottomNav } from '@/components/sections/BottomNav';
import { OfflineBanner } from '@/components/ui/OfflineBanner';
import { syncPendingActions } from '@/utils/syncEngine';
import { getPendingActions } from '@/utils/offlineDB';

const NAV_SCREENS = ['home', 'map', 'chat', 'match', 'accessibility', 'sustainability', 'notifications', 'transport', 'incident', 'navigation', 'dashboard'];

export const AppLayout = ({ children }) => {
  const currentScreen = useAppStore((s) => s.currentScreen);
  const isOnline = useAppStore((s) => s.isOnline);
  const isSyncing = useAppStore((s) => s.isSyncing);
  const setSyncing = useAppStore((s) => s.setSyncing);
  const pendingActionsCount = useAppStore((s) => s.pendingActionsCount);
  const setPendingActionsCount = useAppStore((s) => s.setPendingActionsCount);

  useNetworkStatus();
  useAccessibility();

  // Update pending count
  useEffect(() => {
    const checkPending = async () => {
      const actions = await getPendingActions();
      setPendingActionsCount(actions.length);
    };
    checkPending();
    const timer = setInterval(checkPending, 10000);
    return () => clearInterval(timer);
  }, []);

  // Sync when back online
  useEffect(() => {
    if (isOnline && pendingActionsCount > 0) {
      setSyncing(true);
      syncPendingActions(
        (completed, total) => setPendingActionsCount(total - completed),
        () => {
          setSyncing(false);
          setPendingActionsCount(0);
        }
      );
    }
  }, [isOnline]);

  const showNav = NAV_SCREENS.includes(currentScreen);
  const showBanner = currentScreen !== 'splash' && currentScreen !== 'onboarding';

  return (
    <div className="h-full w-full relative">
      {/* Offline Banner — hidden on splash/onboarding */}
      {showBanner && (
        <OfflineBanner
          isOnline={isOnline}
          isSyncing={isSyncing}
          pendingCount={pendingActionsCount}
        />
      )}

      {/* Main Content */}
      <div className={`h-full w-full ${showBanner && !isOnline ? 'pt-12' : ''}`}>
        {children}
      </div>

      {/* Bottom Navigation */}
      {showNav && <BottomNav />}
    </div>
  );
};
