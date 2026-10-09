"""The tier-structure meta-test (Task 19.27's tiering, re-derived on 2026-10-09).

The suite is two tiers: a bare ``uv run pytest`` (the default gate,
``scripts/check.sh``) runs everything not marked ``campaign``; the campaign
tier is opt-in (``-m campaign``) with a standing automated home in
``.github/workflows/campaign-tier.yml``: weekly, and on every pull request that
changes ``tests/training/**``. The tier map in training/README.md section 2
states the yardstick: a family is always-on when what its assertions judge is
determinism, byte identity, the observation firewall or provenance, and campaign
when it reads role or outcome on a frozen record. This module pins the structure
so it cannot rot silently:

* the three markers are REGISTERED and the default ``-m`` filter plus
  ``--strict-markers`` are in ``addopts`` — a deregistration would silently
  return every campaign family to the default gate;
* each ALWAYS-ON family names what it judges, one of the four always-on
  grounds, and carries NO campaign mark;
* every campaign mark sits under ``tests/training/``;
* the campaign families — the tier map's FREEZE column and the ML value pins
  that read role or outcome on a frozen record — ARE marked, module-level, in
  every file;
* the MIXED-tier files keep their split: each named campaign test carries a
  function-level mark and each named always-on test carries none, with no
  module-level mark on the file;
* the campaign workflow keeps its weekly schedule and its dispatch, and runs on
  every pull request that changes ``tests/training/**``.

The checks read file bytes rather than importing the test modules — importing
a test module as a library is exactly the pattern Task 19.27 removed.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any, Final, NamedTuple

import yaml

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]

#: The four grounds that make a family always-on: what its assertions judge.
_ALWAYS_ON_GROUNDS: Final[frozenset[str]] = frozenset(
    {"determinism", "byte identity", "firewall", "provenance"}
)


class _Family(NamedTuple):
    """An always-on family: what its assertions judge and the files carrying it."""

    judges: str
    files: tuple[str, ...]


#: The always-on families, re-derived once from the direction's yardstick on
#: 2026-10-09 (training/README.md section 2). Each judges determinism, byte
#: identity, the firewall or provenance; none reads role or outcome on a frozen
#: record. (``tests/agents/test_learned_policy.py`` carries BOTH the
#: artifact-digest pins and the train/serve bit-exact parity gate.)
_ALWAYS_ON_FAMILIES: Final[dict[str, _Family]] = {
    "champion acceptance": _Family(
        "provenance", ("tests/training/test_learned_factory_acceptance.py",)
    ),
    "ES": _Family("determinism", ("tests/training/test_es.py",)),
    "determinism": _Family(
        "determinism",
        ("tests/training/test_determinism.py", "eval/determinism_test.py"),
    ),
    "artifact-digest": _Family(
        "byte identity", ("tests/agents/test_learned_policy.py",)
    ),
    "train/serve parity": _Family(
        "determinism", ("tests/agents/test_learned_policy.py",)
    ),
    "leak property sweep": _Family(
        "firewall", ("tests/observation/test_leak_property.py",)
    ),
    "prompt byte-golden": _Family(
        "byte identity", ("tests/meetings/test_prompt_byte_golden.py",)
    ),
}

#: The whole files behind the campaign marker (training/README.md §2): the
#: FREEZE-column families (coevo/campaign machinery incl. scenarios + anchor
#: study, the crew stack, the composed runner, the fidelity harnesses) and the
#: two ML value-pin files that read role or outcome on frozen records (the
#: Goodhart probe and the committed objective's reward pins).
_CAMPAIGN_FILES: Final[tuple[str, ...]] = (
    "tests/training/test_anchor_study.py",
    "tests/training/test_coevo_driver.py",
    "tests/training/test_coevo_rollout.py",
    "tests/training/test_composed_runner.py",
    "tests/training/test_crew_options.py",
    "tests/training/test_crew_owned_tasks.py",
    "tests/training/test_crew_scorer.py",
    "tests/training/test_goodhart_probe.py",
    "tests/training/test_hall_of_fame.py",
    "tests/training/test_rewards.py",
    "tests/training/test_scenarios.py",
    "tests/training/test_surrogate_fidelity.py",
)

_MODULE_MARK_RE: Final[re.Pattern[str]] = re.compile(
    r"^pytestmark = pytest\.mark\.campaign$", re.MULTILINE
)


class _MixedFile(NamedTuple):
    """A mixed-tier file: its campaign tests and its always-on tests, by name."""

    campaign: tuple[str, ...]
    always_on: tuple[str, ...]


#: The MIXED-tier files. Each carries no module-level mark; its named campaign
#: tests carry a FUNCTION-level mark and its named always-on tests none.
#:
#: * ``training/conviction/fidelity.py`` is a FREEZE row of the tier map ("The
#:   fidelity harnesses") with no dedicated test file: its harness-mechanics
#:   tests live inside the KEEP-row conviction-model module, whose
#:   committed-evidence pins (census, artifact round-trip, and the GO-verdict
#:   reproduction the KEEP row itself cites) keep executing on every default
#:   gate run.
#: * The finalist-eval pins and the bake-off harness keep their prefix digest,
#:   row order, stamp conventions, firewall scans, determinism demotion,
#:   digests, round trips, seed-set derivation and objective fence in the
#:   default gate; their value pins (win and loss counts and rates, per-arm
#:   referee verdicts, baseline ids, floors and committed result rows) read
#:   outcome on frozen records and run in the campaign tier.
_MIXED_TIER_FILES: Final[dict[str, _MixedFile]] = {
    "tests/training/test_conviction_model.py": _MixedFile(
        campaign=(
            "test_walk_gate_refuses_raw_mismatches",
            "test_fidelity_requires_a_committed_split",
            "test_fit_corpus_entry_requires_a_committed_split",
            "test_fidelity_rejects_a_leaky_or_partial_split",
            "test_spearman_is_tie_aware_and_fails_loud_on_degenerate_input",
            "test_verdict_consequence_mapping_is_pre_committed",
        ),
        always_on=(
            "test_corpus_census_pins",
            # Both renamed twice: at the baseline-7 record, when the corpus moved
            # under a frozen fit and each pin stated the gap instead of a
            # reproduction; and again at the Task-21.17 re-ground, which closed
            # the gap and restored the strong equality. The verdict pin was
            # renamed once more at the baseline-9 re-ground. Same KEEP-row duty,
            # same default tier throughout.
            "test_committed_artifact_round_trips_and_the_refit_no_longer_matches",
            "test_the_committed_verdict_is_the_baseline9_first_evaluation",
        ),
    ),
    "tests/training/test_finalist_eval_pins.py": _MixedFile(
        campaign=(
            "test_every_phase_18_row_records_the_same_substrate_and_roster",
            "test_the_f13_arm_is_the_49_seed_arm_and_declares_the_missing_seed",
            "test_the_comparator_is_the_slates_only_referee_pass",
            "test_every_arms_floors_are_the_baseline_6_pins_re_derived",
            "test_the_c1_rider_intersection_is_the_persisted_same_seed_deciding_cell",
            "test_the_leg_duration_blocks_price_the_campaign_honestly",
            "test_the_registered_nested_cells_block_is_persisted_on_every_arm",
            "test_the_comparator_carries_the_49_seed_cut_for_the_f13_axis",
            "test_the_f13_intersection_gauges_carry_their_own_split_half_read",
            "test_the_c1_paired_crew_win_table_is_the_49_seed_discordant_cut",
            "test_the_co_present_departure_cell_is_persisted_on_every_arm",
            "test_each_rows_validity_gate_reports_its_own_failures_by_name",
            "test_the_c2_diagnostics_report_the_stall_and_the_dead_meeting_economy",
            "test_the_headline_cells_match_the_committed_rows",
            "test_the_witnessed_event_rate_split_half_is_unresolvable_on_every_arm",
        ),
        always_on=(
            "test_the_two_17_14_rows_stay_first_and_unchanged",
            "test_every_slate_arm_appears_exactly_once_in_the_pre_registered_order",
            "test_impostor_rows_name_the_artifact_they_loaded_on_every_game",
            "test_the_comparator_row_proves_the_opponent_slot_was_empty",
            "test_crew_rows_keep_the_subject_and_the_opponent_in_distinct_slots",
            "test_crew_rows_do_not_follow_the_realpath_v3_stamp_convention",
            "test_every_committed_digest_closes_on_the_artifact_bytes_on_disk",
            "test_the_seed_mod5_splits_partition_each_arms_own_games",
            "test_the_comparator_intersection_carries_its_own_mod5_splits",
            "test_the_f13_intersection_gauges_put_the_quartet_on_one_seed_set",
            "test_the_stalemate_key_is_present_only_where_it_is_meaningful",
        ),
    ),
    "tests/training/test_bakeoff_harness.py": _MixedFile(
        campaign=(
            "test_selection_bar_and_the_three_probe_defaults_pin_one_baseline",
            "test_rerun_rows_pin_the_baseline_5_protocol",
            "test_rerun_rows_carry_the_baseline_5_supply_floors",
        ),
        always_on=(
            "test_eval_seeds_are_the_frozen_corpus_test_split",
            "test_entrant_modules_do_not_import_eval",
            "test_entrant_modules_do_not_import_conviction",
            "test_evaluate_candidate_experiment_tier",
            "test_artifact_round_trip",
            "test_rerun_rows_are_the_four_canonical_entrants",
            "test_rerun_rows_match_the_committed_artifact_digests",
            "test_rerun_artifacts_carry_the_15_9_provenance_stamp",
            "test_no_committed_results_row_claims_this_objective",
            "test_v3_golden_vector_pins_values",
            "test_v3_encode_is_deterministic_on_repeat",
        ),
    ),
}

#: The campaign workflow, its weekly schedule and the per-change trigger.
_CAMPAIGN_WORKFLOW: Final[str] = ".github/workflows/campaign-tier.yml"
_CAMPAIGN_CRON: Final[str] = "17 6 * * 1"
_CAMPAIGN_PATHS: Final[tuple[str, ...]] = ("tests/training/**",)


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


def test_each_always_on_family_judges_an_always_on_ground_and_is_unmarked() -> None:
    for family, (judges, files) in _ALWAYS_ON_FAMILIES.items():
        assert judges in _ALWAYS_ON_GROUNDS, (
            f"{family}: judges {judges!r}, which is no always-on ground "
            f"({sorted(_ALWAYS_ON_GROUNDS)}); a family that reads role or outcome "
            "on a frozen record belongs to the campaign tier"
        )
        for relative in files:
            path = _REPO_ROOT / relative
            assert path.is_file(), f"{family}: missing always-on file {relative}"
            text = path.read_text(encoding="utf-8")
            assert "pytest.mark.campaign" not in text, (
                f"{family}: {relative} judges {judges}, an always-on ground "
                "(training/README.md section 2), and may not move behind the "
                "campaign marker"
            )


def test_every_campaign_mark_sits_under_tests_training() -> None:
    training = _REPO_ROOT / "tests" / "training"
    outside = sorted(
        path.relative_to(_REPO_ROOT).as_posix()
        for path in (_REPO_ROOT / "tests").rglob("*.py")
        if not path.is_relative_to(training)
        and "pytest.mark.campaign" in path.read_text(encoding="utf-8")
    )
    assert outside == [], (
        f"campaign marks outside tests/training/: {outside} — the campaign tier "
        "is the ML campaign machinery and the ML value pins, all under "
        "tests/training/ (training/README.md section 2)"
    )


def test_the_mixed_files_keep_their_split() -> None:
    """Each mixed file's per-test split (first pinned in the Codex review on PR #349).

    A module-level mark on a mixed file would silently drag its always-on pins
    out of the default gate, an unmarked campaign test would silently return a
    role- or outcome-reading pin (or frozen machinery) to every per-change run,
    and a marked always-on test would hide a determinism, firewall, digest or
    provenance pin.
    """

    for relative, (campaign, always_on) in _MIXED_TIER_FILES.items():
        path = _REPO_ROOT / relative
        assert path.is_file(), f"missing mixed-tier file {relative}"
        text = path.read_text(encoding="utf-8")
        assert not _MODULE_MARK_RE.search(text), (
            f"{relative} is a MIXED-tier file and may not carry a module-level "
            "campaign mark — that would hide its always-on pins"
        )
        for name in campaign:
            assert re.search(
                rf"^@pytest\.mark\.campaign\ndef {name}\(", text, re.MULTILINE
            ), (
                f"{relative}::{name} reads role or outcome on a frozen record (or "
                "exercises frozen machinery) and must carry a function-level "
                "campaign mark"
            )
        for name in always_on:
            assert re.search(rf"^def {name}\(", text, re.MULTILINE), (
                f"{relative}::{name} (an always-on pin) is missing"
            )
            assert not re.search(
                rf"^@pytest\.mark\.campaign\ndef {name}\(", text, re.MULTILINE
            ), (
                f"{relative}::{name} is an always-on pin and must stay in the default gate"
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


def _workflow() -> dict[Any, Any]:
    data = yaml.safe_load((_REPO_ROOT / _CAMPAIGN_WORKFLOW).read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_the_campaign_workflow_runs_weekly_and_on_every_training_test_change() -> None:
    """The campaign tier's automated home: the schedule, the dispatch, the paths.

    YAML 1.1 reads the bare key ``on`` as the boolean ``True``, so the trigger
    block is looked up under either spelling.
    """

    workflow = _workflow()
    triggers = workflow.get("on", workflow.get(True))
    assert isinstance(triggers, dict), f"{_CAMPAIGN_WORKFLOW} has no trigger block"
    assert triggers.get("schedule") == [{"cron": _CAMPAIGN_CRON}], (
        f"{_CAMPAIGN_WORKFLOW}: the weekly schedule must stay {_CAMPAIGN_CRON!r}"
    )
    assert "workflow_dispatch" in triggers
    pull_request = triggers.get("pull_request")
    assert isinstance(pull_request, dict), (
        f"{_CAMPAIGN_WORKFLOW} must run on pull requests that change "
        f"{list(_CAMPAIGN_PATHS)}"
    )
    assert tuple(pull_request.get("paths", ())) == _CAMPAIGN_PATHS
    (job,) = workflow["jobs"].values()
    assert "weekly" not in job["name"].lower()
    assert "-m campaign" in " ".join(str(step.get("run", "")) for step in job["steps"])


def test_this_meta_test_runs_in_the_default_tier() -> None:
    # Self-check: the pin that guards the tiers must itself be always-on.
    text = Path(__file__).read_text(encoding="utf-8")
    assert not _MODULE_MARK_RE.search(text)


#: The modules that imported ``tests.meetings.test_manager`` as a library
#: before Task 19.27 extracted the shared harness into the non-test
#: ``tests/meetings/_manager_helpers.py`` — plus ``test_manager.py`` itself
#: and ``test_grounding_label.py``, which reads the same harness. The
#: citation-gate module left the list with the gate it pinned, retired by
#: ruling D6 of 2026-09-19.
_NO_CROSS_TEST_IMPORT_FILES: Final[tuple[str, ...]] = (
    "tests/meetings/test_ballot_observation_citation.py",
    "tests/meetings/test_elicitation_fixtures.py",
    "tests/meetings/test_grounding_label.py",
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
