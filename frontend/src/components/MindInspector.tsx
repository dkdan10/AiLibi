// MindInspector — the per-agent mind inspector (Task 12.8;
// design/phase-12/stage-1-design.md §3.5, slice 6). Rebuilds the mind slot the
// App.tsx workspace mounts via <ThoughtStream/>: pick an agent, then read their
// reasoning across five tabs —
//   • Belief    — this agent's suspicion / trust of each other player, plus the
//                 Thought → Action → Observation reasoning trail for the meeting
//                 (the per-agent DETAIL, complementary to 12.6's cross-agent
//                 matrix, not a duplicate);
//   • Prompt    — `LLMCallView.prompt_text`, the exact text the LLM saw (mono);
//   • Response  — `LLMCallView.response_text` (mono);
//   • Memory    — the `AgentMemoryView` episodic feed (MemoryPanel);
//   • Flags     — the contradictions / markers affecting this agent.
//
// "Show what they saw" drives the store (`setPerspective(agent)` + `selectAgent`)
// so the 12.5 map fogs to that agent — no map edit, the map already reacts.
//
// FIREWALL (the brief's Omniscient-gating rule). The impostor extras —
// `fellow_impostor_ids`, the `own_kill` line, the fabricated cover-task label —
// derive from the omniscient ground truth (roster roles → fellow impostors;
// `KillEventView` → own kills) and are gated on **Omniscient OR when the
// perspective lens IS the inspected agent itself**. An impostor viewing its own
// mind is its own knowledge, not a leak; the secrets disappear ONLY when
// inspecting an impostor through a DIFFERENT agent's eyes (the real leak). The
// ground-truth ROLE reveal rides the same gate.

import { useEffect, useRef, useState } from "react";
import type { KeyboardEvent, ReactNode } from "react";

import { useReplayStore } from "../store/replayStore";
import type { Perspective } from "../lib/playback";
import { tokens, suspicionBucketOf, type SuspicionBucket } from "../tokens";
import { EmptyState } from "../ui/EmptyState";
import { PlayerSwatch } from "../ui/PlayerSwatch";
import type {
  AgentMemoryView,
  BeliefEntryView,
  CompletedTaskObsView,
  KillEventView,
  LLMCallView,
  MeetingView as MeetingViewDTO,
  PlayerView,
  StatementClaimView,
  TurnView,
} from "../types/api";
import { AgentSelector } from "./AgentSelector";
import { heatColor } from "./BeliefCell";
import { ContradictionBadge } from "./ContradictionBadge";
import { LLMCallCard } from "./LLMCallCard";
import { MemoryPanel } from "./MemoryPanel";

type MindTab = "belief" | "prompt" | "response" | "memory" | "flags";

const TABS: ReadonlyArray<{ id: MindTab; label: string }> = [
  { id: "belief", label: "Belief" },
  { id: "prompt", label: "Prompt" },
  { id: "response", label: "Response" },
  { id: "memory", label: "Memory" },
  { id: "flags", label: "Flags" },
];

const BUCKET_LABEL: Record<SuspicionBucket, string> = {
  low: "Low",
  med: "Med",
  high: "High",
};

// ── Thought → Action → Observation trail ────────────────────────────────────
// Synthesised from the agent's role in the meeting: each spoken turn yields a
// Thought (its free text) then an Action (its structured claims); the agent's
// ballot is the terminal Action; the meeting outcome is the closing Observation.

type TrailKind = "thought" | "action" | "observation";

interface TrailStep {
  kind: TrailKind;
  text: string;
}

const TRAIL_STYLE: Record<TrailKind, { label: string; color: string }> = {
  thought: { label: "Thought", color: tokens.trust.strong },
  action: { label: "Action", color: tokens.distrust.strong },
  observation: { label: "Observation", color: tokens.ink[700] },
};

function claimText(claim: StatementClaimView): string {
  switch (claim.type) {
    case "accusation":
      return `accused ${claim.against} (conf ${claim.confidence.toFixed(2)}) — ${claim.reason}`;
    case "alibi":
      return `alibi for ${claim.subject}: ${claim.room}, ticks ${claim.from_tick}–${claim.to_tick}`;
    case "corroboration":
      return `corroborated ${claim.supports} on tick ${claim.on_tick} — ${claim.reason}`;
  }
}

