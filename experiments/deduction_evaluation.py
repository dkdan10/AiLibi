"""Compare recorded deduction mechanisms without claiming scripted model quality."""

from __future__ import annotations

import hashlib
import json
import platform
import argparse
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

from api.replay_loader import ReplayLoader
from eval.balance_eval import load_tournament_report
from eval.report_schema import GameCostSummary, GameProvenance
from experiments.deduction_scenarios import (
    ScenarioCapture,
    ScenarioCase,
    ScenarioDefinition,
    ScriptedDeductionProvider,
    run_case,
    scenario_definition,
)
from orchestrator.experiment_config import (
    RecordedExperimentConfig,
    normalize_experiment_config,
)
from orchestrator.replay import (
    CompletionStatus,
    ReplayEntry,
    WinnerSide,
    read_all_entries,
)


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ComparisonArm(_Frozen):
    name: str
    temporal_version: Literal[1, 2] | None
    experiment_config: RecordedExperimentConfig


def comparison_arms() -> tuple[ComparisonArm, ...]:
    """Keep one repaired-clock reference for independent meeting comparisons."""
    baseline = ComparisonArm(
        name="legacy_reference",
        temporal_version=None,
        experiment_config=RecordedExperimentConfig(),
    )
    variants: tuple[tuple[str, bool, bool, bool], ...] = (
        ("repaired_clock", False, False, False),
        ("common_accounts", True, False, False),
        ("attributed_testimony", False, True, False),
        ("combined_accounts", True, True, False),
        ("combined_with_reply", True, True, True),
    )
    return (
        baseline,
        *(
            ComparisonArm(
                name=name,
                temporal_version=2,
                experiment_config=RecordedExperimentConfig(
                    format_version=2,
                    evidence_reasoning_version=2,
                    public_account_version=1 if accounts else None,
                    attributed_testimony_version=1 if testimony else None,
                    bounded_rebuttal_version=1 if reply else None,
                ),
            )
            for name, accounts, testimony, reply in variants
        ),
    )


def scenario_cases() -> tuple[ScenarioCase, ...]:
    return (
        "honest",
        "impossible_account",
        "insufficient_evidence",
        "already_known_dead",
        "witnessed_kill",
        "witnessed_vent",
        "late_accusation",
    )


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def source_hashes(root: Path) -> dict[str, str]:
    """Bind shipping code, templates, scenario inputs, map and dependency locks."""
    packages = (
        "engine",
        "observation",
        "agents",
        "meetings",
        "llm",
        "orchestrator",
        "eval",
        "api",
        "experiments",
        "maps",
    )
    suffixes = {".py", ".j2", ".json", ".yaml", ".yml"}
    paths = {
        path
        for package in packages
        for path in (root / package).rglob("*")
        if path.is_file() and path.suffix in suffixes
    }
    paths.update(root / name for name in ("pyproject.toml", "uv.lock"))
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(paths)
    }


class CaseMeasurement(_Frozen):
    arm: str
    case: ScenarioCase
    replay_ref: str
    definition_sha256: str
    trajectory_sha256: str
    reader_projection_sha256: str
    memory_projection_sha256: str
    provenance: GameProvenance
    completion_status: CompletionStatus
    outcome_verified: bool
    winner: WinnerSide | None
    cost: GameCostSummary
    prompt_versions: Mapping[str, str]
    meetings: int
    calls: int
    action_counts: Mapping[str, int]
    action_dispositions: Mapping[str, int]
    perspective_observation_counts: Mapping[str, int]
    firsthand_kills: int
    firsthand_vents: int
    public_account_counts: Mapping[str, int]
    accusation_count: int
    reply_turns: int
    role_proof_flags: int
    ballots: int
    voluntary_skips: int
    rewritten_ballots: int
    correct_ejections: int
    wrongful_ejections: int
    own_evidence_context: Mapping[str, tuple[str, ...]]


def validate_channels(case: ScenarioCase, *, kills: int, vents: int) -> None:
    """Reject a mislabeled direct-proof control or contaminated deduction case."""
    if case == "witnessed_kill":
        if kills < 1 or vents:
            raise ValueError(
                "witnessed-kill control lacks its expected evidence channel"
            )
    elif case == "witnessed_vent":
        if vents < 1 or kills:
            raise ValueError(
                "witnessed-vent control lacks its expected evidence channel"
            )
    elif kills or vents:
        raise ValueError("deduction case contains a firsthand kill or vent observation")


