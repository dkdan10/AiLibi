# Recorder, validity gate and candidate landing for experiment-config records

**Status:** active

## Outcome

No committed tool can record, gate or keep a recording whose experimental switches are ON. The
sample recorder hands `scripts/run_tournament.py` seven flags per seed and none of them sets a
`RecordedExperimentConfig` field. A stray meeting-experiment export changes what is recorded while
the recorder's preflight still reports a clean slate. The validity gate and the kill-gift walk
refuse any experiment-stamped set. And there is no in-tree home where an assessment recording is
verified in CI without becoming a canonical sample set.

After this card:
- `scripts/run_tournament.py --experiment-config FILE` records exactly the declared config: the
  file is validated, then threaded to the game, the agent factory, a meeting runner built from the
  config and the resume fingerprint.
- `scripts/refresh_samples.sh --experiment-config FILE` passes the file through and echoes the
  parsed config in `--dry-run`. It refuses every ambient meeting-experiment export, and it refuses
  a non-default config aimed at `replays/samples/` or `replays/ml_corpus/`.
- `scripts/validity_gate.py` reads experiment-stamped sets and checks them against a declaration:
  the expected config on every game, exactly the expected seeds, one recording sha.
- `replays/candidates/` exists as a registered family that is verified like a sample set and is
  neither served nor published.

This card records nothing and moves no committed replay byte. The ladder tip stays at baseline 9.
It is card 5 of the Stage-B set (decision memo section 3.1), and it runs in wave 2.

## Evidence

Sources, all dated 2026-09-24 and held in the orchestrator's `stage-b-2026-09-24/` directory
(not in the tree): the decision memo, sections 1 ("The recorder needs", "The candidate keeps
verifying"), 2.1, 3.2, 3.3 and card 5 of 3.4; and the investigation memo `partial_record.md`,
sections 2, 3, 4, 6 and 7. Every `path:line` below is at `e886b663` and must be re-anchored by its
named symbol at dispatch. Every count was measured at `e886b663` and must be re-measured at
dispatch.

**The owner's rulings of 2026-09-24, verbatim.**
- "We should implement stage B"
- "Let's not re-record all 300 seeds each time. When it's time to record, record the smaller group
  of 50 seeds, assess if the implementations have been effective and resulted in desired results.
  Also it is understood that updating the vent and body reset logic will probably have a
  substantial effect on previous limits and statistics around the baseline voting results, that
  is okay."
- "Hold off on ML as D suggests until gameplay is finished."
- "Tour fix can be deferred to after gameplay is finished"

**The orchestrator's rulings, under the owner's delegation of 2026-09-24** (decision memo 0.3):
- Item 1, landing: "The 50 seeds go to `replays/candidates/stage-b-r1/9p2i/`: in-tree, class (a)
  plus (b), under one `replays/candidates/` family row. Not `replays/samples/9p2i`, and not an
  orphan evidence commit." The owner may overrule this (memo section 5, item 2).
- Item 5, config-only switches: "The recorder refuses every ambient `EXPERIMENT_ENV_NAMES` export
  (`meetings/evidence_profile.py:25-32`), including the existing `AILIBI_BOUNDED_REBUTTAL`, and
  serves the config instead."
- Item 9: the spine refuses each wave ON value while it sits in `WAVE_ARMS_PENDING`.
- Section 2.1 rejects a MANIFEST experiment-config column: "The declared config file carries a
  sha256 in the candidate README, and the validity gate checks every tick row against it."

**The recorder cannot set an arm.** Each seed runs `scripts/run_tournament.py` with seven flags,
none of them an experiment flag (`scripts/refresh_samples.sh:879-886`; the dry run prints that
line, `partial_record.md` section 7). `run_tournament.py`'s argparse (`_parse_args`, `:244-462`)
has no experiment flag. `run_tournament_eval` builds the default factory with no config
(`eval/balance_eval.py:367`) and constructs `HeadlessGame` without `experiment_config` (`:386`).
The resume `configuration` dict (`scripts/run_tournament.py:1380-1403`) holds no config. The
fingerprint hashes every `AILIBI_*` value (`scripts/_tournament_progress.py:92-99`), but it
cannot hash a file.

**An ambient export records silently.** `build_default_meeting_runner` reads the meeting profile
from the environment (`orchestrator/game.py:1380`), and `HeadlessGame` merges that profile into
the recorded config (`:2253-2273`). The recorder's positive slate check,
`substrate_slate_mismatches` (`orchestrator/replay.py:1220-1279`), covers only the five substrate
toggles. Probe (`partial_record.md` sections 2 and 7): with `AILIBI_BOUNDED_REBUTTAL=1` and
`--expect-levers ""`, the dry run printed "Substrate slate OK". Re-run the probe at dispatch; it
is the planted case that must turn red.

**The default target is canonical.** `SAMPLE_DIR` defaults to `replays/samples/4p1i`
(`scripts/refresh_samples.sh:35`). The fake provider is already refused under `replays/` through
physical-path resolution (the fake branch around `:626`, with `resolve_physical_path`), which is
the precedent for a target rule that neither a symlink nor a `..` can get around.

**Two refusing readers are this card's.** Eight walk profiles raise on an experiment-stamped
recording (`eval/replay_walk.py:503-515`). The readers card (`tasks/work/stage-b-readers.md`)
widens kill-craft, funnel, solvability, win-condition and evidence honesty. Two are this card's:
validity (`_WALK_CONFIG`, `eval/validity.py:508`) and kill-gift (`_KILL_GIFT_WALK_CONFIG`,
`eval/balance_eval.py:914`). The recorder's own post-step, `build_sample_report.py`
(`scripts/refresh_samples.sh:1037`), walks both kill-gift (through `load_tournament_report`) and
kill-craft (`build_report`, `scripts/build_sample_report.py:208`). So until both profiles read an
arms-ON refresh, it exits non-zero in any directory (`partial_record.md` sections 3 and 7). A third
profile in this card's file, `current-report` (`_CURRENT_REPORT_WALK_CONFIG`,
`eval/balance_eval.py:933`), already supports experiments; the kill-gift report path uses it
(`:715`), and the lab derives its profiles from it (`experiments/tactical_gameplay.py:199`, `:363`).
Under the spine it refuses every new wave field until its `threaded_layers` are declared, and the
spine names this card as the owner of all three profiles.

**What the validity gate checks today.** Ten named checks, with a JSON schema documented as STABLE
(`eval/validity.py:22-75`). Check 9 (`check_cost_and_provenance`, `:929`) pins the model, prompt
versions and cost on request. The gate takes no experiment-config, seed-set or recording-sha
declaration. Within one recording, tick rows and the footer must already agree
(`validate_recorded_experiment_config`, `orchestrator/experiment_config.py:145`). Across games
nothing compares them, so a set with some seeds recorded bare would pass.

