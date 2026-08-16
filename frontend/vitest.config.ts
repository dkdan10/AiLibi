// Vitest config (Task 19.12) — the frontend's unit-test baseline.
//
// Deliberately SEPARATE from `vite.config.ts` rather than a `test` block inside
// it: the app config loads the React SWC and Tailwind plugins and carries the
// production `manualChunks` rollup wiring, none of which a pure-function unit
// run needs. Keeping them apart means `npm run test` never pays for the app's
// build graph, and a future change to the bundle's chunking cannot alter how
// tests resolve.
//
// `environment: "node"` is a CONTRACT, not a default we drifted into. The three
// suites this baseline lands are all DOM-free by construction:
//   • `src/lib/playback.test.ts`      — pure functions over the view-model.
//   • `src/store/replayStore.test.ts` — the store driven directly through
//     `getState()` / `setState()` with mocked API calls; the async-ordering
//     guards under test are plain closures, so proving them needs no renderer.
//   • `src/tokens.test.ts`            — reads `src/index.css` off disk.
// A test that needs a real DOM belongs in the Playwright journey (`e2e/`),
// which drives the actual app rather than a simulated document — so there is no
// jsdom/happy-dom dependency here, and adding one should be a deliberate act.

import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "node",
    include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
    // `e2e/` is Playwright's; it uses the same `test`/`expect` NAMES from a
    // different runner, so an accidental pickup here fails in a confusing way.
    exclude: ["node_modules/**", "dist/**", "e2e/**"],
    // No watch in CI or in `scripts/check.sh` — `npm run test` is `vitest run`.
    passWithNoTests: false,
  },
});
