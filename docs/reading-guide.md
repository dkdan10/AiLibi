# Reading guide — the outsider's five minutes

You have five minutes and no context. This file is the map: what the project is,
which numbers are real and where they are committed, what to watch, what the
corpus does and does not demonstrate, what the audit idiom means, and which
three audits to read first.

**Every number below carries the committed path that owns it.** Measurements are
cited; judgments are labeled. That is the corpus's own convention
(`audits/audit-phase-19-input-claude.md` header: `[VERIFIED]` = ran or read the
artifact directly, `[JUDGMENT]` = inference, labeled as such). Where this guide
summarizes, the cited file wins.

The route: [README](../README.md) → this guide → the demo (§2) → the three
audits (§5). The glossary (§4) sits between them on purpose.

---

## 1. The meta-story

AiLibi is two things: a deterministic social-deduction simulator, and an
experiment in agent-built software. The loop never varies. A human authors a
task contract in `tasks/phase-N.md` — branch, dependencies, files in and out of
scope, definition of done. `scripts/generate_prompts.py` turns it into a
paste-ready prompt byte-mirrored from that contract and refuses to drift from
it. An AI coding agent implements exactly that contract in a fresh checkout and
opens a PR. CI enforces the architecture instead of trusting it; a human reviews
the rest ([README](../README.md) §"How this is being built").

