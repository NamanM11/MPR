/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ondc: {
          blue: "#003b95",
          orange: "#fd6f22",
        }
      }
    },
  },
  plugins: [],
}
