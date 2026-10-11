import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { PublicResultsView } from "./PublicResults";
import { fmt, PUBLIC_RESULTS_COPY, setOptionLabel } from "../lib/copy";
import type { ExperimentConfigView, PublicResultsView as Summary, ReportProvenanceGroupView } from "../types/api";

const summary: Summary = { format_version: 1, set_name: "9p2i", source_fingerprint: "sha256:example", recorded_from: "2026-08-30", recorded_until: "2026-08-30", models: ["recorded-model"], prompt_versions: ["v5"], source_url: "https://example.com/source", games: 50, completed: 48, aborted: 1, tick_limited: 1, unfinished: 0, crew_wins: 35, impostor_wins: 13, task_wins: 0, meetings: 151, ejections: 95, impostor_ejections: 82, innocent_ejections: 13, proof_backed_ejections: 68, proof_backed_correct: 68, proof_free_ejections: 27, proof_free_correct: 14, reported_cost_usd: 0, input_tokens: 100, output_tokens: 50, cases: [{ case_id: "example", title: "A disputed route", setup: "Investigate the sighting.", explanation: "HIDDEN OUTCOME ROLE", game_id: "headless-seed-46", meeting_id: "headless-seed-46:meeting-3", meeting_tick: 31, observer_id: "p-9", turn_id: "turn-1", observation_id: "p-9:29:3", source_sha256: "hash", source_url: "https://example.com/source", classification: "unsupported" }] };

/** The shown 9-player set's declared config, read off disk by the card test. */
const SHOWN_CONFIG = resolve(dirname(fileURLToPath(import.meta.url)), "../../../replays/samples/9p2i/experiment-config.json");

/** An older payload: none of the later keys is present, every field at its default. */
const OLDER: ExperimentConfigView = { format_version: 1, redistribution_policy: "lowest_id", meeting_reset: "preserve", crew_idle_policy: "hub_wait", vent_exit_policy: "target_distance", post_meeting_retarget: false, self_report: false, sabotage_threshold: "six_sevenths", evidence_reasoning_version: null, bounded_rebuttal_version: null, public_account_version: null, attributed_testimony_version: null };

