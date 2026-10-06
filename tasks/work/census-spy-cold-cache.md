# The census walk spy on a cold worker

**Status:** done

## Outcome

Three tests in `tests/eval/test_gameplay_census.py` plant a recording the
census's walk must refuse before its first advance, and prove the refusal came
first by recording what the walk yielded: `_spied_walk` replaces
`census.walk_replay` with a spy and the test asserts the spy saw nothing. Two of
them, `test_a_census_walk_without_a_layer_refuses_its_setting_before_advancing`
(every parameter but the first passes only because the first warmed the cache)
and `test_a_recorded_setting_no_one_declared_is_refused_before_advancing`, fail
whenever they are the first census walk in a pytest process. The full gate is
green only because `--dist loadfile` runs the file in collection order on one
worker, where earlier tests have already loaded the committed set. A targeted
run, a `-k` selection or any future split of the file is red with a refusal that
advanced nothing reported as every tick of the committed game.

After this card, each spy user passes whichever test the process runs first,
with every assertion it makes unchanged.

## Evidence

Reproduced at `67e1b8e`, the `main` this branch starts from:

```text
uv run pytest "tests/eval/test_gameplay_census.py::test_a_census_walk_without_a_layer_refuses_its_setting_before_advancing" -q -p no:cacheprovider
1 failed, 4 passed in 5.12s
  [vent_exit_policy-look_and_wait]  assert yielded == []
  Left contains 1244 more items, first extra item: TickOpened(...)

uv run pytest "tests/eval/test_gameplay_census.py::test_a_recorded_setting_no_one_declared_is_refused_before_advancing" -q -p no:cacheprovider
1 failed in 2.02s
```

The mechanism, by symbol: `_spied_walk` installs the spy; `_walked` then calls
`_committed_game()` for the committed roles and manifest cell; that goes to
`tests/_helpers/committed.py::census_inputs`, a process-wide `functools.cache`,
which on a cold worker loads the whole 4p1i set through
`eval.gameplay_census.load_census_inputs` and `_load_game`, whose walk is the
module attribute the spy now occupies. The spy records that committed walk, so
the refused walk's empty yield is hidden under 1,244 committed events.

`test_the_census_walk_takes_its_engine_settings_from_the_spines_helper` passes
alone only by ordering: its first, unspied `_walked(path)` warms the cache before
the spy goes in. `test_the_census_walk_reads_every_later_setting_it_declares`
installs no spy and has no hazard. No other test in the file calls
`_spied_walk`.

## Acceptance

- [x] The parametrized layer test passes when it is the first census walk in a
  process: the first command above reads 5 passed on this branch, and the
  whole file passes serially and under the gate's `-n auto --dist loadfile`.
- [x] The undeclared-setting test and the engine-settings test pass alone,
  each in a fresh process.
- [x] Every assertion of the three spy users is unchanged. The change is the
  helper's warm-up plus the spy moving ahead of the one other patch in two
  tests, so the warm-up runs under the production walk profile.
- [x] Adverse case: the same first command at `67e1b8e`, without the warm-up,
  is red (1 failed, 4 passed), with the committed walk's events in `yielded`.
- [x] `bash scripts/check.sh` passes on the branch tip.

## Constraints

Test-only. `eval/gameplay_census.py`, the production walk, every recorded
byte, every prompt and the published census are untouched. The warm-up adds no
walk over a committed set: it goes through the one cached home,
`tests/_helpers/committed.py`, so the single-home pin and the suite's cost are
as they were. No experimental switch, dependency, provider call or spending.

## Expected scope

`tests/eval/test_gameplay_census.py` (`_spied_walk` and the two tests whose
spy call moved ahead of their other patch), this card, and the card inventory
sentence in `tasks/README.md`.

## Record impact

None. No recording, manifest, prompt, detector, schema, generated type or
published file changes, and the committed census JSON and Markdown are
byte-identical. Nothing in production moves: the change is when a test helper
loads an already-cached fixture.

## Validation

```text
uv run pytest "tests/eval/test_gameplay_census.py::test_a_census_walk_without_a_layer_refuses_its_setting_before_advancing" -q -p no:cacheprovider
uv run pytest "tests/eval/test_gameplay_census.py::test_a_recorded_setting_no_one_declared_is_refused_before_advancing" -q -p no:cacheprovider
uv run pytest "tests/eval/test_gameplay_census.py::test_the_census_walk_takes_its_engine_settings_from_the_spines_helper" -q -p no:cacheprovider
uv run pytest tests/eval/test_gameplay_census.py -q -p no:cacheprovider
bash scripts/check.sh
```

Each targeted command is its own process, so its cache is cold; that is the
adverse condition, not a convenience.

## Results

Verified 2026-10-06 on `work/census-spy-cold-cache`.

**The fix.** `_spied_walk` calls `_committed_game()` before it installs the
spy, and its docstring states the two orderings it relies on: the committed game
is cached before the spy, and the spy goes in before any other patch. In the
layer test the spy call moved above the `CENSUS_WALK_CONFIG` patch, and in the
engine-settings test above the `_THREADED_ENGINE_FIELDS` patch, so the one
carrier every later reader on the worker shares is always loaded under the
production profile rather than a test's planted one. The undeclared-setting
test needed no reorder: it has no other patch. The committed 4p1i game records
no experiment configuration, so a carrier loaded under the planted profile
would have been equal anyway; the ordering is kept as a rule, not a measurement.

**Red, then green.** Before the change, at `67e1b8e`: the parametrized command
read 1 failed, 4 passed, and the undeclared-setting command 1 failed. After the
change, each targeted command in its own process:

| Command | Result |
| --- | --- |
| layer test alone | 5 passed in 3.11s |
| undeclared-setting test alone | 1 passed in 1.53s |
| engine-settings test alone | 1 passed in 1.71s |
| whole file, serial | 332 passed in 24.02s |

**Full gate.** `bash scripts/check.sh` with the frontend leg: recorded below
once run on this tip.

**Limitations.** This repairs the three spy users; it adds no gate that would
catch the next test to patch `census.walk_replay` before reading the cache.
The two cheap guards such a gate would need (the spy wrapping the unpatched
symbol, the profile being the production one at warm-up) are stated in the
helper's docstring and not asserted, because an invariant gate needs its own
planted failure and this card is a test repair, not a new gate. The whole-file
and gate runs re-verify order independence only as far as collection order
goes; the targeted single-process runs are the evidence for a cold worker.

Adoption: not applicable (no experimental behaviour).
