"""Vote-tally parity: two implementations of one ejection rule (Task 19.26).

audits/audit-phase-19-triage.md §7 item 27 [S-Claude; verified in the original
triage]: the ejection rule the live game applies
(:meth:`meetings.manager.MeetingManager._tally`, written at Task 3.8) and the
one eval / replay analysis re-checks
(:func:`meetings.voting.tally_ballots`, Task 3.10) are two separate bodies of
code whose equivalence is asserted by PROSE ONLY —
``meetings/voting.py``'s module docstring ("the manager retains its own private
copies … future work may consolidate the manager onto this canonical home …
The threshold semantics in :func:`tally_ballots` exactly match the manager's
``_tally`` so the two implementations agree on every input"). A paragraph is
not a gate: nothing fails when one body drifts.

This module is that gate. It runs BOTH implementations over:

1. **Every committed meeting's recorded ballots** — all four committed sets
   (``replays/samples/{9p2i,4p1i}`` and ``replays/ml_corpus/{9p2i,4p1i}``),
   707 meetings / 3,934 ballots, counts pinned below so a thinned checkout
   cannot pass the sweep by walking fewer files. Driven off the RECORDED
   ballot bytes (the hint's instruction) rather than by re-running 300 games
   through the engine, which the determinism gates already cover.
2. **The recorded ballots re-tallied at seven thresholds** — the corpus was
   recorded at one threshold (0.6), so the confidence rule itself is only
   lightly exercised by the bytes; re-tallying the same ballots across
   ``[0.0, 1.0]`` sweeps the cutoff against real vote distributions.
3. **Synthetic edge fixtures** — the shapes the contract names: ties (two-way,
   three-way, SKIP-tied), coerced ballots, dead voters (a target nobody could
   vote for), the SKIP thresholds (strictly under, exactly at, strictly over),
   and every ballot-guard marker family.

Beyond outcome parity the suite pins the four facts that make the two bodies
substitutable at all: the shared ``SKIP`` sentinel and marker literals, the
normaliser pair (:func:`meetings.manager._normalize_ballot_target` vs
:func:`meetings.voting.normalize_ballot_target`), the ONE structural
difference between the tallies (``tally_ballots`` validates its threshold per
call; the manager validates once at construction — see
:func:`test_the_manager_cannot_carry_an_out_of_range_threshold`, which shows
the difference is unreachable rather than blocking), and — via
:func:`test_a_perturbed_tally_disagrees_on_the_committed_corpus` — that the
sweep can actually FAIL. A parity gate that cannot fail is not a gate.

The suite is written to survive the consolidation it authorises: if parity is
total the manager delegates to :func:`meetings.voting.tally_ballots` and the
outcome families below become the delegation's end-to-end proof; if it is not,
they stay as the permanent two-implementation guard the contract asks for.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Final

import pytest

from meetings.constants import DEFAULT_SKIP_CONFIDENCE_THRESHOLD
from meetings.manager import (
    BALLOT_TARGET_REDIRECT_MARKER,
    INVALID_OBSERVATION_ID_MARKER,
    INVALID_REASON_ID_MARKER,
    TEAMMATE_VOTE_TARGET_MARKER,
    UNCITED_ZERO_FLAG_EJECT_MARKER,
    VOTE_PARSE_DEFAULT_MARKER,
    MeetingConfig,
    MeetingManager,
)
from meetings.manager import (
    INVALID_VOTE_TARGET_MARKER as MANAGER_INVALID_VOTE_TARGET_MARKER,
)
from meetings.manager import (
    _normalize_ballot_target as manager_normalize_ballot_target,  # noqa: PLC2701
)
from meetings.manager import (
    _SKIP_TARGET as MANAGER_SKIP_TARGET,  # noqa: PLC2701
)
from meetings.schemas import MeetingOutcome, PlayerId, VoteBallot
from meetings.voting import (
    INVALID_VOTE_TARGET_MARKER,
    SKIP_TARGET,
    normalize_ballot_target,
    tally_ballots,
)

_REPLAYS: Final[Path] = Path(__file__).resolve().parents[2] / "replays"

# Every committed replay set: the samples (the baseline-6 adopting record) AND
# the ML corpus. "All four sets" is the contract's scope, not a sample of it.
_CORPUS_SETS: Final[tuple[str, ...]] = (
    "samples/9p2i",
    "samples/4p1i",
    "ml_corpus/9p2i",
    "ml_corpus/4p1i",
)

# THE COUNT PIN (recorded 2026-08 against the committed baseline-6 corpus). A
# parity sweep is only as good as its coverage, so the file / meeting / ballot
# counts are pinned per set: a thinned checkout, a glob typo, or a silently
# dropped set fails here instead of passing the parity families vacuously.
_EXPECTED_REPLAY_FILES: Final[dict[str, int]] = {
    "samples/9p2i": 50,
    "samples/4p1i": 50,
    "ml_corpus/9p2i": 150,
    "ml_corpus/4p1i": 50,
}
_EXPECTED_MEETINGS: Final[dict[str, int]] = {
    "samples/9p2i": 165,
    "samples/4p1i": 39,
    "ml_corpus/9p2i": 463,
    "ml_corpus/4p1i": 40,
}
_EXPECTED_BALLOTS: Final[dict[str, int]] = {
    "samples/9p2i": 971,
    "samples/4p1i": 117,
    "ml_corpus/9p2i": 2726,
    "ml_corpus/4p1i": 120,
}
_TOTAL_MEETINGS: Final[int] = 707
_TOTAL_BALLOTS: Final[int] = 3934

# The recorded outcome split over those 707 meetings. Pinned so the sweep
# provably exercises BOTH branches of the rule (an all-SKIPPED corpus would
# leave the eject path untested by the committed bytes).
_EXPECTED_RECORDED_OUTCOMES: Final[dict[MeetingOutcome, int]] = {
    "EJECTED": 435,
    "SKIPPED": 272,
}

# The ballot-guard marker families, keyed by the stable label
# ``api.replay_loader`` uses for the same set. Matched by the literal's fixed
# PREFIX (everything before the ``{...}`` interpolation) and by ``in`` rather
# than ``startswith`` because the guards stack: 16.5 nulls a citation, 16.6
# then coerces the now-uncited ballot, so the second marker sits behind the
# first.
_MARKER_TEMPLATES: Final[dict[str, str]] = {
    "invalid_target": MANAGER_INVALID_VOTE_TARGET_MARKER,
    "teammate_coerced": TEAMMATE_VOTE_TARGET_MARKER,
    "under_gate_redirect": BALLOT_TARGET_REDIRECT_MARKER,
    "invalid_reason_id": INVALID_REASON_ID_MARKER,
    "invalid_observation_id": INVALID_OBSERVATION_ID_MARKER,
    "uncited_zero_flag": UNCITED_ZERO_FLAG_EJECT_MARKER,
    "vote_parse_default": VOTE_PARSE_DEFAULT_MARKER,
}

# THE MARKER PIN. Which coercions production has actually exercised, per set —
# the contract's "the interesting edges are the ones production has actually
# exercised". Zeros are written out rather than omitted so the sweep states
# what it does NOT cover: ``vote_parse_default`` never fired on committed
# bytes, so it is carried by a synthetic fixture instead (see
# ``_EDGE_CASES``).
_EXPECTED_MARKERS: Final[dict[str, dict[str, int]]] = {
    "samples/9p2i": {
        "invalid_target": 3,
        "teammate_coerced": 0,
        "under_gate_redirect": 13,
        "invalid_reason_id": 2,
        "invalid_observation_id": 0,
        "uncited_zero_flag": 1,
        "vote_parse_default": 0,
    },
    "samples/4p1i": {
        "invalid_target": 0,
        "teammate_coerced": 0,
        "under_gate_redirect": 0,
        "invalid_reason_id": 0,
        "invalid_observation_id": 0,
        "uncited_zero_flag": 0,
        "vote_parse_default": 0,
    },
    "ml_corpus/9p2i": {
        "invalid_target": 0,
        "teammate_coerced": 4,
        "under_gate_redirect": 48,
        "invalid_reason_id": 1,
        "invalid_observation_id": 2,
        "uncited_zero_flag": 1,
        "vote_parse_default": 0,
    },
    "ml_corpus/4p1i": {
        "invalid_target": 0,
        "teammate_coerced": 0,
        "under_gate_redirect": 1,
        "invalid_reason_id": 0,
        "invalid_observation_id": 0,
        "uncited_zero_flag": 0,
        "vote_parse_default": 0,
    },
}

# The thresholds the recorded ballots are re-tallied at. The corpus was
# recorded at 0.6 only, so the cutoff rule itself needs the sweep: 0.0 ejects
# on any strict plurality, 1.0 ejects only on a maxed-out ballot, and the
# values around 0.6 straddle the inclusive cutoff.
_SWEEP_THRESHOLDS: Final[tuple[float, ...]] = (
    0.0,
    0.25,
    0.5,
    DEFAULT_SKIP_CONFIDENCE_THRESHOLD,
    0.75,
    0.9,
    1.0,
)

# How many of the 707 committed meetings eject at each swept threshold. The
# first four rows are all 435 — the recorded count — which is the corpus fact
# :func:`test_the_threshold_sweep_actually_moves_outcomes` documents: no
# committed meeting was decided by the confidence gate at its recorded cutoff.
_EXPECTED_EJECTIONS_BY_THRESHOLD: Final[dict[float, int]] = {
    0.0: 435,
    0.25: 435,
    0.5: 435,
    DEFAULT_SKIP_CONFIDENCE_THRESHOLD: 435,
    0.75: 424,
    0.9: 331,
    1.0: 65,
}


# ---------------------------------------------------------------------------
# The committed corpus
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _RecordedMeeting:
    """One committed meeting's tally inputs and its recorded resolution."""

    set_name: str
    replay: str
    meeting_id: str
    ballots: tuple[VoteBallot, ...]
    outcome: MeetingOutcome
    ejected_player_id: PlayerId | None

    @property
    def label(self) -> str:
        """Human-readable locator for an assertion message."""

        return f"{self.set_name}/{self.replay}::{self.meeting_id}"

    @property
    def recorded(self) -> tuple[MeetingOutcome, PlayerId | None]:
        """The resolution the recorded bytes carry."""

        return self.outcome, self.ejected_player_id

    @property
    def candidate_targets_by_voter(self) -> dict[PlayerId, tuple[PlayerId, ...]]:
        """Each voter's living eject candidates, reconstructed from the ballots.

        The manager builds ``candidate_targets`` as the living participants
        minus the voter, and every living participant casts a ballot, so the
        voter set of a recorded meeting IS its living roster. This lets the
        normaliser families run over recorded bytes without re-running the
        meeting.
        """

        voters = sorted({ballot.voter for ballot in self.ballots})
        return {
            voter: tuple(other for other in voters if other != voter)
            for voter in voters
        }


