# The viewer header carries the tagline and a source link only

**Status:** ready

## Outcome

On 2026-10-10 the owner ruled on the live app's header, verbatim: "In the the live app, I think the "directed by
Daniel Keinan, Code and supporting material by Claude Code and Codex AI reviewed. Source & Ownership", Can be
removed. I like the "Recorded AI social deduction" and it can have a link to 'GitHub' that will still tell the full
story." When this card is done:

- The viewer header reads the title, the tagline "Recorded AI social deduction" and one link whose text is "GitHub",
  pointing at the repository. The attribution line (who directs the project, who wrote the code, that it was
  AI-reviewed, "Source & ownership") is gone from the header.
- The guided tour's welcome step, which carries the same attribution sentence, keeps its one link to the repository
  in plain words ("Read the source on GitHub") and drops the attribution sentence. This is the orchestrator's
  extension of the ruling to the second place the same words appear, stated in Results; the owner can reverse it by
  a word.
- Both strings live in `SPECTATOR_COPY` (a new `header` group), not as inline literals, with tests that hold the
  rendered header and the tour step to the copy and that fail if any attribution word returns.
- The committed journey GIF, whose frames show the header, is re-captured from the new head with its provenance and
  the media table; the two stills, which do not show the header, are re-captured in the same run so every asset
  carries one capture revision.

Nothing else on the front door or in the viewer changes. The ownership case study (`docs/ownership-case-study.md`)
and the README stay as they are; the repository tells the story the header no longer does.

## Evidence

- The header strip is an inline literal in `frontend/src/App.tsx:1201` (at `fa213381`): the tagline, "directed by
  Daniel Keinan", "Code and supporting material by Claude Code and Codex", "AI-reviewed" and the link "Source &
  ownership" to `https://github.com/dkdan10/AiLibi`. The header renders only while no meeting is open
  (`App.tsx:1199`).
- The tour's welcome step repeats the attribution in `frontend/src/components/GuidedTour.tsx:156-160`, also inline,
  with the link "Read the source and ownership case study."
- `frontend/src/lib/copy.ts` has no header or tour group (`SPECTATOR_COPY` at `:161`, groups exported at
  `:698-706`); `frontend/src/lib/copy.test.ts` holds the helpers `stringLeaves` (`:130`) and `proseLiterals`
  (`:432`) that the public results tab's copy-ownership cases use (`:439-527`).
- No test, story or e2e spec pins the strip or the tour sentence: `git grep -n -i -E 'directed by|AI-reviewed|Source &
  ownership' -- frontend tests` prints nothing at `fa213381`.
- The journey GIF is captured by full-page screenshots of the map view (`frontend/e2e/media.spec.ts:964`), so its
  frames show the header strip (frame 0 read count-only from `docs/media/spectator-journey.gif`); the meeting still
  is a full-page shot with the meeting dialog open (`:920`), where the header is hidden, and the two-truths still is
  composed from element shots (`:373`). `docs/media/provenance.json` names capture revision `58c7cf03`.

## Acceptance

Each item names its enforcing mechanism and the planted or perturbed case that turns its test red; each new test is
seen red before the code it guards exists.

- [x] **The header reads from the copy and carries no attribution.** `SPECTATOR_COPY.header` holds the tagline, the
  link text and the repository URL; `App.tsx` renders them and nothing else in the header's text. Mechanism: a
  render test of the header asserts the heading, the tagline and one link whose text and `href` equal the copy; a
  `copy.test.ts` case walks `SPECTATOR_COPY`'s string leaves (`stringLeaves`) for `directed by`, `Claude Code`,
  `Codex`, `AI-reviewed` and `ownership` (none), and a span case runs `proseLiterals` over the header JSX (empty).
  Planted: the old strip restored as a literal fails the span case; restored as a copy value fails the leaf walk,
  naming the key.
- [x] **The tour's welcome step keeps one plain link.** The attribution sentence is removed; the step reads its link
  text and URL from the copy. Mechanism: the tour's existing test (or a new case beside it) renders the welcome step
  and asserts the link text equals the copy and that the step's text contains no attribution word. Planted: the old
  sentence restored fails it.
