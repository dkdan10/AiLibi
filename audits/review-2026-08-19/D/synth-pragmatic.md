# D — The pragmatic synthesis: maximum portfolio value per unit of work

**Inputs.** `A/collated-findings.md` (G-1…G-41 + merged idea list), `A/verdicts.md` (12 adversarial
verdicts), `A/ideas-*.md` (3 lenses), `A/ux-visual-pass-lead.md`; `B/collated-findings.md`
(C-1…C-130, §7 "genuinely good", §8 root causes), `B/verdicts.md` (14 verdicts);
`C/collated-portfolio.md` (A1–A6, B*, D rulings, E strengths, F front-door plan).
Repo read-only at `main b809b19c`. Owner budget assumed: **4–8 weeks part-time, exactly one
real-LLM re-record** (~23 h operator wall, $0 flat-rate — `audits/audit-phase-19-close.md` §4.2).

---

## 0. The one-paragraph answer

Ship the **front door this weekend** (it costs no re-record, it is what 6/6 personas said blocks
them, and it is currently the only thing standing between this repo and a "take the meeting"
verdict). Spend the following three weeks building **one evidence-honesty wave** — the ten
substrate/prompt items that the two blind technical tracks *independently* fingered as the cause
of the same failure — landing every one default-OFF/lever-gated so all gates stay green. Then
spend the **single re-record** producing a **pre-registered before/after on an instrument that is
already committed** (`eval/deduction_metrics.py`'s proof-vs-inference cells, the four 19.11
injustice fixtures). That delta table — "non-direct conviction accuracy 0.368 → X, innocent
ejections 79 → Y, on 300 games, pre-registered before the code" — is the single highest-value
artifact this project can still produce, because it is simultaneously the gameplay fix (Track A),
the code fix (Track B) and the results section every persona said was missing (Track C, A6). Do
**not** re-open ML, do **not** ship the balance levers in the same record, do **not** refactor the
God modules.

---

## 1. Where the three tracks reinforce each other (these are the safe bets)

Two tracks that could not see each other landing on the same defect is the strongest evidence in
this whole exercise. Six such pairs:

| A-side | B-side | What the pair proves |
|---|---|---|
| **G-3** false "You completed X" memory lines (5 watchers, 21 spoken alibis) | **C-2** `redistribute` grows `owned_task_ids`; `store.py:1161-1166`'s "the owned set only ever shrinks" is a false invariant *written in a comment* | A saw the lie at the table, B found the wrong premise in the source. Both verdicts: **CONFIRMED-BUG**. 10 %/22 % of remembered crew work is fabricated in 159/300 committed games |
| **G-2** `alibi_vs_sighting` is 14.6 % precise as sole convicting evidence, labelled "VERIFIED evidence" | **C-11** grounding machinery (`SightingRecord`, `transcript.py:159-181`) is wired to the *exculpatory* vouch and never to the prosecutorial flag; 53/60 STRONG flags name a crewmate | Same asymmetry from both ends. B names the exact hook; A prices the damage (70 of 79 wrong ejections carried one, and in all 70 it was the only strong flag) |
| **G-38** spectator DTO shows a faked task as MOVING/IDLE (TASK 0/1747) | **C-7** MapView paints corpses the engine already consumed — **1182/1769 frames (67 %), 50/50 games** | The viewer — the thing you are asking people to look at — lies about two different classes of fact. Both are frontend/DTO-only, **no re-record** |
| **G-34** 66 % co-presence noise, tick-0 lobby block outranks social memory | **C-73** measured survival: reported testimony kept **0/4150** rows once candidates exceed 150 | A explains why the model speaks the stale row; B proves the good row was never in the prompt |
| **G-12** impostor FSM stalks ejected players ≤30 ticks (policy re-run reproduces recorded actions byte-for-byte) | **C-3/C-4** kill gate re-validates only `targets[0]`; 33–46 % of free kills declined; 34 % of stalk moves chase a refuted sighting | Two independent offline re-runs of the shipped policy. This is real, it is measurable, and it is **not** in this plan (see §6) |
| **G-25/G-27/G-29** dev markers in dialogue, singular "a hidden impostor" in 100 % of 2-impostor prompts | **C-129** the same, from the template side, plus `vote_ballot.j2`'s "VERIFIED evidence" contradicting `schemas.py:426` "Flags are information, not verdicts" | Cheapest fixes in the corpus; both tracks rank them high |

