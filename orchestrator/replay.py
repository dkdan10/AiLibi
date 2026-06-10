"""Append-only JSONL replay log (DESIGN.md §11.4).

Each game produces a single replay file. Records are JSON objects, one
per line. The replay log has two kinds of records, discriminated by the
``kind`` field:

* ``"tick"`` — a :class:`ReplayEntry` written each tick by
  :meth:`ReplayLog.record_tick`. Carries the input actions and a state
  hash. This shape pre-dates Task 3.12 and is preserved for the
  existing engine-determinism tests (Task 2.8 byte-identity gate).
* ``"meeting"`` — a :class:`MeetingReplayEntry` written each time the
  orchestrator dispatches to ``MeetingManager`` and applies the
  :class:`MeetingResult`. Carries every artifact needed to reconstruct
  the meeting for replay/eval per DESIGN.md §11.4: the transcript
  (reports + statements), ballots, contradiction flags, the LLM-call
  records (prompt, response text, usage, cost, model) and the prompt
  template versions in play. The before/after state hashes pin the
  engine-owned mutation that resulted from applying the meeting
  outcome.

Engine determinism is unchanged: state hashes + recorded actions cover
the engine layer. LLM-layer determinism is achieved by replaying the
recorded LLM outputs rather than re-calling the provider; the records
written here are the per-meeting payload that future record/replay
clients consume.

Versioning (decision 10; DESIGN.md §11.4). The replay JSONL is
intentionally **unversioned**: none of the replay entry models
(:class:`ReplayEntry`, :class:`MeetingReplayEntry`,
:class:`GameEndReplayEntry`, :class:`FailedCallReplayEntry`) carries a
``format_version`` field, and none is added when the engine state model or
the meeting transcript shape changes. Two guards already reject any replay
recorded under a different model, so a version field would be redundant:
the per-tick ``state_hash`` byte-rejects a replay whose engine-state
serialization differs (a stale replay fails reconstruction rather than
mis-parsing), and the per-set ``roster.json`` sidecar pins the roster the
set was recorded at. The fail-loud version gate lives only on the offline
eval **report** (:data:`eval.report_schema.CURRENT_FORMAT_VERSION`), whose
shape is a fresh artifact; the replay bytes rely on the hash + sidecar
instead.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import fields, is_dataclass
import hashlib
import json
from pathlib import Path
from typing import Annotated, Any, Literal, TextIO, TypeAlias

from pydantic import BaseModel, ConfigDict, Field

from engine.actions import Action
from engine.world import WorldState
from meetings.schemas import (
    ContradictionRef,
    MeetingOutcome,
    MeetingResult,
    MeetingTranscript,
    PlayerId,
    VoteBallot,
)


class LLMCallRecord(BaseModel):
    """One LLM call captured during a meeting (DESIGN.md §11.4).

    Carries every field a record/replay client needs to reproduce the
    response without re-calling the provider: the prompt text, the
    structured response text, the provider-neutral token usage, the
    USD cost, and the model id the adapter actually called. The
    ``call_kind`` ("meeting" / "trigger") tag mirrors the LLM Protocol
    so replay records preserve which model-tier the call routed
    through.

    ``agent_id`` records which game-agent originated the call (the
    speaking participant for meeting calls), so per-call attribution
    survives into replay tooling (DESIGN.md §5, §11.4). It defaults to
    ``None`` so replay JSONLs written before this field existed still
    deserialize: ``extra="forbid"`` rejects unknown fields but permits a
    missing optional one. ``None`` also stands for genuinely agentless
    (system-level) calls.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    call_kind: Literal["meeting", "trigger"]
    model: str
    prompt: str
    response_text: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    agent_id: str | None = None