- [x] **The media follow the header.** The journey GIF, the meeting still and the two-truths still are re-captured
  from the head's bytes by `frontend/e2e/media.spec.ts` in one run; `docs/media/provenance.json` names that capture
  revision and the new digests; the `docs/media/README.md` rows and the `docs/media` row of `docs/artifacts.md`
  are re-derived (bytes and file count). Mechanism: `test_media_hashes_and_labels_are_current` and
  `test_the_captions_scene_is_the_recorded_one` (`tests/scripts/test_public_recording_provenance.py:138`, `:411`)
  pass at H; a count-only read of the new GIF's first frame finds the header without the attribution line (state
  the method). Planted: one digest edited by one character in provenance fails the hash test. If a still's bytes
  did not change, Results says so.
- [x] **Nothing else moves.** `git diff --stat B H` lists only Expected scope's files; `README.md`,
  `docs/reading-guide.md`, `docs/glossary.md`, the public payload and every `data/` file of the bundle are untouched;
  `scripts/check_doc_facts.py` exits 0. Mechanism: the diff and the gate. Perturbed: a README caption tick edited by
  one in a scratch copy fails the caption test, so the unchanged pass is not vacuous.
- [x] **The live strings are stated, and the bundle diff.** The PR body lists every string that goes live, old against
  new, and the demo bundle diff built at B and at H in one checkout (`scripts/build_demo_bundle.py --out`; expected:
  compiled assets only, no `data/` file; the measured diff governs).
- [x] **One bounded mutation pass, and the gate record.** One pass over the listed classes (a dropped filter or wrapper,
  a swapped collection, a comparison made a None test, a kind or key read made a constant, a dropped tuple member,
  swapped branches, a loaded source read as its literal, message arguments) over the header render, the copy leaf
  walk and the tour step; survivors killed or reported. CI's green run at the exact head, cited by run id, is the
  gate record (memo 8.7 item 1); no local `check.sh` at the final head.

## Constraints

**Rules every change keeps.** User-facing copy lives in `SPECTATOR_COPY`, in plain words, with no task or audit id,
no unexplained term and no threshold arithmetic. Nothing in the engine, the agents, the meetings, the observation
layer, the prompts, a recording, a committed report, the corpus, an ML artifact, the scorecard, census or profile
pages, or the public payload moves. No new `AILIBI_*` lever and no prompt registry bump. Every production line has a
test that goes red when it is neutered; no test is weakened. No live provider call; `.env` is never read.

**Not in scope.** Any other header or tour wording; the ownership case study; the README and reading guide; the
dashboard, the belief panel, the badges and the skip tiles (held for the owner); the featured list and the curated
cases. If the welcome step's remaining text needs more than the attribution sentence removed to read well, stop and
ask rather than rewrite it.

**Process (memo 8.7).** CI is the gate record; message-argument survivors follow item 2. Never print a rendered
prompt, transcript text or seed-band prefix.

**One writer per file.** This card alone writes `App.tsx`, `GuidedTour.tsx`, `copy.ts`, `copy.test.ts`, the media
assets, `provenance.json`, `docs/media/README.md` and the media row of `docs/artifacts.md` while it is open.
`tasks/README.md` and this card's Status line are the orchestrator's, on `main`.

