/** The same source-to-decision checks run against the API and a plain static server. */
import { expect, type Page } from "@playwright/test";

/** The slice of a served replay this journey reads its ids from. */
interface ServedBallot {
  voter: string;
  target: string;
  confidence: number;
  primary_reason_observation_id: string | null;
}

interface ServedMeeting {
  meeting_id: string;
  tick: number;
  outcome: "EJECTED" | "SKIPPED";
  ballots: ServedBallot[];
  gate: { leader: string | null; leader_max_confidence: number };
}

interface ServedReplay {
  meetings: ServedMeeting[];
}

/** The slice of a published case this journey walks. */
interface ServedCase {
  case_id: string;
  title: string;
  game_id: string;
  meeting_id: string;
  meeting_tick: number;
  observer_id: string;
  turn_id: string | null;
  observation_id: string | null;
  source_url: string;
}

interface ServedSummary {
  cases: ServedCase[];
  source_url: string | null;
}

// The commit that holds each set's published bytes is typed once, in
// tests/api/test_public_results.py; this journey asserts that every rendered
// source link is the one the served summary carries. History: the two commit
// literals left this file on 2026-10-09.

function isPath(response: { url(): string }, suffix: string): boolean {
  const path = decodeURIComponent(new URL(response.url()).pathname);
  return path.endsWith(suffix) || path.endsWith(`${suffix}.json`);
}

