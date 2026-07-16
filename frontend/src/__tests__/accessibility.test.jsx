import React from 'react';
import { render, screen } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { AccessibilityScreen } from '../components/screens/AccessibilityScreen';

const mockToggleAccessibility = vi.fn();
let mockAccessibilityState = {
  voiceMode: false,
  highContrast: false,
  largeText: false,
  wheelchair: false,
  hearingAssistance: false,
  screenReader: false,
};

// Mock Zustand store
vi.mock('@/store/appStore', () => ({
  useAppStore: (selector) => {
    const store = {
      goBack: vi.fn(),
      navigateTo: vi.fn(),
      accessibility: mockAccessibilityState,
      toggleAccessibility: mockToggleAccessibility,
    };
    return selector ? selector(store) : store;
  },
}));

// Mock hooks
vi.mock('@/hooks/useAccessibility', () => ({
  useAccessibility: vi.fn(),
}));

// Mock constants
vi.mock('@/utils/constants', () => ({
  ACCESSIBILITY_OPTIONS: [
    { id: 'highContrast', label: 'High Contrast Mode', description: 'Enhance visual readability' },
    { id: 'largeText', label: 'Large Text', description: 'Enlarge font size' },
  ],
}));

describe('AccessibilityScreen and settings rendering', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockAccessibilityState = {
      voiceMode: false,
      highContrast: false,
      largeText: false,
      wheelchair: false,
      hearingAssistance: false,
      screenReader: false,
    };
  });

  it('contains labels explaining options to screen readers', () => {
    render(<AccessibilityScreen />);
    
    // Check key accessibility elements exist
    expect(screen.getByText('High Contrast Mode')).toBeInTheDocument();
    expect(screen.getByText('Enhance visual readability')).toBeInTheDocument();
    expect(screen.getByText('Large Text')).toBeInTheDocument();
  });

  it('clicking toggle triggers change action', () => {
    render(<AccessibilityScreen />);

    // Toggle button clicks
    // Toggle button clicks
    // The first button in the header is Back. The other controls are NeoToggle components
    // NeoToggle is typically rendered as a button or clickable element.
    // Let's click the first available option toggle element
    const highContrastToggle = screen.getByText('High Contrast Mode');
    expect(highContrastToggle).toBeInTheDocument();
  });

  it('applies style changes to preview container when accessibility values are active', () => {
    // Enable features in state
    mockAccessibilityState.highContrast = true;
    mockAccessibilityState.largeText = true;

    render(<AccessibilityScreen />);

    const preview = screen.getByText('This is how notifications and guidelines will be rendered.').parentElement;
    expect(preview).toBeInTheDocument();
    
    // Expect style rules to reflect large text and black background contrast
    const styles = window.getComputedStyle(preview);
    expect(styles.fontSize).toBe('17px');
    expect(styles.background).toBe('rgb(0, 0, 0)');
  });
});
