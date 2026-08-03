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

Task 19.6 adds :class:`TestBareEnvironmentFallbackIsLoud`: the default VALUE
still resolves to ``qwen3_5_9b`` (byte-identity is the whole point of the owner
decision), but taking it with no ``AILIBI_PROMPT_SET`` override now emits a
one-line stderr notice naming the variable and the operational baseline set.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agents.strategic.prompts import (
    DEFAULT_PROMPT_SET,
    ENV_PROMPT_SET,
    build_environment,
    build_prompt_renderers,
    crewmate_report_prompt,
    resolve_prompt_set,
)
from agents.strategic.prompts.loader import (
    ACCUSATION_ROUND_TEMPLATE,
    CREWMATE_REPORT_TEMPLATE,
    IMPOSTOR_REPORT_TEMPLATE,
    OPERATIONAL_BASELINE_PROMPT_SET,
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


class TestBareEnvironmentFallbackIsLoud:
    """Task 19.6: the bare-environment fallback emits a one-line stderr notice.

    The default VALUE is unchanged and must stay unchanged — moving it would
    move committed prompt bytes (the byte-golden suite proves those stand).
    What changes is the silence: a bare shell used to take the frozen 9B set
    with no signal at all, two generations behind the
    :data:`OPERATIONAL_BASELINE_PROMPT_SET` every report's recording env names.
    The notice fires on exactly one path — no explicit argument AND no
    ``AILIBI_PROMPT_SET`` override.
    """

    def test_fallback_emits_the_notice_on_stderr(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert resolve_prompt_set(env={}) == DEFAULT_PROMPT_SET
        captured = capsys.readouterr()
        assert ENV_PROMPT_SET in captured.err
        assert OPERATIONAL_BASELINE_PROMPT_SET in captured.err
        assert DEFAULT_PROMPT_SET in captured.err
        # stdout stays clean: CLI surfaces emit machine-readable JSON there.
        assert captured.out == ""

    def test_notice_is_exactly_one_line(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        resolve_prompt_set(env={})
        assert len(capsys.readouterr().err.strip().splitlines()) == 1

    def test_blank_env_value_also_notifies(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Whitespace-only is "absent" for the fallback, so it is "absent" for
        # the notice too -- the two must not disagree.
        assert resolve_prompt_set(env={ENV_PROMPT_SET: "   "}) == DEFAULT_PROMPT_SET
        assert ENV_PROMPT_SET in capsys.readouterr().err

    def test_env_override_is_silent(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert (
            resolve_prompt_set(env={ENV_PROMPT_SET: OPERATIONAL_BASELINE_PROMPT_SET})
            == OPERATIONAL_BASELINE_PROMPT_SET
        )
        assert capsys.readouterr().err == ""

    def test_env_override_naming_the_default_set_is_silent(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Choosing the 9B set deliberately is a choice, not a fallback.
        assert (
            resolve_prompt_set(env={ENV_PROMPT_SET: DEFAULT_PROMPT_SET})
            == DEFAULT_PROMPT_SET
        )
        assert capsys.readouterr().err == ""

    def test_explicit_argument_is_silent(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # A caller pinning its own set (build_prompt_renderers, the runner's
        # one-resolution binding) has not fallen back to anything.
        assert resolve_prompt_set(DEFAULT_PROMPT_SET, env={}) == DEFAULT_PROMPT_SET
        assert capsys.readouterr().err == ""

    def test_operational_baseline_names_a_real_set(self) -> None:
        # A notice pointing at a set that does not exist would be worse than
        # silence: the suggested export would fail loud in build_environment.
        assert OPERATIONAL_BASELINE_PROMPT_SET != DEFAULT_PROMPT_SET
        set_dir = (
            Path(__file__).resolve().parents[2]
            / "agents"
            / "strategic"
            / "prompts"
            / OPERATIONAL_BASELINE_PROMPT_SET
        )
        assert set_dir.is_dir()
        build_environment(OPERATIONAL_BASELINE_PROMPT_SET)


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


class TestBuildPromptRenderersBindsToOneSet:
    def test_renderers_render_the_qwen_set_for_default(self) -> None:
        # build_prompt_renderers(default) renders byte-identically to the module
        # wrapper for the 9B set -- the production binding path is unchanged for
        # the default set (no re-record).
        renderers = build_prompt_renderers("qwen3_5_9b")
        kwargs = dict(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="body_report",
            rendered_memory="## Memory\n- saw p-2 in cafeteria",
            public_transcript="",
            living_ids=("p-1", "p-5"),
            dead_ids=("p-2",),
        )
        assert renderers.crewmate_report(**kwargs) == crewmate_report_prompt(  # type: ignore[arg-type]
            **kwargs  # type: ignore[arg-type]
        )

    def test_renderers_bind_to_resolved_set_independent_of_process_env(
        self, tmp_path: Path
    ) -> None:
        # The provenance fix (PR #203 review): renderers are bound to the set
        # passed at construction, NOT the import-time _ENV / current env var. A
        # second stub set renders its OWN template even though the module default
        # is qwen3_5_9b.
        for name, marker in (("set_a", "ALPHA"), ("set_b", "BRAVO")):
            set_dir = tmp_path / name
            set_dir.mkdir()
            (set_dir / CREWMATE_REPORT_TEMPLATE).write_text(
                f"{marker} {{{{ agent_id }}}}", encoding="utf-8"
            )
        renderers_a = build_prompt_renderers("set_a", root=tmp_path)
        renderers_b = build_prompt_renderers("set_b", root=tmp_path)
        # The stub template only references agent_id; the wrapper still requires
        # its full kwarg set (render ignores the unused ones).
        common = dict(
            agent_id="p-1",
            current_tick=0,
            meeting_trigger="t",
            rendered_memory="",
            public_transcript="",
        )
        assert renderers_a.crewmate_report(**common) == "ALPHA p-1"  # type: ignore[arg-type]
        assert renderers_b.crewmate_report(**common) == "BRAVO p-1"  # type: ignore[arg-type]

    def test_unknown_set_raises_via_factory(self) -> None:
        with pytest.raises(ValueError, match="Unknown prompt set 'no_such_set'"):
            build_prompt_renderers("no_such_set")


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
