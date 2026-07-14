import { getPendingActions, removePendingAction } from './offlineDB';
import { api } from './api';

export const syncPendingActions = async (onProgress, onComplete) => {
  const pending = await getPendingActions();
  if (pending.length === 0) {
    onComplete?.(0);
    return;
  }

  let completed = 0;
  const total = pending.length;

  for (const action of pending) {
    try {
      switch (action.type) {
        case 'incident':
          await api.post('/api/v1/incidents', action.payload);
          break;
        case 'chat':
          await api.post('/api/v1/chat', action.payload);
          break;
        case 'feedback':
          await api.post('/api/v1/feedback', action.payload);
          break;
        case 'preference':
          await api.patch('/api/v1/users/preference', action.payload);
          break;
        default:
          console.warn('Unknown action type:', action.type);
      }
      await removePendingAction(action.id);
      completed++;
      onProgress?.(completed, total);
    } catch (err) {
      console.error('Sync failed for action:', action.id, err);
    }
  }

  onComplete?.(completed);
};
