"""Engine-playback replay loader for the spectator API (DESIGN.md §7, §11.4, §1.3).

The replay log persists ``state_hash`` per tick plus the recorded action
stream, not per-tick player positions (``orchestrator/replay.py``). To produce
the per-tick :class:`~api.schemas.AgentTickStateView` DTOs the frontend needs,
this loader re-seeds the engine from the game's seed and re-applies the
recorded actions through :func:`engine.tick.advance_tick`, mirroring the
orchestrator's own tick loop. Meeting outcomes are re-applied via the
orchestrator's :func:`~orchestrator.game.apply_meeting_result`. Every
reconstructed ``state_hash`` is checked against the recorded one; a divergence
is a determinism break and raises :class:`ReplayStateMismatchError` (surfaced
as HTTP 500 by the routes).

This is a *read-only* engine touch: the loader IMPORTS from ``engine/`` and
``orchestrator/`` but modifies nothing. ``api/`` is a privileged spectator
surface and is intentionally outside the observation firewall (DESIGN.md §1.3),
which forbids ``agents/``, ``llm/``, ``meetings/`` from importing ``engine/`` —
not ``api/``.

Per-game results are memoized in per-process LRU caches. Replays are immutable
once written, but the refresh-samples workflow rewrites a sample in place, so the
cache keys fold in the file's mtime: an in-place rewrite is a cache miss and is
never served stale (Audit H-H-2). No cross-process / cross-worker shared cache —
that is the deferred scale boundary (Audit H-H-6).
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Final, Literal

from fastapi import HTTPException, Query, Request
from pydantic import TypeAdapter

from agents.memory.store import (
    DEFAULT_TOKEN_BUDGET,
    AgentMemory,
    absorb_meeting_evidence,
    absorb_reported_testimony,
    render_for_prompt,
)
from agents.perception import EVENT_SAW_BODY, EVENT_SAW_PLAYER, ingest_packet
from api.schemas import (
    AccusationClaimView,
    AdvantageView,
    AgentMemoryView,
    AgentTickStateView,
    AgentVisibilityView,
    AlibiClaimView,
    AudibleEventView,
    BallotView,
    BeliefEntryView,
    BeliefErrorView,
    BeliefFrameView,
    BodyView,
    CompletedTaskObsView,
    ContradictionView,
    CorroborationClaimView,
    EdgeView,
    EvalCostSummaryView,
    FailedCallView,
    FoundBodyObsView,
    GateView,
    KillEventView,
    LLMCallView,
    MapLayoutView,
    MeetingTriggeredEventView,
    MeetingView,
    PlayerView,
    PositionView,
    ReplayMetadataView,
    ReplayView,
    ReportBodyEventView,
    RoomView,
    RubricGameView,
    RubricView,
    SabotageDetailView,
    SabotageEventView,
    SawPlayerView,
    SizeView,
    TaskCompletedEventView,
    TickEventView,
    TickView,
    TurnView,
    VentEventView,
    VentView,
    VisibleBodyView,
    VisiblePlayerView,
)
from engine.actions import Action
from engine.events import (
    EngineEvent,
    KilledEvent,
    MeetingTriggeredEvent,
    SabotageStartedEvent,
    TaskCompletedEvent,
    VentEnteredEvent,
    VentExitedEvent,
)
from engine.tick import advance_tick
from engine.world import Map, WorldState, load_canonical_map
from eval.meeting_quality import TournamentEvalReport
from meetings.manager import (
    BALLOT_TARGET_REDIRECT_MARKER,
    DEFAULT_SKIP_CONFIDENCE_THRESHOLD,
    EMERGENCY_BODY_STRIP_MARKER,
    INVALID_REASON_ID_MARKER,
    TEAMMATE_VOTE_TARGET_MARKER,
    VOTE_PARSE_DEFAULT_MARKER,
    derive_reported_testimony,
    extract_belief_evidence,
)
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    Claim,
    CompletedTaskObservation,
    ContradictionRef,
    CorroborationClaim,
    FoundBodyObservation,
    MeetingResult,
    MeetingTurn,
    ObservationClaim,
    SawPlayerObservation,
    VoteBallot,
)
from meetings.transcript import is_weak_contradiction
from meetings.voting import INVALID_VOTE_TARGET_MARKER, SKIP_TARGET
from observation.packet import ObservationPacket
from observation.service import ObservationService
from orchestrator.game import (
    DEFAULT_NUM_IMPOSTORS,
    DEFAULT_NUM_PLAYERS,
    apply_meeting_result,
)
from orchestrator.replay import (
    SUBSTRATE_FLAG_KEYS,
    FailedCallReplayEntry,
    GameEndReplayEntry,
    LLMCallRecord,
    MeetingReplayEntry,
    ReplayEntry,
    ReplayLog,
    WinnerSide,
    _state_hash,
    read_all_entries,
    substrate_flag_snapshot,
)
from orchestrator.seeder import seed_initial_state

_LOGGER: Final[logging.Logger] = logging.getLogger(__name__)

_DEFAULT_CACHE_SIZE: Final[int] = 16

# The per-file metadata/cost summary is a handful of ints and floats, so a
# generous bound lets the listing + cost endpoints reuse a parse across requests
# for a large replay directory without re-reading every file. The cross-worker
# shared cache the real scale phase needs is out of scope here (Audit H-H-6).
_DEFAULT_METADATA_CACHE_SIZE: Final[int] = 1024

# Filename of the tournament eval report that ``scripts/run_tournament.py``
# writes into the tournament output dir. The loader serves it read-only from
# the same configured replay/eval directory it scans for replays (Task 5.7).
_TOURNAMENT_REPORT_FILENAME: Final[str] = "tournament-eval-report.json"

# Per-set rubric surface (Task 12.2; DESIGN.md §3.1, §7). The interestingness
# scorer (``experiments/lab/rubric_score.py``) co-locates its
# ``results-rubric-score.json`` into a served set's dir; the loader serves it
# read-only and staleness-guards it against the set's ``MANIFEST.md`` git sha.
_RUBRIC_FILENAME: Final[str] = "results-rubric-score.json"
_MANIFEST_FILENAME: Final[str] = "MANIFEST.md"

# The ``MANIFEST.md`` table row shape (``scripts/_manifest_writer.py``). Task 14.7
# inserted an optional ``flags`` column after ``prompt_versions``, so a data row
# split on ``|`` is now one of:
#   legacy 7-col: ``["", seed, model, prompt_versions, refreshed_at, git_sha, cost_usd, winner, ""]``
#   new 8-col:    ``["", seed, model, prompt_versions, flags, refreshed_at, git_sha, cost_usd, winner, ""]``
# In BOTH, ``git_sha`` is the 4th cell from the end (``cells[-4]``) — reading it
# by a fixed head-index would slide onto ``refreshed_at`` for the 8-col rows and
# make the freshness guard compare a DATE. A data row's first cell is the integer
# seed. Kept in lockstep with ``experiments.lab.rubric_score``.
_MANIFEST_GIT_SHA_FROM_END: Final[int] = -4
# Fewest ``|``-split cells a well-formed data row can have (the legacy 7-col row,
# with its two empty end cells): shorter lines cannot carry ``git_sha`` at -4.
_MANIFEST_MIN_ROW_CELLS: Final[int] = 9

# Per-set roster descriptor (Task 7.4; DESIGN.md §11.4). A committed sample set
# that is NOT the MVP-default flat 4p/1i set ships this sidecar so the loader can
# re-seed it with the right roles + task pool (``num_impostors`` /
# ``tasks_per_crewmate`` are not recoverable from the action stream). A flat
# directory with NO ``roster.json`` is the only path that defaults to 4p/1i, so
# the committed flat baseline keeps reconstructing byte-identically.
_ROSTER_FILENAME: Final[str] = "roster.json"

_GAME_ID_PATTERN: Final[re.Pattern[str]] = re.compile(r"headless-seed-(-?\d+)")
_FILENAME_PATTERN: Final[re.Pattern[str]] = re.compile(r"replay-seed-(-?\d+)\.jsonl")
_PLAYER_ID_PATTERN: Final[re.Pattern[str]] = re.compile(r"p-(\d+)")

# Deterministic render palette assigned to players by their ``p-N`` index so
# the spectator UI gets stable, visually distinct colors without persisting a
# color in the engine. Index past the palette wraps; non-``p-N`` ids fall back
# to a hash-derived color.
#
# This is the Playful **identity palette** transcribed verbatim from the
# committed token seed ``design/phase-12/tokens-seed.md`` — the SAME nine-colour
# ``identity[]`` list Task 12.1 transcribes into ``frontend/src/tokens.ts``, so
# the two parallel tasks cannot drift on it. It replaces the former 12-colour
# rainbow, whose red/amber/blue/orange collided with the reserved firewall
# channels (red=kill, amber=suspicion, blue=trust). The identity hues live in
# greens/teals/purples, disjoint from every semantic channel, so a player's
# colour never encodes role or guilt (DESIGN.md §1.3; claude-design-brief.md
# "FIREWALL COLOR RULES"). Nine colours cover the canonical 9p roster (``p-1``
# … ``p-9``); the index wrap is unchanged. Colours are derived at load — no
# replay re-record, byte-identical reconstruction.
_COLOR_PALETTE: Final[tuple[str, ...]] = (
    "#5DA83A",
    "#2BA45E",
    "#14A06E",
    "#0E9C93",
    "#128F9E",
    "#6C5CE0",
    "#8350D6",
    "#9A4FCB",
    "#A94FC6",
)

_ACTION_ADAPTER: Final[TypeAdapter[Action]] = TypeAdapter(Action)

_TriggerKind = Literal["body", "emergency"]


@dataclass(frozen=True)
class RosterConfig:
    """Per-set roster descriptor parsed from a sample dir's ``roster.json``.

    The replay JSONL persists no roster header — a tick row carries only
    ``game_id``, ``tick``, ``actions``, ``state_hash`` (``orchestrator/replay.py``).
    ``num_players`` is recoverable from the recorded action ids
    (:func:`_infer_num_players`), but ``num_impostors`` and ``tasks_per_crewmate``
    are NOT: a 7p/2i replay re-seeded as 7p/1i assigns the wrong roles (and a wrong
    task count changes ``WorldState.tasks``), so the per-tick ``state_hash`` check
    in :meth:`ReplayLoader._walk` raises :class:`ReplayStateMismatchError`.

    A committed set that is not the MVP-default flat 4p/1i set therefore ships a
    ``roster.json`` carrying exactly these three knobs, parsed here into a pinned,
    frozen descriptor by :func:`_load_roster_config`. The helper FAILS LOUD on a
    missing key, a wrong type, or a non-positive value (AGENTS.md "no silent
    fallbacks"); only the *absence* of the descriptor defaults (to 4p/1i). This is
    the metadata source the deferred frontend browse track reads, so the field set
    is kept minimal and explicit (no inference).
    """

    num_players: int
    num_impostors: int
    tasks_per_crewmate: int


class ReplayStateMismatchError(RuntimeError):
    """Reconstructed ``state_hash`` diverged from the recorded one.

    Indicates a replay-determinism break (DESIGN.md §0, §11.4): either
    non-determinism in :func:`engine.tick.advance_tick`, wrong action
    deserialization, or wrong meeting-result application. Surfaced as HTTP 500
    with the offending tick + game id in the response body.
    """

    def __init__(self, *, game_id: str, tick: int, expected: str, actual: str) -> None:
        self.game_id = game_id
        self.tick = tick
        self.expected = expected
        self.actual = actual
        super().__init__(
            f"replay state-hash mismatch for {game_id!r} at tick {tick}: "
            f"recorded {expected!r}, reconstructed {actual!r}"
        )


class ReplaySubstrateMismatchError(RuntimeError):
    """A stamped replay is being reconstructed under a DIFFERENT substrate (Task 14.7).

    A replay recorded with the corrected Phase-13.5 substrate stamps its lever
    config onto its ``game_over`` record (``orchestrator.replay.GameEndReplayEntry
    .substrate_flags``). The loader HONORS that stamp: reconstruction re-derives
    agent memory / testimony / movement / belief under the active substrate
    (:func:`orchestrator.replay.substrate_flag_snapshot`), so playing back a
    recording stamped with a different lever config would silently reconstruct
    a memory view the recording never produced. Rather than fall back silently
    (AGENTS.md "no silent fallbacks"), the loader fails loud here and names the
    divergent levers. Since Task 14.9 the four 13.5 levers are unconditionally
    ON (their env gates are retired), so this fires only for a legacy stamp
    recording one of them OFF — a substrate this build can no longer reproduce.
    A legacy replay carrying NO stamp is never checked, so the committed
    final-9B baseline reconstructs unchanged. Surfaced as HTTP 500 with the
    offending game id in the response body.
    """

    def __init__(
        self,
        *,
        game_id: str,
        recorded: Mapping[str, bool],
        ambient: Mapping[str, bool],
    ) -> None:
        self.game_id = game_id
        self.recorded = dict(recorded)
        self.ambient = dict(ambient)
        differing = sorted(
            key
            for key in SUBSTRATE_FLAG_KEYS
            if bool(recorded.get(key)) != bool(ambient.get(key))
        )
        super().__init__(
            f"replay substrate mismatch for {game_id!r}: recorded with "
            f"{self.recorded!r} but reconstructing under {self.ambient!r} "
            f"(differing levers: {differing}). The four Phase-13.5 levers are "
            "unconditionally ON since Task 14.9 (their env gates are retired), "
            "so a replay stamped with one of them OFF cannot be faithfully "
            "reconstructed by this build (this is not a determinism break — the "
            "per-tick state hash is substrate-independent)."
        )


def _recorded_substrate_flags(
    entries: Sequence[object],
) -> dict[str, bool] | None:
    """Extract the stamped substrate config from a replay's ``game_over`` record.

    Mirrors :func:`orchestrator.replay.read_substrate_flags` but reads the
    already-loaded ``entries`` (the walk reads the file once) instead of
    re-opening the path. Returns ``None`` for a legacy (pre-14.7) replay that
    carries no stamp — the committed final-9B baseline — so the caller skips the
    substrate check entirely for unstamped replays.
    """

    flags: dict[str, bool] | None = None
    for entry in entries:
        if isinstance(entry, GameEndReplayEntry) and entry.substrate_flags is not None:
            flags = dict(entry.substrate_flags)
    return flags


def _assert_substrate_matches(
    game_id: str,
    entries: Sequence[object],
    *,
    allow_substrate_mismatch: bool = False,
) -> None:
    """Fail loud if a stamped replay is reconstructed under a different substrate.

    The honoring half of the Task-14.7 stamp: a recording's memory
    reconstruction re-derives under the active substrate
    (:func:`orchestrator.replay.substrate_flag_snapshot` — the four 13.5 levers
    unconditionally ON since Task 14.9), so it is only faithful when that
    substrate matches the one stamped at record time. An unstamped (legacy)
    replay is never checked, so the committed final-9B baseline reconstructs
    unchanged.

    ``allow_substrate_mismatch`` is the ANALYSIS-ONLY override (Task 14.8): the
    per-lever substrate ablation DELIBERATELY re-derives the stamped all-ON
    baseline under toggled levers, which this guard otherwise (correctly)
    refuses. Default ``False`` so the serving/verify paths keep failing loud; an
    actually-mismatched reconstruction permitted by the override is logged at
    WARNING (never silent) naming the divergent levers.
    """

    recorded = _recorded_substrate_flags(entries)
    if recorded is None:
        return
    ambient = substrate_flag_snapshot()
    differing = sorted(
        key
        for key in SUBSTRATE_FLAG_KEYS
        if bool(recorded.get(key)) != bool(ambient.get(key))
    )
    if not differing:
        return
    if allow_substrate_mismatch:
        _LOGGER.warning(
            "Deliberate substrate mismatch permitted for %r (analysis-only "
            "override, Task 14.8): recorded %r, reconstructing under %r "
            "(differing levers: %r).",
            game_id,
            dict(recorded),
            dict(ambient),
            differing,
        )
        return
    raise ReplaySubstrateMismatchError(
        game_id=game_id, recorded=recorded, ambient=ambient
    )


@dataclass(frozen=True)
class _WalkResult:
    """Internal result of one engine-playback pass over a replay file."""

    initial_state: WorldState
    ticks: tuple[TickView, ...]
    meeting_entries: tuple[MeetingReplayEntry, ...]
    failed_calls: tuple[FailedCallReplayEntry, ...]
    trigger_kind_by_meeting_id: Mapping[str, _TriggerKind]
    memories: Mapping[tuple[str, str], AgentMemoryView]


@dataclass(frozen=True)
class _ReplaySummary:
    """One-pass reduction of a replay file for the listing + cost endpoints.

    Derived from a single :func:`read_all_entries` and memoized per
    ``(path, mtime)``: replays are immutable once written (DESIGN.md §11.4), so
    the file's mtime is a sufficient invalidation key — an in-place refresh (the
    refresh-samples workflow rewrites the same path) bumps it and misses the
    cache. Folds the cost reduction and decisive outcome ``cost_summary`` needs
    together with the tick/meeting/prompt-version aggregates ``_metadata_view``
    needs, so each file is parsed exactly once per request rather than the
    two-to-four passes the pre-6.6 loader did (Audit G-G-2, H-H-2).
    """

    total_ticks: int
    meeting_count: int
    winner: WinnerSide | None
    winner_reason: str | None
    total_cost_usd: float
    prompt_versions: Mapping[str, str]


class ReplayLoader:
    """Loads + engine-replays JSONL replays into sanitized spectator DTOs.

    The loader is the single source of truth for engine-playback: routes import
    it and never compose engine APIs directly. ``load_replay`` and the
    meeting-memory reconstruction are memoized per ``game_id`` in per-process
    LRU caches (default ``maxsize=16``); :meth:`clear_cache` resets them (used
    by tests to stay hermetic).
    """

    def __init__(
        self,
        replay_dir: Path,
        *,
        game_map: Map | None = None,
        cache_size: int = _DEFAULT_CACHE_SIZE,
        metadata_cache_size: int = _DEFAULT_METADATA_CACHE_SIZE,
        allow_substrate_mismatch: bool = False,
    ) -> None:
        # ``allow_substrate_mismatch`` is the ANALYSIS-ONLY override (Task 14.8):
        # the per-lever substrate ablation deliberately re-derives the stamped
        # all-ON baseline under toggled levers, which the Task-14.7 guard
        # otherwise correctly refuses. Default False — the serving/verify paths
        # keep failing loud; the ablation harness passes True explicitly and a
        # permitted mismatched (re)construction is logged at WARNING, never
        # silent. An override loader additionally folds the ambient substrate
        # snapshot into its reconstruction cache keys (``_substrate_cache_key``)
        # so flipping the ``AILIBI_*`` levers between loads re-derives instead
        # of silently serving the previous substrate's cached reconstruction.
        self._replay_dir = replay_dir
        self._allow_substrate_mismatch = allow_substrate_mismatch
        self._game_map = game_map if game_map is not None else load_canonical_map()
        self._map_view = self._build_map_view()
        self._cached_load = lru_cache(maxsize=cache_size)(self._load_replay)
        self._cached_memories = lru_cache(maxsize=cache_size)(
            self._reconstruct_meeting_memories
        )
        self._cached_belief_frames = lru_cache(maxsize=cache_size)(
            self._compute_belief_frames
        )
        self._cached_summary = lru_cache(maxsize=metadata_cache_size)(
            self._read_summary
        )

    # -- public API -------------------------------------------------------

    def list_replays(
        self, *, limit: int | None = None, offset: int = 0
    ) -> list[ReplayMetadataView]:
        """Return metadata for every replay in the dir, ordered by seed.

        ``limit``/``offset`` page the (seed-sorted) path list *before* any
        metadata view is built, so a request's work is bounded by the page size
        rather than the whole directory (Audit G-G-3). Absent params
        (``limit=None, offset=0``) reproduce the original "every replay"
        behavior.

        A file that fails to parse — :class:`ReplayLog.CorruptedFileError`, the
        doubled-write pattern Task 4.16 detects — is excluded from the listing
        and logged at WARNING rather than aborting the whole request with a 500,
        so one bad replay no longer blocks the picker (Audit K-K-8, backend
        half).
        """

        paths = self._replay_paths()
        window = paths[offset:] if limit is None else paths[offset : offset + limit]
        views: list[ReplayMetadataView] = []
        for seed, path in window:
            try:
                views.append(self._metadata_view(path, seed))
            except ReplayLog.CorruptedFileError as exc:
                _LOGGER.warning("Skipping corrupted replay file %s: %s", path, exc)
        return views

    def load_replay(self, game_id: str) -> ReplayView:
        """Return the full reconstructed :class:`ReplayView` (LRU-cached).

        Raises :class:`FileNotFoundError` if no replay matches ``game_id`` and
        :class:`ReplayStateMismatchError` if engine playback diverges from the
        recorded state hashes. The cache key folds in the file's mtime so an
        in-place refresh (same path, new bytes) is a cache miss rather than a
        stale hit (Audit H-H-2).
        """

        path, seed = self._resolve(game_id)
        return self._cached_load(
            seed,
            path,
            _mtime_ns(path),
            self._roster_mtime(),
            self._substrate_cache_key(),
        )

    def cost_summary(self) -> EvalCostSummaryView:
        """Aggregate LLM cost + decisive-outcome split across every replay.

        Reads each replay file exactly once: both the per-game cost and the
        decisive winner come from a single memoized :class:`_ReplaySummary`
        rather than the two passes (``compute_cost_usd`` + ``read_game_outcome``)
        the pre-6.6 loader did (Audit G-G-2).
        """

        summaries = [self._file_summary(path) for _, path in self._replay_paths()]
        total_replays = len(summaries)
        costs = [summary.total_cost_usd for summary in summaries]
        total_cost = sum(costs)
        decisive = [s.winner for s in summaries if s.winner is not None]

        decisive_split: dict[str, float] = {}
        if decisive:
            for side in ("CREWMATES", "IMPOSTORS"):
                decisive_split[side] = sum(1 for w in decisive if w == side) / len(
                    decisive
                )

        return EvalCostSummaryView(
            total_replays=total_replays,
            total_cost_usd=total_cost,
            mean_cost_per_replay=(total_cost / total_replays if total_replays else 0.0),
            max_cost_per_replay=(max(costs) if costs else 0.0),
            decisive_split=decisive_split,
        )

    def tournament_report(self) -> TournamentEvalReport:
        """Load + validate the latest tournament eval report from the replay dir.

        Reads ``<replay_dir>/tournament-eval-report.json`` (the file
        :mod:`scripts.run_tournament` writes) and validates it against
        :class:`eval.meeting_quality.TournamentEvalReport`. Mirrors
        :meth:`cost_summary` in reading the same configured directory — there is
        a single authoritative tournament report per eval dir, so it is not
        keyed by game id. Raises :class:`FileNotFoundError` when no report file
        exists (the eval route maps that to HTTP 404). A malformed report fails
        loud via Pydantic validation rather than being silently coerced
        (AGENTS.md "no silent fallbacks").
        """

        path = self._replay_dir / _TOURNAMENT_REPORT_FILENAME
        if not path.is_file():
            raise FileNotFoundError(path)
        return TournamentEvalReport.model_validate_json(
            path.read_text(encoding="utf-8")
        )

    def get_meeting_memory(
        self, game_id: str, meeting_id: str, agent_id: str
    ) -> AgentMemoryView:
        """Return one agent's memory snapshot at one meeting boundary.

        Raises :class:`FileNotFoundError` for an unknown ``game_id`` and
        :class:`KeyError` for an unknown meeting or agent (routes map both to
        404). Memory is only exposed at meeting boundaries per the 4.1 decision.
        The cache key folds in the file's mtime so an in-place refresh is a cache
        miss rather than a stale hit (Audit H-H-2).
        """

        path, seed = self._resolve(game_id)
        memories = self._cached_memories(
            seed,
            path,
            _mtime_ns(path),
            self._roster_mtime(),
            self._substrate_cache_key(),
        )
        known_meetings = {meeting for meeting, _ in memories}
        if meeting_id not in known_meetings:
            raise KeyError(f"meeting not found: {meeting_id}")
        key = (meeting_id, agent_id)
        if key not in memories:
            raise KeyError(f"agent not found at meeting {meeting_id}: {agent_id}")
        return memories[key]

    def belief_frames(self, game_id: str) -> tuple[BeliefFrameView, ...]:
        """Return the per-MEETING belief × truth snapshots for a replay.

        Reuses the (cached, expensive) meeting-memory re-walk and reshapes its
        per-(meeting, agent) belief snapshots into the directed observer→subject
        matrix with the Error projection vs ground-truth role (DESIGN.md §3.3,
        §7). Beliefs are timeless/per-meeting (see :class:`BeliefFrameView`), so
        there is one frame per meeting boundary. Cached per ``game_id``.
        """

        path, seed = self._resolve(game_id)
        return self._cached_belief_frames(
            seed,
            path,
            _mtime_ns(path),
            self._roster_mtime(),
            self._substrate_cache_key(),
        )

    def rubric(self) -> RubricView:
        """Load + staleness-guard the per-set rubric from the configured dir.

        Reads ``<replay_dir>/results-rubric-score.json`` (co-located by
        ``experiments/lab/rubric_score.py``) and serves its
        ``interestingness.per_game[]`` rows, comparing the rubric's ``git_head``
        to the set's ``MANIFEST.md`` git sha to flag staleness (DESIGN.md §3.1,
        §7). Raises :class:`FileNotFoundError` when the set ships no rubric (the
        4p1i default → the eval route maps that to a 404 / empty state). A
        malformed rubric fails loud rather than being silently coerced (AGENTS.md
        "no silent fallbacks").
        """

        path = self._replay_dir / _RUBRIC_FILENAME
        if not path.is_file():
            raise FileNotFoundError(path)
        raw: Any = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError(
                f"invalid rubric file {path}: expected a JSON object, got "
                f"{type(raw).__name__}"
            )
        seedset = raw.get("seedset")
        if not isinstance(seedset, str):
            raise ValueError(f"invalid rubric file {path}: missing/invalid 'seedset'")
        git_head = raw.get("git_head")
        if git_head is not None and not isinstance(git_head, str):
            raise ValueError(f"invalid rubric file {path}: invalid 'git_head'")
        # A PRESENT-but-malformed rubric fails loud (AGENTS.md "no silent
        # fallbacks"): the 404/empty state is reserved for an ABSENT rubric (the
        # FileNotFoundError above), so a producer that wrote a file missing its
        # ``interestingness.per_game`` must not masquerade as a legitimate
        # "no highlights" surface.
        inter = raw.get("interestingness")
        if not isinstance(inter, dict):
            raise ValueError(
                f"invalid rubric file {path}: 'interestingness' must be an object"
            )
        per_game_raw = inter.get("per_game")
        if not isinstance(per_game_raw, list):
            raise ValueError(
                f"invalid rubric file {path}: 'interestingness.per_game' must be a list"
            )
        per_game = tuple(RubricGameView.model_validate(g) for g in per_game_raw)
        manifest_sha = _manifest_git_sha(self._replay_dir)
        # Staleness is BOTH a sha mismatch (rubric scored vs replays recorded)
        # AND a SET mismatch (DESIGN.md §7: "fail-loud/banner on set or sha
        # mismatch") — so a rubric from a different set co-located here (e.g. a
        # 4p1i rubric dropped into the 9p2i dir) whose git_head happens to match
        # is still flagged rather than served as fresh, wrong-set highlights.
        expected_seedset = _expected_seedset(self._replay_dir)
        sha_stale = _rubric_is_stale(git_head, manifest_sha)
        set_stale = expected_seedset is not None and seedset != expected_seedset
        return RubricView(
            seedset=seedset,
            git_head=git_head,
            manifest_sha=manifest_sha,
            stale=sha_stale or set_stale,
            per_game=per_game,
        )

    def clear_cache(self) -> None:
        """Drop the per-process caches (engine playback, memory walk, summary)."""

        self._cached_load.cache_clear()
        self._cached_memories.cache_clear()
        self._cached_belief_frames.cache_clear()
        self._cached_summary.cache_clear()

    # -- cached implementations ------------------------------------------

    def _substrate_cache_key(self) -> tuple[tuple[str, bool], ...] | None:
        """The ambient substrate's contribution to the reconstruction cache key.

        ``None`` (a constant) for a default loader — its guard raises on any
        mismatch before a wrong-substrate reconstruction could be cached, so the
        key stays byte-identical to the pre-14.8 shape. An ANALYSIS-ONLY
        override loader (``allow_substrate_mismatch=True``) deliberately walks
        under whatever ``AILIBI_*`` levers are ambient, so the snapshot must
        participate in the key: flipping levers between loads on the same
        instance re-derives (a cache miss) instead of silently serving the
        previous substrate's reconstruction (AGENTS.md "no silent fallbacks").
        """

        if not self._allow_substrate_mismatch:
            return None
        return tuple(sorted(substrate_flag_snapshot().items()))

    def _load_replay(
        self,
        seed: int,
        path: Path,
        _mtime_key: int,
        _roster_mtime_key: int,
        _substrate_key: tuple[tuple[str, bool], ...] | None = None,
    ) -> ReplayView:
        # ``_mtime_key`` / ``_roster_mtime_key`` participate in the LRU key only
        # (Audit H-H-2): an in-place rewrite of the replay OR the per-set
        # ``roster.json`` changes one of them, so the refreshed reconstruction is
        # a cache miss and is never served stale (the roster is re-read in
        # ``_walk``). Resolution + seed parsing already happened in
        # ``load_replay`` (via ``_resolve``).
        #
        # ``collect_visibility=True`` runs the per-tick per-living-agent fog
        # projection (Task 12.3; DESIGN.md §3.2, §7) — the one genuinely-expensive
        # new compute (a visibility solve per living agent per tick, stage-0 §0.5).
        # It is paid once here and memoized by this LRU, so the served payload is
        # never recomputed per request.
        walk = self._walk(path, seed, collect_memory=False, collect_visibility=True)
        return ReplayView(
            metadata=self._metadata_view(path, seed),
            map=self._map_view,
            players=self._players_view(walk.initial_state),
            ticks=walk.ticks,
            meetings=tuple(
                self._meeting_view(entry, walk.trigger_kind_by_meeting_id)
                for entry in walk.meeting_entries
            ),
            failed_calls=tuple(_failed_call_view(entry) for entry in walk.failed_calls),
        )

    def _reconstruct_meeting_memories(
        self,
        seed: int,
        path: Path,
        _mtime_key: int,
        _roster_mtime_key: int,
        _substrate_key: tuple[tuple[str, bool], ...] | None = None,
    ) -> Mapping[tuple[str, str], AgentMemoryView]:
        # ``_mtime_key`` / ``_roster_mtime_key`` / ``_substrate_key`` key the
        # cache only (Audit H-H-2; ``_substrate_cache_key``); see ``_load_replay``.
        return self._walk(path, seed, collect_memory=True).memories

    def _compute_belief_frames(
        self,
        seed: int,
        path: Path,
        _mtime_key: int,
        _roster_mtime_key: int,
        _substrate_key: tuple[tuple[str, bool], ...] | None = None,
    ) -> tuple[BeliefFrameView, ...]:
        # Reshapes the (separately cached) meeting-memory walk; no second walk.
        # ``_mtime_key`` / ``_roster_mtime_key`` / ``_substrate_key`` key the
        # cache only (Audit H-H-2; ``_substrate_cache_key``).
        memories = self._cached_memories(
            seed, path, _mtime_key, _roster_mtime_key, _substrate_key
        )
        return _belief_frames_from_memories(memories)

    # -- engine playback --------------------------------------------------

    def _walk(
        self,
        path: Path,
        seed: int,
        *,
        collect_memory: bool,
        collect_visibility: bool = False,
    ) -> _WalkResult:
        """Re-seed and re-apply the recorded action stream through the engine.

        Mirrors :meth:`orchestrator.game.HeadlessGame.run`'s tick loop. When
        ``collect_memory`` is set, the agent observation+perception pipeline is
        re-run in lockstep so per-agent memory can be re-rendered at meeting
        boundaries (the observation audit log is routed to a throwaway temp
        file). When ``collect_visibility`` is set, each living agent's
        firewall-filtered field of view is captured per tick from the same
        observation pipeline and attached to its tick state — the As-agent fog
        projection (Task 12.3; DESIGN.md §3.2, §7). Verifies every reconstructed
        ``state_hash`` against the record.
        """

        game_id = _game_id_for_seed(seed)
        entries = read_all_entries(path)
        # Honor the stamped substrate (Task 14.7): the memory reconstruction
        # below re-derives under the active substrate (the four 13.5 levers
        # unconditionally ON since Task 14.9), so refuse to reconstruct a
        # replay stamped with a different lever config rather than silently
        # producing a memory view the recording never made. Unstamped (legacy)
        # replays are not checked — the committed final-9B baseline
        # reconstructs unchanged. The 14.8 analysis-only override permits a
        # DELIBERATE mismatch (per-lever ablation) — logged, never silent;
        # serving/verify construct the loader with the default.
        _assert_substrate_matches(
            game_id, entries, allow_substrate_mismatch=self._allow_substrate_mismatch
        )
        replay_entries = [e for e in entries if isinstance(e, ReplayEntry)]
        meeting_entries = tuple(e for e in entries if isinstance(e, MeetingReplayEntry))
        failed_calls = tuple(e for e in entries if isinstance(e, FailedCallReplayEntry))
        meeting_by_tick = {entry.tick: entry for entry in meeting_entries}

        # Re-seed with this set's roster (Task 7.4). The descriptor is read fresh
        # here (not cached at construction) so an in-place ``roster.json`` add /
        # change is picked up — its mtime is folded into the LRU key (see
        # ``_load_replay``), so a stale loader is never served the old roster
        # (Audit H-H-2 parity). When the set ships a ``roster.json``, every knob
        # comes from it — ``num_impostors`` and ``tasks_per_crewmate`` are NOT
        # recoverable from the action stream, so a multi-impostor / multi-task set
        # can only reconstruct from the recorded roster. When there is NO
        # descriptor (the flat 4p/1i baseline), keep the historical default
        # verbatim: infer ``num_players`` from the actions, pin ``num_impostors``
        # to the MVP invariant, and let the seeder default ``tasks_per_crewmate``
        # to 1 — so the committed flat set stays byte-identical. A wrong descriptor
        # cannot corrupt output: the per-tick ``state_hash`` check below fails loud
        # (``ReplayStateMismatchError``).
        roster = _load_roster_config(self._replay_dir)
        if roster is None:
            num_players = _infer_num_players(replay_entries)
            num_impostors = DEFAULT_NUM_IMPOSTORS
            tasks_per_crewmate = 1
        else:
            num_players = roster.num_players
            num_impostors = roster.num_impostors
            tasks_per_crewmate = roster.tasks_per_crewmate

        initial_state = seed_initial_state(
            seed=seed,
            game_map=self._game_map,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
        )
        state = initial_state

        # The FIXED display denominator for the roster task meter (Phase-12
        # close-audit): the game-start task-instance count, snapshotted from the
        # seeded state ONCE. ``state.tasks`` shrinks as crewmates die (their
        # instances leave the pool), so the live per-tick total is a misleading
        # meter denominator; this value never changes across the game.
        fixed_tasks_required_total = len(initial_state.tasks)

        memories: dict[str, AgentMemory] = {}
        service: ObservationService | None = None
        audit_dir: tempfile.TemporaryDirectory[str] | None = None
        # The observation pipeline is re-run when EITHER the meeting-memory walk
        # (``collect_memory``) or the per-tick fog projection (``collect_visibility``,
        # Task 12.3) needs it; either way its audit log is routed to a throwaway
        # temp file. ``memories`` is only allocated for the memory walk — the
        # visibility walk reads the packet and discards it (no episodic ingest).
        if collect_memory or collect_visibility:
            audit_dir = tempfile.TemporaryDirectory(prefix="ailibi-replay-audit-")
            service = ObservationService(
                game_map=self._game_map,
                audit_log_path=Path(audit_dir.name) / "audit.jsonl",
            )
        if collect_memory:
            memories = {pid: AgentMemory() for pid in initial_state.players}

        # Finding 1 (DESIGN.md §3.1, §11.4): ReplayLog.record_tick snapshots
        # state AFTER advance_tick, so the recorded tick 0 already reflects the
        # agents' first-turn moves; the pre-action spawn state is never
        # persisted. Synthesize it here, before the entry loop, as a tick=-1
        # "Start" frame (all players in the seeder's spawn room) so the
        # spectator's first frame is the intuitive initial state, not agents
        # already mid-motion. Read-side only: it is not written back to JSONL
        # and never touches a state hash.
        # The per-tick fog projection (Task 12.3, DESIGN.md §3.2/§7): each LIVING
        # agent's firewall-filtered field of view, captured from the observation
        # packet the pipeline already builds (no second visibility solve). It is
        # built from the POST-advance state below so it matches the frame the
        # spectator scrubs to; the Start frame uses the seeded initial state with
        # no prior events.
        start_visibility = (
            self._agent_visibility_map(service, initial_state, ())
            if collect_visibility and service is not None
            else None
        )
        ticks: list[TickView] = [
            self._tick_view(
                -1,
                initial_state,
                (),
                None,
                start_visibility,
                fixed_tasks_required_total=fixed_tasks_required_total,
            )
        ]
        trigger_kind_by_meeting_id: dict[str, _TriggerKind] = {}
        memory_views: dict[tuple[str, str], AgentMemoryView] = {}
        last_events: tuple[EngineEvent, ...] = ()
        meeting_index = 0

        try:
            for entry in replay_entries:
                if collect_memory and service is not None:
                    self._ingest_tick(service, memories, state, last_events)

                actions = _deserialize_actions(entry.actions)
                state, events = advance_tick(state, actions, game_map=self._game_map)
                actual = _state_hash(state)
                if actual != entry.state_hash:
                    raise ReplayStateMismatchError(
                        game_id=game_id,
                        tick=entry.tick,
                        expected=entry.state_hash,
                        actual=actual,
                    )

                meeting_entry: MeetingReplayEntry | None = None
                meeting_id: str | None = None
                trigger_kind: _TriggerKind | None = None
                body_id: str | None = None
                if state.phase == "MEETING":
                    meeting_entry = meeting_by_tick.get(entry.tick)
                    trigger_kind, body_id = _meeting_trigger_from_events(events)
                    meeting_id = (
                        meeting_entry.meeting_id
                        if meeting_entry is not None
                        else _meeting_id_for(game_id, meeting_index)
                    )
                    trigger_kind_by_meeting_id[meeting_id] = trigger_kind

                # Capture each living agent's field of view from the POST-advance
                # state + this tick's events — the frame the spectator sees at
                # ``entry.tick`` (Task 12.3). Computed once here; LRU-cached by
                # ``_load_replay`` so it is never recomputed per request.
                # ``reopened_body_id`` keeps a just-reported body in the fog on its
                # meeting frame (``_apply_report`` already flagged it discovered);
                # ``body_id`` is the trigger body for a body report, ``None`` for a
                # play tick or an emergency meeting.
                tick_visibility = (
                    self._agent_visibility_map(
                        service, state, events, reopened_body_id=body_id
                    )
                    if collect_visibility and service is not None
                    else None
                )
                ticks.append(
                    self._tick_view(
                        entry.tick,
                        state,
                        events,
                        meeting_id,
                        tick_visibility,
                        fixed_tasks_required_total=fixed_tasks_required_total,
                    )
                )

                if state.phase != "MEETING":
                    if state.phase == "GAME_OVER":
                        break
                    last_events = tuple(events)
                    continue

                assert meeting_id is not None  # set above when phase == MEETING

                if meeting_entry is None:
                    # Partial replay: the meeting opened but never resolved
                    # (the run crashed mid-meeting per Task 3.19). It is not
                    # exposed via /meetings/{meeting_id}, so do NOT snapshot
                    # memory for it either — keep the two endpoints consistent.
                    # The tick timeline is intact up to here; stop the walk.
                    break

                if collect_memory:
                    # Snapshot every known player, alive or dead. The endpoint
                    # contract is agent-based (ThoughtStream selects by agent),
                    # so a player who died before this meeting must still be
                    # retrievable; their memory is frozen at death (perception
                    # stops ingesting once they are dead).
                    for pid in sorted(state.players):
                        memory_views[(meeting_id, pid)] = self._agent_memory_view(
                            agent_id=pid,
                            tick=entry.tick,
                            meeting_state=state,
                            memory=memories[pid],
                            meeting_entry=meeting_entry,
                        )

                pre_meeting_events = tuple(events)
                result = _meeting_result_from_entry(meeting_entry)
                state, post_events = apply_meeting_result(
                    state,
                    result,
                    game_map=self._game_map,
                    triggering_body_id=body_id,
                )
                after = _state_hash(state)
                if after != meeting_entry.state_hash_after:
                    raise ReplayStateMismatchError(
                        game_id=game_id,
                        tick=entry.tick,
                        expected=meeting_entry.state_hash_after,
                        actual=after,
                    )
                # The meeting TickView was appended from the PRE-resolution state
                # (its agent_states / events represent the meeting itself), but
                # the advantage frame is the win-progress trajectory, so it must
                # carry the meeting's OUTCOME — recompute it from the post-result
                # state so an ejection shows as the decisive inflection (otherwise
                # an eject that ends the game leaves the last frame reporting the
                # ejected impostor still alive). Keep the tick's task totals so
                # ``advantage.tasks_*`` stays aligned with ``tasks_*_total``.
                meeting_view_tick = ticks[-1]
                ticks[-1] = meeting_view_tick.model_copy(
                    update={
                        "advantage": _advantage_view(
                            state,
                            tasks_completed=meeting_view_tick.tasks_completed_total,
                            tasks_required=meeting_view_tick.tasks_required_total,
                            tasks_required_total=fixed_tasks_required_total,
                        )
                    }
                )
                if collect_memory:
                    # Mirror the live loop's post-meeting belief fold (Task
                    # 9.8, orchestrator.game._absorb_meeting_beliefs): the
                    # recorded meeting's evidence lands in each still-living
                    # agent's reconstructed beliefs, so the NEXT meeting's
                    # memory snapshot shows the same accumulated/decayed
                    # suspicion the live agents held. Memory-side only --
                    # engine state and its hash checks are untouched.
                    evidence = extract_belief_evidence(result)
                    # Task 13.5.2: mirror the live loop's reported-testimony
                    # content fold in the SAME per-living-agent loop,
                    # unconditionally since Task 14.9 (the adopted lever is the
                    # default substrate). The derivation is the SAME pure
                    # function of the recorded ``result`` the orchestrator
                    # uses, so the live and replay reconstructions are
                    # identical. Memory-side only -- engine state and its hash
                    # checks are untouched.
                    statements = derive_reported_testimony(result)
                    for pid in sorted(state.players):
                        if not state.players[pid].alive:
                            continue
                        absorb_meeting_evidence(
                            memories[pid],
                            accused=evidence.accused,
                            corroborated=evidence.corroborated,
                            contradicted=evidence.contradicted,
                        )
                        absorb_reported_testimony(memories[pid], statements=statements)
                meeting_index += 1
                if state.phase == "GAME_OVER":
                    break
                last_events = pre_meeting_events + tuple(post_events)
        finally:
            if audit_dir is not None:
                audit_dir.cleanup()

        return _WalkResult(
            initial_state=initial_state,
            ticks=tuple(ticks),
            meeting_entries=meeting_entries,
            failed_calls=failed_calls,
            trigger_kind_by_meeting_id=trigger_kind_by_meeting_id,
            memories=memory_views,
        )

    def _ingest_tick(
        self,
        service: ObservationService,
        memories: Mapping[str, AgentMemory],
        state: WorldState,
        last_events: Sequence[EngineEvent],
    ) -> None:
        """Re-run perception for every alive agent (mirrors the game loop).

        Matches :meth:`orchestrator.game.TacticalAgent.decide`: a packet is
        built from the pre-tick world state and the previous tick's events, then
        ingested into the agent's episodic store. Tactical/strategic output is
        irrelevant for replay (we have the recorded actions); only the memory
        side effect matters.
        """

        for pid in sorted(state.players):
            if not state.players[pid].alive:
                continue
            packet = service.build_packet(
                world_state=state, agent_id=pid, engine_events=last_events
            )
            ingest_packet(
                packet=packet,
                memory=memories[pid].episodic,
                beliefs=memories[pid].beliefs,
            )

    def _agent_visibility_map(
        self,
        service: ObservationService,
        state: WorldState,
        events: Sequence[EngineEvent],
        *,
        reopened_body_id: str | None = None,
    ) -> dict[str, AgentVisibilityView]:
        """Build each LIVING agent's firewall-filtered field of view for one tick.

        The one genuinely-expensive per-tick projection (Task 12.3; DESIGN.md §3.2
        fog, §7; stage-0 §0.5): a visibility solve per living agent per tick. Each
        view is captured from the agent's own ``ObservationPacket`` — the SAME
        pipeline output ``observation/service.py`` already assembles per tick
        (``engine.visibility.compute_visibility_for_player`` for the visual field,
        ``ObservationService._audible_events`` for the audio field) — so the
        As-agent perspective *simulates* the firewall and can never expose an
        unseen entity (the UI leak test in ``tests/api/test_leak.py`` pins this).

        Visibility is NOT re-solved here: ``build_packet`` runs the solve once and
        this reads its already-firewall-filtered result, honouring the cost
        budget (the implementation hint's "do NOT re-solve a second time"). Dead
        agents are skipped — a dead agent has no field of view — so the per-agent
        map holds only living agents and the dead get ``visibility=None``.

        ``reopened_body_id`` keeps a JUST-reported body in the fog on its meeting
        frame: on a body-report tick ``engine.tick._apply_report`` has already
        marked the trigger body ``discovered_by``, and ``compute_visibility_for_player``
        excludes discovered bodies — so without this the reporter (and every
        co-located agent) would lose the body from their field of view on the
        exact frame they could see it (it still shows in ``tick.bodies`` + the
        report event). The fog is solved against a state with that one body
        re-opened so the view matches what the agents saw; pure read-side — the
        engine ``state``, its hash, and ``tick.bodies`` are untouched.
        """

        fog_state = state
        if reopened_body_id is not None and reopened_body_id in state.bodies:
            body = state.bodies[reopened_body_id]
            if body.discovered_by is not None:
                bodies = dict(state.bodies)
                bodies[reopened_body_id] = replace(body, discovered_by=None)
                fog_state = replace(state, bodies=bodies)

        visibility: dict[str, AgentVisibilityView] = {}
        for pid in sorted(fog_state.players):
            if not fog_state.players[pid].alive:
                continue
            packet = service.build_packet(
                world_state=fog_state, agent_id=pid, engine_events=events
            )
            visibility[pid] = _agent_visibility_view(packet)
        return visibility

    # -- DTO builders -----------------------------------------------------

    def _tick_view(
        self,
        tick: int,
        state: WorldState,
        events: Sequence[EngineEvent],
        meeting_id: str | None,
        visibility_by_agent: Mapping[str, AgentVisibilityView] | None = None,
        *,
        fixed_tasks_required_total: int,
    ) -> TickView:
        agent_states = tuple(
            self._agent_tick_state(state, pid, visibility_by_agent)
            for pid in sorted(state.players)
        )
        sabotage = state.sabotage
        sabotage_active = (
            (sabotage.kind,) if sabotage is not None and sabotage.active else ()
        )
        tasks_completed_total = sum(1 for t in state.tasks.values() if t.completed)
        tasks_required_total = len(state.tasks)
        return TickView(
            tick=tick,
            agent_states=agent_states,
            events=self._tick_events(state, events, meeting_id),
            sabotage_active=sabotage_active,
            # Spectator task counts are over per-player task *instances*
            # (DESIGN.md §3.2): ``state.tasks`` is keyed ``"{owner}:{map_task_id}"``,
            # so the total is the live instance count and is NOT bounded by the
            # map's task pool (14 instances at the canonical 9p/2i,
            # ``tasks_per_crewmate=2``, vs. the 12 map tasks).
            tasks_completed_total=tasks_completed_total,
            tasks_required_total=tasks_required_total,
            # Additive Phase-12 projections from the same re-walked state (§7):
            bodies=_bodies_view(state),
            sabotage=_sabotage_detail_view(state),
            advantage=_advantage_view(
                state,
                tasks_completed=tasks_completed_total,
                tasks_required=tasks_required_total,
                # The DISPLAY denominator is the FIXED game-start instance count
                # threaded from ``_walk`` — never this tick's shrinking
                # ``len(state.tasks)`` (which stays the live win-condition value).
                tasks_required_total=fixed_tasks_required_total,
            ),
        )

    def _agent_tick_state(
        self,
        state: WorldState,
        pid: str,
        visibility_by_agent: Mapping[str, AgentVisibilityView] | None = None,
    ) -> AgentTickStateView:
        player = state.players[pid]
        # ``visibility_by_agent`` only holds LIVING agents (the As-agent fog
        # projection, Task 12.3), so ``.get`` yields ``None`` for a dead agent —
        # which has no field of view to simulate. When the walk did not collect
        # visibility (the meeting-memory re-walk), the map is ``None`` and every
        # agent state carries ``visibility=None``.
        visibility = (
            visibility_by_agent.get(pid) if visibility_by_agent is not None else None
        )
        return AgentTickStateView(
            agent_id=pid,
            room_id=player.room if player.alive else None,
            is_alive=player.alive,
            is_venting=player.in_vent,
            task_progress=self._task_progress(state, pid, player.role),
            current_action=_current_action(player.last_action),
            visibility=visibility,
        )

    def _task_progress(self, state: WorldState, pid: str, role: str) -> float | None:
        if role == "IMPOSTOR":
            return None
        # Owner-scoped under the per-player keyspace (DESIGN.md §3.2): progress
        # aggregates only this agent's OWN task instances, so the denominator is
        # the agent's instance deal, never the global pool.
        owned = [task for task in state.tasks.values() if task.owner == pid]
        if not owned:
            return 0.0
        required = sum(task.required_ticks for task in owned)
        if required <= 0:
            return 0.0
        progress = sum(task.progress for task in owned)
        return progress / required

    def _tick_events(
        self,
        state: WorldState,
        events: Sequence[EngineEvent],
        meeting_id: str | None,
    ) -> tuple[TickEventView, ...]:
        views: list[TickEventView] = []
        for event in events:
            if isinstance(event, KilledEvent):
                views.append(
                    KillEventView(
                        type="kill",
                        tick=event.tick,
                        killer_id=event.actor,
                        victim_id=event.target,
                        room_id=event.room,
                    )
                )
            elif isinstance(event, TaskCompletedEvent):
                views.append(
                    TaskCompletedEventView(
                        type="task_completed",
                        tick=event.tick,
                        agent_id=event.actor,
                        task_id=event.task_id,
                        room_id=self._game_map.tasks[event.task_id].room,
                    )
                )
            elif isinstance(event, (VentEnteredEvent, VentExitedEvent)):
                # Project the Phase-11 vent lever (DESIGN.md §3.2, §7): the
                # engine emits both endpoints with source/destination rooms +
                # traversal so the map can animate dive→travel→emerge. The
                # per-vent witness sets are the agent-facing firewall channel
                # (Task 12.3), deliberately not on the spectator timeline.
                views.append(
                    VentEventView(
                        type="vent",
                        tick=event.tick,
                        actor_id=event.actor,
                        phase=(
                            "enter" if isinstance(event, VentEnteredEvent) else "exit"
                        ),
                        from_room_id=event.source_room,
                        to_room_id=event.destination_room,
                        traversal_ticks=event.traversal_ticks,
                    )
                )
            elif isinstance(event, SabotageStartedEvent):
                # Project both sabotage kinds (DESIGN.md §8.3, Task 11.5): the
                # visibility ``lights`` and the task-gating ``reactor``, so the
                # contestable-clock win shape surfaces on the public timeline.
                # Narrowed explicitly (event.kind is ``str``) to keep the
                # SabotageEventView ``kind`` Literal mypy-clean and fail-loud on
                # an unknown kind.
                sabotage_view_kind: Literal["lights", "reactor"] | None = None
                if event.kind == "lights":
                    sabotage_view_kind = "lights"
                elif event.kind == "reactor":
                    sabotage_view_kind = "reactor"
                else:
                    raise ValueError(f"unprojectable sabotage kind: {event.kind}")
                views.append(
                    SabotageEventView(
                        type="sabotage",
                        tick=event.tick,
                        kind=sabotage_view_kind,
                        room_id=None,
                        actor_id=event.actor,
                    )
                )
            elif isinstance(event, MeetingTriggeredEvent):
                if meeting_id is None:
                    raise RuntimeError(
                        "MeetingTriggered event without a resolved meeting id"
                    )
                kind: _TriggerKind = (
                    "body" if event.trigger == "report" else "emergency"
                )
                views.append(
                    MeetingTriggeredEventView(
                        type="meeting_triggered",
                        tick=event.tick,
                        meeting_id=meeting_id,
                        triggered_by=event.actor,
                        trigger_kind=kind,
                    )
                )
                if event.trigger == "report" and event.body_id is not None:
                    body = state.bodies.get(event.body_id)
                    if body is not None:
                        views.append(
                            ReportBodyEventView(
                                type="report_body",
                                tick=event.tick,
                                reporter_id=event.actor,
                                body_of=body.player_id,
                                room_id=body.room,
                            )
                        )
        return tuple(views)

    def _meeting_view(
        self,
        entry: MeetingReplayEntry,
        trigger_kind_by_meeting_id: Mapping[str, _TriggerKind],
    ) -> MeetingView:
        return MeetingView(
            meeting_id=entry.meeting_id,
            tick=entry.tick,
            triggered_by=entry.triggered_by,
            trigger_kind=trigger_kind_by_meeting_id[entry.meeting_id],
            outcome=entry.outcome,
            ejected_player_id=entry.ejected_player_id,
            turns=tuple(_turn_view(t) for t in entry.transcript.turns),
            ballots=tuple(_ballot_view(b) for b in entry.ballots),
            contradictions=tuple(_contradiction_view(c) for c in entry.contradictions),
            llm_calls=tuple(
                _llm_call_view(call, entry.prompt_versions) for call in entry.llm_calls
            ),
            prompt_versions=dict(entry.prompt_versions),
            total_cost_usd=sum((call.cost_usd for call in entry.llm_calls), 0.0),
            gate=_gate_view(entry.ballots),
        )

    def _agent_memory_view(
        self,
        *,
        agent_id: str,
        tick: int,
        meeting_state: WorldState,
        memory: AgentMemory,
        meeting_entry: MeetingReplayEntry | None,
    ) -> AgentMemoryView:
        role = meeting_state.players[agent_id].role
        # Per-agent task counts are this agent's OWN instances only (owner-scoped
        # under the per-player keyspace, DESIGN.md §3.2); ``tasks_assigned`` is the
        # agent's instance deal and ``tasks_completed`` the done subset — never
        # another player's instances.
        owned = [
            task for task in meeting_state.tasks.values() if task.owner == agent_id
        ]

        # Observations are projected from the agent's own reconstructed episodic
        # memory (the same store ``rendered_memory_text`` renders), NOT from the
        # agent's submitted report — the report is a selective output and would
        # leave ``observations`` empty/inconsistent with the rendered view (and
        # empty for dead non-participants). Only the structured-claim event
        # types map: ``saw_body`` -> found_body and ``saw_player``. Heard cues
        # and completed-task inferences surface only in ``rendered_memory_text``.
        observations = _observations_from_memory(memory)

        open_contradictions: tuple[ContradictionView, ...] = ()
        if meeting_entry is not None:
            open_contradictions = tuple(
                _contradiction_view(c)
                for c in meeting_entry.contradictions
                if agent_id in c.subjects
            )

        beliefs = tuple(
            _belief_entry_view(memory, subject, tick)
            for subject in sorted(memory.beliefs.known_players())
        )
        return AgentMemoryView(
            agent_id=agent_id,
            tick=tick,
            role=role,
            tasks_completed=sum(1 for task in owned if task.completed),
            tasks_assigned=len(owned),
            observations=observations,
            beliefs=beliefs,
            open_contradictions=open_contradictions,
            rendered_memory_text=render_for_prompt(
                memory, token_budget=DEFAULT_TOKEN_BUDGET
            ),
        )

    def _file_summary(self, path: Path) -> _ReplaySummary:
        """Return the memoized one-pass reduction for ``path`` (Audit G-G-2)."""

        return self._cached_summary(path, _mtime_ns(path))

    def _read_summary(self, path: Path, _mtime_key: int) -> _ReplaySummary:
        # Walk the file once and derive every listing/cost field from the single
        # entry list (Audit G-G-2): cost folds each meeting's ``llm_calls`` plus
        # every failed-call row (mirrors ``compute_cost_usd``); ``winner`` is the
        # game-end record (mirrors ``read_game_outcome``). ``_mtime_key`` keys the
        # cache only (Audit H-H-2).
        tick_count = 0
        meeting_count = 0
        winner: WinnerSide | None = None
        winner_reason: str | None = None
        total_cost = 0.0
        prompt_versions: dict[str, str] = {}
        for entry in read_all_entries(path):
            if isinstance(entry, ReplayEntry):
                tick_count += 1
            elif isinstance(entry, MeetingReplayEntry):
                meeting_count += 1
                total_cost += sum((call.cost_usd for call in entry.llm_calls), 0.0)
                prompt_versions.update(entry.prompt_versions)
            elif isinstance(entry, GameEndReplayEntry):
                winner = entry.winner
                winner_reason = entry.reason
            elif isinstance(entry, FailedCallReplayEntry):
                total_cost += entry.cost_usd
        return _ReplaySummary(
            total_ticks=tick_count,
            meeting_count=meeting_count,
            winner=winner,
            winner_reason=winner_reason,
            total_cost_usd=total_cost,
            prompt_versions=prompt_versions,
        )

    def _metadata_view(self, path: Path, seed: int) -> ReplayMetadataView:
        summary = self._file_summary(path)
        return ReplayMetadataView(
            game_id=_game_id_for_seed(seed),
            seed=seed,
            total_ticks=summary.total_ticks,
            winner=summary.winner,
            winner_reason=summary.winner_reason,
            meeting_count=summary.meeting_count,
            total_cost_usd=summary.total_cost_usd,
            prompt_versions=dict(summary.prompt_versions),
            created_at=_iso_mtime(path),
        )

    def _players_view(self, initial_state: WorldState) -> tuple[PlayerView, ...]:
        return tuple(
            PlayerView(
                agent_id=pid,
                display_name=_display_name(pid),
                role=initial_state.players[pid].role,
                color=_color_for(pid),
            )
            for pid in sorted(initial_state.players)
        )

    def _build_map_view(self) -> MapLayoutView:
        rooms = tuple(
            RoomView(
                id=room.id,
                name=room.name,
                position=PositionView(
                    x=float(room.position.x), y=float(room.position.y)
                ),
                size=SizeView(
                    width=float(room.size.width), height=float(room.size.height)
                ),
            )
            for room in sorted(self._game_map.rooms.values(), key=lambda r: r.id)
        )
        vents = tuple(
            VentView(
                id=vent.id,
                room_id=vent.room,
                connected_room_ids=tuple(
                    self._game_map.vents[connected].room
                    for connected in vent.connects_to
                ),
            )
            for vent in sorted(self._game_map.vents.values(), key=lambda v: v.id)
        )
        edges = tuple(
            EdgeView(
                from_room_id=edge.from_room,
                to_room_id=edge.to_room,
                is_door=edge.kind == "doorway",
            )
            for edge in self._game_map.edges
        )
        return MapLayoutView(rooms=rooms, vents=vents, edges=edges)

    # -- path / seed helpers ----------------------------------------------

    def _replay_paths(self) -> list[tuple[int, Path]]:
        if not self._replay_dir.exists():
            return []
        pairs: list[tuple[int, Path]] = []
        for path in self._replay_dir.glob("replay-seed-*.jsonl"):
            if not path.is_file():
                continue
            seed = _parse_seed_from_filename(path.name)
            if seed is None:
                continue
            pairs.append((seed, path))
        # Sort by (seed, filename) and keep one canonical file per seed. Two
        # filenames can map to the same seed (e.g. ``replay-seed-1`` vs
        # ``replay-seed-01``); deduplicating with a deterministic tie-break (the
        # lexicographically-first filename) keeps ``game_id`` unique in
        # ``list_replays`` and makes ``_resolve_path`` pick the same file across
        # runs despite ``Path.glob`` having unspecified order.
        pairs.sort(key=lambda pair: (pair[0], pair[1].name))
        deduped: list[tuple[int, Path]] = []
        seen: set[int] = set()
        for seed, path in pairs:
            if seed in seen:
                continue
            seen.add(seed)
            deduped.append((seed, path))
        return deduped

    def _resolve(self, game_id: str) -> tuple[Path, int]:
        """Resolve ``game_id`` to its ``(path, seed)`` or raise FileNotFoundError.

        Centralizes the lookup the cached entry points share so the file's mtime
        can be folded into their cache keys (Audit H-H-2) without each caller
        re-deriving the path.
        """

        path = self._resolve_path(game_id)
        seed = _parse_seed_from_game_id(game_id)
        if path is None or seed is None:
            raise FileNotFoundError(game_id)
        return path, seed

    def _resolve_path(self, game_id: str) -> Path | None:
        # Resolve by matching the discovered seed rather than reconstructing the
        # canonical filename, so a file `list_replays` advertised (e.g. a
        # zero-padded `replay-seed-01.jsonl` surfaced as `headless-seed-1`) is
        # always fetchable by the game_id it was advertised under.
        seed = _parse_seed_from_game_id(game_id)
        if seed is None:
            return None
        for found_seed, path in self._replay_paths():
            if found_seed == seed:
                return path
        return None

    def _roster_mtime(self) -> int:
        """Nanosecond mtime of the per-set ``roster.json`` for the LRU key.

        Returns ``-1`` when the descriptor is absent — a sentinel distinct from
        any real ``st_mtime_ns`` — so that adding, changing, or removing the
        sidecar all change the reconstruction cache key and invalidate any
        previously-cached walk (Audit H-H-2 parity for the roster sidecar).
        """

        try:
            return (self._replay_dir / _ROSTER_FILENAME).stat().st_mtime_ns
        except OSError:
            return -1


# ---------------------------------------------------------------------------
# Module-level helpers (pure; no loader state)
# ---------------------------------------------------------------------------


def _game_id_for_seed(seed: int) -> str:
    return f"headless-seed-{seed}"


def _meeting_id_for(game_id: str, index: int) -> str:
    return f"{game_id}:meeting-{index}"


def _parse_seed_from_game_id(game_id: str) -> int | None:
    match = _GAME_ID_PATTERN.fullmatch(game_id)
    return int(match.group(1)) if match is not None else None


def _parse_seed_from_filename(name: str) -> int | None:
    match = _FILENAME_PATTERN.fullmatch(name)
    return int(match.group(1)) if match is not None else None


def _display_name(agent_id: str) -> str:
    match = _PLAYER_ID_PATTERN.fullmatch(agent_id)
    return f"Player {match.group(1)}" if match is not None else agent_id


def _color_for(agent_id: str) -> str:
    match = _PLAYER_ID_PATTERN.fullmatch(agent_id)
    if match is not None:
        return _COLOR_PALETTE[(int(match.group(1)) - 1) % len(_COLOR_PALETTE)]
    return "#" + hashlib.sha256(agent_id.encode("utf-8")).hexdigest()[:6]


def _iso_mtime(path: Path) -> str | None:
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return None
    return datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()


def _mtime_ns(path: Path) -> int:
    """Nanosecond mtime of ``path`` for use as a cache-key component.

    Nanosecond resolution (``st_mtime_ns``) so an in-place rewrite within the
    same wall-clock second still changes the key (Audit H-H-2). Unlike
    :func:`_iso_mtime` this does not swallow ``OSError``: a path being summarized
    or loaded was already resolved to an existing file, so a stat failure here is
    a real error rather than a missing-timestamp cosmetic.
    """

    return path.stat().st_mtime_ns


def _deserialize_actions(raw_actions: Sequence[Mapping[str, Any]]) -> list[Action]:
    return [_ACTION_ADAPTER.validate_python(dict(raw)) for raw in raw_actions]


def _infer_num_players(replay_entries: Sequence[ReplayEntry]) -> int:
    """Recover the player count from the recorded action stream.

    The replay format does not persist the roster (only the seed, via
    ``game_id``), and producers accept non-default ``--num-players``. The seeder
    names players ``p-1 .. p-{num_players}`` and the orchestrator solicits one
    action per alive agent every tick, so a real game's actions name every
    player; the max ``p-N`` index across all recorded actions therefore recovers
    ``num_players``. Falls back to :data:`DEFAULT_NUM_PLAYERS` when no actions
    were recorded (e.g. a synthetic no-op replay). ``num_impostors`` is not
    inferable and stays pinned to the MVP-invariant default (DESIGN.md §8.1/§8.2:
    one impostor). A wrong inference cannot corrupt output: the per-tick
    state-hash check fails loud instead.
    """

    max_index = 0
    for entry in replay_entries:
        for raw_action in entry.actions:
            actor = raw_action.get("actor")
            if not isinstance(actor, str):
                continue
            match = _PLAYER_ID_PATTERN.fullmatch(actor)
            if match is not None:
                max_index = max(max_index, int(match.group(1)))
    return max_index if max_index > 0 else DEFAULT_NUM_PLAYERS


_ROSTER_FIELDS: Final[tuple[str, ...]] = (
    "num_players",
    "num_impostors",
    "tasks_per_crewmate",
)


def _load_roster_config(replay_dir: Path) -> RosterConfig | None:
    """Parse ``<replay_dir>/roster.json`` into a :class:`RosterConfig`, or None.

    Returns ``None`` when the directory has NO ``roster.json`` — the only path
    that defaults: the flat 4p/1i baseline re-seeds with ``num_impostors=
    DEFAULT_NUM_IMPOSTORS`` and ``tasks_per_crewmate=1`` and an inferred
    ``num_players`` (see :meth:`ReplayLoader._walk`).

    A descriptor that IS present must be well-formed: the JSON object must carry
    exactly :data:`_ROSTER_FIELDS`, each a positive integer. A missing key, an
    unexpected key, a non-integer (``bool`` included — ``true`` is not ``1``), or
    a non-positive value raises :class:`ValueError` rather than silently falling
    back to the default (AGENTS.md "no silent fallbacks"). Cross-field roster
    validity (``2 <= num_players`` and ``num_impostors < num_players``) is left to
    :func:`orchestrator.seeder.seed_initial_state`, the single source of truth for
    it, which raises at re-seed time.
    """

    path = replay_dir / _ROSTER_FILENAME
    if not path.exists():
        return None
    # Present but not a regular file (e.g. a directory from a bad checkout/setup)
    # is a malformed descriptor, NOT the absent/default case — the contract
    # reserves "no descriptor" for an ABSENT ``roster.json``, so fail loud rather
    # than silently re-seeding 4p/1i.
    if not path.is_file():
        raise ValueError(f"roster descriptor {path} exists but is not a regular file")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid roster descriptor {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError(
            f"invalid roster descriptor {path}: expected a JSON object, got "
            f"{type(raw).__name__}"
        )
    keys = set(raw)
    expected = set(_ROSTER_FIELDS)
    missing = expected - keys
    if missing:
        raise ValueError(
            f"invalid roster descriptor {path}: missing key(s) "
            f"{', '.join(sorted(missing))}"
        )
    unexpected = keys - expected
    if unexpected:
        raise ValueError(
            f"invalid roster descriptor {path}: unexpected key(s) "
            f"{', '.join(sorted(unexpected))}"
        )
    values: dict[str, int] = {}
    for key in _ROSTER_FIELDS:
        value = raw[key]
        # ``bool`` is an ``int`` subclass; reject it so ``true`` is not read as 1.
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(
                f"invalid roster descriptor {path}: {key} must be an integer, "
                f"got {value!r}"
            )
        if value < 1:
            raise ValueError(
                f"invalid roster descriptor {path}: {key} must be a positive "
                f"integer, got {value}"
            )
        values[key] = value
    return RosterConfig(
        num_players=values["num_players"],
        num_impostors=values["num_impostors"],
        tasks_per_crewmate=values["tasks_per_crewmate"],
    )


def _meeting_trigger_from_events(
    events: Sequence[EngineEvent],
) -> tuple[_TriggerKind, str | None]:
    trigger_event: MeetingTriggeredEvent | None = None
    for event in events:
        if isinstance(event, MeetingTriggeredEvent):
            trigger_event = event
    if trigger_event is None:
        raise RuntimeError(
            "engine entered MEETING phase without a MeetingTriggered event"
        )
    if trigger_event.trigger == "report":
        return "body", trigger_event.body_id
    return "emergency", None


def _meeting_result_from_entry(entry: MeetingReplayEntry) -> MeetingResult:
    return MeetingResult(
        meeting_id=entry.meeting_id,
        triggered_by=entry.triggered_by,
        trigger_tick=entry.tick,
        outcome=entry.outcome,
        ejected_player_id=entry.ejected_player_id,
        ballots=entry.ballots,
        contradictions=entry.contradictions,
        transcript=entry.transcript,
    )


def _current_action(
    last_action: Action | None,
) -> Literal["IDLE", "MOVING", "TASK", "KILL", "VENT", "REPORT", "SABOTAGE"]:
    if last_action is None:
        return "IDLE"
    kind = last_action.type
    if kind == "move":
        return "MOVING"
    if kind == "do_task":
        return "TASK"
    if kind == "kill":
        return "KILL"
    if kind == "vent":
        return "VENT"
    if kind in ("report", "emergency"):
        return "REPORT"
    if kind == "sabotage":
        return "SABOTAGE"
    if kind == "repair_sabotage":
        return "TASK"
    return "IDLE"


def _observations_from_memory(
    memory: AgentMemory,
) -> tuple[SawPlayerView | CompletedTaskObsView | FoundBodyObsView, ...]:
    """Project an agent's reconstructed episodic memory into observation DTOs.

    Only the two episodic event types that map onto the structured-claim union
    are surfaced: ``saw_body`` -> :class:`FoundBodyObsView` (deduplicated by
    body id, as the renderer does) and ``saw_player`` -> :class:`SawPlayerView`.
    Salience order matches DESIGN.md §6.2: body discoveries first, then
    sightings; within each group, most-recent tick first. ``co_present`` is not
    captured per-sighting in the episodic store, so it is left empty.
    """

    found: list[FoundBodyObsView] = []
    seen_bodies: set[str] = set()
    sightings: list[SawPlayerView] = []
    for event in memory.episodic.recent(since_tick=0):
        if event.type == EVENT_SAW_BODY:
            body_id = event.payload.get("body_id")
            victim = event.payload.get("victim_id")
            room = event.payload.get("room")
            if not (
                isinstance(body_id, str)
                and isinstance(victim, str)
                and isinstance(room, str)
            ):
                continue
            if body_id in seen_bodies:
                continue
            seen_bodies.add(body_id)
            found.append(
                FoundBodyObsView(
                    type="found_body", tick=event.tick, body_of=victim, room=room
                )
            )
        elif event.type == EVENT_SAW_PLAYER:
            subject = event.payload.get("player_id")
            room = event.payload.get("room")
            if not (isinstance(subject, str) and isinstance(room, str)):
                continue
            sightings.append(
                SawPlayerView(
                    type="saw_player",
                    tick=event.tick,
                    subject=subject,
                    room=room,
                    co_present=(),
                )
            )
    found.sort(key=lambda obs: obs.tick, reverse=True)
    sightings.sort(key=lambda obs: obs.tick, reverse=True)
    return (*found, *sightings)


def _observation_claim_view(
    claim: ObservationClaim,
) -> SawPlayerView | CompletedTaskObsView | FoundBodyObsView:
    if isinstance(claim, SawPlayerObservation):
        return SawPlayerView(
            type="saw_player",
            tick=claim.tick,
            subject=claim.subject,
            room=claim.room,
            co_present=tuple(claim.co_present),
        )
    if isinstance(claim, CompletedTaskObservation):
        return CompletedTaskObsView(
            type="completed_task",
            tick=claim.tick,
            task_id=claim.task_id,
            room=claim.room,
        )
    if isinstance(claim, FoundBodyObservation):
        return FoundBodyObsView(
            type="found_body",
            tick=claim.tick,
            body_of=claim.body_of,
            room=claim.room,
        )
    raise TypeError(f"unsupported observation claim: {type(claim).__name__}")


def _statement_claim_view(
    claim: Claim,
) -> AlibiClaimView | AccusationClaimView | CorroborationClaimView:
    if isinstance(claim, AlibiClaim):
        return AlibiClaimView(
            type="alibi",
            subject=claim.subject,
            from_tick=claim.from_tick,
            to_tick=claim.to_tick,
            room=claim.room,
            evidence=tuple(claim.evidence),
        )
    if isinstance(claim, AccusationClaim):
        return AccusationClaimView(
            type="accusation",
            against=claim.against,
            confidence=claim.confidence,
            reason=claim.reason,
        )
    if isinstance(claim, CorroborationClaim):
        return CorroborationClaimView(
            type="corroboration",
            supports=claim.supports,
            on_tick=claim.on_tick,
            reason=claim.reason,
        )
    raise TypeError(f"unsupported statement claim: {type(claim).__name__}")


def _turn_view(turn: MeetingTurn) -> TurnView:
    # An emergency opening that fabricated a found_body carries the deterministic
    # strip marker in its free_text (meetings.manager). Parse it server-side via
    # the imported constant (DESIGN.md §3.4 — never hard-code a marker in TS): drop
    # the dev-jargon string (it may sit among other audit markers, not only at the
    # front) and surface a role-neutral ``fabricated_opening`` flag the transcript
    # renders as a "FABRICATED" chip. The marker constant includes its trailing
    # space, so removing it leaves no double space.
    free_text = turn.free_text
    fabricated_opening = EMERGENCY_BODY_STRIP_MARKER in free_text
    if fabricated_opening:
        free_text = free_text.replace(EMERGENCY_BODY_STRIP_MARKER, "")
    return TurnView(
        turn_id=turn.turn_id,
        turn_index=turn.turn_index,
        speaker=turn.speaker,
        turn_kind=turn.turn_kind,
        reply_to=turn.reply_to,
        observations=tuple(_observation_claim_view(o) for o in turn.observations),
        claims=tuple(_statement_claim_view(c) for c in turn.claims),
        free_text=free_text,
        fabricated_opening=fabricated_opening,
    )


def _contradiction_view(contradiction: ContradictionRef) -> ContradictionView:
    # Lift the weak/strong class out of the free-text ``description`` marker via
    # the canonical predicate (imported, never re-implemented) so the meeting
    # view can draw weak=dashed / strong=solid without re-parsing client-side.
    # ``kind`` passes through verbatim -- the Task 13.4 ``alibi_vs_physical`` kind
    # a recorded ``MeetingResult`` carries (the manager persists
    # ``detect_contradictions`` at close) renders like the other alibi kinds.
    weak = is_weak_contradiction(contradiction)
    return ContradictionView(
        contradiction_id=contradiction.contradiction_id,
        kind=contradiction.kind,
        event_a_id=contradiction.event_a_id,
        event_b_id=contradiction.event_b_id,
        subjects=tuple(contradiction.subjects),
        description=contradiction.description,
        weak=weak,
        severity="weak" if weak else "strong",
    )


def _ballot_view(ballot: VoteBallot) -> BallotView:
    reasons, clean = _parse_rewrite_reasons(ballot.rationale_text)
    return BallotView(
        voter=ballot.voter,
        target=ballot.target,
        confidence=ballot.confidence,
        primary_reason_id=ballot.primary_reason_id,
        considered_alternatives=tuple(ballot.considered_alternatives),
        rationale_text=ballot.rationale_text,
        rewrite_reasons=reasons,
        rationale_text_clean=clean,
    )


def _failed_call_view(entry: FailedCallReplayEntry) -> FailedCallView:
    return FailedCallView(
        meeting_id=entry.meeting_id,
        tick=entry.tick,
        model=entry.model,
        cost_usd=entry.cost_usd,
        error_type=entry.error_type,
        error_message=entry.error_message[:200],
    )


def _llm_call_view(
    call: LLMCallRecord, prompt_versions: Mapping[str, str]
) -> LLMCallView:
    return LLMCallView(
        call_kind=call.call_kind,
        model=call.model,
        prompt_template_id=_classify_template_id(call, prompt_versions),
        prompt_text=call.prompt,
        response_text=call.response_text,
        input_tokens=call.input_tokens,
        output_tokens=call.output_tokens,
        cost_usd=call.cost_usd,
        agent_id=call.agent_id,
    )


def _classify_template_id(
    call: LLMCallRecord, prompt_versions: Mapping[str, str]
) -> str:
    """Best-effort template id for one captured LLM call.

    ``LLMCallRecord`` does not persist which prompt template produced a call, so
    the template is inferred from stable markers in the (frozen) rendered prompt
    bodies and mapped to the recorded ``prompt_versions``. Falls back to the
    ``call_kind`` tier when the marker set does not match.

    Markers track the meeting templates across prompt sets. The qwen3_32b.v3 set
    (Task 14.7) renamed the section headers, so each key is matched by its
    qwen3_32b.v3 marker OR the legacy qwen3.5:9b literal (back-compat): the vote
    prompt is the only one with "## Valid ejection targets" (v3) / "casting a
    vote" (9B); the impostor opening the only one with "## Your cover" (v3) /
    "Your role for this match is IMPOSTOR" (9B); the crewmate opening leads with
    "## This meeting" (v3) / "opening speaker" (9B); and the reply / opt-in turns
    carry "## Your turn: a reply" or "## Your turn: an info-share" (v3) /
    "reactive accusation chain" (9B). Vote and impostor markers are checked first
    so they cannot be shadowed by a section echo in a later template.
    """

    if call.call_kind == "trigger":
        return "trigger"
    prompt = call.prompt
    if "## Valid ejection targets" in prompt or "casting a vote" in prompt:
        key = "vote_ballot"
    elif "## Your cover" in prompt or "Your role for this match is IMPOSTOR" in prompt:
        key = "impostor_report"
    elif "## This meeting" in prompt or "opening speaker" in prompt:
        key = "crewmate_report"
    elif (
        "## Your turn: a reply" in prompt
        or "## Your turn: an info-share" in prompt
        or "reactive accusation chain" in prompt
    ):
        key = "accusation_round"
    else:
        return call.call_kind
    return prompt_versions.get(key, key)


def _belief_entry_view(memory: AgentMemory, subject: str, tick: int) -> BeliefEntryView:
    belief = memory.beliefs.view(subject)
    return BeliefEntryView(
        subject=subject,
        suspicion=belief.suspicion,
        confidence=min(1.0, abs(belief.suspicion - 0.5) * 2.0),
        snapshot_tick=tick,
    )


# ---------------------------------------------------------------------------
# Phase-12 additive projections (Task 12.2; DESIGN.md §7). All derive from the
# already-re-walked engine state / persisted meeting records — nothing new is
# persisted and no replay is re-recorded.
# ---------------------------------------------------------------------------


def _agent_visibility_view(packet: ObservationPacket) -> AgentVisibilityView:
    """Project a firewall-filtered ``ObservationPacket`` into the As-agent fog DTO.

    Task 12.3 (DESIGN.md §3.2 fog, §1.3 firewall). Carries only the visual field
    (``visible_players`` / ``visible_bodies``) and the audio field
    (``audible_events``) the packet already exposes — NEVER the privileged self
    channel (``self_state.role`` / ``fellow_impostor_ids`` / ``pending_task_id`` /
    ``own_kill``, or ``cooldown``), which are exactly the fields the As-agent view
    must hide. The agent-facing ``observation.packet.BodyView`` carries no
    ``killed_by`` (only the privileged spectator :class:`BodyView` does), so the
    kill attribution cannot leak through this projection by construction.
    """

    return AgentVisibilityView(
        visible_players=tuple(
            VisiblePlayerView(id=player.id, room=player.room, action=player.action)
            for player in packet.visible_players
        ),
        visible_bodies=tuple(
            VisibleBodyView(id=body.id, room=body.room, victim_id=body.victim_id)
            for body in packet.visible_bodies
        ),
        audible_events=tuple(
            AudibleEventView(kind=event.kind, room=event.room)
            for event in packet.audible_events
        ),
    )


def _bodies_view(state: WorldState) -> tuple[BodyView, ...]:
    """Project every body on the floor this tick (persistent ``killed_by``)."""

    return tuple(
        BodyView(
            body_id=body.id,
            victim_id=body.player_id,
            room_id=body.room,
            killed_by=body.killed_by,
        )
        for body in sorted(state.bodies.values(), key=lambda b: b.id)
    )


def _sabotage_detail_view(state: WorldState) -> SabotageDetailView | None:
    """Project the active sabotage's repair race + countdown, or ``None``."""

    sabotage = state.sabotage
    if sabotage is None or not sabotage.active:
        return None
    # Narrow the engine's ``str`` kind to the projected Literal, fail-loud on an
    # unknown kind (mirrors ``_tick_events``' SabotageStarted handling).
    kind: Literal["lights", "reactor"]
    if sabotage.kind == "lights":
        kind = "lights"
    elif sabotage.kind == "reactor":
        kind = "reactor"
    else:
        raise ValueError(f"unprojectable sabotage kind: {sabotage.kind}")
    return SabotageDetailView(
        kind=kind,
        remaining_ticks=sabotage.remaining_ticks,
        affected_rooms=tuple(sabotage.affected_rooms),
        repair_progress=dict(sabotage.repair_progress),
    )


def _advantage_view(
    state: WorldState,
    *,
    tasks_completed: int,
    tasks_required: int,
    tasks_required_total: int,
) -> AdvantageView:
    """Project the per-tick crew/impostor advantage frame (DESIGN.md §4, §7).

    The counts are authoritative; ``advantage`` is a single signed render
    heuristic in ``[-1, 1]`` (positive favours the crew): the crew task clock
    (``tasks_completed / tasks_required``) minus impostor parity pressure
    (``impostors_alive / max(crew_alive, 1)``, → 1.0 at parity), clamped. It
    starts mildly negative (impostors hold the initiative), rises as the crew
    completes tasks, and falls as kills approach parity.

    ``tasks_required`` is the LIVE win-condition denominator (``len(state.tasks)``
    this tick) and drives the curve. ``tasks_required_total`` is the FIXED
    game-start instance count threaded in from the caller — it never changes
    across a game and is the stable DISPLAY denominator for the roster meter
    (the live count shrinks as crewmates die; see ``AdvantageView``).
    """

    crew_alive = sum(
        1 for p in state.players.values() if p.alive and p.role == "CREWMATE"
    )
    impostors_alive = sum(
        1 for p in state.players.values() if p.alive and p.role == "IMPOSTOR"
    )
    task_progress = (tasks_completed / tasks_required) if tasks_required > 0 else 0.0
    impostor_pressure = impostors_alive / crew_alive if crew_alive > 0 else 1.0
    advantage = max(-1.0, min(1.0, task_progress - impostor_pressure))
    return AdvantageView(
        crew_alive=crew_alive,
        impostors_alive=impostors_alive,
        tasks_completed=tasks_completed,
        tasks_required=tasks_required,
        tasks_required_total=tasks_required_total,
        advantage=advantage,
    )


def _gate_view(ballots: Sequence[VoteBallot]) -> GateView:
    """Recompute the per-meeting §4.6 verdict from the persisted ballots.

    Mirrors :func:`meetings.voting.tally_ballots` exactly — plurality + at least
    one leader ballot ``confidence >= threshold`` (0.6); a SKIP plurality or a
    tie of non-SKIP targets → no leader / not passed — so ``passed`` matches the
    recorded outcome and ``leader`` the recorded ``ejected_player_id``. The
    template-time ``rendered_max`` is intentionally dropped (it is transient and
    only persisted on failed calls).
    """

    threshold = DEFAULT_SKIP_CONFIDENCE_THRESHOLD
    tallies: dict[str, int] = {}
    for ballot in ballots:
        tallies[ballot.target] = tallies.get(ballot.target, 0) + 1
    if not tallies:
        return GateView(
            leader=None, leader_max_confidence=0.0, threshold=threshold, passed=False
        )
    max_votes = max(tallies.values())
    leaders = sorted(target for target, count in tallies.items() if count == max_votes)
    if SKIP_TARGET in leaders or len(leaders) > 1:
        return GateView(
            leader=None, leader_max_confidence=0.0, threshold=threshold, passed=False
        )
    leader = leaders[0]
    leader_max_confidence = max(b.confidence for b in ballots if b.target == leader)
    return GateView(
        leader=leader,
        leader_max_confidence=leader_max_confidence,
        threshold=threshold,
        passed=leader_max_confidence >= threshold,
    )


# (label, marker) for the audit markers the meeting layer prepends to a ballot's
# ``rationale_text``. Imported from ``meetings.voting`` / ``meetings.manager`` —
# never hard-coded, since the markers are ``.format()``-interpolated and a
# rename must break loudly here. The label is the stable, frontend-renderable
# chip id. ``VOTE_PARSE_DEFAULT`` is handled separately: it is the WHOLE
# rationale, not a prefix.
_BALLOT_PREFIX_MARKERS: Final[tuple[tuple[str, str], ...]] = (
    ("invalid_target", INVALID_VOTE_TARGET_MARKER),
    ("teammate_coerced", TEAMMATE_VOTE_TARGET_MARKER),
    ("under_gate_redirect", BALLOT_TARGET_REDIRECT_MARKER),
    ("invalid_reason_id", INVALID_REASON_ID_MARKER),
)
_VOTE_PARSE_DEFAULT_LABEL: Final[str] = "parse_default"

# Every audit marker interpolates its payload with ``{x!r}`` — i.e. a Python
# ``repr`` of a string, which is always quoted (single, or double when the value
# contains a single quote) with backslash escapes. Matching the payload as a
# quoted literal (rather than scanning for the static tail) makes the parse
# robust when the ORIGINAL invalid value itself contains the marker's tail text
# (e.g. a hallucinated target ``"x normalized to SKIP] y"``): the quote-matching
# consumes the whole value first, so the strip stops at the REAL marker end, not
# inside the payload.
_MARKER_REPR_VALUE: Final[str] = r"(?:'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")"


