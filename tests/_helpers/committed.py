"""The one home for walks over the committed replay sets, each computed once.

The five instruments below — the assembled eval report, the information funnel,
the kill-craft, deception and solvability folds — are the suite's most expensive
fixtures: each re-seeds every game in a set, replays every recorded action
through the engine and verifies every state hash. Each is also a pure
deterministic function of frozen committed bytes, so computing one twice is
repeated work and nothing else. Every test-side walk over a committed set goes
through this module.

One instance is shared by every reader on a worker, and two mechanisms — not a
promise — keep that from coupling them: the reports are ``frozen=True``, so no
field can be rebound, and every collection they expose is annotated
``Mapping``/``Sequence``, which has no ``__setitem__``, so ``uv run mypy .``
rejects an in-place mutation where it is written.
``tests/_helpers/test_committed_single_home.py`` walks the five report graphs
and fails if either property is ever dropped.

``functools.cache`` rather than a session fixture: the sharing has to reach
plain helper functions and class bodies that cannot request a fixture, and under
``pytest-xdist`` a session fixture is session-scoped *per worker* anyway — so a
process-level cache is the same lifetime with a wider reach.

Four call sites deliberately walk a set WITHOUT this cache — because a second
independent computation is what they assert, or because the walker itself is the
subject under test. ``tests/_helpers/test_committed_single_home.py`` holds that
allow-list with the reason for each, and pins every other call site here.
"""

from __future__ import annotations

import sys
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from eval.deception_instruments import DeceptionInstrumentsReport
    from eval.funnel import InformationFunnelReport
    from eval.kill_craft import KillCraftReport
    from eval.meeting_quality import TournamentEvalReport
    from eval.solvability import SolvabilityReport
    from meetings.schemas import PlayerId, SightingRecord
    from orchestrator.replay import MeetingReplayEntry

#: The checkout root, derived from this file rather than the process working
#: directory: a test that builds a fixture path from the cwd only passes when
#: pytest happens to be invoked from the repo root.
repo_root: Final[Path] = Path(__file__).resolve().parents[2]

#: The four committed replay sets the pins walk, named once so new callers do not
#: have to spell the layout again. Cache entries are keyed by path VALUE, so a
#: module that builds the same absolute path shares the entry either way.
SAMPLES_9P2I: Final[Path] = repo_root / "replays" / "samples" / "9p2i"
SAMPLES_4P1I: Final[Path] = repo_root / "replays" / "samples" / "4p1i"
CORPUS_9P2I: Final[Path] = repo_root / "replays" / "ml_corpus" / "9p2i"
CORPUS_4P1I: Final[Path] = repo_root / "replays" / "ml_corpus" / "4p1i"


@cache
def report_9p2i() -> TournamentEvalReport:
    """The committed 9p2i set's eval report, assembled once.

    ``build_report`` re-derives roles from the seeds, folds the 50 recorded
    replays through the one operator assembly (``scripts/build_sample_report.py``)
    and runs the state-hash-verified kill-craft walk over the whole directory.

    Imports lazily: ``build_sample_report`` pulls in the api/engine/eval stack,
    which does not belong in the import time of tests that never read a report.
    """

    scripts_dir = repo_root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from build_sample_report import build_report

    return build_report(SAMPLES_9P2I)


@cache
def funnel_report(sample_dir: Path) -> InformationFunnelReport:
    """``sample_dir``'s three-stage information funnel, folded once."""

    from eval.funnel import compute_information_funnel

    return compute_information_funnel(sample_dir)


def funnel_9p2i() -> InformationFunnelReport:
    """The committed 9p2i set's information funnel — the cross-package reader."""

    return funnel_report(SAMPLES_9P2I)


@cache
def kill_craft_report(sample_dir: Path) -> KillCraftReport:
    """``sample_dir``'s kill-craft report, walked once."""

    from eval.kill_craft import compute_kill_craft_report

    return compute_kill_craft_report(sample_dir)


@cache
def deception_instruments_report(sample_dir: Path) -> DeceptionInstrumentsReport:
    """``sample_dir``'s Tier-A deception instruments, folded once."""

    from eval.deception_instruments import compute_deception_instruments

    return compute_deception_instruments(sample_dir)


@cache
def solvability_report(sample_dir: Path) -> SolvabilityReport:
    """``sample_dir``'s solvability ceiling, walked once."""

    from eval.solvability import compute_solvability_report

    return compute_solvability_report(sample_dir)


def sighting_records_from_recorded_flags(
    entry: MeetingReplayEntry,
) -> dict[PlayerId, tuple[SightingRecord, ...]]:
    """Rebuild one meeting's groundable sighting channel from its RECORDED flags.

    The graduated ``grounded_prosecution`` lever (audits/audit-phase-20-baseline-7.md
    §6.1) reads each speaker's typed sighting channel, which the replay does not
    persist -- so a test that re-runs the detector or the belief fold over
    committed bytes WITHOUT it is not re-running production, and measures the
    missing channel instead. The channel is recoverable by inversion: a recorded
    flag carrying :data:`WEAK_REASON_UNGROUNDED_SIGHTING` says the speaker's own
    record did NOT back that sighting, so no record is minted for it; every other
    spoken sighting was grounded at record time and re-grounds by construction.

    The sibling channels do not invert the same way, and callers must not assume
    they do: ``vent_witness_records`` embeds a tick the replay drops, and the
    movement channel is not recoverable at all (a spoken transition is prosecuted
    at its destination, decided against private perception). Record audit §10.3
    holds what that costs.
    """

    from meetings.schemas import SawPlayerObservation, SightingRecord
    from meetings.transcript import WEAK_REASON_UNGROUNDED_SIGHTING

    ungrounded = {
        event_id
        for flag in entry.contradictions
        if WEAK_REASON_UNGROUNDED_SIGHTING in flag.description
        for event_id in (flag.event_a_id, flag.event_b_id)
    }
    records: dict[PlayerId, list[SightingRecord]] = {}
    for turn in entry.transcript.turns:
        for index, observation in enumerate(turn.observations):
            if not isinstance(observation, SawPlayerObservation):
                continue
            if f"turn:{turn.turn_id}:obs:{index}" in ungrounded:
                continue
            records.setdefault(turn.speaker, []).append(
                SightingRecord(
                    subject=observation.subject,
                    room=observation.room,
                    tick=observation.tick,
                )
            )
    return {speaker: tuple(rows) for speaker, rows in records.items()}
