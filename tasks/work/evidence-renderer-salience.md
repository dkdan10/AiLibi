# Rank witnessed evidence above own routine under budget pressure

**Status:** done

## Outcome

Under the production prompt budget a rendered memory keeps the witnessed
evidence a meeting could act on — vent sightings and sightings of other players
— instead of shedding it for the observer's own routine movement and task rows.
Speaker-controlled account-uncertainty text can no longer flood the render.
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
  pre-budget count fails the sweep above at budget 980.
- [x] Review correction: Results claimed the withheld notice reaches the render
  in ordinary play, while the card's own golden carries no such line at 1,500
  tokens. The claim is withdrawn, superseded in place, and replaced by the
  invariant the code enforces — the sentence closes a caveat list the reader can
  see, so a render keeping no caveat carries none — gated by the "a notice
  closing no list" branch of the same sweep.
- [x] Review correction (docs verifier, same sentence): the visibility claim
  named no enforcing mechanism and every notice assertion ran pre-budget against
  `evidence_context_lines`. Both invariants are now asserted on
  `render_for_prompt` output, each with a planted failure recorded in
  "Review corrections, round 1 (2026-09-08)".
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

Implemented on `work/evidence-renderer-salience` from `201849fc`: `7bcc79ed`
(the renderer), `af150ce0` (the held-out restamp), `0c5355a3` (a format fix the
gate asked for), then round 1 of review — `56d3e5fd` (the corrections and their
gates) and `73b7f53f` (the second restamp and the artifacts row). Delivery
state: round-1 findings answered and verified locally; not re-reviewed, not
owner reviewed, not merged. Adoption: not applicable — evidence reasoning v2
stays default-OFF and this repairs a candidate renderer rather than proposing
one. Sections below dated before 2026-09-08 record the first round as it stood;
where a statement there was found false it is marked superseded in place and
corrected in "Review corrections, round 1 (2026-09-08)".

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
   module-level table, because AGENTS forbids module-level mutable state.
2. **Own routine below every sighting.** The observer's route is already
   rendered in full by the unbudgeted `## Where you were:` block, so an
   own-transition row duplicates something the prompt states anyway.
   *Superseded 2026-09-08, review correction 1: that justification is false. The
   route block holds at most `SELF_LOCATION_TRAIL_MAX_SPANS` = 12 spans
   (`store.py:278`) and is charged against the same budget ahead of the
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
   so a subject with more than one distinct placement renders "any of the N
   claimed placements stated for them".
5. **The notice sits one band above the caveats it counts** (16 versus 15), so a
   budget that keeps caveats cannot drop the statement that others were withheld.
   The notice pluralises: `1 further subject not shown`, `3 further subjects not
   shown`.
   *Superseded 2026-09-08, review corrections 2-5: ranking alone left the count
   describing the pre-budget list, so the line could be false. The notice is no
   longer a candidate row at all — `_select_within_budget` mints it after the
   selection and reserves its cost from the first kept caveat. The band is still
   16, which is now only where the minted line is inserted.*
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
the source, running, and restoring.

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
- The negative-verdict band (83) is above the sightings, and negative verdicts
  are not themselves capped. A speaker who states many DIFFERENT impossible
  placements can therefore fill that band. It cannot reach the witnessed vent at
  85, which is what the adverse case pins, but a cap on that class was neither
  required nor added here; if a later measurement shows it matters, it belongs
  with the accounts-channel card that owns the speaking side.
- The account caveat renders subjects in the order their claims were ingested,
  not by any relevance signal, because the caveat carries no evidence to rank by.
- `tests/agents/test_memory_rendering.py` gained one import,
  `orchestrator.boundary.public_map_from_engine_map`, so a fixture can declare a
  canonical public map (`engine.world.load_canonical_map` was already imported
  there). No `agents/` module gained an import and `lint-imports` is green.

### Review corrections, round 1 (2026-09-08)

Three independent verifiers returned five blocking findings on `9cacd3fc`. Every
one reproduces on that commit, none is refuted, and all five are repaired by
`56d3e5fd` (the renderer and its gates) and `73b7f53f` (the held-out restamp and
the artifacts row). Delivery state after this round: corrections applied and
verified locally; the round-1 findings are answered, not re-reviewed, not owner
reviewed, not merged.

**Finding 1 — the demotion rested on a claim the code contradicts.** The comment
at `store.py:108`, the `_build_v2_observations` docstring and Decision 2 all said
the observer's route is "rendered IN FULL and unbudgeted" by
`## Where you were:`. It is neither: `SELF_LOCATION_TRAIL_MAX_SPANS` = 12 caps it
(`store.py:278`, applied at `:575-576`) and `_select_trail_within_budget` charges
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
- The reserve costs the caveat block at most one of its own rows: a budget that
  would have fitted the last caveat spends that room on the sentence saying the
  list is short. It never costs any other class a row.
