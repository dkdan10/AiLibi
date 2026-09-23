"""The gameplay extractor's suspicion-row pattern parses BOTH rendered shapes.

The weighing channel (ruling D5 of 2026-09-19,
``tasks/work/ballot-weighing-channel.md``) deleted the trust column from the
rendered suspicion row rather than keep displaying a constant. Two readers of
that row were widened in that card —
``eval.meeting_quality._SUSPICION_GRAPH_ROW_RE`` and
``eval.validity._SUSPICION_GRAPH_ROW_RE`` — and a THIRD was left narrowed
because the card could not move ``audits/`` bytes; its deviation 5 routed that
third reader to the re-record card by name.

Why this needs a test rather than a one-line diff: a narrowed pattern does not
fail loudly. It returns NO rows, which empties the per-target rendered-suspicion
map, builds no accumulator trajectory, scores ``r3_arcs`` 0 on every game and
sinks the geomean rubric to 0.0 across a whole set — a silently zeroed shipped
surface rather than an error. That is what the re-record observed on its first
leg, and it is what the RED half of this test reproduces.
"""

from __future__ import annotations

import re

from audits.workflows.extract_gameplay_facts import (
    _SUSPICION_GRAPH_HEADERS,
    _parse_suspicion_graph,
)

# The pattern exactly as it stood before this card, kept HERE as a planted
# failure rather than in the module: the assertions below prove it is red on the
# post-weighing-channel shape, so a future narrowing cannot pass silently.
_NARROWED_ROW_RE = re.compile(
    r"`(?P<pid>p-\d+)`: suspicion (?P<sus>[0-9]*\.?[0-9]+), "
    r"trust (?P<trust>[0-9]*\.?[0-9]+)"
)

_PRE_CARD_PROMPT = (
    "## Your suspicion of each player\n"
    "- `p-4`: suspicion 0.60, trust 0.50\n"
    "- `p-7`: suspicion 0.25, trust 0.50\n"
    "\n"
    "## Your ballot\n"
)

_POST_CARD_PROMPT = (
    "## Your suspicion of each player\n"
    "- `p-4`: suspicion 0.60\n"
    "- `p-7`: suspicion 0.25\n"
    "\n"
    "## Your ballot\n"
)

_EXPECTED = {"p-4": 0.60, "p-7": 0.25}


def _narrowed_graph(prompt: str) -> dict[str, float]:
    """``_parse_suspicion_graph``'s body, driven by the pre-card pattern."""

    header = next((h for h in _SUSPICION_GRAPH_HEADERS if h in prompt), None)
    if header is None:
        return {}
    block = prompt.split(header, 1)[1].split("## ", 1)[0]
    return {
        m.group("pid"): float(m.group("sus")) for m in _NARROWED_ROW_RE.finditer(block)
    }


class TestBothRenderedShapesParse:
    def test_the_pre_card_row_with_its_trust_suffix_still_parses(self) -> None:
        # The neutrality half: every committed pre-record row carries the trust
        # suffix, and it must keep parsing to the identical figures.
        assert _parse_suspicion_graph(_PRE_CARD_PROMPT) == _EXPECTED

    def test_the_post_card_row_without_trust_parses(self) -> None:
        # The repair half: the shape the re-record's bytes actually carry.
        assert _parse_suspicion_graph(_POST_CARD_PROMPT) == _EXPECTED

    def test_the_trust_less_shape_yields_a_non_empty_map(self) -> None:
        # Stated separately from the equality above because the FAILURE MODE is
        # an empty map, not a wrong number: this is the assertion that an
        # accumulator trajectory can be built at all.
        parsed = _parse_suspicion_graph(_POST_CARD_PROMPT)
        assert parsed, "a post-weighing-channel row must yield a rendered row"
        assert len(parsed) == 2

    def test_a_prompt_with_no_graph_section_is_empty_for_both_shapes(self) -> None:
        assert _parse_suspicion_graph("## Your ballot\nno graph here\n") == {}


class TestTheNarrowedPatternIsRedOnTheNewShape:
    """The planted failure: the pre-card pattern, shown failing where it must."""

    def test_the_narrowed_pattern_returns_nothing_on_the_post_card_shape(
        self,
    ) -> None:
        # SILENT: an empty map, never an exception — which is exactly why the
        # rubric zeroed a whole set instead of erroring.
        assert _narrowed_graph(_POST_CARD_PROMPT) == {}

    def test_the_narrowed_pattern_and_the_shipped_one_agree_on_the_old_shape(
        self,
    ) -> None:
        # Re-scoring history is the thing this change must not do. Proven
        # exhaustively over the preserved pre-record bytes at the re-record
        # (0 mismatches over 6,779 prompts and 14,599 parsed rows); pinned here
        # on the shape those bytes carry.
        assert _narrowed_graph(_PRE_CARD_PROMPT) == _parse_suspicion_graph(
            _PRE_CARD_PROMPT
        )
