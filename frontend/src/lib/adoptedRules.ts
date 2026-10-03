// The rule settings the owner adopted as the current game.
//
// The public results card calls a recorded setting adopted only when its field
// holds one of these values. Anything else a recording sets is either named as
// set for those recordings or labelled an experiment, never adopted.
//
// The list is the "Adopted arms" paragraph of `docs/experiment-arms.md`, in its
// order. `adoptedRules.test.ts` reads that paragraph and the shown set's
// declared config off disk and requires this list to equal the paragraph's
// pairs, each held by the config, so an edit to either source turns it red.

import type { ExperimentConfigView } from "../types/api";

export const ADOPTED_RULES = Object.freeze([
  { field: "vent_witness_rule", value: "physical" },
  { field: "vent_entry_policy", value: "own_fresh_kill" },
  { field: "meeting_reset", value: "hub_with_grace" },
  { field: "bounded_rebuttal_version", value: 1 },
  { field: "report_body_handle_version", value: 1 },
  { field: "ballot_kill_row_version", value: 1 },
  { field: "impostor_ballot_version", value: 1 },
] as const);

/** One adopted rule: a recorded config field and the value adopted for it. */
export type AdoptedRule = (typeof ADOPTED_RULES)[number];

/** The config fields an adopted rule names. */
export type AdoptedField = AdoptedRule["field"];

/** Whether `config` records `rule`'s field at its adopted value. */
export function holdsAdoptedValue(
  config: ExperimentConfigView,
  rule: AdoptedRule,
): boolean {
  return config[rule.field] === rule.value;
}
