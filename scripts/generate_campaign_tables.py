#!/usr/bin/env python3
"""Render the campaign report's table families from committed artifacts (Task 18.31).

The 18.24 impostor campaign's report tables were hand-assembled from JSON that
was already correct, and **six** of that PR's review findings were transcription
or arithmetic errors — a transposed table, a doubled cost estimate, four count
errors (training/reports/report-impostor-campaign.md §11 defect 5). The §4.0
stability table was the exception: it is machine-computed, and it is the model
this generator generalizes. Every table below is a pure function of committed
bytes, so re-running it is a diff, not a proofread.

Three table families, three subcommands:

``rows``
    The §3 per-run campaign-row tables, from a ``campaign-rows.jsonl`` stream
    (schema ``coevo-campaign-v1``). A stream holding several runs concatenated
    — ``training/reports/results-impostor-campaign.jsonl`` is exactly that — is
    split on ``generation_index`` restarting at 1 and rendered one table per
    segment. Row bytes deliberately carry NO run name (the driver's
    ``run_label`` is stamp metadata, digest-inert and off the row schema), so
    segments are named by ``--label`` in order, else ``segment-<i>``.

``legs``
    The §4 per-leg tables, from a leg's ``ranking-*.jsonl`` files: the candidate
    legend, the 17.14 ranking table (selection / validity / referee / win /
    ejection accuracy / stamp proof), and the signed floor-sensitivity table
    (``measured − floor``, PASS/FAIL per Layer-1 gauge).

``stability``
    The §4.0 MEASUREMENT RELIABILITY table over any two-tranche ranking set,
    plus its machine-readable JSON.

**The free protocol precondition (F12), stated at the seam it runs from.**
``stability`` needs nothing but two tranches of ranking rows, so run it after
the FIRST RETESTED CANDIDATE of any campaign — not after the fortieth hour. The
18.24 campaign read its first non-replication as "that candidate was noise"
rather than "this measurement is noise" and recorded for roughly another day
before computing the table; had it been computed at hour ~16 it would have
re-framed the remaining ~24 h of recording before they were spent. The
computation is mechanical and free: point ``--ranking-root`` at whatever
lineage roots the campaign has recorded so far.

Determinism: every renderer sorts its inputs and formats floats to fixed
precision, so two runs over the same bytes emit identical bytes. Nothing here
writes into ``training/artifacts/`` — the committed 18.24 record is read-only
history to this tool.

Usage::

    python scripts/generate_campaign_tables.py rows \\
        --rows-path training/reports/results-impostor-campaign.jsonl
    python scripts/generate_campaign_tables.py legs \\
        --leg-dir training/artifacts/coevo/realpath/run-01-utility-champion
    python scripts/generate_campaign_tables.py stability --check \\
        training/artifacts/coevo/measurement-stability.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# --------------------------------------------------------------------------- #
# Constants.                                                                   #
# --------------------------------------------------------------------------- #

#: The committed stability artifact this generator reproduces.
DEFAULT_STABILITY_ARTIFACT: Final[Path] = Path(
    "training/artifacts/coevo/measurement-stability.json"
)

#: The 18.24 campaign's LINEAGE ranking roots — the arms §4.0's stability table
#: is computed over. Counterfactual roots are deliberately absent and named here
#: rather than filtered silently: ``realpath-ablation/`` holds the §6 ablation
#: arms (a different objective, not a re-read of the same lineage) and
#: ``realpath-comparator/`` holds the scripted-FSM comparator (no candidate
#: genome at all). Any campaign passes its own roots with ``--ranking-root``.
DEFAULT_RANKING_ROOTS: Final[tuple[Path, ...]] = (
    Path("training/artifacts/coevo/realpath"),
    Path("training/artifacts/coevo/realpath-backfill"),
    Path("training/artifacts/coevo/realpath-runnerups"),
    Path("training/artifacts/coevo/realpath-runnerups-gen3"),
)

#: The §4.0 combination rule, stated in the artifact because it CHANGES the
#: numbers. Emitted verbatim so the artifact carries its own definition.
COMBINATION_RULE: Final[str] = (
    "each (leg, genome) pair is ONE ARM: a policy recorded in two different "
    "lineage legs contributes independent provider draws and is counted twice. "
    "An earlier revision keyed by genome sha alone, which silently discarded "
    "the duplicate arm and made the result depend on filesystem traversal order "
    "(6d327dcb was recorded in both run-01 and run-03 on both tranches)."
)

#: The supply gauge whose tranche-to-tranche swing IS the noise measurement.
_NOISE_GAUGE: Final[str] = "flags_per_meeting"

#: The population-relative conversion gauge whose floor saturates at 1.000 —
#: a structurally unpassable bar, since a conversion fraction cannot exceed 1.
_CONVERSION_GAUGE: Final[str] = "testimony_backed_conversion"
_IMPOSSIBLE_FLOOR: Final[float] = 1.0

#: A win-rate swing of a full game, with a tolerance for float division.
_ONE_GAME: Final[float] = 1.0 - 1e-9

_SHA_DISPLAY_CHARS: Final[int] = 8


# --------------------------------------------------------------------------- #
# Shared helpers.                                                              #
# --------------------------------------------------------------------------- #


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read a JSONL artifact into dicts, failing loud on a malformed line."""

    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{number} is not valid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise SystemExit(f"{path}:{number} is not a JSON object")
        rows.append(row)
    if not rows:
        raise SystemExit(f"{path} holds no rows")
    return rows


