/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#14221f',
        paper: '#f5f7f2',
        moss: '#23685b',
        mint: '#dff3e9',
        ember: '#d76a45',
        sand: '#e9e4d6',
      },
      boxShadow: {
        card: '0 18px 50px -30px rgba(20, 34, 31, 0.35)',
      },
    },
  },
  plugins: [],
}
