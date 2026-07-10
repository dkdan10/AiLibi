"""The productized learned tactical champion (Task 15.20).

The pause's champion — the ``utility-es`` learned utility scorer over
FSM-proposed impostor options (audits/audit-phase-15-pause.md decision 1) —
promoted into production inference behind the observation firewall:

- :mod:`agents.tactical.learned.forward` — the pure-Python forward pass, ported
  bit-exactly from the training-side reference
  (``training/bakeoff/utility_es.py``; the decision-6 Q4 gate pins the parity).
- :mod:`agents.tactical.learned.weights` — the committed champion artifact
  (float-hex ``weights.json`` + sha256 sidecar, value-identical to
  ``training/artifacts/impostor/utility-es/``) and its verifying loader.
- :mod:`agents.tactical.learned.factory` —
  :func:`~agents.tactical.learned.factory.build_learned_agent_factory`, the
  opt-in agent factory beside the untouched scripted FSM default (decision 2,
  branch A), plus the engine-free five-field provenance stamp record 15.21's
  CLI turns into the real ``orchestrator.replay.TacticalPolicyStamp``.

Firewall posture: nothing under this package imports ``engine/``,
``training/``, ``orchestrator/``, numpy, or torch — enforced by import-linter
and the extended source scan in ``tests/test_firewall.py``.
"""
