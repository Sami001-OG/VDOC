import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        surface: {
          0: '#0a0b0e',
          50: '#0e0f13',
          100: '#121318',
          150: '#16171d',
          200: '#1a1b22',
          250: '#1e1f27',
          300: '#22232d',
          350: '#262733',
          400: '#2a2b38',
          450: '#2e2f3d',
        },
        border: {
          DEFAULT: '#1e1f27',
          light: '#262733',
          lighter: '#2a2b38',
        },
        accent: {
          cyan: '#22d3ee',
          blue: '#3b82f6',
          violet: '#8b5cf6',
          green: '#22c55e',
          amber: '#f59e0b',
          red: '#ef4444',
        },
        text: {
          primary: '#e8e9ed',
          secondary: '#94969e',
          muted: '#5c5e66',
          inverse: '#0a0b0e',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      borderRadius: {
        sm: '6px',
        DEFAULT: '8px',
        md: '10px',
        lg: '12px',
        xl: '16px',
      },
      boxShadow: {
        card: '0 1px 2px rgba(0,0,0,0.3), 0 1px 4px rgba(0,0,0,0.15)',
        panel: '0 2px 8px rgba(0,0,0,0.4), 0 1px 2px rgba(0,0,0,0.2)',
        elevated: '0 8px 24px rgba(0,0,0,0.5), 0 2px 4px rgba(0,0,0,0.2)',
        glow: {
          cyan: '0 0 12px rgba(34,211,238,0.15)',
          blue: '0 0 12px rgba(59,130,246,0.15)',
          violet: '0 0 12px rgba(139,92,246,0.15)',
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
        'spin-slow': 'spin 2s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};

export default config;