/** The seven adopted rules, each with the sentence the card must use for it. */
const ADOPTED_WORDS: ReadonlyArray<readonly [keyof ExperimentConfigView, string | number, string]> = [
  ["vent_witness_rule", "physical", "Vent use is seen only in the room where it happens."],
  ["vent_entry_policy", "own_fresh_kill", "Impostors enter a vent only beside a body they have just killed."],
  ["meeting_reset", "hub_with_grace", "After each meeting, the survivors start again from the meeting room with the bodies cleared."],
  ["bounded_rebuttal_version", 1, "A player accused after already speaking gets one reply."],
  ["report_body_handle_version", 1, "A body report does not give the time of death."],
  ["ballot_kill_row_version", 1, "Each ballot lists the kills its voter saw a player from the other side make."],
  ["impostor_ballot_version", 1, "An impostor is asked to vote as a move for its own side."],
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
    expect(html).toContain("Only impostors can vent, so the first count says nothing about how well the table reasoned.");
    expect(html).toContain("27 ejections without a sighting");
    expect(html).toContain("1 aborted");
    expect(html).toContain("not a bill");
    expect(html).toContain("https://example.com/source");
    expect(html).toContain("evidenceId=p-9%3A29%3A3");
    expect(html).not.toContain("HIDDEN OUTCOME ROLE");
    expect(html).not.toContain("unsupported");
  });
  it("heads the ejection tile with what its fraction counts, in the copy's words", () => {
    const html = renderToStaticMarkup(<PublicResultsView results={summary} />);
    const tile = /<h3[^>]*>([^<]*)<\/h3><strong[^>]*>82\/95 \(86%\)<\/strong><p[^>]*>([^<]*)<\/p>/.exec(html);
    expect(tile).not.toBeNull();
    expect(tile?.[1]).toBe(PUBLIC_RESULTS_COPY.ejectionsHeading);
    expect(tile?.[2]).toBe(fmt(PUBLIC_RESULTS_COPY.ejectionsDescription, { meetings: "151", innocent: "13" }));
    expect(tile?.[1]).toBe("Ejected players who were impostors");
    expect(tile?.[2]).toBe("Impostors / all ejected players across 151 resolved meetings. 13 innocent ejections; skips are excluded.");
    expect(html).not.toMatch(/correct ejections/i);
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
    expect(unstamped).toContain("Observation clock: unknown.");
    expect(unstamped).not.toContain("Observation clock: v1.");
  });
  it("calls each adopted rule adopted, in plain words, and leaves a default group unchanged", () => {
    // An older payload: none of the five later keys is present.
    const quiet = groupLines(OLDER);
    expect(quiet).toContain("No enabled experiments recorded. This alone does not certify the default behavior.");
    const adopted: Array<[Partial<ExperimentConfigView>, string]> = [
      [{ vent_witness_rule: "physical" }, "Vent use is seen only in the room where it happens."],
      [{ vent_entry_policy: "own_fresh_kill" }, "Impostors enter a vent only beside a body they have just killed."],
      [{ meeting_reset: "hub_with_grace" }, "After each meeting, the survivors start again from the meeting room with the bodies cleared."],
      [{ bounded_rebuttal_version: 1 }, "A player accused after already speaking gets one reply."],
      [{ report_body_handle_version: 1 }, "A body report does not give the time of death."],
      [{ ballot_kill_row_version: 1 }, "Each ballot lists the kills its voter saw a player from the other side make."],
      [{ impostor_ballot_version: 1 }, "An impostor is asked to vote as a move for its own side."],
    ];
    for (const [change, words] of adopted) {
      const lines = groupLines({ ...OLDER, ...change });
      expect(lines).toContain(`Rules adopted for the current game: ${words}`);
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
    expect(lines).toContain("Impostor policy: the built-in scripted policy. Crew policy: the built-in scripted policy. Rule settings: unknown.");
    const policy = { policy_id: "id", encoder_version: "e1", weights_sha256: "sha", anchor_policy: "anchor" };
    const recorded = renderToStaticMarkup(<PublicResultsView results={{ ...summary, provenance_groups: [{ ...group(OLDER), tactical_policy: { ...policy, method: "rule-based impostor" }, crew_tactical_policy: { ...policy, method: "rule-based crew" }, substrate_flags: {}, temporal_observation_version: 2 }] }} />);
    expect(recorded).toContain("Impostor policy: rule-based impostor. Crew policy: rule-based crew. Rule settings: recorded.");
    expect(recorded).toContain("Observation clock: v2.");
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
      "Rules adopted for the current game: Vent use is seen only in the room where it happens. Impostors enter a vent only beside a body they have just killed. After each meeting, the survivors start again from the meeting room with the bodies cleared. A player accused after already speaking gets one reply. A body report does not give the time of death. Each ballot lists the kills its voter saw a player from the other side make. An impostor is asked to vote as a move for its own side.",
      // was without the route lines, while round 2's config was the shown set's
      "Also in place: impostors in a vent wait briefly for the rooms they can see to clear before coming out, set for these recordings; a kill cooldown of 6 ticks set for these recordings; each ballot lists which changes of room stated at the meeting the doors, or the restart after a meeting, allow, set for these recordings.",
      "Impostor policy: the built-in scripted policy. Crew policy: the built-in scripted policy. Rule settings: unknown.",
      "Observation clock: unknown.",
    ]);
    expect(declared.route_lines_version).toBe(1);
  });

  it("names the route lines as set for these recordings, never adopted or experimental", () => {
    const routes = groupLines({ ...OLDER, route_lines_version: 1 });
    expect(routes).toContain("Also in place: each ballot lists which changes of room stated at the meeting the doors, or the restart after a meeting, allow, set for these recordings.");
    expect(routes.join("\n")).not.toMatch(/experiment|adopted/i);
    expect(routes).not.toContain("No enabled experiments recorded. This alone does not certify the default behavior.");
    // Beside the cooldown, after it.
    expect(groupLines({ ...OLDER, kill_cooldown_ticks: 6, route_lines_version: 1 })).toContain(
      "Also in place: a kill cooldown of 6 ticks set for these recordings; each ballot lists which changes of room stated at the meeting the doors, or the restart after a meeting, allow, set for these recordings.",
    );
    // Planted: a config without the field, or with it null, says nothing of routes.
    for (const config of [OLDER, { ...OLDER, route_lines_version: null }]) {
      const lines = groupLines(config);
      expect(lines.join("\n")).not.toContain("changes of room");
      expect(lines).toContain("No enabled experiments recorded. This alone does not certify the default behavior.");
    }
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
            else expect(adoptedLine).toBe(`Rules adopted for the current game: ${on.map(([, , words]) => words).join(" ")}`);
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
    expect(none).toContain("No worked examples for this set yet; the 9-player set has two.");
    expect(none).not.toContain("source-matched");
  });
});

