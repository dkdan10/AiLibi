# Review B — meetings-manager (meetings/manager.py, constants.py, schemas.py, voting.py, tests/meetings/*manager*)

Reviewer label: `meetings-manager`. Read-only. Repo at `main` (b809b19c). Machine load during timings: `uptime` 5.6–6.7 (1-min), 10-core.

Scratch artefacts (all under `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/meetings-manager/`):
`density.py` (comment/docstring measurement), `fuzz_ballot_chain.py` (hypothesis probe, 3000 examples), `profile_run.py` (cProfile of `MeetingManager.run`), `repro_identity_fields.py` (identity-field default repro), `vacuous_tie_test.py`, `edge_small.py`.

---

## 1. Executive read (10 lines)

1. `meetings/manager.py` is a 3,989-line God module of which only **1,468 lines (36.8%) are code**; 955 comment + 1,255 docstring lines form an embedded changelog (173 lines cite a `Task N.M`, 107 mention audits). radon MI = **C (3.97)**; 7 functions at CC ≥ 14. [VERIFIED]
2. The protocol core (opening → reactive chain → opt-in → roll-call → sequential ballots → tally) is **correct, deterministic and well guarded**: 995 tests pass in 15 s; a hypothesis probe of the full ballot-guard chain (3,000 random inputs) upheld every invariant; the committed 204-meeting corpus shows **0 defaulted turns / 0 defaulted ballots**. [VERIFIED]
3. Error handling is precise, not sloppy: only deadline + `ValidationError` fail soft; provider timeouts are re-tagged (`_isolate_provider_timeout`) to avoid the py3.11 `asyncio.TimeoutError is TimeoutError` alias trap; every default is surfaced via `DefaultedCall` with parse-failure spend recovery. Nothing is silently swallowed. [VERIFIED]
4. The manager is the **only** module of `meetings/` allowed to import `agents.*` (import-linter forbids `agents → meetings.manager`), so the package straddles two layers; the reason is ~500 lines of belief-fold code (`_suspicion_graph_with_contradictions`, `derive_belief_evidence`, `_capped_provenance`) welded into the protocol module. [VERIFIED]
5. The LLM output schema *is* the record schema: models must emit `turn_id/turn_index/speaker/turn_kind/reply_to` (and `VoteBallot.voter`) which the manager discards and overwrites; a bad value in a discarded field fails validation and **defaults an otherwise valid turn** (repro below). [VERIFIED]
6. Four "levers" are dead (`roll_call_round_enabled`, `citation_gate_enabled`, `absence_prior_enabled`, `reporter_exculpation_enabled` all `del env; return True`) yet still threaded, branched on, exported and pinned by ~15 tests whose names/docstrings say the opposite of what they assert. `MeetingParticipant.sighting_records` is populated by the orchestrator but never read by the manager. [VERIFIED]
7. DESIGN.md §5.2 does not know about the roll-call round (which now supplies ~half of all turns: 1,088 turns == 1,088 ballots in the committed sets) and says voting is "parallel"; the code is sequential by design. [VERIFIED]
8. Three `test_manager.py` tie/skip-plurality tests are vacuous since the citation gate graduated: their eject ballots are coerced to SKIP before the tally, so they would pass under a broken tally. [VERIFIED]
9. Manager compute is negligible (~1 ms/meeting excluding LLM); no perf findings. `detect_contradictions` is recomputed per turn over the growing transcript (O(turns²)) but at 7–9 turns it's ~2.5 ms total. [VERIFIED]
10. Net: a sound state machine and guard chain buried under accidental complexity (dead levers, changelog comments, duplicated blocks, an oversized file). Refactor for structure, not for behaviour.

---

## 2. Findings (ranked by severity)

