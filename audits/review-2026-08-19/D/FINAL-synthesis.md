# AiLibi — FINAL synthesis (Track D judge)

**Inputs read in full:** `D/cross-track-map.md`, `D/synth-pragmatic.md`, `D/synth-ambition.md`,
`D/synth-credibility.md`; `A/collated-findings.md` (G-1…G-41 + 43 merged ideas), `A/verdicts.md`
(12 adversarial re-derivations), `A/ideas-summaries.md`, `A/ux-visual-pass-lead.md`;
`B/collated-findings.md` (C-1…C-130, §7 strengths, §8 root causes), `B/verdicts.md` (14 verdicts);
`C/collated-portfolio.md` (A1–A6, B1–B13, D1–D9, E, F). Repo read at `main b809b19c`, read-only.

**Sizes:** S ≤ ~1 day · M ~2–5 days · L > a week / a chartered phase.
**RR** = needs the real-LLM re-record (~23 h operator wall, $0 flat-rate) before the committed
baseline can move. **RR-free** = ships today with every gate green.

**[D-VERIFIED]** marks the eight facts I re-checked myself at HEAD rather than inheriting:
`.importlinter root_packages` = `agents, engine, llm, meetings, observation, training` (no
`orchestrator`/`api`/`eval`/`scripts`) → **C-32 confirmed**; committed
`replays/samples/9p2i/tournament-eval-report.json` `"vote_correctness_rate": 0.9230769…` against a
docstring saying "structurally pinned to 1.0" → **C-113 confirmed**; `detect_contradictions`
(`meetings/transcript.py:1414`) takes `vent_witness_records` and **no** `sighting_records` → **C-11
confirmed at the signature**; `vote_ballot.j2:100` "Each flag below is VERIFIED evidence" verbatim →
**G-2 confirmed**; `store.py:1160-1166` "Its owned set only ever shrinks" verbatim → **C-2/G-3
confirmed**; `adjust_trust` has exactly one hit outside `tests/` — its own definition at
`beliefs.py:1111` → **C-72 confirmed**; `README:47/74/78` carry "zero observation-firewall
violations", "import-linter enforced", "(suspicion, trust, alibi)" verbatim. And one **correction**:
`README.md` mentions `vote_correctness` **nowhere** — C-113's "the README sells it as the
circularity guard" leg is **refuted**; the surface that repeats it is the Tournament tooltip
("sentinel — not a KPI", G-41). The docstring-vs-data contradiction stands; the fix is smaller than
credibility priced it.

---

## 0. The judgment in five sentences

1. **The code is right and the game is wrong.** Track B found no P0 in 130 findings; Track A found
   eight. Both are correct: nearly every gameplay P0 is a faithful implementation of a rule nobody
   would have written after watching it run (G-1, G-2, G-5, G-8, G-19), and nearly every code P1 is
   a latent hazard no spectator can reach (C-1, C-6, C-12, C-31, C-32). Say this out loud in the
   portfolio — it is a mature engineering observation and it explains how 4,600 passing tests and a
   19-phase audit trail coexist with a game in which 20.5% of crew testimony is invented.
2. **One channel decides the game and it is anti-informative.** STRONG `alibi_vs_sighting` names an
   impostor 11.7% of the time against a 26.1% base rate (C-11, p=0.0048), is 14.6% precise as sole
   convicting evidence (12 right / 70 wrong, G-2 verdict), carries 70 of 79 wrongful ejections, and
   is labelled "VERIFIED evidence" to 2,543/2,543 recorded voters [D-VERIFIED]. Its grounding
   machinery already exists and is wired only to the *exculpatory* side.
3. **A one-line comment, a config flip and a test that enshrined the wrong behaviour** put
   fabricated first-hand memories into 159 of 300 committed games, one-sidedly against the crew
   (G-3 ↔ C-2, both CONFIRMED independently, with two separate repros).
4. **The demo is the star-making asset and the least-tested layer in the repo** — 1,182 of 1,769
   committed frames (66.8%, 50/50 games) paint corpses the engine already deleted (C-7), on the
   surface five of six hiring personas said would decide the star, in a package whose test:prod
   ratio is 0.15 against 1.6–2.8 for Python (C-101).
5. **The project's docs are already more honest than its prompts and its gates.**
   `docs/reading-guide.md:196` discloses that the flag doctrine convicts innocents while
   `vote_ballot.j2:100` still says VERIFIED, and `eval/leak_scan.py` cannot see the axis
   `DESIGN.md:933` calls "the most important test" (C-31: mutation M6 survives all four suites).
   Closing that gap converts the project's best trait from a disclosed caveat into a shipped result.

---

## 1. The eight root causes

Ordered by the number of findings they generate across all three tracks. Every finding in this
review is downstream of one of these.

