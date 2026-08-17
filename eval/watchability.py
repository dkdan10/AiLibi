"""The committed champion-SELECTION referee — evidence-supply floors + D1-D4 geomean.

Task 15.2 (tasks/phase-15.md; tasks/post-phase-14-clean-up.md H2) promotes the
lab-tier interestingness scorer (``experiments/lab/rubric_score.py`` — which
self-labels "a design-thread analyzer, NOT a shipped eval gate") into committed,
strict-typed ``eval/`` code, re-anchored to baseline 2 and fed by committed
BYTES + the typed tournament report instead of the audit-tier facts JSON.

SELECTION-ONLY DOCTRINE (audits/post-phase-14-ML-training-signal.md §3.2, §4,
§6 — ratified by the owner 2026-07-05). This referee decides whether a trained
candidate's recorded games are STILL a deduction game; it is applied AFTER
training to accept or reject champions and is **NEVER a training reward**.
"Watchability" is a fuzzy, Goodhart-prone scalar (Pan et al. 2022; Skalse et al.
2022) — optimizing it directly is both un-trainable and self-defeating: taken to
its optimum, a learned impostor achieves perfect stealth, produces no flags,
starves meetings of testimony, and the deduction game un-makes itself (§6). So
the optimizer maximizes measurable competence KL-anchored to the scripted FSM
(§4.1); this referee is the held-out gate. Task 15.14 red-teams THIS referee
(runs ES directly on the geomean to surface exploits) before the mid-phase pause
is allowed to trust it — the Goodhart probe is the referee's own acceptance test.

TASK 15.19 REFEREE HARDENING — the doctrine deltas, with
``audits/audit-phase-15-pause.md`` §4 (the per-channel re-verdict) as the
re-verdict of record. The pause adjudicated BOTH probe runs — the 15.14
fake-provider probe (``training/reports/report-goodhart-probe.md``) and the
15.15 surrogate-path re-run (``training/reports/report-impostor-bakeoff.md``
§6, a HELD on a disqualified substrate — held for the wrong structural reason,
expressly NOT read as exploit-caught) — and contracted the patches this module
now implements, landed BEFORE any champion selection leans on fine
D2-conversion differences (the 15.21 re-score and the 15.23 close gate carry
the dependency edge):

  * SELECTION-ONLY — UNCHANGED. The referee remains a post-training champion
    gate and is NEVER a training reward.
  * CONVERSION-COUPLED D2 (the exploited ``kill``/D2-separation channel:
    ``mean_score`` 6.51 → 16.62, +155%, separation 0.20 → 0.84 with conversion
    pinned at 0.00): the D2 separation sub-term is GATED on deduction evidence
    — it counts only when the game converts an observation-backed accusation
    into an ejection or some meeting carries a contradiction flag (VENT-AWARE:
    re-derived flags plus the persisted role-proving ``vent_sighting`` flags
    the re-derivation cannot mint, mirroring the ``flags_per_meeting`` merge).
    Separation without an ejection or a contradiction flag is suspicion
    theater, not deduction, and scores 0 (:func:`_d2_crew_deduction`).
  * SUBJECT-AWARE OBSERVATION BACKING (owner-ratified 2026-07-09,
    ``audits/review-phase-15-midwave.md`` Q2 / §8): an accusation is
    observation-backed only when the accuser's turn carries a first-hand
    structured sighting WHOSE SUBJECT IS THE ACCUSED. Under the pre-15.19
    subject-AGNOSTIC definition a trained impostor could utter a genuine vent
    sighting of X in the turn that accuses innocent Y and have the
    Y-accusation count "backed". The old definition is retained ONLY as the
    frozen ``historical_15_2`` parity mode (so 15.2's cross-implementation
    evidence stays reproducible); it must never gate a champion.
  * ``mean_score`` must NEVER be read without the supply-floor gate. The
    Layer-2 geomean is a fine-grained selection SCORE among candidates that
    already cleared Layer 1 + integrity (``referee_passed``); read alone it is
    Goodhart-able (the 15.14 exploit lived entirely on the bare sub-metric —
    the composed referee rejected every exploiting genome).
  * ADVISORY RARE-EVENT FLOORS (the pause audit §1/§5.1 one-event floor
    degeneracy): a supply floor pinned on a baseline numerator ≤ 1 (today: the
    4p1i ``witnessed_event_rate``, 1/55) is a rare-event gauge a
    same-substrate set can miss by pure variance — it is ADVISORY: reported in
    the JSON (``advisory: true``), excluded from ``supply_floors_passed``
    (:func:`evaluate_supply_floors`).

TASK 16.11 REFEREE RE-ANCHOR — the POPULATION-RELATIVE conversion floor.
Provenance: the owner ruling of 2026-07-11, ``audits/audit-phase-15-close.md``
§10 (the locked close decision this implements) + §11 (the conversion-seam
finding it answers). The Phase-15 close measured the FIRST non-FSM population
ever scored against the hardened floors, and the champion FAILED exactly one
gauge: ``testimony_backed_conversion`` 0.5743 vs 0.6636
(``training/reports/results-champion-close.jsonl``, the committed calibration
fixture). The owner ruled the miss benign, not blocking: the floor was never a
principled constant but the FSM baseline's own measured conversion re-pinned
(71/107), a baseline-relative calibration pin on FSM-driven gameplay — and a
champion that legitimately reshapes gameplay (witnessed kills 5 → 32, vent
exposure 73 → 40) naturally shifts crew-side conversion. The contracted
consequence lands here: the conversion floor stops being another population's
ratio and becomes POPULATION-RELATIVE — derived from the scored population's
own evidence supply, so a candidate is judged on whether its games CONVERT the
testimony they actually contain.

  * THE Q1-PRECEDENT RATIONALE (``audits/review-phase-15-midwave.md`` §8 Q1,
    owner-ratified 2026-07-09; named by the §10 ruling as the instinct this
    re-anchor follows): every absolute number in this project's history moved
    when the population changed (64% → 26%; ceiling 65.1 → 70.6) —
    population-relative bars survive re-records, absolute ones rot. The 15.13
    GO bar was pinned population-relative on all three axes for exactly this
    reason; the referee's one baseline-absolute conversion constant was the
    remaining outlier, and the close's first non-FSM measurement exposed it.
  * THE DERIVATION (:func:`population_relative_conversion_floor`) — what "the
    scored population's own achievable conversion" means, mechanically: a
    resolved meeting ejects at most ONE player, so the conviction throughput
    available for converting backed accusations is bounded PER MEETING, while
    the testimony competing for that single ejection slot scales with the
    population's own per-meeting evidence supply — the referee's own
    ``flags_per_meeting`` gauge, measured on the same bytes under the same
    definitions as the floors. The demanded conversion rate therefore scales
    INVERSELY with the population's measured evidence density, anchored at
    the baseline's equality point::

        floor(pop) = min(1.0, pinned_conversion
                              * (pinned_flags_per_meeting
                                 / measured_flags_per_meeting))

    Equivalently: ``measured_conversion * measured_flags_per_meeting`` must
    reach ``pinned_conversion * pinned_flags_per_meeting`` — the population
    must convert the testimony its games actually contain at least as well,
    per unit of per-meeting evidence supplied, as the baseline converted its
    own.
  * WHY ``flags_per_meeting`` is the density term: it is the referee's one
    per-MEETING evidence-supply gauge (the same denominator the conversion
    gauge's opportunities live in); it is never rare-event degenerate
    (baseline numerators 259/42, vs ``witnessed_event_rate``'s 4p1i 1/55 —
    the 15.19 advisory finding: corpus-4p1i measures 0.0 witnessed while
    PASSING the referee, so a witnessed-driven derivation would spuriously
    demand conversion 1.0 of a set the referee accepts); and it is the
    CONSERVATIVE choice on the calibration fixture (the champion's flags
    multiple is 1.63×, its witnessed multiple 6.76× — the bar relaxes by the
    smaller supply margin).
  * THE STARVATION CATCH STAYS SHARP: a set with zero backed accusations
    measures ``None`` and FAILS the numeric floor regardless of population
    (unchanged); a population supplying LESS per-meeting evidence than the
    baseline faces a HIGHER demanded rate (capped at 1.0) — and already fails
    the ``flags_per_meeting`` floor itself — so the re-anchor can only RELAX
    the bar for populations that clear the supply floors. The FSM baseline
    still passes at EXACT equality: at its own density the supply ratio is
    exactly 1.0 and the derived floor IS the pin (the multiplication order
    ``pin * (pin_flags / measured_flags)`` preserves bit-exact equality).
  * THE CALIBRATION FIXTURE, re-read under the new definition: the champion
    close row records ``flags_per_meeting`` 3.0431654676258995 (423/139) and
    conversion 0.5742574257425742 (58/101); derived floor =
    0.6635514018691588 × (1.8633093525179856 / 3.0431654676258995) =
    0.40628797419411855 < 0.5743 → the conversion gauge PASSES — the owner's
    close-over ruling, now derived rather than ruled. The committed row is
    untouched: its ``referee_passed: false`` stands as the 15.23 instrument's
    verdict under the then-current absolute floor.
  * SCOPE: exactly the one gauge the close contracted forward re-anchors. The
    ``witnessed_event_rate`` and ``flags_per_meeting`` floors keep their
    per-baseline pinned form, the D1-D4 geomean and the integrity floor are
    untouched, and the frozen baseline-2 block stays ABSOLUTE (its bytes left
    the tree at the 15.7 re-record; a historical pin is never re-derived).

TWO LAYERS, both selection-only:

Layer 1 — EVIDENCE-SUPPLY FLOORS (:func:`evaluate_supply_floors`). The sharp,
data-grounded catch for the perfect-stealth failure mode: three set-level gauges,
each with a per-baseline floor. A candidate whose games produce structurally LESS
evidence than the baseline FAILS the referee even when meeting-rate stays high
(bodies still trigger meetings after testimony has died):

  * ``witnessed_event_rate`` — crew-witnessed kills / total kills, recovered from
    the engine ``KilledEvent.witnesses`` on the reconstruction walk (baseline 2:
    6/160 = 3.75% crew-witnessed in 9p2i — the §6 perfect-stealth anchor).
  * ``flags_per_meeting`` — contradiction flags per meeting, wired from
    :func:`eval.meeting_quality.compute_supply_gauges` (``total_flags`` census) and
    made VENT-AWARE: the grounded role-proving ``vent_sighting`` flag (Task 15.4)
    cannot be re-derived from a transcript (its grounding channel carries no
    transcript id), so the persisted vent flags are merged in — else a vent-rich
    candidate's strongest evidence is undercounted (:func:`_persisted_vent_flag_count`).
  * ``testimony_backed_conversion`` — the fraction of (meeting, OBSERVATION-BACKED-
    accused true impostor) pairs the meeting ejected, using the SAME
    evidence-grounded predicate as the geomean's D2 conversion
    (:func:`_observation_backed_impostors` — an accusation whose accuser also
    logged a first-hand sighting OF THE ACCUSED, subject-aware per Task 15.19).
    Deliberately NOT
    ``compute_conversion_report``'s ``impostor_accused_conversion_rate``, which
    counts ANY verbal accusation of a true impostor: a "testimony-BACKED" floor
    that accepts ungrounded vibe-convictions would let a candidate that ejects
    impostors on unbacked accusations clear the evidence floor. Since Task
    16.11 this gauge's evaluated FLOOR is POPULATION-RELATIVE on baseline-3
    (see the re-anchor section above): the pin stays the baseline's measured
    anchor, the demanded rate derives from the scored set's own
    ``flags_per_meeting``.

The floors are PARAMETERIZED PER BASELINE (:data:`_BASELINE_SUPPLY_FLOORS`, keyed
by baseline id then roster; each pin carries its measured value AND its raw
baseline numerator, :class:`FloorPin` — the numerator drives the 15.19 advisory
rare-event rule). Task 15.2 measured + pinned the baseline-2 values; Task 15.7
pinned baseline-3 (the committed canonical default); Task 15.19 RE-PINNED the
baseline-3 blocks under the subject-aware backing definition by re-measuring the
SAME committed bytes (the measured numbers, with the corpus figures alongside per
the Q3 denominator rule, are in the constants block's comments — the baseline-2
block is a frozen historical pin under the pre-15.19 definition, its bytes having
left the tree at the 15.7 re-record). The floors are set FROM the measured
baseline — "do not accept a champion whose games produce structurally less
evidence than the baseline", not "hit a number" — so the baseline itself passes
at equality and any strictly-poorer candidate fails, and candidate + floor are
always measured under the SAME definition. Task 16.11 re-anchored the
baseline-3 conversion floors POPULATION-RELATIVE (``population_relative_conversion``
on :class:`SupplyFloors`): the pinned (value, numerator) stays the baseline's
measured anchor, but the floor the candidate is gated on is derived from the
candidate's own per-meeting evidence supply — equality at the baseline's own
density, by construction.

Layer 2 — the D1-D4 FLOOR-GATED WEIGHTED GEOMEAN (:func:`compute_game_score`),
promoted verbatim from ``rubric_score.py`` (the geomean composition,
:file:`experiments/lab/rubric_score.py:823`; weights :53; report-rubric-design.md
§3). Each dimension in [0,1]; ``score = 100 * floor * geomean_weighted(D1-D4)``:

  * weights {D1 .40, D2 .25, D3 .15, D4 .20}, ε = 1e-3 (:data:`_GEOMEAN_WEIGHTS` /
    :data:`_GEOMEAN_EPSILON`). A weighted GEOMETRIC mean, so ONE dead dimension
    SINKS the score — a live term cannot mask a dead one (the additive-R1-R7 flaw).
    A meeting-starved game collapses to ~0 by construction.
  * ``floor`` ∈ {0, 1} (:func:`_floor_multiplier`) — a hard R4-style integrity gate,
    0 on ANY of: a firewall/determinism breach (``integrity_ok`` False), a
    friendly-fire kill (an impostor victim — engine-forbidden), or a RAILROAD crew
    ejection (:func:`_is_railroad_ejection`: rendered suspicion among the ejectors
    below the §4.6 gate, or an evidence-free conviction with no observation-backed
    accusation and no contradiction flag). Punish-only; never a tradeable dimension.

INTEGRITY BOUNDARY (the referee's ``integrity_ok`` vs the validity gate). The
DOCTRINE (audits/post-phase-14-ML-training-signal.md §3.2/§6) splits the two jobs:
the HARD validity gate (``scripts/validity_gate.py`` / :func:`eval.validity.run_validity_gate`,
Task 15.1) is the AUTHORITATIVE integrity stage and is meant to PASS before a set
reaches this referee. This module's ``integrity_ok`` is a defense-in-depth
self-check that floors the geomean on the tamper vectors the geomean's own inputs
depend on — determinism / pre-hash / post-hash breaches, a forged or missing
``game_over`` label (feeds D1), a missing / duplicate / trailing meeting row and a
ballots-vs-outcome tally mismatch (feed D2/D3/D4/the railroad floor) — and fails
CLOSED on unreadable bytes. It deliberately does NOT re-implement the validity
gate's full check set (tick-1 kills, betrayal ballots, dangling reason ids, cost /
provenance, the meeting-rate floor): those are the gate's remit, run first, not
duplicated here. Run the validity gate for a complete integrity verdict; this
self-check exists so a champion is never SELECTED on bytes that would corrupt its
own score.

The four dimensions (report-rubric-design.md §3; weights/mappings are the lab's
pre-fix calibration. The committed
``experiments/lab/results-rubric-geomean.json`` remains an exact parity fixture
of the FROZEN pre-15.19 spec via ``compute_game_score(..., historical_15_2=True)``
— the 15.2 promotion re-anchored the INPUTS to bytes, not the numeric spec, and
15.19's hardened D2/backing deltas live beside, not instead of, that
reproducible historical pin):

  * D1 resolution — did PLAY decide the board, not the clock? CREWMATE_EJECT → 1.0;
    a contested IMPOSTOR_PARITY/IMPOSTOR_SABOTAGE (≥1 meeting) → 0.6; some impostor
    ejected but the clock decided → 0.3; a stopwatch / pre-meeting stomp → 0.0.
  * D2 crew deduction — ``0.5·separation_norm + 0.5·conversion``. separation =
    game-mean of (mean rendered-suspicion of true impostors − mean of crew) over
    each meeting's ``suspicion_graph_by_voter``, normalized by
    :data:`_D2_SEPARATION_SCALE` = 0.30 and clamped at 0 (a railroad that raises
    suspicion on an innocent LOWERS separation → penalized), then CONVERSION-
    COUPLED (Task 15.19): gated to 0 unless the game converted a backed
    accusation into an ejection or carries a contradiction flag (re-derived, or
    a persisted vent flag — the vent-aware leg). conversion = of every
    (meeting, observation-backed-accused true impostor) pair, the fraction
    ejected (backing subject-aware per Task 15.19).
  * D3 impostor craft — the EFFECTIVE-deflection value (1.0 effective / 0.2
    accused-not-deflected / 0.0 never-accused): a counter-accusation that MOVED the
    eject-plurality off a true impostor. Passivity scores 0 (never rewarded).
  * D4 arc — ``0.45·arc + 0.35·swing + 0.20·contest``: a cross-meeting suspicion
    rise onto a true impostor; a knife-edge ``plurality_margin == 1`` eject whose
    subject's rendered suspicion MOVED across meetings; and ``min(1, (n-1)/2)``.

THE FACTS-EXTRACTION SUBSET INLINED (the hint's "document exactly which subset").
The lab scorer reads the 4392-line audit facts JSON; this module re-derives ONLY
the fields the D1-D4 geomean + floor read, directly from the committed bytes:
per game — ``seed``/``reason``/``roles`` (re-seeded, :func:`eval.validity.roles_by_seed`),
the resolved ``meetings`` (the loaded :class:`~eval.report_schema.TournamentReport`),
kill victim-roles + witnesses + ``integrity_ok`` (the engine reconstruction walk),
and the per-player cross-meeting ``rendered_suspicion`` trajectory; per meeting —
``ejected_player_id``/``ejected_role``, ``suspicion_graph_by_voter`` (parsed from
the vote prompts via :func:`eval.meeting_quality._parse_suspicion_graph`),
``testimony_records`` (accusation/sighting vehicle + the subject-aware
observation-backed bit, plus the frozen subject-agnostic bit for the parity pin),
``accusations``, ``plurality_target``/``plurality_margin`` (the recorded ballot
tally), ``ejected_rendered_suspicion_among_ejectors``, and
``contradictions_by_subject`` (RE-DERIVED via
:func:`meetings.transcript.detect_contradictions` under the ballot-voter roster,
mirroring the extractor's ``_rederive_meeting_contradictions`` — on the committed
set recorded == re-derived, verified by the parity test; on any future set it
reads the CURRENT detector). The extractor's ``GEOMEAN_RESULTS_FILENAME``
machinery and every field the geomean does not read are untouched.

The 9p2i/4p1i asymmetry is handled, not assumed away: the geomean runs on BOTH
committed sets from bytes (4p1i has no committed rubric artifact — the parity
fixture is 9p2i only), and the supply floors are pinned per roster within the
baseline block.

JSON report schema (``WatchabilityReport.model_dump()`` / ``--watchability
--json``) — consumed by the 15.15 bake-off harness and the 15.7 / 15.18 audits,
STABLE::

    {
      "replay_set_dir": str,
      "baseline_id": str,              # the per-baseline floor block used
      "roster_key": str,              # e.g. "9p2i" / "4p1i"
      "games_total": int,
      "integrity_ok": bool,           # every game reconstructed byte-identically
      "referee_passed": bool,         # supply_floors_passed AND integrity_ok
      "supply_floors_passed": bool,   # AND over the NON-advisory gauges
      "supply_gauges": [              # one per Layer-1 gauge, in order
        {"name": str, "measured": float|null, "floor": float, "passed": bool,
         "advisory": bool},           # advisory = baseline numerator <= 1;
        ...                           # excluded from supply_floors_passed.
                                      # Since 16.11 the conversion row's
                                      # "floor" is the DERIVED population-
                                      # relative value on baseline-3 (the pin
                                      # exactly, when scoring the baseline).
      ],
      "mean_score": float, "median_score": float,  # NEVER read without the
                                      # referee_passed / supply-floor gate
      "per_game": [                   # the Layer-2 geomean, desc by score
        {"seed": int, "reason": str, "n_meetings": int,
         "floor_multiplier": float,
         "d1_resolution": float, "d2_deduction": float,
         "d3_craft": float, "d4_arc": float,
         "d2_separation_norm": float, "d2_conversion": float,
         "d4_arc_term": float, "d4_swing_term": float, "d4_contest_term": float,
         "score": float},
        ...
      ]
    }

The library public surface (stable — downstream tasks import these):
:class:`WatchabilityReport`, :func:`compute_watchability`,
:func:`population_relative_conversion_floor` (Task 16.11 — the 16.14/16.17
audits quote its derivation).

Pure + offline: no network, no ``AILIBI_*`` env.
"""

