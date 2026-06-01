"""Parse-tolerance normalization for structured LLM reports (DESIGN.md §5, §6).

Real models — especially the local ``qwen2.5:7b-instruct`` Ollama provider from
Task 7.5 — emit JSON that is *almost* right but carries fields that do not
belong to the matched variant of a discriminated union. The canonical case
(diagnosed in the Phase 7 Ollama-enablement plan) is a ``co_present`` key on a
``found_body`` observation: ``co_present`` is valid on ``saw_player`` but not on
``found_body``. The meeting/report schemas (``meetings/schemas.py``) use
discriminated unions whose variants are ``frozen``/``extra="forbid"`` models, so
a misplaced key is a hard ``ValidationError`` — which today becomes a FailedCall
and a lost meeting.

This module exposes one pure function, :func:`normalize_report_payload`, that
salvages a near-miss payload into a valid one *before* validation. It performs
two complementary repairs at every discriminated-union point:

1. **Misplaced-key stripping** (the ``co_present`` case above): drop keys not
   declared on the matched variant so ``extra="forbid"`` no longer rejects them.
2. **Chronological-alibi repair** (Task 7.10, audit
   ``audits/audit-2026-06-01-1425-gameplay-data.md`` gp-2): when the matched
   variant declares both ``from_tick`` and ``to_tick`` (the
   ``meetings.schemas.AlibiClaim`` shape) and the payload has them reversed
   (``from_tick > to_tick``), swap them so the strict chronological
   ``model_validator`` accepts the claim. ``qwen2.5:7b-instruct`` emits this
   reversed range in ~6% of the committed 7p/2i set; left unrepaired the
   ``Statement`` validator raises and the whole game aborts with no
   ``game_over``. The schema's validator stays strict — the *input* is fixed
   here, never the schema (the ``AlibiClaim`` validator is unchanged).

It is deliberately:

* **Pure & deterministic** — a function of the parsed JSON value and the target
  schema only. No RNG, no clock, no network, no I/O. A recorded game therefore
  replays byte-identically, and the function is trivially unit-testable.
* **Conservative & discriminator-aware** — it resolves which union variant a
  payload matches via the schema's discriminator value, then drops *only* keys
  not declared on that variant and swaps a reversed ``from_tick``/``to_tick``
  pair *only* on a variant that declares both. It never invents or renames
  fields, never strips keys on a plain (non-union) model, and is a no-op on a
  payload that already validates and on a schema with no discriminated unions.
* **Transport-free** — it imports only the standard library and ``pydantic``
  (no ``engine``/``agents``/``meetings`` imports); the target schema is passed
  in by the caller (``llm/provider.py``), so the ``import-linter`` cross-layer
  contracts are untouched. The chronological repair is keyed on the variant's
  declared field *names*, not on importing ``AlibiClaim``.

Residual risk (intentionally NOT handled here): the normalizer TRUSTS the
discriminator value. A payload with a wrong/mismatched discriminator (e.g.
``type: saw_player`` on a ``found_body``-shaped body) is *not* repaired —
stripping to the named variant's fields is the most we do — so it remains a
FailedCall rather than being silently coerced. The normalizer never infers the
correct variant from body shape.
"""

from __future__ import annotations

import types
from typing import Any, Final, Union, get_args, get_origin

from pydantic import BaseModel


# ``X | Y`` (PEP 604) produces ``types.UnionType``; ``Union[X, Y]`` produces
# ``typing.Union``. The meeting schemas use the ``|`` form inside ``Annotated``,
# but accept both so the normalizer works for any caller's schema.
_UNION_ORIGINS: tuple[Any, ...] = (Union, types.UnionType)

# Field names that carry an inclusive, chronological tick range
# (``from_tick <= to_tick``). When a normalized variant declares BOTH, a
# reversed pair is swapped (see :func:`_repair_chronological_range`). Keyed on
# names, not on importing ``meetings.schemas.AlibiClaim``, so the normalizer
# stays transport-free and schema-agnostic.
_CHRONOLOGICAL_LOWER_FIELD: Final[str] = "from_tick"
_CHRONOLOGICAL_UPPER_FIELD: Final[str] = "to_tick"


