import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { SustainabilityScreen } from '../components/screens/SustainabilityScreen';

// Mock zustand store
vi.mock('@/store/appStore', () => ({
  useAppStore: (selector) => {
    const store = {
      goBack: vi.fn(),
      navigateTo: vi.fn(),
      isOnline: true,
    };
    return selector ? selector(store) : store;
  },
}));

// Mock hooks
vi.mock('@/hooks/useNetworkStatus', () => ({
  useNetworkStatus: () => ({ isOnline: true }),
}));

// Mock api client
vi.mock('@/utils/api', () => ({
  api: {
    post: vi.fn().mockResolvedValue({
      data: {
        item_type: 'Recyclable (Plastic/Metal)',
        bin_type: 'Recycling Bin (Blue)',
        bin_location: 'Concourse 1 corridor near entrance B',
        environmental_impact: 'Reduces landfill waste.',
        disposal_tip: 'Rinse before throwing.',
      },
    }),
  },
}));

describe('SustainabilityScreen Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders correctly and shows main headings', () => {
    render(<SustainabilityScreen />);
    
    // Check main title
    expect(screen.getByText('Sustainability')).toBeInTheDocument();
    // Check subheadings
    expect(screen.getByText('Waste Classifier')).toBeInTheDocument();
    expect(screen.getByText('Carbon Tracker')).toBeInTheDocument();
  });

  it('button is disabled by default and enabled when typing description', () => {
    render(<SustainabilityScreen />);
    
    const button = screen.getByRole('button', { name: /Classify Waste/i });
    expect(button).toBeDisabled();

    const input = screen.getByPlaceholderText(/Describe the item/i);
    fireEvent.change(input, { target: { value: 'plastic bottle' } });

    expect(button).toBeEnabled();
  });

  it('shows classification results when button is clicked', async () => {
    const { api } = await import('@/utils/api');
    
    render(<SustainabilityScreen />);
    
    const input = screen.getByPlaceholderText(/Describe the item/i);
    fireEvent.change(input, { target: { value: 'plastic bottle' } });

    const button = screen.getByRole('button', { name: /Classify Waste/i });
    fireEvent.click(button);

    // Verify API POST request was called
    expect(api.post).toHaveBeenCalledWith('/api/v1/sustainability/waste', {
      item_description: 'plastic bottle',
    });

    // Wait for the resulting card to render
    await waitFor(() => {
      expect(screen.getByText('Recycling Bin (Blue)')).toBeInTheDocument();
      expect(screen.getByText('Concourse 1 corridor near entrance B')).toBeInTheDocument();
    });
  });
});
