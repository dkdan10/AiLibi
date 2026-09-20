# Open the spectator tour on a grounded game and show considered alternatives

**Status:** done

## Outcome

The spectator tour stops opening on the one committed game where the table
established nothing. The curated order becomes a stated, reproducible property
of the recordings, and the two lead captions say what evidence the ballots rest
on, never how the game ended. The ballot card then renders
`considered_alternatives`, the one weighing artefact already on disk: in the
API type, populated on 98.3% of shipped SKIPs, read by no component today.

Both halves are viewer-only. No recording, DTO, schema, prompt, report, audit
or fixture byte moves, so every committed recording keeps loading and verifying
unchanged. A merge to `main` republishes the static demo bundle
(`.github/workflows/pages.yml`, AGENTS.md:21-26), so this is a publication
decision and the card says so.

## Evidence

[The direction of 2026-09-19](../direction-2026-09-19-process-over-outcome.md)
is the basis; the owner accepted its decisions D1 to D8 as a set that date.
This card is D3, its section 9 cards 2 and 3, under the owner's governing
sentence: groundedness before accuracy, and a state the project can be shown
in. Section 9's closing note fixes the rule, that the opener is picked by a
measured criterion and that seed 41 is not it.

**The opener today shows nothing.** `FEATURED_GAMES`
(`frontend/src/components/ReplayPicker.tsx:94`) leads with `9p2i` seed 2, and
the tour opens the curated head for its target set (`GuidedTour.tsx:32`,
`:83-90`; strip at `ReplayPicker.tsx:140-141`, `:685`, markup `:264-286`). Seed
2 is the only game in `replays/samples/9p2i` with no flag and no ejection.

**The criterion, MEASURED over the committed samples.** An ejection is grounded
when the ejected player carries a `role_proof` flag in the same meeting: the
derived category for a `vent_sighting`, a spoken observation matched against
the speaker's own typed vent-witness record (`api/schemas.py:759-777`, rule
table `:844-852`, `:886`). The other categories are two accounts that cannot
both be true, which the direction's section 5 shows the alibi envelope
manufactures against honest movers, so no committed game today can open on a
sound self-contradiction instead.

| `samples/9p2i` band on the ejected player | ejections | role-correct |
| --- | --- | --- |
| `role_proof` flag | 68 | 68 |
| other flag | 7 | 1 |
| no flag | 20 | 13 |

Those rows reproduce the direction's section 3 figures (68/68, 13/20) to the
digit; the other-flag split is new here, and is why the criterion names
`role_proof` and not any flag. `samples/4p1i` runs 19/19 on the proof band and
1/5 without. 32 of the 50 9p2i games and 19 of the 50 4p1i games have a FIRST
meeting that ejects on a `role_proof` flag, and the first meeting is the one
the viewer's auto-follow opens.

**The head this selects is `9p2i` seed 23**, already featured, so the
committed-recording rule and the seed pins hold with an order change alone. Its
meeting 0 records 8 ballots and one strong `vent_sighting` naming the ejected
player; 6 ballots EJECT, 5 citing turn 0 and one citing the voter's own
observation `p-5:8:1`; both SKIPs carry a non-empty `considered_alternatives`,
so the opening meeting exercises both halves of this card.
`docs/reading-guide.md:66` already names that meeting as its source-bound
example, so the guide and the strip agree rather than drift.

**`considered_alternatives` is populated and unread.** MEASURED over the two
9p2i corpora: 1,336 of 1,359 SKIPs (98.3%), reproducing the direction's section
4 figure. Over all 3,385 9p2i ballots the list holds 0 entries 284 times, 1
entry 889 times and 2 entries 2,212 times; across all four committed sets every
entry matches `^p-\d+$` and the longest is 3 characters, so the render is two
tokens wide at most today and must still not assume it. The field is
`tuple[PlayerId, ...]` in the meeting layer (`meetings/schemas.py:772`),
`tuple[str, ...]` at the DTO (`api/schemas.py:967`), mapped through
(`api/replay_loader.py:3297`), typed in the client
(`frontend/src/types/api.ts:383`), read only by stories and tests.

**Which surface the ballot card is.** `BallotCard` treats the target as public
and everything else as private reasoning, gated on `privateVisible`
(`BallotCard.tsx:77`): confidence `:123`, rewrite chips `:82`, citations
`:149-152`, rationale `:16` and `:157-167`. `considered_alternatives` is the
same class (`design/phase-12/stage-0-understand.md:91` records it post-hoc
only, never shown to agents), and an impostor's alternatives can expose whether
it weighed its teammate, so it renders behind that gate. It adds no field to
any surface: the leak tripwire already permits the DTO field name
(`tests/api/test_leak.py:552`).

**What binds the list.** `tests/api/test_sets.py:505` pins the head as
`("9p2i", 2)`; `:493-516` pins the per-set seed sets; `:425-449` bans outcome
spoilers; `:563-575` checks each label's countable claim against the served
replay and `:578-604` runs it per pair with its own planted failure. The
parsers are literal (`:64-65`, `scripts/build_demo_bundle.py:192-228`), and
`scripts/check_doc_facts.py:4739-4781` checks set membership only, so keeping
all seven games leaves it untouched. In the e2e, `openFeaturedReplay`
(`frontend/e2e/journey.spec.ts:58-82`) reads the seed off the card and the
evidence leg branches on the card's own promise (`:53-56`, `:455-463`), so a
flagged head takes the `else` branch and the bundle journey
(`frontend/e2e/bundle.spec.ts:201-221`) needs no change; only the
planted-failure test at `frontend/e2e/journey.spec.ts:549-594`, which hardcodes
`expect(seed).toBe(2)` at `:557` and the zero-flag direction, must be
re-pointed. The viewer ships one theme (`frontend/src/index.css:103`, no
`darkMode` anywhere), so `frontend/CLAUDE.md` applies: tokens only, no hex.

