# Rank witnessed evidence above own routine under budget pressure

**Status:** done

## Outcome

Under the production prompt budget the evidence-v2 render stops shedding
witnessed evidence for the observer's own routine. A witnessed vent (band 85)
now outranks every derived evidence-context class, every sighting, all of the
observer's own routine and the reported testimony at 60; the only bands left
above it are the three first-hand ones this card does not move — a body
discovery (100), the observer's own kill (96) and a witnessed kill (95). A
sighting of another player (50) outranks the observer's own transitions and task
attempts (20), the non-contesting walking verdicts derived from it (45) and the
account-uncertainty caveats (15), so the observer's own movement log can no
longer shed it. A sighting does NOT outrank reported testimony, which stays at
60 and is not this card's to move: a large enough claim volume still evicts
sightings, and the limitation below carries the probe. The caveat block is
bounded per subject, and a render that withholds any caveat subject — by that
bound, by the token budget, or by shedding the class outright — always states
how many it withheld.
Lever-OFF and evidence-v1 rendered bytes stay identical.

## Evidence

Review claims are leads, not measurements of this tree. Reproduce each claim
from the archived follow-up review
([report](../../audits/review-2026-09-06/REVIEW_REPORT_FOLLOWUP.md), findings
NG3-1, VENT-2 and GR-1) on this checkout before implementing, and record the
reproduction with the change.

`agents/memory/store.py` sets `_SALIENCE_VENT_WITNESSED = 85` (`:66`) and
`_SALIENCE_SAW_PLAYER = 50` (`:77`), while the observer's own `own_transition`
(`:1601`) and `own_task_attempt` (`:1612`) rows render at salience 90, and every
evidence-context line enters at salience 90 (`:437-443`). The sort key at
`:459` is `(-salience, -tick, line)`, so own routine outranks witnessed evidence
before the token budget truncates. `agents/memory/evidence_context.py:383`
appends one unbounded, undeduplicated `Account uncertainty for <subject>` line
per ingested claim, and the claim volume is under the speaker's control.

`tests/fixtures/memory_rendering/tight_budget_drops_low_salience.json` and its
`.expected.md` already pin that a tight budget sheds lines; they do not pin
which class of line survives. Reviewers reproduced the eviction on real games
with the real agent factory at the default 1,500-token budget, so the fixture is
the pin, not the discovery.

## Acceptance

- [x] Review correction (closeout round 2): the Outcome rewritten in closeout
  round 1 said a witnessed vent "outranks everything the renderer emits except
  the observer's own kill (96)". Two further bands the v2 renderer emits sit
  above it — a body discovery at 100 and a witnessed kill at 95 — and at 200
  tokens both render while the vent is shed. The Outcome now names all three,
  and the two the card had not pinned anywhere are gated by
  `test_only_the_body_and_the_witnessed_kill_outrank_the_witnessed_vent`, which
  fails when either band is demoted below the vent.
- [x] Review correction (closeout round 2): the same sentence said neither the
  observer's own movement log "nor a speaker's claim volume" can shed a
  sighting, contradicting its own next sentence and the card's committed probe,
  where 42 claims evict the p-3 sighting at 1,500 tokens through reported
  testimony at 60. The claim-volume half is deleted; what stays is what the
  ranking enforces — a sighting outranks the observer's own routine (20), the
  non-contesting walking verdicts (45) and the caveats (15) — with the testimony
  ceiling kept as the limitation it already was. Reproduced by the probe quoted
  in "Review corrections, closeout round 1".
- [x] Review correction (closeout round 2): the Results opening paragraph named
  five of the branch's twelve commits, said the branch was "not re-reviewed"
  after two completed review rounds, and pointed a reader at "sections dated
  before 2026-09-08" — a discriminator selecting nothing, because every review
  subsection is dated 2026-09-08. The ledger now runs through this commit, the
  delivery state names both completed rounds and the commits they were run on,
  and the pointer names all three dated subsections. Checked against
  `git log --oneline 201849fc..HEAD`, and kept current across this round's own
  two commits.
