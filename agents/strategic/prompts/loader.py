"""Jinja loader for the four strategic prompt templates (Task 3.9 C-4).

The four ``.j2`` templates under ``agents/strategic/prompts/`` are the
canonical phase-1 report, accusation-round, and vote-ballot prompts
consumed by :class:`meetings.manager.MeetingManager`. This module wraps
them in a single strict-undefined :class:`jinja2.Environment` and exposes
one named Python callable per template so the wider codebase never touches
the filesystem directly.

Strict-undefined behavior
=========================

The :class:`jinja2.StrictUndefined` policy means a missing or typo'd
template kwarg raises :class:`jinja2.UndefinedError` at render time
instead of silently rendering an empty string. ``trim_blocks=True`` /
``lstrip_blocks=True`` keep the rendered Markdown free of stray
whitespace that the templates' own ``{%- ... -%}`` markers already
intend. ``autoescape=False`` is correct here because the prompts are
plain-text LLM input, not HTML.

Templates remain frozen
=======================

The four ``.j2`` files are out of scope for Task 3.9 — the loader reads
them as-is. If a template needs a new kwarg, the wrapper callable's
signature is updated here; the template itself is not edited from this
module.

Per-model prompt sets (Task 14.2)
=================================

The four templates live under a per-model *set* subdirectory rather than
flat next to this module (owner decision 2026-06-25 — per-model prompt
sets). The frozen ``qwen3.5:9b`` reference set is :data:`DEFAULT_PROMPT_SET`
(directory ``qwen3_5_9b/``); :func:`build_environment` resolves a set name
to its subdirectory and builds the strict-undefined
:class:`jinja2.Environment` against it. The active set is selected by the
:data:`ENV_PROMPT_SET` environment variable (``AILIBI_PROMPT_SET``),
defaulting to :data:`DEFAULT_PROMPT_SET` so existing renders are
byte-identical. An unknown set name (no matching subdirectory) raises
:class:`ValueError` — there is no silent fallback (AGENTS.md §"No silent
fallbacks"). The ``*_TEMPLATE`` filename constants are shared across sets;
only the directory varies.

The default is byte-identity, not a recommendation. Every operational surface
runs :data:`OPERATIONAL_BASELINE_PROMPT_SET` (``qwen3_6_27b``, the bespoke set
for the canonical Featherless model), so a bare environment taking the 9B
default is running a prompt family two generations behind the reports. The
default VALUE stays — moving it would move committed prompt bytes — so
:func:`resolve_prompt_set` says so instead: under a REAL provider a bare
fallback emits one stderr line, once per process, naming
``AILIBI_PROMPT_SET`` and the baseline set. Under the fake provider it is
silent: the fake runs no model, so nothing there can be a generation behind
anything, and a first-run warning that describes no risk is noise (Task 19.6
introduced the notice, Task 20.5 aimed it).

The module-level wrapper callables render through the import-time process
default :data:`_ENV` (selected by ``AILIBI_PROMPT_SET`` at import). Each also
accepts an explicit ``environment`` so a caller can pin a specific set's
:class:`jinja2.Environment` per call — :func:`build_prompt_renderers` uses this
to bind the four renderers to ONE resolved set at construction time, so a runner
renders and records the SAME set even when ``AILIBI_PROMPT_SET`` is changed
in-process after this module is imported (PR #203 review).

Per-template wrapper signatures
===============================

Each wrapper conforms to the :class:`~meetings.render_contract.ReportPromptRenderer`,
:class:`~meetings.render_contract.StatementPromptRenderer`, or
:class:`~meetings.render_contract.VotePromptRenderer` Protocol from
:mod:`meetings.render_contract` so the loader-built callables can be passed
straight into :class:`~meetings.manager.MeetingManager` without an
intermediate adapter layer.

The impostor-answer template arm (Task 18.10)
=============================================

The gate's highest-variance arm, built inert: behind the default-OFF
:func:`impostor_roll_call_enabled` lever (``AILIBI_IMPOSTOR_ROLL_CALL``),
the two impostor-facing templates are swapped for their ``*_roll_call.j2``
VARIANT siblings — the impostor opening and reply ANSWER the whereabouts
ask with a structured self-placement instead of the hard-coded
``"observations": []`` (audits/audit-phase-18-planning.md §3.4, the
structural refusal). Routing is by template FILENAME: the wrapper
callables take an explicit ``template_name`` and
:func:`build_prompt_renderers` resolves the lever ONCE at construction and
binds the variant filenames into the returned bundle, so a runner renders
and stamps one consistent decision (the PR #203 binding discipline applied
to the lever). The variant templates exist only in the ``qwen3_6_27b``
set; lever ON with any other set fails loud at
:func:`build_prompt_renderers` — no silent fallback. Lever OFF (the
default) binds the exact default filenames, so the rendered prompt set is
byte-identical to the committed registry. The matching provenance side
lives in :data:`orchestrator.game.IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`
(recorded ``prompt_versions`` come from that registry, never from this
loader).

The testimony-shapes arm
========================

The default-OFF :func:`meetings.constants.testimony_shapes_enabled` lever
offers the crew turn bodies one witnessed-KILL shape — the strongest testimony
the game produces, which no template offers at all with the lever OFF. It
RE-BODIES rather than swaps: the block is guarded inside the served
``crewmate_report.j2`` / ``accusation_round.j2``, so it cannot drift from the
body it lives in and it composes with a sibling arm's block in the same file.
Routing is therefore a render KWARG, resolved once in
:func:`build_prompt_renderers` and bound into the partials at construction, and
its provenance side is
:data:`orchestrator.game.TESTIMONY_SHAPES_PROMPT_VERSION_SETS`.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, replace
from functools import lru_cache, partial
from pathlib import Path
from types import MappingProxyType
from typing import Final, Literal

from jinja2 import (
    Environment,
    FileSystemLoader,
    StrictUndefined,
    TemplateNotFound,
    TemplateSyntaxError,
)
from jinja2 import nodes

from llm.provider import ENV_PROVIDER, PROVIDER_FAKE
from meetings.constants import ENV_TESTIMONY_SHAPES, testimony_shapes_enabled
from meetings.corroboration import MeetingTestimonyLedger
from meetings.render_contract import (
    PromptRenderInputs,
    ReporterContext,
    ReportPromptRenderer,
    StatementPromptRenderer,
    SuspicionEntry,
    VotePromptRenderer,
)
from meetings.schemas import (
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    PlayerId,
    TurnKind,
)
from meetings.transcript import CANONICAL_ROOM_NEIGHBORS, is_weak_contradiction
from observation.public_map import PublicMapView

# Root holding the per-model prompt-set subdirectories (Task 14.2). The four
# ``.j2`` templates no longer live flat next to this module; each set is a
# subdirectory (``qwen3_5_9b/`` is the frozen 9B reference set).
_PROMPTS_ROOT: Final[Path] = Path(__file__).resolve().parent

# The frozen ``qwen3.5:9b`` reference set — the default so existing renders are
# byte-identical (owner decision 2026-06-25). Selected by ``AILIBI_PROMPT_SET``.
DEFAULT_PROMPT_SET: Final[str] = "qwen3_5_9b"
ENV_PROMPT_SET: Final[str] = "AILIBI_PROMPT_SET"

# The set every operational surface actually runs (Task 19.6): the bespoke
# 27B set recorded against the canonical Featherless model ``Qwen/Qwen3.6-27B``
# (AGENTS.md §"Environment setup"; the baseline-6 recording env in
# training/reports/report-finalist-eval.md is literally
# ``AILIBI_LLM_PROVIDER=featherless AILIBI_PROMPT_SET=qwen3_6_27b``). It is NOT
# the default — :data:`DEFAULT_PROMPT_SET` stays the frozen 9B set so every
# committed render stays byte-identical (owner decision 2026-06-25) — but it is
# named in the bare-environment notice below so a bare shell cannot quietly run
# a prompt family two generations behind what the reports describe.
OPERATIONAL_BASELINE_PROMPT_SET: Final[str] = "qwen3_6_27b"


@lru_cache(maxsize=None)
def _notify_bare_prompt_set_fallback(prompt_set: str) -> None:
    """Emit the bare-environment prompt-set notice on stderr, once per process.

    The rule, in two halves. Under a REAL provider the notice is worth saying:
    the bare default is :data:`DEFAULT_PROMPT_SET`, a different prompt family
    from the :data:`OPERATIONAL_BASELINE_PROMPT_SET` every report and every
    committed sample set was recorded against, and a prompt family written for
    another model is a real difference in how that model behaves. Under the
    deterministic FAKE provider the sentence has nothing to be about: the fake
    fills the response schema with placeholder fields (their filler strings
    seeded by a hash of the prompt, so the bytes do move) and runs no model at
    all, so no generation exists for the prompt family to lag two behind. The
    notice also fires only where the DEFAULT set was taken — under the fake,
    the exact configuration the committed goldens reproduce.
    :func:`resolve_prompt_set` owns that provider gate and never reaches this
    function on the fake path; this function owns the once-per-process half.

    The :func:`functools.lru_cache` memo is what collapses the repeats — the
    resolution points are per-process and per-runner (the import-time
    :data:`_ENV`, ``build_prompt_renderers``,
    ``orchestrator.game.build_default_meeting_runner``), so a five-game
    tournament used to print the same line six times. It is keyed on the
    resolved set alone, so switching real providers mid-process does not repeat
    a line that says nothing about the provider, and unbounded, so nothing is
    ever evicted back into loudness. Its ``cache_clear()`` is the reset seam
    tests drive. A de-duplication memo for a diagnostic is not the
    module-level mutable state AGENTS.md §"No global state" forbids: no caller
    reads a value back out of it, it changes no return value, and it is
    resettable. stderr, never stdout, keeps the machine-readable stdout the CLI
    surfaces emit uncontaminated.

    Provenance: notice added at Task 19.6, provider-gated and deduped at 20.5.
    """

    print(
        f"agents.strategic.prompts.loader: {ENV_PROMPT_SET} is unset — falling "
        f"back to the frozen reference set {prompt_set!r}, two "
        f"generations behind the operational baseline "
        f"{OPERATIONAL_BASELINE_PROMPT_SET!r}; export "
        f"{ENV_PROMPT_SET}={OPERATIONAL_BASELINE_PROMPT_SET} to run the "
        f"baseline set.",
        file=sys.stderr,
    )


def resolve_prompt_set(
    prompt_set: str | None = None,
    *,
    env: Mapping[str, str] | None = None,
) -> str:
    """Resolve the active prompt-set name (Task 14.2).

    An explicit ``prompt_set`` wins; otherwise the :data:`ENV_PROMPT_SET`
    environment variable is consulted, defaulting to :data:`DEFAULT_PROMPT_SET`
    (the frozen 9B set) when unset or empty. The ``env`` argument lets tests
    select a set deterministically without mutating ``os.environ``.

    The bare-environment path is loud where that means something. The default
    value itself is unchanged — it must stay :data:`DEFAULT_PROMPT_SET` for
    byte-identity with every committed render — but taking it under a real
    provider, *without* an ``AILIBI_PROMPT_SET`` override, emits one stderr
    line naming the variable and :data:`OPERATIONAL_BASELINE_PROMPT_SET`,
    because that run is sending a prompt family two generations behind the one
    every report was recorded against. Three paths are silent, each because it
    is not that situation: an explicit ``prompt_set`` argument and a non-empty
    ``AILIBI_PROMPT_SET`` are choices rather than fallbacks, and under the
    deterministic fake provider (the default, and everything CI runs) there is
    no model for the rendered family to be a generation behind. The provider is
    read from the SAME mapping the set is — a test or
    a caller passing ``env=`` is never second-guessed against the ambient
    shell — using ``llm.provider``'s own constants and resolution expression so
    the two cannot drift apart. The notice itself is once per process
    (:func:`_notify_bare_prompt_set_fallback`).
    """

    if prompt_set is not None:
        return prompt_set
    environment = env if env is not None else os.environ
    selected = environment.get(ENV_PROMPT_SET, "").strip()
    if selected:
        return selected
    # Gate first, dedupe second: the fake path records nothing in the memo, so
    # a later real-provider resolution in the same process still gets its line.
    provider = environment.get(ENV_PROVIDER, PROVIDER_FAKE).strip().lower()
    if provider != PROVIDER_FAKE:
        _notify_bare_prompt_set_fallback(DEFAULT_PROMPT_SET)
    return DEFAULT_PROMPT_SET


# How many distinct (prompt set, templates root) environments are held at once.
# A run serves one root and a handful of sets, so the bound never evicts a live
# one; it caps what a caller building against scratch roots (a test tree, the
# byte-golden perturbation leg) can retain for the life of the process.
_ENVIRONMENT_CACHE_SIZE: Final[int] = 32


@lru_cache(maxsize=_ENVIRONMENT_CACHE_SIZE)
def _environment_for_set(name: str, root: Path) -> Environment:
    """The one strict-undefined environment serving set ``name`` under ``root``.

    Keyed on the set and the root and nothing else: an environment holds that
    set's template bytes and their compiled code — no game state, nothing
    per-runner — and the Task-18.10 roll-call lever selects template FILENAMES
    in :func:`build_prompt_renderers`, not anything the environment carries.
    Reached only through :func:`build_environment`, which resolves the set name
    and validates its directory first. Task 20.19 (finding C-42).
    """

    return Environment(
        loader=FileSystemLoader(root / name),
        autoescape=False,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def build_environment(
    prompt_set: str | None = None,
    *,
    root: Path = _PROMPTS_ROOT,
    env: Mapping[str, str] | None = None,
) -> Environment:
    """Build a strict-undefined :class:`jinja2.Environment` for a prompt set.

    Resolves ``prompt_set`` (via :func:`resolve_prompt_set`) to a subdirectory
    of ``root`` and returns that set's environment. An unknown set — no matching
    subdirectory — raises :class:`ValueError`; there is no silent fallback
    (AGENTS.md §"No silent fallbacks"). The strict-undefined / trim / lstrip /
    no-autoescape policy is identical across sets, so a content-preserving move
    of the 9B templates renders byte-identically.

    Both the resolution and the directory check run on every call, above the
    memo that :func:`_environment_for_set` holds: a caller that changes
    ``AILIBI_PROMPT_SET`` in-process still gets its new set, a set whose
    directory is absent still fails loud however often it was built before, and
    the bare-fallback notice fires exactly as often as it did when every call
    built a fresh environment.
    """

    name = resolve_prompt_set(prompt_set, env=env)
    directory = root / name
    if not directory.is_dir():
        raise ValueError(
            f"Unknown prompt set {name!r}: no template directory at {directory}"
        )
    return _environment_for_set(name, root)


# The process-default environment, bound to the active set at import time. The
# wrapper callables below render through it so call sites stay unchanged; the
# set is selected by ``AILIBI_PROMPT_SET`` (default: the frozen 9B set).
_ENV: Final[Environment] = build_environment()

CREWMATE_REPORT_TEMPLATE: Final[str] = "crewmate_report.j2"
IMPOSTOR_REPORT_TEMPLATE: Final[str] = "impostor_report.j2"
ACCUSATION_ROUND_TEMPLATE: Final[str] = "accusation_round.j2"
VOTE_BALLOT_TEMPLATE: Final[str] = "vote_ballot.j2"

# Task 18.10 impostor-answer VARIANT filenames (qwen3_6_27b only): the impostor
# opening and reply answer the whereabouts ask with a structured self-placement
# instead of the hard-coded ``"observations": []``. Selected ONLY through the
# default-OFF :func:`impostor_roll_call_enabled` lever; the default filename
# constants above stay the served path everywhere else.
IMPOSTOR_REPORT_ROLL_CALL_TEMPLATE: Final[str] = "impostor_report_roll_call.j2"
ACCUSATION_ROUND_ROLL_CALL_TEMPLATE: Final[str] = "accusation_round_roll_call.j2"

# The Task 18.10 impostor-answer lever — the one LIVE substrate toggle, DEFAULT-OFF.
# Registered in ``orchestrator.replay._TOGGLEABLE_LEVER_RESOLVERS`` (through a
# local mirror, so a replay-only consumer need not build this module's Jinja
# environment); the CREW-ONLY ruling did not ship its arm, so it never graduated.
ENV_IMPOSTOR_ROLL_CALL: Final[str] = "AILIBI_IMPOSTOR_ROLL_CALL"
_IMPOSTOR_ROLL_CALL_FLAG_TRUE: Final[frozenset[str]] = frozenset(
    {"1", "true", "yes", "on"}
)


def impostor_roll_call_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Whether the Task 18.10 impostor-answer lever is ON. DEFAULT OFF.

    Reads :data:`ENV_IMPOSTOR_ROLL_CALL` from ``env`` (defaulting to the real
    process environment). Default OFF: an
    unset / empty / unrecognised value is ``False`` so the loader keeps serving
    the exact default template filenames and the rendered prompt set stays
    byte-identical to the committed registry (the committed recordings and the
    ``tests/meetings/test_prompt_byte_golden.py`` reconstruction stay clean).
    Accepts ``1/true/yes/on`` (case-insensitive). The ``env`` argument lets
    tests toggle the lever deterministically without mutating ``os.environ``.

    ON swaps the two impostor-facing templates for their ``*_roll_call.j2``
    variant siblings (:data:`IMPOSTOR_REPORT_ROLL_CALL_TEMPLATE` /
    :data:`ACCUSATION_ROUND_ROLL_CALL_TEMPLATE`, authored only in the
    ``qwen3_6_27b`` set): the impostor opening and reply ANSWER the
    whereabouts ask with one structured ``whereabouts`` self-placement — the
    two-tier design lets the claim be a lie, manufacturing exactly the
    contradiction material the alibi rules prosecute
    (audits/audit-phase-18-planning.md §3.4) — at the measured risk of the
    >=44% self-flag class the prompt ladder closed. The 18.11 probe measures
    both (pre-registered bar (c): probe impostor win >= 0.20 AND STRONG
    self-flag rate <= 0.25 of answered impostor roll-calls); the graduation
    flip, if ruled, is Task 18.12. Recorded provenance moves WITH the lever
    through :func:`orchestrator.game.prompt_versions_for_set`
    (:data:`~orchestrator.game.IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`), so
    variant bytes and default bytes never share a version stamp
    (audits/audit-phase-17-absence-gate.md Ruling 3(d)).
    """

    environment = env if env is not None else os.environ
    return (
        environment.get(ENV_IMPOSTOR_ROLL_CALL, "").strip().lower()
        in _IMPOSTOR_ROLL_CALL_FLAG_TRUE
    )