function buildTrail(
  meeting: MeetingViewDTO | undefined,
  agentId: string,
): TrailStep[] {
  if (meeting === undefined) {
    return [];
  }
  const steps: TrailStep[] = [];
  const turns: TurnView[] = meeting.turns
    .filter((turn) => turn.speaker === agentId)
    .sort((a, b) => a.turn_index - b.turn_index);

  for (const turn of turns) {
    if (turn.free_text.trim() !== "") {
      steps.push({ kind: "thought", text: turn.free_text });
    }
    for (const claim of turn.claims) {
      steps.push({ kind: "action", text: claimText(claim) });
    }
  }

  const ballot = meeting.ballots.find((b) => b.voter === agentId);
  if (ballot !== undefined) {
    if (ballot.rationale_text_clean.trim() !== "") {
      steps.push({ kind: "thought", text: ballot.rationale_text_clean });
    }
    const target =
      ballot.target === "SKIP" ? "voted to skip" : `voted to eject ${ballot.target}`;
    steps.push({
      kind: "action",
      text: `${target} (conf ${ballot.confidence.toFixed(2)})`,
    });
  }

  const ejected =
    meeting.outcome === "EJECTED" && meeting.ejected_player_id !== null
      ? `${meeting.ejected_player_id} ejected`
      : "no one ejected";
  steps.push({ kind: "observation", text: `Meeting ${meeting.outcome.toLowerCase()} — ${ejected}` });

  return steps;
}

// An impostor's fabricated cover tasks are the `completed_task` observations it
// states in the meeting — its alibi (api/replay_loader `_observation_claim_view`
// projects turn observations, the only place this type is reachable: episodic
// memory never mints a `completed_task` for an impostor, `agents/memory/store`).
// These are the "fake cover tasks" the brief asks us to label FABRICATED.
function coverTasksOf(
  meeting: MeetingViewDTO | undefined,
  agentId: string,
): CompletedTaskObsView[] {
  const cover: CompletedTaskObsView[] = [];
  for (const turn of meeting?.turns ?? []) {
    if (turn.speaker !== agentId) {
      continue;
    }
    for (const obs of turn.observations) {
      if (obs.type === "completed_task") {
        cover.push(obs);
      }
    }
  }
  return cover;
}

function ReasoningTrail({ steps }: { steps: TrailStep[] }) {
  if (steps.length === 0) {
    return (
      <p className="text-xs italic text-ink-400">
        No recorded decisions for this agent in this meeting.
      </p>
    );
  }
  return (
    <ol className="space-y-2">
      {steps.map((step, index) => {
        const style = TRAIL_STYLE[step.kind];
        return (
          <li key={index} className="flex gap-2">
            <span
              className="mt-0.5 inline-flex h-fit shrink-0 items-center rounded-pill border-2 border-ink-900 px-2 py-0.5 font-mono text-[9px] font-bold uppercase tracking-wide text-paper-0"
              style={{ background: style.color }}
            >
              {style.label}
            </span>
            <span className="min-w-0 break-words text-sm leading-snug text-ink-900">
              {step.text}
            </span>
          </li>
        );
      })}
    </ol>
  );
}

// ── Belief tab ──────────────────────────────────────────────────────────────

function BeliefBar({ belief }: { belief: BeliefEntryView }) {
  const suspicion = Math.max(0, Math.min(1, belief.suspicion));
  const pct = Math.round(suspicion * 100);
  const bucket = suspicionBucketOf(suspicion);
  return (
    <div className="flex items-center gap-2">
      <span className="w-12 shrink-0 truncate font-mono text-xs text-ink-900">
        {belief.subject}
      </span>
      <div
        role="meter"
        aria-valuenow={suspicion}
        aria-valuemin={0}
        aria-valuemax={1}
        aria-label={`suspicion of ${belief.subject}: ${BUCKET_LABEL[bucket]}`}
        className="h-2.5 flex-1 overflow-hidden rounded-pill border border-ink-300 bg-paper-0"
      >
        <div
          className="h-full rounded-pill"
          style={{ width: `${pct}%`, background: heatColor(suspicion) }}
        />
      </div>
      <span className="w-8 shrink-0 text-right font-mono text-[10px] font-semibold uppercase text-ink-500">
        {BUCKET_LABEL[bucket]}
      </span>
      <span
        title={`confidence ${belief.confidence.toFixed(2)} · snapshot tick ${belief.snapshot_tick}`}
        className="shrink-0 rounded-pill border border-ink-300 bg-paper-0 px-1.5 py-0.5 font-mono text-[10px] text-ink-700"
      >
        conf {belief.confidence.toFixed(2)}
      </span>
    </div>
  );
}