### P1-1 — God module straddling the layer boundary [VERIFIED]
- **Where:** `meetings/manager.py` (3,989 lines); `.importlinter` contract `agents_must_not_import_meetings_manager`; `meetings/constants.py` docstring ("lets `agents/` read it WITHOUT importing the 3-KLoC manager module").
- **What:** `manager.py` imports `agents.memory.beliefs` (BeliefState, apply_contradiction_rule, apply_meeting_evidence_rules, …) solely for the belief-fold functions (`_suspicion_graph_with_contradictions` 240 lines, `derive_belief_evidence` 164, `_capped_provenance` 60, `_joint_capped_suspicion`, `_provenance_from_entry`, `MeetingBeliefEvidence`). Everything else in the file is protocol/guard code with no `agents` dependency. Because the fold lives here, `meetings.manager` sits *above* `agents` while `meetings.{schemas,render_contract,constants,transcript}` sit *below* — an import-linter contract exists purely to police that split, and `constants.py` was created just so `agents` could read one float without importing this file.
- **Evidence:** density measurement — `total=3989 blank=311 comment=955 docstring=1255 code=1468 (36.8%)`. radon: `MI C (3.97)`; CC: `_opt_in_eligible_ids` 20, `_collect_turn` 20, `_suspicion_graph_with_contradictions` 19, `derive_belief_evidence` 17, `run` 17, `_collect_one_ballot` 16, `guard_ballot_target_graph` 14. `run` is 305 lines, `_collect_turn` 308, `_collect_one_ballot` 302 (164 of them comments).
- **Why it matters:** every agent-authored task appends to this file (each guard/lever leaves a 40–100-line docstring); nothing can be understood without reading ~2k lines of prose; the layer split forces awkward workarounds (constants leaf, `render_contract.SuspicionEntry` mirroring `SuspicionProvenance` field-by-field with `_provenance_from_entry` to rebuild it).
- **Severity/confidence:** P1 maintainability, high confidence.

### P1-2 — LLM output schema == record schema: discarded identity fields can default a valid turn [VERIFIED]
- **Where:** `meetings/manager.py:1552-1562` (`return parsed.model_copy(update={"turn_id":…,"turn_index":…,"speaker":…,"turn_kind":…,"reply_to":…})`), `:2020` (`normalized.model_copy(update={"voter": participant.agent_id})`), `meetings/schemas.py:298-323` (`MeetingTurn`), templates e.g. `agents/strategic/prompts/qwen3_6_27b/crewmate_report.j2:104` (`{"turn_id": "t", "turn_index": 0, "speaker": …, "turn_kind": "opening", "reply_to": null, …}`).
- **What:** the model is asked to emit five identity fields the manager is "authoritative" for and overwrites. `llm/report_normalize.py` does not repair them. So `turn_kind: "statement"` (not in the `Literal`), a non-int `turn_index`, or a non-string `reply_to` raises `ValidationError` on a content-valid turn → the fail-soft records the placeholder default and the chain step is lost.
- **Evidence:** `repro_identity_fields.py`: reply from p-3 accusing p-2, all content valid, `turn_kind="statement"` →
  ```
  p-3 turn free_text: '(missed deadline; no turn submitted)'   claims: ()
  defaulted_calls: (DefaultedCall(phase='reply', agent_id='p-3', trigger='validation', …),)
  chain kinds: ['opening', 'reply', 'opt_in', 'opt_in']   # chain to p-2 lost
  ```
- **Why it matters:** wasted output tokens on every turn (2× N calls per meeting), an avoidable failure surface, and a validation-default whose recorded text says "missed deadline". A `MeetingTurnPayload` (observations/claims/free_text) as the LLM schema, composed into `MeetingTurn` by the manager, removes the class entirely (the record schema and committed replays stay untouched — only the *prompt-side* schema changes, which is a prompt-version bump).
- **Severity/confidence:** P1 (real defect class, currently latent — 0 occurrences in the 204 committed meetings with the 27B model), high confidence.

