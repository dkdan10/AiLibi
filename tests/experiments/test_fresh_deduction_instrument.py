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
import inspect
import itertools
import json
import re
import subprocess
import time
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any, Final, cast, get_args

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
    SamplingConfig,
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
from engine.world import load_canonical_map
from experiments.held_out_prefixes import (
    CONVERTED_BANDS,
    LEGACY_BODY_HANDLE_PATTERN,
    MANIFEST_PATH,
    PREREGISTERED_BAND,
    TEMPORAL_OBSERVATION_VERSION,
    ConvertedBand,
    HeldOutPrefixError,
    SeedBand,
    assert_no_legacy_body_handles,
    build_prefix,
    canonical_prefix_json,
    prefix_sha256,
)
from llm.budget import BudgetExceededError, GameBudget
from llm.client import CallKind, LLMResponse, TokenUsage
from llm.fake_provider import FAKE_FINISH_REASON
from meetings.citation_relevance import names_player
from meetings.manager import (
    DEFAULT_TURN_FREE_TEXT,
    DEFAULT_VOTE_RATIONALE,
    INVALID_OBSERVATION_ID_MARKER,
    INVALID_REASON_ID_MARKER,
    INVALID_VOTE_TARGET_MARKER,
    OFF_TARGET_CITATION_EJECT_MARKER,
    UNCITED_ZERO_FLAG_EJECT_MARKER,
    VOTE_PARSE_DEFAULT_MARKER,
    DefaultedCall,
    SuspicionEntry,
    guard_ballot_citation,
    guard_ballot_target_graph,
)
from meetings.schemas import (
    AccusationClaim,
    BallotTargetRewriteReason,
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
    LLMCallRecord,
    MeetingReplayEntry,
    read_all_entries,
)
from orchestrator.run_limits import RunDeadlineExceeded
from tests.experiments import burned_call_double
from tests.experiments.burned_call_double import (
    BURNED_INPUT_TOKENS,
    BURNED_OUTPUT_TOKENS,
    EMPTY_BODY_ERROR,
    NO_COMPLETION_MESSAGES,
    RETRYABLE_STATUS_ERROR,
    TRANSPORT_ERROR,
    BurnedCallProvider,
    NoCompletionProvider,
    TruncatedCompletionProvider,
    charged_no_completion,
)
from tests.experiments import usage_replay_double
from tests.experiments.usage_replay_double import (
    STOPPED_RUNS_PROFILE_PATH,
    CallTypeBlindReplayProvider,
    UsageProfile,
    UsageReplayProvider,
    feasible_limits,
    stopped_runs_profile,
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

#: The per-unit OUTPUT ceiling the owner merged on 2026-09-07, kept here as the
#: planted defect rather than as a live constant. The third live run stopped on
#: it — 4,000 against a 9,216-token reservation schedule — and the fourth
#: authorization of 2026-09-14 replaced it with 16,000. It stays planted because
#: the refusal is what the re-sizing answers: under the raised turn cap the same
#: ceiling cannot pay for the first call of a unit, let alone its sixth.
_CEILINGS_MERGED_2026_09_07: Final[int] = 4_000


def _limits_merged_on_2026_09_07() -> RunLimits:
    """The four token ceilings the owner merged on 2026-09-07, as one object.

    The fourth authorization of 2026-09-14 replaced all four. They are kept here
    as the planted set a gate test needs — the committed ceilings now pay for
    their own run, so a refusal has to be planted to be shown — and as the
    denominator the manifest's superseded headroom figures were measured
    against. The walls are today's, because neither of them is what these
    plants are about.
    """

    return AUTHORIZED_LIMITS.model_copy(
        update={
            "run_max_input_tokens": 2_400_000,
            "run_max_output_tokens": 200_000,
            "unit_max_input_tokens": 45_000,
            "unit_max_output_tokens": _CEILINGS_MERGED_2026_09_07,
        }
    )


def _sampling_before_the_raise() -> SamplingConfig:
    """The draw in force until the fourth authorization raised the turn cap.

    A rehearsal that reproduces a stop from before 2026-09-14 has to reserve
    what that run reserved, or it reproduces the stop's shape and not the stop.
    """

    return AUTHORIZED_SAMPLING.model_copy(update={"turn_max_tokens": 2048})


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


_DATED_AMENDMENT_ENTRY: Final[re.Pattern[str]] = re.compile(
    r"\*\*(\d{4}-\d{2}-\d{2}) \(`([0-9a-f]{7,40})`\)"
)
_NAME_IN_BACKTICKS: Final[re.Pattern[str]] = re.compile(
    r"`([a-z][a-z0-9_]*(?:/[a-z0-9_]+)*\.py|[A-Za-z_][A-Za-z0-9_]{3,})`"
)


def _entries_and_the_names_they_attribute(
    section: str,
) -> list[tuple[str, str, frozenset[str]]]:
    """``(date, commit, the backticked names)`` of each dated entry of a log.

    An entry runs from its own bold heading to the next one, so every name
    inside it is a name that entry attributes to the commit its heading names.
    Pure over the text, so the check below can be run against a perturbed
    section as well as the committed one.
    """

    headings = list(_DATED_AMENDMENT_ENTRY.finditer(section))
    entries: list[tuple[str, str, frozenset[str]]] = []
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(section)
        body = section[heading.start() : end]
        entries.append(
            (
                heading.group(1),
                heading.group(2),
                frozenset(_NAME_IN_BACKTICKS.findall(body)),
            )
        )
    return entries


def _names_an_entry_credits_to_a_commit_without_them(
    section: str,
    source_at: Callable[[str], str],
    carried_now: str,
) -> dict[str, list[str]]:
    """``{commit: the names its entry claims that the commit does not carry}``.

    Only names the instrument carries TODAY are checked, so ordinary prose in
    backticks — a flag, a date, a file this module never mentions — is not
    mistaken for a symbol. What is left is the claim that matters: an entry
    dated against one commit describing a mechanism that arrived in another.
    """

    offenders: dict[str, list[str]] = {}
    for _date, commit, named in _entries_and_the_names_they_attribute(section):
        source = source_at(commit)
        missing = sorted(
            name for name in named if name in carried_now and name not in source
        )
        if missing:
            offenders[commit] = missing
    return offenders


def _instrument_source_at(revision: str) -> str:
    """The instrument's bytes at one revision, or "" where it does not exist."""

    shown = _git("show", f"{revision}:{_INSTRUMENT_REPO_PATH}")
    return shown.stdout if shown.returncode == 0 else ""


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

    Derived rather than written down: the band has moved twice already -- the
    3000-3999 set became development data on 2026-09-10 and the 5000-5999 set
    on 2026-09-13, each replaced by a fresh freeze -- and a literal here would
    only re-pin these names to whichever band was current when it was typed.
    """

    accepted = _committed_manifest()["accepted"]
    assert isinstance(accepted, list)
    return int(accepted[0]["seed"])


def _live_band() -> tuple[int, int]:
    """The band the freeze record at ``MANIFEST_PATH`` holds: what a run draws."""

    band = _committed_manifest()["band"]
    return int(band["first_seed"]), int(band["last_seed"])


def _the_document_is_mid_rebinding() -> tuple[int, int] | None:
    """The band the Inputs row still binds while a freeze has moved past it.

    A freeze converts the band the execution manifest binds and freezes a new
    one under its own card, and the card that re-binds the row lands after it.
    Between those two merges the document describes the PREVIOUS band on
    purpose: the row, its dated re-binding entry and every figure measured on
    that band are one consistent statement about a set the runner would no
    longer draw, and ``assert_manifest_binds_the_live_band`` refuses a live run
    for exactly that reason -- which is asserted here rather than assumed, so
    the window is never merely a reason to assert less.

    Returns that band while the window is open and ``None`` once the row is
    settled, so a case whose subject is a figure OF THE BOUND BAND can say
    which of the two states it is reading instead of failing on a staleness the
    tree declares. The window cannot become permanent:
    ``TestExecutionManifest.test_a_binding_to_a_converted_record_stays_an_open_obligation``
    turns red the moment the card that owes the row closes with it still stale.
    """

    bound = instrument.manifest_bound_band(_MANIFEST.read_text(encoding="utf-8"))
    if bound == _live_band():
        return None
    assert bound in {
        (converted.band.first_seed, converted.band.last_seed)
        for converted in CONVERTED_BANDS
    }, (
        f"the execution manifest binds seed band {bound[0]}-{bound[1]}, which "
        "is neither the live freeze nor a converted record: that is a stale "
        "document, not a re-binding window"
    )
    with pytest.raises(LiveRunNotAuthorized):
        instrument.assert_manifest_binds_the_live_band()
    return bound


def _manifest_text_bound_to(band: tuple[int, int]) -> str:
    """The committed execution manifest with its Inputs row moved to ``band``."""

    return re.sub(
        r"^(\|\s*Seed band\s*\|\s*)\d+–\d+",
        rf"\g<1>{band[0]}–{band[1]}",
        _MANIFEST.read_text(encoding="utf-8"),
        count=1,
        flags=re.MULTILINE,
    )


def _root_binding_the_live_band(tmp_path: Path) -> Path:
    """A repository root whose Inputs row binds the band the runner would draw.

    Usually the repository itself: a document bound to the live freeze is the
    settled state. Between a freeze and the re-binding that follows it the
    committed row still names the band that freeze just converted, and
    ``assert_manifest_binds_the_live_band`` refuses there -- deliberately, and
    with its own cases in ``TestTheManifestBindsTheBandTheRunWouldDraw`` below.
    The cases that use this helper are about what the gate does once that check
    passes, so in that window they run against a copy of the committed document
    whose Seed band row is moved to the live band and in which nothing else
    changes.

    The COPY is the point, so being handed the repository is refused rather than
    obeyed. Outside a freeze window the early return below makes such a call
    look harmless; inside one it would rewrite the committed execution manifest
    -- silently re-binding the document a live run is authorized against -- as a
    side effect of running the test suite.
    """

    assert tmp_path.resolve() != _REPO_ROOT.resolve(), (
        "_root_binding_the_live_band writes a rebound copy of the execution "
        "manifest into tmp_path; handed the repository it would rewrite the "
        "committed document"
    )
    live = _live_band()
    if instrument.manifest_bound_band(_MANIFEST.read_text(encoding="utf-8")) == live:
        return _REPO_ROOT
    manifest = tmp_path / EXECUTION_MANIFEST_PATH
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(_manifest_text_bound_to(live), encoding="utf-8")
    _write_frozen_manifest(tmp_path, _committed_manifest())
    return tmp_path


def _root_without_the_clause_binding_the_live_band(tmp_path: Path, clause: str) -> Path:
    """A root whose manifest binds the live band and carries no ``clause``.

    The plant for a gate on the DOCUMENT, now that the committed document
    authorizes both a resume and a calibration: everything else about the tree
    is the committed one, and the owner's sentence is the only thing missing.
    """

    assert tmp_path.resolve() != _REPO_ROOT.resolve(), (
        "this helper writes a planted copy of the execution manifest into "
        "tmp_path; handed the repository it would rewrite the committed document"
    )
    text = _manifest_text_bound_to(_live_band())
    assert clause in text, "the committed manifest does not carry the clause"
    manifest = tmp_path / EXECUTION_MANIFEST_PATH
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(text.replace(clause, "[clause removed]"), encoding="utf-8")
    _write_frozen_manifest(tmp_path, _committed_manifest())
    return tmp_path


def _literal_message(node: ast.expr) -> str:
    """The message a `raise RuntimeError(...)` statement writes, as a literal.

    An f-string's interpolations are replaced by a placeholder: what the
    instrument's classifier keys on is the fixed wording around them, and a
    marker that only matched a formatted value would not be a marker.
    """

    if isinstance(node, ast.Constant):
        return str(node.value)
    if isinstance(node, ast.JoinedStr):
        return "".join(
            str(part.value) if isinstance(part, ast.Constant) else "<value>"
            for part in node.values
        )
    raise AssertionError(f"not a literal message: {ast.unparse(node)}")


def _without_wall(report: InstrumentReport) -> dict[str, Any]:
    """A report's payload minus the clocks, for comparing two runs of it.

    Everything a run MEASURES is comparable; the two wall clocks are real
    seconds and are not the same twice, which is why they are dropped here
    rather than rounded.
    """

    payload = report.model_dump(mode="json")
    payload.pop("elapsed_seconds")
    payload.pop("model_work_seconds")
    for arm in payload["arms"]:
        arm.pop("model_work_seconds")
    return payload


def _token_rows(
    usage_by_arm: Mapping[str, instrument.ArmUsage],
) -> dict[str, tuple[int, int, int]]:
    """``{arm: (input, output, calls)}`` — the three figures a record quotes."""

    return {
        arm: (usage.input_tokens, usage.output_tokens, usage.calls)
        for arm, usage in usage_by_arm.items()
    }


def _arm_rows(report: InstrumentReport) -> dict[str, tuple[int, int, int]]:
    """The same three figures off a finished report's arm summaries."""

    return {
        arm.arm: (arm.input_tokens, arm.output_tokens, arm.calls) for arm in report.arms
    }


def _less_the_stops_own_calls(
    report: InstrumentReport, checkpoint: instrument.RunCheckpoint
) -> dict[str, Any]:
    """A resumed report with the calls its stop abandoned taken back out.

    A resumed run reports what an uninterrupted one does PLUS what the stop
    itself spent inside the pair it interrupted: those calls were billed, the
    resume charges them against the same ceilings, and they belong to no graded
    unit. Subtracting exactly the rows the checkpoint names is how the two runs
    are compared without pretending the stop was free — and it fails loudly if
    the abandoned rows are not the whole of the difference.
    """

    payload = _without_wall(report)
    rows = {row.arm: row for row in checkpoint.abandoned.arms}
    for arm in payload["arms"]:
        row = rows.get(arm["arm"])
        if row is None:
            continue
        arm["calls"] -= row.usage.calls
        arm["input_tokens"] -= row.usage.input_tokens
        arm["output_tokens"] -= row.usage.output_tokens
        arm["cost_usd"] -= row.usage.cost_usd
        arm["cap_signal_disagreements"] -= row.usage.cap_signal_disagreements
        # The per-call readings the abandoned rows carry come out the same way:
        # a key the stop alone contributed disappears rather than reaching zero,
        # so the two payloads compare as dicts.
        remaining = Counter(arm["finish_reasons"])
        remaining.subtract(row.usage.finish_reasons)
        arm["finish_reasons"] = {
            reason: count for reason, count in sorted(remaining.items()) if count
        }
        payload["total_cost_usd"] -= row.usage.cost_usd
    return payload


class _StubClient:
    """A minimal in-process client with no schema behaviour, for cap tests.

    ``finish_reason`` is what this stub reports the provider said about how
    generation stopped: ``None`` by default, which is the reading an adapter
    that maps none records and the one every case here had before the field
    existed.
    """

    def __init__(
        self,
        *,
        output_tokens: int = 5,
        input_tokens: int = 1,
        finish_reason: str | None = None,
    ) -> None:
        self.output_tokens = output_tokens
        self.input_tokens = input_tokens
        self.finish_reason = finish_reason
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
            finish_reason=self.finish_reason,
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

        # Both doubles beside this file are held to the same line rather than
        # exempted from it. The replay double reaches neither `llm.provider` nor
        # the flag; the burned-call double has to reach the parse-failure seam,
        # so what it may take from that module is enumerated.
        for module in (burned_call_double, usage_replay_double):
            double = Path(module.__file__ or "").read_text(encoding="utf-8")
            assert instrument.LIVE_RUN_FLAG not in double
            assert re.search(r"^\s*import\s+llm\.provider", double, re.M) is None
            taken = {
                alias.name
                for node in ast.parse(double).body
                if isinstance(node, ast.ImportFrom) and node.module == "llm.provider"
                for alias in node.names
            }
            assert taken in (set(), {"LLMCallFailure", "_attach_parse_failure"})


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
        # Bound to the live band, so the refusal under test is the moved digest
        # rather than a stale Inputs row, which is checked one gate earlier.
        manifest.write_text(_manifest_text_bound_to(_live_band()), encoding="utf-8")
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

    def test_the_pre_client_gate_returns_the_verified_set(self, tmp_path: Path) -> None:
        """The positive half: it hands back the set the client is then built
        against, so the two cannot come apart. The root is the committed tree
        whenever the Inputs row binds the live band, and a copy of it with that
        one row moved while a re-binding is outstanding."""

        root = _root_binding_the_live_band(tmp_path)
        invocation = LiveRunInvocation.naming(
            root / EXECUTION_MANIFEST_PATH,
            provider=AUTHORIZED_PROVIDER,
            model=AUTHORIZED_MODEL,
            repo_root=root,
        )
        frozen = instrument.assert_ready_for_a_live_run(
            provider=AUTHORIZED_PROVIDER,
            invocation=invocation,
            repo_root=root,
        )
        assert len(frozen.accepted_seeds) == 50

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
        root = _root_binding_the_live_band(tmp_path / "root")
        invocation = LiveRunInvocation.naming(
            root / EXECUTION_MANIFEST_PATH,
            provider=AUTHORIZED_PROVIDER,
            model=AUTHORIZED_MODEL,
            repo_root=root,
        )
        with pytest.raises(_Stop):
            run_instrument(
                output_dir=tmp_path,
                client=_StubClient(),
                provider=AUTHORIZED_PROVIDER,
                live_invocation=invocation,
                repo_root=root,
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


class TestTheManifestBindsTheBandTheRunWouldDraw:
    """The authorization document and the inputs, held together at run time.

    `verify_frozen_set` regenerates whatever record sits at `MANIFEST_PATH` and
    holds it to the generator's own `PREREGISTERED_BAND`; neither reads the
    execution manifest. So when the 3000-3999 band became development data on
    2026-09-10 and 5000-5999 was frozen in its place, the manifest went on
    authorizing a band the runner would no longer draw, with every other gate
    green. Nothing but the re-binding closed that, and a document is not a gate.

    A freeze moves the band before the document that authorizes it can follow:
    the third freeze drew 6000-6999 while the Inputs row still named 5000-5999,
    and the re-binding that closed that window is the transport-resilience
    card's acceptance item. The window is exactly what this gate is for, so the
    first case below asserts the refusal rather than skipping it whenever the
    tree is in one, and
    `TestExecutionManifest.test_a_binding_to_a_converted_record_stays_an_open_obligation`
    is what keeps such a window from becoming permanent.
    """

    def test_the_gate_says_which_bands_actually_moved(self) -> None:
        """The gate's own docstring, held to the records that moved.

        It motivates the check by naming the conversions, which is a list that
        grows: a docstring written at the first conversion went on describing
        5000-5999 as the band frozen in place of 3000-3999 after 5000-5999 had
        itself become development data. Read out of `CONVERTED_BANDS` and each
        record's own `converted.date` instead of trusted, so the next
        conversion turns this red here rather than leaving the enforcing
        function explaining a history that has moved on.
        """

        source = instrument.assert_manifest_binds_the_live_band.__doc__
        assert source is not None, "the gate carries no docstring to check"
        doc = " ".join(source.split())
        for converted in CONVERTED_BANDS:
            record = json.loads(
                (_REPO_ROOT / converted.manifest_path).read_text(encoding="utf-8")
            )
            span = f"{converted.band.first_seed}-{converted.band.last_seed}"
            date = record["converted"]["date"]
            assert re.search(rf"{span}[^.]*?{re.escape(date)}", doc), (
                f"the gate explains itself without saying that {span} became "
                f"development data on {date}"
            )

    def _planted_root(self, root: Path, *, band: tuple[int, int]) -> Path:
        """A repository root whose Inputs row names `band` and whose freeze
        record is the committed one. Everything else is the committed document,
        so the digest and the required-string checks above this one all pass."""

        manifest = root / EXECUTION_MANIFEST_PATH
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(_manifest_text_bound_to(band), encoding="utf-8")
        _write_frozen_manifest(root, _committed_manifest())
        return manifest

    def test_the_committed_manifest_binds_the_live_band_or_is_refused(self) -> None:
        """Settled, or a stale binding this gate refuses while a card owes the row.

        Settled means the Inputs row and the freeze record name one band and the
        gate passes. Otherwise the row has to name a band a CONVERTED record
        holds -- a band no committed record holds at all would be a document
        describing inputs that do not exist -- and the gate has to refuse,
        naming both bands. Either way the committed tree cannot reach a live
        call under a document written for another band.
        """

        live = _live_band()
        bound = instrument.manifest_bound_band(_MANIFEST.read_text(encoding="utf-8"))
        if bound == live:
            instrument.assert_manifest_binds_the_live_band()
            return
        assert bound in {
            (converted.band.first_seed, converted.band.last_seed)
            for converted in CONVERTED_BANDS
        }, (
            f"the Inputs row binds seed band {bound[0]}-{bound[1]}, which is "
            "neither the live freeze nor a converted record"
        )
        with pytest.raises(LiveRunNotAuthorized) as refused:
            instrument.assert_manifest_binds_the_live_band()
        message = str(refused.value)
        assert f"binds seed band {bound[0]}-{bound[1]}" in message
        assert f"holds {live[0]}-{live[1]}" in message

    def test_a_stale_binding_stops_the_run_before_a_client_exists(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: an Inputs row naming the first converted band, 3000-3999,
        while the live record holds whatever band the current freeze drew.

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

    @pytest.mark.parametrize("max_tokens", [8192, 2048, 512])
    def test_a_call_outside_the_authorized_caps_stops_the_run(
        self, max_tokens: int
    ) -> None:
        # PLANTED: a caller asking for a cap the authorization did not name —
        # over the ceiling, and two under it. 2,048 is the shipped turn default
        # and was an authorized cap until 2026-09-14, so it is planted here on
        # purpose: after the raise, a caller still asking for it is a caller
        # drawing from a distribution this manifest no longer binds.
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
    """The work window is a limit on model work, so it has to bind IN FLIGHT.

    Charged only on return it is a one-call-granular limit, and one call on the
    authorized provider is six sends at a 600 s timeout with backoff — close to
    an hour. A run at 5 h 59 m could then spend a seventh hour against an
    authorization of six, with only the separate 8 h elapsed clock behind it.
    """

    def test_the_work_clock_docstring_states_the_authorized_window(self) -> None:
        """PLANTED: the docstring left at the authorization it used to enforce.

        `_ModelWorkClock` is the mechanism the manifest sends an auditor to
        read, so a widened authorization that moved the constants and the record
        but not the class's own account of them would leave the enforcing code
        stating a limit no longer authorized — which is what happened when
        4 h / 6 h became 6 h / 8 h. The figures are derived from the constants
        here, never retyped.
        """

        doc = " ".join((inspect.getdoc(instrument._ModelWorkClock) or "").split())
        work_hours = int(instrument.AUTHORIZED_MODEL_WORK_SECONDS // 3600)
        elapsed_hours = int(instrument.AUTHORIZED_ELAPSED_SECONDS // 3600)
        assert f"{work_hours} h of model work" in doc
        assert f"{elapsed_hours} h elapsed window" in doc
        # The boundary illustration is one minute short of the work window and
        # names the hour past it, so it cannot survive a widening either.
        assert f"{work_hours - 1} h 59 m of model work" in doc
        assert f"separate {elapsed_hours} h elapsed clock" in doc

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
        reached, and mislabelling it would forge a stop reason.

        It is retried like the other no-completion classes, so the stop that
        arrives is the exhausted retry bound and not `RunDeadlineExceeded`; the
        original timeout is chained onto it and named in its message, and the
        work clock carries only the attempts' own (negligible) wall rather than
        a window it never reached.
        """

        clock = instrument._ModelWorkClock(max_seconds=3600.0)
        client = instrument._InstrumentClient(
            _TimingOutProvider(),
            work_clock=clock,
            backoff_base_seconds=0.0,
        )
        with pytest.raises(
            instrument.TransportAttemptsExhausted,
            match="the provider's own read timeout",
        ) as caught:
            asyncio.run(
                client.complete(
                    prompt="p", schema=None, max_tokens=1024, temperature=0.2
                )
            )
        assert not isinstance(caught.value, RunDeadlineExceeded)
        assert isinstance(caught.value.__cause__, TimeoutError)
        assert clock.seconds < 1.0
        assert dict(client.attempts().by_trigger) == {
            "transport_error": instrument.MAX_TRANSPORT_ATTEMPTS
        }

    def test_a_call_inside_the_window_is_untouched(self) -> None:
        clock = instrument._ModelWorkClock(max_seconds=3600.0)
        inner = _SlowProvider(seconds=0.01)
        client = instrument._InstrumentClient(inner, work_clock=clock)
        asyncio.run(
            client.complete(prompt="p", schema=None, max_tokens=1024, temperature=0.2)
        )
        assert inner.finished == 1
        assert 0.0 < clock.seconds < 1.0


class _RecordedSleep:
    """The wrapper's backoff, recorded instead of waited out."""

    def __init__(self) -> None:
        self.waits: list[float] = []

    async def __call__(self, seconds: float) -> None:
        self.waits.append(seconds)


class TestTransportRetry:
    """The bounded retry: what is sent again, what is not, and what it costs.

    The second live run (PR #448) stopped on its fifth call because Featherless
    answered a 2xx with no `choices`, which the adapter refuses with a bare
    `RuntimeError` none of its own retry classes carries. An attempt that
    produced no completion is not a sample, so sending it again re-draws
    nothing; a truncation and a refused payload ARE samples, so sending either
    again would draw a frozen unit twice. Each case below is one side of that
    line, at the wrapper, which is where the bound lives.
    """

    def _client(
        self,
        inner: Any,
        *,
        clock: instrument._ModelWorkClock | None = None,
        sleep: _RecordedSleep | None = None,
        per_attempt_timeout_seconds: float = instrument.PER_ATTEMPT_TIMEOUT_SECONDS,
    ) -> instrument._InstrumentClient:
        return instrument._InstrumentClient(
            inner,
            work_clock=clock or instrument._ModelWorkClock(max_seconds=3600.0),
            per_attempt_timeout_seconds=per_attempt_timeout_seconds,
            sleep=sleep or _RecordedSleep(),
        )

    def _call(
        self, client: instrument._InstrumentClient, *, schema: Any = None
    ) -> LLMResponse:
        return asyncio.run(
            client.complete(prompt="p", schema=schema, max_tokens=1024, temperature=0.2)
        )

    def test_one_empty_body_then_a_completion_continues_the_call(self) -> None:
        """PLANTED: the failure that stopped the run of 2026-09-13, once.

        The call resolves on its second attempt, one retry is counted with its
        trigger, and the attempt that bought nothing is in the ledger with zero
        tokens and its own marker rather than missing from it.
        """

        inner = NoCompletionProvider(mode="empty_body", failures=1)
        sleep = _RecordedSleep()
        client = self._client(inner, sleep=sleep)
        response = self._call(client)
        assert response.text
        assert inner.attempts == 2
        assert sleep.waits == [instrument.TRANSPORT_BACKOFF_BASE_SECONDS]
        attempts = client.attempts()
        assert attempts.retried_calls == 1
        assert attempts.unaccounted_attempts == 1
        assert dict(attempts.by_trigger) == {"empty_completion": 1}
        unaccounted = [
            call
            for call in client.calls
            if call.model == instrument.UNACCOUNTED_ATTEMPT_MODEL
        ]
        assert len(unaccounted) == 1
        assert unaccounted[0].input_tokens == unaccounted[0].output_tokens == 0
        assert unaccounted[0].cost_usd == 0.0

    def test_four_empty_bodies_stop_the_call(self) -> None:
        """PLANTED: the same failure, never recovering. Four attempts is the
        bound, so the fourth is a stop and not a fifth send, and the backoff
        between them is the exponential the constant states."""

        inner = NoCompletionProvider(mode="empty_body", failures=99)
        sleep = _RecordedSleep()
        client = self._client(inner, sleep=sleep)
        with pytest.raises(
            instrument.TransportAttemptsExhausted, match="empty_completion"
        ) as caught:
            self._call(client)
        assert inner.attempts == instrument.MAX_TRANSPORT_ATTEMPTS == 4
        assert sleep.waits == [1.0, 2.0, 4.0]
        assert "refusing to record an empty completion" in str(caught.value)
        attempts = client.attempts()
        assert attempts.retried_calls == 1
        assert attempts.unaccounted_attempts == 4
        assert dict(attempts.by_trigger) == {"empty_completion": 4}

    @pytest.mark.parametrize(
        ("message", "trigger"),
        [
            (TRANSPORT_ERROR, "transport_error"),
            (RETRYABLE_STATUS_ERROR, "retryable_status"),
        ],
    )
    def test_a_transport_failure_and_a_retryable_status_are_retried(
        self, message: str, trigger: str
    ) -> None:
        """PLANTED: the other two shapes the adapter raises without a
        completion — its exhausted transport/parse sends and a 503 it could not
        get past — each recovered on the retry and counted as its own class."""

        mode = "transport_error" if trigger == "transport_error" else "retryable_status"
        inner = NoCompletionProvider(mode=cast(Any, mode), failures=1)
        client = self._client(inner)
        self._call(client)
        assert inner.attempts == 2
        assert dict(client.attempts().by_trigger) == {trigger: 1}
        assert message  # the double raises exactly this wording

    def test_an_attempt_past_the_per_attempt_wall_is_retried(self) -> None:
        """PLANTED: the endpoint holds the connection open and never answers.

        The wrapper cuts the attempt off at its own wall and sends the call
        again; without that bound the attempt runs to the provider client's own
        budget, which is six sends at a 600 s timeout. The assertion is on how
        long it took, not only that it recovered.
        """

        inner = NoCompletionProvider(mode="stall", failures=1, stall_seconds=5.0)
        client = self._client(inner, per_attempt_timeout_seconds=0.05)
        started = time.monotonic()
        self._call(client)
        elapsed = time.monotonic() - started
        assert elapsed < 2.0, (
            f"the retry waited for the stalled attempt: {elapsed:.1f}s"
        )
        assert inner.attempts == 2
        assert dict(client.attempts().by_trigger) == {"attempt_timeout": 1}
        # The wall that cut it off is this wrapper's, not the run's window, so
        # the row it left carries the unaccounted marker rather than the one a
        # limit being reached leaves behind.
        assert [call.model for call in client.calls][0] == (
            instrument.UNACCOUNTED_ATTEMPT_MODEL
        )
        assert len(client.calls) == 2

    def test_the_model_work_window_still_stops_a_stalled_attempt(self) -> None:
        """The two walls are not the same wall. When what is LEFT of the
        model-work window is the tighter of the two, the cut-off attempt is the
        limit being reached — a stop, with no retry — and not an endpoint that
        stopped answering."""

        inner = NoCompletionProvider(mode="stall", failures=1, stall_seconds=5.0)
        clock = instrument._ModelWorkClock(max_seconds=0.2)
        client = self._client(inner, clock=clock, per_attempt_timeout_seconds=60.0)
        with pytest.raises(RunDeadlineExceeded, match="exhausted mid-call"):
            self._call(client)
        assert inner.attempts == 1
        assert client.attempts().unaccounted_attempts == 0
        assert [call.model for call in client.calls] == [
            instrument.ABORTED_ATTEMPT_MODEL
        ]

    def test_a_truncated_response_is_not_retried(self) -> None:
        """PLANTED: a response at its output cap. It is a completion the model
        produced, so it is the datum the stop rule refuses to accept rather
        than an attempt that failed to happen; sending it again would draw the
        same frozen unit twice."""

        inner = NoCompletionProvider(mode="truncation", failures=99)
        client = self._client(inner)
        with pytest.raises(PerCallCapExceeded, match="a truncation is a"):
            self._call(client)
        assert inner.attempts == 1
        assert client.attempts().unaccounted_attempts == 0

    def test_a_payload_the_adapter_refused_on_its_schema_is_not_retried(self) -> None:
        """PLANTED: the adapter validated the completion and re-raised. The
        endpoint produced a body, the meeting layer's default path is what
        handles it, and the reconciliation counts its spend — so the wrapper
        leaves it alone."""

        inner = NoCompletionProvider(mode="invalid_schema", failures=99)
        client = self._client(inner)
        with pytest.raises(ValidationError):
            self._call(client, schema=ModelAuthoredVoteBallot)
        assert inner.attempts == 1
        assert client.attempts().unaccounted_attempts == 0

    def test_a_billed_and_refused_call_is_not_retried(self) -> None:
        """The same line, on the failure the provider CHARGED for: its spend is
        already in this client's ledger and in the budget, so a retry would buy
        a second charge on one unit."""

        inner = BurnedCallProvider()
        client = self._client(inner)
        with pytest.raises(ValidationError):
            self._call(client, schema=ModelAuthoredVoteBallot)
        assert inner.ballots == 1
        assert client.attempts().unaccounted_attempts == 0
        assert [call.input_tokens for call in client.calls] == [BURNED_INPUT_TOKENS]

    @pytest.mark.parametrize(
        "failure",
        [
            BudgetExceededError(
                dimension="input_tokens", current=45_000, delta=1, cap=45_000
            ),
            RunDeadlineExceeded("the elapsed deadline passed"),
            PerCallCapExceeded("a response reached its cap"),
            LiveRunNotAuthorized("no invocation"),
            RuntimeError("something this wrapper has never seen"),
        ],
        ids=["budget", "deadline", "cap", "live-gate", "unclassified"],
    )
    def test_what_the_wrapper_never_sends_again(self, failure: Exception) -> None:
        """An exhausted limit, a refusal this instrument raised and a failure
        nothing here can classify are all `None` to the classifier.

        The first three would be "no retry and no widening of any limit"
        violated by a retry; the last is the conservative direction — an
        unrecognised failure stops the run with its partial accounting rather
        than being sent again blindly.
        """

        assert instrument.transport_trigger(failure) is None

    def test_a_billed_failure_is_not_retried_however_it_is_worded(self) -> None:
        """PLANTED: a refusal the endpoint CHARGED for, worded like an empty body.

        The wording is the only handle the empty-completion class has, so a
        classifier that reached for it first would re-send a call whose spend is
        already in the ledger and in the budget — a second charge on one unit of
        a frozen design. What decides is the class of the failure: usage rides
        this one, so it is a completion that was produced and refused.
        """

        billed = charged_no_completion(EMPTY_BODY_ERROR)
        assert instrument.transport_trigger(billed) is None

    def test_a_refused_payload_quoting_a_status_is_not_a_status_from_the_endpoint(
        self,
    ) -> None:
        """PLANTED: the body the model wrote mentions an HTTP 503.

        A `ValidationError` renders the input it rejected, so a status the MODEL
        wrote appears in the message exactly where a status the ENDPOINT
        returned would. Reading the wording of a payload that arrived is the
        defect; the class is checked first, and a refused payload is a sample
        whatever it says.
        """

        planted = '{"rationale_text": "HTTP 503"}'
        with pytest.raises(ValidationError) as caught:
            ModelAuthoredVoteBallot.model_validate_json(planted)
        assert "HTTP 503" in str(caught.value)
        assert instrument.transport_trigger(caught.value) is None

    def test_an_unaccounted_attempt_says_what_it_cannot_know(self) -> None:
        """The record may not claim a charge this side never sees.

        `_raw_from_response_body` refuses a body with no completion in it BEFORE
        it reads that body's `usage` block, so a 2xx the provider billed for and
        then answered emptily reaches this wrapper as a bare `RuntimeError` with
        nothing riding it. The ledger row is zero tokens — what is KNOWN, not
        what was spent — and `TRANSPORT_RETRY`, which the manifest quotes
        verbatim, says so instead of claiming the usage was recorded. Moving the
        usage read ahead of the refusal is a change to the provider client and
        would turn this red, which is the point: the wording would then be
        wrong.
        """

        function = (
            (_REPO_ROOT / "llm" / "featherless_client.py")
            .read_text(encoding="utf-8")
            .split("def _raw_from_response_body")[1]
        )
        refuses = function.index("refusing to record an empty completion")
        reads_usage = function.index('usage = body.get("usage")')
        assert refuses < reads_usage
        assert (
            "may have been billed for tokens this side cannot see"
            in instrument.TRANSPORT_RETRY
        )
        assert "recorded as an unaccounted attempt carrying zero tokens" in (
            instrument.TRANSPORT_RETRY
        )
        # And the ledger row the run actually writes is that zero.
        inner = NoCompletionProvider(mode="empty_body", failures=1)
        client = self._client(inner)
        self._call(client)
        unaccounted = [
            call
            for call in client.calls
            if call.model == instrument.UNACCOUNTED_ATTEMPT_MODEL
        ]
        assert [(call.input_tokens, call.output_tokens) for call in unaccounted] == [
            (0, 0)
        ]

    def test_a_permanent_status_outranks_the_body_it_quotes(self) -> None:
        """PLANTED: a 400 whose response body contains the empty-completion
        phrase, and one whose body contains the transport-failure phrase.

        `_format_send_error` writes the status first and quotes the body after
        it, so both markers and the status live in one message. Read body-first
        the wrapper would send a request the endpoint has permanently refused
        four times over; only `_RETRYABLE_STATUS_CODES` are retryable at all,
        and the status is the half the adapter wrote rather than the half the
        endpoint returned.
        """

        for body in (
            "refusing to record an empty completion",
            "on a transport/parse error",
        ):
            permanent = RuntimeError(
                "Featherless chat-completions POST failed: HTTP 400 "
                f"(model='Qwen/Qwen3.6-27B'): {body}"
            )
            assert instrument.transport_trigger(permanent) is None, body
        # The same message with a status that IS retryable stays a retry.
        assert (
            instrument.transport_trigger(RuntimeError(RETRYABLE_STATUS_ERROR))
            == "retryable_status"
        )
        # And an empty body, which carries no status at all, is unaffected.
        assert (
            instrument.transport_trigger(RuntimeError(EMPTY_BODY_ERROR))
            == "empty_completion"
        )

    def test_a_retry_is_counted_only_once_the_next_send_begins(self) -> None:
        """PLANTED: the elapsed deadline cancels the call DURING the backoff.

        `RunDeadline` cancels the coroutine it bounds, and the cancellation can
        land in the wait between two attempts. Counted before the wait, the stop
        would report one retried call for a call that was only ever sent once;
        the attempt that produced nothing is still counted, because it happened.
        """

        class _CancellingSleep:
            def __init__(self) -> None:
                self.waits: list[float] = []

            async def __call__(self, seconds: float) -> None:
                self.waits.append(seconds)
                raise asyncio.CancelledError

        inner = NoCompletionProvider(mode="empty_body", failures=99)
        sleep = _CancellingSleep()
        client = instrument._InstrumentClient(
            inner,
            work_clock=instrument._ModelWorkClock(max_seconds=3600.0),
            sleep=sleep,
        )
        with pytest.raises(asyncio.CancelledError):
            self._call(client)
        assert inner.attempts == 1
        assert sleep.waits == [instrument.TRANSPORT_BACKOFF_BASE_SECONDS]
        attempts = client.attempts()
        assert attempts.retried_calls == 0
        assert attempts.unaccounted_attempts == 1

    def test_the_classifier_keys_on_wording_the_adapter_still_uses(self) -> None:
        """The empty-completion class has no type of its own to match on.

        `llm/featherless_client.py` raises a bare `RuntimeError` for a body with
        no `choices`, so the message is the only handle there is. This reads
        that module's SOURCE — text, never an import, so this file gains no
        route to a real client — and holds every fragment the classifier keys
        on, plus the retryable-status set, to what the adapter actually writes.
        A rewording there turns this red instead of turning a retry into a stop
        mid-run.
        """

        source = (_REPO_ROOT / "llm" / "featherless_client.py").read_text(
            encoding="utf-8"
        )
        for marker in instrument._EMPTY_COMPLETION_MARKERS:
            assert marker in source, marker
        assert instrument._TRANSPORT_FAILURE_MARKER in source
        assert "POST failed: HTTP " in source
        bound = next(
            node
            for node in ast.parse(source).body
            if isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "_RETRYABLE_STATUS"
        )
        # ``frozenset({...})`` — the set literal inside the call is the part a
        # literal evaluation can read.
        call = cast(ast.Call, bound.value)
        assert set(ast.literal_eval(call.args[0])) == set(
            instrument._RETRYABLE_STATUS_CODES
        )

    def test_a_retried_run_reports_the_attempts_per_arm(self, tmp_path: Path) -> None:
        """PLANTED at the RUN, not the wrapper: the first call of the first arm
        comes back empty once. The unit still resolves, and the arm summary
        carries what it cost — which is the difference between a clean run and
        a retried one that would otherwise read the same."""

        inner = NoCompletionProvider(mode="empty_body", failures=1)
        report = run_instrument(output_dir=tmp_path, client=inner, units=1)
        reference = next(arm for arm in report.arms if arm.arm == "repaired_clock")
        candidate = next(arm for arm in report.arms if arm.arm == "combined_accounts")
        assert reference.retried_calls == 1
        assert reference.unaccounted_attempts == 1
        assert dict(reference.attempts_by_trigger) == {"empty_completion": 1}
        assert reference.units_with_retries == 1
        assert candidate.retried_calls == 0
        assert candidate.units_with_retries == 0
        assert instrument.UNACCOUNTED_ATTEMPT_MODEL in report.model_ids

    def test_an_exhausted_call_stops_the_run_with_its_attempts(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """PLANTED: an endpoint that answers nothing at all. Four attempts, then
        the stop, with the attempts in the partial accounting a stop reports —
        the same place the spent-but-unusable calls go."""

        monkeypatch.setattr(instrument, "TRANSPORT_BACKOFF_BASE_SECONDS", 0.0)
        inner = NoCompletionProvider(mode="empty_body", failures=99)
        with pytest.raises(InstrumentAborted) as caught:
            run_instrument(output_dir=tmp_path, client=inner, units=1)
        partial = caught.value.partial
        assert "TransportAttemptsExhausted" in partial.reason
        assert partial.completed_units == 0
        attempts = partial.attempts_by_arm["repaired_clock"]
        assert attempts.retried_calls == 1
        assert attempts.unaccounted_attempts == 4
        assert "4 unaccounted attempts (empty_completion 4)" in partial.describe()


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


class TestTruncationIsObservedAsWellAsInferred:
    """The truncation stop reads two signals and prefers neither.

    The fourth run stopped at unit 26 of 100 on a ballot that reached its
    1,024-token output cap, and nothing in the tree recorded the provider's own
    word for it: the stop was INFERRED from `output_tokens >= max_tokens`
    alone (`tasks/diagnosis-2026-09-15-truncation-stop.md`, §5 fix D, approved
    as §6 decision 3). The stop condition's WORDS are unchanged — `STOP_RULE`
    already stops on "a per-call response that reached its output cap", and a
    `finish_reason` of `"length"` is the provider saying exactly that — and its
    evidence is widened: either signal stops the run, and a call on which the
    two disagree is counted rather than silently resolved in favour of one.

    A null observation is not a disagreement: an absent reading contradicts
    nothing, which is what the two null rows below pin.
    """

    def _client(self, inner: Any, **kwargs: Any) -> Any:
        clock = instrument._ModelWorkClock(max_seconds=3600.0)
        return instrument._InstrumentClient(inner, work_clock=clock, **kwargs)

    def _call(self, client: Any, *, max_tokens: int) -> None:
        asyncio.run(
            client.complete(
                prompt="p", schema=None, max_tokens=max_tokens, temperature=0.2
            )
        )

    #: The card's decision table, one row per case: what the provider reported,
    #: how many output tokens it charged against the 1,024 vote cap, whether
    #: the run stops, and whether the row counts as a disagreement.
    @pytest.mark.parametrize(
        ("finish_reason", "output_tokens", "stops", "disagreements"),
        [
            ("length", 1024, True, 0),
            ("length", 900, True, 1),
            ("stop", 1024, True, 1),
            ("stop", 900, False, 0),
            (None, 1024, True, 0),
            (None, 900, False, 0),
        ],
    )
    def test_the_decision_table_is_the_whole_rule(
        self,
        finish_reason: str | None,
        output_tokens: int,
        stops: bool,
        disagreements: int,
    ) -> None:
        cap = AUTHORIZED_SAMPLING.vote_max_tokens
        inner = _StubClient(output_tokens=output_tokens, finish_reason=finish_reason)
        client = self._client(inner)
        if stops:
            with pytest.raises(PerCallCapExceeded, match="a truncation is a stop"):
                self._call(client, max_tokens=cap)
        else:
            self._call(client, max_tokens=cap)
        rows = client.take()
        # Recorded either way, and the reading recorded is the one the provider
        # gave: a stop drops no row, because a stop's partial accounting has to
        # carry the call that caused it.
        assert [row.finish_reason for row in rows] == [finish_reason]
        usage = instrument.ArmUsage().plus(rows)
        assert usage.cap_signal_disagreements == disagreements

    def test_the_two_planted_disagreements_are_red_without_the_reading(self) -> None:
        """PLANTED, both directions, at the authorized 1,024-token vote cap.

        `"length"` at 900 tokens is the case the counters CANNOT see: below the
        cap, so the inference passes it, and the provider says it was cut off.
        `"stop"` at exactly 1,024 is the reverse: the inference stops it and the
        provider's word says otherwise. Before this card the first was not a
        stop at all and the second was a stop nobody could question; both are
        now stops, and both are counted.
        """

        cap = AUTHORIZED_SAMPLING.vote_max_tokens
        observed_only = self._client(
            _StubClient(output_tokens=900, finish_reason="length")
        )
        with pytest.raises(PerCallCapExceeded) as below_cap:
            self._call(observed_only, max_tokens=cap)
        message = str(below_cap.value)
        assert "finish_reason 'length'" in message
        assert f"on 900 of {cap} output tokens" in message
        assert "the two signals disagree" in message
        assert (
            instrument.ArmUsage().plus(observed_only.take()).cap_signal_disagreements
            == 1
        )

        inferred_only = self._client(
            _StubClient(output_tokens=cap, finish_reason="stop")
        )
        with pytest.raises(PerCallCapExceeded) as at_cap:
            self._call(inferred_only, max_tokens=cap)
        at_cap_message = str(at_cap.value)
        # The inference's own wording, unchanged: this half of the rule is the
        # one that has always been there.
        assert f"a response reached its {cap}-token output cap ({cap} tokens)" in (
            at_cap_message
        )
        assert "the two signals disagree" in at_cap_message
        assert (
            instrument.ArmUsage().plus(inferred_only.take()).cap_signal_disagreements
            == 1
        )

    def test_the_agreement_row_stops_without_counting_a_disagreement(self) -> None:
        """The third case, which is what keeps the counter honest: a provider
        that says `"length"` at exactly the cap agrees with the inference, so
        the run stops and NOTHING is counted. Without this the counter could be
        wired to fire on every truncation stop and still look correct."""

        cap = AUTHORIZED_SAMPLING.vote_max_tokens
        client = self._client(_StubClient(output_tokens=cap, finish_reason="length"))
        with pytest.raises(PerCallCapExceeded) as stopped:
            self._call(client, max_tokens=cap)
        message = str(stopped.value)
        assert f"a response reached its {cap}-token output cap" in message
        assert "finish_reason 'length'" in message
        assert "the two signals disagree" not in message
        assert instrument.ArmUsage().plus(client.take()).cap_signal_disagreements == 0

    def test_a_silent_provider_is_stopped_by_the_inference_alone(self) -> None:
        """The adapters this card does not edit report nothing, so their calls
        are judged exactly as they were: the counters stop the run and the
        message claims no observation that was never made."""

        cap = AUTHORIZED_SAMPLING.vote_max_tokens
        client = self._client(_StubClient(output_tokens=cap))
        with pytest.raises(PerCallCapExceeded) as stopped:
            self._call(client, max_tokens=cap)
        message = str(stopped.value)
        assert message == (
            f"a response reached its {cap}-token output cap ({cap} tokens); "
            "a truncation is a stop, not a datum"
        )

    def test_a_refused_completion_carries_the_reading_the_fourth_run_lost(
        self,
    ) -> None:
        """PLANTED on the path the fourth run actually stopped through.

        A body cut off mid-string fails `model_validate_json`, so the run's stop
        came off the parse-failure metadata and not off a response. A reading
        that reached only responses would miss precisely this call: here the
        provider says `"length"` at 900 tokens, below the cap, so ONLY the
        observation can stop it.
        """

        cap = AUTHORIZED_SAMPLING.vote_max_tokens
        provider = BurnedCallProvider(output_tokens=900, finish_reason="length")
        client = self._client(provider)
        with pytest.raises(PerCallCapExceeded, match="finish_reason 'length'"):
            asyncio.run(
                client.complete(
                    prompt="a vote prompt",
                    schema=ModelAuthoredVoteBallot,
                    max_tokens=cap,
                    temperature=AUTHORIZED_SAMPLING.vote_temperature,
                    agent_id="p-1",
                )
            )
        rows = client.take()
        assert [(row.disposition, row.finish_reason) for row in rows] == [
            ("billed_and_refused", "length")
        ]
        assert instrument.ArmUsage().plus(rows).cap_signal_disagreements == 1

    def test_a_refused_completion_from_a_silent_provider_reads_null(self) -> None:
        """The same path with no reading on the metadata: recorded as null and
        judged on the counters alone, which is what an adapter that maps no
        `finish_reason` produces."""

        provider = BurnedCallProvider(output_tokens=900, finish_reason=None)
        client = self._client(provider)
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
        rows = client.take()
        assert [(row.disposition, row.finish_reason) for row in rows] == [
            ("billed_and_refused", None)
        ]
        assert instrument.ArmUsage().plus(rows).cap_signal_disagreements == 0

    def test_an_attempt_that_produced_nothing_records_null(self) -> None:
        """The `unaccounted` row of the table: nothing came back, so there is
        nothing to have reported a reason. Null, and never a disagreement."""

        inner = NoCompletionProvider(mode="empty_body", failures=1)
        client = self._client(inner, per_attempt_timeout_seconds=60.0)
        self._call(client, max_tokens=AUTHORIZED_SAMPLING.vote_max_tokens)
        rows = client.take()
        assert [(row.disposition, row.finish_reason) for row in rows] == [
            ("unaccounted", None),
            ("resolved", FAKE_FINISH_REASON),
        ]
        assert instrument.ArmUsage().plus(rows).cap_signal_disagreements == 0

    def test_an_attempt_the_work_window_cut_off_records_null(self) -> None:
        """The `aborted` row: the run's own window ended the attempt, so the
        provider said nothing about how generation stopped."""

        inner = NoCompletionProvider(mode="stall", failures=1, stall_seconds=5.0)
        clock = instrument._ModelWorkClock(max_seconds=0.2)
        client = instrument._InstrumentClient(
            inner, work_clock=clock, per_attempt_timeout_seconds=60.0
        )
        with pytest.raises(RunDeadlineExceeded, match="exhausted mid-call"):
            self._call(client, max_tokens=AUTHORIZED_SAMPLING.vote_max_tokens)
        rows = client.take()
        assert [(row.disposition, row.finish_reason) for row in rows] == [
            ("aborted", None)
        ]
        assert instrument.ArmUsage().plus(rows).cap_signal_disagreements == 0

    def test_the_identity_stop_still_comes_first(self) -> None:
        """A checkpoint swap is still reported as a checkpoint swap, not as a
        truncation: the served-model check runs before either signal is read,
        and the row it leaves still carries what the provider said."""

        cap = AUTHORIZED_SAMPLING.vote_max_tokens
        client = self._client(
            _StubClient(output_tokens=cap, finish_reason="length"),
            expected_model=AUTHORIZED_MODEL,
        )
        with pytest.raises(instrument.ProviderIdentityMismatch, match="stub"):
            self._call(client, max_tokens=cap)
        assert [row.finish_reason for row in client.take()] == ["length"]

    def test_the_report_counts_disagreements_per_arm(self, tmp_path: Path) -> None:
        """The count is reported, not just held: one field per arm beside
        `retried_calls` and `unaccounted_attempts`. A dry run's double reports
        `"stop"` on every call and none of them reaches a cap, so both arms
        report zero — which is the reading a run with no contradiction has."""

        report = run_instrument(output_dir=tmp_path, units=1)
        assert [arm.cap_signal_disagreements for arm in report.arms] == [0, 0]
        assert all(
            "cap_signal_disagreements" in arm.model_dump() for arm in report.arms
        )

    def test_the_committed_calibration_and_profile_parse_and_read_null(self) -> None:
        """Records written before this card still parse, and read null.

        `CALIBRATION_SCHEMA` stays `fresh-deduction-calibration/1` and the usage
        profile stays `fresh-deduction-usage-profile/1`: an added optional field
        defaulting to null changes how no existing record reads, and this is the
        proof. A double's `"stop"` is the double's own word — the ARCHIVE is
        silent, and stays silent.
        """

        assert instrument.CALIBRATION_SCHEMA == "fresh-deduction-calibration/1"
        payload = json.loads(
            (
                _REPO_ROOT
                / "audits"
                / "deduction-candidate"
                / "calibration-2026-09-14"
                / "calibration.json"
            ).read_text(encoding="utf-8")
        )
        assert payload["report_schema"] == instrument.CALIBRATION_SCHEMA
        calls = [
            instrument.CalibrationCall.model_validate(row) for row in payload["calls"]
        ]
        assert calls, "the committed calibration carries no call rows"
        assert {call.finish_reason for call in calls} == {None}

        # The profile committed BEFORE the reading was captured — the three
        # stopped runs' rows, kept beside the current one since 2026-09-15 —
        # still loads and still reads null, which is the compatibility claim.
        archived = json.loads(
            usage_replay_double.STOPPED_RUNS_PROFILE_PATH.read_text(encoding="utf-8")
        )
        assert archived["schema"] == "fresh-deduction-usage-profile/1"
        assert {row.finish_reason for row in stopped_runs_profile().calls} == {None}
        # What the double puts on the wire for a silent archive is its own word,
        # said so at the constant rather than mistaken for a measurement.
        assert usage_replay_double.REPLAYED_FINISH_REASON == "stop"
        # And the profile the fifth authorization refreshed answers that null
        # with a reading of its own, on every row: a MEASUREMENT this time,
        # written by `--refresh-usage-profile` off the calibration's rows.
        profile = json.loads(
            usage_replay_double.PROFILE_PATH.read_text(encoding="utf-8")
        )
        assert profile["schema"] == "fresh-deduction-usage-profile/1"
        loaded = usage_replay_double.UsageProfile.load()
        assert {row.finish_reason for row in loaded.calls} == {"stop"}


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
            "transport_attempts": instrument.TransportAttempts(),
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
        apart is wrong wherever it is applied.

        The rule now lives in the meeting layer, where the recording-time guard
        can reach it too; this grader-side pin stays because this is where the
        verdict it decides is consumed."""

        assert names_player("tick 4: p-10 in MEDBAY.", "p-1") is False
        assert names_player("tick 4: p-1 in MEDBAY.", "p-1") is True

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
            "turn 4,096 output / vote 1,024",
            "turn temperature 0.4 / vote temperature 0.2",
            "3,844,000 input / 422,000 output run-level",
            "116,000 input / 16,000 output per unit",
            "6 h of model work within an 8 h elapsed deadline",
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
        parent's is an amendment, and its abbreviated hash has to appear in one
        of the dated logs. Three were pre-run — the decision rule's third
        condition with the sampling binding, the stop rule's reversal, and the
        relevance rubric — and two of them went unlogged until round 5 of the
        instrument's pull request. The stop rule's transport clause of
        2026-09-13 is the first that belongs in a post-run log instead, which is
        why the search below is over every log rather than the first one.
        """

        amendments = _frozen_analysis_amendments()
        if amendments is None:
            pytest.skip("no full git history here; the amendment log cannot be walked")
        assert amendments, "no post-freeze revision of the frozen analysis was found"
        section = self._every_amendment_section()
        unlogged = {
            commit: moved
            for commit, moved in amendments.items()
            if f"`{commit}`" not in section
        }
        assert unlogged == {}, f"amendments missing from the log: {unlogged}"

    def _post_run_amendments_section(self, date: str = "2026-09-10") -> str:
        text = self._text()
        start = text.index(f"## Amendments after the stopped run of {date}")
        return text[start : text.index("\n## ", start + 1)]

    def _every_amendment_section(self) -> str:
        """Every dated amendment log this document carries, as one string.

        The pre-run log and one post-run log per stopped run. The completeness
        walk below reads all of them, because WHICH log an amendment belongs in
        is a property of when it was made, and "logged nowhere" is the defect
        that walk exists to catch.
        """

        sections = [self._amendments_section()]
        text = self._text()
        marker = "## Amendments after the stopped run of "
        cursor = 0
        while True:
            found = text.find(marker, cursor)
            if found == -1:
                return "\n".join(sections)
            cursor = found + 1
            sections.append(text[found : text.index("\n## ", cursor)])

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

    def test_the_transport_amendment_names_its_reason_and_a_real_commit(self) -> None:
        """The 2026-09-13 log, held to what the 2026-09-10 log is held to.

        Its own dated section, because it was written after a unit ran; its own
        commit, resolved against this history rather than taken on the
        document's word; and its reason, which is the one thing the stopped run
        of that date establishes — a 2xx body with no completion in it.

        This entry moves the frozen analysis, which the entries above do not, so
        it says which constant moved and which did not, and the stop-rule
        quotation further down this document carries the new bytes (the
        verbatim check above is what holds that).
        """

        section = self._post_run_amendments_section("2026-09-13")
        collapsed = " ".join(section.split())
        assert "an attempt that produced nothing is retried" in collapsed
        assert "retried up to three times" in collapsed
        assert "no `choices`" in collapsed
        assert "`STOP_RULE` gains a transport clause" in collapsed
        for unmoved in (
            "PRIMARY_OUTCOME",
            "DECISION_RULE",
            "MINIMUM_ACTIONABLE_EFFECT_UNITS",
            "WRONGFUL_EJECTION_TRADEOFF",
        ):
            assert unmoved in collapsed
        # Every dated entry of this section, however it is qualified, names the
        # commit that carried it; exactly one of them is the entry that moved
        # the frozen analysis, and a second one would be a second unlogged move.
        commits = re.findall(r"\*\*2026-09-13[^(*]*\(`([0-9a-f]{7,40})`\)", collapsed)
        assert commits, "an amendment entry names no commit"
        assert collapsed.count("`STOP_RULE` gains a transport clause") == 1
        if _git("rev-parse", "--is-shallow-repository").stdout.strip() != "false":
            pytest.skip("no full history here; the named commit cannot be resolved")
        for commit in commits:
            assert (
                _git("rev-parse", "--verify", f"{commit}^{{commit}}").returncode == 0
            ), f"{commit} is not a commit here"
            touched = _git(
                "show", "--name-only", "--format=", commit, "--", _INSTRUMENT_REPO_PATH
            )
            assert _INSTRUMENT_REPO_PATH in touched.stdout
            assert (
                _git("merge-base", "--is-ancestor", commit, "HEAD").returncode == 0
            ), f"named but not an ancestor of HEAD: {commit}"

    def _diagnosis_amendments_section(self) -> str:
        text = self._text()
        start = text.index("## Amendments after the diagnosis of 2026-09-13")
        return text[start : text.index("\n## ", start + 1)]

    def test_each_diagnosis_entry_names_a_commit_that_carries_what_it_claims(
        self,
    ) -> None:
        """An entry does not merely name a commit that exists; it names the one
        its own mechanisms arrived in.

        The check above resolves the named commit and asserts it touched the
        instrument, which a review found is not enough: a later commit's work
        was described inside an earlier commit's entry, and every assertion
        still passed. Three things here instead. Each entry's backticked names
        are looked up in the instrument AT the commit that entry names, so a
        mechanism logged against a commit that predates it is red; each entry
        must name at least one thing its own commit INTRODUCED, so an entry
        cannot be anchored to a commit by naming only what was already there;
        and the section's entries are the dates this log carries, so folding one
        into another is red rather than silent. Only names the instrument
        carries today are checked, so prose in backticks is not read as a
        symbol — which is also the limit of this gate: a mechanism described
        without naming it cannot be attributed by any check over the text.
        """

        if _git("rev-parse", "--is-shallow-repository").stdout.strip() != "false":
            pytest.skip("no full history here; the named commits cannot be read")
        section = self._diagnosis_amendments_section()
        offenders = _names_an_entry_credits_to_a_commit_without_them(
            section,
            _instrument_source_at,
            _instrument_source_at("HEAD"),
        )
        assert offenders == {}, f"entries crediting commits that lack them: {offenders}"
        carried_now = _instrument_source_at("HEAD")
        entries = _entries_and_the_names_they_attribute(section)
        for _date, commit, named in entries:
            before = _instrument_source_at(f"{commit}^")
            introduced = sorted(
                name for name in named if name in carried_now and name not in before
            )
            assert introduced, f"{commit}'s entry names nothing that commit introduced"
        assert [date for date, _commit, _named in entries] == [
            "2026-09-13",
            "2026-09-14",
        ]

    def test_the_entry_check_is_red_when_the_later_work_is_folded_back(
        self,
    ) -> None:
        """The planted case, which is the arrangement a review actually found.

        Delete the 2026-09-14 heading and its body falls inside the 2026-09-13
        entry — exactly what the committed document said before this round, with
        `AbandonedSpend`, the tail check and the widened arm surface all credited
        to a commit that carries none of them. The same pure check over the same
        history then names that commit and the symbols it lacks.
        """

        if _git("rev-parse", "--is-shallow-repository").stdout.strip() != "false":
            pytest.skip("no full history here; the named commits cannot be read")
        section = self._diagnosis_amendments_section()
        heading = next(
            line for line in section.splitlines() if line.startswith("**2026-09-14 (`")
        )
        folded = section.replace(heading, "The commit above also:")
        assert _entries_and_the_names_they_attribute(folded)[0][0] == "2026-09-13"
        offenders = _names_an_entry_credits_to_a_commit_without_them(
            folded,
            _instrument_source_at,
            _instrument_source_at("HEAD"),
        )
        assert list(offenders) == ["78b136bd"], offenders
        assert "AbandonedSpend" in offenders["78b136bd"]
        assert "assert_the_tail_can_be_recorded" in offenders["78b136bd"]
        assert "agents/strategic/prompts/loader.py" in offenders["78b136bd"]

    def test_the_enforcement_section_quotes_the_reservation_policy(self) -> None:
        """The units of account are a thing the code enforces, so this document
        states them in the module's own words.

        `RESERVATION_POLICY` is built from the constants the table above binds —
        the two per-call caps, the living-voter count and the two calibrated
        per-unit figures — so a moved cap changes the constant, this quotation
        and the gate together, and a document that described the schedule in
        prose could not drift from what the budget reserves.
        """

        section = " ".join(self._enforcement_section().split())
        assert " ".join(instrument.RESERVATION_POLICY.split()) in section
        assert "assert_limits_are_feasible" in section

    def test_the_diagnosis_amendment_names_its_reason_and_a_real_commit(self) -> None:
        """The 2026-09-13 diagnosis log, held to what the two stop logs are.

        Its own dated section, because it follows a diagnosis rather than a
        stop; its own commit, resolved against this history rather than taken on
        the document's word; and its reason, which is the one thing the three
        stopped runs establish — a design sized in one unit of account and
        enforced in another.
        """

        section = self._diagnosis_amendments_section()
        collapsed = " ".join(section.split())
        assert "SIZED in charged tokens and ENFORCED in reserved ones" in collapsed
        assert "Under the limits merged on 2026-09-07 it refuses" in collapsed
        assert "9,216 output tokens" in collapsed
        assert "The frozen analysis does not move here" in collapsed
        for unmoved in (
            "PRIMARY_OUTCOME",
            "DECISION_RULE",
            "MINIMUM_ACTIONABLE_EFFECT_UNITS",
            "WRONGFUL_EJECTION_TRADEOFF",
            "STOP_RULE",
        ):
            assert unmoved in collapsed
        commits = re.findall(r"\*\*2026-09-13[^(*]*\(`([0-9a-f]{7,40})`\)", collapsed)
        assert len(commits) == 1
        if _git("rev-parse", "--is-shallow-repository").stdout.strip() != "false":
            pytest.skip("no full history here; the named commit cannot be resolved")
        for commit in commits:
            assert (
                _git("rev-parse", "--verify", f"{commit}^{{commit}}").returncode == 0
            ), f"{commit} is not a commit here"
            touched = _git(
                "show", "--name-only", "--format=", commit, "--", _INSTRUMENT_REPO_PATH
            )
            assert _INSTRUMENT_REPO_PATH in touched.stdout
            assert (
                _git("merge-base", "--is-ancestor", commit, "HEAD").returncode == 0
            ), f"named but not an ancestor of HEAD: {commit}"

    def test_no_frozen_analysis_byte_has_moved_since_the_last_logged_amendment(
        self,
    ) -> None:
        """The frozen design is byte-identical to the last revision that logged one.

        The walk above catches an amendment that moved a frozen constant without
        logging it; this is the stronger statement this card owes, and it is
        taken against the tree rather than against the log: every frozen
        constant at HEAD equals the same constant at the revision the last
        stopped-run entry names. A card that changed one of them, logged or not,
        turns this red.
        """

        if _git("rev-parse", "--is-shallow-repository").stdout.strip() != "false":
            pytest.skip("no full history here; the revision cannot be read")
        collapsed = " ".join(self._post_run_amendments_section("2026-09-13").split())
        named = re.findall(r"\*\*2026-09-13[^(*]*\(`([0-9a-f]{7,40})`\)", collapsed)
        assert named, "the last stopped-run log names no commit"
        last = named[-1]
        before = _frozen_analysis_at(last)
        assert before is not None, last
        now = _frozen_analysis_at("HEAD")
        assert now is not None
        moved = [
            name for name in _FROZEN_ANALYSIS_CONSTANTS if before[name] != now[name]
        ]
        assert moved == [], f"the frozen analysis moved since {last}: {moved}"

    def test_the_manifest_quotes_the_two_clauses_of_2026_09_14_verbatim(self) -> None:
        """The owner's two sentences, byte for byte, under their dated headings.

        The gates look for these bytes, so a paraphrase authorizes nothing and a
        document that quoted them loosely would leave a runner refused with
        every other check green. The module holds one copy and this document the
        other, and this is what keeps the two identical.
        """

        text = self._text()
        assert instrument.RESUMPTION_CLAUSE in text
        assert instrument.CALIBRATION_CLAUSE in text
        assert "## Resumption clause (2026-09-14)" in text
        assert "## Development calibration (2026-09-14)" in text
        assert "assert_resume_is_authorized" in text
        assert "assert_calibration_is_authorized" in text

    def test_the_resumption_section_names_the_stop_it_cannot_carry(self) -> None:
        """The half of the clause the code cannot make true, stated as such.

        The clause names "a process crash" as resumable with the interrupted
        unit's spend carried. `run_instrument` makes that arithmetic for every
        stop that unwinds the process, interrupts included
        (`test_an_interrupt_leaves_the_pairs_spend_in_the_checkpoint_and_reraises`);
        a SIGKILL, an OOM kill or a power loss runs no handler and writes no
        checkpoint, so the interrupted pair's spend is carried by the runner or
        by nobody. A document that asserted the carry for that class too would
        be claiming a mechanism this tree does not have, which is the error this
        test exists to keep out.
        """

        text = self._text()
        section = text.split("## Resumption clause (2026-09-14)", 1)[1].split("\n## ")[
            0
        ]
        # Reflowed, because these are sentences a hard wrap may break anywhere
        # and what is asserted is what the section SAYS.
        section = " ".join(section.split())
        for stated in (
            "SIGKILL",
            "power loss",
            "writes no final checkpoint",
            "is the runner's step, not the instrument's",
        ):
            assert stated in section, stated
        assert "BaseException" in section

    def test_the_calibration_section_states_its_own_limits(self) -> None:
        """Each calibration ceiling is in the document a runner reads.

        The same rule the authorized values are held to: the instrument
        enforces the numbers, and the section that authorizes the spend has to
        name them.
        """

        text = self._text()
        for quoted in (
            "60,000 input / 12,000 output",
            "600,000 input / 120,000 output",
            "1 h of model work within a 1.5 h elapsed deadline",
            "5 paired seeds x 2 arms = 10 units",
        ):
            assert quoted in text, quoted

    def test_the_calibration_limits_are_the_numbers_the_section_quotes(self) -> None:
        """And those numbers are the module's, not a second copy of them."""

        limits = instrument.CALIBRATION_LIMITS
        assert (limits.unit_max_input_tokens, limits.unit_max_output_tokens) == (
            60_000,
            12_000,
        )
        assert (limits.run_max_input_tokens, limits.run_max_output_tokens) == (
            600_000,
            120_000,
        )
        assert (limits.model_work_seconds, limits.elapsed_seconds) == (3_600, 5_400)
        assert limits.max_cost_usd == instrument.AUTHORIZED_MAX_COST_USD
        assert instrument.CALIBRATION_PAIRED_SEEDS == 5
        assert instrument.calibration_units() == 10
        # The three the calibration does NOT re-size.
        assert instrument.AUTHORIZED_SAMPLING == AUTHORIZED_SAMPLING
        assert instrument.MAX_TRANSPORT_ATTEMPTS == 4
        assert instrument.PER_ATTEMPT_TIMEOUT_SECONDS == 180.0

    def test_the_manifest_states_what_a_second_sitting_must_do(self) -> None:
        """Four operational rules, each of them a refusal in the code.

        A runner reads this document and not the module, so a rule the code
        enforces and the document omits is a stop discovered live. Each sentence
        here has a test behind it in `TestCheckpointAndResume`: the fresh output
        directory, the unit count no narrower than the checkpoint, the
        checkpoint that keeps advancing, and the spend a stop abandons mid-pair
        that the next sitting is charged for.
        """

        collapsed = " ".join(self._text().split())
        for stated in (
            "pass a NEW `--output-dir`",
            "a resume narrower than its checkpoint is refused",
            "`--checkpoint` defaults to the `--resume` path",
            "the pair its stop abandoned",
            "one final checkpoint is written on the stop path",
        ):
            assert stated in collapsed, stated

    def _fourth_authorization_section(self) -> str:
        text = self._text()
        start = text.index("## Fourth authorization (2026-09-14)")
        return text[start : text.index("\n## ", start + 1)]

    def test_the_fourth_authorization_section_records_the_change_and_its_basis(
        self,
    ) -> None:
        """The dated entry for the re-sizing, held to the same bar as the rest.

        A limits change is a spending decision, so the section that records it
        has to name the card that authorized it, the measurement it was sized
        from, the one observation that forced the turn cap, and the arithmetic
        the raise moves — not just the numbers, which the table already carries.
        The commit it names is resolved against this history rather than taken
        on the document's word, and is required to have moved the instrument.
        """

        section = " ".join(self._fourth_authorization_section().split())
        for stated in (
            "fresh-deduction-authorization-4.md",
            "calibration-2026-09-14/calibration.json",
            "2,036 output tokens against the 2,048 cap",
            "3 x 4,096 + 3 x 1,024 = 15,360",
            "the per-unit output ceiling is 16,000 and not the 14,000",
            "`CALIBRATION_SAMPLING` freezes the calibration's draw",
            "Round-3 re-binding, same date",
        ):
            assert stated in section, stated
        assert f"turn {instrument.AUTHORIZED_TURN_MAX_TOKENS:,} output" in section
        # The round-3 entry closes the two obligations the entry above opened,
        # and it has to say so in the band that re-binding actually moved the
        # row to, rather than in a span retyped here: a document recording a
        # different one would be describing a re-binding nobody made. That band
        # is history now -- the fourth freeze's 7000-7999 became development
        # data on 2026-09-15 -- so it is read off the module's own record of it,
        # which still catches an entry naming a band this generator never froze.
        # A dated entry is not rewritten when the band moves again; what the
        # LIVE band is checked against is the row itself, in
        # `TestTheManifestBindsTheBandTheRunWouldDraw`.
        rebound = next(
            converted.band
            for converted in CONVERTED_BANDS
            if converted.manifest_path.endswith("manifest-band-7000-7999.json")
        )
        assert f"now binds {rebound.first_seed}-{rebound.last_seed}" in section
        commits = re.findall(r"\*\*2026-09-14[^(*]*\(`([0-9a-f]{7,40})`\)", section)
        assert len(commits) == 1
        if _git("rev-parse", "--is-shallow-repository").stdout.strip() != "false":
            pytest.skip("no full history here; the named commit cannot be resolved")
        for commit in commits:
            assert (
                _git("rev-parse", "--verify", f"{commit}^{{commit}}").returncode == 0
            ), f"{commit} is not a commit here"
            touched = _git(
                "show", "--name-only", "--format=", commit, "--", _INSTRUMENT_REPO_PATH
            )
            assert _INSTRUMENT_REPO_PATH in touched.stdout

    def test_the_enforcement_section_quotes_the_transport_retry(self) -> None:
        """The retry is a thing the instrument DOES, so this document states it
        in the module's own words rather than in a paraphrase that could drift
        from the bound the code enforces."""

        section = " ".join(self._enforcement_section().split())
        assert " ".join(instrument.TRANSPORT_RETRY.split()) in section

    def test_the_stop_rule_and_the_manifest_name_the_bound_the_code_enforces(
        self,
    ) -> None:
        """ "Retried up to three times" is a number, and the number is a constant.

        The frozen rule spells the bound out in words and `MAX_TRANSPORT_ATTEMPTS`
        is what the wrapper actually counts, so a change to one without the other
        would leave the run stopping somewhere the record does not say. The
        quoted rule in this document is the same bytes (the verbatim check
        above), so this pins all three at once.
        """

        assert instrument.MAX_TRANSPORT_ATTEMPTS == 4
        assert "retried up to three times, then a stop" in STOP_RULE
        assert "retried up to three times" in self._text()
        assert f"{instrument.PER_ATTEMPT_TIMEOUT_SECONDS:.0f} s" in self._text()

    def test_the_wall_row_carries_the_constants_the_run_enforces(self) -> None:
        """The widened window, derived from the constants rather than retyped.

        The parametrised check above pins the owner's sentence; this one pins
        the two numbers inside it to `AUTHORIZED_MODEL_WORK_SECONDS` and
        `AUTHORIZED_ELAPSED_SECONDS`, so moving a constant without moving the
        row — or the other way round — is red rather than a document that
        describes a run nobody authorized.
        """

        row = next(
            line
            for line in self._text().splitlines()
            if line.startswith("| Wall-clock deadline")
        )
        work_hours = AUTHORIZED_LIMITS.model_work_seconds / 3600
        elapsed_hours = AUTHORIZED_LIMITS.elapsed_seconds / 3600
        assert f"{work_hours:.0f} h of model work" in row
        assert f"{elapsed_hours:.0f} h elapsed deadline" in row
        assert "widened 2026-09-13" in row

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

    def _seed_band_row(self) -> str:
        row = re.search(r"^\|\s*Seed band\s*\|.*$", self._text(), re.MULTILINE)
        assert row is not None, "the Inputs table carries no Seed band row"
        return row.group(0)

    def test_the_inputs_row_names_every_converted_band(self) -> None:
        """The row that binds one band has to account for the ones it replaced.

        A re-binding leaves a band behind, and the reason it was left behind is
        that a run rendered its prefixes: that is what makes it development
        data rather than a spare held-out set. A row that named only the band
        it now binds would let a reader take a converted band for an unused
        one, so the row names each of them, its date and the record it now
        lives in — read here off `CONVERTED_BANDS` and off each record's own
        `converted` block rather than from a list written down in this test, so
        the NEXT conversion turns this red instead of leaving the document one
        band behind.
        """

        row = self._seed_band_row()
        bound = instrument.manifest_bound_band(self._text())
        for converted in CONVERTED_BANDS:
            if (converted.band.first_seed, converted.band.last_seed) == bound:
                # The band the row still BINDS. A freeze converts the bound band
                # before the card that re-binds the row lands, and in that window
                # the row describes it as the band it draws -- with its own
                # accepted range and skip count -- rather than as one it
                # replaced. Its expiry is
                # `test_a_binding_to_a_converted_record_stays_an_open_obligation`
                # below; a row that binds the LIVE band never takes this branch,
                # because the live band is not a converted one.
                continue
            record = json.loads(
                (_REPO_ROOT / converted.manifest_path).read_text(encoding="utf-8")
            )
            span = f"{converted.band.first_seed}-{converted.band.last_seed}"
            assert span in row, f"the Seed band row does not name {span}"
            assert record["converted"]["date"] in row, (
                f"the Seed band row names {span} without the date it became "
                "development data"
            )
            name = Path(converted.manifest_path).name
            assert name in row, f"the Seed band row names {span} but not {name}"

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


class TestFeasibility:
    """The arithmetic that refuses a run before a provider exists.

    Every case here is the run of 2026-09-13's stop, moved to startup: the
    per-unit output ceiling was sized on charged spend and enforced on reserved
    spend, and nothing about noticing that needed a credential, a connection or
    a held-out prefix.
    """

    def _drive_one_unit(self, ceiling: int) -> int:
        """Six calls at the shipped caps against one per-unit budget.

        The shared budget's own arithmetic, not this module's account of it:
        `GameBudget.preflight` is what `llm/budgeted_client.py` calls before
        every send, with the full per-call cap as the output delta. Returns how
        many of the six calls it let through.
        """

        budget = GameBudget(
            max_cost_usd=0.0, max_input_tokens=10**9, max_output_tokens=ceiling
        )
        caps = [instrument.AUTHORIZED_TURN_MAX_TOKENS] * instrument.UNIT_TURN_CALLS + [
            instrument.AUTHORIZED_VOTE_MAX_TOKENS
        ] * instrument.UNIT_BALLOT_CALLS
        allowed = 0
        for cap in caps:
            usage = TokenUsage(input_tokens=0, output_tokens=cap)
            try:
                budget.preflight(usage=usage, cost_usd=0.0)
            except BudgetExceededError:
                return allowed
            budget.charge(usage=usage, cost_usd=0.0)
            allowed += 1
        return allowed

    def test_the_reservation_is_what_the_shared_budget_actually_reserves(self) -> None:
        """PERTURBED: the same six calls under two ceilings.

        Under the 4,000 merged on 2026-09-07 the budget refuses the FIRST call
        at the raised turn cap although every one of the six is legal and
        untruncated; under the schedule `unit_output_reservation` states it lets
        all six through. The schedule is therefore the budget's own arithmetic
        rather than this module's claim about it, and the gate below refuses
        exactly the ceiling that cannot honour it.
        """

        assert instrument.unit_output_reservation() == 15_360
        assert self._drive_one_unit(_CEILINGS_MERGED_2026_09_07) < 6
        assert self._drive_one_unit(instrument.unit_output_reservation()) == 6

    def test_the_gate_accepts_the_fifth_authorizations_limits(self) -> None:
        """The committed ceilings pay for the run they authorize.

        The fifth authorization card re-sized them from the second live
        calibration of 2026-09-15 precisely so this holds: 16,000 per-unit
        output against a 15,360 schedule, 116,000 per-unit input against the
        largest unit the committed profile carries, and both run ceilings above
        a hundred units at that unit — the OUTPUT one above it plus the turn cap
        its last call reserves. Named for the fourth authorization until that
        day, when the refreshed profile stopped the fourth's own ceilings
        clearing it: the case below.
        """

        instrument.assert_limits_are_feasible()
        assert AUTHORIZED_LIMITS.unit_max_output_tokens >= (
            instrument.unit_output_reservation()
        )
        assert AUTHORIZED_LIMITS.unit_max_input_tokens >= (
            instrument.CALIBRATED_UNIT_INPUT_TOKENS
        )
        assert self._drive_one_unit(AUTHORIZED_LIMITS.unit_max_output_tokens) == 6

    def test_the_fourth_authorizations_run_input_ceiling_is_refused_on_this_profile(
        self,
    ) -> None:
        """PLANTED: 3,710,000, the run-level input ceiling in force until 2026-09-15.

        The finding that opened the fifth authorization, held as arithmetic. The
        second calibration's largest unit charged 38,440 input tokens, so a
        hundred of them need 3,844,000 and the previous ceiling refuses a run of
        the units this evaluation has now measured. Only that one comparison
        moved: the OUTPUT dimension clears the old ceiling with room, which is
        why the same rule LOWERED that one rather than raising it.
        """

        planted = AUTHORIZED_LIMITS.model_copy(
            update={"run_max_input_tokens": 3_710_000}
        )
        with pytest.raises(instrument.LimitsInfeasible) as refused:
            instrument.assert_limits_are_feasible(limits=planted)
        message = str(refused.value)
        assert "run-level input" in message
        assert "3,710,000" in message
        assert "3,844,000" in message
        assert (
            instrument.CALIBRATED_UNIT_INPUT_TOKENS * instrument.planned_units()
            == 3_844_000
        )
        # The output dimension of that same authorization is not what moved.
        instrument.assert_limits_are_feasible(
            limits=AUTHORIZED_LIMITS.model_copy(
                update={"run_max_output_tokens": 459_000}
            )
        )

    def test_the_ceilings_merged_on_2026_09_07_are_still_refused(self) -> None:
        """PLANTED with attempt 3's own number: 4,000 against 15,360.

        The refusal the diagnosis of 2026-09-13 moved to startup is not lifted
        by the re-sizing — it is what the re-sizing answers. The planted ceiling
        is the one that stopped the third live run, and the raised turn cap only
        makes the gap it names wider.
        """

        planted = AUTHORIZED_LIMITS.model_copy(
            update={"unit_max_output_tokens": _CEILINGS_MERGED_2026_09_07}
        )
        with pytest.raises(instrument.LimitsInfeasible) as refused:
            instrument.assert_limits_are_feasible(limits=planted)
        assert "4,000" in str(refused.value)
        assert "15,360" in str(refused.value)

    def test_a_re_sized_authorization_passes(self) -> None:
        """The other half: the diagnosis's provisional re-sizing is feasible."""

        instrument.assert_limits_are_feasible(limits=feasible_limits())

    @pytest.mark.parametrize(
        ("field", "dimension", "in_flight"),
        [
            (
                "run_max_output_tokens",
                "output",
                AUTHORIZED_SAMPLING.turn_max_tokens,
            ),
            ("run_max_input_tokens", "input", 0),
        ],
    )
    def test_a_run_ceiling_below_its_own_units_is_refused(
        self, field: str, dimension: str, in_flight: int
    ) -> None:
        """PLANTED: a run ceiling one token below what its own run reserves.

        The per-unit mismatch one level up. A run whose ceiling cannot pay for
        the units it plans stops near its end on arithmetic rather than on its
        own evidence, which is what two of the four authorized ceilings would
        have done to a complete run even with the per-unit one fixed. The
        OUTPUT bound carries one further turn cap, for the reason
        `test_a_run_output_ceiling_sized_at_exactly_its_units_is_refused`
        plants; the INPUT bound carries none, because an input pre-flight is
        the prompt's own estimated length rather than a cap, and the pair of
        cases here is what holds those two shapes apart.
        """

        calibrated = (
            instrument.CALIBRATED_UNIT_OUTPUT_TOKENS
            if dimension == "output"
            else instrument.CALIBRATED_UNIT_INPUT_TOKENS
        )
        needed = calibrated * instrument.planned_units() + in_flight
        feasible = feasible_limits()
        planted = feasible.model_copy(update={field: needed - 1})
        with pytest.raises(instrument.LimitsInfeasible, match=f"run-level {dimension}"):
            instrument.assert_limits_are_feasible(limits=planted)
        instrument.assert_limits_are_feasible(
            limits=feasible.model_copy(update={field: needed})
        )

    def test_a_run_output_ceiling_sized_at_exactly_its_units_is_refused(
        self,
    ) -> None:
        """PLANTED: the run ceiling this evaluation's own sizing rule produces.

        `GameBudget.preflight` recurses into its parent (`llm/budget.py`), so
        the RUN budget is pre-flighted at a call's full output cap on top of
        everything the run has already charged -- the same two units of account
        the per-unit ceiling was re-sized for, one level up. A run-level output
        ceiling set to exactly a hundred units at the largest measured unit
        therefore cannot pay for its own last call: the run reaches the end of
        its hundredth unit and is refused on the reservation rather than on the
        spend. Until this correction the gate compared against that product
        alone and accepted it, which is the defect planted here; the authorized
        459,000 clears the corrected bound with room, so nothing the fourth
        authorization carries moves.
        """

        turn_cap = AUTHORIZED_SAMPLING.turn_max_tokens
        charged = instrument.CALIBRATED_UNIT_OUTPUT_TOKENS * instrument.planned_units()
        planted = feasible_limits().model_copy(
            update={"run_max_output_tokens": charged}
        )
        with pytest.raises(instrument.LimitsInfeasible) as refused:
            instrument.assert_limits_are_feasible(limits=planted)
        assert f"{charged:,}" in str(refused.value)
        assert f"{turn_cap:,}" in str(refused.value)
        assert f"{charged + turn_cap:,}" in str(refused.value)
        instrument.assert_limits_are_feasible(
            limits=feasible_limits().model_copy(
                update={"run_max_output_tokens": charged + turn_cap}
            )
        )
        assert AUTHORIZED_LIMITS.run_max_output_tokens >= charged + turn_cap

    def test_the_run_output_ceiling_clears_the_calibrations_largest_unit(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """SETTLED (2026-09-15): the authorized ceiling now carries the term.

        The residual this case held from 2026-09-14 to 2026-09-15 was one
        comparison wide. The fourth authorization's run-level OUTPUT ceiling was
        a hundred units at the largest unit the calibration of that day measured
        — 100 x 4,590 = 459,000 — which is exactly the shape
        `test_a_run_output_ceiling_sized_at_exactly_its_units_is_refused` plants
        and the corrected gate refuses, and the gate accepted
        `AUTHORIZED_LIMITS` only because the committed profile still carried the
        three stopped runs' smaller 3,116. That profile was LOAD-BEARING, and
        this case said so.

        The fifth authorization settles it on both sides at once. The profile is
        refreshed to the second calibration's own 4,176, so nothing stale holds
        the gate open; the ceiling is re-sized by the rule that now carries the
        in-flight term, to 422,000 against a floor of 100 x 4,176 + 4,096 =
        421,696. So the statement flips from "does not clear" to "clears", and
        the plant flips with it: the SUPERSEDED pairing — the old ceiling under
        the old calibration's figures — is what goes red here now, which is the
        same arithmetic this case always asserted, read from the other end.
        """

        measured = json.loads(
            (
                _REPO_ROOT
                / "audits"
                / "deduction-candidate"
                / "calibration-2026-09-14"
                / "calibration.json"
            ).read_text(encoding="utf-8")
        )["proposal"]
        largest_output = int(measured["measured_max_unit_output_tokens"])
        largest_input = int(measured["measured_max_unit_input_tokens"])
        units = instrument.planned_units()
        turn_cap = AUTHORIZED_SAMPLING.turn_max_tokens
        # On the profile as committed today: the gate passes, and it passes with
        # the in-flight term included rather than in spite of it.
        instrument.assert_limits_are_feasible()
        needed = instrument.CALIBRATED_UNIT_OUTPUT_TOKENS * units + turn_cap
        assert needed == 421_696
        assert needed <= AUTHORIZED_LIMITS.run_max_output_tokens
        # And the ceiling is no longer the bare product of a largest unit and a
        # unit count, which is the shape that made the residual.
        assert AUTHORIZED_LIMITS.run_max_output_tokens != (
            instrument.CALIBRATED_UNIT_OUTPUT_TOKENS * units
        )
        # PLANTED, as the superseded pairing: the fourth authorization's ceiling
        # under the figures that sized it. 100 x 4,590 is 459,000 to the token,
        # and those hundred units reserve 4,096 more than that.
        monkeypatch.setattr(instrument, "CALIBRATED_UNIT_OUTPUT_TOKENS", largest_output)
        monkeypatch.setattr(instrument, "CALIBRATED_UNIT_INPUT_TOKENS", largest_input)
        superseded = AUTHORIZED_LIMITS.model_copy(
            update={
                "run_max_input_tokens": 3_710_000,
                "run_max_output_tokens": largest_output * units,
            }
        )
        with pytest.raises(instrument.LimitsInfeasible) as refused:
            instrument.assert_limits_are_feasible(limits=superseded)
        message = str(refused.value)
        assert "run-level output" in message
        assert f"{largest_output * units + turn_cap:,}" in message
        # One dimension only, then as now: the 2026-09-14 input figure cleared
        # the ceiling of its own day.
        assert largest_input * units <= 3_710_000

    def test_a_per_unit_ceiling_below_a_unit_already_run_is_refused(self) -> None:
        """PLANTED: a per-unit input ceiling under the largest archived unit."""

        planted = feasible_limits().model_copy(
            update={
                "unit_max_input_tokens": instrument.CALIBRATED_UNIT_INPUT_TOKENS - 1
            }
        )
        with pytest.raises(instrument.LimitsInfeasible, match="per-unit input ceiling"):
            instrument.assert_limits_are_feasible(limits=planted)

    def test_the_calibration_is_the_largest_unit_the_archives_charged(self) -> None:
        """The two calibrated constants are read off committed evidence.

        `deduction_usage_profile.json` carries the seven archived units' charged
        totals; the module's constants are their maxima. A profile rebuilt from
        another run's archives would move both, and this is where that shows up.
        """

        largest_input, largest_output = UsageProfile.load().largest_unit()
        assert instrument.CALIBRATED_UNIT_INPUT_TOKENS == largest_input
        assert instrument.CALIBRATED_UNIT_OUTPUT_TOKENS == largest_output

    def test_the_gate_runs_before_the_frozen_set_is_read(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """PLANTED: a landmine in place of the frozen-set check.

        The readiness gate is what the CLI calls before it builds a client, and
        the feasibility check is the first thing in it — arithmetic over module
        constants, no path resolved and no file opened — so today's limits stop
        the run before a credential is read or a prefix regenerated.
        """

        def landmine(*args: object, **kwargs: object) -> object:
            raise AssertionError("the frozen set was read before the arithmetic")

        monkeypatch.setattr(instrument, "verify_frozen_set", landmine)
        # PLANTED as the authorized set, because the committed one has been
        # feasible since 2026-09-14: the four ceilings #437 merged, which the
        # arithmetic refuses.
        planted = _limits_merged_on_2026_09_07()
        monkeypatch.setattr(instrument, "AUTHORIZED_LIMITS", planted)
        root = _root_binding_the_live_band(tmp_path)
        invocation = LiveRunInvocation.naming(
            root / EXECUTION_MANIFEST_PATH,
            provider=AUTHORIZED_PROVIDER,
            model=AUTHORIZED_MODEL,
            repo_root=root,
        )
        with pytest.raises(instrument.LimitsInfeasible):
            instrument.assert_ready_for_a_live_run(
                provider=AUTHORIZED_PROVIDER,
                invocation=invocation,
                repo_root=root,
                limits=planted,
            )

    def test_the_live_run_path_fails_closed_under_infeasible_limits(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """And the other entry point: `run_instrument` refuses too.

        A caller that skipped the readiness gate and went straight to the run
        would otherwise reach a provider under limits that cannot pay for it.
        PLANTED as the authorized set, since the committed ceilings have paid
        for their own run since 2026-09-14: the ones #437 merged.
        """

        planted = _limits_merged_on_2026_09_07()
        monkeypatch.setattr(instrument, "AUTHORIZED_LIMITS", planted)
        root = _root_binding_the_live_band(tmp_path)
        invocation = LiveRunInvocation.naming(
            root / EXECUTION_MANIFEST_PATH,
            provider=AUTHORIZED_PROVIDER,
            model=AUTHORIZED_MODEL,
            repo_root=root,
        )
        with pytest.raises(instrument.LimitsInfeasible):
            run_instrument(
                output_dir=tmp_path / "out",
                client=_StubClient(),
                provider=AUTHORIZED_PROVIDER,
                live_invocation=invocation,
                repo_root=root,
                limits=planted,
            )

    def test_the_dry_run_is_not_gated_on_feasibility(self, tmp_path: Path) -> None:
        """The rehearsal must be able to run under the limits it is rehearsing.

        A fake-provider run spends nothing, and the whole point of the rehearsal
        below is to reproduce what today's limits do to a run. Gating it on the
        arithmetic would make the defect unobservable offline, which is the
        state this card found.
        """

        report = run_dry(output_dir=tmp_path, units=1)
        assert report.limits == AUTHORIZED_LIMITS


class TestUsageReplay:
    """The rehearsal sees what the provider did, keyed by arm and call type."""

    def _profile_payload(self) -> dict[str, Any]:
        loaded = json.loads(STOPPED_RUNS_PROFILE_PATH.read_text(encoding="utf-8"))
        assert isinstance(loaded, dict)
        return loaded

    def test_the_profile_is_the_archived_calls_and_nothing_else(self) -> None:
        """36 resolved calls and the two billed-and-refused ones, as counts.

        The field list is asserted rather than described: a row carries an arm,
        a call type, two token counts, its attempt and its disposition, and a
        profile that grew a prompt, a response, a seed or a room would fail here
        rather than be committed.

        The subject is the STOPPED RUNS' profile since 2026-09-15, when the
        fifth authorization refreshed the committed one to the second
        calibration's 720 clean calls. These 38 rows are the only archived
        FAULTS this evaluation has — two the provider billed and refused — and
        the eight cases whose subject is a fault read them from
        `deduction_stopped_runs_usage_profile.json` rather than from a profile
        that has none.
        """

        payload = self._profile_payload()
        rows = payload["calls"]
        assert payload["totals"]["resolved_calls"] == 36
        assert payload["totals"]["refused_calls_with_usage"] == 2
        assert len(rows) == 38
        permitted = {
            "arm",
            "call_type",
            "input_tokens",
            "output_tokens",
            "attempt",
            "disposition",
            "error_type",
        }
        assert {key for row in rows for key in row} <= permitted
        encoded = json.dumps(rows)
        for forbidden in ("prompt", "response", "seed", "room", "tick"):
            assert forbidden not in encoded, forbidden

    def test_the_replay_answers_each_call_with_its_own_arms_usage(
        self, tmp_path: Path
    ) -> None:
        """Every call's replayed row is its own arm's and its own call type's.

        The double reads the prompt family for the arm and the schema for the
        call type; this holds that classification against what the run actually
        asked for, over a whole paired unit of each arm.
        """

        double = UsageReplayProvider()
        run_dry(output_dir=tmp_path, units=1, limits=feasible_limits(), client=double)
        assert len(double.replayed) == 12
        assert {row.arm for row in double.replayed} == {
            "repaired_clock",
            "combined_accounts",
        }
        for arm in ("repaired_clock", "combined_accounts"):
            own = [row for row in double.replayed if row.arm == arm]
            assert [row.call_type for row in own] == ["turn"] * 3 + ["ballot"] * 3
            for row in own:
                cap = (
                    AUTHORIZED_SAMPLING.turn_max_tokens
                    if row.call_type == "turn"
                    else AUTHORIZED_SAMPLING.vote_max_tokens
                )
                assert row.output_tokens < cap

    def test_a_prompt_from_neither_family_is_refused(self) -> None:
        """No silent fallback: an unrecognised family would replay another arm."""

        with pytest.raises(ValueError, match="neither arm's marker"):
            usage_replay_double.arm_of("nothing recognisable here", "turn")

    def test_the_rehearsal_reproduces_the_stop_of_2026_09_13(
        self, tmp_path: Path
    ) -> None:
        """The 100-unit rehearsal under the limits OF THAT DAY, on the double.

        It stops where the live run stopped and says the same thing: the
        candidate arm's per-unit output budget refusing a ballot's 1,024-token
        reservation at 3,116 charged, against a 4,000 ceiling. The number is the
        archived unit's own — the rehearsal replays that unit's calls, refusal
        included — so this is the live stop reproduced offline at $0 rather than
        a stop of the same shape. Both halves of that day are planted: the
        ceilings #437 merged AND the 2,048 turn cap the run drew at, because a
        rehearsal at today's 4,096 would be refused on its FIRST call and would
        reproduce a different stop.

        Its profile is the stopped runs' own, committed beside the current one
        since the refresh of 2026-09-15: the unit whose calls this replays is in
        that archive and in no other, and a rehearsal of the live stop has to
        replay the calls that made it.
        """

        double = UsageReplayProvider(profile=stopped_runs_profile())
        with pytest.raises(InstrumentAborted) as stopped:
            run_dry(
                output_dir=tmp_path,
                client=double,
                limits=_limits_merged_on_2026_09_07(),
                sampling=_sampling_before_the_raise(),
            )
        partial = stopped.value.partial
        assert (
            "LLM budget exceeded on output_tokens: current=3116.0 + "
            "delta=1024.0 > cap=4000.0" in partial.reason
        )
        assert partial.completed_units == 5
        assert partial.planned_units == 100
        # The stop is the candidate arm's: it is the arm whose last unit spent
        # more than the reference arm's whole unit.
        candidate = partial.usage_by_arm["combined_accounts"]
        reference = partial.usage_by_arm["repaired_clock"]
        assert candidate.output_tokens > reference.output_tokens
        assert partial.usage_by_arm["combined_accounts"].cost_usd == 0.0

    def test_the_rehearsal_is_green_under_a_feasible_authorization(
        self, tmp_path: Path
    ) -> None:
        """The same 100 units under the re-sizing the diagnosis proposes.

        Both arms complete all fifty of their units, and the per-arm output
        totals are the measured profile's rather than the fixture's 66 tokens a
        call — which is the whole point: the headroom check below reads a number
        a real endpoint produced.

        On the stopped runs' profile, because the per-arm totals below are the
        ones the manifest's output-headroom paragraph quotes and they are that
        archive's: replaying the current profile here would re-measure the
        paragraph rather than check it, and the defaulted turns it also quotes
        come from the two refusals only that archive carries.
        """

        double = UsageReplayProvider(profile=stopped_runs_profile())
        report = run_dry(output_dir=tmp_path, client=double, limits=feasible_limits())
        assert [arm.units for arm in report.arms] == [50, 50]
        assert report.total_cost_usd == 0.0
        assert double.attempts == 600
        for arm in report.arms:
            assert arm.output_tokens / arm.units > 1_000
            assert (
                arm.output_tokens / arm.units < feasible_limits().unit_max_output_tokens
            )
        # Every figure the manifest's output-headroom paragraph quotes is this
        # report's, so the record cannot drift from the run that produced it.
        manifest = _MANIFEST.read_text(encoding="utf-8")
        for arm in report.arms:
            assert f"{arm.input_tokens:,}" in manifest, arm.arm
            assert f"{arm.output_tokens:,}" in manifest, arm.arm
            assert f"{round(arm.input_tokens / arm.units):,}" in manifest, arm.arm
            assert f"{round(arm.output_tokens / arm.units):,}" in manifest, arm.arm
        run_input = sum(arm.input_tokens for arm in report.arms)
        run_output = sum(arm.output_tokens for arm in report.arms)
        assert f"{run_input:,}" in manifest
        assert f"{run_output:,}" in manifest
        share = 100 * run_output / AUTHORIZED_LIMITS.run_max_output_tokens
        ceiling = AUTHORIZED_LIMITS.run_max_output_tokens
        assert f"{share:.1f}% of the {ceiling:,} run-level" in manifest
        assert share < 100
        # And the figure that made the re-sizing necessary, against the ceiling
        # this manifest bound until 2026-09-14: the same measured total, over
        # 100%, which is what a complete run would have stopped on.
        superseded = _limits_merged_on_2026_09_07().run_max_output_tokens
        overrun = 100 * run_output / superseded
        assert f"{overrun:.1f}% of the 200,000 run-level" in manifest
        assert overrun > 100
        candidate = next(arm for arm in report.arms if arm.arm == "combined_accounts")
        assert f"{candidate.defaulted_turns} defaulted turns" in manifest
        assert candidate.defaulted_turns > 0

    def test_the_rehearsal_is_green_under_the_fourth_authorizations_limits(
        self, tmp_path: Path
    ) -> None:
        """The same 100 units under the ceilings and caps this run is AUTHORIZED at.

        The rehearsal above runs under the re-sizing the diagnosis PROPOSES,
        which is not what the owner bound: until the fourth authorization
        `assert_limits_are_feasible` refused `AUTHORIZED_LIMITS` outright, so no
        rehearsal of the whole pipeline could be made under them at all. It can
        now, and this is it — the authorized ceilings, the authorized caps, on
        whatever band the live freeze record holds, which is the fourth since
        that freeze merged. It clears the feasibility gate, completes at $0 and
        stays inside every ceiling it was measured against.

        The per-arm totals are the ones the manifest's output-headroom paragraph
        quotes, and that is the band-independence claim the re-binding rests on:
        the double answers from an archived distribution keyed by arm and call
        type, so what it charges cannot depend on which prefix a unit ran. The
        figures that DO depend on the prefixes are the fake provider's, and they
        are re-measured on the new band by
        `TestDryRun.test_the_mechanics_check_paragraph_quotes_the_run_it_describes`.
        """

        instrument.assert_limits_are_feasible()
        double = UsageReplayProvider(profile=stopped_runs_profile())
        report = run_dry(
            output_dir=tmp_path,
            client=double,
            limits=AUTHORIZED_LIMITS,
            sampling=AUTHORIZED_SAMPLING,
        )
        assert double.attempts == 600
        assert report.total_cost_usd == 0.0
        assert report.limits == AUTHORIZED_LIMITS
        assert report.sampling == AUTHORIZED_SAMPLING
        assert [arm.units for arm in report.arms] == [50, 50]
        for arm in report.arms:
            assert arm.units == arm.terminal_units + arm.partial_units
            assert (
                arm.output_tokens / arm.units < AUTHORIZED_LIMITS.unit_max_output_tokens
            )
            assert (
                arm.input_tokens / arm.units < AUTHORIZED_LIMITS.unit_max_input_tokens
            )
        assert (
            sum(arm.output_tokens for arm in report.arms)
            < AUTHORIZED_LIMITS.run_max_output_tokens
        )
        assert (
            sum(arm.input_tokens for arm in report.arms)
            < AUTHORIZED_LIMITS.run_max_input_tokens
        )
        if _the_document_is_mid_rebinding() is not None:
            # Everything above is band-independent and has just been asserted.
            # What the manifest quotes below is not: `terminal_units` counts the
            # units that reached a meeting on the band the row binds, and
            # re-measuring that paragraph on the new band is the re-binding
            # card's acceptance item, not a freeze's. The refusal asserted by
            # the helper is what stands in for it meanwhile.
            return
        manifest = _MANIFEST.read_text(encoding="utf-8")
        for arm in report.arms:
            assert f"{arm.input_tokens:,}" in manifest, arm.arm
            assert f"{arm.output_tokens:,}" in manifest, arm.arm
            assert f"{arm.terminal_units} terminal units" in manifest, arm.arm

    def test_the_rehearsal_is_green_on_the_refreshed_profile_under_the_new_limits(
        self, tmp_path: Path
    ) -> None:
        """The fifth authorization's own pair: its ceilings, its measurement.

        The two rehearsals above replay the three stopped runs' archive, because
        what they check is a manifest paragraph those runs' numbers wrote. This
        one replays the profile the fifth authorization is SIZED on — the second
        calibration's 720 calls over 120 units — under the ceilings it re-sized
        them to, which is the pairing nothing else in this file makes.

        It clears the feasibility gate first, completes all 100 units and 600
        calls at $0.00, and stays inside every ceiling it is measured against on
        both dimensions and at both levels. The v4 prompts are why the output
        side has so much room: the candidate arm's per-unit output mean fell
        from 3,481.5 at v3 to 1,608.9, which is the same fact that LOWERED the
        run-level output ceiling.

        The band it runs on is whatever the live freeze record holds, and what
        the double charges does not depend on it — the rows are keyed by arm and
        call type — so this case survives the re-binding to band 8000-8999
        without being re-measured.
        """

        instrument.assert_limits_are_feasible()
        double = UsageReplayProvider()
        report = run_dry(
            output_dir=tmp_path,
            client=double,
            limits=AUTHORIZED_LIMITS,
            sampling=AUTHORIZED_SAMPLING,
        )
        assert double.attempts == 600
        assert report.total_cost_usd == 0.0
        assert report.limits == AUTHORIZED_LIMITS
        assert [arm.units for arm in report.arms] == [50, 50]
        for arm in report.arms:
            assert arm.output_tokens / arm.units < (
                AUTHORIZED_LIMITS.unit_max_output_tokens
            )
            assert arm.input_tokens / arm.units < (
                AUTHORIZED_LIMITS.unit_max_input_tokens
            )
        run_input = sum(arm.input_tokens for arm in report.arms)
        run_output = sum(arm.output_tokens for arm in report.arms)
        assert run_input < AUTHORIZED_LIMITS.run_max_input_tokens
        assert run_output < AUTHORIZED_LIMITS.run_max_output_tokens
        # Pinned, so the figures the limits card's Results quotes cannot drift
        # from the rehearsal that produced them.
        assert _arm_rows(report) == {
            "repaired_clock": (1_038_160, 56_765, 300),
            "combined_accounts": (1_134_054, 80_441, 300),
        }

    def test_a_call_type_blind_sampler_manufactures_a_truncation(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: the same replay with the call type thrown away.

        It hands a ballot capped at 1,024 output tokens the 1,045 a turn
        produced, and the instrument stops the run on a truncation the provider
        never produced. Keying the profile by call type is what prevents it, and
        this is the regression that would otherwise be invisible.
        """

        with pytest.raises(InstrumentAborted) as stopped:
            run_dry(
                output_dir=tmp_path,
                client=CallTypeBlindReplayProvider(profile=stopped_runs_profile()),
                limits=feasible_limits(),
            )
        assert "reached its 1024-token output cap" in stopped.value.partial.reason
        # And the keyed sampler does not, on the same units and the same limits.
        keyed = run_dry(
            output_dir=tmp_path / "keyed",
            client=UsageReplayProvider(profile=stopped_runs_profile()),
            units=4,
            limits=feasible_limits(),
        )
        assert [arm.units for arm in keyed.arms] == [4, 4]

    @pytest.mark.parametrize(
        ("mode", "trigger"),
        [
            ("billed_refusal", None),
            ("empty_body", "empty_completion"),
            ("no_usage_body", "empty_completion"),
            ("transport_error", "transport_error"),
        ],
    )
    def test_each_planted_provider_fault_reaches_a_running_unit(
        self, tmp_path: Path, mode: str, trigger: str | None
    ) -> None:
        """PLANTED one provider fault at a time, on the candidate arm's first turn.

        The four the double can plant are the four the live runs met: a payload
        the endpoint billed for and refused (attempt 1 and attempt 3), a 2xx
        body with no completion (attempt 2), one whose usage block the adapter
        would not read (the shape no attempt met and no classifier covered),
        and a dropped connection. Each is planted here through the whole
        pipeline rather than at the wrapper alone, because what a unit DOES
        with one is the thing a rehearsal has to show: the refusal is a sample
        the meeting fail-softs, and the other three are retried and recovered.
        """

        double = UsageReplayProvider(
            profile=stopped_runs_profile(),
            spoil_call=instrument.UNIT_TURN_CALLS + instrument.UNIT_BALLOT_CALLS + 1,
            mode=cast(Any, mode),
        )
        report = run_dry(
            output_dir=tmp_path, units=1, limits=feasible_limits(), client=double
        )
        assert double.spoiled == 1
        assert [arm.units for arm in report.arms] == [1, 1]
        candidate = next(arm for arm in report.arms if arm.arm == "combined_accounts")
        reference = next(arm for arm in report.arms if arm.arm == "repaired_clock")
        assert reference.retried_calls == 0
        if trigger is None:
            # A sample, not a fault: the meeting layer substitutes a
            # placeholder turn for it and the unit resolves. One default, not
            # two: a planted fault consumes no archived row, so this unit's
            # three turns draw the bucket's first two rows and never reach the
            # refusal that sits third in it.
            assert candidate.defaulted_turns == 1
            assert candidate.defaults_by_validation == 1
            assert candidate.retried_calls == 0
        else:
            assert candidate.retried_calls == 1
            assert candidate.attempts_by_trigger == {trigger: 1}

    def test_the_archived_refusal_is_replayed_where_it_happened(
        self, tmp_path: Path
    ) -> None:
        """A unit whose third turn the provider billed for and refused.

        It is a sample, not a fault: the meeting layer substitutes a placeholder
        turn, the unit resolves, and the spend is charged off the parse-failure
        metadata. The rehearsal therefore carries the candidate arm's real
        defaulted-turn rate rather than a clean run the archives do not show.
        """

        double = UsageReplayProvider(profile=stopped_runs_profile())
        report = run_dry(
            output_dir=tmp_path, units=1, limits=feasible_limits(), client=double
        )
        assert double.refused == 1
        candidate = next(arm for arm in report.arms if arm.arm == "combined_accounts")
        assert candidate.defaulted_turns == 1
        assert candidate.defaults_by_validation == 1
        reference = next(arm for arm in report.arms if arm.arm == "repaired_clock")
        assert reference.defaulted_turns == 0


class TestEmptyResponseShapes:
    """Every fail-loud shape the authorized client raises is classified.

    The classifier keys on the adapter's own wording, so the set of wordings is
    ENUMERATED from that adapter's source rather than typed here: a fifth
    refusal added to `_raw_from_response_body` turns this red instead of
    reaching a run as an unretried stop.
    """

    def _raised_messages(self) -> list[str]:
        source = (_REPO_ROOT / "llm" / "featherless_client.py").read_text("utf-8")
        function = next(
            node
            for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.FunctionDef)
            and node.name == "_raw_from_response_body"
        )
        messages: list[str] = []
        for node in ast.walk(function):
            if not isinstance(node, ast.Raise) or node.exc is None:
                continue
            call = node.exc
            assert isinstance(call, ast.Call), ast.unparse(node)
            messages.append(_literal_message(call.args[0]))
        return messages

    def test_every_shape_the_adapter_raises_is_a_retry_class(self) -> None:
        """The enumeration, and the four messages it finds."""

        messages = self._raised_messages()
        assert len(messages) == 4
        for message in messages:
            assert instrument.transport_trigger(RuntimeError(message)) == (
                "empty_completion"
            ), message
        # And the doubles below wear those wordings rather than inventing their
        # own, so the planted cases prove the classifier against the adapter
        # rather than against themselves. Both directions: every shape this
        # function raises has a double, and every body-refusal mode a double
        # plants is one of them.
        body_refusals = (
            "empty_body",
            "empty_content",
            "no_usage_body",
            "partial_usage_body",
        )
        for mode in body_refusals:
            planted = NO_COMPLETION_MESSAGES[mode]
            assert any(planted.startswith(message[:40]) for message in messages), mode
        for message in messages:
            assert any(
                NO_COMPLETION_MESSAGES[mode].startswith(message[:40])
                for mode in body_refusals
            ), f"no double plants this shape: {message}"

    def test_an_uncovered_wording_is_not_classified(self) -> None:
        """PLANTED: a fifth refusal the marker tuple does not carry.

        The enumeration above is only a gate because this is true: a wording
        outside `_EMPTY_COMPLETION_MARKERS` classifies as nothing, so an
        unretried stop is what a new refusal would become — and the test above
        is what makes that red instead.
        """

        planted = (
            "Featherless response carried no completion id (model='x'); refusing "
            "to record it."
        )
        assert instrument.transport_trigger(RuntimeError(planted)) is None

    @pytest.mark.parametrize(
        "mode", ["empty_body", "empty_content", "no_usage_body", "partial_usage_body"]
    )
    def test_each_shape_is_retried_and_the_call_recovers(self, mode: str) -> None:
        """PLANTED per shape: one attempt of that wording, then a completion.

        The two usage-block refusals were uncovered before this card: they
        re-raised bare, uncharged and unretried, so a run would have stopped on
        the first one the endpoint produced.
        """

        clock = instrument._ModelWorkClock(max_seconds=3600.0)
        double = NoCompletionProvider(mode=cast(Any, mode), failures=1)
        client = instrument._InstrumentClient(
            double, work_clock=clock, backoff_base_seconds=0.0
        )
        response = asyncio.run(
            client.complete(prompt="p", schema=None, max_tokens=1024, temperature=0.2)
        )
        assert response.text
        assert double.attempts == 2
        counted = client.attempts()
        assert counted.retried_calls == 1
        assert dict(counted.by_trigger) == {"empty_completion": 1}
        # The attempt that bought nothing is in the ledger at zero tokens.
        assert [call.model for call in client.calls][0] == (
            instrument.UNACCOUNTED_ATTEMPT_MODEL
        )

    def test_the_markers_are_still_the_adapters_own_wording(self) -> None:
        """Each fragment the classifier keys on is in that adapter's source."""

        source = (_REPO_ROOT / "llm" / "featherless_client.py").read_text("utf-8")
        for marker in instrument._EMPTY_COMPLETION_MARKERS:
            assert marker in source, marker


class _InterruptedProvider(UsageReplayProvider):
    """The replay double with an operator's Ctrl-C planted on the nth call.

    An interrupt is not a provider fault, so it is not one of the double's
    `ReplayMode` faults: it is raised above the archived draw, so every call
    before it replayed real usage and the pair it lands in has really bought
    tokens. `KeyboardInterrupt` stands here for the whole class the owner's
    clause calls "a process crash" that still unwinds this process — a Ctrl-C, a
    SIGTERM, a `SystemExit`.
    """

    def __init__(self, *, interrupt_at: int, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.interrupt_at = interrupt_at

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
        if schema is not None and self.attempts + 1 == self.interrupt_at:
            raise KeyboardInterrupt("the operator stopped the sitting")
        return await super().complete(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
            agent_id=agent_id,
        )


class TestCheckpointAndResume:
    """A stopped run continues where it stopped, or is refused for not being it."""

    def _checkpoint(self, tmp_path: Path, *, units: int = 2) -> Path:
        path = tmp_path / "checkpoint.json"
        run_dry(
            output_dir=tmp_path / "run",
            units=units,
            limits=feasible_limits(),
            client=UsageReplayProvider(),
            checkpoint_path=path,
        )
        return path

    def test_a_checkpoint_is_written_after_every_paired_seed(
        self, tmp_path: Path
    ) -> None:
        """Both arms of a prefix, or nothing: a resume never begins mid-pair."""

        checkpoint = instrument.read_checkpoint(self._checkpoint(tmp_path, units=2))
        frozen = verify_frozen_set(_REPO_ROOT)
        assert checkpoint.completed_seeds == tuple(frozen.accepted_seeds[:2])
        assert len(checkpoint.units) == 4
        assert {unit.arm for unit in checkpoint.units} == {
            "repaired_clock",
            "combined_accounts",
        }
        assert checkpoint.held_out_manifest_sha256 == frozen.manifest_sha256
        assert checkpoint.arm_surface_sha256 == dict(instrument.arm_surface_digests())

    def test_the_checkpoint_carries_no_prompt_or_prefix_bytes(
        self, tmp_path: Path
    ) -> None:
        """The report's rule, applied to the other artifact a run writes."""

        path = self._checkpoint(tmp_path, units=2)
        payload = json.loads(path.read_text(encoding="utf-8"))
        frozen = verify_frozen_set(_REPO_ROOT)
        strings = instrument._every_string_in(payload)
        for prefix in frozen.prefixes[:2]:
            assert not any(canonical_prefix_json(prefix) in text for text in strings)
            for step in prefix.steps:
                fragment = json.dumps(
                    step.model_dump(mode="json"),
                    sort_keys=True,
                    separators=(",", ":"),
                )
                assert not any(fragment in text for text in strings)
        assert_no_legacy_body_handles(strings)

    def test_a_resumed_run_reports_what_an_uninterrupted_one_does(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: a provider that stops answering at the third paired seed.

        The run stops there with two seeds completed and a checkpoint on disk;
        a second sitting continues at the third and produces the same report —
        the same graded units, the same verdicts, the same per-arm token totals
        — apart from the two wall clocks, which measure real time and cannot be
        the same twice, and apart from the calls the stop ITSELF made, which a
        resumed run charges rather than forgets. Here the stop lands on a unit's
        first call, so what it abandoned is four attempts that bought no tokens;
        `test_a_stop_inside_a_unit_carries_its_spend` plants the case where the
        abandoned calls carry real usage.
        """

        limits = feasible_limits()
        whole = run_dry(
            output_dir=tmp_path / "whole",
            units=4,
            limits=limits,
            client=UsageReplayProvider(),
        )
        checkpoint_path = tmp_path / "checkpoint.json"
        stopper = UsageReplayProvider(
            spoil_call=25,
            spoil_repeats=instrument.MAX_TRANSPORT_ATTEMPTS,
            mode="transport_error",
        )
        with pytest.raises(InstrumentAborted) as stopped:
            run_dry(
                output_dir=tmp_path / "stopped",
                units=4,
                limits=limits,
                client=stopper,
                checkpoint_path=checkpoint_path,
            )
        assert stopped.value.partial.completed_units == 4
        checkpoint = instrument.read_checkpoint(checkpoint_path)
        assert len(checkpoint.completed_seeds) == 2

        # The double picks the rotation up where the completed units left it:
        # three draws per bucket per unit, two units of each arm finished.
        resumed = run_dry(
            output_dir=tmp_path / "resumed",
            units=4,
            limits=limits,
            client=UsageReplayProvider(seed=6),
            resume=checkpoint,
        )
        assert _less_the_stops_own_calls(resumed, checkpoint) == _without_wall(whole)

    def test_a_stop_inside_a_unit_carries_its_spend(self, tmp_path: Path) -> None:
        """PLANTED: the stop lands mid-unit, where the resume's own cause lands.

        The checkpoint is written at PAIR boundaries, so a stop part-way through
        a pair charges calls that no unit row carries. Before this was fixed the
        second sitting rebuilt its run budget from the last boundary and forgave
        them — once per stop, unboundedly often, because nothing bounds how many
        times a transport may drop.

        Three statements, each a different way the spend has to survive: the
        checkpoint's abandoned rows ARE the difference between what the stopped
        sitting really spent and what its graded units account for; the resumed
        report's totals are the uninterrupted run's plus exactly those rows; and
        the model-work clock carries them too.
        """

        limits = feasible_limits()
        checkpoint_path = tmp_path / "checkpoint.json"
        stopper = UsageReplayProvider(
            profile=stopped_runs_profile(),
            spoil_call=28,
            spoil_repeats=instrument.MAX_TRANSPORT_ATTEMPTS,
            mode="transport_error",
        )
        with pytest.raises(InstrumentAborted) as stopped:
            run_dry(
                output_dir=tmp_path / "stopped",
                units=4,
                limits=limits,
                client=stopper,
                checkpoint_path=checkpoint_path,
            )
        partial = stopped.value.partial
        checkpoint = instrument.read_checkpoint(checkpoint_path)

        # The interrupted unit really did buy tokens before the transport went.
        abandoned = checkpoint.abandoned.usage_by_arm()
        assert abandoned, "a mid-unit stop abandoned no spend at all"
        assert any(row.output_tokens > 0 for row in abandoned.values())
        # And the file accounts for every token the stopped run reported.
        assert {arm: usage for arm, usage in partial.usage_by_arm.items()} == dict(
            checkpoint.charged_usage_by_arm()
        )
        # The rotation is deterministic, so the figures the card's round-1
        # record quotes are pinned here rather than described: the record
        # cannot drift from the rehearsal that produced it.
        assert _token_rows(partial.usage_by_arm) == {
            "repaired_clock": (51_815, 3_579, 19),
            "combined_accounts": (39_773, 5_365, 12),
        }
        assert _token_rows(checkpoint.usage_by_arm()) == {
            "repaired_clock": (40_970, 2_294, 12),
            "combined_accounts": (39_773, 5_365, 12),
        }
        assert _token_rows(abandoned) == {"repaired_clock": (10_845, 1_285, 7)}
        assert checkpoint.charged_model_work_seconds() == pytest.approx(
            partial.model_work_seconds
        )
        assert checkpoint.model_work_seconds < partial.model_work_seconds

        whole = run_dry(
            output_dir=tmp_path / "whole",
            units=4,
            limits=limits,
            client=UsageReplayProvider(profile=stopped_runs_profile()),
        )
        resumed = run_dry(
            output_dir=tmp_path / "resumed",
            units=4,
            limits=limits,
            client=UsageReplayProvider(profile=stopped_runs_profile(), seed=6),
            resume=checkpoint,
        )
        assert _less_the_stops_own_calls(resumed, checkpoint) == _without_wall(whole)
        spent = {arm.arm: arm.output_tokens for arm in resumed.arms}
        uninterrupted = {arm.arm: arm.output_tokens for arm in whole.arms}
        assert spent != uninterrupted
        for arm, tokens in abandoned.items():
            assert spent[arm] == uninterrupted[arm] + tokens.output_tokens
        assert _arm_rows(whole) == {
            "repaired_clock": (85_186, 5_310, 24),
            "combined_accounts": (78_435, 11_154, 24),
        }
        assert _arm_rows(resumed) == {
            "repaired_clock": (96_031, 6_595, 31),
            "combined_accounts": (78_435, 11_154, 24),
        }

    def test_an_interrupt_leaves_the_pairs_spend_in_the_checkpoint_and_reraises(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: a Ctrl-C mid-pair, the stop class the clause's "crash" covers.

        The owner's `RESUMPTION_CLAUSE` names a process crash as resumable "with
        the interrupted unit's spend and model-work time carried". A stop that
        unwinds this process has to reach the final checkpoint for that to be
        arithmetic rather than a promise, so the run loop catches
        `BaseException` for the accounting — and only for it: the interrupt is
        re-raised as itself, it is not reported as a `PartialRun`, and it is not
        given a stop `reason`. Narrow the handler back to `Exception` and this
        goes red on the abandoned rows, with the pair's spend forgiven exactly
        as a transport stop's used to be.

        What this test cannot cover is the rest of the class: a SIGKILL, an OOM
        kill or a power loss runs no handler at all, so it writes nothing and
        carries nothing. That gap is stated in the manifest's dated clause
        section and held by
        `test_the_resumption_section_names_the_stop_it_cannot_carry`.
        """

        limits = feasible_limits()
        checkpoint_path = tmp_path / "checkpoint.json"
        with pytest.raises(KeyboardInterrupt):
            run_dry(
                output_dir=tmp_path / "stopped",
                units=4,
                limits=limits,
                client=_InterruptedProvider(interrupt_at=28),
                checkpoint_path=checkpoint_path,
            )
        checkpoint = instrument.read_checkpoint(checkpoint_path)
        abandoned = checkpoint.abandoned.usage_by_arm()
        assert abandoned, "an interrupt inside a pair carried no spend at all"
        assert any(row.output_tokens > 0 for row in abandoned.values())
        # The two completed pairs are graded and the third is not: an interrupt
        # is a stop between pairs for the resume, and a charge for the budget.
        assert len(checkpoint.completed_seeds) == 2
        assert len(checkpoint.units) == 4
        resumed = run_dry(
            output_dir=tmp_path / "resumed",
            units=4,
            limits=limits,
            client=UsageReplayProvider(seed=6),
            resume=checkpoint,
        )
        for arm, tokens in abandoned.items():
            spent = {row.arm: row.output_tokens for row in resumed.arms}[arm]
            whole = run_dry(
                output_dir=tmp_path / f"whole-{arm}",
                units=4,
                limits=limits,
                client=UsageReplayProvider(),
            )
            assert spent == (
                {row.arm: row.output_tokens for row in whole.arms}[arm]
                + tokens.output_tokens
            )

    def test_the_abandoned_spend_is_charged_against_the_run_ceiling(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: a ceiling only the abandoned calls cross.

        The stronger half of the statement above. The run ceiling here sits one
        token above what the checkpoint's GRADED units spent and below what the
        stopped sitting actually spent, so a resume that carried only the graded
        half would start happily and one that carries the whole spend refuses
        before a unit runs. The refusal is the correct answer: a run that has
        already spent its authorization is finished, not resumable.
        """

        limits = feasible_limits()
        checkpoint_path = tmp_path / "checkpoint.json"
        with pytest.raises(InstrumentAborted):
            run_dry(
                output_dir=tmp_path / "stopped",
                units=4,
                limits=limits,
                client=UsageReplayProvider(
                    spoil_call=28,
                    spoil_repeats=instrument.MAX_TRANSPORT_ATTEMPTS,
                    mode="transport_error",
                ),
                checkpoint_path=checkpoint_path,
            )
        checkpoint = instrument.read_checkpoint(checkpoint_path)
        graded = sum(
            usage.output_tokens for usage in checkpoint.usage_by_arm().values()
        )
        charged = sum(
            usage.output_tokens for usage in checkpoint.charged_usage_by_arm().values()
        )
        assert charged > graded
        tight = limits.model_copy(update={"run_max_output_tokens": graded + 1})
        with pytest.raises(BudgetExceededError):
            run_dry(
                output_dir=tmp_path / "resumed",
                units=4,
                limits=tight,
                client=UsageReplayProvider(seed=6),
                resume=checkpoint.model_copy(update={"limits": tight}),
            )

    def test_a_second_stop_carries_the_first_ones_abandoned_calls(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: two stops in a row, the second inside a later pair.

        The accounting accumulates or it leaks once per sitting. The checkpoint
        the second stop writes carries the first stop's abandoned calls beside
        its own, so a third sitting charges both.
        """

        limits = feasible_limits()
        checkpoint_path = tmp_path / "checkpoint.json"
        with pytest.raises(InstrumentAborted):
            run_dry(
                output_dir=tmp_path / "first",
                units=6,
                limits=limits,
                client=UsageReplayProvider(
                    spoil_call=28,
                    spoil_repeats=instrument.MAX_TRANSPORT_ATTEMPTS,
                    mode="transport_error",
                ),
                checkpoint_path=checkpoint_path,
            )
        first = instrument.read_checkpoint(checkpoint_path)
        first_abandoned = sum(
            usage.input_tokens for usage in first.abandoned.usage_by_arm().values()
        )
        assert first_abandoned > 0
        with pytest.raises(InstrumentAborted):
            run_dry(
                output_dir=tmp_path / "second",
                units=6,
                limits=limits,
                client=UsageReplayProvider(
                    seed=6,
                    spoil_call=16,
                    spoil_repeats=instrument.MAX_TRANSPORT_ATTEMPTS,
                    mode="transport_error",
                ),
                checkpoint_path=checkpoint_path,
                resume=first,
            )
        second = instrument.read_checkpoint(checkpoint_path)
        second_abandoned = sum(
            usage.input_tokens for usage in second.abandoned.usage_by_arm().values()
        )
        assert second_abandoned > first_abandoned
        assert len(second.completed_seeds) > len(first.completed_seeds)

    def test_a_resume_narrower_than_its_checkpoint_is_refused(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: `--units 1` against a checkpoint that finished two.

        `next_seeds_after` computed the finished prefix over the TRUNCATED list,
        so a completed seed outside it was ignored rather than refused: the tail
        came back empty, every carried unit was still reported, and a one-unit
        request produced a two-unit report with no run behind the difference.
        """

        checkpoint = instrument.read_checkpoint(self._checkpoint(tmp_path, units=2))
        frozen = verify_frozen_set(_REPO_ROOT)
        with pytest.raises(
            instrument.ResumeNotAuthorized, match="would not draw"
        ) as refused:
            instrument.next_seeds_after(checkpoint, frozen.prefixes[:1])
        assert str(frozen.accepted_seeds[1]) in str(refused.value)
        with pytest.raises(instrument.ResumeNotAuthorized, match="would not draw"):
            run_dry(
                output_dir=tmp_path / "narrow",
                units=1,
                limits=feasible_limits(),
                client=UsageReplayProvider(seed=6),
                resume=checkpoint,
            )

    def test_a_resume_into_the_stopped_sittings_directory_is_refused(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: a mid-unit stop, then a resume pointed at its own directory.

        The stop leaves the interrupted unit's partial replay behind, so the
        second sitting used to reach the recorder's AlreadyExists refusal — after
        the resume gates had passed, and on a metered provider after the tail had
        begun to spend. It is refused before anything runs now, by name, and a
        fresh directory still works.
        """

        limits = feasible_limits()
        checkpoint_path = tmp_path / "checkpoint.json"
        with pytest.raises(InstrumentAborted):
            run_dry(
                output_dir=tmp_path / "sitting-1",
                units=4,
                limits=limits,
                client=UsageReplayProvider(
                    spoil_call=28,
                    spoil_repeats=instrument.MAX_TRANSPORT_ATTEMPTS,
                    mode="transport_error",
                ),
                checkpoint_path=checkpoint_path,
            )
        checkpoint = instrument.read_checkpoint(checkpoint_path)
        with pytest.raises(
            instrument.ResumeNotAuthorized, match="already holds a recording"
        ) as refused:
            run_dry(
                output_dir=tmp_path / "sitting-1",
                units=4,
                limits=limits,
                client=UsageReplayProvider(seed=6),
                resume=checkpoint,
            )
        assert ".jsonl" in str(refused.value)
        assert "fresh directory" in str(refused.value)
        run_dry(
            output_dir=tmp_path / "sitting-2",
            units=4,
            limits=limits,
            client=UsageReplayProvider(seed=6),
            resume=checkpoint,
        )

    def test_a_resume_continues_at_the_next_unrendered_seed(
        self, tmp_path: Path
    ) -> None:
        """The tail of the ascending list, and a hole in it refused."""

        checkpoint = instrument.read_checkpoint(self._checkpoint(tmp_path, units=2))
        frozen = verify_frozen_set(_REPO_ROOT)
        remaining = instrument.next_seeds_after(checkpoint, frozen.prefixes[:4])
        assert [prefix.seed for prefix in remaining] == list(frozen.accepted_seeds[2:4])
        holed = checkpoint.model_copy(
            update={"completed_seeds": (frozen.accepted_seeds[1],)}
        )
        with pytest.raises(instrument.ResumeNotAuthorized, match="not a prefix"):
            instrument.next_seeds_after(holed, frozen.prefixes[:4])

    @pytest.mark.parametrize(
        ("field", "value", "message"),
        [
            ("manifest_sha256", "0" * 64, "execution manifest"),
            ("held_out_manifest_sha256", "0" * 64, "inputs moved"),
            ("provider", "featherless", "asks for"),
        ],
    )
    def test_a_checkpoint_that_is_not_this_run_is_refused(
        self, tmp_path: Path, field: str, value: str, message: str
    ) -> None:
        """PLANTED one identity at a time: a resume is the SAME run or none."""

        checkpoint = instrument.read_checkpoint(self._checkpoint(tmp_path, units=2))
        planted = checkpoint.model_copy(update={field: value})
        with pytest.raises(instrument.ResumeNotAuthorized, match=message):
            instrument.assert_checkpoint_matches(
                planted,
                provider="fake",
                limits=feasible_limits(),
                sampling=AUTHORIZED_SAMPLING,
                frozen=verify_frozen_set(_REPO_ROOT),
            )

    def test_the_named_arm_surface_carries_the_code_that_renders(self) -> None:
        """The set covers the renderer and the game the meeting runs inside.

        `arm_surface_digests` is what a resume compares two sittings on, so a
        file that decides what a model SEES and is not in it is a change a resume
        would accept. The loader builds the Jinja environment and picks the
        renderers; `orchestrator/game.py` drives the prefix and its meeting, and
        the held-out freeze covers it only for changes that move a generated
        prefix (`verify_frozen_set` deliberately does not re-compare
        `source_sha256`). Both are in the named set, and the constant's own
        comment says where the rest of the run path is covered instead.
        """

        surface = instrument.arm_surface_digests()
        assert "agents/strategic/prompts/loader.py" in surface
        assert "orchestrator/game.py" in surface
        source = _INSTRUMENT_SOURCE.read_text(encoding="utf-8")
        assert "A NAMED set, not a transitive import closure" in source
        # And the claim it replaced is gone: the docstring no longer says the
        # mapping covers every byte an arm renders through.
        assert "every byte an arm renders through" not in source

    @pytest.mark.parametrize(
        "moved_path",
        [
            f"{instrument.ARM_SURFACE_PROMPT_DIR}/vote_ballot.j2",
            "agents/strategic/prompts/loader.py",
            "orchestrator/game.py",
        ],
    )
    def test_a_moved_arm_surface_byte_refuses_the_resume(
        self, tmp_path: Path, moved_path: str
    ) -> None:
        """PLANTED: one arm-surface file, one byte different.

        The digest is recomputed from the tree at resume time, so this is the
        real check: a second sitting whose prompts render differently would pair
        units drawn from two instruments, and the arms are what the design
        compares. Planted on a template, on the loader that selects the
        renderers and on the game module the meeting runs inside — the last two
        were outside the set until this card's review.
        """

        checkpoint = instrument.read_checkpoint(self._checkpoint(tmp_path, units=2))
        moved = dict(checkpoint.arm_surface_sha256)
        template = moved_path
        assert template in moved
        moved[template] = "0" * 64
        planted = checkpoint.model_copy(update={"arm_surface_sha256": moved})
        with pytest.raises(
            instrument.ResumeNotAuthorized, match="arm surface moved"
        ) as refused:
            instrument.assert_checkpoint_matches(
                planted,
                provider="fake",
                limits=feasible_limits(),
                sampling=AUTHORIZED_SAMPLING,
                frozen=verify_frozen_set(_REPO_ROOT),
            )
        assert template in str(refused.value)

    def test_a_resume_under_other_limits_is_refused(self, tmp_path: Path) -> None:
        """The budgets are carried, so the ceilings are the first sitting's."""

        checkpoint = instrument.read_checkpoint(self._checkpoint(tmp_path, units=2))
        with pytest.raises(instrument.ResumeNotAuthorized, match="different limits"):
            instrument.assert_checkpoint_matches(
                checkpoint,
                provider="fake",
                limits=AUTHORIZED_LIMITS,
                sampling=AUTHORIZED_SAMPLING,
                frozen=verify_frozen_set(_REPO_ROOT),
            )

    def test_the_carried_budget_is_charged_before_the_second_sitting_spends(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: a run ceiling the first sitting already exhausted.

        A resume that forgot the first sitting's spend would run the whole tail
        under a fresh budget, which is the one thing a carried budget must not
        do. Here the carried total is already past the ceiling, so the charge
        raises before a unit runs.
        """

        checkpoint = instrument.read_checkpoint(self._checkpoint(tmp_path, units=2))
        spent = sum(usage.output_tokens for usage in checkpoint.usage_by_arm().values())
        assert spent > 0
        tight = feasible_limits().model_copy(
            update={"run_max_output_tokens": spent - 1}
        )
        squeezed = checkpoint.model_copy(update={"limits": tight})
        with pytest.raises(BudgetExceededError):
            run_dry(
                output_dir=tmp_path / "resumed",
                units=4,
                limits=tight,
                client=UsageReplayProvider(seed=6),
                resume=squeezed,
            )

    def test_a_live_resume_is_authorized_by_the_document_and_by_nothing_else(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: the same tree with the owner's sentence taken out.

        The committed manifest has carried the clause since 2026-09-14, so the
        live gate now passes on this tree. A root whose manifest is these bytes
        minus that sentence is refused by the same call, which is what makes
        this a gate on the document rather than on the code.
        """

        instrument.assert_resume_is_authorized(provider=AUTHORIZED_PROVIDER)
        unauthorized = tmp_path / EXECUTION_MANIFEST_PATH
        unauthorized.parent.mkdir(parents=True)
        unauthorized.write_text(
            _MANIFEST.read_text("utf-8").replace(
                instrument.RESUMPTION_CLAUSE, "[clause removed]"
            ),
            encoding="utf-8",
        )
        with pytest.raises(instrument.ResumeNotAuthorized, match="resumption clause"):
            instrument.assert_resume_is_authorized(
                provider=AUTHORIZED_PROVIDER, repo_root=tmp_path
            )
        # And the fake path is untouched: a rehearsal that could not resume
        # could not prove the resume.
        instrument.assert_resume_is_authorized(provider="fake")

    def test_the_readiness_gate_refuses_an_unauthorized_live_resume(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: the refusal reaches the CLI's pre-client gate, not just the helper.

        The committed document authorizes a resume since 2026-09-14, so the
        plant is a root whose manifest is these bytes minus the owner's
        sentence: the gate the CLI calls before it builds a client has to be
        the one that refuses, or an unauthorized second sitting would be
        discovered after a credential was read.
        """

        root = _root_without_the_clause_binding_the_live_band(
            tmp_path, instrument.RESUMPTION_CLAUSE
        )
        invocation = LiveRunInvocation.naming(
            root / EXECUTION_MANIFEST_PATH,
            provider=AUTHORIZED_PROVIDER,
            model=AUTHORIZED_MODEL,
            repo_root=root,
        )
        with pytest.raises(instrument.ResumeNotAuthorized):
            instrument.assert_ready_for_a_live_run(
                provider=AUTHORIZED_PROVIDER,
                invocation=invocation,
                repo_root=root,
                resuming=True,
            )

    def test_a_tree_without_the_arm_surface_cannot_say_what_it_renders(
        self, tmp_path: Path
    ) -> None:
        """No silent fallback: an absent prompt set is a refusal, not an empty
        digest map that would make every resume compare equal."""

        with pytest.raises(instrument.InstrumentError, match="prompt set"):
            instrument.arm_surface_digests(tmp_path)

    def test_a_file_that_is_not_a_checkpoint_is_refused(self, tmp_path: Path) -> None:
        """Four plants: not JSON, JSON of another schema, and JSON that is not an
        object at all.

        The last two are what AGENTS.md's "invalid input raises" means here: a
        file holding `[]` or a bare string used to reach `loaded.get` while the
        refusal was being worded and raise `AttributeError` instead — an
        incidental failure where a named one is owed.
        """

        broken = tmp_path / "broken.json"
        broken.write_text("{not json", encoding="utf-8")
        with pytest.raises(instrument.ResumeNotAuthorized, match="not a checkpoint"):
            instrument.read_checkpoint(broken)
        foreign = tmp_path / "foreign.json"
        foreign.write_text('{"schema_version": "something/9"}', encoding="utf-8")
        with pytest.raises(instrument.ResumeNotAuthorized, match="carries schema"):
            instrument.read_checkpoint(foreign)
        for body in ("[]", '"hello"', "7"):
            shapeless = tmp_path / "shapeless.json"
            shapeless.write_text(body, encoding="utf-8")
            with pytest.raises(instrument.ResumeNotAuthorized, match="carries schema"):
                instrument.read_checkpoint(shapeless)
        with pytest.raises(instrument.ResumeNotAuthorized, match="no checkpoint at"):
            instrument.read_checkpoint(tmp_path / "absent.json")

    def test_the_cli_takes_the_checkpoint_and_the_resume(self, tmp_path: Path) -> None:
        """The operator's own path, driven end to end: write one, then continue.

        The second invocation passes `--resume` and NO `--checkpoint`, which is
        what an operator continuing a stopped run types. That used to write no
        checkpoint at all, so a second interruption lost the resumed sitting's
        progress and a third sitting would re-spend held-out calls already
        bought; `--resume` now implies a checkpoint at the same path, and the
        assertion is that the file advanced.
        """

        checkpoint = tmp_path / "cp.json"
        assert (
            instrument.main(
                [
                    "--dry-run",
                    "--units",
                    "2",
                    "--output-dir",
                    str(tmp_path / "first"),
                    "--checkpoint",
                    str(checkpoint),
                    "--json",
                    str(tmp_path / "first.json"),
                ]
            )
            == 0
        )
        first = instrument.read_checkpoint(checkpoint)
        assert len(first.completed_seeds) == 2
        assert (
            instrument.main(
                [
                    "--dry-run",
                    "--units",
                    "3",
                    "--output-dir",
                    str(tmp_path / "second"),
                    "--resume",
                    str(checkpoint),
                    "--json",
                    str(tmp_path / "second.json"),
                ]
            )
            == 0
        )
        advanced = instrument.read_checkpoint(checkpoint)
        assert len(advanced.completed_seeds) == 3
        assert advanced.completed_seeds[:2] == first.completed_seeds
        report = InstrumentReport.model_validate_json(
            (tmp_path / "second.json").read_text(encoding="utf-8")
        )
        assert [arm.units for arm in report.arms] == [3, 3]


def _converted_record() -> Path:
    """The committed record of the first converted band, which is the input."""

    return _REPO_ROOT / instrument.DEFAULT_CALIBRATION_RECORD


def _converted_payload() -> dict[str, Any]:
    loaded = json.loads(_converted_record().read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _root_with_calibration_record(
    tmp_path: Path, payload: Mapping[str, Any]
) -> tuple[Path, Path]:
    """A repository root carrying ``payload`` where the converted record lives.

    Returns the root and the record's path inside it. The path is what makes a
    record a record: `verify_calibration_set` matches on WHERE the file is, so a
    planted variant has to sit where the real one does.
    """

    record = tmp_path / instrument.DEFAULT_CALIBRATION_RECORD
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(json.dumps(payload), encoding="utf-8")
    return tmp_path, record


class TestCalibrationInputs:
    """Which prefixes a calibration may render, and the four ways it refuses.

    The one mistake that would cost something irreversible is pointing this mode
    at the held-out record: rendering one of those prefixes converts the band
    the evaluation has still to spend. That refusal is first, by name, and
    planted below.
    """

    def test_the_held_out_record_is_refused_by_name(self) -> None:
        """PLANTED: the calibration pointed at the live freeze."""

        with pytest.raises(instrument.CalibrationInputsRejected) as refused:
            instrument.verify_calibration_set(_REPO_ROOT / MANIFEST_PATH)
        assert MANIFEST_PATH in str(refused.value)
        assert "HELD-OUT" in str(refused.value)

    def test_a_record_no_freeze_converted_is_refused(self, tmp_path: Path) -> None:
        """PLANTED: the same bytes, one directory away.

        A record is the freeze it was written as. Matching on the path rather
        than on the band the document claims is what keeps a copy of a converted
        record — or a hand-written one naming a converted band — from standing
        in for the freeze itself.
        """

        elsewhere = tmp_path / "manifest-band-3000-3999.json"
        elsewhere.write_text(_converted_record().read_text("utf-8"), encoding="utf-8")
        with pytest.raises(
            instrument.CalibrationInputsRejected, match="not a converted band"
        ):
            instrument.verify_calibration_set(elsewhere, repo_root=tmp_path)

    def test_a_record_that_still_says_held_out_is_refused(self, tmp_path: Path) -> None:
        """PLANTED: the converted record with its status flipped back.

        The path says which band; the status says whether that band has already
        been spent. Both are checked, because a freeze that has not been
        converted is a held-out set wherever its file happens to sit.
        """

        payload = _converted_payload()
        payload["status"] = "held_out"
        root, record = _root_with_calibration_record(tmp_path, payload)
        with pytest.raises(
            instrument.CalibrationInputsRejected, match="not 'development'"
        ):
            instrument.verify_calibration_set(record, repo_root=root)

    def test_a_moved_digest_is_refused_by_seed(self, tmp_path: Path) -> None:
        """PLANTED: one accepted digest edited in the record.

        The calibration rebuilds each prefix with the unchanged generator and
        holds it to the digest the record froze, so a generator that no longer
        produces these inputs stops the calibration instead of measuring
        something nobody froze.
        """

        payload = _converted_payload()
        payload["accepted"] = [dict(row) for row in payload["accepted"]]
        payload["accepted"][2]["sha256"] = "0" * 64
        root, record = _root_with_calibration_record(tmp_path, payload)
        with pytest.raises(instrument.CalibrationInputsRejected) as refused:
            instrument.verify_calibration_set(record, repo_root=root)
        assert "seed 3002" in str(refused.value)

    def test_the_seeds_are_the_records_first_five_ascending(self) -> None:
        """And they are the GENERATOR's prefixes, rebuilt call for call.

        The prefixes are compared against `build_prefix`'s own output rather
        than against a description of it, so "the unchanged generator" is a
        property of the objects the run renders.
        """

        inputs = instrument.verify_calibration_set(_converted_record())
        rows = _converted_payload()["accepted"]
        assert list(inputs.seeds) == [row["seed"] for row in rows[:5]]
        assert list(inputs.digests) == [row["sha256"] for row in rows[:5]]
        assert inputs.accepted_in_record == len(rows)
        game_map = load_canonical_map()
        for prefix in inputs.prefixes:
            assert prefix == build_prefix(
                seed=prefix.seed, roster=inputs.roster, game_map=game_map
            )

    def test_a_record_missing_its_rows_is_refused_as_a_calibration_input(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: the accepted block deleted.

        The freeze record's own readers raise `FrozenSetMismatch`; on this path
        that is re-raised as this path's refusal, so a runner is told the
        CALIBRATION's inputs were rejected rather than that a frozen set was.
        """

        payload = _converted_payload()
        del payload["accepted"]
        root, record = _root_with_calibration_record(tmp_path, payload)
        with pytest.raises(
            instrument.CalibrationInputsRejected, match="not a readable freeze record"
        ):
            instrument.verify_calibration_set(record, repo_root=root)


class TestCalibrationGate:
    """What authorizes a live calibration, and what it refuses."""

    def _invocation(self, root: Path) -> LiveRunInvocation:
        return LiveRunInvocation.naming(
            root / EXECUTION_MANIFEST_PATH,
            provider=AUTHORIZED_PROVIDER,
            model=AUTHORIZED_MODEL,
            repo_root=root,
        )

    def test_the_committed_manifest_authorizes_the_calibration(self) -> None:
        """The settled state: the clause is in the document the gate reads."""

        instrument.assert_calibration_is_authorized(
            provider=AUTHORIZED_PROVIDER,
            invocation=self._invocation(_REPO_ROOT),
        )

    def test_a_manifest_without_the_clause_refuses_it(self, tmp_path: Path) -> None:
        """PLANTED: the same document with the owner's sentence removed.

        The gate reads the committed manifest, so what authorizes the spend is
        the record rather than a flag on a command line.
        """

        root = _root_without_the_clause_binding_the_live_band(
            tmp_path, instrument.CALIBRATION_CLAUSE
        )
        with pytest.raises(LiveRunNotAuthorized, match="no calibration clause"):
            instrument.assert_calibration_is_authorized(
                provider=AUTHORIZED_PROVIDER,
                invocation=self._invocation(root),
                repo_root=root,
            )

    def test_the_two_authorizations_refuse_each_others_limits(
        self, tmp_path: Path
    ) -> None:
        """PLANTED both ways: each gate refuses the other's ceilings.

        The calibration's limits are not a relaxation of the run's — they are a
        different authorization for a different spend, and neither one may be
        run under the other's numbers.

        The live half needs a root whose Inputs row binds the live band, and it
        takes ``tmp_path`` for it: handed the repository, the helper would
        rewrite the committed document during a freeze window rather than plant
        a copy.
        """

        with pytest.raises(LiveRunNotAuthorized, match="calibration limits"):
            instrument.assert_calibration_is_authorized(
                provider=AUTHORIZED_PROVIDER,
                invocation=self._invocation(_REPO_ROOT),
                limits=AUTHORIZED_LIMITS,
            )
        root = _root_binding_the_live_band(tmp_path)
        with pytest.raises(LiveRunNotAuthorized, match="authorized limits exactly"):
            assert_live_run_is_authorized(
                provider=AUTHORIZED_PROVIDER,
                invocation=self._invocation(root),
                limits=instrument.CALIBRATION_LIMITS,
                repo_root=root,
            )

    def test_the_feasibility_gate_accepts_the_calibration_at_its_own_caps(
        self,
    ) -> None:
        """The arithmetic, on the calibration's ceilings and its own draw.

        Its ten units can pay for themselves at `CALIBRATION_SAMPLING` — the
        caps the owner's ceilings of 2026-09-14 were sized against and the ones
        the committed output was measured at. At the RUN's raised turn cap the
        same ceilings cannot: 12,000 against a 15,360 schedule is the same
        defect the third live run stopped on, one authorization down, which is
        why `assert_calibration_is_authorized` holds a live calibration to the
        calibration draw rather than to the run's.
        """

        instrument.assert_limits_are_feasible(
            limits=instrument.CALIBRATION_LIMITS,
            sampling=instrument.CALIBRATION_SAMPLING,
            units=instrument.calibration_units(),
        )
        with pytest.raises(instrument.LimitsInfeasible, match="per-unit output"):
            instrument.assert_limits_are_feasible(
                limits=instrument.CALIBRATION_LIMITS,
                sampling=AUTHORIZED_SAMPLING,
                units=instrument.calibration_units(),
            )

    def test_a_calibration_limit_below_the_reservation_is_refused(self) -> None:
        """PERTURBED: one token under the schedule a unit reserves."""

        reserved = instrument.unit_output_reservation(
            sampling=instrument.CALIBRATION_SAMPLING
        )
        planted = instrument.CALIBRATION_LIMITS.model_copy(
            update={"unit_max_output_tokens": reserved - 1}
        )
        with pytest.raises(instrument.LimitsInfeasible, match="per-unit output"):
            instrument.assert_limits_are_feasible(
                limits=planted,
                sampling=instrument.CALIBRATION_SAMPLING,
                units=instrument.calibration_units(),
            )

    def test_a_fake_calibration_takes_no_invocation(self, tmp_path: Path) -> None:
        """The rehearsal is the mechanics check and never the authorized run."""

        instrument.assert_calibration_is_authorized(provider="fake", invocation=None)
        with pytest.raises(LiveRunNotAuthorized, match="takes no live invocation"):
            instrument.assert_calibration_is_authorized(
                provider="fake", invocation=self._invocation(_REPO_ROOT)
            )
        del tmp_path

    def test_a_live_calibration_without_an_invocation_is_refused(self) -> None:
        with pytest.raises(LiveRunNotAuthorized, match="carries no LiveRunInvocation"):
            instrument.assert_calibration_is_authorized(
                provider=AUTHORIZED_PROVIDER, invocation=None
            )

    def test_more_seeds_than_the_owner_authorized_are_refused(self) -> None:
        """PLANTED: six paired seeds where five were approved."""

        with pytest.raises(LiveRunNotAuthorized, match="paired seeds"):
            instrument.assert_calibration_is_authorized(
                provider=AUTHORIZED_PROVIDER,
                invocation=self._invocation(_REPO_ROOT),
                paired_seeds=instrument.CALIBRATION_PAIRED_SEEDS + 1,
            )

    def test_a_live_calibration_without_the_runner_flag_is_refused_by_the_cli(
        self,
    ) -> None:
        """PLANTED: the command without the runner's own statement.

        `parser.error` exits rather than running, so this reaches no provider,
        builds no client and reads no record — which is the property: the flag
        is checked before any of that happens.
        """

        with pytest.raises(SystemExit) as exited:
            instrument.main(
                [
                    "--calibrate",
                    "--provider",
                    AUTHORIZED_PROVIDER,
                    "--execution-manifest",
                    str(_MANIFEST),
                    "--output-dir",
                    str(_REPO_ROOT / "does-not-exist"),
                ]
            )
        assert exited.value.code == 2

    def test_the_readiness_gate_verifies_the_inputs_after_the_arithmetic(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """PLANTED: a landmine in place of the input check.

        The order is the live path's: arithmetic and authorization first, the
        record next, and the verified record is what `build_authorized_client`
        requires — so an unauthorized calibration never reaches a credential.
        """

        def landmine(*args: object, **kwargs: object) -> object:
            raise AssertionError("the record was read before the authorization")

        monkeypatch.setattr(instrument, "verify_calibration_set", landmine)
        root = _root_without_the_clause_binding_the_live_band(
            tmp_path, instrument.CALIBRATION_CLAUSE
        )
        with pytest.raises(LiveRunNotAuthorized):
            instrument.assert_ready_for_a_calibration(
                _converted_record(),
                provider=AUTHORIZED_PROVIDER,
                invocation=self._invocation(root),
                repo_root=root,
            )


class TestCalibrationRun:
    """What the mode measures, at $0, on the fake provider and the replay double."""

    def _calibrate(
        self, tmp_path: Path, client: Any = None
    ) -> instrument.CalibrationReport:
        return instrument.run_calibration(
            _converted_record(), output_dir=tmp_path / "units", client=client
        )

    def test_the_calibration_never_reads_the_held_out_record(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """PLANTED: a landmine on the held-out check, and the run completes.

        `verify_frozen_set` is the only reader of the live freeze in this
        module, so a calibration that completes with it mined is a calibration
        that never touched the set the evaluation is holding.
        """

        def landmine(*args: object, **kwargs: object) -> object:
            raise AssertionError("the calibration read the held-out record")

        monkeypatch.setattr(instrument, "verify_frozen_set", landmine)
        report = self._calibrate(tmp_path)
        assert report.inputs.record == instrument.DEFAULT_CALIBRATION_RECORD
        assert report.inputs.status == "development"
        assert report.inputs.band_first_seed == CONVERTED_BANDS[0].band.first_seed

    def test_the_rehearsal_measures_ten_units_at_zero_cost(
        self, tmp_path: Path
    ) -> None:
        """Five paired seeds, both arms, sixty calls, $0.00."""

        report = self._calibrate(tmp_path)
        assert report.units == instrument.calibration_units()
        assert report.paired_seeds == instrument.CALIBRATION_PAIRED_SEEDS
        assert report.dry_run is True
        assert report.total_cost_usd == 0.0
        assert report.limits == instrument.CALIBRATION_LIMITS
        assert [arm.units for arm in report.arms] == [5, 5]
        assert [arm.attempts for arm in report.arms] == [30, 30]
        assert len(report.unit_usage) == 10
        assert len(report.calls) == 60
        for arm in report.arms:
            assert [row.call_type for row in arm.by_call_type] == ["turn", "ballot"]
            assert [row.completions for row in arm.by_call_type] == [15, 15]

    def test_the_report_grades_nothing(self, tmp_path: Path) -> None:
        """No outcome, no verdict, no paired statistic anywhere in the payload.

        The frozen analysis is not evaluated here, and the check is on the
        payload rather than on the intention: a field carrying an outcome would
        fail this whether or not anything read it.
        """

        report = self._calibrate(tmp_path)
        payload = report.model_dump(mode="json")
        # The three prose fields say what this mode does NOT do, in those very
        # words, so they are dropped before the scan: what is under test is the
        # measurements, not the sentences describing their limits.
        payload.pop("caveat")
        payload.pop("percentile_rule")
        payload["proposal"].pop("rule")
        encoded = json.dumps(payload).lower()
        for forbidden in (
            "supported",
            "verdict",
            "mcnemar",
            "eject",
            "outcome",
            "primary",
        ):
            assert forbidden not in encoded, forbidden
        assert "No grader ran" in report.caveat

    def test_the_report_carries_no_prefix_bytes(self, tmp_path: Path) -> None:
        """PLANTED: a step's canonical JSON smuggled into the caveat.

        The evaluation's own guard runs over this report too, so one rule
        covers both payloads rather than one payload having its own.
        """

        inputs = instrument.verify_calibration_set(_converted_record())
        report = self._calibrate(tmp_path)
        assert_report_holds_no_prefix_bytes(report, inputs.prefixes)
        step = inputs.prefixes[0].steps[0]
        leaked = report.model_copy(
            update={
                "caveat": json.dumps(
                    step.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
                )
            }
        )
        with pytest.raises(PrefixBytesLeaked, match="scripted step"):
            assert_report_holds_no_prefix_bytes(leaked, inputs.prefixes)

    def test_the_replay_double_measures_the_two_schedules_apart(
        self, tmp_path: Path
    ) -> None:
        """The point of keying by call type, seen in the calibration's own rows.

        On the archived distribution the candidate arm's turns run to hundreds
        of output tokens and its ballots to a fraction of that, and both stay
        under their own caps. A summary that pooled them would report one
        number for two schedules and size a ballot's ceiling off a turn.
        """

        report = self._calibrate(tmp_path, client=UsageReplayProvider())
        for arm in report.arms:
            turn, ballot = arm.by_call_type
            assert turn.output_mean > ballot.output_mean
            assert turn.output_max < AUTHORIZED_SAMPLING.turn_max_tokens
            assert ballot.output_max < AUTHORIZED_SAMPLING.vote_max_tokens
            assert turn.input_max >= turn.input_p95 >= turn.input_mean
        candidate = next(arm for arm in report.arms if arm.arm == "combined_accounts")
        reference = next(arm for arm in report.arms if arm.arm == "repaired_clock")
        assert candidate.output_tokens > reference.output_tokens

    def test_the_percentile_is_nearest_rank(self) -> None:
        """PERTURBED: the rule stated is the rule computed.

        An interpolating percentile would report 95.5 for the sample below,
        which is not a token count anything was charged.
        """

        sample = list(range(1, 101))
        assert instrument._percentile(sample, 0.95) == 95
        assert instrument._percentile([7], 0.95) == 7
        assert instrument._percentile([1, 2], 0.95) == 2
        with pytest.raises(ValueError, match="no samples"):
            instrument._percentile([], 0.95)

    def test_the_proposal_is_the_stated_rule_applied_to_what_was_measured(
        self, tmp_path: Path
    ) -> None:
        """Recomputed from the report's own measured fields.

        Every number in the proposal is reproducible from the four measurements
        printed beside it, so a reader of the committed output can check the
        arithmetic without re-running anything.
        """

        report = self._calibrate(tmp_path, client=UsageReplayProvider())
        proposal = report.proposal
        units = proposal.units
        assert units == instrument.planned_units()
        assert proposal.unit_max_input_tokens == instrument._rounded_up(
            proposal.measured_max_unit_input_tokens * 3
        )
        assert proposal.unit_max_output_tokens == instrument._rounded_up(
            max(
                # The schedule of the caps the calibration DREW at: a proposal
                # reserves what its own measurement reserved, and lifting it to
                # the run's raised cap is the owner's step, on the card.
                instrument.unit_output_reservation(
                    sampling=instrument.CALIBRATION_SAMPLING
                ),
                proposal.measured_max_unit_output_tokens * 3,
            )
        )
        assert proposal.run_max_input_tokens == instrument._rounded_up(
            max(
                units * proposal.measured_mean_unit_input_tokens * 1.5,
                units * proposal.measured_max_unit_input_tokens,
            )
        )
        assert proposal.run_max_output_tokens == instrument._rounded_up(
            max(
                units * proposal.measured_mean_unit_output_tokens * 1.5,
                # The in-flight headroom term the gate enforces and the
                # proposal now carries: the run's last call is reserved against
                # the run budget after everything before it has been charged.
                units * proposal.measured_max_unit_output_tokens
                + instrument.CALIBRATION_SAMPLING.turn_max_tokens,
            )
        )
        assert proposal.run_max_input_tokens % 1_000 == 0

    def test_a_fixture_sized_proposal_says_it_clears_no_gate(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """PERTURBED by the provider: the same rule on two distributions.

        `DryRunProvider` derives its usage from the length of the payload it
        serialises, so a proposal computed from it is a tenth of a real one and
        the instrument's feasibility gate refuses it AGAINST THE COMMITTED
        PROFILE. The report says so in the gate's words instead of publishing
        the numbers as a measurement. `clears_the_feasibility_gate` is the
        proposal's own claim — these ceilings pay for a run of the units THIS
        sitting measured — which a proposal computed from any distribution
        clears by construction, so it is not where the two differ;
        `clears_the_committed_profiles_gate` is, and it is what this case reads.

        The two constants are patched to the STOPPED RUNS' archive, which is
        the profile the double below replays. That identity is the condition the
        comparison was written under and the refresh of 2026-09-15 broke: the
        committed profile is now a 120-unit sitting, and a five-seed calibration
        subsamples 30 of its 360 rows per bucket, so its maximum is legitimately
        below the profile's and every proposal computed from it is told so. The
        last block reads that unpatched state directly, and reads it as the
        arithmetic of a subsample rather than as a defect.
        """

        archive = stopped_runs_profile()
        largest_input, largest_output = archive.largest_unit()
        monkeypatch.setattr(instrument, "CALIBRATED_UNIT_INPUT_TOKENS", largest_input)
        monkeypatch.setattr(instrument, "CALIBRATED_UNIT_OUTPUT_TOKENS", largest_output)
        fixture = self._calibrate(tmp_path / "fixture")
        assert fixture.proposal.clears_the_committed_profiles_gate is False
        assert fixture.proposal.committed_profile_refusal is not None
        assert "run-level output ceiling" in fixture.proposal.committed_profile_refusal
        # Its own claim still holds: the ceilings pay for the units it saw.
        assert fixture.proposal.clears_the_feasibility_gate is True
        measured = self._calibrate(
            tmp_path / "measured",
            client=UsageReplayProvider(profile=archive),
        )
        assert measured.proposal.clears_the_committed_profiles_gate is True
        assert measured.proposal.committed_profile_refusal is None
        assert measured.proposal.clears_the_feasibility_gate is True
        assert measured.proposal.feasibility_refusal is None
        instrument.assert_limits_are_feasible(
            limits=instrument.proposed_limits(measured.proposal),
            # At the draw the proposal reserved against — its own. The gate it
            # reports clearing is that one, and saying so here is what keeps the
            # report's claim and this check the same claim.
            sampling=instrument.CALIBRATION_SAMPLING,
            calibrated_unit_input_tokens=largest_input,
            calibrated_unit_output_tokens=largest_output,
        )
        # Unpatched, against the profile this tree actually commits: a five-seed
        # sitting proposes below a 120-unit sitting's maxima and is told so.
        monkeypatch.undo()
        subsample = self._calibrate(
            tmp_path / "subsample", client=UsageReplayProvider()
        )
        assert subsample.proposal.clears_the_feasibility_gate is True
        assert subsample.proposal.clears_the_committed_profiles_gate is False
        assert (
            subsample.proposal.measured_max_unit_output_tokens
            < instrument.CALIBRATED_UNIT_OUTPUT_TOKENS
        )

    def test_a_stop_reports_its_partial_accounting(self, tmp_path: Path) -> None:
        """PLANTED: an endpoint that stops answering inside the third call.

        A calibration stops the way a run does — partial accounting, no retry
        beyond the transport bound, and the spend that bought nothing charged
        into it — because it is the same path.
        """

        spoiled = UsageReplayProvider(
            spoil_call=3,
            spoil_repeats=instrument.MAX_TRANSPORT_ATTEMPTS,
            mode="transport_error",
        )
        with pytest.raises(InstrumentAborted) as stopped:
            self._calibrate(tmp_path, client=spoiled)
        partial = stopped.value.partial
        assert partial.completed_units == 0
        assert partial.planned_units == instrument.calibration_units()
        assert "TransportAttemptsExhausted" in partial.reason
        assert partial.usage_by_arm["repaired_clock"].calls > 0

    def test_the_json_destination_is_made_before_the_run_not_after_it(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """PLANTED: the manifest's own command, into a directory nothing made.

        The live command the execution manifest documents writes to
        `audits/deduction-candidate/calibration-<date>/calibration.json`, whose
        dated parent does not exist until something creates it. `write_text`
        does not, and it ran AFTER the units and BEFORE the print — so the once-
        only spend the manifest authorizes would have completed and then lost
        its whole record to a FileNotFoundError with nothing on stdout. Neuter
        the mkdir in `_preflight_json_destination` and this goes red exactly
        there.
        """

        destination = tmp_path / "calibration-2026-09-14" / "calibration.json"
        assert not destination.parent.exists()
        assert (
            instrument.main(
                [
                    "--calibrate",
                    "--output-dir",
                    str(tmp_path / "units"),
                    "--json",
                    str(destination),
                ]
            )
            == 0
        )
        payload = json.loads(destination.read_text(encoding="utf-8"))
        assert payload["report_schema"] == instrument.CALIBRATION_SCHEMA
        # And on stdout as well, written there first: a write that fails anyway
        # costs the operator a copy-paste, not the measurement.
        assert instrument.CALIBRATION_SCHEMA in capsys.readouterr().out

    def test_an_unwritable_json_destination_refuses_before_it_spends(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: a destination whose parent is a FILE, so no directory can be.

        The preflight's other half. A path that cannot be written is refused at
        the argument parser, before a unit runs — which is the whole point of
        moving the check ahead of the calls: a refusal that arrives after the
        spend is not a refusal.
        """

        blocked = tmp_path / "not-a-directory"
        blocked.write_text("", encoding="utf-8")
        marker = tmp_path / "a-unit-ran"

        def landmine(*args: object, **kwargs: object) -> object:
            marker.write_text("", encoding="utf-8")
            raise AssertionError("the calibration ran before its output had a home")

        with pytest.raises(SystemExit) as refused:
            with pytest.MonkeyPatch.context() as patch:
                patch.setattr(instrument, "run_calibration", landmine)
                instrument.main(
                    [
                        "--calibrate",
                        "--output-dir",
                        str(tmp_path / "units"),
                        "--json",
                        str(blocked / "calibration.json"),
                    ]
                )
        assert refused.value.code == 2
        assert not marker.exists()


class TestCalibrationProfileRefresh:
    """The rehearsal double's profile, rebuilt from a calibration output."""

    def test_the_refresh_writes_a_profile_the_double_reads(
        self, tmp_path: Path
    ) -> None:
        """The documented command, run end to end through the CLI.

        `--calibrate --json <out>` writes the measurement;
        `--refresh-usage-profile <out> --profile-out <path>` turns it into a
        profile. Neither step reaches a provider.
        """

        measurement = tmp_path / "calibration.json"
        assert (
            instrument.main(
                [
                    "--calibrate",
                    "--output-dir",
                    str(tmp_path / "units"),
                    "--json",
                    str(measurement),
                ]
            )
            == 0
        )
        profile_path = tmp_path / "profile.json"
        assert (
            instrument.main(
                [
                    "--refresh-usage-profile",
                    str(measurement),
                    "--profile-out",
                    str(profile_path),
                ]
            )
            == 0
        )
        profile = UsageProfile.load(profile_path)
        assert len(profile.calls) == 60
        assert len(profile.units) == 10
        payload = json.loads(profile_path.read_text(encoding="utf-8"))
        # `finish_reason` joins the enumeration because it is the PROVIDER's
        # one-word reason for stopping — `"stop"`, `"length"` — and carries no
        # prompt, prefix or payload bytes; everything else a completion knows
        # stays out, which is what this assertion is for.
        permitted = {
            "arm",
            "call_type",
            "input_tokens",
            "output_tokens",
            "disposition",
            "finish_reason",
        }
        assert {key for row in payload["calls"] for key in row} <= permitted
        encoded = json.dumps(payload["calls"])
        for forbidden in ("prompt", "response", "seed", "room", "tick"):
            assert forbidden not in encoded, forbidden

    def test_the_rehearsal_on_a_refreshed_profile_runs_under_the_proposal(
        self, tmp_path: Path
    ) -> None:
        """The whole loop, at $0: measure, refresh, rehearse, check the gate.

        A hundred units on the refreshed profile complete under the ceilings the
        calibration proposed, and the proposal passes the feasibility gate. That
        is what makes the proposal a re-sizing a fourth authorization card could
        carry rather than four numbers in a report.

        All three steps are at the calibration's own draw, which is the loop as
        it ran: a proposal reserves against the caps it measured. The fourth
        authorization then RAISED the turn cap on the strength of that same
        measurement, and the test below is where the consequence is recorded —
        the proposal's per-unit output figure does not clear the run's new
        schedule, which is why the card lifted it by hand.
        """

        report = instrument.run_calibration(
            _converted_record(),
            output_dir=tmp_path / "units",
            client=UsageReplayProvider(),
        )
        profile_path = tmp_path / "profile.json"
        instrument.write_usage_profile(report, profile_path)
        refreshed = UsageProfile.load(profile_path)
        limits = instrument.proposed_limits(report.proposal)
        assert report.proposal.clears_the_feasibility_gate is True
        instrument.assert_limits_are_feasible(
            limits=limits,
            sampling=instrument.CALIBRATION_SAMPLING,
            # At THIS sitting's own measured maxima, which is the claim the
            # proposal makes and the one the rehearsal below then runs under.
            # Against the module's constants it is a different question — a
            # five-seed sitting against a 120-unit profile — and
            # `clears_the_committed_profiles_gate` is where that one is
            # reported.
            calibrated_unit_input_tokens=(
                report.proposal.measured_max_unit_input_tokens
            ),
            calibrated_unit_output_tokens=(
                report.proposal.measured_max_unit_output_tokens
            ),
        )
        rehearsed = run_dry(
            output_dir=tmp_path / "rehearsal",
            limits=limits,
            sampling=instrument.CALIBRATION_SAMPLING,
            client=UsageReplayProvider(profile=refreshed),
        )
        assert [arm.units for arm in rehearsed.arms] == [50, 50]
        assert rehearsed.total_cost_usd == 0.0

    def test_the_proposal_does_not_clear_the_raised_turn_caps_schedule(
        self, tmp_path: Path
    ) -> None:
        """The one figure the fourth authorization did not take from the report.

        `ceiling_proposal` reserves against the caps it measured, so a proposal
        made at the 2,048 draw clears 9,216 and no more. The card raised the
        run's turn cap on the strength of the same calibration, and a run that
        draws at 4,096 reserves 15,360 — so the proposal's per-unit output
        ceiling is refused for the run it was sizing, and the committed
        `AUTHORIZED_UNIT_MAX_OUTPUT_TOKENS` is the lifted figure rather than the
        reported one. This is that gap, held as arithmetic rather than as a
        sentence in a document.
        """

        report = instrument.run_calibration(
            _converted_record(),
            output_dir=tmp_path / "units",
            client=UsageReplayProvider(),
        )
        proposed = instrument.proposed_limits(report.proposal)
        assert proposed.unit_max_output_tokens < instrument.unit_output_reservation()
        with pytest.raises(instrument.LimitsInfeasible, match="per-unit output"):
            instrument.assert_limits_are_feasible(limits=proposed)
        assert AUTHORIZED_LIMITS.unit_max_output_tokens >= (
            instrument.unit_output_reservation()
        )

    def test_a_refresh_of_another_schema_is_refused(self, tmp_path: Path) -> None:
        """PLANTED: the same payload carrying another schema name.

        No silent fallback. A later shape of this output is a different
        measurement, and turning one into a profile as if it were this one is
        how a rehearsal ends up replaying counts it has misread.
        """

        report = instrument.run_calibration(
            _converted_record(), output_dir=tmp_path / "units"
        )
        planted = report.model_copy(update={"report_schema": "something-else/9"})
        with pytest.raises(ValueError, match="not a calibration"):
            instrument.usage_profile_from_calibration(planted)

    def _measured(self, tmp_path: Path) -> Path:
        """One calibration output on disk, as `--calibrate --json` writes it."""

        measurement = tmp_path / "calibration.json"
        assert (
            instrument.main(
                [
                    "--calibrate",
                    "--output-dir",
                    str(tmp_path / "units"),
                    "--json",
                    str(measurement),
                ]
            )
            == 0
        )
        return measurement

    @pytest.mark.parametrize(
        ("field", "planted"),
        [("disposition", "billed_and_refused_"), ("call_type", "turnn")],
    )
    def test_a_refresh_refuses_a_call_row_it_cannot_read(
        self, tmp_path: Path, field: str, planted: str
    ) -> None:
        """PLANTED: one misspelled value in one of the sixty call rows.

        These two fields are a parse boundary, and the refresh rewrites the
        profile the feasibility gate's two calibrated constants are held to.
        Typed as `str` they parsed clean and went silently wrong twice over:
        `usage_profile_from_calibration` counts a refusal by exact equality with
        `billed_and_refused`, and the rehearsal double keys its refusal off the
        same string, so a misspelled refusal replays as a resolved call and the
        committed profile carries it. Retype either field `str` and this goes
        red. Invalid input raises; there is no third disposition to fall back
        to.
        """

        measurement = self._measured(tmp_path)
        payload = json.loads(measurement.read_text(encoding="utf-8"))
        payload["calls"][0][field] = planted
        measurement.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        profile_path = tmp_path / "profile.json"
        with pytest.raises(ValidationError, match=field):
            instrument.main(
                [
                    "--refresh-usage-profile",
                    str(measurement),
                    "--profile-out",
                    str(profile_path),
                ]
            )
        assert not profile_path.exists(), "a refused refresh wrote a profile anyway"

    def test_the_dispositions_the_boundary_accepts_are_the_ledgers_own(self) -> None:
        """One list of dispositions, not two that drift.

        The boundary model's field and the ledger's `CapturedCall.disposition`
        are the same `CallDisposition`, so a value the run can record is a value
        the refresh can read and nothing else is. The same for the two call
        schedules.
        """

        fields = instrument.CalibrationCall.model_fields
        # Compared by members rather than by identity: what has to hold is the
        # SET of values the boundary accepts, and a plain `str` annotation
        # carries none, which is the defect this pins.
        assert get_args(fields["disposition"].annotation) == get_args(
            instrument.CallDisposition
        )
        assert get_args(fields["call_type"].annotation) == get_args(instrument.CallType)
        assert (
            instrument.CapturedCall.__dataclass_fields__["disposition"].type
            == "CallDisposition"
        )
        assert set(get_args(instrument.CallDisposition)) == {
            "resolved",
            "billed_and_refused",
            "unaccounted",
            "aborted",
        }
        assert set(get_args(instrument.CallType)) == set(instrument.CALL_TYPES)


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

    def test_the_mechanics_check_paragraph_quotes_the_run_it_describes(
        self, tmp_path: Path
    ) -> None:
        """The manifest's dry-run figures, re-derived from the dry run itself.

        These are the figures a re-binding actually moves: the fake provider
        reads each prompt, so its input heuristic and its graded counts are
        the BAND's and not the fixture's, and the paragraph carrying the third
        band's numbers under a row bound to the fourth would be a document
        describing a set it no longer authorizes. Every number quoted there is
        asserted here against the report, so the next re-binding turns this red
        rather than leaving the section stale.

        The command the paragraph names is this run without the temporary
        directory (`run_dry` makes its own), under the same authorized limits
        and caps, which is why it is measured here rather than described.

        The per-arm ballot TOTAL is derived here too, and it is the one figure
        of the paragraph that cannot be read off a single verdict column:
        `UnitGrade.verdict_counts` reports `guard_rewritten` as an OVERLAY on
        `supported`/`unsupported`/`uncited` rather than as a fourth bucket, so
        an arm's ballots are those three summed and nothing else. Quoting the
        two-arm total, or the three columns plus the overlay, is the arithmetic
        this assertion refuses.
        """

        report = run_dry(output_dir=tmp_path)
        assert report.limits == AUTHORIZED_LIMITS
        assert report.sampling == AUTHORIZED_SAMPLING
        if _the_document_is_mid_rebinding() is not None:
            # These figures are exactly the ones a re-binding moves, which is
            # what this case is for -- so while the row is still bound to the
            # band the paragraph WAS measured on, the paragraph is not stale and
            # there is nothing here to hold it to: `run_dry` draws the live
            # band, and re-measuring the section on it is the re-binding card's
            # acceptance item. The helper asserts the live run is refused
            # meanwhile, and the obligation case keeps the window from lasting.
            return
        manifest = _MANIFEST.read_text(encoding="utf-8")
        # The slice runs past `**The output dimension` to the end of the
        # section, because the dry-run paragraph is not the only prose the band
        # moves: the relevance paragraph below quotes the same run's naming
        # ballots and its off-target citations, and those are the band's too.
        paragraph = " ".join(
            manifest[
                manifest.index("## Verification of this manifest") : manifest.index(
                    "**A green dry run"
                )
            ].split()
        )
        for arm in report.arms:
            assert f"{arm.input_tokens:,}" in paragraph, arm.arm
            assert f"{arm.ejections} ejections" in paragraph, arm.arm
            assert f"{arm.role_correct} role-correct" in paragraph, arm.arm
            assert f"{arm.wrongful_ejections} wrongful" in paragraph, arm.arm
            assert (
                f"{arm.supported_correct_ejections} supported-correct" in paragraph
            ), arm.arm
            assert (
                f"{arm.naming_ballots} ballots naming the ejected player" in paragraph
            ), arm.arm
            assert (
                f"{arm.ballot_verdicts['supported']} supported ballots" in paragraph
            ), arm.arm
            assert (
                f"{arm.ballot_verdicts['guard_rewritten']} guard-rewritten" in paragraph
            ), arm.arm
            ballots = sum(
                arm.ballot_verdicts[verdict]
                for verdict in ("supported", "unsupported", "uncited")
            )
            assert f"{ballots:,} ballots an arm cast" in paragraph, arm.arm
            assert (
                f"{arm.terminal_units} of each arm's {arm.units} units" in paragraph
            ), arm.arm
            assert arm.terminal_units + arm.partial_units == arm.units
        larger = max(report.arms, key=lambda arm: arm.input_tokens)
        total = sum(arm.input_tokens for arm in report.arms)
        assert f"{total:,}" in paragraph
        assert f"{round(larger.input_tokens / larger.units):,} per unit" in paragraph

        # The relevance paragraph, further down the same section. Its two
        # figures are graded counts and move with the band exactly as the ones
        # above do, and its claim -- that the rule removed no role-correct
        # ejection -- is the equality it reads off them, asserted here rather
        # than trusted.
        for arm in report.arms:
            assert f"{arm.naming_ballots} naming ballots" in paragraph, arm.arm
            assert f"{arm.off_target_citations} off-target citations" in paragraph, (
                arm.arm
            )
            assert arm.supported_correct_ejections == arm.role_correct, arm.arm
            assert (
                f"the same {arm.supported_correct_ejections} as role-correct"
                in paragraph
            ), arm.arm

    def test_the_full_dry_run_survives_one_empty_completion(
        self, tmp_path: Path
    ) -> None:
        """The whole pipeline over the frozen set, with one call answered emptily.

        The retry's other cases are single units against a double; this is the
        run the card owes: 600 calls, one of which comes back with no
        completion, and the question is whether anything but the counters
        moves. Nothing does — the graded fields, the ballots and the token
        totals are the clean run's, because an attempt that produced nothing
        produced nothing to grade or to charge — and the retried arm is
        readable as retried from its `model_ids` alone.
        """

        clean = run_dry(output_dir=tmp_path / "clean")
        double = NoCompletionProvider(mode="empty_body", failures=1)
        retried = run_instrument(
            output_dir=tmp_path / "retried", client=double, provider="fake"
        )

        assert retried.total_cost_usd == 0.0
        assert retried.paired.paired_units == clean.paired.paired_units
        # One send more than the run has calls: one attempt, one retry, done.
        assert double.attempts == 601
        assert instrument.UNACCOUNTED_ATTEMPT_MODEL in retried.model_ids

        spoiled, untouched = retried.arms[0], retried.arms[1]
        assert spoiled.retried_calls == 1
        assert spoiled.unaccounted_attempts == 1
        assert spoiled.units_with_retries == 1
        assert dict(spoiled.attempts_by_trigger) == {"empty_completion": 1}
        assert untouched.retried_calls == 0
        assert dict(untouched.attempts_by_trigger) == {}

        graded = (
            "units",
            "ejections",
            "role_correct",
            "wrongful_ejections",
            "supported_correct_ejections",
            "naming_ballots",
            "off_target_citations",
            "terminal_units",
            "partial_units",
            "input_tokens",
            "output_tokens",
        )
        for before, after in zip(clean.arms, retried.arms, strict=True):
            assert after.arm == before.arm
            for field in graded:
                assert getattr(after, field) == getattr(before, field), field
            assert after.ballot_verdicts == before.ballot_verdicts
        # The one thing that does move: the unaccounted attempt occupies a row,
        # so the arm's calls exceed its completions by exactly that attempt.
        assert spoiled.calls == clean.arms[0].calls + 1
        assert untouched.calls == clean.arms[1].calls

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
    def test_the_per_call_caps_are_the_fourth_authorizations(self) -> None:
        """The vote cap is still the shipped default; the turn cap is not.

        The fourth authorization of 2026-09-14 raised the turn cap to 4,096 and
        left the vote cap alone, so the divergence is asserted rather than
        allowed to appear: the turn cap is the card's number, the vote cap is
        `meetings.manager`'s, and the shipped pair is still (2048, 1024), so a
        later edit to those defaults breaks this instead of moving what the
        owner authorized.
        """

        from meetings.manager import DEFAULT_TURN_MAX_TOKENS, DEFAULT_VOTE_MAX_TOKENS

        assert instrument.AUTHORIZED_TURN_MAX_TOKENS == 4096
        assert instrument.AUTHORIZED_TURN_MAX_TOKENS != DEFAULT_TURN_MAX_TOKENS
        assert instrument.AUTHORIZED_VOTE_MAX_TOKENS == DEFAULT_VOTE_MAX_TOKENS
        assert (DEFAULT_TURN_MAX_TOKENS, DEFAULT_VOTE_MAX_TOKENS) == (2048, 1024)

    def test_the_calibration_kept_the_caps_it_drew_at(self) -> None:
        """The calibration's own sampling, frozen apart from the run's.

        Its ceilings were approved against the 9,216-token schedule the caps it
        drew at reserve; the run's turn cap has since moved. Holding the two
        apart is what keeps the committed calibration re-derivable and keeps a
        spent authorization from silently paying for a draw nobody sized it for.
        """

        from meetings.manager import DEFAULT_TURN_MAX_TOKENS

        calibration = instrument.CALIBRATION_SAMPLING
        assert calibration.turn_max_tokens == DEFAULT_TURN_MAX_TOKENS
        assert calibration.vote_max_tokens == AUTHORIZED_SAMPLING.vote_max_tokens
        assert calibration.turn_temperature == AUTHORIZED_SAMPLING.turn_temperature
        assert calibration.vote_temperature == AUTHORIZED_SAMPLING.vote_temperature
        assert instrument.unit_output_reservation(sampling=calibration) == 9_216
        # And the committed output was drawn at exactly these values.
        recorded = json.loads(
            (
                _REPO_ROOT
                / "audits"
                / "deduction-candidate"
                / "calibration-2026-09-14"
                / "calibration.json"
            ).read_text(encoding="utf-8")
        )
        assert recorded["sampling"] == calibration.model_dump()

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
            # Re-sized on 2026-09-15 by the fifth authorization card, whose
            # Constraints table the manifest's token-budget row now copies, from
            # the SECOND live development calibration of that day. The output
            # ceiling FELL from the fourth authorization's 459,000 because the
            # rule was followed and v4 made units smaller on output; the input
            # one rose because its largest unit grew to 38,440.
            run_max_input_tokens=3_844_000,
            run_max_output_tokens=422_000,
            unit_max_input_tokens=116_000,
            unit_max_output_tokens=16_000,
            max_cost_usd=0.0,
            # Widened on 2026-09-13 by the third authorization card, whose
            # Constraints table the manifest's wall row now copies.
            elapsed_seconds=8 * 60 * 60,
            model_work_seconds=6 * 60 * 60,
        )

    def test_the_arms_run_the_clock_the_freeze_screened_under(self) -> None:
        for arm in instrument_arms():
            assert arm.temporal_version == TEMPORAL_OBSERVATION_VERSION


def _root_with_both_converted_records(tmp_path: Path) -> Path:
    """A repository root carrying copies of the two records this draw spans.

    The path is what makes a record a record — `_converted_band_for` matches on
    WHERE the file is — so a planted variant has to sit where the real one
    does, and both have to be present for a draw that spills from the first
    into the second.
    """

    assert tmp_path.resolve() != _REPO_ROOT.resolve()
    for converted in CONVERTED_BANDS:
        source = _REPO_ROOT / converted.manifest_path
        if not source.is_file():
            continue
        planted = tmp_path / converted.manifest_path
        planted.parent.mkdir(parents=True, exist_ok=True)
        planted.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return tmp_path


def _unit_record_with(
    *,
    turns: tuple[MeetingTurn, ...] = (),
    ballots: tuple[VoteBallot, ...] = (),
    roles: Mapping[str, Any] | None = None,
    calls: tuple[Any, ...] = (),
    arm: Any = "combined_accounts",
) -> Any:
    """One in-memory unit record carrying only what a detector reads."""

    return instrument.UnitRecord(
        seed=3000,
        arm=arm,
        meeting_id="m-1",
        outcome="SKIPPED",
        ejected_player_id=None,
        ballots=ballots,
        turns=turns,
        roles={"p-1": "IMPOSTOR"} if roles is None else dict(roles),
        prompts_by_agent={},
        calls=calls,
        game_outcome="CREWMATES",
        recorded_temporal_version=TEMPORAL_OBSERVATION_VERSION,
        recorded_experiment_config=None,
        prompt_versions={},
        defaults=instrument.DefaultedAttempts(),
        transport_attempts=instrument.TransportAttempts(),
    )


# ---------------------------------------------------------------------------
# The second development calibration (tasks/work/fresh-deduction-calibration-2.md)
# ---------------------------------------------------------------------------


def _calibration_2_report(
    tmp_path: Path, client: Any = None
) -> instrument.CalibrationReport:
    """One whole second-mode calibration at $0, on a $0 provider."""

    return instrument.run_calibration(
        output_dir=tmp_path / "units",
        client=client,
        limits=instrument.CALIBRATION_2_LIMITS,
        sampling=instrument.CALIBRATION_2_SAMPLING,
        paired_seeds=instrument.CALIBRATION_2_PAIRED_SEEDS,
    )


@pytest.fixture(scope="module")
def calibration_2_fake(
    tmp_path_factory: pytest.TempPathFactory,
) -> instrument.CalibrationReport:
    """One 120-unit rehearsal of the second mode, shared by the cases below.

    Module-scoped because it is the expensive thing in this file — sixty
    prefixes rebuilt and 720 fake completions — and every case that reads it
    reads the same sitting. The cases that have to drive the mode themselves
    (the CLI, a planted refusal) still run their own.
    """

    return _calibration_2_report(tmp_path_factory.mktemp("calibration-2-fake"))


@pytest.fixture(scope="module")
def calibration_2_replayed(
    tmp_path_factory: pytest.TempPathFactory,
) -> instrument.CalibrationReport:
    """The same mode over the archived per-call counts, shared the same way."""

    return _calibration_2_report(
        tmp_path_factory.mktemp("calibration-2-replay"), client=UsageReplayProvider()
    )


#: The planted truncations of the sitting below, as the double is asked for
#: them. One turn cut off across BOTH of its attempts — which is how the
#: manager's placeholder turn is reached rather than its retry — and eight
#: consecutive ballots, a window that spans the first pair of units and so
#: reaches both arms and both hidden roles. Sized to stay inside the mode's
#: 16,000-token per-unit output ceiling: three truncated turns in one unit
#: exhaust it, which is itself the reason the window is a window.
TRUNCATED_FIRST_TURN: Final[int] = 1
TRUNCATED_TURN_ATTEMPTS: Final[int] = 2
TRUNCATED_FIRST_BALLOT: Final[int] = 1
TRUNCATED_BALLOTS: Final[int] = 8


@pytest.fixture(scope="module")
def calibration_2_truncating(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[instrument.CalibrationReport, TruncatedCompletionProvider]:
    """The same mode against a provider that cuts ten completions off at cap.

    The flagship measurement of this card, driven end to end rather than
    asserted at :meth:`_unusable_response`: the sitting has to RUN through ten
    truncations, fail-soft each one and report them per arm, per call type and
    per hidden role with the provider's own `finish_reason`.
    """

    client = TruncatedCompletionProvider(
        truncate_turn=TRUNCATED_FIRST_TURN,
        turn_repeats=TRUNCATED_TURN_ATTEMPTS,
        truncate_ballot=TRUNCATED_FIRST_BALLOT,
        ballot_repeats=TRUNCATED_BALLOTS,
    )
    report = _calibration_2_report(
        tmp_path_factory.mktemp("calibration-2-truncating"), client=client
    )
    return report, client


def _turn_saying(text: str, *, speaker: str = "p-1") -> MeetingTurn:
    """One committed public turn carrying ``text`` and nothing else."""

    return MeetingTurn(
        turn_id="m-1:turn-0",
        turn_index=0,
        speaker=speaker,
        turn_kind="opening",
        reply_to=None,
        free_text=text,
    )


def _ballot_saying(text: str, *, voter: str = "p-1") -> VoteBallot:
    """One recorded ballot whose rationale is ``text``."""

    return VoteBallot(
        voter=voter,
        target="SKIP",
        confidence=0.5,
        primary_reason_id=None,
        rationale_text=text,
    )


class TestTheTwoSpentCalibrationModes:
    """The two SPENT sets, each whole, and every crossing of them refused.

    The first calibration has been spent and its output is the arithmetic this
    tree re-derives, so its five seeds, its 2,048-token turn cap and its ten
    units' ceilings stay exactly where they were. The second is a different
    authorization for a different spend: sixty paired seeds at the RUN's draw,
    under ceilings that pay for the schedule that draw reserves. What makes
    them two authorizations rather than one with knobs is that no value of
    either may be taken into the other.

    A third mode was authorized on 2026-09-18 and is unspent;
    `TestTheThirdAuthorizedCalibrationMode` below is its own set of cases, and
    the crossings of all three are enumerated there.
    """

    def _invocation(self, root: Path) -> LiveRunInvocation:
        return LiveRunInvocation.naming(
            root / EXECUTION_MANIFEST_PATH,
            provider=AUTHORIZED_PROVIDER,
            model=AUTHORIZED_MODEL,
            repo_root=root,
        )

    def test_the_second_set_is_the_cards_constraints_table(self) -> None:
        """The values the owner's merge authorizes, as one object."""

        assert instrument.CALIBRATION_2_PAIRED_SEEDS == 60
        assert instrument.CALIBRATION_2_LIMITS == RunLimits(
            run_max_input_tokens=4_500_000,
            run_max_output_tokens=450_000,
            unit_max_input_tokens=60_000,
            unit_max_output_tokens=16_000,
            max_cost_usd=0.0,
            elapsed_seconds=6 * 60 * 60,
            model_work_seconds=5 * 60 * 60,
        )
        # The point of the second mode: it draws the way the fifth run would.
        assert instrument.CALIBRATION_2_SAMPLING == AUTHORIZED_SAMPLING
        assert instrument.CALIBRATION_2_SAMPLING.turn_max_tokens == 4_096
        assert instrument.CALIBRATION_2_SAMPLING.vote_max_tokens == 1_024

    def test_the_first_set_is_untouched_by_the_second(self) -> None:
        """The spent authorization keeps its own seeds, caps and ceilings."""

        assert instrument.CALIBRATION_PAIRED_SEEDS == 5
        assert instrument.CALIBRATION_SAMPLING.turn_max_tokens == 2_048
        assert instrument.CALIBRATION_LIMITS.unit_max_output_tokens == 12_000
        assert instrument.CALIBRATION_LIMITS != instrument.CALIBRATION_2_LIMITS

    def test_each_mode_is_accepted_whole(self) -> None:
        """Both authorized sets pass, live, against the committed manifest."""

        for mode in instrument.CALIBRATION_MODES:
            matched = instrument.assert_calibration_is_authorized(
                provider=AUTHORIZED_PROVIDER,
                invocation=self._invocation(_REPO_ROOT),
                limits=mode.limits,
                sampling=mode.sampling,
                paired_seeds=mode.paired_seeds,
            )
            assert matched is mode

    def test_sixty_seeds_under_the_first_modes_limits_are_refused(self) -> None:
        """PLANTED: the second calibration's draw under the first's ceilings.

        Twelve thousand output tokens a unit pays for the 9,216-token schedule
        of the 2,048 draw and not for the 15,360 the raised turn cap reserves,
        so this crossing authorizes 720 calls it cannot pay for — the defect
        `assert_limits_are_feasible` exists to refuse, one authorization down.
        """

        with pytest.raises(LiveRunNotAuthorized, match="calibration limits"):
            instrument.assert_calibration_is_authorized(
                provider=AUTHORIZED_PROVIDER,
                invocation=self._invocation(_REPO_ROOT),
                limits=instrument.CALIBRATION_LIMITS,
                sampling=instrument.CALIBRATION_2_SAMPLING,
                paired_seeds=instrument.CALIBRATION_2_PAIRED_SEEDS,
            )

    def test_five_seeds_under_the_second_modes_limits_are_refused(self) -> None:
        """PLANTED: the first calibration's draw under the second's ceilings.

        A spend nobody approved: the owner authorized five paired seeds at the
        2,048 draw and sixty at 4,096, and five at 4,096 under 4.5 M input is
        neither.
        """

        with pytest.raises(LiveRunNotAuthorized, match="paired seeds"):
            instrument.assert_calibration_is_authorized(
                provider=AUTHORIZED_PROVIDER,
                invocation=self._invocation(_REPO_ROOT),
                limits=instrument.CALIBRATION_2_LIMITS,
                sampling=instrument.CALIBRATION_2_SAMPLING,
                paired_seeds=instrument.CALIBRATION_PAIRED_SEEDS,
            )

    def test_either_mode_drawing_at_the_others_caps_is_refused(self) -> None:
        """PLANTED both ways: each mode's seeds and ceilings at the other's draw.

        A calibration that draws differently from the run it sizes measures a
        distribution that run does not draw from. That is why the first mode's
        sampling was frozen at what it drew, and it is why the second exists.
        """

        for mode, other in (
            (instrument.CALIBRATION_MODES[0], instrument.CALIBRATION_MODES[1]),
            (instrument.CALIBRATION_MODES[1], instrument.CALIBRATION_MODES[0]),
        ):
            with pytest.raises(LiveRunNotAuthorized) as refused:
                instrument.assert_calibration_is_authorized(
                    provider=AUTHORIZED_PROVIDER,
                    invocation=self._invocation(_REPO_ROOT),
                    limits=mode.limits,
                    sampling=other.sampling,
                    paired_seeds=mode.paired_seeds,
                )
            assert "cross" in str(refused.value)

    def test_a_crossing_is_refused_on_the_rehearsal_path_too(self) -> None:
        """The mode lookup runs before the fake provider's early return.

        A rehearsal of a shape no live sitting could take is a rehearsal of
        nothing, and it is how a crossing reaches a runner with every offline
        check green.
        """

        with pytest.raises(LiveRunNotAuthorized, match="cross"):
            instrument.assert_calibration_is_authorized(
                provider="fake",
                invocation=None,
                limits=instrument.CALIBRATION_2_LIMITS,
                sampling=instrument.CALIBRATION_SAMPLING,
                paired_seeds=instrument.CALIBRATION_2_PAIRED_SEEDS,
            )

    def test_the_committed_manifest_authorizes_the_second_calibration(self) -> None:
        """The settled state: the second clause is in the document the gate reads."""

        assert instrument.CALIBRATION_2_CLAUSE in _MANIFEST.read_text(encoding="utf-8")

    def test_a_manifest_without_the_second_clause_refuses_it(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: the committed document with the second sentence removed.

        Each mode's clause authorizes that mode's spend and no other, so a
        manifest carrying only the first one authorizes only five seeds.
        """

        root = _root_without_the_clause_binding_the_live_band(
            tmp_path, instrument.CALIBRATION_2_CLAUSE
        )
        assert instrument.CALIBRATION_CLAUSE in (
            root / EXECUTION_MANIFEST_PATH
        ).read_text(encoding="utf-8")
        with pytest.raises(LiveRunNotAuthorized, match="no calibration clause"):
            instrument.assert_calibration_is_authorized(
                provider=AUTHORIZED_PROVIDER,
                invocation=self._invocation(root),
                limits=instrument.CALIBRATION_2_LIMITS,
                sampling=instrument.CALIBRATION_2_SAMPLING,
                paired_seeds=instrument.CALIBRATION_2_PAIRED_SEEDS,
                repo_root=root,
            )

    def test_the_feasibility_gate_accepts_the_second_mode_for_120_units(self) -> None:
        """The arithmetic of the Constraints table, against the shipped gate.

        Per-unit output 16,000 against the 15,360 schedule; per-unit input
        60,000 against the largest unit the mode was SIZED on; and both run
        ceilings against 120 units of that unit, the OUTPUT one with a further
        turn cap of in-flight headroom on top.

        The two figures are `CALIBRATION_SIZING_UNIT_*_TOKENS` rather than the
        module's live calibration, and passing them through the gate's own
        parameters is what the two calibration gates do. A mode's ceilings are
        the record of a spend the manifest authorizes ONCE, and this mode's was
        made on 2026-09-15; the profile that sitting then refreshed is the
        measurement the LIVE run's ceilings are checked against, and checking a
        spent mode against it would ask whether a sitting that already happened
        could be authorized under numbers that did not exist when it was. The
        case below is the other half: the mode read against the refreshed
        profile, refused, with the two figures named.
        """

        units = instrument.calibration_units(instrument.CALIBRATION_2_PAIRED_SEEDS)
        assert units == 120
        instrument.assert_limits_are_feasible(
            limits=instrument.CALIBRATION_2_LIMITS,
            sampling=instrument.CALIBRATION_2_SAMPLING,
            units=units,
            calibrated_unit_input_tokens=(
                instrument.CALIBRATION_SIZING_UNIT_INPUT_TOKENS
            ),
            calibrated_unit_output_tokens=(
                instrument.CALIBRATION_SIZING_UNIT_OUTPUT_TOKENS
            ),
        )
        assert (
            instrument.unit_output_reservation(
                sampling=instrument.CALIBRATION_2_SAMPLING
            )
            == 15_360
        )
        needed = (
            instrument.CALIBRATION_SIZING_UNIT_OUTPUT_TOKENS * units
            + instrument.CALIBRATION_2_SAMPLING.turn_max_tokens
        )
        assert needed <= instrument.CALIBRATION_2_RUN_MAX_OUTPUT_TOKENS
        assert (
            instrument.CALIBRATION_SIZING_UNIT_INPUT_TOKENS * units
            <= instrument.CALIBRATION_2_RUN_MAX_INPUT_TOKENS
        )

    def test_the_sizing_figures_are_the_committed_stopped_runs_archive(self) -> None:
        """The two sizing constants are read off committed evidence.

        `deduction_stopped_runs_usage_profile.json` is the profile that stood in
        `deduction_usage_profile.json` when both modes were authorized, kept
        beside it since the refresh of 2026-09-15. Its maxima are these two
        constants, so the gate a spent mode is checked against is the one it was
        approved under rather than two numbers typed into the module.
        """

        largest_input, largest_output = stopped_runs_profile().largest_unit()
        assert instrument.CALIBRATION_SIZING_UNIT_INPUT_TOKENS == largest_input
        assert instrument.CALIBRATION_SIZING_UNIT_OUTPUT_TOKENS == largest_output
        # And they are NOT the live run's, which is the whole point of the
        # split: the fifth authorization moved those and left these.
        assert instrument.CALIBRATED_UNIT_INPUT_TOKENS != largest_input
        assert instrument.CALIBRATED_UNIT_OUTPUT_TOKENS != largest_output

    def test_the_second_mode_is_refused_on_the_refreshed_profile(self) -> None:
        """PLANTED: the mode read against the measurement its own sitting made.

        120 units of the refreshed profile's largest unit need 4,612,800 input
        and 505,216 output — both above the 4,500,000 / 450,000 the mode binds —
        so a gate reading the live constants refuses it. That refusal is
        correct and is why no further sitting of this mode is authorized; it is
        NOT a reason to re-size `CALIBRATION_2_LIMITS`, which records a spend
        already made. Both numbers are named here so the refusal is a
        measurement rather than a shrug.
        """

        units = instrument.calibration_units(instrument.CALIBRATION_2_PAIRED_SEEDS)
        assert instrument.CALIBRATED_UNIT_INPUT_TOKENS * units == 4_612_800
        assert (
            instrument.CALIBRATED_UNIT_OUTPUT_TOKENS * units
            + instrument.CALIBRATION_2_SAMPLING.turn_max_tokens
            == 505_216
        )
        with pytest.raises(instrument.LimitsInfeasible) as refused:
            instrument.assert_limits_are_feasible(
                limits=instrument.CALIBRATION_2_LIMITS,
                sampling=instrument.CALIBRATION_2_SAMPLING,
                units=units,
            )
        assert "505,216" in str(refused.value)
        # The mode itself did not move.
        assert instrument.CALIBRATION_2_RUN_MAX_INPUT_TOKENS == 4_500_000
        assert instrument.CALIBRATION_2_RUN_MAX_OUTPUT_TOKENS == 450_000

    def test_the_first_modes_per_unit_output_cannot_pay_for_this_draw(self) -> None:
        """PLANTED: 12,000 output a unit against a 15,360-token schedule."""

        planted = instrument.CALIBRATION_2_LIMITS.model_copy(
            update={
                "unit_max_output_tokens": (
                    instrument.CALIBRATION_UNIT_MAX_OUTPUT_TOKENS
                )
            }
        )
        with pytest.raises(instrument.LimitsInfeasible, match="per-unit output"):
            instrument.assert_limits_are_feasible(
                limits=planted,
                sampling=instrument.CALIBRATION_2_SAMPLING,
                units=instrument.calibration_units(
                    instrument.CALIBRATION_2_PAIRED_SEEDS
                ),
            )


class TestTheCalibrationDrawSpansRecords:
    """Sixty paired seeds across the converted bands, in their own order."""

    def test_the_draw_is_fifty_of_one_record_then_ten_of_the_next(self) -> None:
        """The ordering rule, as objects rather than as a description.

        `CONVERTED_BANDS` in list order, ascending within each record, until
        the count is bound: the draw is reproducible from that list and the
        number sixty, with nothing left to the runner.
        """

        draw = instrument.verify_calibration_draw()
        assert draw.paired_seeds == instrument.CALIBRATION_2_PAIRED_SEEDS
        assert [len(drawn.prefixes) for drawn in draw.sets] == [50, 10]
        assert [drawn.band.first_seed for drawn in draw.sets] == [3000, 5000]
        assert list(draw.seeds) == sorted(draw.seeds)
        for drawn, converted in zip(draw.sets, CONVERTED_BANDS):
            assert drawn.record_path == (_REPO_ROOT / converted.manifest_path).resolve()
            assert len(drawn.record_sha256) == 64
            assert len(drawn.digests) == len(drawn.prefixes)

    def test_the_held_out_record_is_refused_by_name_inside_a_draw(self) -> None:
        """PLANTED: the live freeze named among the draw's records.

        The one mistake that costs something irreversible, refused at the path
        rather than after fifty prefixes have been rebuilt.
        """

        with pytest.raises(instrument.CalibrationInputsRejected) as refused:
            instrument.verify_calibration_draw(
                records=[_REPO_ROOT / MANIFEST_PATH], paired_seeds=1
            )
        assert "HELD-OUT" in str(refused.value)

    def test_a_draw_that_runs_out_of_accepted_seeds_is_refused(self) -> None:
        """PLANTED: sixty seeds from one fifty-seed record.

        Sixty paired seeds is the owner's decision 7 — the count that makes the
        bar a 99.2% chance of seeing a 1-in-13 event — so fifty of them measures
        a different thing and is a stop, not a smaller calibration.
        """

        with pytest.raises(
            instrument.CalibrationInputsRejected, match="runs out of accepted seeds"
        ) as refused:
            instrument.verify_calibration_draw(
                records=[_converted_record()],
                paired_seeds=instrument.CALIBRATION_2_PAIRED_SEEDS,
            )
        assert "50 seeds in all" in str(refused.value)

    def test_a_record_named_twice_is_refused(self) -> None:
        """PLANTED: the same record repeated to fill the count.

        The gate above counts SEEDS, so repeating a fifty-seed record fills
        sixty of them out of fifty distinct prefixes — ten rendered twice and
        reported as sixty paired seeds. It verified clean before the review of
        2026-09-15, which is an authorized live sitting spent on a draw the
        card does not describe.
        """

        with pytest.raises(instrument.CalibrationInputsRejected) as refused:
            instrument.verify_calibration_draw(
                records=[_converted_record(), _converted_record()],
                paired_seeds=instrument.CALIBRATION_2_PAIRED_SEEDS,
            )
        assert "twice" in str(refused.value)

    def test_a_record_list_in_another_order_is_refused(self) -> None:
        """PLANTED: the two converted records named back to front.

        Acceptance item 2 and the manifest's dated section both say the draw is
        the converted bands in the order those bands were converted. Reversed,
        the same two records draw fifty seeds of the 5000 band and ten of the
        3000 band — a different sixty seeds under the same authorization.
        """

        records = [
            _REPO_ROOT / CONVERTED_BANDS[1].manifest_path,
            _REPO_ROOT / CONVERTED_BANDS[0].manifest_path,
        ]
        with pytest.raises(instrument.CalibrationInputsRejected) as refused:
            instrument.verify_calibration_draw(
                records=records,
                paired_seeds=instrument.CALIBRATION_2_PAIRED_SEEDS,
            )
        assert "in the order those bands were converted" in str(refused.value)

    def test_a_record_list_that_skips_a_converted_record_is_refused(self) -> None:
        """PLANTED: two ascending, non-repeating lists that are not the draw.

        Round 1 refused a re-ordered list and a repeated one, which left the
        round-2 review a third shape. `CONVERTED_BANDS` held THREE development
        records, so `[band-5000, band-6000]` and `[band-3000, band-6000]` are
        each ascending and name no record twice; both verified clean at sixty
        seeds and drew a draw ending at seed 6010 where the authorized one ends
        at 5009 — a different sixty seeds under the same authorization. The
        rule is a PREFIX of `CONVERTED_BANDS`, not an ordered subsequence of it.
        """

        # The two shapes need three records and `CONVERTED_BANDS` only grows,
        # so they are built from its first three rather than by unpacking it.
        first, second, third = (
            _REPO_ROOT / converted.manifest_path for converted in CONVERTED_BANDS[:3]
        )
        for records in ([second, third], [first, third]):
            with pytest.raises(instrument.CalibrationInputsRejected) as refused:
                instrument.verify_calibration_draw(
                    records=records,
                    paired_seeds=instrument.CALIBRATION_2_PAIRED_SEEDS,
                )
            assert "with none skipped" in str(refused.value)

    def test_only_a_prefix_of_the_converted_records_is_accepted(self) -> None:
        """The PROPERTY acceptance item 2 claims, over every list, not three shapes.

        Three plants are three shapes, and the round-2 review found the fourth
        by enumerating rather than by reading. So this enumerates: every
        ordered arrangement of the converted records up to their own length,
        repetitions included, through `verify_calibration_draw` at the mode's
        sixty seeds. A list is accepted only when it is a prefix of
        `CONVERTED_BANDS` long enough to fill sixty, and every accepted list
        draws exactly the seeds the default draw draws — which is what makes
        the override unable to name a draw the card does not authorize.
        """

        paths = [_REPO_ROOT / converted.manifest_path for converted in CONVERTED_BANDS]
        canonical = instrument.verify_calibration_draw(
            paired_seeds=instrument.CALIBRATION_2_PAIRED_SEEDS
        ).seeds
        accepted: list[tuple[str, ...]] = []
        for length in range(1, len(paths) + 1):
            for candidate in itertools.product(paths, repeat=length):
                try:
                    draw = instrument.verify_calibration_draw(
                        records=list(candidate),
                        paired_seeds=instrument.CALIBRATION_2_PAIRED_SEEDS,
                    )
                except instrument.CalibrationInputsRejected:
                    continue
                accepted.append(tuple(path.name for path in candidate))
                assert draw.seeds == canonical
        # Every prefix long enough to fill sixty, and no other arrangement.
        # The first record holds fifty accepted seeds, so the shortest is the
        # first two; each longer prefix draws the same sixty, which is the
        # property the loop above asserts one candidate at a time.
        assert accepted == [
            tuple(path.name for path in paths[:length])
            for length in range(2, len(paths) + 1)
        ]

    def test_the_live_capable_preflight_refuses_the_same_two_lists(
        self, tmp_path: Path
    ) -> None:
        """The refusal is on the path that can SPEND, not only on the helper.

        `verify_calibration_draw` is where the check lives, but the callers the
        manifest documents as the gate are these two, and both take the same
        `records` override. A refusal that only the helper made would leave the
        live pre-flight accepting a draw nobody approved.
        """

        first = _REPO_ROOT / CONVERTED_BANDS[0].manifest_path
        second = _REPO_ROOT / CONVERTED_BANDS[1].manifest_path
        for records in ([first, first], [second, first]):
            with pytest.raises(instrument.CalibrationInputsRejected):
                instrument.assert_ready_for_a_calibration(
                    provider="fake",
                    invocation=None,
                    records=records,
                    limits=instrument.CALIBRATION_2_LIMITS,
                    sampling=instrument.CALIBRATION_2_SAMPLING,
                    paired_seeds=instrument.CALIBRATION_2_PAIRED_SEEDS,
                )
            with pytest.raises(instrument.CalibrationInputsRejected):
                instrument.run_calibration(
                    output_dir=tmp_path / "units",
                    records=records,
                    limits=instrument.CALIBRATION_2_LIMITS,
                    sampling=instrument.CALIBRATION_2_SAMPLING,
                    paired_seeds=instrument.CALIBRATION_2_PAIRED_SEEDS,
                )

    def test_the_live_capable_preflight_refuses_a_band_skipping_list(
        self, tmp_path: Path
    ) -> None:
        """PLANTED on the two paths that can SPEND: the round-2 review's lists.

        The same reasoning as the case above, for the shape round 1 left open.
        Both of these were ACCEPTED by both entry points at `74b9eea6`, each
        returning sixty seeds ending at 6010 against the authorized 5009, so a
        refusal that only the helper made would leave the live pre-flight and
        the runner spending an authorized sitting on a draw nobody approved.
        """

        # The same two shapes as the helper case above, built the same way.
        first, second, third = (
            _REPO_ROOT / converted.manifest_path for converted in CONVERTED_BANDS[:3]
        )
        for records in ([second, third], [first, third]):
            with pytest.raises(
                instrument.CalibrationInputsRejected, match="with none skipped"
            ):
                instrument.assert_ready_for_a_calibration(
                    provider="fake",
                    invocation=None,
                    records=records,
                    limits=instrument.CALIBRATION_2_LIMITS,
                    sampling=instrument.CALIBRATION_2_SAMPLING,
                    paired_seeds=instrument.CALIBRATION_2_PAIRED_SEEDS,
                )
            with pytest.raises(
                instrument.CalibrationInputsRejected, match="with none skipped"
            ):
                instrument.run_calibration(
                    output_dir=tmp_path / "units",
                    records=records,
                    limits=instrument.CALIBRATION_2_LIMITS,
                    sampling=instrument.CALIBRATION_2_SAMPLING,
                    paired_seeds=instrument.CALIBRATION_2_PAIRED_SEEDS,
                )

    def test_a_status_that_is_not_development_stops_the_draw(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: the second record of the draw flipped back to held out."""

        root = _root_with_both_converted_records(tmp_path)
        second = root / CONVERTED_BANDS[1].manifest_path
        payload = json.loads(second.read_text(encoding="utf-8"))
        payload["status"] = "held_out"
        second.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(
            instrument.CalibrationInputsRejected, match="not 'development'"
        ):
            instrument.verify_calibration_draw(
                repo_root=root, paired_seeds=instrument.CALIBRATION_2_PAIRED_SEEDS
            )

    def test_a_moved_digest_stops_the_draw_by_seed(self, tmp_path: Path) -> None:
        """PLANTED: one accepted digest edited in the record the draw spills into.

        Each drawn prefix is rebuilt with the unchanged generator and held to
        the digest that record froze, in every record of the draw and not only
        in the first.
        """

        root = _root_with_both_converted_records(tmp_path)
        second = root / CONVERTED_BANDS[1].manifest_path
        payload = json.loads(second.read_text(encoding="utf-8"))
        payload["accepted"] = [dict(row) for row in payload["accepted"]]
        moved = payload["accepted"][3]["seed"]
        payload["accepted"][3]["sha256"] = "0" * 64
        second.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(instrument.CalibrationInputsRejected) as refused:
            instrument.verify_calibration_draw(
                repo_root=root, paired_seeds=instrument.CALIBRATION_2_PAIRED_SEEDS
            )
        assert f"seed {moved}" in str(refused.value)

    def test_a_single_record_draw_still_refuses_a_record_it_cannot_fill(self) -> None:
        """The per-record refusal is unchanged where the draw is one record.

        `draw_at_most` is the multi-record path's and is off by default, so the
        first calibration's own "this record accepts N and I draw M" refusal
        still fires where it always did.
        """

        with pytest.raises(
            instrument.CalibrationInputsRejected, match="accepts 50 seeds"
        ):
            instrument.verify_calibration_set(_converted_record(), paired_seeds=51)


class TestATruncationIsAMeasurementInTheSecondModeOnly:
    """The scoped relaxation, and the three things it does not reach."""

    def _client(self, *, measuring: bool) -> Any:
        return instrument._InstrumentClient(
            DryRunProvider(),
            work_clock=instrument._ModelWorkClock(max_seconds=60.0),
            turn_max_tokens=AUTHORIZED_SAMPLING.turn_max_tokens,
            vote_max_tokens=AUTHORIZED_SAMPLING.vote_max_tokens,
            expected_model="the-authorized-model",
            truncation_is_a_measurement=measuring,
        )

    def test_the_live_path_still_stops_on_a_truncation(self) -> None:
        """PLANTED: a completion at its cap, on the run's own wrapper.

        The live evaluation's stop, unchanged. Both signals are planted, one
        at a time and together, because the stop fires on either.
        """

        client = self._client(measuring=False)
        for finish_reason, output_tokens in (
            ("length", 10),
            (None, 1_024),
            ("length", 1_024),
        ):
            stop = client._unusable_response(
                model="the-authorized-model",
                output_tokens=output_tokens,
                max_tokens=1_024,
                finish_reason=finish_reason,
            )
            assert isinstance(stop, instrument.PerCallCapExceeded)

    def test_the_second_calibration_counts_it_instead(self) -> None:
        """The same three completions, in the mode that measures them.

        No stop is returned, so the truncated body goes back to the meeting
        layer's shipped fail-soft and the call stays in the ledger, where the
        role split counts it.
        """

        client = self._client(measuring=True)
        for finish_reason, output_tokens in (
            ("length", 10),
            (None, 1_024),
            ("length", 1_024),
        ):
            assert (
                client._unusable_response(
                    model="the-authorized-model",
                    output_tokens=output_tokens,
                    max_tokens=1_024,
                    finish_reason=finish_reason,
                )
                is None
            )

    def test_the_identity_branch_still_stops_in_the_measurement_mode(self) -> None:
        """PLANTED: a foreign checkpoint's truncated completion.

        A response from a model this run is not authorized for is a stop in
        every mode. The relaxation reaches the cap branch and nothing else, and
        a truncated body from the wrong endpoint must not slip past both.
        """

        stop = self._client(measuring=True)._unusable_response(
            model="some-other-checkpoint",
            output_tokens=1_024,
            max_tokens=1_024,
            finish_reason="length",
        )
        assert isinstance(stop, instrument.ProviderIdentityMismatch)

    def test_the_evaluations_harness_never_asks_for_the_relaxation(self) -> None:
        """The two evaluation entry points build a stopping client.

        The flag is a parameter of `_build_harness` defaulted off, so this is
        what says the run path does not pass it.
        """

        harness = instrument._build_harness(
            client=DryRunProvider(),
            limits=AUTHORIZED_LIMITS,
            sampling=AUTHORIZED_SAMPLING,
            invocation=None,
        )
        assert harness.client._truncation_is_a_measurement is False

    def test_the_stop_rule_still_says_a_truncation_is_a_stop(self) -> None:
        """`STOP_RULE` is not edited by this card, and the manifest quotes it."""

        assert "a truncation is a stop, not a datum" in instrument.STOP_RULE
        assert " ".join(instrument.STOP_RULE.split()) in " ".join(
            _MANIFEST.read_text(encoding="utf-8").split()
        )


class TestTheRoleLeakDiagnostic:
    """The pre-declared detector: two positive shapes and the counted-out one."""

    def test_the_two_positive_shapes_are_counted(self) -> None:
        """PLANTED: the fourth run's two shapes, on an impostor speaker."""

        for text in (
            "I am the impostor and I am tired of pretending otherwise.",
            "I killed p-3 myself. There, I said it.",
            "I did it.",
        ):
            assert instrument.states_own_role_or_kill(text, role="IMPOSTOR") is True

    def test_the_rebuttal_the_diagnosis_counted_out_is_not(self) -> None:
        """PLANTED: seed 7015's turn-1, an impostor rebutting an accusation.

        The words are there and the assertion is not: the sentence attributes
        them to p-1 before quoting them. The diagnosis of 2026-09-15 counted
        this out by hand, and the detector has to count it out the same way or
        it reports a number that document does not.
        """

        assert (
            instrument.states_own_role_or_kill(
                "p-1's claim that I am the impostor rests on nothing and is weak.",
                role="IMPOSTOR",
            )
            is False
        )
        assert (
            instrument.states_own_role_or_kill(
                "I am not the impostor; p-2 is.", role="IMPOSTOR"
            )
            is False
        )

    def test_a_supposition_or_a_question_is_not_a_confession(self) -> None:
        """PLANTED: the shape the review of 2026-09-15 reproduced.

        A deflection that puts the words in play without asserting them —
        "if I am the impostor, why would I report the body?" — scored as a
        confession before the guard carried conditionals, and it inflated BOTH
        reported columns, because `opens_with_a_self_tell` runs the same
        predicate. A detector that counts a deflection as a confession is not
        the floor `ROLE_LEAK_RULE` claimed it was.

        The third case also covers the sentence splitter: `;` is not one of its
        boundaries, so the governor has to be read across it.
        """

        for text in (
            "If I am the impostor, why would I report the body?",
            "Unless I killed p-3, somebody in Electrical did.",
            "Suppose I am the impostor; then who vented in front of p-2?",
            "You all want to know whether I killed p-3.",
        ):
            assert instrument.states_own_role_or_kill(text, role="IMPOSTOR") is False
            assert (
                instrument.opens_with_a_self_tell(_ballot_saying(text), role="IMPOSTOR")
                is False
            )

    def test_the_guard_reaches_only_what_governs_the_words(self) -> None:
        """PERTURBED: the same governors AFTER the statement, where they govern nothing.

        The guard is a prefix check, so widening it must not turn every
        sentence carrying one of these words into a non-leak. A confession with
        a conditional trailing it is still a confession.
        """

        for text in (
            "I am the impostor, if you must know.",
            "I killed p-3, unless somebody wants to argue about it.",
        ):
            assert instrument.states_own_role_or_kill(text, role="IMPOSTOR") is True

    @pytest.mark.parametrize(
        "governor",
        ["how do", "how does", "how did", "why do", "why does", "why did"],
    )
    def test_a_question_in_the_present_or_the_past_is_not_a_confession(
        self, governor: str
    ) -> None:
        """PLANTED: the gap the fifth run's reference arm fell through (F2).

        `ROLE_LEAK_RULE` counts out "a conditional, a hypothetical or a question
        governing the words", but the guard carried only the MODAL
        interrogatives, so a question in the present or the past asserted
        nothing and was counted anyway. One seed-free string per governor, in
        the style of the supposition case above: no seed, no prefix and no
        rendered prompt is quoted here — the shape is what is under test.
        """

        for statement in ("I am the impostor", "I killed p-3"):
            text = f"{governor.capitalize()} you get {statement} out of that?"
            assert instrument.states_own_role_or_kill(text, role="IMPOSTOR") is False
            assert (
                instrument.opens_with_a_self_tell(_ballot_saying(text), role="IMPOSTOR")
                is False
            )

    @pytest.mark.parametrize(
        "text",
        [
            "What do you make of I am the impostor as a reading?",
            "What does it mean that I am the impostor?",
            "What did it look like when I killed p-3?",
        ],
    )
    def test_the_third_question_word_is_carried_too(self, text: str) -> None:
        """PLANTED: `what would` was carried and its siblings were not.

        Split from the pair above only because "what" takes a different frame;
        it is the same defect and the same repair, and the audit that found
        `how do` found these by enumeration rather than by another example.
        Each string carries exactly ONE governor — the one under test — so a
        pass cannot come from a word the old list already held.
        """

        assert instrument.states_own_role_or_kill(text, role="IMPOSTOR") is False
        assert (
            instrument.opens_with_a_self_tell(_ballot_saying(text), role="IMPOSTOR")
            is False
        )

    def test_the_widened_family_still_reaches_only_what_precedes_the_words(
        self,
    ) -> None:
        """PERTURBED: the same three words AFTER the statement govern nothing.

        The suffix perturbation `test_the_guard_reaches_only_what_governs_the_words`
        already pins, re-run against the widening: a confession is still a
        confession when one of the new governors trails it, and widening a
        prefix check must not turn every sentence carrying the word into a
        non-leak.
        """

        for text in (
            "I am the impostor, and how do you like that.",
            "I killed p-3, what did you expect.",
            "I vented, why did nobody look.",
        ):
            assert instrument.states_own_role_or_kill(text, role="IMPOSTOR") is True

    def test_the_governors_are_crossed_rather_than_listed(self) -> None:
        """The family is complete by construction, not by enumeration.

        Twelve pairings from three question words and four auxiliaries, every
        one of them counted out: a guard built by listing the ones somebody
        thought of is how `how do` went missing in the first place.
        """

        for question in ("why", "how", "what"):
            for auxiliary in ("would", "do", "does", "did"):
                text = f"{question} {auxiliary} anyone believe I am the impostor?"
                assert (
                    instrument.states_own_role_or_kill(text, role="IMPOSTOR") is False
                ), text

    def test_a_crewmate_naming_its_own_role_is_not_a_leak(self) -> None:
        """Every crewmate says so; counting it would report the roster."""

        assert (
            instrument.states_own_role_or_kill(
                "I am a crewmate and I was in Electrical.", role="CREWMATE"
            )
            is False
        )
        # And a crewmate LYING about being the impostor is not a leak either:
        # the statement is false, so it discloses nothing about that speaker.
        assert (
            instrument.states_own_role_or_kill(
                "I am the impostor, ha.", role="CREWMATE"
            )
            is False
        )

    def test_the_count_is_over_committed_turns_and_the_units_own_roles(self) -> None:
        """The detector reads the transcript, not the ballots or the prefix."""

        record = _unit_record_with(
            turns=(
                _turn_saying("I killed p-3 myself.", speaker="p-1"),
                _turn_saying("I was in Electrical the whole time.", speaker="p-2"),
                _turn_saying("I am the impostor.", speaker="p-2"),
            ),
            roles={
                "p-1": "IMPOSTOR",
                "p-2": "CREWMATE",
            },
        )
        assert instrument.count_leaking_turns(record) == 1

    def test_a_placeholder_turn_is_not_counted(self) -> None:
        """The meeting layer's substitute is the layer's text, not a leak."""

        placeholder = _turn_saying(
            next(iter(DEFAULT_TURN_FREE_TEXT.values())), speaker="p-1"
        )
        record = _unit_record_with(turns=(placeholder,), roles={"p-1": "IMPOSTOR"})
        assert instrument.count_leaking_turns(record) == 0

    def test_the_self_tell_count_reads_the_ballots_opening(self) -> None:
        """ "Opens with" rather than "contains", which is the measured shape."""

        opening = _ballot_saying("I am the impostor. I vote SKIP.")
        buried = _ballot_saying(
            "p-2 was in Electrical and p-3 never reported. I am the impostor."
        )
        assert instrument.opens_with_a_self_tell(opening, role="IMPOSTOR") is True
        assert instrument.opens_with_a_self_tell(buried, role="IMPOSTOR") is False

    def test_a_guard_marker_does_not_hide_the_opening(self) -> None:
        """A bracketed marker the meeting layer prepended is stripped first."""

        marked = _ballot_saying("[guard: redirected] I killed p-3. I vote SKIP.")
        assert instrument.opens_with_a_self_tell(marked, role="IMPOSTOR") is True

    def test_a_fail_softed_ballot_authors_no_self_tell(self) -> None:
        """PLANTED: the layer's own default SKIP, whose rationale it wrote."""

        defaulted = _ballot_saying(DEFAULT_VOTE_RATIONALE)
        assert instrument.opens_with_a_self_tell(defaulted, role="IMPOSTOR") is False

    def test_the_rule_is_published_with_the_count(self) -> None:
        """A count whose rule lives only in a module is one nobody can check."""

        assert "REPORTED diagnostic and not a gate" in instrument.ROLE_LEAK_RULE
        assert "REBUTTING" in instrument.ROLE_LEAK_RULE
        assert "SUPPOSED or ASKED" in instrument.ROLE_LEAK_RULE

    def test_the_rule_does_not_claim_the_count_is_a_floor(self) -> None:
        """PLANTED: the sentence the review of 2026-09-15 falsified.

        The rule shipped claiming "the figure is a floor" while its
        same-sentence guard could miss an attribution spread across two
        sentences and its conditional case over-counted outright. A string
        quoted in every output of this mode has to describe the error it
        actually carries, so it now says both directions and says so in those
        words.
        """

        assert "the figure is a floor" not in instrument.ROLE_LEAK_RULE
        assert "is not a floor" in instrument.ROLE_LEAK_RULE
        assert "BOTH directions" in instrument.ROLE_LEAK_RULE
        assert "ESTIMATE" in instrument.ROLE_LEAK_RULE


class TestTheRoleSplitReporting:
    """What the second mode measures that the first could not: the author."""

    def test_both_roles_are_reported_on_both_schedules(
        self, calibration_2_fake: instrument.CalibrationReport
    ) -> None:
        """Sixty impostor ballot draws an arm, which is the owner's bar.

        Decision 7 asks for at least sixty impostor-authored candidate ballots.
        Exposure is one impostor per 4p1i unit, so sixty candidate units is
        sixty draws, and this is where that arithmetic is a measurement rather
        than a projection.
        """

        report = calibration_2_fake
        assert report.mode == "2026-09-15"
        assert report.units == 120
        candidate = next(arm for arm in report.arms if arm.arm == "combined_accounts")
        rows = {(row.call_type, row.role): row for row in candidate.by_role}
        assert set(rows) == {
            ("turn", "CREWMATE"),
            ("turn", "IMPOSTOR"),
            ("ballot", "CREWMATE"),
            ("ballot", "IMPOSTOR"),
        }
        assert rows[("ballot", "IMPOSTOR")].draws == 60
        assert rows[("ballot", "CREWMATE")].draws == 120
        for row in candidate.by_role:
            assert row.output_max >= row.output_p95
            assert {stats.field for stats in row.lengths} <= {
                "rationale_text",
                "free_text",
                "claims_reason",
            }
            assert all(stats.samples > 0 for stats in row.lengths)

    def test_the_first_mode_reports_no_role_split(self, tmp_path: Path) -> None:
        """The committed five-seed output's shape, unchanged.

        Its bytes are the arithmetic this tree re-derives, so the mode that
        wrote them keeps writing them.
        """

        report = instrument.run_calibration(
            _converted_record(), output_dir=tmp_path / "units"
        )
        assert report.mode == "2026-09-14"
        assert all(arm.by_role == () for arm in report.arms)
        assert report.role_leak_rule == ""

    def test_the_report_carries_counts_and_lengths_only(
        self, calibration_2_fake: instrument.CalibrationReport
    ) -> None:
        """No prose, no prompt, no prefix and no outcome, checked on the payload.

        The role split measures the CONTENT of three fields, so the one thing
        this payload must not do is carry that content instead of its length.
        No key of any of them appears in it — `rationale_text` and `free_text`
        occur only as the NAME of a length statistic, never as a field with a
        value — and the evaluation's own prefix guard is run over it here as
        well as inside `run_calibration`.
        """

        report = calibration_2_fake
        payload = json.loads(report.model_dump_json())
        encoded = json.dumps(payload)
        for forbidden in (
            '"rationale_text":',
            '"free_text":',
            '"claims":',
            '"turns":',
            '"prompt":',
            '"prompts_by_agent":',
            '"steps":',
            '"outcome":',
        ):
            assert forbidden not in encoded, forbidden
        assert_report_holds_no_prefix_bytes(
            report, instrument.verify_calibration_draw().prefixes
        )
        assert instrument.ROLE_LEAK_RULE in payload["role_leak_rule"]

    def test_a_call_no_role_can_be_read_off_is_refused(self, tmp_path: Path) -> None:
        """PLANTED: a ledger row naming a speaker the unit holds no role for.

        Invalid input raises. Filing it under a default would move one of the
        two distributions this calibration exists to separate, silently.
        """

        record = _unit_record_with(
            turns=(),
            roles={"p-1": "IMPOSTOR"},
            calls=(
                instrument.CapturedCall(
                    agent_id="p-9",
                    prompt="",
                    max_tokens=AUTHORIZED_SAMPLING.vote_max_tokens,
                    input_tokens=1,
                    output_tokens=1,
                    cost_usd=0.0,
                    model="m",
                    seconds=0.1,
                ),
            ),
        )
        with pytest.raises(instrument.InstrumentError, match="no hidden role"):
            instrument._role_split_rows(
                "combined_accounts",
                records=[record],
                sampling=AUTHORIZED_SAMPLING,
            )

    def test_the_truncation_denominator_is_draws_not_rationales(
        self, calibration_2_fake: instrument.CalibrationReport
    ) -> None:
        """A fail-softed ballot is a draw that produced no rationale.

        The rate the fifth run is sized on is truncations per impostor DRAW, so
        the ledger rows are the denominator and the authored payloads are a
        separate, smaller count.
        """

        report = calibration_2_fake
        candidate = next(arm for arm in report.arms if arm.arm == "combined_accounts")
        row = next(
            item
            for item in candidate.by_role
            if (item.call_type, item.role) == ("ballot", "IMPOSTOR")
        )
        samples = {stats.field: stats.samples for stats in row.lengths}
        assert row.draws >= samples.get("rationale_text", 0)
        assert row.truncations == 0
        assert row.truncations_by_finish_reason == {}


class TestTheProposalCarriesTheInFlightHeadroom:
    """The residual of 2026-09-14, closed in the rule that writes the numbers."""

    def test_a_hundred_units_of_the_calibrations_largest_unit(self) -> None:
        """PLANTED: 4,590 over 100 units must propose at least 464,000.

        The first calibration's largest unit was 4,590 output tokens and the
        fourth authorization published 459,000 for a hundred units — exactly
        the product, and 4,096 short of what those hundred units reserve. The
        gate has always enforced the term; the PROPOSAL did not carry it, so
        the number it published was one the gate would refuse. It carries it
        now, and this is the arithmetic.

        The MEAN is deliberately well under the maximum, which is what makes
        this a plant. The rule takes the larger of ``units x mean x 1.5`` and
        ``units x max + one turn cap``, and the first version of this fixture
        set the mean equal to the maximum: 100 x 4,590 x 1.5 = 688,500 dominated
        the headroom branch, so the case passed with the term deleted and the
        plant proved nothing. Five units averaging 2,000 with one of them at
        4,590 put the headroom branch in front — 300,000 against 463,096 — so
        removing ``+ sampling.turn_max_tokens`` drops the proposal to 459,000
        and turns this case red.
        """

        measured = instrument.CalibrationArmUsage(
            arm="combined_accounts",
            units=5,
            attempts=30,
            completions=30,
            input_tokens=100_000,
            output_tokens=10_000,
            cost_usd=0.0,
            model_work_seconds=1.0,
            seconds_per_attempt=1.0,
            by_call_type=(),
            mean_unit_input_tokens=20_000.0,
            mean_unit_output_tokens=2_000.0,
            max_unit_input_tokens=35_232,
            max_unit_output_tokens=4_590,
            defaulted_turns=0,
            defaulted_votes=0,
            defaults_by_validation=0,
            defaults_by_deadline=0,
            degraded_openings=0,
            units_with_defaults=0,
            charged_failed_attempts=0,
            charged_failed_input_tokens=0,
            charged_failed_output_tokens=0,
            retried_calls=0,
            unaccounted_attempts=0,
            aborted_attempts=0,
            attempts_by_trigger={},
        )
        proposal = instrument.ceiling_proposal(
            [measured], sampling=AUTHORIZED_SAMPLING, units=100
        )
        # The mean branch is BELOW the floor being asserted, so the floor can
        # only be cleared by the headroom term. Without this line a reader has
        # to re-derive which branch bound, and the first version of this case
        # was wrong about exactly that.
        assert 100 * 2_000 * instrument.CEILING_PROPOSAL_RUN_MARGIN < 464_000
        assert proposal.run_max_output_tokens >= 464_000
        assert proposal.run_max_output_tokens >= (
            100 * 4_590 + AUTHORIZED_SAMPLING.turn_max_tokens
        )
        # And the number the fourth authorization published is below it, which
        # is what made this a residual rather than a preference. 459,000 is
        # also exactly what this proposal would publish with the term deleted,
        # and it is exactly what that authorization published. The fifth
        # authorization re-sized the ceiling on a later measurement, so the
        # residual is closed at both ends: the rule carries the term, and the
        # number in force was computed with it.
        assert 459_000 == 100 * 4_590
        assert AUTHORIZED_LIMITS.run_max_output_tokens != 459_000
        assert AUTHORIZED_LIMITS.run_max_output_tokens >= (
            instrument.CALIBRATED_UNIT_OUTPUT_TOKENS * 100
            + AUTHORIZED_SAMPLING.turn_max_tokens
        )
        assert AUTHORIZED_LIMITS.run_max_output_tokens < proposal.run_max_output_tokens

    def test_the_proposal_checks_itself_against_its_own_maxima(
        self, tmp_path: Path
    ) -> None:
        """Whose numbers the proposal's own claim is checked against.

        A proposal answers "can these ceilings pay for the run I measured", and
        checking that against a profile built from some earlier run's archives
        answers a different question. Both are reported, and a fixture-sized
        sitting is where they differ.
        """

        fixture = instrument.run_calibration(
            _converted_record(), output_dir=tmp_path / "units"
        )
        assert fixture.proposal.clears_the_feasibility_gate is True
        assert fixture.proposal.feasibility_refusal is None
        assert fixture.proposal.clears_the_committed_profiles_gate is False
        assert "run-level output" in str(fixture.proposal.committed_profile_refusal)
        assert "ONE further per-call turn cap" in instrument.CEILING_PROPOSAL_RULE

    def test_the_gate_reads_the_figures_it_is_handed(self) -> None:
        """PERTURBED: the same limits against two calibrated unit sizes.

        The parameterisation is what lets the proposal check itself; this is
        the parameter doing something, so it cannot be a no-op that happens to
        agree with the module constants.
        """

        limits = instrument.CALIBRATION_2_LIMITS
        instrument.assert_limits_are_feasible(
            limits=limits,
            sampling=instrument.CALIBRATION_2_SAMPLING,
            units=120,
            calibrated_unit_input_tokens=1_000,
            calibrated_unit_output_tokens=1_000,
        )
        with pytest.raises(instrument.LimitsInfeasible, match="per-unit input"):
            instrument.assert_limits_are_feasible(
                limits=limits,
                sampling=instrument.CALIBRATION_2_SAMPLING,
                units=120,
                calibrated_unit_input_tokens=limits.unit_max_input_tokens + 1,
                calibrated_unit_output_tokens=1_000,
            )


class TestTheSecondCalibrationEndToEnd:
    """The mode at $0, twice, and the refresh path over its output."""

    def test_the_fake_provider_runs_the_whole_mode(
        self, calibration_2_fake: instrument.CalibrationReport
    ) -> None:
        """120 units, 720 completions, both arms, $0.00."""

        report = calibration_2_fake
        assert report.units == 120
        assert report.paired_seeds == 60
        assert report.limits == instrument.CALIBRATION_2_LIMITS
        assert report.sampling == instrument.CALIBRATION_2_SAMPLING
        assert report.dry_run is True
        assert report.total_cost_usd == 0.0
        assert len(report.calls) == 720
        assert len(report.unit_usage) == 120
        assert [arm.units for arm in report.arms] == [60, 60]

    def test_the_inputs_block_names_every_record_and_its_seeds(
        self, calibration_2_fake: instrument.CalibrationReport
    ) -> None:
        """Which records were spent, with the digest each of them froze."""

        report = calibration_2_fake
        assert [row.record for row in report.input_records] == [
            CONVERTED_BANDS[0].manifest_path,
            CONVERTED_BANDS[1].manifest_path,
        ]
        assert [len(row.seeds) for row in report.input_records] == [50, 10]
        assert report.inputs == report.input_records[0]
        for row in report.input_records:
            assert row.status == "development"
            assert len(row.record_sha256) == 64
        drawn = [seed for row in report.input_records for seed in row.seeds]
        assert drawn[:1] == [3000]
        assert drawn[50:] == list(range(5000, 5010))

    def test_the_replay_double_runs_the_mode_on_measured_usage(
        self, calibration_2_replayed: instrument.CalibrationReport
    ) -> None:
        """The same mode over the archived per-call counts, still at $0."""

        report = calibration_2_replayed
        assert report.units == 120
        assert report.total_cost_usd == 0.0
        assert report.proposal.measured_max_unit_output_tokens > 0
        assert report.proposal.clears_the_feasibility_gate is True

    def test_the_refresh_path_reads_a_second_mode_output(
        self, tmp_path: Path, calibration_2_replayed: instrument.CalibrationReport
    ) -> None:
        """`--refresh-usage-profile` over a calibration-2 payload, at $0.

        The documented command is the runner's next step after the sitting, so
        the path has to read the shape the sitting writes — a report naming two
        records and carrying a role split — before the sitting is run, not
        after.
        """

        report = calibration_2_replayed
        measurement = tmp_path / "calibration.json"
        measurement.write_text(report.model_dump_json(indent=2), encoding="utf-8")
        profile_path = tmp_path / "profile.json"
        assert (
            instrument.main(
                [
                    "--refresh-usage-profile",
                    str(measurement),
                    "--profile-out",
                    str(profile_path),
                ]
            )
            == 0
        )
        profile = UsageProfile.load(profile_path)
        assert len(profile.calls) == 720
        assert len(profile.units) == 120
        payload = json.loads(profile_path.read_text(encoding="utf-8"))
        assert payload["built_from"]["mode"] == "2026-09-15"
        assert [row["seeds"] for row in payload["built_from"]["records"]] == [50, 10]
        permitted = {
            "arm",
            "call_type",
            "input_tokens",
            "output_tokens",
            "disposition",
            "finish_reason",
        }
        assert {key for row in payload["calls"] for key in row} <= permitted

    def test_the_cli_runs_the_mode_by_name(self, tmp_path: Path) -> None:
        """`--calibrate --calibration-mode 2026-09-15`, dry, at exit 0."""

        measurement = tmp_path / "calibration.json"
        assert (
            instrument.main(
                [
                    "--calibrate",
                    "--calibration-mode",
                    "2026-09-15",
                    "--output-dir",
                    str(tmp_path / "units"),
                    "--json",
                    str(measurement),
                ]
            )
            == 0
        )
        payload = json.loads(measurement.read_text(encoding="utf-8"))
        assert payload["mode"] == "2026-09-15"
        assert payload["units"] == 120

    def test_the_second_mode_refuses_a_single_record_flag(self, tmp_path: Path) -> None:
        """PLANTED: the draw's records named by hand.

        The draw is `CONVERTED_BANDS` in order and the seed count, with nothing
        left to choose; a flag that half-chose it would make the draw a runner
        decision.
        """

        with pytest.raises(SystemExit) as exited:
            instrument.main(
                [
                    "--calibrate",
                    "--calibration-mode",
                    "2026-09-15",
                    "--calibration-record",
                    str(_converted_record()),
                    "--output-dir",
                    str(tmp_path / "units"),
                ]
            )
        assert exited.value.code == 2


class TestATruncationIsMeasuredEndToEnd:
    """Acceptance item 3, driven through `run_calibration` rather than asserted.

    The review of 2026-09-15 neutered the tally in `_role_split_rows` and the
    whole suite stayed green: every case read a sitting with ZERO truncations,
    so `truncations == 0` and `truncations_by_finish_reason == {}` held whether
    the counter worked or not, and nothing drove a truncating provider through
    the mode at all. These cases are that plant — disable the tally and the
    mapping below goes to zeros and this class goes red.
    """

    #: Every role-split row of the truncating sitting, as
    #: `(arm, call type, role) -> (truncations, by finish reason)`. Ten planted
    #: truncations across two arms, two call schedules and both hidden roles,
    #: and a zero on every row that drew none — which is what says the tally is
    #: SPLIT rather than pooled onto the sitting.
    EXPECTED: Final[dict[tuple[str, str, str], tuple[int, dict[str, int]]]] = {
        ("repaired_clock", "turn", "CREWMATE"): (2, {"length": 2}),
        ("repaired_clock", "turn", "IMPOSTOR"): (0, {}),
        ("repaired_clock", "ballot", "CREWMATE"): (3, {"length": 3}),
        ("repaired_clock", "ballot", "IMPOSTOR"): (2, {"length": 2}),
        ("combined_accounts", "turn", "CREWMATE"): (0, {}),
        ("combined_accounts", "turn", "IMPOSTOR"): (0, {}),
        ("combined_accounts", "ballot", "CREWMATE"): (2, {"length": 2}),
        ("combined_accounts", "ballot", "IMPOSTOR"): (1, {"length": 1}),
    }

    def test_the_sitting_finishes_instead_of_stopping_on_the_first_one(
        self,
        calibration_2_truncating: tuple[
            instrument.CalibrationReport, TruncatedCompletionProvider
        ],
    ) -> None:
        """Ten truncations and 120 units: the mode measures them, it does not stop.

        On the live path any one of these raises `PerCallCapExceeded` and the
        sitting ends with 0 of 120 units. That is the behaviour the fourth run
        had and the reason this mode exists, so the run COMPLETING is the first
        half of the item.
        """

        report, client = calibration_2_truncating
        assert client.truncated == (
            [("turn", instrument.CALIBRATION_2_SAMPLING.turn_max_tokens)]
            * TRUNCATED_TURN_ATTEMPTS
            + [("ballot", instrument.CALIBRATION_2_SAMPLING.vote_max_tokens)]
            * TRUNCATED_BALLOTS
        )
        assert report.units == 120
        assert report.total_cost_usd == 0.0
        assert report.mode == "2026-09-15"

    def test_every_truncation_is_counted_on_its_own_arm_type_and_role(
        self,
        calibration_2_truncating: tuple[
            instrument.CalibrationReport, TruncatedCompletionProvider
        ],
    ) -> None:
        """PLANTED: the tally, as the ten rows the sitting has to produce.

        The provider's own `finish_reason` rides each row, which is the field
        the predecessor card added and the reason the count can name WHY a call
        ended rather than inferring it from a token comparison alone.
        """

        report, client = calibration_2_truncating
        counted = {
            (arm.arm, row.call_type, row.role): (
                row.truncations,
                row.truncations_by_finish_reason,
            )
            for arm in report.arms
            for row in arm.by_role
        }
        assert counted == self.EXPECTED
        assert sum(value[0] for value in counted.values()) == len(client.truncated)

    def test_each_truncation_fail_softs_into_the_meeting_layers_substitute(
        self,
        calibration_2_truncating: tuple[
            instrument.CalibrationReport, TruncatedCompletionProvider
        ],
    ) -> None:
        """The other half of the item: a marked SKIP, and a placeholder turn.

        Eight truncated ballots are eight defaulted votes, because a ballot has
        no re-ask. The one truncated TURN is cut across both of its attempts, so
        the manager exhausts its retry and substitutes the placeholder — which
        is why the turn plant is a window and not a single call. Every one of
        the nine is attributed to validation rather than to a deadline, and all
        ten completions are in the ledger as attempts the provider billed for.
        """

        report, client = calibration_2_truncating
        assert sum(arm.defaulted_votes for arm in report.arms) == TRUNCATED_BALLOTS
        assert sum(arm.defaulted_turns for arm in report.arms) == 1
        assert sum(arm.defaults_by_validation for arm in report.arms) == (
            TRUNCATED_BALLOTS + 1
        )
        assert sum(arm.defaults_by_deadline for arm in report.arms) == 0
        assert sum(arm.charged_failed_attempts for arm in report.arms) == len(
            client.truncated
        )

    def test_the_prose_lengths_exclude_what_the_layer_substituted(
        self,
        calibration_2_truncating: tuple[
            instrument.CalibrationReport, TruncatedCompletionProvider
        ],
    ) -> None:
        """A fail-softed draw is a draw that produced no prose, on both counts.

        The denominator rule the card states, under the condition that makes it
        bite: the truncated ballots are still DRAWS and still counted for the
        rate, and their rationales are the layer's, so they are not averaged
        into the length of anything a voter wrote.
        """

        report, _ = calibration_2_truncating
        for arm in report.arms:
            for row in arm.by_role:
                samples = {stats.field: stats.samples for stats in row.lengths}
                authored = samples.get(
                    "rationale_text" if row.call_type == "ballot" else "free_text", 0
                )
                assert authored <= row.draws
                if row.truncations:
                    assert authored <= row.draws - row.truncations


class TestTheManifestCarriesTheSecondCalibration:
    """The dated section, pinned to the constants it describes."""

    def _text(self) -> str:
        return _MANIFEST.read_text(encoding="utf-8")

    def test_the_section_exists_and_quotes_the_clause_verbatim(self) -> None:
        text = self._text()
        assert "## Development calibration 2 (2026-09-15)" in text
        assert instrument.CALIBRATION_2_CLAUSE in text
        # And the first section is still there, and still its own.
        assert "## Development calibration (2026-09-14)" in text
        assert instrument.CALIBRATION_CLAUSE in text

    @pytest.mark.parametrize(
        "quoted",
        [
            "| Calibration-2 paired seeds | 60",
            "| Calibration-2 per-unit token ceiling | 60,000 input / 16,000 output |",
            (
                "| Calibration-2 run-level token ceiling | 4,500,000 input / "
                "450,000 output |"
            ),
            (
                "| Calibration-2 wall-clock deadline | 5 h of model work within "
                "a 6 h elapsed deadline |"
            ),
            "| Calibration-2 units | 60 paired seeds x 2 arms = 120 units",
            "| Calibration-2 dollar limit | $0.00 marginal",
            "turn 4,096 output / vote 1,024",
        ],
    )
    def test_the_table_quotes_each_authorized_value(self, quoted: str) -> None:
        assert quoted in self._text()

    def test_the_table_is_the_constants(self) -> None:
        """The document and the module, held to each other rather than to prose."""

        text = self._text()
        limits = instrument.CALIBRATION_2_LIMITS
        assert f"{limits.unit_max_input_tokens:,} input" in text
        assert f"{limits.run_max_input_tokens:,} input" in text
        assert f"{instrument.CALIBRATION_2_PAIRED_SEEDS} paired seeds x 2 arms" in text
        assert int(limits.model_work_seconds // 3600) == 5
        assert int(limits.elapsed_seconds // 3600) == 6

    def test_the_section_scopes_the_truncation_ruling_to_this_mode(self) -> None:
        """The relaxation is a calibration rule and says so, beside the stop rule."""

        # Whitespace-normalised: the document is hard-wrapped, and a sentence
        # that crosses a line break is the same sentence.
        text = " ".join(self._text().split())
        assert (
            "A per-call truncation is a MEASUREMENT in this mode, and only in it"
        ) in text
        assert "the live run's stop rule is unchanged" in text
        # And the ruling it is scoped against is named in the same section.
        assert "`STOP_RULE` below is unedited" in text

    def test_the_leak_column_is_pre_declared_for_the_fifth_run(self) -> None:
        """Decision 9, as a reported column named before the run that reads it."""

        text = self._text()
        assert "role leak" in text.lower()
        assert "reported diagnostic" in text.lower()
        assert "does not block" in text.lower()


# ---------------------------------------------------------------------------
# The authored-ballot diagnostics
# (tasks/work/fresh-deduction-instrument-diagnostics.md)
# ---------------------------------------------------------------------------

#: The fifth run's committed archive. READ here and never written: the tests
#: below walk its hundred replays, parse each ballot back into the schema the
#: run recorded it under, and feed the run path's own function. No prefix, no
#: rendered prompt and no seed's text is printed by any of them.
_FIFTH_RUN: Final[Path] = (
    _REPO_ROOT / "audits" / "deduction-candidate" / "run-2026-09-16"
)


def _fifth_run_impostors() -> dict[int, str]:
    """``{seed: impostor id}`` for the fifth run, off the archive's own prefixes.

    The archive records no role — the run held them in memory and nothing
    downstream of it ever saw them — so the ground truth is recovered from the
    one action in a prefix that only an impostor can take: its single scripted
    kill. Player IDS only; no step, no prefix and no rendered prompt leaves
    this function.
    """

    payload = json.loads(
        (_FIFTH_RUN / "rendered-prefixes.json").read_text(encoding="utf-8")
    )
    impostors: dict[int, str] = {}
    for entry in payload["rendered"]:
        kills = [
            step
            for step in entry["canonical_json"]["steps"]
            if step["action"]["type"] == "kill"
        ]
        assert len(kills) == 1, entry["seed"]
        impostors[int(entry["seed"])] = str(kills[0]["action"]["actor"])
    return impostors


def _fifth_run_meeting(path: Path) -> Mapping[str, Any]:
    """The one meeting row of one archived replay."""

    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    meetings = [row for row in rows if row.get("kind") == "meeting"]
    assert len(meetings) == 1, path.name
    return cast(Mapping[str, Any], meetings[0])


def _fifth_run_counts(
    arm: str, *, authored_off_the_recorded_target: bool = False
) -> instrument.AuthoredBallotCounts:
    """One arm of the fifth run, through the run path's own function.

    ``authored_off_the_recorded_target`` is the perturbation the archive test
    plants: it drops the guard pair, so the authored target is read off
    ``target`` — what the TALLY saw — which is the whole difference between the
    authored layer and the recorded one.
    """

    impostors = _fifth_run_impostors()
    total = instrument.AuthoredBallotCounts()
    for path in sorted(_FIFTH_RUN.glob(f"{arm}-seed-*.jsonl")):
        seed = int(path.stem.rsplit("-", 1)[-1])
        meeting = _fifth_run_meeting(path)
        ballots = tuple(VoteBallot.model_validate(row) for row in meeting["ballots"])
        if authored_off_the_recorded_target:
            ballots = tuple(
                ballot.model_copy(
                    update={
                        "guard_redirected_from": None,
                        "guard_rewrite_reason": None,
                    }
                )
                for ballot in ballots
            )
        impostor = impostors[seed]
        roles = {
            ballot.voter: ("IMPOSTOR" if ballot.voter == impostor else "CREWMATE")
            for ballot in ballots
        }
        total = total.plus(
            instrument.authored_ballot_diagnostics(
                ballots=ballots,
                roles=cast(Any, roles),
                ejected_player_id=meeting["ejected_player_id"],
            )
        )
    return total


def _ballot_for(
    voter: str,
    target: str,
    *,
    authored: str | None = None,
    reason: str | None = None,
    rationale_text: str = "because.",
) -> VoteBallot:
    """One recorded ballot, with the guard pair set as the meeting layer sets it.

    ``rationale_text`` matters to the rewrite COUNT, which reads the marker
    stack rather than the typed reason; the default carries no marker, which is
    what a ballot no guard touched looks like.
    """

    return VoteBallot(
        voter=voter,
        target=target,
        confidence=0.7,
        primary_reason_id=None,
        rationale_text=rationale_text,
        guard_redirected_from=authored,
        guard_rewrite_reason=cast(Any, reason),
    )


class TestTheAuthoredLayerIsRecoverable:
    """The pure function over one unit's ballots, roles and ejected player."""

    def test_the_authored_target_is_the_guards_own_testimony(self) -> None:
        """Three readings, and the third is why ``target`` is not enough."""

        plain = _ballot_for("p-1", "p-2")
        redirected = _ballot_for(
            "p-1", "p-4", authored="p-2", reason="under_gate_redirect"
        )
        unparsed = _ballot_for("p-1", "SKIP", reason="parse_default")
        assert instrument.authored_ballot_target(plain) == "p-2"
        assert instrument.authored_ballot_target(redirected) == "p-2"
        assert instrument.authored_ballot_target(unparsed) is None

    def test_a_coerced_ballot_is_authored_but_never_cleared(self) -> None:
        """The citation gate's SKIP: the voter named a player, the tally saw none."""

        counts = instrument.authored_ballot_diagnostics(
            ballots=(
                _ballot_for(
                    "p-1",
                    "SKIP",
                    authored="p-4",
                    reason="uncited_coerced",
                    rationale_text=UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-4")
                    + "because.",
                ),
            ),
            roles=cast(Any, {"p-1": "CREWMATE", "p-4": "IMPOSTOR"}),
            ejected_player_id=None,
        )
        assert counts.crew_authored_ejects == 1
        assert counts.crew_authored_naming_impostor == 1
        assert counts.crew_authored_ejects_cleared == 0
        assert counts.guard_rewrites_by_reason["uncited_coerced"] == 1

    def test_the_new_reason_reaches_the_block_with_no_edit_to_it(self) -> None:
        """A reason ADDED to the schema union is a row here by derivation.

        ``BALLOT_REWRITE_REASONS`` reads ``BallotTargetRewriteReason`` itself, so
        ``off_target_coerced`` arrived in this block with a zero count and no
        edit to the block. PERTURBED: a hand-written list would have had to be
        edited, and the seeded zero below is what makes its absence visible
        rather than silent.
        """

        assert "off_target_coerced" in instrument.BALLOT_REWRITE_REASONS
        assert instrument.BALLOT_REWRITE_REASONS == tuple(
            sorted(get_args(BallotTargetRewriteReason))
        )
        counts = instrument.authored_ballot_diagnostics(
            ballots=(_ballot_for("p-1", "p-2"),),
            roles=cast(Any, {"p-1": "CREWMATE", "p-2": "IMPOSTOR"}),
            ejected_player_id=None,
        )
        assert counts.guard_rewrites_by_reason["off_target_coerced"] == 0

    def test_a_doubly_rewritten_ballot_is_counted_under_both_reasons(self) -> None:
        """PLANTED: the trap the typed field sets, at the count that fell into it.

        The fifth run's seed 8006 class, built by the REAL guards rather than by
        hand: an under-gate eject of p-2 is redirected onto p-3 and keeps a
        citation about p-2, and the relevance gate then coerces the redirected
        ballot. ``ballot_target_rewrite_provenance`` refuses to overwrite a
        reason, so ``guard_rewrite_reason`` still reads ``under_gate_redirect``
        while BOTH markers sit on the rationale. Reading the single field --
        what this block did before this card -- reports zero coercions on a run
        full of them; reading the stack reports one of each.
        """

        redirected = guard_ballot_target_graph(
            ballot=VoteBallot(
                voter="p-1",
                target="p-2",
                confidence=0.7,
                primary_reason_id="m-1:turn-0",
                rationale_text="because.",
            ),
            voter_id="p-1",
            suspicion_graph=(
                SuspicionEntry(player_id="p-2", suspicion=0.40, trust=0.5),
                SuspicionEntry(player_id="p-3", suspicion=0.80, trust=0.5),
            ),
            candidate_targets=("p-2", "p-3"),
            skip_confidence_threshold=0.6,
        )
        coerced = guard_ballot_citation(
            ballot=redirected,
            contradictions=(),
            citation_relevance_version=1,
            turns=(
                MeetingTurn(
                    turn_id="m-1:turn-0",
                    turn_index=0,
                    speaker="p-4",
                    turn_kind="opening",
                    reply_to=None,
                    free_text="p-2 was nowhere near ADMIN.",
                ),
            ),
        )
        assert coerced.target == "SKIP"
        assert coerced.guard_rewrite_reason == "under_gate_redirect"
        assert instrument.ballot_rewrites_that_fired(coerced) == (
            "off_target_coerced",
            "under_gate_redirect",
        )

        counts = instrument.authored_ballot_diagnostics(
            ballots=(coerced,),
            roles=cast(Any, {"p-1": "CREWMATE", "p-2": "CREWMATE", "p-3": "IMPOSTOR"}),
            ejected_player_id=None,
        )
        assert counts.guard_rewrites_by_reason["off_target_coerced"] == 1
        assert counts.guard_rewrites_by_reason["under_gate_redirect"] == 1
        # The old rule, restated so its failure is on the record: one row, and
        # the coercion invisible.
        assert Counter([coerced.guard_rewrite_reason]) == {"under_gate_redirect": 1}

    def test_a_model_echoing_a_marker_phrase_is_not_a_guard_that_fired(self) -> None:
        """PLANTED: the marker's own words, inside the model's own rationale.

        The vote prompt renders coerced ballots back to later voters, so
        "[off-target citation for eject target 'p-2' coerced to SKIP]" is a
        phrase the model has SEEN and can reproduce. A substring search over the
        whole rationale — what this counter did at `7a6066c1` — reads that echo
        as a coercion and moves the rewrite tally of a sitting the guard never
        touched. The count is anchored to the marker STACK instead, which the
        meeting layer builds by prepending and never by editing the body
        (`meetings/manager.py::_preserved_ballot_markers` raises if that is ever
        untrue), so text after the stack is the model's and is not read.
        """

        echoed = _ballot_for(
            "p-1",
            "p-3",
            rationale_text=(
                "Last meeting the log said "
                + OFF_TARGET_CITATION_EJECT_MARKER.format(target="p-2")
                + "so I am naming p-3 instead."
            ),
        )
        assert instrument.ballot_rewrites_that_fired(echoed) == ()
        counts = instrument.authored_ballot_diagnostics(
            ballots=(echoed,),
            roles=cast(Any, {"p-1": "CREWMATE", "p-3": "IMPOSTOR"}),
            ejected_player_id=None,
        )
        assert counts.guard_rewrites_by_reason["off_target_coerced"] == 0
        # The SAME marker at the head of the stack is still counted, which is
        # what says the anchor and not the marker text is what changed.
        genuine = _ballot_for(
            "p-1",
            "SKIP",
            authored="p-3",
            reason="off_target_coerced",
            rationale_text=(
                OFF_TARGET_CITATION_EJECT_MARKER.format(target="p-3")
                + "so I am naming p-3 instead."
            ),
        )
        assert instrument.ballot_rewrites_that_fired(genuine) == ("off_target_coerced",)

    def test_a_nulled_citation_marker_does_not_hide_the_rewrite_behind_it(
        self,
    ) -> None:
        """PERTURBED: the two citation-id validators run BEFORE the rewrites.

        Their markers sit deeper in the same stack, so a walk that stopped at
        the first unrecognised chunk would stop at one of them and miss the
        target rewrite in front of it. The walk steps over them and counts
        neither, which is the distinction between "not a rewrite" and "not a
        marker".
        """

        stacked = _ballot_for(
            "p-1",
            "SKIP",
            authored="p-3",
            reason="uncited_coerced",
            rationale_text=(
                UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-3")
                + INVALID_REASON_ID_MARKER.format(reason_id="m-1:turn-99")
                + "because."
            ),
        )
        assert instrument.ballot_rewrites_that_fired(stacked) == ("uncited_coerced",)
        behind = _ballot_for(
            "p-1",
            "SKIP",
            authored="p-3",
            reason="invalid_target",
            rationale_text=(
                INVALID_VOTE_TARGET_MARKER.format(target="p-9")
                + INVALID_OBSERVATION_ID_MARKER.format(observation_id="p-1:4:0")
                + UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-3")
                + "because."
            ),
        )
        assert instrument.ballot_rewrites_that_fired(behind) == (
            "invalid_target",
            "uncited_coerced",
        )

    def test_a_parse_default_rationale_is_the_whole_marker(self) -> None:
        """The one marker that is not a prefix to model text, still counted."""

        defaulted = _ballot_for(
            "p-1",
            "SKIP",
            reason="parse_default",
            rationale_text=VOTE_PARSE_DEFAULT_MARKER.format(head="{'target': 'p-"),
        )
        assert instrument.ballot_rewrites_that_fired(defaulted) == ("parse_default",)

    def test_a_coalition_can_clear_the_gate_without_converting(self) -> None:
        """PLANTED: the two meanings the memo's single "cleared" column carried.

        Both authored ballots pass ``guard_ballot_citation``, so the coalition
        CLEARS; one of them is then re-aimed by ``under_gate_redirect``, so it
        reached the tally naming somebody its voter did not, and the coalition
        does NOT convert. Counting those two as one figure is what made "10
        wrongful coalitions cleared" and "8 converted" read as one number.
        """

        counts = instrument.authored_ballot_diagnostics(
            ballots=(
                _ballot_for("p-1", "p-2"),
                _ballot_for("p-3", "p-4", authored="p-2", reason="under_gate_redirect"),
            ),
            roles=cast(
                Any,
                {"p-1": "CREWMATE", "p-2": "CREWMATE", "p-3": "IMPOSTOR"},
            ),
            ejected_player_id=None,
        )
        assert counts.wrongful_coalitions == 1
        assert counts.wrongful_coalitions_cleared == 1
        assert counts.wrongful_coalitions_converted == 0

    def test_a_coalition_both_of_whose_ballots_land_converts(self) -> None:
        """The control for the case above: no rewrite, so cleared and converted."""

        counts = instrument.authored_ballot_diagnostics(
            ballots=(_ballot_for("p-1", "p-4"), _ballot_for("p-2", "p-4")),
            roles=cast(
                Any,
                {"p-1": "CREWMATE", "p-2": "CREWMATE", "p-4": "IMPOSTOR"},
            ),
            ejected_player_id="p-4",
        )
        assert (
            counts.correct_coalitions,
            counts.correct_coalitions_cleared,
            counts.correct_coalitions_converted,
        ) == (1, 1, 1)
        assert counts.ejections == 1
        assert counts.role_correct_ejections == 1
        assert counts.crew_authored_role_correct_ejections == 1

    def test_a_guard_made_ejection_is_role_correct_but_not_crew_authored(self) -> None:
        """PLANTED: the correction refutation 3 of the diagnosis forced.

        The ejection lands on the impostor because a guard re-aimed a ballot
        the voter wrote against a crewmate. Role-correct, and not the crew's
        deduction — which is why the two counts are reported as a pair.
        """

        counts = instrument.authored_ballot_diagnostics(
            ballots=(
                _ballot_for("p-1", "p-4"),
                _ballot_for("p-2", "p-4", authored="p-1", reason="under_gate_redirect"),
            ),
            roles=cast(
                Any,
                {"p-1": "CREWMATE", "p-2": "CREWMATE", "p-4": "IMPOSTOR"},
            ),
            ejected_player_id="p-4",
        )
        assert counts.role_correct_ejections == 1
        assert counts.crew_authored_role_correct_ejections == 0

    def test_the_units_with_crew_on_crew_column_is_a_unit_flag(self) -> None:
        """Two harmful ballots in one unit are two ballots and one unit."""

        counts = instrument.authored_ballot_diagnostics(
            ballots=(_ballot_for("p-1", "p-2"), _ballot_for("p-2", "p-1")),
            roles=cast(
                Any,
                {"p-1": "CREWMATE", "p-2": "CREWMATE", "p-4": "IMPOSTOR"},
            ),
            ejected_player_id=None,
        )
        assert counts.crew_on_crew_authored_ejects == 2
        assert counts.units_with_crew_on_crew == 1

    def test_the_refused_reason_is_a_member_of_the_schemas_own_alias(self) -> None:
        """A renamed member would otherwise turn the exclusion into a no-op."""

        assert instrument.ILLEGAL_TARGET_REASON in get_args(BallotTargetRewriteReason)

    def test_an_illegal_authored_target_moves_no_harm_counter(self) -> None:
        """PLANTED: ``invalid_target`` is neither the impostor nor a crewmate.

        The id ``guard_redirected_from`` preserves under that reason is the one
        the meeting layer REFUSED — a hallucination here — so the ballot named
        nobody. It may not raise the crew-on-crew harm counter, may not flag
        the unit as carrying one, and may not enter the denominator read
        against the 0.5 null of TWO LEGAL TARGETS, which it had none of. It is
        counted in its own column, and the rewrite tally still sees it.
        """

        counts = instrument.authored_ballot_diagnostics(
            ballots=(
                _ballot_for(
                    "p-1",
                    "SKIP",
                    authored="p-99-ghost",
                    reason="invalid_target",
                    rationale_text=INVALID_VOTE_TARGET_MARKER.format(
                        target="p-99-ghost"
                    )
                    + "because.",
                ),
            ),
            roles=cast(Any, {"p-1": "CREWMATE", "p-2": "CREWMATE", "p-4": "IMPOSTOR"}),
            ejected_player_id=None,
        )
        assert counts.crew_authored_ejects == 0
        assert counts.crew_authored_naming_impostor == 0
        assert counts.crew_on_crew_authored_ejects == 0
        assert counts.units_with_crew_on_crew == 0
        assert counts.crew_authored_illegal_targets == 1
        assert counts.guard_rewrites_by_reason["invalid_target"] == 1

    def test_two_ballots_at_one_refused_id_are_no_coalition(self) -> None:
        """PLANTED: a bloc the meeting could not have ejected anybody on.

        Two voters naming the same hallucinated id agreed about NOBODY, so the
        funnel counts no wrongful coalition and the harm counter stays at zero.
        """

        counts = instrument.authored_ballot_diagnostics(
            ballots=(
                _ballot_for(
                    "p-1", "SKIP", authored="p-99-ghost", reason="invalid_target"
                ),
                _ballot_for(
                    "p-2", "SKIP", authored="p-99-ghost", reason="invalid_target"
                ),
            ),
            roles=cast(Any, {"p-1": "CREWMATE", "p-2": "CREWMATE", "p-4": "IMPOSTOR"}),
            ejected_player_id=None,
        )
        assert counts.wrongful_coalitions == 0
        assert counts.wrongful_coalitions_cleared == 0
        assert counts.crew_on_crew_authored_ejects == 0
        assert counts.crew_authored_illegal_targets == 2

    def test_a_self_vote_and_a_dead_target_are_illegal_too(self) -> None:
        """The other two shapes the same reason is minted for.

        ``normalize_ballot_target`` refuses a vote for oneself and a vote for a
        player no longer living, because the manager's candidate set is
        living-minus-voter. Both are on the roster, so the reason is what
        settles them; the impostor's own row is counted the same way.
        """

        counts = instrument.authored_ballot_diagnostics(
            ballots=(
                _ballot_for("p-1", "SKIP", authored="p-1", reason="invalid_target"),
                _ballot_for("p-4", "SKIP", authored="p-3", reason="invalid_target"),
            ),
            roles=cast(
                Any,
                {
                    "p-1": "CREWMATE",
                    "p-2": "CREWMATE",
                    "p-3": "CREWMATE",
                    "p-4": "IMPOSTOR",
                },
            ),
            ejected_player_id=None,
        )
        assert counts.crew_authored_ejects == 0
        assert counts.crew_authored_illegal_targets == 1
        assert counts.impostor_authored_ejects == 0
        assert counts.impostor_authored_illegal_targets == 1

    def test_an_id_nobody_on_the_roster_carries_is_illegal_unrewritten(self) -> None:
        """The belt to the reason's brace: the roster is checked as well.

        Nothing in the meeting layer records an unrewritten ballot at an id off
        the roster, and if one ever arrived it would still be a trial with no
        legal target rather than crew-on-crew harm.
        """

        counts = instrument.authored_ballot_diagnostics(
            ballots=(_ballot_for("p-1", "p-99-ghost"),),
            roles=cast(Any, {"p-1": "CREWMATE", "p-2": "CREWMATE", "p-4": "IMPOSTOR"}),
            ejected_player_id=None,
        )
        assert counts.crew_authored_ejects == 0
        assert counts.crew_on_crew_authored_ejects == 0
        assert counts.crew_authored_illegal_targets == 1

    def test_the_illegal_column_leaves_the_legal_denominator_alone(self) -> None:
        """The arm's block: one legal trial, not two, and the column beside it.

        The precision tail is the figure the exclusion protects — a refused id
        in the denominator would drag a 1-of-1 toward a 1-of-2.
        """

        counts = instrument.authored_ballot_diagnostics(
            ballots=(
                _ballot_for("p-1", "p-4"),
                _ballot_for(
                    "p-2", "SKIP", authored="p-99-ghost", reason="invalid_target"
                ),
            ),
            roles=cast(Any, {"p-1": "CREWMATE", "p-2": "CREWMATE", "p-4": "IMPOSTOR"}),
            ejected_player_id=None,
        )
        block = instrument.authored_ballot_block(counts)
        assert block.crew_authored_ejects == 1
        assert block.crew_authored_naming_impostor == 1
        assert block.crew_on_crew_authored_ejects == 0
        crew = next(row for row in block.by_voter_role if row.role == "CREWMATE")
        assert (crew.authored, crew.cleared, crew.coerced) == (1, 1, 0)
        assert crew.illegal_targets == 1
        # The tail is asked of 1 of 1 against the 0.5 null — P(X >= 1 | n = 1)
        # = 0.5 — where the refused ballot in the denominator would make it
        # 1 of 2 and P(X >= 1 | n = 2) = 0.75.
        assert instrument.CREW_PRECISION_NULL == 0.5
        assert block.crew_authored_precision_p == pytest.approx(0.5)

    def test_the_rewrite_tally_keys_over_the_schemas_own_alias(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """PLANTED: a member ADDED to the alias appears with a zero count.

        The relevance-aware citation guard adds ``off_target_coerced`` on top of
        this branch. A tally keyed on a literal list would silently drop it, so
        the list is read off ``BallotTargetRewriteReason`` and this plants the
        member the guard card will add.
        """

        assert instrument.BALLOT_REWRITE_REASONS == tuple(
            sorted(get_args(BallotTargetRewriteReason))
        )
        monkeypatch.setattr(
            instrument,
            "BALLOT_REWRITE_REASONS",
            tuple(sorted((*instrument.BALLOT_REWRITE_REASONS, "off_target_coerced"))),
        )
        counts = instrument.authored_ballot_diagnostics(
            ballots=(_ballot_for("p-1", "p-4"),),
            roles=cast(Any, {"p-1": "CREWMATE", "p-4": "IMPOSTOR"}),
            ejected_player_id=None,
        )
        assert counts.guard_rewrites_by_reason["off_target_coerced"] == 0
        assert set(counts.guard_rewrites_by_reason) == set(
            instrument.BALLOT_REWRITE_REASONS
        )


class TestTheFifthRunsArchiveReproducesTheEvidenceTable:
    """The card's Evidence table, recomputed from the hundred committed replays.

    Not a description of the archive: the run path's own
    ``authored_ballot_diagnostics`` is what produces every figure here, over
    ballots parsed back into ``VoteBallot`` with no new parser. What the owner's
    merge authorizes is these numbers, so a later edit that moves one of them
    turns this red rather than quietly re-describing a run that already
    happened.
    """

    def test_the_candidate_arms_crew_rows_are_the_memos(self) -> None:
        """51 of 81 naming the impostor, 30 of 81 on a crewmate, in 27 units."""

        counts = _fifth_run_counts("combined_accounts")
        assert counts.crew_authored_ejects == 81
        assert counts.crew_authored_naming_impostor == 51
        assert counts.crew_on_crew_authored_ejects == 30
        assert counts.units_with_crew_on_crew == 27

    def test_the_reference_arms_crew_rows_are_the_memos(self) -> None:
        """4 of 10 naming the impostor, 6 of 10 on a crewmate, in 6 units."""

        counts = _fifth_run_counts("repaired_clock")
        assert counts.crew_authored_ejects == 10
        assert counts.crew_authored_naming_impostor == 4
        assert counts.crew_on_crew_authored_ejects == 6
        assert counts.units_with_crew_on_crew == 6

    def test_the_coalition_funnel_separates_cleared_from_converted(self) -> None:
        """11 correct and 22 wrongful authored; 2 and 8 convert; 10 wrongful clear.

        The figure the memo carried once and meant twice. Two of the ten
        wrongful coalitions that cleared the citation gate never converted —
        their swing ballot was re-aimed onto the impostor — and those two are
        the "guard-made" role-correct ejections.
        """

        candidate = _fifth_run_counts("combined_accounts")
        assert candidate.correct_coalitions == 11
        assert candidate.correct_coalitions_converted == 2
        assert candidate.wrongful_coalitions == 22
        assert candidate.wrongful_coalitions_cleared == 10
        assert candidate.wrongful_coalitions_converted == 8
        reference = _fifth_run_counts("repaired_clock")
        assert reference.correct_coalitions == 0
        assert (
            reference.wrongful_coalitions,
            reference.wrongful_coalitions_cleared,
        ) == (
            1,
            1,
        )
        assert reference.wrongful_coalitions_converted == 1

    def test_the_gate_survival_is_role_asymmetric(self) -> None:
        """42 of 81 crew and 33 of 38 impostor: the funnel's second stage."""

        candidate = _fifth_run_counts("combined_accounts")
        assert candidate.crew_authored_ejects_cleared == 42
        assert candidate.impostor_authored_ejects == 38
        assert candidate.impostor_authored_ejects_cleared == 33
        reference = _fifth_run_counts("repaired_clock")
        assert reference.crew_authored_ejects_cleared == 10
        assert (
            reference.impostor_authored_ejects,
            reference.impostor_authored_ejects_cleared,
        ) == (4, 4)

    def test_the_ejections_are_four_role_correct_and_two_crew_authored(self) -> None:
        """Of 12: 4 role-correct, and 2 of those the crew actually authored."""

        candidate = _fifth_run_counts("combined_accounts")
        assert candidate.ejections == 12
        assert candidate.role_correct_ejections == 4
        assert candidate.crew_authored_role_correct_ejections == 2
        reference = _fifth_run_counts("repaired_clock")
        assert (
            reference.ejections,
            reference.role_correct_ejections,
            reference.crew_authored_role_correct_ejections,
        ) == (1, 0, 0)

    def test_the_precision_tail_is_the_one_the_memo_quotes(self) -> None:
        """63.0% of 81 against the 0.5 null, one-sided p = 0.013."""

        block = instrument.authored_ballot_block(_fifth_run_counts("combined_accounts"))
        assert round(block.crew_authored_precision_p, 3) == 0.013
        # And the reference arm's 4 of 10 is nowhere near it.
        reference = instrument.authored_ballot_block(
            _fifth_run_counts("repaired_clock")
        )
        assert reference.crew_authored_precision_p > 0.5

    def test_reading_the_authored_target_off_the_recorded_one_moves_the_row(
        self,
    ) -> None:
        """PLANTED: the recorded target is the TALLY's reading, not the voter's.

        Dropping the guard pair — reading ``target`` as though the voter had
        written it — collapses the candidate's crew row from 81 authored
        ejections to the 42 that survived the citation gate, which is exactly
        the layer this block exists to see under. The reference arm barely
        moves, because almost nothing of it was rewritten, which is why the
        defect would have been invisible on that arm alone.
        """

        perturbed = _fifth_run_counts(
            "combined_accounts", authored_off_the_recorded_target=True
        )
        assert perturbed.crew_authored_ejects == 42
        assert perturbed.crew_authored_ejects != 81

    def test_the_walk_writes_nothing_to_the_archive(self) -> None:
        """A test that reads a committed record must leave it byte-identical."""

        def fingerprint() -> dict[str, tuple[int, str]]:
            return {
                path.name: (
                    path.stat().st_size,
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                )
                for path in sorted(_FIFTH_RUN.iterdir())
                if path.is_file()
            }

        before = fingerprint()
        _fifth_run_counts("combined_accounts")
        _fifth_run_counts("repaired_clock")
        assert fingerprint() == before

    def test_the_archive_holds_the_hundred_replays_the_walk_expects(self) -> None:
        """A silent zero would pass every pin above; the denominator is checked."""

        for arm in ("combined_accounts", "repaired_clock"):
            assert len(list(_FIFTH_RUN.glob(f"{arm}-seed-*.jsonl"))) == 50


class TestTheDiagnosticsBlockIsLabelledAndNeverGates:
    """A labelled diagnostic: it says what it is, and nothing reads it."""

    def test_the_precision_is_refused_without_its_harm_counter(self) -> None:
        """PLANTED: the pairing the owner's decision 2 made a condition.

        The precision figure is the one that reads as an achievement. A payload
        that carries it and drops the crew-on-crew counter beside it is refused
        by name rather than reported half-told.
        """

        with pytest.raises(ValidationError) as refused:
            instrument.AuthoredBallotDiagnostics(
                crew_authored_ejects=81,
                crew_authored_naming_impostor=51,
                crew_authored_precision_p=0.013,
            )
        message = str(refused.value)
        assert "never reported without its harm counter" in message
        assert "crew_on_crew_authored_ejects" in message

    def test_a_block_carrying_both_halves_is_accepted(self) -> None:
        """The control: the same payload with the harm counter is a block."""

        block = instrument.AuthoredBallotDiagnostics(
            crew_authored_ejects=81,
            crew_authored_naming_impostor=51,
            crew_authored_precision_p=0.013,
            crew_on_crew_authored_ejects=30,
            units_with_crew_on_crew=27,
        )
        assert block.crew_on_crew_authored_ejects == 30

    def test_an_empty_block_claims_nothing_and_is_accepted(self) -> None:
        """A default block carries neither half, so it is not a half-told claim."""

        assert instrument.AuthoredBallotDiagnostics().crew_authored_ejects == 0

    def test_the_block_says_what_it_is_in_the_report(self) -> None:
        """The four statements the card requires of the report text."""

        note = instrument.AUTHORED_DIAGNOSTICS_NOTE
        assert "AUTHORING-CONDITIONED" in note
        assert "flatters whichever arm authors more" in note
        assert "NEVER a decision input" in note
        assert "never preregistered" in note
        assert "REGISTER" in note
        # And the block carries it, so a reader of the report meets it.
        assert instrument.AuthoredBallotDiagnostics().note == note

    def test_no_decision_reads_the_block(self) -> None:
        """PLANTED: no stop condition, no paired field, no decision branch.

        The three places a diagnostic could become an outcome, checked by name:
        the frozen rule texts the report publishes, the paired result's own
        fields, and the source of the function that computes the decision.
        """

        # ``ejections`` is left out of the prose scan below and only out of
        # that: it is an ordinary English word the frozen rules use for the
        # thing they DO judge, so its presence there says nothing about this
        # block. It is still checked against the paired result's fields.
        names = set(instrument.AuthoredBallotDiagnostics.model_fields) - {"note"}
        assert names.isdisjoint(instrument.PairedResult.model_fields)
        names -= {"ejections"}
        for rule in (
            instrument.STOP_RULE,
            instrument.DECISION_RULE,
            instrument.WRONGFUL_EJECTION_TRADEOFF,
            instrument.PRIMARY_OUTCOME_RUBRIC,
        ):
            for name in names:
                assert name not in rule
        deciding = inspect.getsource(instrument.paired_result)
        for symbol in (
            "authored_diagnostics",
            "authored_ballot_block",
            "AuthoredBallotCounts",
            "diagnostics",
        ):
            assert symbol not in deciding

    def test_the_block_reaches_the_report_beside_the_outcome(
        self, tmp_path: Path
    ) -> None:
        """A dry run's report carries one block per arm, with its note."""

        report = run_dry(
            output_dir=tmp_path / "run",
            units=_SMOKE_UNITS,
            limits=feasible_limits(),
            client=UsageReplayProvider(),
        )
        assert len(report.arms) == 2
        for arm in report.arms:
            assert arm.authored_diagnostics.note == instrument.AUTHORED_DIAGNOSTICS_NOTE
            assert [row.role for row in arm.authored_diagnostics.by_voter_role] == [
                "CREWMATE",
                "IMPOSTOR",
            ]
            for row in arm.authored_diagnostics.by_voter_role:
                assert row.authored == row.cleared + row.coerced

    def test_the_report_carries_no_prefix_bytes_with_the_block_on_it(
        self, tmp_path: Path
    ) -> None:
        """Counts only, so the report's own secrecy check passes over the block."""

        report = run_dry(
            output_dir=tmp_path / "run",
            units=_SMOKE_UNITS,
            limits=feasible_limits(),
            client=UsageReplayProvider(),
        )
        frozen = verify_frozen_set(_REPO_ROOT)
        instrument.assert_report_holds_no_prefix_bytes(
            report, frozen.prefixes[:_SMOKE_UNITS]
        )

    def test_the_block_is_projected_at_unit_close_not_at_report_time(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: a resumed run reports the totals the whole run reports.

        The earlier units of a resumed sitting exist only as checkpoint rows —
        there is no ``UnitRecord`` for them — so a block computed at report time
        from the in-memory records would report the TAIL's authored layer as the
        run's. The projection happens in ``unit_telemetry``, which is what the
        checkpoint carries, and this is the statement that makes the difference
        visible.
        """

        limits = feasible_limits()
        whole = run_dry(
            output_dir=tmp_path / "whole",
            units=4,
            limits=limits,
            client=UsageReplayProvider(),
        )
        checkpoint_path = tmp_path / "checkpoint.json"
        stopper = UsageReplayProvider(
            spoil_call=25,
            spoil_repeats=instrument.MAX_TRANSPORT_ATTEMPTS,
            mode="transport_error",
        )
        with pytest.raises(InstrumentAborted):
            run_dry(
                output_dir=tmp_path / "stopped",
                units=4,
                limits=limits,
                client=stopper,
                checkpoint_path=checkpoint_path,
            )
        checkpoint = instrument.read_checkpoint(checkpoint_path)
        assert len(checkpoint.completed_seeds) == 2
        # The checkpoint really does carry the authored layer of the units it
        # graded; without it the resume below would have nothing to sum.
        assert any(
            unit.telemetry.diagnostics != instrument.AuthoredBallotCounts()
            for unit in checkpoint.units
        )
        resumed = run_dry(
            output_dir=tmp_path / "resumed",
            units=4,
            limits=limits,
            client=UsageReplayProvider(seed=6),
            resume=checkpoint,
        )
        assert {arm.arm: arm.authored_diagnostics for arm in resumed.arms} == {
            arm.arm: arm.authored_diagnostics for arm in whole.arms
        }


class _LengthOnceProvider(DryRunProvider):
    """A dry-run provider that reports ``"length"`` on one call and ``"stop"`` after.

    The reading a completed RUN can never carry — the truncation gate stops on
    it — so the distribution is read off the partial accounting the stop
    reports, which is where a run's spend goes when it stops.
    """

    def __init__(self, *, at_call: int = 3) -> None:
        super().__init__()
        self._at_call = at_call
        self._calls = 0

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
        self._calls += 1
        if self._calls != self._at_call:
            return response
        return LLMResponse(
            text=response.text,
            usage=response.usage,
            cost_usd=response.cost_usd,
            model=response.model,
            finish_reason="length",
        )


class TestPerCallFinishReasonsReachTheRun:
    """`finish_reason` was recorded per call and folded away; now it is reported."""

    def _call(self, finish_reason: str | None) -> instrument.CapturedCall:
        return instrument.CapturedCall(
            agent_id="p-1",
            prompt="x",
            max_tokens=1024,
            input_tokens=10,
            output_tokens=5,
            cost_usd=0.0,
            model=AUTHORIZED_MODEL,
            seconds=0.1,
            finish_reason=finish_reason,
        )

    def test_an_absent_reading_is_keyed_null_rather_than_dropped(self) -> None:
        """ "The provider reported nothing" is a row, not a hole."""

        usage = instrument.ArmUsage().plus(
            [self._call("stop"), self._call(None), self._call("stop")]
        )
        assert usage.finish_reasons == {"null": 1, "stop": 2}
        assert sum(usage.finish_reasons.values()) == usage.calls

    def test_the_empty_distribution_compares_equal_across_instances(self) -> None:
        """PLANTED: `abandoned_spend` decides on `spend == ArmUsage()`.

        A default that did not compare equal — or a fold over NO calls that
        seeded a key — would make an arm that spent nothing look like an arm
        that spent something, and the checkpoint would carry an abandoned row
        for a pair nobody ran.
        """

        assert instrument.ArmUsage() == instrument.ArmUsage()
        assert instrument.ArmUsage().plus([]) == instrument.ArmUsage()
        assert instrument.ArmUsage().merged(instrument.ArmUsage()) == (
            instrument.ArmUsage()
        )
        assert (
            instrument.abandoned_spend(
                instrument.AbandonedSpend(),
                arms=["repaired_clock", "combined_accounts"],
                usage_by_arm={"repaired_clock": instrument.ArmUsage()},
                attempts_by_arm={},
                model_work_seconds=0.0,
            ).arms
            == ()
        )

    def test_two_tallies_of_one_arm_sum_their_readings(self) -> None:
        """A resumed sitting carries totals, not the calls they came from."""

        first = instrument.ArmUsage().plus([self._call("stop"), self._call("length")])
        second = instrument.ArmUsage().plus([self._call("stop")])
        assert first.merged(second).finish_reasons == {"length": 1, "stop": 2}

    def test_a_run_reports_both_readings_rather_than_one_aggregate(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: one `"length"` and `"stop"` otherwise, reported as two rows.

        `cap_signal_disagreements` collapses every reading to one integer, so a
        run whose provider said `"length"` once and a run whose provider said
        nothing at all were indistinguishable in the report. The stop this
        reading earns is unchanged — a truncation is still a stop — and its
        partial accounting now names what the provider said.
        """

        with pytest.raises(InstrumentAborted) as stopped:
            run_dry(
                output_dir=tmp_path / "run",
                units=_SMOKE_UNITS,
                limits=feasible_limits(),
                client=_LengthOnceProvider(at_call=3),
            )
        readings = {
            arm: dict(usage.finish_reasons)
            for arm, usage in stopped.value.partial.usage_by_arm.items()
        }
        assert readings == {"repaired_clock": {"length": 1, "stop": 2}}
        assert "finish_reason 'length'" in stopped.value.partial.reason

    def test_the_readings_of_an_abandoned_pair_survive_a_resume(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: the calls a stop abandoned are on no unit row.

        They are on the checkpoint's abandoned rows, and a resumed run charges
        them. Their readings ride with them, so a run stopped once reports what
        both sittings' providers said rather than what the tail's did.
        """

        limits = feasible_limits()
        checkpoint_path = tmp_path / "checkpoint.json"
        stopper = UsageReplayProvider(
            profile=stopped_runs_profile(),
            spoil_call=28,
            spoil_repeats=instrument.MAX_TRANSPORT_ATTEMPTS,
            mode="transport_error",
        )
        with pytest.raises(InstrumentAborted):
            run_dry(
                output_dir=tmp_path / "stopped",
                units=4,
                limits=limits,
                client=stopper,
                checkpoint_path=checkpoint_path,
            )
        checkpoint = instrument.read_checkpoint(checkpoint_path)
        abandoned = checkpoint.abandoned.usage_by_arm()
        assert abandoned, "a mid-unit stop abandoned no spend at all"
        for name, spend in abandoned.items():
            assert spend.finish_reasons, name
            assert sum(spend.finish_reasons.values()) == spend.calls
        resumed = run_dry(
            output_dir=tmp_path / "resumed",
            units=4,
            limits=limits,
            client=UsageReplayProvider(seed=6),
            resume=checkpoint,
        )
        for summary in resumed.arms:
            assert sum(summary.finish_reasons.values()) == summary.calls

    def test_a_dry_runs_report_carries_the_distribution_per_arm(
        self, tmp_path: Path
    ) -> None:
        """The field reaches the report, summing to the arm's own call count."""

        report = run_dry(
            output_dir=tmp_path / "run",
            units=_SMOKE_UNITS,
            limits=feasible_limits(),
            client=UsageReplayProvider(),
        )
        for arm in report.arms:
            assert arm.finish_reasons
            assert sum(arm.finish_reasons.values()) == arm.calls

    def test_a_carried_distribution_that_is_not_one_row_per_call_is_refused(
        self,
    ) -> None:
        """PLANTED: a checkpoint is a file, and a resumed run merges it whole.

        The contract is that a populated distribution counts calls. A row
        claiming three readings over two calls, or a negative reading, would
        otherwise cross into ``ArmUsage`` and be reported as a reading nobody
        saw, so both are refused at the boundary rather than downstream.
        """

        with pytest.raises(ValidationError, match="one row per call"):
            instrument.CarriedUsage(calls=2, finish_reasons={"stop": 3})
        with pytest.raises(ValidationError, match="negative"):
            instrument.CarriedUsage(calls=0, finish_reasons={"stop": 2, "length": -2})

    def test_an_empty_carried_distribution_stays_legal_at_any_call_count(
        self,
    ) -> None:
        """The legacy reading the refusal above may not take with it.

        A checkpoint written before the field carries calls and no reading at
        all, and the committed fifth run is exactly that record.
        """

        carried = instrument.CarriedUsage(calls=7)
        assert carried.finish_reasons == {}
        assert carried.arm_usage().calls == 7
        assert instrument.CarriedUsage(
            calls=2, finish_reasons={"stop": 1, "null": 1}
        ).arm_usage().finish_reasons == {"stop": 1, "null": 1}

    def test_records_written_before_this_card_read_empty(self) -> None:
        """PLANTED: an archive whose provider reading nobody recorded.

        The fifth run's committed report and checkpoint predate the field. They
        must parse through the current models and read an EMPTY distribution —
        "nothing was recorded" — rather than a fabricated `"stop"` on every
        call. The checkpoint payload version and the replay row are unchanged,
        so the archive is still the archive.
        """

        report = InstrumentReport.model_validate_json(
            (_FIFTH_RUN / "report.json").read_text(encoding="utf-8")
        )
        assert report.arms
        for arm in report.arms:
            assert arm.finish_reasons == {}
            assert arm.calls > 0
            # And the block this card adds beside it reads empty too.
            assert arm.authored_diagnostics.crew_authored_ejects == 0
        checkpoint = instrument.read_checkpoint(_FIFTH_RUN / "checkpoint-final.json")
        assert len(checkpoint.units) == 100
        for unit in checkpoint.units:
            assert unit.telemetry.usage.finish_reasons == {}
            assert unit.telemetry.diagnostics == instrument.AuthoredBallotCounts()
        assert instrument.CHECKPOINT_SCHEMA == "fresh-deduction-checkpoint/1"
        assert checkpoint.schema_version == instrument.CHECKPOINT_SCHEMA
        # The RECORDING path is untouched: the replay row still carries no
        # finish reason, so no committed replay's bytes move for this.
        assert "finish_reason" not in LLMCallRecord.model_fields


# ---------------------------------------------------------------------------
# The THIRD development calibration (tasks/work/fresh-deduction-calibration-3.md)
# ---------------------------------------------------------------------------

#: The card this section implements, read for the one table it and the manifest
#: both carry.
_CALIBRATION_3_CARD: Final[Path] = (
    _REPO_ROOT / "tasks" / "work" / "fresh-deduction-calibration-3.md"
)

#: The 2026-09-15 sitting's committed output. Its own published maxima are what
#: the 2026-09-18 mode's ceilings were sized against, and its ``caveat`` and
#: ``proposal.rule`` are what "byte-identical" is checked against — a committed
#: record rather than a second copy of the strings.
_CALIBRATION_2_ARCHIVE: Final[Path] = (
    _REPO_ROOT
    / "audits"
    / "deduction-candidate"
    / "calibration-2-2026-09-15"
    / "calibration.json"
)


def _calibration_2_published() -> dict[str, Any]:
    payload = json.loads(_CALIBRATION_2_ARCHIVE.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _third_mode() -> instrument.CalibrationMode:
    return instrument.calibration_mode_for(
        limits=instrument.CALIBRATION_3_LIMITS,
        sampling=instrument.CALIBRATION_3_SAMPLING,
        paired_seeds=instrument.CALIBRATION_3_PAIRED_SEEDS,
    )


def _calibration_3_report(
    tmp_path: Path, client: Any = None
) -> instrument.CalibrationReport:
    """One whole third-mode calibration at $0, on a $0 provider."""

    return instrument.run_calibration(
        output_dir=tmp_path / "units",
        client=client,
        limits=instrument.CALIBRATION_3_LIMITS,
        sampling=instrument.CALIBRATION_3_SAMPLING,
        paired_seeds=instrument.CALIBRATION_3_PAIRED_SEEDS,
    )


@pytest.fixture(scope="module")
def calibration_3_fake(
    tmp_path_factory: pytest.TempPathFactory,
) -> instrument.CalibrationReport:
    """One 120-unit rehearsal of the third mode, shared by the cases below."""

    return _calibration_3_report(tmp_path_factory.mktemp("calibration-3-fake"))


@pytest.fixture(scope="module")
def calibration_3_replayed(
    tmp_path_factory: pytest.TempPathFactory,
) -> instrument.CalibrationReport:
    """The same mode over the archived per-call counts, shared the same way."""

    return _calibration_3_report(
        tmp_path_factory.mktemp("calibration-3-replay"), client=UsageReplayProvider()
    )


def _arms_with_the_relevance_lever(
    *versions: int | None,
) -> Callable[[], tuple[Any, ...]]:
    """A stand-in ``instrument_arms`` whose arms carry these lever versions."""

    def _arms() -> tuple[Any, ...]:
        return tuple(
            instrument.InstrumentArm(
                name=arm.name,
                experiment_config=arm.experiment_config.model_copy(
                    update={"citation_relevance_version": version}
                ),
            )
            for arm, version in zip(instrument_arms(), versions)
        )

    return _arms


def _prediction_rows(text: str) -> list[tuple[str, ...]]:
    """Every ``| P<n> | ... |`` row of a markdown table, as four cells."""

    rows: list[tuple[str, ...]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not re.match(r"^\|\s*P\d+\s*\|", stripped):
            continue
        cells = tuple(cell.strip() for cell in stripped.strip("|").split("|"))
        assert len(cells) == 4, cells
        rows.append(cells)
    return rows


class TestTheThirdAuthorizedCalibrationMode:
    """A third set beside the two spent ones, and every crossing refused.

    The two earlier modes record spends that have been MADE, so their seeds,
    caps, ceilings and clauses are history. This one measures the revision of
    2026-09-18 on the second calibration's own sixty seeds, so the only thing
    that moved between the two sittings is the wave's prompt bytes.
    """

    def _invocation(self, root: Path) -> LiveRunInvocation:
        return LiveRunInvocation.naming(
            root / EXECUTION_MANIFEST_PATH,
            provider=AUTHORIZED_PROVIDER,
            model=AUTHORIZED_MODEL,
            repo_root=root,
        )

    def test_the_third_set_is_the_cards_constraints_table(self) -> None:
        """The values the owner's merge authorizes, as one object."""

        assert instrument.CALIBRATION_3_PAIRED_SEEDS == 60
        assert instrument.CALIBRATION_3_LIMITS == RunLimits(
            run_max_input_tokens=4_700_000,
            run_max_output_tokens=520_000,
            unit_max_input_tokens=116_000,
            unit_max_output_tokens=16_000,
            max_cost_usd=0.0,
            elapsed_seconds=6 * 60 * 60,
            model_work_seconds=5 * 60 * 60,
        )
        # The point of the mode: it draws the way the sixth run would, which is
        # the way calibration 2 drew, so the two compare on identical inputs.
        assert instrument.CALIBRATION_3_SAMPLING == AUTHORIZED_SAMPLING
        assert instrument.CALIBRATION_3_SAMPLING.turn_max_tokens == 4_096
        assert instrument.CALIBRATION_3_SAMPLING.vote_max_tokens == 1_024
        # The three this calibration does NOT re-size.
        assert instrument.MAX_TRANSPORT_ATTEMPTS == 4
        assert instrument.PER_ATTEMPT_TIMEOUT_SECONDS == 180.0
        assert instrument.CALIBRATION_3_LIMITS.max_cost_usd == (
            instrument.AUTHORIZED_MAX_COST_USD
        )

    def test_the_two_spent_sets_are_untouched_by_the_third(self) -> None:
        """Neither spent authorization moves, on any axis."""

        assert instrument.CALIBRATION_PAIRED_SEEDS == 5
        assert instrument.CALIBRATION_SAMPLING.turn_max_tokens == 2_048
        assert instrument.CALIBRATION_LIMITS.unit_max_output_tokens == 12_000
        assert instrument.CALIBRATION_2_LIMITS == RunLimits(
            run_max_input_tokens=4_500_000,
            run_max_output_tokens=450_000,
            unit_max_input_tokens=60_000,
            unit_max_output_tokens=16_000,
            max_cost_usd=0.0,
            elapsed_seconds=6 * 60 * 60,
            model_work_seconds=5 * 60 * 60,
        )
        assert instrument.CALIBRATION_CLAUSE != instrument.CALIBRATION_3_CLAUSE
        assert instrument.CALIBRATION_2_CLAUSE != instrument.CALIBRATION_3_CLAUSE
        limits = {mode.limits for mode in instrument.CALIBRATION_MODES}
        assert len(limits) == len(instrument.CALIBRATION_MODES)

    def test_each_of_the_three_modes_is_accepted_whole(self) -> None:
        """All three authorized sets pass, live, against the committed manifest."""

        assert [mode.name for mode in instrument.CALIBRATION_MODES] == [
            "2026-09-14",
            "2026-09-15",
            "2026-09-18",
        ]
        for mode in instrument.CALIBRATION_MODES:
            matched = instrument.assert_calibration_is_authorized(
                provider=AUTHORIZED_PROVIDER,
                invocation=self._invocation(_REPO_ROOT),
                limits=mode.limits,
                sampling=mode.sampling,
                paired_seeds=mode.paired_seeds,
            )
            assert matched is mode

    def test_every_crossing_of_the_three_modes_is_refused(self) -> None:
        """PLANTED each way: the whole 3x3x3 product, not three hand-picked rows.

        Three modes make 27 orderings of (limits, sampling, seed count) taken one
        field at a time from each. Exactly three of them are an authorized mode;
        every other is a spend nobody approved — the 2026-09-15 draw under the
        2026-09-18 ceilings is a larger spend than the one authorized for it, the
        2026-09-18 draw under the 2026-09-15 ceilings cannot pay for the prompt
        bytes the wave adds, and anything at the 2026-09-14 caps measures a
        distribution the run it sizes does not draw from. Enumerated rather than
        sampled, because the review of 2026-09-15 found the shape three
        hand-written plants had left open.
        """

        modes = instrument.CALIBRATION_MODES
        authorized = {(mode.limits, mode.sampling, mode.paired_seeds) for mode in modes}
        accepted: list[str] = []
        for limits, sampling, seeds in itertools.product(
            [mode.limits for mode in modes],
            [mode.sampling for mode in modes],
            [mode.paired_seeds for mode in modes],
        ):
            if (limits, sampling, seeds) in authorized:
                matched = instrument.calibration_mode_for(
                    limits=limits, sampling=sampling, paired_seeds=seeds
                )
                accepted.append(matched.name)
                continue
            with pytest.raises(LiveRunNotAuthorized, match="cross"):
                instrument.calibration_mode_for(
                    limits=limits, sampling=sampling, paired_seeds=seeds
                )
        assert sorted(set(accepted)) == ["2026-09-14", "2026-09-15", "2026-09-18"]

    def test_the_crossing_refusal_reaches_the_live_capable_gate(self) -> None:
        """PLANTED on the paths that can SPEND, not only on the helper.

        A refusal only `calibration_mode_for` made would leave an authorized
        sitting spending under ceilings nobody sized for it.
        """

        with pytest.raises(LiveRunNotAuthorized, match="cross"):
            instrument.assert_calibration_is_authorized(
                provider=AUTHORIZED_PROVIDER,
                invocation=self._invocation(_REPO_ROOT),
                limits=instrument.CALIBRATION_3_LIMITS,
                sampling=instrument.CALIBRATION_SAMPLING,
                paired_seeds=instrument.CALIBRATION_3_PAIRED_SEEDS,
            )
        with pytest.raises(LiveRunNotAuthorized, match="cross"):
            instrument.assert_ready_for_a_calibration(
                provider="fake",
                invocation=None,
                limits=instrument.CALIBRATION_2_LIMITS,
                sampling=instrument.CALIBRATION_3_SAMPLING,
                paired_seeds=instrument.CALIBRATION_PAIRED_SEEDS,
            )

    def test_the_committed_manifest_authorizes_the_third_calibration(self) -> None:
        """The settled state: the third clause is in the document the gate reads."""

        text = _MANIFEST.read_text(encoding="utf-8")
        assert instrument.CALIBRATION_3_CLAUSE in text
        assert "## Development calibration 3 (2026-09-18)" in text
        # And no earlier dated section was edited into it.
        assert instrument.CALIBRATION_CLAUSE in text
        assert instrument.CALIBRATION_2_CLAUSE in text

    def test_a_manifest_without_the_third_clause_refuses_it(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: the committed document with the third sentence removed.

        Each mode's clause authorizes that mode's spend and no other, so a
        manifest carrying only the two earlier ones authorizes only those.
        """

        root = _root_without_the_clause_binding_the_live_band(
            tmp_path, instrument.CALIBRATION_3_CLAUSE
        )
        text = (root / EXECUTION_MANIFEST_PATH).read_text(encoding="utf-8")
        assert instrument.CALIBRATION_2_CLAUSE in text
        with pytest.raises(LiveRunNotAuthorized, match="no calibration clause"):
            instrument.assert_calibration_is_authorized(
                provider=AUTHORIZED_PROVIDER,
                invocation=self._invocation(root),
                limits=instrument.CALIBRATION_3_LIMITS,
                sampling=instrument.CALIBRATION_3_SAMPLING,
                paired_seeds=instrument.CALIBRATION_3_PAIRED_SEEDS,
                repo_root=root,
            )


class TestTheThirdModeIsSizedOnItsOwnProfile:
    """Acceptance item 3: the feasibility gate bites on this mode's numbers."""

    def test_the_sizing_pair_is_a_field_of_each_mode(self) -> None:
        """Two spent modes on the stopped runs' archives, this one on its own."""

        first, second, third = instrument.CALIBRATION_MODES
        for spent in (first, second):
            assert spent.sizing_unit_input_tokens == (
                instrument.CALIBRATION_SIZING_UNIT_INPUT_TOKENS
            )
            assert spent.sizing_unit_output_tokens == (
                instrument.CALIBRATION_SIZING_UNIT_OUTPUT_TOKENS
            )
        assert third.sizing_unit_input_tokens == 38_440
        assert third.sizing_unit_output_tokens == 4_176

    def test_the_sizing_pair_is_the_second_sittings_published_maxima(self) -> None:
        """Read off committed evidence rather than typed.

        The 2026-09-15 sitting's own output publishes the largest of its 120
        units, and that record does not move: it is what a spend measured, not a
        constant a later card may refresh.
        """

        proposal = _calibration_2_published()["proposal"]
        assert (
            instrument.CALIBRATION_3_SIZING_UNIT_INPUT_TOKENS
            == (proposal["measured_max_unit_input_tokens"])
        )
        assert (
            instrument.CALIBRATION_3_SIZING_UNIT_OUTPUT_TOKENS
            == (proposal["measured_max_unit_output_tokens"])
        )

    def test_the_gate_accepts_the_constraints_table_for_120_units(self) -> None:
        """The arithmetic of the Constraints table, against the shipped gate."""

        units = instrument.calibration_units(instrument.CALIBRATION_3_PAIRED_SEEDS)
        assert units == 120
        mode = _third_mode()
        instrument.assert_limits_are_feasible(
            limits=mode.limits,
            sampling=mode.sampling,
            units=units,
            calibrated_unit_input_tokens=mode.sizing_unit_input_tokens,
            calibrated_unit_output_tokens=mode.sizing_unit_output_tokens,
        )
        assert instrument.unit_output_reservation(sampling=mode.sampling) == 15_360
        assert mode.limits.unit_max_output_tokens == 16_000
        assert mode.sizing_unit_input_tokens * units == 4_612_800
        assert (
            mode.sizing_unit_output_tokens * units + mode.sampling.turn_max_tokens
            == 505_216
        )
        assert mode.limits.run_max_input_tokens == 4_700_000
        assert mode.limits.run_max_output_tokens == 520_000

    def test_a_run_input_ceiling_below_the_floor_is_refused_here(self) -> None:
        """PLANTED: 4,600,000 against 120 units of 38,440.

        The same four numbers pass against the profile the two SPENT modes were
        sized on — 120 units of 24,282 is 2,913,840 — which is the whole reason
        the sizing pair is a field of the mode rather than one constant for all
        of them. A gate reading the spent modes' profile would authorize a
        sitting whose ceiling cannot pay for its own units.
        """

        mode = _third_mode()
        units = instrument.calibration_units(mode.paired_seeds)
        planted = mode.limits.model_copy(update={"run_max_input_tokens": 4_600_000})
        with pytest.raises(instrument.LimitsInfeasible, match="run-level input"):
            instrument.assert_limits_are_feasible(
                limits=planted,
                sampling=mode.sampling,
                units=units,
                calibrated_unit_input_tokens=mode.sizing_unit_input_tokens,
                calibrated_unit_output_tokens=mode.sizing_unit_output_tokens,
            )
        instrument.assert_limits_are_feasible(
            limits=planted,
            sampling=mode.sampling,
            units=units,
            calibrated_unit_input_tokens=(
                instrument.CALIBRATION_SIZING_UNIT_INPUT_TOKENS
            ),
            calibrated_unit_output_tokens=(
                instrument.CALIBRATION_SIZING_UNIT_OUTPUT_TOKENS
            ),
        )

    def test_a_refreshed_committed_profile_does_not_move_this_modes_gate(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """PERTURBED: the committed profile moved to a figure this mode fails.

        `tasks/work/fresh-deduction-limits-6.md` refreshes the two calibrated
        constants FROM this sitting. A mode whose gate read them would then be
        checked against the measurement it produced, which is the circularity the
        sizing field exists to refuse. The gate that reads the module constants
        refuses these limits under the perturbation; the mode's own gate does
        not move, and the live-capable pre-flight still accepts the sitting.
        """

        monkeypatch.setattr(instrument, "CALIBRATED_UNIT_INPUT_TOKENS", 90_000)
        mode = _third_mode()
        units = instrument.calibration_units(mode.paired_seeds)
        with pytest.raises(instrument.LimitsInfeasible, match="run-level input"):
            instrument.assert_limits_are_feasible(
                limits=mode.limits, sampling=mode.sampling, units=units
            )
        instrument.assert_limits_are_feasible(
            limits=mode.limits,
            sampling=mode.sampling,
            units=units,
            calibrated_unit_input_tokens=mode.sizing_unit_input_tokens,
            calibrated_unit_output_tokens=mode.sizing_unit_output_tokens,
        )
        instrument.assert_ready_for_a_calibration(
            provider="fake",
            invocation=None,
            limits=mode.limits,
            sampling=mode.sampling,
            paired_seeds=mode.paired_seeds,
        )


class TestTheThirdModesDraw:
    """Acceptance item 2: the shipped prefix draw, named and unchanged."""

    def test_the_draw_is_calibration_2s_draw_to_the_seed(self) -> None:
        """All fifty of the 3000 record, then 5000 to 5009 of the next."""

        draw = instrument.verify_calibration_draw(
            paired_seeds=instrument.CALIBRATION_3_PAIRED_SEEDS
        )
        assert draw.paired_seeds == 60
        assert [len(drawn.prefixes) for drawn in draw.sets] == [50, 10]
        assert [drawn.band.first_seed for drawn in draw.sets] == [3000, 5000]
        assert list(draw.seeds) == sorted(draw.seeds)
        assert list(draw.seeds)[50:] == list(range(5000, 5010))
        assert (
            draw.seeds
            == instrument.verify_calibration_draw(
                paired_seeds=instrument.CALIBRATION_2_PAIRED_SEEDS
            ).seeds
        )
        # Every prefix rebuilt and held to the digest its own record froze.
        for drawn, converted in zip(draw.sets, CONVERTED_BANDS):
            assert drawn.record_path == (_REPO_ROOT / converted.manifest_path).resolve()
            assert len(drawn.digests) == len(drawn.prefixes)
            for prefix, digest in zip(drawn.prefixes, drawn.digests):
                assert prefix_sha256(prefix) == digest

    def test_a_sixth_converted_band_does_not_move_the_draw(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The sixth freeze lands after this sitting and cannot reach into it.

        A PREFIX draw bound at sixty stops inside the second record, so a band
        APPENDED to `CONVERTED_BANDS` is never opened — which is what says this
        sitting's seeds do not move when band 8000-8999 is flipped and added.
        The appended record deliberately does not exist on disk: reaching it
        would be a file read, and this draw makes none.
        """

        appended = CONVERTED_BANDS + (
            ConvertedBand(
                band=SeedBand(first_seed=8000, last_seed=8999, size=50),
                manifest_path=(
                    "audits/deduction-candidate/held-out/manifest-band-8000-8999.json"
                ),
            ),
        )
        before = instrument.verify_calibration_draw(
            paired_seeds=instrument.CALIBRATION_3_PAIRED_SEEDS
        ).seeds
        monkeypatch.setattr(instrument, "CONVERTED_BANDS", appended)
        after = instrument.verify_calibration_draw(
            paired_seeds=instrument.CALIBRATION_3_PAIRED_SEEDS
        )
        assert after.seeds == before
        assert [drawn.band.first_seed for drawn in after.sets] == [3000, 5000]
        assert not (_REPO_ROOT / appended[-1].manifest_path).exists(), (
            "the appended record must not be read, so it must not exist"
        )

    def test_the_held_out_record_is_refused_by_name_at_this_seed_count(self) -> None:
        """PLANTED: the live freeze named among this draw's records."""

        with pytest.raises(
            instrument.CalibrationInputsRejected, match="HELD-OUT"
        ) as refused:
            instrument.verify_calibration_draw(
                records=[_REPO_ROOT / MANIFEST_PATH],
                paired_seeds=instrument.CALIBRATION_3_PAIRED_SEEDS,
            )
        assert str(MANIFEST_PATH) in str(refused.value)

    def test_the_held_out_record_is_refused_on_the_live_capable_path(
        self, tmp_path: Path
    ) -> None:
        """PLANTED on the two callers that can SPEND, in this mode's shape."""

        mode = _third_mode()
        with pytest.raises(instrument.CalibrationInputsRejected, match="HELD-OUT"):
            instrument.assert_ready_for_a_calibration(
                provider="fake",
                invocation=None,
                records=[_REPO_ROOT / MANIFEST_PATH],
                limits=mode.limits,
                sampling=mode.sampling,
                paired_seeds=mode.paired_seeds,
            )
        with pytest.raises(instrument.CalibrationInputsRejected, match="HELD-OUT"):
            instrument.run_calibration(
                output_dir=tmp_path / "units",
                records=[_REPO_ROOT / MANIFEST_PATH],
                limits=mode.limits,
                sampling=mode.sampling,
                paired_seeds=mode.paired_seeds,
            )

    def test_a_record_named_twice_is_refused_at_this_seed_count(self) -> None:
        """PLANTED: sixty seeds filled out of fifty distinct prefixes."""

        with pytest.raises(instrument.CalibrationInputsRejected, match="twice"):
            instrument.verify_calibration_draw(
                records=[_converted_record(), _converted_record()],
                paired_seeds=instrument.CALIBRATION_3_PAIRED_SEEDS,
            )

    def test_a_status_that_is_not_development_stops_this_draw(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: the second record of the draw flipped back to held out."""

        root = _root_with_both_converted_records(tmp_path)
        second = root / CONVERTED_BANDS[1].manifest_path
        payload = json.loads(second.read_text(encoding="utf-8"))
        payload["status"] = "held_out"
        second.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(
            instrument.CalibrationInputsRejected, match="not 'development'"
        ):
            instrument.verify_calibration_draw(
                repo_root=root, paired_seeds=instrument.CALIBRATION_3_PAIRED_SEEDS
            )

    def test_a_moved_prefix_digest_stops_this_draw_by_seed(
        self, tmp_path: Path
    ) -> None:
        """PLANTED: one accepted digest edited in the record the draw spills into."""

        root = _root_with_both_converted_records(tmp_path)
        second = root / CONVERTED_BANDS[1].manifest_path
        payload = json.loads(second.read_text(encoding="utf-8"))
        payload["accepted"] = [dict(row) for row in payload["accepted"]]
        moved = payload["accepted"][2]["seed"]
        payload["accepted"][2]["sha256"] = "1" * 64
        second.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(instrument.CalibrationInputsRejected) as refused:
            instrument.verify_calibration_draw(
                repo_root=root, paired_seeds=instrument.CALIBRATION_3_PAIRED_SEEDS
            )
        assert f"seed {moved}" in str(refused.value)

    def test_a_draw_of_fifty_nine_is_not_this_authorization(self) -> None:
        """PLANTED: the seed COUNT is load-bearing, not decorative.

        Fifty-nine verifies clean and draws a different set — one seed short at
        the far end — and it is not a mode: `calibration_mode_for` refuses it, so
        a sitting cannot quietly shorten the draw and keep the clause.
        """

        short = instrument.verify_calibration_draw(paired_seeds=59)
        full = instrument.verify_calibration_draw(
            paired_seeds=instrument.CALIBRATION_3_PAIRED_SEEDS
        )
        assert short.seeds == full.seeds[:59]
        assert short.seeds != full.seeds
        with pytest.raises(LiveRunNotAuthorized, match="paired seeds"):
            instrument.calibration_mode_for(
                limits=instrument.CALIBRATION_3_LIMITS,
                sampling=instrument.CALIBRATION_3_SAMPLING,
                paired_seeds=59,
            )


class TestTheRevisedWaveIsRequiredByTheThirdMode:
    """Acceptance item 4: both arms carry the revision, or nothing runs."""

    def test_the_committed_arms_resolve_the_lever_on(self) -> None:
        """The settled state, read through the reader the gate reads through."""

        for arm in instrument_arms():
            resolved = instrument.arm_lever_profile(arm)
            assert resolved["AILIBI_CITATION_RELEVANCE"] == "1"
            assert resolved["AILIBI_PROMPT_SET"] == AUTHORIZED_PROMPT_SET
            assert "AILIBI_LLM_PROVIDER" not in resolved
        instrument.assert_the_revised_wave_is_enabled(_third_mode())

    @pytest.mark.parametrize(
        "versions",
        [(None, 1), (1, None), (None, None)],
        ids=["reference-off", "candidate-off", "both-off"],
    )
    def test_the_mode_is_refused_with_the_guard_off_on_either_arm(
        self, monkeypatch: pytest.MonkeyPatch, versions: tuple[int | None, int | None]
    ) -> None:
        """PLANTED each way: the lever resolved OFF, before a client exists.

        A sitting of this mode with the relevance rule off measures the surface
        the revision replaced, under a clause that authorized the other one. The
        refusal is on the helper and on the live-capable pre-flight, the latter
        with the fake provider, so no credential is reached in either.
        """

        monkeypatch.setattr(
            instrument, "instrument_arms", _arms_with_the_relevance_lever(*versions)
        )
        mode = _third_mode()
        with pytest.raises(LiveRunNotAuthorized, match="AILIBI_CITATION_RELEVANCE"):
            instrument.assert_the_revised_wave_is_enabled(mode)
        with pytest.raises(LiveRunNotAuthorized, match="revision of 2026-09-18"):
            instrument.assert_ready_for_a_calibration(
                provider="fake",
                invocation=None,
                limits=mode.limits,
                sampling=mode.sampling,
                paired_seeds=mode.paired_seeds,
            )

    def test_the_run_path_is_refused_too(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """PLANTED on the entry point that would spend: `run_calibration`."""

        monkeypatch.setattr(
            instrument, "instrument_arms", _arms_with_the_relevance_lever(1, None)
        )
        mode = _third_mode()
        with pytest.raises(LiveRunNotAuthorized, match="AILIBI_CITATION_RELEVANCE"):
            instrument.run_calibration(
                output_dir=tmp_path / "units",
                limits=mode.limits,
                sampling=mode.sampling,
                paired_seeds=mode.paired_seeds,
            )

    def test_the_two_spent_modes_are_not_held_to_a_later_lever(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The spent sittings measured the surface they were run on.

        Holding them to a lever that did not exist on their day would refuse a
        spend the manifest already records, which is the wrong direction for a
        gate over history to err in.
        """

        monkeypatch.setattr(
            instrument, "instrument_arms", _arms_with_the_relevance_lever(None, None)
        )
        for mode in instrument.CALIBRATION_MODES[:2]:
            assert mode.requires_the_revised_wave is False
            instrument.assert_the_revised_wave_is_enabled(mode)


class TestTheThirdModesCaveatAndOutcomeGuard:
    """Acceptance items 5 and 6: what it says it is, and what it may not carry."""

    def test_the_spent_caveat_is_byte_identical_to_what_was_published(self) -> None:
        """The spent sitting's own output is the comparison, not a copy."""

        assert instrument.CALIBRATION_CAVEAT == _calibration_2_published()["caveat"]
        assert (
            instrument.CALIBRATION_CAVEATS["2026-09-14"]
            is instrument.CALIBRATION_CAVEAT
        )
        assert (
            instrument.CALIBRATION_CAVEATS["2026-09-15"]
            is instrument.CALIBRATION_CAVEAT
        )

    def test_the_third_mode_publishes_its_own_caveat(self) -> None:
        """It says what it reports and what it does not, and they differ."""

        caveat = instrument.CALIBRATION_CAVEATS["2026-09-18"]
        assert caveat is instrument.CALIBRATION_3_CAVEAT
        assert caveat != instrument.CALIBRATION_CAVEAT
        for stated in (
            "no grader ran",
            "no paired statistic",
            "no decision rule",
            "no primary outcome",
            "authored-ballot and ejection",
            "never per seed",
        ):
            assert stated in caveat, stated

    def test_every_mode_has_a_caveat(self) -> None:
        """A fourth mode cannot silently inherit a third one's statement."""

        assert set(instrument.CALIBRATION_CAVEATS) == {
            mode.name for mode in instrument.CALIBRATION_MODES
        }

    def test_the_third_modes_block_publishes_its_own_note(self) -> None:
        """Review correction, round 1: not the live evaluation's paragraph.

        The live note tells its reader the counts are reported BESIDE THE
        PRIMARY OUTCOME and that a cross-arm reading waits on the v5 prompt
        set. This payload reports no primary outcome and both its arms render
        v5, so it says neither — while the half that makes the block safe to
        read is carried over word for word.
        """

        note = instrument.CALIBRATION_DIAGNOSTICS_NOTES["2026-09-18"]
        assert note is instrument.CALIBRATION_3_AUTHORED_DIAGNOSTICS_NOTE
        assert note != instrument.AUTHORED_DIAGNOSTICS_NOTE
        for dropped in (
            "reported beside the primary outcome",
            "until the v5 prompt set",
        ):
            assert dropped in instrument.AUTHORED_DIAGNOSTICS_NOTE, dropped
            assert dropped not in note, dropped
        for kept in (
            "AUTHORING-CONDITIONED",
            "flatters whichever arm authors more",
            "NEVER a decision input",
            "never preregistered",
            "ONLY beside its harm counter",
            "illegal-target",
        ):
            assert kept in note, kept
        for stated in (
            "no primary outcome is reported",
            "no paired statistic was computed",
            "no decision rule was evaluated",
            "none of those is a gate",
        ):
            assert stated in note, stated

    def test_every_mode_that_reports_the_block_has_its_own_note(self) -> None:
        """The shipped table names exactly the modes that publish one."""

        instrument.assert_every_reporting_mode_has_its_note(
            instrument.CALIBRATION_DIAGNOSTICS_NOTES
        )
        assert set(instrument.CALIBRATION_DIAGNOSTICS_NOTES) == {
            mode.name
            for mode in instrument.CALIBRATION_MODES
            if mode.reports_authored_diagnostics
        }

    @pytest.mark.parametrize(
        "planted",
        [
            {},
            {"2026-09-15": "a note for a mode that reports no block"},
            {
                "2026-09-18": "a note",
                "2026-09-14": "another",
            },
        ],
        ids=["no-note-at-all", "a-mode-that-reports-none", "an-extra-mode"],
    )
    def test_a_note_table_that_does_not_match_the_modes_is_refused(
        self, planted: dict[str, str]
    ) -> None:
        """PLANTED: the failure is a fourth mode inheriting somebody's note.

        Without the entry, a mode that switched `reports_authored_diagnostics`
        on would fall through to the block's default, which is the live
        evaluation's note.
        """

        with pytest.raises(instrument.InstrumentError, match="its OWN note"):
            instrument.assert_every_reporting_mode_has_its_note(planted)

    def test_a_calibration_may_not_publish_the_live_runs_note(self) -> None:
        """PLANTED: the table pointed at the paragraph it exists to avoid."""

        with pytest.raises(instrument.InstrumentError, match="live evaluation's note"):
            instrument.assert_every_reporting_mode_has_its_note(
                {"2026-09-18": instrument.AUTHORED_DIAGNOSTICS_NOTE}
            )

    @pytest.mark.parametrize(
        "planted",
        [
            {"paired": {"b": 3, "c": 1}},
            {"supported_correct_ejection": 2},
            {"decision_rule": "adopt"},
        ],
        ids=["paired-block", "primary-outcome-field", "decision-rule"],
    )
    def test_a_payload_carrying_an_outcome_is_refused(
        self, planted: dict[str, Any]
    ) -> None:
        """PLANTED three ways: an evaluation wearing a calibration's schema.

        The guard runs over the PAYLOAD rather than over the constructed model,
        because the payload is what a reader, the refresh path and a later card
        re-reading a committed archive actually hold.
        """

        payload: dict[str, Any] = {"mode": "2026-09-18", "arms": [dict(planted)]}
        with pytest.raises(
            instrument.CalibrationReportsAnOutcome, match="no outcome"
        ) as refused:
            instrument.assert_calibration_reports_no_outcome(payload)
        assert next(iter(planted)) in str(refused.value)

    def test_the_prose_that_promises_no_outcome_is_not_itself_refused(self) -> None:
        """PERTURBED: the caveat says "no primary outcome" in those words.

        A guard that searched VALUES would refuse the sentence that makes the
        promise, so it searches keys. Both caveats are scanned here, because a
        rule that only held for the mode it was written for is a rule that has
        already started to drift.
        """

        for caveat in set(instrument.CALIBRATION_CAVEATS.values()):
            instrument.assert_calibration_reports_no_outcome({"caveat": caveat})
        for note in (
            instrument.AUTHORED_DIAGNOSTICS_NOTE,
            *instrument.CALIBRATION_DIAGNOSTICS_NOTES.values(),
        ):
            instrument.assert_calibration_reports_no_outcome({"note": note})

    def test_the_live_evaluation_still_stops_on_a_truncation(self) -> None:
        """PLANTED: the relaxation is the calibration's and reaches no run.

        `STOP_RULE` is unedited and the evaluation's own harness builds a client
        that raises `PerCallCapExceeded` on a capped completion, in this mode's
        presence exactly as before it.
        """

        assert "a truncation is a stop, not a datum" in STOP_RULE
        harness = instrument._build_harness(
            client=DryRunProvider(),
            limits=AUTHORIZED_LIMITS,
            sampling=AUTHORIZED_SAMPLING,
            invocation=None,
        )
        assert harness.client._truncation_is_a_measurement is False
        stop = instrument._InstrumentClient(
            DryRunProvider(),
            work_clock=instrument._ModelWorkClock(max_seconds=60.0),
            turn_max_tokens=AUTHORIZED_SAMPLING.turn_max_tokens,
            vote_max_tokens=AUTHORIZED_SAMPLING.vote_max_tokens,
            expected_model="the-authorized-model",
        )._unusable_response(
            model="the-authorized-model",
            output_tokens=1_024,
            max_tokens=1_024,
            finish_reason="length",
        )
        assert isinstance(stop, PerCallCapExceeded)
        # And this mode counts it instead.
        assert _third_mode().truncation_is_a_measurement is True


class TestTheThirdCalibrationEndToEnd:
    """The mode at $0, twice, and what its report carries."""

    def test_the_fake_provider_runs_the_whole_mode(
        self, calibration_3_fake: instrument.CalibrationReport
    ) -> None:
        """120 units, 720 completions, both arms, $0.00."""

        report = calibration_3_fake
        assert report.mode == "2026-09-18"
        assert report.units == 120
        assert report.paired_seeds == 60
        assert report.limits == instrument.CALIBRATION_3_LIMITS
        assert report.sampling == instrument.CALIBRATION_3_SAMPLING
        assert report.dry_run is True
        assert report.total_cost_usd == 0.0
        assert len(report.calls) == 720
        assert len(report.unit_usage) == 120
        assert [arm.units for arm in report.arms] == [60, 60]
        assert report.caveat == instrument.CALIBRATION_3_CAVEAT

    def test_the_replay_double_runs_the_mode_on_measured_usage(
        self, calibration_3_replayed: instrument.CalibrationReport
    ) -> None:
        """The same mode over the archived per-call counts, still at $0."""

        report = calibration_3_replayed
        assert report.units == 120
        assert report.total_cost_usd == 0.0
        assert report.proposal.measured_max_unit_output_tokens > 0
        assert report.proposal.clears_the_feasibility_gate is True

    def test_the_inputs_block_names_every_record_and_its_seeds(
        self, calibration_3_fake: instrument.CalibrationReport
    ) -> None:
        """Which records were spent, with the digest each of them froze."""

        report = calibration_3_fake
        assert [row.record for row in report.input_records] == [
            CONVERTED_BANDS[0].manifest_path,
            CONVERTED_BANDS[1].manifest_path,
        ]
        assert [len(row.seeds) for row in report.input_records] == [50, 10]
        assert report.inputs == report.input_records[0]
        for row in report.input_records:
            assert row.status == "development"
            assert len(row.record_sha256) == 64

    def test_the_profile_and_the_leak_column_are_reported(
        self, calibration_3_fake: instrument.CalibrationReport
    ) -> None:
        """Calibration 2's own shape, unchanged, on this mode's sitting."""

        report = calibration_3_fake
        assert instrument.ROLE_LEAK_RULE in report.role_leak_rule
        for arm in report.arms:
            assert {row.call_type for row in arm.by_call_type} == {"turn", "ballot"}
            assert {(row.call_type, row.role) for row in arm.by_role} == {
                ("turn", "CREWMATE"),
                ("turn", "IMPOSTOR"),
                ("ballot", "CREWMATE"),
                ("ballot", "IMPOSTOR"),
            }
            for row in arm.by_role:
                assert row.draws > 0
                assert row.truncations >= 0
                assert isinstance(row.truncations_by_finish_reason, Mapping)
            assert arm.leaking_turns >= 0
            assert arm.units_with_a_leaking_turn >= 0

    def test_the_diagnostics_block_is_reported_per_arm(
        self, calibration_3_fake: instrument.CalibrationReport
    ) -> None:
        """Every column the card names, summed over the arm's sixty units.

        The precision beside its harm counter (the block's own validator refuses
        one without the other), the illegal-target column, the coalition funnel
        with cleared and converted apart, gate survival by voter role, guard
        rewrites by reason including the guard card's new one, and ejections by
        role-correctness.
        """

        report = calibration_3_fake
        for arm in report.arms:
            block = arm.authored_diagnostics
            assert block is not None
            assert block.note == instrument.CALIBRATION_3_AUTHORED_DIAGNOSTICS_NOTE
            assert [row.role for row in block.by_voter_role] == ["CREWMATE", "IMPOSTOR"]
            for row in block.by_voter_role:
                assert row.authored == row.cleared + row.coerced
                assert row.illegal_targets >= 0
            assert block.crew_authored_naming_impostor <= block.crew_authored_ejects
            assert block.crew_on_crew_authored_ejects >= 0
            assert block.units_with_crew_on_crew >= 0
            assert block.correct_coalitions_cleared <= block.correct_coalitions
            assert block.correct_coalitions_converted <= block.correct_coalitions
            assert block.wrongful_coalitions_cleared <= block.wrongful_coalitions
            assert block.wrongful_coalitions_converted <= block.wrongful_coalitions
            assert block.role_correct_ejections <= block.ejections
            assert block.crew_authored_role_correct_ejections <= block.ejections
            assert set(block.guard_rewrites_by_reason) == set(
                instrument.BALLOT_REWRITE_REASONS
            )
            assert "off_target_coerced" in block.guard_rewrites_by_reason
        assert sum(arm.units for arm in report.arms) == 120

    def test_the_published_block_is_not_the_live_runs_note(
        self, calibration_3_fake: instrument.CalibrationReport
    ) -> None:
        """Review correction, round 1: over the PAYLOAD a reader holds.

        The mode-3 artifact's own bytes, not the constructed model: the block
        each arm publishes carries this mode's note, and the live evaluation's
        paragraph — with its "beside the primary outcome" and its v5 confound —
        appears nowhere in the file.
        """

        payload = json.loads(calibration_3_fake.model_dump_json())
        notes = {row["authored_diagnostics"]["note"] for row in payload["arms"]}
        assert notes == {instrument.CALIBRATION_3_AUTHORED_DIAGNOSTICS_NOTE}
        encoded = json.dumps(payload)
        assert instrument.AUTHORED_DIAGNOSTICS_NOTE not in encoded
        for dropped in (
            "reported beside the primary outcome",
            "until the v5 prompt set",
        ):
            assert dropped not in encoded, dropped
        assert payload["caveat"] == instrument.CALIBRATION_3_CAVEAT

    def test_each_arms_resolved_levers_are_published(
        self, calibration_3_fake: instrument.CalibrationReport
    ) -> None:
        """A profile whose reader cannot tell which surface produced it is a
        number without a subject."""

        report = calibration_3_fake
        for arm in report.arms:
            assert arm.resolved_levers["AILIBI_CITATION_RELEVANCE"] == "1"
            assert arm.resolved_levers["AILIBI_PROMPT_SET"] == AUTHORIZED_PROMPT_SET
            assert "AILIBI_LLM_PROVIDER" not in arm.resolved_levers
        candidate = next(arm for arm in report.arms if arm.arm == "combined_accounts")
        reference = next(arm for arm in report.arms if arm.arm == "repaired_clock")
        assert candidate.resolved_levers["AILIBI_PUBLIC_ACCOUNTS"] == "1"
        assert reference.resolved_levers["AILIBI_PUBLIC_ACCOUNTS"] == "0"

    def test_the_spent_modes_carry_no_diagnostics_block_and_no_levers(
        self,
        calibration_2_fake: instrument.CalibrationReport,
        tmp_path: Path,
    ) -> None:
        """The committed outputs' shape, unchanged.

        An EMPTY block is not empty in the payload — it carries the note — so a
        mode that reports none reports `null` rather than a paragraph about a
        block it never measured.
        """

        for report in (
            calibration_2_fake,
            instrument.run_calibration(
                _converted_record(), output_dir=tmp_path / "units"
            ),
        ):
            for arm in report.arms:
                assert arm.authored_diagnostics is None
                assert arm.resolved_levers == {}
            payload = json.loads(report.model_dump_json())
            assert all(row["authored_diagnostics"] is None for row in payload["arms"])

    def test_the_report_carries_counts_only(
        self, calibration_3_fake: instrument.CalibrationReport
    ) -> None:
        """No prose, no prompt, no prefix and no per-seed outcome."""

        report = calibration_3_fake
        payload = json.loads(report.model_dump_json())
        encoded = json.dumps(payload)
        for forbidden in (
            '"rationale_text":',
            '"free_text":',
            '"claims":',
            '"turns":',
            '"prompt":',
            '"prompts_by_agent":',
            '"steps":',
            '"outcome":',
        ):
            assert forbidden not in encoded, forbidden
        assert_report_holds_no_prefix_bytes(
            report,
            instrument.verify_calibration_draw(
                paired_seeds=instrument.CALIBRATION_3_PAIRED_SEEDS
            ).prefixes,
        )
        instrument.assert_calibration_reports_no_outcome(payload)
        # Per-unit rows carry spend and identity, and nothing the meeting did.
        assert {key for row in payload["unit_usage"] for key in row} == {
            "seed",
            "arm",
            "attempts",
            "completions",
            "input_tokens",
            "output_tokens",
            "model_work_seconds",
            "defaulted_turns",
            "defaulted_votes",
            "charged_failed_attempts",
            "retried_calls",
            "unaccounted_attempts",
        }

    def test_the_proposal_is_published_for_the_hundred_unit_run(
        self, calibration_3_replayed: instrument.CalibrationReport
    ) -> None:
        """Acceptance item 7: the rule and the function are unchanged.

        The rule string is compared against the one the 2026-09-15 sitting
        published rather than against a copy of it, so "unchanged" is checked
        against a committed record.
        """

        report = calibration_3_replayed
        assert report.proposal.rule == instrument.CEILING_PROPOSAL_RULE
        assert report.proposal.rule == _calibration_2_published()["proposal"]["rule"]
        assert report.proposal.units == instrument.planned_units() == 100

    def test_the_cli_runs_the_mode_by_name(self, tmp_path: Path) -> None:
        """`--calibrate --calibration-mode 2026-09-18`, dry, at exit 0."""

        measurement = tmp_path / "calibration.json"
        assert (
            instrument.main(
                [
                    "--calibrate",
                    "--calibration-mode",
                    "2026-09-18",
                    "--output-dir",
                    str(tmp_path / "units"),
                    "--json",
                    str(measurement),
                ]
            )
            == 0
        )
        payload = json.loads(measurement.read_text(encoding="utf-8"))
        assert payload["mode"] == "2026-09-18"
        assert payload["units"] == 120
        assert payload["caveat"] == instrument.CALIBRATION_3_CAVEAT

    def test_the_third_mode_refuses_a_single_record_flag(self, tmp_path: Path) -> None:
        """PLANTED: the draw's records named by hand."""

        with pytest.raises(SystemExit) as exited:
            instrument.main(
                [
                    "--calibrate",
                    "--calibration-mode",
                    "2026-09-18",
                    "--calibration-record",
                    str(_converted_record()),
                    "--output-dir",
                    str(tmp_path / "units"),
                ]
            )
        assert exited.value.code == 2


class TestTheSixPredictionsAreFixedBeforeTheSitting:
    """Acceptance item 8: the card, the manifest and the module agree."""

    def _manifest_section(self) -> str:
        text = _MANIFEST.read_text(encoding="utf-8")
        return text.split("## Development calibration 3 (2026-09-18)", 1)[1].split(
            "\n## ", 1
        )[0]

    def _rows(self) -> list[tuple[str, ...]]:
        return [
            (row.id, row.mechanism, row.fifth_run, row.prediction)
            for row in instrument.CALIBRATION_3_PREDICTIONS
        ]

    def test_the_module_carries_the_cards_six_rows(self) -> None:
        """The card's Evidence table, as objects."""

        rows = _prediction_rows(_CALIBRATION_3_CARD.read_text(encoding="utf-8"))
        assert len(rows) == 6
        assert rows == self._rows()

    def test_the_manifest_copies_them_verbatim(self) -> None:
        """One table, three places, and no paraphrase between them."""

        rows = _prediction_rows(self._manifest_section())
        assert len(rows) == 6
        assert rows == self._rows()
        assert [row.id for row in instrument.CALIBRATION_3_PREDICTIONS] == [
            f"P{index}" for index in range(1, 7)
        ]

    def test_the_manifest_says_none_of_them_is_a_gate(self) -> None:
        """A table of predictions published without this sentence reads as bars."""

        section = " ".join(self._manifest_section().split())
        assert " ".join(instrument.CALIBRATION_3_PREDICTIONS_NOTE.split()) in section
        for stated in ("none of them is a gate", "neither a stop nor a verdict"):
            assert stated in section, stated

    def test_the_manifest_states_this_modes_own_limits(self) -> None:
        """Each ceiling is in the document a runner reads."""

        text = _MANIFEST.read_text(encoding="utf-8")
        for quoted in (
            "116,000 input / 16,000 output",
            "4,700,000 input / 520,000 output",
            "5 h of model work within a 6 h elapsed deadline, one sitting",
            "60 paired seeds x 2 arms = 120 units",
            "4,612,800",
            "505,216",
        ):
            assert quoted in text, quoted

    def test_the_manifest_names_the_draw_with_its_digests(self) -> None:
        """Which records were authorized, and the bytes each of them is."""

        section = self._manifest_section()
        for converted in CONVERTED_BANDS[:2]:
            path = _REPO_ROOT / converted.manifest_path
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            assert digest in section, converted.manifest_path
            assert converted.manifest_path in section
        assert "5000 to 5009" in section
        assert "3000 to 3057" in section
        # And the one record this draw may never name.
        assert "refuses BY NAME" in section

    def test_the_frozen_analysis_strings_are_untouched(self) -> None:
        """This mode edits nothing the run is judged by.

        Compared over collapsed whitespace, the way the manifest's own
        frozen-analysis case is: these are sentences the document hard-wraps,
        and what is asserted is the words rather than the wrap.
        """

        collapsed = " ".join(_MANIFEST.read_text(encoding="utf-8").split())
        for frozen in (
            PRIMARY_OUTCOME,
            DECISION_RULE,
            STOP_RULE,
            instrument.WRONGFUL_EJECTION_TRADEOFF,
        ):
            assert " ".join(frozen.split()) in collapsed
        assert MINIMUM_ACTIONABLE_EFFECT_UNITS == 10
