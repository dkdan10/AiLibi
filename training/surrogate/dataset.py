"""The meeting training table — the surrogate's supervised substrate (Task 15.11).

For every committed meeting this module reconstructs, OFFLINE (LLM-free,
replay-deterministic), the per-(meeting, voter) feature rows the ballot surrogate
(Task 15.13) trains on and every meeting model is judged against
(:mod:`training.surrogate.fidelity`). It joins the reconstructed features to the
ACTUAL recorded ballots ``{voter, target, confidence, primary_reason_id}`` and to
roles ground truth (audits/post-phase-14-ML-training-signal.md §5.4, §7.2).

Reconstruction recipe (MIRRORS ``eval.funnel._walk_game`` /
``api.replay_loader._walk`` — the loader is API-tier and carries serving concerns,
so the re-seed / advance / apply / hash-verify loop is mirrored here, NOT imported):
re-seed each game from its roster, feed the recorded actions through
:func:`engine.tick.advance_tick`, verify every per-tick ``state_hash`` and each
meeting row's ``state_hash_before`` / ``state_hash_after``, and on a MEETING tick
rebuild the :class:`~meetings.schemas.MeetingResult` and apply it via
:func:`orchestrator.game.apply_meeting_result`. A corrupted or drifted set fails
loud (:class:`MeetingTableReconstructionError`) rather than silently mis-building
(AGENTS.md "no silent fallbacks").

The single biggest feature over FO-6's six raw counts
(``experiments/lab/ml_spike/fo6_learned_vote_surrogate.py``) is the **pre-meeting
belief-fold rendered suspicion**. The belief fold in ``agents/memory/beliefs.py`` is
deterministic over recorded events and needs no LLM;
:func:`meetings.manager.extract_belief_evidence` re-derives each meeting's public
evidence (accused / corroborated / contradicted / testimony — the
``derive_belief_evidence`` derivation, roster read off ``result.ballots``,
``meetings/manager.py``). Folding that evidence over PRIOR meetings through the
real :func:`agents.memory.beliefs.apply_meeting_evidence_rules` (the exact persistent
post-meeting absorb the orchestrator runs, ``phase=None``) reconstructs the
per-voter cross-meeting suspicion accumulator the LLM votes on — WITHOUT this
meeting's transcript (a training-time surrogate has no LLM, hence no current
transcript), so it is the honest pre-meeting graph. The perception-time pins
(witnessed kill +1.0 / witnessed vent +0.5 / Rule-1 body proximity +0.2) are
ingested into the perceiving voter's ``BeliefState`` at event time exactly as
production's ``apply_observation_rules`` ingests them — so the scalar carries the
FULL pre-meeting row, and the real Rule-5 fold decays an unreinforced pin toward
the 0.5 prior across later meetings (Codex review: a stale pin never re-applies at
full strength). The boolean pin columns (``witnessed_kill`` / ``witnessed_vent`` /
``body_proximity``) remain first-class first-hand-evidence FLAGS so a linear/tree
surrogate can weight each channel independently.

Row grain is one row per (meeting, voter); the roster is read off ``result.ballots``
(every living participant casts exactly one ballot — ``meetings/manager.py``), which
fixes the candidate universe. Each row carries the voter's per-candidate feature
view (:class:`CandidateFeatures`, one per living player) plus the voter's actual
ballot. EVERY recorded ballot joins exactly one row (100% join rate, asserted by
:func:`build_meeting_table` against the set's assembled tournament report).

The builder takes ANY replay-set directory and reads a committed ``splits.json``
when present (:func:`load_splits`), so it runs identically on the 15.12 corpus.

Every row also carries the audit rewrites the meeting layer applied to its ballot
(``ballot_rewrite_labels``, plus the narrower ``ballot_coerced_skip`` census
column), so the fit can DROP every row whose recorded target is not the voter's
authored choice while the fidelity replay still scores the recorded bytes
unfiltered.

:func:`measure_belief_render_parity` is the end-to-end
cross-check of this module's hand-mirrored belief fold against the PRODUCTION
fold (``eval.funnel``'s memory-augmented walk: real ``TacticalAgent`` instances
fed reconstructed packets, read through the exact
``suspicion_graph_for_meeting()`` accessor a live meeting consumes), which also
measures the graduated-J1 live-parity divergence — the raw ``belief_suspicion``
column this table serves vs the CLAMPED rendered value the live runner would be
served (the Task-16.4 render clamp, unconditional since the 16.17 baseline-5
record).

Pure and offline: no network, no ``AILIBI_*`` env, no LLM call; the only engine
imports are the reconstruction path (seeder + ``advance_tick`` + the orchestrator's
``apply_meeting_result``), mirroring the committed 15.3 / 15.8 folds.

Public surface (stable — downstream tasks import these): :class:`MeetingTableRow`,
:class:`CandidateFeatures`, :class:`MeetingTable`, :class:`SurrogateSplits`,
:class:`BeliefRenderParity`, :func:`build_meeting_table`, :func:`load_splits`,
:func:`measure_belief_render_parity`.
"""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Final, get_args

from pydantic import (
    BaseModel,
    ConfigDict,
    TypeAdapter,
    ValidationError,
    model_validator,
)

from agents.memory.beliefs import (
    BODY_PROXIMITY_SUSPICION_DELTA,
    BODY_PROXIMITY_WINDOW_TICKS,
    SUSPICION_PROVENANCE_ATOL,
    VENTING_SUSPICION_DELTA,
    WITNESSED_KILL_SUSPICION_DELTA,
    BeliefState,
    apply_contradiction_rule,
    apply_meeting_evidence_rules,
)
from engine.actions import Action
from engine.entities import BodyId, PlayerId, Role, RoomId
from engine.events import (
    KilledEvent,
    MeetingTriggeredEvent,
    MovedEvent,
    TaskCompletedEvent,
    TaskProgressedEvent,
    VentEnteredEvent,
    VentExitedEvent,
)
from engine.tick import advance_tick, superseded_meeting_tick
from engine.visibility import compute_visibility_for_player
from engine.world import Map, WorldState, load_canonical_map

# The production-fold walk the 17.10 parity cross-check joins against
# (:func:`measure_belief_render_parity`): eval.funnel's memory-augmented walk is
# the 16.10 instrument's machinery (real TacticalAgents fed reconstructed
# packets), imported rather than forked — a re-implementation here would be a
# second hand-mirror of exactly the fold this cross-check exists to verify.
from eval.funnel import _walk_game_vj
from eval.validity import (
    assemble_tournament_report,
    resolve_roster_knobs,
    roles_by_seed,
    seeds_on_disk,
)
from meetings.manager import (
    BALLOT_TARGET_REDIRECT_MARKER,
    INVALID_OBSERVATION_ID_MARKER,
    INVALID_REASON_ID_MARKER,
    TEAMMATE_VOTE_TARGET_MARKER,
    UNCITED_ZERO_FLAG_EJECT_MARKER,
    VOTE_PARSE_DEFAULT_MARKER,
    extract_belief_evidence,
)
from meetings.render_contract import SuspicionEntry
from meetings.schemas import (
    BallotTargetRewriteReason,
    ContradictionRef,
    MeetingOutcome,
    MeetingResult,
    MeetingTranscript,
    VoteBallot,
)
from meetings.transcript import MeetingTriggerKind, is_weak_contradiction
from meetings.voting import INVALID_VOTE_TARGET_MARKER
from orchestrator.game import apply_meeting_result
from orchestrator.replay import (
    MeetingReplayEntry,
    ReplayEntry,
    _state_hash,
    read_all_entries,
)
from orchestrator.seeder import seed_initial_state

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)

# The kill-scene co-presence window (FO-6 parity: ``0 <= tick - kill_tick <= 2``).
# A candidate co-located in the kill room within this many ticks of a resolved kill
# is "seen at the kill" — the strongest LLM-free physical placement.
SEEN_AT_KILL_WINDOW_TICKS: int = 2

# The committed ``splits.json`` filename the builder reads when present (Task 15.12
# writes it; the baseline sets ship none, so folds are derived by the harness).
SPLITS_FILENAME: str = "splits.json"