### P1-3 — Dead levers, dead plumbing, disconnected mechanisms [VERIFIED]
- **Where / what:**
  - `manager.py:859-892 roll_call_round_enabled(env)` → `del env; return True`; still branched at `:1155 if roll_call_round_enabled():`; `ENV_ROLL_CALL_ROUND` exported "for naming provenance".
  - `constants.py:54-73 citation_gate_enabled(env)` → always True; branched at `manager.py:2015 if citation_gate_enabled():`.
  - `absence_prior_enabled(env)` / `reporter_exculpation_enabled()` (agents side) — `manager.py:2447 folds = … or (evidence.absent and absence_prior_enabled(env))`, `:1766 render_reporter = reporter_id if reporter_exculpation_enabled() else None`, and an `env: Mapping | None = None` parameter threaded through `_suspicion_graph_with_contradictions(...)` (`:2316`, `:2496`) purely to feed always-True resolvers.
  - `MeetingParticipant.sighting_records` (`:686`): populated by `orchestrator/game.py:1081`, **never read** by the manager (`manager.py:1235-1246` says so explicitly: "deliberately NOT threaded"). The consumer seam `derive_belief_evidence(sighting_records=…)` exists and is covered by a 1,046-line test file (`tests/meetings/test_vouch_grounding.py`) for a mechanism that is disconnected in production since Task 16.7.
  - `_guard_teammate_turn_claims` (`:3353-3389`) runs a "backstop" that its own docstring calls "a no-op once the primary guard has run"; `run()` `:1092-1101` calls `drop_teammate_statement_target` on the chain step, self-described as "a provable no-op".
  - `_render_turn_prompt` passes `public_transcript=""` unconditionally (`:1642`); the render contract and 15 templates still carry/branch on it (`crewmate_report.j2:79 {% if public_transcript %}`) — a vestige of the pre-8.7 parallel-reports protocol.
- **Evidence:** vulture is clean (the code is *called*, just pointless); grep of `sighting_records=` outside tests → only `manager.py:3625` (inside the unreached branch) and `orchestrator/game.py:1081`. Tests pin the dead resolvers: `TestRollCallResolver` (3 tests + 7 parametrized), `TestRollCallOffPath` (whose docstring reads "OFF path (the default): the round is skipped" and whose test `test_default_env_skips_the_round_and_issues_no_extra_calls` asserts the round **fires** and 8 calls are made), `test_citation_gate.py::test_is_unconditionally_on / test_env_value_is_ignored`, `tests/orchestrator/test_replay.py` (env-stamp table for both).
- **Why it matters:** each retired lever leaves an `if always_true():` and an unused `env` argument that every future reader must decode; the "widen-the-contract-inert" pattern (16.3/16.7) means production dataclasses carry fields nobody consumes; test names lie.
- **Severity/confidence:** P1 maintainability (accidental complexity), high confidence.

### P1-4 — Comment/docstring sprawl restating history [VERIFIED]
- **Where:** whole file; e.g. `TEAMMATE_COERCED_VOTE_RATIONALE` constant has a 34-line comment (`:222-256`); `MeetingParticipant` docstring 100 lines (`:602-703`); `_suspicion_graph_with_contradictions` docstring 101 lines + 45 comment lines for 82 lines of code; `_collect_one_ballot` 164 comment lines for 138 code lines.
- **Evidence:** 2,210 of 3,989 lines are prose; `grep -c "Task [0-9]"` = 173 (42 distinct task ids); "audit" 107; "byte-identical/unchanged" 35; "UNCONDITIONAL" 31; "default-OFF" 18. Stale references: `:3001` and `:3141` cite `MeetingManager._collect_vote` (no such method — it is `_collect_one_ballot`); `constants.py:32` cites `meetings.voting.tally_votes` (it is `tally_ballots`).
- **Why it matters:** the prose is a git log, not documentation of current behaviour; readers must mentally subtract "was default-OFF at 16.6, graduated at 16.17" from every paragraph to learn what the code does *now*. Stale names show the prose is not maintained with the code.
- **Severity/confidence:** P1 maintainability, high confidence.