And the cross-track link that turns Track A from a liability into an asset: **C's A6 ("state the
results once, plainly") has no strong result to state today** — the ML program is a negative and the
gameplay claims are hedged. The 19.14 proof-vs-inference cross-tab plus a measured before/after is
exactly the missing content. Track A is not a distraction from the portfolio; it is the material
for the portfolio's missing section.

## 2. Where they explain each other

- **B §8 root cause 2 — "byte-identity doctrine freezing legibility bugs"** explains why Track A's
  cheapest fixes (G-1's render, G-25's marker strip, G-34's coalescing) never shipped: each costs a
  real-LLM re-record, so they queue behind a 23 h operator event. That is the correct doctrine for
  substrate and the wrong tax on legibility — and it is *why the single re-record must carry all of
  them at once*. It also argues for one small structural item (a render-version stamp) so this
  never happens again.
- **G-19** ("did a flag fire" predicts the outcome 88.5–100 %) explains the close audit's own
  headline: conviction accuracy is 1.000 where proof exists and 0.303–0.393 where it does not.
  Track A found the mechanism behind the number the owner is already deciding on.
- **C-63 / C-62** (33 % of non-test Python is prose; four God modules) explain **C/A2** (undefined
  private vocabulary): the dialect is not a README problem, it is a house style. That is why A2's
  fix is "define it once on the front door", not "rewrite 129 files".
- **C/D7** ("process theatre?" — unresolved between personas) is answered by A+B jointly: the
  process delivered genuinely rare things (0 dangling ids in 3814 ballots, an airtight teammate
  firewall 0/929, byte-identical determinism, 100/100 replays reconstructing in 3.14 s) **and**
  missed a P0 cluster that 45 spectator reads found in a day. Saying that out loud in B11 is worth
  more than any claim that the process caught everything.

## 3. Where they contradict — and my rulings

1. **Close audit §4 (substrate first) vs Track C (presentation is the only thing blocking 6/6
   audiences).** *Ruling: no calendar conflict.* Presentation costs $0 and no re-record and can
   ship in days; the substrate wave needs ~3 weeks of build before a record is even earned. Ship
   presentation **now**, in the dead time before the record exists. The charter clause "polish never
   ahead of narrative correctness" is honored because the presentation being shipped *states the
   measured gap* (the 19.14 panel is already at HEAD) rather than papering over it.
2. **Track A's own verification demolished three of its P0s.** `A/verdicts.md`: **G-6 is not a
   defect** (fog-of-war working as designed; 189 not 230 bodies; **zero** real misses corpus-wide);
   **G-7's headline is a two-clock artifact** (17.8 % of `found_body` land exactly on the kill tick
   once the +1 agent clock is corrected); **G-4's `saw_vent` half is REFUTED** (739/748 grounded —
   the "fabricated vent" quotes are real *kills* in the wrong syntactic box); **G-5's "89 reporters"
   is 111**; **G-1's 73.4 % attribution is 44.3 % victim-caused + 21.5 % witness-caused**.
   *Ruling:* drop G-6 from the plan entirely, drop the `died_at` field idea (G-7) and keep only its
   surviving corollary, and re-price G-1 honestly in the charter. This saves real weeks.
3. **B's C-33 (969-line fork across the `agents ↛ training` firewall) is PARTIALLY-TRUE — the
   load-bearing risk was REFUTED by experiment (12 states, 0 mismatches).** *Ruling:* do not
   consolidate. Add the parity test and one sentence in `docs/architecture.md`.
4. **A's game-designer: "items 1–7 all help the crew; do not ship the crew half alone."** *Ruling:
   ship it alone anyway.* The measured target of this record is honesty (non-direct accuracy,
   innocent ejections), not balance; mixing in the impostor levers destroys attribution and burns
   the one record you have. Record the win-split shift as an *observation*, charter the balance wave
   next. This is also the repo's own single-variable-arm discipline.
5. **P2 wants the ML negative as the headline; X2 warns it misfires with recruiters.** Endorse C's
   D4 ruling: README gets one paragraph *titled by its result*; `docs/ml-program.md` carries N1/N2
   for researchers.
6. **A-track w2 claims rejected actions are not in the JSONL; five other A reports read them.**
   Relevant because the free PRETEND_TASK fix depends on it. *Ruling:* 30 minutes of verification
   before building (`replays/samples/9p2i` `kind=tick` `actions` array vs `engine/tick.py:599`);
   majority reading is almost certainly right.

---

## 4. The plan

Ordering rule: **anything that needs the re-record must land before it; anything that does not must
ship immediately.** One prompt-version bump carries every prompt edit (the version-bump cascade:
the `.j2` header marker → `orchestrator/game.py::PROMPT_VERSION_SETS` / `DEFAULT_PROMPT_VERSIONS` →
the live-recorded prompt-version test pin; `scripts/regen_test_goldens.py` for the byte golden).