## Acceptance

- [x] Review correction: the PER-SET opener claim is now enforced per set. The
  comment above `FEATURED_GAMES` says each set leads with a game whose first
  meeting ejects on a `role_proof` flag, and the pin applied the criterion to
  `featured[0]` alone — a verifier swapped the two 4p1i entries so the 4p1i row
  led with seed 29, which ejects a CREWMATE on no flag, and
  `tests/api/test_sets.py` stayed green. `_featured_heads()` now derives the
  first entry of EVERY set out of the committed picker data, and
  `test_featured_seeds_exist_in_their_committed_sets` runs
  `_assert_opens_on_role_proof` over each of them; 4p1i seeds 29 and 11 join
  `test_featured_head_criterion_rejects_a_head_that_establishes_nothing` as
  planted rejections. The same swap is red at this tip and the old one-head
  predicate is shown blind to it on the same tree; both runs are quoted in
  Results. The strip's order does not move: 4p1i seed 2 already satisfies the
  criterion, so what was missing was the mechanism, not the ordering.
- [x] Review correction: the `role_proof` CLAUSE of the head criterion now has a
  planted case that isolates it. 9p2i seed 10 joins the parametrize in
  `test_featured_head_criterion_rejects_a_head_that_establishes_nothing`
  (`tests/api/test_sets.py`) — its first meeting ejects p-6, p-6 IS an impostor,
  and a flag in that meeting DOES name p-6, so only the category comparison can
  reject it — and `test_seed_10_isolates_the_role_proof_clause` reads each of
  those facts out of the served bytes. Every case also carries a
  `pytest.raises(match=...)`. Weakening the clause to `ejected in flag.subjects`
  turns both red; the before/after runs are quoted in Results.
- [x] Review correction: the alternatives copy no longer claims the entries are
  OTHER players, because the bytes falsify it — 27 of 869 `samples/9p2i` ballots
  list the voter itself and 22 list the applied target
  (`scripts/measure_featured_criterion.py --alternatives`). The heading is
  neutral, and an entry the card's header already shows is ANNOTATED rather than
  dropped, so the block stays the record. Proved by
  `names an entry the header already shows rather than passing it off as another
  player` and `names a recorded SKIP as the vote cast when the ballot skipped`
  in `frontend/src/components/PrivateReasoning.test.tsx` (per-`li`, so a note on
  the wrong entry fails), and by
  `test_alternatives_shape_reads_the_committed_duplicates` in
  `tests/scripts/test_measure_featured_criterion.py`, which names the committed
  games carrying each shape.
- [x] Review correction: the Results record-impact paragraph counted four
  changed files under `frontend/src/` where its own quoted command prints five.
  The dated subsection restates the count from the command's output.
- [x] The criterion is written into the comment above `FEATURED_GAMES`
  (`ReplayPicker.tsx:90-93`): the strip is still hand-picked, and the ORDER now
  leads with a game whose first meeting ejects on a `role_proof` flag naming
  the ejected player. One offline command, counts only and no provider call,
  reproduces both bands, the eligible-opener counts (32 of 50 and 19 of 50) and
  the one 9p2i game with neither a flag nor an ejection (seed 2); its output is
  quoted in Results.
- [x] `FEATURED_GAMES` is reordered to `9p2i` 23, 13, 46, 2 and `4p1i` 2, 11,
  29. The seven `(set, seed)` pairs are unchanged, so every featured game stays
  a committed recording and `scripts/check_doc_facts.py:4739` keeps resolving.
  Each entry keeps its two-line `set:` then `seed:` shape, one `{` per entry,
  and one double-quoted `label:` literal: `test_sets.py:64-65` and
  `build_demo_bundle.py:213-228` parse those shapes literally, and a
  reformatted entry desynchronises the label zip silently.
- [x] The two lead captions name the evidence, not the outcome. `9p2i` 23:
  "Four meetings, twenty-six spoken turns. A player reports seeing someone use
  a vent, and the meeting files that apart from one account merely
  contradicting another. Read which each ballot cites, and who else its voter
  weighed." `4p1i` 2: "A small table, three spoken turns. A player reports
  seeing someone use a vent. Compare that against what each ballot cites."
  Both keep a countable claim in `_assert_featured_counts`'s vocabulary
  (`test_sets.py:563-575`), name no player and no ending, and carry none of the
  banned tokens at `:432-444` or `:598-604`. The other five are unchanged.
- [x] The head pin becomes a criterion pin.
  `test_featured_seeds_exist_in_their_committed_sets` (`test_sets.py:493`)
  asserts the 9p2i head is `("9p2i", 23)` AND, through the set loader, that the
  head's first meeting is `EJECTED` with a `role_proof` flag naming the ejected
  player whose role is `IMPOSTOR`. Planted, each red before and green after:
  the head at seed 2 (no ejection), at 46 (ejects on no flag), at 13 (first
  meeting SKIPs).
- [x] The journey keeps both evidence directions.
  `frontend/e2e/journey.spec.ts:549-594` stops hardcoding seed 2 as the head
  and opens the featured card whose pill reads exactly `seed 2` (an exact-text
  match, because `seed 2` is a prefix of `seed 23`), asserting the zero-flag
  branch there; the main leg at `:455-463` takes the `else` branch on the
  flagged head; both planted mismatches stay constructed against a real
  rendered meeting. Running the suite before and after the picker change is the
  evidence that the branch moved.
- [x] `BallotCard` renders the alternatives behind `privateVisible`, between
  the citation row (`BallotCard.tsx:149-152`) and the redirect disclosure
  (`:154-156`): a `ul` named by its visible label, one `li` per entry, reusing
  `PlayerPill` (`:49-66`) for an entry matching a served player and a plain
  mono token for one that does not, so an unknown id or a literal `SKIP` (the
  shape `tests/api/test_schemas.py:297` already admits) cannot masquerade as a
  player. Recorded order is kept, the length is not assumed, and an empty list
  renders an explicit "no alternatives recorded" line in the idiom of
  `:164-166`. Every string lives in `SPECTATOR_COPY` beside the meeting group
  (`frontend/src/lib/copy.ts:415-418`) and carry no dialect, so `copy.test.ts`
  covers them through its value leg and its disk leg over `BallotCard.tsx`
  (`frontend/src/lib/copy.test.ts:55`). Colours come from `tokens.ts` only.