### P2-5 — Docs vs code drift on the protocol [VERIFIED]
- **DESIGN.md §5.2** (lines 483-522): phases 1-5 only; **no roll-call round**, which is unconditional since baseline 6 and supplies ~53% of turns (`audits/audit-phase-18-planning.md §3.4`, and in the committed sets every living player speaks: 1,088 turns == 1,088 ballots across 204 meetings). `PHASE 4: VOTING (parallel, deadline T2)` — code collects ballots **sequentially** (`manager.py:1699-1720`, GPU-contention rationale). `MeetingManager.run` docstring (`:1000`) also omits roll-call.
- **Opt-in gate semantics changed silently:** with roll-call unconditional, `_opt_in_eligible_ids` (71 lines, CC 20) no longer decides *whether* a non-speaker speaks — everyone does — only the *order* (co-present first, then the rest by id). Docstrings (`:2121-2147`, DESIGN §5.2 PHASE 3) still describe it as an eligibility gate. Both opt-in and roll-call turns record `turn_kind="opt_in"`, so a transcript cannot distinguish them.
- `tests/meetings/test_manager.py:472` header: `# --- Roll-call round (Task 18.8, DEFAULT-OFF) ---`.
- Severity P2 (docs), high confidence.

### P2-6 — Vacuous tests: tie/skip-plurality assertions pass for the wrong reason [VERIFIED]
- **Where:** `tests/meetings/test_manager.py::TestVotingAndResolution::test_tied_non_skip_targets_resolve_to_skipped` (:929), `::test_skip_plurality_skips_even_with_one_non_skip_vote` (:938), `::TestPreVoteFoldOnProductionPath::test_inform_leaves_the_equal_tally_and_tie_skip_frozen` (:5138).
- **What:** these script eject ballots without `primary_reason_id` and with no contradiction flags; since 16.17 the citation gate coerces every such eject to SKIP *before* the tally, so `SKIPPED` is asserted on a 4×SKIP tally, not on a tie.
- **Evidence:** `vacuous_tie_test.py`: `tie test recorded ballots: [('p-1','SKIP',"[uncited zero-flag eject target 'p-2' coerced"), ('p-2','SKIP',…), ('p-3','SKIP',…), ('p-4','SKIP',…)]`. `test_eject_on_plurality` (:911) was updated with `vote_reason_ids` when the gate graduated; its siblings were not.
- **Why it matters:** the manager-level tie rule and skip-plurality rule are only really tested in `test_voting.py`; a regression in the manager's *wiring* to the tally would not be caught here. Severity P2, high confidence.

### P2-7 — Stringly-typed trigger kind, re-derived in 17 places [VERIFIED]
- **Where:** `MeetingTrigger` (`manager.py:704-717`) has no `kind`; `_trigger_is_emergency` (`:720`) tests `EMERGENCY_TRIGGER_PHRASE in trigger.description`; inline duplicate at `:1686 is_body_report=(EMERGENCY_TRIGGER_PHRASE not in trigger.description)`; `orchestrator/game.py:2440-2467` *has* the structured `trigger_event.trigger` and discards it when building the trigger; 15 template files hard-code `"called an emergency meeting" in meeting_trigger`.
- **Evidence:** `edge_small.py`: description `"p-1 reported a body at tick 5 (right after p-2 called an emergency meeting last round)"` → `_trigger_is_emergency → True` (misclassified). Not reachable with today's orchestrator format, but the manager's whole emergency behaviour (body strip, reporter exculpation, absent-set trigger kind, cover-directive gating) hangs on a substring of free text.
- Fix: add `kind: MeetingTriggerKind` to `MeetingTrigger` (populated from the engine event) and pass `is_emergency` to renderers; keep the phrase only as prompt copy. Severity P2 design, high confidence.