def _marker_pattern(marker: str) -> re.Pattern[str]:
    """Anchored regex matching one whole ``.format()`` marker (head + repr + tail)."""

    head, _, rest = marker.partition("{")
    _, _, tail = rest.partition("}")
    return re.compile("^" + re.escape(head) + _MARKER_REPR_VALUE + re.escape(tail))


# Precompiled prefix-marker patterns + the parse-default head (its whole-string
# special case only needs the static head).
_BALLOT_PREFIX_PATTERNS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = tuple(
    (label, _marker_pattern(marker)) for label, marker in _BALLOT_PREFIX_MARKERS
)
_VOTE_PARSE_DEFAULT_HEAD: Final[str] = VOTE_PARSE_DEFAULT_MARKER.partition("{")[0]


def _parse_rewrite_reasons(rationale_text: str) -> tuple[tuple[str, ...], str]:
    """Parse the firewall/parse audit markers off a ballot's ``rationale_text``.

    Returns ``(rewrite_reasons, rationale_text_clean)``.
    :data:`~meetings.manager.VOTE_PARSE_DEFAULT_MARKER` is the WHOLE rationale
    (the manager's vote fail-soft authored no model text) and is special-cased:
    the entire string is consumed and the clean remainder is empty. The other
    markers are prepended prefixes (possibly stacked, e.g. an invalid target
    plus a nulled reason id) and are stripped front-to-back via their
    repr-aware patterns (see :data:`_MARKER_REPR_VALUE`), leaving the
    model-authored text. Patterns are built from the imported constants, never a
    hard-coded literal.
    """

    if rationale_text.startswith(_VOTE_PARSE_DEFAULT_HEAD):
        return (_VOTE_PARSE_DEFAULT_LABEL,), ""

    reasons: list[str] = []
    text = rationale_text
    stripped = True
    while stripped:
        stripped = False
        for label, pattern in _BALLOT_PREFIX_PATTERNS:
            match = pattern.match(text)
            if match is None:
                continue
            reasons.append(label)
            text = text[match.end() :]
            stripped = True
            break
    return tuple(reasons), text


