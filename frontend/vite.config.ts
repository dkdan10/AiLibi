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
//
// Static demo bundle mode (Task 19.13). `scripts/build_demo_bundle.py` sets
// `VITE_AILIBI_STATIC_DATA=1` (Vite forwards `VITE_`-prefixed process env into
// `import.meta.env`, which is what flips `api/client.ts`'s data-source seam onto
// the pre-baked `./data/*.json`). The ONE thing the seam cannot do from inside
// the app is the asset base: Vite's default `/` emits absolute `/assets/…` URLs,
// which only resolve when the bundle is served from a server ROOT. A demo that is
// "playable from any static file server" has to survive a subdirectory too, so
// bundle builds emit RELATIVE asset URLs — matching the relative `./data/…` the
// seam fetches, from the same document base.
const STATIC_BUNDLE = process.env.VITE_AILIBI_STATIC_DATA === "1";

export default defineConfig({
  base: STATIC_BUNDLE ? "./" : "/",
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
