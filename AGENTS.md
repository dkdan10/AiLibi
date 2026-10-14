# AGENTS.md

Read this file, [docs/architecture.md](docs/architecture.md) and the assigned
`process/tasks/work/<slug>.md` card before each task.
[docs/workflow.md](docs/workflow.md) says how a card is written, delivered and
reviewed; the [task index](process/tasks/README.md) names active ownership and
the next candidates. Dispatch by card path.

## Delivery

Implement a card on a short-lived `work/<card-slug>` branch and deliver it into
**`main`** through one pull request per card that fills every section of
[the PR template](.github/pull_request_template.md), as
[branch and delivery](docs/workflow.md#branch-and-delivery) and
[GitHub operations](docs/workflow.md#github-operations) describe. Commits stay
focused and verified, with the card path in the body; never squash away a
commit another document cites.

A push to `main` also publishes the demo, so a change to the viewer, the
featured games or the public-results payload is a publication decision
([deployment](docs/deployment.md)). Task completion never authorizes a
deployment or an experimental adoption.

## Sources and scope

- `docs/architecture.md` is authoritative for current layering, determinism and
  the substrate ladder. `process/DESIGN.md` is historical rationale.
- The card defines acceptance, permitted boundaries and record impact. Inspect
  current consumers before changing a symbol, path or constant. Directly
  necessary call-site, test, generated-output and documentation follow-through
  within the card's boundaries is permitted; record material decisions in
  Results.
- Protected architecture, additional behavior, public compatibility,
  dependencies, spending and experimental adoption need an owner decision
  unless already authorized. Explain the concrete blocking decision and ask; do
  not guess or claim completion, and continue independent work while it waits.
- Historical records under `process/` (phase contracts, past audits,
  `AGENT_IMPLEMENTATION.md`) are never rewritten, except that a move of the
  folder re-points the relative links they carry.

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
   [the retirement procedure](docs/workflow.md#retiring-substrate-levers).
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
concurrent dispatch, no threads. Ruff and its formatter must pass; tests use
pytest and Hypothesis. Setup, dependency changes and complete history follow
[environment and history](docs/workflow.md#environment-and-history).

A task is done only when every acceptance item has evidence, scope is satisfied,
`bash scripts/check.sh` passes, and Results references the card's architecture
or design sections, decisions, verification and limitations. Targeted tests are
development checks, not a replacement for the full gate. Reopen a done card if
review reveals unfinished work.

CI and ordinary implementation use the fake provider. Live calls need an
explicit provider plus a token, wall-time and cost budget, even on flat-rate
service ([llm/README.md](llm/README.md), `.env.example`); recording provenance
is in each set's `MANIFEST.md`.
