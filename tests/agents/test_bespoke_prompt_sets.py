"""Validation for the Task 14.5 bespoke per-candidate prompt sets.

Five bespoke sets are authored from the ground up — one per candidate
(model, mode) — under ``agents/strategic/prompts/<set>/`` (owner decision
2026-06-30). The ONE hard invariant is the OUTPUT JSON schema: every set's turns
must emit the SAME :class:`~meetings.schemas.MeetingTurn` / :class:`VoteBallot`
shape so all sets parse identically and the graders / recording seam are
unchanged. These tests pin that contract OFFLINE (no LLM, no network):

* every template of every set renders under :class:`jinja2.StrictUndefined` with
  the exact loader kwargs over a reconstructed context (the render smoke test);
* a canonical ``MeetingTurn`` / ``VoteBallot`` parses against the shared schema
  regardless of which set produced it (the cross-set parse check);
* the cover-consistency directive is wired into the REPLY path gated on
  ``is_impostor`` ALONE (present on an impostor reply with
  ``is_body_report=False``; absent on a crewmate reply) — the gp-1 fix the 14.4
  sweep flagged (experiments/lab/report-featherless-sweep.md);
* each set is registered in the per-set version registry with the four shared
  keys + its own namespaced values, and is selectable via ``AILIBI_PROMPT_SET``.
"""

from __future__ import annotations

import pytest

from agents.strategic.prompts.loader import (
    DEFAULT_PROMPT_SET,
    build_prompt_renderers,
    resolve_prompt_set,
)
from meetings.manager import SuspicionEntry
from meetings.schemas import (
    AccusationClaim,
    ContradictionRef,
    FoundBodyObservation,
    MeetingTranscript,
    MeetingTurn,
    SawPlayerObservation,
    VoteBallot,
)
from orchestrator.game import (
    DEFAULT_PROMPT_VERSIONS,
    PROMPT_VERSION_SETS,
    prompt_versions_for_set,
)

# The five Task 14.5 bespoke sets (each a candidate model/mode).
BESPOKE_SETS = (
    "qwen3_32b",
    "qwen3_32b_thinking",
    "qwen3_30b_a3b",
    "glm_4_32b",
    "cydonia_24b",
)

# A small reconstructed body-report meeting context (a found body + an accusation
# chain) — enough to exercise every branch of every template.
_OPENING = MeetingTurn(
    turn_id="m-1:turn-0",
    turn_index=0,
    speaker="p-2",
    turn_kind="opening",
    reply_to=None,
    observations=(
        FoundBodyObservation(
            type="found_body", tick=410, body_of="p-7", room="electrical"
        ),
    ),
    claims=(
        AccusationClaim(
            type="accusation", against="p-3", confidence=0.7, reason="near body"
        ),
    ),
    free_text="Found p-7 in electrical; p-3 was nearby.",
)
_PRIOR = MeetingTurn(
    turn_id="m-1:turn-1",
    turn_index=1,
    speaker="p-4",
    turn_kind="reply",
    reply_to="m-1:turn-0",
    observations=(
        SawPlayerObservation(
            type="saw_player",
            tick=405,
            subject="p-3",
            room="electrical",
            co_present=("p-5",),
        ),
    ),
    claims=(
        AccusationClaim(
            type="accusation", against="p-3", confidence=0.8, reason="seen there"
        ),
    ),
    free_text="p-3 was in electrical at 405.",
)
_TRANSCRIPT = MeetingTranscript(turns=(_OPENING, _PRIOR))
_CONTRAS = (
    ContradictionRef(
        contradiction_id="c-1",
        kind="alibi_vs_sighting",
        event_a_id="e-a",
        event_b_id="e-b",
        subjects=("p-3",),
        description="p-3's alibi conflicts with a sighting",
    ),
)
_SUSP = (
    SuspicionEntry(player_id="p-3", suspicion=0.8, trust=0.5),
    SuspicionEntry(player_id="p-5", suspicion=0.3, trust=0.5),
)
_MEMORY = "## Your role\nIMPOSTOR\n## Observations\n- tick 405: saw p-3 in electrical with p-5\n"

# All sets word the wired reply cover directive around "the body's room".
_COVER_MARKER = "body's room"