- [x] Vitest covers the gate and the shapes in
  `frontend/src/components/PrivateReasoning.test.tsx`, beside the existing
  ballot cases. Planted, red before and green after: an alternative id is
  absent through another agent's lens (extending the secret list at `:86`),
  present under the voter's own lens and under omniscient (`:89-95`), an
  unknown entry renders as a plain token rather than a pill, and an empty list
  renders the empty line rather than nothing. The story helper at
  `frontend/src/stories/MeetingView.stories.tsx:78-98` hardcodes
  `considered_alternatives: []` (`:93`), so it gains an optional parameter
  defaulting to the empty list, and the meeting story gains one ballot with two
  alternatives beside one with none.
- [x] `docs/reading-guide.md:63` is rewritten IN PLACE to say the curated list
  is hand-picked and that its order leads with the evidence the tour opens on.
  The page has 47 words of headroom under its 1,350-word ceiling
  (`check_doc_facts.py:889-894`; `wc -w docs/reading-guide.md` reads 1,303 at
  HEAD), so the edit swaps words rather than adding a paragraph, and the count
  is rerun after. `tasks/README.md:43`'s inventory sentence is recomputed at
  merge, rebasing onto whichever sibling of this wave lands first.

## Constraints

Viewer only. No change to `engine/`, `agents/`, `meetings/`, `orchestrator/`,
`llm/`, `experiments/`, `training/` or `eval/`, and none to any DTO field,
schema or loader mapping. No prompt family is touched, so the version-bump
cascade (the `.j2` marker, `orchestrator/game.py` `DEFAULT_PROMPT_VERSIONS`,
the live-recorded prompt-version pin) does not apply; the
`agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:268-269` clauses belong
to [the grounded SKIP card](grounded-skip-and-guard-labels.md) and
[the weighing channel](ballot-weighing-channel.md), and this card does not
anticipate them. No recording, report, `audits/` or `tests/fixtures/` byte
changes, so no `docs/artifacts.md` row is recomputed (`:101`, `:109`).

No new private field reaches any surface, and the leak allowlist is not
widened; the demo bundle already bakes every ballot field (accepted limitation
G5-5 in `audits/review-2026-09-06/REVIEW_APPENDIX_FOLLOWUP.md`) and this card
does not widen that either. No live provider call of any kind, no recording, no
re-record, no re-scored report, no held-out generation, and band 2100-2999
stays unseen.

One writer per file within wave 1: this card owns `ReplayPicker.tsx`,
`BallotCard.tsx`, `frontend/src/lib/copy.ts`, `frontend/e2e/journey.spec.ts`
and `tests/api/test_sets.py`. `BallotCard.tsx` then passes to the substrate
wave, which stacks on this component rather than beside it: the grounded-SKIP
card adds the grounding-label chip next to the alternatives block this card
creates, and the weighing card adds the counter-evidence link beside the two
citation links. `docs/reading-guide.md` is shared with
[the process scorecard](process-scorecard.md), which owns that page's numbers
section; this card owns only the sentence at `:63` and rebases onto it if that
card lands first. A merge republishes the public demo bundle, so the pull
request states the copy that goes live; task completion authorizes no
deployment beyond that standing publication (AGENTS.md:21-26).

## Expected scope

`frontend/src/components/ReplayPicker.tsx` (the order, the two lead labels, the
criterion comment), `frontend/src/components/BallotCard.tsx`,
`frontend/src/lib/copy.ts`, `frontend/src/components/PrivateReasoning.test.tsx`,
`frontend/src/stories/MeetingView.stories.tsx`, `frontend/e2e/journey.spec.ts`,
`tests/api/test_sets.py`, `docs/reading-guide.md` (one sentence),
`tasks/README.md`'s inventory sentence, the offline criterion command, and this
card. Delivered on `work/spectator-tour-and-alternatives` and one pull request
into `main`, a merge commit or fast-forward and never a squash, with the
trailer `Card: tasks/work/spectator-tour-and-alternatives.md`.

Order, identical on all seven cards. WAVE 1 is parallel and changes no agent
behaviour: [the process scorecard](process-scorecard.md), this card and
[the evaluation close](close-deduction-candidate-evaluation.md); the close
merges FIRST so the substrate wave's `GENERATOR_SOURCES` edits owe no restamp
to a retired band. The SUBSTRATE WAVE is serial, all three moving the
`qwen3_6_27b` prompt stamps and the ballot or claim schema:
[alibi as a route](alibi-as-route.md), then
[grounded SKIP and guard labels](grounded-skip-and-guard-labels.md), then
[the weighing channel](ballot-weighing-channel.md). Then
[the re-record](process-rerecord.md), once. Deferred and in no card: the body
freshness band, an impostor who reports a body, the `docs/` front door.

## Record impact

No recorded bytes move. No replay, sample, report, weight, fixture or audit
file is edited, so `bash scripts/verify_samples.sh` and the four
`build_sample_report.py --sample-dir <set> --check` runs recompute exactly what
they recompute at HEAD, and no backward-compatible loader is needed because no
format changes. Nothing added here is read back from a recording: the
alternatives render is a pure function of a DTO field the loader already
populates from the as-recorded ballot.

