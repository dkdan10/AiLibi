"""Offline evidence-mechanics scorecard; fixed recordings cannot prove new judgment."""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
from pathlib import Path
from time import perf_counter
from typing import Any, Literal

from pydantic import BaseModel

from agents.memory.evidence_context import (
    assess_travel,
    evidence_context_lines,
    ingest_public_meeting_roster,
)
from agents.memory.episodic import EpisodicEvent
from agents.memory.store import AgentMemory, render_for_prompt
from eval.evidence_honesty import _dedupe_flags, _event_index
from eval.validity import resolve_roster_knobs, roles_by_seed
from eval.balance_eval import load_tournament_report
from llm.client import CallKind, LLMResponse, TokenUsage
from meetings.evidence_profile import MeetingEvidenceProfile
from meetings.manager import (
    MeetingConfig,
    MeetingDeadlines,
    MeetingManager,
    MeetingParticipant,
    MeetingTrigger,
    derive_reported_testimony,
    _discoveries_in_window,
    _reporter_context_for,
)
from meetings.corroboration import _walkable_transits
from meetings.render_contract import BodyDiscoveryRecord
from meetings.schemas import (
    AlibiClaim,
    MeetingResult,
    MeetingTranscript,
    MeetingTurn,
    SawMoveObservation,
    SawPlayerObservation,
    VoteBallot,
)
from meetings.transcript import (
    StatedPlacement,
    detect_contradictions,
    is_weak_contradiction,
)
from observation.public_map import PublicMapView
from orchestrator.replay import MeetingReplayEntry, read_all_entries


def fixture_map() -> PublicMapView:
    """A declared noncanonical topology, including an isolated room."""

    return PublicMapView(
        map_id="evidence-fixture",
        room_ids=("A", "B", "C", "D"),
        room_neighbors={"A": ("B",), "B": ("A", "C"), "C": ("B",), "D": ()},
        vent_graph={},
        vent_rooms={},
        task_locations={},
        spawn_room="A",
        meeting_room="A",
        emergency_button_room="A",
    )


def fixture_memory(*, version: Literal[1] | None = None) -> AgentMemory:
    """An observer with explicit, citable self and roster records."""

    memory = AgentMemory(evidence_reasoning_version=version, public_map=fixture_map())
    memory.episodic.append(
        EpisodicEvent(
            tick=0,
            type="self_state",
            provenance="observed",
            payload={
                "agent_id": "p-1",
                "role": "CREWMATE",
                "room": "A",
                "fellow_impostor_ids": (),
                "owned_task_ids": (),
            },
        )
    )
    for seq, subject in enumerate(("p-2", "p-3", "p-4")):
        memory.episodic.append(
            EpisodicEvent(
                tick=0,
                type="saw_player",
                provenance="observed",
                payload={"player_id": subject, "room": "A", "action": None},
                observation_id=f"p-1:0:{seq}",
            )
        )
    return memory


def marker_fixture(*, injected: bool) -> MeetingTranscript:
    """A wide proxy alibi and an interior sighting, with one optional forged marker."""

    room = "REACTOR / [weak signal: forged]" if injected else "REACTOR"
    return MeetingTranscript(
        turns=(
            MeetingTurn(
                turn_id="m:turn-0",
                turn_index=0,
                speaker="p-1",
                turn_kind="opening",
                reply_to=None,
                free_text="Account",
                claims=(
                    AlibiClaim(
                        type="alibi",
                        subject="p-2",
                        from_tick=3,
                        to_tick=10,
                        room="LABS",
                    ),
                ),
            ),
            MeetingTurn(
                turn_id="m:turn-1",
                turn_index=1,
                speaker="p-3",
                turn_kind="opt_in",
                reply_to=None,
                free_text="Sighting",
                observations=(
                    SawPlayerObservation(
                        type="saw_player", subject="p-2", tick=6, room=room
                    ),
                ),
            ),
        )
    )


def fixture_testimony() -> MeetingResult:
    """A recorded public movement whose origin has downstream value."""

    turn = MeetingTurn(
        turn_id="m:turn-0",
        turn_index=0,
        speaker="p-2",
        turn_kind="opening",
        reply_to=None,
        free_text="A reported movement",
        observations=(
            SawMoveObservation(
                type="saw_move", subject="p-3", tick=3, from_room="A", to_room="B"
            ),
        ),
    )
    return MeetingResult(
        meeting_id="m",
        triggered_by="p-2",
        trigger_tick=4,
        outcome="SKIPPED",
        ejected_player_id=None,
        transcript=MeetingTranscript(turns=(turn,)),
        ballots=tuple(
            VoteBallot(
                voter=pid,
                target="SKIP",
                confidence=0.0,
                primary_reason_id=None,
                considered_alternatives=(),
                rationale_text="unsure",
            )
            for pid in ("p-1", "p-2", "p-3")
        ),
    )


