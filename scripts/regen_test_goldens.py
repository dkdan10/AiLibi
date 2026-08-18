#!/usr/bin/env python3
"""Regenerate the committed test goldens from the committed evidence bytes.

Task 19.27 (audits/audit-phase-19-triage.md §7 item 28): the exact-scalar
transcription pins in ``tests/scripts/test_champion_flip_ruling.py`` and
``tests/training/test_finalist_eval_pins.py`` were hand-transcribed literals.
This script re-derives them mechanically from the committed evidence bytes
and writes them as JSON goldens the tests load:

* ``tests/scripts/_goldens/champion_flip_ruling.json`` — the 17.16/18.27
  ruling's measured cells and derived statistics, from
  ``training/reports/results-finalist-eval.jsonl`` and the canonical 9p2i
  ``MANIFEST.md``.
* ``tests/training/_goldens/finalist_eval_pins.json`` — the 18.26 slate
  table and its companion cells, from the same evidence file.

The division of labour the conversion preserves (the task's "convert the pin
DICTS, keep the logic"): a golden holds MEASURED TRANSCRIPTIONS — values
copied off (or arithmetically derived from) the committed evidence — while
independent ANCHORS stay code literals in the test modules: the §8.1
pre-registration order, the pre-append prior-record blob digest, the
baseline floor fractions, the committed artifact digests the tests
cross-check against on-disk bytes, the substrate/roster pre-registration,
and every schema/convention string. Regenerating an anchor from the same
file the tests check it against would turn a file-vs-plan pin into a
file-vs-file tautology.

Committing a regenerated golden IS a re-baselining act: after an evidence
re-record, the golden's diff is the reviewable record of every number the
re-record moved, exactly as the literal diff used to be.

Values are COPIED from the evidence rows wherever a row carries them
(``json.dumps`` re-emits a parsed float's shortest round-trip repr, so a
copied cell re-serializes byte-identically); only genuinely derived
statistics (win edges, pooled z, Fisher z, the F13 margins) are computed
here, with the same formulas the tests re-run.

Usage::

    uv run python scripts/regen_test_goldens.py           # rewrite both
    uv run python scripts/regen_test_goldens.py --check   # diff, exit 1 on drift
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from _manifest_writer import parse_manifest  # noqa: E402

_RESULTS_PATH = _REPO_ROOT / "training" / "reports" / "results-finalist-eval.jsonl"
_SAMPLES_9P2I = _REPO_ROOT / "replays" / "samples" / "9p2i"

_GENERATED_BY = (
    "scripts/regen_test_goldens.py — do not hand-edit. Measured transcriptions "
    "of the committed evidence bytes; regenerate (and REVIEW the diff — "
    "committing it is a re-baselining act) after any evidence re-record."
)

# The two 17.14 rows stay first in the evidence file (report §15); the
# phase-18 slate is everything after them, in committed row order.
_PRIOR_ROW_COUNT = 2

# The §6.a reason strings that mean the IMPOSTORS won a game.
_IMPOSTOR_WIN_REASONS = ("IMPOSTOR_PARITY", "IMPOSTOR_SABOTAGE")

# The game_over reasons that mean the CREW won (mirrors the finalist test's
# convention constant; used here only for the paired-table reconciliation).
_CREW_WIN_REASONS = frozenset({"CREWMATE_EJECT", "CREWMATE_TASKS"})

# The 18.27 F13 quartet (champion lineage vs runner-up lineage) and the seed
# the intersection excludes — pre-registered identities, mirrored from the
# ruling test's own constants.
_F13_CHAMPIONS = ("p18-imp-6d327dcb", "p18-imp-ea4bc955")
_F13_RUNNER_UPS = ("p18-imp-bfd145cb", "p18-imp-7f73929d")
_F13_GAUGES = (
    "witnessed_event_rate",
    "flags_per_meeting",
    "testimony_backed_conversion",
)
_P18_SHORT_ARM = "p18-imp-7f73929d"
_P18_COMPARATOR = "p18-fsm-comparator"
_P18_CHAMPION_ARM = "p18-imp-ea4bc955"


def load_finalist_rows() -> dict[str, dict[str, Any]]:
    """The committed evidence rows, keyed by entrant (the house loader shape)."""

    rows: dict[str, dict[str, Any]] = {}
    for line in _RESULTS_PATH.read_text(encoding="utf-8").splitlines():
        row: dict[str, Any] = json.loads(line)
        rows[row["entrant"]] = row
    return rows


def _phase18_rows_in_file_order() -> list[dict[str, Any]]:
    lines = _RESULTS_PATH.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[_PRIOR_ROW_COUNT:]]


def _gauges(row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {gauge["name"]: gauge for gauge in row["watchability"]["supply_gauges"]}


def _gauge_cells(row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """The three supply-gauge cells, transcribed as {passed, floor, measured}."""

    return {
        name: {
            "passed": gauge["passed"],
            "floor": gauge["floor"],
            "measured": gauge["measured"],
        }
        for name, gauge in _gauges(row).items()
    }


def pooled_z(k_c: int, n_c: int, k_f: int, n_f: int) -> float | None:
    """The §6.a pooled two-proportion z; ``None`` where no delta exists."""

    if n_c == 0 or n_f == 0:
        return None
    pooled = (k_c + k_f) / (n_c + n_f)
    if pooled in (0.0, 1.0):
        return None
    return (k_c / n_c - k_f / n_f) / math.sqrt(
        pooled * (1 - pooled) * (1 / n_c + 1 / n_f)
    )


def fisher_z(r_c: float, n_c: int, r_f: float, n_f: int) -> float:
    """The §6.a Fisher r-to-z for the correlation cell."""

    return (math.atanh(r_c) - math.atanh(r_f)) / math.sqrt(
        1 / (n_c - 3) + 1 / (n_f - 3)
    )


def impostor_win_seeds(row: dict[str, Any]) -> set[int]:
    """Impostor-win seeds from a row's per-game watchability reasons."""

    return {
        game["seed"]
        for game in row["watchability"]["per_game"]
        if game["reason"] in _IMPOSTOR_WIN_REASONS
    }


