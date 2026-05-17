"""Voting tally and ballot normalisation (DESIGN.md §5.5).

The meeting protocol resolves a meeting by tallying each living
participant's :class:`meetings.schemas.VoteBallot`. The tally is
mechanical — it does NOT invoke the LLM — and applies the
uncertainty-aware skip rule from DESIGN.md §4.6 ("the default voting
heuristic does not vote-eject if max suspicion confidence < 0.6;
instead it skips"). The *ballot* itself is LLM-produced (Task 3.7
``vote_ballot.j2``); the resolution step lives here so that meeting
outcomes are deterministic across replays even when the LLM is
non-deterministic (DESIGN.md §0 rule 1: tick-based deterministic
engine).

This module exposes two pure functions:

* :func:`normalize_ballot_target` — defensive normalisation of a
  parsed :class:`VoteBallot`. Targets that are neither
  :data:`SKIP_TARGET` nor in the voter's candidate set are rewritten
  to :data:`SKIP_TARGET` with :data:`INVALID_VOTE_TARGET_MARKER`
  prefixed onto ``rationale_text`` so the audit log preserves the
  original (invalid) target verbatim. Without this, a hallucinated
  id could resolve the meeting to ``EJECTED`` against a
  non-participant — corrupting outcome application and replay
  integrity.

* :func:`tally_ballots` — plurality tally with the confidence
  threshold enforced. :data:`SKIP_TARGET` is a first-class tally
  target (DESIGN.md §5.5 schemas ``VoteBallot.target`` as
  ``PlayerId | Literal["SKIP"]``); see the function docstring for
  the full resolution rules.

Both functions take a :class:`VoteBallot` (already parsed from the
structured LLM output by the caller) and return Python values; no
LLM call, no I/O, no shared mutable state. They are safe to call
from anywhere — the orchestrator's meeting-resolution step, replay
analysis, or eval harnesses — without worrying about side effects.

Manager-side implementation note
================================

:class:`meetings.manager.MeetingManager` retains its own private
copies of :func:`tally_ballots` and :func:`normalize_ballot_target`
(written in Task 3.8). Task 3.10's contract scopes only the new
module + its tests; future work may consolidate the manager onto
this canonical home. The threshold semantics in :func:`tally_ballots`
exactly match the manager's ``_tally`` so the two implementations
agree on every input.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Final

from meetings.schemas import MeetingOutcome, PlayerId, VoteBallot

SKIP_TARGET: Final[str] = "SKIP"
"""Sentinel :attr:`VoteBallot.target` value indicating the voter skips.

DESIGN.md §5.5 schemas this as a literal alongside :class:`PlayerId`
in :attr:`VoteBallot.target`; it is the only non-:class:`PlayerId`
value the tally accepts.
"""

INVALID_VOTE_TARGET_MARKER: Final[str] = (
    "[invalid target {target!r} normalized to SKIP] "
)
"""Marker prefix added to ``rationale_text`` when a target is normalised.

Preserves the original (invalid) target verbatim in the audit log
while the tally treats the ballot as a :data:`SKIP_TARGET`. The
``{target!r}`` placeholder is filled with :func:`repr` of the
original target so quoting is unambiguous (an LLM that returns the
literal string ``"SKIP"`` cannot collide with the sentinel).
Pattern-matchable by downstream replay / eval code.