# Neutral suspicion prior for a NO-BELIEF cell — mirrors the belief store's
# ``_DEFAULT_SUSPICION`` (agents.memory.beliefs) so a never-observed subject is
# the same 0.5 "no lean" the engine would use. Placeholder only: a no-belief
# cell is flagged ``has_belief=False`` and rendered as "NO BELIEF YET", never as
# this magnitude.
_NO_BELIEF_SUSPICION: Final[float] = 0.5


def _belief_frames_from_memories(
    memories: Mapping[tuple[str, str], AgentMemoryView],
) -> tuple[BeliefFrameView, ...]:
    """Reshape per-(meeting, agent) memory snapshots into per-meeting belief
    matrices with the Error projection vs ground-truth role (DESIGN.md §3.3).

    Each frame is the FULL N×N observer×subject grid over the roster (every
    player snapshotted at the meeting), so the hero 9×9 matrix renders as a
    stable square with no client-side synthesis. Two ``has_belief=False`` cases
    are distinct by ``observer == subject``: the **diagonal** self cell (N/A — an
    agent holds no belief about itself) and a **NO BELIEF YET** off-diagonal cell
    (the subject is absent from the observer's sparse belief store) — the latter
    kept explicit so it reads distinct from a genuine neutral/low suspicion
    ("no belief yet" ≠ 0). Both carry the neutral 0.5 prior so the
    ``error == suspicion - truth`` invariant stays total. Each agent's ``role``
    is static, so any snapshot carries its true role; the subject's role drives
    ``subject_is_impostor`` and the signed ``error``. One frame per meeting,
    deterministically ordered (meeting id, observer id, subject id).
    """

    role_by_agent: dict[str, str] = {
        agent_id: view.role for (_, agent_id), view in memories.items()
    }
    roster = sorted(role_by_agent)
    by_meeting: dict[str, list[AgentMemoryView]] = {}
    meeting_tick: dict[str, int] = {}
    for (meeting_id, _), view in memories.items():
        by_meeting.setdefault(meeting_id, []).append(view)
        meeting_tick[meeting_id] = view.tick

    frames: list[BeliefFrameView] = []
    for meeting_id in sorted(by_meeting):
        entries: list[BeliefErrorView] = []
        for view in sorted(by_meeting[meeting_id], key=lambda v: v.agent_id):
            held = {belief.subject: belief for belief in view.beliefs}
            for subject in roster:
                subject_is_impostor = role_by_agent.get(subject) == "IMPOSTOR"
                truth = 1.0 if subject_is_impostor else 0.0
                belief = held.get(subject)
                if subject != view.agent_id and belief is not None:
                    suspicion, confidence, has_belief = (
                        belief.suspicion,
                        belief.confidence,
                        True,
                    )
                else:
                    # Diagonal (self, N/A) or no stored belief -> the neutral
                    # prior, flagged has_belief=False. The diagonal is the
                    # ``observer == subject`` cell; NO BELIEF YET is the rest.
                    suspicion, confidence, has_belief = _NO_BELIEF_SUSPICION, 0.0, False
                entries.append(
                    BeliefErrorView(
                        observer=view.agent_id,
                        subject=subject,
                        suspicion=suspicion,
                        confidence=confidence,
                        subject_is_impostor=subject_is_impostor,
                        error=suspicion - truth,
                        has_belief=has_belief,
                    )
                )
        frames.append(
            BeliefFrameView(
                meeting_id=meeting_id,
                tick=meeting_tick[meeting_id],
                entries=tuple(entries),
            )
        )
    return tuple(frames)