**Delivery and publication.** Branch `work/viewer-header-source-link`, one pull request into `main`, merged or
fast-forwarded, never squashed, never amended after push. Each commit body carries
`Card: tasks/work/viewer-header-source-link.md` immediately followed by the exact line
`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. The merge publishes the header and the tour copy in the
bundle and the re-captured media on GitHub through `.github/workflows/pages.yml`; the owner asked for this change on
2026-10-10, so the orchestrator merges it once the reviews pass and the PR body states the live strings.

## Expected scope

- Viewer: `frontend/src/App.tsx` (the header), `frontend/src/components/GuidedTour.tsx` (the welcome step),
  `frontend/src/lib/copy.ts` (the `header` group) and `frontend/src/lib/copy.test.ts`; one header render test beside
  `App.tsx` or in `frontend/src/components/`; the tour's test file if one exists.
- Media: `docs/media/spectator-journey.gif`, `docs/media/spectator-meeting.png`, `docs/media/spectator-two-truths.png`,
  `docs/media/provenance.json`, `docs/media/README.md`; the `docs/media` row of `docs/artifacts.md`.
- This card's Results.

Never written: `engine/`, `agents/`, `meetings/`, `observation/`, `orchestrator/`, `llm/`, `api/`, `eval/`,
`training/`, `experiments/`, `replays/`, `tests/fixtures/`, `README.md`, `docs/reading-guide.md`, `docs/glossary.md`,
`docs/ownership-case-study.md`, `frontend/e2e/media.spec.ts` unless a selector the capture needs changed (state it),
`ReplayPicker.tsx`, `TournamentDashboard.tsx`, `BeliefPanel.tsx`, `BallotCard.tsx`, the audits and `tasks/README.md`.

## Record impact

**What moves:** the header's and the welcome step's copy, now in `SPECTATOR_COPY`; three media assets, their
provenance and their table rows.

**What stays unchanged:** every recording, MANIFEST, roster, experiment config and committed report; the corpus and
every ML artifact; the scorecard, census and profile pages and JSON; the public payload and every `data/` file of
the bundle; `VIEW_MODEL_VERSION`; the prompts, levers, defaults, ladder tip and era registry; every pre-registration
and audit verdict.

**Future behaviour:** none. **Evaluation:** none. **Publication:** as Constraints states.

## Validation

Run from the branch's worktree; quote each exit code as it came back.

```sh
uv run python scripts/check_doc_facts.py
uv run python scripts/validate_task_docs.py
uv run pytest tests/scripts/test_public_recording_provenance.py -q
(cd frontend && npm test && npm run tsc:check && npm run lint && npm run e2e)
git grep -n -i -E 'directed by|AI-reviewed|Source & ownership|supporting material' -- frontend docs/media README.md
git diff --exit-code <base> -- replays/ training/ api/ eval/ README.md docs/reading-guide.md docs/glossary.md
uv run python scripts/build_demo_bundle.py --out <dir-base>   # at base, then at head into <dir-head>, one checkout
diff -r <dir-base> <dir-head>                                 # file by file into the PR body
```

The mutation pass's rows, the bundle diff and the strings that go live are quoted in Results and the PR; CI's run at
the exact head, by run id, is the gate record.

## Results

Implemented on `work/viewer-header-source-link` from B = `3793d6b5`: `33cad8ab` (the header, the welcome step, the
`header` copy group and their tests), `2c7f9ef8` (two planted cases the mutation pass asked for), `d307de64` (the
media re-captured at `2c7f9ef8`), `18e3f619` (the attribution pattern bounded at a word start) and this Results
commit, H. References: `docs/architecture.md` "Packages" (`frontend/` consumes the generated view types; nothing
below the viewer moves, and no view type, DTO or recorded byte changes), AGENTS.md craft rule 4 (user-facing copy in
plain words, in `SPECTATOR_COPY`), craft rule 2 (each new check has a planted case seen red), and
`docs/deployment.md` with `.github/workflows/pages.yml` for publication. The card's Status line is the
orchestrator's, on `main`.

### Decisions

1. **The header** (orchestrator ruling 1). It renders the heading `AiLibi` and one line: the tagline, a middle dot
   as a visual separator, and one link, "GitHub", to `https://github.com/dkdan10/AiLibi` (new tab, as before). The
   separator is `aria-hidden`, so a screen reader hears the tagline and then the link. There is no attribution, no
   "AI-reviewed" and no "Source & ownership". The title block is a small exported component, `ShellTitle`
   (`frontend/src/App.tsx`), so a test can render it without the whole shell; the shell's `<header>` mounts
   `<ShellTitle />` beside the nav, still only while no meeting is open. The tagline sits in its own `<span>` so a
   literal typed in place of the copy is a text node the span case reads (mutant M03 below).
