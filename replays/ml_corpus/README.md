# ML-calibration corpus, re-recorded at baseline 8

The frozen training/calibration corpus the ballot surrogate and the impostor
bake-off consume, recorded at **exact baseline-8 config** — `Qwen/Qwen3.6-27B`
on Featherless (non-thinking, `fail_loud`, `json_object`), the `qwen3_6_27b`
prompt set (all four templates — `accusation_round`, `crewmate_report`,
`impostor_report`, `vote_ballot` — at **v5**), the **baseline-8 lever slate**
(the twenty-one retired levers, unconditional in code, with `impostor_roll_call`
the **sole live toggle** and its recorded state **OFF**), `$0` flat-rate — with
the FSM-default tactical-policy stamp on every game. The model has been locked
since 2026-07-12.

Two repair gates that guarded behavioural fixes were graduated before this
recording opened and **deleted outright** rather than retired, so the stamp on
every recorded game carries exactly twenty-two keys — the twenty-one retired
levers plus the one live toggle — byte-identical to the previous recording's
stamp. That equality is the cheapest available proof that the lever substrate
did not move while the bytes did. The v5 prompt map is the bump that took the
oracle voice out of the templates, and item 7 below is where that shows up in
the recorded text.

Nothing trains against a meeting layer scheduled to change, so this corpus is a
**separate release artifact** from the canonical `replays/samples/` baseline. It
uses **fresh seed ranges** so a corpus game can never be confused with a
canonical 0–49 game.

> **The corpus and the samples sit at ONE substrate rung, and the ML program
> does not.** This record re-recorded all four committed sets in one window, so
> nothing downstream trains across a substrate seam *inside* `replays/`.
> Everything fitted, selected, or pinned on an earlier corpus — the surrogate,
> the conviction model, the bake-off rankings and finalist rows — is
> prior-substrate-anchored, and by two rungs now rather than one:
> `uv run python scripts/verify_ml_evidence.py` reconstructs 300/300 and
> **exits 0 with 12 rows reporting STALE**, each naming the gap;
> `BAKEOFF_BASELINE_ID` reads `baseline-6`, which is correct — it names the
> baseline the bake-off is GROUNDED on, not the substrate baseline. Read the
> command's `ML grounding` row first: it carries the two corpus fingerprints and
> decides whether a disagreement below it is a defect (FAIL) or this declared
> gap (STALE). Re-grounding those artifacts on these bytes is a NAMED
> FOLLOW-UP, not part of this record. Until it lands, treat every published fit
> metric as anchored to bytes that are no longer committed.

> **Canary denominator — the pairing, unbroken again.** The standing rule (the
> ML corpus is the canary denominator; the canonical `replays/samples/`
> baseline is the continuity anchor) lapses whenever the two artifacts sit at
> different substrate rungs, and it has lapsed before, whenever the two sets
> were recorded in separate windows. This record closes that gap by
> construction: all four sets were recorded in ONE window, so the rule never
> lapses across it. The corpus is the canary denominator, these samples are the
> continuity anchor, and future phase closes re-adopt the pairing.

> **These bytes are the baseline-8 record.** Both sets under `9p2i/` and
> `4p1i/` were re-recorded at baseline 8 by a local operator session and pass
> the acceptance gate: `validity_gate.py --expected-model Qwen/Qwen3.6-27B
> --require-zero-cost` is green on each, reconstruction is byte-identical, every
> recorded `game_over` stamp carries the baseline-8 lever slate + the locked
> model + `$0` cost, and the `FROZEN` line in each `MANIFEST.md` names the
> recording commit. The recorder's freeze-path guards (`check_replay_provenance`
> — the model, the `$0` cost, and the **baseline-8 lever slate** on every
> recorded stamp) PASS over the committed bytes by construction; they refuse
> anything off-substrate (an earlier recording whose stamp carries a retired
> lever OFF; a phantom seed) from being resumed-over and frozen.

## Layout

```
replays/ml_corpus/
  9p2i/    150 games, seeds 1000..1149, roster 9p/2i @ 2 tasks/crewmate   [primary]
  4p1i/     50 games, seeds 1000..1049, roster 4p/1i @ 1 task/crewmate    [secondary]
```

