import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react-swc";
import { defineConfig } from "vite";

// Dev server proxies `/api/*` to the FastAPI app on :8000, stripping the `/api`
// prefix (so `/api/replays` -> `http://localhost:8000/replays`). This keeps the
// browser same-origin in dev, so no CORS config is needed (DESIGN.md §7).
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
