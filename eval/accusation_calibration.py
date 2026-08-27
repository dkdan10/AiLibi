"""Accusation-calibration metric (DESIGN.md §11.3).

A pure analyzer over :class:`eval.report_schema.TournamentReport` answering
DESIGN.md §11.3's calibration question: *are high-confidence accusations
correct more often than low-confidence ones?* A well-calibrated agent
population shows the actual-impostor rate of accusation targets rising
monotonically with stated confidence.

Accusations carry an explicit ``confidence`` in two structurally distinct
places, both reachable from the report without re-scraping raw replay JSONL:

* :class:`meetings.schemas.AccusationClaim` (``type="accusation"``,
  ``against``, ``confidence``) nested in ``MeetingTurn.claims`` across the
  turns of each ``MeetingReport.transcript``.
* :class:`meetings.schemas.VoteBallot` (``voter``, ``target``, ``confidence``)
  on each ``MeetingReport.ballots``; ``target`` may be the literal ``"SKIP"``
  (a non-accusation).

A mid-meeting accusation and a final vote are different acts, so this module
reports the two calibration curves **separately** rather than pooling them
into one (see the PR's ``## Decisions`` block): ``accusation_claim_bins`` and
``vote_ballot_bins``.

Correctness of a single accusation is decided strictly by the post-game role
ground truth of the game it came from: ``roles[target] == "IMPOSTOR"``
(:data:`engine.entities.Role`). ``roles`` is the eval-only ground-truth map the
Task 5.6 loader fills; it is never an inferred role and never exposed to
agents. ``roles`` covers every player by construction, so a ``target`` absent
from it signals a malformed report and fails loud (raises) rather than silently
counting as a non-hit, which would bias that bin's rate downward (AGENTS.md "no
silent fallbacks"). A ``"SKIP"`` ballot accuses no one and is excluded *before*
the lookup.

Binning is fixed-width over ``[0, 1]`` with ``n_bins`` bins (default 10 ->
deciles; see the PR's ``## Decisions`` block). Because ``confidence`` is
``Field(ge=0.0, le=1.0)``, ``1.0`` is legal, so bins are half-open ``[lo, hi)``
except the final bin, which is closed ``[lo, 1.0]``. The index of a confidence
``c`` is ``min(int(c * n_bins), n_bins - 1)``: deterministic, total, and
putting ``c == 1.0`` in the top bin.

A bin with zero accusations reports ``count == 0`` and a ``None`` (not ``0.0``,
not NaN) ``actual_impostor_rate`` / ``mean_confidence`` so an empty bin is never
confused with a populated bin whose accusations all missed (a genuine ``0.0``
rate). A game with no accusations, no meetings, or all-``SKIP`` ballots yields
all-empty bins and a ``None`` calibration error without raising.

**The accuser-role split, and the ceiling it exposes.** ``accusation_claim_*``
pools every accuser, and on both roster shapes an IMPOSTOR accuser sits under a
structural ceiling that no amount of calibration can lift, so the pooled curve
reads a fact about the machinery as agent overconfidence.

* On a 2-impostor roster the only target that scores as a hit is the accuser's
  teammate, and the teammate firewall deletes exactly that accusation at the
  per-turn chokepoint (``meetings.manager._guard_teammate_turn_claims`` and
  ``exclude_teammate_vent_observations``). So every impostor accusation that
  survives to the record names a crewmate and misses by construction.
* On a 1-impostor roster the roster itself is the ceiling: the sole impostor's
  only scoring-correct target is themselves, and a self-accusation is not a
  lawful accusation. The firewall never runs on this shape.

``accusation_claim_crew_accuser`` and ``accusation_claim_impostor_accuser``
therefore ship beside the pooled curve as a PARTITION of it (their totals sum to
``accusation_claim_total``), so a reader can price the artifact instead of
absorbing it. On the committed sets the impostor curves hit zero on all four,
and the crew-only curve still falls with confidence by itself — the mid-range
inversion is roughly a fifth attributable to the impostor block, and the pooled
accusation base rate is about 0.50 on the 9p2i corpus, not a low chance prior.

**Guard-authored ballots are excluded.** A ballot whose recorded rationale opens
with one of the six audit markers the meeting layer prepends carries a target
the voter did not author beside a confidence in the target they did, so no
calibration curve bins it; ``vote_ballot_guard_authored_excluded`` publishes how
many were dropped rather than leaving the exclusion invisible.

**Per-bin counts and the low-power flag (audit F-F-3 / gp-7).** Each curve's
per-bin ``count`` is already on its :class:`CalibrationBin` entries, so the
distribution behind a single ECE scalar is always inspectable. On top of that
each curve carries ``*_populated_bins`` (how many bins actually held a sample)
and ``*_low_power`` -- ``True`` when fewer than
:data:`MIN_POPULATED_BINS_FOR_POWER` bins are populated. A provider whose
confidences cluster into a couple of values (the audited ``qwen2.5`` emitted a
near-constant ``0.55`` / ``0.85`` enum, so ECE was computed from 3-4 populated
bins with no low/high anchors) produces a *technically valid but
statistically weak* ECE; the flag warns a reader not to gate on an ECE delta
from a near-degenerate distribution. It flags interpretation only and changes
no computed number.
"""