from __future__ import annotations

import math
import statistics
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, NoReturn

from pydantic import BaseModel, ConfigDict, ValidationError

from engine.entities import PlayerId, Role
from engine.events import KilledEvent
from engine.world import Map, load_canonical_map
from eval._suspicion_parse import SKIP_SUSPICION_THRESHOLD
from eval.meeting_quality import (
    _parse_suspicion_graph,
    compute_supply_gauges,
)
from eval.report_schema import GameReport, MeetingReport, TournamentReport
from eval.validity import (
    assemble_tournament_report,
    resolve_roster_knobs,
    roles_by_seed,
    seeds_on_disk,
)
from eval.replay_walk import (
    ReplayWalkConfig,
    TickAdvanced,
    WalkViolation,
    walk_replay,
)
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    FoundBodyObservation,
    MeetingTurn,
    SawPlayerObservation,
    SawVentObservation,
)
from meetings.transcript import detect_contradictions, is_weak_contradiction
from orchestrator.replay import ReplayLog

# --------------------------------------------------------------------------- #
# The geomean composition constants — promoted VERBATIM from the lab scorer    #
# (experiments/lab/rubric_score.py:53 weights, :823 composition;               #
# report-rubric-design.md §3, §8). Kept byte-identical so the committed        #
# results-rubric-geomean.json stays an exact parity fixture of the FROZEN      #
# pre-15.19 spec (compute_game_score(..., historical_15_2=True); the 15.19     #
# hardening changed the D2 term's gating, not these constants).                #
# --------------------------------------------------------------------------- #
_GEOMEAN_WEIGHTS: Final[Mapping[str, float]] = {
    "d1": 0.40,
    "d2": 0.25,
    "d3": 0.15,
    "d4": 0.20,
}
_GEOMEAN_EPSILON: Final[float] = 1e-3
# The §4.6 vote gate (DESIGN.md §4.6): a CREWMATE ejected with rendered suspicion
# below it (the anti-railroad tally bypassed) is a RAILROAD floor. Imported from
# the single eval home so the referee and the SKIP-partition census share it.
_RAILROAD_GATE: Final[float] = SKIP_SUSPICION_THRESHOLD
# Suspicion-separation [0,1] normalizer: a per-meeting mean-impostor-minus-mean-crew
# rendered suspicion of >= this maps to 1.0 (committed max ~0.42; a clean +0.30
# separation is a decisively truth-tracking table). report-rubric-design.md §8.
_D2_SEPARATION_SCALE: Final[float] = 0.30

# Malformed-candidate errors that must FAIL CLOSED (integrity_ok=False) rather
# than escape as a traceback — the referee is a machine-readable bake-off gate
# (``scripts/measure_baseline.py --watchability --json``), so one corrupt
# candidate must produce a failing report, not abort the run. Mirrors
# ``eval.validity._MALFORMED_INPUT_ERRORS``.
_MALFORMED_INPUT_ERRORS: Final[tuple[type[Exception], ...]] = (
    ReplayLog.CorruptedFileError,
    ValidationError,
    ValueError,
    KeyError,
    FileNotFoundError,
)


# --------------------------------------------------------------------------- #
# Layer 1 — evidence-supply floors (per baseline, per roster).                 #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class FloorPin:
    """One pinned supply floor: the measured baseline value + its raw numerator.

    ``value`` is the MEASURED baseline gauge pinned as the floor; ``numerator``
    is the raw baseline event count behind it (crew-witnessed kills / total
    flags / converted backed accusations — the measurement is recorded in the
    constants block's comments). The numerator carries the Task-15.19 ADVISORY
    RARE-EVENT rule (audits/audit-phase-15-pause.md §1/§5.1): a floor pinned on
    a numerator ≤ 1 is a rare-event gauge a same-substrate set can miss by pure
    variance, so it is ADVISORY — reported, never referee-failing
    (:func:`evaluate_supply_floors`).
    """

    value: float
    numerator: int