def _manifest_git_sha(replay_dir: Path) -> str | None:
    """The single distinct git sha across the set's ``MANIFEST.md`` data rows.

    Returns ``None`` when the manifest is absent, carries no data rows, or holds
    more than one distinct sha (a piecemeal-refreshed set) — any of which makes a
    clean freshness comparison impossible, so :func:`_rubric_is_stale` reports
    the rubric stale rather than silently fresh.
    """

    try:
        text = (replay_dir / _MANIFEST_FILENAME).read_text(encoding="utf-8")
    except OSError:
        return None
    shas: set[str] = set()
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.split("|")]
        if len(cells) < _MANIFEST_MIN_ROW_CELLS:
            continue
        # cells[0] is the empty leading cell; cells[1] is the seed (data rows
        # only — the header/separator rows fail the integer check).
        if not cells[1].lstrip("-").isdigit():
            continue
        sha = cells[_MANIFEST_GIT_SHA_FROM_END]
        if sha:
            shas.add(sha)
    return next(iter(shas)) if len(shas) == 1 else None


def _rubric_is_stale(git_head: str | None, manifest_sha: str | None) -> bool:
    """Whether the rubric's scoring commit disagrees with the set's record commit.

    Fresh iff both shas are present and one is a prefix of the other (the
    manifest stores a SHORT sha; the rubric a full ``git rev-parse HEAD``). Any
    missing sha → stale (the banner shows rather than a false "fresh").
    """

    if git_head is None or manifest_sha is None:
        return True
    return not (git_head.startswith(manifest_sha) or manifest_sha.startswith(git_head))