def rate_cells(row: dict[str, Any]) -> dict[str, tuple[int, int]]:
    """The eleven registered §6.a rate cells as (numerator, denominator)."""

    instruments = row["instruments"]
    deception = instruments["deception"]
    nested = instruments["registered_nested_cells"]
    kill_craft = instruments["kill_craft"]
    departure = instruments["kill_craft_co_present_departure"]
    off_menu = instruments["off_menu"]
    return {
        "false_vouch_saw_player": (
            deception["false_vouch_saw_player_observations"],
            deception["vouch_observations_impostor"],
        ),
        "false_vouch_corroboration": (
            deception["false_vouch_corroborations"],
            deception["corroboration_claims_impostor"],
        ),
        "false_vouch_fabricated": (
            deception["false_vouch_fabricated"],
            deception["false_vouch_subject_events"],
        ),
        "frame_attempts": (
            deception["frame_attempt_meetings"],
            deception["meetings_total"],
        ),
        "frame_conversions": (
            nested["frame_conversions"]["numerator"],
            nested["frame_conversions"]["denominator"],
        ),
        "teammate_accusations": (
            nested["teammate_accusations"]["numerator"],
            nested["teammate_accusations"]["denominator"],
        ),
        "alibi_survival": (
            nested["alibi_survival"]["survived"],
            nested["alibi_survival"]["total_impostor_alibis"],
        ),
        "effective_deflection": (
            nested["effective_deflection"]["effective_deflections"],
            nested["effective_deflection"]["active_survivals"],
        ),
        "crew_witnessed_kills": (
            kill_craft["crew_witnessed_kills"],
            kill_craft["kills_total"],
        ),
        "co_present_departure": (
            departure["co_present_ge1_kills"],
            departure["kills_total"],
        ),
        "off_menu": (
            off_menu["off_menu_total"],
            off_menu["impostor_decisions"],
        ),
    }


def f13_cell(
    rows: dict[str, dict[str, Any]], entrant: str, gauge: str
) -> tuple[float, float]:
    """One F13 (measured, split-half noise) cell.

    ``7f73929d``'s own n=49 watchability/split-half blocks already ARE the
    intersection view; every other arm reads its persisted
    ``f13_intersection_gauges`` cell.
    """

    if entrant == _P18_SHORT_ARM:
        gauges = _gauges(rows[entrant])
        return (
            gauges[gauge]["measured"],
            rows[entrant]["split_half"][gauge]["noise"],
        )
    cell = rows[entrant]["f13_intersection_gauges"]["gauges"][gauge]
    return cell["measured"], cell["split_half_noise"]


