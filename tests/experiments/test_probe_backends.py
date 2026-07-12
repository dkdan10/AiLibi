"""Unit tests for the provider-neutral probe seam (Task 14.3).

These drive :func:`experiments.lab.probe_backends.call_turn` with the two
provider ``_default_send`` hooks monkeypatched to canned fixtures, so the
dispatch + parse path is exercised with NO network call and no API key on the
wire. They pin:

* dispatch routing — ``backend='ollama'`` hits the ollama send (byte-identical
  wire args), ``backend='featherless'`` hits the featherless send;
* the shared ``_extract_json_block`` -> ``model_validate_json`` parse path,
  including the parse-failure carrier (``parsed is None`` + ``parse_error``);
* the request-time thinking toggle threaded to the featherless send and the
  ``response_format`` translation per ``response_format_mode``;
* the response-side thinking policy — ``strip`` excises a ``<think>`` block /
  ignores a ``reasoning_content`` channel and still parses, ``fail_loud`` raises;
* the recorded ``substrate_flags`` provenance (explicit + default snapshot);
* fail-loud on a missing featherless key / an unknown backend.

Async ``call_turn`` calls are driven with ``asyncio.run`` (no test-only
``pytest-asyncio`` dependency), matching the convention in
:mod:`tests.llm.test_featherless_client`.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

import pytest
from pydantic import BaseModel, ConfigDict

import experiments.lab.featherless_sweep as fs
import experiments.lab.probe_backends as pb
from experiments.lab.probe_backends import (
    CallResult,
    active_substrate_flags,
    call_turn,
    resolve_featherless_base_url,
)
from llm.featherless_client import DEFAULT_FEATHERLESS_BASE_URL, FeatherlessRawResponse
from llm.ollama_client import OllamaRawResponse


class _Ballot(BaseModel):
    """Minimal schema standing in for a probe output contract."""

    model_config = ConfigDict(extra="forbid")

    target: str
    confidence: float


_VALID = '{"target": "p-1", "confidence": 0.5}'
# Valid JSON, schema-invalid (missing ``confidence``) — the shape a weak model
# can emit, which must surface as ``parsed is None`` + a ``parse_error``.
_MALFORMED = '{"target": "p-1"}'

# An arbitrary EXPLICIT provenance dict threaded through call_turn verbatim.
# (Historical flag-OFF shape; since Task 14.9 the live snapshot is
# unconditionally all-ON, so an explicit dict is the only way a row can carry
# anything else — which is exactly what the passthrough contract covers.)
_FLAGS_OFF = {
    "testimony_as_content": False,
    "witnessed_kill_evidence": False,
    "movement_perception": False,
    "unfreeze_memory": False,
}
# The live snapshot under a bare env: the six graduated levers unconditionally ON
# -- the four 13.5 levers since Task 14.9, the Task-14.10 evidence-quality lever
# since the Task-14.12 close, and Task 15.5's reporter_exculpation since the
# Task-15.7 baseline-3 record (each env gate retired once the baseline adopted
# it, so the snapshot no longer reads an AILIBI_* var for any of them) -- plus the
# THREE LIVE default-OFF toggles, Task 16.4's hard_evidence_gate, Task 16.5's
# observation_id_rendering, and Task 16.6's citation_gate, all stamped False
# under the bare env.
_FLAGS_ON = {
    "testimony_as_content": True,
    "witnessed_kill_evidence": True,
    "movement_perception": True,
    "unfreeze_memory": True,
    "evidence_quality_lift": True,
    "reporter_exculpation": True,
    # The three live toggles: DEFAULT-OFF, so the bare/default snapshot stamps
    # them False alongside the six unconditional levers.
    "hard_evidence_gate": False,
    "observation_id_rendering": False,
    "citation_gate": False,
}


@dataclass
class _RecordingOllama:
    """Injectable ollama send recording its kwargs, returning a canned raw."""

    text: str
    thinking: str = ""
    prompt_eval_count: int = 11
    eval_count: int = 7
    seen: dict[str, Any] = field(default_factory=dict)

    async def __call__(self, **kwargs: Any) -> OllamaRawResponse:
        self.seen = kwargs
        return OllamaRawResponse(
            text=self.text,
            model=str(kwargs["model"]),
            prompt_eval_count=self.prompt_eval_count,
            eval_count=self.eval_count,
            thinking=self.thinking,
        )


@dataclass
class _RecordingFeatherless:
    """Injectable featherless send recording its kwargs, returning a canned raw."""

    text: str
    reasoning_content: str = ""
    prompt_tokens: int = 13
    completion_tokens: int = 9
    seen: dict[str, Any] = field(default_factory=dict)

    async def __call__(self, **kwargs: Any) -> FeatherlessRawResponse:
        self.seen = kwargs
        return FeatherlessRawResponse(
            text=self.text,
            model=str(kwargs["model"]),
            prompt_tokens=self.prompt_tokens,
            completion_tokens=self.completion_tokens,
            reasoning_content=self.reasoning_content,
        )


def _run_ollama(monkeypatch: pytest.MonkeyPatch, **kwargs: Any) -> CallResult[_Ballot]:
    send = _RecordingOllama(text=kwargs.pop("_text", _VALID))
    monkeypatch.setattr(pb, "_ollama_send", send)
    monkeypatch.setattr(pb, "_featherless_send", _forbidden_send("featherless"))
    result = asyncio.run(
        call_turn(
            "prompt",
            _Ballot,
            backend="ollama",
            model="qwen3.5:9b",
            temperature=0.0,
            max_tokens=256,
            substrate_flags=_FLAGS_OFF,
            **kwargs,
        )
    )
    result_seen[id(result)] = send.seen
    return result


def _forbidden_send(name: str) -> Any:
    async def _boom(**_kwargs: Any) -> Any:  # pragma: no cover - guard only
        raise AssertionError(f"{name} send must not be called on this dispatch")

    return _boom


# Side-channel so a helper can expose the recorded send kwargs without changing
# call_turn's return shape.
result_seen: dict[int, dict[str, Any]] = {}


# --------------------------------------------------------------------------- #
# Dispatch + parse                                                            #
# --------------------------------------------------------------------------- #
def test_ollama_dispatch_parses_and_maps_tokens(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _run_ollama(monkeypatch)
    assert result.parsed is not None
    assert (result.parsed.target, result.parsed.confidence) == ("p-1", 0.5)
    assert result.parse_error is None
    assert result.raw_text == _VALID
    assert result.latency_s >= 0.0
    assert (result.in_tokens, result.out_tokens) == (11, 7)
    assert result.thinking_chars == 0
    assert result.substrate_flags == _FLAGS_OFF


def test_ollama_wire_args_are_byte_identical(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _run_ollama(monkeypatch, ollama_host="localhost:11434", seed=0, num_ctx=8192)
    seen = next(iter(result_seen.values()))
    assert seen["host"] == "localhost:11434"
    assert seen["model"] == "qwen3.5:9b"
    assert seen["format_schema"] == _Ballot.model_json_schema()
    assert seen["options"] == {
        "temperature": 0.0,
        "seed": 0,
        "num_predict": 256,
        "num_ctx": 8192,
    }
    assert seen["think"] is False


def test_ollama_parse_failure_carries_error_and_raw(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _run_ollama(monkeypatch, _text=_MALFORMED)
    assert result.parsed is None
    assert result.parse_error is not None
    assert result.raw_text == _MALFORMED
    # Tokens / latency are still recorded on a parse failure.
    assert (result.in_tokens, result.out_tokens) == (11, 7)


def test_featherless_dispatch_parses(monkeypatch: pytest.MonkeyPatch) -> None:
    send = _RecordingFeatherless(text=_VALID)
    monkeypatch.setattr(pb, "_featherless_send", send)
    monkeypatch.setattr(pb, "_ollama_send", _forbidden_send("ollama"))
    result = asyncio.run(
        call_turn(
            "prompt",
            _Ballot,
            backend="featherless",
            model="Qwen/Qwen3-32B",
            temperature=0.2,
            max_tokens=512,
            api_key="sk-test",
            request_thinking=True,
            substrate_flags=_FLAGS_OFF,
        )
    )
    assert result.parsed is not None
    assert (result.in_tokens, result.out_tokens) == (13, 9)
    assert send.seen["api_key"] == "sk-test"
    assert send.seen["model"] == "Qwen/Qwen3-32B"
    assert send.seen["max_tokens"] == 512
    assert send.seen["temperature"] == 0.2
    assert send.seen["request_thinking"] is True
    # Default response_format_mode is json_object.
    assert send.seen["response_format"] == {"type": "json_object"}


# --------------------------------------------------------------------------- #
# response_format translation                                                 #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        ("json_object", {"type": "json_object"}),
        ("none", None),
    ],
)
def test_featherless_response_format_simple_modes(
    monkeypatch: pytest.MonkeyPatch, mode: str, expected: Any
) -> None:
    send = _RecordingFeatherless(text=_VALID)
    monkeypatch.setattr(pb, "_featherless_send", send)
    asyncio.run(
        call_turn(
            "prompt",
            _Ballot,
            backend="featherless",
            model="m",
            temperature=0.0,
            max_tokens=64,
            api_key="sk",
            response_format_mode=mode,  # type: ignore[arg-type]
            substrate_flags=_FLAGS_OFF,
        )
    )
    assert send.seen["response_format"] == expected


def test_featherless_response_format_json_schema(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    send = _RecordingFeatherless(text=_VALID)
    monkeypatch.setattr(pb, "_featherless_send", send)
    asyncio.run(
        call_turn(
            "prompt",
            _Ballot,
            backend="featherless",
            model="m",
            temperature=0.0,
            max_tokens=64,
            api_key="sk",
            response_format_mode="json_schema",
            substrate_flags=_FLAGS_OFF,
        )
    )
    rf = send.seen["response_format"]
    assert rf["type"] == "json_schema"
    assert rf["json_schema"]["name"] == "_Ballot"
    assert rf["json_schema"]["strict"] is True
    assert rf["json_schema"]["schema"] == _Ballot.model_json_schema()


# --------------------------------------------------------------------------- #
# response-side thinking policy                                               #
# --------------------------------------------------------------------------- #
def test_featherless_strip_excises_think_block(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw = f"<think>scratch {{}}</think>{_VALID}"
    send = _RecordingFeatherless(text=raw)
    monkeypatch.setattr(pb, "_featherless_send", send)
    result = asyncio.run(
        call_turn(
            "prompt",
            _Ballot,
            backend="featherless",
            model="m",
            temperature=0.0,
            max_tokens=64,
            api_key="sk",
            thinking_policy="strip",
            substrate_flags=_FLAGS_OFF,
        )
    )
    assert result.parsed is not None
    assert result.parsed.target == "p-1"
    # Inline reasoning (no side-channel) is counted: the excised prefix length,
    # not 0 — otherwise inline-tag models under-report thinking pollution.
    assert result.thinking_chars == len(raw) - len(_VALID)
    assert result.thinking_chars > 0


def test_featherless_strip_ignores_reasoning_channel(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    send = _RecordingFeatherless(text=_VALID, reasoning_content="deliberation here")
    monkeypatch.setattr(pb, "_featherless_send", send)
    result = asyncio.run(
        call_turn(
            "prompt",
            _Ballot,
            backend="featherless",
            model="m",
            temperature=0.0,
            max_tokens=64,
            api_key="sk",
            thinking_policy="strip",
            substrate_flags=_FLAGS_OFF,
        )
    )
    assert result.parsed is not None
    assert result.thinking_chars == len("deliberation here")


def test_featherless_fail_loud_raises_on_reasoning(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    send = _RecordingFeatherless(text=_VALID, reasoning_content="deliberation")
    monkeypatch.setattr(pb, "_featherless_send", send)
    with pytest.raises(RuntimeError, match="thinking_policy='fail_loud'"):
        asyncio.run(
            call_turn(
                "prompt",
                _Ballot,
                backend="featherless",
                model="m",
                temperature=0.0,
                max_tokens=64,
                api_key="sk",
                thinking_policy="fail_loud",
                substrate_flags=_FLAGS_OFF,
            )
        )


# --------------------------------------------------------------------------- #
# fail-loud guards + substrate flags                                          #
# --------------------------------------------------------------------------- #
def test_featherless_requires_api_key() -> None:
    with pytest.raises(ValueError, match="requires a non-empty api_key"):
        asyncio.run(
            call_turn(
                "prompt",
                _Ballot,
                backend="featherless",
                model="m",
                temperature=0.0,
                max_tokens=64,
                substrate_flags=_FLAGS_OFF,
            )
        )


def test_unknown_backend_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ValueError, match="unknown backend"):
        asyncio.run(
            call_turn(
                "prompt",
                _Ballot,
                backend="grok",  # type: ignore[arg-type]
                model="m",
                temperature=0.0,
                max_tokens=64,
                substrate_flags=_FLAGS_OFF,
            )
        )


def test_substrate_flags_default_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    # No explicit substrate_flags: call_turn snapshots the live substrate. All
    # six levers are unconditionally ON -- the four 13.5 levers since Task 14.9,
    # the 14.10 evidence-quality lever since the Task-14.12 close, and Task 15.5's
    # reporter_exculpation since the Task-15.7 baseline-3 record -- so the snapshot
    # is env-independent (a stray AILIBI_EVIDENCE_QUALITY_LIFT export cannot flip
    # it).
    monkeypatch.delenv("AILIBI_EVIDENCE_QUALITY_LIFT", raising=False)
    send = _RecordingOllama(text=_VALID)
    monkeypatch.setattr(pb, "_ollama_send", send)
    result = asyncio.run(
        call_turn(
            "prompt",
            _Ballot,
            backend="ollama",
            model="m",
            temperature=0.0,
            max_tokens=64,
        )
    )
    assert result.substrate_flags == _FLAGS_ON


def test_deception_battery_cfg_routes_to_featherless(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Fix #2 regression: BackendConfig threaded through deception_battery._call_cfg
    # must reach call_turn's featherless branch (not the ollama default).
    from experiments.lab.deception_battery import BackendConfig, _call_cfg

    # MeetingTurn is the schema deception_battery uses; a minimal valid body.
    body = (
        '{"turn_index": 0, "turn_id": "m:turn-0", "speaker": "p-1", '
        '"turn_kind": "opening", "reply_to": null, "observations": [], '
        '"claims": [], "free_text": "hello"}'
    )
    send = _RecordingFeatherless(text=body)
    monkeypatch.setattr(pb, "_featherless_send", send)
    monkeypatch.setattr(pb, "_ollama_send", _forbidden_send("ollama"))
    cfg = BackendConfig(backend="featherless", model="Qwen/Qwen3-32B", api_key="sk")
    turn, raw_text, latency = asyncio.run(_call_cfg("prompt", cfg))
    assert turn is not None
    assert send.seen["model"] == "Qwen/Qwen3-32B"
    assert send.seen["api_key"] == "sk"
    assert raw_text == body
    assert latency >= 0.0


def test_resolve_featherless_base_url() -> None:
    # Honors AILIBI_FEATHERLESS_BASE_URL (proxy / self-hosted), else the hosted
    # default — mirroring build_default_client.
    assert (
        resolve_featherless_base_url(env={"AILIBI_FEATHERLESS_BASE_URL": "http://x/v1"})
        == "http://x/v1"
    )
    assert resolve_featherless_base_url(env={}) == DEFAULT_FEATHERLESS_BASE_URL
    # Whitespace-only override falls back to the default (no empty base URL).
    assert (
        resolve_featherless_base_url(env={"AILIBI_FEATHERLESS_BASE_URL": "  "})
        == DEFAULT_FEATHERLESS_BASE_URL
    )


def test_featherless_base_url_resolves_from_env_when_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # base_url=None (the default) -> call_turn resolves the env override and
    # posts there, so a proxy/self-hosted sweep is honored without a CLI flag.
    send = _RecordingFeatherless(text=_VALID)
    monkeypatch.setattr(pb, "_featherless_send", send)
    monkeypatch.setenv("AILIBI_FEATHERLESS_BASE_URL", "http://proxy.local/v1")
    asyncio.run(
        call_turn(
            "prompt",
            _Ballot,
            backend="featherless",
            model="m",
            temperature=0.0,
            max_tokens=64,
            api_key="sk",
            substrate_flags=_FLAGS_OFF,
        )
    )
    assert send.seen["base_url"] == "http://proxy.local/v1"


def test_featherless_explicit_base_url_wins(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    send = _RecordingFeatherless(text=_VALID)
    monkeypatch.setattr(pb, "_featherless_send", send)
    monkeypatch.setenv("AILIBI_FEATHERLESS_BASE_URL", "http://env.local/v1")
    asyncio.run(
        call_turn(
            "prompt",
            _Ballot,
            backend="featherless",
            model="m",
            temperature=0.0,
            max_tokens=64,
            api_key="sk",
            base_url="http://explicit.local/v1",
            substrate_flags=_FLAGS_OFF,
        )
    )
    assert send.seen["base_url"] == "http://explicit.local/v1"


def test_active_substrate_flags_every_lever_unconditional(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Every substrate lever is unconditionally ON: the four 13.5 gates retired
    # at Task 14.9, the Task-14.10 evidence-quality gate at the Task-14.12 close,
    # and Task 15.5's reporter_exculpation gate at the Task-15.7 baseline-3 record.
    # So active_substrate_flags reads all-True under ANY env — bare, a legacy
    # all-ON export, a legacy "0", or a stray lever export — and no AILIBI_* var
    # can flip any of them (the delegation to
    # orchestrator.replay.substrate_flag_snapshot carries this for free).
    monkeypatch.delenv("AILIBI_EVIDENCE_QUALITY_LIFT", raising=False)
    assert active_substrate_flags(env={}) == _FLAGS_ON
    assert active_substrate_flags() == _FLAGS_ON
    assert active_substrate_flags(env={"AILIBI_TESTIMONY_AS_CONTENT": "0"}) == _FLAGS_ON
    assert (
        active_substrate_flags(env={"AILIBI_EVIDENCE_QUALITY_LIFT": "0"}) == _FLAGS_ON
    )
    assert (
        active_substrate_flags(env={"AILIBI_EVIDENCE_QUALITY_LIFT": "1"}) == _FLAGS_ON
    )
    # The graduated reporter_exculpation lever is likewise env-independent: a
    # stray AILIBI_REPORTER_EXCULPATION export (either polarity) cannot flip it.
    assert active_substrate_flags(env={"AILIBI_REPORTER_EXCULPATION": "0"}) == _FLAGS_ON
    assert active_substrate_flags(env={"AILIBI_REPORTER_EXCULPATION": "1"}) == _FLAGS_ON


# --------------------------------------------------------------------------- #
# Slate-entry pins — Task 16.1 probe region (no network)                      #
# --------------------------------------------------------------------------- #
def _find_spec(label: str) -> fs.ModelSpec:
    """The single SLATE entry with ``label`` (fails loud if absent or duplicated)."""

    matches = [spec for spec in fs.SLATE if spec.label == label]
    assert len(matches) == 1, f"expected exactly one slate entry labelled {label!r}"
    return matches[0]


def test_slate_is_well_formed() -> None:
    """The slate is a clean set: unique ids and labels, one 9B-class reference."""

    model_ids = [spec.model_id for spec in fs.SLATE]
    labels = [spec.label for spec in fs.SLATE]
    assert len(model_ids) == len(set(model_ids))
    assert len(labels) == len(set(labels))
    assert all(spec.role in {"candidate", "reference"} for spec in fs.SLATE)
    references = [spec for spec in fs.SLATE if spec.role == "reference"]
    assert len(references) == 1
    assert references[0].label == fs.REFERENCE_LABEL == "qwen3-8b"
    assert all(spec.model_id and spec.label for spec in fs.SLATE)


def test_qwen3_6_candidate_spec_pins() -> None:
    """qwen3-6-27b: served id preflight-confirmed 2026-07-11; the kwarg axis is
    honored live, and Task 16.12 landed its fail-loud entry in the production
    registry (lock: Task 16.2, audits/audit-phase-16-model-lock.md)."""

    spec = _find_spec("qwen3-6-27b")
    assert spec.model_id == "Qwen/Qwen3.6-27B"
    assert spec.thinking_axis is True
    assert spec.qwen_kwarg is True
    assert spec.role == "candidate"
    assert fs._modes_for(spec) == (False, True)


def test_thinkingcap_candidate_spec_pins() -> None:
    """thinkingcap-27b: its deployment 400s on chat_template_kwargs (and, live
    2026-07-11, on every generation) — bare transport, no thinking axis; the
    probe records the NO-GO."""

    spec = _find_spec("thinkingcap-27b")
    assert spec.model_id == "bottlecapai/ThinkingCap-Qwen3.6-27B"
    assert spec.thinking_axis is False
    assert spec.qwen_kwarg is False
    assert spec.role == "candidate"
    assert fs._modes_for(spec) == (False,)


def test_probe_artifacts_are_distinct_from_committed_14_4() -> None:
    """The probe writes its OWN artifacts — it must never clobber the committed
    14.4 matrix (results-featherless-sweep.jsonl / report-featherless-sweep.md)."""

    assert fs.PROBE_RESULTS != fs.RESULTS
    assert fs.PROBE_REPORT != fs.REPORT
    assert fs.PROBE_RESULTS.name == "results-featherless-sweep-qwen3-6-27b.jsonl"
    assert fs.PROBE_REPORT.name == "report-featherless-sweep-qwen3-6-27b.md"


def test_probe_slate_constants() -> None:
    """The probe reuses the incumbent's EXISTING prompt set (qwen3_32b — a 16.1
    finding; the bespoke set is 16.13's) and its labels resolve in the slate."""

    assert fs.PROBE_PROMPT_SET == "qwen3_32b"
    assert fs.PROBE_CANDIDATE_LABELS == ("qwen3-6-27b", "thinkingcap-27b")
    assert fs.PROBE_INCUMBENT_LABEL == "qwen3-32b"
    slate_labels = {spec.label for spec in fs.SLATE}
    for label in (*fs.PROBE_CANDIDATE_LABELS, fs.PROBE_INCUMBENT_LABEL):
        assert label in slate_labels
    assert set(fs._PROBE_ID_FORMS) == set(fs.PROBE_CANDIDATE_LABELS)
    for label, forms in fs._PROBE_ID_FORMS.items():
        assert forms  # a non-empty tuple of id forms...
        assert forms[0] == _find_spec(label).model_id  # ...led by the pinned id


