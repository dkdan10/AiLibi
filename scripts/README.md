# Scripts

The command-line entry points, by purpose. Run them from the repository root;
each file's opening docstring or comment is its manual. "Provider" says whether
a script calls a language model. Games use the free fake provider unless
`AILIBI_LLM_PROVIDER` names a real one ([setup](../llm/README.md)).

## Set up and gate

| Script | What it does | Provider |
| --- | --- | --- |
| `setup_env.sh` | Installs the Python and frontend dependencies (needs the network). | none |
| `check.sh` | The full gate: lint, format, import contracts, task cards, links, types, tests, frontend. | fake |
| `check_doc_facts.py` | Recomputes the results page's figures (`RESULTS.md`) and the ML results table from their sources. | none |
| `check_links.py` | Reports relative links on the live pages that point at nothing. | none |
| `validate_task_docs.py` | Checks the work cards and the task index's card counts. | none |
| `gen_frontend_types.py` | Writes `frontend/src/types/api.ts` from the API's data models. | none |
| `regen_test_goldens.py` | Rewrites the test goldens taken from the finalist evaluation's rows. | none |

## Run

| Script | What it does | Provider |
| --- | --- | --- |
| `run_game.py` | Plays one game from a seed and writes its replay. | fake unless set |
| `run_tournament.py` | Plays a range of seeds and writes one typed report. | fake unless set |
| `run_spectator.sh` | Starts the replay API and the viewer on localhost. | none |

## Record and validate

| Script | What it does | Provider |
| --- | --- | --- |
| `refresh_samples.sh` | Re-records sample seeds and rewrites the set's manifest. | real by default; needs a budget |
| `record_ml_corpus.sh` | Records the training corpus on the locked hosted model. | real; needs a budget |
| `_manifest_writer.py` | Writes and totals a set's `MANIFEST.md` rows from its replays. | none |
| `_declared_experiment.py` | Checks a declared experiment config and where it may record. | none |
| `build_sample_report.py` | Rebuilds a set's tournament report from its replays. | none |
| `verify_samples.sh` | Replays every sample and candidate game and checks each state hash. | none |
| `validity_gate.py` | Runs the ten validity checks over one replay directory. | none |
| `scan_recording_packets.py` | Replays a set and counts its observation leak checks. | none |
| `fetch_evidence.sh` | Restores the evidence kept on pinned commits and verifies it (needs the network). | none |

## Publish

| Script | What it does | Provider |
| --- | --- | --- |
| `build_demo_bundle.py` | Builds the static demo: the viewer and every sample game, no API. | none |
| `publish_process_scorecard.py` | Writes `eval/reports/process-scorecard.md`. | none |
| `publish_gameplay_census.py` | Writes the gameplay census page and its JSON. | none |
| `publish_game_profile.py` | Writes the game-shape profile page and each set's profile JSON. | none |

The three publishers and `build_sample_report.py` take `--check`, which
recomputes and fails on drift.

## Measure

| Script | What it does | Provider |
| --- | --- | --- |
| `verify_ml_evidence.py` | Re-checks the ML evidence: hashes, corpus, verdicts, paired statistics, availability. | none |
| `paired_stats.py` | Paired win statistics over the finalist evaluation's rows. | none |
| `generate_campaign_tables.py` | Renders the campaign reports' tables from committed rows. | none |
| `measure_baseline.py` | Folds a replay set into the baseline measurements. | none |
| `measure_featured_criterion.py` | Counts the grounded ejections that order the viewer's featured games. | none |
| `measure_public_results.py` | Times the public results summary with and without its cache. | none |
| `measure_reasoning_evidence.py` | Writes the offline reasoning-evidence mechanics scorecard. | none |
| `measure_replay_loading.py` | Measures replay loading time, payload and memory. | none |
| `counterfactual_phase21.py` | Re-renders recorded meetings with three unadopted settings on and counts what moves. | none |

`_report_output.py`, `_tournament_progress.py` and `_verify_samples.py` are
helpers the scripts above import; `_verify_samples.py` also runs behind
`verify_samples.sh`.