The shipped default that DOES change is the published viewer: what the demo
opens on, what the captions claim, and what a ballot shows to a privileged
lens. Under the owner's rulings a change to shipped default behaviour is now
intended rather than deferred behind a lever, a departure from the previous
default-OFF rule, stated here rather than discovered. The substrate wave
exercises that departure in full; here it is confined to the spectator surface,
so no agent reads anything different and no game plays out differently. It is
also a publication, because `pages.yml` rebuilds the bundle on every push to
`main`, and the bundle consequence is bounded: the same seven games baked in a
different order, so only the landing game moves. When
[the re-record](process-rerecord.md) replaces the recordings, the criterion
command is rerun and the head re-chosen, which is why the pin at
`tests/api/test_sets.py:493` asserts the criterion and not a seed alone.

## Validation

`cd frontend && npm run lint && npm run tsc:check && npm run test && npm run
build`, then `cd frontend && npm run e2e` locally, because Playwright sits
outside `scripts/check.sh:66` and only CI runs it. `uv run pytest tests/api -q`
with the fake provider, `uv run python scripts/validate_task_docs.py`,
`uv run python scripts/check_doc_facts.py`, and
`uv run python scripts/verify_ml_evidence.py` (offline; never `--complete`).
`bash scripts/verify_samples.sh` and the four
`uv run python scripts/build_sample_report.py --sample-dir <set> --check` runs
over the two `replays/samples/` and two `replays/ml_corpus/` sets, to show the
recordings still load and verify. `wc -w docs/reading-guide.md` against the
1,350-word ceiling. The offline criterion command, quoted in Results. Then
`bash scripts/check.sh` to the end rather than to the first gate, because
`set -e` masks later gates. Do not run a live evaluation, a calibration, the
held-out generator, or any provider call as a check.

## Results

Delivered on `work/spectator-tour-and-alternatives`. Both halves are
viewer-only: no file under `engine/`, `agents/`, `meetings/`, `orchestrator/`,
`llm/`, `experiments/`, `training/` or `eval/` is touched, no DTO field, schema
or loader mapping moves, no prompt family is touched (so the version-bump
cascade does not apply), and no recording, report, `audits/` or
`tests/fixtures/` byte changes — which is why no `docs/artifacts.md` inventory
row is recomputed. No live provider call, no recording, no re-record, no
held-out generation; band 2100-2999 stays unseen.

### The criterion, and the command that reproduces it

The criterion is now a committed instrument rather than a sentence:
`scripts/measure_featured_criterion.py` reads the committed recordings through
the same `SetLoaderRegistry` the spectator API serves them with and prints
counts only. It names the same `role_proof` category
`api.schemas.classify_evidence` derives (the rule table at `api/schemas.py`
:844-852), for the reason the card's Evidence section gives: the other
categories are two accounts that cannot both be true, and the direction memo's
section 5 shows the alibi envelope manufactures those against honest movers.

```
$ uv run python scripts/measure_featured_criterion.py
replays/samples/4p1i — 50 games
  ejections, by the band of the ejected player in that meeting
    role_proof flag   19 ejections  19 role-correct
    other flag         0 ejections   0 role-correct
    no flag            5 ejections   1 role-correct
  first meeting ejects on a role_proof flag: 19 of 50 games
  no flag and no ejection anywhere: seeds [0, 3, 5, 7, 8, 9, 10, 12, 15, 17, 21, 22, 23, 24, 25, 28, 30, 31, 34, 35, 36, 37, 38, 43, 44, 45]
replays/samples/9p2i — 50 games
  ejections, by the band of the ejected player in that meeting
    role_proof flag   68 ejections  68 role-correct
    other flag         7 ejections   1 role-correct
    no flag           20 ejections  13 role-correct
  first meeting ejects on a role_proof flag: 32 of 50 games
  no flag and no ejection anywhere: seeds [2]
```

Every figure the card asserts reproduces to the digit: the three 9p2i bands
(68/68, 7/1, 20/13), the 4p1i proof band (19/19) and its flagless band (1 of
5), both eligible-opener counts (32 of 50 and 19 of 50), and seed 2 as the one
9p2i game that records neither a flag nor an ejection anywhere.

### Decisions

1. **The order is measured; the membership stays editorial.** The comment above
   `FEATURED_GAMES` now says both in as many words and cites the command. The
   seven `(set, seed)` pairs are unchanged, so every featured game is still a
   committed recording, `scripts/check_doc_facts.py:4739` keeps resolving, and
   each entry keeps its two-line `set:` then `seed:` shape with one `{` and one
   double-quoted `label:` — the shapes `tests/api/test_sets.py:64-65` and
   `scripts/build_demo_bundle.py:213-228` parse literally.
2. **The pin asserts the criterion, not a seed.**
   `_assert_opens_on_role_proof` in `tests/api/test_sets.py` loads the head
   through the set loader and requires its FIRST meeting to be `EJECTED`, the
   ejected player to carry a `role_proof` flag naming them in that same
   meeting, and that player's role to be `IMPOSTOR`. It deliberately
   re-implements the predicate rather than importing the script's, in the same
   idiom the evidence taxonomy uses for its API-side and eval-side twins
   (`api/schemas.py` :840-852 against `eval/deduction_metrics.classify_flag`):
   two independent readings of the same bytes are the evidence, and an import
   would make them one. `Record impact` calls for exactly this, so the
   re-record re-chooses the head instead of silently keeping it.
3. **The alternatives block is private-class and stacked, not inline.** It sits
   between the citation row and the redirect disclosure, behind the same
   `privateVisible` gate as the confidence bar, the citations and the rationale
   — `design/phase-12/stage-0-understand.md:91` records `considered_alternatives`
   as post-hoc and never shown to agents, and an impostor's list can expose
   whether it weighed its teammate. It is a labelled block with a `ul` rather
   than a chip row precisely so the substrate wave can stack on it: the
   grounded-SKIP card's meeting-written grounding label goes beside the heading,
   and the weighing card's counter-evidence link beside the two citation links
   above. A `data-ballot-alternatives` hook marks the block so a test can make a
   claim about it that the header's own target pill cannot satisfy.