function BeliefTab({
  memory,
  trail,
}: {
  memory: AgentMemoryView;
  trail: TrailStep[];
}) {
  return (
    <div className="space-y-5">
      <section>
        <TabHeading>Suspicion / trust ({memory.beliefs.length})</TabHeading>
        {memory.beliefs.length === 0 ? (
          <p className="text-xs italic text-ink-400">
            No beliefs formed yet (not 0% — this agent simply holds no belief).
          </p>
        ) : (
          <div className="space-y-1.5">
            {memory.beliefs.map((belief) => (
              <BeliefBar key={belief.subject} belief={belief} />
            ))}
          </div>
        )}
      </section>
      <section>
        <TabHeading>Thought → Action → Observation</TabHeading>
        <ReasoningTrail steps={trail} />
      </section>
    </div>
  );
}

// ── shared bits ─────────────────────────────────────────────────────────────

function TabHeading({ children }: { children: ReactNode }) {
  return (
    <h4 className="mb-2 font-mono text-[10px] font-semibold uppercase tracking-wide text-ink-500">
      {children}
    </h4>
  );
}

function LLMCallList({
  calls,
  hasUnattributed,
  field,
}: {
  calls: LLMCallView[];
  hasUnattributed: boolean;
  field: "prompt" | "response";
}) {
  if (calls.length === 0) {
    if (hasUnattributed) {
      return (
        <p
          className="rounded-md border-2 border-ink-900 px-3 py-2 text-xs text-ink-900"
          style={{ background: tokens.paper[2] }}
        >
          Older replay — per-call agent attribution unavailable.
        </p>
      );
    }
    return (
      <p className="text-xs italic text-ink-400">
        No LLM calls recorded for this agent in this meeting.
      </p>
    );
  }
  return (
    <div className="space-y-3">
      {calls.map((call, index) => (
        <LLMCallCard
          key={`${call.prompt_template_id}#${index}`}
          call={call}
          field={field}
        />
      ))}
    </div>
  );
}

function MemoryGate({
  memory,
  memoryError,
  children,
}: {
  memory: AgentMemoryView | undefined;
  memoryError: string | null;
  children: (memory: AgentMemoryView) => ReactNode;
}) {
  if (memory === undefined) {
    if (memoryError !== null) {
      return (
        <p
          className="rounded-md border-2 border-ink-900 px-3 py-2 text-sm text-paper-0"
          style={{ background: tokens.kill }}
        >
          Failed to load memory: {memoryError}
        </p>
      );
    }
    return (
      <div className="flex items-center gap-2 py-4 text-sm text-ink-500">
        <span
          aria-hidden
          className="h-4 w-4 animate-spin rounded-full border-2 border-ink-200 border-t-ink-700"
        />
        Loading memory…
      </div>
    );
  }
  return <>{children(memory)}</>;
}

// ── presentational panel (Storybook drives this directly) ───────────────────

export interface MindInspectorPanelProps {
  players: PlayerView[];
  selectedAgentId: string | null;
  meeting: MeetingViewDTO | undefined;
  memory: AgentMemoryView | undefined;
  memoryError: string | null;
  isAlive: boolean;
  ownKills: KillEventView[];
  coverTasks: CompletedTaskObsView[];
  perspective: Perspective;
  // An agent is selected but has no meeting at or before the current tick: show
  // the honest "no deliberation yet" state instead of empty/loading tabs (§3.5).
  noMeetingYet?: boolean;
  // Active tab — optionally controlled (the connected wrapper drives it so it can
  // lazy-fetch the meeting bodies only when Prompt / Response is open). Storybook
  // omits both and the panel falls back to its own state.
  tab?: MindTab;
  onTab?: (tab: MindTab) => void;
  onSelectAgent: (agentId: string) => void;
  onShowWhatTheySaw: (agentId: string) => void;
}

