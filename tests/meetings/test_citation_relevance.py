"""The shared aboutness rule, and the agreement it makes structural.

``meetings/citation_relevance.py`` is ONE definition with two callers: the
recording-time gate (:func:`meetings.manager.guard_ballot_citation`, under
``citation_relevance_version``) and the deduction instrument's
``grade_citation_relevance``. This module pins the rule itself, the two walkers
that must agree about a dumped turn, the import direction that made the move
necessary, and -- the point of the whole exercise -- that the guard and the
grader cannot reach different verdicts about the same ballot.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

from experiments.fresh_deduction_instrument import (
    _every_string_in,
    grade_citation_relevance,
)
from meetings.citation_relevance import (
    citations_bear_on,
    cited_line_names,
    every_string_in,
    names_player,
    turn_bears_on,
)
from meetings.manager import (
    OFF_TARGET_CITATION_EJECT_MARKER,
    UNCITED_ZERO_FLAG_EJECT_MARKER,
    guard_ballot_citation,
)
from meetings.schemas import (
    AccusationClaim,
    ContradictionRef,
    MeetingTurn,
    SawVentObservation,
    VoteBallot,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_MODULE = _REPO_ROOT / "meetings" / "citation_relevance.py"


def _turn(
    *,
    turn_id: str = "m-1:turn-0",
    turn_index: int = 0,
    speaker: str = "p-1",
    free_text: str = "nothing to add.",
    claims: tuple[AccusationClaim, ...] = (),
    observations: tuple[SawVentObservation, ...] = (),
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=turn_id,
        turn_index=turn_index,
        speaker=speaker,
        turn_kind="opening",
        reply_to=None,
        free_text=free_text,
        claims=claims,
        observations=observations,
    )


class TestWholeTokenMatch:
    def test_a_longer_id_is_not_the_player_it_starts_with(self) -> None:
        # PLANTED: a substring match reads `p-10` as naming `p-1`. A ten-player
        # table is not the authorized roster, but a rule that cannot tell the
        # two apart is wrong wherever it is applied.
        assert names_player("tick 4: p-10 in MEDBAY.", "p-1") is False
        assert names_player("tick 4: p-1 in MEDBAY.", "p-1") is True

    def test_a_suffixed_id_is_not_the_player_it_starts_with(self) -> None:
        assert names_player("body-p-1-4 was found", "p-1") is False

    def test_punctuation_still_bounds_the_token(self) -> None:
        assert names_player("I accuse p-1.", "p-1") is True
        assert names_player("(p-1)", "p-1") is True


class TestTurnAboutness:
    def test_the_speakers_own_turn_bears_on_them(self) -> None:
        assert turn_bears_on(_turn(speaker="p-2", free_text="I was busy."), "p-2")

    def test_a_turn_naming_nobody_relevant_does_not(self) -> None:
        assert not turn_bears_on(
            _turn(speaker="p-1", free_text="p-3 was in ADMIN."), "p-2"
        )

    def test_a_name_reached_only_through_a_nested_claim_counts(self) -> None:
        """PLANTED: a field-by-field rule that read ``free_text`` alone misses it.

        The turn's prose names nobody; the accusation it carries names p-2. The
        dumped-structure walk is what finds it, and a later schema shape naming
        a player under a new key is found for the same reason.
        """

        turn = _turn(
            speaker="p-1",
            free_text="something is off about that account.",
            claims=(
                AccusationClaim(
                    type="accusation",
                    against="p-2",
                    reason="the timing does not work",
                    confidence=0.7,
                ),
            ),
        )
        assert "p-2" not in turn.free_text
        assert turn_bears_on(turn, "p-2")

    def test_a_name_reached_only_through_an_observation_counts(self) -> None:
        turn = _turn(
            speaker="p-1",
            free_text="I saw something in ENGINEERING.",
            observations=(
                SawVentObservation(
                    type="saw_vent", subject="p-2", room="ENGINEERING", tick=4
                ),
            ),
        )
        assert turn_bears_on(turn, "p-2")


class TestCitedLineRule:
    def test_the_line_is_the_unit_not_the_prompt(self) -> None:
        # PLANTED: a prompt-wide search calls this relevant. The id and the
        # name are in the same PROMPT and in different RECORDS.
        lines = [
            "[obs p-1:4:0] tick 4: p-3 left ELECTRICAL.",
            "[obs p-1:5:0] tick 5: p-2 in MEDBAY.",
        ]
        assert not cited_line_names(lines, citation="p-1:4:0", player="p-2")
        assert cited_line_names(lines, citation="p-1:5:0", player="p-2")

    def test_an_absent_citation_names_nobody(self) -> None:
        assert not cited_line_names(
            ["[obs p-1:5:0] tick 5: p-2 in MEDBAY."],
            citation="p-1:9:0",
            player="p-2",
        )


class TestTheTwoWalkersAgree:
    """The instrument keeps its own walker; the two must read a turn the same.

    ``experiments.fresh_deduction_instrument._every_string_in`` stays where it
    is because it also serves the held-out leak scan, which is outside the
    firewall interior. Two copies is the price of the import direction, so the
    equality is asserted rather than assumed.
    """

    def test_they_agree_on_a_dumped_meeting_turn(self) -> None:
        turn = _turn(
            speaker="p-1",
            free_text="p-3 was in ADMIN.",
            claims=(
                AccusationClaim(
                    type="accusation",
                    against="p-2",
                    reason="the timing does not work",
                    confidence=0.7,
                ),
            ),
            observations=(
                SawVentObservation(
                    type="saw_vent", subject="p-4", room="ENGINEERING", tick=4
                ),
            ),
        )
        dumped = turn.model_dump(mode="json")
        assert every_string_in(dumped) == _every_string_in(dumped)
        # Not vacuous: the walk reaches the nested names, not just the top row.
        assert "p-2" in every_string_in(dumped)
        assert "p-4" in every_string_in(dumped)


class TestTheImportDirection:
    """``meetings/`` may not import ``experiments/`` -- stated at this module.

    ``tests/test_firewall.py``'s closure scan is the gate that enforces it for
    every interior package. This case is the local statement of WHY this module
    exists: it would be a one-line import otherwise.
    """

    def test_the_module_imports_nothing_from_experiments(self) -> None:
        tree = ast.parse(_MODULE.read_text(encoding="utf-8"))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                imported.add(node.module.split(".")[0])
        assert "experiments" not in imported
        assert "engine" not in imported
        assert imported <= {"__future__", "re", "collections", "typing", "meetings"}


def _committed_meeting_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((_REPO_ROOT / "replays" / "samples").glob("*/*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("kind") == "meeting":
                rows.append(row)
    return rows


class TestGuardAndGraderCannotDisagree:
    """One rule, two callers, one verdict per ballot.

    The guard asks "may this EJECT stand?" and the grader asks "was the
    citation about the ejected player?". They coincide exactly where the
    primary outcome reads them: ``grade_privileged`` grades the ballots NAMING
    the ejected player, and on a naming ballot the ejected player IS that
    ballot's own target -- which is the subject the guard uses. So for a naming
    ballot the two questions have one answer, and this case walks every
    committed ballot to say so on the same turns and the same lines.
    """

    def test_every_committed_ballot_gets_one_verdict(self) -> None:
        compared = 0
        coerced = 0
        for row in _committed_meeting_rows():
            turns = tuple(
                MeetingTurn.model_validate(turn) for turn in row["transcript"]["turns"]
            )
            flags = tuple(
                ContradictionRef.model_validate(flag) for flag in row["contradictions"]
            )
            prompts: dict[str, list[str]] = {}
            for call in row["llm_calls"]:
                agent = call.get("agent_id")
                if isinstance(agent, str) and call.get("prompt"):
                    prompts.setdefault(agent, []).append(call["prompt"])
            for payload in row["ballots"]:
                ballot = VoteBallot.model_validate(payload)
                if ballot.target == "SKIP":
                    continue
                lines = [
                    line
                    for prompt in prompts.get(ballot.voter, ())
                    for line in prompt.splitlines()
                ]
                grade = grade_citation_relevance(
                    [ballot],
                    subject=ballot.target,
                    turns=turns,
                    prompts_by_agent={
                        ballot.voter: tuple(prompts.get(ballot.voter, ()))
                    },
                )[0]
                guarded = guard_ballot_citation(
                    ballot=ballot,
                    contradictions=flags,
                    citation_relevance_version=1,
                    turns=turns,
                    prompt_lines=lines,
                )
                compared += 1
                # The guard adds two things the grader does not have: the SKIP
                # short-circuit (excluded above) and the flag exemption. Outside
                # the exemption the two verdicts are the same verdict.
                if ballot.target in {
                    subject for flag in flags for subject in flag.subjects
                }:
                    assert guarded is ballot
                    continue
                # The MARKER is what a coercion is asserted by, not the typed
                # reason: a recorded ballot may already carry an earlier
                # rewrite's reason, which `ballot_target_rewrite_provenance`
                # leaves in place while every rewrite still stacks its marker.
                if grade.verdict == "off_target":
                    coerced += 1
                    assert guarded.target == "SKIP"
                    assert guarded.rationale_text.startswith(
                        OFF_TARGET_CITATION_EJECT_MARKER.format(target=ballot.target)
                    )
                elif grade.verdict == "relevant":
                    assert guarded is ballot
                else:  # uncited -- the other half of the same gate
                    assert guarded.target == "SKIP"
                    assert guarded.rationale_text.startswith(
                        UNCITED_ZERO_FLAG_EJECT_MARKER.format(target=ballot.target)
                    )
        assert compared == 578, compared
        # PLANTED would be silent on a set the rule never bites: it bites here.
        assert coerced > 0, coerced


class TestTheCompositionIsShared:
    def test_an_uncited_ballot_is_vacuously_relevant(self) -> None:
        """Aboutness is a test of what a citation says, so no citation passes it.

        The uncited class is the OTHER half of the same gate, and letting this
        composition answer ``False`` would make the two halves fight over one
        ballot.
        """

        assert citations_bear_on(
            cited_turn_id=None,
            cited_observation_id=None,
            subject="p-2",
            turns_by_id={},
            lines=[],
        )

    def test_a_cited_turn_that_resolves_to_nothing_is_not_relevant(self) -> None:
        assert not citations_bear_on(
            cited_turn_id="m-1:turn-9",
            cited_observation_id=None,
            subject="p-2",
            turns_by_id={},
            lines=[],
        )

    def test_both_channels_must_bear_on_the_subject(self) -> None:
        turn = _turn(speaker="p-2")
        assert not citations_bear_on(
            cited_turn_id="m-1:turn-0",
            cited_observation_id="p-1:4:0",
            subject="p-2",
            turns_by_id={"m-1:turn-0": turn},
            lines=["[obs p-1:4:0] tick 4: p-3 left ELECTRICAL."],
        )
        assert citations_bear_on(
            cited_turn_id="m-1:turn-0",
            cited_observation_id="p-1:4:0",
            subject="p-2",
            turns_by_id={"m-1:turn-0": turn},
            lines=["[obs p-1:4:0] tick 4: p-2 left ELECTRICAL."],
        )
