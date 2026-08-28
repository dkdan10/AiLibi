# ML-calibration corpus (Task 15.12, re-grounded onto baseline 7 by the baseline-7 record)

The frozen training/calibration corpus the ballot surrogate (15.13) and the
impostor bake-off (15.15+) consume, recorded at **exact baseline-7 config** —
`Qwen/Qwen3.6-27B` on Featherless (non-thinking, `fail_loud`, `json_object`), the
`qwen3_6_27b` prompt set (all four templates — `accusation_round`,
`crewmate_report`, `impostor_report`, `vote_ballot` — at **v4**), the
**baseline-7 lever slate** (the twenty-one retired always-on levers, which since
the baseline-7 record include the eight Phase-20 evidence-honesty levers, with
`impostor_roll_call` the **sole live toggle** and its recorded state **OFF**),
`$0` flat-rate — with the 15.9 FSM-default tactical-policy stamp on every game.
The model was locked 2026-07-12 at Task 16.2
(`audits/audit-phase-16-model-lock.md`). The eight Phase-20 graduations were
adopted by owner override of a FINDING verdict at the baseline-7 record
(`audits/audit-phase-20-baseline-7.md` §6.1) — the pre-registered bars were
missed, and the owner adopted the substrate regardless. The v4 prompt map is
Task 20.31's evidence-honesty bump.

Nothing trains against a meeting layer scheduled to change
(`tasks/post-phase-14-plan.md` §4;
`audits/post-phase-14-ML-training-signal.md` §5.6, §7.2), so this corpus is a
**separate release artifact** from the canonical `replays/samples/` baseline. It
uses **fresh seed ranges** so a corpus game can never be confused with a
canonical 0–49 game.

> **The corpus and the samples sit at ONE substrate rung, and the ML program
> does not.** The baseline-7 record re-recorded all four committed sets in one
> window, so nothing downstream trains across a substrate seam *inside*
> `replays/`. Everything fitted, selected, or pinned on the **baseline-6** corpus
> — the surrogate, the conviction model, the bake-off rankings and finalist rows
> — is now prior-substrate-anchored: `uv run python scripts/verify_ml_evidence.py`
> reconstructs 300/300 and **exits 0 with 11 rows reporting STALE**, each naming
> the gap; `BAKEOFF_BASELINE_ID` reads `baseline-6`, which is correct — it names
> the baseline the bake-off is GROUNDED on, not the substrate baseline. Read the
> command's `ML grounding` row first: it carries the two corpus fingerprints and
> decides whether a disagreement below it is a defect (FAIL) or this declared gap
> (STALE). Re-grounding those artifacts on these bytes is a NAMED FOLLOW-UP, not
> part of this record (`audits/audit-phase-20-baseline-7.md` §10.2). Until it
> lands, treat every published fit metric as anchored to bytes that are no longer
> committed.

> **Canary denominator — the Q3 rule, unbroken this time.** The mid-Phase-15 Q3
> ruling (the ML corpus is the canary denominator; the canonical
> `replays/samples/` baseline is the continuity anchor) lapses whenever the two
> artifacts sit at different substrate rungs — it was DEGRADED through Phase 16,
> restored at Task 17.9, and re-lapsed for the interval between the Task-18.12
> samples record and the 18.13 corpus record. The baseline-7 record closes that
> gap by construction: all four sets were recorded in ONE window, so the rule
> never lapses across it. The corpus is the canary denominator, the baseline-7
> samples are the continuity anchor, and future phase closes re-adopt the pairing
> (`audits/audit-phase-17-close.md` §3 is the worked example).

> **These bytes are the baseline-7 record.** Both sets under `9p2i/` and
> `4p1i/` were re-recorded at baseline 7 by a local operator session and pass the
> acceptance gate: `validity_gate.py --expected-model Qwen/Qwen3.6-27B
> --require-zero-cost` is green on each, reconstruction is byte-identical, every
> recorded `game_over` stamp carries the baseline-7 lever slate + the locked
> model + `$0` cost, and the `FROZEN` line in each `MANIFEST.md` names the
> recording commit. The recorder's freeze-path guards (`check_replay_provenance`
> — the model, the `$0` cost, and the **baseline-7 lever slate** on every
> recorded stamp) PASS over the committed bytes by construction; they refuse
> anything off-substrate (a prior baseline-6 recording, whose stamp carries the
> eight Phase-20 levers OFF; a phantom seed) from being resumed-over and frozen.