# The ``{x!r}``-repr payload of a production ``.format()`` marker — the
# established ``api.replay_loader._marker_pattern`` convention, replicated
# locally exactly as ``eval.meeting_quality`` replicates it (the api helper is
# private to the api layer; a cross-layer import would couple training to api
# internals). Matching the QUOTED repr value (not the static tail alone) keeps
# the match at the REAL marker boundary even when the coerced target text
# itself contains the marker's tail.
_MARKER_REPR_VALUE: str = r"(?:'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")"

# (label, marker) for every audit marker the meeting layer PREPENDS to a ballot's
# ``rationale_text``, built from the imported production literals so a rename
# breaks loudly here. Mirrors ``api.replay_loader._BALLOT_PREFIX_MARKERS`` — the
# display layer's table over the same six kinds — and a test pins the two label
# sets against each other. ``VOTE_PARSE_DEFAULT_MARKER`` is the seventh kind and
# sits apart: it is the WHOLE rationale, not a prefix.
BALLOT_AUDIT_MARKERS: Final[tuple[tuple[str, str], ...]] = (
    ("invalid_target", INVALID_VOTE_TARGET_MARKER),
    ("teammate_coerced", TEAMMATE_VOTE_TARGET_MARKER),
    ("under_gate_redirect", BALLOT_TARGET_REDIRECT_MARKER),
    ("invalid_reason_id", INVALID_REASON_ID_MARKER),
    ("invalid_observation_id", INVALID_OBSERVATION_ID_MARKER),
    ("uncited_coerced", UNCITED_ZERO_FLAG_EJECT_MARKER),
)
_VOTE_PARSE_DEFAULT_LABEL: Final[str] = "parse_default"

#: The labels under which a recorded ballot's TARGET is not the voter's authored
#: choice — the meeting layer redirected, coerced, normalized or wholly defaulted
#: it. Read from the public :data:`meetings.schemas.BallotTargetRewriteReason`
#: union, the same source ``api.replay_loader._TARGET_REWRITE_LABELS`` derives
#: from, so the training class and the display class cannot drift apart. The two
#: citation-only labels are deliberately outside it: they null a reference and
#: leave the authored target intact.
TARGET_REWRITE_LABELS: Final[frozenset[str]] = frozenset(
    get_args(BallotTargetRewriteReason)
)


def _marker_pattern(marker: str) -> re.Pattern[str]:
    """Anchored regex matching one whole audit marker at the head of a string.

    A ``.format()`` marker matches head + ``{x!r}`` repr payload + tail; matching
    the QUOTED repr value (rather than the static tail alone) keeps the match at
    the REAL marker boundary even when the rewritten value itself contains that
    tail. A marker with no placeholder matches literally.
    """

    head, brace, rest = marker.partition("{")
    if not brace:
        return re.compile("^" + re.escape(marker))
    _, _, tail = rest.partition("}")
    return re.compile("^" + re.escape(head) + _MARKER_REPR_VALUE + re.escape(tail))


_BALLOT_MARKER_PATTERNS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = tuple(
    (label, _marker_pattern(marker)) for label, marker in BALLOT_AUDIT_MARKERS
)
# The seventh kind, matched with the same repr-aware machinery: the WHOLE
# marker, not its static head. A model-authored rationale that merely opens
# with the head's words is not a defaulted ballot, and dropping it from the fit
# for a phrase would be a false exclusion of an authored target.
_VOTE_PARSE_DEFAULT_PATTERN: Final[re.Pattern[str]] = _marker_pattern(
    VOTE_PARSE_DEFAULT_MARKER
)


def ballot_rewrite_labels(ballot: VoteBallot) -> tuple[str, ...]:
    """Every audit rewrite the meeting layer applied to one recorded ballot.

    :attr:`~meetings.schemas.VoteBallot.guard_rewrite_reason` is the PREFERRED
    source — the meeting layer's own structured testimony — and it always leads
    the result, so a parse can never contradict it away or leave it out. It
    cannot REPLACE the marker chain, though: the field holds ONE reason while a
    ballot can pass two guards, and it is the FIRST rewrite that owns it
    (``meetings.voting.ballot_target_rewrite_provenance``: "the first rewrite
    owns them and a later one leaves them untouched. Every rewrite still
    prepends its own marker"). Reading the field alone would lose the second
    rewrite and undercount the per-kind census, so the markers are read too and
    merge in, deduplicated: the structured value is authoritative, never
    exhaustive.

    That same rule BOUNDS the parse. Markers are prepended, so the first
    rewrite's marker is the innermost one, and the guard region of the string
    ends where it ends — everything past it is the voter's own words. When the
    structured reason is present the strip therefore stops as soon as it
    consumes the marker naming it, so a rationale that merely opens with
    marker-shaped text cannot mint a rewrite that never happened. A legacy
    recording carries no such bound and strips to exhaustion, exactly as the
    display layer's parse does.

    The chain is stripped front-to-back through :data:`BALLOT_AUDIT_MARKERS` so
    a stacked ordering cannot hide the inner label behind the outer one. The
    parse-default marker replaces the whole rationale rather than prefixing it,
    so it is matched apart — as the WHOLE marker, head and repr payload and
    tail, never the head alone.

    Order is structured-first, then recovery order; callers read the SET.
    """

    labels: list[str] = []

    def keep(label: str) -> None:
        if label not in labels:
            labels.append(label)

    first_rewrite = ballot.guard_rewrite_reason
    if first_rewrite is not None:
        keep(first_rewrite)
    text = ballot.rationale_text
    if _VOTE_PARSE_DEFAULT_PATTERN.match(text) is not None:
        keep(_VOTE_PARSE_DEFAULT_LABEL)
        return tuple(labels)
    stripped = True
    while stripped:
        stripped = False
        for label, pattern in _BALLOT_MARKER_PATTERNS:
            match = pattern.match(text)
            if match is None:
                continue
            keep(label)
            text = text[match.end() :]
            if label == first_rewrite:
                # The innermost guard marker; the rest is the voter's own text.
                return tuple(labels)
            stripped = True
            break
    return tuple(labels)


def _ballot_is_coerced_skip(ballot: VoteBallot) -> bool:
    """Whether a recorded ballot is a J2 citation-gate coerced SKIP.

    The narrow census the ballot-surrogate report quotes per kind: a ballot the
    citation gate coerced records ``target="SKIP"`` but was a FORCED eject. It is
    one member of the wider :data:`TARGET_REWRITE_LABELS` class the fit excludes,
    kept as its own column because the report counts the kinds apart.
    """

    return "uncited_coerced" in ballot_rewrite_labels(ballot)


class MeetingTableReconstructionError(RuntimeError):
    """A recorded state hash did not reconstruct — the set is corrupt/drifted.

    Raised during the walk when a per-tick ``state_hash`` or a meeting row's
    ``state_hash_before`` / ``state_hash_after`` disagrees with the engine
    reconstruction, so a drifted or corrupted replay set fails loud rather than
    silently building a wrong table (AGENTS.md "no silent fallbacks"). Mirrors
    :class:`eval.funnel.FunnelReconstructionError`.
    """


