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
import math
import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pydantic import ValidationError, create_model  # noqa: E402

from training.coevo.driver import CoevoCampaignRow  # noqa: E402
from training.realpath_schema import RealPathRerankRow  # noqa: E402

#: The typed model for each supported ranking schema. ``-v2`` is the recorder's
#: own row type; ``-v1`` is that type with the two recorder-identity fields made
#: optional, because the frozen 18.24 corpus genuinely predates them (the
#: round-9 PARTIAL accept) and this generator reproduces that record rather than
#: backfilling it. Every OTHER field is checked identically on both.
_V1_ROW_MODEL = create_model(
    "RealPathRerankRowV1",
    __base__=RealPathRerankRow,
    recording_backend_sha256=(str | None, None),
    game_map_sha256=(str | None, None),
)

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
#: numbers. Emitted verbatim so the artifact carries its own definition. This is
#: the FROZEN sentence: it is a key of the committed
#: ``measurement-stability.json``, so its bytes are fixed by the reproduction
#: requirement. It is exactly true whenever ``(leg, genome)`` and
#: ``(leg, genome, label)`` partition the arms identically, which holds for the
#: entire committed corpus (verified: zero ``(leg, genome)`` pairs carry two
#: labels).
COMBINATION_RULE: Final[str] = (
    "each (leg, genome) pair is ONE ARM: a policy recorded in two different "
    "lineage legs contributes independent provider draws and is counted twice. "
    "An earlier revision keyed by genome sha alone, which silently discarded "
    "the duplicate arm and made the result depend on filesystem traversal order "
    "(6d327dcb was recorded in both run-01 and run-03 on both tranches)."
)

#: The clause appended when a set DOES carry one genome under two labels in a
#: single leg. The recorder emits such rankings deliberately (the 18.17
#: tie-break fixture), and the arm key has carried the label since round 6 — so
#: for those sets the frozen sentence above would understate the keying, and the
#: artifact would be computed under a rule it does not state (Codex review on
#: PR #314). Never reached by the committed corpus, so the frozen bytes stand.
COMBINATION_RULE_LABEL_CLAUSE: Final[str] = (
    " This set additionally records one genome under several labels within a "
    "single leg, so the arm key is the (leg, genome, LABEL) triple: two labels "
    "are two candidates and are counted separately."
)

#: The campaign-row schema this renderer reads. A stream declaring anything else
#: is refused rather than rendered from fields nobody has checked (Task 18.31).
CAMPAIGN_ROWS_SCHEMA: Final[str] = "coevo-campaign-v1"

#: The five ``TacticalPolicyStamp`` fields that together ARE a policy identity.
#: The resume predicate compares all five; an arm's two reads must too.
_STAMP_IDENTITY_FIELDS: Final[tuple[str, ...]] = (
    "policy_id",
    "method",
    "encoder_version",
    "weights_sha256",
    "anchor_policy",
)

#: The supply gauge whose tranche-to-tranche swing IS the noise measurement.
_NOISE_GAUGE: Final[str] = "flags_per_meeting"

#: The population-relative conversion gauge whose derived floor can SATURATE at
#: 1.000 — the maximum a fraction can reach, so such a floor demands a perfect
#: 100% conversion.
#:
#: NOT "impossible", despite the artifact key's name. ``evaluate_supply_floors``
#: clears a gauge on ``measured >= floor``, so a floor of exactly 1.0 is
#: attainable at perfection (Codex review on PR #314). The ``>=`` predicate and
#: the ``arms_with_impossible_conversion_floor`` key are retained because they
#: are what the FROZEN 18.24 artifact computed and published (§4.0: "12 of 22");
#: this generator reproduces that record byte-for-byte and does not get to
#: restate history. What it can fix is its own rendered claim, so the table now
#: says the floor saturated rather than that it was unpassable. The report's
#: own §4.0 wording is an erratum candidate — ``training/reports/`` is outside
#: this task's file scope.
_CONVERSION_GAUGE: Final[str] = "testimony_backed_conversion"
_SATURATED_FLOOR: Final[float] = 1.0

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
            # ``parse_constant`` is the ONLY hook that sees them: Python's
            # ``json.loads`` accepts the non-standard bare constants ``NaN``,
            # ``Infinity`` and ``-Infinity``, and pydantic's strict mode still
            # admits them for an unconstrained ``float`` field — so a row
            # carrying ``"champion_fitness": NaN`` rendered ``nan`` and exited 0,
            # and a non-finite ranking metric poisons every stability average it
            # enters (Codex review on PR #314). They are not JSON, and no
            # artifact this repository writes emits them.
            row = json.loads(line, parse_constant=_refuse_json_constant)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{number} is not valid JSON: {exc}") from exc
        except ValueError as exc:
            raise SystemExit(f"{path}:{number} {exc}") from exc
        if not isinstance(row, dict):
            raise SystemExit(f"{path}:{number} is not a JSON object")
        # The constant hook above is not sufficient on its own: a
        # STANDARDS-COMPLIANT numeric token such as ``1e400`` overflows to
        # ``inf`` inside the float conversion without ever reaching
        # ``parse_constant``, and strict pydantic still admits it for an
        # unconstrained float field (Codex review on PR #314). The two together
        # cover the literal spelling and the overflow; neither covers both.
        nonfinite = sorted(_nonfinite_paths(row))
        if nonfinite:
            raise SystemExit(
                f"{path}:{number} carries non-finite numbers at {nonfinite}; a "
                "measurement artifact holds finite values, and a non-finite one "
                "silently poisons every average and comparison it enters"
            )
        rows.append(row)
    if not rows:
        raise SystemExit(f"{path} holds no rows")
    return rows


def _refuse_json_constant(constant: str) -> float:
    """Refuse ``NaN`` / ``Infinity`` / ``-Infinity`` at the parse boundary."""

    raise ValueError(
        f"carries the non-standard JSON constant {constant}; a measurement "
        "artifact holds finite numbers, and a non-finite one silently poisons "
        "every average and comparison it enters"
    )


def _nonfinite_paths(value: Any, trail: str = "") -> list[str]:
    """Every dotted path in a decoded row whose value is a non-finite float."""

    if isinstance(value, float):
        return [] if math.isfinite(value) else [trail or "<root>"]
    if isinstance(value, dict):
        return [
            found
            for key, item in value.items()
            for found in _nonfinite_paths(item, f"{trail}.{key}" if trail else str(key))
        ]
    if isinstance(value, list):
        return [
            found
            for index, item in enumerate(value)
            for found in _nonfinite_paths(item, f"{trail}[{index}]")
        ]
    return []


