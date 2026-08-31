"""The evidence taxonomy is total, fail-loud, and pinned corpus-wide (Task 19.11).

audits/audit-phase-19-triage.md §7 item 12 [S-Codex/S-Claude; §8 rows 10, 14]:
the meeting layer carries every flag through one ``ContradictionRef`` shape, so
the spectator surface rendered role PROOF, real cross-statement conflicts, and
detector-stamped weak signals identically — a grounded ``vent_sighting`` drew as
``p-X ↔ p-X`` under a "Contradictions" heading (``meetings/schemas.py``: "both
event ids reference the SAME spoken observation"), and a one-tick artifact drew
at hard-evidence weight.

``api.schemas.classify_evidence`` is the derivation. This module pins three
things about it:

1. **The rules** — one test per row of the table, plus the fail-loud row: an
   unclassifiable flag RAISES and never defaults to a bucket.
2. **Totality over committed bytes** — every flag in ``replays/samples/`` AND
   ``replays/ml_corpus/`` classifies, with an exact per-category count per set.
   Classification drift is then a loud diff, which is the integration guard the
   contract asks for. Task 19.14 implements the eval-side twin against these
   same numbers (the cross-pin).
3. **The render invariants** — the committed self-linked vent records classify
   as proof (so the UI never draws ``p-X ↔ p-X``), and the weak-stamped flags
   the injustice exhibits turn on classify as weak signals (so the UI can
   subordinate them).

The corpus walk reads the RECORDED bytes and runs them through the production
``api.replay_loader._contradiction_view`` — the same derivation the served DTO
uses, no re-implementation — rather than reconstructing 300 games through the
engine, which the determinism gates already cover.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Final, get_args

import pytest

from api.replay_loader import ReplayLoader, _contradiction_view
from api.schemas import (
    CROSS_STATEMENT_KINDS,
    ROLE_PROOF_KINDS,
    ContradictionView,
    EvidenceCategory,
    UnclassifiableEvidenceError,
    classify_evidence,
)
from meetings.schemas import ContradictionRef
from meetings.transcript import WEAK_CONTRADICTION_MARKER_PREFIX

_REPLAYS: Final[Path] = Path(__file__).resolve().parents[2] / "replays"
_SAMPLES: Final[Path] = _REPLAYS / "samples"

# Every committed set, samples AND ml_corpus (the DoD's corpus-wide scope).
_CORPUS_SETS: Final[tuple[str, ...]] = (
    "samples/9p2i",
    "samples/4p1i",
    "ml_corpus/9p2i",
    "ml_corpus/4p1i",
)

# THE PIN. Exact per-category flag counts over the committed bytes, recorded
# 2026-08 against the baseline-6 corpus. These are the numbers Task 19.14's
# eval-side twin must reproduce on the same bytes; a diff here is either a
# corpus change (re-record the numbers, in the PR that changes the corpus) or a
# classification change (which is the thing this pin exists to surface).
# Baseline 6 read 96/64/26, 11/2/3, 313/204/90 and 20/1/0; the record that
# followed closed the cross-statement column (64 -> 2, 204 -> 10) and it stays
# closed here (7 and 8).
_EXPECTED_COUNTS: Final[dict[str, dict[EvidenceCategory, int]]] = {
    # was 92/2/50, 20/0/0, 308/10/110 and 28/0/1.
    "samples/9p2i": {"role_proof": 90, "cross_statement": 7, "weak_signal": 50},
    "samples/4p1i": {"role_proof": 20, "cross_statement": 0, "weak_signal": 0},
    "ml_corpus/9p2i": {"role_proof": 315, "cross_statement": 8, "weak_signal": 126},
    "ml_corpus/4p1i": {"role_proof": 28, "cross_statement": 0, "weak_signal": 1},
}

# The committed replay count per set, pinned so a thinned checkout cannot make
# the counts above pass by walking fewer files.
_EXPECTED_REPLAY_COUNTS: Final[dict[str, int]] = {
    "samples/9p2i": 50,
    "samples/4p1i": 50,
    "ml_corpus/9p2i": 150,
    "ml_corpus/4p1i": 50,
}


def _recorded_flags(set_name: str) -> tuple[list[ContradictionRef], int]:
    """Every recorded flag in one committed set, plus the file count."""

    flags: list[ContradictionRef] = []
    files = sorted((_REPLAYS / set_name).glob("replay-seed-*.jsonl"))
    for path in files:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                record = json.loads(line)
                if record.get("kind") != "meeting":
                    continue
                flags.extend(
                    ContradictionRef.model_validate(raw)
                    for raw in record.get("contradictions", ())
                )
    return flags, len(files)


def _served(flag: ContradictionRef) -> ContradictionView:
    """The flag as the spectator API serves it (production derivation)."""

    return _contradiction_view(flag)


# ---------------------------------------------------------------------------
# The rules table
# ---------------------------------------------------------------------------


def test_vent_sighting_kind_is_role_proof_independently_of_self_linkage() -> None:
    """The KIND rule carries its own weight — DISTINCT event ids on purpose.

    Every committed ``vent_sighting`` is also self-linked, so a test using equal
    ids is satisfied by the self-linkage rule alone and would stay green if the
    kind rule were deleted outright. Distinct ids isolate the kind rule: only
    ``kind in ROLE_PROOF_KINDS`` can produce ``role_proof`` here.
    """

    assert (
        classify_evidence(
            kind="vent_sighting", event_a_id="e-1", event_b_id="e-2", weak=False
        )
        == "role_proof"
    )


def test_self_linked_flag_is_role_proof_whatever_its_kind() -> None:
    """The self-linkage rule stands on its own, not on the kind.

    A flag whose two event ids reference the SAME artifact is not a conflict
    between two statements by construction, so a future self-linked kind cannot
    silently arrive on the surface as a contradiction.
    """

    assert (
        classify_evidence(
            kind="alibi_vs_sighting",
            event_a_id="turn:t-0:obs:0",
            event_b_id="turn:t-0:obs:0",
            weak=False,
        )
        == "role_proof"
    )


def test_weak_stamped_cross_statement_flag_is_a_weak_signal() -> None:
    assert (
        classify_evidence(
            kind="alibi_conflict", event_a_id="e-1", event_b_id="e-2", weak=True
        )
        == "weak_signal"
    )


@pytest.mark.parametrize("kind", sorted(CROSS_STATEMENT_KINDS))
def test_unstamped_cross_statement_kinds_are_contradictions(kind: str) -> None:
    assert (
        classify_evidence(kind=kind, event_a_id="e-1", event_b_id="e-2", weak=False)
        == "cross_statement"
    )


def test_role_proof_beats_the_weak_rule() -> None:
    """Proof stays proof even if a weak marker somehow rode along.

    No committed ``vent_sighting`` carries a weak marker (the grounding
    chokepoint is the precision gate, so there is no weak band for the kind) —
    pinned corpus-wide below. The ordering is fixed here anyway so the two
    rules can never race.
    """

    assert (
        classify_evidence(
            kind="vent_sighting", event_a_id="e-1", event_b_id="e-2", weak=True
        )
        == "role_proof"
    )


@pytest.mark.parametrize(
    ("event_a_id", "event_b_id", "weak"),
    [
        ("e-1", "e-2", False),
        # A weak stamp must NOT smuggle an unknown kind into ``weak_signal``…
        ("e-1", "e-2", True),
        # …and neither must self-linkage smuggle it into ``role_proof``.
        ("e-1", "e-1", False),
        ("e-1", "e-1", True),
    ],
)
def test_unknown_kind_raises_and_never_defaults(
    event_a_id: str, event_b_id: str, weak: bool
) -> None:
    """An unrecognised kind fails loud on EVERY combination of the other inputs.

    The kind gate runs before the weak and self-linkage rules for exactly this
    reason: either rule, evaluated first, would give an unknown kind a category
    instead of a raise — a silent default in the one place the contract
    forbids one ("never add a silent OTHER bucket").
    """

    with pytest.raises(UnclassifiableEvidenceError, match="unclassifiable evidence"):
        classify_evidence(
            kind="task_timing_conflict",
            event_a_id=event_a_id,
            event_b_id=event_b_id,
            weak=weak,
        )


def test_every_recorded_kind_has_a_rule() -> None:
    """The taxonomy covers the FROZEN ``ContradictionRef.kind`` union exactly.

    ``meetings/`` is out of scope for this task, so the guard runs the other
    way: adding a kind there without teaching the taxonomy fails here (and, on
    real bytes, raises in the loader) instead of silently rendering as a
    contradiction.
    """

    recorded = set(get_args(ContradictionRef.model_fields["kind"].annotation))
    assert recorded == ROLE_PROOF_KINDS | CROSS_STATEMENT_KINDS
    assert not (ROLE_PROOF_KINDS & CROSS_STATEMENT_KINDS)


def test_category_values_are_exactly_the_three() -> None:
    assert set(get_args(EvidenceCategory)) == {
        "role_proof",
        "cross_statement",
        "weak_signal",
    }


# ---------------------------------------------------------------------------
# Totality + the corpus-wide count pin
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("set_name", _CORPUS_SETS)
def test_committed_set_classification_counts(set_name: str) -> None:
    flags, file_count = _recorded_flags(set_name)
    assert file_count == _EXPECTED_REPLAY_COUNTS[set_name], (
        f"{set_name} has {file_count} committed replays; the pin expects "
        f"{_EXPECTED_REPLAY_COUNTS[set_name]} — the category counts below are "
        "only meaningful over the whole set"
    )

    counts: Counter[EvidenceCategory] = Counter()
    for flag in flags:
        counts[_served(flag).category] += 1

    expected = _EXPECTED_COUNTS[set_name]
    assert dict(counts) == {k: v for k, v in expected.items() if v > 0}
    # Totality: every recorded flag landed in exactly one category.
    assert sum(counts.values()) == len(flags)


def test_corpus_wide_totals() -> None:
    """The whole committed corpus, in one number per category.

    Computed by CLASSIFYING every recorded flag, not by summing
    :data:`_EXPECTED_COUNTS` — summing the expectation table against literals
    would be arithmetic over two constants and could not fail for any corpus or
    classification reason. The per-set pin above and this total are therefore
    independent readings of the same bytes.
    """

    totals: Counter[EvidenceCategory] = Counter()
    flag_count = 0
    for set_name in _CORPUS_SETS:
        flags, _ = _recorded_flags(set_name)
        flag_count += len(flags)
        for flag in flags:
            totals[_served(flag).category] += 1

    assert dict(totals) == {  # was 448 / 161 / 12
        "role_proof": 453,
        "weak_signal": 177,
        "cross_statement": 15,
    }
    assert sum(totals.values()) == flag_count == 645  # was 621


@pytest.mark.parametrize("set_name", _CORPUS_SETS)
def test_role_proof_is_exactly_the_self_linked_vent_records(set_name: str) -> None:
    """On committed bytes the two role-proof rules agree exactly.

    ``kind == "vent_sighting"`` ⟺ ``event_a_id == event_b_id``, and no such flag
    carries a weak marker. Keeping both rules is deliberate (see
    ``classify_evidence``); pinning their agreement is what says the taxonomy
    has not quietly started classifying on only one of them.
    """

    flags, _ = _recorded_flags(set_name)
    for flag in flags:
        served = _served(flag)
        self_linked = flag.event_a_id == flag.event_b_id
        assert (flag.kind == "vent_sighting") == self_linked, (
            f"{flag.contradiction_id}: kind/self-linkage disagree — the "
            "taxonomy's two role-proof rules would diverge"
        )
        if served.category == "role_proof":
            assert not served.weak
            assert WEAK_CONTRADICTION_MARKER_PREFIX not in flag.description


@pytest.mark.parametrize("set_name", _CORPUS_SETS)
def test_weak_category_matches_the_detector_stamp(set_name: str) -> None:
    """``weak_signal`` is exactly the ``[weak signal: …]``-stamped non-proof set."""

    flags, _ = _recorded_flags(set_name)
    for flag in flags:
        served = _served(flag)
        stamped = WEAK_CONTRADICTION_MARKER_PREFIX in flag.description
        assert served.weak is stamped
        if served.category == "weak_signal":
            assert stamped and served.severity == "weak"
        if served.category == "cross_statement":
            assert not stamped and served.severity == "strong"


# ---------------------------------------------------------------------------
# The served DTO + the render invariants
# ---------------------------------------------------------------------------


def test_served_dto_carries_the_category() -> None:
    """The additive field arrives on a real served payload.

    On baseline 6 this meeting carried all three shapes at once -- two
    cross-statement flags against a truthful witness plus the self-linked
    ``vent_sighting`` naming the actual venter -- and ejected the witness. The
    baseline-7 record closed the cross-statement pair: what is served now is the
    role proof alone, and the ejection follows it.
    """

    replay = ReplayLoader(_SAMPLES / "9p2i").load_replay("headless-seed-17")
    meeting = replay.meetings[0]
    assert [flag.category for flag in meeting.contradictions] == ["role_proof"]
    (proof,) = meeting.contradictions
    assert proof.event_a_id == proof.event_b_id
    assert proof.kind == "vent_sighting"
    assert meeting.ejected_player_id in proof.subjects


@pytest.mark.parametrize("set_name", _CORPUS_SETS)
def test_no_committed_flag_can_render_a_self_linked_pair(set_name: str) -> None:
    """The ``p-X ↔ p-X`` render class is empty across the committed corpus.

    ``MeetingView``'s ``link()`` resolves each endpoint to ITS TURN, so two ids
    print the same label whenever they sit in the same turn — not only when they
    are literally equal. That is three distinct render shapes, and every one of
    them has to avoid joining a label to itself:

    * SELF-LINKED (``event_a_id == event_b_id``) — every committed instance
      classifies ``role_proof``, which renders as a single source;
    * SAME TURN, DISTINCT IDS — a speaker's roll-call placement against their
      own alibi claim; the pair form would print the literal
      ``p-5 (opt-in) ↔ p-5 (opt-in)``, so ``link()`` renders "within …";
    * the ``subjects`` FALLBACK — every committed flag names exactly ONE
      subject, and ``link()`` de-duplicates besides.

    :func:`test_endpoint_render_classes` pins that each shape is non-empty, so
    none of these branches is dead code being asserted about in the abstract.
    """

    flags, _ = _recorded_flags(set_name)

    repeated_subjects = [
        flag.contradiction_id
        for flag in flags
        if len(set(flag.subjects)) != len(flag.subjects)
    ]
    assert repeated_subjects == [], (
        f"{set_name}: flags naming the same subject twice would render "
        f"`p-X ↔ p-X` through the subjects fallback: {repeated_subjects}"
    )

    offenders = [
        flag.contradiction_id
        for flag in flags
        if flag.event_a_id == flag.event_b_id and _served(flag).category != "role_proof"
    ]
    assert offenders == [], (
        f"{set_name}: self-linked flags still classified as a statement "
        f"pair: {offenders}"
    )


# The turn an event id belongs to, mirroring ``MeetingView.eventTurnId`` — the
# SAME segment set (``claim`` / ``obs`` / ``whereabouts``, the last being Task
# 16.7's roll-call self-placement). A flag whose two ids share a turn cannot be
# drawn as a pair, because both endpoints resolve to one label.
_EVENT_TURN: Final[re.Pattern[str]] = re.compile(
    r"^turn:(.+):(?:claim|obs|whereabouts):\d+$"
)


def _endpoint_class(flag: ContradictionRef) -> str:
    if flag.event_a_id == flag.event_b_id:
        return "self_linked"
    turn_a = _EVENT_TURN.match(flag.event_a_id)
    turn_b = _EVENT_TURN.match(flag.event_b_id)
    if turn_a is None or turn_b is None:
        return "unresolvable"
    return "same_turn" if turn_a.group(1) == turn_b.group(1) else "two_turns"


def test_endpoint_render_classes() -> None:
    """Every endpoint shape the meeting view must handle, counted corpus-wide.

    ``link()`` has one branch per class; this pins that each branch is REACHED
    by committed bytes (so none is untested dead code) and that no FOURTH class
    exists. ``unresolvable`` is 0 because every committed event id parses —
    which is only true since ``eventTurnId`` learned the ``whereabouts``
    segment: before that, the 230 flags with a roll-call endpoint fell to the
    subjects fallback and rendered as a bare subject id with no attribution.
    """

    counts: Counter[str] = Counter()
    for set_name in _CORPUS_SETS:
        flags, _ = _recorded_flags(set_name)
        for flag in flags:
            counts[_endpoint_class(flag)] += 1

    # was {"self_linked": 448, "two_turns": 113, "same_turn": 60}
    assert dict(counts) == {"self_linked": 453, "two_turns": 126, "same_turn": 66}
    assert sum(counts.values()) == 645  # was 621
    # Every self-linked flag is role proof; the same-turn class is the
    # self-stated pair the "within …" reading exists for.
    assert counts["unresolvable"] == 0


def test_seed_47_is_entirely_weak_signal() -> None:
    """Seed 47 M2 (§8 row 14): an innocent ejected on weak-stamped flags only.

    All three flags subordinate, so the surface can show at a glance that
    nothing above the weak band supported the ejection.
    """

    replay = ReplayLoader(_SAMPLES / "9p2i").load_replay("headless-seed-47")
    meeting = replay.meetings[2]
    assert meeting.outcome == "EJECTED"
    assert {flag.category for flag in meeting.contradictions} == {"role_proof"}
    assert len(meeting.contradictions) == 1