@lru_cache(maxsize=None)
def _recorded_meetings(set_name: str) -> tuple[_RecordedMeeting, ...]:
    """Every committed meeting of one set, read from the recorded bytes."""

    meetings: list[_RecordedMeeting] = []
    for path in sorted((_REPLAYS / set_name).glob("replay-seed-*.jsonl")):
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                record = json.loads(line)
                if record.get("kind") != "meeting":
                    continue
                meetings.append(
                    _RecordedMeeting(
                        set_name=set_name,
                        replay=path.name,
                        meeting_id=record["meeting_id"],
                        ballots=tuple(
                            VoteBallot.model_validate(raw) for raw in record["ballots"]
                        ),
                        outcome=record["outcome"],
                        ejected_player_id=record["ejected_player_id"],
                    )
                )
    return tuple(meetings)


def _replay_file_count(set_name: str) -> int:
    return len(list((_REPLAYS / set_name).glob("replay-seed-*.jsonl")))


def _all_recorded_meetings() -> tuple[_RecordedMeeting, ...]:
    return tuple(
        meeting for set_name in _CORPUS_SETS for meeting in _recorded_meetings(set_name)
    )


def _marker_prefix(template: str) -> str:
    """The fixed head of a marker literal, before its ``{...}`` interpolation."""

    head, _, _ = template.partition("{")
    return head