**MANIFEST recording shas** (count-only, column `git_sha`): s9, s4 and c4 each name 1 and c9
names 2, from
`awk -F'|' '$2 ~ /^ *[0-9]+ *$/ {gsub(/ /,"",$8); print $8}' <set>/MANIFEST.md | sort -u | wc -l`.
So a one-sha rule cannot apply unconditionally. `tests/api/test_sets.py:372-384` pins it for the
two sample sets only.

**The verify leg counts exactly two sets.** `scripts/verify_samples.sh` with no argument walks
`${AILIBI_SAMPLES_ROOT:-replays/samples}/*/` only (`:38-48`), and
`test_verify_sh_no_arg_walks_every_committed_set` asserts exactly 2 clean sets
(`tests/scripts/test_verify_samples.py:163-191`, the count at `:191`). `check.sh` does not call
`verify_samples.sh`: CI reconstructs the 9p2i committed set in `tests/api/test_replay_loader.py`
(near `:1174`). The report-rebuild pattern is `test_check_reports_consistent_on_committed_sets`
(`tests/scripts/test_build_sample_report.py:101-105`). A test-side `check_report` call on a path
naming `replays/` must go through `tests/_helpers/committed.py`
(`tests/_helpers/test_committed_single_home.py`, `WALKERS`).

**Serving and publication read `replays/samples/` only.** The API resolver tries `replays/` and
then `replays/samples/`, and it takes `replays/` when that directory has a direct set
subdirectory (`api/main.py:44`, `_resolve_replay_dir` at `:121`). A set placed directly under
`replays/` would therefore change what the viewer serves, while one at
`replays/candidates/<round>/<set>/` does not. The demo bundle reads `replays/samples` and the
featured list (`scripts/build_demo_bundle.py:90`).

**Staging and the pytest hazard.** Seeds stage in `dirname(SAMPLE_DIR)`
(`scripts/refresh_samples.sh:736`), and `.gitignore:38` ignores only
`replays/samples/.ailibi-refresh-stage-*/`. `tests/scripts/test_refresh_samples.py:1181-1219`
inventories `replays/` and deletes new paths, so a live leg and a pytest run in one checkout
collide (decision memo 0.4).

**The registry.** Each in-tree row of `docs/artifacts.md` (the replay rows are at `:97-99`) is
probed and inventoried by `scripts/verify_ml_evidence.py` (`_IN_TREE_PROBES` at `:2754`,
`_IN_TREE_INVENTORY` at `:2816`). A row that nothing probes fails "registry coverage", and
`_STATED_FILES` (`:2863`) reads `<n> files` and cannot read a singular count.

**The FROZEN header and the fake provider.** `scripts/refresh_samples.sh:3-5` allows "Bug fixes
and evidence readers only"; task 20.33 (`fc5cf719`, 2026-08-24) added `--expect-levers` to both
recorders under the same header. The fake provider never fires a rebuttal (`partial_record.md`
section 7), so this card's fake runs prove stamping and reading, not the arm's behaviour.

## Acceptance

Each item names its enforcing mechanism and the planted or perturbed case that proves it bites.
The test config uses arms that exist today, because the spine's pending guard refuses the wave's
new values:
`{"format_version": 1, "meeting_reset": "hub_with_grace", "vent_exit_policy": "observed_risk", "bounded_rebuttal_version": 1}`.

- [x] **`run_tournament.py --experiment-config FILE` records exactly the file.**
  - Mechanism: the file is parsed once as a `RecordedExperimentConfig` (`extra="forbid"`) and
    threaded to `run_tournament_eval(experiment_config=...)`, `HeadlessGame(experiment_config=...)`,
    `build_default_agent_factory(experiment_config=...)`, a meeting runner built from the config's
    meeting profile (the spine's constructor), and the resume `configuration` dict as the
    normalized config. With no flag, every call is today's.
  - Refusals: the library refuses a non-default config beside a custom `meeting_runner_factory`.
    While the flag is given, the CLI refuses a non-default `--agent-factory`,
    `--candidate-artifact` or `--crew-artifact`, and any of the four `EXPERIMENT_ENV_NAMES` present
    in the environment, whatever its value.
  - Proof: a fake one-seed run stamps exactly the file's config on every tick row and on the
    footer. An unknown field exits non-zero before any file is written. `--resume` with an edited
    config file is refused by the fingerprint. Each refused combination is refused, parametrized
    over the four names and the three factory flags.
- [x] **`refresh_samples.sh` passes the file through, echoes it, and refuses the unsafe slates.**
  - Mechanism: one plumbing-owned Python helper, which the script calls before any preflight or
    staging, in the dry run and the real run alike. It validates the file, prints its sha256 and
    its non-default fields (or "none: historical defaults"), and refuses any of the four experiment
    exports, whether or not a config is given. It also refuses a non-default config unless
    `AILIBI_SAMPLE_DIR` is set explicitly and both it and `AILIBI_MANIFEST` resolve physically
    outside `replays/samples/` and `replays/ml_corpus/`.
  - Inside `replays/`, a non-default config is accepted only at the depth
    `replays/candidates/<round>/<set>/`: the depth the API resolver ignores and the verify loop
    walks.
  - The file is snapshotted into the stage directory once, and every per-seed call passes that
    snapshot, so an edit mid-run cannot mix configs.
  - Proof:
    - the dry run with the file prints its sha256 and fields, stages nothing and leaves
      `git status --porcelain` at 0 lines;
    - with no flag, the dry run's per-seed line is byte-identical to today's seven-flag line;
    - `AILIBI_BOUNDED_REBUTTAL=1 ... --expect-levers "" --dry-run` exits 1 naming the variable,
      where at `e886b663` it printed "Substrate slate OK", and the same holds for the other three
      names;
    - a non-default config is refused with the default target, `replays/samples/9p2i`,
      `replays/ml_corpus/9p2i`, a `..` alias into samples, a symlink into samples, a scratch
      sample directory whose manifest points at a committed `MANIFEST.md`, `replays/<name>/` and
      a one-level `replays/candidates/<round>`. Each case stages nothing and leaves the committed
      tree unchanged, which the existing `_replays_tree_restored` helper guarantees;
    - a config holding only historical defaults is accepted anywhere and records no
      `experiment_config` key.
- [ ] **A fake arms-ON seed recorded through the recorder is read end to end in a bare shell.**
  - Mechanism: this card widens the validity and kill-gift walk profiles to
    `supports_experiments=True`, after the check-by-check review recorded in Results. The readers
    card widens kill-craft and threads `meeting_reset` there in its own acceptance, so this
    post-step does not wait on the meeting-reset card. `temporal_observations` stays refused by
    both profiles.
  - Proof: a recording with `AILIBI_LLM_PROVIDER=fake` and the test config, into a scratch target
    outside `replays/`, stamps exactly the file's config and loads through `ReplayLoader` with
    `outcome_verified` true. The post-step `build_sample_report.py` completes, and its `--check`
    is consistent.
  - Perturbed proof: the same seed, holding at least one meeting, with `meeting_reset` stripped
    from every row, fails both the kill-gift walk's and the gate's meeting post-hash check. So both
    re-simulate from the recorded config and do not default it.
- [x] **The three walk profiles this card owns declare their layers.** Mechanism: validity,
  kill-gift and `current-report` each set the spine's `threaded_layers` to the layers their
  consumers read, named per profile in Results after the review. Proof, per profile: it reads the
  spine's fake full-config recording (a copy of this card's fake recording on the test config, its
  tick rows and footer rewritten to carry every other wave field at its ON value, with the pending
  set patched empty; `vent_witness_rule` joins once the physical-witness card has merged) with every
  hash verified, and it refuses a planted unknown field (a stand-in added to the config model and
  `FIELD_LAYER` in a layer the profile does not declare) by name before its first advance.
  Perturbed: the same profile with its layer declaration removed refuses the full-config copy.
