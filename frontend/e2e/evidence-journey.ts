/** The same source-to-decision checks run against the API and a plain static server. */
import { expect, type Page } from "@playwright/test";

export async function evidenceJourney(page: Page, origin: string): Promise<void> {
  await page.addInitScript(() => localStorage.setItem("ailibi.guidedTourSeen.v1", "1"));
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  const resultsUrl = `${origin}/?set=9p2i&view=tournament`;
  const openCase = async (title: string) => {
    await page.goto(resultsUrl);
    await expect(page.getByRole("heading", { name: "What the recordings show" })).toBeVisible();
    await expect(page.getByRole("region", { name: "Recorded results and cases" })).toContainText("50 games");
    const card = page.getByRole("article").filter({ has: page.getByRole("heading", { name: title }) });
    await expect(card.getByRole("button", { name: "Reveal case analysis (spoilers)", exact: true })).toHaveAttribute("aria-expanded", "false");
    await expect(card.getByRole("link", { name: "Pinned recording source" })).toHaveAttribute("href", /5006a32f/);
    await card.getByRole("link", { name: "Inspect the meeting" }).click();
  };
  const evidence = page.getByRole("region", { name: "Selected evidence" });
  await openCase("A sighting the table can check");
  await expect(page.getByRole("dialog", { name: "Meeting at tick 10", exact: true })).toBeVisible();
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
  const ballots = page.getByRole("region", { name: /^Ballots/ });
  await expect(ballots).toContainText("Private ballot reasoning. View p-5");
  await expect(ballots.getByRole("button", { name: "Cited observation · p-5:8:1", exact: true })).toHaveCount(0);
  await evidence.getByRole("button", { name: "Switch to p-5's perspective" }).click();
  await expect(evidence).toContainText(/p-6.*ENGINEERING/i);
  await expect(page).toHaveURL(/perspective=p-5/);
  await expect(ballots.getByRole("button", { name: "Cited observation · p-5:8:1", exact: true })).toBeVisible();
  await expect(ballots).not.toContainText("Private ballot reasoning. View p-5");
  await expect(ballots).toContainText("Private ballot reasoning. View p-1");
  expect(new URL(page.url()).searchParams.get("reveal")).toBeNull();

  await openCase("Follow an accusation across the map");
  await expect(evidence).toContainText(/p-1/);
  await expect(evidence).toContainText("observation tick 29");
  await evidence.getByRole("button", { name: "View scene frame 28", exact: true }).click();
  await expect(page).toHaveURL(/tick=28(?:&|$)/);
  await evidence.getByRole("button", { name: "Return to meeting and ballots" }).click();
  await page.getByRole("button", { name: "Cited observation · p-3:29:1", exact: true }).click();
  await expect(evidence).toContainText(/p-4.*CAFETERIA/i);
  await page.getByRole("button", { name: "Cited statement · headless-seed-46:meeting-3:turn-1", exact: true }).first().click();
  await expect(evidence).toContainText("p-9 · public reply");
  await evidence.getByRole("button", { name: "Locate in transcript" }).click();
  await expect(page.locator('[id="evidence-headless-seed-46%3Ameeting-3%3Aturn-1"]')).toBeFocused();

  // An invented ID stays missing after hydration; it must never choose nearby content.
  const missing = new URL(page.url());
  missing.searchParams.set("evidenceKind", "observation");
  missing.searchParams.set("evidenceId", "p-3:29:missing");
  missing.searchParams.set("evidenceObserver", "p-3");
  await page.goto(missing.toString());
  await expect(evidence).toContainText("Reference unavailable");
  await expect(evidence.getByRole("button", { name: /View scene/ })).toHaveCount(0);

  await openCase("When accounts do not settle the question");
  await expect(page.getByRole("dialog", { name: "Meeting at tick 12", exact: true })).toBeVisible();
  await expect(evidence).toContainText("p-4 · public opt-in");
  await expect(page.getByRole("region", { name: /^Ballots/ }).getByText("skip", { exact: true })).toHaveCount(7);
  await expect(page.getByRole("button", { name: /^Source 1 ·/ }).first()).toBeVisible();
  await page.getByRole("button", { name: /^Source 1 ·/ }).first().click();
  await expect(evidence).not.toContainText("Reference unavailable");
  await expect(evidence.getByRole("button", { name: "Locate in transcript" })).toBeVisible();
  expect(errors).toEqual([]);
}
