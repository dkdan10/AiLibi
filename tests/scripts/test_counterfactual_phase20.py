"""The offline counterfactual's CLI contract, its OFF baseline and its purity.

Four things are pinned here, in the order a reader has to believe them:

1. the slate is the registry's eight Phase-20 levers, toggled by argument;
2. the OFF column IS the committed baseline — every cell equals its 20.15 pin and
   the innocent-ejection enumeration equals the committed 19.14 split;
3. the run mutates no process environment and reads none;
4. the memo's table equals the script's output, so the document cannot drift.

Each gate ships with a planted case proving it bites.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Final

import pytest

from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.memory.store import DEFAULT_TOKEN_BUDGET, AgentMemory, render_for_prompt
from agents.perception import (
    EVENT_REPORTED_TESTIMONY,
    EVENT_SAW_PLAYER,
    EVENT_SELF_STATE,
    PROVENANCE_OBSERVED,
    PROVENANCE_REPORTED,
)
from eval.evidence_honesty import compute_evidence_honesty, live_impostor_policy
from engine.entities import Role
from meetings.schemas import ContradictionRef
from meetings.transcript import detect_contradictions
from orchestrator.game import TacticalAgent
from orchestrator.replay import (
    TOGGLEABLE_SUBSTRATE_FLAG_KEYS,
    env_var_for_lever,
    substrate_flag_snapshot,
)
import counterfactual_phase20 as cf

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
_MEMO: Final[Path] = _REPO_ROOT / "audits" / "audit-phase-20-counterfactual.md"
# The fastest committed set (50 games, 39 meetings): enough to exercise every
# branch of the CLI without a whole-corpus walk in each test.
_FAST_SET: Final[str] = "samples/4p1i"


@pytest.fixture(scope="module")
def fast_payload() -> Mapping[str, object]:
    """One run over the fast set, shared by every fast test in this module."""

    return cf.run([_FAST_SET])


@pytest.fixture(scope="module")
def full_payload() -> Mapping[str, object]:
    """One whole-corpus run (~30 s), shared by the memo and pooled pins."""

    return cf.run(list(cf.CANONICAL_SETS))


def _rows(payload: Mapping[str, object], set_name: str) -> dict[str, list[int]]:
    sets = payload["sets"]
    assert isinstance(sets, dict)
    block = sets[set_name]
    assert isinstance(block, dict)
    out: dict[str, list[int]] = {}
    for row in block["rows"]:
        for column in ("recorded_off", "reconstructed_off", "on"):
            value = row[column]
            if value is not None:
                out[f"{row['cell']}|{row['label']}|{column}"] = value
    return out


def _pooled(payload: Mapping[str, object]) -> dict[str, list[int]]:
    pooled = payload["pooled"]
    assert isinstance(pooled, list)
    out: dict[str, list[int]] = {}
    for row in pooled:
        for column in ("recorded_off", "reconstructed_off", "on"):
            value = row[column]
            if value is not None:
                out[f"{row['cell']}|{row['label']}|{column}"] = value
    return out


# --------------------------------------------------------------------------- #
# 1. The slate.                                                                #
# --------------------------------------------------------------------------- #


def test_the_slate_is_the_registrys_eight_phase_20_levers() -> None:
    # Read off the substrate registry, never listed locally: a lever registered
    # at 20.33 and forgotten here would silently drop out of the slate this memo
    # predicts for.
    assert len(cf.PHASE_20_LEVERS) == 8
    assert set(cf.PHASE_20_LEVERS) == set(TOGGLEABLE_SUBSTRATE_FLAG_KEYS) - {
        "impostor_roll_call"
    }
    assert dict(cf.SLATE_ON) == {
        env_var_for_lever(key): "1" for key in cf.PHASE_20_LEVERS
    }
    assert dict(cf.SLATE_OFF) == {}
    # The three detector levers are a subset of the eight, and each leave-one-out
    # leg withholds exactly one of them.
    assert set(cf.DETECTOR_LEVERS) <= set(cf.PHASE_20_LEVERS)
    for lever in cf.DETECTOR_LEVERS:
        leg = cf.LEAVE_ONE_OUT[f"-{lever}"]
        assert env_var_for_lever(lever) not in leg
        assert len(leg) == len(cf.SLATE_ON) - 1


def test_the_lever_7_decomposition_slate_names_the_lever_it_withholds() -> None:
    # The census headline runs at the FULL eight (Task 20.34 widened the
    # instrument's row patterns so they read the '[meeting N]' frame lever 7
    # renders). The seven-lever leg survives only as the decomposition printed
    # beside it, and its slate is derived, so the withheld lever cannot silently
    # become two.
    assert (
        env_var_for_lever("meeting_outcome_memory")
        not in cf.LEVER_7_DECOMPOSITION_SLATE
    )
    assert len(cf.LEVER_7_DECOMPOSITION_SLATE) == len(cf.SLATE_ON) - 1
    assert "meeting_outcome_memory" in cf.LEVER_7_DECOMPOSITION_LABEL


# --------------------------------------------------------------------------- #
# 2. The OFF column IS the committed baseline.                                 #
# --------------------------------------------------------------------------- #


def test_the_off_column_equals_the_committed_pins_on_the_fast_set(
    fast_payload: Mapping[str, object],
) -> None:
    """Every §3.1 cell for samples/4p1i, RECORDED and RECONSTRUCTED alike."""

    rows = _rows(fast_payload, _FAST_SET)
    expected: Mapping[str, list[int]] = {
        "I-3|sole-flag convicting precision (per victim)": [1, 2],
        "I-3|class impostor share (STRONG alibi_vs_sighting, dedup subjects)": [1, 2],
        "I-3|living-voter base rate at those meetings": [2, 6],
        "I-4|grounded sighting side (at tick)": [1, 2],
        "I-4|grounded sighting side (within +/-1 tick)": [1, 2],
        "I-4|grounded sighting side (within +/-2 ticks)": [1, 2],
        "I-4|resolvable sighting sides (of all STRONG sides)": [2, 2],
        "I-6|adjacent-room STRONG share": [1, 2],
        "I-6|adjacent-room STRONG share (un-gated adjacent_any_gap)": [1, 2],
        "I-7|movement-origin flags": [0, 3],
        "I-8|marker contamination (turns)": [0, 117],
        "I-8|marker contamination (prompts)": [0, 234],
        "I-9|singular-persona prompts": [234, 234],
        "I-5|fabricated completion lines": [15, 61],
        "I-12|containment (killer in the candidate set)": [35, 35],
        "I-12|singleton candidate sets": [6, 35],
        "I-12|singleton correct": [6, 6],
        "I-12|ejections on an already-cleared player": [0, 8],
    }
    for label, pin in expected.items():
        assert rows[f"{label}|recorded_off"] == pin, label
    # The reconstruction reproduces the recorded artefact exactly wherever the two
    # populations are the same one — every flag cell and the turn cell.
    for label in (
        "I-3|sole-flag convicting precision (per victim)",
        "I-4|grounded sighting side (at tick)",
        "I-6|adjacent-room STRONG share",
        "I-7|movement-origin flags",
        "I-8|marker contamination (turns)",
    ):
        assert rows[f"{label}|reconstructed_off"] == rows[f"{label}|recorded_off"]


def test_the_innocent_ejection_enumeration_reproduces_the_committed_split(
    full_payload: Mapping[str, object],
) -> None:
    """23 / 54 / 2 / 0 — the 19.14 non-direct innocent cells that sum to 79."""

    sets = full_payload["sets"]
    assert isinstance(sets, dict)
    per_set = [sets[name]["innocent_ejections"] for name in cf.CANONICAL_SETS]
    assert per_set == [23, 54, 2, 0]
    assert sum(per_set) == 79
    assert dict(cf.COMMITTED_INNOCENT_EJECTIONS) == dict(
        zip(cf.CANONICAL_SETS, per_set, strict=True)
    )


def test_the_pooled_off_column_equals_the_ratified_baseline_cells(
    full_payload: Mapping[str, object],
) -> None:
    """The §3.1 pooled figures, recomputed by this script's own OFF leg."""

    pooled = _pooled(full_payload)
    assert pooled["I-3|sole-flag convicting precision (per victim)|recorded_off"] == [
        12,
        82,
    ]
    assert pooled["I-4|grounded sighting side (at tick)|recorded_off"] == [124, 234]
    assert pooled["I-6|adjacent-room STRONG share|recorded_off"] == [148, 234]
    assert pooled[
        "I-6|adjacent-room STRONG share (un-gated adjacent_any_gap)|recorded_off"
    ] == [148, 234]
    assert pooled["I-7|movement-origin flags|recorded_off"] == [38, 313]
    assert pooled["I-12|ejections on an already-cleared player|recorded_off"] == [
        83,
        354,
    ]
    # The G-2 census, re-derived rather than quoted: 70 of the 79 wrongful
    # ejections rode a STRONG flag, and every one of those was kind-sole.
    assert pooled["E|innocent ejections still carrying a STRONG flag|recorded_off"] == [
        70,
        79,
    ]
    # And the whole point of the memo: the slate clears all but three.
    assert pooled["E|innocent ejections still carrying a STRONG flag|on"] == [3, 79]


