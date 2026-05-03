"""Validate AiLibi task files and paste-ready Codex prompts.

The phase task files are the source of truth. Prompt files are allowed to add
execution guidance, but the copied task contract must stay byte-for-byte in
sync with the matching task section.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "tasks"
PROMPTS_DIR = ROOT / "codex_prompts"

TASK_HEADER_RE = re.compile(
    r"^### Task (?P<task_id>\d+\.(?:B\d+|P\d+|\d+(?:\.\d+)?[a-z]?))"
    r" — (?P<title>.+)$",
    re.MULTILINE,
)
FUTURE_TASK_ID_RE = re.compile(r"^[2-9]\d*\.[1-9]\d*$")
PROMPT_PATH_RE = re.compile(
    r"\*\*Ready-to-paste prompt:\*\* `(?P<path>codex_prompts/[^`]+\.md)`"
)
FIELD_RE = re.compile(r"^\*\*(?P<field>[^:]+):\*\* (?P<value>.*)$", re.MULTILINE)
TASK_ID_RE = re.compile(r"\b(?P<task_id>\d+\.(?:B\d+|P\d+|\d+(?:\.\d+)?[a-z]?))\b")


@dataclass(frozen=True)
class TaskDoc:
    phase_path: Path
    task_id: str
    title: str
    body: str
    contract: str
    prompt_path: Path
    branch: str
    depends_on: tuple[str, ...]
    section_refs: str
    files_in_scope: tuple[str, ...]


def main() -> int:
    errors: list[str] = []
    tasks = parse_all_tasks(errors)

    if errors:
        print_errors(errors)
        return 1

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


def parse_all_tasks(errors: list[str]) -> list[TaskDoc]:
    tasks: list[TaskDoc] = []
    for phase_path in sorted(TASKS_DIR.glob("phase-*.md")):
        tasks.extend(parse_phase_file(phase_path, errors))
    return tasks


def parse_phase_file(phase_path: Path, errors: list[str]) -> list[TaskDoc]:
    text = phase_path.read_text()
    matches = list(TASK_HEADER_RE.finditer(text))
    tasks: list[TaskDoc] = []

    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        task_id = match.group("task_id")
        title = match.group("title").strip()
        if (
            is_future_phase_task_id(task_id)
            and FUTURE_TASK_ID_RE.fullmatch(task_id) is None
        ):
            errors.append(
                f"{phase_path}: Task {task_id} must use simple numeric "
                "Phase 2+ numbering like N.1, N.2, N.3."
            )

        prompt_match = PROMPT_PATH_RE.search(body)
        if prompt_match is None:
            errors.append(f"{phase_path}: Task {task_id} is missing a prompt path.")
            continue

        contract = extract_contract(phase_path, task_id, body, errors)
        branch = extract_field(body, "Branch")
        depends = parse_depends_on(extract_field(body, "Depends on"))
        section_refs = extract_field(body, "Section refs")
        files_in_scope = extract_files_in_scope(body)

        tasks.append(
            TaskDoc(
                phase_path=phase_path,
                task_id=task_id,
                title=title,
                body=body,
                contract=contract,
                prompt_path=ROOT / prompt_match.group("path"),
                branch=branch,
                depends_on=depends,
                section_refs=section_refs,
                files_in_scope=files_in_scope,
            )
        )

    return tasks


def extract_contract(
    phase_path: Path, task_id: str, body: str, errors: list[str]
) -> str:
    marker = "**Ready-to-paste prompt:**"
    if marker not in body:
        errors.append(f"{phase_path}: Task {task_id} is missing {marker}.")
        return ""

    contract = body.split(marker, maxsplit=1)[0].strip()
    if not contract.startswith("**Branch:**"):
        errors.append(
            f"{phase_path}: Task {task_id} contract must start at **Branch:**."
        )
    if "**Definition of done:**" not in contract:
        errors.append(f"{phase_path}: Task {task_id} is missing Definition of done.")
    if "**Files in scope" not in contract:
        errors.append(f"{phase_path}: Task {task_id} is missing Files in scope.")
    if "**Files NOT in scope:**" not in contract:
        errors.append(f"{phase_path}: Task {task_id} is missing Files NOT in scope.")
    return contract


def extract_field(body: str, field_name: str) -> str:
    for match in FIELD_RE.finditer(body):
        if match.group("field") == field_name:
            return match.group("value").strip()
    return ""


def parse_depends_on(value: str) -> tuple[str, ...]:
    if value.lower() in {"", "none"}:
        return ()
    return tuple(match.group("task_id") for match in TASK_ID_RE.finditer(value))


def is_future_phase_task_id(task_id: str) -> bool:
    return int(task_id.split(".", maxsplit=1)[0]) >= 2


def extract_files_in_scope(body: str) -> tuple[str, ...]:
    match = re.search(
        r"\*\*Files in scope(?: \([^)]+\))?:\*\*\n(?P<items>.*?)(?=\n\*\*)",
        body,
        flags=re.DOTALL,
    )
    if match is None:
        return ()

    files: list[str] = []
    for line in match.group("items").splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            files.append(normalize_scope_item(stripped[2:]))
    return tuple(files)


def normalize_scope_item(item: str) -> str:
    normalized = item.strip().strip("`")
    if "; " in normalized:
        normalized = normalized.split("; ", maxsplit=1)[0].strip()
    return normalized


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
        expected_title = f"# Codex Prompt — {task.task_id} {task.title}"
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


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def print_errors(errors: list[str]) -> None:
    print("Task docs validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
