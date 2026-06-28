"""Loader-seam tests for the per-model prompt-set restructure (Task 14.2).

The four ``.j2`` templates moved VERBATIM from the flat
``agents/strategic/prompts/`` directory into the per-model
``agents/strategic/prompts/qwen3_5_9b/`` set (owner decision 2026-06-25 —
per-model prompt sets; DESIGN.md §11.4 replay provenance). These tests pin the
seam introduced in :mod:`agents.strategic.prompts.loader`:

* the default set resolves to ``qwen3_5_9b`` (via ``AILIBI_PROMPT_SET``) and the
  process-default wrapper callables render byte-identically to that set;
* a second (empty-stub) set is loadable, proving the directory seam;
* an unknown set fails loud (no silent fallback, AGENTS.md);
* the per-set version registry (:data:`orchestrator.game.PROMPT_VERSION_SETS`)
  keeps the 9B set's recorded ``prompt_versions`` byte-identical.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agents.strategic.prompts import (
    DEFAULT_PROMPT_SET,
    ENV_PROMPT_SET,
    build_environment,
    crewmate_report_prompt,
    resolve_prompt_set,
)
from agents.strategic.prompts.loader import (
    ACCUSATION_ROUND_TEMPLATE,
    CREWMATE_REPORT_TEMPLATE,
    IMPOSTOR_REPORT_TEMPLATE,
    VOTE_BALLOT_TEMPLATE,
    _ENV,  # noqa: PLC2701
)
from orchestrator.game import (
    DEFAULT_PROMPT_VERSIONS,
    PROMPT_VERSION_SETS,
    prompt_versions_for_set,
)

_TEMPLATE_NAMES = (
    CREWMATE_REPORT_TEMPLATE,
    IMPOSTOR_REPORT_TEMPLATE,
    ACCUSATION_ROUND_TEMPLATE,
    VOTE_BALLOT_TEMPLATE,
)


class TestResolvePromptSet:
    def test_default_is_qwen3_5_9b_when_env_unset(self) -> None:
        assert resolve_prompt_set(env={}) == "qwen3_5_9b"
        assert DEFAULT_PROMPT_SET == "qwen3_5_9b"

    def test_blank_env_value_falls_back_to_default(self) -> None:
        # An empty / whitespace-only value is treated as unset, not as a set
        # literally named "" (which would fail loud downstream).
        assert resolve_prompt_set(env={ENV_PROMPT_SET: "   "}) == "qwen3_5_9b"

    def test_env_value_selects_named_set(self) -> None:
        assert resolve_prompt_set(env={ENV_PROMPT_SET: "some_model"}) == "some_model"

    def test_explicit_argument_wins_over_env(self) -> None:
        assert (
            resolve_prompt_set("explicit", env={ENV_PROMPT_SET: "ignored"})
            == "explicit"
        )


class TestDefaultSetRendersByteIdentically:
    def test_template_sources_match_committed_qwen_files(self) -> None:
        # The process-default environment (_ENV, bound at import) must read the
        # exact bytes committed under qwen3_5_9b/ -- a content-preserving move.
        set_dir = (
            Path(__file__).resolve().parents[2]
            / "agents"
            / "strategic"
            / "prompts"
            / "qwen3_5_9b"
        )
        for name in _TEMPLATE_NAMES:
            source, _, _ = _ENV.loader.get_source(_ENV, name)  # type: ignore[union-attr]
            assert source == (set_dir / name).read_text(encoding="utf-8")

    def test_default_render_equals_explicit_qwen_set_render(self) -> None:
        # Rendering through the default wrapper (which uses _ENV) is byte-for-byte
        # identical to rendering through an environment built explicitly for the
        # 9B set: the default resolves to qwen3_5_9b.
        kwargs = dict(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="body_report",
            rendered_memory="## Memory\n- saw p-2 in cafeteria",
            public_transcript="",
            living_ids=("p-1", "p-5"),
            dead_ids=("p-2",),
        )
        via_wrapper = crewmate_report_prompt(**kwargs)  # type: ignore[arg-type]
        qwen_env = build_environment("qwen3_5_9b")
        via_explicit = qwen_env.get_template(CREWMATE_REPORT_TEMPLATE).render(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="body_report",
            rendered_memory="## Memory\n- saw p-2 in cafeteria",
            public_transcript="",
            living_ids=("p-1", "p-5"),
            dead_ids=("p-2",),
        )
        assert via_wrapper == via_explicit
        assert via_wrapper  # non-empty

    def test_default_env_is_strict_undefined_set(self) -> None:
        # build_environment() with no argument resolves the active set (default
        # 9B) and carries the same strict-undefined policy as _ENV.
        env = build_environment()
        assert env.undefined is _ENV.undefined
        assert env.autoescape is False
        assert env.trim_blocks is True
        assert env.lstrip_blocks is True


class TestSecondSetLoads:
    def test_empty_stub_set_is_loadable(self, tmp_path: Path) -> None:
        # The seam: an environment can be built against a second set directory.
        # An empty stub set proves the loader resolves arbitrary sets by subdir
        # without requiring the four templates to exist yet (14.5 authors them).
        stub_dir = tmp_path / "stub_model"
        stub_dir.mkdir()
        env = build_environment("stub_model", root=tmp_path)
        assert env.undefined is _ENV.undefined

    def test_second_set_renders_its_own_template(self, tmp_path: Path) -> None:
        stub_dir = tmp_path / "stub_model"
        stub_dir.mkdir()
        (stub_dir / CREWMATE_REPORT_TEMPLATE).write_text(
            "stub crewmate report for {{ agent_id }}", encoding="utf-8"
        )
        env = build_environment("stub_model", root=tmp_path)
        rendered = env.get_template(CREWMATE_REPORT_TEMPLATE).render(agent_id="p-7")
        assert rendered == "stub crewmate report for p-7"


class TestUnknownSetFailsLoud:
    def test_build_environment_raises_for_missing_set(self) -> None:
        with pytest.raises(ValueError, match="Unknown prompt set 'no_such_set'"):
            build_environment("no_such_set")

    def test_build_environment_raises_for_missing_subdir_under_root(
        self, tmp_path: Path
    ) -> None:
        with pytest.raises(ValueError, match="Unknown prompt set 'ghost'"):
            build_environment("ghost", root=tmp_path)

    def test_prompt_versions_for_set_raises_for_unregistered_set(self) -> None:
        with pytest.raises(ValueError, match="Unknown prompt set 'no_such_set'"):
            prompt_versions_for_set("no_such_set")


class TestPerSetVersionRegistry:
    def test_qwen_set_is_default_prompt_versions_byte_identical(self) -> None:
        # The 9B set keeps the EXACT recorded mapping (same object identity), so
        # the committed replays + the prompt_versions assertions in
        # tests/orchestrator/ + tests/scripts/ stay green with no edits.
        assert PROMPT_VERSION_SETS["qwen3_5_9b"] is DEFAULT_PROMPT_VERSIONS
        assert dict(PROMPT_VERSION_SETS["qwen3_5_9b"]) == {
            "crewmate_report": "crewmate_report.v8",
            "impostor_report": "impostor_report_v6",
            "accusation_round": "accusation_round.v9",
            "vote_ballot": "vote_ballot/v7",
        }

    def test_default_lookup_returns_qwen_versions(self) -> None:
        assert prompt_versions_for_set(env={}) is DEFAULT_PROMPT_VERSIONS
        assert prompt_versions_for_set("qwen3_5_9b") is DEFAULT_PROMPT_VERSIONS
