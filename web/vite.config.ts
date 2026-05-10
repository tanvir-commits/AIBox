import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

/** Dev outside Docker: backend on localhost. Docker Compose sets VITE_PROXY_API=http://backend:8000 */
const api = process.env.VITE_PROXY_API ?? "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 3000,
    proxy: {
      "/health": { target: api, changeOrigin: true },
      "/api": { target: api, changeOrigin: true },
    },
  },
});
