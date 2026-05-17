"""Tests for the voting tally and ballot-normalisation helpers (Task 3.10).

The contract exercised here:

* :func:`meetings.voting.tally_ballots` implements DESIGN.md §5.5 +
  §5.2 PHASE 4 + §4.6: plurality with ``SKIP`` as a first-class
  target and the uncertainty-aware confidence-threshold check.
* :func:`meetings.voting.normalize_ballot_target` rewrites
  hallucinated / out-of-set targets to ``SKIP`` and preserves the
  original target in the audit-log marker on ``rationale_text``.
* The threshold check is inclusive at the cutoff: ``confidence ==
  skip_confidence_threshold`` ejects ("below threshold, skip").
* The "max confidence across the target's ballots" reading from
  DESIGN.md §4.6 governs the threshold check.

The functions are pure; tests construct :class:`VoteBallot` values
directly. No LLM, no manager, no orchestrator.
"""

from __future__ import annotations

import pytest

from meetings.schemas import VoteBallot
from meetings.voting import (
    INVALID_VOTE_TARGET_MARKER,
    SKIP_TARGET,
    normalize_ballot_target,
    tally_ballots,
)


# --- helpers ---------------------------------------------------------------


def _ballot(
    *,
    voter: str,
    target: str,
    confidence: float = 0.8,
    rationale_text: str = "stub-rationale",
) -> VoteBallot:
    """Build a :class:`VoteBallot` with non-zero defaults.

    Tests that focus on tally semantics use ``confidence=0.8`` so the
    default :data:`DEFAULT_SKIP_CONFIDENCE_THRESHOLD` of ``0.6`` is
    cleared without each test having to spell it out.
    """

    return VoteBallot(
        voter=voter,
        target=target,
        confidence=confidence,
        primary_reason_id=None,
        considered_alternatives=(),
        rationale_text=rationale_text,
    )


# ---------------------------------------------------------------------------
# tally_ballots
# ---------------------------------------------------------------------------


class TestTallyEmptyAndAllSkip:
    def test_empty_ballots_returns_skipped(self) -> None:
        outcome, ejected = tally_ballots((), skip_confidence_threshold=0.6)

        assert outcome == "SKIPPED"
        assert ejected is None

    def test_all_skip_returns_skipped(self) -> None:
        ballots = (
            _ballot(voter="p-1", target=SKIP_TARGET),
            _ballot(voter="p-2", target=SKIP_TARGET),
            _ballot(voter="p-3", target=SKIP_TARGET),
        )

        outcome, ejected = tally_ballots(ballots, skip_confidence_threshold=0.6)

        assert outcome == "SKIPPED"
        assert ejected is None


class TestTallyPlurality:
    def test_strict_plurality_with_confident_ballot_ejects(self) -> None:
        # 2 confident votes for p-3 vs 1 SKIP -> p-3 has strict
        # plurality and at least one ballot meets the threshold.
        ballots = (
            _ballot(voter="p-1", target="p-3", confidence=0.8),
            _ballot(voter="p-2", target="p-3", confidence=0.7),
            _ballot(voter="p-3", target=SKIP_TARGET),
        )

        outcome, ejected = tally_ballots(ballots, skip_confidence_threshold=0.6)

        assert outcome == "EJECTED"
        assert ejected == "p-3"

    def test_skip_alone_at_top_returns_skipped(self) -> None:
        # 2 SKIPs vs 1 non-SKIP -> SKIP wins plurality alone.
        ballots = (
            _ballot(voter="p-1", target=SKIP_TARGET),
            _ballot(voter="p-2", target=SKIP_TARGET),
            _ballot(voter="p-3", target="p-2", confidence=0.9),
        )

        outcome, ejected = tally_ballots(ballots, skip_confidence_threshold=0.6)

        assert outcome == "SKIPPED"
        assert ejected is None

    def test_skip_tied_with_player_returns_skipped(self) -> None:
        # {p-3: 1, SKIP: 1} -- SKIP is in the leader set, meeting did
        # not converge.
        ballots = (
            _ballot(voter="p-1", target="p-3", confidence=0.9),
            _ballot(voter="p-3", target=SKIP_TARGET),
        )

        outcome, ejected = tally_ballots(ballots, skip_confidence_threshold=0.6)

        assert outcome == "SKIPPED"
        assert ejected is None

    def test_two_non_skip_targets_tied_returns_skipped(self) -> None:
        # p-1 -> p-2, p-2 -> p-1, p-3 -> SKIP. SKIP is in leaders so
        # the tie collapses to SKIPPED; the schema-level TIE outcome
        # was deliberately removed.
        ballots = (
            _ballot(voter="p-1", target="p-2", confidence=0.9),
            _ballot(voter="p-2", target="p-1", confidence=0.9),
            _ballot(voter="p-3", target=SKIP_TARGET),
        )

        outcome, ejected = tally_ballots(ballots, skip_confidence_threshold=0.6)

        assert outcome == "SKIPPED"
        assert ejected is None

    def test_two_non_skip_tied_without_skip_still_returns_skipped(self) -> None:
        # Even without a SKIP vote on the table, a two-way tie
        # between non-skip targets still skips per DESIGN.md §5.2:
        # "If tie ... skip". This is the case that motivates rule (3)
        # in the docstring (the non-SKIP-in-leaders branch of the
        # leaders check).
        ballots = (
            _ballot(voter="p-1", target="p-2", confidence=0.9),
            _ballot(voter="p-2", target="p-1", confidence=0.9),
        )

        outcome, ejected = tally_ballots(ballots, skip_confidence_threshold=0.6)

        assert outcome == "SKIPPED"
        assert ejected is None

    def test_three_way_tie_among_players_returns_skipped(self) -> None:
        # Three distinct non-SKIP targets at one vote each: still a
        # tie at the top, no consensus -> SKIPPED.
        ballots = (
            _ballot(voter="p-1", target="p-2", confidence=0.9),
            _ballot(voter="p-2", target="p-3", confidence=0.9),
            _ballot(voter="p-3", target="p-1", confidence=0.9),
        )

        outcome, ejected = tally_ballots(ballots, skip_confidence_threshold=0.6)

        assert outcome == "SKIPPED"
        assert ejected is None


