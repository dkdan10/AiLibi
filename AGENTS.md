# AGENTS.md

Read this file, [docs/architecture.md](docs/architecture.md), and the assigned
`tasks/work/<slug>.md` card before each task. New cards follow
[docs/workflow.md](docs/workflow.md); [tasks/README.md](tasks/README.md) names the
active ownership and next candidates. Dispatch by card path, without generated
prompt copies.

## Delivery

Work directly on **`codex/cleanup`**. Deliver focused, verified commits and push
them to `origin/codex/cleanup`; include the card path in the commit body.
Preserve published commit identities. Do not create routine implementation
branches or require a per-task PR. Existing PRs remain review records: do not
close, retarget, or merge them as part of cleanup.

Keep **`main` unchanged**. After the entire cleanup, the owner arranges Claude's
review by commit or PR and the final merge. Task completion never authorizes an
intermediate merge, deployment, or experimental adoption.

## Sources and scope

- `docs/architecture.md` is authoritative for current layering, determinism,
  and the substrate ladder. `DESIGN.md` is historical rationale.
- The card defines acceptance, permitted boundaries, and record impact. Inspect
  current consumers before changing a symbol, path, or constant. Directly
  necessary call-site, test, generated-output, and documentation follow-through
  within the card's boundaries is permitted; coordinate shared-file ownership
  and record material decisions in Results.
- Protected architecture, additional behavior, public compatibility,
  dependencies, spending, and experimental adoption need an owner decision
  unless already authorized. Continue independent work while a decision waits.
- Historical `tasks/phase-*.md` and `agent_prompts/` retain their contracts and
  checks. An explicitly resumed phase task keeps its exact scope; edit its
  contract and regenerate with `scripts/generate_prompts.py`, never hand-edit
  generated prompts. `AGENT_IMPLEMENTATION.md` is historical onboarding.

## Load-bearing rules

1. The engine is a pure, deterministic tick function of state and actions.
   Replays from a seed must remain byte-identical within their recorded scope.
2. LLMs run only at meetings or explicit triggers. Tactical decisions are
   rule-based; never add LLM calls inside `agents/tactical/`.
3. Agents reason from typed event memory and derived beliefs; models receive
   rendered memory, not raw chat.
4. The observation firewall is mandatory: `agents/` must not import `engine/`.
   Preserve import-linter and semantic leak checks; do not bypass the boundary.
5. No module-level mutable state or singletons. Explicit objects own state.
   Invalid input raises; no silent fallbacks.

## Craft rules

1. Comments explain current intent. Provenance is at most one trailing line.
2. A new invariant gate includes a planted or perturbed case proving it fails
   on the claimed semantic defect.
3. Retire means delete the dead mechanism and coupled consumers. For graduated
   levers, retain the replay stamp key and one history line; follow
   [the full retirement procedure](docs/agent-procedures.md#retiring-substrate-levers).
4. User-facing copy and model speech contain no task/audit IDs, unexplained
   jargon, or threshold arithmetic. Define necessary terms in `docs/glossary.md`.
5. Claims name their enforcing mechanism; numbers are reproducible from
   committed evidence, with the command in the card's Results or PR.
6. Inspect blast radius before editing and coordinate one writer per file.
7. Declare record impact and measurement. Prompt-byte and detector changes stay
   default-OFF behind an explicit experimental gate until an adopting record;
   graduation deletes the switch. Preserve earlier experiment verdicts.

## Implementation and verification

Use Python 3.11, type hints on every function, strict mypy, Pydantic v2 for data
crossing boundaries, and frozen dataclasses for engine state. Use asyncio for
concurrent dispatch, no threads. Ruff/format must pass; tests use pytest and
Hypothesis. Follow [environment and history procedures](docs/agent-procedures.md#environment-and-history)
for fresh setup, dependency changes, and complete history.

A task is done only when every acceptance item has evidence, scope is satisfied,
`bash scripts/check.sh` passes, and Results references the card's architecture
or design sections, decisions, verification, and limitations. Reopen a done
card if review reveals unfinished work. Targeted tests are development checks,
not a replacement for the full gate.

CI and ordinary implementation use the fake provider. Live calls need an
explicit provider plus token, wall-time, and cost budget, including on flat-rate
service. Provider details are in [llm/README.md](llm/README.md) and `.env.example`;
recording provenance is in each set's `MANIFEST.md`.

For optional PRs, use [GitHub procedures](docs/agent-procedures.md#github-operations)
and populate `.github/pull_request_template.md`. For cleanup commits without a
PR, the task card's Results carries equivalent review evidence. Explain concrete
blocking decisions there and ask the owner; do not guess or claim completion.
