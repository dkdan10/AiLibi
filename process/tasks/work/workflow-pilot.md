# Pilot short, evidence-driven task cards

**Status:** done

## Outcome

New work starts from a short canonical card and current code. Keep the existing
architectural rules and verification while reducing duplicated instructions.
This pilot is authorized by the owner's request to begin the review's
recommendation on 2026-09-05.

## Evidence

`tasks/phase-21.md` mixes executable contracts with long completion histories.
`scripts/generate_prompts.py` copies contracts into committed launch prompts.
`scripts/validate_task_docs.py::validate_parallel_file_scope` conflates shared
files with logical dependencies. These mechanisms remain available for the
historical phase workflow; new cards need neither generated copies nor a new
scheduler.

## Acceptance

- [x] AGENTS routes new work to one card and preserves the historical workflow.
- [x] Guidance separates outcomes, protected boundaries, and expected files;
  direct necessary support work does not require another scope ratification.
- [x] Card validation rejects missing content and premature completion, with
  planted invalid cards proving the checks fail.
- [x] The full project gate checks both formats, and historical contracts,
  generated prompts, and game records remain unchanged.

## Constraints

Preserve the invariants in `docs/architecture.md`, the full verification gate,
human decisions on experiments and release adoption, and all historical phase
and generated-prompt bytes. Do not build a replacement orchestration platform.
The accounting repair is a separate card using this pilot policy.

## Expected scope

`AGENTS.md`, `docs/workflow.md`, `tasks/README.md`, `README.md`,
`CONTRIBUTING.md`, this card,
`scripts/validate_task_docs.py`, and `tests/scripts/test_work_cards.py`.
The existing validator is already invoked by `scripts/check.sh`.

## Record impact

None. Workflow documentation and structural checks do not change simulations,
rendered model prompts, detectors, schemas, or canonical evidence.

## Validation

Run `uv run pytest tests/scripts/test_work_cards.py tests/scripts/test_task_doc_guards.py`,
`uv run python scripts/validate_task_docs.py`,
`uv run python scripts/generate_prompts.py --check`, and `bash scripts/check.sh`.
Inspect `git diff --name-only` to confirm historical artifacts are untouched.

## Results

Verified 2026-09-05. The focused workflow and historical-guard tests passed
(37 tests); both contract formats validate, and all 390 historical prompts
remain synchronized. `bash scripts/check.sh` passed: 6,115 Python tests and
440 frontend tests, plus lint, types, imports, formatting, and build. The
server tests required localhost socket access outside the execution sandbox.

Independent review exposed alternate/nested unchecked items and fenced examples
that the initial parser mishandled; both now have adverse cases. The validator
checks declarations, while reviewers assess the quality of acceptance evidence.
README and CONTRIBUTING routing were necessary documentation follow-through.
Historical phase files, generated prompts, and recording files are unchanged.