from __future__ import annotations

import re
from collections.abc import Iterator, Mapping
from typing import Final

from pydantic import BaseModel, ConfigDict, model_validator

from engine.entities import Role
from eval.report_schema import TournamentReport
from meetings.manager import (
    BALLOT_TARGET_REDIRECT_MARKER,
    INVALID_OBSERVATION_ID_MARKER,
    INVALID_REASON_ID_MARKER,
    INVALID_VOTE_TARGET_MARKER,
    TEAMMATE_VOTE_TARGET_MARKER,
    UNCITED_ZERO_FLAG_EJECT_MARKER,
)
from meetings.schemas import AccusationClaim, MeetingTranscript, PlayerId

# Default number of fixed-width confidence bins over [0, 1]: deciles. An
# explicit, documented choice (DESIGN.md §11.3; see the PR's ## Decisions
# block). Overridable per call via the keyword-only ``n_bins`` argument.
DEFAULT_N_BINS: int = 10

# Minimum number of populated (non-empty) bins a calibration curve needs before
# its ECE is treated as adequately powered. Below this, ``*_low_power`` is set.
# An explicit, documented threshold (see the PR's ## Decisions block): with
# deciles, a provider that clusters confidences into a couple of values
# populates only 2-4 bins, leaving ECE anchored to no low/high tail (audit
# F-F-3). Chosen so such a near-degenerate curve is flagged while a curve
# spread across half the range or more is not. It changes no computed metric.
MIN_POPULATED_BINS_FOR_POWER: int = 5

# Every marker interpolates its payload as a Python ``repr`` — always quoted,
# with backslash escapes — so matching the payload as a quoted literal (rather
# than scanning for the static tail) stops a payload that itself contains the
# marker's tail from truncating the match.
_MARKER_REPR_VALUE: Final[str] = r"(?:'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")"


def _marker_head_pattern(marker: str) -> re.Pattern[str]:
    """An anchored pattern matching one whole audit marker at a string's head.

    Built from the marker CONSTANT and generalized over the placeholder name, so
    a rename or a wording change moves the predicate with it — the alternative,
    a literal copy, is how a guard-authored ballot silently re-enters a metric.
    """

    head, brace, rest = marker.partition("{")
    if not brace:
        raise ValueError(f"marker constant carries no repr placeholder: {marker!r}")
    _, _, tail = rest.partition("}")
    return re.compile("^" + re.escape(head) + _MARKER_REPR_VALUE + re.escape(tail))


# The six audit markers the meeting layer PREPENDS to a recorded
# ``rationale_text``. A ballot whose rationale opens with one is machinery
# testimony about its own rewrite, not the voter's own act, so no calibration
# curve may bin it (audit A-3). Matched by PREDICATE over the marker constants,
# never by literal text; Task 21.3's structured ``guard_redirected_from`` field
# supersedes this once it lands, and Task 21.8 consolidates the entry point.
_GUARD_MARKER_PATTERNS: Final[tuple[re.Pattern[str], ...]] = tuple(
    _marker_head_pattern(marker)
    for marker in (
        INVALID_VOTE_TARGET_MARKER,
        TEAMMATE_VOTE_TARGET_MARKER,
        BALLOT_TARGET_REDIRECT_MARKER,
        INVALID_REASON_ID_MARKER,
        INVALID_OBSERVATION_ID_MARKER,
        UNCITED_ZERO_FLAG_EJECT_MARKER,
    )
)