# ---------------------------------------------------------------------------
# The two implementations, side by side
# ---------------------------------------------------------------------------


def _unused_prompt(**_kwargs: Any) -> str:
    """Protocol-satisfying prompt renderer the tally never reaches.

    ``_tally`` is a pure function of the ballots and the configured
    threshold; constructing a manager to call it must not require a prompt
    stack. Raising rather than returning a placeholder keeps that claim
    honest — if a test ever routes a render through here it fails loudly
    instead of silently exercising a different path.
    """

    raise AssertionError("the tally never renders a prompt")


class _UnusedLLMClient:
    """Protocol-satisfying LLM client the tally never reaches (see above)."""

    async def complete(self, **_kwargs: Any) -> Any:
        raise AssertionError("the tally never calls the LLM")


def _manager(
    *, skip_confidence_threshold: float = DEFAULT_SKIP_CONFIDENCE_THRESHOLD
) -> MeetingManager:
    """A real :class:`MeetingManager` carrying only the tally's inputs."""

    return MeetingManager(
        llm_client=_UnusedLLMClient(),
        crewmate_report_prompt=_unused_prompt,
        impostor_report_prompt=_unused_prompt,
        statement_prompt=_unused_prompt,
        vote_prompt=_unused_prompt,
        config=MeetingConfig(skip_confidence_threshold=skip_confidence_threshold),
    )


@lru_cache(maxsize=None)
def _manager_at(threshold: float) -> MeetingManager:
    return _manager(skip_confidence_threshold=threshold)


def _private_tally(
    ballots: Sequence[VoteBallot], *, threshold: float
) -> tuple[MeetingOutcome, PlayerId | None]:
    """The manager's implementation — the one the live game applies."""

    return _manager_at(threshold)._tally(ballots)  # noqa: SLF001


