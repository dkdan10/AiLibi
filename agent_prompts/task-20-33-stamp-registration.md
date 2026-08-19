# Agent Prompt — 20.33 The substrate stamp registration + the recorder preflight: every Phase-20 lever self-describes

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.33 — The substrate stamp registration + the recorder preflight: every Phase-20 lever self-describes, anchored to audits/audit-phase-20-preregistration.md §9 (the freeze is declared at this task's merge; the record slate is "lever slate all eight ON, `impostor_roll_call` OFF") and §6 (partial adoption is per-lever, so each lever must be independently stampable); audits/review-2026-08-19/B/orchestrator.md item 6 + §"Staleness found" (b) (the registry is thirteen always-True constants plus one env read, with stale comments inside its own tests — the review's anchor `tests/orchestrator/test_replay.py:707,728` is CORRECTED at HEAD to :703-704 and :726-727, the "it is the only non-retired lever" comments); audits/review-2026-08-19/B/collated-findings.md C-64 (the accept-and-ignore residue and the 540-line constant-pinning block `tests/orchestrator/test_replay.py:212-750` — swept post-record, not here); audits/review-2026-08-19/D/FINAL-synthesis.md §4 Wave 2 preamble ("Every item lands default-OFF / lever-gated so the committed baseline and all gates stay green until the record") and row 2.0; tasks/phase-18.md 18.11 (the precedent: lever flags registered into the snapshot BEFORE any probe seed records, so a probe/adoption recording self-describes its arms) and 18.12 (the graduation reclassification shape); orchestrator/replay.py:93-117 (`_impostor_roll_call_enabled`, the loader-only mirror and its stated reason), :547-569 (the registry comment block), :570-572 (`_TOGGLEABLE_LEVER_RESOLVERS`), :580-587 (`TOGGLEABLE_SUBSTRATE_FLAG_KEYS` / `SUBSTRATE_FLAG_KEYS`), :590-625 (`substrate_flag_snapshot`); api/replay_loader.py:381-382 (the stale "env-gated; NONE today" comment) and :553-600 (`_assert_substrate_matches`); scripts/refresh_samples.sh:386-388 (the dry-run echo, featherless-only) and :497-534 (the Task-18.12 substrate-lever preflight); scripts/record_ml_corpus.sh:545-652 (`check_replay_provenance`, whose expected slate is a hard-coded bare snapshot at :571) and :788-832 (the mirrored preflight); scripts/check_doc_facts.py:409-521 (`check_lever_registry` — the live registry drives .env.example); .env.example:68-118 (the belief-substrate section); scripts/_manifest_writer.py:102-115 (`_render_flags`); eval/validity.py:862-895 (the gate's tolerant per-lever match). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-stamp-registration`
**Depends on:** 20.21, 20.23, 20.24, 20.25, 20.26, 20.27, 20.28, 20.29, 20.30, 20.31 — the recorder hardening lands first because this task edits the same wrapper and its preflight is only trustworthy once the worker paths beneath it have real coverage; then each of the eight levers must already own its `*_enabled` resolver before this task can bind that resolver into the stamp BY IDENTITY, one edge per lever: the completed-task-from-events fix, the self-location trail, the movement-claim shape, the grounded prosecution, the map-aware arbitration, the structured turn markers, the meeting-outcome memory and the coalesced memory render; and the prompt-set bump must be merged because the pre-registration names THIS merge as the substrate freeze, and a version bump landing after the freeze would falsify it.; also after 20.20 (the architecture note this task corrects is embedded by the exhibit task first)
**Section refs:** audits/audit-phase-20-preregistration.md §9 (the freeze is declared at this task's merge; the record slate is "lever slate all eight ON, `impostor_roll_call` OFF") and §6 (partial adoption is per-lever, so each lever must be independently stampable); audits/review-2026-08-19/B/orchestrator.md item 6 + §"Staleness found" (b) (the registry is thirteen always-True constants plus one env read, with stale comments inside its own tests — the review's anchor `tests/orchestrator/test_replay.py:707,728` is CORRECTED at HEAD to :703-704 and :726-727, the "it is the only non-retired lever" comments); audits/review-2026-08-19/B/collated-findings.md C-64 (the accept-and-ignore residue and the 540-line constant-pinning block `tests/orchestrator/test_replay.py:212-750` — swept post-record, not here); audits/review-2026-08-19/D/FINAL-synthesis.md §4 Wave 2 preamble ("Every item lands default-OFF / lever-gated so the committed baseline and all gates stay green until the record") and row 2.0; tasks/phase-18.md 18.11 (the precedent: lever flags registered into the snapshot BEFORE any probe seed records, so a probe/adoption recording self-describes its arms) and 18.12 (the graduation reclassification shape); orchestrator/replay.py:93-117 (`_impostor_roll_call_enabled`, the loader-only mirror and its stated reason), :547-569 (the registry comment block), :570-572 (`_TOGGLEABLE_LEVER_RESOLVERS`), :580-587 (`TOGGLEABLE_SUBSTRATE_FLAG_KEYS` / `SUBSTRATE_FLAG_KEYS`), :590-625 (`substrate_flag_snapshot`); api/replay_loader.py:381-382 (the stale "env-gated; NONE today" comment) and :553-600 (`_assert_substrate_matches`); scripts/refresh_samples.sh:386-388 (the dry-run echo, featherless-only) and :497-534 (the Task-18.12 substrate-lever preflight); scripts/record_ml_corpus.sh:545-652 (`check_replay_provenance`, whose expected slate is a hard-coded bare snapshot at :571) and :788-832 (the mirrored preflight); scripts/check_doc_facts.py:409-521 (`check_lever_registry` — the live registry drives .env.example); .env.example:68-118 (the belief-substrate section); scripts/_manifest_writer.py:102-115 (`_render_flags`); eval/validity.py:862-895 (the gate's tolerant per-lever match)
**Complexity:** Medium
**Record impact:** none — stamp-side registration only: a bare environment stamps all eight new keys `False`, every committed replay omits them and the missing-key-reads-False rule makes both sides agree, so no rendered byte, no detector output and no MANIFEST cell moves.
**Measurement:** `uv run pytest tests/orchestrator tests/scripts -q` green; `bash scripts/verify_samples.sh` clean at 100/100; `uv run python scripts/check_doc_facts.py` green; `AILIBI_GROUNDED_PROSECUTION=1 uv run python -c 'from orchestrator.replay import substrate_flag_snapshot as s; print(s())'` prints that key `True` with the other seven still `False`; `bash scripts/refresh_samples.sh --seeds 0 --dry-run --expect-levers grounded_prosecution` refuses in a bare shell and passes with the export set, and the same pair holds for `scripts/record_ml_corpus.sh`.

Phase 20 builds eight substrate levers, each shipped default-OFF behind its own `AILIBI_*`
gate so the committed baseline and every gate stay green until the adopting record. None of
them registers itself into the replay substrate stamp: the lever contracts explicitly defer
registration here, exactly as the Phase-18 wave deferred its four meeting-layer flags to the
gate task that recorded with them. Without this task the eight levers are invisible to the
provenance chain — a recording made with the record slate ON would stamp a `game_over`
substrate snapshot identical to a bare baseline-6 recording, the MANIFEST `flags` cell would
claim the old substrate, and `api/replay_loader.py`'s cross-substrate guard would happily
reconstruct baseline-7 bytes under an OFF build. That is precisely the failure the stamp
exists to prevent, and it would be discovered only after a ~23 h operator record.

The registry today is one entry: `orchestrator/replay.py:570-572` binds `impostor_roll_call`
to a LOCAL mirror resolver because importing `agents.strategic.prompts.loader` would execute
its import-time, prompt-set-sensitive Jinja build inside every replay-only consumer
(:93-103 states the reason; a CI equivalence pin at `tests/orchestrator/test_replay.py:573`
stands in for the identity binding). That caveat is loader-specific and does NOT apply to the
eight Phase-20 levers: their homes are `agents/memory/store.py`, `meetings/transcript.py` and
`meetings/manager.py`, and this session verified at HEAD that importing all three under
`AILIBI_PROMPT_SET=garbage_set` pulls in no `agents.strategic` module at all and costs no
import-time env read. So each of the eight binds BY IDENTITY — the strongest form, and the
one the graduated levers kept before they retired — and the stamp cannot drift from the
read-site without a test failing.

The second half is the recorder preflight, and it is not optional housekeeping: both
recorders currently assert the toggleable set is EXACTLY `("impostor_roll_call",)`
(`scripts/refresh_samples.sh:521-522`, `scripts/record_ml_corpus.sh:818-819`), so the moment
eight keys are registered BOTH recorders refuse every run. The fix is the 18.12 preflight
generalized: an explicit `--expect-levers` slate the operator passes, checked positively
against the live snapshot before any seed stages. The hazard is the one
`replays/ml_corpus/README.md` §"the lever slate" already names — a stale export silently
mis-substrates a multi-hour record while the echo claims the ruled slate, and an acceptance
gate run in the same polluted shell passes coherently because it reads the same environment.
With eight toggles instead of one, the blast radius of a half-set export is eight times
wider and a blacklist of variable names is hopeless; only a positive whole-slate assertion
against a stated expectation catches a lever that is missing from the export as readily as
one that should not be there. `check_replay_provenance`
(`scripts/record_ml_corpus.sh:545-652`) needs the same treatment: it currently freezes
`substrate_flag_snapshot(env={})` as the expected slate at :571, which would refuse every
seed of an ON-path record by name.

Two smaller truths ride along. `api/replay_loader.py:381-382` still says a toggleable lever
is "NONE today — the machinery stays for a future lever"; that has been false since the 18.11
registration and becomes badly false with nine live toggles, and the remediation hint it
guards is the first thing an operator reads when a record and a build disagree. And the
`scripts/refresh_samples.sh` dry-run echo that describes the substrate-lever preflight sits
inside the `featherless` branch (:386-388) while the preflight itself is deliberately
provider-independent (:513, outside the provider block) — so an operator previewing an
anthropic or ollama refresh is told nothing about the check that will refuse them.

What this task does NOT do is graduate anything. Every key lands as a DEFAULT-OFF toggle;
`substrate_flag_snapshot()` in a bare environment must equal the committed baseline-6 stamp
with eight `False` entries appended, `_render_flags` never emits an OFF key so regenerating
the committed MANIFESTs is a no-op, and `eval/validity.py`'s tolerant per-lever match reads
the absent keys as `False` on both sides. The retirement sweep — folding adopted keys into
`_RETIRED_ALWAYS_ON_LEVERS`, deleting their gates, and clearing the accept-and-ignore residue
the review logged as C-64 — belongs to the adopting record and the post-record graduation
sweep, not here.

**Files in scope:**
- orchestrator/replay.py; (the eight Phase-20 levers registered in `_TOGGLEABLE_LEVER_RESOLVERS` bound to their home-module resolvers by identity; SUBSTRATE_FLAG_KEYS ordering documented; one shared slate-comparison helper)
- tests/orchestrator/test_replay.py; (the snapshot stamps all eight False in a bare env and True under their exports; identity binding per lever; the mismatch guard refuses a stamped-OFF replay under an ON environment; the two stale registry comments corrected)
- scripts/refresh_samples.sh; (the preflight asserts the slate equals an explicit expected list passed by flag; refuses otherwise; the dry-run echo describes it for every provider)
- tests/scripts/test_refresh_samples.py
- scripts/record_ml_corpus.sh; (the same preflight, plus `check_replay_provenance` judging recorded stamps against the same expected slate)
- tests/scripts/test_record_ml_corpus.py
- .env.example; (the eight levers documented as default-OFF Phase-20 toggles, with their record fate)
- tests/scripts/test_manifest_writer.py; (the flags column carries the new keys)
- api/replay_loader.py; (the substrate-mismatch remediation comment stops claiming no toggleable lever exists; the hint text itself already enumerates keys dynamically)
- tests/experiments/test_probe_backends.py; (the hard-coded _FLAGS_ON slate gains the eight keys)
- docs/architecture.md; (the toggle-count sentence only)

**Files NOT in scope:**
- every lever's home module (the resolvers already exist; this task imports and binds them, and changes no lever behaviour)
- replays/ and replays/*/MANIFEST.md (committed stamps lack the new keys; the missing-key-reads-False rule makes both sides agree, and `_render_flags` never emits an OFF key — pinned unchanged, not edited)
- agents/strategic/prompts/ and every `.j2` template (the single prompt-set bump owns the template surface; no task after it may touch a template)
- orchestrator/replay.py's `_RETIRED_ALWAYS_ON_LEVERS` (no graduation happens here — the adopting record moves keys across, and the post-record sweep deletes the residue)
- eval/validity.py (its per-lever match already tolerates an absent key; evidence, not an edit target)
- scripts/check_doc_facts.py (it derives everything from the live registry, so .env.example alone must make it pass; if it needs a code change, that is a finding to report, not a silent edit)
- scripts/_manifest_writer.py (`_render_flags` is read as evidence that OFF keys never reach a cell)

**Definition of done:**
- [ ] All eight Phase-20 lever keys — `task_completion_from_events`, `self_location_trail`, `movement_claim_shape`, `grounded_prosecution`, `map_aware_arbitration`, `structured_turn_markers`, `meeting_outcome_memory`, `coalesced_memory_render` — are entries in `_TOGGLEABLE_LEVER_RESOLVERS`, each bound BY IDENTITY to its home-module resolver; `tests/orchestrator/test_replay.py` asserts `dict(_TOGGLEABLE_LEVER_RESOLVERS)[key] is <home_module>.<key>_enabled` for every one of the eight, and pins `SUBSTRATE_FLAG_KEYS` in its documented order with the rationale for that order stated in one line beside the table.
- [ ] `substrate_flag_snapshot({})` equals the committed baseline-6 stamp plus the eight new keys at `False`, and `substrate_flag_snapshot({"AILIBI_<KEY>": "1"})` flips exactly that one key and no other — both pinned in `tests/orchestrator/test_replay.py`, replacing the hard-coded stamp dict at :498-513 rather than sitting beside it.
- [ ] `bash scripts/verify_samples.sh` stays 100/100 and regenerating the four committed MANIFESTs leaves every `flags` cell byte-identical (the missing-key-reads-False rule plus `_render_flags` emitting only ON keys) — the PR quotes both.
- [ ] `_assert_substrate_matches` refuses a replay whose stamp records a new key `False` when that key's `AILIBI_*` export is live, and the raised `ReplaySubstrateMismatchError` lists the offending key under the TOGGLEABLE remediation hint (not the retired one) — pinned in `tests/orchestrator/test_replay.py`; the stale `api/replay_loader.py:381-382` comment now states the true live-toggle count.
- [ ] `scripts/refresh_samples.sh` accepts `--expect-levers <comma list>` naming the toggleable keys expected ON (absent or empty = the bare slate, today's behaviour), positively checks the live snapshot against it before any seed stages, and refuses with a diagnostic naming every deviating key in BOTH directions — an expected-ON key that is OFF and an unexpected export that is ON; `tests/scripts/test_refresh_samples.py` pins accept and refuse for each direction, and pins that the dry-run echo describes the expected slate for anthropic, ollama and featherless alike.
- [ ] `scripts/record_ml_corpus.sh` mirrors the flag and the refusal (`tests/scripts/test_record_ml_corpus.py` pins both directions), AND `check_replay_provenance` judges each recorded `game_over` stamp against the SAME expected slate instead of the hard-coded `substrate_flag_snapshot(env={})` at :571 — so an ON-path record is accepted by its own recorder while a stale baseline-6 replay dropped into an ON-slate set is still refused by name (pinned both ways).
- [ ] `.env.example` documents the eight toggles inside the `# Belief-substrate levers` section — one commented `# AILIBI_<KEY>=0` example line per key showing the bare-environment default, each with a one-sentence description of what turning it on changes and the explicit statement that the Phase-20 adopting record graduates whichever of them the decision rule adopts — and `uv run python scripts/check_doc_facts.py` passes with no change to the checker.
- [ ] `tests/scripts/test_manifest_writer.py` pins that a replay stamped with one Phase-20 lever ON renders that key in the MANIFEST `flags` cell (the same round-trip the `evidence_quality_lift` test at :168-192 pins), and that an all-OFF stamp still renders the unchanged baseline-6 cell.
- [ ] The two stale comments at `tests/orchestrator/test_replay.py:703-704` and :726-727 ("Task 16.8's live default-OFF absence_prior … it is the only non-retired lever") state the truth; no comment in the touched files claims a single live toggle.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — the registration. Follow the comment block above `_TOGGLEABLE_LEVER_RESOLVERS`
(orchestrator/replay.py:547-569): it is the registry's documentation and it must come out of
this task describing nine live toggles, not one. The 18.10 mirror caveat at :93-103 applies
ONLY to the loader-side lever; the eight Phase-20 resolvers live in `agents.memory.store`
(`task_completion_from_events_enabled`, `self_location_trail_enabled`,
`meeting_outcome_memory_enabled`, `coalesced_memory_render_enabled`), `meetings.transcript`
(`movement_claim_shape_enabled`, `grounded_prosecution_enabled`,
`map_aware_arbitration_enabled`) and `meetings.manager` (`structured_turn_markers_enabled`),
and this session verified at HEAD that importing all three modules pulls in zero
`agents.strategic` modules even under `AILIBI_PROMPT_SET=garbage_set` — so import them at
module scope and bind the real functions. Re-run that check yourself before you rely on it
(`AILIBI_PROMPT_SET=garbage_set uv run python -c "import orchestrator.replay"`), because the
existing `test_replay_module_imports_under_a_garbage_prompt_set` pin is what protects every
replay-only consumer. Registration order: append the eight AFTER `impostor_roll_call`, in
wave order (completed-task, trail, movement shape, grounded prosecution, map arbitration,
turn markers, meeting memory, coalesced render), and say in one line why — the tuple is
`Final` and never mutated at runtime, so the order is documentary and the stable choice is
"registration order, newest last", which keeps every prior key's index unchanged and makes
the diff to the pinned `SUBSTRATE_FLAG_KEYS` a pure append.

Step 2 — the shared slate helper. Both recorders inline the same `uv run python -c` snippet
today and both would need the same eight-key edit; give them one home instead. A function
taking the keys expected ON and returning a list of human-readable mismatch strings (empty
when the slate matches) lets the shells stay three lines and lets pytest cover the logic
directly rather than only through a subprocess. Keep the three failure classes the existing
snippets already distinguish: a retired lever reading `False` (a partial graduation), a
toggleable lever whose live state differs from the expectation, and an unknown key in the
expectation itself (a typo in the operator's `--expect-levers` list must fail loud, never be
silently ignored — that is the whole point of a positive check).

Step 3 — the shells. Add `--expect-levers` to the argument loops
(scripts/refresh_samples.sh:173-199, scripts/record_ml_corpus.sh:206-220) and to both usage
blocks. Default it to the empty slate so every existing invocation and every existing test
keeps its meaning. Move the `[dry-run] substrate-lever preflight` echo in refresh_samples out
of the `featherless` branch at :386-388 so it prints for every provider, matching where the
real check runs (:513, outside the provider block), and make both echoes quote the resolved
expected slate rather than a hard-coded baseline-6 sentence. In `check_replay_provenance`,
replace the frozen `slate = substrate_flag_snapshot(env={})` at :571 with the expected slate
threaded in from the same flag; keep the tolerant per-lever match exactly as it is (present
and True for always-on, boolean equality otherwise, unknown key = foreign stamp) so a stale
baseline-6 replay is still refused by name.

Step 4 — the docs surface. `scripts/check_doc_facts.py::check_lever_registry` derives
everything from the live registry, so .env.example is the only file that must move: for each
new key it requires the variable to appear inside the `# Belief-substrate levers` section AND
a commented line matching exactly `# AILIBI_<KEY>=0` (the bare default), and it rejects any
uncommented assignment anywhere in the file. Put the eight in a new block AFTER the blank line
that ends the `# GRADUATED LEVERS` note — the graduated note is parsed as the contiguous
comment block up to the first blank line and it rejects any "default-off" wording inside
itself, so the new default-OFF prose must live outside it, beside the existing
`AILIBI_IMPOSTOR_ROLL_CALL` block. Do not edit the checker.

Step 5 — blast radius before you widen scope. `grep -rn "impostor_roll_call" --include="*.py"
--include="*.sh"` finds every place that assumes one live toggle. Inside scope you will hit
the two shells, `tests/orchestrator/test_replay.py` (the hard-coded stamp dict at :498-513,
the registration pin at :386-420, the stale comments at :703-704 and :726-727) and the
manifest test. Outside scope you will hit `tests/experiments/test_probe_backends.py` and two
prose files — report those in the PR's Decisions rather than editing them.

## Public types this task introduces
- `orchestrator.replay.substrate_slate_mismatches`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import check_doc_facts"`
- `uv run python -c "import eval.leak_scan"`
- `uv run python -c "import meetings.render_contract"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import agents.memory.store"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import eval.evidence_honesty"`
- `uv run python -c "import eval.solvability"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import api.schemas"`

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-20-stamp-registration` with a title like `task 20.33: the substrate stamp registration + the recorder preflight: every phase-20 lever self-describes`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-20-preregistration.md §9 (the freeze is declared at this task's merge; the record slate is "lever slate all eight ON, `impostor_roll_call` OFF") and §6 (partial adoption is per-lever, so each lever must be independently stampable); audits/review-2026-08-19/B/orchestrator.md item 6 + §"Staleness found" (b) (the registry is thirteen always-True constants plus one env read, with stale comments inside its own tests — the review's anchor `tests/orchestrator/test_replay.py:707,728` is CORRECTED at HEAD to :703-704 and :726-727, the "it is the only non-retired lever" comments); audits/review-2026-08-19/B/collated-findings.md C-64 (the accept-and-ignore residue and the 540-line constant-pinning block `tests/orchestrator/test_replay.py:212-750` — swept post-record, not here); audits/review-2026-08-19/D/FINAL-synthesis.md §4 Wave 2 preamble ("Every item lands default-OFF / lever-gated so the committed baseline and all gates stay green until the record") and row 2.0; tasks/phase-18.md 18.11 (the precedent: lever flags registered into the snapshot BEFORE any probe seed records, so a probe/adoption recording self-describes its arms) and 18.12 (the graduation reclassification shape); orchestrator/replay.py:93-117 (`_impostor_roll_call_enabled`, the loader-only mirror and its stated reason), :547-569 (the registry comment block), :570-572 (`_TOGGLEABLE_LEVER_RESOLVERS`), :580-587 (`TOGGLEABLE_SUBSTRATE_FLAG_KEYS` / `SUBSTRATE_FLAG_KEYS`), :590-625 (`substrate_flag_snapshot`); api/replay_loader.py:381-382 (the stale "env-gated; NONE today" comment) and :553-600 (`_assert_substrate_matches`); scripts/refresh_samples.sh:386-388 (the dry-run echo, featherless-only) and :497-534 (the Task-18.12 substrate-lever preflight); scripts/record_ml_corpus.sh:545-652 (`check_replay_provenance`, whose expected slate is a hard-coded bare snapshot at :571) and :788-832 (the mirrored preflight); scripts/check_doc_facts.py:409-521 (`check_lever_registry` — the live registry drives .env.example); .env.example:68-118 (the belief-substrate section); scripts/_manifest_writer.py:102-115 (`_render_flags`); eval/validity.py:862-895 (the gate's tolerant per-lever match)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
