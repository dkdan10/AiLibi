# Phase 9 — Producer hygiene + canonical-model migration (Wave 0)

Goal: establish a clean control baseline on the new canonical model before any conversion work.
Wave 0 lands the model-independent producer/bookkeeping fixes from the two gameplay audits
(audit-2026-06-06-0632 + audit-2026-06-07-0717) and migrates the canonical eval provider from
`qwen2.5:7b-instruct` to **`qwen3.5:9b` with thinking disabled**, converging on ONE combined
re-record of both committed sets. **The phase PAUSES there.**

Why migration-first (owner decision 2026-06-07): the Wave-1 conversion problem statement is
substantially a qwen2.5:7b deficiency catalogue (19/19 inverted §4.6 threshold readings, 0.55
confidence-parking, prompt-example id copying, 54% own-accusation abandonment). Repairs are not
designed against a substrate that is about to be replaced; substrate changes land before behavior
waves. The hygiene fixes below are model-independent and land BEFORE the migration re-record so the
new baseline is not polluted by known producer defects.

Locked decisions (2026-06-07):
- Canonical model: `qwen3.5:9b`, `think: false` in every Ollama API payload (supported natively),
  fail-loud if a response carries populated thinking. The flat 4p/1i + canonical 9p/2i two-set
  structure is unchanged.
- The conversion core (§4.6 verdict rendering, tally-bar/abstain redesign, pass gates — parked
  worksheet Q1–Q3) is NOT in Wave 0. It is re-answered against the post-migration baseline's
  data and authored as Wave 1 (tasks 9.6+) only after the post-migration close audit.
- Impostor build frozen EXCEPT the two firewall-class hygiene items below (9.2 producer bug,
  9.3 input-side team firewall — correctness, not capability). Balance knobs, emergency-button
  scope, and discovery/patrol behavior are all frozen; measurement only.
- Old control (9p2i @ ef30b29, qwen2.5:7b) retires when 9.5 merges; cross-model comparisons must
  name sample dir + commit + model.

Parallelism: 9.1, 9.2, 9.3, 9.4 are independent roots and dispatch in parallel (disjoint file
scopes). 9.5 is the operator-run gate after all four. Track with
`python3 scripts/compute_next_task.py --phase 9`.

### Task 9.1 — kill_gifted definition fix + offline report regeneration
**Branch:** `phase-9-kill-gifted-definition`
**Depends on:** none (hygiene root)
**Section refs:** DESIGN.md §3.5; audits/audit-2026-06-07-0717-gameplay-data.md gp-4 (finding A-A-2)
**Complexity:** Small

The committed report undercounts kill-gifted wins (8/46 vs true 11/46): the current flag requires
that NO task instance completed on the final tick, so a same-tick completion by another player
masks a genuine gift (seed 11 tick 20: victim p-6 killed holding upload_logs 4/6 while p-5
completes a different instance the same tick — the win fires on the drop, wrongly excluded).
Re-anchor the definition to the victim: kill-gifted iff the winner is CREWMATES by tasks AND the
final tick resolves a kill whose victim held at least one incomplete instance at kill resolution.
Regenerate both committed reports offline (same bytes, corrected derivation — no re-record).

**Files in scope:**
- eval/balance_eval.py (`_kill_gift_accounting` — the definition swap; aggregates unchanged in shape)
- replays/samples/tournament-eval-report.json + replays/samples/9p2i/tournament-eval-report.json (regenerated OFFLINE from the committed bytes via the build_sample_report path)
- tests/eval/test_balance_eval.py + tests/eval/test_report_schema.py + tests/eval/test_tournament_report.py (the masked-gift fixture: same-tick completion by another player still flags; any `kill_gifted_wins` pin updates — 9p/2i becomes 11)
- tests/api/test_eval.py (only if it pins a kill_gifted aggregate; otherwise untouched)

**Files NOT in scope:**
- eval/report_schema.py field shapes (fields exist from 8.17; values change, schema does not)
- replays/samples/**/*.jsonl + MANIFEST.md (bytes untouched; offline regen only)
- engine/ (the §3.5 drop semantics are unchanged)

