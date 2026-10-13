# Phase 9 — Producer hygiene + migration (Wave 0) + conversion quality (Wave 1)

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

The Wave-0 gate, mirroring 8.18's operator shape: with the three hygiene fixes, the client
migration, AND the conversion-prompt PR (#131: crewmate_report v3, accusation_round v5,
vote_ballot v5) all merged, smoke first, then re-record BOTH committed sets on `qwen3.5:9b`
(think:false) in ONE PR, regenerate both reports + MANIFESTs + the prompt-regression fixtures and
baseline, and run the validity gate. This establishes the NEW control baseline — model migration and
the conversion prompts together, per the SIMPLIFIED-PATH convergence (the four prompt levers were
validated on the model-probe harness before merge, not designed blind). The phase pauses at this
merge: the close audit and the conversion-wave worksheet re-answer — did the prompts convert, and
the abstain/tally decision — happen in the design thread before any 9.6+ contract exists.

**Files in scope:**
- replays/samples/*.jsonl + tournament-eval-report.json + MANIFEST.md (flat 4p/1i re-recorded on qwen3.5:9b; model rows update)
- replays/samples/9p2i/ (50 replays + report + MANIFEST re-recorded; roster {9,2,2} unchanged)
- tests/fixtures/prompt_regression/{v_a,v_b}/*.jsonl + baseline.json (regenerated — the model changed, so the recorded fixtures must)
- tests/api/test_replay_loader.py + tests/eval/test_win_condition_selfcheck.py (committed-set pins re-verified on the new bytes; re-scope any zero-denominator runtime skips exactly as 8.18 did)
- tests/scripts/test_build_sample_report.py + tests/scripts/test_verify_samples.py + tests/scripts/test_manifest_writer.py + tests/scripts/test_refresh_samples.py (committed-bytes pins: git_sha, model rows `qwen3.5:9b`, cost 0)

**Files NOT in scope:**
- engine/, meetings/, agents/, llm/, eval/ source (behavior landed in 9.1–9.4 plus the merged conversion-prompt PR #131; this task records + regenerates only). In particular `meetings/manager.py` keeps its token caps at turn 2048 / vote 1024 — do NOT raise the vote cap. The v5 one-sentence rationale is the floor fix; the prior attempt's 8192 does not work (the ~6260-token runaways overrun num_ctx=8192 anyway, trading a truncation abort for a ctx-overrun abort).
- audits/workflows/extract_gameplay_facts.py (run read-only for the funnel numbers; do not modify)

**Definition of done:**
- [ ] Smoke first (3–5 seeds at 9p/2i): the think:false guard holds on live calls (zero thinking content), per-seed wall time measured and the full-run projection reported BEFORE the full runs; STOP for operator go. If the smoke surfaces ANY thinking-guard trip (Ollama version predates the `think` parameter, or the flag is not honored), ABANDON this task without recording further: re-open 9.4 (or escalate the Ollama-version/model question to the design thread) — do not proceed to a full record, and do not weaken the guard.
- [ ] Smoke confirms the floor the prior attempt failed: every smoke seed reaches game_over with zero ballot truncation / unterminated-JSON parse failures. The blocked migration aborted 7/100 games when the 9B's `rationale_text` ran past the vote cap under think:false; the v5 one-sentence-rationale prompt is what closes that runaway (harness: ~104-char ballots). If a seed still aborts on a runaway rationale, STOP — the prompt fix did not hold; escalate to the design thread rather than raising the token cap.
- [ ] Both sets re-recorded in ONE PR on `qwen3.5:9b`; both reports regenerated (format v2; kill_gifted under the 9.1 definition); both MANIFESTs carry the new git_sha + `qwen3.5:9b` model rows; prompt-regression fixtures + baseline regenerated.
- [ ] Validity gate (HARD, the v3 set): friendly-fire 0; every game reaches game_over; betrayal ballots/accusations 0 — now structurally absent at the source per 9.3; leak suite green at 4p/1i and 2-of-9; meeting_rate ≥ 0.60 with ≥ 30 resolved meetings at 9p/2i; byte-identical reconstruction; zero tick-1 kills; zero missed-deadline markers; zero dangling primary_reason_id; PLUS migration assertions: zero thinking-guard trips, zero cross-room kill rejections (the 9.2 fix holding), model rows correct.
- [ ] Funnel report ($0): run audits/workflows/extract_gameplay_facts.py over the new 9p/2i set; PR body reports win split + kill-gifted split (9.1 definition), ejection count, accusation precision, accuser follow-through, persuasion rate, and the threshold-quoting-skip count (the 19/19 inversion class). The extractor does NOT compute the threshold-quoting count: derive it operator-inline (a regex over ballot `rationale_text` in the raw replay meeting records — the facts JSON does not carry rationales), and paste the derivation snippet into the PR body so the next migration reuses it instead of rediscovering the gap. Because vote_ballot v5 renders the §4.6 verdict in-prompt, the threshold-quoting-skip count is now expected near-zero — its residual is the check that the rendering held, not the headline. The headline is now the conversion result: ejection count and accuracy, and whether opt-in corroboration builds vote consensus that crosses the SKIP-plurality bar (the input to the parked abstain/tally decision). Report both. Reported, not gated.
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
direction (9.2 raises real kill cadence; the conversion prompts move ejections; the model change
moves everything else). With v5 the threshold-inversion should be largely closed, so the number that
decides what Wave 1 still needs to fix is the conversion result — ejection accuracy and whether
consensus crosses the SKIP-plurality bar. One atomic PR; an intermediate commit is un-reconstructable.

**Integration risk:**

The wave converges here and the phase PAUSES at this merge. The conversion prompts are already
merged (PR #131); 9.5 records them — it does not author, dispatch, or edit any prompt or reasoner
code. If the thinking guard trips or the floor fails, STOP and fix upstream (the v5 prompt, 9.4, or
the model/Ollama choice) rather than papering the gate — in particular do NOT raise the vote token
cap, which the prior attempt tried (8192) and which reintroduces the num_ctx overrun.

**Ready-to-paste prompt:** `agent_prompts/task-9-5-model-migration-rerecord.md`

## Merge Criteria (Phase 9 Wave 0 — hygiene + model migration)
- **Bookkeeping correct (9.1):** kill_gifted re-anchored to the victim's incomplete instances (9p/2i reads 11/46 on the old bytes); committed reports regenerated offline; bytes + MANIFESTs untouched.
- **Producer waste removed (9.2):** zero cross-room kill-intent rejections in the post-migration set; stalk/navigation behavior unchanged.
- **Team firewall complete (9.3):** the 7.12 output firewall is mirrored on the input side — no self-team suspicion edges, no teammate-incriminating renders, no self-subject rows; crew behavior byte-identical; leak suites green.
- **Model migrated (9.4):** every Ollama call carries think:false with a fail-loud guard; DEFAULT_OLLAMA_MODEL is qwen3.5:9b everywhere; parse tolerance revalidated.
- **New control baseline (9.5) — HARD gate:** both sets re-recorded on qwen3.5:9b in ONE PR; the full v3 validity-gate set holds plus the migration assertions (zero thinking trips, zero cross-room kill rejections); the PR reports the funnel numbers INCLUDING the threshold-inversion count.
- **THE PAUSE:** Wave 0 ends at 9.5's merge. The design thread then re-runs the gameplay-data audit on the new baseline and re-answers the parked conversion worksheet (Q1 §4.6 verdict rendering, Q2 tally/abstain, Q3 pass gates) against the new model's actual failure profile. Conversion contracts (9.6+) are authored only after that — no conversion work, prompt edits, or knob changes land in Wave 0. Wave 1's contracts + merge criteria are authored below, added 2026-06-09 after the post-9.5 close audit re-anchored the targets.

## Wave 1 — Conversion quality

Goal: with the post-9.5 close audit done (audits/audit-2026-06-09-0347-gameplay-data.md,
MINOR_ISSUES, baseline VALID), fix the conversion QUALITY the audit anchored. Crew conversion is
DETECTION-bound, not gate-bound: the §4.6 verdict renders and is obeyed (0 genuine inversions), but
the structured-contradiction detector is the SOLE conversion fulcrum and fails both ways — PRECISION
(13/13 wrong ejections are contradiction false-positives, 8/13 self-inflicted by the body reporter)
and RECALL (25/47 impostor-accused meetings carry no contradiction on the impostor, so the gate
forces SKIP; conversion 21/47 = 0.45). Plus the audit's metric blocker, the 9B turn-verbosity
truncations + dead-player accusations, and a double-counted failed_call telemetry bug.

Owner design principle (2026-06-09): voting off innocent crew is legitimate gameplay; the goal is to
stop RANDOM/MECHANICAL ejections, not to make anyone un-ejectable. No single signal or single round
forces an eject — corroboration within a round and accumulation across rounds convert, and
unreinforced suspicion decays (a "collective clear").

Locked decisions (2026-06-09):
- Wave 1 = the conversion-quality bundle only. Impostor gameplay (the gp-6 toolkit: fake do_task,
  impostor self-report, real chain redirect, teammate coordination, same-room kill-intent gating) is
  its OWN PHASE 10, next, authored from Wave 1's close audit. gp-5 token cuts and gp-7 balance knobs
  are deferred/opportunistic.
- gp-1 RECALL ships as a FIRST CUT (the decaying-accumulator in 9.8). Its payoff couples to game
  length — ≈1.5 meetings/game today gives little cross-round runway; it converts more once Phase 10 +
  gp-7 lengthen games. Accepted.
- Convergence: 9.6 is offline (metric hygiene, BLOCKS any A/B) and lands first. 9.7–9.10 are
  byte-changers that merge to main, then ONE combined re-record (9.11) measures them together. The
  §4.6 gate render and the balance knobs are FROZEN during measurement (account-don't-rule-change).

Parallelism: 9.6 (eval/ only) is file-disjoint and dispatches immediately. 9.7–9.10 share
agents/memory/beliefs.py and meetings/manager.py, so they dispatch SEQUENTIALLY (9.7 → 9.8 → 9.9 →
9.10) to avoid merge conflicts. 9.11 is the operator-run gate after all four merge. Track with
`python3 scripts/compute_next_task.py --phase 9`.

### Task 9.6 — Metric hygiene
**Branch:** `phase-9-metric-hygiene`
**Depends on:** none (offline analysis root)
**Section refs:** DESIGN.md §11.3, §5.5; audits/audit-2026-06-09-0347-gameplay-data.md gp-2
**Complexity:** Medium

The audit found the lead conversion metric is a tautology: vote_correctness_rate =
evidence_backed_impostor_ejections / impostor_ejections, and `_has_real_evidence` is satisfied by the
same predicate that classifies an ejection as impostor-backed, so the rate is structurally pinned to
1.0 and measures nothing — a Wave-1 A/B run on it is blind. Fix the ruler BEFORE any conversion
source change records: demote the tautology to a sentinel, publish ejection_accuracy (the PRECISION
lead) and the impostor-accused -> ejected conversion rate (the RECALL lead — Wave 1 changes both, so
name a lead for each), ship the missed-skip SENTINEL, and reframe the inversion count. Offline only — reads the committed
replays, regenerates the offline reports + fixtures, touches no engine/recording path and no
committed bytes. This task BLOCKS the 9.11 A/B and so lands first.

**Files in scope:**
- eval/vote_correctness.py (demote vote_correctness_rate to a documented bug-sentinel: keep it computed but mark it NOT a KPI; surface ejection_accuracy, already computed on VoteCorrectnessReport, as the published lead)
- eval/meeting_quality.py + scripts/build_sample_report.py (ship ejection_accuracy + a new missed_skip_ballots count into tournament-eval-report.json; reframe threshold_inversions as a firewall sentinel on the report surface)
- a new eval/_suspicion_parse.py — the CANONICAL home for the rendered-suspicion parse (the "maximum suspicion among the living ejection targets is" regex), imported by BOTH eval/meeting_quality.py and audits/workflows/extract_gameplay_facts.py (audits -> eval is the allowed consumer direction); do NOT duplicate the regex on either side
- audits/workflows/extract_gameplay_facts.py (swap its inline rendered-suspicion regex for an import of eval/_suspicion_parse.py — the de-dup; the extractor's facts output stays byte-unchanged, a pure refactor; this is the ONLY audits/ edit and is what makes "both sides import" true)
- the missed-skip computation using that shared parse (a SKIP ballot is MISSED when the voter's rendered max-suspicion over a LIVING target was >= 0.60, else CORRECT), AND the recall lead: the impostor-accused -> impostor-ejected conversion rate (impostor ejections / meetings that verbally accused a true impostor, roles re-derived from the seeder — the audit's 21/47 = 0.45; gp-1b's measurable target)
- eval/report_schema.py (CURRENT_FORMAT_VERSION STAYS 2 — the added fields are wrapper-level aggregates older readers ignore, and 9.6 regenerates every report so there is no old-report read; per the §11.4 policy the version bumps only when older readers cannot interpret the shape)
- replays/samples/tournament-eval-report.json + replays/samples/9p2i/tournament-eval-report.json (regenerated offline from the committed replays; bytes + MANIFESTs untouched)
- tests/eval/test_vote_correctness.py + tests/fixtures/prompt_regression/baseline.json + tests/eval/test_prompt_regression.py (pin the new lead + missed_skip; assert vote_correctness_rate is labelled a sentinel; regenerate the baseline)

**Files NOT in scope:**
- engine/, meetings/, agents/, llm/ source (offline metric layer only; no behavior change)
- replays/samples/**/replay-seed-*.jsonl + MANIFESTs (no re-record; reports regenerate from existing bytes)

