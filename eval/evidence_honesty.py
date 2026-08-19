"""The evidence-honesty instrument set — the Phase-20 pre-registration's "before".

Ten cell families over committed bytes, one per instrument row I-2…I-11 of
``audits/audit-phase-20-preregistration.md`` §2, plus the render-budget cells the
lever tasks print. Every number the pre-registration names as a bar's "before"
is recomputed here from the recorded replay bytes, so a bar can be re-derived
rather than quoted: a falsifiability contract whose numbers cannot be re-run is
not one.

**This module is the ONLY home of these definitions.** Task 20.22 pins the
pre-registration from :func:`compute_evidence_honesty`, Task 20.34 runs it under
the lever-ON slate for the offline counterfactual, and Task 20.36 reads it cell by
cell on the baseline-7 bytes. A cell re-implemented anywhere else makes the before
and the after incomparable.

Definitions before counting
---------------------------
The house rule of ``eval.deduction_metrics`` — every metric's numerator,
denominator, clock convention and non-coverage stated before it is counted — is
extended here. The ten sentences live in :data:`CELL_DEFINITIONS` and are repeated
verbatim in each cell family's own docstring; ``tests/eval/test_evidence_honesty.py``
asserts the two never drift, so the string Task 20.22 copies into the memo is the
string the code computes.

* **I-2 false crew self-placement** — numerator: spoken whereabouts claims by
  a living CREWMATE whose room matches the speaker's true room at NEITHER
  engine tick N nor engine tick N-1; denominator: all such claims; measured in
  the spoken (agent) tick frame with both adjacent engine ticks admitted; it
  does NOT measure intent, and a claim that is merely unverifiable is not
  counted false.
* **I-3 sole-flag convicting precision** — numerator: ejections whose ejected
  player carried exactly one STRONG contradiction and it was
  alibi_vs_sighting, and the ejected player was an IMPOSTOR; denominator: all
  such ejections; the per-meeting companion counts meetings whose only STRONG
  flag was alibi_vs_sighting; it does NOT measure whether the flag's content
  was true.
* **I-4 grounded sighting side** — numerator: STRONG alibi_vs_sighting
  sighting sides the speaker's own recorded perception supports within the
  stated tick tolerance; denominator: the RESOLVABLE sides only, never the
  full flag count; the spoken tick is resolved to the engine frame as tick -
  1; it does NOT measure whether the sighting was factually true, only whether
  the speaker could have seen it.
* **I-5 fabricated completion lines** — numerator: distinct rendered You
  completed memory rows with no task_completed engine event for that agent at
  any earlier tick; denominator: all distinct rendered You completed rows; the
  render stamps a completion one tick after the engine event, so the
  calibration is memory tick = event tick + 1; it does NOT measure whether the
  fabricated line was spoken at a meeting.
* **I-6 adjacent-room STRONG share** — numerator: STRONG alibi_vs_sighting
  flags whose alibi room and sighting room are one doorway apart on the
  committed map; denominator: all STRONG alibi_vs_sighting flags; both rooms
  are read from the recorded flag's own two events, no clock conversion
  applies; it does NOT measure reachability across more than one doorway.
* **I-7 movement-origin flags** — numerator: alibi_vs_sighting flags whose
  sighting names the ORIGIN half of a saw_player move from A to B row in the
  speaker's own memory; denominator: all alibi_vs_sighting flags resolvable to
  a spoken sighting; the memory row's tick is the spoken tick, so no
  conversion applies; it does NOT measure destination-half re-speaks, which
  are truthful.
* **I-8 dev-marker contamination** — numerator: transcript turns whose
  free_text begins with a meetings.manager audit marker, and separately the
  recorded prompts containing one; denominators: all turns and all recorded
  prompts; no clock applies; it does NOT measure ballot-rationale markers,
  which never reach a prompt.
* **I-9 singular-persona prompts** — numerator: recorded prompts carrying the
  templates' singular hidden-impostor persona phrase; denominator: all
  recorded prompts; no clock applies; the cell is NOT-APPLICABLE on a
  one-impostor roster, where the singular persona is true, and it does NOT
  measure whether the model acted on the contradiction.
* **I-10 meeting physicality** — numerators: meetings with at least one living
  participant inside a vent, and meetings whose reporter was killed within
  three ticks after it; denominator: all resolved meetings; ticks are engine
  ticks and the kill window is inclusive of the first three ticks after the
  meeting tick; the reporter cell is restricted to body-triggered meetings and
  does NOT measure emergency meetings.
* **I-11 impostor targeting** — numerators: free zero-witness kill
  opportunities the policy declined, and impostor decisions whose top-ranked
  target was already dead; denominators: the free-kill opportunities and all
  reconstructed impostor decisions; opportunities are read from the
  PRE-advance engine state the tick's actions were decided from; it does NOT
  measure whether the declined kill would have landed, because a lower-id
  target may dodge in the same tick.

One clock, asserted rather than assumed
---------------------------------------
The agent memory frame runs exactly +1 against the engine/replay frame. Every
recorded observation at agent tick ``T`` describes the world of engine tick
``T - 1``. The module does not assume it: :func:`compute_evidence_honesty` checks
it on every discriminating sighting (the subject changed room between the two
candidate engine ticks) before any cell is emitted, and raises
:class:`EvidenceHonestyReconstructionError` on a single exception. A future clock
change fails here first instead of silently re-pricing every bar.

Three definitional collisions, resolved
---------------------------------------
* **I-3's two conventions.** "12 right / 70 wrong" is per-VICTIM (the ejected
  player's only STRONG flag) while "77 ejections, 65 of them crewmates" is
  per-MEETING (the meeting's only STRONG flag). Both ship, separately pinned and
  named; the pre-registration's bar 4 is measured on the PER-VICTIM cell. They are
  never averaged.
* **I-4's tolerance.** The review measured at-tick and at ±2, the pre-registration
  writes ±1, and production's exculpatory vouch channel uses
  ``meetings.transcript.SIGHTING_GROUNDING_TICK_TOLERANCE`` (2). That production
  constant is a DIFFERENT thing from this instrument's parameter — it gates a
  −0.05 vouch, not a measurement — so the tolerance is an explicit parameter here
  and ±0, ±1 and ±2 are emitted side by side.
* **I-5's disputed pooled count.** ``A/verdicts.md`` G-3's per-set table sums to
  68/594 over the two ``samples`` sets while ``D/FINAL-synthesis.md`` §4 item 2.1
  quotes 65/594. The instrument's recount is authoritative; the test comment names
  which reading was wrong.

Nothing in production moves
---------------------------
This is an instrument over recorded bytes. The meeting rows carry the transcript,
the detector's own ``ContradictionRef`` flags and the verbatim
``LLMCallRecord.prompt`` text; everything else is reconstructed by the
hash-verifying :func:`eval.replay_walk.walk_replay` walk plus the real
``ObservationService`` / ``agents.perception`` / ``ImpostorPolicy`` code paths. It
reads baseline-6 behaviour exactly as it is, bugs included: a cell computed against
a quietly repaired code path would make the phase's before/after meaningless.

Purity: offline, no network, no ``AILIBI_*`` env read, no LLM call. Two runs over
the same bytes produce identical reports.

STABLE JSON report schema (``EvidenceHonestyReport.model_dump()``): one object per
measured set carrying ``replay_set_dir``, the roster knobs, ``games_total``,
``clock_alignment_checked``, and the eleven cell-family blocks named on
:class:`EvidenceHonestyReport`. Every rate is an
``eval.deduction_metrics.WilsonRateCell`` (counts + the Wilson 95% score interval);
the blocks are count-only — no player ids, rooms or transcript text leave here.
"""

from __future__ import annotations

import re
import tempfile
from collections import Counter, deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, NoReturn

from pydantic import BaseModel, ConfigDict

from agents.memory.episodic import MemoryStore
from agents.perception import (
    EVENT_SAW_BODY,
    EVENT_SAW_PLAYER,
    EVENT_SAW_PLAYER_MOVE,
    ingest_packet,
)
from agents.tactical.impostor_policy import ImpostorPolicy, RankedTarget
from engine.entities import PlayerId, Role, RoomId
from engine.events import KilledEvent, TaskCompletedEvent
from engine.world import Map, WorldState, load_canonical_map
from eval.deduction_metrics import (
    _RARE_EVENT_ADVISORY_MAX_NUMERATOR,
    WilsonRateCell,
    _wilson_interval,
)
from eval.replay_walk import (
    MeetingApplied,
    MeetingOpened,
    ReplayWalkConfig,
    TickAdvanced,
    TickOpened,
    WalkViolation,
    walk_replay,
)
from eval.validity import resolve_roster_knobs, roles_by_seed, seeds_on_disk
from meetings.manager import (
    INVALID_ACCUSATION_TARGET_MARKER,
    INVALID_ALIBI_SUBJECT_MARKER,
    INVALID_CORROBORATION_SUPPORTS_MARKER,
)
from meetings.schemas import (
    AlibiClaim,
    ContradictionRef,
    MeetingTranscript,
    SawPlayerObservation,
    WhereaboutsClaim,
)
from meetings.transcript import canonical_rooms, is_weak_contradiction
from observation.public_map import PublicMapView
from observation.service import ObservationService
from orchestrator.boundary import public_map_from_engine_map, translate_action_intent
from orchestrator.replay import LLMCallRecord, MeetingReplayEntry

