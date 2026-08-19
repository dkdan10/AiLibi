# Agent Prompt — 20.19 Two byte-identical speed-ups: the cached Jinja environment and the bisecting episodic scan

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.19 — Two byte-identical speed-ups: the cached Jinja environment and the bisecting episodic scan, anchored to C-42 + C-43 [both P1, adversarially CONFIRMED] — audits/review-2026-08-19/B/collated-findings.md rows C-42 and C-43; audits/review-2026-08-19/B/perf-runtime.md §3 F1, §3 F2, §5 (the lifetime-conflation and derived-view-sprawl diagnoses) and §6 R1/R2/R3; audits/review-2026-08-19/B/verdicts.md (the C-42 verdict corrects the win to 1.20x, REFUTES the "the cache key must include the roll-call lever" caveat, and corrects "the production path never uses `_ENV`" — `_ENV` is the live default for the `experiments/lab/` wrappers; the C-43 verdict reproduces 5,160 `recent()` calls and 3,158,709 event-visits exactly, measures 1.34x and 1.27x on long games, and records that the bisect ALONE is not enough — the full-log tuple must also be cached); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 1, the C-42 + C-43 row ("replay SHA unchanged; A/B ratios reproduce"). Anchors re-verified at HEAD f1e970a4: agents/strategic/prompts/loader.py:194-235 `resolve_prompt_set`, :238-266 `build_environment`, :272 the import-time `_ENV`, :683 + :711 `build_prompt_renderers` calling `build_environment` on every construction, :712-718 the impostor-roll-call lever selecting template FILENAMES outside the environment; orchestrator/game.py:858 + :910-911 a fresh runner — and therefore a fresh environment — per game; agents/memory/episodic.py:96-117 `append` with its non-decreasing-tick guard and :119-122 the linear `recent()`; 32 non-test `.recent(` call sites of which 29 pass `since_tick=0` — 13 in agents/memory/store.py, orchestrator/game.py:2758,2819,2870,2921,2988,3049, agents/perception.py:284, agents/tactical/crewmate_policy.py:304 and :361, agents/tactical/impostor_policy.py:266, agents/tactical/features.py:471, agents/tactical/learned/forward.py:252, agents/tactical/learned/crew_forward.py:342, api/replay_loader.py:2308, training/crew/options.py:349 and training/bakeoff/utility_es.py:270, the only three windowed callers being agents/perception.py:143 taking since_tick=tick, :315 taking since_tick=earliest_tick and agents/tactical/features.py:392 taking a tick-minus-window bound; tests/agents/test_memory.py:26-92 the existing `recent()` behaviour pins; tests/meetings/test_prompt_byte_golden.py:835-840, :1089 and :1149-1160 the golden and one-byte-perturbation legs, each built against its own root.. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-byte-identical-speedups`
**Depends on:** 20.5 — the loader's first-run-notice change lands first, so the two edits to the prompt-loader module and its test file serialise instead of colliding, and this memo is layered beneath an already-settled set-resolution path.
**Section refs:** C-42 + C-43 [both P1, adversarially CONFIRMED] — audits/review-2026-08-19/B/collated-findings.md rows C-42 and C-43; audits/review-2026-08-19/B/perf-runtime.md §3 F1, §3 F2, §5 (the lifetime-conflation and derived-view-sprawl diagnoses) and §6 R1/R2/R3; audits/review-2026-08-19/B/verdicts.md (the C-42 verdict corrects the win to 1.20x, REFUTES the "the cache key must include the roll-call lever" caveat, and corrects "the production path never uses `_ENV`" — `_ENV` is the live default for the `experiments/lab/` wrappers; the C-43 verdict reproduces 5,160 `recent()` calls and 3,158,709 event-visits exactly, measures 1.34x and 1.27x on long games, and records that the bisect ALONE is not enough — the full-log tuple must also be cached); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 1, the C-42 + C-43 row ("replay SHA unchanged; A/B ratios reproduce"). Anchors re-verified at HEAD f1e970a4: agents/strategic/prompts/loader.py:194-235 `resolve_prompt_set`, :238-266 `build_environment`, :272 the import-time `_ENV`, :683 + :711 `build_prompt_renderers` calling `build_environment` on every construction, :712-718 the impostor-roll-call lever selecting template FILENAMES outside the environment; orchestrator/game.py:858 + :910-911 a fresh runner — and therefore a fresh environment — per game; agents/memory/episodic.py:96-117 `append` with its non-decreasing-tick guard and :119-122 the linear `recent()`; 32 non-test `.recent(` call sites of which 29 pass `since_tick=0` — 13 in agents/memory/store.py, orchestrator/game.py:2758,2819,2870,2921,2988,3049, agents/perception.py:284, agents/tactical/crewmate_policy.py:304 and :361, agents/tactical/impostor_policy.py:266, agents/tactical/features.py:471, agents/tactical/learned/forward.py:252, agents/tactical/learned/crew_forward.py:342, api/replay_loader.py:2308, training/crew/options.py:349 and training/bakeoff/utility_es.py:270, the only three windowed callers being agents/perception.py:143 taking since_tick=tick, :315 taking since_tick=earliest_tick and agents/tactical/features.py:392 taking a tick-minus-window bound; tests/agents/test_memory.py:26-92 the existing `recent()` behaviour pins; tests/meetings/test_prompt_byte_golden.py:835-840, :1089 and :1149-1160 the golden and one-byte-perturbation legs, each built against its own root.
**Complexity:** Small
**Record impact:** none — no lever is introduced, no template byte moves, no committed artifact is regenerated, and both changes are replay-byte-identical, so the Phase-20 adopting record is untouched by this task.
**Measurement:** `bash scripts/verify_samples.sh` re-walks 100/100 committed replays clean; three 9p2i fake-provider games recorded with `uv run python scripts/run_game.py --seed <s> --num-players 9 --num-impostors 2 --tasks-per-crewmate 2 --replay-path <tmp>/r-<s>.jsonl` have `shasum -a 256` digests identical to the same three seeds recorded on the merge-base; `uv run pytest tests/agents tests/meetings/test_prompt_byte_golden.py -q` green; and `time uv run python scripts/run_tournament.py --num-games 10 --roster-preset 9p2i --output-dir <tmp>` quoted before/after — three interleaved legs per arm with the `uptime` load average beside each, expected direction: faster, with the review-measured references 1.20x from the environment memo and 1.27–1.34x on long games from the bisect.

Two accidental costs sit in the hot path of every LLM-free game, and the review measured
both, fixed both by monkeypatch, and proved both byte-identical before recommending
anything. First: `build_prompt_renderers` builds a fresh `jinja2.Environment` on every
call (agents/strategic/prompts/loader.py:711), and `build_default_meeting_runner` is
constructed once per game by design (orchestrator/game.py:910-911), so the three to four
meeting templates are re-lexed, re-parsed and re-compiled per game. The 10-game
tournament profile in audits/review-2026-08-19/B/perf-runtime.md §2.4 attributes 0.405 s
of 2.52 s — 16 % — to `jinja2/loaders.py:107(load)`; the adversarial re-measurement in
audits/review-2026-08-19/B/verdicts.md reads 0.369 s / 14.7 % and, decisively,
`Environment.__init__ == 11` for ten games — one import-time `_ENV` plus one per game.
A fresh environment plus four compiles costs 15.6 ms; the warm cache costs 0.010 ms.
Second: `MemoryStore.recent()` (agents/memory/episodic.py:119-122) is a full-log generator
scan, although `append` (:96-117) already raises on a decreasing tick and is the only
mutator of `_events` anywhere in the repo. The invariant that makes the scan unnecessary
is enforced and unused. The consequence is Θ(T²) agent cost: the review's instrumented
`_collect_intents` rises cleanly from 0.35 ms/tick at tick 0 to 2.11 ms/tick at tick 120,
and one 119-tick 9p2i game makes 5,160 `recent()` calls visiting 3,158,709 events.

Neither fix changes a byte that anyone records. Both were A/B'd inside one process with
the replay SHA-256 compared across arms and found identical — the environment memo at
1.24x claimed and 1.20x re-measured, the bisect-plus-cache at 1.28x claimed and
1.34x / 1.27x re-measured on long games (all figures review-measured on the reviewer's
macOS box under load averages of 5.7–10.4, and to be reproduced, not trusted, by this task).
That is why this contract's record impact is none: there is no recording to shorten here,
and audits/review-2026-08-19/D/cross-track-map.md is explicit that these two do not
shorten the ~23 h re-record, which is LLM-bound. What they do shorten is everything the
rest of Phase 20 leans on — the default test gate, the eval harness, and every offline
counterfactual a lever task runs over committed bytes.

Two review claims are wrong at HEAD and this contract corrects them rather than
inheriting them. The recommendation in perf-runtime.md §6 R1 says the cache key should
include the roll-call lever; it must not, and need not — the lever is read in
`build_prompt_renderers` at loader.py:712 and only chooses which template FILENAMES the
renderers bind, while `build_environment` at :238-266 never reads it. And F1's aside that
the module's `_ENV` is dead code is false: it is the live default for the module-level
wrapper callables (loader.py:382, :463, :583, :647) that `experiments/lab/` drives.
`_ENV` stays exactly where it is; after this task it simply becomes the first entry in
the memo instead of the one environment in eleven that the game path never reached.

The scope is deliberately the cheap half. The structural fix — O(1) incremental
accessors for the three per-tick recomputations at agents/perception.py:143,284,315 and
one pass replacing the thirteen independent projections in agents/memory/store.py — is
perf-runtime.md §6 R3, a day of work that touches the render path, and it is recorded
here as out of scope rather than left silent. This task keeps the public signature of
`recent()` and every call site's arguments untouched, which is what makes the byte
identity provable in one diff.

**Files in scope:**
- agents/strategic/prompts/loader.py; (memoize the Environment per resolved set and root — the AGENTS.md no-mutable-global rule is respected because the memo is `functools.lru_cache` over a pure constructor, holding no game state)
- agents/memory/episodic.py; (bisect on the sorted tick index; a cached full-log tuple invalidated on append)
- tests/agents/test_prompt_loader.py; (the memo: same object for the same key, different for a different set or root; an in-process AILIBI_PROMPT_SET change still re-resolves; the unknown-set raise still fires on every call)
- tests/agents/test_episodic_ids.py; (recent() equivalence against a linear reference over random legal logs, plus the structural bisect and invalidation pins)
- tests/agents/test_memory_store.py; (no render change: render_for_prompt is byte-identical over a fixture)

**Files NOT in scope:**
- agents/perception.py and agents/memory/store.py (every call site keeps its `since_tick` argument; the speed-up lives entirely inside `recent()`, and the O(1)-accessor rewrite is perf-runtime.md §6 R3, explicitly deferred)
- orchestrator/, api/, training/, eval/ (no API change and no call-site edit; `build_default_meeting_runner`'s documented per-game freshness of the budget and the recording client is preserved untouched)
- eval/balance_eval.py (the process-parallel tournament is perf-runtime.md §6 R4, a separate change)
- replays/ and any committed artifact (reconstruction must stay byte-identical; `scripts/verify_samples.sh` is the pin)
- agents/strategic/prompts/*.j2 (no task in this phase edits a game prompt template except the single prompt-set bump; a memo over template loading must not become an excuse to touch one)
- orchestrator/replay.py (this task introduces no lever, so there is no substrate-stamp registration to do)
- tests/agents/test_memory.py (the existing `recent()` behaviour pins at :26-92 are the regression evidence: they stay untouched and must stay green)

**Definition of done:**
- [ ] Byte identity is proved, not asserted: three 9p2i fake-provider seeds recorded before and after the change produce replay JSONL files with identical `shasum -a 256` digests, and `bash scripts/verify_samples.sh` re-walks all 100 committed replays clean; both outputs are pasted into the PR Summary.
- [ ] `build_environment` keeps its signature and its behaviour — it resolves the set, rejects an unknown set with `ValueError`, and then returns an environment memoized on the resolved set name and the templates root. `tests/agents/test_prompt_loader.py` pins that two calls for one set return the same object, that a different set and a different `root` each return a different object, and that the environment carried by two separate `build_prompt_renderers` bundles for one set is one object.
- [ ] The memo sits strictly beneath resolution: `resolve_prompt_set` is still called once per `build_environment` call, so the bare-fallback stderr notice that Task 20.5 leaves in place fires exactly as often as it did before. `tests/agents/test_prompt_loader.py` pins the notice count over N consecutive `build_prompt_renderers` calls under a real-provider environment — that count is ONE, because Task 20.5 landed the notice as a once-per-process `functools.lru_cache` memo on `_notify_bare_prompt_set_fallback` (loader.py:148-149) which the file's autouse `_reset_bare_fallback_notice` fixture clears around every test.
- [ ] An in-process prompt-set change still re-resolves: `build_environment` called with `env={ENV_PROMPT_SET: "qwen3_32b"}` and with `env={ENV_PROMPT_SET: "qwen3_5_9b"}` returns two different environments, each bound to its own set, and an unknown set raises `ValueError` on the second call as well as the first — the memo caches no failure. Pinned in `tests/agents/test_prompt_loader.py`.
- [ ] The impostor-roll-call lever is NOT part of the key, with the reason recorded in one line at the memo: the lever chooses template filenames at loader.py:712-718, outside the environment. `uv run pytest tests/agents/test_impostor_answer_arm.py tests/agents/test_bespoke_prompt_sets.py -q` stays green, including the ON-with-a-variant-less-set `ValueError`.
- [ ] `MemoryStore.recent()` locates its window with one `bisect_left` over a tick index maintained in `append`, and returns a cached materialized tuple when the window starts at index 0; the full-log generator expression at episodic.py:122 is gone. The public signature, the return type, and the append-order guarantee are unchanged.
- [ ] `tests/agents/test_episodic_ids.py` pins output equivalence against a linear reference implementation over at least 1,000 randomly generated legal append sequences — including duplicate ticks, gaps, and negative and past-the-end `since_tick` values — with zero mismatches, and pins structurally that exactly one `bisect_left` call occurs per `recent()` call.
- [ ] The full-log cache is invalidated on write: `recent(since_tick=0)`, then `append`, then `recent(since_tick=0)` returns the longer tuple including the new event; the duplicate-observation-id and non-decreasing-tick guards still raise, and a rejected `append` leaves the tick index and the cache consistent with `_events`.
- [ ] No render change: `tests/agents/test_memory_store.py` pins that `render_for_prompt` produces byte-identical output over a fixture store before and after the change, with the expected bytes committed as the fixture rather than recomputed at assert time.
- [ ] Both new gates are shown able to fail: the PR quotes the failing output produced by temporarily restoring the linear generator in `recent()` and by temporarily removing the append-time cache invalidation.
- [ ] The 10-game fake-provider tournament timing is quoted before and after with the load average beside each leg, using interleaved arms in the same session rather than one run per arm.
- [ ] Provenance discipline: each touched function gains at most one line naming this task and the finding it closes; no narration of the change's history beyond that.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

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
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-20-byte-identical-speedups` with a title like `task 20.19: two byte-identical speed-ups: the cached jinja environment and the bisecting episodic scan`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing C-42 + C-43 [both P1, adversarially CONFIRMED] — audits/review-2026-08-19/B/collated-findings.md rows C-42 and C-43; audits/review-2026-08-19/B/perf-runtime.md §3 F1, §3 F2, §5 (the lifetime-conflation and derived-view-sprawl diagnoses) and §6 R1/R2/R3; audits/review-2026-08-19/B/verdicts.md (the C-42 verdict corrects the win to 1.20x, REFUTES the "the cache key must include the roll-call lever" caveat, and corrects "the production path never uses `_ENV`" — `_ENV` is the live default for the `experiments/lab/` wrappers; the C-43 verdict reproduces 5,160 `recent()` calls and 3,158,709 event-visits exactly, measures 1.34x and 1.27x on long games, and records that the bisect ALONE is not enough — the full-log tuple must also be cached); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 1, the C-42 + C-43 row ("replay SHA unchanged; A/B ratios reproduce"). Anchors re-verified at HEAD f1e970a4: agents/strategic/prompts/loader.py:194-235 `resolve_prompt_set`, :238-266 `build_environment`, :272 the import-time `_ENV`, :683 + :711 `build_prompt_renderers` calling `build_environment` on every construction, :712-718 the impostor-roll-call lever selecting template FILENAMES outside the environment; orchestrator/game.py:858 + :910-911 a fresh runner — and therefore a fresh environment — per game; agents/memory/episodic.py:96-117 `append` with its non-decreasing-tick guard and :119-122 the linear `recent()`; 32 non-test `.recent(` call sites of which 29 pass `since_tick=0` — 13 in agents/memory/store.py, orchestrator/game.py:2758,2819,2870,2921,2988,3049, agents/perception.py:284, agents/tactical/crewmate_policy.py:304 and :361, agents/tactical/impostor_policy.py:266, agents/tactical/features.py:471, agents/tactical/learned/forward.py:252, agents/tactical/learned/crew_forward.py:342, api/replay_loader.py:2308, training/crew/options.py:349 and training/bakeoff/utility_es.py:270, the only three windowed callers being agents/perception.py:143 taking since_tick=tick, :315 taking since_tick=earliest_tick and agents/tactical/features.py:392 taking a tick-minus-window bound; tests/agents/test_memory.py:26-92 the existing `recent()` behaviour pins; tests/meetings/test_prompt_byte_golden.py:835-840, :1089 and :1149-1160 the golden and one-byte-perturbation legs, each built against its own root.), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
