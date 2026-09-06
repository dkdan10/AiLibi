"""Common account vocabulary and independently recorded testimony semantics."""

from __future__ import annotations

from dataclasses import replace
from functools import partial
from typing import Any, Literal

import pytest
from jinja2 import DictLoader, Environment

from agents.strategic.prompts import (
    build_prompt_renderers,
    PromptRenderers,
    public_account_prompt_versions,
    validate_public_account_renderers,
)
from meetings.schemas import MeetingTranscript, MeetingTurn, TaskActivityAccount


def _opening_kwargs() -> dict[str, Any]:
    return dict(
        agent_id="p-1",
        current_tick=8,
        meeting_trigger="Emergency meeting",
        rendered_memory="own memory",
        public_transcript="",
        living_ids=("p-2", "p-3"),
    )


def test_both_roles_receive_exactly_the_same_account_menu() -> None:
    renderers = build_prompt_renderers(
        "qwen3_6_27b", env={}, public_account_version=1, attributed_testimony_version=1
    )
    crew = renderers.crewmate_report(**_opening_kwargs())
    impostor = renderers.impostor_report(**_opening_kwargs())
    start, end = "Public accounts are statements", "Open the meeting"
    assert (
        crew[crew.index(start) : crew.index(end)]
        == impostor[impostor.index(start) : impostor.index(end)]
    )
    for kind in (
        "whereabouts",
        "task_activity",
        "completed_task",
        "saw_player",
        "saw_move",
        "found_body",
        "saw_vent",
        "saw_kill",
        "alibi",
        "accusation",
        "corroboration",
    ):
        assert f'"type":"{kind}"' in crew
    assert "Privately, you are an impostor" not in crew
    assert "Privately, you are an impostor" in impostor
    assert "Keep observations empty" not in impostor


def test_attribution_alone_does_not_enable_the_common_role_menu() -> None:
    renderers = build_prompt_renderers(
        "qwen3_6_27b", env={}, attributed_testimony_version=1
    )
    prompt = renderers.impostor_report(**_opening_kwargs())
    assert "Keep observations empty" in prompt
    assert '"type":"task_activity"' not in prompt
    assert "another player's private memory" in prompt


def test_common_accounts_alone_preserve_certified_vent_explanation() -> None:
    renderers = build_prompt_renderers("qwen3_6_27b", env={}, public_account_version=1)
    assert "certified vent findings remain available" in renderers.impostor_report(
        **_opening_kwargs()
    )


def test_statement_and_ballot_keep_activity_a_named_speakers_claim() -> None:
    renderers = build_prompt_renderers(
        "qwen3_6_27b", env={}, public_account_version=1, attributed_testimony_version=1
    )
    turn = MeetingTurn(
        turn_id="opaque",
        turn_index=0,
        speaker="p-3",
        turn_kind="opening",
        reply_to=None,
        free_text="I worked on fuel.",
        observations=(
            TaskActivityAccount(
                type="task_activity",
                task_id="fuel_reserves",
                room="STORAGE",
                from_tick=3,
                to_tick=5,
            ),
        ),
    )
    transcript = MeetingTranscript(turns=(turn,))
    statement = renderers.statement(
        agent_id="p-1",
        rendered_memory="own memory",
        transcript=transcript,
        contradictions=(),
        prior_turn=turn,
        turn_kind="reply",
    )
    vote = renderers.vote(
        voter_id="p-1",
        rendered_memory="own memory",
        transcript=transcript,
        contradiction_flags=(),
        suspicion_graph=(),
        candidate_targets=("p-2", "p-3"),
        skip_confidence_threshold=0.6,
    )
    for prompt in (statement, vote):
        assert '[turn:opaque:obs:0] p-3 stated {"type":"task_activity"' in prompt
        assert "fuel_reserves" in prompt
        assert "rejection_reason" not in prompt and "owned_task_ids" not in prompt
    assert "Answer the new point in [opaque] by p-3" in statement
    assert "not proof of completed work" in vote


@pytest.mark.parametrize(
    "name",
    [
        "AILIBI_REPORTER_REASONING",
        "AILIBI_TESTIMONY_SHAPES",
        "AILIBI_IMPOSTOR_ROLL_CALL",
        "AILIBI_CORROBORATION_DISCIPLINE",
    ],
)
def test_old_experiment_cannot_silently_overlap_new_templates(name: str) -> None:
    with pytest.raises(ValueError, match="cannot overlap"):
        build_prompt_renderers("qwen3_6_27b", env={name: "1"}, public_account_version=1)


def test_versions_distinguish_each_arm_and_refuse_unsupported_families() -> None:
    common = public_account_prompt_versions("qwen3_6_27b", public_account_version=1)
    attributed = public_account_prompt_versions(
        "qwen3_6_27b", attributed_testimony_version=1
    )
    combined = public_account_prompt_versions(
        "qwen3_6_27b", public_account_version=1, attributed_testimony_version=1
    )
    assert common is not None and attributed is not None and combined is not None
    assert (
        len(set(common.values()) | set(attributed.values()) | set(combined.values()))
        == 12
    )
    assert public_account_prompt_versions("qwen3_6_27b") is None
    with pytest.raises(ValueError, match="require qwen3_6_27b"):
        build_prompt_renderers("qwen3_5_9b", env={}, attributed_testimony_version=1)