class TestTallyConfidenceThreshold:
    def test_below_threshold_plurality_returns_skipped(self) -> None:
        # 2 votes for p-3, both at confidence 0.4 -- below default
        # threshold 0.6, so plurality alone does not eject.
        ballots = (
            _ballot(voter="p-1", target="p-3", confidence=0.4),
            _ballot(voter="p-2", target="p-3", confidence=0.4),
            _ballot(voter="p-3", target=SKIP_TARGET),
        )

        outcome, ejected = tally_ballots(ballots, skip_confidence_threshold=0.6)

        assert outcome == "SKIPPED"
        assert ejected is None

    def test_max_confidence_across_target_satisfies_threshold(self) -> None:
        # Two voters for p-3: one well below threshold (0.2) and one
        # at threshold (0.6). The *max* meets the threshold per §4.6
        # so the eject proceeds.
        ballots = (
            _ballot(voter="p-1", target="p-3", confidence=0.2),
            _ballot(voter="p-2", target="p-3", confidence=0.6),
            _ballot(voter="p-3", target=SKIP_TARGET),
        )

        outcome, ejected = tally_ballots(ballots, skip_confidence_threshold=0.6)

        assert outcome == "EJECTED"
        assert ejected == "p-3"

    def test_threshold_is_inclusive_at_cutoff(self) -> None:
        # confidence == threshold ejects. "Below threshold, skip"
        # places the threshold value on the eject side.
        ballots = (
            _ballot(voter="p-1", target="p-3", confidence=0.6),
            _ballot(voter="p-2", target="p-3", confidence=0.6),
            _ballot(voter="p-3", target=SKIP_TARGET),
        )

        outcome, ejected = tally_ballots(ballots, skip_confidence_threshold=0.6)

        assert outcome == "EJECTED"
        assert ejected == "p-3"

    def test_higher_configured_threshold_skips_what_default_would_eject(
        self,
    ) -> None:
        # With threshold raised to 0.9, ballots at the default 0.8
        # confidence must skip even with a clean plurality.
        ballots = (
            _ballot(voter="p-1", target="p-3", confidence=0.8),
            _ballot(voter="p-2", target="p-3", confidence=0.8),
            _ballot(voter="p-3", target=SKIP_TARGET),
        )

        outcome, ejected = tally_ballots(ballots, skip_confidence_threshold=0.9)

        assert outcome == "SKIPPED"
        assert ejected is None

    def test_threshold_zero_always_ejects_on_strict_plurality(self) -> None:
        # Edge case: threshold=0 means any non-zero (or zero)
        # confidence is fine -- strict plurality alone determines
        # the eject.
        ballots = (
            _ballot(voter="p-1", target="p-3", confidence=0.0),
            _ballot(voter="p-2", target="p-3", confidence=0.0),
            _ballot(voter="p-3", target=SKIP_TARGET),
        )

        outcome, ejected = tally_ballots(ballots, skip_confidence_threshold=0.0)

        assert outcome == "EJECTED"
        assert ejected == "p-3"

    def test_threshold_one_requires_full_confidence(self) -> None:
        # threshold=1.0 requires a perfectly confident ballot.
        ballots = (
            _ballot(voter="p-1", target="p-3", confidence=0.99),
            _ballot(voter="p-2", target="p-3", confidence=0.99),
            _ballot(voter="p-3", target=SKIP_TARGET),
        )

        outcome, ejected = tally_ballots(ballots, skip_confidence_threshold=1.0)

        assert outcome == "SKIPPED"
        assert ejected is None

        # Bump one ballot to 1.0 and the eject proceeds.
        ballots_with_one = (
            _ballot(voter="p-1", target="p-3", confidence=1.0),
            _ballot(voter="p-2", target="p-3", confidence=0.99),
            _ballot(voter="p-3", target=SKIP_TARGET),
        )

        outcome, ejected = tally_ballots(
            ballots_with_one, skip_confidence_threshold=1.0
        )

        assert outcome == "EJECTED"
        assert ejected == "p-3"


