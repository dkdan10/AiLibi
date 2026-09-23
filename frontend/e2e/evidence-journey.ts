/** The same source-to-decision checks run against the API and a plain static server. */
import { expect, type Page } from "@playwright/test";

export async function evidenceJourney(page: Page, origin: string): Promise<void> {
  await page.addInitScript(() => localStorage.setItem("ailibi.guidedTourSeen.v1", "1"));
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto(`${origin}/?set=9p2i&view=replays`);
  const browser = page.getByRole("region", { name: "Replay browser", exact: true });
  // The committed rubric is current for these recordings: no stale-score banner,
  // the score legend is shown, and every card carries a score. (Every score reads
  // 0 today, the extractor self-check floor pinned in tests/api/test_sets.py.)
  await expect(browser).toContainText("The 0–100 score is an internal pacing/structure heuristic");
  await expect(browser).not.toContainText("Earlier scores");
  await expect(browser.getByRole("button", { name: /^Open replay seed \d+, interestingness score \d+ of 100$/ }).first()).toBeVisible();
  await expect(browser).not.toContainText("ships no");
  await expect(browser).not.toContainText("No score available for this recording");
  await page.goto(`${origin}/?set=4p1i&view=replays`);
  await expect(browser).toContainText("ships no");
  await expect(browser).not.toContainText("Earlier scores");
  const resultsUrl = `${origin}/?set=9p2i&view=tournament`;
  const openCase = async (title: string) => {
    await page.goto(resultsUrl);
    await expect(page.getByRole("heading", { name: "What the recordings show" })).toBeVisible();
    await expect(page.getByRole("region", { name: "Recorded results and cases" })).toContainText("50 games");
    await expect(page.getByRole("region", { name: "Recorded results and cases" })).toContainText("100% by construction");
    const card = page.getByRole("article").filter({ has: page.getByRole("heading", { name: title }) });
    await expect(card.getByRole("button", { name: "Reveal case analysis (spoilers)", exact: true })).toHaveAttribute("aria-expanded", "false");
    await expect(card.getByRole("link", { name: "Pinned recording source" })).toHaveAttribute("href", /9bae2b03/);
    await card.getByRole("link", { name: "Inspect the meeting" }).click();
  };
  const evidence = page.getByRole("region", { name: "Selected evidence" });
  await openCase("A sighting the table can check");
  await expect(page.getByRole("dialog", { name: "Meeting at tick 10", exact: true })).toBeVisible();
  const gate = page.getByText(/How the vote resolved/);
  await expect(gate).toContainText("top ballot 1.00");
  await expect(evidence).toContainText(/p-6.*ENGINEERING/i);
  await expect(evidence).toContainText("observation tick 8");
  const scene = evidence.getByRole("button", { name: "View scene frame 7", exact: true });
  await scene.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("dialog", { name: "Meeting at tick 10", exact: true })).not.toBeVisible();
  await expect(page).toHaveURL(/tick=7(?:&|$)/);
  await expect(page).toHaveURL(/evidenceId=p-5%3A8%3A1/);
  await page.reload();
  await expect(evidence).toContainText(/p-6.*ENGINEERING/i);
  await evidence.getByRole("button", { name: "Return to meeting and ballots" }).click();
  await expect(page.getByRole("dialog", { name: "Meeting at tick 10", exact: true })).toBeVisible();
  // Share the settled URL; the dialog renders before debounced URL write-back.
  await expect(page).toHaveURL((url) =>
    url.searchParams.get("tick") === "10" &&
    url.searchParams.get("selectedMeeting") === "headless-seed-23:meeting-0",
  );

  // Opening a shared citation through another lens must not expose private memory.
  const fog = new URL(page.url());
  fog.searchParams.set("perspective", "p-2");
  await page.goto(fog.toString());
  await expect(evidence).toContainText("private observation");
  await expect(evidence).not.toContainText("You witnessed");
  await expect(page).toHaveURL(/perspective=p-2/);
  await expect(gate).not.toContainText("top ballot");
  await expect(gate).not.toContainText("1.00");
  await expect(gate).toContainText("EJECTED");
  const ballots = page.getByRole("region", { name: /^Ballots/ });
  await expect(ballots).toContainText("Private ballot reasoning. View p-5");
  await expect(ballots.getByRole("button", { name: "Cited observation · p-5:8:1", exact: true })).toHaveCount(0);
  await evidence.getByRole("button", { name: "Switch to p-5's perspective" }).click();
  await expect(evidence).toContainText(/p-6.*ENGINEERING/i);
  await expect(page).toHaveURL(/perspective=p-5/);
  await expect(gate).toContainText("your ballot 1.00");
  await expect(gate).not.toContainText("top ballot");
  await expect(ballots.getByRole("button", { name: "Cited observation · p-5:8:1", exact: true })).toBeVisible();
  await expect(ballots).not.toContainText("Private ballot reasoning. View p-5");
  await expect(ballots).toContainText("Private ballot reasoning. View p-1");
  expect(new URL(page.url()).searchParams.get("reveal")).toBeNull();

  // Both witnesses' own cited records show p-1 moving from Labs to Medbay, the
  // move p-1's route states; the scene link lands on the frame that move depicts.
  await openCase("Follow an accusation across the map");
  await expect(page.getByRole("dialog", { name: "Meeting at tick 9", exact: true })).toBeVisible();
  await expect(evidence).toContainText(/p-1.*LABS.*MEDBAY/i);
  await expect(evidence).toContainText("observation tick 6");
  await evidence.getByRole("button", { name: "View scene frame 5", exact: true }).click();
  await expect(page).toHaveURL(/tick=5(?:&|$)/);
  await evidence.getByRole("button", { name: "Return to meeting and ballots" }).click();
  await page.getByRole("button", { name: "Cited observation · p-7:6:2", exact: true }).click();
  await expect(evidence).toContainText(/p-1.*LABS.*MEDBAY/i);
  await page.getByRole("button", { name: "Cited statement · headless-seed-29:meeting-1:turn-2", exact: true }).first().click();
  await expect(evidence).toContainText("p-1 · public opt-in");
  await evidence.getByRole("button", { name: "Locate in transcript" }).click();
  await expect(page.locator('[id="evidence-headless-seed-29%3Ameeting-1%3Aturn-2"]')).toBeFocused();

  // An invented ID stays missing after hydration; it must never choose nearby content.
  const missing = new URL(page.url());
  missing.searchParams.set("evidenceKind", "observation");
  missing.searchParams.set("evidenceId", "p-7:6:missing");
  missing.searchParams.set("evidenceObserver", "p-7");
  await page.goto(missing.toString());
  await expect(evidence).toContainText("Reference unavailable");
  await expect(evidence.getByRole("button", { name: /View scene/ })).toHaveCount(0);

  await openCase("When accounts do not settle the question");
  const unresolved = page.getByRole("dialog", { name: "Meeting at tick 17", exact: true });
  await expect(unresolved).toBeVisible();
  await expect(evidence).toContainText("p-4 · public opt-in");
  // Five voluntary skips and two votes for p-1: no one is ejected.
  await expect(page.getByRole("region", { name: /^Ballots/ }).getByText("skip", { exact: true })).toHaveCount(5);
  await expect(unresolved).toContainText("skip ×5");
  await expect(unresolved).toContainText("p-1 ×2");
  await expect(unresolved).toContainText("Skipped — no ejection");
  await expect(page.getByRole("button", { name: /^Source 1 ·/ }).first()).toBeVisible();
  await page.getByRole("button", { name: /^Source 1 ·/ }).first().click();
  await expect(evidence).not.toContainText("Reference unavailable");
  await expect(evidence.getByRole("button", { name: "Locate in transcript" })).toBeVisible();
  expect(errors).toEqual([]);
}