class ReplayEntry(BaseModel):
    """One per-tick replay record written by :meth:`ReplayLog.record_tick`."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: Literal["tick"] = "tick"
    game_id: str
    tick: int
    actions: tuple[dict[str, Any], ...]
    state_hash: str


class MeetingReplayEntry(BaseModel):
    """One meeting replay record (Task 3.12, DESIGN.md §11.4).

    Bundles every artifact the orchestrator persists when a meeting
    resolves. The :attr:`transcript`, :attr:`ballots`, and
    :attr:`contradictions` fields hold the structured payloads from
    :class:`MeetingResult` so eval scripts can read them without
    re-running the meeting. :attr:`llm_calls` carries the captured
    per-call telemetry needed for LLM-layer replay determinism.
    :attr:`prompt_versions` records the static version markers for
    each prompt template in play; bumping a template version while
    keeping the old replay around lets future tooling diff outputs
    across prompt revisions.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: Literal["meeting"] = "meeting"
    game_id: str
    meeting_id: str
    tick: int
    triggered_by: PlayerId
    outcome: MeetingOutcome
    ejected_player_id: PlayerId | None
    transcript: MeetingTranscript
    ballots: tuple[VoteBallot, ...]
    contradictions: tuple[ContradictionRef, ...]
    llm_calls: tuple[LLMCallRecord, ...]
    prompt_versions: Mapping[str, str]
    state_hash_before: str
    state_hash_after: str


WinnerSide: TypeAlias = Literal["CREWMATES", "IMPOSTORS"]


class GameEndReplayEntry(BaseModel):
    """One game-outcome replay record (DESIGN.md §11.4; Task 3.19 finding 3).

    Written once per game by :meth:`ReplayLog.record_game_end` after the
    engine emits its ``GameOverEvent``, as the LAST row of a completed
    game's replay. Persisting the decisive outcome makes win-rate
    computable from any replay log via :func:`read_game_outcome` —
    including a partial tournament that crashed mid-run, where a
    ``game_over`` row is present for every game that finished before the
    crash. ``winner`` is ``None`` only for an unfinished / drawn game; the
    engine always names a side, so orchestrator-written rows always carry
    a winner.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: Literal["game_over"] = "game_over"
    game_id: str
    tick: int | None = None
    winner: WinnerSide | None
    reason: str


class FailedCallReplayEntry(BaseModel):
    """One failed-LLM-call replay record (DESIGN.md §11.4; Task 3.19 finding 2).

    Written by :meth:`ReplayLog.record_failed_call` when a meeting aborts
    because a structured-output response failed schema validation. The
    ``ValidationError`` fires inside the provider before an
    :class:`~llm.client.LLMResponse` exists, so the tokens the model
    already burned would otherwise be invisible to both the budget layer
    and :meth:`ReplayLog.record_meeting` (which never runs for the crashed
    meeting). This row captures that spend — plus enough of the raw
    response and the error to reconstruct what broke — so per-meeting cost
    is auditable even for the meeting that crashed the run.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: Literal["failed_call"] = "failed_call"
    game_id: str
    meeting_id: str
    tick: int
    model: str
    prompt_length: int
    raw_response: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    error_type: str
    error_message: str


ReplayLogEntry: TypeAlias = Annotated[
    ReplayEntry | MeetingReplayEntry | GameEndReplayEntry | FailedCallReplayEntry,
    Field(discriminator="kind"),
]