def _file_identity(path: Path) -> tuple[int, int]:
    """``(st_dev, st_ino)`` — the same FILE under any number of names.

    A resolved path collapses symlink aliases but not HARD links: the same
    ranking bytes reachable as two names in two leg directories resolved to two
    distinct paths, so the fold counted them as two independent lineage legs and
    doubled ``arms_with_both_tranches`` (Codex review on PR #314). Filesystem
    identity is the question the seen-set was always asking.
    """

    stat = path.stat()
    return (stat.st_dev, stat.st_ino)


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

    # The SCHEMA, before any field is read. The leg reader has pinned its row
    # schema since round 9, but this renderer took the CLI's promise of
    # ``coevo-campaign-v1`` on trust and read the fields directly: a later
    # generation that keeps the names and changes the semantics would render an
    # authoritative-looking table that is simply wrong, which is the
    # transcription-error class this whole tool exists to remove (Codex review
    # on PR #314). Every row is checked, not just the first, so a concatenated
    # mixed-schema stream is refused rather than judged by its opening line.
    drifted = sorted(
        {
            str(row.get("schema_version"))
            for row in rows
            if row.get("schema_version") != CAMPAIGN_ROWS_SCHEMA
        }
    )
    if drifted:
        raise SystemExit(
            f"campaign rows declare schema_version {drifted}, but this renderer "
            f"reads {CAMPAIGN_ROWS_SCHEMA!r}. A later schema can keep these field "
            "names and change what they mean, so the table is refused rather "
            "than rendered from fields nobody has checked"
        )
    # And the field TYPES, through the driver's own row model. Declaring the
    # right schema says nothing about the values under it, and this renderer
    # read them straight: a corrupted ``"champion_updated": "false"`` — the
    # STRING — is truthy, so it rendered as ``yes`` and the run reported
    # success. A generator whose whole purpose is to remove transcription error
    # must not invent one (Codex review on PR #314).
    #
    # ``model_validate_json`` in STRICT mode, not ``model_validate``. Lax
    # validation coerces ``"false"`` to ``False`` and would have accepted the
    # corrupted row silently; strict validation over a dict is unusable here,
    # because a JSON array is not a ``tuple`` and every committed row fails. From
    # JSON the two are reconciled: arrays satisfy tuple fields, and a
    # string-for-bool is still refused. Verified against the committed corpus —
    # all 52 rows pass, and a wrong type in any field does not.
    for index, row in enumerate(rows, start=1):
        try:
            CoevoCampaignRow.model_validate_json(json.dumps(row), strict=True)
        except ValidationError as exc:
            raise SystemExit(
                f"campaign row {index} declares {CAMPAIGN_ROWS_SCHEMA} but does "
                f"not satisfy it: {exc}. The table is refused rather than "
                "rendered from values whose types were never checked"
            ) from exc
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
    # Each segment must run 1, 2, … consecutively. Without this a run that lost
    # its generation-1 row (or any missing / duplicated / reordered row) is
    # silently merged into the preceding segment, and the rendered counts, swap
    # totals and game totals come out plausible but wrong — the exact
    # transcription-error class this generator exists to remove (Codex review on
    # PR #314).
    for index, segment in enumerate(segments, start=1):
        actual = [row.get("generation_index") for row in segment]
        expected = list(range(1, len(segment) + 1))
        if actual != expected:
            raise SystemExit(
                f"segment {index} has generation indices {actual}, not the "
                f"consecutive {expected}; a row is missing, duplicated, or "
                "reordered — refusing to render a plausible-but-wrong table"
            )
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


#: The PROTOCOL a leg ran under — everything that defines the experiment except
#: which seeds it drew. Two reads of one genome are comparable only if all of
#: these agree: a swing across a changed roster, baseline, mode or budget
#: measures the change, not provider noise.
_LEG_PROTOCOL_FIELDS: Final[tuple[str, ...]] = (
    "num_players",
    "num_impostors",
    "tasks_per_crewmate",
    "baseline_id",
    "mode",
    "max_attempts",
    "max_ticks",
    "meeting_timeout_seconds",
)

#: WHO recorded a leg and on WHAT topology. Not on :data:`_LEG_PROTOCOL_FIELDS`
#: because the frozen 18.24 corpus predates them: ``realpath-rerank-v1`` rows
#: carry no recorder identity at all, and this generator reproduces that record
#: rather than fabricating history for it. Every ``-v2`` row carries both, and
#: for those the fields are protocol in the fullest sense — two tranche rankings
#: written into one leg directory by separate calls can otherwise use different
#: providers, prompt sets, custom runners or maps while agreeing on every field
#: above, and §4.0 would report that behavioural change as provider/seed noise
#: (Codex review on PR #314).
_RECORDER_IDENTITY_FIELDS: Final[tuple[str, ...]] = (
    "recording_backend_sha256",
    "game_map_sha256",
)

#: The row schemas that predate :data:`_RECORDER_IDENTITY_FIELDS`. A CLOSED set
#: — the only member is the frozen 18.24 corpus, and it will never grow, because
#: a schema that omits the recorder identity is not one this repository writes
#: any more. Every other version MUST carry the fields, so a future generation
#: that forgot them is refused rather than quietly treated as legacy. (Comparing
#: version STRINGS with ``>=`` would have done the opposite: ``"...-v10"`` sorts
#: below ``"...-v2"``, so the tenth schema would silently read as pre-18.31.)
_PRE_RECORDER_IDENTITY_SCHEMAS: Final[frozenset[str]] = frozenset(
    {"realpath-rerank-v1"}
)
_RECORDER_IDENTITY_SCHEMA: Final[str] = "realpath-rerank-v2"

#: The CREW-ARM schema (Task 18.32). Purely ADDITIVE over ``-v2``: the crew
#: read-back proof (``crew_stamp`` + its verified/uniform/digest twins) and the
#: frozen opponent's identity (``opponent_weights_sha256`` / ``opponent_stamp``).
#: Every ``-v2`` field keeps its meaning, which is what lets both versions be
#: validated by the recorder's own row model — the new fields are optional there,
#: so a ``-v2`` row satisfies it unchanged (the ``_V1_ROW_MODEL`` pattern, one
#: generation on).
_CREW_ARM_SCHEMA: Final[str] = "realpath-rerank-v3"

#: The FROZEN OPPONENT's identity, which a ``-v3`` leg shares across every row:
#: the opponent is installed for EVERY candidate in the leg, so two rows of one
#: ranking disagreeing on it means the file is not one leg. Absent (``None`` on
#: both) is the scripted-FSM comparator cell and agrees with itself.
_OPPONENT_IDENTITY_FIELDS: Final[tuple[str, ...]] = (
    "opponent_weights_sha256",
    "opponent_stamp",
)