def _render_all(set_name: str) -> dict[str, str]:
    """Render every template of ``set_name`` over the reconstructed context."""

    r = build_prompt_renderers(set_name)
    out: dict[str, str] = {}
    for trig in (
        "p-2 reported body of p-7 at tick 410",
        "p-2 called an emergency meeting at tick 410",
    ):
        tag = "body" if "reported" in trig else "emergency"
        out[f"crewmate_report/{tag}"] = r.crewmate_report(
            agent_id="p-2",
            current_tick=410,
            meeting_trigger=trig,
            rendered_memory=_MEMORY,
            public_transcript="",
            living_ids=("p-3", "p-5"),
            dead_ids=("p-7",),
        )
        out[f"impostor_report/{tag}"] = r.impostor_report(
            agent_id="p-3",
            current_tick=410,
            meeting_trigger=trig,
            rendered_memory=_MEMORY,
            public_transcript="",
            fellow_impostor_ids=("p-9",),
            living_ids=("p-2", "p-5"),
            dead_ids=("p-7",),
        )
    for is_imp in (True, False):
        for is_body in (True, False):
            out[f"reply/imp={is_imp}/body={is_body}"] = r.statement(
                agent_id="p-3",
                rendered_memory=_MEMORY,
                transcript=_TRANSCRIPT,
                contradictions=_CONTRAS,
                prior_turn=_PRIOR,
                turn_kind="reply",
                fellow_impostor_ids=(("p-9",) if is_imp else ()),
                living_ids=("p-2", "p-5"),
                dead_ids=("p-7",),
                is_impostor=is_imp,
                is_body_report=is_body,
            )
    out["opt_in"] = r.statement(
        agent_id="p-3",
        rendered_memory=_MEMORY,
        transcript=_TRANSCRIPT,
        contradictions=(),
        prior_turn=None,
        turn_kind="opt_in",
        fellow_impostor_ids=(),
        living_ids=("p-2", "p-5"),
        dead_ids=(),
        is_impostor=False,
        is_body_report=False,
    )
    out["vote"] = r.vote(
        voter_id="p-2",
        rendered_memory=_MEMORY,
        transcript=_TRANSCRIPT,
        contradiction_flags=_CONTRAS,
        suspicion_graph=_SUSP,
        candidate_targets=("p-3", "p-5"),
        skip_confidence_threshold=0.6,
        fellow_impostor_ids=(),
    )
    return out


@pytest.mark.parametrize("set_name", BESPOKE_SETS)
class TestBespokeSetRenders:
    def test_every_template_renders_non_empty_under_strict_undefined(
        self, set_name: str
    ) -> None:
        # StrictUndefined raises on a missing / typo'd kwarg, so a clean render of
        # every branch proves no template kwarg drift (the sweep's abort risk).
        for label, text in _render_all(set_name).items():
            assert text.strip(), f"{set_name}: {label} rendered empty"

    def test_vote_renders_eval_suspicion_parse_line(self, set_name: str) -> None:
        # The recorded-ballot analyzer (eval._suspicion_parse) reads this exact
        # wording; keep it stable across every set for a future re-record.
        vote = _render_all(set_name)["vote"]
        assert "maximum suspicion among the living ejection targets is" in vote

    def test_cover_directive_wired_into_reply_path_gated_on_is_impostor(
        self, set_name: str
    ) -> None:
        rendered = _render_all(set_name)
        # Wired into the REPLY path gated on is_impostor ALONE: present even with
        # is_body_report=False (not gated off the body-report opening as 9B is).
        assert _COVER_MARKER in rendered["reply/imp=True/body=False"].lower()
        # Absent from a crewmate reply (is_impostor=False), even body=True.
        assert _COVER_MARKER not in rendered["reply/imp=False/body=True"].lower()


def test_cross_set_parse_invariant_is_shared() -> None:
    # The one hard invariant: a canonical MeetingTurn / VoteBallot parses against
    # the shared schema regardless of which set produced it. The set only changes
    # the instruction prose; model_validate_json + the recording seam are
    # set-independent, which is the precondition for later heterogeneous play.
    turn = MeetingTurn.model_validate_json(_OPENING.model_dump_json())
    assert turn == _OPENING
    ballot = VoteBallot(
        voter="p-2",
        target="p-3",
        confidence=0.7,
        primary_reason_id="m-1:turn-0",
        considered_alternatives=("p-5",),
        rationale_text="p-3 near body",
    )
    assert VoteBallot.model_validate_json(ballot.model_dump_json()) == ballot


@pytest.mark.parametrize("set_name", BESPOKE_SETS)
class TestBespokeSetRegistration:
    def test_selectable_via_env(self, set_name: str) -> None:
        assert resolve_prompt_set(env={"AILIBI_PROMPT_SET": set_name}) == set_name
        # The renderers build (the set directory exists and is loadable).
        assert build_prompt_renderers(set_name) is not None

    def test_version_registry_has_shared_keys_and_own_values(
        self, set_name: str
    ) -> None:
        versions = prompt_versions_for_set(set_name)
        # Same FOUR keys as the 9B default (the recording seam is set-independent).
        assert set(versions) == set(DEFAULT_PROMPT_VERSIONS)
        # Own namespaced values, distinct from the pinned 9B set.
        assert versions != DEFAULT_PROMPT_VERSIONS
        for key, value in versions.items():
            assert set_name in value, f"{set_name}: {key} version not namespaced"

    def test_registered_set_is_not_the_default(self, set_name: str) -> None:
        assert set_name in PROMPT_VERSION_SETS
        assert set_name != DEFAULT_PROMPT_SET