@dataclass(frozen=True)
class SupplyFloors:
    """The three evidence-supply floors for one (baseline, roster) (Layer 1).

    Each field pins the MEASURED baseline value as the floor: a candidate's
    gauge must be ``>= floor.value`` to clear it, so the baseline itself passes
    at equality and any strictly-poorer set fails. ``testimony_backed_conversion``
    may be ``None`` when the baseline supplies no accused-impostor meeting (the
    undefined-not-zero convention); a ``None`` floor is vacuously cleared. A
    floor whose baseline ``numerator`` is ≤ 1 is advisory (:class:`FloorPin`).

    ``population_relative_conversion`` (Task 16.11 — the close audit §10 owner
    ruling, 2026-07-11) switches the conversion gauge's EVALUATED floor from
    the pin's absolute value to the population-relative derivation
    (:func:`population_relative_conversion_floor`): the pin stays the
    baseline's measured ``(value, numerator)`` anchor — it still drives the
    advisory rare-event rule and the derivation's equality point — but the
    floor a candidate is gated on derives from the candidate's OWN measured
    ``flags_per_meeting``. ``False`` (absolute) on the frozen baseline-2 block:
    its bytes left the tree, so the historical pin is never re-derived.
    """

    witnessed_event_rate: FloorPin
    flags_per_meeting: FloorPin
    testimony_backed_conversion: FloorPin | None
    population_relative_conversion: bool = False


def population_relative_conversion_floor(
    *,
    pinned_conversion: float,
    pinned_flags_per_meeting: float,
    measured_flags_per_meeting: float | None,
) -> float:
    """The Task-16.11 population-relative ``testimony_backed_conversion`` floor.

    THE DERIVATION (the quotable form — the 16.14/16.17 audits print this).
    A resolved meeting ejects at most ONE player, so the conviction throughput
    available for converting backed accusations is bounded per meeting, while
    the testimony competing for that single ejection slot scales with the
    scored population's own per-meeting evidence supply (its measured
    ``flags_per_meeting`` — the referee's one per-MEETING evidence-supply
    gauge). The demanded conversion rate therefore scales INVERSELY with the
    population's own evidence density, anchored so the baseline's density
    demands exactly the baseline's own measured conversion::

        floor = min(1.0, pinned_conversion
                         * (pinned_flags_per_meeting
                            / measured_flags_per_meeting))

    Equivalently, the bar preserves the baseline's conversion-per-unit-of-
    supplied-evidence: ``measured_conversion * measured_flags_per_meeting``
    must reach ``pinned_conversion * pinned_flags_per_meeting`` — the
    population is judged on whether its games CONVERT the testimony they
    actually contain, not on whether they reproduce another population's
    ratio (close audit §10; the Q1 population-relative precedent).

    Properties, by construction:

    * EQUALITY SELF-CONSISTENCY — at the baseline's own density the ratio is
      exactly ``1.0`` and the floor IS the pin, bit-exact (the multiplication
      order ``pin * (pin_flags / measured_flags)`` is deliberate: it keeps
      "the baseline passes at equality" an exact float identity).
    * STARVATION STAYS SHARP — a population with LESS per-meeting evidence
      than the baseline faces a HIGHER demanded rate, capped at ``1.0``; a
      population with no per-meeting evidence at all (``None`` — no meetings —
      or ``0.0`` flags) faces the maximal demand ``1.0``. A set with zero
      backed accusations measures ``None`` on the conversion gauge and fails
      the numeric floor regardless (:func:`evaluate_supply_floors`).
    * RELAX-ONLY ABOVE THE SUPPLY FLOOR — the derived floor drops below the
      pin only when the population's flags density EXCEEDS the baseline's,
      i.e. only for sets that already clear the ``flags_per_meeting`` floor
      with margin; an evidence-poorer set is gated HARDER than under the
      retired absolute constant.

    Pure: a function of the pinned anchor and the measured supply, no I/O.
    Raises :class:`ValueError` on a degenerate pin (no silent fallbacks — an
    un-measurable anchor must not gate a champion).
    """

    if not 0.0 < pinned_conversion <= 1.0:
        raise ValueError(
            "pinned_conversion must be a measured rate in (0, 1], got "
            f"{pinned_conversion!r}"
        )
    if pinned_flags_per_meeting <= 0.0:
        raise ValueError(
            "pinned_flags_per_meeting must be a positive measured density, got "
            f"{pinned_flags_per_meeting!r}"
        )
    if measured_flags_per_meeting is None or measured_flags_per_meeting <= 0.0:
        return 1.0
    return min(
        1.0,
        pinned_conversion * (pinned_flags_per_meeting / measured_flags_per_meeting),
    )


