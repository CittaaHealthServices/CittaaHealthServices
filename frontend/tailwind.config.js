/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // CITTAA Brand Colors
        primary: {
          50: '#f5f0f6',
          100: '#e8dcea',
          200: '#d4bdd8',
          300: '#b994be',
          400: '#9e6ba4',
          500: '#8B5A96', // Main purple
          600: '#744a7d',
          700: '#5d3b64',
          800: '#472d4b',
          900: '#311e33',
        },
        secondary: {
          50: '#f0f7f5',
          100: '#dcece8',
          200: '#bdd9d2',
          300: '#9bc5bb',
          400: '#7BB3A8', // Main teal
          500: '#5a9a8d',
          600: '#487d73',
          700: '#3a645c',
          800: '#2c4b45',
          900: '#1e322e',
        },
        accent: {
          50: '#fff5ed',
          100: '#ffe6d5',
          200: '#ffc9a8',
          300: '#ffa66f',
          400: '#FF8C42', // Main orange
          500: '#e67330',
          600: '#c45a20',
          700: '#a24418',
          800: '#803512',
          900: '#5e270d',
        },
        background: '#F8F9FA',
        text: '#2C3E50',
        success: '#27AE60',
        warning: '#F39C12',
        error: '#E74C3C',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
