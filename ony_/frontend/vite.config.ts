import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        // Sur certains Windows, "localhost" peut résoudre en IPv6 (::1) et provoquer ECONNREFUSED
        // si le backend n'écoute qu'en IPv4. Forcer 127.0.0.1 évite ce souci.
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})

