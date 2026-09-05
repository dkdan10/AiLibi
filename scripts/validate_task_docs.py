"""Validate current work cards and historical phase/prompt contracts.

New work cards have a small structural check; acceptance evidence still needs
review. Historical phase task files are their prompts' source of truth.
Prompt files may add execution guidance, but the copied contract stays in
sync with the matching task section.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

from _task_parser import (
    COMPLEXITY_VALUES,
    PROMPTS_DIR,
    TASKS_DIR,
    TaskDoc,
    extract_field,
    parse_all_tasks,
    relative,
)

# When a task is a Medium- or Integration-tier deliverable that introduces
# public types or hooks consumed by downstream tasks, the contract must
# include the corresponding scaffolding fields.
_REQUIRES_HINT = {"Medium", "Integration"}
_REQUIRES_INTEGRATION_RISK = {"Integration"}

# From Phase 20 on, every contract states its record impact (does the change
# move rendered/detector bytes, and so wait on the adopting record?) and the
# measurement that proves its DoD — AGENTS.md "Craft rules" rule 7. Earlier
# phases are history and are not re-validated.
_RECORD_IMPACT_PHASE_FLOOR = 20
_RECORD_IMPACT_FIELD = "Record impact"
_MEASUREMENT_FIELD = "Measurement"


def main() -> int:
    errors: list[str] = []
    tasks = parse_all_tasks(errors)

    if errors:
        print_errors(errors)
        return 1

    validate_complexity(tasks, errors)
    validate_record_impact_fields(tasks, errors)
    validate_public_types_unique(tasks, errors)
    validate_dependency_graph(tasks, errors)
    validate_hint_symbol_resolution(tasks)
    validate_prompt_set(tasks, errors)
    validate_prompts(tasks, errors)
    validate_parallel_file_scope(tasks, errors)
    work_count = validate_work_cards(TASKS_DIR / "work", errors)

    if errors:
        print_errors(errors)
        return 1

    print(
        "Task docs validation passed: "
        f"{len(tasks)} historical phase tasks and "
        f"{len(list(PROMPTS_DIR.glob('task-*.md')))} prompts; "
        f"{work_count} work cards."
    )
    return 0


def validate_work_cards(directory: Path, errors: list[str]) -> int:
    """Check card structure and completion declarations, not evidence quality."""

    paths = sorted(directory.glob("*.md"))
    if not paths:
        errors.append(f"{directory}: expected at least one work card.")
    for path in paths:
        body = _without_fenced_content(path.read_text())
        if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", path.stem) is None:
            errors.append(f"{path}: use a lowercase, hyphen-separated card name.")
        if len(re.findall(r"^# \S.*$", body, re.MULTILINE)) != 1:
            errors.append(f"{path}: expected one # title.")
        statuses = re.findall(r"^\*\*Status:\*\* (.*)$", body, re.MULTILINE)
        if len(statuses) != 1 or statuses[0] not in {"ready", "active", "done"}:
            errors.append(f"{path}: expected one Status: ready, active, or done.")

        sections: dict[str, str] = {}
        for block in re.split(r"^## ", body, flags=re.MULTILINE)[1:]:
            heading, _, content = block.partition("\n")
            if heading in sections:
                errors.append(f"{path}: duplicate section {heading!r}.")
            sections[heading] = content.strip()
        for heading in (
            "Outcome",
            "Evidence",
            "Acceptance",
            "Constraints",
            "Expected scope",
            "Record impact",
            "Validation",
        ):
            if not sections.get(heading):
                errors.append(f"{path}: missing or empty ## {heading}.")

        checks = re.findall(
            r"^[ \t]*(?:[-*+]|\d+[.)]) \[([^\]]*)\] \S.*$",
            sections.get("Acceptance", ""),
            re.MULTILINE,
        )
        if not checks:
            errors.append(f"{path}: Acceptance needs at least one checkbox.")
        if any(check not in {" ", "x", "X"} for check in checks):
            errors.append(f"{path}: Acceptance checkbox must be [ ] or [x].")
        if statuses == ["done"]:
            if " " in checks:
                errors.append(f"{path}: done card has unchecked acceptance items.")
            if not sections.get("Results"):
                errors.append(f"{path}: done card needs ## Results with evidence.")
    return len(paths)


def _without_fenced_content(body: str) -> str:
    """Ignore example syntax while retaining fences as nonempty section content."""

    lines: list[str] = []
    fence: str | None = None
    for line in body.splitlines():
        if fence is not None:
            if re.fullmatch(
                rf" {{0,3}}{re.escape(fence[0])}{{{len(fence)},}}[ \t]*", line
            ):
                fence = None
                lines.append(line)
            continue
        match = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if match is not None:
            fence = match.group(1)
        lines.append(line)
    return "\n".join(lines)


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


def _phase_number(task: TaskDoc) -> int:
    return int(task.task_id.split(".", maxsplit=1)[0])


def validate_record_impact_fields(tasks: list[TaskDoc], errors: list[str]) -> None:
    """Phase >= 20 contracts carry **Record impact:** and **Measurement:**.

    Both are inline fields (``**Field:** value`` on one line) and must be
    non-empty; they render into the prompt as part of the contract block.
    """

    for task in tasks:
        if _phase_number(task) < _RECORD_IMPACT_PHASE_FLOOR:
            continue
        for field_name in (_RECORD_IMPACT_FIELD, _MEASUREMENT_FIELD):
            if not extract_field(task.body, field_name):
                errors.append(
                    f"{relative(task.phase_path)}: Task {task.task_id} is missing "
                    f"**{field_name}:** (required from Phase "
                    f"{_RECORD_IMPACT_PHASE_FLOOR} on)."
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


def validate_dependency_graph(tasks: list[TaskDoc], errors: list[str]) -> None:
    """Reject unknown dependency ids and dependency cycles.

    Duplicate ids are already collapsed by the parser's order-preserving
    dedupe; unknown ids and cycles would otherwise surface only as a wedged
    frontier at dispatch time.
    """

    seen_ids: dict[str, TaskDoc] = {}
    for task in tasks:
        if task.task_id in seen_ids:
            other = seen_ids[task.task_id]
            errors.append(
                f"Duplicate task id {task.task_id}: "
                f"{relative(other.phase_path)}:{other.header_line} and "
                f"{relative(task.phase_path)}:{task.header_line} both define "
                "it — downstream id-keyed state would silently collapse them."
            )
        else:
            seen_ids[task.task_id] = task

    known = set(seen_ids)
    for task in tasks:
        for dependency_id in task.depends_on:
            if dependency_id not in known:
                errors.append(
                    f"{relative(task.phase_path)}: Task {task.task_id} depends "
                    f"on unknown task {dependency_id}."
                )

    by_id = {task.task_id: task for task in tasks}
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {task_id: WHITE for task_id in by_id}

    def visit(task_id: str, stack: list[str]) -> None:
        color[task_id] = GRAY
        stack.append(task_id)
        for dependency_id in by_id[task_id].depends_on:
            if dependency_id not in by_id:
                continue
            if color[dependency_id] == GRAY:
                cycle_start = stack.index(dependency_id)
                cycle = " -> ".join(stack[cycle_start:] + [dependency_id])
                errors.append(f"Dependency cycle: {cycle}.")
            elif color[dependency_id] == WHITE:
                visit(dependency_id, stack)
        stack.pop()
        color[task_id] = BLACK

    for task_id in by_id:
        if color[task_id] == WHITE:
            visit(task_id, [])


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