def measure_capture(
    capture: ScenarioCapture, *, arm: ComparisonArm, output_dir: Path
) -> CaseMeasurement:
    """Reconstruct real records; never substitute authored claims for observations."""
    if not isinstance(capture.provider, ScriptedDeductionProvider):
        raise ValueError("offline mechanics require the scripted deduction provider")
    directory = capture.replay_path.parent
    roster = {
        "num_players": capture.definition.num_players,
        "num_impostors": capture.definition.num_impostors,
        "tasks_per_crewmate": capture.definition.tasks_per_crewmate,
    }
    roster_path = directory / "roster.json"
    roster_bytes = (json.dumps(roster, sort_keys=True) + "\n").encode()
    try:
        with roster_path.open("xb") as stream:
            stream.write(roster_bytes)
    except FileExistsError:
        if roster_path.read_bytes() != roster_bytes:
            raise ValueError(
                "existing scenario roster does not match captured inputs"
            ) from None
    roles = {
        pid: player.role for pid, player in capture.result.final_state.players.items()
    }
    report = load_tournament_report(directory, roles_by_seed={1: roles}).games[0]
    loader = ReplayLoader(directory)
    replay = loader.load_replay(report.game_id)
    expected = normalize_experiment_config(arm.experiment_config)
    if (
        report.agent_factory_kind != "custom"
        or report.experiment_config != expected
        or replay.metadata.agent_factory_kind != "custom"
        or (
            replay.metadata.experiment_config.model_dump()
            if replay.metadata.experiment_config
            else None
        )
        != (expected.model_dump() if expected else None)
    ):
        raise ValueError(
            "scenario recording identity disagrees with its comparison arm"
        )
    if not report.outcome_verified or not replay.metadata.outcome_verified:
        raise ValueError(
            "scenario did not produce a strictly verified completed outcome"
        )
    if any(
        call.model != "scripted-deduction-control"
        for meeting in report.meetings
        for call in meeting.llm_calls
    ):
        raise ValueError("scenario contains an unexpected provider or fallback")
    memories = {
        f"{meeting.meeting_id}/{player}": loader.get_meeting_memory(
            report.game_id, meeting.meeting_id, player
        )
        for meeting in report.meetings
        for player in roles
        if any(ballot.voter == player for ballot in meeting.ballots)
    }
    for name, memory in memories.items():
        player = name.rsplit("/", 1)[1]
        if not any(
            agent == player and memory.rendered_memory_text in prompt
            for agent, prompt in capture.provider.prompts
        ):
            raise ValueError(
                "reconstructed meeting memory differs from live provider input"
            )
    entries = read_all_entries(capture.replay_path)
    ticks = [row for row in entries if isinstance(row, ReplayEntry)]
    if any(row.temporal_observation_version != arm.temporal_version for row in ticks):
        raise ValueError("scenario clock version disagrees with its comparison arm")
    actions: Counter[str] = Counter(
        str(action["type"]) for row in ticks for action in row.actions
    )
    dispositions: Counter[str] = Counter(
        disposition for row in ticks for disposition in row.action_dispositions or ()
    )
    observations: Counter[str] = Counter()
    for agent in capture.agents.values():
        for event in agent.memory.episodic.recent(since_tick=0):
            if event.provenance != "observed":
                continue
            kind = event.type
            if kind == "saw_player" and event.payload.get("action") in ("kill", "vent"):
                kind = "witnessed_" + str(event.payload["action"])
            observations[kind] += 1
    kills, vents = observations["witnessed_kill"], observations["witnessed_vent"]
    validate_channels(capture.definition.case, kills=kills, vents=vents)
    turns = [turn for meeting in report.meetings for turn in meeting.transcript.turns]
    ballots = [ballot for meeting in replay.meetings for ballot in meeting.ballots]
    ejected = [
        meeting.ejected_player_id
        for meeting in report.meetings
        if meeting.ejected_player_id is not None
    ]
    return CaseMeasurement(
        arm=arm.name,
        case=capture.definition.case,
        replay_ref=str(capture.replay_path.relative_to(output_dir)),
        definition_sha256=_digest(capture.definition.model_dump(mode="json")),
        trajectory_sha256=_digest(
            [
                {
                    "tick": row.tick,
                    "actions": row.actions,
                    "dispositions": row.action_dispositions,
                    "state_hash": row.state_hash,
                }
                for row in ticks
            ]
        ),
        reader_projection_sha256=_digest(
            replay.model_dump(mode="json", exclude={"metadata": {"created_at"}})
        ),
        memory_projection_sha256=_digest(
            {key: value.model_dump(mode="json") for key, value in memories.items()}
        ),
        provenance=report.recorded_provenance(),
        completion_status=report.completion_status,
        outcome_verified=report.outcome_verified,
        winner=report.winner,
        cost=report.cost,
        prompt_versions=report.prompt_versions,
        meetings=len(report.meetings),
        calls=sum(len(meeting.llm_calls) for meeting in report.meetings),
        action_counts=dict(sorted(actions.items())),
        action_dispositions=dict(sorted(dispositions.items())),
        perspective_observation_counts=dict(sorted(observations.items())),
        firsthand_kills=kills,
        firsthand_vents=vents,
        public_account_counts=dict(
            sorted(
                Counter(
                    observation.type
                    for turn in turns
                    for observation in turn.observations
                ).items()
            )
        ),
        accusation_count=sum(
            claim.type == "accusation" for turn in turns for claim in turn.claims
        ),
        reply_turns=sum(turn.turn_kind == "reply" for turn in turns),
        role_proof_flags=sum(
            flag.category == "role_proof"
            for meeting in replay.meetings
            for flag in meeting.contradictions
        ),
        ballots=len(ballots),
        voluntary_skips=sum(
            ballot.target == "SKIP" and not ballot.rewrite_reasons for ballot in ballots
        ),
        rewritten_ballots=sum(bool(ballot.rewrite_reasons) for ballot in ballots),
        correct_ejections=sum(roles[player] == "IMPOSTOR" for player in ejected),
        wrongful_ejections=sum(roles[player] == "CREWMATE" for player in ejected),
        own_evidence_context={
            name: tuple(
                line
                for line in memory.rendered_memory_text.splitlines()
                if "walking" in line
                or "Separated sightings" in line
                or "known dead" in line
            )
            for name, memory in sorted(memories.items())
        },
    )


