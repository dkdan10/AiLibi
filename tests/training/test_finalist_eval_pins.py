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


def _origin_main_prior_rows() -> list[dict[str, Any]] | None:
    """The pre-append evidence rows from ``origin/main``, or ``None``.

    ``None`` when the ref does not resolve — CI checks out at
    ``fetch-depth: 1`` and carries no ``origin/main``, where the committed
    digest pin above is the proof instead.
    """

    result = subprocess.run(
        ["git", "show", f"origin/main:{_RESULTS_PATH.as_posix()}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return [json.loads(line) for line in result.stdout.splitlines()]


# -- file integrity: the prior record is preserved ---------------------------


def test_the_two_17_14_rows_stay_first_and_unchanged() -> None:
    """Part I's record is PRESERVED under the phase-18 append (report §15).

    The 17.16 ruling re-derives itself from these two rows every run, so an
    append that rewrote, re-ordered or re-scored them would silently move a
    committed ruling. Pinned two ways: the file's two-row prefix still hashes
    to the pre-append ``origin/main`` blob digest (always on, no git needed),
    and — when the ref resolves — the DECODED rows compare equal as dicts,
    which stays true across a re-serialisation where a byte compare would not.
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
