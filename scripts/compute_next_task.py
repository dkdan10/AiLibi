#!/usr/bin/env python3
"""Compute the dispatchable task frontier from the phase task graph.

A task is **dispatchable** when it is not yet merged and every task it
``Depends on`` is merged. "Merged" is read from merged PRs via ``gh``: a task
``N.M`` counts as merged when a merged PR's **title** starts with ``task N.M``
(the project's PR convention, e.g. ``task 8.1: per-player task re-key``) or, as a
fallback, when its ``**Branch:**`` matches a merged PR's head branch. The title is
the robust signal — Claude Code web sessions often merge from an auto-generated
branch (``claude/…``) rather than the contract's branch name.

This reuses ``scripts/_task_parser.py`` — the exact parser
``scripts/validate_task_docs.py`` and ``scripts/generate_prompts.py`` use — so the
dependency graph comes from a single source of truth (the ``tasks/phase-*.md``
contracts), never a second hand-maintained list.

Usage::

    python scripts/compute_next_task.py [--phase N] [--json]

``--phase N`` restricts the reported frontier to one phase (recommended — older
phases' PRs age out of the query window). ``--json`` emits
``{"dispatchable": [...], "blocked": [...], "merged": [...]}`` for an orchestrator
(each dispatchable entry carries ``task_id`` / ``branch`` / ``prompt`` /
``complexity`` so a dispatcher can paste the prompt and apply a risk-tiered
auto-merge policy off ``complexity``). Default output is human-readable.

If the ``gh`` CLI is unavailable or unauthenticated, the merged set is treated as
empty and a warning is printed — so the command still previews the graph offline
(roots show as dispatchable); in CI / an orchestrator, ``gh`` is present and the
frontier is accurate.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

from _task_parser import TaskDoc, parse_all_tasks, relative

_MERGED_PR_LIMIT = 500


def merged_pr_index() -> tuple[set[str], list[str]]:
    """``(head branches, titles)`` of merged PRs via ``gh`` (empty + warn on failure)."""

    try:
        result = subprocess.run(
            [
                "gh",
                "pr",
                "list",
                "--state",
                "merged",
                "--limit",
                str(_MERGED_PR_LIMIT),
                "--json",
                "headRefName,title",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        detail = getattr(exc, "stderr", "") or str(exc)
        print(
            f"warning: `gh pr list` unavailable ({detail.strip()}); treating the "
            "merged set as empty (offline preview — roots will show dispatchable).",
            file=sys.stderr,
        )
        return set(), []
    rows = json.loads(result.stdout or "[]")
    return {row["headRefName"] for row in rows}, [row["title"] for row in rows]


def is_task_merged(task: TaskDoc, branches: set[str], titles: list[str]) -> bool:
    """A task is merged if a merged PR title starts ``task N.M`` or its branch matches."""

    if task.branch in branches:
        return True
    # The negative lookahead keeps a PARENT id (10.9) from matching a SUB-task's
    # title (``task 10.9.1: ...``): a plain ``\b`` sits at the 9->. boundary and
    # would mark 10.9 merged the moment 10.9.1 lands. Reject a following ``.digit``
    # (longer id) or bare digit (10.9 vs 10.91).
    pattern = re.compile(
        rf"^\s*task\s+{re.escape(task.task_id)}(?!\.?\d)", re.IGNORECASE
    )
    return any(pattern.search(title) for title in titles)


def compute_frontier(
    tasks: list[TaskDoc],
    branches: set[str],
    titles: list[str],
    phase: int | None,
) -> tuple[list[TaskDoc], list[tuple[TaskDoc, list[str]]], set[str]]:
    """Split the candidate tasks into (dispatchable, blocked, merged_ids).

    ``merged_ids`` is computed over ALL tasks so a cross-phase dependency resolves
    correctly; only the reported candidates are restricted to ``phase`` when given.
    """

    by_id = {task.task_id: task for task in tasks}
    merged_ids = {
        task.task_id for task in tasks if is_task_merged(task, branches, titles)
    }

    candidates = tasks
    if phase is not None:
        prefix = f"{phase}."
        candidates = [task for task in tasks if task.task_id.startswith(prefix)]

    dispatchable: list[TaskDoc] = []
    blocked: list[tuple[TaskDoc, list[str]]] = []
    for task in candidates:
        if task.task_id in merged_ids:
            continue
        unmet = [
            dep for dep in task.depends_on if dep in by_id and dep not in merged_ids
        ]
        if unmet:
            blocked.append((task, unmet))
        else:
            dispatchable.append(task)

    return dispatchable, blocked, merged_ids & {task.task_id for task in candidates}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase", type=int, help="Restrict the reported frontier to phase N (e.g. 8)."
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit JSON for an orchestrator."
    )
    args = parser.parse_args()

    errors: list[str] = []
    tasks = parse_all_tasks(errors)
    if errors:
        print("task-doc parse errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    branches, titles = merged_pr_index()
    dispatchable, blocked, merged_ids = compute_frontier(
        tasks, branches, titles, args.phase
    )

    if args.json:
        print(
            json.dumps(
                {
                    "dispatchable": [
                        {
                            "task_id": task.task_id,
                            "branch": task.branch,
                            "prompt": relative(task.prompt_path),
                            "complexity": task.complexity,
                        }
                        for task in dispatchable
                    ],
                    "blocked": [
                        {"task_id": task.task_id, "waiting_on": unmet}
                        for task, unmet in blocked
                    ],
                    "merged": sorted(merged_ids),
                },
                indent=2,
            )
        )
        return 0

    scope = f"phase {args.phase}" if args.phase is not None else "all phases"
    print(f"Task frontier ({scope}) — merged: {len(merged_ids)}")
    print(f"\ndispatchable now ({len(dispatchable)}):")
    for task in dispatchable or ():
        print(f"  {task.task_id}  [{task.complexity}]  {relative(task.prompt_path)}")
    if not dispatchable:
        print("  (none)")
    print(f"\nblocked ({len(blocked)}):")
    for task, unmet in blocked or ():
        print(f"  {task.task_id}  waiting on {', '.join(unmet)}")
    if not blocked:
        print("  (none)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