class ReplayLog:
    """Append-only JSONL replay log for deterministic game replays.

    Fail-loud on an already-existing target (DESIGN.md §11.4; Task 4.16):
    constructing a log against a path that already holds a file raises
    :class:`AlreadyExistsError` unless ``force=True`` is passed, which
    truncates the existing file first. This guards the silent doubled-file
    corruption that bit the project in Phase 4 UX prep — two tournament runs
    against the same ``--output-dir`` concatenated per-seed JSONL files,
    breaking the loader's ``meeting_by_tick`` dedup. The read side
    (:func:`read_all_entries`) detects the same doubled pattern after the
    fact and raises :class:`CorruptedFileError`.
    """

    class AlreadyExistsError(FileExistsError):
        """Raised when a :class:`ReplayLog` targets an existing path without
        ``force=True``.

        Prevents the doubled-files corruption pattern (two runs appending to
        the same per-seed JSONL) that broke ``meeting_by_tick`` dedup in
        Phase 4 UX prep. Subclasses :class:`FileExistsError` so callers that
        only catch the stdlib type still intercept it.
        """

    class CorruptedFileError(RuntimeError):
        """Raised by :func:`read_all_entries` when it detects the doubled-file
        pattern: two ``kind="tick"`` rows sharing a ``tick`` value, or more
        than one ``kind="game_over"`` row in a single replay file.
        """

    def __init__(self, path: Path, game_id: str, *, force: bool = False) -> None:
        # Assigned first so __del__ is safe even if construction raises below
        # (e.g. AlreadyExistsError on an existing path).
        self._handle: TextIO | None = None
        if path.exists():
            if not force:
                raise self.AlreadyExistsError(
                    f"Replay file already exists: {path}. Pass force=True to "
                    "overwrite it, or choose a different path. (Re-using a "
                    "replay path silently doubled per-seed files in Phase 4 "
                    "and broke the loader's dedup — DESIGN.md §11.4.)"
                )
            # force=True: truncate via delete-then-recreate so the new game
            # starts from an empty file rather than appending to the old one.
            path.unlink()
        self._path = path
        self._game_id = game_id
        self._path.parent.mkdir(parents=True, exist_ok=True)
        # Single-write guard for failed-call rows (Task 9.10, audit gp-4):
        # every row already written by :meth:`record_failed_call`, keyed by
        # the full frozen entry. See that method for the dedup contract.
        self._recorded_failed_calls: set[FailedCallReplayEntry] = set()

    @property
    def path(self) -> Path:
        return self._path

    @property
    def game_id(self) -> str:
        return self._game_id

    def record_tick(self, tick: int, actions: list[Action], state: WorldState) -> None:
        entry = {
            "kind": "tick",
            "game_id": self._game_id,
            "tick": tick,
            "actions": _serialize_actions(actions),
            "state_hash": _state_hash(state),
        }
        self._append(entry)

    def record_meeting(
        self,
        *,
        meeting_id: str,
        result: MeetingResult,
        llm_calls: Sequence[LLMCallRecord],
        prompt_versions: Mapping[str, str],
        state_hash_before: str,
        state_hash_after: str,
    ) -> None:
        """Persist one resolved meeting (DESIGN.md §11.4).

        ``state_hash_before`` / ``state_hash_after`` pin the engine
        state on either side of :meth:`HeadlessGame._apply_meeting_result`
        so a replay can verify the meeting outcome was applied byte-
        identically to the engine-owned world state.
        """

        entry = MeetingReplayEntry(
            game_id=self._game_id,
            meeting_id=meeting_id,
            tick=result.trigger_tick,
            triggered_by=result.triggered_by,
            outcome=result.outcome,
            ejected_player_id=result.ejected_player_id,
            transcript=result.transcript,
            ballots=result.ballots,
            contradictions=result.contradictions,
            llm_calls=tuple(llm_calls),
            prompt_versions=dict(prompt_versions),
            state_hash_before=state_hash_before,
            state_hash_after=state_hash_after,
        )
        self._append(entry.model_dump(mode="json"))

    def record_game_end(
        self,
        *,
        winner: WinnerSide | None,
        reason: str,
        tick: int | None = None,
    ) -> None:
        """Persist the decisive game outcome (DESIGN.md §11.4; Task 3.19).

        Emitted once by :meth:`HeadlessGame.run` after the engine fires
        its ``GameOverEvent``, as the final row of a completed game's
        replay. :func:`read_game_outcome` reads it back so win-rate is
        evaluable from any replay log, including partial tournaments.
        ``tick`` defaults to ``None`` for callers (e.g. unit tests) that
        only care about the winner; the orchestrator passes the
        game-over tick.
        """

        entry = GameEndReplayEntry(
            game_id=self._game_id,
            tick=tick,
            winner=winner,
            reason=reason,
        )
        self._append(entry.model_dump(mode="json"))

    def record_failed_call(
        self,
        *,
        meeting_id: str,
        tick: int,
        model: str,
        prompt_length: int,
        raw_response: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        error_type: str,
        error_message: str,
    ) -> None:
        """Persist a meeting-aborting failed LLM call (DESIGN.md §11.4; Task 3.19).

        Called by the orchestrator on the meeting-failure path when a
        structured-output response failed schema validation (the metadata
        rides the propagating ``ValidationError`` and is recovered via
        :func:`llm.provider.extract_parse_failure`). Captures the spend
        and partial response for the rejected call so per-meeting cost is
        reconstructable even though the meeting crashed and
        :meth:`record_meeting` never ran.

        Single-write guard (Task 9.10, audit gp-4 / MECH-B-1): a row that is
        byte-identical to one already written by this log is dropped instead
        of appended. A deterministic provider (seeded local model, fixed
        prompt) regenerates the SAME failing response on the in-turn retry,
        so a single defaulted opening surfaced the same burned generation
        twice — seeds 8/36/39 each persisted a duplicate ``failed_call`` row,
        double-counting 5,969 input / 6,144 output tokens. De-duplication is
        on the FULL frozen entry — the audit's byte-identity tuple
        ``(model, raw_response, input_tokens, output_tokens)`` scoped by
        ``meeting_id`` / ``tick`` / error fields — so two zero-spend
        ``deadline_default`` visibility markers from DIFFERENT participants
        (which share the zero tuple but differ in ``error_message``) and any
        genuinely distinct failures in one meeting still each record once.
        """

        entry = FailedCallReplayEntry(
            game_id=self._game_id,
            meeting_id=meeting_id,
            tick=tick,
            model=model,
            prompt_length=prompt_length,
            raw_response=raw_response,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            error_type=error_type,
            error_message=error_message,
        )
        if entry in self._recorded_failed_calls:
            return
        self._recorded_failed_calls.add(entry)
        self._append(entry.model_dump(mode="json"))

    def read_entries(self) -> tuple[ReplayEntry, ...]:
        return read_replay_entries(self._path)

    def read_all_entries(self) -> tuple[ReplayLogEntry, ...]:
        """Read every replay record (tick + meeting) from the JSONL file."""

        return read_all_entries(self._path)

    def read_meeting_entries(self) -> tuple[MeetingReplayEntry, ...]:
        """Read just the meeting replay records from the JSONL file."""

        return read_meeting_entries(self._path)

    def close(self) -> None:
        """Flush and release the append handle (idempotent).

        Per-tick games open and append thousands of times; re-opening the
        file for every line (the original ``open("a")``-per-write) was a
        per-tick syscall cost the Task 5.9 profile surfaced. The handle is
        now opened lazily on the first append (:meth:`_append`) and reused,
        and ``close`` releases the descriptor at end of game. This is a
        write-cadence change only — the bytes written are byte-identical, so
        the determinism contract (state hashes + recorded actions) is
        unchanged.

        Lazy open also preserves the force=True "nothing on disk until the
        next append" contract (DESIGN.md §11.4, Task 4.16): a log that never
        recorded anything closes to a no-op and leaves no file.
        """

        handle = self._handle
        if handle is not None:
            self._handle = None
            handle.close()

    def __enter__(self) -> ReplayLog:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def __del__(self) -> None:
        # Best-effort descriptor release for callers that never close the log
        # (e.g. the direct-construction paths in eval/determinism_test.py).
        # Per-write flush already persisted every line, so this only frees the
        # file descriptor; swallow errors because __del__ must never raise.
        try:
            self.close()
        except Exception:
            pass

    def _append(self, entry: Mapping[str, Any]) -> None:
        handle = self._handle
        if handle is None:
            # Lazy open: the file is created on the first append, not at
            # construction, so force=True leaves nothing on disk until a row
            # is written (DESIGN.md §11.4, Task 4.16).
            handle = self._path.open("a", encoding="utf-8")
            self._handle = handle
        handle.write(_stable_json(entry))
        handle.write("\n")
        # Flush each row so a reader that opens the path while the log is still
        # alive (eval/determinism_test.py reads bytes without closing the log)
        # sees every recorded line — the same on-disk visibility the original
        # open/close-per-write gave, minus the per-write open/close syscalls.
        handle.flush()