def test_the_cleared_census_is_a_join_and_not_a_subtraction(
    full_payload: Mapping[str, object],
) -> None:
    """79 - 3 is the wrong arithmetic, in both directions, and the rows say so."""

    pooled = _pooled(full_payload)
    survivors = pooled["E|innocent ejections still carrying a STRONG flag|on"]
    cleared = pooled[
        "E|innocent ejections that LOSE the STRONG flag they convicted on|on"
    ]
    minted = pooled["E|innocent ejections that NEWLY carry a STRONG flag|on"]
    # The two denominators partition the 79: those that had a STRONG flag to lose
    # and those that never had one.
    assert cleared[1] + minted[1] == 79
    assert cleared[1] == 70
    # 67 of the 70 lose it; none of the nine gains one. The naive 79 - 3 = 76 is
    # NINE larger than the population that could possibly have lost anything.
    assert cleared[0] == 67
    assert minted[0] == 0
    assert cleared[1] - cleared[0] + minted[0] == survivors[0]
    assert 79 - survivors[0] != cleared[0]


def test_the_render_census_population_is_the_recorded_prompt_count(
    full_payload: Mapping[str, object],
) -> None:
    """The census unit is the recorded LLM call, not the meeting-agent.

    A meeting issues a different number of opening / reply / opt-in / ballot calls
    per agent. The reconstruction weights each agent's single render by that
    recorded multiplicity — an agent's memory does not change inside a meeting —
    so the two OFF readings share ONE denominator instead of the reconstruction
    silently re-weighting the population.
    """

    pooled = _pooled(full_payload)
    recorded = pooled["R|rendered memory rows per snapshot (mean)|recorded_off"]
    rebuilt = pooled["R|rendered memory rows per snapshot (mean)|reconstructed_off"]
    on = pooled["R|rendered memory rows per snapshot (mean)|on"]
    # The recorded prompt population, and both reconstruction legs on it.
    assert recorded[1] == 7932
    assert rebuilt[1] == recorded[1]
    assert on[1] == recorded[1]
    # The residual is carried, not smoothed: under a quarter of a percent.
    assert abs(rebuilt[0] - recorded[0]) / recorded[0] < 0.0025
    # An unweighted census would land on 3,934 meeting-agent renders — half the
    # population — so a regression to the equal-weight form fails here.
    assert rebuilt[1] != 3934