# --------------------------------------------------------------------------- #
# v4 render inputs: the map card, the evidence split, the impostor count       #
# --------------------------------------------------------------------------- #


# The prose name each walkable room answers to, paired with its id everywhere
# the map card names a room. This is the ONLY authored surface that spells a
# room out, so it is what anchors the register agents speak rooms in; the id
# rides alongside because the JSON contract asks for the id. Frozen DATA, the
# same discipline CANONICAL_ROOM_NEIGHBORS uses -- a test cross-pins it against
# ``engine.world.load_canonical_map()``, so the card cannot drift off the map.
CANONICAL_ROOM_DISPLAY_NAMES: Final[Mapping[str, str]] = MappingProxyType(
    {
        "ADMIN": "Admin",
        "CAFETERIA": "Cafeteria",
        "EAST_HALL": "East Hallway",
        "ENGINEERING": "Engineering",
        "LABS": "Labs",
        "MEDBAY": "MedBay",
        "REACTOR": "Reactor",
        "STORAGE": "Storage",
        "UPPER_HALL": "Upper Hall",
        "WEST_HALL": "West Hallway",
    }
)


def _named_room(room: str, names: Mapping[str, str]) -> str:
    """Render one room as ``Prose Name (ROOM_ID)``.

    An unnamed room raises rather than falling back to the bare id: a card that
    silently drops the prose half would un-anchor the register it exists to set
    (AGENTS.md "no silent fallbacks").
    """

    if room not in names:
        raise ValueError(
            f"room {room!r} has no display name; CANONICAL_ROOM_DISPLAY_NAMES "
            f"must name every walkable room the map card renders"
        )
    return f"{names[room]} ({room})"


