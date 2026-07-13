"""Task 16.16 — persona text: the voice layer, per-branch render fixtures.

The persona card assigned in Task 16.9 (``orchestrator.personas`` — frozen
there; only card TEXT refines in 16.16) renders as a guarded ``<voice>`` block
in the instruction preamble of all four locked-set templates, behind ONE
set-level version bump (v2 -> v3, pinned in
``tests/agents/test_bespoke_prompt_sets.py``). The design contract
(post-phase-14 V&J planning §4.1-4.2):

* **Style only, never claims** — the voice shapes ``free_text`` /
  ``rationale_text`` diction; observations, claims, and ballots stay
  schema-locked, and the card never enters ``rendered_memory`` (the firewall
  orthogonality §4.1 proves: the persona is an instruction-preamble input,
  disjoint from the visibility-gated memory feed).
* **Guarded byte-identical** — an empty persona renders the exact pre-16.16
  bytes, so the layer is inert wherever assignment is off. The committed-set
  proof is the prompt-byte golden (``tests/meetings/test_prompt_byte_golden``,
  green over both committed sample sets); the per-branch structural proof is
  :func:`test_persona_layer_is_purely_additive_for_every_bank_card` below —
  excising the voice layer from a persona-bearing render restores the empty
  render byte-for-byte, so nothing outside the guarded block moved.
* **Per-turn re-anchoring** (§4.2's drift toolkit) — the reactive turn
  template (``accusation_round.j2``, the one a chain renders repeatedly)
  closes its ``<rules>`` block with the "Stay in the voice described above"
  line; the opening/ballot templates render once per meeting and carry no
  re-anchor.

The role-neutrality of the refined card TEXT is the leak-suite sweep in
``tests/orchestrator/test_personas.py`` (the forbidden-substring scan + the
chi-square role-independence sweeps), which re-runs on the committed bank
these fixtures render.

Renders go through
:func:`agents.strategic.prompts.loader.build_prompt_renderers` — the
production loader over the real template bytes (the 16.15 fixture
convention).
"""

from __future__ import annotations

from agents.strategic.prompts.loader import (
    PromptRenderers,
    build_environment,
    build_prompt_renderers,
    vote_ballot_prompt,
)
from meetings.manager import SuspicionEntry
from meetings.schemas import (
    AccusationClaim,
    MeetingTranscript,
    MeetingTurn,
    TurnKind,
)
from orchestrator.personas import load_persona_bank

# The locked set (Task 16.2 GO; directory agents/strategic/prompts/qwen3_6_27b/).
_LOCKED_SET = "qwen3_6_27b"

# The voice layer's rendered markers. ``_VOICE_PREFIX`` prefixes the card text
# in every preamble block; ``_REANCHOR`` is the drift-discipline line the turn
# template alone carries (the task hint's phrase, verbatim).
_VOICE_OPEN_LINE = "<voice>\n"
_VOICE_CLOSE_LINE = "</voice>\n"
_VOICE_PREFIX = "Your voice at this table: "
_REANCHOR = "Stay in the voice described above"

# A sentinel card text that appears nowhere in any template or fixture input,
# so occurrence counts are exact. Shaped like a real card (disposition + two
# diction notes + the never-beat) without being one.
_SENTINEL_PERSONA = (
    "A dry, deliberate test voice. Speaks in short lines. Never rambles past the point."
)

# A small reconstructed body-report context — enough to exercise every branch
# (mirrors tests/meetings/test_elicitation_fixtures.py).
_OPENING = MeetingTurn(
    turn_id="m-1:turn-0",
    turn_index=0,
    speaker="p-2",
    turn_kind="opening",
    reply_to=None,
    observations=(),
    claims=(
        AccusationClaim(
            type="accusation", against="p-3", confidence=0.7, reason="near body"
        ),
    ),
    free_text="p-3 was near where it happened.",
)
_PRIOR = MeetingTurn(
    turn_id="m-1:turn-1",
    turn_index=1,
    speaker="p-4",
    turn_kind="reply",
    reply_to="m-1:turn-0",
    observations=(),
    claims=(
        AccusationClaim(
            type="accusation", against="p-3", confidence=0.8, reason="seen there"
        ),
    ),
    free_text="p-3 was in electrical at 405.",
)
_TRANSCRIPT = MeetingTranscript(turns=(_OPENING, _PRIOR))
_MEMORY = (
    "## Your role\nCREWMATE\n## Observations\n- [tick 405] You saw p-3 in ELECTRICAL.\n"
)
_GRAPH = (
    SuspicionEntry(player_id="p-3", suspicion=0.80, trust=0.50, flag_lift=0.30),
    SuspicionEntry(player_id="p-5", suspicion=0.55, trust=0.50, unattributed=0.05),
)


def _renderers() -> PromptRenderers:
    return build_prompt_renderers(_LOCKED_SET)


