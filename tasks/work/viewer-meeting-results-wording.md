# The meeting, the panels and the Results tab read in plain words

**Status:** ready

## Outcome

On 2026-10-11 the owner answered the visitor-wording survey by number; this card carries, verbatim, "3. A", "10. B",
"11. B", "12. B", "13. B", "14. B", "15. B" (`tasks/decision-2026-10-11-visitor-wording.md:19`, `:26-31`; table `:117`;
reading `:66` keeps 3 as is), and "8. B" (`:24`) at the belief panel's four view-name lines, which the binding order
gives it (`:99-106`). Survey options (`tasks/decisions-2026-10-11-visitor-wording/survey.md`, "survey" below): 3 (a),
"keep; the line becomes 'p-4 was an impostor'" (`:17`), that line only; 8, 10, 11, 15 (b), "Appendix A's pass" (`:31`,
`:37`, `:39`, `:49`; strings `:123`, `:131-151`); 12 (b), "Low / Med / High, number on hover" (`:41`); 13 (b), "a plain
row after the cases, headed by what it counts" (`:45`); 14 (b), "Inspect the meeting (shows roles)" and "Raw recording
file" (`:47`). When done, the meeting dialog, ballots, inspector, belief panel and Results tab read in plain words, free
of design notes, threshold arithmetic and undefined terms; numbers show Low / Med / High, the number on hover, and no
copy calls the suspicion a model's own number; the proof box is a plain row after the cases; every reworded string lives
in `SPECTATOR_COPY`, held by tests that fail if an old phrase returns.

**The orchestrator's rulings at card review** (decision §2b, each reversible by the owner's word). Ruling 1 (`:73-77`):
tour step 3's one word "Ground-Truth" follows the control it names to "Real roles", as necessary follow-through of item
11; "Error" and the rest of step 3 stay, held with the Error-layer words (D8.1); this card writes that word after the
header card and `viewer-browse-wording`. Ruling 5 (`:84-86`): "$0: a flat-rate service, so usage, not a bill" is true of
both shown sets; no provider-aware branch is added in this wave; the limit (a locally recorded set with another provider
would read the same) goes in Results. The binding file order (`:99-106`) is quoted in Constraints.

