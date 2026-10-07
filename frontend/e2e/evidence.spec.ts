import { expect, test } from "@playwright/test";
import { evidenceJourney } from "./evidence-journey";

test("API: exact evidence, results, cases, fog and shared links", async ({ page, baseURL }) => {
  await evidenceJourney(page, baseURL!);
});

// Live only: the static bundle is built without the full diagnostic report, so
// no moments panel ships there.
test("API: the dashboard counts the shown set's moments and words the other set's absence", async ({
  page,
  baseURL,
}) => {
  await page.addInitScript(() => localStorage.setItem("ailibi.guidedTourSeen.v1", "1"));
  const moments = page
    .locator("section")
    .filter({ has: page.getByRole("heading", { name: "Moments in this set", exact: true }) });
  const openReport = () => page.getByText("Full diagnostic report (larger download)", { exact: true }).click();
  await page.goto(`${baseURL!}/?set=9p2i&view=tournament`);
  await openReport();
  await expect(moments).toContainText("The reporter saw it happen", { timeout: 60_000 });
  await expect(moments).not.toContainText("Caught venting");
  await page.goto(`${baseURL!}/?set=4p1i&view=tournament`);
  await openReport();
  await expect(moments).toContainText("No game-shape profile.", { timeout: 60_000 });
});
