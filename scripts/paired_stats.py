"""Paired exact-McNemar + Wilson intervals over a finalist-eval JSONL (Task 19.20).

The finalist eval runs every arm over the SAME seed set, so the honest test of
"is this arm better than the FSM comparator?" is a PAIRED one: per seed, did the
arm win where the comparator lost (``b``), or lose where it won (``c``)? This
module recomputes that from the committed measurement — no re-run, no re-record,
pure stdlib arithmetic (``math.comb``; no numpy, no scipy) so the numbers a
report quotes can be reproduced byte-for-byte on a fresh clone.

Win = an IMPOSTOR win for the arm's impostor side (``IMPOSTOR_PARITY`` or
``IMPOSTOR_SABOTAGE``); loss = a crew win (``CREWMATE_EJECT`` or
``CREWMATE_TASKS``). Any other ``reason`` string on an entrant a comparison
actually reads is NOT silently dropped — it raises. (The committed file's CREW
arms carry a ``"no game_over record in replay"`` reason; they are never one of
the compared sides, so their rows are loaded raw and left unmapped.)

The two-sided p is the EXACT binomial on the discordant pairs (``b + c`` trials
at 1/2), not the chi-square approximation: with b + c on the order of 20 the
approximation is exactly where a marginal result would be manufactured.
Intervals are Wilson score (95%), which stays inside [0, 1] at the edges where
the normal approximation would not.

Usage::

    uv run python scripts/paired_stats.py training/reports/results-finalist-eval.jsonl
    uv run python scripts/paired_stats.py training/reports/results-finalist-eval.jsonl \
        --json
    uv run python scripts/paired_stats.py results.jsonl --baseline p18-fsm-comparator

``--json`` emits a JSON array of :class:`ArmPairedStats` rows (the machine-
readable form Task 19.23's report generator consumes).

Exit codes: ``0`` success, ``2`` usage error (file missing, entrant missing,
malformed rows — the message goes to stderr). Pure + offline: no network, no
``AILIBI_*`` env.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Final, cast

from pydantic import BaseModel, ConfigDict

#: ``reason`` strings that count as a WIN for the arm's impostor side.
IMPOSTOR_WIN_REASONS: Final[frozenset[str]] = frozenset(
    {"IMPOSTOR_PARITY", "IMPOSTOR_SABOTAGE"}
)
#: ``reason`` strings that count as a LOSS for the arm's impostor side.
CREW_WIN_REASONS: Final[frozenset[str]] = frozenset(
    {"CREWMATE_EJECT", "CREWMATE_TASKS"}
)
#: The default paired baseline (the Phase-18 hand-written FSM comparator).
DEFAULT_BASELINE: Final[str] = "p18-fsm-comparator"
#: Autodetected arms are the learned-impostor entrants.
ARM_PREFIX: Final[str] = "p18-imp-"
#: 97.5th percentile of the standard normal (two-sided 95%).
Z_95: Final[float] = 1.959963984540054
#: Family-wise error rate the Bonferroni line corrects.
FAMILY_ALPHA: Final[float] = 0.05


class ArmPairedStats(BaseModel):
    """One arm's paired comparison against the baseline (frozen value object).

    ``b`` / ``c`` are the discordant pair counts (arm wins where the baseline
    loses / arm loses where the baseline wins); ``p_exact`` is the two-sided
    exact-binomial McNemar p over those. Wilson bounds are flat floats rather
    than tuples so ``--json`` rows stay a flat table.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    entrant: str
    n: int
    arm_wins: int
    baseline_wins: int
    delta: float
    b: int
    c: int
    p_exact: float
    arm_rate: float
    baseline_rate: float
    arm_wilson_low: float
    arm_wilson_high: float
    baseline_wilson_low: float
    baseline_wilson_high: float


def exact_mcnemar_p(b: int, c: int) -> float:
    """Two-sided EXACT binomial McNemar p over discordant pairs ``b`` and ``c``.

    Under the null the ``n = b + c`` discordant pairs are fair coin flips, so the
    two-sided p is twice the lower tail at ``k = min(b, c)``, capped at 1.0. With
    no discordant pairs at all there is no evidence either way and p is 1.0.

    Raises ``ValueError`` on a negative count.
    """

    if b < 0 or c < 0:
        raise ValueError(f"discordant counts must be non-negative, got b={b}, c={c}")
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1))
    return min(1.0, 2.0 * tail / 2.0**n)