def fsm_comparator_win_rate() -> float:
    """The same-seed scripted-FSM impostor win rate from committed provenance."""

    manifest = parse_manifest(
        (_SAMPLES_9P2I / "MANIFEST.md").read_text(encoding="utf-8")
    )
    impostor_wins = sum(1 for row in manifest.values() if row.winner == "IMPOSTORS")
    return impostor_wins / len(manifest)


def crew_wins_excluding(row: dict[str, Any], seed: int) -> int:
    """The row's crew wins with one seed removed, from its own per-game bytes."""

    per_game = {game["seed"]: game for game in row["watchability"]["per_game"]}
    was_crew_win = per_game[seed]["reason"] in _CREW_WIN_REASONS
    return int(row["core"]["crew_wins"]) - (1 if was_crew_win else 0)


def build_champion_flip_golden() -> dict[str, Any]:
    """The measured cells + derived statistics behind the 17.16/18.27 ruling."""

    rows = load_finalist_rows()
    fsm_rate = fsm_comparator_win_rate()

    finalists: dict[str, Any] = {}
    for entrant in ("utility-es", "policy-es"):
        row = rows[entrant]
        finalists[entrant] = {
            "impostor_win_rate": row["core"]["impostor_win_rate"],
            "win_edge_vs_fsm": row["core"]["impostor_win_rate"] - fsm_rate,
            "referee_passed": row["watchability"]["referee_passed"],
            "mean_score": row["watchability"]["mean_score"],
            "gauges": _gauge_cells(row),
        }

    comparator = rows[_P18_COMPARATOR]
    comparator_win_seeds = impostor_win_seeds(comparator)
    intersection_rate = len(comparator_win_seeds - {35}) / 49

    candidates: dict[str, Any] = {}
    for entrant in (
        "p18-imp-ea4bc955",
        "p18-imp-bfd145cb",
        "p18-imp-6d327dcb",
        "p18-imp-7f73929d",
    ):
        row = rows[entrant]
        comparator_rate = (
            intersection_rate
            if entrant == _P18_SHORT_ARM
            else comparator["core"]["impostor_win_rate"]
        )
        candidates[entrant] = {
            "games_total": row["core"]["games_total"],
            "win_edge": row["core"]["impostor_win_rate"] - comparator_rate,
            "gauges": _gauge_cells(row),
        }

    f13: dict[str, Any] = {}
    for gauge in _F13_GAUGES:
        champ_cells = [f13_cell(rows, entrant, gauge) for entrant in _F13_CHAMPIONS]
        ru_cells = [f13_cell(rows, entrant, gauge) for entrant in _F13_RUNNER_UPS]
        margin = sum(measured for measured, _ in ru_cells) / 2 - (
            sum(measured for measured, _ in champ_cells) / 2
        )
        f13[gauge] = {
            "margin": margin,
            "champion_noise": sum(noise for _, noise in champ_cells) / 2,
            "runner_up_noise": sum(noise for _, noise in ru_cells) / 2,
        }
    bfd_conv, bfd_noise = f13_cell(rows, "p18-imp-bfd145cb", _F13_GAUGES[2])
    ea4_conv, ea4_noise = f13_cell(rows, _P18_CHAMPION_ARM, _F13_GAUGES[2])

    champion_cells = rate_cells(rows[_P18_CHAMPION_ARM])
    comparator_cells = rate_cells(comparator)
    z_values = {
        name: pooled_z(*champion_cells[name], *comparator_cells[name])
        for name in champion_cells
    }
    fisher = fisher_z(
        rows[_P18_CHAMPION_ARM]["instruments"]["kill_craft"][
            "witnessed_point_biserial_within_one_hop"
        ],
        rows[_P18_CHAMPION_ARM]["instruments"]["kill_craft"]["kills_total"],
        comparator["instruments"]["kill_craft"][
            "witnessed_point_biserial_within_one_hop"
        ],
        comparator["instruments"]["kill_craft"]["kills_total"],
    )

    return {
        "_generated_by": _GENERATED_BY,
        "fsm_comparator_win_rate": fsm_rate,
        "finalists": finalists,
        "p18": {
            "comparator": {
                "win_rate": comparator["core"]["impostor_win_rate"],
                "win_seed_count": len(comparator_win_seeds),
                "intersection_rate": intersection_rate,
            },
            "candidates": candidates,
            "bfd_flags_noise": rows["p18-imp-bfd145cb"]["split_half"][
                "flags_per_meeting"
            ]["noise"],
            "f13": f13,
            "f13_within_lineage_conversion": {
                "delta": bfd_conv - ea4_conv,
                "bfd_noise": bfd_noise,
                "ea4_noise": ea4_noise,
            },
            "axis2": {
                "pooled_z": z_values,
                "fisher_z": fisher,
                "clause_a_pass": sorted(
                    name
                    for name, z in z_values.items()
                    if z is not None and abs(z) >= 1.96
                ),
            },
        },
    }