def _is_guard_authored(rationale: str) -> bool:
    """Whether a recorded rationale opens with a guard audit marker."""

    return any(pattern.match(rationale) for pattern in _GUARD_MARKER_PATTERNS)


class _FrozenModel(BaseModel):
    """Frozen, ``extra="forbid"`` base shared by the result models.

    Mirrors :mod:`eval.report_schema` and :mod:`meetings.schemas`: result
    artifacts are immutable value objects and an unexpected field is a bug, not
    something to silently absorb (AGENTS.md "no silent fallbacks").
    """

    model_config = ConfigDict(frozen=True, extra="forbid")


class CalibrationBin(_FrozenModel):
    """One fixed-width confidence bin's calibration tally (DESIGN.md §11.3).

    ``lo``/``hi`` are the nominal bin edges; the bin is half-open ``[lo, hi)``
    except the final bin, which is closed ``[lo, 1.0]`` so ``confidence == 1.0``
    lands here. ``midpoint`` is ``(lo + hi) / 2`` -- the confidence the bin
    represents for the "rate vs midpoint" calibration reading.

    ``count`` is how many accusations fell in the bin and ``impostor_hits`` how
    many of those targeted an actual impostor. ``actual_impostor_rate`` is
    ``impostor_hits / count`` and ``mean_confidence`` the empirical mean of the
    binned confidences; both are ``None`` (never ``0.0`` or NaN) for an empty
    bin, so a bin with no data is never mistaken for a populated bin whose
    accusations all missed.
    """

    bin_index: int
    lo: float
    hi: float
    midpoint: float
    count: int
    impostor_hits: int
    actual_impostor_rate: float | None
    mean_confidence: float | None


class CalibrationCurve(_FrozenModel):
    """One calibration curve packaged as a value: bins, total, ECE, power.

    The same five quantities the pooled ``accusation_claim_*`` /
    ``vote_ballot_*`` field groups carry, gathered into one object so a
    conditioned curve can be added without adding five parallel fields per
    condition. The pooled groups keep their flat shape: refactoring them into
    this model would change the served wire shape for no gain.
    """

    bins: tuple[CalibrationBin, ...]
    total: int
    ece: float | None
    populated_bins: int
    low_power: bool


