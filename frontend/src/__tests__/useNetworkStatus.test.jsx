
import { renderHook, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { useNetworkStatus } from '../hooks/useNetworkStatus';

const mockSetOnline = vi.fn();

// Mock Zustand store
vi.mock('@/store/appStore', () => ({
  useAppStore: (selector) => {
    const store = {
      setOnline: mockSetOnline,
      isOnline: true,
    };
    return selector ? selector(store) : store;
  },
}));

describe('useNetworkStatus Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('subscribes to window online/offline events', () => {
    const addEventSpy = vi.spyOn(window, 'addEventListener');
    const removeEventSpy = vi.spyOn(window, 'removeEventListener');

    const { unmount } = renderHook(() => useNetworkStatus());

    expect(addEventSpy).toHaveBeenCalledWith('online', expect.any(Function));
    expect(addEventSpy).toHaveBeenCalledWith('offline', expect.any(Function));

    unmount();

    expect(removeEventSpy).toHaveBeenCalledWith('online', expect.any(Function));
    expect(removeEventSpy).toHaveBeenCalledWith('offline', expect.any(Function));
  });

  it('triggers updates when window online status changes', () => {
    renderHook(() => useNetworkStatus());

    // Simulate online event
    act(() => {
      window.dispatchEvent(new Event('online'));
    });
    expect(mockSetOnline).toHaveBeenCalledWith(true);

    // Simulate offline event
    act(() => {
      window.dispatchEvent(new Event('offline'));
    });
    expect(mockSetOnline).toHaveBeenCalledWith(false);
  });
});