### P2-8 — Duplicated helpers and triplicated loop bodies [VERIFIED]
- `manager._normalize_ballot_target` / `_SKIP_TARGET` / `INVALID_VOTE_TARGET_MARKER` duplicate `voting.normalize_ballot_target` / `SKIP_TARGET` / `INVALID_VOTE_TARGET_MARKER` byte-for-byte (`voting.py:63-84` documents this as "backlog"; kept in sync only by `test_vote_tally_parity.py`).
- `rendered_vote_max = float("%.2f" % max(...))` (`:1837-1848`) re-implements `_render_gate_value` (`:3130`) — the comment even says "Identical to".
- `run()` contains three near-identical 20-line blocks (reply `:1102-1120`, opt-in `:1128-1150`, roll-call `:1156-1178`): build `transcript_so_far`, call `detect_contradictions`, call `_collect_turn`, append, add to `spoken`. One `_take_turn(speaker, kind, reply_to, prior)` closure removes ~40 lines and one source of divergence.
- `_MARKER_REPR_VALUE` regex duplicated in `api/replay_loader.py` (acknowledged in comment `:2969`).
- Severity P2, high confidence.

### P2-9 — Hidden coupling via audit-marker strings and private imports [VERIFIED]
- Nine marker literals (`INVALID_VOTE_TARGET_MARKER`, `TEAMMATE_VOTE_TARGET_MARKER`, `BALLOT_TARGET_REDIRECT_MARKER`, `VOTE_PARSE_DEFAULT_MARKER`, `INVALID_REASON_ID_MARKER`, `INVALID_OBSERVATION_ID_MARKER`, `UNCITED_ZERO_FLAG_EJECT_MARKER`, `EMERGENCY_BODY_STRIP_MARKER`, `INVALID_*_MARKER` on turns) are the *only* structured record of guard activity; they are prepended to `rationale_text`/`free_text` and then regex/substring-parsed by `api/replay_loader.py`, `eval/deduction_metrics.py`, `eval/vj_instruments.py`, `eval/meeting_quality.py`, `training/surrogate/dataset.py`. The `{x!r}` repr shape and the `]` terminator are load-bearing across four packages (see the 19.15 redaction saga, `:2963-3054`).
- `eval/vj_instruments.py:173-180` imports the private `_suspicion_graph_with_contradictions` and `_provenance_from_entry`.
- The orchestrator's hard-evidence gate (`orchestrator/game.py:2720`, `hard_evidence_gated_suspicion`) is applied to the *input* graph only; the manager's pre-vote fold can lift a clamped 0.59 soft-only row over the 0.60 gate via testimony spread (documented as "composes, never bypasses" in `beliefs.py:370-378`). Noted here as coupling; the gameplay consequence is the other track's call.
- Guard activity in the committed 204 meetings (marker grep): `[invalid accusation …dropped]` 53 turns (4.9%), `[under-gate … redirected]` 13 ballots (1.2%), `[invalid target …]` 3, `[invalid primary_reason_id …]` 2, `[uncited zero-flag …]` 1, teammate coercions 0, defaults 0.
- A structured `guard_events: tuple[BallotRewrite,…]` field on the DTO would make the contract typed; today it cannot change without moving replay bytes, so it is a P2 design note.

### P2-10 — Tests that pin source text / signatures rather than behaviour [VERIFIED]
- `tests/meetings/test_vote_tally_parity.py:420-451`: `inspect.getsource(MeetingManager._tally)` and asserts the identifiers `tallies/max_votes/leaders/leader_max_confidence` do not appear anywhere in `manager.py`'s source (a comment mentioning `max_votes` would fail it) and that the literal `"self._tally(ballots)"` appears in `run`'s source.
- `tests/meetings/test_citation_gate.py:497`: `set(inspect.signature(guard_ballot_citation).parameters) == {"ballot","contradictions"}`.
- Severity P2, high confidence.

