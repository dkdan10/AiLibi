# ML-calibration corpus (Task 15.12, re-grounded onto baseline 6 by Task 18.13)

The frozen training/calibration corpus the ballot surrogate (15.13) and the
impostor bake-off (15.15+) consume, recorded at **exact baseline-6 config** —
the adopted Phase-18 substrate: `Qwen/Qwen3.6-27B` on Featherless (non-thinking,
`fail_loud`, `json_object`), the `qwen3_6_27b` prompt set (all four templates —
`accusation_round`, `crewmate_report`, `impostor_report`, `vote_ballot` — at
**v3**), the **baseline-6 lever slate** (the thirteen retired always-on levers,
which since Task 18.12 include the four meeting-layer graduations
`roll_call_round` / `whereabouts_interior_flags` /
`vent_placement_contradictions` / `absence_prior`, with `impostor_roll_call` the
**sole live toggle** and its recorded state **OFF**), `$0` flat-rate — with the
15.9 FSM-default tactical-policy stamp on every game. The model was locked
2026-07-12 at Task 16.2 (`audits/audit-phase-16-model-lock.md`); the four
meeting-layer graduations and the `impostor_roll_call` stay-OFF are the CREW-ONLY
ruling of `audits/audit-phase-18-meeting-gate.md` §9, adopted at the Task-18.12
record (`audits/audit-phase-18-baseline-6.md` §0.1). Baseline 6 graduated
**levers, not templates**, so the locked v3 prompt map is unchanged from
baseline 5.

Nothing trains against a meeting layer scheduled to change
(`tasks/post-phase-14-plan.md` §4;
`audits/post-phase-14-ML-training-signal.md` §5.6, §7.2), so this corpus is a
**separate release artifact** from the canonical `replays/samples/` baseline. It
uses **fresh seed ranges** so a corpus game can never be confused with a
canonical 0–49 game.

> **This record discharges the Phase-18 staleness rule.**
> `audits/audit-phase-17-close.md` §5 ruled that "a Phase-18 meeting-layer change
> … makes the corpus PRIOR-SUBSTRATE-ANCHORED again — re-record before any
> training against it." The Task-18.12 meeting-layer graduation was exactly that
> change, and this re-record discharges the rule: the corpus and the canonical
> samples now sit at the **same** substrate rung (samples at 18.12, corpus here),
> so nothing downstream trains across a substrate seam. Everything fitted,
> selected, or pinned on the **baseline-5** corpus (the 17.10 surrogate, the
> 17.12/17.14 bake-off rankings and finalist rows) is prior-substrate-anchored
> and re-grounds against these bytes — that re-grounding is Task 18.14's.

> **Canary denominator — the Q3 restoration.** With this baseline-6 re-record the
> corpus is again the **canonical canary denominator**: the mid-Phase-15 Q3 ruling
> (the ML corpus is the canary denominator; the canonical `replays/samples/`
> baseline is the continuity anchor) was DEGRADED through Phase 16 while the
> corpus sat two substrate rungs behind, restored at the baseline-5 re-record
> (Task 17.9), and **re-lapsed for exactly the interval between the Task-18.12
> samples record and this one** — the window in which the samples were baseline 6
> and the corpus was not. It is **operative again from this record**: the corpus
> is the canary denominator, the 18.12 baseline-6 samples are the continuity
> anchor, and future phase closes re-adopt the pairing
> (`audits/audit-phase-17-close.md` §3 is the worked example of a close reading
> anchors off the restored denominator).

> **These bytes are the baseline-6 re-record (Task 18.13).** Both sets under
> `9p2i/` and `4p1i/` were re-recorded at baseline 6 by a local operator session
> and pass the acceptance gate: `validity_gate.py --expected-model
> Qwen/Qwen3.6-27B --require-zero-cost` is green on each, reconstruction is
> byte-identical, every recorded `game_over` stamp carries the baseline-6 lever
> slate + the locked model + `$0` cost, and the `FROZEN` line in each
> `MANIFEST.md` names the recording commit. The recorder's freeze-path guards
> (`check_replay_provenance` — the model, the `$0` cost, and the **baseline-6
> lever slate** on every recorded stamp) now PASS over the committed bytes by
> construction; they refuse anything off-substrate (the prior baseline-5
> recording, whose stamp carries the four meeting-layer levers OFF; a phantom
> seed) from being resumed-over and frozen.

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