def normalize_report_payload(payload: Any, schema: type[BaseModel]) -> Any:
    """Return ``payload`` with misplaced discriminated-union keys stripped.

    ``payload`` is a parsed JSON value (typically a ``dict`` for a model
    schema). ``schema`` is the target Pydantic model the caller is about to
    validate against. The function walks the schema's field annotations and, at
    every discriminated-union point, keeps only the keys declared on the variant
    selected by the discriminator value — dropping extras that would trip
    ``extra="forbid"``.

    Guarantees (see the module docstring and ``tests/llm/test_report_normalize``):

    * A payload that already validates is returned deep-equal to the input (the
      caller treats an unchanged result as a byte-identical no-op).
    * A schema with no discriminated unions is left untouched.
    * Missing required fields are NOT fabricated — a genuinely-invalid payload
      still fails loud at ``model_validate``.
    * A wrong/unknown discriminator value is left as-is (not repaired).
    """

    return _normalize(payload, schema)


def _normalize(value: Any, annotation: Any) -> Any:
    """Recursively normalize ``value`` against a type ``annotation``."""

    resolved = _resolve_discriminated_union(annotation)
    if resolved is not None and isinstance(value, dict):
        discriminator, variants = resolved
        discriminator_value = value.get(discriminator)
        try:
            variant = variants.get(discriminator_value)
        except TypeError:
            # A malformed discriminator (e.g. ``{"type": ["found_body"]}``) is
            # unhashable, so the dict lookup itself raises. Treat it as unknown
            # and leave the payload untouched so the downstream
            # ``model_validate_json`` raises the expected ``ValidationError``
            # (carrying failed-call metadata) rather than this pure helper
            # leaking a ``TypeError`` past the provider's validation ``try``.
            return value
        if variant is None:
            # Unknown / missing discriminator: we cannot safely pick a variant,
            # so leave the payload untouched (residual risk — see module
            # docstring). ``model_validate`` will raise the appropriate error.
            return value
        pruned = {
            key: _normalize(item, variant.model_fields[key].annotation)
            for key, item in value.items()
            if key in variant.model_fields
        }
        # After stripping misplaced keys, repair a reversed chronological tick
        # range on the matched variant (the AlibiClaim case; Task 7.10). This
        # is the only production path that reaches AlibiClaim, since meeting
        # claims are always nested inside the ``Claim`` discriminated union.
        return _repair_chronological_range(pruned, variant)

    core, _metadata = _unwrap_annotated(annotation)

    if (
        isinstance(core, type)
        and issubclass(core, BaseModel)
        and isinstance(value, dict)
    ):
        # Plain (non-union) model: recurse into KNOWN fields to reach nested
        # discriminated unions, but keep unknown keys verbatim. We do not strip
        # extras here — only discriminated-union variants are pruned — so a stray
        # top-level key still fails loud (conservative; the diagnosed failure is
        # a misplaced *variant* key, not a top-level one).
        return {
            key: (
                _normalize(item, core.model_fields[key].annotation)
                if key in core.model_fields
                else item
            )
            for key, item in value.items()
        }

    origin = get_origin(core)
    if origin in (list, tuple, set, frozenset) and isinstance(value, list):
        args = get_args(core)
        if origin is tuple and not (len(args) == 2 and args[1] is Ellipsis):
            # Fixed-length positional tuple: normalize element-wise by position.
            return [
                _normalize(item, args[index]) if index < len(args) else item
                for index, item in enumerate(value)
            ]
        element = args[0] if args else Any
        return [_normalize(item, element) for item in value]

    return value


