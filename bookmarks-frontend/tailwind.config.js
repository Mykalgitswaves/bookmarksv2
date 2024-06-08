/** @type {import('tailwindcss').Config} */
module.exports = {
  purge: ['./src/**/*.{html,vue,js,ts,jsx,tsx}'],
  content: ["./src/**/*.vue"],
  theme: {
    screens: {
      'md_lg': '850px',
    },
    extend: {},
  },
  plugins: [],
}