def _map_card_from_neighbors(
    neighbors: Mapping[str, Iterable[str]],
    *,
    names: Mapping[str, str] = CANONICAL_ROOM_DISPLAY_NAMES,
) -> str:
    """Render the room-and-doorway card from a walkable-room adjacency table."""

    lines = [
        "Rooms and doors. Every door below is ONE tick of walking, so two "
        "players in rooms that share a door can be one tick apart:"
    ]
    for room in sorted(neighbors):
        doors = ", ".join(_named_room(n, names) for n in sorted(neighbors[room]))
        lines.append(f"- {_named_room(room, names)}: {doors}")
    return "\n".join(lines)


def render_map_card(map_view: PublicMapView) -> str:
    """Render the compact adjacency card every meeting template shows.

    One header line stating the one-tick doorway fact, then one line per
    walkable room, each room written ``Prose Name (ROOM_ID)`` so the table has
    an authored spelling to speak and the id the JSON contract asks for. Reads
    :attr:`PublicMapView.room_neighbors` and nothing else: ``vent_graph`` and
    ``vent_rooms`` are impostor-only knowledge the same public view happens to
    carry, and publishing them to the table would turn a legibility fix into a
    firewall breach.
    """

    return _map_card_from_neighbors(map_view.room_neighbors)


# The card every meeting renders. Built from
# :data:`meetings.transcript.CANONICAL_ROOM_NEIGHBORS` -- the same frozen table
# the contradiction detector arbitrates one-tick adjacency with, and the only
# room graph reachable from ``agents/`` without crossing the §1.3 observation
# firewall into ``engine/``. A test cross-pins it against
# ``render_map_card(public_map_from_engine_map(load_canonical_map()))``, so the
# agents' card, the detector's table and the engine map cannot disagree.
CANONICAL_MAP_CARD: Final[str] = _map_card_from_neighbors(CANONICAL_ROOM_NEIGHBORS)