# The per-baseline supply-floor block, read by baseline id then roster key. The
# floors are the baseline's OWN measured supply (each pin carries the measured
# value + the raw numerator behind it), so the baseline passes at equality and a
# candidate that produces structurally less evidence (the perfect-stealth
# failure mode) fails. Task 15.2 pinned baseline-2; Task 15.7 pinned baseline-3;
# Task 15.19 RE-PINNED the baseline-3 blocks under the SUBJECT-AWARE backing
# definition on the same committed bytes (only the conversion gauge's definition
# changed; witnessed kills + flags are backing-independent). Task 16.11
# re-anchored the baseline-3 conversion floors POPULATION-RELATIVE (close audit
# §10, owner 2026-07-11): the conversion pins below stay the baseline's
# measured anchors, but the floor a scored set is gated on is derived from its
# OWN flags_per_meeting via population_relative_conversion_floor().
_BASELINE_SUPPLY_FLOORS: Final[Mapping[str, Mapping[str, SupplyFloors]]] = {
    # FROZEN HISTORICAL PIN (Task 15.19): the baseline-2 bytes left the tree at
    # the 15.7 re-record, so this block CANNOT be re-measured and stays pinned
    # under the pre-15.19 subject-AGNOSTIC backing definition. A candidate
    # (measured subject-aware, hence never higher than subject-agnostic) scored
    # against these floors faces a strictly conservative conversion gate; new
    # champions are gated by the canonical baseline-3 block below.
    "baseline-2": {
        # Measured on replays/samples/9p2i (baseline 2, Qwen/Qwen3-32B qwen3_32b.v4;
        # the values are the baseline's OWN supply, so it passes at equality):
        #   witnessed_event_rate        = 6/160  = 0.0375 (crew-witnessed kills; §6)
        #   flags_per_meeting           = 285/142 = 2.007042253521127
        #   testimony_backed_conversion = 56/128 = 0.4375 (OBSERVATION-BACKED,
        #                                 pre-15.19 subject-agnostic)
        "9p2i": SupplyFloors(
            witnessed_event_rate=FloorPin(value=0.0375, numerator=6),
            flags_per_meeting=FloorPin(value=2.007042253521127, numerator=285),
            testimony_backed_conversion=FloorPin(value=0.4375, numerator=56),
        ),
        # Measured on replays/samples/4p1i (the flat determinism/leak reference —
        # 4 players, 1 impostor, short games; supply is naturally sparse):
        #   witnessed_event_rate        = 1/64  = 0.015625 (numerator 1 -> ADVISORY)
        #   flags_per_meeting           = 29/39 = 0.7435897435897436
        #   testimony_backed_conversion = 12/37 = 0.32432432432432434 (OBSERVATION-
        #                                 BACKED, pre-15.19 subject-agnostic)
        "4p1i": SupplyFloors(
            witnessed_event_rate=FloorPin(value=0.015625, numerator=1),
            flags_per_meeting=FloorPin(value=0.7435897435897436, numerator=29),
            testimony_backed_conversion=FloorPin(
                value=0.32432432432432434, numerator=12
            ),
        ),
    },
    # Task 15.7 baseline-3 record (Qwen/Qwen3-32B, qwen3_32b.v5 + vote_ballot v6,
    # the 6-lever Wave-0 substrate), RE-PINNED by Task 15.19 under the
    # subject-aware backing definition on the SAME committed bytes (baseline-3
    # samples; the ml_corpus figures reported alongside per the midwave Q3
    # denominator rule — the corpus is measured AGAINST these floors, never
    # pinned as them; the 50-seed samples remain the byte-identity anchor).
    # Finding at the 15.19 re-pin: the subject-aware predicate SHRANK the
    # backed-pair pool as expected (9p2i attempted 117 -> 107; 4p1i 35 -> 33)
    # but the conversion RATE nudged UP, not down (9p2i 71/117=0.6068 ->
    # 71/107=0.6636; 4p1i 21/35=0.6000 -> 20/33=0.6061): the accusations that
    # lost their backing were disproportionately the NON-converted ones. A
    # direction, not a failure — candidate and baseline are measured under the
    # same definition, so the relative gate stays sound (Phase-14 doctrine:
    # directions are findings, not pass bars).
    "baseline-3": {
        # Measured on replays/samples/9p2i (baseline 3, re-measured at 15.19
        # with the committed CLIs; corpus-9p2i alongside per the Q3 rule):
        #   witnessed_event_rate        = 5/154  = 0.032467532467532464 (crew-witnessed
        #                                 kills; §6)     [corpus: 16/470 = 0.0340]
        #   flags_per_meeting           = 259/139 = 1.8633093525179856
        #                                                [corpus: 948/440 = 2.1545]
        #   testimony_backed_conversion = 71/107 = 0.6635514018691588 (OBSERVATION-
        #                                 BACKED, SUBJECT-AWARE; was 71/117 = 0.6068
        #                                 subject-agnostic)
        #                                                [corpus: 235/331 = 0.7100]
        # TASK 16.11 RE-ANCHOR (population_relative_conversion=True): the
        # conversion pin above stays the measured 71/107 ANCHOR; the evaluated
        # floor is derived per scored population:
        #   floor = 0.6635514018691588 * (1.8633093525179856 / measured
        #           flags_per_meeting), capped at 1.0.
        # Existing sets re-measured at 16.11 under the derivation (committed
        # CLIs on this checkout; every verdict matches the close audit §1/§3):
        #   samples 9p2i (the baseline itself): flags 259/139 -> ratio exactly
        #     1.0 -> derived floor = pin = 0.6635514018691588; measured
        #     71/107 -> PASS at exact equality (self-consistency).
        #   corpus 9p2i: flags 948/440 = 2.1545454545454548 -> derived
        #     0.5738572515937326; measured 235/331 = 0.7100 -> PASS (was PASS
        #     under the absolute pin too).
        #   champion-close fixture (results-champion-close.jsonl, the §10
        #     calibration row): flags 423/139 = 3.0431654676258995 -> derived
        #     0.40628797419411855; measured 58/101 = 0.5742574257425742 ->
        #     PASS — the owner's close-over ruling, now derived (the recorded
        #     FAIL vs the absolute 0.6636 stands in the committed row as the
        #     15.23 instrument's verdict).
        "9p2i": SupplyFloors(
            witnessed_event_rate=FloorPin(value=0.032467532467532464, numerator=5),
            flags_per_meeting=FloorPin(value=1.8633093525179856, numerator=259),
            testimony_backed_conversion=FloorPin(
                value=0.6635514018691588, numerator=71
            ),
            population_relative_conversion=True,
        ),
        # Measured on replays/samples/4p1i (baseline 3, re-measured at 15.19
        # with the committed CLIs; corpus-4p1i alongside per the Q3 rule):
        #   witnessed_event_rate        = 1/55  = 0.01818181818181818 (numerator 1
        #                                 -> ADVISORY, the pause-audit §1/§5.1
        #                                 one-event floor degeneracy)
        #                                                [corpus: 0/46 = 0.0]
        #   flags_per_meeting           = 42/39 = 1.0769230769230769 (the raw
        #                                 census incl. 11 persisted vent flags;
        #                                 15.7 recorded the reduced form 14/13)
        #                                                [corpus: 60/40 = 1.5]
        #   testimony_backed_conversion = 20/33 = 0.6060606060606061 (OBSERVATION-
        #                                 BACKED, SUBJECT-AWARE; was 21/35 = 0.6
        #                                 subject-agnostic — 15.7 recorded the
        #                                 reduced form 3/5)
        #                                                [corpus: 26/36 = 0.7222]
        # TASK 16.11 RE-ANCHOR (population_relative_conversion=True — same
        # derivation, this roster's pins):
        #   floor = 0.6060606060606061 * (1.0769230769230769 / measured
        #           flags_per_meeting), capped at 1.0.
        # Existing sets re-measured at 16.11:
        #   samples 4p1i (the baseline itself): flags 42/39 -> ratio exactly
        #     1.0 -> derived floor = pin = 0.6060606060606061; measured
        #     20/33 -> PASS at exact equality (self-consistency).
        #   corpus 4p1i: flags 60/40 = 1.5 -> derived 0.43512043512043513;
        #     measured 26/36 = 0.7222 -> PASS (the witnessed miss stays
        #     advisory per 15.19 — and is deliberately NOT a derivation input,
        #     see the module docstring's density-term rationale).
        "4p1i": SupplyFloors(
            witnessed_event_rate=FloorPin(value=0.01818181818181818, numerator=1),
            flags_per_meeting=FloorPin(value=1.0769230769230769, numerator=42),
            testimony_backed_conversion=FloorPin(
                value=0.6060606060606061, numerator=20
            ),
            population_relative_conversion=True,
        ),
    },
    # Task 16.14 baseline-4 record (Qwen/Qwen3.6-27B, the qwen3_6_27b v1 set,
    # the same 6-retired-lever substrate — the model/set as the ONLY layer
    # change), pinned under the 16.11 population-relative definition from the
    # committed bytes. NO corpus figures accompany these pins: the ml_corpus is
    # baseline-3/Qwen3-32B substrate and is STALE from this record on (the
    # DEGRADED-Q3 rule — the corpus may be quoted as stale context only, never
    # measured against these floors as same-substrate evidence).
    # Finding at the pin (audits/audit-phase-16-baseline-4.md §4): the bespoke
    # set's impostor profile emits near-zero structured alibi material (alibi
    # claims 281 -> 109; alibi_vs_* transcript flags 190 -> 7, all
    # crew-subject), so flags_per_meeting drops ~3.5x and is now vent-dominated
    # (79 of 86 flags) — while the SIGHTING-backed conversion the referee
    # actually gates barely moves (0.664 -> 0.626) and the witnessed-kill
    # supply RISES. The 16.11 derivation makes the conversion floor
    # density-aware, so an evidence-starved candidate still faces a sharpened
    # demand rather than a free pass.
    "baseline-4": {
        # Measured on replays/samples/9p2i (baseline 4, this record, via the
        # committed CLIs / the compute_watchability gauge seam):
        #   witnessed_event_rate        = 9/178  = 0.05056179775280899
        #   flags_per_meeting           = 86/160 = 0.5375 (79 persisted vent
        #                                 flags + 7 re-derived transcript flags)
        #   testimony_backed_conversion = 77/123 = 0.6260162601626016
        #                                 (OBSERVATION-BACKED, SUBJECT-AWARE)
        # TASK 16.11 derivation (population_relative_conversion=True): the
        # evaluated floor per scored population is
        #   floor = 0.6260162601626016 * (0.5375 / measured flags_per_meeting),
        #   capped at 1.0.
        # The baseline itself: flags 86/160 -> ratio exactly 1.0 -> derived
        # floor = pin = 0.6260162601626016; measured 77/123 -> PASS at exact
        # equality (self-consistency).
        "9p2i": SupplyFloors(
            witnessed_event_rate=FloorPin(value=0.05056179775280899, numerator=9),
            flags_per_meeting=FloorPin(value=0.5375, numerator=86),
            testimony_backed_conversion=FloorPin(
                value=0.6260162601626016, numerator=77
            ),
            population_relative_conversion=True,
        ),
        # Measured on replays/samples/4p1i (baseline 4, this record):
        #   witnessed_event_rate        = 1/58  = 0.017241379310344827
        #                                 (numerator 1 -> ADVISORY, the 15.19
        #                                 rare-event rule)
        #   flags_per_meeting           = 11/39 = 0.28205128205128205 (all 11
        #                                 persisted vent flags; the transcript
        #                                 census re-derives ZERO on this set)
        #   testimony_backed_conversion = 17/29 = 0.5862068965517241
        #                                 (OBSERVATION-BACKED, SUBJECT-AWARE)
        # TASK 16.11 derivation (same shape, this roster's pins):
        #   floor = 0.5862068965517241 * (0.28205128205128205 / measured
        #           flags_per_meeting), capped at 1.0.
        # The baseline itself: flags 11/39 -> ratio exactly 1.0 -> derived
        # floor = pin = 0.5862068965517241; measured 17/29 -> PASS at exact
        # equality (self-consistency).
        "4p1i": SupplyFloors(
            witnessed_event_rate=FloorPin(value=0.017241379310344827, numerator=1),
            flags_per_meeting=FloorPin(value=0.28205128205128205, numerator=11),
            testimony_backed_conversion=FloorPin(
                value=0.5862068965517241, numerator=17
            ),
            population_relative_conversion=True,
        ),
    },
    "baseline-5": {
        # Measured on replays/samples/9p2i (baseline 5, the Task-16.17 close
        # record: locked model + qwen3_6_27b v3 + the graduated slate — J1,
        # id-rendering, citation gate unconditional; absence_prior OFF), via
        # the committed CLIs / the compute_watchability gauge seam:
        #   witnessed_event_rate        = 7/203  = 0.034482758620689655
        #   flags_per_meeting           = 90/179 = 0.5027932960893855 (75
        #                                 persisted vent flags + 15 re-derived
        #                                 transcript flags)
        #   testimony_backed_conversion = 64/135 = 0.4740740740740741
        #                                 (OBSERVATION-BACKED, SUBJECT-AWARE)
        # TASK 16.11 derivation (population_relative_conversion=True): the
        # evaluated floor per scored population is
        #   floor = 0.4740740740740741 * (0.5027932960893855 / measured
        #           flags_per_meeting), capped at 1.0.
        # The baseline itself: flags 90/179 -> ratio exactly 1.0 -> derived
        # floor = pin = 0.4740740740740741; measured 64/135 -> PASS at exact
        # equality (self-consistency). The conversion drop vs baseline 4
        # (77/123 = 0.6260 -> 0.4741) is the graduated judgment layer working
        # as designed — J1 clamps conviction-grade soft-only renders sub-gate
        # and J2 coerces uncited zero-flag EJECTs — so convictions demand
        # cited evidence (audits/audit-phase-16-close.md §5 quotes this
        # derivation and the direction read).
        "9p2i": SupplyFloors(
            witnessed_event_rate=FloorPin(value=0.034482758620689655, numerator=7),
            flags_per_meeting=FloorPin(value=0.5027932960893855, numerator=90),
            testimony_backed_conversion=FloorPin(
                value=0.4740740740740741, numerator=64
            ),
            population_relative_conversion=True,
        ),
        # Measured on replays/samples/4p1i (baseline 5, this record):
        #   witnessed_event_rate        = 1/61  = 0.01639344262295082
        #                                 (numerator 1 -> ADVISORY, the 15.19
        #                                 rare-event rule)
        #   flags_per_meeting           = 16/39 = 0.41025641025641024 (11
        #                                 persisted vent flags + 5 re-derived
        #                                 transcript flags)
        #   testimony_backed_conversion = 10/28 = 0.35714285714285715
        #                                 (OBSERVATION-BACKED, SUBJECT-AWARE)
        # TASK 16.11 derivation (same shape, this roster's pins):
        #   floor = 0.35714285714285715 * (0.41025641025641024 / measured
        #           flags_per_meeting), capped at 1.0.
        # The baseline itself: flags 16/39 -> ratio exactly 1.0 -> derived
        # floor = pin = 0.35714285714285715; measured 10/28 -> PASS at exact
        # equality (self-consistency).
        "4p1i": SupplyFloors(
            witnessed_event_rate=FloorPin(value=0.01639344262295082, numerator=1),
            flags_per_meeting=FloorPin(value=0.41025641025641024, numerator=16),
            testimony_backed_conversion=FloorPin(
                value=0.35714285714285715, numerator=10
            ),
            population_relative_conversion=True,
        ),
    },
    "baseline-6": {
        # Measured on replays/samples/9p2i (baseline 6, the Task-18.12 adopting
        # record: locked model + qwen3_6_27b v3 + the meeting-layer graduation slate
        # — roll_call_round, whereabouts_interior_flags, vent_placement_contradictions,
        # absence_prior all unconditional beside the earlier graduations, PLUS the
        # 17.5 vent-placement WIDENING wired into the absent-set fold (Codex P1 fix,
        # PR #300); impostor_roll_call OFF, the CREW-ONLY ruling), via the
        # compute_watchability gauge seam:
        #   witnessed_event_rate        = 6/177  = 0.03389830508474576
        #   flags_per_meeting           = 180/165 = 1.0909090909090908 (96
        #                                 persisted vent flags + 84 re-derived
        #                                 transcript flags)
        #   testimony_backed_conversion = 78/136 = 0.5735294117647058
        #                                 (OBSERVATION-BACKED, SUBJECT-AWARE)
        # TASK 16.11 derivation (population_relative_conversion=True): the
        # evaluated floor per scored population is
        #   floor = 0.5735294117647058 * (1.0909090909090908 / measured
        #           flags_per_meeting), capped at 1.0.
        # The baseline itself: flags 180/165 -> ratio exactly 1.0 -> derived
        # floor = pin = 0.5735294117647058; measured 78/136 -> PASS at exact
        # equality (self-consistency). The flag census still rises sharply vs
        # baseline 5 (90/179 = 0.5028 -> 180/165 = 1.0909) — the graduated meeting
        # layer working as designed (the roll-call round elicits whereabouts answers
        # the endpoint-band exemption bands STRONG, and the vent variant mints
        # grounded-vent STRONG flags) — so evidence supply rises with the conviction
        # rate (64/135 = 0.4741 -> 78/136 = 0.5735). The vent WIDENING re-record
        # (removing grounded-vent subjects from the absent set so the absence prior
        # no longer double-charges them) shifted the game trajectories — meetings
        # 156 -> 165, flags 207 -> 180, kills 173 -> 177 — the honest cascade of a
        # corrected substrate. audits/audit-phase-18-baseline-6.md §5 quotes this.
        "9p2i": SupplyFloors(
            witnessed_event_rate=FloorPin(value=0.03389830508474576, numerator=6),
            flags_per_meeting=FloorPin(value=1.0909090909090908, numerator=180),
            testimony_backed_conversion=FloorPin(
                value=0.5735294117647058, numerator=78
            ),
            population_relative_conversion=True,
        ),
        # Measured on replays/samples/4p1i (baseline 6, this record):
        #   witnessed_event_rate        = 1/61  = 0.01639344262295082
        #                                 (numerator 1 -> ADVISORY, the 15.19
        #                                 rare-event rule)
        #   flags_per_meeting           = 16/39 = 0.41025641025641024 (11
        #                                 persisted vent flags + 5 re-derived
        #                                 transcript flags)
        #   testimony_backed_conversion = 9/30 = 0.3
        #                                 (OBSERVATION-BACKED, SUBJECT-AWARE)
        # TASK 16.11 derivation (same shape, this roster's pins):
        #   floor = 0.3 * (0.41025641025641024 / measured flags_per_meeting),
        #           capped at 1.0.
        # The baseline itself: flags 16/39 -> ratio exactly 1.0 -> derived
        # floor = pin = 0.3; measured 9/30 -> PASS at exact equality
        # (self-consistency). The 4p1i witnessed + flag censuses are unchanged from
        # the pre-widening cut (the small 4p1i games elicit no new roll-call/vent
        # flags and the widening removes no absent-set subject that flips an
        # outcome); the conversion floor eases by one converted attempt (10/30 ->
        # 9/30) as the widening's absence-prior change nudges one backed accusation.
        "4p1i": SupplyFloors(
            witnessed_event_rate=FloorPin(value=0.01639344262295082, numerator=1),
            flags_per_meeting=FloorPin(value=0.41025641025641024, numerator=16),
            testimony_backed_conversion=FloorPin(value=0.3, numerator=9),
            population_relative_conversion=True,
        ),
    },
}

# baseline 6 is the committed canonical SAMPLES set since Task 18.12 (the
# meeting-layer adopting record on the graduated slate), so a bare
# ``measure_baseline.py --watchability`` reads baseline 6's own floors — the
# referee accepts the committed bytes at equality. (Baselines 3, 4, and 5 moved
# here from Tasks 15.7, 16.14, and 16.17 the same way; their blocks above stay
# scoreable via an explicit --baseline-id.) NOTE the bake-off lag REOPENS at this
# record: ``BAKEOFF_BASELINE_ID`` (training/bakeoff/harness.py) stays
# ``baseline-5`` until Task 18.14 flips it, so the training-side selection floors
# deliberately lag this default until the surrogate re-ground
# (audits/audit-phase-18-baseline-6.md §8; the corpus canary denominator is
# restored at the 18.13 corpus re-record).
_DEFAULT_BASELINE_ID: Final[str] = "baseline-6"


@dataclass(frozen=True)
class SupplyGaugeValues:
    """The three measured Layer-1 gauges over a replay set (pre-floor).

    ``testimony_backed_conversion`` is the fraction of (meeting, OBSERVATION-BACKED-
    accused true impostor) pairs the meeting EJECTED — the SAME evidence-grounded
    predicate the geomean's D2 conversion uses (a turn whose accuser also logged a
    first-hand sighting OF THE ACCUSED — subject-aware, Task 15.19), NOT any
    verbal accusation. It is ``None`` when no meeting carried an
    observation-backed accusation of a true impostor (undefined, not 0.0).
    ``witnessed_event_rate`` is ``None`` when the set recorded zero kills.
    """

    witnessed_event_rate: float | None
    total_kills: int
    crew_witnessed_kills: int
    flags_per_meeting: float | None
    total_flags: int
    persisted_vent_flags: int
    meetings_total: int
    testimony_backed_conversion: float | None
    backed_conversion_attempted: int
    backed_conversion_converted: int