class TestTallyThresholdValidation:
    @pytest.mark.parametrize("threshold", [-0.1, 1.1, -1.0, 2.0])
    def test_out_of_range_threshold_raises(self, threshold: float) -> None:
        ballots = (_ballot(voter="p-1", target=SKIP_TARGET),)
        with pytest.raises(ValueError, match="skip_confidence_threshold"):
            tally_ballots(ballots, skip_confidence_threshold=threshold)


class TestTallyDeterminism:
    def test_outcome_is_independent_of_ballot_order(self) -> None:
        # Two non-SKIP targets tied at one vote each + one SKIP.
        # Permuting the ballot order must not change the outcome
        # (SKIPPED) -- the tally cannot leak insertion order into
        # the resolution.
        b1 = _ballot(voter="p-1", target="p-2", confidence=0.9)
        b2 = _ballot(voter="p-2", target="p-1", confidence=0.9)
        b3 = _ballot(voter="p-3", target=SKIP_TARGET)

        results = []
        for permutation in (
            (b1, b2, b3),
            (b3, b2, b1),
            (b2, b3, b1),
            (b3, b1, b2),
        ):
            results.append(tally_ballots(permutation, skip_confidence_threshold=0.6))

        assert all(r == results[0] for r in results)
        assert results[0] == ("SKIPPED", None)

    def test_strict_plurality_outcome_is_independent_of_ballot_order(
        self,
    ) -> None:
        # Same idea but for the EJECTED branch: a clean plurality
        # must always resolve to the same ejected id no matter the
        # ballot order.
        b1 = _ballot(voter="p-1", target="p-3", confidence=0.8)
        b2 = _ballot(voter="p-2", target="p-3", confidence=0.8)
        b3 = _ballot(voter="p-3", target=SKIP_TARGET)

        results = []
        for permutation in (
            (b1, b2, b3),
            (b3, b2, b1),
            (b2, b3, b1),
            (b3, b1, b2),
        ):
            results.append(tally_ballots(permutation, skip_confidence_threshold=0.6))

        assert all(r == results[0] for r in results)
        assert results[0] == ("EJECTED", "p-3")


# ---------------------------------------------------------------------------
# normalize_ballot_target
# ---------------------------------------------------------------------------


class TestNormalizePassthrough:
    def test_skip_target_passes_through_unchanged(self) -> None:
        ballot = _ballot(voter="p-1", target=SKIP_TARGET, rationale_text="no read")
        normalized = normalize_ballot_target(ballot, candidate_targets=("p-2", "p-3"))

        assert normalized is ballot
        assert normalized.target == SKIP_TARGET
        assert normalized.rationale_text == "no read"

    def test_valid_candidate_passes_through_unchanged(self) -> None:
        ballot = _ballot(voter="p-1", target="p-3", rationale_text="caught venting")
        normalized = normalize_ballot_target(ballot, candidate_targets=("p-2", "p-3"))

        assert normalized is ballot
        assert normalized.target == "p-3"
        assert normalized.rationale_text == "caught venting"


