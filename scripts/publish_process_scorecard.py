#!/usr/bin/env python3
"""Publish the nine-row process scorecard over the committed recordings.

Writes ``docs/process-scorecard.md`` and ``docs/process-scorecard.json`` from
:func:`eval.process_scorecard.compute_process_scorecard` — a fold over bytes
already in the tree with **zero model calls**. ``--check`` recomputes both and
exits 1 on drift, in the remediation shape
``scripts/build_sample_report.py::check_report`` uses: it names the stale file
and the exact command that regenerates it.

Destinations are pre-flighted through
``scripts/_report_output.py`` before anything is computed, exactly as
``scripts/measure_reasoning_evidence.py`` does, with every ``replays/**`` path,
the recording ROOTS themselves AND the fifth run's archive declared as protected
inputs — so this writer cannot be aimed at a recording directory, however it is
invoked and whether or not the destination exists yet.

Usage::

    python scripts/publish_process_scorecard.py
    python scripts/publish_process_scorecard.py --check
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _report_output import atomic_write_report, preflight_report_output  # noqa: E402
from eval.process_scorecard import (  # noqa: E402
    COMMITTED_SETS,
    FIFTH_RUN_ARCHIVE,
    RECORDINGS_ROOT,
    ProcessScorecard,
    RateCell,
    SetScorecard,
    compute_process_scorecard,
    scorecard_source_paths,
    serialize_scorecard,
)

MARKDOWN_PATH = Path("docs/process-scorecard.md")
JSON_PATH = Path("docs/process-scorecard.json")

#: The one command a reader — or a red ``--check`` — is told to run.
REGENERATE_COMMAND = "uv run python scripts/publish_process_scorecard.py"


def protected_inputs(root: Path) -> list[Path]:
    """Every recording location this command must never be able to write into.

    Two halves, because neither contains a writer alone. The FILES are
    ``replays/**`` in full (not only ``*.jsonl``: a roster, a manifest and a
    committed report live beside the recordings and are equally inputs) plus
    every byte the fold reads: they refuse an alias of an existing recording,
    including a HARD LINK placed outside the recording tree, which resolves to
    its own path and is caught only by ``_check_destination``'s ``samefile``
    probe against the recording itself. The DIRECTORIES are the recording roots
    themselves — ``replays/``, each committed set and the fifth run's archive —
    which is what refuses a destination that does not exist YET:
    ``_report_output._check_destination`` asks whether a protected path is among
    the destination's parents, so a root on the list refuses everything beneath
    it, created or not. Without them a destination like
    ``replays/samples/9p2i/new-scorecard.md`` matched no protected file and this
    writer would have created a new file inside a recording set.
    """

    directories = {
        root / name
        for name in (RECORDINGS_ROOT, *COMMITTED_SETS, FIFTH_RUN_ARCHIVE)
        if (root / name).is_dir()
    }
    return [
        *sorted(directories),
        *(path for path in root.glob(f"{RECORDINGS_ROOT}/**/*") if path.is_file()),
        *scorecard_source_paths(root),
    ]


def _rate(cell: RateCell) -> str:
    """``numerator/denominator = rate`` with the not-evaluable count beside it."""

    rate = "n/a" if cell.rate is None else f"{cell.rate:.4f}"
    suffix = f" (not evaluable {cell.not_evaluable})" if cell.not_evaluable else ""
    return f"{cell.numerator}/{cell.denominator} = {rate}{suffix}"


