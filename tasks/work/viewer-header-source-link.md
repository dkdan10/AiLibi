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

- [ ] **The header reads from the copy and carries no attribution.** `SPECTATOR_COPY.header` holds the tagline, the
  link text and the repository URL; `App.tsx` renders them and nothing else in the header's text. Mechanism: a
  render test of the header asserts the heading, the tagline and one link whose text and `href` equal the copy; a
  `copy.test.ts` case walks `SPECTATOR_COPY`'s string leaves (`stringLeaves`) for `directed by`, `Claude Code`,
  `Codex`, `AI-reviewed` and `ownership` (none), and a span case runs `proseLiterals` over the header JSX (empty).
  Planted: the old strip restored as a literal fails the span case; restored as a copy value fails the leaf walk,
  naming the key.
- [ ] **The tour's welcome step keeps one plain link.** The attribution sentence is removed; the step reads its link
  text and URL from the copy. Mechanism: the tour's existing test (or a new case beside it) renders the welcome step
  and asserts the link text equals the copy and that the step's text contains no attribution word. Planted: the old
  sentence restored fails it.
- [ ] **The media follow the header.** The journey GIF, the meeting still and the two-truths still are re-captured
  from the head's bytes by `frontend/e2e/media.spec.ts` in one run; `docs/media/provenance.json` names that capture
  revision and the new digests; the `docs/media/README.md` rows and the `docs/media` row of `docs/artifacts.md`
  are re-derived (bytes and file count). Mechanism: `test_media_hashes_and_labels_are_current` and
  `test_the_captions_scene_is_the_recorded_one` (`tests/scripts/test_public_recording_provenance.py:138`, `:411`)
  pass at H; a count-only read of the new GIF's first frame finds the header without the attribution line (state
  the method). Planted: one digest edited by one character in provenance fails the hash test. If a still's bytes
  did not change, Results says so.
- [ ] **Nothing else moves.** `git diff --stat B H` lists only Expected scope's files; `README.md`,
  `docs/reading-guide.md`, `docs/glossary.md`, the public payload and every `data/` file of the bundle are untouched;
  `scripts/check_doc_facts.py` exits 0. Mechanism: the diff and the gate. Perturbed: a README caption tick edited by
  one in a scratch copy fails the caption test, so the unchanged pass is not vacuous.
- [ ] **The live strings are stated, and the bundle diff.** The PR body lists every string that goes live, old against
  new, and the demo bundle diff built at B and at H in one checkout (`scripts/build_demo_bundle.py --out`; expected:
  compiled assets only, no `data/` file; the measured diff governs).
- [ ] **One bounded mutation pass, and the gate record.** One pass over the listed classes (a dropped filter or wrapper,
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

Filled by the implementation.