class TestNormalizeInvalid:
    def test_hallucinated_target_is_rewritten_to_skip(self) -> None:
        ballot = _ballot(voter="p-1", target="ghost", rationale_text="ghost did it")
        normalized = normalize_ballot_target(ballot, candidate_targets=("p-2", "p-3"))

        assert normalized.target == SKIP_TARGET

    def test_original_target_preserved_in_marker(self) -> None:
        ballot = _ballot(voter="p-1", target="ghost", rationale_text="ghost did it")
        normalized = normalize_ballot_target(ballot, candidate_targets=("p-2", "p-3"))

        expected_marker = INVALID_VOTE_TARGET_MARKER.format(target="ghost")
        assert normalized.rationale_text.startswith(expected_marker)
        # repr of "ghost" should appear so the original target is
        # recoverable from the audit log.
        assert "'ghost'" in normalized.rationale_text

    def test_original_rationale_is_preserved_after_marker(self) -> None:
        ballot = _ballot(
            voter="p-1", target="ghost", rationale_text="the original reason"
        )
        normalized = normalize_ballot_target(ballot, candidate_targets=("p-2", "p-3"))

        # Marker then original rationale, concatenated.
        assert normalized.rationale_text.endswith("the original reason")
        marker = INVALID_VOTE_TARGET_MARKER.format(target="ghost")
        assert normalized.rationale_text == marker + "the original reason"

    def test_self_vote_is_treated_as_invalid(self) -> None:
        # The manager builds candidate_targets by excluding the voter.
        # A ballot whose target equals the voter must therefore be
        # normalised even though "p-1" is a real participant id.
        ballot = _ballot(voter="p-1", target="p-1", rationale_text="meta vote")
        normalized = normalize_ballot_target(ballot, candidate_targets=("p-2", "p-3"))

        assert normalized.target == SKIP_TARGET
        marker = INVALID_VOTE_TARGET_MARKER.format(target="p-1")
        assert normalized.rationale_text.startswith(marker)

    def test_ejected_participant_id_is_treated_as_invalid(self) -> None:
        # An LLM may reference a player who was ejected in a prior
        # meeting -- the orchestrator omits that id from
        # candidate_targets. The ballot must be normalised so the
        # tally cannot resolve to ``EJECTED`` against a non-living
        # participant.
        ballot = _ballot(
            voter="p-2",
            target="p-9",
            rationale_text="p-9 was suspicious last meeting",
        )
        normalized = normalize_ballot_target(ballot, candidate_targets=("p-1", "p-3"))

        assert normalized.target == SKIP_TARGET
        marker = INVALID_VOTE_TARGET_MARKER.format(target="p-9")
        assert normalized.rationale_text.startswith(marker)

    def test_normalized_ballot_is_a_new_object(self) -> None:
        # ``VoteBallot`` is frozen; the normaliser must return a
        # copy rather than mutate the input. Test by mutating-style
        # equality: the original ballot must still carry the original
        # target after the call.
        ballot = _ballot(voter="p-1", target="ghost", rationale_text="x")
        normalized = normalize_ballot_target(ballot, candidate_targets=("p-2", "p-3"))

        assert ballot.target == "ghost"
        assert normalized.target == SKIP_TARGET
        assert normalized is not ballot


class TestNormalizeAndTallyTogether:
    """Round-trip: normalise then tally, end-to-end on bogus inputs."""

    def test_normalised_hallucinated_ballots_do_not_corrupt_tally(self) -> None:
        # All three voters return "ghost" with high confidence. After
        # normalisation every ballot is a SKIP, so the tally must
        # SKIP with no non-participant id reachable.
        raw = (
            _ballot(voter="p-1", target="ghost", confidence=0.95),
            _ballot(voter="p-2", target="ghost", confidence=0.95),
            _ballot(voter="p-3", target="ghost", confidence=0.95),
        )
        candidates = ("p-1", "p-2", "p-3")
        normalised = tuple(
            normalize_ballot_target(b, candidate_targets=candidates) for b in raw
        )

        outcome, ejected = tally_ballots(normalised, skip_confidence_threshold=0.6)

        assert outcome == "SKIPPED"
        assert ejected is None
        for ballot in normalised:
            assert ballot.target == SKIP_TARGET

    def test_mixed_valid_and_invalid_ballots_tally_correctly(self) -> None:
        # p-1, p-2 cast confident valid votes for p-3; p-3 hallucinates
        # "ghost". After normalisation: 2 votes for p-3 + 1 SKIP.
        # Outcome: EJECTED p-3.
        candidates_for_p1_p2 = ("p-2", "p-3")
        candidates_for_p3 = ("p-1", "p-2")
        raw = (
            normalize_ballot_target(
                _ballot(voter="p-1", target="p-3", confidence=0.8),
                candidate_targets=candidates_for_p1_p2,
            ),
            normalize_ballot_target(
                _ballot(voter="p-2", target="p-3", confidence=0.7),
                candidate_targets=candidates_for_p1_p2,
            ),
            normalize_ballot_target(
                _ballot(voter="p-3", target="ghost", confidence=0.5),
                candidate_targets=candidates_for_p3,
            ),
        )

        outcome, ejected = tally_ballots(raw, skip_confidence_threshold=0.6)

        assert outcome == "EJECTED"
        assert ejected == "p-3"
