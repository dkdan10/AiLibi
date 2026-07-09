# ML-calibration corpus (Task 15.12)

The frozen training/calibration corpus the ballot surrogate (15.13) and the
impostor bake-off (15.15+) consume, recorded at **exact baseline-3 config** —
the 15.7 substrate: `Qwen/Qwen3-32B` on Featherless (non-thinking, `fail_loud`,
`json_object`), the `qwen3_32b` prompt set (turn/opening at **v5**, `vote_ballot`
at **v6**), all substrate levers unconditionally ON, `$0` flat-rate — with the
15.9 FSM-default tactical-policy stamp on every game.

Nothing trains against a meeting layer scheduled to change
(`tasks/post-phase-14-plan.md` §4;
`audits/post-phase-14-ML-training-signal.md` §5.6, §7.2), so this corpus is a
**separate release artifact** from the canonical `replays/samples/` baseline. It
uses **fresh seed ranges** so a corpus game can never be confused with a
canonical 0–49 game.

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
the loader is 15.11's).

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

## Recording (operator, `$0`, ~7h)

This is an operator-run step gated on `FEATHERLESS_API_KEY`; it is **not** run in
CI or by an agent session (the fake CI provider is refused — the corpus records
only on Featherless). Preview the plan first:

```bash
bash scripts/record_ml_corpus.sh --dry-run
```

Then record both sets (2 Featherless seed workers, per-seed transport
crash-retry):

```bash
export FEATHERLESS_API_KEY=...        # hosted flat-rate; recorded as $0
export AILIBI_PROMPT_SET=qwen3_32b    # the locked baseline-3 prompt set
bash scripts/record_ml_corpus.sh      # --set 9p2i|4p1i|both (default both)
```

The preflight locks the full baseline-3 substrate, not just the provider: a
leftover `AILIBI_LLM_MEETING_MODEL` / `AILIBI_LLM_TRIGGER_MODEL` export from a
model sweep is refused unless it names the baseline model, a non-default
`AILIBI_FEATHERLESS_BASE_URL` (a mock/staging endpoint) is refused outright, and
all three knobs are then exported pinned so the recorded substrate can never
drift from the one the `MANIFEST` stamps. The prompt **versions** are locked
too, not just the set name: the preflight asserts the registry still resolves
`qwen3_32b` to the baseline-3 map (turn/opening v5, `vote_ballot` v6), and the
finalize refuses to freeze a set unless every meeting-bearing `MANIFEST` row
carries **exactly** that map (a foreign version string AND a stripped/partial
row both refuse — the manager stamps the full set map on every meeting, so
anything short of the exact four is missing provenance) — a later registry bump
stops the recorder cold instead of silently recording (or resuming into) a
non-baseline corpus. The recorder also refuses a
set dir containing any `replay-seed-*.jsonl` outside the set's locked seed range
(checked before recording and again before freezing), so a stray file can never
be swept into the frozen corpus or its splits.

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
**bytes** carry the full baseline-3 provenance — the canonical **five-field**
15.9 `fsm-default` tactical-policy stamp (not just its id: a hand-crafted stamp
with non-canonical method/encoder/weights/anchor fields renders identically in
the `MANIFEST`), the locked model on **every** recorded call (meeting calls and
failed-call rows alike, so a wall-clock-miss phantom or a foreign-model
recording is refused), and exactly `$0` recorded cost. An unstamped replay (a
pre-15.9 recording, a canonical sample copied in) is refused for the same
reason: it would render in the `MANIFEST` policy column identically to a
stamped one and the validity gate does not check the stamp. A fully-recorded
set records nothing and just re-finalizes, so re-running is always safe and
idempotent:

```bash
export FEATHERLESS_API_KEY=... AILIBI_PROMPT_SET=qwen3_32b
bash scripts/record_ml_corpus.sh --set 9p2i           # resumes from wherever it left off
```

For a long, flaky hosted run, raise the per-seed transport retry budget:
`AILIBI_SEED_MAX_ATTEMPTS=8 bash scripts/record_ml_corpus.sh --set 9p2i`. A set
directory that carries `replay-seed-*.jsonl` but no `FROZEN` line in its
`MANIFEST.md` is a **partial** (not-yet-finished) recording — re-run to complete
and freeze it before running the acceptance gate.

## Acceptance (per set, before the PR merges)

Hosted models do not byte-reproduce **fresh** generation; **recordings** replay
byte-identically (the loosened contract the canonical baselines already carry),
so the validity gate + byte-verify — not generation-replay equality — is the
acceptance:

```bash
uv run python scripts/validity_gate.py replays/ml_corpus/9p2i \
    --expected-model Qwen/Qwen3-32B --require-zero-cost
scripts/verify_samples.sh replays/ml_corpus/9p2i
# ... and again for 4p1i
```
