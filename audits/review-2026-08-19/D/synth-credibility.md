# D — Credibility / risk synthesis across tracks A (gameplay), B (code), C (portfolio)

Sources read in full: `A/collated-findings.md` (G-1…G-41), `A/verdicts.md` (12 adversarial re-derivations),
`A/ux-visual-pass-lead.md`, `B/collated-findings.md` (C-1…C-130, §7 strengths, §8 root causes),
`B/verdicts.md` (14 adversarial re-derivations), `C/collated-portfolio.md` (A1–A6, B1–B13, D1–D9, E, F),
`C/x1-front-door-reproduction.md`, `C/p2-ml-research-lead.md`. Spot-checks against the repo at `main b809b19c`
are marked **[D-VERIFIED]**; everything else carries its source id.

The question this file answers: **what, left as is, would embarrass this project in front of a careful reader,
and how do the three blind tracks compound?**

---

## 0. The one-paragraph answer

The front door does not lie. Every reproducible claim above the fold reproduces in under ten seconds
(X1 §1, six personas independently), and `docs/reading-guide.md` §3 already volunteers more damaging facts
about the corpus than a hostile reviewer would find in an hour — the flag doctrine convicting innocents, the
5% diagnostic husks, the 21.3% engine-rejected kill submissions, the roll-call role tell, "general social
deduction: NOT demonstrated". That disclosure discipline is the project's single biggest credibility asset and
it holds under adversarial re-derivation from both other tracks. The exposure is not in what the docs admit;
it is in **four undisclosed items that contradict the project's own stated pillars** (fabricated first-hand
memory; a firewall gate that cannot see the axis it advertises; a `trust` channel named in the ADR that has
zero writers; an ML comparator with two measured target-selection defects), plus **a demo surface that visibly
malfunctions on 67% of frames** — and the presentation phase's first act is to make that demo public.

---

## 1. Claim-by-claim grading of the front door

Grades: **HOLDS** · **HOLDS-WITH-CAVEAT** (true as stated, but a named qualification is missing) ·
**UNDERMINED** (a careful reader can falsify the sentence as written).

### 1.1 "Tick-based deterministic engine… bit-exact replays" (ADR-0001 #1, README:96, scopes 1–2) — **HOLDS**

The strongest claim in the repo, and the only one three independent tracks all tried and failed to break.
Track B re-derived byte-identical per-tick hash chains across 3 seeds × 400 ticks under two `PYTHONHASHSEED`
values, run-twice byte-identical replay *and* audit JSONL, a 300-game / 28,362-tick fuzz with 0 violations
across 12 structural invariants, and `verify_samples.sh` 100/100 in 3.14 s (B §2 "determinism claims that HELD",
B §7 items 1–3). Track A's corpus sweeps add an independent, *gameplay-level* integrity audit that nobody
claims anywhere: 0 non-adjacent moves in 16,453 room changes; 188/188 kill rejections fully explained with
**0 unexplained**; 0 bodies without a kill event; 0 double reports in 626; 0 dangling citation ids in 3,814
ballots (A §E, re-derived in A/verdicts G-10). Track C's personas ran it and it worked (E1).

Caveats that do **not** cost the grade but should be stated once: `eval/validity.py:518` accepts a
tail-truncated corpus game as a legitimate `TICK_BUDGET` outcome with every state hash still verifying
(C-6, verdict CONFIRMED at P1 for that site) — i.e. the acceptance gate for *new* corpus bytes has a hole the
committed corpus does not. And scope 3 may be **under-claimed** — see §3.4.

### 1.2 "Observation firewall… zero observation-firewall violations" (README:47, ADR #1) — **HOLDS-WITH-CAVEAT**

The boundary itself is genuinely good: one privileged object, engine-free frozen `extra="forbid"` schemas,
witness gates that read only *resolved* engine events, and a 16-mutation probe confirming every classic channel
bites (B §7 item 4). Enforcement is three-way, not one (B §7 item 5). No live leak exists on `main` — every
reviewer says so explicitly.

The caveat is that the sentence's three supports each have a measured blind spot:

- **C-31 (CONFIRMED, P1):** `assert_packet_is_leak_clean(packet, events)` receives no `WorldState` and no
  `VisibilityResult`, so it structurally cannot check *entitlement*. Mutation M6 — every undiscovered body
  visible to everyone — takes `body_views 33 → 249`, `cross_room_body_views 7 → 222`, and passes **all four
  suites**; the whole-suite diff is empty. `DESIGN.md:933` calls this "the most important test", and the ML
  champion gate runs exactly it (`training/crew/scorer.py:1735`, `training/bakeoff/harness.py:1828`).
- **C-32 (CONFIRMED, P1):** `orchestrator`/`api`/`eval` are not import-linter `root_packages`, so a planted
  `agents/_probe_orch.py` importing `orchestrator.game` reports `4 kept, 0 broken` and `check.sh` is fully
  green. README:74's "directly or transitively (import-linter enforced)" is true only for hops via the six
  roots. Coverage: 89 of 383 tracked `.py`.
