"""Pin: eval's re-declared skip threshold equals the constants home (Task 15.6).

``eval._suspicion_parse.SKIP_SUSPICION_THRESHOLD`` is deliberately
re-declared as a literal rather than imported, so the audits workflow can
import the parse module without dragging in the simulation (the module
stays pure-stdlib; see its own docstring and ``eval/_suspicion_parse.py:54``).
The cost of that deliberate duplication is drift risk: if the §4.6 gate
constant ever moves and the eval literal is not updated in lockstep, the
shipped ``missed_skip`` / ``threshold_inversion`` SKIP metrics would classify
RECORDED ballots against a threshold different from the one those prompts
were rendered under.

This is the pin the post-phase-14 pause audit (§3, constant homing) asked
for: it fails loudly the moment the eval literal diverges from
:data:`meetings.constants.DEFAULT_SKIP_CONFIDENCE_THRESHOLD`, its single
definition home. The committed baseline sets were recorded under that value,
so the eval literal must equal it exactly for the recorded-ballot
classification to stay honest.
"""

from __future__ import annotations

from eval._suspicion_parse import SKIP_SUSPICION_THRESHOLD
from meetings.constants import DEFAULT_SKIP_CONFIDENCE_THRESHOLD


def test_eval_threshold_equals_the_constants_home() -> None:
    # The deliberate re-declaration (eval/_suspicion_parse.py:54) must track
    # the single definition home byte-for-byte, or the recorded-ballot SKIP
    # metrics classify against a stale gate.
    assert SKIP_SUSPICION_THRESHOLD == DEFAULT_SKIP_CONFIDENCE_THRESHOLD
