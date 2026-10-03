import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { PublicResultsView } from "./PublicResults";
import type { ExperimentConfigView, PublicResultsView as Summary, ReportProvenanceGroupView } from "../types/api";

const summary: Summary = { format_version: 1, set_name: "9p2i", source_fingerprint: "sha256:example", recorded_from: "2026-08-30", recorded_until: "2026-08-30", models: ["recorded-model"], prompt_versions: ["v5"], source_url: "https://example.com/source", games: 50, completed: 48, aborted: 1, tick_limited: 1, unfinished: 0, crew_wins: 35, impostor_wins: 13, task_wins: 0, meetings: 151, ejections: 95, impostor_ejections: 82, innocent_ejections: 13, proof_backed_ejections: 68, proof_backed_correct: 68, proof_free_ejections: 27, proof_free_correct: 14, reported_cost_usd: 0, input_tokens: 100, output_tokens: 50, cases: [{ case_id: "example", title: "A disputed route", setup: "Investigate the sighting.", explanation: "HIDDEN OUTCOME ROLE", game_id: "headless-seed-46", meeting_id: "headless-seed-46:meeting-3", meeting_tick: 31, observer_id: "p-9", turn_id: "turn-1", observation_id: "p-9:29:3", source_sha256: "hash", source_url: "https://example.com/source", classification: "unsupported" }] };

/** The shown 9-player set's declared config, read off disk by the card test. */
const SHOWN_CONFIG = resolve(dirname(fileURLToPath(import.meta.url)), "../../../replays/samples/9p2i/experiment-config.json");

/** An older payload: none of the later keys is present, every field at its default. */
const OLDER: ExperimentConfigView = { format_version: 1, redistribution_policy: "lowest_id", meeting_reset: "preserve", crew_idle_policy: "hub_wait", vent_exit_policy: "target_distance", post_meeting_retarget: false, self_report: false, sabotage_threshold: "six_sevenths", evidence_reasoning_version: null, bounded_rebuttal_version: null, public_account_version: null, attributed_testimony_version: null };

/** The seven adopted rules, each with the words the card must use for it. */
const ADOPTED_WORDS: ReadonlyArray<readonly [keyof ExperimentConfigView, string | number, string]> = [
  ["vent_witness_rule", "physical", "vent use seen only in the room where it happens"],
  ["vent_entry_policy", "own_fresh_kill", "impostors enter a vent only beside a body they have just killed"],
  ["meeting_reset", "hub_with_grace", "after each meeting, the survivors start again from the meeting room with the bodies cleared"],
  ["bounded_rebuttal_version", 1, "one reply to a late accusation"],
  ["report_body_handle_version", 1, "body reports without the time of death"],
  ["ballot_kill_row_version", 1, "witnessed kills listed on the voter's ballot"],
  ["impostor_ballot_version", 1, "impostor ballots cast by strategy"],
];

/** One non-default value of every other config field, and the experiment words it earns. */
const OTHER_FIELDS: ReadonlyArray<readonly [Partial<ExperimentConfigView>, string | null]> = [
  [{ crew_idle_policy: "patrol" }, "experimental movement or action policies"],
  [{ post_meeting_retarget: true }, "experimental movement or action policies"],
  [{ self_report: true }, "experimental movement or action policies"],
  [{ sabotage_threshold: "two_thirds" }, "experimental movement or action policies"],
  [{ redistribution_policy: "least_remaining_work" }, "experimental round or task rules"],
  [{ evidence_reasoning_version: 2 }, "observation timing and travel checks v2"],
  [{ investigation_version: 1 }, "bounded missing-player searches"],
  [{ contextual_self_report_version: 1 }, "context-dependent self-reporting"],
  [{ public_account_version: 1 }, "common public accounts"],
  [{ attributed_testimony_version: 1 }, "attributed witness testimony"],
  // The recording format is not a behavior: it earns no words at all.
  [{ format_version: 3 }, null],
];

function group(config: ExperimentConfigView | null, kind: ReportProvenanceGroupView["agent_factory_kind"] = "experimental"): ReportProvenanceGroupView {
  return { game_ids: ["headless-seed-1"], agent_factory_kind: kind, experiment_config: config, substrate_flags: null, tactical_policy: null, crew_tactical_policy: null, temporal_observation_version: null };
}

