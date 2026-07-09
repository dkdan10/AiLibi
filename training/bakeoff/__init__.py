"""The Phase-15 bake-off package (Task 15.14+).

Home of the shared, audited evolution-strategy optimizer
(:mod:`training.bakeoff.es`) that every ES/QD trainer in the phase reuses, and
the adversarial Goodhart probe (:mod:`training.bakeoff.goodhart`) that red-teams
the Task 15.2 champion-selection referee before the mid-phase pause is allowed to
trust it as a gate.

The ES core lands here first (Task 15.14) so 15.15 (the impostor bake-off) and
15.16 (the crew track) extend ONE optimizer behind their dependency edge, rather
than each re-deriving a population loop. numpy is deliberately NOT used in the ES
core: the champion genome + fitness trace are hash-pinned for determinism, and a
pure-Python loop is bit-stable across machines and thread counts where BLAS
reductions are not (the ``training.env`` production-inference posture).
"""

from __future__ import annotations
