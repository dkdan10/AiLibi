"""Canonical parse of the rendered §4.6 vote-gate suspicion line (Task 9.6).

The v5 vote prompt (``agents/strategic/prompts/vote_ballot.j2``) renders the
DESIGN.md §4.6 gate verdict for the voter as::

    Your maximum suspicion among the living ejection targets is
    **0.80**; the skip threshold is **0.60**.

The captured ``**X**`` is the voter's maximum suspicion over the LIVING
ejection candidates (the template computes it over ``candidate_targets``, so
dead / ejected / self / teammate rows never contribute), and it is the only
place that per-ballot gate input survives into the recorded replay — the
belief graph itself is not persisted per ballot. Two offline consumers
classify SKIP ballots against it:

* :mod:`eval.meeting_quality` — the shipped ``missed_skip_ballots`` /
  ``threshold_inversions`` SKIP sentinels on the tournament eval report
  (DESIGN.md §11.3, §5.5; audit gp-2).
* ``audits/workflows/extract_gameplay_facts.py`` — the gameplay-data audit's
  ``skip_partition`` / ``threshold_inversions`` facts (``audits`` -> ``eval``
  is the allowed consumer direction).

This module is their single shared home (audit gp-2): the regex and the
classification threshold live HERE and are imported by both sides, so the
shipped metric and the audit extractor can never drift apart on what "the
rendered max" or "missed" means. Do not duplicate the regex in either
consumer. Pure stdlib (``re`` only): no engine / agents / meetings imports,
so the audits workflow can import it without dragging in the simulation.
"""

from __future__ import annotations

import re
from typing import Final

# The rendered §4.6 vote-gate line in the v5 vote prompt (built by
# meetings.manager from vote_ballot.j2; surveyed across the committed sets as
# "...maximum suspicion among the living ejection targets is    **0.80**; the
# skip threshold is **0.60**..."). The capture group is the rendered MAX over
# the living ejection targets the voter was shown. ``\s*`` bridges the
# template's line wrap between "is" and the bolded value.
VOTE_MAX_SUSPICION_RE: Final[re.Pattern[str]] = re.compile(
    r"maximum suspicion among the living ejection targets is\s*\*\*([0-9]*\.?[0-9]+)\*\*"
)

# Classification cutoff for a SKIP ballot: CORRECT when the rendered max is
# below this, MISSED at or above it (Task 9.6 contract; mirrors the inclusive
# ">= threshold ejects" rule of meetings.voting.tally_votes). 0.60 is the
# §4.6 default the committed sets were recorded under
# (``meetings.manager.DEFAULT_SKIP_CONFIDENCE_THRESHOLD``); it is re-declared
# here as a literal so this module stays import-free for the audits workflow,
# and because classification of RECORDED ballots must match the threshold
# rendered into those prompts, not whatever the live knob later becomes.
SKIP_SUSPICION_THRESHOLD: Final[float] = 0.60


def parse_rendered_max_suspicion(prompt: str) -> float | None:
    """Pull the rendered §4.6 max suspicion from a v5 vote prompt, or None.

    Returns the float captured from the "maximum suspicion among the living
    ejection targets is **X**" line. ``None`` means the prompt is not a vote
    prompt (no such line) — callers treat that as "could not classify", never
    as a zero.
    """

    match = VOTE_MAX_SUSPICION_RE.search(prompt)
    if match is None:
        return None
    return float(match.group(1))


__all__ = [
    "SKIP_SUSPICION_THRESHOLD",
    "VOTE_MAX_SUSPICION_RE",
    "parse_rendered_max_suspicion",
]
