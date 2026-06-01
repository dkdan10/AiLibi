"""Deterministic Extract phase of the gameplay-data audit.

Re-derives ground-truth roles (firewalled OUT of the replays) by re-seeding the
engine, re-runs the recorded action stream through ``engine.tick.advance_tick``
(mirroring ``api.replay_loader.ReplayLoader._walk``) so the engine itself
surfaces resolved events (Killed actor/target/room, ActionRejected, Moved,
MeetingTriggered, GameOver), then emits a structured FACTS JSON plus
code-certain HARD rule-violation findings.

Because ``advance_tick`` ENFORCES every hard rule (impostor-only kill, cooldown,
same-room kill, adjacency move, alive-player gate, eligible reporter) by emitting
an ``ActionRejectedEvent`` and NOT applying the offending action, a rule-breaking
action in the recorded stream becomes a rejection — and the rejection's reason is
the code-certain classifier. We additionally re-derive each Killed event's
victim role from the re-seeded roster to catch impostor-on-impostor kills.

Usage:
    PYTHONPATH=<repo root> uv run python audits/workflows/extract_gameplay_facts.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from engine.actions import Action
from engine.events import (
    ActionRejectedEvent,
    KilledEvent,
    MeetingTriggeredEvent,
)
from engine.tick import advance_tick
from engine.world import load_canonical_map
from orchestrator.game import apply_meeting_result
from orchestrator.replay import (
    FailedCallReplayEntry,
    GameEndReplayEntry,
    MeetingReplayEntry,
    ReplayEntry,
    _state_hash,
    read_all_entries,
)
from orchestrator.seeder import seed_initial_state

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = REPO_ROOT / "replays" / "samples" / "7p2i"
SEEDSET = "7p2i"

# Action adapter for deserializing recorded raw actions.
_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)


def _deserialize_actions(raw_actions: list[dict[str, Any]]) -> list[Action]:
    return [_ACTION_ADAPTER.validate_python(dict(raw)) for raw in raw_actions]


def _git_head() -> str:
    out = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout.strip()


def _classify_rejection(reason: str) -> str | None:
    """Map an ActionRejected reason to a HARD-rule category, or None.

    Only reasons that correspond to a *hard rule violation in the recorded
    stream* (the producer queued an action the engine had to refuse) are
    classified. Reasons that are normal contention (e.g. a stale do_task whose
    room changed) are not hard violations and return None.
    """

    r = reason.lower()
    if "player is dead" in r or "unknown player" in r:
        return "dead_or_unknown_player_action"
    if "only impostors can kill" in r:
        return "non_impostor_kill"
    if "kill is on cooldown" in r:
        return "kill_ignored_cooldown"
    if "kill requires same room" in r:
        return "kill_cross_room"
    if "move destination must be current or adjacent" in r:
        return "move_non_adjacent"
    if "unknown destination room" in r:
        return "move_unknown_room"
    if "report requires actor and body in same room" in r:
        return "report_ineligible_room"
    if "unknown body id" in r:
        return "report_unknown_body"
    return None


def main() -> int:
    game_map = load_canonical_map()
    roster = json.loads((SAMPLE_DIR / "roster.json").read_text(encoding="utf-8"))
    num_players = int(roster["num_players"])
    num_impostors = int(roster["num_impostors"])
    tasks_per_crewmate = int(roster["tasks_per_crewmate"])

    replay_paths = sorted(
        SAMPLE_DIR.glob("replay-seed-*.jsonl"),
        key=lambda p: int(p.stem.rsplit("-", 1)[1]),
    )
    games_analyzed = len(replay_paths)

    games: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []

    # Self-check accumulators.
    total_meeting_records = 0
    invariant_failures: list[str] = []

    # Aggregates.
    win_split: dict[str, int] = {}
    reason_counts: dict[str, int] = {}
    total_kills = 0
    impostor_victim_kills = 0
    total_meetings = 0
    ejections_by_role: dict[str, int] = {}
    total_calls = 0
    total_failed_calls = 0
    agg_input_tokens = 0
    agg_output_tokens = 0
    agg_cost = 0.0
    no_game_over = 0

    for path in replay_paths:
        seed = int(path.stem.rsplit("-", 1)[1])
        game_id = f"headless-seed-{seed}"

        # 1) Ground-truth roles.
        init_state = seed_initial_state(
            seed=seed,
            game_map=game_map,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
        )
        roles = {pid: p.role for pid, p in init_state.players.items()}
        found_impostors = sum(1 for r in roles.values() if r == "IMPOSTOR")
        if found_impostors != num_impostors:
            invariant_failures.append(
                f"seed {seed}: found {found_impostors} impostors, "
                f"roster says {num_impostors}"
            )

        # 2) Reconstruct resolved events by re-running the engine.
        entries = read_all_entries(path)
        replay_entries = [e for e in entries if isinstance(e, ReplayEntry)]
        meeting_entries = [e for e in entries if isinstance(e, MeetingReplayEntry)]
        failed_call_entries = [
            e for e in entries if isinstance(e, FailedCallReplayEntry)
        ]
        game_end = next((e for e in entries if isinstance(e, GameEndReplayEntry)), None)
        meeting_by_tick = {e.tick: e for e in meeting_entries}
        total_meeting_records += len(meeting_entries)

        kills: list[dict[str, Any]] = []
        deaths: set[str] = set()
        meetings_out: list[dict[str, Any]] = []
        # Win-condition-gap tracking: the first tick at which alive impostors hit 0.
        first_zero_impostor_tick: int | None = None

        state = init_state
        last_state_for_final = state
        meeting_index = 0

        for entry in replay_entries:
            actions = _deserialize_actions(list(entry.actions))
            state, events = advance_tick(state, actions, game_map=game_map)

            # State-hash self-check (replay determinism; the whole audit trusts
            # this reconstruction).
            actual = _state_hash(state)
            if actual != entry.state_hash:
                invariant_failures.append(
                    f"seed {seed} tick {entry.tick}: state-hash mismatch "
                    f"(recorded {entry.state_hash[:12]}, "
                    f"reconstructed {actual[:12]})"
                )

            for ev in events:
                if isinstance(ev, KilledEvent):
                    victim_role = roles.get(ev.target, "UNKNOWN")
                    killer_role = roles.get(ev.actor, "UNKNOWN")
                    kills.append(
                        {
                            "tick": ev.tick,
                            "killer": ev.actor,
                            "killer_role": killer_role,
                            "victim": ev.target,
                            "victim_role": victim_role,
                            "room": ev.room,
                        }
                    )
                    deaths.add(ev.target)
                    total_kills += 1
                    if victim_role == "IMPOSTOR":
                        impostor_victim_kills += 1
                        findings.append(
                            {
                                "id": f"KILL-IMP-{seed}-{ev.tick}",
                                "severity": "blocking",
                                "title": "Impostor killed a fellow impostor",
                                "claim": (
                                    "A resolved kill has victim_role==IMPOSTOR — an "
                                    "impostor was killed by another player, which "
                                    "the engine should never produce in a normal game."
                                ),
                                "evidence": (
                                    f"seed {seed} tick {ev.tick}: {ev.actor} "
                                    f"({killer_role}) killed {ev.target} (IMPOSTOR) "
                                    f"in {ev.room}"
                                ),
                                "repair_hint": (
                                    "Inspect engine.rules.resolve_kill / the agent "
                                    "target selection that produced an impostor-on-"
                                    "impostor kill; confirm role-aware target "
                                    "filtering for impostor kill intents."
                                ),
                            }
                        )
                elif isinstance(ev, ActionRejectedEvent):
                    category = _classify_rejection(ev.reason)
                    if category is not None:
                        # Severity: dead/unknown-player rejections are downstream
                        # symptoms of same-tick kill races (the actor died earlier
                        # in this tick's action ordering) — informational, not an
                        # independent hard violation. Cross-room / non-adjacent /
                        # ineligible-report are intent-generation waste -> high.
                        if category == "dead_or_unknown_player_action":
                            sev = "informational"
                        else:
                            sev = "high"
                        findings.append(
                            {
                                "id": f"REJ-{category}-{seed}-{ev.tick}",
                                "severity": sev,
                                "title": (
                                    f"Recorded action rejected by engine ({category})"
                                ),
                                "claim": (
                                    "The recorded action stream queued an action the "
                                    "engine refused: "
                                    f"{ev.reason!r}."
                                ),
                                "evidence": (
                                    f"seed {seed} tick {ev.tick}: actor {ev.actor} "
                                    f"({roles.get(ev.actor, 'UNKNOWN')}) action "
                                    f"{ev.action!r} rejected: {ev.reason!r}"
                                ),
                                "repair_hint": (
                                    "Trace the agent/orchestrator path that emitted "
                                    "this action; a producer that queues "
                                    "engine-illegal actions wastes a turn (the agent "
                                    "no-ops) and signals an intent-generation bug."
                                ),
                            }
                        )

            # Track alive impostors AFTER this tick resolved.
            alive_impostors = sum(
                1
                for pid, p in state.players.items()
                if p.alive and roles.get(pid) == "IMPOSTOR"
            )
            if alive_impostors == 0 and first_zero_impostor_tick is None:
                first_zero_impostor_tick = entry.tick

            last_state_for_final = state

            if state.phase == "GAME_OVER":
                break

            if state.phase != "MEETING":
                continue

            # Meeting resolved this tick.
            meeting_entry = meeting_by_tick.get(entry.tick)
            if meeting_entry is None:
                # Partial replay (meeting opened, never resolved). Stop the walk.
                break

            # Trigger body id for corpse consumption.
            body_id: str | None = None
            for ev in events:
                if isinstance(ev, MeetingTriggeredEvent):
                    body_id = ev.body_id

            from meetings.schemas import MeetingResult

            result = MeetingResult(
                meeting_id=meeting_entry.meeting_id,
                triggered_by=meeting_entry.triggered_by,
                trigger_tick=meeting_entry.tick,
                outcome=meeting_entry.outcome,
                ejected_player_id=meeting_entry.ejected_player_id,
                ballots=meeting_entry.ballots,
                contradictions=meeting_entry.contradictions,
                transcript=meeting_entry.transcript,
            )

            ejected_id = meeting_entry.ejected_player_id
            ejected_role = roles.get(ejected_id) if ejected_id is not None else None

            ballots_out = [
                {"voter": b.voter, "target": b.target} for b in meeting_entry.ballots
            ]
            meetings_out.append(
                {
                    "meeting_id": meeting_entry.meeting_id,
                    "tick": meeting_entry.tick,
                    "triggered_by": meeting_entry.triggered_by,
                    "outcome": meeting_entry.outcome,
                    "ejected_player_id": ejected_id,
                    "ejected_role": ejected_role,
                    "ballots": ballots_out,
                    "n_contradictions": len(meeting_entry.contradictions),
                }
            )
            total_meetings += 1
            if ejected_id is not None and ejected_role is not None:
                ejections_by_role[ejected_role] = (
                    ejections_by_role.get(ejected_role, 0) + 1
                )

            # Per-call token totals from this meeting's llm_calls.
            for call in meeting_entry.llm_calls:
                total_calls += 1
                agg_input_tokens += call.input_tokens
                agg_output_tokens += call.output_tokens
                agg_cost += call.cost_usd

            state, post_events = apply_meeting_result(
                state,
                result,
                game_map=game_map,
                triggering_body_id=body_id,
            )
            after = _state_hash(state)
            if after != meeting_entry.state_hash_after:
                invariant_failures.append(
                    f"seed {seed} meeting {meeting_entry.meeting_id}: "
                    f"post-meeting state-hash mismatch"
                )
            meeting_index += 1

            # Re-track alive impostors after the ejection.
            alive_impostors = sum(
                1
                for pid, p in state.players.items()
                if p.alive and roles.get(pid) == "IMPOSTOR"
            )
            if alive_impostors == 0 and first_zero_impostor_tick is None:
                first_zero_impostor_tick = meeting_entry.tick

            last_state_for_final = state
            if state.phase == "GAME_OVER":
                break

        # Failed-call accounting (these carry burned tokens for the aborted run).
        failed_calls_out: list[dict[str, Any]] = []
        for fc in failed_call_entries:
            total_failed_calls += 1
            total_calls += 1
            agg_input_tokens += fc.input_tokens
            agg_output_tokens += fc.output_tokens
            agg_cost += fc.cost_usd
            failed_calls_out.append(
                {
                    "meeting_id": fc.meeting_id,
                    "tick": fc.tick,
                    "model": fc.model,
                    "error_type": fc.error_type,
                    "error_message": fc.error_message[:200],
                    "input_tokens": fc.input_tokens,
                    "output_tokens": fc.output_tokens,
                    "cost_usd": fc.cost_usd,
                }
            )

        # Recorded winner/reason from the game_end row (authoritative producer record).
        recorded_winner = game_end.winner if game_end is not None else None
        recorded_reason = game_end.reason if game_end is not None else None
        recorded_go_tick = game_end.tick if game_end is not None else None
        if game_end is None:
            no_game_over += 1
        else:
            win_split[recorded_winner or "NONE"] = (
                win_split.get(recorded_winner or "NONE", 0) + 1
            )
            if recorded_reason is not None:
                reason_counts[recorded_reason] = (
                    reason_counts.get(recorded_reason, 0) + 1
                )

        # --- Win-condition-gap check ---
        # If alive impostors hit 0 at tick T but the game's recorded game_over
        # tick is strictly later, the game continued past the crew-win point.
        if (
            first_zero_impostor_tick is not None
            and recorded_go_tick is not None
            and recorded_go_tick > first_zero_impostor_tick
        ):
            findings.append(
                {
                    "id": f"WINGAP-{seed}",
                    "severity": "blocking",
                    "title": "Game continued past the tick alive impostors hit 0",
                    "claim": (
                        "Alive impostors reached 0 before the recorded game_over "
                        "tick — the game ran on past the crew-win point "
                        "(win-condition gap)."
                    ),
                    "evidence": (
                        f"seed {seed}: alive impostors hit 0 at tick "
                        f"{first_zero_impostor_tick}, but game_over recorded at tick "
                        f"{recorded_go_tick} ({recorded_winner}/{recorded_reason})"
                    ),
                    "repair_hint": (
                        "engine.win_conditions now has the alive_impostors==0 crew "
                        "win; verify the replay was recorded with that build."
                    ),
                }
            )

        # --- Recorded winner vs final reconstructed state cross-check ---
        if game_end is not None:
            alive_players = [
                p for p in last_state_for_final.players.values() if p.alive
            ]
            alive_imp = sum(1 for p in alive_players if p.role == "IMPOSTOR")
            alive_crew = sum(1 for p in alive_players if p.role == "CREWMATE")
            total_tasks = len(last_state_for_final.tasks)
            done_tasks = sum(
                1 for t in last_state_for_final.tasks.values() if t.completed
            )
            mismatch_reason: str | None = None
            if recorded_reason == "CREWMATE_TASKS":
                if not (total_tasks > 0 and done_tasks == total_tasks):
                    mismatch_reason = (
                        f"CREWMATE_TASKS but tasks {done_tasks}/{total_tasks} done"
                    )
            elif recorded_reason == "CREWMATE_EJECT":
                if alive_imp != 0:
                    mismatch_reason = (
                        f"CREWMATE_EJECT but {alive_imp} impostor(s) alive"
                    )
            elif recorded_reason == "IMPOSTOR_PARITY":
                if not (alive_imp >= alive_crew):
                    mismatch_reason = (
                        f"IMPOSTOR_PARITY but alive imp {alive_imp} < crew {alive_crew}"
                    )
            if mismatch_reason is not None:
                findings.append(
                    {
                        "id": f"WINMISMATCH-{seed}",
                        "severity": "blocking",
                        "title": "Recorded winner/reason contradicts final state",
                        "claim": (
                            "The recorded game_over winner/reason does not match the "
                            "final reconstructed alive-roles/tasks state."
                        ),
                        "evidence": (
                            f"seed {seed}: recorded {recorded_winner}/"
                            f"{recorded_reason} but {mismatch_reason}"
                        ),
                        "repair_hint": (
                            "Compare engine.win_conditions.evaluate_win_conditions "
                            "against the recorded outcome for this seed."
                        ),
                    }
                )

        # Per-game token totals.
        game_input = sum(
            c.input_tokens for e in meeting_entries for c in e.llm_calls
        ) + sum(fc.input_tokens for fc in failed_call_entries)
        game_output = sum(
            c.output_tokens for e in meeting_entries for c in e.llm_calls
        ) + sum(fc.output_tokens for fc in failed_call_entries)
        game_cost = sum(c.cost_usd for e in meeting_entries for c in e.llm_calls) + sum(
            fc.cost_usd for fc in failed_call_entries
        )

        # Self-check: every kill-derived death has its victim in deaths.
        for k in kills:
            if k["victim"] not in deaths:
                invariant_failures.append(
                    f"seed {seed}: kill victim {k['victim']} at tick {k['tick']} "
                    f"not in deaths set"
                )

        games.append(
            {
                "seed": seed,
                "game_id": game_id,
                "roles": roles,
                "winner": recorded_winner,
                "reason": recorded_reason,
                "game_over_tick": recorded_go_tick,
                "kills": kills,
                "deaths": sorted(deaths),
                "meetings": meetings_out,
                "first_zero_impostor_tick": first_zero_impostor_tick,
                "tokens": {
                    "input": game_input,
                    "output": game_output,
                    "cost_usd": game_cost,
                },
                "failed_calls": failed_calls_out,
            }
        )

    # --- Self-check invariants (FAIL LOUD) ---
    self_checks: list[str] = []
    ok_meetings = total_meetings == total_meeting_records
    self_checks.append(
        f"total meetings in facts ({total_meetings}) == meeting records "
        f"({total_meeting_records}): {'OK' if ok_meetings else 'FAIL'}"
    )
    if not ok_meetings:
        invariant_failures.append(
            f"meeting count mismatch: facts {total_meetings} vs records "
            f"{total_meeting_records}"
        )

    n_files = len(list(SAMPLE_DIR.glob("replay-seed-*.jsonl")))
    ok_games = games_analyzed == n_files
    self_checks.append(
        f"games_analyzed ({games_analyzed}) == replay files ({n_files}): "
        f"{'OK' if ok_games else 'FAIL'}"
    )
    if not ok_games:
        invariant_failures.append(f"games_analyzed {games_analyzed} != files {n_files}")

    impostor_check_ok = all(
        sum(1 for r in g["roles"].values() if r == "IMPOSTOR") == num_impostors
        for g in games
    )
    self_checks.append(
        f"every seed has exactly {num_impostors} impostors: "
        f"{'OK' if impostor_check_ok else 'FAIL'}"
    )

    for line in self_checks:
        print(line, file=sys.stderr)

    if invariant_failures:
        for f in invariant_failures:
            print(f"INVARIANT FAILURE: {f}", file=sys.stderr)
        raise RuntimeError(
            f"{len(invariant_failures)} extraction invariant(s) failed; "
            "the facts file would be untrustworthy. Aborting."
        )

    aggregates = {
        "win_split": win_split,
        "reason_counts": reason_counts,
        "no_game_over_games": no_game_over,
        "total_kills": total_kills,
        "impostor_victim_kills": impostor_victim_kills,
        "total_meetings": total_meetings,
        "ejections_by_role": ejections_by_role,
        "total_calls": total_calls,
        "total_failed_calls": total_failed_calls,
        "tokens": {
            "input": agg_input_tokens,
            "output": agg_output_tokens,
            "cost_usd": agg_cost,
        },
    }

    facts = {
        "git_head": _git_head(),
        "sample_dir": str(SAMPLE_DIR),
        "seedset": SEEDSET,
        "roster": roster,
        "games_analyzed": games_analyzed,
        "self_checks": self_checks,
        "aggregates": aggregates,
        "games": games,
    }

    tmpdir = os.environ.get("TMPDIR", "/tmp")
    facts_path = Path(tmpdir) / f"ailibi-gameplay-facts-{SEEDSET}.json"
    facts_path.write_text(
        json.dumps(facts, indent=2, sort_keys=False), encoding="utf-8"
    )

    # Emit machine-readable summary for the caller on stdout.
    print(
        json.dumps(
            {
                "facts_path": str(facts_path),
                "games_analyzed": games_analyzed,
                "aggregates": aggregates,
                "n_findings": len(findings),
                "findings": findings,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
