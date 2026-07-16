import { useEffect } from 'react';
import { useAppStore } from '@/store/appStore';

export const useAccessibility = () => {
  const accessibility = useAppStore((s) => s.accessibility);

  useEffect(() => {

    if (accessibility.highContrast) {
      document.body.classList.add('high-contrast');
    } else {
      document.body.classList.remove('high-contrast');
    }

    if (accessibility.largeText) {
      document.body.classList.add('large-text');
    } else {
      document.body.classList.remove('large-text');
    }

    return () => {
      document.body.classList.remove('high-contrast', 'large-text');
    };
  }, [accessibility.highContrast, accessibility.largeText]);

  return accessibility;
};
