"""Featherless model x thinking-mode sweep over reconstructed 9p2i contexts (Task 14.4).

Operator-run, $0-marginal matrix driver. It runs each candidate Featherless
model over the SAME reconstructed opening/reply/vote contexts from the committed
``replays/samples/9p2i`` set, on the PINNED 9B prompts, and grades every cell
with the IDENTICAL mechanical detectors used for the 9B reference so the only
moving variable is the model (and, in the cover 2x2, the directive injection):

* **opening corpus** — the impostor self-report: the killer opens the meeting
  for their OWN kill (``impostor_report`` prompt, real reconstructed memory),
  graded by :func:`experiments.lab.deception_battery._grade_fabrication`
  (self-incrimination vs the engine-walk kill ground truth). Needs the extractor
  facts JSON (``--facts``) for the kill room/tick; skipped with a logged note
  when absent.
* **reply corpus** — the 16 hard impostor *reply* contexts frozen by
  :func:`experiments.lab.model_ceiling_probe._select` (a body was reported and an
  impostor must answer). Rendered through the production ``accusation_round``
  reply prompt and graded by :func:`experiments.lab.deflection_probe._grade`
  (``self_co_locates_body`` / ``new_self_flag`` / ``deflects_legal``). This is
  both the model-ceiling read (cover OFF across models) and one half of the
  cover 2x2.
* **cover 2x2** — the SAME reply contexts re-run with the gp-1 cover directive
  (:func:`experiments.lab.deflection_probe._cover_directive`) injected into
  rendered memory (cover ON), so each ``(model, {cover OFF, cover ON})`` cell is
  graded by the same detector — settling whether the self-incrimination tell is
  a capability ceiling, a prompt artifact, both, or the information ceiling.
* **vote corpus** — real vote-ballot decision contexts
  (:func:`experiments.model_probe.corpus.build_corpus`) rendered through the
  production vote prompt, scored for parse-success and conversion (did the voter
  pick an available impostor).

The corpus item IDs are PINNED ONCE and the SAME ids are re-rendered per
substrate cell, so a substrate comparison is a controlled re-render of
identical contexts, not a re-selection (vote selection in particular is
substrate-sensitive — its ``available_impostor`` gate reads the suspicion
graph — so pinning is load-bearing there).

HISTORICAL substrate axis: the 14.4 matrix ran every cell on BOTH the flag-OFF
(legacy) and the flag-ON (corrected 13.5) substrate, toggled via the four
``AILIBI_*`` env vars; the committed ``results-featherless-sweep.jsonl`` rows
retain that genuine two-column data and the report grouping still reads it.
Since Task 14.9 the four levers are unconditionally ON (their env gates are
retired), so the flag-OFF cohort can no longer be reconstructed: a NEW run is
single-substrate (all-ON) and requesting ``off`` fails loud
(:func:`_set_substrate`) instead of silently double-spending on a second
all-ON cohort mislabeled ``flag_off``. Each result row carries the
``substrate_flags`` config that produced its context. The Qwen3 models run in
both non-thinking and thinking mode (the request-time ``enable_thinking``
toggle, Task 14.1, threaded via
:func:`experiments.lab.probe_backends.call_turn`, Task 14.3).

9B-class reference: ``qwen3.5:9b`` is a local Ollama model off the hosted
endpoint, so the IN-SWEEP reference is its closest served Featherless analogue —
``Qwen/Qwen3-8B`` (same Qwen3 generation, nearest size, native
``enable_thinking``) — run over the SAME frozen contexts per substrate cell, so
the model-ceiling/information-ceiling read is controlled on identical contexts
(addresses the prior version's stale-9B mismatch). The committed Ollama
``results-model-ceiling-q9b.jsonl`` is folded only as a secondary HISTORICAL row
(prior recording; non-item-matched), clearly labelled.

Non-Qwen transport: the Task 14.1 adapter ALWAYS sends
``chat_template_kwargs.enable_thinking`` (the Qwen3 convention), which is honored
by the Qwen3 models but BREAKS the non-Qwen slate (GLM collapses to ``{}``,
Cydonia 400/504s). So the non-Qwen models are routed through a sweep-local BARE
send that omits that field and posts the same ``json_object`` request, then
parses through the SAME shared :func:`llm.provider._extract_json_block` +
``model_validate_json`` seam — giving their real structured-output fidelity
rather than a harness artifact. (The proper fix — making the field conditional —
belongs in ``llm/featherless_client.py``, which is out of scope for 14.4; this is
reported as adapter-compat feedback to 14.1/14.6.)

This module is READ-ONLY over the committed replays and CONSUMES the 14.2/14.3
seams without editing them.

Slate (HuggingFace repo form). Two of the contract's owner-confirmed ids
(``Qwen/Qwen3-30B-A3B``, ``zai-org/GLM-4-32B``) return a hard HTTP 404 from the
live endpoint as of 2026-06-29 — Featherless now serves the suffixed canonical
revisions ``Qwen/Qwen3-30B-A3B-Instruct-2507`` and ``zai-org/GLM-4-32B-0414``,
which ARE the MoE-speed and agentic models the contract names. The driver
confirms each id via a generation preflight before the run and substitutes the
served revision (documented in the PR ``Decisions``).

Usage (run as a module so the repo root is on the path)::

    # the kill ground truth for the opening corpus ($0, offline):
    PYTHONPATH=. uv run python audits/workflows/extract_gameplay_facts.py

    # full matrix (needs FEATHERLESS_API_KEY; concurrency<=2 — the plan caps at
    # 4 concurrency units and a 32B request costs 2):
    uv run python -m experiments.lab.featherless_sweep run \
        --sample-dir replays/samples/9p2i \
        --facts /tmp/ailibi-gameplay-facts-9p2i.json

    # (re)generate the report from the committed results:
    uv run python -m experiments.lab.featherless_sweep report

Phase-16 probe (Task 16.1)
==========================

A SEPARATE ``probe`` / ``probe-report`` pipeline probes the owner-directed
new-generation slate over the SAME committed contexts BEFORE any production
change, writing its OWN artifacts (``results-featherless-sweep-qwen3-6-27b.jsonl``
/ ``report-featherless-sweep-qwen3-6-27b.md``) so the 14.4 ``run`` / ``report``
path is byte-identical and untouched. The 16.1 contract text names qwen3.5-27b;
the owner redirected the probe mid-task (2026-07-11) to **Qwen/Qwen3.6-27B** plus
a second candidate **bottlecapai/ThinkingCap-Qwen3.6-27B**, so the artifact names
follow the actual slate. Four probe row kinds are recorded as JSONL evidence the
report regenerates every number from:

* ``served_id`` + ``no_go`` — a paced generation preflight per id form (pinned
  SLATE id first) is the arbiter of what is served; an unserved PINNED candidate
  is a first-class recorded NO-GO (never a crash), excluded from later passes.
* ``response_format`` — ``json_object`` AND strict ``json_schema`` over both
  production schemas, two attempts each (deterministic rejection vs transient
  load).
* ``thinking_kwarg`` — the ``enable_thinking`` posture per id (absent/false/true)
  and WHICH channel carries reasoning (``reasoning_content`` / ``reasoning`` /
  the Qwen3.6 inline ``</think>``-close shape) — the evidence a Task 16.12
  registry entry will encode.
* the graded matrix — the served specs re-rendered through the EXISTING
  ``qwen3_32b`` prompt set (held constant; the bespoke 3.6 set is 16.13's) on
  BOTH thinking modes, via the unmodified ``run_sweep``.

The new-generation ids are NOT in the production ``_THINKING_KWARG_BY_MODEL``
registry (that fail-loud entry is Task 16.12's, post-lock), so the adapter would
fail loud on them; the matrix routes an unregistered id through a sweep-local send
(``_probe_send``) that carries the Qwen kwarg and splits the inline reasoning.

Usage::

    # probe (needs FEATHERLESS_API_KEY; hours-scale, $0 flat-rate):
    uv run python -m experiments.lab.featherless_sweep probe \
        --sample-dir replays/samples/9p2i \
        --facts /tmp/ailibi-gameplay-facts-9p2i.json

    # (re)generate the probe report from the committed probe rows:
    uv run python -m experiments.lab.featherless_sweep probe-report
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import statistics
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Final, Generic, TypeVar

from pydantic import BaseModel, ValidationError

from agents.strategic.prompts.loader import (
    DEFAULT_PROMPT_SET,
    PromptRenderers,
    build_prompt_renderers,
)
from experiments.lab.deception_battery import (
    KillContext,
    ReplyContext,
    _grade_fabrication,
    build_kill_contexts,
)
from experiments.lab.deflection_probe import _body, _cover_directive, _grade
from experiments.lab.model_ceiling_probe import _select
from experiments.lab.probe_backends import (
    active_substrate_flags,
    call_turn,
    resolve_featherless_base_url,
)
from experiments.model_probe.corpus import CorpusItem, build_corpus
from experiments.model_probe.probe import select_corpus
from llm.featherless_client import (
    FeatherlessRawResponse,
    _THINKING_KWARG_BY_MODEL,
    _raw_from_response_body,
    _send_with_retry,
)
from llm.provider import _extract_json_block
from meetings.schemas import MeetingTurn, VoteBallot

WORK: Final[Path] = Path("experiments/lab")
RESULTS: Final[Path] = WORK / "results-featherless-sweep.jsonl"
REPORT: Final[Path] = WORK / "report-featherless-sweep.md"
# Committed Ollama 9B data (PRIOR recording) — folded only as a HISTORICAL row.
REF_REPLY: Final[Path] = WORK / "results-model-ceiling-q9b.jsonl"
REF_COVER: Final[Path] = WORK / "results-deflection-probe.jsonl"

# ── Phase-16 probe (Task 16.1) artifacts + slate constants ──
# The probe writes its OWN jsonl/report so it can NEVER clobber the committed 14.4
# matrix (RESULTS / REPORT) — the `run`/`report` subcommands stay byte-identical.
# Artifact names follow the ACTUAL owner-directed slate (2026-07-11): the 16.1
# contract text names qwen3.5-27b, but the owner redirected the probe mid-task to
# Qwen3.6-27B (plus bottlecapai/ThinkingCap-Qwen3.6-27B), so the filenames pin the
# generation actually probed.
PROBE_RESULTS: Final[Path] = WORK / "results-featherless-sweep-qwen3-6-27b.jsonl"
PROBE_REPORT: Final[Path] = WORK / "report-featherless-sweep-qwen3-6-27b.md"
# The probe renders through the incumbent's EXISTING bespoke set (a deliberate
# 16.1 finding — the bespoke 3.6 set is Task 16.13's), held CONSTANT across both
# matrix models and BOTH thinking modes (mode is the controlled axis).
PROBE_PROMPT_SET: Final[str] = "qwen3_32b"
# The two owner-directed candidates (matrix + preflight); the incumbent is the
# same-day re-verified baseline the candidates are read against.
PROBE_CANDIDATE_LABELS: Final[tuple[str, ...]] = ("qwen3-6-27b", "thinkingcap-27b")
PROBE_INCUMBENT_LABEL: Final[str] = "qwen3-32b"
# Every probe-scoped label (candidates + incumbent), used to slice the SLATE.
_PROBE_LABELS: Final[tuple[str, ...]] = (
    *PROBE_CANDIDATE_LABELS,
    PROBE_INCUMBENT_LABEL,
)
# label -> id forms the served-id pass tries, PINNED SLATE id FIRST. Qwen3.6-27B
# is served (HTTP 200); its `-Instruct` suffix is NOT in the catalog (404) — we
# record it anyway so the report shows the preflight, not a guess, is the arbiter.
# ThinkingCap has ONE form (its slate id), whose deployment 400s deterministically.
_PROBE_ID_FORMS: Final[dict[str, tuple[str, ...]]] = {
    "qwen3-6-27b": ("Qwen/Qwen3.6-27B", "Qwen/Qwen3.6-27B-Instruct"),
    "thinkingcap-27b": ("bottlecapai/ThinkingCap-Qwen3.6-27B",),
}

# Production turn caps (the deployed sim's frozen backstop) — recorded for
# reference only; the PROBE does NOT constrain models to these, it measures each
# model's BEST-SHOT result (see _profile below).
PROD_TURN_CAP: Final[int] = 2048
PROD_VOTE_CAP: Final[int] = 1024
TEMPERATURE: Final[float] = 0.4
VOTE_TEMPERATURE: Final[float] = 0.0
# The harness discards reasoning explicitly so a reasoning model does not abort
# the sweep (probe-side default; the recorded baseline at 14.7 uses fail_loud).
THINKING_POLICY: Final[str] = "strip"

# ── Best-shot probe call profiles (owner decision 2026-06-29) ──
# The probe's job is to rank how well each model performs on the corpus, so each
# model/mode is called with the settings MOST LIKELY TO SUCCEED, not the 9B-era
# 2048 / json_object handicap. The OUTPUT (the parsed MeetingTurn / VoteBallot)
# is schema-identical regardless, so downstream graders / consumers are unchanged
# — only the LLM-call knobs vary, and reasoning is DISCARDED (never recorded), so
# it cannot leak into game state.
#
# * THINKING rows: ``response_format=none`` (json_object SUPPRESSES Qwen3
#   reasoning — calibrated 2026-06-29: out=243 vs 3187 tokens), so the model
#   actually reasons; the ``<think>`` block is stripped before extract→validate.
#   A generous 16384 generation budget so reasoning (observed ~3.2k–4.7k tokens)
#   + the answer never truncate, while staying inside the 32K context (~4k input).
# * NON-THINKING rows: ``json_object`` forces JSON-first output; a 4096 budget
#   (headroom over the ~250–500-token turns) removes the rare non-thinking
#   truncation. The recorded answer still fits the production 2048 turn cap.
THINK_BUDGET: Final[int] = 16384
NONTHINK_BUDGET: Final[int] = 4096


def _profile(request_thinking: bool) -> tuple[str, int]:
    """Best-shot ``(response_format_mode, max_tokens)`` for the given mode."""

    if request_thinking:
        return "none", THINK_BUDGET
    return "json_object", NONTHINK_BUDGET


# The in-sweep 9B-class reference (closest served analogue of ``qwen3.5:9b``).
REFERENCE_LABEL: Final[str] = "qwen3-8b"

# The Featherless plan also limits how often the account may SWITCH the active
# model (observed: "switch models 4 times per minute"). The sweep is structured
# model-outer (each model does ALL its work before the next), so switches are
# naturally minutes apart — but preflight (and the first loaded model) can bunch,
# so a pacer enforces a minimum gap between switches to a DIFFERENT model.
MIN_SWITCH_INTERVAL_S: Final[float] = 20.0

# Bounded retry on transport exceptions (network outage / connection reset) that
# the HTTP-status retry in ``_send_with_retry`` does not cover — so a brief blip
# mid-run does not turn a whole model's cells into recorded ConnectErrors.
_TURN_MAX_ATTEMPTS: Final[int] = 4
_TURN_RETRY_BACKOFF_S: Final[float] = 5.0
# Hard per-attempt ceiling on ONE transport await. The 2026-07-11 probe run
# wedged permanently: two in-flight calls lost their sockets without httpx's own
# 600s deadline ever firing (event loop idle in select, zero ESTABLISHED
# connections, no timer converging), and every queued cell then waited on the
# semaphore forever. This ceiling sits ABOVE the stack's 600s deadline plus its
# bounded internal retries, so it only fires on exactly that pathology — the
# attempt is then recorded/retried as a normal transport failure (TimeoutError)
# instead of hanging the matrix.
_TURN_ATTEMPT_CEILING_S: Final[float] = 1200.0

ModelT = TypeVar("ModelT", bound=BaseModel)


class _SwitchPacer:
    """Enforce a minimum interval between switches to a different model id."""

    def __init__(self, interval_s: float = MIN_SWITCH_INTERVAL_S) -> None:
        self._interval = interval_s
        self._last = 0.0
        self._current: str | None = None

    def touch(self, model: str) -> None:
        if model == self._current:
            return
        if self._current is not None:
            wait = self._interval - (time.monotonic() - self._last)
            if wait > 0:
                print(
                    f"  pacing model switch -> {model}: sleeping {wait:.0f}s "
                    "(4 switches/min plan limit)",
                    flush=True,
                )
                time.sleep(wait)
        self._last = time.monotonic()
        self._current = model


@dataclass(frozen=True)
class ModelSpec:
    """One slate model: served id, short label, mode axis, transport, role."""

    model_id: str
    label: str
    # Run the non-thinking AND thinking modes (the request-time enable_thinking
    # sweep axis)? Only the Qwen3 chat models have a meaningful axis.
    thinking_axis: bool
    # Send ``chat_template_kwargs.enable_thinking`` (the Qwen3 convention, via the
    # 14.1 adapter / ``call_turn``)? FALSE routes through the sweep-local BARE
    # send that omits the field — required for the non-Qwen slate, which the
    # adapter's mandatory field otherwise breaks.
    qwen_kwarg: bool
    # "candidate" (eligible for the recommended tuple) or "reference" (the
    # 9B-class baseline, excluded from the recommendation).
    role: str = "candidate"


# The slate the contract pins, plus the 9B-class reference, with the two 404'd
# ids substituted by their served canonical revisions. Order = report order.
SLATE: Final[tuple[ModelSpec, ...]] = (
    ModelSpec(
        "Qwen/Qwen3-8B",
        REFERENCE_LABEL,
        # The contract wants the 9B-class reference in BOTH modes where available;
        # Qwen3-8B honors enable_thinking, so run the thinking axis too — its
        # thinking row matches the candidate Qwen thinking rows on identical
        # contexts.
        thinking_axis=True,
        qwen_kwarg=True,
        role="reference",
    ),
    ModelSpec("Qwen/Qwen3-32B", "qwen3-32b", thinking_axis=True, qwen_kwarg=True),
    ModelSpec(
        "Qwen/Qwen3-30B-A3B-Instruct-2507",
        "qwen3-30b-a3b",
        thinking_axis=True,
        qwen_kwarg=True,
    ),
    ModelSpec(
        "zai-org/GLM-4-32B-0414", "glm-4-32b", thinking_axis=False, qwen_kwarg=False
    ),
    ModelSpec(
        "TheDrummer/Cydonia-24B-v2",
        "cydonia-24b",
        thinking_axis=False,
        qwen_kwarg=False,
    ),
    # ── Phase-16 probe candidates (Task 16.1; owner-directed slate 2026-07-11) ──
    # Appended AFTER Cydonia so every existing 14.4 table ordering (SLATE-index
    # keyed) is untouched, and excluded from the `run` default so `run` stays
    # byte-identical — the `probe` subcommand selects them explicitly.
    #
    # qwen3-6-27b honors `enable_thinking` (verified live 2026-07-11 — false gives
    # a clean answer, true/absent reasons) so it carries the thinking axis and
    # `qwen_kwarg=True`; but it is NOT in the production registry
    # (`_THINKING_KWARG_BY_MODEL`), so the adapter fails loud on it and the
    # sweep-local `_probe_send` carries the kwarg instead (the fail-loud registry
    # entry is Task 16.12's, post-lock).
    ModelSpec("Qwen/Qwen3.6-27B", "qwen3-6-27b", thinking_axis=True, qwen_kwarg=True),
    # thinkingcap-27b's deployment 400s on `chat_template_kwargs` — and, live, on
    # EVERY generation ("Chat template is passed with request, but
    # --trust-request-chat-template is not set") — so it is declared BARE like the
    # non-Qwen slate (no axis, no kwarg) and the probe records its NO-GO.
    ModelSpec(
        "bottlecapai/ThinkingCap-Qwen3.6-27B",
        "thinkingcap-27b",
        thinking_axis=False,
        qwen_kwarg=False,
    ),
)


# Each Task 14.5 bespoke set is authored for ONE (model, mode). The A/B is "each
# set vs pinned-9B on its OWN model" and the report groups rows by ``prompt_set``,
# so a ``--prompt-set`` run MUST target only that owner model/mode — otherwise the
# bespoke templates render across the whole slate and stamp invalid comparison rows
# after a multi-hour run. Maps set -> (owner model label, owner request-thinking).
_SET_OWNER: Final[dict[str, tuple[str, bool]]] = {
    "qwen3_32b": ("qwen3-32b", False),
    "qwen3_32b_thinking": ("qwen3-32b", True),
    "qwen3_30b_a3b": ("qwen3-30b-a3b", False),
    "glm_4_32b": ("glm-4-32b", False),
    "cydonia_24b": ("cydonia-24b", False),
}


@dataclass
class SweepConfig:
    """Knobs for one sweep invocation."""

    sample_dir: Path
    facts_path: Path | None = None
    reply_cap: int = 16
    vote_limit: int = 8
    opening_cap: int = 10
    # Plan concurrency limit is 4 UNITS and a 32B request costs 2 units, so the
    # safe default is 2 concurrent requests (>2 turns valid cells into 429s).
    concurrency: int = 2
    latency_samples: int = 2
    # Single all-ON cohort since Task 14.9 (the flag-OFF substrate is retired;
    # ``_set_substrate`` fails loud on a ``False`` request).
    substrates: tuple[bool, ...] = (True,)
    base_url: str | None = None
    # Where ``run_sweep`` streams result rows. Defaults to the committed 14.4
    # RESULTS constant so ``run`` stays byte-identical; the Task 16.1 probe points
    # it at PROBE_RESULTS so the probe matrix never touches the 14.4 jsonl.
    results_path: Path = RESULTS
    models: tuple[ModelSpec, ...] = SLATE
    # Append to the results file instead of truncating — used to re-run a single
    # model (``--models``) after an environment outage and merge it back, rather
    # than repeating the whole multi-hour matrix.
    append: bool = False
    # The prompt SET to render through (Task 14.5 A/B axis). ``None`` keeps the
    # 14.4 behavior byte-identical: the import-time default set (the pinned 9B
    # templates) renders, and the non-Qwen slate routes through the sweep-local
    # ``_bare_send``. A non-``None`` set renders the BESPOKE templates via
    # ``build_prompt_renderers`` and routes the non-Qwen slate through the REAL
    # adapter (``call_turn``) — the 14.4.1 fix having retired the bare-send
    # workaround for them. Every row is stamped with the resolved ``prompt_set``.
    prompt_set: str | None = None
    # Restrict the thinking axis to these request-thinking values (Task 14.5): a
    # bespoke set maps to ONE (model, mode), so the non-thinking ``qwen3_32b`` set
    # runs ``--modes non_thinking`` and the ``qwen3_32b_thinking`` set runs
    # ``--modes thinking`` on the same model. ``None`` keeps the full per-model
    # axis (the 14.4 behavior). Intersected with each spec's own axis.
    mode_filter: tuple[bool, ...] | None = None


@dataclass(frozen=True)
class TurnOutcome(Generic[ModelT]):
    """Normalized outcome of one model call, transport-agnostic."""

    parsed: ModelT | None
    raw_text: str
    latency_s: float
    in_tokens: int
    out_tokens: int
    thinking_chars: int
    error: str | None
    parse_error: str | None


@dataclass(frozen=True)
class RenderBinding:
    """How one sweep run renders + routes its turns (Task 14.5 ``--prompt-set``).

    Built ONCE per run and threaded into every cell so the render set, the row
    ``prompt_set`` stamp, the transport choice, and the reply cover-directive
    gate move together. The no-flag default (``--prompt-set`` absent) reproduces
    the 14.4 behavior byte-identically: the pinned 9B templates render, the
    non-Qwen slate routes through ``_bare_send``, and impostor replies render
    ``is_impostor=False`` (the 9B reply template carries no cover directive).
    """

    renderers: PromptRenderers
    # The resolved set name (the bespoke set, or DEFAULT_PROMPT_SET on a no-flag
    # run). Stamped on a row ONLY when ``is_bespoke`` (see below).
    prompt_set: str
    # Is this an explicit ``--prompt-set`` (bespoke) run? Drives ALL three
    # divergences from the 14.4 default path, so the no-flag path stays
    # byte-identical: (1) the row ``prompt_set`` stamp is added ONLY when bespoke
    # (a no-flag row omits the field entirely — the committed 14.4 rows have no
    # such key, and ``_prompt_set_of`` reads a missing field as the default set,
    # so a no-flag re-run reproduces the prior JSONL byte-for-byte); (2) the
    # non-Qwen slate routes through the real adapter; (3) impostor replies render
    # ``is_impostor=True`` to fire the wired cover directive.
    is_bespoke: bool
    # Route the non-Qwen slate through the real adapter (``call_turn``) instead of
    # ``_bare_send``? True only for a bespoke set — the 14.4.1 fix retired the
    # bare-send workaround for GLM / Cydonia in the re-sweep.
    force_adapter: bool
    # Render impostor replies with ``is_impostor=True`` so a bespoke set's wired
    # reply cover directive fires (the reply corpus is impostor-only). False for
    # the default set keeps the 9B reply render byte-identical.
    reply_is_impostor: bool


def _binding_for(cfg: SweepConfig) -> RenderBinding:
    """Resolve the render binding for one sweep run from its ``prompt_set``.

    The sweep's ``--prompt-set`` axis is EXPLICIT and does NOT inherit the ambient
    ``AILIBI_PROMPT_SET`` selector: a no-flag run is ALWAYS the pinned-9B baseline
    (byte-identical 14.4 behavior) even when ``AILIBI_PROMPT_SET`` is exported in
    the environment — which the 14.7 re-record workflow does. Binding the renderers
    to an EXPLICIT set name (``DEFAULT_PROMPT_SET`` when the flag is absent) rather
    than resolving ``None`` through the env var is what keeps the default path's
    render + row stamping + transport from silently flipping to a bespoke set (and
    so keeps the committed 14.4 report regenerating byte-identically).
    """

    bespoke = cfg.prompt_set is not None
    set_name = cfg.prompt_set if cfg.prompt_set is not None else DEFAULT_PROMPT_SET
    return RenderBinding(
        renderers=build_prompt_renderers(set_name),
        prompt_set=set_name,
        is_bespoke=bespoke,
        force_adapter=bespoke,
        reply_is_impostor=bespoke,
    )


def _set_substrate(flag_on: bool) -> dict[str, bool]:
    """Return the active substrate config for a sweep cell (all-ON since 14.9).

    The four 13.5 levers are unconditionally ON since Task 14.9 (their env
    gates are retired), so the legacy flag-OFF cohort can no longer be
    reconstructed. Requesting it fails loud here — BEFORE any context
    reconstruction or model spend — rather than silently deriving a second
    all-ON cohort that the ``substrate_flags`` row label would mark
    ``flag_on`` while the matrix believed it ran ``flag_off`` (AGENTS.md "no
    silent fallbacks"). The committed results keep their genuine pre-14.9
    ``flag_off`` rows; only NEW runs are single-substrate.
    """

    if not flag_on:
        raise SystemExit(
            "substrate 'off' is retired: the four 13.5 levers are "
            "unconditionally ON since Task 14.9, so a flag-OFF context can no "
            "longer be reconstructed. Run with --substrates on."
        )
    return active_substrate_flags()


def _modes_for(
    spec: ModelSpec, mode_filter: tuple[bool, ...] | None = None
) -> tuple[bool, ...]:
    """Request-thinking values to run for ``spec`` (the non-thinking/thinking axis).

    ``mode_filter`` (Task 14.5) intersects the spec's own axis so a bespoke set's
    A/B runs only its one mode; ``None`` keeps the full per-model axis (14.4). A
    filter that excludes every axis value yields an empty tuple (the model is then
    a no-op for that run — e.g. asking GLM for thinking-only).
    """

    axis = (False, True) if spec.thinking_axis else (False,)
    if mode_filter is None:
        return axis
    return tuple(m for m in axis if m in mode_filter)


def _mode_label(request_thinking: bool) -> str:
    return "thinking" if request_thinking else "non_thinking"


async def _bare_send(
    *,
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    response_format: dict[str, Any] | None,
    max_tokens: int,
    temperature: float,
) -> Any:
    """A Featherless POST that OMITS ``chat_template_kwargs`` (non-Qwen path).

    Reuses the production bounded-retry (:func:`_send_with_retry`) + body mapping
    (:func:`_raw_from_response_body`) so the only difference from the 14.1 adapter
    is the omitted Qwen-only thinking field — exactly the field that breaks the
    non-Qwen slate. Returns a ``FeatherlessRawResponse``.
    """

    import httpx

    payload: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if response_format is not None:
        payload["response_format"] = response_format
    url = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    async with httpx.AsyncClient() as client:

        async def _post() -> httpx.Response:
            return await client.post(
                url, headers=headers, json=payload, timeout=httpx.Timeout(600.0)
            )

        body = await _send_with_retry(_post, model=model)
    return _raw_from_response_body(body, model=model)


async def _probe_send(
    *,
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    response_format: dict[str, Any] | None,
    max_tokens: int,
    temperature: float,
    request_thinking: bool,
    send_kwarg: bool,
) -> FeatherlessRawResponse:
    """Sweep-local send for an UNREGISTERED new-generation id (Task 16.1).

    This is the 16.1 stand-in for the Task 16.12 registry entry. The production
    adapter (``llm/featherless_client.py``) fails loud via
    :func:`_supports_thinking_kwarg` on any id NOT in
    :data:`_THINKING_KWARG_BY_MODEL`, and ``llm/`` is out of scope pre-lock, so a
    new-generation candidate CANNOT route through ``call_turn``. This send carries
    the Qwen kwarg (and the Qwen3.6 inline ``</think>``-close-only reasoning shape)
    sweep-locally instead:

    * ``chat_template_kwargs.enable_thinking`` is included IFF ``send_kwarg`` (the
      spec's ``qwen_kwarg``); an empty ``{}`` object is OMITTED entirely — that
      empty object is exactly what broke GLM in 14.4.
    * the response BODY is mapped so the Qwen3.5-style ``message.reasoning``
      side-channel is not silently dropped: :func:`_raw_from_response_body`
      supplies the fail-loud guards + token counters (it reads only
      ``reasoning_content``), then the raw ``message.reasoning`` key is merged in
      (``reasoning_content = raw.reasoning_content or that``). The Qwen3.6 INLINE
      reasoning (a bare ``</think>`` close in ``content``) is split by the caller.

    Reuses the production bounded-retry (:func:`_send_with_retry`) so transient
    5xx/429s are handled identically to the real adapter. The fail-loud
    ``_THINKING_KWARG_BY_MODEL`` classification is Task 16.12's, post-lock.
    """

    import httpx

    payload: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if send_kwarg:
        payload["chat_template_kwargs"] = {"enable_thinking": request_thinking}
    if response_format is not None:
        payload["response_format"] = response_format
    url = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    async with httpx.AsyncClient() as client:

        async def _post() -> httpx.Response:
            return await client.post(
                url, headers=headers, json=payload, timeout=httpx.Timeout(600.0)
            )

        body = await _send_with_retry(_post, model=model)
    raw = _raw_from_response_body(body, model=model)
    # Recover the Qwen3.5-style ``message.reasoning`` channel that
    # ``_raw_from_response_body`` does NOT read (it reads only ``reasoning_content``,
    # the incumbent Qwen3-32B channel). Carrying it here keeps the new-generation
    # reasoning out of the recorded ANSWER without a production adapter change.
    message = body["choices"][0].get("message") or {}
    side_reasoning = message.get("reasoning") or ""
    reasoning_content = raw.reasoning_content or side_reasoning
    if reasoning_content == raw.reasoning_content:
        return raw
    return FeatherlessRawResponse(
        text=raw.text,
        model=raw.model,
        prompt_tokens=raw.prompt_tokens,
        completion_tokens=raw.completion_tokens,
        reasoning_content=reasoning_content,
    )


def _registry_knows(model_id: str) -> bool:
    """Exact-id membership in the production ``_THINKING_KWARG_BY_MODEL`` registry.

    The production adapter fails loud via :func:`_supports_thinking_kwarg` on any
    id NOT in this registry, so this predicate is how :func:`_run_turn` decides
    whether a spec can route through the production ``call_turn`` adapter (a
    registered id) or must use the sweep-local :func:`_probe_send` transport (an
    unregistered new-generation id). ``llm/`` is out of scope for Task 16.1 — the
    fail-loud registry entry for the new generation is Task 16.12's, post-lock.
    """

    return any(model_id == known_id for known_id, _ in _THINKING_KWARG_BY_MODEL)


def _split_inline_think(text: str) -> tuple[str, str]:
    """Split Qwen3.6-style inline reasoning from the answer; ``(answer, reasoning)``.

    Qwen3.6-27B surfaces reasoning INLINE in ``message.content`` terminated by a
    bare ``</think>`` CLOSE tag — with NO ``<think>`` OPEN tag and NO
    ``reasoning_content`` side-channel (verified live 2026-07-11; contrast the
    incumbent Qwen3-32B, which uses the ``reasoning_content`` channel). Split on
    the LAST ``</think>`` (``rsplit`` maxsplit=1) so a stray close tag inside the
    reasoning does not truncate the answer: everything after it is the answer
    (lstripped), everything before is the reasoning, with a leading ``<think>``
    open tag peeled if present. With no close tag the whole text is the answer and
    the reasoning is empty.
    """

    close, open_ = "</think>", "<think>"
    if close not in text:
        return text, ""
    reasoning, answer = text.rsplit(close, 1)
    if reasoning.startswith(open_):
        reasoning = reasoning[len(open_) :]
    return answer.lstrip(), reasoning


def _parse(schema: type[ModelT], text: str) -> tuple[ModelT | None, str | None]:
    """Shared extract -> validate path; ``(parsed, parse_error)``."""

    try:
        return schema.model_validate_json(_extract_json_block(text, schema)), None
    except ValidationError as exc:
        return None, str(exc)


async def _run_turn(
    spec: ModelSpec,
    prompt: str,
    schema: type[ModelT],
    *,
    request_thinking: bool,
    max_tokens: int,
    temperature: float,
    response_format_mode: str,
    flags: Mapping[str, bool],
    api_key: str,
    base_url: str | None,
    sem: asyncio.Semaphore,
    force_adapter: bool = False,
) -> TurnOutcome[ModelT]:
    """Run one model call via the right transport; never raises.

    Three routes, chosen so REGISTERED-model behavior is BYTE-IDENTICAL to 14.4:

    * REGISTERED Qwen3 / force-adapter models — ``(qwen_kwarg or force_adapter)``
      AND :func:`_registry_knows` — go through ``call_turn`` (the 14.1 adapter,
      sending ``chat_template_kwargs.enable_thinking`` — the real thinking axis).
      The 14.4.1 fix made the adapter omit the Qwen-only field for the non-Qwen
      slate, so a bespoke-set re-sweep (Task 14.5) iterates the REAL client.
    * UNREGISTERED new-generation ids (Task 16.1) — ``not _registry_knows`` —
      route through the sweep-local :func:`_probe_send`: the production adapter
      fails loud on an unclassified id and ``llm/`` is out of scope pre-lock, so
      the probe carries the Qwen kwarg (gated on ``qwen_kwarg``) and the Qwen3.6
      inline ``</think>``-close reasoning shape sweep-locally. The fail-loud
      registry entry is Task 16.12's, post-lock.
    * REGISTERED non-Qwen models without ``force_adapter`` — go through
      :func:`_bare_send` (omitting the Qwen-only field), unchanged from 14.4.

    All three route the response through the shared extract -> validate seam.
    """

    resolved = base_url if base_url is not None else resolve_featherless_base_url()
    async with sem:
        # Bounded retry on TRANSPORT exceptions (e.g. ``httpx.ConnectError`` from
        # a brief network outage — which a multi-hour run is exposed to and which
        # ``_send_with_retry`` does NOT cover, as it only retries HTTP statuses,
        # not connection failures). A schema-invalid body is NOT an exception
        # here (``_parse`` returns it as ``parse_error``), so this only retries
        # genuine transport failures; the last error is recorded if all fail.
        last_exc: Exception | None = None
        for attempt in range(_TURN_MAX_ATTEMPTS):
            started = time.perf_counter()
            try:
                # Every transport await sits under the _TURN_ATTEMPT_CEILING_S
                # wedge guard: a call whose socket silently dies without the
                # stack's own 600s deadline firing becomes a recorded/retried
                # TimeoutError here instead of hanging the gather (and, through
                # the shared semaphore, the whole matrix) forever.
                async with asyncio.timeout(_TURN_ATTEMPT_CEILING_S):
                    if (spec.qwen_kwarg or force_adapter) and _registry_knows(
                        spec.model_id
                    ):
                        r = await call_turn(
                            prompt,
                            schema,
                            backend="featherless",
                            model=spec.model_id,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            api_key=api_key,
                            base_url=base_url,
                            request_thinking=request_thinking,
                            thinking_policy=THINKING_POLICY,  # type: ignore[arg-type]
                            response_format_mode=response_format_mode,  # type: ignore[arg-type]
                            substrate_flags=flags,
                        )
                        return TurnOutcome(
                            parsed=r.parsed,
                            raw_text=r.raw_text,
                            latency_s=r.latency_s,
                            in_tokens=r.in_tokens,
                            out_tokens=r.out_tokens,
                            thinking_chars=r.thinking_chars,
                            error=None,
                            parse_error=r.parse_error,
                        )
                    if not _registry_knows(spec.model_id):
                        # Unregistered new-generation id (Task 16.1): the production
                        # adapter would fail loud on it, so the sweep-local probe send
                        # carries the Qwen kwarg (iff ``qwen_kwarg``) and recovers the
                        # 3.6 inline ``</think>``-close reasoning out of the answer.
                        praw = await _probe_send(
                            base_url=resolved,
                            api_key=api_key,
                            model=spec.model_id,
                            prompt=prompt,
                            response_format=(
                                None
                                if response_format_mode == "none"
                                else {"type": response_format_mode}
                            ),
                            max_tokens=max_tokens,
                            temperature=temperature,
                            request_thinking=request_thinking,
                            send_kwarg=spec.qwen_kwarg,
                        )
                        latency = time.perf_counter() - started
                        answer, inline = _split_inline_think(praw.text)
                        parsed, parse_error = _parse(schema, answer)
                        return TurnOutcome(
                            parsed=parsed,
                            # The STRIPPED answer, never praw.text: on a parse
                            # failure _record_outcome commits raw_head from
                            # raw_text, and the inline reasoning prefix must not
                            # leak into the jsonl (reasoning is discarded, never
                            # recorded — its length survives in thinking_chars).
                            raw_text=answer,
                            latency_s=latency,
                            in_tokens=praw.prompt_tokens,
                            out_tokens=praw.completion_tokens,
                            thinking_chars=len(praw.reasoning_content) + len(inline),
                            error=None,
                            parse_error=parse_error,
                        )
                    raw = await _bare_send(
                        base_url=resolved,
                        api_key=api_key,
                        model=spec.model_id,
                        prompt=prompt,
                        response_format=(
                            None
                            if response_format_mode == "none"
                            else {"type": response_format_mode}
                        ),
                        max_tokens=max_tokens,
                        temperature=temperature,
                    )
                    latency = time.perf_counter() - started
                    parsed, parse_error = _parse(schema, raw.text)
                    return TurnOutcome(
                        parsed=parsed,
                        raw_text=raw.text,
                        latency_s=latency,
                        in_tokens=raw.prompt_tokens,
                        out_tokens=raw.completion_tokens,
                        thinking_chars=len(raw.reasoning_content),
                        error=None,
                        parse_error=parse_error,
                    )
            except Exception as exc:  # noqa: BLE001 — record transport failures, don't abort
                last_exc = exc
                if attempt < _TURN_MAX_ATTEMPTS - 1:
                    await asyncio.sleep(_TURN_RETRY_BACKOFF_S * (attempt + 1))
        return TurnOutcome(
            parsed=None,
            raw_text="",
            latency_s=0.0,
            in_tokens=0,
            out_tokens=0,
            thinking_chars=0,
            error=f"{type(last_exc).__name__}: {last_exc}"[:240],
            parse_error=None,
        )


def _base_row(
    *,
    corpus: str,
    spec: ModelSpec,
    request_thinking: bool,
    flags: Mapping[str, bool],
    response_format_mode: str,
    max_tokens: int,
    binding: RenderBinding,
) -> dict[str, Any]:
    # The transport stamp mirrors _run_turn's ACTUAL route, not just the spec
    # axes: an id absent from the production registry rides the sweep-local
    # _probe_send regardless of qwen_kwarg/force_adapter (the adapter would
    # fail loud on it), and stamping it "adapter" would misstate how the row
    # was produced to the 16.2 lock.
    if not _registry_knows(spec.model_id):
        transport = "probe_send"
    elif spec.qwen_kwarg or binding.force_adapter:
        transport = "adapter"
    else:
        transport = "bare"
    row: dict[str, Any] = {
        "corpus": corpus,
        "model": spec.model_id,
        "label": spec.label,
        "role": spec.role,
        "mode": _mode_label(request_thinking),
        "request_thinking": request_thinking,
        "transport": transport,
        "substrate": "flag_on" if any(flags.values()) else "flag_off",
        "substrate_flags": dict(flags),
    }
    # Stamp the prompt SET (Task 14.5 A/B axis) ONLY on a bespoke ``--prompt-set``
    # run. A no-flag default run omits the field entirely so its rows are
    # byte-identical to the committed 14.4 matrix (which predates the column); the
    # report's ``_prompt_set_of`` reads a missing field as the default 9B set, so
    # the A/B stays self-describing without polluting the legacy output path.
    if binding.is_bespoke:
        row["prompt_set"] = binding.prompt_set
    # The best-shot call profile that produced this row (so the comparison is
    # transparent and 14.6 sees exactly how each number was obtained).
    row["response_format_mode"] = response_format_mode
    row["max_tokens"] = max_tokens
    return row


def _record_outcome(rec: dict[str, Any], out: TurnOutcome[Any]) -> None:
    rec["latency_s"] = round(out.latency_s, 1)
    rec["in_tokens"] = out.in_tokens
    rec["out_tokens"] = out.out_tokens
    rec["thinking_chars"] = out.thinking_chars
    rec["parsed_ok"] = out.parsed is not None
    if out.error is not None:
        rec["error"] = out.error
    if out.parsed is None and out.parse_error is not None:
        rec["parse_error"] = out.parse_error[:200]
        rec["raw_head"] = out.raw_text[:200]


async def _reply_cell(
    *,
    ctx: ReplyContext,
    spec: ModelSpec,
    request_thinking: bool,
    cover: bool,
    flags: Mapping[str, bool],
    api_key: str,
    base_url: str | None,
    sem: asyncio.Semaphore,
    binding: RenderBinding,
) -> dict[str, Any]:
    body_room, body_tick = _body(ctx)
    prompt = _reply_prompt(ctx, cover=cover, binding=binding)
    rf_mode, cap = _profile(request_thinking)
    rec = _base_row(
        corpus="reply",
        spec=spec,
        request_thinking=request_thinking,
        flags=flags,
        response_format_mode=rf_mode,
        max_tokens=cap,
        binding=binding,
    )
    rec["cover"] = "on" if cover else "off"
    rec["item"] = ctx.item_id
    rec["body_room"] = body_room
    out = await _run_turn(
        spec,
        prompt,
        MeetingTurn,
        request_thinking=request_thinking,
        max_tokens=cap,
        temperature=TEMPERATURE,
        response_format_mode=rf_mode,
        flags=flags,
        api_key=api_key,
        base_url=base_url,
        sem=sem,
        force_adapter=binding.force_adapter,
    )
    _record_outcome(rec, out)
    if out.parsed is not None:
        rec.update(_grade(out.parsed, ctx, body_room, body_tick))
    return rec


async def _vote_cell(
    *,
    item: CorpusItem,
    spec: ModelSpec,
    request_thinking: bool,
    flags: Mapping[str, bool],
    api_key: str,
    base_url: str | None,
    sem: asyncio.Semaphore,
    binding: RenderBinding,
) -> dict[str, Any]:
    vc = item.context
    prompt = binding.renderers.vote(
        voter_id=vc.voter_id,
        rendered_memory=vc.rendered_memory,
        transcript=vc.transcript,
        contradiction_flags=vc.contradiction_flags,
        suspicion_graph=vc.suspicion_graph,
        candidate_targets=vc.candidate_targets,
        skip_confidence_threshold=vc.skip_confidence_threshold,
        fellow_impostor_ids=vc.fellow_impostor_ids,
    )
    rf_mode, cap = _profile(request_thinking)
    rec = _base_row(
        corpus="vote",
        spec=spec,
        request_thinking=request_thinking,
        flags=flags,
        response_format_mode=rf_mode,
        max_tokens=cap,
        binding=binding,
    )
    rec["cover"] = "n/a"
    rec["item"] = item.item_id
    rec["voter_role"] = item.voter_role
    rec["recorded_target"] = item.recorded_target
    rec["is_inversion"] = item.is_inversion
    rec["available_impostor_ids"] = list(item.available_impostor_ids)
    rec["max_impostor_suspicion"] = round(item.max_impostor_suspicion, 4)
    out = await _run_turn(
        spec,
        prompt,
        VoteBallot,
        request_thinking=request_thinking,
        max_tokens=cap,
        temperature=VOTE_TEMPERATURE,
        response_format_mode=rf_mode,
        flags=flags,
        api_key=api_key,
        base_url=base_url,
        sem=sem,
        force_adapter=binding.force_adapter,
    )
    _record_outcome(rec, out)
    ballot = out.parsed
    if ballot is not None:
        rec["target"] = ballot.target
        rec["confidence"] = ballot.confidence
        rec["voted_available_impostor"] = ballot.target in item.available_impostor_ids
    return rec


async def _opening_cell(
    *,
    ctx: KillContext,
    spec: ModelSpec,
    request_thinking: bool,
    flags: Mapping[str, bool],
    api_key: str,
    base_url: str | None,
    sem: asyncio.Semaphore,
    binding: RenderBinding,
) -> dict[str, Any]:
    """Run + grade one impostor self-report opening cell (fabrication grade)."""

    prompt = binding.renderers.impostor_report(
        agent_id=ctx.killer,
        current_tick=ctx.trigger_tick,
        meeting_trigger=ctx.trigger_description,
        rendered_memory=ctx.rendered_memory,
        public_transcript="",
        fellow_impostor_ids=ctx.fellow_living,
        living_ids=tuple(p for p in ctx.living if p != ctx.killer),
        dead_ids=tuple(ctx.dead),
    )
    rf_mode, cap = _profile(request_thinking)
    rec = _base_row(
        corpus="opening",
        spec=spec,
        request_thinking=request_thinking,
        flags=flags,
        response_format_mode=rf_mode,
        max_tokens=cap,
        binding=binding,
    )
    rec["cover"] = "n/a"
    rec["item"] = ctx.item_id
    rec["kill_room"] = ctx.kill_room
    rec["kill_tick"] = ctx.kill_tick
    out = await _run_turn(
        spec,
        prompt,
        MeetingTurn,
        request_thinking=request_thinking,
        max_tokens=cap,
        temperature=TEMPERATURE,
        response_format_mode=rf_mode,
        flags=flags,
        api_key=api_key,
        base_url=base_url,
        sem=sem,
        force_adapter=binding.force_adapter,
    )
    _record_outcome(rec, out)
    if out.parsed is not None:
        grade = _grade_fabrication(out.parsed, ctx)
        # ``honest_placement`` = the opener placed itself at the true kill room =
        # the opening-turn self-incrimination tell (mirrors the reply self-co).
        rec["self_co_locates_kill"] = bool(grade["honest_placement"])
        rec["lie_attempted"] = bool(grade["lie_attempted"])
        rec["self_incriminating_text"] = bool(grade["self_incriminating_text"])
        flags_vs_witness = grade["flags_vs_witness"]
        assert isinstance(flags_vs_witness, dict)
        rec["self_flag_vs_witness"] = int(flags_vs_witness["strong"]) > 0
    return rec


async def _latency_cell(
    *,
    ctx: ReplyContext,
    spec: ModelSpec,
    request_thinking: bool,
    flags: Mapping[str, bool],
    api_key: str,
    base_url: str | None,
    sem: asyncio.Semaphore,
    binding: RenderBinding,
) -> dict[str, Any]:
    """One SEQUENTIAL reply call timed in isolation (the latency pass)."""

    prompt = _reply_prompt(ctx, cover=False, binding=binding)
    rf_mode, cap = _profile(request_thinking)
    rec = _base_row(
        corpus="latency",
        spec=spec,
        request_thinking=request_thinking,
        flags=flags,
        response_format_mode=rf_mode,
        max_tokens=cap,
        binding=binding,
    )
    rec["item"] = ctx.item_id
    out = await _run_turn(
        spec,
        prompt,
        MeetingTurn,
        request_thinking=request_thinking,
        max_tokens=cap,
        temperature=TEMPERATURE,
        response_format_mode=rf_mode,
        flags=flags,
        api_key=api_key,
        base_url=base_url,
        sem=sem,
        force_adapter=binding.force_adapter,
    )
    rec["latency_s"] = round(out.latency_s, 1)
    rec["parsed_ok"] = out.parsed is not None
    rec["out_tokens"] = out.out_tokens
    if out.error is not None:
        rec["error"] = out.error
    return rec


def _reply_prompt(ctx: ReplyContext, *, cover: bool, binding: RenderBinding) -> str:
    """Render the reply prompt for the bound set; inject the gp-1 cover if ON.

    The reply corpus is impostor-only (``build_reply_contexts`` filters to
    ``IMPOSTOR`` speakers), so for a BESPOKE set ``is_impostor=True`` is passed:
    the new set wires the cover directive into the reply path gated on
    ``is_impostor`` alone (the gp-1 fix), so passing it exercises that wiring.
    For the default 9B set ``is_impostor=False`` keeps the render byte-identical
    (its reply template carries no cover directive on this path). The ``cover``
    arm's injected ``_cover_directive`` is the set-independent 2×2 control and is
    applied to memory either way.
    """

    memory = ctx.rendered_memory
    if cover:
        body_room, body_tick = _body(ctx)
        if body_room is not None:
            memory = memory + _cover_directive(body_room, body_tick or 0)
    return binding.renderers.statement(
        agent_id=ctx.speaker,
        rendered_memory=memory,
        transcript=ctx.transcript,
        contradictions=ctx.contradictions,
        prior_turn=ctx.prior_turn,
        turn_kind="reply",
        fellow_impostor_ids=ctx.fellow_living,
        living_ids=tuple(p for p in ctx.living if p != ctx.speaker),
        dead_ids=tuple(ctx.dead),
        is_impostor=binding.reply_is_impostor,
        is_body_report=False,
    )


def _preflight_models(
    specs: Sequence[ModelSpec],
    *,
    api_key: str,
    base_url: str | None,
    pacer: _SwitchPacer,
) -> dict[str, bool]:
    """Confirm each id is served via a tiny generation probe (an unknown id 404s).

    Resolves the base URL the SAME way as the sweep calls
    (:func:`resolve_featherless_base_url`, honoring ``AILIBI_FEATHERLESS_BASE_URL``)
    so preflight and the run hit the same endpoint. Paces each model touch through
    the shared :class:`_SwitchPacer` so the probe does not trip the 4-switches/min
    plan limit. Only a NON-BUSY 404/400 (an unrecognized id) is a real skip; a
    transient 5xx/429/blip — including a busy-typed ``server_error``-body 4xx,
    the shape :func:`_probe_retryable` classifies — is retried.
    """

    import httpx

    resolved = base_url if base_url is not None else resolve_featherless_base_url()
    served: dict[str, bool] = {}
    for spec in specs:
        payload = {
            "model": spec.model_id,
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 1,
            "temperature": 0.0,
        }
        served[spec.model_id] = False
        last = ""
        for attempt in range(6):
            pacer.touch(spec.model_id)
            try:
                resp = httpx.post(
                    f"{resolved}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json=payload,
                    timeout=180,
                )
                if resp.status_code == 200:
                    served[spec.model_id] = True
                    print(f"  PREFLIGHT {spec.model_id}: served", flush=True)
                    break
                last = f"HTTP {resp.status_code} {resp.text[:120]}"
                # A busy-typed (server_error-body) 4xx is a TRANSIENT load shape,
                # not an unrecognized id — skipping on it would drop a served
                # model from the matrix (e.g. the probe's Pass-4 re-preflight of
                # a spec Pass 1 just confirmed) and bias the evidence. Only a
                # non-busy 400/404 is a real skip.
                try:
                    pf_body: Any = resp.json()
                except Exception:  # noqa: BLE001 — non-JSON body: status decides
                    pf_body = {"_raw": resp.text}
                if resp.status_code in (400, 404) and not _probe_retryable(
                    resp.status_code, pf_body
                ):
                    break  # a genuinely unrecognized id — a real skip, no retry
            except Exception as exc:  # noqa: BLE001
                last = f"{type(exc).__name__}: {exc}"
            # Generous backoff: a 429 here is a transient concurrency / switch-rate
            # blip (not "unserved"); wait long enough to clear the 1-minute window.
            time.sleep(min(30.0, 5.0 * (attempt + 1)))
        if not served[spec.model_id]:
            print(f"  PREFLIGHT {spec.model_id}: {last} -> SKIPPED", flush=True)
    return served


@dataclass(frozen=True)
class PinnedIds:
    """Item IDs selected ONCE (flag-OFF) and re-rendered under each substrate."""

    reply: tuple[str, ...]
    vote: tuple[str, ...]
    opening: tuple[str, ...]


def _pin_ids(cfg: SweepConfig) -> PinnedIds:
    """Select the corpus item IDs once, off the (all-ON) reconstruction.

    Historically pinned off the flag-OFF reconstruction; since Task 14.9 the
    unconditional all-ON substrate is the only one a NEW run can derive.
    """

    _set_substrate(True)
    reply = tuple(c.item_id for c in _select(cfg.sample_dir)[: cfg.reply_cap])
    votes = select_corpus(
        build_corpus(cfg.sample_dir),
        all_votes=False,
        crew_all=False,
        limit=cfg.vote_limit,
    )
    opening: tuple[str, ...] = ()
    if cfg.facts_path is not None:
        opening = tuple(
            c.item_id
            for c in build_kill_contexts(
                cfg.sample_dir, cfg.facts_path, cfg.opening_cap
            )
        )
    return PinnedIds(reply=reply, vote=tuple(i.item_id for i in votes), opening=opening)


def _contexts_for(
    cfg: SweepConfig, flag_on: bool, pinned: PinnedIds
) -> tuple[dict[str, bool], list[ReplyContext], list[CorpusItem], list[KillContext]]:
    """Re-render the PINNED ids under ``flag_on`` (controlled substrate compare)."""

    flags = _set_substrate(flag_on)
    reply_by_id = {c.item_id: c for c in _select(cfg.sample_dir)}
    reply = [reply_by_id[i] for i in pinned.reply if i in reply_by_id]
    vote_by_id = {i.item_id: i for i in build_corpus(cfg.sample_dir)}
    votes = [vote_by_id[i] for i in pinned.vote if i in vote_by_id]
    openings: list[KillContext] = []
    if pinned.opening and cfg.facts_path is not None:
        kill_by_id = {
            c.item_id: c
            for c in build_kill_contexts(cfg.sample_dir, cfg.facts_path, 10_000)
        }
        openings = [kill_by_id[i] for i in pinned.opening if i in kill_by_id]
    # Fail loud (AGENTS.md: no silent fallbacks) if a pinned id cannot be
    # re-rendered under this substrate: silently shrinking the corpus would make
    # the flag-OFF vs flag-ON delta compare DIFFERENT contexts while the report
    # still describes a same-context delta. Opening ids are checked too.
    opening_ids = {c.item_id for c in openings}
    missing = (
        [f"reply:{i}" for i in pinned.reply if i not in reply_by_id]
        + [f"vote:{i}" for i in pinned.vote if i not in vote_by_id]
        + [f"opening:{i}" for i in pinned.opening if i not in opening_ids]
    )
    if missing:
        raise SystemExit(
            f"substrate {'ON' if flag_on else 'OFF'}: {len(missing)} pinned ids "
            "could not be re-rendered (aborting rather than comparing different "
            f"corpora): {missing[:8]}"
        )
    print(
        f"substrate {'ON' if flag_on else 'OFF'} {flags}: {len(reply)} reply, "
        f"{len(votes)} vote, {len(openings)} opening ctxs",
        flush=True,
    )
    return flags, reply, votes, openings


async def run_sweep(cfg: SweepConfig, *, api_key: str) -> int:
    """Run the full matrix and stream rows to ``cfg.results_path``.

    ``cfg.results_path`` defaults to the committed 14.4 :data:`RESULTS` so ``run``
    stays byte-identical; the Task 16.1 probe (Pass 4) supplies ``PROBE_RESULTS``
    (with ``append=True``) so the graded matrix rides this harness unmodified in
    shape while streaming into the probe jsonl.
    """

    pacer = _SwitchPacer()
    served = _preflight_models(
        cfg.models, api_key=api_key, base_url=cfg.base_url, pacer=pacer
    )
    specs = [s for s in cfg.models if served.get(s.model_id)]
    skipped = [s.model_id for s in cfg.models if not served.get(s.model_id)]
    if skipped:
        print(f"SKIPPED (unserved): {skipped}", flush=True)
    if not specs:
        raise SystemExit("no slate models are served; nothing to sweep")
    if cfg.facts_path is None:
        print(
            "NOTE: --facts not supplied; the opening corpus is SKIPPED "
            "(reply + vote + latency still run).",
            flush=True,
        )

    # Resolve the render binding ONCE (Task 14.5): which prompt SET renders, how
    # rows are stamped, the non-Qwen transport, and the reply cover gate.
    binding = _binding_for(cfg)
    print(
        f"prompt_set={binding.prompt_set} "
        f"(transport: non-Qwen via {'adapter' if binding.force_adapter else 'bare-send'}; "
        f"reply is_impostor={binding.reply_is_impostor})",
        flush=True,
    )

    # Reconstruct each substrate's contexts ONCE (memory is baked into the
    # returned objects), so the model-outer loop can re-use them without touching
    # the env again — and, crucially, without interleaving model switches.
    pinned = _pin_ids(cfg)
    ctx_by_sub = {flag: _contexts_for(cfg, flag, pinned) for flag in cfg.substrates}

    sem = asyncio.Semaphore(cfg.concurrency)
    n_rows = 0
    matrix_log: list[str] = []
    mode_skipped: list[str] = []
    with cfg.results_path.open("a" if cfg.append else "w", encoding="utf-8") as sink:

        def emit(rec: dict[str, Any]) -> None:
            nonlocal n_rows
            sink.write(json.dumps(rec) + "\n")
            sink.flush()
            n_rows += 1

        # Model-OUTER, substrate/mode-INNER: each model is loaded once and does
        # ALL its work before the next, so the 4-switches/min plan limit is
        # respected (the pacer guards the boundary).
        for spec in specs:
            # A --modes filter that excludes this model's only axis value (e.g.
            # --modes thinking against GLM / Cydonia, which run non-thinking only)
            # leaves it with no mode to run. Surface that EXPLICITLY rather than
            # silently emitting zero rows (AGENTS.md: no silent fallbacks) — and
            # skip before the pacer burns a model switch on a no-op.
            spec_modes = _modes_for(spec, cfg.mode_filter)
            if not spec_modes:
                print(
                    f"  NOTE: {spec.label} has no mode under --modes "
                    f"{[_mode_label(m) for m in (cfg.mode_filter or ())]}; "
                    "emitting no rows for it.",
                    flush=True,
                )
                mode_skipped.append(spec.label)
                continue
            pacer.touch(spec.model_id)
            for flag_on in cfg.substrates:
                flags, reply_ctxs, vote_items, kill_ctxs = ctx_by_sub[flag_on]
                sub = "flag_on" if flag_on else "flag_off"
                for request_thinking in spec_modes:
                    mode = _mode_label(request_thinking)
                    tag = f"{spec.label}/{mode}/{sub}"

                    # Sequential latency micro-pass (isolated timing).
                    for ctx in reply_ctxs[: cfg.latency_samples]:
                        emit(
                            await _latency_cell(
                                ctx=ctx,
                                spec=spec,
                                request_thinking=request_thinking,
                                flags=flags,
                                api_key=api_key,
                                base_url=cfg.base_url,
                                sem=sem,
                                binding=binding,
                            )
                        )

                    # Opening pass (impostor self-report), bounded concurrency.
                    if kill_ctxs:
                        for rec in await asyncio.gather(
                            *[
                                _opening_cell(
                                    ctx=ctx,
                                    spec=spec,
                                    request_thinking=request_thinking,
                                    flags=flags,
                                    api_key=api_key,
                                    base_url=cfg.base_url,
                                    sem=sem,
                                    binding=binding,
                                )
                                for ctx in kill_ctxs
                            ]
                        ):
                            emit(rec)

                    # Reply behavior pass (cover OFF + cover ON = the 2x2).
                    for rec in await asyncio.gather(
                        *[
                            _reply_cell(
                                ctx=ctx,
                                spec=spec,
                                request_thinking=request_thinking,
                                cover=cover,
                                flags=flags,
                                api_key=api_key,
                                base_url=cfg.base_url,
                                sem=sem,
                                binding=binding,
                            )
                            for cover in (False, True)
                            for ctx in reply_ctxs
                        ]
                    ):
                        emit(rec)

                    # Vote pass.
                    for rec in await asyncio.gather(
                        *[
                            _vote_cell(
                                item=item,
                                spec=spec,
                                request_thinking=request_thinking,
                                flags=flags,
                                api_key=api_key,
                                base_url=cfg.base_url,
                                sem=sem,
                                binding=binding,
                            )
                            for item in vote_items
                        ]
                    ):
                        emit(rec)

                    matrix_log.append(
                        f"{tag}: opening={len(kill_ctxs)} reply={len(reply_ctxs)}x2 "
                        f"vote={len(vote_items)} latency="
                        f"{min(cfg.latency_samples, len(reply_ctxs))}"
                    )
                    print(f"  done {tag}", flush=True)

    print(f"\nwrote {n_rows} rows -> {cfg.results_path}")
    print("matrix actually run (no silent truncation):")
    for line in matrix_log:
        print(f"  {line}")
    if skipped:
        print(f"  skipped models (unserved): {skipped}")
    if mode_skipped:
        print(f"  skipped models (no mode under --modes filter): {mode_skipped}")
    return 0


# ─────────────────────────── report generation ───────────────────────────


def _read_rows(path: Path) -> list[dict[str, Any]]:
    """Read a results jsonl into a list of row dicts (fails loud if absent)."""

    if not path.exists():
        raise SystemExit(f"{path} not found — run the sweep first.")
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _rows() -> list[dict[str, Any]]:
    return _read_rows(RESULTS)


def _prompt_set_of(row: Mapping[str, Any]) -> str:
    """The prompt set a row was rendered through.

    Rows recorded before the Task 14.5 ``prompt_set`` stamp (the committed 14.4
    matrix) carry no field and are the pinned 9B default set — so the 14.4 tables
    reproduce byte-identically once the bespoke A/B rows share the file.
    """

    return str(row.get("prompt_set", DEFAULT_PROMPT_SET))


def _summ_reply(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    parsed = [r for r in rows if r.get("parsed_ok")]
    return {
        "n": n,
        "parsed": len(parsed),
        "self_co": sum(1 for r in parsed if r.get("self_co_locates_body")),
        "self_flag": sum(1 for r in parsed if r.get("new_self_flag")),
        "deflect": sum(1 for r in parsed if r.get("deflects_legal")),
    }


def _pct(num: int, den: int) -> str:
    return f"{num}/{den} ({100 * num / den:.0f}%)" if den else "0/0 (—)"


def _fmt_reply(s: Mapping[str, Any]) -> str:
    p = int(s["parsed"])
    return (
        f"parse {_pct(p, int(s['n']))} · deflect {_pct(int(s['deflect']), p)} · "
        f"self-co-loc {_pct(int(s['self_co']), p)} · "
        f"self-flag {_pct(int(s['self_flag']), p)}"
    )


def _group_reply(
    rows: Sequence[Mapping[str, Any]], *, cover: str, substrate: str
) -> dict[tuple[str, str], dict[str, Any]]:
    out: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for r in rows:
        if r.get("corpus") != "reply":
            continue
        if r.get("cover") != cover or r.get("substrate") != substrate:
            continue
        out.setdefault((str(r["label"]), str(r["mode"])), []).append(r)
    return {k: _summ_reply(v) for k, v in out.items()}


def _group_vote(
    rows: Sequence[Mapping[str, Any]], *, substrate: str
) -> dict[tuple[str, str], dict[str, Any]]:
    by: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for r in rows:
        if r.get("corpus") != "vote" or r.get("substrate") != substrate:
            continue
        by.setdefault((str(r["label"]), str(r["mode"])), []).append(r)
    summ: dict[tuple[str, str], dict[str, Any]] = {}
    for k, v in by.items():
        parsed = [r for r in v if r.get("parsed_ok")]
        summ[k] = {
            "n": len(v),
            "parsed": len(parsed),
            "conv": sum(1 for r in parsed if r.get("voted_available_impostor")),
        }
    return summ


def _group_opening(
    rows: Sequence[Mapping[str, Any]], *, substrate: str
) -> dict[tuple[str, str], dict[str, Any]]:
    by: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for r in rows:
        if r.get("corpus") != "opening" or r.get("substrate") != substrate:
            continue
        by.setdefault((str(r["label"]), str(r["mode"])), []).append(r)
    summ: dict[tuple[str, str], dict[str, Any]] = {}
    for k, v in by.items():
        parsed = [r for r in v if r.get("parsed_ok")]
        summ[k] = {
            "n": len(v),
            "parsed": len(parsed),
            "self_co": sum(1 for r in parsed if r.get("self_co_locates_kill")),
            "confess": sum(1 for r in parsed if r.get("self_incriminating_text")),
        }
    return summ


def _latency_by_model(
    rows: Sequence[Mapping[str, Any]],
) -> dict[tuple[str, str], float]:
    by: dict[tuple[str, str], list[float]] = {}
    for r in rows:
        if r.get("corpus") != "latency" or not r.get("parsed_ok"):
            continue
        by.setdefault((str(r["label"]), str(r["mode"])), []).append(
            float(r["latency_s"])
        )
    return {k: round(statistics.mean(v), 1) for k, v in by.items() if v}


def _ordered_cells(summary: Mapping[tuple[str, str], Any]) -> list[tuple[str, str]]:
    order = {s.label: i for i, s in enumerate(SLATE)}
    return sorted(summary, key=lambda k: (order.get(k[0], 99), k[1]))


def _profile_info(
    rows: Sequence[Mapping[str, Any]],
) -> dict[tuple[str, str], tuple[str, int, float]]:
    """Per (label, mode): the call profile (response_format_mode, max_tokens) and
    mean reasoning length (thinking_chars over parsed reply rows) — so the
    fidelity table shows exactly how each cell was called and whether the model
    actually reasoned."""

    out: dict[tuple[str, str], tuple[str, int, float]] = {}
    think: dict[tuple[str, str], list[float]] = {}
    for r in rows:
        if r.get("corpus") != "reply":
            continue
        k = (str(r["label"]), str(r["mode"]))
        if k not in out:
            out[k] = (
                str(r.get("response_format_mode", "?")),
                int(r.get("max_tokens", 0)),
                0.0,
            )
        if r.get("parsed_ok"):
            think.setdefault(k, []).append(float(r.get("thinking_chars", 0)))
    return {
        k: (mode, cap, round(statistics.mean(think[k]), 0) if think.get(k) else 0.0)
        for k, (mode, cap, _) in out.items()
    }


def _historical_q9b() -> dict[str, Any]:
    rows = [
        json.loads(line) for line in REF_REPLY.read_text().splitlines() if line.strip()
    ]
    return _summ_reply(rows)


def _rate(s: Mapping[str, Any], key: str) -> float:
    p = int(s["parsed"])
    return (int(s[key]) / p) if p else 0.0


# ── Task 14.5 bespoke per-set A/B (new set vs pinned-9B set, same model) ──


def _rows_for_set(
    rows: Sequence[Mapping[str, Any]], prompt_set: str
) -> list[Mapping[str, Any]]:
    return [r for r in rows if _prompt_set_of(r) == prompt_set]


def _bespoke_sets_present(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    """Non-default prompt sets present in the results, in SLATE model order.

    Each bespoke set is keyed by its model label for ordering; an unknown set
    sorts last. A set carries rows only for its own model, so the first row's
    label orders it.
    """

    order = {s.label: i for i, s in enumerate(SLATE)}
    present = sorted(set(map(_prompt_set_of, rows)) - {DEFAULT_PROMPT_SET})

    def _key(ps: str) -> tuple[int, str]:
        labels = [str(r["label"]) for r in rows if _prompt_set_of(r) == ps]
        first = labels[0] if labels else ""
        return (order.get(first, 99), ps)

    return sorted(present, key=_key)


def _delta_pp(new: Mapping[str, Any], base: Mapping[str, Any] | None, key: str) -> str:
    if base is None:
        return "—"
    return f"{100 * (_rate(new, key) - _rate(base, key)):+.0f} pp"


def _ab_section(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    """The Task 14.5 A/B addendum: each bespoke set vs the pinned-9B set on its
    own model, over the SAME reconstructed contexts (the one clean control in a
    co-designed change). Renders the per-set delta automatically from any
    ``prompt_set``-tagged rows; degrades to a how-to note when none are present."""

    out: list[str] = []
    out.append("## Bespoke per-set A/B (Task 14.5): new set vs pinned-9B set")
    out.append("")
    out.append(
        "Each Task 14.5 bespoke set is rendered over the SAME reconstructed "
        "contexts as the 14.4 sweep and compared to the PINNED 9B prompts ON ITS "
        "OWN MODEL — the one clean control in a co-designed change (model + prompt "
        "co-vary by owner decision 2026-06-30, so this is a REFERENCE point, NOT a "
        "single-variable ablation; do not over-claim causality). The bespoke arm "
        "wires the cover directive into the impostor REPLY path (gated on "
        "`is_impostor` alone) and routes the non-Qwen slate through the REAL "
        "adapter (`call_turn`) — the 14.4.1 fix having retired the harness "
        "bare-send. Each row is stamped with its `prompt_set`; the no-flag default "
        "rows are the pinned-9B baseline and reproduce the 14.4 numbers."
    )
    out.append("")
    bespoke = _bespoke_sets_present(rows)
    if not bespoke:
        out.append(
            "_No `prompt_set`-tagged bespoke rows are in "
            "`results-featherless-sweep.jsonl` yet — this is the operator-run A/B "
            "($0 marginal, needs `FEATHERLESS_API_KEY`). Run it per set on its own "
            "model and merge the rows in, then regenerate this report:_"
        )
        out.append("")
        out.append("```")
        out.append("# example: the qwen3_32b set on Qwen3-32B, merged into the matrix")
        out.append("# (the mode is pinned so the non-thinking set is not also run")
        out.append(
            "#  in thinking mode, which would overlap the qwen3_32b_thinking set)"
        )
        out.append("uv run python -m experiments.lab.featherless_sweep run \\")
        out.append(
            "    --prompt-set qwen3_32b --models qwen3-32b --modes non_thinking --append"
        )
        out.append("```")
        out.append("")
        out.append(
            "_Once those rows exist this section renders the per-set delta tables "
            "(reply self-co-location — the impostor tell — plus parse-success, "
            "deflection, self-flag, and vote conversion) automatically._"
        )
        return out

    base = _rows_for_set(rows, DEFAULT_PROMPT_SET)
    # Reply corpus (cover OFF): self-co-location is the headline impostor tell.
    out.append("### Reply corpus (cover OFF) — self-co-location is the impostor tell")
    out.append("")
    out.append(
        "| prompt_set | model | mode | substrate | parse new/9B | deflect new/9B "
        "| self-co-loc new/9B (Δ) | self-flag new/9B (Δ) |"
    )
    out.append("|---|---|---|---|---|---|---|---|")
    for ps in bespoke:
        new_rows = _rows_for_set(rows, ps)
        for substrate in ("flag_off", "flag_on"):
            new_g = _group_reply(new_rows, cover="off", substrate=substrate)
            base_g = _group_reply(base, cover="off", substrate=substrate)
            for label, mode in _ordered_cells(new_g):
                ns = new_g[(label, mode)]
                bs = base_g.get((label, mode))
                np_, nn = int(ns["parsed"]), int(ns["n"])
                bp = f"{_pct(int(bs['parsed']), int(bs['n']))}" if bs else "—"
                bd = f"{_pct(int(bs['deflect']), int(bs['parsed']))}" if bs else "—"
                bco = f"{_pct(int(bs['self_co']), int(bs['parsed']))}" if bs else "—"
                bfl = f"{_pct(int(bs['self_flag']), int(bs['parsed']))}" if bs else "—"
                out.append(
                    f"| {ps} | {label} | {mode} | {substrate} | "
                    f"{_pct(np_, nn)} / {bp} | "
                    f"{_pct(int(ns['deflect']), np_)} / {bd} | "
                    f"{_pct(int(ns['self_co']), np_)} / {bco} "
                    f"({_delta_pp(ns, bs, 'self_co')}) | "
                    f"{_pct(int(ns['self_flag']), np_)} / {bfl} "
                    f"({_delta_pp(ns, bs, 'self_flag')}) |"
                )
    out.append("")
    out.append(
        "Self-co-location Δ is new-set minus pinned-9B-set on the same model "
        "(negative = the bespoke set self-incriminates LESS); self-flag Δ likewise."
    )
    out.append("")
    # Vote corpus: conversion on the hard inversion cases.
    out.append("### Vote corpus — parse-success + conversion")
    out.append("")
    out.append(
        "| prompt_set | model | mode | substrate | parse new/9B | conversion new/9B |"
    )
    out.append("|---|---|---|---|---|---|")
    has_vote = False
    for ps in bespoke:
        new_rows = _rows_for_set(rows, ps)
        for substrate in ("flag_off", "flag_on"):
            new_g = _group_vote(new_rows, substrate=substrate)
            base_g = _group_vote(base, substrate=substrate)
            for label, mode in _ordered_cells(new_g):
                has_vote = True
                ns = new_g[(label, mode)]
                bs = base_g.get((label, mode))
                bp = f"{_pct(int(bs['parsed']), int(bs['n']))}" if bs else "—"
                bc = f"{_pct(int(bs['conv']), int(bs['parsed']))}" if bs else "—"
                out.append(
                    f"| {ps} | {label} | {mode} | {substrate} | "
                    f"{_pct(int(ns['parsed']), int(ns['n']))} / {bp} | "
                    f"{_pct(int(ns['conv']), int(ns['parsed']))} / {bc} |"
                )
    if not has_vote:
        out.append("| _(no vote rows in the bespoke arm)_ | | | | | |")
    out.append("")
    # Opening corpus, only if the bespoke arm ran it (requires --facts).
    op_lines: list[str] = []
    for ps in bespoke:
        new_rows = _rows_for_set(rows, ps)
        for substrate in ("flag_off", "flag_on"):
            new_g = _group_opening(new_rows, substrate=substrate)
            base_g = _group_opening(base, substrate=substrate)
            for label, mode in _ordered_cells(new_g):
                ns = new_g[(label, mode)]
                bs = base_g.get((label, mode))
                bp = f"{_pct(int(bs['parsed']), int(bs['n']))}" if bs else "—"
                bco = f"{_pct(int(bs['self_co']), int(bs['parsed']))}" if bs else "—"
                op_lines.append(
                    f"| {ps} | {label} | {mode} | {substrate} | "
                    f"{_pct(int(ns['parsed']), int(ns['n']))} / {bp} | "
                    f"{_pct(int(ns['self_co']), int(ns['parsed']))} / {bco} |"
                )
    if op_lines:
        out.append("### Opening corpus — impostor self-report")
        out.append("")
        out.append(
            "| prompt_set | model | mode | substrate | parse new/9B | self-co-loc new/9B |"
        )
        out.append("|---|---|---|---|---|---|")
        out.extend(op_lines)
        out.append("")
    out.append(
        "**Cover directive (14.4 finding):** the 14.4 sweep found the cover "
        "directive a WEAK / inconsistent lever (mean Δ +2 pp, leaning information "
        "ceiling) but with a real prompt-artifact component — audit gp-1: the 9B's "
        "v5 directive is gated off the body-report OPENING and never reaches an "
        "impostor, who only ever speaks on REPLY turns. The bespoke sets therefore "
        "WIRE it into the reply path (gated on `is_impostor` alone); the A/B above "
        "measures the net effect on the same model. It is wired because it is a "
        "cheap prompt-artifact fix, NOT because 14.4 proved it dissolves the tell."
    )
    return out


def _verdict(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    off_off = _group_reply(rows, cover="off", substrate="flag_off")
    off_on = _group_reply(rows, cover="on", substrate="flag_off")
    fit = {
        k
        for k, s in off_off.items()
        if int(s["n"]) and int(s["parsed"]) / int(s["n"]) >= 0.5
    }

    # Cover Δ is only meaningful when BOTH arms parsed comparably: a cover-ON
    # cell that fails to parse would make `_rate` 0 (zero denominator) and read
    # as a large self-co IMPROVEMENT, corrupting the prompt-artifact-vs-ceiling
    # read. Require cover-ON parse ≥ 50% (same bar as `fit`) to count the cell;
    # otherwise it is INCONCLUSIVE (surfaced separately).
    def _ok(s: Mapping[str, Any]) -> bool:
        return bool(int(s["n"])) and int(s["parsed"]) / int(s["n"]) >= 0.5

    cover_helps = [
        (k, _rate(off_off[k], "self_co") - _rate(off_on[k], "self_co"))
        for k in fit
        if k in off_on and _ok(off_on[k])
    ]
    cover_inconclusive = sorted(k for k in fit if k not in off_on or not _ok(off_on[k]))
    flag_floor = min((_rate(off_off[k], "self_flag") for k in fit), default=0.0)
    ref = off_off.get((REFERENCE_LABEL, "non_thinking"), {"n": 0, "parsed": 0})
    return {
        "off_off": off_off,
        "off_on": off_on,
        "fit_cells": sorted(fit),
        "cover_helps": cover_helps,
        "cover_inconclusive": cover_inconclusive,
        "flag_floor": flag_floor,
        "ref_cell": ref,
    }


def write_report() -> int:
    rows = _rows()
    # The 14.4 tables describe the PINNED 9B prompts; scope them to the default
    # set so they reproduce byte-identically once the Task 14.5 bespoke A/B rows
    # share the file. Committed 14.4 rows carry no ``prompt_set`` field and are the
    # default set (``_prompt_set_of``), so a no-bespoke-rows file is unchanged.
    base_rows = [r for r in rows if _prompt_set_of(r) == DEFAULT_PROMPT_SET]
    v = _verdict(base_rows)
    lat = _latency_by_model(base_rows)
    hist = _historical_q9b()

    lines: list[str] = []
    add = lines.append
    add("# Lab report — Featherless model x thinking-mode sweep (Task 14.4)")
    add("")
    add(
        "**Decision informed:** which Featherless `(meeting_model, trigger_model, "
        "mode)` to lock at Task 14.6, and whether the Phase-13 information-ceiling "
        "hypothesis (`audits/audit-2026-06-25-0859-phase-13-close.md`) survives a "
        "stronger model. **Method:** the model-ceiling-vs-information design of "
        "`experiments/lab/report-model-ceiling-probe.md`, generalized across the "
        "Featherless slate over the SAME reconstructed `replays/samples/9p2i` "
        "opening/reply/vote contexts (item IDs pinned once and re-rendered under "
        "each substrate), on the PINNED 9B prompts, graded by the IDENTICAL "
        "mechanical detectors. **Cost:** $0 (Featherless flat-rate)."
    )
    add("")
    add(
        "**9B-class reference (in-sweep, item-matched):** `qwen3.5:9b` is local "
        "Ollama (off the hosted endpoint), so the reference column is its closest "
        "served analogue **`Qwen/Qwen3-8B`** (same Qwen3 generation / nearest "
        "size / native `enable_thinking`), run over the SAME frozen contexts on "
        "BOTH substrates. The committed Ollama `results-model-ceiling-q9b.jsonl` "
        f"(self-co {100 * _rate(hist, 'self_co'):.0f}%, self-flag "
        f"{100 * _rate(hist, 'self_flag'):.0f}%, deflect "
        f"{100 * _rate(hist, 'deflect'):.0f}%) is folded only as a secondary "
        "HISTORICAL row — it predates the current 9p2i recording (non-item-matched)."
    )
    add("")
    add(
        "**Non-Qwen transport:** GLM-4-32B-0414 and Cydonia-24B-v2 are routed "
        "through a sweep-local BARE send that OMITS the 14.1 adapter's mandatory "
        "`chat_template_kwargs.enable_thinking` field (the Qwen3 convention that "
        "otherwise collapses GLM to `{}` and 400/504s Cydonia) — so their rows "
        "reflect real model structured-output fidelity, not a harness artifact. "
        "The proper conditional-field fix belongs in `llm/featherless_client.py` "
        "(out of scope for 14.4; flagged to 14.1/14.6)."
    )
    add("")
    add(
        "Slate substitution (live, 2026-06-29): the contract's `Qwen/Qwen3-30B-A3B` "
        "and `zai-org/GLM-4-32B` ids 404; Featherless serves the canonical "
        "revisions `Qwen/Qwen3-30B-A3B-Instruct-2507` and `zai-org/GLM-4-32B-0414`."
    )
    add("")
    add(
        "**Best-shot call profiles (owner decision 2026-06-29):** the probe's job "
        "is to rank how each model performs on the corpus, so each model/mode is "
        "called with the settings MOST LIKELY TO SUCCEED — not the 9B-era "
        f"`json_object` / {PROD_TURN_CAP}-token handicap. THINKING rows use "
        f"`response_format=none` (json_object SUPPRESSES Qwen3 reasoning — "
        "calibrated: out=243 vs 3187 tokens) + a 16384-token budget so reasoning "
        "actually happens and never truncates, with the `<think>` block stripped "
        "before extract→validate. NON-THINKING rows use `json_object` + a 4096 "
        "budget. The OUTPUT is the schema-identical `MeetingTurn`/`VoteBallot` "
        "either way (downstream graders unchanged), and reasoning is DISCARDED "
        "(never recorded), so it cannot leak into game state. Per-row `profile` "
        f"(mode + max_tokens) is stamped in the jsonl. The deployed sim still caps "
        f"turns at {PROD_TURN_CAP} / votes at {PROD_VOTE_CAP}; choosing thinking "
        "for the recorded baseline is a 14.6/14.7 decision (raise the generation "
        "budget, cap the recorded answer, strip reasoning) — see the latency note "
        "in the recommendation."
    )
    add("")

    # ── Fidelity ──
    add("## Structured-output fidelity (parse-success, best-shot profile)")
    add("")
    add("Reply corpus, cover OFF, flag-OFF substrate.")
    add("")
    prof = _profile_info(base_rows)
    add(
        "| model | mode | profile | parse-success | latency (isolated) | reasoning | fit? |"
    )
    add("|---|---|---|---|---|---|---|")
    for k in _ordered_cells(v["off_off"]):
        s = v["off_off"][k]
        p, n = int(s["parsed"]), int(s["n"])
        pr = p / n if n else 0.0
        fit = "yes" if pr >= 0.9 else ("marginal" if pr >= 0.5 else "**NO**")
        latv = lat.get(k)
        lats = f"~{latv}s" if latv is not None else "—"
        ref_tag = " (ref)" if k[0] == REFERENCE_LABEL else ""
        pmode, pcap, think = prof.get(k, ("?", 0, 0.0))
        prof_s = f"{pmode}/{pcap}"
        reason_s = f"~{think:.0f} ch" if think else "—"
        add(
            f"| {k[0]}{ref_tag} | {k[1]} | {prof_s} | {_pct(p, n)} | {lats} | "
            f"{reason_s} | {fit} |"
        )
    add("")

    # ── Model-ceiling read ──
    add("## Model-ceiling-vs-information read (cover OFF, flag-OFF)")
    add("")
    add(
        "`qwen3-8b` is the item-matched 9B-class reference. Read the candidate "
        "rows against it on identical contexts."
    )
    add("")
    add("| model | mode | deflect | self-co-loc (the *tell*) | self-flag |")
    add("|---|---|---|---|---|")
    for k in _ordered_cells(v["off_off"]):
        s = v["off_off"][k]
        p = int(s["parsed"])
        ref_tag = " (ref)" if k[0] == REFERENCE_LABEL else ""
        if p == 0:
            add(f"| {k[0]}{ref_tag} | {k[1]} | — (unfit) | — | — |")
            continue
        add(
            f"| {k[0]}{ref_tag} | {k[1]} | {_pct(int(s['deflect']), p)} | "
            f"{_pct(int(s['self_co']), p)} | {_pct(int(s['self_flag']), p)} |"
        )
    add(
        f"| qwen3.5:9b (Ollama, historical) | non_thinking | "
        f"{_pct(int(hist['deflect']), int(hist['parsed']))} | "
        f"{_pct(int(hist['self_co']), int(hist['parsed']))} | "
        f"{_pct(int(hist['self_flag']), int(hist['parsed']))} |"
    )
    add("")

    # ── Cover 2x2 ──
    add("## Cover-directive 2x2 (model x {cover OFF, cover ON-reply})")
    add("")
    add("Self-co-location (the tell) with the cover directive OFF vs ON, flag-OFF:")
    add("")
    add("| model | mode | cover OFF self-co-loc | cover ON self-co-loc | Δ |")
    add("|---|---|---|---|---|")
    for k in _ordered_cells(v["off_off"]):
        soff = v["off_off"][k]
        son = v["off_on"].get(k)
        poff, noff = int(soff["parsed"]), int(soff["n"])
        if poff == 0 or noff == 0:
            add(f"| {k[0]} | {k[1]} | — | — | — |")
            continue
        pon = int(son["parsed"]) if son else 0
        non = int(son["n"]) if son else 0
        coff = _pct(int(soff["self_co"]), poff)
        # A cover-ON cell that did not parse comparably (≥50%) is INCONCLUSIVE,
        # not an improvement: a 0-denominator self-co rate would otherwise read
        # as a spurious cover win (corrupting the prompt-artifact-vs-ceiling read).
        if son is None or non == 0 or pon / non < 0.5:
            con = _pct(pon, non) if son else "—"
            add(f"| {k[0]} | {k[1]} | {coff} | inconclusive (parse {con}) | — |")
            continue
        add(
            f"| {k[0]} | {k[1]} | {coff} | {_pct(int(son['self_co']), pon)} | "
            f"{100 * (int(son['self_co']) / pon - int(soff['self_co']) / poff):+.0f} pp |"
        )
    add("")
    add(_quadrant_text(v))
    add("")

    # ── Substrate delta ──
    add("## Per-model substrate delta (flag-ON vs flag-OFF)")
    add("")
    add(
        "Does the corrected 13.5 substrate help THIS model decide where the 9B "
        "degraded? Reply corpus, cover OFF, SAME pinned contexts re-rendered."
    )
    add("")
    add("| model | mode | flag-OFF | flag-ON |")
    add("|---|---|---|---|")
    on_off = _group_reply(base_rows, cover="off", substrate="flag_on")
    empty = {"n": 0, "parsed": 0, "deflect": 0, "self_co": 0, "self_flag": 0}
    for k in _ordered_cells(v["off_off"]):
        add(
            f"| {k[0]} | {k[1]} | {_fmt_reply(v['off_off'][k])} | "
            f"{_fmt_reply(on_off.get(k, empty))} |"
        )
    add("")

    # ── Opening ──
    add("## Opening corpus — impostor self-report (parse + self-incrimination)")
    add("")
    op_off = _group_opening(base_rows, substrate="flag_off")
    op_on = _group_opening(base_rows, substrate="flag_on")
    if not op_off and not op_on:
        add(
            "_Not run in this sweep (no `--facts` supplied). The opening pass "
            "renders the production `impostor_report` prompt over reconstructed "
            "kill contexts and grades fabrication vs the engine-walk kill ground "
            "truth._"
        )
    else:
        add(
            "Killer opens the meeting for their own kill. `self-co-loc` = the "
            "opener placed itself at the true kill room (the opening tell); "
            "`confess` = self-incriminating free text. Tabulated per substrate."
        )
        add("")
        add("| model | mode | substrate | parse-success | self-co-loc | confess |")
        add("|---|---|---|---|---|---|")
        for sub, g in (("flag_off", op_off), ("flag_on", op_on)):
            for k in _ordered_cells(g):
                s = g[k]
                p = int(s["parsed"])
                ref_tag = " (ref)" if k[0] == REFERENCE_LABEL else ""
                add(
                    f"| {k[0]}{ref_tag} | {k[1]} | {sub} | {_pct(p, int(s['n']))} | "
                    f"{_pct(int(s['self_co']), p)} | {_pct(int(s['confess']), p)} |"
                )
    add("")

    # ── Votes ──
    add("## Vote corpus — parse-success + conversion")
    add("")
    add(
        "Crew votes WITH a visible impostor; half are recorded-SKIP inversion "
        "cases (a true impostor at suspicion 1.00 over the 0.60 gate where the 9B "
        "SKIPPED). `conversion` = voter picked an available impostor. Same pinned "
        "vote ids re-rendered under each substrate."
    )
    add("")
    add("| model | mode | substrate | parse-success | conversion |")
    add("|---|---|---|---|---|")
    for sub in ("flag_off", "flag_on"):
        g = _group_vote(base_rows, substrate=sub)
        for k in _ordered_cells(g):
            s = g[k]
            add(
                f"| {k[0]} | {k[1]} | {sub} | "
                f"{_pct(int(s['parsed']), int(s['n']))} | "
                f"{_pct(int(s['conv']), int(s['parsed']))} |"
            )
    add("")

    # ── Recommendation + hypothesis ──
    add("## Recommended tuple + evidence")
    add("")
    add(_recommendation_text(v, lat))
    add("")
    add("## Honest read of the information-ceiling hypothesis")
    add("")
    add(_hypothesis_text(v))
    add("")
    add(
        "**Harness/raw:** `experiments/lab/featherless_sweep.py` + "
        "`experiments/lab/results-featherless-sweep.jsonl` (per-cell grades + "
        "parse-success + tokens + latency + `transport` + `substrate_flags`; the "
        "matrix actually run is logged at run time — no silent truncation). The "
        "9B-class reference is the in-sweep `Qwen/Qwen3-8B`; the committed Ollama "
        "`results-model-ceiling-q9b.jsonl` is a secondary historical row."
    )
    add("")
    # Task 14.5 addendum: the bespoke per-set A/B (rendered from any
    # ``prompt_set``-tagged rows; a how-to note when none are present yet).
    lines.extend(_ab_section(rows))
    add("")
    REPORT.write_text("\n".join(lines))
    print(f"wrote {REPORT}")
    return 0


def _fit_labels(v: Mapping[str, Any]) -> list[str]:
    return sorted({k[0] for k in v["fit_cells"]})


def _quadrant_text(v: Mapping[str, Any]) -> str:
    fit = _fit_labels(v)
    if not fit:
        return (
            "**Quadrant verdict — UNDETERMINED.** No model cleared the "
            "structured-output bar (see fidelity table)."
        )
    deltas = [d for _k, d in v["cover_helps"]]
    mean_delta = statistics.mean(deltas) if deltas else 0.0
    helped = sum(1 for d in deltas if d >= 0.1)
    floor = float(v["flag_floor"])
    inconclusive = v.get("cover_inconclusive", [])
    incon_note = (
        f" ({len(inconclusive)} cell(s) excluded as INCONCLUSIVE — cover-ON "
        "parse-success below 50%, so a 0-denominator self-co rate is not counted "
        "as a cover win.)"
        if inconclusive
        else ""
    )
    return (
        "**Quadrant verdict — BOTH, leaning INFORMATION CEILING.** The cover "
        "directive's effect on self-co-location is SMALL and INCONSISTENT across "
        f"the fit cells (mean Δ {100 * mean_delta:+.0f} pp; helps ≥10 pp in only "
        f"{helped} of {len(deltas)} comparable cells, back-fires in others) — far "
        "weaker than its effect on the 9B's own contexts (cover cut self-co "
        f"55%→21% in `results-deflection-probe.jsonl`).{incon_note} So there IS a "
        "prompt-artifact component (the v5 directive never reaches the reply path "
        "today, audit gp-1) worth wiring in at 14.5, but it does NOT reliably "
        "dissolve the tell. The decisive ceiling signal is the self-FLAG floor: it "
        f"never falls below {100 * floor:.0f}% on any fit model — the impostor keeps "
        "minting a structured self-contradiction because it is lying into a "
        "detector fed by sightings it never saw (`report-model-ceiling-probe.md`). "
        "Capability buys cleaner JSON, not a clean alibi."
    )


def _recommendation_text(
    v: Mapping[str, Any], lat: Mapping[tuple[str, str], float]
) -> str:
    off_off = v["off_off"]
    cands = [
        k
        for k, s in off_off.items()
        if k[0] != REFERENCE_LABEL
        and int(s["n"])
        and int(s["parsed"]) / int(s["n"]) >= 0.9
    ]
    if not cands:
        return (
            "No candidate cleared a 90% parse-success bar; recommend re-opening "
            "the upstream adapter before locking a tuple at 14.6."
        )
    order = {s.label: i for i, s in enumerate(SLATE)}
    cands.sort(key=lambda k: (k[1] != "non_thinking", order.get(k[0], 99)))
    best = cands[0]
    best_s = off_off[best]
    best_parse = _pct(int(best_s["parsed"]), int(best_s["n"]))
    latv = lat.get(best)
    lats = f"~{latv}s/turn isolated" if latv is not None else "latency n/a"
    speed = next(
        (k for k in cands if k[0] == "qwen3-30b-a3b" and k[1] == "non_thinking"), None
    )
    speed_lat = lat.get(speed) if speed else None
    speed_line = (
        f" For the trigger_model (latency-sensitive), "
        f"`{_id_for('qwen3-30b-a3b')}` (MoE) is the speed option at "
        f"~{speed_lat}s/turn vs ~{latv}s for the 32B."
        if speed and speed_lat is not None
        else ""
    )

    # Classify the non-Qwen models against the SAME 90% structured-output bar the
    # recommendation/fidelity table use (NOT the 50% verdict-`fit` threshold), so
    # the text doesn't claim a marginal model "clears the parse bar".
    def _parse_rate(label: str) -> float:
        s = off_off.get((label, "non_thinking"))
        return (int(s["parsed"]) / int(s["n"])) if s and int(s["n"]) else 0.0

    nq_bits: list[str] = []
    for label, name in (
        ("cydonia-24b", "Cydonia-24B-v2"),
        ("glm-4-32b", "GLM-4-32B-0414"),
    ):
        pr = _parse_rate(label)
        if pr >= 0.9:
            nq_bits.append(f"{name} clears the 90% bar ({pr * 100:.0f}%)")
        elif pr >= 0.5:
            nq_bits.append(f"{name} is MARGINAL ({pr * 100:.0f}%, below the 90% bar)")
        else:
            nq_bits.append(f"{name} is unfit ({pr * 100:.0f}%)")
    nq = (
        " Via the bare send (omitting the Qwen-only chat kwarg), "
        + "; ".join(nq_bits)
        + " — so the 0% in the prior version was an adapter artifact, now "
        "corrected. They remain non-default (a marginal/lower-deflection profile "
        "behind the recommended Qwen3-32B), not disqualified on a parse artifact."
    )
    # Data-driven mode rationale: thinking now ACTUALLY reasons (best-shot
    # profile = none + 16384 + strip), so compare the recommended model's thinking
    # vs non-thinking cells on the FAIR test and report the DIRECTION from the
    # numbers — not a pre-data assumption that thinking is inert.
    nt = off_off.get((best[0], "non_thinking"))
    th = off_off.get((best[0], "thinking"))
    mode_note = ""
    if nt and th and int(nt["parsed"]) and int(th["parsed"]):

        def _r(s: Mapping[str, Any], key: str) -> int:
            return round(100 * _rate(s, key))

        d_defl = _r(th, "deflect") - _r(nt, "deflect")
        d_co = _r(th, "self_co") - _r(nt, "self_co")
        d_flag = _r(th, "self_flag") - _r(nt, "self_flag")
        helps = (d_defl >= 10 or d_flag <= -10 or d_co <= -10) and not (
            d_defl <= -10 or d_flag >= 10 or d_co >= 10
        )
        hurts = (d_defl <= -10 or d_flag >= 10 or d_co >= 10) and not (
            d_defl >= 10 or d_flag <= -10 or d_co <= -10
        )
        nt_lat, th_lat = (
            lat.get((best[0], "non_thinking")),
            lat.get((best[0], "thinking")),
        )
        cost = (
            f" at a real latency cost (~{th_lat}s vs ~{nt_lat}s/turn)"
            if nt_lat is not None and th_lat is not None
            else " at a real latency cost"
        )
        deltas = (
            f"deflect {d_defl:+d} pp, self-flag {d_flag:+d} pp, self-co {d_co:+d} pp"
        )
        if helps:
            mode_note = (
                f" **Mode is a genuine tradeoff now** (the fair best-shot test — "
                f"thinking really reasons, ~16k tokens): on this model thinking "
                f"MEASURABLY IMPROVES behavior ({deltas}){cost}. Mode is therefore "
                f"a 14.6 quality-vs-latency call — `non_thinking` is the "
                f"latency-cheap default, `thinking` the higher-quality option; it is "
                f"no longer the degenerate axis it was under the 2048/json_object "
                f"handicap."
            )
        elif hurts:
            mode_note = (
                f" Mode: on a fair best-shot test thinking does NOT help here "
                f"({deltas}){cost}; `non_thinking` recommended."
            )
        else:
            mode_note = (
                f" Mode: on a fair best-shot test thinking and non-thinking are "
                f"close ({deltas}){cost}; `non_thinking` recommended for latency."
            )
    return (
        f"**Recommended (meeting_model, trigger_model, mode) = "
        f"(`{_id_for(best[0])}`, `{_id_for(best[0])}`, `{best[1]}`).** Evidence: "
        f"it clears the structured-output bar at {best_parse} parse-success "
        f"({lats}), posts a low self-co-location, and converts on the hard vote "
        f"cases.{speed_line}{mode_note}{nq} NOTE (integration risk): these "
        f"isolated-turn metrics are PROXIES, not the live R-gate — a model can "
        f"deflect/convert better in isolation yet still correctly SKIP in a noisy "
        f"full game. The lock at 14.6 must read this as evidence, not verdict; the "
        f"trigger_model defaults to the meeting_model id pending a dedicated "
        f"trigger-corpus pass."
    )


def _hypothesis_text(v: Mapping[str, Any]) -> str:
    ref = v["ref_cell"]
    floor = float(v["flag_floor"])
    fit = _fit_labels(v)
    if int(ref["parsed"]) == 0 or not fit:
        return "Inconclusive: the reference or fit cells did not parse."
    ref_co = _rate(ref, "self_co")
    ref_flag = _rate(ref, "self_flag")
    return (
        "**Supported — and now controlled on identical contexts.** With the "
        "9B-class `qwen3-8b` reference run over the SAME frozen contexts as the "
        "stronger candidates, the self-incrimination tell does NOT fall as model "
        f"strength rises: the self-FLAG floor stays ≥ {100 * floor:.0f}% across "
        f"every fit model (reference self-flag {100 * ref_flag:.0f}%, self-co "
        f"{100 * ref_co:.0f}%) and the cover prompt does not reliably remove it. "
        "This is the `model_ceiling_probe.py:11-14` signature of an INFORMATION "
        "ceiling, not a model ceiling — the impostor reasons faithfully from a "
        'memory that says "you found the body here" into a detector fed by '
        "sightings it never saw. The one place the stronger models clearly DIFFER "
        "from the 9B is the vote corpus: on the hard inversion cases (a true "
        "impostor at suspicion 1.00 over the 0.60 gate where the recorded 9B "
        "SKIPPED) the fit Featherless models convert — the sharpened Phase-14 "
        "question ('can the new model DRIVE the corrected substrate where the 9B "
        "couldn't?') answered YES *in isolation*. But that is an isolated "
        "single-ballot proxy, NOT the live R-gate: only the 14.7 re-record + 14.8 "
        "R-gate can settle it. Net: a stronger model is necessary (it fixes the "
        "9B's structured output + the isolated skip pathology) but the "
        "meeting-deflection tell points at Phase-15 information levers "
        "(asymmetric visibility / vents / sabotage), not a further model upgrade."
    )


def _id_for(label: str) -> str:
    for s in SLATE:
        if s.label == label:
            return s.model_id
    return label


# ─────────────────────── Phase-16 probe (Task 16.1) ───────────────────────
#
# A SEPARATE ``probe`` / ``probe-report`` pipeline that discovers whether the
# owner-directed new-generation slate (Qwen3.6-27B + ThinkingCap-Qwen3.6-27B) is
# viable on the committed sweep contexts BEFORE any production change. It writes
# its own PROBE_RESULTS / PROBE_REPORT so the committed 14.4 ``run`` / ``report``
# path is byte-identical and untouched. Four probe row kinds are recorded as JSONL
# evidence the report regenerates every number from (zero hardcoded conclusions):
# ``served_id`` + ``no_go`` (Pass 1, the generation preflight is the arbiter),
# ``response_format`` (Pass 2), ``thinking_kwarg`` (Pass 3), plus the graded matrix
# cells (Pass 4, streamed by the EXISTING ``run_sweep``).


async def _probe_post(
    payload: dict[str, Any], *, base_url: str, api_key: str
) -> tuple[int, Any]:
    """Low-level Featherless chat POST for the discovery passes; NEVER raises on status.

    Returns ``(status_code, body)`` where ``body`` is the parsed JSON object, or
    ``{"_raw": text}`` when the response is not JSON. Unlike the graded transports
    (which fail loud through :func:`_send_with_retry`), the discovery passes must
    RECORD a 400/404 body as evidence rather than raise — a NO-GO / a
    deterministic rejection is a first-class recorded outcome for the 16.2 lock.
    TRANSIENT failures (429 / 5xx / a connection blip) are retried a bounded
    number of times so a load spike is not misrecorded as a capability verdict
    (a false "rejected" in the 16.12 thinking-kwarg evidence); the deterministic
    400/404 statuses are NEVER retried — determinism across attempts IS the
    evidence the response_format pass records. Lazy ``httpx`` import; a 600s
    timeout matches the production ``_default_send``.
    """

    import httpx

    status = 0
    body: Any = {"_raw": ""}
    async with httpx.AsyncClient() as client:
        for attempt in range(3):
            try:
                resp = await client.post(
                    f"{base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json=payload,
                    timeout=httpx.Timeout(600.0),
                )
                status = resp.status_code
                try:
                    body = resp.json()
                except Exception:  # noqa: BLE001 — a non-JSON error body is recorded raw
                    body = {"_raw": resp.text}
                if status == 200 or not _probe_retryable(status, body):
                    return status, body
            except Exception as exc:  # noqa: BLE001 — record transport failures as evidence
                status = 0
                body = {"_raw": f"{type(exc).__name__}: {exc}"[:240]}
            if attempt < 2:
                await asyncio.sleep(10.0 * (attempt + 1))
    return status, body


def _probe_retryable(status: int, body: Any) -> bool:
    """Is a non-200 discovery response TRANSIENT (retry) or a capability verdict?

    Retried: 429, any 5xx, and — the shape a load spike actually presents as on
    this endpoint — a 4xx whose error body is TYPED ``server_error`` ("This model
    is busy, please try again later" arrives as an HTTP 400/422 with
    ``{"error": {"type": "server_error", ...}}``). Without the body check, a
    busy blip would be recorded as a deterministic ``json_schema`` rejection and
    feed the 16.2 lock a false capability verdict; with it, a rejection verdict
    means the busy-typed body persisted across every bounded retry while
    ``json_object`` control requests on the same model succeeded around it.
    NOT retried: 4xx with ``invalid_request_error`` (or any other non-server
    type) — e.g. ``model_not_found`` and ThinkingCap's chat-template 400 —
    because that determinism IS the recorded evidence.
    """

    if status == 429 or status >= 500:
        return True
    if 400 <= status < 500 and isinstance(body, dict):
        error = body.get("error")
        if isinstance(error, dict) and error.get("type") == "server_error":
            return True
    return False


def _probe_preflight_one(
    model_id: str, *, api_key: str, base_url: str, pacer: _SwitchPacer
) -> tuple[bool, int, str]:
    """Paced 1-token generation preflight for ONE id; ``(served, attempts, evidence)``.

    Same shape / backoff / skip logic as :func:`_preflight_models` (200 -> served;
    400/404 -> deterministic non-served, no retry; 5xx/429/transport -> bounded
    retries up to 6 attempts, ``sleep(min(30, 5*(attempt+1)))``) but reports the
    attempts used and the last evidence string so Pass 1 can record per id form.
    Synchronous ``httpx`` mirrors :func:`_preflight_models` (a paced serial probe,
    not part of the concurrent matrix). ``evidence`` is ``"ok"`` when served, else
    the last ``HTTP <code> <first 160 chars of body>`` (or a transport error head).
    """

    import httpx

    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 1,
        "temperature": 0.0,
    }
    last = "ok"
    attempts = 0
    for attempt in range(6):
        attempts = attempt + 1
        pacer.touch(model_id)
        try:
            resp = httpx.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
                timeout=180,
            )
            if resp.status_code == 200:
                return True, attempts, "ok"
            last = f"HTTP {resp.status_code} {resp.text[:160]}"
            # Deterministic non-served (unknown id / refused deployment) stops
            # the probe; a busy-typed 4xx does NOT — the same server_error body
            # shape _probe_retryable handles for the later passes can dress a
            # transient load spike as a 400/422 here, and recording it as
            # served=false would hand 16.2 a FALSE NO-GO on a viable candidate.
            try:
                body: Any = resp.json()
            except Exception:  # noqa: BLE001 — a non-JSON error body: status decides
                body = {"_raw": resp.text}
            if resp.status_code in (400, 404) and not _probe_retryable(
                resp.status_code, body
            ):
                return False, attempts, last  # a genuinely unrecognized id — no retry
        except Exception as exc:  # noqa: BLE001
            last = f"{type(exc).__name__}: {exc}"[:160]
        # A 429 / 5xx / busy-typed 4xx here is a transient concurrency / switch-rate
        # blip; wait long enough to clear the 1-minute window (same as
        # _preflight_models).
        time.sleep(min(30.0, 5.0 * (attempt + 1)))
    return False, attempts, last


def _probe_served_pass(
    *,
    api_key: str,
    base_url: str,
    pacer: _SwitchPacer,
    emit: Callable[[dict[str, Any]], None],
) -> dict[str, str]:
    """Pass 1 — served-id discovery: the generation preflight is the arbiter.

    For each candidate label (its owner-directed id forms, PINNED SLATE id first)
    plus the incumbent (same-day re-verification of its single SLATE id), runs a
    paced 1-token preflight per id form and emits one ``served_id`` row per form.
    Returns ``label -> served id form`` for every label that proceeds: the pinned
    id when it serves, else the FIRST served alternate form — which the later
    passes ADOPT (loudly, and self-described in every row's ``model`` stamp),
    because excluding a model whose canonical revision the preflight just found
    would record a FALSE NO-GO (the 14.4 slate needed exactly such suffixed
    revisions). An adopted alternate is an explicit re-pin instruction for the
    SLATE, not a silent fallback: the served_id rows carry both forms' evidence.
    A label none of whose forms serve emits a ``no_go`` row and is EXCLUDED from
    every later pass — this NEVER raises, because a NO-GO is a first-class
    recorded outcome for the 16.2 lock (e.g. ThinkingCap's deterministic 400).
    """

    proceed: dict[str, str] = {}
    for label in _PROBE_LABELS:
        slate_id = _id_for(label)
        forms = _PROBE_ID_FORMS.get(label, (slate_id,))
        served_forms: list[str] = []
        evidence_by_form: list[tuple[str, str]] = []
        for form in forms:
            served, attempts, evidence = _probe_preflight_one(
                form, api_key=api_key, base_url=base_url, pacer=pacer
            )
            emit(
                {
                    "corpus": "served_id",
                    "label": label,
                    "model": form,
                    "pinned": form == slate_id,
                    "served": served,
                    "attempts": attempts,
                    "evidence": evidence,
                }
            )
            evidence_by_form.append((form, evidence))
            if served:
                served_forms.append(form)
        if slate_id in served_forms:
            proceed[label] = slate_id
            print(f"  PROBE served: {label} -> {slate_id}", flush=True)
        elif served_forms:
            # The pinned guess is wrong but a canonical revision IS served:
            # adopt it for the later passes rather than recording a false
            # NO-GO. The operator should re-pin the SLATE id to this form.
            proceed[label] = served_forms[0]
            print(
                f"  PROBE served (ALTERNATE): {label} pinned id {slate_id} is "
                f"not served, adopting {served_forms[0]} — re-pin the SLATE "
                "entry to this form.",
                flush=True,
            )
        else:
            reason = next(
                (ev for form, ev in evidence_by_form if form == slate_id),
                "; ".join(f"{form}: {ev}" for form, ev in evidence_by_form),
            )
            emit(
                {
                    "corpus": "no_go",
                    "label": label,
                    "model": slate_id,
                    "forms_tried": [form for form, _ in evidence_by_form],
                    "reason": reason,
                }
            )
            print(f"  PROBE NO-GO: {label} ({slate_id}): {reason}", flush=True)
    return proceed


def _probe_response_format(rf_mode: str, schema: type[BaseModel]) -> dict[str, Any]:
    """Wire ``response_format`` for the probe, mirroring the production translation.

    ``json_object`` -> ``{"type":"json_object"}``; ``json_schema`` -> the strict
    grammar shape the production adapter (``_featherless_response_format``) sends,
    so the verdict speaks to what the REAL adapter would send.
    """

    if rf_mode == "json_object":
        return {"type": "json_object"}
    return {
        "type": "json_schema",
        "json_schema": {
            "name": schema.__name__,
            "strict": True,
            "schema": schema.model_json_schema(),
        },
    }


def _probe_body_head(body: Any, limit: int = 200) -> str:
    """A <=``limit``-char preview of a response body for an evidence cell."""

    try:
        return json.dumps(body)[:limit]
    except (TypeError, ValueError):
        return str(body)[:limit]


def _probe_content_is_json(body: Any) -> bool:
    """Whether ``choices[0].message.content`` parses as JSON (guarded)."""

    try:
        content = body["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError):
        return False
    try:
        json.loads(content)
    except (TypeError, ValueError):
        return False
    return True


async def _probe_response_format_pass(
    specs: Sequence[ModelSpec],
    *,
    api_key: str,
    base_url: str,
    pacer: _SwitchPacer,
    emit: Callable[[dict[str, Any]], None],
) -> None:
    """Pass 2 — response_format verification (json_object AND strict json_schema).

    For each SERVED model probes both wire shapes over both production schemas with
    TWO attempts each: two attempts distinguish a DETERMINISTIC rejection (both
    attempts 400 -> the endpoint does not implement that shape for this model) from
    a TRANSIENT load 400 (one fails, the other 200s). The json_schema payload
    mirrors :func:`_probe_response_format` (the production translation) EXACTLY;
    ``chat_template_kwargs.enable_thinking=false`` is included iff the spec carries
    the Qwen kwarg (the incumbent honors it; the 3.6 candidate does too, verified
    live). The one-line prompt is DERIVED from the schema's property names, never
    hand-written per schema.
    """

    for spec in specs:
        # Pace the switch onto this spec (the pass is spec-outer, so this is the
        # only switch boundary) — same 4-switches/min plan limit as the matrix.
        pacer.touch(spec.model_id)
        for schema in (MeetingTurn, VoteBallot):
            keys = sorted(schema.model_json_schema()["properties"])
            prompt = (
                "Reply with a single JSON object containing exactly these keys: "
                f"{keys}. Output only the JSON object and nothing else."
            )
            for rf_mode in ("json_object", "json_schema"):
                rf = _probe_response_format(rf_mode, schema)
                for attempt in (1, 2):
                    payload: dict[str, Any] = {
                        "model": spec.model_id,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 256,
                        "temperature": 0.0,
                        "response_format": rf,
                    }
                    if spec.qwen_kwarg:
                        payload["chat_template_kwargs"] = {"enable_thinking": False}
                    status, body = await _probe_post(
                        payload, base_url=base_url, api_key=api_key
                    )
                    accepted = status == 200
                    emit(
                        {
                            "corpus": "response_format",
                            "label": spec.label,
                            "model": spec.model_id,
                            "rf_mode": rf_mode,
                            "schema": schema.__name__,
                            "attempt": attempt,
                            "http_status": status,
                            "accepted": accepted,
                            "content_is_json": (
                                _probe_content_is_json(body) if accepted else None
                            ),
                            "body_head": _probe_body_head(body),
                        }
                    )
        print(f"  PROBE response_format: {spec.label}", flush=True)


def _probe_reasoning_channel(
    body: Any, accepted: bool
) -> tuple[str | None, int, int, str, int | None]:
    """Classify which channel (if any) carried reasoning in a Pass-3 response.

    Returns ``(channel, channel_chars, content_chars, content_head, out_tokens)``.
    Precedence mirrors the three observed shapes: the dedicated
    ``reasoning_content`` side-channel (the incumbent Qwen3-32B), the Qwen3.5-style
    ``reasoning`` key, then the Qwen3.6 INLINE ``</think>``-close shape detected by a
    bare close tag in ``content`` (``channel_chars`` = the length of the reasoning
    part from :func:`_split_inline_think`). ``None`` when no reasoning is present or
    the request was not accepted.
    """

    if not accepted:
        return None, 0, 0, "", None
    try:
        message = body["choices"][0]["message"]
        content = message.get("content") or ""
        reasoning_content = message.get("reasoning_content") or ""
        reasoning_side = message.get("reasoning") or ""
    except (KeyError, IndexError, TypeError, AttributeError):
        return None, 0, 0, "", None
    out_tokens: int | None = None
    usage = body.get("usage") if isinstance(body, dict) else None
    if isinstance(usage, dict):
        raw_out = usage.get("completion_tokens")
        if isinstance(raw_out, int):
            out_tokens = raw_out
    content_chars = len(content)
    # ``content_head`` is the STRIPPED-answer head, never the raw content: for
    # the inline shape the raw prefix IS chain-of-thought, and committing it to
    # the jsonl/report would violate the reasoning-is-discarded-never-recorded
    # doctrine — 16.12 only needs the channel + its length.
    answer, inline = _split_inline_think(content)
    content_head: str = answer[:120]
    if reasoning_content:
        return (
            "reasoning_content",
            len(reasoning_content),
            content_chars,
            content_head,
            out_tokens,
        )
    if reasoning_side:
        return (
            "reasoning",
            len(reasoning_side),
            content_chars,
            content_head,
            out_tokens,
        )
    # Keyed on the CLOSE TAG, not on a non-empty reasoning prefix: Qwen3.6's
    # known empty think-sandwich quirk can emit the tag pair with zero chars
    # between, and that channel presence is itself 16.12 evidence.
    if "</think>" in content:
        return (
            "inline_think_close",
            len(inline),
            content_chars,
            content_head,
            out_tokens,
        )
    return None, 0, content_chars, content_head, out_tokens


async def _probe_thinking_kwarg_pass(
    specs: Sequence[ModelSpec],
    *,
    api_key: str,
    base_url: str,
    pacer: _SwitchPacer,
    emit: Callable[[dict[str, Any]], None],
) -> None:
    """Pass 3 — thinking-kwarg behavior: the evidence a 16.12 registry entry encodes.

    For each SERVED model sends a fixed arithmetic prompt under three kwarg
    settings — ``absent`` (no ``chat_template_kwargs`` at all — the DEFAULT
    posture), ``false``, ``true`` — with NO response_format, and records WHICH
    channel carried the reasoning (``reasoning_content`` / ``reasoning`` /
    ``inline_think_close`` / none). This is exactly the per-id posture Task 16.12's
    ``_THINKING_KWARG_BY_MODEL`` entry (and the production reasoning mapping) will
    encode — 16.1 only RECORDS it.
    """

    prompt = "What is 17*23? Reply with just the number."
    for spec in specs:
        # Pace the switch onto this spec (spec-outer; the only switch boundary).
        pacer.touch(spec.model_id)
        for kwarg in ("absent", "false", "true"):
            payload: dict[str, Any] = {
                "model": spec.model_id,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 768,
                "temperature": 0.0,
            }
            if kwarg != "absent":
                payload["chat_template_kwargs"] = {"enable_thinking": kwarg == "true"}
            status, body = await _probe_post(
                payload, base_url=base_url, api_key=api_key
            )
            accepted = status == 200
            channel, channel_chars, content_chars, content_head, out_tokens = (
                _probe_reasoning_channel(body, accepted)
            )
            emit(
                {
                    "corpus": "thinking_kwarg",
                    "label": spec.label,
                    "model": spec.model_id,
                    "kwarg": kwarg,
                    "http_status": status,
                    "accepted": accepted,
                    "reasoning_channel": channel,
                    "channel_chars": channel_chars,
                    "content_chars": content_chars,
                    "content_head": content_head,
                    "out_tokens": out_tokens,
                }
            )
        print(f"  PROBE thinking_kwarg: {spec.label}", flush=True)


async def run_probe(cfg: SweepConfig, *, api_key: str) -> int:
    """Run the Task 16.1 probe: discovery passes 1-3 then the graded matrix (Pass 4).

    Truncates/creates ``cfg.results_path`` and streams passes 1-3 into it, then
    rides the EXISTING :func:`run_sweep` (Pass 4, ``append=True`` so the matrix
    lands after the discovery rows) so the graded matrix uses the unmodified
    harness shape. The ``probe`` CLI never sets ``cfg.append``: with no
    --models/--modes selection an append could only duplicate rows and corrupt
    the report's rates (partial recovery is a driver-level row replacement). The
    served-id pass excludes any NO-GO candidate from the later passes and the
    matrix. NEVER calls ``write_report`` (the CLI calls :func:`write_probe_report`
    after this returns 0). The ``_SwitchPacer`` is shared across passes 1-3; Pass 4
    re-preflights through ``run_sweep``'s own internal pacer (it is called
    unmodified).
    """

    resolved = (
        cfg.base_url if cfg.base_url is not None else resolve_featherless_base_url()
    )
    pacer = _SwitchPacer()
    n_rows = 0
    served_specs: tuple[ModelSpec, ...] = ()
    open_mode = "a" if cfg.append else "w"
    with cfg.results_path.open(open_mode, encoding="utf-8") as sink:

        def emit(rec: dict[str, Any]) -> None:
            nonlocal n_rows
            sink.write(json.dumps(rec) + "\n")
            sink.flush()
            n_rows += 1

        print("PROBE pass 1 — served-id discovery", flush=True)
        proceed = _probe_served_pass(
            api_key=api_key, base_url=resolved, pacer=pacer, emit=emit
        )
        # Adopt the served form per label: identical to the SLATE spec when the
        # pinned id served; a `replace`d spec carrying the served ALTERNATE
        # revision otherwise (never a silent fallback — pass 1 printed the
        # re-pin instruction and the served_id rows carry both forms).
        served_specs = tuple(
            s
            if proceed[s.label] == s.model_id
            else replace(s, model_id=proceed[s.label])
            for s in SLATE
            if s.label in _PROBE_LABELS and s.label in proceed
        )
        print(
            f"PROBE served: {[(s.label, s.model_id) for s in served_specs]}",
            flush=True,
        )
        if served_specs:
            print("PROBE pass 2 — response_format verification", flush=True)
            await _probe_response_format_pass(
                served_specs,
                api_key=api_key,
                base_url=resolved,
                pacer=pacer,
                emit=emit,
            )
            print("PROBE pass 3 — thinking-kwarg behavior", flush=True)
            await _probe_thinking_kwarg_pass(
                served_specs,
                api_key=api_key,
                base_url=resolved,
                pacer=pacer,
                emit=emit,
            )
    print(f"wrote {n_rows} probe rows (passes 1-3) -> {cfg.results_path}", flush=True)

    if not served_specs:
        print("PROBE: no candidate/incumbent served; skipping the graded matrix.")
        return 0
    # Pass 4 — the graded matrix, APPENDED to the same jsonl via the EXISTING
    # run_sweep (which re-preflights: cheap, paced, and keeps the DoD's "rides the
    # existing harness unmodified in shape" — pinned corpus ids re-rendered per
    # cell, model-outer loop, switch pacing, generation preflight). append=True so
    # it does not truncate the passes 1-3 rows. The bespoke ``qwen3_32b`` set is
    # held CONSTANT across both matrix models and BOTH modes (mode is the axis) —
    # bypassing the ``_SET_OWNER`` restriction ON PURPOSE (that restriction stays
    # intact for the ``run`` subcommand, enforced in main()).
    print("PROBE pass 4 — graded matrix (via run_sweep)", flush=True)
    matrix_cfg = replace(
        cfg,
        models=served_specs,
        # The CALLER-selected sink, not the PROBE_RESULTS constant: a scratch /
        # repair invocation with a non-default results_path must keep all four
        # passes in ONE file (and must never append matrix rows to the
        # committed artifact behind the caller's back).
        results_path=cfg.results_path,
        prompt_set=PROBE_PROMPT_SET,
        substrates=(True,),
        append=True,
    )
    await run_sweep(matrix_cfg, api_key=api_key)
    return 0


# ─────────────────────── probe report generation ───────────────────────


def _md_cell(text: str, limit: int = 160) -> str:
    """Make a string safe for a Markdown table cell (escape pipes, flatten newlines)."""

    flat = text.replace("\n", " ").replace("\r", " ").replace("|", "\\|")
    return flat[:limit]


def _probe_served_labels(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    """Labels ANY of whose id forms served (candidates + incumbent), SLATE order.

    Any-form, not pinned-only: pass 1 ADOPTS a served alternate revision when
    the pinned guess 404s, so that label's later-pass rows exist and the report
    must render them (the served_id table shows which form actually served).
    """

    served = {
        str(r["label"])
        for r in rows
        if r.get("corpus") == "served_id" and r.get("served")
    }
    return [s.label for s in SLATE if s.label in served]


def _probe_served_form(rows: Sequence[Mapping[str, Any]], label: str) -> str:
    """The id form that actually served for ``label`` (pinned first), from rows."""

    forms = [
        str(r["model"])
        for r in rows
        if r.get("corpus") == "served_id" and r["label"] == label and r.get("served")
    ]
    pinned = [
        str(r["model"])
        for r in rows
        if r.get("corpus") == "served_id"
        and r["label"] == label
        and r.get("served")
        and r.get("pinned")
    ]
    return pinned[0] if pinned else (forms[0] if forms else _id_for(label))


def _probe_thinking_prose(tk_rows: Sequence[Mapping[str, Any]], label: str) -> str:
    """A computed one-line thinking-posture summary for ``label`` (Section 5).

    Every clause is GATED on the underlying call having been ACCEPTED: a busy
    4xx / 5xx cell looks exactly like "accepted with no reasoning channel" to a
    naive reader, and summarizing it as "does NOT reason by default" (or as
    kwarg suppression) would hand 16.12 a wrong thinking policy off a failed
    probe. A failed cell reads INCONCLUSIVE instead.
    """

    by: dict[str, Mapping[str, Any]] = {
        str(r["kwarg"]): r for r in tk_rows if r["label"] == label
    }
    absent = by.get("absent")
    false_r = by.get("false")

    def _ok(r: Mapping[str, Any] | None) -> bool:
        return r is not None and bool(r.get("accepted"))

    def _reasons(r: Mapping[str, Any] | None) -> bool:
        return r is not None and bool(r.get("reasoning_channel"))

    channels = sorted(
        {
            str(r["reasoning_channel"])
            for r in by.values()
            if r.get("accepted") and r.get("reasoning_channel")
        }
    )
    if not _ok(absent):
        default_posture = "default posture INCONCLUSIVE (the kwarg-absent call failed)"
    elif _reasons(absent):
        default_posture = "REASONS by default"
    else:
        default_posture = "does NOT reason by default"
    if not _ok(false_r):
        false_note = (
            "`enable_thinking=false` INCONCLUSIVE (call failed or not recorded)"
        )
    elif not _reasons(false_r):
        false_note = "`enable_thinking=false` SUPPRESSES reasoning"
    else:
        false_note = "`enable_thinking=false` does NOT suppress reasoning"
    channel_note = (
        "reasoning channel(s): " + ", ".join(f"`{c}`" for c in channels)
        if channels
        else "no reasoning channel observed"
    )
    # The id the rows were ACTUALLY produced against (pass 1 may have adopted a
    # served alternate revision), never the SLATE pin — the registered-vs-
    # sweep-local prose below is integration evidence 16.2/16.12 consumes.
    row_ids = {str(r["model"]) for r in by.values()}
    served_id = next(iter(row_ids)) if len(row_ids) == 1 else _id_for(label)
    extra = ""
    if "inline_think_close" in channels:
        if _registry_knows(served_id):
            # A REGISTERED id routes through the production adapter, whose strip
            # policy already excises inline reasoning — no sweep-local handling.
            extra += (
                " Reasoning is INLINE in `content`, closed by a bare `</think>` "
                "with no side-channel; the production adapter's `strip` policy "
                "excises it for this registered id (and production always pins "
                "`enable_thinking` explicitly, so the bare-request default never "
                "reaches game state)."
            )
        else:
            extra += (
                " Reasoning is INLINE in `content`, closed by a bare `</think>` "
                "with no side-channel — `_raw_from_response_body` reads only "
                "`reasoning_content`, so the sweep-local transport carries the "
                "split (the production mapping is 16.12's)."
            )
    if "reasoning" in channels:
        extra += (
            " It uses a `message.reasoning` key `_raw_from_response_body` does not "
            "read — the sweep-local transport merges it so it is not dropped."
        )
    if label == PROBE_INCUMBENT_LABEL and "reasoning_content" in channels:
        extra += (
            " (Incumbent: reasoning on `reasoning_content`, the channel the "
            "production mapping already reads.)"
        )
    return (
        f"**{label}:** kwarg absent ⇒ {default_posture}; {false_note}; "
        f"{channel_note}.{extra}"
    )


def write_probe_report() -> int:
    """Regenerate PROBE_REPORT from PROBE_RESULTS (every number from the rows)."""

    if not PROBE_RESULTS.exists():
        raise SystemExit(
            f"{PROBE_RESULTS} not found — run the probe first "
            "(`python -m experiments.lab.featherless_sweep probe`)."
        )
    rows = _read_rows(PROBE_RESULTS)
    served_labels = _probe_served_labels(rows)
    served_rows = [r for r in rows if r.get("corpus") == "served_id"]
    nogo_rows = [r for r in rows if r.get("corpus") == "no_go"]
    rf_rows = [r for r in rows if r.get("corpus") == "response_format"]
    tk_rows = [r for r in rows if r.get("corpus") == "thinking_kwarg"]
    reply_off = _group_reply(rows, cover="off", substrate="flag_on")
    reply_on = _group_reply(rows, cover="on", substrate="flag_on")
    vote_g = _group_vote(rows, substrate="flag_on")
    open_g = _group_opening(rows, substrate="flag_on")
    lat = _latency_by_model(rows)
    prof = _profile_info(rows)

    lines: list[str] = []
    add = lines.append

    # 1-2. Title + header.
    add(
        "# Lab report — Featherless new-generation probe: qwen3.6-27b vs the "
        "incumbent (Task 16.1)"
    )
    add("")
    add(
        "**Decision informed:** the Phase-16 model lock (Task 16.2, "
        "`audits/audit-phase-16-model-lock.md`) — whether the newer Qwen "
        "generation should displace the incumbent `Qwen/Qwen3-32B` before any "
        "production change. **Method:** the SAME reconstructed `replays/samples/"
        "9p2i` contexts as the 14.4 sweep (opening/reply/vote item ids pinned once "
        "and re-rendered per cell), the IDENTICAL mechanical detectors, and the "
        "prompt held CONSTANT at the EXISTING `qwen3_32b` set on BOTH thinking "
        "modes — running the incumbent's set on the candidate is itself a finding "
        "(the bespoke 3.6 set is Task 16.13's). **Cost:** $0 (Featherless "
        "flat-rate)."
    )
    add("")
    add(
        "**Owner redirect (2026-07-11):** the 16.1 contract text names "
        "`qwen3.5-27b`; the owner redirected the probe mid-task to **Qwen3.6-27B** "
        "plus a second candidate **bottlecapai/ThinkingCap-Qwen3.6-27B**. The "
        "artifact names (`results-`/`report-featherless-sweep-qwen3-6-27b`) follow "
        "the ACTUAL slate. Every finding below is DISCOVERED from the committed "
        "probe rows — the generation preflight, not a hardcoded conclusion, is the "
        "arbiter."
    )
    add("")

    # 3. Served-id findings.
    add("## Served-id findings (the generation preflight is the arbiter)")
    add("")
    if not served_rows:
        add("_No served-id rows recorded._")
        add("")
    else:
        add("| label | id form tried | pinned? | served | attempts | evidence |")
        add("|---|---|---|---|---|---|")
        for r in served_rows:
            add(
                f"| {r['label']} | `{r['model']}` | "
                f"{'yes' if r.get('pinned') else 'no'} | "
                f"{'yes' if r.get('served') else 'no'} | {r.get('attempts', '—')} | "
                f"{_md_cell(str(r.get('evidence', '')))} |"
            )
        add("")
    for r in nogo_rows:
        add(
            f"**NO-GO — {r['label']}** (`{r['model']}`, forms tried "
            f"{r.get('forms_tried', [])}): {_md_cell(str(r.get('reason', '')))}"
        )
        add("")
    if nogo_rows:
        add(
            "A NO-GO is a FIRST-CLASS recorded outcome for the 16.2 lock, not a task "
            "failure: the probe records the deterministic evidence and excludes the "
            "model from the later passes rather than crashing."
        )
        add("")

    # 4. response_format verdict.
    add("## response_format verdict (json_object AND json_schema, both probed)")
    add("")
    if not rf_rows:
        add("_No response_format rows recorded (no served model)._")
        add("")
    else:
        add(
            "| model | rf_mode | schema | attempts accepted | content-was-JSON | "
            "verdict |"
        )
        add("|---|---|---|---|---|---|")
        for label in served_labels:
            for rf_mode in ("json_object", "json_schema"):
                mode_rows = [
                    r
                    for r in rf_rows
                    if r["label"] == label and r["rf_mode"] == rf_mode
                ]
                for schema_name in ("MeetingTurn", "VoteBallot"):
                    cell = [r for r in mode_rows if r["schema"] == schema_name]
                    n_acc = sum(1 for r in cell if r.get("accepted"))
                    # The verdict is PER (model, rf_mode, SCHEMA) — derived from
                    # this row's own cell, never pooled across schemas: an
                    # endpoint can accept a strict grammar for the flat
                    # VoteBallot yet reject the nested MeetingTurn, and a pooled
                    # verdict would stamp "supported" beside a 0/2 row. The
                    # rejection status is likewise DERIVED, not assumed: the
                    # 14.1-era live testing recorded a 400, but the code can
                    # drift (the probe observed 422 on the incumbent) — the
                    # verdict quotes what actually came back.
                    # Split the failures by what they can EVIDENCE: a 4xx (bar
                    # 429) that survived the discovery POST's bounded busy-body
                    # retries is a HARD rejection signal; a 5xx / 429 /
                    # status-0 transport failure is not a schema verdict at all
                    # (the committed incumbent evidence includes a mid-retry
                    # 504 gateway page beside its 422s) and must not be counted
                    # toward determinism — only reported beside it.
                    hard_codes = sorted(
                        {
                            int(r["http_status"])
                            for r in cell
                            if not r.get("accepted")
                            and 400 <= int(r["http_status"]) < 500
                            and int(r["http_status"]) != 429
                        }
                    )
                    transient_n = sum(
                        1
                        for r in cell
                        if not r.get("accepted")
                        and (
                            int(r["http_status"]) >= 500
                            or int(r["http_status"]) in (0, 429)
                        )
                    )
                    hard_s = "/".join(str(c) for c in hard_codes) or "?"
                    transient_note = (
                        f"; {transient_n} transient failure(s) recorded beside it"
                        if transient_n
                        else ""
                    )
                    if any(r.get("accepted") for r in cell):
                        verdict = "supported"
                    elif not hard_codes:
                        verdict = (
                            "inconclusive (only transient failures — 5xx/429/"
                            "transport — after bounded retries; re-run before "
                            "reading this as a capability verdict)"
                        )
                    else:
                        # A rejection is only DETERMINISTIC against a same-pass
                        # CONTROL: the json_object rows for the same model+schema
                        # ran minutes apart on the same deployment, so if they
                        # succeeded, "the model is busy" cannot explain the
                        # failures (the discovery POST also retries
                        # server_error-typed 4xx bodies before recording one).
                        # Without a passing control the cell is INCONCLUSIVE —
                        # a load spike, not a capability verdict.
                        control_ok = any(
                            r.get("accepted")
                            for r in rf_rows
                            if r["label"] == label
                            and r["rf_mode"] == "json_object"
                            and r["schema"] == schema_name
                        )
                        if rf_mode == "json_object" or control_ok:
                            verdict = (
                                f"rejected (deterministic HTTP {hard_s} across "
                                "attempts + busy-body retries; a busy-TYPED 4xx "
                                "counts as rejection here because the same-pass "
                                "json_object control succeeded — a genuinely "
                                f"busy deployment fails both shapes{transient_note})"
                                if rf_mode != "json_object"
                                else f"rejected (deterministic HTTP {hard_s} "
                                f"across attempts{transient_note})"
                            )
                        else:
                            verdict = (
                                f"inconclusive (HTTP {hard_s}, but the "
                                "json_object control also failed — retry "
                                "off-peak before reading this as a rejection)"
                            )
                    json_flags = [
                        r.get("content_is_json") for r in cell if r.get("accepted")
                    ]
                    if not json_flags:
                        json_str = "—"
                    elif all(json_flags):
                        json_str = "yes"
                    elif any(json_flags):
                        json_str = "mixed"
                    else:
                        json_str = "no"
                    add(
                        f"| {label} | {rf_mode} | {schema_name} | "
                        f"{n_acc}/{len(cell)} | {json_str} | {verdict} |"
                    )
        add("")
        inc_js = any(
            r.get("accepted")
            for r in rf_rows
            if r["label"] == PROBE_INCUMBENT_LABEL and r["rf_mode"] == "json_schema"
        )
        inc_verdict = (
            "supported for at least one schema (see the per-schema rows)"
            if inc_js
            else "rejected for every schema probed"
        )
        add(
            "Production posture (`llm/featherless_client.py` docstring, recorded "
            "2026-06-27): the incumbent rejects strict `json_schema` "
            "deterministically (a 400 at the time) and runs on `json_object`. "
            "Re-verified here same-day — the incumbent's `json_schema` verdict "
            f"above is **{inc_verdict}** (each verdict cell is per-schema and "
            "quotes the HTTP status actually observed, which may drift from the "
            "documented code); read each candidate's row beside it."
        )
        add("")

    # 5. Thinking-kwarg behavior.
    add("## Thinking-kwarg behavior (the evidence a 16.12 registry entry will encode)")
    add("")
    if not tk_rows:
        add("_No thinking-kwarg rows recorded (no served model)._")
        add("")
    else:
        add(
            "| model | kwarg | accepted | reasoning channel | channel chars | "
            "out_tokens | content head |"
        )
        add("|---|---|---|---|---|---|---|")
        for label in served_labels:
            for kwarg in ("absent", "false", "true"):
                cell = [
                    r for r in tk_rows if r["label"] == label and r["kwarg"] == kwarg
                ]
                if not cell:
                    continue
                r = cell[0]
                out_tok = r.get("out_tokens")
                add(
                    f"| {label} | {kwarg} | "
                    f"{'yes' if r.get('accepted') else 'no'} | "
                    f"{r.get('reasoning_channel') or '—'} | "
                    f"{r.get('channel_chars', 0)} | "
                    f"{out_tok if out_tok is not None else '—'} | "
                    f"{_md_cell(str(r.get('content_head', '')), 80)} |"
                )
        add("")
        for label in served_labels:
            add(_probe_thinking_prose(tk_rows, label))
            add("")

    # 6. Structured-output fidelity.
    add(
        "## Structured-output fidelity (parse-success per call kind, best-shot profile)"
    )
    add("")
    if not reply_off:
        add(
            "_No graded matrix rows (Pass 4 did not run — no served model, or the "
            "probe was interrupted before the matrix)._"
        )
        add("")
    else:
        add(
            "Reply / opening / vote parse-success per served model and mode, on the "
            "held-constant `qwen3_32b` prompt set, flag-on substrate. `fit?` uses "
            "the 14.4 bar: >=90% yes, >=50% marginal, else NO (reply parse)."
        )
        add("")
        add(
            "| model | mode | profile | reply parse | opening parse | vote parse | "
            "isolated latency | reasoning | fit? |"
        )
        add("|---|---|---|---|---|---|---|---|---|")
        for k in _ordered_cells(reply_off):
            s = reply_off[k]
            p, n = int(s["parsed"]), int(s["n"])
            pr = p / n if n else 0.0
            fit = "yes" if pr >= 0.9 else ("marginal" if pr >= 0.5 else "**NO**")
            op = open_g.get(k)
            op_s = _pct(int(op["parsed"]), int(op["n"])) if op else "—"
            vt = vote_g.get(k)
            vt_s = _pct(int(vt["parsed"]), int(vt["n"])) if vt else "—"
            latv = lat.get(k)
            lats = f"~{latv}s" if latv is not None else "—"
            pmode, pcap, think = prof.get(k, ("?", 0, 0.0))
            reason_s = f"~{think:.0f} ch" if think else "—"
            add(
                f"| {k[0]} | {k[1]} | {pmode}/{pcap} | {_pct(p, n)} | {op_s} | "
                f"{vt_s} | {lats} | {reason_s} | {fit} |"
            )
        add("")

    # 7. Opening corpus.
    add("## Opening corpus — impostor self-report")
    add("")
    if not open_g:
        add(
            "_Opening corpus skipped (no `--facts` supplied). Provide `--facts` to "
            "run the impostor self-report pass._"
        )
    else:
        add(
            "Killer opens the meeting for their own kill. `self-co-loc` = the opener "
            "placed itself at the true kill room (the opening tell); `confess` = "
            "self-incriminating free text. flag-on substrate."
        )
        add("")
        add("| model | mode | parse-success | self-co-loc | confess |")
        add("|---|---|---|---|---|")
        for k in _ordered_cells(open_g):
            s = open_g[k]
            p = int(s["parsed"])
            add(
                f"| {k[0]} | {k[1]} | {_pct(p, int(s['n']))} | "
                f"{_pct(int(s['self_co']), p)} | {_pct(int(s['confess']), p)} |"
            )
    add("")

    # 8. Reply corpus — cover 2x2.
    add("## Reply corpus — cover 2×2")
    add("")
    if not reply_off:
        add("_No reply rows recorded._")
    else:
        add(
            "Cover OFF metrics (parse / deflect / self-co-location — the impostor "
            "tell — / self-flag), then the cover OFF->ON self-co-location delta. "
            "flag-on substrate, held-constant `qwen3_32b` set."
        )
        add("")
        add("| model | mode | parse | deflect | self-co-loc | self-flag |")
        add("|---|---|---|---|---|---|")
        for k in _ordered_cells(reply_off):
            s = reply_off[k]
            p = int(s["parsed"])
            add(
                f"| {k[0]} | {k[1]} | {_pct(p, int(s['n']))} | "
                f"{_pct(int(s['deflect']), p)} | {_pct(int(s['self_co']), p)} | "
                f"{_pct(int(s['self_flag']), p)} |"
            )
        add("")
        add("Cover OFF vs ON — self-co-location (the tell):")
        add("")
        add("| model | mode | cover OFF self-co-loc | cover ON self-co-loc | Δ |")
        add("|---|---|---|---|---|")
        for k in _ordered_cells(reply_off):
            soff = reply_off[k]
            son = reply_on.get(k)
            poff, noff = int(soff["parsed"]), int(soff["n"])
            if poff == 0 or noff == 0:
                add(f"| {k[0]} | {k[1]} | — | — | — |")
                continue
            coff = _pct(int(soff["self_co"]), poff)
            pon = int(son["parsed"]) if son else 0
            non = int(son["n"]) if son else 0
            if son is None or non == 0 or pon / non < 0.5:
                con = _pct(pon, non) if son else "—"
                add(f"| {k[0]} | {k[1]} | {coff} | inconclusive (parse {con}) | — |")
                continue
            delta = 100 * (int(son["self_co"]) / pon - int(soff["self_co"]) / poff)
            add(
                f"| {k[0]} | {k[1]} | {coff} | {_pct(int(son['self_co']), pon)} | "
                f"{delta:+.0f} pp |"
            )
    add("")

    # 9. Vote corpus.
    add("## Vote corpus — parse + conversion")
    add("")
    if not vote_g:
        add("_No vote rows recorded._")
    else:
        add("`conversion` = voter picked an available impostor. flag-on substrate.")
        add("")
        add("| model | mode | parse-success | conversion |")
        add("|---|---|---|---|")
        for k in _ordered_cells(vote_g):
            s = vote_g[k]
            add(
                f"| {k[0]} | {k[1]} | {_pct(int(s['parsed']), int(s['n']))} | "
                f"{_pct(int(s['conv']), int(s['parsed']))} |"
            )
    add("")

    # 10. Latency.
    add("## Latency")
    add("")
    if not lat:
        add("_No latency samples recorded._")
    else:
        add(
            "Isolated single-turn latency (sequential micro-pass), flag-on "
            "substrate only. Candidate rows sit beside the same-day incumbent rows."
        )
        add("")
        add("| model | mode | isolated latency |")
        add("|---|---|---|")
        for k in _ordered_cells(lat):
            add(f"| {k[0]} | {k[1]} | ~{lat[k]}s |")
    add("")

    # 11. Recommendation.
    add("## Recommendation (ranked, not self-declared — 16.2 decides)")
    add("")
    if not reply_off:
        add(
            "_The graded matrix did not run, so no ranking is possible. The "
            "served-id and response_format / thinking passes above still inform the "
            "16.2 lock._"
        )
        add("")
    else:

        def _rank_key(k: tuple[str, str]) -> tuple[float, float, float, float]:
            s = reply_off[k]
            p, n = int(s["parsed"]), int(s["n"])
            parse_rate = p / n if n else 0.0
            self_co = _rate(s, "self_co")
            vt = vote_g.get(k)
            conv = (
                (int(vt["conv"]) / int(vt["parsed"]))
                if vt and int(vt["parsed"])
                else 0.0
            )
            latv = lat.get(k)
            latency = latv if latv is not None else float("inf")
            return (-parse_rate, self_co, -conv, latency)

        ranked = sorted(reply_off.keys(), key=_rank_key)
        add(
            "Ranked by: parse fitness (desc), then reply self-co-location (asc — "
            "lower is a cleaner alibi), then vote conversion (desc), then isolated "
            "latency (asc)."
        )
        add("")
        add(
            "| rank | model | mode | reply parse | self-co-loc | vote conversion | "
            "latency |"
        )
        add("|---|---|---|---|---|---|---|")
        for i, k in enumerate(ranked, 1):
            s = reply_off[k]
            p, n = int(s["parsed"]), int(s["n"])
            vt = vote_g.get(k)
            conv_s = _pct(int(vt["conv"]), int(vt["parsed"])) if vt else "—"
            latv = lat.get(k)
            lats = f"~{latv}s" if latv is not None else "—"
            add(
                f"| {i} | {k[0]} | {k[1]} | {_pct(p, n)} | "
                f"{_pct(int(s['self_co']), p)} | {conv_s} | {lats} |"
            )
        add("")
    cand_served = [c for c in served_labels if c in PROBE_CANDIDATE_LABELS]
    if cand_served:
        # The served FORM comes from the rows (pass 1 may have adopted an
        # alternate revision when the pinned guess 404'd), never from the pin.
        add(
            "Served candidate id(s): "
            + ", ".join(f"`{_probe_served_form(rows, c)}` ({c})" for c in cand_served)
            + "."
        )
    else:
        add("_No candidate id served — see the NO-GO evidence above._")
    add("")
    add("**Open risks:**")
    add("")
    risks = [
        "The prompt set is the INCUMBENT's (`qwen3_32b`), held constant across both "
        "models and modes; the bespoke 3.6 set is Task 16.13's, so candidate "
        "numbers may UNDERSTATE a model authored against its own templates.",
        "The isolated-turn parse / self-co-location / conversion metrics are "
        "PROXIES, not the live R-gate — a model can look better in isolation yet "
        "behave differently in a full noisy game.",
        "The new generation's thinking DEFAULT posture (it reasons unless "
        "`enable_thinking` is pinned false) means a production integration must PIN "
        "`enable_thinking` explicitly (or strip the inline `</think>` reasoning), or "
        "reasoning leaks into recorded state.",
        "The production registry entry does NOT exist yet (Task 16.12, post-lock): "
        "the probe carries the Qwen kwarg + the inline reasoning split sweep-locally; "
        "the fail-loud `_THINKING_KWARG_BY_MODEL` classification is 16.12's.",
    ]
    if nogo_rows:
        risks.append(
            "ThinkingCap-Qwen3.6-27B is a documented NO-GO (its deployment 400s on "
            "the chat template / every generation — see the served-id evidence), a "
            "first-class outcome for 16.2, not a probe failure."
        )
    for risk in risks:
        add(f"- {risk}")
    add("")
    add("This report recommends; the 16.2 lock decides.")
    add("")

    # 12. Reproduce.
    add("## Reproduce")
    add("")
    add("```")
    add("# facts (offline, $0):")
    add("PYTHONPATH=. uv run python audits/workflows/extract_gameplay_facts.py")
    add("# probe run (needs FEATHERLESS_API_KEY; hours-scale, $0 flat-rate):")
    add("uv run python -m experiments.lab.featherless_sweep probe \\")
    add("    --sample-dir replays/samples/9p2i \\")
    add("    --facts $TMPDIR/ailibi-gameplay-facts-9p2i.json")
    add("# regenerate THIS report from the committed rows:")
    add("uv run python -m experiments.lab.featherless_sweep probe-report")
    add("```")
    add("")

    # 13. Footer.
    add(
        "**Harness/raw:** `experiments/lab/featherless_sweep.py` + "
        "`experiments/lab/results-featherless-sweep-qwen3-6-27b.jsonl` (served-id + "
        "response_format + thinking-kwarg discovery rows and the graded matrix "
        "cells; every number in this report regenerates from those rows)."
    )
    add("")

    PROBE_REPORT.write_text("\n".join(lines))
    print(f"wrote {PROBE_REPORT}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    r = sub.add_parser("run", help="run the full sweep matrix")
    r.add_argument("--sample-dir", type=Path, default=Path("replays/samples/9p2i"))
    r.add_argument(
        "--facts",
        type=Path,
        default=None,
        help="extractor facts JSON (kill ground truth) enabling the opening "
        "corpus; produced by audits/workflows/extract_gameplay_facts.py.",
    )
    r.add_argument("--reply-cap", type=int, default=16)
    r.add_argument("--vote-limit", type=int, default=8)
    r.add_argument("--opening-cap", type=int, default=10)
    r.add_argument(
        "--concurrency",
        type=int,
        default=2,
        help="Concurrent requests. Default 2: the plan caps at 4 concurrency "
        "units and a 32B request costs 2 units, so >2 risks 429s.",
    )
    r.add_argument("--latency-samples", type=int, default=2)
    r.add_argument(
        "--substrates",
        type=str,
        default="on",
        help="Comma list of substrates to run. Only 'on' remains runnable: the "
        "flag-OFF substrate is retired since Task 14.9 (requesting 'off' "
        "fails loud).",
    )
    r.add_argument("--base-url", type=str, default=None)
    r.add_argument(
        "--models",
        type=str,
        default=None,
        help="Comma list of model LABELS to run (default all). Use with --append "
        "to re-run a single model after an outage and merge it back, e.g. "
        "--models cydonia-24b --append.",
    )
    r.add_argument(
        "--append",
        action="store_true",
        help="Append to the results file instead of truncating (for a --models "
        "partial re-run merged into an existing matrix).",
    )
    r.add_argument(
        "--modes",
        type=str,
        default=None,
        help="Comma list restricting the thinking axis: non_thinking, thinking, or "
        "both (default both / the full per-model axis). A bespoke set maps to ONE "
        "(model, mode), so pair e.g. --prompt-set qwen3_32b --modes non_thinking and "
        "--prompt-set qwen3_32b_thinking --modes thinking on the same model.",
    )
    r.add_argument(
        "--prompt-set",
        type=str,
        default=None,
        help="Render through this BESPOKE prompt set (Task 14.5 A/B axis), e.g. "
        "qwen3_32b. Omit to keep the 14.4 behavior byte-identical: the pinned 9B "
        "templates render and the non-Qwen slate routes through the bare-send. A "
        "bespoke set renders its own templates (build_prompt_renderers) and routes "
        "the non-Qwen slate through the real adapter; every row is stamped with "
        "its prompt_set. Use with --append + --models <set's model> for a clean "
        "new-set-vs-pinned-9B A/B on the set's own model.",
    )
    sub.add_parser("report", help="(re)generate the report from the results jsonl")

    # ── Phase-16 probe (Task 16.1): a SEPARATE pipeline over PROBE_RESULTS ──
    p = sub.add_parser(
        "probe",
        help="probe the owner-directed new-generation slate (Qwen3.6-27B + "
        "ThinkingCap) — served-id / response_format / thinking-kwarg discovery "
        "then the graded matrix, into results-featherless-sweep-qwen3-6-27b.jsonl.",
    )
    p.add_argument("--sample-dir", type=Path, default=Path("replays/samples/9p2i"))
    p.add_argument(
        "--facts",
        type=Path,
        default=None,
        help="extractor facts JSON (kill ground truth) enabling the opening "
        "corpus; produced by audits/workflows/extract_gameplay_facts.py.",
    )
    p.add_argument("--reply-cap", type=int, default=16)
    p.add_argument("--vote-limit", type=int, default=8)
    p.add_argument("--opening-cap", type=int, default=10)
    p.add_argument(
        "--concurrency",
        type=int,
        default=2,
        help="Concurrent requests. Default 2: the plan caps at 4 concurrency "
        "units and a 32B request costs 2 units, so >2 risks 429s.",
    )
    p.add_argument("--latency-samples", type=int, default=2)
    p.add_argument("--base-url", type=str, default=None)
    # NO --append here, deliberately: `probe` carries no --models/--modes
    # selection, so an append could ONLY duplicate every discovery + matrix row
    # for the same pinned contexts and silently corrupt probe-report's rates
    # (unlike `run`, whose --models/--modes filters make a merge meaningful).
    # A partial recovery is a driver-level operation over the harness cell
    # functions on the same pinned ids, replacing rows — not a CLI re-append.
    sub.add_parser(
        "probe-report",
        help="(re)generate the probe report from "
        "results-featherless-sweep-qwen3-6-27b.jsonl",
    )
    args = parser.parse_args()

    if args.mode == "report":
        return write_report()
    if args.mode == "probe-report":
        return write_probe_report()

    api_key = os.environ.get("FEATHERLESS_API_KEY")
    if not api_key:
        raise SystemExit(f"{args.mode} requires FEATHERLESS_API_KEY in the env.")

    if args.mode == "probe":
        # Select the three probe specs from SLATE (candidates + incumbent) and run
        # the 16.1 probe over PROBE_RESULTS with the held-constant qwen3_32b set.
        # Substrate is single all-ON (14.9); both thinking modes run (no mode
        # filter) — the _SET_OWNER restriction is deliberately bypassed here (it
        # stays intact for the `run` subcommand above).
        probe_models = tuple(s for s in SLATE if s.label in _PROBE_LABELS)
        probe_cfg = SweepConfig(
            sample_dir=args.sample_dir,
            facts_path=args.facts,
            reply_cap=args.reply_cap,
            vote_limit=args.vote_limit,
            opening_cap=args.opening_cap,
            concurrency=args.concurrency,
            latency_samples=args.latency_samples,
            substrates=(True,),
            base_url=args.base_url,
            results_path=PROBE_RESULTS,
            models=probe_models,
            prompt_set=PROBE_PROMPT_SET,
        )
        rc = asyncio.run(run_probe(probe_cfg, api_key=api_key))
        if rc == 0:
            write_probe_report()
        return rc
    # Validate the substrate tokens exactly (a typo like "onn" must not silently
    # be treated as flag-OFF and mislabel the operator-run matrix).
    tokens = [t.strip().lower() for t in args.substrates.split(",") if t.strip()]
    bad = [t for t in tokens if t not in ("off", "on")]
    if bad or not tokens:
        raise SystemExit(
            f"--substrates must be a comma list of 'off'/'on' (got {args.substrates!r}"
            + (f"; invalid: {bad}" if bad else "; empty")
            + ")"
        )
    substrates = tuple(t == "on" for t in tokens)
    mode_filter: tuple[bool, ...] | None = None
    if args.modes:
        mtokens = [t.strip().lower() for t in args.modes.split(",") if t.strip()]
        mbad = [t for t in mtokens if t not in ("non_thinking", "thinking")]
        if mbad or not mtokens:
            raise SystemExit(
                f"--modes must be a comma list of 'non_thinking'/'thinking' (got "
                f"{args.modes!r}" + (f"; invalid: {mbad}" if mbad else "; empty") + ")"
            )
        mode_filter = tuple(t == "thinking" for t in mtokens)
    # The `run` default is the 14.4 slate ONLY — the Phase-16 probe candidates are
    # appended to SLATE for the `probe` subcommand but EXCLUDED here so `run` stays
    # byte-identical (an explicit --models can still name them).
    models = tuple(s for s in SLATE if s.label not in PROBE_CANDIDATE_LABELS)
    if args.models:
        want = {m.strip() for m in args.models.split(",") if m.strip()}
        models = tuple(s for s in SLATE if s.label in want)
        unknown = want - {s.label for s in SLATE}
        if unknown or not models:
            raise SystemExit(
                f"--models: unknown label(s) {sorted(unknown)}; "
                f"valid: {[s.label for s in SLATE]}"
            )
    # A bespoke ``--prompt-set`` run must target ONLY that set's owner model/mode
    # (the A/B compares each set on its own model; the report groups by prompt_set).
    # Auto-restrict when --models / --modes are omitted; fail loud on a mismatch
    # rather than silently rendering the set across the slate (AGENTS.md: no silent
    # fallbacks) — which would waste a multi-hour run on invalid comparison rows.
    if args.prompt_set is not None:
        owner = _SET_OWNER.get(args.prompt_set)
        if owner is None:
            raise SystemExit(
                f"--prompt-set {args.prompt_set!r} is not a known bespoke set "
                f"(valid: {sorted(_SET_OWNER)})"
            )
        owner_label, owner_thinking = owner
        owner_mode = _mode_label(owner_thinking)
        if not args.models:
            models = tuple(s for s in SLATE if s.label == owner_label)
            print(
                f"NOTE: --prompt-set {args.prompt_set} -> restricting --models to "
                f"its owner {owner_label} (the A/B runs each set on its own model).",
                flush=True,
            )
        elif [s.label for s in models] != [owner_label]:
            raise SystemExit(
                f"--prompt-set {args.prompt_set} owns model {owner_label!r}, but "
                f"--models is {[s.label for s in models]}. A bespoke A/B must run "
                f"ONLY on its owner model (the report groups by prompt_set); rerun "
                f"with --models {owner_label}."
            )
        if mode_filter is None:
            mode_filter = (owner_thinking,)
            print(
                f"NOTE: --prompt-set {args.prompt_set} -> setting "
                f"--modes {owner_mode}.",
                flush=True,
            )
        elif mode_filter != (owner_thinking,):
            raise SystemExit(
                f"--prompt-set {args.prompt_set} is the {owner_mode} set; --modes "
                f"must be {owner_mode} (got {[_mode_label(m) for m in mode_filter]})."
            )
    cfg = SweepConfig(
        sample_dir=args.sample_dir,
        facts_path=args.facts,
        reply_cap=args.reply_cap,
        vote_limit=args.vote_limit,
        opening_cap=args.opening_cap,
        concurrency=args.concurrency,
        latency_samples=args.latency_samples,
        substrates=substrates,
        base_url=args.base_url,
        models=models,
        append=args.append,
        prompt_set=args.prompt_set,
        mode_filter=mode_filter,
    )
    rc = asyncio.run(run_sweep(cfg, api_key=api_key))
    if rc == 0:
        write_report()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