class AccusationCalibrationReport(_FrozenModel):
    """Per-source accusation-calibration curves for a tournament (§11.3).

    ``accusation_claim_*`` covers :class:`~meetings.schemas.AccusationClaim`
    confidences (mid-meeting accusations) and ``vote_ballot_*`` covers
    :class:`~meetings.schemas.VoteBallot` confidences (final votes, ``"SKIP"``
    excluded). The two are reported separately, never pooled, because a vote and
    a mid-meeting accusation are different acts (see the PR's ## Decisions
    block).

    Each ``*_bins`` tuple has exactly ``n_bins`` entries in ascending
    ``bin_index`` order. Each ``*_total`` is the number of accusations the curve
    binned (the sum of its bins' ``count``). Each ``*_ece`` is the expected
    calibration error: the count-weighted mean over populated bins of
    ``abs(actual_impostor_rate - mean_confidence)`` -- a scalar miscalibration
    summary in ``[0, 1]`` where ``0`` is perfect calibration. ECE uses each
    bin's empirical ``mean_confidence`` (the standard formulation); the simpler
    "rate vs ``midpoint``" reading the DoD names is available per bin too. It is
    ``None`` when the curve binned no accusations (an undefined error over zero
    samples is reported as "no data", never a misleading ``0.0``).

    Each curve also carries ``*_populated_bins`` (how many of its ``n_bins``
    bins held >= 1 sample) and ``*_low_power`` (``True`` when that count is
    below :data:`MIN_POPULATED_BINS_FOR_POWER`). These surface, next to the ECE
    scalar, whether the ECE rests on a well-spread distribution or a couple of
    clustered confidence values whose ECE delta is unreliable (audit F-F-3).
    They are interpretation flags; the ECE value itself is unchanged.

    ``accusation_claim_crew_accuser`` / ``accusation_claim_impostor_accuser``
    are the same claim curve conditioned on the ACCUSER's true role — a
    partition of the pooled one, validated to sum to
    ``accusation_claim_total`` — because an impostor accuser's hit rate is
    ceilinged by the roster and the teammate firewall rather than by
    calibration (see the module docstring).
    ``vote_ballot_guard_authored_excluded`` counts the ballots left out of the
    vote curve because the meeting layer, not the voter, authored their target.
    """

    n_bins: int
    accusation_claim_bins: tuple[CalibrationBin, ...]
    accusation_claim_total: int
    accusation_claim_ece: float | None
    accusation_claim_populated_bins: int
    accusation_claim_low_power: bool
    accusation_claim_crew_accuser: CalibrationCurve
    accusation_claim_impostor_accuser: CalibrationCurve
    vote_ballot_bins: tuple[CalibrationBin, ...]
    vote_ballot_total: int
    vote_ballot_ece: float | None
    vote_ballot_populated_bins: int
    vote_ballot_low_power: bool
    vote_ballot_guard_authored_excluded: int

    @model_validator(mode="after")
    def _validate_bins(self) -> AccusationCalibrationReport:
        if self.n_bins < 1:
            raise ValueError(f"n_bins must be >= 1, got {self.n_bins}")
        crew = self.accusation_claim_crew_accuser
        impostor = self.accusation_claim_impostor_accuser
        if crew.total + impostor.total != self.accusation_claim_total:
            raise ValueError(
                "the accuser-role split must PARTITION the pooled claim curve: "
                f"{crew.total} + {impostor.total} != "
                f"{self.accusation_claim_total}"
            )
        if self.vote_ballot_guard_authored_excluded < 0:
            raise ValueError(
                "vote_ballot_guard_authored_excluded must be >= 0, got "
                f"{self.vote_ballot_guard_authored_excluded}"
            )
        for label, bins, declared in (
            (
                "accusation_claim_bins",
                self.accusation_claim_bins,
                self.accusation_claim_populated_bins,
            ),
            (
                "vote_ballot_bins",
                self.vote_ballot_bins,
                self.vote_ballot_populated_bins,
            ),
            ("accusation_claim_crew_accuser.bins", crew.bins, crew.populated_bins),
            (
                "accusation_claim_impostor_accuser.bins",
                impostor.bins,
                impostor.populated_bins,
            ),
        ):
            if len(bins) != self.n_bins:
                raise ValueError(
                    f"{label} must have exactly n_bins={self.n_bins} entries, "
                    f"got {len(bins)}"
                )
            for expected_index, current_bin in enumerate(bins):
                if current_bin.bin_index != expected_index:
                    raise ValueError(
                        f"{label} must be in ascending bin_index order: entry "
                        f"{expected_index} has bin_index={current_bin.bin_index}"
                    )
            actual_populated = sum(1 for current_bin in bins if current_bin.count > 0)
            if declared != actual_populated:
                raise ValueError(
                    f"{label} populated-bin count must equal the number of bins "
                    f"with count > 0: declared {declared}, found {actual_populated}"
                )
        return self


def _is_impostor(
    roles: Mapping[PlayerId, Role],
    target: PlayerId,
    *,
    game_id: str,
    source: str,
) -> bool:
    """Return whether ``target`` was an impostor, failing loud on a gap.

    Uses subscript lookup (not ``.get``): ``roles`` is post-game ground truth
    covering every player by construction, so a missing ``target`` means the
    report is malformed and must raise rather than silently count as a non-hit
    (AGENTS.md "no silent fallbacks"). The bare ``KeyError`` is re-raised as a
    ``ValueError`` naming the offending game / source for a debuggable failure.
    """

    try:
        role = roles[target]
    except KeyError as exc:
        raise ValueError(
            f"malformed report: {source} target {target!r} in game {game_id!r} "
            "is absent from the post-game role ground truth, which covers every "
            "player by construction; refusing to silently treat it as a non-hit"
        ) from exc
    return role == "IMPOSTOR"