Enforcement is four `import-linter` contracts, `mypy --strict` repo-wide, a
recursive observation-leak sweep over Hypothesis-generated games, and
byte-identical replay determinism (`docs/architecture.md` §"Enforced
boundaries"). The load-bearing one is the **observation firewall**: `agents/`
cannot import `engine/`, directly or transitively — an agent physically cannot
read the hidden state it is supposed to deduce.

### The numbers worth knowing

| Claim | Figure | Committed source |
|---|---|---|
| Agent-authored PRs, each merged green through the same gate | 300+ (deliberately not re-pinned by hand — the live count is on GitHub) | [README](../README.md) §"What this is" |
| Observation-firewall violations, all phases | zero | [README](../README.md) §"What this is"; enforcement in `docs/architecture.md` §"Enforced boundaries" |
| Gate at the Phase-19 chartering commit | 4,531 passed / 20 skipped / 3 xfailed | `tasks/phase-19.md` STATUS line; re-run from a cold clone in `audits/audit-phase-19-input-claude.md` §0 |
| Committed sample replays that reconstruct byte-identically | 100 of 100 | `scripts/verify_samples.sh`; `audits/audit-phase-19-input-claude.md` §0 |
| Impostor win rate, committed samples | 34% (4p1i), 30% (9p2i) | `replays/samples/{4p1i,9p2i}/MANIFEST.md`; the README's copy of both rates is re-derived from those manifests on every test run by `scripts/check_doc_facts.py` |
| Eject ballots carrying a valid citation — a turn or an observation id (9p2i) | 520 / 520, zero dangling | `tests/eval/test_vj_instruments.py::test_9p2i_citation_compliance_pins`; `audits/audit-phase-19-triage.md` §2 row 11 |
| Impostor ballots cast against a partner (9p2i) | 0 of 245 — meeting-layer enforced, see §3 | `audits/audit-phase-19-input-claude.md` §5.3; the guard is `meetings/manager.py::coerce_teammate_ballot_to_skip` |
| Correct 9p ejections riding an ejectee-specific vent sighting | 68 / 78 = 87% | `audits/audit-phase-19-triage.md` §8 row 3 (three independent parses agree) |
| Pre-registered emergence rulings demonstrated, Phase 18 | 0 of 14 | `audits/audit-phase-18-close.md` title and `:719`; derived cell by cell in `audits/audit-phase-18-flip-emergence.md` |
| Learned movers that became the default | none — NO-FLIP twice | `audits/audit-phase-17-close.md`, `audits/audit-phase-18-close.md` |

### The honesty culture — the strongest single asset

Three habits, all visible in the bytes and all defined in §4: bars and
instruments are **pre-registered** before the measurement that judges them
(`audits/audit-phase-18-baseline-6.md` §0); a measurement that misses its bar is
recorded as a **finding, not a failure**, and the phase closes on it rather than
moving the goalposts (`audits/audit-phase-18-close.md` §6 — Phase 18 published
four learned arms that each beat the scripted baseline on wins and promoted
none of them to the default; the incumbent champion stays opt-in and unswapped,
`:38-39`); and records are corrected by additive dated **errata**, never in-place
rewrites (`training/reports/report-finalist-eval.md` §18).

The sharpest demonstration: two independent external audits were commissioned
against the same tree, reconciled row by row in
`audits/audit-phase-19-triage.md`, and the reconciliation **refuted a claim from
one of its own source audits** rather than absorbing it (§8 row 19 — a headline
`0.9375` labeled "decision accuracy" is in fact conversion-label accuracy; the
composed decision figure is `0.8646`).

---

## 2. The demo path — what to run, what to watch

```bash
git clone --filter=blob:none https://github.com/dkdan10/AiLibi.git && cd AiLibi
bash scripts/setup_env.sh      # one-time: Python deps + npm ci in frontend/
bash scripts/run_spectator.sh  # API + UI, opens http://localhost:5173
```

`--filter=blob:none` is the fast path: a blobless partial clone pulls file
contents on demand, so you download roughly the 256 MiB the working tree needs
rather than every version of every blob in the history. **The honest caveat:** a
full-history clone stays heavy. Task 19.22 moved the Phase-18 co-evolution bytes
no test reads onto a pinned evidence commit (a 28% smaller tracked working tree)
but rewrote no history, so a plain `git clone` still pays for them, and will until
someone deliberately rewrites history — which invalidates every existing clone
and every commit sha these audits cite, and is not scheduled.
[docs/artifacts.md](artifacts.md) is the retention rule; `scripts/fetch_evidence.sh`
restores the moved bytes by their pinned sha.

The served default is the 9-player / 2-impostor set — the one with meetings,
suspicion arcs and a scored highlight reel (`api/replay_loader.py::DEFAULT_SET`,
pinned by `tests/api/test_sets.py::test_default_set_is_the_curated_9p2i_set`).
The 4-player set is a fast technical fixture: median 12 ticks, at most one
meeting per game, 23 of 50 games decided by the task timer
(`frontend/src/components/ReplayPicker.tsx`). On a first visit the guided tour
opens the head of the curated list below
(`frontend/src/components/GuidedTour.tsx`).

**The featured path** is hand-curated, not scored: the interestingness rubric is
an internal pacing heuristic that inverts the human-interest tails, so this
order is editorial (`frontend/src/components/ReplayPicker.tsx`,
`FEATURED_GAMES` — the list this table mirrors exactly, pinned by
`tests/api/test_sets.py::test_featured_seeds_exist_in_their_committed_sets`).
The labels are the committed blurbs, deliberately spoiler-free; §5's audits
carry the answers.

| # | Set / seed | Why watch |
|---|---|---|
| 1 | 9p2i seed 2 | Four meetings, four acts: a cold open, a case that nearly lands, and a last meeting that turns on one piece of hard evidence. |
| 2 | 9p2i seed 17 | An impostor pair builds a fabricated sighting against a truthful vent witness — watch whose testimony the engine stamps “verified”. |
| 3 | 9p2i seed 23 | A sighting that is factually true but provenance-impossible: the flag fires, and nothing asks whether the observer could have seen it. |
| 4 | 9p2i seed 8 | The corpus's most contested endgame — and the game the rubric ranks 45th of 50. Read the last ballots against what each voter knew. |
| 5 | 4p1i seed 29 | One alibi in the only meeting reads completely differently the second time through — the most Among-Us moment in the corpus. |
| 6 | 4p1i seed 2 | The emergency button, pressed with no body ever found: the table has to argue from absence alone. |
| 7 | 4p1i seed 41 | The one meeting in the corpus an LLM tie-break decided rather than the flags — two flags of equal weight pointing opposite ways. |

Seeds 17, 23 and 41 are the exhibits the audits traced case by case. Watch them
first, then read §5.2 of the Claude input audit and see whether you agree.

One qualification on blurb #2, whose wording is reproduced verbatim from the
committed list: the "verified" stamp is applied by the **vote-ballot prompt**
("Each flag below is VERIFIED evidence" —
`agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:100`), over a flag minted
in `meetings/transcript.py`. The engine certifies the vent *observation*
underneath a `vent_sighting` flag; it never certifies the fabricated testimony
that game turns on. That gap is the first limit in §3, and it is most of why
seed 17 is worth watching.

Two claims you can check yourself, offline and free: the run-twice determinism
demo and `bash scripts/verify_samples.sh`, both in the README's
"Reproduce a game". Its "Three reproducibility scopes" states exactly which
determinism claims those support and which they do not — cross-platform
optimizer portability is designed for, not confirmed. Do not upgrade the claim.

---

## 3. What the corpus demonstrates — and what it does not

Three capabilities get conflated in projects like this one. Keep them apart.

**Evidence-processing: demonstrated.** Deliberation is typed, and every one of
the 520 eject ballots in the 9p2i samples carries a *valid* citation — a
transcript turn or an observation id, resolving to a real line the voter could
see. The committed instrument splits it: 478 turn citations and 156 observation
citations, zero dangling on either channel, compliance 1.000
(`tests/eval/test_vj_instruments.py::test_9p2i_citation_compliance_pins`;
hallucinated ids nulled behind audit markers,
`audits/audit-phase-19-input-claude.md` §5.3).

**Deception: demonstrated, and the strongest capability on display.**
Coordinated fabricated alibis built by reading the transcript, strategic
truth-telling at parity, verbal bussing of a caught partner while the ballot
skips (`audits/audit-phase-19-input-claude.md` §5.3).

One number in that section needs its guard stated: across 245 impostor ballots,
zero votes against a partner. A **betrayal vote is not available to the model** —
`meetings/manager.py::coerce_teammate_ballot_to_skip` deterministically rewrites
any ballot targeting a fellow impostor to SKIP, so the zero is the teammate
firewall holding, not a capability the model demonstrated (the audits say so:
"the teammate firewall held perfectly, and within it the models produce genuine
variety"). What the committed bytes add is that in this set the guard never had
to fire: it stamps `[teammate target … coerced to SKIP]` into the rationale
whenever it does, and `replays/samples/9p2i/` carries zero such markers — while
`replays/ml_corpus/9p2i/` carries 4, across 4 of its 150 games
(`replays/ml_corpus/README.md:69`). Read the zero as enforcement plus restraint,
never as restraint alone.

**General social deduction: NOT demonstrated.** This is the qualification the
project's credibility rests on volunteering. A *flag* is a contradiction the
**meeting layer** detects across the transcript and shows to the voters
(`meetings/transcript.py::detect_contradictions` — not the engine); a
`vent_sighting` flag is the one class only an impostor can produce, because it
rests on an engine-certified observation of a vent. **87% of
correct 9p ejections ride an ejectee-specific vent sighting; ~30–39%
otherwise.** The cross-tab, over all 165 committed 9p2i meetings, reproduced by
three independent parses (`audits/audit-phase-19-triage.md` §8 row 3;
`audits/audit-phase-19-input-claude.md` §5.1):

| Meeting contains a `vent_sighting` flag | impostor ejected | innocent ejected |
|---|---|---|
| yes (70 meetings) | 68 | 2 |
| no (95 meetings) | 10 | 21 |

A vent sighting is hard, impostor-only evidence the *engine* certifies and the
scripted mover donates by venting in witnessed conditions. Without one, ejection
accuracy is roughly chance and innocents go down 2:1. The audits' summary: the
system demonstrates LLM evidence-processing of engine-certified facts, plus real
deception, on top of a conviction engine that is substantially deterministic —
"conviction engine" meaning the flag → ballot → tally pipeline in `meetings/`,
not the `engine/` package.

Two limits belong in the same breath:

- **The flag doctrine convicts innocents.** An `alibi_vs_sighting` flag
  juxtaposes two *unverified* model-authored statements and is nonetheless
  labeled "VERIFIED evidence" to the voters; 40% of directional flag subjects in
  9p2i are innocents (75/186), and four injustice classes were traced case by
  case (`audits/audit-phase-19-input-claude.md` §5.2; both flagship exhibits
  re-verified at `audits/audit-phase-19-triage.md` §2 row 9).
- **Scaffold shows through.** ~5% of 9p2i turns ship a diagnostic husk in
  player-visible text (53/971 sampled turns), and 21.3% of 9p impostor kill
  submissions are engine-rejected (48/225) — a mover-quality signal no eval
  report surfaces (`audits/audit-phase-19-triage.md` §8 rows 12–13). Response
  shape is role-correlated too: coverage of the meeting's roll-call round runs
  ~99.6–99.7% for crew against ~45.5–46.5% for impostors — a behavioral tell,
  not a firewall leak (same file, §4 item 24).

[JUDGMENT, grounded] The median game is formulaic; roughly one game in eight
holds something a human would rewind (`audits/audit-phase-19-input-claude.md`
§5.4, from that audit's full reads). Hence §2's hand curation.

---

## 4. The audit idiom, defined

The corpus is case law. These eleven terms carry most of its weight; each entry
names a committed usage you can check.

- **baseline N** — a numbered substrate record: one recording of the sample sets
  under a stated set of behavioral levers, which everything afterwards is
  measured against. Six exist, from
  `audits/audit-2026-07-01-phase-14-baseline1-characterization.md` to
  `audits/audit-phase-18-baseline-6.md`; the referee's floor registry
  `_BASELINE_SUPPLY_FLOORS` (`eval/watchability.py:548`) holds baseline-2
  through baseline-6.
- **adopting record** — the point of a baseline: it is the recording that
  *adopts* a substrate change, not a tag applied afterwards. Hence a lever
  "graduates at its own adopting record" (`audits/audit-phase-17-absence-gate.md:149`),
  and baseline 6 is named as "the 18.12 CREW-ONLY adopting record"
  (`audits/audit-phase-18-close.md:7-8`; the rule in `docs/architecture.md`
  §"Determinism and the substrate ladder").
- **the ladder tip** — the newest baseline; where the substrate stands. "The
  ladder tip STANDS at baseline 6" (`audits/audit-phase-18-close.md:7-8`); every
  README sentence naming a tip is checked against that audit by
  `scripts/check_doc_facts.py::check_ladder_tip`.
- **graduated lever** — a behavioral change ships behind an `AILIBI_*` env gate,
  then *graduates* at a baseline: the gate is deleted, the behavior becomes
  unconditional, the key stays in the recording stamp for provenance. Thirteen
  have graduated, one live toggle remains (`orchestrator/replay.py`,
  `_RETIRED_ALWAYS_ON_LEVERS` vs `TOGGLEABLE_SUBSTRATE_FLAG_KEYS`), and
  graduating obliges a prose sweep (`AGENTS.md` §"Graduation sweeps"). The
  usage, at the record that performed the most recent four: "the four
  meeting-layer levers graduated to unconditional ON … beside the nine
  already-retired levers" (`audits/audit-phase-18-baseline-6.md:7` — the 4 + 9
  that make thirteen).
- **the §1.3 bar** — the flip bar. `audits/audit-phase-17-close.md` §1.3 states
  what a learned mover must do to become the default: close both
  evidence-supply gaps *without surrendering the win edge*. Later rulings read
  against it (`audits/audit-phase-18-close.md:104-105`).
- **NO-FLIP** — the ruling that the bar was not cleared, so the scripted mover
  stays default and the learned champion stays opt-in. Ruled twice, in the
  titles of `audits/audit-phase-17-close.md` and
  `audits/audit-phase-18-close.md`.
- **canary denominator** — the largest same-substrate, validity-gated recording
  set canary metrics are judged on (today `replays/ml_corpus/`, ~3× the
  samples). An owner ruling (`audits/review-phase-15-midwave.md` Q3), restored
  at `audits/audit-phase-17-close.md` §3, re-grounded onto baseline 6 at
  `audits/audit-phase-18-close.md:12`.
- **findings, not failures** — the closing doctrine: a pre-registered
  measurement that misses its bar is a finding to record, not a failure to hide
  or re-price (`audits/audit-phase-18-close.md` §6 heading; chartered at
  `tasks/phase-18.md:118`).
- **the 15.18 convention** — named after the Phase-15 pause task: decision
  documents (plans, close readings, tier maps) are proposed as PRs and the
  owner's *merge* is the ratification; measurements commit their
  pre-registration first and their reproduction snippets beside the numbers
  (`audits/audit-phase-17-close.md:453`; `audits/audit-phase-18-baseline-6.md:3`;
  `tasks/phase-19.md:22-23`).
- **the two-owner gate** — a phase's ruling and its close are two separate owner
  merges, and the close PR carries no new evidence, so the second merge ratifies
  a reading rather than a surprise (`tasks/phase-18.md:2299-2301`; "the phase's
  second owner gate", `audits/audit-phase-17-close.md:453-454`; invoked to
  refuse new work at `audits/audit-phase-18-close.md:984`).
- **errata discipline** — living documentation (README, design notes) is
  rewritten; *records* — campaign reports and audits — never are. They get
  additive, dated errata, and later prose quotes only errata-approved figures
  (`tasks/phase-19.md:106-108`; `training/reports/report-finalist-eval.md` §18;
  `audits/audit-phase-18-close.md:1113`).

**Citation shorthand.** `§N.M` is a section of the cited document; `F<n>` a
numbered campaign finding carried between contracts (F13 closed as unsupported,
`audits/audit-phase-18-close.md:180`); `L<n>` an item in a ruling's own ledger
(same file, §6.1); `P0`–`P2` the input audits' severity ranks. In
`audits/audit-phase-19-triage.md`, `[C]` marks a finding both external audits
reached, `[S-Claude]`/`[S-Codex]` a single-source finding, `[L]` an
internal-ledger-only one — provenance tags, not verification status, which lives
in its §8 table.

---

## 5. Where the bodies are buried — three audits, in this order

1. **`audits/audit-phase-19-input-claude.md`** — an independent audit run from a
   fresh clone. Read §5: 18 committed games read end-to-end and all 300 replays
   parsed, producing §3's cross-tab, the four traced injustice classes (§5.2),
   and the honest good/bad lists (§5.3–5.4). **What it proves:** the corpus is
   auditable by a stranger — every derived metric reproduces from the committed
   raw bytes with no pipeline access. §3.2 item 5 is also the diagnosis that
   produced this guide: the corpus is case law with no glossary.
2. **`audits/audit-phase-19-triage.md`** — the reconciliation of that audit
   against a second, independent one by a different model. Read §1, §3 (the
   contradiction rulings), §8 (the claim-verification table). **What it
   proves:** the review culture is real. Disagreements are ruled on evidence,
   not seniority; a "gate green vs gate red" contradiction resolves to a
   platform-scoped portability defect (C1); and one of its own source audits'
   headline terms is refuted rather than absorbed (§8 row 19).
3. **`audits/audit-phase-18-close.md`** — the close of Phase 18, and with it of
   the four-phase ML program. Read the header block and §6. **What it proves:**
   the machinery holds under a result nobody wanted. Every learned arm beat the
   same-seed scripted comparator on wins (+0.12 to +0.30, `:104-105`) and every
   arm failed the *referee* — the pre-registered selection gate that prices what
   a mover does to the deduction economy it plays in — so **no arm became the
   default** (the learned champion stays opt-in, where Phase 15 left it, and no
   crew artifact was adopted); zero of fourteen pre-registered emergence
   rulings were demonstrated, including two
   real, selected-for effects the registered clause could not certify.
   `audits/audit-phase-18-flip-emergence.md` derives that reading cell by cell.

---

## 6. The honest ML story

Four phases (15–18) built a machine-learned tactical-policy program: a rollout
environment, an ES optimizer, a ballot surrogate, a conviction model, a
co-evolution driver. **It did not ship a default policy change, and that is the
result, not a footnote.**

**What was positively learned** (`training/README.md` §3, every cell anchored to
the committed audits):

- **N1** — the learned mover kills into witnesses at ~3.3× the scripted rate:
  crew-witnessed-kill rate 30/197 = 0.15228 vs the FSM comparator's
  8/174 = 0.04598, z = +3.370, sign-reproduced 3/3.
- **N2** — it emits a kill class the scripted mover structurally cannot:
  co-present kills, 20/197 = 0.10152 vs 0/174, z = +4.321.
- Both are ruled **NOT-DEMONSTRATED** under the pre-registered discipline — not
  because the effects are doubtful, but because the registered ablation clause
  was unsatisfiable by construction. The effects are recorded; the claim is not
  upgraded to fit them.

**The clean negatives, kept as results** (same source): the crew stack's triple
negative (0/30 wins against the FSM's 3/30 under a passing validity gate); the
torch PPO probe; the policy-ES real path, whose impostor **win rate** collapsed
to 0.02 = 1/50 against the same-substrate FSM's 0.36 — an edge of −0.34, and a
referee PASS bought by losing (`training/reports/report-finalist-eval.md:268-271`;
the per-arm cells at `audits/audit-phase-17-close.md:61`); and the surrogate's
always-SKIP decision arm — 0 ejections across 96 held-out meetings, retired
while its *ranking* channel (46/60 top-1) is kept.

**One statistic the program corrected about itself:** the shipped champion's
paired win edge is statistically unresolved at n=50 — exact McNemar 15/9,
p = 0.3075 (`training/README.md` §3; `audits/audit-phase-19-triage.md` §8 row 4;
recomputable via `scripts/paired_stats.py`). The terminology erratum belongs
here too: `0.9375` is conversion-label accuracy, and the composed runner's
meeting-decision accuracy is `0.8646` against a 0.625 always-eject constant
(`training/reports/report-conviction-model.md` and
`training/reports/report-composed-runner.md`, both carrying dated errata).

**The program is frozen.** Every frozen surface carries a header naming the tier
map, and the map is `training/README.md` — keep / freeze / retire, component by
component. **The reopening checklist is `training/README.md` §7**: two recorded
routes back (re-price the referee floor, or give training real-path conviction
signal), four mandatory pre-campaign checks, and the rule that the owner picks a
route only against a concrete proposal. Nothing reopens in the abstract.

---

## 7. Where to go next

Current architecture: [docs/architecture.md](architecture.md). Workflow
protocol: [AGENTS.md](../AGENTS.md). Design *history*, not current shape:
[DESIGN.md](../DESIGN.md). The spectator API's exposure posture — an
unauthenticated GM view, loopback-only by design:
[docs/deployment.md](deployment.md). Which bytes live in git, which live on a
pinned evidence sha, and how to fetch them:
[docs/artifacts.md](artifacts.md).
