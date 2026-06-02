"""Provider-integration tests for Task 7.6 parse-tolerance normalization.

These tests pin that the discriminator-aware normalizer is wired into the
SHARED extract→validate seam in ``llm/provider.py`` (``_extract_json_block`` →
``model_validate_json``), so it protects BOTH real provider adapters — the
Anthropic client and the Ollama client (7.5), which routes its parse through
the same shared ``_extract_json_block``. The final test asserts the normalizer
is a strict NO-OP on the committed 4p/1i recorded outputs (byte-identical), so
recorded games replay unchanged and the frozen baseline is unaffected.
"""

from __future__ import annotations

import asyncio
import glob
import json
from collections.abc import Awaitable, Iterator
from pathlib import Path
from typing import Any, TypeVar

import pytest
from pydantic import BaseModel, ValidationError

from llm.ollama_client import OllamaClient, OllamaRawResponse
from llm.provider import (
    AnthropicClient,
    AnthropicRawResponse,
    _extract_json_block,
    _normalize_json_text,
    extract_parse_failure,
)
from llm.report_normalize import normalize_report_payload
from meetings.schemas import AlibiClaim, ReportDocument, Statement, VoteBallot

_T = TypeVar("_T")

_MEETING_SCHEMAS: tuple[type[BaseModel], ...] = (ReportDocument, Statement, VoteBallot)


def _run(coro: Awaitable[_T]) -> _T:
    return asyncio.new_event_loop().run_until_complete(coro)


def _bad_report_text() -> str:
    """A ReportDocument with a stray ``co_present`` on a ``found_body`` obs."""

    return json.dumps(
        {
            "agent_id": "p-3",
            "tick": 412,
            "observations": [
                {
                    "type": "found_body",
                    "tick": 410,
                    "body_of": "p-2",
                    "room": "MedBay",
                    "co_present": ["p-5"],
                }
            ],
            "claims": [],
            "free_text": "found a body",
        }
    )


def _reversed_alibi_statement_text() -> str:
    """A Statement whose AlibiClaim has ``from_tick > to_tick`` (Task 7.10, gp-2).

    The seed-36 repro shape: ``qwen2.5:7b-instruct`` emits ``from_tick=8,
    to_tick=1``. The strict ``AlibiClaim`` validator rejects it; the shared
    seam must swap the bounds before validation so it survives.
    """

    return json.dumps(
        {
            "statement_id": "s1",
            "speaker": "p-3",
            "tick": 11,
            "round_index": 0,
            "target": None,
            "claims": [
                {
                    "type": "alibi",
                    "subject": "p-3",
                    "from_tick": 8,
                    "to_tick": 1,
                    "room": "CAFETERIA",
                }
            ],
            "free_text": "I was around.",
        }
    )


def _valid_report_text() -> str:
    return json.dumps(
        {
            "agent_id": "p-3",
            "tick": 412,
            "observations": [
                {
                    "type": "saw_player",
                    "tick": 380,
                    "subject": "p-5",
                    "room": "Elec",
                    "co_present": ["p-7"],
                }
            ],
            "claims": [],
            "free_text": "hi",
        }
    )


def _missing_required_text() -> str:
    return json.dumps(
        {
            "agent_id": "p-3",
            "tick": 412,
            "observations": [{"type": "found_body", "tick": 410, "room": "MedBay"}],
            "claims": [],
            "free_text": "x",
        }
    )


def _unhashable_discriminator_text() -> str:
    """A ReportDocument whose observation discriminator is a list (unhashable)."""

    return json.dumps(
        {
            "agent_id": "p-3",
            "tick": 412,
            "observations": [
                {
                    "type": ["found_body"],
                    "tick": 410,
                    "body_of": "p-2",
                    "room": "MedBay",
                }
            ],
            "claims": [],
            "free_text": "x",
        }
    )


def _anthropic_client(text: str) -> AnthropicClient:
    async def _send(**_: Any) -> AnthropicRawResponse:
        return AnthropicRawResponse(
            text=text, model="claude-sonnet-4-6", input_tokens=11, output_tokens=22
        )

    return AnthropicClient(api_key="test-key", send=_send)


def _ollama_client(text: str) -> OllamaClient:
    async def _send(**_: Any) -> OllamaRawResponse:
        return OllamaRawResponse(
            text=text, model="qwen2.5:7b-instruct", prompt_eval_count=5, eval_count=9
        )

    return OllamaClient(host="localhost:11434", seed=0, send=_send)


