# The ambition synthesis — what would make AiLibi remarkable

Cross-track read of `A/` (gameplay-down, G-1…G-41 + 12 adversarial verdicts), `B/` (code-up,
C-1…C-130 + 14 adversarial verdicts), `C/` (portfolio perception, A1–A6 / B1–B13 / D1–D9 / E / F),
against the repo's own open decision in `audits/audit-phase-19-close.md` §4.

Sizes: **S** ≈ one agent-directed task (<1 day) · **M** ≈ a small wave (2–5 tasks) · **L** ≈ a
chartered phase. "Re-record" = requires the ~23 h operator wall / $0 flat-rate real-LLM re-record
to move the committed baseline.

---

## 0. The one-line answer

**The three blind tracks converged on one cell, and it is the same cell the project's own close
audit measured: convictions are perfect where the substrate hands the crew role-proof
(310/310 = 1.000) and worse than a coin flip where agents must actually infer (46/125 = 0.368,
with 79/79 of all innocent ejections there).** Fixing that cell is simultaneously the best
engineering move, the best research result, the best demo, and the best portfolio narrative —
because the before/after instrument is already committed and costs $0 to run. Everything else in
this document is either (a) the $0 work that must land *first* so the result has somewhere to be
published and so the project's loudest claims survive a skeptic, or (b) the counterweight that
keeps the fix from breaking the game.

---

## 1. Where the tracks reinforce each other

These are the findings where a spectator watching replays, a reviewer reading source, and an
outside reader judging the repo each arrived at the same thing from different directions. That
triple corroboration is the strongest evidence in this whole review, and it is what makes the
plan below low-risk.

### 1.1 The inference channel is broken — and each track names a different half of the same defect

| Track | What it saw | Ids |
|---|---|---|
| A (gameplay) | `alibi_vs_sighting/strong` names an impostor **17.2%** of the time against a **25.3%** random baseline (p=0.0048); `alibi_conflict` is **0/35** (p=2.9e-5); yet 82 meetings whose only strong flag is one of these produce **77 ejections (93.9%)** | G-2 (verdict CONFIRMED-DESIGN-CHOICE, every number reproduced) |
| A | Crew have no dated self-position line; 20.5% of crew `whereabouts` are false; of 79 crew ejections, **35 (44.3%) victim-caused, 17 (21.5%) caused by a *witness's* mis-dated sighting** | G-1 (verdict PARTIALLY-TRUE — attribution corrected down from 73%) |
| A | 38/313 flags re-speak the **origin** half of a true `move A→B` memory line as a placement; **38/38 are factually wrong**, 32 STRONG, 10 wrongful ejections across 25 games | G-9(a) (CONFIRMED-BUG, unsanctioned) |
| A | 10.0–23.1% of `You completed X` memory lines are **fabricated**, in **159/300 games**, minted on the tick a teammate dies — the exact window the next meeting litigates; three manufactured STRONG flags traced | G-3 (CONFIRMED-BUG) |
| B (code) | The grounding channel (`SightingRecord`) is wired **only to the exculpatory path**; `_iter_sightings` (`meetings/transcript.py:2170-2179`) yields every spoken sighting unfiltered. STRONG `alibi_vs_sighting` = 60, **53 name a crewmate**, 17 minted by an impostor — contradicting the module's own repeated comment that such a flag *is* a false positive | C-11 |
| B | The same fabrication, found from source with an independent repro: `store.py:1157-1200`'s "the owned set only ever shrinks" premise was falsified by `dead_task_rule: redistribute` | C-2 |
| B | The belief block asserts a stale `last_seen` that the observation list in the *same prompt* contradicts | C-10 |
| C (outside) | The project's own reading guide already volunteers it: "**87% of correct 9p ejections ride an engine-certified vent sighting** … general social deduction: NOT demonstrated" — which the research-lead persona called "the single most credible thing I read all session" | C-E5, P2 §3 |
| Repo | 19.14's committed cross-tab: 310/310 with proof, 46/125 without, 79/79 innocent ejections in the non-direct cell, weak-flag-only convictions **5/5 innocent** | audit-phase-19-close §4.1 |

Two facts make this *actionable* rather than merely diagnosed:

