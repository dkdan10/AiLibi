"""The freeze's gates: determinism, proof-freedom, the body handle, and the manifest.

Every planted prefix here is built on seed 1 -- the seed the seven committed
development cases already use, and therefore development data by construction.
None of these tests reads a prefix drawn from the preregistered held-out band;
the only band prefixes they touch are the digests they compare against the
committed manifest.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import get_args

import pytest
from pydantic import TypeAdapter, ValidationError

from engine.world import load_canonical_map
from experiments.deduction_scenarios import ScenarioDefinition
from experiments.held_out_prefixes import (
    AUTHORIZED_ROSTER,
    MANIFEST_PATH,
    MAX_TICKS,
    PREREGISTERED_BAND,
    TALLY_ACCEPTED_KEY,
    TALLY_SEEDS_KEY,
    TEMPORAL_OBSERVATION_VERSION,
    HeldOutPrefix,
    HeldOutPrefixError,
    PrefixRoster,
    PrefixStep,
    RejectionReason,
    SeedBand,
    _FILTER_ENV,
    _replay_prefix,
    assert_no_legacy_body_handles,
    build_manifest,
    build_prefix,
    canonical_prefix_json,
    development_definition_digests,
    evaluate_prefix,
    generate,
    legacy_body_handles,
    prefix_sha256,
    prefix_surface_texts,
    tally_reasons,
)
from observation.action_intent import ActionIntent
from orchestrator.game import _build_meeting_trigger

REPO_ROOT = Path(__file__).resolve().parents[2]
_INTENTS: TypeAdapter[ActionIntent] = TypeAdapter(ActionIntent)

#: Seeds used for debugging and planted cases. All OUTSIDE the preregistered
#: band, so inspecting them converts nothing.
_PLANT_SEED = 1
_DEBUG_SEEDS = (9001, 9002)

#: The two total rows ``tally_reasons`` reports before its reason histogram.
_TALLY_TOTALS = (TALLY_SEEDS_KEY, TALLY_ACCEPTED_KEY)


def _step(tick: int, actor: str, kind: str, payload: dict[str, object]) -> PrefixStep:
    return PrefixStep(
        tick=tick,
        action=_INTENTS.validate_python(
            {"actor": actor, "type": kind, "payload": payload}
        ),
    )


def _planted(
    *, steps: tuple[PrefixStep, ...], kill_tick: int, report_tick: int
) -> HeldOutPrefix:
    """A hand-authored seed-1 prefix, used only to prove a gate fires."""

    return HeldOutPrefix(
        seed=_PLANT_SEED,
        roster=AUTHORIZED_ROSTER,
        max_ticks=MAX_TICKS,
        steps=tuple(sorted(steps, key=lambda step: (step.tick, step.action.actor))),
        report_tick=report_tick,
        kill_tick=kill_tick,
    )


def _walk_to_admin(actor: str) -> tuple[PrefixStep, ...]:
    return (
        _step(0, actor, "move", {"to_room": "UPPER_HALL"}),
        _step(1, actor, "move", {"to_room": "ADMIN"}),
    )


def _walk_to_medbay(actor: str) -> tuple[PrefixStep, ...]:
    return (
        _step(0, actor, "move", {"to_room": "WEST_HALL"}),
        _step(1, actor, "move", {"to_room": "MEDBAY"}),
    )


def _unwitnessed_seed_one_prefix() -> HeldOutPrefix:
    """Seed 1's impostor p-4 kills p-1 alone in ADMIN; p-2 walks in and reports."""

    return _planted(
        steps=(
            *_walk_to_admin("p-1"),
            *_walk_to_admin("p-4"),
            *_walk_to_medbay("p-3"),
            _step(4, "p-4", "kill", {"target": "p-1"}),
            _step(5, "p-4", "move", {"to_room": "EAST_HALL"}),
            _step(5, "p-2", "move", {"to_room": "UPPER_HALL"}),
            _step(6, "p-2", "move", {"to_room": "ADMIN"}),
            _step(7, "p-2", "report", {"body_id": "body-p-1"}),
        ),
        kill_tick=4,
        report_tick=7,
    )


