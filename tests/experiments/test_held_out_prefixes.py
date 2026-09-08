"""The freeze's gates: determinism, proof-freedom, the body handle, and the manifest.

Every planted prefix here is built on seed 1 -- the seed the seven committed
development cases already use, and therefore development data by construction --
or on the debugging seeds 9001 and 9002, which the card records as inspected
outside the band. None of these tests reads a prefix drawn from the preregistered
held-out band; the only band prefixes they touch are the digests they compare
against the committed manifest.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import get_args

import pytest
from pydantic import TypeAdapter, ValidationError

from engine.world import Map, load_canonical_map
from experiments import held_out_prefixes
from experiments.deduction_scenarios import ScenarioDefinition
from experiments.held_out_prefixes import (
    AUTHORIZED_ROSTER,
    MANIFEST_PATH,
    MAX_TICKS,
    PREREGISTERED_BAND,
    TEMPORAL_OBSERVATION_VERSION,
    HeldOutPrefix,
    HeldOutPrefixError,
    PrefixRoster,
    PrefixStep,
    RejectionReason,
    ScheduleTickBudgetError,
    SeedBand,
    SkippedSeed,
    _replay_prefix,
    assert_no_legacy_body_handles,
    build_manifest,
    build_prefix,
    canonical_prefix_json,
    development_definition_digests,
    evaluate_prefix,
    filter_environment,
    generate,
    legacy_body_handles,
    manifest_skipped_seeds,
    prefix_sha256,
    prefix_surface_texts,
    skip_witness_roles,
    skip_witness_roles_over_range,
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


def _reporter_witnessed_seed_one_prefix() -> HeldOutPrefix:
    """The REPORTER's own wander left it in ADMIN when p-4 killed p-1 there.

    p-2 is the reporter in both witnessed plants. Here its pre-kill walk put it
    in the kill room, so the row the filter refuses the prefix for is the
    reporter's own -- the shape that produced six of the frozen band's eight
    skips.
    """

    return _planted(
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


def _bystander_witnessed_seed_one_prefix() -> HeldOutPrefix:
    """The uninvolved crewmate p-3 stood in ADMIN; the reporter p-2 walked in after.

    The same kill and the same reporter as the unwitnessed prefix above, with the
    ONE uninvolved crewmate the authorized 4p1i roster seats walking into the
    kill room instead of MEDBAY. The row the filter refuses the prefix for is
    that bystander's.
    """

    return _planted(
        steps=(
            *_walk_to_admin("p-1"),
            *_walk_to_admin("p-3"),
            *_walk_to_admin("p-4"),
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


def test_a_step_outside_the_replayed_window_is_refused() -> None:
    """A hashed step the loop never reaches is a digest for a run that never happened.

    The loop halts at ``MEETING_PHASE_REACHED`` on ``report_tick`` and the
    scheduler stops at ``max_ticks``, so a step past either is bound by
    ``prefix_sha256`` and never asked for. Both shapes are refused before a
    prefix object exists.
    """

    valid = _unwitnessed_seed_one_prefix()
    for late in (
        _step(valid.report_tick + 1, "p-2", "move", {"to_room": "UPPER_HALL"}),
        _step(99, "p-2", "move", {"to_room": "UPPER_HALL"}),
    ):
        with pytest.raises(ValidationError, match="inside the replayed window"):
            HeldOutPrefix(
                seed=valid.seed,
                roster=valid.roster,
                max_ticks=valid.max_ticks,
                steps=(*valid.steps, late),
                report_tick=valid.report_tick,
                kill_tick=valid.kill_tick,
            )
        with pytest.raises(ValidationError, match="inside the replayed window"):
            HeldOutPrefix.model_validate(
                {
                    **valid.model_dump(mode="json"),
                    "steps": [
                        step.model_dump(mode="json") for step in (*valid.steps, late)
                    ],
                }
            )
    with pytest.raises(ValidationError, match="inside its tick budget"):
        HeldOutPrefix(
            seed=valid.seed,
            roster=valid.roster,
            max_ticks=valid.report_tick,
            steps=valid.steps,
            report_tick=valid.report_tick,
            kill_tick=valid.kill_tick,
        )


def test_a_step_the_engine_never_resolves_never_reaches_a_digest() -> None:
    """The certifying seam: ``evaluate_prefix`` refuses a partly executed schedule.

    Neither shape is visible in the schedule alone, so the model cannot refuse
    them: a step addressed to a player the roster never seats reaches no agent,
    and a step addressed to a player the loop stopped asking because it was dead
    is never requested. Both move ``prefix_sha256`` while the engine resolves no
    action for the hashed ``(tick, actor)`` pair, which is the defect the
    duplicate gate closed for one route only.
    """

    valid = _unwitnessed_seed_one_prefix()
    unseated = _planted(
        steps=(*valid.steps, _step(5, "p-9", "move", {"to_room": "UPPER_HALL"})),
        kill_tick=valid.kill_tick,
        report_tick=valid.report_tick,
    )
    # p-1 is killed on tick 4, so the loop stops asking it for actions.
    after_death = _planted(
        steps=(*valid.steps, _step(6, "p-1", "move", {"to_room": "UPPER_HALL"})),
        kill_tick=valid.kill_tick,
        report_tick=valid.report_tick,
    )
    for planted in (unseated, after_death):
        assert prefix_sha256(planted) != prefix_sha256(valid)
        with pytest.raises(HeldOutPrefixError, match="executed step for step"):
            evaluate_prefix(planted)
    assert evaluate_prefix(valid).reason is None


def _with_extra_move(
    prefix: HeldOutPrefix, *, actor: str, to_room: str
) -> HeldOutPrefix:
    """``prefix`` plus one move for ``actor`` on its report tick."""

    steps = (
        *prefix.steps,
        _step(prefix.report_tick, actor, "move", {"to_room": to_room}),
    )
    return HeldOutPrefix(
        seed=prefix.seed,
        roster=prefix.roster,
        max_ticks=prefix.max_ticks,
        steps=tuple(sorted(steps, key=lambda step: (step.tick, step.action.actor))),
        report_tick=prefix.report_tick,
        kill_tick=prefix.kill_tick,
    )


def _report_tick_neighbour(
    seed: int, *, after_reporter: bool
) -> tuple[HeldOutPrefix, str, str]:
    """A generated prefix, an actor ordered against its reporter, and a legal room.

    The room is read from the state at meeting open, which — because no actor but
    the reporter is scheduled on the report tick — is the room that actor stands
    in when the report tick opens, so the added move is a legal one door away.
    """

    prefix = build_prefix(
        seed=seed, roster=AUTHORIZED_ROSTER, game_map=load_canonical_map()
    )
    reporter = next(
        step.action.actor for step in prefix.steps if step.action.type == "report"
    )
    final = _replay_prefix(prefix).result.final_state
    candidates = sorted(
        pid
        for pid, player in final.players.items()
        if player.alive
        and pid != reporter
        and ((pid > reporter) if after_reporter else (pid < reporter))
    )
    assert candidates, f"seed {seed} seats no such actor beside {reporter}"
    actor = candidates[0]
    return (
        prefix,
        actor,
        load_canonical_map().room_neighbors(final.players[actor].room)[0],
    )


def test_a_step_the_meeting_tick_discards_never_reaches_a_digest() -> None:
    """The seam counts what the ENGINE resolved, not what the agent served.

    ``advance_tick`` returns the instant the report puts the world in ``MEETING``,
    and the tick's actions are ordered by actor, so an action from an actor whose
    id sorts AFTER the reporter's is discarded with no event at all — not even a
    rejection. The agent still handed it to the loop, so a served-action count
    reads "honoured in full" while the digest binds a step the engine never ran.
    Seed 9001 is an out-of-band debugging seed whose reporter is not the
    last-sorting living player.
    """

    prefix, actor, to_room = _report_tick_neighbour(
        _DEBUG_SEEDS[0], after_reporter=True
    )
    planted = _with_extra_move(prefix, actor=actor, to_room=to_room)
    assert prefix_sha256(planted) != prefix_sha256(prefix)
    with pytest.raises(HeldOutPrefixError, match="executed step for step"):
        evaluate_prefix(planted)
    assert evaluate_prefix(prefix).reason is None


def test_a_report_tick_step_the_engine_does_resolve_passes_the_seam() -> None:
    """The seam tracks the engine rather than banning the report tick outright.

    The same shape on seed 9002, whose reporter sorts last among the living: the
    added move is ordered BEFORE the report, so the engine executes it and emits
    its ``Moved`` event. The generator still refuses to script it — which actor
    sorts where is not a property a hashed schedule should depend on — but the
    seam's business is what the engine resolved, and here it resolved this.
    """

    prefix, actor, to_room = _report_tick_neighbour(
        _DEBUG_SEEDS[1], after_reporter=False
    )
    planted = _with_extra_move(prefix, actor=actor, to_room=to_room)
    assert prefix_sha256(planted) != prefix_sha256(prefix)
    _replay_prefix(planted)


def test_the_generator_scripts_nobody_but_the_reporter_on_the_report_tick() -> None:
    """The generated schedules stay clear of the tick the meeting interrupts."""

    game_map = load_canonical_map()
    for seed in _DEBUG_SEEDS:
        prefix = build_prefix(seed=seed, roster=AUTHORIZED_ROSTER, game_map=game_map)
        on_report_tick = [
            step for step in prefix.steps if step.tick == prefix.report_tick
        ]
        assert [step.action.type for step in on_report_tick] == ["report"]


def test_the_filter_environment_is_built_per_use_and_refuses_mutation() -> None:
    """Prefix selection must not depend on state a same-process caller can reach.

    ``filter_environment`` builds its mapping from this module's pinned constants
    on every call, so there is no stored mapping to mutate; the returned proxy
    refuses item assignment as well, so a caller holding one cannot move it
    either. A caller that rebinds the module attribute is rewriting the module,
    which no in-module mechanism prevents -- the manifest's ``filter_environment``
    and ``source_sha256`` are what catch that, through
    ``test_the_committed_manifest_regenerates_from_its_own_band``.
    """

    expected = {
        "AILIBI_LLM_PROVIDER": "fake",
        "AILIBI_TEMPORAL_OBSERVATIONS": str(TEMPORAL_OBSERVATION_VERSION),
    }
    held = filter_environment()
    assert dict(held) == expected
    with pytest.raises(TypeError):
        held["AILIBI_TEMPORAL_OBSERVATIONS"] = "1"  # type: ignore[index]
    fresh = filter_environment()
    assert fresh is not held, "a stored mapping would be reachable state"
    assert dict(fresh) == expected


def test_the_tally_counts_an_out_of_band_range_without_opening_a_prefix() -> None:
    """The reproducing command behind the card's out-of-band rejection rate.

    The totals are fields rather than entries in the histogram, so a future
    reason code named ``seeds`` or ``accepted`` cannot overwrite one.
    """

    first, last = _DEBUG_SEEDS[0], _DEBUG_SEEDS[-1]
    walked = last - first + 1
    tally = tally_reasons(first, last)
    assert tally.seeds == walked
    assert tally.accepted + sum(tally.reasons.values()) == walked
    assert set(tally.reasons) <= set(get_args(RejectionReason))
    assert {"seeds", "accepted"}.isdisjoint(tally.reasons)


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


def _skip_roles_over_one_planted_seed(
    monkeypatch: pytest.MonkeyPatch, prefix: HeldOutPrefix
) -> Mapping[str, int]:
    """``skip_witness_roles`` over one out-of-band seed whose draw is ``prefix``.

    The attribution is a property of the drawn schedule, not of the seed, so the
    plant is served through ``build_prefix`` for an out-of-band debugging seed:
    the count is then produced by the same walk the manifest command runs, with
    no band seed touched.
    """

    def stub(
        *,
        seed: int,
        roster: PrefixRoster,
        game_map: Map,
        max_ticks: int = MAX_TICKS,
    ) -> HeldOutPrefix:
        assert seed == _DEBUG_SEEDS[0]
        return prefix

    monkeypatch.setattr(held_out_prefixes, "build_prefix", stub)
    return skip_witness_roles([_DEBUG_SEEDS[0]])


def test_a_skip_is_attributed_to_the_reporter_when_its_own_wander_witnessed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A reporter standing in the kill room is a reporter row, not a bystander one.

    The card claimed the uninvolved crewmate's wander was where every band skip
    came from. The reporter wanders before the kill exactly as a bystander does,
    so its own walk can leave it in the kill room -- and counted over the frozen
    band's published skips it is the more common witness. Without this split the
    claim cannot be checked at all, because a skip records only its reason code.
    """

    evaluation = evaluate_prefix(_reporter_witnessed_seed_one_prefix())
    assert evaluation.reason == "witnessed_kill"
    assert evaluation.proof_rows_by_role == {"bystander": 0, "reporter": 1}
    assert _skip_roles_over_one_planted_seed(
        monkeypatch, _reporter_witnessed_seed_one_prefix()
    ) == {"bystander": 0, "reporter": 1}


