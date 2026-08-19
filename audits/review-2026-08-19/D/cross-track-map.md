# The cross-track map — AiLibi (Track D synthesis)

Inputs, read in full: `A/collated-findings.md` (G-1…G-41 + 43 merged ideas + 12 adversarial
verdicts in `A/verdicts.md` + `A/ux-visual-pass-lead.md` + `A/ideas-summaries.md`),
`B/collated-findings.md` (C-1…C-130, §7 "genuinely good", §8 cross-cutting) + `B/verdicts.md`
(14 adversarial verdicts), `C/collated-portfolio.md` (A1–A6, B1–B13, C, D1–D9 rulings, E1–E8,
F1–F6). Repo read-only at `main b809b19c`. Owner-decision context:
`audits/audit-phase-19-close.md` §4 (substrate-first recommendation, the 19.14 proof/non-proof
cross-tab, the ~23 h / $0 re-record price).

**Sizes** are engineering size for the change named, not for the phase: **S** ≤ ~1 day,
**M** ~2–5 days, **L** > a week or a new baseline. **RR** = needs a real-LLM re-record
(~23 h operator wall, $0) *before the committed baseline can move*; **RR-free** = ships against
the existing corpus with every gate green.

---

## 0. The one-sentence result

**Track B found no P0 and Track A found eight** — and both are right, because the code is
correct and the *game* is wrong: nearly every gameplay P0 is a faithful implementation of a
rule nobody would have written if they had watched it run (G-1, G-2, G-5, G-6, G-7, G-8, G-19),
while nearly every code P1 is a latent hazard no spectator can ever see (C-1, C-6, C-12, C-31,
C-32, C-35). The three findable failures that are *both* — a real bug with a visible symptom and
a named code cause — are **G-3 ↔ C-2** (fabricated task memories), **G-2/G-9a ↔ C-11**
(unverified speech stamped VERIFIED), and **G-38 ↔ C-7** (the map paints corpses the engine
deleted). Those three are the spine of the whole review.

---

## 1. Why a cross-track map is possible at all: each track's structural blind spot

| track | can see | structurally cannot see | proof from this review |
|---|---|---|---|
| **A** gameplay-down | missing affordances, rules that read badly, everything that reached the corpus | latent code hazards no shipped policy reaches; the gates that *admitted* the corpus it measures | A never found C-1 (vent-legal kill), C-6, C-12, C-31, C-32 — none is reachable by the recorded FSM |
| **B** code-up | invariants, gates, provenance, hazards, cost | anything that is absent rather than wrong | B reviewed `agents/memory/store.py` five times (C-2, C-10, C-29, C-71, C-72, C-73) and never noticed there is no self-location line (G-1) — because no code is broken |
| **C** portfolio | what a stranger believes in 6 minutes | any mechanism; it reads claims, not behaviour | where C *did* run things (X1) it independently hit B-class defects: C's B2 (fake tournament yields an all-null report) is exactly B's **C-88** (`fake-target-<hash>` ⇒ every fake ballot normalises to SKIP, `claims=[]`) |

Three clean cases of two tracks measuring the same object from opposite ends without knowing:

- **C/B2 ↔ C-88.** Persona saw an all-null report; code review found the mechanism. One fix (B2 +
  C-88) closes both.
