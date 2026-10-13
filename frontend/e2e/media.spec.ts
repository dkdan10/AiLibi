// The README's pictures, captured from the committed bytes.
//
// INERT BY DEFAULT. Nothing here runs without `AILIBI_CAPTURE_MEDIA=1`, so the
// standing browser leg (`npm run e2e`, the `frontend-e2e` CI job) pays only for
// the skip. This is a CAPTURE tool that happens to be written as a spec — it
// writes into `docs/media/`, which no gate may ever do on its own.
//
// EVERY CAPTION IS A CHECKED CLAIM. The README's sentences about these pictures
// are asserted here against the served bytes before anything is shot: the two
// halves are the same tick of the same game, the fog subject is a crewmate who
// could see one player and no bodies, both impostors are on the omniscient half,
// and the quoted accusation is read out of the replay rather than typed. A
// capture that cannot make those claims true fails instead of publishing.
//
// WHAT IT SHOOTS, against the built static demo bundle (so every picture is a
// picture of the artifact a reader can build in one command):
//   • spectator-two-truths.png — one tick twice: the omniscient map beside the
//     same tick under one crewmate's fog, with that crewmate's accusation from
//     the following meeting composited underneath.
//   • spectator-meeting.png — the meeting still, mid-deliberation.
//   • spectator-journey.gif — the walk from the opening tick to the first
//     meeting as still frames, which GitHub plays inline in the README.
//
// DETERMINISM. Every asset is shot under `prefers-reduced-motion: reduce`, which
// is what the map layer reads to snap token tweens and freeze the kill ring, so
// two runs produce the same bytes.
//
// Task 20.39; the recipe and every asset's provenance live in docs/media/README.md.

