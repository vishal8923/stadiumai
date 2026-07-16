import { useEffect, useRef, useCallback } from 'react';
import { useAppStore } from '@/store/appStore';
import { api } from '@/utils/api';
import { MOCK_CROWD_DATA } from '@/utils/constants';
import { saveCrowdData, getCrowdData } from '@/utils/offlineDB';

export const useCrowdPolling = (interval = 30000) => {
  const setCrowdData = useAppStore((s) => s.setCrowdData);
  const isOnline = useAppStore((s) => s.isOnline);
  const timerRef = useRef(null);

  const fetchCrowd = useCallback(async () => {
    try {
      const response = await api.get('/api/v1/crowd/all');
      setCrowdData(response.data);
      await saveCrowdData(response.data);
    } catch {
      const cached = await getCrowdData();
      if (cached?.data) {
        setCrowdData(cached.data);
      } else {
        setCrowdData(MOCK_CROWD_DATA);
      }
    }
  }, [setCrowdData]);

  useEffect(() => {
    fetchCrowd();
    timerRef.current = setInterval(fetchCrowd, interval);
    return () => clearInterval(timerRef.current);
  }, [isOnline, fetchCrowd, interval]);

  return { refresh: fetchCrowd };
};