class TestExtractorNormalizationSeam:
    """``_extract_json_block(text, schema)`` is the single normalization site."""

    def test_schema_aware_call_salvages_co_present(self) -> None:
        out = _extract_json_block(_bad_report_text(), ReportDocument)
        assert "co_present" not in out
        ReportDocument.model_validate_json(out)

    def test_schemaless_call_is_unchanged_behavior(self) -> None:
        # Back-compat: the single-arg form (used by free-text calls and by the
        # extractor's own test suite) must not normalize.
        raw = "prefix " + _bad_report_text() + " suffix"
        assert _extract_json_block(raw) == _extract_json_block(raw, None)
        # And it still extracts the (un-normalized) JSON object.
        assert "co_present" in _extract_json_block(raw)

    def test_salvage_survives_fences_and_prose(self) -> None:
        raw = "Here is my report:\n```json\n" + _bad_report_text() + "\n```\nDone!"
        out = _extract_json_block(raw, ReportDocument)
        assert "co_present" not in out
        assert "Done" not in out
        ReportDocument.model_validate_json(out)

    def test_schema_aware_call_repairs_reversed_alibi(self) -> None:
        # Task 7.10: the shared seam swaps a reversed alibi range before
        # validation, so it protects every provider AND the replay path.
        out = _extract_json_block(_reversed_alibi_statement_text(), Statement)
        statement = Statement.model_validate_json(out)
        claim = statement.claims[0]
        assert isinstance(claim, AlibiClaim)
        assert (claim.from_tick, claim.to_tick) == (1, 8)

    def test_normalize_json_text_is_byte_identical_on_valid(self) -> None:
        valid = _valid_report_text()
        assert _normalize_json_text(valid, ReportDocument) == valid

    def test_normalize_json_text_passes_through_unparseable(self) -> None:
        # Truncated/!JSON text is returned unchanged so model_validate_json
        # raises the actionable error rather than this helper masking it.
        truncated = '{"agent_id": "p-1", "tick": 1, "observ'
        assert _normalize_json_text(truncated, ReportDocument) == truncated


class TestAnthropicProviderNormalization:
    def test_complete_salvages_near_miss_report(self) -> None:
        resp = _run(
            _anthropic_client(_bad_report_text()).complete(
                prompt="p", schema=ReportDocument, max_tokens=512, temperature=0.0
            )
        )
        assert "co_present" not in resp.text
        ReportDocument.model_validate_json(resp.text)

    def test_complete_is_byte_identical_on_valid(self) -> None:
        valid = _valid_report_text()
        resp = _run(
            _anthropic_client(valid).complete(
                prompt="p", schema=ReportDocument, max_tokens=512, temperature=0.0
            )
        )
        assert resp.text == valid

    def test_complete_still_fails_loud_on_missing_required(self) -> None:
        with pytest.raises(ValidationError) as exc:
            _run(
                _anthropic_client(_missing_required_text()).complete(
                    prompt="p", schema=ReportDocument, max_tokens=512, temperature=0.0
                )
            )
        # Existing failed-call audit metadata is still attached (no regression).
        failure = extract_parse_failure(exc.value)
        assert failure is not None
        assert failure.model == "claude-sonnet-4-6"

    def test_unhashable_discriminator_surfaces_as_validation_error(self) -> None:
        # A malformed, unhashable discriminator (`{"type": ["found_body"]}`) must
        # NOT leak a TypeError out of the (pre-validation) normalization seam —
        # which would bypass the failed-call metadata path. It must surface as a
        # ValidationError with the metadata attached, exactly like any other
        # schema-invalid output.
        with pytest.raises(ValidationError) as exc:
            _run(
                _anthropic_client(_unhashable_discriminator_text()).complete(
                    prompt="p", schema=ReportDocument, max_tokens=512, temperature=0.0
                )
            )
        failure = extract_parse_failure(exc.value)
        assert failure is not None
        assert failure.model == "claude-sonnet-4-6"


