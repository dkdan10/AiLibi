# Sample Replay Manifest

Provenance for the replay samples under `replays/samples/`. Each row records the
model snapshot and prompt-template versions a sample was generated with, so
Phase 5 metric outputs can be attributed to a specific prompt version + model
snapshot (DESIGN.md §9, §11.4). Maintained by `scripts/refresh_samples.sh` (Task
4.17); run `scripts/verify_samples.sh` to confirm every sample still reconstructs
byte-identically under the current engine.

| seed | model | prompt_versions | refreshed_at | git_sha | cost_usd | winner |
|------|-------|-----------------|--------------|---------|----------|--------|
| 0 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | CREWMATES |
| 1 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 2 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 3 | qwen2.5:7b-instruct | (none — no meetings) | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 4 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | CREWMATES |
| 5 | qwen2.5:7b-instruct | (none — no meetings) | 2026-06-03 | 7444e74 | 0.0000 | CREWMATES |
| 6 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 7 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 8 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 9 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 10 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 11 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | CREWMATES |
| 12 | qwen2.5:7b-instruct | (none — no meetings) | 2026-06-03 | 7444e74 | 0.0000 | CREWMATES |
| 13 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 14 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 15 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 16 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 17 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 18 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | CREWMATES |
| 19 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 20 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | CREWMATES |
| 21 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 22 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 23 | qwen2.5:7b-instruct | (none — no meetings) | 2026-06-03 | 7444e74 | 0.0000 | CREWMATES |
| 24 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 25 | qwen2.5:7b-instruct | (none — no meetings) | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 26 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 27 | qwen2.5:7b-instruct | (none — no meetings) | 2026-06-03 | 7444e74 | 0.0000 | CREWMATES |
| 28 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | CREWMATES |
| 29 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 30 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 31 | qwen2.5:7b-instruct | (none — no meetings) | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 32 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 33 | qwen2.5:7b-instruct | (none — no meetings) | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 34 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 35 | qwen2.5:7b-instruct | (none — no meetings) | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 36 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 37 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 38 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 39 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | CREWMATES |
| 40 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 41 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 42 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | CREWMATES |
| 43 | qwen2.5:7b-instruct | (none — no meetings) | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 44 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 45 | qwen2.5:7b-instruct | (none — no meetings) | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 46 | qwen2.5:7b-instruct | (none — no meetings) | 2026-06-03 | 7444e74 | 0.0000 | CREWMATES |
| 47 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 48 | qwen2.5:7b-instruct | (none — no meetings) | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
| 49 | qwen2.5:7b-instruct | accusation_round.v3, crewmate_report.v1, impostor_report_v2, vote_ballot/v2 | 2026-06-03 | 7444e74 | 0.0000 | IMPOSTORS |