def _expected_seedset(replay_dir: Path) -> str | None:
    """The served set's identity (``"{players}p{impostors}i"``) from its roster.

    Read from the set's ``roster.json`` (the authoritative per-set descriptor),
    so it is cwd/name-independent: the canonical 9p2i set resolves to ``"9p2i"``.
    Returns ``None`` for the flat default (no ``roster.json``), which ships no
    rubric — there the seedset check is moot and only the sha guard applies.
    Used to flag a co-located rubric whose ``seedset`` does not match the set it
    is being served for (DESIGN.md §7 "set mismatch").
    """

    roster = _load_roster_config(replay_dir)
    if roster is None:
        return None
    return f"{roster.num_players}p{roster.num_impostors}i"


# Multi-set serving (Task 12.12; design/phase-12/stage-1-design.md §2.1, §7).
# ``AILIBI_REPLAY_DIR`` is the PARENT of per-set subdirs (``replays/samples/`` ->
# ``4p1i/``, ``9p2i/``, + future). ``get_replay_loader`` takes a ``set`` query
# param resolving ``<parent>/<set>/`` to a per-set loader.
_REPLAY_GLOB: Final[str] = "replay-seed-*.jsonl"

# The default set served when a request carries no ``set`` query param — the flat
# 4p/1i baseline that was the pre-12.12 default-served set, so existing deep-links
# (which omit ``set``) and the dashboard still resolve unchanged.
DEFAULT_SET: Final[str] = "4p1i"

