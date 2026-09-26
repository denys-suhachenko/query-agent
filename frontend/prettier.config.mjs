/** @type {import('prettier').Config & import('prettier-plugin-tailwindcss').PluginOptions} */
const prettierConfig = {
  singleQuote: true,
  plugins: ['prettier-plugin-tailwindcss'],
  tailwindStylesheet: './app/globals.css',
};

export default prettierConfig;