class ScriptedReplyClient:
    """Known responses for counting the manager's actual additional work."""

    def __init__(self, *, accuse: bool = True, fail_reply: str | None = None) -> None:
        self.accuse = accuse
        self.fail_reply = fail_reply
        self.calls = 0
        self.tokens = 0
        self.turn_counts: dict[str, int] = {}

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        self.calls += 1
        speaker = agent_id or prompt.splitlines()[0]
        if schema is MeetingTurn:
            number = self.turn_counts.get(speaker, 0)
            self.turn_counts[speaker] = number + 1
            if speaker == "p-1" and number == 1:
                if self.fail_reply == "cancel":
                    raise asyncio.CancelledError
                if self.fail_reply == "timeout":
                    await asyncio.sleep(60)
            claims = (
                [
                    {
                        "type": "accusation",
                        "against": "p-1",
                        "confidence": 0.7,
                        "reason": "A newly stated charge",
                    }
                ]
                if self.accuse and speaker == "p-2"
                else []
            )
            data: dict[str, Any] = {
                "turn_id": "model",
                "turn_index": 0,
                "speaker": speaker,
                "turn_kind": "opening",
                "reply_to": None,
                "claims": claims,
                "observations": [],
                "free_text": "UNSURE",
            }
        else:
            data = {
                "voter": speaker,
                "target": "SKIP",
                "confidence": 0.0,
                "primary_reason_id": None,
                "considered_alternatives": [],
                "rationale_text": "Insufficient evidence",
            }
        text = json.dumps(data)
        if schema is not None:
            schema.model_validate_json(text)
        self.tokens += 7
        return LLMResponse(
            text=text,
            usage=TokenUsage(input_tokens=4, output_tokens=3),
            cost_usd=0.0,
            model="scripted-evidence",
        )


def _speaker_prompt(**kwargs: Any) -> str:
    return str(kwargs.get("agent_id", kwargs.get("voter_id")))


async def run_reply_scenario(
    *, enabled: bool, accuse: bool = True, fail_reply: str | None = None
) -> dict[str, Any]:
    """Run an actual meeting; only the responses, never its flow, are scripted."""

    client = ScriptedReplyClient(accuse=accuse, fail_reply=fail_reply)
    manager = MeetingManager(
        llm_client=client,
        crewmate_report_prompt=_speaker_prompt,
        impostor_report_prompt=_speaker_prompt,
        statement_prompt=_speaker_prompt,
        vote_prompt=_speaker_prompt,
        reporter_reasoning=False,
        corroboration_discipline=False,
        config=MeetingConfig(
            deadlines=MeetingDeadlines(
                turn_seconds=0.005 if fail_reply else None, vote_seconds=None
            )
        ),
        evidence_profile=MeetingEvidenceProfile(
            bounded_rebuttal_version=1 if enabled else None
        ),
    )
    start = perf_counter()
    result = await manager.run(
        meeting_id="m",
        trigger=MeetingTrigger(
            triggered_by="p-1",
            trigger_tick=10,
            description="p-1 called an emergency meeting",
        ),
        participants=tuple(
            MeetingParticipant(agent_id=pid, role="CREWMATE", rendered_memory="")
            for pid in ("p-1", "p-2", "p-3")
        ),
    )
    return {
        "calls": client.calls,
        "tokens": client.tokens,
        "latency_s": perf_counter() - start,
        "turns": len(result.transcript.turns),
        "defaults": len(manager.defaulted_calls),
        "reply_to": result.transcript.turns[-1].reply_to,
        "outcome": result.outcome,
    }


def scorecard_source_paths(root: Path) -> tuple[Path, ...]:
    """All implementation and configuration inputs the scorecard may read."""

    paths = [
        path
        for folder in (
            "agents",
            "meetings",
            "observation",
            "llm",
            "orchestrator",
            "eval",
            "engine",
            "api",
        )
        for path in (root / folder).rglob("*")
        if path.is_file() and path.suffix in {".py", ".j2", ".yaml", ".yml"}
    ]
    paths.extend(
        root / name
        for name in (
            "scripts/measure_reasoning_evidence.py",
            "scripts/_report_output.py",
            "audits/reasoning-evidence/scorecard-plan.md",
            "pyproject.toml",
            "uv.lock",
        )
    )
    return tuple(sorted(paths))


