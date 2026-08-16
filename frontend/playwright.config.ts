// Playwright config (Task 19.12) — ONE browser journey over the real app.
//
// THE BROWSER IS PINNED, NOT ASSUMED. `@playwright/test` is held at an EXACT
// version in package.json (no `^`), because the Playwright version IS the
// browser version: 1.56.1 ships Chromium build 1194. That pin is what makes the
// run reproducible in three different places without any of them downloading a
// browser mid-test:
//   • the agent/dev container, whose preinstalled Chromium is build 1194 under
//     `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers` — Playwright resolves it with
//     no extra configuration precisely because the versions agree;
//   • CI, where `.github/workflows/ci.yml` caches `~/.cache/ms-playwright` on a
//     key derived from that exact version and installs only on a cache miss;
//   • a laptop, after one `npx playwright install chromium`.
// Bumping `@playwright/test` therefore means bumping a browser — do it
// deliberately, and expect the CI cache key to change with it.
//
// FLAKE POSTURE (the implementation hint's warning: flake here poisons the whole
// gate's credibility):
//   • ONE worker, no parallelism. The specs share one dev server and one
//     backend; concurrent replay loads would interleave for no benefit on a
//     suite this size.
//   • Exactly ONE retry in CI, none locally. A local retry hides a real bug from
//     the person able to fix it; more than one in CI turns a flaky test into a
//     silent pass.
//   • Condition-based waits only. There is no `waitForTimeout` anywhere in
//     `e2e/` — every wait is `expect(locator).toBeVisible()` against a state the
//     app actually reaches. The one time-shaped wait is the autoplay assertion,
//     and it is expressed as a generous ASSERTION timeout, not a sleep.
//   • `trace: "retain-on-failure"` so a CI failure arrives with a timeline
//     instead of a screenshot and a guess.

import { defineConfig } from "@playwright/test";

// The two servers the journey drives. Ports match `scripts/run_spectator.sh`
// (8000 API, 5173 Vite) so the local on-demand run and the CI run exercise the
// same topology the project documents.
const API_PORT = 8000;
const UI_PORT = 5173;

export default defineConfig({
  testDir: "./e2e",
  // Artifacts live UNDER `e2e/` rather than in Playwright's default
  // `test-results/` + `playwright-report/` at the package root: the browser leg
  // owns them, `e2e/.gitignore` keeps them out of the index in one place, and
  // nothing new appears beside `src/` and `dist/` for a reader to wonder about.
  outputDir: "./e2e/.artifacts",
  // One spec, one worker: the journey is a sequence, not a matrix.
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  // `forbidOnly` keeps a stray `test.only` from silently shrinking the CI leg to
  // one test that passes.
  forbidOnly: Boolean(process.env.CI),
  timeout: 90_000,
  expect: { timeout: 15_000 },
  reporter: process.env.CI
    ? [["list"], ["html", { open: "never", outputFolder: "./e2e/.report" }]]
    : [["list"]],
  use: {
    baseURL: `http://127.0.0.1:${UI_PORT}`,
    browserName: "chromium",
    headless: true,
    viewport: { width: 1440, height: 960 },
    trace: "retain-on-failure",
    video: "off",
  },
  webServer: [
    {
      // The spectator API, serving the COMMITTED sample sets. `AILIBI_REPLAY_DIR`
      // is set explicitly for the same reason `run_spectator.sh` sets it: the
      // loader's fallthrough would otherwise prefer a local `./replays` scratch
      // dir, and the journey asserts on a specific curated game.
      command: "uv run uvicorn api.main:app --port 8000",
      cwd: "..",
      env: { AILIBI_REPLAY_DIR: "replays/samples" },
      url: `http://127.0.0.1:${API_PORT}/health`,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      stdout: "pipe",
      stderr: "pipe",
    },
    {
      command: "npm run dev",
      url: `http://127.0.0.1:${UI_PORT}/`,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      stdout: "pipe",
      stderr: "pipe",
    },
  ],
});