class CandidateFeatures(BaseModel):
    """One living candidate's reconstructed features, from a voter's view (frozen).

    All columns derive OFFLINE from the committed bytes. The suspicion/trust pair
    is the voter's FULL pre-meeting belief row: prior meetings' public evidence
    folded by the real post-meeting absorb PLUS the perception pins the voter took
    at event time (witnessed kill/vent, Rule-1 body proximity), with the real
    Rule-5 fold decaying unreinforced rows toward the 0.5 prior — the production
    graph, not an accumulator subset. The candidate's OWN row is never held about
    the voter, so a ``is_self`` candidate reads the neutral 0.5 prior. The
    contradiction-flag
    counts (``strong_flags`` / ``weak_flags`` / ``vent_flags``), sighting counts
    (``witnessed`` / ``isolation``), ``seen_at_kill``, ``is_reporter``,
    ``task_submissions`` and ``move_count`` are voter-INDEPENDENT meeting/window
    facts (identical across a meeting's voters), so a meeting-level ranker (FO-6)
    reads them off any row; ``witnessed_kill`` / ``witnessed_vent`` /
    ``body_proximity`` are VOTER-LOCAL perception pins. ``is_ejected`` /
    ``is_impostor`` are labels (roles ground truth), never predictive inputs.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    candidate: PlayerId
    role: Role
    is_self: bool
    is_impostor: bool
    is_ejected: bool
    is_reporter: bool
    # The voter's full pre-meeting belief row: prior-meeting evidence fold +
    # perception pins ingested at event time, Rule-5 decayed by the real fold.
    belief_suspicion: float
    belief_trust: float
    # THIS meeting's contradiction-flag structure naming the candidate.
    strong_flags: int
    weak_flags: int
    vent_flags: int
    # The candidate's RENDERED vote-time contradiction lift for this meeting,
    # computed by the real :func:`agents.memory.beliefs.apply_contradiction_rule`
    # (one delta per (subject, claim) lift group — repeated flags of one underlying
    # claim never stack — capped at one strong flag's worth). The raw count columns
    # above are surrogate features; THIS is the production-faithful magnitude the
    # honest ceiling folds in (Codex review: dedup by claim, not raw counts).
    contradiction_lift: float
    # Physical reconstruction over the pre-meeting play window (FO-6 parity).
    witnessed: int
    isolation: int
    seen_at_kill: bool
    # VOTER-LOCAL role-proving eyewitness pins (Codex review): this row's VOTER
    # personally witnessed the candidate kill (+1.0) / vent (+0.5) — the exact
    # belief-store pins, exposed only to the witness, never the co-presence proxy.
    witnessed_kill: bool
    witnessed_vent: bool
    # VOTER-LOCAL §6.3 Rule 1 pin (Codex review): this row's VOTER first-sighted
    # a body and had personally observed the candidate in that body's room within
    # the prior window (+0.2) — never a global corpse-room-occupancy flag.
    body_proximity: bool
    # Game-long cadence signals from ACCEPTED engine events (Codex review): one
    # ``TaskProgressed``/``TaskCompleted`` per accepted task-work tick, one
    # ``Moved`` per accepted room change — a rejected replay intent (dead actor,
    # wrong room, unowned task) emits neither and never counts.
    task_submissions: int
    move_count: int


class MeetingTableRow(BaseModel):
    """One (meeting, voter) training row (Task 15.11 public type; frozen).

    Carries the meeting/voter identity, the voter's ACTUAL recorded ballot (the
    join target — ``ballot_target`` / ``ballot_confidence`` /
    ``ballot_primary_reason_id``), the meeting-level outcome + ejected target
    (labels), and the voter's per-candidate feature view (:class:`CandidateFeatures`,
    one per LIVING player incl. the voter, sorted by id). ``candidates`` is the full
    living roster so a meeting's candidate set is identical across its voters, which
    the fidelity harness reads off any row. Signature is stable per the task
    contract.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    seed: int
    game_id: str
    meeting_id: str
    meeting_index: int
    tick: int
    trigger: MeetingTriggerKind
    reporter: PlayerId
    outcome: MeetingOutcome
    ejected_player_id: PlayerId | None
    voter: PlayerId
    voter_role: Role
    voter_is_impostor: bool
    ballot_target: PlayerId | str
    ballot_confidence: float
    ballot_primary_reason_id: str | None
    # Whether the recorded ballot is a J2 citation-gate coerced SKIP — one
    # member of ``ballot_rewrite_labels`` below, carried as its own column
    # because the ballot-surrogate report counts the marker kinds apart.
    ballot_coerced_skip: bool
    # Every audit rewrite the meeting layer applied to this ballot
    # (:func:`ballot_rewrite_labels`). A label in
    # :data:`TARGET_REWRITE_LABELS` means the recorded ``ballot_target`` is not
    # the voter's authored choice, so fit-side consumers DROP the row; the two
    # citation-only labels null a reference and leave the target intact, so they
    # stay in the fit, labelled and counted. The fidelity replay scores the
    # recorded bytes unfiltered either way.
    ballot_rewrite_labels: tuple[str, ...]
    candidates: tuple[CandidateFeatures, ...]


class SurrogateSplits(BaseModel):
    """A committed by-GAME train/val/test split over a replay set (frozen).

    Read from ``splits.json`` when present (:func:`load_splits`). The lists hold
    game SEEDS (never meeting ids — by-game CV is the anti-leakage discipline,
    §5.5). Task 15.12 commits this alongside the corpus; the baseline sets ship
    none, so the fidelity harness derives K folds itself.

    The 15.12 recorder (``scripts/record_ml_corpus.sh::write_splits``) emits four
    audit-metadata keys beside the seed lists — ``set``, ``split_rule``,
    ``counts``, ``total_games`` — so the committed file documents its own split
    rule (the frozen corpus files carry all four). They are DECLARED here as
    typed optional fields rather than ignored: ``extra="forbid"`` stays, so a
    truly unknown key still fails loud, and present count metadata must agree
    with the seed lists (a self-inconsistent split file is a corrupted artifact,
    refused — never silently trusted). Regression pin for PR #240's review
    finding: the frozen corpus ``splits.json`` files must load unchanged.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    train: tuple[int, ...]
    val: tuple[int, ...] = ()
    test: tuple[int, ...] = ()
    # 15.12 audit metadata (present on the committed corpus files; absent on the
    # baseline sets' hand-built fixtures). Documentation of the split's own rule,
    # cross-checked against the seed lists below — never a substitute for them.
    set: str | None = None
    split_rule: str | None = None
    counts: dict[str, int] | None = None
    total_games: int | None = None

    @model_validator(mode="after")
    def _metadata_agrees_with_seed_lists(self) -> "SurrogateSplits":
        sides = {"train": self.train, "val": self.val, "test": self.test}
        if self.counts is not None:
            unknown = sorted(k for k in self.counts if k not in sides)
            if unknown:
                raise ValueError(f"splits counts name unknown sides: {unknown}")
            for name, declared in sorted(self.counts.items()):
                if declared != len(sides[name]):
                    raise ValueError(
                        f"splits counts[{name!r}] = {declared} != "
                        f"{len(sides[name])} seeds in the {name} list"
                    )
        if self.total_games is not None:
            actual = sum(len(seeds) for seeds in sides.values())
            if self.total_games != actual:
                raise ValueError(
                    f"splits total_games = {self.total_games} != {actual} seeds "
                    "across train/val/test"
                )
        return self


class MeetingTable(BaseModel):
    """The reconstructed meeting training table over one replay set (frozen).

    ``rows`` is every (meeting, voter) row, sorted deterministically (by seed,
    meeting_index, voter). The count aggregates are DERIVED from the set's assembled
    tournament report (:func:`eval.validity.assemble_tournament_report`), not
    hard-coded, and asserted equal to the reconstruction — substrate-agnostic (the
    committed sets are baseline 5 since the 17.9 re-record). ``model_dump_json()``
    is byte-stable across rebuilds (the determinism pin).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    replay_set_dir: str
    num_players: int
    num_impostors: int
    tasks_per_crewmate: int
    games_total: int
    meetings_total: int
    ejections_total: int
    skips_total: int
    ballots_total: int
    # EVERY recorded game seed in the set, sorted — including games with no
    # meetings (a real shape on every recorded substrate: 10 of the baseline-5
    # 4p1i corpus games end before any meeting fires, so they carry no rows).
    # Split validation and by-game folds partition THIS list, so a committed
    # 15.12 split that legitimately assigns a no-meeting game is never falsely
    # rejected, and ``games_total == len(seeds)``.
    seeds: tuple[int, ...]
    splits: SurrogateSplits | None
    rows: tuple[MeetingTableRow, ...]

    def game_seeds(self) -> tuple[int, ...]:
        """Every recorded game seed in the set, sorted (``self.seeds``).

        The by-game fold universe. A game with no meetings is still a GAME — it
        must be assignable to a fold/split side even though it contributes no
        scoreable meeting rows.
        """

        return self.seeds