### 4.1 Do first this weekend (each ≤ 1 day, none needs a re-record)

| # | id(s) | What | Files | Size | Why it is on the critical path | Success measure |
|---|---|---|---|---|---|---|
| W1 | **C/A4** | GitHub About + topics + homepage + CI/MIT/Python badges + byline | repo settings, `README.md` head | S (15 min) | Recruiter persona: "on the repo card there is literally nothing but the name". Zero code, unblocks the 1-second health check | About non-empty, ≥8 topics, homepage set |
| W2 | **C-7** | MapView must read `TickView.bodies` instead of accumulating kill events | `frontend/src/components/MapView.tsx:227-264,570,591,734` | S | **67 % of frames on the demo's central surface are wrong.** You cannot host a demo that paints phantom corpses. Also kills the dead `killed_by` field | Re-run B's probe: `phantomFrames 1182 → 0` over 50 games; add the first `MapView.test.ts` (closes part of C-101) |
| W3 | **C/B1** | Silence/settle the `AILIBI_PROMPT_SET` fallback notice on the three front-door commands; document the var | `agents/strategic/prompts/loader.py:238-242`, `.env.example`, `README.md` | S | It is the **first output every verifier sees**, printed 6× in the README's own 5-game example, and contradicts the reproducibility pitch | Front-door commands produce zero unexplained stderr |
| W4 | **C-113** | `vote_correctness_rate` truth-up: docstring says "structurally pinned to 1.0", committed 9p2i reads **0.923** | `eval/vote_correctness.py:11-31`, `README.md:190` | S | This is a **headline metric the README sells as the circularity guard**. An ML researcher checking it finds the doc wrong — the one thing this project cannot afford | `scripts/check_doc_facts.py` extended to assert the README figure against the committed report |
| W5 | **C/A3(a)** + **C/B6** + **G-41** | Pages workflow (~15 lines) + bundle empty-state fixes (Tournament-tab 404 dump, picker copy, absolute `/Users/...` path in the bundle README) + strip "(DESIGN.md §11.3)" / "Task 19.14" from UI tooltips + expand "4p1i/9p2i" once + un-fix the dock below ~800 px + hide the ballot **CORRECT** badge in unspoiled mode | `.github/workflows/pages.yml` (new), `scripts/build_demo_bundle.py`, `frontend/src/components/{TournamentDashboard,MeetingView,ReplayPicker,ReplayControls}.tsx` | S–M (1 day) | "For this audience the URL *is* the project" (P3). Today every reader must clone ~256 MiB to see anything move. Do W2 first | Live URL in About + README line 1; `frontend/e2e/bundle.spec.ts` green against the deployed artifact; map visible at 1280×800 |
| W6 | **G-38 / V16** | Project the *intended* action into the spectator DTO: `PRETEND_TASK`, `EMERGENCY`, `REPAIR`, `BLOCKED` | `api/replay_loader.py:2208 _current_action` + `api/schemas.py` + `MapView`/`AgentToken` | S | Free (derived from the recorded `actions` row — **no re-record**), and it makes the impostor's central deception *visible* for the first time. 1747 fake tasks currently render as IDLE/MOVING | `TASK 0 → 1747` reclassified as `PRETEND_TASK`; DTO leak snapshot still green |

### 4.2 Week 1–2 — the front door and the two gate-truth fixes (no re-record)