# Bound the per-set loader cache (the integration-risk LRU cap): each set's
# ReplayLoader carries its own per-game caches, so a stray/one-off set cannot
# evict the canonical ones unboundedly. Per-process, not cross-worker — the same
# scale boundary the single loader had (Audit H-H-6, deferred).
_DEFAULT_SET_CACHE_SIZE: Final[int] = 8

# A set name is a single safe path segment: it names a subdir under the parent and
# is taken straight from an untrusted query param, so it must never contain a path
# separator, ``..``, or a leading dot. Anchored so the WHOLE name matches.
_SET_NAME_PATTERN: Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


def _validate_set_name(set_name: str) -> None:
    """Reject a malformed / path-traversal set name (``..``, ``a/b``, ``/abs``)."""

    if _SET_NAME_PATTERN.fullmatch(set_name) is None:
        raise ValueError(f"invalid set name: {set_name!r}")


def _dir_has_replays(path: Path) -> bool:
    """True iff ``path`` holds >=1 regular file whose name PARSES to a seed.

    Matches the loader's own definition of a replay (:func:`_parse_seed_from_filename`,
    the ``replay-seed-<int>.jsonl`` pattern), not just the looser ``_REPLAY_GLOB`` —
    so a non-parseable ``replay-seed-debug.jsonl`` (or a directory with that suffix)
    does NOT make a dir look like a set the loader would then serve empty.
    """

    if not path.is_dir():
        return False
    return any(
        child.is_file() and _parse_seed_from_filename(child.name) is not None
        for child in path.glob(_REPLAY_GLOB)
    )