def load_splits(sample_dir: Path) -> SurrogateSplits | None:
    """Read a committed ``splits.json`` from ``sample_dir`` when present.

    Returns ``None`` when the file is absent (the baseline sets). A present but
    malformed file raises (fail loud — a typo'd split silently ignored would leak
    games across folds). The 15.12 corpus commits this; the schema is
    :class:`SurrogateSplits`.
    """

    path = sample_dir / SPLITS_FILENAME
    if not path.is_file():
        return None
    try:
        return SurrogateSplits.model_validate_json(path.read_text())
    except ValidationError as exc:
        raise ValueError(f"malformed {path}: {exc}") from exc


def _deserialize_actions(raw_actions: Sequence[Mapping[str, object]]) -> list[Action]:
    return [_ACTION_ADAPTER.validate_python(dict(raw)) for raw in raw_actions]


def _meeting_result_from_entry(entry: MeetingReplayEntry) -> MeetingResult:
    return MeetingResult(
        meeting_id=entry.meeting_id,
        triggered_by=entry.triggered_by,
        trigger_tick=entry.tick,
        outcome=entry.outcome,
        ejected_player_id=entry.ejected_player_id,
        ballots=entry.ballots,
        contradictions=entry.contradictions,
        transcript=entry.transcript,
    )


def _flag_counts(
    contradictions: Sequence[ContradictionRef],
) -> dict[PlayerId, tuple[int, int, int]]:
    """Per-subject ``(strong, weak, vent)`` flag counts for one meeting.

    ``vent_sighting`` (Task 15.4, the new role-proving vent flag) is counted in its
    OWN band — it is always strong but is the load-bearing LLM-free signal, so the
    surrogate sees it separately from an alibi-based strong flag. A weak
    ``alibi_*`` flag (:func:`meetings.transcript.is_weak_contradiction`) is the
    down-weighted band; every other flag is strong.
    """

    counts: dict[PlayerId, tuple[int, int, int]] = defaultdict(lambda: (0, 0, 0))
    for flag in contradictions:
        for subject in flag.subjects:
            strong, weak, vent = counts[subject]
            if flag.kind == "vent_sighting":
                counts[subject] = (strong, weak, vent + 1)
            elif is_weak_contradiction(flag):
                counts[subject] = (strong, weak + 1, vent)
            else:
                counts[subject] = (strong + 1, weak, vent)
    return counts


def _contradiction_lifts(
    contradictions: Sequence[ContradictionRef],
    living: Sequence[PlayerId],
    *,
    transcript: MeetingTranscript | None,
) -> dict[PlayerId, float]:
    """Per-candidate RENDERED contradiction lift for one meeting (Codex review).

    Runs the REAL production rule — :func:`agents.memory.beliefs.
    apply_contradiction_rule` — on a zero-seeded state, so the lift carries the
    exact vote-time semantics: one delta per ``(subject,
    meetings.transcript.contradiction_lift_key)`` group (repeated flags of one
    underlying claim never stack — the seed-9 19-duplicate shape folds to one
    delta), summed across groups, capped at one strong flag's worth. Raw count
    sums would double a duplicated weak flag (0.16 vs the rendered 0.08) and
    corrupt the ceiling's strict-argmax reachability.

    ``transcript`` is THIS meeting's recorded transcript, threaded exactly as the
    production vote path threads it (``meetings/manager.py``): the Task-14.10
    self-refuted-alibi downgrade — unconditional since the 14.12 close — reads
    :func:`meetings.transcript.self_refuted_alibi_claim_ids` off it, so a strong
    flag riding an alibi the speaker disproved within their own turn renders the
    WEAK 0.08, never the full 0.30 the flag-kind alone would suggest (Codex
    review; the ``eval.meeting_quality`` flag-mass fold threads it for the same
    reason). Deterministic: a pure function of the committed transcript bytes.
    """

    if not contradictions:
        return {pid: 0.0 for pid in living}
    base = BeliefState()
    for pid in living:
        base.seed_player(pid, suspicion=0.0, trust=0.5)
    lifted = apply_contradiction_rule(base, contradictions, transcript=transcript)
    return {pid: lifted.view(pid).suspicion for pid in living}


