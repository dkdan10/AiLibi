"""Validate AiLibi task files and paste-ready task prompts.

The phase task files are the source of truth. Prompt files are allowed to add
execution guidance, but the copied task contract must stay byte-for-byte in
sync with the matching task section.
"""

from __future__ import annotations

from pathlib import Path
import sys

from _task_parser import (
    COMPLEXITY_VALUES,
    PROMPTS_DIR,
    TaskDoc,
    parse_all_tasks,
    relative,
)

# When a task is a Medium- or Integration-tier deliverable that introduces
# public types or hooks consumed by downstream tasks, the contract must
# include the corresponding scaffolding fields.
_REQUIRES_HINT = {"Medium", "Integration"}
_REQUIRES_INTEGRATION_RISK = {"Integration"}


def main() -> int:
    errors: list[str] = []
    tasks = parse_all_tasks(errors)

    if errors:
        print_errors(errors)
        return 1

    validate_complexity(tasks, errors)
    validate_public_types_unique(tasks, errors)
    validate_hint_symbol_resolution(tasks)
    validate_prompt_set(tasks, errors)
    validate_prompts(tasks, errors)
    validate_parallel_file_scope(tasks, errors)

    if errors:
        print_errors(errors)
        return 1

    print(
        "Task docs validation passed: "
        f"{len(tasks)} tasks and {len(list(PROMPTS_DIR.glob('task-*.md')))} prompts."
    )
    return 0


def validate_complexity(tasks: list[TaskDoc], errors: list[str]) -> None:
    for task in tasks:
        if task.complexity is None:
            errors.append(
                f"{relative(task.phase_path)}: Task {task.task_id} is missing "
                f"**Complexity:** ({', '.join(COMPLEXITY_VALUES)})."
            )
            continue
        if task.complexity not in COMPLEXITY_VALUES:
            errors.append(
                f"{relative(task.phase_path)}: Task {task.task_id} has invalid "
                f"complexity {task.complexity!r}; expected one of "
                f"{', '.join(COMPLEXITY_VALUES)}."
            )
            continue

        if task.complexity in _REQUIRES_HINT and task.implementation_hint is None:
            errors.append(
                f"{relative(task.phase_path)}: Task {task.task_id} is "
                f"{task.complexity}-tier but is missing "
                "**Implementation hint:**."
            )
        if (
            task.complexity in _REQUIRES_INTEGRATION_RISK
            and task.integration_risk is None
        ):
            errors.append(
                f"{relative(task.phase_path)}: Task {task.task_id} is "
                "Integration-tier but is missing **Integration risk:**."
            )


def validate_public_types_unique(tasks: list[TaskDoc], errors: list[str]) -> None:
    seen: dict[str, str] = {}
    for task in tasks:
        for symbol in task.public_types:
            if symbol in seen:
                errors.append(
                    f"Public type {symbol!r} is claimed by both task "
                    f"{seen[symbol]} and task {task.task_id}."
                )
                continue
            seen[symbol] = task.task_id


def validate_hint_symbol_resolution(tasks: list[TaskDoc]) -> None:
    """Best-effort traversal: walk implementation hints for dotted symbols.

    Today this is a no-op walk — it just exercises the upstream graph so the
    helper stays warm. When tighter resolution lands, switch to error
    accumulation here without changing call sites.
    """

    public_types_by_task = {task.task_id: set(task.public_types) for task in tasks}
    for task in tasks:
        if task.implementation_hint is None:
            continue
        upstream = _collect_upstream_public_types(task, tasks, public_types_by_task)
        own = set(task.public_types)
        for _ in _dotted_paths_in_block(task.implementation_hint):
            _ = upstream | own  # placeholder for future resolution check


def _collect_upstream_public_types(
    task: TaskDoc,
    all_tasks: list[TaskDoc],
    public_types_by_task: dict[str, set[str]],
) -> set[str]:
    by_id = {item.task_id: item for item in all_tasks}
    seen: set[str] = set()
    stack = list(task.depends_on)
    while stack:
        upstream_id = stack.pop()
        if upstream_id not in by_id or upstream_id in seen:
            continue
        seen.add(upstream_id)
        stack.extend(by_id[upstream_id].depends_on)
    aggregated: set[str] = set()
    for upstream_id in seen:
        aggregated.update(public_types_by_task.get(upstream_id, set()))
    return aggregated


def _dotted_paths_in_block(block: str) -> list[str]:
    import re

    return re.findall(r"\b[a-z][a-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*){2,}", block)