def test_a_duplicate_action_for_one_actor_and_tick_is_refused() -> None:
    """The hashed schedule and the replayed schedule must be the same schedule.

    ``_PrefixAgent`` keys its script by tick, so a second step for the same actor
    and tick would be dropped at replay while ``canonical_prefix_json`` still
    hashed it -- a digest certified for a run that never happened. The model
    refuses the prefix instead.
    """

    valid = _unwitnessed_seed_one_prefix()
    duplicated = (
        *valid.steps,
        _step(4, "p-4", "move", {"to_room": "UPPER_HALL"}),
    )
    with pytest.raises(ValidationError, match="one action per actor per tick"):
        HeldOutPrefix(
            seed=valid.seed,
            roster=valid.roster,
            max_ticks=valid.max_ticks,
            steps=tuple(
                sorted(duplicated, key=lambda step: (step.tick, step.action.actor))
            ),
            report_tick=valid.report_tick,
            kill_tick=valid.kill_tick,
        )
    with pytest.raises(ValidationError, match="one action per actor per tick"):
        HeldOutPrefix.model_validate(
            {
                **valid.model_dump(mode="json"),
                "steps": [step.model_dump(mode="json") for step in duplicated],
            }
        )


def test_the_filter_environment_cannot_be_moved_by_a_same_process_caller() -> None:
    """A writable global would let a caller re-screen the set under other flags."""

    with pytest.raises(TypeError):
        _FILTER_ENV["AILIBI_TEMPORAL_OBSERVATIONS"] = "1"  # type: ignore[index]
    assert dict(_FILTER_ENV) == {
        "AILIBI_LLM_PROVIDER": "fake",
        "AILIBI_TEMPORAL_OBSERVATIONS": str(TEMPORAL_OBSERVATION_VERSION),
    }


def test_the_tally_counts_an_out_of_band_range_without_opening_a_prefix() -> None:
    """The reproducing command behind the card's out-of-band rejection rate."""

    first, last = _DEBUG_SEEDS[0], _DEBUG_SEEDS[-1]
    walked = last - first + 1
    tally = tally_reasons(first, last)
    assert tally["seeds"] == walked
    reasons = {key: count for key, count in tally.items() if key not in _TALLY_TOTALS}
    assert tally["accepted"] + sum(reasons.values()) == walked
    assert set(reasons) <= set(get_args(RejectionReason))


def test_the_tally_refuses_to_probe_the_preregistered_band() -> None:
    """An aggregate count over band seeds is still a read of the held-out set."""

    for first, last in (
        (PREREGISTERED_BAND.first_seed, PREREGISTERED_BAND.first_seed),
        (PREREGISTERED_BAND.first_seed - 1, PREREGISTERED_BAND.first_seed),
        (PREREGISTERED_BAND.last_seed, PREREGISTERED_BAND.last_seed + 1),
        (1, PREREGISTERED_BAND.last_seed + 1000),
    ):
        with pytest.raises(
            HeldOutPrefixError, match="intersect the preregistered band"
        ):
            tally_reasons(first, last)
    with pytest.raises(HeldOutPrefixError, match="must not run backwards"):
        tally_reasons(_DEBUG_SEEDS[1], _DEBUG_SEEDS[0])


def test_the_preregistered_band_is_the_one_the_card_froze() -> None:
    assert (
        PREREGISTERED_BAND.first_seed,
        PREREGISTERED_BAND.last_seed,
        PREREGISTERED_BAND.size,
    ) == (3000, 3999, 50)
    assert AUTHORIZED_ROSTER == PrefixRoster(
        num_players=4, num_impostors=1, tasks_per_crewmate=1
    )
    assert TEMPORAL_OBSERVATION_VERSION == 2


def test_a_seed_always_yields_the_same_prefix() -> None:
    game_map = load_canonical_map()
    digests = set()
    for seed in _DEBUG_SEEDS:
        first = build_prefix(seed=seed, roster=AUTHORIZED_ROSTER, game_map=game_map)
        second = build_prefix(seed=seed, roster=AUTHORIZED_ROSTER, game_map=game_map)
        assert canonical_prefix_json(first) == canonical_prefix_json(second)
        assert prefix_sha256(first) == prefix_sha256(second)
        digests.add(prefix_sha256(first))
    assert len(digests) == len(_DEBUG_SEEDS), "distinct seeds must not collide"