class _WindowStats:
    """Per-player physical accumulators over the current inter-meeting window.

    Sighting/kill-proximity/body-proximity reset each meeting (FO-6 "recent
    activity" parity); ``task_submissions`` / ``moves`` accumulate over the whole
    game (a player who has completed no tasks all game is a game-long cadence
    signal). Both cadence counters derive from ACCEPTED engine events
    (``TaskProgressed`` / ``TaskCompleted`` and ``Moved`` — Codex review), never
    from submitted replay intents: the committed corpora contain REJECTED
    ``do_task`` / ``move`` attempts (dead actors, wrong rooms, unowned tasks)
    that produce a rejection event and no state change, so counting intents
    would credit work that never happened.

    ``witnessed_kill`` / ``witnessed_vent`` are the EXACT role-proving eyewitness
    pins from ``KilledEvent`` / vent-event witnesses (Codex review), mapping a
    KILLER/VENTER to the set of witnesses whose belief takes the pin. Production
    only stamps ``action="kill"`` / ``"vent"`` for the WITNESSING agent before
    that agent's own belief update, so the pin is VOTER-LOCAL: exposed only for a
    row whose voter is in the witness set. The kill pin is CREW witnesses only —
    the belief rule's §4.7 guard skips a fellow impostor, and the killer is
    always the witness's teammate there; the VENT pin covers EVERY witness — the
    production vent rule carries no teammate guard, so an impostor witnessing a
    teammate's vent takes the +0.5 too (Codex review). The FLAG sets persist
    (they record that the voter once held first-hand evidence) and do not reset;
    the pin's belief DELTA (+1.0 / +0.5 / +0.2) is ingested into the witness's
    ``BeliefState`` at event time — production's ``apply_observation_rules`` —
    where the real Rule-5 fold decays it toward 0.5 across later unreinforced
    meetings (Codex review), so the magnitude lives in ``belief_suspicion``,
    never re-applied at full strength. All updates read only reconstructed
    engine truth.

    ``body_proximity`` is the VOTER-LOCAL §6.3 Rule 1 reconstruction (Codex
    review): production fires the +0.2 bump in agent A's OWN beliefs only on the
    tick A FIRST sees a body, and only for players A itself observed in that
    body's room within the prior ``BODY_PROXIMITY_WINDOW_TICKS`` ticks (the
    victim excluded; an impostor observer's fellow impostors excluded, §4.7) —
    never for whoever happens to stand in the corpse's room at report time. The
    reconstruction runs the REAL :func:`engine.visibility.
    compute_visibility_for_player` per observer per tick (role-asymmetric sight,
    sabotage degrades, vent/dead filtering, ``discovered_by`` body gating), keeps
    each observer's rolling same-as-production sighting window, and maps a
    CANDIDATE to the set of observers holding the pin. Like production's
    perception-time bump it persists in the observer's graph, so it does not
    reset. The witness-gated kill/vent action stamps production also folds into
    ``saw_player`` rows feed the SAME sighting log (``event_sightings`` — even
    when the actor is not currently visible, e.g. hidden in a vent), so they can
    carry a later Rule-1 pin exactly as ``_recent_co_presence`` allows.
    """

    def __init__(self, game_map: Map) -> None:
        self.witnessed: dict[PlayerId, int] = defaultdict(int)
        self.isolation: dict[PlayerId, int] = defaultdict(int)
        self.seen_at_kill: dict[PlayerId, bool] = defaultdict(bool)
        self.witnessed_kill: dict[PlayerId, set[PlayerId]] = defaultdict(set)
        self.witnessed_vent: dict[PlayerId, set[PlayerId]] = defaultdict(set)
        self.body_proximity: dict[PlayerId, set[PlayerId]] = defaultdict(set)
        self.task_submissions: dict[PlayerId, int] = defaultdict(int)
        self.moves: dict[PlayerId, int] = defaultdict(int)
        self._pending_kills: list[tuple[int, RoomId]] = []
        self._game_map = game_map
        # Per-observer first-sighting guard (production: ``saw_body`` rows
        # strictly before the current tick) and per-observer sighting log
        # (production: ``saw_player`` rows keyed by the SEEN player's room).
        self._seen_bodies: dict[PlayerId, set[BodyId]] = defaultdict(set)
        self._sightings: dict[PlayerId, dict[RoomId, list[tuple[int, PlayerId]]]] = (
            defaultdict(dict)
        )

    def absorb_tick(
        self,
        state: WorldState,
        events: Sequence[object],
        roles: Mapping[PlayerId, Role],
        *,
        beliefs: Mapping[PlayerId, BeliefState],
    ) -> None:
        by_room: dict[RoomId, list[PlayerId]] = {}
        for pid, player in state.players.items():
            if player.alive and not player.in_vent:
                by_room.setdefault(player.room, []).append(pid)
        for occupants in by_room.values():
            if len(occupants) >= 2:
                for pid in occupants:
                    self.witnessed[pid] += 1
            else:
                self.isolation[occupants[0]] += 1
        # Witness-gated kill/vent action stamps ALSO land as ``saw_player`` rows in
        # production (``_observed_actions_for_agent`` merges them into
        # ``visible_players`` even when the actor is not currently visible — e.g. a
        # venting actor hidden in the vent), and ``_recent_co_presence`` reads those
        # rows for Rule-1 body proximity (Codex review). Collected here and appended
        # to the sighting log by ``_absorb_body_proximity`` AFTER its body pass, so
        # the current-tick exclusion holds.
        event_sightings: list[tuple[PlayerId, RoomId, PlayerId]] = []
        for event in events:
            # Task cadence / movement from ACCEPTED events only (Codex review): a
            # ``TaskProgressed`` / ``TaskCompleted`` is one accepted task-work tick
            # (explicit submission or engine continuation), a ``Moved`` one accepted
            # room change. A rejected intent emits neither, so it never counts.
            if isinstance(event, (TaskProgressedEvent, TaskCompletedEvent)):
                self.task_submissions[event.actor] += 1
            elif isinstance(event, MovedEvent):
                self.moves[event.actor] += 1
            elif isinstance(event, KilledEvent):
                self._pending_kills.append((event.tick, event.room))
                # The EXACT witnessed-kill pin (Codex review): production stamps
                # ``action="kill"`` for the event's witnesses; the belief rule
                # then applies the +1.0 hard pin with the §4.7 teammate guard —
                # the killer is an impostor, so an impostor witness (its
                # teammate) accrues nothing and only CREW witnesses take the
                # pin. Voter-local, never the co-presence proxy: a witnessed
                # killer who moved or was alone is not missed and a bystander is
                # never mismarked.
                crew_witnesses = {
                    w for w in event.witnesses if roles.get(w) == "CREWMATE"
                }
                if crew_witnesses:
                    self.witnessed_kill[event.actor].update(crew_witnesses)
                    # Ingest the pin into the witness's OWN belief row at
                    # perception, exactly as production does — so Rule 5 decays
                    # it at later unreinforced meeting folds (Codex review:
                    # never reapply a stale pin at full strength).
                    for witness in sorted(crew_witnesses):
                        beliefs[witness].adjust_suspicion(
                            event.actor, delta=WITNESSED_KILL_SUSPICION_DELTA
                        )
                # The ``saw_player`` stamp itself exists for EVERY witness (the
                # co-presence teammate filter is applied at read time, as in
                # production's ``_recent_co_presence``).
                for witness in event.witnesses:
                    if witness != event.actor:
                        event_sightings.append((witness, event.room, event.actor))
            elif isinstance(event, (VentEnteredEvent, VentExitedEvent)):
                # The witnessed-VENT pin (Codex review): a witness who SAW the
                # vent takes the +0.5 role-proving pin at perception
                # (VENTING_SUSPICION_DELTA), persisting into the pre-meeting graph
                # even when no grounded ``vent_sighting`` contradiction is spoken.
                # Witnesses = the source-room ∪ destination-room witness sets the
                # engine records. Production's vent rule carries NO fellow-
                # impostor guard (venting is impostor-exclusive; the kill rule's
                # §4.7 guard exists because teammate kills are routine), so an
                # IMPOSTOR witnessing a teammate's vent takes the pin too —
                # crew-only filtering here would drop real production belief
                # updates from impostor voters' rows (Codex review).
                vent_witnesses = {
                    w
                    for w in (*event.source_witnesses, *event.destination_witnesses)
                    if w != event.actor
                }
                if vent_witnesses:
                    self.witnessed_vent[event.actor].update(vent_witnesses)
                    for witness in sorted(vent_witnesses):
                        beliefs[witness].adjust_suspicion(
                            event.actor, delta=VENTING_SUSPICION_DELTA
                        )
                # The vent ``saw_player`` stamp's room mirrors production's
                # ``_vent_observation_for_agent``: the source room when the
                # witness saw the entry side, else the destination room.
                for witness in vent_witnesses:
                    room = (
                        event.source_room
                        if witness in event.source_witnesses
                        else event.destination_room
                    )
                    event_sightings.append((witness, room, event.actor))
        for kill_tick, kill_room in self._pending_kills:
            if 0 <= state.tick - kill_tick <= SEEN_AT_KILL_WINDOW_TICKS:
                occupants = by_room.get(kill_room, [])
                if len(occupants) >= 2:
                    for pid in occupants:
                        self.seen_at_kill[pid] = True
        self._absorb_body_proximity(state, roles, beliefs, event_sightings)

    def _absorb_body_proximity(
        self,
        state: WorldState,
        roles: Mapping[PlayerId, Role],
        beliefs: Mapping[PlayerId, BeliefState],
        event_sightings: Sequence[tuple[PlayerId, RoomId, PlayerId]] = (),
    ) -> None:
        """§6.3 Rule 1, voter-local (Codex review): first sighting + co-presence.

        Per observer, through the REAL :func:`compute_visibility_for_player`:
        on the tick the observer FIRST sees a body, every player the observer
        itself saw in that body's room within the prior
        ``BODY_PROXIMITY_WINDOW_TICKS`` ticks (current tick excluded — the
        window is "shortly before" the discovery) gains the pin IN THAT
        OBSERVER'S view only. The victim is skipped (a corpse seen alive
        moments earlier is not a suspect) and an impostor observer's fellow
        impostors are skipped (§4.7 — a teammate near a teammate's kill never
        manufactures crew-shaped evidence). Bodies are processed BEFORE this
        tick's sightings are recorded, mirroring production's strict
        ``event.tick < current_tick`` co-presence window.
        """

        impostor_ids = frozenset(
            pid for pid, role in roles.items() if role == "IMPOSTOR"
        )
        cutoff = state.tick - BODY_PROXIMITY_WINDOW_TICKS
        for observer in sorted(state.players):
            visibility = compute_visibility_for_player(
                observer_id=observer, world_state=state, game_map=self._game_map
            )
            sightings = self._sightings[observer]
            for body_id in visibility.visible_body_ids:
                seen = self._seen_bodies[observer]
                if body_id in seen:
                    continue  # Rule 1 fires only on the FIRST sighting.
                seen.add(body_id)
                body = state.bodies[body_id]
                teammates = (
                    impostor_ids - {observer}
                    if observer in impostor_ids
                    else frozenset()
                )
                co_present = {
                    pid
                    for tick, pid in sightings.get(body.room, ())
                    if tick >= cutoff and pid != body.player_id and pid not in teammates
                }
                for pid in sorted(co_present):
                    self.body_proximity[pid].add(observer)
                    # Production ingests the +0.2 into the OBSERVER's own belief
                    # row at perception; the real Rule-5 fold then decays it at
                    # later unreinforced meetings (Codex review).
                    beliefs[observer].adjust_suspicion(
                        pid, delta=BODY_PROXIMITY_SUSPICION_DELTA
                    )
            # Record this tick's sightings (and prune beyond the window) AFTER
            # the body pass, keyed by the SEEN player's room like ``saw_player``.
            for room in list(sightings):
                kept = [(t, pid) for t, pid in sightings[room] if t >= cutoff]
                if kept:
                    sightings[room] = kept
                else:
                    del sightings[room]
            for pid in visibility.visible_player_ids:
                room = state.players[pid].room
                sightings.setdefault(room, []).append((state.tick, pid))
        # Witness-gated kill/vent action stamps become ``saw_player`` rows in
        # production even when the actor is not currently visible (a venting
        # actor is hidden in the vent), so they feed the SAME co-presence window
        # (Codex review). Appended after the body pass, like the visible rows.
        for witness, room, actor in event_sightings:
            if witness in state.players:
                self._sightings[witness].setdefault(room, []).append(
                    (state.tick, actor)
                )

    def reset_window(self) -> None:
        # ``body_proximity`` deliberately survives the reset: production's Rule 1
        # bump lands once at first sighting and persists in the observer's stored
        # beliefs, like the witnessed kill/vent pins.
        self.witnessed.clear()
        self.isolation.clear()
        self.seen_at_kill.clear()
        self._pending_kills.clear()