def _iter_accusation_claims(
    transcript: MeetingTranscript,
) -> Iterator[tuple[PlayerId, AccusationClaim]]:
    """Yield ``(speaker, claim)`` for every accusation in a meeting transcript.

    Accusations live on the turns of the reactive accusation chain (DESIGN.md
    §5.2, §5.3) -- the opening turn, every reply, and every opt-in turn -- and
    each is a distinct act that is counted. The ``Claim`` union is filtered by
    type via ``isinstance`` so the yielded value narrows to ``AccusationClaim``
    for the caller. The SPEAKER rides along because the accuser's role
    conditions the curve, and a second parallel walk to recover it could drift
    from this one.
    """

    for turn in transcript.turns:
        for claim in turn.claims:
            if isinstance(claim, AccusationClaim):
                yield turn.speaker, claim


def _accusation_claim_samples(
    report: TournamentReport,
) -> list[tuple[float, bool, bool]]:
    """Collect ``(confidence, is_impostor, accuser_is_impostor)`` per accusation."""

    samples: list[tuple[float, bool, bool]] = []
    for game in report.games:
        for meeting in game.meetings:
            for speaker, claim in _iter_accusation_claims(meeting.transcript):
                hit = _is_impostor(
                    game.roles,
                    claim.against,
                    game_id=game.game_id,
                    source="accusation-claim",
                )
                accuser_is_impostor = _is_impostor(
                    game.roles,
                    speaker,
                    game_id=game.game_id,
                    source="accusation-claim-speaker",
                )
                samples.append((claim.confidence, hit, accuser_is_impostor))
    return samples


def _vote_ballot_samples(report: TournamentReport) -> list[tuple[float, bool]]:
    """Collect ``(confidence, is_impostor)`` for every BINNABLE ballot.

    A ``"SKIP"`` ballot accuses no one and is excluded *before* the role lookup,
    so ``roles`` is never queried for the non-player ``"SKIP"``.

    A ballot whose rationale opens with a guard audit marker
    (:func:`_is_guard_authored`) is excluded too: the meeting layer rewrote its
    target while preserving the voter's confidence in the target they actually
    authored, so the recorded ``(target, confidence)`` pair is not one act by
    one agent and binning it scores the machinery's rewrite as agent
    miscalibration (audit A-3). :func:`_guard_authored_ballot_count` publishes
    how many were dropped, so the exclusion is never silent.
    """

    samples: list[tuple[float, bool]] = []
    for game in report.games:
        for meeting in game.meetings:
            for ballot in meeting.ballots:
                if _is_guard_authored(ballot.rationale_text):
                    continue
                if ballot.target == "SKIP":
                    continue
                hit = _is_impostor(
                    game.roles,
                    ballot.target,
                    game_id=game.game_id,
                    source="vote-ballot",
                )
                samples.append((ballot.confidence, hit))
    return samples


def _guard_authored_ballot_count(report: TournamentReport) -> int:
    """How many recorded ballots the vote curve dropped as guard-authored."""

    return sum(
        1
        for game in report.games
        for meeting in game.meetings
        for ballot in meeting.ballots
        if _is_guard_authored(ballot.rationale_text)
    )


def _bin_samples(
    samples: list[tuple[float, bool]], n_bins: int
) -> tuple[tuple[CalibrationBin, ...], int, float | None]:
    """Bin ``(confidence, is_impostor)`` samples into ``n_bins`` fixed bins.

    Returns the per-bin tally, the total sample count, and the expected
    calibration error (``None`` when there are no samples).
    """

    counts = [0] * n_bins
    hits = [0] * n_bins
    confidence_sums = [0.0] * n_bins
    for confidence, is_impostor in samples:
        index = min(int(confidence * n_bins), n_bins - 1)
        counts[index] += 1
        confidence_sums[index] += confidence
        if is_impostor:
            hits[index] += 1

    total = len(samples)
    bins: list[CalibrationBin] = []
    ece = 0.0
    for index in range(n_bins):
        lo = index / n_bins
        hi = (index + 1) / n_bins
        count = counts[index]
        rate = hits[index] / count if count else None
        mean_confidence = confidence_sums[index] / count if count else None
        bins.append(
            CalibrationBin(
                bin_index=index,
                lo=lo,
                hi=hi,
                midpoint=(lo + hi) / 2,
                count=count,
                impostor_hits=hits[index],
                actual_impostor_rate=rate,
                mean_confidence=mean_confidence,
            )
        )
        if count and rate is not None and mean_confidence is not None:
            ece += (count / total) * abs(rate - mean_confidence)

    return tuple(bins), total, (ece if total else None)