PromptEvidenceCategory = Literal["role_proof", "cross_statement", "weak_signal"]
"""What kind of evidence a flag is, in the words the prompt groups it under."""

# The role-proving kinds: a grounded vent sighting names an impostor outright.
_ROLE_PROOF_KINDS: Final[frozenset[str]] = frozenset({"vent_sighting"})
# Two DIFFERENT public statements that cannot both be true. Whether such a flag
# reads as a conflict or as a weak signal is the detector's own weak stamp.
_CROSS_STATEMENT_KINDS: Final[frozenset[str]] = frozenset(
    {"alibi_conflict", "alibi_vs_sighting", "alibi_vs_physical"}
)


def classify_flag_for_prompt(flag: ContradictionRef) -> PromptEvidenceCategory:
    """Classify one flag into the group the prompt shows it under.

    The rule table is ``api.schemas.classify_evidence``'s, re-implemented here
    rather than imported: this is agent-facing render code and ``agents/`` does
    not import ``api/``. A test asserts the two derivations produce identical
    per-category counts over every flag of both committed sample sets, which is
    evidence precisely because neither side calls the other. The weak predicate
    is NOT re-implemented -- :func:`meetings.transcript.is_weak_contradiction`
    is imported, so the marker reader stays beside the marker writer.

    An unrecognised kind raises rather than bucketing (AGENTS.md "no silent
    fallbacks"). ``ContradictionRef.kind`` is a closed ``Literal`` today, so the
    raise is unreachable until a new kind lands -- which is exactly when a
    prompt that silently called it a conflict would start lying.
    """

    if flag.kind not in _ROLE_PROOF_KINDS and flag.kind not in _CROSS_STATEMENT_KINDS:
        raise ValueError(
            f"unclassifiable flag kind {flag.kind!r} "
            f"(contradiction_id={flag.contradiction_id!r}); the prompt evidence "
            "taxonomy has no group for it — add the rule rather than widening a "
            "bucket"
        )
    if flag.kind in _ROLE_PROOF_KINDS or flag.event_a_id == flag.event_b_id:
        return "role_proof"
    if is_weak_contradiction(flag):
        return "weak_signal"
    return "cross_statement"


@dataclass(frozen=True)
class _FlagGroups:
    """The three flag groups a template loops over, computed in Python."""

    proof: tuple[ContradictionRef, ...] = ()
    conflicting: tuple[ContradictionRef, ...] = ()
    weak: tuple[ContradictionRef, ...] = ()


def _group_flags(flags: Iterable[ContradictionRef]) -> _FlagGroups:
    """Split flags into proof / conflicting accounts / weak signals, in order."""

    buckets: dict[PromptEvidenceCategory, list[ContradictionRef]] = {
        "role_proof": [],
        "cross_statement": [],
        "weak_signal": [],
    }
    for flag in flags:
        buckets[classify_flag_for_prompt(flag)].append(flag)
    return _FlagGroups(
        proof=tuple(buckets["role_proof"]),
        conflicting=tuple(buckets["cross_statement"]),
        weak=tuple(buckets["weak_signal"]),
    )


# What a render assumes when no caller threaded the game's impostor count: the
# four-player preset's single impostor, i.e. the wording every template carried
# before the count was threadable.
DEFAULT_IMPOSTOR_COUNT: Final[int] = 1

_COUNT_WORDS: Final[tuple[str, ...]] = (
    "no",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
)


@dataclass(frozen=True)
class _ImpostorWording:
    """The persona sentence's parts, agreeing in number with the roster."""

    count: int
    phrase: str  # "a hidden impostor" / "two hidden impostors"
    verb_be: str  # "is" / "are"
    verb_kill: str  # "kills" / "kill"
    subject: str  # "the impostor" / "the impostors"
    verb_win: str  # "wins" / "win"
    eject_all: str  # "the impostor out" / "both impostors out"
    one_of_them: str  # "the impostor" / "an impostor"


def _impostor_wording(count: int | None) -> _ImpostorWording:
    """Build the number-agreeing persona wording for ``count`` impostors."""

    resolved = DEFAULT_IMPOSTOR_COUNT if count is None else count
    if resolved < 1:
        raise ValueError(f"impostor_count must be at least 1, got {resolved}")
    if resolved == 1:
        return _ImpostorWording(
            count=1,
            phrase="a hidden impostor",
            verb_be="is",
            verb_kill="kills",
            subject="the impostor",
            verb_win="wins",
            eject_all="the impostor out",
            one_of_them="the impostor",
        )
    word = _COUNT_WORDS[resolved] if resolved < len(_COUNT_WORDS) else str(resolved)
    return _ImpostorWording(
        count=resolved,
        phrase=f"{word} hidden impostors",
        verb_be="are",
        verb_kill="kill",
        subject="the impostors",
        verb_win="win",
        eject_all=(
            "both impostors out" if resolved == 2 else f"all {word} impostors out"
        ),
        one_of_them="an impostor",
    )


def _render_inputs_for(
    render_inputs: PromptRenderInputs | None, *, map_card: str
) -> PromptRenderInputs:
    """Compose the per-render facts, splitting the two inputs by lifetime.

    The impostor count is per-GAME and arrives per call (the manager threads it
    the way it threads ``dead_ids``); the map card is a constant of the map and
    is bound onto each renderer at construction. A card supplied explicitly on
    ``render_inputs`` wins, so a caller rendering an alternative topology is
    never overridden by the bound one.
    """

    if render_inputs is None:
        return PromptRenderInputs(map_card=map_card)
    if render_inputs.map_card:
        return render_inputs
    return replace(render_inputs, map_card=map_card)


