// THE ARTIFACT journey (Task 19.13) — the same featured walk as `journey.spec.ts`,
// but driven against the BUILT static demo bundle instead of the dev server, with
// every `/api` request blocked at the network layer.
//
// WHY A SECOND BROWSER SPEC. `scripts/build_demo_bundle.py` has Python tests, and
// they prove the builder writes the files it claims to. They cannot prove the
// thing that actually matters about a shippable artifact: that the built bundle
// PLAYS — that the seam in `api/client.ts` really compiled into the emitted JS,
// that the baked file names really are the ones the client asks for, that the
// relative asset base really survives being served from a plain file server, and
// that none of it quietly falls back to the API that is not there. Only a browser
// against the real output can say that, so this spec exercises the artifact
// itself.
//
// NO API, PROVEN TWICE. First structurally: the bundle is served by the ~40-line
// static file server below — no uvicorn, no Vite, no proxy, nothing that COULD
// answer `/api`. Then by assertion: every request the page makes is intercepted,
// anything under `/api` is aborted and recorded, and the journey must still
// complete with that list empty. Aborting rather than merely counting is what
// makes it a real firewall — if the bundle ever regressed to calling the API, the
// walk would fail on the missing data rather than passing on a lucky cache.
//
// NO SLEEPS, same as the sibling spec: every wait is an `expect` against a state
// the app genuinely reaches.

import { spawnSync } from "node:child_process";
import { createReadStream, existsSync, mkdtempSync, rmSync } from "node:fs";
import { createServer } from "node:http";
import type { AddressInfo } from "node:net";
import type { Server } from "node:http";
import { tmpdir } from "node:os";
import { extname, join, resolve, sep } from "node:path";

import { expect, test as base } from "@playwright/test";
import type { Page } from "@playwright/test";

/** The first-run tour's "seen" key (frontend/src/components/GuidedTour.tsx). */
const TOUR_SEEN_KEY = "ailibi.guidedTourSeen.v1";

const REPO_ROOT = resolve(import.meta.dirname, "..", "..");

// Enough for `npm run build` plus the engine re-walk of seven featured games on a
// cold CI runner. Measured locally at well under a minute.
const BUILD_TIMEOUT_MS = 300_000;

const CONTENT_TYPES: Readonly<Record<string, string>> = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".ico": "image/x-icon",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".map": "application/json; charset=utf-8",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".ttf": "font/ttf",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
};

/**
 * Build the bundle from committed bytes.
 *
 * Always rebuilt (unless `AILIBI_DEMO_BUNDLE_DIR` names one to reuse) — a cached
 * bundle from before the edit you are testing is the classic way for a browser
 * suite to go green on last week's code.
 */
function buildBundle(outDir: string): void {
  const result = spawnSync(
    "uv",
    ["run", "python", "scripts/build_demo_bundle.py", "--out", outDir],
    { cwd: REPO_ROOT, encoding: "utf-8", timeout: BUILD_TIMEOUT_MS },
  );
  if (result.status !== 0) {
    throw new Error(
      `scripts/build_demo_bundle.py failed (status ${String(result.status)}):\n` +
        `${result.stdout ?? ""}\n${result.stderr ?? ""}`,
    );
  }
}

/**
 * A static file server over one directory: the whole backend this artifact needs.
 *
 * Deliberately dumb — no rewrites, no SPA fallback, no proxy. The bundle is
 * supposed to work behind `python -m http.server`, so anything cleverer here
 * would be testing a server the reader will not have.
 */
function serveStatic(root: string): Promise<{ server: Server; origin: string }> {
  const server = createServer((request, response) => {
    const requested = new URL(request.url ?? "/", "http://localhost");
    const relative = decodeURIComponent(requested.pathname).replace(/^\/+/, "");
    const filePath = relative === "" ? join(root, "index.html") : join(root, relative);
    // Path-traversal guard: a resolved path must stay under the served root.
    if (filePath !== root && !filePath.startsWith(root + sep)) {
      response.writeHead(403).end("forbidden");
      return;
    }
    if (!existsSync(filePath)) {
      response.writeHead(404, { "content-type": "text/plain" }).end("not found");
      return;
    }
    response.writeHead(200, {
      "content-type":
        CONTENT_TYPES[extname(filePath).toLowerCase()] ?? "application/octet-stream",
    });
    createReadStream(filePath).pipe(response);
  });
  return new Promise((resolveServer) => {
    server.listen(0, "127.0.0.1", () => {
      const { port } = server.address() as AddressInfo;
      resolveServer({ server, origin: `http://127.0.0.1:${port}` });
    });
  });
}