- [x] **The validity gate checks a declaration, within its ten checks.**
  - Mechanism: check 9 learns three declarations:
    - `--expected-experiment-config FILE`: every game's recorded config equals the file's, read
      through the existing recorded-config resolver, not re-parsed.
    - `--expected-seeds A-B` (or a comma list): the replay files and the MANIFEST rows are exactly
      those seeds.
    - `--require-one-recording-sha`: the MANIFEST names one `git_sha`. It is opt-in, like
      `--require-zero-cost`, because c9 names 2.
  - With no config flag, the expected config is the historical default: every game must carry no
    config. No check is added or renamed, and the report's top-level JSON shape is unchanged.
  - Proof, each on a fake set:
    - a set mixing two configs fails, and so does a set whose seed 1 was recorded without the
      arm;
    - an arms-ON set gated with no declaration fails, naming the recorded config;
    - one MANIFEST row given another sha fails under the sha flag;
    - a seed removed with its MANIFEST row fails under `--expected-seeds` and passes without it,
      which proves that the flag is what catches it;
    - an unknown field in the declared file exits with a usage error.

    With no new flag, every check's verdict on the four committed sets is unchanged.
- [x] **`verify_samples.sh` walks candidates.**
  - Mechanism: the no-argument run also walks `${AILIBI_CANDIDATES_ROOT:-replays/candidates}/*/*/`,
    with a header per candidate set, and folds each status into the aggregate. An empty or absent
    candidates root is not an error. The exit-2 "no sample sets" rule keeps its meaning for the
    samples root. `test_verify_sh_no_arg_walks_every_committed_set` points
    `AILIBI_CANDIDATES_ROOT` at an empty directory and still asserts exactly 2.
  - Proof: a planted candidate root holding one copied seed and its roster adds a third clean
    set. One corrupted candidate hash makes the aggregate exit 1 while both sample sets are clean.
- [x] **Candidate rounds have one declared shape, and CI checks it.**
  - Mechanism, the layout: `replays/candidates/README.md` defines the round layout:
    `<round>/README.md`, `<round>/experiment-config.json`, and `<round>/<set>/` holding the
    replays, `MANIFEST.md`, `roster.json` and `tournament-eval-report.json.gz`.
  - Mechanism, the declaration: each round README carries exactly one fenced block with the info
    string `candidate-declaration`. Its first line is what `shasum -a 256 experiment-config.json`
    prints in the round directory. Then comes one line `<set> seeds <first>-<last>` per set
    directory.
  - Mechanism, the test: a new candidate test walks every round through a
    `tests/_helpers/committed.py` enumerator and a cached report check. For each round it asserts:
    - the config parses and is non-default, and the declared sha256 equals the file's;
    - the declared sets equal the set directories, and each set holds exactly its declared seeds;
    - its MANIFEST names one sha;
    - every game carries the declared config, through the gate's library check (no second
      implementation);
    - `_verify_samples.verify_samples(set) == []`, and the report gz equals a rebuild from the
      set's bytes.

    At this card's merge the tree holds no round. So the committed leg walks zero rounds and
    asserts that `replays/candidates/` holds only `README.md` and round directories.
  - Proof: a planted fake round in `tmp_path` passes. Each of these perturbations fails it: one
    byte of the config, a missing or doubled block, an undeclared set directory, a missing seed, a
    foreign sha, a mixed config, one edited report cell, a stray file in the family root.
- [x] **The family is registered.**
  - Mechanism: `docs/artifacts.md` gains the `replays/candidates/` row: class (a) plus (b), in
    git, with its file count. `scripts/verify_ml_evidence.py` gains its `_IN_TREE_PROBES` entry,
    anchored on `replays/candidates/README.md`, and its `_IN_TREE_INVENTORY` entry. If a singular
    count must be read, `_STATED_FILES` is widened to read `1 file`, with a planted singular case.
    The offline `uv run python scripts/verify_ml_evidence.py` reads the row IN-TREE and OK.
  - Proof: a planted registry without the row fails "registry coverage", and a planted tree
    without the README fails the probe (`tests/scripts/test_verify_ml_evidence.py`).
- [x] **Serving and publication do not change with a candidate present.**
  - Mechanism: the resolver and the bundle read `replays/samples/` only, and the depth rule keeps a
    round below them.
  - Proof:
    - in a hermetic tree, `_resolve_replay_dir(anchor=...)` with a planted
      `replays/candidates/r/9p2i/replay-seed-0.jsonl` still returns `replays/samples/` and the
      same set list;
    - the perturbed placement `replays/9p2i/` makes it return `replays/`, which proves that the
      test sees a change;
    - the demo bundle's `data/` tree, built at the base with no round and at the head with a
      planted round (untracked, then deleted), is byte-identical (`diff -r`);
    - `git diff --stat <base>..HEAD -- api frontend replays/samples` is empty.
- [x] **The copy this card adds is plain.**
  - Mechanism: a test scans the family README and every new refusal and echo message for task or
    audit identifiers (`Task \d`, `audit-`) and bare threshold arithmetic. The README defines
    "candidate round" and "experimental switch" in its own words and adds no glossary entry.
  - Proof: a planted message containing "Task 20.33" fails the scan.
- [x] **Everything committed keeps verifying byte-identically, and the full gate is green.**
  - Mechanism: the gates in Validation, run in a clean worktree and in a bare shell.
  - Proof: `git diff --stat <base>..HEAD -- replays/samples replays/ml_corpus tests/fixtures` is
    empty, and the prompt-byte golden passes on s9 and s4 unedited. `bash scripts/check.sh` and
    `uv run pytest -m campaign` both exit 0, each with its real exit code quoted.

## Constraints

**The partial-record principle binds this card.**
- Only `replays/samples/9p2i`'s seeds 0-49 are ever re-recorded, and only into a candidate
  directory. The record card (`tasks/work/stage-b-record-r1.md`) does that, not this card; this
  card builds the refusal that keeps a non-default config out of the canonical trees.
- Every switch is a `RecordedExperimentConfig` field, default-OFF and omitted at its default. This
  card adds none and adds no env lever. `AILIBI_CANDIDATES_ROOT` is a path override like
  `AILIBI_SAMPLES_ROOT`, not a switch.