/** The text of each line of the one recorded-behavior card `config` renders. */
function groupLines(config: ExperimentConfigView | null, kind: ReportProvenanceGroupView["agent_factory_kind"] = "experimental"): string[] {
  const html = renderToStaticMarkup(<PublicResultsView results={{ ...summary, provenance_groups: [group(config, kind)] }} />);
  const card = /<ul[^>]*aria-label="Recorded behavior groups"[^>]*>([\s\S]*?)<\/ul>/.exec(html)?.[1];
  if (card === undefined) throw new Error("no recorded-behavior card rendered");
  return [...card.matchAll(/<p>([\s\S]*?)<\/p>/g)].map((match) =>
    (match[1] ?? "").replace(/<[^>]*>/g, "").replaceAll("&#x27;", "'").replaceAll("&quot;", '"').replaceAll("&lt;", "<").replaceAll("&gt;", ">").replaceAll("&amp;", "&"),
  );
}

describe("public result interpretation", () => {
  it("uses completed outcomes for win denominator, distinct evidence groups and source links", () => {
    const html = renderToStaticMarkup(<PublicResultsView results={summary} />);
    expect(html).toContain("35/48");
    expect(html).toContain("68/68");
    expect(html).toContain("14/27");
    expect(html).toContain("100% by construction");
    expect(html).toContain("27 ejections without role proof");
    expect(html).toContain("1 aborted");
    expect(html).toContain("not a bill");
    expect(html).toContain("https://example.com/source");
    expect(html).toContain("evidenceId=p-9%3A29%3A3");
    expect(html).not.toContain("HIDDEN OUTCOME ROLE");
    expect(html).not.toContain("unsupported");
  });
  it("keeps an empty denominator explicit instead of displaying a fabricated rate", () => {
    const html = renderToStaticMarkup(<PublicResultsView results={{ ...summary, completed: 0, crew_wins: 0 }} />);
    expect(html).toContain("0/0 (no eligible records)");
    expect(html).not.toContain("NaN");
  });
  it("keeps historical unknown and mixed custom identities visible", () => {
    const old = renderToStaticMarkup(<PublicResultsView results={summary} />);
    expect(old).toContain("Behavior provenance is unavailable");
    const mixed = renderToStaticMarkup(<PublicResultsView results={{ ...summary, provenance_groups: [
      { game_ids: ["headless-seed-1"], agent_factory_kind: null, experiment_config: null, substrate_flags: null, tactical_policy: null, crew_tactical_policy: null, temporal_observation_version: null },
      { game_ids: ["headless-seed-2"], agent_factory_kind: "custom", experiment_config: null, substrate_flags: null, tactical_policy: null, crew_tactical_policy: null, temporal_observation_version: 2 },
    ] }} />);
    expect(mixed).toContain("mixes recorded behavior configurations");
    expect(mixed).toContain("Agent factory not recorded");
    expect(mixed).toContain("Custom agent factory");
    expect(mixed).not.toContain("Built-in scripted agent factory");
  });
  it("names the observation clock, so two groups that differ only by it do not read alike", () => {
    const base = { game_ids: ["headless-seed-1"], agent_factory_kind: "scripted" as const, experiment_config: null, substrate_flags: null, tactical_policy: null, crew_tactical_policy: null };
    const mixed = renderToStaticMarkup(<PublicResultsView results={{ ...summary, provenance_groups: [
      { ...base, temporal_observation_version: 1 },
      { ...base, game_ids: ["headless-seed-2"], temporal_observation_version: 2 },
    ] }} />);
    expect(mixed).toContain("mixes recorded behavior configurations");
    expect(mixed).toContain("Observation clock: v1.");
    expect(mixed).toContain("Observation clock: v2.");
    const unstamped = renderToStaticMarkup(<PublicResultsView results={{ ...summary, provenance_groups: [
      { ...base, temporal_observation_version: null },
    ] }} />);
    expect(unstamped).toContain("Observation clock: not recorded.");
    expect(unstamped).not.toContain("Observation clock: v1.");
  });
  it("calls each adopted rule adopted, in plain words, and leaves a default group unchanged", () => {
    // An older payload: none of the five later keys is present.
    const quiet = groupLines(OLDER);
    expect(quiet).toContain("No enabled experiments recorded. This alone does not certify the default behavior.");
    const adopted: Array<[Partial<ExperimentConfigView>, string]> = [
      [{ vent_witness_rule: "physical" }, "vent use seen only in the room where it happens"],
      [{ vent_entry_policy: "own_fresh_kill" }, "impostors enter a vent only beside a body they have just killed"],
      [{ meeting_reset: "hub_with_grace" }, "after each meeting, the survivors start again from the meeting room with the bodies cleared"],
      [{ bounded_rebuttal_version: 1 }, "one reply to a late accusation"],
      [{ report_body_handle_version: 1 }, "body reports without the time of death"],
      [{ ballot_kill_row_version: 1 }, "witnessed kills listed on the voter's ballot"],
      [{ impostor_ballot_version: 1 }, "impostor ballots cast by strategy"],
    ];
    for (const [change, words] of adopted) {
      const lines = groupLines({ ...OLDER, ...change });
      expect(lines).toContain(`Rules adopted for the current game: ${words}.`);
      // The words these rules carried as experiments, now absent.
      expect(lines.join("\n")).not.toContain("Recorded experiments:");
      expect(lines.join("\n")).not.toContain("experimental movement or action policies");
      expect(lines.join("\n")).not.toContain("experimental round or task rules");
      expect(lines).not.toContain("No enabled experiments recorded. This alone does not certify the default behavior.");
    }
    const defaults: ExperimentConfigView = { ...OLDER, vent_witness_rule: "both_rooms", vent_entry_policy: "any_body", report_body_handle_version: null, ballot_kill_row_version: null, impostor_ballot_version: null, kill_cooldown_ticks: null };
    expect(groupLines(defaults)).toContain("No enabled experiments recorded. This alone does not certify the default behavior.");
  });

  it("names the kept vent exit and a recorded cooldown as set for these recordings, never adopted or experimental", () => {
    const waits = groupLines({ ...OLDER, vent_exit_policy: "look_and_wait" });
    expect(waits).toContain("Also in place: impostors in a vent wait briefly for the rooms they can see to clear before coming out, set for these recordings.");
    // Its old classification, now absent.
    expect(waits.join("\n")).not.toContain("Recorded experiments: experimental movement or action policies.");
    expect(waits.join("\n")).not.toMatch(/experiment|adopted/i);
    // The other non-default exit is still an experiment.
    expect(groupLines({ ...OLDER, vent_exit_policy: "observed_risk" })).toContain("Recorded experiments: experimental movement or action policies.");
    // The two groups differ only by the cooldown: one names it, the other has none.
    const cooled = groupLines({ ...OLDER, kill_cooldown_ticks: 6 });
    expect(cooled).toContain("Also in place: a kill cooldown of 6 ticks set for these recordings.");
    expect(cooled.join("\n")).not.toContain("Recorded experiments: a kill cooldown");
    expect(cooled.join("\n")).not.toMatch(/experiment|adopted/i);
    const unset = groupLines(OLDER);
    expect(unset.join("\n")).not.toContain("kill cooldown");
    expect(unset).toContain("No enabled experiments recorded. This alone does not certify the default behavior.");
    expect(groupLines({ ...OLDER, kill_cooldown_ticks: 1 })).toContain("Also in place: a kill cooldown of 1 tick set for these recordings.");
    // Both together, in that order.
    expect(groupLines({ ...OLDER, vent_exit_policy: "look_and_wait", kill_cooldown_ticks: 6 })).toContain(
      "Also in place: impostors in a vent wait briefly for the rooms they can see to clear before coming out, set for these recordings; a kill cooldown of 6 ticks set for these recordings.",
    );
  });

  it("keeps every other setting an experiment, each in its own words", () => {
    for (const [change, words] of OTHER_FIELDS) {
      const lines = groupLines({ ...OLDER, ...change });
      if (words === null) {
        expect(lines).toContain("No enabled experiments recorded. This alone does not certify the default behavior.");
      } else {
        expect(lines).toContain(`Recorded experiments: ${words}.`);
      }
    }
    expect(groupLines({ ...OLDER, evidence_reasoning_version: 1 })).toContain("Recorded experiments: observation timing and travel checks v1.");
    expect(groupLines({ ...OLDER, investigation_version: 1, public_account_version: 1, redistribution_policy: "least_remaining_work" })).toContain(
      "Recorded experiments: bounded missing-player searches, common public accounts, experimental round or task rules.",
    );
  });

  it("labels the built-in agents with recorded tactical settings by what they record", () => {
    const lines = groupLines(OLDER);
    expect(lines[0]).toBe("Built-in agents with recorded tactical settings · 1 recording.");
    expect(groupLines(OLDER, "scripted")[0]).toBe("Built-in scripted agent factory · 1 recording.");
    expect(groupLines(OLDER, "custom")[0]).toBe("Custom agent factory · 1 recording.");
    expect(groupLines(OLDER, null)[0]).toBe("Agent factory not recorded · 1 recording.");
    expect(lines.join("\n")).not.toContain("Experimental agent factory");
    const many = renderToStaticMarkup(<PublicResultsView results={{ ...summary, provenance_groups: [{ ...group(OLDER), game_ids: ["headless-seed-1", "headless-seed-2"] }] }} />);
    expect(many).toContain("Built-in agents with recorded tactical settings</strong> · 2 recordings.");
    expect(lines).toContain("Impostor policy: not recorded. Crew policy: not recorded. Rule settings: not recorded.");
  });

  it("reads the shown set's declared config off disk and calls nothing on its card an experiment", () => {
    const declared = JSON.parse(readFileSync(SHOWN_CONFIG, "utf8")) as Partial<ExperimentConfigView>;
    const config: ExperimentConfigView = { ...OLDER, ...declared };
    const html = renderToStaticMarkup(<PublicResultsView results={{ ...summary, provenance_groups: [{ ...group(config), game_ids: Array.from({ length: 50 }, (_, seed) => `headless-seed-${String(seed)}`), substrate_flags: {} }] }} />);
    expect(html).not.toMatch(/experiment/i);
    // Nor any project word a visitor has no definition for.
    expect(html).not.toMatch(/\b(?:arms?|regroup|era|stage-b)\b/i);
    expect(groupLines(config)).toEqual([
      "Built-in agents with recorded tactical settings · 1 recording.",
      "Rules adopted for the current game: vent use seen only in the room where it happens; impostors enter a vent only beside a body they have just killed; after each meeting, the survivors start again from the meeting room with the bodies cleared; one reply to a late accusation; body reports without the time of death; witnessed kills listed on the voter's ballot; impostor ballots cast by strategy.",
      "Also in place: impostors in a vent wait briefly for the rooms they can see to clear before coming out, set for these recordings; a kill cooldown of 6 ticks set for these recordings.",
      "Impostor policy: not recorded. Crew policy: not recorded. Rule settings: not recorded.",
      "Observation clock: not recorded.",
    ]);
  });

  it("over every combination, calls exactly the adopted values adopted and nothing else", () => {
    // 128 on/off combinations of the seven adopted fields, times the three vent
    // exits, times a cooldown set or unset: 768 renders. Each is repeated with
    // one non-default value of every other field, so a value outside the seven
    // is never called adopted, and an adopted value is never called an
    // experiment or left out.
    let renders = 0;
    for (let mask = 0; mask < 2 ** ADOPTED_WORDS.length; mask += 1) {
      const on = ADOPTED_WORDS.filter((_, index) => (mask >> index) % 2 === 1);
      for (const exit of ["target_distance", "look_and_wait", "observed_risk"] as const) {
        for (const cooldown of [null, 6]) {
          for (const [other, otherWords] of [[{}, null] as const, ...OTHER_FIELDS]) {
            const config: ExperimentConfigView = { ...OLDER, ...Object.fromEntries(on.map(([field, value]) => [field, value])), vent_exit_policy: exit, kill_cooldown_ticks: cooldown, ...other };
            const lines = groupLines(config);
            renders += 1;
            const adoptedLine = lines.find((line) => line.startsWith("Rules adopted for the current game: "));
            if (on.length === 0) expect(adoptedLine).toBeUndefined();
            else expect(adoptedLine).toBe(`Rules adopted for the current game: ${on.map(([, , words]) => words).join("; ")}.`);
            const experimentsLine = lines.find((line) => line.startsWith("Recorded experiments: ")) ?? "";
            const placeLine = lines.find((line) => line.startsWith("Also in place: ")) ?? "";
            for (const [, , words] of ADOPTED_WORDS) {
              expect(experimentsLine).not.toContain(words);
              expect(placeLine).not.toContain(words);
            }
            const waits = exit === "look_and_wait";
            expect(placeLine.includes("impostors in a vent wait briefly")).toBe(waits);
            expect(placeLine.includes("a kill cooldown of 6 ticks set for these recordings")).toBe(cooldown !== null);
            expect(experimentsLine.includes("experimental movement or action policies")).toBe(exit === "observed_risk" || otherWords === "experimental movement or action policies");
            if (otherWords !== null) expect(experimentsLine).toContain(otherWords);
            const nothing = on.length === 0 && exit === "target_distance" && cooldown === null && otherWords === null;
            expect(lines.includes("No enabled experiments recorded. This alone does not certify the default behavior.")).toBe(nothing);
            expect(experimentsLine === "").toBe(exit !== "observed_risk" && otherWords === null);
          }
        }
      }
    }
    expect(renders).toBe(768 * (1 + OTHER_FIELDS.length));
  }, 60_000);

  it("heads the cases without a count, however many the set publishes", () => {
    const one = renderToStaticMarkup(<PublicResultsView results={summary} />);
    expect(summary.cases).toHaveLength(1);
    expect(one).toContain("Decisions to investigate");
    expect(one).not.toMatch(/\b(?:three|two|one) decisions\b/i);
    const none = renderToStaticMarkup(<PublicResultsView results={{ ...summary, cases: [] }} />);
    expect(none).not.toContain("Decisions to investigate");
    expect(none).toContain("No source-matched editorial cases are published for this set.");
  });
});
