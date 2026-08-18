"""The Task 19.27 tier-structure meta-test (triage §7 item 19, tiering half).

The suite is two tiers: a bare ``uv run pytest`` (the default gate,
``scripts/check.sh``) runs everything not marked ``campaign``; the campaign
tier is opt-in (``-m campaign``) with a standing automated home in
``.github/workflows/ci.yml``'s weekly scheduled job. This module pins the
structure so it cannot rot silently:

* the three Task-19.27 markers are REGISTERED and the default ``-m`` filter
  plus ``--strict-markers`` are in ``addopts`` — a deregistration would
  silently return every campaign family to the default gate;
* the ALWAYS-ON families the contract names (champion acceptance, ES,
  determinism, artifact-digest, train/serve parity, the leak property sweep,
  the prompt byte-golden, the prompt-regression close gate — the tier map's
  un-marked list, training/README.md §2) carry NO campaign mark;
* the campaign families the tier map's FREEZE column drives behind the
  marker ARE marked, module-level, in every file.

The checks read file bytes rather than importing the test modules — importing
a test module as a library is exactly the pattern Task 19.27 removed.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Final

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]

#: The contract's always-on families, each mapped to the file(s) that carry it.
#: (``tests/agents/test_learned_policy.py`` carries BOTH the artifact-digest
#: pins and the Q4 train/serve bit-exact parity gate.)
_ALWAYS_ON_FAMILIES: Final[dict[str, tuple[str, ...]]] = {
    "champion acceptance": ("tests/training/test_learned_factory_acceptance.py",),
    "ES": ("tests/training/test_es.py",),
    "determinism": ("tests/training/test_determinism.py", "eval/determinism_test.py"),
    "artifact-digest": ("tests/agents/test_learned_policy.py",),
    "train/serve parity": ("tests/agents/test_learned_policy.py",),
    "leak property sweep": ("tests/observation/test_leak_property.py",),
    "prompt byte-golden": ("tests/meetings/test_prompt_byte_golden.py",),
    "prompt-regression close gate": ("tests/eval/test_prompt_regression.py",),
}

#: The FREEZE-column families behind the campaign marker (training/README.md
#: §2: coevo/campaign machinery incl. scenarios + anchor study, the crew
#: stack, the composed runner, the fidelity harnesses).
_CAMPAIGN_FILES: Final[tuple[str, ...]] = (
    "tests/training/test_anchor_study.py",
    "tests/training/test_coevo_driver.py",
    "tests/training/test_coevo_rollout.py",
    "tests/training/test_composed_runner.py",
    "tests/training/test_crew_options.py",
    "tests/training/test_crew_owned_tasks.py",
    "tests/training/test_crew_scorer.py",
    "tests/training/test_hall_of_fame.py",
    "tests/training/test_scenarios.py",
    "tests/training/test_surrogate_fidelity.py",
)

_MODULE_MARK_RE: Final[re.Pattern[str]] = re.compile(
    r"^pytestmark = pytest\.mark\.campaign$", re.MULTILINE
)


def _pytest_ini_options() -> dict[str, object]:
    pyproject = tomllib.loads(
        (_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    options: dict[str, object] = pyproject["tool"]["pytest"]["ini_options"]
    return options


def test_the_three_markers_are_registered_and_campaign_is_the_default_filter() -> None:
    options = _pytest_ini_options()

    markers = options["markers"]
    assert isinstance(markers, list)
    registered = {str(marker).split(":", 1)[0].strip() for marker in markers}
    assert {"campaign", "slow", "perf"} <= registered

    addopts = options["addopts"]
    assert isinstance(addopts, str)
    # The default tier IS the default invocation: campaign is opt-in, and an
    # unregistered (typo'd) marker is a collection error, not a silent no-op.
    assert "-m 'not campaign'" in addopts
    assert "--strict-markers" in addopts


def test_the_contract_always_on_families_carry_no_campaign_mark() -> None:
    for family, files in _ALWAYS_ON_FAMILIES.items():
        for relative in files:
            path = _REPO_ROOT / relative
            assert path.is_file(), f"{family}: missing always-on file {relative}"
            text = path.read_text(encoding="utf-8")
            assert "pytest.mark.campaign" not in text, (
                f"{family}: {relative} is contract-pinned ALWAYS-ON "
                "(triage §7 item 19) and may not move behind the campaign marker"
            )


def test_every_freeze_family_file_is_campaign_marked_module_level() -> None:
    for relative in _CAMPAIGN_FILES:
        path = _REPO_ROOT / relative
        assert path.is_file(), f"missing campaign-tier file {relative}"
        text = path.read_text(encoding="utf-8")
        assert _MODULE_MARK_RE.search(text), (
            f"{relative} is a tier-map FREEZE family and must carry the "
            "module-level `pytestmark = pytest.mark.campaign`"
        )


def test_this_meta_test_runs_in_the_default_tier() -> None:
    # Self-check: the pin that guards the tiers must itself be always-on.
    text = Path(__file__).read_text(encoding="utf-8")
    assert not _MODULE_MARK_RE.search(text)


#: The five modules that imported ``tests.meetings.test_manager`` as a library
#: before Task 19.27 extracted the shared harness into the non-test
#: ``tests/meetings/_manager_helpers.py`` — plus ``test_manager.py`` itself.
_NO_CROSS_TEST_IMPORT_FILES: Final[tuple[str, ...]] = (
    "tests/meetings/test_ballot_observation_citation.py",
    "tests/meetings/test_citation_gate.py",
    "tests/meetings/test_elicitation_fixtures.py",
    "tests/meetings/test_manager.py",
    "tests/meetings/test_vote_guard_rationale.py",
    "tests/meetings/test_vouch_grounding.py",
)

_CROSS_TEST_IMPORT_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:from|import)\s+tests\.[\w.]*\btest_\w+", re.MULTILINE
)


def test_the_extracted_meeting_modules_import_no_test_module() -> None:
    """The Task 19.27 extraction's grep-pin, kept by automation.

    Importing a test module as a library re-imports (and re-couples) a whole
    suite to reach its helpers; the shared harness lives in
    ``tests/meetings/_manager_helpers.py`` now, and these six modules may
    never grow a ``tests.*.test_*`` import back. (The repo's five OTHER
    cross-test imports — test_absence_prior / test_episodic_ids /
    test_beliefs_hard_evidence_gate → test_prompt_byte_golden,
    test_real_provider → test_client, test_leak_property →
    test_tick_properties — are outside this task's cut line and recorded in
    the Task 19.27 PR, so this pin deliberately covers only the six.)
    """

    for relative in _NO_CROSS_TEST_IMPORT_FILES:
        path = _REPO_ROOT / relative
        assert path.is_file(), f"missing extracted module {relative}"
        text = path.read_text(encoding="utf-8")
        match = _CROSS_TEST_IMPORT_RE.search(text)
        assert match is None, (
            f"{relative} imports a test module again ({match.group(0)!r}); "
            "shared helpers belong in tests/meetings/_manager_helpers.py"
        )
