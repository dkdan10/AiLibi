# docs/media — the committed pictures

Five assets, all of them shown in or linked from the repository
[README](../../README.md) — this note is the directory's sixth file:

| File | What it is |
| --- | --- |
| `spectator-two-truths.png` | 2036×850 — one tick shown twice: the omniscient map beside the same tick under one crewmate's fog, with the accusation that crewmate wrote at the meeting that followed |
| `spectator-meeting.png` | 1440×900 — mid-deliberation: accusation chain, ballots, mind inspector |
| `spectator-journey.gif` | 640×400, 8 frames — the walk from the first tick to the meeting the transport stops at |
| `spectator-journey.webm` | 1440×900, 9 s — the same walk recorded live: a token crossing rooms, the kill flash, the transport pausing itself, the flip into fog |
| `architecture.svg` | The layering as built — hand-authored, not captured: the packages, the data-flow arrows, and the barred import the observation firewall forbids |

The four spectator assets are captures of the **static demo bundle**
(`scripts/build_demo_bundle.py`), not of a dev server. That is deliberate: the
picture in the README is then a picture of the artifact a reader can build and
run themselves in one command, and it cannot drift into showing a surface the
bundle does not ship.

`architecture.svg` is not a capture at all: it is hand-written SVG text — real
`<text>`, no raster, no external font — so it diffs line by line and reads in
both GitHub themes, which its internal `prefers-color-scheme` block handles. The
rule for changing it: edit the file whenever the layering in
[`docs/architecture.md`](../architecture.md) moves, and keep the two saying the
same thing. `tests/scripts/test_check_doc_facts.py` pins the parse, the size
ceiling, the labels the picture has to carry, and the contrast of every ink
against the ground it really sits on — the backdrop composited over a light page
and over a dark one, because the picture's theme follows the reader's system and
the page around it need not. A silent drift into a raster export, a lost package
name or a washed-out palette fails the gate.

Nothing regenerates any of them automatically. They are committed bytes,
refreshed by hand when the surface changes enough that they misrepresent it — a
screenshot is a claim about the product, and a stale one is a false claim. That
standard cuts both ways: a capture is also a claim about a GAME, so when the
recorded corpus moves, every asset below has to be re-shot from the bytes the
repository now holds.

## Regenerating all four spectator assets

One command, from a checkout with the frontend set up
(`bash scripts/setup_env.sh`, plus one `npx playwright install chromium ffmpeg`
on a laptop — `npm ci` installs the Playwright *package*, not the browser or the
ffmpeg build it drives):

```bash
cd frontend && AILIBI_CAPTURE_MEDIA=1 npx playwright test e2e/media.spec.ts
```

`frontend/e2e/media.spec.ts` builds the demo bundle from the committed replays,
serves it on a loopback port, and shoots all four. Without
`AILIBI_CAPTURE_MEDIA=1` the file skips entirely, so the standing browser gate
(`npm run e2e`, the `frontend-e2e` CI job) never writes into this directory.
Set `AILIBI_DEMO_BUNDLE_DIR` to a bundle you already built to skip the rebuild.

The harness is committed, reversing the earlier call to keep it out of the tree.
The reason it is worth a file: a composite of two perspectives of one tick has to
PROVE the two halves are the same tick of the same game, name the fog subject,
and read the quoted accusation out of the replay rather than out of a caption —
and the recipe it replaced silently encoded a viewport where the transport dock
covered the whole map, so the asset most readers ever saw contained no map at
all. The capture now asserts the map is clear of the dock before it shoots, and
fails rather than shipping a picture of the dock.

### Provenance

Every spectator asset is a capture of **9p2i seed 2** (`headless-seed-2`) from
the baseline-7 record: recorded 2026-08-25 on `Qwen/Qwen3.6-27B` at prompt set
v4, $0, and listed in [`replays/samples/9p2i/MANIFEST.md`](../../replays/samples/9p2i/MANIFEST.md).

| Asset | Engine tick | Perspective | Capture viewport |
| --- | --- | --- | --- |
| `spectator-two-truths.png` | 5 (both halves), plus the meeting at tick 7 for the card | omniscient (left) and as-agent `p-3` (right) | 1440×900 at 2× density, laid out on a 2036 px sheet |
| `spectator-meeting.png` | 7 — meeting `headless-seed-2:meeting-0` open | omniscient | 1440×900 |
| `spectator-journey.gif` | 0 → 7 | omniscient | 1440×900 at 2× density, scaled to 640 wide |
| `spectator-journey.webm` | 1 → 7, then as-agent fog | omniscient, then as-agent | 1440×900 |

`p-3` is the fog subject because the picture's argument depends on it: at tick 5
`p-3` is a crewmate in MedBay who can see one other player, while the omniscient
half of the same tick carries two bodies and both impostors — and at the meeting
that follows, `p-3` accuses `p-1`, who is also a crewmate. The capture re-checks
each of those facts against the bundle's own replay JSON before it shoots, so the
caption is a checked claim rather than a remembered one.

### What is deterministic, and what is not

Two consecutive capture runs produce a byte-identical `spectator-two-truths.png`,
`spectator-meeting.png` and `spectator-journey.gif`. They are shot under
`prefers-reduced-motion: reduce`, which the map layer reads directly to snap
token tweens and freeze the kill ring.

`spectator-journey.webm` is deliberately the other case — the tween and the
pulsing kill ring are two of its four beats — so its bytes differ run to run.
What is fixed is its shape: the same 1440×900 frame size and the same 9.00 s
running time, because the published clip is the last nine seconds of a longer
recording rather than the recording itself.

That cut is checked against the clip's own bytes, not against a clock. Playwright
stretches a recording's final frame to the end of the capture, so a walk's
wall-clock offsets do not project into the container's timeline and arithmetic
cannot answer "is the last beat inside the cut". The capture instead decodes the
published clip's first and final frames and matches each against what the page
looked like at the first and last beat; if the fog flip has fallen past the cut,
the final frame resolves to the opening view and the capture fails.

### Why the clip is linked and the GIF is shown

GitHub's README renderer strips `<video>`. Checked, not assumed: a `<video>`
element pointing at a repository-relative path — `.webm` and `.mp4` alike —
renders as an empty paragraph both through the rendered-README API and on the
repository's own landing page. So the README shows the GIF, which renders, and
links the clip, which does not. Re-check this before swapping the two; if GitHub
ever starts rendering repository-relative video, the clip becomes the inline
asset and the GIF retires.

Budget: the directory is currently 1.4 MB. Keep the still under 400 kB, the clip
under 3 MB and the GIF under 1.5 MB — the capture asserts all three, so a walk
that grows past them fails instead of landing in the tree.
