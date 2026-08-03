"""Provider-integration tests for Task 7.6 parse-tolerance normalization.

These tests pin that the discriminator-aware normalizer is wired into the
SHARED extract→validate seam in ``llm/provider.py`` (``_extract_json_block`` →
``model_validate_json``), so it protects BOTH real provider adapters — the
Anthropic client and the Ollama client (7.5), which routes its parse through
the same shared ``_extract_json_block``. The final test asserts the normalizer
is a strict NO-OP on the committed 4p/1i recorded outputs (byte-identical), so
recorded games replay unchanged and the frozen baseline is unaffected.

Task 8.9 moved the structured meeting schema to :class:`~meetings.schemas.MeetingTurn`
(the Task 8.7 ordered-``turns`` reshape) -- the same schema ``reasoner.py``
feeds the provider as ``format=`` -- so the fixtures here are turn-shaped, and
``_MEETING_SCHEMAS`` is ``(MeetingTurn, VoteBallot)``: the structured-output
kinds the provider is constrained by.

Task 19.6 adds :class:`TestPricingFailsLoudOnUnknownModel` at the bottom: the
unit-level pin on the OTHER shared seam in ``llm/provider.py``,
``_compute_cost_usd``, which all three adapters route their cost through. The
end-to-end pin (the raise surfacing out of ``AnthropicClient.complete``) rides
in ``tests/llm/test_client.py``.
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
    DEFAULT_MEETING_MODEL,
    DEFAULT_TRIGGER_MODEL,
    PROVIDER_ANTHROPIC,
    PROVIDER_FEATHERLESS,
    PROVIDER_OLLAMA,
    AnthropicClient,
    AnthropicRawResponse,
    _compute_cost_usd,
    _extract_json_block,
    _normalize_json_text,
    extract_parse_failure,
)
from llm.report_normalize import normalize_report_payload
from meetings.schemas import AlibiClaim, MeetingTurn, VoteBallot

_T = TypeVar("_T")

_MEETING_SCHEMAS: tuple[type[BaseModel], ...] = (MeetingTurn, VoteBallot)


def _run(coro: Awaitable[_T]) -> _T:
    return asyncio.new_event_loop().run_until_complete(coro)


def _bad_turn_text() -> str:
    """A MeetingTurn with a stray ``co_present`` on a ``found_body`` obs."""

    return json.dumps(
        {
            "turn_id": "m-7:turn-0",
            "turn_index": 0,
            "speaker": "p-3",
            "turn_kind": "opening",
            "reply_to": None,
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


def _reversed_alibi_turn_text() -> str:
    """A MeetingTurn whose AlibiClaim has ``from_tick > to_tick`` (Task 7.10, gp-2).

    The seed-36 repro shape: ``qwen2.5:7b-instruct`` emits ``from_tick=8,
    to_tick=1``. The strict ``AlibiClaim`` validator rejects it; the shared
    seam must swap the bounds before validation so it survives.
    """

    return json.dumps(
        {
            "turn_id": "m-1:turn-2",
            "turn_index": 2,
            "speaker": "p-3",
            "turn_kind": "reply",
            "reply_to": "m-1:turn-0",
            "observations": [],
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


def _valid_turn_text() -> str:
    return json.dumps(
        {
            "turn_id": "m-7:turn-0",
            "turn_index": 0,
            "speaker": "p-3",
            "turn_kind": "opening",
            "reply_to": None,
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
            "turn_id": "m-7:turn-0",
            "turn_index": 0,
            "speaker": "p-3",
            "turn_kind": "opening",
            "reply_to": None,
            "observations": [{"type": "found_body", "tick": 410, "room": "MedBay"}],
            "claims": [],
            "free_text": "x",
        }
    )


def _unhashable_discriminator_text() -> str:
    """A MeetingTurn whose observation discriminator is a list (unhashable)."""

    return json.dumps(
        {
            "turn_id": "m-7:turn-0",
            "turn_index": 0,
            "speaker": "p-3",
            "turn_kind": "opening",
            "reply_to": None,
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
        out = _extract_json_block(_bad_turn_text(), MeetingTurn)
        assert "co_present" not in out
        MeetingTurn.model_validate_json(out)

    def test_schemaless_call_is_unchanged_behavior(self) -> None:
        # Back-compat: the single-arg form (used by free-text calls and by the
        # extractor's own test suite) must not normalize.
        raw = "prefix " + _bad_turn_text() + " suffix"
        assert _extract_json_block(raw) == _extract_json_block(raw, None)
        # And it still extracts the (un-normalized) JSON object.
        assert "co_present" in _extract_json_block(raw)

    def test_salvage_survives_fences_and_prose(self) -> None:
        raw = "Here is my report:\n```json\n" + _bad_turn_text() + "\n```\nDone!"
        out = _extract_json_block(raw, MeetingTurn)
        assert "co_present" not in out
        assert "Done" not in out
        MeetingTurn.model_validate_json(out)

    def test_schema_aware_call_repairs_reversed_alibi(self) -> None:
        # Task 7.10: the shared seam swaps a reversed alibi range before
        # validation, so it protects every provider AND the replay path.
        out = _extract_json_block(_reversed_alibi_turn_text(), MeetingTurn)
        turn = MeetingTurn.model_validate_json(out)
        claim = turn.claims[0]
        assert isinstance(claim, AlibiClaim)
        assert (claim.from_tick, claim.to_tick) == (1, 8)

    def test_normalize_json_text_is_byte_identical_on_valid(self) -> None:
        valid = _valid_turn_text()
        assert _normalize_json_text(valid, MeetingTurn) == valid

    def test_normalize_json_text_passes_through_unparseable(self) -> None:
        # Truncated/!JSON text is returned unchanged so model_validate_json
        # raises the actionable error rather than this helper masking it.
        truncated = '{"turn_id": "m-1:turn-0", "turn_index": 0, "observ'
        assert _normalize_json_text(truncated, MeetingTurn) == truncated


class TestAnthropicProviderNormalization:
    def test_complete_salvages_near_miss_report(self) -> None:
        resp = _run(
            _anthropic_client(_bad_turn_text()).complete(
                prompt="p", schema=MeetingTurn, max_tokens=512, temperature=0.0
            )
        )
        assert "co_present" not in resp.text
        MeetingTurn.model_validate_json(resp.text)

    def test_complete_is_byte_identical_on_valid(self) -> None:
        valid = _valid_turn_text()
        resp = _run(
            _anthropic_client(valid).complete(
                prompt="p", schema=MeetingTurn, max_tokens=512, temperature=0.0
            )
        )
        assert resp.text == valid

    def test_complete_still_fails_loud_on_missing_required(self) -> None:
        with pytest.raises(ValidationError) as exc:
            _run(
                _anthropic_client(_missing_required_text()).complete(
                    prompt="p", schema=MeetingTurn, max_tokens=512, temperature=0.0
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
                    prompt="p", schema=MeetingTurn, max_tokens=512, temperature=0.0
                )
            )
        failure = extract_parse_failure(exc.value)
        assert failure is not None
        assert failure.model == "claude-sonnet-4-6"


class TestOllamaProviderNormalization:
    """The whole point of 7.6: protect the local model's near-miss reports."""

    def test_complete_salvages_near_miss_report(self) -> None:
        resp = _run(
            _ollama_client(_bad_turn_text()).complete(
                prompt="p", schema=MeetingTurn, max_tokens=512, temperature=0.0
            )
        )
        assert "co_present" not in resp.text
        assert resp.cost_usd == 0.0
        MeetingTurn.model_validate_json(resp.text)

    def test_complete_salvages_reversed_alibi_turn(self) -> None:
        # Task 7.10 / gp-2: the local model's reversed-alibi turn (the
        # seed-25/36/40 crash) is salvaged end-to-end through complete(), so
        # the manager that consumes resp.text gets a valid MeetingTurn instead
        # of a meeting-aborting ValidationError.
        resp = _run(
            _ollama_client(_reversed_alibi_turn_text()).complete(
                prompt="p", schema=MeetingTurn, max_tokens=512, temperature=0.0
            )
        )
        turn = MeetingTurn.model_validate_json(resp.text)
        claim = turn.claims[0]
        assert isinstance(claim, AlibiClaim)
        assert (claim.from_tick, claim.to_tick) == (1, 8)

    def test_complete_is_byte_identical_on_valid(self) -> None:
        valid = _valid_turn_text()
        resp = _run(
            _ollama_client(valid).complete(
                prompt="p", schema=MeetingTurn, max_tokens=512, temperature=0.0
            )
        )
        assert resp.text == valid

    def test_complete_still_fails_loud_on_missing_required(self) -> None:
        with pytest.raises(ValidationError):
            _run(
                _ollama_client(_missing_required_text()).complete(
                    prompt="p", schema=MeetingTurn, max_tokens=512, temperature=0.0
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
    # The committed flat 4p1i set now lives under replays/samples/4p1i/ (Task 12.12).
    samples = root / "replays" / "samples" / "4p1i"
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


# Harvest once at collection. The committed 4p/1i baseline still carries the
# PRE-8.7 ``Statement`` / ``ReportDocument`` outputs (the meeting record is
# re-recorded to the ordered-``turns`` shape in Task 8.12); those old outputs no
# longer validate against ``MeetingTurn``, so until the re-record the only thing
# the harvest finds is the unchanged ``VoteBallot`` rows. Gating the
# frozen-baseline no-op guard on "does the committed baseline already carry a
# MeetingTurn output" makes it self-healing: it stays skipped on the pre-8.12
# bytes and runs automatically the moment 8.12's re-recorded turns land — no
# manual un-skip is needed (Task 8.12 does not edit tests/llm).
_RECORDED_OUTPUTS = _recorded_outputs()
_baseline_pending_rerecord = pytest.mark.skipif(
    not any(schema is MeetingTurn for _, _, schema in _RECORDED_OUTPUTS),
    reason=(
        "committed 4p/1i baseline still carries pre-8.7 Statement/ReportDocument "
        "outputs; re-recorded to the MeetingTurn shape in Task 8.12"
    ),
)


@_baseline_pending_rerecord
class TestNoOpOnCommittedBaseline:
    """Explicit byte-identical no-op on the frozen 4p/1i recorded outputs.

    DESIGN.md §10.1: recorded LLM outputs replay byte-identically. The frozen
    baseline was recorded against valid schemas, so the normalizer MUST be a
    no-op on every committed output — otherwise replay would drift. This loads
    the committed set and asserts that directly (not via ``check.sh``). It is
    skipped until Task 8.12 re-records the baseline to the turn shape (see the
    self-healing gate above).
    """

    def test_baseline_has_structured_outputs_to_check(self) -> None:
        rows = _RECORDED_OUTPUTS
        kinds = {schema.__name__ for _, _, schema in rows}
        # The committed 4p/1i meeting replays carry chain turns + ballots.
        assert {"MeetingTurn", "VoteBallot"} <= kinds
        # Guard against a vacuous test if the corpus ever shrinks unexpectedly.
        # Floor sized to the Task 8.12 re-record: 4 meeting-bearing flat seeds
        # under the chain protocol yield 19 structured outputs (turns +
        # ballots); 15 keeps headroom for re-record variance while staying a
        # real non-vacuousness guard.
        assert len(rows) >= 15

    def test_normalizer_is_byte_identical_on_every_recorded_output(self) -> None:
        for seed_file, text, schema in _RECORDED_OUTPUTS:
            # Pure function is a deep-equal no-op...
            payload = json.loads(text)
            assert normalize_report_payload(payload, schema) == payload, seed_file
            # ...and the provider seam returns the recorded text byte-identical.
            assert _extract_json_block(text, schema) == text, seed_file

    def test_at_least_one_recorded_turn_exercises_the_union(self) -> None:
        # Ensure the corpus actually contains discriminated-union observations or
        # claims, so the no-op assertion above is meaningful (not just scalar
        # payloads like a bare VoteBallot).
        saw_union = False
        for _, text, schema in _RECORDED_OUTPUTS:
            if schema is MeetingTurn:
                payload = json.loads(text)
                if payload.get("observations") or payload.get("claims"):
                    saw_union = True
                    break
        assert saw_union


class TestPricingFailsLoudOnUnknownModel:
    """Task 19.6: ``_compute_cost_usd`` has no Anthropic fallback rate.

    The Anthropic table used to carry a ``(3.00, 15.00)`` Sonnet-shaped
    default, so an unpriced model — a new release, a typo'd
    ``AILIBI_LLM_MEETING_MODEL``, a dated alias resolution echoed back in
    ``raw.model`` — was billed at frontier rates and the recorded
    ``cost_usd`` became fiction. Cost accounting is exactly where AGENTS.md
    §"No silent fallbacks" binds hardest, so the lookup now raises with the
    model name. The two PROVIDER-keyed zero fallbacks (Ollama, Featherless)
    are a different mechanism and are pinned here as unchanged: they key on
    provider, not model, so they cannot substitute one model's rate for
    another's.
    """

    def test_known_models_price_exactly_as_before(self) -> None:
        # Sonnet: $3/Mtok in + $15/Mtok out.
        assert _compute_cost_usd(
            model=DEFAULT_MEETING_MODEL,
            input_tokens=1_000_000,
            output_tokens=1_000_000,
        ) == pytest.approx(18.0)
        # Haiku: $1/Mtok in + $5/Mtok out.
        assert _compute_cost_usd(
            model=DEFAULT_TRIGGER_MODEL,
            input_tokens=1_000_000,
            output_tokens=1_000_000,
        ) == pytest.approx(6.0)

    def test_unknown_anthropic_model_raises_naming_the_model(self) -> None:
        with pytest.raises(ValueError, match="claude-sonnet-9-9") as excinfo:
            _compute_cost_usd(
                model="claude-sonnet-9-9",
                input_tokens=2_000_000,
                output_tokens=0,
                provider=PROVIDER_ANTHROPIC,
            )
        message = str(excinfo.value)
        # Actionable: names where to declare the rate and what IS priced.
        assert "_ANTHROPIC_PRICING_USD_PER_MTOK" in message
        assert DEFAULT_MEETING_MODEL in message
        assert DEFAULT_TRIGGER_MODEL in message

    def test_unknown_model_raises_on_the_default_provider_arg(self) -> None:
        # The Anthropic call site omits ``provider=``; the raise must reach it.
        with pytest.raises(ValueError, match="unknown-model-id"):
            _compute_cost_usd(model="unknown-model-id", input_tokens=1, output_tokens=1)

    def test_zero_token_call_on_an_unknown_model_still_raises(self) -> None:
        # The defect is the missing RATE, not the amount: a zero-token call
        # that would have "cost $0.00 anyway" must not launder an unpriced
        # model past the check.
        with pytest.raises(ValueError, match="unknown-model-id"):
            _compute_cost_usd(model="unknown-model-id", input_tokens=0, output_tokens=0)

    def test_provider_keyed_zero_fallbacks_are_unchanged(self) -> None:
        # Ollama and Featherless stay free for ANY model name: their fallback
        # is keyed by provider (a deliberate flat-rate/local-$0 statement),
        # not a guess at another model's price.
        assert (
            _compute_cost_usd(
                model="qwen3.5:9b",
                input_tokens=5_000_000,
                output_tokens=5_000_000,
                provider=PROVIDER_OLLAMA,
            )
            == 0.0
        )
        assert (
            _compute_cost_usd(
                model="Qwen/Qwen3.6-27B",
                input_tokens=5_000_000,
                output_tokens=5_000_000,
                provider=PROVIDER_FEATHERLESS,
            )
            == 0.0
        )