## Layout

```
replays/ml_corpus/
  9p2i/    150 games, seeds 1000..1149, roster 9p/2i @ 2 tasks/crewmate   [primary]
  4p1i/     50 games, seeds 1000..1049, roster 4p/1i @ 1 task/crewmate    [secondary]
```

Each set carries: `replay-seed-*.jsonl`, `MANIFEST.md` (with the 15.9 `policy`
column stamping `fsm-default`, plus the explicit `FROZEN` line naming the
`git_sha`), `roster.json`, `tournament-eval-report.json` (the roles ground
truth), and a committed by-game `splits.json` (train/val/test — **data only**;
the loader is 15.11's). The corpus keeps its Task-15.12 shape across the
re-record — same 150-game 9p2i + 50-game 4p1i scale, same seed ranges, same split
rule — so `CORPUS_SPLITS_PATH` stays structurally identical.

### The two-level nesting is load-bearing

A set placed directly under `replays/` would make the API's directory resolution
treat `./replays` as the active parent and **shadow** the canonical samples
(`api/main.py::_resolve_replay_dir` + `api/replay_loader.py::_is_set_dir`, Task
12.12). Nesting each set under `replays/ml_corpus/<set>/` keeps the corpus
invisible to default spectator resolution while an operator can still opt-in
serve it explicitly with `AILIBI_REPLAY_DIR=replays/ml_corpus`. The invariant is
pinned by `tests/api/test_set_discovery_ml_corpus.py`.

## By-game split rule

`splits.json` partitions games (one game per seed) by a deterministic,
auditable rule — the split is a total function of the seed, so no game can appear
in two splits:

```
seed mod 5:  {0,1,2} -> train    {3} -> val    {4} -> test        (60/20/20)
```

For 9p2i (150 games): 90 train / 30 val / 30 test.
For 4p1i (50 games):  30 train / 10 val / 10 test.

## Capability disclosures (measured, not tuned)

The corpus is honest about what it contains; this section is honest about what
that implies. Four surfaces are measured: this corpus's two sets and the
canonical `replays/samples/` twins, all four recorded at the same baseline-7
substrate — **S9** (`replays/samples/9p2i`, 50 games), **S4**
(`replays/samples/4p1i`, 50 games), **C9** (`replays/ml_corpus/9p2i`, 150
games), **C4** (`replays/ml_corpus/4p1i`, 50 games).

**Which numbers below are current, and how you can tell.** Items 1, 2, 8 and 9
are re-derived from the committed baseline-7 bytes. Their headline cells — the
meeting total and the eight roll-call coverage pairs — are re-derived on *every*
gate run by `check_doc_facts.check_corpus_disclosures`, which reads each set's
own `tournament-eval-report.json` and fails on disagreement, so this section can
never again be relabelled without its arithmetic. The rest of each item is folded
from the replay bytes through `eval.replay_walk` (the resolved-kill and
crew-witness cells are the same walk `tests/eval/test_kill_craft.py` pins).
**Items 3 through 7 are not current**: they were measured on the baseline-6
bytes and were never re-derived at the baseline-7 record, so their counts and
denominators describe the previous recording. Each carries that flag on its own
line. Their *mechanism* claims still hold; their numbers are history, and
anything fitted on this corpus must re-derive them first.

Because the by-game split rule above is a function of the seed alone — never of
content — the pervasive phenomena below (the structural prior, the husk rate,
the response shape, the skip templating, both theater classes, the evidence
economy) land in train, val, and test alike, so a model fitted on the train split
learns them as if they were the game; rare events, by the same seed-blindness,
land wherever their seed falls.

1. **The absolute reporter-innocence prior (structural).** The scripted FSM
   impostor never files a body report and never calls a meeting — the COVER
   branch is explicit: "after the kill the body is in the room and the impostor
   must not file a report" (`agents/tactical/impostor_policy.py:39-40`).
   Measured across all four sets: meetings crew-triggered **668/668**, opening
   turns crew-spoken **668/668**, and the tick streams carry **717/717**
   `report` and **67/67** `emergency` submissions by crew — zero
   impostor-originated, anywhere. 100% of training examples therefore embed
   "the reporter is innocent" as an absolute prior. A crew model fitted here
   has never seen a lying reporter, and any learned impostor that self-reports
   instantly invalidates the crew's learned prior. The prior is disclosed, not
   changed: the scripted policy is what it describes.

2. **Non-resolving kill submissions.** Of **1,011** submitted `kill` actions
   across the four sets, **825 resolved** and **186 (18.4%) produced no kill**
   — in two distinct ways. **150 were engine-rejected**, every single one on
   the same-room check (the target was no longer co-located when the action
   applied mid-tick; zero cooldown and zero dead-target rejections anywhere),
   and **36 were never evaluated at all** (an earlier `report`/`emergency` in
   the same tick moved the phase to MEETING before the kill applied — those
   were not necessarily illegal when submitted). Per set,
   non-resolving = rejected + pre-empted: S9 **43/220 = 19.5%** (36 + 7), C9
   **137/663 = 20.7%** (110 + 27), S4 2/67 = 3.0% (1 + 1), C4 4/61 = 6.6%
   (3 + 1). At 9p, roughly one scripted kill decision in five fails to land,
   and most of those failures are outright illegal at application (36/220 =
   16.4% S9, 110/663 = 16.6% C9) — a mover-quality limitation no eval report
   surfaces. The resolved counts are the committed kill-craft pins exactly —
   C9 526, S9 177, S4 65 (`tests/eval/test_kill_craft.py:69`, `:100`, `:127`) —
   and C4's 57 is recounted here through the same fold.

3. **Player-visible `[invalid accusation target …]` husks — a recorded
   deviation from this README's own no-husk doctrine.** The "Defaulted turns"
   section below rules that a frozen training/eval corpus **must not contain**
   fallback husks, and the freeze guard enforces that for `deadline_default`
   rows — and indeed all four sets carry **zero** defaulted turns. But the
   doctrine's guard keys on `error_type`, so a *different*, unguarded husk
   class sits in the frozen bytes: the validator annotation
   `[invalid accusation target 'p-N' dropped]` is welded into player-visible
   `free_text` on **53/971 S9 turns (5.5%)** and **137/2,726 C9 turns (5.0%)**
   (both 4p sets: zero). The doctrine and the bytes contradict each other; this
   paragraph records the deviation rather than leaving it silent. Shape facts:
   every husk is a line-leading prefix on otherwise-model text (190/190), ~80%
   sit on `opt_in` turns, and the class never appears in ballot
   `rationale_text` (0/3,934). C9 also carries a second, rarer free-text class
   — `[invalid corroboration supports … dropped]` ×2 — which resolves an
   audit's 139-vs-137 discrepancy as a class difference, not a substring
   boundary. A separate husk surface the audits did not reach: **ballot**
   `rationale_text` carries vote-guard husks — `[under-gate eject target …
   redirected]` (13 S9 / 48 C9 / 1 C4), `[invalid target … normalized to
   SKIP]`, `[teammate target … coerced to SKIP]` (4 C9 — machinery that names
   the impostor's ally in the record), and `[invalid primary_reason… nulled]`
   variants: 18/971 S9 and 55/2,726 C9 ballots. As a capability datum: at 9p
   the model names an illegal accusation target roughly one turn in twenty.
   *Baseline-6 counts; not re-derived at the baseline-7 record.*

4. **Zombie-vent re-litigation.** Dead impostors' vents keep getting re-argued:
   **56/165 S9 meetings (33.9%)** and **174/463 C9 meetings (37.6%)** contain a
   `saw_vent` observation whose subject was already dead at meeting time —
   **230/707 meetings (32.5%)** corpus-wide, touching 68% of 9p games, and all
   300 such observations name an **ejected impostor** (never a killed crew).
   The structured `claims[]` arrays are clean (0/3,181 accusation claims name a
   dead player — the validator strips them); the free-text husk drops in item 3
   are the visible symptom of exactly that stripping. Worst meetings: C9 seed
   1118 meeting-1 carries five drops — the only five-drop meeting in all 300
   games; the S9 maximum is four (seed 23 meeting-1, tied with seed 19
   meeting-1). Delta noted: an audit placed "five drops" in S9 seed 23; the
   recount says four, and the five belongs to C9 seed 1118.
   *Baseline-6 counts; not re-derived at the baseline-7 record.*

5. **Skip-template repetition.** Skips are encoded as `target == "SKIP"`
   (there are no null targets). Skip shares: S9 451/971 = 46.5%, C9 1,148/2,726
   = 42.1%, S4 90/117 = 76.9%, C4 75/120 = 62.5% of ballots. Among skip
   ballots, exact-duplicate `rationale_text` copies (beyond each string's first
   use): S9 **30/451 = 6.7%**, C9 **149/1,148 = 13.0%**, S4 11/90 = 12.2%, C4
   2/75 = 2.7% — and **261/1,764 = 14.8%** pooled, higher than any single set
   because the same template strings recur *across* sets ("The evidence is too
   thin to justify an ejection." ×30 corpus-wide). The repetition is almost
   entirely a skip phenomenon (261 of 270 redundant ballot copies are skips).
   Transcript `free_text`, by contrast, is byte-unique: 3,934/3,934 distinct
   across all four sets, zero exact repeats anywhere.
   *Baseline-6 counts; not re-derived at the baseline-7 record.*

6. **Wait-streak and ping-pong mover theater.** Two scripted-mover artifacts
   with mirror-image role signatures — one absolute, one strong but not
   perfect. **Wait streaks** (longest run of consecutive-tick
   `wait` actions per player-game; meetings do not break a run): **170/2,200
   player-games (7.7%) idle ≥10 consecutive ticks — 170/170 of them crew, 0
   impostor**. Per set: S9 53/450 (worst 36 ticks: seed 32 `p-9`, ticks 20–55,
   sitting through three meetings), C9 109/1,350 (worst 33), S4 7/200 (worst
   19: seed 16 `p-4`, ticks 8–26), C4 1/200. **Ping-pong pathing** (a minted
   definition, disclosed as such: ≥4 consecutive-tick `move` actions strictly
   alternating between exactly two rooms): **124/2,200 player-games (5.6%),
   119/124 of them impostors** — 119/500 = 23.8% of impostor player-games vs
   5/1,700 = 0.29% of crew. Longest: 24 alternating moves (C9 seed 1016 `p-4`,
   REACTOR↔ENGINEERING); S9's longest is 14 (seed 10 `p-3`, ending in a kill).
   The two artifacts are mirror images: crew theater is standing still,
   impostor theater is pacing.
   *Baseline-6 counts; not re-derived at the baseline-7 record.*

7. **Model-originated fourth-wall statements and machinery quotation.** The
   fourth wall holds almost everywhere in *player-visible* text and fails
   routinely in *recorded private* text. Ballot `rationale_text` (never shown
   to players, but committed and audit-visible): **29/245 = 11.8% of S9** and
   **81/684 = 11.8% of C9** impostor-voter ballots name a partner ("my
   partner" / "my teammate" / "my fellow impostor"; a looser phrase net
   reaches 36 and 107; crew false-positive control 0/2,926), and **8/245 S9,
   14/684 C9, 2/40 C4** ballots state the role outright — C4 seed 1011's "I am
   the impostor. Voting is futile." is the bluntest. Player-visible
   `free_text` carries exactly **one** genuine fourth-wall leak in 3,934 turns
   (C9 seed 1023, an impostor saying "my teammate" aloud). Model-originated
   *machinery quotation* splits by register. Literal implementation tokens in
   model output: **zero**. Of the audit-suggested tokens (`vent_sighting`,
   `alibi_vs_sighting`, `[weak signal`, `roll_call`, …) none appears in any
   player-visible or rationale text, and the only `primary_reason` occurrences
   in persisted text (5/3,934 ballots) are guard-injected `[invalid
   primary_reason… nulled]` prefixes — item 3's vote-guard husk surface, not
   quotation: the corresponding raw `llm_calls[].response_text` rationales
   carry zero such tokens. But *natural-language* machinery talk is common in ballot
   rationales: "threshold" in **90/971 = 9.3% (S9)** and **208/2,726 = 7.6%
   (C9)**, "suspicion" in 85/971 and 244/2,726, and a quoted internal decimal
   (`0.NN`) in **39/971 = 4.0%** and **94/2,726 = 3.4%** — S9 seed 38's "my
   suspicion is 0.45 … the threshold is 0.60. I skip." reproduces the scoring
   internals verbatim, and S9 seed 44 asks whether "the system" flagged
   verified evidence. The vocabulary counts are an upper bound (a deduction
   game says "suspicion" naturally); the quoted decimals are unambiguous.
   In player-visible `free_text` the same vocabulary is rarer ("suspicion"
   16/971 and 47/2,726). The bracketed machinery text that reaches
   player-visible surfaces is the machinery-injected husk class of item 3,
   not model quotation — the earlier "~17% quote machinery" reading spanned
   both registers without separating them.
   *Baseline-6 counts; not re-derived at the baseline-7 record.*

8. **Role-correlated public response shape.** The share of a role's transcript
   turns carrying a structured `whereabouts` observation (the roll-call
   answer), pooled over turns: crew S9 **652/652 = 100.0%**, crew C9
   **1,854/1,854 = 100.0%**, crew S4 **80/80 = 100.0%** and crew C4 **88/88 =
   100.0%**, versus impostor S9 **104/219 = 47.5%**, impostor C9 **283/625 =
   45.3%**, impostor S4 **5/40 = 12.5%** and impostor C4 **1/44 = 2.3%**. The
   estimator matters and is named: the *unweighted per-meeting macro-average*
   of the same bytes reads 43.8% (S9) and 41.1% (C9) for the impostor side
   (`deduction.public_response_coverage`); the pooled turn-level figures above
   are the headline here. The mechanism is the templates' role-differentiated
   output contract, not model choice: the role-blind info-share/roll-call
   surface elicits whereabouts from both roles (impostor `opt_in` turns answer
   104/104 in S9 and 283/283 in C9), but the impostor REPLY surface hard-codes
   `observations: []` (0/115 S9, 0/342 C9) while the crew reply carries the
   full vocabulary (78/78 S9, 207/207 C9) — and impostors are disproportionately
   in reply position (115/219 of their turns vs 78/652 for crew in S9;
   342/625 vs 207/1,854 in C9). So the tell is the *absent* observation, and it
   is absolute: on these bytes no crew turn anywhere lacks a whereabouts answer
   and no impostor reply carries one.

   The whereabouts that *are* recorded are almost never lies. Counting
   whereabouts *observations* (a turn may carry more than one) against the
   pre-advance decision frame — the reconstructed state each recorded tick's
   actions were decided against, read from `eval.replay_walk`'s per-tick
   pre-advance state, the same frame as item 9's census — self-placements match
   the reconstructed room in **102/104 = 98.1% (S9)** and **283/285 = 99.3%
   (C9)** for impostors, versus crew **656/659 = 99.5% (S9)** and **1,875/1,892
   = 99.1% (C9)**; pooled over all four sets, crew **2,701/2,722 = 99.2%** and
   impostor **391/395 = 99.0%**. This frame agrees cell for cell with the
   engine's own rendered route line in each meeting prompt. The 48.3%/45.3%
   impostor and 79.5%/79.6% crew match rates this item used to publish were
   measured on the baseline-6 bytes and reproduce in neither frame here; they
   are retired rather than carried forward. **Impostors essentially do not lie
   in the one structured channel the alibi rules prosecute** — anything fitted
   on "impostors lie in roll call" is fitted on nothing.

9. **The too-clean evidence economy.** Across all **825** resolved kills in
   the four sets, the pre-advance decision frame shows **zero** kills with any
   non-victim living crew co-present in the kill room (co-present histogram
   `{0: 825}`, the fold `tests/eval/test_kill_craft.py` pins per set), and only
   **20/825 = 2.4%** were crew-witnessed at all (16 C9 / 3 S9 / 1 S4 / 0 C4 —
   every witness a same-tick one-hop arrival, a mid-tick engine fact that only
   the engine walk can read). The scripted impostor kills only isolated targets
   (`agents/tactical/impostor_policy.py` KILL guard), so the corpus supplies
   almost no direct kill testimony: convictions ride the post-kill vent tell
   instead, and a crew stack trained here has effectively never seen a
   contested kill scene.

Measured at Task 19.8 on the baseline-6 bytes; items 1, 2, 8 and 9 re-derived at
Task 21.11 on the committed baseline-7 bytes, and Task 21.15's re-record moves
every cell here again.

## Recording (operator, `$0`, ~22–23h MEASURED)

This is an operator-run step gated on `FEATHERLESS_API_KEY`; it is **not** run in
CI or by an agent session (the fake CI provider is refused — the corpus records
only on Featherless). The Task-18.13 record is the measured figure, not an
estimate:

| leg | wall clock |
|---|---|
| 4p1i (50 games) | 0h 47m 01s |
| 9p2i (150 games) | 16h 00m 16s |
| phantom-repair pass (2 seeds, see below) | 0h 12m 33s |
| **corpus total** | **~17h 00m** |

Those are the corpus legs alone. The baseline-7 record recorded all four
committed sets in one window — **23h 25m 42s** for 300 games at **$0.0000**,
including the two samples legs (`audits/audit-phase-20-baseline-7.md` §0.3). It
came in inside a bracket committed in advance (22.2 h at the smoke's own game
lengths, 26.3 h at baseline-6 lengths), nearer the lower figure. Treat the
baseline-6 figures (0h45m / 19h26m / 2h43m, ~22h54m) as history: the v4 prompt
set is shorter per meeting call than v3 was. Note the wall clock includes any time the machine spends asleep — a
suspend pauses the run rather than corrupting it. Apply the 16.14/17.9/18.12
operator notes (staggered worker starts, jittered backoff, per-seed atomic
staging, `AILIBI_SEED_MAX_ATTEMPTS=8`) and **checkpoint-push discipline**: commit
and push each completed seed range as it lands, so an interruption (machine
sleep, a transport blip that kills the process, a reclaimed container) never
loses a leg. Preview the plan first:

```bash
bash scripts/record_ml_corpus.sh --dry-run
```

Then record both sets (2 Featherless seed workers, per-seed transport
crash-retry) from a **bare** lever environment — record the short 4p1i set first
to validate the pipeline end to end, then the long 9p2i leg:

```bash
export FEATHERLESS_API_KEY=...          # hosted flat-rate; recorded as $0
export AILIBI_LLM_PROVIDER=featherless  # the locked baseline-7 provider
export AILIBI_PROMPT_SET=qwen3_6_27b    # the locked baseline-7 prompt set
export AILIBI_SEED_MAX_ATTEMPTS=8       # raised transport retry budget for the long run
bash scripts/record_ml_corpus.sh --set 4p1i    # short leg first
bash scripts/record_ml_corpus.sh --set 9p2i    # then the long leg
```

Those four exports are the **whole** recording environment. The twenty-one retired
levers are unconditional in code and need no env at all; `AILIBI_IMPOSTOR_ROLL_CALL`
must stay **UNSET** (see below).

The preflight locks the full baseline-7 substrate, not just the provider:

- **the lever slate.** The preflight POSITIVELY checks the live substrate
  snapshot equals the ruled baseline-7 state — the twenty-one retired levers ON and
  `impostor_roll_call` OFF — and refuses before any seed stages. A leftover
  `AILIBI_IMPOSTOR_ROLL_CALL` export would ship the **unshipped** impostor-answer
  arm into the record while the echo claimed the ruled substrate, and an
  acceptance gate run in the same polluted shell would then PASS coherently
  (`substrate_flag_snapshot()` reads the same env) — the C6 recording-preflight
  hazard the graduations discharge. Because the check compares the *slate* rather
  than blacklisting a variable name, it also catches a partial graduation and any
  future toggleable-set drift. This mirrors the Task-18.12 preflight in
  `scripts/refresh_samples.sh`.
- **the model.** A leftover `AILIBI_LLM_MEETING_MODEL` / `AILIBI_LLM_TRIGGER_MODEL`
  export from a model sweep is refused unless it names the baseline model
  (`Qwen/Qwen3.6-27B`).
- **the endpoint.** A non-default `AILIBI_FEATHERLESS_BASE_URL` (a mock/staging
  endpoint) is refused outright.

All three knobs are then exported pinned so the recorded substrate can never
drift from the one the `MANIFEST` stamps. The prompt **versions** are locked too,
not just the set name: the preflight asserts the registry still resolves
`qwen3_6_27b` to the baseline-7 map (all four templates at v4), and the finalize
refuses to freeze a set unless every meeting-bearing `MANIFEST` row carries
**exactly** that map (a foreign version string AND a stripped/partial row both
refuse — the manager stamps the full set map on every meeting, so anything short
of the exact four is missing provenance) — a later registry bump stops the
recorder cold instead of silently recording (or resuming into) a non-baseline
corpus. The recorder also refuses a set dir containing any `replay-seed-*.jsonl`
outside the set's locked seed range (checked before recording and again before
freezing), so a stray file can never be swept into the frozen corpus or its
splits.

The wrapper composes the same tooling `scripts/refresh_samples.sh` drives
(`scripts/run_tournament.py --tactical-policy-stamp fsm-default`,
`scripts/_manifest_writer.py`, `scripts/build_sample_report.py`); it never edits
them. Per set it stages each seed, moves only the replay JSONL into place,
maintains `MANIFEST.md`, rebuilds `tournament-eval-report.json`, writes
`splits.json`, and appends the `FROZEN` line.

`splits.json` can be regenerated from the recorded replays alone (no network):

```bash
bash scripts/record_ml_corpus.sh --splits-only        # --set to scope
```

### Resuming an interrupted recording

The recorder is **resumable**. A multi-hour hosted record can be interrupted
(machine sleep, a transport blip that kills the process). Simply re-run the same
command — it **skips any seed whose replay is already present** in the set dir and
records only the missing ones, then re-finalizes (report + splits + `FROZEN`).
Provenance is per-seed: a resume backfills `MANIFEST.md` rows only for seeds
that lack one (the crash window between a replay landing and its row being
written) — rows recorded by an earlier session keep that session's `git_sha`,
so a resume never rewrites the provenance of bytes it did not record. File
presence alone is not provenance: before a present replay is skipped as
"already recorded" (and again before the freeze), the recorder proves its
**bytes** carry the full baseline-7 provenance —

- the canonical **five-field** 15.9 `fsm-default` tactical-policy stamp (not just
  its id: a hand-crafted stamp with non-canonical method/encoder/weights/anchor
  fields renders identically in the `MANIFEST`);
- the locked model (`Qwen/Qwen3.6-27B`) on **every** recorded call (meeting calls
  and failed-call rows alike, so a wall-clock-miss phantom or a foreign-model
  recording is refused);
- exactly `$0` recorded cost;
- the **baseline-7 lever slate** stamped **positively** on the `game_over` record
  (the same tolerant per-lever match the validity gate and the loader enforce:
  every retired always-on lever present and True — including the four Task-18.12
  meeting-layer graduations `roll_call_round` / `whereabouts_interior_flags` /
  `vent_placement_contradictions` / `absence_prior` — and `impostor_roll_call`
  OFF). This asserts the slate in the recorded bytes, not just the env refusal,
  so a **stale baseline-5 replay** (which carries those four levers OFF) is
  refused **at the recorder**, not only at the external validity gate. That
  refusal is what made this a re-record rather than a resume: pointed at the
  committed baseline-5 corpus, the guard refused all 200 replays by name.

### Defaulted turns, and why a refused freeze is cheap

A long hosted record produces occasional **defaulted turns**: a meeting turn that
misses its deadline records a `failed_call` row with
`error_type: deadline_default` (e.g. "opening turn (turn 0) defaulted
(validation)"). The transcript then carries a **fallback husk** rather than model
output, which a frozen training/eval corpus must not contain — so
`check_replay_provenance` refuses the set and it **will not freeze** while any
survive.

**These rows come in TWO shapes, and only one is visible in the `model` column**
(`orchestrator/game.py::_record_deadline_defaults`):

| shape | `model` column | when |
|---|---|---|
| zero-spend marker | `"(deadline_default)"` sentinel | the participant submitted nothing |
| **burned generation** | the **real baseline model** | the response failed to parse AND the in-turn retry also failed |

A model-based check catches only the first. The recorder therefore keys on
**`error_type`**, which is the property that actually matters — the shape is just
an artifact of which branch emitted the row. (Note `scripts/validity_gate.py` has
no `deadline_default` check at all; it rejects the sentinel shape only
incidentally, via the model column. The corpus recorder is deliberately stricter
than the gate here, because the corpus is a training artifact.)

**Expect to iterate.** The 18.13 baseline-6 record paid a 2h43m repair pass at
**10/150**; the baseline-7 record paid **2/150**, repaired in 12m33s, and
absorbed no transport retry anywhere in its 23-hour window. Budget a repair pass
anyway — the rate is a property of meeting length, and a re-recorded seed can
pick up a fresh default. The deadline cannot be widened to compensate without
changing the locked substrate, so re-recording is the only honest fix (`audits/audit-phase-16-close.md` §5.2's
runbook rule: the seed re-records clean and its MANIFEST row honestly stamps the
re-record date):

```bash
# after a refused freeze: drop the offending replays, then resume
bash scripts/record_ml_corpus.sh --set 9p2i     # records ONLY the dropped seeds, then re-finalizes
```

Both baseline-7 seeds came back clean on the first retry (all 10 did at 18.13). **A refused freeze costs only the bad
seeds**, never the good ones: provenance is checked separately from presence, so
19 hours of recorded work survived the refusal untouched.

> **Dropping phantoms while the leg still runs is safe — the finalize refuses a
> short set.** `check_seed_count` asserts the exact contiguous locked set
> (every seed in the range, no gap) is on disk before `build_sample_report` /
> `write_splits` / `freeze_manifest`, and again in `--splits-only`. So if a
> defaulted replay is dropped from a still-running or resumed leg (or any in-range
> replay is lost), the finalize fails loud with the missing seeds named rather
> than globbing a short set into a frozen 146-game corpus. Still, the tidy order
> is to drop after the drain: the guard turns a mistimed drop into a hard stop,
> not a silent corruption.

An unstamped replay (a pre-15.9 recording, a canonical sample copied in) is
refused for the same reason: it would render in the `MANIFEST` policy column
identically to a stamped one and the validity gate does not check the stamp. A
fully-recorded set records nothing and just re-finalizes, so re-running is always
safe and idempotent:

```bash
export FEATHERLESS_API_KEY=... AILIBI_PROMPT_SET=qwen3_6_27b
bash scripts/record_ml_corpus.sh --set 9p2i           # resumes from wherever it left off
```

For a long, flaky hosted run, raise the per-seed transport retry budget:
`AILIBI_SEED_MAX_ATTEMPTS=8 bash scripts/record_ml_corpus.sh --set 9p2i`. A set
directory that carries `replay-seed-*.jsonl` but no `FROZEN` line in its
`MANIFEST.md` is a **partial** (not-yet-finished) recording — re-run to complete
and freeze it before running the acceptance gate. A multi-day session spanning
several UTC midnights is expected at the measured **~22–23h** (see the section
header for the per-leg breakdown); `MANIFEST` dates are honest per-seed (the
16.14 mixed-date precedent — the gate checks coherence, not
uniformity).

## Finding these bytes later: the annotated tag

The `FROZEN` line in each `MANIFEST.md` names the **recording-time code state** —
`HEAD` at the moment the recorder ran, i.e. the engine/prompt/lever version that
*produced* the bytes. It is deliberately **not** a pointer to the commit that
*contains* them: that commit does not exist yet when the freeze line is written,
so no recorder could name it. Checking that sha out gives you the generating code,
not the corpus.

The pointer to the bytes is an **annotated tag** cut after the record lands
(`phase-18-corpus-<sha>` for this record). Dispatch environments refuse tag pushes
(the 16.14 limitation), so this is an operator-session step:

```bash
git tag -a "phase-18-corpus-$(git rev-parse --short HEAD)" -m "…substrate + acceptance…"
git push origin "phase-18-corpus-$(git rev-parse --short HEAD)"
```

Both halves are provenance: the freeze line answers "what code made this?", the
tag answers "where are the bytes?".

## Acceptance (per set, before the PR merges)

Hosted models do not byte-reproduce **fresh** generation; **recordings** replay
byte-identically (the loosened contract the canonical baselines already carry),
so the validity gate + byte-verify — not generation-replay equality — is the
acceptance:

```bash
uv run python scripts/validity_gate.py replays/ml_corpus/9p2i \
    --expected-model Qwen/Qwen3.6-27B --require-zero-cost
scripts/verify_samples.sh replays/ml_corpus/9p2i
# ... and again for 4p1i
```
