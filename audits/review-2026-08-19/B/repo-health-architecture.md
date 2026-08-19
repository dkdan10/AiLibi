# AiLibi — repo-level architecture & health review

Track: **repo-health-architecture** (code-up, read-only)
Repo: `/Users/danielkeinan/projects/AiLibi` @ `main` `b809b19c`
Date: 2026-08-19. Machine load during measurements: `load average 4.5–8.9` (other reviewers concurrent; all timings noted with load).
All commands run as `uv run …`. Nothing in the repo was edited. One environment mutation (`uv run --no-dev --exact`, to verify a pyproject claim) was reverted with `uv sync`.

---

## 1. Executive read (10 lines)

1. This is an unusually **disciplined** repo for AI-agent-authored code: `ruff` clean, `mypy --strict` green over 354 files, `lint-imports` 4/4 contracts kept, 4621 tests green in 5m37s, **zero TODO/FIXME/HACK/XXX in 121k lines of non-test Python**, and **zero runtime import cycles** at module granularity.
2. The observation firewall is real and multiply enforced (import-linter contract + AST source scan + recursive packet leak test); the numpy/torch exclusion from `agents/` is likewise enforced by a source scan.
3. The **cost centre is size, not correctness**: 20 non-test Python files exceed 1500 lines and hold 53,792 lines — 44% of all non-test Python. `meetings/manager.py` (3989), `meetings/transcript.py` (3537), `orchestrator/game.py` (3193), `api/replay_loader.py` (3165) are true God modules with 1200–1400-line classes inside them.
4. **969 lines of structurally identical function bodies are forked across files**, 763 of them across the deliberate `agents ↛ training` boundary (`enumerate_crew_options`, 411 lines, duplicated verbatim). I verified the forks still agree — but **nothing in the suite enforces it**.
5. **Eight independent reimplementations of the tick+meeting loop** (`advance_tick` + `apply_meeting_result`) exist. Task 19.25 consolidated the *eval* consumers behind `eval/replay_walk.py`; 7 other sites still hand-roll it.
6. `eval/replay_walk.py`'s consolidation froze the inconsistency into a **13-flag validation matrix**; the 7 profiles enable 0–10 checks each, so "a valid replay" means seven different things.
7. **Git hygiene is the worst area**: 190 MB `.git` / 146 MB pack is dominated by two *generated, regenerable* JSON aggregates whose revision history totals **~700 MB uncompressed**. 350 remote branches, none pruned.
8. **The repo is 1.7× more process narration than product**: 95.8k lines of `agent_prompts/` + `tasks/` + `audits/` markdown vs 57.8k lines of core product Python — while durable engineering docs are 3.4k lines (0.8%).
9. Docs are genuinely good and *gated* (`scripts/check_doc_facts.py` re-derives README facts from committed bytes). Of 10 spot-checked claims, 9 held; 2 comments misattribute the numpy firewall to a nonexistent import-linter contract.
10. **Verdict for a new engineer**: the guard rails are excellent and the *invariants* are legible; the *code* is not. Onboarding cost is dominated by four 3000+-line modules and a 33%-prose docstring culture that mixes behaviour with changelog.

---

## 2. Findings, ranked

### F1 — [P1][VERIFIED] 969 lines of forked logic across the `agents ↛ training` boundary, with no parity test

`agents/tactical/learned/crew_forward.py` and `training/crew/options.py` are a copy-fork. Structural AST comparison of normalized function bodies (script: `scratchpad/work/repo-health/`):

```
cross-file structurally identical function bodies (>=4 stmts): 14 groups
  411 lines x2: agents/tactical/learned/crew_forward.py:275 enumerate_crew_options | training/crew/options.py:282 enumerate_crew_options
  183 lines x2: agents/tactical/learned/crew_forward.py:689 enumerate_owned_task_options | training/crew/options.py:737 enumerate…
  169 lines x2: agents/tactical/learned/crew_forward.py:968 _build_action_mask | training/env.py:206 build_action_mask
   34 lines x2: agents/tactical/learned/crew_forward.py:1140 owned_task_do_task_is_submission_legal | training/crew/scorer.py:230 …
   28 lines x2: agents/tactical/learned/forward.py:159 intent_key | training/bakeoff/harness.py:343 intent_key
   23 lines x2: agents/tactical/learned/forward.py:282 features_for | training/bakeoff/utility_es.py:300 features_for
   …
duplicate lines across ALL groups: 969
```

`agents/tactical/learned/crew_forward.py:281` even documents it: *"Ported verbatim from the training-side reference (`training/crew/options.py::enumerate_crew_options`)"*.

**Why it matters.** `training/crew/options.py` is the option menu the ES optimizer searches against; `agents/tactical/learned/crew_forward.py` is the menu that runs in a real game. Silent drift means learned weights are optimised against a different action space than the one deployed — a class of bug that produces *plausible but wrong* agents and is invisible to every existing test.

**Evidence they currently agree, and that nothing enforces it.**
- `grep -rn 'from agents.tactical.learned' training/` → **no hits**. `grep -rn 'crew_forward' training/` → **no hits**. The two sides never meet.
- No test imports both. I wrote a 40-line parity probe (`scratchpad/work/repo-health/fork_probe.py`) over 12 packet states built from the repo's own test helpers:
  ```
  feature-name alphabets identical: True | widened: True
  12 probe states; option-menu mismatches: 0
  ```
  So the fork has **not yet** drifted. That probe is exactly the test that is missing.

**Fix.** `training/` already imports `agents/` (43 edges) and the contract only forbids the *reverse*. Make `agents/tactical/learned/crew_forward.py` the single home and have `training/crew/options.py` re-export from it (deleting ~600 lines), or — if the training side must stay independent for freeze reasons — land the parity probe above as a test. Confidence: high.