# The agent memory frame runs one ahead of the engine/replay frame: a row stamped
# ``[tick T]`` describes engine tick ``T - 1``.
AGENT_CLOCK_OFFSET: Final[int] = 1

# The prompt-set whose recorded bytes the committed sets carry.
_RECORDED_PROMPT_SET: Final[str] = "qwen3_6_27b"

# The six templates whose persona block hard-codes a singular hidden impostor.
_PERSONA_TEMPLATES: Final[tuple[str, ...]] = (
    "accusation_round.j2",
    "accusation_round_roll_call.j2",
    "crewmate_report.j2",
    "impostor_report.j2",
    "impostor_report_roll_call.j2",
    "vote_ballot.j2",
)
_SINGULAR_PERSONA_PATTERN: Final[re.Pattern[str]] = re.compile(r"a hidden impostor")
# The phrase the committed baseline-6 prompts carry, kept so the cell stays
# countable once the templates are reworded.
_RECORDED_SINGULAR_PERSONA_PHRASE: Final[str] = "a hidden impostor"

# One rendered self-location row, the only "You" shape that places the speaker.
_COMPLETED_LINE: Final[re.Pattern[str]] = re.compile(
    r"^- \[obs (?P<observation_id>[^\]]+)\] \[tick (?P<tick>\d+)\] "
    r"You completed (?P<task>\S+) \(you were in (?P<room>[^)]+)\)\.$",
    re.MULTILINE,
)
# The two rendered MEMORY row shapes, and only those: a first-hand observation
# carries an ``[obs …]`` handle, heard testimony a ``[tick N] [meeting] CLAIM``
# stamp. The prompt templates also format transcript turns and contradiction flags
# as ``- […]`` bullets, which are not memory and must not enter the budget.
_RENDERED_ROW: Final[re.Pattern[str]] = re.compile(
    r"^- (?:\[obs [^\]]+\] |\[tick \d+\] \[meeting\] CLAIM by )", re.MULTILINE
)
# The reported-testimony row shape (``agents.memory.store`` renders heard claims).
_TESTIMONY_ROW: Final[re.Pattern[str]] = re.compile(r"^- \[.*\[meeting\] CLAIM by ")

CELL_DEFINITIONS: Final[Mapping[str, str]] = {
    "I-2": (
        "numerator: spoken whereabouts claims by a living CREWMATE whose room "
        "matches the speaker's true room at NEITHER engine tick N nor engine tick "
        "N-1; denominator: all such claims; measured in the spoken (agent) tick "
        "frame with both adjacent engine ticks admitted; it does NOT measure "
        "intent, and a claim that is merely unverifiable is not counted false."
    ),
    "I-3": (
        "numerator: ejections whose ejected player carried exactly one STRONG "
        "contradiction and it was alibi_vs_sighting, and the ejected player was an "
        "IMPOSTOR; denominator: all such ejections; the per-meeting companion "
        "counts meetings whose only STRONG flag was alibi_vs_sighting; it does NOT "
        "measure whether the flag's content was true."
    ),
    "I-4": (
        "numerator: STRONG alibi_vs_sighting sighting sides the speaker's own "
        "recorded perception supports within the stated tick tolerance; "
        "denominator: the RESOLVABLE sides only, never the full flag count; the "
        "spoken tick is resolved to the engine frame as tick - 1; it does NOT "
        "measure whether the sighting was factually true, only whether the speaker "
        "could have seen it."
    ),
    "I-5": (
        "numerator: distinct rendered You completed memory rows with no "
        "task_completed engine event for that agent at any earlier tick; "
        "denominator: all distinct rendered You completed rows; the render stamps "
        "a completion one tick after the engine event, so the calibration is "
        "memory tick = event tick + 1; it does NOT measure whether the fabricated "
        "line was spoken at a meeting."
    ),
    "I-6": (
        "numerator: STRONG alibi_vs_sighting flags whose alibi room and sighting "
        "room are one doorway apart on the committed map; denominator: all STRONG "
        "alibi_vs_sighting flags; both rooms are read from the recorded flag's own "
        "two events, no clock conversion applies; it does NOT measure reachability "
        "across more than one doorway."
    ),
    "I-7": (
        "numerator: alibi_vs_sighting flags whose sighting names the ORIGIN half "
        "of a saw_player move from A to B row in the speaker's own memory; "
        "denominator: all alibi_vs_sighting flags resolvable to a spoken sighting; "
        "the memory row's tick is the spoken tick, so no conversion applies; it "
        "does NOT measure destination-half re-speaks, which are truthful."
    ),
    "I-8": (
        "numerator: transcript turns whose free_text begins with a "
        "meetings.manager audit marker, and separately the recorded prompts "
        "containing one; denominators: all turns and all recorded prompts; no "
        "clock applies; it does NOT measure ballot-rationale markers, which never "
        "reach a prompt."
    ),
    "I-9": (
        "numerator: recorded prompts carrying the templates' singular "
        "hidden-impostor persona phrase; denominator: all recorded prompts; no "
        "clock applies; the cell is NOT-APPLICABLE on a one-impostor roster, where "
        "the singular persona is true, and it does NOT measure whether the model "
        "acted on the contradiction."
    ),
    "I-10": (
        "numerators: meetings with at least one living participant inside a vent, "
        "and meetings whose reporter was killed within three ticks after it; "
        "denominator: all resolved meetings; ticks are engine ticks and the kill "
        "window is inclusive of the first three ticks after the meeting tick; the "
        "reporter cell is restricted to body-triggered meetings and does NOT "
        "measure emergency meetings."
    ),
    "I-11": (
        "numerators: free zero-witness kill opportunities the policy declined, and "
        "impostor decisions whose top-ranked target was already dead; "
        "denominators: the free-kill opportunities and all reconstructed impostor "
        "decisions; opportunities are read from the PRE-advance engine state the "
        "tick's actions were decided from; it does NOT measure whether the "
        "declined kill would have landed, because a lower-id target may dodge in "
        "the same tick."
    ),
}
"""The ten definition sentences Task 20.22 copies into the pre-registration memo.

Each is repeated verbatim in its cell family's docstring and in this module's
docstring; the test asserts all three copies agree, so the memo cannot drift from
the code that computes the number.
"""


class EvidenceHonestyReconstructionError(RuntimeError):
    """A recording did not reconstruct, or the agent clock moved.

    Raised on a walk-integrity breach (per-tick ``state_hash`` mismatch, duplicate
    or missing meeting row, meeting pre/post hash mismatch, a replay ending before
    GAME_OVER, rows trailing the terminal tick, a missing ``game_over`` row, or a
    replay-set directory with no ``replay-seed-*.jsonl`` files), on a discriminating
    sighting that does not sit at ``obs.tick - 1``, and on an impostor decision the
    reconstructed policy does not reproduce. Under-measuring a broken recording is
    worse than failing loudly (AGENTS.md "no silent fallbacks").
    """


