"""Provider-neutral prompt cache (DESIGN.md §7).

Single-process, in-memory cache keyed on the engine-free pieces of an LLM
call: the rendered prompt text, the schema name (if any), the call kind,
and the max-tokens / temperature knobs. Anthropic-specific concepts such
as message-shape internals or ``cache_control`` markers never enter the
key — that is what makes the cache portable.

The cache is layered *above* :class:`~llm.client.LLMClient`:

::

    cache.get_or_call(client, prompt=..., schema=..., ...)

Misses call ``client.complete`` and store the result; hits return the
cached :class:`~llm.client.LLMResponse` without touching the underlying
client. The cache never mutates state inside the wrapped client.

The cache is intentionally bounded so a long-running orchestrator
process does not grow unbounded; the eviction policy is FIFO (least-
recently-inserted), which keeps replay-style workloads deterministic.
"""

from __future__ import annotations

import hashlib
from collections import OrderedDict
from typing import Final

from pydantic import BaseModel

from llm.client import CallKind, LLMClient, LLMResponse


_DEFAULT_MAX_ENTRIES: Final[int] = 1024


class PromptCache:
    """Bounded, provider-neutral prompt → response cache.

    Keys are SHA-256 digests over a canonical tuple of provider-agnostic
    inputs so two equivalent calls collide even when the caller passes
    schemas by import path. The cache stores immutable
    :class:`~llm.client.LLMResponse` instances and returns them directly;
    callers must not mutate them.
    """

    def __init__(self, *, max_entries: int = _DEFAULT_MAX_ENTRIES) -> None:
        if max_entries <= 0:
            raise ValueError(f"max_entries must be positive, got {max_entries}")
        self._max_entries = max_entries
        self._entries: OrderedDict[str, LLMResponse] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def __len__(self) -> int:
        return len(self._entries)

    @property
    def hits(self) -> int:
        return self._hits

    @property
    def misses(self) -> int:
        return self._misses

    def get(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind,
        model: str | None,
    ) -> LLMResponse | None:
        key = _make_key(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
        )
        entry = self._entries.get(key)
        if entry is None:
            self._misses += 1
            return None
        self._hits += 1
        return entry

    def put(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind,
        model: str | None,
        response: LLMResponse,
    ) -> None:
        key = _make_key(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
        )
        if key in self._entries:
            self._entries.pop(key)
        self._entries[key] = response
        while len(self._entries) > self._max_entries:
            self._entries.popitem(last=False)

    async def get_or_call(
        self,
        client: LLMClient,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
    ) -> LLMResponse:
        cached = self.get(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
        )
        if cached is not None:
            return cached
        response = await client.complete(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
        )
        self.put(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
            response=response,
        )
        return response

    def clear(self) -> None:
        self._entries.clear()
        self._hits = 0
        self._misses = 0


def _make_key(
    *,
    prompt: str,
    schema: type[BaseModel] | None,
    max_tokens: int,
    temperature: float,
    call_kind: CallKind,
    model: str | None,
) -> str:
    schema_id = _schema_identity(schema)
    payload = "|".join(
        (
            prompt,
            schema_id,
            str(max_tokens),
            f"{temperature:.6f}",
            call_kind,
            model if model is not None else "",
        )
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _schema_identity(schema: type[BaseModel] | None) -> str:
    if schema is None:
        return ""
    return f"{schema.__module__}.{schema.__qualname__}"


__all__ = ["PromptCache"]