def wilson_interval(successes: int, total: int, z: float = Z_95) -> tuple[float, float]:
    """Wilson score interval for a binomial rate (default two-sided 95%).

    Preferred over the normal approximation because it stays inside [0, 1] and
    does not collapse to a zero-width interval at ``successes`` 0 or ``total``.

    Raises ``ValueError`` on a non-positive ``total`` or ``successes`` outside
    ``[0, total]``.
    """

    if total <= 0:
        raise ValueError(f"total must be positive, got {total}")
    if successes < 0 or successes > total:
        raise ValueError(f"successes must be in [0, {total}], got {successes}")
    phat = successes / total
    denom = 1.0 + z * z / total
    center = (phat + z * z / (2.0 * total)) / denom
    half = (
        z * math.sqrt(phat * (1.0 - phat) / total + z * z / (4.0 * total * total))
    ) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def _require_object(value: object, what: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{what}: expected a JSON object, got {type(value).__name__}")
    return cast(dict[str, Any], value)


def _require_str(value: object, what: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{what}: expected a string, got {type(value).__name__}")
    return value


def _require_int(value: object, what: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{what}: expected an integer, got {type(value).__name__}")
    return value


def _arm_won(reason: str, *, entrant: str, seed: int) -> bool:
    """Map a game-over ``reason`` to an arm win, refusing anything unrecognised."""

    if reason in IMPOSTOR_WIN_REASONS:
        return True
    if reason in CREW_WIN_REASONS:
        return False
    raise ValueError(
        f"{entrant} seed {seed}: unrecognised game-over reason {reason!r} "
        f"(expected one of {sorted(IMPOSTOR_WIN_REASONS | CREW_WIN_REASONS)})"
    )


def _load_reasons(jsonl_path: Path) -> dict[str, dict[int, str]]:
    """Load ``entrant -> {seed: reason}`` from a finalist-eval JSONL.

    Reasons are kept RAW here and mapped to win/loss only for the entrants a
    comparison actually reads (:func:`_arm_won`) — the file also carries crew
    arms whose unrecognised reasons must not veto an impostor-arm comparison
    they take no part in.

    Raises ``ValueError`` on a missing file, a malformed line, a duplicate
    entrant, or a duplicate seed within an entrant.
    """

    if not jsonl_path.is_file():
        raise ValueError(f"Results JSONL not found: {jsonl_path}")
    outcomes: dict[str, dict[int, str]] = {}
    for lineno, raw in enumerate(jsonl_path.read_text().splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{jsonl_path}:{lineno}: malformed JSON ({exc})") from exc
        row = _require_object(parsed, f"{jsonl_path}:{lineno}")
        if "entrant" not in row:
            raise ValueError(f"{jsonl_path}:{lineno}: row has no 'entrant' field")
        entrant = _require_str(row["entrant"], f"{jsonl_path}:{lineno} entrant")
        if entrant in outcomes:
            raise ValueError(f"{jsonl_path}:{lineno}: duplicate entrant {entrant!r}")
        watchability = _require_object(
            row.get("watchability"), f"{entrant}: watchability"
        )
        per_game = watchability.get("per_game")
        if not isinstance(per_game, list):
            raise ValueError(
                f"{entrant}: watchability.per_game must be a list, got "
                f"{type(per_game).__name__}"
            )
        games: dict[int, str] = {}
        for index, entry in enumerate(per_game):
            game = _require_object(entry, f"{entrant}: per_game[{index}]")
            seed = _require_int(game.get("seed"), f"{entrant}: per_game[{index}].seed")
            if seed in games:
                raise ValueError(f"{entrant}: duplicate seed {seed} in per_game")
            games[seed] = _require_str(
                game.get("reason"), f"{entrant}: per_game[{index}].reason"
            )
        if not games:
            raise ValueError(f"{entrant}: watchability.per_game is empty")
        outcomes[entrant] = games
    if not outcomes:
        raise ValueError(f"{jsonl_path}: no result rows")
    return outcomes


def _pair_one_arm(
    entrant: str,
    arm_reasons: dict[int, str],
    baseline_entrant: str,
    baseline_reasons: dict[int, str],
) -> ArmPairedStats:
    seeds = sorted(set(arm_reasons) & set(baseline_reasons))
    if not seeds:
        raise ValueError(f"{entrant}: no seeds shared with baseline {baseline_entrant}")
    arm = {
        seed: _arm_won(arm_reasons[seed], entrant=entrant, seed=seed) for seed in seeds
    }
    baseline = {
        seed: _arm_won(baseline_reasons[seed], entrant=baseline_entrant, seed=seed)
        for seed in seeds
    }
    n = len(seeds)
    arm_wins = sum(1 for seed in seeds if arm[seed])
    baseline_wins = sum(1 for seed in seeds if baseline[seed])
    b = sum(1 for seed in seeds if arm[seed] and not baseline[seed])
    c = sum(1 for seed in seeds if not arm[seed] and baseline[seed])
    arm_low, arm_high = wilson_interval(arm_wins, n)
    base_low, base_high = wilson_interval(baseline_wins, n)
    return ArmPairedStats(
        entrant=entrant,
        n=n,
        arm_wins=arm_wins,
        baseline_wins=baseline_wins,
        delta=(arm_wins - baseline_wins) / n,
        b=b,
        c=c,
        p_exact=exact_mcnemar_p(b, c),
        arm_rate=arm_wins / n,
        baseline_rate=baseline_wins / n,
        arm_wilson_low=arm_low,
        arm_wilson_high=arm_high,
        baseline_wilson_low=base_low,
        baseline_wilson_high=base_high,
    )


def compute_paired_stats(
    jsonl_path: Path,
    *,
    baseline_entrant: str = DEFAULT_BASELINE,
    arm_entrants: Sequence[str] | None = None,
) -> list[ArmPairedStats]:
    """Recompute the paired arm-vs-baseline statistics from a finalist-eval JSONL.

    Arms are paired with the baseline on the SORTED INTERSECTION of their seed
    sets (an arm that recorded fewer games is compared only over the seeds both
    actually played). ``arm_entrants=None`` autodetects every entrant whose name
    starts with ``p18-imp-``, in file order.

    Raises ``ValueError`` if the file is missing or malformed, if the baseline or
    a named arm is absent, if no arm is found, or if a compared entrant carries
    an unrecognised game-over reason.
    """

    outcomes = _load_reasons(jsonl_path)
    if baseline_entrant not in outcomes:
        raise ValueError(
            f"baseline entrant {baseline_entrant!r} not found in {jsonl_path} "
            f"(entrants: {', '.join(outcomes)})"
        )
    baseline = outcomes[baseline_entrant]
    if arm_entrants is None:
        arms = [name for name in outcomes if name.startswith(ARM_PREFIX)]
        if not arms:
            raise ValueError(
                f"no arm entrants matching {ARM_PREFIX!r}* in {jsonl_path} "
                f"(entrants: {', '.join(outcomes)})"
            )
    else:
        arms = list(arm_entrants)
        missing = [name for name in arms if name not in outcomes]
        if missing:
            raise ValueError(
                f"arm entrant(s) not found in {jsonl_path}: {', '.join(missing)} "
                f"(entrants: {', '.join(outcomes)})"
            )
    return [
        _pair_one_arm(name, outcomes[name], baseline_entrant, baseline) for name in arms
    ]


def _render_human(
    rows: Sequence[ArmPairedStats], *, jsonl_path: Path, baseline_entrant: str
) -> str:
    """Render the aligned per-arm table plus the Bonferroni honesty lines."""

    width = max([len("entrant"), *(len(row.entrant) for row in rows)])
    lines: list[str] = [
        f"Paired exact-McNemar vs baseline {baseline_entrant} over {jsonl_path}",
        "win = impostor win (IMPOSTOR_PARITY/IMPOSTOR_SABOTAGE); pairing key = seed",
        "",
        f"{'entrant':<{width}}  {'n':>3}  {'arm':>4}  {'base':>4}  {'delta':>8}"
        f"  {'b':>3}  {'c':>3}  {'p_exact':>8}  {'arm 95% Wilson':<18}"
        f"  baseline 95% Wilson",
    ]
    for row in rows:
        arm_ci = f"[{row.arm_wilson_low:.4f}, {row.arm_wilson_high:.4f}]"
        base_ci = f"[{row.baseline_wilson_low:.4f}, {row.baseline_wilson_high:.4f}]"
        lines.append(
            f"{row.entrant:<{width}}  {row.n:>3}  {row.arm_wins:>4}"
            f"  {row.baseline_wins:>4}  {row.delta:>+8.4f}  {row.b:>3}  {row.c:>3}"
            f"  {row.p_exact:>8.4f}  {arm_ci:<18}  {base_ci}"
        )

    family = len(rows)
    threshold = FAMILY_ALPHA / family
    clears = [row.entrant for row in rows if row.p_exact < threshold]
    fails = [row.entrant for row in rows if row.p_exact >= threshold]
    uncorrected = [row.entrant for row in rows if row.p_exact >= FAMILY_ALPHA]
    lines.extend(
        [
            "",
            f"Bonferroni over the {family}-arm family: "
            f"alpha = {FAMILY_ALPHA} / {family} = {threshold:.4f}.",
            f"  clears alpha: {', '.join(clears) if clears else '(none)'}",
            f"  fails alpha:  {', '.join(fails) if fails else '(none)'}",
        ]
    )
    if uncorrected:
        lines.append(
            f"  not significant even UNCORRECTED (p >= {FAMILY_ALPHA}): "
            f"{', '.join(uncorrected)}"
        )
    else:
        lines.append(f"  every arm is significant uncorrected (p < {FAMILY_ALPHA}).")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Recompute paired exact-binomial McNemar tests + Wilson 95% intervals "
            "for each learned-impostor arm against the FSM comparator baseline "
            "(Task 19.20). Pure, offline, stdlib arithmetic."
        ),
    )
    parser.add_argument(
        "results_jsonl",
        type=Path,
        help="finalist-eval JSONL (e.g. training/reports/results-finalist-eval.jsonl)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the per-arm ArmPairedStats rows as a JSON array instead of text",
    )
    parser.add_argument(
        "--baseline",
        default=DEFAULT_BASELINE,
        help=f"entrant to pair every arm against (default: {DEFAULT_BASELINE})",
    )
    args = parser.parse_args(argv)
    results_jsonl: Path = args.results_jsonl
    emit_json: bool = args.json
    baseline_entrant: str = args.baseline

    try:
        rows = compute_paired_stats(results_jsonl, baseline_entrant=baseline_entrant)
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if emit_json:
        print(json.dumps([row.model_dump() for row in rows], indent=2))
    else:
        print(
            _render_human(
                rows, jsonl_path=results_jsonl, baseline_entrant=baseline_entrant
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