#: Every ranking schema this generator knows how to READ. The membership test
#: above answers "does this file carry the recorder identity?", and answering it
#: with "anything that is not v1" made every unknown string — a future
#: ``-v3`` with re-specified fields, or a plain typo — read as current: the
#: generator would check the two identity fields exist and then interpret every
#: other field under v2 semantics, emitting authoritative tables from a schema
#: whose meanings it had never validated (Codex review on PR #314). A schema is
#: supported when it is named here, and refusing an unknown one costs a one-line
#: addition on the day a v3 is actually specified.
_SUPPORTED_RANKING_SCHEMAS: Final[frozenset[str]] = _PRE_RECORDER_IDENTITY_SCHEMAS | {
    _RECORDER_IDENTITY_SCHEMA,
    _CREW_ARM_SCHEMA,
}

#: The schemas that predate the crew arm. A ``crew_stamp`` on one of them is a
#: row wearing a field its declared schema does not define — refused rather than
#: read, for the same reason an unknown schema is: this generator would then be
#: interpreting fields it never validated. (The recorder cannot emit such a row;
#: a hand-assembled or half-migrated file can.)
_PRE_CREW_ARM_SCHEMAS: Final[frozenset[str]] = _PRE_RECORDER_IDENTITY_SCHEMAS | {
    _RECORDER_IDENTITY_SCHEMA
}

#: Every field the crew arm added. Present only on ``-v3``.
_CREW_ARM_FIELDS: Final[tuple[str, ...]] = (
    "crew_stamp",
    "crew_stamp_verified_games",
    "crew_stamp_uniform",
    "crew_stamp_equals_computed_digest",
    *_OPPONENT_IDENTITY_FIELDS,
)

#: The leg-level fields ONE ranking file's rows must agree on — the protocol,
#: the seed set (one ranking file is one tranche), the schema generation, and
#: the recorder identity when the schema carries it.
_LEG_LEVEL_FIELDS: Final[tuple[str, ...]] = (
    "seeds",
    "schema_version",
    *_LEG_PROTOCOL_FIELDS,
)


def _recorder_identity_fields(rows: Sequence[Mapping[str, Any]]) -> tuple[str, ...]:
    """The recorder-identity fields THIS file's schema generation carries.

    ``read_validated_ranking`` has already proven every row agrees on
    ``schema_version``, so rank 1 speaks for the file.
    """

    if not rows:
        return ()
    if str(rows[0]["schema_version"]) not in _PRE_RECORDER_IDENTITY_SCHEMAS:
        return _RECORDER_IDENTITY_FIELDS
    # A ``-v1`` file that nonetheless CARRIES the identity is compared on it.
    # Returning ``()`` for the whole schema meant those values were accepted and
    # never checked, so two v1 tranches naming different recorders produced a
    # clean stability artifact that reported a known provider/map change as
    # measurement noise (Codex review on PR #314). Absence stays a recorded fact
    # about the frozen corpus; PRESENCE is evidence, and evidence gets compared.
    return tuple(
        field
        for field in _RECORDER_IDENTITY_FIELDS
        if any(row.get(field) is not None for row in rows)
    )


def _candidate_stamp(row: Mapping[str, Any]) -> Mapping[str, Any]:
    """The stamp naming the CANDIDATE this row ranks.

    A ``-v3`` crew row (Task 18.32) carries two identities: ``crew_stamp`` is
    the candidate's, and ``stamp`` is the impostor side it was played against
    (the frozen opponent, or the scripted-FSM default when none was installed).
    Every other row carries one, in ``stamp``. Reading the candidate identity
    from the wrong slot would key a crew arm on its OPPONENT — which is
    leg-level and identical for every candidate in the leg, so the whole leg
    would collapse into one arm.
    """

    crew_stamp = row.get("crew_stamp")
    if isinstance(crew_stamp, dict):
        return crew_stamp
    stamp = row["stamp"]
    assert isinstance(stamp, dict)  # read_validated_ranking proves the shape
    return stamp


def _candidate_stamp_prefix(row: Mapping[str, Any]) -> str:
    """``"crew_"`` when this row's candidate identity is the crew stamp."""

    return "crew_" if isinstance(row.get("crew_stamp"), dict) else ""


def _stamp_proof(row: Mapping[str, Any]) -> str:
    """The 17.14 stamp-proof cell, rendered from the row's own proof fields.

    Rendered for the CANDIDATE's side: a crew row's proof lives in the
    ``crew_stamp_*`` twins, and rendering the impostor block there would report
    the FROZEN OPPONENT's read-back (or, in the comparator cell, zero games)
    as though it were the ranked policy's provenance.
    """

    prefix = _candidate_stamp_prefix(row)
    verified = row[f"{prefix}stamp_verified_games"]
    parts = [f"{verified}/{len(row['seeds'])} games stamped"]
    parts.append("uniform" if row[f"{prefix}stamp_uniform"] else "**NOT uniform**")
    parts.append(
        "sha == computed digest"
        if row[f"{prefix}stamp_equals_computed_digest"]
        else "**sha != computed digest**"
    )
    return ", ".join(parts)