def _pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def _set_section(card: SetScorecard) -> list[str]:
    """One group's nine rows, in the order the direction memo's section 8 lists."""

    argmax = card.argmax_independence
    manufactured = card.manufactured_contradiction
    unexplained = card.unexplained_decision
    mix = card.evidence_quality_mix
    faith = card.rationale_faithfulness
    authored = card.agent_authored_share
    lines = [
        f"### {card.label}",
        "",
        f"{card.games} games, {card.meetings} meetings, {card.ballots} ballots "
        f"({card.eject_ballots} EJECT, {card.skip_ballots} SKIP). Sources: "
        + ", ".join(f"`{source}`" for source in card.sources)
        + ".",
        "",
        "| # | row | value |",
        "| --- | --- | --- |",
        f"| 1 | grounded-decision rate, EJECT | {_rate(card.grounded_eject)} |",
        f"| 1 | grounded-decision rate, SKIP | {_rate(card.grounded_skip)} |",
        f"| 1 | grounded-decision rate, all ballots | {_rate(card.grounded_all)} |",
        f"| 2 | argmax-independence: deviating EJECTs | "
        f"{argmax.deviators}/{argmax.unambiguous_ballots} = "
        f"{_pct(argmax.deviator_share)} |",
        f"| 2 | argmax-independence: role-correct, followers vs deviators | "
        f"{argmax.follower_role_correct}/{argmax.followers} = "
        f"{_pct(argmax.follower_role_correct_share)} vs "
        f"{argmax.deviator_role_correct}/{argmax.deviators} = "
        f"{_pct(argmax.deviator_role_correct_share)} (chance "
        f"{_pct(argmax.chance_baseline)}) |",
        f"| 3 | manufactured-contradiction rate | {_rate(manufactured.flags)} |",
        f"| 4 | unexplained-decision rate | {_rate(unexplained.decisions)} |",
        "| 5 | evidence-quality mix | "
        + ", ".join(
            f"{band} {count}" for band, count in sorted(mix.band_counts.items())
        )
        + f" over {mix.ejections} ejections |",
        f"| 6 | rationale faithfulness (TOKENS) | {_rate(faith.ballots)} |",
        f"| 7 | agent-authored share | {_rate(authored.ballots)} |",
        f"| 8 | wrong-but-believable rate | {_rate(card.wrong_but_believable)} "
        f"— {card.wrong_but_believable_label} |",
        f"| 9 | role-correct ejection rate | {_rate(card.role_correct_ejection)} "
        f"— {card.role_correct_ejection_label} |",
        "",
        "Row 2 detail: followers "
        f"{argmax.followers}, deviators {argmax.deviators}, ties excluded "
        f"{argmax.ties_excluded}, no rendered row inside the valid-target list "
        f"{argmax.no_rendered_row}. In meetings where the engine minted no "
        "contradiction at all, role-correct: followers "
        f"{argmax.zero_flag_follower_role_correct}/{argmax.zero_flag_followers}, "
        f"deviators {argmax.zero_flag_deviator_role_correct}/"
        f"{argmax.zero_flag_deviators}.",
        "",
        "Row 3 detail: manufactured flags contradicting an account the engine "
        "route makes true at EVERY tick, "
        f"{manufactured.manufactured_on_a_wholly_true_claim} of "
        f"{manufactured.flags.numerator}; the rest are the span-envelope "
        "artifact proper.",
        "",
        "Row 3 claim census: "
        f"{manufactured.self_alibi_claims} self-alibi claims "
        f"({manufactured.self_alibi_claims_multi_tick} spanning more than one "
        f"tick), {manufactured.self_alibi_claims_envelope_false} false under the "
        f"envelope test of which "
        f"{manufactured.self_alibi_claims_envelope_false_multi_tick} are "
        f"multi-tick, {manufactured.self_alibi_claims_strict_false} false under "
        "the strict test (in that room at NO tick the claim covers), "
        f"{manufactured.self_alibi_claims_unresolvable} unresolvable, and "
        f"{manufactured.other_subject_alibi_claims} further alibi claims name "
        "another player and are out of the census.",
        "",
        "Row 4 detail: EJECT ballots whose citation does not resolve, "
        f"{unexplained.uncited_ejects}; SKIP ballots naming no player at all, "
        f"{unexplained.skips_naming_no_player} "
        f"({unexplained.skips_with_considered_alternatives} SKIPs carry "
        f"considered_alternatives and {unexplained.skips_naming_a_player_in_prose} "
        "name a player in prose).",
        "",
        "Row 5 detail (role-correct beside each band, gating nothing): "
        + ", ".join(
            f"{band} {mix.band_role_correct.get(band, 0)}/{count}"
            for band, count in sorted(mix.band_counts.items())
        )
        + ".",
        "",
        "Row 6 detail: "
        f"{faith.tokens_absent} of {faith.tokens_checked} extracted tokens are "
        "absent from what the voter held.",
        "",
        "Row 7 detail: typed guard rewrites "
        + (
            ", ".join(
                f"{reason} {count}"
                for reason, count in sorted(authored.rewrite_reasons.items())
            )
            or "none"
        )
        + f"; {authored.marker_unwound_without_typed_reason} unwound from a marker "
        "with no typed reason; "
        f"{authored.citation_nulled_target_intact} citation nulled, target "
        f"intact; redirect-marker census {authored.redirect_marker_ballots} "
        f"({authored.redirect_marker_eject_ballots} EJECT, "
        f"{authored.redirect_marker_coerced_skip_ballots} coerced SKIP).",
        "",
        "Context: impostor alibis "
        f"{card.context.impostor_alibis_survived}/{card.context.impostor_alibis} "
        "survived contradiction detection; reporter slots "
        f"{card.context.reporter_ejections}/{card.context.reporter_slots} ejected "
        "against innocent non-reporter slots "
        f"{card.context.innocent_non_reporter_ejections}/"
        f"{card.context.innocent_non_reporter_slots}.",
        "",
    ]
    return lines


