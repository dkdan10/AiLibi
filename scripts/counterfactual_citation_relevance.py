"""Price the relevance-aware citation guard on an archived run, offline.

Counts only. Reads one archived run directory — its per-unit replays and its
final checkpoint — and prints aggregates: no prompt, no prefix, no transcript,
no ballot text and no seed-level text reaches the output, which is what lets it
be run against a band that is now development data without publishing a byte of
it. It makes no provider call, opens no held-out prefix, writes nothing into the
directory it reads, and imports the rule it prices rather than restating it.

    .venv/bin/python scripts/counterfactual_citation_relevance.py \
      audits/deduction-candidate/run-2026-09-16

Three tables, in the shape ``audits/deduction-candidate/run-2026-09-16/
reconcile.py`` established:

* **grading** — every archived ballot re-graded by the committed
  ``grade_citation_relevance``, and the naming ballots (those naming the player
  the meeting ejected) split by verdict. This is the sizing figure: how much of
  the primary outcome relevance rather than presence was deciding.
* **reach** — which recorded EJECT ballots ``guard_ballot_citation`` would
  coerce with ``citation_relevance_version=1``, split by the voter's role. The
  class is counted off the MARKER STACK (``ballot_rewrites_that_fired``), never
  off ``VoteBallot.guard_rewrite_reason``: a ballot already re-aimed by
  ``under_gate_redirect`` keeps that reason in the typed field when the citation
  gate then coerces it, and the archive contains exactly that ballot.
* **counterfactual** — the ejection table before and after, per arm: ejections,
  role-correct, wrongful, and the paired ``supported_correct_ejection`` cells,
  re-tallied by the committed ``tally_ballots`` at each meeting's own recorded
  ``skip_confidence_threshold``.

The re-tally is a counterfactual over RECORDED ballots, not a re-run: the model
is never asked what it would have said into a meeting that went differently, so
everything downstream of the coerced vote is the archive's. Coercion only ever
removes an EJECT vote and adds a SKIP one, so the re-tally can LOSE an ejection
and, on this roster, cannot invent one — asserted here rather than argued, by
checking that every after-ejection was a before-ejection.

Roles come from each replay's own tick rows: the actor of the scripted kill is
that seed's impostor, the recovery ``reconcile.py`` uses, sound because only an
impostor kills. The before-column is checked against the archive's own
checkpoint before the after-column is believed.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from types import MappingProxyType
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from experiments.fresh_deduction_instrument import (  # noqa: E402
    DefaultedAttempts,
    TransportAttempts,
    UnitRecord,
    ballot_rewrites_that_fired,
    grade_citation_relevance,
    grade_privileged,
    grade_supported,
)
from meetings.manager import guard_ballot_citation  # noqa: E402
from meetings.schemas import (  # noqa: E402
    ContradictionRef,
    MeetingTurn,
    VoteBallot,
)
from meetings.voting import tally_ballots  # noqa: E402

_SKIP = "SKIP"


class CounterfactualError(RuntimeError):
    """The archive does not support the counterfactual it is being asked for."""


def _rows(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _impostor_of(rows: Sequence[Mapping[str, Any]]) -> str:
    """This seed's impostor: the actor of the scripted kill in its tick rows."""

    for row in rows:
        if row["kind"] != "tick":
            continue
        for action in row["actions"]:
            if action.get("type") == "kill":
                actor = action.get("actor")
                if isinstance(actor, str):
                    return actor
    raise CounterfactualError("a unit with no scripted kill has no recoverable roles")


