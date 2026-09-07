import { describe, expect, it } from "vitest";

import type { GameReport } from "../types/api";
import { balanceCounts, completionStatus } from "./completion";

function game(changes: Partial<GameReport> = {}): GameReport {
  return { game_id: "g", seed: 1, winner: null, reason: "no game_over record in replay",
    final_tick: null, ...changes };
}

describe("completion evidence", () => {
  it("keeps legacy outcomes unverified and missing outcomes unfinished", () => {
    expect(completionStatus(game())).toBe("unfinished");
    expect(completionStatus(game({ reason: "TICK_BUDGET_REACHED" }))).toBe("tick_limited");
    expect(balanceCounts([game({ winner: "CREWMATES" })])).toMatchObject({
      crewWins: 0, decisive: 0, unverified: 1, tickBudget: 0,
    });
  });

  it("uses only verified terminal outcomes as the decisive denominator", () => {
    expect(balanceCounts([
      game({ winner: "CREWMATES", completion_status: "completed", outcome_verified: true }),
      game({ winner: "IMPOSTORS", completion_status: "completed", outcome_verified: true }),
      game({ winner: "CREWMATES" }),
      game({ completion_status: "aborted" }),
      game({ completion_status: "tick_limited" }),
      game(),
    ])).toEqual({ crewWins: 1, impostorWins: 1, decisive: 2,
      unverified: 1, aborted: 1, tickBudget: 1, unfinished: 1 });
  });

  it("cannot verify a winner attached to a nonterminal status", () => {
    expect(balanceCounts([game({ winner: "CREWMATES", completion_status: "unfinished",
      outcome_verified: true })])).toMatchObject({ crewWins: 0, decisive: 0, unfinished: 1 });
  });
});