Each set carries: `replay-seed-*.jsonl`, `MANIFEST.md` (with the `policy`
column stamping `fsm-default`, plus the explicit `FROZEN` line naming the
`git_sha`), `roster.json`, `tournament-eval-report.json` (the roles ground
truth), and a committed by-game `splits.json` (train/val/test — **data only**;
the loader lives in the training package). The corpus keeps its original shape
across the re-record — same 150-game 9p2i + 50-game 4p1i scale, same seed ranges, same split
rule — so `CORPUS_SPLITS_PATH` stays structurally identical.

### The two-level nesting is load-bearing

A set placed directly under `replays/` would make the API's directory resolution
treat `./replays` as the active parent and **shadow** the canonical samples
(`api/main.py::_resolve_replay_dir` + `api/replay_loader.py::_is_set_dir`).
Nesting each set under `replays/ml_corpus/<set>/` keeps the corpus
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
canonical `replays/samples/` twins, all four recorded at the same baseline-8
substrate — **S9** (`replays/samples/9p2i`, 50 games), **S4**
(`replays/samples/4p1i`, 50 games), **C9** (`replays/ml_corpus/9p2i`, 150
games), **C4** (`replays/ml_corpus/4p1i`, 50 games). Together: 300 games, 672
meetings, 3,631 transcript turns and 3,631 ballots.

**Every figure below is current, and every one is re-derivable.** All nine items
were recomputed from these committed bytes at this recording; nothing is carried
forward from a previous one. Before trusting any of it, prove the bytes:
`uv run python scripts/verify_ml_evidence.py` reconstructs all 300 games. Three
folds then produce every figure, each of them offline and at `$0`:

```bash
# (a) the REPORT fold — each set's own tournament-eval-report.json
uv run python scripts/check_doc_facts.py

# (b) the REPLAY fold — re-seed the engine, walk every recorded tick, verify
#     every state hash; the only frame that can see mid-tick facts
uv run python -c "from pathlib import Path; from eval.kill_craft import compute_kill_craft_report as f
r = f(Path('replays/ml_corpus/9p2i')); print(r.kills_total, r.crew_witnessed_kills, dict(r.co_present_histogram))"

# (c) the TEXT fold — direct counts over the recorded replay-seed-*.jsonl rows
uv run python -c "import glob, json, collections
c = collections.Counter()
for p in glob.glob('replays/*/*/replay-seed-*.jsonl'):
    for line in open(p):
        row = json.loads(line)
        if row['kind'] == 'meeting':
            c['ballots'] += len(row['ballots']); c['turns'] += len(row['transcript']['turns'])
            c['skips'] += sum(b['target'] == 'SKIP' for b in row['ballots'])
        elif row['kind'] == 'tick':
            for a, d in zip(row['actions'], row['action_dispositions']):
                c[a['type'] + ':' + d] += 1
print(c['turns'], c['ballots'], c['skips'], c['kill:applied'], c['kill:rejected'])"
```

Which item comes from which. The headline cells of items 1, 8 and 9 are fold
(a), and `scripts/check_doc_facts.py` re-derives them on *every* gate run —
reading the four eval reports and failing on disagreement, so this section can
never be relabelled onto a new recording without its arithmetic moving with it.
Item 2's rejection causes, item 4, item 8's truthfulness cells and item 9's
kill census are fold (b), which reads the engine's own per-tick output rather
than inferring it from the transcript. Items 3, 5, 6, 7, item 1's action-stream
counts and item 2's submission counts are fold (c), straight counts over the
recorded rows.

The by-game split rule above assigns each game by its seed alone, never by what
the game contains, so no phenomenon below influenced which split it landed in.
That is the whole of what the rule buys, and it is a statement about the
*assignment*, not about the result: a phenomenon rare enough, or correlated with
the seed, can still end up entirely inside one split. How often anything below
actually occurs in train, val or test is a per-split measurement, and this
section does not currently publish one.

1. **The absolute reporter-innocence prior (structural).** The scripted FSM
   impostor never files a body report and never calls a meeting — the COVER
   branch is explicit: "after the kill the body is in the room and the impostor
   must not file a report" (`agents/tactical/impostor_policy.py:39-40`).
   Measured across all four sets: meetings crew-triggered **672/672**, opening
   turns crew-spoken **672/672**, and the tick streams carry **718/718**
   `report` and **69/69** `emergency` submissions by crew — zero
   impostor-originated, anywhere. 100% of training examples therefore embed
   "the reporter is innocent" as an absolute prior. A crew model fitted here
   has never seen a lying reporter, and any learned impostor that self-reports
   instantly invalidates the crew's learned prior. The prior is disclosed, not
   changed: the scripted policy is what it describes.