/** Markup as text: tags and React's text-joining comments dropped. */
function textOf(html: string): string {
  return html.replace(/<!--[\s\S]*?-->/g, "").replace(/<[^>]*>/g, "").replaceAll("&#x27;", "'").replaceAll("&amp;", "&");
}

/** The proof row's markup, or a failure naming its absence. */
function proofRow(html: string): string {
  const match = /<section aria-label="[^"]*" data-proof-row="true"[^>]*>[\s\S]*?<\/section>/.exec(html);
  if (match === null) throw new Error("no proof row rendered");
  return match[0];
}

describe("the Results tab's proof row", () => {
  it("sits after the cases, in the body style, headed by what it counts", () => {
    const html = renderToStaticMarkup(<PublicResultsView results={summary} />);
    const row = proofRow(html);
    expect(html.indexOf("Decisions to investigate")).toBeGreaterThan(0);
    expect(html.indexOf(row)).toBeGreaterThan(html.indexOf("Decisions to investigate"));
    expect(row).toContain(">Ejected players who were impostors, with and without a vent sighting</h3>");
    // Never the old bold bordered box.
    expect(row).not.toMatch(/border-2|bg-paper-2|<strong/);
    expect(html).not.toContain("Separate direct proof from uncertain inference");
    const text = textOf(row);
    expect(text).toContain("With a vent sighting: 68/68 (100%) · Without one: 14/27 (52%)");
    expect(text).toContain("Only impostors can vent");
    expect(text).toContain("A sighting in a meeting does not show that it caused the vote");
    expect(text).toContain("these counts describe this set of recordings only");
    expect(html).not.toMatch(/by construction|ejectee|role proof/i);
  });

  it("sits after the empty state when a set publishes no case", () => {
    const html = renderToStaticMarkup(<PublicResultsView results={{ ...summary, cases: [] }} />);
    expect(html.indexOf(proofRow(html))).toBeGreaterThan(html.indexOf(PUBLIC_RESULTS_COPY.noCases));
  });

  it("reads one ejection in the singular", () => {
    const html = renderToStaticMarkup(<PublicResultsView results={{ ...summary, proof_free_ejections: 1, proof_free_correct: 0 }} />);
    expect(textOf(proofRow(html))).toContain("The 1 ejection without a sighting shows how the table decided without proof.");
    expect(html).not.toMatch(/\b1 ejections\b/);
  });
});

