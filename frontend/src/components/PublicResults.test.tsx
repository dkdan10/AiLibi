import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { PublicResultsView } from "./PublicResults";
import type { ExperimentConfigView, PublicResultsView as Summary } from "../types/api";

const summary: Summary = { format_version: 1, set_name: "9p2i", source_fingerprint: "sha256:example", recorded_from: "2026-08-30", recorded_until: "2026-08-30", models: ["recorded-model"], prompt_versions: ["v5"], source_url: "https://example.com/source", games: 50, completed: 48, aborted: 1, tick_limited: 1, unfinished: 0, crew_wins: 35, impostor_wins: 13, task_wins: 0, meetings: 151, ejections: 95, impostor_ejections: 82, innocent_ejections: 13, proof_backed_ejections: 68, proof_backed_correct: 68, proof_free_ejections: 27, proof_free_correct: 14, reported_cost_usd: 0, input_tokens: 100, output_tokens: 50, cases: [{ case_id: "example", title: "A disputed route", setup: "Investigate the sighting.", explanation: "HIDDEN OUTCOME ROLE", game_id: "headless-seed-46", meeting_id: "headless-seed-46:meeting-3", meeting_tick: 31, observer_id: "p-9", turn_id: "turn-1", observation_id: "p-9:29:3", source_sha256: "hash", source_url: "https://example.com/source", classification: "unsupported" }] };

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
  it("names each later experiment in plain words and leaves a default group unchanged", () => {
    const base = { game_ids: ["headless-seed-1"], agent_factory_kind: "experimental" as const, substrate_flags: null, tactical_policy: null, crew_tactical_policy: null, temporal_observation_version: null };
    // An older payload: none of the five later keys is present.
    const older: ExperimentConfigView = { format_version: 1, redistribution_policy: "lowest_id", meeting_reset: "preserve", crew_idle_policy: "hub_wait", vent_exit_policy: "target_distance", post_meeting_retarget: false, self_report: false, sabotage_threshold: "six_sevenths", evidence_reasoning_version: null, bounded_rebuttal_version: null, public_account_version: null, attributed_testimony_version: null };
    const quiet = renderToStaticMarkup(<PublicResultsView results={{ ...summary, provenance_groups: [{ ...base, experiment_config: older }] }} />);
    expect(quiet).toContain("No enabled experiments recorded. This alone does not certify the default behavior.");
    const phrases: Array<[Partial<ExperimentConfigView>, string]> = [
      [{ vent_witness_rule: "physical" }, "vent use seen only in the room where it happens"],
      [{ report_body_handle_version: 1 }, "body reports without the time of death"],
      [{ ballot_kill_row_version: 1 }, "witnessed kills listed on the voter&#x27;s ballot"],
      [{ impostor_ballot_version: 1 }, "impostor ballots cast by strategy"],
      [{ vent_entry_policy: "own_fresh_kill" }, "experimental movement or action policies"],
      [{ vent_exit_policy: "look_and_wait" }, "experimental movement or action policies"],
    ];
    for (const [change, phrase] of phrases) {
      const html = renderToStaticMarkup(<PublicResultsView results={{ ...summary, provenance_groups: [{ ...base, experiment_config: { ...older, ...change } }] }} />);
      expect(html).toContain(`Recorded experiments: ${phrase}.`);
    }
    const defaults: ExperimentConfigView = { ...older, vent_witness_rule: "both_rooms", vent_entry_policy: "any_body", report_body_handle_version: null, ballot_kill_row_version: null, impostor_ballot_version: null };
    const spelled = renderToStaticMarkup(<PublicResultsView results={{ ...summary, provenance_groups: [{ ...base, experiment_config: defaults }] }} />);
    expect(spelled).toContain("No enabled experiments recorded. This alone does not certify the default behavior.");
  });
});
