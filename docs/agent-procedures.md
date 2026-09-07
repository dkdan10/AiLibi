# Agent procedures

[AGENTS.md](../AGENTS.md) carries the universal rules. Read the relevant
procedure here when retiring mechanisms or publishing review records.

## Retiring substrate levers


When a substrate lever graduates — its `AILIBI_*` env gate retired, its
behavior unconditional, normally at a baseline adopting record — **delete the
mechanism, keep the stamp key and one history line.** What goes: the
`*_enabled()` resolver, the `ENV_*` constant and its `__all__` entry, the `env`
parameter wherever no live resolver is reachable from that call chain, every
`if <lever>_enabled():` guard (replaced by its always-taken side), and the tests
that pin the parameter rather than the behavior. What stays: the lever's
snake_case key in `orchestrator/replay.py::_RETIRED_ALWAYS_ON_LEVERS`, so a
recording keeps self-describing its substrate and the loader can still refuse a
legacy stamp recording it OFF — plus at most one trailing provenance line naming
the adopting record.

The prose sweep is still required; it is the smaller half. Grep the lever's
snake_case name repo-wide and rewrite every docstring, comment, and doc line
that still describes it as live or default-OFF: nothing may tell a reader it can
be switched off. The registry in `orchestrator/replay.py`
(`_RETIRED_ALWAYS_ON_LEVERS` / `_TOGGLEABLE_LEVER_RESOLVERS`) is the source of
truth for which levers are still live.

Keeping the shape is how nine dead resolvers accumulated across five
graduations. Task 20.37 is the precedent for doing it properly: it swept both
generations at once (seventeen resolvers, 332 source lines, 227 test env-lines)
and left behind the structural gate that stops them regenerating —
`tests/meetings/test_lever_registry.py` walks `agents/`, `meetings/` and
`orchestrator/` with `ast` and fails on any `*_enabled` function that neither
reads its `env` argument nor returns anything but a bare `True`.

## GitHub operations


GitHub tooling is environment-dependent: different dispatch environments
provision different integrations, so make no absolute assumption that one
path always works or another always fails. Detect what is available and use
it — do not declare GitHub work impossible without trying both.

- **Prefer whatever is actually configured.** If the `gh` CLI is present
  and authenticated (`which gh && gh auth status`), use it for GitHub work
  — PRs, issues, comments, diffs, reviews. If `gh` is absent or
  unauthenticated, use the environment's GitHub integration instead (e.g.
  the MCP-based `github` tools, `mcp__github__*`), which is the working
  path in environments where `gh` is not provisioned. Fall back from one to
  the other rather than giving up.
- **For PR creation,** populate every section of
  `.github/pull_request_template.md` (see "PR description (always)" below).
  On the `gh` path write the body to a file and use `gh pr create --body-file`;
  on the integration-tool path pass the same populated body to the
  create-PR call. Either way the body must contain every required section —
  never ship an empty body.

## PR description (always)

Every PR — task-driven or ad-hoc (audits, hygiene, hotfixes) — must
populate the sections in `.github/pull_request_template.md`:

- `## Summary` — 1–3 bullets stating what changed and why.
- `## Definition of done` — copy the task's checklist and tick each item;
  for ad-hoc PRs, list the scope you actually executed.
- `## Decisions` — every judgment call resolved without human input.
  Write "None." if there were none.
- `## Questions` — blocking questions only; omit the section if none.

When creating the PR, pass the fully populated template as the body: on the
`gh` path, `gh pr create --body-file` with the prepared file; on the
integration-tool path, the body parameter of the create-PR call. An
explicit body overrides the repo template, so the body you pass must itself
include every required section. Auto-fill or empty-body shortcuts (e.g.
`gh pr create --fill` / `--body ""`, or omitting the body field) ship empty
bodies and are not permitted.

## Environment and history

Run `bash scripts/setup_env.sh` in a fresh environment. Use `uv add` or
`uv lock` for intentional dependency changes and commit both project metadata
and the lockfile. Tests use the deterministic fake provider; real-provider
integration tests are opt-in as documented in [llm/README.md](../llm/README.md).

Before a history-derived claim, check `git rev-parse --is-shallow-repository`.
A shallow clone needs `git fetch --unshallow` or an equivalent full fetch;
never interpret a truncated log as complete project history.
