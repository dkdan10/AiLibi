# Contributing

Read this before opening anything. The short version: **issues are welcome,
pull requests are not the workflow.**

## What this repository is

AiLibi is an experiment in agentic software workflow as much as it is a
social-deduction simulator. Every coding change is written by an AI coding agent
working against a task contract authored by the owner, in a fresh checkout, with
CI and a human review as the gates. The contract — not this file, and not a
conversation on a PR — is the specification the agent sees.

That has a direct consequence for outside contributions: there is no review lane
for unsolicited code. A drive-by pull request has no contract behind it, no
place in the phase dependency graph, and no reviewer budget. It will not be
merged, and saying so up front is fairer than leaving one open.

## What is welcome

**Issues.** Bug reports, reproductions, questions about the architecture, and
"this claim in the docs does not match the code" findings are all genuinely
useful — the last category especially. This project takes truth-in-documentation
seriously enough to spend whole tasks on it, and an outside reader spotting a
stale number or a docstring that contradicts the bytes is doing exactly the kind
of work the internal audits do.

A good issue says what you observed, what you expected, and how to reproduce it.
If it is about a specific claim, quote the file and line.

**Forks.** The license is MIT (see [LICENSE](LICENSE)). Fork it, take it apart,
build something else with it. No permission needed.

**Security reports** go through [SECURITY.md](SECURITY.md), not the issue
tracker.

## How the work actually happens

If you want to understand the loop — or you are an agent dispatched against a
contract in this repository — the authoritative reading order is:

1. [AGENTS.md](AGENTS.md) — the standing rules for any agent working here: the
   three load-bearing architectural decisions, the observation firewall, the
   coding conventions, and the definition of done.
2. `tasks/phase-N.md` — the task contracts. Each names its branch,
   dependencies, files in and out of scope, definition of done, and section
   refs. This is the spec.
3. `agent_prompts/task-*.md` — generated from those contracts by
   `scripts/generate_prompts.py`. **Never hand-edit a prompt**; edit the
   contract and regenerate.
4. [DESIGN.md](DESIGN.md) — the architecture document the contracts reference.

## Working on a change locally

```bash
bash scripts/setup_env.sh   # uv sync (incl. the dev group) + frontend deps
bash scripts/check.sh       # the full gate: ruff, import-linter, mypy, pytest, frontend
```

`scripts/check.sh` is the required gate and the one-command local truth: ruff,
import-linter, mypy, the task-doc and prompt generators, pytest, and the
frontend lint, typecheck, unit-test and build legs.

CI runs those same checks and one more the script deliberately leaves out: a
Playwright browser journey over the real app and the real API
(`.github/workflows/ci.yml`). It needs a browser and both dev servers running,
which is minutes of setup for a gate that is otherwise dependency-free. So a
green `check.sh` predicts CI except for that one job. To run it on demand:

```bash
cd frontend
npx playwright install chromium   # once per Playwright version; setup_env.sh
                                  # installs the npm packages, not the browser
npm run e2e
```

Neither the script nor CI's per-change jobs run the campaign tier: the frozen
ML-campaign test families, selected with `uv run pytest -m campaign`. Those run
weekly against `main` from `.github/workflows/campaign-tier.yml`.

Targeted `uv run ...` commands are fine while you are iterating, but a change is
not done until the whole script is green.

Two notes on the environment:

- Dev tooling (pytest, hypothesis, ruff, mypy, import-linter) lives in the `dev`
  dependency group, not in the runtime dependencies. `scripts/setup_env.sh`
  installs it; a plain `uv sync --no-dev` deliberately will not.
- Checks never hit the network. CI and `check.sh` always run against the
  deterministic fake LLM provider; the real-provider tests are opt-in behind
  environment gates (see [AGENTS.md](AGENTS.md)).

## The invariants that are not negotiable

If you do end up proposing a change, these hold regardless of how good the idea
is — they are enforced by tooling, and a change that breaks one is a change to
the architecture, not a change to the code:

- **The observation firewall.** `agents/` must not import from `engine/`,
  directly or transitively. `import-linter` enforces it.
- **Determinism.** The engine is a pure function of state and actions; replays
  are byte-identical from a seed. No wall-clock, no unseeded randomness.
- **No global state, no silent fallbacks.** State is owned by an explicit object
  and passed through. Invalid input raises rather than being papered over.

[ADR-0001](docs/adr/0001-three-load-bearing-decisions.md) records the reasoning.
