/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        chess: {
          dark: '#302e2b',
          lightSquare: '#ebecd0',
          darkSquare: '#739552',
          highlight: '#f6f669',
        }
      }
    },
  },
  plugins: [],
}
