# docs/media — the committed pictures

Five visual assets are kept here. The repository [README](../../README.md)
shows the two-perspective PNG and links the WebM clip. The architecture note
embeds the diagram; the meeting still and GIF are archive assets no page embeds.
The four spectator captures show the game the demo's guided tour opens on, 9p2i
seed 19 from the shown 9-player set, a game the current demo serves.
[provenance.json](provenance.json) identifies their source and exact asset bytes:

Placement below refers to the README and architecture note.

| File | What it is | Current placement |
| --- | --- | --- |
| `spectator-two-truths.png` | 2036×909 — the same scene through omniscient and crewmate views, with the following accusation | [README image](../../README.md) |
| `spectator-meeting.png` | 1440×900 — accusation chain, ballots and mind inspector | Archive only |
| `spectator-journey.gif` | 640×400, 13 frames — playback from the opening tick to a meeting | Archive only |
| `spectator-journey.webm` | 1440×900, 9 s — movement, a kill flash, a meeting pause and fog | [README clip link](../../README.md) |
| `architecture.svg` | Text SVG of the packages, data flow and observation firewall | [Architecture image](../architecture.md) |

The four spectator assets were captured from the **static demo bundle**
(`scripts/build_demo_bundle.py`) built at the capture revision below, whose
recordings are the ones the current checkout serves.

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
standard also applies to the recorded game: when the corpus changes, captures
must either be refreshed from the new bytes, as these were after the 9-player
set's promotion, or clearly labelled historical. A new capture must update the
provenance file and its captions.

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

Every spectator asset is a capture of **9p2i seed 19** (`headless-seed-19`)
from the shown 9-player set, recorded 2026-10-09 on `Qwen/Qwen3.6-27B` with v6
prompts and a v8 ballot, $0, under that set's declared experiment config. Its
[manifest](https://github.com/dkdan10/AiLibi/blob/5095a1c210d890d289405564d2af2607d2fbd4e9/replays/samples/9p2i/MANIFEST.md) and [source replay](https://github.com/dkdan10/AiLibi/blob/5095a1c210d890d289405564d2af2607d2fbd4e9/replays/samples/9p2i/replay-seed-19.jsonl) are pinned to the commit that landed those bytes.

Verify the source replay against the one this checkout serves:

```bash
shasum -a 256 replays/samples/9p2i/replay-seed-19.jsonl
```

The digest must equal `recording.sha256` in `provenance.json`.
`tests/scripts/test_public_recording_provenance.py` verifies each committed
asset digest, holds that digest to the served replay's bytes, and rejects a
changed image with unchanged provenance.

| Asset | Engine tick | Perspective | Capture viewport |
| --- | --- | --- | --- |
| `spectator-two-truths.png` | 9 (both halves), plus the meeting at tick 12 for the card | omniscient (left) and as-agent `p-5` (right) | 1440×900 at 2× density, laid out on a 2036 px sheet |
| `spectator-meeting.png` | 12 — meeting `headless-seed-19:meeting-0` open | omniscient | 1440×900 |
| `spectator-journey.gif` | 0 → 12 | omniscient | 1440×900 at 2× density, scaled to 640 wide |
| `spectator-journey.webm` | 1 → 12, then as-agent fog | omniscient, then as-agent | 1440×900 |

`p-5` is the fog subject because the picture's argument depends on it: at tick 9
`p-5` is a crewmate in Labs who can see one other player, while the omniscient
half of the same tick carries two bodies and both impostors — one in MedBay with
the player it has just killed, the other inside the vents — and at the meeting
that follows, `p-5` accuses `p-4`, who is also a crewmate. The capture harness
checks the body count, the kill, how many players `p-5` can see and the
accusation against the served bytes before shooting. The test suite reads each
claim of the README caption's scene, MedBay and the vent included, and holds it
to the same bytes in every run.

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

### Current README presentation

The README embeds `spectator-two-truths.png` and links
`spectator-journey.webm`; it does not embed the GIF or meeting still. Its caption
names the game, its set and its recording date, and the image links to the
interactive demo, which serves the same game.

Budget: the directory is currently 1.6 MB. Keep the still under 400 kB, the clip
under 3 MB and the GIF under 1.5 MB — the capture asserts all three, so a walk
that grows past them fails instead of landing in the tree.