def test_the_render_census_headline_is_the_full_eight_lever_slate(
    full_payload: Mapping[str, object],
) -> None:
    """The census the record reads against is the slate the record ships.

    Task 20.34 widened the instrument's row patterns once, in
    ``eval/evidence_honesty.py``, so a ``[meeting N]``-tagged testimony frame is
    counted. The headline census therefore runs at all eight, and the seven-lever
    reading survives only BESIDE it, labelled as the lever-7 decomposition.
    """

    pooled = full_payload["pooled"]
    assert isinstance(pooled, list)
    by_label = {f"{row['cell']}|{row['label']}": row for row in pooled}
    for label in (
        "R|rendered memory rows per snapshot (mean)",
        "R|reported-testimony rows retained",
        "R|reported-testimony rows, <=4 living",
        "R|reported-testimony rows, 5-6 living",
        "R|reported-testimony rows, >=7 living",
    ):
        assert by_label[label]["on_slate"] == cf.FULL_SLATE_LABEL, label
    for label in (
        "R|rendered memory rows per snapshot (mean), less lever 7",
        "R|reported-testimony rows retained, less lever 7",
    ):
        assert by_label[label]["on_slate"] == cf.LEVER_7_DECOMPOSITION_LABEL, label
    # The decomposition is a real second measurement, not a copy: withholding the
    # lever moves both cells. If these ever coincide the leg has stopped toggling.
    full_rows = by_label["R|rendered memory rows per snapshot (mean)"]["on"]
    seven_rows = by_label["R|rendered memory rows per snapshot (mean), less lever 7"][
        "on"
    ]
    assert full_rows[1] == seven_rows[1]
    assert full_rows[0] != seven_rows[0]
    full_testimony = by_label["R|reported-testimony rows retained"]["on"]
    seven_testimony = by_label["R|reported-testimony rows retained, less lever 7"]["on"]
    assert full_testimony[0] > seven_testimony[0]
    # And the widening bites where it was supposed to: at the full slate the
    # census counts MORE testimony rows than the seven-lever leg, which is the
    # tagged frame the OFF-shaped pattern used to drop.
    assert full_testimony[0] / full_testimony[1] > (
        seven_testimony[0] / seven_testimony[1]
    )


