"""Raw-vs-rendered gate-band pin for the ballot-redirect guard (Task 15.6).

The §4.6 verdict the model reads is the ``"%.2f"``-rendered max suspicion
over the living ejection targets (``vote_ballot.j2``); the redirect guard
(:func:`meetings.manager.guard_ballot_target_graph`) recomputes that verdict
so it can bind an under-gate eject target. Before Task 15.6 the guard
compared RAW suspicion floats while the prompt rendered two decimals, so a
raw value in the ``[0.595, 0.60)`` band -- which renders as ``0.60`` (the
model reads MUST-vote) -- read MUST-skip in the guard, and the two
disagreed (audit post-phase-14-pause §4.1).

These fixtures pin guard-vs-render agreement across ``[0.55, 0.65]``,
including the band, three ways: against the pure 2dp quantization, against
the ACTUAL rendered prompt as parsed by the shipped eval parser, and on the
specific band values the fix exists for. Committed sets still byte-verify
independently (``verify_samples.sh``): replays reconstruct from recorded
actions, so no OFF-path prompt byte moves -- only live in-band recordings
change.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agents.strategic.prompts.loader import build_environment, vote_ballot_prompt
from eval._suspicion_parse import (
    SKIP_SUSPICION_THRESHOLD,
    parse_rendered_max_suspicion,
)
from meetings.manager import (
    BALLOT_TARGET_REDIRECT_MARKER,
    guard_ballot_target_graph,
)
from meetings.render_contract import SuspicionEntry
from meetings.schemas import MeetingTranscript, VoteBallot

_GATE: float = 0.6
_VOTER = "p-1"
# p-2 carries the sole graph row (the verdict max); p-3 is the ballot's
# under-gate eject target (no row at all), so a MUST-vote verdict redirects
# to p-2 and a MUST-skip verdict leaves the eject on p-3 unchanged.
_ROW_HOLDER = "p-2"
_UNDER_GATE_TARGET = "p-3"
_CANDIDATES: tuple[str, ...] = (_ROW_HOLDER, _UNDER_GATE_TARGET)


def _sweep_values() -> list[float]:
    """A dense sweep of ``[0.55, 0.65]`` plus points straddling the boundary.

    The straddle points sit inside the ``[0.595, 0.60)`` band where raw and
    2dp-rendered verdicts diverge -- 0.596/0.597/0.599 all render ``0.60``
    (MUST-vote) while their raw float reads MUST-skip.
    """

    grid = [round(0.55 + 0.0025 * step, 4) for step in range(41)]
    straddle = [0.594, 0.595, 0.596, 0.597, 0.599, 0.5999, 0.6, 0.6001, 0.601]
    return sorted(set(grid) | set(straddle))


def _eject_ballot(target: str) -> VoteBallot:
    return VoteBallot(
        voter=_VOTER,
        target=target,
        confidence=0.85,
        primary_reason_id=None,
        considered_alternatives=(),
        rationale_text="model rationale",
    )


def _guarded(value: float) -> VoteBallot:
    return guard_ballot_target_graph(
        ballot=_eject_ballot(_UNDER_GATE_TARGET),
        voter_id=_VOTER,
        suspicion_graph=(
            SuspicionEntry(player_id=_ROW_HOLDER, suspicion=value, trust=0.5),
        ),
        candidate_targets=_CANDIDATES,
        skip_confidence_threshold=_GATE,
    )


def _guard_reads_must_vote(value: float) -> bool:
    # MUST-vote redirects the under-gate p-3 eject onto the p-2 row; MUST-skip
    # leaves the eject on p-3 (a recorded inversion, frozen semantics).
    guarded = _guarded(value)
    if guarded.target == _ROW_HOLDER:
        assert guarded.rationale_text.startswith(
            BALLOT_TARGET_REDIRECT_MARKER.format(target=_UNDER_GATE_TARGET)
        )
        return True
    assert guarded.target == _UNDER_GATE_TARGET
    assert guarded == _eject_ballot(_UNDER_GATE_TARGET)
    return False


class TestGuardRenderAgreementAcrossBand:
    """The redirect guard's verdict equals the rendered-value verdict."""

    @pytest.mark.parametrize("value", _sweep_values())
    def test_guard_matches_the_2dp_rendered_verdict(self, value: float) -> None:
        # The model reads the "%.2f"-rendered value; the guard must read the
        # same number. Quantize the raw value to the 2dp grid and compare.
        rendered_must_vote = float("%.2f" % value) >= _GATE
        assert _guard_reads_must_vote(value) is rendered_must_vote

    @pytest.mark.parametrize("value", _sweep_values())
    def test_guard_matches_the_actual_prompt_as_the_eval_parser_reads_it(
        self, value: float
    ) -> None:
        # End-to-end: render the canonical qwen3_32b ballot, recover the max
        # the model saw with the SHIPPED eval parser, and confirm the guard's
        # verdict agrees with that recovered value against the eval threshold.
        environment = build_environment("qwen3_32b")
        prompt = vote_ballot_prompt(
            voter_id=_VOTER,
            rendered_memory="(private memory)",
            transcript=MeetingTranscript(turns=()),
            contradiction_flags=(),
            suspicion_graph=(
                SuspicionEntry(player_id=_ROW_HOLDER, suspicion=value, trust=0.5),
            ),
            candidate_targets=_CANDIDATES,
            skip_confidence_threshold=_GATE,
            environment=environment,
        )
        parsed = parse_rendered_max_suspicion(prompt)
        assert parsed is not None
        rendered_must_vote = parsed >= SKIP_SUSPICION_THRESHOLD
        assert _guard_reads_must_vote(value) is rendered_must_vote


