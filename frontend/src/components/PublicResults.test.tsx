import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { PublicResultsView } from "./PublicResults";
import type { PublicResultsView as Summary } from "../types/api";

const summary: Summary = { format_version: 1, set_name: "9p2i", source_fingerprint: "sha256:example", recorded_from: "2026-08-30", recorded_until: "2026-08-30", models: ["recorded-model"], prompt_versions: ["v5"], source_url: "https://example.com/source", games: 50, completed: 48, aborted: 1, tick_limited: 1, unfinished: 0, crew_wins: 35, impostor_wins: 13, task_wins: 0, meetings: 151, ejections: 95, impostor_ejections: 82, innocent_ejections: 13, proof_backed_ejections: 68, proof_backed_correct: 68, proof_free_ejections: 27, proof_free_correct: 14, reported_cost_usd: 0, input_tokens: 100, output_tokens: 50, cases: [{ case_id: "example", title: "A disputed route", setup: "Investigate the sighting.", explanation: "HIDDEN OUTCOME ROLE", game_id: "headless-seed-46", meeting_id: "headless-seed-46:meeting-3", meeting_tick: 31, observer_id: "p-9", turn_id: "turn-1", observation_id: "p-9:29:3", source_sha256: "hash", source_url: "https://example.com/source", classification: "unsupported" }] };

describe("public result interpretation", () => {
  it("uses completed outcomes for win denominator, distinct evidence groups and source links", () => {
    const html = renderToStaticMarkup(<PublicResultsView results={summary} />);
    expect(html).toContain("35/48");
    expect(html).toContain("68/68");
    expect(html).toContain("14/27");
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
});