- [x] Review correction (closeout round 1): acceptance item 3 held only on the
  unbudgeted `evidence_context_lines` surface — at the default 1,500-token
  budget the committed fixture withheld all seven of its subjects and the
  model-facing render said nothing. `_select_within_budget` now reserves the
  notice's cost from the FIRST row it selects and keeps it reserved until every
  subject is shown, so the sentence always fits and the item's own wording holds
  on `render_for_prompt`. Gated by
  `test_a_truncated_caveat_list_states_the_subjects_the_budget_dropped` (the
  sweep's former "a notice closing no list" branch now requires the notice) and
  by `test_the_production_budget_keeps_the_witnessed_evidence_beside_the_notice`,
  which pins both what the reserve guarantees and what it costs.
- [x] Review correction (closeout round 1): the reserve invariant was guarded by
  a production `assert`, which `python -O` strips. It is now an explicit raise of
  the named `UnreservedAccountNoticeError`, and the planted revert to the round-1
  conditional reserve raises it (`3 failed` of the 4 reds that revert produces,
  each with the token arithmetic in the message).
- [x] Review correction (closeout round 1): the Outcome claimed sightings of
  other players are kept under budget pressure without qualification, while the
  code ranks them at 50 against reported testimony at 60. The Outcome now states
  the ranks it enforces, the reported-testimony ceiling is a limitation with a
  reproduced probe, every stale `store.py` line reference in the round-1
  subsection is corrected to this head, and the round-0 planted-failure counts
  carry the head's values beside the commit they were measured on. *Amended
  2026-09-08, closeout round 2: the rewritten sentence was still wider than the
  code — it named one band above the vent where three sit — and it contradicted
  itself on sightings. Both are corrected by the first two items in this list;
  the stale-anchor and round-0-count halves of this item stand as written.*
- [x] Review correction: the demotion's stated justification was false. The
  `## Where you were:` route is capped at `SELF_LOCATION_TRAIL_MAX_SPANS` = 12
  spans and charged against the same budget, not "rendered in full and
  unbudgeted". All three statements now say what the code enforces, and the
  placement the demotion costs is pinned by
  `test_a_tick_off_the_trail_keeps_no_own_placement_under_the_budget` and
  recorded as a limitation instead of going unmentioned.
- [x] Review correction: the `N further subjects not shown` count was computed
  before the budget ran, so a render missing nine subjects announced four. It is
  now computed after the selection, in
  `agents/memory/store.py::_select_within_budget`, and checked at every budget
  that cuts inside the block by
  `test_a_truncated_caveat_list_states_the_subjects_the_budget_dropped`.
- [x] Review correction (second verifier, same defect): the number came from
  `len(uncertain) - len(shown)` in `evidence_context` and could never see a
  budget-shed subject. The notice is now minted post-selection and its cost
  reserved as soon as a caveat is kept — the pattern `_select_trail_within_budget`
  uses for the route's truncation line — and the planted revert to the
  pre-budget count fails the sweep above at budget 980. *Amended 2026-09-08,
  closeout round 1: post-selection minting stands and is what makes the count
  true. The reserve no longer waits for a kept caveat — it runs from the first
  row selected — so the sentence survives a budget that sheds the whole class.*
- [x] Review correction: Results claimed the withheld notice reaches the render
  in ordinary play, while the card's own golden carries no such line at 1,500
  tokens. The claim is withdrawn, superseded in place, and replaced by the
  invariant the code enforces — the sentence closes a caveat list the reader can
  see, so a render keeping no caveat carries none — gated by the "a notice
  closing no list" branch of the same sweep. *Superseded 2026-09-08, closeout
  round 1: the replacement invariant was the narrower of the two available and
  the coordinator reversed the choice. The notice is now reserved before any
  caveat is selected, a render keeping no caveat DOES carry it, and the
  withdrawn round-0 claim is true again as originally written — including on the
  committed golden at 1,500 tokens.*
- [x] Review correction (docs verifier, same sentence): the visibility claim
  named no enforcing mechanism and every notice assertion ran pre-budget against
  `evidence_context_lines`. Both invariants are now asserted on
  `render_for_prompt` output, each with a planted failure recorded in
  "Review corrections, round 1 (2026-09-08)". *Still true: every notice
  assertion runs on `render_for_prompt` output. Which invariants they assert
  changed in closeout round 1 — see the item at the top of this list.*
- [x] Reproduce the eviction first, as a fixture: at the default 1,500-token
  budget a witnessed vent and a third-party sighting are shed while own
  transitions, own task attempts and account-uncertainty lines survive. The
  fixture fails on the current renderer and passes after the change.
- [x] Re-rank inside the evidence-reasoning v2 renderer only. A fixture pair
  proves lever-OFF and evidence-v1 rendered bytes are identical before and
  after; the re-ranking is not applied to either.
- [x] Bound the per-claim account-uncertainty lines with a named constant and
  emit an explicit `N further subjects not shown` line when the bound truncates,
  so shedding is visible rather than silent. Duplicate subjects collapse.
- [x] Own-kill rows (`_SALIENCE_OWN_KILL` = 96, `store.py:1615`) still outrank
  the re-ranked evidence and survive the same budget.
- [x] No committed replay's OFF or evidence-v1 render changes: canonical
  reconstruction and all four derived sample reports stay green.
- [x] Adverse case planted: a speaker emitting many claims cannot push a
  witnessed vent out of the render, and a planted revert of the ordering fails
  the new fixture rather than passing quietly.

## Constraints

Evidence reasoning v2 and temporal v2 stay default-OFF; this repairs a candidate
renderer and is not an adoption or a measurement of model judgment. Add no new
lever, env switch or profile field — the ordering is a property of the v2
renderer, not a new toggle. No re-record, no committed recording or report
rewritten, no provider calls. One writer owns `agents/memory/store.py` for the
duration; card (c) touches the meeting layer and must not run concurrently over
this file. Follow `docs/architecture.md` Layering and Determinism, and keep
listener-visible evidence distinct from privileged reader state.

## Expected scope

`agents/memory/store.py`, `agents/memory/evidence_context.py`,
`tests/agents/test_memory_rendering.py`, and a new fixture pair under
`tests/fixtures/memory_rendering/` (`.json` input plus `.expected.md`).
Directly necessary call-site and docstring updates inside those files may
follow through. Do not edit meeting or reader modules here.

## Record impact

Evidence-v2 rendered prompt bytes only. No committed recording, report, DTO or
schema byte changes, and the default path is untouched. Evaluation impact: every
evidence-v2 arm captured before this lands measured a renderer that evicted its
own evidence, so those captures remain historical mechanics records and are not
comparable to post-repair arms. Adoption remains a separate decision requiring
its own record.

## Validation

`uv run pytest tests/agents/test_memory_rendering.py -q` for the fixture pair
and the planted regression, then `bash scripts/check.sh`, then
`bash scripts/verify_samples.sh`, then the four derived report checks:

```sh
uv run python scripts/build_sample_report.py --sample-dir replays/samples/4p1i --check
uv run python scripts/build_sample_report.py --sample-dir replays/samples/9p2i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/4p1i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/9p2i --check
```

## Results

Implemented on `work/evidence-renderer-salience` from `201849fc` in thirteen
commits before this one (`git log --oneline 201849fc..HEAD` lists them, this
commit last). Round 0:
`7bcc79ed` (the renderer), `af150ce0` (the first held-out restamp), `0c5355a3`
(a format fix the gate asked for) and `9cacd3fc` (the card's first close) — the
commit all five round-1 findings and both Codex comments were raised on. Round 1
of review: `56d3e5fd` (the corrections and their gates), `73b7f53f` (the second
restamp and the `audits/` row) and `bd6f05dc` (the round-1 record in this card).
Closeout round 1: `00ac7fbb` (the unconditional notice reserve, its gates and
the regenerated golden), `0815333d` (the third restamp and both artifacts rows),
`59df8a9e` (the closeout record), `86e133e3` (the round-1 text that record
reverses, superseded in place) and `864b18a1` (naming the commit the closeout
gate was re-run on). Closeout round 2 is `6ba434fb` (the ranking gate, the
corrected headline and this record) and the commit this paragraph ships with,
which withdraws one sentence of that record that claimed more than this worker
can know; the whole gate suite was re-run on the bytes of each, with identical
results, so every number below was measured on exactly the bytes it ships with.

Delivery state: closeout round-2 findings answered and verified locally. Round 1
was re-reviewed on `bd6f05dc` — three verifiers, no blocking findings — and
closeout round 1 was re-reviewed on `864b18a1`, which returned three blocking
findings (two lenses on the same rewritten Outcome sentence, plus this
paragraph's own staleness), all answered below. Not owner reviewed, not merged.
Adoption: not applicable — evidence reasoning v2 stays default-OFF and this
repairs a candidate renderer rather than proposing one.

Where a statement in an earlier section was later found false it keeps its text,
is marked superseded or corrected in place with the date, and the correction
lives in one of the three dated subsections that close this Results: "Review
corrections, round 1 (2026-09-08)", "Review corrections, closeout round 1
(2026-09-08)" and "Review corrections, closeout round 2 (2026-09-08)". All three
carry the same date; the round each belongs to is in its heading, not in the
date.

Architecture and contract sections this follows: `docs/architecture.md`
"Layering" (`agents/` reasons from typed memory and never imports `engine/`;
no new import was added and `lint-imports` is green), "Determinism and the
substrate ladder" (no lever, env variable or profile field was added, and the
five live toggles are unchanged), and "Explicit cleanup experiments", whose
`agents/memory/evidence_context.py` sentence — deriving public death bounds and
conditional walking feasibility from the observer's own records and public
topology — still describes the module exactly, so no architecture text changed.
The listener-visible / privileged distinction is preserved: every re-ranked line
is derived from the agent's own episodic rows and the public map, and the
privileged `self_state` channel is still read only for the render guards.

### Reproduction of the review's claims on this checkout

The three source facts the card cites are exact on `201849fc`:
`_SALIENCE_VENT_WITNESSED = 85` (`agents/memory/store.py:66`),
`_SALIENCE_SAW_PLAYER = 50` (`:77`), `salience = 90` for `own_transition`
(`:1601`) and `own_task_attempt` (`:1612`), the evidence-context block entering
at `salience=90` (`:437-443`), the sort key `(-salience, -tick, line)` (`:459`),
and the one-line-per-claim `Account uncertainty` append
(`agents/memory/evidence_context.py:383`).

The behaviour was reproduced as the new fixture
`tests/fixtures/memory_rendering/evidence_v2_budget_keeps_witnessed_evidence.json`
— a twenty-tick 9p2i-shaped crewmate memory with sixteen own transitions, seven
own task attempts, five third-party sightings, one witnessed vent, one body
discovery and one speaker's seven whereabouts claims — rendered under evidence
v2 at `DEFAULT_TOKEN_BUDGET` = 1,500. Observation-block composition before and
after the repair, same input, same budget:

| class | before | after |
| --- | --- | --- |
| witnessed vent | 0 | 1 |
| third-party sightings | 0 | 5 |
| reported testimony | 0 | 7 |
| body discovery | 1 | 1 |
| death evidence | 1 | 1 |
| negative walking verdicts | 1 of 3 | 3 of 3 |
| other walking verdicts | 0 | 4 |
| account-uncertainty caveats | 7 | 0 |
| own transitions | 16 | 8 |
| own task attempts | 7 | 3 |

The "before" column is reproducible on this tree, byte for byte, by the planted
revert below; the "after" column is the committed
`…evidence_v2_budget_keeps_witnessed_evidence.expected.md`.

### Decisions

1. **A ladder by class, not one band.** `v2_evidence_context_rows` now returns
   `EvidenceContextRow(kind, line, subject_count)` (the third field arrived with
   review correction 2) and `_evidence_context_salience` maps the
   kind to a band: death bounds 84 and a negative walking verdict 83 (just under
   the witnessed vent at 85, above the sightings at 50), the remaining walking
   verdicts 45, own transitions and task attempts 20, the bound notice 16 and the
   account caveat 15. An exhaustive `match` on a `Literal` kind means a new class
   is a type error rather than an unranked line; the mapping is a function, not a
   module-level table, because AGENTS forbids module-level mutable state. These
   are the bands this card sets. Above them the ladder keeps three first-hand
   bands this card does not touch — a body discovery at 100, the observer's own
   kill at 96 and a witnessed kill at 95 — so the witnessed vent leads everything
   except those three; the whole ladder is printed by the command in "Review
   corrections, closeout round 2 (2026-09-08)".
2. **Own routine below every sighting.** The observer's route is already
   rendered in full by the unbudgeted `## Where you were:` block, so an
   own-transition row duplicates something the prompt states anyway.
   *Superseded 2026-09-08, review correction 1: that justification is false. The
   route block holds at most `SELF_LOCATION_TRAIL_MAX_SPANS` = 12 spans
   (`store.py:309` at this head) and is charged against the same budget ahead of the
   observations, shed oldest-first. The ranking decision stands on the corrected
   reasoning, and the placement it costs is a limitation — both in "Review
   corrections, round 1 (2026-09-08)".*
3. **The caveat is the only speaker-inflatable class, so it ranks last and is
   bounded.** `MAX_ACCOUNT_UNCERTAINTY_SUBJECTS` = 6: one row per subject rather
   than one per claim, at most six subjects, then one row saying how many were
   withheld. Six covers every subject in 437 of the 672 meetings in the four
   committed sets (median six placement subjects, largest nine), reproducible
   with the command in "Verification". A subject past the bound keeps its
   travel-check rows, which carry their own "this alone does not prove a role"
   hedge.
4. **A subject with several claims states the count.** Collapsing to one row per
   subject would otherwise silently promote one speaker's claim over another's,
   so a subject named by more than one distinct claim renders "any of the N
   claimed placements stated for them". Distinct means distinct
   `(speaker, room, tick)`: two speakers who agree on one placement render as
   two, which is the point — the count exists so that collapsing never hides a
   speaker, and a placement is only "the same claim" when the same speaker made
   it. *Corrected 2026-09-08, closeout round 1: this decision previously said
   "more than one distinct placement", which is narrower than the key
   `agents/memory/evidence_context.py` actually uses.*
5. **The notice sits one band above the caveats it counts** (16 versus 15), so a
   budget that keeps caveats cannot drop the statement that others were withheld.
   The notice pluralises: `1 further subject not shown`, `3 further subjects not
   shown`.
   *Superseded 2026-09-08, review corrections 2-5: ranking alone left the count
   describing the pre-budget list, so the line could be false. The notice is no
   longer a candidate row at all — `_select_within_budget` mints it after the
   selection and reserves its cost from the first kept caveat. The band is still
   16, which is now only where the minted line is inserted.*
   *Superseded again 2026-09-08, closeout round 1: the reserve is no longer
   charged from the first kept caveat but from the first row selected, and holds
   until every subject is shown, so the budget cannot shed the notice at all —
   whether it keeps caveats or none. The band is still 16 and still only decides
   where the minted line is inserted.*
6. **Evidence v1 keeps its flat band** under the new name
   `_SALIENCE_EVIDENCE_V1_CONTEXT` = 90. v1 is a committed comparison arm; moving
   it would change what the committed v1-versus-v2 captures measured.
7. **`evidence_context_lines` keeps its `tuple[str, ...]` signature**, so
   `eval/reasoning_evidence.py`, `experiments/deduction_evaluation.py` and the
   four test modules outside this card's scope are untouched.

### Verification

Every command below was run on the committed tree at `0c5355a3`, exit codes
captured directly.

- `.venv/bin/python -m pytest tests/agents/test_memory_rendering.py -q` →
  `134 passed`.
- `bash scripts/check.sh` → exit 0. `ruff check` / `ruff format --check` clean,
  `lint-imports` clean, `validate_task_docs` "390 historical phase tasks and 390
  prompts; 43 work cards", `generate_prompts --check` clean, `mypy` "no issues
  found in 469 source files", pytest `7211 passed, 20 skipped, 3 xfailed` in
  226.93 s, frontend `19` test files / `514` tests passed plus lint, tsc and
  build.
- `bash scripts/verify_samples.sh` → exit 0, "All 50 samples verified clean."
  for `replays/samples/4p1i` and again for `replays/samples/9p2i` (100 canonical
  reconstructions).
- The four derived report checks → exit 0 each, "… is consistent with its
  replays." for `replays/samples/4p1i`, `replays/samples/9p2i`,
  `replays/ml_corpus/4p1i` and `replays/ml_corpus/9p2i`.
- `.venv/bin/python -m pytest tests/orchestrator --collect-only -q` in isolation
  → `583 tests collected`.
- `.venv/bin/python scripts/verify_ml_evidence.py` (offline half) →
  `checks: 60 | OK 48 | FAIL 0 | ABSENT 7 | INFO 5`. The seven absent rows are
  the evidence-branch bytes a fresh clone lacks; `--complete` was not run and is
  not claimed.
- The bound's number, over the committed replays only:

  ```sh
  uv run python -c "
  import glob, json, statistics
  from collections import Counter
  kinds = {'whereabouts', 'alibi', 'saw_player'}
  seen = Counter()
  for group in ('replays/samples/4p1i', 'replays/samples/9p2i', 'replays/ml_corpus/4p1i', 'replays/ml_corpus/9p2i'):
      for path in sorted(glob.glob(group + '/replay-seed-*.jsonl')):
          for line in open(path):
              row = json.loads(line)
              if row.get('kind') != 'meeting':
                  continue
              seen[len({str(item.get('subject') or turn['speaker']) for turn in row['transcript']['turns'] for field in ('observations', 'claims') for item in (turn.get(field) or []) if item.get('type') in kinds})] += 1
  print('meetings', sum(seen.values()), 'at most six', sum(v for k, v in seen.items() if k <= 6), 'median', statistics.median([k for k, v in seen.items() for _ in range(v)]), 'max', max(seen))
  "
  ```

  → `meetings 672 at most six 437 median 6.0 max 9`.

No live provider call of any kind was made; the fake provider is the only one
these paths construct, and `scripts/verify_ml_evidence.py --complete` was not
run.

### Planted failures

Each new gate was shown to fail on the defect it claims to detect, by editing
the source, running, and restoring. The counts below were measured on
`0c5355a3` and reproduce there; later rounds added gates to the same `-k`
selections, so the same commands give larger counts at the head. Re-run at
`864b18a1` they gave `7 failed, 15 passed, 116 deselected` (1), `3 failed, 8
passed, 127 deselected` (2) and `1 failed, 10 passed, 127 deselected` (3); at
this head, where closeout round 2 adds one more case to both selections, they
give `8 failed, 15 passed, 116 deselected` (1), `3 failed, 9 passed, 127
deselected` (2) and `1 failed, 11 passed, 127 deselected` (3) — every originally
named test still red, plus the round-1 and closeout gates. The head-side detail
is in "Review corrections, closeout round 1 (2026-09-08)" and, for the deltas
this round adds, in "Review corrections, closeout round 2 (2026-09-08)".

1. **The ordering.** Setting the six new v2 constants back to 90 in
   `agents/memory/store.py` (`_SALIENCE_OWN_ROUTINE`, `…_DEATH`,
   `…_TRAVEL_CONTRADICTED`, `…_TRAVEL`, `…_ACCOUNT_NOTICE`,
   `…_ACCOUNT_UNCERTAINTY`) and rerunning
   `pytest tests/agents/test_memory_rendering.py -k "EvidenceV2Salience or Golden"`
   gives `5 failed, 13 passed, 116 deselected`: the golden fixture,
   `test_the_vent_and_a_sighting_outrank_every_own_routine_row`,
   `test_a_budget_for_a_few_rows_spends_it_on_the_witnessed_evidence`,
   `test_a_claim_flood_cannot_push_the_witnessed_vent_out` and
   `test_a_negative_walking_verdict_outranks_the_caveat_about_the_same_claim`.
   The two arm goldens and the own-kill case stay green, which is the point: the
   revert is v2-only and 96 still outranks 90.
2. **The bound.** Dropping the `[:MAX_ACCOUNT_UNCERTAINTY_SUBJECTS]` slice in
   `agents/memory/evidence_context.py` and rerunning
   `pytest tests/agents/test_memory_rendering.py -k EvidenceV2Salience` gives
   `2 failed, 5 passed, 127 deselected`
   (`test_the_account_caveat_collapses_subjects_and_states_what_it_withheld` and
   the withheld-notice assertion inside
   `test_a_claim_flood_cannot_push_the_witnessed_vent_out`).
3. **The per-subject collapse.** Making `stated.append(placement)` unconditional
   (so a repeated identical claim counts twice) gives `1 failed, 6 passed, 127
   deselected` on the "any of the 2 claimed placements" assertion.
4. **The three reverts together reproduce the pre-repair render exactly.** With
   all three planted, the committed fixture renders byte-identically to the
   capture taken on `201849fc` before any edit — `diff` reports no difference —
   so the "before" column of the table above is reproducible on this tree rather
   than asserted from a working copy nobody else can see.

### Held-out set

`agents/memory/store.py` is one of the twenty-two `GENERATOR_SOURCES` in
`experiments/held_out_prefixes.py`, so `7bcc79ed` turned
`tests/experiments/test_held_out_prefixes.py::test_the_committed_manifest_regenerates_from_its_own_band`
red on its `source_sha256` assertion alone; the `accepted` and `skipped`
assertions above it passed. Regenerating with
`.venv/bin/python -m experiments.held_out_prefixes` and comparing the new
manifest against `HEAD`'s: all 50 accepted prefix digests identical, all 8 skips
identical, `last_accepted_seed` still 3057, and exactly two source digests moved
— `agents/memory/store.py` and `experiments/held_out_prefixes.py`, the latter
because the restamp record was added to it. Following the restamp rule in
`tasks/post-merge-plan.md`, `build_manifest` now emits `dependency_restamps`
(the field the plan says the manifest lacked) carrying a dated entry naming
`7bcc79ed` and this card, plus the rule that a commit which DOES move a prefix
digest or a skip is not restamped but converts the set to development data under
a new card. The list is built by `build_manifest`, so the regeneration test
compares it like every other field. No prefix was printed or opened; the band
was read only through the manifest's own counts. `tests/experiments/test_held_out_prefixes.py`
was not edited — it belongs to the freeze card's writer, and its existing
`rebuilt == manifest` assertion already covers the new field. After the restamp:
`28 passed`.

`docs/artifacts.md` inventory rows recomputed with the change staged: `audits/`
14,850,288 → 14,851,417 tracked bytes across the same 202 files, and
`tests/fixtures/` 2,054,135 → 2,085,311 bytes across 23 → 27 files (the four new
fixture files). Both rows are checked by
`tests/scripts/test_verify_ml_evidence.py::test_every_counted_registry_row_matches_the_index`,
which is red on either row alone; that test and the whole
`tests/scripts/test_verify_ml_evidence.py` module are green (`80 passed`).

### Record impact and limitations

- No committed recording, report, DTO or schema byte changed. The 100 canonical
  reconstructions and all four derived reports are green, and lever-OFF and
  evidence-v1 rendered bytes are pinned byte-for-byte by
  `…lever_off.expected.md` and `…evidence_v1.expected.md`, both captured on
  `201849fc` before any source edit.
- Every evidence-v2 arm captured before this lands measured a renderer that
  evicted its own evidence. Those captures stay historical mechanics records and
  are not comparable to post-repair arms. This is a repair, not an adoption and
  not a measurement of model judgment: v2 remains default-OFF and the adopting
  record for evidence v2 is still outstanding.
- The card's Expected scope names one new fixture pair. Two sibling goldens were
  added beside it in the same owned directory —
  `…lever_off.expected.md` and `…evidence_v1.expected.md` — because acceptance
  item 2 asks for proof that the OFF and v1 bytes are unchanged, and a golden
  captured on the pre-repair tree is the only artifact that can carry that proof
  across the change. `_load_fixture` gained an `arm` argument for them.
- The bound truncates in ordinary play: 235 of the 672 committed meetings name
  more than six placement subjects, so those renders will carry the withheld
  notice. That is the intended trade — the caveat carries no placement, and the
  travel-check rows for a withheld subject still render.
  *Superseded 2026-09-08, review corrections 4 and 5: the arithmetic half holds
  (672 − 437 = 235) but the rendering half was never true and is withdrawn. The
  notice closes a caveat list, so it reaches a prompt only when that prompt keeps
  at least one caveat; at 1,500 tokens this card's own golden keeps none and
  carries neither. What the bound's truncation guarantees is stated correctly in
  "Review corrections, round 1 (2026-09-08)". The rest of the bullet stands: the
  caveat carries no placement, and a withheld subject keeps its travel-check
  rows — `Travel check for p-9` is in the golden.*
  *Restored 2026-09-08, closeout round 1: the withdrawal is itself withdrawn. The
  reserve now runs from the first row selected, so those 235 renders do carry the
  notice, and this card's golden at 1,500 tokens carries it over zero caveats:
  `- Account uncertainty: 7 further subjects not shown.` is the last observation
  bullet in
  `…evidence_v2_budget_keeps_witnessed_evidence.expected.md`. The
  "at least one caveat" clause in the note above is history, not current
  behaviour.*
- The negative-verdict band (83) is above the sightings, and negative verdicts
  are not themselves capped. A speaker who states many DIFFERENT impossible
  placements can therefore fill that band. It cannot reach the witnessed vent at
  85, which is what the adverse case pins, but a cap on that class was neither
  required nor added here; if a later measurement shows it matters, it belongs
  with the accounts-channel card that owns the speaking side.
- The account caveat renders subjects in the order their claims were ingested,
  not by any relevance signal, because the caveat carries no evidence to rank by.
- `tests/agents/test_memory_rendering.py` gained three imports:
  `orchestrator.boundary.public_map_from_engine_map`, so a fixture can declare a
  canonical public map (`engine.world.load_canonical_map` was already imported
  there); `agents.memory.evidence_context` names for the row model and the notice
  sentence; and `typing.Literal` for the arm parameter. No `agents/` module
  gained an import and `lint-imports` is green — "Contracts: 4 kept, 0 broken".
  *Corrected 2026-09-08, closeout round 1: this bullet said "gained one import".
  `git diff 201849fc <head> -- tests/agents/test_memory_rendering.py` shows
  three. The operative claim — no `agents/` module gained a dependency — was and
  is true.*

### Review corrections, round 1 (2026-09-08)

Three independent verifiers returned five blocking findings on `9cacd3fc`. Every
one reproduces on that commit, none is refuted, and all five are repaired by
`56d3e5fd` (the renderer and its gates) and `73b7f53f` (the held-out restamp and
the artifacts row). Delivery state after this round: corrections applied and
verified locally; the round-1 findings are answered, not re-reviewed, not owner
reviewed, not merged.

**Finding 1 — the demotion rested on a claim the code contradicts.** The comment
above `_SALIENCE_OWN_ROUTINE` (`store.py:110-119` at this head; `:108` at
`9cacd3fc`, the commit the finding was raised on), the `_build_v2_observations`
docstring and Decision 2 all said
the observer's route is "rendered IN FULL and unbudgeted" by
`## Where you were:`. It is neither: `SELF_LOCATION_TRAIL_MAX_SPANS` = 12 caps it
(`store.py:309` at this head, applied at `:623-624`; `:278` and `:575-576` at
`9cacd3fc`) and `_select_trail_within_budget` charges
it against the same budget ahead of the observations, shedding oldest-first. All
three statements now say that. The consequence the verifier measured is real and
was recorded nowhere: on the committed fixture at 1,500 tokens, of the twenty
ticks the agent holds a `self_state` row for, seven — 0 through 6 — get no own
placement anywhere in the render, neither from the route (which starts at t7 and
says it is truncated) nor from an own-transition row (that band is shed below
t12) nor from an event-phase row's "immediately before this event" clause:

```sh
uv run python -c "
import importlib.util as u, json, re
from pathlib import Path
from agents.memory.store import render_for_prompt
spec = u.spec_from_file_location('t', 'tests/agents/test_memory_rendering.py')
t = u.module_from_spec(spec); spec.loader.exec_module(t)
base = 'tests/fixtures/memory_rendering/evidence_v2_budget_keeps_witnessed_evidence'
fixture = json.loads(Path(base + '.json').read_text())
memory = t._build_memory_from_fixture(fixture)
view = render_for_prompt(memory, token_budget=1500)
recorded = {e.tick for e in memory.episodic.recent(since_tick=0) if e.type == 'self_state'}
placed = set()
for line in view.splitlines():
    during = re.search(r'during tick (\d+)', line)
    if line.startswith('- Your route (t = tick): '):
        for a, b in re.findall(r't(\d+)(?:-(\d+))?', line):
            placed.update(range(int(a), int(b or a) + 1))
    elif during and ('You moved from' in line or 'You were in' in line):
        placed.add(int(during.group(1)))
print('recorded', len(recorded), 'truncated', '- Earlier parts of your route are not listed.' in view)
print('stated nowhere', sorted(recorded - placed))
"
```

→ `recorded 20 truncated True` and `stated nowhere [0, 1, 2, 3, 4, 5, 6]`, on
`9cacd3fc` and on this tree alike: correcting the comment does not undo the loss,
so the loss is now a limitation and a gate,
`test_a_tick_off_the_trail_keeps_no_own_placement_under_the_budget`. The
verifier's option (b) — promote an own-routine row whose tick falls outside the
rendered trail — was not taken, and this is the reasoning: how far the trail
reaches is decided by `_select_trail_within_budget` from the budget left after
the non-elastic blocks, which is settled AFTER the salience sort that would have
to read it. The rank would have to be computed from its own consequence.

**Findings 2 and 3 (two lenses, one defect) — the withheld count described a list
the prompt does not contain.** `evidence_context` computed `withheld =
len(uncertain) - len(shown)`, only the subjects `MAX_ACCOUNT_UNCERTAINTY_SUBJECTS`
dropped; the notice then entered the candidate rows at band 16 while the budget
shed the caveats at band 15 below it, so the number was fixed before the shedding
it purported to describe. One command reproduces both the defect and the repair:

```sh
uv run python -c "
import importlib.util as u, json
from pathlib import Path
from agents.memory.store import render_for_prompt
spec = u.spec_from_file_location('t', 'tests/agents/test_memory_rendering.py')
t = u.module_from_spec(spec); spec.loader.exec_module(t)
base = 'tests/fixtures/memory_rendering/evidence_v2_budget_keeps_witnessed_evidence'
fixture = json.loads(Path(base + '.json').read_text())
for budget in (1500, 1980, 2500):
    rows = t._observation_rows(render_for_prompt(t._build_memory_from_fixture(fixture), token_budget=budget))
    caveats = [r for r in rows if r.startswith('- Account uncertainty for ')]
    notice = [r for r in rows if r.startswith('- Account uncertainty: ')]
    print(budget, 'caveats', len(caveats), 'of 7 subjects; notice', notice)
"
```

On `9cacd3fc` the middle line reads `1980 caveats 1 of 7 subjects; notice ['-
Account uncertainty: 1 further subject not shown.']` — one caveat rendered, six
subjects missing, the prompt asserting one. On this tree the same line reads
`6 further subjects not shown`, and `2500`, where all six caveats fit, reads
`1 further subject not shown`.

The mechanism: `v2_evidence_context_rows` no longer hands the notice to the
renderer as a candidate row. `EvidenceContextRow` carries `subject_count` — 1 on
a caveat, the bound's withheld count on the notice, 0 on every other class, with
a `model_validator` that rejects any other combination — `render_for_prompt` sums
it into `account_uncertainty_subjects`, and `_select_within_budget` counts the
caveats it actually keeps and mints the sentence from
`account_uncertainty_notice_line(total - kept)` once the selection is made. That
function is the line's one copy, so the two surfaces cannot word it differently.
The unbudgeted `evidence_context_lines` still carries the bound's own count,
which is exact there: that surface renders every row it returns, sheds nothing,
and its docstring now states the distinction rather than leaving both numbers
looking like the same claim.

**Findings 4 and 5 (two lenses, one sentence) — "those renders will carry the
withheld notice" was false.** The sentence is withdrawn and marked superseded
where it stands. What the code enforces is narrower, and now has a mechanism
instead of a hope: the sentence closes a caveat list, so it renders exactly when
the render keeps at least one caveat and leaves at least one subject out, and
`_select_within_budget` reserves its cost from the first kept caveat — the
pattern `_select_trail_within_budget` already used for `_TRAIL_TRUNCATED_LINE`.
No budget can therefore keep part of the list and drop the statement that it is
partial. Swept over 388 budgets from 120 to 3,990 on the committed fixture: 202
render a truncated list and every one carries the correct count, 186 render no
caveat and none carries the sentence, zero violations. The gate
`test_a_truncated_caveat_list_states_the_subjects_the_budget_dropped` runs the
same sweep over 400-2,980 on a ten-subject memory and asserts both halves.
*Superseded 2026-09-08, closeout round 1: this whole paragraph describes the
round-1 mechanism, which no longer ships. The reserve runs from the first row
selected, so the "keeps at least one caveat" condition is gone; the same sweep
now reads `empty 11 correct 377 closing no list 175 violations 0` and the gate
requires the sentence at every budget in its range, not only where a list
survives. The withdrawal this paragraph justifies is itself withdrawn.*

Why the notice is not reserved unconditionally, which would make the withdrawn
sentence true as written: it would state a quantity with nothing to count
against — "7 further subjects not shown" above a render showing no caveat at all
names subjects the reader cannot locate — and it would let a speaker's claim
volume buy a line from first-hand evidence. Measured, not assumed: with the
reserve charged from the first row rather than the first caveat, the committed
fixture at 290 tokens renders the body discovery and the notice and drops the
witnessed vent, which is planted failure 2 below and what
`test_the_withheld_notice_never_costs_the_witnessed_evidence_a_line` now forbids.
Ranking is not an alternative to the reserve either: the budget cuts above band
16 as readily as below it, which is why the notice was silent at 1,500 tokens to
begin with.
*Superseded 2026-09-08, closeout round 1: the coordinator reversed this choice
and the unconditional reserve is what ships. The measurement stands and is
reproduced at the new head — 290 tokens still buys the notice with the witnessed
vent — but it is now the accepted price rather than the reason to decline, and
`test_the_withheld_notice_never_costs_the_witnessed_evidence_a_line` is replaced
by `test_the_production_budget_keeps_the_witnessed_evidence_beside_the_notice`,
which pins the same 290-token render as the price and the production budget as
the case where nothing is paid. The reasoning that fell: "a quantity with nothing
to count against" weighs a reader's momentary confusion against a render that
silently hides speaker-supplied subjects, and the second is the worse failure —
the reader cannot even know those subjects existed. Ranking is still not an
alternative, for the reason given.*

**Verification (round 1).** Run at `73b7f53f`, the tree this card's own Markdown
and one test docstring are the only later change to; exit codes captured
directly.

- `.venv/bin/python -m pytest tests/agents/test_memory_rendering.py
  tests/agents/test_evidence_context.py -q` → `162 passed` (138 in the rendering
  module, four of them new).
- `bash scripts/check.sh` → exit 0. `ruff check` "All checks passed!",
  `ruff format --check` "498 files already formatted", `lint-imports`
  "Contracts: 4 kept, 0 broken", `validate_task_docs` "390 historical phase
  tasks and 390 prompts; 43 work cards", `generate_prompts --check` "All 390
  prompts are in sync", `mypy` "no issues found in 469 source files", pytest
  `7215 passed, 20 skipped, 3 xfailed` in 327.56 s (the four new cases are the
  whole difference from the 7,211 of round 0), frontend lint, `tsc:check`,
  `19` test files / `514` tests passed, and the production build.
- `bash scripts/verify_samples.sh` → exit 0, "All 50 samples verified clean."
  for `replays/samples/4p1i` and again for `replays/samples/9p2i` (100 canonical
  reconstructions).
- The four derived report checks → exit 0 each, "… is consistent with its
  replays." for `replays/samples/4p1i`, `replays/samples/9p2i`,
  `replays/ml_corpus/4p1i` and `replays/ml_corpus/9p2i`.
- `.venv/bin/python -m pytest tests/orchestrator --collect-only -q` in isolation
  → `583 tests collected`.
- `.venv/bin/python scripts/verify_ml_evidence.py` (offline half) →
  `checks: 60 | OK 48 | FAIL 0 | ABSENT 7 | INFO 5`, "every check passed", exit
  0. The seven absent rows are the evidence-branch bytes a fresh clone lacks.

The frontend leg needed `npm ci` in this worktree before it could run: the first
attempt exited 127 on `eslint: command not found`, which is a missing local
install and not a finding. No live provider call of any kind was made in this
round either; `scripts/verify_ml_evidence.py --complete` was not run.

**Planted failures (round 1).** Each new gate was shown to fail on the defect it
claims to detect, by editing the source, running, and restoring.

1. **The pre-budget count.** Returning the notice to the candidate rows (drop the
   `if row.kind != "account_uncertainty_notice"` filter and set
   `account_uncertainty_subjects = 0`) restores exactly the reviewed behaviour and
   fails
   `test_a_truncated_caveat_list_states_the_subjects_the_budget_dropped` at budget
   980 with `a notice closing no list` /
   `['- Account uncertainty: 4 further subjects not shown.']`. Sweeping that
   planted tree over 900-1,580 shows the defect's whole shape: at 1,020 one caveat
   of ten subjects renders and the line still says four; at 1,140, five render and
   it still says four.
2. **The reserve's scope.** Charging the reserve from the first row
   (`reserved = _account_notice_cost(...)` unconditionally, and emitting the notice
   whenever anything was kept) gives `3 failed`:
   `test_the_withheld_notice_never_costs_the_witnessed_evidence_a_line`
   (`assert 'You witnessed p-6 vent in ENGINEERING.' in '- Account uncertainty: 7
   further subjects not shown.'`), the same sweep's "closing no list" branch, and
   the v2 golden.
   *Superseded 2026-09-08, closeout round 1: this edit is no longer a plant, it
   is the shipping behaviour, and all three tests it broke were changed
   deliberately — the gate named here is replaced by
   `test_the_production_budget_keeps_the_witnessed_evidence_beside_the_notice`,
   the sweep's branch is inverted, and the golden was regenerated. Its measured
   consequence, the vent giving way to the notice at 290 tokens, is unchanged and
   is now the card's stated price. The plant that proves the CURRENT reserve is
   its inverse, closeout planted failure 1.*
3. **The ordering the correction defends.** Setting `_SALIENCE_OWN_ROUTINE` back
   to 90 fails
   `test_a_tick_off_the_trail_keeps_no_own_placement_under_the_budget`: the seven
   unstated ticks become two, so the test measures the demotion rather than the
   fixture.
4. **The row's own count.** Dropping `subject_count=1` from the caveat row in
   `v2_evidence_context_rows` — the edit that would silently make every withheld
   count too small — raises out of the validator instead: `9 failed` across the v2
   salience and golden cases, and
   `test_a_caveat_row_that_counts_no_subject_is_rejected` pins the three rejected
   combinations directly.

**Held-out set (round 1).** `agents/memory/store.py` moved again, so
`tests/experiments/test_held_out_prefixes.py::test_the_committed_manifest_regenerates_from_its_own_band`
went red on `source_sha256` alone, with the `accepted` and `skipped` assertions
above it passing. Regenerated with
`.venv/bin/python -m experiments.held_out_prefixes` and compared field by field
against the committed manifest: all 50 accepted digests identical, all 8 skips
identical, `last_accepted_seed` still 3057, band and roster identical, no other
field changed, and exactly two source digests moved — `agents/memory/store.py`
and `experiments/held_out_prefixes.py`, the latter because the restamp entry was
added to it. `DEPENDENCY_RESTAMPS` gained a second dated entry naming `56d3e5fd`.
No prefix was printed or opened; the band was read only through the manifest's
own counts. The manifest grew 12,653 → 13,275 bytes, so `docs/artifacts.md`'s
`audits/` row was recomputed with the change staged: 14,851,417 → 14,852,039
tracked bytes across the same 202 files (`git ls-files audits` = 202 files). The
`tests/fixtures/` row is untouched this round — no fixture file changed, and the
three committed goldens still render byte-for-byte, v2 included.
`tests/experiments/test_held_out_prefixes.py` and
`tests/scripts/test_verify_ml_evidence.py` together: `108 passed`.

**Scope this round.** The same four owned paths plus the two the restamp rule
directs here (`experiments/held_out_prefixes.py`,
`audits/deduction-candidate/held-out/manifest.json`) and the `docs/artifacts.md`
row. `test_a_caveat_row_that_counts_no_subject_is_rejected` exercises a model in
`agents/memory/evidence_context.py` but lives in
`tests/agents/test_memory_rendering.py`, the test module this card owns;
`tests/agents/test_evidence_context.py` was deliberately not opened. No fixture
file changed, no new lever, env switch or profile field, no committed recording,
report, DTO or schema byte.

**Limitations this round adds or corrects.**

- Under evidence v2 a tick that has fallen off the rendered route keeps no own
  placement in the prompt once the routine band is shed — seven of twenty ticks
  on the committed fixture at the production budget. The trade is deliberate:
  those rows are the observer's own past position, which no other player's
  testimony rests on, and the alternative is the eviction of witnessed evidence
  this card exists to stop. It is pinned rather than merely stated.
- A render that keeps no account-uncertainty caveat says nothing about the class,
  exactly like every other class the budget sheds. At 1,500 tokens on the
  committed fixture that is what happens, so the caveats' hedging work falls to
  the travel-check rows and to the self-framing of the testimony rows
  ("CLAIM by … (unverified)"), both of which do render there.
  *Superseded 2026-09-08, closeout round 1: half of this is now false. Such a
  render still shows no caveat — the hedging work does still fall to the
  travel-check and testimony rows, which is the half that stands — but it no
  longer says nothing about the class: it carries the withheld-subjects notice.
  On the committed fixture at 1,500 tokens the notice is the last observation
  bullet, over zero caveats.*
- The reserve costs the caveat block at most one of its own rows: a budget that
  would have fitted the last caveat spends that room on the sentence saying the
  list is short. It never costs any other class a row.
  *Superseded 2026-09-08, closeout round 1: the reserve now runs from the first
  row selected, so it can cost any class its last row, not only the caveats. It
  is still at most ONE row, it is still paid only by a render that goes on to
  carry the notice, and it is paid only where the budget cuts inside the reserved
  margin — on the committed fixture at the production budget it costs nothing at
  all. Measured both ways in the closeout subsection below.*

### Review corrections, closeout round 1 (2026-09-08)

Three independent verifiers returned NO blocking findings on `bd6f05dc`. The
coordinator overruled three of their nonblocking items into required changes;
this subsection records those three, what else in the nonblocking set was fixed,
and why the remainder stays. Repaired by `00ac7fbb` (the renderer, its gates and
the golden) and `0815333d` (the third held-out restamp and the `audits/` row).
Delivery state: closeout findings answered and verified locally; not
re-reviewed, not owner reviewed, not merged.

**Finding A — the render the model reads could still hide subjects silently.**
Acceptance item 3 asks for an explicit `N further subjects not shown` line when
the bound truncates. After round 1 that held on the unbudgeted
`evidence_context_lines` surface and, in `render_for_prompt`, only when at least
one caveat survived the budget. On the committed fixture — seven caveat subjects
against a bound of six, so the bound does truncate — the model-facing render at
`DEFAULT_TOKEN_BUDGET` carried neither a caveat nor the notice. Reproduced on
`bd6f05dc` and again as the "before" column here:

| budget | caveats of 7 | notice, before | notice, after |
| --- | --- | --- | --- |
| 290 | 0 | — | `7 further subjects not shown` |
| 1,500 | 0 | — | `7 further subjects not shown` |
| 1,980 | 1 | `6 further subjects not shown` | `6 further subjects not shown` |
| 2,500 | 6 | `1 further subject not shown` | `1 further subject not shown` |

The mechanism: `_select_within_budget` reserves the notice's cost from the FIRST
row it selects, not from the first kept caveat, and keeps it reserved until
every subject is shown. The reserve is exact rather than pessimistic — at each
row it is `_account_notice_cost(total - shown_after)`, the cost of the sentence
that row's acceptance would leave due — so it is charged only while a notice is
genuinely owed, and it drops to zero the moment the last subject renders. Two
consequences follow by construction rather than by test: the reserve is never
spent on nothing (a break can only happen while subjects are unshown, and then
the notice is due and renders), and the sentence always fits (the last accepted
row reserved exactly what the minted line costs).

The whole shape, swept over 388 budgets from 120 to 3,990 on the committed
fixture:

```sh
uv run python -c "
import importlib.util as u, json
from pathlib import Path
from agents.memory.store import render_for_prompt
from agents.memory.evidence_context import account_uncertainty_notice_line
spec = u.spec_from_file_location('t', 'tests/agents/test_memory_rendering.py')
t = u.module_from_spec(spec); spec.loader.exec_module(t)
base = 'tests/fixtures/memory_rendering/evidence_v2_budget_keeps_witnessed_evidence'
memory = t._build_memory_from_fixture(json.loads(Path(base + '.json').read_text()))
empty = correct = closing_no_list = violations = 0
for budget in range(120, 4000, 10):
    rows = t._observation_rows(render_for_prompt(memory, token_budget=budget))
    shown = [r for r in rows if r.startswith('- Account uncertainty for ')]
    notice = [r for r in rows if r.startswith('- Account uncertainty: ')]
    if not rows:
        empty += 1
        continue
    if notice != ['- ' + account_uncertainty_notice_line(7 - len(shown))]:
        violations += 1
        continue
    correct += 1
    closing_no_list += not shown
print('budgets', 388, 'empty', empty, 'correct', correct, 'closing no list', closing_no_list, 'violations', violations)
"
```

→ `budgets 388 empty 11 correct 377 closing no list 175 violations 0`. The
eleven are budgets 120-220, where the non-elastic blocks leave no room for any
observation and the notice has nothing to be reserved from; 230-260 render the
notice as the only observation. The gate
`test_a_truncated_caveat_list_states_the_subjects_the_budget_dropped` runs the
same sweep over 400-2,980 on a ten-subject memory and now asserts the notice at
EVERY budget, counting separately the renders that close a visible list and the
renders that close none, and failing if either count is zero.

What the reserve costs, measured both ways and pinned by
`test_the_production_budget_keeps_the_witnessed_evidence_beside_the_notice`: at
`DEFAULT_TOKEN_BUDGET` on the committed fixture it costs nothing — the
regenerated golden's diff against `bd6f05dc` is one added line, the notice, with
no row displaced, so the witnessed vent, all five third-party sightings and the
seven testimony rows still render. At 290 tokens, where there is room for
exactly two observations, it costs the witnessed vent. That is the trade the
round-1 note above declined and the coordinator accepted: a render that hides
speaker-supplied subjects must say so, because a reader cannot otherwise know
they existed.

Unchanged by this finding, and re-verified: own-kill rows still lead
(`test_an_own_kill_row_outranks_every_re_ranked_evidence_line`, a 40-claim flood
at 200 tokens), and the lever-OFF and evidence-v1 goldens are byte-identical —
the fixture diff between `bd6f05dc` and this head touches only
`…evidence_v2_budget_keeps_witnessed_evidence.expected.md`. The notice exists
only on the v2 path: `account_uncertainty_subjects` is 0 on every other arm, so
`_account_notice_cost` returns 0 and no reserve is charged.

**Finding B — the reserve's guard was a production `assert`.** `python -O`
strips assertions, so the one statement standing between a broken reserve and a
prompt over its token budget could vanish from a production run. It is now an
explicit `raise` of the named `UnreservedAccountNoticeError`
(`agents/memory/store.py:177` for the class, raised at `:2925`), carrying the
token arithmetic. It is not reachable from any input — the reserve makes it
unreachable, which is what a guard is for — so it is proved by perturbation:
planted failure 1 below restores the round-1 conditional reserve and three of
the four resulting reds are this error, e.g. `the withheld-subjects notice was
not reserved while rows were selected: 14 tokens due for 40 withheld subjects, 1
left of a 1378-token budget`.

**Finding C — statements wider than the code, and stale anchors.** All corrected
in place:

- The Outcome said the render "keeps the witnessed evidence a meeting could act
  on — vent sightings and sightings of other players". Only the vent is
  protected outright: at 85 it clears the uncapped
  `_SALIENCE_EVIDENCE_TRAVEL_CONTRADICTED` = 83 and everything below. A sighting
  sits at 50, under `_SALIENCE_REPORTED_TESTIMONY` = 60 (`store.py:96`), which
  this card does not touch. The adverse probe — 42 claims from one speaker about
  the already-observed p-3, spread over three ticks and eight rooms so each
  mints its own testimony row and negative verdict:

  ```sh
  uv run python -c "
  import importlib.util as u
  from agents.memory.store import render_for_prompt
  spec = u.spec_from_file_location('t', 'tests/agents/test_memory_rendering.py')
  t = u.module_from_spec(spec); spec.loader.exec_module(t)
  rooms = ['REACTOR','LABS','ADMIN','MEDBAY','STORAGE','ENGINEERING','WEST_HALL','CAFETERIA']
  memory = t._v2_memory()
  for i in range(42):
      t._v2_claim(memory, subject='p-3', speaker='p-5', tick=1 + (i // len(rooms)) % 3, room=rooms[i % len(rooms)])
  for budget in (200, 400, 800, 1500, 3000):
      rows = t._observation_rows(render_for_prompt(memory, token_budget=budget))
      print('budget', budget, 'rows', len(rows),
            'vent', sum(t._VENT_LINE_FRAGMENT in r for r in rows),
            'p-3 sighting', sum(t._SIGHTING_LINE_FRAGMENT in r for r in rows),
            'contradicted', sum('walking cannot reconcile' in r for r in rows),
            'testimony', sum('CLAIM by' in r for r in rows))
  "
  ```

  → the vent survives at every budget (`vent 1` at 200, 400, 800, 1,500 and
  3,000) while the p-3 sighting is absent from 200 through 1,500 and returns at
  3,000, with 30 testimony rows and 9 negative verdicts occupying 1,500. This is
  not a regression this card introduced — testimony outranked sightings before
  it — but the Outcome did not qualify the sighting half, and now does. Moving
  band 60 belongs to the card that owns the speaking side, not here.
- Every `store.py` line number inside "Review corrections, round 1" pointed at
  `9cacd3fc`, the commit the findings were raised on, while the surrounding
  sentences described the corrected code. Each now carries this head's number
  with the old one named as history: the constant at `:309` (was `:278`),
  applied at `:623-624` (was `:575-576`), the corrected comment block at
  `:110-119` (was `:108`). The `## Evidence` section's citations are exact on
  `201849fc`, which it names, and were re-checked: `:66`, `:77`, `:1601`,
  `:1612`, `:437-443`, `:459` and `evidence_context.py:383`.
- The round-0 "Planted failures" counts were measured on `0c5355a3` and do not
  reproduce at the head, because each later round added gates to the same `-k`
  selections. That block now carries the head's counts beside the originals.
- "Two surfaces, two numbers" is now stated as the invariant it is, in
  `account_uncertainty_notice_line`'s docstring: one copy of the sentence, and
  each surface states what THAT surface withholds. The unbudgeted
  `evidence_context_lines` sheds nothing, so its count is the per-subject
  bound's alone; `render_for_prompt` counts the bound's subjects plus the ones
  its budget shed. The only non-test consumer, `eval/reasoning_evidence.py`, is
  on the v1 arm and reads neither.
- Decision 4 said "a subject with more than one distinct placement", which is
  narrower than the `(speaker, room, tick)` key the code uses: two speakers
  agreeing on one placement render as two. Corrected in place; the design intent
  (collapsing never hides a speaker) is what the wider key serves.
- "Record impact and limitations" said the test module "gained one import"; the
  diff against `201849fc` shows three. Corrected in place, with the operative
  claim — no `agents/` module gained a dependency, `lint-imports` "Contracts: 4
  kept, 0 broken" — unchanged.
- `7bcc79ed`'s commit message body says "The observer's route is already
  rendered in full by the unbudgeted route block, so an own-transition row
  duplicates it." Round-1 finding 1 established that this is false — the route is
  capped at `SELF_LOCATION_TRAIL_MAX_SPANS` = 12 spans and charged against the
  same budget — and the delivery policy forbids amending a pushed commit, so the
  history will carry the false sentence into main. The correct statement, for a
  reader arriving from that message: inside the window the route block renders,
  an own-transition row duplicates a placement the route already states; outside
  that window the placement is stated nowhere, which is the limitation
  `test_a_tick_off_the_trail_keeps_no_own_placement_under_the_budget` pins. The
  ranking decision rests on the corrected reasoning, not on the message's.

**Nonblocking items left standing.** One, with its reason: a render of 120-220
tokens on the committed fixture carries no observation block and therefore no
notice either. Nothing is reserved because nothing was selected, and a prompt
with no observations has no shedding to disclose; the alternative — spending a
budget that fits no evidence on a sentence about evidence — states a quantity
with nothing to count against and nothing beside it. It is a stated limitation
rather than a defect, and the sweep counts those eleven budgets explicitly
rather than skipping them.

**Codex review.** Two comments, both re-fetched at this head; no new review was
triggered by `56d3e5fd`, `73b7f53f`, `bd6f05dc`, `00ac7fbb` or `0815333d` (the
PR's review-comments endpoint returns the same two, the latest review
`COMMENTED` on `9cacd3fc`).

- **P1, "Preserve the commit named by the restamp record" — REFUTED, no change.**
  Codex asserts that the reviewed commit is "a sibling of `7bcc79ed`, not its
  descendant (`029aaab` and `7bcc79ed` both have `201849fc` as their parent)",
  so the manifest would cite a commit the delivered history will not preserve.
  There is no such object: `cat-file -t 029aaab` reports `fatal: Not a valid
  object name 029aaab`. The branch is one linear chain —
  `0815333d ← 00ac7fbb ← bd6f05dc ← 73b7f53f ← 56d3e5fd ← 9cacd3fc ← 0c5355a3 ←
  af150ce0 ← 7bcc79ed ← 201849fc` — and `merge-base --is-ancestor` succeeds for
  each of the three commits `dependency_restamps` names (`7bcc79ed`,
  `56d3e5fd`, `00ac7fbb`) against the head, while `rev-parse 7bcc79ed^` is
  `201849fc`. Under the post-#436 delivery policy (merge commit or fast-forward,
  never squash, never amend) all three stay retrievable in main.
- **P2, "Keep the truncation notice through the prompt budget" — VALID, now
  fully addressed.** Its first half (the band-16 notice can be budget-shed, so
  the count describes a list the prompt does not contain) was repaired by
  `56d3e5fd`; its second half (assert on `render_for_prompt`, not on
  `evidence_context_lines`) was answered by the same commit. Its remaining
  recommendation — protect the notice in the final render so it always ships —
  was declined in round 1 and is implemented here by `00ac7fbb`. Codex's
  observation that a 1,500-token render of a seven-subject memory carried no
  notice is no longer true at this head: it carries
  `- Account uncertainty: 7 further subjects not shown.`

**Verification (closeout round 1).** Run on the committed tree at `0815333d`,
and `scripts/check.sh` re-run at `86e133e3` with identical numbers — the two
commits in between change this card's Markdown only. Exit codes captured
directly, never through a pipe, and each log checked for its own worktree's
`rootdir` because a concurrent session on this machine shares the scratch
directory.

- `.venv/bin/python -m pytest tests/agents/test_memory_rendering.py
  tests/agents/test_evidence_context.py -q` → `162 passed` (138 in the rendering
  module; one round-1 gate was replaced by one closeout gate, so the count is
  unchanged from round 1).
- `bash scripts/check.sh` → exit 0. `ruff check` "All checks passed!",
  `ruff format --check` "498 files already formatted", `lint-imports`
  "Contracts: 4 kept, 0 broken", `validate_task_docs` "390 historical phase
  tasks and 390 prompts; 43 work cards", `generate_prompts --check` "All 390
  prompts are in sync", `mypy` "no issues found in 469 source files", pytest
  `7215 passed, 20 skipped, 3 xfailed`, and the frontend leg: lint, `tsc:check`,
  `19` test files / `514` tests passed, and the production build.
- `bash scripts/verify_samples.sh` → exit 0, "All 50 samples verified clean."
  for `replays/samples/4p1i` and again for `replays/samples/9p2i` (100 canonical
  reconstructions).
- The four derived report checks → exit 0 each, "… is consistent with its
  replays." for `replays/samples/4p1i`, `replays/samples/9p2i`,
  `replays/ml_corpus/4p1i` and `replays/ml_corpus/9p2i`.
- `.venv/bin/python -m pytest tests/orchestrator --collect-only -q` in isolation
  → `583 tests collected`.
- `.venv/bin/python scripts/verify_ml_evidence.py` (offline half) →
  `checks: 60 | OK 48 | FAIL 0 | ABSENT 7 | INFO 5`, exit 0. The seven absent
  rows are the evidence-branch bytes a fresh clone lacks; `--complete` was not
  run and is not claimed.

No live provider call of any kind was made in this round: the fake provider is
the only one these paths construct.

**Planted failures (closeout round 1).** Each edit was applied to the source,
run, and restored; the working tree is clean of all of them. The counts are the
tree at `0815333d`. Closeout round 2 adds one case to both `-k` selections, so
each of the seven gains exactly one pass or one fail at this head; the
re-measured values are listed in "Review corrections, closeout round 2
(2026-09-08)".

1. **The conditional reserve** (the round-1 behaviour this round reverses):
   restoring `if shown_after else 0` around the reserve gives `4 failed, 18
   passed, 116 deselected` on
   `pytest tests/agents/test_memory_rendering.py -k "EvidenceV2Salience or Golden"`
   — `test_a_claim_flood_cannot_push_the_witnessed_vent_out`,
   `test_an_own_kill_row_outranks_every_re_ranked_evidence_line` and
   `test_a_truncated_caveat_list_states_the_subjects_the_budget_dropped` by
   raising `UnreservedAccountNoticeError` (the guard of finding B, doing its
   job), and
   `test_the_production_budget_keeps_the_witnessed_evidence_beside_the_notice`
   on the missing notice at 1,500 tokens.
2. **The pre-budget count** (round-1 planted failure 1, re-run here): returning
   the notice to the candidate rows and zeroing `account_uncertainty_subjects`
   gives `3 failed, 19 passed, 116 deselected` — the same sweep, the new
   production-budget gate, and the v2 golden.
3. **The ordering** (round-0 planted failure 1, re-run here): the six v2
   constants back to 90 gives `7 failed, 15 passed, 116 deselected`, every test
   the round-0 record named plus
   `test_a_tick_off_the_trail_keeps_no_own_placement_under_the_budget` and the
   new production-budget gate.
4. **The demotion** (round-1 planted failure 3, re-run here):
   `_SALIENCE_OWN_ROUTINE` back to 90 gives `5 failed, 17 passed, 116
   deselected`.
5. **The bound** (round-0 planted failure 2, re-run here): dropping the
   `[:MAX_ACCOUNT_UNCERTAINTY_SUBJECTS]` slice gives `3 failed, 8 passed, 127
   deselected` on `-k EvidenceV2Salience`.
6. **The per-subject collapse** (round-0 planted failure 3, re-run here): making
   `stated.append(placement)` unconditional gives `1 failed, 10 passed, 127
   deselected`.
7. **The row's own count** (round-1 planted failure 4, re-run here): dropping
   `subject_count=1` from the caveat row gives `9 failed, 13 passed, 116
   deselected`.

**Held-out set (closeout round 1).** `agents/memory/store.py` moved a third
time, so
`tests/experiments/test_held_out_prefixes.py::test_the_committed_manifest_regenerates_from_its_own_band`
went red on `source_sha256` alone — the failure names exactly one differing key,
`agents/memory/store.py`. Regenerated with
`.venv/bin/python -m experiments.held_out_prefixes` and compared field by field
against the committed manifest: all 50 accepted digests identical, all 8 skips
identical, `last_accepted_seed` still 3057, band, roster,
`skipped_reason_counts` and `development_definitions` identical, the top-level
key set identical, and exactly two of the 22 source digests moved —
`agents/memory/store.py` and `experiments/held_out_prefixes.py`, the latter
because the third restamp entry was added to it. `DEPENDENCY_RESTAMPS` gained a
dated entry naming `00ac7fbb` and this card. The `7bcc79ed` entry's note also
said `held_out_prefixes.py` moved "because this restamp list was added to it",
which read as if `7bcc79ed` had made that edit; the list was added in the
restamp commit that followed it, `af150ce0`, and the note now says so. No prefix
was printed or opened; the band was read only through the manifest's own counts.
`tests/experiments/test_held_out_prefixes.py` was not edited. After the restamp:
`28 passed`.

`docs/artifacts.md` inventory rows recomputed with the change staged, from
`git ls-files` and `git cat-file --batch-check`: `tests/fixtures/` 2,085,311 →
2,085,364 tracked bytes across the same 27 files (the one regenerated golden),
and `audits/` 14,852,039 → 14,852,791 tracked bytes across the same 202 files
(the manifest grew 13,275 → 14,027 bytes). Both are pinned by
`tests/scripts/test_verify_ml_evidence.py::test_every_counted_registry_row_matches_the_index`;
that module is green (`80 passed`). The `audits/` row is contended with
`origin/work/followup-review-dispositions`, which rewrites the same line for its
own tree — same-line edits, so git conflicts rather than mismerging, and
whichever card merges second must recompute the row from its own tree rather
than taking either side.

**Scope this round.** `agents/memory/store.py`,
`agents/memory/evidence_context.py` (docstrings only),
`tests/agents/test_memory_rendering.py`, the one v2 golden, plus the two paths
the restamp rule directs here (`experiments/held_out_prefixes.py`,
`audits/deduction-candidate/held-out/manifest.json`), the two `docs/artifacts.md`
rows and this card. No fixture INPUT changed, no new lever, env switch or profile
field, no committed recording, report, DTO or schema byte, and the default path
is untouched.

**Limitations this round adds or corrects.**

- A sighting of another player is not protected against reported testimony: 50
  against 60. A speaker with enough distinct claims still evicts sightings from
  the production render — 42 claims does it on the probe above — while the
  witnessed vent at 85 survives. Band 60 is outside this card's scope and
  belongs with the accounts-channel card that owns the speaking side.
- The notice's reserve can cost one row of any class, not only a caveat. It is
  paid only by a render that goes on to carry the notice, and only where the
  budget cuts inside the reserved margin: nothing at the production budget on
  the committed fixture, the witnessed vent at 290 tokens. Both are pinned.
- A render with no observation block at all — 120 to 220 tokens on the committed
  fixture — carries no notice, because nothing was selected to reserve it from.
- Every number in this subsection was produced by a command run on the committed
  tree at `00ac7fbb` or `0815333d`; the two commands worth re-running are quoted
  above in full.

### Review corrections, closeout round 2 (2026-09-08)

The verification round on `864b18a1` returned three blocking findings from two
lenses: two on the Outcome sentence closeout round 1 had just rewritten, one on
the opening paragraph of this Results. All three are documentation defects — no
shipped behaviour was found wrong this round — so the only source change is one
new gate, which turns the corrected headline into an assertion on rendered rows
instead of a claim about eighteen constants.

**Findings 1 and 2 (two lenses, one sentence) — the rewritten ranking claim was
false.** Closeout round 1 replaced one over-wide Outcome with another: "A
witnessed vent (band 85) now outranks everything the renderer emits except the
observer's own kill (96)". Three bands sit above 85, and the v2 path emits all
three. The ladder, read from the constants the renderer sorts by:

```sh
uv run python -c "
import agents.memory.store as s
names = [n for n in dir(s) if n.startswith('_SALIENCE_') and n != '_SALIENCE_EVIDENCE_V1_CONTEXT']
bands = sorted(((getattr(s, n), n) for n in names), reverse=True)
print(' '.join(f'{v}:{n[10:].lower()}' for v, n in bands))
print('above the vent:', [(v, n) for v, n in bands if v > s._SALIENCE_VENT_WITNESSED])
"
```

→ `100:found_body 96:own_kill 95:kill_witnessed 85:vent_witnessed
84:evidence_death 83:evidence_travel_contradicted 65:sabotage_heard
60:reported_testimony 55:saw_player_active 52:saw_player_move 50:saw_player
48:transition 45:evidence_travel 30:completed_task 20:own_routine
16:evidence_account_notice 15:evidence_account_uncertainty 10:cooldown_status`,
and `above the vent: [(100, '_SALIENCE_FOUND_BODY'), (96,
'_SALIENCE_OWN_KILL'), (95, '_SALIENCE_KILL_WITNESSED')]` — three bands, not
one. The same three lead in the render, on a crewmate memory carrying a body
discovery, a witnessed kill of another player and the fixture's witnessed vent:

```sh
uv run python -c "
import importlib.util as u
from agents.memory.episodic import EpisodicEvent
from agents.memory.store import render_for_prompt
spec = u.spec_from_file_location('t', 'tests/agents/test_memory_rendering.py')
t = u.module_from_spec(spec); spec.loader.exec_module(t)
memory = t._v2_memory()
memory.episodic.append(t._saw_body_event(tick=6, body_id='b-2', victim_id='p-2', room='ADMIN'))
memory.episodic.append(EpisodicEvent(tick=6, type='saw_player', payload={'player_id': 'p-4', 'room': 'MEDBAY', 'action': 'kill', 'observation_phase': 'event', 'observation_order': 4, 'observer_room': 'MEDBAY', 'observer_in_vent': False}, provenance='observed'))
for budget in (200, 220, 1500):
    rows = t._observation_rows(render_for_prompt(memory, token_budget=budget))
    print('budget', budget, 'rows', len(rows),
          'body', [i for i, r in enumerate(rows) if \"discovered p-2's body\" in r],
          'kill', [i for i, r in enumerate(rows) if 'You witnessed p-4 kill' in r],
          'vent', [i for i, r in enumerate(rows) if t._VENT_LINE_FRAGMENT in r])
"
```

→ `budget 200 rows 2 body [0] kill [1] vent []`, `budget 220 rows 3 body [0]
kill [1] vent [2]`, `budget 1500 rows 14 body [0] kill [1] vent [2]`. A budget
with room for two observations spends both above the vent and sheds it; every
wider budget puts the vent third, behind exactly those two. The card already
contradicted its own sentence in two places — the composition table lists a
surviving body-discovery row, and
`test_the_production_budget_keeps_the_witnessed_evidence_beside_the_notice`
asserts `You discovered p-2's body in ADMIN.` is the first row at 290 tokens —
so the body half was pinned and only the prose was wrong about it. The witnessed
kill was pinned nowhere, which is how the sentence survived two review rounds.

Fixed by stating what the ladder enforces. The Outcome now says the vent
outranks every derived evidence-context class, every sighting, all of the
observer's own routine and the reported testimony at 60, and is itself outranked
only by the body discovery (100), the observer's own kill (96) and the witnessed
kill (95) — three bands this card does not move. Decision 1 gained the same
clause, because it lists only the bands this card sets and a reader could take
that list for the whole ladder. The claim is now enforced by
`test_only_the_body_and_the_witnessed_kill_outrank_the_witnessed_vent`, which
asserts the 200-token and the production render of the probe above — the two
that carry the claim, one where the vent is shed under both bands and one where
it sits directly behind them; the own-kill band keeps the gate it
already had (`test_an_own_kill_row_outranks_every_re_ranked_evidence_line`). The
gate's memory carries no spoken claim, so it does not depend on the caveat block
or its reserve: of the seven plants re-run below, only the two that promote a
band above the vent redden it.

The second half of finding 2 was the same sentence contradicting itself: "so
neither the observer's own movement log nor a speaker's claim volume can shed
them", two lines above "a large enough claim volume still evicts sightings". The
claim-volume half is deleted rather than qualified — it is false, and the
sentence after it was already the true one. What the ranking does enforce for a
sighting at 50 is stated in its place: it outranks the observer's own transitions
and task attempts (20), the non-contesting walking verdicts derived from it (45)
and the account-uncertainty caveats (15). The eviction route is
`_SALIENCE_REPORTED_TESTIMONY` = 60, and the probe recorded under finding C of
the previous subsection re-runs unchanged at this head: `budget 1500 rows 41
vent 1 p-3 sighting 0 contradicted 9 testimony 30`.

**Finding 3 — the Results ledger was a round behind and read as current.** Its
opening paragraph named five of the branch's twelve commits, said "round-1
findings answered … not re-reviewed" after two completed review rounds, and
pointed a reader at "sections below dated before 2026-09-08" — a discriminator
that selects nothing, because all three review subsections carry that same date.
Nothing in the paragraph was marked as history, so it read as the head's state.
Rewritten: the ledger now runs through this round, grouped by the round each
commit belongs to, and names `9cacd3fc` — the commit the five round-1 findings
and both Codex comments were raised on, which the old ledger omitted entirely;
the delivery state names both completed re-reviews and the commits they ran on
(`bd6f05dc`, three verifiers, no blocking findings; `864b18a1`, three blocking
findings, answered here); and the pointer names all three dated subsections and
says outright that the shared date does not discriminate between them. Checked
against `git log --oneline 201849fc..HEAD`, which lists this commit and the
thirteen before it.

**Codex review.** Both comments re-fetched at `864b18a1`
(`gh api repos/dkdan10/AiLibi/pulls/440/comments`): still exactly two, both with
`original_commit_id` `9cacd3fc`, and the only review on the PR is still the
single `COMMENTED` one on that commit — `00ac7fbb`, `0815333d`, `59df8a9e`,
`86e133e3` and `864b18a1` triggered no new review. GitHub has re-anchored P1's
`commit_id` to `864b18a1` because the manifest line it sits on still exists; its
text is unchanged from what was written against `9cacd3fc`.

- **P1, "Preserve the commit named by the restamp record" — REFUTED again at
  this head, no change.** Re-run here: `git cat-file -t 029aaab` →
  `fatal: Not a valid object name 029aaab`, so the sibling commit Codex describes
  is not an object in this repository; `git rev-parse 7bcc79ed^` → `201849fc`;
  and `git merge-base --is-ancestor <commit> HEAD` exits 0 for each of the three
  commits `dependency_restamps` names (`7bcc79ed`, `56d3e5fd`, `00ac7fbb`). The
  branch is one linear chain. Under the post-#436 delivery policy (merge commit
  or fast-forward, never squash, never amend) all three stay retrievable in main.