## Recording (operator, `$0`, ~22–23h MEASURED)

This is an operator-run step gated on `FEATHERLESS_API_KEY`; it is **not** run in
CI or by an agent session (the fake CI provider is refused — the corpus records
only on Featherless). The Task-18.13 record is the measured figure, not an
estimate:

| leg | wall clock |
|---|---|
| 4p1i (50 games) | 0h 45m |
| 9p2i (150 games) | 19h 26m |
| phantom-repair pass (10 seeds, see below) | 2h 43m |
| **total** | **~22h 54m** |

Baseline-5 ran ~14–15h; the baseline-6 roll-call round adds ~36% meeting LLM
calls and drives the 9p2i meeting rate to **1.00**, so budget **~22–23h** and
treat both the ~14–15h baseline-5 figure and the pre-record ~18–20h projection as
stale. Note the wall clock includes any time the machine spends asleep — a
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
export AILIBI_LLM_PROVIDER=featherless  # the locked baseline-6 provider
export AILIBI_PROMPT_SET=qwen3_6_27b    # the locked baseline-6 prompt set
export AILIBI_SEED_MAX_ATTEMPTS=8       # raised transport retry budget for the long run
bash scripts/record_ml_corpus.sh --set 4p1i    # short leg first
bash scripts/record_ml_corpus.sh --set 9p2i    # then the long leg
```

Those four exports are the **whole** recording environment. The thirteen retired
levers are unconditional in code and need no env at all; `AILIBI_IMPOSTOR_ROLL_CALL`
must stay **UNSET** (see below).

The preflight locks the full baseline-6 substrate, not just the provider:

- **the lever slate.** The preflight POSITIVELY checks the live substrate
  snapshot equals the ruled baseline-6 state — the thirteen retired levers ON and
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
`qwen3_6_27b` to the baseline-6 map (all four templates at v3), and the finalize
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
**bytes** carry the full baseline-6 provenance —

- the canonical **five-field** 15.9 `fsm-default` tactical-policy stamp (not just
  its id: a hand-crafted stamp with non-canonical method/encoder/weights/anchor
  fields renders identically in the `MANIFEST`);
- the locked model (`Qwen/Qwen3.6-27B`) on **every** recorded call (meeting calls
  and failed-call rows alike, so a wall-clock-miss phantom or a foreign-model
  recording is refused);
- exactly `$0` recorded cost;
- the **baseline-6 lever slate** stamped **positively** on the `game_over` record
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

**Expect to iterate.** Across the Task-18.13 record, roughly **1 recording in 8**
produced a defaulted turn of some shape, and a re-recorded seed can pick up a
fresh one (seed 1115 did). Budget a repair pass or two; the 18.12 samples record
hit only 1/150, so the rate is a property of the longer baseline-6 meetings. The
deadline cannot be widened to compensate without changing the locked substrate, so
re-recording is the only honest fix (`audits/audit-phase-16-close.md` §5.2's
runbook rule: the seed re-records clean and its MANIFEST row honestly stamps the
re-record date):

```bash
# after a refused freeze: drop the offending replays, then resume
bash scripts/record_ml_corpus.sh --set 9p2i     # records ONLY the dropped seeds, then re-finalizes
```

All 10 came back clean on the first retry. **A refused freeze costs only the bad
seeds**, never the good ones: provenance is checked separately from presence, so
19 hours of recorded work survived the refusal untouched.

> **Drop the phantoms only AFTER the leg drains.** The finalize has no "all N
> present" assertion — it discovers seeds by globbing the set dir — so deleting
> replays while the run is still going would let `write_splits` and the MANIFEST
> backfill freeze a SHORT set (e.g. 146 games) as if it were complete.

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
several UTC midnights is expected at ~18–20h; `MANIFEST` dates are honest
per-seed (the 16.14 mixed-date precedent — the gate checks coherence, not
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