class TestGateBandFix:
    """The specific band the fix exists for, and the unchanged extremes."""

    @pytest.mark.parametrize("value", [0.596, 0.597, 0.599, 0.5999])
    def test_in_band_raw_reads_must_vote_matching_the_rendered_060(
        self, value: float
    ) -> None:
        # These raw floats are BELOW the gate but render as **0.60** (the model
        # reads MUST-vote). The pre-15.6 raw comparison read MUST-skip; the
        # quantize-then-compare guard now agrees with the render.
        assert value < _GATE  # raw is under the gate...
        assert float("%.2f" % value) == _GATE  # ...but renders AT it.
        assert _guard_reads_must_vote(value) is True

    def test_just_below_the_band_still_reads_must_skip(self) -> None:
        # 0.594 renders as 0.59 -> the model reads MUST-skip and the guard
        # agrees; the eject stays a recorded inversion.
        assert float("%.2f" % 0.594) < _GATE
        assert _guard_reads_must_vote(0.594) is False

    def test_clearly_over_and_under_are_unchanged(self) -> None:
        assert _guard_reads_must_vote(0.65) is True
        assert _guard_reads_must_vote(0.55) is False


class TestLoaderImportsNoManager:
    """Grep-zero: the loader imports NOTHING from ``meetings.manager``."""

    def test_loader_source_has_no_meetings_manager_import(self) -> None:
        # The render contract now lives in the ``meetings.render_contract`` leaf,
        # so ``agents/strategic/prompts/loader.py`` -- an ``agents/`` module --
        # must not import the 3-KLoC manager (the ``agents ↛ meetings.manager``
        # firewall, enforced at lint time and pinned here).
        import agents.strategic.prompts.loader as loader_mod

        source = Path(loader_mod.__file__).read_text()
        tree = ast.parse(source)
        offending: list[int] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "meetings.manager":
                offending.append(node.lineno)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "meetings.manager" or alias.name.startswith(
                        "meetings.manager."
                    ):
                        offending.append(node.lineno)
        assert offending == [], (
            f"loader.py imports from meetings.manager at lines {offending}"
        )
