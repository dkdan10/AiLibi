# Sample Replay Manifest

Provenance for the replay samples under `replays/samples/`. Each row records the
model snapshot and prompt-template versions a sample was generated with, so
Phase 5 metric outputs can be attributed to a specific prompt version + model
snapshot (DESIGN.md §9, §11.4). Maintained by `scripts/refresh_samples.sh` (Task
4.17); run `scripts/verify_samples.sh` to confirm every sample still reconstructs
byte-identically under the current engine.

| seed | model | prompt_versions | refreshed_at | git_sha | cost_usd | winner |
|------|-------|-----------------|--------------|---------|----------|--------|
| 0 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 1 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 2 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 3 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 4 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | IMPOSTORS |
| 5 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 6 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 7 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 8 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 9 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 10 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | IMPOSTORS |
| 11 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 12 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 13 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 14 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 15 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | IMPOSTORS |
| 16 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 17 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | IMPOSTORS |
| 18 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | IMPOSTORS |
| 19 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | IMPOSTORS |
| 20 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | IMPOSTORS |
| 21 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | IMPOSTORS |
| 22 | claude-sonnet-4-6 | accusation_round.v2, crewmate_report.v1, impostor_report_v1, vote_ballot/v1 | 2026-05-30 | 772d15d | 0.2171 | CREWMATES |
| 23 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | IMPOSTORS |
| 24 | claude-sonnet-4-6 | accusation_round.v2, crewmate_report.v1, impostor_report_v1, vote_ballot/v1 | 2026-05-30 | 772d15d | 0.2109 | CREWMATES |
| 25 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 26 | claude-sonnet-4-6 | accusation_round.v2, crewmate_report.v1, impostor_report_v1, vote_ballot/v1 | 2026-05-30 | 772d15d | 0.3745 | CREWMATES |
| 27 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 28 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | IMPOSTORS |
| 29 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | IMPOSTORS |
| 30 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 31 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 32 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | IMPOSTORS |
| 33 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 34 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | IMPOSTORS |
| 35 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 36 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 37 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | IMPOSTORS |
| 38 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 39 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 40 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 41 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | IMPOSTORS |
| 42 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 43 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 44 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | IMPOSTORS |
| 45 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | IMPOSTORS |
| 46 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | IMPOSTORS |
| 47 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 48 | claude-sonnet-4-6 | (none — no meetings) | 2026-05-27 | b61d67e | 0.0000 | CREWMATES |
| 49 | claude-sonnet-4-6 | accusation_round.v2, crewmate_report.v1, impostor_report_v1, vote_ballot/v1 | 2026-05-30 | 772d15d | 0.2438 | CREWMATES |
