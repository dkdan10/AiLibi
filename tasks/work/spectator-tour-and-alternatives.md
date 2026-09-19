# Open the spectator tour on a grounded game and show considered alternatives

**Status:** ready

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

- [ ] The criterion is written into the comment above `FEATURED_GAMES`
  (`ReplayPicker.tsx:90-93`): the strip is still hand-picked, and the ORDER now
  leads with a game whose first meeting ejects on a `role_proof` flag naming
  the ejected player. One offline command, counts only and no provider call,
  reproduces both bands, the eligible-opener counts (32 of 50 and 19 of 50) and
  the one 9p2i game with neither a flag nor an ejection (seed 2); its output is
  quoted in Results.
- [ ] `FEATURED_GAMES` is reordered to `9p2i` 23, 13, 46, 2 and `4p1i` 2, 11,
  29. The seven `(set, seed)` pairs are unchanged, so every featured game stays
  a committed recording and `scripts/check_doc_facts.py:4739` keeps resolving.
  Each entry keeps its two-line `set:` then `seed:` shape, one `{` per entry,
  and one double-quoted `label:` literal: `test_sets.py:64-65` and
  `build_demo_bundle.py:213-228` parse those shapes literally, and a
  reformatted entry desynchronises the label zip silently.
- [ ] The two lead captions name the evidence, not the outcome. `9p2i` 23:
  "Four meetings, twenty-six spoken turns. A player reports seeing someone use
  a vent, and the meeting files that apart from one account merely
  contradicting another. Read which each ballot cites, and who else its voter
  weighed." `4p1i` 2: "A small table, three spoken turns. A player reports
  seeing someone use a vent. Compare that against what each ballot cites."
  Both keep a countable claim in `_assert_featured_counts`'s vocabulary
  (`test_sets.py:563-575`), name no player and no ending, and carry none of the
  banned tokens at `:432-444` or `:598-604`. The other five are unchanged.
- [ ] The head pin becomes a criterion pin.
  `test_featured_seeds_exist_in_their_committed_sets` (`test_sets.py:493`)
  asserts the 9p2i head is `("9p2i", 23)` AND, through the set loader, that the
  head's first meeting is `EJECTED` with a `role_proof` flag naming the ejected
  player whose role is `IMPOSTOR`. Planted, each red before and green after:
  the head at seed 2 (no ejection), at 46 (ejects on no flag), at 13 (first
  meeting SKIPs).
- [ ] The journey keeps both evidence directions.
  `frontend/e2e/journey.spec.ts:549-594` stops hardcoding seed 2 as the head
  and opens the featured card whose pill reads exactly `seed 2` (an exact-text
  match, because `seed 2` is a prefix of `seed 23`), asserting the zero-flag
  branch there; the main leg at `:455-463` takes the `else` branch on the
  flagged head; both planted mismatches stay constructed against a real
  rendered meeting. Running the suite before and after the picker change is the
  evidence that the branch moved.
- [ ] `BallotCard` renders the alternatives behind `privateVisible`, between
  the citation row (`BallotCard.tsx:149-152`) and the redirect disclosure
  (`:154-156`): a `ul` named by its visible label, one `li` per entry, reusing
  `PlayerPill` (`:49-66`) for an entry matching a served player and a plain
  mono token for one that does not, so an unknown id or a literal `SKIP` (the
  shape `tests/api/test_schemas.py:297` already admits) cannot masquerade as a
  player. Recorded order is kept, the length is not assumed, and an empty list
  renders an explicit "no alternatives recorded" line in the idiom of
  `:164-166`. Both strings live in `SPECTATOR_COPY` beside the meeting group
  (`frontend/src/lib/copy.ts:415-418`) and carry no dialect, so `copy.test.ts`
  covers them through its value leg and its disk leg over `BallotCard.tsx`
  (`frontend/src/lib/copy.test.ts:55`). Colours come from `tokens.ts` only.
- [ ] Vitest covers the gate and the shapes in
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
- [ ] `docs/reading-guide.md:63` is rewritten IN PLACE to say the curated list
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