def render_markdown(scorecard: ProcessScorecard) -> str:
    """The published page: the demotion first, the nine rows, then the appendix."""

    lines = [
        "# The process scorecard",
        "",
        f"**{scorecard.role_correctness_note}**",
        "",
        "Nine measures of whether a decision rested on data the agent actually "
        "held, computed with **zero model calls** from recordings already in the "
        "tree. The suite is "
        "[the direction of 2026-09-19](../tasks/direction-2026-09-19-process-over-outcome.md) "
        "section 8; the card that publishes it is "
        "[the process scorecard card](../tasks/work/process-scorecard.md). Every "
        "row's definition — numerator, denominator, non-coverage — is published "
        "beside the number here and as typed keys in "
        "[`process-scorecard.json`](process-scorecard.json).",
        "",
        "This page is GENERATED. Do not edit it by hand: run "
        f"`{REGENERATE_COMMAND}` and commit the result. "
        f"`{REGENERATE_COMMAND} --check` recomputes both files from the "
        "recordings and fails on drift.",
        "",
        "## Why rows 2 and 3 are the point",
        "",
        "Without **argmax-independence** the headline certifies an arithmetic "
        "aggregator as a reasoner: on the shipped corpus most crew EJECT ballots "
        "simply name the voter's own rendered suspicion argmax, and every "
        "departing ballot still carries a valid citation — so a "
        '"cited and on-target" measure scores the two alike. Without the '
        "**manufactured-contradiction rate** it certifies the seed-41 failure: "
        "the alibi schema compresses a truthfully-moving player into a "
        "single-room envelope, the detectors flag the envelope, and a "
        "right-looking process convicts an innocent on evidence the schema "
        "invented.",
        "",
        "## Recording provenance",
        "",
        "These four sets are one era — baseline 9, recorded after the substrate "
        "wave (the route claim, the grounded SKIP with its labelling guards, and "
        "the weighing channel) by "
        "[the process re-record](../audits/audit-2026-09-22-process-rerecord.md). "
        "They are labelled, never averaged across a boundary: the column on the "
        "recordings made before that wave is committed in that record's section "
        "1, the SKIP row read 0 there by instruction, and row 3's claims became "
        "routes across the same line, so no row pools with that column.",
        "",
    ]
    lines.extend(f"* `{source}`" for source in scorecard.recording_provenance)
    lines.extend(
        [
            "",
            f"Report format version {scorecard.report_format_version}; scorecard "
            f"schema version {scorecard.schema_version}; decision date "
            f"{scorecard.decision_date}.",
            "",
            "## Pooled",
            "",
        ]
    )
    lines.extend(_set_section(scorecard.pooled))
    lines.extend(_set_section(scorecard.pooled_9p2i))
    lines.extend(["## Per set", ""])
    for card in scorecard.sets:
        lines.extend(_set_section(card))
    lines.extend(["## Row definitions", ""])
    for name, definition in scorecard.row_definitions.items():
        lines.extend([f"**{name}.** {definition}", ""])
    appendix = scorecard.appendix
    lines.extend(
        [
            f"## {appendix.label}",
            "",
            appendix.note,
            "",
            f"Archive: `{appendix.archive}` (read, never written).",
            "",
            "| arm | recordings | meetings | EJECT | EJECT cited | SKIP | SKIP cited |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    lines.extend(
        f"| {arm.arm} | {arm.recordings} | {arm.meetings} | {arm.eject_ballots} | "
        f"{arm.eject_ballots_cited} | {arm.skip_ballots} | {arm.skip_ballots_cited} |"
        for arm in appendix.arms
    )
    lines.extend(
        [
            "",
            "Ballots per meeting: "
            + ", ".join(
                f"{size} ballots in {count} meetings"
                for size, count in sorted(appendix.ballots_per_meeting.items())
            )
            + ".",
            "",
            f"{scorecard.no_consumer_note}",
            "",
        ]
    )
    return "\n".join(lines)


def publish(root: Path) -> ProcessScorecard:
    """Compute the fold and replace both published files atomically."""

    protected = protected_inputs(root)
    markdown_path = root / MARKDOWN_PATH
    json_path = root / JSON_PATH
    preflight_report_output(markdown_path, protected)
    preflight_report_output(json_path, protected)
    scorecard = compute_process_scorecard(root)
    atomic_write_report(markdown_path, render_markdown(scorecard))
    atomic_write_report(json_path, serialize_scorecard(scorecard))
    return scorecard


def check_report(root: Path) -> int:
    """Recompute both files and diff; 0 when consistent, 1 on drift or absence."""

    stale: list[str] = []
    markdown_path = root / MARKDOWN_PATH
    json_path = root / JSON_PATH
    for path in (markdown_path, json_path):
        if not path.exists():
            print(f"--check: no committed scorecard at {path}")
            return 1
    scorecard = compute_process_scorecard(root)
    if markdown_path.read_text(encoding="utf-8") != render_markdown(scorecard):
        stale.append(str(MARKDOWN_PATH))
    if json_path.read_text(encoding="utf-8") != serialize_scorecard(scorecard):
        stale.append(str(JSON_PATH))
    if stale:
        print(
            f"--check: {', '.join(stale)} is STALE — it does not match a "
            "recomputation from the committed recordings. Re-run "
            f"`{REGENERATE_COMMAND}` and commit the result."
        )
        return 1
    print(
        f"--check: {MARKDOWN_PATH} and {JSON_PATH} are consistent with the "
        "committed recordings."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Recompute both files and diff against the committed ones; exit 1 on drift.",
    )
    args = parser.parse_args(argv)
    if args.check:
        return check_report(_REPO_ROOT)
    scorecard = publish(_REPO_ROOT)
    pooled = scorecard.pooled
    print(
        f"Wrote {MARKDOWN_PATH} and {JSON_PATH}: {pooled.ballots} ballots over "
        f"{pooled.meetings} meetings; grounded "
        f"{pooled.grounded_all.numerator}/{pooled.grounded_all.denominator}; "
        f"deviating EJECTs {pooled.argmax_independence.deviators}/"
        f"{pooled.argmax_independence.unambiguous_ballots}; manufactured flags "
        f"{pooled.manufactured_contradiction.flags.numerator}/"
        f"{pooled.manufactured_contradiction.flags.denominator}; "
        "role-correctness is reported and gates nothing."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
