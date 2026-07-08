# Sample Replay Manifest

Provenance for the replay samples under `replays/samples/`. Each row records the
model snapshot and prompt-template versions a sample was generated with, so
Phase 5 metric outputs can be attributed to a specific prompt version + model
snapshot (DESIGN.md §9, §11.4). Maintained by `scripts/refresh_samples.sh` (Task
4.17); run `scripts/verify_samples.sh` to confirm every sample still reconstructs
byte-identically under the current engine.

| seed | model | prompt_versions | flags | policy | refreshed_at | git_sha | cost_usd | winner |
|------|-------|-----------------|-------|--------|--------------|---------|----------|--------|
| 1000 | Qwen/Qwen3-32B | accusation_round.qwen3_32b.v5, crewmate_report.qwen3_32b.v5, impostor_report.qwen3_32b.v5, vote_ballot.qwen3_32b.v6 | evidence_quality_lift, movement_perception, reporter_exculpation, testimony_as_content, unfreeze_memory, witnessed_kill_evidence | fsm-default | 2026-07-08 | a0c92e0 | 0.0000 | IMPOSTORS |
| 1001 | Qwen/Qwen3-32B | accusation_round.qwen3_32b.v5, crewmate_report.qwen3_32b.v5, impostor_report.qwen3_32b.v5, vote_ballot.qwen3_32b.v6 | evidence_quality_lift, movement_perception, reporter_exculpation, testimony_as_content, unfreeze_memory, witnessed_kill_evidence | fsm-default | 2026-07-08 | a0c92e0 | 0.0000 | CREWMATES |
| 1002 | Qwen/Qwen3-32B | accusation_round.qwen3_32b.v5, crewmate_report.qwen3_32b.v5, impostor_report.qwen3_32b.v5, vote_ballot.qwen3_32b.v6 | evidence_quality_lift, movement_perception, reporter_exculpation, testimony_as_content, unfreeze_memory, witnessed_kill_evidence | fsm-default | 2026-07-08 | a0c92e0 | 0.0000 | CREWMATES |
| 1003 | Qwen/Qwen3-32B | accusation_round.qwen3_32b.v5, crewmate_report.qwen3_32b.v5, impostor_report.qwen3_32b.v5, vote_ballot.qwen3_32b.v6 | evidence_quality_lift, movement_perception, reporter_exculpation, testimony_as_content, unfreeze_memory, witnessed_kill_evidence | fsm-default | 2026-07-08 | a0c92e0 | 0.0000 | CREWMATES |
| 1004 | Qwen/Qwen3-32B | accusation_round.qwen3_32b.v5, crewmate_report.qwen3_32b.v5, impostor_report.qwen3_32b.v5, vote_ballot.qwen3_32b.v6 | evidence_quality_lift, movement_perception, reporter_exculpation, testimony_as_content, unfreeze_memory, witnessed_kill_evidence | fsm-default | 2026-07-08 | a0c92e0 | 0.0000 | CREWMATES |
| 1005 | Qwen/Qwen3-32B | accusation_round.qwen3_32b.v5, crewmate_report.qwen3_32b.v5, impostor_report.qwen3_32b.v5, vote_ballot.qwen3_32b.v6 | evidence_quality_lift, movement_perception, reporter_exculpation, testimony_as_content, unfreeze_memory, witnessed_kill_evidence | fsm-default | 2026-07-08 | a0c92e0 | 0.0000 | CREWMATES |
| 1006 | Qwen/Qwen3-32B | accusation_round.qwen3_32b.v5, crewmate_report.qwen3_32b.v5, impostor_report.qwen3_32b.v5, vote_ballot.qwen3_32b.v6 | evidence_quality_lift, movement_perception, reporter_exculpation, testimony_as_content, unfreeze_memory, witnessed_kill_evidence | fsm-default | 2026-07-08 | a0c92e0 | 0.0000 | CREWMATES |
