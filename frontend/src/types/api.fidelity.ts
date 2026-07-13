// GENERATED FILE — do not edit by hand.
//
// Codegen FIDELITY gate (Task 12.2, DESIGN.md §7). A REAL served
// ReplayView payload (produced by the loader) type-checks against the
// generated `./api` types, and every discriminated union narrows
// exhaustively. `npm run tsc:check` compiles this (tsconfig includes
// `src`); it is never imported by app code, so vite does not bundle it.
//
// Regenerate with: uv run python scripts/gen_frontend_types.py

import type {
  ObservationClaimView,
  ReplayView,
  StatementClaimView,
  TickEventView,
  AccusationClaimView,
  AlibiClaimView,
  CompletedTaskObsView,
  CorroborationClaimView,
  FoundBodyObsView,
  KillEventView,
  MeetingTriggeredEventView,
  ReportBodyEventView,
  SabotageEventView,
  SawPlayerView,
  SawVentObservationView,
  TaskCompletedEventView,
  VentEventView,
  WhereaboutsClaimView,
} from "./api";

export const _fidelityReplay: ReplayView = {
  "failed_calls": [],
  "map": {
    "edges": [
      {
        "from_room_id": "CAFETERIA",
        "is_door": true,
        "to_room_id": "UPPER_HALL"
      },
      {
        "from_room_id": "UPPER_HALL",
        "is_door": true,
        "to_room_id": "ADMIN"
      },
      {
        "from_room_id": "CAFETERIA",
        "is_door": false,
        "to_room_id": "EAST_HALL"
      },
      {
        "from_room_id": "EAST_HALL",
        "is_door": true,
        "to_room_id": "ENGINEERING"
      },
      {
        "from_room_id": "ADMIN",
        "is_door": false,
        "to_room_id": "EAST_HALL"
      },
      {
        "from_room_id": "ENGINEERING",
        "is_door": true,
        "to_room_id": "REACTOR"
      },
      {
        "from_room_id": "ENGINEERING",
        "is_door": true,
        "to_room_id": "STORAGE"
      },
      {
        "from_room_id": "CAFETERIA",
        "is_door": false,
        "to_room_id": "WEST_HALL"
      },
      {
        "from_room_id": "WEST_HALL",
        "is_door": true,
        "to_room_id": "MEDBAY"
      },
      {
        "from_room_id": "ADMIN",
        "is_door": false,
        "to_room_id": "WEST_HALL"
      },
      {
        "from_room_id": "MEDBAY",
        "is_door": true,
        "to_room_id": "LABS"
      }
    ],
    "rooms": [
      {
        "id": "ADMIN",
        "name": "Admin",
        "position": {
          "x": 36.0,
          "y": 22.0
        },
        "size": {
          "height": 8.0,
          "width": 16.0
        }
      },
      {
        "id": "CAFETERIA",
        "name": "Cafeteria",
        "position": {
          "x": 36.0,
          "y": 4.0
        },
        "size": {
          "height": 10.0,
          "width": 16.0
        }
      },
      {
        "id": "EAST_HALL",
        "name": "East Hallway",
        "position": {
          "x": 56.0,
          "y": 12.0
        },
        "size": {
          "height": 14.0,
          "width": 4.0
        }
      },
      {
        "id": "ENGINEERING",
        "name": "Engineering",
        "position": {
          "x": 64.0,
          "y": 14.0
        },
        "size": {
          "height": 10.0,
          "width": 14.0
        }
      },
      {
        "id": "LABS",
        "name": "Labs",
        "position": {
          "x": 0.0,
          "y": 16.0
        },
        "size": {
          "height": 8.0,
          "width": 10.0
        }
      },
      {
        "id": "MEDBAY",
        "name": "MedBay",
        "position": {
          "x": 14.0,
          "y": 14.0
        },
        "size": {
          "height": 10.0,
          "width": 14.0
        }
      },
      {
        "id": "REACTOR",
        "name": "Reactor",
        "position": {
          "x": 82.0,
          "y": 16.0
        },
        "size": {
          "height": 8.0,
          "width": 10.0
        }
      },
      {
        "id": "STORAGE",
        "name": "Storage",
        "position": {
          "x": 64.0,
          "y": 26.0
        },
        "size": {
          "height": 6.0,
          "width": 14.0
        }
      },
      {
        "id": "UPPER_HALL",
        "name": "Upper Hall",
        "position": {
          "x": 38.0,
          "y": 16.0
        },
        "size": {
          "height": 4.0,
          "width": 12.0
        }
      },
      {
        "id": "WEST_HALL",
        "name": "West Hallway",
        "position": {
          "x": 30.0,
          "y": 12.0
        },
        "size": {
          "height": 14.0,
          "width": 4.0
        }
      }
    ],
    "vents": [
      {
        "connected_room_ids": [
          "REACTOR",
          "MEDBAY"
        ],
        "id": "ADMIN_VENT",
        "room_id": "ADMIN"
      },
      {
        "connected_room_ids": [
          "STORAGE",
          "LABS"
        ],
        "id": "ENGINEERING_VENT",
        "room_id": "ENGINEERING"
      },
      {
        "connected_room_ids": [
          "ENGINEERING",
          "MEDBAY"
        ],
        "id": "LABS_VENT",
        "room_id": "LABS"
      },
      {
        "connected_room_ids": [
          "ADMIN",
          "LABS"
        ],
        "id": "MEDBAY_VENT",
        "room_id": "MEDBAY"
      },
      {
        "connected_room_ids": [
          "STORAGE",
          "ADMIN"
        ],
        "id": "REACTOR_VENT",
        "room_id": "REACTOR"
      },
      {
        "connected_room_ids": [
          "REACTOR",
          "ENGINEERING"
        ],
        "id": "STORAGE_VENT",
        "room_id": "STORAGE"
      }
    ]
  },
  "meetings": [],
  "metadata": {
    "created_at": null,
    "game_id": "headless-seed-0",
    "meeting_count": 0,
    "prompt_versions": {},
    "seed": 0,
    "total_cost_usd": 0.0,
    "total_ticks": 3,
    "winner": "CREWMATES",
    "winner_reason": "all_tasks_complete"
  },
  "players": [
    {
      "agent_id": "p-1",
      "color": "#5DA83A",
      "display_name": "Player 1",
      "role": "CREWMATE"
    },
    {
      "agent_id": "p-2",
      "color": "#2BA45E",
      "display_name": "Player 2",
      "role": "CREWMATE"
    },
    {
      "agent_id": "p-3",
      "color": "#14A06E",
      "display_name": "Player 3",
      "role": "IMPOSTOR"
    },
    {
      "agent_id": "p-4",
      "color": "#0E9C93",
      "display_name": "Player 4",
      "role": "CREWMATE"
    }
  ],
  "ticks": [
    {
      "advantage": {
        "advantage": -0.3333333333333333,
        "crew_alive": 3,
        "impostors_alive": 1,
        "tasks_completed": 0,
        "tasks_required": 3,
        "tasks_required_total": 3
      },
      "agent_states": [
        {
          "agent_id": "p-1",
          "current_action": "IDLE",
          "is_alive": true,
          "is_venting": false,
          "room_id": "CAFETERIA",
          "task_progress": 0.0,
          "visibility": {
            "audible_events": [],
            "visible_bodies": [],
            "visible_players": [
              {
                "action": null,
                "id": "p-2",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-3",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-4",
                "room": "CAFETERIA"
              }
            ]
          }
        },
        {
          "agent_id": "p-2",
          "current_action": "IDLE",
          "is_alive": true,
          "is_venting": false,
          "room_id": "CAFETERIA",
          "task_progress": 0.0,
          "visibility": {
            "audible_events": [],
            "visible_bodies": [],
            "visible_players": [
              {
                "action": null,
                "id": "p-1",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-3",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-4",
                "room": "CAFETERIA"
              }
            ]
          }
        },
        {
          "agent_id": "p-3",
          "current_action": "IDLE",
          "is_alive": true,
          "is_venting": false,
          "room_id": "CAFETERIA",
          "task_progress": null,
          "visibility": {
            "audible_events": [],
            "visible_bodies": [],
            "visible_players": [
              {
                "action": null,
                "id": "p-1",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-2",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-4",
                "room": "CAFETERIA"
              }
            ]
          }
        },
        {
          "agent_id": "p-4",
          "current_action": "IDLE",
          "is_alive": true,
          "is_venting": false,
          "room_id": "CAFETERIA",
          "task_progress": 0.0,
          "visibility": {
            "audible_events": [],
            "visible_bodies": [],
            "visible_players": [
              {
                "action": null,
                "id": "p-1",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-2",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-3",
                "room": "CAFETERIA"
              }
            ]
          }
        }
      ],
      "bodies": [],
      "events": [],
      "sabotage": null,
      "sabotage_active": [],
      "tasks_completed_total": 0,
      "tasks_required_total": 3,
      "tick": -1
    },
    {
      "advantage": {
        "advantage": -0.3333333333333333,
        "crew_alive": 3,
        "impostors_alive": 1,
        "tasks_completed": 0,
        "tasks_required": 3,
        "tasks_required_total": 3
      },
      "agent_states": [
        {
          "agent_id": "p-1",
          "current_action": "IDLE",
          "is_alive": true,
          "is_venting": false,
          "room_id": "CAFETERIA",
          "task_progress": 0.0,
          "visibility": {
            "audible_events": [],
            "visible_bodies": [],
            "visible_players": [
              {
                "action": null,
                "id": "p-2",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-3",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-4",
                "room": "CAFETERIA"
              }
            ]
          }
        },
        {
          "agent_id": "p-2",
          "current_action": "IDLE",
          "is_alive": true,
          "is_venting": false,
          "room_id": "CAFETERIA",
          "task_progress": 0.0,
          "visibility": {
            "audible_events": [],
            "visible_bodies": [],
            "visible_players": [
              {
                "action": null,
                "id": "p-1",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-3",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-4",
                "room": "CAFETERIA"
              }
            ]
          }
        },
        {
          "agent_id": "p-3",
          "current_action": "IDLE",
          "is_alive": true,
          "is_venting": false,
          "room_id": "CAFETERIA",
          "task_progress": null,
          "visibility": {
            "audible_events": [],
            "visible_bodies": [],
            "visible_players": [
              {
                "action": null,
                "id": "p-1",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-2",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-4",
                "room": "CAFETERIA"
              }
            ]
          }
        },
        {
          "agent_id": "p-4",
          "current_action": "IDLE",
          "is_alive": true,
          "is_venting": false,
          "room_id": "CAFETERIA",
          "task_progress": 0.0,
          "visibility": {
            "audible_events": [],
            "visible_bodies": [],
            "visible_players": [
              {
                "action": null,
                "id": "p-1",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-2",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-3",
                "room": "CAFETERIA"
              }
            ]
          }
        }
      ],
      "bodies": [],
      "events": [],
      "sabotage": null,
      "sabotage_active": [],
      "tasks_completed_total": 0,
      "tasks_required_total": 3,
      "tick": 0
    },
    {
      "advantage": {
        "advantage": -0.3333333333333333,
        "crew_alive": 3,
        "impostors_alive": 1,
        "tasks_completed": 0,
        "tasks_required": 3,
        "tasks_required_total": 3
      },
      "agent_states": [
        {
          "agent_id": "p-1",
          "current_action": "IDLE",
          "is_alive": true,
          "is_venting": false,
          "room_id": "CAFETERIA",
          "task_progress": 0.0,
          "visibility": {
            "audible_events": [],
            "visible_bodies": [],
            "visible_players": [
              {
                "action": null,
                "id": "p-2",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-3",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-4",
                "room": "CAFETERIA"
              }
            ]
          }
        },
        {
          "agent_id": "p-2",
          "current_action": "IDLE",
          "is_alive": true,
          "is_venting": false,
          "room_id": "CAFETERIA",
          "task_progress": 0.0,
          "visibility": {
            "audible_events": [],
            "visible_bodies": [],
            "visible_players": [
              {
                "action": null,
                "id": "p-1",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-3",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-4",
                "room": "CAFETERIA"
              }
            ]
          }
        },
        {
          "agent_id": "p-3",
          "current_action": "IDLE",
          "is_alive": true,
          "is_venting": false,
          "room_id": "CAFETERIA",
          "task_progress": null,
          "visibility": {
            "audible_events": [],
            "visible_bodies": [],
            "visible_players": [
              {
                "action": null,
                "id": "p-1",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-2",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-4",
                "room": "CAFETERIA"
              }
            ]
          }
        },
        {
          "agent_id": "p-4",
          "current_action": "IDLE",
          "is_alive": true,
          "is_venting": false,
          "room_id": "CAFETERIA",
          "task_progress": 0.0,
          "visibility": {
            "audible_events": [],
            "visible_bodies": [],
            "visible_players": [
              {
                "action": null,
                "id": "p-1",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-2",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-3",
                "room": "CAFETERIA"
              }
            ]
          }
        }
      ],
      "bodies": [],
      "events": [],
      "sabotage": null,
      "sabotage_active": [],
      "tasks_completed_total": 0,
      "tasks_required_total": 3,
      "tick": 1
    },
    {
      "advantage": {
        "advantage": -0.3333333333333333,
        "crew_alive": 3,
        "impostors_alive": 1,
        "tasks_completed": 0,
        "tasks_required": 3,
        "tasks_required_total": 3
      },
      "agent_states": [
        {
          "agent_id": "p-1",
          "current_action": "IDLE",
          "is_alive": true,
          "is_venting": false,
          "room_id": "CAFETERIA",
          "task_progress": 0.0,
          "visibility": {
            "audible_events": [],
            "visible_bodies": [],
            "visible_players": [
              {
                "action": null,
                "id": "p-2",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-3",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-4",
                "room": "CAFETERIA"
              }
            ]
          }
        },
        {
          "agent_id": "p-2",
          "current_action": "IDLE",
          "is_alive": true,
          "is_venting": false,
          "room_id": "CAFETERIA",
          "task_progress": 0.0,
          "visibility": {
            "audible_events": [],
            "visible_bodies": [],
            "visible_players": [
              {
                "action": null,
                "id": "p-1",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-3",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-4",
                "room": "CAFETERIA"
              }
            ]
          }
        },
        {
          "agent_id": "p-3",
          "current_action": "IDLE",
          "is_alive": true,
          "is_venting": false,
          "room_id": "CAFETERIA",
          "task_progress": null,
          "visibility": {
            "audible_events": [],
            "visible_bodies": [],
            "visible_players": [
              {
                "action": null,
                "id": "p-1",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-2",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-4",
                "room": "CAFETERIA"
              }
            ]
          }
        },
        {
          "agent_id": "p-4",
          "current_action": "IDLE",
          "is_alive": true,
          "is_venting": false,
          "room_id": "CAFETERIA",
          "task_progress": 0.0,
          "visibility": {
            "audible_events": [],
            "visible_bodies": [],
            "visible_players": [
              {
                "action": null,
                "id": "p-1",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-2",
                "room": "CAFETERIA"
              },
              {
                "action": null,
                "id": "p-3",
                "room": "CAFETERIA"
              }
            ]
          }
        }
      ],
      "bodies": [],
      "events": [],
      "sabotage": null,
      "sabotage_active": [],
      "tasks_completed_total": 0,
      "tasks_required_total": 3,
      "tick": 2
    }
  ],
  "viewModelVersion": "1"
};
void _fidelityReplay;

