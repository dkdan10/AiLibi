// The adopted list is held to its two sources, both read off disk: the
// "Adopted arms" paragraph of `docs/experiment-arms.md`, and the declared
// config of the shown 9-player set. Each source has a planted edit that turns
// the pin red, so the list cannot drift from either without a failing test.

import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import type { ExperimentConfigView } from "../types/api";
import { ADOPTED_RULES, holdsAdoptedValue } from "./adoptedRules";

const REPO_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
const ARMS_DOC = readFileSync(resolve(REPO_ROOT, "docs/experiment-arms.md"), "utf8");
const SHOWN_CONFIG: Readonly<Record<string, unknown>> = JSON.parse(
  readFileSync(resolve(REPO_ROOT, "replays/samples/9p2i/experiment-config.json"), "utf8"),
) as Record<string, unknown>;

/**
 * The `field = value` pairs the paragraph's adoption sentence lists, in order.
 *
 * Only that sentence: the same paragraph goes on to name `vent_exit_policy =
 * look_and_wait` as kept but not adopted, so the read stops where the
 * paragraph starts defining what adopted means.
 */
function adoptedPairs(doc: string): readonly string[] {
  const paragraph = /^## Adopted arms\n\n([\s\S]*?)\n\n/m.exec(doc)?.[1];
  if (paragraph === undefined) throw new Error("no Adopted arms paragraph");
  const sentence = paragraph.replace(/\s+/g, " ").split(" Adopted means ")[0] ?? "";
  return [...sentence.matchAll(/`(\w+) = (\w+)`/g)].map((match) => `${match[1] ?? ""} = ${match[2] ?? ""}`);
}

/** Why the adopted list disagrees with the paragraph or the shown set's config. */
function adoptedRuleProblems(doc: string, config: Readonly<Record<string, unknown>>): readonly string[] {
  const listed = ADOPTED_RULES.map((rule) => `${rule.field} = ${String(rule.value)}`);
  const stated = adoptedPairs(doc);
  const problems: string[] = [];
  if (listed.join(", ") !== stated.join(", ")) {
    problems.push(`the list reads ${listed.join(", ")}; the paragraph reads ${stated.join(", ")}`);
  }
  for (const rule of ADOPTED_RULES) {
    if (config[rule.field] !== rule.value) {
      problems.push(`the shown set's config holds ${rule.field} = ${String(config[rule.field])}`);
    }
  }
  return problems;
}

describe("the adopted rules", () => {
  it("are the paragraph's seven pairs, in its order, each held by the shown set's config", () => {
    expect(adoptedPairs(ARMS_DOC)).toHaveLength(7);
    expect(adoptedRuleProblems(ARMS_DOC, SHOWN_CONFIG)).toEqual([]);
    // The kept vent exit is in the config and in the paragraph, but not adopted.
    expect(SHOWN_CONFIG.vent_exit_policy).toBe("look_and_wait");
    expect(ADOPTED_RULES.map((rule) => rule.field)).not.toContain("vent_exit_policy");
    expect(ADOPTED_RULES.map((rule) => rule.field)).not.toContain("kill_cooldown_ticks");
  });

  it("fail the pin when the paragraph's value for one pair is edited (planted)", () => {
    // Edited inside the adoption sentence; the same pair also appears earlier in
    // the document, where the validation rules name it.
    const pair = "`vent_entry_policy = own_fresh_kill`, `meeting_reset = hub_with_grace`,";
    expect(ARMS_DOC.split(pair)).toHaveLength(2);
    const edited = ARMS_DOC.replace(pair, "`vent_entry_policy = own_fresh_kill`, `meeting_reset = preserve`,");
    expect(adoptedRuleProblems(edited, SHOWN_CONFIG)).toEqual([
      expect.stringContaining("meeting_reset = preserve"),
    ]);
  });

  it("fail the pin when a config copy moves one adopted field (planted)", () => {
    const moved = { ...SHOWN_CONFIG, vent_entry_policy: "any_body" };
    expect(adoptedRuleProblems(ARMS_DOC, moved)).toEqual([
      "the shown set's config holds vent_entry_policy = any_body",
    ]);
  });

  it("read only the adoption sentence, not the kept vent exit after it", () => {
    expect(adoptedPairs(ARMS_DOC)).not.toContain("vent_exit_policy = look_and_wait");
    expect(ARMS_DOC).toContain("`vent_exit_policy = look_and_wait`");
  });
});

describe("holdsAdoptedValue", () => {
  const base = { vent_exit_policy: "target_distance" } as unknown as ExperimentConfigView;
  it("is true only at the adopted value", () => {
    for (const rule of ADOPTED_RULES) {
      expect(holdsAdoptedValue({ ...base, [rule.field]: rule.value }, rule)).toBe(true);
      // A missing key is the historical default, never the adopted value.
      expect(holdsAdoptedValue(base, rule)).toBe(false);
    }
    const physical = ADOPTED_RULES[0];
    expect(holdsAdoptedValue({ ...base, vent_witness_rule: "both_rooms" }, physical)).toBe(false);
    const handle = ADOPTED_RULES[4];
    expect(handle.field).toBe("report_body_handle_version");
    expect(holdsAdoptedValue({ ...base, report_body_handle_version: null }, handle)).toBe(false);
  });
});
