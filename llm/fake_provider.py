"""Deterministic fake :class:`~llm.client.LLMClient` for CI and unit tests.

The fake satisfies the same Protocol as :class:`llm.provider.AnthropicClient`
and never touches the network. Same prompt + same ``schema`` + same
``call_kind`` always returns byte-identical :class:`~llm.client.LLMResponse`.

The fake's job is to provide a schema-valid string the call site can parse —
it is **not** a recorder, hash-replay, or fuzzing tool. When a ``schema`` is
supplied the fake builds a minimal valid instance by introspecting the
Pydantic model; without a schema it echoes a deterministic canned string
derived from the prompt.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Final

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from llm.client import CallKind, LLMResponse, TokenUsage


_FAKE_MEETING_MODEL: Final[str] = "fake-meeting"
_FAKE_TRIGGER_MODEL: Final[str] = "fake-trigger"


class FakeProvider:
    """In-process LLM stub that returns schema-valid, deterministic output.

    Designed to satisfy :class:`~llm.client.LLMClient` structurally — the
    isinstance check in unit tests and the call-site type hints both pass.

    Determinism notes:

    * Token counts derive from prompt and response string lengths so the
      same call yields the same :class:`TokenUsage` every time.
    * ``cost_usd`` is always ``0.0`` (the fake never spends money).
    * The model id reported back is the fake-tier id matching
      ``call_kind`` (or the explicit ``model`` argument when given).
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
        if max_tokens <= 0:
            raise ValueError(f"max_tokens must be positive, got {max_tokens}")
        if not 0.0 <= temperature <= 2.0:
            raise ValueError(f"temperature must be in [0, 2], got {temperature}")
        # ``agent_id`` is replay-attribution metadata, not part of the
        # deterministic response contract; the fake accepts and ignores it.
        del agent_id
        text = _build_response_text(prompt=prompt, schema=schema)
        if schema is not None:
            schema.model_validate_json(text)
        chosen_model = model if model is not None else _fake_model_for(call_kind)
        return LLMResponse(
            text=text,
            usage=TokenUsage(
                input_tokens=_approx_tokens(prompt),
                output_tokens=_approx_tokens(text),
            ),
            cost_usd=0.0,
            model=chosen_model,
        )


def _fake_model_for(call_kind: CallKind) -> str:
    if call_kind == "meeting":
        return _FAKE_MEETING_MODEL
    if call_kind == "trigger":
        return _FAKE_TRIGGER_MODEL
    # Unreachable under `mypy --strict` because `CallKind` is a
    # `Literal`, but AGENTS.md mandates no silent fallbacks.
    raise ValueError(f"unknown call_kind: {call_kind!r}")


def _approx_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _build_response_text(
    *,
    prompt: str,
    schema: type[BaseModel] | None,
) -> str:
    if schema is None:
        digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]
        return f"fake-response:{digest}"
    instance = _minimal_valid_instance(schema, prompt=prompt)
    return instance.model_dump_json()


def _minimal_valid_instance(
    schema: type[BaseModel],
    *,
    prompt: str,
) -> BaseModel:
    """Build a minimal Pydantic instance that survives validation.

    The fake produces a deterministic value per field by introspecting the
    Pydantic field type. Fields with defaults keep them; fields without
    defaults receive a canonical zero-value of the right shape (empty list
    / empty dict / ``""`` / ``0`` / ``False`` / ``None`` for optionals).
    """

    seed = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:8]
    values: dict[str, Any] = {}
    for field_name, field_info in schema.model_fields.items():
        if not field_info.is_required():
            continue
        values[field_name] = _zero_value_for(
            field_info=field_info,
            seed=seed,
            field_name=field_name,
        )
    return schema.model_validate(values)


def _zero_value_for(
    *,
    field_info: FieldInfo,
    seed: str,
    field_name: str,
) -> Any:
    annotation = field_info.annotation
    return _zero_value_from_annotation(annotation, seed=seed, field_name=field_name)


def _zero_value_from_annotation(
    annotation: Any,
    *,
    seed: str,
    field_name: str,
) -> Any:
    from typing import Literal, Union, get_args, get_origin

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is Union:
        non_none = [arg for arg in args if arg is not type(None)]
        if len(non_none) < len(args):
            return None
        if non_none:
            return _zero_value_from_annotation(
                non_none[0], seed=seed, field_name=field_name
            )
    if origin is Literal:
        return args[0] if args else ""
    if origin in (list, tuple, set, frozenset):
        if origin is tuple and len(args) == 2 and args[1] is Ellipsis:
            return ()
        if origin is tuple and args:
            return tuple(
                _zero_value_from_annotation(arg, seed=seed, field_name=field_name)
                for arg in args
            )
        return origin()
    if origin is dict:
        return {}
    if annotation is str:
        if field_name == "free_text":
            # A turn's conversational field. The meeting manager
            # content-validates OPENING turns (Task 10.3, DESIGN.md §5.2
            # PHASE 1): accuse or explicitly declare "unsure". The fake's
            # minimal instance carries no claims, so its free_text declares
            # unsure -- keeping the fake a protocol-valid participant the
            # call site accepts on the first attempt (no synthetic
            # retry/default noise in CI meeting records). Deterministic per
            # prompt like every other fake field.
            return f"fake-free_text-{seed} (unsure)"
        return f"fake-{field_name}-{seed}"
    if annotation is int:
        return 0
    if annotation is float:
        return 0.0
    if annotation is bool:
        return False
    if annotation is bytes:
        return b""
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return _minimal_valid_instance(annotation, prompt=seed).model_dump()
    return _fallback_zero(annotation)


def _fallback_zero(annotation: Any) -> Any:
    try:
        return json.loads("null")
    except Exception:  # pragma: no cover - defensive
        return None


__all__ = ["FakeProvider"]