- **The taxonomy already exists and is already on the spectator surface, and the agents are never
  told.** `api/schemas.py:622-752` `classify_evidence` splits flags into `role_proof` /
  `cross_statement` / `weak_signal`; `frontend/src/components/MeetingView.tsx:338-393` renders all
  three. Meanwhile `agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:100` tells the voter, in
  **2543/2543** recorded ballot prompts, that "Each flag below is VERIFIED evidence … never side
  with an unverified counter-accusation over a verified flag." The product knows the difference
  between proof and inference. The agents do not. (G-2 ∧ C-129 ∧ A-idea-2)
- **The data the agents needed is already in the store.** `store.py:1025-1028` already keeps
  `own_room_by_tick` and uses it only to scope *others'* sightings; `DESIGN.md:705`'s worked
  example specifies a richer self-location line **with a tick range** than what ships. The fix is
  rendering, not modelling. (G-1 verdict)

### 1.2 The code track independently found the mechanism behind almost every gameplay symptom

G-3 ↔ C-2 (fabricated completions; two independent repros). G-2 ↔ C-11 (ungrounded prosecution).
G-38/ux-lead ↔ C-7 (phantom corpses: 1182/1769 frames = 67%, 50/50 games). G-25 ↔ C-67 (guard
markers as an in-band substring channel). G-27 ↔ C-129 ("the render contract carries no impostor
count, so the templates *cannot* say it right"). G-12 ↔ C-3/C-4 (impostor FSM: 126/387 = 33%
missed co-located kills; 298/880 = 34% of stalk moves toward a refuted sighting). G-10 ↔ C-22
(intra-tick id order decides contested kills and witness sets).

**This pairing is itself a portfolio asset** and nobody has ever assembled it: a symptom census
over 300 replays and a blind source review landing on the same eight defects, with the source
review supplying the line numbers and the gameplay review supplying the body count.

### 1.3 The strongest engineering in the repo is invisible to every audience

