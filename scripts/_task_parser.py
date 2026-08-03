"""Shared parser for AiLibi task contracts.

Reads ``tasks/phase-N.md`` files and yields :class:`TaskDoc` records used by
both ``scripts/validate_task_docs.py`` (validation) and
``scripts/generate_prompts.py`` (template materialization).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "tasks"
PROMPTS_DIR = ROOT / "agent_prompts"

TASK_HEADER_RE = re.compile(
    r"^### Task (?P<task_id>\d+\.(?:B\d+|P\d+|\d+(?:\.\d+)?[a-z]?))"
    r" — (?P<title>.+)$",
    re.MULTILINE,
)
# Phase number is any integer >= 2: a single digit 2-9, or two-plus digits
# (10 and up). The previous pattern `[2-9]\d*` required the FIRST digit to be
# 2-9, silently excluding phases 10-19; it surfaced the day phase-10.md landed.
FUTURE_TASK_ID_RE = re.compile(r"^(?:[2-9]|[1-9]\d+)\.[1-9]\d*(?:\.[1-9]\d*)?$")
PROMPT_PATH_RE = re.compile(
    r"\*\*Ready-to-paste prompt:\*\* `(?P<path>agent_prompts/[^`]+\.md)`"
)
FIELD_RE = re.compile(r"^\*\*(?P<field>[^:]+):\*\* (?P<value>.*)$", re.MULTILINE)
TASK_ID_RE = re.compile(r"\b(?P<task_id>\d+\.(?:B\d+|P\d+|\d+(?:\.\d+)?[a-z]?))\b")
COMPLEXITY_VALUES = ("Trivial", "Small", "Medium", "Integration")


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
    complexity: str | None
    public_types: tuple[str, ...]
    implementation_hint: str | None
    integration_risk: str | None
    dependency_check: tuple[str, ...]
    # 1-indexed line of the ``### Task`` header in ``phase_path`` — duplicate-id
    # diagnostics print it so two headers in one file are distinguishable.
    header_line: int = 0


def parse_all_tasks(errors: list[str] | None = None) -> list[TaskDoc]:
    """Parse every task in every phase file under tasks/."""

    accumulator: list[str] = errors if errors is not None else []
    tasks: list[TaskDoc] = []
    for phase_path in sorted(TASKS_DIR.glob("phase-*.md")):
        tasks.extend(parse_phase_file(phase_path, accumulator))
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
        complexity = extract_optional_field(body, "Complexity") or None
        public_types = extract_bullet_block(body, "Public types introduced")
        implementation_hint = extract_block_section(body, "Implementation hint")
        integration_risk = extract_block_section(body, "Integration risk")
        dependency_check = extract_bullet_block(body, "Dependency check")

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
                complexity=complexity,
                public_types=public_types,
                implementation_hint=implementation_hint,
                integration_risk=integration_risk,
                dependency_check=dependency_check,
                header_line=text.count("\n", 0, match.start()) + 1,
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

    contract_region = body.split(marker, maxsplit=1)[0]
    # The contract proper ends at the first non-core field. The generator
    # renders Implementation hint, Public types, Integration risk, and
    # Dependency check as their own sections; including them in the embedded
    # contract block would double-render them.
    end_markers = (
        "**Implementation hint:**",
        "**Public types introduced:**",
        "**Integration risk:**",
        "**Dependency check:**",
    )
    cutoff = len(contract_region)
    for marker_text in end_markers:
        index = contract_region.find(marker_text)
        if index != -1 and index < cutoff:
            cutoff = index
    contract = contract_region[:cutoff].strip()
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
            return _strip_inline_backticks(match.group("value").strip())
    return ""


def _strip_inline_backticks(value: str) -> str:
    """Remove a single matching pair of surrounding backticks if present."""

    if len(value) >= 2 and value.startswith("`") and value.endswith("`"):
        return value[1:-1]
    return value


def extract_optional_field(body: str, field_name: str) -> str:
    """Return the field value or empty string if missing (no error)."""

    return extract_field(body, field_name)


def parse_depends_on(value: str) -> tuple[str, ...]:
    if value.lower() in {"", "none"}:
        return ()
    # Order-preserving dedupe: explanatory parentheticals in a Depends line may
    # repeat a task id already listed; a dependency is a set membership, and
    # duplicated blockers confuse frontier displays downstream.
    return tuple(
        dict.fromkeys(match.group("task_id") for match in TASK_ID_RE.finditer(value))
    )


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


def extract_bullet_block(body: str, field_name: str) -> tuple[str, ...]:
    """Return the bullet items under a `**field_name:**` heading.

    Returns an empty tuple when the field is missing.
    """

    pattern = re.compile(
        r"\*\*" + re.escape(field_name) + r":\*\*\n(?P<items>.*?)(?=\n\*\*|\Z)",
        flags=re.DOTALL,
    )
    match = pattern.search(body)
    if match is None:
        return ()

    items: list[str] = []
    for line in match.group("items").splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip().strip("`"))
    return tuple(items)


def extract_block_section(body: str, field_name: str) -> str | None:
    """Return the freeform block under a `**field_name:**` heading, or None."""

    pattern = re.compile(
        r"\*\*" + re.escape(field_name) + r":\*\*\n(?P<block>.*?)(?=\n\*\*|\Z)",
        flags=re.DOTALL,
    )
    match = pattern.search(body)
    if match is None:
        return None
    block = match.group("block").rstrip()
    return block if block else None


def normalize_scope_item(item: str) -> str:
    normalized = item.strip().strip("`")
    if "; " in normalized:
        normalized = normalized.split("; ", maxsplit=1)[0].strip()
    return normalized


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))