- **P2, "Keep the truncation notice through the prompt budget" — VALID on
  `9cacd3fc`, fully addressed.** Its count half and its "assert on
  `render_for_prompt`, not on `evidence_context_lines`" half were repaired by
  `56d3e5fd`; its remaining recommendation, that the notice always ship, was
  declined in round 1 and implemented by `00ac7fbb`. Nothing this round changes
  it, and the committed golden still carries
  `- Account uncertainty: 7 further subjects not shown.` at the production
  budget.

**Nonblocking items left standing.** Every finding routed to this round was
blocking, so this round adds none; whether the verifiers also filed nonblocking
observations is not something this record can speak to. The two
carried from closeout round 1 stand with their reasons: a render of 120-220
tokens on the committed fixture carries no observation block and therefore no
notice, because nothing was selected to reserve it from; and the `audits/`
inventory row is contended with `origin/work/followup-review-dispositions`, so
whichever card merges second must recompute that row from its own tree rather
than take either side. This round touches neither row.

**Verification (closeout round 2).** Every command below was run on both of this
round's commit trees, with exit codes captured directly, never through a pipe,
and reported identical counts on each. `bash scripts/check.sh` — the only gate
here that reads this card, through `validate_task_docs` — was additionally
re-run after every edit to this subsection, the last of them on the bytes this
commit records; the other gates read no Markdown, so a prose edit cannot move
them. Wall time varies by more than a factor of three on this shared machine and
is not part of any claim. Each pytest log was checked for its own `rootdir`
(`.claude/worktrees/wf_be58e68f-39e-8`), because a concurrent session on this
machine shares the scratch directory. `uv sync --frozen` and `npm ci` were run
first in this worktree.