2. **The tour's welcome step** (ruling 2). This is the orchestrator's extension of the owner's ruling to the second
   place the same words appeared, and the owner can reverse it by a word. The attribution sentence ("Daniel Keinan
   directs the project; ... with separate AI review.") is deleted, and the link keeps a sentence of its own, "Read the
   source on GitHub.", with the period inside the link as the old link had it. The rest of the step is unchanged.
   The first paragraph now reads: "AiLibi asks whether AI agents can reason from what they actually saw. You are
   watching saved games, not making live model calls. Read the source on GitHub." It reads well with only the
   sentence removed, so the stop clause did not fire. `STEPS` is exported so the welcome step renders in a test.
3. **The copy** (ruling 3). `SPECTATOR_COPY.header` (exported as `HEADER_COPY`) holds `tagline`, `sourceLinkText`,
   `sourceUrl` and a fourth key, `tourSourceLinkText`. The fourth key exists because acceptance item 2 has the step
   read its link text from the copy, and this group is where the source link's words live. The header and the
   tour both read `sourceUrl`.
4. **The media** (ruling 4), with one deviation. All four spectator assets were re-shot in one run of the committed
   harness at `2c7f9ef8` (`cd frontend && AILIBI_CAPTURE_MEDIA=1 npx playwright test e2e/media.spec.ts`: 3 passed,
   1.1 min), committed in `d307de64` with `provenance.json` naming capture revision `2c7f9ef8` and each digest; the
   recording block is unchanged. Earlier captures followed the same order: the run happens at the head, then a later
   commit carries the assets and the provenance. **Deviation:** the WebM clip, `docs/media/spectator-journey.webm`,
   is not in Expected scope, but it was re-shot and committed too. The same capture test ("the clip and the GIF")
   writes it, its frames are full-viewport and show the header, the README links it, and provenance carries one
   capture revision for all four. Keeping the old clip would have left the attribution on screen in the README's
   linked clip, under a provenance revision it was not shot at. `frontend/e2e/media.spec.ts` is unchanged: no
   selector moved.
5. **Nothing else** (ruling 5). `README.md`, `docs/reading-guide.md`, `docs/glossary.md`,
   `docs/ownership-case-study.md`, the picker, the dashboard, the belief panel and the badges are untouched. The
   README keeps its own attribution line, since the repository tells the story the header no longer does. The
   header and the tour linked the repository root, never the case study. The case study is still linked from the
   same places as at B (`git grep -c ownership-case-study -- README.md docs frontend`: README.md 3,
   docs/reading-guide.md 1, at B and at H).
6. **The pattern's boundary.** The ballot label "Vote redirected by the meeting rule" (`BallotCard.tsx:26`, not this
   card's file) contains the letters "directed by", and the built index chunk carries it. Both tests therefore bound
   the phrase at a word start (`\bdirected by`). A planted case shows the label passes the leaf walk; with the
   unbounded pattern it went red (1 failed).
7. The merge is the orchestrator's (the owner asked for this change on 2026-10-10); this worker did not merge.

### Acceptance evidence

- **Item 1 (header).** Mechanisms: `frontend/src/App.test.tsx` "the shell header" renders `<ShellTitle />` with
  `renderToStaticMarkup`. It checks that the heading is `AiLibi`, that there is exactly one link whose text and
  `href` equal `HEADER_COPY.sourceLinkText` and `sourceUrl`, that the whole text equals
  "AiLibiRecorded AI social deduction · GitHub", and that no attribution word appears. `frontend/src/lib/copy.test.ts`
  "the header's and the tour's source link" walks every `SPECTATOR_COPY` leaf with `stringLeaves` for the five words
  (none; 0 paths). Its span case takes `ShellTitle`'s body and the shell `<header>` inside `App`, checks that they
  read `HEADER_COPY.tagline`, `sourceLinkText` and `sourceUrl` and mount `<ShellTitle />`, and runs `proseLiterals`
  over both (empty) and the word pattern (no hit). Planted: the old strip typed in as a literal is named by
  `proseLiterals`, and "Source & ownership" typed in as the link trips the word pattern. Each of the five words
  restored as a copy value fails the leaf walk, naming `SPECTATOR_COPY.header.tagline`. A word planted in
  `dashboard.intro` is named there, and a word inside a list is named by its index. A render planted with the
  attribution, a second link or the old link text is named by `titleProblems`. Red first: the new cases, run before
  `copy.ts`, `App.tsx` and `GuidedTour.tsx` changed, gave `Test Files 2 failed (2)`, `Tests 10 failed | 382 passed`
  (the copy group and the spans were missing), and `App.test.tsx` failed to load (`ShellTitle` was undefined).
  After the change they pass. The plants were also made as real edits (edit, run both unit files, restore; a
  scratch script). P1 put the old strip back into `ShellTitle` as literals: 4 failed, the span case among them.
  P2 put the old strip back as the `tagline` value in `copy.ts`: 5 failed, and the leaf walk reports
  `expected [ 'SPECTATOR_COPY.header.tagline' ] to deeply equal []`. Restored, both unit files pass 406.
- **Item 2 (tour).** Mechanism: `App.test.tsx` "the guided tour's welcome step" renders `STEPS[0].body`. It checks
  for exactly one link whose text and `href` equal `HEADER_COPY.tourSourceLinkText` and `sourceUrl`, no attribution
  word in the step's text, and the first paragraph's exact sentence quoted above. `copy.test.ts` checks that the
  welcome step's span has exactly one `<a `, that its link reads both copy keys, that `proseLiterals` over the link
  is empty, and that the step carries no attribution word. Planted: the old sentence spliced back in is named ("the
  step says Claude Code"); the old link text is named (links and "the step says ownership"); each of the five words
  planted in the step is named by itself; the old link text typed in as a literal is named by `proseLiterals`; the
  old sentence typed back into the source trips the word pattern. The real edit P3 restored the old sentence in
  `GuidedTour.tsx`: 3 failed (the render case, the span case, and a planted case, because the restored sentence adds
  its own word hit); restored, they pass.
- **Item 3 (media).** Old against new digests: `spectator-two-truths.png` `b9989243...` (107,510 B) to `3e5e1c31...`
  (107,401 B); `spectator-meeting.png` `afa121fa...` (263,404 B), **unchanged byte for byte** (the header is hidden
  while a meeting is open); `spectator-journey.gif` `754e61b3...` (626,072 B) to `5d8fd110...` (599,731 B);
  `spectator-journey.webm` `83cbc683...` (620,047 B) to `1a85a8b8...` (653,820 B). The two-truths sheet differs in
  72 of 1,850,724 pixels, all in its fog half (bounding box x 1001-2006, y 78-410; a Pillow difference, count-only).
  A probe run at the same head reproduced both stills and the GIF byte for byte, so the capture is deterministic at
  H; its outputs were discarded, and the committed bytes are the first run's (the WebM differs run to run, as its
  README says). GIF first frame, count-only (Pillow, frame 0, the left third of the frame): ink bands below grey 230
  in rows 0 to 38, which hold the title block, number 3 in the old GIF (the name, the tagline line, the attribution
  line) and 2 in the new (the name, the tagline line). The tagline row's ink ends at column 100 where it ended at
  144, so "directed by Daniel Keinan" is gone from it. The frame was never committed. ffprobe: the GIF reads
  640x400, 13 frames, 8.5 s (17 frames are shot; identical tail frames merge); the WebM reads 1440x900, 9.00 s. The
  `docs/media/README.md` rows (2036x909; 1440x900; 640x400, 13 frames; 1440x900, 9 s; directory 1.6 MB) and the
  `docs/artifacts.md` row (1.6 MB / 7 files) re-derive **unchanged**: 1,643,105 bytes, 7 tracked files, so neither
  file is edited. `uv run pytest tests/scripts/test_public_recording_provenance.py -q`: 31 passed. Planted: the GIF's
  digest edited by one character (`5d8fd110` to `6d8fd110`) fails `test_media_hashes_and_labels_are_current`
  (`assert not ['spectator-journey.gif']`, 1 failed); restored, it passes.
- **Item 4 (nothing else).** `git diff --stat 3793d6b5 H`: `docs/media/provenance.json`, the GIF, the WebM (the
  deviation above), the two-truths PNG, `frontend/src/App.test.tsx`, `App.tsx`, `GuidedTour.tsx`, `copy.test.ts`,
  `copy.ts` and this card. `git diff --exit-code 3793d6b5 -- replays/ training/ api/ README.md
  docs/reading-guide.md docs/glossary.md`: exit 0, and the evaluation package is absent from the stat. No `data/`
  file of the bundle differs (below). `check_doc_facts.py`: exit 0. Perturbed: the README caption's "at tick 9" made
  "at tick 10" in a scratch copy, read through the caption test's own helpers (`_scratch_front_door`,
  `_readme_scene_problems`), returns 3 problems ("names tick 10, the picture shows tick 9" first); the unchanged
  README returns none.
