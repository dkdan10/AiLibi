# Sample Replay Manifest

Provenance for the replay samples under `replays/samples/`. Each row records the
model snapshot and prompt-template versions a sample was generated with, so
Phase 5 metric outputs can be attributed to a specific prompt version + model
snapshot (DESIGN.md §9, §11.4). Maintained by `scripts/refresh_samples.sh` (Task
4.17); run `scripts/verify_samples.sh` to confirm every sample still reconstructs
byte-identically under the current engine.

| seed | model | prompt_versions | refreshed_at | git_sha | cost_usd | winner |
|------|-------|-----------------|--------------|---------|----------|--------|
| 0 | qwen2.5:7b-instruct | (none — no meetings) | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 1 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 2 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 3 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 4 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 5 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 6 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 7 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 8 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | IMPOSTORS |
| 9 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 10 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 11 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 12 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | IMPOSTORS |
| 13 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | IMPOSTORS |
| 14 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 15 | qwen2.5:7b-instruct | (none — no meetings) | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 16 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 17 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 18 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 19 | qwen2.5:7b-instruct | (none — no meetings) | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 20 | qwen2.5:7b-instruct | (none — no meetings) | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 21 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 22 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 23 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 24 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 25 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 26 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 27 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 28 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 29 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 30 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 31 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 32 | qwen2.5:7b-instruct | (none — no meetings) | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 33 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 34 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 35 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 36 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 37 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 38 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 39 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | IMPOSTORS |
| 40 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 41 | qwen2.5:7b-instruct | (none — no meetings) | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 42 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 43 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 44 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 45 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 46 | qwen2.5:7b-instruct | (none — no meetings) | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 47 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 48 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
| 49 | qwen2.5:7b-instruct | accusation_round.v4, crewmate_report.v2, impostor_report_v3, vote_ballot/v4 | 2026-06-07 | 83a8bd8 | 0.0000 | CREWMATES |
