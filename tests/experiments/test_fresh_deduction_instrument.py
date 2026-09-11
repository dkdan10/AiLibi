"""Tests for experiments/fresh_deduction_instrument.py.

The fake provider is the only provider anything here reaches. Three properties
hold that, and each is tested rather than asserted: the live gate refuses every
other provider without an explicit invocation AND refuses a client whose real
type does not match the label it was given; this file carries no occurrence of
the instrument's live-run flag, so the tree scan below covers it like every
other committed file; and the one function that builds a real client cannot even
be called before the frozen set is verified. Invocations ARE constructed here —
proving each refusal is what they are for — and none of them is ever handed to a
provider.

Each guard the instrument adds is paired with a planted or perturbed case that
fails on the defect the guard claims to catch — a moved digest, a changed skip
list, a call over the cap, a truncated response, an exhausted budget, an expired
deadline, a model-work window that has to bite while a call is still in flight,
a mislabelled clock, a citation the voter never saw, a citation about somebody
other than the player it was cast against, a meeting whose turns or ballots all
fell back to the layer's defaults, a call the provider billed and then refused
on its own schema validation, a leaked prefix step and a planted body handle.
"""

from __future__ import annotations

import ast
import asyncio
import hashlib
import json
import re
import subprocess
import time
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any, Final, cast

import pytest
from pydantic import BaseModel, ValidationError

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
    CONVERTED_BANDS,
    LEGACY_BODY_HANDLE_PATTERN,
    MANIFEST_PATH,
    PREREGISTERED_BAND,
    TEMPORAL_OBSERVATION_VERSION,
    HeldOutPrefixError,
    assert_no_legacy_body_handles,
    canonical_prefix_json,
)
from llm.budget import BudgetExceededError, GameBudget
from llm.client import CallKind, LLMResponse, TokenUsage
from meetings.manager import DefaultedCall
from meetings.schemas import (
    AccusationClaim,
    MeetingTurn,
    ModelAuthoredVoteBallot,
    VoteBallot,
)

# The PRODUCER of the ``deadline_default`` message the instrument classifies.
# Imported private on purpose: pinning the counter's regex against a copy of the
# wording would pin it against itself, and the ``deadline`` trigger is
# interactive-only, so no headless test can reach it end to end.
from orchestrator.game import _deadline_default_message
from orchestrator.replay import (
    FailedCallReplayEntry,
    MeetingReplayEntry,
    read_all_entries,
)
from orchestrator.run_limits import RunDeadlineExceeded
from tests.experiments import burned_call_double
from tests.experiments.burned_call_double import (
    BURNED_INPUT_TOKENS,
    BURNED_OUTPUT_TOKENS,
    BurnedCallProvider,
)

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
_MANIFEST: Final[Path] = _REPO_ROOT / EXECUTION_MANIFEST_PATH
_INSTRUMENT_SOURCE: Final[Path] = (
    _REPO_ROOT / "experiments" / "fresh_deduction_instrument.py"
)

#: How many units a test that only needs the pipeline to turn over should run.
#: Two prefixes is enough for a paired comparison and keeps these tests fast;
#: the full 50 runs once, in the dry-run test.
_SMOKE_UNITS: Final[int] = 2

#: The commit that first bound the execution manifest. Every later change to a
#: frozen-analysis constant is an amendment to a document that already existed,
#: so it belongs in the manifest's amendment log; the commit that introduced the
#: constants is the freeze itself and is an ancestor of this one.
_MANIFEST_FREEZE_COMMIT: Final[str] = "87c4ef3d"

#: What "the frozen analysis" means for the amendment walk: the constants this
#: manifest quotes as the design it binds before any outcome exists. A change to
#: any of them after the freeze moves what a result would MEAN.
_FROZEN_ANALYSIS_CONSTANTS: Final[tuple[str, ...]] = (
    "AUTHORIZED_SAMPLING",
    "CITATION_RELEVANCE_RUBRIC",
    "DECISION_ALPHA",
    "DECISION_RULE",
    "MINIMUM_ACTIONABLE_EFFECT_RATIONALE",
    "MINIMUM_ACTIONABLE_EFFECT_UNITS",
    "PRIMARY_OUTCOME",
    "PRIMARY_OUTCOME_RUBRIC",
    "PRIVILEGED_RUBRIC",
    "STOP_RULE",
    "SUPPORTED_RUBRIC",
    "WRONGFUL_EJECTION_TRADEOFF",
)

_INSTRUMENT_REPO_PATH: Final[str] = "experiments/fresh_deduction_instrument.py"


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _frozen_analysis_at(revision: str) -> dict[str, str] | None:
    """The frozen-analysis constants as one revision of the module defines them.

    Parsed, never imported: the point is to read a revision that is not the one
    running, and executing an arbitrary past revision to read four strings off it
    would be a worse idea than parsing it. ``None`` when the module does not
    exist at that revision.
    """

    shown = _git("show", f"{revision}:{_INSTRUMENT_REPO_PATH}")
    if shown.returncode != 0:
        return None
    values: dict[str, str] = {}
    for node in ast.parse(shown.stdout).body:
        target: str | None = None
        bound: ast.expr | None = None
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target, bound = node.target.id, node.value
        elif (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):
            target, bound = node.targets[0].id, node.value
        if target in _FROZEN_ANALYSIS_CONSTANTS and bound is not None:
            values[target] = ast.unparse(bound)
    return values


def _frozen_analysis_amendments() -> dict[str, list[str]] | None:
    """``{abbreviated commit: the constants it moved}`` since the manifest froze.

    ``None`` with no usable history — a shallow clone or a missing git — the way
    ``tests/scripts/test_check_doc_facts.py`` handles the same problem: a
    truncated log would report an empty amendment set and pass vacuously, so the
    caller skips rather than passes.
    """

    shallow = _git("rev-parse", "--is-shallow-repository")
    if shallow.returncode != 0 or shallow.stdout.strip() != "false":
        return None
    if _git(
        "rev-parse", "--verify", f"{_MANIFEST_FREEZE_COMMIT}^{{commit}}"
    ).returncode:
        return None
    listed = _git(
        "log",
        "--format=%h",
        f"{_MANIFEST_FREEZE_COMMIT}..HEAD",
        "--",
        _INSTRUMENT_REPO_PATH,
    )
    if listed.returncode != 0:
        return None
    amendments: dict[str, list[str]] = {}
    for commit in listed.stdout.split():
        before = _frozen_analysis_at(f"{commit}^") or {}
        after = _frozen_analysis_at(commit) or {}
        moved = [
            name
            for name in _FROZEN_ANALYSIS_CONSTANTS
            if before.get(name) != after.get(name)
        ]
        if moved:
            amendments[commit] = moved
    return amendments


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


def _converted_manifest_paths() -> tuple[Path, ...]:
    """Every freeze record that has been converted to development data.

    A converted band keeps its record beside the live one under its own name
    (``experiments.held_out_prefixes.CONVERTED_BANDS``). The execution manifest
    binds the live freeze; these records are what it may bind INSTEAD while a
    re-binding is an open obligation, which is the state the binding tests below
    allow and bound.
    """

    return tuple(_REPO_ROOT / converted.manifest_path for converted in CONVERTED_BANDS)


def _first_accepted_seed() -> int:
    """The first seed of the committed freeze; the unit files are named for it.

    Derived rather than written down: the band has moved once already -- the
    3000-3999 set became development data on 2026-09-10 and 5000-5999 was
    frozen in its place -- and a literal here would only re-pin these names to
    whichever band was current when it was typed.
    """

    accepted = _committed_manifest()["accepted"]
    assert isinstance(accepted, list)
    return int(accepted[0]["seed"])


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