- **C-34 (CONFIRMED, P1):** `tests/test_firewall.py` plants five files at fixed paths inside the live
  checkout; 2 of 12 concurrent `lint-imports` runs printed **false BROKEN** naming those modules, and
  `.gitignore` has no `_firewall*` pattern, so a killed run leaves a committable file containing `import engine`.
- **C-24 (P2, unruled):** `dead_task_rule: redistribute` hands the lowest-id living crewmate, from anywhere on
  the map, on the kill tick, the fact that someone died and which task they held (13/16 kills across 4 games).
  The leak suite **blesses** it by asserting `owned_task_ids == engine truth`. On any plain reading this is an
  information channel from hidden state to an agent; it is not disclosed anywhere.
- **C-23 (P2):** the observer's own move rides `moved_players` for impostors only — a role-correlated packet
  shape, papered over twice downstream.

Nothing here is a live leak. But "zero violations" is an absolute, and a careful reader who tries the obvious
falsification (plant an import; mutate visibility) finds the gate silent both times. X1's GOOD-11 wording fix is
the right one and costs a sentence.

### 1.3 "Memory is structured first… a derived belief state (suspicion, trust, alibi)" (README:100, ADR #3) — **UNDERMINED as worded**

This is the pillar with the worst evidence-to-claim ratio, and all three tracks land on it independently.

- **`trust` is dead.** [D-VERIFIED] `adjust_trust` (`agents/memory/beliefs.py:1111`) has **zero non-test
  callers** repo-wide; `trust` is always `_DEFAULT_TRUST`. C-72 measured `trust` lines rendered in **0 of 1,656**
  replay renders, and `## Open contradictions` likewise 0/1,656, while `DESIGN.md §6.6` still shows both as
  canonical. The ADR the README calls "recorded verbatim" names "trust scores" as one of three components of the
  belief state. A reader greps `adjust_trust` and gets seven test hits and one definition.
- **The typed log renders facts that never happened.** C-2/G-3 (both CONFIRMED, independently, with repros):
  `redistribute` grows `owned_task_ids` at the kill tick, `store.py:1157-1200` infers a completion from any
  `pending_task_id` change under the comment *"the owned set only ever shrinks"*, and the agent is shown a
  citable, id-stamped `[tick N] You completed <task> (you were in ROOM)` for work it never did. Rate over the
  committed corpus: **53/529 (10.0%) 9p2i samples, 15/65 (23.1%) 4p1i, 140/1,528 ml/9p2i**, hit in **159 of 300
  games**, **spoken at the table 67 times**, and three of them minted STRONG contradiction flags against
  innocents (s11 p-6, s46 p-1, s13 p-5). Redistribution correlation is **100%** (58 kills + 7 ejections at T−1/T−2).
- **The belief line contradicts the observation list in the same prompt.** C-10 (P1): `last_seen` is fed only
  from `saw_player_move` rows, so a prompt can carry `obs: saw p-3 in STORAGE @20` beside
  `p-3: … (last seen in ADMIN at tick 5)`.
- **The structure the agent most needs is absent.** G-1 (verdict: mechanism CONFIRMED, attribution corrected):
  no dated self-position line exists in 971 rendered memories — the only self-placing shape is the
  completed-task suffix, which is itself mis-dated (matches the agent's real room at tick N **16.0%** of the
  time, at N−1 97.0%). Crew answer the mandated roll-call falsely **20.5%** of the time; 44.3% of the 79 crew
  ejections trace to the victim's own false self-placement (the claimed 73% was inflated; 21.5% are the
  opposite bug — a truthful victim killed by a witness's mis-dated sighting).
- **Two thirds of the block is noise.** G-34: 66.1% bare co-presence/movement, hard evidence 1.54%, **49.8% of
  snapshots contain zero hard-evidence line**, and under budget pressure the render sheds prior-meeting
  testimony 365/456 times while keeping the 8 constant tick-0 lobby lines (C-73 measures the same shedding from
  the code side: reported rows kept **0 of 4,150** at >150 candidates).
- **The scaffolding is honest about itself in comments but not in the ADR.** C-71: `WorkingMemory.goal`/`path`
  have zero production writers; `last_seen` is written *by the renderer* to satisfy an audit gate.

Grade rationale: the sentence "typed event log + derived belief state" is defensible; the parenthetical
"(suspicion, trust, alibi)" and the ADR's "trust scores" are falsifiable in one grep, and the log's contents are
provably fabricated at a measured 9–23% rate on the completion channel. Cheapest honest repair is a word
(§4 item 5) and a disclosed known-issue; the real repair needs a re-record.

### 1.4 "Evidence-processing: demonstrated — 520/520 eject ballots carry a valid citation" — **HOLDS-WITH-CAVEAT**

The number is real and Track A re-derived the class independently: 0 dangling observation ids, 0 mis-owned ids,
0 dangling turn ids in 3,814 ballots, 0 self-votes, 0 dead targets (A §E). Citation *hygiene* is perfect.