def read_validated_ranking(ranking_path: Path) -> list[dict[str, Any]]:
    """Read one ranking file, refusing any file that is not ONE coherent leg.

    Shared by the leg renderer AND the stability fold. The stability path used
    to read rows directly, so a file with duplicated ranks or candidates — or
    rows recorded under mixed leg settings — could still produce an
    authoritative stability artifact as long as each genome had a matching read
    in the other tranche (Codex review on PR #314). The integrity of a ranking
    file is a property of the file, not of the table being rendered from it.

    Rows come back sorted by rank, having been checked for: a contiguous
    ``1..N`` rank sequence; no repeated ``weights_sha256`` or ``label``; and
    agreement across every leg-level field, since one ranking file is one
    tranche of one experiment.
    """

    rows = sorted(_read_jsonl(ranking_path), key=lambda row: row["rank"])
    # A leg file asserts a TOTAL ORDER over the leg's candidates. Sorting by
    # ``rank`` alone accepts a duplicated, concatenated or truncated file —
    # repeated positions, gaps, or one candidate appearing twice — and this
    # generator exists to remove exactly that class of hand-assembly error, not
    # to reproduce it faster.
    ranks = [row["rank"] for row in rows]
    if ranks != list(range(1, len(rows) + 1)):
        raise SystemExit(
            f"{ranking_path}: ranks are {ranks}, not a contiguous 1..{len(rows)} "
            "sequence; a leg table is one total order over the leg's candidates"
        )
    # LABELS are the candidate identity, not digests. The 18.17 re-rank recorder
    # (retired at Task 19.19) deliberately permitted one genome under two labels
    # — the 18.17 tie-break fixture — so rejecting a repeated ``weights_sha256``
    # here refused a
    # ranking the recorder legitimately emitted — this generator's own PR
    # contradicting itself (Codex review on PR #314).
    labels = [row["label"] for row in rows]
    duplicated = sorted({value for value in labels if labels.count(value) > 1})
    if duplicated:
        raise SystemExit(
            f"{ranking_path}: label {duplicated} appears more than once; "
            "each candidate holds exactly one rank in a leg"
        )
    for field in _LEG_LEVEL_FIELDS:
        values = {json.dumps(row[field], sort_keys=True) for row in rows}
        if len(values) != 1:
            raise SystemExit(
                f"{ranking_path}: rows disagree on the leg-level field {field!r} "
                f"({sorted(values)}); one leg table describes ONE experiment"
            )
    # The schema itself, now that every row is known to declare the same one.
    # This is the precondition for reading ANY other field: every check below
    # interprets the rows under this generator's understanding of the format, so
    # a schema it does not know is a file it must not render (Codex review on
    # PR #314).
    declared_schema = str(rows[0]["schema_version"])
    if declared_schema not in _SUPPORTED_RANKING_SCHEMAS:
        raise SystemExit(
            f"{ranking_path}: rows declare schema_version {declared_schema!r}, "
            f"which this generator does not support (known: "
            f"{sorted(_SUPPORTED_RANKING_SCHEMAS)}). An unrecognised schema is "
            "refused rather than read under the newest one's field meanings — "
            "regenerate the table with the matching generator, or teach this one "
            "the schema"
        )
    # A row may not wear a field its declared schema does not define. The crew
    # arm's fields are optional on the recorder's row model (that is what makes
    # them additive), so a ``-v2`` row carrying a ``crew_stamp`` validates
    # cleanly and would then be rendered as a crew arm by a file that claims to
    # predate the crew arm entirely — the same "read under field meanings nobody
    # checked" defect the unknown-schema refusal above exists to prevent.
    if declared_schema in _PRE_CREW_ARM_SCHEMAS:
        for row in rows:
            worn = sorted(field for field in _CREW_ARM_FIELDS if field in row)
            if worn:
                raise SystemExit(
                    f"{ranking_path}: rank {row['rank']} declares "
                    f"{declared_schema} but carries the crew-arm fields {worn}, "
                    f"which arrived with {_CREW_ARM_SCHEMA}; a row is read under "
                    "the schema it declares, so this file is refused rather than "
                    "rendered as a crew arm it does not claim to be"
                )
    else:
        # The FROZEN OPPONENT is leg protocol on a crew arm: it is installed for
        # every candidate in the leg, so rows disagreeing on it are not one leg.
        for field in _OPPONENT_IDENTITY_FIELDS:
            values = {json.dumps(row.get(field), sort_keys=True) for row in rows}
            if len(values) != 1:
                raise SystemExit(
                    f"{ranking_path}: rows disagree on the frozen opponent's "
                    f"{field!r} ({sorted(values)}); the opponent is installed for "
                    "EVERY candidate in a leg, so one ranking file names one"
                )
    # The recorder identity, once the schema generation says the rows carry it.
    # Keying on the row's OWN declared ``schema_version`` is what keeps this
    # honest for the frozen ``-v1`` corpus: absence is then a recorded fact
    # about a pre-18.31 record, not a silent omission that vouches for itself
    # (Codex review on PR #314).
    for field in _recorder_identity_fields(rows):
        values = {json.dumps(row.get(field), sort_keys=True) for row in rows}
        if len(values) != 1 or values == {"null"}:
            raise SystemExit(
                f"{ranking_path}: rows declare {rows[0]['schema_version']} but "
                f"disagree on (or omit) {field!r} ({sorted(values)}); from "
                f"{_RECORDER_IDENTITY_SCHEMA} on, a ranking row names the recorder "
                "that produced it"
            )
    # The stamp SHAPE, before anything compares stamps. The stability fold reads
    # identity fields with ``.get``, so a field absent from BOTH tranche rows
    # collapses to ``{None}`` and the arm passes as one policy read twice — a
    # missing stamp certifying its own agreement (Codex review on PR #314). And
    # a stamp whose ``weights_sha256`` names other bytes than the row it sits on
    # is a conflation of exactly the 17.14 kind, so bind the two here rather
    # than trusting the pair downstream.
    for row in rows:
        # EVERY stamp block the row carries — the impostor stamp, the crew twin
        # and the frozen opponent's — because each is an identity and a
        # malformed one is exactly as unreadable as a malformed ``stamp``.
        for key in ("stamp", "crew_stamp", "opponent_stamp"):
            stamp = row.get(key)
            if stamp is None and key != "stamp":
                continue
            if not isinstance(stamp, dict) or set(stamp) != set(_STAMP_IDENTITY_FIELDS):
                raise SystemExit(
                    f"{ranking_path}: rank {row['rank']} carries {key} {stamp!r}; a "
                    f"ranking row's stamp is EXACTLY the five fields "
                    f"{list(_STAMP_IDENTITY_FIELDS)}, which is what makes it an "
                    "identity"
                )
            nonstring = sorted(
                name for name, value in stamp.items() if not isinstance(value, str)
            )
            if nonstring:
                raise SystemExit(
                    f"{ranking_path}: rank {row['rank']} {key} fields {nonstring} "
                    "are not strings; every TacticalPolicyStamp field is a string"
                )
        # The CANDIDATE's stamp names the CANDIDATE's bytes. On a crew row that
        # is ``crew_stamp``; the ``stamp`` block there names the frozen opponent
        # (or the scripted FSM), whose digest is deliberately NOT this row's.
        candidate_stamp = _candidate_stamp(row)
        if candidate_stamp["weights_sha256"] != row["weights_sha256"]:
            raise SystemExit(
                f"{ranking_path}: rank {row['rank']} is recorded for "
                f"{row['weights_sha256']} but stamped "
                f"{candidate_stamp['weights_sha256']}; a stamp names the bytes it "
                "was frozen from (the 17.14 conflation guard)"
            )
        opponent_stamp = row.get("opponent_stamp")
        if isinstance(opponent_stamp, dict) and opponent_stamp[
            "weights_sha256"
        ] != row.get("opponent_weights_sha256"):
            raise SystemExit(
                f"{ranking_path}: rank {row['rank']} names frozen opponent "
                f"{row.get('opponent_weights_sha256')!r} but stamps "
                f"{opponent_stamp['weights_sha256']!r}; the opponent's stamp names "
                "the bytes it was frozen from too"
            )
    # The field TYPES, through the recorder's own row model. The structural
    # checks above are all about SHAPE — ranks, uniqueness, agreement — and none
    # of them looks at what a value is: `"referee_passed": "false"` is a non-empty
    # string, so the leg table printed PASS and the stability fold counted a
    # referee pass (Codex review on PR #314). This is the same defect the
    # campaign-row validator was added to prevent, one artifact family over, and
    # it gets the same treatment: JSON-strict, because lax coerces the string to
    # a bool and strict-over-dict rejects every committed row.
    model = (
        _V1_ROW_MODEL
        if declared_schema in _PRE_RECORDER_IDENTITY_SCHEMAS
        else RealPathRerankRow
    )
    for row in rows:
        try:
            model.model_validate_json(json.dumps(row), strict=True)
        except ValidationError as exc:
            raise SystemExit(
                f"{ranking_path}: rank {row.get('rank')!r} declares "
                f"{declared_schema} but does not satisfy it: {exc}. The table is "
                "refused rather than rendered from values whose types were never "
                "checked"
            ) from exc
    return rows