import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import {
  createReadStream,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { createServer } from "node:http";
import type { Server } from "node:http";
import type { AddressInfo } from "node:net";
import { tmpdir } from "node:os";
import { extname, join, resolve, sep } from "node:path";

import { expect, test as base } from "@playwright/test";
import type { Browser, Page } from "@playwright/test";

/** The capture writes into the repository, so it never runs unasked. */
const CAPTURE_REQUESTED = process.env.AILIBI_CAPTURE_MEDIA === "1";

const REPO_ROOT = resolve(import.meta.dirname, "..", "..");
const MEDIA_DIR = join(REPO_ROOT, "docs", "media");

/** The first-run tour's "seen" key (frontend/src/components/GuidedTour.tsx). */
const TOUR_SEEN_KEY = "ailibi.guidedTourSeen.v1";

/** Enough for `npm run build` plus the engine re-walk of every committed recording. */
const BUILD_TIMEOUT_MS = 300_000;

/**
 * The moment the hero pictures, chosen from the recorded corpus this repository
 * ships and re-checked against those bytes below.
 *
 * 9p2i seed 19 is the game the guided tour opens on in the shown 9-player set,
 * the first entry of FEATURED_GAMES (ReplayPicker.tsx); this capture names its
 * game id directly and does not read that list. At tick 9 the omniscient map
 * carries two bodies and both impostors: one in Medbay with the player it has
 * just killed, the other inside the vents between Storage and Engineering. The
 * fog subject, in Labs, saw one other player and none of it, and then spent the
 * meeting at tick 12 accusing that fellow crewmate — which is the whole point of
 * the picture.
 */
const HERO = {
  set: "9p2i",
  gameId: "headless-seed-19",
  tick: 9,
  fogSubject: "p-5",
  accused: "p-4",
  meetingId: "headless-seed-19:meeting-0",
  meetingTick: 12,
  /** Bodies on the omniscient half at `tick` — the caption's "two players are already dead". */
  bodies: 2,
  /** Players the fog subject can see at `tick` — the caption's "one other player". */
  fogSubjectSees: 1,
} as const;

/** Both halves and both stills are shot here; the dock must clear the map. */
const SHOT_VIEWPORT = { width: 1440, height: 900 } as const;

/**
 * The sheet's layout, in CSS pixels.
 *
 * The parts are shot at twice this density, so every image lands on the sheet
 * either 1:1 or supersampled — never upscaled, which is what made the first cut
 * of the accusation card look soft.
 */
const SHEET = { halfWidth: 980, cardWidth: 980, pad: 28, gap: 20 } as const;

/**
 * How the sheet's parts are shot: the capture viewport, at twice its density.
 *
 * `reducedMotion` is the determinism knob — the map layer reads that preference
 * directly to snap token tweens and freeze the kill ring, so it is what makes two
 * runs of this capture produce the same bytes.
 */
const PART_CONTEXT = {
  viewport: { ...SHOT_VIEWPORT },
  deviceScaleFactor: 2,
  reducedMotion: "reduce",
} as const;

/** The GIF: the walk as stills, at the pace the transport plays it. */
const GIF_WIDTH = 640;
const GIF_FRAME_MS = 500;

/** Budgets the PR quotes; `docs/media/README.md` records them too. */
const STILL_MAX_BYTES = 400_000;
const GIF_MAX_BYTES = 1_500_000;

// ─────────────────────────────────────────────────────────────────────────────
// The bundle: built from committed bytes, served over loopback
// ─────────────────────────────────────────────────────────────────────────────

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

/** A static file server over one directory: the whole backend a capture needs. */
function serveStatic(root: string): Promise<{ server: Server; origin: string }> {
  const server = createServer((request, response) => {
    const requested = new URL(request.url ?? "/", "http://localhost");
    const relative = decodeURIComponent(requested.pathname).replace(/^\/+/, "");
    const filePath = relative === "" ? join(root, "index.html") : join(root, relative);
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
  return new Promise((settle) => {
    server.listen(0, "127.0.0.1", () => {
      const { port } = server.address() as AddressInfo;
      settle({ server, origin: `http://127.0.0.1:${port}` });
    });
  });
}

/** The served bundle: where it lives on disk, and the origin serving it. */
interface ServedBundle {
  readonly origin: string;
  readonly dir: string;
}

const test = base.extend<object, { bundle: ServedBundle }>({
  bundle: [
    // eslint-disable-next-line no-empty-pattern
    async ({}, provide) => {
      const prebuilt = process.env.AILIBI_DEMO_BUNDLE_DIR;
      const reusing = prebuilt !== undefined && prebuilt !== "";
      const bundleDir = reusing
        ? prebuilt
        : mkdtempSync(join(tmpdir(), "ailibi-media-bundle-"));
      if (!reusing) {
        buildBundle(bundleDir);
      }
      const root = resolve(bundleDir);
      const { server, origin } = await serveStatic(root);
      try {
        await provide({ origin, dir: root });
      } finally {
        await new Promise<void>((done) => {
          server.close(() => {
            done();
          });
        });
        if (!reusing) {
          rmSync(bundleDir, { recursive: true, force: true });
        }
      }
    },
    { scope: "worker", timeout: BUILD_TIMEOUT_MS },
  ],
});

// ─────────────────────────────────────────────────────────────────────────────
// The bytes the pictures are pictures of
// ─────────────────────────────────────────────────────────────────────────────

interface BakedTurn {
  readonly speaker: string;
  readonly free_text: string;
  readonly claims: readonly { readonly type: string; readonly against?: string }[];
}

interface BakedReplay {
  readonly players: readonly { readonly agent_id: string; readonly role: string }[];
  readonly meetings: readonly {
    readonly meeting_id: string;
    readonly tick: number;
    readonly turns: readonly BakedTurn[];
  }[];
  readonly ticks: readonly {
    readonly tick: number;
    readonly events: readonly { readonly type: string; readonly killer_id?: string }[];
    readonly bodies: readonly { readonly victim_id: string }[];
    readonly agent_states: readonly {
      readonly agent_id: string;
      readonly room_id: string | null;
      readonly is_alive: boolean;
      readonly visibility: {
        readonly visible_players: readonly { readonly id: string }[];
        readonly visible_bodies: readonly { readonly victim_id: string }[];
      } | null;
    }[];
  }[];
}

/** The replay JSON the served bundle bakes — the same bytes the page fetches. */
function bakedReplay(bundle: ServedBundle): BakedReplay {
  const path = join(bundle.dir, "data", HERO.set, "replays", `${HERO.gameId}.json`);
  return JSON.parse(readFileSync(path, "utf-8")) as BakedReplay;
}

// ─────────────────────────────────────────────────────────────────────────────
// Driving the app
// ─────────────────────────────────────────────────────────────────────────────

/** The eight round-tripping URL keys are the whole deep-link API (lib/playback.ts). */
function momentUrl(
  origin: string,
  extra: Readonly<Record<string, string>> = {},
): string {
  const params = new URLSearchParams({
    set: HERO.set,
    game_id: HERO.gameId,
    tick: String(HERO.tick),
    ...extra,
  });
  return `${origin}/?${params.toString()}`;
}

/** Land on a deep-linked moment with the map painted and its fonts rasterised. */
async function openMoment(page: Page, url: string): Promise<void> {
  await page.addInitScript((key) => {
    window.localStorage.setItem(key, "1");
  }, TOUR_SEEN_KEY);
  await page.goto(url);
  await expect(page.locator("[data-transport-region]")).toBeVisible();
  await expect(page.locator("canvas")).toBeVisible();
  // The scrubber holds the FRAME index and the URL holds the ENGINE tick; the
  // walk opens at tick -1, so the two differ by one. Asserting the join here is
  // what makes "this picture is of that tick" true of the pixels, not just of
  // the address bar.
  const tick = Number(new URL(url).searchParams.get("tick"));
  await expect(page.getByLabel("Seek tick")).toHaveValue(String(tick + 1));
  // The map layer redraws once the web fonts land (MapView's font nudge). Shoot
  // before that and the labels are rasterised in a fallback face, which is both
  // ugly and the one thing that would differ between two runs.
  await page.evaluate(async () => {
    await document.fonts.ready;
  });
}

/**
 * The map's box and the dock's, so a capture can refuse to shoot a covered map.
 *
 * `.map-canvas-fill` is the map's stable on-screen handle (src/index.css); the
 * Pixi canvas inside it is CSS-scaled to the stage width, so the wrapper IS the
 * map. Same shape the journey spec's geometry helpers use.
 */
async function mapAndDockGeometry(page: Page) {
  return page.evaluate(() => {
    const map = document.querySelector(".map-canvas-fill");
    const dock = document.querySelector("[data-transport-region]");
    if (map === null || dock === null) {
      throw new Error("the map wrapper or the transport region is not mounted");
    }
    const mapBox = map.getBoundingClientRect();
    const dockBox = dock.getBoundingClientRect();
    return {
      mapTop: Math.round(mapBox.top),
      mapBottom: Math.round(mapBox.bottom),
      mapWidth: Math.round(mapBox.width),
      dockTop: Math.round(dockBox.top),
      dockContentHeight: dock.clientHeight,
      viewportHeight: window.innerHeight,
      transportH: Number.parseFloat(
        getComputedStyle(document.documentElement).getPropertyValue("--transport-h"),
      ),
    };
  });
}

/**
 * Put the map at the top of the viewport and shoot it — but only once the dock's
 * published height has settled and the dock is genuinely clear of the canvas.
 *
 * This is the finding the whole task exists for: the retired GIF was recorded at
 * a viewport where the fixed dock covered the canvas entirely, so the one asset
 * most readers ever saw contained no map at all. A capture that cannot see the
 * map must fail, not ship.
 */
async function uncoverMap(page: Page): Promise<void> {
  const disclosure = page.getByRole("button", { name: "Timeline", exact: true });
  if ((await disclosure.getAttribute("aria-expanded")) === "true") {
    await disclosure.click();
    await expect(disclosure).toHaveAttribute("aria-expanded", "false");
  }
  await page.evaluate(() => {
    window.scrollTo(0, 0);
  });
  // Wait for the dock's ResizeObserver to republish its height before believing
  // any of the numbers below — `--transport-h` is what the layout reserves.
  await expect
    .poll(async () => {
      const geometry = await mapAndDockGeometry(page);
      return Math.abs(geometry.transportH - geometry.dockContentHeight);
    })
    .toBeLessThanOrEqual(1);
  const geometry = await mapAndDockGeometry(page);
  expect(geometry.mapTop).toBeGreaterThanOrEqual(0);
  expect(geometry.mapBottom).toBeLessThanOrEqual(geometry.dockTop);
  expect(geometry.mapWidth).toBeGreaterThan(0);
}

async function shootMap(page: Page): Promise<Buffer> {
  await uncoverMap(page);
  return page.locator(".map-canvas-fill").screenshot({ animations: "disabled" });
}

// ─────────────────────────────────────────────────────────────────────────────
// The composite sheet
// ─────────────────────────────────────────────────────────────────────────────

/** The bundle's own stylesheet, so the sheet is set in the product's faces. */
function bundleStylesheet(bundle: ServedBundle): string {
  const html = readFileSync(join(bundle.dir, "index.html"), "utf-8");
  const match = /<link rel="stylesheet"[^>]*href="\.?\/?([^"]+\.css)"/.exec(html);
  if (match?.[1] === undefined) {
    throw new Error("the built bundle has no stylesheet to borrow");
  }
  return `/${match[1]}`;
}

function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

interface SheetCopy {
  readonly leftLabel: string;
  readonly rightLabel: string;
  readonly caption: string;
}

/**
 * Lay the two halves side by side with the accusation card underneath, and shoot
 * the sheet.
 *
 * Assembled as a page rather than in an image library because the halves are
 * already browser pixels and the labels have to be set in the same faces as the
 * product — one more renderer in the pipeline would be one more thing to keep in
 * step with the design tokens.
 */
async function shootSheet(
  browser: Browser,
  bundle: ServedBundle,
  parts: { left: Buffer; right: Buffer; card: Buffer },
  copy: SheetCopy,
): Promise<Buffer> {
  const sheetDir = join(bundle.dir, "_media");
  mkdirSync(sheetDir, { recursive: true });
  writeFileSync(join(sheetDir, "left.png"), parts.left);
  writeFileSync(join(sheetDir, "right.png"), parts.right);
  writeFileSync(join(sheetDir, "card.png"), parts.card);
  const width = SHEET.pad * 2 + SHEET.halfWidth * 2 + SHEET.gap;
  writeFileSync(
    join(sheetDir, "sheet.html"),
    `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<link rel="stylesheet" href="${bundleStylesheet(bundle)}">
<style>
  html, body { margin: 0; background: var(--color-paper-2, #efe7d7); }
  .sheet { display: inline-block; padding: ${String(SHEET.pad)}px; }
  .halves { display: flex; gap: ${String(SHEET.gap)}px; align-items: flex-start; }
  .half { display: flex; flex-direction: column; gap: 10px; }
  .half img {
    display: block; width: ${String(SHEET.halfWidth)}px; height: auto;
    border: 2px solid var(--color-ink-900, #1a1a1a); border-radius: 12px;
  }
  .label {
    font-family: Fredoka, ui-sans-serif, system-ui, sans-serif; font-weight: 600;
    font-size: 22px; color: var(--color-ink-900, #1a1a1a);
  }
  /* The accusation belongs to the fog half, so it sits under it. */
  .card { margin-top: 22px; display: flex; justify-content: flex-end; }
  .card img {
    display: block; width: ${String(SHEET.cardWidth)}px; height: auto;
    border-radius: 12px;
  }
  .caption {
    margin: 20px 0 0; width: ${String(SHEET.halfWidth * 2 + SHEET.gap)}px;
    font-family: Fredoka, ui-sans-serif, system-ui, sans-serif; font-size: 22px;
    line-height: 1.45; color: var(--color-ink-700, #3a3a3a);
  }
</style></head>
<body><div class="sheet" id="sheet">
  <div class="halves">
    <div class="half"><div class="label">${escapeHtml(copy.leftLabel)}</div><img src="left.png" alt=""></div>
    <div class="half"><div class="label">${escapeHtml(copy.rightLabel)}</div><img src="right.png" alt=""></div>
  </div>
  <div class="card"><img src="card.png" alt=""></div>
  <p class="caption">${escapeHtml(copy.caption)}</p>
</div></body></html>`,
  );

  const context = await browser.newContext({
    viewport: { width: width + 40, height: 1400 },
    reducedMotion: "reduce",
  });
  try {
    const page = await context.newPage();
    await page.goto(`${bundle.origin}/_media/sheet.html`);
    await page.evaluate(async () => {
      await document.fonts.ready;
    });
    const sheet = page.locator("#sheet");
    await expect(sheet).toBeVisible();
    return await sheet.screenshot({ animations: "disabled" });
  } finally {
    await context.close();
  }
}

/**
 * Re-encode a PNG against a 256-colour median-cut palette.
 *
 * The product's design is flat colour, so this is invisible on the page and
 * roughly halves the file — which is what keeps a sheet wide enough to read when
 * clicked through inside the README's size budget.
 */
function flattenPng(path: string): void {
  const script = `
import sys
from PIL import Image

path = sys.argv[1]
image = Image.open(path).convert("RGB")
colors = set(image.getdata())
unique = Image.new("RGB", (len(colors), 1))
unique.putdata(sorted(colors))
palette = unique.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
image.quantize(palette=palette, dither=Image.Dither.NONE).save(path, optimize=True)
`;
  const result = spawnSync("uv", ["run", "--with", "pillow", "python", "-", path], {
    cwd: REPO_ROOT,
    input: script,
    encoding: "utf-8",
    timeout: 300_000,
  });
  if (result.status !== 0) {
    throw new Error(
      `PNG flattening failed (status ${String(result.status)}):\n` +
        `${result.stdout ?? ""}\n${result.stderr ?? ""}`,
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Assembling the GIF
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Assemble a GIF from still frames with Pillow, in an ephemeral environment.
 *
 * The palette is median-cut over the frames' UNIQUE colours, not over the frames
 * themselves: an area-weighted palette spends all 256 slots on the cream-and-ink
 * chrome and flattens the per-player identity hues to grey, which silently breaks
 * the viewer's identity grammar in the one image most readers ever see.
 */
function assembleGif(frames: readonly Buffer[], width: number, out: string): void {
  const frameDir = mkdtempSync(join(tmpdir(), "ailibi-gif-frames-"));
  try {
    frames.forEach((frame, index) => {
      writeFileSync(join(frameDir, `f${String(index).padStart(4, "0")}.png`), frame);
    });
    const script = `
import pathlib, sys
from PIL import Image

frame_dir, out_path, width, frame_ms = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
paths = sorted(pathlib.Path(frame_dir).glob("*.png"))
frames = []
for path in paths:
    image = Image.open(path).convert("RGB")
    height = round(image.height * width / image.width)
    frames.append(image.resize((width, height), Image.LANCZOS))

colors = set()
for frame in frames:
    colors.update(frame.getdata())
unique = Image.new("RGB", (len(colors), 1))
unique.putdata(sorted(colors))
palette = unique.quantize(colors=256, method=Image.Quantize.MEDIANCUT)

flat = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
flat[0].save(
    out_path, save_all=True, append_images=flat[1:], duration=frame_ms, loop=0,
    optimize=True, disposal=2,
)
`;
    const result = spawnSync(
      "uv",
      [
        "run",
        "--with",
        "pillow",
        "python",
        "-",
        frameDir,
        out,
        String(width),
        String(GIF_FRAME_MS),
      ],
      { cwd: REPO_ROOT, input: script, encoding: "utf-8", timeout: 300_000 },
    );
    if (result.status !== 0) {
      throw new Error(
        `GIF assembly failed (status ${String(result.status)}):\n` +
          `${result.stdout ?? ""}\n${result.stderr ?? ""}`,
      );
    }
  } finally {
    rmSync(frameDir, { recursive: true, force: true });
  }
}

function digest(path: string): string {
  return createHash("sha256").update(readFileSync(path)).digest("hex").slice(0, 16);
}

function writeAsset(name: string, bytes: Buffer): string {
  const path = join(MEDIA_DIR, name);
  writeFileSync(path, bytes);
  return path;
}

// ─────────────────────────────────────────────────────────────────────────────
// The captures
// ─────────────────────────────────────────────────────────────────────────────

test.describe("README media capture", () => {
  test.skip(
    !CAPTURE_REQUESTED,
    "capture only: re-shoot the README assets with AILIBI_CAPTURE_MEDIA=1",
  );
  test.use({ viewport: { ...SHOT_VIEWPORT } });
  test.describe.configure({ mode: "serial", timeout: 300_000 });

  test("the hero: one tick, two truths", async ({ browser, bundle }) => {
    const replay = bakedReplay(bundle);

    // ── the moment, checked against the bytes rather than the caption ────────
    const fogRole = replay.players.find(
      (player) => player.agent_id === HERO.fogSubject,
    )?.role;
    expect(fogRole).toBe("CREWMATE");
    const heroFrame = replay.ticks.find((frame) => frame.tick === HERO.tick);
    expect(heroFrame, `the replay must reach tick ${String(HERO.tick)}`).toBeDefined();
    expect(heroFrame?.events.some((event) => event.type === "kill")).toBe(true);
    // "two players are already dead" — the caption's count, not a rounded one.
    expect(heroFrame?.bodies).toHaveLength(HERO.bodies);
    // Both impostors are alive and placed in a room this frame, one of them inside
    // a vent there; tests/scripts/test_public_recording_provenance.py holds the
    // caption's vent clause to the served bytes in every run.
    const impostors = replay.players
      .filter((player) => player.role === "IMPOSTOR")
      .map((player) => player.agent_id);
    expect(impostors.length).toBeGreaterThan(0);
    for (const agentId of impostors) {
      const state = heroFrame?.agent_states.find(
        (agent) => agent.agent_id === agentId,
      );
      expect(state?.is_alive, `${agentId} must be alive at the hero tick`).toBe(true);
      expect(state?.room_id, `${agentId} must be in a room at the hero tick`).not.toBeNull();
    }
    // "one lit room and one other player": the fog half's whole claim, read off
    // the same projection the right-hand capture renders.
    const fogState = heroFrame?.agent_states.find(
      (agent) => agent.agent_id === HERO.fogSubject,
    );
    expect(fogState?.is_alive).toBe(true);
    expect(fogState?.visibility?.visible_players).toHaveLength(HERO.fogSubjectSees);
    expect(fogState?.visibility?.visible_bodies).toHaveLength(0);

    const meeting = replay.meetings.find((each) => each.meeting_id === HERO.meetingId);
    expect(meeting, `${HERO.meetingId} must be the meeting that follows`).toBeDefined();
    expect(meeting?.tick).toBe(HERO.meetingTick);
    expect(meeting?.tick).toBeGreaterThan(HERO.tick);
    // …and nothing earlier, so "the meeting that followed" stays literally true.
    expect(
      replay.meetings.filter((each) => each.tick <= HERO.tick),
    ).toHaveLength(0);
    const turn = meeting?.turns.find((each) => each.speaker === HERO.fogSubject);
    expect(turn, `${HERO.fogSubject} must speak at that meeting`).toBeDefined();
    const accusation = turn?.claims.find((claim) => claim.type === "accusation");
    expect(accusation?.against).toBe(HERO.accused);
    const accusedRole = replay.players.find(
      (player) => player.agent_id === HERO.accused,
    )?.role;
    // The picture's whole argument: the fog subject accused an innocent.
    expect(accusedRole).toBe("CREWMATE");

    // ── left: what happened ──────────────────────────────────────────────────
    const omniscient = await browser.newContext({ ...PART_CONTEXT });
    const omniscientPage = await omniscient.newPage();
    await openMoment(omniscientPage, momentUrl(bundle.origin));
    await expect(omniscientPage.locator('[aria-label^="Perspective:"]')).toHaveText(
      "Omniscient",
    );
    const left = await shootMap(omniscientPage);
    const leftUrl = new URL(omniscientPage.url());
    await omniscient.close();

    // ── right: what the fog subject could see at the same tick ───────────────
    const fogged = await browser.newContext({ ...PART_CONTEXT });
    const foggedPage = await fogged.newPage();
    await openMoment(
      foggedPage,
      momentUrl(bundle.origin, { perspective: HERO.fogSubject }),
    );
    await expect(foggedPage.locator('[aria-label^="Perspective:"]')).toHaveText(
      `Watching as ${HERO.fogSubject}`,
    );
    const right = await shootMap(foggedPage);
    const rightUrl = new URL(foggedPage.url());
    await fogged.close();

    // "The same tick" is a CHECKED claim, not a caption: both halves round-trip
    // the same game and the same engine tick through the deep-link keys.
    expect(leftUrl.searchParams.get("game_id")).toBe(HERO.gameId);
    expect(rightUrl.searchParams.get("game_id")).toBe(HERO.gameId);
    expect(leftUrl.searchParams.get("tick")).toBe(String(HERO.tick));
    expect(rightUrl.searchParams.get("tick")).toBe(String(HERO.tick));
    expect(leftUrl.searchParams.get("perspective")).toBeNull();
    expect(rightUrl.searchParams.get("perspective")).toBe(HERO.fogSubject);

    // ── underneath: the accusation that crewmate actually wrote ──────────────
    const meetingContext = await browser.newContext({ ...PART_CONTEXT });
    const meetingPage = await meetingContext.newPage();
    await openMoment(
      meetingPage,
      momentUrl(bundle.origin, { selectedMeeting: meeting?.meeting_id ?? "" }),
    );
    const dialog = meetingPage.getByRole("dialog");
    await expect(dialog).toBeVisible();
    // Located by the words the model actually wrote (read out of the bundle a
    // sentence ago), so the card in the picture cannot drift to another speaker.
    const opening = (turn?.free_text ?? "").slice(0, 60);
    const card = dialog.locator("article").filter({ hasText: opening });
    await expect(card).toHaveCount(1);
    await expect(card).toContainText(`accuses${HERO.accused}`);
    // The transcript column scrolls behind the fixed dock, so "scrolled into
    // view" is not the same as "on screen": the card has to end ABOVE the dock
    // or the capture would photograph the dock instead of the accusation.
    await card.evaluate((element) => {
      element.scrollIntoView({ block: "center", behavior: "instant" });
    });
    const cardBox = await card.boundingBox();
    const dockBox = await meetingPage.locator("[data-transport-region]").boundingBox();
    expect(cardBox).not.toBeNull();
    expect(dockBox).not.toBeNull();
    expect((cardBox?.y ?? 0) + (cardBox?.height ?? 0)).toBeLessThanOrEqual(
      dockBox?.y ?? 0,
    );
    expect(cardBox?.y ?? -1).toBeGreaterThanOrEqual(0);
    const cardShot = await card.screenshot({ animations: "disabled" });
    await meetingContext.close();

    // ── the sheet ────────────────────────────────────────────────────────────
    const sheet = await shootSheet(
      browser,
      bundle,
      { left, right, card: cardShot },
      {
        leftLabel: `What happened — tick ${String(HERO.tick)}`,
        rightLabel: `Everything ${HERO.fogSubject} could see — tick ${String(HERO.tick)}`,
        caption:
          `Left: what happened at tick ${String(HERO.tick)}. Right: what ${HERO.fogSubject} ` +
          `could see at the same tick. Below: the accusation ${HERO.fogSubject} wrote at ` +
          `the meeting that followed, at tick ${String(HERO.meetingTick)}.`,
      },
    );
    const path = writeAsset("spectator-two-truths.png", sheet);
    flattenPng(path);
    const size = statSync(path).size;
    console.log(
      `[media] spectator-two-truths.png ${String(size)} B sha256:${digest(path)}`,
    );
    expect(size).toBeLessThanOrEqual(STILL_MAX_BYTES);
  });

  test("the meeting still", async ({ browser, bundle }) => {
    const replay = bakedReplay(bundle);
    // Pinned to the meeting `docs/media/README.md` names, not to whichever one
    // happens to be first: the provenance tuple is part of the asset.
    const meeting = replay.meetings.find((each) => each.meeting_id === HERO.meetingId);
    expect(meeting, `${HERO.meetingId} must exist in the replay`).toBeDefined();
    expect(meeting?.tick).toBe(HERO.meetingTick);

    // A reduced-motion context, at the asset's own density: the same preference
    // the map layer reads, so re-shooting this still reproduces its bytes.
    const context = await browser.newContext({
      viewport: { ...SHOT_VIEWPORT },
      reducedMotion: "reduce",
    });
    const page = await context.newPage();
    // Opened AT the meeting's own tick, not merely with its modal on top: the
    // transport behind the dialog is in the picture, and `docs/media/README.md`
    // publishes this asset at the meeting's tick. `openMoment` asserts the
    // scrubber lands on the frame the URL names, so the deep link and the
    // pixels agree.
    await openMoment(
      page,
      momentUrl(bundle.origin, {
        tick: String(HERO.meetingTick),
        selectedMeeting: meeting?.meeting_id ?? "",
      }),
    );
    const dialog = page.getByRole("dialog", {
      name: `Meeting at tick ${String(HERO.meetingTick)}`,
    });
    await expect(dialog).toBeVisible();
    await expect(dialog.getByRole("region", { name: /^Ballots \(\d+\)$/ })).toBeVisible();
    await page.evaluate(async () => {
      await document.fonts.ready;
    });

    const shot = await page.screenshot({ animations: "disabled" });
    await context.close();
    const path = writeAsset("spectator-meeting.png", shot);
    const size = statSync(path).size;
    console.log(
      `[media] spectator-meeting.png ${String(size)} B sha256:${digest(path)}`,
    );
    expect(size).toBeLessThanOrEqual(STILL_MAX_BYTES);
  });

  test("the GIF", async ({ browser, bundle }) => {
    // ── the GIF: the walk to the first meeting, as frames GitHub renders ─────
    // Shot from the page rather than transcoded: frames off the page palettise
    // to a few dozen flat colours.
    const frames: Buffer[] = [];
    // Its own reduced-motion context: with the tween live, a frame shot between
    // two ticks catches tokens mid-flight, and the GIF stops being reproducible.
    const gifContext = await browser.newContext({ ...PART_CONTEXT });
    const gifPage = await gifContext.newPage();
    await openMoment(gifPage, momentUrl(bundle.origin, { tick: "0" }));
    await uncoverMap(gifPage);
    const gifSeek = gifPage.getByLabel("Seek tick");
    const forward = gifPage.getByRole("button", { name: "Step forward 1 tick" });
    for (let tick = 0; tick <= HERO.meetingTick; tick += 1) {
      await expect(gifSeek).toHaveValue(String(tick + 1));
      frames.push(await gifPage.screenshot({ animations: "disabled" }));
      if (tick < HERO.meetingTick) {
        await forward.click();
      }
    }
    // The meeting the walk stops at, held for a beat so a reader can read it.
    await expect(gifPage.getByRole("dialog")).toBeVisible();
    const meetingFrame = await gifPage.screenshot({ animations: "disabled" });
    frames.push(meetingFrame, meetingFrame, meetingFrame, meetingFrame);
    await gifContext.close();

    const gifPath = join(MEDIA_DIR, "spectator-journey.gif");
    assembleGif(frames, GIF_WIDTH, gifPath);
    const gifSize = statSync(gifPath).size;
    console.log(
      `[media] spectator-journey.gif ${String(gifSize)} B ` +
        `${String(frames.length)} frames sha256:${digest(gifPath)}`,
    );
    expect(gifSize).toBeLessThanOrEqual(GIF_MAX_BYTES);
  });
});