### F2 — [P1][VERIFIED] `.git` is 190 MB because two *regenerable* JSON aggregates are version-controlled

```
$ git count-objects -vH        →  size-pack: 145.83 MiB
$ ls -la replays/ml_corpus/9p2i/tournament-eval-report.json  →  82,362,295 bytes
```
The largest objects in the pack are all revisions of the same two files:
```
80896K replays/ml_corpus/9p2i/tournament-eval-report.json
80431K replays/ml_corpus/9p2i/tournament-eval-report.json
53056K replays/ml_corpus/9p2i/tournament-eval-report.json  (x3)
27456K replays/samples/9p2i/tournament-eval-report.json
…
replays/ml_corpus/9p2i/tournament-eval-report.json: 399 MB across all revisions (uncompressed)  [6 revisions]
replays/samples/9p2i/tournament-eval-report.json:   301 MB across all revisions (uncompressed)  [24 revisions]
```
Both are **derived**: `scripts/build_sample_report.py:2` — *"Rebuild a sample set's `tournament-eval-report.json` offline from its replays."* — regenerates them from the `replay-seed-*.jsonl` files sitting in the same directory. Every re-record rewrites the whole 80 MB blob (JSON is not delta-friendly), so history grows by the full file each phase.

**Why it matters.** A fresh `git clone` pulls ~190 MB for a repo whose source is 2.6 MB. The per-replay JSONLs *should* stay (they are the determinism evidence and README's headline demo); the aggregate should not.

**Fix.** Untrack the two `tournament-eval-report.json` files, add them to `.gitignore` beside the existing `replays/tournament-eval-report.json` entry (which already ignores the top-level one — the pattern is established, it just wasn't extended to the per-set dirs), and regenerate on demand. Rewriting history is optional; stopping the bleed is not. Confidence: high.

### F3 — [P1][VERIFIED] Eight independent reimplementations of the tick+meeting loop

```
$ git ls-files '*.py' | grep -v '^tests/' | xargs grep -n 'advance_tick(' | grep -v 'def '
api/replay_loader.py:1151            audits/workflows/extract_gameplay_facts.py:2295
eval/determinism_test.py:61,92       eval/leak_test.py:130
eval/off_menu.py:434                 eval/replay_walk.py:412
orchestrator/game.py:1786            scripts/gen_frontend_types.py:395
training/anchor_study.py:562         training/rollout.py:545
training/surrogate/dataset.py:901
```
Eight of those also call `apply_meeting_result` — i.e. eight sites independently implement seed → advance → detect meeting → apply result → verify hash. `api/replay_loader.py::ReplayLoader._walk` alone is **331 lines** and its own docstring says *"Mirrors `orchestrator.game.HeadlessGame.run`'s tick loop."*

**Why it matters.** Byte-identical determinism is the project's headline claim. Every one of these eight must independently get seeding, action ordering, RNG policy, meeting application and substrate-lever checking right. Task 19.25 already recognised this and consolidated the seven `eval/` consumers onto `eval/replay_walk.py::walk_replay` — the remaining seven sites are the same debt, unpaid.

**Evidence the two surviving big walkers do agree** (my cross-check, `AILIBI_PROMPT_SET=qwen3_6_27b`, load 5.16):
```
eval.replay_walk : 24 ticks in 0.028s  (tick+meeting pre/post hashes VERIFIED)
api.ReplayLoader : 25 ticks in 0.039s  (own independent walk)
api loader ticks : [-1, 0, 1, … 23]     ← the -1 is a synthesised seed-state row for the viewer
eval walker ticks: [ 0, 1, … 23]
```
The one-tick difference is definitional (the API synthesises a pre-game frame), not a divergence. Good — but it took a bespoke script to establish, and no test asserts it.

**Fix.** Migrate `api/replay_loader._walk` onto `eval.replay_walk.walk_replay` (or lift the walker into a package neither `api` nor `eval` owns), then `training/rollout.py` and `training/surrogate/dataset.py`. Confidence: high.

### F4 — [P1][JUDGMENT] Four God modules hold 44% of non-test Python; the biggest classes are 1200–1400 lines

```
non-test .py size histogram      >1500 lines:  20 files,  53,792 lines
                                1000-1500  :  16 files,  19,606 lines
                                 500-1000  :  36 files,  25,150 lines
                                  200-500  :  52 files,  16,048 lines
                                    <200   :  75 files,   6,572 lines
```
Structure of the worst offenders:

| file | lines | worst class | worst functions |
|---|---|---|---|
| `meetings/manager.py` | 3989 | `MeetingManager` — 10 methods, **1217 lines** | `_collect_turn` 307, `run` 304, `_collect_one_ballot` 301, `_suspicion_graph_with_contradictions` 239 |
| `meetings/transcript.py` | 3537 | (7 classes, 58 free functions) | `detect_contradictions` 255, `_detect_alibi_vs_physical` 176 |
| `orchestrator/game.py` | 3193 | `HeadlessGame` 648, `TacticalAgent` 589 | `__init__` **175**, `_run_and_apply_meeting` 159, `apply_meeting_result` 153 |
| `api/replay_loader.py` | 3165 | `ReplayLoader` — 32 methods, **1363 lines** | `_walk` 331, `_finale_view` 153 |
| `eval/meeting_quality.py` | 3101 | — | `decompose_ejection_channels` 184 |
| `agents/memory/beliefs.py` | 1964 | `BeliefState` 245 | `apply_meeting_evidence_rules` **401** |

`orchestrator.game` is simultaneously the highest fan-out module (31 local deps) and 4th-highest fan-in (24) — the classic god-object signature.

**Concrete decomposition sketch** (each of these is a clean seam already visible in the top-level layout):
- `meetings/manager.py` → `manager.py` (the `run` state machine only, ~600 lines) + `meetings/turn_collection.py` (`_collect_turn`, `_default_turn`, `_normalize_self_alibi_subjects`, `_opening_*`, ~600) + `meetings/ballots.py` (`_collect_one_ballot`, `_normalize_ballot_*`, `coerce_teammate_ballot_to_skip`, `guard_ballot_target_graph`, `guard_ballot_citation`, `_preserved_ballot_markers`, ~700) + `meetings/teammate_firewall.py` (`exclude_teammate_*`, `drop_teammate_statement_target`, `_guard_teammate_turn_claims`, ~150) + `meetings/belief_evidence.py` (`MeetingBeliefEvidence`, `derive_belief_evidence`, `extract_belief_evidence`, `derive_reported_testimony`, ~450). The last of these also breaks the `agents ↔ meetings` package cycle (F7).
- `api/replay_loader.py` → `replay_loader.py` (`ReplayLoader` + `SetLoaderRegistry`) + `api/view_builders.py` (the 20-odd `_*_view` free functions at lines 2179–2717, ~700 lines of pure DTO mapping) + `api/manifest.py` (`_manifest_*`, `_set_fingerprint`, `_rubric_is_stale`, `_expected_seedset`) — and delete `_walk` per F3.
- `orchestrator/game.py` → `game.py` (`HeadlessGame`) + `orchestrator/tactical_agent.py` (`TacticalAgent` + `KillWitnessRecord` + `BodyProximityRecord`, ~620) + `orchestrator/meeting_runner.py` (`MeetingRunner`…`build_default_meeting_runner`, `_build_participants`, `_build_meeting_trigger`, ~450) + `orchestrator/meeting_absorb.py` (`apply_meeting_result`, `_absorb_meeting_beliefs`, `_record_*`, `_notify_meeting_concluded`, ~400).

None of these require behaviour changes — they are pure moves of already-separate top-level definitions. Confidence: high that the seams are real; medium on exact line counts.

### F5 — [P1][VERIFIED] `.importlinter` covers 89 of 383 Python files; `api/`, `orchestrator/`, `eval/`, `scripts/`, `experiments/` have no contracts at all

```
$ uv run lint-imports
Analyzed 89 files, 379 dependencies.
Agents must not import engine KEPT / … / Contracts: 4 kept, 0 broken.
$ git ls-files 'agents/*.py' 'engine/*.py' 'llm/*.py' 'meetings/*.py' 'observation/*.py' 'training/*.py' | wc -l  →  89
```
`root_packages` lists only `agents engine llm meetings observation training`. The 108 Python files in `api/` (8), `orchestrator/` (8), `eval/` (25), `scripts/` (18) and `experiments/` (49) are outside the tool's world entirely.

`docs/architecture.md` states the boundary honestly (*"Four import-linter contracts"*) but the README's stronger framing — *"Architecture is enforced by tooling — import-linter, mypy --strict…"* — reads as repo-wide. The layering diagram's bottom rows (`orchestrator/` → `eval/ api/`) are the *unenforced* half.

**What that lets through** (all verified present today):
- `eval/validity.py:95` imports `api` — the eval gate depends on the web layer.
- `eval/determinism_test.py:14` and `eval/leak_test.py:60` import `tests._helpers.world_state` — production-tier eval depends on the test tree.
- `eval/validity.py:139-142` `sys.path.insert`s `scripts/` (not a package, no `__init__.py`) and imports `_verify_samples` under a `# noqa: E402`.

**Fix.** Add `api`, `orchestrator`, `eval` to `root_packages` and land three layered contracts: `orchestrator ↛ {api, eval}`, `eval ↛ api`, `{engine, observation, agents, meetings, llm, orchestrator, api, eval} ↛ tests`. The last one is a one-line contract that would have caught the `eval → tests` edge. Confidence: high.

### F6 — [P2][VERIFIED] The retired-lever mechanism leaves 10 accept-and-ignore functions and 152 lines of tests exercising a parameter that is read by nothing

13 substrate levers "graduated" to unconditional. The graduation deletes the *env read* but keeps the *shape*:

```python
# meetings/manager.py:854
# ``ENV_ROLL_CALL_ROUND`` is retained (no longer read) for the stamp
# key's naming provenance and backward-compatible imports.
ENV_ROLL_CALL_ROUND: Final[str] = "AILIBI_ROLL_CALL_ROUND"

def roll_call_round_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Whether the Task 18.8 roll-call-round lever is ON — now always True.
    …The ``env`` argument is accepted and ignored…"""
```
Ten such functions exist (`agents/memory/beliefs.py:190,224,292,407`, `agents/memory/store.py:189`, `agents/strategic/prompts/loader.py:264`, `meetings/constants.py:54`, `meetings/manager.py:859`, `meetings/transcript.py:1362,1389`, `orchestrator/replay.py:110`), and 29 comment lines say "accepted and ignored" / "no longer read" / "now always True". The test suite still spends **152 lines** setting those env vars (`grep -rn 'ENV_ROLL_CALL_ROUND|ENV_WHEREABOUTS_…' tests/ | wc -l` → 152), e.g. `tests/meetings/test_manager.py:492-811` monkeypatching a variable no production code reads.

**Why it matters.** It is a permanent tax on every reader: 13 knobs that look live, 13 signatures with a dead parameter, and a test surface that pins the *absence* of behaviour. The stamp provenance (the stated reason for retention) needs only the *string key*, not the function or its parameter.

**Fix.** Keep a single `orchestrator/replay.py::RETIRED_LEVER_KEYS: frozenset[str]` for the stamp; delete the 10 functions, their `ENV_*` constants and the 152 test lines; replace with one test asserting the stamp contains all 13 keys unconditionally. Confidence: high.

### F7 — [P2][VERIFIED] `agents ↔ meetings` and `api ↔ eval` are mutually dependent packages (no runtime cycle, but no separability either)

Package-level edges (`scratchpad/work/repo-health/import_detail.json`):
```
agents -> meetings  9   (agents/memory/beliefs.py:48-50 meetings.schemas, meetings.transcript; agents/memory/store.py:35; agents/strategic/prompts/loader.py:109,115; agents/tactical/{crewmate_policy,features}.py, agents/tactical/learned/crew_forward.py → meetings.constants)
meetings -> agents  1   (meetings/manager.py:108 → agents.memory.beliefs — 8 symbols, top-level)
api -> eval         8   (api/routes/eval.py:45-56, api/replay_loader.py:118)
eval -> api         1   (eval/validity.py:95)
```
Good news, measured: **module-level runtime import cycles = 0**.
```
TOP-LEVEL (runtime) import cycles: 0
```
(The 8 cycles a naive `ast.walk` finds — `engine.actions ↔ engine.entities`, `llm.provider ↔ {featherless,ollama}_client`, `training.bakeoff.harness ↔ 5 siblings` — are all `TYPE_CHECKING`-guarded or function-local. That is careful work and I count it as a positive.)

Still, neither package pair can be extracted, tested or reasoned about independently. The `agents ↔ meetings` pair is arguably intentional (`docs/architecture.md` puts them on the same layer row) and is mitigated by the `agents ↛ meetings.manager` contract. The `api ↔ eval` pair is not defended anywhere: `eval/validity.py` reaches into `api.replay_loader._load_roster_config` (a private symbol) purely to reuse a roster parser. Confidence: high.

### F8 — [P2][VERIFIED] The consolidated replay walker exports a 13-flag validation matrix; the 7 profiles enable 0–10 checks each

`eval/replay_walk.py:231` `ReplayWalkConfig` has 13 settings and documents *"Every check is an OPTION (module docstring: no check is core-mandatory)."* Measured across the 7 call sites:

```
eval/leak_scan.py:479        profile='leak-scan-factory'         checks_on=0:  []
eval/balance_eval.py:859     profile='kill-gift'                 checks_on=2
eval/validity.py:451         profile='validity-gate'             checks_on=2:  [verify_meeting_post_hashes, verify_tick_hashes]
eval/win_condition_selfcheck.py:205 profile='win-condition-selfcheck' checks_on=2
eval/funnel.py:240           profile='funnel-instrument'         checks_on=3
eval/kill_craft.py:527       profile='kill-craft'                checks_on=7
eval/watchability.py:1229    profile='watchability-referee'      checks_on=10
```
The *validity gate* runs 2 of 13 checks; the *watchability referee* runs 10. `leak-scan-factory` runs **none** — it walks a replay, reconstructs packets, and scans them for hidden-state leaks without ever confirming the reconstruction matches the record.

Both zero-check and two-check profiles carry an explicit justification in-source (`eval/leak_scan.py:472-477`: *"NO checks, deliberately — … it performed neither hash verification nor doubled-record detection before 19.25; enabling either would change what it accepts"*). That is honest, and the refactor was correct to be behaviour-preserving. But the end state is that the *mechanics* were unified while the *semantics* stayed seven-way inconsistent, and the config object is now the place that inconsistency is permanently encoded.

**Fix.** Promote `verify_tick_hashes` + `verify_meeting_post_hashes` to non-optional (they are cheap — my probe walked 24 ticks with both on in 28 ms) and delete the two flags; keep only the genuinely policy-shaped options (`missing_meeting_row`, `ballot_tally_threshold`, the completeness set). Confidence: medium-high (needs a re-run of the affected gates).

### F9 — [P2][VERIFIED] 33% of non-test Python is prose, and 2691 source prose lines are changelog

```
non-test py: 121,367 lines, 10,825 comment lines, 29,249 docstring lines => prose 33.0%
  meetings/manager.py: 2210 prose / 3990 lines = 55%
  meetings/transcript.py: 1956 / 3538 = 55%
  eval/watchability.py: 1067 / 2201 = 48%
  orchestrator/game.py: 1422 / 3194 = 45%
```
Classifying prose lines that mention `Task N.M` / `Phase N` / `PR #N` / `audits/audit-*` / `Wave N` / `baseline N`:
```
source       prose lines= 35900  history-narration lines=  2691  ( 7.5%)
tests        prose lines= 27079  history-narration lines=  1688  ( 6.2%)
  meetings/manager.py      283/2210 (13%)
  orchestrator/replay.py    88/ 646 (14%)
  agents/strategic/prompts/loader.py 61/390 (16%)
```
Raw mention counts across the 199 non-test files: **1896 `Task N.M`**, 214 `Phase N`, 205 PR refs, 141 audit-path refs — present in **129 of 199 files (65%)**.

`meetings/manager.py`'s module docstring is 95 lines and contains sentences like *"UNCONDITIONAL since the Task-18.12 baseline-6 record (the CREW-ONLY graduation slate; it was default-OFF and env-gated at Wave 1, retired to always-on once baseline 6 adopted it, mirroring the 16.17 slate)"* — three historical states of a flag that today has one.

**Mitigating evidence, and it is strong**: I checked every `audits/*.md` and `tasks/*.md` path referenced from Python. **43 of 44 resolve**; the single miss is the literal template placeholder `tasks/phase-N.md`. So the references are *maintained*, not rotted — this is deliberate, curated provenance, not sloppiness.

**Judgment.** The behaviour half of these docstrings is excellent and should be kept. The changelog half belongs in `git log` / the audits, which already exist and are already linked. Cutting the ~2700 narration lines would remove ~2.2% of source and materially reduce the "what is the current shape of this?" cost that dominates onboarding. Confidence: high on the measurement, medium on the value of cutting (the owner's workflow may depend on it).

### F10 — [P2][VERIFIED] Two comments attribute the numpy firewall to an import-linter contract that does not exist

```
agents/tactical/features.py:23  "…``numpy`` is confined to ``training/`` by an import-linter contract."
tests/test_firewall.py:83       "…why ``numpy`` stays confined to ``training/`` (its own import-linter contract)"
docs/architecture.md            "``numpy`` is confined here by contract"
```
`.importlinter` contains four contracts: agents↛engine, agents↛training, agents↛meetings.manager, observation↛{agents,meetings,llm}. **There is no numpy contract.** The real enforcement is `tests/test_firewall.py:118 test_agents_have_no_numpy_or_torch_import` — an AST source scan, which is in fact *stronger* (it catches a planted import even inside a function). Verified: no `numpy`/`torch` import exists anywhere under `agents/`.

Harmless today, but it teaches a reader a false model of where enforcement lives, and someone editing `.importlinter` would reasonably assume the numpy rule is one of the four they can see. Confidence: high.

### F11 — [P2][VERIFIED] Ruff runs only its default rule set; an expanded set finds 89 issues in the core packages

`pyproject.toml` `[tool.ruff]` sets only `target-version` and `line-length = 88` — no `select`, so only `E4,E7,E9,F` (≈pyflakes) run. `line-length` is therefore *declared but unenforced* (E501 is not in the default select):
```
$ uv run ruff check --select E,W,F,I,B,SIM,UP,C4,ARG,RET,PTH --statistics engine observation agents meetings orchestrator llm api eval
36 E501  line-too-long          13 I001  unsorted-imports        9 B904  raise-without-from-inside-except
 5 ARG001 unused-function-argument   4 ARG002 unused-method-argument   3 C420 …
Found 89 errors.  [*] 24 fixable
```
Nothing here is severe — 9 × `B904` (losing exception context in `raise` inside `except`) is the only one with runtime consequence. The point is that `ruff format --check` (383 files clean) is doing the heavy lifting and `ruff check` is nearly a no-op. Confidence: high.

### F12 — [P2][VERIFIED] `agents/runtime.py` is documented-dead code kept alive by its own tests

`agents/runtime.py:1` — *"TEST-ONLY runtime harness … `_choose_action` is a hardcoded `WaitIntent` and its `_update_memory` is a no-op … do not delete it as dead code."* 137 lines + 120 lines of tests (`tests/agents/test_runtime.py`) + `tests/agents/test_beliefs_wiring.py` + `tests/agents/test_perception.py` exercise a class the production path never constructs. `vulture --min-confidence 60` flags `agents/runtime.py:27: unused class 'AgentRuntime'`. `docs/architecture.md` correctly labels it TEST-ONLY.

This is a small, well-signposted 257-line liability, not a defect. It is worth naming only because it is the clearest instance of a pattern the review brief asks about: agent-authored code that is preserved *because a task contract created it*, with the justification ("the Phase-2 skeleton later phases keep around as a documented reference") written into the file. Confidence: high.

### F13 — [P2][VERIFIED] `api.main` does filesystem I/O and prints to stdout at import time

`api/main.py:262` `app = create_app()` at module scope. Importing `api.main` — which `eval/validity.py`, tests and tooling all do transitively — scans the replay directory and prints:
```
$ uv run python -c "import api.main"
Serving replay sets from /Users/…/replays/samples (2 set(s): 4p1i, 9p2i).
```
A factory already exists; `uvicorn --factory api.main:create_app` would remove the module-scope call. Confidence: high.

### F14 — [P2][VERIFIED] Branch sprawl: 350 remote branches, 41 local, 24 already merged into `main`

```
local branches: 41   remote branches: 350   merged into main (local): 24
```
Every task is a branch and none are pruned. Combined with F2 this is most of the clone cost. Also: `.claude/worktrees/` holds **810 MB** of untracked duplicate checkouts inside the repo directory — gitignored, so not a repo defect, but every recursive tool (`grep -r`, `find`, `du`) run at the repo root traverses it (it polluted three of my own greps). Confidence: high.

### F15 — [P2][JUDGMENT] Not installable; `scripts/` is imported but is not a package

`pyproject.toml` has `[project]` metadata but **no `[build-system]`** and no packages/entry-points declaration, so `pip install .` / `uv pip install -e .` cannot work. Everything runs off `[tool.pytest.ini_options] pythonpath = ["."]` and `uv run` from the repo root. `scripts/` has no `__init__.py`, yet is imported as a module by `eval/validity.py` and 13 scripts via `sys.path.insert` (`# noqa: E402` ×14 outside `experiments/`).

For a research testbed this is a defensible choice and the code explains it (`eval/validity.py:130-137`). But it means: no console entry points (every CLI is `uv run python scripts/foo.py`), no way to vendor the engine into another project, and `mypy_path = "scripts"` in `pyproject.toml` as the type-checker's workaround for the same gap. Confidence: high.

---

## 3. What is genuinely good

Recording these because the review should be fair, and several are better than what I usually see in hand-written repos.

- **G1 [VERIFIED] Zero runtime import cycles.** 130 modules, 674 local edges, module-level (non-`TYPE_CHECKING`, non-lazy) cycles = **0**. The 8 logical cycles that exist are all deliberately broken with `TYPE_CHECKING` guards or function-local imports.
- **G2 [VERIFIED] Zero TODO/FIXME/HACK/XXX** across 121,367 lines of non-test Python. Unfinished work is written as prose decisions with named owners ("deferred", "scale-phase fix", 34 mentions in 18 files) rather than left as markers.
- **G3 [VERIFIED] The gates are real and fast.** `ruff check` + `ruff format --check` (383 files) < 0.1 s each; `lint-imports` 4/4 kept in 0.22 s; `mypy .` **"Success: no issues found in 354 source files"** in 0.58 s warm; full default test tier **4621 passed, 20 skipped, 3 xfailed, 317 deselected in 337.96 s** at load ~5–6. One command (`scripts/check.sh`) runs all of it plus the frontend.
- **G4 [VERIFIED] The observation firewall is enforced three ways**, not one: an import-linter contract, an AST *source* scan that catches planted imports (`tests/test_firewall.py:133`), and a recursive packet walker over Hypothesis-generated games. All 72 tests in `tests/test_firewall.py` + `tests/observation/` pass in 5.6 s.
- **G5 [VERIFIED] `scripts/check_doc_facts.py` is a real doc-drift gate**, and it is wired into the suite (`tests/scripts/test_check_doc_facts.py:72` asserts `check_facts(_REPO_ROOT) == []` against the *live* README). It re-derives the README's sample provenance, win rates, ladder tip and lever registry from the committed bytes. Green at HEAD: *"Doc facts verified: README.md and .env.example agree with 2 sample manifests, audits/audit-phase-18-close.md, and the 14-lever substrate registry."* I have not seen this in a hobby repo before. (Minor nit: it is not named in `scripts/check.sh`, so its coverage is invisible to someone reading the gate script.)
- **G6 [VERIFIED] Doc references do not rot.** 43 of 44 `audits/*.md` / `tasks/*.md` paths cited from Python resolve on disk; the one miss is a template placeholder.
- **G7 [VERIFIED] `pyproject.toml` states a falsifiable dependency claim and it holds.** The runtime/dev partition comment includes its own probe; I ran it: `uv run --no-dev --exact python -c "import api.main, orchestrator.game, meetings.manager, agents.strategic.prompts.loader, llm.provider, engine.tick"` → OK. `uv lock --check` clean. Deps are exact-pinned (`==`).
- **G8 [VERIFIED] Security posture is honest and correct for what this is.** `SECURITY.md` states up front that the unauthenticated GM view is *the design*, scopes what is in/out of report scope, and points at `docs/deployment.md`. CORS is closed-by-default with a literal `*` rejected at startup (`api/main.py:41-47`). CI workflow has `permissions: contents: read` and **every action pinned to a full commit SHA** with the resolved tag in a trailing comment. No `.DS_Store` and no `.env` tracked (both gitignored, both present untracked). MIT licensed. Replay-set and game-id path resolution is traversal-safe: game ids are parsed to an integer seed and matched against a directory listing (`api/replay_loader.py:1985-1996`), set names go through `_validate_set_name` + a name pattern (`:3107`).
- **G9 [VERIFIED] `docs/architecture.md` is excellent** — 146 lines, written from the code, correctly labels `DESIGN.md` as a historical record, and states its enforcement boundary honestly (*"`meetings/` and `llm/` are engine-free in fact, without a contract of their own"*). Nine of my ten spot-checks held: numpy absent from `agents/`, `llm/` is a true leaf (zero local imports), `meetings/` engine-free, 13 retired + 1 toggleable = 14 registry levers, four adapters present, `determinism_test.py` covers all 3 committed fixtures, `agents/runtime.py` correctly labelled TEST-ONLY, generated frontend types pinned by a test, "300+ merged PRs" (170 squash-merged PR-numbered commits + 182 merge commits, highest PR #350).
- **G10 [VERIFIED] The frontend is well-proportioned** where the Python is not: 22k lines across 77 files, largest file 1181 lines (`App.tsx`), four-leg gate (lint → tsc → vitest → build) ordered cheapest-first, Playwright e2e in its own CI job.
- **G11 [JUDGMENT] The test tiering is principled.** `--strict-markers` with a `campaign` tier excluded by default and given a weekly CI schedule (`.github/workflows/campaign-tier.yml`) — automation, not a promise — and `tests/training/test_suite_tiers.py` pins which tests stay always-on.

---

## 4. Architecture & design assessment

**What is well-designed.**
The *invariant* layer is the best thing here. `engine → observation → agents/meetings → orchestrator → eval/api` is a real, defensible layering; the firewall is the sharpest boundary and gets the most enforcement; `llm/` is a genuine leaf with a Protocol and four adapters; `observation/` is small (1107 lines) and does one thing. The determinism story — seed + config + factory + recorded responses → bytes, with the substrate stamped onto every recording and the loader refusing a cross-substrate replay — is a genuinely good design for a research testbed where every metric must be attributable. The lever/graduation ladder is the right *idea*: behaviour changes land as registered toggles, get adopted by a baseline recording, then become unconditional.

**Where the accidental complexity is.**
1. **The layering is real at the top and imaginary at the bottom.** `engine/observation/agents` are small, clean and contract-enforced. `orchestrator/game.py`, `api/replay_loader.py` and `eval/*` are large, mutually entangled and covered by no contract (F5). The diagram's bottom two rows are aspiration.
2. **The `agents ↛ training` firewall bought purity with a 763-line copy-fork** (F1). This is the single most expensive architectural decision in the repo, and it was made for a good reason (numpy's BLAS reduction order is not bit-stable, and inference must be). The mistake is not the constraint — it is that the constraint was satisfied by copying rather than by putting the shared, numpy-free logic in the package that *is* allowed to be imported by both.
3. **Behaviour-preserving refactors froze the inconsistency they were meant to remove.** `eval/replay_walk.py` unified seven walkers' mechanics but kept seven different validation semantics as a 13-flag matrix (F8); the lever graduations deleted the env reads but kept the functions, the parameters and the tests (F6). Both are the same anti-pattern: *"preserve the exact prior behaviour"* applied so strictly that the cleanup's benefit is cancelled.
4. **The God modules are where three concerns pile up**: protocol sequencing, LLM-response normalisation/guarding, and belief derivation all live in `meetings/manager.py`; tick loop, agent construction and meeting absorption all live in `orchestrator/game.py`; engine replay, DTO construction and manifest bookkeeping all live in `api/replay_loader.py`. Each has visible seams (F4).
5. **The repo is more process than product.** Measured over all 1687 tracked files:
   ```
   bucket                                      MB   %bytes    lines  %lines
   replay artifacts (data)                  231.1    85.9%      931    0.2%
   tests (py)                                 7.4     2.8%   134119   33.1%
   process: prompts + task contracts (md)     5.0     1.8%    66631   16.4%
   process: audits (md)                       2.7     1.0%    29193    7.2%
   core product (py)                          2.6     1.0%    57776   14.2%
   training (py)                              1.3     0.5%    29441    7.3%
   frontend (ts/tsx/css)                      1.2     0.4%    23437    5.8%
   docs (md)                                  1.9     0.7%     3358    0.8%
   ...
   TOTAL                                    269.1   100.0%   405467  100.0%
   ```
   **95,824 lines of process narration vs 57,776 lines of core product Python (1.66:1), against 3,358 lines of durable engineering docs (0.8%).** And `agent_prompts/` (321 files, 36.8k lines) is 100% *generated* from `tasks/phase-*.md` by `scripts/generate_prompts.py` (gated by `--check` in `check.sh`) — I measured 65% of its substantive lines as verbatim copies of the phase contracts. Committing it is a deliberate workflow choice (they are the paste target for per-task dispatch sessions), but it doubles every contract diff and is 1.8% of repo bytes.

**What I would refactor, in order.**
1. Collapse the `agents`/`training` fork, or land the parity probe (F1) — highest risk-to-effort ratio in the repo, ~40 lines of test.
2. Untrack the two generated `tournament-eval-report.json` files (F2) — one `.gitignore` line stops a 190 MB `.git` from growing.
3. Extend `.importlinter` to `api`/`orchestrator`/`eval` and add `* ↛ tests` (F5) — ~15 lines of config, closes the only structurally-unguarded half of the layering.
4. Split the four God modules along the seams in F4 — pure moves, no behaviour change.
5. Migrate `api/replay_loader._walk` onto `eval.replay_walk.walk_replay` (F3), then the two `training/` sites.
6. Delete the retired-lever residue (F6).

---

## 5. Test assessment (for this area)

**Volume and shape.** 184 test files / 134,094 lines vs 57,776 lines of core product — **2.3:1**. Per area:
```
observation 2.59   meetings 2.77   llm 1.84   agents 1.79   orchestrator 1.69
api 1.64   engine 1.63   eval 1.00   scripts 0.95   training 0.89
```
The ratio tracks risk sensibly: the firewall and the meeting protocol are the most-tested; `training/` (frozen, per `training/README.md`) the least. 4961 tests collected, 4644 in the default tier.

**Strengths.**
- The *architecture* tests are the good ones: `tests/test_firewall.py` plants a bad import and asserts `lint-imports` rejects it (mechanism-testing, not mock-testing); `tests/observation/test_leak_property.py` runs Hypothesis-generated games through a recursive packet scanner; `tests/api/test_view_model.py` fails CI if the generated TS types drift from the Python DTOs; `tests/scripts/test_check_doc_facts.py` runs the doc gate against the real README.
- Test files themselves are prose-heavy but the prose is mostly *why this test exists*, and the audit/task references resolve.

**Weaknesses.**
- **Test files are as big as the God modules they test.** `tests/meetings/test_manager.py` is **7152 lines** — the largest file in the repo, larger than `meetings/manager.py` itself; 18 test files exceed 1500 lines, holding 45,114 lines. A new engineer cannot find the test for a behaviour by reading.
- **243 imports of 186 distinct private production symbols across 67 test files (36% of all test files).** Worst: `tests/eval/test_watchability.py` (23), `tests/eval/test_vj_instruments.py` (19), `tests/eval/test_funnel.py` (16). Most-imported privates: `meetings.manager._suspicion_graph_with_contradictions` (×8), `eval.watchability._reconstruct_kills` (×8), `orchestrator.replay._state_hash` (×6), `orchestrator.game._build_participants` (×5). Some of this is unavoidable given the God modules (they expose two public entry points over 3000 lines), which is itself an argument for F4.
- **152 lines pin a parameter nothing reads** (F6).
- **Two gaps I can name precisely:** no test cross-checks the forked crew-option implementations (F1), and no test cross-checks the two surviving replay walkers against each other (F3). Both are cheap to write — my two probe scripts are the prototypes.
- **`eval/determinism_test.py:17` hardcodes its 3 fixture filenames** rather than globbing `tests/fixtures/scripted_game_*.json`. Today the list is complete (3 on disk, 3 listed), so `docs/architecture.md`'s *"replays every scripted fixture twice"* is true — but a 4th fixture would be silently untested.

**Runtime.** Full default tier: **337.96 s** (5m37s), `4621 passed, 20 skipped, 317 deselected, 3 xfailed`, exit 0, at load ~5–6 with concurrent reviewers. Slowest tests ~1.5 s each (`tests/eval/test_watchability.py`, `tests/training/test_surrogate_dataset.py`) — no single pathological test. This is a healthy 5-minute gate.

---

## 6. Recommendations (prioritized)

1. **[P1] Land a parity test for the `agents`/`training` option-menu fork, then collapse it.** `scratchpad/work/repo-health/fork_probe.py` is a working 40-line prototype (12 states, 0 mismatches today). Then make `training/crew/options.py` re-export from `agents/tactical/learned/crew_forward.py` — `training → agents` is already a legal edge (43 existing imports) — deleting ~600 duplicated lines. Same for `agents/tactical/learned/forward.py` ↔ `training/bakeoff/utility_es.py` (~51 lines) and `_build_action_mask` ↔ `training/env.py::build_action_mask` (169 lines).
2. **[P1] Untrack the generated tournament reports.** Add `replays/*/*/tournament-eval-report.json` to `.gitignore` (extending the existing `replays/tournament-eval-report.json` rule), remove the two files from tracking, and note in `docs/artifacts.md` that `scripts/build_sample_report.py` regenerates them offline. Stops ~700 MB of blob history from growing further. Prune the 350 remote branches while you are there.
3. **[P1] Extend the import contracts to the unguarded half of the layering.** Add `api`, `orchestrator`, `eval` to `.importlinter` `root_packages` and land: `eval ↛ api`, `orchestrator ↛ {api, eval}`, and a `* ↛ tests` forbidden contract. The last one is one stanza and immediately catches the two existing `eval → tests._helpers` edges; fixing them means promoting `scripted_initial_world_state` out of `tests/` (which the Task 19.24 note in `pyproject.toml` already anticipates).
4. **[P1] Split the four God modules along the seams in §2 F4.** Start with `api/replay_loader.py` (the 20 `_*_view` functions at 2179–2717 are a clean, dependency-free lift into `api/view_builders.py`), then `meetings/manager.py`. These are moves, not rewrites; the 2.3:1 test ratio makes them safe.
5. **[P2] Delete the retired-lever residue.** Replace 10 accept-and-ignore `*_enabled(env=…)` functions + 13 `ENV_*` constants with one `RETIRED_LEVER_KEYS` frozenset in `orchestrator/replay.py`, and drop the 152 test lines that monkeypatch them. Keep exactly one test: the stamp carries all 13 keys unconditionally.
6. **[P2] Turn on more of ruff and enforce the line length you declared.** `[tool.ruff.lint] select = ["E","W","F","I","B","SIM","UP","C4","RET"]` — 89 findings today over the core packages, 24 auto-fixable, and only the 9 `B904` have runtime meaning. Cheap, and it stops the ratchet loosening.
7. **[P2] Make one pass over the God-module docstrings separating behaviour from changelog.** ~2691 source prose lines carry `Task N.M` / `Phase N` / `PR #N` / audit references; the audits they cite all exist and are linked from `docs/architecture.md`. Keep the "what it does and why" (excellent); move "what it used to do and when that changed" to the audit it already names. `meetings/manager.py`'s 95-line module docstring is the place to start.
8. **[P2] Small correctness/hygiene items.** Fix the two comments claiming a numpy import-linter contract that does not exist (`agents/tactical/features.py:23`, `tests/test_firewall.py:83`) — point them at `tests/test_firewall.py::test_agents_have_no_numpy_or_torch_import` instead. Switch `uvicorn` to `--factory api.main:create_app` so importing `api.main` stops doing I/O and printing. Glob the determinism fixtures instead of hardcoding three names. Name `scripts/check_doc_facts.py` in `scripts/check.sh` (even as a comment) so its coverage is discoverable.

---

## 7. Overall maintainability judgement for a new engineer

**Above average, with a specific and fixable bottleneck.**

What a newcomer gets for free is unusually strong: one command runs every gate in ~6 minutes and it is green; the invariants that actually matter (firewall, determinism, type strictness, DTO/TS sync, doc facts) are all *mechanically* enforced rather than documented; `docs/architecture.md` is short, accurate and current; `SECURITY.md` and `CONTRIBUTING.md` tell the truth about what this project is. There are no TODOs to triage, no dead dependencies, no lockfile drift, no cycles to untangle. That is a better starting position than most repos of this size.

What costs them is concentrated in four files. To change one thing about how a meeting resolves, they must read a 3989-line module whose central class is 1217 lines, whose largest function is 307, and whose 95-line module docstring narrates three superseded versions of the feature they are touching — then find the behaviour among 7152 lines of tests, 36% of whose files reach into private symbols. The same shape repeats in `orchestrator/game.py`, `api/replay_loader.py` and `meetings/transcript.py`. Roughly 44% of the non-test Python is in files no one can hold in their head.

Second-order: they will read `README.md`'s "architecture is enforced by tooling" and reasonably assume it is repo-wide, when in fact `api/`, `orchestrator/` and `eval/` — where the entanglement actually is — have no contracts at all. And the process tree (96k lines of prompts, contracts and audits, 1.7× the product) is a genuine asset for understanding *why* decisions were made, but there is no short path from "I need to change X" to "here is the one audit that explains X" other than the in-code references.

Nothing here is structural rot. It is size and repetition, both of which the existing test coverage makes safe to attack. Recommendations 1–4 would move this from "well-guarded but hard to read" to "well-guarded and readable" without touching behaviour.

---

## Appendix — artefacts produced

| path | what |
|---|---|
| `scratchpad/work/repo-health/imports.py` | package-level import-graph builder |
| `scratchpad/work/repo-health/import_detail.json` | every cross-package import with file:line:module |
| `scratchpad/work/repo-health/modgraph.txt` | 130-module graph, cycle detection, fan-in/fan-out |
| `scratchpad/work/repo-health/narration.txt` | history-narration classification + dangling-doc-ref scan |
| `scratchpad/work/repo-health/vulture80.txt`, `vulture60.txt` | dead-code scans (2 hits @80, 517 @60) |
| `scratchpad/work/repo-health/fork_probe.py` | **runnable** agents-vs-training crew-option parity probe (F1) |

Vulture at `--min-confidence 80` over `engine observation agents meetings orchestrator llm eval api training scripts` found only two hits — `eval/deduction_metrics.py:683: unreachable code after 'while'` and `orchestrator/replay.py:910: unused variable 'exc_info'` — which is a good result and why dead code does not appear as a finding above. At confidence 60 the 517 hits are dominated by 417 pydantic `model_config` / field declarations and FastAPI route handlers (false positives) plus `agents/runtime.py::AgentRuntime` (F12).