/**
 * Block and record every `/api` request the page attempts.
 *
 * Returns the (expected empty) list, asserted at the end of each test.
 */
async function forbidApi(page: Page): Promise<string[]> {
  const attempted: string[] = [];
  await page.route("**/*", async (route) => {
    const url = route.request().url();
    if (new URL(url).pathname.startsWith("/api")) {
      attempted.push(url);
      await route.abort();
      return;
    }
    await route.continue();
  });
  return attempted;
}

/** The served bundle: an origin to browse, and the lifecycle behind it. */
interface ServedBundle {
  readonly origin: string;
}

/**
 * The bundle fixture — built once per worker, served, and torn down by Playwright.
 *
 * The server handle, the origin and "did we build this, so may we delete it"
 * were module-level `let`s. That is the module-level mutable state AGENTS.md
 * forbids, and it made the lifecycle implicit: teardown depended on bindings any
 * test could have reassigned, and a setup that threw halfway left a live server
 * with nothing tracking it. As a worker fixture the state is owned by the
 * fixture's own closure, teardown runs after `use` returns whatever the tests
 * did, and the tests receive an origin instead of reaching for a global.
 *
 * Worker-scoped, not test-scoped: the bundle costs a `vite build` plus an engine
 * re-walk of seven games, and paying that per test would triple it for nothing.
 */
// `provide`, not `use`: Playwright names this callback `use`, which collides
// with React's `use` hook and makes `react-hooks/rules-of-hooks` fire on the
// try/finally below. The parameter name is ours to choose, so choosing one that
// is not a hook name beats suppressing a rule that is doing its job elsewhere.
const test = base.extend<object, { bundle: ServedBundle }>({
  bundle: [
    // Playwright REQUIRES a destructuring pattern as the first parameter — it
    // parses the pattern to build the fixture dependency graph, and rejects a
    // plain identifier at runtime ("First argument must use the object
    // destructuring pattern"). This fixture depends on no other fixtures, so
    // the empty pattern IS the API here, not an oversight.
    // eslint-disable-next-line no-empty-pattern
    async ({}, provide) => {
      const prebuilt = process.env.AILIBI_DEMO_BUNDLE_DIR;
      const reusing = prebuilt !== undefined && prebuilt !== "";
      // A temp dir, NOT a path under `frontend/`: the bundle is ~8 MB of built
      // output, and anything living inside the package gets swept up by the
      // repo's own tooling (eslint walks `e2e/`, and a `dist/`-shaped ignore
      // would have to be maintained in three config files for output nobody
      // keeps).
      const bundleDir = reusing
        ? prebuilt
        : mkdtempSync(join(tmpdir(), "ailibi-demo-bundle-"));
      if (!reusing) {
        buildBundle(bundleDir);
      }
      const { server, origin } = await serveStatic(resolve(bundleDir));
      try {
        await provide({ origin });
      } finally {
        await new Promise<void>((done) => {
          server.close(() => {
            done();
          });
        });
        // Only a bundle THIS run built is ours to delete; a caller-supplied one
        // is never removed underneath them.
        if (!reusing) {
          rmSync(bundleDir, { recursive: true, force: true });
        }
      }
    },
    { scope: "worker", timeout: BUILD_TIMEOUT_MS },
  ],
});

/** Land on the head of the curated featured list, and return the seed it opened. */
async function openFeaturedReplay(page: Page, origin: string): Promise<number> {
  // Suppressed for the same reason as in `journey.spec.ts`: on a virgin visit the
  // tour AUTO-LOADS its own teaching seed, and two replay loads in flight make
  // "which game am I looking at" a race.
  await page.addInitScript((key) => {
    window.localStorage.setItem(key, "1");
  }, TOUR_SEEN_KEY);
  await page.goto(`${origin}/`);

  const featured = page.getByRole("region", { name: "Featured games" });
  await expect(featured).toBeVisible();
  const head = featured.getByRole("listitem").first().getByRole("button");
  const seedLabel = await head.locator("span").first().innerText();
  const seed = Number(seedLabel.replace(/[^0-9]/g, ""));
  expect(Number.isFinite(seed)).toBe(true);

  await head.click();
  await expect(page.locator("[data-transport-region]")).toBeVisible();
  await expect(page.locator("canvas")).toBeVisible();
  return seed;
}

