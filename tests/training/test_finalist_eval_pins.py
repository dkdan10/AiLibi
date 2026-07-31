"""Task 18.26 — the phase-18 finalist-eval slate, pinned against its own bytes.

``training/reports/results-finalist-eval.jsonl`` is the evidence file two
separate rulings read: Part I's 17.14 rows (baseline-5) already carry the
17.16 default-flip ruling (``tests/scripts/test_champion_flip_ruling.py``),
and the phase-18 rows appended under them (baseline-6) are what Task 18.27
rules on. Both live in ONE file, so this module pins the two properties that
make that safe — the prior record is PRESERVED, and every appended row says
exactly what it measured — from the committed bytes, never from the report's
prose.

What is pinned, and why:

* **The prior record.** The two 17.14 rows stay FIRST and unchanged (report
  §15: "never overwritten and never re-scored at baseline-6"). The always-on
  pin is a **committed digest** of the file's two-row prefix against
  ``git show origin/main:…`` as it stood before this task, because CI checks
  out at ``fetch-depth: 1`` and has no ``origin/main`` ref to diff against.
  When that ref DOES resolve (a full local clone), the test additionally
  parses both sides and compares the decoded **dicts** — semantic identity
  that survives a re-serialisation, which a bare byte compare would not.
* **The slate.** All nine pre-registered arms appear exactly once, in the
  report's own §8.1 listing order. §15 says the phase-18 rows APPEND to the
  file, and the first eight did; the ninth (``p18-crew-c1-gen0``) recorded
  last but was written into its §8.1 SLOT rather than at the tail, so the
  committed row order now equals the §8.1 order exactly and is pinned as
  such. The expected values all come from ONE module-level table,
  :data:`_SLATE`.
* **The stamp conventions, which DIFFER by arm side.** Impostor rows carry a
  single read-back identity (``tactical_policy_stamp``) that must equal both
  the committed sidecar digest and the sha embedded in the artifact directory
  name. Crew rows carry TWO identities in DISTINCT slots — the row's SUBJECT
  is the crew artifact (``crew_tactical_policy_stamp``) and the frozen
  impostor opponent lives in its own ``opponent_*`` fields. That is
  explicitly **not** the ``realpath-rerank-v3`` convention (``training/
  realpath.py``), where ``stamp`` holds the IMPOSTOR read-back even on a crew
  leg and ``opponent_stamp`` holds the DECLARATION; copying that shape here
  would seat the opponent in the subject slot and label four crew diagnostics
  with the champion's identity (the 18.19 conflation guard, read-side). The
  realpath-v3 field NAMES are therefore asserted ABSENT from crew rows —
  a convention drift between the row writer and 18.27's reader would then
  fail loud rather than silently re-attribute an identity.
* **The comparator's opponent-absence proof**, mirroring 18.32's
  ``test_the_comparator_cell_proves_the_impostor_side_is_scripted``: the
  all-scripted arm carries the canonical fsm-default stamp, ZERO learned and
  ZERO crew stamp games, and states ``opponent_absence_proven``.
* **The §12 deciding cell.** The c1 pair's same-seed kill-craft rider
  intersection is persisted on the c1-gen9 row, so 18.27 reads a committed
  cell rather than recomputing one. Its rates and margin are re-derived from
  its own counts, and its excluded seed is tied back to c1-gen0's declared
  stalemate.
* **The split views and the leg clocks.** The §6.b seed-mod-5 partitions,
  with every expected size DERIVED from the arm's own seed list and declared
  fences, and their cells summing back to the flattened parents; plus each
  leg's wall clock, including the two arms that look like broken
  instrumentation and are not.
* **The registered nested cells.** The six rulings' nested sources, persisted
  per arm because the flattened rows dropped them — shape pinned at every
  level, plus the standing no-betrayal invariant (no arm accuses a teammate),
  asserted only where it has content and with the one vacuous arm named.
* **The same-seed comparison blocks.** The F13 quartet's gauges re-measured
  on one common 49-seed set (carried by the three FULL impostor arms; absent
  from ``7f73929d``, whose own block already IS that view), and the c1 pair's
  paired per-seed crew-win table. Both are reconciled against the arms they
  summarise rather than trusted as self-consistent tables.
* **The co-present-departure cell.** Persisted per arm because the flattened
  rows dropped the histogram it is cut from, so the committed number is now
  the only copy. Its rate is re-derived from its own counts, its denominator
  checked against the row's own ``kill_craft``, and the scripted comparator's
  numerator pinned at exactly 0 — the anchor of the learned-vs-scripted split.
* **The honesty pins.** Three of the four crew diagnostics FAIL their validity
  gate, and the rows say so themselves — the failing check names, the
  stalemate replay files, the starved meeting rate. A row that quietly flipped
  to ``passed`` while its counters stayed broken is exactly the drift these
  pins exist to catch, so the failures are pinned as precisely as the passes.

Floors are re-derived arithmetically from the baseline-6 pins
(``eval/watchability.py``: witnessed 6/177, flags 180/165, conversion 78/136
population-relative), never restated as decimal literals.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

import pytest

from orchestrator.replay import fsm_default_tactical_policy_stamp

# The evidence file both rulings read (17.14 rows + the 18.26 append).
_RESULTS_PATH: Final[Path] = Path("training/reports/results-finalist-eval.jsonl")

# -- the preserved Part I record ----------------------------------------------

#: The 17.14 rows, in order, that MUST stay first (report §15).
_PRIOR_ENTRANTS: Final[tuple[str, ...]] = ("utility-es", "policy-es")

#: sha256 of ``git show origin/main:training/reports/results-finalist-eval.jsonl``
#: as it stood before the 18.26 append — i.e. of the file's two-row prefix.
_PRIOR_BLOB_SHA256: Final[str] = (
    "dc667debc04396d3b8caf5df453ed0d93131b18b03745fcfbb3b1b791d26e66c"
)

# -- the baseline-6 supply floors (eval/watchability.py, re-derived) ----------

_WITNESSED_FLOOR: Final[float] = 6 / 177
_FLAGS_FLOOR: Final[float] = 180 / 165
_CONVERSION_PIN: Final[float] = 78 / 136

# -- the substrate every phase-18 arm recorded on (report §9) -----------------

_PROVIDER: Final[str] = "featherless"
_MODEL: Final[str] = "Qwen/Qwen3.6-27B"
_PROMPT_SET: Final[str] = "qwen3_6_27b"
_ROSTER: Final[dict[str, int]] = {
    "num_players": 9,
    "num_impostors": 2,
    "tasks_per_crewmate": 2,
}
_CANONICAL_SEEDS: Final[tuple[int, ...]] = tuple(range(50))

# -- the slate table ----------------------------------------------------------

_IMPOSTOR: Final[str] = "impostor"
_COMPARATOR: Final[str] = "comparator"
_CREW: Final[str] = "crew"

#: A game_over reason that means the CREW won (everything else is an impostor
#: win, or — for a stalled game — no win at all).
_CREW_WIN_REASONS: Final[frozenset[str]] = frozenset(
    {"CREWMATE_EJECT", "CREWMATE_TASKS"}
)

#: The F13 quartet re-measured on ONE seed set: the three FULL impostor arms
#: cut down to 7f73929d's native 49 seeds, so the four arms are compared on
#: identical games. Measured values only — every floor is re-derived.
_F13_EXCLUDED_SEED: Final[int] = 35
_F13_INTERSECTION_MEASURED: Final[dict[str, dict[str, float]]] = {
    "p18-imp-ea4bc955": {
        "witnessed_event_rate": 0.15625,
        "flags_per_meeting": 0.9536423841059603,
        "testimony_backed_conversion": 0.3716216216216216,
    },
    "p18-imp-bfd145cb": {
        "witnessed_event_rate": 0.1507537688442211,
        "flags_per_meeting": 0.8974358974358975,
        "testimony_backed_conversion": 0.3493150684931507,
    },
    "p18-imp-6d327dcb": {
        "witnessed_event_rate": 0.2275132275132275,
        "flags_per_meeting": 0.9559748427672956,
        "testimony_backed_conversion": 0.43661971830985913,
    },
}

#: The shape of ``registered_nested_cells`` — the six registered rulings whose
#: nested sources the flattened rows dropped, re-persisted verbatim.
_NESTED_KEYS: Final[frozenset[str]] = frozenset(
    {
        "note",
        "frame_conversions",
        "teammate_accusations",
        "alibi_survival",
        "effective_deflection",
        "action_entropy",
    }
)
_RATIO_KEYS: Final[frozenset[str]] = frozenset({"numerator", "denominator"})
_ENTROPY_KEYS: Final[frozenset[str]] = frozenset(
    {"mean_conditional_entropy", "agents", "decisions"}
)

#: Spot pins on the two slate-critical arms' frame-conversion cell.
_NESTED_FRAME_CONVERSIONS: Final[dict[str, tuple[int, int]]] = {
    "p18-imp-ea4bc955": (10, 151),
    "p18-fsm-comparator": (6, 148),
}

#: The §6.b split-reproducibility views: seed mod 5 partitioned 012/3/4.
_MOD5_RESIDUES: Final[dict[str, tuple[int, ...]]] = {
    "train_mod5_012": (0, 1, 2),
    "val_mod5_3": (3,),
    "test_mod5_4": (4,),
}
#: The eleven ``{n, d}`` claim cells per split; ``one_hop_point_biserial`` is
#: the twelfth and carries ``{r, kills_total}`` instead.
_MOD5_RATIO_CELLS: Final[frozenset[str]] = frozenset(
    {
        "alibi_survival",
        "co_present_departure",
        "crew_witnessed_kills",
        "effective_deflection",
        "false_vouch_corroboration",
        "false_vouch_fabricated",
        "false_vouch_saw_player",
        "frame_attempts",
        "frame_conversions",
        "off_menu",
        "teammate_accusations",
    }
)

#: The campaign's last recorded event — 7f73929d's post-PR retry leg.
_CAMPAIGN_LAST_EVENT_AT: Final[str] = "2026-07-31T18:00:06Z"
#: c2-gen0's wall clock is REAL, not a missing measurement: every game ended
#: before a meeting convened, so almost no LLM call was ever made.
_C2_GEN0_WALL_SECONDS: Final[int] = 27

#: The comparator's cells re-cut onto the F13 49-seed intersection.
_COMPARATOR_INTERSECTION_COUNTS: Final[dict[str, int]] = {
    "crew_witnessed_kills": 8,
    "kills_total": 170,
    "co_present_ge1_kills": 0,
    "impostor_decisions": 2219,
    "off_menu_total": 0,
}

#: The c1 pair's paired per-seed crew-win table (McNemar-style discordant
#: counts) over the 49 seeds both sides finalized.
_C1_PAIRED_EXCLUDED_SEED: Final[int] = 20
_C1_PAIRED_49: Final[dict[str, int]] = {
    "both_win": 20,
    "gen9_only_win": 6,
    "gen0_only_win": 5,
    "neither_win": 18,
}

#: The §8.1 arm listing, in the report's own order — quoted from the
#: pre-registration, not from the file, so the file is checked AGAINST the
#: plan rather than described by itself.
_SLATE_8_1_ORDER: Final[tuple[str, ...]] = (
    "p18-imp-ea4bc955",
    "p18-imp-bfd145cb",
    "p18-imp-6d327dcb",
    "p18-imp-7f73929d",
    "p18-fsm-comparator",
    "p18-crew-c1-gen9",
    "p18-crew-c1-gen0",
    "p18-crew-c2-gen9",
    "p18-crew-c2-gen0",
)


@dataclass(frozen=True)
class Arm:
    """One slate arm's expected row, read off the committed bytes.

    ``stamp_games`` is the arm's SUBJECT-side read-back count
    (``stamp_verified_games`` on an impostor/comparator row,
    ``crew_stamp_verified_games`` on a crew row); it drops below
    ``games_total`` only where a game recorded no ``game_over`` to read a stamp
    from. ``stalemate_replays`` is ``None`` where the row carries no
    ``stalemate_games_no_game_over`` key at all (the impostor and comparator
    rows), distinguishing "absent" from "empty".
    """

    entrant: str
    side: str
    weights_sha256: str | None
    artifact_path: str | None
    policy_id: str
    method: str
    encoder_version: str
    anchor_policy: str
    games_total: int
    stamp_games: int
    missing_seeds: tuple[int, ...]
    impostor_wins: int
    impostor_win_rate: float
    meeting_rate: float
    mean_score: float
    median_score: float
    referee_passed: bool
    validity_passed: bool
    validity_failures: frozenset[str]
    stalemate_replays: tuple[str, ...] | None
    #: The registered co-present-departure cell's NUMERATOR — kills the
    #: mover left with at least one crewmate co-present. Its denominator is
    #: not carried here: it must equal the row's own ``kill_craft.kills_total``
    #: and is derived from it, so the two can never disagree silently.
    co_present_ge1_kills: int


#: The pre-registered slate, in committed row order (== the §8.1 order). Every
#: test below derives its expectations from this table, and none of them names
#: an arm's numbers anywhere else, so an arm is ONE entry.
_SLATE: Final[tuple[Arm, ...]] = (
    Arm(
        entrant="p18-imp-ea4bc955",
        side=_IMPOSTOR,
        weights_sha256=(
            "ea4bc955dfe0beb8f82663d659e6c990083cebb26a1dab9600c6b68b7783d79f"
        ),
        artifact_path=(
            "training/artifacts/coevo/intermediates/run-02-utility-lambda4/gen-2/"
            "ea4bc955dfe0beb8f82663d659e6c990083cebb26a1dab9600c6b68b7783d79f"
        ),
        policy_id="coevo-run-02-utility-lambda4-intermediate-gen-2",
        method="alternating-freeze-es",
        encoder_version="impostor-option-features-v1",
        anchor_policy="fsm-default",
        games_total=50,
        stamp_games=50,
        missing_seeds=(),
        impostor_wins=26,
        impostor_win_rate=0.52,
        meeting_rate=1.0,
        mean_score=48.9,
        median_score=50.15,
        referee_passed=False,
        validity_passed=True,
        validity_failures=frozenset(),
        stalemate_replays=None,
        co_present_ge1_kills=20,
    ),
    Arm(
        entrant="p18-imp-bfd145cb",
        side=_IMPOSTOR,
        weights_sha256=(
            "bfd145cb4883fa7fd0f009811cdc6e660b4f4a62105534f384afbb45b2c12ee8"
        ),
        artifact_path=(
            "training/artifacts/coevo/runnerups/run-02-utility-lambda4/gen-9/"
            "bfd145cb4883fa7fd0f009811cdc6e660b4f4a62105534f384afbb45b2c12ee8"
        ),
        policy_id="coevo-run-02-utility-lambda4-runnerup-gen-9",
        method="alternating-freeze-es",
        encoder_version="impostor-option-features-v1",
        anchor_policy="fsm-default",
        games_total=50,
        stamp_games=50,
        missing_seeds=(),
        impostor_wins=28,
        impostor_win_rate=0.56,
        meeting_rate=1.0,
        mean_score=47.24,
        median_score=48.0,
        referee_passed=False,
        validity_passed=True,
        validity_failures=frozenset(),
        stalemate_replays=None,
        co_present_ge1_kills=21,
    ),
    Arm(
        entrant="p18-imp-6d327dcb",
        side=_IMPOSTOR,
        weights_sha256=(
            "6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0"
        ),
        artifact_path=(
            "training/artifacts/coevo/run-01-utility-champion/impostor/gen-3/"
            "6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0"
        ),
        policy_id="coevo-run-01-utility-champion-alternating-freeze-champion-gen3",
        method="alternating-freeze-es",
        encoder_version="impostor-option-features-v1",
        anchor_policy="fsm-default",
        games_total=50,
        stamp_games=50,
        missing_seeds=(),
        impostor_wins=19,
        impostor_win_rate=0.38,
        meeting_rate=1.0,
        mean_score=51.15,
        median_score=63.95,
        referee_passed=False,
        validity_passed=True,
        validity_failures=frozenset(),
        stalemate_replays=None,
        co_present_ge1_kills=36,
    ),
    Arm(
        entrant="p18-imp-7f73929d",
        side=_IMPOSTOR,
        weights_sha256=(
            "7f73929d5b91f4afe67adc1b2ac7ca42bdd3ab1f49ed0393342ab21c7db0985e"
        ),
        artifact_path=(
            "training/artifacts/coevo/runnerups/run-03-utility-bcanchor/gen-8/"
            "7f73929d5b91f4afe67adc1b2ac7ca42bdd3ab1f49ed0393342ab21c7db0985e"
        ),
        policy_id="coevo-run-03-utility-bcanchor-runnerup-gen-8",
        method="alternating-freeze-es",
        encoder_version="impostor-option-features-v1",
        # The slate's ONLY filtered-BC-anchored arm (§8.1, the F13 test arm).
        anchor_policy="filtered-bc-anchor",
        games_total=49,
        stamp_games=49,
        missing_seeds=(35,),
        impostor_wins=21,
        impostor_win_rate=21 / 49,
        meeting_rate=1.0,
        mean_score=52.49,
        median_score=53.7,
        referee_passed=False,
        validity_passed=True,
        validity_failures=frozenset(),
        stalemate_replays=None,
        co_present_ge1_kills=35,
    ),
    Arm(
        entrant="p18-fsm-comparator",
        side=_COMPARATOR,
        weights_sha256=None,
        artifact_path=None,
        policy_id="fsm-default",
        method="scripted-fsm",
        encoder_version="none",
        anchor_policy="fsm-default",
        games_total=50,
        stamp_games=50,
        missing_seeds=(),
        impostor_wins=13,
        impostor_win_rate=0.26,
        meeting_rate=1.0,
        mean_score=54.96,
        median_score=53.55,
        # The slate's ONLY referee PASS.
        referee_passed=True,
        validity_passed=True,
        validity_failures=frozenset(),
        stalemate_replays=None,
        co_present_ge1_kills=0,
    ),
    Arm(
        entrant="p18-crew-c1-gen9",
        side=_CREW,
        weights_sha256=(
            "0bf179b719a67c1b40f97377ba49bad6512d08932e0d944e4d024691f60e71df"
        ),
        artifact_path=(
            "training/artifacts/coevo/run-c1-crew-owned-tasks/crew/gen-9/"
            "0bf179b719a67c1b40f97377ba49bad6512d08932e0d944e4d024691f60e71df"
        ),
        policy_id=(
            "coevo-run-c1-crew-owned-tasks-crew-alternating-freeze-champion-gen9-"
            "0bf179b719a67c1b40f97377ba49bad6512d08932e0d944e4d024691f60e71df"
        ),
        method="alternating-freeze-es",
        encoder_version="crew-option-features-v2",
        anchor_policy="fsm-default",
        games_total=50,
        stamp_games=50,
        missing_seeds=(),
        impostor_wins=24,
        impostor_win_rate=0.48,
        meeting_rate=1.0,
        mean_score=47.99,
        median_score=49.2,
        referee_passed=False,
        validity_passed=True,
        validity_failures=frozenset(),
        stalemate_replays=None,
        co_present_ge1_kills=21,
    ),
    Arm(
        entrant="p18-crew-c1-gen0",
        side=_CREW,
        weights_sha256=(
            "bd6fdd0a030a01cc57f2ef8c95abf66f46d8cbc5ac270e04ae74a6cab587f19c"
        ),
        # The c1 CONTROL dir, named for the control and NOT sha-named — the
        # dir-name-sha identity stays an impostor-arm pin.
        artifact_path=(
            "training/artifacts/coevo/realpath-crew/controls/crew-owned-tasks-es-gen0"
        ),
        policy_id="crew-owned-tasks-es",
        method="crew-utility-scorer-es",
        encoder_version="crew-option-features-v2",
        anchor_policy="fsm-default",
        games_total=50,
        # One seed stalled out with no ``game_over`` row, so 49 games' bytes
        # could prove either identity — and the referee scored NOTHING.
        stamp_games=49,
        missing_seeds=(),
        impostor_wins=24,
        impostor_win_rate=0.48,
        meeting_rate=1.0,
        mean_score=0.0,
        median_score=0.0,
        referee_passed=False,
        validity_passed=False,
        validity_failures=frozenset(
            {"all_games_reach_game_over", "cost_and_provenance_exact"}
        ),
        stalemate_replays=("replay-seed-20.jsonl",),
        co_present_ge1_kills=25,
    ),
    Arm(
        entrant="p18-crew-c2-gen9",
        side=_CREW,
        weights_sha256=(
            "515fc066f7aafc5d3603ab531adb9fe78cd496192c7565e9d8b4d3ff7b09a635"
        ),
        artifact_path=(
            "training/artifacts/coevo/run-c2-crew-general/crew/gen-9/"
            "515fc066f7aafc5d3603ab531adb9fe78cd496192c7565e9d8b4d3ff7b09a635"
        ),
        policy_id=(
            "coevo-run-c2-crew-general-crew-alternating-freeze-champion-gen9-"
            "515fc066f7aafc5d3603ab531adb9fe78cd496192c7565e9d8b4d3ff7b09a635"
        ),
        method="alternating-freeze-es",
        encoder_version="crew-option-features-v1",
        anchor_policy="fsm-default",
        games_total=50,
        # Two seeds stalled out with no ``game_over`` row, so only 48 games'
        # bytes could prove either identity.
        stamp_games=48,
        missing_seeds=(),
        impostor_wins=41,
        impostor_win_rate=0.82,
        meeting_rate=0.6,
        mean_score=0.0,
        median_score=0.0,
        referee_passed=False,
        validity_passed=False,
        validity_failures=frozenset(
            {"all_games_reach_game_over", "cost_and_provenance_exact"}
        ),
        stalemate_replays=("replay-seed-19.jsonl", "replay-seed-20.jsonl"),
        co_present_ge1_kills=25,
    ),
    Arm(
        entrant="p18-crew-c2-gen0",
        side=_CREW,
        weights_sha256=(
            "888046d082daf62853c9d10d25dde04e20691c042dcd6a6609492d554ed569bf"
        ),
        # A gen-0 CONTROL artifact dir is named for the control, not for its
        # digest — the dir-name-sha identity is an impostor-arm pin only.
        artifact_path=(
            "training/artifacts/coevo/realpath-crew/controls/crew-utility-es-gen0"
        ),
        policy_id="crew-utility-es",
        method="crew-utility-scorer-es",
        encoder_version="crew-option-features-v1",
        anchor_policy="fsm-default",
        games_total=50,
        stamp_games=50,
        missing_seeds=(),
        impostor_wins=49,
        impostor_win_rate=0.98,
        # Zero meetings ever convened: the meeting economy never opened.
        meeting_rate=0.0,
        mean_score=0.1,
        median_score=0.1,
        referee_passed=False,
        validity_passed=False,
        validity_failures=frozenset(
            {"meeting_rate_and_resolution", "cost_and_provenance_exact"}
        ),
        stalemate_replays=(),
        co_present_ge1_kills=19,
    ),
)

#: The frozen impostor opponent every crew diagnostic was recorded against
#: (§8.1: "vs the frozen champion ``ea4bc955…``") — derived from the slate's
#: own impostor arm, so the two can never drift apart.
_FROZEN_OPPONENT: Final[Arm] = _SLATE[0]


# -- loaders ------------------------------------------------------------------


def _lines() -> list[str]:
    """The committed evidence file's lines, in file order."""

    return _RESULTS_PATH.read_text(encoding="utf-8").splitlines()


