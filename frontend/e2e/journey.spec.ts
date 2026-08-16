// THE spectator journey (Task 19.12) — one spec file, four tests, one browser.
//
// It drives the REAL app against the REAL API serving the REAL committed sample
// set: featured replay → play → meeting pause → inspect ballots → finale
// (unspoiled → reveal), plus three pins on behaviors that already work and must
// keep working — the keyboard transport, the As-agent fog firewall, and reduced
// motion.
//
// WHAT THIS FILE IS FOR. The unit suites cover the pure derivations and the
// store's async guards; neither can see the thing that actually breaks in a
// viewer — a lazy Pixi route that fails to mount, a modal that swallows the
// keyboard, a fog toggle that leaves a role badge on screen. Those are
// browser-only facts, so there is exactly ONE browser leg and it is spent on
// them.
//
// NO SLEEPS. Every wait in this file is `expect(...)` against a state the app
// genuinely reaches, so a slow CI runner makes the suite slower, never redder.
// The one time-shaped wait is the autoplay→pause assertion, expressed as a
// generous assertion timeout (the transport advances one frame per 500 ms at
// 1×, and the curated head's first meeting is ~8 frames in).
//
// The guided tour is suppressed via `localStorage` before the first paint —
// see `openFeaturedReplay`.

import { expect, test } from "@playwright/test";
import type { Page } from "@playwright/test";

/** The first-run tour's "seen" key (frontend/src/components/GuidedTour.tsx). */
const TOUR_SEEN_KEY = "ailibi.guidedTourSeen.v1";

/**
 * Land in the workspace on the head of the CURATED featured list, and return
 * the seed it opened.
 *
 * The tour is marked seen before the first paint. Not because it is untested
 * territory to be avoided, but because on a virgin visit it AUTO-LOADS its own
 * teaching seed — so leaving it on would put two replay loads in flight and make
 * "which game am I looking at" a race. Suppressing it is what makes the featured
 * click the ONLY thing that selects a replay here.
 *
 * The seed is READ from the card rather than hardcoded: `FEATURED_GAMES` is
 * editorial data (ReplayPicker.tsx says so in as many words), and a journey that
 * hardcoded today's head would fail the next time someone re-ordered the list
 * for reasons that have nothing to do with this test. What IS pinned is the
 * join: the card you click opens that seed's workspace.
 */
async function openFeaturedReplay(page: Page): Promise<number> {
  await page.addInitScript((key) => {
    window.localStorage.setItem(key, "1");
  }, TOUR_SEEN_KEY);
  await page.goto("/");

  const featured = page.getByRole("region", { name: "Featured games" });
  await expect(featured).toBeVisible();
  const head = featured.getByRole("listitem").first().getByRole("button");
  const seedLabel = await head.locator("span").first().innerText();
  const seed = Number(seedLabel.replace(/[^0-9]/g, ""));
  expect(Number.isFinite(seed)).toBe(true);

  await head.click();

  // The workspace is up once the transport region has mounted.
  await expect(page.locator("[data-transport-region]")).toBeVisible();
  // …and the lazy Pixi map has actually rendered its canvas. Asserting this
  // here means a broken map route fails ONE obvious assertion instead of
  // surfacing as a mysterious timeout three steps later.
  await expect(page.locator("canvas")).toBeVisible();
  return seed;
}

/**
 * Drop focus to `document.body` before driving the global keyboard shortcuts.
 *
 * The shell deliberately does NOT fire transport accelerators while focus sits
 * on a form control or on an activatable widget outside the transport region
 * (App.tsx `KeyboardTransport`) — Space would double-fire a focused button, and
 * arrows are a tablist's own navigation keys. So "where is focus" is part of the
 * contract, and a test that pressed keys at whatever the previous step happened
 * to leave focused would be asserting on luck.
 */
async function resetFocus(page: Page): Promise<void> {
  await page.evaluate(() => {
    const active = document.activeElement;
    if (active instanceof HTMLElement) {
      active.blur();
    }
  });
}

/** The transport's frame index, read off the scrubber (the store's `currentTick`). */
function frameIndex(page: Page) {
  return page.getByLabel("Seek tick");
}