def validate_prompt_set(tasks: list[TaskDoc], errors: list[str]) -> None:
    referenced: dict[Path, TaskDoc] = {}
    for task in tasks:
        if task.prompt_path in referenced:
            other = referenced[task.prompt_path]
            errors.append(
                "Duplicate prompt path "
                f"{relative(task.prompt_path)} for tasks {other.task_id} and "
                f"{task.task_id}."
            )
        referenced[task.prompt_path] = task

    actual = set(PROMPTS_DIR.glob("task-*.md"))
    expected = set(referenced)

    for path in sorted(expected - actual):
        errors.append(f"Missing prompt file: {relative(path)}.")
    for path in sorted(actual - expected):
        errors.append(
            f"Extra prompt file not referenced by phase tasks: {relative(path)}."
        )


def validate_prompts(tasks: list[TaskDoc], errors: list[str]) -> None:
    for task in tasks:
        if not task.prompt_path.exists():
            continue

        prompt = task.prompt_path.read_text()
        expected_title = f"# Agent Prompt — {task.task_id} {task.title}"
        if expected_title not in prompt.splitlines()[:1]:
            errors.append(
                f"{relative(task.prompt_path)}: expected title {expected_title!r}."
            )

        expected_reference = f"Implement Task {task.task_id} — {task.title}"
        if expected_reference not in prompt:
            errors.append(
                f"{relative(task.prompt_path)}: missing task reference "
                f"{expected_reference!r}."
            )

        if task.contract not in prompt:
            errors.append(
                f"{relative(task.prompt_path)}: copied task contract does not match "
                f"{relative(task.phase_path)} Task {task.task_id}."
            )

        for required_phrase in (
            "Pre-flight checklist",
            "Inspect the current implementation before editing.",
            "Verification checklist",
            "Run `git diff --name-only` and confirm the diff stays within scope.",
            "If any Definition of done item is unchecked, report it explicitly",
            "Decisions vs questions",
        ):
            if required_phrase not in prompt:
                errors.append(
                    f"{relative(task.prompt_path)}: missing required prompt guidance "
                    f"{required_phrase!r}."
                )


def validate_parallel_file_scope(tasks: list[TaskDoc], errors: list[str]) -> None:
    by_phase: dict[Path, list[TaskDoc]] = {}
    for task in tasks:
        by_phase.setdefault(task.phase_path, []).append(task)

    for phase_path, phase_tasks in by_phase.items():
        task_by_id = {task.task_id: task for task in phase_tasks}
        dependencies = {
            task.task_id: dependencies_within_phase(task, task_by_id)
            for task in phase_tasks
        }

        for index, left in enumerate(phase_tasks):
            for right in phase_tasks[index + 1 :]:
                overlap = overlapping_scope_items(
                    left.files_in_scope, right.files_in_scope
                )
                if not overlap:
                    continue
                if is_ordered(left.task_id, right.task_id, dependencies):
                    continue
                errors.append(
                    f"{relative(phase_path)}: tasks {left.task_id} and "
                    f"{right.task_id} both edit {', '.join(overlap)} but neither "
                    "depends on the other."
                )


def dependencies_within_phase(
    task: TaskDoc, task_by_id: dict[str, TaskDoc]
) -> set[str]:
    direct = {task_id for task_id in task.depends_on if task_id in task_by_id}
    resolved: set[str] = set()
    stack = list(direct)
    while stack:
        task_id = stack.pop()
        if task_id in resolved:
            continue
        resolved.add(task_id)
        stack.extend(
            dependency_id
            for dependency_id in task_by_id[task_id].depends_on
            if dependency_id in task_by_id
        )
    return resolved


def overlapping_scope_items(
    left_items: tuple[str, ...], right_items: tuple[str, ...]
) -> list[str]:
    overlaps: list[str] = []
    for left in left_items:
        for right in right_items:
            if scope_items_overlap(left, right):
                overlaps.append(f"{left} / {right}" if left != right else left)
    return overlaps


def scope_items_overlap(left: str, right: str) -> bool:
    if "*" in left or "*" in right:
        return left == right
    if left == right:
        return True

    left_dir = left if left.endswith("/") else f"{left}/"
    right_dir = right if right.endswith("/") else f"{right}/"
    return right.startswith(left_dir) or left.startswith(right_dir)


def is_ordered(left_id: str, right_id: str, dependencies: dict[str, set[str]]) -> bool:
    return left_id in dependencies[right_id] or right_id in dependencies[left_id]


def print_errors(errors: list[str]) -> None:
    print("Task docs validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