export function MindInspectorPanel({
  players,
  selectedAgentId,
  meeting,
  memory,
  memoryError,
  isAlive,
  ownKills,
  coverTasks,
  perspective,
  noMeetingYet = false,
  tab: tabProp,
  onTab: onTabProp,
  onSelectAgent,
  onShowWhatTheySaw,
}: MindInspectorPanelProps) {
  const [tabState, setTabState] = useState<MindTab>("belief");
  const tab = tabProp ?? tabState;
  const onTab = onTabProp ?? setTabState;

  const inspected =
    selectedAgentId === null
      ? undefined
      : players.find((p) => p.agent_id === selectedAgentId);

  return (
    <div className="flex flex-col gap-3">
      <AgentSelector
        players={players}
        selectedAgentId={selectedAgentId}
        onSelect={onSelectAgent}
      />

      {inspected === undefined ? (
        <EmptyState title="Open a mind" className="mt-1">
          Pick an agent above — or click any token on the map or roster — to read
          their belief, prompt, response, memory, and flags. Ground truth renders
          solid; an agent's belief renders ghosted.
        </EmptyState>
      ) : (
        <InspectedAgent
          inspected={inspected}
          players={players}
          meeting={meeting}
          memory={memory}
          memoryError={memoryError}
          isAlive={isAlive}
          ownKills={ownKills}
          coverTasks={coverTasks}
          perspective={perspective}
          noMeetingYet={noMeetingYet}
          tab={tab}
          onTab={onTab}
          onShowWhatTheySaw={onShowWhatTheySaw}
        />
      )}
    </div>
  );
}