def _arm_side(entrant: str) -> str:
    """An arm's side, from its pre-registered §8.1 name — never from row shape."""

    if entrant == _P18_COMPARATOR:
        return "comparator"
    if entrant.startswith("p18-imp-"):
        return "impostor"
    if entrant.startswith("p18-crew-"):
        return "crew"
    raise ValueError(f"entrant {entrant!r} matches no pre-registered side prefix")


def build_finalist_eval_golden() -> dict[str, Any]:
    """The 18.26 slate table + companion cells, in committed row order."""

    rows = load_finalist_rows()
    slate_rows = _phase18_rows_in_file_order()

    slate: list[dict[str, Any]] = []
    for row in slate_rows:
        entrant = row["entrant"]
        side = _arm_side(entrant)
        stamp = row[
            "crew_tactical_policy_stamp" if side == "crew" else "tactical_policy_stamp"
        ]
        gate = row["validity_gate"]
        slate.append(
            {
                "entrant": entrant,
                "side": side,
                "weights_sha256": row["committed_weights_sha256"],
                "artifact_path": row["artifact_path"],
                "policy_id": stamp["policy_id"],
                "method": stamp["method"],
                "encoder_version": stamp["encoder_version"],
                "anchor_policy": stamp["anchor_policy"],
                "games_total": row["core"]["games_total"],
                "stamp_games": row[
                    "crew_stamp_verified_games"
                    if side == "crew"
                    else "stamp_verified_games"
                ],
                "missing_seeds": sorted(
                    set(range(50)) - set(row["recording"]["seeds"])
                ),
                "impostor_wins": row["core"]["impostor_wins"],
                "impostor_win_rate": row["core"]["impostor_win_rate"],
                "meeting_rate": row["core"]["meeting_rate"],
                "mean_score": row["watchability"]["mean_score"],
                "median_score": row["watchability"]["median_score"],
                "referee_passed": row["watchability"]["referee_passed"],
                "validity_passed": gate["passed"],
                "validity_failures": sorted(
                    check["name"] for check in gate["checks"] if not check["passed"]
                ),
                # None where the row never carried the key (absent-vs-empty is
                # semantic — the test pins the distinction).
                "stalemate_replays": row.get("stalemate_games_no_game_over"),
                "retry_wall_seconds": row["leg_duration"]["retry_wall_seconds"],
                "co_present_ge1_kills": row["instruments"][
                    "kill_craft_co_present_departure"
                ]["co_present_ge1_kills"],
            }
        )

    f13_block = rows[_P18_CHAMPION_ARM]["f13_intersection_gauges"]
    f13_measured = {
        row["entrant"]: {
            gauge: row["f13_intersection_gauges"]["gauges"][gauge]["measured"]
            for gauge in _F13_GAUGES
        }
        for row in slate_rows
        if "f13_intersection_gauges" in row
    }

    nested_frame_conversions = {
        entrant: dict(
            rows[entrant]["instruments"]["registered_nested_cells"]["frame_conversions"]
        )
        for entrant in (_P18_CHAMPION_ARM, _P18_COMPARATOR)
    }

    intersection = rows[_P18_COMPARATOR]["instruments"][
        "intersection_49_seed_for_7f73929d"
    ]
    comparator_intersection = {
        "crew_witnessed_kills": intersection["crew_witnessed_kills"],
        "kills_total": intersection["kills_total"],
        "co_present_ge1_kills": intersection["co_present_ge1_kills"],
        "impostor_decisions": intersection["impostor_decisions"],
        "off_menu_total": intersection["off_menu_total"],
        "frame_attempts": dict(intersection["frame_attempts"]),
        "frame_conversions": dict(intersection["frame_conversions"]),
    }

    rider = rows["p18-crew-c1-gen9"]["instruments"]["kill_craft_rider_intersection"]
    c1_rider = {
        "excluded_seed": rider["excluded_seed"],
        "gen9_crew_witnessed_kills": rider["gen9_crew_witnessed_kills"],
        "gen9_kills_total": rider["gen9_kills_total"],
        "gen0_crew_witnessed_kills": rider["gen0_crew_witnessed_kills"],
        "gen0_kills_total": rider["gen0_kills_total"],
        "corpus_rate": rider["corpus_rate"],
    }

    paired = rows["p18-crew-c1-gen9"]["instruments"]["conversion_paired_49_seed"]
    paired_seed = paired["excluded_seed"]
    c1_paired = {
        "excluded_seed": paired_seed,
        "both_win": paired["both_win"],
        "gen9_only_win": paired["gen9_only_win"],
        "gen0_only_win": paired["gen0_only_win"],
        "neither_win": paired["neither_win"],
        "gen9_wins_49": crew_wins_excluding(rows["p18-crew-c1-gen9"], paired_seed),
        "gen0_wins_49": crew_wins_excluding(rows["p18-crew-c1-gen0"], paired_seed),
    }

    seventh_leg = rows[_P18_SHORT_ARM]["leg_duration"]
    retry = seventh_leg["post_pr_retry_leg"]
    leg_clocks = {
        "campaign_last_event_at": max(
            rows[row["entrant"]]["leg_duration"]["last_event_at"] for row in slate_rows
        ),
        "c2_gen0_wall_seconds": rows["p18-crew-c2-gen0"]["leg_duration"][
            "sum_wall_seconds_ok"
        ],
        "post_pr_retry_attempts": retry["attempts"],
        "in_leg_original_retry_wall_seconds": (
            seventh_leg["retry_wall_seconds"] - retry["sum_wall_seconds"]
        ),
    }

    return {
        "_generated_by": _GENERATED_BY,
        "slate": slate,
        "f13_intersection": {
            "excluded_seed": f13_block["excluded_seed"],
            "measured": f13_measured,
        },
        "nested_frame_conversions": nested_frame_conversions,
        "comparator_intersection": comparator_intersection,
        "c1_rider": c1_rider,
        "c1_paired": c1_paired,
        "leg_clocks": leg_clocks,
        "c2_gen9": {
            "tick_budget_reached": rows["p18-crew-c2-gen9"]["core"][
                "tick_budget_reached"
            ]
        },
    }


