"""The shared aboutness rule, and the agreement it makes structural.

``meetings/citation_relevance.py`` is ONE definition with two callers: the
recording-time labeller (:func:`meetings.manager.label_ballot_grounding`, which
asks it unconditionally since ruling D6 of 2026-09-19 retired the
``citation_relevance_version`` lever) and the deduction instrument's
``grade_citation_relevance``. This module pins the rule itself, the two walkers
that must agree about a dumped turn, the import direction that made the move
necessary, and -- the point of the whole exercise -- that the labeller and the
grader cannot reach different verdicts about the same ballot.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any

from experiments.fresh_deduction_instrument import (
    _every_string_in,
    grade_citation_relevance,
)
from meetings.citation_relevance import (
    carries_citation,
    citations_bear_on,
    citations_bear_on_any,
    cited_line_names,
    every_string_in,
    names_player,
    turn_bears_on,
)
from meetings.manager import label_ballot_grounding
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

    def test_a_longer_observation_id_is_not_the_citation_it_starts_with(
        self,
    ) -> None:
        # PLANTED, and the same defect as the player half: an observation id is
        # `{agent}:{tick}:{seq}`, so a substring match reads the line of
        # `p-1:4:10` as carrying a citation of `p-1:4:1`. That is the voter's
        # TENTH observation of tick 4 answering for its FIRST.
        assert carries_citation("[obs p-1:4:10] tick 4: p-2 vented.", "p-1:4:1") is (
            False
        )
        assert carries_citation("[obs p-1:4:1] tick 4: p-2 vented.", "p-1:4:1") is True

    def test_the_citation_token_is_bounded_on_both_sides(self) -> None:
        # The lookbehind too, for the same reason the player rule has one: an
        # id that ENDS with the cited id is not the cited id. Today's agent ids
        # cannot build that collision, and a boundary rule that only holds on
        # one side is wrong wherever it is applied.
        assert carries_citation("[obs xp-1:4:1] tick 4: p-2 vented.", "p-1:4:1") is (
            False
        )
        # A bare id with no wrapper still matches: the rule is the id, not the
        # `[obs ...]` render dressing.
        assert carries_citation("cited p-1:4:1, which I saw.", "p-1:4:1") is True


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

    def test_a_longer_id_does_not_answer_for_a_shorter_citation(self) -> None:
        # PLANTED against the substring rule this module shipped with: the
        # cited record is about p-3, and the only line naming p-2 belongs to a
        # DIFFERENT observation whose id merely starts with the cited one. A
        # substring test answers True here, which is the gate failing OPEN on
        # the exact class it exists to close.
        lines = [
            "[obs p-1:4:1] tick 4: p-3 left ELECTRICAL.",
            "[obs p-1:4:10] tick 4: p-2 vented in MEDBAY.",
        ]
        assert not cited_line_names(lines, citation="p-1:4:1", player="p-2")
        # The collision is one-directional: the longer id's own citation still
        # reads its own line.
        assert cited_line_names(lines, citation="p-1:4:10", player="p-2")
        assert cited_line_names(lines, citation="p-1:4:1", player="p-3")


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


#: The rendered observation handle, as ``agents/memory/store.py`` folds it in.
_RENDERED_OBSERVATION_ID = re.compile(r"\[obs ([0-9A-Za-z_:-]+)\]")


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

    The labeller asks "what basis does this EJECT carry?" and the grader asks
    "was the citation about the ejected player?". They coincide exactly where
    the primary outcome reads them: ``grade_privileged`` grades the ballots
    NAMING the ejected player, and on a naming ballot the ejected player IS
    that ballot's own target -- which is the subject the labeller uses. So for
    a naming ballot the two questions have one answer, and this case walks
    every committed ballot to say so on the same turns and the same lines.

    Since ruling D6 the labeller writes a LABEL where the retired gate wrote a
    coercion, so the agreement is now read off ``grounding_label`` and the
    ballot's ``target`` is asserted unchanged on every row -- which is the
    stronger statement, and the one this card exists to make.
    """

    def test_every_committed_ballot_gets_one_verdict(self) -> None:
        compared = 0
        off_target = 0
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
                labelled = label_ballot_grounding(
                    ballot=ballot,
                    contradictions=flags,
                    turns=turns,
                    prompt_lines=lines,
                )
                compared += 1
                # The ruling, asserted on every committed EJECT: whatever the
                # label says, the recorded target does not move, and the label
                # is the only field the labeller writes. The recorded ballot
                # carries its recording-time label, so both sides drop it.
                assert labelled.target == ballot.target
                assert labelled.model_copy(
                    update={"grounding_label": None}
                ) == ballot.model_copy(update={"grounding_label": None})
                # A ballot the layer already rewrote is not the voter's, so it
                # is not assessed and the grader's verdict does not apply.
                if ballot.guard_rewrite_reason is not None:
                    assert labelled.grounding_label == "not_assessed"
                    continue
                if grade.verdict == "off_target":
                    off_target += 1
                    assert labelled.grounding_label == "off_target"
                elif grade.verdict == "relevant":
                    assert labelled.grounding_label == "supported"
                else:
                    # The grader's ONE uncited verdict splits three ways here,
                    # by what the ballot holds instead of a citation.
                    assert labelled.grounding_label in {
                        "flag_only",
                        "none_held",
                        "uncited",
                    }
        assert compared == 545, compared  # was 578 on baseline 8
        # PLANTED would be silent on a set the rule never bites: it bites here.
        assert off_target > 0, off_target

    def test_a_prefix_colliding_citation_is_off_target_for_both_callers(self) -> None:
        """One rule, so a WRONG rule is wrong in both callers and they agree.

        The case above pins agreement and cannot pin correctness: the shared
        substring rule this module shipped with answered ``relevant`` in both
        callers on this ballot. So the verdict itself is stated here, on both
        callers, over the one surface the rule can be fooled by -- a cited id
        that is a strict PREFIX of another id rendered in the same prompt.
        """

        ballot = VoteBallot(
            voter="p-1",
            target="p-2",
            confidence=0.8,
            primary_reason_id=None,
            primary_reason_observation_id="p-1:4:1",
            considered_alternatives=(),
            rationale_text="they vented.",
        )
        prompt = "\n".join(
            [
                "- [obs p-1:4:1] tick 4: p-3 left ELECTRICAL.",
                "- [obs p-1:4:10] tick 4: p-2 vented in MEDBAY.",
            ]
        )
        labelled = label_ballot_grounding(
            ballot=ballot,
            contradictions=(),
            prompt_lines=prompt.splitlines(),
        )
        assert labelled.grounding_label == "off_target"
        # The label is the WHOLE consequence: the vote still stands as cast.
        assert labelled.target == "p-2"
        assert labelled.guard_rewrite_reason is None
        grade = grade_citation_relevance(
            [ballot],
            subject="p-2",
            turns=(),
            prompts_by_agent={"p-1": (prompt,)},
        )[0]
        assert grade.verdict == "off_target"
        # And the ballot that really does cite the vent line still stands, in
        # both callers: the fix is a boundary, not a blanket refusal.
        on_target = ballot.model_copy(
            update={"primary_reason_observation_id": "p-1:4:10"}
        )
        assert (
            label_ballot_grounding(
                ballot=on_target,
                contradictions=(),
                prompt_lines=prompt.splitlines(),
            ).grounding_label
            == "supported"
        )
        assert (
            grade_citation_relevance(
                [on_target],
                subject="p-2",
                turns=(),
                prompts_by_agent={"p-1": (prompt,)},
            )[0].verdict
            == "relevant"
        )

    def test_the_collision_is_reachable_on_committed_bytes(self) -> None:
        """The case above is not hypothetical: committed prompts render it.

        A voter's tenth observation within one tick is what mints the pair, and
        the committed sample prompts hold 212 of them (244 on baseline 8). The
        count is pinned the way this module pins ``compared``: over bytes that
        move only when a card deliberately moves them.
        """

        colliding = 0
        for row in _committed_meeting_rows():
            for call in row["llm_calls"]:
                prompt = call.get("prompt")
                if not isinstance(prompt, str) or not prompt:
                    continue
                ids = sorted(set(_RENDERED_OBSERVATION_ID.findall(prompt)))
                if any(
                    other != one and other.startswith(one)
                    for one in ids
                    for other in ids
                ):
                    colliding += 1
        assert colliding == 212, colliding  # was 244 on baseline 8


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

    def test_the_one_subject_case_is_the_pooled_rule(self) -> None:
        """ONE definition: the single-subject call IS the pooled call.

        Not "agrees with" -- the same answer over every shape this module can
        build, so a future edit to either cannot open a gap between the
        grader's single-subject question and the labeller's pooled one.
        """

        turn = _turn(speaker="p-2")
        lines = ["[obs p-1:4:0] tick 4: p-2 left ELECTRICAL."]
        for cited_turn_id in (None, "m-1:turn-0", "m-1:turn-9"):
            for cited_observation_id in (None, "p-1:4:0", "p-1:4:9"):
                for subject in ("p-2", "p-3"):
                    assert citations_bear_on(
                        cited_turn_id=cited_turn_id,
                        cited_observation_id=cited_observation_id,
                        subject=subject,
                        turns_by_id={"m-1:turn-0": turn},
                        lines=lines,
                    ) == citations_bear_on_any(
                        cited_turn_id=cited_turn_id,
                        cited_observation_id=cited_observation_id,
                        subjects=(subject,),
                        turns_by_id={"m-1:turn-0": turn},
                        lines=lines,
                    )

    def test_a_pool_is_satisfied_by_any_one_member(self) -> None:
        """The SKIP's rule: a citation about one weighed player is a basis.

        And its floor -- a pool holding nobody the citation is about answers
        ``False``, which is what makes ``off_target`` reachable for a SKIP.
        """

        lines = ["[obs p-1:4:0] tick 4: p-2 left ELECTRICAL."]
        assert citations_bear_on_any(
            cited_turn_id=None,
            cited_observation_id="p-1:4:0",
            subjects=("p-4", "p-2"),
            turns_by_id={},
            lines=lines,
        )
        assert not citations_bear_on_any(
            cited_turn_id=None,
            cited_observation_id="p-1:4:0",
            subjects=("p-4", "p-5"),
            turns_by_id={},
            lines=lines,
        )

    def test_an_empty_pool_answers_before_it_is_read(self) -> None:
        """Vacuity beats the pool: an uncited ballot is relevant to everyone.

        The order matters. An uncited ballot answers ``True`` against an empty
        pool (the vacuous branch runs first), while a CITED one answers
        ``False`` -- there is no subject for it to bear on. Production cannot
        reach the second: a vote is collected only while a candidate lives.
        """

        assert citations_bear_on_any(
            cited_turn_id=None,
            cited_observation_id=None,
            subjects=(),
            turns_by_id={},
            lines=[],
        )
        assert not citations_bear_on_any(
            cited_turn_id=None,
            cited_observation_id="p-1:4:0",
            subjects=(),
            turns_by_id={},
            lines=["[obs p-1:4:0] tick 4: p-2 left ELECTRICAL."],
        )
