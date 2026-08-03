"""Guards for the task-doc control surface added at the Phase-19 planning PR.

Three behaviors are pinned here because they gate every generated prompt and
every frontier computation: (1) the scope-gated DESIGN.md /
AGENT_IMPLEMENTATION.md constraint rules — a task listing the file in scope is
exempt, every other task keeps the line byte-identically; (2) the dependency
parser's order-preserving dedupe (explanatory parentheticals must not produce
duplicated blockers); (3) the validator's unknown-dependency and cycle
detection.
"""

from __future__ import annotations

from pathlib import Path

import _task_parser
import generate_prompts
import validate_task_docs


def _task(
    task_id: str,
    *,
    files_in_scope: tuple[str, ...] = (),
    depends_on: tuple[str, ...] = (),
) -> _task_parser.TaskDoc:
    return _task_parser.TaskDoc(
        phase_path=_task_parser.ROOT / "tasks" / "phase-99.md",
        task_id=task_id,
        title="fixture",
        body="",
        contract="",
        prompt_path=Path(f"agent_prompts/task-{task_id.replace('.', '-')}.md"),
        branch=f"phase-99-{task_id}",
        depends_on=depends_on,
        section_refs="",
        files_in_scope=files_in_scope,
        complexity="Small",
        public_types=(),
        implementation_hint=None,
        integration_risk=None,
        dependency_check=(),
    )


class TestScopeGatedConstraints:
    def test_design_md_bar_present_when_not_in_scope(self) -> None:
        rules = generate_prompts._constraints_for(_task("99.1"))
        assert "Do not modify DESIGN.md." in rules
        assert "Do not modify AGENT_IMPLEMENTATION.md." in rules

    def test_design_md_bar_dropped_when_listed_in_scope(self) -> None:
        rules = generate_prompts._constraints_for(
            _task("99.1", files_in_scope=("DESIGN.md", "README.md"))
        )
        assert "Do not modify DESIGN.md." not in rules
        assert "Do not modify AGENT_IMPLEMENTATION.md." in rules

    def test_agent_implementation_bar_dropped_when_listed_in_scope(self) -> None:
        rules = generate_prompts._constraints_for(
            _task("99.1", files_in_scope=("AGENT_IMPLEMENTATION.md",))
        )
        assert "Do not modify AGENT_IMPLEMENTATION.md." not in rules
        assert "Do not modify DESIGN.md." in rules


class TestDependsOnParsing:
    def test_prose_repeats_do_not_duplicate_blockers(self) -> None:
        parsed = _task_parser.parse_depends_on(
            "19.5, 19.9 (the 19.5 edge is the shared DTO surface)"
        )
        assert parsed == ("19.5", "19.9")

    def test_order_is_preserved(self) -> None:
        assert _task_parser.parse_depends_on("19.9, 19.5") == ("19.9", "19.5")


class TestDependencyGraphValidation:
    def test_unknown_dependency_is_an_error(self) -> None:
        errors: list[str] = []
        validate_task_docs.validate_dependency_graph(
            [_task("99.1", depends_on=("99.7",))], errors
        )
        assert any("unknown task 99.7" in error for error in errors)

    def test_cycle_is_an_error(self) -> None:
        errors: list[str] = []
        validate_task_docs.validate_dependency_graph(
            [
                _task("99.1", depends_on=("99.2",)),
                _task("99.2", depends_on=("99.1",)),
            ],
            errors,
        )
        assert any("Dependency cycle" in error for error in errors)

    def test_clean_graph_produces_no_errors(self) -> None:
        errors: list[str] = []
        validate_task_docs.validate_dependency_graph(
            [
                _task("99.1"),
                _task("99.2", depends_on=("99.1",)),
            ],
            errors,
        )
        assert errors == []
