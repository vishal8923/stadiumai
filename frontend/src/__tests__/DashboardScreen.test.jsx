import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { DashboardScreen } from '../components/screens/DashboardScreen';

// Mock Zustand store
vi.mock('@/store/appStore', () => ({
  useAppStore: (selector) => {
    const store = {
      goBack: vi.fn(),
      crowdData: {
        zones: [
          { zone_id: 'gate_a', current_density: 0.3, level: 'medium', trend: 'stable' },
          { zone_id: 'gate_b', current_density: 0.8, level: 'high', trend: 'rising' },
        ],
      },
    };
    return selector ? selector(store) : store;
  },
}));

// Mock hook
vi.mock('@/hooks/useCrowdPolling', () => ({
  useCrowdPolling: vi.fn(),
}));

// Mock api utility
vi.mock('@/utils/api', () => ({
  api: {
    get: vi.fn().mockImplementation((url) => {
      if (url.includes('/admin/dashboard')) {
        return Promise.resolve({
          data: {
            activeIncidents: 5,
            crowdLevel: 'High',
            aiQueries_today: 450,
            avg_response_time: 1.5,
          },
        });
      }
      if (url.includes('/admin/incidents')) {
        return Promise.resolve({
          data: {
            incidents: [
              { id: 'INC-001', type: 'medical', location: 'Gate C', severity: 'high', status: 'dispatched', assigned: 'Team A', time: '2 min ago' },
              { id: 'INC-002', type: 'security', location: 'Section 12', severity: 'medium', status: 'reported', assigned: '-', time: '5 min ago' },
            ],
          },
        });
      }
      return Promise.reject(new Error('Unknown URL'));
    }),
  },
}));

describe('DashboardScreen Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders correctly and shows stats cards and tables', async () => {
    render(<DashboardScreen />);

    // Titles
    expect(screen.getByText('Operations Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Live Zone Congestion')).toBeInTheDocument();

    // Verify incident listing fallback/default list renders initially
    // Since api call runs on mount, wait for rendering
    await vi.waitFor(() => {
      expect(screen.getByText(/medical Report at Gate C/i)).toBeInTheDocument();
      expect(screen.getByText(/security Report at Section 12/i)).toBeInTheDocument();
    });
  });

  it('filters incident list when select value changes', async () => {
    render(<DashboardScreen />);

    // Wait for data load
    await vi.waitFor(() => {
      expect(screen.getByText(/medical Report at Gate C/i)).toBeInTheDocument();
    });

    const select = screen.getByRole('combobox');
    expect(select).toBeInTheDocument();

    // Filter to only reported
    fireEvent.change(select, { target: { value: 'reported' } });
    
    // INC-002 is reported, INC-001 is dispatched. INC-001 should not be found in filtered listing.
    expect(screen.queryByText(/medical Report at Gate C/i)).not.toBeInTheDocument();
    expect(screen.getByText(/security Report at Section 12/i)).toBeInTheDocument();
  });
});
