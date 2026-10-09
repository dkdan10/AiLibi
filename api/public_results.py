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

# Each set's source link is rooted at a commit that holds exactly the bytes its
# fingerprint certifies. The shown 9-player set's bytes landed in
# 5095a1c2 (the promotion of candidate round 3); the 4-player set's replays are
# unchanged since 9bae2b03, so its link, and the bundle bytes that carry it, do
# not move.
_REPOSITORY_BLOB = "https://github.com/dkdan10/AiLibi/blob/"
_SOURCE_ROOT_9P2I = (
    _REPOSITORY_BLOB + "5095a1c210d890d289405564d2af2607d2fbd4e9/replays/samples/9p2i/"
)
_SOURCE_ROOT_4P1I = (
    _REPOSITORY_BLOB + "9bae2b03032cede6a180c0888fde3b4e47f9a5f1/replays/samples/4p1i/"
)
_SOURCE_ROOTS: dict[str, str] = {
    "sha256:ea53a00f4c59aa23dd6c014c92443b36049ee192ec8a33e07d3ca69301f55329": (
        _SOURCE_ROOT_9P2I
    ),
    "sha256:2abab5c07eafb01c5efeef4d1234a77a6b57939a6923f3aee240349e0c0b1566": (
        _SOURCE_ROOT_4P1I
    ),
}
_SEED_19_SHA = "01bbbd8b31c6aee0703bffc1fb8943682b825a181a2b8391bdbb71b89c11f31c"
MAX_PUBLIC_RESULTS_BYTES = 50 * 1024


def _curated_cases() -> tuple[PublicCaseView, ...]:
    """Editorial examples; source identity and semantic checks qualify publication.

    Both sit on the featured strip's 9-player head, so the demo bundle, which
    bakes only featured games, carries them.
    """
    return (
        PublicCaseView(
            case_id="witnessed-vent",
            title="A sighting the table can check",
            setup="A body report opens the meeting, and another player then describes seeing someone use a vent. Follow that observation into the ballots.",
            explanation="p-1's observation records p-6 venting in Engineering at tick 12, and p-1's ballot cites it. Four other voters cite p-1's turn and vote for p-6. The meeting carries role proof and ejects p-6. This is a supported use of a certified observation; it does not demonstrate general social deduction.",
            classification="supported",
            game_id="headless-seed-19",
            meeting_id="headless-seed-19:meeting-0",
            meeting_tick=12,
            observer_id="p-1",
            turn_id="headless-seed-19:meeting-0:turn-2",
            observation_id="p-1:12:1",
            source_sha256=_SEED_19_SHA,
            source_url=_SOURCE_ROOT_9P2I + "replay-seed-19.jsonl",
        ),
        PublicCaseView(
            case_id="weak-evidence",
            title="When accounts do not settle the question",
            setup="A body reporter is accused, and the meeting raises no flag at all. Read the accusations, the reporter's reply, and how the table handles uncertainty.",
            explanation="Four speakers accuse the reporter, crewmate p-1, and no flag names anyone. p-1 replies with an account of its own route. Four voters skip, each saying it held nothing, and one votes for p-1, so no one is ejected. Withholding a conviction is defensible on this evidence; this example does not establish that skipping was the optimal game strategy.",
            classification="unresolved",
            game_id="headless-seed-19",
            meeting_id="headless-seed-19:meeting-1",
            meeting_tick=31,
            observer_id="p-1",
            turn_id="headless-seed-19:meeting-1:turn-5",
            observation_id=None,
            source_sha256=_SEED_19_SHA,
            source_url=_SOURCE_ROOT_9P2I + "replay-seed-19.jsonl",
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

    if case.classification == "supported":
        witness, venter = "p-1", "p-6"
        # A body report opens the meeting, and another player's later turn
        # describes the vent sighting.
        if not (
            meeting.trigger_kind == "body"
            and meeting.triggered_by != witness
            and case.observer_id == case_turn.speaker == witness
            and case_turn.turn_kind != "opening"
            and any(
                isinstance(o, SawVentObservationView)
                and (o.subject, o.room, o.tick) == (venter, "ENGINEERING", 12)
                for o in case_turn.observations
            )
        ):
            raise stale
        # The witness's ballot cites that observation, which resolves in the
        # witness's own memory to the vent use it describes.
        if not any(
            b.voter == witness
            and b.target == venter
            and b.primary_reason_observation_id == case.observation_id
            for b in meeting.ballots
        ):
            raise stale
        observation = cited(witness, case.observation_id)
        if observation is None or (
            observation.kind,
            observation.subject_id,
            observation.room,
            observation.observation_tick,
            observation.scene_tick,
        ) != ("saw_vent", venter, "ENGINEERING", 12, 11):
            raise stale
        # Four other voters cite the witness's turn and vote for the venter.
        if (
            sum(
                b.voter != witness
                and b.target == venter
                and b.primary_reason_id == case.turn_id
                for b in meeting.ballots
            )
            != 4
        ):
            raise stale
        # Role proof in the meeting, and the ejection it names.
        if not (
            meeting.ejected_player_id == venter
            and roles[venter] == "IMPOSTOR"
            and any(
                c.category == "role_proof" and venter in c.subjects
                for c in meeting.contradictions
            )
        ):
            raise stale
    else:
        reporter = "p-1"
        # A body reporter whom four other speakers accuse, in a meeting that
        # raises no flag.
        accusers = [
            t
            for t in meeting.turns
            if t.speaker != reporter
            and any(
                isinstance(c, AccusationClaimView) and c.against == reporter
                for c in t.claims
            )
        ]
        if not (
            meeting.trigger_kind == "body"
            and meeting.triggered_by == reporter
            and roles[reporter] == "CREWMATE"
            and len({t.speaker for t in accusers}) == 4
            and not meeting.contradictions
        ):
            raise stale
        # The reporter replies after the first accusation with an account of
        # its own route.
        if not (
            case.observer_id == case_turn.speaker == reporter
            and case_turn.turn_kind == "reply"
            and case_turn.turn_index > min(t.turn_index for t in accusers)
            and any(
                isinstance(c, AlibiClaimView)
                and c.subject == reporter
                and c.route is not None
                and len(c.route) > 0
                for c in case_turn.claims
            )
        ):
            raise stale
        # Four voluntary skips, each labelled as holding nothing, and one vote
        # for the reporter: no ejection.
        skips = [b for b in meeting.ballots if b.target == "SKIP"]
        if not (
            meeting.outcome == "SKIPPED"
            and meeting.ejected_player_id is None
            and len(meeting.ballots) == 5
            and len(skips) == 4
            and all(b.grounding_label == "none_held" for b in skips)
            and sum(b.target == reporter for b in meeting.ballots) == 1
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
    """The pinned source for a set whose bytes match a published fingerprint."""
    return _SOURCE_ROOTS.get(fingerprint)


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