def render_leg_tables(ranking_path: Path) -> list[str]:
    """The candidate legend + ranking + floor-sensitivity tables for one tranche."""

    rows = read_validated_ranking(ranking_path)
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

    # The heading describes the LEG, so every row must agree on the leg-level
    # fields it quotes. Taking them from rank 1 alone would let a corrupted or
    # concatenated file render one authoritative-looking table whose heading
    # describes the first candidate while the metrics below came from another
    # experiment (Codex review on PR #314).
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
    """Every ``ranking-*.jsonl`` under the given roots, in sorted path order.

    The WHOLE set is sorted, not each root's walk: sorting per root would make
    the rendered bytes depend on the order the roots were typed, which is not
    determinism (Codex review on PR #314).
    """

    found: list[Path] = []
    for root in roots:
        if not root.is_dir():
            raise SystemExit(f"ranking root {root} is not a directory")
        found.extend(root.rglob("ranking-*.jsonl"))
    if not found:
        raise SystemExit(f"no ranking-*.jsonl files under {[str(r) for r in roots]}")
    return sorted(found)


def render_legs_document(ranking_paths: Sequence[Path]) -> str:
    """Every leg's tables, in sorted path order."""

    lines = ["## Real-path re-rank legs", ""]
    for path in ranking_paths:
        lines.extend(render_leg_tables(path))
    return "\n".join(lines).rstrip("\n") + "\n"


# --------------------------------------------------------------------------- #
# Family 3 — the §4.0 measurement-stability table.                             #
# --------------------------------------------------------------------------- #


def _tranche_identity(ranking_path: Path) -> tuple[str, frozenset[int]]:
    """A tranche's identity is its RECORDED SEEDS, not its filename (18.31).

    A filename suffix is a label an operator chose; the ``seeds`` on each row
    are the experiment. Two differently-named files over the SAME seeds are one
    provider draw counted twice — a false reliability result the stability
    table would present as a retest (Codex review on PR #314). Keying on the
    recorded seeds makes that collide into one tranche, where the duplicate
    check catches it. Rows within one file must agree on their seed set; the
    library writes one tranche per ranking file, so disagreement is corruption.
    """

    seed_sets = {
        tuple(sorted(row["seeds"])) for row in read_validated_ranking(ranking_path)
    }
    if len(seed_sets) != 1:
        raise SystemExit(
            f"{ranking_path} mixes seed sets {sorted(seed_sets)}; one ranking file "
            "is one tranche, and its rows all record the same seeds"
        )
    (seeds,) = seed_sets
    # CANONICAL (sorted): the seed SET is the experiment, so [1,2,3] and [3,2,1]
    # are one tranche recorded twice, not two independent draws (Codex review on
    # PR #314). Recording order is a detail of how the leg was invoked.
    # The identity string is LOSSY (negative seeds render as ``-3--2--1``, which
    # no split can invert), so the structured set is returned alongside it and
    # threaded through the fold rather than re-derived from the display form or
    # parked in module state (Codex review on PR #314).
    return "-".join(str(seed) for seed in seeds), frozenset(seeds)


@dataclass(frozen=True)
class _Arm:
    """One ``(leg, genome)`` arm's two tranche reads (the §4.0 combination rule)."""

    leg: str
    weights_sha256: str
    tranche_pair: tuple[str, str]
    first: Mapping[str, Any]
    second: Mapping[str, Any]