def _unit_record(
    *,
    seed: int,
    arm: str,
    meeting: Mapping[str, Any],
    impostor: str,
    ballots: Sequence[VoteBallot],
    ejected: str | None,
    turns: Sequence[MeetingTurn],
    prompts: Mapping[str, tuple[str, ...]],
) -> UnitRecord:
    """The grader's input, built from archived bytes.

    Only the fields the two graders read carry meaning here; the rest are the
    empty shapes of a record that is not being run, and nothing in this script
    puts one back into a run path.
    """

    players = {ballot.voter for ballot in ballots} | {turn.speaker for turn in turns}
    if ejected is not None:
        players.add(ejected)
    return UnitRecord(
        seed=seed,
        arm=arm,  # type: ignore[arg-type]
        meeting_id=str(meeting["meeting_id"]),
        outcome=str(meeting["outcome"]),
        ejected_player_id=ejected,
        ballots=tuple(ballots),
        turns=tuple(turns),
        roles=MappingProxyType(
            {
                player: ("IMPOSTOR" if player == impostor else "CREWMATE")
                for player in sorted(players)
            }
        ),
        prompts_by_agent=MappingProxyType(dict(prompts)),
        calls=(),
        game_outcome="",
        recorded_temporal_version=None,
        recorded_experiment_config=None,
        prompt_versions=MappingProxyType({}),
        defaults=DefaultedAttempts(),
        transport_attempts=TransportAttempts(),
    )


def _graded(record: UnitRecord) -> tuple[bool, bool, bool]:
    """``(ejected, role_correct, supported_correct_ejection)`` for one unit."""

    privileged = grade_privileged(
        record,
        supported=grade_supported(
            record.ballots, prompts_by_agent=record.prompts_by_agent
        ),
    )
    return (
        privileged.ejected_player_id is not None,
        privileged.role_correct,
        privileged.supported_correct_ejection,
    )


def _empty_arm() -> dict[str, Any]:
    return {
        "units": 0,
        "recorded_ballots": 0,
        "recorded_ejects": 0,
        "naming_ballots": 0,
        "naming_verdicts": Counter(),
        "naming_off_target_by_role": Counter(),
        "reached": 0,
        "reached_by_role": Counter(),
        "before": Counter(),
        "after": Counter(),
        "ejection_moved_units": 0,
        "invented_ejections": 0,
    }