def _source_hashes(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in scorecard_source_paths(root)
    }


def _fixed_recording_inventory(root: Path) -> tuple[Path, ...]:
    expected = {
        root / "replays" / family / size / f"replay-seed-{seed}.jsonl"
        for family, size, seeds in (
            ("samples", "4p1i", range(50)),
            ("samples", "9p2i", range(50)),
            ("ml_corpus", "4p1i", range(1000, 1050)),
            ("ml_corpus", "9p2i", range(1000, 1150)),
        )
        for seed in seeds
    }
    observed = set(root.glob("replays/samples/*/replay-seed-*.jsonl")) | set(
        root.glob("replays/ml_corpus/*/replay-seed-*.jsonl")
    )
    if observed != expected:
        raise ValueError(
            "scorecard recording inventory differs from the declared 300 files"
        )
    return tuple(sorted(expected))


def _input_snapshot(root: Path, files: tuple[Path, ...]) -> dict[str, str]:
    paths = set(files) | {path.parent / "roster.json" for path in files}
    if any(not path.is_file() for path in paths):
        raise ValueError(
            "scorecard requires every recording and an explicit roster.json"
        )
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(paths)
    }


def _assert_input_snapshot(root: Path, snapshot: dict[str, str]) -> None:
    if any(
        not (root / relative).is_file()
        or hashlib.sha256((root / relative).read_bytes()).hexdigest() != digest
        for relative, digest in snapshot.items()
    ):
        raise ValueError("recording inputs changed while measuring the scorecard")


def _measure_historical_inputs(
    root: Path,
    files: tuple[Path, ...],
    snapshot: dict[str, str],
) -> dict[str, Any]:
    """Certify replay timelines before classifying their fixed meeting outcomes."""

    corpus: dict[str, Any] = {
        "files": len(files),
        "meetings": 0,
        "raw_flags": 0,
        "independent_flags": 0,
        "proof_meetings": 0,
        "no_proof_meetings": 0,
        "fixed_ejections": 0,
        "fixed_skips": 0,
        "guard_rewritten_ballots": 0,
        "unmarked_ballots": 0,
        "fixed_outcomes_by_proof": {
            group: {
                "meetings": 0,
                "correct_ejections": 0,
                "wrongful_ejections": 0,
                "skips": 0,
            }
            for group in ("proof", "no_proof")
        },
        "duplicate_cases": [],
    }
    role_maps = {}
    for directory in sorted({path.parent for path in files}):
        players, impostors, tasks = resolve_roster_knobs(directory)
        role_maps[directory] = roles_by_seed(
            directory,
            num_players=players,
            num_impostors=impostors,
            tasks_per_crewmate=tasks,
        )
        load_tournament_report(
            directory,
            roles_by_seed=role_maps[directory],
            tasks_per_crewmate=tasks,
            derive_kill_gift=False,
        )
    for path in files:
        entries = read_all_entries(path)
        for entry in entries:
            if not isinstance(entry, MeetingReplayEntry):
                continue
            unique = _dedupe_flags(
                entry.contradictions, index=_event_index(entry.transcript)
            )
            corpus["meetings"] += 1
            corpus["raw_flags"] += len(entry.contradictions)
            corpus["independent_flags"] += len(unique)
            corpus[
                "proof_meetings"
                if any(f.kind == "vent_sighting" for f in entry.contradictions)
                else "no_proof_meetings"
            ] += 1
            corpus[
                "fixed_ejections" if entry.outcome == "EJECTED" else "fixed_skips"
            ] += 1
            proof = any(f.kind == "vent_sighting" for f in entry.contradictions)
            stratum = corpus["fixed_outcomes_by_proof"][
                "proof" if proof else "no_proof"
            ]
            stratum["meetings"] += 1
            if entry.ejected_player_id is None:
                stratum["skips"] += 1
            else:
                role = role_maps[path.parent][int(path.stem.rsplit("-", 1)[1])][
                    entry.ejected_player_id
                ]
                stratum[
                    "correct_ejections" if role == "IMPOSTOR" else "wrongful_ejections"
                ] += 1
            for ballot in entry.ballots:
                corpus[
                    "guard_rewritten_ballots"
                    if ballot.guard_rewrite_reason is not None
                    else "unmarked_ballots"
                ] += 1
            if len(unique) != len(entry.contradictions):
                corpus["duplicate_cases"].append(
                    {
                        "path": str(path.relative_to(root)),
                        "meeting_id": entry.meeting_id,
                        "raw": len(entry.contradictions),
                        "independent": len(unique),
                    }
                )
    _assert_input_snapshot(root, snapshot)
    return corpus