def crewmate_report_prompt(
    *,
    agent_id: PlayerId,
    current_tick: int,
    meeting_trigger: str,
    rendered_memory: str,
    public_transcript: str,
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
    living_ids: tuple[PlayerId, ...] = (),
    dead_ids: tuple[PlayerId, ...] = (),
    persona: str = "",
    suspicion_provenance: tuple[SuspicionEntry, ...] = (),
    render_inputs: PromptRenderInputs | None = None,
    reporter_context: ReporterContext | None = None,
    at_body: bool = False,
    testimony_shapes: bool = False,
    environment: Environment | None = None,
    map_card: str = "",
) -> str:
    """Render the Phase-1 crewmate report prompt (DESIGN.md §5.3).

    ``fellow_impostor_ids`` (Task 7.12) is accepted so this wrapper
    conforms to the same :class:`~meetings.render_contract.ReportPromptRenderer`
    Protocol as :func:`impostor_report_prompt` and the meeting manager
    can dispatch by role without an adapter. A crewmate has no teammate
    list (the value is always ``()``) and the crewmate template never
    references it, so the rendered prompt is byte-unchanged.

    ``living_ids`` (Task 9.9, audit gp-3) is the living-roster accusation
    list -- living participants minus this speaker, the turn-side mirror of
    the vote ballot's ``candidate_targets`` -- rendered as the only valid
    accusation targets. The template guards the block on a non-empty value,
    so the default ``()`` (ad-hoc renders) keeps the prompt byte-unchanged.

    ``dead_ids`` (Task 10.3, audit gp-9) is the dead / ejected negative
    list, rendered as an explicit do-not-accuse line under the living
    roster. Guarded the same way: the default ``()`` omits the line.

    ``persona`` (Task 16.3, populated 16.9, rendered 16.16) and
    ``suspicion_provenance`` (Task 16.3, rendered 16.15) are accepted so this
    wrapper conforms to the widened
    :class:`~meetings.render_contract.ReportPromptRenderer` Protocol and are
    passed straight through to ``.render(...)``. The current template references
    neither, so jinja ignores them and the prompt is byte-unchanged (the
    widen-the-contract-inert pattern; the 15.5 ``reporter_id`` precedent). The
    seam is landed once here so 16.15/16.16 edit ONLY the template.

    ``reporter_context`` (the reporter-voice lever) names the body-report
    meeting's reporter, threaded only when the opener IS that reporter, so the
    served template can ask for the discovery account plainly. ``at_body`` is
    accepted for Protocol symmetry with the statement renderer and is not
    referenced by any report template -- the opener is the reporter, whose
    discovery IS the report. Both are passed straight through; ``None`` /
    ``False`` renders byte-identically, which the prompt-byte golden pins.

    ``testimony_shapes`` opens the served body's guarded witnessed-kill block --
    one shape-menu row and the instruction line beside the vent mandate. It is
    a render input rather than a lever read: :func:`build_prompt_renderers`
    binds the resolved boolean at construction, so the routing decision is
    frozen where ``prompt_versions_for_set`` reads the same lever and a mid-run
    export cannot move bytes while the stamp stays put. The default ``False``
    renders the committed bytes exactly.
    """

    inputs = _render_inputs_for(render_inputs, map_card=map_card)
    return (
        (environment or _ENV)
        .get_template(CREWMATE_REPORT_TEMPLATE)
        .render(
            agent_id=agent_id,
            current_tick=current_tick,
            meeting_trigger=meeting_trigger,
            rendered_memory=rendered_memory,
            public_transcript=public_transcript,
            living_ids=living_ids,
            dead_ids=dead_ids,
            persona=persona,
            suspicion_provenance=suspicion_provenance,
            map_card=inputs.map_card,
            impostors=_impostor_wording(inputs.impostor_count),
            reporter_context=reporter_context,
            at_body=at_body,
            testimony_shapes=testimony_shapes,
        )
    )


def impostor_report_prompt(
    *,
    agent_id: PlayerId,
    current_tick: int,
    meeting_trigger: str,
    rendered_memory: str,
    public_transcript: str,
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
    living_ids: tuple[PlayerId, ...] = (),
    dead_ids: tuple[PlayerId, ...] = (),
    persona: str = "",
    suspicion_provenance: tuple[SuspicionEntry, ...] = (),
    render_inputs: PromptRenderInputs | None = None,
    reporter_context: ReporterContext | None = None,
    at_body: bool = False,
    environment: Environment | None = None,
    template_name: str | None = None,
    map_card: str = "",
) -> str:
    """Render the Phase-1 impostor report prompt (DESIGN.md §4.5, §5.3).

    Conforms to the same :class:`~meetings.render_contract.ReportPromptRenderer`
    Protocol as :func:`crewmate_report_prompt` so the meeting manager
    can dispatch by role without an extra adapter. The impostor
    template itself does not reference ``agent_id``, ``current_tick``,
    or ``meeting_trigger`` — they are accepted and passed through so
    a future template revision can opt in without breaking call sites.

    ``fellow_impostor_ids`` (Task 7.12) is the impostor's teammate list;
    the template renders the "never accuse / incriminate a teammate"
    block only when it is non-empty, so a sole impostor (``()``) gets a
    byte-unchanged prompt.

    ``living_ids`` (Task 9.9) is the living-roster accusation list,
    rendered since impostor_report_v4 (Task 10.3): the dead-id
    accusation hallucination was disproportionately impostor-spoken
    (12/18, audit gp-9 D-D-8), so the impostor opening now carries the
    same roster block as the crewmate one. ``dead_ids`` (Task 10.3) is
    the matching dead / ejected do-not-accuse line. Both are guarded on
    a non-empty value, so the defaults (``()``) omit the blocks.

    ``persona`` (Task 16.3, populated 16.9, rendered 16.16) and
    ``suspicion_provenance`` (Task 16.3, rendered 16.15) are the inert
    render-contract widenings, passed straight through; the current template
    references neither, so the prompt is byte-unchanged (the
    widen-the-contract-inert pattern, landed once so 16.15/16.16 edit only the
    template).

    ``template_name`` (Task 18.10) selects the template FILE this wrapper
    renders: the default ``None`` resolves it live from the
    :func:`impostor_roll_call_enabled` lever (OFF — the default — is the
    exact pre-task :data:`IMPOSTOR_REPORT_TEMPLATE` path, byte-identical),
    while :func:`build_prompt_renderers` passes an explicit name so a
    recording runner's routing decision is pinned at construction time (the
    PR #203 binding discipline). Lever ON outside the ``qwen3_6_27b`` set
    fails loud with :class:`jinja2.TemplateNotFound` — the variant file
    exists only there, and there is no silent fallback.

    ``reporter_context`` / ``at_body`` (the reporter-voice lever) are accepted so
    this wrapper conforms to the widened
    :class:`~meetings.render_contract.ReportPromptRenderer` Protocol and are
    passed straight through. The impostor never reports a body (the FSM impostor
    presses no button), so the impostor templates reference neither and the
    prompt is byte-unchanged.
    """

    resolved_template = (
        template_name
        if template_name is not None
        else (
            IMPOSTOR_REPORT_ROLL_CALL_TEMPLATE
            if impostor_roll_call_enabled()
            else IMPOSTOR_REPORT_TEMPLATE
        )
    )
    inputs = _render_inputs_for(render_inputs, map_card=map_card)
    return (
        (environment or _ENV)
        .get_template(resolved_template)
        .render(
            agent_id=agent_id,
            current_tick=current_tick,
            meeting_trigger=meeting_trigger,
            rendered_memory=rendered_memory,
            public_transcript=public_transcript,
            fellow_impostor_ids=fellow_impostor_ids,
            living_ids=living_ids,
            dead_ids=dead_ids,
            persona=persona,
            suspicion_provenance=suspicion_provenance,
            map_card=inputs.map_card,
            impostors=_impostor_wording(inputs.impostor_count),
            reporter_context=reporter_context,
            at_body=at_body,
        )
    )