def test_explicit_off_preserves_every_default_renderer() -> None:
    before = build_prompt_renderers("qwen3_6_27b", env={})
    after = build_prompt_renderers(
        "qwen3_6_27b",
        env={},
        public_account_version=None,
        attributed_testimony_version=None,
    )
    assert before.crewmate_report(**_opening_kwargs()) == after.crewmate_report(
        **_opening_kwargs()
    )
    assert before.impostor_report(**_opening_kwargs()) == after.impostor_report(
        **_opening_kwargs()
    )
    statement_kwargs: dict[str, Any] = dict(
        agent_id="p-1",
        rendered_memory="own memory",
        transcript=MeetingTranscript(),
        contradictions=(),
        prior_turn=None,
        turn_kind="opt_in",
    )
    vote_kwargs: dict[str, Any] = dict(
        voter_id="p-1",
        rendered_memory="own memory",
        transcript=MeetingTranscript(),
        contradiction_flags=(),
        suspicion_graph=(),
        candidate_targets=("p-2",),
        skip_confidence_threshold=0.6,
    )
    assert before.statement(**statement_kwargs) == after.statement(**statement_kwargs)
    assert before.vote(**vote_kwargs) == after.vote(**vote_kwargs)
    for renderers in (before, after):
        assert "task_activity" not in renderers.crewmate_report(**_opening_kwargs())


def _validate_bundle(
    renderers: PromptRenderers,
    *,
    common: Literal[1] | None = 1,
    attributed: Literal[1] | None = 1,
) -> None:
    validate_public_account_renderers(
        crewmate_report=renderers.crewmate_report,
        impostor_report=renderers.impostor_report,
        statement=renderers.statement,
        vote=renderers.vote,
        prompt_versions=public_account_prompt_versions(
            "qwen3_6_27b",
            public_account_version=common,
            attributed_testimony_version=attributed,
        )
        or {},
        public_account_version=common,
        attributed_testimony_version=attributed,
    )


@pytest.mark.parametrize("common,attributed", [(1, None), (None, 1), (1, 1)])
def test_actual_loader_callables_match_their_independent_profile(
    common: Literal[1] | None,
    attributed: Literal[1] | None,
) -> None:
    _validate_bundle(
        build_prompt_renderers(
            "qwen3_6_27b",
            env={},
            public_account_version=common,
            attributed_testimony_version=attributed,
        ),
        common=common,
        attributed=attributed,
    )


@pytest.mark.parametrize(
    "name", ["crewmate_report", "impostor_report", "statement", "vote"]
)
def test_a_legacy_renderer_cannot_claim_new_profile_through_a_version_label(
    name: str,
) -> None:
    current = build_prompt_renderers(
        "qwen3_6_27b",
        env={},
        public_account_version=1,
        attributed_testimony_version=1,
    )
    old = build_prompt_renderers("qwen3_6_27b", env={})
    with pytest.raises(ValueError, match="binding disagrees"):
        _validate_bundle(replace(current, **{name: getattr(old, name)}))


@pytest.mark.parametrize(
    "mutation", ["profile", "coerced_profile", "template", "environment", "callable"]
)
def test_manual_binding_mutations_cannot_certify_legacy_or_different_bodies(
    mutation: str,
) -> None:
    current = build_prompt_renderers(
        "qwen3_6_27b",
        env={},
        public_account_version=1,
        attributed_testimony_version=1,
    )
    original = current.vote
    assert isinstance(original, partial)
    keywords = dict(original.keywords)
    if mutation == "profile":
        keywords["attributed_testimony_version"] = None
    elif mutation == "coerced_profile":
        keywords["public_account_version"] = True
    elif mutation == "template":
        keywords["template_name"] = "vote_ballot.j2"
    elif mutation == "environment":
        keywords["environment"] = Environment(
            loader=DictLoader(
                {
                    "vote_ballot_accounts.j2": "Legacy output behind a new filename",
                }
            )
        )
    mutated = partial(original.func, **keywords)
    if mutation == "callable":

        def arbitrary(**kwargs: Any) -> str:
            return "Legacy output behind a new version label"

        replacement: Any = arbitrary
    else:
        replacement = mutated
    with pytest.raises(ValueError, match="public account"):
        _validate_bundle(replace(current, vote=replacement))


def test_off_preserves_custom_renderer_extension_point() -> None:
    def custom(**kwargs: Any) -> str:
        return "custom baseline fixture"

    _validate_bundle(
        PromptRenderers(
            crewmate_report=custom,
            impostor_report=custom,
            statement=custom,
            vote=custom,
        ),
        common=None,
        attributed=None,
    )