class PairedComparison(_Frozen):
    arm: str
    reference: str
    paired_cases: int
    changed_trajectories: int
    changed_observation_counts: int
    changed_public_proof: int
    additional_reply_turns: int
    additional_calls: int


def paired_comparisons(
    rows: Sequence[CaseMeasurement],
    *,
    arms: Sequence[ComparisonArm],
    definitions: Sequence[ScenarioDefinition],
) -> tuple[PairedComparison, ...]:
    indexed = {(row.arm, row.case): row for row in rows}
    if len(indexed) != len(rows):
        raise ValueError("duplicate scenario comparison identity")
    if not arms or not definitions:
        raise ValueError("comparison requires the complete frozen arm-by-case matrix")
    if len({arm.name for arm in arms}) != len(arms) or len(
        {row.case for row in definitions}
    ) != len(definitions):
        raise ValueError("duplicate frozen comparison inputs")
    expected = {(arm.name, row.case) for arm in arms for row in definitions}
    if set(indexed) != expected:
        raise ValueError("comparison requires the complete frozen arm-by-case matrix")
    definition_hashes = {
        row.case: _digest(row.model_dump(mode="json")) for row in definitions
    }
    for row in rows:
        expected_hash = definition_hashes[row.case]
        if row.definition_sha256 != expected_hash:
            raise ValueError("paired scenario inputs differ from the frozen definition")
    comparisons = []
    for arm in arms[1:]:
        reference = (
            "legacy_reference"
            if arm.name == "repaired_clock"
            else "combined_accounts"
            if arm.name == "combined_with_reply"
            else "repaired_clock"
        )
        pairs = [
            (row, indexed[(reference, row.case)]) for row in rows if row.arm == arm.name
        ]
        comparisons.append(
            PairedComparison(
                arm=arm.name,
                reference=reference,
                paired_cases=len(pairs),
                changed_trajectories=sum(
                    a.trajectory_sha256 != b.trajectory_sha256 for a, b in pairs
                ),
                changed_observation_counts=sum(
                    a.perspective_observation_counts != b.perspective_observation_counts
                    for a, b in pairs
                ),
                changed_public_proof=sum(
                    a.role_proof_flags != b.role_proof_flags for a, b in pairs
                ),
                additional_reply_turns=sum(
                    a.reply_turns - b.reply_turns for a, b in pairs
                ),
                additional_calls=sum(a.calls - b.calls for a, b in pairs),
            )
        )
    return tuple(comparisons)