def accusation_round_prompt(
    *,
    agent_id: PlayerId,
    rendered_memory: str,
    transcript: MeetingTranscript,
    contradictions: tuple[ContradictionRef, ...],
    prior_turn: MeetingTurn | None,
    turn_kind: TurnKind,
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
    living_ids: tuple[PlayerId, ...] = (),
    dead_ids: tuple[PlayerId, ...] = (),
    is_impostor: bool = False,
    is_body_report: bool = False,
    persona: str = "",
    suspicion_provenance: tuple[SuspicionEntry, ...] = (),
    render_inputs: PromptRenderInputs | None = None,
    reporter_context: ReporterContext | None = None,
    at_body: bool = False,
    testimony_shapes: bool = False,
    environment: Environment | None = None,
    template_name: str | None = None,
    map_card: str = "",
) -> str:
    """Render a reactive ``reply`` / ``opt_in`` turn prompt (DESIGN.md §5.2).

    Conforms to the :class:`~meetings.render_contract.StatementPromptRenderer`
    Protocol so the meeting manager and strategic reasoner can invoke it
    for every reactive-chain and opt-in turn without an adapter.

    Task 8.8 grew two inputs over the old fixed-round statement renderer:

    * ``prior_turn`` is the accusing turn this speaker answers -- the
      "who accused me" context. It is the prior chain turn on a
      ``reply`` and ``None`` on an opt-in info-share turn.
    * ``turn_kind`` is ``"reply"`` or ``"opt_in"`` so the template frames
      the turn correctly (the opt-in turn is terminal and never extends
      the chain).

    ``transcript`` is the transcript-so-far in chain order (its ``turns``
    tuple); ``contradictions`` are the §5.4 flags warranted up to this
    turn. ``agent_id`` is threaded into the template so the self-alibi
    example renders the speaker's own canonical player id (e.g.
    ``"subject": "p-3"``) rather than a placeholder the model might
    mis-substitute, keeping DESIGN.md §5.4 contradiction detection able to
    match self-alibis across speakers.

    ``fellow_impostor_ids`` (Task 7.12) is the impostor-only teammate
    list; the template renders the "never target a teammate" block only
    when it is non-empty, so a crewmate / sole-impostor turn (``()``) is
    byte-unchanged.

    ``living_ids`` (Task 9.9, audit gp-3) is the living-roster accusation
    list -- living participants minus this speaker, the turn-side mirror of
    the vote ballot's ``candidate_targets`` -- rendered as the only valid
    accusation targets. The template guards the block on a non-empty value,
    so the default ``()`` (ad-hoc renders) keeps the prompt byte-unchanged.

    ``dead_ids`` (Task 10.3, audit gp-9) is the dead / ejected negative
    list, rendered as an explicit do-not-accuse line under the living
    roster. Guarded the same way: the default ``()`` omits the line.

    ``is_impostor`` (Task 11.2) gates the cover-consistency directive on
    the reply branch -- the impostor commits to ONE sheltered room +
    tick-window away from the body and reuses it every turn (DESIGN.md
    §5.2; experiments/lab/report-vent-escape-lab.md, the residual
    self-pair alibi_conflict drift). It is an explicit bool rather than a
    reuse of ``fellow_impostor_ids`` because a SOLE impostor has empty
    fellows but must still get the directive. The default ``False`` keeps
    the crewmate (and ad-hoc) render byte-unchanged.

    ``is_body_report`` (Task 11.2; PR #159 review) is the second gate on the
    cover directive: the wording speaks of "the body's room and the tick it
    happened", so -- mirroring ``impostor_report.j2``'s ``body_report_opening``
    gate -- the block must fire only when a body is on the table, never on a
    body-less emergency reply. The default ``False`` keeps the block off unless
    the caller explicitly marks the meeting a body report.

    ``persona`` (Task 16.3, populated 16.9, rendered 16.16) and
    ``suspicion_provenance`` (Task 16.3, rendered 16.15) are the inert
    render-contract widenings, passed straight through; the current template
    references neither, so the prompt is byte-unchanged (the
    widen-the-contract-inert pattern, landed once so 16.15/16.16 edit only the
    template).

    ``template_name`` (Task 18.10) selects the template FILE this wrapper
    renders: the default ``None`` resolves it live from the
    :func:`impostor_roll_call_enabled` lever (OFF — the default — is the
    exact pre-task :data:`ACCUSATION_ROUND_TEMPLATE` path, byte-identical),
    while :func:`build_prompt_renderers` passes an explicit name so a
    recording runner's routing decision is pinned at construction time (the
    PR #203 binding discipline). The variant file swaps ONLY the impostor
    reply surfaces; the crew reply and the role-blind info-share render
    byte-identically through it (fixture-pinned), which is why the swap is
    per-FILE rather than per-role — one meeting's ``accusation_round``
    prompts all carry one provenance stamp. Lever ON outside the
    ``qwen3_6_27b`` set fails loud with :class:`jinja2.TemplateNotFound`.

    ``reporter_context`` (the reporter-voice lever) names the body-report
    meeting's reporter, threaded only for speakers who are NOT that reporter, so
    the table reads the same base rate the ballot states before it forms a
    target. ``at_body`` says THIS speaker's own record places them at the body
    when the meeting opened and renders one neutral self-addressed line -- never
    a roster of who else was there. ``None`` / ``False`` renders byte-identically,
    which the prompt-byte golden pins.

    ``testimony_shapes`` opens the served body's guarded witnessed-kill block on
    the CREW branch -- one shape-menu row and the instruction line beside the
    vent mandate. An impostor-facing render is byte-identical under both states:
    an impostor holds no witnessed-kill row it could honestly speak (its own
    kill is its own first-person memory, and a teammate's is suppressed before
    render), so offering it there would only be a confession prompt. Bound at
    construction by :func:`build_prompt_renderers`, alongside the same lever
    read that serves the version stamp; the default ``False`` renders the
    committed bytes exactly.
    """

    resolved_template = (
        template_name
        if template_name is not None
        else (
            ACCUSATION_ROUND_ROLL_CALL_TEMPLATE
            if impostor_roll_call_enabled()
            else ACCUSATION_ROUND_TEMPLATE
        )
    )
    inputs = _render_inputs_for(render_inputs, map_card=map_card)
    return (
        (environment or _ENV)
        .get_template(resolved_template)
        .render(
            agent_id=agent_id,
            rendered_memory=rendered_memory,
            transcript=transcript,
            contradictions=contradictions,
            prior_turn=prior_turn,
            turn_kind=turn_kind,
            fellow_impostor_ids=fellow_impostor_ids,
            living_ids=living_ids,
            dead_ids=dead_ids,
            is_impostor=is_impostor,
            is_body_report=is_body_report,
            persona=persona,
            suspicion_provenance=suspicion_provenance,
            map_card=inputs.map_card,
            impostors=_impostor_wording(inputs.impostor_count),
            flag_groups=_group_flags(contradictions),
            reporter_context=reporter_context,
            at_body=at_body,
            testimony_shapes=testimony_shapes,
        )
    )


