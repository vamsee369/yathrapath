/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./core/templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        divineGold: "#FFD700",
        templeDark: "#0f0f1a",
      },
      fontFamily: {
        devotional: ['"Playfair Display"', 'serif'],
      },
    },
  },
  plugins: [],
}