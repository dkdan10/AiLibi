import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import type { AgentMemoryView } from "../types/api";
import { MemoryPanel } from "./MemoryPanel";

const memory: AgentMemoryView = {
  agent_id: "p-2", tick: 9, role: "CREWMATE", tasks_completed: 0,
  tasks_assigned: 2, observations: [], beliefs: [], open_contradictions: [],
  rendered_memory_text: "ordinary memory",
  investigation_plan: {
    decision_tick: 8, target_id: "missing-player", source_observation_id: "private-source",
    source_tick: 3, last_known_room: "last-seen-room", started_tick: 7,
    expires_tick: 13, visited_rooms: [],
  },
};

function render(revealSecrets: boolean) {
  return renderToStaticMarkup(<MemoryPanel memory={memory} revealSecrets={revealSecrets}
    isImpostor={false} ownKills={[]} coverTasks={[]} fellowImpostors={[]} />);
}

describe("search intentions", () => {
  it("states an actual plan separately from later evidence", () => {
    const html = render(true);
    expect(html).toContain("missing-player");
    expect(html).toContain("last-seen-room");
    expect(html).toContain("This is a plan, not a sighting");
    expect(html).toContain("Finding someone later does not confirm where they were earlier");
    expect(html).not.toContain("private-source");
  });

  it("does not expose another observer's intention through their fog", () => {
    const html = render(false);
    expect(html).not.toContain("Search intention");
    expect(html).not.toContain("missing-player");
    expect(html).not.toContain("last-seen-room");
    expect(html).not.toContain("private-source");
  });

  it("names the hidden memory's way in as the controls do", () => {
    const html = render(false);
    expect(html).toContain(
      "Raw rendered memory is hidden in another player&#x27;s view: it holds this player&#x27;s role and private memory. Switch to Omniscient, or use “See as p-2”, to read it.",
    );
    expect(html).not.toMatch(/\bfog\b|\blens\b/i);
    expect(render(true)).not.toContain("Raw rendered memory is hidden");
    const other = renderToStaticMarkup(<MemoryPanel memory={{ ...memory, agent_id: "p-5" }}
      revealSecrets={false} isImpostor={false} ownKills={[]} coverTasks={[]} fellowImpostors={[]} />);
    expect(other).toContain("use “See as p-5”, to read it.");
  });
});