**Definition of done:**
- [ ] vote_correctness_rate is documented + surfaced as a bug-sentinel (structurally 1.0), not a KPI; a test asserts the semantics so a future reader cannot mistake it for the lead.
- [ ] TWO leads are published: ejection_accuracy (precision: impostor_ejections / total_ejections, denom all ejections) and the impostor-accused -> ejected conversion rate (recall). missed_skip_ballots is shipped as a SENTINEL (count + CORRECT/MISSED partition) — most MISSED are correct firewall coercions, so it is NOT a down-is-good metric; threshold_inversions likewise reads as a firewall sentinel.
- [ ] The 9p/2i report regenerates to the audited values from the committed bytes as a regression pin: ejection_accuracy 22/35 = 0.6286, conversion rate 21/47 = 0.45, missed_skip 38 (34 firewall + 4 invalid-target + 0 genuine). These pin the 9.5 baseline (9p2i @ fb3cfa5) and are NOT immutable — 9.11 updates them in the regenerated baseline.json, the standard re-record pattern.
- [ ] prompt-regression baseline regenerated; the metric-diff demonstration still attributes to one template version; the CI exact-match test holds.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

ejection_accuracy already exists on VoteCorrectnessReport — the work is plumbing it (and missed_skip +
the conversion rate) into the SHIPPED report surface, not recomputing it. The audit extractor already
parses the rendered max-suspicion per SKIP ballot; lift that parse into eval/_suspicion_parse.py and
import it from BOTH sides so they can never drift. Keep the tautology computed (removing it churns the
schema); just relabel it and add the real leads beside it.

