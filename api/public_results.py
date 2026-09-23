"""Small, source-bound results for the spectator and its static distribution."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from collections import Counter
from pathlib import Path

from api.replay_loader import ReplayLoader
from api.schemas import (
    AccusationClaimView,
    AlibiClaimView,
    ObservationReferenceView,
    PublicCaseView,
    PublicResultsView,
    ReplayView,
    ReportProvenanceGroupView,
    SawPlayerView,
    SawVentObservationView,
)
from orchestrator.recording_fingerprint import (
    REPLAY_FILENAME_GLOB,
    recording_fingerprint,
    replay_seed_from_filename,
)
from orchestrator.replay import (
    AbortedMeetingReplayEntry,
    FailedCallReplayEntry,
    MeetingReplayEntry,
    read_all_entries,
)

_SOURCE_ROOT = (
    "https://github.com/dkdan10/AiLibi/blob/"
    "9bae2b03032cede6a180c0888fde3b4e47f9a5f1/replays/samples/9p2i/"
)
_SEED_0_SHA = "5e0b8421b960cdf7dc5eddc516281197656fa9a7d2e9f7007155d997850f9f7f"
_SEED_23_SHA = "35ccb2420b411d81bfa490d998dd973d33c168baee2f07982e11c1f53a7e1bfc"
_SEED_29_SHA = "06d8fb4c816ed80bfe0fa060daa4c149fc0142544bdf148cb39e2f77f6a54668"
MAX_PUBLIC_RESULTS_BYTES = 50 * 1024


def _curated_cases() -> tuple[PublicCaseView, ...]:
    """Editorial examples; source identity and semantic checks qualify publication."""
    return (
        PublicCaseView(
            case_id="witnessed-vent",
            title="A sighting the table can check",
            setup="An emergency meeting follows a reported vent sighting. Follow the witness's observation into the ballots.",
            explanation="p-5's observation records p-6 venting in Engineering at tick 8. The meeting carries role proof and ejects p-6. This is a supported use of a certified observation; it does not demonstrate general social deduction.",
            classification="supported",
            game_id="headless-seed-23",
            meeting_id="headless-seed-23:meeting-0",
            meeting_tick=10,
            observer_id="p-5",
            turn_id="headless-seed-23:meeting-0:turn-0",
            observation_id="p-5:8:1",
            source_sha256=_SEED_23_SHA,
            source_url=_SOURCE_ROOT + "replay-seed-23.jsonl",
        ),
        PublicCaseView(
            case_id="disputed-route",
            title="Follow an accusation across the map",
            setup="Two players' sightings dispute a third player's stated route. Compare the sightings with the voters' own cited observations and the recorded moves.",
            explanation="Five voters eject crewmate p-1, citing the turn where p-1 gives that route. p-9 and p-7 each placed p-1 in Labs at tick 6, where the route says Medbay. Both then cite their own observation of p-1 moving from Labs to Medbay at tick 6, and the replay has p-1 in Medbay at that moment. The statements do conflict, but the recorded moves support p-1's route, not the sightings. A citation can resolve and still fail to support an accusation.",
            classification="unsupported",
            game_id="headless-seed-29",
            meeting_id="headless-seed-29:meeting-1",
            meeting_tick=9,
            observer_id="p-9",
            turn_id="headless-seed-29:meeting-1:turn-2",
            observation_id="p-9:6:2",
            source_sha256=_SEED_29_SHA,
            source_url=_SOURCE_ROOT + "replay-seed-29.jsonl",
        ),
        PublicCaseView(
            case_id="weak-evidence",
            title="When accounts do not settle the question",
            setup="A body reporter is accused, and weak flags question where two other players stood. Read the weak flags, the replies, and how the table handles uncertainty.",
            explanation="Six speakers accuse the reporter, crewmate p-1, but no flag names p-1. The three flags are weak signals about p-5 and p-7, all resting on p-4's sightings, and none is role proof. Five voters choose to skip and two vote for p-1, so no one is ejected. Withholding a conviction is defensible on this evidence; this example does not establish that skipping was the optimal game strategy.",
            classification="unresolved",
            game_id="headless-seed-0",
            meeting_id="headless-seed-0:meeting-1",
            meeting_tick=17,
            observer_id="p-4",
            turn_id="headless-seed-0:meeting-1:turn-3",
            observation_id=None,
            source_sha256=_SEED_0_SHA,
            source_url=_SOURCE_ROOT + "replay-seed-0.jsonl",
        ),
    )


def _check_case(case: PublicCaseView, replay: ReplayView, loader: ReplayLoader) -> None:
    """Hold every sentence of a case's setup and explanation to its recording."""
    stale = ValueError(f"Curated case no longer describes its source: {case.case_id}")
    meeting = next(m for m in replay.meetings if m.meeting_id == case.meeting_id)
    roles = {p.agent_id: p.role for p in replay.players}
    turns = {t.turn_id: t for t in meeting.turns}
    case_turn = turns.get(case.turn_id or "")
    if meeting.tick != case.meeting_tick or case_turn is None:
        raise stale

    def cited(
        observer: str, observation_id: str | None
    ) -> ObservationReferenceView | None:
        memory = loader.get_meeting_memory(case.game_id, case.meeting_id, observer)
        return next(
            (
                r
                for r in memory.observation_references
                if r.observation_id == observation_id and r.resolved
            ),
            None,
        )

    def room_at(agent_id: str, tick: int) -> str | None:
        return next(
            (
                state.room_id
                for frame in replay.ticks
                if frame.tick == tick
                for state in frame.agent_states
                if state.agent_id == agent_id
            ),
            None,
        )

    if case.classification == "supported":
        # An emergency meeting the witness opens with the vent sighting, and the
        # witness's ballot carries the observation behind it.
        if not (
            meeting.trigger_kind == "emergency"
            and meeting.triggered_by == case.observer_id == case_turn.speaker == "p-5"
            and case_turn.turn_kind == "opening"
            and any(
                isinstance(o, SawVentObservationView)
                and (o.subject, o.room, o.tick) == ("p-6", "ENGINEERING", 8)
                for o in case_turn.observations
            )
            and any(
                b.voter == case.observer_id
                and b.target == "p-6"
                and b.primary_reason_observation_id == case.observation_id
                for b in meeting.ballots
            )
        ):
            raise stale
        # Role proof in the meeting, and the ejection it names.
        if not (
            meeting.ejected_player_id == "p-6"
            and roles["p-6"] == "IMPOSTOR"
            and any(
                c.category == "role_proof" and "p-6" in c.subjects
                for c in meeting.contradictions
            )
        ):
            raise stale
        observation = cited(case.observer_id, case.observation_id)
        if observation is None or (
            observation.kind,
            observation.subject_id,
            observation.room,
            observation.observation_tick,
            observation.scene_tick,
        ) != ("saw_vent", "p-6", "ENGINEERING", 8, 7):
            raise stale
    elif case.classification == "unsupported":
        accused = "p-1"
        # The case turn is the accused's own route, which says Medbay at tick 6.
        route = next(
            (
                c
                for c in case_turn.claims
                if isinstance(c, AlibiClaimView) and c.subject == accused
            ),
            None,
        )
        if (
            case_turn.speaker != accused
            or route is None
            or route.route is None
            or not any(
                leg.room == "MEDBAY" and leg.from_tick <= 6 <= leg.to_tick
                for leg in route.route
            )
        ):
            raise stale
        # Five voters eject crewmate p-1, each citing that turn.
        if not (
            meeting.ejected_player_id == accused
            and roles[accused] == "CREWMATE"
            and sum(b.target == accused for b in meeting.ballots) == 5
            and all(
                b.primary_reason_id == case.turn_id
                for b in meeting.ballots
                if b.target == accused
            )
        ):
            raise stale
        # Exactly two flags, each pairing that route with a different witness's
        # sighting that places p-1 in Labs at tick 6.
        route_id = f"turn:{case.turn_id}:claim:{case_turn.claims.index(route)}"
        witnesses: set[str] = set()
        if len(meeting.contradictions) != 2:
            raise stale
        for flag in meeting.contradictions:
            ends = {flag.event_a_id, flag.event_b_id}
            if not (
                flag.kind == "alibi_vs_physical"
                and flag.category == "cross_statement"
                and flag.subjects == (accused,)
                and route_id in ends
                and len(ends) == 2
            ):
                raise stale
            (sighting_id,) = ends - {route_id}
            sighting_turn_id, _, index = sighting_id.removeprefix("turn:").rpartition(
                ":obs:"
            )
            sighting_turn = turns.get(sighting_turn_id)
            if not (
                sighting_turn is not None
                and index.isdigit()
                and int(index) < len(sighting_turn.observations)
            ):
                raise stale
            sighting = sighting_turn.observations[int(index)]
            if not (
                isinstance(sighting, SawPlayerView)
                and (sighting.room, sighting.tick) == ("LABS", 6)
                and accused in sighting.co_present
            ):
                raise stale
            witnesses.add(sighting_turn.speaker)
        if witnesses != {"p-9", "p-7"}:
            raise stale
        # Both witnesses vote for p-1 citing their own record of p-1 moving from
        # Labs to Medbay at tick 6, and the replay has p-1 in Medbay at that scene.
        if (case.observer_id, case.observation_id) != ("p-9", "p-9:6:2"):
            raise stale
        for voter, observation_id in (("p-9", "p-9:6:2"), ("p-7", "p-7:6:2")):
            if not any(
                b.voter == voter
                and b.target == accused
                and b.primary_reason_observation_id == observation_id
                for b in meeting.ballots
            ):
                raise stale
            move = cited(voter, observation_id)
            if move is None or move.scene_tick is None:
                raise stale
            if (
                move.kind,
                move.subject_id,
                move.from_room,
                move.to_room,
                move.observation_tick,
            ) != ("saw_player_move", accused, "LABS", "MEDBAY", 6):
                raise stale
            if (
                room_at(accused, move.scene_tick - 1),
                room_at(accused, move.scene_tick),
            ) != ("LABS", "MEDBAY"):
                raise stale
    else:
        reporter = "p-1"
        # A body reporter whom six other speakers accuse, with a reply on record.
        accusers = {
            t.speaker
            for t in meeting.turns
            for c in t.claims
            if isinstance(c, AccusationClaimView) and c.against == reporter
        }
        if not (
            meeting.trigger_kind == "body"
            and meeting.triggered_by == reporter
            and roles[reporter] == "CREWMATE"
            and len(accusers) == 6
            and reporter not in accusers
            and any(t.turn_kind == "reply" for t in meeting.turns)
        ):
            raise stale
        # Three weak alibi-versus-sighting flags about p-5 and p-7 only, each
        # resting on one of the case speaker's sightings of its subject.
        flags = meeting.contradictions
        if not (
            case_turn.speaker == case.observer_id == "p-4"
            and len(flags) == 3
            and {s for c in flags for s in c.subjects} == {"p-5", "p-7"}
            and all(
                c.kind == "alibi_vs_sighting" and c.category == "weak_signal"
                for c in flags
            )
        ):
            raise stale
        for flag in flags:
            prefix = f"turn:{case.turn_id}:obs:"
            indexes = [
                end.removeprefix(prefix)
                for end in (flag.event_a_id, flag.event_b_id)
                if end.startswith(prefix)
            ]
            if not (
                len(indexes) == 1
                and indexes[0].isdigit()
                and int(indexes[0]) < len(case_turn.observations)
            ):
                raise stale
            sighting = case_turn.observations[int(indexes[0])]
            if not (
                isinstance(sighting, SawPlayerView)
                and (sighting.subject,) == flag.subjects
            ):
                raise stale
        # Five voluntary skips and two votes for the reporter: no ejection.
        if not (
            meeting.outcome == "SKIPPED"
            and meeting.ejected_player_id is None
            and len(meeting.ballots) == 7
            and sum(b.target == "SKIP" for b in meeting.ballots) == 5
            and sum(b.target == reporter for b in meeting.ballots) == 2
            and not any(b.rewrite_reasons for b in meeting.ballots)
        ):
            raise stale