function InspectedAgent({
  inspected,
  players,
  meeting,
  memory,
  memoryError,
  isAlive,
  ownKills,
  coverTasks,
  perspective,
  noMeetingYet,
  tab,
  onTab,
  onShowWhatTheySaw,
}: {
  inspected: PlayerView;
  players: PlayerView[];
  meeting: MeetingViewDTO | undefined;
  memory: AgentMemoryView | undefined;
  memoryError: string | null;
  isAlive: boolean;
  ownKills: KillEventView[];
  coverTasks: CompletedTaskObsView[];
  perspective: Perspective;
  noMeetingYet: boolean;
  tab: MindTab;
  onTab: (tab: MindTab) => void;
  onShowWhatTheySaw: (agentId: string) => void;
}) {
  const agentId = inspected.agent_id;
  const isImpostor = inspected.role === "IMPOSTOR";
  const omniscient = perspective.mode === "omniscient";
  const lensIsSelf = perspective.mode === "agent" && perspective.agentId === agentId;
  // FIREWALL: impostor secrets + the role reveal show in Omniscient OR when the
  // lens IS this agent (its own knowledge); they vanish through a different
  // agent's eyes (the real leak).
  const revealSecrets = omniscient || lensIsSelf;

  const fellowImpostors = players.filter(
    (p) => p.role === "IMPOSTOR" && p.agent_id !== agentId,
  );
  const calls = (meeting?.llm_calls ?? []).filter((c) => c.agent_id === agentId);
  const hasUnattributed = (meeting?.llm_calls ?? []).some((c) => c.agent_id === null);
  const trail = buildTrail(meeting, agentId);

  // Roving tabindex (Task 12.13 a11y; WAI-ARIA tabs pattern): only the active tab
  // is in the tab order; Left/Right (and Up/Down) move + activate, Home/End jump
  // to the ends. Activation follows focus, matching the click behaviour.
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);
  const onTabKeyDown = (
    event: KeyboardEvent<HTMLButtonElement>,
    index: number,
  ): void => {
    const count = TABS.length;
    let next = index;
    switch (event.key) {
      case "ArrowRight":
      case "ArrowDown":
        next = (index + 1) % count;
        break;
      case "ArrowLeft":
      case "ArrowUp":
        next = (index - 1 + count) % count;
        break;
      case "Home":
        next = 0;
        break;
      case "End":
        next = count - 1;
        break;
      default:
        return;
    }
    event.preventDefault();
    const target = TABS[next];
    if (target !== undefined) {
      onTab(target.id);
      tabRefs.current[next]?.focus();
    }
  };

  return (
    <div className="flex flex-col gap-3">
      <header className="flex flex-wrap items-center gap-2 rounded-md border-2 border-ink-900 bg-paper-0 px-3 py-2 shadow-chrome-1">
        <PlayerSwatch color={inspected.color} size="md" />
        <span className="font-semibold text-ink-900">{inspected.display_name}</span>
        <span className="font-mono text-3xs text-ink-500">{agentId}</span>

        {/* FIREWALL: alive/dead is ground truth — an agent may not know a hidden
            death — so the chip rides the same Omniscient-or-self gate (matching
            the fogged roster rail, which also hides per-player liveness). */}
        {revealSecrets && !isAlive && (
          <span
            className="inline-flex items-center gap-1 rounded-pill border-2 border-ink-900 px-2 py-0.5 font-mono text-[10px] font-bold uppercase tracking-wide"
            style={{ background: tokens.paper[2], color: tokens.ink[500] }}
          >
            <span aria-hidden>✕</span> dead
          </span>
        )}

        {revealSecrets ? (
          <span
            className="inline-flex items-center rounded-pill border-2 border-ink-900 px-2 py-0.5 font-mono text-[10px] font-bold uppercase tracking-wide"
            style={
              isImpostor
                ? { background: tokens.contradiction, color: tokens.paper[0] }
                : { background: tokens.paper[2], color: tokens.ink[900] }
            }
          >
            {inspected.role}
          </span>
        ) : (
          <span
            title="Role is hidden through another agent's fog (firewall)."
            className="inline-flex items-center rounded-pill border border-dashed border-ink-300 px-2 py-0.5 font-mono text-3xs uppercase tracking-wide text-ink-500"
          >
            role hidden
          </span>
        )}

        <button
          type="button"
          aria-pressed={lensIsSelf}
          onClick={() => {
            onShowWhatTheySaw(agentId);
          }}
          className={
            "ml-auto rounded-md border-2 border-ink-900 px-2.5 py-1 text-xs font-medium transition-colors " +
            (lensIsSelf
              ? "bg-ink-900 text-paper-0"
              : "bg-paper-0 text-ink-900 hover:bg-paper-2")
          }
        >
          {lensIsSelf ? "Seeing what they saw ✓" : "Show what they saw"}
        </button>
      </header>

      {noMeetingYet ? (
        // Agent selected from the map/roster, but no meeting at or before this
        // tick. Honest empty state — never fabricate between-meeting LLM data.
        <EmptyState title="No deliberation yet">
          {inspected.display_name} hasn’t been in a meeting at or before this tick.
          Belief, prompt, response, memory, and flags appear after their first
          meeting — scrub forward to a meeting to read this mind.
        </EmptyState>
      ) : (
        <>
          {/* FIREWALL — PER-FIELD, not whole-body (the inspector and the map lens
              are separate controls; a spectator may inspect one agent's mind while
              the map stays fogged to another for comparison). The task contract
              gates only the ground-truth tells that leak alignment/secrets through
              a DIFFERENT agent's fog: the role chip + dead chip (header), the
              impostor extras + the task tally (Memory), and the VERBATIM prompt /
              response / raw rendered-memory (which embed the `Your role` block +
              the impostor self-channel). The PUBLIC / non-role-revealing tabs stay
              inspectable: Belief (suspicion + the reasoning trail, both derived
              from meeting speech everyone heard), the episodic observation feed,
              and Flags. */}
          <div
            role="tablist"
            aria-label="Mind inspector tabs"
            className="flex flex-wrap gap-1"
          >
            {TABS.map(({ id, label }, index) => {
              const active = id === tab;
              return (
                <button
                  key={id}
                  ref={(el) => {
                    tabRefs.current[index] = el;
                  }}
                  type="button"
                  role="tab"
                  id={`mind-tab-${id}`}
                  aria-selected={active}
                  aria-controls="mind-tabpanel"
                  tabIndex={active ? 0 : -1}
                  onClick={() => {
                    onTab(id);
                  }}
                  onKeyDown={(event) => {
                    onTabKeyDown(event, index);
                  }}
                  className={
                    "rounded-md border-2 px-2.5 py-1 text-xs font-semibold transition-colors " +
                    (active
                      ? "border-ink-900 bg-ink-900 text-paper-0"
                      : "border-ink-300 bg-paper-1 text-ink-700 hover:border-ink-900")
                  }
                >
                  {label}
                </button>
              );
            })}
          </div>

          <div
            role="tabpanel"
            id="mind-tabpanel"
            aria-labelledby={`mind-tab-${tab}`}
            tabIndex={0}
            className="min-h-[6rem] focus-visible:outline focus-visible:outline-2 focus-visible:outline-ink-900"
          >
            {tab === "belief" && (
              <MemoryGate memory={memory} memoryError={memoryError}>
                {(m) => <BeliefTab memory={m} trail={trail} />}
              </MemoryGate>
            )}

            {tab === "prompt" &&
              (revealSecrets ? (
                <LLMCallList
                  calls={calls}
                  hasUnattributed={hasUnattributed}
                  field="prompt"
                />
              ) : (
                <RedactedVerbatim field="prompt" />
              ))}

            {tab === "response" &&
              (revealSecrets ? (
                <LLMCallList
                  calls={calls}
                  hasUnattributed={hasUnattributed}
                  field="response"
                />
              ) : (
                <RedactedVerbatim field="response" />
              ))}

            {tab === "memory" && (
              <MemoryGate memory={memory} memoryError={memoryError}>
                {(m) => (
                  <MemoryPanel
                    memory={m}
                    revealSecrets={revealSecrets}
                    isImpostor={isImpostor}
                    ownKills={ownKills}
                    coverTasks={coverTasks}
                    fellowImpostors={fellowImpostors}
                  />
                )}
              </MemoryGate>
            )}

            {tab === "flags" && (
              <MemoryGate memory={memory} memoryError={memoryError}>
                {(m) => <FlagsTab memory={m} />}
              </MemoryGate>
            )}
          </div>
        </>
      )}
    </div>
  );
}

