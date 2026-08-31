"""The four evidence-honesty mechanisms, preserved as separate exhibits.

Task 19.11 (audits/audit-phase-19-triage.md §7 item 12 + item 20; §8 rows 10,
14). Phase 19 instruments and labels the evidence pipeline; it deliberately does
NOT change how the pipeline decides (locked decision 1 — prompt templates and
``meetings/`` are untouched). Whether the four substrate fixes below become the
first post-19 gameplay phase is an OWNER decision the triage explicitly reserves,
and the triage's own closing note says that decision must be made on evidence.

This module is that evidence, in executable form: four SEPARATE fixtures, each
anchored to committed bytes by set / seed / meeting index, each with a one-line
statement of what it demonstrates, and each verified against the SERVED DTOs by
``tests/api/test_evidence_mechanisms.py``. They are deliberately not collapsed
into one "wrong ejections" list — they are four different failure mechanisms
with four different fixes, and merging them would lose exactly the distinction
the decision turns on.

Nothing here asserts a bug in the code as specified. Each anchor records what
the pipeline actually does on the committed bytes, so a future phase can tell at
a glance whether its change moved the mechanism — and so a change that moves it
by accident fails loudly here.

The baseline-7 record is that future phase. All four mechanisms are FLIPPED on
its bytes: each anchor now records the baseline-7 reading, and each carries the
baseline-6 reading it replaced as one frozen line, so the flip is legible here
rather than only in the audit (audits/audit-phase-20-baseline-7.md §4).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from api.schemas import EvidenceCategory


@dataclass(frozen=True)
class MechanismFlag:
    """One flag inside an anchored meeting, as the spectator DTO serves it.

    ``speaker_a`` / ``speaker_b`` are the SPEAKERS of the two referenced turns
    (``event_a_id`` / ``event_b_id`` resolved through the transcript) — the
    provenance the flag itself never records and the detector never checks. For
    a self-linked flag both are the single witness.
    """

    kind: str
    category: EvidenceCategory
    subjects: tuple[str, ...]
    speaker_a: str
    speaker_b: str
    self_linked: bool
    weak: bool
    # A distinctive substring of the recorded description, pinned so a
    # re-worded detector message is a loud diff rather than a silent one.
    description_contains: str


@dataclass(frozen=True)
class MechanismAnchor:
    """One committed meeting an exhibit points at."""

    seedset: str
    seed: int
    meeting_index: int
    tick: int
    outcome: str
    ejected_player_id: str | None
    # The ejected player's ground-truth role, from the loader's re-seeded roster
    # (the replay bytes never carry roles).
    ejected_role: str | None
    impostors: tuple[str, ...]
    # Every flag the meeting carries, in recorded order.
    flags: tuple[MechanismFlag, ...]
    # What this meeting read on the baseline-6 bytes, in one line. Frozen: the
    # bytes it describes are gone, and this is the only record of them here.
    baseline6: str

    @property
    def game_id(self) -> str:
        return f"headless-seed-{self.seed}"


@dataclass(frozen=True)
class EvidenceMechanism:
    """One evidence-honesty mechanism plus the bytes that exhibit it."""

    key: str
    title: str
    # THE one-line description of what this fixture demonstrates.
    demonstrates: str
    # What a future phase would have to add for this mechanism to be closed.
    missing_check: str
    audit_ref: str
    # FLIPPED / SURVIVING / RE-ANCHORED, as the baseline-7 record read it.
    status: str
    anchors: tuple[MechanismAnchor, ...]


# ---------------------------------------------------------------------------
# 1. The provenance-impossible sighting (9p2i seed 23, meeting 1)
# ---------------------------------------------------------------------------

PROVENANCE_IMPOSSIBLE_SIGHTING: Final[EvidenceMechanism] = EvidenceMechanism(
    key="provenance_impossible_sighting",
    title="Provenance-impossible sighting",
    demonstrates=(
        "A flag fires on a sighting whose PROVENANCE is never examined: the "
        "detector matches WHAT was claimed against the subject's alibi and "
        "never asks whether the claimant could have seen it — here the "
        "sighting's author is an impostor and its subject the crewmate ejected."
    ),
    # What the exhibit VERIFIES is the authorship + outcome above. The audit's
    # stronger reading — that this particular sighting was physically
    # impossible for its author to make — is cited, not re-derived here; the
    # missing check below is what makes the distinction moot for the pipeline.
    missing_check=(
        "No provenance gate on spoken sightings — a sighting is never checked "
        "against the speaker's own visibility at the tick it names."
    ),
    audit_ref="audits/audit-phase-19-input-claude.md §5.2 (9p2i seed 23 M1)",
    status="FLIPPED",
    anchors=(
        MechanismAnchor(
            seedset="9p2i",
            seed=23,
            meeting_index=1,
            tick=12,
            outcome="SKIPPED",
            ejected_player_id=None,
            ejected_role=None,
            impostors=("p-6", "p-7"),
            # On baseline 8 the mechanism's flag is DEMOTED rather than absent:
            # two survive, both weak-banded and both naming p-4, and the table
            # still skips. The conviction this exhibit is about — a STRONG
            # alibi_vs_sighting carrying a crewmate out — does not happen.
            flags=(
                MechanismFlag(
                    kind="alibi_conflict",
                    category="weak_signal",
                    subjects=("p-4",),
                    speaker_a="p-4",
                    speaker_b="p-4",
                    self_linked=False,
                    weak=True,
                    description_contains="[weak signal: self-stated",
                ),
                MechanismFlag(
                    kind="alibi_vs_sighting",
                    category="weak_signal",
                    subjects=("p-4",),
                    speaker_a="p-4",
                    speaker_b="p-7",
                    self_linked=False,
                    weak=True,
                    description_contains="[weak signal: narrow alibi",
                ),
            ),
            baseline6=(
                "EJECTED p-4 (CREWMATE) on one STRONG alibi_vs_sighting whose "
                "sighting side was authored by impostor p-7"
            ),
        ),
    ),
)


# ---------------------------------------------------------------------------
# 2. The content-vs-own-memory miss (9p2i seed 12, meeting 0)
# ---------------------------------------------------------------------------

CONTENT_VS_OWN_MEMORY_MISS: Final[EvidenceMechanism] = EvidenceMechanism(
    key="content_vs_own_memory_miss",
    title="Content-vs-own-memory miss",
    demonstrates=(
        "A truthful crewmate is ejected on a flag built from two innocents' "
        "statements: citation IDs are validated rigorously, but the restated "
        "CONTENT is never checked against the speaker's own episodic record, "
        "which sits in the same store."
    ),
    missing_check=(
        "No content-vs-memory validation — a misremembered tick or room in a "
        "restated observation passes as evidence against a third party."
    ),
    audit_ref="audits/audit-phase-19-input-claude.md §5.2 (9p2i seed 12 M0)",
    # PARTLY FLIPPED on baseline 8, and the halves are stated separately because
    # they moved in opposite directions. The EVIDENCE half held: the fatal STRONG
    # flag is still gone and both survivors are weak-banded. The OUTCOME half did
    # not: this meeting ejects the crewmate p-5, where the previous recording
    # skipped. So the mechanism's own claim — "no longer ejects an innocent" — is
    # false on these bytes, and the exhibit says so rather than keeping a status
    # its anchor contradicts. Same family as the sole-flag class re-opening
    # (audits/audit-phase-21-rerecord.md §5.1.1); the Wave-2 record rules on it.
    status="PARTLY FLIPPED",
    anchors=(
        MechanismAnchor(
            seedset="9p2i",
            seed=12,
            meeting_index=0,
            tick=7,
            outcome="EJECTED",
            ejected_player_id="p-5",
            ejected_role="CREWMATE",
            impostors=("p-1", "p-7"),
            # The fatal STRONG flag against p-3 is gone. What survives names
            # p-5, and BOTH survivors are weak-banded — but the ejection landed
            # on p-5 anyway, which is the half that regressed.
            flags=(
                MechanismFlag(
                    kind="alibi_conflict",
                    category="weak_signal",
                    subjects=("p-5",),
                    speaker_a="p-5",
                    speaker_b="p-5",
                    self_linked=False,
                    weak=True,
                    description_contains="[weak signal: self-stated",
                ),
                MechanismFlag(
                    kind="alibi_vs_sighting",
                    category="weak_signal",
                    subjects=("p-5",),
                    speaker_a="p-4",
                    speaker_b="p-5",
                    self_linked=False,
                    weak=True,
                    description_contains=(
                        "[weak signal: endpoint-tick si"
                    ),
                ),
            ),
            baseline6=(
                "EJECTED p-3 (CREWMATE) on a STRONG alibi_vs_sighting built "
                "from two innocents' statements (p-3's alibi, p-9's sighting)"
            ),
        ),
    ),
)


# ---------------------------------------------------------------------------
# 3. The one-tick interval artifact (4p1i seeds 41 + 49)
# ---------------------------------------------------------------------------

ONE_TICK_INTERVAL_ARTIFACT: Final[EvidenceMechanism] = EvidenceMechanism(
    key="one_tick_interval_artifact",
    title="One-tick interval artifact",
    demonstrates=(
        "Both 4p1i impostor social wins turn on flags that hang on a SINGLE "
        "tick of a stated interval: seed 49 ejects on two flags the detector "
        "itself stamped `[weak signal: …]` for narrow-window / endpoint-tick "
        "reasons, and seed 41's flag rests on a one-tick roll-call placement "
        "that the Task-18.9 interior exemption promotes to STRONG."
    ),
    missing_check=(
        "Interval extraction and weighting — a one-tick placement contradicted "
        "at its own tick carries the same conviction weight as a real window."
    ),
    audit_ref="audits/audit-phase-19-input-claude.md §5.2 (4p1i seeds 41/49)",
    status="FLIPPED",
    anchors=(
        MechanismAnchor(
            seedset="4p1i",
            seed=49,
            meeting_index=0,
            tick=6,
            outcome="EJECTED",
            ejected_player_id="p-4",
            ejected_role="IMPOSTOR",
            impostors=("p-4",),
            # The interval flags are gone entirely; what convicts is engine
            # -certified role proof.
            flags=(
                MechanismFlag(
                    kind="vent_sighting",
                    category="role_proof",
                    subjects=("p-4",),
                    speaker_a="p-1",
                    speaker_b="p-1",
                    self_linked=True,
                    weak=False,
                    description_contains="venting is impostor-only",
                ),
            ),
            baseline6=(
                "EJECTED p-3 (CREWMATE) at tick 9 on two weak-stamped interval flags"
            ),
        ),
        MechanismAnchor(
            seedset="4p1i",
            seed=41,
            meeting_index=0,
            tick=9,
            outcome="EJECTED",
            ejected_player_id="p-3",
            ejected_role="IMPOSTOR",
            impostors=("p-3",),
            flags=(
                MechanismFlag(
                    kind="vent_sighting",
                    category="role_proof",
                    subjects=("p-3",),
                    speaker_a="p-4",
                    speaker_b="p-4",
                    self_linked=True,
                    weak=False,
                    description_contains="venting is impostor-only",
                ),
            ),
            baseline6=(
                "EJECTED p-4 (CREWMATE) on a STRONG one-tick roll-call "
                "placement, beside the vent flag naming the real impostor"
            ),
        ),
    ),
)


# ---------------------------------------------------------------------------
# 4. The equal-weight conflict (4p1i seed 41, meeting 0)
# ---------------------------------------------------------------------------

EQUAL_WEIGHT_CONFLICT: Final[EvidenceMechanism] = EvidenceMechanism(
    key="equal_weight_conflict",
    title="Equal-weight conflict",
    demonstrates=(
        "One meeting carries both a grounded vent flag naming the real impostor "
        "AND a cross-statement flag naming a crewmate — and the crewmate is the "
        "one ejected, with the impostor's own ballot in the tally."
    ),
    # The audit's account of WHY (both flags enter the suspicion graph at the
    # same +0.30 lift) is cited from audit-phase-19-input-claude.md §5.2 and is
    # NOT re-derived here: this fixture reads served spectator DTOs, which carry
    # no suspicion lift. What it verifies is the co-occurrence and the outcome.
    missing_check=(
        "No hard-evidence precedence — role proof and an unverified statement "
        "pair enter the suspicion graph at the same lift, against the project's "
        "own hard-evidence doctrine."
    ),
    audit_ref="audits/audit-phase-19-input-claude.md §5.1, §5.2 (4p1i seed 41)",
    status="FLIPPED",
    anchors=(
        MechanismAnchor(
            seedset="4p1i",
            seed=41,
            meeting_index=0,
            tick=9,
            outcome="EJECTED",
            ejected_player_id="p-3",
            ejected_role="IMPOSTOR",
            impostors=("p-3",),
            # There is no longer a conflict to weigh: the cross-statement flag
            # against the crewmate is gone and the role proof stands alone.
            flags=ONE_TICK_INTERVAL_ARTIFACT.anchors[1].flags,
            baseline6=ONE_TICK_INTERVAL_ARTIFACT.anchors[1].baseline6,
        ),
    ),
)


# The four mechanisms, in triage order. Iterated by the exhibit tests; the four
# constants above stay individually importable on purpose (item 20 asks for
# SEPARATE fixtures, so a consumer can cite one without dragging in the rest).
EVIDENCE_MECHANISMS: Final[tuple[EvidenceMechanism, ...]] = (
    PROVENANCE_IMPOSSIBLE_SIGHTING,
    CONTENT_VS_OWN_MEMORY_MISS,
    ONE_TICK_INTERVAL_ARTIFACT,
    EQUAL_WEIGHT_CONFLICT,
)