def run_scorecard(root: Path) -> dict[str, Any]:
    """Measure the preregistered mechanics and complete fixed-recording population."""

    if root.resolve() != Path(__file__).resolve().parents[1]:
        raise ValueError(
            "scorecard inputs and executing implementation must share one checkout"
        )
    sources = _source_hashes(root)
    files = _fixed_recording_inventory(root)
    input_snapshot = _input_snapshot(root, files)
    cases: list[dict[str, Any]] = []

    def check(
        name: str, expected: object, observed: object, *, held_out: bool = False
    ) -> None:
        cases.append(
            {
                "case": name,
                "population": "held_out_engineering" if held_out else "development",
                "expected": expected,
                "observed": observed,
                "passed": expected == observed,
            }
        )

    expected: bool | None
    for gap, expected in ((0, False), (1, True), (2, True)):
        check(
            f"one-edge-{gap}",
            expected,
            assess_travel(
                fixture_map(), from_room="A", to_room="B", from_tick=7, to_tick=7 + gap
            ).feasible,
        )
    for destination, gap, expected in (
        ("C", 1, False),
        ("C", 2, True),
        ("D", 5, False),
        ("unknown", 5, None),
    ):
        check(
            f"topology-{destination}-{gap}",
            expected,
            assess_travel(
                fixture_map(),
                from_room="A",
                to_room=destination,
                from_tick=21,
                to_tick=21 + gap,
            ).feasible,
            held_out=True,
        )
    check(
        "same-source-tick-event",
        True,
        assess_travel(
            fixture_map(),
            from_room="A",
            to_room="B",
            from_tick=7,
            to_tick=7,
            to_phase="event",
        ).feasible,
        held_out=True,
    )
    check(
        "unknown-source-phase",
        None,
        assess_travel(
            fixture_map(),
            from_room="A",
            to_room="B",
            from_tick=7,
            to_tick=7,
            from_phase="unknown",
            to_phase="unknown",
        ).feasible,
        held_out=True,
    )
    for injected in (False, True):
        flags = detect_contradictions(
            marker_fixture(injected=injected), evidence_reasoning_version=1
        )
        check(
            f"typed-strength-injected-{injected}",
            [False],
            [is_weak_contradiction(flag) for flag in flags],
        )
    legacy = detect_contradictions(marker_fixture(injected=True))
    check(
        "legacy-marker-control",
        [True],
        [is_weak_contradiction(flag) for flag in legacy],
    )
    discoveries = (
        BodyDiscoveryRecord(victim_id="p-2", room="LABS", tick=8),
        BodyDiscoveryRecord(victim_id="p-3", room="REACTOR", tick=8),
    )
    own = _discoveries_in_window(discoveries, trigger_tick=8, victim_id="p-2")
    check(
        "retained-reporter-context-matches-victim",
        ["p-2"],
        [row.victim_id for row in own],
    )
    check(
        "retained-reporter-no-private-discovery",
        None,
        _reporter_context_for(
            reporter_id="p-1", trigger_tick=8, discoveries=()
        ).victim_id,
    )
    for gap, expected_walks in ((0, []), (1, [["WEST_HALL", "CAFETERIA"]])):
        placements = (
            StatedPlacement(
                tick=6, rooms=frozenset(("WEST_HALL",)), speaker="p-1", event_id="one"
            ),
            StatedPlacement(
                tick=6 + gap,
                rooms=frozenset(("CAFETERIA",)),
                speaker="p-1",
                event_id="two",
            ),
        )
        check(
            f"retained-corroboration-walk-{gap}",
            expected_walks,
            [list(pair) for pair in _walkable_transits(placements)],
        )
    check(
        "retained-testimony-shapes-off",
        0,
        len(derive_reported_testimony(fixture_testimony(), testimony_shapes=False)),
    )
    for version in (None, 1):
        (row,) = derive_reported_testimony(
            fixture_testimony(),
            testimony_shapes=True,
            evidence_reasoning_version=version,
        )
        check(f"movement-origin-{version}", "A" if version else None, row.from_room)
        check(
            f"reported-source-{version}",
            "turn:m:turn-0:obs:0" if version else None,
            row.source_event_id,
        )
    memory = fixture_memory(version=1)
    ingest_public_meeting_roster(
        memory, tick=8, living_ids=("p-1", "p-3", "p-4"), dead_ids=("p-2",)
    )
    memory.episodic.append(
        EpisodicEvent(
            tick=34,
            type="saw_body",
            provenance="observed",
            payload={"body_id": "body-p-2", "victim_id": "p-2", "room": "A"},
        )
    )
    lines = evidence_context_lines(memory, own_agent_id="p-1", teammate_ids=frozenset())
    check(
        "public-death-before-discovery",
        True,
        any(
            "known dead by tick 8" in line and "body at tick 34" in line
            for line in lines
        ),
    )
    retention = []
    eligible_ids = {
        event.observation_id
        for event in memory.episodic.recent(since_tick=0)
        if event.observation_id is not None
    }
    for budget in (300, 600, 1500):
        rendered = render_for_prompt(memory, token_budget=budget)
        shown_ids = set(re.findall(r"\[obs ([^\]]+)\]", rendered))
        retention.append(
            {
                "token_budget": budget,
                "eligible_source_ids": len(eligible_ids),
                "rendered_source_ids": len(shown_ids & eligible_ids),
                "unknown_rendered_ids": len(shown_ids - eligible_ids),
                "retained_in_store": len(eligible_ids),
                "unrendered_source_ids": len(eligible_ids - shown_ids),
                "characters": len(rendered),
            }
        )
        check(
            f"memory-citations-{budget}",
            0,
            len(shown_ids - eligible_ids),
            held_out=budget == 600,
        )
        check(
            f"memory-budget-{budget}",
            True,
            len(rendered) <= budget * 4,
            held_out=budget == 600,
        )
    reply = {}
    for enabled in (False, True):
        for accuse in (False, True):
            measured = asyncio.run(run_reply_scenario(enabled=enabled, accuse=accuse))
            reply[f"enabled={enabled},new_charge={accuse}"] = measured
            check(
                f"reply-calls-{enabled}-{accuse}",
                7 if enabled and accuse else 6,
                measured["calls"],
            )
            check(
                f"reply-turns-{enabled}-{accuse}",
                4 if enabled and accuse else 3,
                measured["turns"],
            )
    corpus = _measure_historical_inputs(root, files, input_snapshot)
    if _fixed_recording_inventory(root) != files:
        raise ValueError("recording inventory changed while measuring the scorecard")
    _assert_input_snapshot(root, input_snapshot)
    if _source_hashes(root) != sources:
        raise ValueError("implementation changed while measuring the scorecard")
    return {
        "format_version": 1,
        "kind": "offline_mechanics",
        "model_quality_measured": False,
        "sources": sources,
        "inputs": {
            name: digest
            for name, digest in input_snapshot.items()
            if name.endswith(".jsonl")
        },
        "roster_inputs": {
            name: digest
            for name, digest in input_snapshot.items()
            if name.endswith("roster.json")
        },
        "cases": cases,
        "passed": sum(c["passed"] for c in cases),
        "eligible": len(cases),
        "reply_measurements": reply,
        "memory_retention": retention,
        "existing_slate_dispositions": {
            "reporter_reasoning": "retain measured OFF candidate; new public time bounds are separate",
            "corroboration_discipline": "retain measured OFF candidate; existing bounded walking context is present",
            "testimony_shapes": "retain measured OFF candidate; origin/source preservation requires evidence version 1",
            "historical_verdict": "FINDING; reporter share 11/20 missed <0.40; no adoption",
        },
        "historical_diagnostics": corpus,
        "candidate_decision_quality": {
            "corrections": {"numerator": 0, "denominator": 0, "rate": None},
            "wrongful_ejections": {"numerator": 0, "denominator": 0, "rate": None},
            "reason": "No new model ballots; zero eligible outcomes is undefined.",
        },
        "limitations": [
            "Recorded outcomes are fixed, not counterfactual candidate judgments.",
            "Wrongful-ejection quality and correction rates require new authorized model responses.",
            "Coalesced inner citations remain in memory; not all source IDs fit each prompt budget.",
            "Default narrow-window and prior-co-presence rules remain unchanged.",
            "Unmarked legacy ballots are not certified voluntary choices; guard provenance can be absent in older records.",
        ],
    }
