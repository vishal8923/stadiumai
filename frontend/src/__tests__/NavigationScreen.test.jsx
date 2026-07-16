import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { NavigationScreen } from '../components/screens/NavigationScreen';

// Mock app store
vi.mock('@/store/appStore', () => ({
  useAppStore: (selector) => {
    const store = {
      goBack: vi.fn(),
      ticketInfo: { section: '10' },
    };
    return selector ? selector(store) : store;
  },
}));

// Mock hooks
vi.mock('@/hooks/useVoice', () => ({
  useVoice: () => ({
    speak: vi.fn(),
  }),
}));

describe('NavigationScreen Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders correctly and shows ticket destination section', () => {
    render(<NavigationScreen />);
    
    // Check destination heading from mock ticketInfo
    expect(screen.getByText('Section 10')).toBeInTheDocument();
    expect(screen.getByText('Turn left at Concourse 1')).toBeInTheDocument();
  });

  it('toggles voice guidance on and off', () => {
    render(<NavigationScreen />);
    
    // Voice mode starts off. Find toggle button
    const toggleButton = screen.getAllByRole('button')[1]; // second button is voice toggle
    expect(toggleButton).toBeInTheDocument();
    
    // Toggle on
    fireEvent.click(toggleButton);
    // Toggle off
    fireEvent.click(toggleButton);
  });
});
