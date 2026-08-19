# Code-track adversarial verification verdicts (14 claims)

VERDICT: **CONFIRMED** (all sub-claims held; one framing correction on `training/env.py`).

**Decisive evidence** — repro at `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-C-1/repro.py`, `repro2.py`, `repro3.py` (load avg 3.41):
```
after vent: ['VentEntered','TickAdvanced'] in_vent= True room= ADMIN
KILL events: ['Killed','TickAdvanced']
p-1 alive: False | killer in_vent: True
REPORT events: ['MeetingTriggered'] phase: MEETING killer in_vent: True
SABOTAGE events: ['SabotageStarted','TickAdvanced'] killer in_vent: True
--- repro2 (witness co-located) ---
Killed.witnesses = ('p-2',) | killer in_vent = True
p-2 visible_players: [('p-3','ADMIN','kill')]      # a VENTED player in visible_players
--- repro3 (RL mask) ---
vented impostor sees: [('p-1','ADMIN')] in_vent: True
ENGINE-LEGAL while vented: ['kill','sabotage','vent','wait']
```
Code path, read in full: `engine/rules.py:56 resolve_kill` (checks role, target-role, cooldown, same-room — no `in_vent`), `:182 resolve_report` (body-room only), `:225 resolve_sabotage` (role + not-already-active). Contrast the four that *do* guard: `engine/tick.py:243` move, `:280` do_task, `engine/rules.py:209` emergency, `:254` repair. `engine/visibility.py:78` hides the vented from others but never restricts a vented *observer* → invisible + full sight, as claimed.

**Refutation attempts that failed:** (a) no orchestrator/agent-boundary guard (`grep -rn in_vent orchestrator/` → only `seeder.py:186`); (b) no existing test covers it — `tests/engine/test_tick.py` has vent tests at :941–1025 and `test_emergency_rejects_actor_in_vent():1158`, but nothing for kill/report/sabotage; (c) no design ruling — `DESIGN.md:334` lists kill preconditions as role, crew-target, same room, cooldown 0, and `:336` says nothing about acting while vented, so this is an unruled gap, not an intentional mechanic.

**Framing correction:** `training/env.py:288-296` is *not* an independent defect. Its docstring (`env.py:212-223`) declares it "a faithful mirror the property test pins against the real engine", and `tests/training/test_env.py:340 test_mask_legality_against_engine` asserts every masked-legal intent is engine-accepted. Adding `not in_vent` to the mask alone would fail that test. The defect is single-sourced in `engine/rules.py`; the mask is downstream.

**Committed replays unaffected — confirmed.** `agents/tactical/impostor_policy.py:304` (`if in_vent: return self._vent_exit(...)`) is the highest-priority branch, above all kill/body/sabotage logic; `agents/tactical/learned/forward.py:323-329` likewise emits ONLY exit options when `in_vent`. So no shipped FSM/ES policy can emit it today.

**Secondary finding (new):** `observation/service.py:365-372` unconditionally adds any actor in `observed_actions` to `visible_players`, so a vented killer surfaces as `('p-3','ADMIN','kill')` — the "vented players are invisible" invariant (`engine/visibility.py:78`) is not total. Defensible as intended kill-attribution, but undocumented and it means `visible_players` is not a pure vision output. P2.

**Corrected severity: P1** (was implicitly higher). Not P0: no shipped policy reaches it, no committed replay or eval number is wrong, no security/data-loss dimension. But it is a real engine-rule defect that inverts the project's own stated principle — `engine/rules.py:60-66` argues, for the friendly-fire guard, that "a buggy or future LLM-driven policy must not be able to" break the rule, and `DESIGN.md:359` makes the engine the single source of truth. The identical argument was simply not applied to `in_vent`, leaving rule enforcement load-bearing on agent code.

