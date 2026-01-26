/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // CITTAA Brand Colors - Lavender/Purple Theme
        primary: {
          50: '#FAF5FA',
          100: '#F3E8F3',
          200: '#E8D5E8',
          300: '#DCC8DC',
          400: '#C9A8C9',
          500: '#9B7B9B', // Main lavender purple
          600: '#7D5E7D',
          700: '#5D4E6D',
          800: '#4A3F55',
          900: '#3A2F45',
        },
        secondary: {
          50: '#f0f7f2',
          100: '#dcece0',
          200: '#bdd9c4',
          300: '#9bc5a5',
          400: '#6B9B6B', // Main green (floral accent)
          500: '#5a8a5a',
          600: '#487048',
          700: '#3a5c3a',
          800: '#2c482c',
          900: '#1e321e',
        },
        accent: {
          50: '#fdf8f5',
          100: '#f9efe8',
          200: '#f0ddd0',
          300: '#e5c8b5',
          400: '#D4A88A', // Warm accent
          500: '#c49070',
          600: '#a87858',
          700: '#8c6248',
          800: '#704c38',
          900: '#543828',
        },
        lavender: {
          light: '#E8D5E8',
          DEFAULT: '#DCC8DC',
          dark: '#C9A8C9',
        },
        background: '#FAF5FA',
        text: '#3A2F45',
        success: '#6B9B6B',
        warning: '#D4A88A',
        error: '#C97070',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Playfair Display', 'serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'slide-down': 'slideDown 0.4s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
        'float': 'float 3s ease-in-out infinite',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideDown: {
          '0%': { opacity: '0', transform: 'translateY(-20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
      },
      backgroundImage: {
        'gradient-lavender': 'linear-gradient(135deg, #FAF5FA 0%, #E8D5E8 50%, #DCC8DC 100%)',
        'gradient-purple': 'linear-gradient(135deg, #9B7B9B 0%, #7D5E7D 100%)',
      },
    },
  },
  plugins: [],
}
