/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./pages/**/*.{js,jsx}", "./components/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0a0f1f",
        panel: "#101936",
        glow: "#19b5c5",
        ember: "#ff845a",
        mint: "#76f2ba"
      },
      boxShadow: {
        panel: "0 24px 50px rgba(0, 0, 0, 0.35)",
        neon: "0 0 20px rgba(25, 181, 197, 0.35)"
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-8px)" }
        },
        pulseSoft: {
          "0%, 100%": { opacity: "0.5" },
          "50%": { opacity: "1" }
        }
      },
      animation: {
        float: "float 4s ease-in-out infinite",
        pulseSoft: "pulseSoft 2.5s ease-in-out infinite"
      }
    }
  },
  plugins: []
};