class _InvalidTurnProvider(DryRunProvider):
    """A dry-run provider whose TURN payloads never satisfy the schema.

    The meeting layer's fail-soft substitutes a placeholder turn for each one,
    so the unit resolves with no model-authored turn in it at all — the case
    that used to reach the report as a complete, fully supported unit.
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
        if schema is MeetingTurn:
            return LLMResponse(
                text='{"this": "is not a turn"}',
                usage=TokenUsage(input_tokens=len(prompt) // 4, output_tokens=6),
                cost_usd=0.0,
                model=instrument.DRY_RUN_MODEL,
            )
        return await super().complete(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
            agent_id=agent_id,
        )


class _InvalidBallotProvider(DryRunProvider):
    """A dry-run provider whose FIRST ballot payload fails validation.

    The manager degrades it to a marked SKIP, which reaches the ballot verdicts
    as one more abstention: without a separate count it is indistinguishable
    from a voter who chose to abstain.
    """

    def __init__(self) -> None:
        super().__init__()
        self.ballots = 0

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
        if schema is ModelAuthoredVoteBallot:
            self.ballots += 1
            if self.ballots == 1:
                return LLMResponse(
                    text='{"not_a_ballot": true}',
                    usage=TokenUsage(input_tokens=len(prompt) // 4, output_tokens=6),
                    cost_usd=0.0,
                    model=instrument.DRY_RUN_MODEL,
                )
        return await super().complete(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
            agent_id=agent_id,
        )


class _PositionlessOpeningProvider(DryRunProvider):
    """A dry-run provider whose OPENING takes no position, on both attempts.

    DESIGN.md §5.2 PHASE 1 requires an opening to accuse or say "unsure"; an
    opening that parses but does neither is the Task 10.6 validation-DEGRADE,
    rebuilt as an unsure turn and annotated `opening_degraded_unsure`. Every
    later turn is the ordinary dry-run one.
    """

    def __init__(self) -> None:
        super().__init__()
        self.turns = 0

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
        if schema is MeetingTurn:
            self.turns += 1
            # The opening gets one retry, so both of its attempts must be
            # position-less for the degrade rather than a plain default to fire.
            if self.turns <= 2:
                payload = MeetingTurn.model_validate(
                    {
                        "turn_id": "dry-run",
                        "turn_index": 0,
                        "speaker": agent_id or "p-1",
                        "turn_kind": "opening",
                        "reply_to": None,
                        "observations": [],
                        "claims": [],
                        "free_text": "I spent the round finishing my own tasks.",
                    }
                )
                text = payload.model_dump_json()
                return LLMResponse(
                    text=text,
                    usage=TokenUsage(
                        input_tokens=max(1, len(prompt) // 4),
                        output_tokens=max(1, len(text) // 4),
                    ),
                    cost_usd=0.0,
                    model=instrument.DRY_RUN_MODEL,
                )
        return await super().complete(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
            agent_id=agent_id,
        )


class _SlowProvider:
    """A client whose single call stays in flight far longer than the window."""

    def __init__(self, *, seconds: float) -> None:
        self.seconds = seconds
        self.finished = 0

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
        await asyncio.sleep(self.seconds)
        self.finished += 1
        return LLMResponse(
            text="{}",
            usage=TokenUsage(input_tokens=1, output_tokens=1),
            cost_usd=0.0,
            model="slow",
        )


class _TimingOutProvider:
    """A client that raises its OWN ``TimeoutError``, not the window's."""

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
        raise TimeoutError("the provider's own read timeout")


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
        """The set the run would use is the one the committed manifest records.

        The seeds are read from that manifest rather than written down here: a
        literal would pin this test to one band, and the band moves when a
        result converts a set to development data.
        """

        manifest = _committed_manifest()
        accepted = manifest["accepted"]
        skipped = manifest["skipped"]
        assert isinstance(accepted, list)
        assert isinstance(skipped, list)
        frozen = verify_frozen_set(_REPO_ROOT)
        assert frozen.accepted_seeds == tuple(int(row["seed"]) for row in accepted)
        assert frozen.skipped_seeds == tuple(int(row["seed"]) for row in skipped)
        assert len(frozen.accepted_seeds) == 50
        assert len(frozen.prefixes) == 50
        assert frozen.accepted_seeds[0] >= PREREGISTERED_BAND.first_seed
        assert list(frozen.accepted_seeds) == sorted(set(frozen.accepted_seeds))

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

    @pytest.mark.parametrize("block", ["accepted", "skipped"])
    def test_a_manifest_missing_a_row_block_is_a_named_stop(
        self, tmp_path: Path, block: str
    ) -> None:
        """PLANTED: the block removed. This used to be a bare `KeyError` — an
        unnamed crash where the stop rule promises a refusal that says what
        differed."""

        manifest = _committed_manifest()
        del manifest[block]
        _write_frozen_manifest(tmp_path, manifest)
        with pytest.raises(FrozenSetMismatch, match=f"no {block!r} block"):
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

    def test_the_cli_live_path_is_unreachable_without_the_runners_own_flag(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A live provider named on the command line, without the runner's flag,
        is refused by the parser before anything is constructed.

        This suite never passes that flag — the tree scan below is what keeps it
        that way — so this is as far as a test may drive the live branch. The
        client factory is replaced by a landmine first, so even a CLI perturbed
        to skip the flag check cannot construct a provider from here.
        """

        def landmine(*args: Any, **kwargs: Any) -> Any:
            raise AssertionError("a client was constructed by the test suite")

        monkeypatch.setattr(instrument, "build_authorized_client", landmine)
        with pytest.raises(SystemExit) as caught:
            instrument.main(
                [
                    "--provider",
                    AUTHORIZED_PROVIDER,
                    "--execution-manifest",
                    str(_MANIFEST),
                    "--output-dir",
                    str(tmp_path),
                ]
            )
        assert caught.value.code == 2

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

    def test_no_committed_file_outside_the_module_and_the_manifest_names_the_flag(
        self,
    ) -> None:
        """The live flag exists in exactly two committed places: the module that
        defines it and the manifest's documented command. A third — a test, a
        script, a workflow, a card — would be a path to a call nobody chose.

        Two things make this scan cover THIS file as well. The needle is
        ``instrument.LIVE_RUN_FLAG`` itself rather than a second copy of the
        string, so looking for it writes no occurrence of it here; and the file
        list is every tracked file with a suffix a command could be written in,
        taken from the git index rather than from a hand-kept list of roots, so
        ``tasks/``, the repository root and everything else are in it. The
        count assertion keeps a listing failure from passing vacuously.
        """

        listed = subprocess.run(
            ["git", "ls-files"],
            cwd=_REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()
        searchable = {".py", ".sh", ".yml", ".yaml", ".md", ".j2", ".toml", ".txt"}
        allowed = {
            "experiments/fresh_deduction_instrument.py",
            EXECUTION_MANIFEST_PATH,
        }
        candidates = [
            name
            for name in listed
            if Path(name).suffix in searchable and name not in allowed
        ]
        assert len(candidates) > 1000, "the tracked-file listing came back short"
        offenders = [
            name
            for name in candidates
            if instrument.LIVE_RUN_FLAG
            in (_REPO_ROOT / name).read_text(encoding="utf-8", errors="ignore")
        ]
        assert offenders == []

    def test_this_test_module_neither_names_the_flag_nor_builds_a_client(self) -> None:
        """The scan above needs no exemption for this file, and this is why.

        No occurrence of the flag, and no import of the real client factory: the
        two ways a test file could become a path to a live call.

        The burned-call double beside this file is held to the same line rather
        than exempted from it. It has to reach `llm.provider` — the burned spend
        rides an exception attribute that module owns, and copying the attribute
        name would pin the double against a copy of the seam instead of the seam
        — so what it may take from `llm.provider` is enumerated: the failure
        model and the attach helper, and nothing that builds a client.
        """

        source = Path(__file__).read_text(encoding="utf-8")
        assert instrument.LIVE_RUN_FLAG not in source
        assert re.search(r"^\s*(?:from|import)\s+llm\.provider", source, re.M) is None

        double = Path(burned_call_double.__file__).read_text(encoding="utf-8")
        assert instrument.LIVE_RUN_FLAG not in double
        assert re.search(r"^\s*import\s+llm\.provider", double, re.M) is None
        taken = {
            alias.name
            for node in ast.parse(double).body
            if isinstance(node, ast.ImportFrom) and node.module == "llm.provider"
            for alias in node.names
        }
        assert taken == {"LLMCallFailure", "_attach_parse_failure"}


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
            instrument.build_authorized_client(
                verify_frozen_set(_REPO_ROOT), env={"AILIBI_LLM_PROVIDER": "fake"}
            )

    def test_the_default_environment_is_the_process_one_and_still_pinned(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("AILIBI_LLM_PROVIDER", "fake")
        monkeypatch.delenv("FEATHERLESS_API_KEY", raising=False)
        with pytest.raises(LiveRunNotAuthorized, match="FEATHERLESS_API_KEY"):
            instrument.build_authorized_client(verify_frozen_set(_REPO_ROOT))

    def test_a_client_cannot_be_built_before_the_frozen_set_is_verified(self) -> None:
        """PLANTED: the round-3 defect — the CLI evaluated the client factory in
        an argument list, so a run whose held-out set had moved constructed a
        provider before anything checked the set.

        The verified `FrozenSet` is now a required argument and `verify_frozen_set`
        is its only producer, so the ordering is a property of the signature: the
        call below does not type-check and does not run, and no client is built.
        """

        build = cast(Callable[..., object], instrument.build_authorized_client)
        with pytest.raises(TypeError, match="frozen"):
            build(env={"FEATHERLESS_API_KEY": "unused"})

    def test_the_pre_client_gate_stops_on_a_moved_frozen_set(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: a repository root whose execution manifest is the committed
        one and whose held-out manifest carries a moved digest. The readiness
        gate refuses there, which is BEFORE the client the CLI builds from its
        return value exists — the gate itself constructs none."""

        manifest = tmp_path / EXECUTION_MANIFEST_PATH
        manifest.parent.mkdir(parents=True)
        manifest.write_text(_MANIFEST.read_text(encoding="utf-8"), encoding="utf-8")
        moved = _committed_manifest()
        moved["accepted"][0]["sha256"] = "0" * 64
        _write_frozen_manifest(tmp_path, moved)
        invocation = LiveRunInvocation.naming(
            manifest,
            provider=AUTHORIZED_PROVIDER,
            model=AUTHORIZED_MODEL,
            repo_root=tmp_path,
        )
        with pytest.raises(FrozenSetMismatch, match="accepted prefixes"):
            instrument.assert_ready_for_a_live_run(
                provider=AUTHORIZED_PROVIDER,
                invocation=invocation,
                repo_root=tmp_path,
            )

    def test_the_pre_client_gate_returns_the_verified_set(self) -> None:
        """The positive half: on the committed tree it hands back the set the
        client is then built against, so the two cannot come apart."""

        invocation = LiveRunInvocation.naming(
            _MANIFEST, provider=AUTHORIZED_PROVIDER, model=AUTHORIZED_MODEL
        )
        frozen = instrument.assert_ready_for_a_live_run(
            provider=AUTHORIZED_PROVIDER, invocation=invocation
        )
        assert len(frozen.accepted_seeds) == 50


class TestTheManifestBindsTheBandTheRunWouldDraw:
    """The authorization document and the inputs, held together at run time.

    `verify_frozen_set` regenerates whatever record sits at `MANIFEST_PATH` and
    holds it to the generator's own `PREREGISTERED_BAND`; neither reads the
    execution manifest. So when the 3000-3999 band became development data on
    2026-09-10 and 5000-5999 was frozen in its place, the manifest went on
    authorizing a band the runner would no longer draw, with every other gate
    green. Nothing but the re-binding closed that, and a document is not a gate.
    """

    def _planted_root(self, root: Path, *, band: tuple[int, int]) -> Path:
        """A repository root whose Inputs row names `band` and whose freeze
        record is the committed one. Everything else is the committed document,
        so the digest and the required-string checks above this one all pass."""

        manifest = root / EXECUTION_MANIFEST_PATH
        manifest.parent.mkdir(parents=True, exist_ok=True)
        text = re.sub(
            r"^(\|\s*Seed band\s*\|\s*)\d+–\d+",
            rf"\g<1>{band[0]}–{band[1]}",
            _MANIFEST.read_text(encoding="utf-8"),
            count=1,
            flags=re.MULTILINE,
        )
        manifest.write_text(text, encoding="utf-8")
        _write_frozen_manifest(root, _committed_manifest())
        return manifest

    def test_the_committed_manifest_binds_the_live_band(self) -> None:
        """The settled state: the Inputs row and the freeze record agree."""

        record_band = _committed_manifest()["band"]
        assert instrument.manifest_bound_band(
            _MANIFEST.read_text(encoding="utf-8")
        ) == (record_band["first_seed"], record_band["last_seed"])
        instrument.assert_manifest_binds_the_live_band()

    def test_a_stale_binding_stops_the_run_before_a_client_exists(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: the exact state this branch inherited — an Inputs row naming
        the converted 3000-3999 band while the live record holds 5000-5999.

        The refusal comes out of `assert_ready_for_a_live_run`, which is the
        call the CLI makes before it builds anything: the gate constructs no
        client, and `LiveRunNotAuthorized` names both bands so the reader is
        told which document to move rather than which check to delete.
        """

        converted = CONVERTED_BANDS[0].band
        manifest = self._planted_root(
            tmp_path, band=(converted.first_seed, converted.last_seed)
        )
        invocation = LiveRunInvocation.naming(
            manifest,
            provider=AUTHORIZED_PROVIDER,
            model=AUTHORIZED_MODEL,
            repo_root=tmp_path,
        )
        with pytest.raises(LiveRunNotAuthorized) as refused:
            instrument.assert_ready_for_a_live_run(
                provider=AUTHORIZED_PROVIDER,
                invocation=invocation,
                repo_root=tmp_path,
            )
        message = str(refused.value)
        assert (
            f"binds seed band {converted.first_seed}-{converted.last_seed}" in message
        )
        assert f"holds {PREREGISTERED_BAND.first_seed}-" in message

    def test_a_dry_run_is_not_gated_on_the_binding(self, tmp_path: Path) -> None:
        """The fake path takes no invocation and spends nothing, so a stale
        binding is not its business: it returns before this check, and the run
        that would spend the wrong band is the only one refused."""

        self._planted_root(tmp_path, band=(1, 2))
        instrument.assert_live_run_is_authorized(
            provider="fake", invocation=None, repo_root=tmp_path
        )

    @pytest.mark.parametrize("rows", [0, 2])
    def test_a_document_that_does_not_say_which_band_is_refused(
        self, rows: int
    ) -> None:
        """PLANTED both ways: a manifest with no Seed band row, and one with two.

        Neither states which inputs the owner authorized, and resolving the
        ambiguity by taking the first row would let a second row be added
        without a reader ever seeing the run change bands.
        """

        text = _MANIFEST.read_text(encoding="utf-8")
        row = re.search(r"^\|\s*Seed band\s*\|.*$", text, re.MULTILINE)
        assert row is not None
        planted = text.replace(
            row.group(0), "" if rows == 0 else f"{row.group(0)}\n{row.group(0)}"
        )
        with pytest.raises(LiveRunNotAuthorized, match=f"carries {rows} 'Seed band'"):
            instrument.manifest_bound_band(planted)

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


class TestClientType:
    """The gate reads the client's real type, not the provider label it was told.

    A label is not a client. `provider="fake"` with a metered client handed in
    would reach that provider with every other refusal in the module satisfied,
    and a live label served by the offline fixture would write a report labelled
    live that no model authored.
    """

    def test_a_non_fake_client_labelled_fake_is_refused_before_any_call(
        self, tmp_path: Path
    ) -> None:
        # PLANTED: the label says fake; the client is not the offline provider.
        client = _StubClient()
        with pytest.raises(LiveRunNotAuthorized, match="not the offline fake"):
            run_instrument(output_dir=tmp_path, client=client, provider="fake")
        assert client.calls == 0

    def test_a_fake_client_on_a_live_label_is_refused(self) -> None:
        # PLANTED: a live-labelled run served by the fixture, which would record
        # `dry_run: false` over output no model wrote.
        with pytest.raises(LiveRunNotAuthorized, match="offline fake provider"):
            instrument.assert_client_matches_provider(
                provider=AUTHORIZED_PROVIDER, client=DryRunProvider()
            )

    def test_a_live_label_with_no_client_at_all_is_refused(self) -> None:
        """`None` is the dry-run fallback, so it is a fake by another name."""

        with pytest.raises(LiveRunNotAuthorized, match="no client"):
            instrument.assert_client_matches_provider(
                provider=AUTHORIZED_PROVIDER, client=None
            )

    def test_the_offline_providers_and_their_subclasses_pass(self) -> None:
        for client in (None, DryRunProvider(), _TruncatingProvider()):
            instrument.assert_client_matches_provider(provider="fake", client=client)


class TestPreflightRates:
    """The wrapper exposes the WRAPPED client's USD pre-flight rates.

    `BudgetedLLMClient` reads those rates off whatever it is handed, so a
    hardcoded zero on the wrapper disabled the USD dimension for every client it
    ever composed — including a metered one, whose $0.00 cap would then stop
    nothing.
    """

    def _client(self, inner: Any) -> Any:
        clock = instrument._ModelWorkClock(max_seconds=3600.0)
        return instrument._InstrumentClient(inner, work_clock=clock)

    def test_a_metered_clients_rates_pass_through(self) -> None:
        # PLANTED: a client that bills. Hardcoded zeros made this $0.00.
        class _Metered(_StubClient):
            preflight_cost_per_input_token_usd = 6e-6
            preflight_cost_per_output_token_usd = 30e-6

        client = self._client(_Metered())
        assert client.preflight_cost_per_input_token_usd == 6e-6
        assert client.preflight_cost_per_output_token_usd == 30e-6

    def test_a_client_that_states_no_rates_leaves_the_budget_its_defaults(
        self,
    ) -> None:
        """No rate is stated, so the budget layer applies its own calibrated
        defaults exactly as it would to the unwrapped client."""

        client = self._client(_StubClient())
        assert not hasattr(client, "preflight_cost_per_input_token_usd")

    def test_the_fake_provider_is_free_by_construction(self) -> None:
        """Zero is the honest rate for a client whose `cost_usd` is 0.0 by
        construction — the same statement the authorized provider makes about
        itself (`llm/featherless_client.py:244-245`), which is why the manifest's
        $0.00 cap is bookkeeping on both paths."""

        client = self._client(DryRunProvider())
        assert client.preflight_cost_per_input_token_usd == 0.0
        assert client.preflight_cost_per_output_token_usd == 0.0


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


class TestModelWorkWindow:
    """The 4 h window is a limit on model work, so it has to bind IN FLIGHT.

    Charged only on return it is a one-call-granular limit, and one call on the
    authorized provider is six sends at a 600 s timeout with backoff — close to
    an hour. A run at 3 h 59 m could then spend a fifth hour against an
    authorization of four, with only the separate 6 h elapsed clock behind it.
    """

    def test_the_window_stops_during_the_call_that_exhausts_it(self) -> None:
        """PLANTED: a 0.2 s window and a call that stays in flight for 5 s.

        The stop must arrive while the call is still running. Without the bound
        the same call returns first and the stop lands 5 s later, which is the
        defect: the assertion below is on WHEN it stopped, not that it stopped.
        """

        clock = instrument._ModelWorkClock(max_seconds=0.2)
        inner = _SlowProvider(seconds=5.0)
        client = instrument._InstrumentClient(inner, work_clock=clock)
        started = time.monotonic()
        with pytest.raises(RunDeadlineExceeded, match="exhausted mid-call"):
            asyncio.run(
                client.complete(
                    prompt="p", schema=None, max_tokens=1024, temperature=0.2
                )
            )
        elapsed = time.monotonic() - started
        assert elapsed < 2.0, f"the stop waited for the call: {elapsed:.1f}s"
        assert inner.finished == 0

    def test_the_cut_off_attempt_is_charged_and_reported(self) -> None:
        """The attempt bought no response but held the provider, so its wall is
        on the clock and its call is in the partial accounting — marked, so a
        reader cannot mistake it for a response that arrived."""

        clock = instrument._ModelWorkClock(max_seconds=0.2)
        client = instrument._InstrumentClient(
            _SlowProvider(seconds=5.0), work_clock=clock
        )
        with pytest.raises(RunDeadlineExceeded):
            asyncio.run(
                client.complete(
                    prompt="p", schema=None, max_tokens=1024, temperature=0.2
                )
            )
        usage = instrument.ArmUsage().plus(client.take())
        assert usage.calls == 1
        assert usage.input_tokens == usage.output_tokens == 0
        assert usage.model_work_seconds >= 0.2
        assert clock.seconds >= 0.2

    def test_a_providers_own_timeout_is_not_relabelled_as_the_window(self) -> None:
        """PLANTED: the inner client raises `TimeoutError` with the window wide
        open. A provider timeout is a transport failure, not a limit that was
        reached, and mislabelling it would forge a stop reason."""

        clock = instrument._ModelWorkClock(max_seconds=3600.0)
        client = instrument._InstrumentClient(_TimingOutProvider(), work_clock=clock)
        with pytest.raises(TimeoutError, match="the provider's own read timeout"):
            asyncio.run(
                client.complete(
                    prompt="p", schema=None, max_tokens=1024, temperature=0.2
                )
            )
        assert clock.seconds == 0.0

    def test_a_call_inside_the_window_is_untouched(self) -> None:
        clock = instrument._ModelWorkClock(max_seconds=3600.0)
        inner = _SlowProvider(seconds=0.01)
        client = instrument._InstrumentClient(inner, work_clock=clock)
        asyncio.run(
            client.complete(prompt="p", schema=None, max_tokens=1024, temperature=0.2)
        )
        assert inner.finished == 1
        assert 0.0 < clock.seconds < 1.0


class TestMeetingDefaults:
    """A meeting-internal default is counted, never invisible and never a stop.

    The meeting layer substitutes a placeholder turn or a marked SKIP ballot for
    a payload that failed schema validation (`meetings/manager.py::_default_turn`,
    `_vote_parse_default`, the runaway class accepted at about 1 in 50). The
    preregistration requires missing attempts to remain visible, so the
    instrument reads the `deadline_default` rows the orchestrator records.
    """

    def _entries(self, directory: Path, name: str) -> Sequence[Any]:
        return read_all_entries(directory / name)

    def test_a_clean_unit_records_no_defaults(self, tmp_path: Path) -> None:
        report = run_instrument(output_dir=tmp_path, units=1)
        for arm in report.arms:
            assert arm.defaulted_turns == arm.defaulted_votes == 0
            assert arm.units_with_defaults == 0
            assert arm.degraded_openings == 0

    def test_a_unit_whose_turns_all_defaulted_is_counted_not_hidden(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: every turn payload fails validation, so the meeting holds no
        model-authored turn at all. Before this count the unit reached the report
        as `units 1, ejections 1, supported 3` with nothing saying so."""

        report = run_instrument(
            output_dir=tmp_path, client=_InvalidTurnProvider(), units=1
        )
        for arm in report.arms:
            assert arm.units == 1
            assert arm.defaulted_turns == 3
            assert arm.defaulted_votes == 0
            assert arm.defaults_by_validation == 3
            assert arm.defaults_by_deadline == 0
            assert arm.units_with_defaults == 1

    def test_a_defaulted_ballot_is_counted_apart_from_a_voluntary_abstention(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: the first ballot payload is unparseable. It degrades to a
        marked SKIP, which reaches `ballot_verdicts` as one more abstention; the
        `defaulted_votes` count is what separates the two."""

        report = run_instrument(
            output_dir=tmp_path, client=_InvalidBallotProvider(), units=1
        )
        reference = report.arms[0]
        assert reference.defaulted_votes == 1
        assert reference.defaults_by_validation == 1
        assert reference.defaulted_turns == 0
        assert reference.units_with_defaults == 1

    def test_a_defaulted_unit_still_completes_and_is_not_a_stop(
        self, tmp_path: Path
    ) -> None:
        """The counterpart claim: the run does NOT abort. A fixed 50-unit paired
        sample cannot be abandoned for a substitution the engine is designed to
        make, which is why the stop rule says so explicitly."""

        report = run_instrument(
            output_dir=tmp_path, client=_InvalidBallotProvider(), units=1
        )
        assert [arm.units for arm in report.arms] == [1, 1]
        assert "A meeting-internal default is NOT itself a stop" in report.stop_rule

    def test_a_degraded_opening_is_counted_as_the_degrade_it_was(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: an opening that parses but takes no position, on both of its
        attempts. The manager rebuilds it as an unsure turn — the Task 10.6
        degrade — which keeps the model's observations and is therefore NOT the
        same event as a full placeholder default. The replay carries no
        `degraded` field, so the typed turn annotation is the only seam."""

        report = run_instrument(
            output_dir=tmp_path, client=_PositionlessOpeningProvider(), units=1
        )
        reference = report.arms[0]
        assert reference.degraded_openings == 1
        assert reference.defaulted_turns == 1
        assert reference.defaults_by_validation == 1
        assert reference.units_with_defaults == 1

    def test_a_default_the_counter_cannot_classify_stops_the_run(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: a `deadline_default` row whose message the producer would
        never write. An unclassifiable row means the wording moved and the
        counts are no longer evidence, so it is a stop rather than a zero."""

        run_instrument(output_dir=tmp_path, units=1)
        entries = list(
            self._entries(
                tmp_path, f"repaired_clock-seed-{_first_accepted_seed()}.jsonl"
            )
        )
        meeting = next(e for e in entries if isinstance(e, MeetingReplayEntry))
        foreign = FailedCallReplayEntry(
            game_id="g",
            meeting_id=meeting.meeting_id,
            tick=1,
            model="m",
            prompt_length=0,
            raw_response="",
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.0,
            error_type="deadline_default",
            error_message="something else went wrong",
        )
        with pytest.raises(instrument.InstrumentError, match="cannot classify"):
            instrument.count_defaulted_attempts(
                [*entries, foreign], meeting=meeting, seed=3000
            )

    @pytest.mark.parametrize(
        ("default", "phase", "trigger"),
        [
            (
                DefaultedCall(phase="vote", agent_id="p-1", trigger="validation"),
                "vote",
                "validation",
            ),
            (
                DefaultedCall(phase="vote", agent_id="p-1", trigger="deadline"),
                "vote",
                "deadline",
            ),
            (
                DefaultedCall(
                    phase="opening",
                    agent_id="p-1",
                    trigger="validation",
                    turn_index=0,
                ),
                "turn",
                "validation",
            ),
            (
                DefaultedCall(phase="opt_in", agent_id="p-2", trigger="deadline"),
                "turn",
                "deadline",
            ),
        ],
    )
    def test_the_counter_parses_what_the_producer_writes(
        self, default: DefaultedCall, phase: str, trigger: str
    ) -> None:
        """Pinned against `orchestrator.game._deadline_default_message` itself,
        not against a copy of its wording. The `deadline` trigger is
        interactive-only, so this is the only place it can be covered."""

        message = _deadline_default_message(default)
        vote = instrument._DEFAULTED_VOTE_MESSAGE.match(message)
        turn = instrument._DEFAULTED_TURN_MESSAGE.match(message)
        matched = vote or turn
        assert matched is not None
        assert ("vote" if vote is not None else "turn") == phase
        assert matched.group(1) == trigger


class TestChargedCallAccounting:
    """Every call the provider charged is reconciled, and counted once.

    The run of 2026-09-10 stopped on its first unit of one hundred: the recorded
    spend summed over `MeetingReplayEntry.llm_calls` was 13,263 in / 1,448 out
    against an enforced budget of 15,491 / 2,309, and the 2,228 / 861 gap was
    one paid call whose payload the provider validated and refused before any
    recording client could log it. Both halves of that are gated here — the
    charged failure is counted, and a returned-but-invalid payload whose spend
    `llm_calls` already holds is not counted again.
    """

    def _failed_rows(
        self, directory: Path, name: str
    ) -> tuple[FailedCallReplayEntry, ...]:
        return tuple(
            entry
            for entry in read_all_entries(directory / name)
            if isinstance(entry, FailedCallReplayEntry)
        )

    def test_a_burned_call_is_reconciled_instead_of_stopping_the_run(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: a provider that bills for a ballot and then refuses it, the
        way a real one does. Summing `llm_calls` alone stops this unit on an
        accounting gap; summing every charged call resolves it."""

        provider = BurnedCallProvider()
        report = run_instrument(output_dir=tmp_path, client=provider, units=1)

        assert provider.burned == 1
        assert [arm.units for arm in report.arms] == [1, 1]
        charged = [
            row
            for row in self._failed_rows(
                tmp_path, f"repaired_clock-seed-{_first_accepted_seed()}.jsonl"
            )
            if row.input_tokens or row.output_tokens or row.cost_usd
        ]
        assert len(charged) == 1
        assert (charged[0].input_tokens, charged[0].output_tokens) == (
            BURNED_INPUT_TOKENS,
            BURNED_OUTPUT_TOKENS,
        )
        assert report.arms[0].defaulted_votes == 1

    def test_the_burned_calls_spend_reaches_the_partial_accounting(self) -> None:
        """The client's own ledger, at the seam. A call that raised is absent
        from every `llm_calls` row there will ever be, so a stop that reported
        only returned responses would understate what the run had spent."""

        clock = instrument._ModelWorkClock(max_seconds=3600.0)
        client = instrument._InstrumentClient(BurnedCallProvider(), work_clock=clock)
        with pytest.raises(ValidationError):
            asyncio.run(
                client.complete(
                    prompt="a vote prompt",
                    schema=ModelAuthoredVoteBallot,
                    max_tokens=AUTHORIZED_SAMPLING.vote_max_tokens,
                    temperature=AUTHORIZED_SAMPLING.vote_temperature,
                    agent_id="p-1",
                )
            )
        assert len(client.calls) == 1
        assert client.calls[0].input_tokens == BURNED_INPUT_TOKENS
        assert client.calls[0].output_tokens == BURNED_OUTPUT_TOKENS
        assert clock.seconds == client.calls[0].seconds

    def test_a_stop_after_a_burned_call_reports_that_spend(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: one billed-and-refused ballot, then a transport failure. The
        unit never resolves, so the charged call reaches the report through the
        partial accounting or not at all."""

        provider = BurnedCallProvider(then_transport_failure=True)
        with pytest.raises(InstrumentAborted) as aborted:
            run_instrument(output_dir=tmp_path, client=provider, units=1)
        partial = aborted.value.partial
        assert partial.completed_units == 0
        usage = partial.usage_by_arm["repaired_clock"]
        assert usage.input_tokens >= BURNED_INPUT_TOKENS
        assert usage.output_tokens >= BURNED_OUTPUT_TOKENS
        assert f"{usage.input_tokens} in" in partial.describe()

    def test_a_returned_invalid_payload_is_charged_once(self, tmp_path: Path) -> None:
        """PLANTED double-count: `_InvalidBallotProvider` RETURNS an invalid
        payload with usage, so the recording client logged it and the meeting
        row carries its spend. The orchestrator writes that default as a
        zero-spend marker precisely so it is not charged twice; counting every
        default row regardless of usage would overstate this unit."""

        report = run_instrument(
            output_dir=tmp_path, client=_InvalidBallotProvider(), units=1
        )
        assert report.arms[0].defaulted_votes == 1
        rows = self._failed_rows(
            tmp_path, f"repaired_clock-seed-{_first_accepted_seed()}.jsonl"
        )
        assert rows, "the defaulted ballot must leave a visible row"
        assert all(
            (row.input_tokens, row.output_tokens, row.cost_usd) == (0, 0, 0.0)
            for row in rows
        )

    def test_only_the_rows_that_carry_usage_are_charged_calls(self) -> None:
        """The discriminator, planted row by row: a zero-spend visibility marker
        is not a charged call, a paid attempt is one whatever error type the
        producer stamped on it, and another meeting's row is not this unit's."""

        def row(**overrides: Any) -> FailedCallReplayEntry:
            fields: dict[str, Any] = {
                "game_id": "g",
                "meeting_id": "m",
                "tick": 1,
                "model": "m",
                "prompt_length": 0,
                "raw_response": "",
                "input_tokens": 0,
                "output_tokens": 0,
                "cost_usd": 0.0,
                "error_type": "deadline_default",
                "error_message": "vote defaulted (validation); p-1 submitted no ballot",
            }
            fields.update(overrides)
            return FailedCallReplayEntry(**fields)

        marker = row()
        captured = row(error_type="ValidationError", input_tokens=7, output_tokens=3)
        legacy_default = row(input_tokens=5)
        other_meeting = row(meeting_id="other", input_tokens=9)
        charged = instrument._charged_failed_attempts(
            [marker, captured, legacy_default, other_meeting], meeting_id="m"
        )
        assert charged == (captured, legacy_default)


class TestBurnedCallStopConditions:
    """A refused payload is still a completion, and the stops read it as one.

    Recording a billed-and-refused call is not the same as judging it. Both
    stops the client applies to a response — the truncation cap and the served
    checkpoint — read facts the parse-failure metadata carries, and a body
    truncated at the output cap is precisely the body that then fails schema
    validation, so skipping them on this path would put the usual cause of a
    truncation past the truncation stop.
    """

    def _client(self, inner: Any, *, expected_model: str | None = None) -> Any:
        clock = instrument._ModelWorkClock(max_seconds=3600.0)
        return instrument._InstrumentClient(
            inner, work_clock=clock, expected_model=expected_model
        )

    def _vote(self, client: Any) -> None:
        asyncio.run(
            client.complete(
                prompt="a vote prompt",
                schema=ModelAuthoredVoteBallot,
                max_tokens=AUTHORIZED_SAMPLING.vote_max_tokens,
                temperature=AUTHORIZED_SAMPLING.vote_temperature,
                agent_id="p-1",
            )
        )

    def test_a_burned_call_that_reached_its_output_cap_stops_the_run(self) -> None:
        """PLANTED: the provider bills for a ballot that ran to its 1,024-token
        cap and then refuses the truncated body. Without the cap check on this
        path the meeting fail-softs the `ValidationError` to a SKIP and the run
        carries on with a truncation in its evidence."""

        provider = BurnedCallProvider(output_tokens=AUTHORIZED_SAMPLING.vote_max_tokens)
        client = self._client(provider)
        with pytest.raises(PerCallCapExceeded, match="a truncation is a stop"):
            self._vote(client)
        assert [call.output_tokens for call in client.calls] == [
            AUTHORIZED_SAMPLING.vote_max_tokens
        ]

    def test_a_burned_call_under_its_output_cap_is_not_a_truncation(self) -> None:
        """The boundary the other way: one token under the cap is a refused
        payload and nothing more, so it raises the provider's own error."""

        client = self._client(
            BurnedCallProvider(output_tokens=AUTHORIZED_SAMPLING.vote_max_tokens - 1)
        )
        with pytest.raises(ValidationError):
            self._vote(client)

    def test_a_burned_call_from_another_checkpoint_stops_the_run(self) -> None:
        """PLANTED: the endpoint bills for a ballot, refuses it, and names a
        checkpoint this run is not authorized for. Reported rather than stopped,
        that model id would reach `InstrumentReport.model_ids` after the whole
        run had been spent."""

        client = self._client(
            BurnedCallProvider(served_model="some-other-checkpoint"),
            expected_model=AUTHORIZED_MODEL,
        )
        with pytest.raises(
            instrument.ProviderIdentityMismatch, match="some-other-checkpoint"
        ):
            self._vote(client)
        # Recorded first, like every other stop in this client: the endpoint
        # billed for the attempt whatever it served.
        assert [(call.model, call.input_tokens) for call in client.calls] == [
            ("some-other-checkpoint", BURNED_INPUT_TOKENS)
        ]

    def test_the_burned_call_stop_reaches_the_run(self, tmp_path: Path) -> None:
        """The same truncation through the whole pipeline: a stop with the
        capped call's spend in its partial accounting, not a completed run."""

        provider = BurnedCallProvider(output_tokens=AUTHORIZED_SAMPLING.vote_max_tokens)
        with pytest.raises(InstrumentAborted) as aborted:
            run_instrument(output_dir=tmp_path, client=provider, units=1)
        partial = aborted.value.partial
        assert "a truncation is a stop" in partial.reason
        assert partial.completed_units == 0
        usage = partial.usage_by_arm["repaired_clock"]
        assert usage.output_tokens >= AUTHORIZED_SAMPLING.vote_max_tokens


class TestChargedSpendAgainstCaps:
    """A charge applied without a pre-flight still has to meet the ceiling.

    `llm/budgeted_client.py` charges a refused call's usage off its
    parse-failure metadata AFTER the fact and downgrades the resulting
    `BudgetExceededError` to a note, which the meeting layer then fail-softs. On
    a unit's last call no later pre-flight exists to find that overrun, so
    without the post-unit read-back the per-unit ceiling is crossed and the run
    continues.
    """

    def _arm(self) -> Any:
        return instrument_arms()[0]

    def _budget(self, **caps: Any) -> GameBudget:
        limits: dict[str, Any] = {
            "max_cost_usd": 1.0,
            "max_input_tokens": 1_000,
            "max_output_tokens": 1_000,
        }
        limits.update(caps)
        return GameBudget(**limits)

    def _check(self, budget: GameBudget, *, level: str = "per-unit") -> None:
        instrument._assert_charged_spend_is_within_caps(
            budget, level=level, seed=1, arm=self._arm()
        )

    def _charge_over(self, budget: GameBudget, **spend: Any) -> None:
        """Charge past a cap the way the budgeted client does: the overrun is
        raised AFTER the spend is applied, and that raise is what the failed-call
        path swallows."""

        with pytest.raises(BudgetExceededError):
            budget.charge(
                usage=TokenUsage(
                    input_tokens=spend.get("input_tokens", 0),
                    output_tokens=spend.get("output_tokens", 0),
                ),
                cost_usd=spend.get("cost_usd", 0.0),
            )

    def test_a_budget_inside_its_caps_is_not_a_stop(self) -> None:
        budget = self._budget()
        budget.charge(
            usage=TokenUsage(input_tokens=1_000, output_tokens=1_000), cost_usd=1.0
        )
        # The boundary: charged EQUALS the cap, which the budget's own pre-flight
        # allows, so a read-back that stopped here would refuse a run the
        # authorization permits.
        self._check(budget)

    @pytest.mark.parametrize(
        ("spend", "quoted"),
        [
            ({"input_tokens": 1_001}, "input tokens (1001 charged against a 1000"),
            ({"output_tokens": 1_001}, "output tokens (1001 charged against a 1000"),
            ({"cost_usd": 1.5}, "cost (1.5 USD charged against a 1.0 USD cap)"),
        ],
    )
    def test_a_charge_past_any_cap_stops_the_run(
        self, spend: dict[str, Any], quoted: str
    ) -> None:
        # PLANTED, one dimension at a time: spend the budget recorded and then
        # reported as an overrun nobody acted on.
        budget = self._budget()
        self._charge_over(budget, **spend)
        with pytest.raises(instrument.BudgetExhausted, match=re.escape(quoted)):
            self._check(budget)

    def test_the_run_level_cap_is_read_back_too(self) -> None:
        """A unit inside its own ceiling whose parent is past the run one. The
        per-unit read-back cannot see this, which is why both budgets are read."""

        run_budget = self._budget(max_input_tokens=1_500)
        unit_budget = GameBudget(
            max_cost_usd=1.0,
            max_input_tokens=1_000,
            max_output_tokens=1_000,
            parent=run_budget,
        )
        run_budget.charge(
            usage=TokenUsage(input_tokens=900, output_tokens=0), cost_usd=0.0
        )
        self._charge_over(unit_budget, input_tokens=900)
        self._check(unit_budget)
        with pytest.raises(instrument.BudgetExhausted, match="the run token budget"):
            self._check(run_budget, level="run")

    def test_a_cost_within_the_budgets_own_slack_is_not_a_stop(self) -> None:
        """The USD cap is $0.00 on this run and floats do not add exactly, so
        the read-back tolerates the same millionth of a dollar the budget does —
        otherwise it would stop a run the budget considers inside its cap."""

        budget = self._budget(max_cost_usd=0.0)
        budget.charge(usage=TokenUsage(input_tokens=0, output_tokens=0), cost_usd=1e-9)
        self._check(budget)

    def test_an_overrun_burned_on_a_units_last_call_stops_the_run(
        self, tmp_path: Path
    ) -> None:
        """PLANTED end to end: the provider bills 45,000 input tokens for the
        unit's LAST ballot and then refuses the payload. The charge lands with no
        pre-flight left to refuse it and the unit budget is discarded straight
        after, so the post-unit read-back is the only thing between that overrun
        and a hundred further units."""

        provider = BurnedCallProvider(
            input_tokens=AUTHORIZED_LIMITS.unit_max_input_tokens,
            output_tokens=7,
            burn_on_ballot=instrument.AUTHORIZED_LIVING_VOTERS,
        )
        with pytest.raises(InstrumentAborted) as aborted:
            run_instrument(output_dir=tmp_path, client=provider, units=1)
        partial = aborted.value.partial
        assert provider.burned == 1
        assert partial.completed_units == 0
        assert "the per-unit token budget is exhausted on input tokens" in (
            partial.reason
        )
        assert (
            f"against a {AUTHORIZED_LIMITS.unit_max_input_tokens} cap" in partial.reason
        )
        # The charge the budget applied is also in the client's own ledger, so
        # the accounting the stop reports names the call that crossed the cap
        # rather than only the cap.
        usage = partial.usage_by_arm["repaired_clock"]
        assert usage.input_tokens >= AUTHORIZED_LIMITS.unit_max_input_tokens

    def test_an_overrun_that_only_the_run_budget_can_see_stops_the_run(
        self, tmp_path: Path
    ) -> None:
        """PLANTED end to end at the RUN level: 20,000 burned input tokens leave
        the unit inside its own 45,000 ceiling and the run past a 30,000 one. The
        per-unit read-back is blind to this by construction, so it is the run
        budget's read-back or nothing."""

        starved = AUTHORIZED_LIMITS.model_copy(update={"run_max_input_tokens": 30_000})
        provider = BurnedCallProvider(
            input_tokens=20_000,
            output_tokens=7,
            burn_on_ballot=instrument.AUTHORIZED_LIVING_VOTERS,
        )
        with pytest.raises(InstrumentAborted) as aborted:
            run_instrument(
                output_dir=tmp_path, client=provider, units=1, limits=starved
            )
        partial = aborted.value.partial
        assert provider.burned == 1
        assert "the run token budget is exhausted on input tokens" in partial.reason
        assert "against a 30000 cap" in partial.reason


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

    def _turn(self, **kwargs: Any) -> MeetingTurn:
        payload: dict[str, Any] = {
            "turn_id": "m:turn-0",
            "turn_index": 0,
            "speaker": "p-2",
            "turn_kind": "opening",
            "reply_to": None,
            "free_text": "I was in ELECTRICAL the whole time.",
        }
        payload.update(kwargs)
        return MeetingTurn.model_validate(payload)

    def _record(self, **kwargs: Any) -> Any:
        payload: dict[str, Any] = {
            "seed": 3000,
            "arm": "repaired_clock",
            "meeting_id": "m",
            "outcome": "EJECTED",
            "ejected_player_id": "p-2",
            # The ballot the support grades below describe: the two graders read
            # the same ballots, and the privileged one needs the citations
            # themselves to judge what they are about.
            "ballots": (self._ballot(primary_reason_id="m:turn-0"),),
            "turns": (self._turn(),),
            "roles": {"p-1": "CREWMATE", "p-2": "IMPOSTOR", "p-3": "CREWMATE"},
            "prompts_by_agent": {},
            "calls": (),
            "game_outcome": "CREWMATES",
            "recorded_temporal_version": 2,
            "recorded_experiment_config": None,
            "prompt_versions": {},
            "defaults": instrument.DefaultedAttempts(),
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
            naming_ballots=1,
            off_target_citations=0,
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

    # -- citation relevance: right for THAT reason, not just with a citation --

    def _supported(self, **kwargs: Any) -> tuple[SupportedGrade, ...]:
        payload: dict[str, Any] = {
            "voter": "p-1",
            "target": "p-2",
            "cited_turn_id": "m:turn-0",
            "cited_observation_id": None,
            "verdict": "supported",
            "guard_rewrite_reason": None,
        }
        payload.update(kwargs)
        return (SupportedGrade(**payload),)

    def test_a_citation_about_another_player_is_not_the_primary_outcome(self) -> None:
        """PLANTED: the exact case the presence check could not see — the ballot
        names the impostor and cites a turn that is somebody else's, about
        somebody else. Present in the voter's prompt, so 'supported'; about the
        wrong player, so not right for THAT reason."""

        elsewhere = self._turn(
            speaker="p-3",
            free_text="p-1 was with me in MEDBAY.",
        )
        record = self._record(
            turns=(elsewhere,),
            ballots=(self._ballot(primary_reason_id="m:turn-0"),),
        )
        grade = grade_privileged(record, supported=self._supported())
        assert grade.role_correct is True
        assert grade.supported_correct_ejection is False
        assert (grade.naming_ballots, grade.off_target_citations) == (1, 1)

    def test_a_turn_naming_the_ejected_player_still_scores(self) -> None:
        """The other half of the same gate: a turn somebody else spoke, ABOUT the
        ejected player, is exactly the evidence a voter should cite."""

        accusing = self._turn(
            speaker="p-3",
            claims=(
                AccusationClaim(
                    type="accusation",
                    against="p-2",
                    confidence=0.8,
                    reason="they left ELECTRICAL right after the body was found",
                ),
            ),
            free_text="It was not me.",
        )
        record = self._record(turns=(accusing,))
        grade = grade_privileged(record, supported=self._supported())
        assert grade.supported_correct_ejection is True
        assert grade.off_target_citations == 0

    def test_a_cited_turn_this_meeting_never_recorded_is_off_target(self) -> None:
        record = self._record(
            ballots=(self._ballot(primary_reason_id="m:turn-9"),),
        )
        grade = grade_privileged(
            record, supported=self._supported(cited_turn_id="m:turn-9")
        )
        assert grade.supported_correct_ejection is False

    def test_an_observation_line_naming_the_ejected_player_is_relevant(self) -> None:
        record = self._record(
            ballots=(
                self._ballot(
                    primary_reason_id=None, primary_reason_observation_id="p-1:4:0"
                ),
            ),
            prompts_by_agent={
                "p-1": (
                    "<memory>\n"
                    "[obs p-1:3:0] tick 3: p-3 in MEDBAY.\n"
                    "[obs p-1:4:0] tick 4: p-2 left ELECTRICAL.\n"
                    "</memory>",
                )
            },
        )
        grade = grade_privileged(
            record,
            supported=self._supported(
                cited_turn_id=None, cited_observation_id="p-1:4:0"
            ),
        )
        assert grade.supported_correct_ejection is True

    def test_an_observation_line_about_another_player_is_off_target(self) -> None:
        # PLANTED: the voter cites a real line of its own memory that has
        # nothing to do with the player it voted for.
        record = self._record(
            ballots=(
                self._ballot(
                    primary_reason_id=None, primary_reason_observation_id="p-1:3:0"
                ),
            ),
            prompts_by_agent={
                "p-1": (
                    "<memory>\n"
                    "[obs p-1:3:0] tick 3: p-3 in MEDBAY.\n"
                    "[obs p-1:4:0] tick 4: p-2 left ELECTRICAL.\n"
                    "</memory>",
                )
            },
        )
        grade = grade_privileged(
            record,
            supported=self._supported(
                cited_turn_id=None, cited_observation_id="p-1:3:0"
            ),
        )
        assert grade.supported_correct_ejection is False
        assert grade.off_target_citations == 1

    def test_a_longer_id_is_not_the_player_it_starts_with(self) -> None:
        """PLANTED: a substring match would read `p-10` as naming `p-1`. A ten
        player table is not this roster, but a rule that cannot tell the two
        apart is wrong wherever it is applied."""

        assert instrument._names_player("tick 4: p-10 in MEDBAY.", "p-1") is False
        assert instrument._names_player("tick 4: p-1 in MEDBAY.", "p-1") is True

    def test_relevance_reads_no_role(self) -> None:
        """The rule is public-information-only: the same ballots and turns grade
        the same way whoever the hidden impostor is."""

        record = self._record()
        ballots = list(record.ballots)
        relevance = instrument.grade_citation_relevance(
            ballots,
            subject="p-2",
            turns=record.turns,
            prompts_by_agent=record.prompts_by_agent,
        )
        assert [grade.verdict for grade in relevance] == ["relevant"]

    def test_the_run_path_calls_no_grader(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Judge information cannot reach a listener or a tactic if no grader
        runs while the game does. Every grader is replaced by a landmine and a
        unit is run anyway; the run must complete.

        The landmine list is READ off the module rather than typed here. A
        hand-kept tuple does not grow with the module: round 4 added
        ``grade_citation_relevance`` and the tuple kept naming the other three,
        so a run path that called the new grader passed this gate. The equality
        below is the other half of the mechanism — it fails if a grader is
        renamed out of the ``grade_`` prefix and out of the sweep with it.
        """

        graders = sorted(
            name
            for name, value in vars(instrument).items()
            if name.startswith("grade_") and callable(value)
        )
        assert graders == [
            "grade_citation_relevance",
            "grade_privileged",
            "grade_supported",
            "grade_unit",
        ], graders

        def landmine(*args: Any, **kwargs: Any) -> Any:
            raise AssertionError("a grader ran inside the run path")

        for name in graders:
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
            "primary_outcome_rubric",
            "citation_relevance_rubric",
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

    def _enforcement_section(self) -> str:
        text = self._text()
        start = text.index("### How each limit is enforced")
        return text[start : text.index("\n### ", start + 1)]

    def test_the_enforcement_section_claims_no_stop_the_stop_rule_omits(self) -> None:
        """The two lists have to be one list.

        This section used to end its token-budget bullet with "a difference is
        a stop", naming a stop condition `STOP_RULE` does not carry — and the
        run of 2026-09-10 was then stopped by a rule the frozen analysis never
        stated. The bullet now quotes `SPEND_RECONCILIATION` verbatim, which is
        the same string the reconciliation's own module states, so the code's
        account of the check and this document's cannot drift apart.
        """

        section = " ".join(self._enforcement_section().split())
        assert " ".join(instrument.SPEND_RECONCILIATION.split()) in section
        assert "a difference is a stop" not in section

    def test_the_enforcement_section_quotes_the_budget_read_back(self) -> None:
        """The other direction of the same requirement: a stop `STOP_RULE`
        carries has to be one the code applies. "A token budget exhausted at
        either the per-unit or the run level" is a stop, and a charge applied
        without a pre-flight to refuse it — a billed-and-refused call on a
        unit's last ballot — reaches no pre-flight at all, so the bullet states
        the post-unit read-back that does, in the module's own words."""

        section = " ".join(self._enforcement_section().split())
        assert " ".join(instrument.BUDGET_CAP_READBACK.split()) in section

    def test_the_enforcement_section_applies_both_response_stops_to_a_refusal(
        self,
    ) -> None:
        """The truncation and identity stops read a completion, not a parse.

        Both used to be described — and applied — on the success path only,
        which put a body truncated at the output cap past the truncation stop:
        a cut-off body is the usual reason a payload then fails schema
        validation, and the meeting layer fail-softs that failure."""

        section = " ".join(self._enforcement_section().split())
        assert "off the `model` its parse-failure metadata carries" in section
        assert (
            "the same check is applied to the `output_tokens` a refused call's "
            "parse-failure metadata reports" in section
        )

    def test_the_manifest_quotes_the_grading_rubrics_verbatim(self) -> None:
        """The primary outcome and the relevance rule are what a result means, so
        the manifest carries them word for word rather than in paraphrase."""

        text = " ".join(self._text().split())
        assert " ".join(instrument.PRIMARY_OUTCOME_RUBRIC.split()) in text
        assert " ".join(instrument.CITATION_RELEVANCE_RUBRIC.split()) in text

    def _amendments_section(self) -> str:
        text = self._text()
        start = text.index("## Amendments before first run")
        return text[start : text.index("\n## ", start + 1)]

    @pytest.mark.parametrize(
        ("commit", "subject"),
        [
            ("2dde0c91", "the decision rule gains its third condition"),
            ("bfd5696b", "a meeting-internal default is counted, not"),
            ("3a02ede8", "citation relevance joins the primary outcome"),
        ],
    )
    def test_the_manifest_dates_each_amendment(self, commit: str, subject: str) -> None:
        """A preregistration may be amended before results exist, and only if the
        amendment is on the record with its date, its commit and its reason.

        One entry per amendment, each naming the commit that carried it, so a
        reader reconstructing the frozen design from this document can walk to
        the bytes that moved it.
        """

        section = self._amendments_section()
        assert f"**2026-09-09 (`{commit}`) — {subject}" in section

    def test_the_amendment_log_names_every_commit_that_moved_the_frozen_analysis(
        self,
    ) -> None:
        """The log's completeness is checked rather than asserted.

        "Every amendment is dated here" is the kind of sentence a document asks
        to be trusted about. This walks the history instead: every commit after
        the manifest's own freeze whose frozen-analysis constants differ from its
        parent's is an amendment, and its abbreviated hash has to appear in the
        section. Three do — the decision rule's third condition with the sampling
        binding, the stop rule's reversal, and the relevance rubric — and two of
        them went unlogged until round 5 of this pull request's review.
        """

        amendments = _frozen_analysis_amendments()
        if amendments is None:
            pytest.skip("no full git history here; the amendment log cannot be walked")
        assert amendments, "no post-freeze revision of the frozen analysis was found"
        section = self._amendments_section()
        unlogged = {
            commit: moved
            for commit, moved in amendments.items()
            if f"`{commit}`" not in section
        }
        assert unlogged == {}, f"amendments missing from the log: {unlogged}"

    def _post_run_amendments_section(self) -> str:
        text = self._text()
        start = text.index("## Amendments after the stopped run of 2026-09-10")
        return text[start : text.index("\n## ", start + 1)]

    def test_the_post_run_amendments_name_their_reason_and_a_real_commit(
        self,
    ) -> None:
        """An amendment made AFTER a unit ran is a different thing from one made
        before any existed, so it is logged in its own dated section — with the
        commit that carried it, resolved against this history rather than taken
        on the document's word.

        The frozen analysis is not what moved: the enforcement text and the
        reconciliation behind it are, and the section says so.

        Three entries carry that date. The first is the reconciliation; the
        second is the review round that put the truncation, identity and budget
        stops on the charged-failure path the first one opened; the third is the
        re-binding of the Inputs table to the second held-out band, with the gate
        that holds a live run to it. Every entry is resolved, not just the first
        — a log whose later lines are unchecked is the same document asking to be
        trusted that the walk above refuses to be.
        """

        section = self._post_run_amendments_section()
        collapsed = " ".join(section.split())
        assert "the reconciliation counts every charged call" in collapsed
        assert "2,228 input and 861 output tokens" in collapsed
        assert "The frozen analysis does not move" in collapsed
        assert "the stops a charged failure has to meet" in collapsed
        assert "the Inputs table is re-bound to the second held-out band" in collapsed
        commits = re.findall(r"\*\*2026-09-10 \(`([0-9a-f]{7,40})`\)", collapsed)
        assert len(commits) == 3
        if _git("rev-parse", "--is-shallow-repository").stdout.strip() != "false":
            pytest.skip("no full history here; the named commits cannot be resolved")
        for commit in commits:
            resolved = _git("rev-parse", "--verify", f"{commit}^{{commit}}")
            assert resolved.returncode == 0, f"{commit} is not a commit here"
            touched = _git(
                "show", "--name-only", "--format=", commit, "--", _INSTRUMENT_REPO_PATH
            )
            assert _INSTRUMENT_REPO_PATH in touched.stdout

    def test_every_named_post_run_commit_is_in_this_branchs_history(self) -> None:
        """Reachable from HEAD, not merely present in some local object store.

        A reviewer read the pull request as a squash onto `c12ec85a` and warned
        that the commit the log names would be orphaned. It is not — this branch
        is delivered by merge or fast-forward and never squashed, so every named
        commit is an ancestor — but "the object exists here" was the weaker claim
        the check above made, and ancestry is the one worth making.
        """

        collapsed = " ".join(self._post_run_amendments_section().split())
        commits = re.findall(r"\*\*2026-09-10 \(`([0-9a-f]{7,40})`\)", collapsed)
        assert commits
        if _git("rev-parse", "--is-shallow-repository").stdout.strip() != "false":
            pytest.skip("no full history here; ancestry cannot be walked")
        orphaned = [
            commit
            for commit in commits
            if _git("merge-base", "--is-ancestor", commit, "HEAD").returncode != 0
        ]
        assert orphaned == [], f"named but not an ancestor of HEAD: {orphaned}"

    def test_the_post_run_amendments_credit_no_clause_the_stop_rule_omits(
        self,
    ) -> None:
        """The enforcement-section gate above, pointed at the log instead.

        The second entry first read "Three stops `STOP_RULE` carries were
        reachable only on the success path" and closed "each of these three is a
        clause it already carried". Two of the three are quoted from the rule;
        the third, a checkpoint this run does not authorize, is nowhere in it —
        which is why it was the only member with no quotation. Crediting the
        frozen rule with a stop it omits is the defect this card retired from the
        enforcement section, in mirror image, so the log is held to the same
        rule: every phrase this section quotes is a clause of `STOP_RULE`, a
        heading or bullet of this document, or one the section says in so many
        words that the rule does NOT carry; and the count it claims the rule
        carried is the number of clauses it actually quotes.

        The checkpoint refusal is the manifest's own "Provider and model" limit,
        which is why the last assertion here is that provider identity appears
        nowhere in the frozen rule: adding it there would move the frozen
        analysis, and that is the owner's to make rather than this card's.
        """

        text = self._text()
        section = " ".join(self._post_run_amendments_section().split())
        rule = " ".join(instrument.STOP_RULE.split())

        quoted = re.findall(r'"([^"]+)"', section)
        carried = [phrase for phrase in quoted if phrase in rule]
        for phrase in quoted:
            if phrase in carried:
                continue
            assert (
                f'"{phrase}" — a stop condition `STOP_RULE` does not carry' in section
                or f"## {phrase}" in text
                or f"**{phrase}.**" in text
            ), f"quoted as the frozen rule's, but it does not state it: {phrase!r}"

        words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
        claimed = re.findall(r"([A-Za-z]+) stops? `STOP_RULE` carries", section)
        assert claimed, "the section states how many of the rule's clauses it reached"
        for word in claimed:
            assert word.lower() in words, f"count not spelled out: {word!r}"
        assert {words[word.lower()] for word in claimed} == {
            len(dict.fromkeys(carried))
        }

        lowered = instrument.STOP_RULE.lower()
        named = [
            word
            for word in ("checkpoint", "identity", "provider", "endpoint", "served")
            if word in lowered
        ]
        assert named == [], f"the frozen rule now names provider identity: {named}"

    def test_the_manifest_marks_the_row_the_authorization_card_does_not_carry(
        self,
    ) -> None:
        """Every other row of that table is the owner's, copied verbatim. The
        sampling row is not in the authorization card at all, so the claim above
        the table is qualified and the row itself says so."""

        authorization = (
            _REPO_ROOT / "tasks" / "work" / "fresh-deduction-authorization.md"
        ).read_text(encoding="utf-8")
        assert "Sampling temperature" not in authorization
        assert (
            "| Sampling temperature *(not from the authorization card" in self._text()
        )

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
        assert instrument.LIVE_RUN_FLAG in text

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

    def _bound_held_out_record(self) -> tuple[Path, dict[str, Any]]:
        """The one freeze record on disk whose band the Inputs row names.

        Which record that is moves with the row: the live freeze at
        ``MANIFEST_PATH``, or -- while a re-binding is outstanding -- a
        converted record beside it. These tests follow the row rather than a
        band written down here.

        The row is read with ``instrument.manifest_bound_band``, the same reader
        the run-time gate uses, so this test and
        ``assert_manifest_binds_the_live_band`` cannot come to different
        conclusions about which band the document binds. Reading the whole text
        instead -- which is what this helper did while the row was stale -- would
        also match the converted band the row now NAMES in prose, and the
        document would be unable to say what it supersedes.
        """

        bound = instrument.manifest_bound_band(self._text())
        candidates: list[tuple[Path, dict[str, Any]]] = [
            (_REPO_ROOT / MANIFEST_PATH, _committed_manifest())
        ]
        for path in _converted_manifest_paths():
            loaded = json.loads(path.read_text(encoding="utf-8"))
            assert isinstance(loaded, dict)
            candidates.append((path, loaded))
        matched = [
            (path, record)
            for path, record in candidates
            if (record["band"]["first_seed"], record["band"]["last_seed"]) == bound
        ]
        assert len(matched) == 1, (
            f"the Inputs row binds seed band {bound[0]}-{bound[1]}, which is "
            "the band of no committed freeze record"
        )
        return matched[0]

    def test_the_manifest_binds_a_committed_held_out_record(self) -> None:
        """Every number in the Inputs row comes from a freeze record on disk."""

        text = self._text()
        _, manifest = self._bound_held_out_record()
        first_accepted = manifest["accepted"][0]["seed"]
        assert (
            f"accepted seeds run {first_accepted}–"
            f"{manifest['last_accepted_seed']}" in text
        )
        assert f"{manifest['skipped_reason_counts']['witnessed_kill']} skips" in text

    def test_a_binding_to_a_converted_record_stays_an_open_obligation(self) -> None:
        """A development record may be bound only while the re-binding is open.

        ``verify_frozen_set`` regenerates whatever ``MANIFEST_PATH`` holds, so a
        document bound to some other band authorizes inputs the run would not
        draw. A live run is refused outright for that now
        (``assert_manifest_binds_the_live_band``, in
        ``TestTheManifestBindsTheBandTheRunWouldDraw`` above).

        What is enforced here is the other half, and it holds with no live run in
        sight: a binding to a converted record cannot go silent or become
        permanent. Such a record has to name the record that replaced it; that
        record has to be the live held-out freeze of another band; and the card
        the conversion named has to be still open and still name the record it
        owes the row. A held-out binding is the settled state -- the state this
        document is in since the re-binding of 2026-09-10 -- and then it has to
        be the live freeze itself.
        """

        path, record = self._bound_held_out_record()
        if record["status"] == "held_out":
            assert path == _REPO_ROOT / MANIFEST_PATH
            return
        assert record["status"] == "development", (
            f"the execution manifest binds {path.name}, whose status is "
            f"{record['status']!r}: a freeze record is held out or converted"
        )
        converted = record["converted"]
        assert converted["superseded_by"] == MANIFEST_PATH, (
            f"{path.name} is bound while development and names "
            f"{converted['superseded_by']!r} as its replacement, not the live "
            f"freeze {MANIFEST_PATH}"
        )
        live = _committed_manifest()
        assert live["status"] == "held_out"
        assert live["band"] != record["band"]
        rebinding = _REPO_ROOT / converted["informed"]
        # Read into booleans rather than asserting on the membership directly:
        # a failure here should name the card, not print it.
        rebinding_text = rebinding.read_text(encoding="utf-8")
        still_open = "**Status:** done" not in rebinding_text
        names_the_live_record = MANIFEST_PATH in rebinding_text
        assert still_open, (
            f"{rebinding.name} is closed while the execution manifest still "
            f"binds the converted {path.name}"
        )
        assert names_the_live_record, (
            f"{rebinding.name} owes the Inputs row a binding to {MANIFEST_PATH} "
            "and no longer names it"
        )


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
        seed = _first_accepted_seed()
        assert written == [
            f"combined_accounts-seed-{seed}.jsonl",
            f"repaired_clock-seed-{seed}.jsonl",
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