2. **Non-resolving kill submissions.** Of **1,033** submitted `kill` actions
   across the four sets, **834 resolved** and **199 (19.3%) produced no kill**
   — in two distinct ways. **161 were engine-rejected**, every single one of
   them on the same-room check (the engine's own recorded rejection reason
   reads `kill requires same room` on 161 of 161: the target was no longer
   co-located when the action applied mid-tick, and there are zero cooldown
   and zero dead-target rejections anywhere), and **38 were never evaluated at
   all** (an earlier `report`/`emergency` in the same tick moved the phase to
   MEETING before the kill applied — those were not necessarily illegal when
   submitted). Per set, non-resolving = rejected + pre-empted: S9
   **47/229 = 20.5%** (39 + 8), C9 **146/678 = 21.5%** (118 + 28), S4
   2/64 = 3.1% (1 + 1), C4 4/62 = 6.5% (3 + 1). At 9p, roughly one scripted
   kill decision in five fails to land, and most of those failures are outright
   illegal at application (39/229 = 17.0% S9, 118/678 = 17.4% C9) — a
   mover-quality limitation no eval report surfaces. The submitted counts and
   their verdicts are read off each tick row's recorded `action_dispositions`;
   the resolved counts — C9 532, S9 182, S4 62, C4 58 — are the engine walk's
   own kill census (`eval/kill_craft.py`), and the two agree set for set.

