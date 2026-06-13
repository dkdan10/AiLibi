"""Tests for the dispatch-frontier helper's merge detection.

Regression coverage for the parent/sub-task id collision: a parent task id
(``10.9``) must NOT be marked merged by a sub-task's PR title (``task 10.9.1:
...``). A plain ``\\b`` boundary sits at the ``9`` -> ``.`` transition and
matched the child title, silently marking the parent merged the moment the
first child landed (surfaced when 10.9.1 / 10.9.2 split off 10.9).
"""

from __future__ import annotations

from compute_next_task import is_task_merged
from _task_parser import TaskDoc


def _task(task_id: str, branch: str = "unused-branch") -> TaskDoc:
    # Only task_id and branch are consulted by is_task_merged; the rest are
    # structural filler so the frozen dataclass constructs.
    return TaskDoc(
        phase_path=__import__("pathlib").Path("tasks/phase-10.md"),
        task_id=task_id,
        title="t",
        body="",
        contract="",
        prompt_path=__import__("pathlib").Path("agent_prompts/x.md"),
        branch=branch,
        depends_on=(),
        section_refs="",
        files_in_scope=(),
        complexity=None,
        public_types=(),
        implementation_hint=None,
        integration_risk=None,
        dependency_check=(),
    )


def test_parent_id_not_marked_merged_by_subtask_title() -> None:
    titles = [
        "task 10.9.1: vote-ballot fail-soft",
        "task 10.9.2: ballot-target graph guard",
    ]
    assert is_task_merged(_task("10.9"), set(), titles) is False
    assert is_task_merged(_task("10.9.1"), set(), titles) is True
    assert is_task_merged(_task("10.9.2"), set(), titles) is True


def test_parent_id_marked_merged_by_its_own_title() -> None:
    titles = ["task 10.9: wave-1 combined re-record and gate"]
    assert is_task_merged(_task("10.9"), set(), titles) is True


def test_sibling_numeric_ids_do_not_cross_match() -> None:
    # 10.9 must not match a "task 10.91" title (no such id today, but the
    # bare-digit continuation is the other half of the boundary fix).
    titles = ["task 10.91: hypothetical"]
    assert is_task_merged(_task("10.9"), set(), titles) is False


def test_branch_match_still_wins() -> None:
    assert (
        is_task_merged(_task("10.9", branch="phase-10-x"), {"phase-10-x"}, []) is True
    )
