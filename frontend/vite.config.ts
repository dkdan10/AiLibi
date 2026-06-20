import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react-swc";
import { defineConfig } from "vite";

// Dev server proxies `/api/*` to the FastAPI app on :8000, stripping the `/api`
// prefix (so `/api/replays` -> `http://localhost:8000/replays`). This keeps the
// browser same-origin in dev, so no CORS config is needed (DESIGN.md §7).
//
// Code-split (Task 12.11; design/phase-12/stage-1-design.md §9): split the heavy
// vendors into their own chunks and lazy-load the route-level surfaces
// (Dashboard / Highlights / the Pixi map) in App.tsx so the initial download is
// the shell, not one 859 kB monolith. `manualChunks` carves react-dom and Pixi
// out of the app chunk; the lazy boundaries push Pixi behind the map route so it
// is fetched only when a replay opens. The combination keeps every emitted chunk
// under Vite's 500 kB warning threshold.
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
  build: {
    rollupOptions: {
      output: {
        // Vendor chunking. react-dom is carved into its own long-lived cache
        // chunk. Pixi is intentionally NOT forced into a single chunk: as one
        // chunk it is ~640 kB (over the warning limit), so it is left for
        // rolldown to split by subsystem — and because the only importer
        // (`MapView`) is behind a `React.lazy` boundary in App.tsx, those Pixi
        // pieces land in async chunks fetched only when a replay opens. Every
        // emitted chunk then stays under the 500 kB threshold.
        manualChunks(id) {
          if (!id.includes("node_modules")) {
            return undefined;
          }
          // Match the bare react packages by their full `node_modules/<pkg>/`
          // path so `@pixi/react` (which also contains "/react/") is NOT pulled
          // in — that would drag all of pixi.js into this chunk and blow past the
          // 500 kB limit. Pixi is left unassigned so it splits into async chunks
          // behind the lazy MapView route.
          if (
            id.includes("/node_modules/react/") ||
            id.includes("/node_modules/react-dom/") ||
            id.includes("/node_modules/scheduler/")
          ) {
            return "react-vendor";
          }
          return undefined;
        },
      },
    },
  },
});
