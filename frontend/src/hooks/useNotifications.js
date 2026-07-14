import { useEffect } from 'react';
import { useAppStore } from '@/store/appStore';
import { api } from '@/utils/api';

export const useNotifications = () => {
  const userId = useAppStore((s) => s.userId);
  const setNotifications = useAppStore((s) => s.setNotifications);
  const notifications = useAppStore((s) => s.notifications);

  const fetchNotifications = async () => {
    if (!userId) return;
    try {
      const response = await api.get(`/api/v1/notifications/${userId}`);
      setNotifications(response.data.notifications || []);
    } catch {
      // Use mock notifications
      setNotifications([
        { id: '1', type: 'crowd', title: 'Crowd Alert', message: 'Gate C is crowded — use Gate D', read: false, time: new Date().toISOString(), color: '#FF3D00' },
        { id: '2', type: 'match', title: 'GOAL!', message: 'USA 2-1 BRA — Weah scores!', read: false, time: new Date(Date.now() - 300000).toISOString(), color: '#FFD700' },
        { id: '3', type: 'transport', title: 'Shuttle Update', message: 'Shuttle arriving in 5 min', read: true, time: new Date(Date.now() - 600000).toISOString(), color: '#00B4D8' },
      ]);
    }
  };

  const markRead = async (id) => {
    try {
      await api.post('/api/v1/notifications/mark-read', { notification_id: id });
    } catch {
      // offline - will sync later
    }
  };

  useEffect(() => {
    fetchNotifications();
    const timer = setInterval(fetchNotifications, 60000);
    return () => clearInterval(timer);
  }, [userId]);

  return { notifications, fetchNotifications, markRead };
};