def read_replay_entries(path: Path) -> tuple[ReplayEntry, ...]:
    """Read the tick replay records (``kind == "tick"``) from the JSONL file.

    Meeting records are skipped — call :func:`read_meeting_entries`
    for those, or :func:`read_all_entries` for the discriminated
    union. This preserves the pre-Task-3.12 contract: callers that
    only care about tick-by-tick state hashes can stay untouched
    while Phase 3 grows the replay format.
    """

    return tuple(
        entry for entry in read_all_entries(path) if isinstance(entry, ReplayEntry)
    )


def read_meeting_entries(path: Path) -> tuple[MeetingReplayEntry, ...]:
    """Read the meeting replay records (``kind == "meeting"``) from the JSONL file."""

    return tuple(
        entry
        for entry in read_all_entries(path)
        if isinstance(entry, MeetingReplayEntry)
    )


def read_failed_call_entries(path: Path) -> tuple[FailedCallReplayEntry, ...]:
    """Read the failed-call records (``kind == "failed_call"``) from the JSONL file.

    These are the LLM calls that aborted a meeting on schema-validation
    failure (Task 3.19 finding 2). Empty for any game whose meetings all
    completed; carries the rejected-call spend otherwise.
    """

    return tuple(
        entry
        for entry in read_all_entries(path)
        if isinstance(entry, FailedCallReplayEntry)
    )