### P2-11 — Misleading default text on validation-triggered defaults [VERIFIED]
- `DEFAULT_TURN_FREE_TEXT = "(missed deadline; no turn submitted)"` and `DEFAULT_VOTE_RATIONALE = "(missed deadline; default skip)"` (`:197-198`) are recorded for **both** deadline misses and schema-validation failures (`:1393-1420`). The `DefaultedCall.trigger` is correct, but the transcript the spectator/eval sees says "missed deadline" for a parse failure (see P1-2 repro output). Frozen for committed bytes; only future recordings can be fixed. Low confidence anyone is misled today (0 defaults in the corpus).

### P2-12 — Per-run mutable ledgers on the manager instance [JUDGMENT]
- `_defaulted_calls` / `_recovered_call_failures` (`:949-963`) are reset at the top of `run` and read by the orchestrator afterwards — a side channel instead of a return value; a `run` that raises leaves the previous meeting's ledger half-overwritten; not reentrant. A `MeetingRunReport(result, defaulted_calls, recovered_failures)` return would be cleaner (`MeetingResult` is the frozen replay DTO and rightly does not carry them).

### P2-13 — Sequential ballots hard-coded [JUDGMENT]
- `_collect_ballots` (`:1691-1720`) is sequential for local-GPU contention reasons; there is no `MeetingConfig` knob, so a cloud provider (Featherless) pays N× vote latency per meeting. Ordering determinism does not depend on concurrency (ballots are keyed by participant and sorted), so a bounded-concurrency option would be safe.

---

## 3. What is genuinely GOOD

- **Single chokepoints.** Every turn kind flows through `_collect_turn`; every ballot through `_collect_one_ballot`; the guard order (roster normalise → reason-id → observation-id → teammate coercion → graph guard → citation gate) is fixed and documented, and the guards are pure functions of their inputs. [VERIFIED]
- **Guard-chain invariants hold under fuzzing.** `fuzz_ballot_chain.py` (hypothesis, 3,000 examples over voters/candidates/teammates/graphs/thresholds incl. the 0.595 band, quote-bearing ids and marker-shaped payloads): recorded target ∈ candidates ∪ {SKIP}; never a teammate; never the voter; cited ids ∈ valid sets; teammate coercion always redacts the model body while keeping upstream markers; no under-gate eject survives a MUST-vote verdict; no uncited zero-flag eject survives. `fuzz OK: 3000 examples, invariants held`. [VERIFIED]
- **Determinism discipline.** Participants sorted at entry; opt-in and roll-call in id order; tie-break by lowest id; `derive_belief_evidence` returns sorted tuples; `_reported_statement_sort_key` totalises `None`s; the chain is re-derivable from `transcript.turns` alone (`next_chain_step`). [VERIFIED by reading + `TestReplayWalk`]
- **Error model is deliberate.** Only `asyncio.TimeoutError` (deadline) and `ValidationError` degrade; `_isolate_provider_timeout` re-tags inner `TimeoutError` → `LLMProviderError` so infrastructure timeouts propagate (the 3.11 alias trap is called out and tested, `TestProviderTimeoutDistinctFromDeadline`); parse-failure spend that a real provider raised before the recording client logged is recovered on both the default path (`DefaultedCall.parse_failures`) and the success-after-retry path (`recovered_call_failures`). No swallowed failures found. [VERIFIED]
- **Fail-loud entry validation.** Bad role literal, non-impostor with `fellow_impostor_ids`, opener not a participant, dead∩living overlap, ≤0 deadlines, out-of-range threshold — all raise before any LLM spend. [VERIFIED]
- **The prompt-byte golden** (`tests/meetings/test_prompt_byte_golden.py`) re-runs the *real* `MeetingManager.run` over 204 committed meetings with a stub client keyed by recorded prompt bytes — a byte-for-byte end-to-end regression of the whole render/guard path, with a one-byte perturbation leg proving it can fail. Runs in 7 s. [VERIFIED]
- **Tally consolidation (19.26)** removed the duplicate `_tally` body; `test_vote_tally_parity.py` checked both over 707 meetings before deleting one. `voting.tally_ballots` is small, pure, and its 5-rule docstring is exact. [VERIFIED]
- **Test harness** (`tests/meetings/_manager_helpers.py`): scripted client with phase-tagged stub prompts + per-speaker responder builder makes protocol tests short and readable; 995 tests in 15 s.
- **Performance is a non-issue:** ~1 ms of manager compute per 7-player meeting (cProfile: 5 meetings in 40 ms incl. asyncio loop), dominated by `detect_contradictions` re-runs (18 ms/5 meetings). [VERIFIED]