**Real-world impact:** Today it is latent — the FSM and ES option menus both short-circuit on `in_vent`, so no committed replay, eval, or ES artifact is contaminated. The risk is forward-facing and concentrated in `training/`: the RL/surrogate action mask *actively advertises* `kill` and `sabotage` as engine-legal from inside a vent, so the next learned policy that samples the mask rather than the hand-written option menu can discover a strictly dominant, untraceable strategy (never appear in anyone's `visible_players`, retain full sight, kill on cooldown, then open the meeting yourself), silently invalidating any impostor-side balance measurement taken with it. Fix belongs in `engine/rules.py` (three `if actor.in_vent: raise ActionRejectedError(...)` guards, matching `:209`/`:254`), after which `training/env.py`'s mask should be updated in the same change to keep `test_mask_legality_against_engine` green.

---

**VERDICT: CONFIRMED** (P1)

**Code path.** `engine/visibility.py:83-94` `_visible_body_ids` filters `body.room in visible_room_set`; `:64-80` `_visible_player_ids` filters room + `not player.in_vent`. `observation/service.py:298-303` copies `visibility.visible_body_ids` verbatim into `BodyView`s. The scanner signature is `eval/leak_scan.py:609-611`:
```python
def assert_packet_is_leak_clean(
    packet: ObservationPacket, engine_events: Sequence[EngineEvent] = ()
) -> None:
```
No `WorldState`, no `Map`, no `VisibilityResult` — so it structurally *cannot* recompute what the observer was entitled to see. Its body check (`:642-645`) is a key-set pin `{"id","room","victim_id"}` only. `visible_players` gets a witness-permission cross-check for `kill`/`vent` actions (`:626-637`), but nothing checks *presence*.

**M6 repro** (scratch copy at `.../scratchpad/work/verify-C-31/repo`, `_visible_body_ids` returns every undiscovered body, room filter dropped):
```
77 passed in 6.27s   # eval/leak_test.py + tests/observation/test_service.py
                     # + tests/observation/test_leak_property.py + tests/test_firewall.py
```
The mutation is not a no-op — instrumenting `collect_factory_packet_records` (the exact walker `scan_factory_packets` uses):
```
BASELINE: packets=534 body_views=33  cross_room_body_views=7
M6:       packets=564 body_views=249 cross_room_body_views=222
```
Every crewmate is handed the map-wide corpse ledger and all four suites are silent. Whole-suite delta (tests/ + eval/, api/scripts/training excluded — corpus-dependent, equally broken in baseline): `comm -23 m6_full.txt base_full.txt` → **empty**. Zero tests in the repo catch M6.

**M1** (`visible_player_ids` := all alive): `eval/leak_test.py 19 passed`, `test_leak_property.py 6 passed`, `test_firewall.py 9 passed`; caught only by `tests/observation/test_service.py` (2 tests). **M10** (vent filter dropped alone): `eval/leak_test.py 19 passed`, leak_property + firewall pass; caught only by `test_service.py::test_vented_player_is_hidden_without_same_tick_event`. So the claim's per-suite bite table reproduces exactly. (M14 not independently re-derived — mutation site unspecified; the other three carry the claim.)

**Blast radius is real, not hypothetical.** `scan_factory_packets` is the leak gate the ML champion path runs outside pytest: `training/crew/scorer.py:1735` and `training/bakeoff/harness.py:1828`. `DESIGN.md:933` titles §11.2 "Information-leakage test (the most important test)". Note DESIGN's own sketch is field-name oriented (`assert "role" not in visible.dict()`), so this is design-consistent rather than a violated ruling — but §11.2 also asks for a version that asserts "no field whose value should be hidden ever appears", which a presence check is required to deliver.

**Corrected severity: P1** (not P0 — no live leak exists today; `engine/visibility.py` is correct on main, and `tests/observation/test_service.py` does pin the *player*-side room/vent rules with hand-built world states). The defect is gate coverage: the leak firewall's most-advertised, ML-gate-wired scanner validates packet *shape* and *string content*, never packet *entitlement*, so the entire body-visibility axis and (in the three suites other than `test_service.py`) the player-visibility axis are unguarded. A refactor of `_visible_body_ids` — or a learned-agent path that reaches bodies differently — would ship a total hidden-information leak green. The cheap fix: give the scanner the `VisibilityResult`/`WorldState` and assert `set(packet.visible_bodies ids) == set(visibility.visible_body_ids)` recomputed independently, or at minimum assert every `BodyView.room` lies in `visible_rooms_for_player`.

Full report: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-C-31/` (repro copy, `count_bodies.py`, `m6_full.txt`, `base_full.txt`, `visibility_m6.py`). Repo untouched — `git status --porcelain` empty. Load at measurement: `load averages: 4.95 5.04 5.43`.

---

**VERDICT: CONFIRMED** [VERIFIED] — high confidence. Severity corrected P2 → **P1**.

**Decisive evidence.** Scratch copy of HEAD (`git archive`, repo untouched), planted `agents/_probe_orch.py` containing `import orchestrator.game` / `import api.main` / `import eval.leak_scan`:

```
Analyzed 90 files, 379 dependencies.
Agents must not import engine KEPT
Agents must not import training KEPT
Agents must not import meetings.manager KEPT
Observation must not import agents, meetings, or llm KEPT
Contracts: 4 kept, 0 broken.
```
Clean baseline: `Analyzed 89 files, 379 dependencies.` — so the probe *was* parsed (89→90) and still passed. Rest of the gate on the same probe: `pytest tests/test_firewall.py tests/observation -q` → **72 passed**; `ruff check` → `All checks passed!`. `scripts/check.sh:15-21` is fully green on an `agents/` module that transitively pulls in `engine`.

**Mechanism.** `.importlinter:2-9` lists `agents, engine, llm, meetings, observation, training`; `orchestrator`/`api`/`eval`/`scripts`/`experiments` are absent and `include_external_packages` is unset, so grimp builds no nodes for them and the traversal dies at the first hop. `orchestrator/game.py:71-81` imports `engine.{actions,entities,events,rng,rules,tick,world}`; `eval/leak_scan.py:38-47` and `api/*` likewise.

**Refutation attempts, all failed.**
1. *Existing test?* Only `tests/test_firewall.py:167-174`, which bans `orchestrator` (not `api`/`eval`) and rglobs **only** `agents/tactical/learned/`. Copying the probe there DID fail: `offenders: [(.../learned/_probe2.py, ['orchestrator'])]`. At `agents/` top level nothing fires — the repo-wide scan at `tests/test_firewall.py:90` bans only `{"numpy","torch"}`.
2. *Transitive contract?* `test_agents_cannot_reach_engine_through_observation` (`tests/test_firewall.py:40`) plants through `observation` — a *root* package. Transitivity holds only inside the 6 roots.
3. *Design ruling?* `orchestrator/game.py:12-20` rules on *direction* (privileged modules may import engine), never on the `agents -> privileged -> engine` back-channel.

**Coverage numbers** [VERIFIED]: root-package `.py` = **89**; tracked non-test `.py` = **199**; all tracked `.py` = **383**. Uncovered non-test: `experiments` 49, `eval` 25, `scripts` 18, `orchestrator` 8, `api` 8.

**Doc drift.** `README.md:74` claims agents cannot import engine "directly or transitively (import-linter enforced)" — true only for hops via the 6 roots. `README.md:47`, `docs/architecture.md:106`, `docs/reading-guide.md:30` repeat "enforced by tooling / four contracts" uncaveated. `DESIGN.md:119` cites a pre-commit hook; no `.pre-commit-config.yaml` exists.

**Real-world impact.** No live violation exists today, so nothing is currently broken — hence P1, not P0. But the project's loudest architectural claim and its "zero observation-firewall violations" record rest on a contract that a single import through `orchestrator`, `api` or `eval` slips past with the whole gate green. Since agent authors work from contracts citing that README framing, an accidental privileged import in `agents/` would land unnoticed and silently void the firewall.

**Credit where due.** The blind spot is known and written down in-repo at `tests/test_firewall.py:162-166`; all four existing contracts are plant-tested ("a gate that cannot fail is not a gate", `tests/test_firewall.py:141`); `orchestrator/game.py:23-25` retracts a now-false claim in a "Historical note" rather than leaving stale prose. Cheapest fix: add the four dirs to `root_packages`, or widen the repo-wide scan at `tests/test_firewall.py:90` using the machinery already at `:167`.

Full report: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-C-32/report-C-32.md`

---

**VERDICT: CONFIRMED**

**Code path (read in full)**
- `engine/maps/canonical_1.yaml:45` — `dead_task_rule: redistribute` is the canonical default (flipped from `drop` by Task 13.12).
- `engine/tick.py:400-405` → `engine/tick.py:314-367 redistribute_dead_tasks` — re-keys the victim's incomplete instances onto the lowest-id living crewmate: `surviving_tasks[f"{recipient}:{map_task_id}"] = replace(task, ...)`. The recipient's owned set **grows**.
- `observation/service.py:638-645` — `pending_task_id = sorted(owned_unfinished_map_ids)[0]`. A newly gifted id that sorts *before* the current pending silently replaces it.
- `agents/memory/store.py:1157-1200` — the inference, under the comment *"Its owned set only ever shrinks -- a task completes; none is added mid-game -- so the pending id changes if and only if the previous pending task completed"*. That premise is now false. Gated to `role == "CREWMATE"` (the 10.14 impostor fix), which is exactly the population redistribution targets.
- `agents/perception.py:354-361` — `_self_state_payload` returns only `agent_id/room/role/pending_task_id/fellow_impostor_ids/in_vent`. `owned_task_ids` exists on `SelfView` (`observation/packet.py:73`) but is **not** recorded, so the store genuinely cannot see the set. Cross-check confirmed.

**Decisive repro** (`/private/tmp/.../scratchpad/work/verify-C-2/repro.py`, real engine + ObservationService + ingest + render):
```
PRE-KILL  p-2 pending = upload_logs | owned = ('upload_logs',)
post-kill tasks       = ['p-2:align_engine_output', 'p-2:upload_logs']
POST-KILL p-2 pending = align_engine_output | owned = ('align_engine_output','upload_logs')
---- rendered memory ----
  ## Tasks completed (global): 0 / 2
  - [obs p-2:0:1] [tick 0] You completed upload_logs (you were in ADMIN).
FABRICATED: True
```
p-2 never acted. The prompt is self-contradictory: global counter 0/2 while first-hand memory claims a completion, and the line carries an `observation_id`, i.e. it is **citable** as evidence.

**Scope / rate.** Conditional on lexicographic order: `repro_after.py` (gifted `upload_logs` vs pending `align_engine_output`) → `FABRICATED: False`. Independent 4-seed 9p/2i FSM measurement (`rate.py`, no meetings, 400-tick cap; load avg 4.4–5.0): `kills=5 owned-growth=5 real=14 fabricated=3` — ~3/5 growth events fabricate, ~18% of all rendered completion lines. Different absolutes than the claim's 4/43 over 16 kills (my loop has no meetings), same qualitative result.

**Tests / docs.** No test covers it; `tests/agents/test_memory_rendering.py:834-851 test_pending_rollover_to_next_map_id_emits_completion` actively **pins** the any-change-emits rule, enshrining the mechanism. `DESIGN.md` §3.5 documents only the `drop` rule — `grep -rn redistribute DESIGN.md` returns nothing, despite `engine/tick.py:322` citing "DESIGN.md §3.5, redistribute variant". No design ruling anywhere sanctions the interaction; `tasks/phase-13.md:442-464` flipped the flag without touching the inference.

**Corrected severity: P1** (borderline P0 for evidence integrity), confidence high.

**Impact.** A crewmate's *first-hand* memory — the one channel the design treats as ground truth — gains a false, id-stamped "You completed X (you were in ROOM)" row, and the report prompts instruct agents to quote their own `completed_task` rows verbatim as alibi evidence (`agents/strategic/prompts/qwen3_6_27b/crewmate_report.j2:107-112`). So an innocent crewmate can emit a structurally-valid but factually false alibi and be contradicted by other agents' honest testimony. The same rows feed eval/ML features derived from rendered memory, so the corruption is silently baked into recorded baselines. The store's own comment names this exact failure ("corrupt the meeting/eval evidence") when justifying the impostor gate — the fix it applied is now incomplete for crewmates.

Repro files: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-C-2/{repro.py,repro_after.py,rate.py}`

---

VERDICT: **CONFIRMED** — and the claim is *understated*, not overstated.

**Decisive evidence.** `_scored_targets` (`agents/tactical/impostor_policy.py:937-1008`) has **no proximity term**: `score = isolation * (1 - witness_risk) * (cooldown == 0)`, sorted `(-score, player_id)` at `:1008`. A victim in the impostor's own room and one seen alone in an adjacent room both score exactly `1.0` (and the impostor *does* see adjacent rooms — `engine/visibility.py:98-127`, asymmetric visibility keeps `same_room_and_adjacent` for impostors). The kill seam then re-validates **only** `best = targets[0]` (`:353`, `:369-371`) and, on failure, walks toward `best.room` (`:385-387`).

Unit repro (`work/verify-C-3/repro_kill_ranking.py`), same inputs, ids swapped:
```
[A] ranking = [('p-2','ADMIN',0,1.0), ('p-5','CAFETERIA',0,1.0)] -> MoveIntent to_room='ADMIN'
[B] ids swapped                                                  -> KillIntent target='p-2'
[C] higher-ranked target's sighting is our OWN room              -> WaitIntent   (not even a move)
```

Population measurement (`work/verify-C-3/measure_missed_kills.py`) over all 50 committed 9p2i seeds, via `eval.replay_walk.walk_replay` with tick + meeting pre/post **state-hash verification**, rebuilding each agent's memory with `ObservationService.build_packet` + `ingest_packet`. The "free kill" predicate is derived from `engine/rules.py:56-98` + `:29-44` (actor alive impostor, not vented, cooldown 0, alive crewmate co-located, zero other living non-vented non-fellow players) — **not** from the policy's own `_kill_available_now`:
```
impostor_ticks=2461  in_vent=130
kill_available_ticks=415  intent_kill=225  MISSED_KILL=190   (45.8% of opportunities)
strict_kill_available=357 strict_MISSED=147
miss reasons:  168 RANKING_targets0_not_colocated | 15 fellow_impostor_defer | 7 cover_body_in_own_room
tie_at_score=168  NOT_a_tie=0   lower_id_wins=168  id_order_not_the_cause=0
```
All 168 are exact `1.0` ties broken by the lower id; the other 22 misses are the legitimate Task-7.9 defer and COVER branches; the `policy_would_kill_but_action_differs` bucket is empty, so the reconstruction is faithful. Replaying the real `decide()` on the reconstructed memory reproduces the recorded bytes exactly:
```
seed=5 tick=12 imp=p-4 room=EAST_HALL ranking=[('p-1','ENGINEERING',0,1.0), ('p-6','EAST_HALL',0,1.0), ...]
  -> decide() replays as MoveIntent to_room='ENGINEERING' (recorded action=move); free victim p-6 stood in EAST_HALL
```

**Corrections to the claim.** My counts are larger (415/225/190, 168 attributable) than the claimed 387/233/126. The sample set is 50 seeds, not 54 (54 is the raw file count incl. `MANIFEST.md`). The mechanism is *always* the id tie-break — never a genuinely higher-scoring stale lead, since a free co-located victim always scores the maximum. `_kill_available_now` (`:766-810`) inherits the same `targets[0]`-only defect, so the SABOTAGE lever can also fire on a tick with a free kill available.

**Refutations attempted, all failed.** No design ruling: `DESIGN.md:434` is silent, and `grep` over `audits/ tasks/ docs/ experiments/` finds no acknowledgement. No test covers or pins it — `tests/agents/test_impostor_policy.py` (84 tests, all pass) never places a free co-located victim alongside a higher-ranked remote one, so a fix breaks nothing.

**Corrected severity: P1.** Not P0 — the engine backstop (`engine/rules.py:62-76`) never accepts an illegal kill, replays stay byte-identical, no data loss; the policy is conservatively wrong (forgoes kills), not unsafely wrong.

**Real-world impact.** The impostor FSM discards ~40% of its legal zero-witness kill opportunities purely because a crewmate with a lexicographically smaller id is visible one room away — it walks out of the room it could have killed in, or stands still. This depresses impostor kill rate and every impostor-side number in the committed 9p2i baseline, so the long-running "impostor win rate too low / the meeting never decides" investigation has been measuring a hobbled inner loop. Fix is clean: re-validate co-location across `targets`, or add a proximity term to `score`.

Note: running `pytest tests/agents/test_impostor_policy.py` left an untracked `.coverage` file in the repo root (pytest side-effect); I did not delete it, per the read-only rule. Nothing else in the repo changed.

/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-C-3/REPORT-C-3.md

---

**VERDICT: CONFIRMED** (all three sub-claims, including exception typing)

**Decisive evidence** (repro under `work/verify-C-5/`; 4 copies of `replays/samples/4p1i`, seed-1 truncated 40 bytes, seed-2 emptied, seed-3 row 5 given `"tick": "not-an-int"`, served via `TestClient` with `AILIBI_REPLAY_DIR` pointed at the scratch parent):

```
read_all_entries(replay-seed-1) -> builtins.ValueError: invalid replay JSON at line 16
   isinstance CorruptedFileError? False
read_all_entries(replay-seed-2) -> OK, 0 entries
read_all_entries(replay-seed-3) -> pydantic_core.ValidationError: 2 validation errors for ReplayEntry
   isinstance CorruptedFileError? False
GET /replays?set=4p1i            -> 500  Internal Server Error
GET /eval/cost-summary?set=4p1i  -> 500  Internal Server Error
GET /replays/headless-seed-0     -> 200  ticks=21 meetings=1   (healthy, but unreachable via listing)
GET /replays/headless-seed-1     -> 500                        (truncated)
GET /replays/headless-seed-2     -> 200  ticks=1 meetings=0    (EMPTY file, metadata total_ticks:0, tick0=-1)
GET /replays/headless-seed-3     -> 500                        (schema-invalid)
```
Path: `api/replay_loader.py:727` catches only `CorruptedFileError`; `cost_summary` (:750-774) has no guard at all; both reach `orchestrator/replay.py:1170` (`raise ValueError`) and `_parse_entry`'s `model_validate` (`ValidationError`). Routes `api/routes/replays.py:33-42` and `api/routes/eval.py:183-184` are bare delegates, and `api/main.py:231` registers a handler only for `ReplayStateMismatchError`.

**Refutation attempts, all failed**
1. The one guarding test, `tests/api/test_replay_loader.py:539-559` ("K-K-8 … must not 500 the whole picker"), builds its corruption as `bad.write_text(bad.read_text() * 2)` — the duplicate-tick branch only. It pins the implemented path, not the docstring's claim; nothing covers truncated/schema-invalid/empty.
2. No app-level handler widens this.
3. No design ruling in DESIGN.md/AGENTS.md/docs. The only ruling found points the other way: `agent_prompts/task-4-16-replaylog-fail-loud.md:57-59` explicitly deferred "comprehensive read-side hardening (corrupted JSON, …)", and `orchestrator/replay.py:1147-1149` repeats that deferral. So the 500 is known-deferred scope — but `api/replay_loader.py:716-717` ("one bad replay no longer blocks the picker") still overclaims what was built, and the empty-file 200 has no ruling at all.
4. Exception typing as claimed. One nuance the claim's suggested fix would get wrong: pydantic v2's `ValidationError` **is** a `ValueError` subclass (`MRO: ValidationError, ValueError, Exception, …`), so a single added `ValueError` clause covers both raise sites.

**Corrected severity: P1** (not P0). Read-only endpoints, no data loss or security exposure, and the committed sample sets are healthy and hash-verified in CI, so it only bites operator-produced dirs. Above P2 because one bad byte takes out the whole collection and because the empty-file case is a silent-bad-data path in a repo whose AGENTS.md forbids silent fallbacks — with only healthy + empty present, the listing advertises the empty file as an ordinary replay and `cost_summary` counts it (`total_replays=2`), diluting `mean_cost_per_replay`.

**Real-world impact.** Any interrupted recording — Ctrl-C'd tournament, OOM-killed worker, full disk — leaves a partial last line, and from then on the spectator picker and cost endpoint 500 for the entire set, making every *healthy* replay in that directory unreachable through the listing rather than degrading to "skip the bad one". The narrow `except CorruptedFileError` plus its passing test create a false impression that K-K-8 was fixed generally. Separately, a zero-byte file is served as a legitimate 0-tick replay and quietly skews the eval cost aggregate.

Full report: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-C-5/report-C-5.md`

---

**VERDICT: PARTIALLY-TRUE** — mechanism CONFIRMED and reproduced; the attributed cause REFUTED; impact overstated for `training/rollout.py` but understated elsewhere.

**Decisive evidence** (scratch repro on a copy of `replays/ml_corpus/9p2i/replay-seed-1000.jsonl`):
```
INTACT:    NO ERROR, outcome=CREWMATES truncated=False winner=CREWMATES complete=True  hashes_verified=25
CORRUPT-A (last tick row dropped, meeting+game_over kept):
           NO ERROR RAISED, outcome=TICK_BUDGET truncated=True winner=None complete=False
           hashes_verified=23 win_shape='TICK_BUDGET'
```

What I found trying to refute it:
- **Cause REFUTED.** `record_ml_corpus.sh:979-999`'s mutex guards MANIFEST.md only; replays go through a per-seed private stage and land via `mv -f` (atomic, same fs, only on success) at `:1079`. Plus `orchestrator/replay.py:923-937` flushes every row. That race cannot truncate a replay.
- **Blast radius via rollout.py REFUTED (mostly).** Every caller (`bakeoff/harness.py:704`, `crew/scorer.py:929`, `coevo/rollout.py:197`, `env.py:706`) reconstructs a replay it wrote itself seconds earlier. `grep -rn reconstruct_episode tests/ scripts/ experiments/` finds no corpus consumer.
- **Guard is vestigial, and provably so.** `git log -L 650,665` → original at `adca07f8` when `EpisodeBoundary` still had `"first_meeting"`, which legitimately truncated a winner-bearing replay. 19.19 retired the boundary and left the clause. `orchestrator/game.py:1774-1776` returns `TICK_BUDGET_REACHED` *without* `record_game_end`, so `game_end is not None` + `winner is None` is now always corruption.
- **Docstring claim only half-wrong.** `complete`/`__post_init__`/`TruncatedEpisodeError` do prevent scoring-as-full-game. But `harness.py:942` and `crew/scorer.py:988` pre-check `.complete` and return `TRUNCATED_EPISODE_FITNESS` — so the containment is a silent floor score, not the loud raise the docstring implies.
- **NEW, worse instance.** `eval/validity.py:518` has the identical inversion (`if game.reconstructed_winner is not None and ...`) on the gate that *does* read committed corpus bytes. Verified: `CORRUPT-A validity-gate: reconstructed_winner=None game_over_tick=21 -> all_games_reach_game_over PASSED=True violations=()` while summarising "1/1 games reached game_over".
- **The fix already exists, un-back-ported.** `training/anchor_study.py:631-655` (added "Codex review on PR #292") rejects the same bytes: `CorpusWalkError: seed 1000: the reconstructed walk never reached GAME_OVER (truncated tick stream)`. Four+ copies of the walk recipe exist; the hardening landed in one.
- No test covers tail loss (`tests/training/test_rollout.py:129` only mutates a hash); no design ruling sanctions the guard — `tasks/phase-18.md:2534` states the opposite invariant.

**Corrected severity:** `eval/validity.py:518` **P1** (high confidence, VERIFIED); `training/rollout.py:653-663` **P2** (real but unreachable — vestigial guard, no foreign-byte caller); docstring over-claim **P2**; lock-race attribution **refuted**.

**Real-world impact:** No live corruption path exists today through `reconstruct_episode`, so no fitness number in the repo is currently wrong because of it. The genuine exposure is the corpus acceptance gate: a corpus replay shortened by any route outside the recorder (interrupted direct `run_tournament` into a set dir, a bad copy, hand edit) passes `eval/validity.py`'s `all_games_reach_game_over` and would enter downstream consumers as a "verified" game. Both sites are one-line fixes, and the correct version is already written in `anchor_study.py`.

Full report: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-C-6/report-C-6.md`

---

VERDICT: **CONFIRMED** — every numeric sub-claim reproduces exactly, plus the "dead served field" part.

Decisive evidence — `buildBodyStatesByTick` extracted **verbatim** (`sed -n '229,264p' frontend/src/components/MapView.tsx`), compiled with the repo's own esbuild, run against `ReplayView` payloads dumped via `api.replay_loader.ReplayLoader("replays/samples/9p2i")` for all 50 committed replays (load avg 4.09):

```
{"games":50,"totalTicks":1769,"mismatchTicks":1182,"phantomTicks":1182,
 "phantomTotal":2426,"missingTicks":0,"phantomWithoutReport":0,
 "examples":[{"game":"headless-seed-0","tick":19,"served":[],"drawn":["p-2"],"phantom":["p-2"]}]}
```
1182/1769 = 66.8%. Mechanism trace (seed-0, index / served / events):
```
18 ["p-2"]  meeting_triggered, report_body:p-2
19 []                      <- consumed at orchestrator/game.py:1256-1259
20 ["p-1"]  kill:p-1       <- MapView draws {p-2, p-1}
```
(The claim's "tick 18" is the `event.tick` field, my 19 is the array index — same frame.)

Code path: `MapView.tsx:229-264` never deletes from `killRoomByVictim`; consumed at `:569-571`, `:591`, `:733-745`; rendered `:758-790`. `api/replay_loader.py:2568-2580` projects `state.bodies` correctly. `engine/visibility.py:93` filters `discovered_by is None`, so the As-agent branch (`MapView.tsx:736-745`) is correct — the two perspectives genuinely disagree. MapView is live (`App.tsx:1083`).

Dead field confirmed: `grep -rn "killed_by\|\.bodies" frontend/src` finds no production consumer of `TickView.bodies` — only `types/api.ts:104,197`, fidelity fixtures, and `stories/MapStage.stories.tsx`. Backend is tested and correct (`tests/api/test_view_model.py:490-493`).

Refutation attempts, all failed:
1. Intentional history view? `BodyMarker.tsx:13-16` documents ghosted/solid, but phase-12 design calls the base map "always Ground Truth" (`design/phase-12/stage-1-design.md:46`) and phantoms render **solid**, identical to real corpses.
2. Deliberate later divergence? No — the accumulate pattern was copied from the contract sketch `tasks/phase-4.md:1595-1607`, and corpse consumption predates it (`git log -S "del bodies[triggering_body_id]"` → `7094e0dd task 3.12`, 2026-05-17). Drift, not a decision.
3. Existing coverage? None — there is no `MapView.test.*` in `frontend/src/components/`; nothing pins or contradicts it on either side.
4. Fixed downstream? No — `bodySpecs` feeds `BodyMarker` directly.

Corrected severity: **P1**, high confidence (display-only, so not P0; no engine/eval/ML path reads it). Downgrades to P2 only if the owner rules the map should show kill *history* — and even then the solid styling misleads and `TickView.bodies`/`killed_by` stay dead weight.

Impact: on 67% of committed frames the Omniscient map paints corpses the world no longer contains, styled exactly like real ones, permanently; anyone reading "what was on the floor at tick N" over-counts, and a room can hit the `BODY_CAP` "✕ ×N" mass-grave collapse from phantoms alone. The API meanwhile serves the correct set with `killed_by`, and no frontend code reads it.

Full report: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-C-7/report-C-7.md`

---

**VERDICT: CONFIRMED** (all six sub-assertions verified; one framing nuance corrected, plus one aggravating fact the claim missed)

Decisive evidence — repro at `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-C-8/c8.test.ts` (config + symlinked node_modules alongside; repo untouched, `git status --porcelain` empty). One skewed `RubricView` payload, two code paths, load avg 7.58:

```
✓ C-8 > ReplayPicker/GuidedTour path (client.getRubric) REJECTS 27ms
✓ C-8 > TournamentDashboard path (raw fetch, verbatim from :1028-1050) ACCEPTS 1ms
stdout | dashboard state = {"status":"ready","view":{"viewModelVersion":"9.9.9-from-a-future-server",...}}
```

Verified facts:
- `frontend/src/api/client.ts:132-155` — `getJson` calls `assertViewModelVersion(data, url)` immediately before `return data as T`; its own comment: "The one thing checked at runtime before the cast below."
- `api/schemas.py:1223` (ReplayView) and `:1291` (RubricView) are the **only** two `view_model_version` stamps in the file; `TournamentEvalReport` and `SetsResponse` carry none.
- `TournamentDashboard.tsx:38` imports **only** `apiUrl` from `../api/client`; `:1028` raw-fetches `/eval/rubric` and `:1046` does `(await response.json()) as RubricView`. `getRubric` exists at `client.ts:319` and is used at `ReplayPicker.tsx:612` and `GuidedTour.tsx:66` — confirmed.
- `getTick` (`client.ts:257`) and `getEvalCostSummary` (`:295`) have zero production consumers; the only hits are `store/replayStore.test.ts:31,34`, which are `vi.fn()` stubs inside a whole-module mock — i.e. the test would keep passing if both were deleted. Dead.
- `BeliefMatrix.tsx:33-49` is the second raw fetch; no `getBeliefFrames` anywhere.

Corrections / additions:
- **Nuance (softens one part):** `BeliefMatrix` fetches `BeliefFrameView[]` — an array. `assertViewModelVersion` (`client.ts:117-119`) returns early for arrays, so routing it through `getJson` would add no guard today. It's an architecture/consistency defect, not a bypassed guard. The claim doesn't actually assert otherwise, but the two sites are not equivalent.
- **Aggravating (claim understated it):** the Tournament route has **no** guarded payload at all. `App.tsx:1170` mounts `TournamentDashboard` alone; its three loads are `loadSets` (unstamped `SetsResponse`), `getTournamentReport` (unstamped), and the raw rubric fetch. The app-shell `loadReplayList` (`App.tsx:1154`) returns an array, which the guard skips. A user landing on `/tournament` is running fully unchecked.
- **Third partial hole:** `GuidedTour.tsx:66` does `getRubric(set).catch(() => null)` — a `ViewModelVersionError` there is swallowed into the "no rubric" empty state, so 1 of the 2 "correct" call sites fails quiet anyway.
- No design ruling exempting these sites: `tasks/phase-19.md:1678` states only "the client rejects a mismatched `viewModelVersion` loudly", and 19.24's Files-in-scope lists `client.ts`/`client.test.ts` — the pre-existing raw fetches (Phase 12) were simply never migrated. No eslint `no-restricted-globals` rule on `fetch`; no e2e coverage of the rubric path.

**Corrected severity: P2** (not P1). `VIEW_MODEL_VERSION = "1"` (`types/api.ts:22`) and `git log -S` shows exactly one commit touching it — the one that introduced it (1b4b1693). The guard has never fired in anger, and the stamped-and-checked `ReplayView` still covers the replay path. Fix is three lines (`getRubric(seedSet)` + `ApiError.status === 404`, mirroring `ReplayPicker.tsx:612-625`). Confidence high.

Real-world impact: today, latent — a version bump is required to trigger it, and none has happened. The moment `VIEW_MODEL_VERSION` is bumped (the only reason the mechanism exists), a stale dashboard build against a fresh API renders the rubric panel from a foreign contract silently, while the picker on the adjacent route throws loudly on the same endpoint — the confusing half-failure the loud-fail design was meant to prevent. Escalate to P1 on any bump.

---

**VERDICT: CONFIRMED** (one sub-clause narrowed; one mitigating context found)

**Code path [VERIFIED].** `meetings/transcript.py:2170-2180` `_iter_sightings` yields *every* `SawPlayerObservation` from *every* turn, computing only `canonical_rooms`. `:2380-2495` `_detect_alibi_vs_sightings` never reads `sighting.speaker` except for the proxy re-target. `:1414-1421` `detect_contradictions(...)` has **no `sighting_records` parameter** — it cannot ground this kind. `meetings/schemas.py:194` states grounding for sightings feeds the vouch channel "NEVER a contradiction flag". `manager.py:1235-1246` confirms the live mapping is unthreaded; `manager.py:3779` states "observations are NOT chokepoint-validated".

**Repro [VERIFIED]** (`scratchpad/work/verify-C-11/repro.py`) — speaker with zero records, never co-located:
```
CASE 1: kind=alibi_vs_sighting band=STRONG subjects=('p-1',)
        vent_sighting flags minted: 0   <-- grounded channel refuses the same fabrication
CASE 2 (multi-tick alibi, ONE lone sighting): band=STRONG
detect_contradictions accepts sighting_records?  False
```

**Census re-derived from engine truth [VERIFIED]** (killers from `kill`/`vent` tick actions; games kept only when `|killers|==n_impostors`; no flag used to infer role):
```
files=100 exact-role-truth games=96
STRONG alibi_vs_sighting total=60 crew=53 imp=7 crew%=88.3
  subj=crew sighting_by=IMP  17     subj=crew sighting_by=crew  36
STRONG vent_sighting total=107 crew=0 imp=107
```
All claimed numbers reproduce exactly, including the 17-vs-36 split and the clean grounded channel.

**Base-rate refutation attempt FAILED — it strengthens the claim.** `P(IMP)` over living meeting participants = **0.261** (284 IMP / 804 crew). The flag names an impostor at **0.117** — *less than half of random*. The STRONG `alibi_vs_sighting` is anti-informative.

**Downstream impact [VERIFIED]** (`CONTRADICTION_SUSPICION_DELTA=0.3` vs weak `0.08`, `beliefs.py:104,108`):
```
Ejections where the ONLY strong flag on the ejected was alibi_vs_sighting: {IMP: 3, CREW: 20}
Ejections where the ONLY strong flag was vent_sighting:                    {IMP: 73, CREW: 0}
```
**20 of the corpus's 25 wrongful ejections (80%)** are the ungrounded class, at 13% precision, versus 100% for the grounded sibling.

**Other refutations attempted.** No test contradicts it — `tests/agents/test_beliefs.py:3814,3853` *confirms* it ("a STRONG `alibi_vs_sighting` false positive… a PRECISION cost"), but pins only the 2 body-reporter cases, blind to the other 51. DESIGN.md:568,683 describe the kind mechanically with no grounding requirement, so there is a partial design ruling — but the module's own docstring at `transcript.py:105` (restated `:150`, `:3276`) declares "A STRONG flag naming a CREWMATE is a false positive", so code and stated doctrine conflict. **Mitigating:** `audits/audit-phase-19-triage.md:89` item 20(b) already states verbatim that "sighting provenance is not checked against whether the speaker could have observed the event", VERIFIED at rows 9/14 — a known, owner-deferred issue.

**Narrowing.** "no check that the speaker was **alive**" is over-stated — only living participants take turns (`manager.py:1024`). The real gaps are co-location and record-matching.

**Bonus P2 doc drift.** DESIGN.md §5.4 calls the WEAK band "a single uncorroborated voice"; since Task 13.14 that is false here — CASE 2 is exactly that shape and classifies STRONG.

**Corrected severity: P1** (not P0: precision/gameplay, no correctness/security/data-loss, already audited and deferred; not P2: it drives 80% of wrongful ejections, the fix already exists in the sibling channel, and it contradicts the module's own doctrine). **Confidence: very high.**

**Real-world impact.** Any player's unverified speech can mint the maximum-weight evidence label against an innocent, and impostors demonstrably exploit it (17 of 53 crew-naming STRONG flags had the sighting spoken by an impostor). It is the single largest source of wrongful ejections in the committed corpus, and it inverts the project's stated evidence hierarchy — fabricated testimony carries the same +0.30 as engine-grounded vent proof.

/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-C-11/REPORT-C-11.md

---

**VERDICT: PARTIALLY-TRUE** — the fork is real at roughly the claimed scale; the load-bearing risk assertion is REFUTED by experiment.

**CONFIRMED [VERIFIED]** (my own AST-normalised scan, `verify-C-33/ast_dup.py`):
- `enumerate_crew_options` 412 lines: `agents/tactical/learned/crew_forward.py:275` == `training/crew/options.py:282`. 17 cross-firewall groups / 888 agents-side lines (claim: 14 / 969 — right ballpark).
- `enumerate_owned_task_options` (184) pairs with `training/crew/options.py:737` `OwnedTaskOptionBasis.enumerate` (renamed method, so a plain `def` grep misses it).
- `crew_forward.py:281` docstring "Ported verbatim from the training-side reference" — verbatim.
- Both greps return nothing (exit 1). `.importlinter` forbids only `agents → training`; the reverse edge is legal and used **43 times across 19 files / 7 agents modules** — `training/crew/options.py:78-91` itself imports four. The fork is avoidable in principle.

**REFUTED [VERIFIED]:**

1. *"no parity test"* — **false; five gates exist**, all always-on (no markers; registered in `tests/training/test_suite_tiers.py:38-45`): crew Q4 bit-exact gate `tests/training/test_learned_factory_acceptance.py:616`; impostor twin `tests/agents/test_learned_policy.py:462`; action-mask parity `:971`; feature-basis `:504`; genome bytes `:479,:497`. `_CrewQ4Comparator` (`:527`) runs **both** implementations in lockstep at every crew decision of a real `rollout_crew_candidate`, comparing float-hex feature bits, score bits and chosen intent.

2. *"no test imports both"* — **false**: `…acceptance.py` imports `crew_forward` (line 56, incl. private `_build_action_mask`) **and** `training.crew.options` (113), `training.crew.scorer` (119), `training.env.build_action_mask` (125). `tests/scripts/test_champion_flip_ruling.py` too.

3. *"silent drift"* — **refuted by injection** (`verify-C-33/drift_test.py`, monkeypatch only, no repo edit; load 9.4):
```
[BASELINE]       decisions=223, multi-option=216, mismatches=0
[DRIFT-INJECTED] decisions=223, multi-option=216, mismatches=446
  'agent p-1 tick 0: feature bits diverged' / 'score bits diverged'
GATE CATCHES ONE-SIDED DRIFT: True
```
A 1e-9 one-sided perturbation goes loudly red. The gate is non-vacuous (216 multi-option menus actually exercise the argmax).

**Design ruling exists:** `audits/audit-phase-15-pause.md` §7 decision 6 (owner-ratified 2026-07-09) contracts bit-exact training-vs-shipped equality as "**a test, not an architecture change**". `tasks/phase-18.md:373` shows the import-don't-fork posture used elsewhere — so this fork is deliberate.

**Genuine residual [VERIFIED]** — coverage of the forked module under the Q4 gate:
```
crew_forward.py  335 stmts  90 miss  106 branch  68%   Missing: ... 987-1133 ...
```
`_build_action_mask` (987–1133) is **uncovered by the Q4 gate**, and its own parity test exercises exactly **one** packet state. A mask divergence in another state (in-vent, cooldown, 0 emergency uses, other sabotage vocabulary) passes both. The 2-seed stream `_CREW_Q4_SEEDS=(1004,1009)` also pins only reachable states [JUDGMENT].

**Corrected severity: P2** (duplication cost + narrow mask-parity coverage gap), down from the implied P1/P0.

**Real-world impact:** ES cannot silently optimise a different action space — the crew and impostor Q4 gates would fail the build on any bit-level divergence in the option menu or scoring, as demonstrated. The residual exposure is narrow: a drift confined to `_build_action_mask` branches outside its single tested state, or to option branches seeds 1004/1009 never reach. The 888 duplicated lines remain a real maintainability tax (every edit made twice by hand, caught only after the fact), but this is a fork defended by measurement, not an undefended one.

Full report: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-C-33/REPORT.md`

---

VERDICT: **CONFIRMED** (one nuance on the xdist leg)

**Plant sites — all fixed, repo-relative, all try/finally, no fixture** (`tests/test_firewall.py`):
- :21-23 `repo_root/"agents"/"_firewall_bad_import.py"` → cleanup :36-37
- :41-47 `observation/_firewall_engine_bridge.py` + `agents/_firewall_bad_transitive_import.py` → :60-62
- :142-144 `agents/_firewall_numpy_bad_import.py` → :156-157
- :213-215 `agents/tactical/learned/_firewall_bad_import.py` → :224-225

Five files, five fixed paths inside the live checkout. Every cleanup is a bare `finally:` inside the test body — no `yield` fixture, no `tmp_path`, no `monkeypatch.syspath_prepend`, no lock.

**Repro (my own, independent of the offered one)** — `uv run pytest tests/test_firewall.py -q` in one shell (9 passed in 0.55s) while 12 serial `uv run lint-imports --no-cache` polled in another; `uptime` load at start 9.79 (concurrent reviewers):
```
run 3 rc=1
run 4 rc=1        (10 others rc=0)
```
```
Agents must not import engine BROKEN
...
-   agents._firewall_bad_import -> engine (l.1)
-   agents._firewall_bad_transitive_import -> observation._firewall_engine_bridge (l.1)
    observation._firewall_engine_bridge -> engine (l.1)
```
2/12 false BROKEN, naming exactly the planted modules. Matches the offered 2/7.

**Junk leg confirmed:** `git check-ignore -v agents/_firewall_bad_import.py training/_firewall_probe.py` → **exit=1** (no pattern matches). `.gitignore` has no `_firewall*`; its only firewall mention is a comment at line 24 about `**/*.audit.jsonl`. A SIGKILLed run therefore leaves untracked `.py` files that a `git add -A` would stage — and the staged file *contains* `import engine`, which would turn the flake into a permanently red architectural gate.

**Refutation attempts that failed:** no serialization marker (`pyproject.toml:74` addopts is only `--strict-markers -m 'not campaign'`); no `pytest.mark` at all in the file; no lock/`flock`; no design ruling in `docs/architecture.md` (grep for the plant names returns only prose, no exemption); the only other `lint-imports` callers are `scripts/check.sh:17` and `scripts/setup_env.sh:33`, both of which run it *before* `pytest` in the same sequential script — so the single-developer happy path is genuinely safe, which is why this has survived.

**Nuance (partial on one sub-claim):** `import xdist` → `ModuleNotFoundError`. pytest-xdist is not installed and `-n auto` is not configured anywhere, so "makes `pytest -n auto` permanently unsafe" is a correct *forward-looking constraint on the fix*, not an active breakage today. The plants would also collide worker-to-worker (all five paths are process-independent), so the constraint is real.

**Corrected severity: P1** (claim's framing sustained; lower bound P2). Confidence: high — [VERIFIED] for the plant paths, the 2/12 false BROKEN, the `git check-ignore` miss and the absent xdist; [JUDGMENT] only for the SIGKILL-then-`git add -A` consequence chain.

**Real-world impact:** any second process touching the checkout during `tests/test_firewall.py` — a parallel `check.sh`, a CI job sharing a workspace, an editor's on-save lint, a concurrent reviewer — can see the repo's headline architectural contract report BROKEN against modules that do not exist, which is exactly the kind of signal a developer trusts and then chases. The window is sub-second per plant so it is rare enough to read as cosmic-ray flake rather than a known hazard. The fix is cheap and unambiguous: plant into a `tmp_path` package added to the linter's root via a generated config, or at minimum move cleanup into a `yield` fixture and add `_firewall*` to `.gitignore` so a killed run cannot leave a committable `import engine`.

---

**VERDICT: CONFIRMED** (mechanism and direction exact; one stated caveat is wrong; severity overstated)

**Code path** (read in full): `orchestrator/game.py:910-911` calls `build_prompt_renderers(active_prompt_set)` per runner; `agents/strategic/prompts/loader.py:676` → `build_environment` → `Environment(FileSystemLoader(...))` at `:225-232`, a fresh instance whose template cache starts empty. Every production per-game runner site does this: `eval/balance_eval.py:359`, `eval/benchmark.py:124`, `eval/leak_scan.py:589`, `training/coevo/rollout.py:194`, `training/bakeoff/harness.py:701`, `training/crew/scorer.py:926`, `training/env.py:662`.

**Profile** (`cProfile scripts/run_tournament.py --num-games 10 --roster-preset 9p2i`, load 7.7):
```
in 2.514 seconds
   30  0.000  0.369  jinja2/loaders.py:107(load)
   30  0.001  0.364  jinja2/environment.py:731(compile)
   11  0.000  0.000  jinja2/environment.py:294(Environment.__init__)   <- 1 import-time _ENV + 10 per-game
```
0.369 s = **14.7%** (claim said 0.405 s / 16%). `Environment.__init__ == 11` is the decisive proof of one fresh env per game.

**A/B** (my own script, 4 ABBA rounds = 8 legs, one process, 10 seeds each, 9p2i tpc=2; load 8.8–9.4):
```
rep0 base 75.52 | rep0 jinja 65.01 | rep1 jinja 68.39 | rep1 base 76.43
rep2 base 77.60 | rep2 jinja 61.71 | rep3 jinja 61.60 | rep3 base 77.42
base 76.74 ms/game   cached 64.18 ms/game   speedup 1.196x   saved 12.57 ms/game (16.4%)
replay SHA-256 identical across all 4 runs: True
```
Every base leg > every cached leg. **1.20x, not 1.24x** — claim modestly optimistic but within this machine's noise. Isolated cost: `build_environment()` alone 0.010 ms; compiling all four templates 15.3 ms (accusation_round 6.5, vote_ballot 4.6, impostor 2.3, crewmate 2.1); 3 compile per game.

**REFUTED sub-claim:** "the cache key must include the roll-call lever or AILIBI_PROMPT_SET switching breaks." `build_environment` (`loader.py:203-232`) never reads the lever — the lever picks template *filenames* in `build_prompt_renderers` (`loader.py:680-686`). Keying on `(resolve_prompt_set(...), root)` with the env read **before** the lookup is sufficient. Verified directly: set-switching still distinct, lever ON/OFF still binds `impostor_report_roll_call.j2` vs `impostor_report.j2`, lever ON with `qwen3_5_9b` still raises. Also `auto_reload=True`, so a shared env re-stats and does **not** serve stale bytes after an on-disk template edit (verified: V1→V2). With the cache installed as a pytest plugin: `tests/agents tests/meetings tests/orchestrator/test_game.py` → **1918 passed**; the byte-golden + perturbation gates pass because every test uses a distinct `tmp_path` root.

**Corrected minor:** "_ENV the production path never uses" — true of the game path, but `_ENV` is the live default for the module wrappers used by `experiments/lab/{meeting_prompt_battery,deception_battery,deception_battery_2}.py`. Not dead code.

**Corrected severity: P2** (was implicitly P1). The default client is `FakeProvider` (`llm/provider.py:305`), so this 12–17 ms/game only bites the LLM-free paths: CI, the eval harness, and `training/` ES rollouts, where thousands of games run and ~16% is real throughput. On any real provider (Ollama/Featherless) a meeting costs seconds, so the saving is noise. Real-world impact: a one-line memoization would cut CI/tournament and ML-rollout wall time by ~1/6 with byte-identical replays and no loss of the PR #203 set-binding discipline.

Scratch: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-C-42/{ab.py,cacheplug.py,t10.prof}`

---

**VERDICT: CONFIRMED** (confidence HIGH). Corrected severity: **P1** for batch/simulation paths, P2 in interactive production.

**Decisive evidence** (all [VERIFIED], scripts in `.../scratchpad/work/verify-C-43/`):

1. Figures reproduced *exactly*: `seed=5 tpc=12 ticks=119 outcome=CREWMATES / recent() calls=5,160 events visited=3,158,709`, top callers `perception.py:143` (1,080/663,457), `:284`, `:315`, `crewmate_policy.py:304`, `:361`, `impostor_policy.py:266` — the claimed set, in the claimed order.
2. cProfile of one 119-tick game (0.814 s): `1870084 0.177 ... episodic.py:122(<genexpr>)` is #1 by tottime (22% of the game) and `5160 0.087 cumtime 0.264 ... episodic.py:119(recent)` is 32% of total cumtime. Runner-up (`_scored_targets`) is 0.061 s.
3. Scaling, 2 seeds, load 8.33: `_collect_intents` 0.36→2.10 ms (seed 5) and 0.36→2.31 ms (seed 11) across tick octiles — clean linear-in-tick-index, i.e. Θ(T²) total.
4. A/B interleaved base/bisect twice (load 10.38 → 10.03): long 9p2i `322.5 → 241.2 ms` and `300.4 → 237.2 ms` (1.34x / 1.27x, claim said 1.28x), with **replay SHA-256 byte-identical across all four runs and all three seeds**. Short tpc=2 games only 1.07x — the win is superlinear in game length, as the model predicts.

**Refutation attempts that failed:**
- Semantics: 3,000 random legal append sequences × full `since_tick` sweep (negatives, duplicate ticks, gaps) → `mismatches=0`. `append()` at `agents/memory/episodic.py:96-117` rejects `tick < last.tick`, and `_events` has no other mutator anywhere in `agents/`, `orchestrator/`, `training/` — so bisect is a provably exact drop-in.
- Existing tests: `tests/agents/test_memory.py:33-92` pins only behaviour (order, filtering, out-of-order rejection, equal-tick append). Nothing pins the linear scan; nothing contradicts the claim.
- Design ruling: none. `tasks/phase-2.md:200-203` specifies only the two signatures; DESIGN.md/AGENTS.md/docs say nothing about scan cost. Unforced omission, not a deliberate trade-off.

**Two corrections to the claim's own evidence** (non-material): (a) "3 per tick in perception.py [pass `since_tick=0`]" — only `perception.py:284` passes 0; `:143` and `:315` pass non-zero ticks but still full-scan under the shipped implementation. (b) The quoted `bisect 0.3us` is unreachable by bisect alone — materialising the whole tuple at `since_tick=0` is still an O(n) memcpy (I measured 1.0us@400 → 39.4us@8000). That figure is the *cached* path; both halves of the patch are needed for the 1.28x.

**Real-world impact:** In a live/recorded game, LLM meeting calls dominate (seconds), so ~80 ms/game is invisible — this is not a user-facing defect. It bites where throughput is the binding constraint: the ES/bakeoff training loops (`training/bakeoff/utility_es.py:270`, `training/crew/options.py:349`, `agents/tactical/learned/crew_forward.py:342`) and eval-harness batch replays, which run thousands of unrecorded games and are burning a flat ~25-30% of engine CPU rescanning an already-sorted list. Because the cost is Θ(T²), any future rule change that lengthens games silently makes it worse; the fix is ~10 lines behind an invariant `append()` already enforces, and leaves replay bytes untouched.

**Good, for the record:** `append()`'s fail-loud non-decreasing-tick guard and duplicate-`observation_id` guard are exactly the right kind of cheap invariant enforcement — they are what makes the fix safe and provable.

Full report: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-C-43/report.md`