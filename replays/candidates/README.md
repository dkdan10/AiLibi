# Candidate rounds

This directory holds recordings made to assess experimental switches before
anyone decides to adopt them. They are kept in the tree so every change
re-verifies them, and they are not the canonical sample sets.

**An experimental switch** is one setting of a recording's experiment config: a
field that is off by default and, when turned on, changes how the game is played
or how a meeting runs. A recording writes its settings on every row, so it
always says which switches it was made with. The fields and their values are
listed in [the experiment arms page](../../docs/experiment-arms.md).

**A candidate round** is one such assessment: a set of games recorded with a
single declared config that turns one or more switches on, stored under
`replays/candidates/<round>/`. A round records nothing about whether its
switches are good. That reading happens after the recording, against questions
fixed before it started.

## What a candidate is not

- **Not canonical.** The committed sets under `replays/samples/` and
  `replays/ml_corpus/` are recorded with every switch off, and a candidate never
  replaces one of their bytes.
- **Not served or published.** The spectator API looks for a set of recordings
  directly under `replays/` or `replays/samples/`, and the static demo reads
  `replays/samples/` alone. A candidate set sits at
  `replays/candidates/<round>/<set>/`, where neither looks, so its presence
  changes nothing a viewer sees.
- **Not adopted by being here.** Adopting a switch is the owner's decision,
  made after the round is assessed. The adopting change either re-records the
  committed sets with the switch on or promotes a candidate, and in both cases it
  lifts the recorder's refusal of a switched-on config aimed at
  `replays/samples/` or `replays/ml_corpus/`. A later round lands in its own
  directory; the change that lands it, or the adopting change, decides whether
  an earlier round is removed.

## Layout

```text
replays/candidates/
  README.md                    this file
  <round>/
    README.md                  the round's declaration and what it assesses
    experiment-config.json     the declared config
    <set>/                     one directory per roster, for example 9p2i
      replay-seed-<n>.jsonl    one recording per declared seed
      MANIFEST.md
      roster.json
      tournament-eval-report.json.gz
```

A round or set name starts with a letter or digit and uses only letters,
digits, `.`, `_` and `-`. Nothing else sits in this directory, in a round, or in
a set.

## The declaration

Each round's `README.md` carries exactly one fenced block whose info string is
`candidate-declaration`. Its first line is what `shasum -a 256
experiment-config.json` prints in the round directory. Each further line names
one set directory and the seeds it holds, as `<set> seeds <first>-<last>`. For
example, written here with the `text` info string so that this file declares
nothing:

```text
<sha256 of experiment-config.json>  experiment-config.json
9p2i seeds 0-49
```

## Recording a round

Record with the sample recorder, the round's config and an explicit set
directory:

```bash
AILIBI_SAMPLE_DIR=replays/candidates/<round>/9p2i \
AILIBI_MANIFEST=replays/candidates/<round>/9p2i/MANIFEST.md \
AILIBI_NUM_PLAYERS=9 AILIBI_NUM_IMPOSTORS=2 AILIBI_TASKS_PER_CREWMATE=2 \
  bash scripts/refresh_samples.sh --seeds 0,1,2 --expect-levers "" \
    --experiment-config replays/candidates/<round>/experiment-config.json
```

The recorder checks the config before anything stages, refuses any
meeting-experiment environment variable, copies the config into its stage once
and records every seed from that copy. It refuses a switched-on config aimed at
the committed sets, at the default target, or anywhere inside `replays/` other
than `replays/candidates/<round>/<set>/`.

**Record in a dedicated worktree, and run no test suite and no `check.sh` in a
checkout while a recording is running there.** The recorder stages each seed
under the round directory, and the recorder's own tests remove any new path they
find under `replays/` when they finish.

Then gate the set against its declaration:

```bash
uv run python scripts/validity_gate.py replays/candidates/<round>/9p2i \
  --expected-experiment-config replays/candidates/<round>/experiment-config.json \
  --expected-seeds 0-49 --require-one-recording-sha
```

## What checks a round

- `bash scripts/verify_samples.sh`, with no argument, re-simulates every
  candidate set beside the sample sets and fails if any recording no longer
  reproduces.
- `tests/scripts/test_candidate_sets.py` checks every round: the config parses,
  turns a switch on and matches the declared sha256; the declared sets are the
  set directories and each holds exactly its declared seeds; each `MANIFEST.md`
  names one recording sha; every game recorded the declared config; every
  recording reproduces; and each report equals a rebuild from the set's
  recordings.
- `scripts/verify_ml_evidence.py` holds the file count this family's row in
  `docs/artifacts.md` states.
