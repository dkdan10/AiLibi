# Post-Phase-14 planning — Voice & Judgment: distinct personas, evidence-grounded conviction, and the zero-flag mis-eject channel

**Date:** 2026-07-03
**Author task:** planning-only map for the phase after Phase 14 (closed 2026-07-03, baseline 2). No source
files were modified; the only repo output is this document.
**Baselines referenced:** baseline 1 = `qwen3_32b.v3` @ recording commit `bb9d1b3` (PR #213); baseline 2 =
`qwen3_32b.v4` @ HEAD (`8304e5b`, PR #218), the committed `replays/samples/{9p2i,4p1i}`.
**Model of record:** `Qwen/Qwen3-32B` (Featherless, both call kinds, non-thinking, `$0`).

**Label key (per the charter's "assume nothing"):**
- **VERIFIED** — reproduced by me from committed bytes / read directly in source (with `file:line` or a
  seed+meeting citation, or a scratch-script result reproduced below in §11).
- **INFERRED** — a conclusion I draw from verified facts but did not independently re-measure end-to-end.
- **PROPOSED** — a design option or recommendation, not a fact.

Every headline number in this document was re-derived by me from the committed `tournament-eval-report.json`
and/or the raw `replay-seed-*.jsonl` bytes, cross-checked two independent ways where it mattered (§11 has the
scripts). Where I could not reproduce the close audit's exact definition I say so and give my own number.

---

## 0. One-screen summary

The close audit's central residual claim **reproduces exactly** from my own fold of the committed bytes: the
zero-flag crew mis-eject channel rose **22 → 31** (`+9`) baseline-1 → baseline-2 while the flag-driven channel
fell **31 → 25** (`−6`); net crew mis-ejects `53 → 56`, so 9p2i ejection accuracy held flat (`0.566 → 0.525`).
[VERIFIED — §2.1, `channel_split.py`]

Going **past** the audit, I decomposed the zero-flag channel from the recorded vote-ballot prompt bytes and
found the mechanism is sharper than "prior-carry + persuasive voice":

- **82% of the deciding votes** on zero-flag crew mis-ejects are cast against an innocent rendered at a
  suspicion of **0.60–0.69** — *just* over the hard `0.60` §4.6 gate — carried there by the belief fold's
  **soft accumulators** (testimony spread `+0.12`/`+0.15`, accusation-received `+0.05`, cross-meeting
  prior-carry), **not** by contradiction flags and **not** by body-proximity. [VERIFIED — §2.2,
  `zeroflag_render.py`]
- At the meeting level, **24 of 31** crew zero-flag mis-ejects are "soft-only" (the ejectee never rendered
  ≥0.70 in any convicting voter's graph), vs only **6 of 16** impostor zero-flag catches. [VERIFIED — §2.3]
- The vote surface renders suspicion as a **bare `%.2f` scalar with no provenance** — carried-prior and
  fresh same-meeting evidence are summed into one number the voter cannot tell apart — and **nothing in the
  gate, tally, or guard requires a conviction to cite an observation or turn**. The ballot template even
  ships a sanctioned "gut-read" example with `primary_reason_id: null`. [VERIFIED — §3.2, `af73a` brief,
  `vote_ballot.j2:142-144`, `manager.py:1745-1765`]

**The over-damping ledger the mission demanded up front:** the impostor share of zero-flag ejections is
**34% (16/47)** [VERIFIED — §2.3]. But of those 16 impostor catches, **10 are "hard-backed" (max rendered
≥0.70 — body/kill/vent) and would survive** a rule that only caps *soft-only* suspicion below the gate; only
**6 are soft-only and at risk**. So a hard-evidence-exempt gate is a measured **≈24-crew-mis-ejects-prevented
: 6-impostor-catches-at-risk** trade — and even those 6 impostors can be caught in a later meeting, while a
mis-ejected crewmate is gone for good. [VERIFIED counts; INFERRED downstream-recovery]

**The mission's "vent hallucination" premise is REFUTED.** Vents, the `LABS` room, and `LABS_VENT` all exist
in the engine, and vent-use is a witness-gated *observation*; 141/149 (95%) of vent rationales in baseline 2
name a player who genuinely vented, and my seed-9 deep-check shows the flagged venter was really venting in a
room two of the accusers were standing in. The real (much smaller) concern is possible over-attribution of
*unwitnessed* vents — a firewall question, not a nonexistent-mechanic hallucination. [VERIFIED — §2.4,
`vent_census.py`, `engine/maps/canonical_1.yaml`, `observation/service.py:322-368`]

**The unifying thesis (why Voice and Judgment must be designed together):** the zero-flag channel *is* "voice
beating evidence." The multi-agent-debate literature is consistent and blunt — confident/persuasive rhetoric
overrides truthful peers (CW-POR, sycophancy), and in social-deduction specifically **deception outruns
detection**. A persona layer that makes voices *more* distinct and persuasive, shipped **without** an
evidence-linkage bound, risks making the zero-flag channel **worse**, not better. The two demonstrated
antidotes both point the same way: **per-claim citation of a concrete source/turn as the precondition for a
claim to count**, and **not weighting conviction by raw self-reported confidence**. [INFERRED from §5 research
+ §2 measurements]

Recommendation (§7): a measurement-first Phase 15 that first lands a **shared foundation** (per-subject
suspicion *provenance* + a widened render-input contract — both the Judgment surface and the Voice personas
need it, and recording it is a prerequisite the belief store's aggregate scalar can't skip), then runs a
**Judgment track** (a measured, default-OFF hard-evidence gate lever + a provenance-aware, citation-gated vote
surface) and a **Voice track** (deterministic per-seed persona cards threaded as a render input) as parallel
disjoint tracks *downstream of that foundation*, converging on **one atomic re-record (baseline 3)** — with the
evidence-linkage bound landing *with or before* persona realization so we never ship a louder voice channel
without the evidence gate that tames it.

---

## 1. Verification method & what is reproducible

Baseline 2 is the committed set (`replays/samples/`); baseline 1 lives in git at `bb9d1b3`. The
`tournament-eval-report.json` in each set is a committed, byte-reproducible artifact that carries, per game:
authoritative `roles` (crew/impostor), and per meeting the `outcome`, `ejected_player_id`, full `transcript`,
`ballots`, `contradictions`, and `llm_calls` (the recorded prompt + response bytes). Everything below is a
fold over those two artifacts (and, for cross-checks, the raw `replay-seed-*.jsonl`). The scratch scripts are
listed in §11; each reproduces the close-audit anchor numbers *before* I trusted my own extensions.

Definitions I use (matching the audit's §4/§7): an **ejection** = a meeting with `outcome == "EJECTED"`; a
**crew mis-eject** = an ejection whose `ejected_player_id` is a `CREWMATE`; a **flag on the ejectee** = a
`contradictions[]` entry whose `subjects` list contains the ejectee; **zero-flag** = no such entry;
**flag-driven** = ≥1. These reproduce the audit's `crewmate_ejections` totals exactly (§2.1), so the
definitions are the same.

---

## 2. Verifying the close-audit claim (my own numbers)

### 2.1 The channel split — VERIFIED, exact match

`channel_split.py` over both baselines' eval reports, cross-checked against `vote_correctness` and (for
baseline 2) independently recomputed from the raw JSONL `contradictions`:

| 9p2i | baseline 1 (v3) | baseline 2 (v4) | Δ |
|---|---|---|---|
| total ejections | 122 | 118 | |
| ejection accuracy | 0.566 (69 imp / 53 crew) | 0.525 (62 imp / 56 crew) | −0.041 |
| **crew flag-driven** (the fix's channel) | **31** | **25** | **−6** |
| **crew zero-flag** (voice/carry) | **22** | **31** | **+9** |
| impostor flag-driven | 57 | 46 | −11 |
| impostor zero-flag | 12 | 16 | +4 |

Every cell matches `audit-phase-14-close.md` §4 and the baseline-1 characterization §2 ("12 impostor and 22
crew ejections carried ZERO flags"). The raw-JSONL recompute for baseline 2 returned the identical split
(crew 25/31, impostor 46/16), so the eval report's `contradictions` faithfully mirror the replay bytes.
[VERIFIED — `channel_split.py`, `vent_census`-adjacent recompute]

4p1i moves the same way, with less data: crew mis-ejects `7 → 1` (flag `3→0`, zero-flag `4→1`); it stays the
secondary set. [VERIFIED]

**Reading:** the close audit is correct that the fixes thinned the flag channel and the untouched zero-flag /
voice channel rose to dominate the residual. This is now *my* number, not a trusted one.

### 2.2 Decomposing the zero-flag channel — where the 0.60 gate is crossed (NEW)

The recorded vote-ballot prompt (`llm_calls[].prompt`, `call_kind == "meeting"`, contains "Valid ejection
targets") renders each voter's **exact** per-player suspicion the model saw. `zeroflag_render.py` parses, for
every zero-flag crew mis-eject, the ejectee's rendered suspicion in the graph of each voter who convicted
them (125 deciding votes across the 31 meetings):

| ejectee's rendered suspicion, as SEEN by the convicting voter | share |
|---|---|
| **0.60–0.69** (soft: testimony-spread / accusation / prior-carry, over the gate) | **102 (82%)** |
| < 0.60 (voter ejected against a sub-gate graph — pure voice inversion) | 12 (10%) |
| absent from the voter's graph (below the render floor — pure narrative) | 7 (6%) |
| ≥ 0.70 (body-proximity / kill / vent hard prior) | 4 (3%) |

And the voter's own §4.6 verdict line: **85% read MUST-VOTE** (their max living-target suspicion ≥0.60),
**15% read MUST-SKIP** but the model ejected anyway. Many of the 0.60–0.69 rows sit at **exactly 0.60** — the
minimum gate-crossing value (worked example: seed-0 m2, seed-1 m2 — every convicting voter's ejectee row is
`0.60`). [VERIFIED — `zeroflag_render.py`]

This maps precisely onto the belief fold's non-flag accumulator paths (§3.1): a player reaches `0.60–0.69`
with zero contradiction flags via testimony spread (`0.50 + 0.12 = 0.62`), verbal accusation accumulation
across meetings (`0.55 → 0.60 → 0.65`), or prior-carry + a single-witness inform (`0.55 + 0.05 = 0.60`). The
render ceiling (`0.97`) and self-refuted downgrade — the anti-railroad bounds 14.10 shipped — **only touch
flag/testimony LIFT in the transient channel and deliberately leave these paths alone** (`beliefs.py:141-144`,
`1055-1060`). That is the code-level reason the zero-flag channel was "untouched by design." [VERIFIED —
`abe456` beliefs brief, `beliefs.py`]

A second, smaller sub-mechanism the audit did not name: the **§4.6 under-gate redirect launder**. When a
voter names an under-gate target while someone else is over-gate, `guard_ballot_target_graph` redirects the
ballot to the argmax-rendered eligible candidate (`manager.py:2455-2522`). This routes votes onto whoever the
belief fold ranked highest — often a soft-band prior-carry player. But it is a **minority** of the channel:
only **4 of 31** zero-flag crew mis-ejects had any redirected vote on the ejectee; **27 of 31 are direct**
narrative conviction on a target the model freely chose and whose 0.60–0.69 rendered suspicion let the vote
stand unredirected. [VERIFIED — §11 redirect attribution]

Two worked cases I hand-read (the mission's "read the meetings yourself" — this caught the redirect mechanic
graders' summaries missed):
- **seed-9 m0** [VERIFIED]: zero contradictions in the whole meeting; innocent **p-1 ejected**, game **lost to
  IMPOSTOR_PARITY**. The two crew who *correctly* fingered impostor p-4 did so on a witnessed vent
  (`p-4` really vented `LABS_VENT` at t6 with both accusers in LABS — §2.4), but that private evidence never
  entered the transcript, so p-4 drew only 2 votes; p-1 drew 5 via "Turn 3" narrative momentum (steered by
  impostor p-7) plus two under-gate redirects. Real evidence existed and lost to voice.
- **seed-47 m0** [VERIFIED]: both impostors (p-1, p-9) were correctly flagged but all their flags were "weak
  signal" and stayed under-gate; crew ballots aimed at p-1 were redirected onto the unflagged innocent **p-5**
  while both impostors steered the crowd ("Turn 6 settled it").

### 2.3 The over-damping ledger — impostor share, soft vs hard (NEW, the mission's precondition)

The mission requires the impostor share of zero-flag ejections *before* proposing any damping. At the meeting
level, `zeroflag_render.py` classifies each zero-flag ejection by the **max** rendered suspicion on the
ejectee across convicting voters:

| zero-flag ejection MEETINGS (9p2i baseline 2) | crew mis-eject (31) | impostor catch (16) |
|---|---|---|
| **SOFT-only** (max 0.60–0.69) — neutralizable by a soft-suspicion cap | **24 (77%)** | **6 (38%)** |
| **HARD-backed** (max ≥0.70 — body/kill/vent) — preserved by an exemption | 4 (13%) | **10 (62%)** |
| sub-gate inversion (max < 0.60) | 2 (6%) | 0 |
| no-render (pure narrative) | 1 (3%) | 0 |

- **Impostor share of zero-flag ejections = 16/47 = 34%.** [VERIFIED]
- A rule that keeps *soft-only* suspicion below the 0.60 gate while exempting hard evidence (a same-meeting
  flag, body-proximity, or a witnessed kill/vent) would neutralize **24 of 31** crew mis-ejects and put
  **6 of 16** impostor catches at risk (the other 10 are hard-backed and preserved). A ≈**4:1** favorable
  ratio, measured. [VERIFIED counts]
- **Caveat (honesty):** this is a *static* vote-composition counterfactual, not a re-simulation. Whether a
  meeting still ejects after a cap depends on plurality re-formation (it may SKIP, or redirect to another
  over-gate target). Confirming the real effect requires a re-record (§6). And a prevented impostor eject at
  meeting *m* is not a lost impostor — they can be caught at *m+1*, whereas a mis-ejected crewmate is
  permanently removed. So 6 is an upper bound on the true impostor cost. [INFERRED]

The 4 HARD-backed crew mis-ejects are innocents who drew body-proximity (`0.50 + 0.20 = 0.70`) with zero flags
— a hard-evidence gate would *not* fix these; they need a separate look at whether co-presence with a body
should alone gate-cross (§3.4, option J1b). [VERIFIED]

**Second caveat — the hard/soft split is a rendered-VALUE proxy, not true provenance.** The belief store keeps
only an aggregate `suspicion` scalar per subject (§3.1; `PlayerBelief`), with no record of *which* deltas built
it. I classified "hard-backed" as max rendered suspicion ≥0.70, which is a good proxy (a single body/kill/vent
pin is the fastest way to ≥0.70) but not exact: the soft accumulation path C (`+0.05`/reinforced meeting) can
in principle climb a carried prior into the ≥0.70 band across several meetings, and a hard pin can later mix
with soft deltas. So some of the "4 hard / 10 hard" cells could be soft priors that reached the hard band by
value. The corollary for J1 (§3.4): the actual clamp cannot classify soft-vs-hard from the aggregate scalar
either — it needs **per-subject suspicion provenance** (the composition by source) recorded first, which is why
the staged sketch makes that a shared foundation task (15.0). [VERIFIED store shape; INFERRED proxy error bound]

### 2.4 The "used a vent" hallucination — REFUTED as stated; a smaller firewall question remains

The mission asked me to verify a reported rationale hallucination framed as "'used a vent' — vents do not
exist in the engine." **That premise is literally false**, and verifying it is exactly the "assume nothing"
the charter demands:

- Vents exist as an impostor action (`engine/rules.py`, `actions.py`); the **`LABS` room and `LABS_VENT`
  exist** in the only map (`engine/maps/canonical_1.yaml:159-160, 266-267`); and vent-use is a **witness-gated
  observation** — a co-located witness receives an actor-attributed vent sighting via
  `VentEntered/ExitedEvent` (`observation/service.py:322-368`), plus a room-only `AudibleEvent("vent_use_heard")`
  to same-room players (`service.py:305-316`). [VERIFIED]
- Census of every vent-mentioning free_text/rationale in baseline 2 9p2i (`vent_census.py`): **149 mentions;
  141 (95%) name a player who genuinely vented** somewhere in that game; only **8 (5%)** name a never-venter —
  and those 8 are mostly "near the vent use" *proximity* narratives, not fabricated first-person sightings.
  [VERIFIED]
- Deep-check, seed-9 m0: p-4 (impostor) really vented `LABS_VENT` at t6; **p-5 and p-8 were both in LABS at
  t6**, so "I saw p-4 vent in LABS" is a *grounded witness observation*, not a hallucination. [VERIFIED —
  `replay-seed-9.jsonl` action + position reconstruction]

**Corrected finding:** the defect is not a nonexistent-mechanic hallucination. There are two real, smaller
issues worth a bounded audit in Phase 15: (a) whether models sometimes *narrate* a vent they did not
personally witness (a firewall-adjacency question — the census's necessary-condition test can't confirm the
*speaker* witnessed it), and (b) that a genuine witnessed vent is **private** and often never reaches the
transcript to become a public flag (seed-9), so real evidence fails to aggregate. (b) is itself a
Judgment/aggregation problem, not a Voice one. [VERIFIED premise-refutation; INFERRED residual framing]

### 2.5 Voice residue on the committed bytes (my own metrics)

The mission asked me to measure the current voice residue (template-rationale share ~15% claimed;
within-meeting ballot echo; register variety). `voice_metrics.py` (normalized: player-ids→`player`,
rooms→`room`, ticks/turns/digits collapsed):

| metric (9p2i) | baseline 1 (v3) | baseline 2 (v4) |
|---|---|---|
| within-meeting ballot **echo** (≥0.5 trigram-Jaccard near-dup of another same-meeting ballot) | 23.3% | **8.8%** |
| mean per-meeting max echo-cluster share | 30.2% | 22.1% |
| template **opening** cluster share (top-6 6-token openings) | 16.7% | **9.6%** |
| alibi/contradiction phrasing family (any position) | 53.9% | **35.2%** |
| exact normalized-skeleton echo (top-5 clusters) | 6.5% | **2.0%** |
| distinct normalized skeletons / ballots | 748/891 | 821/844 |
| ballot **ECE** (my recompute — matches eval report exactly) | 0.272 | 0.264 |

[VERIFIED — `voice_metrics.py`; ballot-ECE recompute equals the committed `vote_ballot_ece` to 3 dp.]

**Reading:** v4 roughly *halved* every voice-homogeneity measure — the template collapse the audit reported is
real. But the residue is not zero: ~1 in 11 ballots is still a near-duplicate of another *in the same
meeting*, ~35% still ride the "alibi contradicts sighting" analytic frame, and the register is uniformly that
of a single detached analyst. I could not reproduce the audit's exact `14.8%` "p-N's alibi …" figure (their
marker-stripped clustering is a narrower family than mine); I report my own numbers and note the direction is
identical. The vivid qualitative signature (seed-0 m0: six voters all writing "Turn 2 confirmed p-3's alibi
… contradicts … ADMIN") is the "one analyst times nine" the persona layer targets. [VERIFIED reading;
definitional gap noted]

**Calibration is still poor** — the conviction-confidence question the Judgment side cares about. Committed
baseline-2 accusation-claim ECE is **0.32** (9p2i): bin `[0.6,0.7)` has mean confidence 0.629 but an actual
impostor rate of only **0.330**; bin `[0.7,0.8)` mean 0.706 vs rate **0.289** — large, systematic
overconfidence. Ballot ECE 0.264. [VERIFIED — `abea2` brief + committed `accusation_calibration`.]

---

## 3. JUDGMENT — how zero-flag convictions form (code-cited mechanism)

### 3.1 The belief fold: accumulators, ceilings, and what they deliberately do not touch

Constants (all `agents/memory/beliefs.py`, verified first-hand and in the `abe456` brief):

| source | value | line | persists across meetings? |
|---|---|---|---|
| default prior | 0.50 | :38 | — |
| `BODY_PROXIMITY_SUSPICION_DELTA` | +0.20 | :69 | yes (perception) |
| `VENTING_SUSPICION_DELTA` | +0.50 | :45 | yes (perception) |
| `WITNESSED_KILL_SUSPICION_DELTA` | +1.00 | :48 | yes (perception) |
| `CONTRADICTION_SUSPICION_DELTA` (strong flag lift) | +0.30 | :76 | transient (vote-time) |
| `WEAK_CONTRADICTION_SUSPICION_DELTA` | +0.08 | :80 | transient |
| `MEETING_CONTRADICTION_LIFT_CAP` (the 13.14 `prior+0.3` cap) | 0.30 | :101 | transient cap |
| `ACCUSATION_SUSPICION_DELTA` (accusation received) | +0.05 | :177 | **yes** (reinforced) |
| `TESTIMONY_SPREAD_TWO_VOICE_DELTA` | +0.12 | :256 | transient (pre-vote) |
| `TESTIMONY_SPREAD_CAP_DELTA` (3+ voices) | +0.15 | :278 | transient (pre-vote) |
| `CORROBORATION_SUSPICION_DELTA` (subtractive) | −0.05 | :318 | removes |
| `MEETING_SUSPICION_DECAY_RATE` | 0.25 | :356 | decay toward 0.5 |
| `CONTRADICTION_RENDER_CEIL` | 0.97 | :120 | ceiling on transient lift |

The §4.6 eject gate is **0.60** (`manager.py:138`).

**The zero-flag paths to ≥0.60 (no contradiction flag naming the subject), all verified in the fold code:**
- **A — body proximity alone:** `0.50 + 0.20 = 0.70` ≥ 0.60. Co-presence with a body at discovery
  (`beliefs.py:706`), persists.
- **B — testimony spread:** `0.50 + 0.12 = 0.62` (two voices) or `0.50 + 0.15 = 0.65` (3+); accusation
  *voices*, not flags (`beliefs.py:1152-1153`, `293-315`).
- **C — accusation accumulation across meetings:** `0.50 + 0.05 = 0.55 → 0.60 → 0.65`; reinforced subjects
  skip decay (`beliefs.py:1167`), so a repeatedly-accused innocent climbs monotonically.
- **D — prior-carry + single-witness inform:** carried `0.55 + 0.05 = 0.60` (the single inform is engineered
  to tip only an already-≥0.55 listener, `beliefs.py:240-243`).

**Why 14.10 doesn't touch any of this (the crux):** the certain-guilt ceiling (`0.97`) and the
self-refuted-alibi downgrade apply **only to flag/testimony LIFT in the transient `pre_vote` channel**
(`beliefs.py:1145`, `1055-1060`); the `max(prior, …)` term is an explicit "bound the LIFT, never the prior"
exemption (`beliefs.py:137-141`), and the persistent across-meeting accumulator "stays the allowed channel"
(`beliefs.py:141-144`). So paths A–D — priors and perception pins and *accusation* voices — are precisely the
channels the anti-railroad work leaves alone. [VERIFIED — `abe456` brief]

My §2.2 measurement (82% of convictions at 0.60–0.69) is the empirical fingerprint of paths **B/C/D**; the
`≥0.70` cases (§2.3) are path **A** (and, for impostors, kill/vent pins).

### 3.2 The vote surface: a bare scalar with no provenance

The ballot template (`agents/strategic/prompts/qwen3_32b/vote_ballot.j2`) shows the voter five blocks: private
memory, the accusation chain, contradiction flags (or "(none flagged this meeting)"), **"## Your suspicion of
each player"** as a bare `%.2f` scalar per player, and the §4.6 max/threshold line. Verified facts
(`af73a` brief):

- The suspicion scalar has **no provenance**: `SuspicionEntry` is `(player_id, suspicion, trust)` only
  (`manager.py:472-484`), and the fold *sums* carried prior + this-meeting lift/spread into one number before
  rendering (`manager.py:2011-2057`). **A voter cannot distinguish carried suspicion from fresh evidence.**
- **No evidence-linkage requirement anywhere.** The tally reads only `ballot.confidence` and `ballot.target`
  (`manager.py:1745-1765`); `guard_ballot_target_graph` reads only the bare `entry.suspicion`
  (`manager.py:2486-2498`); `primary_reason_id` is nullable, validated only against this meeting's turn-ids,
  and **consulted by no gate** (`manager.py:1676-1684`, `schemas.py:268`).
- The template **explicitly authorizes** a flagless conviction: the "gut-read" register example — *"Nobody
  vouched for them all meeting and their story kept shifting; that silence is my reason"* — with
  `primary_reason_id: null` (`vote_ballot.j2:114-115, 133, 142-144`).

This is the design surface the zero-flag channel exploits: an unflagged innocent nudged to 0.60 by soft
accumulators shows up as an authoritative-looking `suspicion 0.60`, and the model is invited to convict on it
with no citation. [VERIFIED]

### 3.3 The §4.6 gate + tally + redirect

To EJECT: a strict single-target plurality (no SKIP at the top, no tie) **and** at least one ballot for the
leader with `confidence ≥ 0.60`; the guard additionally forces any confident eject to land on a target whose
rendered `suspicion ≥ 0.60`, redirecting or SKIP-coercing otherwise (`manager.py:1745-1765`, `2455-2522`).
Two distinct `0.60` gates (ballot *confidence* vs rendered *suspicion*) share the constant. [VERIFIED —
`af73a` brief.] The redirect is a minor zero-flag contributor (§2.2: 4/31).

### 3.4 Candidate mechanisms for taming the zero-flag channel

Each with its measured evidence, over-damping analysis, determinism/replay cost, and where it sits
(belief-side / prompt-side / gate-side). All are PROPOSED.

**J1 — Hard-evidence gate lever (belief-side; the measured, highest-leverage option).**
Cap *soft-accumulator-only* rendered suspicion **below** the 0.60 gate, and require a **hard** signal — a
same-meeting contradiction flag on the subject, body-proximity, or a witnessed kill/vent — for a player to
render ≥0.60. Concretely: in the `pre_vote` render, if a subject's suspicion is composed entirely of
testimony-spread + accusation + carried prior (no flag, no perception pin), clamp its rendered value to
`< 0.60` (e.g. `0.59`).
- *Hard prerequisite — evidence provenance (§2.3 caveat 2):* the clamp must know *what built* a subject's
  suspicion, but the belief store keeps only an aggregate `suspicion` scalar (§3.1) — a carried soft prior at
  0.70 is indistinguishable from a body-proximity pin at 0.70. So J1 cannot be implemented on the current
  state: it depends on **recording per-subject suspicion provenance** (a source-tagged decomposition —
  flag-lift / body / kill-vent / testimony-spread / accusation-carry) first. That provenance is the shared
  foundation task 15.0 (§7), which J2's rendering (below) also needs.
- *Measured effect (static, §2.3):* neutralizes **24/31** crew mis-ejects; risks **6/16** impostor catches
  (10 hard-backed preserved) — subject to the value-proxy caveat above; the provenance record makes the split
  exact. ≈4:1 favorable.
- *Over-damping:* the failure mode to watch is genuine-class conversion (the 14.10 canary). Because the
  exemption keeps flags + kill/vent pins fully potent, the primary conversion fuel (R1) is untouched; the
  6 at-risk impostor catches are soft-only and recoverable downstream. Prove it on the committed bytes with
  the analysis-only `allow_substrate_mismatch` override before spending on a re-record.
- *Determinism/replay:* this is a **belief-fold change** → forces a re-record (§6). Ship as a default-OFF
  lever registered in `substrate_flag_snapshot()` / `SUBSTRATE_FLAG_KEYS` (the exact 13.5/14.10 pattern), OFF
  = byte-identical to baseline 2, baseline 3 records it ON.
- *Sub-option J1b:* also downweight **body-proximity-alone** below the gate (`+0.20 → +0.09`, so
  `0.50+0.09=0.59`). Fixes the 4 HARD-backed crew mis-ejects (§2.3) but touches an impostor-detection signal —
  price it separately (body-proximity is legitimately incriminating for the impostor who lingers at their
  kill). Owner call.

**J2 — Provenance-aware, evidence-linked vote surface (prompt-side + gate-side; where Voice and Judgment
meet).**
Two coordinated changes: (a) render the suspicion scalar **with its provenance** (the same source-tagged
decomposition J1 records, foundation task 15.0) — split "carried prior" from "this-meeting evidence," or
annotate rows whose suspicion is soft-only ("0.60 — no flag; carried/soft") — so the model (and a human
reader) can see a bare-carry number for what it is; (b) require an EJECT ballot against a **zero-flag** target
to cite a concrete in-game source, and have the tally/guard **enforce** it (today the citation field is
decorative). This is the direct implementation of the research's load-bearing finding (§5): *a claim counts
toward conviction only if it cites a specific in-game source*.
- **Citation schema must be widened first — the current field cannot cite private evidence (VERIFIED, the C3
  catch).** Today `primary_reason_id: TurnId | None` (`schemas.py:268`) is validated *only* against this
  meeting's transcript turn-ids (`valid_reason_ids = frozenset(turn.turn_id ...)`, `manager.py:1676`), and a
  dangling id is nulled. A witnessed kill/vent lives in the voter's **private** memory, not the transcript, so
  it has no `TurnId` — the seed-9 vent votes correctly carried `primary_reason_id: null`. Enforcing a non-null
  `primary_reason_id` on zero-flag ejects *as-is* would therefore **block** exactly the private hard-evidence
  catches the exemption is meant to protect (an over-damp of correct impostor ejections). J2b must first
  extend the ballot schema with an **observation-citation path** — e.g. a `primary_reason_observation_id`
  (an `ObservationRef` into the voter's reconstructed memory) alongside the turn-id — and a validator for it,
  so "cite a source" admits *both* a transcript turn *and* a private observation. Without that path the gate
  is unsound.
- *Measured target:* the 82% soft-band convictions (§2.2) and the "gut-read null-reason" sanction (§3.2).
- *Over-damping:* with the observation-citation path in place, citation-gating an EJECT does not stop
  convicting flagged impostors (they have flags), witnessed kill/vent (now a citable observation), or a
  transcript-cited catch; the residual risk is a legitimate but *inferential* crew read ("nobody vouched for
  them") that cites nothing — measure how many correct impostor ejections would fail the citation requirement
  before enforcing it (a `zeroflag_render`-style pass restricted to impostor ejections, counting how many have
  *any* citable turn or observation).
- *Determinism/replay:* variant **J2a (prompt-only)** changes rendered prompt bytes but *not* the belief fold
  → a new prompt-set version (v5) and a re-record to take effect, but does **not** retroactively break
  reconstruction of baseline 2. Variant **J2b (gate-side)** — tally/guard requires an over-gate zero-flag
  target to have a cited turn — is a deterministic decision-rule change; it can be a default-OFF lever like
  J1 (it changes recorded ballots/outcomes, so it needs the re-record + stamp).

**J3 — Calibrated, citation-required ballot confidence (prompt-side; research-backed).**
Elicit ballot confidence as a two-field output `{confidence, cited_turn_or_observation}` where the citation
slot is *mandatory* and confidence is verbalized/calibrated (§5 #1, #6, #7). Pairs naturally with J2. Attacks
the 0.32 claim-ECE overconfidence (§2.5) directly. *Cost:* prompt-set version bump + re-record; measured
against ECE and the zero-flag rate.

**J4 — (Cautioned) blunt soft-delta reduction or gate raise.**
Simply shrinking the testimony-spread/accusation deltas or raising the gate above 0.60 would also suppress the
soft band — but bluntly, with no hard-evidence exemption, so it costs impostor conversion one-for-one and
risks the over-damping the 14.10 audit explicitly warned against (§3a: do **not** require ≥2 groups; 54/57
flagged impostor ejections ride exactly one group). **J1's exemption is strictly better** — same crew-side
suppression, hard evidence preserved. Recorded here as the tempting-but-measured-worse option to *not* take.

**Recommended Judgment shape:** **J1 (hard-evidence gate lever) + J2 (provenance-aware, citation-gated
surface)**, composed. J1 removes the soft-band gate-crossings the fold creates; J2 removes the prompt-side
invitation to convict on a bare number and makes conviction cite evidence — the two halves of "voice beating
evidence." Prove both offline on committed bytes, ship behind the default-OFF lever pattern, record baseline 3
with them ON. [PROPOSED]

---

## 4. VOICE — the substrate for personas

### 4.1 Where personas live: a render input, deterministic per seed, schema- and firewall-safe

**The seam (VERIFIED — `a2cfa` loader brief + first-hand read of `loader.py`).** Each of the four prompt
renderers is a keyword-only wrapper with an explicit frozen signature that re-enumerates its kwargs in an
explicit `.render(...)` call (no `**kwargs` passthrough). Adding a render input is a well-worn path — Tasks
7.12 (`fellow_impostor_ids`), 9.9 (`living_ids`), 10.3 (`dead_ids`), 11.2 (`is_impostor`, `is_body_report`)
all added exactly this way: a new keyword arg, defaulted so unmodified templates render **byte-identically**,
guarded in the template on a non-empty value. A **persona** is the same move, in three lockstep layers:
1. Protocol signatures (`ReportPromptRenderer` / `StatementPromptRenderer` / `VotePromptRenderer`,
   `manager.py:697-708, 753-767, 785-796`).
2. Each wrapper's signature **and** its `.render(...)` body (`loader.py:162-386`).
3. The manager render seams (`manager.py:1430-1463, 1550-1558`), sourced from a new
   `MeetingParticipant.persona` field (`manager.py:488`).

**Why it's schema-safe (VERIFIED):** the same-schema invariant is enforced on the **response** side
(`MeetingTurn` / `VoteBallot`, `extra="forbid"`, `schemas.py:49/171/257`), not the templates. A persona is a
render **input**, never an output field, so `extra="forbid"` cannot reject it, and the frozen JSON stays
frozen. Personas shape only `free_text` / `rationale_text` diction — the structured fields (`target`,
`confidence`, `observations`, `claims`) remain schema-locked. [VERIFIED — `a2cfa`, `af73a`]

**Why it stays out of the firewall's way (VERIFIED/INFERRED):** the observation firewall lives in
`rendered_memory` (the per-agent, visibility-gated observation feed). A persona enters the *instruction
preamble* only; it never touches `rendered_memory`. The render inputs already cleanly separate the two, so a
persona is orthogonal to the firewall by construction. [INFERRED from the verified separation]

**Determinism per seed (PROPOSED, matching research #2):** at game setup (where roster roles are seeded,
`orchestrator/seeder.py`), draw personas by **sampling without replacement** — a deterministic
`game_seed`-keyed permutation of the persona-bank indices (a seeded Fisher–Yates shuffle), assigning seat `i`
the `i`-th entry of the shuffled order. This *guarantees* (a) reproducibility — a replay reconstructs the same
nine voices — and (b) disjointness: **no persona is drawn twice in a nine-seat game** (the structural fix for
"one analyst times nine"). Note the naive `bank[hash(game_seed, seat_index) % len(bank)]` does **not**
guarantee (b) — independent per-seat hashes collide (birthday problem), handing two seats the same persona and
re-introducing the very homogeneity we are removing — so the without-replacement/permutation scheme is
load-bearing, and the bank must hold at least the max seat count (≥9). The persona bank is a committed data
file; the assignment is a pure function of the seed, so it is part of provenance but *not* a belief-fold
change (it changes prompt bytes only).

### 4.2 Persona design techniques (from the literature, mapped to a frozen-schema game)

Distinctness is a *pipeline*, not a prompt (persona demographic variables alone explain <10% of output
variance — Hu & Collier, ACL 2024, arXiv:2402.10811). The mapped toolkit (§5 research brief `a24ce`):
- **Structured persona cards + speech-style exemplars** (RoleLLM, arXiv:2310.00746) — a card per seat with
  background + 2–3 in-character utterance exemplars carries diction far better than a one-line label.
- **Disposition mixing** (Peacemaker/Troublemaker, arXiv:2509.23055; Persona Inconstancy, arXiv:2405.03862) —
  spread *contrasting* social dispositions across seats (aggressive accuser, cautious hedger, quiet follower,
  jokester). This preserves behavioral variance **and** resists the premature-consensus / stance-homogenization
  that neutral personas collapse into — directly relevant to the sycophantic zero-flag cascade.
- **Big-Five / trait-vector conditioning** (arXiv:2508.06149) and **decode-time activation steering**
  (arXiv:2511.03738) — numeric register dials; steering acts on hidden states so structured fields are
  untouched (a robustness option if prompt-only voices collapse over long games).
- **Persona-drift instrumentation + re-anchoring** (arXiv:2402.10962) — personas decay over turns; log a
  per-agent drift metric and re-inject the persona header each turn.
- **Verbalized Sampling** (arXiv:2510.01171) — counter RLHF mode collapse by sampling k candidate rationales
  and selecting the most distinctive; attacks the homogenization root cause; schema untouched.
- **Persistent memory / reflection** (Generative Agents, arXiv:2304.03442) — a private memory of prior
  accusations keeps a voice self-consistent across a game.

**Design caution (the unifying thesis, §0):** more distinct + more persuasive voices, *without* the §3 evidence
gate, can make the zero-flag channel **worse** — CW-POR (arXiv:2504.00374) and sycophancy (arXiv:2310.13548;
arXiv:2509.23055) show confident rhetoric overrides truthful peers, and social-deduction benchmarks find
deception outruns detection (WOLF, arXiv:2512.09187; Werewolf Arena, arXiv:2407.13943). Persona work must land
**with or after** J2/J3 evidence-linkage, and its voice metrics (§5) must be watched *alongside* the zero-flag
conviction rate, not in isolation.

### 4.3 Heterogeneous-model casts (models as voices) — the plumbing gap, sized

Owner-deferred to Phase 15 explicitly (phase-14 STATUS banner). The **same-schema invariant is what makes it
possible** (every set parses to the same DTO). What's already there vs missing (VERIFIED — `a1168`, `a75cb`
briefs):

*Already there:* the per-call `model=` override is plumbed end-to-end through the Protocol
(`client.py:157-167`), the Budgeted and Recording wrappers forward it (`budgeted_client.py:326-334`), and
`LLMCallRecord` records per-call `model` **and** `agent_id` (`replay.py:89, 95`); cost rolls up per-model
already (`balance_eval.py:1093-1108`). It is simply **never passed** by any call site.

*Missing (sized as tasks):*
- **R1 — Routing by player id (Small).** Add an `agent_id → model_id` cast map as a construction knob on
  `build_default_meeting_runner → DefaultMeetingRunner → MeetingManager`; resolve at each `complete()`
  (`manager.py:1185-1191, 1597-1603`) from `participant.agent_id` and pass `model=`.
- **R2 — Cross-provider multiplexer (Medium).** If the cast spans providers, `build_default_client` builds one
  provider from one env var (`provider.py:290-352`); need a multiplexing `LLMClient` dispatching by `agent_id`
  to sub-clients, with per-sub-client cost-rate hints.
- **P1/P2 — Per-agent provenance (Medium).** The MANIFEST row flattens `model` and `prompt_versions` to one
  set-unioned string per game, dropping `agent_id` (`_manifest_writer.py:219-224`); `MeetingReplayEntry`
  records one `prompt_versions` per meeting from one global `AILIBI_PROMPT_SET` (`game.py:755-782`). Per-agent
  routing needs a provenance **schema change**: associate model + prompt-set with `agent_id` (a per-agent map
  or per-agent rows), and update MANIFEST rendering + the version-assertion tests.
- **C1/C2 — Cost attribution (Small–Medium).** Add `by_agent` to `GameCostSummary` (`agent_id` already
  recorded); fix the per-prompt-version cost roll-up, which currently attributes the whole game cost to each
  key in the single game-level `prompt_versions` map (`cost_dashboard.py:174-177`).
- **D1/D2 — Determinism (Small–Medium).** Recorded calls append in **completion order**
  (`game.py:583-594`); with mixed-latency models the `llm_calls` order can vary run-to-run — verify every
  consumer keys by `agent_id`/turn-id (not list index) or make recording order-stable. Thread per-agent
  seed/temperature (today one `turn_temperature`/`vote_temperature` for all).

*Replay determinism itself is safe:* replays serve recorded outputs, not fresh calls, so a heterogeneous
recorded game reconstructs byte-identically. [VERIFIED — `a75cb`]

**Sizing verdict:** ~7 tasks, mostly Small/Medium, dominated by the P1/P2 provenance schema change. Value is
"models as voices" (a second axis of voice diversity + a lever on impostor concealment), but it is the
**least-measured** Phase-15 candidate. Recommend deferring behind the measured Judgment + Voice work unless
the owner wants the capability now (§8 Q5).

---

## 5. Research grounding (cited)

Full catalogs are in the workflow briefs; the load-bearing conclusions:

**Persona consistency / anti-collapse** — persona demographic alone <10% of variance (Hu & Collier, ACL 2024,
arXiv:2402.10811); realize voices via cards+exemplars (RoleLLM 2310.00746), disposition mixing (2509.23055),
trait vectors (2508.06149) / activation steering (2511.03738); defend against drift (2402.10962) and RLHF mode
collapse (Verbalized Sampling 2510.01171); persistent memory for identity (Generative Agents 2304.03442);
deterministic disjoint assignment from a persona bank (Persona Hub 2406.20094); survey 2406.01171.

**Dialogue diversity measurement** — offline, deterministic, $0 tier: distinct-n (1510.03055), **cross-speaker
echo / local-context-repetition** (2311.13061; 2112.08657), compression ratio + long-n-gram self-repetition
(2403.00553), n-gram entropy (1809.05972); MTLD (McCarthy & Jarvis 2010; survey 2006.14799), self-BLEU
(1802.01886), copy-from-context coverage/density (1804.11283); heavier tier (pin the encoder/classifier):
embedding cosine diversity (2004.02990 / SBERT 1908.10084), **per-speaker style separability / authorship
attribution** (2405.10150; 2311.07564), Vendi (2210.02410); MAUVE (2102.01454) only for benchmarking.

**Multi-agent debate / persuasion vs evidence** — debate *can* help (2305.14325) but often doesn't beat
self-consistency and mostly amplifies the hardest arguer (2311.17371; 2502.08788); confident-but-wrong agents
override truthful ones (CW-POR 2504.00374); sycophancy is trained-in (2310.13548) and cascades between agents
(2509.23055; 2509.05396); the demonstrated antidotes are a **mandated opposing voice + separate adjudicator**
(2402.06782; 2407.04622) and **per-claim verified citation as the precondition to count** (2503.04830); do
**not** weight votes by raw confidence (2404.09127; 2309.13007; 2509.16839; 2505.19184); in-domain, deception
outruns detection (WOLF 2512.09187; Werewolf Arena 2407.13943; Avalon 2310.01320); persuasiveness rises with
capability independent of correctness (Anthropic, *Measuring Model Persuasiveness*).

**Calibration / evidence-linkage** — verbalized confidence beats token-prob calibration (2305.14975) but is
overconfident (2306.13063); belief-side interlocks P(True) (2207.05221) and semantic entropy (2302.09664);
citation-grounded generation with citation recall/precision (ALCE 2305.14627) and verified-quote + abstention
(GopherCite 2203.11147); selective prediction via sampling repetition (2305.14613); threshold-set-by-reliability
(smoothECE 2309.12236); and the **anti-momentum counterfactual** — remove the cited turn; if the verdict is
unchanged, it rode narrative momentum, so veto (unfaithful-CoT 2305.04388; 2307.13702; anchoring 2412.06593).
This last is the sharpest research instrument for the zero-flag channel, though expensive/replay-hard (§8 Q7).

---

## 6. Re-record economics (why a belief-fold change forces a re-record)

VERIFIED (`a75cb` provenance brief). The chain: (a) at record time the vote-ballot prompt bytes are rendered
from the belief-derived suspicion graph and frozen into `llm_calls[].prompt`, with the real model's answer in
`response_text` (LLM outputs are **replayed, not recomputed** — `replay.py:22-25`). (b) The loader
reconstructs meeting-open beliefs by **re-running `beliefs.py`** against the recorded ticks
(`replay_loader.py:1065-1128`), mirroring the live fold. (c) The two `state_hash` gates hash only the engine
`WorldState`, which is **substrate/belief-blind** (`replay_loader.py:353-355, 943-949, 1030-1037`). So a
`beliefs.py` change makes the loader silently re-derive a *different* suspicion graph that diverges from the
committed prompt bytes — and no state-hash catches it. The **only** guard is the substrate stamp
(`_assert_substrate_matches`, `replay_loader.py:401-425`).

Consequences for the mechanisms:
- **J1 / J2b / J4** (belief-fold or decision-rule changes): must be a default-OFF lever registered in the
  stamp machinery (OFF = byte-identical to baseline 2; committed replays keep reconstructing), then baseline 3
  records it ON. This is exactly the 13.5 / 14.10 pattern.
- **J2a / J3 / persona prompts** (prompt-only changes): change rendered bytes but not the fold, so they do
  **not** retroactively break baseline 2's reconstruction; they need a new prompt-set version and a re-record
  to *take effect*.
- Per-agent model routing (R/P/C/D): replay-safe (recorded outputs), but P1/P2 change the provenance schema.

Net: Phase 15's belief-side and prompt-side changes all converge on **one atomic re-record (baseline 3)** —
the same shape as 14.12 — proven offline on the committed bytes first (the `allow_substrate_mismatch`
analysis-only override, `replay_loader.py:412-422`), then spent once.

---

## 7. Staged phase sketch

Task contracts below mirror `tasks/phase-14.md`'s format (`### Task N.M — title`, `Branch` / `Depends on` /
`Section refs` / `Complexity`, a contract prose paragraph, `Files in scope` / `Files NOT in scope` /
`Definition of done` with the fixed CI tail / `Implementation hint` / `Integration risk` / `Ready-to-paste
prompt`). They are sketches to be filled at phase authoring time, sized by file footprint like the 14.x set.

### Proposed task set

- **15.1 — Voice & Judgment measurement harness (analysis-only, $0).** *Depends on:* none. *Complexity:*
  Medium. Add to `eval/` (and wire into the rubric loop): (a) **zero-flag conviction rate** — crew vs
  impostor, and the soft-band-only vs hard-backed split (§2.2/§2.3), extending the existing hooks
  `rubric_score.py:147` (R3 "carry-driven ejections (zero-contradiction)") and `:771` (D2 "evidence-free
  conviction"); (b) **evidence-linkage rate** — share of ejections whose deciding ballots cite a
  turn/flag; (c) **voice metrics** — within-meeting cross-speaker echo, compression ratio, distinct-n, MTLD,
  template-skeleton share (the §2.5 metrics, promoted from scratch scripts); (d) a nightly heavier tier —
  per-speaker style separability + embedding cosine diversity (pinned encoder for determinism). *Not in
  scope:* any belief-fold or prompt change (this task only measures). This is the foundation so every later
  fix is specified against a number, per project discipline.

- **15.0 — Shared foundation: suspicion provenance + render-input plumbing (byte-identical).** *Depends on:*
  15.1. *Complexity:* Integration. This is the seam **both** the Judgment surface (15.3) and the Voice persona
  layer (15.4) need, landed once so they don't collide (the C4/C5 review catch). Two parts, both proven
  byte-identical to baseline 2: (a) **record per-subject suspicion provenance** — a source-tagged
  decomposition (flag-lift / body-proximity / kill-vent pin / testimony-spread / accusation-carry) recorded
  *alongside* the aggregate `suspicion` scalar in `BeliefState` / `PlayerBelief`, **without changing the scalar
  value or any rendered byte** (so it reconstructs baseline 2 exactly). This is what J1's clamp classifies on
  and what J2's surface renders — neither can be built on today's aggregate-only scalar (§3.1, §2.3 caveat 2).
  (b) **Widen the render-input contract once** — add the `persona` and `suspicion_provenance` render kwargs
  through the 3-layer contract (Protocol sigs `manager.py:697-796`, the four wrapper sigs + `.render` bodies
  `loader.py:162-386`, the manager render seams `manager.py:1430-1558`), plus the `MeetingParticipant.persona`
  and `SuspicionEntry` provenance fields — all **inert/defaulted so no template references them yet** and every
  render stays byte-identical. *Files in scope:* `agents/memory/beliefs.py` + `agents/memory/store.py`
  (provenance record), `agents/strategic/prompts/loader.py` + `meetings/manager.py` (the contract widening +
  the two DTO fields), tests. *Not in scope:* `orchestrator/replay.py` levers, any template text, any gate
  logic (those are 15.2–15.5). *DoD:* `verify_samples.sh` bare reconstructs baseline 2 byte-identically (the
  provenance record + inert kwargs change nothing rendered); the CI tail. *Why it de-conflicts the tracks:*
  after 15.0 the render-contract functions in `loader.py`/`manager.py` are already widened, so 15.3 edits only
  `vote_ballot.j2` + the gate and 15.4 edits only the persona assignment + template text — no shared function.

- **15.2 — Hard-evidence gate lever (J1; default-OFF).** *Depends on:* 15.1, **15.0** (uses its per-subject
  provenance to classify soft-only vs hard-backed — the clamp cannot read that off the aggregate scalar).
  *Complexity:* Integration. Cap soft-accumulator-only rendered suspicion below the 0.60 gate, exempting flags
  + body-proximity + witnessed kill/vent, behind a new `*_enabled()` resolver registered in
  `substrate_flag_snapshot()`. *Files in scope:* `agents/memory/beliefs.py` (the pre-vote render clamp, reading
  15.0's provenance), `orchestrator/replay.py` (lever registration), `.env.example`, **`scripts/refresh_samples.sh`
  + `tests/scripts/` (wire the new lever ON for the baseline-3 record — see below), `tests/agents/test_beliefs.py`,
  `tests/orchestrator/test_replay.py`. *Not in scope:* `replays/samples/` (re-record is 15.7), prompt sets, the
  detectors. *Recording preflight (the C6 catch):* since 14.12 the refresh/verify scripts assume every
  substrate lever is unconditional and export **no** lever env (`refresh_samples.sh:270-275`); a new default-OFF
  lever must be exported ON for the baseline-3 recording, or the operator silently records it OFF and only finds
  out from the stamped MANIFEST afterward. So this task must add the lever's `AILIBI_*` export to
  `refresh_samples.sh` (and a test asserting the stamp comes out ON) — or, mirroring 14.12, graduate the lever
  to unconditional-ON *at* 15.7. *DoD (measured):* OFF = byte-identical to baseline 2; offline over committed
  bytes (via `allow_substrate_mismatch`) the 24 soft-only crew mis-ejects fall below gate while the 10
  hard-backed impostor catches still gate-cross (the over-damping canary); the record preflight stamps the
  lever ON; the CI tail. *Integration risk:* over-damping genuine conversion — watch the 6 soft-only impostor
  catches; do not weaken the detectors.

- **15.3 — Provenance-aware, citation-gated vote surface (J2, +optionally J3).** *Depends on:* 15.1, **15.0**
  (consumes its render-input seam + suspicion provenance); **J2b parallelism is variant-dependent** (below).
  *Complexity:* Integration. (a, J2a) Render the provenance 15.0 records in `vote_ballot.j2` (split carried vs
  same-meeting; annotate soft-only rows) — no signature edits, since 15.0 already widened the contract.
  (b, J2b gate-side) require a zero-flag EJECT ballot to **cite a concrete in-game source** and enforce it in
  the tally/guard behind a default-OFF lever. **Citation-schema extension is mandatory for J2b (the C3 catch):**
  today `primary_reason_id: TurnId` is validated only against transcript turn-ids (`manager.py:1676`), so a
  **private** witnessed kill/vent (no transcript turn) cannot be cited and a naive non-null gate would block
  the very hard-evidence catches the exemption protects (seed-9's vent votes carried `reason_id: null`). J2b
  must add an **observation-citation path** — a `primary_reason_observation_id` (`ObservationRef` into the
  voter's reconstructed memory) + validator — so "cite a source" admits a transcript turn *or* a private
  observation. *Files in scope:* prompt sets (a v5 bump), `meetings/manager.py` (surface + optional gate),
  `meetings/schemas.py` (the observation-citation field/validator, J2b), `vote_ballot.j2`; **plus
  `orchestrator/replay.py` + `.env.example` + `tests/orchestrator/test_replay.py` ONLY if J2b (gate-side lever)
  is taken.** *Parallelism caveat:* J2a touches no belief/gate/replay file and runs parallel to 15.2. But the
  J2b lever registration edits the **same** `_TOGGLEABLE_LEVER_RESOLVERS` / `substrate_flag_snapshot()` seam in
  `orchestrator/replay.py` that 15.2 reserves — a same-function collision (the reason 14.10 stayed sequential
  behind 14.9). So if J2b is in scope, **either serialize 15.3 behind 15.2, or register both levers in one
  shared `15.2r` task both depend on.** *DoD:* the observation-citation path lands *before* any enforcement;
  measure how many *correct impostor* ejections would fail the citation requirement (must be near-zero,
  counting either a citable turn or a citable observation); the CI tail.

- **15.4 — Persona registry + deterministic assignment.** *Depends on:* 15.1, **15.0** (the
  `MeetingParticipant.persona` field + render-input seam already exist, inert). *Complexity:* Integration.
  A committed persona bank + the deterministic `game_seed`-keyed permutation (sampling without replacement,
  §4.1) assignment at setup. Because 15.0 owns the render-contract widening, this task no longer touches the
  `loader.py`/`manager.py` render signatures — it is now **genuinely disjoint** from 15.3. *Files in scope:*
  `orchestrator/game.py` / `seeder.py` (the assignment that fills `participant.persona`), a `personas/` data
  file, tests. *Not in scope:* the render-contract signatures (15.0), the templates' persona *text* (15.5).

- **15.5 — Persona-conditioned prompt additions (v5) + A/B on voice metrics.** *Depends on:* 15.1, 15.4.
  *Complexity:* Integration. Author disposition-varied persona cards + speech-style exemplars into each set's
  preamble (guarded, byte-identical when persona empty); A/B new-vs-pinned on the same model, scored on the
  15.1 voice metrics **and** the zero-flag conviction rate (the anti-collapse guard: a louder voice must not
  raise zero-flag convictions). *Files in scope:* prompt sets; **plus `orchestrator/game.py` — the
  `PROMPT_VERSION_SETS` registry bump `qwen3_32b` v4 → v5 (the C7 catch).** Replay provenance is stamped from
  that static registry (`prompt_versions_for_set`, `game.py:308-314`), *not* derived from the `.j2` files, so
  editing templates without the one-line registry bump would render v5 text while `MeetingReplayEntry.prompt_versions`
  + the MANIFEST still report v4 — breaking provenance and the version-assertion tests (14.11 bumped the
  registry for exactly this reason). *Ready-to-paste prompt* per set.

- **15.6 — (Deferred/optional) Heterogeneous-model routing.** *Depends on:* — . *Complexity:* Integration
  (large). R1/R2 routing + P1/P2 per-agent provenance schema + C1/C2 cost + D1/D2 determinism (§4.3). Only if
  the owner wants the capability in Phase 15; least-measured value.

- **15.7 — Baseline 3: atomic re-record + phase close.** *Depends on:* 15.2, 15.3, 15.5 (and 15.6 if taken).
  *Complexity:* Integration (operator-run / spend gate). Re-record both sets with the chosen levers exported ON
  (verify the `refresh_samples.sh` preflight from 15.2 stamps every new lever ON *before* spending — the C6
  guard) + v5 persona prompts (registry bumped, 15.5), HARD validity gate + bare reconstruction, re-measure the
  §2 channel split and §2.5 voice metrics as the close finding. Same shape as 14.12.

### Sequencing options

- **Option A — Judgment-first.** 15.1 → 15.0 → 15.2 → 15.3 → (15.4 → 15.5) → 15.7. *Rationale:* fix the
  measured, highest-value defect first; the evidence gate is in place before louder voices land.
- **Option B — Voice-first.** 15.1 → 15.0 → 15.4 → 15.5 → (15.2/15.3) → 15.7. *Rationale:* personas may
  themselves shift the channel (disposition variety reduces sycophantic cascade) — measure that before
  belief-side surgery. *Risk:* ships a louder voice channel before the evidence gate (the §0 thesis warns
  against this).
- **Option C — Shared foundation, then parallel disjoint tracks (RECOMMENDED).** 15.1 (measurement) → 15.0
  (the shared provenance + render-input foundation, landed once so the tracks don't collide on the
  render-contract functions — the C4 fix); *then* the **Judgment track** and the **Voice track** (15.4 → 15.5)
  run in parallel, now genuinely disjoint (`beliefs.py` / gate / `orchestrator/replay.py` / `schemas.py` vs
  the persona assignment + prompt text — 15.0 already absorbed the shared `loader.py`/`manager.py` seam).
  *Within* the Judgment track, 15.2 and 15.3's J2a surface may run parallel, but 15.3's J2b gate-side lever
  shares the `orchestrator/replay.py` registration seam with 15.2, so it **serializes behind 15.2** (or both
  depend on a shared `15.2r` lever-registration task). 15.5 follows 15.4. Converge on the single re-record
  15.7. Defer 15.6.

**Recommendation: Option C, with the evidence-linkage bound (15.3) required to land in the same re-record as
the persona prompts (15.5).** This honors the mission's "design them together," gets the measured 4:1 Judgment
win (15.2) moving immediately, and structurally prevents shipping personas without the evidence gate the
persuasion literature says they need. The whole phase costs **one** atomic re-record (baseline 3), proven
offline first.

DAG (shared foundation + the two same-function seams made explicit): `15.1 → 15.0 → { [ 15.2 → 15.3(J2b) ]  ∥
[ 15.4 → 15.5 ] } → 15.7`. 15.3's J2a surface may instead run `∥ 15.2`; only its gate-side lever (J2b) is
order-constrained behind 15.2. 15.0 is what makes the `[Judgment] ∥ [Voice]` split real — without it, 15.3 and
15.4 would both edit the `loader.py`/`manager.py` render contract (the C4 collision). (15.6 deferred.)

---

## 8. Open questions for the owner

1. **Persona scope & shape.** Full persona cards (background + exemplars + disposition) per seat, or
   lightweight disposition tags only to start? Assignment source = a `game_seed`-keyed permutation (sampling
   without replacement, §4.1) over a committed bank (my proposal) — acceptable as provenance? Bank size (must
   be ≥ the max seat count) / who authors it?
2. **Sequencing the two faces.** Do you accept the §0 thesis that a persona layer without an evidence gate
   risks *worsening* the zero-flag channel — i.e. that 15.3 (evidence-linkage) must land with/before 15.5
   (persona text)? Or ship personas first and measure?
3. **Hard-evidence gate exemptions (J1).** Is **body-proximity** "hard evidence" (exempt, leaving 4 crew
   mis-ejects unfixed) or should body-proximity-alone be downweighted below the gate (J1b — fixes them but
   touches an impostor-detection signal)?
4. **Evidence-linkage placement (J2).** Belief-side (fold change), prompt-side (v5), or gate-side (lever)?
   Appetite for enforcing `primary_reason_id` on zero-flag EJECT ballots (today decorative)?
5. **Heterogeneous models (15.6).** In-scope for Phase 15 or deferred again? It is the largest plumbing and the
   least-measured value; the same-schema invariant already supports it.
6. **Re-record budget.** One combined baseline-3 re-record for all chosen levers + persona prompts (my
   proposal), or staged? (14.12 was ~3.85h wall on 2 Featherless workers.)
7. **Calibration ambition (J3).** Given claim-ECE 0.32, is a calibrated/citation-required confidence
   elicitation worth a prompt-set redesign, or out of Phase-15 scope? And is the research-favored
   **counterfactual momentum veto** (remove-the-cited-turn) worth prototyping despite its extra-LLM-call cost
   and replay-determinism friction?
8. **The vent/firewall finding.** The mission's "vents don't exist" premise is refuted (§2.4). Do you want a
   bounded firewall audit of vent *attribution* (witnessed vs narrated) as a Phase-15 task, and treatment of
   the private-evidence-fails-to-aggregate problem (seed-9) — which is a Judgment/aggregation issue, not Voice?

---

## 9. What I verified vs assumed (summary ledger)

- **VERIFIED from committed bytes:** the channel split and its delta (§2.1); the zero-flag decomposition and
  the 82% soft-band figure (§2.2); the over-damping ledger incl. 34% impostor share and the 24-vs-6 meeting
  split (§2.3); the vent-premise refutation (§2.4); the voice-residue metrics and ballot-ECE reproduction
  (§2.5); the belief-fold constants and zero-flag paths (§3.1); the bare-scalar vote surface and absence of
  evidence-linkage (§3.2); the gate/tally/redirect (§3.3); the persona render seam and schema/firewall safety
  (§4.1); the heterogeneous-model plumbing gap (§4.3); the re-record mechanism (§6).
- **INFERRED:** downstream recoverability of at-risk impostor catches (§2.3); the persona-firewall
  orthogonality (§4.1); the unifying "voice beats evidence, so personas need the gate" thesis (§0/§4.2) — from
  verified measurements + cited research.
- **PROPOSED:** all mechanisms J1–J4, the metrics, the staged sketch, sequencing, and recommendation.
- **Definitional gap noted, not hidden:** I could not reproduce the audit's exact `14.8%` template figure (a
  narrower marker-stripped family than my clustering); I report my own numbers with the same direction (§2.5).

---

## 10. Bottom line

The close audit's residual is real and reproduces exactly: the zero-flag / voice-driven channel now dominates
crew mis-ejects (31 of 56), and it is **82% soft-band gate-crossings** on a **bare, unprovenanced suspicion
scalar** that **no gate requires to cite evidence**. The measured, favorable move is a **hard-evidence gate
lever** (≈24 crew mis-ejects prevented : 6 impostor catches at risk, 10 preserved) composed with a
**provenance-aware, citation-gated vote surface** — the Judgment face. The Voice face is a clean render-input
persona layer (schema- and firewall-safe, deterministic per seed) whose job is distinct voices — but the
persuasion literature and the game's own bytes say a persona layer must ship **with** the evidence gate, or it
will make "voice beating evidence" worse. Both faces converge on one atomic baseline-3 re-record, proven
offline first. That is the phase.

---

## 11. Method & reproduction (all $0, offline, committed bytes)

Scratch scripts (kept out of the repo; runnable against the committed sets and the baseline-1 eval report
extracted from git `bb9d1b3`):

- **`channel_split.py`** — folds each set's `tournament-eval-report.json`: per EJECTED meeting, joins the
  authoritative `roles`, counts `contradictions[].subjects ∋ ejectee` as the flag test, splits crew/impostor
  ejections into flag-driven vs zero-flag. Reproduces `vote_correctness` totals (122/118 ejections) and the
  audit's split (crew 31/22 → 25/31; impostor zero-flag 12 → 16) exactly; cross-checked by an independent
  recompute from the raw `replay-seed-*.jsonl` `contradictions` (identical).
- **`zeroflag_render.py`** — parses the recorded vote-ballot prompt (`llm_calls[].prompt`) for each convicting
  voter, extracts the ejectee's rendered `suspicion 0.NN` and the "maximum suspicion … skip threshold" verdict
  line, and buckets by soft-band (0.60–0.69) / hard (≥0.70) / sub-gate / absent — per deciding vote and per
  meeting (max over voters). Produces the 82% and the 24-vs-6 splits.
- **`voice_metrics.py`** — normalized-rationale metrics (within-meeting trigram-Jaccard echo, template-opening
  and skeleton clusters, distinct-2/TTR) and a ballot-ECE recompute that matches the committed
  `vote_ballot_ece` to 3 dp on both baselines (validating the method), plus the alibi/contradiction family.
- **`vent_census.py`** — reconstructs each game's vent actions (`vent_id → room` from `canonical_1.yaml`) and
  positions from move actions; censuses every vent-mentioning free_text/rationale and tests whether the named
  player ever vented (necessary-condition groundedness). 141/149 grounded; 8 name a never-venter.
- **`pp.py`** — full-meeting pretty-printer (transcript turns + observations + claims + contradictions +
  ballots + roles) used for the seed-0 / seed-9 / seed-47 hand-reads.

Belief-fold and gate reproduction follow the 14.8 method: reconstruct meeting-open beliefs via the loader
memory walk, fold with `apply_contradiction_rule` + `apply_meeting_evidence_rules(phase="pre_vote")` + the
13.14 joint cap, compare against the recorded vote-prompt rows; the analysis-only `allow_substrate_mismatch`
override is the escape hatch for lever counterfactuals. Source line citations throughout are into HEAD
(`8304e5b`).
