import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { IncidentScreen } from '../components/screens/IncidentScreen';

// Mock Zustand store
vi.mock('@/store/appStore', () => ({
  useAppStore: (selector) => {
    const store = {
      goBack: vi.fn(),
      isOnline: true,
    };
    return selector ? selector(store) : store;
  },
}));

// Mock hooks
vi.mock('@/hooks/useNetworkStatus', () => ({
  useNetworkStatus: () => ({ isOnline: true }),
}));

// Mock api utility
vi.mock('@/utils/api', () => ({
  api: {
    post: vi.fn().mockResolvedValue({
      data: { incident_id: 'INC-12345' },
    }),
  },
}));

describe('IncidentScreen Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders correctly and guides user through steps', async () => {
    render(<IncidentScreen />);

    // Step 0: Type Selection
    expect(screen.getByText('What type of incident?')).toBeInTheDocument();
    
    // Select medical type
    const medicalBtn = screen.getByText('Medical');
    fireEvent.click(medicalBtn);

    // Click Next
    const nextBtn = screen.getByRole('button', { name: /Next/i });
    fireEvent.click(nextBtn);

    // Step 1: Details form
    expect(screen.getByText('Location')).toBeInTheDocument();
    expect(screen.getByText('Description')).toBeInTheDocument();
    
    const submitBtn = screen.getByRole('button', { name: /Submit Report/i });
    expect(submitBtn).toBeDisabled();

    // Type description
    const descInput = screen.getByPlaceholderText(/Describe the incident/i);
    fireEvent.change(descInput, { target: { value: 'Someone collapsed' } });
    expect(submitBtn).toBeEnabled();

    // Submit report
    fireEvent.click(submitBtn);

    // Step 2: Confirmation screen
    await waitFor(() => {
      expect(screen.getByText('Incident Reported')).toBeInTheDocument();
      expect(screen.getByText('INC-12345')).toBeInTheDocument();
    });
  });
});
