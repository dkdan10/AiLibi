import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import type { ObservationReferenceView } from "../types/api";
import { ObservationClock } from "./EvidencePanel";

const reference: ObservationReferenceView = {
  observation_id: "opaque-99999", observer_id: "p-2", resolved: true,
  observation_tick: 6, scene_tick: 6, provenance: "observed",
  kind: "saw_player_move", text: "A movement", subject_id: "p-3",
  room: null, from_room: "STORAGE", to_room: "ENGINEERING",
};

describe("evidence clock boundaries", () => {
  it("uses explicit event order and position without promising a simultaneous map frame", () => {
    const html = renderToStaticMarkup(<ObservationClock observation={{ ...reference,
      source_tick: 6, observation_phase: "event", observation_order: 1,
      observer_room: "ENGINEERING", observer_in_vent: false,
    }} />);
    expect(html).toContain("During actions at tick 6");
    expect(html).toContain("observed event 2 for this agent");
    expect(html).toContain("in ENGINEERING just before this event");
    expect(html).toContain("later actions may have changed positions");
    expect(html).not.toContain("99999");
  });
  it("distinguishes pre-action snapshots from events", () => {
    const html = renderToStaticMarkup(<ObservationClock observation={{ ...reference,
      source_tick: 6, observation_phase: "snapshot", scene_tick: 5,
      observer_room: "STORAGE", observer_in_vent: false,
    }} />);
    expect(html).toContain("Before actions at tick 6");
    expect(html).toContain("Scene frame 5 shows the state before these actions");
    expect(html).not.toContain("observed event");
  });
  it("does not invent legacy phase or order", () => {
    const html = renderToStaticMarkup(<ObservationClock observation={reference} />);
    expect(html).toContain("different boundaries");
    expect(html).not.toContain("During actions");
    expect(html).not.toContain("Before actions");
  });
});
