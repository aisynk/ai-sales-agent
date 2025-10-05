/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f5f7ff',
          100: '#ebefff',
          200: '#dce3ff',
          300: '#c3cdff',
          400: '#a5adff',
          500: '#667eea',
          600: '#5568d3',
          700: '#4451bc',
          800: '#363aa5',
          900: '#2d2e8e',
        },
        secondary: {
          50: '#faf5ff',
          100: '#f3e8ff',
          200: '#e9d5ff',
          300: '#d8b4fe',
          400: '#c084fc',
          500: '#764ba2',
          600: '#6b3d91',
          700: '#5f3080',
          800: '#53236f',
          900: '#47165e',
        }
      }
    },
  },
  plugins: [],
}