def _recording_dates(directory: Path, seeds: set[int]) -> tuple[str, ...]:
    """Use manifest provenance, never checkout-dependent filesystem timestamps."""
    path = directory / "MANIFEST.md"
    if not path.exists():
        return ()
    rows = [
        line.strip().strip("|").split("|")
        for line in path.read_text().splitlines()
        if line.startswith("|")
    ]
    if not rows:
        return ()
    header = [cell.strip() for cell in rows[0]]
    if "seed" not in header or "refreshed_at" not in header:
        return ()
    seed_index, date_index = header.index("seed"), header.index("refreshed_at")
    dates = []
    for row in rows[2:]:
        if len(row) <= max(seed_index, date_index):
            raise ValueError("Malformed recording provenance row")
        if int(row[seed_index].strip()) in seeds:
            dates.append(date.fromisoformat(row[date_index].strip()).isoformat())
    return tuple(dates)


def _source_url(fingerprint: str) -> str | None:
    if (
        fingerprint
        == "sha256:cde794abe57af44da0fd3e16652435b7b1af88aaf7310d495cf3108ae80cd09f"
    ):
        return _SOURCE_ROOT
    if (
        fingerprint
        == "sha256:2abab5c07eafb01c5efeef4d1234a77a6b57939a6923f3aee240349e0c0b1566"
    ):
        return _SOURCE_ROOT.replace("9p2i/", "4p1i/")
    return None


