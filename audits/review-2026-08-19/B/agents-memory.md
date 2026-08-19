# Code review — `agents/memory/` (label: agents-memory)

Scope: `agents/memory/{episodic,working,beliefs,store}.py` (4,178 lines; ~1,600 of them code) plus
`tests/agents/test_{memory,memory_store,memory_rendering,memory_meeting_history,beliefs,
beliefs_hard_evidence_gate,beliefs_provenance,beliefs_wiring,reported_testimony,episodic_ids,
absence_prior}.py` (11,320 lines, 413 tests). Read-only; branch `main` @ b809b19c.
Machine load during timings: `uptime` load 5.6–8.9 on 10 cores (other reviewers running).

Evidence scripts (all under the scratchpad, none in the repo):
`work/agents-memory/{profile_game.py, replay_survival.py, replay_sections.py, bench_scan.py,
fuzz_probe.py, repro_last_seen.py, repro_alibi_dup.py}`.

---

## 1. Executive read (10 lines)

1. The core model is sound and small: an append-only typed event log with a monotonic-tick guard and
   deterministic `{agent}:{tick}:{seq}` ids, pure copy-and-return belief folds iterated in sorted order,
   and a deterministic salience-sorted, token-budgeted renderer. mypy --strict and ruff are clean [VERIFIED].
2. Random probes (300 renders / 500 belief write sequences) found zero violations of the two documented
   invariants (render ≤ budget whenever the elastic block is present; `0.5 + provenance.total == suspicion`)
   and zero render non-idempotency [VERIFIED].
3. The area is buried under history: beliefs.py is 1,964 lines of which ~480 are code (64% docstring/comment);
   `apply_meeting_evidence_rules` has a 210-line docstring, 14 keyword params and cyclomatic complexity 54 (radon F).
   116 "Task N.N" references and 41 "audit" references in one file [VERIFIED].
4. Five "retired" lever resolvers (`*_enabled(env)` → `del env; return True`), five dead `ENV_*` constants,
   and an `env` kwarg threaded through 4 public functions + orchestrator/meetings call sites survive purely as
   provenance; 49 test assertions pin `f(...) is True` [VERIFIED].
5. Real defect: the belief-line "last seen in ROOM at tick T" is fed only from `saw_player_move` rows, so it can
   contradict a newer `saw_player` line in the same prompt (repro below) [VERIFIED, P1].
6. Real design consequence: reported testimony (salience 25) is shed wholesale once a render has >100 candidate
   observations — on 60 committed 9p2i replays, 0/4150 reported rows survive in renders with >150 candidates and
   only 12% in the 101–150 bucket; the "testimony as content" lever is structurally starved in exactly the long
   games where later meetings happen [VERIFIED, P1-design].
7. Half the belief model is dead in production: `trust` is never written, `record_contradiction` never lands on the
   persistent store, so `## Open contradictions` rendered in 0/1,656 replay renders and `trust` lines in 0/1,656 [VERIFIED].
