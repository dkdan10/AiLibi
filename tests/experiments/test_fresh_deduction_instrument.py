"""Tests for experiments/fresh_deduction_instrument.py.

The fake provider is the only provider anything here reaches: the instrument's
own live gate refuses every other one without an explicit invocation, and the
tree scan below keeps that flag out of every committed test, script and
workflow.

Each guard the instrument adds is paired with a planted or perturbed case that
fails on the defect the guard claims to catch — a moved digest, a changed skip
list, a call over the cap, a truncated response, an exhausted budget, an expired
deadline, a mislabelled clock, a citation the voter never saw, a leaked prefix
step and a planted body handle.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Final

import pytest
from pydantic import BaseModel

import experiments.fresh_deduction_instrument as instrument
from experiments.fresh_deduction_instrument import (
    AUTHORIZED_LIMITS,
    AUTHORIZED_MODEL,
    AUTHORIZED_PROMPT_SET,
    AUTHORIZED_PROVIDER,
    AUTHORIZED_SAMPLING,
    DECISION_RULE,
    EXECUTION_MANIFEST_PATH,
    MINIMUM_ACTIONABLE_EFFECT_UNITS,
    PRIMARY_OUTCOME,
    STOP_RULE,
    DryRunProvider,
    FrozenSetMismatch,
    InstrumentAborted,
    InstrumentReport,
    LiveRunInvocation,
    LiveRunNotAuthorized,
    PerCallCapExceeded,
    PrefixBytesLeaked,
    PrivilegedGrade,
    RunLimits,
    SupportedGrade,
    UnitGrade,
    assert_live_run_is_authorized,
    assert_report_holds_no_prefix_bytes,
    grade_privileged,
    grade_supported,
    grade_unit,
    instrument_arms,
    paired_result,
    run_dry,
    run_instrument,
    verify_frozen_set,
)
from experiments.held_out_prefixes import (
    LEGACY_BODY_HANDLE_PATTERN,
    MANIFEST_PATH,
    TEMPORAL_OBSERVATION_VERSION,
    HeldOutPrefixError,
    assert_no_legacy_body_handles,
    canonical_prefix_json,
)
from llm.client import CallKind, LLMResponse, TokenUsage
from meetings.schemas import VoteBallot

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
_MANIFEST: Final[Path] = _REPO_ROOT / EXECUTION_MANIFEST_PATH
_INSTRUMENT_SOURCE: Final[Path] = (
    _REPO_ROOT / "experiments" / "fresh_deduction_instrument.py"
)

#: How many units a test that only needs the pipeline to turn over should run.
#: Two prefixes is enough for a paired comparison and keeps these tests fast;
#: the full 50 runs once, in the dry-run test.
_SMOKE_UNITS: Final[int] = 2


def _manifest_digest() -> str:
    """The committed execution manifest's own digest, as the gate recomputes it."""

    return hashlib.sha256(_MANIFEST.read_bytes()).hexdigest()


def _write_frozen_manifest(root: Path, payload: dict[str, Any]) -> None:
    path = root / MANIFEST_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", "utf-8")