def _render_crewmate(*, persona: str = "", emergency: bool = False) -> str:
    trigger = (
        "p-2 called an emergency meeting at tick 410"
        if emergency
        else "p-2 reported body of p-7 at tick 410"
    )
    return _renderers().crewmate_report(
        agent_id="p-2",
        current_tick=410,
        meeting_trigger=trigger,
        rendered_memory=_MEMORY,
        public_transcript="",
        living_ids=("p-3", "p-5"),
        dead_ids=("p-7",),
        persona=persona,
    )


def _render_impostor_opening(*, persona: str = "") -> str:
    return _renderers().impostor_report(
        agent_id="p-3",
        current_tick=410,
        meeting_trigger="p-3 reported body of p-7 at tick 410",
        rendered_memory=_MEMORY,
        public_transcript="",
        fellow_impostor_ids=("p-9",),
        living_ids=("p-2", "p-5"),
        dead_ids=("p-7",),
        persona=persona,
    )


def _render_statement(
    *, turn_kind: TurnKind, is_impostor: bool, persona: str = ""
) -> str:
    return _renderers().statement(
        agent_id="p-3",
        rendered_memory=_MEMORY,
        transcript=_TRANSCRIPT,
        contradictions=(),
        prior_turn=_PRIOR if turn_kind == "reply" else None,
        turn_kind=turn_kind,
        fellow_impostor_ids=(("p-9",) if is_impostor else ()),
        living_ids=("p-2", "p-5"),
        dead_ids=("p-7",),
        is_impostor=is_impostor,
        is_body_report=True,
        persona=persona,
    )


def _render_vote(*, persona: str = "") -> str:
    return _renderers().vote(
        voter_id="p-2",
        rendered_memory=_MEMORY,
        transcript=_TRANSCRIPT,
        contradiction_flags=(),
        suspicion_graph=_GRAPH,
        candidate_targets=("p-3", "p-5"),
        skip_confidence_threshold=0.6,
        persona=persona,
    )


def _all_locked_set_renders(persona: str = "") -> dict[str, str]:
    """Every branch of every template of the locked set (the sweep surface)."""

    return {
        "crewmate_report/body": _render_crewmate(persona=persona),
        "crewmate_report/emergency": _render_crewmate(persona=persona, emergency=True),
        "impostor_report/body": _render_impostor_opening(persona=persona),
        "reply/crew": _render_statement(
            turn_kind="reply", is_impostor=False, persona=persona
        ),
        "reply/impostor": _render_statement(
            turn_kind="reply", is_impostor=True, persona=persona
        ),
        "opt_in": _render_statement(
            turn_kind="opt_in", is_impostor=False, persona=persona
        ),
        "vote": _render_vote(persona=persona),
    }


# The turn-template branches (the re-anchor surface) vs the once-per-meeting
# surfaces (openings + ballot, deliberately re-anchor-free).
_TURN_BRANCHES = frozenset({"reply/crew", "reply/impostor", "opt_in"})


def _strip_voice_layer(rendered: str) -> str:
    """Excise the 16.16 voice layer from a render, byte-exactly.

    Removes each ``<voice>`` block together with the ONE guarded blank
    separator line that renders before it (the ``{% if persona %}`` block
    opens with a blank line, matching the template's section-separator
    convention), and the re-anchor line the turn template's rules block
    carries. On an empty-persona render this is the identity — which
    :func:`test_empty_persona_renders_zero_trace_of_the_layer` pins — so
    ``strip(with_persona) == render(empty)`` proves the layer is purely
    additive: every byte outside the guarded regions is untouched.
    """

    lines = rendered.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line == _VOICE_OPEN_LINE:
            assert out and out[-1] == "\n", "expected a blank line before <voice>"
            out.pop()
            while i < len(lines) and lines[i] != _VOICE_CLOSE_LINE:
                i += 1
            assert i < len(lines), "unterminated <voice> block"
            i += 1
            continue
        if line.startswith(_REANCHOR):
            i += 1
            continue
        out.append(line)
        i += 1
    return "".join(out)


def _section(rendered: str, open_tag: str, close_tag: str) -> str:
    """The ``open_tag``..``close_tag`` slice of a render (tags included)."""

    start = rendered.index(open_tag)
    end = rendered.index(close_tag, start)
    return rendered[start : end + len(close_tag)]


# ---------------------------------------------------------------------------
# Empty persona: byte-identity (the layer is inert wherever assignment is off)
# ---------------------------------------------------------------------------


def test_empty_persona_renders_zero_trace_of_the_layer() -> None:
    # DoD: an empty persona renders the exact pre-16.16 bytes. The committed
    # sets are the golden's business; per branch, the structural half is that
    # no voice-layer byte renders at all — and the stripper is the identity,
    # which is what gives the purely-additive test below its meaning.
    for name, rendered in _all_locked_set_renders().items():
        assert "<voice>" not in rendered, name
        assert _VOICE_PREFIX not in rendered, name
        assert _REANCHOR not in rendered, name
        assert _strip_voice_layer(rendered) == rendered, name