**Definition of done:**
- [ ] `kill_gifted` is true iff winner is CREWMATES by tasks AND the final tick resolves a kill whose victim held ≥1 incomplete instance at kill resolution; a same-tick completion by another player does not mask it; derivation stays engine-walk-based (resolved events, not raw action rows).
- [ ] Both committed reports are regenerated offline and `build_sample_report --check` is consistent; the 9p/2i `kill_gifted_wins` reads 11; replay bytes and MANIFESTs are untouched.
- [ ] A regression fixture covers the masked-gift case (kill + unrelated same-tick completion) and the non-gift case (victim held no incomplete instances).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The helper already walks resolved events; the change is the predicate, not the plumbing. The
victim's instance state must be read at kill RESOLUTION (before the §3.5 drop executes), so take it
from the pre-drop state the walk already has in hand. Verify against the audit's repro pair:
seed 11 tick 20 flags, seed 40 tick 22 stays excluded.

**Integration risk:**

Offline regeneration of committed reports is legitimate ONLY because the bytes are unchanged —
do not touch replays or MANIFESTs, or the provenance chain breaks. 9.5 regenerates everything
again on the new model; this task exists so the pre-migration bookkeeping is correct.

**Ready-to-paste prompt:** `agent_prompts/task-9-1-kill-gifted-definition.md`

### Task 9.2 — Impostor kill-intent room validation
**Branch:** `phase-9-kill-intent-room`
**Depends on:** none (hygiene root)
**Section refs:** DESIGN.md §3.4; audits/audit-2026-06-07-0717-gameplay-data.md gp-5 (findings MECH-B-1, A-A-3)
**Complexity:** Small

25 of 164 recorded kill attempts (15%, across 19/50 seeds) were engine-rejected "kill requires same
room": the tactical policy ranks `saw_player` sightings from ANY tick, so it emits KillIntent
against targets that already left (or dodge by id-order move resolution). A wasted kill attempt is
a wasted impostor tick and a confound on impostor-side reads. Validate the candidate against the
actor's CURRENT room at intent time.

**Files in scope:**
- agents/tactical/impostor_policy.py (the kill branch: emit KillIntent only when the chosen target is co-located with the actor THIS tick — re-validate the sighting against current-tick visibility before queuing; stale sightings remain valid for stalking/navigation, only the kill emission tightens)
- tests/agents/test_impostor_policy.py (a stale-sighting case: target seen earlier in another room → no KillIntent; a co-located case still kills; the teammate-exclusion cases stay green)

