"""The conviction-economy training table — evidence supply → conviction (Task 18.15).

For every committed meeting this module reduces the 15.11 meeting table
(:mod:`training.surrogate.dataset` — the hash-verified engine walk, imported and
never forked) to ONE per-meeting row: the pre-meeting evidence-supply features a
training-time runner can honestly reconstruct at ``run_meeting`` time, joined to
the two labels the phase's referee economy gates — contradiction flags minted and
testimony-backed conversion (audits/audit-phase-18-planning.md §2.3).

**The feature fence (the live-parity argument, re-run).** Every feature must be
derivable from the ``MeetingRunner.run_meeting`` inputs ``(meeting_id, trigger,
state, agents)`` at trigger time (``orchestrator/game.py::MeetingRunner``):

* ``alive_count`` — the living roster off ``state.players``.
* ``meeting_index`` — parsed off the orchestrator-formatted ``meeting_id``
  (the ``training/surrogate/runner.py`` precedent).
* ``max_suspicion`` / ``mean_suspicion`` / ``suspicion_margin`` /
  ``cells_at_gate`` — aggregates over the non-self (voter, candidate) belief
  cells, live via each agent's ``suspicion_graph_for_meeting()``. Offline they
  read the table's ``belief_suspicion`` column, whose parity with the production
  fold is MEASURED (0 raw mismatches) by
  :func:`training.surrogate.dataset.measure_belief_render_parity` — the same
  walk re-validation this task's fit entry gates on. The known divergence is the
  graduated J1 render clamp (live serves the CLAMPED ``SuspicionEntry.suspicion``);
  it is measured per corpus and quoted in
  ``training/reports/report-conviction-model.md``, never assumed away.
* ``vent_witness_pairs`` / ``vent_witnessed_candidates`` — the voter-local
  witnessed-vent pins, live via each agent's typed
  ``vent_witness_records_for_meeting()`` channel naming the candidate.
* ``kill_pin_pairs`` / ``kill_pinned_candidates`` and ``body_proximity_pairs``
  / ``body_proximity_candidates`` — the voter-local witnessed-kill and §6.3
  Rule-1 body-proximity pins, with the GAME-LONG semantics of exactly the
  channels the task contract's section ref defines as live-reconstructable
  (the honest ceiling's ``proximity_legible`` flag sets,
  ``training/surrogate/fidelity.py:213-243``). Their live substrate is the
  agent's OWN append-only episodic store (audit §2.3 [VERIFIED]): the
  kill-stamped first-hand ``saw_player`` rows and the body/sighting rows the
  §6.3 Rule-1 reconstruction reads persist for the whole game. Precision on
  the serving surface: the ``SuspicionEntry.kill_or_vent_pin`` /
  ``body_proximity`` provenance channels carry ONLY pins minted since the
  previous meeting — the boundary roll folds older pins into the
  undifferentiated ``carried_hard`` bucket
  (``agents/memory/beliefs.py::SuspicionProvenance.carried``) — and the raw
  kill/body episodic rows are not yet projected onto a ``*_for_meeting``
  accessor (``sighting_records_for_meeting`` deliberately excludes
  incriminating-action rows), so the runner-side consumer needs the
  ``vent_witness_records_for_meeting()`` twin for kill/body records — a
  firewall-clean one-accessor seam that belongs to the 18.16 integration,
  recorded there, never papered over here.

Columns a live runner CANNOT reconstruct are excluded BY DESIGN, not oversight:
the contradiction-flag structure and ``contradiction_lift`` need THIS meeting's
transcript (they are the LABEL side here, never features); the omniscient window
stats (``witnessed`` / ``isolation`` / ``seen_at_kill`` / ``task_submissions`` /
``move_count``) need the inter-meeting event history the runner never sees; and
raw first-hand sighting-record supply, though live-servable via
``sighting_records_for_meeting()``, has no verified offline mirror in the 15.11
table (the table's co-presence counts are omniscient, not per-voter episodic),
so it enters only through the belief scalar's corroboration folds rather than
being fitted against an unverified reconstruction.
:data:`CONVICTION_FEATURE_PROVENANCE` records the per-feature derivation and the
committed provenance test asserts it feature by feature; the committed poison
test proves the builder never reads a fenced column.

**The labels (mirrored, never imported).** The two labels are exactly the
quantities the 15.2 referee gates — the Goodhart-adjacent seam — so this module
MIRRORS the ``eval/watchability.py`` assembly from the recorded bytes and never
imports ``eval.*`` (the AST firewall the task contract names; the committed
firewall test enforces it):

* ``flags_minted`` — the transcript-re-derived census PLUS the persisted
  ``vent_sighting`` subset: ``len(detect_contradictions(transcript,
  roster=frozenset(ballot voters)))`` + the recorded ``vent_sighting`` flags
  (the re-derivation can never mint one — the vent grounding channel is
  private). Mirrors ``eval/meeting_quality.py::compute_supply_gauges`` +
  ``eval/watchability.py::_persisted_vent_flag_count``; the detector itself IS
  the production :func:`meetings.transcript.detect_contradictions`, imported —
  only the eval-layer assembly is mirrored.
* ``conversion_attempted`` / ``conversion_converted`` — the observation-BACKED
  conversion (``eval/watchability.py::_observation_backed_impostors`` + the
  subject-aware Task-15.19 backing bit): a true impostor named by a non-self
  ``AccusationClaim`` where some accusing turn ALSO carries a first-hand
  ``SawPlayerObservation`` / ``SawVentObservation`` whose subject IS the
  accused; converted when the meeting ejects exactly that subject. Roles ground
  truth comes from the deterministic engine re-seed
  (:func:`orchestrator.seeder.seed_initial_state` — the same recipe
  ``eval.validity.roles_by_seed`` runs; raw replays are role-free by firewall
  design).

Each row also carries the ceiling channel: ``ceiling_reachable`` — whether the
ejected target is the STRICT argmax of the best-case reconstructed
physical+belief suspicion (:attr:`training.surrogate.fidelity.MeetingView.
recon_suspicion`), so ``voice_driven_share`` re-measures on ANY population of
rows (the fidelity harness quotes it on the held-out split as the structural
denominator of the conversion bar).

The builder takes ANY replay-set directory, reads a committed ``splits.json``
when present (the surrogate's :func:`~training.surrogate.dataset.load_splits`
machinery), and is pure and offline: no network, no LLM, no ``eval.*`` import.

Public surface (stable — downstream tasks import these):
:data:`CONVICTION_FEATURE_NAMES`, :data:`CONVICTION_FEATURE_PROVENANCE`,
:class:`ConvictionMeetingRow`, :class:`ConvictionTable`,
:class:`ConvictionWalkGateError`, :func:`build_conviction_table`,
:func:`require_clean_walk`.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict, model_validator

from engine.entities import PlayerId, Role
from engine.world import load_canonical_map
from meetings.constants import DEFAULT_SKIP_CONFIDENCE_THRESHOLD
from meetings.schemas import (
    AccusationClaim,
    MeetingTranscript,
    SawPlayerObservation,
    SawVentObservation,
)
from meetings.transcript import detect_contradictions
from orchestrator.replay import MeetingReplayEntry, read_all_entries
from orchestrator.seeder import seed_initial_state
from training.surrogate.dataset import (
    BeliefRenderParity,
    MeetingTableRow,
    SurrogateSplits,
    build_meeting_table,
)
from training.surrogate.fidelity import MeetingView, build_meeting_views

# The per-meeting feature order (serialized into the weights artifact and
# validated on load — a drifted layout fails loud instead of silently
# mis-multiplying, the ballots.py convention). See the module docstring for the
# live derivation of each; :data:`CONVICTION_FEATURE_PROVENANCE` records it
# machine-readably and the committed provenance test asserts it.
CONVICTION_FEATURE_NAMES: Final[tuple[str, ...]] = (
    "alive_count",
    "meeting_index",
    "max_suspicion",
    "mean_suspicion",
    "suspicion_margin",
    "cells_at_gate",
    "vent_witness_pairs",
    "vent_witnessed_candidates",
    "kill_pin_pairs",
    "kill_pinned_candidates",
    "body_proximity_pairs",
    "body_proximity_candidates",
)

# The run_meeting-time input universe (orchestrator/game.py::MeetingRunner):
# every feature's declared provenance must draw ONLY from these sources. The
# ``agents:*`` entries name the agent-side channel: the two ``*_for_meeting``
# accessors that exist today, plus the agent's OWN append-only episodic
# first-hand records (kill-stamped ``saw_player`` rows, body/sighting rows) —
# the audit-§2.3 substrate whose typed ``*_for_meeting`` projection (the vent
# accessor's kill/body twin) is the 18.16 runner-side seam (see the module
# docstring's precision note). Never a transcript-derived source: the
# vocabulary has no entry for one.
CONVICTION_PROVENANCE_SOURCES: Final[frozenset[str]] = frozenset(
    {
        "meeting_id",
        "trigger",
        "state",
        "agents:suspicion_graph_for_meeting",
        "agents:vent_witness_records_for_meeting",
        "agents:episodic_first_hand_records",
    }
)

# Feature -> the run_meeting-time sources it derives from. Asserted complete and
# fence-compliant by the committed provenance test (feature-by-feature, per the
# task hint — never just this docstring).
CONVICTION_FEATURE_PROVENANCE: Final[Mapping[str, tuple[str, ...]]] = {
    "alive_count": ("state",),
    "meeting_index": ("meeting_id",),
    "max_suspicion": ("agents:suspicion_graph_for_meeting",),
    "mean_suspicion": ("agents:suspicion_graph_for_meeting",),
    "suspicion_margin": ("agents:suspicion_graph_for_meeting",),
    "cells_at_gate": ("agents:suspicion_graph_for_meeting",),
    "vent_witness_pairs": ("agents:vent_witness_records_for_meeting",),
    "vent_witnessed_candidates": ("agents:vent_witness_records_for_meeting",),
    # Game-long voter-local pins off the agent's own episodic store (the
    # module docstring's precision note: the SuspicionEntry channels carry
    # only the current window's pins, so the episodic records are the honest
    # game-long source; their typed projection is the 18.16 runner-side seam).
    "kill_pin_pairs": ("agents:episodic_first_hand_records",),
    "kill_pinned_candidates": ("agents:episodic_first_hand_records",),
    "body_proximity_pairs": ("agents:episodic_first_hand_records",),
    "body_proximity_candidates": ("agents:episodic_first_hand_records",),
}

# The ONLY 15.11 table columns the feature builder may read (the fence's
# positive statement; the committed poison test derives the forbidden set as
# everything else, so a future table column lands fenced by default).
# Identity/grouping fields: seed, game_id, meeting_id, meeting_index, tick,
# voter, candidates. CandidateFeatures fields: candidate, is_self,
# belief_suspicion, witnessed_kill, witnessed_vent, body_proximity.
CONVICTION_READABLE_ROW_FIELDS: Final[frozenset[str]] = frozenset(
    {"seed", "game_id", "meeting_id", "meeting_index", "tick", "voter", "candidates"}
)
CONVICTION_READABLE_CANDIDATE_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "candidate",
        "is_self",
        "belief_suspicion",
        "witnessed_kill",
        "witnessed_vent",
        "body_proximity",
    }
)


class ConvictionWalkGateError(RuntimeError):
    """The 17.10 walk re-validation failed — no fit over this set can be trusted.

    Raised by :func:`require_clean_walk` when the hand-mirrored belief fold
    disagrees with the production fold on ANY raw cell (``raw_mismatches`` /
    ``trust_mismatches`` nonzero). The dataset walk must re-validate against
    production folds BEFORE any fit (the task contract's 17.10 discipline);
    a drifted walk silently fitted would be exactly the corruption the
    discipline exists to catch.
    """


def require_clean_walk(parity: BeliefRenderParity) -> BeliefRenderParity:
    """Gate a fit on the 17.10 walk re-validation: 0 raw mismatches, or raise.

    The J1 render-clamp divergence (``j1_divergent_cells``) is a MEASURED,
    reported quantity — never a failure (the live runner serves the clamped
    render by design); only a raw fold mismatch is corruption. Returns the
    parity unchanged so callers thread the measured numbers into the report.
    """

    if parity.raw_mismatches or parity.trust_mismatches:
        raise ConvictionWalkGateError(
            f"{parity.replay_set_dir}: the hand-mirrored belief fold diverged "
            f"from the production fold ({parity.raw_mismatches} raw / "
            f"{parity.trust_mismatches} trust mismatches over "
            f"{parity.cells_compared} cells, max |Δ| "
            f"{parity.max_raw_abs_delta}) — refusing to fit on a drifted walk "
            "(the 17.10 discipline)"
        )
    return parity


class ConvictionMeetingRow(BaseModel):
    """One meeting's conviction-economy training row (Task 18.15; frozen).

    ``features`` maps exactly :data:`CONVICTION_FEATURE_NAMES` (order preserved
    for byte-stable dumps) — the run_meeting-reconstructable evidence supply.
    ``flags_minted`` / ``conversion_*`` are the mirrored referee labels (module
    docstring); ``rederived_flags`` + ``persisted_vent_flags`` decompose the
    flag label's two disjoint sources. ``ceiling_reachable`` is the label-side
    ceiling channel: whether the ejected target is the strict argmax of the
    best-case reconstructed physical+belief suspicion (always ``False`` on a
    SKIP meeting), so ``voice_driven_share`` re-measures on any row population.
    Labels and the ceiling channel are NEVER model inputs — the committed
    poison test proves the feature builder cannot see them.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    seed: int
    game_id: str
    meeting_id: str
    meeting_index: int
    tick: int
    features: Mapping[str, float]
    # Labels (the referee's quantities, mirrored — never features).
    flags_minted: int
    rederived_flags: int
    persisted_vent_flags: int
    conversion_attempted: int
    conversion_converted: int
    testimony_backed_conversion: bool
    # The ceiling channel (label-side; the conversion bar's denominator).
    is_ejection: bool
    ceiling_reachable: bool

    @model_validator(mode="after")
    def _feature_layout_matches(self) -> "ConvictionMeetingRow":
        keys = tuple(self.features)
        if keys != CONVICTION_FEATURE_NAMES:
            raise ValueError(
                f"features keys {keys} != CONVICTION_FEATURE_NAMES "
                f"{CONVICTION_FEATURE_NAMES} (order included — the layout is "
                "the artifact contract)"
            )
        if self.flags_minted != self.rederived_flags + self.persisted_vent_flags:
            raise ValueError(
                f"flags_minted {self.flags_minted} != rederived "
                f"{self.rederived_flags} + persisted vent "
                f"{self.persisted_vent_flags} — the two sources are disjoint "
                "by construction"
            )
        if self.conversion_converted > self.conversion_attempted:
            raise ValueError(
                f"conversion_converted {self.conversion_converted} > attempted "
                f"{self.conversion_attempted}"
            )
        if self.testimony_backed_conversion != (self.conversion_converted > 0):
            raise ValueError(
                "testimony_backed_conversion must equal conversion_converted > 0"
            )
        if self.ceiling_reachable and not self.is_ejection:
            raise ValueError("a SKIP meeting has no ejected target to reach")
        return self


class ConvictionTable(BaseModel):
    """The per-meeting conviction table over one replay set (frozen).

    ``rows`` is every recorded meeting, sorted by ``(seed, meeting_index)``.
    The census aggregates are derived from the rows and asserted against the
    15.11 table's report-backed counts at build time. ``model_dump_json()`` is
    byte-stable across rebuilds (the determinism pin). ``seeds`` is EVERY
    recorded game — including no-meeting games — so split validation partitions
    the same universe the surrogate machinery validates.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    replay_set_dir: str
    num_players: int
    num_impostors: int
    tasks_per_crewmate: int
    games_total: int
    meetings_total: int
    ejections_total: int
    conversions_total: int
    conversion_attempts_total: int
    flags_minted_total: int
    seeds: tuple[int, ...]
    splits: SurrogateSplits | None
    rows: tuple[ConvictionMeetingRow, ...]


def _roles_for_seed(
    seed: int,
    *,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
) -> dict[PlayerId, Role]:
    """Roles ground truth via the deterministic engine re-seed.

    The same recipe ``eval.validity.roles_by_seed`` runs (never imported — the
    AST firewall): raw replays are role-free by firewall design, and the seeder
    is a pure function of ``(seed, roster knobs)``, so the re-seeded roles are
    byte-identical to the recording's.
    """

    state = seed_initial_state(
        seed=seed,
        game_map=load_canonical_map(),
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    return {player_id: player.role for player_id, player in state.players.items()}


def _observation_backed_impostor_subjects(
    transcript: MeetingTranscript, roles: Mapping[PlayerId, Role]
) -> frozenset[PlayerId]:
    """True impostors carrying an observation-BACKED accusation (mirrored).

    Mirrors ``eval/watchability.py::_observation_backed_impostors`` +
    ``_subject_has_observation_backed_accusation`` + ``_testimony_vehicle`` on
    the LIVE (subject-aware, Task-15.19) predicate, from the recorded transcript
    bytes: a subject enters the accused universe through a NON-self
    ``AccusationClaim`` edge; it is BACKED when some turn both accuses it and
    carries a first-hand ``SawPlayerObservation`` / ``SawVentObservation``
    whose subject IS the accused (a grounded observation about someone else
    never backs — the exploit 15.19 closed; a ``FoundBodyObservation`` names a
    dead victim and structurally cannot back). Only true impostors count — the
    referee's conversion is deception that convicts the RIGHT target.
    """

    accused = {
        claim.against
        for turn in transcript.turns
        for claim in turn.claims
        if isinstance(claim, AccusationClaim) and claim.against != turn.speaker
    }
    backed: set[PlayerId] = set()
    for subject in sorted(accused):
        if roles.get(subject) != "IMPOSTOR":
            continue
        for turn in transcript.turns:
            accuses = any(
                isinstance(claim, AccusationClaim) and claim.against == subject
                for claim in turn.claims
            )
            if not accuses:
                continue
            if any(
                isinstance(obs, (SawPlayerObservation, SawVentObservation))
                and obs.subject == subject
                for obs in turn.observations
            ):
                backed.add(subject)
                break
    return frozenset(backed)


def _meeting_labels(
    entry: MeetingReplayEntry, roles: Mapping[PlayerId, Role]
) -> tuple[int, int, int, int]:
    """One meeting's ``(rederived_flags, persisted_vent_flags, attempted, converted)``.

    The flag census re-derives under the ballot-voter roster exactly as the
    referee's supply gauge does (``eval/meeting_quality.py::compute_supply_gauges``
    — mirrored, with the production :func:`detect_contradictions` imported), then
    the persisted ``vent_sighting`` flags merge in from the recorded
    contradictions (the ONLY read of them — the re-derivation cannot mint a vent
    flag; the two sets are disjoint, so no double count). Conversion follows
    :func:`_observation_backed_impostor_subjects`; a meeting ejects at most one
    player, so ``converted`` is 0 or 1.
    """

    roster = frozenset(ballot.voter for ballot in entry.ballots)
    rederived = len(detect_contradictions(entry.transcript, roster=roster))
    persisted_vent = sum(
        1 for flag in entry.contradictions if flag.kind == "vent_sighting"
    )
    backed = _observation_backed_impostor_subjects(entry.transcript, roles)
    attempted = len(backed)
    converted = int(
        entry.ejected_player_id is not None and entry.ejected_player_id in backed
    )
    return rederived, persisted_vent, attempted, converted


def _meeting_features(rows: Sequence[MeetingTableRow]) -> dict[str, float]:
    """Reduce one meeting's (meeting, voter) rows to the fenced feature vector.

    Reads ONLY :data:`CONVICTION_READABLE_ROW_FIELDS` /
    :data:`CONVICTION_READABLE_CANDIDATE_FIELDS` (the committed poison test
    proves it). All aggregates run over the NON-self (voter, candidate) cells —
    a voter holds no belief row about itself (the table pins the self cell at
    the neutral prior and never stamps a self pin), exactly the cells a live
    runner reads off each agent's own accessors. Iteration follows the table's
    sorted row/candidate order, so float summation is deterministic.
    """

    sample = rows[0]
    alive_count = float(len(sample.candidates))
    suspicions: list[float] = []
    per_candidate_max: dict[PlayerId, float] = {}
    cells_at_gate = 0
    vent_pairs = 0
    kill_pairs = 0
    proximity_pairs = 0
    vent_candidates: set[PlayerId] = set()
    kill_candidates: set[PlayerId] = set()
    proximity_candidates: set[PlayerId] = set()
    for row in rows:
        for feat in row.candidates:
            if feat.is_self:
                continue
            suspicion = feat.belief_suspicion
            suspicions.append(suspicion)
            prior = per_candidate_max.get(feat.candidate)
            if prior is None or suspicion > prior:
                per_candidate_max[feat.candidate] = suspicion
            if suspicion >= DEFAULT_SKIP_CONFIDENCE_THRESHOLD:
                cells_at_gate += 1
            if feat.witnessed_vent:
                vent_pairs += 1
                vent_candidates.add(feat.candidate)
            if feat.witnessed_kill:
                kill_pairs += 1
                kill_candidates.add(feat.candidate)
            if feat.body_proximity:
                proximity_pairs += 1
                proximity_candidates.add(feat.candidate)
    if not suspicions:
        raise ValueError(
            f"meeting {sample.seed}:{sample.meeting_id} has no non-self belief "
            "cells — a recorded meeting always seats at least two voters"
        )
    leads = sorted(per_candidate_max.values(), reverse=True)
    margin = leads[0] - leads[1] if len(leads) >= 2 else 0.0
    return {
        "alive_count": alive_count,
        "meeting_index": float(sample.meeting_index),
        "max_suspicion": max(suspicions),
        "mean_suspicion": sum(suspicions) / len(suspicions),
        "suspicion_margin": margin,
        "cells_at_gate": float(cells_at_gate),
        "vent_witness_pairs": float(vent_pairs),
        "vent_witnessed_candidates": float(len(vent_candidates)),
        "kill_pin_pairs": float(kill_pairs),
        "kill_pinned_candidates": float(len(kill_candidates)),
        "body_proximity_pairs": float(proximity_pairs),
        "body_proximity_candidates": float(len(proximity_candidates)),
    }


def _is_strict_recon_leader(view: MeetingView) -> bool:
    """Whether the ejected target strictly leads the reconstructed suspicion.

    The per-meeting form of the honest ceiling's reachability read
    (``training/surrogate/fidelity.py::compute_honest_ceiling`` — its aggregate
    stays the surrogate's; this row-level bit lets ``voice_driven_share``
    re-measure on any population of conviction rows). ``False`` on a SKIP
    meeting and on a flat tie (a tie is not uniquely rankable).
    """

    target = view.ejected
    if target is None:
        return False
    target_score = view.recon_suspicion[target]
    return all(
        view.recon_suspicion[cand] < target_score
        for cand in view.candidates
        if cand != target
    )


def build_conviction_table(
    sample_dir: Path, *, splits_path: Path | None = None
) -> ConvictionTable:
    """Build the per-meeting conviction table for a replay-set directory.

    Runs the 15.11 hash-verified walk (:func:`training.surrogate.dataset.
    build_meeting_table` — every recorded tick and meeting state-hash verified,
    fail-loud on drift), reduces each meeting's rows to the fenced feature
    vector, and joins the mirrored referee labels read off the raw meeting
    replay entries. A meeting present in one source but not the other fails
    loud rather than silently under-building. Pure and offline; reads a
    committed ``splits.json`` when present.
    """

    table = build_meeting_table(sample_dir, splits_path=splits_path)

    rows_by_meeting: dict[tuple[int, str], list[MeetingTableRow]] = defaultdict(list)
    for row in table.rows:
        rows_by_meeting[(row.seed, row.meeting_id)].append(row)

    reachable_by_meeting = {
        (view.seed, view.meeting_id): _is_strict_recon_leader(view)
        for view in build_meeting_views(table)
    }

    conviction_rows: list[ConvictionMeetingRow] = []
    for seed in table.seeds:
        seed_meetings = [key for key in rows_by_meeting if key[0] == seed]
        entries = [
            entry
            for entry in read_all_entries(sample_dir / f"replay-seed-{seed}.jsonl")
            if isinstance(entry, MeetingReplayEntry)
        ]
        if len(entries) != len(seed_meetings):
            raise ValueError(
                f"{sample_dir}: seed {seed} carries {len(entries)} recorded "
                f"meetings but the reconstructed table has {len(seed_meetings)} "
                "— the two sources must join 1:1"
            )
        if not entries:
            continue
        roles = _roles_for_seed(
            seed,
            num_players=table.num_players,
            num_impostors=table.num_impostors,
            tasks_per_crewmate=table.tasks_per_crewmate,
        )
        for entry in entries:
            key = (seed, entry.meeting_id)
            meeting_rows = rows_by_meeting.get(key)
            if not meeting_rows:
                raise ValueError(
                    f"{sample_dir}: recorded meeting {entry.meeting_id!r} of seed "
                    f"{seed} has no reconstructed table rows — the two sources "
                    "must join 1:1"
                )
            rederived, persisted_vent, attempted, converted = _meeting_labels(
                entry, roles
            )
            sample = meeting_rows[0]
            conviction_rows.append(
                ConvictionMeetingRow(
                    seed=seed,
                    game_id=sample.game_id,
                    meeting_id=entry.meeting_id,
                    meeting_index=sample.meeting_index,
                    tick=sample.tick,
                    features=_meeting_features(meeting_rows),
                    flags_minted=rederived + persisted_vent,
                    rederived_flags=rederived,
                    persisted_vent_flags=persisted_vent,
                    conversion_attempted=attempted,
                    conversion_converted=converted,
                    testimony_backed_conversion=converted > 0,
                    is_ejection=entry.ejected_player_id is not None,
                    ceiling_reachable=reachable_by_meeting[key],
                )
            )

    conviction_rows.sort(key=lambda row: (row.seed, row.meeting_index))
    if len(conviction_rows) != table.meetings_total:
        raise ValueError(
            f"{sample_dir}: built {len(conviction_rows)} conviction rows != "
            f"{table.meetings_total} reconstructed meetings (join rate < 100%)"
        )
    ejections = sum(1 for row in conviction_rows if row.is_ejection)
    if ejections != table.ejections_total:
        raise ValueError(
            f"{sample_dir}: conviction rows carry {ejections} ejections != the "
            f"table's report-backed {table.ejections_total}"
        )

    return ConvictionTable(
        replay_set_dir=str(sample_dir),
        num_players=table.num_players,
        num_impostors=table.num_impostors,
        tasks_per_crewmate=table.tasks_per_crewmate,
        games_total=table.games_total,
        meetings_total=table.meetings_total,
        ejections_total=table.ejections_total,
        conversions_total=sum(row.conversion_converted for row in conviction_rows),
        conversion_attempts_total=sum(
            row.conversion_attempted for row in conviction_rows
        ),
        flags_minted_total=sum(row.flags_minted for row in conviction_rows),
        seeds=table.seeds,
        splits=table.splits,
        rows=tuple(conviction_rows),
    )


__all__ = [
    "CONVICTION_FEATURE_NAMES",
    "CONVICTION_FEATURE_PROVENANCE",
    "CONVICTION_PROVENANCE_SOURCES",
    "CONVICTION_READABLE_CANDIDATE_FIELDS",
    "CONVICTION_READABLE_ROW_FIELDS",
    "ConvictionMeetingRow",
    "ConvictionTable",
    "ConvictionWalkGateError",
    "build_conviction_table",
    "require_clean_walk",
]