The caveat is that "valid" means **resolvable**, not **supported**, and three findings show the difference is
load-bearing:

- G-9's seed-12 case: p-9's ballot cites `reason_obs=p-9:3:2` — and that observation line
  (`You saw p-3 move from MEDBAY to LABS`) **refutes** the flag the ballot is voting on. The citation gate is
  satisfied by the evidence that contradicts the vote. 38/313 `alibi_vs_sighting` flags (12.1%) are this exact
  shape and **38/38** have a truthful memory line re-spoken as a false placement; 10 meetings ejected the
  innocent it framed.
- G-2's grounding pass: of 170 resolvable sighting-sides, **63.5% were never perceived by that speaker at that
  tick** (28.8% not even ±2 ticks). The id resolves; the perception never happened.
- C-11 (CONFIRMED, very high confidence): `detect_contradictions` has no `sighting_records` parameter — it
  *cannot* ground the prosecutorial channel, while the identical grounding machinery is wired to the
  exculpatory vouch. STRONG `alibi_vs_sighting` names a crewmate **53/60 = 88%**; it names an impostor at
  **0.117** against a base rate of **0.261** — less than half of random, binomial p=0.0048.

Add the "VERIFIED evidence" wording, which is the sharpest single sentence a hostile reader can quote:
`vote_ballot.j2:100` — *"Each flag below is VERIFIED evidence… never side with an unverified
counter-accusation over a verified flag"* — present in **2,543/2,543** recorded ballot prompts, sitting over a
detector whose sole-convicting precision is **12 right / 70 wrong = 14.6%** while its engine-grounded sibling
`vent_sighting` is **310/316**. `meetings/schemas.py:426` says the opposite in the same repo ("Flags are
information, not verdicts").

Mitigating, and it matters: the reading guide **already discloses** this ("labeled 'VERIFIED evidence'…40% of
directional flag subjects in 9p2i are innocents"). The residual exposure is (a) the product surface still says
"verified" with no qualification, and (b) the precision number the guide gives (40% innocent subjects) is
gentler than the measured one (85% of sole-flag ejections wrong).

### 1.5 "Deception: demonstrated, and the strongest capability on display" — **HOLDS-WITH-CAVEAT**

Real deception is present and Track A saw it repeatedly: impostors manufacture sightings that mint "VERIFIED"
flags against innocents in **15.1%** of `alibi_vs_sighting` flags (17 of 53 crew-naming STRONG flags), seed 17
being the flagship case. The guide's own guard on the 0/245 partner votes is correct and well-stated.

Four qualifications no doc carries:

- **The demonstrated deception rides on the defect.** The impostor's most effective weapon is exactly the
  ungrounded-sighting channel of §1.4. Fixing C-11 will *reduce* the measured deception. Presentation-first
  would publish "deception demonstrated" as a capability at the moment the substrate phase is about to remove
  its main mechanism — a compounding risk only visible because A and B were run blind and agreed.
- **Half the deception is prompt-manufactured.** G-22: the impostor persona says "explain nothing about your own
  whereabouts", so **P(impostor | turn has no whereabouts) = 97.7–100%**. Disclosed in guide §3 as a behavioral
  tell — good — but it means the crew's failure to catch impostors coexists with a trivially learnable role
  classifier in the transcript.
- **The genre's signature bluffs are never used.** 0/626 self-reports, 0/707 meeting calls by an impostor;
  `impostor_report.qwen3_6_27b.v3` is a pinned, version-bumped template with **0 calls out of 7,932** meeting
  LLM calls (G-22/G-33, corrob 6 — not independently re-derived in A/verdicts, so mark medium confidence).
- **15.6–15.9% of impostor ballots confess the role in plain text** on the spectator surface (G-28):
  *"I am the impostor. Voting is suicide."* Harmless to gameplay, fatal to a demo viewer's suspension of disbelief.

### 1.6 "General social deduction: NOT demonstrated" — **HOLDS, and is under-stated**

The most credible sentence in the repo, and every track strengthens it. P2 reproduced the 68/2 vs 10/21
cross-tab from a committed JSON in 20 lines of stdlib. Track A raises it from "87% ride a vent" to a mechanism:
**"did any contradiction flag fire" predicts the meeting outcome 88.5–100%** of the time (G-19); `vent_sighting`
drives 71% of all ejections (G-13); spoken accusation confidence in the 0.6–0.8 band converts *below* the ~25–29%
random baseline (G-19/G-30); the vote-time conviction lift is 19.1% retained (G-21). The honest negative is
better evidenced than the README knows.

### 1.7 The ML NO-FLIP rigor — **HOLDS-WITH-CAVEAT (the method holds; one input is contaminated)**

Method: verified from three directions. C/E4 confirmed pre-registration (PR #298, 07-19) precedes measurement
(#317, 07-31) precedes ruling (#318, 08-01) in git, and that `paired_stats.py` reproduces the McNemar cells
exactly. B §7 item 27: `verify_ml_evidence.py` re-*derives* 54 headline numbers from frozen weights in 20 s
offline with 0 failures, an independent surrogate rebuild matched 46/60 and 55/60 exactly, and **the negative
result survived a 100× epoch / 300× lr sweep — the NO-GO is structural, not a hyperparameter artifact**.
B §7 item 28: split-by-game, `extra="forbid"` split validators, a fold validator, a feature set restricted to
what a live runner can reconstruct, a label-poisoning fence.

The caveat is the comparator, and it is the single most likely question from a senior ML reader:

- **C-3 (CONFIRMED, and understated):** the impostor FSM re-validates only `targets[0]`, so a free, co-located,
  zero-witness kill is skipped whenever a crewmate with a lexicographically smaller id is visible one room away.
  Measured over all 50 committed 9p2i seeds with tick + meeting state-hash verification:
  `kill_available=415, intent_kill=225, MISSED=190 (45.8%)`, of which **168 are exact 1.0 ties broken by the
  lower id**, `id_order_not_the_cause=0`. The verifier's own conclusion: *"the long-running 'impostor win rate
  too low / the meeting never decides' investigation has been measuring a hobbled inner loop."*
- **G-12 (CONFIRMED-BUG, offline policy re-run reproducing 10,335 recorded decisions with 0 mismatches):**
  `_confirmed_dead` is built only from bodies the impostor itself saw, so ejected players stay top-ranked
  targets for 30 ticks. 8–12% of impostor decisions on 9p2i; **0/100 on 4p1i**; seed 36 is a demonstrably thrown
  game. The verifier states it "silently biases the canonical 9p2i impostor-win baseline downward".

Both defects are 9p2i-only and both depress the FSM. NO-FLIP itself is the conservative ruling and is not at
risk — but the *published* headline "every learned arm keeps a real win edge over the same-seed scripted FSM
(+0.12 to +0.30)" is a comparison against a comparator now known to discard ~40% of its legal kill opportunities.
A project whose thesis is "we don't publish numbers we know are confounded" cannot leave that unstated.

Secondary: **the raw 449-game finalist slate is not in the repo** (`training/reports/_finalist_eval_raw` empty,
rows point at `/Users/…` — P2 [VERIFIED], C/B10). The derived cells reproduce; the raw evidence does not.
Plus C-78 (a `SupplyFloors` block documented as *"FROZEN HISTORICAL PIN … CANNOT be re-measured"*) and P2's
point that the referee floors carry no uncertainty though a Wilson helper exists.

### 1.8 "300+ merged agent-authored PRs — every one of them merged green through the same full gate" — **HOLDS-WITH-CAVEAT**

346 merged PRs [X1 §2 via `gh`], the count is conservative. Two documented exceptions to "the same full gate":
CI additionally runs a Playwright e2e job that `check.sh` does not (C-125), and **317 campaign-tier tests (6.4%)
are schedule-only and invisible to every PR** — a PR can break them and merge green, up to 6 days of detection
latency (C-99). Also C-96: the documented evidence-restore (`fetch_evidence.sh`) and the documented gate
(`check.sh`) are mutually exclusive at the mypy leg, because ruff honours `.gitignore` and mypy does not.
None of this makes the claim false; all of it makes it *precise*, and X1 GOOD-11's rephrasing costs one line.

The perception risk here is different and larger: **the README names no human** (A5, 4/6 personas MUST).
LICENSE says Daniel Keinan; git shows "Claude" as first-class author on 310 commits (35%); all 346 PRs show one
human author on GitHub. X2: the mechanics of authorship are more legible here than in almost any agent-built
repo, but the *narrative* is absent, "and absence gets read uncharitably".

### 1.9 The spectator as the demo asset — **HOLDS-WITH-CAVEAT (and the caveats block hosting)**

Unanimous praise: "a better LLM-agent debugging surface than most commercial agent tools ship" (P3);
"the project's best demo asset" (A ux lead). Four defects sit directly on the path a reviewer will walk:

- **C-7 (CONFIRMED, exact reproduction):** the omniscient map accumulates kill events and never reads
  `TickView.bodies`, so **1,182 of 1,769 frames (66.8%) across 50/50 committed games** paint corpses the engine
  has already consumed, styled identically to real ones; seed 2 t29 shows four corpses where the engine has one.
  Note the compounding with G-6, which *refuted* the gameplay-side version of this: bodies legitimately persist
  as findable evidence, so a viewer cannot distinguish the correct design from the frontend bug.
- The ballot **`CORRECT` badge reveals a target's role even in "outcome hidden" mode** (A ux lead) — the demo's
  one spoiler-protection feature leaks through its own badge.
- **The prompt panel — the single best feature — shows a self-contradicting prompt.** G-27/C-129, re-derived at
  **1,956/1,956 and 5,502/5,502 prompts (100%)**: `<persona>` says "a hidden impostor is killing crewmates one
  at a time" in a 2-impostor game, and 90 lines later the same prompt says "Your fellow saboteurs: p-8".
  490/1,956 and 1,368/5,502 prompts carry both strings. It also states a win condition that is arithmetically
  wrong for two impostors.
- **Layout and jargon:** the fixed dock takes ~35% of a 900 px viewport and hides the map entirely at 800×450
  (which is why the hero GIF never shows the map — P3's frame-sheet finding, A3); card subtitles read
  "(DESIGN.md §11.3)", "Task 9.6 / 10.x, typed on the wire by 12.2", "sentinel — not a KPI"; "4p1i/9p2i" is
  never expanded.

---

## 2. How the tracks compound (the six couplings worth knowing)

1. **Gameplay symptom ⇄ code cause, same defect, two independent discoveries.** G-3 ⇄ C-2 (fabricated
   completions), G-1 ⇄ C-10/C-71 (self-location and stale `last_seen`), G-2 ⇄ C-11 (ungrounded sighting),
   G-38/ux ⇄ C-7 (phantom corpses), G-25 ⇄ C-67 (marker husks), G-12/G-13 ⇄ C-3/C-4 (impostor target
   selection). Six blind co-discoveries is strong evidence the findings are real, and it is also the honest
   answer to "did the reviewers just agree with each other" — they could not have.
2. **The evidence defect and the deception result are one mechanism.** §1.4 + §1.5. Fixing the flag grounds the
   crew *and* removes the impostor's best weapon; the measured "deception demonstrated" and the measured
   "conviction engine convicts innocents" are the same number read from two sides.
3. **The memory defect contaminates the ML evidence.** C-2's verifier: *"the same rows feed eval/ML features
   derived from rendered memory, so the corruption is silently baked into recorded baselines."* Track C's
   researcher persona is the audience most likely to ask what the features were built on.
4. **The comparator defects sit under the ML headline.** C-3 + G-12 both depress the 9p2i FSM impostor, and both
   are 9p2i-only — the exact roster the referee, the canary denominator and the win-edge table all use.
5. **The presentation plan's first act publishes the product's worst bugs.** C/A3 recommends hosting the demo
   bundle and re-recording the GIF; C-7, the CORRECT badge, the singular persona and the jargon copy all live in
   that artifact. And the GIF/bundle bake *featured replays* — a substrate re-record invalidates them, so a GIF
   re-recorded before the substrate phase gets re-recorded again.
6. **Byte-identity doctrine is what makes "just fix the wording" hard.** B §8's second root cause: the
   prompt-byte golden plus committed baselines pin every render byte, so C-10, C-15, C-29, C-73 and the whole
   §1.3 cluster need a real-LLM re-record. B's own proposal — a render-version stamp decoupling legibility fixes
   from substrate fixes — is the structural answer and belongs in the substrate phase's scope.

---

## 3. Where the project is *stronger* than it claims (under-sold)

1. **`tests/meetings/test_prompt_byte_golden.py` is a better agentic-workflow artifact than "300 PRs".**
   B §7 item 8: it re-runs the *real* `MeetingManager` over 204 committed meetings against recorded prompt bytes,
   explicitly refuses to re-implement the assembly ("a second source of truth and a dishonest golden"), and ships
   `test_one_byte_template_perturbation_breaks_the_golden` — *"a golden that cannot fail is not a gate."* 7 s.
   Named nowhere on the front door. The same instinct is repo-wide: every gate is plant-detect-cleanup tested
   (B §7 item 9).
2. **The ML negative result is robust, not just honest.** B §7 item 27: 54 offline re-derivations from frozen
   weights, 0 failures, 20 s; an independent surrogate rebuild matching 46/60 and 55/60 exactly; **the NO-GO
   surviving a 100× epoch / 300× lr sweep**. The docs say "we didn't ship it"; they never say "and we tried to
   break our own negative and could not". That is the sentence a research lead wants.
3. **There is a corpus-level integrity audit nobody has written down.** A §E: 0 teleports in 16,453 room
   changes; 188/188 kill rejections explained with 0 unexplained; 0 double reports in 626; 0 bodies without a
   kill event; 0 dangling ids in 3,814 ballots; 0 impostor ballots naming a partner in 929; crew reporting
   exceptionless (0/700 agent-ticks in a body room ended without a report). This is a stronger, more specific
   determinism story than the run-twice `diff`, and it is free — the measurements already exist.
4. **The vent channel is a perfect end-to-end pipeline, and it is only ever described as a limitation.**
   `vent_sighting` 440/440 = 100% precision across 300 games; 99.6–100% of held vents reach the table;
   96.7–97.1% convert to the right ejection; 310/316 as sole convicting evidence (G-2, A §E, G-13). The guide
   sells "87% of catches ride a vent" as the thing that *isn't* general deduction — true — but the positive
   reading ("the one engine-grounded evidence channel is clean from perception through memory, speech, flag,
   ballot and tally, measured at n=440") is never stated and is exactly the claim a systems reviewer values.
5. **Reproducibility scope 3 may already be closed.** README:132 says cross-platform optimizer portability is
   "designed for, not yet confirmed" and asks a reader to close it; B §7 item 26 reports the reviewer measured
   `_ln` max rel dev 4.14e-16, AS241 abs dev 2.67e-15, and **the ES golden digest reproducing bit-identically on
   Darwin-arm64**. ⚠️ Do **not** upgrade the README on this alone: the owner's own working note records that
   committed ES artifacts/pins reproduce only inside the Linux container, not on bare macOS, so these may be two
   different digests. Worth one controlled owner-assisted run — it is the only front-door claim that might be
   upgradeable for free.
6. *(bonus)* Zero `type: ignore` in any production package under `mypy --strict`; zero TODO/FIXME/HACK across
   121,367 lines; zero `any`/`@ts-ignore` in the frontend under `noUncheckedIndexedAccess` +
   `exactOptionalPropertyTypes`; redaction split by provenance not by pattern, fuzzed 3,000 examples
   (B §7 items 7, 15, 20, 29).

---

## 4. Top 10 must-fix before showing a senior reviewer

Ordered by (probability the reader hits it) × (damage to a stated claim) ÷ (fix cost).
**RR** = needs a real-LLM re-record to move the committed baseline.

| # | Item | Smallest honest fix | Files | Size | RR? |
|---|---|---|---|---|---|
| 1 | **Fabricated `You completed X` memory** (C-2 / G-3) — 10–23% of completion lines, 159/300 games, 67 spoken at the table, 3 minted STRONG flags. Falsifies pillar 3 and contaminates every ML feature derived from rendered memory. | No wording fix exists. Derive the completion from the engine's `TaskCompleted` event instead of a `pending_task_id` flip (the invariant comment at `store.py:1161` is already false and says so). Until then: a dated known-issue line in the reading guide with the measured rate. | `agents/memory/store.py:1157-1200`; `tests/agents/test_memory_rendering.py:834` pins the wrong rule | S code | **yes** |
| 2 | **Ungrounded sighting minting "VERIFIED evidence"** (C-11 / G-2) — 88% of STRONG `alibi_vs_sighting` name a crewmate, impostor-naming rate 0.117 vs base 0.261, 80% of wrongful ejections, 14.6% precision as sole evidence. | Two-step. **Now (no RR):** re-label on the spectator surface using `api/schemas.py::classify_evidence`, which already splits `role_proof` / `cross_statement` / `weak_signal`, and add one sentence to the guide replacing "40% of subjects are innocents" with the sole-flag precision. **Substrate wave:** thread `SightingRecord` into `detect_contradictions` (the exculpatory path already has it). | `meetings/transcript.py:1414,2380-2495`; `api/schemas.py`; `vote_ballot.j2:100` | S / M | wording no · fix **yes** |
| 3 | **Firewall gate blind spots** (C-31, C-32, C-34) — the leak scanner cannot see visibility, the linter cannot see three packages, and the firewall test plants files in the live tree (2/12 concurrent runs printed false BROKEN). | Three cheap, independent fixes: pass `VisibilityResult` into `assert_packet_is_leak_clean` and assert set-equality of body/player ids; add `orchestrator, api, eval, scripts` to `.importlinter` `root_packages`; plant into `tmp_path` and add `_firewall*` to `.gitignore`. Plus X1 GOOD-11's rewording of "zero violations" → "never breached in CI: contract + planted-leak test + recursive sweep". | `eval/leak_scan.py:610`, `eval/leak_test.py`, `.importlinter`, `tests/test_firewall.py`, `.gitignore`, README:47/74 | M | no |
| 4 | **Phantom corpses on 67% of demo frames** (C-7) — and it blocks hosting. | Consume `TickView.bodies` instead of accumulating kill events; the API already serves the right set with `killed_by` and nothing reads it. Add the missing `MapView` unit test (there is none). | `frontend/src/components/MapView.tsx:227-264,570,591,734` | S | no |
| 5 | **Every prompt tells a 2-impostor game there is one impostor** (G-27 / C-129) — 100% of 7,458 prompts, self-contradicting 90 lines later, in the panel that is the project's best feature. | **Now (no RR):** one caption in the Mind Inspector prompt tab + a known-issue line ("the persona line is not parameterised by impostor count; recorded at baseline 6"). **Substrate wave:** parameterise the six `qwen3_6_27b` templates and fix `"p-4 are your fellow saboteurs"`. | `agents/strategic/prompts/qwen3_6_27b/*.j2` (6 files); `frontend` prompt tab | XS / S | caption no · template **yes** |
| 6 | **The ML comparator is hobbled** (C-3, G-12) — 45.8% of free kills discarded on an id tie-break; 8–12% of impostor decisions stalking ejected players; both 9p2i-only. | State it before someone else does: one paragraph in `docs/ml-program.md` / the close-audit errata saying the +0.12–0.30 win edge is measured against an FSM with two identified target-selection defects, with the measured rates. Then fix both in the substrate wave (re-validate co-location across `targets`; fold `meeting_history` into `_confirmed_dead` — the data is already in memory, only the v3 encoder reads it). | `agents/tactical/impostor_policy.py:336-361,813-838`; `training/reports/*`, `docs/` | S text / S code | text no · fix **yes** |
| 7 | **`vote_correctness_rate`: docstring, README and committed data disagree** (C-113). [D-VERIFIED] the docstring says "structurally pinned to 1.0 … any value below 1.0 is a detector/recording bug to chase"; `replays/samples/9p2i/tournament-eval-report.json` reads **0.9230769**; README:190 sells it as the circularity guard. The repo's own sentinel is red on its flagship artifact and nothing surfaces it. | Correct the docstring (the 6 zero-flag impostor ejections are legitimate — the gate is not the only eject path), and either investigate them or record the ruling. One README clause. | `eval/vote_correctness.py:11-31`, `README.md:190` | XS | no |
| 8 | **`trust` is named in ADR-0001 and README decision 3 and has zero writers** (C-72; [D-VERIFIED] `adjust_trust` has 7 test callers, 0 production). `## Open contradictions` rendered 0/1,656. `DESIGN.md §6.6` shows both as canonical. | Drop "trust" from the README/ADR parenthetical (or say "a trust channel exists and is currently unused"), and mark `DESIGN.md §6.6` as target-not-as-built the way `docs/architecture.md` already handles `DESIGN.md`. Optionally delete `adjust_trust` + `WorkingMemory.goal/path` (C-71). | `docs/adr/0001-*.md:18`, `README.md:100`, `DESIGN.md §6.6` | XS | no |
| 9 | **Dev husks inside quoted dialogue on the spectator surface** (G-25 / C-67) — `[invalid accusation target 'p-6' dropped]` opens 5.1–5.5% of turns and appears in 12.2–12.6% of prompts; ballots are already parsed into chips, turns are not. Plus the `CORRECT` badge spoiler and the audit-citation tooltips. | **Now (no RR):** extend the existing `_BALLOT_PREFIX_MARKERS` parser at `api/replay_loader.py:2696` to turn `free_text`; hide the `CORRECT` badge under "outcome hidden"; strip `(DESIGN.md §…)` / `Task N.M` from user-facing copy. **Substrate wave:** stop splicing the marker into `free_text` at all. | `api/replay_loader.py:2696`; `frontend` ballot/tooltip copy; `meetings/manager.py:3908` | S | spectator no · prompt **yes** |
| 10 | **The front door runs a prompt set no committed replay uses** (B1 + C-130) — every command prints "AILIBI_PROMPT_SET is unset — falling back to … two generations behind the operational baseline" (6× in the 5-game tournament) for a variable documented in no front-door file; and the README's tournament example produces an all-null report (B2). | Default the CLI surfaces to the operational set (or silence the notice under the fake provider) **and** document `AILIBI_PROMPT_SET` beside `AILIBI_LLM_PROVIDER`; point the README's report example at `replays/samples/9p2i/tournament-eval-report.json`. | `agents/strategic/prompts/loader.py:238-242`, `scripts/*`, `README.md`, `.env.example` | S | no |

**Near-misses, all cheap:** C-24 (rule + document the `redistribute` self-channel, or gate it in the substrate
wave); the `--filter=blob:none` clone caveat and the bundle README baking `/Users/danielkeinan/…` (B8/B9);
"recorded verbatim in ADR-0001" is not verbatim (X1 GOOD-12); `docs/deployment.md`'s unresolvable "audit
C-C-1/2/4"; C-115/C-117/C-118 DESIGN drift (four counts in the engine section alone, incl. `redistribute`
appearing 0 times in DESIGN while `tick.py:322` cites it).

---

## 5. The owner's decision: substrate-first vs presentation-first

### 5.1 What each option actually costs, given these findings

The dichotomy is slightly false, and the tracks show why. Sorting the top-10 by `RR?`:
**six of ten need no re-record at all** (#3, #4, #7, #8, #10, and the "now" halves of #2, #5, #6, #9), and they
are precisely the ones a reader hits first. The four that need a re-record (#1, and the deep halves of #2, #5,
#6) are exactly the close audit's evidence-honesty scope.

Three sequencing constraints fall out of the cross-track reading and none of them are in either option as stated:

- **Do not host the demo before fixing C-7, the `CORRECT` badge and the jargon copy.** Hosting is A3, the
  presentation phase's highest-value single act; shipping it with a map that paints phantom corpses on two
  frames in three converts the project's best asset into its most public bug.
- **Do not re-record the hero GIF or bake the demo bundle before the substrate re-record.** Both bake featured
  replays. Doing it first means doing it twice (and P3's GIF finding requires a re-record of the media anyway).
- **Do not publish a results table containing corpus numbers before the re-record** — every number in it
  (34%/30% impostor wins, the 68/2 vs 10/21 cross-tab, 520/520, the win edges) moves. A6 is the one *big*
  presentation item that is not invariant.

### 5.2 The argument for substrate-first (the close audit's recommendation), sharpened

1. **The presentation phase's flagship deliverable is a results table, and three of its rows are now known to be
   confounded**: the +0.12–0.30 win edge (comparator defects C-3/G-12), the impostor win rates (same), and the
   evidence-processing story (C-2's fabricated memory feeding the features). Publishing them with footnotes is
   possible, but it directly contradicts the thesis the presentation is selling — "records a miss as a finding
   rather than moving the bar". A project that just discovered its comparator is hobbled and then published the
   comparison anyway loses more credibility than one that waited a wave.
2. **The substrate fixes are individually small.** #1 is a ~40-line change behind an already-false invariant
   comment; #2's deep half is threading an existing `SightingRecord` into an existing detector; #5's is
   parameterising six templates; #6's is one co-location re-check and one dict lookup. The cost is not
   engineering, it is the single ~23h $0 re-record — which the substrate cadence doctrine says to spend exactly
   once, on a combined wave.
3. **The re-record is the natural moment to pay off B §8's root cause.** A render-version stamp that decouples
   legibility fixes from substrate fixes is the structural fix for "byte-identity doctrine freezes legibility
   bugs", and it can only be introduced at a record.
4. **It converts the biggest remaining risk into the best remaining story.** "I ran three blind reviews of my own
   project, they found that my evidence channel was anti-informative and my memory renderer fabricated
   completions, I fixed both, re-recorded, and here is the before/after" is a stronger portfolio narrative than
   any amount of README editing — and it is the same honesty culture the personas already rate as the top asset,
   applied one more time.

### 5.3 The argument for presentation-first, honestly stated

6/6 personas are blocked at the README, not at the substrate; 5/6 named the same 850 words as the single
highest-leverage change; the GitHub About panel is empty and costs five minutes; and no persona's verdict turned
on any of A's or B's findings — they never got that far. A substrate wave that ships nothing readable leaves the
project exactly as unfindable as it is today for another month.

### 5.4 Recommendation — a sequenced hybrid, substrate in the middle

**Wave 0 — "stop the embarrassment" (days, zero re-record, zero corpus numbers).**
Top-10 items #3, #4, #7, #8, #10, the "now" halves of #2/#5/#9, plus every C-track item that is invariant to a
re-record: A4 (About/topics/badge/byline, 5 min), A5 (the authorship statement — the one thing only the human
can write, and 4/6 personas' MUST), A1/A2 (the README restructure and the jargon rule) *written with placeholders
for the corpus numbers*, B12/B3 (`docs/history.md`, `audits/README.md`, glossary), B4 (architecture one click
from the top). Explicitly deferred out of Wave 0: hosting the demo, re-recording the GIF, and the A6 results
table — all three are corpus-dependent or gated on #4.

**Wave 1 — the evidence-honesty substrate phase (one combined re-record).**
Scope it by the claims it repairs, not by defect count: #1 (memory truth), #2-deep (sighting provenance —
the close audit's own item), G-1 (render the self-location spans `store.py:1025` already holds — the
most-proposed change in Track A, 9 reports), G-9 (a `moved`/`saw_move` shape so a true movement line stops
becoming a false placement), #5-deep (persona parameterisation), #6-deep (the two FSM target-selection defects —
cheap, and they are what makes the ML comparison honest), #9-deep (husks out of `free_text`), C-10 (`last_seen`),
C-24 (rule or gate the redistribute channel), and the render-version stamp. Everything else on A's 43-item idea
list is a *game-design* wave, not an evidence-honesty wave — keep it out.

**Wave 2 — presentation, on corrected bytes.** A6 results table with real numbers, `docs/ml-program.md` in
research shape with N1/N2 as the headline (P2's MUST), the demo hosted (now safe), the GIF re-recorded against
the new corpus, B11 "what I learned" — which now has a genuinely good chapter in it.

**Net:** the close audit's "substrate first" is right about the *ordering of the expensive thing*, and Track C is
right that the project is currently unreadable. They are not in conflict once you notice that six of the ten
credibility risks and most of C's MUST list cost nothing but text and a frontend fix. Do the free half now, spend
the one re-record on the evidence-honesty wave, and let the presentation quote numbers you will not have to
footnote.

---

## 6. Confidence and residual uncertainty

- **[High]** everything carrying an A/verdicts or B/verdicts CONFIRMED, plus the four items I re-checked in the
  repo directly (`adjust_trust` callers, `vote_correctness_rate = 0.923`, the README/ADR wording, the docstring).
- **[Medium]** G-22/G-33's "0 impostor reports / 0 meeting calls / 0 calls of the pinned impostor_report
  template" — corroborated by six A reports but not adversarially re-derived; check before quoting.
- **[Medium]** the Darwin-arm64 ES digest (§3.5) — B measured it, the owner's own note says otherwise; resolve
  before touching the scope-3 wording.
- **[Open]** A §E flags one unsettled inter-report contradiction (w2 claims rejected actions are absent from the
  JSONL; five other reports read them out of the same array). The majority reading is almost certainly right,
  but w2's per-game conclusions that depend on it should be re-checked before any of them are cited publicly.