def _canonical_tally(
    ballots: Sequence[VoteBallot], *, threshold: float
) -> tuple[MeetingOutcome, PlayerId | None]:
    """The ``meetings.voting`` implementation — the one eval re-checks."""

    return tally_ballots(ballots, skip_confidence_threshold=threshold)


# ---------------------------------------------------------------------------
# 1. The corpus is what the sweep claims it is
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("set_name", _CORPUS_SETS)
def test_committed_corpus_counts_are_pinned(set_name: str) -> None:
    """Files, meetings, and ballots per set — the sweep's coverage, pinned."""

    meetings = _recorded_meetings(set_name)

    assert _replay_file_count(set_name) == _EXPECTED_REPLAY_FILES[set_name]
    assert len(meetings) == _EXPECTED_MEETINGS[set_name]
    assert sum(len(m.ballots) for m in meetings) == _EXPECTED_BALLOTS[set_name]


def test_committed_corpus_totals_are_pinned() -> None:
    """The whole-corpus totals the module docstring quotes."""

    meetings = _all_recorded_meetings()

    assert len(meetings) == _TOTAL_MEETINGS
    assert sum(len(m.ballots) for m in meetings) == _TOTAL_BALLOTS
    assert sum(_EXPECTED_MEETINGS.values()) == _TOTAL_MEETINGS
    assert sum(_EXPECTED_BALLOTS.values()) == _TOTAL_BALLOTS


def test_recorded_outcome_split_exercises_both_branches() -> None:
    """Both arms of the rule are represented in the recorded bytes.

    A corpus that only ever SKIPPED would leave the eject arm — the arm that
    removes a player from the game — proven by synthetic fixtures alone.
    """

    counts: dict[MeetingOutcome, int] = {"EJECTED": 0, "SKIPPED": 0}
    for meeting in _all_recorded_meetings():
        counts[meeting.outcome] += 1

    assert counts == _EXPECTED_RECORDED_OUTCOMES


@pytest.mark.parametrize("set_name", _CORPUS_SETS)
def test_committed_guard_marker_counts_are_pinned(set_name: str) -> None:
    """Which ballot coercions production actually exercised, per set.

    This is the coverage statement behind the contract's "coerced ballots and
    redirects are greppable via their markers": the parity sweep runs over
    ballots that really were normalised, teammate-coerced, citation-coerced,
    and under-gate redirected, not only over clean ones.
    """

    counts = dict.fromkeys(_MARKER_TEMPLATES, 0)
    for meeting in _recorded_meetings(set_name):
        for ballot in meeting.ballots:
            for label, template in _MARKER_TEMPLATES.items():
                if _marker_prefix(template) in ballot.rationale_text:
                    counts[label] += 1

    assert counts == _EXPECTED_MARKERS[set_name]


# ---------------------------------------------------------------------------
# 2. Parity over every committed meeting
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("set_name", _CORPUS_SETS)
def test_both_implementations_agree_on_every_committed_meeting(
    set_name: str,
) -> None:
    """THE PARITY CLAIM, over recorded bytes: identical outcomes, every meeting."""

    disagreements = [
        (
            meeting.label,
            _private_tally(
                meeting.ballots, threshold=DEFAULT_SKIP_CONFIDENCE_THRESHOLD
            ),
            _canonical_tally(
                meeting.ballots, threshold=DEFAULT_SKIP_CONFIDENCE_THRESHOLD
            ),
        )
        for meeting in _recorded_meetings(set_name)
        if _private_tally(meeting.ballots, threshold=DEFAULT_SKIP_CONFIDENCE_THRESHOLD)
        != _canonical_tally(
            meeting.ballots, threshold=DEFAULT_SKIP_CONFIDENCE_THRESHOLD
        )
    ]

    assert disagreements == []


@pytest.mark.parametrize("set_name", _CORPUS_SETS)
def test_both_implementations_reproduce_the_recorded_outcome(set_name: str) -> None:
    """Both bodies re-derive the resolution the replay actually recorded.

    Agreeing with each other is necessary but not sufficient: two bodies could
    agree on a rule that is not the one the committed games were resolved
    under. Anchoring both to the recorded ``outcome`` /
    ``ejected_player_id`` closes that.
    """

    mismatches = [
        (meeting.label, meeting.recorded, private, canonical)
        for meeting in _recorded_meetings(set_name)
        for private, canonical in [
            (
                _private_tally(
                    meeting.ballots, threshold=DEFAULT_SKIP_CONFIDENCE_THRESHOLD
                ),
                _canonical_tally(
                    meeting.ballots, threshold=DEFAULT_SKIP_CONFIDENCE_THRESHOLD
                ),
            )
        ]
        if not (meeting.recorded == private == canonical)
    ]

    assert mismatches == []


