import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// En développement, /api est redirigé vers le backend FastAPI (pas de CORS à gérer côté backend)
const BACKEND_URL = process.env.PINARD_BACKEND_URL ?? "http://127.0.0.1:9090";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: BACKEND_URL,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