def compute_accusation_calibration(
    report: TournamentReport, *, n_bins: int = DEFAULT_N_BINS
) -> AccusationCalibrationReport:
    """Compute per-source accusation calibration for a tournament (§11.3).

    Walks every meeting in ``report``, collecting the confidence of every
    :class:`~meetings.schemas.AccusationClaim` and every non-``SKIP``
    :class:`~meetings.schemas.VoteBallot`, scoring each against the per-game
    role ground truth (``roles[target] == "IMPOSTOR"``), and binning the two
    sources into separate fixed-width calibration curves. Pure: it reads the
    report and returns a fresh result, mutating nothing.

    ``n_bins`` is the number of fixed-width bins over ``[0, 1]`` (default
    deciles). Raises ``ValueError`` if ``n_bins < 1``. Raises ``ValueError`` if
    any accusation targets a player absent from that game's ``roles`` (a
    malformed report -- see :func:`_is_impostor`). Each curve's
    ``*_populated_bins`` / ``*_low_power`` are derived from its binned counts
    (see :func:`_populated_bins` and :data:`MIN_POPULATED_BINS_FOR_POWER`).
    """

    if n_bins < 1:
        raise ValueError(f"n_bins must be >= 1, got {n_bins}")

    claim_samples = _accusation_claim_samples(report)
    claim_bins, claim_total, claim_ece = _bin_samples(
        [(confidence, hit) for confidence, hit, _ in claim_samples], n_bins
    )
    ballot_bins, ballot_total, ballot_ece = _bin_samples(
        _vote_ballot_samples(report), n_bins
    )
    claim_populated = _populated_bins(claim_bins)
    ballot_populated = _populated_bins(ballot_bins)
    return AccusationCalibrationReport(
        n_bins=n_bins,
        accusation_claim_bins=claim_bins,
        accusation_claim_total=claim_total,
        accusation_claim_ece=claim_ece,
        accusation_claim_populated_bins=claim_populated,
        accusation_claim_low_power=claim_populated < MIN_POPULATED_BINS_FOR_POWER,
        accusation_claim_crew_accuser=_curve(
            [
                (confidence, hit)
                for confidence, hit, accuser_is_impostor in claim_samples
                if not accuser_is_impostor
            ],
            n_bins,
        ),
        accusation_claim_impostor_accuser=_curve(
            [
                (confidence, hit)
                for confidence, hit, accuser_is_impostor in claim_samples
                if accuser_is_impostor
            ],
            n_bins,
        ),
        vote_ballot_bins=ballot_bins,
        vote_ballot_total=ballot_total,
        vote_ballot_ece=ballot_ece,
        vote_ballot_populated_bins=ballot_populated,
        vote_ballot_low_power=ballot_populated < MIN_POPULATED_BINS_FOR_POWER,
        vote_ballot_guard_authored_excluded=_guard_authored_ballot_count(report),
    )


def _curve(samples: list[tuple[float, bool]], n_bins: int) -> CalibrationCurve:
    """Bin ``samples`` and package the result as a :class:`CalibrationCurve`."""

    bins, total, ece = _bin_samples(samples, n_bins)
    populated = _populated_bins(bins)
    return CalibrationCurve(
        bins=bins,
        total=total,
        ece=ece,
        populated_bins=populated,
        low_power=populated < MIN_POPULATED_BINS_FOR_POWER,
    )


def _populated_bins(bins: tuple[CalibrationBin, ...]) -> int:
    """Count the bins that held at least one sample (the curve's ECE support)."""

    return sum(1 for current_bin in bins if current_bin.count > 0)


__all__ = [
    "AccusationCalibrationReport",
    "CalibrationBin",
    "CalibrationCurve",
    "DEFAULT_N_BINS",
    "MIN_POPULATED_BINS_FOR_POWER",
    "compute_accusation_calibration",
]