**Integration risk:**

Offline metric/report change. The hard line: committed replay bytes + MANIFESTs do NOT change — only
the regenerated reports + the offline baseline. Any format-version bump must keep the
prompt-regression exact-match test green.

**Ready-to-paste prompt:** `agent_prompts/task-9-6-metric-hygiene.md`

### Task 9.7 — Detector precision
**Branch:** `phase-9-detector-precision`
**Depends on:** none (belief-dynamics root)
**Section refs:** DESIGN.md §5.4, §6.3, §4.6; audits/audit-2026-06-09-0347-gameplay-data.md gp-1 (precision)
**Complexity:** Medium

The detector is the sole conversion fulcrum and a single contradiction lifts suspicion 0.5 → 0.8,
crossing the 0.60 eject-gate ALONE — so one noisy `alibi_vs_sighting` mismatch railroads an ejection.
13/13 wrong ejections were this; 8/13 were the body reporter's own self-stated alibi contradicted by
a third party's sighting of them. Per the owner principle, a LONE WEAK contradiction must not force
an eject; corroboration must. Reporters and innocents stay fully ejectable WITH a second signal — the
fix removes the mechanical railroad, not the ejectability.

**Files in scope:**
- meetings/transcript.py (thread `turn.speaker` onto `_IndexedAlibi`/`_IndexedSighting` in `_iter_alibis`/`_iter_sightings`; in `_detect_alibi_vs_sightings` identify a self-stated alibi `speaker == claim.subject` and a narrow window `to_tick - from_tick` below a small constant — these are the false-positive patterns)
- agents/memory/beliefs.py (PREFER a NARROW, GRADUATED down-weight that targets ONLY the flagged-weak contradictions (self-stated / narrow-window) and preserves a strong contradiction's full weight — a weak signal alone lands suspicious-but-below-gate in [0.5, 0.60), NOT zeroed and NOT crossing. Lower `CONTRADICTION_SUSPICION_DELTA` GLOBALLY only if the narrow version is impractical, stating the recall cost — global weakens strong contradictions too — and any schema/byte implication. Classifying a contradiction as weak for the graduated delta likely needs a derivable property or a new ContradictionRef kind; pick one and state its byte/format implication)
- tests/meetings/test_transcript.py + tests/agents/test_beliefs.py + tests/meetings/test_manager.py (self-stated and narrow-window contradictions do not alone cross 0.60; a self-stated alibi PLUS a second independent signal does; the seed-3/16/47 false-positive shapes no longer auto-eject)

**Files NOT in scope:**
- agents/strategic/prompts/** (no prompt edits here; gp-3 owns the turn prompts in 9.9)
- the §4.6 gate render in vote_ballot.j2 (FROZEN during measurement — the gate is gate-correct; this is a detector/suspicion change)
- replays/samples/** (re-record is 9.11)

**Definition of done:**
- [ ] A self-stated `alibi_vs_sighting` (the reporter's own alibi vs a sighting of them) and a narrow-window mismatch do NOT alone lift the subject across 0.60 — but the down-weight is GRADUATED, not a hard zero: a lone weak contradiction lands in the suspicious-but-not-eject band [0.5, 0.60), so it still raises suspicion (a self-stated conflict IS mildly suspicious). Pinned numerically with the seed-3/16/47 shapes.
- [ ] The same subject WITH a second independent contradiction (or a body-proximity / vent signal) DOES cross — corroboration still ejects. A test asserts the corroboration path so the fix is not "innocents become un-ejectable".
- [ ] If a per-contradiction weight on ContradictionRef is introduced, it is documented as a public-schema change and the format/byte implications are stated; otherwise the down-weight is derived from re-derivable properties with no schema change (preferred).
- [ ] Replay determinism holds: the detector + belief math are pure functions, re-running yields byte-identical flags.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The seam is small: `_iter_alibis`/`_iter_sightings` already have the turn in scope, so the speaker is
one field away. Prefer filtering/down-weighting from re-derivable properties (self-stated, window
width) over a ContradictionRef schema field — it avoids a byte/format change and keeps the recorded
flag set honest. Whatever mechanism is chosen, the corroboration test is the contract's hard line:
proving an innocent is still ejectable on a second signal is what distinguishes "stop the railroad"
from "shield the reporter".

**Integration risk:**

Touches the shared belief/detector path. Recording-side only; committed reconstruction is unaffected
until 9.11 re-records. The corroboration property must be preserved or recall regresses further.

**Ready-to-paste prompt:** `agent_prompts/task-9-7-detector-precision.md`

### Task 9.8 — Suspicion accumulator and decay
**Branch:** `phase-9-suspicion-accumulator`
**Depends on:** 9.7 (shares agents/memory/beliefs.py)
**Section refs:** DESIGN.md §6.3 (belief Rules 3 + 5), §4.6; audits/audit-2026-06-09-0347-gameplay-data.md gp-1 (recall)
**Complexity:** Integration

The first cut of the owner's collective-suspicion model — the recall side of gp-1. 25/47
impostor-accused meetings carry no contradiction (clean fabricated alibi, killed unseen), so no
voter's PRIVATE suspicion reaches 0.60 and the gate forces SKIP. The fix is a decaying accumulator: a
small persistent suspicion bump for being accused in a meeting, plus the deferred decay/clear rules,
so sustained suspicion across rounds converts while one round never does. Accepted to convert weakly
in today's short games (≈1.5 meetings each) — its runway grows once Phase 10 + gp-7 lengthen games.

**Files in scope:**
- agents/memory/beliefs.py (a new accusation-driven rule: an accusation naming a subject adds a SMALL delta, e.g. +0.05, well below the gate alone; wire in the already-present `decay_suspicion` for §6.3 Rule 5 drift toward 0.5 when unreinforced; add Rule 3 corroboration-lowers-suspicion)
- meetings/manager.py + agents/memory/store.py + the game loop (the PERSISTENCE path: the accusation bump must be written to each living agent's PERSISTENT belief state across meetings, unlike the transient vote-time contradiction-lift in `_suspicion_graph_with_contradictions` which rebuilds a throwaway BeliefState — establish/confirm a post-meeting belief-update hook so suspicion carries forward and decays)
- tests/agents/test_beliefs.py + tests/meetings/test_manager.py + tests/agents/test_memory_store.py (one accusation does not cross 0.60; the same subject accused across 2–3 meetings does; an unreinforced bump decays back toward 0.5; a corroboration lowers suspicion; persistence across meetings is asserted)

**Files NOT in scope:**
- the §4.6 gate render in vote_ballot.j2 (FROZEN — this changes how suspicion ACCRUES, not the gate)
- agents/strategic/prompts/** (no prompt edits)
- replays/samples/** (re-record is 9.11)

**Definition of done:**
- [ ] FIRST: the contract verifies/establishes the persistent post-meeting belief-update path; if none exists, building it is part of this task (without persistence the accumulator is inert). The design choice is documented.
- [ ] A single accusation adds the small delta and stays well under 0.60; the same subject accused across 2–3 meetings accumulates over the gate. Pinned numerically.
- [ ] Unreinforced suspicion decays toward 0.5 (Rule 5); a corroboration lowers a subject's suspicion (Rule 3). Both pinned.
- [ ] Determinism + the §1.3 firewall hold: an impostor voter accrues NO accusation-bump against a fellow impostor (the bump rides the same teammate guard as 7.12/9.3); crew leak suites green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The decay half is largely turning on rules already specced in §6.3 and an existing
`beliefs.decay_suspicion`. The hard part is PERSISTENCE: today the contradiction-lift is recomputed
at vote time and thrown away, so a verbal accusation touches nothing durable. Find or add the
post-meeting hook that folds the meeting's accusations into each agent's stored beliefs, then let
decay erode them between meetings. Tune the bump small enough that one round is never decisive — the
owner principle is no single round ejects. If the persistence path must be BUILT rather than found — a
new post-meeting hook + store wiring + determinism + replay-walk safety — expect this task to run
LARGER than 9.7; say so in the PR description so reviewers read the size as scope, not drift.

**Integration risk:**

The largest Wave-1 task — it changes the cross-meeting belief dynamics shared by all roles. The
teammate-firewall invariant (9.3) and crew byte-identity for non-accusation paths are the hard lines.
Expect muted measured effect in 9.11 (short games); that is known and accepted, not a failure.

**Ready-to-paste prompt:** `agent_prompts/task-9-8-suspicion-accumulator-and-decay.md`

### Task 9.9 — Turn prompt discipline and living-roster
**Branch:** `phase-9-turn-prompt-discipline`
**Depends on:** 9.8 (shares meetings/manager.py)
**Section refs:** DESIGN.md §5.1, §5.2, §5.5; audits/audit-2026-06-09-0347-gameplay-data.md gp-3
**Complexity:** Medium

Two 9B-artifact fixes, prompt-layer. (1) Turn-verbosity: with think:false the 9B relocates
deliberation into free_text and overruns the 2048 turn cap, truncating the turn into a fail-soft
default (seeds 8/36/39 — a defaulted opening is a lost chain-driving accusation). Fix it at the
ROOT with a length discipline, NOT by raising the cap (the runaway is unbounded; a higher cap
re-creates the num_ctx overrun the vote rationale hit). (2) Dead-player accusations: the 9B accuses
players no longer living (seeds 11, 33), dropped by the fb3cfa5 validation but wasting the turn —
constrain accusations to the living roster.

**Files in scope:**
- agents/strategic/prompts/crewmate_report.j2 + agents/strategic/prompts/accusation_round.j2 (free_text discipline: "at most 2–3 sentences stating your single conclusion; do NOT narrate or second-guess your reasoning"; a living-roster constraint: "you may ONLY accuse a player on the LIVING list below")
- meetings/manager.py + agents/strategic/prompts/loader.py (thread `living_ids` through `_render_turn_prompt` → `crewmate_report_prompt`/`accusation_round_prompt` → the templates. The accusation roster is living players MINUS the turn's own speaker — an agent cannot accuse itself — mirroring vote_ballot's candidate_targets (living minus voter); reuse the exact filtering, not a parallel implementation)
- orchestrator/game.py (bump DEFAULT_PROMPT_VERSIONS: crewmate_report v3 → v4, accusation_round v5 → v6)
- tests/agents/test_strategic_prompts.py + tests/orchestrator/test_replay_meetings.py (version pins; the living-roster list renders; the discipline text is present; a render-without-living_ids still validates under StrictUndefined per the optional-kwarg pattern)

**Files NOT in scope:**
- meetings/manager.py turn/vote token caps (FROZEN at 2048/1024 — the fix is the prompt, not the cap)
- agents/memory/beliefs.py (no belief change here)
- replays/samples/** (re-record is 9.11)

**Definition of done:**
- [ ] Both turn prompts carry the free_text length discipline; rendered turns state a conclusion without narrating reasoning. The version markers bump (crewmate_report v4, accusation_round v6) end-to-end in a fresh replay entry.
- [ ] The living roster renders into both turn prompts and the templates instruct accusations to stay on it; reuses the candidate_targets threading pattern, not a new one.
- [ ] DEFAULT_PROMPT_VERSIONS + every committed-fresh-replay version assertion updated; committed-fixture assertions (recorded bytes) left UNCHANGED until 9.11 re-records.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The vote ballot already threads candidate_targets (living players minus voter) from the manager into
the prompt; mirror that exact path for the turn prompts' living-roster list rather than inventing a
new channel. The length discipline is the same medicine that fixed the vote rationale (one-sentence
rule) ported to the turn free_text. Do NOT touch the 2048 cap — that is the contract's hard line.

**Integration risk:**

Prompt-version bump touches the meeting-record provenance. Distinguish fresh-replay version
assertions (update) from committed-byte fixture pins (leave for 9.11), exactly as the PR #131 +
8.18 coupling did.

**Ready-to-paste prompt:** `agent_prompts/task-9-9-turn-prompt-discipline-and-living-roster.md`

### Task 9.10 — Failed-call telemetry de-dup
**Branch:** `phase-9-failed-call-dedup`
**Depends on:** 9.9 (shares meetings/manager.py + orchestrator/game.py)
**Section refs:** DESIGN.md §11.4; audits/audit-2026-06-09-0347-gameplay-data.md gp-4 (MECH-B-1)
**Complexity:** Small

Code-certain telemetry bug. Seeds 8/36/39 each persist a byte-identical failed_call row TWICE,
double-counting 5,969 input + 6,144 output tokens and inflating total_failed_calls from a true 4
distinct defaults to a reported 7. Meeting outcomes are unaffected (the meeting count comes from
meeting records), so it is telemetry-accuracy, not eval-invalidating — but it must be fixed before
any per-game token A/B. The duplicate comes through the parse_failures branch: a single DefaultedCall
carries the same LLMCallFailure twice (a retry path appends, the deadline-default capture appends
again).

**Files in scope:**
- orchestrator/game.py (`_record_deadline_defaults` ~L1213-1226: the parse_failures population that writes each failure)
- meetings/manager.py (the DefaultedCall / `recovered_call_failures` plumbing that double-appends)
- orchestrator/replay.py (`record_failed_call` — the single-write guard, if dedup lands at the recording chokepoint)
- tests/orchestrator/test_replay.py + tests/meetings/test_manager.py (a defaulted turn whose parse failed records EXACTLY ONE failed_call row; the seed-8/36/39 shape no longer double-counts)

**Files NOT in scope:**
- the fail-soft default behavior itself (7.10 — unchanged; only the telemetry write is de-duplicated)
- agents/, eval/ (the report reads whatever is recorded; 9.6 already reframed the metric surface)
- replays/samples/** (re-record is 9.11; the existing committed dup is fixed-forward on the new bytes)

**Definition of done:**
- [ ] A defaulted-turn parse failure records exactly one failed_call row; de-duplicated by (model, raw_response, input_tokens, output_tokens) OR recorded on exactly one path, with the choice documented.
- [ ] Confirmed offline against seeds 8/36/39: the failed-call token aggregate drops by 5,969 in / 6,144 out and total_failed_calls reads the true 4 distinct.
- [ ] The single non-duplicated default (seed 5) is unaffected; legitimate distinct failures in one meeting still each record once.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Trace the LLMCallFailure from the provider's parse-retry through DefaultedCall into
`_record_deadline_defaults`; the cleanest fix is a single-write chokepoint (record_failed_call dedups
by the byte-identity tuple) so neither path can double-append. Confirm by collapsing the raw JSONL
failed_call lines for headless-seed-8:meeting-1 tick 14 — two identical rows become one.

**Integration risk:**

Recording-path change; takes effect on the 9.11 re-record. The existing committed dup is known and
fixed-forward, not retro-patched. Keep distinct in-meeting failures each recording once.

**Ready-to-paste prompt:** `agent_prompts/task-9-10-failed-call-telemetry-de-dup.md`

### Task 9.11 — Wave-1 combined re-record and gate
**Branch:** `phase-9-wave1-rerecord`
**Depends on:** 9.5, 9.6, 9.7, 9.8, 9.9, 9.10
**Section refs:** DESIGN.md §11.4, §3.5; audits/audit-2026-06-09-0347-gameplay-data.md (the Wave-1 set)
**Complexity:** Integration

The Wave-1 gate, mirroring 9.5's operator shape. With the metric hygiene (9.6) and the four
byte-changers (9.7–9.10) merged, smoke first, then re-record BOTH committed sets on `qwen3.5:9b`
(think:false) in ONE PR, regenerate both reports + MANIFESTs + the prompt-regression fixtures and
baseline, and run the validity gate PLUS the conversion-quality deltas. The phase pauses at this
merge: the design thread re-runs the close audit on the new baseline and authors Phase 10 (impostor
gameplay) from its findings.

**Files in scope:**
- replays/samples/*.jsonl + tournament-eval-report.json + MANIFEST.md (flat 4p/1i re-recorded; model rows unchanged at qwen3.5:9b, git_sha updates)
- replays/samples/9p2i/ (50 replays + report + MANIFEST re-recorded; roster {9,2,2} unchanged)
- tests/fixtures/prompt_regression/{v_a,v_b}/*.jsonl + baseline.json (regenerated — prompts + detector changed)
- tests/api/test_replay_loader.py + tests/eval/test_win_condition_selfcheck.py + the committed-bytes pins in tests/scripts/* (git_sha, prompt-version rows crewmate_report.v4 / accusation_round.v6, model qwen3.5:9b, cost 0; re-scope any zero-denominator skips as 8.18/9.5 did)

**Files NOT in scope:**
- engine/, meetings/, agents/, llm/, eval/ source (all behavior landed in 9.6–9.10; this task records + regenerates only). The §4.6 gate render and balance knobs stay FROZEN.
- audits/workflows/extract_gameplay_facts.py (run read-only for the funnel; the close audit re-run is a separate design-thread step)

**Definition of done:**
- [ ] Smoke first (3–5 seeds @ 9p/2i): the think:false guard holds; every smoke seed reaches game_over with zero ballot truncation AND zero TURN truncation now that 9.9's discipline is in (a residual runaway turn → STOP, escalate, do NOT raise the cap); per-seed wall time + full-run projection reported; STOP for operator go.
- [ ] Both sets re-recorded in ONE PR on qwen3.5:9b; both reports regenerated; both MANIFESTs carry the new git_sha + the crewmate_report.v4 / accusation_round.v6 rows; prompt-regression fixtures + baseline regenerated.
- [ ] Validity gate (HARD, the v3 set): friendly-fire 0; every game reaches game_over; betrayal ballots/accusations 0; leak suite green; meeting_rate >= 0.60 with >= 30 resolved meetings @ 9p/2i; byte-identical reconstruction; zero tick-1 kills; zero dangling primary_reason_id; zero thinking trips; zero cross-room kill rejections; model rows correct.
- [ ] Conversion-quality deltas reported (the 9.6 metrics), each attributed honestly: PRECISION (primarily 9.7) — ejection_accuracy UP from 0.629, wrong_ejections DOWN from 13/35. RECALL (primarily 9.8) — the impostor-accused -> ejected conversion rate UP from 21/47 = 0.45, expecting a SMALL lift in these short games (the accumulator's runway is limited — known, not a failure). missed_skip_ballots is a SENTINEL, not a down-is-good metric: 34 of the 38 are correct firewall coercions that SHOULD persist; only the 4 invalid-target ones drop (via 9.9's living-roster). Plus defaulted-turn count DOWN from 4 (9.9), invalid-accusation-target drops DOWN from 17 (9.9), total_failed_calls the true distinct count (9.10). Reported, not gated.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Operator-run local session, identical mechanics to 9.5: `ollama pull qwen3.5:9b`,
AILIBI_LLM_PROVIDER=ollama on every refresh, model from the 9.4 constant. The conversion deltas are
the headline — read them against the 9.5 baseline (9p2i @ fb3cfa5) and name dir + commit + model in
the comparison. Expect the recall accumulator's effect to be SMALL in these short games; that is
known. One atomic PR; an intermediate commit is un-reconstructable.

**Integration risk:**

The wave converges here and the phase PAUSES at this merge — do not author or implement Phase 10
work in this task. If the floor fails, STOP and fix upstream rather than papering the gate; the
2048 turn cap stays frozen (9.9 is the turn-verbosity fix).

**Ready-to-paste prompt:** `agent_prompts/task-9-11-wave-1-combined-re-record-and-gate.md`

## Merge Criteria (Phase 9 Wave 1 — conversion quality)
- **Metric ruler fixed (9.6) — BLOCKS the A/B:** vote_correctness_rate demoted to a sentinel; ejection_accuracy (precision lead) + the impostor-accused -> ejected conversion rate (recall lead) published; missed_skip_ballots shipped as a sentinel; threshold_inversions reframed; the rendered-suspicion parse shared via eval/_suspicion_parse.py (no duplication); offline, committed bytes untouched.
- **Precision (9.7):** a lone weak (self-stated / narrow-window) contradiction no longer alone crosses 0.60; corroboration still ejects — innocents stay ejectable, the mechanical railroad is gone.
- **Recall first cut (9.8):** a persistent, decaying accusation-accumulator carries suspicion across rounds (no single round decisive); decay + corroboration clear; teammate firewall preserved; muted-but-correct in short games.
- **9B artifacts (9.9):** turn free_text length discipline (no cap raise) + living-roster accusation constraint; versions bumped.
- **Telemetry (9.10):** failed_call rows de-duplicated; true distinct count; offline-confirmed.
- **New baseline (9.11) — HARD gate:** both sets re-recorded on qwen3.5:9b in ONE PR; the full v3 validity gate holds; the conversion deltas are reported (ejection_accuracy up; wrong/missed/defaulted/invalid down).
- **THE PAUSE:** Wave 1 ends at 9.11's merge. The design thread re-runs the gameplay-data close audit on the new baseline, confirms precision improved without a new degeneracy, and authors Phase 10 (impostor gameplay) from its findings. No Phase-10 work lands in Wave 1.