def _rows() -> dict[str, dict[str, Any]]:
    """Every committed row, keyed by entrant (the house loader shape)."""

    rows: dict[str, dict[str, Any]] = {}
    for line in _lines():
        row: dict[str, Any] = json.loads(line)
        rows[row["entrant"]] = row
    return rows


def _arms(*sides: str) -> tuple[Arm, ...]:
    """The slate arms on the named sides, in slate order."""

    return tuple(arm for arm in _SLATE if arm.side in sides)


def _subject_stamp(row: dict[str, Any], arm: Arm) -> dict[str, Any]:
    """The row's SUBJECT-side stamp — the crew slot on a crew row."""

    key = "crew_tactical_policy_stamp" if arm.side == _CREW else "tactical_policy_stamp"
    stamp: dict[str, Any] = row[key]
    return stamp


def _gauges(row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """The row's supply gauges, keyed by gauge name."""

    return {gauge["name"]: gauge for gauge in row["watchability"]["supply_gauges"]}


def _fenced_seeds(row: dict[str, Any]) -> frozenset[int]:
    """The seeds a row's INSTRUMENT view excludes — its declared stalemates.

    Parsed from the row's own ``stalemate_games_no_game_over`` filenames, so
    the fence and the reason for it are the same fact. An absent key (the
    impostor and comparator rows) fences nothing.
    """

    stalled: list[str] = row.get("stalemate_games_no_game_over") or []
    return frozenset(
        int(name.removeprefix("replay-seed-").removesuffix(".jsonl"))
        for name in stalled
    )


def _summed_across_splits(block: dict[str, Any], cell: str, field: str) -> int:
    """One mod-5 claim cell's field, summed across the three splits."""

    return sum(int(block[split][cell][field]) for split in _MOD5_RESIDUES)


def _crew_wins_excluding(row: dict[str, Any], seed: int) -> int:
    """The row's crew wins with one seed removed, read from its own per-game bytes.

    A paired cut may only be compared against the same arm's wins over the
    SAME seeds. Rather than assume the excluded seed was a loss, this looks up
    what actually happened in it: a crew win there is subtracted, an impostor
    win or a stalled game is not.
    """

    per_game = {game["seed"]: game for game in row["watchability"]["per_game"]}
    excluded = per_game[seed]
    was_crew_win = excluded["reason"] in _CREW_WIN_REASONS
    return int(row["core"]["crew_wins"]) - (1 if was_crew_win else 0)


def _assert_digest_closes_on_the_artifact_bytes(
    artifact_dir: str, declared: str
) -> None:
    """A declared digest closes on the committed artifact BYTES, on disk.

    Two links, both opened from disk rather than inferred from the row:
    ``<dir>/weights.json.sha256`` (``sha256sum`` format, so the digest is the
    line's first token) must NAME ``declared``, and ``<dir>/weights.json``
    must HASH to it. Without the second link a sidecar could name a genome
    that no longer sits beside it, and the row's self-consistent fields would
    never notice.
    """

    directory = Path(artifact_dir)
    sidecar = directory / "weights.json.sha256"
    payload = directory / "weights.json"
    assert sidecar.is_file(), f"missing committed sidecar: {sidecar}"
    assert payload.is_file(), f"missing committed genome: {payload}"

    recorded = sidecar.read_text(encoding="utf-8").split()[0]
    assert recorded == declared, f"{sidecar} names {recorded}, row declares {declared}"
    computed = hashlib.sha256(payload.read_bytes()).hexdigest()
    assert computed == recorded, f"{payload} hashes to {computed}, sidecar {recorded}"


def _origin_main_prior_rows() -> list[dict[str, Any]] | None:
    """``origin/main``'s FIRST TWO evidence rows, or ``None``.

    ``origin/main`` is a MOVABLE ref: today it holds the two 17.14 rows, and
    the moment this work merges it holds all eleven. So the comparison is
    against the PREFIX, never the whole file — slicing here is the
    preservation invariant itself, since the first two rows of main's file are
    forever the 17.14 rows no matter how many phase-18 rows sit under them.
    Comparing full files instead would pass only until merge and then fail on
    every full clone.

    ``None`` when the ref does not resolve — CI checks out at
    ``fetch-depth: 1`` and carries no ``origin/main``, where the committed
    digest pin is the proof instead.
    """

    result = subprocess.run(
        ["git", "show", f"origin/main:{_RESULTS_PATH.as_posix()}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    lines = result.stdout.splitlines()[: len(_PRIOR_ENTRANTS)]
    return [json.loads(line) for line in lines]


# -- file integrity: the prior record is preserved ---------------------------


def test_the_two_17_14_rows_stay_first_and_unchanged() -> None:
    """Part I's record is PRESERVED under the phase-18 append (report §15).

    The 17.16 ruling re-derives itself from these two rows every run, so an
    append that rewrote, re-ordered or re-scored them would silently move a
    committed ruling.

    The PRIMARY pin is immutable: the file's two-row prefix still hashes to
    the pre-append ``origin/main`` blob digest, which needs no git and holds
    forever. The secondary check is against the MOVABLE ``origin/main`` ref
    when it resolves — and it compares PREFIX to PREFIX, because that ref
    gains the phase-18 rows the moment this work merges. Prefix-to-prefix is
    the invariant worth stating anyway: whatever else main accumulates, its
    first two rows stay these two. The comparison decodes both sides and
    compares dicts, so it survives a re-serialisation a byte compare would
    not.
    """

    lines = _lines()
    assert len(lines) == len(_PRIOR_ENTRANTS) + len(_SLATE)

    prior_lines = lines[: len(_PRIOR_ENTRANTS)]
    assert [json.loads(line)["entrant"] for line in prior_lines] == list(
        _PRIOR_ENTRANTS
    )

    prefix = "".join(f"{line}\n" for line in prior_lines).encode("utf-8")
    assert hashlib.sha256(prefix).hexdigest() == _PRIOR_BLOB_SHA256

    baseline = _origin_main_prior_rows()
    if baseline is not None:
        assert [json.loads(line) for line in prior_lines] == baseline
        assert [row["entrant"] for row in baseline] == list(_PRIOR_ENTRANTS)

    # ... and they are still the baseline-5 rows, never re-scored at 6.
    rows = _rows()
    for entrant in _PRIOR_ENTRANTS:
        assert rows[entrant]["watchability"]["baseline_id"] == "baseline-5"


def test_every_slate_arm_appears_exactly_once_in_the_pre_registered_order() -> None:
    """The phase-18 rows ARE the §8.1 slate, complete and in §8.1 order.

    File ORDER is the pin, not just membership: 18.27's tables join on these
    rows, so a duplicated, re-ordered, missing or unregistered row must fail
    here rather than be read as another arm's cell. The order is checked
    against the report's own §8.1 listing (quoted in :data:`_SLATE_8_1_ORDER`)
    rather than against the file describing itself — the ninth arm recorded
    last but was written into its §8.1 SLOT, so plan and file agree exactly,
    and equality is what says the slate is COMPLETE at nine.
    """

    recorded = [json.loads(line)["entrant"] for line in _lines()]
    slate = [arm.entrant for arm in _SLATE]

    assert recorded[len(_PRIOR_ENTRANTS) :] == slate
    assert len(set(recorded)) == len(recorded)
    assert tuple(slate) == _SLATE_8_1_ORDER


def test_every_phase_18_row_records_the_same_substrate_and_roster() -> None:
    """One substrate, one roster, one price across the whole slate (§9).

    A slate is only comparable if every arm played the same game: same
    provider and model, same prompt set, same 9p/2i roster, and the local
    $0 price. The seed set is pinned per-arm from the table, so a partial
    recording is a DECLARED gap rather than a quiet short set.
    """

    rows = _rows()
    for arm in _SLATE:
        recording = rows[arm.entrant]["recording"]
        assert recording["provider"] == _PROVIDER
        assert recording["model"] == _MODEL
        assert recording["prompt_set"] == _PROMPT_SET
        assert recording["cost_usd"] == 0.0
        assert recording["roster"] == _ROSTER
        assert "(Task 18.26)" in recording["seam"]

        expected_seeds = [
            seed for seed in _CANONICAL_SEEDS if seed not in arm.missing_seeds
        ]
        assert recording["seeds"] == expected_seeds
        assert len(recording["seeds"]) == arm.games_total

        assert rows[arm.entrant]["watchability"]["baseline_id"] == "baseline-6"
        assert rows[arm.entrant]["watchability"]["roster_key"] == "9p2i"


# -- impostor arms: one identity, proved on every game ------------------------


def test_impostor_rows_name_the_artifact_they_loaded_on_every_game() -> None:
    """Three digests agree, and the bytes of every game proved it.

    The stamp is READ BACK from the recordings, so the identity chain has to
    close on all three surfaces before a cell is trusted: the read-back
    ``weights_sha256``, the committed sidecar digest, and the sha embedded in
    the artifact DIRECTORY name (§8.1: "dir name == full ``weights_sha256``").
    The proof is counted, too — the stamp is verified on every decisive game,
    which equals the games scored and the seeds recorded.
    """

    rows = _rows()
    for arm in _arms(_IMPOSTOR):
        row = rows[arm.entrant]
        assert arm.weights_sha256 is not None
        assert arm.artifact_path is not None

        stamp = _subject_stamp(row, arm)
        assert stamp["weights_sha256"] == arm.weights_sha256
        assert row["committed_weights_sha256"] == arm.weights_sha256
        assert row["artifact_path"] == arm.artifact_path
        assert Path(arm.artifact_path).name == arm.weights_sha256
        assert row["committed_sidecar"] == f"{arm.artifact_path}/weights.json.sha256"
        assert row["stamp_equals_committed_sha256"] is True

        assert stamp["policy_id"] == arm.policy_id
        assert stamp["method"] == arm.method
        assert stamp["encoder_version"] == arm.encoder_version
        assert stamp["anchor_policy"] == arm.anchor_policy

        # The proof count: every decisive game named the loaded candidate.
        assert row["stamp_verified_games"] == arm.stamp_games
        assert row["stamp_verified_games"] == row["core"]["games_total"]
        assert row["stamp_verified_games"] == len(row["recording"]["seeds"])
        assert "read back from the recording bytes" in row["stamp_source"]


def test_the_f13_arm_is_the_49_seed_arm_and_declares_the_missing_seed() -> None:
    """``7f73929d`` is scored at n=49, with seed 35 declared absent.

    The short set is a DECLARED gap, not a silently truncated run: the row's
    seed list is the canonical 0-49 minus exactly one seed, and every
    denominator on the row follows it down to 49. The win rate is therefore
    21/49, never rounded into a 50-game rate.
    """

    rows = _rows()
    arm = next(
        candidate for candidate in _SLATE if candidate.entrant.endswith("7f73929d")
    )
    row = rows[arm.entrant]

    assert arm.missing_seeds == (35,)
    assert row["recording"]["seeds"] == sorted(set(range(50)) - {35})
    assert row["core"]["games_total"] == 49
    assert row["stamp_verified_games"] == 49
    assert row["watchability"]["games_total"] == 49
    assert row["validity_gate"]["games_total"] == 49
    assert row["core"]["impostor_win_rate"] == pytest.approx(21 / 49)


# -- the comparator: the opponent slot was EMPTY, and it is proved ------------


def test_the_comparator_row_proves_the_opponent_slot_was_empty() -> None:
    """The all-scripted arm loaded nothing, and says so with counted proof.

    The mirror of 18.32's comparator-cell proof (``tests/training/
    test_realpath.py``): an absent learned stamp MEANS the scripted FSM, and
    the row does not ASSUME that absence — it carries the canonical
    fsm-default stamp, states ZERO learned and ZERO crew stamp games, and
    flags ``opponent_absence_proven``. No artifact, no sidecar, no digest to
    compare against: those three fields are null, not empty strings, so a
    reader can never join this arm onto an artifact identity.
    """

    rows = _rows()
    arm = next(candidate for candidate in _SLATE if candidate.side == _COMPARATOR)
    row = rows[arm.entrant]

    assert row["artifact_path"] is None
    assert row["committed_sidecar"] is None
    assert row["committed_weights_sha256"] is None
    assert row["stamp_equals_committed_sha256"] is None

    stamp = row["tactical_policy_stamp"]
    assert stamp["policy_id"] == "fsm-default"
    assert stamp["weights_sha256"] == "none"
    assert stamp["encoder_version"] == "none"
    assert stamp["method"] == "scripted-fsm"
    assert stamp["anchor_policy"] == "fsm-default"
    # ... and that is the canonical stand-in verbatim, not a look-alike.
    assert stamp == fsm_default_tactical_policy_stamp().model_dump()

    assert row["learned_stamp_games"] == 0
    assert row["crew_stamp_games"] == 0
    assert row["opponent_absence_proven"] is True
    # No crew identity on this row at all — absent, not null-valued.
    assert "crew_tactical_policy_stamp" not in row
    assert row.get("crew_tactical_policy_stamp") is None

    assert row["core"]["games_total"] == 50
    assert row["stamp_verified_games"] == 50


def test_the_comparator_is_the_slates_only_referee_pass() -> None:
    """One arm clears baseline-6, and it is the scripted one.

    Pinned as a slate-wide property, not an isolated cell: the comparator
    passes with every supply gauge strictly ABOVE its floor, and no learned
    arm passes. The conversion floor is population-relative, so it is
    re-derived from the flag supply the arm actually produced rather than
    restated — a starved flag economy is what LIFTS the bar it then misses.
    """

    rows = _rows()
    passing = {arm.entrant for arm in _SLATE if arm.referee_passed}
    assert passing == {"p18-fsm-comparator"}

    comparator = rows["p18-fsm-comparator"]
    assert comparator["watchability"]["referee_passed"] is True
    assert comparator["watchability"]["supply_floors_passed"] is True
    assert comparator["watchability"]["integrity_ok"] is True
    assert comparator["watchability"]["mean_score"] == pytest.approx(54.96, abs=0.01)
    assert comparator["watchability"]["median_score"] == pytest.approx(53.55, abs=0.01)

    gauges = _gauges(comparator)
    witnessed = gauges["witnessed_event_rate"]
    assert witnessed["floor"] == pytest.approx(_WITNESSED_FLOOR)
    assert witnessed["measured"] > witnessed["floor"]
    assert witnessed["passed"] is True

    flags = gauges["flags_per_meeting"]
    assert flags["floor"] == pytest.approx(_FLAGS_FLOOR)
    assert flags["measured"] > flags["floor"]
    assert flags["passed"] is True

    conversion = gauges["testimony_backed_conversion"]
    assert conversion["measured"] > conversion["floor"]
    assert conversion["passed"] is True
    assert conversion["floor"] == pytest.approx(
        min(1.0, _CONVERSION_PIN * (_FLAGS_FLOOR / flags["measured"]))
    )


def test_every_arms_floors_are_the_baseline_6_pins_re_derived() -> None:
    """The floors are one baseline's arithmetic, per arm, not per-row literals.

    ``witnessed_event_rate`` and ``flags_per_meeting`` are fixed baseline-6
    pins; ``testimony_backed_conversion`` is POPULATION-RELATIVE — derived
    from each arm's own measured flag supply (16.11). Re-deriving all three
    here is what keeps a re-record from quietly re-basing an arm onto floors
    another arm never faced. The split-half read's ``threshold_base`` must
    name the same number the referee judged against, or the noise verdict and
    the floor verdict would be about different bars.
    """

    rows = _rows()
    for arm in _SLATE:
        gauges = _gauges(rows[arm.entrant])
        split_half = rows[arm.entrant]["split_half"]

        assert gauges["witnessed_event_rate"]["floor"] == pytest.approx(
            _WITNESSED_FLOOR
        )
        assert gauges["flags_per_meeting"]["floor"] == pytest.approx(_FLAGS_FLOOR)

        measured_flags = gauges["flags_per_meeting"]["measured"]
        expected_conversion_floor = (
            1.0
            if measured_flags is None
            else min(1.0, _CONVERSION_PIN * (_FLAGS_FLOOR / measured_flags))
        )
        assert gauges["testimony_backed_conversion"]["floor"] == pytest.approx(
            expected_conversion_floor
        )

        for name, gauge in gauges.items():
            assert split_half[name]["threshold_base"] == pytest.approx(gauge["floor"])


# -- crew arms: two identities, DISTINCT slots --------------------------------


def test_crew_rows_keep_the_subject_and_the_opponent_in_distinct_slots() -> None:
    """The row's SUBJECT is the crew artifact; the opponent has its own fields.

    Every crew diagnostic ran one crew candidate against ONE frozen impostor
    (§8.1, ``ea4bc955…``), and the two identities are read back from the two
    distinct replay slots into two distinct row slots. The conflation guard is
    echoed here as an explicit inequality: the subject digest and the opponent
    digest DIFFER, and the encoder versions name opposite sides
    (``crew-…`` vs ``impostor-…``), so neither can be re-read as the other's.
    The opponent block is pinned against the frozen champion's OWN slate row,
    field for field — a drift in either would break the join 18.27 relies on.
    """

    rows = _rows()
    frozen = rows[_FROZEN_OPPONENT.entrant]
    for arm in _arms(_CREW):
        row = rows[arm.entrant]
        assert arm.weights_sha256 is not None

        crew_stamp = row["crew_tactical_policy_stamp"]
        assert crew_stamp["weights_sha256"] == arm.weights_sha256
        assert row["committed_weights_sha256"] == arm.weights_sha256
        assert row["artifact_path"] == arm.artifact_path
        assert row["committed_sidecar"] == f"{arm.artifact_path}/weights.json.sha256"
        assert row["crew_stamp_equals_committed_sha256"] is True
        assert row["crew_stamp_verified_games"] == arm.stamp_games
        assert crew_stamp["policy_id"] == arm.policy_id
        assert crew_stamp["method"] == arm.method
        assert crew_stamp["encoder_version"] == arm.encoder_version
        assert crew_stamp["anchor_policy"] == arm.anchor_policy

        opponent_stamp = row["opponent_tactical_policy_stamp"]
        assert opponent_stamp["weights_sha256"] == _FROZEN_OPPONENT.weights_sha256
        assert (
            row["opponent_committed_weights_sha256"] == _FROZEN_OPPONENT.weights_sha256
        )
        assert row["opponent_artifact_path"] == _FROZEN_OPPONENT.artifact_path
        assert row["opponent_stamp_equals_committed_sha256"] is True
        assert row["opponent_stamp_verified_games"] == arm.stamp_games
        # The frozen opponent is the SAME identity its own slate row recorded.
        assert opponent_stamp == frozen["tactical_policy_stamp"]

        # The conflation guard, echoed: two identities, never one.
        assert crew_stamp["weights_sha256"] != opponent_stamp["weights_sha256"]
        assert crew_stamp["policy_id"] != opponent_stamp["policy_id"]
        assert crew_stamp["encoder_version"].startswith("crew-")
        assert opponent_stamp["encoder_version"].startswith("impostor-")


def test_crew_rows_do_not_follow_the_realpath_v3_stamp_convention() -> None:
    """The realpath-v3 field NAMES are absent, deliberately (report §15).

    ``realpath-rerank-v3`` (``training/realpath.py``) seats the IMPOSTOR
    read-back in ``stamp`` even on a crew leg and puts the frozen opponent's
    DECLARATION in ``opponent_stamp``. Reusing that shape in this file would
    seat the opponent in the subject slot and label four crew diagnostics with
    the champion's identity. So the convention here is asserted by ABSENCE as
    well as by presence: no ``stamp``, no ``opponent_stamp``, no ``crew_stamp``
    key on any crew row, and no repurposed ``tactical_policy_stamp`` subject
    field either — a writer that drifted back to the v3 names fails loud here
    instead of handing 18.27 a mislabelled identity.
    """

    rows = _rows()
    v3_names = ("stamp", "opponent_stamp", "crew_stamp", "opponent_weights_sha256")
    for arm in _arms(_CREW):
        row = rows[arm.entrant]
        for name in v3_names:
            assert name not in row
        # The subject slot is the CREW slot; the impostor-side key an impostor
        # row uses is not repurposed to carry the opponent here.
        assert "tactical_policy_stamp" not in row
        assert "stamp_verified_games" not in row
        assert "stamp_equals_committed_sha256" not in row

        assert "crew_tactical_policy_stamp" in row
        assert "opponent_tactical_policy_stamp" in row
        # The stamps came from the two DISTINCT schema slots in the bytes.
        assert "read_policy_stamps" in row["stamp_source"]
        assert ".crew / .tactical" in row["stamp_source"]


# -- the identity chain reaches the DISK --------------------------------------


def test_every_committed_digest_closes_on_the_artifact_bytes_on_disk() -> None:
    """Each declared identity is checked against the committed genome itself.

    Everything above compares a row's fields to a row's other fields, which
    proves only that a row is SELF-consistent — a row naming an artifact that
    was never committed, or one whose sidecar drifted from the genome beside
    it, would satisfy every one of those pins. This closes the chain on disk
    for both links (row digest -> committed sidecar -> ``weights.json``
    bytes), across every slot that names an artifact: each impostor arm's
    subject dir, and each crew arm's subject dir AND its frozen opponent's
    dir. The comparator names none — the one arm that loaded nothing.
    """

    rows = _rows()
    checked: list[tuple[str, str]] = []
    for arm in _SLATE:
        row = rows[arm.entrant]
        if arm.artifact_path is not None:
            _assert_digest_closes_on_the_artifact_bytes(
                arm.artifact_path, row["committed_weights_sha256"]
            )
            checked.append((arm.entrant, "subject"))
        if arm.side == _CREW:
            _assert_digest_closes_on_the_artifact_bytes(
                row["opponent_artifact_path"],
                row["opponent_committed_weights_sha256"],
            )
            checked.append((arm.entrant, "opponent"))

    # Coverage is asserted, not assumed: no arm may quietly carry no dir and
    # so skip the whole check.
    assert len(checked) == len(_arms(_IMPOSTOR)) + 2 * len(_arms(_CREW))
    assert [arm.artifact_path for arm in _arms(_COMPARATOR)] == [None]


# -- the §12 deciding cell ----------------------------------------------------


def test_the_c1_rider_intersection_is_the_persisted_same_seed_deciding_cell() -> None:
    """The §12 cell 18.27 decides on, persisted in the row rather than recomputed.

    The c1 pair is compared on the SAME seeds: seed 20 is c1-gen0's stalemate,
    so it is excluded from BOTH sides — comparing a 50-seed set against a
    49-seed one would let a missing game masquerade as a behavioural margin.
    The excluded seed is derived from c1-gen0's own declared stalemate file, so
    the exclusion cannot drift from the reason for it.

    Every rate is re-derived from the cell's OWN numerator and denominator, and
    the margin from the two rates, so no decimal here can drift from the counts
    behind it. The two sides sit differently against their parent instruments,
    and that asymmetry is pinned too: c1-gen0's ``kill_craft`` ALREADY excludes
    the stalled seed (it scored 49 games), so the gen0 side matches it exactly;
    c1-gen9 scored all 50, so its denominator drops by seed 20's kills while
    its witnessed count is untouched — seed 20 contributed no witnessed kill.
    """

    rows = _rows()
    row = rows["p18-crew-c1-gen9"]

    # The cell is the c1 pair's, and lives on exactly one row — checked before
    # it is read, so a dropped cell fails as a missing PIN rather than as a
    # stray KeyError.
    carriers = [
        entrant
        for entrant, candidate in rows.items()
        if "kill_craft_rider_intersection" in candidate.get("instruments", {})
    ]
    assert carriers == ["p18-crew-c1-gen9"]
    cell = row["instruments"]["kill_craft_rider_intersection"]

    # The excluded seed IS c1-gen0's declared stalemate, not a bare 20.
    stalemates = rows["p18-crew-c1-gen0"]["stalemate_games_no_game_over"]
    assert stalemates == ["replay-seed-20.jsonl"]
    assert cell["excluded_seed"] == 20
    assert f"replay-seed-{cell['excluded_seed']}.jsonl" in stalemates

    assert cell["gen9_crew_witnessed_kills"] == 30
    assert cell["gen9_kills_total"] == 191
    assert cell["gen0_crew_witnessed_kills"] == 33
    assert cell["gen0_kills_total"] == 200

    gen9_rate = cell["gen9_crew_witnessed_kills"] / cell["gen9_kills_total"]
    gen0_rate = cell["gen0_crew_witnessed_kills"] / cell["gen0_kills_total"]
    assert cell["gen9_rate"] == pytest.approx(gen9_rate)
    assert cell["gen9_rate"] == pytest.approx(30 / 191)
    assert cell["gen0_rate"] == pytest.approx(gen0_rate)
    assert cell["gen0_rate"] == pytest.approx(33 / 200)

    assert cell["margin_gen9_minus_gen0"] == pytest.approx(gen9_rate - gen0_rate)
    assert cell["margin_gen9_minus_gen0"] == pytest.approx(30 / 191 - 33 / 200)
    # The trained crew reads BELOW its own gen-0 control on this gauge; 18.27
    # rules on that, this only pins the sign against the numbers.
    assert cell["margin_gen9_minus_gen0"] < 0

    assert cell["corpus_rate"] == pytest.approx(12 / 505)

    # Coherence with the parent instruments each side was cut from.
    gen9_parent = row["instruments"]["kill_craft"]
    gen0_parent = rows["p18-crew-c1-gen0"]["instruments"]["kill_craft"]
    # gen0 already dropped the stalled seed, so the cut is a no-op there.
    assert gen0_parent["games_total"] == 49
    assert cell["gen0_crew_witnessed_kills"] == gen0_parent["crew_witnessed_kills"]
    assert cell["gen0_kills_total"] == gen0_parent["kills_total"]
    # gen9 scored all 50, so excluding seed 20 can only REMOVE kills.
    assert gen9_parent["games_total"] == 50
    assert cell["gen9_kills_total"] < gen9_parent["kills_total"]
    assert cell["gen9_crew_witnessed_kills"] == gen9_parent["crew_witnessed_kills"]


def test_the_seed_mod5_splits_partition_each_arms_own_games() -> None:
    """The §6.b split views partition each arm's OWN seeds, fences included.

    Every expected split size is DERIVED, never listed: count the arm's own
    ``recording.seeds`` by ``seed % 5``, then remove the seeds its instrument
    view fences (its declared stalemates, parsed from their own filenames).
    That reproduces all nine arms from two facts already on the row, so the
    three arms whose splits look "wrong" are explained rather than special-
    cased — 7f73929d's train is 29 because seed 35 is not in its seed list at
    all, while c1-gen0's is 29 and c2-gen9's is 29/10/9 because their stalled
    seeds (20, and 19+20) fall in those residues. Listing the sizes would
    hide exactly that distinction.

    The three splits must also exhaust the arm's instrument view: their games
    sum to ``kill_craft.games_total`` — the stalemate-excluded count, not
    ``core.games_total``.

    Cross-split coherence closes the loop on three cells whose parents are
    pinned elsewhere in this module: summed over the three splits, the
    ``{n, d}`` pairs must equal the arm's flattened parent EXACTLY — the
    kill-craft cells, the co-present cell, and the teammate-accusation cell.
    Verified to hold on all nine arms including the fenced ones, because
    those parents are themselves the fenced instrument view; no case split is
    needed.
    """

    rows = _rows()
    carriers = {
        entrant
        for entrant, row in rows.items()
        if "seed_mod5_splits" in row.get("instruments", {})
    }
    assert carriers == {arm.entrant for arm in _SLATE}

    notes: set[str] = set()
    for arm in _SLATE:
        row = rows[arm.entrant]
        block = row["instruments"]["seed_mod5_splits"]
        assert set(block) == {"note"} | set(_MOD5_RESIDUES)
        notes.add(block["note"])

        seeds = row["recording"]["seeds"]
        fenced = _fenced_seeds(row)
        assert fenced == {
            seed for seed in fenced if seed in seeds
        }  # a fence names a seed the arm actually recorded

        for split, residues in _MOD5_RESIDUES.items():
            expected = sum(
                1 for seed in seeds if seed % 5 in residues and seed not in fenced
            )
            assert block[split]["games"] == expected

            cells = block[split]
            assert set(cells) == {"games", "one_hop_point_biserial"} | set(
                _MOD5_RATIO_CELLS
            )
            for name in _MOD5_RATIO_CELLS:
                assert set(cells[name]) == {"n", "d"}
                assert cells[name]["n"] <= cells[name]["d"]
            assert set(cells["one_hop_point_biserial"]) == {"r", "kills_total"}

        # The splits exhaust the INSTRUMENT view (fenced), not the raw games.
        kill_craft = row["instruments"]["kill_craft"]
        assert (
            sum(block[split]["games"] for split in _MOD5_RESIDUES)
            == kill_craft["games_total"]
        )
        assert kill_craft["games_total"] == arm.games_total - len(fenced)

        # Cross-split coherence against the parents pinned elsewhere here.
        summed = _summed_across_splits
        assert (
            summed(block, "crew_witnessed_kills", "n")
            == kill_craft["crew_witnessed_kills"]
        )
        assert summed(block, "crew_witnessed_kills", "d") == kill_craft["kills_total"]

        co_present = row["instruments"]["kill_craft_co_present_departure"]
        assert (
            summed(block, "co_present_departure", "n")
            == co_present["co_present_ge1_kills"]
        )
        assert summed(block, "co_present_departure", "d") == co_present["kills_total"]

        teammate = row["instruments"]["registered_nested_cells"]["teammate_accusations"]
        assert summed(block, "teammate_accusations", "n") == teammate["numerator"] == 0
        assert summed(block, "teammate_accusations", "d") == teammate["denominator"]

    assert len(notes) == 1


def test_the_leg_duration_blocks_price_the_campaign_honestly() -> None:
    """Each leg's wall clock, with the two arms that look wrong explained.

    ``games_recorded_ok`` counts what the RECORDER logged, which includes
    re-records and retried games, so it is deliberately NOT reconciled to 50
    here — only the floor is pinned (a leg logs at least the games that were
    scored), because tightening it would encode a semantics this block does
    not carry.

    Two arms would read as broken instrumentation and are pinned as REAL:

    * ``c2-gen0``'s whole leg is **27 seconds**. That is not a missing
      measurement — the arm is the totally-starved control where no meeting
      ever convened, so almost no LLM call was ever made. Pinned exactly, and
      pinned as the slate's minimum, so a genuinely missing timing (0) or a
      silent backfill would both fail.
    * ``7f73929d`` alone carries ``post_pr_retry_leg`` — the 4-attempt retry
      that closed its seed-35 budget. Its last event IS the campaign's last
      event across all nine arms, which is asserted as a uniquely-held
      maximum and tied back to the retry leg that produced it.
    """

    rows = _rows()
    # Checked before any value is read — and exact, so the frozen 17.14 rows
    # (which carry no leg clock) may not sprout one either.
    carriers = {entrant for entrant, row in rows.items() if "leg_duration" in row}
    assert carriers == {arm.entrant for arm in _SLATE}

    base_keys = {
        "note",
        "games_recorded_ok",
        "retry_events",
        "sum_wall_seconds_ok",
        "first_event_at",
        "last_event_at",
    }

    notes: set[str] = set()
    for arm in _SLATE:
        row = rows[arm.entrant]
        leg = row["leg_duration"]
        expected_keys = base_keys | (
            {"post_pr_retry_leg"} if arm.entrant == "p18-imp-7f73929d" else set()
        )
        assert set(leg) == expected_keys
        notes.add(leg["note"])

        assert leg["sum_wall_seconds_ok"] > 0
        assert leg["retry_events"] >= 0
        # The recorder logged at least the games that were scored.
        assert leg["games_recorded_ok"] >= arm.games_total
        assert leg["first_event_at"] <= leg["last_event_at"]

    assert len(notes) == 1

    # c2-gen0: 27 seconds, and the slate's floor.
    walls = {
        arm.entrant: rows[arm.entrant]["leg_duration"]["sum_wall_seconds_ok"]
        for arm in _SLATE
    }
    assert walls["p18-crew-c2-gen0"] == _C2_GEN0_WALL_SECONDS
    assert min(walls.values()) == _C2_GEN0_WALL_SECONDS
    assert min(walls, key=lambda entrant: walls[entrant]) == "p18-crew-c2-gen0"

    # 7f73929d: the retry leg, and the campaign's last event.
    retry = rows["p18-imp-7f73929d"]["leg_duration"]["post_pr_retry_leg"]
    assert retry["attempts"] == 4
    assert retry["sum_wall_seconds"] > 0
    assert retry["first_at"] <= retry["last_event_at"]

    lasts = {
        arm.entrant: rows[arm.entrant]["leg_duration"]["last_event_at"]
        for arm in _SLATE
    }
    assert max(lasts.values()) == _CAMPAIGN_LAST_EVENT_AT
    assert [
        entrant for entrant, stamp in lasts.items() if stamp == _CAMPAIGN_LAST_EVENT_AT
    ] == ["p18-imp-7f73929d"]
    # ... and that maximum is the retry leg's own last event.
    assert retry["last_event_at"] == _CAMPAIGN_LAST_EVENT_AT
    assert (
        rows["p18-imp-7f73929d"]["leg_duration"]["last_event_at"]
        == _CAMPAIGN_LAST_EVENT_AT
    )


def test_the_registered_nested_cells_block_is_persisted_on_every_arm() -> None:
    """The six registered rulings' nested sources, re-persisted per arm.

    The flattened rows dropped the nested structures these rulings are cut
    from, so — as with the co-present cell — the committed block is now the
    only copy and nothing downstream can rebuild it. Presence is checked as a
    set over all nine arms before any value is read, the field-set SHAPE is
    pinned at every level (the ratio pairs, the two survival cells, and both
    action-entropy roles), and the note must be a single shared definition.

    Two spot values anchor the slate-critical arms, and ``c2-gen0``'s
    starvation shape is pinned in full — with the distinction that matters:
    its meeting-economy cells are all zero because no meeting ever convened,
    but its ACTION-entropy cells are NOT, because agents still acted. A
    blanket-zero block would be a different (and wrong) claim about that arm.

    The standing no-betrayal invariant rides along: no arm accuses a teammate.
    It is asserted only where it has content — an arm with a zero denominator
    satisfies it vacuously — and WHICH arm is vacuous is pinned too, so a
    denominator silently collapsing elsewhere cannot quietly empty the check.
    """

    rows = _rows()
    carriers = {
        entrant
        for entrant, row in rows.items()
        if "registered_nested_cells" in row.get("instruments", {})
    }
    assert carriers == {arm.entrant for arm in _SLATE}

    notes: set[str] = set()
    vacuous: set[str] = set()
    for arm in _SLATE:
        block = rows[arm.entrant]["instruments"]["registered_nested_cells"]
        assert set(block) == _NESTED_KEYS
        notes.add(block["note"])

        for name in ("frame_conversions", "teammate_accusations"):
            assert set(block[name]) == _RATIO_KEYS
            assert block[name]["numerator"] <= block[name]["denominator"]
        assert set(block["alibi_survival"]) == {"survived", "total_impostor_alibis"}
        assert (
            block["alibi_survival"]["survived"]
            <= block["alibi_survival"]["total_impostor_alibis"]
        )
        assert set(block["effective_deflection"]) == {
            "effective_deflections",
            "active_survivals",
        }
        assert (
            block["effective_deflection"]["effective_deflections"]
            <= block["effective_deflection"]["active_survivals"]
        )
        assert set(block["action_entropy"]) == {"IMPOSTOR", "CREWMATE"}
        for role in ("IMPOSTOR", "CREWMATE"):
            assert set(block["action_entropy"][role]) == _ENTROPY_KEYS
            assert block["action_entropy"][role]["decisions"] > 0

        # The standing no-betrayal invariant, where it has content.
        teammate = block["teammate_accusations"]
        if teammate["denominator"] > 0:
            assert teammate["numerator"] == 0
        else:
            vacuous.add(arm.entrant)

        if arm.entrant in _NESTED_FRAME_CONVERSIONS:
            numerator, denominator = _NESTED_FRAME_CONVERSIONS[arm.entrant]
            assert block["frame_conversions"]["numerator"] == numerator
            assert block["frame_conversions"]["denominator"] == denominator

    assert len(notes) == 1
    # Exactly one arm satisfies the invariant vacuously — the dead-meeting
    # control. Anywhere else, a zero denominator would be a new finding.
    assert vacuous == {"p18-crew-c2-gen0"}

    # c2-gen0: the meeting economy is empty, the ACTION stream is not.
    starved = rows["p18-crew-c2-gen0"]["instruments"]["registered_nested_cells"]
    assert starved["frame_conversions"] == {"numerator": 0, "denominator": 0}
    assert starved["teammate_accusations"] == {"numerator": 0, "denominator": 0}
    assert starved["alibi_survival"] == {"survived": 0, "total_impostor_alibis": 0}
    assert starved["effective_deflection"] == {
        "effective_deflections": 0,
        "active_survivals": 0,
    }
    for role in ("IMPOSTOR", "CREWMATE"):
        assert starved["action_entropy"][role]["decisions"] > 0
        assert starved["action_entropy"][role]["mean_conditional_entropy"] > 0.0


def test_the_comparator_carries_the_49_seed_cut_for_the_f13_axis() -> None:
    """The scripted anchor re-cut onto the F13 intersection, and only there.

    ``7f73929d``'s axis-2 reads pair against the comparator, so the comparator
    needs a same-seed view of its own instrument cells — the same 49-seed cut
    the F13 gauge block uses, which is asserted by deriving the excluded seed
    from that block rather than restating 35.

    The scripted anchor is the load-bearing pin: ``co_present_ge1_kills`` is 0
    on the intersection exactly as it is on the full 50, so the
    learned-vs-scripted split does not depend on which seed set is read. The
    no-betrayal invariant holds on the cut too. Counts are then reconciled
    against the comparator's own full-50 instruments — a cut may only remove,
    never add — and the two the cut did NOT move (witnessed kills, alibi
    survival) are pinned as equal rather than glossed as "roughly the same".
    """

    rows = _rows()
    carriers = [
        entrant
        for entrant, row in rows.items()
        if "intersection_49_seed_for_7f73929d" in row.get("instruments", {})
    ]
    assert carriers == ["p18-fsm-comparator"]

    comparator = rows["p18-fsm-comparator"]
    block = comparator["instruments"]["intersection_49_seed_for_7f73929d"]

    # The same cut the F13 gauge block uses, derived not restated.
    assert block["excluded_seed"] == _F13_EXCLUDED_SEED
    assert (
        block["excluded_seed"]
        == rows["p18-imp-ea4bc955"]["f13_intersection_gauges"]["excluded_seed"]
    )

    for name, count in _COMPARATOR_INTERSECTION_COUNTS.items():
        assert block[name] == count
    assert block["frame_attempts"] == {"numerator": 146, "denominator": 154}
    assert block["frame_conversions"] == {"numerator": 5, "denominator": 146}

    # THE ANCHOR: the scripted mover never departs a kill co-present — on the
    # full 50 and on the cut alike, so the split survives the seed set.
    full_co_present = comparator["instruments"]["kill_craft_co_present_departure"]
    assert block["co_present_ge1_kills"] == 0
    assert full_co_present["co_present_ge1_kills"] == 0

    # The no-betrayal invariant holds on the cut too.
    assert block["teammate_accusations"]["numerator"] == 0

    # A cut may only REMOVE. Strictly-less where the excluded seed had
    # content, equal where it had none.
    kill_craft = comparator["instruments"]["kill_craft"]
    off_menu = comparator["instruments"]["off_menu"]
    nested = comparator["instruments"]["registered_nested_cells"]
    assert block["kills_total"] < kill_craft["kills_total"]
    assert block["impostor_decisions"] < off_menu["impostor_decisions"]
    assert block["off_menu_total"] == off_menu["off_menu_total"] == 0
    assert (
        block["teammate_accusations"]["denominator"]
        < nested["teammate_accusations"]["denominator"]
    )
    assert (
        block["frame_conversions"]["numerator"]
        <= nested["frame_conversions"]["numerator"]
    )
    assert (
        block["effective_deflection"]["active_survivals"]
        < nested["effective_deflection"]["active_survivals"]
    )
    # Untouched by the cut: the excluded seed carried neither a witnessed kill
    # nor an impostor alibi.
    assert block["crew_witnessed_kills"] == kill_craft["crew_witnessed_kills"]
    assert block["alibi_survival"] == nested["alibi_survival"]


def test_the_f13_intersection_gauges_put_the_quartet_on_one_seed_set() -> None:
    """The F13 four are compared on IDENTICAL games, not near-identical ones.

    ``7f73929d`` recorded 49 seeds; the other three recorded 50. Comparing
    those directly would let one extra game move a gauge and read as a
    behavioural margin, so the three FULL arms carry a re-measurement on
    7f73929d's own seed set. The block therefore sits on exactly those three
    rows — and its ABSENCE from ``7f73929d`` is not an oversight but the
    point: that arm's ordinary ``watchability`` block already IS the n=49
    view, which is asserted here rather than left as a claim in a note.

    Both halves are pinned: the measured values, and every floor re-derived —
    the two fixed baseline-6 pins, plus the population-relative conversion
    floor recomputed from the INTERSECTION's own flag supply (not the
    full-50 one, which would silently judge the cut against the wrong bar).
    Finally, every intersection value must DIFFER from the row's own full-50
    gauge: a block copied wholesale from the uncut measurement would satisfy
    every other assertion here.
    """

    rows = _rows()
    carriers = {
        entrant for entrant, row in rows.items() if "f13_intersection_gauges" in row
    }
    assert carriers == set(_F13_INTERSECTION_MEASURED)

    # The six non-carriers, and WHY 7f73929d is one of them.
    non_carriers = {arm.entrant for arm in _SLATE} - carriers
    assert len(non_carriers) == len(_SLATE) - len(carriers)
    f13_arm = next(arm for arm in _SLATE if arm.entrant == "p18-imp-7f73929d")
    assert "p18-imp-7f73929d" in non_carriers
    assert f13_arm.missing_seeds == (_F13_EXCLUDED_SEED,)
    seventh = rows["p18-imp-7f73929d"]
    intersection_seeds = sorted(set(_CANONICAL_SEEDS) - {_F13_EXCLUDED_SEED})
    assert seventh["recording"]["seeds"] == intersection_seeds
    assert seventh["watchability"]["games_total"] == len(intersection_seeds) == 49

    notes: set[str] = set()
    for entrant, expected in _F13_INTERSECTION_MEASURED.items():
        block = rows[entrant]["f13_intersection_gauges"]
        assert block["excluded_seed"] == _F13_EXCLUDED_SEED
        notes.add(block["note"])

        gauges = block["gauges"]
        assert set(gauges) == set(expected)
        full = _gauges(rows[entrant])
        for name, measured in expected.items():
            assert set(gauges[name]) == {"floor", "measured"}
            assert gauges[name]["measured"] == pytest.approx(measured)
            # The cut MOVED the gauge — this is not the uncut block again.
            assert gauges[name]["measured"] != full[name]["measured"]

        assert gauges["witnessed_event_rate"]["floor"] == pytest.approx(
            _WITNESSED_FLOOR
        )
        assert gauges["flags_per_meeting"]["floor"] == pytest.approx(_FLAGS_FLOOR)
        # Population-relative, off the INTERSECTION's own flag supply.
        assert gauges["testimony_backed_conversion"]["floor"] == pytest.approx(
            min(
                1.0,
                _CONVERSION_PIN
                * (_FLAGS_FLOOR / gauges["flags_per_meeting"]["measured"]),
            )
        )

    assert len(notes) == 1
    assert str(_F13_EXCLUDED_SEED) in notes.pop()


def test_the_c1_paired_crew_win_table_is_the_49_seed_discordant_cut() -> None:
    """The c1 pair's per-seed win table, reconciled against both arms' totals.

    A paired (McNemar-style) table only means anything if its four cells
    describe the same games both arms finalized: seed 20 is c1-gen0's
    stalemate, so it is excluded, and the cells must sum to the remaining 49.

    The margins are then reconciled ACROSS rows, which is what stops the table
    being internally tidy but detached from the arms it summarises:
    ``both_win + gen9_only_win`` must equal c1-gen9's crew wins over those same
    49 seeds, and ``both_win + gen0_only_win`` c1-gen0's. Each side's 49-seed
    total is re-derived from its OWN per-game bytes rather than assumed equal
    to its full-50 count — they happen to coincide here, but only because
    neither arm won seed 20 as crew (gen9 lost it to an impostor parity, gen0
    never finished it). Asserting the raw equality would pass for the wrong
    reason the moment that changed.
    """

    rows = _rows()
    carriers = [
        entrant
        for entrant, row in rows.items()
        if "conversion_paired_49_seed" in row.get("instruments", {})
    ]
    assert carriers == ["p18-crew-c1-gen9"]

    gen9 = rows["p18-crew-c1-gen9"]
    gen0 = rows["p18-crew-c1-gen0"]
    table = gen9["instruments"]["conversion_paired_49_seed"]

    assert table["excluded_seed"] == _C1_PAIRED_EXCLUDED_SEED
    assert gen0["stalemate_games_no_game_over"] == [
        f"replay-seed-{_C1_PAIRED_EXCLUDED_SEED}.jsonl"
    ]
    for cell, count in _C1_PAIRED_49.items():
        assert table[cell] == count

    assert sum(_C1_PAIRED_49.values()) == 49
    assert sum(table[cell] for cell in _C1_PAIRED_49) == 49

    # The cross-row reconciliation, against each arm's own 49-seed total.
    gen9_wins_49 = _crew_wins_excluding(gen9, _C1_PAIRED_EXCLUDED_SEED)
    gen0_wins_49 = _crew_wins_excluding(gen0, _C1_PAIRED_EXCLUDED_SEED)
    assert table["both_win"] + table["gen9_only_win"] == gen9_wins_49 == 26
    assert table["both_win"] + table["gen0_only_win"] == gen0_wins_49 == 25

    # ... and the reason both survive the cut unchanged: neither arm won the
    # excluded seed as crew, so removing it moved neither total.
    gen9_seed = {game["seed"]: game for game in gen9["watchability"]["per_game"]}[
        _C1_PAIRED_EXCLUDED_SEED
    ]
    assert gen9_seed["reason"] == "IMPOSTOR_PARITY"
    assert gen9_wins_49 == gen9["core"]["crew_wins"]
    assert gen0_wins_49 == gen0["core"]["crew_wins"]


def test_the_co_present_departure_cell_is_persisted_on_every_arm() -> None:
    """The registered co-present-departure cell, on all nine arms.

    The flattened rows had DROPPED the ``co_present_histogram`` this cell is
    cut from, so it was re-derived and persisted per arm — which means the
    committed number is now the only copy, and nothing downstream can
    recompute it from a histogram that is no longer there. Presence is
    therefore checked on every arm before any value is read: a silently
    missing cell must fail as a missing PIN, not as a KeyError deep in a
    consumer.

    The rate is re-derived from the cell's own numerator and denominator, and
    the denominator is checked against the row's OWN flattened
    ``kill_craft.kills_total`` rather than carried in the table — the two
    describe the same kills, so they may never disagree.

    The anchor of the learned-vs-scripted split is pinned exactly: the
    scripted comparator's numerator is **0** — the FSM mover never departs a
    kill with a crewmate co-present — while every learned arm's is non-zero.
    That contrast is what the cell exists to measure, so it is asserted as a
    slate-wide property rather than as one arm's cell in isolation.
    """

    rows = _rows()
    carriers = {
        entrant
        for entrant, row in rows.items()
        if "kill_craft_co_present_departure" in row.get("instruments", {})
    }
    assert carriers == {arm.entrant for arm in _SLATE}

    notes: set[str] = set()
    for arm in _SLATE:
        row = rows[arm.entrant]
        cell = row["instruments"]["kill_craft_co_present_departure"]
        assert set(cell) == {"note", "co_present_ge1_kills", "kills_total", "rate"}

        assert cell["co_present_ge1_kills"] == arm.co_present_ge1_kills
        # The denominator is the row's own kill population, not a second count.
        assert cell["kills_total"] == row["instruments"]["kill_craft"]["kills_total"]
        assert cell["co_present_ge1_kills"] <= cell["kills_total"]
        assert cell["rate"] == pytest.approx(
            cell["co_present_ge1_kills"] / cell["kills_total"]
        )
        notes.add(cell["note"])

    # ONE registered definition across the slate, not nine ad-hoc cuts.
    assert len(notes) == 1
    assert "co_present_crew >= 1" in notes.pop()

    # The split this cell anchors: scripted 0, every learned arm above it.
    comparator = _arms(_COMPARATOR)[0]
    assert comparator.co_present_ge1_kills == 0
    comparator_cell = rows[comparator.entrant]["instruments"][
        "kill_craft_co_present_departure"
    ]
    assert comparator_cell["co_present_ge1_kills"] == 0
    assert comparator_cell["rate"] == 0.0
    learned = [arm for arm in _SLATE if arm.side != _COMPARATOR]
    assert len(learned) == len(_SLATE) - 1
    assert all(arm.co_present_ge1_kills > 0 for arm in learned)


# -- honesty: the failing diagnostics say what failed -------------------------


def test_each_rows_validity_gate_reports_its_own_failures_by_name() -> None:
    """Pass and FAIL are pinned with equal precision, per arm.

    Two crew diagnostics fail their validity gate. The pin is the exact SET of
    failing check names, re-derived from the per-check ``passed`` flags rather
    than trusting the summary boolean — a row that flipped to ``passed`` while
    its checks still reported violations (or vice versa) is precisely the
    drift worth catching, and 18.27 must never read a failed diagnostic as a
    clean measurement.
    """

    rows = _rows()
    for arm in _SLATE:
        gate = rows[arm.entrant]["validity_gate"]
        failing = {check["name"] for check in gate["checks"] if not check["passed"]}
        assert failing == arm.validity_failures
        assert gate["passed"] is arm.validity_passed
        assert gate["passed"] == (not failing)
        assert gate["games_total"] == arm.games_total


def test_the_c2_diagnostics_report_the_stall_and_the_dead_meeting_economy() -> None:
    """The two failed crew rows name their own defects, in their own counters.

    ``c2-gen9`` stalled on two seeds — no ``game_over`` row, so those games
    proved no identity either (48 of 50 stamp-verified) and the referee scored
    nothing (integrity not ok). ``c2-gen0`` is the starved control: not one
    meeting ever convened, so ejection accuracy, conversion and both flag
    gauges are UNDEFINED (``None``) rather than 0.0, and the derived
    conversion floor clamps to 1.0 against a supply that does not exist.
    ``c1-gen9`` is the ONE crew diagnostic that passed its gate — pinned
    alongside, so "everything fails" can never pass as a description of this
    slate either (the other three crew rows do fail, each for its own reason).
    """

    rows = _rows()

    gen9 = rows["p18-crew-c2-gen9"]
    assert gen9["validity_gate"]["passed"] is False
    assert gen9["stalemate_games_no_game_over"] == [
        "replay-seed-19.jsonl",
        "replay-seed-20.jsonl",
    ]
    assert gen9["core"]["meeting_rate"] == pytest.approx(0.60)
    assert gen9["core"]["tick_budget_reached"] == 2
    assert gen9["crew_stamp_verified_games"] == 48
    assert gen9["opponent_stamp_verified_games"] == 48
    assert gen9["watchability"]["integrity_ok"] is False
    assert gen9["watchability"]["mean_score"] == pytest.approx(0.0)

    gen0 = rows["p18-crew-c2-gen0"]
    assert gen0["validity_gate"]["passed"] is False
    assert gen0["stalemate_games_no_game_over"] == []
    assert gen0["core"]["meeting_rate"] == 0.0
    assert gen0["core"]["resolved_meetings"] == 0
    assert gen0["core"]["total_ejections"] == 0
    # UNDEFINED, never coerced to 0.0.
    assert gen0["core"]["ejection_accuracy"] is None
    assert gen0["core"]["genuine_class_conversion"] is None
    gauges = _gauges(gen0)
    assert gauges["flags_per_meeting"]["measured"] is None
    assert gauges["testimony_backed_conversion"]["measured"] is None
    assert gauges["testimony_backed_conversion"]["floor"] == pytest.approx(1.0)

    assert rows["p18-crew-c1-gen9"]["validity_gate"]["passed"] is True


# -- headline values ----------------------------------------------------------


def test_the_headline_cells_match_the_committed_rows() -> None:
    """The numbers 18.27 rules on, pinned to the bytes that produced them.

    Every win rate is re-derived as ``impostor_wins / games_total`` as well as
    pinned, so a rate can never drift away from the count behind it — the
    n=49 arm in particular reads 21/49, not a 50-game rounding. Every game is
    then accounted for on both sides — a decided game went to exactly one
    side, a stalemate to neither — which pins each arm's crew count by
    arithmetic rather than by a literal free to drift from it. Referee mean
    and median ride along because the referee verdict is read WITH the win
    edge, never alone.
    """

    rows = _rows()
    for arm in _SLATE:
        core = rows[arm.entrant]["core"]
        watchability = rows[arm.entrant]["watchability"]

        assert core["games_total"] == arm.games_total
        assert core["impostor_wins"] == arm.impostor_wins
        assert core["impostor_win_rate"] == pytest.approx(arm.impostor_win_rate)
        assert core["impostor_win_rate"] == pytest.approx(
            arm.impostor_wins / arm.games_total
        )
        assert core["meeting_rate"] == pytest.approx(arm.meeting_rate)

        stalemates = len(arm.stalemate_replays or ())
        assert core["crew_wins"] + core["impostor_wins"] + stalemates == arm.games_total

        assert watchability["mean_score"] == pytest.approx(arm.mean_score, abs=0.01)
        assert watchability["median_score"] == pytest.approx(arm.median_score, abs=0.01)
        assert watchability["referee_passed"] is arm.referee_passed
        assert watchability["games_total"] == arm.games_total


def test_the_witnessed_event_rate_split_half_is_unresolvable_on_every_arm() -> None:
    """No arm can resolve ``witnessed_event_rate`` against its own noise.

    The split-half read compares H1-vs-H2 noise against 25% of the gauge's
    threshold; for the witnessed-kill rate the measured noise exceeds that
    ceiling on EVERY arm of the slate, including the scripted comparator and
    the starved control. That is a property of the gauge at n=50, not of any
    candidate — pinned slate-wide so no 18.27 cell may read a witnessed-rate
    difference as signal.
    """

    rows = _rows()
    for arm in _SLATE:
        witnessed = rows[arm.entrant]["split_half"]["witnessed_event_rate"]
        assert witnessed["precondition"] == "UNRESOLVABLE"
        assert witnessed["ceiling_25pct"] == pytest.approx(0.25 * _WITNESSED_FLOOR)


def test_the_stalemate_key_is_present_only_where_it_is_meaningful() -> None:
    """Absent vs empty is a real distinction, and the rows keep it.

    ``stalemate_games_no_game_over`` appears on the rows whose recorder
    tracked it; an EMPTY list means "checked, none", while the key's absence
    on the impostor and comparator rows means the arm never carried the
    field. Collapsing the two would let a missing check read as a clean one.
    """

    rows = _rows()
    for arm in _SLATE:
        row = rows[arm.entrant]
        if arm.stalemate_replays is None:
            assert "stalemate_games_no_game_over" not in row
        else:
            assert row["stalemate_games_no_game_over"] == list(arm.stalemate_replays)