class SupplyFloorGauge(BaseModel):
    """One Layer-1 gauge's measured value + floor + pass verdict (frozen).

    ``advisory`` marks the Task-15.19 rare-event rule: the pin's baseline
    numerator is ≤ 1, so the row still reports the honest measured-vs-floor
    ``passed`` verdict but is EXCLUDED from the set-level
    ``supply_floors_passed`` (it can never fail the referee on its own). The
    field defaults to ``False`` so pre-15.19 serialized reports still validate.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    measured: float | None
    floor: float | None
    passed: bool
    advisory: bool = False


def evaluate_supply_floors(
    gauges: SupplyGaugeValues, floors: SupplyFloors
) -> tuple[bool, tuple[SupplyFloorGauge, ...]]:
    """Gate the measured gauges against a (baseline, roster) floor set.

    A gauge clears when its measured value is ``>= floor``. A ``None`` measured
    value FAILS a numeric floor (starvation is not a pass — an evidence-starved
    candidate with zero kills/meetings must not slip through), except that a
    ``None`` conversion floor (the baseline itself supplied no accused-impostor
    meeting) is vacuously cleared. The set-level ``passed`` is the AND over the
    NON-ADVISORY gauges — the referee's Layer-1 verdict.

    ADVISORY RARE-EVENT FLOORS (Task 15.19; audits/audit-phase-15-pause.md
    §1/§5.1): a floor pinned on a baseline numerator ≤ 1 (today: the 4p1i
    ``witnessed_event_rate``, 1/55) is a rare-event gauge that a same-substrate
    set can miss by pure variance — the corpus-4p1i set measures 0.0 on it while
    passing the hard validity gate and every other floor. Such a floor is marked
    ``advisory``: its row keeps the honest measured-vs-floor verdict for the
    report, but it is EXCLUDED from the set-level AND, so it is reported, never
    referee-failing.

    POPULATION-RELATIVE CONVERSION (Task 16.11; close audit §10): when the
    floor block carries ``population_relative_conversion``, the conversion
    gauge is gated on :func:`population_relative_conversion_floor` — derived
    from the CANDIDATE's own measured ``flags_per_meeting`` against the pinned
    baseline anchor — and the gauge row reports that DERIVED floor (exactly
    the pin when the scored set is the baseline itself). The advisory rule
    still reads the pin's baseline numerator; a ``None`` measured conversion
    (zero backed accusations — the starvation catch) still fails the derived
    floor regardless of the population's supply.
    """

    gauge_specs: tuple[tuple[str, float | None, FloorPin | None], ...] = (
        (
            "witnessed_event_rate",
            gauges.witnessed_event_rate,
            floors.witnessed_event_rate,
        ),
        ("flags_per_meeting", gauges.flags_per_meeting, floors.flags_per_meeting),
        (
            "testimony_backed_conversion",
            gauges.testimony_backed_conversion,
            floors.testimony_backed_conversion,
        ),
    )
    results: list[SupplyFloorGauge] = []
    for name, measured, pin in gauge_specs:
        advisory = pin is not None and pin.numerator <= 1
        floor_value: float | None = None if pin is None else pin.value
        if (
            pin is not None
            and name == "testimony_backed_conversion"
            and floors.population_relative_conversion
        ):
            floor_value = population_relative_conversion_floor(
                pinned_conversion=pin.value,
                pinned_flags_per_meeting=floors.flags_per_meeting.value,
                measured_flags_per_meeting=gauges.flags_per_meeting,
            )
        if floor_value is None:
            passed = True
        elif measured is None:
            passed = False
        else:
            passed = measured >= floor_value
        results.append(
            SupplyFloorGauge(
                name=name,
                measured=measured,
                floor=floor_value,
                passed=passed,
                advisory=advisory,
            )
        )
    return all(gauge.passed for gauge in results if not gauge.advisory), tuple(results)


# --------------------------------------------------------------------------- #
# Typed per-game facts (the inlined facts-extraction subset).                  #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class _TrajectoryPoint:
    """One point of a player's cross-meeting rendered-suspicion trajectory."""

    meeting_index: int
    rendered_suspicion: float
    ejected_here: bool


@dataclass(frozen=True)
class _TestimonyTurn:
    """How one turn names an accused subject (vehicle + observation-backed bits).

    ``observation_backed`` is the LIVE subject-aware bit (Task 15.19): the turn
    carries a first-hand structured sighting whose subject IS this record's
    accused. ``observation_backed_any`` is the FROZEN pre-15.19
    subject-AGNOSTIC bit (ANY grounded observation in the turn) — retained ONLY
    for the 15.2 historical geomean-parity pin, never for live scoring.
    """

    vehicle: str | None
    observation_backed: bool
    observation_backed_any: bool


@dataclass(frozen=True)
class _TestimonyRecord:
    """One verbally-accused living subject's testimony record (D2 conversion)."""

    subject: PlayerId
    subject_role: Role | None
    testimony_turns: tuple[_TestimonyTurn, ...]


@dataclass(frozen=True)
class _Accusation:
    """A single (speaker, accused) accusation edge (D3 effective deflection)."""

    speaker: PlayerId
    accused: PlayerId


@dataclass(frozen=True)
class _MeetingFacts:
    """The geomean/floor inputs for one resolved meeting (typed subset).

    ``contradictions_by_subject`` is the RE-DERIVED transcript census (the
    parity-mandated source the railroad floor reads); it can NEVER contain the
    grounded role-proving ``vent_sighting`` flag (its grounding channel is not
    in the transcript, Task 15.4), so the PERSISTED vent flags are carried
    separately in ``persisted_vent_flags`` for the vent-aware consumers (the
    15.19 D2 deduction-evidence gate, mirroring the ``flags_per_meeting``
    merge).
    """

    meeting_index: int
    ejected_player_id: PlayerId | None
    ejected_role: Role | None
    suspicion_graph_by_voter: Mapping[PlayerId, Mapping[PlayerId, float]]
    rendered_suspicion_by_target: Mapping[PlayerId, float]
    testimony_records: tuple[_TestimonyRecord, ...]
    accusations: tuple[_Accusation, ...]
    plurality_target: PlayerId | None
    plurality_margin: int
    ejected_rendered_suspicion_among_ejectors: float | None
    contradictions_by_subject: Mapping[PlayerId, tuple[bool, ...]]
    persisted_vent_flags: int = 0


@dataclass(frozen=True)
class _GameFacts:
    """The geomean/floor inputs for one game (typed subset), plus integrity."""

    seed: int
    reason: str
    roles: Mapping[PlayerId, Role]
    meetings: tuple[_MeetingFacts, ...]
    kill_victim_roles: tuple[Role | None, ...]
    trajectories: Mapping[PlayerId, tuple[_TrajectoryPoint, ...]]
    integrity_ok: bool = True


# --------------------------------------------------------------------------- #
# Reconstruction walk — kills (+witnesses) + integrity (mirrors validity).     #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class _KillWitnessFact:
    """One resolved kill recovered from reconstruction: victim role + witnesses."""

    seed: int
    victim_role: Role | None
    crew_witnessed: bool


@dataclass
class _SetReconstruction:
    """Engine-reconstruction facts over a whole set (kills + integrity)."""

    kills: list[_KillWitnessFact] = field(default_factory=list)
    integrity_ok: bool = True