@pytest.mark.parametrize("set_name", _CORPUS_SETS)
@pytest.mark.parametrize("threshold", _SWEEP_THRESHOLDS)
def test_both_implementations_agree_at_every_threshold(
    set_name: str, threshold: float
) -> None:
    """Parity holds across the cutoff, not only at the recorded 0.6.

    The committed bytes were all recorded at ``DEFAULT_SKIP_CONFIDENCE_THRESHOLD``,
    so they exercise exactly one point of the confidence rule. Re-tallying the
    same real vote distributions across ``[0, 1]`` sweeps the rest of it.
    """

    disagreements = [
        meeting.label
        for meeting in _recorded_meetings(set_name)
        if _private_tally(meeting.ballots, threshold=threshold)
        != _canonical_tally(meeting.ballots, threshold=threshold)
    ]

    assert disagreements == []


def test_the_threshold_sweep_actually_moves_outcomes() -> None:
    """The sweep is not vacuous — and it says exactly what the corpus misses.

    Without this, :func:`test_both_implementations_agree_at_every_threshold`
    could be seven identical re-runs of the 0.6 case.

    The pinned numbers below record a real property of the committed bytes: at
    and BELOW the recorded 0.6 threshold every meeting resolves exactly as it
    was recorded, so no committed meeting was ever decided by the confidence
    gate — the "strict plurality but no confident ballot -> SKIPPED" branch is
    not exercised by the corpus at its own threshold. Raising the cutoff turns
    435 recorded ejections into 424 / 331 / 65, which is what makes the sweep
    real coverage of that branch over real ballots rather than a re-run; the
    ``plurality_strictly_under_threshold`` edge fixture covers it directly.
    """

    meetings = _all_recorded_meetings()
    recorded = [m.recorded for m in meetings]
    by_threshold = {
        threshold: [_canonical_tally(m.ballots, threshold=threshold) for m in meetings]
        for threshold in _SWEEP_THRESHOLDS
    }

    assert {
        threshold: sum(outcome == "EJECTED" for outcome, _ in resolutions)
        for threshold, resolutions in by_threshold.items()
    } == _EXPECTED_EJECTIONS_BY_THRESHOLD
    # At or below the recorded cutoff: byte-for-byte the recorded resolutions.
    for threshold in (0.0, 0.25, 0.5, DEFAULT_SKIP_CONFIDENCE_THRESHOLD):
        assert by_threshold[threshold] == recorded, threshold
    # Above it: the gate bites, so the sweep covers ground the corpus does not.
    for threshold in (0.75, 0.9, 1.0):
        assert by_threshold[threshold] != recorded, threshold


# ---------------------------------------------------------------------------
# 3. The synthetic edges
# ---------------------------------------------------------------------------


def _ballot(
    *,
    voter: str,
    target: str,
    confidence: float = 0.8,
    rationale_text: str = "stub-rationale",
) -> VoteBallot:
    return VoteBallot(
        voter=voter,
        target=target,
        confidence=confidence,
        primary_reason_id=None,
        considered_alternatives=(),
        rationale_text=rationale_text,
    )


def _rendered_marker(template: str, value: str) -> str:
    """Render a marker literal, whatever its single placeholder is named.

    The seven families interpolate different field names (``target``,
    ``reason_id``, ``observation_id``, ``head``); rendering them generically
    keeps the fixtures honest — they carry the REAL literal, formatted the way
    the guard formats it, not a hand-typed lookalike.
    """

    field = template.partition("{")[2].partition("!")[0].partition("}")[0]
    return template.format(**{field: value})


def _coerced(
    *, voter: str, marker: str, original: str, confidence: float = 0.95
) -> VoteBallot:
    """A ballot as a coercing guard leaves it: ``SKIP`` behind an audit marker.

    The coercing guards rewrite ``target`` to ``SKIP`` and prefix the marker
    onto ``rationale_text``; the tally sees the rewritten shape, so that is the
    shape the edge fixtures carry.
    """

    return _ballot(
        voter=voter,
        target=SKIP_TARGET,
        confidence=confidence,
        rationale_text=_rendered_marker(marker, original) + "coerced",
    )


def _marked(
    *, voter: str, target: str, marker: str, original: str, confidence: float = 0.9
) -> VoteBallot:
    """A ballot a NON-coercing guard annotated: target kept, marker prefixed.

    The two citation-nulling guards (16.5's observation id, the reason id)
    rewrite a cited id to ``None`` and leave ``target`` alone, so a marked
    ballot still competes in the tally. Parity must hold on that shape too.
    """

    return _ballot(
        voter=voter,
        target=target,
        confidence=confidence,
        rationale_text=_rendered_marker(marker, original) + "marked",
    )