def test_the_decomposition_leg_is_ingest_lineage_invariant() -> None:
    """Withholding lever 7 at RENDER time prices its INGEST half too.

    `meeting_outcome_memory` is the one lever with an ingest seam: ON, a spoken
    `saw_vent` statement is kept as reported CONTENT, so the ON memory lineage
    holds an event a lever-OFF ingest would have dropped. The decomposition leg
    renders that ON lineage under the withheld-lever slate rather than rebuilding
    a third lineage, which is sound because the extra event renders to NOTHING
    when the render-time lever is OFF (`_render_reported_testimony` returns None
    for that kind) and a reported-testimony event carries no observation id to
    shift a sequence. Asserted here, not argued: the two lineages render
    byte-identically on the decomposition slate, and differ on the full one.
    """

    def _memory(*, with_vent: bool) -> AgentMemory:
        store = MemoryStore()
        store.append(
            EpisodicEvent(
                tick=4,
                type=EVENT_SELF_STATE,
                payload={
                    "agent_id": "p-1",
                    "room": "CAFETERIA",
                    "role": "CREWMATE",
                    "pending_task_id": None,
                    "owned_task_ids": (),
                    "fellow_impostor_ids": (),
                    "in_vent": False,
                },
                provenance=PROVENANCE_OBSERVED,
                observation_id="p-1:4:0",
            )
        )
        statements: list[tuple[str, str]] = [("saw_player", "p-3")]
        if with_vent:
            statements.append(("saw_vent", "p-4"))
        for kind, subject in statements:
            store.append(
                EpisodicEvent(
                    tick=5,
                    type=EVENT_REPORTED_TESTIMONY,
                    payload={
                        "speaker": "p-2",
                        "kind": kind,
                        "subject": subject,
                        "meeting_index": 1,
                        "from_tick": 3,
                        "to_tick": 3,
                        "room": "ADMIN",
                        "co_present": (),
                    },
                    provenance=PROVENANCE_REPORTED,
                )
            )
        return AgentMemory(episodic=store)

    on_ingest = _memory(with_vent=True)
    off_ingest = _memory(with_vent=False)
    withheld = {
        "seven": cf.LEVER_7_DECOMPOSITION_SLATE,
        "full": cf.SLATE_ON,
    }
    rendered = {
        f"{slate}:{leg}": render_for_prompt(
            memory, token_budget=DEFAULT_TOKEN_BUDGET, env=env
        )
        for slate, env in withheld.items()
        for leg, memory in (("on", on_ingest), ("off", off_ingest))
    }
    # The decomposition leg cannot tell the two lineages apart — which is exactly
    # what makes rendering the ON lineage under the withheld slate legitimate.
    assert rendered["seven:on"] == rendered["seven:off"]
    # And the two stores really do differ: the full slate renders the vent claim.
    assert rendered["full:on"] != rendered["full:off"]
    assert "VENT" in rendered["full:on"]
    assert "VENT" not in rendered["seven:on"]


def test_the_testimony_buckets_partition_the_testimony_total(
    full_payload: Mapping[str, object],
) -> None:
    """The registered census is per living-roster bucket and never blended."""

    pooled = _pooled(full_payload)
    total_off = pooled["R|reported-testimony rows retained|recorded_off"]
    buckets = [
        pooled[f"R|reported-testimony rows, {bucket} living|recorded_off"]
        for bucket in ("<=4", "5-6", ">=7")
    ]
    assert sum(pair[0] for pair in buckets) == total_off[0]
    # Every bucket shares one denominator: the leg's own testimony total.
    assert {pair[1] for pair in buckets} == {total_off[0]}
    # The ON leg gains in ALL THREE bands, so the published aggregate is not one
    # band's gain wearing a blended figure's clothes.
    on_buckets = [
        pooled[f"R|reported-testimony rows, {bucket} living|on"]
        for bucket in ("<=4", "5-6", ">=7")
    ]
    reconstructed = [
        pooled[f"R|reported-testimony rows, {bucket} living|reconstructed_off"]
        for bucket in ("<=4", "5-6", ">=7")
    ]
    for on_pair, off_pair in zip(on_buckets, reconstructed, strict=True):
        assert on_pair[0] > off_pair[0]
    # The ON buckets partition the ON total too, on the full-slate leg: the
    # headline census and its bands are one measurement, not two.
    total_on = pooled["R|reported-testimony rows retained|on"]
    assert sum(pair[0] for pair in on_buckets) == total_on[0]
    assert {pair[1] for pair in on_buckets} == {total_on[0]}