**The card's readings** of the adopted text, stated in Results, reversible by the owner's word: the counter link takes
the citation links' two forms; number-on-hover covers every surface printing those numbers (claim line, cell detail);
confidence takes the suspicion cut points, none added; the change since the last meeting reads as a bucket move ("rose
from Med to High"), points on hover; the proof row takes the body style, never the bold bordered box; a private ballot
reason is Voted, never Said; a non-zero cost keeps its value. Open wording: plain words, readability first, brevity over
completeness, every term defined or avoided. **Held for the owner, untouched** (decision `:125-127`, survey `:7`): the
"vote gate" badge, the Error layer and its words, the "correct / incorrect" ballot badge, every word of step 3 but
"Ground-Truth" and the browse card's "panel" (survey `:125`). No served byte, recording or payload moves.

## Evidence

Every `path:line` is at `f223b9fe` (`227c047f..f223b9fe` changes only the decision document); counts only; no prompt,
transcript text or seed-band prefix was read. Bare names are under `frontend/src/components/` or as first given.

**Meeting.** `MeetingView.tsx:127`, `:164-167`, `:195-217`, `:319-321`, `:346`, `:353-357`, `:396-400`, `:452-485`,
`:513-518`, `:613`; `TurnCard.tsx:47-51`, `:340`; `api/schemas.py:830` (a statement id names no speaker);
`frontend/src/lib/copy.ts:140-145`, `:372-397` (held `:374`, heading `:380`), `:440`; `EvidencePanel.tsx:63`, `:64`,
`:71`; `frontend/src/ui/ClaimLine.tsx:63`. **Ballots:** `BallotCard.tsx:22-36` (meaning `meetings/schemas.py:950-970`),
`:59-69`, `:213-225` (held), `:228-238`, `:262-264`, `:286-294`, `:321-323`, `:325` (item 8's); label pins
`frontend/e2e/bundle.spec.ts:268`, `frontend/e2e/journey.spec.ts:444`.

**Inspector and panel.** `MindInspector.tsx:39-43`, `:57-61`, `:66`, `:124`, `:128-132`, `:221`, `:251`; unsurveyed
empty state `:440-442`. `BeliefPanel.tsx:33-37`, `:247-248`, `:251-270`, `:452-455`, `:476-525` (heading `:478`, scale
`:489`), `:526-549` (held), `:690-692`, `:727-729`; item 8's view names `:253`, `:270`, `:512`, `:552`; suspicion is the
reconstructed belief state (`api/schemas.py:1257-1258`). `BeliefCell.tsx:105-113`, `:250`; held `:127-153`, `:239-248`.
Cut points `frontend/src/tokens.ts:69`, `:157-161`. Tour step 3: `GuidedTour.tsx:196`; survey `:125`.

**Results tab.** `PublicResults.tsx:65`, `:66`, `:68`, `:80` (one `<p>`: item 6's raw set id, survey `:116`, and the
reconstruction sentence), `:100-109` (the bold box above the cases), `:108`, `:113`, `:114-122`, `:121`;
`PublicResults.test.tsx:10` (cost 0); `copy.ts:122-125` (set-name helper), `:501`, `:509-518`, `:535-538`. Through
`build_public_results` (`scripts/build_demo_bundle.py:414`): 9p2i, 50 games, 2 cases, 24 ejections with a vent sighting,
37 without; 4p1i, 50, 0, 19 and 1 ("The 1 ejections"); both $0 from the flat-rate row (`llm/README.md:83`; `fake`,
`ollama` also $0, `:80`, `:82`); one provenance group each, no policy stamp, settings recorded with timed observations
off, no clock version. Defaults: `orchestrator/replay.py:698-699`, `:711-713`, `:957-961`; `api/schemas.py:1480`;
`docs/experiment-arms.md:112-113`. Titles are served (`api/public_results.py:66-84`), links not (`api/schemas.py:77`).

**Pins, helpers, captures, glossary.** `PrivateReasoning.test.tsx:59-111`, `:201-234`, `:286-297`;
`MeetingView.test.tsx:185-187`, `:309`; `copy.test.ts:444-447`; `frontend/e2e/evidence-journey.ts:15`, `:96`, `:99`, `:106`,
`:110`, `:130`, `:145`, `:180-222`; `journey.spec.ts:483`, `:949`, `:953-956`, `:965`; `PublicResults.test.tsx:65-66`, `:101-139`,
`:180-209`, `:277`; `tests/api/test_public_results.py:72`. Helpers `copy.test.ts:51-67`, `:130`, `:350`, `:432`, `:524`;
`copy.ts:54`; `frontend/src/lib/adoptedRules.ts:7-10`. Captures `docs/media/README.md:14`;
`frontend/e2e/media.spec.ts:836-858`, `:884-925`, `:1160-1163`. Glossary `docs/glossary.md:158`, `:174-191`, no "vote
rule" or "weak signal" in `:158-392`; front-door page `scripts/check_doc_facts.py:272-278`, figure scan `:37-39`.

## Acceptance

Each item names its enforcing mechanism and a planted or perturbed case that turns it red; new tests are seen red first.

- [ ] **A1. The role line (item 3).** Omniscient only, after an ejection, the Resolution card reads "p-4 was an
  impostor" or "p-4 was a crewmate", no "post-hoc"; the all-roles start and the gate are unchanged. Mechanism:
  `MeetingView.test.tsx` renders both roles, omniscient and under a lens. Planted: the gate made `true` fails.
- [ ] **A2. The readout is a plain sentence with no number (item 10).** A passed vote reads "Most votes went to p-4 and
  a voter was sure enough, so p-4 was ejected" (survey `:131`); a failed vote and a tie or skip lead say, in that shape,
  why no one was ejected; under every perspective, omniscient included, it has no digit outside a player id (`p-\d+`), and no "plurality", "threshold",
  "EJECTED", "SKIPPED" or comparison sign. Mechanism: the number pins (`PrivateReasoning.test.tsx:75`, `:83`;
  `evidence-journey.ts:181`, `:217`) and phrase negatives (`:69`, `:76`, `:84`; e2e `:207`, `:219`, `:221`) become one
  check per perspective that the readout, with each `p-\d+` id removed, has no digit (no weakening); the value negatives ("0.73", "0.42", "0.53") stay; outcome pins
  (`:94`; e2e `:208`) follow to "was ejected" / "no one was ejected"; a case per branch; `thresholdHits` on the
  templates. Planted: "0.73" left in the sentence fails while "p-4" passes; the old template fails each perspective; swapped branches fail.
- [ ] **A3. The design notes go (item 10).** `MeetingView.tsx:346` is deleted; the caption reads "Arrows point from
  accuser to accused", every verb "accuses" (survey `:133`); the record heading reads "Where everyone really was"
  (`:136`); `MeetingView.test.tsx:185-187`, `:309` and the region name at `journey.spec.ts:949` follow, `:953-956`, `:965` kept.
  Mechanism: renders of an opening and a reply; the e2e lens case. Planted: "redirects" or the old name back fails.
- [ ] **A4. Evidence captions say what each group holds (item 10).** Captions drop "grounded", "detector", "stamped" and
  "endpoint tick"; a kept heading's term (`journey.spec.ts:483`) that is not plain English gets one glossary entry under
  "How a meeting works", with no figure; the proof term joins "hard evidence" (`glossary.md:174`) or points at it.
  Mechanism: a `copy.test.ts` case reads the glossary for each listed term. Planted: an entry deleted fails, naming it.
- [ ] **A5. Turn kinds read "first statement", "reply", "spoke up" (item 10, `:135`).** One `SPECTATOR_COPY.turn` map
  serves the tag (its tick in words), the evidence endpoints and links, and `EvidencePanel.tsx:71`. Mechanism: a copy
  case keys the three kinds; renders of an opt-in tag and a source line. Planted: a leftover hand-typed map fails.
- [ ] **A6. The eleven adjustment chips (item 10).** They move to `BALLOT_COPY` in plain words; the redirect chip says
  the vote was "changed by the vote rule" (`:137`), `BallotCard.tsx:322` follows, and "vote rule" gets a glossary entry
  true to `meetings/schemas.py:950-970`. Mechanism: a copy case holds a value per reason `rewriteLabel` names and the
  fallback; a render per reason. Planted: one reason dropped renders the fallback and fails.
- [ ] **A7. Citations name what they point at; the basis shows (item 10).** Ballot links read "Statement by p-3 (turn
  3)" and "What p-1 saw at tick 12" (`:138`): the speaker from the public turn with that id, the rest from the id; the
  counter link (`counterKind`) and the panel's id line likewise; an unmatched or unreadable id says so plainly; "A
  citation shows where a claim came from, not that it is right." shows only if resolved (`:140`); the chip leads "Basis
  on the record:" (`:139`). Mechanism: renders of each shape, the chip, an unmatched, malformed and unresolved id;
  `evidence-journey.ts:211`, `:222` follow. Planted: the resolved test made `true` fails.
- [ ] **A8. The trail reads Said / Claimed / Voted / Result (item 11, `:141`).** Spoken text is Said, claims Claimed,
  the ballot (its written reason and vote) Voted, the outcome Result, "Meeting: p-4 was ejected" or the plain
  no-ejection form. Mechanism: `MindInspector.test.tsx` renders the belief tab over a turn, a claim and a ballot,
  asserting the labels in order. Planted: the ballot reason labelled Said fails.
- [ ] **A9. The panel and step 3 read by meaning (item 11, §2b ruling 1).** Heading "Who suspects whom", a plain
  rows-and-columns line; "Real roles" in the truth toggle, group label, fog chip, disabled title (`:142`), legend
  heading (`:478`; "READING: ERROR" held) and fog note (`:552`, "error" kept); legend rows say what each mark means
  ("Dagger: a real impostor, all-roles view only", `:143`), no "hue", "mono", "file" or "role-neutral"; step 3's
  "Ground-Truth" reads "Real roles", its one `GuidedTour.tsx` edit. Mechanism: new `BeliefPanel.test.tsx` layer and fog
  cases; A17's walk. Planted: "Ground-truth" in toggle, heading or fog note fails; "Ground-Truth" back in step 3 fails.
- [ ] **A10. The panel's view names take item 8's words (item 8, §2b order).** At `BeliefPanel.tsx:253`, `:270`, `:512`
  and `:552`, "fog" and "As-agent" leave text, tooltips and accessible names for the words `viewer-browse-wording` gives
  item 8 ("perspective" throughout, survey `:123`); the Error word stays. Mechanism: `BeliefPanel.test.tsx` under a
  lens; A17's walk of `BeliefPanel.tsx`. Planted: "fog" back in the chip fails.
- [ ] **A11. Low / Med / High, the number on hover (item 12).** Ballot confidence, belief cells, the inspector's three
  readouts, the claim line and the cell detail show the word, the number in a `title` and the accessible name; the
  "confidence" label stays; the detail's change reads as the bucket move; one bucketing (`suspicionBucketOf`), one word
  map, no new cut point, the paint unchanged; no hover shows a number its lens hides today. Mechanism: a render per
  surface, lens cases kept. Planted: a constant bucket read fails 0.72 → Med, 0.73 → High; "+5" on a face fails.
- [ ] **A12. The proof row (item 13).** The proof box becomes a plain body-style row after the cases, not the bold box,
  headed "Ejected players who were impostors, with and without a vent sighting" (`:145`); its caption says plainly that
  only impostors can vent (that half measures no deduction), a sighting does not show it caused the vote, and the counts
  describe this set; no "by construction" or "ejectee"; one ejection reads singular. Mechanism: `PublicResults.test.tsx`
  holds order and copy (`:65-66` follow); `evidence-journey.ts:96` follows. Planted: the row above the cases fails; "1 ejections" fails.
- [ ] **A13. The case links (item 14).** The links read "Inspect the meeting (shows roles)" and "Raw recording file";
  hrefs, the reveal button and the served titles stay. Mechanism: `PublicResults.test.tsx` holds labels and hrefs;
  `evidence-journey.ts:106`, `:110`, `:145` follow. Planted: "Pinned recording source" restored fails.
- [ ] **A14. The Results prose (item 15).** The intro says each recording was replayed and checked before counting
  (`:147`), its set name through the helper `viewer-browse-wording` exports; the empty state reads "No worked examples
  for this set yet; the 9-player set has two." (`:148`); each adopted rule is its own plain sentence, true to its field.
  Mechanism: `PublicResults.test.tsx` (`:116-139`, `:277`, `evidence-journey.ts:99`, `:130` follow);
  `tests/api/test_public_results.py` holds the count word to the curated cases (`:72`). Planted: a third case fails.
- [ ] **A15. Defaults are named (item 15).** "the built-in scripted policy" for an absent impostor or crew stamp
  (`:150`); the standard timing where recorded settings show timed observations off; "unknown" only where the record
  cannot say; stamps stay; prompt versions and the fingerprint under "Technical identifiers, for reproduction". A zero
  cost reads "$0: a flat-rate service, so usage, not a bill" (`:151`), no provider-aware branch (§2b ruling 5); a
  non-zero cost keeps its value with "usage, not a bill". Mechanism: `PublicResults.test.tsx` per branch (`:101-114`,
  `:180-209` follow). Planted: flags-off read as unknown fails; a cost of 1.5 shown as "$0" fails.
- [ ] **A16. Nothing held moves.** The badge, the Error layer's label, rows, look and accessible words, the ballot badge
  with its gate, and every word of tour step 3 but "Ground-Truth" keep their bytes (measured from `<base>`, after that
  "panel"). Mechanism: a copy case pins the
  badge, `BeliefPanel.test.tsx` the Error words; `git diff <base> <head>` over those lines and `GuidedTour.tsx` is
  quoted in the PR. Perturbed: either edited fails; a second step-3 word edited shows in the diff.
- [ ] **A17. Copy ownership and the walk.** Every reworded string sits in `SPECTATOR_COPY` (keys under `meeting`,
  `turn`, `ballot`, `publicResults` and the new `inspector`, `beliefPanel`, `evidenceSource`, `buckets`); strings not
  reworded may stay inline (survey `:175`). The walk reads every leaf and the comment-stripped source of each file
  written here for the retired phrases, plus `As-agent` and `fog` in `BeliefPanel.tsx`, and only "Ground-Truth" in
  `GuidedTour.tsx` (the rest of step 3 is held); `proseLiterals` runs over each reworded span; the dialect scan gains
  these files. Planted: a phrase restored as a literal fails naming the file, as a value naming the key.
- [ ] **A18. Nothing else moves; the live strings.** `git diff --stat <base> <head>` lists only Expected scope;
  `check_doc_facts.py` exits 0. The PR body lists every live string, old against new, the bundle diff file by file
  (expected: compiled assets only, no `data/` file; the measured diff governs) and, count-only, each committed capture
  showing a changed string. Perturbed: a scratch edit under `api/` shows in the `git diff --exit-code` guard (exit 1).
- [ ] **A19. One bounded mutation pass.** The listed classes (a dropped filter or wrapper, a swapped collection, a
  comparison made a None test, a kind or key read made a constant, a dropped tuple member, swapped branches, a loaded
  source read as its literal, message arguments) run once over the readout, bucket read, kind map, id labels, cost
  branch, proof row and defaults; survivors killed or reported. Gate record: CI's green run at the exact head (run id).

## Constraints

**Rules every change keeps.** User-facing copy lives in `SPECTATOR_COPY`, in plain words, with no task or audit id, no
unexplained term and no threshold arithmetic; a new glossary entry carries no task, audit, card or ruling id and no
figure. Role-correctness is reported, never a gate. Nothing in `engine/`, `agents/`, `meetings/`, `observation/`,
`orchestrator/`, `llm/`, `eval/`, `training/`, `experiments/`, `replays/` or `tests/fixtures/` moves; no recorded byte
is edited; no new `AILIBI_*` lever, prompt registry bump or provider call. A lens shows no more than today (the firewall
rules, `frontend/CLAUDE.md:53-60`). Every production line has a test that goes red when neutered; no test is weakened (a
pin that follows reworded text, its assertion kept, is not). Memo 8.7: CI at the exact head is the gate record;
message-argument survivors are nonblocking after the first fix round. Never print a rendered prompt, transcript text or
seed-band prefix. **Not in scope:** the held halves and every other word of tour step 3; the cases' served text; item
8's view names outside `BeliefPanel.tsx` and the neighbouring cards' other items; strings the survey does not list (the
inspector's empty state among them), unless they share a reworded string's map. The README and reading guide are not
written, so their ceilings (`_FRONT_DOOR_BUDGETS`, `scripts/check_doc_facts.py:1008`) and doc-facts pins stay put.

**One writer per file, across the wave.** The binding order (decision §2b, `:99-106`), word for word: "`GuidedTour.tsx`:
header card, then `viewer-browse-wording`, then `viewer-meeting-results-wording` (step 3's one word).
`PublicResults.tsx` and its test: `viewer-meeting-results-wording` alone (it calls the set-name helper the browse card
exports). `BeliefPanel.tsx` view names (item 8's words at its four lines): `viewer-meeting-results-wording`, which also
carries item 11 there. `PrivateReasoning.test.tsx`, `journey.spec.ts`, `MindInspector.test.tsx`,
`EvidencePanel.test.tsx`: the browse card, then the meeting card. `media.spec.ts`: the header card if it changed a
selector, then the browse card (the banner pin), then `front-door-plain-words` (the clip removal). `copy.ts` and
`copy.test.ts`: the header card, the browse card, the meeting card, in different groups. Items 2 and 19 are kept as is and are no card's work." The meeting card is
this one;
it never writes `media.spec.ts`. By the merge order (decision §3, `:120-123`), `viewer-header-source-link` merges first,
writing `copy.ts`, `copy.test.ts`, `GuidedTour.tsx`, `App.tsx`, the media, `provenance.json`, `docs/media/README.md` and
the `docs/artifacts.md` media row (its card `:99-100`, `:112-116`); then `viewer-browse-wording`; then this card,
merging `main` (never a rebase) before its final review, both hunks kept. The header card's captures (README image,
meeting still, GIF meeting frames) show this card's old words until `front-door-plain-words`, merging last, captures
again. In that order, the browse card then this card: `BallotCard.tsx`, `EvidencePanel.tsx`, `MindInspector.tsx` (item
8's strings there are the browse card's), `evidence-journey.ts`; `docs/glossary.md`: this card (entries only), then
`front-door-plain-words`. Other cards only: `docs/media/`, `App.tsx`, `ReplayPicker.tsx`, `bundle.spec.ts`, `README.md`.
The rest of Expected scope is this card's; `tasks/README.md` and the Status line are the orchestrator's, on `main`.

**Delivery and publication.** Branch `work/viewer-meeting-results-wording`, one pull request into `main`, merged after
`viewer-browse-wording` (merging `main` in and re-running its gate first), by merge or fast-forward, never squashed or
amended. Each commit body carries `Card: tasks/work/viewer-meeting-results-wording.md` immediately followed by the exact
line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. The merge publishes through
`.github/workflows/pages.yml`; the owner's answers of 2026-10-11 are the publication decision.

**Stop and ask** if a held string would have to move; open wording needs a term that can be neither defined nor avoided;
a bucket needs a new cut point; a served label would change (moving `VIEW_MODEL_VERSION`); a pin cannot follow the text
without weakening, above all a lens assertion; the curated cases no longer number two; the browse card merged without
the set-name helper or item 8's words; an unmerged card this map does not order writes a file here; or
`front-door-plain-words` merged first or will not capture the stills.

## Expected scope

- `frontend/src/components/MeetingView.tsx`, `TurnCard.tsx`, `EvidencePanel.tsx`, `BallotCard.tsx`, `MindInspector.tsx`,
  `BeliefPanel.tsx`, `BeliefCell.tsx`, `GuidedTour.tsx` (step 3's one word, `:196`), `PublicResults.tsx`;
  `frontend/src/ui/ClaimLine.tsx`; `frontend/src/lib/copy.ts`, `copy.test.ts`; `docs/glossary.md`.
- Tests: `MeetingView.test.tsx`, `PrivateReasoning.test.tsx`, `PublicResults.test.tsx`, `ClaimLine.test.tsx`;
  `MindInspector.test.tsx` and `EvidencePanel.test.tsx` (absent at `f223b9fe`; created by `viewer-browse-wording`,
  extended here, or created here if it did not); new `BeliefPanel.test.tsx`; `frontend/e2e/evidence-journey.ts`,
  `journey.spec.ts`; `tests/api/test_public_results.py`; story comments quoting a changed string; this card's Results.

Never written: `engine/`, `agents/`, `meetings/`, `observation/`, `orchestrator/`, `llm/`, `api/`, `eval/`, `training/`,
`experiments/`, `replays/`, `tests/fixtures/`, `scripts/`, `README.md`, every `docs/` file but the glossary,
`frontend/index.html`, `frontend/src/types/`, `frontend/src/store/`, `tokens.ts`, `App.tsx`, `ReplayPicker.tsx` and the
browse card's other files, `media.spec.ts`, `bundle.spec.ts`, the audits, the decisions and `tasks/README.md`.

## Record impact

**What moves:** the copy of the meeting dialog, ballots, inspector, belief panel and Results tab; tour step 3's one
word; bucket words for numbers; the Results tab's order; glossary entries. **What stays unchanged:** every recording,
MANIFEST, roster, config and report; the corpus, ML artifacts, scorecard, census and profile pages and JSON; the public
payload and the bundle's `data/` files; `VIEW_MODEL_VERSION`; prompts, levers, defaults, era registry and cut points;
the held halves and the rest of step 3; the media, README and reading guide. **Future behaviour, evaluation:** none; the
proof row reports, never gates. **Publication:** Constraints.

## Validation

Quote each exit code. `<base>` is `git merge-base <head> origin/main` once `main` is merged in at the final review;
A16's and A18's diffs, the live strings and the bundle (built at `<base>` and `<head>` in one checkout) use it.

```bash
uv run python scripts/validate_task_docs.py
uv run python scripts/check_doc_facts.py
uv run pytest tests/api/test_public_results.py tests/api/test_view_model.py -q
(cd frontend && npm test && npm run tsc:check && npm run lint && npm run e2e)
git grep -n -E -e 'post-hoc|plurality leader|top ballot|your ballot|guilt is never|distrust orange|suspicion matrix' \
  -e 'never a hue|Thought → Action|Cited (statement|observation)|by construction|ejectee|Pinned recording' \
  -e 'source-matched|What the recording shows|[Gg]round[- ][Tt]ruth|GROUND[- ]TRUTH' -- frontend/src/lib/copy.ts \
  frontend/e2e/{evidence-journey,journey.spec}.ts frontend/src/ui/ClaimLine.tsx frontend/src/components/{MeetingView,\
TurnCard,EvidencePanel,BallotCard,MindInspector,BeliefPanel,BeliefCell,PublicResults}.tsx
# expected: comments, planted cases and the inspector's empty state (MindInspector.tsx:441, not surveyed) only
git grep -n -e 'As-agent' -e 'fog' -- frontend/src/components/BeliefPanel.tsx   # expected: comments only
git grep -n -e 'Ground-Truth' -- frontend/src/components/GuidedTour.tsx          # expected: no line (exit 1)
git diff --exit-code <base> <head> -- api/ engine/ agents/ meetings/ observation/ orchestrator/ llm/ eval/ training/ \
  experiments/ replays/ tests/fixtures/ scripts/ docs/media/ frontend/src/types/ frontend/src/tokens.ts README.md
git diff --stat <base> <head>
uv run python scripts/build_demo_bundle.py --out <dir-base>   # at <base>, then at <head> into <dir-head>, one checkout
diff -r <dir-base> <dir-head>                                 # file by file into the PR body
```

## Results

Filled by the implementation.