def build_public_results(loader: ReplayLoader) -> PublicResultsView:
    """Reuse one verified result per loader while source bytes and substrate agree.

    Content hashes include the roster and manifest. On a miss, clear the
    mtime-keyed playback caches too: replacement bytes can preserve their mtime.

    Clearing and installing hold the loader's lock, so two builds cannot
    interleave their clear with each other's install, and every cached walk is
    keyed by the loader's cache generation, so a peer read that was already in
    flight during a clear cannot be read back afterwards. Together those close
    the window in which a same-length, same-mtime replacement let a build
    install pre-flip parsed replays under the post-flip fingerprint.

    Concurrent cold requests may each reconstruct; this cache does not coalesce
    in-flight work or create threads.
    """
    if loader._allow_substrate_mismatch:
        raise ValueError("Public results require strict substrate validation")
    fingerprint = recording_fingerprint(loader._replay_dir)
    substrate = loader._substrate_cache_key()
    cached = loader._public_results_cache
    if cached is not None and cached[:2] == (fingerprint, substrate):
        return cached[2]
    with loader._results_lock:
        # Re-read under the lock: a peer build may have installed the very
        # result this call was about to reconstruct.
        cached = loader._public_results_cache
        if cached is not None and cached[:2] == (fingerprint, substrate):
            return cached[2]
        loader.clear_cache()
        result = _build_public_results(loader, fingerprint)
        if loader._substrate_cache_key() != substrate:
            raise ValueError("Substrate changed during public-results generation")
        loader._public_results_cache = (fingerprint, substrate, result)
    return result