# (name, ballots, threshold). The shapes the contract names: ties, coerced
# ballots, dead voters, the SKIP thresholds, and the guard markers.
_EDGE_CASES: Final[tuple[tuple[str, tuple[VoteBallot, ...], float], ...]] = (
    ("empty", (), 0.6),
    ("single_confident_vote", (_ballot(voter="p-1", target="p-2"),), 0.6),
    ("single_skip", (_ballot(voter="p-1", target=SKIP_TARGET),), 0.6),
    (
        "all_skip",
        tuple(_ballot(voter=f"p-{i}", target=SKIP_TARGET) for i in (1, 2, 3)),
        0.6,
    ),
    (
        "two_way_tie",
        (
            _ballot(voter="p-1", target="p-3"),
            _ballot(voter="p-2", target="p-4"),
        ),
        0.6,
    ),
    (
        "three_way_tie",
        (
            _ballot(voter="p-1", target="p-4"),
            _ballot(voter="p-2", target="p-5"),
            _ballot(voter="p-3", target="p-6"),
        ),
        0.6,
    ),
    (
        "skip_tied_with_a_player",
        (
            _ballot(voter="p-1", target="p-3"),
            _ballot(voter="p-2", target=SKIP_TARGET),
        ),
        0.6,
    ),
    (
        "skip_plurality_over_two_split_targets",
        (
            _ballot(voter="p-1", target=SKIP_TARGET),
            _ballot(voter="p-2", target=SKIP_TARGET),
            _ballot(voter="p-3", target="p-4"),
            _ballot(voter="p-4", target="p-5"),
        ),
        0.6,
    ),
    (
        "plurality_strictly_under_threshold",
        (
            _ballot(voter="p-1", target="p-3", confidence=0.59),
            _ballot(voter="p-2", target="p-3", confidence=0.5),
        ),
        0.6,
    ),
    (
        "plurality_exactly_at_threshold",
        (
            _ballot(voter="p-1", target="p-3", confidence=0.6),
            _ballot(voter="p-2", target="p-3", confidence=0.1),
        ),
        0.6,
    ),
    (
        "plurality_one_ulp_over_threshold",
        (_ballot(voter="p-1", target="p-3", confidence=0.6000000000000001),),
        0.6,
    ),
    (
        "max_confidence_across_the_targets_ballots_decides",
        (
            _ballot(voter="p-1", target="p-3", confidence=0.05),
            _ballot(voter="p-2", target="p-3", confidence=0.95),
        ),
        0.6,
    ),
    (
        "threshold_floor_zero",
        (_ballot(voter="p-1", target="p-2", confidence=0.0),),
        0.0,
    ),
    (
        "threshold_ceiling_one_met",
        (_ballot(voter="p-1", target="p-2", confidence=1.0),),
        1.0,
    ),
    (
        "threshold_ceiling_one_missed",
        (_ballot(voter="p-1", target="p-2", confidence=0.999999),),
        1.0,
    ),
    (
        # A "dead voter": a target nobody living could legally have been given
        # as a candidate. The tally is target-agnostic by design — the
        # normaliser is what keeps such an id out — so parity must hold on the
        # un-normalised shape too, which is exactly the corruption case
        # ``normalize_ballot_target`` exists to prevent.
        "dead_or_unknown_target_survives_to_the_tally",
        (
            _ballot(voter="p-1", target="p-9", confidence=0.9),
            _ballot(voter="p-2", target=SKIP_TARGET),
        ),
        0.6,
    ),
    (
        "self_vote_survives_to_the_tally",
        (
            _ballot(voter="p-1", target="p-1", confidence=0.9),
            _ballot(voter="p-2", target=SKIP_TARGET),
        ),
        0.6,
    ),
    (
        "invalid_target_marker",
        (
            _coerced(
                voter="p-1",
                marker=MANAGER_INVALID_VOTE_TARGET_MARKER,
                original="imp-2",
            ),
            _ballot(voter="p-2", target="p-3", confidence=0.9),
        ),
        0.6,
    ),
    (
        "teammate_coerced_marker",
        (
            _coerced(voter="p-1", marker=TEAMMATE_VOTE_TARGET_MARKER, original="p-5"),
            _ballot(voter="p-2", target="p-3", confidence=0.9),
        ),
        0.6,
    ),
    (
        "under_gate_redirect_marker",
        (
            _coerced(voter="p-1", marker=BALLOT_TARGET_REDIRECT_MARKER, original="p-4"),
            _ballot(voter="p-2", target=SKIP_TARGET),
        ),
        0.6,
    ),
    (
        "uncited_zero_flag_marker",
        (
            _coerced(
                voter="p-1", marker=UNCITED_ZERO_FLAG_EJECT_MARKER, original="p-6"
            ),
            _ballot(voter="p-2", target="p-6", confidence=0.9),
        ),
        0.6,
    ),
    (
        # The one guard family the committed corpus never exercised (see
        # ``_EXPECTED_MARKERS``): a ballot whose completion never parsed.
        "vote_parse_default_marker",
        (
            _coerced(voter="p-1", marker=VOTE_PARSE_DEFAULT_MARKER, original='{"tar'),
            _ballot(voter="p-2", target=SKIP_TARGET),
        ),
        0.6,
    ),
    (
        "invalid_reason_id_marker_keeps_its_target",
        (
            _marked(
                voter="p-1",
                target="p-3",
                marker=INVALID_REASON_ID_MARKER,
                original="m-9:turn-4",
            ),
            _ballot(voter="p-2", target=SKIP_TARGET),
        ),
        0.6,
    ),
    (
        "invalid_observation_id_marker_keeps_its_target",
        (
            _marked(
                voter="p-1",
                target="p-3",
                marker=INVALID_OBSERVATION_ID_MARKER,
                original="p-1:410:2",
            ),
            _ballot(voter="p-2", target="p-3", confidence=0.2),
        ),
        0.6,
    ),
    (
        "every_ballot_coerced_to_skip",
        tuple(
            _coerced(voter=f"p-{i}", marker=TEAMMATE_VOTE_TARGET_MARKER, original="p-9")
            for i in (1, 2, 3)
        ),
        0.6,
    ),
    (
        "coerced_skips_outvote_a_confident_ejector",
        (
            _coerced(voter="p-1", marker=BALLOT_TARGET_REDIRECT_MARKER, original="p-4"),
            _coerced(
                voter="p-2", marker=UNCITED_ZERO_FLAG_EJECT_MARKER, original="p-4"
            ),
            _ballot(voter="p-3", target="p-4", confidence=1.0),
        ),
        0.6,
    ),
    (
        "unanimous_eject",
        tuple(_ballot(voter=f"p-{i}", target="p-9", confidence=0.9) for i in (1, 2, 3)),
        0.6,
    ),
)