def vote_ballot_prompt(
    *,
    voter_id: PlayerId,
    rendered_memory: str,
    transcript: MeetingTranscript,
    contradiction_flags: tuple[ContradictionRef, ...],
    suspicion_graph: tuple[SuspicionEntry, ...],
    candidate_targets: tuple[PlayerId, ...],
    skip_confidence_threshold: float,
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
    reporter_id: PlayerId | None = None,
    persona: str = "",
    suspicion_provenance: tuple[SuspicionEntry, ...] = (),
    render_inputs: PromptRenderInputs | None = None,
    testimony_ledger: MeetingTestimonyLedger | None = None,
    environment: Environment | None = None,
    map_card: str = "",
) -> str:
    """Render a vote-ballot prompt (DESIGN.md §5.5).

    Conforms to the :class:`~meetings.render_contract.VotePromptRenderer`
    Protocol; the meeting manager invokes this callable verbatim per
    voter to produce the ballot-phase prompt.

    ``fellow_impostor_ids`` (Task 7.12) is the impostor-only teammate
    list; the template renders the "never vote a teammate — SKIP
    instead" block only when it is non-empty, so a crewmate /
    sole-impostor ballot (``()``) is byte-unchanged.

    ``reporter_id`` (the reporter-exculpation annotation) is the body-report
    meeting's own reporter, threaded by the manager for every body report. The
    v6 template renders the self-report base-rate annotation only when it is
    non-``None``; the default ``None`` (an emergency call, or an ad-hoc render)
    omits the block.

    ``persona`` (Task 16.3, populated 16.9, rendered 16.16) and
    ``suspicion_provenance`` (Task 16.3, rendered 16.15) are the inert
    render-contract widenings, passed straight through; the current template
    references neither, so the prompt is byte-unchanged. On the ballot the
    manager threads the same post-fold rows into ``suspicion_provenance`` as into
    ``suspicion_graph`` (the render-after-fold consistency pin), so 16.15's
    surface will decompose exactly the scalars already shown -- landed once here
    so 16.15 edits only the template.

    ``testimony_ledger`` is the meeting's per-subject source count, threaded by
    the manager only while the corroboration lever is ON. The template renders
    one row per accused candidate; ``None`` omits the block entirely, so an OFF
    meeting renders byte-identically to the pre-lever prompt.
    """

    inputs = _render_inputs_for(render_inputs, map_card=map_card)
    return (
        (environment or _ENV)
        .get_template(VOTE_BALLOT_TEMPLATE)
        .render(
            voter_id=voter_id,
            rendered_memory=rendered_memory,
            transcript=transcript,
            contradiction_flags=contradiction_flags,
            suspicion_graph=suspicion_graph,
            candidate_targets=candidate_targets,
            skip_confidence_threshold=skip_confidence_threshold,
            fellow_impostor_ids=fellow_impostor_ids,
            reporter_id=reporter_id,
            persona=persona,
            suspicion_provenance=suspicion_provenance,
            map_card=inputs.map_card,
            impostors=_impostor_wording(inputs.impostor_count),
            flag_groups=_group_flags(contradiction_flags),
            testimony_ledger=testimony_ledger,
        )
    )


@dataclass(frozen=True)
class PromptRenderers:
    """The four strategic prompt renderers bound to ONE prompt set (Task 14.2).

    Each field is a wrapper callable pre-bound (via :func:`functools.partial`)
    to a single set's :class:`jinja2.Environment`, so a meeting runner renders
    its turns and records its ``prompt_versions`` from the SAME set -- even if
    ``AILIBI_PROMPT_SET`` is changed in-process after this module's import-time
    :data:`_ENV` was built (PR #203 review). The field names mirror the
    :class:`~meetings.manager.MeetingManager` prompt-callable parameters.
    """

    crewmate_report: ReportPromptRenderer
    impostor_report: ReportPromptRenderer
    statement: StatementPromptRenderer
    vote: VotePromptRenderer


_TESTIMONY_SHAPES_GUARD: Final[str] = "testimony_shapes"


def _carries_a_live_guard(template: nodes.Template) -> bool:
    """Whether a parsed body branches on the arm's variable for real.

    True when some ``{% if %}`` condition reads
    :data:`_TESTIMONY_SHAPES_GUARD` AND does not fold to a constant. Jinja
    folds ``false and x`` to ``False`` without evaluating ``x``, so a dead
    guard is exactly the case ``as_const`` decides and a live one is exactly
    the case it refuses.
    """

    for branch in template.find_all(nodes.If):
        test = branch.test
        if not isinstance(test, nodes.Expr):
            continue
        names = {node.name for node in test.find_all(nodes.Name)}
        if isinstance(test, nodes.Name):
            names.add(test.name)
        if _TESTIMONY_SHAPES_GUARD not in names:
            continue
        try:
            test.as_const()
        except nodes.Impossible:
            return True
    return False