def test_the_i13_anchored_fixtures_publish_their_flag_half(
    full_payload: Mapping[str, object],
) -> None:
    """Bar 8's computable half: the four committed anchors, OFF and ON."""

    sets = full_payload["sets"]
    assert isinstance(sets, dict)
    anchors = {
        f"{name} {key}": cells
        for name, block in sets.items()
        for key, cells in block["i13_anchors"].items()
    }
    assert set(anchors) == {
        "samples/9p2i 23:1",
        "samples/9p2i 12:0",
        "samples/4p1i 49:0",
        "samples/4p1i 41:0",
    }
    # (a) and (b) lose their only STRONG flag; the ejectee's goes with it.
    for key in ("samples/9p2i 23:1", "samples/9p2i 12:0"):
        assert anchors[key] == {
            "strong_off": 1,
            "strong_on": 0,
            "victim_strong_off": 1,
            "victim_strong_on": 0,
        }
    # (c)'s seed-49 anchor carried NO strong flag OFF, so its flag half cannot
    # move at all — the memo says so rather than claiming a flip.
    assert anchors["samples/4p1i 49:0"]["strong_off"] == 0
    assert anchors["samples/4p1i 49:0"]["strong_on"] == 0
    # (d)'s equal-weight conflict resolves the right way: one of the two STRONG
    # flags survives and it is NOT the one against the ejected crewmate.
    seed41 = anchors["samples/4p1i 41:0"]
    assert seed41["strong_off"] == 2
    assert seed41["strong_on"] == 1
    assert seed41["victim_strong_off"] == 1
    assert seed41["victim_strong_on"] == 0


def test_a_perturbed_innocent_pin_fails_the_enumeration_gate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The gate bites: a join that miscounts is a defect in the script."""

    monkeypatch.setattr(
        cf, "COMMITTED_INNOCENT_EJECTIONS", {_FAST_SET: 999}, raising=True
    )
    with pytest.raises(SystemExit) as raised:
        cf.run([_FAST_SET])
    assert "DEFECT IN THIS SCRIPT" in str(raised.value)
    assert "999" in str(raised.value)


def test_a_drifted_reconstruction_refuses_to_print_an_on_column(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The fidelity gate bites: an OFF leg that is not the record stops the run."""

    def dropping(*args: object, **kwargs: object) -> tuple[ContradictionRef, ...]:
        flags = detect_contradictions(*args, **kwargs)  # type: ignore[arg-type]
        return flags[1:] if kwargs.get("env") == cf.SLATE_OFF else flags

    monkeypatch.setattr(
        "counterfactual_phase20.detect_contradictions", dropping, raising=True
    )
    with pytest.raises(SystemExit) as raised:
        cf.run([_FAST_SET])
    assert "not the recorded substrate" in str(raised.value)
    assert "DEFECT IN THIS SCRIPT" in str(raised.value)


def test_the_reconstruction_reproduces_every_recorded_flag_on_the_fast_set() -> None:
    """The claim the whole ON column rests on, stated as its own pin."""

    walk = cf.walk_set(Path("replays") / _FAST_SET, set_name=_FAST_SET)
    assert walk.meetings == 39
    assert walk.off_flags_match_recorded == walk.meetings
    # And the OFF fold lands on the instrument's own report over the same bytes.
    recorded = compute_evidence_honesty(Path("replays") / _FAST_SET)
    off = walk.legs["off"].tallies
    assert off.adjacent_flags == recorded.adjacent_room_flags.adjacent.numerator
    assert off.strong_flags == recorded.adjacent_room_flags.adjacent.denominator