- Every committed recording, derived view, fixture, gate and doc fact keeps verifying
  byte-identically. There is no registry prompt bump: this card touches no template and no stamp.
- Role-correctness is reported and never gated; the gate gains no role check.
- Nothing pushes an agent toward the correct answer, because this card changes no agent input.
- The meeting layer labels and never rewrites, and this card does not touch it.
- There is no MANIFEST column. All four sets' MANIFEST format and the `fsm-default` policy column
  are unchanged (memo 2.1).

**Wave, order and ownership.**
- Wave 2. This card starts after the spine (`tasks/work/stage-b-arm-spine.md`) has merged, and it
  runs in parallel with the readers card and B0 (`tasks/work/vent-witness-physical.md`).
- It merges after the readers card, whose kill-craft widening the post-step needs, and after the
  census card (`tasks/work/gameplay-census.md`), which edits the registry pair first. It merges
  before the record card.
- It relies on these spine symbols: the constructor for a runner built from a config;
  `profile_from_config`; the engine-arguments helper and its thread-or-refuse walk
  classification; `WAVE_ARMS_PENDING`. Their names are as the spine lands them; re-anchor them at
  dispatch.
- The dated 2026-09-24 addendum to `tasks/direction-2026-09-19-process-over-outcome.md` (memo
  section 6) lands as a `docs:` commit before wave 1. The PR cites it.

Shared files, one writer at a time, per memo 3.2:
- `scripts/verify_samples.sh` and `tests/scripts/test_verify_samples.py` are this card's alone.
- `docs/artifacts.md` is written in merge order by the census card, the readers card, this card,
  look-and-wait, the meeting reset and the record card, each writing only its own row (memo 3.2, as
  amended for this card set). `scripts/verify_ml_evidence.py` and
  `tests/scripts/test_verify_ml_evidence.py` pass from the census card to this card; the record
  card edits neither. This card's region is the `replays/candidates/` row, its probe and inventory
  entries, and `_STATED_FILES`, edited only after the census and readers cards have merged.
- `tests/_helpers/committed.py` passes, serially, from A3 to the census card to the readers card
  to this card, and then to the reset card (memo 3.2, as amended to add this card, which brief 3.4
  requires because the candidate walk goes through this file). This card appends one region (the
  candidates root, the round enumerator and the cached report check) after the readers card has
  merged. The reset card starts its edit of this file only after this card merges.
- 3.2 names no other writer for `scripts/run_tournament.py`, `scripts/refresh_samples.sh`,
  `eval/balance_eval.py`, `eval/validity.py`, `scripts/validity_gate.py` or `.gitignore`. Confirm
  at dispatch.

**What stays out.**
- No live call, no `.env`, no held-out band, no printed prompt. Fake provider only, into scratch
  targets outside `replays/`.
- No ML training, refit or corpus change (ruling 12). No tour, featured or public-results change
  (ruling 11). No scorecard cell (R13).
- No edit to `api/`, `frontend/`, `docs/architecture.md`, `docs/glossary.md`, `.env.example` or
  the experiment registry.
- No change to `scripts/record_ml_corpus.sh`: the corpus recorder gets no config flag.
- No round directory, `experiment-config.json` or round README: those are the record card's. The
  FROZEN header of `refresh_samples.sh` is not edited; the departure is declared under Record
  impact.

**Operating rule**, for this card's own fake runs and for the record card: record in a dedicated
worktree, and run no pytest or `check.sh` in a checkout while a leg is live there. The family
README states this rule. This card also adds `replays/candidates/*/.ailibi-refresh-stage-*/` to
`.gitignore`, beside the samples pattern.

**Delivery.**
- Branch `work/stage-b-record-plumbing`, one pull request into `main`, merged or fast-forwarded,
  never squashed. Never amend a pushed commit; bring `main` in by merging it, never by rebasing.
- Each commit body carries `Card: tasks/work/stage-b-record-plumbing.md`, immediately followed by
  the exact line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` (the house trailer, verbatim, whichever model the worker session runs).
- The PR body fills Summary, Definition of done (this Acceptance list, ticked), Decisions and
  Questions, and ends with the Claude Code attribution line. Agents post no PR comments. Every
  merge is the owner's. `tasks/README.md` and this card's Status line are the orchestrator's; the
  worker fills Results and leaves Status alone.

**Stop and ask** if a committed byte or derived view moves or the golden needs an edit; if the
spine's constructor cannot carry the config's meeting profile; if the review cannot justify a
validity check for experiment-stamped sets; or if the owner overrules the landing (memo 5, item 2).

## Expected scope

- **Recorder:** `scripts/run_tournament.py` (the flag, the refusals, the fingerprint);
  `eval/balance_eval.py` (`run_tournament_eval(experiment_config=...)`, the kill-gift profile and
  the layers of the `current-report` profile);
  `scripts/refresh_samples.sh` (the flag, the snapshot, the helper call, the dry-run and real-run
  echoes); and a new plumbing-owned helper module (for example `scripts/_declared_experiment.py`),
  which holds the validation, the ambient refusal and the target rule, and which both recorders
  call.
- **Gate:** `eval/validity.py` (the profile, the check-9 declarations) and
  `scripts/validity_gate.py` (the three flags, the usage text).
- **Candidates:** `scripts/verify_samples.sh`; a new `replays/candidates/README.md`; one
  `.gitignore` line; `docs/artifacts.md` (the row, and one sentence in the class rules);
  `scripts/verify_ml_evidence.py`; and one region of `tests/_helpers/committed.py`.
- **Tests:** `tests/scripts/test_run_tournament.py`, `tests/scripts/test_refresh_samples.py`,
  `tests/eval/test_validity.py`, `tests/scripts/test_verify_samples.py`,
  `tests/scripts/test_verify_ml_evidence.py`, and a new candidate test (for example
  `tests/scripts/test_candidate_sets.py`) that also holds the resolver and copy-scan cases.
- **Permitted follow-through:** direct call-site, test and docstring updates for the new keyword
  arguments, within these files.
- **Not in scope:** the engine, `agents/`, `meetings/`, `observation/` and `orchestrator/` beyond
  calling the spine's symbols; the prompt set, `api/`, `frontend/`, `replays/samples/`,
  `replays/ml_corpus/`, `tests/fixtures/`; and the readers card's instruments (kill-craft, funnel,
  solvability, win-condition, evidence honesty, the golden, `walk_chain`, scorecard `--set-dir`).

## Record impact

**Nothing moves.**
- No committed replay, MANIFEST, report, fixture or doc fact changes. The new tracked bytes are the
  family README, the registry row and its probe, one `.gitignore` line, and tests.
- With no flag, the recorders behave as today; a test pins the dry-run line byte for byte.
- The one intended default-path change: `refresh_samples.sh` now refuses an ambient
  meeting-experiment export that it used to record silently. No committed set was recorded with
  one: `grep -l '"experiment_config"'` over the 300 committed replay files finds 0.
- The ladder tip stays at baseline 9. `_LADDER_TIP_AUDIT` and `check_vote_correctness_provenance`
  are untouched, and the candidate sits outside `_RECORDED_SETS`.

**Declared FROZEN departure.** `scripts/refresh_samples.sh:3-5` limits the script to bug fixes
and evidence readers. This card adds recording capability to it: a declared config, two refusals
and an echo. The owner's record ruling (quoted under Evidence) and the orchestrator's landing
ruling authorize the departure. Precedent: task 20.33 (`fc5cf719`) added `--expect-levers` under
the same header. The PR states the departure under Decisions.

**Publication.** None. `pages.yml` builds from `replays/samples/` and the featured list, and this
card touches neither `api/` nor `frontend/`. Acceptance proves, with a planted round present, that
the bundle's `data/` tree is byte-identical and the served set list is unchanged.

**Evaluation.** The validity gate reads experiment-stamped sets only against a declaration. With
no flag it keeps demanding the historical default, so a stray experiment in a canonical set fails
a named check instead of being unreadable. Adoption stays the owner's decision per arm, after the
assessment. The adopting card lifts this card's refusal, for a promotion or an in-place record
(memo section 1, adoption item 5).

## Validation

Every gate runs in a bare shell, with no `AILIBI_*` export except the ones a planted case sets on
purpose. Quote each exit code as it came back.

```
bash scripts/check.sh                               # clean worktree, whole
uv run pytest -m campaign                           # the c9 refit pins' campaign half
uv run pytest tests/scripts/test_run_tournament.py tests/scripts/test_refresh_samples.py \
  tests/eval/test_validity.py tests/scripts/test_verify_samples.py \
  tests/scripts/test_verify_ml_evidence.py tests/scripts/test_candidate_sets.py \
  tests/meetings/test_prompt_byte_golden.py tests/_helpers/test_committed_single_home.py
