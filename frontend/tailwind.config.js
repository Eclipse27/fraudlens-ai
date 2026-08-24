/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--color-bg)',
        surface: 'var(--color-surface)',
        'surface-alt': 'var(--color-surface-alt)',
        border: 'var(--color-border)',
        navy: {
          900: 'var(--color-navy-900)',
          800: 'var(--color-navy-800)',
          700: 'var(--color-navy-700)',
        },
        primary: 'var(--color-text-primary)',
        secondary: 'var(--color-text-secondary)',
        inverse: 'var(--color-text-inverse)',
        accent: {
          DEFAULT: 'var(--color-accent-blue)',
          hover: 'var(--color-accent-blue-600)',
        },
        ai: 'var(--color-ai-indigo)',
        risk: {
          low: 'var(--color-risk-low)',
          'low-bg': 'var(--color-risk-low-bg)',
          medium: 'var(--color-risk-medium)',
          'medium-bg': 'var(--color-risk-medium-bg)',
          high: 'var(--color-risk-high)',
          'high-bg': 'var(--color-risk-high-bg)',
          suspicious: 'var(--color-risk-suspicious)',
          'suspicious-bg': 'var(--color-risk-suspicious-bg)',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      },
    },
  },
  plugins: [],
}