def test_the_prefix_model_pins_neither_seed_nor_roster() -> None:
    """The contrast with ``ScenarioDefinition``, which pins both as literals."""

    prefix = build_prefix(
        seed=_DEBUG_SEEDS[0],
        roster=PrefixRoster(num_players=5, num_impostors=1, tasks_per_crewmate=1),
        game_map=load_canonical_map(),
    )
    assert prefix.seed == _DEBUG_SEEDS[0]
    assert prefix.roster.num_players == 5
    with pytest.raises(ValidationError):
        ScenarioDefinition(
            case="honest",
            seed=2,  # type: ignore[arg-type]
            steps=(),
            claimed_room="ADMIN",
            expected_report_tick=6,
            information_limit="",
        )


def test_an_unwitnessed_planted_prefix_passes_and_keeps_the_killer_record() -> None:
    """The exclusion is visible: the killer holds a kill record and is not counted."""

    evaluation = evaluate_prefix(_unwitnessed_seed_one_prefix())
    assert evaluation.reason is None
    assert evaluation.living_crew_proof_rows == 0
    assert evaluation.killer_own_kill_records == 1
    assert evaluation.trigger_line == "p-2 reported body body-p-1 at tick 7"


def test_a_planted_witnessed_kill_fails_the_filter() -> None:
    """p-2 stands in ADMIN when p-4 kills p-1, so the crew can prove it outright."""

    planted = _planted(
        steps=(
            *_walk_to_admin("p-1"),
            *_walk_to_admin("p-2"),
            *_walk_to_admin("p-4"),
            *_walk_to_medbay("p-3"),
            _step(4, "p-4", "kill", {"target": "p-1"}),
            _step(5, "p-2", "report", {"body_id": "body-p-1"}),
        ),
        kill_tick=4,
        report_tick=5,
    )
    evaluation = evaluate_prefix(planted)
    assert evaluation.reason == "witnessed_kill"
    assert evaluation.living_crew_proof_rows == 1


def test_a_planted_witnessed_vent_fails_the_filter() -> None:
    """The kill is unwitnessed; p-2 then watches p-4 drop into the ADMIN vent."""

    planted = _planted(
        steps=(
            *_walk_to_admin("p-1"),
            *_walk_to_admin("p-4"),
            *_walk_to_medbay("p-3"),
            _step(4, "p-4", "kill", {"target": "p-1"}),
            _step(5, "p-2", "move", {"to_room": "UPPER_HALL"}),
            _step(6, "p-2", "move", {"to_room": "ADMIN"}),
            _step(7, "p-4", "vent", {"vent_id": "ADMIN_VENT"}),
            _step(8, "p-2", "report", {"body_id": "body-p-1"}),
        ),
        kill_tick=4,
        report_tick=8,
    )
    evaluation = evaluate_prefix(planted)
    assert evaluation.reason == "witnessed_vent"
    assert evaluation.living_crew_proof_rows == 1


def test_an_illegal_step_is_refused_rather_than_silently_kept() -> None:
    """A move across two rooms in one tick is not a legal held-out schedule."""

    planted = _planted(
        steps=(
            *_walk_to_admin("p-1"),
            *_walk_to_admin("p-4"),
            *_walk_to_medbay("p-3"),
            _step(2, "p-3", "move", {"to_room": "REACTOR"}),
            _step(4, "p-4", "kill", {"target": "p-1"}),
            _step(5, "p-4", "move", {"to_room": "EAST_HALL"}),
            _step(5, "p-2", "move", {"to_room": "UPPER_HALL"}),
            _step(6, "p-2", "move", {"to_room": "ADMIN"}),
            _step(7, "p-2", "report", {"body_id": "body-p-1"}),
        ),
        kill_tick=4,
        report_tick=7,
    )
    assert evaluate_prefix(planted).reason == "engine_rejected_action"