def _collect_arms(
    ranking_paths: Sequence[Path],
) -> tuple[dict[tuple[str, str, str], dict[str, Mapping[str, Any]]], list[_Arm]]:
    """Group ranking rows by ``(leg dir, genome sha)`` -> tranche -> row.

    The tranche key is the ranking file's own suffix, so two files in one leg
    dir are two independent provider draws of the same arm. A third read of one
    arm in one leg is not representable in a two-tranche stability check and
    fails loud rather than silently picking two of them.
    """

    by_arm: dict[tuple[str, str, str], dict[str, Mapping[str, Any]]] = {}
    tranche_seeds: dict[str, frozenset[int]] = {}
    label_genomes: dict[tuple[str, str], str] = {}
    # RESOLVED leg identity, and each ranking file counted once. The same tree
    # supplied through both its real path and a symlinked ``--ranking-root``
    # yields different LEXICAL parents for identical files, so the arms are
    # folded twice and every count doubles behind a valid-looking artifact
    # (Codex review on PR #314). Resolving the leg collapses the alias; the
    # seen-set drops a file offered twice under two spellings.
    # Keyed by FILESYSTEM IDENTITY, not resolved path: resolving collapses a
    # symlink alias but leaves two hard-linked names distinct, so identical bytes
    # offered under two names still manufactured a second lineage leg.
    seen_files: set[tuple[int, int]] = set()
    for path in ranking_paths:
        resolved = path.resolve()
        identity = _file_identity(resolved)
        if identity in seen_files:
            continue
        seen_files.add(identity)
        leg = resolved.parent.as_posix()
        tranche, seeds = _tranche_identity(path)
        tranche_seeds[tranche] = seeds
        for row in read_validated_ranking(path):
            # The LABEL rides the arm key: one genome under two labels is two
            # candidates, and collapsing them would pair the wrong reads.
            # A LABEL names one candidate within a leg. If two tranche files
            # reuse it for different genomes, the digest in the arm key turns
            # them into two unrelated ONE-tranche arms, both dropped by the
            # ``len(reads) < 2`` branch below — so the identity drift is
            # silently omitted from the table rather than reported, and the
            # result still succeeds on the other arms (Codex review on PR #314).
            label_key = (leg, row["label"])
            known = label_genomes.setdefault(label_key, row["weights_sha256"])
            if known != row["weights_sha256"]:
                raise SystemExit(
                    f"{path}: label {row['label']!r} names genome "
                    f"{row['weights_sha256']} here but {known} in another tranche "
                    f"of leg {leg}; a label is a candidate's identity within a "
                    "leg, so a label that moves between genomes is drift, not two "
                    "candidates"
                )
            key = (leg, row["weights_sha256"], row["label"])
            reads = by_arm.setdefault(key, {})
            if tranche in reads:
                raise SystemExit(
                    f"{path}: genome {row['weights_sha256']} appears twice in "
                    f"tranche {tranche} of one leg; an arm is one (leg, genome) "
                    "pair read once per tranche"
                )
            reads[tranche] = row
    arms: list[_Arm] = []
    for (leg, sha, label), reads in sorted(by_arm.items()):
        if len(reads) < 2:
            continue
        if len(reads) > 2:
            raise SystemExit(
                f"{leg}: genome {sha} was recorded on {sorted(reads)} — the "
                "stability check compares exactly two independent tranches; pass "
                "the two roots you mean to compare"
            )
        first_key, second_key = sorted(reads)
        # An arm is ONE policy read twice. Identical float bytes under two
        # different stamped families are two policies whose layouts happen to
        # collide — precisely the ambiguity the artifact stamps exist to remove
        # — so a swing between them measures nothing (Codex review on PR #314).
        # The COMPLETE five-field stamp is policy identity in this repository —
        # the resume predicate compares all five for exactly this reason. Two
        # reads agreeing only on the encoder family can still differ in
        # ``policy_id`` / ``method`` / ``anchor_policy``, and a swing between
        # two differently-stamped policies is not measurement noise (Codex
        # review on PR #314).
        for field in _STAMP_IDENTITY_FIELDS:
            # ``[field]``, not ``.get``: ``read_validated_ranking`` has already
            # proven the exact five-field shape, so an absent field can no
            # longer collapse to ``{None}`` and certify its own agreement.
            # The CANDIDATE's stamp (Task 18.32): on a crew arm the ``stamp``
            # block names the frozen opponent, which is leg-level and therefore
            # identical across every candidate — comparing it would certify
            # agreement about the opponent while the ranked policies differed.
            values = {
                _candidate_stamp(reads[key])[field] for key in (first_key, second_key)
            }
            if len(values) != 1:
                raise SystemExit(
                    f"{leg}: genome {sha} is stamped {field}={sorted(map(str, values))} "
                    "across its two tranches; the same bytes under two policy "
                    "identities are two policies, not one arm read twice"
                )
        # Same policy, same PROTOCOL. A swing is only provider/seed noise if
        # nothing else about the experiment moved: a changed roster, baseline,
        # mode or budget between the two reads makes the difference a measured
        # effect of that change, which this table would then report as
        # measurement instability (Codex review on PR #314).
        # The recorder identity is protocol too, and it is compared on the SAME
        # schema generation: an arm read once under ``-v1`` and once under
        # ``-v2`` is half-anonymous, so the pair is refused rather than
        # compared on the half that happens to be present. Within one
        # generation the fields are either both required (``-v2``) or both
        # absent by record (``-v1``) — never absent-and-therefore-agreeing
        # (Codex review on PR #314).
        for field in ("schema_version", *_LEG_PROTOCOL_FIELDS):
            values = {
                json.dumps(reads[key][field], sort_keys=True)
                for key in (first_key, second_key)
            }
            if len(values) != 1:
                raise SystemExit(
                    f"{leg}: genome {sha} was recorded under different {field} "
                    f"across tranches {first_key} and {second_key} "
                    f"({sorted(values)}); a stability swing compares one policy "
                    "under ONE protocol, twice"
                )
        for field in _recorder_identity_fields([reads[first_key]]):
            values = {
                json.dumps(reads[key][field], sort_keys=True)
                for key in (first_key, second_key)
            }
            if len(values) != 1:
                raise SystemExit(
                    f"{leg}: genome {sha} was recorded under different {field} "
                    f"across tranches {first_key} and {second_key} "
                    f"({sorted(values)}); a swing between two different recorders "
                    "or two different maps is a measured effect of that change, "
                    "not provider/seed noise"
                )
        # The FROZEN OPPONENT is protocol too (Task 18.32): a crew candidate
        # retested against a different impostor side is a measured effect of the
        # opponent change, not provider/seed noise. ``.get`` because a pre-``-v3``
        # pair carries neither field — and the pair already agrees on
        # ``schema_version``, so absence is never mixed with presence.
        for field in _OPPONENT_IDENTITY_FIELDS:
            values = {
                json.dumps(reads[key].get(field), sort_keys=True)
                for key in (first_key, second_key)
            }
            if len(values) != 1:
                raise SystemExit(
                    f"{leg}: genome {sha} was recorded against different {field} "
                    f"across tranches {first_key} and {second_key} "
                    f"({sorted(values)}); a swing between two different frozen "
                    "opponents measures the opponent, not the candidate"
                )
        arms.append(
            _Arm(
                leg=leg,
                weights_sha256=sha,
                tranche_pair=(first_key, second_key),
                first=reads[first_key],
                second=reads[second_key],
            )
        )
    # The emitted combination rule must describe the fold that actually ran.
    # :data:`COMBINATION_RULE` says each ``(leg, genome)`` pair is ONE arm, but
    # since round 6 the key also carries the LABEL — because the recorder
    # legitimately emits one genome under two labels, and refusing such a set
    # was itself a round-6 finding. On a set where labels DISCRIMINATE, the
    # frozen sentence is therefore false about its own artifact (Codex review on
    # PR #314).
    #
    # Refusing is not available: it would re-break the round-6 finding by
    # rejecting a ranking this PR's own recorder emits. Rewriting the frozen
    # sentence is not available either: it is a key of the committed
    # ``measurement-stability.json`` this generator reproduces byte-for-byte,
    # and ``training/artifacts/`` is read-only fixture here. So the artifact
    # self-describes ACCURATELY in both cases: when the two keyings partition
    # identically — which they do for the whole committed corpus, verified — the
    # frozen sentence is exactly true and is emitted unchanged; when they do
    # not, the label clause is emitted alongside it.
    # ONE global tranche pair, not merely two reads per arm: a set where arm A
    # was read on (t1, t2) and arm B on (t2, t3) yields an aggregate that mixes
    # different comparisons while the table presents it as a single two-tranche
    # measurement (Codex review on PR #314).
    tranche_pairs = sorted({arm.tranche_pair for arm in arms})
    if len(tranche_pairs) > 1:
        raise SystemExit(
            f"the arms do not share ONE tranche pair ({tranche_pairs}); a "
            "stability table compares the SAME two tranches for every arm — "
            "pass the roots (or the two tranches) you mean to compare"
        )
    # DISJOINT, not merely distinct. Canonicalising on the seed set makes
    # (1,2,3) and (3,4,5) two identities, but they share seed 3: that game is
    # then counted on BOTH sides of every swing, so a shared-seed pair reports
    # agreement it did not independently observe. Two tranches are two
    # independent draws or they are not a retest (Codex review on PR #314).
    if tranche_pairs:
        ((first_key, second_key),) = tranche_pairs
        overlap = sorted(tranche_seeds[first_key] & tranche_seeds[second_key])
        if overlap:
            raise SystemExit(
                f"tranches {first_key} and {second_key} share seeds {overlap}; a "
                "stability swing compares two INDEPENDENT draws, and a shared "
                "seed is the same game counted on both sides"
            )
        # The pair is chosen from the PAIRED arms, so a third tranche carrying
        # only single-read arms is invisible to the check above — and the
        # ``referee_passes_total`` fold walks all of ``by_arm``, so its PASS
        # counts could come from a tranche absent from every swing in the table
        # (Codex review on PR #314). Single-read arms from the compared pair are
        # legitimate and still counted; a read from anywhere else is not part of
        # this experiment.
        pair = {first_key, second_key}
        foreign = sorted(
            {tranche for reads in by_arm.values() for tranche in reads} - pair
        )
        if foreign:
            raise SystemExit(
                f"the ranking set carries tranche(s) {foreign} outside the "
                f"compared pair ({first_key}, {second_key}); their rows would "
                "enter the totals while appearing in no swing — pass only the "
                "roots for the two tranches you mean to compare"
            )
    return by_arm, arms