def test_the_sighting_channel_is_the_two_stage_production_composition() -> None:
    """The channel the detector grounds against is the accessor AND the manager.

    ``TacticalAgent.sighting_records_for_meeting`` deliberately KEEPS an
    impostor's rows naming a fellow impostor (its only other consumer
    corroborates); ``MeetingManager`` drops them when it builds the per-speaker
    mapping it threads into ``detect_contradictions`` (meetings/manager.py, "The
    §4.7 TEAMMATE firewall is applied HERE, not inherited"). Reading either half
    alone gives the ON slate a channel production never grounds against, so this
    composes both and pins the counterfactual's rebuild against the result.
    """

    roles: Mapping[str, Role] = {
        "p-1": "IMPOSTOR",
        "p-2": "IMPOSTOR",
        "p-3": "CREWMATE",
    }
    store = MemoryStore()
    store.append(
        EpisodicEvent(
            tick=1,
            type=EVENT_SELF_STATE,
            payload={
                "agent_id": "p-1",
                "room": "CAFETERIA",
                "role": "IMPOSTOR",
                "pending_task_id": None,
                "owned_task_ids": (),
                "fellow_impostor_ids": ("p-2",),
                "in_vent": False,
            },
            provenance=PROVENANCE_OBSERVED,
            observation_id="p-1:1:0",
        )
    )
    for index, subject in enumerate(("p-2", "p-3")):
        store.append(
            EpisodicEvent(
                tick=1,
                type=EVENT_SAW_PLAYER,
                payload={"player_id": subject, "room": "CAFETERIA"},
                provenance=PROVENANCE_OBSERVED,
                observation_id=f"p-1:1:{index + 1}",
            )
        )

    agent = TacticalAgent(
        agent_id="p-1",
        policy=live_impostor_policy("p-1"),
        role="IMPOSTOR",
        memory=AgentMemory(episodic=store),
    )
    accessor_rows = agent.sighting_records_for_meeting()
    # Stage 1 keeps the teammate row — this is the half a reader can mistake for
    # the whole channel.
    assert {record.subject for record in accessor_rows} == {"p-2", "p-3"}
    # Stage 2 is the manager's own filter, restated from its source predicate.
    fellows = frozenset(("p-2",))
    production = tuple(
        record for record in accessor_rows if record.subject not in fellows
    )
    assert {record.subject for record in production} == {"p-3"}
    # And the counterfactual rebuilds the COMPOSITION, not either half.
    rebuilt = cf._sighting_channel(store, speaker="p-1", roles=roles)
    assert rebuilt == production
    # A crewmate speaker filters nothing, in either path.
    crew_store = MemoryStore()
    crew_store.append(
        EpisodicEvent(
            tick=1,
            type=EVENT_SELF_STATE,
            payload={
                "agent_id": "p-3",
                "room": "CAFETERIA",
                "role": "CREWMATE",
                "pending_task_id": None,
                "owned_task_ids": (),
                "fellow_impostor_ids": (),
                "in_vent": False,
            },
            provenance=PROVENANCE_OBSERVED,
            observation_id="p-3:1:0",
        )
    )
    crew_store.append(
        EpisodicEvent(
            tick=1,
            type=EVENT_SAW_PLAYER,
            payload={"player_id": "p-1", "room": "CAFETERIA"},
            provenance=PROVENANCE_OBSERVED,
            observation_id="p-3:1:1",
        )
    )
    assert [
        record.subject
        for record in cf._sighting_channel(crew_store, speaker="p-3", roles=roles)
    ] == ["p-1"]


# --------------------------------------------------------------------------- #
# 3. Purity: toggled by argument, never by environment.                        #
# --------------------------------------------------------------------------- #


def test_a_full_run_leaves_the_process_environment_identical() -> None:
    before = dict(os.environ)
    cf.run([_FAST_SET])
    assert dict(os.environ) == before
    # And the ambient slate the recorders stamp is still all-OFF afterwards, so a
    # recording started in this process would stamp baseline 6.
    snapshot = substrate_flag_snapshot()
    assert [snapshot[key] for key in cf.PHASE_20_LEVERS] == [False] * 8


def test_the_script_assigns_to_no_environment() -> None:
    """The seam is the ``env`` parameter, so no write path may exist at all."""

    source = (_REPO_ROOT / "scripts" / "counterfactual_phase20.py").read_text(
        encoding="utf-8"
    )
    assert "os.environ[" not in source
    assert "environ.setdefault" not in source
    assert "environ.update" not in source
    assert "putenv" not in source
    # And the read side: every slate reaches a resolver as an argument, so the
    # module never needs ``os`` at all.
    assert "\nimport os\n" not in source


