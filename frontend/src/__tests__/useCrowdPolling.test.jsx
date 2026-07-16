
import { renderHook } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { useCrowdPolling } from '../hooks/useCrowdPolling';
import { api } from '@/utils/api';

const mockSetCrowdData = vi.fn();

// Mock Zustand store
vi.mock('@/store/appStore', () => ({
  useAppStore: (selector) => {
    const store = {
      setCrowdData: mockSetCrowdData,
      isOnline: true,
    };
    return selector ? selector(store) : store;
  },
}));

// Mock API utility
vi.mock('@/utils/api', () => ({
  api: {
    get: vi.fn(),
  },
}));

// Mock DB utilities
vi.mock('@/utils/offlineDB', () => ({
  saveCrowdData: vi.fn(),
  getCrowdData: vi.fn().mockResolvedValue(null),
}));

describe('useCrowdPolling Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('calls API and updates crowd data in store on successful fetch', async () => {
    const mockData = { zones: [{ zone_id: 'gate_a', current_density: 0.2 }] };
    vi.mocked(api.get).mockResolvedValue({ data: mockData });

    renderHook(() => useCrowdPolling(10000));

    // Should fetch on mount
    expect(api.get).toHaveBeenCalledWith('/api/v1/crowd/all');
    
    // Wait for the async code in the hook to resolve
    await vi.waitFor(() => {
      expect(mockSetCrowdData).toHaveBeenCalledWith(mockData);
    });
  });

  it('falls back to mock data or offline cache when fetch fails', async () => {
    vi.mocked(api.get).mockRejectedValue(new Error('Network Error'));

    renderHook(() => useCrowdPolling(10000));

    await vi.waitFor(() => {
      expect(mockSetCrowdData).toHaveBeenCalled();
    });
  });
});