4. **A served player wears the identity pill; nothing else may.**
   `AlternativeEntry` reuses `PlayerPill` only when the entry matches a served
   `agent_id`, and renders a dashed mono token otherwise, so an id no longer in
   the game or the literal `SKIP` the ballot schema also admits
   (`tests/api/test_schemas.py:297`) cannot read as somebody at the table.
   Recorded order is preserved and the length is not assumed: the list wraps.
5. **An empty list is a record, not an absence.** It renders
   "no alternatives recorded" in the idiom of the existing "no rationale
   recorded" line, so a viewer reads "this voter weighed nobody else" rather
   than "not shown here". Every string lives in `SPECTATOR_COPY.ballot` beside
   the meeting group, so `copy.test.ts` covers them through its value leg, and
   `BallotCard.tsx` stays clean for its disk leg. (Round 1 of review added two
   more strings to that group, the notes below; the same two legs cover them.)
6. **The journey keeps both evidence directions.** `openFeaturedReplay` now
   takes an optional seed matched on the pill's EXACT text — exact because
   `seed 2` is a prefix of `seed 23` — and the planted-failure test opens seed 2
   by name instead of assuming it is the head. The main leg now takes the `else`
   branch on the flagged head; the planted case still walks the `if` branch and
   constructs both mismatches against a real rendered meeting. The bundle
   journey reads the seed off the card and needed no change.

### Corrections to the card, recorded rather than silently absorbed

* The card's third planted head, seed 46, is described as "ejects on no flag".
  Measured, 9p2i seed 46's FIRST meeting SKIPS, so it fails the criterion for
  the same reason seed 13 does. It is kept as a planted case for the reason it
  actually fails, and seeds 44 and 12 were added for the one the card was
  reaching for: 44's first meeting ejects an impostor on NO flag, 12's ejects a
  crewmate on a flag that is not role proof. A pin checking only "the head
  ejects", or even "the head ejects correctly", would wave seed 44 through.
  (Round 1 of review showed that neither ISOLATES the `role_proof` clause —
  seed 44 fails the subjects clause and seed 12 the role clause under a weakened
  category comparison. Seed 10 is the isolating case and was added; see the
  dated subsection below.)