B §7 lists 32 genuinely-good items; C's personas found almost none of them. The most under-sold:
`mypy --strict` with **zero `type: ignore` in any production package**; the prompt-byte golden
that re-runs the real `MeetingManager` over 204 committed meetings and ships
`test_one_byte_template_perturbation_breaks_the_golden` ("a golden that cannot fail is not a
gate"); the plant-detect-cleanup pattern on every firewall gate; `check_doc_facts.py` running
against the real repository *inside* the normal gate; `verify_ml_evidence.py` re-deriving 54
headline numbers from frozen weights in 20 s offline; the ES golden digest reproducing
bit-identically on Darwin-arm64, closing an open question the repo asks a reader to close
(B §7.26). C-E1 confirms the front-door claims reproduce offline in seconds and calls it "the
single best thing this project has going for it."

---

## 2. Where the tracks contradict — and the rulings that matter for ambition

- **A's own verdicts refuted or corrected four of A's headline claims.** G-6 (bodies) is
  CONFIRMED-DESIGN-CHOICE with **zero real misses** corpus-wide (all 6 crew-seen unreported
  bodies were first seen on the final tick); G-7's "median +4 ticks" headline is a two-clock
  artifact (the agent clock runs exactly +1, on 18,936/18,936 discriminating sightings) though the
  underlying "no time of death" fact holds; G-4's alarming fabricated-`saw_vent` half is REFUTED
  (739/748 = **98.8%** grounded); G-1's 73% attribution drops to 44.3%.
  **Ruling: do not charter work on the refuted items.** The honest substrate list is
  G-1 / G-2 / G-3 / G-9(a) / G-8 / G-25(a) / G-12. That discipline is also the story — see §4 FM-5.
- **B §8 vs the substrate cost.** B's root cause #2 is that byte-identity doctrine freezes
  *legibility* bugs behind a real-LLM re-record (C-10, C-15, C-29, C-73, plus G-25/G-27/G-34).
  **Ruling: this is an argument for batching, not for skipping.** Every pending legibility fix
  should ride the ONE combined re-record the substrate phase already has to pay for (the standing
  cadence doctrine). Queue them explicitly now so none is dropped.
- **C-D7: process as asset or theatre.** P2 reads the ledgers/gates as "process theatre for a
  one-person project" and notes the flip bar is "close to unpassable by construction" (quoting the
  project's own input audit); P1/P4/X2 read the identical protocol as the differentiated 2026
  story. **Ruling (C's merger, and I agree): framing, not removal** — with P2's sharper point
  ("strong on measurement, weak on knowing when to stop building measurement") *owned* in writing.
  B's measurement makes it concrete and quotable: **95,824 lines of process narration against
  57,776 lines of core product Python (1.66:1)**.
- **C-D4: the ML negative result.** Researcher wants it as the headline; recruiter read it as
  "the last two phases produced nothing." **Ruling: split by audience** — README gets one
  paragraph *titled by its result*; `docs/ml-program.md` carries N1/N2 as the lede.
- **The one genuinely dangerous contradiction — C amplifies claims B proved hollow.** C's plan
  (A1/A4/F2) puts "zero firewall violations", "agents cannot import engine directly or
  transitively (import-linter enforced)" and "the most important test" in the GitHub About field
  and README line 1. B showed a planted `agents/_probe_orch.py` importing `orchestrator.game`
  passes all four contracts **and the whole of `check.sh`** (C-32), and that a mutation making
  every undiscovered body visible to every crewmate survives **all four leak suites including the
  ML champion gate** (C-31). **Ruling: FM-4 is a hard prerequisite for the front-door push.**
  Amplifying a claim a senior engineer can break in ten minutes converts the project's best asset
  into its worst liability.

---

## 3. The four stories, and what each is one move away from

| Story | Best audience | Strongest existing evidence | The one thing missing |
|---|---|---|---|
| **B. Deterministic multi-agent reasoning testbed** | senior engineers, researchers | replay contract (100 replays re-walk + hash-verify in 3.14 s), the observation firewall as a real chokepoint, `engine/tick.py` as a pure function over frozen dataclasses | the firewall gate cannot actually fail (C-31/C-32) — fix, then say it precisely |
| **A. Agent-directed engineering at scale** | hiring managers, builders | 321 contracts ↔ 321 byte-mirrored prompts with a `--check` gate, 350 merged PRs, AGENTS.md, coordination re-anchoring commits, co-author trailers on ~90% of commits | the human is never named or described at the front door (C-A5, 6/6 personas); the loop is linked but never *shown* (C-B5) |
| **C. Honest, pre-registered eval / negative ML results** | ML & agents researchers | pre-registration (#298) precedes measurement (#317) precedes ruling (#318) *in git*; NO-FLIP ×2 with losing evidence committed; N1/N2; the 87% cross-tab | no research-shaped artifact, and **no ceiling** — nothing says how much deduction was *available* to be recovered (FM-2) |
| **D. Spectator product** | recruiters, product engineers, everyone | meeting view + Mind Inspector ("a better LLM-agent debugging surface than most commercial agent tools ship" — P3), as-agent fog, guided tour | not hosted, and the map ships a corpse bug in 50/50 games (C-7) |

---

## 4. The seven flagship moves

### FM-1 — The inference-channel substrate phase, run as a pre-registered before/after
**Builds on:** G-1, G-2, G-3, G-9(a), G-34 · C-2, C-10, C-11, C-15, C-29, C-73 ·
A-researcher R1/R4/R5/R7/R8 · audit-phase-19-close §4.1/§4.2.
**Audience:** all four. This is the only move that advances every story at once.

Five changes, each independently small, all sharing one re-record:

| # | Change | Files | Size |
|---|---|---|---|
| a | Render a dated self-location trail (ideally with a tick range, as `DESIGN.md:705` already specifies) from the `own_room_by_tick` map the store already keeps; auto-fill or validate the roll-call `whereabouts` against it | `agents/memory/store.py:1025-1028,1191-1197`; `qwen3_6_27b/*roll_call*.j2` | S |
| b | Ground the **prosecution** side of a flag against `SightingRecord` the way the vouch side already is; suppress a flag whose sighting-side row is a `move A→B` transition or whose alibi window is a single tick equal to the sighting tick | `meetings/transcript.py:2170-2179,2379-2494` | M |
| c | Derive `You completed X` from the engine's `TaskCompleted` event instead of a `pending_task_id` flip | `agents/memory/store.py:1157-1200` | S |
| d | Split the flag block by `classify_evidence` category: "this is proof" for `role_proof`, "one of these two accounts is wrong and nothing here says which" for `cross_statement`/`weak_signal`. Stop calling all of it VERIFIED | `agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:100-104` (+ the render context) | S |
| e | Ship a map/adjacency card in the meeting prompt and demote a flag whose two rooms are adjacent within one tick | prompts + `transcript.py` | S–M |

Change (e) alone has a startling justification: **148/234 (63.2%) of strong `alibi_vs_sighting`
flags name *adjacent* rooms** — one tick of walking reconciles both statements — 130 of those name
innocents, and **0 of 7,458 meeting prompts contain a map, adjacency, or travel times**
(A-researcher, verified).

**Size:** L (a chartered phase) · **Re-record: YES** (one combined; ~23 h operator, $0).
**Risk:** (i) every one of a–e pushes crew-ward and crew already wins 70–75% of 9p2i — ship with
FM-7 as the impostor budget or the balance moves the wrong way and the recording is wasted;
(ii) recording variance; (iii) scope creep into mechanics — the phase charter needs its own
NOT-list.
**Evidence it worked (all $0, all against instruments already at HEAD):** non-direct-cell
conviction accuracy 0.368 → target ≥0.60; corpus innocent ejections 79 → target <35; false crew
`whereabouts` 20.5% → <3%; sole-`alibi_vs_sighting` precision 14.6% → ≥50%; grounded sighting-side
36.5% → 100%; fabricated completion lines 10.0%/23.1% → 0; turn→ballot consistency 0.447 → higher.
Plus FM-2's ceiling as the y-axis.

### FM-2 — Publish the solvability oracle and a research-shaped results page
**Builds on:** A-researcher's new census · G-8 verdict · G-19 · C-A6 · P2 MUST-2 · audit §4.1.
**Audience:** ML/agents researchers, senior engineers.

The single most publishable number nobody has stated yet: computing, from **living crewmates' own
perception only, with no LLM**, who could have committed the last kill —

- the candidate set is a **singleton in 109/626 body meetings, and correct 103/109 = 94.5%**;
- ≤2 candidates in 208/626; the killer is inside the set in **581/626 = 92.8%**;
- **61 of 354 actual ejections landed on someone the crew's own pooled perception had already
  cleared.**

That is an *information ceiling*: the game is solvable from the crew's own eyes far more often
than the crew solves it, which converts "deduction not demonstrated" from an apology into a
measured gap with a number on it. Ship as `eval/solvability.py` (a `replay_walk` consumer) plus a
≤2-page `docs/ml-program.md` in research shape — problem, environment (obs/actions/meeting
protocol, one figure), method (ES over a 19-weight utility scorer; the referee as *selection*
gate, never reward), one results table (arm, win vs same-seed FSM, McNemar p, referee verdict),
**N1/N2 framed as specification gaming of a social-deduction referee**, the 87% vent cross-tab,
the ceiling chart, limitations (one model, one prompt set, n=50), related work.

**Size:** M · **Re-record: NO** (runs over committed bytes, offline, $0).
**Risk:** it publishes a self-critical number — which is exactly the currency this project already
trades in (C-E5) and the reason all six personas trusted it.
**Evidence it worked:** the analyzer reproduces from a fresh clone in <60 s the way
`paired_stats.py` already does (P2 re-derived the McNemar cells and the 2×2 with stdlib in
minutes); a reader can rerun the ceiling themselves; the ceiling becomes FM-1's headline axis.
**Do also:** commit or explicitly de-scope `training/reports/_finalist_eval_raw` (P2 GOOD) — today
the central ML ruling rests on measurements of evidence not in the repo.

### FM-3 — Host the demo, after fixing the three things that make it lie
**Builds on:** C-A3/A4/F3/F4 · C-7 · C-9 · C-47 · G-38 · G-41 · G-28 · A/ux-visual-pass-lead.
**Audience:** recruiters, product/frontend engineers, and every reader's first 10 seconds.

`scripts/build_demo_bundle.py` already produces an 8.8 MB static directory in 4–5 s that plays
with no API and is e2e-tested with `/api` blocked at the network layer. `has_pages: false`,
homepage `null`. A ~15-line Pages workflow is the whole deployment. **But do not host it first** —
today it ships: four corpses on the map at seed-2 t29 when the engine has one
(`MapView.tsx:227-264`, phantom in **1182/1769 frames, 50/50 games**, C-7 — the corpses never
disappear); two stacked focus traps that make Tab a no-op over an open meeting (C-9); product copy
carrying "(DESIGN.md §11.3)" and "Task 9.6 / 10.x" (G-41, C-B6); a bottom dock eating ~35% of a
900 px viewport and hiding the map entirely at 1000×640 — **the exact viewport the hero GIF was
recorded at**, which is why the GIF never shows the map (P3's measured frame sheet: canvas top
311 px vs dock top 308 px); a "CORRECT" ballot badge that reveals a role in unspoiled mode; and
impostor ballots confessing the role in 15.9% of cases on the spectator surface (G-28).

**Size:** M · **Re-record: NO** (frontend + docs + one workflow).
**Risk:** hosting unfixed spends the one first impression on a bug every visitor sees.
**Evidence it worked:** `buildBodyStatesByTick` consumes `TickView.bodies`, phantom frames
1182 → 0 over all 50 committed games; Pages URL live in README line 1 and the GitHub homepage
field; the re-recorded hero shows a moving token, a kill and the meeting auto-pause in frame.

### FM-4 — Make the loudest architectural claims true before amplifying them
**Builds on:** C-31, C-32, C-34, C-125 · C-B9 · (blocks C-A1/A4/F2).
**Audience:** senior engineers, hiring managers — and it is the best interview story in the set.

Three fixes, all cheap, all no-re-record:

- `.importlinter`: add `orchestrator, api, eval, scripts` to `root_packages`. Today a planted
  `agents/_probe_orch.py` importing `orchestrator.game` yields "Contracts: 4 kept, 0 broken" and a
  fully green `check.sh`; contract coverage is **89 of 383 tracked Python files** (C-32).
- `eval/leak_scan.py`: give `assert_packet_is_leak_clean` the `WorldState`/`VisibilityResult` so it
  can recompute *entitlement*, not just shape, and add B's mutation harness as a gate — today
  mutation **M6 (every undiscovered body visible to everyone) survives all four suites**, including
  the ML champion gate wired at `training/crew/scorer.py:1735`, while `DESIGN.md:933` titles the
  test "the most important test" (C-31).
- `tests/test_firewall.py`: plant into `tmp_path`, not the live tree — 2 of 7 concurrent
  `lint-imports` runs FAILED with a false BROKEN contract (C-34).

Then restate the claims precisely (C-B9): "never breached in CI: import-linter contract +
planted-import test + recursive leak sweep", not "enforced by tooling" repo-wide.
**Size:** M · **Re-record: NO** · **Risk:** none material; the pattern the repo already uses
("a gate that cannot fail is not a gate") is the fix.
**Evidence it worked:** the planted probe now BREAKS a contract; M6/M1/M10 now fail; a short
`docs/` paragraph naming exactly what is enforced and what is discipline. Write it up: *"my own
blind review found that my most-advertised test could not fail; here is the mutation gate I added"*
is worth more to a senior engineer than the original claim ever was.

### FM-5 — Publish the review itself: "three blind AI reviews of a repo built by AI agents"
**Builds on:** the existence of A (13 reports, 300 replays, 707 meetings, 12 verdicts), B (16 area
reviews, 130 findings, no P0, 14 verdicts), C (6 persona reads) · C-B11 · C-D7 · C-D9.
**Audience:** builders, hiring managers, agent-tooling people. Highest novelty of any move here.

Curate the three tracks into `audits/review-2026-08-19/` plus a short essay. The *interesting*
part is not the 171 findings — it is the adversarial layer: the reviews **disproved four of their
own headline claims** (G-6 bodies is correct fog-of-war with zero real misses; G-7's headline is a
two-clock artifact; G-4's fabricated-vent half is 98.8% grounded; G-1's attribution drops from
73% to 44.3%) and **corrected severities in both directions** (C-1, C-31, C-32 up; others down).
An essay titled by that — *"we ran three blind AI reviews on an AI-built codebase; the most useful
output was the four claims they retracted"* — is a genuinely new artifact, and it is the honest
answer to C-D7's "process theatre" critique: the process *catches things*, including itself.
**Size:** M (curation + essay; the reports exist) · **Re-record: NO**
**Risk:** a large pile of self-criticism needs the verdicts and the fix-PR links up front or it
reads as chaos rather than rigor.
**Evidence it worked:** each subsequent fix PR cites its `G-n`/`C-n`; the finding→verdict→fix→PR
chain is browsable; the essay is the thing people link to.

### FM-6 — The agent-directed engineering page, with mechanics and receipts
**Builds on:** C-A5 (6/6 personas), C-B5, C-B11, X2 story A, C-E6 · B §8's 1.66:1 measurement.
**Audience:** hiring managers, builders. X2 and P4 both call this the most differentiated and most
saleable story in 2026, and it is **entirely absent from the front door** — the README names no
person, while git shows "Claude" as first-class author on 310 commits (35%).

`docs/how-it-was-built.md` + a public post: the five-step loop; **one real contract shown inline**
next to its generated prompt and the PR it produced (not linked — shown, per C-B5); the standing
rules in `AGENTS.md`; the byte-mirror gate (`generate_prompts.py --check`, 321 ↔ 321); the
coordination re-anchoring commits; what CI could and could not catch — with C-31/C-32 as the
honest answer; and the lesson P2 handed over: 95,824 lines of process narration against 57,776 of
product Python, owned rather than hidden ("strong on measurement, weak on knowing when to stop
building measurement"). Close with FM-5.
**Size:** M · **Re-record: NO** · **Risk:** the only move here that cannot be delegated — it is the
one page only the human can write, and every hiring-manager persona said they would ask about it.
**Evidence it worked:** a reader can verify agent authorship in git in 30 s (branch names, commit
authors, `Co-Authored-By` trailers naming model versions); the contract→prompt→PR triple is one
click each.

### FM-7 — The impostor's half: fix the visible stupidity, and pay for FM-1's crew buff
**Builds on:** G-12 (verdict CONFIRMED-BUG), C-3, C-4, G-13, G-15, G-39 · A-idea V6/V9.
**Audience:** everyone who watches one game — i.e. the demo's whole audience — plus it is the
balance budget FM-1 requires.

The verification here is unusually strong: an offline re-run of the real `ImpostorPolicy` matched
the recorded action stream with **0 mismatches over 10,335 decisions across 300 games**, and then
showed the impostor spends 8–12% of decisions hunting players the whole table watched get ejected,
walking past isolated killable crewmates because a corpse's id sorts lower — **provably throwing
seed 36**. From source, C-3 measures `kill_available_ticks=387, intent_kill=233, MISSED_KILL=126`
(**33%**) and C-4 measures `stalk_moves=880, toward_refuted=298` (**34%**). Add: fold meeting
outcomes into `_confirmed_dead`; re-validate all scored targets, not just `targets[0]`; invalidate
a sighting whose room is currently visible and empty; peek before venting (exits are seen 56.5–59.2%
of the time, enters only 6–9% — the crew wins almost every game it wins on a vent exit); give
finished crew a job (48.6% of ticks contain nothing at all; done-crew are literal `wait` 60.4% of
the time, longest run 36 consecutive ticks).
**Size:** M · **Re-record: YES** (rides FM-1's single combined re-record).
**Risk:** the largest balance risk in the set — must be measured as its own arm, not merged blind.
**Evidence it worked:** `measure_missed_kills.py` 33% → <10%; stalk-toward-refuted 34% → <5%;
dead ticks 48.6% → <35%; impostor win share stays inside a pre-registered band.

---

## 5. Ranking and coverage

**By (impact × credibility) / effort:**

| rank | move | size | re-record | why here |
|---|---|---|---|---|
| 1 | **FM-4** make the claims true | M | no | cheapest, and it protects every other move; without it the front-door push is amplifying a claim a skeptic breaks in 10 min |
| 2 | **FM-3** host the fixed demo | M | no | 6/6 personas gate on the front door; the URL *is* the project for two audiences |
| 3 | **FM-2** the oracle + research page | M | no | the highest-value *new* result in the review, $0, and it is FM-1's y-axis |
| 4 | **FM-6** how it was built | M | no | most differentiated story, currently absent; only the human can write it |
| 5 | **FM-5** publish the review | M | no | highest novelty; near-zero marginal cost; answers the "process theatre" critique with evidence |
| 6 | **FM-1** the substrate phase | L | **yes** | lowest ratio, highest ceiling — the keystone; turns the project's biggest admission into a measured result |
| 7 | **FM-7** the impostor half | M | rides FM-1 | required for FM-1's balance; independently fixes what a viewer notices in game one |

Ratio ranking understates FM-1: it is the only move that moves all four stories, and FM-2/FM-7
exist largely to instrument and counterweight it. Treat 1–5 as *the runway* and 6+7 as *the flight*.

**Moves × stories** (● primary, ○ secondary):

| | B testbed | A agent-directed | C research | D product |
|---|---|---|---|---|
| FM-1 substrate | ● | ○ | ● | ● |
| FM-2 oracle + paper | ○ | | ● | |
| FM-3 hosted demo | | | | ● |
| FM-4 real gates | ● | ● | ○ | |
| FM-5 publish review | ○ | ● | ○ | |
| FM-6 how it was built | | ● | | |
| FM-7 impostor half | ○ | | ○ | ● |

**Assumed, not listed as flagship:** Track C's A1–A6 README/authorship/About work. It is
table-stakes (6/6 personas, one afternoon) and every move above assumes it has landed.

---

## 6. Sequencing — and the answer to the open post-19 decision

The close audit recommends **Option A (evidence-honesty substrate) before Option B
(presentation)**, on the grounds that "polish never ahead of narrative correctness" and that a
presentation phase "amplifies the measured narrative as-is." Both are right. But the menu as
written is a false binary, because most of what this synthesis calls presentation is **not
polish** — FM-4 fixes two false claims, and FM-2 *measures the gap the substrate phase exists to
close*. Neither is amplification of a broken narrative; both are narrative correctness at $0.

**Recommended sequence** (keeps the audit's ruling intact, changes only what runs in front of it):

- **Lane 1, days 1–3 (all $0, no re-record):** FM-4 → C's A1/A2/A4/A5 README+authorship PR →
  FM-3's bug fixes → host. Nothing here touches gameplay bytes; every gate stays green.
- **Lane 2, weeks 1–3 (all $0, no re-record):** FM-2 (`eval/solvability.py` + `docs/ml-program.md`
  + the README results table), FM-6, FM-5. Lane 2 is also where the **legibility batch queue**
  gets written down — every fix that is blocked only by the prompt-byte golden (C-10, C-15, C-29,
  C-73, G-25 husks, G-27 plural impostor, G-34 spawn-block/coalescing, G-23 dead-subject vent
  rule) is staged so it rides FM-1's single re-record rather than being deferred one at a time.
- **Lane 3, the chartered phase:** FM-1 + FM-7 + the legibility queue as **one** combined
  re-record, pre-registered against the 19.14 cells *and* FM-2's ceiling, with the impostor arm
  measured separately. Publish the before/after into the venue Lane 2 built.

Two dependencies are hard: **FM-4 before any amplification** (§2 last bullet), and **FM-7 shipped
with FM-1, never after it** (the crew-ward balance).

---

## 7. The one-paragraph pitch

**Shippable today** (product-first, human named, ML titled by its result — per C-D5/D4):

> **AiLibi** is a deterministic Among-Us-style social-deduction simulator where LLM agents move,
> witness, remember, accuse and vote behind an enforced observation firewall — every game replays
> byte-for-byte from an action log and a per-tick hash, and the spectator lets you open any agent's
> mind at any tick: its prompt, its response, its memory, its beliefs. I'm Daniel Keinan; I wrote
> the 321 task contracts, the review gates and the audit rulings, and AI coding agents wrote every
> line of production code across 350 merged PRs and 19 phases. The measurements are published the
> same way: 100 committed replays reconstruct in three seconds, and the project's own headline
> finding is that **87% of the crew's correct ejections ride one engine-certified tell rather than
> reasoning** — general social deduction is not demonstrated, and saying so is the point. Four
> learned tactical policies beat the scripted baseline on wins; none was adopted, because they
> failed a bar that was pre-registered before the measurement was taken.

**After FM-1 + FM-2 land** — replace the last two sentences with the thing no comparable project
can say:

> …and we can now measure how much deduction was *available*: from the crew's own perception
> alone, with no LLM, the killer is inside a computable candidate set in 92.8% of body meetings
> and that set is a correct singleton 109 times in 626 — while the agents' convictions were
> perfect where the substrate handed them proof (310/310) and worse than a coin flip where they
> had to infer (46/125). This is the before/after of closing that gap.

---

## 8. The one image

**Not the GIF, and not the meeting screenshot alone: a single side-by-side still of the same tick
— omniscient on the left, one crewmate's as-agent fog on the right.**

Why this frame and no other:

- It is the only image that states all four stories at once: the firewall (story B), the product
  (story D), the research premise (story C — "this is what the agent was allowed to know when it
  wrote the sentence below"), and, with a byline, story A.
- Every persona called the meeting PNG "the money shot" (C-D1, C-F4), and the ux lead independently
  called the as-agent fog view plus the one-click full-prompt panel "the project's best demo
  asset." P3 called the firewall-safe visual grammar (identity ≠ guilt) "a design decision I'd hire
  for." Compositing them is free.
- Both halves already render correctly today: the ux pass verified the fog view for p-3 at seed-2
  t29 lights only MedBay, shows the trailing p-7, and hides roles.
- It fixes the GIF's measured failure without needing the GIF: the current hero never shows the map
  because the fixed dock covers the canvas at the 1000×640 recording viewport (P3's frame sheet).

**How to make it:** after FM-3's corpse fix and dock-layout fix, take two screenshots of the same
featured game and tick at ≥1440×900 — one omniscient (dagger badges, the body, everyone placed),
one as-agent for a crewmate who is about to be wrong — composite side by side, and caption in one
sentence: *"Left: what happened. Right: everything p-3 was allowed to know when it voted."*
Underneath, the accusation card p-3 actually wrote.

**Second asset (the GIF/MP4), 8–10 s, one loop:** tokens move → kill flash → the transport stops
itself at the meeting → the fog toggle flips. Ship MP4/WebM beside the GIF (GitHub renders video;
640 px GIF is palette-crushed).

---

## 9. What not to do

- **Do not build on the refuted findings.** G-6 (unreported bodies) is correct fog-of-war with
  zero real misses; G-7's headline latency is a clock artifact; G-4's fabricated-vent half is
  98.8% grounded. (A/verdicts)
- **Do not touch the vent channel or crew same-room-only vision.** All three ideation lenses
  independently named these as the two things to leave alone: `vent_sighting` is 440/440 precise
  and drives 71% of ejections — every deduction game needs one certain channel; the visibility
  asymmetry is the forcing function that makes the meeting exist. Narrow repair only: adjacent-room
  **bodies**, never players — and fix `canonical_1.yaml:52-58`, which still documents uniform
  adjacency the code no longer implements (G-14).
- **Do not reach for a bigger model or longer instructions.** Both the memory record
  (impostor info-ceiling, model-upgrade RULED OUT) and A's researcher lens agree: in the exemplar
  meetings the model *had* the right row and read the wrong one, twelve lines down a badly sorted
  list. The defect is rendering and grounding, not capability.
- **Do not ship the crew half of FM-1 alone.** Crew already win 70–75% of 9p2i.
- **Do not host the demo before C-7.** Four corpses in 50/50 games is not the first impression.
- **Do not add more measurement apparatus without a result attached.** P2's unrebutted critique —
  ~29 k LOC of `training/` around a 19-weight champion, 1.66:1 narration-to-product — should be
  *owned in writing* (FM-6), not answered with more tooling.

---

### Provenance

Read in full: `A/collated-findings.md`, `A/verdicts.md`, `A/ideas-summaries.md`,
`A/ux-visual-pass-lead.md`, `B/collated-findings.md` (all 8 sections), `B/verdicts.md`,
`C/collated-portfolio.md`, `C/p2-ml-research-lead.md`, `C/x2-narrative-and-positioning.md`.
Repo touched read-only for grounding: `audits/audit-phase-19-close.md` §4,
`api/schemas.py:622-752`, `frontend/src/components/MeetingView.tsx:338-393`,
`agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:97-104`, `scripts/`, `eval/`.
No repo file was modified.