- **Item 5 (live strings and bundle).** Both are in the pull request body. Bundle at B and at H, built in this one
  checkout (`uv run python scripts/build_demo_bundle.py --out <dir>`, B before any edit, H at `d307de64`; the later
  commits change only tests and this card): 110 files each, 102 identical. `index.html` changed only in the index
  chunk's name. Seven compiled chunks were renamed: `index-*.js` (the header and tour strings), and `MapView`,
  `ReplayPicker`, `TournamentDashboard`, `CanvasRenderer`, `WebGLRenderer` and `WebGPURenderer`, which differ only
  in chunk names and one-letter minified import bindings from the index chunk. No `data/` file, no stylesheet, no
  font and the bundle README are byte-identical. In H's index chunk, `Claude Code`, `Codex`, `AI-reviewed`,
  `ownership` and `supporting material` count 0 each and `\bdirected by` counts 0; its one `directed by` substring is
  the ballot label "Vote redirected by the meeting rule". `Recorded AI social deduction` counts 1 and `Read the
  source on GitHub` counts 1.
- **Item 6 (mutation pass and gate).** Below. The gate record is CI's green run at the exact head of the pull
  request, cited there by run id; memo 8.7 item 1 bars a further card-only commit to record it here, and no local
  `check.sh` ran at the final head.