* The card cites `docs/reading-guide.md:66` as already naming seed 23's meeting
  0. It does, and the sentence rewritten in place is the one at `:62-63`
  (`:63` in the card's numbering) about the curated list, as the acceptance item
  specifies. No other sentence on that page moved.

### Verification

Run at the tip of this branch with the fake provider and no network.

| command | result |
| --- | --- |
| `uv run python scripts/measure_featured_criterion.py` | exit 0, output quoted above |
| `bash scripts/verify_samples.sh` | exit 0 — 50 + 50 samples verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check` x4 | exit 0 for `replays/samples/{9p2i,4p1i}` and `replays/ml_corpus/{9p2i,4p1i}`: each report consistent with its replays |
| `uv run python scripts/check_doc_facts.py` | exit 0 — doc facts, front door, `docs/ml-program.md` and the 4 word budgets all verified |
| `uv run python scripts/verify_ml_evidence.py` | exit 0 — 60 checks, 48 OK, 0 FAIL, 7 expected EVIDENCE-BRANCH-ABSENT, 5 INFO. Never run with `--complete`. |
| `wc -w docs/reading-guide.md` | 1,329 against the 1,350 ceiling (1,303 at HEAD; the swap spends 26 of the 47 words of headroom) |

The rest is recorded in the dated subsection below, which carries the full-gate
and end-to-end counts.

### Limitations

* The criterion ranks games by the one evidence channel that demonstrably
  works. It is not a claim that the other bands are worthless — the flagless
  band is 13 of 20 role-correct on 9p2i, above chance — only that a tour should
  not OPEN on a table that established nothing.
* The strip's membership is still hand-picked and unmeasured. Only the head of
  each set carries the criterion — both heads, since the round-1 repair below;
  the remaining five entries are editorial, and the pin says so.
* The alternatives render shows WHO a voter weighed, not WHY or how much. The
  recorded field carries no weight, no order semantics and no reason, and this
  card adds none: the weighing channel proper is
  [the weighing card](ballot-weighing-channel.md).
* The demo bundle already bakes every ballot field (accepted limitation G5-5 in
  `audits/review-2026-09-06/REVIEW_APPENDIX_FOLLOWUP.md`); rendering the field
  neither widens that nor narrows it.
* A merge to `main` republishes the public bundle
  (`.github/workflows/pages.yml`, AGENTS.md:21-26). The consequence is bounded —
  the same seven games baked in a different order, two rewritten captions, and
  a block visible only to a privileged lens — but it is a publication, and the
  pull request states the copy that goes live. Task completion authorizes no
  deployment beyond that standing publication.

### 2026-09-19 — planted failures and the full gate

**Planted failure 1: the ballot render.** The committed vitest cases are only
worth something if the component can fail them, so the alternatives block was
deleted from `BallotCard.tsx`, the suite run, and the block restored:

```
$ cd frontend && npx vitest run src/components/PrivateReasoning.test.tsx   # block removed
 × shows reasoning from the voter's lens or omniscient mode: false
 × shows reasoning from the voter's lens or omniscient mode: true
 × renders every considered alternative in its recorded order, omniscient=false
 × renders every considered alternative in its recorded order, omniscient=true
 × does not dress SKIP as a player at the table
 × does not dress p-404 as a player at the table
 × says so explicitly when the voter recorded no alternative
      Tests  7 failed | 18 passed (25)
$ cd frontend && npx vitest run src/components/PrivateReasoning.test.tsx   # restored
      Tests  25 passed (25)
```

**Planted failure 2: the head criterion, committed.**
`test_featured_head_criterion_rejects_a_head_that_establishes_nothing` applies
`_assert_opens_on_role_proof` to five real committed 9p2i games and requires
each to raise: seed 2 (no ejection anywhere), 13 and 46 (the first meeting
skips), 44 (the first meeting ejects an IMPOSTOR, but on no flag) and 12 (the
first meeting ejects on a flag that is not role proof). It runs on every gate.

**Planted failure 3: the head criterion, live.** The committed test proves the
predicate bites; this proves the PIN does. The picker's `FEATURED_GAMES` order
was re-pointed at each of the card's three named seeds — with the seed literal
moved alongside it, so the criterion clause rather than the equality above it is
what fails — the test run, and both files restored:

```
$ uv run pytest tests/api/test_sets.py::test_featured_seeds_exist_in_their_committed_sets -q
# head planted at 9p2i seed 2
E       AssertionError: ('9p2i', 2, 'SKIPPED')
E       assert 'SKIPPED' == 'EJECTED'
# head planted at 9p2i seed 46
E       AssertionError: ('9p2i', 46, 'SKIPPED')
E       assert 'SKIPPED' == 'EJECTED'
# head planted at 9p2i seed 13
E       AssertionError: ('9p2i', 13, 'SKIPPED')
E       assert 'SKIPPED' == 'EJECTED'
$ uv run pytest tests/api/test_sets.py -q   # both files restored
45 passed
```

Each of the three is red before and green after. Seed 46 fails as a
first-meeting SKIP rather than as the card's "ejects on no flag"; seeds 44 and
12 in planted failure 2 cover that case, as the correction above records.

**The end-to-end suite.** `cd frontend && npm run e2e` — exit 0, 13 passed and
3 skipped of 16 (the three skips are the `media.spec.ts` README captures, which
need `AILIBI_CAPTURE_MEDIA=1` and write into the repository). Both evidence
directions ran: the main leg's requests now load `headless-seed-23` and take the
"has evidence" branch, while the evidence-guard case opens `seed 2` by exact
pill text and walks the "no evidence" branch. The bundle and evidence specs
passed unchanged.

**The full gate.** `bash scripts/check.sh` — exit 0, captured directly rather
than through a pipe. 514 files formatted clean, import-linter clean, task docs
validated (390 historical phase tasks and 390 prompts, 73 work cards), prompts
in sync, `mypy` clean over 485 source files, **7,992 Python tests passed** with
20 skipped and 3 xfailed in 214.93s, then the four frontend legs: lint, three
typecheck projects, **522 frontend tests passed** across 19 files, and the
production build. The first run of the gate failed on one `ruff format` hunk in
`tests/api/test_sets.py` and nothing else; the reformat is its own commit and
the rerun above is the green one.

**Record impact, confirmed rather than asserted.** No recorded bytes moved:
`git diff --stat origin/main...HEAD` touches only `docs/reading-guide.md`, five
files under `frontend/src/`, two under `frontend/e2e/`,
`scripts/measure_featured_criterion.py`, `tasks/README.md`,
`tests/api/test_sets.py` and this card. No `audits/` or `tests/fixtures/` byte
changed, so no `docs/artifacts.md` inventory row is recomputed; the frozen
held-out manifest is untouched and band 2100-2999 stays unseen.

### Review corrections, round 1 (2026-09-19)

Three blocking findings from the independent verifiers at `bc01c8f1`, each
repaired rather than argued with. Commands in this subsection are pinned to the
tip of this branch, not to `bc01c8f1`.

**1. The `role_proof` clause had no planted case that isolated it.** The
correctness lens weakened `_assert_opens_on_role_proof` from
`flag.category == "role_proof" and ejected in flag.subjects` to
`ejected in flag.subjects` and the suite stayed green: of the five committed
planted seeds, 2/13/46 trip the EJECTED clause, 44 the subjects clause and 12
the role clause, so nothing proved the one comparison that separates this
criterion from "any flag". The verifier's diagnosis reproduced here exactly, and
the Results claim that "only the role-proof clause bites" was wrong as written.

9p2i seed 10 is the isolating case and is now a sixth parametrized rejection.
Read off the served replay, its first meeting EJECTS, the ejected player is
`p-6`, `p-6` is an IMPOSTOR, and both flags in that meeting name `p-6` — only
their category is `weak_signal`. So every other clause is satisfied and the
category comparison is the only thing left that can reject it.
`test_seed_10_isolates_the_role_proof_clause` asserts those five facts against
the bytes, so the isolation is read rather than claimed. Every parametrized case
also gained a `pytest.raises(match=...)` naming the message it must fail
through, so a case that starts failing for a different reason stops counting as
proof of its clause.

```
$ uv run pytest tests/api/test_sets.py -q              # clause weakened as above
FAILED ...rejects_a_head_that_establishes_nothing[12-...-weak_signal]
FAILED ...rejects_a_head_that_establishes_nothing[10-...-weak_signal]
2 failed, 45 passed
#   seed 10: Failed: DID NOT RAISE <class 'AssertionError'>
#   seed 12: Regex pattern did not match  (it raised ('9p2i', 12, 'p-5', 'CREWMATE'))
$ uv run pytest tests/api/test_sets.py -q              # clause restored
47 passed
```

Seed 12's red is the second half of the proof: with the category comparison
weakened it reaches the ROLE clause, which is exactly why it could not serve as
the category clause's own planted case. Seeds 44 and 12 are kept for the clauses
they do prove, and the Decisions text above is corrected rather than deleted.

**2. The "Also weighed" copy was falsified by the bytes it renders.** The
docs lens reproduced Codex C2: over the seven featured games 4 of 80 ballots
list the VOTER itself and 3 list the applied TARGET, and over `samples/9p2i` 27
of 869 and 22 of 869 — each rendering a second pill identical to one in the
card's header, under a heading that called the list "the other players".
Measured here with the same instrument, now carrying the counts:

```
$ uv run python scripts/measure_featured_criterion.py --alternatives
replays/samples/4p1i — 50 games
  ...
  considered_alternatives, over every ballot in those games
     117 ballots   179 recorded entries
    ballots listing the voter itself:        0
    ballots listing the applied target:      1
replays/samples/9p2i — 50 games
  ...
  considered_alternatives, over every ballot in those games
     869 ballots  1376 recorded entries
    ballots listing the voter itself:       27
    ballots listing the applied target:     22
$ uv run python scripts/measure_featured_criterion.py --alternatives \
    --games 9p2i:23 9p2i:13 9p2i:46 9p2i:2 4p1i:2 4p1i:11 4p1i:29
#   9p2i, 4 of 50 (selected):  71 ballots, 123 entries, 4 self, 3 target
#   4p1i, 3 of 50 (selected):   9 ballots,  12 entries, 0 self, 0 target
```

Both of the fix's options were on the table; the entry is ANNOTATED, not
filtered, because the block is the record and a render that drops a recorded
entry disagrees with the bytes it claims to show. So: the heading becomes
`Weighed on this ballot`, which asserts nothing about who the entries are, and
`alternativeNote` adds `(this voter)` or `(the vote cast)` to an entry the
header already shows — plain text inside the same `li`, so a screen reader reads
it with the entry it qualifies. The voter wins a tie. Two vitest cases prove it
per-`li` (so a note on the wrong entry fails, not just a missing one), and one
of them is the SKIP shape, where the note lands on a dashed token rather than a
pill. `test_alternatives_shape_reads_the_committed_duplicates` names the
committed games that carry each shape, so the render change stays tied to real
bytes: 9p2i seed 2 (7 ballots, 2 listing the voter) and seed 13 (18 ballots, 1
self and 2 target) against seed 23, the landing game, which carries neither.

```
$ cd frontend && npx vitest run src/components/PrivateReasoning.test.tsx
# alternativeNote stubbed to return null        → 2 failed | 25 passed (27)
# alternativeNote stubbed to note EVERY entry   → 2 failed | 25 passed (27)
# restored                                      → 27 passed (27)
```

The seed-23 caption's "who else its voter weighed" was checked against the same
measurement and left alone: that game records neither shape (0 of 26 ballots),
so the sentence is true of the game it describes.

**3. The record-impact paragraph miscounted its own diff.** It said four files
under `frontend/src/` where `git diff --name-only origin/main...HEAD | grep -c
'^frontend/src/'` printed five. Corrected in place above. At this tip the same
command prints 5 and the full diff is 13 files: `docs/reading-guide.md`, five
under `frontend/src/` (`BallotCard.tsx`, `PrivateReasoning.test.tsx`,
`ReplayPicker.tsx`, `lib/copy.ts`, `stories/MeetingView.stories.tsx`), two under
`frontend/e2e/`, `scripts/measure_featured_criterion.py`,
`tests/api/test_sets.py`, `tests/scripts/test_measure_featured_criterion.py`,
`tasks/README.md` and this card. Still no recorded byte: no `audits/` or
`tests/fixtures/` file is touched, so no `docs/artifacts.md` inventory row is
recomputed, no provider is called, and band 2100-2999 stays unseen.

**What the round added beyond the three repairs.** One new file,
`tests/scripts/test_measure_featured_criterion.py`, because the instrument grew
two flags: `--alternatives` (the counts above) and `--games SET:SEED` (the
featured strip's seven in one run). A malformed selector raises rather than
measuring fewer games than asked for, which is what the test's second case pins.
The default invocation prints exactly what it printed before, so the output
quoted earlier in these Results is unchanged.

**Gates, rerun at this tip.**

| command | result |
| --- | --- |
| `bash scripts/check.sh` | exit 0 (captured directly) — 515 files formatted clean, import-linter 4 contracts kept, task docs validated (390 historical phase tasks and 390 prompts, 73 work cards), prompts in sync, `mypy` clean over 486 source files, **7,998 Python tests passed** (20 skipped, 3 xfailed, 210s), then lint, three typecheck projects, **526 frontend tests** across 19 files, and the production build |
| `cd frontend && npm run e2e` | exit 0, 13 passed and 3 skipped of 16 (the skips are the `media.spec.ts` README captures, which need `AILIBI_CAPTURE_MEDIA=1`) |
| `uv run python scripts/measure_featured_criterion.py` | exit 0, output identical to the block quoted above |
| `bash scripts/verify_samples.sh` | exit 0 — 50 + 50 samples verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check` x4 | exit 0 over `replays/samples/{9p2i,4p1i}` and `replays/ml_corpus/{9p2i,4p1i}` |
| `uv run python scripts/check_doc_facts.py` | exit 0 |
| `uv run python scripts/validate_task_docs.py` | exit 0 |
| `uv run python scripts/verify_ml_evidence.py` | exit 0 (offline; never `--complete`) |
| `wc -w docs/reading-guide.md` | 1,329 against the 1,350 ceiling, unchanged this round |

The Python suite grew by six: the sixth parametrized rejection, the seed-10
isolation test, and the four cases of the new script test. The frontend suite
grew by four: the two annotation cases, plus two more that the copy gate's value
leg generates for the two new `SPECTATOR_COPY.ballot` strings.

One honest note on how these were run. A first pass launched `check.sh` and the
Playwright suite CONCURRENTLY, and two Python tests and two e2e cases failed on
that pass — `test_wall_deadline_cancels_meeting_and_retains_success` (a wall
clock deadline), `test_generated_logs_agree_event_for_event` (a Hypothesis
`FailedHealthCheck: Input generation is slow`), and two 90s Playwright timeouts.
All four are load-sensitive rather than diff-sensitive, and none touches a file
this card changes. The runs recorded above are the serial ones: `check.sh` alone
to exit 0, then `npm run e2e` alone to exit 0.

### Review corrections, round 1 continued (2026-09-20)

A fourth blocking finding, from the correctness lens, against the same round-1
verification: the three repaired above landed at `986f9ff1` and are unchanged
here. Commands in this subsection are pinned to the tip of this branch.

**4. The per-set opener claim was enforced for the 9p2i head only.** The comment
above `FEATURED_GAMES` says every set leads with a game whose FIRST meeting
ejects on a `role_proof` flag, and names `tests/api/test_sets.py` as the
mechanism; the Limitation above says the head OF EACH SET carries the criterion.
The pin ran `_assert_opens_on_role_proof(registry, *featured[0])` — the strip's
global head alone. The verifier swapped the complete 4p1i seed-2 and seed-29
entries, so the 4p1i row led with a game whose one meeting ejects a CREWMATE on
no flag, and the suite stayed green. The claim and its named mechanism disagreed,
which is the defect; the committed ORDER was never wrong.

The claim is the one worth keeping, so the mechanism was widened rather than the
sentence narrowed. `_featured_heads()` reads the first entry of EVERY set out of
the committed picker data — derived, not typed, so a set added to the strip is
covered the day it lands — and the pin asserts the criterion over each, after
checking that the derived heads cover every set the strip names (a helper that
regressed to returning one head fails there rather than passing silently).
4p1i seeds 29 and 11 join the parametrized rejections, each with its own
`match=`, and the rejection cases now carry their set name.

Measured, the 4p1i head already satisfies the criterion, so nothing in the
shipped strip moves:

```
$ uv run python scripts/measure_featured_criterion.py --games 4p1i:2 9p2i:23
replays/samples/4p1i — 1 games of 50 (selected)
  ejections, by the band of the ejected player in that meeting
    role_proof flag    1 ejections   1 role-correct
    other flag         0 ejections   0 role-correct
    no flag            0 ejections   0 role-correct
  first meeting ejects on a role_proof flag: 1 of 1 games
  no flag and no ejection anywhere: seeds []
replays/samples/9p2i — 1 games of 50 (selected)
  ...
  first meeting ejects on a role_proof flag: 1 of 1 games
```

**The verifier's route-around, now red.** The same swap of the two complete 4p1i
entries, applied to `ReplayPicker.tsx` at this tip, the suite run, the file
restored byte-for-byte from a copy taken before the plant:

```
$ uv run pytest tests/api/test_sets.py -q      # 4p1i entries 2 and 29 swapped
E       AssertionError: ('4p1i', 29, [])
FAILED tests/api/test_sets.py::test_featured_seeds_exist_in_their_committed_sets
1 failed, 48 passed
$ uv run pytest tests/api/test_sets.py -q      # picker restored
49 passed
```

On that same planted tree the OLD one-head predicate is blind, which is the
other half of the proof rather than a re-statement of the verifier's report:
loading the test module and calling `_assert_opens_on_role_proof(registry,
*_parse_featured_games()[0])` while the swap was in place returned cleanly,
because the strip's first entry is still 9p2i seed 23. `_featured_heads()`
returned `[('9p2i', 23), ('4p1i', 29)]` on the same tree — the 4p1i head the old
pin never read.

**The two 4p1i cases pin the flag clause, not just the outcome.** Dropping the
`role_proof`-flag assertion out of `_assert_opens_on_role_proof` entirely:

```
$ uv run pytest tests/api/test_sets.py::test_featured_head_criterion_rejects_a_head_that_establishes_nothing -q
5 failed, 3 passed          # flag clause dropped
#   4p1i seed 11: Failed: DID NOT RAISE <class 'AssertionError'>
#   4p1i seed 29: Regex pattern did not match (it reached the ROLE clause)
#   9p2i 44, 12, 10 red too; only the three SKIPPED cases stay green
```

Seed 11 goes green-should-be-red on the dropped clause and seed 29 falls through
to the role clause, so the pair covers the flag clause on both roles. The tree
was restored from a copy taken before the weakening and the suite is 49 passed
again.

**What 4p1i cannot prove, recorded rather than left as a gap.** No 4p1i game can
isolate the CATEGORY comparison the way 9p2i seed 10 does: over all 50 games the
other-flag band is 0 ejections (the band table quoted at the top of these
Results), so `replays/samples/4p1i` contains no ejection on a flag that is not
role proof, in a first meeting or anywhere else. That clause's planted case stays
9p2i seed 10 and the rejection test's comment says so.

**Gates, rerun at this tip.**

| command | result |
| --- | --- |
| `bash scripts/check.sh` | exit 0 (captured directly) — see the counts below |
| `uv run pytest tests/api/test_sets.py -q` | 49 passed (47 at `986f9ff1`: the two 4p1i rejections) |
| `uv run python scripts/measure_featured_criterion.py` | exit 0, output identical to the block quoted above |
| `uv run python scripts/validate_task_docs.py` | exit 0 |
| `uv run python scripts/check_doc_facts.py` | exit 0 |
| `uv run python scripts/verify_ml_evidence.py` | exit 0 (offline; never `--complete`) |
| `bash scripts/verify_samples.sh` | exit 0 — 50 + 50 samples verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check` x4 | exit 0 over `replays/samples/{9p2i,4p1i}` and `replays/ml_corpus/{9p2i,4p1i}` |
| `cd frontend && npm run e2e` | exit 0, 13 passed and 3 skipped of 16 (the skips are the `media.spec.ts` README captures) |

**Record impact, restated at this tip.** Two files move this round:
`tests/api/test_sets.py` and a five-line comment above `FEATURED_GAMES` in
`frontend/src/components/ReplayPicker.tsx`. No `FEATURED_GAMES` entry, label,
component render or copy string changes, so the published bundle is
byte-identical to `986f9ff1`'s. `git diff --name-only origin/main...HEAD` still
prints the same 13 paths listed in the previous subsection: no `audits/` or
`tests/fixtures/` byte moves, no `docs/artifacts.md` inventory row is recomputed,
no provider is called, and band 2100-2999 stays unseen.