---

## 4. Architecture / design assessment

**Well-designed:** the reactive-chain-as-pure-function-of-recorded-turns idea (replay never re-calls the model); the two-tier fail-soft (validation-degrade keeps the body report, only a never-parsed opening gets the placeholder); the provenance-split redaction in `coerce_teammate_ballot_to_skip` (split by provenance, never by pattern — the correct security argument, and the fuzz confirms it); the 2-dp quantisation in `guard_ballot_target_graph` so guard and prompt read the same number.

**Accidental complexity:**
1. *Levers that never die.* Every graduated lever leaves a resolver returning `True`, an `env` kwarg, an `if`, an `ENV_*` export, a stamp-table entry and a test class. Four are dead in this area alone. The "byte-identical OFF path" doctrine was right *while measuring*; keeping the branches after graduation is pure debt.
2. *"Widen-the-contract-inert".* Fields/kwargs added "inert" (`persona`, `suspicion_provenance`, `sighting_records`, `public_transcript`) accrete on the dataclasses and renderer Protocols; one (`sighting_records`) never got connected.
3. *Record schema doubling as LLM schema* (P1-2).
4. *Prose as changelog* (P1-4). Git and `audits/` already hold this history; the code should state current behaviour and link.
5. *Meetings package split across layers* (P1-1). Belief-fold code has no business in the protocol module.

**Refactor I would do (behaviour-preserving, replay-byte-neutral):**
- `meetings/manager.py` → `meetings/protocol.py` (MeetingManager + config/participant/trigger/DefaultedCall, ~900 lines with prose trimmed) ; `meetings/turn_guards.py` (self-alibi normalise, teammate claim/vent guards, `_drop_non_roster_claims`, opening position check, retry feedback, turn markers) ; `meetings/ballot_guards.py` (the six-stage chain, ballot markers, `_render_gate_value`; absorb `voting.normalize_ballot_target` here or import it) ; `meetings/belief_fold.py` (`MeetingBeliefEvidence`, `derive_belief_evidence`, `extract_belief_evidence`, `_suspicion_graph_with_contradictions`, joint cap, provenance helpers — the *only* module importing `agents.memory.beliefs`) ; move `_opt_in_eligible_ids` and `derive_reported_testimony` into `meetings/transcript.py` (they are pure transcript reductions). Keep `meetings/manager.py` as a thin re-export shim for the 20+ importers for one phase, then retire it. Update the import-linter contract to `agents ↛ meetings.protocol, meetings.belief_fold`.
- Introduce `MeetingTurnPayload` / `VoteBallotPayload` as the LLM-facing schemas (prompt-version bump); compose the record models in the manager.
- Add `kind: Literal["report","emergency"]` to `MeetingTrigger`; delete substring detection; pass `is_emergency` to renderers.
- Delete the four dead resolvers and their `env` plumbing/`if`s; delete `ENV_ROLL_CALL_ROUND`/`ENV_CITATION_GATE` from the public surface (the replay stamp table can hold the literals); delete the two "provable no-op" guard calls; either connect `sighting_records` in `run()` (a substrate change → re-record) or drop the field and its 1k-line test file.
- Collapse the three turn-loop blocks in `run()` into one local helper.
- Trim prose: keep the *what/why-now* of each guard (≤ 10 lines), move task/audit history to a `## History` footer or to `audits/`.

---

## 5. Test assessment (tests/meetings/ targeting the manager)