### Mutation pass

One pass, 39 mutants, exactly the listed classes, over the header render (`ShellTitle` and the shell `<header>`),
the copy leaf walk (`stringLeaves`, `attributionLeaves`, the word pattern, the spans) and the tour step. Each mutant
was one exact replacement, run against `src/App.test.tsx` and `src/lib/copy.test.ts` and then restored (a scratch
script). While the pass was designed it found two survivors: M35, the branch swap that a tree without lists cannot
see, and the five-word pattern in `App.test.tsx`, which only some words reached. Each got a planted case
(`2c7f9ef8`). After the boundary was added (`18e3f619`) the pass ran once over all 38 unit-judged mutants at that
head, and every one was killed. M13 was judged by the browser leg.

- Dropped filter or wrapper (5): M01 `<ShellTitle />` dropped from the header; M02 the header link's `<a>` dropped;
  M03 the tagline's `<span>` dropped; M04 the tour link's `<a>` dropped; M05 the leaf walk's filter dropped. All
  killed (1, 3, 1, 9 and 8 failed).
- Swapped collection (3): M06 the leaf walk walks `HEADER_COPY` instead of the tree; M07 the walk takes object keys
  for values; M08 the span's key list becomes all of `HEADER_COPY`'s keys. Killed (6, 10, 1).
- Comparison made a None test or inverted (5): M09 `value !== null` to `=== null` in `stringLeaves`; M10 and M11
  the header and step word checks inverted; M12 the heading's `undefined` test inverted. Killed (10, 2, 7, 2). M13,
  the shell's `meetingOpen` read inverted (`selectedMeetingId === null`), passes the unit files and is killed by
  `npm run e2e` (2 failed: `journey.spec.ts:1004` and `bundle.spec.ts:342`); the clean e2e at `2c7f9ef8` passed 15,
  with 3 skipped.
