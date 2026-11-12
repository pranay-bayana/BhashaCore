/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: 'var(--bg-base)',
          deep: 'var(--bg-deep)',
          elevated: 'var(--bg-elevated)',
        },
        surface: {
          glass: 'var(--glass-surface)',
          'glass-elevated': 'var(--glass-elevated)',
          'glass-subtle': 'var(--glass-subtle)',
        },
        accent: {
          lime: 'var(--accent-lime)',
          emerald: 'var(--accent-emerald)',
          'lime-surface': 'var(--accent-lime-surface)',
          'emerald-surface': 'var(--accent-emerald-surface)',
          glow: 'var(--glow-beam)',
        },
        text: {
          primary: 'var(--text-primary)',
          secondary: 'var(--text-secondary)',
          muted: 'var(--text-muted)',
        },
        border: {
          subtle: 'var(--glass-border-subtle)',
          glass: 'var(--glass-border)',
        }
      },
      fontFamily: {
        sans: [
          'Plus Jakarta Sans',
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          '"Noto Sans Devanagari"',
          '"Noto Sans Telugu"',
          '"Noto Sans Tamil"',
          '"Noto Sans Kannada"',
          '"Noto Sans Malayalam"',
          'sans-serif'
        ],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      boxShadow: {
        'glass-sm': 'var(--shadow-glass-sm)',
        'glass-md': 'var(--shadow-glass-md)',
        'glass-lg': 'var(--shadow-glass-lg)',
        'lime-glow': '0 0 24px -4px var(--glow-beam)',
        'emerald-glow': '0 0 24px -4px var(--accent-emerald-surface)',
      },
      backdropBlur: {
        xs: '2px',
        glass: '24px',
        deep: '32px',
      },
      animation: {
        'pulse-subtle': 'pulseSubtle 4s ease-in-out infinite',
        'beam-drift': 'beamDrift 8s ease-in-out infinite alternate',
      },
      keyframes: {
        pulseSubtle: {
          '0%, 100%': { opacity: '0.4' },
          '50%': { opacity: '0.75' },
        },
        beamDrift: {
          '0%': { transform: 'translateX(-50%) scaleX(1)' },
          '100%': { transform: 'translateX(-50%) scaleX(1.15)' },
        }
      }
    },
  },
  plugins: [],
}