test.describe("static demo bundle", () => {
  test("the built bundle plays the featured journey with ZERO /api requests", async ({
    page,
    bundle,
  }) => {
    const apiAttempts = await forbidApi(page);
    const pageErrors: string[] = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));

    const seed = await openFeaturedReplay(page, bundle.origin);

    // The data really came from `data/*.json`: the header names the seed the
    // featured card opened, and the outcome is gated exactly as it is live.
    const banner = page
      .locator("header")
      .filter({ has: page.locator('[aria-label^="Perspective:"]') });
    await expect(banner).toContainText(`seed ${seed}`);
    await expect(banner).toContainText("outcome hidden");

    // ── play → the meeting pause ─────────────────────────────────────────────
    await page.getByRole("button", { name: "▶ Play" }).click();
    const pauseBar = page.getByRole("status").filter({ hasText: "playback paused" });
    await expect(pauseBar).toBeVisible({ timeout: 60_000 });
    await expect(pauseBar).toContainText(/Meeting at tick \d+ — playback paused/);

    // ── the meeting's own payload ────────────────────────────────────────────
    // Auto-follow opened it. Ballots are a SEPARATE baked file from the replay
    // view (`…/meetings/<id>.json`), so this is the step that proves the meeting
    // endpoint's file names survived the URL→filename reduction.
    const meeting = page.getByRole("dialog");
    await expect(meeting).toBeVisible();
    const ballots = meeting.getByRole("region", { name: /^Ballots \(\d+\)$/ });
    await expect(ballots).toBeVisible();
    await expect(ballots).toContainText("confidence");

    // ── to the finale ────────────────────────────────────────────────────────
    await page.keyboard.press("Escape");
    await expect(meeting).toBeHidden();
    await page.evaluate(() => {
      const active = document.activeElement;
      if (active instanceof HTMLElement) {
        active.blur();
      }
    });
    await page.keyboard.press("End");

    const frameIndex = page.getByLabel("Seek tick");
    const lastIndex = await frameIndex.getAttribute("max");
    await expect(frameIndex).toHaveValue(lastIndex ?? "");

    // Branch on the FRAME, not on the overlays — see `journey.spec.ts` for why
    // any overlay-keyed branch races auto-follow's effect on a meeting ending.
    const finale = page.getByRole("region", { name: "End of replay" });
    const endsOnMeeting = await page
      .locator("[data-transport-region]")
      .getByText("meeting", { exact: true })
      .isVisible();
    if (endsOnMeeting) {
      const showFinale = page.getByRole("button", { name: "Show finale" });
      await expect(showFinale).toBeVisible();
      await showFinale.click();
    }
    await expect(finale).toBeVisible();
    await expect(finale).toContainText("The game is over");
    await expect(finale).toContainText("The outcome is hidden");

    // ── reveal ───────────────────────────────────────────────────────────────
    await finale.getByRole("button", { name: "Reveal the outcome" }).click();
    await expect(finale).toContainText(/Crew win|Impostor win/);
    await expect(finale).toContainText("What they knew vs the truth");

    // THE POINT OF THIS FILE.
    expect(apiAttempts).toEqual([]);
    expect(pageErrors).toEqual([]);
  });

  test("the Belief × Truth hero reads its frames from the bundle", async ({
    page,
    bundle,
  }) => {
    // The belief frames are the one surface that fetches OUTSIDE `api/client`'s
    // methods (BeliefMatrix owns its own `fetch`), so it is the one most likely
    // to bypass the seam — hence its own case rather than a line in the walk.
    const apiAttempts = await forbidApi(page);
    await openFeaturedReplay(page, bundle.origin);

    await page.getByRole("button", { name: /Belief . Truth/ }).click();
    const panel = page.getByRole("dialog", { name: /Belief/ });
    await expect(panel).toBeVisible();
    // A rendered matrix, not an error card: observer rows are labelled by agent.
    await expect(panel.getByText(/^p-\d+$/).first()).toBeVisible();

    expect(apiAttempts).toEqual([]);
  });

  test("the bundle ships no aggregate report, and says so", async ({
    page,
    bundle,
  }) => {
    // Deliberate omission, not an oversight: the 9p2i tournament report is 29 MB.
    // The dashboard's existing first-class no-report panel is the honest state,
    // and pinning it here keeps the omission a DECISION rather than a surprise.
    const apiAttempts = await forbidApi(page);
    await page.addInitScript((key) => {
      window.localStorage.setItem(key, "1");
    }, TOUR_SEEN_KEY);
    await page.goto(`${bundle.origin}/`);

    await page.getByRole("button", { name: "Tournament" }).click();
    await expect(page.getByText("No tournament report.")).toBeVisible();

    expect(apiAttempts).toEqual([]);
  });
});
