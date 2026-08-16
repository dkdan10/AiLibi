# docs/media — the committed captures

Two files, both shown at the top of the repository [README](../../README.md):

| File | What it is |
| --- | --- |
| `spectator-journey.gif` | 15 s, 8 fps, 640 px wide — the featured 9p2i journey end to end |
| `spectator-meeting.png` | 1440×900 — mid-deliberation: accusation chain, ballots, mind inspector |

Both are captures of the **static demo bundle**
(`scripts/build_demo_bundle.py`), not of a dev server. That is deliberate: the
picture in the README is then a picture of the artifact a reader can build and
run themselves in one command, and it cannot drift into showing a surface the
bundle does not ship.

Nothing regenerates these automatically. They are committed bytes, refreshed by
hand when the surface changes enough that they misrepresent it — a screenshot is
a claim about the product, and a stale one is a false claim.

## Recipe

The capture harness is intentionally NOT committed: it is a dozen lines of
throwaway Playwright driving the same journey `frontend/e2e/bundle.spec.ts`
already pins, and a second copy of that walk would be a second thing to keep in
sync. What is recorded here is the recipe, which is the part worth keeping.

1. **Build the bundle** — `uv run python scripts/build_demo_bundle.py --out /tmp/bundle`
2. **Serve it** on a loopback port (`python -m http.server -d /tmp/bundle 8080`).
3. **Drive it** with the Playwright installed under `frontend/`. `npm ci`
   installs the *package*, not the browser, so on a laptop this needs one
   `npx playwright install chromium` first — the same prerequisite
   `frontend/playwright.config.ts` documents. (In the agent/dev container it is
   a no-op: `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers` already holds the build
   the pinned version resolves to, which is why nothing downloads there — but
   the recipe should not assume you are in that container.) Then do exactly what
   `bundle.spec.ts` does: suppress the first-run tour
   (`localStorage["ailibi.guidedTourSeen.v1"] = "1"`, so the tour does not
   auto-load a second replay mid-capture), open the head of the featured strip,
   set the transport to 2×, press Play, let the meeting pause fire, `Escape` then
   `End`, then reveal the outcome. Record with a `recordVideo` context at
   1000×640 for the GIF; take the screenshot in a separate 1440×900 context with
   the meeting open (`]` jumps to the first meeting and opens it).
4. **Extract frames** — Playwright ships its own ffmpeg at
   `$PLAYWRIGHT_BROWSERS_PATH/ffmpeg-*/ffmpeg-linux`. It is a stripped build with
   **no GIF encoder and no `fps`/`palettegen` filters**, so use it only to demux:
   `ffmpeg -i capture.webm -r 8 -vf scale=640:-2 -f image2 frames/f%04d.png`.
5. **Assemble the GIF** with Pillow (`uv run --with pillow python …` — an
   ephemeral env, so this never touches `pyproject.toml`/`uv.lock`), 125 ms per
   frame, `dither=NONE`, and — the one non-obvious step — a palette built by
   median-cutting the **unique colours** of the frames rather than the frames
   themselves. An area-weighted palette spends all 256 slots on the cream/ink
   chrome and flattens the per-player identity hues to grey, which silently
   breaks the viewer's identity grammar in the one image most readers will ever
   see. Dithering costs ~3× the bytes for no legibility here — the design is
   flat colour.

Budget: keep the pair under a couple of MB (currently ~1.7 MB). Drop the
leading loading frames, and prefer a narrower GIF over a shorter one — the walk
is the point.
