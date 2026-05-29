"""Accusation-calibration metric (DESIGN.md §11.3).

A pure analyzer over :class:`eval.report_schema.TournamentReport` answering
DESIGN.md §11.3's calibration question: *are high-confidence accusations
correct more often than low-confidence ones?* A well-calibrated agent
population shows the actual-impostor rate of accusation targets rising
monotonically with stated confidence.

Accusations carry an explicit ``confidence`` in two structurally distinct
places, both reachable from the report without re-scraping raw replay JSONL:

* :class:`meetings.schemas.AccusationClaim` (``type="accusation"``,
  ``against``, ``confidence``) nested in ``ReportDocument.claims`` and
  ``Statement.claims`` inside each ``MeetingReport.transcript``.
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
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping

from pydantic import BaseModel, ConfigDict, model_validator

from engine.entities import Role
from eval.report_schema import TournamentReport
from meetings.schemas import AccusationClaim, MeetingTranscript, PlayerId

# Default number of fixed-width confidence bins over [0, 1]: deciles. An
# explicit, documented choice (DESIGN.md §11.3; see the PR's ## Decisions
# block). Overridable per call via the keyword-only ``n_bins`` argument.
DEFAULT_N_BINS: int = 10


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
    """

    n_bins: int
    accusation_claim_bins: tuple[CalibrationBin, ...]
    accusation_claim_total: int
    accusation_claim_ece: float | None
    vote_ballot_bins: tuple[CalibrationBin, ...]
    vote_ballot_total: int
    vote_ballot_ece: float | None

    @model_validator(mode="after")
    def _validate_bins(self) -> AccusationCalibrationReport:
        if self.n_bins < 1:
            raise ValueError(f"n_bins must be >= 1, got {self.n_bins}")
        for label, bins in (
            ("accusation_claim_bins", self.accusation_claim_bins),
            ("vote_ballot_bins", self.vote_ballot_bins),
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
) -> Iterator[AccusationClaim]:
    """Yield every :class:`AccusationClaim` in a meeting transcript.

    Accusations live on both the Phase-1 ``reports`` and the Phase-2
    ``statements`` (DESIGN.md §5.2, §5.3); each is a distinct act and is
    counted. The ``Claim`` union is filtered by type via ``isinstance`` so the
    yielded value narrows to ``AccusationClaim`` for the caller.
    """

    for report_doc in transcript.reports:
        for claim in report_doc.claims:
            if isinstance(claim, AccusationClaim):
                yield claim
    for statement in transcript.statements:
        for claim in statement.claims:
            if isinstance(claim, AccusationClaim):
                yield claim


def _accusation_claim_samples(report: TournamentReport) -> list[tuple[float, bool]]:
    """Collect ``(confidence, is_impostor)`` for every accusation claim."""

    samples: list[tuple[float, bool]] = []
    for game in report.games:
        for meeting in game.meetings:
            for claim in _iter_accusation_claims(meeting.transcript):
                hit = _is_impostor(
                    game.roles,
                    claim.against,
                    game_id=game.game_id,
                    source="accusation-claim",
                )
                samples.append((claim.confidence, hit))
    return samples


def _vote_ballot_samples(report: TournamentReport) -> list[tuple[float, bool]]:
    """Collect ``(confidence, is_impostor)`` for every non-SKIP ballot.

    A ``"SKIP"`` ballot accuses no one and is excluded *before* the role lookup,
    so ``roles`` is never queried for the non-player ``"SKIP"``.
    """

    samples: list[tuple[float, bool]] = []
    for game in report.games:
        for meeting in game.meetings:
            for ballot in meeting.ballots:
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
    malformed report -- see :func:`_is_impostor`).
    """

    if n_bins < 1:
        raise ValueError(f"n_bins must be >= 1, got {n_bins}")

    claim_bins, claim_total, claim_ece = _bin_samples(
        _accusation_claim_samples(report), n_bins
    )
    ballot_bins, ballot_total, ballot_ece = _bin_samples(
        _vote_ballot_samples(report), n_bins
    )
    return AccusationCalibrationReport(
        n_bins=n_bins,
        accusation_claim_bins=claim_bins,
        accusation_claim_total=claim_total,
        accusation_claim_ece=claim_ece,
        vote_ballot_bins=ballot_bins,
        vote_ballot_total=ballot_total,
        vote_ballot_ece=ballot_ece,
    )


__all__ = [
    "AccusationCalibrationReport",
    "CalibrationBin",
    "DEFAULT_N_BINS",
    "compute_accusation_calibration",
]
