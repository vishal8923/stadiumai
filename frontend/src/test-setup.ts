import '@testing-library/jest-dom';
import { vi } from 'vitest';
import React from 'react';

// Mock matchMedia if components use layout hooks
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock ResizeObserver
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}
window.ResizeObserver = ResizeObserverMock;

// Mock framer-motion to render elements synchronously without animation overhead
vi.mock('framer-motion', () => {
  const actual = vi.importActual('framer-motion');
  const dummyComponent = (name: string) => {
    return React.forwardRef(({ children, ...props }: Record<string, unknown> & { children?: React.ReactNode }, ref: React.Ref<unknown>) => {
      // Clean standard attributes for React elements
      const cleanProps = { ...props };
      delete cleanProps.whileHover;
      delete cleanProps.whileTap;
      delete cleanProps.transition;
      delete cleanProps.initial;
      delete cleanProps.animate;
      delete cleanProps.exit;
      return React.createElement(name, { ...cleanProps, ref }, children);
    });
  };

  return {
    ...actual,
    motion: {
      div: dummyComponent('div'),
      button: dummyComponent('button'),
      span: dummyComponent('span'),
      p: dummyComponent('p'),
      h1: dummyComponent('h1'),
      h2: dummyComponent('h2'),
      ul: dummyComponent('ul'),
      li: dummyComponent('li'),
    },
    AnimatePresence: ({ children }: { children?: React.ReactNode }) => children,
  };
});