def _is_set_dir(path: Path) -> bool:
    """True iff ``path`` is an available set: a dir with parseable replays that is
    a LEAF, not a parent-of-sets.

    The single definition of "a set" shared by listing (:meth:`available_sets`)
    AND resolution (:meth:`get`), so an explicit ``?set=<name>`` cannot serve a
    name ``/sets`` omits — a stray / in-progress replay-less (or
    non-parseable-replay) subdir is a 404, not an empty-but-200 list (which would
    mask a typo'd set name). A dir that ALSO contains a replay-bearing subdir is a
    PARENT/container, not a single set: a legacy flat ``replays/samples/`` holding
    stray ``*.jsonl`` next to ``4p1i/`` + ``9p2i/`` must not be served as one set
    named ``samples`` (it would shadow the real nested sets).
    """

    if not _dir_has_replays(path):
        return False
    return not any(
        _dir_has_replays(child) for child in path.iterdir() if child.is_dir()
    )


class SetLoaderRegistry:
    """Per-app registry of per-set :class:`ReplayLoader`\\ s over a parent dir.

    ``AILIBI_REPLAY_DIR`` resolves to the PARENT of per-set subdirs
    (``replays/samples/``); each set (``4p1i``, ``9p2i``, + future) is a subdir
    served by its own :class:`ReplayLoader`. Loaders are built lazily and memoized
    in a bounded per-process LRU keyed by set name, so each set's engine re-walk
    caches independently and a stray set cannot evict the canonical ones
    unboundedly. Mirrors the single-loader scale boundary (Audit H-H-6): the cache
    is per-process, not cross-worker — that remains the deferred scale-phase fix.
    """

    def __init__(
        self, parent_dir: Path, *, cache_size: int = _DEFAULT_SET_CACHE_SIZE
    ) -> None:
        self._parent_dir = parent_dir
        self._cached_loader = lru_cache(maxsize=cache_size)(self._build_loader)

    @property
    def parent_dir(self) -> Path:
        return self._parent_dir

    def available_sets(self) -> list[str]:
        """Sorted set names: parent subdirs holding >=1 ``replay-seed-*.jsonl``.

        Skips stray non-set entries (a top-level README, a loose file, an empty or
        replay-less subdir) so the list AUTO-GROWS: a newly-recorded
        ``replays/samples/<set>/`` appears with no code change (Task 12.12 DoD).
        """

        if not self._parent_dir.is_dir():
            return []
        names: list[str] = []
        for child in self._parent_dir.iterdir():
            if _SET_NAME_PATTERN.fullmatch(child.name) is None:
                continue
            if _is_set_dir(child):
                names.append(child.name)
        return sorted(names)

    def default_set(self) -> str:
        """The set served when a request omits ``set``.

        Prefers :data:`DEFAULT_SET` (the committed 4p1i baseline) when present, so
        existing no-``set`` deep-links resolve to the historical default; otherwise
        the first available set, so the advertised default ALWAYS resolves — the
        ``/sets`` ``default`` and the route fallback share this one resolver, so
        they cannot disagree on a non-4p1i parent. Falls back to :data:`DEFAULT_SET`
        for an empty parent (every set request 404s there anyway).
        """

        sets = self.available_sets()
        if DEFAULT_SET in sets:
            return DEFAULT_SET
        if sets:
            return sets[0]
        return DEFAULT_SET

    def get(self, set_name: str) -> ReplayLoader:
        """Return the per-set loader for ``set_name`` (LRU-cached).

        Raises :class:`ValueError` for a malformed / path-traversal name and
        :class:`FileNotFoundError` for an unknown set — no such subdir, OR a subdir
        that ships no ``replay-seed-*.jsonl`` (a stray / in-progress dir ``/sets``
        also omits); the route maps both to HTTP 404. Requiring replays here keeps
        resolution consistent with listing, so a typo'd set 404s rather than
        serving an empty-but-200 list.
        """

        _validate_set_name(set_name)
        if not _is_set_dir(self._parent_dir / set_name):
            raise FileNotFoundError(set_name)
        return self._cached_loader(set_name)

    def _build_loader(self, set_name: str) -> ReplayLoader:
        return ReplayLoader(replay_dir=self._parent_dir / set_name)