Matches :data:`meetings.manager.INVALID_VOTE_TARGET_MARKER` byte for
byte so the manager's private normaliser and this module produce
identical audit-trail strings on the same input.
"""


def normalize_ballot_target(
    ballot: VoteBallot,
    *,
    candidate_targets: tuple[PlayerId, ...],
) -> VoteBallot:
    """Defensively normalise a ballot whose ``target`` is unknown.

    Returns ``ballot`` unchanged when ``ballot.target`` is
    :data:`SKIP_TARGET` or appears in ``candidate_targets``. Otherwise
    rewrites ``target`` to :data:`SKIP_TARGET` and prepends
    :data:`INVALID_VOTE_TARGET_MARKER` (formatted with the original
    target) onto ``rationale_text``.

    Voting for oneself is treated as an invalid target because the
    meeting manager excludes the voter from its own
    ``candidate_targets``; this catches the case where an LLM
    hallucinates self-voting. Likewise an id that belonged to a
    participant who is no longer living (e.g. ejected in a prior
    meeting) is normalised because the meeting manager only includes
    living participants in ``candidate_targets``.

    The rewrite uses :meth:`VoteBallot.model_copy` to preserve the
    frozen-model invariants on :class:`VoteBallot`; the input is not
    mutated.
    """

    if ballot.target == SKIP_TARGET or ballot.target in candidate_targets:
        return ballot
    marker = INVALID_VOTE_TARGET_MARKER.format(target=ballot.target)
    return ballot.model_copy(
        update={
            "target": SKIP_TARGET,
            "rationale_text": marker + ballot.rationale_text,
        }
    )


def tally_ballots(
    ballots: Sequence[VoteBallot],
    *,
    skip_confidence_threshold: float,
) -> tuple[MeetingOutcome, PlayerId | None]:
    """Plurality tally with confidence threshold (DESIGN.md §5.2 + §4.6 + §5.5).

    :data:`SKIP_TARGET` is a real tally target — a vote of
    :data:`SKIP_TARGET` competes with non-skip votes for plurality.
    Two reads from the protocol motivate this:

    * DESIGN.md §5.5 schemas :attr:`VoteBallot.target` as
      ``PlayerId | Literal["SKIP"]`` — :data:`SKIP_TARGET` is a
      first-class target, not an abstention.
    * DESIGN.md §5.2 PHASE 4 says "If tie or below threshold, skip"
      — if :data:`SKIP_TARGET` were dropped from the tally, a single
      non-skip vote among many skips would still eject, which
      contradicts the "below threshold, skip" intent.

    Resolution rules (applied in order):

    1. **Empty ballots** -> ``"SKIPPED"``. No votes to tally.
    2. **:data:`SKIP_TARGET` has plurality** (alone or tied at the
       top) -> ``"SKIPPED"``. A skip tied with one or more players
       is treated as skip because the table did not converge on an
       eject.
    3. **Two or more non-skip targets tied at the top** ->
       ``"SKIPPED"`` (DESIGN.md §5.2: "if tie ... skip"). The
       schema-level ``TIE`` outcome was deliberately omitted from
       :class:`meetings.schemas.MeetingOutcome` because DESIGN.md
       only defines ejection-or-skip.
    4. **Single non-skip target with strict plurality AND at least
       one ballot for that target has ``confidence >=
       skip_confidence_threshold``** -> ``"EJECTED"``.
    5. **Otherwise** (strict plurality but no confident ballot) ->
       ``"SKIPPED"``. This is the mechanical "meets threshold" check
       from DESIGN.md §5.2 PHASE 4. The tally enforces it
       independent of LLM compliance with the vote prompt's
       ``skip_confidence_threshold`` instruction. The "max confidence
       across the target's ballots" reading matches DESIGN.md §4.6
       ("max suspicion confidence < 0.6 ... skip"): the eject requires
       at least one voter to be confident, not all of them.

    The threshold check is **inclusive** at the cutoff: a confidence
    of exactly ``skip_confidence_threshold`` ejects. The rule is
    "below threshold, skip", so the threshold value itself is on the
    eject side.

    Args:
        ballots: Living participants' ballots, parsed and (ideally)
            normalised by :func:`normalize_ballot_target`. Order does
            not affect the result.
        skip_confidence_threshold: Eject cutoff in ``[0, 1]``;
            DESIGN.md §4.6 defaults to ``0.6``. Must be a valid
            probability; out-of-range values raise to fail loud
            (AGENTS.md "no silent fallbacks").

    Returns:
        Tuple of (outcome, ejected_player_id). On ``"EJECTED"`` the
        second element is the ejected player id; on ``"SKIPPED"`` it
        is ``None``.

    Raises:
        ValueError: If ``skip_confidence_threshold`` is not in
            ``[0, 1]``.
    """

    if not 0.0 <= skip_confidence_threshold <= 1.0:
        raise ValueError(
            "skip_confidence_threshold must be in [0, 1], "
            f"got {skip_confidence_threshold}"
        )

    tallies: dict[str, int] = {}
    for ballot in ballots:
        tallies[ballot.target] = tallies.get(ballot.target, 0) + 1
    if not tallies:
        return "SKIPPED", None

    max_votes = max(tallies.values())
    leaders = sorted(target for target, count in tallies.items() if count == max_votes)

    if SKIP_TARGET in leaders:
        return "SKIPPED", None
    if len(leaders) > 1:
        return "SKIPPED", None

    leader = leaders[0]
    leader_max_confidence = max(
        ballot.confidence for ballot in ballots if ballot.target == leader
    )
    if leader_max_confidence < skip_confidence_threshold:
        return "SKIPPED", None
    return "EJECTED", leader


__all__ = [
    "INVALID_VOTE_TARGET_MARKER",
    "SKIP_TARGET",
    "normalize_ballot_target",
    "tally_ballots",
]