### RC1 — The agent has no record of *itself*
No dated self-location line exists in 971 rendered memories; the store already keeps
`own_room_by_tick` (`store.py:1025-1028`) and uses it only to scope *others'* sightings. The one
self-placing shape — the `You completed X (you were in ROOM)` suffix — is mis-dated (matches the
agent's real room at tick N **16.0%**, at N−1 **97.0%**). Nothing about a prior ejection, verdict,
revealed role, or absence survives a meeting: **0 of 7,458** meeting prompts record any prior
ejection or its role.
**Gameplay:** G-1, G-21, G-22, G-23, G-30, G-35, part of G-9a. **Code:** C-10 (belief line
contradicts the observation list in the same prompt), C-71 (`WorkingMemory` is scaffolding plus a
render-time cache), C-72 (`trust` never written [D-VERIFIED]; `## Open contradictions` in 0/1,656
renders), C-73, C-117, C-29.
**Portfolio:** directly falsifies README:78's "(suspicion, trust, alibi)".

### RC2 — Unverified speech is stamped VERIFIED; provenance is checked on the exculpatory side only
`_iter_sightings` yields every spoken sighting unfiltered; `detect_contradictions` cannot ground the
prosecutorial channel [D-VERIFIED]; the identical machinery (`SightingRecord`, Task 16.7) is wired
to the −0.05 vouch. Two independent censuses with different denominators agree: 70 of 79 wrongful
ejections (Track A) and 20 of 25 (Track B) ride this one class.
**Gameplay:** G-2, G-4 (`saw_player` half), G-9a, G-19, G-31, G-32, G-36. **Code:** C-11, C-129,
C-15, C-19, C-120. **Portfolio:** the reading guide already discloses it; the close audit already
scoped it (`audit-phase-19-close.md` §4.2 item 1).

### RC3 — A false invariant in the memory store, broken two phases later by a map-config flip
`dead_task_rule: redistribute` grows `owned_task_ids`; `store.py:1157-1200` infers a completion from
any `pending_task_id` change under a comment asserting the opposite [D-VERIFIED]; the inference is
gated to `role == "CREWMATE"`, so the bug is strictly one-sided against the crew; a test
(`test_pending_rollover_to_next_map_id_emits_completion`) pins the wrong rule; `DESIGN.md` documents
only the retired `drop` rule.
**Gameplay:** G-3 (10.0%/23.1% of completion lines false, 159/300 games, 67 spoken at the table,
3 minted STRONG flags against innocents), G-16 (485 progress reversals). **Code:** C-2, C-24, C-119,
C-115. **Portfolio:** the best bug story in the repo.

### RC4 — Lexicographic actor id is load-bearing at three layers and documented at none of them
**Gameplay:** G-10 (156/156 lower-id victims escape, 90/90 higher-id die; per-seat escape 24.7% →
0%), G-11, G-18. **Code:** C-22 (witness membership), **C-3** (the same `(-score, player_id)` tie-break
declines **190/415 = 45.8%** of free zero-witness kills, 168/168 on exact 1.0 ties), C-4 (34% of
stalk moves chase a refuted sighting), C-95 (a tie-break that can never fire), C-25.
**Portfolio:** determinism ≠ fairness — `DESIGN.md:334` already says so; and C-3 re-frames the
project's own long-running "the impostor never wins / the meeting never decides" narrative as partly
a target-selection bug measured on a hobbled inner loop.

### RC5 — The private dialect leaks to every surface
One habit, five surfaces, flagged by every C persona and tripped over by every A watcher.
**Gameplay:** G-25 (a dev marker inside quoted dialogue in 12.6% of prompts), G-26, G-29 ("0.60
threshold" ×208), G-41 (task numbers in product tooltips). **Code:** C-67 (nine marker literals
parsed by four packages, the `]` terminator load-bearing), C-63 (1,896 `Task N.M` refs in source),
C-129, C-121. **Portfolio:** C/A2 (6 of 11 glossary terms undefined in the README, ≥15 defined
nowhere), C/B6, C/B7.

### RC6 — "Preserve the exact prior bytes" applied beyond its remit
**Code:** C-64 (10 accept-and-ignore resolvers + 13 `ENV_*` constants + 152 test lines), C-104 (~70
tautology assertions whose docstrings say the opposite), C-37, C-130 (a version-bumped template with
**0 of 7,932** calls; the *default* prompt set used by no committed replay), C-102, and the tax on
C-10/C-15/C-29/C-73. **Gameplay:** G-27 — a one-word wording fix blocked behind a template-version
cascade *and* a re-record. **Fix:** the render-version stamp, plus one deletion pass.

### RC7 — Gates validate shape, not entitlement — and several validate nothing
**Code:** C-31 (the scanner takes no `WorldState`/`VisibilityResult`; M6 — every undiscovered body
visible to everyone — survives all four suites with an empty whole-suite diff), C-32 [D-VERIFIED]
(contract coverage 89 of 383 tracked `.py`), C-6 (the corpus acceptance gate reads truncation as a
legitimate `TICK_BUDGET`), C-103 (three tally tests pass on a 4×SKIP tally), C-113, C-40, C-34 (the
loudest gate flakes red: 2 of 12 concurrent `lint-imports` runs printed a false BROKEN).
**Gameplay:** G-20 (the SKIP-plurality rule that decides outcomes is the least-tested rule in the
meeting). **Portfolio:** everything under C/E2 and README:47/74. The honest counterweight B insisted
on: the plant-detect-cleanup pattern, the one-byte perturbation golden and `check_doc_facts.py` are
the *right* instinct — the failures are location and scope, not culture.

### RC8 — The spectator surface derives from the wrong source and is the least-tested layer
**Gameplay:** G-38 (bodies never cleared; 1,747 fake `do_task` render as IDLE 800 / MOVING 844 /
TASK 0), G-41. **Code:** C-7, C-80 (MapView's five pure derivations live in `.tsx` the node-only
vitest project cannot import — *which is why C-7 went unnoticed*), C-101, C-120, C-8, C-9, C-58,
C-79, C-90. **This is the only root cause that is entirely RR-free.**

---

## 2. Claim-by-claim credibility grade

**HOLDS** = survives a hostile reader · **CAVEAT** = true as written, a named qualification is
missing · **UNDERMINED** = falsifiable as worded.

| # | Claim (where it lives) | Grade | Why | Repair |
|---|---|---|---|---|
| 1 | Tick-based deterministic engine, bit-exact replays (README:74, ADR #1) | **HOLDS** | The only claim three blind tracks all tried and failed to break: byte-identical hash chains over 3 seeds × 400 ticks under two `PYTHONHASHSEED`s, run-twice byte-identical replay *and* audit JSONL, 300-game/28,362-tick fuzz with 0 violations, `verify_samples.sh` 100/100 in 3.14 s; plus A's independent gameplay-level integrity audit (0 teleports in 16,453 room changes, 188/188 kill rejections explained, 0 dangling ids in 3,814 ballots) | none — **under-sold**, see §3 |
| 2 | "zero observation-firewall violations" (README:47) | **HOLDS** | No live leak exists on `main`; every reviewer says so; the boundary is a genuine chokepoint (B §7.4) | keep, reword per C/B9 |
| 3 | "agents cannot import engine directly or transitively (import-linter enforced)" (README:74) | **UNDERMINED** [D-VERIFIED] | True only for hops via the six root packages; a planted `agents/_probe_orch.py` importing `orchestrator.game` reports `4 kept, 0 broken` with `check.sh` fully green (C-32) | C-32 + C-34 + C-31, then restate precisely |
| 4 | "the most important test" / the leak scanner (DESIGN.md:933) | **UNDERMINED** | It receives no `WorldState`/`VisibilityResult` and cannot check entitlement; M6 takes `body_views 33 → 249` and passes all four suites, ML champion gate included (C-31) | C-31 (M) |
| 5 | "Memory is structured first… a derived belief state (suspicion, trust, alibi)" (README:78, ADR #3) | **UNDERMINED** [D-VERIFIED] | `trust` has zero production writers; `## Open contradictions` renders 0/1,656 (C-72); the typed log renders 10.0–23.1% fabricated completions (C-2/G-3); no self-location line exists at all (G-1) | wording now (S); substrate later (RR) |
| 6 | "520/520 eject ballots carry a valid citation" | **CAVEAT** | Citation *hygiene* is perfect and independently re-derived. But "valid" means **resolvable**, not **supported**: 63.5% of resolvable sighting-sides were never perceived by that speaker; seed 12's ballot cites the observation that *refutes* its own flag | one sentence, then the S4 fix |
| 7 | "Deception: demonstrated, the strongest capability on display" | **CAVEAT** | Real — impostors mint "VERIFIED" flags against innocents in 15.1% of the class. But it **rides the defect**: fixing C-11 will *reduce* measured deception. Publishing it as a capability the month before removing its mechanism is the compounding risk only a blind cross-track read exposes | say it in the same paragraph |
| 8 | "General social deduction: NOT demonstrated" (reading-guide §3) | **HOLDS, under-stated** | A raises it from "87% ride a vent" to a mechanism: "did a flag fire" predicts the outcome 88.5–100% (G-19); spoken confidence 0.6–0.8 converts *below* the 25–29% random baseline (G-30); vote-time conviction retains 19.1% (G-21) | lead with it (A6) |
| 9 | ML NO-FLIP rigor / "+0.12–0.30 win edge over the same-seed FSM" | **CAVEAT — the method holds, one input is contaminated** | Method verified three ways (54 offline re-derivations in 20 s, 0 failures; the NO-GO survives a 100× epoch / 300× lr sweep; pre-registration → measurement → ruling ordered in git). The **comparator** discards 45.8% of its free kills on an id tie-break (C-3) and spends 8–12% of decisions stalking ejected players (G-12), both 9p2i-only, both depressing the FSM | state it first (S text), fix in wave 2 |
| 10 | "300+ merged PRs, every one green through the same full gate" | **CAVEAT** | 346 merged (conservative). Two exceptions: CI also runs a Playwright job `check.sh` does not (C-125), and 317 campaign-tier tests (6.4%) are schedule-only and invisible to every PR (C-99) | one line each |
| 11 | "one bad replay no longer blocks the picker" (`api/replay_loader.py:716`) | **UNDERMINED** | A truncated last line 500s the whole listing *and* `cost_summary`; an empty file is served as a valid 0-tick replay and counted (C-5). This is the X1 front-door path | one `except ValueError` (S) |
| 12 | `vote_correctness_rate` "structurally pinned to 1.0 … any value below 1.0 is a detector/recording bug to chase" | **UNDERMINED — with a correction** [D-VERIFIED] | The committed 9p2i report reads **0.9230769**. But `README.md` never mentions the metric: C-113's README leg is **refuted**; the repeating surface is the Tournament tooltip | docstring + investigate the 6 zero-flag ejections (S) |
| 13 | The spectator as the demo asset | **CAVEAT — the caveats block hosting** | Unanimous praise ("a better LLM-agent debugging surface than most commercial agent tools ship"). And 66.8% of frames paint phantom corpses (C-7); the `CORRECT` badge spoils role in unspoiled mode; the prompt panel — the best feature — shows a prompt that says "a hidden impostor" and "Your fellow saboteurs: p-8" 90 lines apart in 100% of 2-impostor games (G-27) | wave 0 |
| 14 | Reproducibility scope 3 (cross-platform optimizer portability, "designed for, not yet confirmed") | **UNRESOLVED — do not touch** | B measured the ES golden digest reproducing bit-identically on Darwin-arm64; the owner's own working note says committed ES artifacts reproduce only inside the Linux container. Two different digests may be in play | one controlled owner-run, or leave the honest hedge |
| 15 | In-code provenance references (`audits/`, `tasks/`) | **HOLDS** | 43 of 44 cited paths resolve on disk — maintained, not rotted (B §7.30) | cite it as evidence |
| 16 | `check_doc_facts.py` guards the README's numbers | **HOLDS** | It runs against the real repository inside the normal gate | extend it with every new headline number |

**Net:** the front door does not lie. Its exposure is four undisclosed items that contradict the
project's own stated pillars (#3, #4, #5, #9) plus one demo surface that visibly malfunctions
(#13) — and the presentation phase's first act was going to publish that demo.

---

## 3. Where the project is stronger than it claims (fold into the front door, cost: text)

1. `tests/meetings/test_prompt_byte_golden.py` re-runs the **real** `MeetingManager` over 204
   committed meetings, explicitly refuses to re-implement the assembly ("a second source of truth and
   a dishonest golden"), and ships `test_one_byte_template_perturbation_breaks_the_golden` — *"a
   golden that cannot fail is not a gate."* 7 s. Named nowhere on the front door.
2. The ML negative is **robust, not merely honest**: it survived a 100× epoch / 300× lr sweep. The
   docs say "we didn't ship it"; they never say "and we tried to break our own negative and could not."
3. A corpus-level integrity audit exists and is unwritten: 0 teleports in 16,453 room changes,
   188/188 kill rejections explained with 0 unexplained, 0 double reports in 626, 0 dangling ids in
   3,814 ballots, 0/929 impostor ballots naming a partner (A §E). Stronger and more specific than the
   run-twice `diff`, and free — the measurements already exist.
4. The vent channel is a **perfect end-to-end pipeline** — perception → memory → speech → flag →
   ballot → tally, `vent_sighting` 440/440 precise at n=440 — and is only ever described as a
   limitation.
5. Zero `type: ignore` in any production package under `mypy --strict`; zero TODO/FIXME/HACK across
   121,367 lines; zero `any`/`@ts-ignore` in the frontend under `noUncheckedIndexedAccess`.

---

## 4. The roadmap

Ordering rule: **anything that needs the re-record must land before it; everything that does not
ships now.** One prompt-version bump carries every prompt edit (the `.j2` marker →
`orchestrator/game.py::PROMPT_VERSION_SETS`/`DEFAULT_PROMPT_VERSIONS` → the live-recorded
prompt-version pin → `scripts/regen_test_goldens.py`).

### Wave 0 — this weekend (≤2 days, $0, RR-free, zero gameplay risk)

Nothing here repeats a claim that is currently false, so it does not block on wave 1.

| # | ids | Change | Files | Size | Rationale | Measurement |
|---|---|---|---|---|---|---|
| 0.1 | **C/A4** | GitHub About + ≥8 topics + homepage + CI/MIT/Python badges + byline | repo settings, `README.md` head | S (15 min) | "On the repo card there is literally nothing but the name" (P4). Zero code; unblocks the 1-second health check for the audience most likely to bounce | About non-empty, topics set, homepage set |
| 0.2 | **C-7 / G-38 / A-F41** | `buildBodyStatesByTick` consumes `TickView.bodies` instead of accumulating kill events; add the first `MapView.test.ts` | `frontend/src/components/MapView.tsx:227-264,570,591,734` | S | **67% of frames on the demo's central surface are wrong, in 50/50 games.** You cannot host a demo that paints corpses the engine deleted. Also revives the already-correct `killed_by` field | re-run B's probe: `phantomFrames 1182 → 0`; a component test exists where C-101 says none does |
| 0.3 | **G-41 / C/B6 / C-9** | Strip `(DESIGN.md §11.3)` / `Task 9.6` / `INTERNAL HEURISTIC` from product copy; expand "4p1i/9p2i" once; legend the R1/R2/R3/R7 bars; un-fix the dock below ~800 px; hide the ballot `CORRECT` badge in unspoiled mode; delete GuidedTour's inline focus-trap copy | `frontend/src/components/{TournamentDashboard,MeetingView,ReplayPicker,ReplayControls,GuidedTour}.tsx`, `hooks/useFocusTrap.ts` | S | RC5 on the product surface, plus the keyboard lock that fires during the demo's opening move | `grep -E "DESIGN\.md §|Task [0-9]+\.[0-9]+" frontend/src` → 0 in user-facing copy; map visible at 1280×800; Tab advances the tour over an open meeting |
| 0.4 | **C-5** | One `except ValueError` in `list_replays`/`cost_summary` (pydantic's `ValidationError` **is** a `ValueError`); skip zero-byte files instead of serving them as 0-tick replays | `api/replay_loader.py:703-778` | S | One Ctrl-C'd tournament 500s the whole picker — and the README hands a stranger a tournament command. It also makes `:716`'s own docstring true | B's repro dir (truncated + empty + invalid) → listing 200 with the healthy replays present |
| 0.5 | **C/B1 + C-83 + C-126** | Silence the `AILIBI_PROMPT_SET` fallback notice under the fake provider; document the variable beside `AILIBI_LLM_PROVIDER` | `agents/strategic/prompts/loader.py:238-242`, `.env.example`, `README.md` | S | It is the **first output every verifier sees**, printed 6× by the README's own 5-game example, for a variable documented in no `.md` | the three front-door commands produce zero unexplained stderr |
| 0.6 | **C/B2** | Point the README's report example at `replays/samples/9p2i/tournament-eval-report.json`; say what fake-provider output looks like and why | `README.md` | S | The tournament command the README hands out yields an all-null report — mechanism is C-88 (`fake-target-<hash>` ⇒ every fake ballot normalises to SKIP) | a reader following the README sees a populated report |
| 0.7 | **C-113** | Correct the docstring to match reality; open one investigation of the 6 zero-flag impostor ejections; extend `check_doc_facts.py` to pin the committed value | `eval/vote_correctness.py:11-31` | S | The repo's own sentinel is red on its flagship artifact and nothing surfaces it. **Correction: the README does not carry this claim** [D-VERIFIED] — the fix is a docstring and a tooltip, not a README edit | docstring and committed data agree; `check_doc_facts` fails if they diverge again |
| 0.8 | **C/A3(a)** | `.github/workflows/pages.yml` (~15 lines) building `frontend/dist/demo-bundle`; URL into About + README line 1 | new workflow | S | "For this audience the URL *is* the project" (P3). Today every reader must clone ~256 MiB to see anything move. Because Pages rebuilds on push, a future re-record refreshes the demo for free — this is why hosting now is not work done twice | `frontend/e2e/bundle.spec.ts` green against the deployed artifact; live URL |

**Weekend deliverable:** the project becomes linkable, and the map stops lying. Recruiter and
frontend personas unblocked in a day (5 of 6 said they would not star today).

### Wave 1 — no re-record (weeks 1–2): make the loudest claims true, then make the project readable

Order matters inside this wave: **the claim repairs (1.1–1.4) land before the README amplifies
them.** Amplifying "import-linter enforced" and "the most important test" while a senior engineer
can break both in ten minutes converts the project's best asset into its worst liability.

| # | ids | Change | Files | Size | Rationale | Measurement |
|---|---|---|---|---|---|---|
| 1.1 | **C-31** | Give `assert_packet_is_leak_clean` the `VisibilityResult`/`WorldState`; assert set-equality of visible body/player ids; adopt B's 16-mutation harness as a gate | `eval/leak_scan.py:610`, `eval/leak_test.py` | M | `DESIGN.md:933` calls it "the most important test" and the ML champion gate runs exactly it (`training/crew/scorer.py:1735`) — and it cannot see entitlement. **You found this yourself; that is the story** | M6, M1, M10 all caught; champion gate still green |
| 1.2 | **C-32 + C-125** | Add `orchestrator, api, eval, scripts` to `.importlinter root_packages`; correct README:74 and CONTRIBUTING's "same checks CI runs" | `.importlinter`, `README.md`, `CONTRIBUTING.md` | S | [D-VERIFIED] contract coverage is 89 of 383 files. Cheap; makes the claim **true** rather than softening it | re-plant `agents/_probe_orch.py` → contract BROKEN |
| 1.3 | **C-34** | Plant into `tmp_path` with a generated linter config; add `_firewall*` to `.gitignore` | `tests/test_firewall.py`, `.gitignore` | S | 2 of 12 concurrent `lint-imports` runs print a **false BROKEN** on the repo's loudest gate; a SIGKILLed run leaves a committable file containing `import engine`. Also unblocks 1.9 | 12 concurrent runs → 0 false BROKEN |
| 1.4 | **C-6** | Back-port `training/anchor_study.py:631-655`'s correct check into `eval/validity.py:518` (and `training/rollout.py:653`) | one line each | S | It is the **corpus acceptance gate**: a truncated replay passes `all_games_reach_game_over` and enters downstream as "verified" — directly under the "100/100 byte-reconstruct" claim you are about to feature | the corrupt fixture is rejected by `validity_gate.py` |
| 1.5 | **C-1** | Three `if actor.in_vent: raise ActionRejectedError` guards on kill/report/sabotage, matching the four rules that already guard; update `training/env.py`'s mask in the same change | `engine/rules.py:56,182,225`, `training/env.py:288-296` | S | No committed replay is contaminated (both shipped policies short-circuit on `in_vent`), so this is **RR-free** — but the RL action mask *advertises* untraceable kill+sabotage to the next sampled policy, and it inverts `rules.py:60-66`'s own stated principle | B's repro rejects all three; `test_mask_legality_against_engine` green |
| 1.6 | **C/A1+A2+A5+B8+B12** | README rewrite per C/F1: ≤150-word status, phase table extended to 19, the authorship statement, the prose pass; create `docs/history.md`, `docs/glossary.md`, `audits/README.md`; evict the 846-word ledger and the 234-word lever paragraph | `README.md` + 3 new docs | M | 6/6 personas stopped reading at README:84–107. This is *the* single change every persona named, and A5 (who the human is, what they did) is the one page only the human can write | time-to-"what is this" < 60 s; `check_doc_facts.py` extended so the new numbers cannot rot |
| 1.7 | **C/A6 + C-72 wording** | Results stated once: README table + `docs/ml-program.md` in research shape (problem / environment / method / results / limitations / related work), N1/N2 framed as specification gaming. **Every volatile number stamped with its baseline and record date.** Drop "trust" from README:78/ADR-0001 or say the channel is unused; mark `DESIGN.md §6.6` target-not-as-built | `README.md`, new `docs/ml-program.md`, `docs/adr/0001-*.md` | M | The enabling move for 1.6 (the ledger needs somewhere to land) and the answer to "I cannot tell what was achieved". The **19.14 cells (proof 310/310 = 1.000 vs non-proof 46/125 = 0.368) are the strongest number in the repo and the README never states them** | a researcher reads it in 5 min; every row cites a committed file; `paired_stats.py` reproduces the intervals |
| 1.8 | **C-3 + G-12 errata** | One honest paragraph: the +0.12–0.30 win edge is measured against an FSM with two identified target-selection defects, with the measured rates (45.8% of free kills declined; 8–12% of decisions stalking ejected players; both 9p2i-only) | `docs/ml-program.md`, close-audit errata | S | State it before a senior ML reader does. A project whose thesis is "we don't publish numbers we know are confounded" cannot leave this unstated | the paragraph exists and cites the two measurement scripts |
| 1.9 | **FM-2 / new** | `eval/solvability.py` — a `replay_walk` consumer computing, from living crewmates' own perception with **no LLM**, who could have committed the last kill | new file (~1 module) | M | The **only new instrument I sanction.** It converts "deduction not demonstrated" from an apology into a measured ceiling: singleton candidate set in **109/626** body meetings, correct **103/109 = 94.5%**; killer inside the set **581/626 = 92.8%**; **61 of 354 ejections landed on someone the crew's own pooled perception had already cleared**. It is also wave 2's y-axis | reproduces from a fresh clone in < 60 s |
| 1.10 | **G-38 + C-8** | Project the intended action into the spectator DTO (`PRETEND_TASK`, `EMERGENCY`, `REPAIR`, `BLOCKED`); route `TournamentDashboard`'s and `BeliefMatrix`'s raw fetches through `client.getJson` **in the same PR** (the DTO change bumps `viewModelVersion`, which escalates C-8 from latent to live) | `api/replay_loader.py:2208`, `api/schemas.py`, `MapView`/`AgentToken`, `TournamentDashboard.tsx:1025-1060` | S–M | Free (derived from the recorded `actions` row, **no re-record**), and it makes the impostor's central deception *visible for the first time*: 1,747 fake tasks currently render as IDLE/MOVING, never TASK | `TASK 0 → 1747` reclassified; the version guard fires on a skewed payload from both routes |
| 1.11 | **C-96 + C-35** | Extend the mypy exclude regex to the two `fetch_evidence.sh` restore destinations; pin the `AILIBI_*` surface in the root conftest | `pyproject.toml`, `tests/conftest.py` | S | Two documented steps currently produce a spurious red; a visitor with a realistic 13-var env gets 10 failures | documented restore → `check.sh` green; the 13-var env run is clean |
| 1.12 | **C-34 + C-48** | `pytest-xdist` + promote the shared replay fixture to session scope | `pyproject.toml`, `tests/conftest.py` | S–M | 338 s serial, and you are about to run it ~50 times during wave 2. Pays for itself inside the wave | `pytest -n auto` green; wall < 90 s |
| 1.13 | **C-42 + C-43** | Memoize the Jinja `Environment` per `(prompt_set, root)`; bisect + cache `recent()` | `agents/strategic/prompts/loader.py`, `agents/memory/episodic.py:119` | S each | 1.20× and 1.28×, both **verified replay-SHA-identical** by B. They do not shorten the 23 h record (LLM-bound) — they cut CI, the eval harness and every offline counterfactual wave 2 depends on | replay SHA unchanged; A/B ratios reproduce |
| 1.14 | **C/B4 + C/B5** | An as-built architecture SVG one click from the top; one contract shown inline next to its generated prompt and the PR it produced | `README.md`, `docs/architecture.md` | S | Makes "350 agent-authored PRs" concrete instead of asserted — 6/6 personas asked for the human/agent split, and X1/X2 asked to be *shown* the loop, not linked to it | three links resolve; a reader verifies agent authorship in git in 30 s |

### Wave 2 — the evidence-honesty substrate phase (weeks 3–6, ONE re-record)

**Day 1, before any code: pre-register.** Write `tasks/phase-20.md` naming the metrics and the bar
*before* the fixes exist. Pre-registration preceding measurement preceding ruling is the thing P2
verified in git and praised; do it again and the wave writes its own credibility.

Every item lands **default-OFF / lever-gated** so the committed baseline and all gates stay green
until the record. Before the record, run the **$0 offline counterfactual**: re-run the new detector
rules over the existing 300 committed games and publish, in advance, how many of the 79 innocent
ejections would no longer be minted. That is a falsifiable prediction made before the measurement,
and it de-risks a 23 h event.

| # | ids | Change | Files | Size | RR | Rationale | Measurement |
|---|---|---|---|---|---|---|---|
| 2.0 | **C-74** | Harden `refresh_samples.sh`'s worker paths (`run_worker`, `_acquire_lock`, `record_one_seed`) with real coverage; stop remapping `AILIBI_LLM_PROVIDER=fake` to `anthropic` | `scripts/refresh_samples.sh`, `tests/scripts/test_refresh_samples.py` | M | RR-free | **The record runs on 917 lines of Bash with zero coverage of its worker paths.** 23 h of operator wall and the project's canonical baseline ride on it | a fake-provider end-to-end worker run passes; the 59 `--dry-run` tests gain ≥1 real path each |
| 2.1 | **G-3 / C-2** | Derive the completed-task memory line from the engine's `TaskCompleted` event, not a `pending_task_id` flip; record `owned_task_ids` in `_self_state_payload`; delete the false invariant comment; fix the test that pins the wrong rule | `agents/memory/store.py:1157-1200`, `agents/perception.py:354-361`, `tests/agents/test_memory_rendering.py:834` | S | **yes** | The one unambiguous bug both tracks confirmed with independent repros. It poisons *first-hand* memory — the channel the design treats as ground truth — and mints STRONG flags against innocents | fabricated `You completed` lines 65/594 → **0**; the verify-G-3 scanner becomes a test |
| 2.2 | **G-1** | Render the self-location trail the store already keeps (`own_room_by_tick`), ideally with a tick range as `DESIGN.md:705` already specifies; re-date the completed-task line to the tick its room belongs to | `agents/memory/store.py:1025-1028,1191-1205` | S | **yes** | 20.5% of crew roll-call answers are invented; **44.3%** of the 79 innocent ejections are the victim mis-stating its own position and **21.5%** are a witness's mis-dated sighting. No prompt change needed — this is rendering, not modelling | crew false `whereabouts` 20.5% → < 5%; the s30-m3 and 4p1i-s10 exemplars stop reproducing |
| 2.3 | **G-9a** | Give movement a first-class encoding: a `saw_move` observation shape, or make the detector treat "A at T−1 → B at T" as consistent with "B at T" | `meetings/schemas.py`, `meetings/transcript.py:2379-2494`, `accusation_round.j2:205-209` | S–M | **yes** | **38/38** flags built on a re-spoken movement line are memory-truthful and spoken-false; 10 meetings ejected the innocent they framed — including an impostor engineering a 7–1 ejection of the body reporter by quoting the *origin* half of a true line (seed 39 m0). That exemplar is the best 60-second demo of "why evidence honesty matters" in the corpus | those 38 flags → 0, with no new flag class in their place |
| 2.4 | **G-2 / C-11** | Thread `SightingRecord` into `detect_contradictions` [D-VERIFIED absent]; resolve every spoken `saw_player` against the speaker's own record; require 2 independent sources for a STRONG `alibi_vs_sighting`; suppress single-tick endpoint windows | `meetings/transcript.py:159-181, 2170-2179, 2379-2494` | M | **yes** | **The centrepiece**, and scope item 1 of the project's own close audit. 63.5% of sighting sides were never perceived by the speaker; the class is 14.6% precise as sole evidence, below chance; 70 of 79 wrongful ejections ride one. The exculpatory side already does this — **the right thing was built once, on the wrong half** | sole-flag precision 14.6% → ≥ 50%; grounded sighting side 36.5% → 100% |
| 2.5 | **R1 + R12** | Map-aware arbitration: adjacent rooms within ≤1 tick ⇒ demote or suppress; ship a map/adjacency card in the meeting prompt | `meetings/transcript.py`, the six `.j2` templates | S | **yes** | **148/234 (63.2%) of STRONG `alibi_vs_sighting` flags name adjacent rooms** — one tick of walking reconciles both statements — 130 name innocents, and **0 of 7,458 prompts contain a map, adjacency or travel times.** Highest measured veto-per-line in the whole idea list | adjacent-room STRONG share 63.2% → ~0; **run as the offline counterfactual first** |
| 2.6 | **G-2 prompt / C-129** | Split the flag block by the taxonomy that already exists in code (`api/schemas.py::classify_evidence`, already rendered by `MeetingView`): "this is proof" vs "two accounts conflict and nothing here says which". Delete "Each flag below is VERIFIED evidence… never side with an unverified counter-accusation" | `vote_ballot.j2:100`, `accusation_round*.j2` | S | **yes** | The product knows the difference between proof and inference; the agents are never told. It is in 2,543/2,543 recorded ballot prompts [D-VERIFIED] and it is the sentence that converts a bookkeeping artefact into a conviction | weak-flag-only convictions 5/5 innocent → 0; model-omniscient language gone from rationales |
| 2.7 | **G-27** | Parameterise the persona by impostor count; fix the arithmetically wrong win condition and `"p-4 are your fellow saboteurs"` | all six `qwen3_6_27b/*.j2` + the render contract in `orchestrator/game.py` | S | **yes** | 1,956/1,956 and 5,502/5,502 prompts — 100% — tell a 2-impostor game there is one impostor, 90 lines above "Your fellow saboteurs". A visitor sees it in the Mind Inspector in their first meeting. Highest embarrassment-to-effort ratio in the review | 0 singular-persona strings in a 2-impostor render; a template test pins the count |
| 2.8 | **G-25** | Stop splicing dev markers into `free_text`; parse them into structured chips as ballots already are (the spectator half can ship in wave 0/1) | `meetings/manager.py:3884-3912`, `api/replay_loader.py:2696-2703` | S | **yes** | Editor-console text sits **inside quoted dialogue in 12.6% of prompts**, immediately before the sentence that usually names a vent | markers in `free_text` 5.5% → 0; contaminated prompts 12.6% → 0 |
| 2.9 | **G-23** | Exempt dead/ejected subjects from "a witnessed vent outranks everything — speak it FIRST" | `crewmate_report.j2`, `accusation_round*.j2` | S | **yes** | 232 `saw_vent` observations name a corpse; 5.0–5.5% of turns lose their accusation to it; whole meetings (s13 m2, s15 m1 — the last 3-alive meetings) are spent re-prosecuting an ejected impostor. The most visible "why are they still arguing about him?" moment for a viewer | struck accusations 5% → 0 |
| 2.10 | **R4 + R5 (G-35)** | Persist meeting outcomes into memory ("p-4 was EJECTED at meeting 1 — IMPOSTOR; one remains") and keep testimony as *content* ("p-8 says he saw p-4 vent") rather than `accused p-4` | `agents/memory/store.py:1485`, the `meetings/manager.py` belief fold | S–M | **yes** | **0 of 7,458** prompts record any prior ejection or its revealed role. Nothing survives a meeting today; this is the cheapest possible way to make meetings compound | ejection-outcome lines in 100% of post-ejection renders; re-litigation meetings → 0 |
| 2.11 | **G-34 / R8 / C-73** | Coalesce co-presence into spans; drop the tick-0 spawn block when it is the full roster; raise reported-testimony salience above bare co-presence | `agents/memory/store.py:85,1854` | S–M | **yes** | **The enabler.** ~32% of the block is recoverable at zero information loss, and without it 2.2's and 2.10's new lines are shed first under the 1,500-token budget (measured: reported rows kept **0 of 4,150** at >150 candidates). A's researcher found the smoking gun: in seed 17 the correct row *was present*, at line 22, under twelve near-identical CAFETERIA rows — *"the model is reading the top of a badly sorted list, not hallucinating"* | render lines/snapshot 53 → ~36; reported rows kept > 80% at every budget |
| 2.12 | **C-3 + G-12** | Re-validate co-location across all scored `targets`, not only `targets[0]`; fold `memory.meeting_history` into `_confirmed_dead` | `agents/tactical/impostor_policy.py:336-361,813-838` | S | **yes** | **Defect repairs, not balance levers** — see §5 ruling R3. 45.8% of free zero-witness kills declined on an id tie-break; one game (seed 36) provably thrown; the ML comparator and every impostor-side baseline number rest on this | `measure_missed_kills.py` 45.8% → < 10%; stalk-toward-refuted 34% → < 5% |
| 2.13 | **B §8 / T1** | A **render-version stamp** so the prompt byte-golden pins "these recorded bytes reproduce under render v1" while new code emits v2 | `agents/memory/store.py`, `tests/meetings/test_prompt_byte_golden.py` | S–M | no | Structural: today a one-word prompt fix (G-27) is taxed a 23 h re-record. This is the one item that changes the **cost curve** of every future wave. It can only be introduced at a record | the golden still fails on a one-byte template perturbation, and no longer fails on an intentional render bump |
| 2.14 | **G-37 / C-36** *(if the calendar holds)* | Resolve the +1 agent-clock convention: re-stamp or label explicitly, and assert `obs.tick <= meeting.tick - 1` | `orchestrator/game.py:1778-1793`, memory render, viewer | M | **yes** | Every one of eight watchers opened with a hand-derived "tick convention" paragraph, and the seam silently inflated three of Track A's own headline numbers by one tick. **The friction is the finding** | the two canonical walkers' −1 frame disagreement becomes an asserted invariant |

**Dependency order inside the wave:** 2.0 before the record · 2.1 → 2.2 (same lines in `store.py`) ·
2.2 → 2.4 (grounding needs a self-record to ground against) · 2.11 alongside 2.2/2.10 (or their new
lines are shed) · 2.6+2.7+2.9 batched into **one** prompt-version bump · 2.5's counterfactual runs
before anything records.

**The record:** freeze `agents/`, `meetings/`, `observation/` and the prompt set. Record in value
order — `replays/samples/9p2i` (50; the set the demo and featured seeds serve) → `replays/ml_corpus/9p2i`
(150) → `replays/samples/4p1i` (50). The corpus matters for **power**: the non-direct cell is n=33 in
samples and n=89 in the corpus; a delta on n=33 will not separate. If the window forces a choice,
record 9p2i corpus **before** 4p1i.

**Close gates:** `verify_samples.sh` (100/100), `validity_gate.py` (now with 1.4's fix),
`eval/leak_scan.py` (now entitlement-checking, 1.1), `check_doc_facts.py`, the prompt-version pins,
MANIFEST regeneration, `check.sh` in a clean worktree.

**Primary bar (pre-registered):** non-direct-cell conviction accuracy **0.368 → ≥ 0.60**; corpus
innocent ejections **79 → < 35**; false crew `whereabouts` **20.5% → < 5%**; sole-`alibi_vs_sighting`
precision **14.6% → ≥ 50%**; grounded sighting side **36.5% → 100%**; fabricated completion lines
**10.0%/23.1% → 0**; adjacent-room STRONG share **63.2% → ~0**; plus pass/fail on each of the four
19.11 injustice fixtures. **Secondary, observed not gated:** the win split, inside a pre-registered
band. **Y-axis:** 1.9's solvability ceiling.

### Wave 3 — the presentation multiplier (weeks 6–8, RR-free)

| # | ids | Change | Size | Rationale |
|---|---|---|---|---|
| 3.1 | — | Re-curate `FEATURED_GAMES` against the new bytes; Pages redeploys itself | S | Some of the best old demo games were injustices you just fixed |
| 3.2 | **C/A6 amend** | The results table gains its before/after column; `docs/ml-program.md` gains the wave's close audit | S | **The payoff.** "Pre-registered, measured, reported — including the part that did not move" is the strongest single sentence this repo can add |
| 3.3 | **C/A3(b) + C/F4** | The one image: a side-by-side still of the same tick — omniscient left, one crewmate's as-agent fog right, captioned *"Left: what happened. Right: everything p-3 was allowed to know when it voted"* — plus an 8–10 s MP4/WebM (tokens move → kill flash → the transport stops itself at the meeting → the fog toggle flips) at ≥1440×900 | S–M | It states all four stories in one frame: the firewall, the product, the research premise, and (with the byline) the authorship. It also fixes the measured GIF failure — the current hero never shows the map because the fixed dock covers the canvas at the 1000×640 recording viewport |
| 3.4 | **C/B11** | `docs/lessons.md`: directing agents at scale; what 4,600 tests and four import contracts could **not** catch; doc drift as a first-class bug; pre-registration; and P2's unrebutted line owned verbatim — *"strong on measurement, weak on knowing when to stop building measurement"* (95,824 lines of process narration against 57,776 of product Python) | M | The one page only the human can write, and the thing every hiring-manager persona said they would ask about on the call |
| 3.5 | **FM-5** | Publish the review: `audits/review-2026-08-19/` + a short essay whose hook is the **retractions** — G-6 refuted (fog-of-war correct, zero real misses), G-7's headline a two-clock artefact, G-4's fabricated-vent half 98.8% grounded, G-1's attribution 73% → 44.3%, and B's severity corrections in both directions | M | Highest novelty of anything here and near-zero marginal cost — the reports exist. It is also the evidence-backed answer to C/D7's "process theatre" critique: the process catches things, *including itself*. Sequenced here so every finding links to its fix PR |
| 3.6 | **C/B3 + B9 + B10** | Reading-guide split; verifiable-shaped claim rewrites; commit or explicitly de-scope `training/reports/_finalist_eval_raw` | S–M | Tail polish. B10 matters most: today the central ML ruling rests on measurements *of* evidence not in the repo |

### Later, or never

| Item | Ruling |
|---|---|
| Re-open ML (Phase C, co-evolution, a training campaign) | **Never on this timeline.** The pre-registered NO-GO is already the strongest research artefact in the repo and it survived a 100×/300× sweep. P2's complaint is that it is *under-sold* — the gap is a 2-page write-up (1.7), not more training. Anything trained must run on a post-substrate corpus anyway |
| God-module refactor (C-62), the 969-line fork (C-33), the C-63 prose sweep | **No.** B's own verdict **refuted** C-33's load-bearing risk (five always-on parity gates; a 1e-9 injected drift goes loudly red). Buy 90% of the credit for 1% of the cost: one honest paragraph in `docs/architecture.md`, plus a mask-parity test for the uncovered `_build_action_mask`. For C-63, do the targeted version only — lead with plain intent in the five files a reader actually opens (`observation/service.py:31-83` is the named offender) |
| Rewrite git history to shrink `.git` (C-45, 190 MB) | **No.** It would break the 43/44 live in-code `audits/`/`tasks/` references, every PR link, and the commit-authorship graph that **is** the authorship evidence. Instead: `git rm --cached` the two regenerable aggregates going forward, extend `.gitignore` past the top level, and replace the ~150-word clone caveat with one line + `--filter=blob:none` |
| Balance levers — G-5 post-meeting reset, G-15 finished-crew jobs, G-13 vent peek, G-8 `saw_kill`, G-22 symmetric roll-call, G-40 sabotage, G-43 the 4p1i second act | **A separate chartered balance wave with its own record.** Every one is well-evidenced and several are large wins; shipping any alongside the honesty wave destroys the attribution of the one measured delta you are buying with 23 h |
| "Fix" G-6 (bodies surviving meetings) and add `died_at` (G-7) | **No — both refuted by A's own verification.** `discovered_by=None` is precisely what makes a body *visible*; 0 real misses corpus-wide; 230 → 189. The surviving corollary of G-7 is `saw_kill`, which is a balance-wave item |
| Touch crew same-room-only vision or the vent channel | **No.** All three ideation lenses independently named these N1/N2: crew blindness is the forcing function that makes the meeting exist, and `vent_sighting` is 440/440 precise carrying 71% of ejections. The problem was never the vent — it was everything else sharing its "VERIFIED" label. Only sanctioned narrowing: adjacent-room **bodies**, never players, in the balance wave — and fix `canonical_1.yaml:52-58`, which still documents uniform adjacency the code no longer implements (C-115) |
| The remaining ~94 P2 findings | **Triaged backlog, and say so.** A triaged backlog reads better than a half-done sweep |
| A live-API deployment | **No.** The static bundle is the sanctioned path and already has an e2e spec that runs with `/api` blocked |
| Upgrading README's reproducibility scope 3 | **Blocked** pending one controlled owner-assisted run (§2 row 14) |

---

## 5. Where the syntheses disagreed — and my rulings

**R1 — Host the demo now, or after the re-record?** *(credibility: after — the bundle and GIF bake
featured replays, so doing it first means doing it twice. pragmatic / ambition / map: now.)*
**Ruling: host now; defer only the expensive media.** Pages rebuilds on every push, so a re-record
refreshes the hosted bundle for free; the featured *seed ids* survive a re-record, only their
curation may change (3.1, S). What genuinely would be done twice is the hand-recorded hero
GIF/MP4 — so that is the one artefact I move to wave 3 (3.3). Ship the meeting PNG as the hero still
now. credibility's objection is right about the media and wrong about the URL.

**R2 — Publish the results table now, or after the numbers move?** *(credibility: after — every
corpus number in it moves. pragmatic: now.)* **Ruling: now, with every volatile number stamped with
its baseline and record date** — which is exactly the discipline `replays/samples/*/MANIFEST.md`
already enforces. Then the re-record **adds a column** rather than invalidating a page. This turns
credibility's objection into the asset: the before/after table is pre-built, and a reader watches a
claim get re-measured instead of quietly replaced.

**R3 — Ship the crew half of the substrate alone, or bundle the impostor fixes?** *(pragmatic: crew
only, or attribution dies. ambition + A's game-designer: never ship the crew half alone — crew
already win 70–75%.)* **Ruling: include C-3 and G-12 (2.12); exclude every design lever.** The
distinction is not crew-vs-impostor, it is **defect-vs-lever**. C-3 (45.8% of free kills declined on
a string comparison) and G-12 (stalking ejected players) are bugs in the same class as C-2/G-3: they
bias a measured baseline. Publishing a before/after whose comparator is knowingly hobbled is exactly
the failure the project's thesis forbids. Pre-register them as a named co-intervention, keep the
offline counterfactual (frozen bytes, detector-only) as the clean attribution instrument, and report
the win split as a secondary observation inside a pre-registered band. Post-meeting reset,
finished-crew jobs, vent peek, `saw_kill`, symmetric roll-call, sabotage: **out**.

**R4 — Build the solvability oracle, or build no new instruments?** *(ambition: FM-2 is the
highest-value new result. pragmatic: build no new eval instruments — P2's unrebutted critique.)*
**Ruling: build exactly one (1.9), and say it is the last.** P2's critique targets apparatus without
results; `eval/solvability.py` is ~one module producing a headline *result* — the game is solvable
from the crew's own eyes in 92.8% of body meetings and correctly solvable by a singleton in 109/626,
while 61 of 354 ejections landed on someone already cleared. That is the y-axis wave 2 has been
missing, and it converts the project's biggest admission into a measured gap. Everything else reuses
`deduction_metrics` + the four 19.11 fixtures.

**R5 — Is FM-4 (make the claims true) a hard prerequisite for the front-door push?** *(ambition:
yes, blocking. pragmatic: week 1–2, unblocking.)* **Ruling: it blocks the amplification, not the
weekend.** Nothing in wave 0 repeats "import-linter enforced", "the most important test", or "zero
firewall violations" — so 0.1–0.8 ship immediately. The README rewrite (1.6) and the About text that
restate those claims land **after** 1.1–1.4, with C/B9's precise wording: *"never breached in CI:
import-linter contract + planted-leak test + recursive leak sweep."*

**R6 — Publish the review itself?** *(ambition: FM-5, rank 5. pragmatic and credibility: silent.)*
**Ruling: yes, in wave 3, curated, and titled by the retractions.** Not 171 findings dumped — the
interesting artefact is the adversarial layer: three blind reviews of an AI-built codebase that
disproved four of their own headline claims and corrected severities in both directions. Sequenced
after the fixes so every finding links to its PR; publishing a pile of open self-criticism *before*
any of it is fixed reads as chaos, not rigor.

**R7 — G-1's attribution: 73.4% or 44.3%?** **Ruling: 44.3% victim-caused / 21.5% witness-caused,
and the 73% figure never appears in public.** A's own verifier showed the missing 29.1% are real
one-tick corridor transits, and that two of the claim's own exemplars fall in the *opposite* bucket.
The honest split is also the better story: the bug cuts both ways.

**R8 — C-113's severity.** **Ruling: corrected by my own check.** The docstring-vs-committed-data
contradiction is real and worth fixing [D-VERIFIED: 0.9230769]; the "README sells it as the
circularity guard" leg is **refuted** — the README never mentions the metric. Do not write a README
fix for it; fix the docstring and the Tournament tooltip.

**R9 — Scope 3 / the Darwin-arm64 ES digest.** *(B measured it reproducing bit-identically; the
owner's own working note says committed ES artifacts reproduce only in the Linux container.)*
**Ruling: do not upgrade the claim.** This is the only front-door claim that might be upgradeable
for free, and it is also the only one where a wrong upgrade would cost more than the upgrade is
worth. One controlled owner-assisted run, or leave the honest hedge standing.

**R10 — Track A's internal contradiction (w2 says rejected actions are absent from the JSONL; five
other reports read them out of the same array).** **Ruling: the majority reading is correct** — the
G-10 verifier re-derived 1,003 rejected moves and 188 whiffed kills from that array. Spend 30
minutes confirming before citing any w2-dependent conclusion publicly.

**R11 — "no P0" (B) vs "eight P0s" (A).** **Ruling: not a contradiction — different ontologies, and
the difference is the headline.** B's P0 = correctness/security/data-loss; A's P0 = breaks
believability of the core loop. Every A P0 is a *product* defect over *correct* code. Put that
sentence in `docs/lessons.md`.

**R12 — Process volume: asset or theatre?** **Ruling: three artefacts, three verdicts** (the word
"volume" was doing three jobs). The `audits/` tree: **keep and index** — B proved 43 of 44 citations
resolve. In-code narration: **trim**, targeted only. The README: **evict** the 846 words. And own
P2's sharper line in writing rather than answering it with more tooling.

---

## 6. The owner's open decision: substrate vs presentation

**Recommendation: neither, in the order posed. Do the free half of "presentation" now — because most
of it is claim-repair, not polish — then the substrate phase exactly as the close audit recommends,
then the presentation multiplier on corrected bytes.**

The close audit's ruling (`audits/audit-phase-19-close.md` §4: substrate first, "polish never ahead
of narrative correctness") is **right about the ordering of the expensive thing and wrong only in
what it counts as presentation.** Sorting this review's top credibility risks by re-record cost,
**six of ten need no record at all**, and they are precisely the ones a reader hits first. Hosting a
demo whose map is wrong on 67% of frames is not polish, it is a defect. Giving the leak scanner the
visibility result is not polish, it is making the project's loudest claim true. Publishing the
solvability ceiling is not polish, it *measures the gap the substrate phase exists to close.*
Neither is amplification of a broken narrative; both are narrative correctness at $0.

Three facts the §4 framing did not have, all from the cross-track read:

1. **The substrate phase's own instrument is already at HEAD and costs $0.** `eval/deduction_metrics.py`'s
   proof-vs-inference cells and the four 19.11 injustice fixtures mean the measurement can start —
   and the offline counterfactual can be published — *before* the record is spent.
2. **The record itself runs on 917 lines of untested Bash** (C-74). Harden that first (2.0) or the
   23 h is at risk.
3. **The close audit's four scope items map exactly onto findings all three blind tracks reached
   independently:** sighting provenance = **G-2/G-4/G-9a ↔ C-11**; content-vs-own-memory validation =
   **G-1**, plus **G-3 ↔ C-2** which is the same class and is a *bug*; interval/weighting honesty =
   **G-2's single-tick windows, G-36 ↔ C-29**; flag naming = **G-27, G-29 ↔ C-129**. That convergence
   is the strongest evidence in this document that Option A is correctly scoped — and the roadmap
   above simply gives it a readable venue to land in and a comparator honest enough to measure
   against.

And the case for doing the substrate phase at all, stated as the owner will need to state it: **it
converts the project's biggest remaining risk into its best remaining story.** "I ran three blind
reviews of my own project; they found my evidence channel was anti-informative and my memory
renderer fabricated completions; I fixed both, pre-registered the bar, re-recorded, and here is the
before/after — including the part that did not move" is a stronger portfolio artefact than any
amount of README editing. If the record fails to move the metric (the Phase-13.12 precedent —
mechanism built, model could not drive it), **publish it as the result.** This repo has already
reported a NO-FLIP twice with the losing evidence committed, and every persona named that honesty as
the thing they would hire for. A pre-registered null on a fixed instrument beats an unmeasured
improvement.

**If the calendar collapses to four weeks:** keep wave 0 and wave 1 in full; cut wave 2 to
**2.0, 2.1, 2.2, 2.4, 2.5, 2.6, 2.7, 2.8, 2.11, 2.12** (the two confirmed bugs, the grounding, the
map arbitration, the three prompt-string fixes, the render enabler and the comparator repair — every
one S or S–M and together the entire measured causal chain); record 9p2i samples + corpus only; move
`docs/lessons.md` ahead of the tail polish. The story survives intact; only the residue list grows.

---

## 7. The pitch and the front door I endorse

### The paragraph (shippable the moment wave 0 lands)

> **AiLibi** is a deterministic Among-Us-style social-deduction simulator where LLM agents move,
> witness, remember, accuse and vote behind an enforced observation firewall — every game replays
> byte-for-byte from an action log and a per-tick hash, and the spectator lets you open any agent's
> mind at any tick: its prompt, its response, its memory, its beliefs. I'm Daniel Keinan; I wrote the
> 321 task contracts, the review gates and the audit rulings, and AI coding agents wrote every line
> of production code across 350 merged PRs and 19 phases. The measurements are published the same
> way: 100 committed replays reconstruct in three seconds, and the project's own headline finding is
> that **87% of the crew's correct ejections ride one engine-certified tell rather than reasoning** —
> general social deduction is not demonstrated, and saying so is the point. Four learned tactical
> policies beat the scripted baseline on wins; none was adopted, because they failed a bar that was
> pre-registered before the measurement was taken.

**After wave 2 lands, replace the last two sentences with the thing no comparable project can say:**

> …and we can now measure how much deduction was *available*: from the crew's own perception alone,
> with no LLM, the killer is inside a computable candidate set in 92.8% of body meetings and that set
> is a correct singleton 109 times in 626 — while the agents' convictions were perfect where the
> substrate handed them proof (310/310) and worse than a coin flip where they had to infer (46/125).
> This is the before/after of closing that gap.

### The front door (C/F1, adopted with three edits)

```
# AiLibi — LLM social deduction behind an observation firewall, built by directing AI coding agents
  by Daniel Keinan · code by Claude Code / Codex agents · MIT · [CI] [Python 3.11] · May–Aug 2026, solo
  ▶ Live demo (GitHub Pages)  ·  [meeting PNG hero]  ·  [omniscient|as-agent side-by-side still]

## Sixty seconds: what you are looking at        3 sentences, product first. Name pun in one clause.
## At a glance                                    stack · 877 commits / 350 PRs / 321 contracts / 19 phases
                                                  · 100 committed replays · ~4.6k tests · status: active
## Verify it yourself in one minute               the existing three commands, EACH LABELLED with the
                                                  claim it proves (byte-identical replay / 100 samples
                                                  reconstruct / the demo is a static directory)
## How it was built — who did what                the 5-step loop; the human/agent split in ~120 words;
                                                  ONE CONTRACT SHOWN INLINE next to its generated prompt
                                                  and the PR it produced; how to verify authorship in git
## What it is                                     three load-bearing decisions; the as-built layering SVG
## What the measurements said                     the results table, every volatile row stamped with its
                                                  baseline + record date; the proof/non-proof cross-tab;
                                                  one ML paragraph TITLED BY ITS RESULT
## What I learned                                 6–10 bullets → docs/lessons.md
## Status & history                               2 lines + phase table 0–19, each row linking its audit
## Run it · Architecture · Docs index · Reading guide · Glossary
```

My three edits to C/F1: **(a)** the demo link and byline sit above the three commands (D2's ruling,
P3's objection honoured) but the commands stay on the first screen — X1/P1/P4/X2 all called them the
best thing in the repo; **(b)** every volatile number carries its baseline stamp from day one, so
wave 3 adds a column instead of rewriting the page; **(c)** the honesty claims are worded in C/B9's
verifiable shape — *"never breached in CI: import-linter contract + planted-leak test + recursive
leak sweep"* — and only after wave 1 has made them true.

**The one image:** not the GIF. A single side-by-side still of the same tick — omniscient on the
left, one crewmate's as-agent fog on the right — captioned *"Left: what happened. Right: everything
p-3 was allowed to know when it voted,"* with the accusation card p-3 actually wrote underneath. It
is the only frame that states all four stories at once: the firewall, the product, the research
premise, and, with the byline, the authorship. Both halves already render correctly today; the
compositing is free; and it sidesteps the measured GIF failure entirely.

---

## 8. Re-record ledger (the one-line answer to "can I ship this today?")

| Needs the ~23 h record before the baseline moves | Ships now, every gate green |
|---|---|
| G-1, G-2, G-3, G-4, G-9, G-23, G-25, G-27, G-29, G-34, G-35, G-36, G-37 · C-2, C-3, C-11, C-29, C-129 · R1/R4/R5/R8/R12 · every A idea except F-41/F-42 | **All of wave 0 and wave 1** — C-1, C-5, C-6, C-7, C-8, C-9, C-31, C-32, C-34, C-35, C-42, C-43, C-48, C-74, C-96, C-113, C-115…C-128, G-38, G-41 · **all of C/A1–A6 and B1–B13** · the solvability oracle · the render-version stamp |

*C-42 (1.20×) and C-43 (1.28×) are verified replay-SHA-identical and may ship on either side; neither
shortens the record, which is LLM-bound.* **Sequencing hazard:** the G-38 DTO fix bumps
`viewModelVersion`, which turns C-8 from latent to live — ship them in one PR (1.10).

---

### Provenance

Every claim above carries a `G-n` / `C-n` / `A1`–`F6` id traceable to `A/`, `B/` or `C/`. The eight
`[D-VERIFIED]` facts and the one correction (C-113's README leg) were re-checked against the repo at
`main b809b19c` during this synthesis. No repo file was modified.