- **Volume/health:** 23 files, 24k lines, 995 tests, 15 s (helpers extracted in 19.27, good). `test_manager.py` alone is 7,152 lines / 237 tests — the test file has the same accretion disease as the module (classes named after tasks and audits: `TestCommittedBytes107FoldPins`, `TestSingleWitnessInformYieldOnCommittedBytes`, `TestBallotTargetGuardSeed12Pin`).
- **Behaviour vs implementation:** the majority are behavioural and good (chain termination, opt-in ordering, fail-soft, provider-timeout distinction, teammate firewall on the production path, redirect/citation gate on the production path, defaults surfaced, redaction provenance). Weak spots: (a) 3 vacuous tally tests (P2-6); (b) ~15 tests pin dead resolvers and carry inverted names/docstrings (P1-3); (c) source-text/signature pins (P2-10); (d) several "committed-bytes" classes read `replays/samples` and pin corpus counts (`_TOTAL_MEETINGS = 707`, "fourteen of the ninety-seven") — legitimate as regressions but they make a unit-test module depend on 60 MB of replays and on ml_corpus.
- **Coverage gaps I noticed:** no test that a content-valid turn survives arbitrary values in the discarded identity fields (it doesn't — P1-2); no test that a `report` description containing the emergency phrase is *not* an emergency (it is — P2-7); no test of the DTO round-trip when `run()` raises mid-meeting (ledger state); no property/fuzz test of the guard chain (mine found none, but the invariants are only asserted example-by-example).
- **The golden** (`test_prompt_byte_golden.py`) is the single most valuable test in the area and it is fast.

---

## 6. Recommendations (prioritised)

1. **Split `manager.py` into protocol / turn_guards / ballot_guards / belief_fold (+ move pure reductions to `transcript.py`)**, keeping a re-export shim; move `agents` imports to `belief_fold` only and re-point the import-linter contract. Byte-neutral. (P1-1)
2. **Retire dead levers and inert plumbing:** delete `roll_call_round_enabled`, `citation_gate_enabled`, `absence_prior_enabled`, `reporter_exculpation_enabled` call sites and `env` kwargs; drop the two no-op teammate backstops; drop `public_transcript` from the render contract; decide `sighting_records` (connect via a scheduled substrate re-record, or delete field + test file); fix/rename `TestRollCallOffPath` & friends. (P1-3)
3. **Separate the LLM-facing turn/ballot payload schemas from the record schemas** (`MeetingTurnPayload`, `VoteBallotPayload`; manager composes ids/speaker/kind). Prompt-version bump only. Also make the validation-default placeholder say "validation" not "missed deadline". (P1-2, P2-11)
4. **Prose diet:** cap per-symbol docstrings at what a new reader needs *now*; move task/audit provenance to `audits/` or a footer; fix the stale `_collect_vote` / `tally_votes` references. Target ≤ 40% prose. (P1-4)
5. **Sync DESIGN.md §5.2 with the code:** add the roll-call round (and its cost), mark voting as sequential (or add the concurrency knob and keep "parallel"), restate opt-in as ordering, and note the guard chain. Consider a distinct `turn_kind="roll_call"` at the next re-record so transcripts can tell the two apart. (P2-5, P2-13)
6. **Give `MeetingTrigger` a structured `kind`** from the engine event; delete substring detection in the manager and pass `is_emergency` to templates. (P2-7)
7. **Fix the vacuous tally tests** by adding `vote_reason_ids` (as `test_eject_on_plurality` already does) and add a guard-chain hypothesis test (the probe in scratch is a starting point). Replace the source-grep parity assertions with the behavioural ones the same file already has. (P2-6, P2-10)
8. **De-duplicate:** use `voting.normalize_ballot_target`/`SKIP_TARGET` in the manager; use `_render_gate_value` for `rendered_vote_max`; fold the three turn loops in `run()` into one helper. (P2-8)

---

Full report: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/reports/B/meetings-manager.md`