def _build_public_results(loader: ReplayLoader, fingerprint: str) -> PublicResultsView:
    """Validate every replay before publishing outcomes, with no historical fold.

    Raw reported usage remains explicitly labelled as such. Curated prose is
    omitted when its exact recording changed; current numeric results still
    derive from the new valid source. Invalid recordings fail publication.
    """
    directory = loader._replay_dir
    metadata = loader.list_replays()
    source_names = {
        path.name
        for path in directory.glob(REPLAY_FILENAME_GLOB)
        if replay_seed_from_filename(path.name) is not None
    }
    if source_names != {f"replay-seed-{meta.seed}.jsonl" for meta in metadata}:
        raise ValueError("Public results cannot omit invalid or unverified recordings")
    counts: Counter[str] = Counter()
    dates = _recording_dates(directory, {meta.seed for meta in metadata})
    models: set[str] = set()
    prompts: set[str] = set()
    cases: list[PublicCaseView] = []
    groups: dict[str, ReportProvenanceGroupView] = {}
    cost = 0.0
    for meta in metadata:
        replay = loader.load_replay(meta.game_id, include_llm_bodies=False)
        meta = replay.metadata
        identity = ReportProvenanceGroupView(
            agent_factory_kind=meta.agent_factory_kind,
            experiment_config=meta.experiment_config,
            substrate_flags=meta.substrate_flags,
            tactical_policy=meta.tactical_policy,
            crew_tactical_policy=meta.crew_tactical_policy,
            temporal_observation_version=meta.temporal_observation_version,
            game_ids=(),
        )
        key = json.dumps(identity.model_dump(mode="json"), sort_keys=True)
        previous = groups.get(key, identity)
        groups[key] = previous.model_copy(
            update={"game_ids": (*previous.game_ids, meta.game_id)}
        )
        status = meta.completion_status
        if status == "completed" and not meta.outcome_verified:
            raise ValueError(f"Unverified terminal outcome: {meta.game_id}")
        counts["games"] += 1
        counts[status] += 1
        if status == "completed":
            counts["crew_wins" if meta.winner == "CREWMATES" else "impostor_wins"] += 1
            counts["task_wins"] += meta.winner_reason == "CREWMATE_TASKS"
        prompts.update(meta.prompt_versions.values())
        path = directory / f"replay-seed-{meta.seed}.jsonl"
        entries = read_all_entries(path)
        for entry in entries:
            if isinstance(entry, (MeetingReplayEntry, AbortedMeetingReplayEntry)):
                for call in entry.llm_calls:
                    models.add(call.model)
                    cost += call.cost_usd
                    counts["input_tokens"] += call.input_tokens
                    counts["output_tokens"] += call.output_tokens
            elif isinstance(entry, FailedCallReplayEntry):
                if entry.model != "(deadline_default)":
                    models.add(entry.model)
                cost += entry.cost_usd
                counts["input_tokens"] += entry.input_tokens
                counts["output_tokens"] += entry.output_tokens
        resolved_ids = {
            e.meeting_id for e in entries if isinstance(e, MeetingReplayEntry)
        }
        counts["meetings"] += len(resolved_ids)
        roles = {p.agent_id: p.role for p in replay.players}
        for meeting in replay.meetings:
            target = meeting.ejected_player_id
            if target is None or meeting.meeting_id not in resolved_ids:
                continue
            correct = roles[target] == "IMPOSTOR"
            counts["ejections"] += 1
            counts["impostor_ejections" if correct else "innocent_ejections"] += 1
            has_proof = any(
                c.category == "role_proof" and target in c.subjects
                for c in meeting.contradictions
            )
            prefix = "proof_backed" if has_proof else "proof_free"
            counts[prefix + "_ejections"] += 1
            counts[prefix + "_correct"] += correct
        for case in _curated_cases():
            if case.game_id != meta.game_id or directory.name != "9p2i":
                continue
            if hashlib.sha256(path.read_bytes()).hexdigest() != case.source_sha256:
                continue
            _check_case(case, replay, loader)
            cases.append(case)
    if recording_fingerprint(directory) != fingerprint:
        raise ValueError("Recording inputs changed during public-results generation")
    result = PublicResultsView(
        provenance_groups=tuple(groups[key] for key in sorted(groups)),
        set_name=directory.name,
        source_fingerprint=fingerprint,
        recorded_from=min(dates) if dates else None,
        recorded_until=max(dates) if dates else None,
        models=tuple(sorted(models)),
        prompt_versions=tuple(sorted(prompts)),
        source_url=_source_url(fingerprint),
        reported_cost_usd=cost,
        cases=tuple(
            sorted(
                cases,
                key=lambda case: [c.case_id for c in _curated_cases()].index(
                    case.case_id
                ),
            )
        ),
        games=counts["games"],
        completed=counts["completed"],
        aborted=counts["aborted"],
        tick_limited=counts["tick_limited"],
        unfinished=counts["unfinished"],
        crew_wins=counts["crew_wins"],
        impostor_wins=counts["impostor_wins"],
        task_wins=counts["task_wins"],
        meetings=counts["meetings"],
        ejections=counts["ejections"],
        impostor_ejections=counts["impostor_ejections"],
        innocent_ejections=counts["innocent_ejections"],
        proof_backed_ejections=counts["proof_backed_ejections"],
        proof_backed_correct=counts["proof_backed_correct"],
        proof_free_ejections=counts["proof_free_ejections"],
        proof_free_correct=counts["proof_free_correct"],
        input_tokens=counts["input_tokens"],
        output_tokens=counts["output_tokens"],
    )
    if len(result.model_dump_json().encode()) > MAX_PUBLIC_RESULTS_BYTES:
        raise ValueError("Public results exceed the 50 KiB publication budget")
    return result