def read_game_outcome(path: Path) -> WinnerSide | None:
    """Return the winner from the last game-end record in a replay log.

    Scans for ``kind == "game_over"`` records and returns the winner of
    the last one (a game writes exactly one, as its final row). Returns
    ``None`` when no game-end record is present — a partial / crashed game
    whose outcome was never decided (Task 3.19 finding 3) — so a
    tournament's win rate can be computed across every replay log,
    skipping the undecided ones.
    """

    outcome: WinnerSide | None = None
    for entry in read_all_entries(path):
        if isinstance(entry, GameEndReplayEntry):
            outcome = entry.winner
    return outcome


def compute_cost_usd(path: Path) -> float:
    """Sum LLM cost (USD) across a replay log (DESIGN.md §11.4; Task 3.19).

    Reads every record once and sums :attr:`LLMCallRecord.cost_usd` over
    each ``kind == "meeting"`` record's captured calls *plus* each
    ``kind == "failed_call"`` record's cost. This is the canonical
    per-game cost reduction: future eval code (including the real-provider
    50-game eval that checks the ``<= $0.30`` merge criterion) consumes it
    rather than re-deriving the sum inline. Folding in the failed-call
    rows means a meeting that aborted on a rejected response still
    contributes the tokens the model already burned, so a crashed run's
    spend is not silently undercounted (Task 3.19 finding 2).

    Returns ``0.0`` for replay logs with no meeting or failed-call entries
    (e.g. games that ended before any meeting fired) and for meetings
    whose ``llm_calls`` list is empty. The sum is seeded with a float so
    the return value is always a finite, non-negative float (fake-provider
    runs report ``cost_usd == 0.0`` per call).
    """

    total = 0.0
    for entry in read_all_entries(path):
        if isinstance(entry, MeetingReplayEntry):
            total += sum((call.cost_usd for call in entry.llm_calls), 0.0)
        elif isinstance(entry, FailedCallReplayEntry):
            total += entry.cost_usd
    return total


