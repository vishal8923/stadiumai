/* eslint-disable @typescript-eslint/no-require-imports, no-undef */
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{jsx,js,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'stadium-bg': '#0A1628',
        'stadium-surface': '#111D2E',
        'stadium-pressed': '#070F1A',
        'stadium-gold': '#FFD700',
        'stadium-green': '#00C853',
        'stadium-blue': '#00B4D8',
        'stadium-red': '#FF3D00',
        'stadium-orange': '#FF9800',
        'stadium-yellow': '#FFC107',
        'stadium-text': '#F0F4F8',
        'stadium-text-secondary': '#8B9DB8',
        'stadium-text-tertiary': '#4A5D75',
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
      },
      fontSize: {
        'h1': ['24px', { lineHeight: '1.2', fontWeight: '700' }],
        'h2': ['18px', { lineHeight: '1.3', fontWeight: '600' }],
        'h3': ['14px', { lineHeight: '1.4', fontWeight: '600' }],
        'body': ['14px', { lineHeight: '1.5', fontWeight: '400' }],
        'caption': ['11px', { lineHeight: '1.4', fontWeight: '400' }],
        'score': ['32px', { lineHeight: '1', fontWeight: '700' }],
      },
      boxShadow: {
        'neo-raised': '8px 8px 16px #050A10, -8px -8px 16px #1A2A40',
        'neo-pressed': 'inset 6px 6px 12px #050A10, inset -6px -6px 12px #1A2A40',
        'neo-float': '4px 4px 8px #050A10, -4px -4px 8px #1A2A40',
        'neo-glow': '0 0 20px rgba(0, 180, 216, 0.3), 8px 8px 16px #050A10, -8px -8px 16px #1A2A40',
      },
      borderRadius: {
        'neo-card': '24px',
        'neo-button': '20px',
        'neo-input': '16px',
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      keyframes: {
        'orb-breathe': {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.03)' },
        },
        'pulse-dot': {
          '0%, 100%': { transform: 'scale(1)', opacity: '1' },
          '50%': { transform: 'scale(1.2)', opacity: '0.8' },
        },
        'slide-up': {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'wave-bar': {
          '0%': { height: '8px' },
          '100%': { height: '32px' },
        },
      },
      animation: {
        'orb-breathe': 'orb-breathe 4s ease-in-out infinite',
        'pulse-dot': 'pulse-dot 1.5s ease-in-out infinite',
        'slide-up': 'slide-up 0.4s ease-out',
        'wave-bar': 'wave-bar 0.3s ease-in-out infinite alternate',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};
