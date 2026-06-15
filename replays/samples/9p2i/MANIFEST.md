# Sample Replay Manifest

Provenance for the replay samples under `replays/samples/`. Each row records the
model snapshot and prompt-template versions a sample was generated with, so
Phase 5 metric outputs can be attributed to a specific prompt version + model
snapshot (DESIGN.md §9, §11.4). Maintained by `scripts/refresh_samples.sh` (Task
4.17); run `scripts/verify_samples.sh` to confirm every sample still reconstructs
byte-identically under the current engine.

| seed | model | prompt_versions | refreshed_at | git_sha | cost_usd | winner |
|------|-------|-----------------|--------------|---------|----------|--------|
| 0 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 1 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 2 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 3 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 4 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 5 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 6 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 7 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 8 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 9 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 10 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 11 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 12 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 13 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | IMPOSTORS |
| 14 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 15 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 16 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 17 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | IMPOSTORS |
| 18 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 19 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 20 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 21 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 22 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 23 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 24 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 25 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | IMPOSTORS |
| 26 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 27 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 28 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 29 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 30 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 31 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 32 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 33 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 34 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 35 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 36 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 37 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 38 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 39 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 40 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 41 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 42 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 43 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 44 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 45 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 46 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 47 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
| 48 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | IMPOSTORS |
| 49 | qwen3.5:9b | accusation_round.v8, crewmate_report.v7, impostor_report_v5, vote_ballot/v5 | 2026-06-15 | 37d150f | 0.0000 | CREWMATES |