def _committed_manifest() -> dict[str, Any]:
    loaded = json.loads((_REPO_ROOT / MANIFEST_PATH).read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


class _StubClient:
    """A minimal in-process client with no schema behaviour, for cap tests."""

    def __init__(self, *, output_tokens: int = 5, input_tokens: int = 1) -> None:
        self.output_tokens = output_tokens
        self.input_tokens = input_tokens
        self.calls = 0

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        del prompt, schema, temperature, call_kind, model, agent_id
        self.calls += 1
        return LLMResponse(
            text="{}",
            usage=TokenUsage(
                input_tokens=self.input_tokens, output_tokens=self.output_tokens
            ),
            cost_usd=0.0,
            model="stub",
        )


class _TruncatingProvider(DryRunProvider):
    """A dry-run provider whose responses always reach their output cap.

    Well-formed payloads, so the meeting layer accepts them and the stop comes
    from the truncation gate rather than from a validation failure.
    """

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        response = await super().complete(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
            agent_id=agent_id,
        )
        return LLMResponse(
            text=response.text,
            usage=TokenUsage(
                input_tokens=response.usage.input_tokens, output_tokens=max_tokens
            ),
            cost_usd=response.cost_usd,
            model=response.model,
        )


class _FailingProvider(DryRunProvider):
    """A dry-run provider whose transport fails partway through a unit."""

    def __init__(self, *, fail_on_call: int) -> None:
        super().__init__()
        self._fail_on_call = fail_on_call
        self.calls = 0

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        self.calls += 1
        if self.calls >= self._fail_on_call:
            raise RuntimeError("transport failure: connection reset by peer")
        return await super().complete(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
            agent_id=agent_id,
        )


class TestFrozenSet:
    def test_the_regenerated_set_matches_the_committed_freeze(self) -> None:
        frozen = verify_frozen_set(_REPO_ROOT)
        assert len(frozen.accepted_seeds) == 50
        assert len(frozen.skipped_seeds) == 8
        assert frozen.accepted_seeds[0] == 3000
        assert len(frozen.prefixes) == 50

    def test_a_moved_digest_stops_the_run(self, tmp_path: Path) -> None:
        # PLANTED: one accepted digest is flipped. The regenerated prefix
        # re-hashes to the committed value, so the comparison must refuse it.
        manifest = _committed_manifest()
        manifest["accepted"][7]["sha256"] = "0" * 64
        _write_frozen_manifest(tmp_path, manifest)
        with pytest.raises(FrozenSetMismatch, match="differ at row 7"):
            verify_frozen_set(tmp_path)

    def test_a_changed_skip_list_stops_the_run(self, tmp_path: Path) -> None:
        # PERTURBED: the skip list loses its last row. The filter still refuses
        # that seed, so the regenerated skips are longer than the frozen ones.
        manifest = _committed_manifest()
        manifest["skipped"] = manifest["skipped"][:-1]
        _write_frozen_manifest(tmp_path, manifest)
        with pytest.raises(FrozenSetMismatch, match="skipped seeds"):
            verify_frozen_set(tmp_path)

    def test_a_set_marked_development_is_refused(self, tmp_path: Path) -> None:
        manifest = _committed_manifest()
        manifest["status"] = "development"
        _write_frozen_manifest(tmp_path, manifest)
        with pytest.raises(FrozenSetMismatch, match="not 'held_out'"):
            verify_frozen_set(tmp_path)

    def test_a_foreign_observation_clock_is_refused(self, tmp_path: Path) -> None:
        manifest = _committed_manifest()
        manifest["temporal_observation_version"] = 1
        _write_frozen_manifest(tmp_path, manifest)
        with pytest.raises(FrozenSetMismatch, match="observation clock"):
            verify_frozen_set(tmp_path)

    def test_a_roster_the_budget_is_not_sized_on_is_refused(
        self, tmp_path: Path
    ) -> None:
        manifest = _committed_manifest()
        manifest["roster"]["num_players"] = 9
        _write_frozen_manifest(tmp_path, manifest)
        with pytest.raises(FrozenSetMismatch, match="change of roster"):
            verify_frozen_set(tmp_path)

    def test_a_moved_band_is_refused(self, tmp_path: Path) -> None:
        """PLANTED: the manifest describes a band the run does not draw. Without
        the check the digests still matched, because they came from the
        generator's defaults either way, and the manifest could have described a
        different set from the one regenerated."""

        manifest = _committed_manifest()
        manifest["band"]["first_seed"] = 9000
        manifest["band"]["last_seed"] = 9999
        _write_frozen_manifest(tmp_path, manifest)
        with pytest.raises(FrozenSetMismatch, match="preregistered band"):
            verify_frozen_set(tmp_path)

    def test_a_moved_tick_budget_is_refused(self, tmp_path: Path) -> None:
        # PLANTED: a tick budget no prefix in this set was screened under.
        manifest = _committed_manifest()
        manifest["max_ticks"] = 999
        _write_frozen_manifest(tmp_path, manifest)
        with pytest.raises(FrozenSetMismatch, match="tick budget"):
            verify_frozen_set(tmp_path)

    def test_a_moved_task_count_is_refused(self, tmp_path: Path) -> None:
        # PLANTED: the roster field the 4p1i check does not look at.
        manifest = _committed_manifest()
        manifest["roster"]["tasks_per_crewmate"] = 7
        _write_frozen_manifest(tmp_path, manifest)
        with pytest.raises(FrozenSetMismatch, match="change of roster"):
            verify_frozen_set(tmp_path)

    def test_a_descending_draw_is_refused(self, tmp_path: Path) -> None:
        manifest = _committed_manifest()
        manifest["band"]["draw_order"] = "descending"
        _write_frozen_manifest(tmp_path, manifest)
        with pytest.raises(FrozenSetMismatch, match="draws ascending"):
            verify_frozen_set(tmp_path)

    def test_a_missing_manifest_is_refused(self, tmp_path: Path) -> None:
        with pytest.raises(FrozenSetMismatch, match="missing"):
            verify_frozen_set(tmp_path)


class TestLiveGate:
    def test_a_live_provider_without_an_invocation_is_refused(
        self, tmp_path: Path
    ) -> None:
        # PLANTED: the authorized provider, and nothing else. Without the
        # explicit invocation the run must not reach a provider at all.
        with pytest.raises(LiveRunNotAuthorized, match="LiveRunInvocation"):
            run_instrument(
                output_dir=tmp_path,
                client=_StubClient(),
                provider=AUTHORIZED_PROVIDER,
            )

    def test_the_refusal_precedes_every_call(self, tmp_path: Path) -> None:
        client = _StubClient()
        with pytest.raises(LiveRunNotAuthorized):
            run_instrument(
                output_dir=tmp_path, client=client, provider=AUTHORIZED_PROVIDER
            )
        assert client.calls == 0

    def test_the_dry_run_refuses_a_live_invocation(self) -> None:
        invocation = LiveRunInvocation.naming(
            _MANIFEST, provider=AUTHORIZED_PROVIDER, model=AUTHORIZED_MODEL
        )
        with pytest.raises(LiveRunNotAuthorized, match="mechanics check"):
            run_dry(live_invocation=invocation)

    def test_a_fake_run_takes_no_invocation(self) -> None:
        invocation = LiveRunInvocation.naming(
            _MANIFEST, provider=AUTHORIZED_PROVIDER, model=AUTHORIZED_MODEL
        )
        with pytest.raises(LiveRunNotAuthorized, match="takes no live invocation"):
            assert_live_run_is_authorized(provider="fake", invocation=invocation)

    def test_an_invocation_naming_another_file_is_refused(self, tmp_path: Path) -> None:
        stray = tmp_path / "execution-manifest.md"
        stray.write_text(_MANIFEST.read_text(encoding="utf-8"), encoding="utf-8")
        with pytest.raises(LiveRunNotAuthorized, match="authorized execution manifest"):
            LiveRunInvocation.naming(
                stray, provider=AUTHORIZED_PROVIDER, model=AUTHORIZED_MODEL
            )

    def test_an_invocation_whose_manifest_omits_the_model_is_refused(
        self, tmp_path: Path
    ) -> None:
        # PERTURBED: this scratch root's own manifest, authorizing nothing.
        stray = tmp_path / "audits" / "deduction-candidate" / "execution-manifest.md"
        stray.parent.mkdir(parents=True)
        stray.write_text("# not an authorization\n", encoding="utf-8")
        with pytest.raises(LiveRunNotAuthorized, match="does not name"):
            LiveRunInvocation.naming(
                stray,
                provider=AUTHORIZED_PROVIDER,
                model=AUTHORIZED_MODEL,
                repo_root=tmp_path,
            )

    def test_a_same_named_manifest_outside_the_repository_is_refused(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: the review's own reproduction — a 41-byte file whose last
        three path components match, carrying none of the owner's limits."""

        forged = tmp_path / "audits" / "deduction-candidate" / "execution-manifest.md"
        forged.parent.mkdir(parents=True)
        forged.write_text(
            f"{AUTHORIZED_PROVIDER} {AUTHORIZED_MODEL} {AUTHORIZED_PROMPT_SET}",
            encoding="utf-8",
        )
        with pytest.raises(LiveRunNotAuthorized, match="authorized execution manifest"):
            LiveRunInvocation.naming(
                forged, provider=AUTHORIZED_PROVIDER, model=AUTHORIZED_MODEL
            )

    def test_a_hand_built_invocation_naming_another_path_is_refused(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: ``naming`` bypassed entirely, so the authorization boundary
        has to carry the path check on its own."""

        forged = LiveRunInvocation(
            manifest_path=tmp_path / "execution-manifest.md",
            manifest_sha256=_manifest_digest(),
            provider=AUTHORIZED_PROVIDER,
            model=AUTHORIZED_MODEL,
        )
        with pytest.raises(LiveRunNotAuthorized, match="committed execution manifest"):
            assert_live_run_is_authorized(
                provider=AUTHORIZED_PROVIDER, invocation=forged
            )

    def test_a_hand_built_invocation_with_a_stale_digest_is_refused(self) -> None:
        """PLANTED: the right path, a digest that is not this file's. The
        invocation's own field is not evidence; the file on disk is."""

        forged = LiveRunInvocation(
            manifest_path=_MANIFEST,
            manifest_sha256="0" * 64,
            provider=AUTHORIZED_PROVIDER,
            model=AUTHORIZED_MODEL,
        )
        with pytest.raises(LiveRunNotAuthorized, match="manifest digest"):
            assert_live_run_is_authorized(
                provider=AUTHORIZED_PROVIDER, invocation=forged
            )

    def test_a_hand_built_invocation_naming_another_model_is_refused(self) -> None:
        # PLANTED: the authorized provider, somebody else's model.
        forged = LiveRunInvocation(
            manifest_path=_MANIFEST,
            manifest_sha256=_manifest_digest(),
            provider=AUTHORIZED_PROVIDER,
            model="claude-sonnet-4-6",
        )
        with pytest.raises(LiveRunNotAuthorized, match="not the authorized"):
            assert_live_run_is_authorized(
                provider=AUTHORIZED_PROVIDER, invocation=forged
            )

    def test_a_live_invocation_carrying_a_unit_override_is_refused(self) -> None:
        """PLANTED: the one-unit live pilot. A live run is the whole frozen set;
        a subset spends part of a set the rest of which is still held out."""

        invocation = LiveRunInvocation.naming(
            _MANIFEST, provider=AUTHORIZED_PROVIDER, model=AUTHORIZED_MODEL
        )
        with pytest.raises(LiveRunNotAuthorized, match="whole frozen set"):
            assert_live_run_is_authorized(
                provider=AUTHORIZED_PROVIDER, invocation=invocation, units=1
            )

    def test_the_cli_refuses_a_live_unit_override_before_building_a_client(
        self, tmp_path: Path
    ) -> None:
        """The same refusal through the documented command shape, which is where
        a runner would actually type it."""

        with pytest.raises(LiveRunNotAuthorized, match="whole frozen set"):
            instrument.main(
                [
                    "--provider",
                    AUTHORIZED_PROVIDER,
                    "--execution-manifest",
                    str(_MANIFEST),
                    "--i-am-the-runner",
                    "--output-dir",
                    str(tmp_path),
                    "--units",
                    "1",
                ]
            )

    def test_a_live_run_may_not_move_the_authorized_sampling(self) -> None:
        invocation = LiveRunInvocation.naming(
            _MANIFEST, provider=AUTHORIZED_PROVIDER, model=AUTHORIZED_MODEL
        )
        hotter = instrument.AUTHORIZED_SAMPLING.model_copy(
            update={"turn_temperature": 1.0}
        )
        with pytest.raises(LiveRunNotAuthorized, match="sampling configuration"):
            assert_live_run_is_authorized(
                provider=AUTHORIZED_PROVIDER, invocation=invocation, sampling=hotter
            )

    def test_a_manifest_that_does_not_name_the_provider_authorizes_nothing(
        self,
    ) -> None:
        with pytest.raises(LiveRunNotAuthorized, match="does not name 'anthropic'"):
            LiveRunInvocation.naming(
                _MANIFEST, provider="anthropic", model=AUTHORIZED_MODEL
            )

    def test_an_unauthorized_provider_is_refused_even_with_an_invocation(self) -> None:
        # PLANTED: a hand-built invocation that skips ``naming``'s own refusal,
        # so the second gate has to carry the refusal on its own.
        forged = LiveRunInvocation(
            manifest_path=_MANIFEST,
            manifest_sha256="0" * 64,
            provider="anthropic",
            model=AUTHORIZED_MODEL,
        )
        with pytest.raises(LiveRunNotAuthorized, match="not the authorized provider"):
            assert_live_run_is_authorized(provider="anthropic", invocation=forged)

    def test_an_invocation_for_another_provider_is_refused(self) -> None:
        invocation = LiveRunInvocation.naming(
            _MANIFEST, provider=AUTHORIZED_PROVIDER, model=AUTHORIZED_MODEL
        )
        with pytest.raises(LiveRunNotAuthorized, match="names provider"):
            assert_live_run_is_authorized(provider="ollama", invocation=invocation)

    def test_a_live_run_may_not_move_the_authorized_limits(self) -> None:
        invocation = LiveRunInvocation.naming(
            _MANIFEST, provider=AUTHORIZED_PROVIDER, model=AUTHORIZED_MODEL
        )
        widened = AUTHORIZED_LIMITS.model_copy(
            update={"run_max_input_tokens": 99_000_000}
        )
        with pytest.raises(LiveRunNotAuthorized, match="authorized limits exactly"):
            assert_live_run_is_authorized(
                provider=AUTHORIZED_PROVIDER, invocation=invocation, limits=widened
            )

    def test_no_committed_test_script_or_workflow_performs_the_live_invocation(
        self,
    ) -> None:
        """The live flag exists in exactly two committed places: here, and the
        instrument that defines it. Anything else would be a path to a call that
        no one chose."""

        allowed = {
            Path("experiments/fresh_deduction_instrument.py"),
            Path("tests/experiments/test_fresh_deduction_instrument.py"),
            Path(EXECUTION_MANIFEST_PATH),
        }
        roots = ("tests", "scripts", ".github", "experiments", "audits")
        offenders: list[str] = []
        for root in roots:
            for path in sorted((_REPO_ROOT / root).rglob("*")):
                if not path.is_file() or path.suffix not in {
                    ".py",
                    ".sh",
                    ".yml",
                    ".yaml",
                    ".md",
                }:
                    continue
                relative = path.relative_to(_REPO_ROOT)
                if relative in allowed:
                    continue
                if "--i-am-the-runner" in path.read_text(
                    encoding="utf-8", errors="ignore"
                ):
                    offenders.append(str(relative))
        assert offenders == []

    def test_this_test_module_never_reaches_a_live_provider(self) -> None:
        """The one test file the scan above exempts must not build a real client.

        The scan lets this file mention the flag so the refusal can be tested;
        this keeps the exemption from becoming a hole, by refusing any import of
        the real client factory here.
        """

        source = Path(__file__).read_text(encoding="utf-8")
        assert "--i-am-the-runner" in source
        assert re.search(r"^\s*(?:from|import)\s+llm\.provider", source, re.M) is None


class TestAuthorizedClient:
    """The live client is built from the authorization, not from the shell.

    Nothing here constructs a real provider: the pinned environment carries no
    credential in any of these cases, so every call refuses before a client
    exists. That refusal IS the property under test.
    """

    def test_the_pinned_environment_ignores_the_ambient_provider_and_model(
        self,
    ) -> None:
        # PLANTED: a shell that names a metered provider and another model —
        # the review's reproduction, which used to decide what a run labelled
        # `featherless` actually reached.
        pinned = instrument.authorized_client_environment(
            {
                "AILIBI_LLM_PROVIDER": "anthropic",
                "AILIBI_LLM_MEETING_MODEL": "claude-sonnet-4-6",
                "AILIBI_LLM_TRIGGER_MODEL": "claude-haiku-4-5",
                "ANTHROPIC_API_KEY": "sk-ambient",
                "FEATHERLESS_API_KEY": "fk-ambient",
            }
        )
        assert pinned["AILIBI_LLM_PROVIDER"] == AUTHORIZED_PROVIDER
        assert pinned["AILIBI_LLM_MEETING_MODEL"] == AUTHORIZED_MODEL
        assert pinned["AILIBI_LLM_TRIGGER_MODEL"] == AUTHORIZED_MODEL
        # The credential is the only ambient value that crosses over, and no
        # other provider's key comes with it.
        assert set(pinned) == {
            "AILIBI_LLM_PROVIDER",
            "AILIBI_LLM_MEETING_MODEL",
            "AILIBI_LLM_TRIGGER_MODEL",
            "FEATHERLESS_API_KEY",
        }
        assert pinned["FEATHERLESS_API_KEY"] == "fk-ambient"

    def test_an_ambient_fake_provider_cannot_stand_in_for_the_authorized_one(
        self,
    ) -> None:
        """PLANTED: exactly the reproduction that recorded a fake run as live —
        `AILIBI_LLM_PROVIDER=fake` and no Featherless key. It must refuse, not
        hand back a `FakeProvider` for a report labelled `dry_run: false`."""

        with pytest.raises(LiveRunNotAuthorized, match="FEATHERLESS_API_KEY"):
            instrument.build_authorized_client(env={"AILIBI_LLM_PROVIDER": "fake"})

    def test_the_default_environment_is_the_process_one_and_still_pinned(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("AILIBI_LLM_PROVIDER", "fake")
        monkeypatch.delenv("FEATHERLESS_API_KEY", raising=False)
        with pytest.raises(LiveRunNotAuthorized, match="FEATHERLESS_API_KEY"):
            instrument.build_authorized_client()

    def test_a_response_from_another_model_stops_the_run(self) -> None:
        """PLANTED: the endpoint serves a different checkpoint. The stop lands on
        the call that returned it, not in the report afterwards."""

        import asyncio

        clock = instrument._ModelWorkClock(max_seconds=3600.0)
        client = instrument._InstrumentClient(
            _StubClient(), work_clock=clock, expected_model=AUTHORIZED_MODEL
        )
        with pytest.raises(instrument.ProviderIdentityMismatch, match="'stub'"):
            asyncio.run(
                client.complete(
                    prompt="p", schema=None, max_tokens=1024, temperature=0.2
                )
            )
        # Spent, therefore retained: the response came back before it was refused.
        assert [call.model for call in client.calls] == ["stub"]

    def test_a_live_run_binds_the_client_to_the_invocations_model(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The wiring, not just the gate: the run must hand the client the model
        it is authorized for. Nothing is called — the spy stops the run at the
        moment the client is built, so no unit and no provider is reached."""

        seen: dict[str, Any] = {}

        class _Stop(RuntimeError):
            pass

        def spy(inner: Any, **kwargs: Any) -> Any:
            seen.update(kwargs)
            raise _Stop("stopped before any unit ran")

        monkeypatch.setattr(instrument, "_InstrumentClient", spy)
        invocation = LiveRunInvocation.naming(
            _MANIFEST, provider=AUTHORIZED_PROVIDER, model=AUTHORIZED_MODEL
        )
        with pytest.raises(_Stop):
            run_instrument(
                output_dir=tmp_path,
                client=_StubClient(),
                provider=AUTHORIZED_PROVIDER,
                live_invocation=invocation,
            )
        assert seen["expected_model"] == AUTHORIZED_MODEL

    def test_the_dry_run_binds_no_served_model(self) -> None:
        """The check is a live-run one: the dry run's fixture model is its own
        marker, so binding it would be a fiction rather than a gate."""

        import asyncio

        clock = instrument._ModelWorkClock(max_seconds=3600.0)
        client = instrument._InstrumentClient(_StubClient(), work_clock=clock)
        asyncio.run(
            client.complete(prompt="p", schema=None, max_tokens=1024, temperature=0.2)
        )
        assert [call.model for call in client.calls] == ["stub"]


class TestPerCallCaps:
    def _client(self, inner: _StubClient, *, work_seconds: float = 3600.0) -> Any:
        clock = instrument._ModelWorkClock(max_seconds=work_seconds)
        return instrument._InstrumentClient(inner, work_clock=clock)

    @pytest.mark.parametrize("max_tokens", [4096, 512])
    def test_a_call_outside_the_shipped_caps_stops_the_run(
        self, max_tokens: int
    ) -> None:
        # PLANTED: a caller asking for a cap the authorization did not name.
        import asyncio

        client = self._client(_StubClient())
        with pytest.raises(PerCallCapExceeded):
            asyncio.run(
                client.complete(
                    prompt="p",
                    schema=None,
                    max_tokens=max_tokens,
                    temperature=0.2,
                )
            )

    def test_a_truncated_response_stops_the_run(self) -> None:
        # PLANTED: the response reaches its own cap, which is a cap artifact.
        import asyncio

        client = self._client(_StubClient(output_tokens=1024))
        with pytest.raises(PerCallCapExceeded, match="a truncation is a stop"):
            asyncio.run(
                client.complete(
                    prompt="p", schema=None, max_tokens=1024, temperature=0.2
                )
            )

    def test_a_truncation_stop_retains_the_capped_calls_spend(self) -> None:
        """The truncation stop is the one stop condition this gate itself
        creates, so the partial accounting it hands back must carry the call
        that caused it. PLANTED: a response that reaches its cap at 1,234 input
        tokens."""

        import asyncio

        clock = instrument._ModelWorkClock(max_seconds=3600.0)
        client = instrument._InstrumentClient(
            _StubClient(output_tokens=1024, input_tokens=1234), work_clock=clock
        )
        with pytest.raises(PerCallCapExceeded, match="a truncation is a stop"):
            asyncio.run(
                client.complete(
                    prompt="p", schema=None, max_tokens=1024, temperature=0.2
                )
            )
        usage = instrument.ArmUsage().plus(client.take())
        assert (usage.calls, usage.input_tokens, usage.output_tokens) == (1, 1234, 1024)
        assert usage.model_work_seconds >= 0.0
        assert clock.seconds >= 0.0

    def test_a_truncation_mid_run_reports_the_partial_state(
        self, tmp_path: Path
    ) -> None:
        """The same property through the run: a provider whose first response
        reaches its cap stops the run with the stopped unit's spend."""

        with pytest.raises(InstrumentAborted) as caught:
            run_instrument(output_dir=tmp_path, client=_TruncatingProvider(), units=1)
        partial = caught.value.partial
        assert "a truncation is a stop" in partial.reason
        usage = partial.usage_by_arm["repaired_clock"]
        assert usage.calls == 1
        assert usage.input_tokens > 0

    def test_a_response_under_its_cap_is_kept(self) -> None:
        import asyncio

        client = self._client(_StubClient(output_tokens=7))
        asyncio.run(
            client.complete(prompt="p", schema=None, max_tokens=1024, temperature=0.2)
        )
        assert [call.output_tokens for call in client.calls] == [7]

    def test_the_meeting_only_asks_for_the_shipped_caps(self, tmp_path: Path) -> None:
        report = run_instrument(output_dir=tmp_path, units=1)
        assert report.arms[0].calls == 6
        # 3 turns at 2048 and 3 votes at 1024 per unit: the client would have
        # refused anything else, so a green run IS the assertion. The report's
        # call count is what says the calls happened at all.
        assert report.limits == AUTHORIZED_LIMITS


class TestBudgetAndDeadline:
    def test_a_budget_overrun_stops_the_run_and_reports_partial_state(
        self, tmp_path: Path
    ) -> None:
        # PLANTED: a run-level input budget one unit cannot fit inside.
        starved = AUTHORIZED_LIMITS.model_copy(update={"run_max_input_tokens": 4_000})
        with pytest.raises(InstrumentAborted) as caught:
            run_instrument(output_dir=tmp_path, units=_SMOKE_UNITS, limits=starved)
        partial = caught.value.partial
        assert partial.completed_units == 0
        assert partial.planned_units == _SMOKE_UNITS * 2
        assert "BudgetExceededError" in partial.reason
        assert "0/4 units completed" in partial.describe()

    def test_the_stopped_units_spend_is_retained(self, tmp_path: Path) -> None:
        # The calls that were made before the overrun are unusable but real, so
        # the partial accounting must carry them rather than round them away.
        starved = AUTHORIZED_LIMITS.model_copy(update={"run_max_input_tokens": 12_000})
        with pytest.raises(InstrumentAborted) as caught:
            run_instrument(output_dir=tmp_path, units=1, limits=starved)
        usage = caught.value.partial.usage_by_arm["repaired_clock"]
        assert usage.calls > 0
        assert usage.input_tokens > 0

    def test_a_provider_transport_failure_stops_the_run_with_partial_state(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: the provider drops the connection on its fifth call. The
        stop rule calls a missing attempt a stop, so it must arrive as an
        `InstrumentAborted` carrying the spend, not as a bare `RuntimeError`."""

        failing = _FailingProvider(fail_on_call=5)
        with pytest.raises(InstrumentAborted) as caught:
            run_instrument(output_dir=tmp_path, client=failing, units=1)
        partial = caught.value.partial
        assert "transport failure" in partial.reason
        assert partial.completed_units == 0
        usage = partial.usage_by_arm["repaired_clock"]
        assert usage.calls == 4
        assert usage.input_tokens > 0

    def test_a_mid_run_legacy_body_handle_stops_the_run_with_partial_state(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """PLANTED: the handle check fires on a RENDERED PROMPT rather than on a
        regenerated prefix, which is the half of that stop condition the frozen
        set's own verification cannot reach. The planted assertion passes every
        prefix (canonical JSON, so it starts with a brace) and refuses every
        prompt."""

        def planted(texts: Sequence[str]) -> None:
            for text in texts:
                if not text.startswith("{"):
                    raise HeldOutPrefixError(
                        "planted handle match in a rendered prompt: body-p-1-7"
                    )

        monkeypatch.setattr(instrument, "assert_no_legacy_body_handles", planted)
        with pytest.raises(InstrumentAborted) as caught:
            run_instrument(output_dir=tmp_path, units=1)
        partial = caught.value.partial
        assert "body-p-1-7" in partial.reason
        assert partial.usage_by_arm["repaired_clock"].calls == 6

    def test_an_expired_deadline_stops_the_run_and_reports_partial_state(
        self, tmp_path: Path
    ) -> None:
        # PLANTED: a wall the first unit cannot fit inside.
        expired = AUTHORIZED_LIMITS.model_copy(update={"elapsed_seconds": 0.0})
        with pytest.raises(InstrumentAborted) as caught:
            run_instrument(output_dir=tmp_path, units=1, limits=expired)
        assert "RunDeadlineExceeded" in caught.value.partial.reason

    def test_an_exhausted_model_work_window_stops_the_run(self, tmp_path: Path) -> None:
        # PLANTED: a work window smaller than one call's own wall.
        tiny = AUTHORIZED_LIMITS.model_copy(update={"model_work_seconds": 1e-9})
        with pytest.raises(InstrumentAborted) as caught:
            run_instrument(output_dir=tmp_path, units=1, limits=tiny)
        assert "model-work window" in caught.value.partial.reason


class TestProvenance:
    def test_each_unit_records_its_arms_clock_and_config(self, tmp_path: Path) -> None:
        report = run_instrument(output_dir=tmp_path, units=1)
        # A green run IS the assertion: run_unit refuses a unit whose recorded
        # clock or config is not the arm's. The prompt versions prove the two
        # arms rendered different template families, which is what the recorded
        # config distinguishes.
        reference, candidate = report.arms
        assert reference.prompt_versions != candidate.prompt_versions
        assert reference.units == candidate.units == 1

    def test_a_mislabelled_clock_stops_the_run_and_reports_partial_state(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # PERTURBED: the recorded clock reads back as v1. Without the provenance
        # check the two arms would be indistinguishable in the record, which is
        # the defect this gate exists for.
        monkeypatch.setattr(
            instrument, "recorded_temporal_observation_version", lambda entries: 1
        )
        with pytest.raises(InstrumentAborted) as caught:
            run_instrument(output_dir=tmp_path, units=1)
        assert "ProvenanceMismatch" in caught.value.partial.reason

    def test_the_arms_differ_only_in_the_account_channels(self) -> None:
        reference, candidate = instrument_arms()
        assert reference.temporal_version == candidate.temporal_version == 2
        base = reference.experiment_config.model_dump()
        changed = {
            key
            for key, value in candidate.experiment_config.model_dump().items()
            if base.get(key) != value
        }
        assert changed == {"public_account_version", "attributed_testimony_version"}


class TestGraders:
    def _ballot(self, **kwargs: Any) -> VoteBallot:
        payload: dict[str, Any] = {
            "voter": "p-1",
            "target": "p-2",
            "confidence": 0.7,
            "primary_reason_id": None,
            "primary_reason_observation_id": None,
            "considered_alternatives": (),
            "rationale_text": "",
        }
        payload.update(kwargs)
        return VoteBallot.model_validate(payload)

    def test_a_citation_in_the_voters_own_prompt_is_supported(self) -> None:
        grades = grade_supported(
            [self._ballot(primary_reason_id="m:turn-0")],
            prompts_by_agent={"p-1": ["... [m:turn-0] ..."]},
        )
        assert [grade.verdict for grade in grades] == ["supported"]

    def test_a_citation_only_another_voter_saw_is_unsupported(self) -> None:
        # PLANTED: the cited turn exists, in somebody else's prompt. A grader
        # that searched the meeting rather than the voter would call this
        # supported.
        grades = grade_supported(
            [self._ballot(primary_reason_id="m:turn-0")],
            prompts_by_agent={"p-1": ["nothing"], "p-2": ["... [m:turn-0] ..."]},
        )
        assert [grade.verdict for grade in grades] == ["unsupported"]

    def test_a_ballot_with_no_citation_is_uncited(self) -> None:
        grades = grade_supported(
            [self._ballot(target="SKIP")], prompts_by_agent={"p-1": ["anything"]}
        )
        assert [grade.verdict for grade in grades] == ["uncited"]

    def test_both_citation_channels_must_be_supported(self) -> None:
        grades = grade_supported(
            [
                self._ballot(
                    primary_reason_id="m:turn-0",
                    primary_reason_observation_id="p-1:4:0",
                )
            ],
            prompts_by_agent={"p-1": ["[m:turn-0] but no observation id"]},
        )
        assert [grade.verdict for grade in grades] == ["unsupported"]

    def _record(self, **kwargs: Any) -> Any:
        payload: dict[str, Any] = {
            "seed": 3000,
            "arm": "repaired_clock",
            "meeting_id": "m",
            "outcome": "EJECTED",
            "ejected_player_id": "p-2",
            "ballots": (),
            "turn_ids": (),
            "roles": {"p-1": "CREWMATE", "p-2": "IMPOSTOR", "p-3": "CREWMATE"},
            "prompts_by_agent": {},
            "calls": (),
            "game_outcome": "CREWMATES",
            "recorded_temporal_version": 2,
            "recorded_experiment_config": None,
            "prompt_versions": {},
        }
        payload.update(kwargs)
        return instrument.UnitRecord(**payload)

    def test_the_privileged_pass_scores_role_truth(self) -> None:
        supported = (
            SupportedGrade(
                voter="p-1",
                target="p-2",
                cited_turn_id="m:turn-0",
                cited_observation_id=None,
                verdict="supported",
                guard_rewrite_reason=None,
            ),
        )
        grade = grade_privileged(self._record(), supported=supported)
        assert grade == PrivilegedGrade(
            ejected_player_id="p-2",
            ejected_role="IMPOSTOR",
            role_correct=True,
            supported_correct_ejection=True,
        )

    def test_a_role_correct_ejection_on_an_unsupported_ballot_is_not_the_primary(
        self,
    ) -> None:
        # The conjunction is the point: right for the wrong reason scores 0 on
        # the primary outcome and 1 on role-correctness, and the two are
        # reported separately.
        supported = (
            SupportedGrade(
                voter="p-1",
                target="p-2",
                cited_turn_id="m:turn-9",
                cited_observation_id=None,
                verdict="unsupported",
                guard_rewrite_reason=None,
            ),
        )
        grade = grade_privileged(self._record(), supported=supported)
        assert grade.role_correct is True
        assert grade.supported_correct_ejection is False

    def test_a_guard_rewritten_ballot_is_not_the_voters_supported_call(self) -> None:
        supported = (
            SupportedGrade(
                voter="p-1",
                target="p-2",
                cited_turn_id="m:turn-0",
                cited_observation_id=None,
                verdict="supported",
                guard_rewrite_reason="under_gate_redirect",
            ),
        )
        grade = grade_privileged(self._record(), supported=supported)
        assert grade.role_correct is True
        assert grade.supported_correct_ejection is False

    def test_a_skip_scores_neither(self) -> None:
        grade = grade_privileged(
            self._record(outcome="SKIPPED", ejected_player_id=None), supported=()
        )
        assert grade.role_correct is False
        assert grade.supported_correct_ejection is False

    def test_the_run_path_calls_no_grader(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Judge information cannot reach a listener or a tactic if no grader
        runs while the game does. Every grader is replaced by a landmine and a
        unit is run anyway; the run must complete."""

        def landmine(*args: Any, **kwargs: Any) -> Any:
            raise AssertionError("a grader ran inside the run path")

        for name in ("grade_unit", "grade_supported", "grade_privileged"):
            monkeypatch.setattr(instrument, name, landmine)
        frozen = verify_frozen_set(_REPO_ROOT)
        arm = instrument_arms()[0]
        work_clock = instrument._ModelWorkClock(max_seconds=3600.0)
        client = instrument._InstrumentClient(DryRunProvider(), work_clock=work_clock)
        from llm.budget import GameBudget
        from orchestrator.run_limits import RunDeadline

        record = instrument.run_unit(
            frozen.prefixes[0],
            arm=arm,
            client=client,
            run_budget=GameBudget(
                max_cost_usd=0.0, max_input_tokens=2_400_000, max_output_tokens=200_000
            ),
            deadline=RunDeadline(seconds=600.0),
            work_clock=work_clock,
            output_dir=tmp_path,
        )
        assert record.ballots

    def test_no_prompt_carries_a_grader_verdict(self, tmp_path: Path) -> None:
        frozen = verify_frozen_set(_REPO_ROOT)
        arm = instrument_arms()[0]
        work_clock = instrument._ModelWorkClock(max_seconds=3600.0)
        client = instrument._InstrumentClient(DryRunProvider(), work_clock=work_clock)
        from llm.budget import GameBudget
        from orchestrator.run_limits import RunDeadline

        record = instrument.run_unit(
            frozen.prefixes[0],
            arm=arm,
            client=client,
            run_budget=GameBudget(
                max_cost_usd=0.0, max_input_tokens=2_400_000, max_output_tokens=200_000
            ),
            deadline=RunDeadline(seconds=600.0),
            work_clock=work_clock,
            output_dir=tmp_path,
        )
        grade = grade_unit(record)
        assert grade.supported
        for prompts in record.prompts_by_agent.values():
            for prompt in prompts:
                for token in (
                    PRIMARY_OUTCOME,
                    "supported_correct_ejection",
                    "role_correct",
                    "right for that reason",
                ):
                    assert token not in prompt


class TestPairedStatistics:
    def _grades(
        self, reference: Sequence[bool], candidate: Sequence[bool]
    ) -> list[UnitGrade]:
        grades: list[UnitGrade] = []
        for index, (ref, cand) in enumerate(zip(reference, candidate)):
            for arm, primary in (("repaired_clock", ref), ("combined_accounts", cand)):
                grades.append(
                    UnitGrade(
                        seed=3000 + index,
                        arm=arm,  # type: ignore[arg-type]
                        outcome="EJECTED" if primary else "SKIPPED",
                        stop="terminal",
                        supported=(),
                        privileged=PrivilegedGrade(
                            ejected_player_id="p-2" if primary else None,
                            ejected_role="IMPOSTOR" if primary else None,
                            role_correct=primary,
                            supported_correct_ejection=primary,
                        ),
                    )
                )
        return grades

    def test_the_discordant_counts_drive_the_exact_test(self) -> None:
        result = paired_result(
            self._grades([False] * 6 + [True] * 4, [True] * 6 + [True] * 4)
        )
        assert (result.b, result.c, result.net) == (6, 0, 6)
        assert result.p_exact == pytest.approx(0.03125)
        # Significant, but under the minimum actionable effect, so the decision
        # rule still says no. That conjunction is the whole point of the rule.
        assert result.meets_decision_rule is False

    def test_the_decision_rule_needs_both_halves(self) -> None:
        result = paired_result(
            self._grades([False] * 10 + [True] * 40, [True] * 10 + [True] * 40)
        )
        assert (result.b, result.c) == (10, 0)
        assert result.p_exact < 0.05
        assert result.wrongful_net == 0
        assert result.meets_decision_rule is True

    def _wrongful_grades(
        self, *, reference: Sequence[bool], candidate: Sequence[bool]
    ) -> list[UnitGrade]:
        """Units whose meetings ejected a CREWMATE where the flag is set.

        The primary outcome is False on every one of them: a wrongful ejection is
        neither role-correct nor supported-correct.
        """

        grades: list[UnitGrade] = []
        for index, (ref, cand) in enumerate(zip(reference, candidate)):
            for arm, wrongful in (
                ("repaired_clock", ref),
                ("combined_accounts", cand),
            ):
                grades.append(
                    UnitGrade(
                        seed=4000 + index,
                        arm=arm,  # type: ignore[arg-type]
                        outcome="EJECTED" if wrongful else "SKIPPED",
                        stop="terminal",
                        supported=(),
                        privileged=PrivilegedGrade(
                            ejected_player_id="p-3" if wrongful else None,
                            ejected_role="CREWMATE" if wrongful else None,
                            role_correct=False,
                            supported_correct_ejection=False,
                        ),
                    )
                )
        return grades

    def test_a_wrongful_ejection_is_an_ejected_crewmate_not_a_skip(self) -> None:
        wrongful, skipped = self._wrongful_grades(
            reference=[True, False], candidate=[True, False]
        )[:2]
        del skipped
        assert wrongful.privileged.wrongful_ejection is True
        clean = self._grades([True], [True])[0]
        assert clean.privileged.wrongful_ejection is False
        # A meeting that decided nothing is not a wrongful decision.
        no_ejection = self._grades([False], [False])[0]
        assert no_ejection.privileged.wrongful_ejection is False

    def test_a_candidate_that_buys_ejections_with_innocents_is_blocked(self) -> None:
        """PLANTED: the exact trade the preregistration's acceptable-tradeoff
        field exists to refuse — 12 supported-correct ejections bought while
        converting 13 reference-arm skips into wrongful crew ejections. p and
        the minimum actionable effect are both satisfied; the rule is not."""

        gains = self._grades([False] * 12 + [True] * 25, [True] * 12 + [True] * 25)
        cost = self._wrongful_grades(reference=[False] * 13, candidate=[True] * 13)
        result = paired_result([*gains, *cost])
        assert (result.b, result.c, result.net) == (12, 0, 12)
        assert result.p_exact < 0.05
        assert (result.reference_wrongful_ejections, result.wrongful_net) == (0, 13)
        assert result.meets_wrongful_ejection_tradeoff is False
        assert result.meets_decision_rule is False

    def test_one_for_one_is_paid_for_and_still_advances(self) -> None:
        """The bound is one-for-one, so 12 extra wrongful ejections against a net
        of 12 is the boundary and passes; 13 does not."""

        gains = self._grades([False] * 12 + [True] * 25, [True] * 12 + [True] * 25)
        cost = self._wrongful_grades(reference=[False] * 12, candidate=[True] * 12)
        result = paired_result([*gains, *cost])
        assert (result.net, result.wrongful_net) == (12, 12)
        assert result.meets_decision_rule is True

    def test_the_minimum_actionable_effects_own_figures_reproduce(self) -> None:
        """Every number in the manifest's justification, recomputed."""

        from paired_stats import exact_mcnemar_p

        assert exact_mcnemar_p(5, 0) == pytest.approx(0.0625)
        assert exact_mcnemar_p(6, 0) == pytest.approx(0.03125)
        assert exact_mcnemar_p(15, 5) == pytest.approx(0.041389, abs=1e-6)
        assert exact_mcnemar_p(16, 6) == pytest.approx(0.052479, abs=1e-6)
        assert MINIMUM_ACTIONABLE_EFFECT_UNITS == 10

    def test_an_unpaired_seed_is_refused(self) -> None:
        grades = self._grades([True], [True])
        with pytest.raises(instrument.InstrumentError, match="same seeds"):
            paired_result(grades[:1])

    def test_a_duplicated_seed_is_refused(self) -> None:
        grades = self._grades([True], [True])
        with pytest.raises(instrument.InstrumentError, match="appears twice"):
            paired_result([*grades, grades[0]])


class TestPrefixSecrecy:
    def test_the_report_carries_no_prefix_bytes(self, tmp_path: Path) -> None:
        report = run_instrument(output_dir=tmp_path, units=_SMOKE_UNITS)
        frozen = verify_frozen_set(_REPO_ROOT)
        assert_report_holds_no_prefix_bytes(report, frozen.prefixes)

    def test_a_report_carrying_a_scripted_step_is_refused(self, tmp_path: Path) -> None:
        # PLANTED: one prefix step's canonical JSON smuggled into a free-text
        # field. Without this guard a summary line could publish a held-out
        # input and convert the set to development data silently.
        frozen = verify_frozen_set(_REPO_ROOT)
        prefix = frozen.prefixes[0]
        report = run_instrument(output_dir=tmp_path, units=1)
        step = json.dumps(
            prefix.steps[0].model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
        )
        leaked = report.model_copy(update={"caveat": f"leaked {step}"})
        with pytest.raises(PrefixBytesLeaked, match="scripted step"):
            assert_report_holds_no_prefix_bytes(leaked, [prefix])

    def test_a_report_carrying_a_whole_prefix_is_refused(self, tmp_path: Path) -> None:
        frozen = verify_frozen_set(_REPO_ROOT)
        prefix = frozen.prefixes[0]
        report = run_instrument(output_dir=tmp_path, units=1)
        leaked = report.model_copy(update={"caveat": canonical_prefix_json(prefix)})
        with pytest.raises(PrefixBytesLeaked, match="canonical JSON"):
            assert_report_holds_no_prefix_bytes(leaked, [prefix])

    def test_the_report_model_declares_no_prompt_prefix_or_role_field(self) -> None:
        """A tripwire on the shape, so a later field cannot quietly publish an
        input. ``extra='forbid'`` stops an unknown key; this stops a known one
        being added without a decision."""

        assert set(InstrumentReport.model_fields) == {
            "provider",
            "model_ids",
            "execution_mode",
            "instrument_sha256",
            "prompt_set",
            "held_out_manifest_sha256",
            "held_out_accepted_seeds",
            "held_out_skipped_seeds",
            "limits",
            "sampling",
            "primary_outcome",
            "decision_rule",
            "wrongful_ejection_tradeoff",
            "stop_rule",
            "arms",
            "paired",
            "elapsed_seconds",
            "model_work_seconds",
            "total_cost_usd",
            "dry_run",
            "caveat",
        }


class TestBodyHandle:
    def test_no_frozen_prefix_matches_the_legacy_body_handle(self) -> None:
        frozen = verify_frozen_set(_REPO_ROOT)
        assert_no_legacy_body_handles(
            [canonical_prefix_json(prefix) for prefix in frozen.prefixes]
        )

    def test_no_rendered_prompt_matches_the_legacy_body_handle(
        self, tmp_path: Path
    ) -> None:
        frozen = verify_frozen_set(_REPO_ROOT)
        work_clock = instrument._ModelWorkClock(max_seconds=3600.0)
        client = instrument._InstrumentClient(DryRunProvider(), work_clock=work_clock)
        from llm.budget import GameBudget
        from orchestrator.run_limits import RunDeadline

        seen = 0
        for arm in instrument_arms():
            record = instrument.run_unit(
                frozen.prefixes[0],
                arm=arm,
                client=client,
                run_budget=GameBudget(
                    max_cost_usd=0.0,
                    max_input_tokens=2_400_000,
                    max_output_tokens=200_000,
                ),
                deadline=RunDeadline(seconds=600.0),
                work_clock=work_clock,
                output_dir=tmp_path,
            )
            for call in record.calls:
                assert LEGACY_BODY_HANDLE_PATTERN.search(call.prompt) is None
                seen += 1
        assert seen == 12

    def test_the_assertion_fails_on_a_planted_handle(self) -> None:
        # PLANTED: the exact handle temporal v1 used to render.
        with pytest.raises(HeldOutPrefixError, match="body-p-2-4"):
            assert_no_legacy_body_handles(["the body body-p-2-4 was found"])


class TestExecutionManifest:
    def _text(self) -> str:
        return _MANIFEST.read_text(encoding="utf-8")

    def test_the_manifest_exists_where_the_instrument_names_it(self) -> None:
        assert _MANIFEST.is_file()

    @pytest.mark.parametrize(
        "quoted",
        [
            "`featherless`",
            "`Qwen/Qwen3.6-27B`",
            "turn 2,048 output / vote 1,024",
            "turn temperature 0.4 / vote temperature 0.2",
            "2,400,000 input / 200,000 output run-level",
            "45,000 input / 4,000 output per unit",
            "4 h of model work within a 6 h elapsed deadline",
            "$0.00 marginal",
            "4p1i with 3 living voters at meeting open",
            "| Execution mode | sequential |",
            "`qwen3_6_27b`",
        ],
    )
    def test_the_manifest_quotes_each_authorized_value(self, quoted: str) -> None:
        assert quoted in self._text()

    def test_the_manifest_quotes_the_cost_statement_verbatim(self) -> None:
        authorization = (
            _REPO_ROOT / "tasks" / "work" / "fresh-deduction-authorization.md"
        ).read_text(encoding="utf-8")
        start = authorization.index(
            "> This evaluation runs on the Featherless AI Premium plan"
        )
        end = authorization.index("Rejected, with grounds")
        statement = authorization[start:end].rstrip()
        assert statement in self._text()

    def test_the_manifest_quotes_the_frozen_analysis(self) -> None:
        text = self._text()
        assert PRIMARY_OUTCOME in text
        assert " ".join(DECISION_RULE.split()) in " ".join(text.split())
        assert " ".join(STOP_RULE.split()) in " ".join(text.split())
        assert f"at least {MINIMUM_ACTIONABLE_EFFECT_UNITS} units" in text

    def test_the_manifest_binds_the_acceptable_tradeoff(self) -> None:
        """The preregistration names 'acceptable tradeoffs' among the fields a
        manifest must bind, so the wrongful-decision bound is quoted here the
        same way the decision rule is."""

        text = " ".join(self._text().split())
        assert " ".join(instrument.WRONGFUL_EJECTION_TRADEOFF.split()) in text
        assert "acceptable tradeoff" in text.lower()

    def test_the_manifest_binds_the_sampling_temperatures(self) -> None:
        text = self._text()
        assert f"turn temperature {AUTHORIZED_SAMPLING.turn_temperature}" in text
        assert f"vote temperature {AUTHORIZED_SAMPLING.vote_temperature}" in text

    def test_the_manifest_states_that_it_authorizes_no_run(self) -> None:
        text = self._text()
        assert "This document authorizes no live call" in text
        assert "#437 authorized LIMITS, not a run" in text
        assert "--i-am-the-runner" in text

    def test_the_manifest_records_the_supersession_of_the_empty_fields(self) -> None:
        text = self._text()
        assert "present and EMPTY" in text
        assert "present and FILLED" in text

    def test_the_manifest_states_the_death_tick_handle_choice(self) -> None:
        text = self._text()
        assert "Left as temporal version 2 renders it" in text
        assert LEGACY_BODY_HANDLE_PATTERN.pattern in text

    def test_the_manifest_names_the_preparer_and_the_runner(self) -> None:
        text = self._text()
        assert "held-out-prefix-freeze.md" in text
        assert "23a23c2d" in text
        assert "It ran no arm" in text

    def test_the_manifest_binds_the_held_out_set_it_regenerates(self) -> None:
        manifest = _committed_manifest()
        text = self._text()
        assert str(manifest["band"]["first_seed"]) in text
        assert str(manifest["band"]["last_seed"]) in text
        assert f"accepted seeds run 3000–{manifest['last_accepted_seed']}" in text
        assert f"{manifest['skipped_reason_counts']['witnessed_kill']} skips" in text


class TestHarnessesUntouched:
    def test_the_instrument_imports_neither_mechanics_only_harness(self) -> None:
        source = _INSTRUMENT_SOURCE.read_text(encoding="utf-8")
        imports = re.findall(r"^\s*(?:from|import)\s+(\S+)", source, re.MULTILINE)
        forbidden = {
            "experiments.deduction_evaluation",
            "experiments.investigation_evaluation",
        }
        assert forbidden.isdisjoint(imports)

    def test_the_committed_harnesses_still_refuse_a_real_provider(self) -> None:
        for module in ("deduction_evaluation", "investigation_evaluation"):
            source = (_REPO_ROOT / "experiments" / f"{module}.py").read_text(
                encoding="utf-8"
            )
            assert "MECHANICS_ONLY" in source

    def test_the_frozen_generator_is_consumed_not_reimplemented(self) -> None:
        source = _INSTRUMENT_SOURCE.read_text(encoding="utf-8")
        assert "from experiments.held_out_prefixes import" in source
        # The instrument regenerates through the frozen module's own entry
        # point; a second generator would be a second definition of the set.
        assert "def build_prefix" not in source
        assert "def generate(" not in source


class TestDryRun:
    def test_the_full_dry_run_completes_at_zero_cost(self, tmp_path: Path) -> None:
        report = run_dry(output_dir=tmp_path)
        assert report.dry_run is True
        assert report.provider == "fake"
        assert report.total_cost_usd == 0.0
        assert report.paired.paired_units == 50
        assert sum(arm.units for arm in report.arms) == 100
        assert sum(arm.calls for arm in report.arms) == 600
        assert report.prompt_set == AUTHORIZED_PROMPT_SET
        # The mechanics claim: BOTH arms carried a non-SKIP decision through to
        # a graded outcome. Nothing here says a model would.
        for arm in report.arms:
            assert arm.ejections > 0
            assert arm.supported_correct_ejections > 0
            assert arm.ballot_verdicts["supported"] > 0
        assert "says nothing about model judgment" in report.caveat

    def test_the_dry_run_writes_nothing_outside_the_directory_it_is_given(
        self, tmp_path: Path
    ) -> None:
        run_dry(output_dir=tmp_path, units=1)
        written = sorted(path.name for path in tmp_path.iterdir())
        # The replays and nothing else: the observation audit, which restates
        # the prefix packet by packet, goes to the null device instead.
        assert written == [
            "combined_accounts-seed-3000.jsonl",
            "repaired_clock-seed-3000.jsonl",
        ]

    def test_the_dry_run_provider_reads_only_its_prompt(self) -> None:
        """It has no roster, no roles and no prefix: with no candidate block in
        the prompt it abstains rather than inventing a target."""

        import asyncio

        from meetings.schemas import ModelAuthoredVoteBallot

        provider = DryRunProvider()
        response = asyncio.run(
            provider.complete(
                prompt="nothing useful here",
                schema=ModelAuthoredVoteBallot,
                max_tokens=1024,
                temperature=0.2,
                agent_id="p-1",
            )
        )
        ballot = ModelAuthoredVoteBallot.model_validate_json(response.text)
        assert ballot.target == "SKIP"
        assert ballot.primary_reason_id is None

    def test_the_cli_dry_run_writes_its_report(self, tmp_path: Path) -> None:
        destination = tmp_path / "report.json"
        assert (
            instrument.main(
                [
                    "--dry-run",
                    "--units",
                    "1",
                    "--output-dir",
                    str(tmp_path / "runs"),
                    "--json",
                    str(destination),
                ]
            )
            == 0
        )
        payload = json.loads(destination.read_text(encoding="utf-8"))
        assert payload["provider"] == "fake"
        assert payload["total_cost_usd"] == 0.0

    def test_the_cli_refuses_a_live_provider_without_the_two_flags(self) -> None:
        with pytest.raises(SystemExit):
            instrument.main(["--provider", AUTHORIZED_PROVIDER])


class TestAuthorizedConstants:
    def test_the_per_call_caps_are_the_shipped_defaults(self) -> None:
        from meetings.manager import DEFAULT_TURN_MAX_TOKENS, DEFAULT_VOTE_MAX_TOKENS

        assert instrument.AUTHORIZED_TURN_MAX_TOKENS == DEFAULT_TURN_MAX_TOKENS
        assert instrument.AUTHORIZED_VOTE_MAX_TOKENS == DEFAULT_VOTE_MAX_TOKENS
        # And the numbers the manifest names, so a moved shipped default breaks
        # this rather than moving what the owner authorized.
        assert (DEFAULT_TURN_MAX_TOKENS, DEFAULT_VOTE_MAX_TOKENS) == (2048, 1024)

    def test_the_sampling_temperatures_are_the_shipped_defaults(self) -> None:
        """The manifest binds the sampling configuration, so the run may not
        inherit it. The constants are written as numbers and checked against the
        shipped ones here: a change to `meetings.manager` then turns this red
        instead of quietly moving a frozen design's draw."""

        from meetings.manager import DEFAULT_TURN_TEMPERATURE, DEFAULT_VOTE_TEMPERATURE

        assert AUTHORIZED_SAMPLING.turn_temperature == DEFAULT_TURN_TEMPERATURE
        assert AUTHORIZED_SAMPLING.vote_temperature == DEFAULT_VOTE_TEMPERATURE
        assert (
            AUTHORIZED_SAMPLING.turn_temperature,
            AUTHORIZED_SAMPLING.vote_temperature,
        ) == (0.4, 0.2)

    def test_the_served_meeting_config_carries_the_authorized_sampling(self) -> None:
        """Passed, not defaulted — and passed with the HEADLESS deadlines, since
        any explicit config would otherwise opt this run into the interactive
        30 s per-turn wall."""

        from orchestrator.game import HEADLESS_MEETING_DEADLINES

        config = AUTHORIZED_SAMPLING.meeting_config()
        assert config.turn_temperature == AUTHORIZED_SAMPLING.turn_temperature
        assert config.vote_temperature == AUTHORIZED_SAMPLING.vote_temperature
        assert config.turn_max_tokens == AUTHORIZED_SAMPLING.turn_max_tokens
        assert config.vote_max_tokens == AUTHORIZED_SAMPLING.vote_max_tokens
        assert config.deadlines == HEADLESS_MEETING_DEADLINES

    def test_the_report_records_the_sampling_it_drew_at(self, tmp_path: Path) -> None:
        report = run_instrument(output_dir=tmp_path, units=1)
        assert report.sampling == AUTHORIZED_SAMPLING

    def test_the_run_serves_the_authorized_meeting_config(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The wiring, not the value: every unit's runner must be built WITH the
        authorized configuration, or the meeting layer defaults it and the
        manifest's binding is decoration."""

        from orchestrator.game import build_default_meeting_runner

        served: list[Any] = []
        real = build_default_meeting_runner

        def spy(**kwargs: Any) -> Any:
            served.append(kwargs.get("config"))
            return real(**kwargs)

        monkeypatch.setattr(instrument, "build_default_meeting_runner", spy)
        run_instrument(output_dir=tmp_path, units=1)
        assert served == [AUTHORIZED_SAMPLING.meeting_config()] * 2

    def test_the_limits_object_is_the_authorized_numbers(self) -> None:
        assert AUTHORIZED_LIMITS == RunLimits(
            run_max_input_tokens=2_400_000,
            run_max_output_tokens=200_000,
            unit_max_input_tokens=45_000,
            unit_max_output_tokens=4_000,
            max_cost_usd=0.0,
            elapsed_seconds=6 * 60 * 60,
            model_work_seconds=4 * 60 * 60,
        )

    def test_the_arms_run_the_clock_the_freeze_screened_under(self) -> None:
        for arm in instrument_arms():
            assert arm.temporal_version == TEMPORAL_OBSERVATION_VERSION