def test_a_stale_export_refuses_to_run(monkeypatch: pytest.MonkeyPatch) -> None:
    """The gate bites: an operator with a lever exported gets a refusal."""

    monkeypatch.setenv(env_var_for_lever("grounded_prosecution"), "1")
    with pytest.raises(SystemExit) as raised:
        cf.run([_FAST_SET])
    assert "the ambient process slate is not OFF" in str(raised.value)
    assert "AILIBI_GROUNDED_PROSECUTION" in str(raised.value)


# --------------------------------------------------------------------------- #
# 4. The CLI contract, and the memo that cannot drift from it.                 #
# --------------------------------------------------------------------------- #


def test_the_cli_emits_the_table_and_the_json(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cf.main(["--sets", _FAST_SET]) == 0
    printed = capsys.readouterr().out
    assert "RECORDED-OFF" in printed
    assert "RECONSTRUCTED-OFF" in printed
    assert "reading rules:" in printed
    assert "wall time:" in printed

    assert cf.main(["--sets", _FAST_SET, "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["levers"] == list(cf.PHASE_20_LEVERS)
    assert payload["slate_on"] == dict(cf.SLATE_ON)
    assert _FAST_SET in payload["sets"]
    assert payload["pooled"]


_MEMO_ROW: Final[re.Pattern[str]] = re.compile(
    r"^\| (?P<cell>[A-Z0-9-]+) \| (?P<label>[^|]+?) \| (?P<off>[^|]+?) \| "
    r"(?P<on>[^|]+?) \|",
    re.MULTILINE,
)
_COUNTS: Final[re.Pattern[str]] = re.compile(r"^(\d+)/(\d+)$")


def _memo_pooled_rows() -> dict[str, tuple[str, str]]:
    """The memo's pooled OFF/ON table, parsed back into ``label -> (off, on)``."""

    return _parse_pooled_rows(_MEMO.read_text(encoding="utf-8"))


def _parse_pooled_rows(text: str) -> dict[str, tuple[str, str]]:
    """Parse one memo's fenced pooled table; shared with the perturbation gate."""

    body = text.split("<!-- POOLED-TABLE-START -->")[1].split(
        "<!-- POOLED-TABLE-END -->"
    )[0]
    return {
        f"{match.group('cell')}|{match.group('label').strip()}": (
            match.group("off").strip(),
            match.group("on").strip(),
        )
        for match in _MEMO_ROW.finditer(body)
    }


def test_the_memo_table_equals_the_scripts_output(
    full_payload: Mapping[str, object],
) -> None:
    """The document cannot drift from the instrument: every row is re-derived."""

    stated = _memo_pooled_rows()
    assert stated, "the memo's pooled table did not parse — the markers moved"
    pooled = full_payload["pooled"]
    assert isinstance(pooled, list)
    computed = {f"{row['cell']}|{row['label']}": row for row in pooled}
    # Row inventory both ways: a memo row this script does not compute is drift,
    # and a computed row the memo drops is a silent omission.
    assert set(stated) == set(computed), (
        f"memo-only: {sorted(set(stated) - set(computed))}; "
        f"script-only: {sorted(set(computed) - set(stated))}"
    )
    mismatches: list[str] = []
    for label, (off_text, on_text) in stated.items():
        row = computed[label]
        _check_cell(label, "OFF", off_text, row["recorded_off"], mismatches)
        _check_cell(label, "ON", on_text, row["on"], mismatches)
    assert not mismatches, "\n".join(mismatches)


_PER_SET_RENDER_ROW: Final[re.Pattern[str]] = re.compile(
    r"^\| (?P<label>render rows/snapshot|testimony retained), "
    r"(?P<slate>all eight ON|less lever 7) \|(?P<cells>.+)\|$",
    re.MULTILINE,
)


def _per_set_render_mismatches(
    text: str, sets: Mapping[str, Mapping[str, object]]
) -> list[str]:
    """Re-derive every §5 render figure — BOTH sides of each ``OFF → ON`` cell.

    The OFF half is the RECONSTRUCTED leg, which §5 uses on purpose for its
    apples-to-apples comparison against a reconstructed ON, so a stale OFF value
    is drift exactly like a stale ON one.
    """

    stated = list(_PER_SET_RENDER_ROW.finditer(text))
    assert len(stated) == 4, "§5's four render rows did not parse — the table moved"
    mismatches: list[str] = []
    for match in stated:
        suffix = "" if match.group("slate") == "all eight ON" else ", less lever 7"
        label = (
            "rendered memory rows per snapshot (mean)"
            if match.group("label") == "render rows/snapshot"
            else "reported-testimony rows retained"
        ) + suffix
        cells = [
            cell.strip() for cell in match.group("cells").split("|") if cell.strip()
        ]
        assert len(cells) == len(cf.CANONICAL_SETS)
        for set_name, cell_text in zip(cf.CANONICAL_SETS, cells, strict=True):
            block = sets[set_name]["rows"]
            assert isinstance(block, list)
            row = next(
                candidate
                for candidate in block
                if candidate["cell"] == "R" and candidate["label"] == label
            )
            off_text, on_text = (part.strip() for part in cell_text.split("\u2192"))
            for column, stated_text, pair in (
                ("OFF", off_text, row["reconstructed_off"]),
                ("ON", on_text, row["on"]),
            ):
                computed = _render_figure(pair, display=row["display"])
                if stated_text != computed:
                    mismatches.append(
                        f"{set_name} {label} {column}: memo states {stated_text}, "
                        f"script computes {computed}"
                    )
    return mismatches


def _render_figure(pair: Sequence[int], *, display: str) -> str:
    """One §5 render figure, formatted the way the memo's table prints it."""

    num, den = pair
    if display == "mean":
        return f"{num / den:.2f}"
    share = (100 * num / den) if den else 0.0
    return "0%" if share == 0 else f"{share:.1f}%"


def test_the_memo_per_set_render_rows_are_the_scripts_own(
    full_payload: Mapping[str, object],
) -> None:
    """§5's per-set render rows must not sit on a different slate from §4.

    The pooled headline moved to the full eight; a per-set breakdown left on the
    withheld-lever leg would silently stop being a like-for-like comparison for
    the smoke and record audits. Every stated figure is re-derived here — the OFF
    half as well as the ON one.
    """

    sets = full_payload["sets"]
    assert isinstance(sets, dict)
    mismatches = _per_set_render_mismatches(_MEMO.read_text(encoding="utf-8"), sets)
    assert not mismatches, "\n".join(mismatches)


def test_a_perturbed_per_set_off_figure_is_caught(
    full_payload: Mapping[str, object],
) -> None:
    """The §5 gate bites on the OFF half, not only on the ON half."""

    sets = full_payload["sets"]
    assert isinstance(sets, dict)
    text = _MEMO.read_text(encoding="utf-8")
    perturbed = text.replace("| 51.13 \u2192 40.77 |", "| 51.14 \u2192 40.77 |", 1)
    assert perturbed != text, "the §5 render OFF figure moved — re-anchor this gate"
    mismatches = _per_set_render_mismatches(perturbed, sets)
    assert any("51.14" in line for line in mismatches), mismatches


def _check_cell(
    label: str,
    column: str,
    stated: str,
    computed: Sequence[int] | None,
    mismatches: list[str],
) -> None:
    """Compare one stated ``n/d`` (or an em-dash) against the computed pair."""

    if stated in {"—", "--", "n/a"}:
        if computed is not None:
            mismatches.append(
                f"{label} {column}: the memo states no reading but the script "
                f"computes {computed[0]}/{computed[1]}"
            )
        return
    match = _COUNTS.match(stated)
    if match is None:
        mismatches.append(f"{label} {column}: {stated!r} is not an n/d pair")
        return
    if computed is None:
        mismatches.append(
            f"{label} {column}: the memo states {stated} but the script computes "
            "no reading"
        )
        return
    pair = [int(match.group(1)), int(match.group(2))]
    if pair != list(computed):
        mismatches.append(
            f"{label} {column}: the memo states {stated} but the script computes "
            f"{computed[0]}/{computed[1]}"
        )


def test_a_perturbed_memo_row_is_caught(
    full_payload: Mapping[str, object],
) -> None:
    """The drift gate bites: one changed digit in the memo fails the pin."""

    text = _MEMO.read_text(encoding="utf-8")
    perturbed = text.replace("| 148/234 |", "| 149/234 |", 1)
    assert perturbed != text, "the I-6 pooled OFF row moved — re-anchor this gate"
    stated = _parse_pooled_rows(perturbed)
    pooled = full_payload["pooled"]
    assert isinstance(pooled, list)
    computed = {f"{row['cell']}|{row['label']}": row for row in pooled}
    mismatches: list[str] = []
    for label, (off_text, on_text) in stated.items():
        row = computed[label]
        _check_cell(label, "OFF", off_text, row["recorded_off"], mismatches)
        _check_cell(label, "ON", on_text, row["on"], mismatches)
    assert any("149/234" in line for line in mismatches), mismatches
