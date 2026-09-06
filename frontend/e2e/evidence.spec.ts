import { test } from "@playwright/test";
import { evidenceJourney } from "./evidence-journey";

test("API: exact evidence, results, cases, fog and shared links", async ({ page, baseURL }) => {
  await evidenceJourney(page, baseURL!);
});