- **C/B1 (first-run `AILIBI_PROMPT_SET` warning, printed 6× in the README's own 5-game command)
  ↔ C-83 + C-126 + C-130.** The warning is printed at *import* time (C-83), names a variable
  documented in no `.md` (C-126), and defends a default prompt set that **no committed replay
  uses** (C-130). One three-line fix closes a front-door wart and three code findings.
- **C/A3 (hero GIF never shows the map — canvas top 311 px vs dock top 308 px at the 1000×640
  recording viewport) ↔ `A/ux-visual-pass-lead.md`** (dock is ~35 % of a 900 px viewport, map
  entirely hidden at 800×450). A frame-sheet and an in-app browser pass measured the same CSS.

---

## 2. §A — Gameplay finding → mechanical cause → portfolio consequence

### 2.1 The P0 cluster

| G | claim (verdict from `A/verdicts.md`) | code finding(s) that explain it | portfolio consequence | size / RR |
|---|---|---|---|---|
| **G-1** | No "you were in ROOM at tick N" line, yet the roll-call demands one → 20.5 % of crew whereabouts false. *PARTIALLY-TRUE: mechanism CONFIRMED-BUG; attribution honest-split 44.3 % victim-caused / 21.5 % **witness**-caused* | **No B finding exists** — the store *keeps* `own_room_by_tick` (`store.py:1025-1028`) and uses it only to scope others' sightings. Nearest: **C-71** (`WorkingMemory` is scaffolding + a render-time cache), **C-73** (salience 25 sheds testimony first), **C-117** (DESIGN §6 drift). Aggravator: the one self-placing line is mis-dated — matches the agent's room at tick N only **16.0 %** of the time, at N−2 **100 %** (A/G-1 verdict) ⇒ same clock seam as **G-37/C-36** | Falsifies README:78 *"Memory is structured first. Each agent reasons from a typed event log and a derived belief state (suspicion, trust, alibi)"* — the agent cannot state where it was. Touches P1 (hiring manager: "the one technical claim I'd probe"), P2 (env spec), C/A6 results table | S (render spans the store already holds) · **RR** |
| **G-2** | `alibi_vs_sighting` STRONG = speech-vs-speech, labelled "VERIFIED evidence", **14.6 % precision as sole convicting evidence** (12 right / 70 wrong); **70 of 79 wrong ejections** carry one and it is the only strong flag in all 70. *CONFIRMED-DESIGN-CHOICE (gate crossing twice owner-ratified) with a bug-shaped residue* | **C-11** (P1, verdict CONFIRMED, "very high"): `_detect_alibi_vs_sightings` never reads `sighting.speaker`; `detect_contradictions()` has **no `sighting_records` parameter**; the grounding channel (`SightingRecord`, Task 16.7) is wired only to the *exculpatory* −0.05 vouch. Independent census: STRONG `alibi_vs_sighting` names an impostor **11.7 %** vs a 26.1 % base rate — *anti*-informative; **20 of 25** wrongful ejections vs `vent_sighting` 107/107 impostor. Plus **C-129** (`vote_ballot.j2:100` "VERIFIED evidence" vs `meetings/schemas.py:426` "Flags are information, not verdicts"), **C-15** (weak/strong band is an in-band substring of LLM text), **C-19** (`PHYSICAL_CONTRADICTION_MIN_VOICES = 2` == the impostor count) | The centre of gravity. `docs/reading-guide.md:196` *already discloses this honestly* ("40 % of directional flag subjects in 9p2i are innocents") — **the project's docs are more honest than its prompts.** Fixing the prompt converts a disclosed weakness into a shipped result (C/A6, C/D4). It is also scope item 1 of `audit-phase-19-close.md` §4.2 | S (naming) + M (grounding) · **RR** |
| **G-3** | `redistribute` mints false `You completed X` memory lines. *CONFIRMED-BUG* — **10.0 % (9p2i) / 23.1 % (4p1i)** of all completion lines false, **159/300 games**, 100 % correlated with a kill/ejection at T−1/T−2, 21 spoken as alibis, **3 minted STRONG flags against innocents** | **C-2** (P1, verdict CONFIRMED, borderline P0 for evidence integrity): `dead_task_rule: redistribute` grows `owned_task_ids`; `store.py:1157-1200` infers a completion from any `pending_task_id` change under the comment *"Its owned set only ever shrinks"*. `observation/service.py:638-645` picks the lexicographically-first owned id, so an inherited earlier-sorting task flips it. Gated to `role == "CREWMATE"` — **the bug is one-sided against the crew.** Companions: **C-24** (redistribute is an instantaneous kill side-channel on the self channel — 13/16 kills), **C-119** (the invariant comment is false), **C-115** (DESIGN.md documents only the retired `drop` rule; `grep redistribute DESIGN.md` → 0 hits while `tick.py:378` cites "§3.5 (dropped)"). **A test pins the defect**: `test_pending_rollover_to_next_map_id_emits_completion` | The best *story* in the review and the cleanest interview anecdote: a one-line comment stating an invariant, a map-config flip that broke it two phases later, a doc that never recorded the flip, and a test that enshrined the wrong behaviour. Belongs in C/B11 "What I learned" verbatim | S (derive from `TaskCompleted`) · **RR** |
| **G-5** | Meetings are disembodied: no gather, no cooldown reset, **9.8 % of meetings have a participant speaking from inside a vent**, **15.7 % of reporters die ≤3 ticks after their own meeting** (claim said 89; true 111/707). *PARTIALLY-TRUE — (1)(2) documented design, (3) CONFIRMED-BUG* | The venting-participant half is the **C-1 family**: the engine consults `in_vent` on move/do_task/emergency/repair and **not** on kill/report/sabotage (`rules.py:56,182,225`), and the meeting roster is gated on liveness only (`game.py:1029-1031`) — one blind spot, two surfaces. **C-68** (`MeetingTrigger` has no structured `kind`; emergency-vs-report is a substring) is the adjacent smell | The single most-corroborated gameplay item (12/13 A reports) and the one a viewer notices in game one. Directly damages C/E3's "best debugging surface" impression: an agent argues about where it was from inside a vent | M (reset) · **RR** |
| **G-6** | Only the reported corpse exists; 172/798 never reported. **REFUTED as a defect** — `discovered_by=None` is what makes a body *visible*; **0 real misses** (all 6 crew-seen unreported bodies had gap = 0, final tick); 230 → **189**; the "corpse in the meeting room" image is an artefact of meetings being non-spatial | The *spectator-side* corpse defect is real and is **C-7**: `MapView.buildBodyStatesByTick` accumulates kill events and never deletes, ignoring `TickView.bodies`; **1182/1769 frames (67 %), 50/50 games** show corpses the engine already consumed, styled identically to real ones | Do not "fix" the engine. Do fix the map before hosting the demo (C/A3) — this is the defect a viewer *does* see, on two thirds of frames, on the surface C calls the star-making asset | S (read `TickView.bodies`) · **RR-free** |
| **G-7** | `found_body` carries the report tick, never the death tick. *PARTIALLY-TRUE — documented design; the histogram is inflated by one tick by the agent-clock offset (**17.8 % land exactly** on the kill tick after correction); still 82.2 % late, 18.7 % of body meetings never touch the kill tick* | No B finding (`BodyState` simply has no death field, `entities.py:43-49`). The sharper defect A's verifier surfaced is **G-8's**: `You witnessed pN kill` exists in memory with the true tick, **93.5 % of witnesses are alive at the next meeting**, and it is *unspeakable* | Feeds the same README/reading-guide claim as G-1: typed memory that cannot express the two facts a detective needs (where I was; when they died) | S (`fresh`/`cold` band) · **RR** |
| **G-8** | A witnessed kill cannot become evidence for anyone but the witness (0.025 % of memory lines; +0.08 to peers). *PARTIALLY-TRUE — an owner-LOCKED deferral (`tasks/phase-13-5.md:159-201`); the kill-scene path fires **once in ~830 contradictions***. Killer ejected 30 % after a witnessed kill vs 66 % after a witnessed vent — **and a second eyewitness makes it worse (20 %)** | No B finding — the schema is as designed (`meetings/schemas.py:454-456`, 4 kinds). Related: **C-72** (half the belief model is dead — `trust` never written, `record_contradiction` never lands: `## Open contradictions` in **0/1656** renders) | The most quotable inversion in the game and the best "designed, measured, ruled" anecdote — the deferral was a *documented* choice to stop fabricated kill-accusations, and the corpus shows the STRICT gate is an OFF switch. C/B11 material; also the honest answer to "why doesn't the meeting decide?" | M (`saw_kill` kind) · **RR** |
| **G-19** | Meeting outcome is a function of the flag detector, not the discussion (flag ⇒ EJECT predicts 88.5–100 %); spoken confidence 0.6–0.8 is *below* the 25–29 % random baseline | **C-11** (the flag that decides is the anti-informative one) + `beliefs.py` `CONTRADICTION_SUSPICION_DELTA = 0.3` vs weak `0.08` (quoted in B's C-11 verdict) + **C-63** (`apply_meeting_evidence_rules` = 210-line docstring, 14 kwargs, **CC 54 / radon F** — the function that decides the game is the least legible in the repo) + **C-72** (the persistent half of the belief model is dead) | This is the finding the project's own close audit already priced: proof cell **310/310 = 1.000**, non-direct cell **46/125 = 0.368**, all 79 innocent ejections in the non-direct cell. Three independent tracks and the owner's audit converge — the strongest possible argument for Option A | L (phase) · **RR** |

### 2.2 The P1 cluster

| G | claim | code finding(s) | portfolio consequence | size / RR |
|---|---|---|---|---|
| **G-4** | Crew fabricate testimony that renders as fact. *PARTIALLY-TRUE — `saw_vent` **REFUTED** (739/748 grounded; the 9 exceptions are witnessed **kills** filed in the wrong slot, cf. G-8); `saw_player` **CONFIRMED** 11.6–13.3 % unseeable, 71 % of false placements name a hallway* | **C-11** again (no provenance chokepoint on the prosecutorial side). A's verifier adds a fresh one B missed: `RoomId: TypeAlias = str` (`meetings/schemas.py:41`) — no map validation; `CAFERIA` was accepted, stored and rendered into the next prompt | Softens the scariest-sounding gameplay claim: the vent channel is honest and *well-defended* ("an ungrounded spoken vent mints NOTHING"). That defence is the template for the G-2 fix and is a good story: the right thing was already built once | S (room enum) + M (ground sightings) · **RR** |
| **G-9a** | `You saw X move A→B` has no structured counterpart; **38 flags speak the origin, 38/38 factually false, 10 wrong ejections**. *CONFIRMED-BUG* | **C-119** (`packet.py::MovedPlayerView` claims "WITNESS-gated exactly like a saw_player sighting" while `service.py` calls that gate "wrong"), **C-23** (`_moved_players_for_agent` lacks `actor != agent_id`, so an impostor's own move rides its packet — papered over twice downstream), **C-11** (nothing grounds the spoken side) | The exemplar (`seed 39 m0`: an impostor quotes the *origin* half of a true movement line and manufactures a 7–1 ejection of the body reporter) is the single best 60-second demo of "why evidence honesty matters" — better than any prose | S (`saw_move` shape / detector rule) · **RR** |
| **G-9b** | Departure-room gate evaluated on post-advance visibility. *CONFIRMED-DESIGN-CHOICE — cited cause **refuted**, already owner-pinned; 18.2 % of move lines unwitnessable, but **19 435 genuine departures are dropped** vs 7 569 kept* | same file, `observation/service.py:463-505`; hook already exposed (`departure_visible_rooms` in `eval/leak_scan.py`) | Low priority; mention only as the counter-example to "every finding is a bug" | S · **RR** |
| **G-10** | Contested kills 100 % decided by player id (156/156 lower-id escape, 90/90 higher-id die; per-seat escape p-1 24.7 % → p-9 0 %). *CONFIRMED-DESIGN-CHOICE — `DESIGN.md:334` states it verbatim and names per-seat fairness as its own open item* | **C-22** (kill/vent **witness** membership has the same id dependency — `exp_witness_order.py`), **C-95** (`_action_order_key` claims a `type`/payload tie-break that `_validate_unique_actors` makes unreachable — the code advertises an ordering rule it never exercises), **C-18** (engine invariants hold only under the orchestrator wrapper), **C-25** (post-trigger actions vanish with no `ActionRejected`, against DESIGN §3.1) | Determinism ≠ fairness. B's §7 praises determinism at length and is right; this is the one place a reviewer can say "deterministic and unfair", and the honest answer is already in DESIGN.md. **Any per-seat metric ever published must control for it** | M (move-before-kill or seeded order) · **RR** |
| **G-11** | Vent/kill witness sets depend on intra-tick id order | **C-22** exactly (`exp_witness_order.py`: witnesses `('p-5',)` only) | see G-10 | — |
| **G-12** | Impostor FSM stalks ejected players for 30 ticks. *CONFIRMED-BUG (seed 36 = a demonstrably thrown game) with magnitudes corrected: ghost-top **8.3–12.3 %** of decisions, not "most dead time"; seed 42 **refuted**; **0/100 in 4p1i** — the defect is 9p2i-only and biases the canonical impostor baseline downward* | **C-4** (P1: stalk ignores negative evidence — `stalk_moves=880, toward_refuted_sighting=298 = 34 %`) and, larger, **C-3** (P1, verdict CONFIRMED and *understated*): the kill seam re-validates only `targets[0]`, so **190/415 = 45.8 %** of free zero-witness kills are declined, **168/168** of them on an exact 1.0 score tie broken by the lower id. A's veteran lens measured the same thing from the replay side — *"55.8 % of solo + off-cooldown decision points declined"* — with no knowledge of C-3 | **The strongest independent corroboration in the whole review**, and it re-frames a long-running project narrative: *"the impostor never wins / the meeting never decides"* has been measured on a hobbled inner loop. That sentence belongs in the ML page (C/A6) and in "what I learned" (C/B11) | S (re-validate across targets) · **RR** |
| **G-13** | Vent exits are blind and land in occupied rooms (exit seen 56.5–59.2 % vs enter 8.8/6.4 %); 71 % of ejections are `vent_sighting` | no B finding (policy, not a rule violation) | Do not over-fix: A's three ideation lenses independently rule the vent channel untouchable (440/440 precise). "Peek before venting" is the narrow repair | S · **RR** |
| **G-14** | Crew blind one room away, impostors not: **327/798 kills (41 %) had an adjacent blind crewmate, 327/327 perceived nothing**; impostor testimony is the most accurate at the table | **C-115**: `canonical_1.yaml` still *documents* `base: same_room_and_adjacent` "uniform across the map" (and its `visibility:` block is rejected by `Room(extra="forbid")`) while `engine/visibility.py:98-126` applies the asymmetry in code | Keep the mechanic (all three A lenses say so: it is the forcing function that makes the meeting exist), fix the map file, take the narrow repair (adjacent-room **bodies** only). A doc-vs-code split on the game's most counter-intuitive rule is exactly what a senior reviewer probes | S (doc) / M (bodies-only) · doc **RR-free** |
| **G-15** | Finished crewmates emit `wait` forever — **7 939 done-crew ticks, 60.4 % literal `wait`, max run 36 ticks**; 45.9–61.4 % of ticks contain no event at all | no B finding (missing behaviour) | The watchability ceiling. Every A watcher raised it; it is the reason the hosted demo (C/A3) needs *curated* seeds, and the reason the featured-strip curation is a genuine product decision worth naming | M · **RR** |
| **G-16** | Redistribution is a body-beacon / progress-bar reversal / death conveyor (**485 `task_progress` decreases**) | **C-2 + C-24** (same mechanism as G-3, second-order) | one fix, three symptoms — good "root cause" material for B11 | S–M · **RR** |
| **G-17** | The emergency button is a t10 timer: **112/112 `suspicion_accumulation`, 0/112 with a body in view, 71/112 at t10–t11**; a fresh-crossing rule blocks a witness who already suspects | **C-68** (emergency-vs-report is a `EMERGENCY_TRIGGER_PHRASE` substring across 15 templates while the orchestrator *has* the structured event and discards it); **C-105** (three strict xfails for `TestEmergencySuspicionMeetingEndToEnd` dead since Task 13.8, "until Wave B redesign lands" — the redesign never came) | C-105 is the tell that this is *known* dead scope. Cheap honesty win: either delete the xfails or schedule them | S · **RR** |
| **G-20** | Impostor SKIP bloc is a free blocking vote (SKIP rate 75–95 %; **39 of 78** skipped-with-eject-ballots meetings had a real impostor as sole non-SKIP leader) | **C-103**: three tally tests "pass for the wrong reason" — their eject ballots are coerced to SKIP by the citation gate *before* the tally, so `SKIPPED` is asserted on a 4×SKIP tally, not a tie; **they would pass under a broken tally**. The SKIP-plurality semantics is the least-tested rule in the meeting | The clean example for the "gates that don't gate" root cause (RC7), on the rule that decides the game's outcome | S (tests) / M (rule) · tests **RR-free** |
| **G-21** | Meetings don't compound: vote-time lift **+0.209 → +0.040 persisted (19.1 % retention)**; nothing between belief 0.65 and 0.90 | **C-72** (P2 but load-bearing): `trust` never written (always 0.5), `record_contradiction` never lands on the persistent store — `## Open contradictions` in **0/1656** renders and `trust` lines in **0/1656**, "while DESIGN §6.6 still shows both as canonical". **C-66** (the belief fold is ~500 lines welded into `meetings/manager.py`, straddling the layer boundary an import-linter contract exists purely to police) | **C-72 is the direct falsifier of README:78's "(suspicion, trust, alibi)".** One-third of the advertised belief model is dead in production. This is the highest-value doc-truth fix in the repo: either wire it or stop claiming it | S (claim) / M (persist) · claim **RR-free** |
| **G-22** | Two mechanical role tells: **P(impostor \| no whereabouts) = 97.7–100 %**; **0/626** impostor body reports, **0/707** impostor meeting calls | **C-130** (`impostor_report.qwen3_6_27b.v3` is a pinned, version-bumped template with **0 calls out of 7 932**; five sweep sets and the *default* set are used by no replay), **C-116** (DESIGN §5.2 doesn't know the roll-call round exists and calls voting "parallel"; opt-in is now an ordering rule, and both kinds record `turn_kind="opt_in"` so a transcript cannot distinguish them) | A version-bumped, zero-call template is a perfect small exhibit of RC6 (byte-preservation beyond its remit) and is trivially fixable | S · **RR** |
| **G-23** | Prompt mandates re-litigating a vent whose subject is already dead (**232 such observations**; 5.0–5.5 % of turns lose their accusation to a corpse) | **C-72** (no meeting outcome persists anywhere) + **C-129** (prompt content). A's researcher lens: **0/7 458 prompts record any prior ejection or its revealed role** | The most visible "why are they still arguing about him?" moment for a viewer. Cheapest legibility fix in the track | S · **RR** |
| **G-25** | `[invalid accusation target 'p-N' dropped]` is spliced into spoken text and rendered verbatim into later speakers' prompts. *PARTIALLY-TRUE — turn half CONFIRMED-BUG (**246/1956 = 12.6 %** of prompts contaminated, 25/50 games); ballot half REFUTED as a leak (0/7458 prompts) and DESIGN-sanctioned* | **C-67** (guard activity exists only as marker substrings parsed by four packages; the `{x!r}` repr shape and `]` terminator are load-bearing across `api/`, `eval/` ×3, `training/surrogate/`), **C-15** (the weak/strong band is itself an in-band substring — a crafted room string flips STRONG to weak), **C-129** (`autoescape=False`, no `max_length` on `free_text`) | One in eight prompts contains editor-console text inside quoted dialogue, and it is on the spectator surface the demo shows. `ReplayLoader` already strips ballot markers into chips — the turn path was never given the same treatment | S · **RR** |
| **G-27** | Every 2-impostor prompt says "a hidden impostor" (singular). *CONFIRMED — **1956/1956** and **5502/5502** prompts, 100 %; 490/1956 carry the singular persona **and** "Your fellow saboteurs: p-8" in the same prompt; the stated win condition is arithmetically wrong for 2 impostors* | **C-129** states the mechanism exactly: *"the render contract carries no impostor count, so the templates cannot say it right"* | A visitor reading the Mind Inspector's prompt tab (C/E3's showcase surface) sees it in their first meeting. `A/ux-visual-pass-lead.md` hit it in one pass. Embarrassment-to-effort ratio is the highest in the review | S · **RR** |
| **G-31** | Reporter-blame is the default deflection and it works in speech (65/165 meetings; only 3 reporters ever ejected) | **C-68** (the reporter-exculpation path keys off `EMERGENCY_TRIGGER_PHRASE in trigger.description`) | Good news, actually: the ballot-time guard works. Worth stating as a designed defence that holds | — |
| **G-34** | Memory render: **66.1 % bare co-presence/movement, 1.54 % hard evidence, 49.8 % of snapshots contain zero hard-evidence line**; the constant tick-0 spawn block (14.4 %) outranks prior-meeting testimony under budget | **C-73** (P2, load-bearing): reported testimony has salience 25, below every first-hand row; over 60 games / 1 656 renders it is kept **0/4 150 at >150 candidates**, and **166 of 835** renders with reported rows shed ALL of them. **C-117** (DESIGN §6.6 claims 8k–16k budgets; production is 1 500 everywhere). **C-43** (`recent()` linear rescan, Θ(T²)) is the perf twin of the same "no coalescing" choice | A's researcher lens found the smoking gun: in seed 17 the correct sighting row *was present*, at line 22, under twelve near-identical CAFETERIA rows — **"the model is reading the top of a badly sorted list, not hallucinating."** That sentence reframes the whole ML narrative (C/A6, C/D4) away from "the 9B is too weak" | S–M (coalesce + drop spawn) · **RR** |
| **G-35** | Testimony is absorbed as `[meeting] CLAIM by X (unverified): accused Y` — the *content* is dropped; the liar's alibi buys the **larger** discount (−0.086 vs −0.04) | **C-72** (contradictions never persist), **C-29** (`record_alibi` never dedups and `absorb_reported_testimony` stores only `from_tick`, so "ticks 0–1" renders "at tick 0"), **C-117** (§6.1's own truth-up note is stale three ways) | Same README:78 claim | S–M · **RR** |
| **G-37** | Agent tick stamps are +1 vs the replay timeline; own-task lines −2. **111 283/111 283** sighting lines match at Δ=−1, **0** at Δ=0; meeting headers 771/771 exact | **C-36** (P1): eight independent reimplementations of the tick+meeting loop; the eval walker reads 24 ticks where the api loader reads 25 and *"agree, but **no test asserts it**"*. Cause named in C-36's own evidence pointer: `orchestrator/game.py:1786` (packets built before `advance_tick`, `input_tick=N` recorded beside post-advance state) | Every one of the eight A watchers opened their report with a hand-derived "tick convention" paragraph — that is 8 × the onboarding cost of one missing assertion, and it silently inflated G-7's headline by one tick. The friction is the finding | S (assert + re-label) · label **RR** |
| **G-38** | Spectator DTO misrepresents four action classes (**1 747 fake `do_task` → IDLE 800 / MOVING 844 / TASK 0**, while co-located crew correctly see `task`); the map never clears bodies | **C-7** (verdict CONFIRMED, all numerics exact: **1182/1769 frames = 66.8 %, 50/50 games, `phantomWithoutReport: 0`**; `TickView.bodies` + `killed_by` are served correctly and have **no frontend consumer**). The `current_action` half has **no B finding** — the DTO layer was reviewed (C-87, C-65, C-51) for *shape*, never for *meaning* | The demo is the star-making asset (C/A3, C/E3) and its map is wrong on two thirds of frames. **C-80** explains why it was never caught (MapView's five pure derivations live in `.tsx` the node-only vitest project cannot import) and **C-101** why nothing would have (zero component render tests; test:prod ratio 0.15 vs 1.6–2.8 for Python). Note the dependency: projecting the real action changes `api/schemas.py` ⇒ a `viewModelVersion` bump ⇒ **C-8 escalates from P2 to P1** the day that lands | S (bodies) / S–M (action) · **RR-free** |
| **G-41** | Spectator UI: internal jargon on the product surface ("(DESIGN.md §11.3)", "Task 9.6 / 10.x", "56/100 MED · INTERNAL HEURISTIC", unlabelled R1/R2/R3/R7); dock takes 35 % of a 900 px viewport; the ballot "CORRECT" badge spoils role in unspoiled mode | **C-79** (`App.tsx` 1 181-line God module contradicting its own no-edit header), **C-90** (a11y: `role="slider"` on a div containing buttons; no role/keyboard on `EventTimeline`; no `aria-label` on the Pixi canvas), **C-58** (per-frame `TextStyle` churn; `KillFlash` never terminates — parking on a kill tick drives an unbounded render loop), **C-9** (two stacked focus traps lock the keyboard when the tour is over an open meeting) | This is C/B6 verbatim, from an independent direction. All of it is RR-free and all of it is pre-flight for A3 | S · **RR-free** |

### 2.3 The P2 tail (compressed)

| G | code cause | note |
|---|---|---|
| G-18 kills land on the meeting tick | **C-25** (post-trigger actions vanish with no `ActionRejected`, against DESIGN §3.1), **C-18** | 11 kills on the exact trigger tick; 32 attempts annihilated at no cooldown cost |
| G-24 fixed round-robin in a debate costume | **C-116** (opt-in is an ordering rule, not a gate; both kinds record `turn_kind="opt_in"`), **C-91** (ballots hard-coded sequential, no `MeetingConfig` knob) | 553/1542 accusations never answered |
| G-26 ballot redirect contradicts its own rationale | **C-67** | 84 eject ballots argue for a player they do not vote for |
| G-28 impostor ballots confess the role (15.6–15.9 %) | **C-129** (`vote_ballot.j2:126` asks for an honest rationale after ordering a teammate redirect) | masking exists for the *target* (`TEAMMATE_VOTE_TARGET_MARKER`), never for the rationale |
| G-29 threshold arithmetic in characters' mouths ("0.60 threshold" ×208) | **C-129** (instructions are 55–70 % of a 3.9–5.9 k-token prompt; "one room, one tick" ×11) | |
| G-30 confidence bimodal, 0.80–0.90 less accurate than 0.60–0.70 | **C-72** + the ballot prompt's own confidence cap (A researcher lens: 3 697/3 697 prompts) | ≥337 crew ballots named a real impostor aloud and voted elsewhere |
| G-32 impostor `found_body` self-incrimination ignored | **C-11** (no contradiction kind consumes it) | 27 spoken before the body's report; 4 for a body never reported |
| G-33 impostor never self-reports / never plays its ballot | **C-130** (0/7 932 calls to its report template) | |
| G-36 duplicate contradiction flags | **C-29** (`record_alibi` never dedups) | same sentence rendered up to 4× |
| G-39 impostor pairs travel together; the opening is a script | — | 43/50 first kills at t4–t5; 10/10 identical openings in 4p1i |
| G-40 sabotage is a walk simulator; "when the lights went out" with no lights sabotage | **C-115** (DESIGN says "lights only / no reactor"; the shipped map has `reactor` with `gates_tasks`) | 110 sabotages, **100 % reactor, 0 lights ever** |

---

## 3. §B — Code P1s with no gameplay symptom: would a spectator ever notice, and why they still matter

| C | would a spectator notice? | why it still matters | portfolio claim it touches | size / RR |
|---|---|---|---|---|
| **C-1** kill/report/sabotage legal from inside a vent | **No** — both shipped policies short-circuit on `in_vent`; no committed replay is contaminated | The **training action mask actively advertises** kill+sabotage as engine-legal while vented (`training/env.py:288-296`, pinned by `test_mask_legality_against_engine`). The next sampled policy discovers a strictly dominant untraceable strategy: never appear in `visible_players`, keep full sight, kill on cooldown, open the meeting yourself. It also inverts the engine's own stated principle (`rules.py:60-66`: "a buggy or future LLM-driven policy must not be able to") | README/`docs/architecture.md` "the engine is the single source of truth"; blocks any future ML re-open (C/B10, D4) | S (3 guards + mask) · **RR-free** |
| **C-5** corrupt/truncated/empty replay 500s the listing and the cost endpoint | **Yes, but only after they break something** — one Ctrl-C'd tournament and the whole picker 500s; an empty file is served as a valid 0-tick replay and counted in `cost_summary` | Exactly the X1 reproduction path: the README hands a stranger a tournament command. It also makes `api/replay_loader.py:716` ("one bad replay no longer blocks the picker") an overclaim, in a repo whose AGENTS.md forbids silent fallbacks | C/X1 front-door; C/B9 "make claims verifiable-shaped" | S (one `except ValueError`) · **RR-free** |
| **C-6** `reconstruct_episode` + **`eval/validity.py:518`** read corruption as legitimate truncation | **No** | It is the **corpus acceptance gate**: a shortened replay passes `all_games_reach_game_over` and enters downstream as "verified". The correct version already exists in `training/anchor_study.py:631-655` and was never back-ported | The "100/100 replays byte-reconstruct" claim (C/E1) is the front door's best asset; this is the one gate that would let a bad one through | S · **RR-free** |
| **C-8** two raw `fetch`es bypass `assertViewModelVersion` | **Not yet** — `VIEW_MODEL_VERSION` has never been bumped. **The Tournament route has no guarded payload at all** | Latent until the first bump — which the **G-38 DTO fix would cause**. Sequencing dependency, not a free-standing item | C/A3 hosted demo (the Tournament tab is already the bundle's worst surface) | S · **RR-free** |
| **C-9** two stacked focus traps (`useFocusTrap` + GuidedTour's un-deleted inline copy) | **Yes** — a keyboard user in the guided tour over an open meeting: Tab is a no-op, "Back" unreachable | The guided tour is the demo's opening move (C/E3, `ux-visual-pass-lead`). This is a hosted-demo pre-flight item | C/A3 | S · **RR-free** |
| **C-12** LLM output schema == record schema; junk in a discarded identity field defaults a content-valid turn | **No** — 0 occurrences in 204 committed meetings | Fires on a **model swap**, and a model swap is the standing Phase-14 plan. The failure is silent and mislabelled ("missed deadline; no turn submitted") | any future model-portability claim (C/P2's "one model, n=50" caveat) | S · **RR-free** |
| **C-13 / C-14** failed-call spend never charged to `GameBudget`; successful calls before a meeting abort are dropped and `compute_cost_usd` under-reports (**$0.10 burned → 0.0 reported**) | **No** — production is $0 flat-rate Featherless | C-14 directly contradicts `replay.py:1071-1076` ("a crashed run's spend is not silently undercounted"). The cost dashboard is a shipped product surface | the cost-transparency story in the Tournament tab | S · **RR-free** |
| **C-31** the leak scanner cannot check visibility entitlement | **No** | `assert_packet_is_leak_clean(packet, events)` takes no `WorldState`/`VisibilityResult`, so it validates shape and strings, never entitlement. **M6 (every undiscovered body visible to everyone) survives all four suites, whole-suite diff empty.** It is the gate `DESIGN.md §11.2` calls "the most important test" and the one the ML champion path runs outside pytest | README "zero firewall violations" / C/E2 "architecture enforced by tooling, and it is real". **This is the single most important claim-integrity fix in the repo** | S–M (pass the visibility result) · **RR-free** |
| **C-32** import-linter blind to `agents → orchestrator\|api\|eval → engine` | **No** | A planted `agents/_probe_orch.py` importing `orchestrator.game` passes all four contracts *and* `check.sh` green. Coverage is **89 of 383 tracked `.py`**; `api/`(8), `orchestrator/`(8), `eval/`(25), `scripts/`(18), `experiments/`(49) have none. `README.md:74` says "directly or transitively (import-linter enforced)" | Same claim as C-31 — and C/B9 already asks (blind) for exactly this rewrite: *"'zero firewall violations' → 'never breached in CI: contract + planted-leak test + recursive sweep'"* | S (4 root packages) · **RR-free** |
| **C-33** 969-line fork across the `agents ↛ training` firewall | **No**. *Verdict: PARTIALLY-TRUE* — the risk assertion is **refuted**: five always-on parity gates exist and a 1e-9 injected drift goes loudly red | Residual is narrow and real: `_build_action_mask` (147 lines) is **uncovered** by the Q4 gate and its own parity test exercises **one** packet state | reads as duplication to any senior reviewer; needs one sentence in `docs/architecture.md`, not a refactor | S (doc) · **RR-free** |
| **C-34** `tests/test_firewall.py` plants 5 files at fixed paths in the live tree | **No** — but **2 of 12 concurrent `lint-imports` runs printed a false BROKEN** naming the planted modules | The loudest architectural gate can flake red against modules that do not exist; `.gitignore` has no `_firewall*`, so a SIGKILLed run leaves a committable `import engine`. Also blocks `pytest -n auto` forever (which C-48 wants) | C/E2; and it is a *lovely* B11 anecdote about gates that test themselves | S · **RR-free** |
| **C-35** root conftest pins **1 of 43** `AILIBI_*` variables | **No** — until a visitor's shell has one set. A realistic 13-var env → **10 failed** | Pairs with **C-126** (the knobs are documented in no `.md`) and **B1** (the one that *is* printed is undocumented). `AILIBI_MAX_COST_USD=0.001` alone breaks `test_balance_eval.py` | C/X1 reproduction; C/E1 "the front-door claims reproduce offline" | S · **RR-free** |
| **C-36** eight reimplementations of the tick+meeting loop | **Indirectly — as G-37** | see G-37; the −1 frame disagreement between the two canonical walkers is asserted by no test | onboarding cost (C/B4, C/B12) | M · **RR-free** |
| **C-42/C-43/C-46/C-48** perf: fresh Jinja env per game (**1.20×**, replay SHA identical); `recent()` Θ(T²) (**1.28×**, replay SHA identical); serial tournament (**4.98×** at 8 procs); 338 s default test tier | **No** | Both big wins are **verified byte-identical**, so they are safe inside any phase. They do **not** shorten the ~23 h re-record (that is LLM-bound and `refresh_samples.sh` already pools workers) — they cut CI, the eval harness and ES rollouts | C/X1 ("the three commands work in seconds" is the best thing the project has) | S each · **RR-free** |
| **C-44/C-45/C-47** the eval report is a second copy of the corpus (**47 MB/100 games, 584 MB peak RSS**); `.git` is **190 MB** because two *regenerable* JSON aggregates are tracked; the frontend downloads then discards **75–81 %** | **Yes, as friction** | C-45 is the mechanical cause of the README's ~150-word `--filter=blob:none` clone caveat that C/B8 wants deleted and C/A3 calls the barrier ("every reader must clone ~256 MiB"). `.gitignore:23` already ignores the *top-level* aggregate — the pattern was never extended to the per-set dirs | C/A3, C/B8, C/X1 | S (ignore) / M (history) · **RR-free** |
| **C-62/C-63/C-64/C-66** four God modules = 44 % of non-test Python; 33 % of non-test Python is prose with **1 896 `Task N.M`** refs; 10 accept-and-ignore resolvers + 152 test lines for retired levers; the belief fold welded into `meetings/manager.py` | **No** | This is C/B7 verbatim ("`meetings/manager.py` 3 989 lines will be asked about") and C/D9's volume ruling, arrived at independently from the code side. Mitigating and worth keeping: **43 of 44** cited `audits/`/`tasks/` paths resolve on disk | C/B7, C/D9, C/D7 | M–L · **RR-free** |
| **C-74** 917 lines of Bash as an application runtime on the money path, **zero real coverage** (`AILIBI_LLM_PROVIDER=fake` is remapped to `anthropic`; 59 tests are all `--dry-run` echo assertions) | **No** | **This is the re-record path.** If the owner takes Option A, ~23 h of operator wall time and the project's canonical baseline ride on an untested worker pool with a hand-rolled mkdir mutex and dead-owner detection | directly gates the substrate phase | M · **RR-free** (and it *protects* the RR) |
| **C-75** production shape dictated by test doubles (three near-identical `run_tournament_eval` branches) | **No** | the kind of thing a senior reviewer notices in 30 seconds, with the comment saying so | C/P1 | S · **RR-free** |
| **C-96** the documented evidence-restore and the documented gate are mutually exclusive (`ruff` honours `.gitignore`, `mypy` does not) | **Yes** — a visitor following two documented steps gets a spurious red | one-line fix (extend the mypy exclude regex); it is an *open audit item* (F1's mypy facet) | C/X1; C/B9 | S · **RR-free** |
| **C-97** `ruff check` at stock defaults; **1 431** findings in the standard families; the declared `line-length = 88` is unenforced | **No** | "Architecture is enforced by tooling" is true for the four contracts and false for lint | C/E2, C/B9 | S (select) + M (fix) · **RR-free** |
| **C-113** `vote_correctness_rate`: docstring says "structurally pinned to 1.0 … any value below 1.0 is a detector/recording bug to chase"; the committed 9p2i report reads **0.923** (6 legitimate zero-flag impostor ejections); the README sells it as the circularity guard | **No** — but a *researcher* would (P2 re-derived neighbouring numbers by hand in 20 lines) | The one place where a README claim and a committed number disagree in a repo whose whole thesis is that they never do | **README:190**; C/A6, C/B9. Highest embarrassment-per-line in the review | S · **RR-free** |

---

## 4. §C — Contradictions and tensions between tracks, with rulings

**T1 — B praises the prompt-byte golden; B also names byte-identity as a root cause freezing legibility bugs.**
`B/§7.8` calls `test_prompt_byte_golden.py` *"the single most valuable test in the repo"* (it re-runs the real
`MeetingManager` over 204 committed meetings and ships a one-byte perturbation test: *"a golden that cannot fail
is not a gate"*); `B/§8` then names byte-identity doctrine as the tax that freezes C-10, C-15, C-29, C-73 — and
A's entire idea list (39 of 43 items) inherits it.
**Ruling: not a contradiction — a scope error, and B is right about the fix.** The golden is a *test* artefact;
the baseline is a *measurement* artefact; today one word of prompt copy (G-27) is blocked behind both. Add the
render-version stamp B proposes so goldens re-key automatically, and keep the honest half of the doctrine:
**any render or prompt change still needs the re-record before the baseline can move** — which is precisely why
the standing cadence rule says *one combined re-record*. Practical consequence: **batch every RR item in this
map into one wave**; ship every RR-free item now.

**T2 — C wants less process volume; B says the process tree is why the code is auditable.**
C/D9 rules the volume problem is navigation, not deletion; C/A1 evicts 846 words of ledger from the README.
B/§7.30 verifies **43 of 44** cited `audits/`/`tasks/` paths resolve on disk ("maintained, not rotted") — *and*
B/C-63 files 33 % prose / 1 896 `Task N.M` refs as **P1**, raised by **all 16** reviewers.
**Ruling: three different artefacts, three different verdicts.** (a) The `audits/` tree — **keep**, index it
(C/B12, `audits/README.md`); it is a genuine asset and B proved the citations are live. (b) In-code narration —
**trim** (C-63): lead with intent, push provenance to the end (C/B7 says the same thing about
`observation/service.py:31–83`). (c) The README — **evict** (C/A1). The word "volume" was doing three jobs.

**T3 — B judges the ML program sound; C/P2 calls the apparatus-to-result ratio theatre.**
B verified `verify_ml_evidence.py` re-derives 54 headline numbers from frozen weights with 0 failures in 20 s,
that the negative results survive a 100× epoch / 300× lr sweep, and that the anti-leakage discipline (split by
game, fold validator, label-poisoning fence) is above most published work (B/§7.27–28). P2 reads
"~29k LOC training + 26k tests + 17k experiments around a 19-weight champion" as theatre and the flip bar as
"close to unpassable by construction".
**Ruling: both hold, and B independently *supports* P2 on two axes it did not know about** — **C-69**
(`training/` PROD closure = **0 modules, 0 LOC**; training+experiments = **39.8 %** of non-test Python) and
**C-94** (the `(1+λ)` hill-climber is documented as an "evolution strategy": no antithetic sampling, no rank
normalisation, no step-size adaptation). The *rigor* is real and verified; the *proportion* and one *name* are
the critique. Do C/A6's `docs/ml-program.md` in research shape, retitle the optimiser honestly (C-94 — a
research reader will spot it exactly as P2 did), and put P2's sharper line — *"strong on measurement, weak on
knowing when to stop building measurement"* — in C/B11 as an owned lesson.

**T4 — A says fix the substrate; C says nobody will ever see it; the owner's open decision is exactly this.**
**Ruling: they are not competing for the same resource, and the map says do C's front door *first* — as a
pre-wave, not as "the presentation phase".** C/A1–A5 are hours-to-a-day, $0, no re-record, no gameplay risk,
and they unblock the audience for everything that follows. The substrate wave is weeks of contract work plus a
~23 h record. Two additional facts from this map that the owner's §4 framing did not have: (i) the substrate
phase's own instrument is at HEAD and costs $0, so **measurement can start before the record**; (ii) **C-74**
means the record itself runs on 917 lines of untested Bash — harden that first or the 23 h is at risk. And
`audit-phase-19-close.md` §4.2's four scope items map exactly onto findings all three tracks reached
independently: *sighting provenance* = **G-2/G-4/G-9a ↔ C-11**; *content-vs-own-memory validation* =
**G-1 ↔ (no code finding, by construction)**; *interval/weighting honesty* = **G-2's single-tick windows,
G-36 ↔ C-29**; *flag naming* = **G-2 ↔ C-129**. The convergence is the strongest evidence in this document
that Option A is correctly scoped.

**T5 — A's G-6 ("bodies invisible, never mentioned") vs A's own verdict (correct fog-of-war) vs the UX pass
("the map shows FOUR corpses when the engine has one").**
**Ruling: the engine is right and the frontend is wrong.** G-6 is **REFUTED as an engine defect** (0 real
misses; `discovered_by=None` is what makes a body *visible*; meetings are non-spatial so nobody stands over a
corpse ignoring it). The corpse defect worth fixing is **C-7**, on 67 % of committed frames. This is the
cleanest case in the review of one track's symptom being explained by a *different layer* than it assumed.

**T6 — A calls `alibi_vs_sighting` a design-hole; A's verifier calls it a twice-ratified design choice; B calls
it a P1 code defect contradicting the module's own doctrine.**
**Ruling: all three, at different layers, and the fix needs no design re-litigation.** The *gate crossing* is a
ratified owner decision (`tasks/phase-13.md:700` LONE-STRONG, over an audit that blocked it). The *ungrounded
provenance* is unruled: `transcript.py:105` (restated at `:150`, `:3276`) declares *"A STRONG flag naming a
CREWMATE is a false positive"* while the code mints 53 of them. Ground the prosecutorial side the way
`vent_sighting` and the `SightingRecord` vouch channel already are, and the ratified gate keeps its meaning.

**T7 — the project's docs are more honest than its prompts.**
`docs/reading-guide.md:196` already tells the reader the flag doctrine convicts innocents, with the 40 % figure
and the `vote_ballot.j2:100` line number. The prompt still says "VERIFIED evidence" to 2 543/2 543 voters.
**Ruling: this is the highest-leverage portfolio fix in the review.** Every persona rated the honesty culture
the project's best trait (C/E5); shipping the fix turns the disclosed caveat into a *result* and lets the
reading guide say "found, measured, fixed, re-measured" — which is the strongest possible version of C/A6.

**T8 — G-14 files crew same-room-only vision as P1; all three A ideation lenses independently rule "do NOT
change it"; B finds the map file still documents the opposite.**
**Ruling: keep the mechanic, fix the doc (C-115: `canonical_1.yaml:52-58` still declares
`base: same_room_and_adjacent` "uniform across the map"), take the one narrow repair all three lenses
converged on — adjacent-room **bodies** only, never players.** A doc-vs-code split on the game's most
counter-intuitive rule is exactly what a senior reviewer probes, and the doc fix is RR-free.

**T9 — B praises determinism at length; A finds a 100 % seat lottery.**
**Ruling: no conflict — determinism is not fairness, and `DESIGN.md:334` already says so and names per-seat
fairness as its own open item.** Two things follow: any published per-seat metric must control for it, and
**C-95** should be fixed alongside (the code advertises a `type`/payload tie-break that can never fire, while
the real tie-break — actor id — decides 156 kills, every contested witness set (C-22), and 168 declined kills
(C-3)).

**T10 — "no P0" (B) vs "eight P0s" (A).**
**Ruling: different ontologies, and the difference is the headline.** B's P0 = correctness/security/data-loss;
A's P0 = breaks believability of the core loop. Every A P0 is a *product* defect over *correct* code. Say this
out loud in the portfolio: it is a mature engineering observation, and it explains why 4 600 passing tests and
a 19-phase audit trail did not catch a game in which 20 % of crew testimony is invented.

**T11 — C wants the demo hosted now; B and the UX pass found what would ship with it.**
**Ruling: A3 gets a pre-flight, and it is the highest-leverage bundle in the review** — all RR-free, ~1 day:
**C-7** (phantom corpses, 67 % of frames) · **C-9** (focus trap in the tour) · **G-41/C-track B6** (strip
`(DESIGN.md §11.3)` / `Task 9.6` / `56/100 MED · INTERNAL HEURISTIC` from product copy; expand "4p1i/9p2i";
legend the R1/R2/R3/R7 bars) · the dock height (map hidden below ~800 px) · the Tournament tab's raw 404 dump ·
the bundle README's baked `/Users/danielkeinan/…` path. Then re-record the GIF (C/A3) against a fixed map.

**T12 — a minor inter-report contradiction inside A, for the record.**
`w2` claimed rejected actions are not recorded in the JSONL; s1/s2/w1/w4/w5/w6 all read attempted actions out
of the same `kind=tick` `actions` array, and the G-10 verifier re-derived 1 003 rejected moves and 188 whiffed
kills from it. **Ruling: the majority reading is correct; w2's dependent per-game conclusions should be
re-checked before any of them is cited.**

---

## 5. §D — The eight root causes, with their full rosters

Ordered by total findings generated across the three tracks.

### RC1 — The agent has no record of *itself*
No dated self-location line (the store keeps `own_room_by_tick` and uses it only to scope others' sightings);
the one self-placing line is mis-dated by two ticks; no ejection outcome, no meeting verdict, no revealed role,
no absence, nothing persisted from the last meeting.
**Gameplay:** G-1, G-3 (second-order), G-21, G-22, G-23, G-35, G-30, part of G-9a.
**Code:** C-10 (`last_seen` fed only from `saw_player_move`, so the belief line contradicts the observation
list in the same prompt), C-71 (`WorkingMemory` is scaffolding + a cache written by the renderer), C-72
(`trust` never written; `record_contradiction` never persists — 0/1 656 renders), C-73 (testimony sheds first),
C-117 (DESIGN §6 drift ×5), C-29.
**Portfolio:** falsifies **README:78** ("typed event log and a derived belief state (suspicion, trust,
alibi)"); the researcher lens' *0/7 458 prompts record any prior ejection*.
**Ideas that close it:** A/F-1, F-9, F-10, F-11, F-12; R2/R4/R5; V1/V8.

### RC2 — Unverified speech is stamped VERIFIED; provenance is checked on the exculpatory side only
**Gameplay:** G-2, G-4, G-9a, G-19, G-31, G-32, G-36; and it is the mechanism behind 70/79 (A) and 20/25 (B)
wrongful ejections — two independent censuses, different denominators, same conclusion.
**Code:** C-11 (P1, "very high" confidence, anti-informative at 11.7 % vs a 26.1 % base rate), C-129
(prompt vs `schemas.py` in-repo contradiction), C-15 (band is an in-band substring), C-19 (STRONG bar == the
impostor count), C-120 (whereabouts-anchored ids never resolve a frontend badge — **61/404** event ids).
**Portfolio:** reading-guide §3 limit 1 (already disclosed); `audit-phase-19-close.md` §4.2 scope item 1;
C/A6.
**Ideas:** A/F-2, F-3, F-13, F-27; R1/R7/R12; V7.

### RC3 — A false invariant in the memory store, broken two phases later by a map-config flip
`"the owned set only ever shrinks"` + `dead_task_rule: redistribute` + lexicographic `pending_task_id`
selection + a `role == "CREWMATE"` gate.
**Gameplay:** G-3 (10 %/23 % of completion lines false, 159/300 games, 3 STRONG flags minted against
innocents), G-16 (485 progress reversals, the body-beacon conveyor), part of G-22.
**Code:** C-2 (P1, borderline P0 for evidence integrity), C-24 (an instantaneous kill side-channel on the
self channel, 13/16 kills), C-119, C-115 (DESIGN documents only the retired rule).
**Portfolio:** the best bug story in the repo; C/B11.
**Ideas:** A/F-22.

### RC4 — Lexicographic actor id is load-bearing at three layers and documented at none of the surfaces that consume it
**Gameplay:** G-10 (156/156 escapes / 90/90 deaths; per-seat 24.7 % → 0 %), G-11, G-18, part of G-13.
**Code:** C-22 (witness membership), **C-3** (the *same* `(-score, player_id)` tie-break declines
**190/415 = 45.8 %** of free kills; 168/168 on exact 1.0 ties), C-4, C-95 (a tie-break that can never fire),
C-18, C-25.
**Portfolio:** determinism-vs-fairness; and C-3 re-frames the project's own long-running "the impostor never
wins" narrative as partly a target-selection bug measured on a hobbled inner loop.
**Ideas:** A/F-14, F-17, F-19; V4/V9.

### RC5 — The private dialect leaks to every surface
One habit; five surfaces; every C persona flagged it and every A watcher tripped on it.
**Gameplay:** G-25 (12.6 % of prompts carry a dev marker inside quoted dialogue), G-26, G-29
("0.60 threshold" ×208), G-41 (task numbers in UI tooltips).
**Code:** C-67 (nine marker literals, parsed by four packages, `]`-terminator load-bearing), C-15, C-63
(1 896 `Task N.M` refs in source), C-129 (`autoescape=False`, no `max_length`), C-121 (runtime HTTP messages
embed task numbers).
**Portfolio:** C/A2 (6/11 glossary terms undefined in the README + ≥15 defined nowhere; conventions named
after task numbers), C/B6 (UI copy), C/B7 (source comments).
**Ideas:** A/F-35, F-37, F-38.

### RC6 — "Preserve the exact prior bytes" applied beyond its remit
B's own §8 root cause, extended by this map.
**Code:** C-64 (10 accept-and-ignore resolvers, 13 `ENV_*` constants, 152 test lines), C-104 (~70 tautology
assertions whose docstrings say the opposite of what they test), C-37 (the walker consolidation froze seven
validation semantics into a 13-flag matrix, 0–10 checks per profile), C-130 (a version-bumped template with
**0 of 7 932** calls; the *default* prompt set used by no replay), C-102 (tests pin source text and
signatures), and the tax on C-10/C-15/C-29/C-73.
**Gameplay:** G-27 — a one-word wording fix blocked behind a template version cascade *and* a re-record.
**Fix:** the render-version stamp (T1) plus one deletion pass; C/B11 material about when a preservation rule
stops paying.

### RC7 — Gates validate shape, not entitlement — and several validate nothing
**Code:** C-31 (leak scanner cannot recompute visibility; M6 survives all four suites), C-32 (import-linter
covers 89 of 383 files), C-6 (the corpus validity gate accepts truncation), C-103 (three tally tests pass on a
4×SKIP tally), C-104, C-102, C-113 (a metric documented as "structurally pinned to 1.0" reading 0.923),
C-40 (Hypothesis unconfigured *and* its sweeps never move anyone — all spawn CAFETERIA, so visibility coverage
is vacuous), C-112 (the named coverage gaps), C-34 (the gate that flakes red).
**Gameplay:** G-20 (the SKIP-plurality rule that decides outcomes is the least-tested rule in the meeting).
**Portfolio:** every one of these sits under **C/E2** ("architecture enforced by tooling, and it is real") and
under README:74. **C/B9 already asks for the rewrite without knowing the mechanism** — this root cause hands it
the receipts. Note the honest counterweight B insisted on: the plant-detect-cleanup pattern, the one-byte
perturbation golden and `check_doc_facts.py` are the *right* instinct; the failures are location and scope,
not culture.

### RC8 — The spectator surface derives from the wrong source, and is the least-tested layer in the repo
**Gameplay:** G-38 (bodies + four mis-projected action classes), G-41, G-6's misread.
**Code:** C-7 (67 % of frames), C-80 (the derivations live in `.tsx` the node-only vitest project cannot
import — *"which is why C-7 went unnoticed"*), C-101 (zero component render tests; test:prod **0.15** vs
1.6–2.8), C-120 (61/404 badge ids never resolve), C-8, C-9, C-58, C-79, C-89, C-90.
**Portfolio:** C/A3 + C/E3 — the demo is the star-making asset and the thing five of six personas said would
decide the star. **This is the only root cause that is entirely RR-free.**

---

## 6. §E — What the map says about the open owner decision

The close audit recommends substrate-then-presentation. The cross-track evidence **confirms the ordering of
the two phases and inserts a third thing before both**, because it is neither:

| slot | content | why here | cost |
|---|---|---|---|
| **0. Front-door pre-wave** (1–2 days, $0) | C/A4 (About/topics/badge/byline, 5 min) · C/A1+A2+A5 in one README PR · the **A3 pre-flight bundle** (C-7, C-9, jargon copy, dock, Tournament 404, bundle README path) then Pages + GIF · **C-113** (the one README number that disagrees with committed data) · **C-96**, **B1/C-83/C-126/C-130**, **C-5**, **C-35** (the four things a stranger hits in the first ten minutes) | None of it needs a re-record, none of it risks the baseline, and all of it is upstream of *whether anyone reads the rest*. Five of six personas would not star today | S |
| **0b. Claim-integrity pass** (2–3 days, $0) | **C-31**, **C-32**, **C-6**, **C-34**, **C-1** | These are the receipts under C/E2 and README:74 — the claims the project is most proud of. Fix them before writing a results page that repeats them (C/A6) | S–M |
| **1. Evidence-honesty substrate phase** (Option A) | audit §4.2's four scope items, each now with a cross-track finding roster: provenance (**G-2/G-4/G-9a ↔ C-11**), content-vs-own-memory (**G-1**, plus **C-2/G-3** which is the same class and is a *bug*), interval/weighting (**G-2, G-36 ↔ C-29**), flag naming (**G-27, G-29 ↔ C-129**). Ride along, same re-record: G-23, G-25, G-34, G-35, G-22 | The 19.14 cells already locate the damage (non-direct accuracy 0.368, all 79 innocent ejections in that cell) and the instrument is at HEAD at $0 | L · **RR** |
| **1-pre.** | **C-74** (harden the 917-line recording script) and **C-3/C-4** decision | The record runs on untested Bash. And C-3 must be *decided* before the record: fixing it changes impostor behaviour, so it either rides this record or waits for the next one | M |
| **2. Presentation phase** | C/A6 results page, `docs/ml-program.md`, C/B3/B4/B5/B11/B12, the G-38 action projection (+ **C-8**, which it escalates) | Now multiplying quality that exists, and able to say "found, measured, fixed, re-measured" about RC2 | M |

One sequencing hazard worth naming: **the G-38 DTO fix bumps `viewModelVersion`, which turns C-8 from latent
to live.** Do them in the same PR.

---

## 7. §F — Re-record ledger

| needs the ~23 h re-record before the baseline moves | ships now, every gate green |
|---|---|
| G-1, G-2, G-3, G-4, G-5, G-7, G-8, G-9, G-10, G-12, G-13, G-15, G-16, G-17, G-18, G-22, G-23, G-25, G-27, G-29, G-34, G-35, G-36, G-40 · C-2, C-11, C-29, C-129 · every A idea except F-41/F-42 | G-38+C-7 (frontend), G-41/C-track B6 (copy), C-1, C-5, C-6, C-8, C-9, C-12, C-13, C-14, C-31, C-32, C-33, C-34, C-35, C-42, C-43, C-44, C-45, C-46, C-47, C-48, C-58, C-62…C-66, C-74, C-75, C-79, C-89, C-90, C-96, C-97, C-101, C-113, C-115…C-128 · **all of C/A1–A6, B1–B13** |
| *Note:* C-42 (1.20×) and C-43 (1.28×) are **verified replay-SHA-identical** and can ship on either side; they do **not** shorten the re-record (LLM-bound; `refresh_samples.sh` already pools workers) | |

---

## 8. The five sentences that carry this map

1. **The code is right and the game is wrong** — B found no P0, A found eight, and every one of A's is a
   faithful implementation of a rule nobody would have written after watching it (T10).
2. **One channel decides the game and it is anti-informative** — `alibi_vs_sighting` is 14.6 % precise as sole
   evidence, names an impostor less than half as often as chance, is labelled "VERIFIED evidence" to
   2 543/2 543 voters, and drives 70 of 79 wrongful ejections; the fix (ground the prosecution side the way the
   defence side already is) is already scoped by the project's own close audit (RC2, T6).
3. **A one-line comment, a config flip and a test that enshrined the wrong behaviour** put fabricated first-hand
   memories into 159 of 300 committed games, one-sidedly against the crew (RC3).
4. **The demo is the star-making asset and the least-tested layer** — 67 % of map frames paint corpses the
   engine deleted, on the surface five of six hiring personas said would decide the star, in a codebase with a
   test:prod ratio of 0.15 there and 1.6–2.8 everywhere else (RC8, T11).
5. **The project's docs are already more honest than its prompts and its gates** — reading-guide §3 discloses
   the flag doctrine's injustice, while the prompt still says VERIFIED and the leak scanner cannot check
   entitlement. Closing that gap converts the project's best trait from a caveat into a result (T7, RC7).