def test_a_skip_is_attributed_to_the_bystander_when_its_wander_witnessed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The other side: the one uninvolved crewmate walks in and the reporter does not."""

    evaluation = evaluate_prefix(_bystander_witnessed_seed_one_prefix())
    assert evaluation.reason == "witnessed_kill"
    assert evaluation.proof_rows_by_role == {"bystander": 1, "reporter": 0}
    assert _skip_roles_over_one_planted_seed(
        monkeypatch, _bystander_witnessed_seed_one_prefix()
    ) == {"bystander": 1, "reporter": 0}


def test_the_skip_role_split_reaches_the_band_only_through_the_published_skips() -> (
    None
):
    """A per-range role count over band seeds is still a read of the held-out set.

    The range form refuses the band exactly as the tally does. The band's own
    skips are reachable only through ``manifest_skipped_seeds``, which reads the
    seeds the committed manifest already publishes rather than choosing a range,
    and the count it feeds names a role, never a step, a room or a tick.
    """

    for first, last in (
        (PREREGISTERED_BAND.first_seed, PREREGISTERED_BAND.first_seed),
        (PREREGISTERED_BAND.first_seed - 1, PREREGISTERED_BAND.first_seed),
        (PREREGISTERED_BAND.last_seed, PREREGISTERED_BAND.last_seed + 1),
        (1, PREREGISTERED_BAND.last_seed + 1000),
    ):
        with pytest.raises(
            HeldOutPrefixError, match="intersect the preregistered band"
        ):
            skip_witness_roles_over_range(first, last)
    with pytest.raises(HeldOutPrefixError, match="must not run backwards"):
        skip_witness_roles_over_range(_DEBUG_SEEDS[1], _DEBUG_SEEDS[0])

    published = manifest_skipped_seeds(REPO_ROOT)
    skipped = _committed_manifest()["skipped"]
    assert isinstance(skipped, list)
    assert published == tuple(int(row["seed"]) for row in skipped)
    assert all(
        PREREGISTERED_BAND.first_seed <= seed <= PREREGISTERED_BAND.last_seed
        for seed in published
    )


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

    evaluation = evaluate_prefix(_reporter_witnessed_seed_one_prefix())
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


def test_a_seed_whose_schedule_overruns_the_budget_is_skipped_not_a_stop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A seed the generator cannot SCHEDULE is a skip with a reason code.

    No seed walked so far draws a schedule that overruns the budget, so the path
    is planted: ``build_prefix`` is made to raise ``ScheduleTickBudgetError`` for
    the first of two out-of-band debugging seeds. Before this, the exception
    escaped ``generate`` and ``tally_reasons`` and one unlucky seed would have
    aborted the whole draw instead of being recorded and walked past.
    """

    doomed, healthy = _DEBUG_SEEDS
    real = held_out_prefixes.build_prefix

    def stub(
        *,
        seed: int,
        roster: PrefixRoster,
        game_map: Map,
        max_ticks: int = MAX_TICKS,
    ) -> HeldOutPrefix:
        if seed == doomed:
            raise ScheduleTickBudgetError(
                f"seed {seed} staged the reporter beyond the tick budget"
            )
        return real(seed=seed, roster=roster, game_map=game_map, max_ticks=max_ticks)

    monkeypatch.setattr(held_out_prefixes, "build_prefix", stub)
    generated = generate(
        SeedBand(first_seed=doomed, last_seed=healthy, size=1), AUTHORIZED_ROSTER
    )
    assert generated.skipped == (
        SkippedSeed(seed=doomed, reason="schedule_exceeds_tick_budget"),
    )
    assert [prefix.seed for prefix in generated.prefixes] == [healthy]

    tally = tally_reasons(doomed, healthy)
    assert tally.reasons["schedule_exceeds_tick_budget"] == 1
    assert tally.accepted + sum(tally.reasons.values()) == tally.seeds


def test_an_unauthorized_roster_still_raises_rather_than_becoming_a_skip() -> None:
    """The skip path is for a seed's own draw, not for invalid input."""

    with pytest.raises(HeldOutPrefixError, match="authorized held-out roster"):
        generate(
            SeedBand(first_seed=_DEBUG_SEEDS[0], last_seed=_DEBUG_SEEDS[1], size=1),
            PrefixRoster(num_players=3, num_impostors=1, tasks_per_crewmate=1),
        )


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