def serialize_golden(golden: dict[str, Any]) -> str:
    """Deterministic golden JSON: construction order, 2-space indent, newline."""

    return json.dumps(golden, indent=2) + "\n"


_GOLDEN_TARGETS: tuple[tuple[Path, Any], ...] = (
    (
        _REPO_ROOT / "tests" / "scripts" / "_goldens" / "champion_flip_ruling.json",
        build_champion_flip_golden,
    ),
    (
        _REPO_ROOT / "tests" / "training" / "_goldens" / "finalist_eval_pins.json",
        build_finalist_eval_golden,
    ),
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate the committed test goldens from the evidence bytes."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Regenerate in memory and diff against the committed goldens; "
        "exit 1 on drift (the byte-identity gate).",
    )
    args = parser.parse_args()

    drift = 0
    for path, builder in _GOLDEN_TARGETS:
        rendered = serialize_golden(builder())
        relative = path.relative_to(_REPO_ROOT)
        if args.check:
            if not path.exists():
                print(f"--check: {relative} is MISSING — run the script to write it.")
                drift = 1
            elif path.read_text(encoding="utf-8") != rendered:
                print(
                    f"--check: {relative} is STALE — it does not match a "
                    "regeneration from the committed evidence bytes. Re-run "
                    "`python scripts/regen_test_goldens.py`, review the diff, "
                    "and commit the result."
                )
                drift = 1
            else:
                print(f"--check: {relative} regenerates byte-identically.")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(rendered, encoding="utf-8")
            print(f"Wrote {relative}")
    return drift


if __name__ == "__main__":
    raise SystemExit(main())