test.describe("spectator journey", () => {
  test("featured replay → play → meeting pause → ballots → finale (unspoiled → reveal)", async ({
    page,
  }) => {
    // An uncaught exception anywhere in this walk is a failure, whatever else
    // passes. Collected for the whole test and asserted at the end.
    const pageErrors: string[] = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));

    const seed = await openFeaturedReplay(page);

    // ── unspoiled by default (Task 19.10) ────────────────────────────────────
    // The header USED to print the winner from frame zero. Unrevealed it now
    // says so in words, and no winner value reaches the DOM at all.
    //
    // Picked by what it CONTAINS, not by position: the workspace's mode banner
    // and the shell's own header are both `<header>` elements, and only the
    // shell one (outside any section) carries the `banner` role.
    const banner = page
      .locator("header")
      .filter({ has: page.locator('[aria-label^="Perspective:"]') });
    await expect(banner).toContainText(`seed ${seed}`);
    await expect(banner).toContainText("outcome hidden");
    await expect(banner).not.toContainText("CREWMATES");
    await expect(banner).not.toContainText("IMPOSTORS");
    await expect(frameIndex(page)).toHaveValue("0");

    // ── play → the meeting pause ─────────────────────────────────────────────
    await page.getByRole("button", { name: "▶ Play" }).click();

    // A meeting occupies exactly ONE frame, so autoplay used to flash a whole
    // deliberation past in 500 ms. Entering one now stops the transport and says
    // why. Generous timeout, no sleep: the wait is for the pause to HAPPEN.
    const pauseBar = page.getByRole("status").filter({ hasText: "playback paused" });
    await expect(pauseBar).toBeVisible({ timeout: 60_000 });
    await expect(pauseBar).toContainText(/Meeting at tick \d+ — playback paused/);
    // The pause is real, not cosmetic: the transport is back to Play, and the
    // bar offers both ways forward.
    await expect(page.getByRole("button", { name: "▶ Play" })).toBeVisible();
    await expect(pauseBar.getByRole("button", { name: /Resume/ })).toBeVisible();
    await expect(pauseBar.getByRole("button", { name: /Next beat/ })).toBeVisible();

    // ── inspect the ballots ──────────────────────────────────────────────────
    // Auto-follow opened the meeting on entering its tick.
    const meeting = page.getByRole("dialog");
    await expect(meeting).toBeVisible();
    await expect(meeting).toHaveAttribute("aria-label", /Meeting at tick \d+/);
    const ballots = meeting.getByRole("region", { name: /^Ballots \(\d+\)$/ });
    await expect(ballots).toBeVisible();
    // Every ballot in the panel names a voter and carries a confidence readout —
    // the meeting's actual payload, not just a heading that rendered.
    await expect(ballots).toContainText("confidence");
    await expect(ballots.getByText(/^p-\d+$/).first()).toBeVisible();

    // ── to the end ───────────────────────────────────────────────────────────
    await page.keyboard.press("Escape"); // the meeting's own keyboard exit
    await expect(meeting).toBeHidden();
    await resetFocus(page);
    await page.keyboard.press("End");

    // The end-of-replay beat is POSITION-derived, so `End` lands on it exactly
    // as autoplay or a scrub to the far right would.
    const finale = page.getByRole("region", { name: "End of replay" });
    const showFinale = page.getByRole("button", { name: "Show finale" });

    // A game that ends on an ejection has the meeting and the finale on the SAME
    // frame, and the card yields to any open meeting — so the pause bar's
    // "Show finale" is the documented hand-off. A game that ends on a kill shows
    // the card straight away. Take whichever path this game presents rather than
    // pinning the journey to one ending shape.
    //
    // BRANCH ON THE FRAME, NOT ON THE OVERLAYS. `End` only moves the playhead;
    // auto-follow opens the last frame's meeting from an EFFECT, so on a
    // meeting-ending game there is a commit where the finale card is already
    // mounted and the meeting is not yet open. Any branch keyed on the overlays
    // — including "wait for the card OR the hand-off button" — can therefore be
    // satisfied by that transient card, skip the hand-off, and then race the
    // effect that hides it. The pre-effect DOM is genuinely indistinguishable
    // from a kill ending's settled DOM, so no union of those two locators can
    // tell them apart.
    //
    // The transport's `meeting` chip can: it is a pure function of the FRAME
    // (`meetingAtTick`), rendered by the same component and the same commit as
    // the scrubber value asserted just above, with no effect in between. So once
    // the scrubber reads the last index, the chip is already the settled answer
    // to "does this game end on a meeting" — and each branch then waits for its
    // own terminal condition.
    const lastIndex = await frameIndex(page).getAttribute("max");
    await expect(frameIndex(page)).toHaveValue(lastIndex ?? "");
    const endsOnMeeting = await page
      .locator("[data-transport-region]")
      .getByText("meeting", { exact: true })
      .isVisible();

    if (endsOnMeeting) {
      // Auto-follow will open it; the hand-off button appearing IS the proof
      // that the effect has run.
      await expect(showFinale).toBeVisible();
      await showFinale.click();
    }
    await expect(finale).toBeVisible();

    // ── unspoiled finale ─────────────────────────────────────────────────────
    // The card EXISTS unrevealed — that the game is over is not a spoiler, and
    // hiding it would leave the reader on a dead screen with a disabled Play.
    await expect(finale).toContainText("The game is over");
    await expect(finale).toContainText("The outcome is hidden");
    await expect(finale).not.toContainText("Crew win");
    await expect(finale).not.toContainText("Impostor win");
    await expect(finale).not.toContainText("What they knew vs the truth");

    // ── reveal ───────────────────────────────────────────────────────────────
    await finale.getByRole("button", { name: "Reveal the outcome" }).click();
    await expect(finale).toContainText(/Crew win|Impostor win/);
    await expect(finale).toContainText("Decisive events");
    await expect(finale).toContainText("What they knew vs the truth");
    await expect(finale).toContainText(/final tick \d+/);
    // The reveal is a shareable, deliberate hand-off: it — and only it — writes
    // the spoiler key into the URL.
    await expect(page).toHaveURL(/[?&]reveal=1\b/);
    // The header's outcome gate is the SAME axis, so it flips with the card.
    await expect(banner).not.toContainText("outcome hidden");

    // Hiding it again takes the key back out (a URL a reader thought was clean
    // must not re-spoil the ending on reload).
    await finale.getByRole("button", { name: "Hide outcome" }).click();
    await expect(finale).toContainText("The outcome is hidden");
    await expect(page).not.toHaveURL(/[?&]reveal=1\b/);

    expect(pageErrors).toEqual([]);
  });

  test("the keyboard transport drives the playhead", async ({ page }) => {
    await openFeaturedReplay(page);
    await resetFocus(page);

    // Step ±1 and ±10 (Shift), and the Home/End ends.
    await page.keyboard.press("ArrowRight");
    await expect(frameIndex(page)).toHaveValue("1");
    await page.keyboard.press("Shift+ArrowRight");
    await expect(frameIndex(page)).toHaveValue("11");
    await page.keyboard.press("ArrowLeft");
    await expect(frameIndex(page)).toHaveValue("10");
    await page.keyboard.press("Shift+ArrowLeft");
    await expect(frameIndex(page)).toHaveValue("0");
    await page.keyboard.press("Home");
    await expect(frameIndex(page)).toHaveValue("0");

    // `]` jumps to the next meeting AND selects it (explicit user intent —
    // auto-follow would also catch it, but jumping must never miss the open).
    await page.keyboard.press("]");
    const meeting = page.getByRole("dialog");
    await expect(meeting).toBeVisible();
    const atFirstMeeting = await frameIndex(page).inputValue();
    expect(Number(atFirstMeeting)).toBeGreaterThan(0);

    await page.keyboard.press("Escape");
    await expect(meeting).toBeHidden();
    await resetFocus(page);

    // `n` = the next key-moment inflection: strictly forward, never in place.
    await page.keyboard.press("n");
    await expect(frameIndex(page)).not.toHaveValue(atFirstMeeting);
    const afterKeyMoment = Number(await frameIndex(page).inputValue());
    expect(afterKeyMoment).toBeGreaterThan(Number(atFirstMeeting));

    // Space toggles the transport both ways.
    const play = page.getByRole("button", { name: "▶ Play" });
    const pause = page.getByRole("button", { name: "⏸ Pause" });
    await page.keyboard.press(" ");
    await expect(pause).toBeVisible();
    await page.keyboard.press(" ");
    await expect(play).toBeVisible();

    // End walks to the last frame; the scrubber's max IS the last index.
    await page.keyboard.press("End");
    const lastIndex = await frameIndex(page).getAttribute("max");
    await expect(frameIndex(page)).toHaveValue(lastIndex ?? "");
  });

  test("As-agent fog hides every omniscient-only fact", async ({ page }) => {
    await openFeaturedReplay(page);

    const roster = page.getByRole("complementary");
    const perspective = page.locator('[aria-label^="Perspective:"]');

    // Omniscient: ground truth is on screen — role badges per roster row, the
    // impostor-badge legend, and the crew/impostor arithmetic.
    await expect(perspective).toHaveText("Omniscient");
    const roleBadges = roster.getByText(/^(CREWMATE|IMPOSTOR)$/);
    const omniscientRoleCount = await roleBadges.count();
    expect(omniscientRoleCount).toBeGreaterThan(0);
    await expect(roster.getByText(/^crew \d+$/)).toBeVisible();
    await expect(page.getByText("= impostor")).toBeVisible();

    // Enter the fog from the map toolbar — the ONE interactive switcher (the
    // shell banner is a read-only indicator by design).
    await page.getByRole("button", { name: "As-agent" }).click();

    // THE FIREWALL, simulated in the UI: an agent does not know anyone's role,
    // the living-crew count, or the impostor count. None of it may remain in the
    // DOM — not greyed, not hidden behind an attribute: absent.
    await expect(perspective).toHaveText(/^As p-\d+ · fog$/);
    await expect(roleBadges).toHaveCount(0);
    await expect(roster.getByText(/^crew \d+$/)).toBeHidden();
    await expect(page.getByText("= impostor")).toBeHidden();
    // The Belief × Truth hero is an Omniscient cross-agent overview, so its
    // launcher goes with them.
    await expect(page.getByRole("button", { name: /Belief . Truth/ })).toBeHidden();
    // The fog SUBJECT is explicit and switchable, and the moment is shareable.
    await expect(page.getByLabel("Perspective agent")).toBeVisible();
    await expect(page).toHaveURL(/[?&]perspective=p-\d+\b/);

    // Exiting restores exactly what fog took away.
    await page.getByRole("button", { name: "Exit fog" }).click();
    await expect(perspective).toHaveText("Omniscient");
    await expect(roleBadges).toHaveCount(omniscientRoleCount);
    await expect(page).not.toHaveURL(/[?&]perspective=p-\d+\b/);
  });

  test("reduced motion collapses DOM transitions and is visible to the canvas layer", async ({
    browser,
  }) => {
    // A CONTRAST, not a single reading: asserting "duration is ~0 under reduce"
    // alone would also pass if the element simply had no transition at all.
    async function probe(reducedMotion: "reduce" | "no-preference") {
      const context = await browser.newContext({ reducedMotion });
      const page = await context.newPage();
      await page.addInitScript((key) => {
        window.localStorage.setItem(key, "1");
      }, TOUR_SEEN_KEY);
      await page.goto("/");
      const tab = page.getByRole("button", { name: "Highlights" });
      await expect(tab).toBeVisible();
      const reading = await tab.evaluate((element) => ({
        // The DOM-side blanket reset (src/index.css).
        transitionSeconds: Number.parseFloat(
          getComputedStyle(element).transitionDuration,
        ),
        // The SAME preference the Pixi layer reads directly to snap token
        // tweens, the vent dive, and the kill flash (MapView.tsx) — the canvas
        // has no CSS to reset, so this media query is its only signal.
        canvasSignal: window.matchMedia("(prefers-reduced-motion: reduce)").matches,
      }));
      await context.close();
      return reading;
    }

    const reduced = await probe("reduce");
    const normal = await probe("no-preference");

    expect(normal.transitionSeconds).toBeGreaterThan(0.05);
    expect(reduced.transitionSeconds).toBeLessThan(0.005);
    expect(normal.canvasSignal).toBe(false);
    expect(reduced.canvasSignal).toBe(true);
  });
});