| # | id(s) | What | Size | Why | Measure |
|---|---|---|---|---|---|
| P1 | **A1 + A2 + A5 + B8 + B12** | The README rewrite per C/F1: ≤150-word status, phase table extended to 19, the authorship statement (F5 draft is usable), the prose pass; create `docs/history.md`, `docs/glossary.md`, `audits/README.md`; move the 846-word ledger and the 234-word lever paragraph off the front door | M (2–3 d) | 6/6 personas stopped reading at README:84–107. This is *the* single change every persona named | `check_doc_facts.py` extended so the new numbers cannot rot; re-read time to "what is this" < 60 s |
| P2 | **A6** | Results stated once: README table (100/100 byte-reconstruct · 520/520 cited ballots · **proof 310/310 = 1.000 vs non-proof 46/125 = 0.368** · learned movers +0.12–0.30 wins, NOT adopted) + `docs/ml-program.md` in research shape (problem/env/method/results/limitations/related work), N1/N2 framed as specification gaming | M (1–2 d) | The enabling move for A1 (the ledger has to land somewhere) and the answer to "I cannot tell what was achieved". **The 19.14 cells are the strongest number in the repo and the README never states them** | One page a researcher can read in 5 min; every row cites a committed file; `paired_stats.py` reproduces the intervals |
| P3 | **A3(b) + B4 + B5** | Re-record the hero GIF at ≥1440×900 showing the map/a kill/the meeting pause (today the dock covers the canvas entirely — measured); an as-built architecture SVG one click from the top; show one contract → its generated prompt → the PR inline | S–M (1 d) | "The only asset most readers will ever see" never shows the product's central surface. B5 makes "350 agent-authored PRs" concrete instead of asserted | Frame-sheet check: map + a moving token + a meeting pause all in frame |
| P4 | **C-31** | Give `assert_packet_is_leak_clean` the `VisibilityResult`/`WorldState` and assert *entitlement*, not just shape | M (1–2 d) | DESIGN §11.2 calls it "the most important test"; B's 16-mutation harness shows **M6 (every undiscovered body visible) survives all four suites**. Your loudest test claim has a hole and *you found it yourself* — that is a B11 bullet | Re-run B's mutation harness: M6, M1, M10 all caught; ML champion gate (`training/crew/scorer.py:1735`) still green |
| P5 | **C-32 + C-125** | Add `orchestrator`, `api`, `eval` (and `scripts`) to `.importlinter` `root_packages`, or widen the AST scan; then correct README:74's "directly or transitively (import-linter enforced)" | S | Same shape as P4: the repo's loudest architectural claim is true only for hops via the 6 roots. Cheap; makes the claim true rather than softening it | Re-plant B's `agents/_probe_orch.py` → contract BROKEN |
| P6 | **C-34 + C-48** | Move `tests/test_firewall.py`'s planted files to `tmp_path`; enable `pytest-xdist`; promote the one shared replay fixture to session scope | S–M (1 d) | 2 of 7 concurrent `lint-imports` runs currently print a **false BROKEN contract**; the suite is 338 s serial and you are about to run it ~50 times during the wave. Pays for itself inside week 3 | `pytest -n auto` green; wall 338 s → target < 90 s; `check.sh` unchanged in semantics |

*Deliberately excluded from week 1–2:* everything else in C's B/C lists (B3 reading-guide split, B7,
B9, B10, B11) except that **B11 "what I learned" is scheduled after the record** (§4.5) because the
record gives it its best chapter.

### 4.3 Week 3–5 — the evidence-honesty wave (all items need the re-record to move the baseline)

**Day 1 of the wave, before any code: pre-register.** Write `tasks/phase-20.md` naming the metrics
and the bar *before* the fixes exist — non-direct conviction accuracy, innocent-ejection count,
crew false-`whereabouts` rate, sole-`alibi_vs_sighting` precision, adjacent-room share of STRONG
flags, and the four 19.11 fixtures as pass/fail exhibits. Pre-registration preceding measurement
preceding ruling is the thing P2 verified in git and praised; do it again and the wave writes its
own credibility.

Every item lands **default-OFF / lever-gated** (standing rule 4) so the committed baseline and all
gates stay green until the record.

