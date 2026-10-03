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

/** The first ballot, in served order, that cites one of its voter's observations. */
function firstCitedObservation(replay: ServedReplay): { meeting: ServedMeeting; ballot: ServedBallot; id: string } {
  for (const meeting of replay.meetings) {
    for (const ballot of meeting.ballots) {
      if (ballot.primary_reason_observation_id !== null) {
        return { meeting, ballot, id: ballot.primary_reason_observation_id };
      }
    }
  }
  throw new Error("the head game's ballots cite no observation");
}

export async function evidenceJourney(page: Page, origin: string): Promise<void> {
  await page.addInitScript(() => localStorage.setItem("ailibi.guidedTourSeen.v1", "1"));
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));

  // No committed set ships a rubric since 2026-10-02 (the gameplay-facts
  // extractor does not read the shown 9-player set's recordings), so both sets
  // render the set-level unscored state, in words that name no set as the
  // unscored one, and neither draws the score legend.
  const browser = page.getByRole("region", { name: "Replay browser", exact: true });
  for (const set of ["9p2i", "4p1i"]) {
    await page.goto(`${origin}/?set=${set}&view=replays`);
    await expect(browser).toContainText("ships no interestingness rubric — its games are unscored.");
    await expect(browser).not.toContainText("The 0–100 score is an internal pacing/structure heuristic");
    await expect(browser).not.toContainText("fixture");
    await expect(browser).not.toContainText("Earlier scores");
    await expect(browser).not.toContainText("No score available for this recording");
  }

  // The results cover the whole set, and the curated cases written for the
  // set's earlier recording are withheld by their source check: no case card,
  // no case source link, and no pinned-source link for the set.
  const results = page.getByRole("region", { name: "Recorded results and cases" });
  await page.goto(`${origin}/?set=9p2i&view=tournament`);
  await expect(page.getByRole("heading", { name: "What the recordings show" })).toBeVisible();
  await expect(results).toContainText("50 games");
  await expect(results).toContainText("100% by construction");
  await expect(results).toContainText("No source-matched editorial cases are published for this set.");
  await expect(results.getByRole("article")).toHaveCount(0);
  await expect(results.getByRole("link", { name: "Pinned recording source" })).toHaveCount(0);
  await results.getByText("Recording provenance and reported usage").click();
  await expect(results).toContainText("Source fingerprint");
  await expect(results.getByRole("link", { name: "Inspect this pinned source set and manifest" })).toHaveCount(0);

  // The evidence legs enter through the featured head's first cited
  // observation. Its ids are read from the replay the app itself fetched, so
  // the walk follows the served bytes rather than a hardcoded case.
  await page.goto(`${origin}/?set=9p2i`);
  const featured = page.getByRole("region", { name: "Featured games" });
  await expect(featured).toBeVisible();
  const headCard = featured.getByRole("listitem").first().getByRole("button");
  const seed = Number((await headCard.locator("span").first().innerText()).replace(/[^0-9]/g, ""));
  expect(Number.isInteger(seed)).toBe(true);
  const gameId = `headless-seed-${seed}`;
  const served = page.waitForResponse((response) => {
    const path = decodeURIComponent(new URL(response.url()).pathname);
    return path.endsWith(`/replays/${gameId}`) || path.endsWith(`/replays/${gameId}.json`);
  });
  await headCard.click();
  const replay = (await (await served).json()) as ServedReplay;
  const { meeting, ballot, id } = firstCitedObservation(replay);
  const observer = ballot.voter;
  const observationTick = id.split(":")[1] ?? "";
  const other = meeting.ballots.find((candidate) => candidate.voter !== observer)?.voter;
  if (other === undefined) throw new Error(`${meeting.meeting_id} has no second voter`);
  const meetingDialog = page.getByRole("dialog", { name: `Meeting at tick ${meeting.tick}`, exact: true });
  const evidence = page.getByRole("region", { name: "Selected evidence" });
  const observed = `${observer} · observation tick ${observationTick}`;

  const shared = new URL(`${origin}/`);
  shared.search = new URLSearchParams({
    set: "9p2i",
    game_id: gameId,
    tick: String(meeting.tick),
    selectedMeeting: meeting.meeting_id,
    view: "workspace",
    evidenceKind: "observation",
    evidenceId: id,
    evidenceMeeting: meeting.meeting_id,
    evidenceObserver: observer,
  }).toString();
  await page.goto(shared.toString());
  await expect(meetingDialog).toBeVisible();
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
