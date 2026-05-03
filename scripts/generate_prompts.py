"""Generate every ``agent_prompts/task-*.md`` from the task contracts.

The phase task files in ``tasks/phase-*.md`` are the single source of truth.
This generator materializes the shared Jinja2 template once per task,
producing the paste-ready prompts under ``agent_prompts/``.

Usage:
  - ``uv run python scripts/generate_prompts.py``         -- write prompts
  - ``uv run python scripts/generate_prompts.py --check`` -- diff against
        what is on disk; exit non-zero if any prompt would change.

The template lives next to this script as ``prompt_template.md.j2``.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from _task_parser import TaskDoc, parse_all_tasks, relative
from jinja2 import Environment, FileSystemLoader, StrictUndefined


SCRIPTS_DIR = Path(__file__).resolve().parent
TEMPLATE_NAME = "prompt_template.md.j2"


@dataclass(frozen=True)
class _ConstraintRule:
    sentence: str
    """One literal Section 5 line."""

    applies: bool
    """Whether this constraint applies to the current task."""


def render_prompt(
    task: TaskDoc,
    *,
    all_tasks: list[TaskDoc] | None = None,
) -> str:
    env = Environment(
        loader=FileSystemLoader(SCRIPTS_DIR),
        keep_trailing_newline=True,
        undefined=StrictUndefined,
    )
    template = env.get_template(TEMPLATE_NAME)
    siblings = all_tasks if all_tasks is not None else [task]
    return template.render(
        task=task,
        phase_basename=task.phase_path.name,
        title_lowercased=task.title.lower(),
        applicable_constraints=_constraints_for(task),
        dependency_check=_dependency_check_for(task, siblings),
    )


def _dependency_check_for(task: TaskDoc, all_tasks: list[TaskDoc]) -> list[str]:
    """Build importability commands from upstream tasks' Public types.

    The check is a best-effort tripwire: ``python -c "import X.Y"`` for each
    fully-qualified module path declared in upstream Public types. Bare or
    method-attribute symbols are skipped — they would fail import on their
    own dotted-path form.

    Tasks may also override or extend this list via the ``Dependency check``
    field in their contract; explicit commands take precedence.
    """

    if task.dependency_check:
        return list(task.dependency_check)

    by_id = {item.task_id: item for item in all_tasks}
    seen: set[str] = set()
    stack = list(task.depends_on)
    upstream_symbols: list[str] = []
    while stack:
        upstream_id = stack.pop()
        if upstream_id not in by_id or upstream_id in seen:
            continue
        seen.add(upstream_id)
        stack.extend(by_id[upstream_id].depends_on)
        upstream_symbols.extend(by_id[upstream_id].public_types)

    commands: list[str] = []
    seen_modules: set[str] = set()
    for symbol in upstream_symbols:
        module = _module_path(symbol)
        if module is None or module in seen_modules:
            continue
        seen_modules.add(module)
        commands.append(f'uv run python -c "import {module}"')
    return commands


def _module_path(symbol: str) -> str | None:
    """Return the importable module portion of a dotted symbol path.

    Strategy: drop the trailing identifier (whether ``ClassName`` or
    ``snake_function``) — every Public type declaration is module-qualified,
    so the last segment is always the symbol inside the module.

    ``agents.memory.episodic.MemoryStore`` -> ``agents.memory.episodic``.
    ``agents.tactical.pathing.find_path`` -> ``agents.tactical.pathing``.
    ``MemoryStore.append`` (no module prefix) -> ``None``.
    """

    parts = symbol.split(".")
    if len(parts) < 2:
        return None
    # The first segment must be a top-level package; if the symbol is a bare
    # ``ClassName.method`` reference, the leading segment is PascalCase, which
    # we treat as un-importable.
    if not parts[0].islower():
        return None
    return ".".join(parts[:-1])


def _constraints_for(task: TaskDoc) -> list[str]:
    """Return the Section 5 lines that apply to ``task``.

    The order matches the legacy hand-authored prompts so generated output is
    byte-identical for the existing prompt set.
    """

    in_scope = task.files_in_scope
    touches_agents = any(item.startswith("agents/") for item in in_scope)
    rules = (
        _ConstraintRule("Do not modify DESIGN.md.", True),
        _ConstraintRule("Do not modify AGENT_IMPLEMENTATION.md.", True),
        _ConstraintRule(
            "Do not modify tasks/phase-*.md unless this task explicitly lists "
            "those files in scope.",
            True,
        ),
        _ConstraintRule("Do not implement work outside this task.", True),
        _ConstraintRule(
            "Do not add LLM calls inside agents/tactical/.", touches_agents
        ),
        _ConstraintRule("Do not import engine/ from agents/.", touches_agents),
        _ConstraintRule(
            "If the task mentions engine-free boundary schemas, keep agents/ "
            "free of engine imports and put engine translation only in "
            "orchestrator-owned code.",
            touches_agents,
        ),
    )
    return [rule.sentence for rule in rules if rule.applies]


def write_prompt(task: TaskDoc, all_tasks: list[TaskDoc]) -> tuple[Path, str]:
    rendered = render_prompt(task, all_tasks=all_tasks)
    return task.prompt_path, rendered


def cmd_write() -> int:
    errors: list[str] = []
    tasks = parse_all_tasks(errors)
    if errors:
        print("Cannot generate prompts: parser errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    written = 0
    for task in tasks:
        path, content = write_prompt(task, tasks)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written += 1
    print(f"Wrote {written} prompts.")
    return 0


def cmd_check() -> int:
    errors: list[str] = []
    tasks = parse_all_tasks(errors)
    if errors:
        print("Cannot generate prompts: parser errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    drift: list[Path] = []
    for task in tasks:
        path, expected = write_prompt(task, tasks)
        actual = path.read_text(encoding="utf-8") if path.exists() else ""
        if actual != expected:
            drift.append(path)

    if drift:
        print(
            "Generated prompts are out of sync. Run "
            "`uv run python scripts/generate_prompts.py` and commit the result:",
            file=sys.stderr,
        )
        for path in drift:
            print(f"- {relative(path)}", file=sys.stderr)
        return 1

    print(f"All {len(tasks)} prompts are in sync.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify on-disk prompts match the template; do not write.",
    )
    args = parser.parse_args(argv)
    return cmd_check() if args.check else cmd_write()


if __name__ == "__main__":
    raise SystemExit(main())
