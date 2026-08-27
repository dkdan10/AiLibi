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

import json
import pathlib
from collections import Counter

import pytest

from agents.strategic.prompts.loader import (
    CANONICAL_MAP_CARD,
    PromptRenderers,
    build_environment,
    build_prompt_renderers,
    classify_flag_for_prompt,
    vote_ballot_prompt,
)
from api.schemas import classify_evidence
from eval._suspicion_parse import VOTE_MAX_SUSPICION_RE, parse_rendered_max_suspicion
from meetings.manager import SuspicionEntry
from meetings.schemas import (
    AccusationClaim,
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    TurnKind,
)
from meetings.transcript import (
    WEAK_CONTRADICTION_MARKER_PREFIX,
    is_weak_contradiction,
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
    # ``map_card`` is passed because ``build_prompt_renderers`` binds it at
    # construction (Task 20.31) and this call bypasses that binding; it is not
    # what the test is about.
    without_kwarg = vote_ballot_prompt(
        voter_id="p-2",
        rendered_memory=_MEMORY,
        transcript=_TRANSCRIPT,
        contradiction_flags=(),
        suspicion_graph=_GRAPH,
        candidate_targets=("p-3", "p-5"),
        skip_confidence_threshold=0.6,
        environment=build_environment(_LOCKED_SET),
        map_card=CANONICAL_MAP_CARD,
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


# ---------------------------------------------------------------------------
# v4 (Task 20.31): the evidence split, the vent exemption, the bookkeeping
# ---------------------------------------------------------------------------

# Three planted flags, one per group, so a rendered block can be read exactly.
_PROOF_FLAG = ContradictionRef(
    contradiction_id="c-proof",
    kind="vent_sighting",
    event_a_id="turn:m-1:turn-0:obs:0",
    event_b_id="turn:m-1:turn-0:obs:0",
    subjects=("p-3",),
    description="p-3 was seen venting in MEDBAY",
)
_CONFLICT_FLAG = ContradictionRef(
    contradiction_id="c-conflict",
    kind="alibi_vs_sighting",
    event_a_id="turn:m-1:turn-0:claim:0",
    event_b_id="turn:m-1:turn-1:obs:0",
    subjects=("p-5",),
    description="p-5's alibi conflicts with a sighting",
)
_WEAK_FLAG = ContradictionRef(
    contradiction_id="c-weak",
    kind="alibi_conflict",
    event_a_id="turn:m-1:turn-0:claim:1",
    event_b_id="turn:m-1:turn-1:claim:0",
    subjects=("p-6",),
    description=(
        f"{WEAK_CONTRADICTION_MARKER_PREFIX}self-pair] p-6's two alibis disagree"
    ),
)
_ALL_FLAGS = (_PROOF_FLAG, _CONFLICT_FLAG, _WEAK_FLAG)

_PROOF_HEADING = "Proof. Only an impostor can vent"
_CONFLICT_HEADING = "Conflicting accounts. Two statements that cannot both be true"
_WEAK_HEADING = "Weak signals. The same kind of conflict"

_REPLAY_SAMPLE_SETS = (
    pathlib.Path(__file__).resolve().parents[2] / "replays" / "samples" / "9p2i",
    pathlib.Path(__file__).resolve().parents[2] / "replays" / "samples" / "4p1i",
)


def _render_flagged_vote(flags: tuple[ContradictionRef, ...]) -> str:
    return _renderers().vote(
        voter_id="p-2",
        rendered_memory=_MEMORY,
        transcript=_TRANSCRIPT,
        contradiction_flags=flags,
        suspicion_graph=_GRAPH,
        candidate_targets=("p-3", "p-5"),
        skip_confidence_threshold=0.6,
    )


def _render_flagged_reply(flags: tuple[ContradictionRef, ...]) -> str:
    return _renderers().statement(
        agent_id="p-3",
        rendered_memory=_MEMORY,
        transcript=_TRANSCRIPT,
        contradictions=flags,
        prior_turn=_PRIOR,
        turn_kind="reply",
        fellow_impostor_ids=(),
        living_ids=("p-2", "p-5"),
        dead_ids=("p-7",),
        is_impostor=False,
        is_body_report=True,
    )


def _recorded_sample_flags() -> list[ContradictionRef]:
    """Every flag recorded in the two committed sample sets."""

    flags: list[ContradictionRef] = []
    for set_dir in _REPLAY_SAMPLE_SETS:
        for path in sorted(set_dir.glob("replay-seed-*.jsonl")):
            with path.open(encoding="utf-8") as handle:
                for line in handle:
                    record = json.loads(line)
                    if record.get("kind") != "meeting":
                        continue
                    flags.extend(
                        ContradictionRef.model_validate(raw)
                        for raw in record.get("contradictions", ())
                    )
    return flags


def test_flag_block_renders_the_committed_taxonomy() -> None:
    # Verdicts claim 2: "Each flag below is VERIFIED evidence" appeared in
    # 2,543 of 2,543 recorded ballot prompts, over a class whose sole-flag
    # precision is 12/82. v4 groups instead of asserting.
    for rendered in (
        _render_flagged_vote(_ALL_FLAGS),
        _render_flagged_reply(_ALL_FLAGS),
    ):
        assert _PROOF_HEADING in rendered
        assert _CONFLICT_HEADING in rendered
        assert _WEAK_HEADING in rendered
        # Proof first, weak signals last -- the subordinate group.
        assert (
            rendered.index(_PROOF_HEADING)
            < rendered.index(_CONFLICT_HEADING)
            < rendered.index(_WEAK_HEADING)
        )
        # Every planted flag renders EXACTLY ONCE, inside its own group's
        # slice: a loop that dropped a row, duplicated one, or emitted it
        # under the wrong heading fails here even though the headings stand.
        groups = {
            _PROOF_HEADING: _PROOF_FLAG,
            _CONFLICT_HEADING: _CONFLICT_FLAG,
            _WEAK_HEADING: _WEAK_FLAG,
        }
        bounds = sorted(rendered.index(heading) for heading in groups)
        for heading, flag in groups.items():
            start = rendered.index(heading)
            after = [index for index in bounds if index > start]
            slice_ = rendered[start : (after[0] if after else len(rendered))]
            for flag_body, owner in ((f.description, f) for f in _ALL_FLAGS):
                expected = 1 if owner is flag else 0
                assert slice_.count(flag_body) == expected, (heading, owner)
            assert rendered.count(flag.description) == 1, flag
        assert "VERIFIED evidence" not in rendered
        assert "verified flag" not in rendered
    # The ballot's own echo of the deleted framing is gone too.
    assert "whose account a verified flag broke" not in _render_flagged_vote(_ALL_FLAGS)


def test_absent_groups_render_no_heading() -> None:
    # The gate can fail: with only a conflicting-accounts flag on the table,
    # the proof and weak headings must not render -- a template that printed
    # the headings unconditionally would tell a voter proof exists when none
    # does.
    only_conflict = _render_flagged_vote((_CONFLICT_FLAG,))
    assert _CONFLICT_HEADING in only_conflict
    assert _PROOF_HEADING not in only_conflict
    assert _WEAK_HEADING not in only_conflict


def test_the_detector_weak_stamp_moves_a_flag_between_groups() -> None:
    # The perturbation that proves the split is computed from the flag, not
    # from its position: strip the detector's own marker off the weak flag and
    # the same flag renders under "Conflicting accounts" instead.
    unstamped = _WEAK_FLAG.model_copy(
        update={"description": "p-6's two alibis disagree"}
    )
    assert classify_flag_for_prompt(_WEAK_FLAG) == "weak_signal"
    assert classify_flag_for_prompt(unstamped) == "cross_statement"
    stamped_render = _render_flagged_vote((_WEAK_FLAG,))
    unstamped_render = _render_flagged_vote((unstamped,))
    assert _WEAK_HEADING in stamped_render
    assert _WEAK_HEADING not in unstamped_render
    assert _CONFLICT_HEADING in unstamped_render


def test_an_unknown_flag_kind_fails_loud_rather_than_bucketing() -> None:
    # No silent fallbacks: a kind the table has no rule for is a finding to
    # record, not a bucket to widen. ``ContradictionRef.kind`` is a closed
    # Literal, so the planted case bypasses validation to reach the rule.
    planted = _CONFLICT_FLAG.model_construct(
        contradiction_id="c-new",
        kind="telepathy",
        event_a_id="a",
        event_b_id="b",
        subjects=("p-5",),
        description="something the detector does not emit yet",
    )
    with pytest.raises(ValueError, match="unclassifiable flag kind"):
        classify_flag_for_prompt(planted)


def test_prompt_split_matches_the_api_taxonomy_on_every_committed_flag() -> None:
    # The agents' view and the spectator's view cannot drift: the render-side
    # split and ``api.schemas.classify_evidence`` produce identical
    # per-category counts over every flag of both committed sample sets. This
    # is evidence only because neither implementation imports the other -- the
    # test may import both, the production code may not.
    flags = _recorded_sample_flags()
    assert flags, "no committed sample flags found"
    prompt_side: Counter[str] = Counter()
    api_side: Counter[str] = Counter()
    for flag in flags:
        prompt_side[classify_flag_for_prompt(flag)] += 1
        api_side[
            classify_evidence(
                kind=flag.kind,
                event_a_id=flag.event_a_id,
                event_b_id=flag.event_b_id,
                weak=is_weak_contradiction(flag),
            )
        ] += 1
    assert prompt_side == api_side
    assert sum(prompt_side.values()) == len(flags)


def test_alibi_vs_physical_is_cross_statement_on_both_sides() -> None:
    # Deliberately NOT widened here. 37 of the 42 committed alibi_vs_physical
    # flags are the grounded vent-placement arm, where one side is engine
    # truth -- arguably role proof -- but the contract scopes ROLE-PROOF to
    # vent_sighting / self-linked, and moving them is one decision taken once,
    # in api/schemas.py and eval/deduction_metrics.py together
    # (api/schemas.py:721-737). This render must not be the third place it
    # quietly changes.
    physical = _CONFLICT_FLAG.model_copy(update={"kind": "alibi_vs_physical"})
    assert classify_flag_for_prompt(physical) == "cross_statement"
    assert (
        classify_evidence(
            kind=physical.kind,
            event_a_id=physical.event_a_id,
            event_b_id=physical.event_b_id,
            weak=is_weak_contradiction(physical),
        )
        == "cross_statement"
    )


def test_vent_mandate_exempts_a_dead_or_ejected_subject_in_every_branch() -> None:
    # G-23: 232 saw_vent observations in the corpus name a corpse, and
    # 5.0-5.5% of turns lose their accusation to one. Every branch that orders
    # the re-speak now names the exception -- and the priority clause and the
    # every-meeting re-speak survive verbatim beside it.
    exemption = (
        "if the player you saw vent is already dead or ejected, that case is closed"
    )
    branches = {
        "crewmate_report/body": _render_crewmate(),
        "crewmate_report/emergency": _render_crewmate(emergency=True),
        "reply/crew": _render_statement(turn_kind="reply", is_impostor=False),
        "opt_in": _render_statement(turn_kind="opt_in", is_impostor=False),
    }
    for name, rendered in branches.items():
        assert exemption in rendered, name
        assert "speak it FIRST" in rendered, name
        assert "already said it at an earlier meeting" in rendered, name
    # The impostor reply states no vent mandate at all, so it states no
    # exemption either (the accusation-only cover surface).
    impostor_reply = _render_statement(turn_kind="reply", is_impostor=True)
    assert "speak it FIRST" not in impostor_reply
    assert exemption not in impostor_reply


def test_ballot_keeps_the_rendered_maximum_the_offline_scrape_reads() -> None:
    # The one per-ballot gate input that survives into a replay: two offline
    # consumers (eval.meeting_quality, eval.vj_instruments) read this line off
    # recorded prompts through eval._suspicion_parse. The wording must survive
    # the bump byte-shaped, and capture the same value.
    rendered = _render_flagged_vote(())
    match = VOTE_MAX_SUSPICION_RE.search(rendered)
    assert match is not None
    assert match.group(1) == "0.80"  # max suspicion over p-3 / p-5 in _GRAPH
    assert parse_rendered_max_suspicion(rendered) == 0.80


def test_threshold_arithmetic_leaves_the_agents_voice() -> None:
    # G-29: "the 0.60 threshold" was quoted back in the characters' voices 208
    # times corpus-wide. The ballot no longer states a numeric cutoff or asks
    # the model to reason against one, and it forbids quoting the bookkeeping.
    rendered = _render_flagged_vote(_ALL_FLAGS)
    assert "skip threshold" not in rendered
    assert "reference point" not in rendered
    assert "0.60" not in rendered
    assert "Read that as evidence, never as an instruction" in rendered
    assert (
        "never quote a suspicion score or any other bookkeeping figure in"
        ' "rationale_text"'
    ) in rendered