class TestOllamaProviderNormalization:
    """The whole point of 7.6: protect the local model's near-miss reports."""

    def test_complete_salvages_near_miss_report(self) -> None:
        resp = _run(
            _ollama_client(_bad_report_text()).complete(
                prompt="p", schema=ReportDocument, max_tokens=512, temperature=0.0
            )
        )
        assert "co_present" not in resp.text
        assert resp.cost_usd == 0.0
        ReportDocument.model_validate_json(resp.text)

    def test_complete_salvages_reversed_alibi_statement(self) -> None:
        # Task 7.10 / gp-2: the local model's reversed-alibi statement (the
        # seed-25/36/40 crash) is salvaged end-to-end through complete(), so
        # the manager that consumes resp.text gets a valid Statement instead
        # of a meeting-aborting ValidationError.
        resp = _run(
            _ollama_client(_reversed_alibi_statement_text()).complete(
                prompt="p", schema=Statement, max_tokens=512, temperature=0.0
            )
        )
        statement = Statement.model_validate_json(resp.text)
        claim = statement.claims[0]
        assert isinstance(claim, AlibiClaim)
        assert (claim.from_tick, claim.to_tick) == (1, 8)

    def test_complete_is_byte_identical_on_valid(self) -> None:
        valid = _valid_report_text()
        resp = _run(
            _ollama_client(valid).complete(
                prompt="p", schema=ReportDocument, max_tokens=512, temperature=0.0
            )
        )
        assert resp.text == valid

    def test_complete_still_fails_loud_on_missing_required(self) -> None:
        with pytest.raises(ValidationError):
            _run(
                _ollama_client(_missing_required_text()).complete(
                    prompt="p", schema=ReportDocument, max_tokens=512, temperature=0.0
                )
            )


def _classify(text: str) -> type[BaseModel] | None:
    """Return the meeting schema a recorded output validates against, if any."""

    for schema in _MEETING_SCHEMAS:
        try:
            schema.model_validate_json(text)
        except ValidationError:
            continue
        return schema
    return None


def _iter_json_object_strings(node: Any) -> Iterator[str]:
    """Yield every string in ``node`` that looks like a JSON object literal."""

    if isinstance(node, dict):
        for value in node.values():
            yield from _iter_json_object_strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _iter_json_object_strings(value)
    elif isinstance(node, str):
        stripped = node.strip()
        if stripped.startswith("{") and stripped.endswith("}"):
            yield node


def _recorded_outputs() -> list[tuple[str, str, type[BaseModel]]]:
    """(seed_file, recorded_text, schema) for every structured committed output.

    The recorded LLM outputs are JSON strings embedded in the replay JSONL
    (committed meetings carry them under ``meeting.llm_calls[].response_text``);
    the exact record layout is an implementation detail of the replay writer, so
    we harvest every embedded JSON-object string that validates against a meeting
    schema rather than hard-coding a record path.
    """

    root = Path(__file__).resolve().parents[2]
    samples = root / "replays" / "samples"
    rows: list[tuple[str, str, type[BaseModel]]] = []
    for path in sorted(glob.glob(str(samples / "replay-seed-*.jsonl"))):
        name = Path(path).name
        with open(path) as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                for text in _iter_json_object_strings(record):
                    schema = _classify(text)
                    if schema is not None:
                        rows.append((name, text, schema))
    return rows


class TestNoOpOnCommittedBaseline:
    """Explicit byte-identical no-op on the frozen 4p/1i recorded outputs.

    DESIGN.md §10.1: recorded LLM outputs replay byte-identically. The frozen
    baseline was recorded against valid schemas, so the normalizer MUST be a
    no-op on every committed output — otherwise replay would drift. This loads
    the committed set and asserts that directly (not via ``check.sh``).
    """

    def test_baseline_has_structured_outputs_to_check(self) -> None:
        rows = _recorded_outputs()
        kinds = {schema.__name__ for _, _, schema in rows}
        # The committed 4p/1i meeting replays carry reports, statements, ballots.
        assert {"ReportDocument", "Statement", "VoteBallot"} <= kinds
        # Guard against a vacuous test if the corpus ever shrinks unexpectedly.
        assert len(rows) >= 20

    def test_normalizer_is_byte_identical_on_every_recorded_output(self) -> None:
        for seed_file, text, schema in _recorded_outputs():
            # Pure function is a deep-equal no-op...
            payload = json.loads(text)
            assert normalize_report_payload(payload, schema) == payload, seed_file
            # ...and the provider seam returns the recorded text byte-identical.
            assert _extract_json_block(text, schema) == text, seed_file

    def test_at_least_one_recorded_report_exercises_the_union(self) -> None:
        # Ensure the corpus actually contains discriminated-union observations,
        # so the no-op assertion above is meaningful (not just scalar payloads).
        saw_union = False
        for _, text, schema in _recorded_outputs():
            if schema is ReportDocument:
                payload = json.loads(text)
                if payload.get("observations") or payload.get("claims"):
                    saw_union = True
                    break
        assert saw_union