def get_loader_registry(request: Request) -> SetLoaderRegistry:
    """FastAPI dependency: the process-wide per-set registry on ``app.state``.

    Scale boundary (Audit H-H-6, deferred): the registry + its per-set loaders are
    constructed once in :mod:`api.main` and their caches are per-process. A
    cross-worker shared cache is the scale-phase fix and is intentionally NOT built
    here.
    """

    registry = getattr(request.app.state, "loader_registry", None)
    if not isinstance(registry, SetLoaderRegistry):
        raise RuntimeError("SetLoaderRegistry is not configured on app.state")
    return registry


def get_replay_loader(
    request: Request,
    set_: str | None = Query(default=None, alias="set"),
) -> ReplayLoader:
    """FastAPI dependency: the per-set loader for the ``set`` query param.

    Every replay/eval route depends on this, so threading ``set`` here
    set-parametrizes ``/replays``, ``/replays/{game_id}/*``, ``/eval/rubric``, and
    ``/eval/tournament-report`` at once over a per-set cached loader. An omitted (or
    empty) ``set`` resolves to :meth:`SetLoaderRegistry.default_set` — the SAME
    resolver ``GET /sets`` advertises, so the no-``set`` default and the advertised
    default never disagree (e.g. on a parent that ships no 4p1i). An unknown or
    malformed set is a 404.
    """

    registry = get_loader_registry(request)
    resolved = set_ if set_ else registry.default_set()
    try:
        return registry.get(resolved)
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail=f"unknown replay set: {resolved!r}")


__all__ = [
    "DEFAULT_SET",
    "ReplayLoader",
    "ReplayStateMismatchError",
    "ReplaySubstrateMismatchError",
    "RosterConfig",
    "SetLoaderRegistry",
    "get_loader_registry",
    "get_replay_loader",
]