def _combination_rule(by_arm: Mapping[tuple[str, str, str], object]) -> str:
    """The combination rule THIS artifact was actually computed under (18.31).

    :data:`COMBINATION_RULE` says each ``(leg, genome)`` pair is one arm, but
    since round 6 the key also carries the LABEL — because the recorder
    legitimately emits one genome under two labels, and refusing such a set was
    itself a round-6 finding. On a set where labels DISCRIMINATE, the frozen
    sentence understates the keying and the artifact would be computed under a
    rule it does not state (Codex review on PR #314).

    Neither obvious remedy is available. Refusing would re-break the round-6
    finding by rejecting a ranking this PR's own recorder emits. Rewriting the
    frozen sentence would break the byte reproduction of the committed
    ``measurement-stability.json``, of which it is a key, and
    ``training/artifacts/`` is read-only fixture to this task. So the artifact
    self-describes accurately in BOTH cases: where the two keyings partition
    identically the frozen sentence is exactly true and is emitted unchanged —
    which is every arm of the committed corpus, verified — and where they do not,
    the label clause is appended.
    """

    labels_per_genome: dict[tuple[str, str], set[str]] = {}
    for leg, sha, label in by_arm:
        labels_per_genome.setdefault((leg, sha), set()).add(label)
    if any(len(labels) > 1 for labels in labels_per_genome.values()):
        return COMBINATION_RULE + COMBINATION_RULE_LABEL_CLAUSE
    return COMBINATION_RULE