def test_production_registry_boundary_post_lock() -> None:
    """The experiment-tier boundary pin, RE-PINNED post-lock: Task 16.12 landed
    the fail-loud registry entry for the locked id (lock: Task 16.2,
    audits/audit-phase-16-model-lock.md), so ``Qwen/Qwen3.6-27B`` is now a
    REGISTERED production id that supports the enable_thinking kwarg. The
    ThinkingCap NO-GO candidate stays UNREGISTERED — the probe never promoted it
    — so the production adapter still fails loud on it and the sweep-local
    transport remains its only route."""

    from llm.featherless_client import _supports_thinking_kwarg

    # The incumbent stays registered.
    assert fs._registry_knows("Qwen/Qwen3-32B") is True
    # 16.12 landed the locked id: registered AND kwarg-supporting.
    assert fs._registry_knows("Qwen/Qwen3.6-27B") is True
    assert _supports_thinking_kwarg("Qwen/Qwen3.6-27B") is True
    # The NO-GO ThinkingCap id is never registered: the adapter fails loud on it.
    assert fs._registry_knows("bottlecapai/ThinkingCap-Qwen3.6-27B") is False
    with pytest.raises(ValueError):
        _supports_thinking_kwarg("bottlecapai/ThinkingCap-Qwen3.6-27B")


def test_split_inline_think_shapes() -> None:
    """_split_inline_think splits on the LAST </think>: no tag is a passthrough,
    the reasoning prefix is peeled (a leading <think> dropped), the answer is the
    lstripped tail."""

    # No close tag: passthrough answer, empty reasoning.
    answer, reasoning = fs._split_inline_think("plain answer")
    assert answer == "plain answer"
    assert reasoning == ""

    # A bare close tag: the tail is the answer (no </think> leaks through), the
    # prefix becomes the reasoning.
    answer, reasoning = fs._split_inline_think("reasoning stuff</think>\n\n391")
    assert "391" in answer
    assert "</think>" not in answer
    assert "reasoning stuff" in reasoning

    # Wrapped <think>...</think> then a JSON tail: reasoning is the peeled scratch,
    # answer is the JSON (tolerant of trimming choices).
    answer, reasoning = fs._split_inline_think('<think>scratch</think>{"a": 1}')
    assert answer.strip() == '{"a": 1}'
    assert reasoning.strip() == "scratch"

    # Multiple close tags: the split is on the LAST one, so the answer is "c".
    answer, reasoning = fs._split_inline_think("a</think>b</think>c")
    assert answer.strip() == "c"
    assert "</think>" not in answer