class _FrozenModel(BaseModel):
    """Frozen, ``extra="forbid"`` base (the ``eval/`` report convention)."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class FalseWhereaboutsCells(_FrozenModel):
    """I-2 false crew self-placement.

    numerator: spoken whereabouts claims by a living CREWMATE whose room matches
    the speaker's true room at NEITHER engine tick N nor engine tick N-1;
    denominator: all such claims; measured in the spoken (agent) tick frame with
    both adjacent engine ticks admitted; it does NOT measure intent, and a claim
    that is merely unverifiable is not counted false.

    ``crew_false_agent_frame`` is the stricter reading of the same rule — the
    claim compared against the two AGENT-frame ticks N and N-1 (engine N-1 and
    N-2) — carried so the tick convention stays a measured difference rather than
    an assumption. ``copyable_self_location`` is the self-placement coverage cell:
    the share of crew whereabouts claims whose exact (tick, room) pair appears in a
    rendered self-location row the speaker could have copied it from.
    """

    crew_claims: int
    crew_false: WilsonRateCell
    crew_false_agent_frame: WilsonRateCell
    impostor_false: WilsonRateCell
    copyable_self_location: WilsonRateCell


class SoleFlagPrecisionCells(_FrozenModel):
    """I-3 sole-``alibi_vs_sighting`` convicting precision.

    numerator: ejections whose ejected player carried exactly one STRONG
    contradiction and it was alibi_vs_sighting, and the ejected player was an
    IMPOSTOR; denominator: all such ejections; the per-meeting companion counts
    meetings whose only STRONG flag was alibi_vs_sighting; it does NOT measure
    whether the flag's content was true.

    ``per_victim_precision`` reads "only" as ONLY THAT KIND — a victim carrying
    two ``alibi_vs_sighting`` STRONG flags and nothing else was still convicted on
    that class alone — and it is the reading that reproduces the review's 12 right
    / 70 wrong. ``per_victim_single_flag_precision`` is the stricter
    exactly-one-flag reading of the same population, carried so the choice stays a
    measured difference rather than an argument.

    The pre-registration's bar 4 is measured on ``per_victim_precision``. The two
    conventions are never averaged: ``per_meeting_ejections`` /
    ``per_meeting_crewmate_ejections`` answer a different question (what the
    meeting class does) from ``per_victim_precision`` (what the evidence proves
    about the person it convicted). ``class_impostor_share`` deduplicates STRONG
    ``alibi_vs_sighting`` flags by (meeting, subject) and is read against
    ``living_voter_base_rate``, the pooled impostor share of the living rosters at
    those same meetings.
    """

    per_victim_precision: WilsonRateCell
    per_victim_single_flag_precision: WilsonRateCell
    per_meeting_sole_flag_meetings: int
    per_meeting_ejections: int
    per_meeting_crewmate_ejections: WilsonRateCell
    class_impostor_share: WilsonRateCell
    living_voter_base_rate: WilsonRateCell


class GroundedSightingCells(_FrozenModel):
    """I-4 grounded sighting side.

    numerator: STRONG alibi_vs_sighting sighting sides the speaker's own recorded
    perception supports within the stated tick tolerance; denominator: the
    RESOLVABLE sides only, never the full flag count; the spoken tick is resolved
    to the engine frame as tick - 1; it does NOT measure whether the sighting was
    factually true, only whether the speaker could have seen it.

    ``meetings.transcript.SIGHTING_GROUNDING_TICK_TOLERANCE`` (2) is production's
    tolerance for the exculpatory vouch channel and is a DIFFERENT thing from this
    instrument's parameter: it gates a −0.05 belief nudge, not a measurement. The
    three cells are emitted side by side so no bar is stated on an unnamed
    tolerance.
    """

    strong_sides: int
    resolvable_sides: int
    unresolvable_sides: int
    grounded_at_tick: WilsonRateCell
    grounded_within_1: WilsonRateCell
    grounded_within_2: WilsonRateCell


class FabricatedCompletionCells(_FrozenModel):
    """I-5 fabricated completion lines.

    numerator: distinct rendered You completed memory rows with no task_completed
    engine event for that agent at any earlier tick; denominator: all distinct
    rendered You completed rows; the render stamps a completion one tick after the
    engine event, so the calibration is memory tick = event tick + 1; it does NOT
    measure whether the fabricated line was spoken at a meeting.

    ``render_offset_matches`` / ``render_offset_checked`` calibrate that +1 in
    module: every TRUE line whose agent has exactly one earlier completion must sit
    one tick after it. ``games_hit`` counts games carrying at least one fabricated
    row.
    """

    lines: int
    fabricated: WilsonRateCell
    render_offset_matches: int
    render_offset_checked: int
    games_hit: int


class AdjacentRoomFlagCells(_FrozenModel):
    """I-6 adjacent-room STRONG share.

    numerator: STRONG alibi_vs_sighting flags whose alibi room and sighting room
    are one doorway apart on the committed map; denominator: all STRONG
    alibi_vs_sighting flags; both rooms are read from the recorded flag's own two
    events, no clock conversion applies; it does NOT measure reachability across
    more than one doorway.

    Adjacency comes from ``engine/maps/canonical_1.yaml``'s doorway list through
    ``Map.room_neighbors`` — never a hard-coded room table. ``adjacent`` is the
    REGISTERED cell and carries the tick-gap rule with it: the sighting must also
    sit within one tick of the alibi window's nearest endpoint, which is what makes
    the pair reconcilable by one tick of walking. ``adjacent_any_gap`` drops that
    condition, and the two coincide on the committed bytes (148/234 either way) —
    which is exactly why the bar has to name the stricter one before a lever can
    separate them. ``single_tick_window`` counts flags whose alibi window is one
    tick.
    """

    strong_flags: int
    adjacent: WilsonRateCell
    adjacent_any_gap: WilsonRateCell
    distance_two: int
    distance_three_or_more: int
    single_tick_window: int


class MovementOriginFlagCells(_FrozenModel):
    """I-7 movement-origin flags.

    numerator: alibi_vs_sighting flags whose sighting names the ORIGIN half of a
    saw_player move from A to B row in the speaker's own memory; denominator: all
    alibi_vs_sighting flags resolvable to a spoken sighting; the memory row's tick
    is the spoken tick, so no conversion applies; it does NOT measure
    destination-half re-speaks, which are truthful.

    ``memory_truthful_spoken_false`` is the sub-count of origin flags whose memory
    row was TRUE (the subject really moved A→B across that tick pair) while the
    spoken placement was false — the shape that makes the flag a manufactured
    contradiction rather than a caught lie.
    """

    resolved_flags: int
    backed_by_move_line: int
    spoke_destination: int
    spoke_origin: WilsonRateCell
    origin_strong: int
    memory_truthful_spoken_false: int


class MarkerContaminationCells(_FrozenModel):
    """I-8 dev-marker contamination.

    numerator: transcript turns whose free_text begins with a meetings.manager
    audit marker, and separately the recorded prompts containing one; denominators:
    all turns and all recorded prompts; no clock applies; it does NOT measure
    ballot-rationale markers, which never reach a prompt.

    The marker set is derived from the ``meetings.manager`` constants
    (``INVALID_ACCUSATION_TARGET_MARKER``, ``INVALID_ALIBI_SUBJECT_MARKER``,
    ``INVALID_CORROBORATION_SUPPORTS_MARKER``), so a constant edit moves the cell
    instead of leaving it silently stale.
    """

    turns_with_marker: WilsonRateCell
    prompts_with_marker: WilsonRateCell
    meetings_with_marker: int
    games_with_marker: int


class SingularPersonaCells(_FrozenModel):
    """I-9 singular-persona prompts.

    numerator: recorded prompts carrying the templates' singular hidden-impostor
    persona phrase; denominator: all recorded prompts; no clock applies; the cell
    is NOT-APPLICABLE on a one-impostor roster, where the singular persona is true,
    and it does NOT measure whether the model acted on the contradiction.

    ``applicable`` is ``False`` on a one-impostor roster: the count is still
    reported, because a zero here would read as "clean" when it is merely correct.
    The phrase is extracted from the committed templates rather than re-typed, so a
    prompt-set edit shows up as a changed cell.
    """

    applicable: bool
    prompts_with_singular_persona: WilsonRateCell


class MeetingPhysicalityCells(_FrozenModel):
    """I-10 meeting physicality (context cells).

    numerators: meetings with at least one living participant inside a vent, and
    meetings whose reporter was killed within three ticks after it; denominator:
    all resolved meetings; ticks are engine ticks and the kill window is inclusive
    of the first three ticks after the meeting tick; the reporter cell is restricted
    to body-triggered meetings and does NOT measure emergency meetings.
    """

    meetings: int
    body_triggered_meetings: int
    venting_participants: WilsonRateCell
    reporter_killed_within_three: WilsonRateCell


class ImpostorTargetingCells(_FrozenModel):
    """I-11 impostor targeting (co-intervention cells).

    numerators: free zero-witness kill opportunities the policy declined, and
    impostor decisions whose top-ranked target was already dead; denominators: the
    free-kill opportunities and all reconstructed impostor decisions; opportunities
    are read from the PRE-advance engine state the tick's actions were decided
    from; it does NOT measure whether the declined kill would have landed, because
    a lower-id target may dodge in the same tick.

    ``decisions_reconstructed`` / ``reconstruction_mismatches`` are the
    precondition's own witness: the walk RAISES on the first decision the rebuilt
    memory + real ``ImpostorPolicy.decide`` does not reproduce, so a report that
    exists at all carries ``reconstruction_mismatches == 0`` — the field is here
    because the memo quotes the pair ("0 mismatches over N decisions") and the
    denominator moves when the corpus does. ``ghost_top_ejected`` / ``ghost_top_unseen_death`` split the
    ghost-top population into the two sub-populations that cause it.
    """

    decisions_reconstructed: int
    reconstruction_mismatches: int
    in_vent_decisions: int
    free_kill_opportunities: int
    free_kills_declined: WilsonRateCell
    decline_reason_ranking: int
    decline_reason_fellow_defer: int
    decline_reason_cover: int
    decline_reason_other: int
    ghost_top: WilsonRateCell
    ghost_top_ejected: int
    ghost_top_unseen_death: int


class RenderBudgetCells(_FrozenModel):
    """The render-budget cells the lever tasks and the counterfactual print.

    ``rendered_lines_mean`` is the mean number of rendered episodic rows per prompt
    snapshot — the budget any render lever spends against.
    ``testimony_rows_by_living_bucket`` counts reported-testimony rows kept,
    bucketed by the meeting's LIVING-player count, so a retention change reads per
    bucket rather than as one blended number. The bucket key is the roster size,
    NOT the number of candidate rows the token-budget selector saw — the selector's
    own input is not recoverable from the recorded prompt, and a cell keyed on it
    belongs to the render task that owns the selector.
    """

    snapshots: int
    rendered_lines_total: int
    rendered_lines_mean: float | None
    testimony_rows_total: int
    testimony_rows_by_living_bucket: Mapping[str, int]


class EvidenceHonestyReport(_FrozenModel):
    """One replay set's evidence-honesty cells — counts and rate cells only.

    ``clock_alignment_checked`` is the number of discriminating sightings the +1
    agent-clock assertion passed on, and ``clock_alignment_action_stamped`` the
    subset of those whose row carried a perceived action and was therefore checked
    against the two-frame rule. Both are zero only for a set with no sighting that
    discriminates, which no committed set is.
    """

    replay_set_dir: str
    num_players: int
    num_impostors: int
    tasks_per_crewmate: int
    games_total: int
    clock_alignment_checked: int
    clock_alignment_action_stamped: int
    false_whereabouts: FalseWhereaboutsCells
    sole_flag_precision: SoleFlagPrecisionCells
    grounded_sighting: GroundedSightingCells
    fabricated_completions: FabricatedCompletionCells
    adjacent_room_flags: AdjacentRoomFlagCells
    movement_origin_flags: MovementOriginFlagCells
    marker_contamination: MarkerContaminationCells
    singular_persona: SingularPersonaCells
    meeting_physicality: MeetingPhysicalityCells
    impostor_targeting: ImpostorTargetingCells
    render_budget: RenderBudgetCells


# --------------------------------------------------------------------------- #
# Per-game folded facts (counts only leave the module).                        #
# --------------------------------------------------------------------------- #


@dataclass
class _Tallies:
    """Every cell's raw counters, accumulated across a replay set's games."""

    clock_checked: int = 0
    clock_checked_action_stamped: int = 0
    crew_claims: int = 0
    crew_false: int = 0
    crew_false_agent_frame: int = 0
    impostor_claims: int = 0
    impostor_false: int = 0
    copyable_self_location: int = 0

    sole_victim_total: int = 0
    sole_victim_impostor: int = 0
    single_flag_victim_total: int = 0
    single_flag_victim_impostor: int = 0
    sole_meetings: int = 0
    sole_meeting_ejections: int = 0
    sole_meeting_crewmate_ejections: int = 0
    class_subjects: int = 0
    class_subject_impostors: int = 0
    base_rate_living: int = 0
    base_rate_impostors: int = 0

    strong_sides: int = 0
    resolvable_sides: int = 0
    grounded_at_tick: int = 0
    grounded_within_1: int = 0
    grounded_within_2: int = 0

    completion_lines: int = 0
    fabricated_lines: int = 0
    render_offset_matches: int = 0
    render_offset_checked: int = 0
    fabricated_games: int = 0

    strong_flags: int = 0
    adjacent_flags: int = 0
    adjacent_any_gap: int = 0
    distance_two: int = 0
    distance_three_plus: int = 0
    single_tick_window: int = 0

    resolved_sighting_flags: int = 0
    move_backed_flags: int = 0
    destination_flags: int = 0
    origin_flags: int = 0
    origin_strong: int = 0
    origin_memory_truthful: int = 0

    turns: int = 0
    marker_turns: int = 0
    prompts: int = 0
    marker_prompts: int = 0
    marker_meetings: int = 0
    marker_games: int = 0
    persona_prompts: int = 0

    meetings: int = 0
    body_meetings: int = 0
    venting_meetings: int = 0
    reporter_killed_meetings: int = 0

    decisions: int = 0
    mismatches: int = 0
    in_vent_decisions: int = 0
    free_kill_opportunities: int = 0
    free_kills_declined: int = 0
    decline_ranking: int = 0
    decline_fellow: int = 0
    decline_cover: int = 0
    decline_other: int = 0
    ghost_top: int = 0
    ghost_top_ejected: int = 0
    ghost_top_unseen: int = 0

    snapshots: int = 0
    rendered_lines: int = 0
    testimony_rows: int = 0
    testimony_by_bucket: Counter[str] = field(default_factory=Counter)


def compute_evidence_honesty(sample_dir: Path) -> EvidenceHonestyReport:
    """Compute the evidence-honesty cells over one committed replay set.

    Pure + offline: resolve the roster, recover per-seed role ground truth by
    re-seeding, walk every committed game once under the referee-grade profile
    (rebuilding each living agent's memory through the real perception path), and
    fold every cell from the recorded transcripts, flags and prompts. Fails loud
    (:class:`EvidenceHonestyReconstructionError`) on any reconstruction
    disagreement, on a clock-offset exception, or on a policy decision the
    reconstruction cannot reproduce.
    """

    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(sample_dir)
    game_map = load_canonical_map()
    per_seed_roles = roles_by_seed(
        sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
    )
    seeds = seeds_on_disk(sample_dir)
    if not seeds:
        raise EvidenceHonestyReconstructionError(
            f"{sample_dir}: no replay-seed-*.jsonl files found — not a replay set "
            "(wrong path?); refusing to report a zero-game measurement"
        )

    distances = _room_distances(game_map)
    persona_phrase = _singular_persona_phrase()
    tallies = _Tallies()
    public_map = public_map_from_engine_map(game_map)
    for seed in seeds:
        _fold_game(
            sample_dir / f"replay-seed-{seed}.jsonl",
            seed=seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            roles=per_seed_roles[seed],
            game_map=game_map,
            public_map=public_map,
            distances=distances,
            persona_phrase=persona_phrase,
            tallies=tallies,
        )

    return _report(
        sample_dir=sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        games_total=len(seeds),
        tallies=tallies,
    )


def _report(
    *,
    sample_dir: Path,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
    games_total: int,
    tallies: _Tallies,
) -> EvidenceHonestyReport:
    """Assemble the frozen report from the folded counters."""

    return EvidenceHonestyReport(
        replay_set_dir=str(sample_dir),
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        games_total=games_total,
        clock_alignment_checked=tallies.clock_checked,
        clock_alignment_action_stamped=tallies.clock_checked_action_stamped,
        false_whereabouts=FalseWhereaboutsCells(
            crew_claims=tallies.crew_claims,
            crew_false=cell(tallies.crew_false, tallies.crew_claims),
            crew_false_agent_frame=cell(
                tallies.crew_false_agent_frame, tallies.crew_claims
            ),
            impostor_false=cell(tallies.impostor_false, tallies.impostor_claims),
            copyable_self_location=cell(
                tallies.copyable_self_location, tallies.crew_claims
            ),
        ),
        sole_flag_precision=SoleFlagPrecisionCells(
            per_victim_precision=cell(
                tallies.sole_victim_impostor, tallies.sole_victim_total
            ),
            per_victim_single_flag_precision=cell(
                tallies.single_flag_victim_impostor, tallies.single_flag_victim_total
            ),
            per_meeting_sole_flag_meetings=tallies.sole_meetings,
            per_meeting_ejections=tallies.sole_meeting_ejections,
            per_meeting_crewmate_ejections=cell(
                tallies.sole_meeting_crewmate_ejections, tallies.sole_meeting_ejections
            ),
            class_impostor_share=cell(
                tallies.class_subject_impostors, tallies.class_subjects
            ),
            living_voter_base_rate=cell(
                tallies.base_rate_impostors, tallies.base_rate_living
            ),
        ),
        grounded_sighting=GroundedSightingCells(
            strong_sides=tallies.strong_sides,
            resolvable_sides=tallies.resolvable_sides,
            unresolvable_sides=tallies.strong_sides - tallies.resolvable_sides,
            grounded_at_tick=cell(tallies.grounded_at_tick, tallies.resolvable_sides),
            grounded_within_1=cell(tallies.grounded_within_1, tallies.resolvable_sides),
            grounded_within_2=cell(tallies.grounded_within_2, tallies.resolvable_sides),
        ),
        fabricated_completions=FabricatedCompletionCells(
            lines=tallies.completion_lines,
            fabricated=cell(tallies.fabricated_lines, tallies.completion_lines),
            render_offset_matches=tallies.render_offset_matches,
            render_offset_checked=tallies.render_offset_checked,
            games_hit=tallies.fabricated_games,
        ),
        adjacent_room_flags=AdjacentRoomFlagCells(
            strong_flags=tallies.strong_flags,
            adjacent=cell(tallies.adjacent_flags, tallies.strong_flags),
            adjacent_any_gap=cell(tallies.adjacent_any_gap, tallies.strong_flags),
            distance_two=tallies.distance_two,
            distance_three_or_more=tallies.distance_three_plus,
            single_tick_window=tallies.single_tick_window,
        ),
        movement_origin_flags=MovementOriginFlagCells(
            resolved_flags=tallies.resolved_sighting_flags,
            backed_by_move_line=tallies.move_backed_flags,
            spoke_destination=tallies.destination_flags,
            spoke_origin=cell(tallies.origin_flags, tallies.resolved_sighting_flags),
            origin_strong=tallies.origin_strong,
            memory_truthful_spoken_false=tallies.origin_memory_truthful,
        ),
        marker_contamination=MarkerContaminationCells(
            turns_with_marker=cell(tallies.marker_turns, tallies.turns),
            prompts_with_marker=cell(tallies.marker_prompts, tallies.prompts),
            meetings_with_marker=tallies.marker_meetings,
            games_with_marker=tallies.marker_games,
        ),
        singular_persona=SingularPersonaCells(
            applicable=num_impostors > 1,
            prompts_with_singular_persona=cell(
                tallies.persona_prompts, tallies.prompts
            ),
        ),
        meeting_physicality=MeetingPhysicalityCells(
            meetings=tallies.meetings,
            body_triggered_meetings=tallies.body_meetings,
            venting_participants=cell(tallies.venting_meetings, tallies.meetings),
            reporter_killed_within_three=cell(
                tallies.reporter_killed_meetings, tallies.meetings
            ),
        ),
        impostor_targeting=ImpostorTargetingCells(
            decisions_reconstructed=tallies.decisions,
            reconstruction_mismatches=tallies.mismatches,
            in_vent_decisions=tallies.in_vent_decisions,
            free_kill_opportunities=tallies.free_kill_opportunities,
            free_kills_declined=cell(
                tallies.free_kills_declined, tallies.free_kill_opportunities
            ),
            decline_reason_ranking=tallies.decline_ranking,
            decline_reason_fellow_defer=tallies.decline_fellow,
            decline_reason_cover=tallies.decline_cover,
            decline_reason_other=tallies.decline_other,
            ghost_top=cell(tallies.ghost_top, tallies.decisions),
            ghost_top_ejected=tallies.ghost_top_ejected,
            ghost_top_unseen_death=tallies.ghost_top_unseen,
        ),
        render_budget=RenderBudgetCells(
            snapshots=tallies.snapshots,
            rendered_lines_total=tallies.rendered_lines,
            rendered_lines_mean=(
                tallies.rendered_lines / tallies.snapshots
                if tallies.snapshots
                else None
            ),
            testimony_rows_total=tallies.testimony_rows,
            testimony_rows_by_living_bucket=dict(
                sorted(tallies.testimony_by_bucket.items())
            ),
        ),
    )


def cell(numerator: int, denominator: int) -> WilsonRateCell:
    """Build a :class:`WilsonRateCell` over the imported Wilson helper."""

    rate, low, high = _wilson_interval(numerator, denominator)
    return WilsonRateCell(
        numerator=numerator,
        denominator=denominator,
        rate=rate,
        wilson_low=low,
        wilson_high=high,
        advisory=numerator <= _RARE_EVENT_ADVISORY_MAX_NUMERATOR,
    )


# --------------------------------------------------------------------------- #
# Map geometry (doorways only — never a hard-coded room table).                #
# --------------------------------------------------------------------------- #


def _room_distances(game_map: Map) -> Mapping[RoomId, Mapping[RoomId, int]]:
    """All-pairs doorway distance over the committed map's room graph."""

    rooms = sorted(game_map.rooms)
    distances: dict[RoomId, Mapping[RoomId, int]] = {}
    for source in rooms:
        seen: dict[RoomId, int] = {source: 0}
        queue: deque[RoomId] = deque([source])
        while queue:
            current = queue.popleft()
            for neighbor in game_map.room_neighbors(current):
                if neighbor not in seen:
                    seen[neighbor] = seen[current] + 1
                    queue.append(neighbor)
        distances[source] = seen
    return distances


def _singular_persona_phrase() -> str:
    """The singular hidden-impostor phrase the I-9 cell counts.

    Read out of the committed templates while they still carry it, so a template
    edit that rewords the persona moves the cell instead of leaving it silently
    stale. Once every template has dropped the singular wording the cell must
    still be countable — a fresh tournament reads 0/N and the committed bytes keep
    reading 1956/1956 — so the literal falls back to the recorded phrase rather
    than raising and taking the instrument down with the fix. Templates that
    disagree with each other DO raise: that is drift, not a graduation.
    """

    root = Path(__file__).resolve().parent.parent / "agents" / "strategic" / "prompts"
    phrases: set[str] = set()
    for name in _PERSONA_TEMPLATES:
        text = (root / _RECORDED_PROMPT_SET / name).read_text(encoding="utf-8")
        match = _SINGULAR_PERSONA_PATTERN.search(text)
        if match is not None:
            phrases.add(match.group(0))
    if not phrases:
        return _RECORDED_SINGULAR_PERSONA_PHRASE
    if len(phrases) != 1:
        raise EvidenceHonestyReconstructionError(
            f"the persona templates carry {len(phrases)} different singular "
            f"phrases: {sorted(phrases)}"
        )
    return phrases.pop()


def _marker_prefixes() -> tuple[str, ...]:
    """The turn-``free_text`` audit-marker prefixes, from the manager constants."""

    return tuple(
        marker.split("{", 1)[0]
        for marker in (
            INVALID_ACCUSATION_TARGET_MARKER,
            INVALID_ALIBI_SUBJECT_MARKER,
            INVALID_CORROBORATION_SUPPORTS_MARKER,
        )
    )


_MARKER_PREFIXES: Final[tuple[str, ...]] = _marker_prefixes()


# --------------------------------------------------------------------------- #
# The walk (eval.replay_walk under the 'evidence-honesty' profile).            #
# --------------------------------------------------------------------------- #


@dataclass
class _MeetingFacts:
    """One recorded meeting, with the reconstruction facts its cells need."""

    entry: MeetingReplayEntry
    living: frozenset[PlayerId]
    venting: frozenset[PlayerId]
    body_triggered: bool


def _fold_game(
    replay_path: Path,
    *,
    seed: int,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
    roles: Mapping[PlayerId, Role],
    game_map: Map,
    public_map: PublicMapView,
    distances: Mapping[RoomId, Mapping[RoomId, int]],
    persona_phrase: str,
    tallies: _Tallies,
) -> None:
    """Walk one recording once and fold every cell it contributes to."""

    game_id = f"headless-seed-{seed}"
    impostor_ids = frozenset(pid for pid, role in roles.items() if role == "IMPOSTOR")
    memories: dict[PlayerId, MemoryStore] = {pid: MemoryStore() for pid in roles}
    policies = {pid: ImpostorPolicy(agent_id=pid) for pid in sorted(impostor_ids)}
    # Engine frame: ``room_at[T]`` is the state after tick ``T``'s recorded
    # actions resolved — the frame the replay row's ``state_hash`` covers and the
    # frame the loader serves as "tick T". A memory row at agent tick ``T``
    # describes ``room_at[T - AGENT_CLOCK_OFFSET]``.
    room_at: dict[int, Mapping[PlayerId, RoomId]] = {}
    completions: dict[PlayerId, set[int]] = {pid: set() for pid in roles}
    death_tick: dict[PlayerId, int] = {}
    ejected_at: dict[PlayerId, int] = {}
    kill_ticks: list[tuple[int, PlayerId]] = []
    meetings: list[_MeetingFacts] = []
    # Top-ranked targets, deferred until the death table is complete: a target can
    # be ejected at a meeting later than the decision that ranked it.
    ranked_first: list[tuple[int, PlayerId]] = []

    audit_dir = tempfile.TemporaryDirectory(prefix="ailibi-honesty-")
    service = ObservationService(
        game_map=game_map, audit_log_path=Path(audit_dir.name) / "audit.jsonl"
    )
    try:
        for walk_event in walk_replay(
            replay_path,
            seed=seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            game_map=game_map,
            config=_WALK_CONFIG,
        ):
            if isinstance(walk_event, TickOpened):
                state = walk_event.state
                for pid in sorted(state.players):
                    if not state.players[pid].alive:
                        continue
                    ingest_packet(
                        packet=service.build_packet(
                            world_state=state,
                            agent_id=pid,
                            engine_events=walk_event.last_events,
                        ),
                        memory=memories[pid],
                    )
                _fold_impostor_decisions(
                    game_id=game_id,
                    walk_event=walk_event,
                    impostor_ids=impostor_ids,
                    memories=memories,
                    policies=policies,
                    public_map=public_map,
                    ranked_first=ranked_first,
                    tallies=tallies,
                )
            elif isinstance(walk_event, TickAdvanced):
                room_at[walk_event.entry.tick] = {
                    pid: player.room for pid, player in walk_event.state.players.items()
                }
                for event in walk_event.events:
                    if isinstance(event, TaskCompletedEvent):
                        completions[event.actor].add(event.tick)
                    elif isinstance(event, KilledEvent):
                        death_tick.setdefault(event.target, event.tick)
                        kill_ticks.append((event.tick, event.target))
            elif isinstance(walk_event, MeetingOpened):
                state = walk_event.state
                meetings.append(
                    _MeetingFacts(
                        entry=walk_event.entry,
                        living=frozenset(
                            pid for pid, p in state.players.items() if p.alive
                        ),
                        venting=frozenset(
                            pid
                            for pid, p in state.players.items()
                            if p.alive and p.in_vent
                        ),
                        body_triggered=walk_event.body_id is not None,
                    )
                )
            elif isinstance(walk_event, MeetingApplied):
                entry = walk_event.entry
                if entry.outcome == "EJECTED" and entry.ejected_player_id is not None:
                    ejected_at.setdefault(entry.ejected_player_id, entry.tick)
                    death_tick.setdefault(entry.ejected_player_id, entry.tick)
    finally:
        service.close()
        audit_dir.cleanup()

    _assert_clock_alignment(
        game_id=game_id, memories=memories, room_at=room_at, tallies=tallies
    )
    _fold_ghost_top(
        tallies=tallies,
        ranked_first=ranked_first,
        death_tick=death_tick,
        ejected_at=ejected_at,
    )
    _fold_meetings(
        game_id=game_id,
        meetings=meetings,
        roles=roles,
        memories=memories,
        room_at=room_at,
        completions=completions,
        kill_ticks=kill_ticks,
        distances=distances,
        persona_phrase=persona_phrase,
        tallies=tallies,
    )


def _fold_impostor_decisions(
    *,
    game_id: str,
    walk_event: TickOpened,
    impostor_ids: frozenset[PlayerId],
    memories: Mapping[PlayerId, MemoryStore],
    policies: Mapping[PlayerId, ImpostorPolicy],
    public_map: PublicMapView,
    ranked_first: list[tuple[int, PlayerId]],
    tallies: _Tallies,
) -> None:
    """Reconstruct this tick's impostor decisions and fold the I-11 counters.

    The recorded action for an actor is the ground truth: a decision is counted
    only for an impostor the recording asked to act this tick, and every
    reconstructed intent is compared against the recorded action before any cell
    reads the ranking.
    """

    state = walk_event.state
    recorded = {
        str(raw["actor"]): raw
        for raw in walk_event.entry.actions
        if isinstance(raw.get("actor"), str)
    }
    for pid in sorted(impostor_ids):
        raw_action = recorded.get(pid)
        if raw_action is None:
            continue
        player = state.players[pid]
        if not player.alive:
            continue
        tallies.decisions += 1
        if player.in_vent:
            tallies.in_vent_decisions += 1
        intent = policies[pid].decide(memories[pid], public_map)
        if translate_action_intent(intent).model_dump(mode="python") != dict(
            raw_action
        ):
            tallies.mismatches += 1
            raise EvidenceHonestyReconstructionError(
                f"{game_id}: tick {walk_event.entry.tick} impostor {pid} "
                "reconstructed a different action than the recording holds — the "
                "targeting cells would price a policy the recording never ran"
            )

        targets = policies[pid].ranked_targets(memories[pid])
        if targets:
            ranked_first.append((walk_event.entry.tick, targets[0].player_id))

        victim = _free_kill_victim(
            state=state, actor=pid, impostor_ids=impostor_ids, cooldown=state.cooldowns
        )
        if victim is None:
            continue
        tallies.free_kill_opportunities += 1
        if intent.type == "kill":
            continue
        tallies.free_kills_declined += 1
        _classify_decline(
            actor=pid,
            victim=victim,
            state=state,
            impostor_ids=impostor_ids,
            memory=memories[pid],
            targets=targets,
            tallies=tallies,
        )


def _free_kill_victim(
    *,
    state: WorldState,
    actor: PlayerId,
    impostor_ids: frozenset[PlayerId],
    cooldown: Mapping[PlayerId, int],
) -> PlayerId | None:
    """The lone killable crewmate this tick, or ``None`` if there is no free kill.

    The predicate is derived from the ENGINE rules, never from the policy's own
    ``_kill_available_now`` (which inherits the ``targets[0]``-only defect these
    cells measure): the actor is a living, non-vented impostor off cooldown, an
    alive non-vented non-fellow player shares its room, and no OTHER living
    non-vented non-fellow player is there to witness it.
    """

    player = state.players[actor]
    if not player.alive or player.in_vent or cooldown.get(actor, 0) != 0:
        return None
    others = [
        pid
        for pid, other in state.players.items()
        if pid != actor
        and pid not in impostor_ids
        and other.alive
        and not other.in_vent
        and other.room == player.room
    ]
    return others[0] if len(others) == 1 else None


def _classify_decline(
    *,
    actor: PlayerId,
    victim: PlayerId,
    state: WorldState,
    impostor_ids: frozenset[PlayerId],
    memory: MemoryStore,
    targets: Sequence[RankedTarget],
    tallies: _Tallies,
) -> None:
    """Attribute one declined free kill to the branch that swallowed it.

    Branch order mirrors ``ImpostorPolicy.decide``: a body in the impostor's own
    room takes the COVER branch before any kill logic; otherwise the kill seam only
    re-validates ``targets[0]``, so a top-ranked target that is not the co-located
    victim is the ranking defect; a co-located lower-id fellow is the Task-7.9
    deliberate defer.
    """

    own_room = state.players[actor].room
    latest_tick = memory.recent(since_tick=0)[-1].tick
    body_here = any(
        event.type == EVENT_SAW_BODY
        and event.tick == latest_tick
        and event.payload.get("room") == own_room
        for event in memory.recent(since_tick=latest_tick)
    )
    if body_here:
        tallies.decline_cover += 1
        return
    if not targets or targets[0].player_id != victim or targets[0].co_present != 0:
        tallies.decline_ranking += 1
        return
    if any(
        pid < actor
        and pid in impostor_ids
        and other.alive
        and not other.in_vent
        and other.room == own_room
        for pid, other in state.players.items()
    ):
        tallies.decline_fellow += 1
        return
    tallies.decline_other += 1


def _fold_ghost_top(
    *,
    tallies: _Tallies,
    ranked_first: Sequence[tuple[int, PlayerId]],
    death_tick: Mapping[PlayerId, int],
    ejected_at: Mapping[PlayerId, int],
) -> None:
    """Score the deferred top-ranked targets once the death table is complete.

    A ghost-top decision ranks first a player already removed from the game at the
    decision tick: ejected at an earlier meeting (the sub-population the dead-set
    repair closes) or killed with a body this impostor never had to see.
    """

    for tick, target in ranked_first:
        died = death_tick.get(target)
        if died is None or died >= tick:
            continue
        tallies.ghost_top += 1
        if target in ejected_at and ejected_at[target] < tick:
            tallies.ghost_top_ejected += 1
        else:
            tallies.ghost_top_unseen += 1


def _assert_clock_alignment(
    *,
    game_id: str,
    memories: Mapping[PlayerId, MemoryStore],
    room_at: Mapping[int, Mapping[PlayerId, RoomId]],
    tallies: _Tallies,
) -> None:
    """Prove the +1 agent clock on this game's discriminating sightings.

    A sighting DISCRIMINATES when the subject's engine room differs between the
    two candidate ticks. EVERY discriminating sighting is checked, under the rule
    its own row was stamped by:

    * a STATE-READ row (no perceived ``action``) must name the subject's room at
      ``obs.tick - 1`` exactly — the +1 offset;
    * an ACTION-BEARING row is stamped with that action's OWN room out of the
      previous tick's event list rather than read off the world state
      (``observation.service.ObservationService._visible_players`` prefers
      ``observed_action.room``), so it names the room at ``obs.tick - 1`` or the
      room the action resolved in at ``obs.tick - 2``.

    Neither branch tolerates anything else, so a clock change fails here first
    instead of silently re-pricing every bar.
    """

    for observer in sorted(memories):
        for event in memories[observer].recent(since_tick=0):
            if event.type != EVENT_SAW_PLAYER:
                continue
            subject = event.payload.get("player_id")
            room = event.payload.get("room")
            if not isinstance(subject, str) or not isinstance(room, str):
                continue
            engine_tick = event.tick - AGENT_CLOCK_OFFSET
            here = room_at.get(engine_tick, {}).get(subject)
            if here is None:
                continue
            action_stamped = event.payload.get("action") is not None
            # A row DISCRIMINATES when its own two candidate frames disagree: the
            # state read is ``obs.tick - 1`` against ``obs.tick``, the action stamp
            # is ``obs.tick - 1`` against ``obs.tick - 2``. Comparing an
            # action-bearing row against the state-read pair would skip exactly the
            # rows whose subject moved during the action but stood still after it.
            other = room_at.get(
                engine_tick - 1 if action_stamped else event.tick, {}
            ).get(subject)
            if other is None or here == other:
                continue
            tallies.clock_checked += 1
            allowed = [here]
            if action_stamped:
                tallies.clock_checked_action_stamped += 1
                allowed.append(other)
            if room not in allowed:
                raise EvidenceHonestyReconstructionError(
                    f"{game_id}: {observer} recorded seeing {subject} in {room} at "
                    f"agent tick {event.tick}, but the engine frame allows only "
                    f"{sorted(set(allowed))} — the +1 agent clock moved and every "
                    "cell below would be re-priced by one tick"
                )


# --------------------------------------------------------------------------- #
# The meeting-row folds (transcripts, recorded flags, recorded prompts).       #
# --------------------------------------------------------------------------- #


def _fold_meetings(
    *,
    game_id: str,
    meetings: Sequence[_MeetingFacts],
    roles: Mapping[PlayerId, Role],
    memories: Mapping[PlayerId, MemoryStore],
    room_at: Mapping[int, Mapping[PlayerId, RoomId]],
    completions: Mapping[PlayerId, set[int]],
    kill_ticks: Sequence[tuple[int, PlayerId]],
    distances: Mapping[RoomId, Mapping[RoomId, int]],
    persona_phrase: str,
    tallies: _Tallies,
) -> None:
    """Fold every meeting-derived cell for one game."""

    game_marked = False
    game_fabricated = False
    # One rendered memory row is one row for the whole GAME: an agent's prompts
    # repeat the same row at every meeting it is still salient at.
    seen_rows: set[tuple[PlayerId, str]] = set()
    for facts in meetings:
        entry = facts.entry
        tallies.meetings += 1
        if facts.body_triggered:
            tallies.body_meetings += 1
        if facts.venting:
            tallies.venting_meetings += 1
        if facts.body_triggered and any(
            entry.tick < tick <= entry.tick + 3 and victim == entry.triggered_by
            for tick, victim in kill_ticks
        ):
            tallies.reporter_killed_meetings += 1

        self_locations = _fold_prompts(
            entry=entry,
            living=facts.living,
            persona_phrase=persona_phrase,
            completions=completions,
            seen_rows=seen_rows,
            tallies=tallies,
        )
        if self_locations.fabricated:
            game_fabricated = True

        marked = _fold_turns(entry.transcript, tallies=tallies)
        if marked:
            tallies.marker_meetings += 1
            game_marked = True

        _fold_whereabouts(
            transcript=entry.transcript,
            living=facts.living,
            roles=roles,
            room_at=room_at,
            copyable=self_locations.pairs,
            tallies=tallies,
        )
        _fold_flags(
            game_id=game_id,
            facts=facts,
            roles=roles,
            memories=memories,
            room_at=room_at,
            distances=distances,
            tallies=tallies,
        )
    if game_marked:
        tallies.marker_games += 1
    if game_fabricated:
        tallies.fabricated_games += 1


@dataclass
class _SelfLocations:
    """The rendered self-location rows one meeting's prompts exposed."""

    pairs: set[tuple[PlayerId, int, RoomId]] = field(default_factory=set)
    fabricated: bool = False


def _fold_prompts(
    *,
    entry: MeetingReplayEntry,
    living: frozenset[PlayerId],
    persona_phrase: str,
    completions: Mapping[PlayerId, set[int]],
    seen_rows: set[tuple[PlayerId, str]],
    tallies: _Tallies,
) -> _SelfLocations:
    """Fold I-5, I-8's prompt half, I-9 and the render-budget cells.

    Completion rows are deduplicated by ``(agent, observation_id)`` — one rendered
    memory row repeated across an agent's prompts is one row, not one per prompt.
    """

    found = _SelfLocations()
    for call in entry.llm_calls:
        tallies.prompts += 1
        prompt = call.prompt
        if persona_phrase in prompt:
            tallies.persona_prompts += 1
        if any(prefix in prompt for prefix in _MARKER_PREFIXES):
            tallies.marker_prompts += 1
        tallies.snapshots += 1
        rows = _RENDERED_ROW.findall(prompt)
        tallies.rendered_lines += len(rows)
        testimony = sum(
            1 for line in prompt.splitlines() if _TESTIMONY_ROW.match(line) is not None
        )
        tallies.testimony_rows += testimony
        tallies.testimony_by_bucket[_living_bucket(len(living))] += testimony
        _fold_completion_rows(
            call=call,
            completions=completions,
            seen_rows=seen_rows,
            found=found,
            tallies=tallies,
        )
    return found


def _living_bucket(living: int) -> str:
    """The living-roster bucket label a testimony count is reported under."""

    if living <= 4:
        return "<=4"
    if living <= 6:
        return "5-6"
    return ">=7"


def _fold_completion_rows(
    *,
    call: LLMCallRecord,
    completions: Mapping[PlayerId, set[int]],
    seen_rows: set[tuple[PlayerId, str]],
    found: _SelfLocations,
    tallies: _Tallies,
) -> None:
    """Score one prompt's rendered ``You completed`` rows (I-5)."""

    agent = call.agent_id
    if agent is None:
        return
    for match in _COMPLETED_LINE.finditer(call.prompt):
        key = (agent, match.group("observation_id"))
        tick = int(match.group("tick"))
        room = match.group("room")
        found.pairs.add((agent, tick, room))
        if key in seen_rows:
            continue
        seen_rows.add(key)
        tallies.completion_lines += 1
        completed: frozenset[int] | set[int] = completions.get(agent, frozenset())
        if not any(event_tick < tick for event_tick in completed):
            tallies.fabricated_lines += 1
            found.fabricated = True
            continue
        # Calibration: a TRUE row is stamped exactly one tick after the engine
        # event it reports, which is what makes "no event at any earlier tick"
        # the right falsity rule rather than "no event at tick - 1".
        tallies.render_offset_checked += 1
        if tick - AGENT_CLOCK_OFFSET in completed:
            tallies.render_offset_matches += 1


def _fold_turns(transcript: MeetingTranscript, *, tallies: _Tallies) -> bool:
    """Fold I-8's turn half; returns whether this meeting carried a marker."""

    marked = False
    for turn in transcript.turns:
        tallies.turns += 1
        if turn.free_text.startswith(_MARKER_PREFIXES):
            tallies.marker_turns += 1
            marked = True
    return marked


def _fold_whereabouts(
    *,
    transcript: MeetingTranscript,
    living: frozenset[PlayerId],
    roles: Mapping[PlayerId, Role],
    room_at: Mapping[int, Mapping[PlayerId, RoomId]],
    copyable: set[tuple[PlayerId, int, RoomId]],
    tallies: _Tallies,
) -> None:
    """Fold I-2 over the meeting's spoken ``whereabouts`` claims."""

    for turn in transcript.turns:
        speaker = turn.speaker
        if speaker not in living:
            continue
        for observation in turn.observations:
            if not isinstance(observation, WhereaboutsClaim):
                continue
            engine_rooms = tuple(
                room
                for room in (
                    room_at.get(observation.tick - offset, {}).get(speaker)
                    for offset in (0, 1)
                )
                if room is not None
            )
            if not engine_rooms:
                # The spoken tick names no recorded engine tick for this speaker
                # (a hallucinated tick past the game, or before it was alive):
                # unverifiable, and an unverifiable claim is not a false one.
                continue
            agent_frame_rooms = tuple(
                room
                for room in (
                    room_at.get(observation.tick - offset, {}).get(speaker)
                    for offset in (1, 2)
                )
                if room is not None
            )
            false_here = observation.room not in engine_rooms
            if roles.get(speaker) == "CREWMATE":
                tallies.crew_claims += 1
                tallies.crew_false += int(false_here)
                tallies.crew_false_agent_frame += int(
                    bool(agent_frame_rooms)
                    and observation.room not in agent_frame_rooms
                )
                if (speaker, observation.tick, observation.room) in copyable:
                    tallies.copyable_self_location += 1
            else:
                tallies.impostor_claims += 1
                tallies.impostor_false += int(false_here)


# --------------------------------------------------------------------------- #
# The recorded-flag folds (I-3, I-4, I-6, I-7).                                #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class _ResolvedFlag:
    """One recorded ``alibi_vs_sighting`` flag, resolved back to its two events."""

    flag: ContradictionRef
    strong: bool
    subject: PlayerId
    speaker: PlayerId
    sighting: SawPlayerObservation
    alibi_room: RoomId
    from_tick: int
    to_tick: int


def _fold_flags(
    *,
    game_id: str,
    facts: _MeetingFacts,
    roles: Mapping[PlayerId, Role],
    memories: Mapping[PlayerId, MemoryStore],
    room_at: Mapping[int, Mapping[PlayerId, RoomId]],
    distances: Mapping[RoomId, Mapping[RoomId, int]],
    tallies: _Tallies,
) -> None:
    """Fold I-3, I-4, I-6 and I-7 over one meeting's recorded flags."""

    entry = facts.entry
    index = _event_index(entry.transcript)
    strong_flags = [f for f in entry.contradictions if not is_weak_contradiction(f)]

    # I-3, per-meeting: alibi_vs_sighting is the meeting's ONLY strong evidence.
    if strong_flags and all(f.kind == "alibi_vs_sighting" for f in strong_flags):
        tallies.sole_meetings += 1
        if entry.outcome == "EJECTED" and entry.ejected_player_id is not None:
            tallies.sole_meeting_ejections += 1
            if roles.get(entry.ejected_player_id) == "CREWMATE":
                tallies.sole_meeting_crewmate_ejections += 1

    # I-3, per-victim: the ejected player's only strong flag is alibi_vs_sighting.
    if entry.outcome == "EJECTED" and entry.ejected_player_id is not None:
        victim = entry.ejected_player_id
        on_victim = [f for f in strong_flags if victim in f.subjects]
        if on_victim and all(f.kind == "alibi_vs_sighting" for f in on_victim):
            tallies.sole_victim_total += 1
            if roles.get(victim) == "IMPOSTOR":
                tallies.sole_victim_impostor += 1
            if len(on_victim) == 1:
                tallies.single_flag_victim_total += 1
                if roles.get(victim) == "IMPOSTOR":
                    tallies.single_flag_victim_impostor += 1

    # I-3, the class base rate: the living roster at meetings carrying the class.
    class_subjects = {
        subject
        for flag in strong_flags
        if flag.kind == "alibi_vs_sighting"
        for subject in flag.subjects
    }
    if class_subjects:
        tallies.class_subjects += len(class_subjects)
        tallies.class_subject_impostors += sum(
            1 for subject in class_subjects if roles.get(subject) == "IMPOSTOR"
        )
        tallies.base_rate_living += len(facts.living)
        tallies.base_rate_impostors += sum(
            1 for pid in facts.living if roles.get(pid) == "IMPOSTOR"
        )

    for flag in entry.contradictions:
        if flag.kind != "alibi_vs_sighting":
            continue
        resolved = _resolve_flag(flag, index=index)
        if resolved is None:
            raise EvidenceHonestyReconstructionError(
                f"{game_id}: meeting at tick {entry.tick} carries an "
                f"alibi_vs_sighting flag whose events {flag.event_a_id!r} / "
                f"{flag.event_b_id!r} do not resolve to one spoken sighting and "
                "one alibi — the flag would vanish from I-4, I-6 and I-7 while "
                "still counting in the I-3 class census"
            )
        if resolved.strong:
            tallies.strong_flags += 1
            _fold_geometry(resolved, distances=distances, tallies=tallies)
            _fold_grounding(
                resolved,
                memories=memories,
                room_at=room_at,
                tallies=tallies,
            )
        _fold_movement_origin(
            resolved, memories=memories, room_at=room_at, tallies=tallies
        )


def _event_index(
    transcript: MeetingTranscript,
) -> Mapping[str, tuple[PlayerId, object]]:
    """Index every turn artifact by the id ``meetings.transcript`` stamps on it."""

    index: dict[str, tuple[PlayerId, object]] = {}
    for turn in transcript.turns:
        for position, observation in enumerate(turn.observations):
            index[f"turn:{turn.turn_id}:obs:{position}"] = (turn.speaker, observation)
            if isinstance(observation, WhereaboutsClaim):
                index[f"turn:{turn.turn_id}:whereabouts:{position}"] = (
                    turn.speaker,
                    observation,
                )
        for position, claim in enumerate(turn.claims):
            index[f"turn:{turn.turn_id}:claim:{position}"] = (turn.speaker, claim)
    return index


def _resolve_flag(
    flag: ContradictionRef, *, index: Mapping[str, tuple[PlayerId, object]]
) -> _ResolvedFlag | None:
    """Resolve a recorded flag back to its alibi side and its sighting side.

    The two ids are read by TYPE, not by position: the detector emits the alibi in
    ``event_a_id`` on the direct path and in ``event_b_id`` on the re-targeted
    proxy path, so keying on position would silently drop a fifth of the class.
    """

    first = index.get(flag.event_a_id)
    second = index.get(flag.event_b_id)
    if first is None or second is None:
        return None
    sides = [(flag.event_a_id, first), (flag.event_b_id, second)]
    sightings = [
        (speaker, artifact)
        for event_id, (speaker, artifact) in sides
        if isinstance(artifact, SawPlayerObservation)
        and ":whereabouts:" not in event_id
    ]
    alibis = [
        artifact
        for event_id, (_, artifact) in sides
        if isinstance(artifact, AlibiClaim)
        or (isinstance(artifact, WhereaboutsClaim) and ":whereabouts:" in event_id)
    ]
    if len(sightings) != 1 or len(alibis) != 1:
        return None
    speaker, sighting = sightings[0]
    alibi = alibis[0]
    if not isinstance(sighting, SawPlayerObservation):
        return None
    if isinstance(alibi, AlibiClaim):
        alibi_room, from_tick, to_tick = alibi.room, alibi.from_tick, alibi.to_tick
    elif isinstance(alibi, WhereaboutsClaim):
        alibi_room, from_tick, to_tick = alibi.room, alibi.tick, alibi.tick
    else:
        return None
    return _ResolvedFlag(
        flag=flag,
        strong=not is_weak_contradiction(flag),
        subject=sighting.subject,
        speaker=speaker,
        sighting=sighting,
        alibi_room=alibi_room,
        from_tick=from_tick,
        to_tick=to_tick,
    )


def _fold_geometry(
    resolved: _ResolvedFlag,
    *,
    distances: Mapping[RoomId, Mapping[RoomId, int]],
    tallies: _Tallies,
) -> None:
    """Fold I-6 for one STRONG flag."""

    if resolved.from_tick == resolved.to_tick:
        tallies.single_tick_window += 1
    # Canonical room SETS, the comparison the detector itself made: a spoken label
    # may be lower-case or a compound ``A/B`` account, and a raw string compare
    # would move this cell on formatting alone.
    pairs = [
        distances.get(alibi, {}).get(seen)
        for alibi in canonical_rooms(resolved.alibi_room)
        for seen in canonical_rooms(resolved.sighting.room)
    ]
    reachable = [d for d in pairs if d is not None]
    if not reachable:
        return
    distance = min(reachable)
    gap = max(
        0,
        resolved.from_tick - resolved.sighting.tick,
        resolved.sighting.tick - resolved.to_tick,
    )
    if distance == 1:
        tallies.adjacent_any_gap += 1
        if gap <= 1:
            tallies.adjacent_flags += 1
    elif distance == 2:
        tallies.distance_two += 1
    elif distance >= 3:
        tallies.distance_three_plus += 1
    # distance 0 means the two canonical room sets intersect, which the detector
    # treats as CONSISTENT and never flags; it is counted in no geometry bucket.


def _fold_grounding(
    resolved: _ResolvedFlag,
    *,
    memories: Mapping[PlayerId, MemoryStore],
    room_at: Mapping[int, Mapping[PlayerId, RoomId]],
    tallies: _Tallies,
) -> None:
    """Fold I-4 for one STRONG flag's sighting side."""

    tallies.strong_sides += 1
    memory = memories.get(resolved.speaker)
    engine_tick = resolved.sighting.tick - AGENT_CLOCK_OFFSET
    if memory is None or engine_tick not in room_at:
        return
    tallies.resolvable_sides += 1
    spoken = canonical_rooms(resolved.sighting.room)
    gaps = [
        abs(event.tick - resolved.sighting.tick)
        for event in memory.recent(since_tick=0)
        if event.type == EVENT_SAW_PLAYER
        and event.payload.get("player_id") == resolved.sighting.subject
        and isinstance(event.payload.get("room"), str)
        and canonical_rooms(str(event.payload["room"])) & spoken
    ]
    if not gaps:
        return
    nearest = min(gaps)
    tallies.grounded_within_2 += int(nearest <= 2)
    tallies.grounded_within_1 += int(nearest <= 1)
    tallies.grounded_at_tick += int(nearest == 0)


def _fold_movement_origin(
    resolved: _ResolvedFlag,
    *,
    memories: Mapping[PlayerId, MemoryStore],
    room_at: Mapping[int, Mapping[PlayerId, RoomId]],
    tallies: _Tallies,
) -> None:
    """Fold I-7 for one flag resolvable to a spoken sighting."""

    tallies.resolved_sighting_flags += 1
    memory = memories.get(resolved.speaker)
    if memory is None:
        return
    moves = [
        event
        for event in memory.recent(since_tick=0)
        if event.type == EVENT_SAW_PLAYER_MOVE
        and event.tick == resolved.sighting.tick
        and event.payload.get("player_id") == resolved.sighting.subject
    ]
    if not moves:
        return
    move = moves[-1]
    origin = move.payload.get("from_room")
    destination = move.payload.get("to_room")
    tallies.move_backed_flags += 1
    spoken = canonical_rooms(resolved.sighting.room)
    if isinstance(destination, str) and canonical_rooms(destination) & spoken:
        tallies.destination_flags += 1
        return
    if not isinstance(origin, str) or not (canonical_rooms(origin) & spoken):
        return
    tallies.origin_flags += 1
    if resolved.strong:
        tallies.origin_strong += 1
    # The move resolved during engine tick ``T - AGENT_CLOCK_OFFSET``: the subject
    # stood in ``from_room`` at the end of the tick before it and in ``to_room``
    # at the end of that tick.
    engine_tick = resolved.sighting.tick - AGENT_CLOCK_OFFSET
    was_at_origin = room_at.get(engine_tick - 1, {}).get(resolved.sighting.subject)
    was_at_destination = room_at.get(engine_tick, {}).get(resolved.sighting.subject)
    if (
        was_at_origin == origin
        and was_at_destination == destination
        and was_at_destination != resolved.sighting.room
    ):
        tallies.origin_memory_truthful += 1


def _raise_walk_violation(violation: WalkViolation) -> NoReturn:
    """The ``evidence-honesty`` profile's violation hook — one message per kind."""

    messages: Mapping[str, str] = {
        "duplicate_meeting_rows": (
            "duplicate meeting rows (same tick or meeting id) — the collapsed "
            "duplicate's transcript and flags would never be counted"
        ),
        "tick_hash_mismatch": (
            f"tick {violation.tick} reconstructed {violation.actual!r} != "
            f"recorded {violation.expected!r}"
        ),
        "missing_meeting_row": (
            f"tick {violation.tick} entered MEETING with no recorded meeting row "
            "— every meeting-derived cell would silently under-count"
        ),
        "meeting_pre_hash_mismatch": (
            f"meeting at tick {violation.tick} recorded state_hash_before "
            f"{violation.expected!r} != reconstructed {violation.actual!r}"
        ),
        "meeting_post_hash_mismatch": (
            f"meeting at tick {violation.tick} recorded state_hash_after "
            f"{violation.expected!r} != reconstructed {violation.actual!r}"
        ),
        "missing_terminal_tick": (
            f"replay ends at tick {violation.state_tick} in phase "
            f"{violation.phase!r} without reaching GAME_OVER — a truncated "
            "recording would under-count every denominator"
        ),
        "trailing_replay_rows": (
            f"rows recorded after the terminal tick {violation.terminal_tick} — "
            "bytes the walk never validated"
        ),
        "missing_game_end_row": "no terminal game_over row",
    }
    detail = messages.get(violation.kind, f"walk violation {violation.kind!r}")
    raise EvidenceHonestyReconstructionError(f"{violation.game_id}: {detail}")


_WALK_CONFIG: Final[ReplayWalkConfig] = ReplayWalkConfig(
    profile="evidence-honesty",
    on_violation=_raise_walk_violation,
    verify_tick_hashes=True,
    reject_duplicate_meeting_rows=True,
    missing_meeting_row="violation",
    verify_meeting_pre_hashes=True,
    verify_meeting_post_hashes=True,
    require_terminal_tick=True,
    reject_trailing_rows=True,
    require_game_end_row=True,
)


__all__ = [
    "AGENT_CLOCK_OFFSET",
    "CELL_DEFINITIONS",
    "AdjacentRoomFlagCells",
    "EvidenceHonestyReconstructionError",
    "EvidenceHonestyReport",
    "FabricatedCompletionCells",
    "FalseWhereaboutsCells",
    "GroundedSightingCells",
    "ImpostorTargetingCells",
    "MarkerContaminationCells",
    "MeetingPhysicalityCells",
    "MovementOriginFlagCells",
    "RenderBudgetCells",
    "SingularPersonaCells",
    "SoleFlagPrecisionCells",
    "compute_evidence_honesty",
]
