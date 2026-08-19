# Code review — area `api` (api/, tests/api/)

Reviewer track: code-up, read-only. Repo: /Users/danielkeinan/projects/AiLibi @ main (b809b19c). Date 2026-08-18.
Machine load during timings: `uptime` load averages 4.4–6.2 on 10 cores (other reviewers concurrent) — treat absolute timings as ±30%.

Files: `api/main.py` (240), `api/replay_loader.py` (3165), `api/schemas.py` (1355), `api/routes/{replays,eval,sets}.py` (102/216/44), `tests/api/*` (19 files, ~6.9k lines, 2 fixture modules).

---

## 1. Executive read (10 lines)

1. The API is a thin FastAPI shell (routes ≈ 360 lines) over one big library module, `api/replay_loader.py`, which re-runs the deterministic engine over a recorded action stream and projects it into ~50 frozen pydantic DTOs (`api/schemas.py`). Correctness rests on the per-tick `state_hash` re-verification, and it holds: the committed 4p1i + 9p2i + ml_corpus sets reconstruct byte-identically (tests + my runs).
2. Performance is comfortably fine at the project's scale [VERIFIED]: cold `load_replay` 25 ms (9p2i seed 0, 25 ticks) / 52 ms (longest ml_corpus game, 65 ticks); warm 0.4 ms; `list_replays` over 50 files 112 ms cold / 0.7 ms warm; over the 150-file ml_corpus set 0.38 s cold / 2 ms warm; 100 cached replays ≈ +100 MB RSS (~1–1.5 MB each); steady-state HTTP 2–3 ms per request.
3. Caching is thoughtfully done (mtime-keyed `lru_cache`, roster-sidecar mtime, single-pass metadata summary, pagination) and the security posture is honest: closed CORS with wildcard rejection, GET-only, set-name/game-id validated (path traversal blocked [VERIFIED]); loopback-only is convention (uvicorn default / compose port binding), not enforced in code — documented as such.
4. The one real defect: `list_replays` / `cost_summary` claim "one bad replay no longer blocks the picker" but only skip the doubled-write `CorruptedFileError`; a truncated last line (the killed-recorder case) or a schema-invalid row 500s the whole listing and cost endpoint [VERIFIED].
5. `ReplayLoader._walk` is a 330-line, CC-35 God method that duplicates the reconstruction mechanics Task 19.25 centralised in `eval/replay_walk.py` (the loader was explicitly left as backlog); `_meeting_result_from_entry` exists 4× across the repo.
6. Each game is walked TWICE (visibility walk for `/replays/{id}`, memory walk for `/beliefs` + `/memory`), and every walk writes every observation packet to a temp-file audit log it then deletes — accidental cost (~10% of walk time) and an unclosed handle.
7. Docstring/comment sprawl is heavy: `schemas.py` has 1.6 prose lines per code line; the api package carries 143 "Task N.N / Audit X-Y-Z" references; runtime error messages embed task numbers. Some docstrings have drifted from behaviour (mismatch errors do NOT reach the HTTP body).
8. DTO design is disciplined (frozen, extra=forbid, generated TS types + committed check + `viewModelVersion` guard) but carries dead/speculative shapes (`SuspicionGraphView`, `FailedCallEvalView` clone) and a hand-mirrored 3-level eval-report view that turns any new eval field into a runtime 500.
9. Tests are strong on behaviour (fixtures write real replays via `ReplayLog`; TestClient end-to-end; 404/500/corruption/roster paths), 294 pass in 25 s; blemishes: one stale-skipped test with stale numbers, gameplay-audit corpus pins living in `tests/api`, a 400-name field snapshot with low signal.
10. Architecturally `api.replay_loader` is a shared "replay reconstruction + view-model" library used by scripts/, experiments/, and tests across the repo; it should not live under `api/` nor import FastAPI.

---

## 2. Findings (ranked)