def _fold_meeting_into_beliefs(
    beliefs: dict[PlayerId, BeliefState],
    *,
    result: MeetingResult,
    trigger_kind: MeetingTriggerKind,
    roles: Mapping[PlayerId, Role],
    roster: frozenset[PlayerId],
    voters: Sequence[PlayerId],
) -> None:
    """Fold one resolved meeting's public evidence into each voter's beliefs.

    The EXACT persistent post-meeting absorb the orchestrator runs
    (:func:`agents.memory.store.absorb_meeting_evidence` →
    :func:`agents.memory.beliefs.apply_meeting_evidence_rules` with ``phase=None``):
    one :func:`meetings.manager.extract_belief_evidence` reduction (roster off
    ``result.ballots``), then the composed accusation-bump / Rule-3 corroboration /
    Rule-5 decay fold per living voter, so suspicion carries into the NEXT meeting's
    pre-meeting graph. An impostor voter's fold drops fellow-impostor subjects (the
    §4.7 firewall); ``roster`` is the full co-spawned player set (the store's
    ``_known_roster_ids`` is a no-op on real-player data — every player co-spawns).
    """

    evidence = extract_belief_evidence(result, trigger_kind=trigger_kind)
    impostor_ids = frozenset(pid for pid, role in roles.items() if role == "IMPOSTOR")
    for voter in voters:
        teammates = (
            tuple(sorted(impostor_ids - {voter}))
            if roles.get(voter) == "IMPOSTOR"
            else ()
        )
        beliefs[voter] = apply_meeting_evidence_rules(
            beliefs[voter],
            own_id=voter,
            accused=evidence.accused,
            corroborated=evidence.corroborated,
            contradicted=evidence.contradicted,
            fellow_impostor_ids=teammates,
            roster=roster,
        )


def _candidate_features(
    candidate: PlayerId,
    *,
    voter: PlayerId,
    beliefs: BeliefState,
    roles: Mapping[PlayerId, Role],
    reporter: PlayerId,
    ejected: PlayerId | None,
    flags: Mapping[PlayerId, tuple[int, int, int]],
    lifts: Mapping[PlayerId, float],
    stats: _WindowStats,
) -> CandidateFeatures:
    strong, weak, vent = flags.get(candidate, (0, 0, 0))
    belief = beliefs.view(candidate)
    return CandidateFeatures(
        candidate=candidate,
        role=roles[candidate],
        is_self=candidate == voter,
        is_impostor=roles[candidate] == "IMPOSTOR",
        is_ejected=ejected is not None and candidate == ejected,
        is_reporter=candidate == reporter,
        belief_suspicion=belief.suspicion,
        belief_trust=belief.trust,
        strong_flags=strong,
        weak_flags=weak,
        vent_flags=vent,
        contradiction_lift=lifts.get(candidate, 0.0),
        witnessed=stats.witnessed.get(candidate, 0),
        isolation=stats.isolation.get(candidate, 0),
        seen_at_kill=stats.seen_at_kill.get(candidate, False),
        # Voter-local: each pin is exposed only when THIS row's voter is in the
        # candidate's witness/observer set (production stamps the evidence only
        # into the perceiving agent's own beliefs).
        witnessed_kill=voter in stats.witnessed_kill.get(candidate, set()),
        witnessed_vent=voter in stats.witnessed_vent.get(candidate, set()),
        body_proximity=voter in stats.body_proximity.get(candidate, set()),
        task_submissions=stats.task_submissions.get(candidate, 0),
        move_count=stats.moves.get(candidate, 0),
    )