- Kind or key read made a constant (4): M14 the header link text to `"Source"`; M15 the header `href` to another
  URL; M16 the tour link text to `"GitHub"`; M18 the leaf walk's path to a fixed key. Killed (4, 3, 9, 1).
- Message argument made a constant (4): M19 to M22, the four problem messages in `App.test.tsx`. Killed (1, 6, 1,
  1).
- Dropped tuple member (12): M23 to M27 each word dropped from `copy.test.ts`'s pattern; M28 to M32 each dropped
  from `App.test.tsx`'s; M33 the header span dropped from `headerSpans`' pair; M34 `tourSourceLinkText` dropped from
  the copy group. Killed (2, 1, 1, 2, 2; 2, 2, 1, 1, 3; 1; 8).
- Swapped adjacent branches (2): M35 `stringLeaves`' list and object branches; M36 the header's text and word
  checks. Killed (1, 1).
- Loaded source read as its literal (4): M17 the header `href` as the literal URL; M37 the tagline as its literal;
  M38 the tour link text as its literal; M39 the tour `href` as its literal. Killed (1, 2, 2, 1).

### Validation

Run from the branch's worktree with `.venv/bin/python` for the card's `uv run python`, count-only. No local
`check.sh` ran at the final head (memo 8.7 item 1).

- `check_doc_facts.py`: exit 0. `validate_task_docs.py`: exit 0, "390 historical phase tasks and 390 prompts; 107
  work cards".
- `pytest tests/scripts/test_public_recording_provenance.py -q`: 31 passed; `tests/scripts/test_check_doc_facts.py`:
  368 passed.
- `cd frontend`: `npm test` 847 passed (28 files); `npm run tsc:check` exit 0; `npm run lint` exit 0; `npm run e2e`
  15 passed, 3 skipped (the capture spec, inert without its switch), 1.6 min, at `2c7f9ef8`.
- `git grep -n -i -E 'directed by|AI-reviewed|Source & ownership|supporting material' -- frontend docs/media
  README.md`: at B, 4 lines (`README.md:3`, the README's own attribution, which stays; `App.tsx:1201`, the strip;
  `BallotCard.tsx:26` and `PrivateReasoning.test.tsx:296`, the "redirected by" ballot label). At H, `App.tsx` is
  gone. `README.md:3`, `BallotCard.tsx:26` and `PrivateReasoning.test.tsx:296` remain, and the planted fixtures and
  the pattern add 8 lines in `App.test.tsx` and 10 in `copy.test.ts`. Outside tests, `frontend/src` has 0 hits in
  `SPECTATOR_COPY`, `App.tsx` and `GuidedTour.tsx`.
- `git diff --exit-code 3793d6b5 -- replays/ training/ api/ README.md docs/reading-guide.md docs/glossary.md`:
  exit 0.
- The bundle diff, as in item 5.
- Also run: `build_sample_report.py --check` on `samples/4p1i`, `samples/9p2i`, `ml_corpus/4p1i` and
  `ml_corpus/9p2i`, exit 0 each; `UV_OFFLINE=1 bash scripts/verify_samples.sh`, exit 0, 4 sets of 50 verified clean.

### Limitations

- The WebM clip moved although the card named three assets (Decision 4); it is the one file beyond Expected scope.
- Tests reference the five attribution words and the old sentence as planted fixtures, so the card's grep over
  `frontend` prints test lines; outside tests the only hits are in files this card does not own: the ballot label
  "redirected by", and code comments that mention Claude Code, Codex or ownership in `glyphs.ts`,
  `BeliefMatrix.tsx`, `usePlayback.ts` and a story. None of them is rendered as attribution.
- The two-truths sheet's 72-pixel change in its fog half is attributed to the header's change (the map sits one
  text line higher on the page). The probe shows the capture is deterministic at H, but no capture at B was run to
  isolate the cause.
- The GIF check is a count of text bands and a row extent, not OCR (no OCR tool on this machine).
