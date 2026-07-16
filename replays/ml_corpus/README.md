# ML-calibration corpus (Task 15.12, re-grounded onto baseline 5 by Task 17.9)

The frozen training/calibration corpus the ballot surrogate (15.13) and the
impostor bake-off (15.15+) consume, recorded at **exact baseline-5 config** —
the locked Phase-16 substrate: `Qwen/Qwen3.6-27B` on Featherless (non-thinking,
`fail_loud`, `json_object`), the `qwen3_6_27b` prompt set (all four templates —
`accusation_round`, `crewmate_report`, `impostor_report`, `vote_ballot` — at
**v3**), the **graduated lever slate** (`hard_evidence_gate` /
`observation_id_rendering` / `citation_gate` unconditionally ON, `absence_prior`
default-**OFF**), `$0` flat-rate — with the 15.9 FSM-default tactical-policy stamp
on every game. The model was locked 2026-07-12 at Task 16.2
(`audits/audit-phase-16-model-lock.md`); the three lever graduations and the
`absence_prior` stay-OFF are the Task-16.17 slate
(`audits/audit-phase-16-close.md` §0.1).

Nothing trains against a meeting layer scheduled to change
(`tasks/post-phase-14-plan.md` §4;
`audits/post-phase-14-ML-training-signal.md` §5.6, §7.2), so this corpus is a
**separate release artifact** from the canonical `replays/samples/` baseline. It
uses **fresh seed ranges** so a corpus game can never be confused with a
canonical 0–49 game.

> **Canary denominator — the Q3 restoration.** With this baseline-5 re-record the
> corpus is again the **canonical canary denominator**: the mid-Phase-15 Q3 ruling
> (the ML corpus is the canary denominator; the canonical `replays/samples/`
> baseline is the continuity anchor) was **DEGRADED through Phase 16** — quoted as
> STALE CONTEXT only while the corpus sat two substrate rungs behind
> (`audits/audit-phase-16-close.md` §0.4, §8) — and is **operative again from this
> record**. Future phase closes re-adopt it (`tasks/phase-17.md`, designer
> rulings).

> **These bytes are the baseline-5 re-record (Task 17.9).** Both sets under
> `9p2i/` and `4p1i/` were re-recorded at baseline 5 by an operator session and
> pass the acceptance gate: `validity_gate.py --expected-model Qwen/Qwen3.6-27B
> --require-zero-cost` is 10/10 green on each, reconstruction is byte-identical,
> every recorded `game_over` stamp carries the graduated-lever slate + the locked
> model + `$0` cost, and the `FROZEN` line in each `MANIFEST.md` names the
> recording commit. The recorder's freeze-path guards (`check_replay_provenance`
> — the model, the `$0` cost, and the **graduated-lever slate** on every recorded
> stamp) now PASS over the committed bytes by construction; they refuse anything
> off-substrate (the prior baseline-3 recording, a phantom seed) from being
> resumed-over and frozen.

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

## Recording (operator, `$0`, ~14–15h)

This is an operator-run step gated on `FEATHERLESS_API_KEY`; it is **not** run in
CI or by an agent session (the fake CI provider is refused — the corpus records
only on Featherless). Baseline-5 meetings run **~2× baseline-3**, so plan
**~14–15h** wall for both sets — roughly double the stale ~7h baseline-3 estimate
— with the 16.14/16.17 operator notes applied (staggered worker starts, jittered
backoff, per-seed atomic staging, `AILIBI_SEED_MAX_ATTEMPTS=8`). Preview the plan
first:

```bash
bash scripts/record_ml_corpus.sh --dry-run
```

Then record both sets (2 Featherless seed workers, per-seed transport
crash-retry) from a **bare** lever environment — record the short 4p1i set first
to validate the pipeline end to end, then the long 9p2i leg:

```bash
export FEATHERLESS_API_KEY=...          # hosted flat-rate; recorded as $0
export AILIBI_PROMPT_SET=qwen3_6_27b    # the locked baseline-5 prompt set
export AILIBI_SEED_MAX_ATTEMPTS=8       # raised transport retry budget for the long run
bash scripts/record_ml_corpus.sh --set 4p1i    # short leg first
bash scripts/record_ml_corpus.sh --set 9p2i    # then the long leg
```

The preflight locks the full baseline-5 substrate, not just the provider: a
leftover `AILIBI_LLM_MEETING_MODEL` / `AILIBI_LLM_TRIGGER_MODEL` export from a
model sweep is refused unless it names the baseline model
(`Qwen/Qwen3.6-27B`), a non-default `AILIBI_FEATHERLESS_BASE_URL` (a mock/staging
endpoint) is refused outright, and all three knobs are then exported pinned so
the recorded substrate can never drift from the one the `MANIFEST` stamps. The
one remaining live lever, `absence_prior`, is the slate's recorded **stay-OFF**:
any `AILIBI_ABSENCE_PRIOR` export — truthy or not — is refused, because the
documented recording environment is bare and a leftover export would record the
whole multi-hour corpus lever-ON while the echo claims the OFF substrate. The
prompt **versions** are locked too, not just the set name: the preflight asserts
the registry still resolves `qwen3_6_27b` to the baseline-5 map (all four
templates at v3), and the finalize refuses to freeze a set unless every
meeting-bearing `MANIFEST` row carries **exactly** that map (a foreign version
string AND a stripped/partial row both refuse — the manager stamps the full set
map on every meeting, so anything short of the exact four is missing provenance)
— a later registry bump stops the recorder cold instead of silently recording
(or resuming into) a non-baseline corpus. The recorder also refuses a set dir
containing any `replay-seed-*.jsonl` outside the set's locked seed range (checked
before recording and again before freezing), so a stray file can never be swept
into the frozen corpus or its splits.

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
**bytes** carry the full baseline-5 provenance —

- the canonical **five-field** 15.9 `fsm-default` tactical-policy stamp (not just
  its id: a hand-crafted stamp with non-canonical method/encoder/weights/anchor
  fields renders identically in the `MANIFEST`);
- the locked model (`Qwen/Qwen3.6-27B`) on **every** recorded call (meeting calls
  and failed-call rows alike, so a wall-clock-miss phantom or a foreign-model
  recording is refused);
- exactly `$0` recorded cost;
- the **graduated-lever slate** stamped **positively** on the `game_over` record
  (the same tolerant per-lever match the validity gate and the loader enforce:
  every retired always-on lever present and True — including the three Phase-16
  graduations `hard_evidence_gate` / `observation_id_rendering` / `citation_gate`
  — and `absence_prior` OFF). This asserts the slate in the recorded bytes, not
  just the env refusal, so a **stale baseline-3 replay** (which carries the
  six-lever slate, missing the three graduations) is refused **at the recorder**,
  not only at the external validity gate.

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
and freeze it before running the acceptance gate. A ~14–15h session spanning UTC
midnight is expected; `MANIFEST` dates are honest per-seed (the 16.14 mixed-date
precedent — the gate checks coherence, not uniformity).

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