| # | id(s) | What (the change, concretely) | Files | Size | Re-record? | Why it is on the critical path | Measure (all $0 offline against the current corpus first) |
|---|---|---|---|---|---|---|---|
| S1 | **G-3 / C-2** | Derive the completed-task memory line from the engine's `TaskCompleted` event, not from a `pending_task_id` flip | `agents/memory/store.py:1157-1200`, `agents/perception.py:354-361` (record `owned_task_ids`) | S | yes | The one unambiguous **bug** both tracks confirmed; it poisons *first-hand* memory — the channel the design treats as ground truth — and mints STRONG flags against innocents | Fabricated `You completed` lines 65/594 → **0** on a re-recorded set; the false-line detector from `verify-G-3` becomes a test |
| S2 | **G-1** | Render the self-location trail the store already keeps (`own_room_by_tick`) and re-date the completed-task line to the tick its room belongs to (today the room is right at N-1 97 %, at N only 16 %) | `agents/memory/store.py:1025-1028,1191-1205` | S | yes | 20.5 % of crew roll-call answers are invented; **44.3 % of innocent ejections are the victim mis-stating its own position**. `DESIGN.md:705` already specifies more than shipped. No prompt change needed | crew false `whereabouts` 20.5 % → target < 5 %; the s30-m3 and 4p1i-s10 exemplars stop reproducing |
| S3 | **G-9(a)** | Give movement a first-class encoding: a `moved` observation shape (or make the detector accept "A at T-1 → B at T" as consistent with "B at T") | `meetings/schemas.py`, `meetings/transcript.py:2379-2494`, `agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:205-209` | S–M | yes | **38/38** flags built on a re-spoken movement line are memory-truthful and spoken-false; **10 meetings ejected the innocent they framed**, one of them a 7–1 engineered by an impostor quoting the origin half of a true line | those 38 flags → 0; no new flag class appears in their place |
| S4 | **G-2 / C-11** | Ground the *prosecution* side the way the vouch side already is: resolve every spoken `saw_player` against the speaker's own `SightingRecord`; require 2 independent sources for a STRONG `alibi_vs_sighting`; suppress single-tick endpoint windows | `meetings/transcript.py:159-181, 2170-2179, 2379-2494` | M | yes | **The centrepiece.** 63.5 % of sighting sides were never perceived by the speaker; the class is 14.6 % precise as sole convicting evidence, below chance; 70 of 79 wrong ejections rode one | sole-flag precision 14.6 % → target ≥ 50 %; grounded share of sighting sides 36.5 % → 100 % |
| S5 | **R1 (A-researcher)** | Map-aware arbitration: adjacent rooms + ≤1 tick apart ⇒ demote or suppress the flag; ship the agent-side half as a map card in the prompt (R12) | `meetings/transcript.py`, the six `.j2` templates | S | yes | **148/234 (63 %) of STRONG `alibi_vs_sighting` name adjacent rooms** — one tick of walking reconciles both statements — and **0/7458 prompts contain a map or travel times**. Highest measured-veto-per-line in the whole idea list (78 of 126 flag ejections, 68 wrongful) | adjacent-room STRONG share 63 % → ~0; run as an **offline counterfactual on today's 300 games before recording** |
| S6 | **G-2 prompt / C-129** | Split the flag block by the taxonomy that already exists in code (`api/schemas.py::classify_evidence`): "role proof" vs "two accounts conflict and nothing here says which"; delete "each flag below is VERIFIED evidence … never side with an unverified counter-accusation" | `qwen3_6_27b/vote_ballot.j2:100`, `accusation_round*.j2` | S | yes | It is in **2543/2543** recorded ballot prompts and it is the sentence that converts a bookkeeping artifact into a conviction. Named explicitly in the close audit's Option-A scope | model-omniscient/gate-arithmetic language in rationales; `deduction_metrics` weak-flag-only convictions 5/5 innocent → 0 |
| S7 | **G-27** | Parameterise the persona by impostor count; fix the arithmetically wrong win condition told to crewmates and `"p-4 are your fellow saboteurs"` | all six `qwen3_6_27b/*.j2`, the render contract in `orchestrator/game.py` | S | yes | **100 % of prompts** in every 2-impostor game tell the crew to hunt one killer, in the same prompt that hands the impostor a teammate. Trivial, and it plausibly under-motivates the second ejection | 0 singular-persona strings in a 2-impostor render; a template test pins the count |
| S8 | **G-25** | Strip dev audit markers from `free_text` before the transcript, the prompt and the spectator; parse them into structured chips as ballots already are | `meetings/manager.py:3884-3912`, `accusation_round*.j2:136`, `api/replay_loader.py:2696-2703` | S | yes | Editor-console text sits **inside quoted dialogue in 12.6 % of prompts**, immediately before the sentence that usually names a vent. Breaks the fiction for every spectator and injects an unexplained token at the highest-leverage moment | markers in `free_text` 5.5 % → 0; contaminated prompts 12.6 % → 0 |
| S9 | **G-23** | Exempt dead/ejected subjects from "a witnessed vent outranks everything — speak it FIRST, even if you said it before" | `crewmate_report.j2`, `accusation_round*.j2` | S | yes | 300 `saw_vent` observations name a corpse; **5.0–5.5 % of turns have their accusation struck**; whole meetings (s13 m2, s15 m1 — the last 3-alive meetings) are spent re-prosecuting an ejected impostor | struck accusations 5 % → 0; meetings with zero live content down |
| S10 | **R4/R5 (G-35)** | Persist meeting outcomes into memory ("p-4 was EJECTED at meeting 1 — IMPOSTOR; one remains") and keep testimony as *content* ("p-8 says he saw p-4 vent") rather than `accused p-4` | `agents/memory/store.py:1485`, `meetings/manager.py` fold | S–M | yes | **0 / 7458 prompts** record any prior ejection or its revealed role. Nothing survives a meeting today; this is the cheapest possible way to make meetings compound | ejection-outcome lines present in 100 % of post-ejection renders; re-litigation meetings → 0 |
| S11 | **G-34 / R8 / C-73** | Coalesce co-presence into spans, drop the tick-0 lobby block when it is the full roster, raise reported-testimony salience above bare co-presence | `agents/memory/store.py:85,1854` | S–M | yes | The **enabler**: ~32 % of the block is recoverable at zero information loss, and without it S2/S10's new lines are shed first under the 1500-token budget (measured: reported rows kept **0/4150** at >150 candidates) | render lines/snapshot 53 → ~36; reported rows kept > 80 % at every budget |
| S12 | **G-36 / G-26** | De-duplicate contradiction flags (one fact rendered up to 4×); surface the ballot target-redirect instead of silently rewriting it | `meetings/transcript.py`, `api/replay_loader.py` | S | yes (dedup) / no (surface) | 84 eject ballots argue for a player they do not vote for; one duplicated flag ejected p-6 4–1 | duplicate flag copies 40 → 0 |
| S13 | **B §8 root cause 2** | A **render-version stamp** so the prompt byte-golden can pin "these recorded bytes reproduce under render v1" while new code emits v2 | `agents/memory/store.py`, `tests/meetings/test_prompt_byte_golden.py` | S–M | no | Structural: today every legibility fix is taxed a 23 h re-record. This is the one item that changes the *cost curve* of all future waves | The golden still fails on a one-byte template perturbation (its own self-test) and no longer fails on an intentional render bump |
| S14 | *(optional, if time)* **G-37 / C-119** | Resolve the +1 agent-clock convention: either re-stamp or label it explicitly everywhere | `orchestrator/game.py:1778-1793`, memory render, viewer | M | yes | Every watcher had to hand-derive it; it silently contaminated three of Track A's own headline numbers and it means a viewer scrubbing the map can never line up the dialogue | assert `obs.tick <= meeting.tick - 1` in a test; the viewer and the transcript agree at every frame |

