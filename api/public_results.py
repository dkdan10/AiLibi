"""Small, source-bound results for the spectator and its static distribution."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from collections import Counter
from pathlib import Path

from api.replay_loader import ReplayLoader
from api.schemas import (
    PublicCaseView,
    PublicResultsView,
    ReplayView,
    ReportProvenanceGroupView,
)
from orchestrator.recording_fingerprint import recording_fingerprint
from orchestrator.replay import (
    AbortedMeetingReplayEntry,
    FailedCallReplayEntry,
    MeetingReplayEntry,
    read_all_entries,
)

_SOURCE_ROOT = (
    "https://github.com/dkdan10/AiLibi/blob/"
    "5006a32fb31b62e52ff6a29909baeba661fe86ac/replays/samples/9p2i/"
)
_SEED_23_SHA = "e493a2f64cc6a8e5cfbfa5c92d034b65575f0cbcf062acfb42d89dd3670c086d"
_SEED_46_SHA = "4cb6027dc80781aaaf4861bc92990aaa17d65a2d7419b3ef9ad55d84fdc32116"
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
            case_id="impossible-route",
            title="Follow an accusation across the map",
            setup="A body reporter is accused of an impossible journey. Compare the cited sighting with the rooms and the next two moves.",
            explanation="Three voters eject crewmate p-1 after p-9 calls the route impossible. The recorded route is legal: East Hall, Engineering, then Storage. p-9's citation confirms the first move, not the inference. p-3's cited observation concerns p-4 in Cafeteria, not p-1's move. A citation can resolve and still fail to support an accusation.",
            classification="unsupported",
            game_id="headless-seed-46",
            meeting_id="headless-seed-46:meeting-3",
            meeting_tick=31,
            observer_id="p-9",
            turn_id="headless-seed-46:meeting-3:turn-1",
            observation_id="p-9:29:3",
            source_sha256=_SEED_46_SHA,
            source_url=_SOURCE_ROOT + "replay-seed-46.jsonl",
        ),
        PublicCaseView(
            case_id="weak-evidence",
            title="When accounts do not settle the question",
            setup="An alibi spans two neighboring rooms. Read the weak flags, the replies, and how the table handles uncertainty.",
            explanation="All seven voters voluntarily skip. The two flags concern crewmate p-4's adjacent-room alibi endpoints and are weak signals, with no role proof. Withholding a conviction is defensible on this evidence; this example does not establish that skipping was the optimal game strategy.",
            classification="unresolved",
            game_id="headless-seed-23",
            meeting_id="headless-seed-23:meeting-1",
            meeting_tick=12,
            observer_id="p-4",
            turn_id="headless-seed-23:meeting-1:turn-3",
            observation_id=None,
            source_sha256=_SEED_23_SHA,
            source_url=_SOURCE_ROOT + "replay-seed-23.jsonl",
        ),
    )


def _check_case(case: PublicCaseView, replay: ReplayView, loader: ReplayLoader) -> None:
    meeting = next(m for m in replay.meetings if m.meeting_id == case.meeting_id)
    roles = {p.agent_id: p.role for p in replay.players}
    valid = meeting.tick == case.meeting_tick and any(
        t.turn_id == case.turn_id for t in meeting.turns
    )
    if case.classification == "supported":
        valid &= meeting.ejected_player_id == "p-6" and roles["p-6"] == "IMPOSTOR"
        valid &= any(
            c.category == "role_proof" and "p-6" in c.subjects
            for c in meeting.contradictions
        )
    elif case.classification == "unsupported":
        valid &= meeting.ejected_player_id == "p-1" and roles["p-1"] == "CREWMATE"
        valid &= not meeting.contradictions
        valid &= (
            sum(
                b.target == "p-1" and b.primary_reason_id == case.turn_id
                for b in meeting.ballots
            )
            == 3
        )
        route = [
            next(p.room_id for p in frame.agent_states if p.agent_id == "p-1")
            for frame in replay.ticks
            if frame.tick in (28, 29, 30)
        ]
        valid &= route == ["EAST_HALL", "ENGINEERING", "STORAGE"]
    else:
        valid &= len(meeting.ballots) == 7 and all(
            b.target == "SKIP" and not b.rewrite_reasons for b in meeting.ballots
        )
        valid &= len(meeting.contradictions) == 2 and all(
            c.category == "weak_signal" for c in meeting.contradictions
        )
        valid &= roles["p-4"] == "CREWMATE"
    if case.observation_id is not None:
        memory = loader.get_meeting_memory(
            case.game_id, case.meeting_id, case.observer_id
        )
        observation = next(
            (
                r
                for r in memory.observation_references
                if r.observation_id == case.observation_id
            ),
            None,
        )
        valid &= observation is not None and observation.resolved
        if observation is not None:
            expected = (
                ("saw_vent", "p-6", "ENGINEERING", 8, 7)
                if case.classification == "supported"
                else ("saw_player_move", "p-1", None, 29, 28)
            )
            valid &= (
                observation.kind,
                observation.subject_id,
                observation.room,
                observation.observation_tick,
                observation.scene_tick,
            ) == expected
            if case.classification == "unsupported":
                valid &= (observation.from_room, observation.to_room) == (
                    "CAFETERIA",
                    "EAST_HALL",
                )
                other = loader.get_meeting_memory(case.game_id, case.meeting_id, "p-3")
                unrelated = next(
                    (
                        r
                        for r in other.observation_references
                        if r.observation_id == "p-3:29:1"
                    ),
                    None,
                )
                valid &= unrelated is not None and unrelated.resolved
                if unrelated is not None:
                    valid &= (unrelated.kind, unrelated.subject_id, unrelated.room) == (
                        "saw_player",
                        "p-4",
                        "CAFETERIA",
                    )
    if not valid:
        raise ValueError(f"Curated case no longer describes its source: {case.case_id}")


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
        == "sha256:85fb119eeb09cc9b70fc8e9c7e202d41a3c3a93ff62b8ef824907c4cdec25d10"
    ):
        return _SOURCE_ROOT
    if (
        fingerprint
        == "sha256:8bbf89bf86072311d45338dd84a98f4fe51c42fe6709bb606926072c4e617d14"
    ):
        return _SOURCE_ROOT.replace("9p2i/", "4p1i/")
    return None


def build_public_results(loader: ReplayLoader) -> PublicResultsView:
    """Reuse one verified result per loader while source bytes and substrate agree.

    Content hashes include the roster and manifest. On a miss, clear the
    mtime-keyed playback caches too: replacement bytes can preserve their mtime.
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
        for path in directory.glob("replay-seed-*.jsonl")
        if re.fullmatch(r"replay-seed-\d+\.jsonl", path.name)
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