8. `WorkingMemory` is a leaky abstraction: `goal`/`path` have zero production writers ("scaffolding, NOT dead code to
   delete" says the docstring), and `last_seen` is a render-time cache written *by the renderer* to satisfy an audit
   gate ("render reads all three stores"); the ML feature encoder had to re-derive it and merge [VERIFIED].
9. `MemoryStore.recent(since_tick)` is a linear filter despite the enforced tick ordering; 13 full-log passes per
   render, 3 per perception tick — O(T²) growth per agent, latent (games are ~30 ticks) but measurable [VERIFIED, P2].
10. Rendered bytes are frozen by the prompt-byte golden against committed real-LLM baselines, so every render fix
    (incl. #5) costs a baseline re-record — the biggest architectural drag on this module.

---

## 2. Findings (ranked)

### F1 [P1][VERIFIED] Belief-line "last seen" contradicts the observation list
- `agents/memory/store.py:1536-1590` (`_record_movement_sightings`) fills `WorkingMemory.last_seen` ONLY from
  `saw_player_move` rows; ordinary `saw_player` rows never update it. `_build_belief_lines` (store.py:1655) then
  renders "last seen in X at tick T" from that.
- Repro (`repro_last_seen.py`): move p-3→ADMIN witnessed at tick 5, then p-3 seen standing in STORAGE at tick 20:
  ```
  - [obs p-1:5:1] [tick 5] You saw p-3 move from CAFETERIA to ADMIN.
  - [obs p-1:20:1] [tick 20] You saw p-3 in STORAGE.
  ## Your current beliefs:
  - p-3: suspicion 0.70 (last seen in ADMIN at tick 5)
  ```
  The prompt asserts two incompatible "last seen" facts. `agents/tactical/features.py:485-505`
  (`_combined_last_seen`) already papers over this by re-deriving last-seen from `saw_player` AND `saw_player_move`
  and taking the max — the encoder knows the working-memory value is stale.
- Why it matters: this is the one place the belief block gives the model a location fact; it is wrong whenever a
  subject was seen after its last witnessed transit (the common case). Confidence: high.
- Note: fixing it changes render bytes → prompt-byte golden + committed baseline re-record (see §3).

### F2 [P1-design][VERIFIED] Reported testimony is starved by the salience band in long games
- `store.py:85` `_SALIENCE_REPORTED_TESTIMONY = 25` sits below every first-hand row (`saw_player`=50, move=52,
  transition=48, completed task=30). `_select_within_budget` (store.py:1854) keeps a strict salience-ordered
  prefix at `DEFAULT_TOKEN_BUDGET=1500` (~80 lines).
- Measurement over 60 committed `replays/ml_corpus/9p2i` games via `ReplayLoader._walk(collect_memory=True)`,
  1,656 renders (`replay_survival.py`):
  ```
  class        kept/total     ≤60 cand.   61–100      101–150     >150
  reported     14618/26297    5481/5481   8419/10780  718/5886    0/4150
  transition    6242/7576     3017/3017   2475/2484   722/1273    28/802
  task (own)    1401/1495      734/734     545/549    122/160     0/52
  saw          29914/33526   13781/13781 9599/9601   4807/5294   1727/4850
  ```
  In 166 of the 835 renders that had reported rows, ALL of them were shed. Min-salience-kept histogram:
  {10: 193, 25: 665, 30: 384, 48: 234, 50: 168, 52: 12}.
- Why it matters: `absorb_reported_testimony` (Task 13.5.2) exists to make "social info content, not a scalar";
  the docstring even calls the band ordering "load-bearing". But its effect is inversely proportional to how much
  the agent has seen — the later the meeting, the less testimony reaches the model — and the agent's own
  completed-task alibi (salience 30) is likewise gone in long games (0/52). Whether the *ordering* is right is a
  gameplay call (other track); that the lever silently no-ops in the regime it targets is a code/design fact.
- Also [JUDGMENT]: within a band the sort is `(-tick, line)`; all reported rows share the boundary tick, so the
  tie-break is alphabetical by "CLAIM by p-N" — arbitrary, not by claim relevance or recency.

### F3 [P2][VERIFIED] Dead halves of the belief model still rendered/tested/documented
- `BeliefState.adjust_trust` (beliefs.py:1111): zero production callers (grep over agents/orchestrator/meetings/
  eval/api/training). `trust` is always 0.5, so `_format_belief_score`'s trust branch (store.py:1712-1732) is dead.
- `record_contradiction` (beliefs.py:1149) is called only inside `apply_contradiction_rule`, whose result is a
  TRANSIENT vote-time state (`meetings/manager.py:2455-2470` seeds a fresh `BeliefState` from the suspicion graph);
  it is never loaded back into `memory.beliefs`. So `PlayerBelief.inconsistencies` and `_build_contradiction_lines`
  (store.py:1741, with its roster filter + dedup) are dead in production.
- Evidence (`replay_sections.py`, 1,656 renders): `has_contradictions_section=0`, `has_trust_line=0`,
  `store_has_inconsistencies=0`, `store_has_trust_dev=0`.
- DESIGN.md §6.6 still shows `p1: trust 0.70` and an `## Open contradictions:` block as the canonical render;
  §6.4 says "the detector runs … on the local belief state when memory is updated" — not implemented.

### F4 [P2][VERIFIED] Retired levers, dead `env` plumbing, tautology tests
- `beliefs.py:190,224,292,407` and `store.py:189`: five `*_enabled(env)` resolvers that `del env; return True`,
  each with a 15–25 line docstring; five `ENV_*` constants "retained (no longer read)". The `env` kwarg is still
  threaded through `render_for_prompt`, `_build_belief_lines`, `apply_contradiction_rule`,
  `apply_meeting_evidence_rules`, and callers in `orchestrator/game.py:2713`, `meetings/manager.py:1759,2448`.
- Dead branches guarded by them: `if lift_enabled:` (beliefs.py:1499), `ceil_lift = phase == "pre_vote" and
  evidence_quality_lift_enabled(env)` (1783), `gate_on` (store.py:1631), `ids_on` (store.py:270).
- Tests: 49 assertions of the form `*_enabled(...) is True` across the area (e.g. test_absence_prior.py:183-201,
  test_beliefs_hard_evidence_gate.py:96-108, test_episodic_ids.py:384-420). They pin a constant.

### F5 [P2][VERIFIED] `WorkingMemory` is scaffolding + a render-time cache
- `working.py:38-118`: `set_goal/clear_goal/set_path/clear_path/Goal` have zero non-test callers (11 references,
  all in tests/agents/test_memory.py). The module docstring itself says "zero non-test callers, NOT dead code to
  delete" — a comment defending dead code.
- `last_seen` is written by the RENDERER (`store.py:307-313` → `_record_movement_sightings`) — a read path with a
  write side effect, justified by "the R-6 composite-memory gate: render reads all three stores". The value is a
  cache of a subset of episodic rows (see F1). DESIGN.md §6.1 says working memory is "rebuilt each tick"; it is
  instantiated once and never rebuilt.

### F6 [P2][VERIFIED] Linear scans over the whole log; O(T²) per agent
- `episodic.py:119-122` `recent()` filters the entire list even though `append` enforces non-decreasing ticks;
  `recent(since_tick=0)` is used as the de-facto "all events" accessor at 29 production sites (13 in store.py).
  `render_for_prompt` makes ~13 full passes (`_latest_role`, `_latest_self_state_tick`, `_latest_self_guard_fields`
  each scan for fields of the SAME latest self_state row; `_collect_body_sightings` computed twice; two passes in
  `_collect_transitions`). `ingest_packet` (perception.py:141,284,315) does 3 full scans per tick.
- Bench (`bench_scan.py`, load 5.6): `recent(last_tick)` = 4.6 µs @400 events, 100.6 µs @8,000 events
  (bisect equivalent: 0.3 µs); `render_for_prompt` = 1.3 ms @400, 27.6 ms @8,000. Replay walk of 60 committed
  games: 63k `recent` calls, 5.8M rows scanned, total render 0.65 s. Not a live problem (games are ~30 ticks,
  stores ≤ ~500 rows) — latent, and it also blocks a cheap "last N ticks" API.

### F7 [P2][VERIFIED] Alibi suffix duplicates and loses the window
- `store.py:1684-1709` `_format_alibi_suffix` sorts twice (`ordered = sorted(...)`, then
  `sorted(ordered, key=same)[-3:]` — the second sort is redundant). `record_alibi` never dedups, so a restated
  alibi renders twice and, with the cap of 3, can crowd out others. Repro (`repro_alibi_dup.py`):
  `- p-3: alibi: in STORAGE at tick 0 per p-2; in STORAGE at tick 0 per p-2`.
- `absorb_reported_testimony` (store.py:533-546) stores only `from_tick`; the alibi WINDOW (`to_tick`) is lost in
  the belief `AlibiClaim`, so the belief line says "at tick 0" for a claim of "ticks 0–1". The docstring's
  "most-recent alibi supersedes" sorts by CLAIMED tick, not by when it was claimed.
- Also: `room=statement.room if ... else ""` (store.py:544) would render "in  at tick" — unreachable in production
  (schema `AlibiClaim.room` is required) but defensive-dead.

### F8 [P2][JUDGMENT] Reported-testimony line prefix is misleading
- `_render_reported_testimony` (store.py:1458) emits `[tick 42] [meeting] CLAIM by p-2 (unverified): saw p-3 in
  ADMIN @ tick 12` where `[tick 42]` is the meeting-fold tick (resume tick), not the claim's. Documented as
  intentional, but for the model it reads as two ticks per line and every reported line in a meeting shares the
  same leading tick. Also `[obs p-1:5:1] [tick 5]` double-bracket prefix on every first-hand line (16 chars ≈ 4
  tokens per line, ~25% of an 80-line render's budget) — a cost the budget arithmetic charges.

### F9 [P2][VERIFIED] Docs drift (DESIGN.md §6 vs code)
- §6.1 "HEAD status" note (itself a truth-up) is stale on three counts: says `WorkingMemory.record_sighting` "is
  uncalled" (it is called at render time), says goal/path are "written by the tactical policy" (zero writers),
  says testimony-as-content is gated on `AILIBI_TESTIMONY_AS_CONTENT` default OFF (retired; only the top banner
  corrects this).
- §6.5 "persisted alongside replay log as JSONL" — episodic memory is never persisted; it is reconstructed by
  replaying (no `episodic` in `orchestrator/replay.py`).
- §6.6 "realistic budgets (8k–16k tokens)" — production `DEFAULT_TOKEN_BUDGET = 1500` everywhere
  (`build_default_meeting_runner`); signature shown as `render_for_prompt(meeting_id)`.
- §6.2 stage-1 coalescing "NOT IMPLEMENTED" is honest; §6.4 local-belief contradiction detection is not.
- `docs/architecture.md:46` is accurate at its altitude.
- Cross-track note [JUDGMENT]: prompts (`crewmate_report.j2:96,110`) ask the agent to answer roll-call "copied from
  your own record", but the render has no "you were in ROOM at tick T" line — own location is only implicit in
  "You saw X in ROOM" (absent when alone) and in completed-task lines (salience 30, shed in long games).

### F10 [P2][JUDGMENT] Complexity hot spots
- `apply_meeting_evidence_rules` (beliefs.py:1518-1929): 402 lines, 210-line docstring, 14 kwargs, CC 54 (radon F),
  three phases × four caps × three guards in one loop body. `_build_observations` CC 32; `_collect_transitions` CC 24.
- Parameter plumbing: `own_agent_id=…, teammate_ids=…, body_sightings=…` repeated 12–13× through six store
  helpers to reach `_sighting_is_suppressed` — a `_SuppressionContext` frozen dataclass would delete ~40 lines.
- The `meeting_boundary` marker (store.py:110, appended by `absorb_meeting_evidence`) is a render hint stored as an
  "inferred" memory event — mixing renderer state into the log; it exists because `_collect_transitions` cannot
  otherwise see the boundary.

### What is GOOD [VERIFIED unless noted]
- `episodic.py`: 122 lines, does exactly one thing; monotonic-tick guard and duplicate-id guard fail loud; ids are
  content-free coordinates (replay-safe by construction).
- Fold functions are pure (copy → mutate copy → return), iterate `sorted(...)`, and the manager/orchestrator adopt
  results via `load_from` — determinism is structural, not incidental. Fuzz: 0 provenance-invariant violations.
- Renderer: stable `(−salience, −tick, line)` sort, ceiling-division token estimate charged on the exact bytes
  including separators; fuzz: 0 budget violations, 0 non-idempotent renders. Golden fixtures + a leak scanner run
  over the rendered view (test_memory_rendering.py:37) hold the render to the packet anti-leak invariants.
- `_sighting_is_suppressed` is a single source of truth for the §4.7 team firewall shared by sighting / co-presence /
  transitions / move / last-seen; roster filtering is applied on both the input and the store side (self-healing).
- `SuspicionProvenance` is a clean frozen value type; hard/soft split survives decay and carry by construction.
- `MeetingHistory` (working.py:121) is a small, honest channel with the same guard style as its siblings.
- Tests mostly drive public API (only `store._estimate_tokens` / `store._build_belief_lines` are touched directly),
  and boundary tables are asserted "quantize-then-compare" on the rendered `%.2f` grid, which is the right way to
  pin float thresholds.

---

## 3. Architecture / design assessment

**Well designed.** The three-layer split (raw typed log → derived beliefs → budgeted render) matches DESIGN §6 and
is the right shape. Determinism is designed in at every layer (sorted iteration, stable sorts, coordinate ids,
pure folds), which is what makes byte-identical replay reconstruction and the prompt-byte golden possible at all.
The firewall suppression being a single predicate reused by every render surface is a good example of "one source
of truth" done properly.

**Accidental complexity (in order of cost).**
1. *History as code.* ~64% of beliefs.py and ~37% of store.py is prose that narrates which task/audit/Codex review
   introduced each line, often three times (constant docstring, function docstring, inline comment). Five retired
   levers keep functions, constants, kwargs and 49 tests alive to document that they once existed. The
   documentation should live in `audits/` (it already does); the code should carry the invariant, not the story.
2. *The renderer as the integration point.* Because an audit gate said "render reads all three stores", the render
   grew a write path into WorkingMemory (F5) and a marker event into the episodic log (F10), and WorkingMemory's
   `last_seen` became a stale cache (F1). The honest model is: episodic is the only store; beliefs are derived state
   the folds own; "working memory" as a concept has no production consumer and should be deleted or made a real
   per-tick scratchpad the tactical policies use.
3. *One fold to rule them all.* `apply_meeting_evidence_rules` accreted every per-phase cap and guard behind
   14 kwargs. It should be two small functions (`fold_pre_vote`, `fold_post_meeting`) each ~40 lines, plus a
   `SoftLiftPolicy` value (ceiling, reporter cap, absence delta) — the "one function, phase argument, never
   duplicated logic" rule in its docstring is what produced CC 54.
4. *Frozen bytes.* The prompt-byte golden + committed baseline replays pin every render byte, so F1/F2/F7/F8 fixes
   are gated on a real-LLM re-record. That is a legitimate doctrine for *substrate* changes, but it also freezes
   pure legibility bugs. Consider decoupling: a render-version stamp in the replay (already partly there via
   `_RETIRED_ALWAYS_ON_LEVERS`) so the loader can reconstruct old baselines with the old renderer while new games
   use the fixed one — otherwise every P2 render fix accrues to a phase gate.
5. *Linear `recent()`.* A `bisect` on ticks (or a parallel `_ticks` list) plus an explicit `all()`/`latest(type)`
   accessor removes 13 full passes per render and the O(T²) shape (F6).

**What I would refactor and how (no behaviour change first, byte-preserving):**
- Delete the five retired resolvers, `ENV_*` constants and the `env` kwargs; delete the tautology tests
  (~-400 lines code+docs, ~-49 tests). Byte-identical output.
- Delete `Goal/set_goal/set_path/clear_*` and their tests; rename `WorkingMemory` → `LastSeenCache` or fold it
  into a render-local dict (byte-identical as long as F1 is left as is).
- Collapse `_latest_role/_latest_self_state_tick/_latest_self_guard_fields` into one `_latest_self_state()`; pass a
  `_RenderContext(own_id, teammate_ids, body_sightings, breadcrumbs, co_presence)` instead of 3 kwargs × 13 sites.
- Move each constant's rationale to a single "belief weights" table docstring; cut function docstrings to the
  contract (inputs, outputs, invariants) and a one-line pointer to the audit.
- Then, as a substrate change (re-record): fix F1 (derive last-seen from both row types), fix F7 (dedup alibis,
  keep the window), and revisit F2's band or budget.

---

## 4. Test assessment

- Volume: 11,320 test lines for ~1,600 code lines (≈7:1); 413 tests, 17.8 s [VERIFIED]. Coverage of the public
  surface is thorough (guards, boundary tables, goldens, leak-scan of the rendered view, replay-determinism pins).
- Behaviour vs implementation: mostly behaviour. Goldens pin bytes deliberately (replay contract). Weak spots:
  49 `*_enabled(...) is True` tautologies (F4); 11 tests for dead `set_goal/set_path` (F5); a 1,475-line file
  (`test_absence_prior.py`) for a single 0.08 delta whose lever is now unconditional; `test_beliefs.py` at 3,952
  lines mixes belief math with meeting-manager integration and eval-corpus re-derivation ("_rederived_rows",
  "_recorded_rows"), so a belief-constant change fans out into replay-corpus assertions.
- Missing tests (evidence: this review found them by probing): last-seen consistency between observation lines and
  belief lines (F1); reported-row survival at realistic candidate counts (F2 — the only budget test uses a
  4-line fixture at `token_budget=40`); alibi dedup across meetings (F7); any test that `Open contradictions` or
  `trust` can occur in production (F3 — nothing asserts they can, and nothing notices they never do).
- Fixture goldens (`tests/fixtures/memory_rendering/*.expected.md`) are small and readable — good.

---

## 5. Recommendations (prioritized)

1. **Fix F1 (last-seen from all sighting rows)** as part of the next substrate re-record; add a test asserting the
   belief-line last-seen equals the max-tick sighting in the rendered observations. (P1)
2. **Decide F2 explicitly**: either raise reported-testimony (and own completed-task) salience into/above the
   sighting band, or budget the elastic block per class (e.g. reserve N lines for reported rows), or raise the
   budget. Add a regression test that renders a 150-candidate store and asserts ≥1 reported row survives. Measure
   with `replay_survival.py` before/after. (P1-design; gameplay track to weigh the ordering)
3. **Delete the retired levers, `env` plumbing and tautology tests** (F4) — byte-identical, no re-record. (P2, cheap, big readability win)
4. **Prune docstrings/comments to contracts + one audit pointer**; move history to `audits/`. Target: beliefs.py
   < 900 lines, store.py < 1,300 lines with no behaviour change. (P2)
5. **Delete `WorkingMemory` scaffolding and the trust/contradiction render paths, or wire them** (F3, F5); update
   DESIGN §6.1/§6.4/§6.6 to the real model (F9). (P2)
6. **`MemoryStore`: bisect-based `recent()`, add `all()`/`latest(type)`; single self-state scan in the renderer** (F6). (P2)
7. **Split `apply_meeting_evidence_rules`** into pre-vote / post-meeting folds with a small policy value; add a
   `_RenderContext` in store.py to kill the 13× triple-kwarg plumbing (F10). (P2)
8. **Consider a render-version stamp** so legibility fixes to the renderer don't require re-recording every
   committed baseline (architecture §3.4). (P2, design decision for the owner)