def _walk_game(
    replay_path: Path,
    *,
    seed: int,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
    roles: Mapping[PlayerId, Role],
    game_map: Map,
) -> list[MeetingTableRow]:
    """Re-seed + replay one game into its per-(meeting, voter) rows.

    Mirrors :func:`eval.funnel._walk_game`: re-seed, advance every recorded tick
    with state-hash verification, and on a MEETING tick build the rows from the
    PRE-meeting belief state + window physical stats, then fold the meeting into the
    beliefs and apply it to the engine (verifying ``state_hash_after``) before
    resuming. A meeting row missing from the replay fails loud rather than
    under-building.
    """

    game_id = f"headless-seed-{seed}"
    entries = read_all_entries(replay_path)
    tick_entries = [entry for entry in entries if isinstance(entry, ReplayEntry)]
    meeting_by_tick: dict[int, MeetingReplayEntry] = {
        entry.tick: entry for entry in entries if isinstance(entry, MeetingReplayEntry)
    }

    state = seed_initial_state(
        seed=seed,
        game_map=game_map,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    roster = frozenset(state.players)
    beliefs: dict[PlayerId, BeliefState] = {pid: BeliefState() for pid in roster}
    stats = _WindowStats(game_map)
    rows: list[MeetingTableRow] = []
    meeting_index = 0

    # The initial tick-0 packet (Codex review): production builds and ingests a
    # packet from the INITIAL state before collecting the first actions
    # (orchestrator/game.py `_build_packets` runs at the top of the loop), so the
    # spawn-tick sightings/co-presence are in every agent's memory before tick 1.
    # Without this seed the first window is systematically one packet short.
    stats.absorb_tick(state, (), roles, beliefs=beliefs)

    for entry in tick_entries:
        actions = _deserialize_actions(entry.actions)
        state, events = advance_tick(state, actions, game_map=game_map)
        actual = _state_hash(state)
        if actual != entry.state_hash:
            # Two committed recordings pinned a meeting-trigger tick the engine
            # now concludes. The pre-ruling pair is accepted only when a meeting
            # row exists for the tick AND it re-hashes to the recorded hash
            # exactly, so it cannot mask a determinism break or a roster
            # mismatch. Retired by Task 21.15's re-record.
            restored = superseded_meeting_tick(state, events)
            if restored is not None and meeting_by_tick.get(entry.tick) is not None:
                candidate_state, candidate_events = restored
                if _state_hash(candidate_state) == entry.state_hash:
                    state = candidate_state
                    events = list(candidate_events)
                    actual = entry.state_hash
            if actual != entry.state_hash:
                raise MeetingTableReconstructionError(
                    f"{game_id}: tick {entry.tick} reconstructed {actual!r} != recorded "
                    f"{entry.state_hash!r} (roster mismatch or engine non-determinism)"
                )

        if state.phase != "MEETING":
            # An absorb here ≡ the production packet the orchestrator builds at
            # the NEXT tick from this post-action state (packets are built from
            # the PRE-action state each tick, ``orchestrator/game.py``).
            stats.absorb_tick(state, events, roles, beliefs=beliefs)
            if state.phase == "GAME_OVER":
                break
            continue

        # MEETING trigger tick (Codex review — pre-meeting perception timing):
        # production voters last ingested the packet built BEFORE this tick's
        # actions (≡ the previous iteration's absorb); the trigger tick's own
        # events and post-action state are deliberately preserved and delivered
        # on the RESUME tick, after the meeting. So the rows are built from the
        # stats/beliefs as of the PREVIOUS absorb — a same-tick witnessed
        # kill/vent never leaks into this meeting's rows — and this tick's
        # events are absorbed after the meeting below.

        trigger_event = next(
            (e for e in events if isinstance(e, MeetingTriggeredEvent)), None
        )
        if trigger_event is None:
            raise MeetingTableReconstructionError(
                f"{game_id}: tick {entry.tick} entered MEETING with no "
                "MeetingTriggeredEvent in the reconstructed events"
            )
        meeting_entry = meeting_by_tick.get(entry.tick)
        if meeting_entry is None:
            raise MeetingTableReconstructionError(
                f"{game_id}: tick {entry.tick} entered MEETING but the replay carries "
                "no meeting row for that tick (partial recording) — refusing to "
                "silently under-build"
            )
        if meeting_entry.state_hash_before != actual:
            raise MeetingTableReconstructionError(
                f"{game_id}: meeting at tick {entry.tick} recorded state_hash_before "
                f"{meeting_entry.state_hash_before!r} != reconstructed pre-meeting "
                f"state {actual!r}"
            )

        result = _meeting_result_from_entry(meeting_entry)
        trigger_kind: MeetingTriggerKind = trigger_event.trigger
        reporter = meeting_entry.triggered_by
        ejected = meeting_entry.ejected_player_id
        # Roster off the recorded ballots: every living participant casts exactly one
        # ballot (meetings/manager.py :2823), so the ballot voters ARE the living
        # candidate universe. Sorted for deterministic candidate/row order.
        voters = sorted(ballot.voter for ballot in result.ballots)
        living = tuple(voters)
        flags = _flag_counts(result.contradictions)
        lifts = _contradiction_lifts(
            result.contradictions, living, transcript=result.transcript
        )

        by_voter = {ballot.voter: ballot for ballot in result.ballots}
        for voter in living:
            ballot = by_voter[voter]
            candidate_features = tuple(
                _candidate_features(
                    candidate,
                    voter=voter,
                    beliefs=beliefs[voter],
                    roles=roles,
                    reporter=reporter,
                    ejected=ejected,
                    flags=flags,
                    lifts=lifts,
                    stats=stats,
                )
                for candidate in living
            )
            rows.append(
                MeetingTableRow(
                    seed=seed,
                    game_id=game_id,
                    meeting_id=meeting_entry.meeting_id,
                    meeting_index=meeting_index,
                    tick=entry.tick,
                    trigger=trigger_kind,
                    reporter=reporter,
                    outcome=meeting_entry.outcome,
                    ejected_player_id=ejected,
                    voter=voter,
                    voter_role=roles[voter],
                    voter_is_impostor=roles[voter] == "IMPOSTOR",
                    ballot_target=ballot.target,
                    ballot_confidence=ballot.confidence,
                    ballot_primary_reason_id=ballot.primary_reason_id,
                    ballot_coerced_skip=_ballot_is_coerced_skip(ballot),
                    ballot_rewrite_labels=ballot_rewrite_labels(ballot),
                    candidates=candidate_features,
                )
            )

        _fold_meeting_into_beliefs(
            beliefs,
            result=result,
            trigger_kind=trigger_kind,
            roles=roles,
            roster=roster,
            voters=living,
        )

        state, post_events = apply_meeting_result(
            state,
            result,
            game_map=game_map,
            triggering_body_id=trigger_event.body_id,
        )
        after = _state_hash(state)
        if after != meeting_entry.state_hash_after:
            raise MeetingTableReconstructionError(
                f"{game_id}: meeting at tick {entry.tick} reconstructed {after!r} != "
                f"recorded {meeting_entry.state_hash_after!r}"
            )
        stats.reset_window()
        # The RESUME-tick packet (orchestrator/game.py: ``last_events =
        # pre_meeting_events + post_events``): the post-meeting resumed state
        # plus the trigger tick's preserved events. This is where the trigger
        # tick's witnessed kill/vent pins land (after the meeting, exactly as
        # production delivers them) and where the new window's sightings begin.
        stats.absorb_tick(
            state, tuple(events) + tuple(post_events), roles, beliefs=beliefs
        )
        meeting_index += 1
        if state.phase == "GAME_OVER":
            break

    return rows


def build_meeting_table(
    sample_dir: Path, *, splits_path: Path | None = None
) -> MeetingTable:
    """Build the per-(meeting, voter) training table for a replay-set directory.

    Re-seeds every game from the set's roster (``roster.json`` via
    :func:`eval.validity.resolve_roster_knobs`; the flat 4p1i default otherwise),
    recovers roles ground truth from the set's assembled tournament report
    (:func:`eval.validity.assemble_tournament_report` — the report carries per-game
    ``roles``; raw replays are role-free by firewall design), and walks each recorded
    action stream through the engine (:func:`_walk_game`) into rows. The count
    aggregates are read off the SAME assembled report, and the reconstruction is
    asserted to reproduce them exactly — every recorded ballot joins exactly one row
    (100% join rate). Runs on any replay-set directory + both roster presets; reads
    a committed ``splits.json`` when present. Pure and offline.
    """

    if not sample_dir.is_dir():
        raise NotADirectoryError(f"replay-set directory not found: {sample_dir}")
    seeds = seeds_on_disk(sample_dir)
    if not seeds:
        raise ValueError(f"no replay-seed-*.jsonl found under {sample_dir}")

    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(sample_dir)
    game_map = load_canonical_map()
    per_seed_roles = roles_by_seed(
        sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
    )

    # Roles ground truth + the count aggregates come from the set's assembled
    # tournament report (the report carries per-game roles + meeting/ballot rows),
    # NOT hard-coded. The re-seeded roles are byte-identical to the report's (both
    # re-seed the same deterministic recipe); the table asserts against the report.
    report = assemble_tournament_report(sample_dir)
    report_roles = {game.seed: dict(game.roles) for game in report.games}
    report_meetings = [meeting for game in report.games for meeting in game.meetings]
    ejections_total = sum(1 for m in report_meetings if m.outcome == "EJECTED")
    skips_total = sum(1 for m in report_meetings if m.outcome == "SKIPPED")
    ballots_total = sum(len(m.ballots) for m in report_meetings)

    rows: list[MeetingTableRow] = []
    for seed in seeds:
        roles = report_roles.get(seed, per_seed_roles[seed])
        rows.extend(
            _walk_game(
                sample_dir / f"replay-seed-{seed}.jsonl",
                seed=seed,
                num_players=num_players,
                num_impostors=num_impostors,
                tasks_per_crewmate=tasks_per_crewmate,
                roles=roles,
                game_map=game_map,
            )
        )

    rows.sort(key=lambda row: (row.seed, row.meeting_index, row.voter))

    # Every recorded ballot MUST join exactly one row (the 100% join assertion): the
    # table's row count equals the tournament report's ballot total, and its meeting
    # count equals the report's meeting count.
    reconstructed_meetings = len({(row.seed, row.meeting_id) for row in rows})
    if reconstructed_meetings != len(report_meetings):
        raise MeetingTableReconstructionError(
            f"{sample_dir}: reconstructed {reconstructed_meetings} meetings != report "
            f"{len(report_meetings)} (a meeting failed to join)"
        )
    if len(rows) != ballots_total:
        raise MeetingTableReconstructionError(
            f"{sample_dir}: reconstructed {len(rows)} ballot rows != report "
            f"{ballots_total} ballots (join rate < 100%)"
        )

    # A committed split: an explicit ``splits_path`` (e.g. a 15.12 corpus file staged
    # outside the read-only replay dir) takes precedence; otherwise the set's own
    # ``splits.json`` when present. The baseline sets ship none, so the harness
    # derives its folds.
    splits: SurrogateSplits | None
    if splits_path is not None:
        splits = SurrogateSplits.model_validate_json(splits_path.read_text())
    else:
        splits = load_splits(sample_dir)

    return MeetingTable(
        replay_set_dir=str(sample_dir),
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        games_total=len(seeds),
        meetings_total=len(report_meetings),
        ejections_total=ejections_total,
        skips_total=skips_total,
        ballots_total=ballots_total,
        seeds=tuple(seeds),
        splits=splits,
        rows=tuple(rows),
    )


class BeliefRenderParity(BaseModel):
    """The 17.10 walk re-validation: hand-mirrored fold vs the production fold.

    Measured per non-self (meeting, voter, candidate) cell over a whole replay
    set by :func:`measure_belief_render_parity`, joining this module's
    reconstructed rows to the PRODUCTION fold's meeting-open suspicion graphs
    (``eval.funnel``'s memory-augmented walk: real ``TacticalAgent`` instances
    ingest every reconstructed packet and serve
    ``suspicion_graph_for_meeting()`` exactly as a live meeting reads it — the
    16.10 instrument's machinery; measured, never assumed).

    Two independent gauges:

    * FOLD FIDELITY — ``raw_mismatches`` / ``trust_mismatches``: the table's
      ``belief_suspicion`` / ``belief_trust`` vs the production row's RAW
      stored scalar. The graph entry's scalar is the CLAMPED render, so the
      raw side is recovered from the 16.3 sum invariant (``0.5 + Σ`` of the
      eight provenance channels the entry carries beside it — the invariant
      the vj gauge pins on every committed set). A nonzero count means the
      hand-mirrored perception→belief pins (:class:`_WindowStats`) drifted
      from a baseline-5 belief rule — the silent corruption the 17.10
      integration risk names — and no fit over the table can be trusted.
    * J1 LIVE-PARITY DIVERGENCE — ``j1_divergent_cells`` / ``j1_divergent_rows``:
      cells where the CLAMPED rendered value the live runner would be served
      (``SuspicionEntry.suspicion`` under the graduated Task-16.4 J1 gate,
      unconditional since the 16.17 baseline-5 record) differs from the raw
      ``belief_suspicion`` the table — and therefore the 15.13 fit — reads.
      The fit-side/test-side split localizes the divergence under the
      committed ``splits.json`` (``None`` when the set ships none).

    Tolerance is the production ``SUSPICION_PROVENANCE_ATOL`` throughout. The
    voter's own ``is_self`` cell is excluded: the table pins it at the neutral
    0.5 prior by construction and production holds no self-row.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    replay_set_dir: str
    games_total: int
    meetings_total: int
    rows_total: int
    cells_compared: int
    raw_mismatches: int
    trust_mismatches: int
    max_raw_abs_delta: float
    j1_divergent_cells: int
    j1_divergent_rows: int
    j1_divergent_fit_cells: int | None
    j1_divergent_test_cells: int | None
    j1_max_abs_divergence: float


def measure_belief_render_parity(sample_dir: Path) -> BeliefRenderParity:
    """Cross-check the table's belief fold against the production fold (17.10).

    Walks every recorded game TWICE — this module's reconstruction
    (:func:`_walk_game`) and the production-fold walk (``eval.funnel``'s
    memory-augmented walk: real agents, reconstructed packets, the exact
    ``suspicion_graph_for_meeting()`` accessor a live meeting reads) — and
    joins them per non-self (meeting, voter, candidate) cell into
    :class:`BeliefRenderParity`. Both walks are hash-verified and offline; a
    (meeting, voter) present in one walk but absent from the other fails loud
    rather than silently under-comparing.
    """

    if not sample_dir.is_dir():
        raise NotADirectoryError(f"replay-set directory not found: {sample_dir}")
    seeds = seeds_on_disk(sample_dir)
    if not seeds:
        raise ValueError(f"no replay-seed-*.jsonl found under {sample_dir}")
    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(sample_dir)
    game_map = load_canonical_map()
    per_seed_roles = roles_by_seed(
        sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
    )
    splits = load_splits(sample_dir)
    fit_seeds = (
        frozenset(splits.train) | frozenset(splits.val) if splits is not None else None
    )
    test_seeds = frozenset(splits.test) if splits is not None else None

    meetings_total = 0
    rows_total = 0
    cells_compared = 0
    raw_mismatches = 0
    trust_mismatches = 0
    max_raw_abs_delta = 0.0
    j1_cells = 0
    j1_rows = 0
    j1_fit_cells = 0
    j1_test_cells = 0
    j1_max = 0.0
    for seed in seeds:
        replay_path = sample_dir / f"replay-seed-{seed}.jsonl"
        roles = per_seed_roles[seed]
        rows = _walk_game(
            replay_path,
            seed=seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            roles=roles,
            game_map=game_map,
        )
        walk = _walk_game_vj(
            replay_path,
            seed=seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            roles=roles,
            game_map=game_map,
        )
        served: dict[tuple[str, PlayerId], dict[PlayerId, SuspicionEntry]] = {
            (meeting.meeting_id, voter): {entry.player_id: entry for entry in graph}
            for meeting in walk.meetings
            for voter, graph in meeting.suspicion_graph_by_voter.items()
        }
        meetings_total += len(walk.meetings)
        for row in rows:
            graph = served.get((row.meeting_id, row.voter))
            if graph is None:
                raise MeetingTableReconstructionError(
                    f"{sample_dir}: meeting {row.meeting_id!r} voter {row.voter!r} "
                    "reconstructed a table row but no production-fold graph — the "
                    "two walks disagree on the meeting roster"
                )
            rows_total += 1
            row_divergent = False
            for feat in row.candidates:
                if feat.is_self:
                    continue
                entry = graph.get(feat.candidate)
                if entry is None:
                    # An absent graph row is production's unseeded neutral
                    # prior — the same 0.5 the table's ``view()`` default
                    # carries for a never-evidenced player.
                    rendered, raw, trust = 0.5, 0.5, 0.5
                else:
                    rendered = entry.suspicion
                    raw = 0.5 + (
                        entry.flag_lift
                        + entry.body_proximity
                        + entry.kill_or_vent_pin
                        + entry.testimony_spread
                        + entry.accusation_carry
                        + entry.carried_hard
                        + entry.carried_soft
                        + entry.unattributed
                    )
                    trust = entry.trust
                cells_compared += 1
                raw_delta = abs(feat.belief_suspicion - raw)
                if raw_delta > SUSPICION_PROVENANCE_ATOL:
                    raw_mismatches += 1
                    max_raw_abs_delta = max(max_raw_abs_delta, raw_delta)
                if abs(feat.belief_trust - trust) > SUSPICION_PROVENANCE_ATOL:
                    trust_mismatches += 1
                divergence = abs(rendered - feat.belief_suspicion)
                if divergence > SUSPICION_PROVENANCE_ATOL:
                    j1_cells += 1
                    row_divergent = True
                    j1_max = max(j1_max, divergence)
                    if fit_seeds is not None and row.seed in fit_seeds:
                        j1_fit_cells += 1
                    if test_seeds is not None and row.seed in test_seeds:
                        j1_test_cells += 1
            if row_divergent:
                j1_rows += 1

    return BeliefRenderParity(
        replay_set_dir=str(sample_dir),
        games_total=len(seeds),
        meetings_total=meetings_total,
        rows_total=rows_total,
        cells_compared=cells_compared,
        raw_mismatches=raw_mismatches,
        trust_mismatches=trust_mismatches,
        max_raw_abs_delta=max_raw_abs_delta,
        j1_divergent_cells=j1_cells,
        j1_divergent_rows=j1_rows,
        j1_divergent_fit_cells=j1_fit_cells if fit_seeds is not None else None,
        j1_divergent_test_cells=j1_test_cells if test_seeds is not None else None,
        j1_max_abs_divergence=j1_max,
    )


__all__ = [
    "BALLOT_AUDIT_MARKERS",
    "SEEN_AT_KILL_WINDOW_TICKS",
    "SPLITS_FILENAME",
    "TARGET_REWRITE_LABELS",
    "BeliefRenderParity",
    "CandidateFeatures",
    "MeetingTable",
    "MeetingTableReconstructionError",
    "MeetingTableRow",
    "SurrogateSplits",
    "ballot_rewrite_labels",
    "build_meeting_table",
    "load_splits",
    "measure_belief_render_parity",
]