**Internal dependency order inside the wave:** S1 → S2 (same lines in `store.py`); S2 → S4 (grounding
needs a self-record to ground against); S11 alongside S2/S10 (or their lines get shed); S6+S7+S9
batched into **one** prompt-version bump; S5 offline counterfactual runs before anything records.

**The offline dry-run that costs nothing.** Before the record, re-run the new detector rules over
the **existing** 300 committed games and publish: of the 79 innocent ejections, how many decisive
flags would no longer be minted. That is a real, falsifiable, $0 prediction made *before* the
measurement — exactly the pre-registration shape, and it de-risks a 23 h event.

### 4.4 Week 5–6 — the one re-record

- **Freeze the substrate** (standing rule: freeze-during-measurement). Nothing merges into
  `agents/`, `meetings/`, `observation/` or the prompt set while it runs.
- **Order of recording, by value:** `replays/samples/9p2i` (50 — the set the demo and the featured
  seeds serve) → `replays/samples/4p1i` (50 — fast, median ~12 ticks) → as much of
  `replays/ml_corpus/9p2i` (150) as the window allows. The corpus matters for *statistical power*:
  the non-direct cell is n=33 in samples but n=89 in the corpus; a delta on n=33 will not separate.
  If the window forces a choice, record 9p2i corpus **before** 4p1i.
- **Path:** `scripts/refresh_samples.sh` / `scripts/record_ml_corpus.sh` with
  `AILIBI_PROMPT_SET=qwen3_6_27b`, featherless, ~23 h operator wall, **$0**. Note C-74 honestly:
  these 917/1276-line bash runtimes have **zero automated coverage of their worker paths** — budget
  half a day of babysitting and keep the per-seed forensic copies.
- **Gates at close:** `scripts/verify_samples.sh` (100/100 byte-reconstruct), `scripts/validity_gate.py`,
  `eval/leak_scan.py` (now entitlement-checking, per P4), `scripts/check_doc_facts.py`, the
  prompt-version pins, MANIFEST regeneration, `scripts/check.sh` in a clean worktree.
- **The deliverable:** the before/after table from `eval/deduction_metrics.py` on the *same* cells,
  with Wilson intervals from `scripts/paired_stats.py`, plus a pass/fail line for each of the four
  19.11 injustice fixtures (each exhibit that stops reproducing is a named win; each that survives
  is a named residue).

### 4.5 Week 6–8 — after

