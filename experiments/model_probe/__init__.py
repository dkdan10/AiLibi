"""Model-probe harness — isolated prompt/config lab (Phase 9 investigation).

Reconstructs real vote-ballot decision contexts from committed replays and runs
them through model x think x num_ctx x prompt-variant matrices against local
Ollama, with deterministic grading against ground truth. Read-only against the
sim; outputs an artifact (results table + findings). See
.claude/plans (the approved plan) for the rationale.

Layout:
  corpus.py  -- reconstruct the decision corpus (the heavy, reuse-only piece)
  probe.py   -- the matrix runner (drives Ollama directly via llm._default_send)
  grade.py   -- deterministic grader + report
"""