def test_temporal_v2_renders_no_death_tick_body_handle() -> None:
    """The same meeting, rendered both ways: only the legacy handle carries the tick."""

    prefix = _unwitnessed_seed_one_prefix()
    replay = _replay_prefix(prefix)
    events = replay.result.tick_steps[-1].events
    current, _, _ = _build_meeting_trigger(
        state=replay.result.final_state, events=events, temporal_observations=True
    )
    legacy, _, _ = _build_meeting_trigger(
        state=replay.result.final_state, events=events, temporal_observations=False
    )
    assert not legacy_body_handles(
        prefix_surface_texts(prefix, trigger_line=current.description)
    )
    assert_no_legacy_body_handles(
        prefix_surface_texts(prefix, trigger_line=current.description)
    )

    # The planted legacy handle: the pre-v2 renderer names the death tick, and the
    # assertion refuses it.
    assert legacy_body_handles((legacy.description,)) == ("body-p-1-4",)
    with pytest.raises(HeldOutPrefixError, match="death-tick body handle"):
        assert_no_legacy_body_handles((legacy.description,))


def test_every_accepted_prefix_and_its_trigger_stay_free_of_the_legacy_handle() -> None:
    generated = generate()
    for prefix in generated.prefixes:
        evaluation = evaluate_prefix(prefix)
        assert evaluation.reason is None
        assert_no_legacy_body_handles(
            prefix_surface_texts(prefix, trigger_line=evaluation.trigger_line)
        )


def test_a_band_that_cannot_fill_the_set_stops_instead_of_widening() -> None:
    with pytest.raises(HeldOutPrefixError, match="not a reason to widen"):
        generate(SeedBand(first_seed=1, last_seed=3, size=50), AUTHORIZED_ROSTER)


def _committed_manifest() -> dict[str, object]:
    manifest = json.loads((REPO_ROOT / MANIFEST_PATH).read_text(encoding="utf-8"))
    assert isinstance(manifest, dict)
    return manifest


def test_the_committed_manifest_regenerates_from_its_own_band() -> None:
    """The freeze's fail-loud: any source edit that moves the set turns this red."""

    manifest = _committed_manifest()
    band = manifest["band"]
    assert isinstance(band, dict)
    roster = manifest["roster"]
    assert isinstance(roster, dict)
    generated = generate(
        SeedBand(
            first_seed=int(band["first_seed"]),
            last_seed=int(band["last_seed"]),
            size=int(band["size"]),
        ),
        PrefixRoster.model_validate(roster),
    )
    rebuilt = build_manifest(generated, repo_root=REPO_ROOT, card=str(manifest["card"]))
    assert rebuilt["accepted"] == manifest["accepted"]
    assert rebuilt["skipped"] == manifest["skipped"]
    assert rebuilt["source_sha256"] == manifest["source_sha256"]
    assert rebuilt == manifest


def test_the_manifest_records_the_development_definitions_as_absent() -> None:
    manifest = _committed_manifest()
    development = manifest["development_definitions"]
    assert isinstance(development, dict)
    assert development["sha256"] == development_definition_digests()
    assert development["absent_from_accepted"] is True
    accepted = manifest["accepted"]
    assert isinstance(accepted, list)
    digests = {str(row["sha256"]) for row in accepted}
    assert digests.isdisjoint(development_definition_digests().values())
    assert len(digests) == len(accepted) == int(str(manifest["band"]["size"]))  # type: ignore[index]


def test_the_manifest_commits_no_prefix_bytes() -> None:
    """Hashes only: the runner regenerates, it does not read a committed schedule."""

    text = (REPO_ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    for token in ('"steps"', '"to_room"', '"actor"', '"payload"'):
        assert token not in text
    for prefix in generate().prefixes:
        assert canonical_prefix_json(prefix) not in text


def test_the_manifest_records_the_flip_rather_than_a_deletion() -> None:
    manifest = _committed_manifest()
    assert manifest["status"] == "held_out"
    assert "never by deleting this file" in str(manifest["status_note"])
