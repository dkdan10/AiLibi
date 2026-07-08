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