def _display(path: Path) -> str:
    """Repo-relative when possible, so rendered headings are machine-independent."""

    try:
        return path.resolve().relative_to(_REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _short(sha: str) -> str:
    """The report's candidate shorthand: the first 8 hex chars + an ellipsis."""

    return f"`{sha[:_SHA_DISPLAY_CHARS]}…`"


def _table(headers: Sequence[str], rows: Iterable[Sequence[str]]) -> list[str]:
    """One GitHub-flavoured markdown table (fixed column order, no alignment padding)."""

    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    lines.extend("| " + " | ".join(cells) + " |" for cells in rows)
    return lines


def _fixed(value: float | None, places: int) -> str:
    """A fixed-precision cell; ``None`` renders as ``None`` (never a zero-ghost)."""

    return "None" if value is None else f"{value:.{places}f}"


def _verdict(passed: bool) -> str:
    return "PASS" if passed else "FAIL"


def _gauge(row: Mapping[str, Any], name: str) -> Mapping[str, Any] | None:
    for gauge in row["watchability"]["supply_gauges"]:
        if gauge["name"] == name:
            typed: Mapping[str, Any] = gauge
            return typed
    return None


def _require_gauge(
    row: Mapping[str, Any], name: str, *, where: str
) -> Mapping[str, Any]:
    gauge = _gauge(row, name)
    if gauge is None:
        raise SystemExit(
            f"{where}: ranking row {row.get('label')!r} carries no {name!r} supply "
            "gauge; the stability table cannot be computed from it"
        )
    return gauge


# --------------------------------------------------------------------------- #
# Family 1 — the §3 campaign-row tables.                                       #
# --------------------------------------------------------------------------- #

_ROW_HEADERS: Final[tuple[str, ...]] = (
    "gen",
    "swap",
    "moving",
    "pool",
    "champion_fitness",
    "updated",
    "anchor_champ",
    "anchor_fsm",
    "exploiter",
    "conv_uses",
    "games_cum",
)


def split_run_segments(
    rows: Sequence[Mapping[str, Any]],
) -> list[list[Mapping[str, Any]]]:
    """Split a concatenated row stream where ``generation_index`` restarts at 1.

    The committed ``results-impostor-campaign.jsonl`` is five runs' streams
    concatenated in run order; §3 states the boundary rule this implements. A
    stream that does not start at generation 1 is a truncated extract and fails
    loud rather than being rendered as a run.
    """

    if rows and rows[0].get("generation_index") != 1:
        raise SystemExit(
            "the row stream does not begin at generation_index 1 "
            f"(got {rows[0].get('generation_index')!r}); it is a partial extract, "
            "not a run"
        )
    segments: list[list[Mapping[str, Any]]] = []
    for row in rows:
        if row.get("generation_index") == 1:
            segments.append([])
        segments[-1].append(row)
    return segments


def _exploiter_cell(row: Mapping[str, Any]) -> str:
    outcome = row["exploiter_outcome"]
    if outcome != "frozen":
        return str(outcome)
    return (
        f"**frozen** {row['exploiter_fitness']:.2f}>"
        f"{row['exploiter_baseline_fitness']:.2f}"
    )


def render_rows_table(rows: Sequence[Mapping[str, Any]], *, label: str) -> list[str]:
    """The §3 table for one run segment, plus its machine-derived footer."""

    body = [
        (
            str(row["generation_index"]),
            str(row["swap_index"]),
            str(row["moving_side"]),
            str(row["opponent_pool_size"]),
            f"{row['champion_fitness']:.4f}",
            "yes" if row["champion_updated"] else "no",
            f"{row['anchor_benchmark_champion_side']:.4f}",
            f"{row['anchor_benchmark_fsm_side']:.4f}",
            _exploiter_cell(row),
            "—" if row["conviction_uses"] is None else str(row["conviction_uses"]),
            str(row["games_played_cumulative"]),
        )
        for row in rows
    ]
    last = rows[-1]
    frozen = [
        f"swap {row['swap_index']} {row['moving_side']} `{row['champion_frozen_sha']}`"
        for row in rows
        if row["champion_frozen"]
    ]
    footer = (
        f"Rows: {len(rows)}; swaps: {last['swap_index'] + 1}; games: "
        f"{last['games_played_cumulative']}; conviction uses: "
        f"{last['conviction_uses'] if last['conviction_uses'] is not None else '—'}; "
        f"surrogate uses: "
        f"{last['surrogate_uses'] if last['surrogate_uses'] is not None else '—'}; "
        f"exploiter freezes: "
        f"{sum(1 for row in rows if row['exploiter_outcome'] == 'frozen')}."
    )
    lines = [f"### {label}", ""]
    lines.extend(_table(_ROW_HEADERS, body))
    lines.extend(["", footer, ""])
    if frozen:
        lines.extend(["Frozen swap champions: " + "; ".join(frozen) + ".", ""])
    return lines


def render_rows_document(rows_path: Path, *, labels: Sequence[str]) -> str:
    """Every §3 table for a campaign-row stream, in stream order."""

    segments = split_run_segments(_read_jsonl(rows_path))
    lines = [f"## Campaign rows — {_display(rows_path)}", ""]
    for index, segment in enumerate(segments):
        label = labels[index] if index < len(labels) else f"segment-{index + 1}"
        lines.extend(render_rows_table(segment, label=label))
    return "\n".join(lines).rstrip("\n") + "\n"


# --------------------------------------------------------------------------- #
# Family 2 — the §4 leg tables.                                                #
# --------------------------------------------------------------------------- #

_RANKING_HEADERS: Final[tuple[str, ...]] = (
    "rank",
    "candidate",
    "selection",
    "validity",
    "referee",
    "win",
    "ejection acc",
    "stamp proof",
)


def _stamp_proof(row: Mapping[str, Any]) -> str:
    """The 17.14 stamp-proof cell, rendered from the row's own proof fields."""

    parts = [f"{row['stamp_verified_games']}/{len(row['seeds'])} games stamped"]
    parts.append("uniform" if row["stamp_uniform"] else "**NOT uniform**")
    parts.append(
        "sha == computed digest"
        if row["stamp_equals_computed_digest"]
        else "**sha != computed digest**"
    )
    return ", ".join(parts)


def render_leg_tables(ranking_path: Path) -> list[str]:
    """The candidate legend + ranking + floor-sensitivity tables for one tranche."""

    rows = sorted(_read_jsonl(ranking_path), key=lambda row: row["rank"])
    legend = _table(
        ("candidate", "label", "weights_sha256"),
        [
            (_short(row["weights_sha256"]), f"`{row['label']}`", row["weights_sha256"])
            for row in rows
        ],
    )
    ranking = _table(
        _RANKING_HEADERS,
        [
            (
                str(row["rank"]),
                _short(row["weights_sha256"]),
                _fixed(row["selection_score"], 2),
                _verdict(row["validity_passed"]),
                _verdict(row["referee_passed"]),
                _fixed(row["core_impostor_win_rate"], 3),
                _fixed(row["core_ejection_accuracy"], 3),
                _stamp_proof(row),
            )
            for row in rows
        ],
    )

    gauge_names = tuple(
        gauge["name"] for gauge in rows[0]["watchability"]["supply_gauges"]
    )
    for row in rows[1:]:
        other = tuple(gauge["name"] for gauge in row["watchability"]["supply_gauges"])
        if other != gauge_names:
            raise SystemExit(
                f"{ranking_path}: candidate {row['label']!r} reports supply gauges "
                f"{other} but rank 1 reports {gauge_names}; a leg table cannot mix "
                "gauge sets"
            )
    sensitivity = _table(
        ("candidate", *gauge_names),
        [
            (
                _short(row["weights_sha256"]),
                *(
                    _sensitivity_cell(
                        _require_gauge(row, name, where=str(ranking_path))
                    )
                    for name in gauge_names
                ),
            )
            for row in rows
        ],
    )

    seeds = rows[0]["seeds"]
    lines = [
        f"### Leg — {_display(ranking_path)}",
        "",
        f"Seeds {seeds}; roster "
        f"{rows[0]['num_players']}p{rows[0]['num_impostors']}i; baseline "
        f"`{rows[0]['baseline_id']}`; mode `{rows[0]['mode']}`; per-seed retry "
        f"budget {rows[0]['max_attempts']}; meeting timeout "
        f"{rows[0]['meeting_timeout_seconds']:.1f}s.",
        "",
        "**Candidates:**",
        "",
        *legend,
        "",
        "**Ranking (17.14 discipline — stamp proofs beside every read):**",
        "",
        *ranking,
        "",
        "**Floor sensitivity (measured − floor, signed):**",
        "",
        *sensitivity,
        "",
    ]
    return lines


def _sensitivity_cell(gauge: Mapping[str, Any]) -> str:
    """One signed floor-distance cell (``None`` measured is an honest FAIL)."""

    measured = gauge["measured"]
    floor = gauge["floor"]
    suffix = " (advisory)" if gauge.get("advisory") else ""
    if floor is None:
        return (
            f"{_fixed(measured, 4)} vs no floor → {_verdict(gauge['passed'])}{suffix}"
        )
    if measured is None:
        return (
            f"None vs {floor:.4f} → **{_verdict(gauge['passed'])}** "
            f"(denominator empty){suffix}"
        )
    delta = measured - floor
    return (
        f"{measured:.4f} − {floor:.4f} = **{delta:+.4f} "
        f"{_verdict(gauge['passed'])}**{suffix}"
    )


def find_ranking_files(roots: Sequence[Path]) -> list[Path]:
    """Every ``ranking-*.jsonl`` under the given roots, in sorted path order."""

    found: list[Path] = []
    for root in roots:
        if not root.is_dir():
            raise SystemExit(f"ranking root {root} is not a directory")
        found.extend(sorted(root.rglob("ranking-*.jsonl")))
    if not found:
        raise SystemExit(f"no ranking-*.jsonl files under {[str(r) for r in roots]}")
    return found


def render_legs_document(ranking_paths: Sequence[Path]) -> str:
    """Every leg's tables, in sorted path order."""

    lines = ["## Real-path re-rank legs", ""]
    for path in ranking_paths:
        lines.extend(render_leg_tables(path))
    return "\n".join(lines).rstrip("\n") + "\n"


# --------------------------------------------------------------------------- #
# Family 3 — the §4.0 measurement-stability table.                             #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class _Arm:
    """One ``(leg, genome)`` arm's two tranche reads (the §4.0 combination rule)."""

    leg: str
    weights_sha256: str
    first: Mapping[str, Any]
    second: Mapping[str, Any]


def _collect_arms(
    ranking_paths: Sequence[Path],
) -> tuple[dict[tuple[str, str], dict[str, Mapping[str, Any]]], list[_Arm]]:
    """Group ranking rows by ``(leg dir, genome sha)`` -> tranche -> row.

    The tranche key is the ranking file's own suffix, so two files in one leg
    dir are two independent provider draws of the same arm. A third read of one
    arm in one leg is not representable in a two-tranche stability check and
    fails loud rather than silently picking two of them.
    """

    by_arm: dict[tuple[str, str], dict[str, Mapping[str, Any]]] = {}
    for path in ranking_paths:
        leg = path.parent.as_posix()
        tranche = path.name.removeprefix("ranking-").removesuffix(".jsonl")
        for row in _read_jsonl(path):
            key = (leg, row["weights_sha256"])
            reads = by_arm.setdefault(key, {})
            if tranche in reads:
                raise SystemExit(
                    f"{path}: genome {row['weights_sha256']} appears twice in one "
                    "tranche of one leg; an arm is one (leg, genome) pair"
                )
            reads[tranche] = row
    arms: list[_Arm] = []
    for (leg, sha), reads in sorted(by_arm.items()):
        if len(reads) < 2:
            continue
        if len(reads) > 2:
            raise SystemExit(
                f"{leg}: genome {sha} was recorded on {sorted(reads)} — the "
                "stability check compares exactly two independent tranches; pass "
                "the two roots you mean to compare"
            )
        first_key, second_key = sorted(reads)
        arms.append(
            _Arm(
                leg=leg,
                weights_sha256=sha,
                first=reads[first_key],
                second=reads[second_key],
            )
        )
    return by_arm, arms


def compute_stability(ranking_paths: Sequence[Path]) -> dict[str, Any]:
    """The §4.0 stability numbers over any two-tranche ranking set.

    Every quantity is a pure fold over the committed rows: the mean absolute
    tranche-to-tranche swing in ``flags_per_meeting``, that swing as a fraction
    of the floor the gauge is tested against, how many arms faced a
    structurally unpassable (``>= 1.000``) conversion floor on at least one
    tranche, the mean absolute win-rate swing in games, how many arms swung a
    full game, and the referee PASS / retested / replicated census.
    """

    by_arm, arms = _collect_arms(ranking_paths)
    if not arms:
        raise SystemExit(
            "no arm was recorded on two tranches; the stability check needs a "
            "retest (run it after the campaign's FIRST retested candidate — F12)"
        )

    floors = {
        _require_gauge(read, _NOISE_GAUGE, where=arm.leg)["floor"]
        for arm in arms
        for read in (arm.first, arm.second)
    }
    if len(floors) != 1:
        raise SystemExit(
            f"the {_NOISE_GAUGE} floor is not uniform across the arms ({sorted(floors)}); "
            "a noise-to-threshold ratio needs ONE threshold"
        )
    (flags_floor,) = floors
    if flags_floor is None or flags_floor <= 0.0:
        raise SystemExit(
            f"the {_NOISE_GAUGE} floor is {flags_floor!r}; a noise-to-threshold "
            "ratio needs a positive threshold"
        )

    flag_swings: list[float] = []
    win_swings: list[float] = []
    impossible = 0
    swinging = 0
    for arm in arms:
        reads = (arm.first, arm.second)
        measured = [
            _require_gauge(read, _NOISE_GAUGE, where=arm.leg)["measured"]
            for read in reads
        ]
        if any(value is None for value in measured):
            raise SystemExit(
                f"{arm.leg}: genome {arm.weights_sha256} has no measured "
                f"{_NOISE_GAUGE} on one tranche; an unmeasured gauge has no swing"
            )
        flag_swings.append(abs(float(measured[0]) - float(measured[1])))
        conversion_floors = [
            _require_gauge(read, _CONVERSION_GAUGE, where=arm.leg)["floor"]
            for read in reads
        ]
        if any(
            floor is not None and floor >= _IMPOSSIBLE_FLOOR
            for floor in conversion_floors
        ):
            impossible += 1
        wins = [
            read["core_impostor_win_rate"] * read["core_games_total"] for read in reads
        ]
        swing = abs(wins[0] - wins[1])
        win_swings.append(swing)
        if swing >= _ONE_GAME:
            swinging += 1

    mean_flags = sum(flag_swings) / len(flag_swings)
    passes = [
        (key, tranche)
        for key, reads in sorted(by_arm.items())
        for tranche, row in sorted(reads.items())
        if row["referee_passed"]
    ]
    retested = sum(
        1 for arm in arms if arm.first["referee_passed"] or arm.second["referee_passed"]
    )
    replicated = sum(
        1
        for arm in arms
        if arm.first["referee_passed"] and arm.second["referee_passed"]
    )
    return {
        "arms_swinging_ge_one_game": swinging,
        "arms_with_both_tranches": len(arms),
        "arms_with_impossible_conversion_floor": impossible,
        "combination_rule": COMBINATION_RULE,
        "distinct_genomes": len({arm.weights_sha256 for arm in arms}),
        "flags_floor": flags_floor,
        "mean_abs_flags_swing": round(mean_flags, 4),
        "mean_abs_win_swing_games_of_3": round(sum(win_swings) / len(win_swings), 2),
        "noise_to_threshold_ratio": round(mean_flags / flags_floor, 4),
        "referee_passes_replicated": replicated,
        "referee_passes_retested": retested,
        "referee_passes_total": len(passes),
    }


def render_stability_table(stability: Mapping[str, Any]) -> str:
    """The §4.0 markdown table for a computed stability mapping."""

    arms = stability["arms_with_both_tranches"]
    genomes = stability["distinct_genomes"]
    header = (
        f"stability check — **{arms} ARMS** ({genomes} distinct genomes) "
        "recorded on both tranches"
    )
    body = [
        (
            f"mean absolute swing in `{_NOISE_GAUGE}` between tranches",
            f"**{stability['mean_abs_flags_swing']:.4f}**",
        ),
        (
            "the floor that quantity is tested against",
            f"{stability['flags_floor']:.4f}",
        ),
        (
            "**noise as a fraction of the threshold**",
            f"**{stability['noise_to_threshold_ratio'] * 100:.0f}%**",
        ),
        (
            "arms whose derived conversion floor hit 1.000 (structurally "
            "unpassable) on ≥1 tranche",
            f"**{stability['arms_with_impossible_conversion_floor']} of {arms}**",
        ),
        (
            "mean absolute win-rate swing, in games",
            f"{stability['mean_abs_win_swing_games_of_3']:.2f}",
        ),
        (
            "arms swinging ≥ 1 game in win rate between tranches",
            f"**{stability['arms_swinging_ge_one_game']} of {arms}**",
        ),
        (
            "referee PASSes recorded / retested / replicated",
            f"**{stability['referee_passes_total']} / "
            f"{stability['referee_passes_retested']} / "
            f"{stability['referee_passes_replicated']}**",
        ),
    ]
    lines = _table((header, "value"), body)
    lines.extend(["", f"**Combination rule:** {stability['combination_rule']}"])
    return "\n".join(lines) + "\n"


def stability_json(stability: Mapping[str, Any]) -> str:
    """The committed artifact's exact byte form: key-sorted, indent 2, no newline.

    Byte-for-byte what ``training/artifacts/coevo/measurement-stability.json``
    holds (including its missing trailing newline), so ``--json-out`` over that
    path is a no-op diff rather than a reformat.
    """

    return json.dumps(stability, indent=2, sort_keys=True)


# --------------------------------------------------------------------------- #
# CLI.                                                                         #
# --------------------------------------------------------------------------- #


def _emit(text: str, out: Path | None) -> None:
    if out is None:
        sys.stdout.write(text)
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else _REPO_ROOT / path


def _run_stability(args: argparse.Namespace) -> int:
    roots = [
        _resolve(Path(root))
        for root in (args.ranking_root or [str(p) for p in DEFAULT_RANKING_ROOTS])
    ]
    if args.check is not None and (args.out is not None or args.json_out is not None):
        raise SystemExit(
            "--check VERIFIES a committed artifact and writes nothing; drop --out / "
            "--json-out (or drop --check to render)."
        )
    stability = compute_stability(find_ranking_files(roots))
    if args.check is not None:
        committed_path = _resolve(Path(args.check))
        committed = json.loads(committed_path.read_text(encoding="utf-8"))
        drift = sorted(
            key
            for key in set(stability) | set(committed)
            if stability.get(key) != committed.get(key)
        )
        if drift:
            for key in drift:
                sys.stderr.write(
                    f"{key}: computed {stability.get(key)!r} != committed "
                    f"{committed.get(key)!r}\n"
                )
            sys.stderr.write(
                f"{committed_path} does not reproduce from {[str(r) for r in roots]}\n"
            )
            return 1
        sys.stdout.write(
            f"{committed_path.as_posix()} reproduces exactly "
            f"({stability['arms_with_both_tranches']} arms, "
            f"{stability['distinct_genomes']} distinct genomes).\n"
        )
        return 0
    if args.json_out is not None:
        _emit(stability_json(stability), _resolve(Path(args.json_out)))
    _emit(
        render_stability_table(stability),
        None if args.out is None else _resolve(Path(args.out)),
    )
    return 0


def _run_rows(args: argparse.Namespace) -> int:
    document = render_rows_document(
        _resolve(Path(args.rows_path)), labels=args.label or []
    )
    _emit(document, None if args.out is None else _resolve(Path(args.out)))
    return 0


def _run_legs(args: argparse.Namespace) -> int:
    if args.ranking:
        paths = [_resolve(Path(entry)) for entry in args.ranking]
    else:
        paths = find_ranking_files([_resolve(Path(args.leg_dir))])
    document = render_legs_document(paths)
    _emit(document, None if args.out is None else _resolve(Path(args.out)))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Render the campaign report's table families from committed artifacts "
            "(Task 18.31). Every table is a pure function of the bytes it reads."
        ),
        epilog=(
            "Protocol precondition (F12): run `stability` after the FIRST RETESTED "
            "candidate of a campaign — it needs nothing but two tranches of "
            "ranking rows, and reading the noise level early re-frames what is "
            "worth recording next."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    rows = subparsers.add_parser("rows", help="the §3 campaign-row tables")
    rows.add_argument(
        "--rows-path",
        required=True,
        help="a coevo-campaign-v1 campaign-rows.jsonl stream (runs may be concatenated)",
    )
    rows.add_argument(
        "--label",
        action="append",
        help="segment name, in stream order (repeatable); default segment-<i>",
    )
    rows.add_argument("--out", help="write the markdown here instead of stdout")
    rows.set_defaults(handler=_run_rows)

    legs = subparsers.add_parser("legs", help="the §4 per-leg tables")
    source = legs.add_mutually_exclusive_group(required=True)
    source.add_argument("--leg-dir", help="a leg dir holding ranking-*.jsonl files")
    source.add_argument(
        "--ranking", action="append", help="an explicit ranking JSONL (repeatable)"
    )
    legs.add_argument("--out", help="write the markdown here instead of stdout")
    legs.set_defaults(handler=_run_legs)

    stability = subparsers.add_parser(
        "stability", help="the §4.0 measurement-stability table"
    )
    stability.add_argument(
        "--ranking-root",
        action="append",
        help=(
            "a ranking root to walk (repeatable); default: the 18.24 lineage roots "
            f"{[str(p) for p in DEFAULT_RANKING_ROOTS]}"
        ),
    )
    stability.add_argument("--out", help="write the markdown here instead of stdout")
    stability.add_argument(
        "--json-out", help="also write the machine-readable JSON here"
    )
    stability.add_argument(
        "--check",
        nargs="?",
        const=str(DEFAULT_STABILITY_ARTIFACT),
        help=(
            "recompute and diff against a committed stability JSON, exiting "
            f"non-zero on drift (default {DEFAULT_STABILITY_ARTIFACT})"
        ),
    )
    stability.set_defaults(handler=_run_stability)

    args = parser.parse_args(argv)
    handler: Any = args.handler
    exit_code: int = handler(args)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