- `.venv/bin/python -m pytest tests/agents/test_memory_rendering.py
  tests/agents/test_evidence_context.py -q` → `163 passed` (139 in the rendering
  module, one more than round 1: the new gate).
- `bash scripts/check.sh` → exit 0. `ruff check` "All checks passed!",
  `ruff format --check` "498 files already formatted", `lint-imports`
  "Contracts: 4 kept, 0 broken", `validate_task_docs` "390 historical phase
  tasks and 390 prompts; 43 work cards", `generate_prompts --check` "All 390
  prompts are in sync", `mypy` "no issues found in 469 source files", pytest
  `7216 passed, 20 skipped, 3 xfailed` (the one added case is the whole
  difference from round 1's 7,215), and the frontend leg: lint,
  `tsc:check`, `19` test files / `514` tests passed, and the production build.
- `bash scripts/verify_samples.sh` → exit 0, "All 50 samples verified clean."
  for `replays/samples/4p1i` and again for `replays/samples/9p2i` (100 canonical
  reconstructions).
- The four derived report checks → exit 0 each, "… is consistent with its
  replays." for `replays/samples/4p1i`, `replays/samples/9p2i`,
  `replays/ml_corpus/4p1i` and `replays/ml_corpus/9p2i`.
- `.venv/bin/python -m pytest tests/orchestrator --collect-only -q` in isolation
  → `583 tests collected`.
- `.venv/bin/python scripts/verify_ml_evidence.py` (offline half) →
  `checks: 60 | OK 48 | FAIL 0 | ABSENT 7 | INFO 5`, "every check passed", exit
  0. The seven absent rows are the evidence-branch bytes a fresh clone lacks;
  `--complete` was not run and is not claimed.

No live provider call of any kind was made in this round: the fake provider is
the only one these paths construct.

**Planted failures (closeout round 2).** The new gate was shown to fail on each
defect it claims to detect, and the seven plants the earlier rounds recorded were
re-run so their counts are current at this head. Every plant was applied to the
source, run, and restored by one script; `git status` is clean of all of them.
Selections: `-k "EvidenceV2Salience or Golden"` except where noted.

A method note that matters for anyone re-running these: a band edit such as
`20` → `90` leaves the file size unchanged, and CPython invalidates a `.pyc` on
`(mtime, size)`, so a same-second rewrite can leave a stale bytecode cache and
make the plant a silent no-op — one such run reported a plant as `23 passed`.
Every count below was taken with `python -B`, `-p no:cacheprovider` and every
`__pycache__/*.pyc` deleted immediately before the run.

1. **The witnessed kill demoted below the vent** (`_SALIENCE_KILL_WITNESSED`
   95 → 80): `1 failed, 22 passed, 116 deselected`, and the one red is
   `test_only_the_body_and_the_witnessed_kill_outrank_the_witnessed_vent` on
   `assert 'You witnessed p-4 kill in MEDBAY.' in tight[1]`, where the vent has
   taken that row. Run against the whole module rather than the selection, the
   same plant gives `1 failed, 138 passed` — no other case anywhere in the
   module covers that band.
2. **The body discovery demoted below the vent** (`_SALIENCE_FOUND_BODY`
   100 → 80): `6 failed, 17 passed, 116 deselected` — the new gate, the
   production-budget gate whose `tight[0]` assertion this breaks, and all four
   goldens, since the body row moves in every arm. The second plant is the wider
   one on purpose: it shows the band was already pinned by the goldens and the
   290-token gate, so only the prose was ever wrong about it.

Re-measured at this head, the seven plants of closeout round 1, in that
subsection's own order — the new gate is the extra red in 3 and 4, the two that
promote a band above the vent, and an extra pass in the other five:

| plant | at `0815333d` | at this head |
| --- | --- | --- |
| 1 the conditional reserve | 4 failed, 18 passed, 116 deselected | 4 failed, 19 passed, 116 deselected |
| 2 the pre-budget count | 3 failed, 19 passed, 116 deselected | 3 failed, 20 passed, 116 deselected |
| 3 the ordering (six constants → 90) | 7 failed, 15 passed, 116 deselected | 8 failed, 15 passed, 116 deselected |
| 4 the demotion (own routine → 90) | 5 failed, 17 passed, 116 deselected | 6 failed, 17 passed, 116 deselected |
| 5 the bound (`-k EvidenceV2Salience`) | 3 failed, 8 passed, 127 deselected | 3 failed, 9 passed, 127 deselected |
| 6 the per-subject collapse (`-k EvidenceV2Salience`) | 1 failed, 10 passed, 127 deselected | 1 failed, 11 passed, 127 deselected |
| 7 the row's own count | 9 failed, 13 passed, 116 deselected | 9 failed, 14 passed, 116 deselected |

Every test each round named as red is still red, and the deselected counts are
unchanged because the added case falls inside both selections.

**Scope this round.** `tests/agents/test_memory_rendering.py` (one added test)
and this card. No production source changed, so the frozen held-out manifest is
untouched and needs no restamp — `git diff 864b18a1 HEAD -- agents docs audits
experiments tests/fixtures` is empty — and neither `docs/artifacts.md` inventory
row moves, because no `audits/` or `tests/fixtures/` byte changed. No fixture, no
new lever, env switch or profile field, no committed recording, report, DTO or
schema byte, and the default path is untouched.

**Limitations this round adds.** None. The two the corrected Outcome now states
in the card's own voice were already recorded here: a sighting at 50 is not
protected against reported testimony at 60, and the three first-hand bands above
the witnessed vent are outside this card's scope and unchanged by it.