@pytest.mark.parametrize(
    ("name", "ballots", "threshold"),
    _EDGE_CASES,
    ids=[case[0] for case in _EDGE_CASES],
)
def test_both_implementations_agree_on_the_synthetic_edges(
    name: str, ballots: tuple[VoteBallot, ...], threshold: float
) -> None:
    """THE PARITY CLAIM, over constructed edges the corpus under-covers."""

    assert _private_tally(ballots, threshold=threshold) == _canonical_tally(
        ballots, threshold=threshold
    ), name


def test_the_synthetic_edges_cover_both_outcomes_and_every_marker() -> None:
    """The edge fixtures are not all one shape.

    Guards against a fixture table that quietly drifts into all-SKIPPED (or
    loses a marker family) and keeps passing while covering less.
    """

    outcomes = {
        _canonical_tally(ballots, threshold=threshold)[0]
        for _, ballots, threshold in _EDGE_CASES
    }
    rationales = " ".join(
        ballot.rationale_text for _, ballots, _ in _EDGE_CASES for ballot in ballots
    )

    assert outcomes == {"EJECTED", "SKIPPED"}
    for label, template in _MARKER_TEMPLATES.items():
        assert _marker_prefix(template) in rationales, label


# ---------------------------------------------------------------------------
# 4. The normaliser pair and the shared literals
# ---------------------------------------------------------------------------


def _normalizer_inputs() -> Iterable[tuple[str, VoteBallot, tuple[PlayerId, ...]]]:
    """Synthetic normaliser cases: valid, SKIP, hallucinated, self, dead."""

    candidates: tuple[PlayerId, ...] = ("p-2", "p-3")
    yield "valid_candidate", _ballot(voter="p-1", target="p-2"), candidates
    yield "skip_sentinel", _ballot(voter="p-1", target=SKIP_TARGET), candidates
    yield "hallucinated_id", _ballot(voter="p-1", target="imp-2"), candidates
    yield "self_vote", _ballot(voter="p-1", target="p-1"), candidates
    yield "ejected_player", _ballot(voter="p-1", target="p-4"), candidates
    yield "empty_candidate_set", _ballot(voter="p-1", target="p-2"), ()
    yield (
        "lookalike_skip",
        _ballot(voter="p-1", target="skip"),
        candidates,
    )


@pytest.mark.parametrize(
    ("name", "ballot", "candidates"),
    list(_normalizer_inputs()),
    ids=[case[0] for case in _normalizer_inputs()],
)
def test_both_normalizers_agree_on_the_synthetic_targets(
    name: str, ballot: VoteBallot, candidates: tuple[PlayerId, ...]
) -> None:
    """The normaliser pair rides beside the tally pair and gets the same guard.

    ``meetings/voting.py``'s note covers BOTH private copies, and a normaliser
    drift corrupts the tally's input rather than its rule — a silent failure
    the outcome families above would not catch.
    """

    assert manager_normalize_ballot_target(
        ballot=ballot, candidate_targets=candidates
    ) == normalize_ballot_target(ballot, candidate_targets=candidates), name