def main(directory: Path) -> int:
    checkpoint = json.loads((directory / "checkpoint-final.json").read_text())
    recorded = {
        (str(unit["arm"]), int(unit["seed"])): unit for unit in checkpoint["units"]
    }
    arms: dict[str, dict[str, Any]] = {}

    for path in sorted(directory.glob("*.jsonl")):
        arm_name, _, seed_text = path.stem.partition("-seed-")
        arm = arms.setdefault(arm_name, _empty_arm())
        seed = int(seed_text)
        rows = _rows(path)
        meeting = next(r for r in rows if r["kind"].startswith("meeting"))
        impostor = _impostor_of(rows)
        turns = tuple(
            MeetingTurn.model_validate(turn) for turn in meeting["transcript"]["turns"]
        )
        flags = tuple(
            ContradictionRef.model_validate(flag) for flag in meeting["contradictions"]
        )
        ballots = tuple(VoteBallot.model_validate(b) for b in meeting["ballots"])
        threshold = float(meeting["skip_confidence_threshold"])

        # Every prompt the voter received (the grader's surface) and the one
        # that carried its ballot (the guard's). A call whose completion parses
        # with a ``target`` is a ballot; one with a ``speaker`` is a turn.
        prompts: dict[str, list[str]] = {}
        ballot_prompt: dict[str, list[str]] = {}
        for call in meeting["llm_calls"]:
            agent = call.get("agent_id")
            if not isinstance(agent, str) or not call.get("prompt"):
                continue
            prompts.setdefault(agent, []).append(call["prompt"])
            try:
                payload = json.loads(call["response_text"])
            except (TypeError, ValueError):
                continue
            if isinstance(payload, dict) and "target" in payload:
                ballot_prompt.setdefault(agent, []).append(call["prompt"])
        frozen_prompts = {agent: tuple(texts) for agent, texts in prompts.items()}

        arm["units"] += 1
        arm["recorded_ballots"] += len(ballots)
        arm["recorded_ejects"] += sum(1 for b in ballots if b.target != _SKIP)

        ejected_before = meeting["ejected_player_id"]
        before_record = _unit_record(
            seed=seed,
            arm=arm_name,
            meeting=meeting,
            impostor=impostor,
            ballots=ballots,
            ejected=ejected_before,
            turns=turns,
            prompts=frozen_prompts,
        )
        before = _graded(before_record)
        archived = recorded.get((arm_name, seed))
        if archived is not None and (
            bool(archived["role_correct"]) != before[1]
            or bool(archived["supported_correct_ejection"]) != before[2]
        ):
            raise CounterfactualError(
                f"the re-grade of {arm_name} seed {seed} disagrees with the "
                "archive's own checkpoint; the before-column is not the record's"
            )

        # The naming ballots, graded against the ejected player -- the cells the
        # primary outcome's third conjunct reads.
        if ejected_before is not None:
            naming = [b for b in ballots if b.target == ejected_before]
            for grade in grade_citation_relevance(
                naming,
                subject=ejected_before,
                turns=turns,
                prompts_by_agent=frozen_prompts,
            ):
                arm["naming_ballots"] += 1
                arm["naming_verdicts"][grade.verdict] += 1
                if grade.verdict == "off_target":
                    role = "IMPOSTOR" if grade.voter == impostor else "CREWMATE"
                    arm["naming_off_target_by_role"][role] += 1

        # The rule, applied to the recorded ballots.
        after_ballots: list[VoteBallot] = []
        for ballot in ballots:
            guarded = guard_ballot_citation(
                ballot=ballot,
                contradictions=flags,
                citation_relevance_version=1,
                turns=turns,
                prompt_lines=[
                    line
                    for prompt in ballot_prompt.get(ballot.voter, ())
                    for line in prompt.splitlines()
                ],
            )
            if "off_target_coerced" in ballot_rewrites_that_fired(guarded):
                arm["reached"] += 1
                arm["reached_by_role"][
                    "IMPOSTOR" if ballot.voter == impostor else "CREWMATE"
                ] += 1
            after_ballots.append(guarded)

        _, ejected_after = tally_ballots(
            after_ballots, skip_confidence_threshold=threshold
        )
        if ejected_after is not None and ejected_after != ejected_before:
            arm["invented_ejections"] += 1
        if ejected_after != ejected_before:
            arm["ejection_moved_units"] += 1
        after = _graded(
            _unit_record(
                seed=seed,
                arm=arm_name,
                meeting=meeting,
                impostor=impostor,
                ballots=after_ballots,
                ejected=ejected_after,
                turns=turns,
                prompts=frozen_prompts,
            )
        )
        for column, cells in (("before", before), ("after", after)):
            arm[column]["ejections"] += int(cells[0])
            arm[column]["role_correct"] += int(cells[1])
            arm[column]["wrongful"] += int(cells[0] and not cells[1])
            arm[column]["supported_correct_ejection"] += int(cells[2])

    payload = {
        "source": directory.name,
        "rule": (
            "guard_ballot_citation(citation_relevance_version=1): an EJECT whose "
            "citations are present but do not bear on its own target takes the "
            "uncited path -- exempt when the target is contradiction-flagged, "
            "coerced to SKIP otherwise, under off_target_coerced."
        ),
        "arms": {
            name: {
                "units": arm["units"],
                "recorded_ballots": arm["recorded_ballots"],
                "recorded_ejects": arm["recorded_ejects"],
                "naming_ballots": arm["naming_ballots"],
                "naming_verdicts": dict(sorted(arm["naming_verdicts"].items())),
                "naming_off_target_by_voter_role": dict(
                    sorted(arm["naming_off_target_by_role"].items())
                ),
                "ballots_reached_by_the_rule": arm["reached"],
                "ballots_reached_by_voter_role": dict(
                    sorted(arm["reached_by_role"].items())
                ),
                "before": dict(sorted(arm["before"].items())),
                "after": dict(sorted(arm["after"].items())),
                "units_whose_ejection_moved": arm["ejection_moved_units"],
                "ejections_invented": arm["invented_ejections"],
            }
            for name, arm in sorted(arms.items())
        },
    }
    invented = sum(a["ejections_invented"] for a in payload["arms"].values())  # type: ignore[union-attr]
    if invented:
        raise CounterfactualError(
            f"{invented} unit(s) gained an ejection the archive did not have; "
            "coercion removes an EJECT vote and must never create one"
        )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(Path(sys.argv[1])))