### F1 — P1 — Corrupt replay files still 500 the listing and cost endpoints, contrary to the docstring  [VERIFIED]
- `api/replay_loader.py:703-729` (`list_replays`), `:750-778` (`cost_summary`), `:1688` (`_read_summary`).
- `list_replays` catches only `ReplayLog.CorruptedFileError` (the doubled-write pattern). `orchestrator/replay.py:1137-1187 read_all_entries` raises `ValueError` for a truncated/partial JSON line and `pydantic.ValidationError` for a schema-invalid row. `cost_summary` catches nothing.
- Repro (scratch script `work/api/corrupt.py`; a 4p1i copy with one file truncated by 40 bytes, one empty, one schema-invalid row):
  ```
  LIST with truncated+empty+invalid: 500 Internal Server Error
  GET seed 3 (truncated): 500     GET seed 4 (empty): 200, total_ticks=0, finale=null     GET seed 5 (invalid): 500
  cost-summary: 500
  LIST after removing seed 3: 500      LIST after removing seed 5: 200 (4 items)
  ```
- Why it matters: a recorder killed mid-write (tournament runner writes incrementally) leaves exactly a partial last line; one such file takes the whole set's picker and dashboard down. The docstring at `:713-717` ("one bad replay no longer blocks the picker … Audit K-K-8") over-claims. Also an EMPTY file is served as a 200 "partial replay" with 0 ticks (silent).
- Fix: catch `ValueError` (pydantic `ValidationError` subclasses it) alongside `CorruptedFileError` in both `list_replays` and `cost_summary`, log at WARNING, and treat a zero-entry file as corrupt. Confidence: high.

