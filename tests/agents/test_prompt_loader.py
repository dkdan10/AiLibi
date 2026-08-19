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

The bare-environment notice is pinned by three classes. The default VALUE still
resolves to ``qwen3_5_9b`` (byte-identity is the whole point of the owner
decision), and taking it with no ``AILIBI_PROMPT_SET`` override emits a
one-line stderr notice naming the variable and the operational baseline set —
but only where that line describes a real risk:
:class:`TestBareEnvironmentFallbackIsLoud` pins the notice under a real
provider, :class:`TestNoticeIsProviderGated` pins the silence under the fake
one (and the two gates' agreement with ``llm.provider``'s own selector over the
env grid), and :class:`TestNoticeIsOncePerProcess` pins the de-duplication.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from functools import partial
from pathlib import Path
from typing import cast

import pytest
from jinja2 import Environment, FileSystemLoader

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
    ENV_IMPOSTOR_ROLL_CALL,
    IMPOSTOR_REPORT_TEMPLATE,
    OPERATIONAL_BASELINE_PROMPT_SET,
    VOTE_BALLOT_TEMPLATE,
    PromptRenderers,
    _ENV,  # noqa: PLC2701
    _notify_bare_prompt_set_fallback,  # noqa: PLC2701
)
from llm.fake_provider import FakeProvider
from llm.provider import (
    ENV_ANTHROPIC_API_KEY,
    ENV_FEATHERLESS_API_KEY,
    ENV_PROVIDER,
    PROVIDER_ANTHROPIC,
    PROVIDER_FAKE,
    PROVIDER_FEATHERLESS,
    PROVIDER_OLLAMA,
    build_default_client,
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

# The notice fires only under a real provider, so every assertion that expects
# it resolves through one. Featherless is the canonical eval provider (AGENTS.md
# §"Environment setup"); no client is ever constructed from this mapping, so no
# credential is needed and nothing reaches the network.
_REAL_PROVIDER_ENV = {ENV_PROVIDER: PROVIDER_FEATHERLESS}

# The provider grid the loader's gate and ``llm.provider``'s selector must agree
# on, each row (label, env mapping, expected silence). Credentials are supplied
# for the two key-checked providers so the selector reaches its branch instead
# of raising on a missing key; the constructors it then runs are pure.
_PROVIDER_GRID: tuple[tuple[str, dict[str, str], bool], ...] = (
    ("unset", {}, True),
    ("fake", {ENV_PROVIDER: PROVIDER_FAKE}, True),
    ("FAKE", {ENV_PROVIDER: "FAKE"}, True),
    ("padded fake", {ENV_PROVIDER: " fake "}, True),
    ("empty", {ENV_PROVIDER: ""}, False),
    (
        "anthropic",
        {ENV_PROVIDER: PROVIDER_ANTHROPIC, ENV_ANTHROPIC_API_KEY: "test-key"},
        False,
    ),
    ("ollama", {ENV_PROVIDER: PROVIDER_OLLAMA}, False),
    (
        "featherless",
        {ENV_PROVIDER: PROVIDER_FEATHERLESS, ENV_FEATHERLESS_API_KEY: "test-key"},
        False,
    ),
)


@pytest.fixture(autouse=True)
def _reset_bare_fallback_notice() -> Iterator[None]:
    """Clear the loader's once-per-process notice memo around every test here.

    The memo is process-wide and lives longer than any test: importing the
    loader builds ``_ENV``, which resolves the prompt set, so in a shell that
    exports a real provider the one allowed emission is already spent before
    collection starts. Without this reset the notice assertions below would
    observe silence and pass for the wrong reason — and would depend on
    collection order among themselves. Clearing on the way out too keeps this
    file from handing a primed memo to the rest of the suite.
    """

    _notify_bare_prompt_set_fallback.cache_clear()
    yield
    _notify_bare_prompt_set_fallback.cache_clear()


def _selector_picks_the_fake(env: Mapping[str, str]) -> bool:
    """Whether :func:`llm.provider.build_default_client` takes its fake branch.

    A raise — an unrecognized provider value, a missing credential — is
    decisively NOT the fake branch, so it answers ``False`` rather than
    propagating: the question the grid asks is which branch the selector picks,
    not whether the picked client could be constructed.
    """

    try:
        return isinstance(build_default_client(env=dict(env)), FakeProvider)
    except ValueError:
        return False


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
    """Under a real provider the bare fallback emits a one-line stderr notice.

    The default VALUE is unchanged and must stay unchanged — moving it would
    move committed prompt bytes (the byte-golden suite proves those stand).
    What the notice buys is the signal: a real-provider shell taking the frozen
    9B set is sending a prompt family two generations behind the
    :data:`OPERATIONAL_BASELINE_PROMPT_SET` every report's recording env names.
    It fires on exactly one path — a real provider AND no explicit argument AND
    no ``AILIBI_PROMPT_SET`` override — so every case here resolves through
    :data:`_REAL_PROVIDER_ENV`; the fake-provider silence is
    :class:`TestNoticeIsProviderGated`'s subject.
    """

    def test_fallback_emits_the_notice_on_stderr(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert resolve_prompt_set(env=_REAL_PROVIDER_ENV) == DEFAULT_PROMPT_SET
        captured = capsys.readouterr()
        assert ENV_PROMPT_SET in captured.err
        assert OPERATIONAL_BASELINE_PROMPT_SET in captured.err
        assert DEFAULT_PROMPT_SET in captured.err
        # stdout stays clean: CLI surfaces emit machine-readable JSON there.
        assert captured.out == ""

    def test_notice_is_exactly_one_line(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        resolve_prompt_set(env=_REAL_PROVIDER_ENV)
        assert len(capsys.readouterr().err.strip().splitlines()) == 1

    def test_blank_env_value_also_notifies(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Whitespace-only is "absent" for the fallback, so it is "absent" for
        # the notice too -- the two must not disagree.
        env = {**_REAL_PROVIDER_ENV, ENV_PROMPT_SET: "   "}
        assert resolve_prompt_set(env=env) == DEFAULT_PROMPT_SET
        assert ENV_PROMPT_SET in capsys.readouterr().err

    def test_env_override_is_silent(self, capsys: pytest.CaptureFixture[str]) -> None:
        env = {**_REAL_PROVIDER_ENV, ENV_PROMPT_SET: OPERATIONAL_BASELINE_PROMPT_SET}
        assert resolve_prompt_set(env=env) == OPERATIONAL_BASELINE_PROMPT_SET
        assert capsys.readouterr().err == ""

    def test_env_override_naming_the_default_set_is_silent(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Choosing the 9B set deliberately is a choice, not a fallback.
        env = {**_REAL_PROVIDER_ENV, ENV_PROMPT_SET: DEFAULT_PROMPT_SET}
        assert resolve_prompt_set(env=env) == DEFAULT_PROMPT_SET
        assert capsys.readouterr().err == ""

    def test_explicit_argument_is_silent(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # A caller pinning its own set (build_prompt_renderers, the runner's
        # one-resolution binding) has not fallen back to anything.
        resolved = resolve_prompt_set(DEFAULT_PROMPT_SET, env=_REAL_PROVIDER_ENV)
        assert resolved == DEFAULT_PROMPT_SET
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


class TestNoticeIsProviderGated:
    """The notice fires under a real provider and nowhere else.

    The notice's claim is that the rendered prompt family is two model
    generations behind the baseline one; the fake provider runs no model, so
    under it the sentence has nothing to be about. (Its placeholder strings ARE
    prompt-seeded, so the family does move the fake's bytes — but only where a
    set was deliberately selected, and the notice fires solely where the
    DEFAULT was taken, which is the configuration the committed goldens
    reproduce.) That path is also every CI run and every first run of the
    front-door commands, which is why the gate is worth having. The gate must
    agree with the selector it mirrors:
    :data:`_PROVIDER_GRID` pins loader silence against
    :func:`llm.provider.build_default_client`'s own branch choice, value for
    value.
    """

    def test_unset_provider_is_silent(self, capsys: pytest.CaptureFixture[str]) -> None:
        # The front door: a bare shell resolves the fake and says nothing.
        assert resolve_prompt_set(env={}) == DEFAULT_PROMPT_SET
        assert capsys.readouterr().err == ""

    def test_explicit_fake_provider_is_silent(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        env = {ENV_PROVIDER: PROVIDER_FAKE}
        assert resolve_prompt_set(env=env) == DEFAULT_PROMPT_SET
        assert capsys.readouterr().err == ""

    @pytest.mark.parametrize(
        "provider", [PROVIDER_ANTHROPIC, PROVIDER_OLLAMA, PROVIDER_FEATHERLESS]
    )
    def test_each_real_provider_still_notifies(
        self, provider: str, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert resolve_prompt_set(env={ENV_PROVIDER: provider}) == DEFAULT_PROMPT_SET
        assert len(capsys.readouterr().err.strip().splitlines()) == 1

    @pytest.mark.parametrize(("label", "env", "expected_silent"), _PROVIDER_GRID)
    def test_gate_agrees_with_the_client_selector(
        self,
        label: str,
        env: Mapping[str, str],
        expected_silent: bool,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        # Two readings of one variable that must never diverge: the loader's
        # "is this the fake?" and the selector's "which client do I build?".
        # ``" fake "`` and ``"FAKE"`` are the fake (both strip/lower to it);
        # ``""`` is not (it raises in the selector), so the loader is loud.
        assert resolve_prompt_set(env=env) == DEFAULT_PROMPT_SET
        silent = capsys.readouterr().err == ""
        assert silent is expected_silent, label
        assert silent is _selector_picks_the_fake(env), label

    def test_the_equivalence_catches_a_drifting_gate(self) -> None:
        # The perturbation the grid exists to catch: a hand-rolled gate that
        # skips .strip().lower() -- the drift a copied string literal invites,
        # and the reason the loader imports PROVIDER_FAKE instead. It reads
        # " fake " and "FAKE" as real providers, disagreeing with the selector
        # on exactly the rows the real gate agrees on.
        def drifted_gate_is_silent(env: Mapping[str, str]) -> bool:
            return env.get(ENV_PROVIDER, PROVIDER_FAKE) == PROVIDER_FAKE

        disagreements = [
            label
            for label, env, _ in _PROVIDER_GRID
            if drifted_gate_is_silent(env) is not _selector_picks_the_fake(env)
        ]
        assert disagreements == ["FAKE", "padded fake"]

    def test_provider_is_read_from_the_passed_mapping(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # The mapping is authoritative in BOTH directions: a caller passing
        # env= is never second-guessed against the ambient shell (which the
        # suite's conftest pins to the fake provider).
        monkeypatch.setenv(ENV_PROVIDER, PROVIDER_FEATHERLESS)
        assert resolve_prompt_set(env={ENV_PROVIDER: PROVIDER_FAKE}) == (
            DEFAULT_PROMPT_SET
        )
        assert capsys.readouterr().err == ""
        monkeypatch.setenv(ENV_PROVIDER, PROVIDER_FAKE)
        assert resolve_prompt_set(env=_REAL_PROVIDER_ENV) == DEFAULT_PROMPT_SET
        assert capsys.readouterr().err != ""

    def test_no_mapping_reads_the_process_environment(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # The production path (build_default_meeting_runner calls it bare):
        # with no mapping the provider comes from os.environ, same as the set.
        monkeypatch.delenv(ENV_PROMPT_SET, raising=False)
        monkeypatch.setenv(ENV_PROVIDER, PROVIDER_FEATHERLESS)
        assert resolve_prompt_set() == DEFAULT_PROMPT_SET
        assert len(capsys.readouterr().err.strip().splitlines()) == 1
        monkeypatch.setenv(ENV_PROVIDER, PROVIDER_FAKE)
        _notify_bare_prompt_set_fallback.cache_clear()
        assert resolve_prompt_set() == DEFAULT_PROMPT_SET
        assert capsys.readouterr().err == ""


class TestNoticeIsOncePerProcess:
    """The real-provider notice prints once per process, not once per game.

    The resolution points are per-process and per-runner — the import-time
    ``_ENV``, ``build_prompt_renderers``, and one per
    ``orchestrator.game.build_default_meeting_runner`` — so a five-game
    tournament printed the same line six times. Once is the message; six times
    is noise. The de-duplication is a memo, not a mute: clearing it re-arms the
    notice, which is what the autouse fixture above does around every test in
    this file.
    """

    def test_three_resolutions_emit_one_line(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        for _ in range(3):
            assert resolve_prompt_set(env=_REAL_PROVIDER_ENV) == DEFAULT_PROMPT_SET
        assert len(capsys.readouterr().err.strip().splitlines()) == 1

    def test_switching_real_providers_does_not_repeat_it(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # "Once per process" means once, full stop -- the memo is keyed on the
        # resolved SET, not the provider, so a process that resolves under
        # three different real providers still gets one line. The notice says
        # nothing about the provider, so a second copy would be noise.
        for provider in (PROVIDER_FEATHERLESS, PROVIDER_OLLAMA, PROVIDER_ANTHROPIC):
            assert resolve_prompt_set(env={ENV_PROVIDER: provider}) == (
                DEFAULT_PROMPT_SET
            )
        assert len(capsys.readouterr().err.strip().splitlines()) == 1

    def test_the_first_resolution_still_emits(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # The half of "at most once" that can regress into silence: a memo
        # primed at import (or a gate that swallowed everything) would make the
        # count above 0 rather than 1, and this is the test that would fail.
        resolve_prompt_set(env=_REAL_PROVIDER_ENV)
        assert len(capsys.readouterr().err.strip().splitlines()) == 1

    def test_clearing_the_memo_re_arms_the_notice(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # The perturbation proving the suppression is a memo and the fixture's
        # reset really resets: without the clear the second resolution is
        # silent, with it the line comes back.
        resolve_prompt_set(env=_REAL_PROVIDER_ENV)
        capsys.readouterr()
        resolve_prompt_set(env=_REAL_PROVIDER_ENV)
        assert capsys.readouterr().err == ""
        _notify_bare_prompt_set_fallback.cache_clear()
        resolve_prompt_set(env=_REAL_PROVIDER_ENV)
        assert len(capsys.readouterr().err.strip().splitlines()) == 1

    def test_a_fake_resolution_does_not_consume_the_one_emission(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Gate first, dedupe second: the silent fake path must record nothing,
        # or a process that resolves under the fake before switching to a real
        # provider (a tournament script, a notebook) would lose its one line.
        assert resolve_prompt_set(env={}) == DEFAULT_PROMPT_SET
        assert capsys.readouterr().err == ""
        assert resolve_prompt_set(env=_REAL_PROVIDER_ENV) == DEFAULT_PROMPT_SET
        assert len(capsys.readouterr().err.strip().splitlines()) == 1


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


def _set_directory(environment: Environment) -> Path:
    """The template directory an environment is bound to."""

    loader = environment.loader
    assert isinstance(loader, FileSystemLoader)
    return Path(loader.searchpath[0])


def _bundle_environment(renderers: PromptRenderers) -> Environment:
    """The environment a :class:`PromptRenderers` bundle bound its wrappers to."""

    bound = cast("partial[str]", renderers.vote)
    environment = bound.keywords["environment"]
    assert isinstance(environment, Environment)
    return environment


class TestEnvironmentIsMemoizedPerSetAndRoot:
    """One environment per (resolved set, templates root), shared by every caller.

    An environment holds a set's template bytes and their compiled code and
    nothing per-game, so building one per meeting runner re-lexed and
    re-compiled the same templates once a game. These pin the memo's key — the
    set and the root, and only those — and the identity every caller now shares.
    """

    def test_two_calls_for_one_set_return_the_same_object(self) -> None:
        assert build_environment(DEFAULT_PROMPT_SET) is build_environment(
            DEFAULT_PROMPT_SET
        )

    def test_a_different_set_returns_its_own_environment(self) -> None:
        default_env = build_environment(DEFAULT_PROMPT_SET)
        baseline_env = build_environment(OPERATIONAL_BASELINE_PROMPT_SET)
        assert default_env is not baseline_env
        # Not merely different objects: each is bound to its OWN set directory.
        assert _set_directory(default_env).name == DEFAULT_PROMPT_SET
        assert _set_directory(baseline_env).name == OPERATIONAL_BASELINE_PROMPT_SET

    def test_a_different_root_returns_a_different_environment(
        self, tmp_path: Path
    ) -> None:
        # Same set name under another root (the byte-golden perturbation leg's
        # shape: a scratch copy of the template tree) must never be served the
        # committed tree's environment.
        (tmp_path / DEFAULT_PROMPT_SET).mkdir()
        scratch = build_environment(DEFAULT_PROMPT_SET, root=tmp_path)
        assert scratch is not build_environment(DEFAULT_PROMPT_SET)
        assert _set_directory(scratch) == tmp_path / DEFAULT_PROMPT_SET
        # ...and is itself stable for that root.
        assert scratch is build_environment(DEFAULT_PROMPT_SET, root=tmp_path)

    def test_two_bundles_for_one_set_carry_one_environment(self) -> None:
        # The production shape: a meeting runner (and so a bundle) is built per
        # game, and two bundles for one set now share the one environment.
        first = build_prompt_renderers(DEFAULT_PROMPT_SET)
        second = build_prompt_renderers(DEFAULT_PROMPT_SET)
        assert _bundle_environment(first) is _bundle_environment(second)
        assert _bundle_environment(first) is build_environment(DEFAULT_PROMPT_SET)

    def test_the_roll_call_lever_is_not_part_of_the_key(self) -> None:
        # The lever picks template FILENAMES in build_prompt_renderers; the
        # environment those names are looked up in is the set's one environment
        # either way, which is why the key does not carry the lever.
        lever_on = build_prompt_renderers(
            OPERATIONAL_BASELINE_PROMPT_SET, env={ENV_IMPOSTOR_ROLL_CALL: "1"}
        )
        lever_off = build_prompt_renderers(OPERATIONAL_BASELINE_PROMPT_SET, env={})
        assert _bundle_environment(lever_on) is _bundle_environment(lever_off)

    def test_an_in_process_set_change_re_resolves(self) -> None:
        # The memo sits beneath resolution, so a caller that changes
        # AILIBI_PROMPT_SET mid-process gets the new set, not the cached one.
        first = build_environment(env={ENV_PROMPT_SET: "qwen3_32b"})
        second = build_environment(env={ENV_PROMPT_SET: DEFAULT_PROMPT_SET})
        assert first is not second
        assert _set_directory(first).name == "qwen3_32b"
        assert _set_directory(second).name == DEFAULT_PROMPT_SET

    def test_the_memo_caches_no_failure(self) -> None:
        # An unknown set raises on the second call exactly as on the first: a
        # lookup that raised stored nothing to serve back as success or silence.
        for _ in range(3):
            with pytest.raises(ValueError, match="Unknown prompt set 'no_such_set'"):
                build_environment("no_such_set")

    def test_a_set_that_appears_later_still_loads(self, tmp_path: Path) -> None:
        # The other half of "no failure is cached": the failed lookup must not
        # poison the key it failed on.
        with pytest.raises(ValueError, match="Unknown prompt set 'late_set'"):
            build_environment("late_set", root=tmp_path)
        set_dir = tmp_path / "late_set"
        set_dir.mkdir()
        (set_dir / CREWMATE_REPORT_TEMPLATE).write_text(
            "late {{ agent_id }}", encoding="utf-8"
        )
        environment = build_environment("late_set", root=tmp_path)
        rendered = environment.get_template(CREWMATE_REPORT_TEMPLATE).render(
            agent_id="p-9"
        )
        assert rendered == "late p-9"


class TestResolutionStillRunsOnEveryBuild:
    """The memo is beneath resolution, so the bare-fallback notice is unmoved.

    Task 20.5 made the notice once per process by memoizing the emission itself
    (:func:`_notify_bare_prompt_set_fallback`, which the autouse fixture above
    clears around every test here), so the count a caller sees is ONE however
    many bundles it builds. What the environment memo must not do is skip the
    resolution that feeds the notice: clearing the notice memo between builds
    re-arms the line, so a build that still resolves prints it again — and a
    memo wrapped ABOVE resolution would print once and then fall silent.
    """

    def test_five_bundles_emit_one_line(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        for _ in range(5):
            build_prompt_renderers(env=_REAL_PROVIDER_ENV)
        assert len(capsys.readouterr().err.strip().splitlines()) == 1

    def test_every_build_resolves(self, capsys: pytest.CaptureFixture[str]) -> None:
        for _ in range(5):
            _notify_bare_prompt_set_fallback.cache_clear()
            build_environment(env=_REAL_PROVIDER_ENV)
        assert len(capsys.readouterr().err.strip().splitlines()) == 5