**Files NOT in scope:**
- engine/ (the same-room rule and id-order resolution are canon — DESIGN.md §3.4; the engine guard stays the backstop)
- agents/strategic/** (no prompt or reasoner change — the impostor build freeze holds)
- replays/samples/** (re-record is 9.5)

**Definition of done:**
- [ ] KillIntent is emitted only for a target whose current-tick observation places it in the actor's room; the stale-sighting regression test passes; no change to stalk/navigation scoring.
- [ ] The DESIGN.md §3.4 id-order canon is referenced in the kill-branch comment (the engine remains the enforcement; this is producer-side waste removal).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The policy's docstring documents the scoring model (isolation × witness × cooldown over saw_player
sightings); the fix belongs at the EMISSION seam, not the scoring — current-tick co-location is
already derivable from the freshest observation packet the policy holds. Audit repro: seed 0 tick 4
(p-6 kills p-4, the queued move dodges), seed 14 ticks 16/19 identical dodges.

**Integration risk:**

Behavior-only producer change: committed-byte reconstruction is unaffected (replays re-run recorded
actions). Expect the post-9.5 baseline to show a real kill-cadence uptick — that is the defect
disappearing, not a balance knob.

**Ready-to-paste prompt:** `agent_prompts/task-9-2-kill-intent-room.md`

### Task 9.3 — Teammate-perception firewall (input side)
**Branch:** `phase-9-teammate-perception-firewall`
**Depends on:** none (hygiene root)
**Section refs:** DESIGN.md §1.3, §4.7; audits/audit-2026-06-06-0632-gameplay-data.md gp-7; audits/audit-2026-06-07-0717-gameplay-data.md gp-8 item 6
**Complexity:** Medium

The 7.12 firewall guards the meeting OUTPUT side (no impostor accuses/votes a teammate), but the
INPUT side still manufactures evidence against the team: a witnessed teammate kill generates
suspicion of the teammate in the witness's own belief graph, teammate-incriminating sightings flow
into the impostor's meeting inputs (seed 47: impostor p-9's opt-in placed teammate p-1 at the kill
room/tick, generating both alibi_vs_sighting contradiction flags), and self-subject sighting rows
render into a player's own prompt as third-person garble. Once conversion works, these own-goals
corrupt the crew-intel read. Implement DESIGN.md §4.7's team-internal guard.

**Files in scope:**
- agents/perception.py (the impostor's own-witness path: a `saw_player` co-located with a kill it knows is a teammate's generates no teammate-suspicion belief; `fellow_impostor_ids` already rides the privileged self channel)
- agents/memory/store.py (`render_for_prompt` / `_render_saw_player`: suppress self-subject sighting rows in a player's own rendered memory; drop teammate-incriminating kill-window sightings from an IMPOSTOR's rendered meeting inputs)
- meetings/manager.py (`_suspicion_graph_with_contradictions`: deterministic backstop — an impostor voter's graph carries no edge against a fellow impostor; mirrors the existing 7.12 coercion precedent)
- tests/agents/test_perception.py + tests/agents/test_memory_rendering.py + tests/agents/test_beliefs.py + tests/meetings/test_manager.py (the seed-47-shaped case: teammate kill witnessed → no self-team suspicion, no teammate-incriminating render row, graph edge masked; crew behavior unchanged; the §1.3 observation firewall suite stays green)

**Files NOT in scope:**
- agents/strategic/prompts/** (NO prompt edits — the teammate-alibi consistency instruction is deferred to the conversion wave; the impostor build freeze holds)
- observation/service.py (the packet already carries what is needed; no schema change)
- meetings/voting.py, replays/samples/**

**Definition of done:**
- [ ] An impostor witnessing a teammate's kill generates no suspicion of the teammate in its own belief state; teammate-incriminating kill-window `saw_player` rows do not render into the impostor's meeting inputs; self-subject sighting rows never render into any player's own prompt.
- [ ] `_suspicion_graph_with_contradictions` masks fellow-impostor edges for impostor voters (deterministic backstop, 7.12-style). Auditable invariant, pinned: the recorded contradiction set of any game contains NO alibi_vs_sighting entry whose supporting sighting is an impostor's own observation of a fellow impostor (the seed-47 class) — assert it in tests; downstream audits verify it from recorded contradictions + re-derived roles (input-side masking leaves no recorded marker text, so the invariant IS the gateable surface).
- [ ] Crew perception/render behavior is byte-identical for non-impostors, regression-tested in this pinned shape: the existing memory-render goldens pass UNCHANGED for crewmate fixtures (no golden regeneration), plus a synthetic role-flip test — one 9p/2i-shaped fixture rendered twice, as CREWMATE and as IMPOSTOR-with-fellow-ids — asserting the renders are identical except for the teammate-guard suppressions. The observation-firewall and leak suites pass unchanged.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Three small guards, one per layer, all keyed off `fellow_impostor_ids` on the privileged self
channel (the reasoner's leak-guard at agents/strategic/reasoner.py shows the role-gating
precedent — non-impostors must never observe these code paths firing). The graph mask in
meetings/manager.py is the cheapest and most load-bearing: even if a sighting slips through
memory, the voter-side graph carries no team edge. Keep each guard independently tested so the
defense-in-depth claim is real.

**Integration risk:**

Touches the perception/belief path shared by all roles — the non-impostor byte-identity regression
is the contract's hard line. Recording-side only; committed reconstruction unaffected.

**Ready-to-paste prompt:** `agent_prompts/task-9-3-teammate-perception-firewall.md`

### Task 9.4 — qwen3.5:9b client compat (think:false, fail-loud)
**Branch:** `phase-9-qwen35-client`
**Depends on:** none (migration-prep root)
**Section refs:** DESIGN.md §11.4 (recording provenance); owner decision 2026-06-07 (canonical model qwen2.5:7b-instruct → qwen3.5:9b, thinking disabled)
**Complexity:** Medium

Migrate the canonical local provider to `qwen3.5:9b`. Qwen3.5 thinks by default; Ollama supports
disabling per request (`"think": false` in the API payload). The client must send it on every sim
call and FAIL LOUD if a response nonetheless carries populated thinking content (a silently
half-thinking run would record at multiplied latency with un-audited reasoning text). Update the
default-model constants and revalidate the parse-tolerance layer against the new chat template.

**Files in scope:**
- llm/ollama_client.py (`DEFAULT_OLLAMA_MODEL` → `"qwen3.5:9b"`; `think: false` in every request payload; the fail-loud guard: a response with non-empty thinking raises, mirroring the no-silent-fallbacks rule; docstring model references)
- llm/provider.py (the qwen2.5 docstring references; no behavior change beyond what the client carries)
- scripts/refresh_samples.sh (`DEFAULT_OLLAMA_MODEL` literal → `qwen3.5:9b`; the preflight pulls/validates the new model name)
- tests/llm/ (unit: payload carries think:false, the thinking-populated fail-loud case, model-constant pins; the skip-gated real-provider round-trips re-pointed at qwen3.5:9b — they run in 9.5's operator session, not CI)
- AGENT_IMPLEMENTATION.md + README.md (the canonical-model one-liners — swept here; this wave has no separate docs task)

**Files NOT in scope:**
- agents/**, meetings/** (prompts and protocol are model-agnostic; no prompt-version bump — the templates are unchanged)
- replays/samples/** + MANIFESTs (the model row changes only when 9.5 re-records; provenance rides the recorded git_sha)
- `_ollama_num_ctx_from_env` default (keep 8192; 9.5's smoke watches for truncation before any change)

**Definition of done:**
- [ ] Every Ollama request carries `think: false`; a response with populated thinking raises a descriptive error (fail-loud, no silent strip); `DEFAULT_OLLAMA_MODEL == "qwen3.5:9b"` in both the client and refresh_samples.sh.
- [ ] The parse-tolerance suites (the 7.6/8.9 lineage in tests/llm/) pass against the new template assumptions; the env-gated real-provider tests are re-pointed and documented as 9.5-operator-verified.
- [ ] No prompt template, prompt version, or meeting-protocol change.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The payload assembly already sets `options` (num_ctx, seed) — `think` is a TOP-LEVEL request field
in the Ollama API, not an options entry; place it accordingly. The fail-loud guard checks the
response's thinking field (Ollama surfaces it separately when enabled) — assert absent-or-empty.
CLI spot-check for the operator: `ollama run qwen3.5:9b --think=false`. Mock-based tests carry CI;
the real round-trip is 9.5's smoke. Before declaring done, grep `qwen2.5:7b` across the WHOLE repo
and sweep every stale reference in source, docs, and test pins — with one deliberate carve-out:
committed provenance (replays/samples/** MANIFEST model rows, replay JSONL llm_calls, the committed
tournament reports, and the tests/scripts pins that assert those committed rows) correctly keeps
the old model string until 9.5 re-records; that is provenance, not staleness. Leave those for 9.5.

**Integration risk:**

If the installed Ollama version predates the `think` parameter, the guard is what stops a silent
thinking run — the 9.5 smoke surfaces it immediately. No committed bytes change here.

**Ready-to-paste prompt:** `agent_prompts/task-9-4-qwen35-client.md`

### Task 9.5 — Migration re-record of BOTH sets on qwen3.5:9b + gate (PHASE PAUSES AFTER)
**Branch:** `phase-9-model-migration-rerecord`
**Depends on:** 9.1, 9.2, 9.3, 9.4
**Section refs:** DESIGN.md §11.4, §3.5; audits/audit-2026-06-07-0717-gameplay-data.md (the migration + hygiene set)
**Complexity:** Integration

The Wave-0 gate, mirroring 8.18's operator shape: with the three hygiene fixes and the client
migration merged, smoke first, then re-record BOTH committed sets on `qwen3.5:9b` (think:false) in
ONE PR, regenerate both reports + MANIFESTs + the prompt-regression fixtures and baseline, and run
the validity gate. This establishes the NEW control baseline. The phase pauses at this merge: the
close audit and the conversion-wave worksheet re-answer happen in the design thread before any 9.6+
contract exists.

**Files in scope:**
- replays/samples/*.jsonl + tournament-eval-report.json + MANIFEST.md (flat 4p/1i re-recorded on qwen3.5:9b; model rows update)
- replays/samples/9p2i/ (50 replays + report + MANIFEST re-recorded; roster {9,2,2} unchanged)
- tests/fixtures/prompt_regression/{v_a,v_b}/*.jsonl + baseline.json (regenerated — the model changed, so the recorded fixtures must)
- tests/api/test_replay_loader.py + tests/eval/test_win_condition_selfcheck.py (committed-set pins re-verified on the new bytes; re-scope any zero-denominator runtime skips exactly as 8.18 did)
- tests/scripts/test_build_sample_report.py + tests/scripts/test_verify_samples.py + tests/scripts/test_manifest_writer.py + tests/scripts/test_refresh_samples.py (committed-bytes pins: git_sha, model rows `qwen3.5:9b`, cost 0)

**Files NOT in scope:**
- engine/, meetings/, agents/, llm/, eval/ source (all behavior landed in 9.1–9.4; this task records + regenerates)
- audits/workflows/extract_gameplay_facts.py (run read-only for the funnel numbers; do not modify)

**Definition of done:**
- [ ] Smoke first (3–5 seeds at 9p/2i): the think:false guard holds on live calls (zero thinking content), per-seed wall time measured and the full-run projection reported BEFORE the full runs; STOP for operator go. If the smoke surfaces ANY thinking-guard trip (Ollama version predates the `think` parameter, or the flag is not honored), ABANDON this task without recording further: re-open 9.4 (or escalate the Ollama-version/model question to the design thread) — do not proceed to a full record, and do not weaken the guard.
- [ ] Both sets re-recorded in ONE PR on `qwen3.5:9b`; both reports regenerated (format v2; kill_gifted under the 9.1 definition); both MANIFESTs carry the new git_sha + `qwen3.5:9b` model rows; prompt-regression fixtures + baseline regenerated.
- [ ] Validity gate (HARD, the v3 set): friendly-fire 0; every game reaches game_over; betrayal ballots/accusations 0 — now structurally absent at the source per 9.3; leak suite green at 4p/1i and 2-of-9; meeting_rate ≥ 0.60 with ≥ 30 resolved meetings at 9p/2i; byte-identical reconstruction; zero tick-1 kills; zero missed-deadline markers; zero dangling primary_reason_id; PLUS migration assertions: zero thinking-guard trips, zero cross-room kill rejections (the 9.2 fix holding), model rows correct.
- [ ] Funnel report ($0): run audits/workflows/extract_gameplay_facts.py over the new 9p/2i set; PR body reports win split + kill-gifted split (9.1 definition), ejection count, accusation precision, accuser follow-through, persuasion rate, and the threshold-quoting-skip count (the 19/19 inversion class — the migration's headline question). The extractor does NOT compute the threshold-quoting count: derive it operator-inline (a regex over ballot `rationale_text` in the raw replay meeting records — the facts JSON does not carry rationales), and paste the derivation snippet into the PR body so the next migration reuses it instead of rediscovering the gap. Reported, not gated.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Operator-run local session: `ollama pull qwen3.5:9b` first; AILIBI_LLM_PROVIDER=ollama on every
refresh invocation (still defaults to anthropic); the model name now comes from 9.4's constant —
no model env needed. Expect roughly 2× per-token cost vs the 7B — the smoke's projection decides
whether the full run is an evening or a day. Win split is reported only and may move in ANY
direction (9.2 raises real kill cadence; the model change moves everything else) — the
threshold-inversion count is the number that decides what Wave 1 still needs to fix. One atomic
PR; an intermediate commit is un-reconstructable.

**Integration risk:**

The wave converges here and the phase PAUSES at this merge — do not author, dispatch, or implement
any conversion-wave work in this task. If the thinking guard trips or the floor fails, STOP and fix
upstream (9.4 or the model choice) rather than papering the gate.

**Ready-to-paste prompt:** `agent_prompts/task-9-5-model-migration-rerecord.md`

## Merge Criteria (Phase 9 Wave 0 — hygiene + model migration)
- **Bookkeeping correct (9.1):** kill_gifted re-anchored to the victim's incomplete instances (9p/2i reads 11/46 on the old bytes); committed reports regenerated offline; bytes + MANIFESTs untouched.
- **Producer waste removed (9.2):** zero cross-room kill-intent rejections in the post-migration set; stalk/navigation behavior unchanged.
- **Team firewall complete (9.3):** the 7.12 output firewall is mirrored on the input side — no self-team suspicion edges, no teammate-incriminating renders, no self-subject rows; crew behavior byte-identical; leak suites green.
- **Model migrated (9.4):** every Ollama call carries think:false with a fail-loud guard; DEFAULT_OLLAMA_MODEL is qwen3.5:9b everywhere; parse tolerance revalidated.
- **New control baseline (9.5) — HARD gate:** both sets re-recorded on qwen3.5:9b in ONE PR; the full v3 validity-gate set holds plus the migration assertions (zero thinking trips, zero cross-room kill rejections); the PR reports the funnel numbers INCLUDING the threshold-inversion count.
- **THE PAUSE:** Wave 0 ends at 9.5's merge. The design thread then re-runs the gameplay-data audit on the new baseline and re-answers the parked conversion worksheet (Q1 §4.6 verdict rendering, Q2 tally/abstain, Q3 pass gates) against the new model's actual failure profile. Conversion contracts (9.6+) are authored only after that — no conversion work, prompt edits, or knob changes land in Wave 0. Wave 1's merge criteria are deliberately absent from this file: they are authored alongside the Wave-1 contracts once the post-9.5 close audit re-anchors the targets.
