import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Only VITE_* variables reach the browser bundle. Never put secrets in them.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:8787',
    },
  },
});
