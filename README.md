# Phase-21 Wave-2 lever-ON recording — the FINDING record's evidence bytes

**These bytes reconstruct ONLY under the declared Wave-2 slate**
(`AILIBI_REPORTER_REASONING=1`, `AILIBI_CORROBORATION_DISCIPLINE=1`,
`AILIBI_TESTIMONY_SHAPES=1`, with `AILIBI_IMPOSTOR_ROLL_CALL` unset), and they are NOT the
canonical replay sets. Every game here stamps those three keys `True`; the keys are still live
toggles that resolve `False` in a bare shell, so `api/replay_loader.py::_assert_substrate_matches`
compares the recorded `True` against a live `False` and REFUSES the game. That is why this recording
lives on its own commit instead of replacing `replays/samples/` or `replays/ml_corpus/`: putting it
there would break the bare `scripts/verify_samples.sh` leg, the served frontend and the phase close's
own gate rerun, on bytes that are perfectly valid under their own slate.

## What this is

Task 21.24's adopting record: 300 games over the four sets, recorded live on Featherless
`Qwen/Qwen3.6-27B` at `$0`, source state `44f0a28c`. The pre-registered rule
(`audits/audit-phase-21-preregistration.md` §6) read **FINDING** over them — bars 1, 2 and 3 MET,
bar 4 MISSED at 0.5500 against a target of < 0.40 — so the Wave-2 levers did not graduate, the
ladder tip stayed at baseline 8, and the canonical sets kept their baseline-8 bytes. The record is
published all the same: `audits/audit-phase-21-adopting-record.md` carries the whole read, and these
are the bytes it reads.

| set | games | meetings | ejections |
|---|---|---|---|
| `samples/9p2i` | 50 | 168 | 89 |
| `ml_corpus/9p2i` | 150 | 435 | 277 |
| `samples/4p1i` | 50 | 39 | 19 |
| `ml_corpus/4p1i` | 50 | 43 | 26 |

Every leg passed the validity gate on all ten checks, the lever-ON tripwire reader exits 0 with
`stopped_cells` empty on all four, and no leg carries a `deadline_default` row under either shape.

## How to read them

```bash
# the substrate these bytes need, in the shell that opens them
export AILIBI_LLM_PROVIDER=featherless AILIBI_PROMPT_SET=qwen3_6_27b
export AILIBI_LLM_MEETING_MODEL=Qwen/Qwen3.6-27B
export AILIBI_REPORTER_REASONING=1 AILIBI_CORROBORATION_DISCIPLINE=1 AILIBI_TESTIMONY_SHAPES=1
unset AILIBI_IMPOSTOR_ROLL_CALL

uv run python scripts/validity_gate.py <set dir> --expected-model Qwen/Qwen3.6-27B --require-zero-cost
uv run python scripts/counterfactual_phase21.py --recording <set dir> --recorded-slate on --json
uv run python -m eval.reporter_justice <the four set dirs> --pooled
```

Reading them in a BARE shell will fail, loudly and correctly. That refusal is the mechanism working,
not a corrupt recording.

## Provenance

Model `Qwen/Qwen3.6-27B` at the pinned Featherless endpoint; prompt set `qwen3_6_27b` at the
composite lever-ON stamp
`accusation_round.qwen3_6_27b.v5.reporter_reasoning+…testimony_shapes`,
`crewmate_report.…`, `impostor_report.qwen3_6_27b.v5`,
`vote_ballot.qwen3_6_27b.v5.corroboration_discipline+…testimony_shapes`; tactical policy
`fsm-default`; `$0.0000` on every MANIFEST row. Each set's MANIFEST names the `git_sha` its rows were
recorded at — the only thing that separates this record's ballot body from the certified smoke's,
since PR #424 changed one line inside the lever-guarded block without a version bump.
