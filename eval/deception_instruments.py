"""Tier-A deception instruments over committed replay bytes (Task 18.1).

Anchored to ``audits/audit-phase-18-planning.md`` §3.1-§3.2, DESIGN.md §11.3, and
the Task 18.1 definition of done. This module folds a replay-set directory's
committed bytes into a single frozen diagnostic report describing HOW impostors
deceive: whom they accuse, whom they vouch for, and whether those vouches are
grounded in the impostor's own reconstructed sightings.

Tier-A doctrine
---------------
These are pure, offline, $0 DIAGNOSTICS. They never gate a build and never feed
an agent reward (DESIGN.md §11.3's population-relative doctrine: a diagnostic
reports the population's behaviour, it does not score an individual). Every cell
is a deterministic function of the committed replay bytes.

Why the signature takes a directory, not a ``TournamentReport``
---------------------------------------------------------------
The grounded-vs-fabricated vouch split MUST run through the production
chokepoint :func:`meetings.transcript.grounded_vouch_subjects`, which requires
each speaker's own reconstructed :class:`~meetings.schemas.SightingRecord`
snapshots. Those exist only via the memory-augmented walk
:func:`eval.funnel._walk_set_vj` (which takes a directory and reconstructs the
per-agent memory layer exactly where the live game reads it). Precedent:
:func:`eval.funnel.compute_pooling_funnel` and
:mod:`eval.vj_instruments` already import and reuse the private
``_walk_set_vj`` / ``_VJMeeting`` carriers from :mod:`eval.funnel`; this module
follows that idiomatic reuse path rather than re-implementing the walk.

Landed census predicates (audit §3.1, measured on ``replays/ml_corpus/9p2i``:
150 games, 541 meetings)
----------------------------------------------------------------------------
All accusation / vouch / corroboration channels are measured over IMPOSTOR
speech (the deception the instrument studies). During reconciliation against the
audit's §3.1 targets, two audit labels proved to name IMPOSTOR-scoped counts
rather than all-speaker totals (verified against the committed bytes):

* the audit's "84 whereabouts claims" is the IMPOSTOR whereabouts count (the raw
  all-speaker total is 1099); whereabouts is not a cell here, noted only to
  document the scoping convention.
* the audit's "46 corroboration claims" is the IMPOSTOR corroboration count (the
  raw all-speaker total is 176). This module keeps the honest raw total in
  ``corroboration_claims_total`` (176 on corpus) AND the impostor-scoped count in
  ``corroboration_claims_impostor`` (46) -- the audit's 46 lands on the latter.
  Reconciliation note: the spec's suggested "living-speaker filter" does not move
  the raw total (no dead player speaks a corroboration in this corpus), so the
  audit's 46 is fundamentally the impostor-speaker count.

The primary §3.1 pins that land EXACTLY on the corpus bytes:

* impostor accusations of crew (frame attempts): 455; of a co-impostor: 0;
  self-accusations: 0 (partition of 455 total impostor accusations).
* impostor ``saw_player`` false vouches placing the co-impostor: 34.
* impostor corroboration claims: 46.
* crew ejected / impostor ejected / no-eject meetings: 13 / 229 / 299 (== 541).
* frame conversions (a crewmate ejected whom an impostor accused that meeting): 5.

Predicate definitions (each landed on the corpus bytes):

1. Impostor accusation census -- for every turn whose speaker is an impostor
   (author-role subscript, mirroring ``eval/alibi_fabrication.py:203-211``; no
   living filter needed -- the pins land without one), every
   :class:`~meetings.schemas.AccusationClaim` is partitioned by target role:
   frame attempt (target is a crewmate), teammate accusation (target is another
   impostor), self accusation (target is the speaker). The three partition the
   total exactly.
2. Frame-attempt meetings -- meetings with >=1 frame attempt (the conversion
   denominator).
3. Frame conversion (meeting-level) -- ``outcome == "EJECTED"`` and the ejected
   player is a crewmate whom some impostor accused in that meeting. A guaranteed
   subset of frame-attempt meetings.
4. Eject-outcome context -- crew-ejected / impostor-ejected / no-eject counts.
   No-eject == ``outcome != "EJECTED"`` (``ejected is None`` there by the
   :class:`~meetings.schemas.MeetingResult` invariant).
5. Impostor vouch census (``saw_player`` channel) -- mirrors
   ``eval/funnel.py:1404`` ``_vouch_census`` with an added living-impostor
   speaker filter: a :class:`~meetings.schemas.SawPlayerObservation` whose
   subject is another living player. ``vouch_observations_impostor`` is the
   denominator; ``false_vouch_saw_player_observations`` is the subset whose
   subject is the co-impostor.
6. Corroboration channel -- ``corroboration_claims_total`` is the raw count of
   :class:`~meetings.schemas.CorroborationClaim` over ALL turns.
   ``corroboration_claims_impostor`` is the subset spoken by a living impostor
   supporting another living player (the false-vouch denominator);
   ``false_vouch_corroborations`` is the subset supporting the co-impostor.
7. ``false_vouches_total`` == ``false_vouch_saw_player_observations`` +
   ``false_vouch_corroborations`` (the contract's two false-vouch channels).
8. Grounded-vs-fabricated split (``saw_player`` channel only -- the chokepoint's
   domain). Per meeting, :func:`meetings.transcript.grounded_vouch_subjects` is
   called exactly as ``eval/funnel.py:1430`` ``_grounded_vouch_set`` does, but
   with the sighting-records mapping RESTRICTED to impostor speakers. Rationale:
   the false-vouch split asks whether the IMPOSTOR's placement of the teammate is
   backed by the impostor's OWN records; passing the full mapping could ground a
   co-impostor subject through a crew speaker's records. The restriction is an
   INPUT filter -- all grounding semantics remain the production function's.
   ``false_vouch_subject_events`` counts (meeting, subject) pairs where >=1
   impostor ``saw_player`` false vouch names that co-impostor subject (the
   chokepoint's per-meeting-per-subject granularity); ``false_vouch_grounded`` is
   the pairs whose subject is in the restricted grounded set;
   ``false_vouch_fabricated`` is the rest. The split therefore partitions
   SUBJECT EVENTS, deliberately NOT the observation numerator (34 observations
   vs 28 subject events on the corpus: repeat placements of the same teammate
   within one meeting collapse). This granularity is the production function's
   own -- it dedups subjects internally (``meetings/transcript.py``,
   "``if observation.subject in grounded``") and returns a per-meeting subject
   set, so no per-observation verdict exists to adopt, and re-matching records
   per observation would be the re-derivation the 18.1 DoD forbids.

   For downstream reconciliation the report ALSO carries the observation-level
   companion join: ``false_vouch_grounded_subject_observations`` +
   ``false_vouch_fabricated_subject_observations`` partition
   ``false_vouch_saw_player_observations`` exactly, bucketing every false-vouch
   observation by its SUBJECT's chokepoint verdict. These are an explicit join
   (a duplicate placement inherits its subject's classification), NOT
   per-observation grounding verdicts -- the docstring on
   :func:`_grounded_split` states the distinction.

   "Fabricated" here means UNGROUNDED BY THE CHOKEPOINT: the impostor holds no
   record that both matches the spoken sighting AND passes the §6.3 Rule-3
   relevance gate. The cell is therefore a corroboration-grade-backing verdict,
   not a literal no-record-exists claim: a placement backed only by a
   Rule-3-excluded record (a spawn-window or kill-scene sighting --
   evidentially-empty cover by the production bar) counts as fabricated,
   deliberately, and the two ungrounded shapes are not separable through the
   chokepoint's public inputs (separating them would re-derive the record
   match the DoD forbids). Empirically, on the committed corpus bytes ALL 7
   fabricated subject events are of the record-matched-but-Rule-3-excluded
   shape (spawn-window/kill-scene co-presence weaponized as cover); none is a
   whole-cloth invention with no matching record at all.
9. Adoption wrappers (pure assembly, no metric math re-implemented -- the
   ``build_tournament_eval_report`` doctrine, ``eval/meeting_quality.py:2649``):
   :func:`eval.validity.assemble_tournament_report` feeds
   :func:`eval.alibi_fabrication.compute_alibi_fabrication_rate` and
   :func:`eval.meeting_quality.compute_effective_deflection`; both frozen reports
   nest as fields. A fail-loud cross-check raises if the walk's total meeting
   count disagrees with the assembled report's.

Rare-event advisory + Wilson (the 15.19 rule, generalized per the 18.1 DoD)
---------------------------------------------------------------------------
:class:`RareEventCell` pairs a rare-count point estimate with its Wilson 95%
score interval (stdlib ``math`` only). ``advisory`` fires when the numerator is
at most :data:`_RARE_EVENT_ADVISORY_MAX_NUMERATOR` (7), generalizing 15.19's
``<= 1`` guard: at that scale the point rate is statistically fragile and the
interval should be read instead.

Leak-safety
-----------
Every model on this module carries only ints, floats, ``float | None`` rates,
and a single directory-path string -- no roles, transcripts, player ids, or
engine-owned types cross the model boundary.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict, model_validator

from engine.entities import PlayerId, Role
from eval.alibi_fabrication import (
    AlibiFabricationReport,
    compute_alibi_fabrication_rate,
)
from eval.funnel import _VJGameWalk, _VJMeeting, _walk_set_vj
from eval.meeting_quality import (
    EffectiveDeflectionReport,
    compute_effective_deflection,
)
from eval.validity import assemble_tournament_report
from meetings.schemas import (
    AccusationClaim,
    CorroborationClaim,
    SawPlayerObservation,
)
from meetings.transcript import grounded_vouch_subjects

# 95% two-sided Wilson score constant.
_WILSON_Z: Final[float] = 1.96
# 18.1 DoD rare-event advisory bar (generalizes 15.19's <= 1 guard).
_RARE_EVENT_ADVISORY_MAX_NUMERATOR: Final[int] = 7


class _FrozenModel(BaseModel):
    """Frozen, ``extra="forbid"`` base (the ``eval/alibi_fabrication.py`` base)."""

    model_config = ConfigDict(frozen=True, extra="forbid")


def _wilson_interval(
    numerator: int, denominator: int
) -> tuple[float | None, float | None, float | None]:
    """Point rate and Wilson 95% score interval for ``numerator`` of ``denominator``.

    Returns ``(rate, low, high)``. All three are ``None`` when ``denominator``
    is 0 (the None-not-0.0 sentinel -- ``eval/meeting_quality.py`` convention).
    Pure stdlib ``math``; no numpy/scipy (18.1 DoD).
    """

    if denominator == 0:
        return None, None, None
    z = _WILSON_Z
    n = denominator
    p_hat = numerator / n
    denom = 1.0 + z * z / n
    center = (p_hat + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p_hat * (1 - p_hat) / n + z * z / (4 * n * n))
    low = max(0.0, center - half)
    high = min(1.0, center + half)
    return p_hat, low, high


class RareEventCell(_FrozenModel):
    """A rare-count point estimate beside its Wilson 95% score interval.

    ``rate`` / ``wilson_low`` / ``wilson_high`` are ``None`` iff
    ``denominator == 0``. ``advisory`` fires when ``numerator`` is at most
    :data:`_RARE_EVENT_ADVISORY_MAX_NUMERATOR`, flagging that the point rate is
    statistically fragile and the interval should be read instead.

    **Leak-safety.** Two ints, three ``float | None`` fields, one bool -- no
    roles, transcripts, or engine-owned types.
    """

    numerator: int
    denominator: int
    rate: float | None
    wilson_low: float | None
    wilson_high: float | None
    advisory: bool

    @model_validator(mode="after")
    def _validate(self) -> RareEventCell:
        if self.numerator < 0 or self.denominator < 0:
            raise ValueError("RareEventCell counts must be non-negative")
        if self.numerator > self.denominator:
            raise ValueError(
                "RareEventCell numerator cannot exceed denominator: "
                f"{self.numerator} > {self.denominator}"
            )
        interval_is_none = (
            self.rate is None and self.wilson_low is None and self.wilson_high is None
        )
        if self.denominator == 0:
            if not interval_is_none:
                raise ValueError(
                    "RareEventCell with denominator 0 must have None rate/interval"
                )
        else:
            if self.rate is None or self.wilson_low is None or self.wilson_high is None:
                raise ValueError(
                    "RareEventCell with a positive denominator must have a "
                    "defined rate and interval"
                )
            # Fail-loud value check (AGENTS.md "no silent fallbacks"): a cell
            # loaded from stale or hand-built JSON must not carry a rate or
            # interval that contradicts its own counts. Exact equality is
            # correct here -- construction and JSON round-trip both preserve
            # the identical doubles.
            expected_rate, expected_low, expected_high = _wilson_interval(
                self.numerator, self.denominator
            )
            if (
                self.rate != expected_rate
                or self.wilson_low != expected_low
                or self.wilson_high != expected_high
            ):
                raise ValueError(
                    "RareEventCell rate/interval must equal the Wilson values "
                    f"recomputed from {self.numerator}/{self.denominator}: got "
                    f"({self.rate}, {self.wilson_low}, {self.wilson_high}), "
                    f"expected ({expected_rate}, {expected_low}, {expected_high})"
                )
        expected_advisory = self.numerator <= _RARE_EVENT_ADVISORY_MAX_NUMERATOR
        if self.advisory != expected_advisory:
            raise ValueError(
                "RareEventCell advisory flag must equal numerator <= "
                f"{_RARE_EVENT_ADVISORY_MAX_NUMERATOR}"
            )
        return self


def _rare_event_cell(numerator: int, denominator: int) -> RareEventCell:
    """Build a :class:`RareEventCell` with its Wilson interval and advisory flag."""

    rate, low, high = _wilson_interval(numerator, denominator)
    return RareEventCell(
        numerator=numerator,
        denominator=denominator,
        rate=rate,
        wilson_low=low,
        wilson_high=high,
        advisory=numerator <= _RARE_EVENT_ADVISORY_MAX_NUMERATOR,
    )


class DeceptionInstrumentsReport(_FrozenModel):
    """Tier-A deception diagnostics over one replay set (Task 18.1).

    A pure fold of committed replay bytes: the impostor accusation partition,
    the eject-outcome context, the two false-vouch channels with their
    grounded-vs-fabricated split, and the two adopted analyzers. Never gates,
    never rewards (DESIGN.md §11.3).

    **Leak-safety.** Ints, ``float | None`` rates, nested frozen count-only
    reports, and one directory-path string -- no roles, transcripts, player ids,
    or engine-owned types.
    """

    replay_set_dir: str
    num_players: int
    num_impostors: int
    tasks_per_crewmate: int
    games_total: int
    meetings_total: int
    # accusation census
    impostor_accusations_total: int
    frame_attempts: int
    impostor_self_accusations: int
    teammate_accusations: RareEventCell
    frame_attempt_meetings: int
    frame_conversions: RareEventCell
    # eject-outcome context
    crew_ejected_meetings: int
    impostor_ejected_meetings: int
    no_eject_meetings: int
    # false-vouch census
    vouch_observations_impostor: int
    false_vouch_saw_player_observations: int
    false_vouch_saw_player_rate: float | None
    corroboration_claims_total: int
    corroboration_claims_impostor: int
    false_vouch_corroborations: int
    false_vouch_corroboration_rate: float | None
    false_vouches_total: int
    # grounded split (production chokepoint, saw_player channel)
    false_vouch_subject_events: int
    false_vouch_grounded: int
    false_vouch_fabricated: int
    false_vouch_grounded_share: float | None
    # observation-level companion join (partitions the observation numerator)
    false_vouch_grounded_subject_observations: int
    false_vouch_fabricated_subject_observations: int
    # adopted analyzers (pure assembly)
    alibi_fabrication: AlibiFabricationReport
    effective_deflection: EffectiveDeflectionReport

    @model_validator(mode="after")
    def _validate(self) -> DeceptionInstrumentsReport:
        counts = (
            self.num_players,
            self.num_impostors,
            self.tasks_per_crewmate,
            self.games_total,
            self.meetings_total,
            self.impostor_accusations_total,
            self.frame_attempts,
            self.impostor_self_accusations,
            self.frame_attempt_meetings,
            self.crew_ejected_meetings,
            self.impostor_ejected_meetings,
            self.no_eject_meetings,
            self.vouch_observations_impostor,
            self.false_vouch_saw_player_observations,
            self.corroboration_claims_total,
            self.corroboration_claims_impostor,
            self.false_vouch_corroborations,
            self.false_vouches_total,
            self.false_vouch_subject_events,
            self.false_vouch_grounded,
            self.false_vouch_fabricated,
            self.false_vouch_grounded_subject_observations,
            self.false_vouch_fabricated_subject_observations,
        )
        if any(count < 0 for count in counts):
            raise ValueError("deception-instrument counts must be non-negative")

        if (
            self.frame_attempts
            + self.teammate_accusations.numerator
            + self.impostor_self_accusations
            != self.impostor_accusations_total
        ):
            raise ValueError(
                "accusation partition must sum to impostor_accusations_total: "
                f"{self.frame_attempts} + {self.teammate_accusations.numerator} + "
                f"{self.impostor_self_accusations} != "
                f"{self.impostor_accusations_total}"
            )
        if self.teammate_accusations.denominator != self.impostor_accusations_total:
            raise ValueError(
                "teammate_accusations.denominator must equal "
                "impostor_accusations_total: "
                f"{self.teammate_accusations.denominator} != "
                f"{self.impostor_accusations_total}"
            )
        if (
            self.crew_ejected_meetings
            + self.impostor_ejected_meetings
            + self.no_eject_meetings
            != self.meetings_total
        ):
            raise ValueError(
                "eject-outcome partition must sum to meetings_total: "
                f"{self.crew_ejected_meetings} + {self.impostor_ejected_meetings} "
                f"+ {self.no_eject_meetings} != {self.meetings_total}"
            )
        if self.frame_conversions.denominator != self.frame_attempt_meetings:
            raise ValueError(
                "frame_conversions.denominator must equal frame_attempt_meetings: "
                f"{self.frame_conversions.denominator} != "
                f"{self.frame_attempt_meetings}"
            )
        if self.frame_conversions.numerator > self.crew_ejected_meetings:
            raise ValueError(
                "frame_conversions.numerator cannot exceed crew_ejected_meetings: "
                f"{self.frame_conversions.numerator} > {self.crew_ejected_meetings}"
            )
        if (
            self.false_vouch_grounded + self.false_vouch_fabricated
            != self.false_vouch_subject_events
        ):
            raise ValueError(
                "grounded + fabricated must equal false_vouch_subject_events: "
                f"{self.false_vouch_grounded} + {self.false_vouch_fabricated} != "
                f"{self.false_vouch_subject_events}"
            )
        if (
            self.false_vouch_grounded_subject_observations
            + self.false_vouch_fabricated_subject_observations
            != self.false_vouch_saw_player_observations
        ):
            raise ValueError(
                "the observation-level companion join must partition "
                "false_vouch_saw_player_observations: "
                f"{self.false_vouch_grounded_subject_observations} + "
                f"{self.false_vouch_fabricated_subject_observations} != "
                f"{self.false_vouch_saw_player_observations}"
            )
        if self.false_vouch_grounded_subject_observations < self.false_vouch_grounded:
            raise ValueError(
                "every grounded subject event carries >=1 observation: "
                f"{self.false_vouch_grounded_subject_observations} < "
                f"{self.false_vouch_grounded}"
            )
        if (
            self.false_vouch_fabricated_subject_observations
            < self.false_vouch_fabricated
        ):
            raise ValueError(
                "every fabricated subject event carries >=1 observation: "
                f"{self.false_vouch_fabricated_subject_observations} < "
                f"{self.false_vouch_fabricated}"
            )
        if (
            self.false_vouch_saw_player_observations + self.false_vouch_corroborations
            != self.false_vouches_total
        ):
            raise ValueError(
                "false_vouches_total must equal saw_player + corroboration channels: "
                f"{self.false_vouch_saw_player_observations} + "
                f"{self.false_vouch_corroborations} != {self.false_vouches_total}"
            )

        _validate_rate(
            "false_vouch_saw_player_rate",
            self.false_vouch_saw_player_rate,
            self.false_vouch_saw_player_observations,
            self.vouch_observations_impostor,
        )
        _validate_rate(
            "false_vouch_corroboration_rate",
            self.false_vouch_corroboration_rate,
            self.false_vouch_corroborations,
            self.corroboration_claims_impostor,
        )
        _validate_rate(
            "false_vouch_grounded_share",
            self.false_vouch_grounded_share,
            self.false_vouch_grounded,
            self.false_vouch_subject_events,
        )
        return self


def _validate_rate(
    name: str, rate: float | None, numerator: int, denominator: int
) -> None:
    """Enforce the None-iff-zero-denominator sentinel and the ratio value."""

    if denominator == 0:
        if rate is not None:
            raise ValueError(f"{name} must be None when its denominator is 0")
        return
    if rate is None:
        raise ValueError(f"{name} must be defined when its denominator is positive")
    if abs(rate - numerator / denominator) > 1e-12:
        raise ValueError(
            f"{name} must equal numerator/denominator: "
            f"{rate} != {numerator}/{denominator}"
        )


def _rate_or_none(numerator: int, denominator: int) -> float | None:
    """``numerator/denominator`` or ``None`` when the denominator is 0."""

    return numerator / denominator if denominator else None


def _impostor_accusation_partition(
    meeting: _VJMeeting, roles: Mapping[PlayerId, Role]
) -> tuple[int, int, int, int]:
    """Partition impostor accusations into (total, frame, teammate, self).

    Mirrors the ``eval/alibi_fabrication.py:203-211`` author-role pattern: the
    author is the enclosing turn's speaker, resolved by subscript (fail-loud
    ``KeyError`` -- AGENTS.md "no silent fallbacks"). No living filter -- the
    §3.1 pins land without one.
    """

    total = frame = teammate = self_acc = 0
    for turn in meeting.transcript.turns:
        speaker = turn.speaker
        if roles[speaker] != "IMPOSTOR":
            continue
        for claim in turn.claims:
            if not isinstance(claim, AccusationClaim):
                continue
            total += 1
            against = claim.against
            if against == speaker:
                self_acc += 1
            elif roles[against] == "IMPOSTOR":
                teammate += 1
            else:
                frame += 1
    return total, frame, teammate, self_acc


def _impostor_accused_targets(
    meeting: _VJMeeting, roles: Mapping[PlayerId, Role]
) -> frozenset[PlayerId]:
    """Every player an impostor accused in this meeting (for frame conversion)."""

    targets: set[PlayerId] = set()
    for turn in meeting.transcript.turns:
        if roles[turn.speaker] != "IMPOSTOR":
            continue
        for claim in turn.claims:
            if isinstance(claim, AccusationClaim):
                targets.add(claim.against)
    return frozenset(targets)


def _is_frame_conversion(meeting: _VJMeeting, roles: Mapping[PlayerId, Role]) -> bool:
    """A crewmate ejected whom an impostor accused this meeting (meeting-level)."""

    if meeting.outcome != "EJECTED" or meeting.ejected is None:
        return False
    if roles[meeting.ejected] != "CREWMATE":
        return False
    return meeting.ejected in _impostor_accused_targets(meeting, roles)


def _impostor_vouch_census(
    meeting: _VJMeeting, roles: Mapping[PlayerId, Role]
) -> tuple[int, int]:
    """Impostor ``saw_player`` vouches: (observations, co-impostor false vouches).

    Mirrors ``eval/funnel.py:1404`` ``_vouch_census`` with an added
    living-impostor speaker filter: a living impostor's spoken
    :class:`~meetings.schemas.SawPlayerObservation` placing ANOTHER living
    player. The false-vouch subset is the co-impostor placements.
    """

    observations = 0
    false_vouches = 0
    for turn in meeting.transcript.turns:
        speaker = turn.speaker
        if roles[speaker] != "IMPOSTOR" or speaker not in meeting.living:
            continue
        for obs in turn.observations:
            if (
                isinstance(obs, SawPlayerObservation)
                and obs.subject != speaker
                and obs.subject in meeting.living
            ):
                observations += 1
                if roles[obs.subject] == "IMPOSTOR":
                    false_vouches += 1
    return observations, false_vouches


def _corroboration_census(
    meeting: _VJMeeting, roles: Mapping[PlayerId, Role]
) -> tuple[int, int, int]:
    """Corroboration channel: (raw total, impostor denominator, co-impostor subset).

    ``raw total`` counts every :class:`~meetings.schemas.CorroborationClaim` over
    ALL turns; the impostor denominator is a living impostor supporting another
    living player; the co-impostor subset is the false-vouch numerator.
    """

    total = 0
    impostor_denom = 0
    false_vouches = 0
    for turn in meeting.transcript.turns:
        speaker = turn.speaker
        is_living_impostor = roles[speaker] == "IMPOSTOR" and speaker in meeting.living
        for claim in turn.claims:
            if not isinstance(claim, CorroborationClaim):
                continue
            total += 1
            if (
                is_living_impostor
                and claim.supports != speaker
                and claim.supports in meeting.living
            ):
                impostor_denom += 1
                if roles[claim.supports] == "IMPOSTOR":
                    false_vouches += 1
    return total, impostor_denom, false_vouches


def _restricted_grounded_subjects(
    meeting: _VJMeeting, roles: Mapping[PlayerId, Role]
) -> frozenset[PlayerId]:
    """Grounded-vouch subjects via the production chokepoint, impostor records only.

    Mirrors ``eval/funnel.py:1430`` ``_grounded_vouch_set`` but restricts the
    sighting-records mapping to impostor speakers: the false-vouch split asks
    whether the IMPOSTOR's placement is backed by the impostor's OWN records, so
    a co-impostor subject grounded only through a crew speaker's records must NOT
    count. The restriction is an input filter -- all grounding semantics remain
    :func:`meetings.transcript.grounded_vouch_subjects`'s.
    """

    return grounded_vouch_subjects(
        meeting.transcript,
        sighting_records={
            pid: recs
            for pid, recs in meeting.sighting_records_by_speaker.items()
            if roles[pid] == "IMPOSTOR"
        },
        roster=meeting.living,
        trigger_kind=meeting.trigger_kind,
    )


def _grounded_split(
    meeting: _VJMeeting, roles: Mapping[PlayerId, Role]
) -> tuple[int, int, int, int, int]:
    """Per-meeting false-vouch grounded split, both granularities.

    Returns ``(subject_events, grounded, fabricated,
    grounded_subject_observations, fabricated_subject_observations)``.

    Chokepoint granularity is per-meeting-per-subject: each co-impostor subject a
    living impostor false-vouches for is one subject event, classified grounded
    iff it is in the impostor-restricted grounded set, else fabricated. The split
    partitions subject events, NOT the observation count -- the production
    chokepoint dedups subjects internally and returns a subject set, so repeat
    placements of the same teammate in one meeting are one event here (see the
    module docstring, predicate 8, for why no per-observation verdict is
    derivable without the re-derivation the DoD forbids).

    The last two counts are the observation-level COMPANION join: every false
    vouch observation (the ``false_vouch_saw_player_observations`` predicate),
    bucketed by its SUBJECT's chokepoint verdict. They partition the observation
    numerator exactly, reconciling it with the subject-event split downstream.
    They are a join on the subject verdict, NOT per-observation grounding: a
    duplicate placement inherits its subject's classification.
    """

    observations_by_subject: dict[PlayerId, int] = {}
    for turn in meeting.transcript.turns:
        speaker = turn.speaker
        if roles[speaker] != "IMPOSTOR" or speaker not in meeting.living:
            continue
        for obs in turn.observations:
            if (
                isinstance(obs, SawPlayerObservation)
                and obs.subject != speaker
                and obs.subject in meeting.living
                and roles[obs.subject] == "IMPOSTOR"
            ):
                observations_by_subject[obs.subject] = (
                    observations_by_subject.get(obs.subject, 0) + 1
                )
    if not observations_by_subject:
        return 0, 0, 0, 0, 0
    grounded_set = _restricted_grounded_subjects(meeting, roles)
    grounded = sum(1 for subject in observations_by_subject if subject in grounded_set)
    grounded_obs = sum(
        count
        for subject, count in observations_by_subject.items()
        if subject in grounded_set
    )
    total_obs = sum(observations_by_subject.values())
    return (
        len(observations_by_subject),
        grounded,
        len(observations_by_subject) - grounded,
        grounded_obs,
        total_obs - grounded_obs,
    )


def compute_deception_instruments(sample_dir: Path) -> DeceptionInstrumentsReport:
    """Fold a replay set's committed bytes into the Tier-A deception diagnostics.

    Pure and offline (DESIGN.md §11.3). Walks every game through the
    memory-augmented :func:`eval.funnel._walk_set_vj` (the only walk that
    reconstructs the per-speaker sighting records the grounded-vouch chokepoint
    needs), folds the accusation / vouch / corroboration census, then assembles
    the two adopted analyzers. Fail-loud if the walk's meeting count disagrees
    with the assembled report's.
    """

    walks: list[_VJGameWalk]
    walks, num_players, num_impostors, tasks_per_crewmate = _walk_set_vj(sample_dir)

    meetings_total = 0
    impostor_accusations_total = 0
    frame_attempts = 0
    teammate_accusations = 0
    impostor_self_accusations = 0
    frame_attempt_meetings = 0
    frame_conversions = 0
    crew_ejected_meetings = 0
    impostor_ejected_meetings = 0
    no_eject_meetings = 0
    vouch_observations_impostor = 0
    false_vouch_saw_player_observations = 0
    corroboration_claims_total = 0
    corroboration_claims_impostor = 0
    false_vouch_corroborations = 0
    false_vouch_subject_events = 0
    false_vouch_grounded = 0
    false_vouch_fabricated = 0
    false_vouch_grounded_subject_observations = 0
    false_vouch_fabricated_subject_observations = 0

    for walk in walks:
        roles = walk.roles
        for meeting in walk.meetings:
            meetings_total += 1

            total, frame, teammate, self_acc = _impostor_accusation_partition(
                meeting, roles
            )
            impostor_accusations_total += total
            frame_attempts += frame
            teammate_accusations += teammate
            impostor_self_accusations += self_acc
            if frame > 0:
                frame_attempt_meetings += 1
            if _is_frame_conversion(meeting, roles):
                frame_conversions += 1

            if meeting.outcome == "EJECTED":
                assert meeting.ejected is not None  # MeetingResult invariant
                if roles[meeting.ejected] == "IMPOSTOR":
                    impostor_ejected_meetings += 1
                else:
                    crew_ejected_meetings += 1
            else:
                no_eject_meetings += 1

            observations, false_saw = _impostor_vouch_census(meeting, roles)
            vouch_observations_impostor += observations
            false_vouch_saw_player_observations += false_saw

            corr_total, corr_impostor, corr_false = _corroboration_census(
                meeting, roles
            )
            corroboration_claims_total += corr_total
            corroboration_claims_impostor += corr_impostor
            false_vouch_corroborations += corr_false

            events, grounded, fabricated, grounded_obs, fabricated_obs = (
                _grounded_split(meeting, roles)
            )
            false_vouch_subject_events += events
            false_vouch_grounded += grounded
            false_vouch_fabricated += fabricated
            false_vouch_grounded_subject_observations += grounded_obs
            false_vouch_fabricated_subject_observations += fabricated_obs

    report = assemble_tournament_report(sample_dir)
    report_meetings_total = sum(len(game.meetings) for game in report.games)
    if report_meetings_total != meetings_total:
        raise ValueError(
            "walk meeting count disagrees with the assembled report's: "
            f"{meetings_total} != {report_meetings_total}"
        )
    alibi = compute_alibi_fabrication_rate(report)
    deflection = compute_effective_deflection(report)

    false_vouches_total = (
        false_vouch_saw_player_observations + false_vouch_corroborations
    )
    return DeceptionInstrumentsReport(
        replay_set_dir=str(sample_dir),
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        games_total=len(walks),
        meetings_total=meetings_total,
        impostor_accusations_total=impostor_accusations_total,
        frame_attempts=frame_attempts,
        impostor_self_accusations=impostor_self_accusations,
        teammate_accusations=_rare_event_cell(
            teammate_accusations, impostor_accusations_total
        ),
        frame_attempt_meetings=frame_attempt_meetings,
        frame_conversions=_rare_event_cell(frame_conversions, frame_attempt_meetings),
        crew_ejected_meetings=crew_ejected_meetings,
        impostor_ejected_meetings=impostor_ejected_meetings,
        no_eject_meetings=no_eject_meetings,
        vouch_observations_impostor=vouch_observations_impostor,
        false_vouch_saw_player_observations=false_vouch_saw_player_observations,
        false_vouch_saw_player_rate=_rate_or_none(
            false_vouch_saw_player_observations, vouch_observations_impostor
        ),
        corroboration_claims_total=corroboration_claims_total,
        corroboration_claims_impostor=corroboration_claims_impostor,
        false_vouch_corroborations=false_vouch_corroborations,
        false_vouch_corroboration_rate=_rate_or_none(
            false_vouch_corroborations, corroboration_claims_impostor
        ),
        false_vouches_total=false_vouches_total,
        false_vouch_subject_events=false_vouch_subject_events,
        false_vouch_grounded=false_vouch_grounded,
        false_vouch_fabricated=false_vouch_fabricated,
        false_vouch_grounded_share=_rate_or_none(
            false_vouch_grounded, false_vouch_subject_events
        ),
        false_vouch_grounded_subject_observations=(
            false_vouch_grounded_subject_observations
        ),
        false_vouch_fabricated_subject_observations=(
            false_vouch_fabricated_subject_observations
        ),
        alibi_fabrication=alibi,
        effective_deflection=deflection,
    )


__all__ = [
    "DeceptionInstrumentsReport",
    "RareEventCell",
    "compute_deception_instruments",
]