def _reconstruct_kills(sample_dir: Path) -> _SetReconstruction:
    """Re-seed + replay every game to recover kill witnesses + the integrity flag.

    Mirrors the read-only playback in :func:`eval.validity._reconstruct_game`,
    but collects each :class:`~engine.events.KilledEvent`'s crew-witness status
    (``KilledEvent.witnesses`` filtered to CREWMATE roles — the witnessed-event
    supply gauge) rather than the kill split. An integrity breach — a recorded
    ``state_hash`` that does not reconstruct, OR a game that reached a meeting with
    no recorded meeting row (a truncated / crashed-mid-meeting replay) — flips
    ``integrity_ok`` (the geomean floor then zeroes EVERY game in the set) instead
    of raising, so a drifted / truncated candidate is REJECTED, never crashes or
    silently certifies the referee.
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
    result = _SetReconstruction()
    for seed in seeds_on_disk(sample_dir):
        roles = per_seed_roles[seed]
        try:
            result.kills.extend(
                _reconstruct_game_kills(
                    sample_dir / f"replay-seed-{seed}.jsonl",
                    seed=seed,
                    num_players=num_players,
                    num_impostors=num_impostors,
                    tasks_per_crewmate=tasks_per_crewmate,
                    roles=roles,
                    game_map=game_map,
                )
            )
        except _RECON_CATCH:
            # An integrity breach OR malformed bytes the reconstruction cannot
            # read (a corrupt action row, a truncated file) both mean the set is
            # not a trustworthy recording — floor it, never crash the referee.
            result.integrity_ok = False
    return result


class _IntegrityBreach(Exception):
    """A game did not reconstruct cleanly (integrity breach — the set scores 0).

    Raised on ANY corruption that the referee must not certify:

    * a per-tick or ``state_hash_after`` mismatch (determinism/firewall breach);
    * a duplicate meeting row (two ``MeetingReplayEntry`` for the same tick or
      meeting id) — the report loader double-counts them into D2 / the supply
      floors while the reconstruction dict would silently keep one (mirrors
      ``eval.validity.check_no_duplicate_meeting_rows``);
    * a meeting ``state_hash_before`` that does not equal the trigger tick's hash
      (corrupted meeting metadata the byte-identity walk rejects — mirrors
      ``scripts/_verify_samples.py::_check_meeting_pre_hashes``);
    * a game that reached a meeting with no recorded meeting row (a truncated /
      crashed-mid-meeting replay);
    * a recorded meeting whose ballots do NOT tally (:func:`meetings.voting.tally_ballots`)
      to its recorded ``outcome`` / ``ejected_player_id`` — ``apply_meeting_result``
      consumes only the outcome fields, so tampered ballots pass the hash chain yet
      drive ``plurality_margin`` / ejecting-voters into D3/D4/the railroad floor;
    * a trailing replay row after the terminal event (a fabricated post-game tick /
      meeting the report loader would still fold into D2 / the supply floors);
    * a MISSING terminal outcome — no recorded ``game_over`` row, or a playback
      that never reconstructs a terminal :class:`~engine.events.GameOverEvent`
      (an incomplete recording; a valid game has both);
    * a recorded ``game_over`` winner/reason that does not match the reconstructed
      terminal ``GameOverEvent`` (a FORGED outcome label — the state-hash chain
      does not cover it, so D1/mean_score could otherwise be inflated on a
      tampered set; mirrors ``eval.validity`` check 1).

    Any of these means the recorded bytes are not a trustworthy, complete
    deduction game, so the referee floors the whole set rather than scoring on
    partial / tampered data or silently certifying a corrupt candidate.
    """


# The per-game reconstruction catch: an integrity breach OR malformed bytes both
# floor the set (named so the ``except`` is a statically-checkable tuple).
_RECON_CATCH: Final[tuple[type[BaseException], ...]] = (
    _IntegrityBreach,
    *_MALFORMED_INPUT_ERRORS,
)


def _reconstruct_game_kills(
    replay_path: Path,
    *,
    seed: int,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
    roles: Mapping[PlayerId, Role],
    game_map: Map,
) -> list[_KillWitnessFact]:
    """One read-only playback recovering each kill's crew-witness status.

    :func:`eval.replay_walk.walk_replay` under the named
    ``watchability-referee`` profile (Task 19.25; the walker's docstring is the
    drift record): EVERY profile option is ON — per-tick / meeting pre / post
    hash verification, duplicate-meeting-row and ballot-tally rejection, and
    the completeness / trailing-row / forged-outcome post-walk checks — and
    every violation collapses to the same bare :class:`_IntegrityBreach` (the
    referee floors the whole set, whatever the breach).
    """

    kills: list[_KillWitnessFact] = []
    for walk_event in walk_replay(
        replay_path,
        seed=seed,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
        config=_REFEREE_WALK_CONFIG,
    ):
        if isinstance(walk_event, TickAdvanced):
            for event in walk_event.events:
                if isinstance(event, KilledEvent):
                    kills.append(
                        _KillWitnessFact(
                            seed=seed,
                            victim_role=roles.get(event.target),
                            crew_witnessed=any(
                                roles.get(witness) == "CREWMATE"
                                for witness in event.witnesses
                            ),
                        )
                    )
    return kills


def _raise_integrity_breach(violation: WalkViolation) -> NoReturn:
    raise _IntegrityBreach


# The named Task 19.25 profile (see eval/replay_walk.py's drift record): the
# referee-grade walk — every option ON, every violation the same bare breach.
_REFEREE_WALK_CONFIG: Final[ReplayWalkConfig] = ReplayWalkConfig(
    profile="watchability-referee",
    on_violation=_raise_integrity_breach,
    verify_tick_hashes=True,
    reject_duplicate_meeting_rows=True,
    missing_meeting_row="violation",
    verify_meeting_pre_hashes=True,
    ballot_tally_threshold=SKIP_SUSPICION_THRESHOLD,
    verify_meeting_post_hashes=True,
    require_terminal_tick=True,
    require_reconstructed_outcome=True,
    reject_trailing_rows=True,
    require_game_end_row=True,
    verify_recorded_outcome=True,
)


# --------------------------------------------------------------------------- #
# Meeting-facts derivation (the vote-prompt parse + tally + testimony fold).    #
# --------------------------------------------------------------------------- #


def _testimony_vehicle(
    turn: MeetingTurn, subject: PlayerId
) -> tuple[str | None, bool, bool]:
    """How ``turn`` names ``subject`` + whether the mention is observation-backed.

    Returns ``(vehicle, observation_backed, observation_backed_any)``. The
    vehicle mirrors ``audits/workflows/extract_gameplay_facts.py::_testimony_vehicle``:
    ``"accusation"`` if the turn carries an :class:`AccusationClaim` against the
    subject, else ``"sighting"`` for a :class:`SawPlayerObservation` /
    :class:`SawVentObservation` / other-player :class:`AlibiClaim` naming them,
    else ``"free_text_only"`` if the id appears only in prose, else ``None``.

    SUBJECT-AWARE BACKING (Task 15.19; owner-ratified 2026-07-09,
    audits/review-phase-15-midwave.md Q2): ``observation_backed`` is True iff
    the turn carries a first-hand structured sighting whose subject IS
    ``subject`` — a grounded observation about someone ELSE can no longer back
    this accusation (the exploit the re-anchoring closes: a genuine vent
    sighting of X uttered in the turn that accuses innocent Y counted the
    Y-accusation "backed" under the pre-15.19 predicate). A
    :class:`FoundBodyObservation` names its dead victim (``body_of``), never a
    living accused (the meeting layer drops non-living accusation targets,
    DESIGN.md §5.5), so it structurally cannot back an accusation under the
    subject-aware rule. ``observation_backed_any`` is the FROZEN pre-15.19
    subject-AGNOSTIC bit (ANY grounded observation in the turn — the audit
    extractor's definition), retained ONLY for the 15.2 historical parity pin.

    VENT-AWARE (Task 15.4) — the LIVE bit only: a :class:`SawVentObservation`
    is a first-hand, role-proving structured sighting (a witnessed impostor
    vent — the game's HARDEST evidence), so it counts toward the subject-aware
    ``observation_backed`` bit exactly like a :class:`SawPlayerObservation`,
    keeping a vent-backed accusation from being scored as an unbacked vibe.
    The FROZEN ``observation_backed_any`` bit deliberately does NOT count it:
    that bit exists solely to reproduce the 15.2-era lab scorer
    (``extract_gameplay_facts._testimony_vehicle``), whose isinstance tuple is
    ``(SawPlayerObservation, FoundBodyObservation)`` — the vocabulary at the
    15.2 freeze. Widening the frozen bit to the 15.4 vent type silently broke
    the bit-exact geomean parity on the first bytes where an accusation is
    backed ONLY by a vent sighting (the baseline-4 record, seeds 5/22 —
    Task 16.14's re-pin found the drift), so the frozen bit now mirrors the
    extractor byte-for-byte.
    """

    has_observation = any(
        isinstance(obs, (SawPlayerObservation, FoundBodyObservation))
        for obs in turn.observations
    )
    subject_observed = any(
        isinstance(obs, (SawPlayerObservation, SawVentObservation))
        and obs.subject == subject
        for obs in turn.observations
    )
    accuses = any(
        isinstance(claim, AccusationClaim) and claim.against == subject
        for claim in turn.claims
    )
    sights = subject_observed or any(
        isinstance(claim, AlibiClaim) and claim.subject == subject
        for claim in turn.claims
    )
    if accuses:
        return "accusation", subject_observed, has_observation
    if sights:
        return "sighting", subject_observed, has_observation
    if subject in (turn.free_text or ""):
        return "free_text_only", subject_observed, has_observation
    return None, subject_observed, has_observation


def _suspicion_graph_by_voter(
    meeting: MeetingReport,
) -> dict[PlayerId, dict[PlayerId, float]]:
    """``{voter: {target: rendered_suspicion}}`` parsed from the vote prompts.

    Wires :func:`eval.meeting_quality._parse_suspicion_graph` (the single-home
    §6.6 graph parse) over each meeting llm_call, keyed by ``agent_id`` — the only
    place a per-TARGET rendered suspicion survives into the replay. A voter has one
    graph-bearing vote call; a non-vote prompt parses empty and is skipped.
    """

    graphs: dict[PlayerId, dict[PlayerId, float]] = {}
    for call in meeting.llm_calls:
        if call.agent_id is None:
            continue
        graph = _parse_suspicion_graph(call.prompt)
        if graph:
            graphs[call.agent_id] = graph
    return graphs


def _meeting_facts(
    meeting: MeetingReport,
    meeting_index: int,
    roles: Mapping[PlayerId, Role],
) -> _MeetingFacts:
    """Fold one resolved meeting into the typed geomean/floor input subset.

    Reproduces the ``extract_gameplay_facts._analyze_meeting`` derivations the
    geomean reads: the per-voter suspicion graph + per-target max, the recorded
    ballot tally (plurality target/margin), the ejected player's rendered
    suspicion among the voters who ejected them, the testimony records (accusation
    vehicle + observation-backed bit) over verbally-accused subjects, and the
    contradiction flags RE-DERIVED under the ballot-voter roster.

    The extractor additionally filters accused subjects to the living roster at
    the meeting tick; that filter is a PROVABLE no-op on any valid recording — the
    meeting layer drops non-living / hallucinated accusation targets at record time
    (DESIGN.md §5.5), so every recorded ``AccusationClaim`` names a living
    participant — and is dropped here (verified: the parity fixture reproduces
    exactly without a per-meeting living-roster reconstruction walk).
    """

    graphs = _suspicion_graph_by_voter(meeting)

    # Per-TARGET rendered suspicion = the MAX any OTHER voter rendered (a voter
    # holds no row about itself) — the accumulator-trajectory value.
    rendered_by_target: dict[PlayerId, float] = {}
    for voter, graph in graphs.items():
        for pid, sus in graph.items():
            if pid == voter:
                continue
            prior = rendered_by_target.get(pid)
            if prior is None or sus > prior:
                rendered_by_target[pid] = sus

    ejected_id = meeting.ejected_player_id
    ejected_role = roles.get(ejected_id) if ejected_id is not None else None

    # Recorded ballot tally: plurality target + margin (non-SKIP), and the voters
    # who cast a ballot AT the ejected player.
    non_skip = [b.target for b in meeting.ballots if b.target != "SKIP"]
    target_counts: Counter[PlayerId] = Counter(non_skip)
    plurality_target: PlayerId | None = None
    plurality_margin = 0
    if target_counts:
        ordered = target_counts.most_common()
        plurality_target, plurality_votes = ordered[0]
        runner_up = ordered[1][1] if len(ordered) > 1 else 0
        plurality_margin = plurality_votes - runner_up

    ejecting_voters = [
        b.voter
        for b in meeting.ballots
        if b.target != "SKIP" and b.target == ejected_id
    ]
    ejected_among_ejectors: float | None = None
    if ejected_id is not None:
        ej_values = [
            graphs[v][ejected_id]
            for v in ejecting_voters
            if v in graphs and ejected_id in graphs[v]
        ]
        if ej_values:
            ejected_among_ejectors = max(ej_values)

    # Contradiction flags, RE-DERIVED under the ballot-voter roster (mirrors the
    # extractor's _rederive_meeting_contradictions), grouped by subject with the
    # strong/weak bit; presence of a subject key == "some flag names them".
    roster = frozenset(b.voter for b in meeting.ballots)
    contradictions_by_subject: dict[PlayerId, list[bool]] = {}
    for flag in detect_contradictions(meeting.transcript, roster=roster):
        strong = not is_weak_contradiction(flag)
        for subject in flag.subjects:
            contradictions_by_subject.setdefault(subject, []).append(strong)

    # Testimony records over verbally-accused subjects (either role); a recorded
    # accusation always names a living participant (see the docstring).
    accusations: list[_Accusation] = []
    for turn in meeting.transcript.turns:
        for claim in turn.claims:
            if isinstance(claim, AccusationClaim):
                accusations.append(
                    _Accusation(speaker=turn.speaker, accused=claim.against)
                )
    accused_subjects = sorted(
        {acc.accused for acc in accusations if acc.accused != acc.speaker}
    )
    testimony_records: list[_TestimonyRecord] = []
    for subject in accused_subjects:
        turns: list[_TestimonyTurn] = []
        for turn in meeting.transcript.turns:
            vehicle, obs_backed, obs_backed_any = _testimony_vehicle(turn, subject)
            if vehicle is None:
                continue
            turns.append(
                _TestimonyTurn(
                    vehicle=vehicle,
                    observation_backed=obs_backed,
                    observation_backed_any=obs_backed_any,
                )
            )
        testimony_records.append(
            _TestimonyRecord(
                subject=subject,
                subject_role=roles.get(subject),
                testimony_turns=tuple(turns),
            )
        )

    return _MeetingFacts(
        meeting_index=meeting_index,
        ejected_player_id=ejected_id,
        ejected_role=ejected_role,
        suspicion_graph_by_voter=graphs,
        rendered_suspicion_by_target=rendered_by_target,
        testimony_records=tuple(testimony_records),
        accusations=tuple(accusations),
        plurality_target=plurality_target,
        plurality_margin=plurality_margin,
        ejected_rendered_suspicion_among_ejectors=ejected_among_ejectors,
        contradictions_by_subject={
            subject: tuple(bits) for subject, bits in contradictions_by_subject.items()
        },
        # The persisted role-proving vent flags (readable ONLY from the recorded
        # contradictions — the re-derivation above cannot mint them, Task 15.4).
        persisted_vent_flags=sum(
            1 for flag in meeting.contradictions if flag.kind == "vent_sighting"
        ),
    )


def _accumulator_trajectories(
    meetings: Sequence[_MeetingFacts],
) -> dict[PlayerId, tuple[_TrajectoryPoint, ...]]:
    """Per-player cross-meeting rendered-suspicion trajectory (D4 arc/swing).

    Mirrors ``extract_gameplay_facts``'s ACCUMULATOR TRAJECTORY fold: for each
    player who is a vote CANDIDATE (appears in some other voter's §6.6 graph,
    i.e. in ``rendered_suspicion_by_target``) in 2+ meetings, the meeting-ordered
    sequence of their per-target max rendered suspicion + whether they were
    ejected there. Players in < 2 candidate meetings have no trajectory.
    """

    by_player: dict[PlayerId, list[_TrajectoryPoint]] = {}
    for meeting in meetings:
        for pid, sus in meeting.rendered_suspicion_by_target.items():
            by_player.setdefault(pid, []).append(
                _TrajectoryPoint(
                    meeting_index=meeting.meeting_index,
                    rendered_suspicion=sus,
                    ejected_here=meeting.ejected_player_id == pid,
                )
            )
    return {
        pid: tuple(sorted(points, key=lambda point: point.meeting_index))
        for pid, points in by_player.items()
        if len(points) >= 2
    }


# --------------------------------------------------------------------------- #
# The D1-D4 dimensions + floor + composition (promoted from rubric_score.py).   #
# --------------------------------------------------------------------------- #


def _geomean_weighted(dims: Mapping[str, float]) -> float:
    """ε-floored weighted geometric mean of D1-D4 (rubric_score.py:472).

    ``exp(Σ wₙ · ln(max(dₙ, ε)))`` with ``Σ wₙ == 1`` (a true weighted geomean in
    ``[ε, 1]``). The ε floors each term so a single ZERO dimension SINKS the score
    (the "requires contest" property) without ``ln(0)`` → −∞/NaN.
    """

    total = math.fsum(
        weight * math.log(max(dims[key], _GEOMEAN_EPSILON))
        for key, weight in _GEOMEAN_WEIGHTS.items()
    )
    return math.exp(total)


def _d1_resolution(game: _GameFacts) -> float:
    """D1 — did PLAY decide the board, not the clock? (report-rubric-design.md §3)."""

    reason = game.reason
    n_mtg = len(game.meetings)
    ejected_imp_mtgs = sum(1 for m in game.meetings if m.ejected_role == "IMPOSTOR")
    if reason == "CREWMATE_EJECT":
        return 1.0
    if reason in ("IMPOSTOR_PARITY", "IMPOSTOR_SABOTAGE") and n_mtg >= 1:
        return 0.6
    if ejected_imp_mtgs >= 1:
        return 0.3
    return 0.0


def _meeting_suspicion_separation(
    meeting: _MeetingFacts, roles: Mapping[PlayerId, Role]
) -> float | None:
    """Mean rendered-suspicion(true impostors) − mean(crew) for ONE meeting.

    The D2 truth-tracking primitive: partition every ``voter -> target`` graph row
    by the TARGET's true role (excluding self rows), return impostor-mean minus
    crew-mean. ``None`` when either side has no rows.
    """

    imp: list[float] = []
    crew: list[float] = []
    for voter, graph in meeting.suspicion_graph_by_voter.items():
        for target, sus in graph.items():
            if target == voter:
                continue
            role = roles.get(target)
            if role == "IMPOSTOR":
                imp.append(sus)
            elif role == "CREWMATE":
                crew.append(sus)
    if not imp or not crew:
        return None
    return (math.fsum(imp) / len(imp)) - (math.fsum(crew) / len(crew))


def _subject_has_observation_backed_accusation(
    record: _TestimonyRecord, *, historical_15_2: bool = False
) -> bool:
    """A testimony record carries an OBSERVATION-BACKED ACCUSATION of its subject.

    An ``accusation`` turn whose accuser ALSO logged a first-hand sighting OF
    THE ACCUSED (subject-aware, Task 15.19); a sighting-only turn or a bare
    free-text mention does NOT count (so an enriched meeting's mere sightings
    cannot masquerade as evidence-backed convictions). ``historical_15_2=True``
    reads the frozen pre-15.19 subject-AGNOSTIC bit instead — ONLY for the 15.2
    geomean-parity pin, never for live selection.
    """

    return any(
        turn.vehicle == "accusation"
        and (
            turn.observation_backed_any if historical_15_2 else turn.observation_backed
        )
        for turn in record.testimony_turns
    )


def _observation_backed_impostors(
    meeting: _MeetingFacts, *, historical_15_2: bool = False
) -> set[PlayerId]:
    """True impostors named by an OBSERVATION-BACKED ACCUSATION this meeting."""

    return {
        record.subject
        for record in meeting.testimony_records
        if record.subject_role == "IMPOSTOR"
        and _subject_has_observation_backed_accusation(
            record, historical_15_2=historical_15_2
        )
    }


def _d2_crew_deduction(
    game: _GameFacts, *, historical_15_2: bool = False
) -> tuple[float, float, float]:
    """D2 — does collective suspicion track truth AND convert? (§3 D2).

    Returns ``(d2, separation_norm, conversion)``.
    ``d2 = 0.5 * separation_norm + 0.5 * conversion``.

    CONVERSION-COUPLED (Task 15.19; audits/audit-phase-15-pause.md §4 — the
    EXPLOITED ``kill``/D2-separation channel; report-goodhart-probe.md: forcing
    kills drove separation 0.20 → 0.84 with conversion pinned at 0.00, lifting
    ``mean_score`` 6.51 → 16.62): the separation sub-term is GATED on deduction
    evidence — it counts only when the game converted a backed accusation into
    an ejection (``converted >= 1``) or some meeting carries a contradiction
    flag. Separation without an ejection or a contradiction flag is suspicion
    theater, not deduction, and contributes 0. The flag leg is VENT-AWARE
    (mirroring the ``flags_per_meeting`` merge): the re-derived
    ``contradictions_by_subject`` census can never contain the grounded
    role-proving ``vent_sighting`` flag (Task 15.4), so the persisted vent
    flags (``persisted_vent_flags``) also open the gate — a game whose only
    deduction evidence is a witnessed impostor vent is evidence-rich, not
    suspicion theater. The returned ``separation_norm`` is the GATED value, so
    the reported sub-term always composes to the scored d2.
    ``historical_15_2=True`` computes the FROZEN pre-15.19 spec
    (subject-agnostic backing, uncoupled separation) — ONLY for the 15.2
    geomean-parity pin.
    """

    separations = [
        sep
        for m in game.meetings
        if (sep := _meeting_suspicion_separation(m, game.roles)) is not None
    ]
    separation_norm = (
        max(
            0.0,
            min(
                1.0,
                (math.fsum(separations) / len(separations)) / _D2_SEPARATION_SCALE,
            ),
        )
        if separations
        else 0.0
    )
    converted = attempted = 0
    for m in game.meetings:
        for subject in _observation_backed_impostors(
            m, historical_15_2=historical_15_2
        ):
            attempted += 1
            if m.ejected_player_id == subject:
                converted += 1
    conversion = (converted / attempted) if attempted else 0.0
    if not historical_15_2:
        has_deduction_evidence = converted >= 1 or any(
            m.contradictions_by_subject or m.persisted_vent_flags for m in game.meetings
        )
        if not has_deduction_evidence:
            separation_norm = 0.0
    return 0.5 * separation_norm + 0.5 * conversion, separation_norm, conversion


def _active_deflection_counts(game: _GameFacts) -> tuple[int, bool]:
    """Per-game ``(effective_deflections, any_accused)`` (D3 impostor craft).

    For every (meeting, true impostor verbally accused by ANOTHER speaker) the
    impostor SURVIVES unless that meeting ejected them; a survival is EFFECTIVE
    iff the impostor counter-accused some other player AND the strict eject
    plurality (``plurality_margin > 0``) landed OFF the impostor — the
    counter-accusation MOVED the table.
    """

    effective = 0
    any_accused = False
    for m in game.meetings:
        accused_impostors = {
            acc.accused
            for acc in m.accusations
            if game.roles.get(acc.accused) == "IMPOSTOR" and acc.accused != acc.speaker
        }
        if not accused_impostors:
            continue
        any_accused = True
        for impostor in accused_impostors:
            if m.ejected_player_id == impostor:
                continue  # caught here — not a survival
            counter_targets = {
                acc.accused
                for acc in m.accusations
                if acc.speaker == impostor and acc.accused != impostor
            }
            if not counter_targets:
                continue  # passive / clock survival — no active deflection
            plurality = m.plurality_target if m.plurality_margin > 0 else None
            if plurality is not None and plurality != impostor:
                effective += 1
    return effective, any_accused


def _d3_impostor_craft(game: _GameFacts) -> float:
    """D3 — is deception + agency load-bearing? (§3 D3)."""

    effective, any_accused = _active_deflection_counts(game)
    if effective >= 1:
        return 1.0
    if any_accused:
        return 0.2
    return 0.0


def _suspicion_rose_onto_impostor(game: _GameFacts) -> bool:
    """The game ejected a true impostor on a RISING cross-meeting arc (D4 arc)."""

    for m in game.meetings:
        ejected = m.ejected_player_id
        if ejected is None or game.roles.get(ejected) != "IMPOSTOR":
            continue
        sequence = game.trajectories.get(ejected)
        if sequence is None:
            continue
        eject_points = [i for i, point in enumerate(sequence) if point.ejected_here]
        if not eject_points:
            continue
        j = eject_points[0]
        if j >= 1 and sequence[j].rendered_suspicion > sequence[0].rendered_suspicion:
            return True
    return False


def _game_has_swing(game: _GameFacts) -> bool:
    """The D4 SWING term: a knife-edge eject + REAL cross-meeting suspicion move."""

    for m in game.meetings:
        if m.ejected_player_id is None or m.plurality_margin != 1:
            continue
        sequence = game.trajectories.get(m.ejected_player_id)
        if sequence is None:
            continue
        eject_points = [i for i, point in enumerate(sequence) if point.ejected_here]
        if not eject_points:
            continue
        j = eject_points[0]
        if (
            j >= 1
            and abs(sequence[j].rendered_suspicion - sequence[0].rendered_suspicion)
            > 1e-9
        ):
            return True
    return False


def _d4_arc(game: _GameFacts) -> tuple[float, float, float, float]:
    """D4 — a CONTESTED build, not a one-shot. (§3 D4).

    Returns ``(d4, arc, swing, contest)``.
    ``d4 = 0.45 * arc + 0.35 * swing + 0.20 * contest``.
    """

    n_mtg = len(game.meetings)
    arc = 1.0 if _suspicion_rose_onto_impostor(game) else 0.0
    swing = 1.0 if _game_has_swing(game) else 0.0
    contest = min(1.0, max(0, n_mtg - 1) / 2.0)
    return 0.45 * arc + 0.35 * swing + 0.20 * contest, arc, swing, contest


def _is_railroad_ejection(
    meeting: _MeetingFacts, *, historical_15_2: bool = False
) -> bool:
    """Whether a CREWMATE ejection is a railroad (report-rubric-design.md §3 floor).

    Two structural forms, EITHER floors: **gate-bypass** — the ejected crewmate's
    rendered suspicion among the ejectors is below the §4.6 gate or absent (the
    anti-railroad tally was bypassed); or **evidence-free conviction** — NO
    observation-backed accusation names the ejected AND no contradiction flag names
    them. A crewmate ejected ABOVE the gate WITH a backed accusation or a flag is
    an honest (mistaken) deduction, scored low by D2, never floored.

    The backed-accusation leg uses the ONE live backing predicate
    (:func:`_subject_has_observation_backed_accusation`), so it is SUBJECT-AWARE
    since Task 15.19: a conviction whose only "backing" is a grounded
    observation about someone ELSE is an evidence-free conviction of the
    ejected. ``historical_15_2=True`` keeps the frozen pre-15.19 behavior for
    the parity pin.
    """

    among = meeting.ejected_rendered_suspicion_among_ejectors
    if among is None or among < _RAILROAD_GATE:
        return True
    ejected = meeting.ejected_player_id
    record = next((r for r in meeting.testimony_records if r.subject == ejected), None)
    has_flag = ejected in meeting.contradictions_by_subject
    backed = record is not None and _subject_has_observation_backed_accusation(
        record, historical_15_2=historical_15_2
    )
    return not backed and not has_flag


def _floor_multiplier(game: _GameFacts, *, historical_15_2: bool = False) -> float:
    """The hard integrity floors (report-rubric-design.md §3): 0.0 on ANY breach.

    Punish-only, never a tradeable dimension: a firewall/determinism breach
    (``integrity_ok`` False), a friendly-fire kill (an impostor victim), or a
    railroad CREWMATE ejection each sink the WHOLE game to 0.
    """

    if not game.integrity_ok:
        return 0.0
    if any(role == "IMPOSTOR" for role in game.kill_victim_roles):
        return 0.0
    for m in game.meetings:
        if (
            m.ejected_player_id is not None
            and m.ejected_role == "CREWMATE"
            and _is_railroad_ejection(m, historical_15_2=historical_15_2)
        ):
            return 0.0
    return 1.0


class WatchabilityGameScore(BaseModel):
    """The Layer-2 D1-D4 geomean breakdown for one game (frozen)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    seed: int
    reason: str
    n_meetings: int
    floor_multiplier: float
    d1_resolution: float
    d2_deduction: float
    d3_craft: float
    d4_arc: float
    d2_separation_norm: float
    d2_conversion: float
    d4_arc_term: float
    d4_swing_term: float
    d4_contest_term: float
    score: float


def compute_game_score(
    game: _GameFacts, *, historical_15_2: bool = False
) -> WatchabilityGameScore:
    """Score one game: ``100 * floor * geomean_weighted(D1-D4)`` (rubric_score.py:823).

    The SINGLE source of the composition — both the per-game ``score`` and the
    D1-D4 breakdown route through here so they can never drift.

    ``historical_15_2=True`` scores under the FROZEN pre-15.19 spec
    (subject-agnostic observation backing, uncoupled D2 separation) — the mode
    exists ONLY so the committed ``experiments/lab/results-rubric-geomean.json``
    stays an exact, reproducible cross-implementation parity fixture for Task
    15.2. It must NEVER select a champion; live selection always uses the
    default hardened doctrine.
    """

    d1 = _d1_resolution(game)
    d2, d2_sep, d2_conv = _d2_crew_deduction(game, historical_15_2=historical_15_2)
    d3 = _d3_impostor_craft(game)
    d4, d4_arc, d4_swing, d4_contest = _d4_arc(game)
    floor = _floor_multiplier(game, historical_15_2=historical_15_2)
    geomean = _geomean_weighted({"d1": d1, "d2": d2, "d3": d3, "d4": d4})
    return WatchabilityGameScore(
        seed=game.seed,
        reason=game.reason,
        n_meetings=len(game.meetings),
        floor_multiplier=floor,
        d1_resolution=round(d1, 3),
        d2_deduction=round(d2, 3),
        d3_craft=round(d3, 3),
        d4_arc=round(d4, 3),
        d2_separation_norm=round(d2_sep, 3),
        d2_conversion=round(d2_conv, 3),
        d4_arc_term=round(d4_arc, 3),
        d4_swing_term=round(d4_swing, 3),
        d4_contest_term=round(d4_contest, 3),
        score=round(100.0 * floor * geomean, 1),
    )


# --------------------------------------------------------------------------- #
# The composed referee.                                                        #
# --------------------------------------------------------------------------- #


class WatchabilityReport(BaseModel):
    """The composed selection-referee verdict over one replay-set directory (frozen).

    ``referee_passed`` is the Layer-1 supply-floor verdict AND the set integrity
    flag; the Layer-2 ``per_game`` geomean is the selection SCORE (a champion is
    chosen by it, never trained on it). ``mean_score`` / ``median_score`` must
    NEVER be read without the supply-floor gate: the bare geomean is
    Goodhart-able (the 15.14 exploit lived entirely on the ungated sub-metric).
    See the module JSON schema.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    replay_set_dir: str
    baseline_id: str
    roster_key: str
    games_total: int
    integrity_ok: bool
    referee_passed: bool
    supply_floors_passed: bool
    supply_gauges: tuple[SupplyFloorGauge, ...]
    mean_score: float
    median_score: float
    per_game: tuple[WatchabilityGameScore, ...]


def _roster_key(sample_dir: Path) -> str:
    """The ``{num_players}p{num_impostors}i`` key for the per-baseline floor block."""

    num_players, num_impostors, _ = resolve_roster_knobs(sample_dir)
    return f"{num_players}p{num_impostors}i"


def _game_facts(
    game: GameReport,
    roles: Mapping[PlayerId, Role],
    kill_victim_roles: Sequence[Role | None],
    *,
    integrity_ok: bool,
) -> _GameFacts:
    """Assemble one game's typed geomean/floor input subset from its report."""

    meetings = tuple(
        _meeting_facts(meeting, index, roles)
        for index, meeting in enumerate(game.meetings)
    )
    return _GameFacts(
        seed=game.seed,
        reason=game.reason,
        roles=roles,
        meetings=meetings,
        kill_victim_roles=tuple(kill_victim_roles),
        trajectories=_accumulator_trajectories(meetings),
        integrity_ok=integrity_ok,
    )


def _persisted_vent_flag_count(report: TournamentReport) -> int:
    """Count the persisted role-proving ``vent_sighting`` flags across a report.

    The grounded ``vent_sighting`` flag (Task 15.4 — the game's HARDEST evidence,
    a witnessed impostor vent) is minted only when the live meeting layer holds the
    speaker's private :class:`~meetings.schemas.VentWitnessRecord` grounding
    channel, which carries no transcript id by design. So the re-derivation
    :func:`~meetings.transcript.detect_contradictions` runs from a recorded
    transcript alone (with no grounding channel) can NEVER reproduce it — see
    ``meetings/transcript.py``'s ``if vent_witness_records`` gate. The flag is
    instead persisted on the recorded :attr:`~eval.report_schema.MeetingReport.contradictions`;
    this reads it from there.
    """

    return sum(
        1
        for game in report.games
        for meeting in game.meetings
        for flag in meeting.contradictions
        if flag.kind == "vent_sighting"
    )


def _observation_backed_conversion(
    games: Sequence[_GameFacts],
) -> tuple[float | None, int, int]:
    """Set-level OBSERVATION-BACKED conversion — the D2 conversion, aggregated.

    Returns ``(rate, attempted, converted)``. Over every (meeting,
    observation-backed-accused true impostor) pair (:func:`_observation_backed_impostors`
    — the SAME evidence-grounded predicate the per-game D2 conversion uses,
    SUBJECT-AWARE since Task 15.19: the accuser's grounded sighting must name
    the accused), the fraction the meeting EJECTED. ``rate`` is ``None`` when no
    such pair exists (undefined, not 0.0). This is deliberately the backed
    predicate, not any verbal accusation, so the "testimony-BACKED" floor cannot
    be cleared by ungrounded vibe-convictions — nor, since 15.19, by a genuine
    observation about someone other than the accused.
    """

    attempted = converted = 0
    for game in games:
        for meeting in game.meetings:
            for subject in _observation_backed_impostors(meeting):
                attempted += 1
                if meeting.ejected_player_id == subject:
                    converted += 1
    rate = (converted / attempted) if attempted else None
    return rate, attempted, converted


def _supply_gauge_values(
    report: TournamentReport,
    kills: Sequence[_KillWitnessFact],
    games: Sequence[_GameFacts],
) -> SupplyGaugeValues:
    """The three Layer-1 gauges over a report + reconstructed kills + game facts.

    ``flags_per_meeting`` is VENT-AWARE: :func:`eval.meeting_quality.compute_supply_gauges`
    re-derives flags from the transcript and cannot reproduce the grounded
    ``vent_sighting`` flag (the grounding channel is not in the transcript), so the
    persisted vent flags are MERGED in (:func:`_persisted_vent_flag_count`) — else a
    vent-rich baseline-3 candidate's strongest evidence would be undercounted as
    evidence-starved. Zero on the committed v4 sets (no vent turns), so the pinned
    baseline-2 floors are unchanged; the persisted census and the re-derived
    non-vent flags are disjoint (re-derivation never mints ``vent_sighting``), so no
    double count.

    ``testimony_backed_conversion`` is the OBSERVATION-BACKED conversion
    (:func:`_observation_backed_conversion`), consistent with the geomean's D2 —
    NOT the unbacked ``impostor_accused_conversion_rate``.
    """

    total_kills = len(kills)
    crew_witnessed = sum(1 for kill in kills if kill.crew_witnessed)
    supply = compute_supply_gauges(report)
    persisted_vent_flags = _persisted_vent_flag_count(report)
    total_flags = supply.total_flags + persisted_vent_flags
    backed_rate, backed_attempted, backed_converted = _observation_backed_conversion(
        games
    )
    return SupplyGaugeValues(
        witnessed_event_rate=(crew_witnessed / total_kills if total_kills else None),
        total_kills=total_kills,
        crew_witnessed_kills=crew_witnessed,
        flags_per_meeting=(
            total_flags / supply.meetings_total if supply.meetings_total else None
        ),
        total_flags=total_flags,
        persisted_vent_flags=persisted_vent_flags,
        meetings_total=supply.meetings_total,
        testimony_backed_conversion=backed_rate,
        backed_conversion_attempted=backed_attempted,
        backed_conversion_converted=backed_converted,
    )


def compute_watchability(
    sample_dir: Path, *, baseline_id: str = _DEFAULT_BASELINE_ID
) -> WatchabilityReport:
    """Run the two-layer selection referee over ``sample_dir`` from committed bytes.

    FROZEN (Phase 19 tier map, training/README.md): the champion-SELECTION
    referee is frozen with the champion opt-in path it serves. Bug fixes and
    evidence readers only; no new search. The supply floors it evaluates are
    pinned measurements and stay untouched — re-pricing them is the reopening
    checklist's route A, an owner decision (the map §7).

    Pure + offline. Assembles the typed tournament report (roster + re-seeded
    roles + frozen-outcome fold, shared with the validity gate), reconstructs each
    game once for kill witnesses + the integrity flag, folds the Layer-2 D1-D4
    geomean per game, and evaluates the Layer-1 supply floors for the resolved
    ``(baseline_id, roster_key)``.

    ``referee_passed`` is ``supply_floors_passed AND integrity_ok`` — a candidate
    whose games produce structurally less evidence than the baseline, or whose
    bytes do not reconstruct, is REJECTED. Raises :class:`KeyError` if
    ``baseline_id`` / the resolved roster has no pinned floor block (no silent
    fallback — an un-pinned baseline must not certify a champion).
    """

    if not sample_dir.is_dir():
        raise NotADirectoryError(f"replay-set directory not found: {sample_dir}")
    seeds = seeds_on_disk(sample_dir)
    if not seeds:
        raise ValueError(f"no replay-seed-*.jsonl found under {sample_dir}")

    roster_key = _roster_key(sample_dir)
    baseline_floors = _BASELINE_SUPPLY_FLOORS.get(baseline_id)
    if baseline_floors is None:
        raise KeyError(
            f"no supply-floor block pinned for baseline_id {baseline_id!r} "
            f"(known: {sorted(_BASELINE_SUPPLY_FLOORS)})"
        )
    floors = baseline_floors.get(roster_key)
    if floors is None:
        raise KeyError(
            f"baseline {baseline_id!r} has no supply floors for roster "
            f"{roster_key!r} (known: {sorted(baseline_floors)})"
        )

    # Fail CLOSED on malformed candidate bytes: the report loader / reconstruction
    # rejecting a corrupt set (duplicate ticks, an unrecoverable meeting trigger, a
    # bad action row) must produce a FAILING report, not abort the bake-off's
    # ``--watchability --json`` run with a traceback. (The dir / seed / baseline
    # resolution above are caller errors and still propagate.)
    try:
        report = assemble_tournament_report(sample_dir)
        num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(
            sample_dir
        )
        game_map = load_canonical_map()
        per_seed_roles = roles_by_seed(
            sample_dir,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            game_map=game_map,
        )
        reconstruction = _reconstruct_kills(sample_dir)
    except _MALFORMED_INPUT_ERRORS:
        return _fail_closed_report(
            sample_dir, baseline_id, roster_key, floors, games_total=len(seeds)
        )

    kills_by_seed: dict[int, list[_KillWitnessFact]] = {}
    for kill in reconstruction.kills:
        kills_by_seed.setdefault(kill.seed, []).append(kill)

    all_facts = [
        _game_facts(
            game,
            per_seed_roles[game.seed],
            [kill.victim_role for kill in kills_by_seed.get(game.seed, [])],
            integrity_ok=reconstruction.integrity_ok,
        )
        for game in report.games
    ]
    scores = sorted(
        (compute_game_score(facts) for facts in all_facts),
        key=lambda s: s.score,
        reverse=True,
    )
    gauges = _supply_gauge_values(report, reconstruction.kills, all_facts)
    supply_passed, gauge_reports = evaluate_supply_floors(gauges, floors)

    return WatchabilityReport(
        replay_set_dir=str(sample_dir),
        baseline_id=baseline_id,
        roster_key=roster_key,
        games_total=len(report.games),
        integrity_ok=reconstruction.integrity_ok,
        referee_passed=supply_passed and reconstruction.integrity_ok,
        supply_floors_passed=supply_passed,
        supply_gauges=gauge_reports,
        mean_score=(
            round(math.fsum(s.score for s in scores) / len(scores), 2)
            if scores
            else 0.0
        ),
        median_score=(
            round(statistics.median(s.score for s in scores), 2) if scores else 0.0
        ),
        per_game=tuple(scores),
    )


def _fail_closed_report(
    sample_dir: Path,
    baseline_id: str,
    roster_key: str,
    floors: SupplyFloors,
    *,
    games_total: int,
) -> WatchabilityReport:
    """A rejecting :class:`WatchabilityReport` for a set the loader can't read.

    Every gauge is ``None`` (so every numeric floor fails), ``integrity_ok`` and
    ``referee_passed`` are False, and there are no scored games — the fail-closed
    verdict a bake-off consumer reads instead of a traceback.
    """

    unreadable = SupplyGaugeValues(
        witnessed_event_rate=None,
        total_kills=0,
        crew_witnessed_kills=0,
        flags_per_meeting=None,
        total_flags=0,
        persisted_vent_flags=0,
        meetings_total=0,
        testimony_backed_conversion=None,
        backed_conversion_attempted=0,
        backed_conversion_converted=0,
    )
    _, gauge_reports = evaluate_supply_floors(unreadable, floors)
    return WatchabilityReport(
        replay_set_dir=str(sample_dir),
        baseline_id=baseline_id,
        roster_key=roster_key,
        games_total=games_total,
        integrity_ok=False,
        referee_passed=False,
        supply_floors_passed=False,
        supply_gauges=gauge_reports,
        mean_score=0.0,
        median_score=0.0,
        per_game=(),
    )


__all__ = [
    "FloorPin",
    "SupplyFloorGauge",
    "SupplyFloors",
    "SupplyGaugeValues",
    "WatchabilityGameScore",
    "WatchabilityReport",
    "compute_game_score",
    "compute_watchability",
    "evaluate_supply_floors",
    "population_relative_conversion_floor",
]
