# Recorder, validity gate and candidate landing for experiment-config records

**Status:** ready

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

- [ ] **`run_tournament.py --experiment-config FILE` records exactly the file.**
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
- [ ] **`refresh_samples.sh` passes the file through, echoes it, and refuses the unsafe slates.**
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
- [ ] **The three walk profiles this card owns declare their layers.** Mechanism: validity,
  kill-gift and `current-report` each set the spine's `threaded_layers` to the layers their
  consumers read, named per profile in Results after the review. Proof, per profile: it reads the
  spine's fake full-config recording (a copy of this card's fake recording on the test config, its
  tick rows and footer rewritten to carry every other wave field at its ON value, with the pending
  set patched empty; `vent_witness_rule` joins once the physical-witness card has merged) with every
  hash verified, and it refuses a planted unknown field (a stand-in added to the config model and
  `FIELD_LAYER` in a layer the profile does not declare) by name before its first advance.
  Perturbed: the same profile with its layer declaration removed refuses the full-config copy.
- [ ] **The validity gate checks a declaration, within its ten checks.**
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
- [ ] **`verify_samples.sh` walks candidates.**
  - Mechanism: the no-argument run also walks `${AILIBI_CANDIDATES_ROOT:-replays/candidates}/*/*/`,
    with a header per candidate set, and folds each status into the aggregate. An empty or absent
    candidates root is not an error. The exit-2 "no sample sets" rule keeps its meaning for the
    samples root. `test_verify_sh_no_arg_walks_every_committed_set` points
    `AILIBI_CANDIDATES_ROOT` at an empty directory and still asserts exactly 2.
  - Proof: a planted candidate root holding one copied seed and its roster adds a third clean
    set. One corrupted candidate hash makes the aggregate exit 1 while both sample sets are clean.
- [ ] **Candidate rounds have one declared shape, and CI checks it.**
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
- [ ] **The family is registered.**
  - Mechanism: `docs/artifacts.md` gains the `replays/candidates/` row: class (a) plus (b), in
    git, with its file count. `scripts/verify_ml_evidence.py` gains its `_IN_TREE_PROBES` entry,
    anchored on `replays/candidates/README.md`, and its `_IN_TREE_INVENTORY` entry. If a singular
    count must be read, `_STATED_FILES` is widened to read `1 file`, with a planted singular case.
    The offline `uv run python scripts/verify_ml_evidence.py` reads the row IN-TREE and OK.
  - Proof: a planted registry without the row fails "registry coverage", and a planted tree
    without the README fails the probe (`tests/scripts/test_verify_ml_evidence.py`).
- [ ] **Serving and publication do not change with a candidate present.**
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
- [ ] **The copy this card adds is plain.**
  - Mechanism: a test scans the family README and every new refusal and echo message for task or
    audit identifiers (`Task \d`, `audit-`) and bare threshold arithmetic. The README defines
    "candidate round" and "experimental switch" in its own words and adds no glossary entry.
  - Proof: a planted message containing "Task 20.33" fails the scan.
- [ ] **Everything committed keeps verifying byte-identically, and the full gate is green.**
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
  the `Co-Authored-By:` attribution line the worker's own session supplies (never a model name copied from this card).
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

Not started. The implementer records here and in the PR:
- the sections relied on (the spine's arm page, `docs/experiment-arms.md`, linked from
  `docs/architecture.md`; memo 1, 2.1, 3.4);
- the check-by-check review behind each profile flip: for each of the ten validity checks and for
  kill-gift, what it reads from an experiment-stamped recording and why that reading is correct,
  and the layers each of the three profiles declares;
- the decisions: the depth rule, the gate's absent-flag default, the two opt-in declarations, the
  helper module's name and the `committed.py` region;
- each planted failure with its red output, every Validation command with its exit code, and the
  bundle diff;
- limitations: the fake provider fires no rebuttal, and at merge the candidate leg walks zero
  rounds.
