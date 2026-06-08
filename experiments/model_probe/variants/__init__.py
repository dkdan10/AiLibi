"""Prompt-variant registry for the conversion lab (P2).

A variant is a callable ``(VoteContext) -> str`` that renders the vote-ballot
prompt from the SAME reconstructed context as the baseline, through an alternate
template in ``templates/``. This is how we test whether rewriting the §4.6 skip
rule (the F1 command-asymmetry) flips real skipped decisions.

P1 uses only ``baseline`` (the production template, injected by the caller). The
variant templates + their schemas land in P2; ``KNOWN_VARIANTS`` lists the
planned set so ``probe.py --variants`` validates names up front.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from experiments.model_probe.corpus import VoteContext

_TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
_ENV = Environment(
    loader=FileSystemLoader(_TEMPLATE_DIR),
    autoescape=False,
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
)

# Planned P2 variants (templates added in P2):
#   v1_verdict   — orchestrator-rendered §4.6 verdict line ("0.80 >= 0.60 — skip
#                  does NOT apply"); the model keeps the choice.
#   v2_symmetric — remove the hard-SKIP / soft-eject asymmetry + the rule-2
#                  override-license + the cascade excuse; eject and skip are
#                  equally hard commands.
#   v3_abstain   — 3-way ballot: SKIP = active objection, ABSTAIN = unsure and
#                  does NOT block (needs an abstain-capable output schema).
#   v4_brief     — cap the rationale (orthogonal F2-pollution mitigation).
KNOWN_VARIANTS: dict[str, str] = {
    "v1_verdict": "v1_verdict.j2",
    "v1_verdict_hard": "v1_verdict_hard.j2",  # 9B-targeted anti-discount
    "v2_symmetric": "v2_symmetric.j2",
    "v3_abstain": "v3_abstain.j2",
    "v4_brief": "v4_brief.j2",
}


def _render_with(template_name: str) -> Callable[[VoteContext], str]:
    def render(context: VoteContext) -> str:
        return _ENV.get_template(template_name).render(
            voter_id=context.voter_id,
            rendered_memory=context.rendered_memory,
            transcript=context.transcript,
            contradiction_flags=context.contradiction_flags,
            suspicion_graph=context.suspicion_graph,
            candidate_targets=context.candidate_targets,
            skip_confidence_threshold=context.skip_confidence_threshold,
            fellow_impostor_ids=context.fellow_impostor_ids,
        )

    return render


def variant_renderers(
    names: list[str], *, baseline: Callable[[VoteContext], str]
) -> dict[str, Callable[[VoteContext], str]]:
    """Resolve variant names to renderers; ``baseline`` is injected by the caller."""

    renderers: dict[str, Callable[[VoteContext], str]] = {}
    for name in names:
        if name == "baseline":
            renderers["baseline"] = baseline
        elif name in KNOWN_VARIANTS:
            renderers[name] = _render_with(KNOWN_VARIANTS[name])
        else:
            raise SystemExit(
                f"unknown variant {name!r}; known: "
                f"baseline, {', '.join(KNOWN_VARIANTS)}"
            )
    return renderers