def compute_stability(ranking_paths: Sequence[Path]) -> dict[str, Any]:
    """The §4.0 stability numbers over any two-tranche ranking set.

    Every quantity is a pure fold over the committed rows: the mean absolute
    tranche-to-tranche swing in ``flags_per_meeting``, that swing as a fraction
    of the floor the gauge is tested against, how many arms faced a
    structurally unpassable (``>= 1.000``) conversion floor on at least one
    tranche, the mean absolute win-rate swing in games, how many arms swung a
    full game, and the referee PASS / retested / replicated census.

    Three preconditions are ENFORCED rather than assumed, because violating any
    of them yields a number that reads like a two-tranche measurement and is
    not one: every arm shares ONE tranche pair, every arm's two tranches carry
    the same game count, and that game count is the same across the whole set.
    The ``mean_abs_win_swing_games_of_3`` key name records the 18.24
    denominator (the committed artifact's schema, kept so the reproduction is
    byte-exact); the uniformity check is what guarantees a run's denominator is
    single and knowable, and the rendered table's row label states the unit
    without hard-coding it.
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
    games_per_tranche: set[int] = set()
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
            floor is not None and floor >= _SATURATED_FLOOR
            for floor in conversion_floors
        ):
            impossible += 1
        # A win swing is reported IN GAMES, so the two tranches must share a
        # denominator: subtracting raw win counts across unequal game totals
        # would read identical 50% rates over 2 and 4 games as a one-game swing
        # (Codex review on PR #314).
        games = [read["core_games_total"] for read in reads]
        if games[0] != games[1]:
            raise SystemExit(
                f"{arm.leg}: genome {arm.weights_sha256} was recorded over "
                f"{games[0]} and {games[1]} games on its two tranches; a win "
                "swing in GAMES needs one denominator — re-record the short "
                "tranche or compare tranches of equal size"
            )
        games_per_tranche.add(games[0])
        wins = [
            read["core_impostor_win_rate"] * read["core_games_total"] for read in reads
        ]
        swing = abs(wins[0] - wins[1])
        win_swings.append(swing)
        if swing >= _ONE_GAME:
            swinging += 1

    if len(games_per_tranche) > 1:
        raise SystemExit(
            f"the arms were recorded over {sorted(games_per_tranche)} games per "
            "tranche; a mean win swing IN GAMES needs one denominator across the "
            "whole set — compare tranches of equal size"
        )
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
        "combination_rule": _combination_rule(by_arm),
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
            "arms whose derived conversion floor saturated at 1.000 (a perfect "
            "100% conversion required) on ≥1 tranche",
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


def _emit(text: str, out: Path | None, *, inputs: Sequence[Path] = ()) -> None:
    """Write ``text`` to ``out`` (or stdout), never over an artifact it READ.

    This generator is read-only history to ``training/artifacts/`` and
    ``training/reports/`` — the module docstring says so — but nothing enforced
    it: ``rows --out`` naming its own ``--rows-path``, ``legs --out`` naming one
    of its ranking files, or a stability output naming an input ranking would
    render the source and then overwrite that committed JSON/JSONL evidence
    with Markdown, returning 0 (Codex review on PR #314). A tool whose whole
    premise is reproducing committed bytes must not be able to destroy them.
    """

    if out is None:
        sys.stdout.write(text)
        return
    aliased = sorted(
        {source.as_posix() for source in inputs if _same_file(source, out)}
    )
    if aliased:
        raise SystemExit(
            f"refusing to write {out}: it is an INPUT this render just read "
            f"({aliased}). This generator reproduces committed artifacts and "
            "never overwrites them — point --out at a separate path."
        )
    _refuse_output_under_frozen_root(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")


#: The roots this generator treats as read-only history. Stated as data because
#: the module docstring and :func:`_emit` both make the claim in prose, and a
#: claim nothing enforces is the defect round 12 filed against this same tool.
FROZEN_EVIDENCE_ROOTS: Final[tuple[Path, ...]] = (
    Path("training/artifacts"),
    Path("training/reports"),
)


def _refuse_output_under_frozen_root(out: Path) -> None:
    """Refuse an output ANYWHERE under the frozen evidence roots (Task 18.31).

    The round-12 alias check protects only the files THIS invocation read, so
    ``rows --out training/artifacts/coevo/measurement-stability.json`` — an
    artifact this render never opened — overwrote committed evidence and
    returned 0 (Codex review on PR #314). Containment is the real rule: the task
    contract makes ``training/artifacts/coevo/`` a frozen record this PR
    reproduces byte-for-byte, and both the module docstring and :func:`_emit`
    already claim the same for the report root. Enforcing the claim the code
    makes is not a new policy; leaving it unenforced was the bug.

    Resolved before comparison, so ``..`` segments and symlinks cannot walk back
    into a protected root. Rendering INTO the repo is otherwise unaffected —
    only these two subtrees are refused.
    """

    # ``_resolve`` first, not a bare ``.resolve()``: every CLI path already goes
    # through it (a relative path is repo-root-relative here, not CWD-relative),
    # and re-applying it means this guard does not depend on each caller having
    # remembered to.
    # A HARD LINK defeats containment by construction: a second name outside the
    # frozen roots shares the frozen file's inode, so the resolved path is
    # legitimately outside and ``write_text`` truncates the shared data anyway
    # (Codex review on PR #314). Resolution answers "where is this name?", and
    # that is the wrong question for a link that has no separate bytes to
    # protect. Any existing multiply-linked output is refused: this generator
    # writes fresh renders, so a target already sharing its inode with something
    # else is never a path it should truncate.
    target = _resolve(out)
    try:
        links = target.stat().st_nlink if target.is_file() else 1
    except OSError:  # pragma: no cover - unstattable path fails at write
        links = 1
    if links > 1:
        raise SystemExit(
            f"refusing to write {out}: it is a hard link ({links} names share "
            "its inode), so writing it would truncate whatever else points at "
            "those bytes — including a frozen artifact this containment check "
            "cannot see through the link. Render to a fresh path."
        )
    resolved = target.resolve()
    for root in FROZEN_EVIDENCE_ROOTS:
        frozen = (_REPO_ROOT / root).resolve()
        if resolved == frozen or resolved.is_relative_to(frozen):
            raise SystemExit(
                f"refusing to write {out}: it is inside {root.as_posix()}/, which "
                "this generator treats as read-only history — it reproduces those "
                "committed bytes and never writes them. Render to a path outside "
                f"{'/, '.join(r.as_posix() for r in FROZEN_EVIDENCE_ROOTS)}/ and "
                "copy deliberately if the record really is meant to change."
            )


def _same_file(left: Path, right: Path) -> bool:
    """True iff two paths name one file, resolving links and ``..`` segments.

    ``Path.samefile`` needs both to exist; an output that does not exist yet is
    the normal case, so fall back to comparing fully-resolved paths.
    """

    try:
        if left.exists() and right.exists():
            return left.samefile(right)
    except OSError:  # pragma: no cover - unreadable path is not an alias
        return False
    return left.resolve() == right.resolve()


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
    # Two DIFFERENT artifacts are requested, so they need two paths. Pointing
    # both at one file emitted the JSON and then immediately overwrote it with
    # the Markdown, returning success while silently discarding one of the two
    # things the operator asked for (Codex review on PR #314). Compared after
    # ``_resolve`` so ``./x.json`` and ``x.json`` are recognised as one file.
    if args.out is not None and args.json_out is not None:
        rendered, machine = _resolve(Path(args.out)), _resolve(Path(args.json_out))
        # ``_same_file``, not ``==``: two different path STRINGS can resolve to
        # one file through a symlink or hard link, and the round-11 equality
        # check missed exactly that (Codex review on PR #314). The helper the
        # round-12 input/output guard already uses handles both.
        if _same_file(rendered, machine):
            raise SystemExit(
                f"--out and --json-out both name {rendered}; they emit different "
                "artifacts (Markdown and JSON), so one would overwrite the other. "
                "Give them separate paths."
            )
    ranking_files = find_ranking_files(roots)
    stability = compute_stability(ranking_files)
    if args.check is not None:
        committed_path = _resolve(Path(args.check))
        # read_BYTES, not read_text: text mode applies universal-newline
        # translation, so a CRLF or mixed-ending artifact decodes equal to the
        # generator's LF-only string while its bytes differ — and `--json-out`
        # would then rewrite the file this check just called reproducible,
        # defeating the very invariant round 4 added (Codex review on PR #314).
        committed_raw = committed_path.read_bytes()
        generated_raw = stability_json(stability).encode("utf-8")
        # BYTES, not decoded values. ``--json-out`` over this same artifact must
        # be a no-op diff, and a value-only comparison passes through key
        # reordering, indent/newline drift and numeric respelling (1 vs 1.0) —
        # so the check would go on reporting "reproduces exactly" while
        # regenerating the file changed it (Codex review on PR #314). The
        # decoded diff is still printed, because it names WHICH number moved
        # when the mismatch is semantic rather than formatting.
        if generated_raw != committed_raw:
            committed = json.loads(committed_raw)
            drift = sorted(
                key
                for key in set(stability) | set(committed)
                if stability.get(key) != committed.get(key)
            )
            for key in drift:
                sys.stderr.write(
                    f"{key}: computed {stability.get(key)!r} != committed "
                    f"{committed.get(key)!r}\n"
                )
            if not drift:
                sys.stderr.write(
                    "every value matches, but the committed BYTES differ "
                    "(key order, indentation, or trailing newline); regenerate "
                    "with --json-out so the artifact is what this generator emits\n"
                )
            sys.stderr.write(
                f"{committed_path} does not reproduce from {[str(r) for r in roots]}\n"
            )
            return 1
        sys.stdout.write(
            f"{committed_path.as_posix()} reproduces exactly, byte for byte "
            f"({stability['arms_with_both_tranches']} arms, "
            f"{stability['distinct_genomes']} distinct genomes).\n"
        )
        return 0
    if args.json_out is not None:
        _emit(
            stability_json(stability),
            _resolve(Path(args.json_out)),
            inputs=ranking_files,
        )
    _emit(
        render_stability_table(stability),
        None if args.out is None else _resolve(Path(args.out)),
        inputs=ranking_files,
    )
    return 0


def _run_rows(args: argparse.Namespace) -> int:
    rows_path = _resolve(Path(args.rows_path))
    document = render_rows_document(rows_path, labels=args.label or [])
    _emit(
        document,
        None if args.out is None else _resolve(Path(args.out)),
        inputs=[rows_path],
    )
    return 0


def _run_legs(args: argparse.Namespace) -> int:
    if args.ranking:
        # Sorted for the same reason find_ranking_files sorts: argument order
        # must not change the rendered bytes.
        paths = sorted(_resolve(Path(entry)) for entry in args.ranking)
    else:
        paths = find_ranking_files([_resolve(Path(args.leg_dir))])
    document = render_legs_document(paths)
    _emit(
        document,
        None if args.out is None else _resolve(Path(args.out)),
        inputs=paths,
    )
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