def read_all_entries(path: Path) -> tuple[ReplayLogEntry, ...]:
    """Read every replay record (tick + meeting) from the JSONL file.

    Walks the file once and fails loud on the doubled-file corruption
    pattern (DESIGN.md §11.4; Task 4.16): if two ``kind="tick"`` rows share
    a ``tick`` value, or more than one ``kind="game_over"`` row is present,
    raise :class:`ReplayLog.CorruptedFileError`. Both signatures mean two
    games' records were concatenated into one file — the silent doubled
    write that broke the loader in Phase 4 UX prep. The error names the file
    and the conflicting tick (or game_over count). Broader corruption
    hardening (mid-line partial writes, etc.) is deferred; Pydantic
    validation already rejects malformed rows.
    """

    if not path.exists():
        raise FileNotFoundError(path)

    entries: list[ReplayLogEntry] = []
    first_tick_line: dict[int, int] = {}
    game_over_count = 0
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not raw_line:
            continue
        try:
            raw_entry = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid replay JSON at line {line_number}") from exc
        entry = _parse_entry(raw_entry)
        if isinstance(entry, ReplayEntry):
            if entry.tick in first_tick_line:
                raise ReplayLog.CorruptedFileError(
                    f"Duplicate tick {entry.tick} in {path} (first at line "
                    f"{first_tick_line[entry.tick]}, again at line "
                    f"{line_number}). The file is likely a doubled-write from "
                    "re-using a tournament --output-dir without --force; "
                    "truncate the file and re-run."
                )
            first_tick_line[entry.tick] = line_number
        elif isinstance(entry, GameEndReplayEntry):
            game_over_count += 1
            if game_over_count > 1:
                raise ReplayLog.CorruptedFileError(
                    f"Multiple game_over rows in {path} ({game_over_count} "
                    "found). The file is likely a doubled-write from re-using "
                    "a tournament --output-dir without --force; truncate the "
                    "file and re-run."
                )
        entries.append(entry)
    return tuple(entries)


def _parse_entry(raw_entry: Any) -> ReplayLogEntry:
    if not isinstance(raw_entry, dict):
        raise ValueError(
            f"replay entry must be a JSON object, got: {type(raw_entry).__name__}"
        )
    # Default the discriminator to "tick" so pre-Task-3.12 replay files
    # (which never wrote a ``kind`` field) keep validating against
    # :class:`ReplayEntry` without a migration step.
    kind = raw_entry.get("kind", "tick")
    if kind == "tick":
        return ReplayEntry.model_validate({**raw_entry, "kind": "tick"})
    if kind == "meeting":
        return MeetingReplayEntry.model_validate(raw_entry)
    if kind == "game_over":
        return GameEndReplayEntry.model_validate(raw_entry)
    if kind == "failed_call":
        return FailedCallReplayEntry.model_validate(raw_entry)
    raise ValueError(f"unknown replay entry kind: {kind!r}")


def _serialize_actions(actions: list[Action]) -> list[dict[str, Any]]:
    serialized_actions: list[dict[str, Any]] = []
    for action in actions:
        serialized = _to_jsonable(action)
        if not isinstance(serialized, dict):
            raise TypeError(
                f"action did not serialize to object: {type(action).__name__}"
            )
        serialized_actions.append(serialized)
    return serialized_actions


def _state_hash(state: WorldState) -> str:
    serialized_state = _stable_json(_serialize_world_state(state)).encode("utf-8")
    return hashlib.sha256(serialized_state).hexdigest()


def _serialize_world_state(state: WorldState) -> dict[str, Any]:
    serialized = _to_jsonable(state)
    if not isinstance(serialized, dict):
        raise TypeError("world state did not serialize to object")
    return serialized


def _to_jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, BaseModel):
        return _to_jsonable(value.model_dump(mode="json"))
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _to_jsonable(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, Mapping):
        serialized_mapping: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"unsupported mapping key type: {type(key).__name__}")
            serialized_mapping[key] = _to_jsonable(item)
        return serialized_mapping
    if isinstance(value, tuple):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_to_jsonable(item) for item in value]
    raise TypeError(f"unsupported replay serialization type: {type(value).__name__}")


def _stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


__all__ = [
    "FailedCallReplayEntry",
    "GameEndReplayEntry",
    "LLMCallRecord",
    "MeetingReplayEntry",
    "ReplayEntry",
    "ReplayLog",
    "ReplayLogEntry",
    "WinnerSide",
    "compute_cost_usd",
    "read_all_entries",
    "read_failed_call_entries",
    "read_game_outcome",
    "read_meeting_entries",
    "read_replay_entries",
]
