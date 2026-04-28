/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        abyss: "#050505",
        amber: "#ffb000",
        steel: "#9aa0a6",
      },
      fontFamily: {
        mono: ["Courier New", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      boxShadow: {
        glow: "0 0 24px rgba(255, 176, 0, 0.25)",
      },
    },
  },
  plugins: [],
};