// Exhaustive narrowing of TickEventView: each discriminant resolves to its
// member (the `satisfies`), and an unhandled member is a compile error
// (the `never` default) — the codegen's discriminated-union fidelity.
export function _narrow_TickEventView(e: TickEventView): TickEventView {
  switch (e.type) {
    case "kill":
      return e satisfies KillEventView;
    case "report_body":
      return e satisfies ReportBodyEventView;
    case "sabotage":
      return e satisfies SabotageEventView;
    case "task_completed":
      return e satisfies TaskCompletedEventView;
    case "meeting_triggered":
      return e satisfies MeetingTriggeredEventView;
    case "vent":
      return e satisfies VentEventView;
    default: {
      const _exhaustive: never = e;
      return _exhaustive;
    }
  }
}

// Exhaustive narrowing of ObservationClaimView: each discriminant resolves to its
// member (the `satisfies`), and an unhandled member is a compile error
// (the `never` default) — the codegen's discriminated-union fidelity.
export function _narrow_ObservationClaimView(e: ObservationClaimView): ObservationClaimView {
  switch (e.type) {
    case "saw_player":
      return e satisfies SawPlayerView;
    case "completed_task":
      return e satisfies CompletedTaskObsView;
    case "found_body":
      return e satisfies FoundBodyObsView;
    case "saw_vent":
      return e satisfies SawVentObservationView;
    case "whereabouts":
      return e satisfies WhereaboutsClaimView;
    default: {
      const _exhaustive: never = e;
      return _exhaustive;
    }
  }
}

// Exhaustive narrowing of StatementClaimView: each discriminant resolves to its
// member (the `satisfies`), and an unhandled member is a compile error
// (the `never` default) — the codegen's discriminated-union fidelity.
export function _narrow_StatementClaimView(e: StatementClaimView): StatementClaimView {
  switch (e.type) {
    case "alibi":
      return e satisfies AlibiClaimView;
    case "accusation":
      return e satisfies AccusationClaimView;
    case "corroboration":
      return e satisfies CorroborationClaimView;
    default: {
      const _exhaustive: never = e;
      return _exhaustive;
    }
  }
}
