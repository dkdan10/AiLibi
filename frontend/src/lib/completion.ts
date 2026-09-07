import type { GameReport } from "../types/api";

/** Missing legacy metadata cannot establish a verified outcome or a tick limit. */
export function completionStatus(game: GameReport) {
  if (game.completion_status !== undefined) return game.completion_status;
  if (game.winner !== null) return "completed";
  if (game.reason === "TICK_BUDGET_REACHED") return "tick_limited";
  if (game.reason.startsWith("meeting aborted")) return "aborted";
  return "unfinished";
}

export function balanceCounts(games: readonly GameReport[]) {
  let crewWins = 0;
  let impostorWins = 0;
  let tickBudget = 0;
  let aborted = 0;
  let unfinished = 0;
  let unverified = 0;
  for (const game of games) {
    const status = completionStatus(game);
    if (status === "completed") {
      if (game.outcome_verified === true && game.winner === "CREWMATES") crewWins++;
      else if (game.outcome_verified === true && game.winner === "IMPOSTORS") impostorWins++;
      else unverified++;
    } else if (status === "tick_limited") tickBudget++;
    else if (status === "aborted") aborted++;
    else unfinished++;
  }
  return { crewWins, impostorWins, tickBudget, aborted, unfinished, unverified,
    decisive: crewWins + impostorWins };
}
