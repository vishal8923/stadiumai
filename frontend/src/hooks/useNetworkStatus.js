import { useState, useEffect } from 'react';
import { useAppStore } from '@/store/appStore';

export const useNetworkStatus = () => {
  const [wasOffline, setWasOffline] = useState(false);
  const setOnline = useAppStore((s) => s.setOnline);
  const isOnline = useAppStore((s) => s.isOnline);

  useEffect(() => {
    const handleOnline = () => {
      setOnline(true);
      setWasOffline(true);
    };
    const handleOffline = () => {
      setOnline(false);
      setWasOffline(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [setOnline]);

  return { isOnline, wasOffline, setWasOffline };
};