| # | id(s) | What | Size | Why |
|---|---|---|---|---|
| F1 | — | Re-curate the featured seeds (`frontend/src/components/ReplayPicker.tsx::FEATURED_GAMES`, `scripts/build_demo_bundle.py`) against the new bytes and redeploy Pages | S–M | The old exemplars were chosen for the old corpus; some of your best demo games were injustices you just fixed |
| F2 | **A6 amend** | The README results table gains the before/after row; `docs/ml-program.md` gains the wave's close audit | S | **This is the payoff.** "Pre-registered, measured, reported — including the part that did not move" is the strongest single sentence this repo can add |
| F3 | **C/B11** | `docs/lessons.md` — "what I learned": directing agents at scale; what 4600 tests and 4 import contracts *could not* catch (a P0 cluster found in a day of watching); doc drift as a first-class bug; pre-registration; and owning P2's unrebutted critique — "strong on measurement, weak on knowing when to stop building measurement" | M | The one page only the human can write, and the thing every hiring-manager persona said they would ask about on the call |
| F4 | **C/B3, B9, B10** | Reading-guide split (3239 words at an advertised 5 minutes), the verifiable-shaped claim rewrites, commit-or-de-scope the 449-game finalist raw slate | S–M | Tail polish; do it only if the calendar holds |
| F5 | *(nice)* | One cross-model spot-check (10 seeds, second open model) to bound how model-specific the vent finding is; a write-up thread | S | P2's suggestion; cheap credibility on the generality question |

---

## 5. Success measurement, in one place

Everything below already exists in the repo — no new instrument family (heeding P2's D7 critique
that this project is "weak on knowing when to stop building measurement"):

