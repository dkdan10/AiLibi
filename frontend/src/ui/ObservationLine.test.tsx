import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { MemoryPanel } from "../components/MemoryPanel";
import { TurnCard } from "../components/TurnCard";
import type { TaskActivityAccountView, TurnView } from "../types/api";
import { ObservationLine } from "./ObservationLine";

const activity: TaskActivityAccountView = {
  type: "task_activity", task_id: "fuel_reserves", room: "STORAGE", from_tick: 3, to_tick: 5,
};

describe("public task accounts", () => {
  it("shows an activity claim without calling it completed work", () => {
    const html = renderToStaticMarkup(<ObservationLine obs={activity} />);
    expect(html).toContain("claimed task activity");
    expect(html).toContain("fuel_reserves");
    expect(html).toContain("3–5");
    expect(html).not.toContain("completed");
    expect(html).not.toContain("impostor");
    expect(html).not.toContain("verified");
  });

  it("keeps the speaker and public source link on the actual turn card", () => {
    const turn: TurnView = { turn_id: "opaque-account", turn_index: 0, speaker: "p-3",
      turn_kind: "opening", reply_to: null, observations: [activity], claims: [],
      free_text: "I worked on fuel.", fabricated_opening: false, annotations: [] };
    const html = renderToStaticMarkup(<TurnCard turn={turn} players={[]} contradictions={[]} depth={0} meetingTick={8} />);
    expect(html).toContain("p-3");
    expect(html).toContain("claimed task activity");
    expect(html).toContain("fuel_reserves");
    expect(html).not.toContain("fabricated");
  });

  it("handles account intervals in the private panel without changing task totals", () => {
    const html = renderToStaticMarkup(<MemoryPanel memory={{ agent_id: "p-3", tick: 8,
      role: "IMPOSTOR", tasks_completed: 0, tasks_assigned: 0, observations: [
        { type: "saw_player", subject: "p-2", room: "LABS", tick: 2, co_present: [] }, activity,
      ], beliefs: [], open_contradictions: [], rendered_memory_text: "Private activity history." }}
      revealSecrets isImpostor ownKills={[]} coverTasks={[]} fellowImpostors={[]} />);
    expect(html).toContain("claimed task activity");
    expect(html.indexOf("fuel_reserves")).toBeLessThan(html.indexOf("LABS"));
    expect(html).not.toContain("Cover tasks (fabricated)");
  });
});
