# Agent Prompt — 16.17 Baseline 5: the graduation slate, the atomic re-record, the phase close (operator + owner, $0)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-16.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 16.17 — Baseline 5: the graduation slate, the atomic re-record, the phase close (operator + owner, $0), anchored to tasks/phase-15.md 15.7 + 15.23 (the graduate-at-record runbook + the close-gates pattern); the Wave-1 counterfactuals (16.4/16.6/16.8's committed reports — the graduation evidence); eval/vj_instruments.py (16.10 — the before/after instrument); audits/audit-phase-16-baseline-4.md (the BEFORE column, GO path; NO-GO: the baseline-3 measure file per 16.2's rewrite). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-16.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-16-baseline-5-close`
**Depends on:** 16.7.1, 16.8, 16.10, 16.11, 16.16
**Section refs:** tasks/phase-15.md 15.7 + 15.23 (the graduate-at-record runbook + the close-gates pattern); the Wave-1 counterfactuals (16.4/16.6/16.8's committed reports — the graduation evidence); eval/vj_instruments.py (16.10 — the before/after instrument); audits/audit-phase-16-baseline-4.md (the BEFORE column, GO path; NO-GO: the baseline-3 measure file per 16.2's rewrite)
**Complexity:** Integration

The phase's terminal record and its second owner gate. **Preflight — the GRADUATION SLATE (owner
decision):** for each Wave-1 lever — J1 hard-evidence gate (16.4), observation-id rendering
(16.5), J2 citation gate (16.6), the absence prior (16.8) — the owner rules graduate-ON or
stay-OFF, each ruling citing the lever's committed counterfactual against its named canary (J1:
zero hard-backed outcome changes; J2: near-zero honest catches blocked; absence: the boundary
pins + set-size evidence, plus the PR #264-flagged owner question of whether vent sightings
should widen the placement substrate; id-rendering: golden-proven inertness + 16.15's citation
surface needs it ON). A lever that fails its canary stays OFF as a RECORDED decision — with the disable-path
honesty this contract can actually deliver: for levers whose surface is kwarg/lever-gated with no
template presence (J1, the absence prior), stay-OFF is coherent as-is; but for the COUPLED pair
whose elicitation surface 16.15 already landed (the citation gate + observation-id rendering —
the templates now ask for citations the substrate would neither render ids for nor honor), a
stay-OFF ruling CANNOT be absorbed by this task (the template retreat is out of scope and needs
its own version bump), so that outcome PAUSES the close for owner re-planning and the surface
retreat becomes a new contract — a defect the close finds becomes a contract, never a close edit. **Then the 15.7 runbook:** graduate the slate
at the record (resolvers constant-true, registry entries → `_RETIRED_ALWAYS_ON_LEVERS` — C6
discharged, bare reconstruction), re-pin `record_ml_corpus.sh`'s coupled pin block (model + set +
`REQUIRED_PROMPT_VERSIONS`) to the baseline-5 substrate with its stale-corpus comment updated to
name the substrate any future corpus records at (`refresh_samples.sh` needs no edit here — it has
no version literal; HEAD's registry governs, and the MANIFEST provenance check is the proof), record both sets
atomically on the locked model + final prompt versions, Q5 tag, validity gate + the re-anchored
referee + baseline-5 floor pins. **The close reading:** the full before/after on 16.10's
instruments — zero-flag conviction rate (soft/hard split), citation compliance, roll-call
coverage, vouch and grounded-vouch rates, absence-set sizes, whereabouts-lie detections, voice
metrics ALONGSIDE zero-flag (the named NO-GO pairing), conversion under the population-relative
floor, the funnel, canaries under the degraded-Q3 discipline — every number from the committed
CLIs, BEFORE column from the committed measure file. `audits/audit-phase-16-close.md` records
the slate rulings, the uptake findings (elicitation asks vs measured compliance — findings, not
pass bars), re-states the Phase-17 staleness rule (surrogate/corpus/champion are
prior-substrate-anchored; re-ground before any training), and flips this file's banner to CLOSED.

**Files in scope:**
- replays/samples/9p2i/ (the baseline-5 set)
- replays/samples/4p1i/ (the baseline-5 set)
- agents/memory/beliefs.py (resolver graduation region — constants to True per the slate; behind the lever chain)
- meetings/constants.py (citation-gate resolver graduation region)
- agents/memory/store.py (id-rendering resolver graduation region)
- orchestrator/replay.py (registry graduation region — slate entries to retired)
- scripts/record_ml_corpus.sh (the FULL pin block — model + set + versions — re-pinned coherently to the baseline-5 substrate, with the stale-corpus comment updated; its preflight couples the three, so this is the one task that moves them together) + its tests/scripts pin sweep. NOTE: `scripts/refresh_samples.sh` carries NO version literal (only the set-name gate, already flipped by 16.13) — it records whatever HEAD's registry resolves, which at this task IS the 16.15/16.16 versions; the version proof is the recorded MANIFEST provenance check in the DoD, not a script literal
- eval/watchability.py (baseline-5 floors region — behind 16.11/16.14's)
- audits/baseline4-final-measure.json (new: the BEFORE column, captured pre-replacement — GO path naming; 16.2's surgery renames under NO-GO)
- audits/audit-phase-16-close.md (new)
- tasks/phase-16.md (the STATUS banner flip to CLOSED — or to PAUSED on the slate's pause path; the 15.23 precedent)
- README.md (sample-provenance paragraph)
- tests/ (graduation re-pins + the byte-coupled sweep)

**Files NOT in scope:**
- replays/ml_corpus/ (stale; Phase 17 re-grounds — the audit re-states it)
- agents/tactical/learned/ (untouched; its Phase-17 re-grounding is out of scope)
- meetings/manager.py + meetings/transcript.py (no mechanism change at the close — graduation touches resolvers/registry only)

**Definition of done:**
- [ ] The graduation slate is recorded in the close audit BEFORE the record (each lever's ruling + its counterfactual citation + the owner sign-off via PR merge). Stay-OFF is coherent in-scope ONLY for the template-free levers (J1, absence); a stay-OFF ruling on the citation gate or id-rendering AFTER 16.15's asks landed PAUSES the close. **PAUSE-path DoD** (replaces every bullet below except the CI tail): the slate audit section is committed with the pause ruling and its counterfactual evidence, the banner flips to PAUSED naming the re-plan owner-side, NO record is performed, and the surface-retreat successor contract is named — the remaining bullets bind ONLY on the proceed path.
- [ ] [proceed path] The recorded substrate matches the slate exactly (stamped flags = graduated set).
- [ ] Both sets recorded atomically at the final substrate (locked model, 16.15/16.16 versions, slate graduated), Q5 tags, MANIFEST provenance exact; validity gate PASSES with `--expected-model`; BARE byte-verification clean (no `AILIBI_*` export — C6 discharged by graduation).
- [ ] The before/after table regenerates end-to-end from committed artifacts (the BEFORE measure file + the new bytes via the committed CLIs); the named pairing is explicit: voice metrics and zero-flag conviction rate in one table, with the persona-attribution question answered (a zero-flag rise with voice-metric movement and no judgment-lever change = the phase NO-GO, paused for the owner).
- [ ] Canaries on the 50-seed sets per the degraded-Q3 rule (pre-registered bands, two-proportion tests, UNDERPOWERED recorded honestly); a regression pauses the close.
- [ ] Baseline-5 floors pinned; the population-relative conversion floor reported for the new population with its derivation quoted.
- [ ] The close audit records uptake per elicitation ask (roll-call answer rate, citation compliance, vent-tail movement, self-accusation recurrence — findings scoping Phase 17/18), re-states the staleness rule, and flips the banner.
- [ ] The byte-coupled re-pin sweep lands in this PR; `bash scripts/check.sh` green on the final tree.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Sequence the PR like 15.7: slate + graduation commits first (offline-provable), the record next,
the re-pins last. The slate's owner sign-off rides the PR merge (the 15.18 convention) but the
AUDIT text with the rulings must be in the tree before the recording session starts — the operator
records what the slate says, nothing else. Budget ~4–5h; the uptake numbers land wherever they
land (record-only discipline — a weak roll-call answer rate scopes Phase-17/18 prompt work, it
does not reopen 16.15 inside this task).

## Integration risk

This record graduates up to FOUR levers plus two prompt bumps in one substrate — the largest
single-record behavioral delta since 14.12. That is the deliberate design (the offline
counterfactuals + the golden are the proof the risk is priced), but the close audit must
attribute honestly: the before/after table reports against baseline 4 (model held constant, GO
path) so the V&J delta is clean; under NO-GO it reports against baseline 3 with the model
unchanged — either way ONE layer moved per record and the attribution chain from baseline 3 to 5
is unbroken. The one unhedged risk is elicitation uptake at scale (the A/B and fixtures de-risk
mechanism, not model behavior) — hence findings-not-failures, and Phase 17 trains against
whatever this close measures.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.watchability"`
- `uv run python -c "import agents.memory.beliefs"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import agents.memory.episodic"`
- `uv run python -c "import agents.memory.store"`
- `uv run python -c "import orchestrator.personas"`
- `uv run python -c "import eval.vj_instruments"`
- `uv run python -c "import api.schemas"`

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-16-baseline-5-close` with a title like `task 16.17: baseline 5: the graduation slate, the atomic re-record, the phase close (operator + owner, $0)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/phase-15.md 15.7 + 15.23 (the graduate-at-record runbook + the close-gates pattern); the Wave-1 counterfactuals (16.4/16.6/16.8's committed reports — the graduation evidence); eval/vj_instruments.py (16.10 — the before/after instrument); audits/audit-phase-16-baseline-4.md (the BEFORE column, GO path; NO-GO: the baseline-3 measure file per 16.2's rewrite)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
