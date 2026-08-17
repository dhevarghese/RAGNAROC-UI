import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// base is set at build time for GitHub Pages (see .github/workflows/deploy.yml)
export default defineConfig({
  plugins: [react()],
  base: process.env.VITE_BASE ?? '/',
  build: { target: 'es2022' },
  worker: { format: 'es' },
})