def test_default_persona_kwarg_is_the_empty_render() -> None:
    # The loader wrappers default ``persona=""`` (the 16.3 widening), so a
    # call site that never threads a persona — every ad-hoc render — gets the
    # empty-persona bytes. One direct loader call without the kwarg pins it
    # (environment pinned to the locked set; the process default is the 9B set).
    without_kwarg = vote_ballot_prompt(
        voter_id="p-2",
        rendered_memory=_MEMORY,
        transcript=_TRANSCRIPT,
        contradiction_flags=(),
        suspicion_graph=_GRAPH,
        candidate_targets=("p-3", "p-5"),
        skip_confidence_threshold=0.6,
        environment=build_environment(_LOCKED_SET),
    )
    assert without_kwarg == _render_vote()


def test_persona_layer_is_purely_additive_for_every_bank_card() -> None:
    # DoD: each bank card renders into the preamble with the schema-locked
    # sections untouched. Excising the voice layer from a persona-bearing
    # render must restore the empty render BYTE-FOR-BYTE, for every committed
    # card on every branch — so the card changed nothing outside the guarded
    # block: not the rules, not the output contract, not the memory.
    empties = _all_locked_set_renders()
    for card in load_persona_bank():
        renders = _all_locked_set_renders(persona=card.text)
        for name, rendered in renders.items():
            assert rendered != empties[name], (name, card.id)  # the layer rendered
            assert _strip_voice_layer(rendered) == empties[name], (name, card.id)


# ---------------------------------------------------------------------------
# The preamble placement: instruction preamble only, never memory/observations
# ---------------------------------------------------------------------------


def test_each_bank_card_renders_into_every_instruction_preamble() -> None:
    # DoD: each bank card renders into the preamble on a fixture. The voice
    # block sits after the role framing and BEFORE the memory block on every
    # branch, and it introduces no markdown header (the machine anchors —
    # "## This meeting" / "## Your turn" — stay the first header).
    for card in load_persona_bank():
        marker = f"{_VOICE_PREFIX}{card.text}"
        for name, rendered in _all_locked_set_renders(persona=card.text).items():
            assert marker in rendered, (name, card.id)
            assert rendered.index(marker) < rendered.index("<memory>"), (name, card.id)
            assert rendered.index("</persona>") < rendered.index("<voice>"), (
                name,
                card.id,
            )
            assert rendered.index("<voice>") < rendered.index("\n## "), (name, card.id)


def test_persona_text_appears_nowhere_in_memory_or_observation_sections() -> None:
    # DoD: the persona block appears in the instruction preamble and NOWHERE
    # in the memory/observation sections — the firewall orthogonality. The
    # sentinel occurs exactly once per render (the preamble block), and the
    # <memory> / <transcript> sections are byte-identical to the empty
    # render's (the card never perturbs the visibility-gated feed).
    empties = _all_locked_set_renders()
    for name, rendered in _all_locked_set_renders(_SENTINEL_PERSONA).items():
        assert rendered.count(_SENTINEL_PERSONA) == 1, name
        memory = _section(rendered, "<memory>", "</memory>")
        assert _SENTINEL_PERSONA not in memory, name
        assert "<voice>" not in memory, name
        assert memory == _section(empties[name], "<memory>", "</memory>"), name
        if "<transcript>" in rendered:
            transcript = _section(rendered, "<transcript>", "</transcript>")
            assert _SENTINEL_PERSONA not in transcript, name
            assert "<voice>" not in transcript, name
            assert transcript == _section(
                empties[name], "<transcript>", "</transcript>"
            ), name


# ---------------------------------------------------------------------------
# The per-turn re-anchor line (drift discipline, §4.2's toolkit)
# ---------------------------------------------------------------------------


def test_reanchor_line_closes_the_turn_template_rules() -> None:
    # DoD: the per-turn re-anchor line is present in the turn template. It
    # renders inside the <rules> block on every reactive branch (reply crew,
    # reply impostor, opt_in) — the template a chain renders repeatedly, where
    # persona drift accumulates — and only when a persona is on.
    for name, rendered in _all_locked_set_renders(_SENTINEL_PERSONA).items():
        if name in _TURN_BRANCHES:
            assert _REANCHOR in rendered, name
            assert (
                rendered.index("<rules>")
                < rendered.index(_REANCHOR)
                < rendered.index("</rules>")
            ), name
        else:
            # The openings and the ballot render once per meeting — no drift
            # to re-anchor; the preamble block alone carries the voice there
            # (a deliberate pin: growing a re-anchor onto a once-per-meeting
            # surface is a design change, not a drive-by).
            assert _REANCHOR not in rendered, name