class DeductionEvaluation(_Frozen):
    format_version: Literal[1] = 1
    provider: Literal["scripted-deduction-control"] = "scripted-deduction-control"
    verdict: Literal["MECHANICS_ONLY"] = "MECHANICS_ONLY"
    limitations: tuple[str, ...] = (
        "Custom legal action schedules and authored SKIP ballots are development controls, not normal-policy trials or model reasoning evidence.",
        "Source observations count observer perspectives: the same world event may be observed independently by several players.",
        "A public account is a claim. Evaluation roles and private memories are privileged audit artifacts, never listener inputs.",
        "Reader projection hashes exclude filesystem-derived creation time; projections are rebuilt from the retained recordings, not duplicated as large artifacts.",
        "Already-known-dead controls bound knowledge; the simple real case does not reproduce the scalar proximity defect isolated in the adverse unit test.",
        "No experimental adoption, real-provider calls, held-out confirmation or win-rate improvement is established.",
    )
    source_hashes: Mapping[str, str]
    input_sha256: str
    python: str
    platform: str
    arms: tuple[ComparisonArm, ...]
    definitions: tuple[ScenarioDefinition, ...]
    captures: tuple[CaseMeasurement, ...]
    comparisons: tuple[PairedComparison, ...]
    artifact_hashes: Mapping[str, str]


def evaluate(output_dir: Path, *, root: Path) -> DeductionEvaluation:
    """Publish only a complete matrix from stable sources into a new directory."""
    arms = comparison_arms()
    definitions = tuple(scenario_definition(case) for case in scenario_cases())
    inputs = _digest(
        {
            "arms": [arm.model_dump(mode="json") for arm in arms],
            "cases": [case.model_dump(mode="json") for case in definitions],
        }
    )
    sources = source_hashes(root)
    output_dir.mkdir(parents=True, exist_ok=False)
    rows: list[CaseMeasurement] = []
    for arm in arms:
        for definition in definitions:
            destination = output_dir / arm.name / definition.case
            destination.mkdir(parents=True)
            capture = run_case(
                destination,
                case=definition.case,
                experiment_config=arm.experiment_config,
                temporal_version=arm.temporal_version,
            )
            if capture.definition != definition:
                raise ValueError("scenario inputs changed during capture")
            rows.append(measure_capture(capture, arm=arm, output_dir=output_dir))
    if source_hashes(root) != sources:
        raise ValueError("implementation sources changed during capture")
    artifacts = {
        str(path.relative_to(output_dir)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(output_dir.rglob("*"))
        if path.is_file()
    }
    result = DeductionEvaluation(
        source_hashes=sources,
        input_sha256=inputs,
        python=platform.python_version(),
        platform=platform.platform(),
        arms=arms,
        definitions=definitions,
        captures=tuple(rows),
        comparisons=paired_comparisons(rows, arms=arms, definitions=definitions),
        artifact_hashes=artifacts,
    )
    (output_dir / "evaluation.json").write_text(result.model_dump_json(indent=2) + "\n")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    result = evaluate(args.output_dir, root=Path(__file__).resolve().parents[1])
    print(
        f"{result.verdict}: {len(result.captures)} recorded comparisons in {args.output_dir}"
    )
    for comparison in result.comparisons:
        print(
            f"{comparison.arm} vs {comparison.reference}: {comparison.changed_trajectories}/{comparison.paired_cases} changed trajectories; {comparison.additional_reply_turns:+d} reply turns"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