| Instrument | What it gates | Where |
|---|---|---|
| `eval/deduction_metrics.py` | proof vs non-direct conviction accuracy; weak-flag-only convictions; turn→ballot consistency (0.447/0.459 today); impostor whereabouts coverage | the wave's primary bar |
| the four 19.11 injustice fixtures | executable exhibits: provenance-impossible sighting (9p2i s23 M1), content-vs-own-memory (s12 M0), one-tick interval (4p1i s41/s49), equal-weight conflict (s41) | pass/fail per mechanism |
| `scripts/verify_samples.sh` | 100/100 byte reconstruction in ~3.1 s | every commit, and the record's close |
| `scripts/check_doc_facts.py` | README numbers re-derived from committed bytes | keeps A1/A6 from rotting — **extend it with the new headline figures** |
| `scripts/paired_stats.py` | Wilson + exact McNemar | the before/after intervals |
| `eval/leak_scan.py` (post-P4) | packet *entitlement*, not just shape | the firewall claim |
| `eval/validity.py` / `scripts/validity_gate.py` | corpus acceptance (fix C-6's inverted guard at `:518` while you are in there — one line, and the correct version is already written in `training/anchor_study.py:631-655`) | the record's acceptance |
| B's own probes | `verify-C-7` phantom-frame counter, `verify-C-31` mutation harness, `verify-C-32` planted import, `verify-G-3` false-line scan | each becomes a test, which is how a review becomes an asset |

---

## 6. What I would explicitly NOT do, and why

1. **Do not re-open the ML program (Phase C / co-evolution / a training campaign).** The
   pre-registered NO-GO is already the strongest *research* artifact in the repo (54 checks in
   `verify_ml_evidence.py`, 0 failures, negatives surviving a 100×/300× sweep, pre-registration
   preceding measurement preceding ruling — all verified by P2 in git). P2's complaint is that it is
   **under-sold**, i.e. the gap is a 2-page write-up (A6), not more training. And anything trained
   must run on a post-substrate corpus, so it would queue behind this record anyway. Cost: weeks.
   Benefit: risks converting a clean negative into an ambiguous one.
2. **Do not put the balance levers in this record.** G-5 post-meeting reset, G-15 finished-crew
   jobs, G-12/C-3/C-4 impostor FSM, G-13 vent-peek, G-8 `saw_kill`, G-22 symmetric roll-call, G-40
   sabotage, G-43 the 4p1i second act. Every one is well-evidenced and several are large wins — and
   shipping any of them alongside the honesty wave destroys the attribution of the one measured
   delta you are buying with 23 h. They are the charter for the *next* wave. (G-12/C-3 in particular
   is a documented impostor buff worth its own baseline: 33–46 % of free kills declined, one game
   provably thrown.)
3. **Do not rewrite git history to shrink `.git` (C-45, 190 MB).** It would break the 43/44 in-code
   `audits/`/`tasks/` references, every PR link, and the commit-authorship graph that is **A5's
   evidence** — the provenance is the portfolio. Instead: `git rm --cached` the two regenerable
   aggregates going forward, extend `.gitignore` past the top level, and replace the ~150-word clone
   caveat with one line + `--filter=blob:none`.
4. **Do not refactor the God modules (C-62) or consolidate the 969-line fork (C-33).** 3989/3537/3193/3165-line
   files are real debt, but the refactor is invisible to all four audiences, high-risk against a
   byte-golden-pinned system, and B's own verdict REFUTED the fork's load-bearing risk (0 mismatches
   over 12 probed states). Buy 90 % of the credit for 1 % of the cost with C/B7: one honest paragraph
   in `docs/architecture.md` and a parity test.
5. **Do not attempt C-63 as a sweep** (33 % of non-test Python is prose, 129 files, 1896 `Task N.M`
   refs). The provenance is an asset. Do the targeted version: lead with plain intent in the five
   files a reader actually opens (`observation/service.py:31-83` is the named offender).
6. **Do not touch crew same-room-only vision or the vent channel.** All three A ideation lenses
   independently listed these as N1/N2 do-not-change: crew blindness is the forcing function that
   makes the meeting exist, and `vent_sighting` is 440/440 precise and carries 71 % of ejections.
   The problem was never the vent — it was everything else sharing its "VERIFIED" label (S6). The
   *only* sanctioned narrowing is adjacent-room **bodies** (not players), and even that belongs in
   the balance wave.
7. **Do not fix G-6** (bodies surviving meetings). Track A's own verification found fog-of-war
   working exactly as designed, the 230 figure unreproducible (189), the "invisible corpse" claim
   backwards (`discovered_by=None` is what makes a body *visible*), and **zero** real misses
   corpus-wide. Likewise drop the `died_at` field (G-7) — the surviving corollary is `saw_kill`,
   which is a balance-wave item.
8. **Do not build new eval instruments** beyond the one small flag-precision-by-source-and-adjacency
   row S5 needs. P2's "weak on knowing when to stop building measurement" is the one criticism no
   persona rebutted; the honest response is to reuse `deduction_metrics` + the 19.11 fixtures and
   put the critique in `docs/lessons.md` as an owned lesson.
9. **Do not chase the remaining ~94 P2 findings.** Take only those that make an already-*claimed*
   thing true (C-31, C-32, C-113, C-125, C-6's one-line validity fix) plus the two that unblock your
   own throughput (C-34, C-48). File the rest as a tracked backlog and say so — a triaged backlog
   reads better than a half-done sweep.
10. **Do not host a live-API deployment.** The static bundle is the sanctioned path
    (`docs/deployment.md`), it already has a relative asset base and an e2e spec that runs with
    `/api` blocked, and `SECURITY.md` already argues the trust boundary.

---

## 7. Calendar summary

| When | Wave | Re-record? | Portfolio effect |
|---|---|---|---|
| Weekend 0 | W1–W6: About/badges, MapView phantoms, prompt-set notice, vote-correctness truth-up, Pages + bundle/UI polish, PRETEND_TASK | no | The project becomes **linkable**. Recruiter and frontend personas unblocked in a day |
| Week 1–2 | P1–P6: README/authorship/results rewrite, GIF + architecture SVG + contract→prompt→PR, leak-scanner entitlement, import-linter coverage, fast hermetic suite | no | Hiring-manager, researcher and skimmer personas unblocked; two loudest claims become true; your own build loop gets 4× faster |
| Week 3–5 | S1–S13 evidence-honesty wave, pre-registered, default-OFF, plus the $0 offline counterfactual | built for it | The gameplay P0 cluster is *addressed*, and the fix is instrumented before it is measured |
| Week 5–6 | The single re-record (9p2i samples → 9p2i corpus → 4p1i), ~23 h wall, $0 | **the record** | The delta table |
| Week 6–8 | F1–F5: re-curate the demo, amend the results section, `docs/lessons.md`, tail polish | no | The story closes: measured problem → pre-registered fix → measured result → honest report |

**If the calendar collapses to 4 weeks:** keep Weekend 0 + week 1–2 in full, cut the wave to
**S1, S2, S4, S5, S6, S7, S8, S11** (the two confirmed bugs, the grounding, the map arbitration, and
the three prompt-string fixes — every one is S and together they are the entire measured causal
chain), record 9p2i samples + corpus only, and move `docs/lessons.md` ahead of the tail polish. The
portfolio story survives intact; only the residue list gets longer.

**If the record fails to move the metric** (the Phase-13.12 precedent — mechanism built, model could
not drive it): publish it as the result. This repo has already demonstrated twice that it can report
a NO-FLIP with the losing evidence committed, and every persona named that honesty as the thing they
would hire for. A pre-registered null on a fixed instrument is a better portfolio artifact than an
unmeasured improvement.