@pytest.mark.parametrize("set_name", _CORPUS_SETS)
def test_both_normalizers_agree_on_every_committed_ballot(set_name: str) -> None:
    """Normaliser parity over the recorded bytes, at each voter's real candidate set."""

    disagreements = [
        (meeting.label, ballot.voter)
        for meeting in _recorded_meetings(set_name)
        for ballot in meeting.ballots
        if manager_normalize_ballot_target(
            ballot=ballot,
            candidate_targets=meeting.candidate_targets_by_voter[ballot.voter],
        )
        != normalize_ballot_target(
            ballot,
            candidate_targets=meeting.candidate_targets_by_voter[ballot.voter],
        )
    ]

    assert disagreements == []


def test_the_shared_literals_match_byte_for_byte() -> None:
    """The sentinel and the audit marker the two homes each define separately.

    ``meetings/voting.py`` documents both as matching the manager's
    "byte for byte"; the tally families above are meaningless if they do not.
    """

    assert MANAGER_SKIP_TARGET == SKIP_TARGET == "SKIP"
    assert MANAGER_INVALID_VOTE_TARGET_MARKER == INVALID_VOTE_TARGET_MARKER


# ---------------------------------------------------------------------------
# 5. The one structural difference — and why it is not a blocking one
# ---------------------------------------------------------------------------


def test_the_canonical_tally_rejects_an_out_of_range_threshold() -> None:
    """``tally_ballots`` validates its threshold per call (AGENTS.md fail-loud)."""

    with pytest.raises(ValueError, match=r"skip_confidence_threshold"):
        tally_ballots((), skip_confidence_threshold=1.5)


def test_the_manager_cannot_carry_an_out_of_range_threshold() -> None:
    """The manager validates ONCE, at construction — the difference is unreachable.

    This is the only structural difference between the two bodies:
    :func:`meetings.voting.tally_ballots` re-checks ``skip_confidence_threshold
    in [0, 1]`` on every call, while ``_tally`` reads a
    :class:`MeetingConfig` whose threshold ``MeetingManager.__init__`` already
    validated (and which is frozen thereafter). Because no manager can exist
    with an out-of-range threshold, no ``_tally`` call can ever observe one, so
    the difference cannot change an outcome — which is what makes the
    consolidation mechanical rather than behavioural.
    """

    with pytest.raises(ValueError, match=r"MeetingConfig.skip_confidence_threshold"):
        _manager(skip_confidence_threshold=1.5)
    with pytest.raises(ValueError, match=r"MeetingConfig.skip_confidence_threshold"):
        _manager(skip_confidence_threshold=-0.1)


# ---------------------------------------------------------------------------
# 6. The gate can fail
# ---------------------------------------------------------------------------


def _tally_dropping_skip(
    ballots: Sequence[VoteBallot], *, threshold: float
) -> tuple[MeetingOutcome, PlayerId | None]:
    """A plausible WRONG tally: ``SKIP`` treated as an abstention, not a target.

    This is the exact drift ``meetings/voting.py``'s docstring argues against
    ("if SKIP were dropped from the tally, a single non-skip vote among many
    skips would still eject"). If the sweep cannot catch it, the sweep proves
    nothing.
    """

    tallies: dict[str, int] = {}
    for ballot in ballots:
        if ballot.target == SKIP_TARGET:
            continue
        tallies[ballot.target] = tallies.get(ballot.target, 0) + 1
    if not tallies:
        return "SKIPPED", None
    max_votes = max(tallies.values())
    leaders = sorted(t for t, count in tallies.items() if count == max_votes)
    if len(leaders) > 1:
        return "SKIPPED", None
    leader = leaders[0]
    if max(b.confidence for b in ballots if b.target == leader) < threshold:
        return "SKIPPED", None
    return "EJECTED", leader


def test_a_perturbed_tally_disagrees_on_the_committed_corpus() -> None:
    """The corpus sweep detects a real rule change — it is a gate, not a ritual."""

    disagreements = [
        meeting.label
        for meeting in _all_recorded_meetings()
        if _tally_dropping_skip(
            meeting.ballots, threshold=DEFAULT_SKIP_CONFIDENCE_THRESHOLD
        )
        != meeting.recorded
    ]

    assert disagreements != []


def test_a_perturbed_tally_disagrees_on_the_synthetic_edges() -> None:
    """And so do the edge fixtures, independently of the corpus."""

    disagreements = [
        name
        for name, ballots, threshold in _EDGE_CASES
        if _tally_dropping_skip(ballots, threshold=threshold)
        != _canonical_tally(ballots, threshold=threshold)
    ]

    assert disagreements != []