def _repair_chronological_range(value: dict[Any, Any], model: type[BaseModel]) -> Any:
    """Swap a reversed ``from_tick``/``to_tick`` pair (Task 7.10, gp-2).

    Returns ``value`` unchanged unless ``model`` declares BOTH
    :data:`_CHRONOLOGICAL_LOWER_FIELD` and :data:`_CHRONOLOGICAL_UPPER_FIELD`
    (the ``meetings.schemas.AlibiClaim`` shape) AND the payload carries them as
    plain ``int``\\ s in the wrong order (``from_tick > to_tick``). In that one
    case it returns a shallow copy with the two values swapped, turning a
    reversed range into the chronological one the strict ``AlibiClaim``
    ``model_validator`` accepts.

    Swapping (rather than coercing to a one-tick window at ``to_tick``) keeps
    both tick values the model emitted, so DESIGN.md §5.4 contradiction
    detection — which indexes alibis by ``(subject, tick_range, location)`` —
    still has a meaningful window to match on. The repair is gated on the
    variant declaring both fields, so it never touches a model without a
    chronological range, and it only fires on the invalid ordering, so an
    already-chronological payload is returned unchanged (the byte-identical
    no-op the replay path depends on).

    Bools are excluded (``type(x) is int``, not ``isinstance``) because
    ``bool`` is an ``int`` subclass; a non-int / float value is left untouched
    so the downstream validator fails loud on it rather than this helper
    masking it (the normalizer never fabricates or coerces field *types*).
    """

    if not (
        _CHRONOLOGICAL_LOWER_FIELD in model.model_fields
        and _CHRONOLOGICAL_UPPER_FIELD in model.model_fields
    ):
        return value
    lower = value.get(_CHRONOLOGICAL_LOWER_FIELD)
    upper = value.get(_CHRONOLOGICAL_UPPER_FIELD)
    if type(lower) is int and type(upper) is int and lower > upper:
        repaired = dict(value)
        repaired[_CHRONOLOGICAL_LOWER_FIELD] = upper
        repaired[_CHRONOLOGICAL_UPPER_FIELD] = lower
        return repaired
    return value


def _unwrap_annotated(annotation: Any) -> tuple[Any, tuple[Any, ...]]:
    """Split ``Annotated[X, *meta]`` into ``(X, meta)``; pass others through."""

    if hasattr(annotation, "__metadata__"):
        args = get_args(annotation)
        return args[0], args[1:]
    return annotation, ()


def _resolve_discriminated_union(
    annotation: Any,
) -> tuple[str, dict[Any, type[BaseModel]]] | None:
    """Return ``(discriminator, {value: variant})`` for a discriminated union.

    Recognizes the ``Annotated[A | B | C, Field(discriminator="type")]`` shape
    the meeting schemas use: the discriminator name is read off the ``Annotated``
    metadata (any object exposing a string ``.discriminator``), and the
    value→variant map is built from each member model's discriminator ``Literal``.
    Returns ``None`` for anything that is not a usable discriminated union, so
    the caller leaves the value untouched.
    """

    core, metadata = _unwrap_annotated(annotation)
    discriminator = _discriminator_from_metadata(metadata)
    if discriminator is None:
        return None
    if get_origin(core) not in _UNION_ORIGINS:
        return None

    variants: dict[Any, type[BaseModel]] = {}
    for member in get_args(core):
        if member is type(None):
            continue
        if not (isinstance(member, type) and issubclass(member, BaseModel)):
            return None
        field = member.model_fields.get(discriminator)
        if field is None:
            continue
        for literal_value in get_args(field.annotation):
            variants[literal_value] = member
    if not variants:
        return None
    return discriminator, variants


def _discriminator_from_metadata(metadata: tuple[Any, ...]) -> str | None:
    """Return the first string ``.discriminator`` in ``Annotated`` metadata."""

    for meta in metadata:
        discriminator = getattr(meta, "discriminator", None)
        if isinstance(discriminator, str):
            return discriminator
    return None


__all__ = ["normalize_report_payload"]