def _require_testimony_shapes_bodies(
    environment: Environment,
    *,
    set_name: str,
    templates: tuple[str, ...],
) -> None:
    """Refuse a lever-ON bundle whose bodies never READ the arm's variable.

    The arm RE-BODIES the set's own templates, so "no arm here" is a MISSING
    BODY -- a real defect that must surface at construction rather than as a
    silently unguarded render. The message names the body, never a sibling
    lever: an all-ON slate is exactly what the adopting record runs.

    The test is the PARSED template, not a substring of its source: the body
    must carry at least one ``{% if %}`` whose condition READS the variable and
    is not a foldable constant. A name in a ``{# comment #}`` or in literal
    prose fails (it is no condition), and so does a dead guard such as
    ``{% if false and testimony_shapes %}`` (its condition folds to a constant,
    so ON and OFF would render identical bytes under a stamp claiming the arm).
    What the check does NOT decide is whether the live guard adds the RIGHT
    lines; that is the diff gate's job
    (``tests/agents/test_bespoke_prompt_sets.py``), and duplicating it here
    would need a full render context this seam does not have.

    Checked against the templates THIS arm re-bodies, not against whatever
    filename a sibling swapped in. An arm that swaps a variant FILE serves a
    body written independently of every sibling, so this arm's block does not
    reach it -- the known gap pinned in
    ``tests/meetings/test_prompt_byte_golden.py``, which belongs to the swapping
    arm and is not a defect in this set's bodies.

    An unparseable or absent body is the same refusal as an unguarded one:
    either way the set cannot serve the arm, and the message says which file.
    """

    for name in templates:
        try:
            source = environment.loader.get_source(environment, name)[0]  # type: ignore[union-attr]
            guarded = _carries_a_live_guard(environment.parse(source))
        except (TemplateNotFound, TemplateSyntaxError, AttributeError):
            guarded = False
        if not guarded:
            raise ValueError(
                f"Prompt set {set_name!r} template {name!r} carries no live "
                f"{_TESTIMONY_SHAPES_GUARD!r} guard; the "
                f"{ENV_TESTIMONY_SHAPES} lever is only authored for the "
                "'qwen3_6_27b' set — unset the lever or select a set whose "
                "bodies carry the block"
            )


def build_prompt_renderers(
    prompt_set: str | None = None,
    *,
    root: Path = _PROMPTS_ROOT,
    env: Mapping[str, str] | None = None,
    map_card: str = CANONICAL_MAP_CARD,
) -> PromptRenderers:
    """Build the four renderers bound to a single resolved prompt set.

    Resolves ``prompt_set`` once (via :func:`build_environment`) and binds every
    renderer to that set's :class:`jinja2.Environment`. Pairing the returned
    bundle with :func:`orchestrator.game.prompt_versions_for_set` for the SAME
    resolved set keeps a recording's rendered templates and recorded
    ``prompt_versions`` on one set, which is the replay-provenance invariant
    (DESIGN.md §11.4). An unknown set raises via :func:`build_environment`.

    The Task 18.10 impostor-answer lever is resolved HERE, once, from the same
    ``env`` mapping (the PR #203 binding discipline extended to the lever):
    lever OFF — the default — binds the exact default template filenames, so
    the bundle is byte-identical to the pre-task path; lever ON binds the two
    ``*_roll_call.j2`` variant filenames into the impostor-report and
    statement renderers. ON with a set that does not carry the variant files
    (only ``qwen3_6_27b`` does) raises :class:`ValueError` at construction —
    no silent fallback, and no half-routed bundle can reach a runner.
    ``prompt_versions_for_set`` reads the same lever from the same ``env``,
    which is what keeps a recording's rendered bytes and recorded stamps on
    one routing decision.

    The ``testimony_shapes`` lever is resolved in the same place and for the
    same reason, and binds a render KWARG rather than a filename: its block
    lives inside the served body, so ON binds ``True`` into the crewmate-report
    and statement partials and OFF binds ``False`` — the exact committed bytes.
    ON with a set whose served bodies carry no such block raises
    :class:`ValueError` at construction, naming the missing BODY and never a
    sibling lever being on.

    ``map_card`` defaults to the live :data:`CANONICAL_MAP_CARD` and exists for
    one caller: the bump-in-flight archive, which pairs an older set's template
    bytes with the card THOSE bytes rendered. The card is a render input, not a
    template, so pointing ``root`` at an archived set is not by itself enough to
    reproduce its recordings once the card's own format has moved.
    """

    environment = build_environment(prompt_set, root=root, env=env)
    variant = impostor_roll_call_enabled(env)
    shapes = testimony_shapes_enabled(env)
    impostor_report_template = (
        IMPOSTOR_REPORT_ROLL_CALL_TEMPLATE if variant else IMPOSTOR_REPORT_TEMPLATE
    )
    statement_template = (
        ACCUSATION_ROUND_ROLL_CALL_TEMPLATE if variant else ACCUSATION_ROUND_TEMPLATE
    )
    if variant:
        for name in (impostor_report_template, statement_template):
            try:
                environment.get_template(name)
            except TemplateNotFound as exc:
                raise ValueError(
                    f"Prompt set {resolve_prompt_set(prompt_set, env=env)!r} has "
                    f"no impostor-answer variant template {name!r}; the Task "
                    "18.10 lever (AILIBI_IMPOSTOR_ROLL_CALL) is only authored "
                    "for the 'qwen3_6_27b' set — unset the lever or select a "
                    "variant-capable set"
                ) from exc
    if shapes:
        _require_testimony_shapes_bodies(
            environment,
            set_name=resolve_prompt_set(prompt_set, env=env),
            templates=(CREWMATE_REPORT_TEMPLATE, ACCUSATION_ROUND_TEMPLATE),
        )
    return PromptRenderers(
        crewmate_report=partial(
            crewmate_report_prompt,
            environment=environment,
            map_card=map_card,
            testimony_shapes=shapes,
        ),
        impostor_report=partial(
            impostor_report_prompt,
            environment=environment,
            template_name=impostor_report_template,
            map_card=map_card,
        ),
        statement=partial(
            accusation_round_prompt,
            environment=environment,
            template_name=statement_template,
            map_card=map_card,
            testimony_shapes=shapes,
        ),
        vote=partial(
            vote_ballot_prompt,
            environment=environment,
            map_card=map_card,
        ),
    )


__all__ = [
    "ACCUSATION_ROUND_ROLL_CALL_TEMPLATE",
    "ACCUSATION_ROUND_TEMPLATE",
    "CANONICAL_MAP_CARD",
    "CANONICAL_ROOM_DISPLAY_NAMES",
    "CREWMATE_REPORT_TEMPLATE",
    "DEFAULT_IMPOSTOR_COUNT",
    "DEFAULT_PROMPT_SET",
    "ENV_IMPOSTOR_ROLL_CALL",
    "ENV_PROMPT_SET",
    "IMPOSTOR_REPORT_ROLL_CALL_TEMPLATE",
    "IMPOSTOR_REPORT_TEMPLATE",
    "OPERATIONAL_BASELINE_PROMPT_SET",
    "VOTE_BALLOT_TEMPLATE",
    "PromptEvidenceCategory",
    "PromptRenderers",
    "accusation_round_prompt",
    "build_environment",
    "build_prompt_renderers",
    "classify_flag_for_prompt",
    "crewmate_report_prompt",
    "impostor_report_prompt",
    "impostor_roll_call_enabled",
    "render_map_card",
    "resolve_prompt_set",
    "vote_ballot_prompt",
]