3. **Bracketed guard annotations, and where they no longer are.** The
   "Defaulted turns" section below rules that a frozen training/eval corpus
   **must not contain** fallback husks, and the freeze guard enforces that for
   `deadline_default` rows — all four sets carry **zero** defaulted turns. That
   guard keys on `error_type`, so it has never covered a second, unrelated
   class: the bracketed annotations the validators weld into recorded text when
   they drop or rewrite part of a model response. On the previous recording
   that class reached **player-visible** transcript text, and this item existed
   to record the resulting contradiction between the doctrine and the bytes.
   **It no longer reaches it.** Across all **3,631** transcript turns in the
   four sets, player-visible `free_text` carries **zero** bracketed annotations
   of any class — the `[invalid accusation target …]` and
   `[invalid corroboration supports …]` classes this item was named for occur
   nowhere in these 300 games. The contradiction is closed on the surface a
   player or a crew model reads.

   The class survives on the surface it always sat on: **ballot**
   `rationale_text`, which is never shown to players but is committed and
   trainable. **113/3,631 ballots (3.1%)** carry at least one — S9 30/869
   (3.5%), C9 80/2,516 (3.2%), S4 1/117, C4 2/129 — in six kinds:
   `[under-gate eject target … redirected]` (83: 23 S9 / 57 C9 / 1 S4 / 2 C4),
   `[invalid primary_reason… nulled]` variants (20: 4 S9 / 16 C9),
   `[teammate target … coerced to SKIP]` (7: 2 S9 / 5 C9 — machinery that
   names the impostor's ally in the record), `[rationale redacted by the vote
   guard…]` (7: 2 S9 / 5 C9), `[uncited zero-flag eject target … coerced]`
   (6, C9 only) and `[invalid target … normalized to SKIP]` (4: 2 S9 / 2 C9).
   A few ballots carry two kinds, which is why the kinds sum to 127 over 113
   ballots. Anything fitted on ballot text is fitting on machinery output at
   this rate; anything fitted on transcript text now is not.

4. **Zombie-vent re-litigation.** Dead impostors' vents still get re-argued,
   but far less often than they used to: **8/151 S9 meetings (5.3%)** and
   **42/439 C9 meetings (9.6%)** contain a `saw_vent` observation whose subject
   was already dead when the meeting opened — **50/672 meetings (7.4%)** across
   the four sets, touching 43 of the 200 9p games (21.5%), with both 4p sets at
   zero. That is **52 of the 512** `saw_vent` observations recorded anywhere
   (10.2%). Every one of the 52 names an impostor who had already been
   **ejected** in an earlier meeting of the same game; not one names a killed
   crewmate. The structured `claims[]` arrays are clean — **0 of 3,114**
   accusation claims name a dead player, because the validator drops those —
   and, unlike the previous recording, that dropping now leaves no visible
   residue in player-facing text at all (item 3). Worst meetings: two drops,
   in C9 seed 1019 meeting-1 and C9 seed 1149 meeting-1; the S9 maximum is one.
   Deaths are resolved against the engine walk's own alive set at the moment
   each meeting opened, not inferred from the transcript.

5. **Skip-template repetition.** Skips are encoded as `target == "SKIP"`
   (there are no null targets: 0 of 3,631 ballots carry one). Skip shares: S9
   342/869 = 39.4%, C9 1,017/2,516 = 40.4%, S4 66/117 = 56.4%, C4 60/129 =
   46.5% of ballots. Among skip ballots, exact-duplicate `rationale_text`
   copies (beyond each string's first use): S9 **6/342 = 1.8%**, C9
   **70/1,017 = 6.9%**, S4 0/66, C4 0/60 — and **103/1,485 = 6.9%** pooled,
   which is fractionally above the highest single set because the same template
   strings recur *across* sets (the most-repeated one appears 16 times across
   three of the four sets — 13 of them inside C9). The repetition is almost entirely
   a skip phenomenon: 103 of the 107 redundant ballot copies are skips.
   Transcript `free_text`, by contrast, is byte-unique — 3,631/3,631 distinct
   across all four sets, zero exact repeats anywhere.

6. **Wait-streak and ping-pong mover theater.** Two scripted-mover artifacts
   with mirror-image role signatures. Neither is absolute on these bytes, and
   both are rarer than they were. **Wait streaks** (longest run of
   consecutive-tick `wait` actions per player-game; meetings do not break a
   run): **100/2,200 player-games (4.5%) idle ≥10 consecutive ticks — 99 crew,
   1 impostor**. Per set: S9 20/450 (longest 23 ticks: seed 27 `p-8`, ticks
   17–39), C9 75/1,350 (longest 29: seed 1085 `p-9`, ticks 19–47), S4 4/200
   (longest 13: seed 36 `p-4`, ticks 4–16), C4 1/200 (12 ticks). The single
   impostor streak is S9 seed 27 `p-7`, 14 ticks — so "only crew stand still"
   is a strong tendency here, not the invariant it was. **Ping-pong pathing**
   (a minted definition, disclosed as such: ≥4 consecutive-tick `move` actions
   strictly alternating between exactly two rooms): **31/2,200 player-games
   (1.4%), 30 of the 31 impostors** — 30/500 = 6.0% of impostor player-games
   versus 1/1,700 = 0.06% of crew. Per set: S9 8/450, C9 23/1,350, and zero
   in both 4p sets. Longest: 8 alternating
   moves (C9 seed 1111 `p-1`, ADMIN↔EAST_HALL); S9's longest is 4. The lone
   crew instance is C9 seed 1098 `p-1`, 4 moves MEDBAY↔WEST_HALL. The two
   artifacts remain mirror images: crew theater is standing still, impostor
   theater is pacing — but both are now weak enough that a detector trained on
   either would be fitting a handful of games.

7. **Model-originated fourth-wall statements and machinery quotation.** The
   fourth wall now holds completely in *player-visible* text and fails
   routinely in *recorded private* text — a sharper split than the previous
   recording showed, in both directions. Ballot `rationale_text` (never shown
   to players, but committed and trainable): **36/218 = 16.5% of S9** and
   **137/636 = 21.5% of C9** impostor-voter ballots name a partner ("my
   partner" / "my teammate" / "my fellow impostor"; a looser phrase net reaches
   46 and 159; both 4p sets are zero, having one impostor and so no partner to
   name; crew false-positive control **0/2,695**), and **62 of the 936**
   impostor ballots state the role outright (10 S9, 39 C9, 5 S4, 8 C4) — C4
   seed 1011's "I am the impostor. I skip to survive." is the bluntest.
   Player-visible `free_text` carries **zero** fourth-wall leaks in all 3,631
   turns: no partner phrase and no role statement reaches a surface another
   player reads, on any of the four sets.

   Machinery quotation has gone to zero in both registers. Literal
   implementation tokens in model output: **none** — `vent_sighting`,
   `alibi_vs_sighting`, `[weak signal`, `roll_call`, `absence_prior`,
   `hard_evidence_gate`, `citation_gate` appear in no transcript turn and no
   ballot rationale, and the only `primary_reason` occurrences in persisted
   text (20 ballots: 4 S9, 16 C9) are the guard-injected `[invalid
   primary_reason… nulled]` prefixes of item 3, not quotation — parse each
   recorded `llm_calls[].response_text` and its own rationale and free-text
   fields carry zero such tokens. *Natural-language* machinery talk has gone
   with them: "threshold" appears in **0 of 3,631** ballot rationales and **0
   of 3,631** transcript turns, and a quoted internal decimal (`0.NN`) in
   **0 of 3,631** of either. Both ran at several per cent of ballots on the
   previous recording; the templates that invited that voice were rewritten at
   this one. What is left is ordinary deduction vocabulary at a low rate:
   "suspicion" in 17/3,631 ballot rationales (0 S9, 11 C9, 2 S4, 4 C4) and
   43/3,631 transcript turns (8 S9, 31 C9, 4 S4, 0 C4) — a word a deduction
   game says naturally, and an upper bound on anything stronger. **Nothing in
   these bytes reproduces the scoring internals**, so a model fitted here
   cannot learn to read them back.

8. **Role-correlated public response shape.** The share of a role's transcript
   turns carrying a structured `whereabouts` observation (the roll-call
   answer), pooled over turns: crew S9 **651/651 = 100.0%**, crew C9
   **1,880/1,880 = 100.0%**, crew S4 **78/78 = 100.0%** and crew C4 **86/86 =
   100.0%**, versus impostor S9 **106/218 = 48.6%**, impostor C9 **292/636 =
   45.9%**, impostor S4 **6/39 = 15.4%** and impostor C4 **3/43 = 7.0%**. The
   estimator matters and is named: the *unweighted per-meeting macro-average*
   of the same bytes reads 45.4% (S9) and 42.0% (C9) for the impostor side
   (`deduction.public_response_coverage`); the pooled turn-level figures above
   are the headline here. The mechanism is the templates' role-differentiated
   output contract, not model choice: the role-blind info-share/roll-call
   surface elicits whereabouts from both roles (impostor `opt_in` turns answer
   106/106 in S9, 292/292 in C9, 6/6 in S4 and 3/3 in C4), but the impostor
   REPLY surface hard-codes `observations: []` (0/112 S9, 0/344 C9, 0/33 S4,
   0/40 C4) while the crew reply carries the full vocabulary (76/76 S9, 217/217
   C9, 9/9 S4, 9/9 C4) — and impostors are disproportionately in reply position
   (112/218 of their turns vs 76/651 for crew in S9; 344/636 vs 217/1,880 in
   C9). So the tell is the *absent* observation, and it is absolute: on these
   bytes no crew turn anywhere lacks a whereabouts answer and no impostor reply
   carries one.

   The whereabouts that *are* recorded are almost never lies. Counting
   whereabouts *observations* (a turn may carry more than one) against the
   pre-advance decision frame — the reconstructed state each recorded tick's
   actions were decided against, read from `eval/replay_walk.py`'s per-tick
   pre-advance state, the same frame as item 9's census — impostor
   self-placements match the reconstructed room in **105/106 = 99.1%** (S9),
   **290/294 = 98.6%** (C9), 6/6 (S4) and 3/3 (C4); the crew figures are
   **654/660 = 99.1%** (S9), **1,901/1,920 = 99.0%** (C9), 79/79 (S4) and
   88/89 (C4). Pooled over all four sets: crew **2,722/2,748 = 99.1%** and
   impostors **404/409 = 98.8%**. Every observation resolved in this frame —
   there is no observation whose claimed tick the walk could not reconstruct.
   **Impostors essentially do not lie in the one structured channel the alibi
   rules prosecute** — anything fitted on "impostors lie in roll call" is
   fitted on nothing. Note that the two sides now match at the same rate, so
   the truthfulness of a whereabouts answer carries no role signal at all; only
   its *presence* does.

9. **The too-clean evidence economy.** Across all **834** resolved kills in
   the four sets, the pre-advance decision frame shows **zero** kills with any
   non-victim living crew co-present in the kill room (co-present histogram
   `{0: 834}`, from `eval/kill_craft.py`'s per-set fold), and only
   **22/834 = 2.6%** were crew-witnessed at all (18 C9 / 3 S9 / 1 S4 / 0 C4 —
   every witness a same-tick one-hop arrival, a mid-tick engine fact that only
   the engine walk can read). The scripted impostor kills only isolated targets
   (`agents/tactical/impostor_policy.py` KILL guard), so the corpus supplies
   almost no direct kill testimony: convictions ride the post-kill vent tell
   instead, and a crew stack trained here has effectively never seen a
   contested kill scene.

Every cell in this section was re-derived on the committed bytes at this
recording. The next re-record of all four sets moves every one of them again,
and the same three commands re-derive them.

## Recording (operator, `$0`, ~12h MEASURED)

This is an operator-run step gated on `FEATHERLESS_API_KEY`; it is **not** run in
CI or by an agent session (the fake CI provider is refused — the corpus records
only on Featherless). These are the measured walls of the record that produced
the committed bytes, not estimates — all four sets in one window:

| leg | games | wall clock |
|---|---|---|
| `replays/samples/9p2i` | 50 | 3h 07m 00s |
| `replays/ml_corpus/9p2i` | 150 | 7h 59m 32s |
| `replays/samples/4p1i` | 50 | 0h 23m 15s |
| `replays/ml_corpus/4p1i` | 50 | 0h 27m 48s |
| **four legs, one window** | **300** | **12h 21m 01s** at **`$0.0000`** |

The four leg walls sum to 11h 57m 35s; the window total is 23m 26s longer
because the last leg did not run straight through — a hard provider
account-balance refusal stopped it at 49 of its 50 seeds, and it was completed
on a resume. That is the resumable path below working as designed, and it is
recorded here rather than smoothed into the leg row.

Treat the previous recording's figures as history — it took roughly twice as
long for the same 300 games, and the corpus legs alone (0h 47m 01s at 4p1i,
16h 00m 16s at 9p2i, plus a 12m 33s repair pass) took more than the whole
window does now. The prompt set is shorter per meeting call than it was.
Note the wall clock includes any time the machine spends asleep — a
suspend pauses the run rather than corrupting it. Apply the accumulated
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
export AILIBI_LLM_PROVIDER=featherless  # the locked baseline-8 provider
export AILIBI_PROMPT_SET=qwen3_6_27b    # the locked baseline-8 prompt set
export AILIBI_SEED_MAX_ATTEMPTS=8       # raised transport retry budget for the long run
bash scripts/record_ml_corpus.sh --set 4p1i    # short leg first
bash scripts/record_ml_corpus.sh --set 9p2i    # then the long leg
```

Those four exports are the **whole** recording environment. The twenty-one retired
levers are unconditional in code and need no env at all; `AILIBI_IMPOSTOR_ROLL_CALL`
must stay **UNSET** (see below).

The preflight locks the full baseline-8 substrate, not just the provider:

- **the lever slate.** The preflight POSITIVELY checks the live substrate
  snapshot equals the ruled baseline-8 state — the twenty-one retired levers ON and
  `impostor_roll_call` OFF — and refuses before any seed stages. A leftover
  `AILIBI_IMPOSTOR_ROLL_CALL` export would ship the **unshipped** impostor-answer
  arm into the record while the echo claimed the ruled substrate, and an
  acceptance gate run in the same polluted shell would then PASS coherently
  (`substrate_flag_snapshot()` reads the same env) — the C6 recording-preflight
  hazard the graduations discharge. Because the check compares the *slate* rather
  than blacklisting a variable name, it also catches a partial graduation and any
  future toggleable-set drift. This mirrors the preflight in
  `scripts/refresh_samples.sh`.
- **the model.** A leftover `AILIBI_LLM_MEETING_MODEL` / `AILIBI_LLM_TRIGGER_MODEL`
  export from a model sweep is refused unless it names the baseline model
  (`Qwen/Qwen3.6-27B`).
- **the endpoint.** A non-default `AILIBI_FEATHERLESS_BASE_URL` (a mock/staging
  endpoint) is refused outright.

All three knobs are then exported pinned so the recorded substrate can never
drift from the one the `MANIFEST` stamps. The prompt **versions** are locked too,
not just the set name: the preflight asserts the registry still resolves
`qwen3_6_27b` to the baseline-8 map (all four templates at v5), and the finalize
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
**bytes** carry the full baseline-8 provenance —

- the canonical **five-field** `fsm-default` tactical-policy stamp (not just
  its id: a hand-crafted stamp with non-canonical method/encoder/weights/anchor
  fields renders identically in the `MANIFEST`);
- the locked model (`Qwen/Qwen3.6-27B`) on **every** recorded call (meeting calls
  and failed-call rows alike, so a wall-clock-miss phantom or a foreign-model
  recording is refused);
- exactly `$0` recorded cost;
- the **baseline-8 lever slate** stamped **positively** on the `game_over` record
  (the same tolerant per-lever match the validity gate and the loader enforce:
  every one of the twenty-one retired levers present and True — including the
  meeting-layer graduations `roll_call_round` / `whereabouts_interior_flags` /
  `vent_placement_contradictions` / `absence_prior` — and `impostor_roll_call`
  OFF). This asserts the slate in the recorded bytes, not just the env refusal,
  so a replay from an older substrate, whose stamp carries one of those levers
  OFF, is refused **at the recorder**, not only at the external validity gate.
  That refusal is what turns a substrate change into a re-record rather than a
  resume: pointed at a corpus recorded before a graduation, the guard refuses
  every replay in it by name.

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

**Expect to iterate.** Two records ago the repair pass ran to 10 of 150 seeds
and cost 2h43m; the one before these bytes paid 2 of 150 in 12m33s. The
committed bytes carry **zero** `deadline_default` rows on all four sets, which
is what a clean freeze means — but budget a repair pass anyway: the rate is a
property of meeting length, and a re-recorded seed can pick up a fresh default.
The deadline cannot be widened to compensate without changing the locked
substrate, so re-recording is the only honest fix — the seed re-records clean
and its `MANIFEST` row honestly stamps the re-record date:

```bash
# after a refused freeze: drop the offending replays, then resume
bash scripts/record_ml_corpus.sh --set 9p2i     # records ONLY the dropped seeds, then re-finalizes
```

Re-recorded seeds have come back clean on the first retry at every record so
far. **A refused freeze costs only the bad seeds**, never the good ones:
provenance is checked separately from presence, so hours of recorded work
survive the refusal untouched. The same separation is what let the interrupted
4p1i leg of this record resume over its 49 completed seeds rather than re-run
them.

> **Dropping phantoms while the leg still runs is safe — the finalize refuses a
> short set.** `check_seed_count` asserts the exact contiguous locked set
> (every seed in the range, no gap) is on disk before `build_sample_report` /
> `write_splits` / `freeze_manifest`, and again in `--splits-only`. So if a
> defaulted replay is dropped from a still-running or resumed leg (or any in-range
> replay is lost), the finalize fails loud with the missing seeds named rather
> than globbing a short set into a frozen 146-game corpus. Still, the tidy order
> is to drop after the drain: the guard turns a mistimed drop into a hard stop,
> not a silent corruption.

An unstamped replay (a recording that predates the stamp, a canonical sample
copied in) is
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
and freeze it before running the acceptance gate. A session spanning a UTC
midnight is expected at the measured **~12h** for all four sets (see the section
header for the per-leg breakdown); `MANIFEST` dates are honest per-seed, so
mixed dates across a set are correct rather than suspect — the gate checks
coherence, not uniformity.

## Finding these bytes later: the annotated tag

The `FROZEN` line in each `MANIFEST.md` names the **recording-time code state** —
`HEAD` at the moment the recorder ran, i.e. the engine/prompt/lever version that
*produced* the bytes. It is deliberately **not** a pointer to the commit that
*contains* them: that commit does not exist yet when the freeze line is written,
so no recorder could name it. Checking that sha out gives you the generating code,
not the corpus.

The pointer to the bytes is an **annotated tag** cut after the record lands.
Dispatch environments refuse tag pushes, so this is an operator-session step:

```bash
git tag -a "baseline-8-corpus-$(git rev-parse --short HEAD)" -m "…substrate + acceptance…"
git push origin "baseline-8-corpus-$(git rev-parse --short HEAD)"
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