export async function evidenceJourney(page: Page, origin: string): Promise<void> {
  await page.addInitScript(() => localStorage.setItem("ailibi.guidedTourSeen.v1", "1"));
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));

  // The shown 9-player set ships the game-shape profile: its Highlights tab
  // opens on "Browse by moment", whose first shelf lists the featured head, seed
  // 19, and no reveal-only shelf shows before the reveal. The four-player set
  // ships none and renders the set-neutral no-profile state. Neither draws a
  // score.
  const moments = page.getByRole("region", { name: "Browse by moment", exact: true });
  await page.goto(`${origin}/?set=9p2i&view=highlights`);
  const reporter = moments.getByRole("region", { name: "The reporter saw it happen", exact: true });
  await expect(reporter.getByRole("button", { name: "Open replay seed 19", exact: true })).toBeVisible();
  await expect(moments.getByRole("region", { name: "All games", exact: true })).toBeVisible();
  await expect(moments).not.toContainText("Caught venting");
  await expect(moments).not.toContainText("ships no game-shape profile");
  await expect(moments).not.toContainText("/100");
  await page.goto(`${origin}/?set=4p1i&view=highlights`);
  await expect(moments).toContainText("No game-shape profile for this set");
  await expect(moments).not.toContainText("fixture");

  const browser = page.getByRole("region", { name: "Replay browser", exact: true });
  await page.goto(`${origin}/?set=9p2i&view=replays`);
  await expect(browser.getByRole("button", { name: "Open replay seed 19", exact: true })).toContainText(
    "The reporter saw it happen",
  );
  await expect(browser).not.toContainText("ships no game-shape profile");
  await page.goto(`${origin}/?set=4p1i&view=replays`);
  await expect(browser).toContainText("ships no game-shape profile, so its cards show no shelves.");
  await expect(browser).not.toContainText("fixture");
  await expect(browser).not.toContainText("interestingness");

  // The 9p2i results cover the whole set and publish the curated cases, each
  // on a featured game and each pinned, with the set itself, to the commit
  // that landed its bytes. The case list is read from the summary the app
  // fetched, so the walk follows the published payload rather than a copy.
  const results = page.getByRole("region", { name: "Recorded results and cases" });
  const resultsUrl = `${origin}/?set=9p2i&view=tournament`;
  const summaryResponse = page.waitForResponse((response) => isPath(response, "/eval/summary"));
  await page.goto(resultsUrl);
  const summary = (await (await summaryResponse).json()) as ServedSummary;
  await expect(page.getByRole("heading", { name: "What the recordings show" })).toBeVisible();
  await expect(results).toContainText("50 games");
  await expect(results).toContainText("100% by construction");
  expect(summary.cases.map((example) => example.case_id)).toEqual(["witnessed-vent", "weak-evidence"]);
  await expect(results.getByRole("article")).toHaveCount(summary.cases.length);
  await expect(results).not.toContainText("No source-matched editorial cases are published for this set.");
  for (const example of summary.cases) {
    const card = results.getByRole("article").filter({ has: page.getByRole("heading", { name: example.title }) });
    await expect(card.getByRole("button", { name: "Reveal case analysis (spoilers)", exact: true })).toHaveAttribute(
      "aria-expanded",
      "false",
    );
    await expect(card.getByRole("link", { name: "Pinned recording source" })).toHaveAttribute(
      "href",
      example.source_url,
    );
    await expect(card.getByRole("link", { name: "Pinned recording source" })).toHaveAttribute(
      "href",
      new RegExp(`replay-seed-${example.game_id.replace("headless-seed-", "")}\\.jsonl$`),
    );
  }
  await results.getByText("Recording provenance and reported usage").click();
  await expect(results).toContainText("Source fingerprint");
  expect(summary.source_url).not.toBeNull();
  await expect(results.getByRole("link", { name: "Inspect this pinned source set and manifest" })).toHaveAttribute(
    "href",
    summary.source_url ?? "",
  );

  // The 4-player set publishes no case, and its set link stays where its
  // replays were recorded.
  const fourSummaryResponse = page.waitForResponse(
    (response) => isPath(response, "/eval/summary") && response.url().includes("4p1i"),
  );
  await page.goto(`${origin}/?set=4p1i&view=tournament`);
  const fourSummary = (await (await fourSummaryResponse).json()) as ServedSummary;
  await expect(results).toContainText("No source-matched editorial cases are published for this set.");
  await expect(results.getByRole("article")).toHaveCount(0);
  await results.getByText("Recording provenance and reported usage").click();
  expect(fourSummary.source_url).not.toBeNull();
  expect(fourSummary.source_url).not.toBe(summary.source_url);
  await expect(results.getByRole("link", { name: "Inspect this pinned source set and manifest" })).toHaveAttribute(
    "href",
    fourSummary.source_url ?? "",
  );

  const evidence = page.getByRole("region", { name: "Selected evidence" });
  const openCase = async (example: ServedCase): Promise<ServedReplay> => {
    await page.goto(resultsUrl);
    const card = page.getByRole("article").filter({ has: page.getByRole("heading", { name: example.title }) });
    const served = page.waitForResponse((response) => isPath(response, `/replays/${example.game_id}`));
    await card.getByRole("link", { name: "Inspect the meeting" }).click();
    const replay = (await (await served).json()) as ServedReplay;
    await expect(page.getByRole("dialog", { name: `Meeting at tick ${example.meeting_tick}`, exact: true })).toBeVisible();
    return replay;
  };

  // Each case opens its own meeting on the evidence it names: the statement
  // case on its turn, which "Locate in transcript" focuses.
  for (const example of summary.cases.filter((candidate) => candidate.observation_id === null)) {
    await openCase(example);
    await expect(evidence).toContainText(`${example.observer_id} · public`);
    await evidence.getByRole("button", { name: "Locate in transcript" }).click();
    await expect(page.locator(`[id="evidence-${encodeURIComponent(example.turn_id ?? "")}"]`)).toBeFocused();
  }

  // The evidence legs enter through the observation case: its cited
  // observation, the scene frame it depicts, the fog lens and the switch back.
  const witnessed = summary.cases.find((candidate) => candidate.observation_id !== null);
  if (witnessed === undefined || witnessed.observation_id === null) {
    throw new Error("no published case cites an observation");
  }
  const id = witnessed.observation_id;
  const observer = witnessed.observer_id;
  const replay = await openCase(witnessed);
  const meeting = replay.meetings.find((candidate) => candidate.meeting_id === witnessed.meeting_id);
  if (meeting === undefined) throw new Error(`${witnessed.meeting_id} is not in the served replay`);
  const ballot = meeting.ballots.find((candidate) => candidate.voter === observer);
  if (ballot === undefined) throw new Error(`${observer} cast no ballot in ${meeting.meeting_id}`);
  expect(ballot.primary_reason_observation_id).toBe(id);
  const observationTick = id.split(":")[1] ?? "";
  const other = meeting.ballots.find((candidate) => candidate.voter !== observer)?.voter;
  if (other === undefined) throw new Error(`${meeting.meeting_id} has no second voter`);
  const meetingDialog = page.getByRole("dialog", { name: `Meeting at tick ${meeting.tick}`, exact: true });
  const observed = `${observer} · observation tick ${observationTick}`;

  const gate = page.getByText(/How the vote resolved/);
  await expect(gate).toContainText(`top ballot ${meeting.gate.leader_max_confidence.toFixed(2)}`);
  await expect(evidence).toContainText(observed);
  const scene = evidence.getByRole("button", { name: /^View scene frame -?\d+$/ });
  const sceneTick = (await scene.innerText()).replace("View scene frame ", "").trim();
  await scene.focus();
  await page.keyboard.press("Enter");
  await expect(meetingDialog).not.toBeVisible();
  await expect(page).toHaveURL(new RegExp(`tick=${sceneTick}(?:&|$)`));
  await expect(page).toHaveURL(new RegExp(`evidenceId=${encodeURIComponent(id)}`));
  await page.reload();
  await expect(evidence).toContainText(observed);
  await evidence.getByRole("button", { name: "Return to meeting and ballots" }).click();
  await expect(meetingDialog).toBeVisible();
  // Share the settled URL; the dialog renders before debounced URL write-back.
  await expect(page).toHaveURL((url) =>
    url.searchParams.get("tick") === String(meeting.tick) &&
    url.searchParams.get("selectedMeeting") === meeting.meeting_id,
  );

  // Opening a shared citation through another lens must not expose private memory.
  const fog = new URL(page.url());
  fog.searchParams.set("perspective", other);
  await page.goto(fog.toString());
  await expect(evidence).toContainText("private observation");
  await expect(evidence).not.toContainText("You witnessed");
  await expect(page).toHaveURL(new RegExp(`perspective=${other}`));
  await expect(gate).not.toContainText("top ballot");
  await expect(gate).toContainText(meeting.outcome);
  const ballots = page.getByRole("region", { name: /^Ballots/ });
  await expect(ballots).toContainText(`Private ballot reasoning. View ${observer}`);
  await expect(ballots.getByRole("button", { name: `Cited observation · ${id}`, exact: true })).toHaveCount(0);
  await evidence.getByRole("button", { name: `Switch to ${observer}'s perspective` }).click();
  await expect(evidence).toContainText(observed);
  await expect(page).toHaveURL(new RegExp(`perspective=${observer}`));
  // An agent lens names its own ballot on the leader, never the table's maximum.
  if (ballot.target === meeting.gate.leader) {
    await expect(gate).toContainText(`your ballot ${ballot.confidence.toFixed(2)}`);
  } else {
    await expect(gate).not.toContainText("your ballot");
  }
  await expect(gate).not.toContainText("top ballot");
  await expect(ballots.getByRole("button", { name: `Cited observation · ${id}`, exact: true })).toBeVisible();
  await expect(ballots).not.toContainText(`Private ballot reasoning. View ${observer}`);
  await expect(ballots).toContainText(`Private ballot reasoning. View ${other}`);
  expect(new URL(page.url()).searchParams.get("reveal")).toBeNull();

  // An invented ID stays missing after hydration; it must never choose nearby content.
  const missing = new URL(page.url());
  missing.searchParams.set("evidenceKind", "observation");
  missing.searchParams.set("evidenceId", `${observer}:${observationTick}:missing`);
  missing.searchParams.set("evidenceObserver", observer);
  await page.goto(missing.toString());
  await expect(evidence).toContainText("Reference unavailable");
  await expect(evidence.getByRole("button", { name: /View scene/ })).toHaveCount(0);
  expect(errors).toEqual([]);
}