### F2 — P1 (maintainability) — `_walk` is a 330-line God method duplicating the shared walker; helper duplicated 4×  [VERIFIED]
- `api/replay_loader.py:1003-1334` — radon CC **E (35)**; `_finale_view` `:1752-1905` CC D (24); module MI = C (0.00).
- `eval/replay_walk.py` (Task 19.25) already centralises re-seed → `advance_tick` → `apply_meeting_result` → hash checks with per-consumer profiles and typed events (`TickOpened`/`MeetingOpened`/…). Its docstring even names `api.replay_loader`'s partial-replay truncation as the semantics one profile mirrors. `tasks/phase-19.md:1791` records the api loader as "backlog per the cut line".
- `_meeting_result_from_entry` is copy-pasted in `api/replay_loader.py:2195`, `eval/replay_walk.py:340`, `training/rollout.py:412`, `training/surrogate/dataset.py:437`. `_recorded_substrate_flags` / `_recorded_tactical_policy` re-implement `orchestrator.replay.read_substrate_flags` / `read_tactical_policy_stamp` over in-memory entries; `_read_summary` re-implements `compute_cost_usd` + `read_game_outcome` (documented, deliberate single-pass).
- Why it matters: two reconstruction loop bodies that must stay semantically identical (the loader's docstring says it "mirrors HeadlessGame.run"); every substrate change touches both. Confidence: high.

### F3 — P2 — Two full engine walks per game + throwaway audit-log disk writes; observation service never closed  [VERIFIED]
- `_load_replay` (`:936`) walks with `collect_memory=False, collect_visibility=True`; `_reconstruct_meeting_memories` (`:973`) walks again with `collect_memory=True`. Serving one game's full UI (replay + beliefs + memory) = 2 engine walks + 2× per-agent packet builds. Measured: 25 ms + 38 ms (seed 0), 52 ms + 87 ms (65-tick game).
- Every walk creates `tempfile.TemporaryDirectory` and an `ObservationService(audit_log_path=…)` (`:1092-1099`); `observation/audit.py:record_packet` opens the file, writes JSON and `flush()`es per packet (346 packets, ~8 ms of an 80 ms walk in the profile), then `audit_dir.cleanup()` unlinks it. `service.close()` is never called (handle released only by refcount).
- Fix: one walk collecting both (memory views are small), or at least a no-op audit sink (`ObservationService` should accept `audit_log_path: Path | None`). Confidence: high (measured); severity P2 because absolute cost is small.

### F4 — P2 — Mismatch errors documented as "HTTP 500 with the offending game id in the body" are served as a bare 500  [VERIFIED]
- `ReplaySubstrateMismatchError` docstring `:343-364`, `ReplayPolicyMismatchError` `:413-432` both promise a body; only `ReplayStateMismatchError` has a handler (`api/main.py:150-158`, registered `:222`).
- Repro (`work/api/mismatch_http.py`: 9p2i seed 0 re-stamped all-OFF): `GET /replays/headless-seed-0?set=9p2i` → `500 Internal Server Error` (Starlette default text; the 40-line remediation message goes only to the server log).
- Also: those runtime messages embed task numbers ("Phase-13.5 at Task 14.9, evidence_quality_lift at the Task-14.12 close") — history in user-facing error text. Confidence: high.

### F5 — P2 — `_classify_template_id` silently mislabels calls for prompt sets whose markers it does not know  [VERIFIED grep]
- `api/replay_loader.py:2480-2519` infers `prompt_template_id` by substring-sniffing rendered prompt bodies ("## Your cover", "## This meeting", …) and falls back to `call.call_kind` ("meeting").
- `agents/strategic/prompts/glm_4_32b/impostor_report.j2` uses "## Cover (decide before you write)" and `crewmate_report.j2` has no "## This meeting" → both classify as the bare `"meeting"` — a silent default in a codebase whose doctrine is "no silent fallbacks". Root cause: `orchestrator.replay.LLMCallRecord` does not persist the template id/version that produced the call (`orchestrator/replay.py:120-150`). Not hit by the committed sets (qwen3_6_27b/qwen3_5_9b markers covered). Confidence: medium-high.

### F6 — P2 — Eval-report route hand-mirrors three wrapper models with `extra="forbid"`; every eval field addition is a runtime 500 unless mirrored  [JUDGMENT + code]
- `api/routes/eval.py:88-152` (`_GameReportEvalView`, `_TournamentReportEvalView`, `_TournamentEvalReportView`) exist solely to redact one leaf (`failed_calls`). The docstring itself says a new field on `TournamentEvalReport` "MUST be mirrored here or … 500s" (it happened for `meeting_rate` and again for `deduction`, 19.14).
- The mirrored view embeds `engine.entities.Role`, `meetings.schemas.PlayerId`, `orchestrator.replay.WinnerSide` and eval leaf types verbatim — the opposite of `schemas.py`'s "shadow, never embed" doctrine, papered over by `tests/api/test_leak.py`'s 400-name field snapshot.
- Simpler: redact at the source (make `eval.report_schema.GameReport.failed_calls` a sanitized type, since `raw_response` is a debugging blob) or dump→redact→return with `response_model=None` for a report that is already an eval-owned contract. Confidence: medium.

### F7 — P2 — Dead / speculative DTO surface  [VERIFIED]
- `api/schemas.py:1010-1042` `SuspicionEntryView` / `SuspicionGraphView`: "Intentionally dead — kept, not revived", 15-line justification; no producer, no route, but inventoried in `EXPECTED_DTOS`, exported to `frontend/src/types/api.ts`.
- `FailedCallEvalView` `:1175-1206` is field-for-field identical to `FailedCallView` "so the two surfaces can diverge later" (speculative generality; a 30-line docstring for a duplicate).
- `classify_evidence` (`:693-752`) has a deliberately re-implemented twin `eval.deduction_metrics.classify_flag`, "cross-pinned … evidence only because neither imports the other" — both written from the same table by the same process; that is duplication with a rationale, not independent verification. Confidence: high (facts), medium (judgment).

### F8 — P2 — Test-suite hygiene: stale skip, misplaced corpus pins, low-signal snapshot  [VERIFIED]
- `tests/api/test_eval_routes.py:192-220` skipped with reason "re-enabled in Task 8.12" (Phase 8 closed 2026-06-07); its asserted numbers (4/50 games with meetings) are stale — the committed 4p1i report now says 39/50 (`games_with_meeting=39, meeting_rate=0.78`), and `tests/api/test_sets.py::test_tournament_report_is_per_set` already covers the load. Delete it.
- `tests/api/test_evidence_mechanisms.py` + `tests/api/fixtures/evidence_mechanisms.py` (272 + 358 lines) are gameplay-audit exhibits pinned to specific seeds/meetings of committed bytes ("what the frozen pipeline DOES"); they read through the loader but test nothing about the API. Every re-record moves them; they belong with the eval/audit corpus pins, marked as such.
- `tests/api/test_leak.py:300-700` `EXPECTED_EVAL_REPORT_FIELDS` pins ~400 field names of `TournamentEvalReport`; every eval metric addition must edit tests/api. The adjacent `FORBIDDEN_EVAL_ENGINE_FIELDS` test carries the actual invariant.
- Cache tests (`test_lru_cache_returns_same_instance_until_cleared`, `test_*_reads_each_file_once` via monkeypatched call counters) pin implementation (identity, call counts) — acceptable as perf contracts but brittle under F3's refactor.

### F9 — P2 — Loopback-only is convention, not enforcement  [VERIFIED docs vs code]
- `docs/deployment.md:25-52`: "safe only when unreachable by anyone but the local operator"; enforcement = `scripts/run_spectator.sh:90` omitting `--host` and `docker-compose.yml` publishing on `127.0.0.1:`. `api/main.py` has no client-host / TrustedHost guard; `AILIBI_CORS_ORIGINS` is the only network-facing switch (closed by default, `*` rejected — good, `test_app_config.py` pins it plus the compose binding).
- Judgment: acceptable for a local MVP and honestly documented (audit C-C-1/C-C-4), but a 10-line ASGI middleware refusing non-loopback `request.client.host` unless `AILIBI_ALLOW_REMOTE=1` would convert a doc rule into a code rule at zero cost (the compose path sets the env). Confidence: high on facts.

### F10 — P2 — Prose sprawl and history restated in code  [VERIFIED]
- Measured (scratch `ratio.py`): `replay_loader.py` 582 docstring + 457 comment lines vs 1793 code (0.58); `schemas.py` 607 + 55 vs 417 code (**1.59**); `main.py` 0.97; `routes/eval.py` 0.91. 143 `Task N.N` / `Audit X-Y-Z` references across api/. Examples: `_contradiction_view` `:2393-2433` has a 25-line comment for a 12-line function; `_COLOR_PALETTE` `:264-290` 17 lines of colour-theory provenance; `DEFAULT_SET` `:2970-2979` restates the audit argument for the flip.
- Why it matters: agent-authored comments narrate the change history rather than the invariant; readers must page past task archaeology to find code. Confidence: high.

### F11 — P2 — Layering: the reconstruction library lives in `api/` and imports FastAPI  [VERIFIED]
- `api/replay_loader.py:44` imports `HTTPException, Query, Request`; the FastAPI dependencies `get_loader_registry` / `get_replay_loader` (`:3117-3160`) live in the library module. Consumers outside the API: `scripts/_verify_samples.py`, `scripts/build_demo_bundle.py`, `scripts/gen_frontend_types.py`, 6 modules under `experiments/`, `tests/meetings`, `tests/agents`, `tests/scripts` (grep). Import cost 0.26–0.4 s, ~half fastapi.
- The package boundary says "spectator API"; the code is "replay reconstruction + view model + set registry + rubric/manifest provenance parsing". Confidence: high.

### F12 — P2 — Small DTO/loader nits  [VERIFIED]
- `TickView.sabotage_active: tuple[str, ...]` (`schemas.py:449`) is redundant with `TickView.sabotage: SabotageDetailView | None` (always `(kind,)` or `()`).
- `EvalCostSummaryView.decisive_split: dict[str, float]` in a frozen model (elsewhere `Mapping`); `GameFinale` breaks the `*View` naming; `RubricView`/`ReplayView` carry `viewModelVersion` but list/tick/meeting/memory/beliefs payloads do not (the client only guards the two).
- `_announce` prints to stderr instead of `logging` (`main.py:70`); `app = create_app()` at import time (`main.py:240`) does filesystem discovery on `import api.main` (documented; `test_cwd_independence.py` covers it).
- `_walk` `meeting_by_tick = {entry.tick: entry …}` (`:1050`) silently collapses two meeting rows on one tick (the shared walker has an opt-in check for exactly this).
- `list_replays` `_replay_paths()` globs + regexes + sorts the directory on every `_resolve` (each `GET /replays/{id}`), and `get_replay_loader` → `default_set()` → `available_sets()` re-globs every set dir per request when `?set=` is omitted. ~1–2 ms today; documented as the deferred negative-lookup cache.

---

## 3. What is GOOD

- **Determinism as a first-class contract** [VERIFIED]: every reconstructed tick and every meeting's `state_hash_after` is checked; `tests/api/test_replay_loader.py::test_committed_9p2i_set_reconstructs_byte_identically` and `test_sets.py::test_determinism_holds_per_set` gate the committed corpora; my full loads of all 100 sample + 150 ml_corpus replays raised nothing.
- **Cache design** [VERIFIED]: mtime-ns keyed `lru_cache` for load/memory/belief-frames, roster-sidecar mtime folded in, in-place rewrite invalidation tested (`test_in_place_rewrite_is_not_served_stale`, `test_roster_descriptor_change_in_place_is_not_served_stale`), single-pass `_ReplaySummary` for listing + cost, bounded per-set registry LRU. Memory footprint is modest (~1–1.5 MB per cached replay).
- **Input hardening**: `_SET_NAME_PATTERN` (single safe segment; `..`, `/`, `%2e%2e%2f` → 404 [VERIFIED]); game ids resolved by seed match, never joined into a path; `limit`/`offset` validated (`ge=0`; `limit=-1` → 422 [VERIFIED]).
- **CORS posture**: closed by default, explicit allowlist, wildcard refused at app build, GET-only + `Content-Type` only; `test_app_config.py` pins it and even the compose port binding.
- **CWD independence + fail-loud config** (`main.py:_resolve_replay_dir`, `_anchored`): honest, tested (`test_replay_dir_fallthrough.py`, `test_cwd_independence.py`).
- **Roster sidecar handling** (`_load_roster_config`): strict, bool-rejecting, unexpected-key-rejecting; the wrong-roster case is caught by the hash check (tested).
- **DTO contract tooling**: frozen + `extra="forbid"` everywhere; AST-based leak inventory (`test_leak.py`) that forbids engine types in annotations and forbids backend imports in `schemas.py`; TS types generated from the models with a committed-file check and a client-side `viewModelVersion` guard.
- **Routes are genuinely thin**: exception mapping only; the loader is the single seam; `ReplayStateMismatchError` → 500 with tick/game id.
- **Ballot-marker parsing** (`_parse_rewrite_reasons`) is regex-anchored on the imported marker constants with repr-aware payload matching — a real robustness win over substring stripping, and it is tested against the committed set.
- **Tests exercise behaviour through real artefacts**: fixtures record through `ReplayLog` + `HeadlessGame`/`FakeProvider`, then load through the real loader and TestClient; 404/500/corruption/pagination/partial-replay/unresolved-meeting/dead-agent-memory paths all covered; suite is fast (25 s).

---

## 4. Architecture / design assessment

**Well-designed.** The engine-playback loader is the right idea: the replay log stores actions + hashes, the API re-derives everything else, and the hash chain makes the reconstruction self-verifying. The DTO layer as a deliberate shadow surface with generated TS types is a good boundary. The set registry + per-set loader with lazy construction is a clean way to serve many corpora. Error handling for the documented failure modes (unknown set/game/meeting/agent, determinism break, malformed roster/rubric) is explicit and tested.

**Accidental complexity.**
- The `_walk` monolith (F2) carries three concerns in one loop: engine replay + hash checks, per-tick view projection (`_tick_view`, visibility packets, the labeled pre/post meeting-resolution `model_copy`), and agent-memory reconstruction (ingest, meeting-evidence absorption). The shared walker already provides the first as typed events; the loader should be a fold over `walk_replay` with a profile.
- The double walk + temp-file audit sink (F3).
- The eval route's mirrored report tree (F6) and the DTO twins (F7) are guard-rails that cost more than they guard.
- The stamped-substrate / policy-claim machinery (`ReplaySubstrateMismatchError`, `_substrate_cache_key`, `allow_substrate_mismatch`, `expected_tactical_policy`) is ~250 lines for guards whose "toggleable" set is currently empty ("NONE today — the machinery stays for a future lever" `:381`). It is correct and tested, but it is speculative weight inside the serving path.
- Provenance parsing (`MANIFEST.md` table cell indexing, `multi:` fingerprints, rubric staleness) lives in the loader (`:2845-2960`) — a lab-tooling concern (`experiments/lab/rubric_score.py` "kept in lockstep") sitting in the API module.

**Refactor sketch (in order):**
1. Move the library out: `replay/` (or `orchestrator/reconstruct.py`) = `ReplayLoader` + projections + `SetLoaderRegistry`; `api/deps.py` = the two FastAPI dependencies; `api/` keeps routes/schemas/main. No behaviour change; drops the FastAPI import from every script/experiment that only wants reconstruction.
2. Re-base `_walk` on `eval.replay_walk.walk_replay` with a `spectator` profile (tick hash ON, post hash ON, missing meeting row → truncate), folding `TickAdvanced`→`_tick_view`, `MeetingOpened`→memory snapshot, `MeetingApplied`→resolution label + belief absorption. Delete the loader's copy of `_meeting_result_from_entry`, `_recorded_*` readers.
3. Single walk producing `_WalkResult` with both `ticks` and `memories`; one LRU; belief frames derived. Give `ObservationService` a null audit sink.
4. Split provenance/rubric parsing into `replay/provenance.py` shared with `experiments/lab/rubric_score.py` (it is literally "kept in lockstep" by hand today).
5. Redact failed calls at the eval schema source; delete the three mirrored wrapper models.

---

## 5. Test assessment

- 294 passed / 2 skipped in ~25 s (`uv run pytest tests/api -q`), slowest 2.7 s (committed-set sweeps). Good density: 21 route tests, 53 loader tests, 42 view-model tests, 27 set-registry tests, 11 app-config, 11 dir-fallthrough, 9 leak, 16 taxonomy.
- Behaviour-oriented on the whole: replays are produced by the real writer/engine, loaded through the real loader, served through TestClient; error paths (404s, 500 mismatch, doubled-file corruption, malformed roster/rubric, partial replay, unresolved meeting, dead agent memory, pagination bounds, path traversal, CORS wildcard, compose binding) are all covered.
- Gaps: no test for a truncated/schema-invalid file in the listing (F1 — the doubled-write test gives false confidence); no HTTP-level test that a substrate/policy mismatch yields a useful body (F4 — the tests stop at the exception); no test that `_classify_template_id` covers every shipped prompt set (F5).
- Implementation pinning: cache identity/call-count tests, the ~400-name eval field snapshot, the corpus-content exhibits in `test_evidence_mechanisms.py`, and golden pins on specific committed seeds in `test_view_model.py` (finale/gate/marker pins) — legitimate regression anchors, but they will all move together on the next re-record and add churn without indicating a bug.
- Hygiene: stale skip in `test_eval_routes.py:192` (F8); the `tests/api/test_view_model.py` grab-bag (1314 lines, 12 concerns) would read better split by surface.

---

## 6. Recommendations (prioritised)

1. **Fix F1 now** (small): catch `ValueError` (covers pydantic `ValidationError`) in `list_replays` and `cost_summary`, log and skip; treat empty files as corrupt; add a truncated-file listing test. Also register handlers for `ReplaySubstrateMismatchError` / `ReplayPolicyMismatchError` (or one for a common base) so the documented body actually ships (F4).
2. **Re-base `_walk` on `eval.replay_walk`** with a spectator profile and collapse to a single walk (F2, F3); delete the duplicated helpers; give `ObservationService` a null audit sink. This is the largest maintainability win in the area and is already on the project's own backlog.
3. **Move the library out of `api/`** (F11): `replay/` package for loader + registry + provenance; `api/` keeps routes/schemas/deps. Scripts and experiments stop importing FastAPI transitively.
4. **Persist the prompt template id on `LLMCallRecord`** (orchestrator area) and make `_classify_template_id` fail loud on unknown markers for legacy records instead of defaulting (F5).
5. **Trim the DTO surface**: delete `SuspicionGraphView`/`SuspicionEntryView` (a one-line "decided against per-tick suspicion" note in DESIGN.md is enough), alias `FailedCallEvalView = FailedCallView`, redact failed calls at the eval schema and remove the mirrored report views (F6, F7). Consider dropping `sabotage_active` at the next `viewModelVersion` bump.
6. **Test hygiene**: delete the stale skipped test; move `test_evidence_mechanisms.py` + its fixture to the eval/audit corpus-pin suite with a marker; replace the 400-name eval snapshot with the forbidden-field assertion plus a much smaller top-level-field pin (F8).
7. **Optional loopback guard middleware** (F9): refuse non-loopback clients unless `AILIBI_ALLOW_REMOTE` is set; keeps the compose path working and turns the doc rule into code.
8. **Prose pass** (F10): cut task/audit archaeology from comments and runtime error strings; keep the invariant, link the audit. Target ≤0.4 prose/code in `replay_loader.py`, ≤0.8 in `schemas.py`.

---

## Appendix — measurements (scratch scripts in `scratchpad/work/api/`)

```
uptime load: 4.6–6.2 (10 cores)
import api.main                                 0.26 s   (api.replay_loader alone 0.26–0.40 s, ~50% fastapi)
list_replays 9p2i (50 files, 55 MB)             cold 0.112 s   warm 0.7 ms
list_replays 4p1i (50 files, 4.9 MB)            cold 0.013 s
list_replays ml_corpus/9p2i (150 files)         cold 0.38 s    warm 2.0 ms
load_replay 9p2i seed 0 (25 ticks, 3 mtgs)      cold 25 ms     warm 0.38 ms   payload 0.68 MB JSON (dump 1.8 ms)
memory walk seed 0                              38 ms          belief_frames reshape 0.8 ms
longest ml_corpus game (65 ticks, 5 mtgs)       load 52 ms     memory walk 87 ms
profile of one cold load (65 ticks): _walk 80 ms = state_hash 26 ms (json canonicalisation) + build_packet 23 ms (of which audit temp-file writes 8 ms) + advance_tick 17 ms + read_all_entries 7 ms (called twice: walk + summary)
GET /replays/{id} steady state 2.5–2.7 ms; GET /replays 2.0 ms; GET /sets 1.8 ms; /ticks/5 2.1 ms  (TestClient)
100 replays (4p1i+9p2i) cached: 2.0 s, +100 MB RSS;  50 memory walks: +50 MB
150 ml_corpus/9p2i cached: 5.1 s, +219 MB RSS (~1.5 MB/replay)
tests/api: 294 passed, 2 skipped, 24.8 s
radon: _walk E(35), _finale_view D(24), _tick_events C(15); MI replay_loader.py = C (0.00)
prose/code: replay_loader 0.58, schemas 1.59, main 0.97, routes/eval 0.91; 143 Task/Audit refs in api/
```
