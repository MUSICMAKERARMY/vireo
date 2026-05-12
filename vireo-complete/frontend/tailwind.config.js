/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#00E5A0',
        'primary-dark': '#00B4D8',
        surface: '#131B2C',
        glass: 'rgba(255, 255, 255, 0.05)',
      },
    },
  },
  plugins: [],
};