bash scripts/verify_samples.sh                      # both sample sets plus candidates (none yet)
for d in replays/samples/9p2i replays/samples/4p1i replays/ml_corpus/9p2i replays/ml_corpus/4p1i; do
  bash scripts/verify_samples.sh "$d"               # once per set directory
  uv run python scripts/build_sample_report.py --sample-dir "$d" --check; done
uv run python scripts/publish_process_scorecard.py --check
uv run python scripts/publish_gameplay_census.py --check
uv run python scripts/check_doc_facts.py
uv run python scripts/validate_task_docs.py
uv run python scripts/verify_ml_evidence.py         # offline; never --complete
uv run python scripts/validity_gate.py replays/samples/9p2i --json   # verdicts as at the base
```

Also run these fake-provider rehearsals, into scratch directories outside `replays/`:
- the dry run with the test config;
- a `--seeds 0,1` recording with the test config;
- `validity_gate.py <scratch> --expected-experiment-config <file> --expected-seeds 0-1
  --require-one-recording-sha`;
- the bundle `diff -r` from Acceptance.

`npm --prefix frontend test` and the e2e are not required, because this card touches neither
`api/` nor `frontend/`; `check.sh` still runs the frontend unit tests.

## Results

Implemented on `work/stage-b-record-plumbing` from base `bdfa5b19` in nine commits: `bfd7ceb8` (the harness,
the three walk profiles and the gate's declarations), `86274c1b` (both recorders), `d2dbc4c0` (the candidate
family), `5d1ff825` (two refresh lines removed), and `e817b3ca`, `f8bf9e3d`, `1f98d945`, `fc4c384b`, `17cd2e65`
(tests).
Every number below was measured at `17cd2e65` unless a row names another commit. The commit that carries this
section changes only this card and `tasks/README.md`.

**Status: active, one box open.** Every acceptance item but the third is met at `17cd2e65`. The third's
post-step, `build_sample_report.py` over the arms-ON recording, walks kill-craft, which refuses every experiment
recording until the readers card (`tasks/work/stage-b-readers.md`) widens it. That card has not merged into
`main`, so at this head the fake recording stamps exactly the file and loads verified, the perturbed reset
fails every walk, and the post-step still exits 1 on kill-craft's refusal. The test that proves the box,
`test_the_post_step_builds_and_checks_the_report_of_an_arms_on_set`, is a strict xfail keyed on kill-craft's own
profile: it runs for real, and must pass, once `main` carries the readers card and is merged here. At a trial
merge of `fc4c384b` (one test line short of `17cd2e65`'s typing fix) with `origin/work/stage-b-readers` at
`9bab8d16` (a throwaway local branch, deleted, never pushed), it ran and PASSED, and the card's eight test files passed whole (485 passed); the box is ticked when
that merge is this branch's.

**What it implements.** Decision memo (`tasks/decision-2026-09-24-stage-b-wave.md`) section 0.3 items 1, 5, 9
and 10; section 1, "The recorder needs" and "The candidate keeps verifying"; 2.1 (no MANIFEST column; the
config's sha256 in the round README; the gate checks every row); 3.2 (the writer map) and the card-5 brief in
3.4. The spine's arm page, [`docs/experiment-arms.md`](../../docs/experiment-arms.md), linked from
`docs/architecture.md` ("Determinism and the substrate ladder"), for `FIELD_LAYER`, `threaded_layers`,
`engine_arguments`, `profile_from_config` and the pending guard. The owner's rulings of 2026-09-24 ("We should
implement stage B"; the 50-seed record paragraph) and the dated 2026-09-24 addendum to
`tasks/direction-2026-09-19-process-over-outcome.md` section 12.

### The check-by-check review behind the three profiles

Each profile now sets `supports_experiments=True` and declares `threaded_layers = {orchestrator, tactical,
meeting}`, every layer a profile can declare; engine fields reach all three through the spine's
`engine_arguments`, which refuses one it does not thread (`vent_witness_rule` until B0 threads it). What each
consumer reads from an experiment-stamped recording, and why that reading is correct:

| Consumer | What it reads | Why the reading holds under the wave's settings |
| --- | --- | --- |
| 1 `all_games_reach_game_over` | the walk's `GameOverEvent` and the recorded `game_over` row | the walk applies the recorded actions (whatever tactical policy chose them) and the recorded meeting outcomes, with the recorded `meeting_reset` threaded into `apply_meeting_result`; a stripped reset fails the meeting post-hash (planted below) |
| 2 `meeting_rate_and_resolution` | meeting rows per game, and whether each resolved | counts rows; no setting changes what a row is. The 0.60 floor is the Stage-A enablement floor, unchanged |
| 3 `no_duplicate_meeting_rows` | meeting ids and ticks | structural |
| 4 `no_tick_1_kills` | `KilledEvent` ticks from the walk | the spawn cooldown is seeded before any setting acts; the reset sets cooldowns after a meeting, never at spawn |
| 5 `no_friendly_fire_kills` | `KilledEvent` victims against seeded roles | engine truth |
| 6 `no_betrayal_ballots_or_accusations` | recorded impostor ballots and accusations naming a fellow impostor | the strategic impostor ballot keeps the teammate firewall (memo 2.5, direction addendum), so a teammate target stays the regression this row reports |
| 7 `no_railroaded_crew_ejections` | the suspicion block of each recorded vote prompt, bounded by the next `## ` header | the ballot arms add their own guarded blocks to `vote_ballot.j2`; a block outside the suspicion block is not read (a limitation: the ballot card must keep its rows outside it) |
| 8 `no_dangling_primary_reason_id` | ballot `primary_reason_id` against the meeting's turn ids | a rebuttal reply is a transcript turn with its own id; an own-evidence citation travels in `primary_reason_observation_id`, which this row does not read |
| 9 `cost_and_provenance_exact` | substrate stamp, model and prompt-version sets, cost rows, and now the recorded config | the wave adds no lever, so the bare-shell stamp comparison is unchanged; a ballot arm stamps its composite versions on every meeting of the set, which stays one coherent set; the recorded config is checked against the declaration |
| 10 `byte_identical_reconstruction` | `ReplayLoader` re-simulation | the loader re-simulates from the recorded config (engine arguments and `meeting_reset`, from the spine) |
| kill-gift (`_kill_gift_accounting`) | task instances and the final tick's kill, from the walk | engine truth over recorded actions and outcomes |
| current-report (`_current_replay_facts`, the lab's two derived profiles) | the same kill-gift facts; the lab's action and event counts (`measure_identity_effects` refuses every experiment recording first) | action-level folds; its format-3 policy reconstruction builds agents from the recorded config (`build_default_agent_factory(experiment_config=...)`), so a recorded tactical setting is decided as recorded. The census derives its own profile and declares its own layers |

Temporal observations stay refused by validity and kill-gift (planted: the recorded version patched to 2 is
refused by both and read by current-report).

### Verification at `17cd2e65`

Each command ran in a bare shell (`env -i HOME PATH`), with its exit code captured directly, never through a
pipe.

| Command | Result |
| --- | --- |
| `bash scripts/check.sh` | exit 0: ruff, format (532 files), import contracts 4 kept, task docs, prompts, mypy (503 source files), 9,004 passed, 20 skipped, 4 xfailed (the new strict xfail is the fourth); frontend lint, `tsc:check`, 559 vitest tests and the build. The same run at `fc4c384b` exited 1 on strict mypy (a set minus an optional set in the new ordering canary), fixed in `17cd2e65` |
| `uv run pytest -m campaign -n auto --dist loadfile -q` | exit 0: 336 passed |
| the card's eight test files (`uv run pytest <the eight files> -q -n 6 --dist loadfile`) | exit 0: 474 passed, 1 xfailed |
| `bash scripts/verify_samples.sh` (no argument) | exit 0: 2 sets verified clean, 0 candidate sets |
| `bash scripts/verify_samples.sh <set>`, once per set | exit 0 each: s9 50, s4 50, c9 150, c4 50 verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check`, the four sets | exit 0 each, consistent |
| `uv run python scripts/publish_process_scorecard.py --check` | exit 0, consistent |
| `uv run python scripts/publish_gameplay_census.py --check` | exit 0, consistent |
| `uv run python scripts/check_doc_facts.py` | exit 0 |
| `uv run python scripts/validate_task_docs.py` | exit 0, 88 work cards |
| `uv run python scripts/verify_ml_evidence.py` (offline) | exit 0: 63 checks, 51 OK, 0 FAIL, 7 ABSENT, 5 INFO; `replays/candidates/ [(a) + (b)]` OK |
| `uv run python scripts/validity_gate.py <set> --json`, the four sets | exit 0 each; each JSON byte-identical (`cmp`) to the same command at `bdfa5b19` |
| `git diff --stat bdfa5b19..17cd2e65 -- api frontend replays/samples replays/ml_corpus tests/fixtures` | empty |
| `tests/meetings/test_prompt_byte_golden.py` on s9 and s4, unedited | passes (inside the targeted run and `check.sh`) |
| `grep -l '"experiment_config"'` over the 300 committed replay files | 0 |

**The fake-provider rehearsals** (at `1f98d945`, whose production files equal `17cd2e65`'s; a scratch directory
outside `replays/`, the 9p2i roster, the test config):

| Rehearsal | Result |
| --- | --- |
| the dry run with the file | exit 0; prints the file's sha256 (`8984cfef…`), its three settings, the per-seed line ending `--experiment-config <stage-dir>/experiment-config.json`, and "Substrate slate OK"; `git status --porcelain` 0 lines before and after, the scratch target not created |
| `--seeds 0,1` with the file | both seeds recorded from the stage snapshot, "Refresh complete", 2 of 2 reached a meeting; then exit 1 in the post-step: `replay profile 'kill-craft' does not support experimental recordings` (the open box) |
| `validity_gate.py <scratch> --expected-experiment-config <file> --expected-seeds 0-1 --require-one-recording-sha` | exit 0, all ten checks PASS (5 resolved meetings, 31 ballots) |
| the same set with no declaration | exit 1, `cost_and_provenance_exact` the one failing check |
| `bash scripts/verify_samples.sh <scratch>` | exit 0, 2 verified clean |

**Publication.** `scripts/build_demo_bundle.py` built at `bdfa5b19` with no round, and at `1f98d945` (whose
production files equal `17cd2e65`'s) with an
untracked planted round (`replays/candidates/planted-r1/9p2i/` holding s9 seed 0 and its roster; deleted after
the build, leaving `git status` clean): 156 baked JSON files each, `diff -r` of the two `data/` trees empty (exit
0). This card touches neither `api/` nor `frontend/`.

**The probe the card named.** At `bdfa5b19`, `AILIBI_BOUNDED_REBUTTAL=1 bash scripts/refresh_samples.sh --seeds 0
--expect-levers "" --dry-run` in a bare shell exited 0 and printed "Substrate slate OK". At `17cd2e65` it exits 1:
"Refused: the environment exports AILIBI_BOUNDED_REBUTTAL. … Nothing was staged.", and the same holds for the
other three names, at value `1` and at value `0`.

### Planted and perturbed failures

Each is a committed test; each was seen red with its defect and green without it.

| Claim | Planted or perturbed case | Red |
| --- | --- | --- |
| the flag records exactly the file | one fake 4p1i seed on the test config | every tick row and the footer parse equal to the file's config; loads with `outcome_verified` |
| an unknown field stops before any write | `{"hidden_travel": "on"}`; a repeated key | `SystemExit` naming the field or the key; the output directory never created |
| resume binds the config | the file edited between a run and `--resume` | "Continuation configuration differs"; unedited, the resume exits 0 |
| refusals beside the flag | each of the four names at `1` and at `0` (and a Hypothesis family of values); `--agent-factory learned-champion`, `learned-crew`, `--candidate-artifact`, `--crew-artifact` | `SystemExit` naming each; `fsm-default` accepted |
| the library runner | a switched-on config beside a custom `meeting_runner_factory`; `AILIBI_BOUNDED_REBUTTAL=1` beside a declared config | `ValueError` each; a config of defaults beside a custom runner accepted |
| the recorder's exports | the four names at `1` and `0`, with no config | exit 1 naming each, before "Substrate slate OK" |
| the target rule | the default target, `samples/9p2i`, `ml_corpus/9p2i`, a `..` alias, a symlink, a scratch directory with a committed manifest, `replays/<name>`, a one-level `candidates/<round>`, a hidden round name | exit 1, each naming its rule and the path as it resolves, nothing staged, no key gate reached; a Hypothesis property over composed paths (links, `..`, names one level off) finds no accepted target inside a canonical tree |
| the snapshot | the file edited after the check; a copy that no longer parses; an unreadable file | refused, naming both sha256 values; nothing written |
| every seed uses the copy | a traced (`bash -x`) fake run | both `run_tournament.py` calls end `--experiment-config <stage>/experiment-config.json`, never the source path |
| the gate's default | the arms-ON set with no declaration | check 9 names each game's recorded settings against "none: historical defaults" |
| mixed configs | seed 2's rows without the rebuttal field | check 9 names `headless-seed-2` alone |
| a seed recorded without the arm | seed 1 recorded bare | check 9 names `headless-seed-1` |
| one sha | one MANIFEST row given `def5678` | fails under `--require-one-recording-sha` only |
| exact seeds | seed 2 removed with its MANIFEST row | fails under `--expected-seeds` only |
| a usage error | `--expected-experiment-config` with `hidden_travel` | exit 2 naming the field |
| profiles re-simulate the reset | `meeting_reset` stripped from every row of a game with a meeting | `meeting_post_hash_mismatch` at the meeting tick, for validity, kill-gift and current-report |
| profiles read the full config | the fake game's rows rewritten to carry every other wave setting at its ON value (pending set patched empty) | each profile's result equals the unedited game's, every hash verified |
| declarations bite | each profile with its layers removed; a stand-in field added to the config model and `FIELD_LAYER` in each layer | refused by name before the first advance (the advance counter reads 0); a declared layer's stand-in is read |
| temporal stays refused | the recorded version patched to 2 | validity and kill-gift refuse; current-report reads |
| the candidates loop | a planted round with one copied seed; one corrupted candidate hash; a set holding no replay; an absent root; no sample set | 3 clean; exit 1 with both sample sets clean; exit 1; exit 0; exit 2 |
| the candidate shape | a planted fake round, then one byte of the config, a missing and a doubled block, an undeclared set, a missing seed, a foreign sha, a mixed config, one edited report cell, a stray file in the family root, a config of defaults | the planted round passes; each perturbation fails with its own line |
| registration | the registry without the row; the tree without the README; a two-file row restated as `1 file` | "registry coverage" FAIL; the row MISSING; the inventory FAIL |
| serving | a planted round, then the same set moved to `replays/9p2i/` | the resolver keeps `replays/samples/` and its set list; the moved set makes it return `replays/` |
| plain copy | "Task 20.33", an audit filename, "`>= 0.6`", "6/7" | the scan flags each; every template, help text, echo and the README pass |

### The neutering pass

Every production line or row this card added or changed was neutered in place, the named test files run
(`pytest -x -n 6 --dist loadfile`), and the file restored from a byte copy (sha256 compared, never `git
checkout`). The pass ran at `e817b3ca`; 155 probes, 155 restored.

| File | Probes | Red |
| --- | --- | --- |
| `scripts/_declared_experiment.py` (constants, the 15 message templates and their tuple, parsing, sha, the environment, the target rule, the snapshot, the command line) | 58 | 58 |
| `scripts/run_tournament.py` (the flag, the resolver's rows and calls, the placement, the resume key, the harness option) | 15 | 15 |
| `eval/balance_eval.py` (the refusal, the profile, the factory, runner and game calls and their absent-config branches, each layer of both profiles) | 18 | 18 |
| `eval/validity.py` (each layer, the inventory, each violation function's filters and messages, check 9's branches, the gate's reads and pass-throughs) | 29 | 29 |
| `scripts/validity_gate.py` | 9 | 9 |
| `scripts/refresh_samples.sh` | 14 | 14 |
| `scripts/verify_samples.sh` | 4 | 4 |
| `scripts/verify_ml_evidence.py` (probe, inventory, `_STATED_FILES`) | 3 | 3 |
| `tests/_helpers/committed.py` region | 4 | 4 |
| `.gitignore` | 1 | 1 |

No probe came back green in the pass. Before it, a line-by-line review found two refresh lines no test could
reach (a relative config path made absolute, and a refusal of an empty checked sha), removed in `5d1ff825`, and
the probes it predicted would survive were closed in `e817b3ca` before the pass ran: the repository reached
through a link, the `records/` family at the candidate depth, an unreadable file, the run deadline beside a
config, a default config object against none, a MANIFEST naming no sha, an unreadable MANIFEST, the gate's sha
flag, the default candidates root, and the template tuple's completeness.

### The mutation pass

One bounded pass over the production modules this card touched, with the eight operator classes and no others,
each mutant run against its targeted test files only. It ran at `f8bf9e3d`; 56 mutants, 56 restored.

| Operator class | Mutants | Killed | Survivors |
| --- | --- | --- | --- |
| drop a filter or wrapper on a collection | 8 | 8 | none after `fc4c384b` (below) |
| swap one collection for a related one | 4 | 4 | |
| replace a comparison with a None test or its inverse | 18 | 18 | |
| replace a role, kind, room or tick read with a constant | 3 | 3 | |
| replace a message argument with a constant | 15 | 15 | |
| drop one member of a tuple of kinds or types | 2 | 2 | |
| swap adjacent branches | 3 | 3 | |
| replace a read of a loaded source with the canonical literal | 3 | 1 | 2 equivalent |

- **Killed after the first run.** `sorted(expected_seeds - seeds)` replaced by `list(...)` survived: every planted
  difference held one seed. `1f98d945` planted two missing and two unexpected seeds, but chose unexpected seeds
  that share a slot in a small set's table, so their order depended on how the set was built, and the trial merge
  with the readers branch iterated them sorted. `fc4c384b` uses values in distinct slots, asserts the unsorted
  order the set gives, and both mutants (this one and its twin on the unexpected seeds, 56 mutants in all) are
  killed at `fc4c384b`.
- **Equivalent, named.** The kill-gift profile's and the validity profile's `threaded_layers=<constant>` replaced
  by the literal `frozenset({"orchestrator", "tactical", "meeting"})`: the constant is that literal, defined in the
  same module and read from no other source; the tests hold the profile, the constant and the literal equal.

### Decisions

- **The helper module.** `scripts/_declared_experiment.py` holds the three rules and the copy: the file (one
  JSON object, no repeated key, `RecordedExperimentConfig` with `extra="forbid"`, sha256 over the bytes read),
  the environment (the four `EXPERIMENT_ENV_NAMES`, refused when present at any value) and the target. Its
  command line has `check` (run by `refresh_samples.sh` before any preflight, dry run and real run alike) and
  `snapshot` (run once the stage exists). `run_tournament.py` imports it; `eval/validity.py` reads its
  `describe_settings` through the existing `scripts/` edge; `scripts/validity_gate.py` reads a declared file
  through it.
- **The depth rule.** A switched-on config needs an explicit `AILIBI_SAMPLE_DIR`. Its sample directory and its
  manifest are resolved physically (`os.path.realpath`, the repository's own `replays/` resolved the same
  way). Inside `replays/samples/` or `replays/ml_corpus/` they are refused; elsewhere inside `replays/` the
  sample directory must be exactly `replays/candidates/<round>/<set>/` and the manifest must sit directly in
  such a directory; a round or set name starts with a letter or digit (`[A-Za-z0-9][A-Za-z0-9._-]*`), so the
  verifier's `*/*/` glob sees every set. Outside `replays/` anything goes. A config of historical defaults
  records nothing new and goes anywhere.
- **The environment refusal is presence-based and unconditional in the sample recorder.** Any of the four
  names present, at any value, is refused by `refresh_samples.sh` with or without a config (the intended
  default-path change), and by `run_tournament.py` beside `--experiment-config`. The runner built from a
  config still refuses an ON export on its own (the spine's rule), so the library path is covered too.
- **The snapshot.** The check prints the file's sha256; `snapshot` reads the file once, copies it into the
  stage only if it still has that sha256, validates it again and writes a new file; every per-seed call passes
  that copy. An edit between the check and the copy is refused; an edit after the copy cannot reach a seed.
- **The resume configuration** carries `experiment_config` (the normalized config, or `null` for historical
  defaults) only when the flag is given, so an unflagged run's sidecar keeps its keys; a resume with an edited
  file that records anything different fails the fingerprint.
- **The library's absent-config path is byte-for-byte today's calls.** `run_tournament_eval` adds a keyword to
  the factory, the runner and the game only when a config is declared; a declared config of defaults still
  builds the runner from its (all-none) profile, so an ambient ON export is refused beside it. A switched-on
  config beside a custom `meeting_runner_factory` is refused, as the card states; a config of defaults beside
  one is accepted.
- **The gate's absent-flag default** is the historical defaults: every game must have recorded no config. An
  experiment set gated without a declaration now fails check 9, naming its recorded settings, where it used to
  be unreadable. With no new flag, the gate's JSON on the four committed sets is byte-identical to the base.
- **Two opt-in declarations**, inside check 9: `--expected-seeds` (the replay files and the MANIFEST rows are
  exactly the seeds) and `--require-one-recording-sha` (every MANIFEST row names one sha; opt-in because c9
  names 2). They read the set's MANIFEST through the two readers the tree already has: the verifier's seed list
  (`_verify_samples._manifest_seeds`) and the loader's sha list (`replay_loader._manifest_seed_shas`); a row the
  second cannot read counts as naming no sha, which fails closed.
- **The `committed.py` region** is appended at the end of the file: `CANDIDATES_ROOT`, `candidate_rounds`
  (directories only, an absent root holds none) and the cached `candidate_report_check`.
- **The candidate test builds its planted round with kill-craft reading the test config.** Kill-craft refuses
  every experiment recording until the readers card widens it, and the report build walks it; the test config
  sets only settings that existed before the wave, which `supports_experiments` alone covers, so an autouse
  fixture patches exactly that while kill-craft refuses, and does nothing once it reads them. It should be
  deleted when `main` is merged in after the readers card.
- **The post-step end-to-end test is a conditional strict xfail**, keyed on kill-craft's own profile: it is
  expected to fail while kill-craft refuses experiment recordings and runs for real, and must pass, once the
  readers card lands. A pass before then fails the suite.
- **Two refresh lines removed** in `5d1ff825`: making a relative config path absolute (the check, the snapshot
  and every seed run in one working directory) and refusing an empty checked sha (the snapshot already refuses
  it). The review before the neutering pass found no test could reach either, and neither changed what the
  recorder does.
- **Status and the index.** The card reserves its Status line and the index sentence for the orchestrator; the
  dispatch delegated both, and asked for `done` only if every box is truly met. The third box is not met at this
  head, so the Status is `active` and the index sentence is re-derived to "88 cards: 8 ready, 1 active, 79 done".
- **Declared FROZEN departure.** `refresh_samples.sh`'s header allows bug fixes and evidence readers; this card
  adds a declared config, two refusals and an echo, under the owner's record ruling of 2026-09-24 and the
  orchestrator's landing ruling, with the `--expect-levers` flag as precedent. The header is not edited.

### Closing greps

- `git grep -niE '(validity|kill.gift|current.report)[^.]{0,80}(refus|reject|cannot read|does not (support|read))[^.]{0,60}experiment' -- ':!tasks' ':!audits' ':!agent_prompts'`:
  none.
- `git grep -niE 'recorder (cannot|can.t) set|refresh_samples[^.]{0,80}(no|without an?) experiment' -- ':!tasks' ':!audits' ':!agent_prompts'`:
  none.
- `git grep -nE 'verify_samples\.sh' -- '*.md' ':!tasks' ':!audits' ':!agent_prompts'`: 16 hits; none says the
  bare run walks only the samples root (`training/README.md` says it walks every `replays/samples/` set, which
  stays true).
- `git grep -niE 'every profile declares no layer'`: `eval/replay_walk.py` (and `docs/experiment-arms.md`, where
  the phrase wraps a line), the spine's rule ("until its owner reviews what its consumer reads"), which these three
  reviews follow; the third hit is this card.
- The decision memo and the Stage-B cards cite the old recorder and verifier at their `e886b663` anchors; they are
  dated records and are not edited.

### Limitations

- The third acceptance box waits on the readers card (above). The candidate test's planted round is built with
  an autouse fixture that lets kill-craft read the test config while kill-craft refuses experiment recordings; it
  does nothing once kill-craft reads them, and should be deleted when `main` is merged in after the readers card.
- The fake provider fires no rebuttal, so these fake runs prove stamping, reading and refusing, not an arm's
  behaviour.
- At merge the candidate leg walks zero rounds; the first round is the record card's.
- `vent_witness_rule` is not in the full-config copy: the engine-arguments helper refuses it until the physical
  witness card threads it.
- A layer declaration covers every later field in that layer, which is the spine's mechanism: a later field's card
  must re-read these three reviews. The railroad check reads the suspicion block up to the next header, so the
  ballot card must keep its rows outside that block.
- The tactical lab's two profiles derive from current-report, so they now read wave settings in the three layers
  (its `measure_identity_effects` still refuses every experiment recording first).
- The MANIFEST is read through two existing readers that differ on a malformed row; a row the sha reader skips
  counts as naming no sha, which fails closed.
- The bundle comparison was built on macOS; CI builds on Linux.