describe("the Results tab's case links and prose", () => {
  it("labels the meeting link and the raw file plainly, hrefs and reveal kept", () => {
    const html = renderToStaticMarkup(<PublicResultsView results={summary} />);
    const meetingLink = /<a [^>]*href="([^"]*)"[^>]*>([^<]*)<\/a>/.exec(html);
    expect(meetingLink?.[2]).toBe("Inspect the meeting (shows roles)");
    expect(meetingLink?.[1]).toContain("selectedMeeting=headless-seed-46%3Ameeting-3");
    expect(meetingLink?.[1]).toContain("evidenceId=p-9%3A29%3A3");
    expect(html).toContain('href="https://example.com/source" target="_blank" rel="noreferrer">Raw recording file</a>');
    expect(html).toContain(">Reveal case analysis (spoilers)</button>");
    expect(html).not.toContain("Pinned recording source");
  });

  it("says each recording was replayed and checked, naming the set through the set-name helper", () => {
    const text = textOf(renderToStaticMarkup(<PublicResultsView results={summary} />));
    expect(text).toContain(`Results cover all 50 games with ${setOptionLabel("9p2i")};`);
    expect(text).toContain("Each recording was replayed and checked before counting.");
    expect(text).not.toContain("The engine reconstructed");
  });
});

describe("the Results tab's provenance defaults", () => {
  const scripted = { game_ids: ["headless-seed-1"], agent_factory_kind: "scripted" as const, experiment_config: null, tactical_policy: null, crew_tactical_policy: null };
  const lines = (provenance: ReportProvenanceGroupView): string[] => {
    const html = renderToStaticMarkup(<PublicResultsView results={{ ...summary, provenance_groups: [provenance] }} />);
    const card = /aria-label="Recorded behavior groups"[^>]*>([\s\S]*?)<\/ul>/.exec(html)?.[1] ?? "";
    return [...card.matchAll(/<p>([\s\S]*?)<\/p>/g)].map((match) => textOf(match[1] ?? ""));
  };

  it("names the default policy and the standard timing, as both shown sets record them", () => {
    const shown = lines({ ...scripted, substrate_flags: { temporal_observations: false }, temporal_observation_version: null });
    expect(shown).toContain("Impostor policy: the built-in scripted policy. Crew policy: the built-in scripted policy. Rule settings: recorded.");
    expect(shown).toContain("Observation clock: the standard timing.");
    expect(shown.join("\n")).not.toContain("not recorded");
  });

  it("keeps unknown for what the record cannot say, and a recorded version or stamp as it is", () => {
    expect(lines({ ...scripted, substrate_flags: null, temporal_observation_version: null })).toContain("Observation clock: unknown.");
    expect(lines({ ...scripted, substrate_flags: { temporal_observations: true }, temporal_observation_version: null })).toContain("Observation clock: unknown.");
    expect(lines({ ...scripted, substrate_flags: { temporal_observations: true }, temporal_observation_version: 2 })).toContain("Observation clock: v2.");
    const policy = { policy_id: "id", encoder_version: "e1", weights_sha256: "sha", anchor_policy: "anchor" };
    expect(lines({ ...scripted, substrate_flags: null, temporal_observation_version: null, tactical_policy: { ...policy, method: "learned impostor" } })).toContain(
      "Impostor policy: learned impostor. Crew policy: the built-in scripted policy. Rule settings: unknown.",
    );
  });

  it("puts the prompt versions and the fingerprint under the technical identifiers", () => {
    const html = renderToStaticMarkup(<PublicResultsView results={summary} />);
    const technical = textOf(/<div data-technical-identifiers="true"[^>]*>([\s\S]*?)<\/div>/.exec(html)?.[1] ?? "");
    expect(technical).toContain("Technical identifiers, for reproduction");
    expect(technical).toContain("Prompt versions: v5.");
    expect(technical).toContain("Source fingerprint: sha256:example");
  });

  it("reads a zero cost as the flat-rate service and keeps any other figure", () => {
    const zero = textOf(renderToStaticMarkup(<PublicResultsView results={summary} />));
    expect(zero).toContain("100 input tokens · 50 output tokens · $0: a flat-rate service, so usage, not a bill.");
    const paid = textOf(renderToStaticMarkup(<PublicResultsView results={{ ...summary, reported_cost_usd: 1.5 }} />));
    expect(paid).toContain("· $1.5000 of usage, not a bill.");
    expect(paid).not.toContain("$0:");
    expect(paid).not.toContain("flat-rate");
  });
});

