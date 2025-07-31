import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0',
    open: false,
    cors: true,
    hmr: {
      clientPort: 3000,
      overlay: true
    },
    watch: {
      usePolling: true
    },
    proxy: {
      '/api': {
        target: 'http://user-management:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/notification-api': {
        target: 'http://notification:8004',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/notification-api/, '')
      },
      '/ws': {
        target: 'ws://notification:8004',
        ws: true
      }
    }
  }
})