// Shown in place of the VERBATIM prompt / response when the inspected agent is
// viewed through a DIFFERENT agent's fog. The raw LLM I/O carries the agent's
// `Your role` memory block + (for an impostor) the fellow-impostor / own-kill
// self-channel, so it rides the same Omniscient-or-self gate as the other tells.
function RedactedVerbatim({ field }: { field: "prompt" | "response" }) {
  return (
    <p
      className="rounded-md border-2 border-dashed border-ink-300 px-3 py-3 text-xs text-ink-500"
      style={{ background: tokens.paper[2] }}
    >
      The raw {field} is hidden through another agent's fog — it embeds this
      agent's role and private rendered memory. Switch to Omniscient, or view this
      agent through its own lens (“Show what they saw”), to read it verbatim.
    </p>
  );
}

function FlagsTab({ memory }: { memory: AgentMemoryView }) {
  const flags = memory.open_contradictions;
  return (
    <section>
      <TabHeading>Flags affecting this agent ({flags.length})</TabHeading>
      {flags.length === 0 ? (
        <p className="text-xs italic text-ink-400">No contradictions or markers.</p>
      ) : (
        <ul className="space-y-2">
          {flags.map((flag) => (
            <li
              key={flag.contradiction_id}
              className="flex flex-wrap items-center gap-2 text-sm text-ink-900"
            >
              <ContradictionBadge contradiction={flag} />
              <span className="min-w-0 break-words">{flag.description}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

// ── connected wrapper (mounted by ThoughtStream) ────────────────────────────

// Scan the recorded ticks for this agent's kills UP TO the meeting boundary (the
// omniscient ground truth for the `own_kill` line). The rest of the inspector is
// meeting-boundary data (`fetchMemoryView(meetingId, …)`), so scoping the scan to
// `maxTick` keeps a kill from a LATER meeting out of an earlier meeting's tab — it
// must reflect only what the agent had done by this meeting. Always derived here;
// the panel only shows them under the firewall gate.
function ownKillsOf(
  ticks: readonly { tick: number; events: readonly { type: string }[] }[],
  agentId: string,
  maxTick: number,
): KillEventView[] {
  const kills: KillEventView[] = [];
  for (const frame of ticks) {
    if (frame.tick > maxTick) {
      continue;
    }
    for (const event of frame.events) {
      if (event.type === "kill" && (event as KillEventView).killer_id === agentId) {
        kills.push(event as KillEventView);
      }
    }
  }
  return kills;
}

export function MindInspector({ meetingId }: { meetingId: string | null }) {
  const replay = useReplayStore((s) => s.currentReplay);
  const selectedAgentId = useReplayStore((s) => s.selectedAgentId);
  const memoryCache = useReplayStore((s) => s.memoryCache);
  const meetingCache = useReplayStore((s) => s.meetingCache);
  const perspective = useReplayStore((s) => s.perspective);
  const memoryError = useReplayStore((s) => s.currentReplayError);
  const fetchMemoryView = useReplayStore((s) => s.fetchMemoryView);
  const fetchMeeting = useReplayStore((s) => s.fetchMeeting);
  const selectAgent = useReplayStore((s) => s.selectAgent);
  const setPerspective = useReplayStore((s) => s.setPerspective);

  const [tab, setTab] = useState<MindTab>("belief");

  // FIREWALL gate (mirrors the panel): the ground-truth tells + verbatim prompt
  // memory are revealable only in Omniscient OR when the lens IS the inspected
  // agent. Used here to gate the BODIES fetch (the verbatim text rides the gate).
  const revealSecrets =
    perspective.mode === "omniscient" ||
    (perspective.mode === "agent" && perspective.agentId === selectedAgentId);

  // Lazy-hydrate the un-windowed meeting (Task 6.7 strips the prompt/response
  // bodies from the bulk payload, DESIGN.md §11.4) ONLY when the Prompt / Response
  // tab is actually open AND revealable — so scrubbing / auto-following through
  // meetings never eagerly pulls the large body payloads and the windowing holds.
  const bodiesNeeded =
    meetingId !== null && revealSecrets && (tab === "prompt" || tab === "response");
  useEffect(() => {
    if (bodiesNeeded && meetingId !== null) {
      void fetchMeeting(meetingId);
    }
  }, [bodiesNeeded, meetingId, fetchMeeting]);

  // Hydrate the selected agent's meeting-boundary memory snapshot whenever an
  // agent is picked — the Belief / observation / Flags tabs render through fog
  // too (they don't reveal the observer's own role), so memory is always needed.
  // The memory snapshot is small; only the per-meeting LLM BODIES are windowed.
  // No fetch before the agent's first meeting (`meetingId === null`): there is no
  // snapshot, and the panel shows the honest "no deliberation yet" state instead.
  useEffect(() => {
    if (selectedAgentId !== null && meetingId !== null) {
      void fetchMemoryView(meetingId, selectedAgentId);
    }
  }, [meetingId, selectedAgentId, fetchMemoryView]);

  if (replay === null) {
    return null;
  }

  // An agent is selected but has no meeting at or before the current tick — open
  // to an honest empty state, never fabricated between-meeting LLM data (§3.5).
  const noMeetingYet = selectedAgentId !== null && meetingId === null;

  const meeting =
    meetingId === null
      ? undefined
      : (meetingCache[meetingId] ??
        replay.meetings.find((m) => m.meeting_id === meetingId));
  const memory =
    selectedAgentId === null || meetingId === null
      ? undefined
      : memoryCache[`${meetingId}:${selectedAgentId}`];

  // Liveness at the meeting tick (role-neutral "dead" chip). Defaults to alive
  // when the frame isn't found (e.g. a synthetic story meeting).
  const meetingTick = meeting?.tick ?? null;

  // Own kills are scoped to this meeting's tick so a later kill never leaks back
  // into an earlier meeting's tab. The memory snapshot's `tick` is the truest
  // boundary; fall back to the meeting tick when memory hasn't loaded yet.
  const killBoundary = memory?.tick ?? meetingTick;
  const ownKills =
    selectedAgentId === null || killBoundary === null
      ? []
      : ownKillsOf(replay.ticks, selectedAgentId, killBoundary);
  const coverTasks =
    selectedAgentId === null ? [] : coverTasksOf(meeting, selectedAgentId);
  const frame =
    meetingTick === null
      ? undefined
      : replay.ticks.find((t) => t.tick === meetingTick);
  const isAlive =
    selectedAgentId === null
      ? true
      : (frame?.agent_states.find((s) => s.agent_id === selectedAgentId)?.is_alive ??
        true);

  // "Show what they saw" — the task contract's control: `selectAgent(agent)` +
  // `setPerspective(agent)`. IDEMPOTENT — it always SETS this agent's lens (never
  // toggles back to Omniscient), so re-clicking it in the already-self state is a
  // no-op, matching its label. Exiting fog is the perspective banner / map
  // toolbar's job, not this button's.
  const onShowWhatTheySaw = (agentId: string): void => {
    selectAgent(agentId);
    setPerspective({ mode: "agent", agentId });
  };

  return (
    <MindInspectorPanel
      players={replay.players}
      selectedAgentId={selectedAgentId}
      meeting={meeting}
      memory={memory}
      memoryError={memoryError}
      isAlive={isAlive}
      ownKills={ownKills}
      coverTasks={coverTasks}
      perspective={perspective}
      noMeetingYet={noMeetingYet}
      tab={tab}
      onTab={setTab}
      onSelectAgent={selectAgent}
      onShowWhatTheySaw={onShowWhatTheySaw}
    />
  );
}
