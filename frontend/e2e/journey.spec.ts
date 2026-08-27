// THE spectator journey (Task 19.12) — one spec file, one browser.
//
// It drives the REAL app against the REAL API serving the REAL committed sample
// set: featured replay → play → meeting pause → inspect ballots → finale
// (unspoiled → reveal), plus pins on behaviors that already work and must keep
// working — the keyboard transport, the As-agent fog firewall, reduced motion,
// the single focus-trap owner when overlays stack, and the transport dock
// leaving the map on screen at laptop viewport heights.
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

/**
 * The guided tour's dialog.
 *
 * Picked by a control the tour OWNS rather than by its title: the meeting, the
 * Belief × Truth matrix and the tour all render `role="dialog"`, and the tour's
 * `aria-labelledby` heading changes on every step while its close button does
 * not.
 */
function tourDialog(page: Page) {
  return page
    .getByRole("dialog")
    .filter({ has: page.getByRole("button", { name: "Close the guided tour" }) });
}

/**
 * Open the guided tour OVER whatever overlay is already on screen, through the
 * app's own re-open channel (`GuidedTour.tsx`).
 *
 * Not through the header's Tour button, because the stacked case is exactly the
 * case where that button cannot be clicked: the shell unmounts the header while
 * a meeting is open, and the Belief × Truth overlay's full-viewport scrim covers
 * it. This dispatches the same event `openGuidedTour()` does.
 */
async function openGuidedTourOverOverlay(page: Page): Promise<void> {
  await page.evaluate(() => {
    window.dispatchEvent(new CustomEvent("ailibi:open-guided-tour"));
  });
  await expect(tourDialog(page)).toBeVisible();
}

/**
 * Press `key` `presses` times and report, after each press, the focused
 * control's label and whether focus is still inside the tour.
 *
 * Read from `document.activeElement` rather than asserted on a locator, because
 * the defect this pins is about WHICH element focus lands on across a whole
 * ring — including the transient landings inside the scrim-covered overlay
 * behind, which a per-locator focus assertion cannot see.
 */
async function walkFocusRing(
  page: Page,
  key: "Tab" | "Shift+Tab",
  presses: number,
): Promise<{ label: string; insideTour: boolean }[]> {
  const visited: { label: string; insideTour: boolean }[] = [];
  for (let index = 0; index < presses; index += 1) {
    await page.keyboard.press(key);
    visited.push(
      await page.evaluate(() => {
        const close = document.querySelector('[aria-label="Close the guided tour"]');
        const dialog = close === null ? null : close.closest('[role="dialog"]');
        const active = document.activeElement;
        return {
          label: active === null ? "" : (active.textContent ?? "").trim(),
          insideTour: dialog !== null && active !== null && dialog.contains(active),
        };
      }),
    );
  }
  return visited;
}

/**
 * With the tour stacked over `behind`, assert that ONE trap owns Tab: the whole
 * ring of tour controls is reachable in both directions and focus never lands in
 * the overlay underneath.
 *
 * Two traps both listening on `window` produce `Tab -> Skip` forever (the lower
 * trap pulls focus into itself, the tour's pulls it back to its own first
 * control), so "Back is reachable" is the symptom and the WHOLE ring is the
 * check.
 */
async function expectTourOwnsTab(page: Page, behind: ReturnType<Page["getByRole"]>) {
  const tour = tourDialog(page);

  // Step forward once first: on the opening step "Back" is disabled and so is
  // correctly outside the ring, which would hide the very control the defect
  // makes unreachable.
  await tour.getByRole("button", { name: "Next" }).click();
  // A step change hands focus back to the card, so the ring below starts from a
  // known place rather than from wherever the click left it.
  await expect
    .poll(() =>
      page.evaluate(() => document.activeElement?.getAttribute("role") ?? ""),
    )
    .toBe("dialog");

  const controls = (await tour.getByRole("button").allInnerTexts()).map((text) =>
    text.trim(),
  );
  expect(controls).toHaveLength(3);
  expect(controls).toContain("Back");

  const forward = await walkFocusRing(page, "Tab", controls.length * 2);
  expect(forward.map((visit) => visit.label)).toEqual([...controls, ...controls]);
  expect(forward.map((visit) => visit.insideTour)).toEqual(forward.map(() => true));

  // Focus ended on the last control; walking back visits the same ring in
  // reverse, wrapping at the first.
  const backwardLabels: string[] = [];
  let cursor = controls.length - 1;
  for (let index = 0; index < controls.length * 2; index += 1) {
    cursor = (cursor - 1 + controls.length) % controls.length;
    backwardLabels.push(controls[cursor]!);
  }
  const backward = await walkFocusRing(page, "Shift+Tab", controls.length * 2);
  expect(backward.map((visit) => visit.label)).toEqual(backwardLabels);
  expect(backward.map((visit) => visit.insideTour)).toEqual(backward.map(() => true));

  // Escape still belongs to the tour alone — the overlay behind yields it and
  // stays open.
  await page.keyboard.press("Escape");
  await expect(tour).toBeHidden();
  await expect(behind).toBeVisible();
}

/** The dock's disclosure control (the transport row's Timeline toggle). */
function timelineDisclosure(page: Page) {
  return page.getByRole("button", { name: "Timeline", exact: true });
}

/**
 * The map's and the dock's boxes, plus the height the dock publishes.
 *
 * `.map-canvas-fill` is the map's stable handle (`src/index.css`); the Pixi
 * canvas inside it is CSS-scaled to the stage width, so the wrapper IS the
 * on-screen map.
 */
async function mapAndDockGeometry(page: Page) {
  return page.evaluate(() => {
    const map = document.querySelector(".map-canvas-fill");
    const dock = document.querySelector("[data-transport-region]");
    if (map === null || dock === null) {
      throw new Error("the map wrapper or the transport region is not mounted");
    }
    const mapBox = map.getBoundingClientRect();
    const dockBox = dock.getBoundingClientRect();
    return {
      mapTop: Math.round(mapBox.top),
      mapBottom: Math.round(mapBox.bottom),
      dockTop: Math.round(dockBox.top),
      // The ResizeObserver measures the CONTENT box, which for this borderless-
      // inside container is `clientHeight`.
      dockContentHeight: dock.clientHeight,
      viewportHeight: window.innerHeight,
      transportH: Number.parseFloat(
        getComputedStyle(document.documentElement).getPropertyValue("--transport-h"),
      ),
    };
  });
}

/** Scroll the map to the top of the viewport — its best case against the dock. */
async function scrollMapToTop(page: Page): Promise<void> {
  await page.evaluate(() => {
    document
      .querySelector(".map-canvas-fill")
      ?.scrollIntoView({ block: "start", behavior: "instant" });
  });
}

/**
 * Geometry once the dock's `ResizeObserver` has republished its height — and the
 * assertion that it republished the REAL one, which is what makes collapsing the
 * dock reflow the overlays that reserve `--transport-h`.
 */
async function settledGeometry(page: Page) {
  await expect
    .poll(async () => {
      const geometry = await mapAndDockGeometry(page);
      return Math.abs(geometry.transportH - geometry.dockContentHeight);
    })
    .toBeLessThanOrEqual(1);
  return mapAndDockGeometry(page);
}

/**
 * The arrival promise as ONE predicate: the whole map is on screen and clear of
 * the dock. Returned as a named breakdown so a failure says which half broke.
 */
function mapWhollyVisible(geometry: {
  mapTop: number;
  mapBottom: number;
  dockTop: number;
  viewportHeight: number;
}) {
  return {
    topOnScreen: geometry.mapTop >= 0,
    bottomOnScreen: geometry.mapBottom <= geometry.viewportHeight,
    clearOfDock: geometry.mapBottom <= geometry.dockTop,
  };
}

/** Every half of the promise holding. */
const MAP_WHOLLY_VISIBLE = {
  topOnScreen: true,
  bottomOnScreen: true,
  clearOfDock: true,
} as const;

/**
 * The viewport height at which the dock opens its timeline half, read back out
 * of its ONE home in `src/index.css` — so the arrival test asserts the drawer
 * state AGAINST the threshold instead of hardcoding a second copy of it.
 */
async function expandedMinHeight(page: Page): Promise<number> {
  return page.evaluate(() =>
    Number.parseFloat(
      getComputedStyle(document.documentElement).getPropertyValue(
        "--transport-expanded-min-height",
      ),
    ),
  );
}

/** The Task-19.17 tail surfaces: the running beat feed and the spend chips. */
function ticker(page: Page) {
  return page.getByRole("region", { name: "Event ticker" });
}

function costChips(page: Page) {
  return page.getByRole("group", { name: "LLM cost to the current frame" });
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

    // ── the tail surfaces open EMPTY (Task 19.17) ────────────────────────────
    // This is the frame-bounding, stated where it is easiest to see it fail: at
    // the synthetic Start frame nothing has played, so the feed is empty and the
    // chips are zero. A GAME TOTAL — the thing these chips must never be — would
    // already read the whole game's token spend right here, before a tick.
    await expect(ticker(page)).toContainText("Nothing has happened yet.");
    await expect(costChips(page)).toContainText("in 0 tok");
    await expect(costChips(page)).toContainText("out 0 tok");

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

    // ── the tail surfaces followed the playhead (Task 19.17) ─────────────────
    // The feed carries the beat the transport just stopped on, and the chips
    // moved off zero at exactly the frame the meeting's calls entered the
    // window. Both are still frame-bounded — this is the SAME cumulative number
    // as before, one meeting later, not a total that was always there.
    await expect(ticker(page)).toContainText(/Meeting called by p-\d+/);
    await expect(costChips(page)).toContainText(/in [1-9][\d,]* tok/);
    await expect(costChips(page)).not.toContainText("in 0 tok");

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

    // ── the reconstruction half ──────────────────────────────────────────────
    // The dialog's other half is what the viewer exists for — the accusation
    // chain, the turn cards, the evidence taxonomy — and the gate used to stop at
    // the ballots, so a regression anywhere in it shipped green.
    const transcript = meeting.getByRole("region", {
      name: "Accusation chain & transcript",
    });
    await expect(transcript).toBeVisible();
    // A turn card really rendered (`TurnCard`'s article), so "the panel is on
    // screen" cannot pass over an empty transcript.
    await expect(transcript.getByRole("article").first()).toBeVisible();

    // The evidence readout has to RECONCILE: `Evidence (N)` equals the sum of
    // its group counts, and every group is one of the three taxonomy headings.
    // `EvidenceSection` renders nothing at all on an empty flag list, so the
    // empty meeting falls out of the same arithmetic instead of being skipped —
    // no `Evidence` heading has to mean no group heading, i.e. 0 = 0.
    //
    // Located by heading LEVEL, not by a name pattern: a name-filtered locator
    // can only ever match the headings it already expects, which would make "every
    // group heading is one of the three" vacuous. `EvidenceSection`'s are the only
    // h4 and h5 anywhere in this panel, so neither locator can drift. Read as text
    // CONTENT, not innerText — the headings are CSS-uppercased, and innerText
    // would hand back the transformed string.
    const evidenceHeadings = await transcript.getByRole("heading", { level: 4 }).allTextContents();
    const groupHeadings = await transcript.getByRole("heading", { level: 5 }).allTextContents();

    expect(evidenceHeadings.length).toBeLessThanOrEqual(1);
    const declared = evidenceHeadings.map((text) => {
      const parsed = /^Evidence \((\d+)\)$/.exec(text.trim());
      if (parsed === null) {
        throw new Error(`the evidence heading does not read "Evidence (N)": ${text}`);
      }
      return Number(parsed[1]);
    });
    const grouped = groupHeadings.map((text) => {
      const parsed = /^(Role proof|Contradictions|Weak signals) \((\d+)\)$/.exec(text.trim());
      if (parsed === null) {
        throw new Error(`"${text.trim()}" is not one of the three evidence taxonomy headings`);
      }
      return Number(parsed[2]);
    });
    expect(grouped.reduce((sum, n) => sum + n, 0)).toBe(
      declared.reduce((sum, n) => sum + n, 0),
    );
    // …and a heading only exists when a group does, in both directions.
    expect(declared.length === 0).toBe(grouped.length === 0);

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

  test("the guided tour owns Tab when it stacks over another overlay", async ({
    page,
  }) => {
    await openFeaturedReplay(page);

    // ── stack 1: over the Belief × Truth matrix ──────────────────────────────
    // Its launcher is the one a spectator reaches by pointer; the tour then has
    // to come from its own re-open channel, because the matrix's scrim covers
    // the header the Tour button lives in.
    await page.getByRole("button", { name: "Open the Belief × Truth matrix" }).click();
    const matrix = page.getByRole("dialog", { name: "Belief × Truth matrix" });
    await expect(matrix).toBeVisible();
    await openGuidedTourOverOverlay(page);
    await expectTourOwnsTab(page, matrix);
    await page.keyboard.press("Escape");
    await expect(matrix).toBeHidden();

    // ── stack 2: over an open meeting ────────────────────────────────────────
    await resetFocus(page);
    await page.keyboard.press("]");
    const meeting = page.getByRole("dialog", { name: /Meeting at tick \d+/ });
    await expect(meeting).toBeVisible();
    await openGuidedTourOverOverlay(page);
    await expectTourOwnsTab(page, meeting);
  });

  test("the transport dock leaves the map on screen at laptop heights", async ({
    page,
  }) => {
    await openFeaturedReplay(page);

    // The review's clean case (1440×900 and up, which the config's 1440×960
    // viewport is) keeps today's full dock.
    const disclosure = timelineDisclosure(page);
    await expect(disclosure).toHaveAttribute("aria-expanded", "true");

    // ── 1280×800: the map lands whole, unscrolled, above the dock ────────────
    // The review measured the dock eating the bottom of the map here. Asserted at
    // the scroll position a visitor ARRIVES at, which is the position the review
    // measured and the one the README recording shows.
    await page.setViewportSize({ width: 1280, height: 800 });
    await expect(disclosure).toHaveAttribute("aria-expanded", "false");
    await page.evaluate(() => {
      window.scrollTo(0, 0);
    });
    // `settledGeometry` also pins `--transport-h` to the dock's real height in
    // the collapsed state.
    const laptop = await settledGeometry(page);
    expect(laptop.mapTop).toBeGreaterThanOrEqual(0);
    expect(laptop.mapBottom).toBeLessThanOrEqual(laptop.viewportHeight);
    expect(laptop.mapBottom).toBeLessThanOrEqual(laptop.dockTop);

    // ── 1000×640: the recording viewport, at the map's best scroll ───────────
    // 640 px cannot hold the whole page, so the honest question is whether ANY
    // scroll position shows the whole map. With the un-collapsed dock the answer
    // was no — it was taller than the room it left above itself.
    await page.setViewportSize({ width: 1000, height: 640 });
    await expect(disclosure).toHaveAttribute("aria-expanded", "false");
    await scrollMapToTop(page);
    const recording = await settledGeometry(page);
    expect(recording.mapTop).toBeGreaterThanOrEqual(0);
    expect(recording.mapBottom).toBeLessThanOrEqual(recording.dockTop);

    // ── `--transport-h` still measures the real dock in BOTH states ──────────
    // Which is the whole mechanism: the overlays reserve the measured height, so
    // collapsing the dock un-clips the mind rail and the meeting modal with no
    // constant to keep in step.
    const collapsed = await settledGeometry(page);
    expect(collapsed.transportH).toBeGreaterThan(0);

    await disclosure.click();
    await expect(disclosure).toHaveAttribute("aria-expanded", "true");
    const expanded = await settledGeometry(page);
    expect(expanded.transportH).toBeGreaterThan(collapsed.transportH);

    // A deliberate toggle wins over the height default for the rest of the
    // session — closing it here keeps it closed on a viewport that would have
    // opened it.
    await disclosure.click();
    await expect(disclosure).toHaveAttribute("aria-expanded", "false");
    await page.setViewportSize({ width: 1440, height: 960 });
    await expect(disclosure).toHaveAttribute("aria-expanded", "false");
  });

  // The most common desktop arrival. Both legs of the test above run against a
  // COLLAPSED dock — 800 and 640 are below `--transport-expanded-min-height`, so
  // the shell opens shorter and the spec asserts that before it measures. 900 is
  // the height the dock is EXPANDED at, and until now nothing measured it.
  test.describe("the 1440×900 arrival", () => {
    test.use({ viewport: { width: 1440, height: 900 } });

    test("shows the whole map, clear of the dock, with no scroll and no toggle", async ({
      page,
    }) => {
      await openFeaturedReplay(page);

      // What a visitor is owed is the PROMISE — the whole map on screen and clear
      // of the dock at the position they land on — not a particular dock state.
      // So nothing here scrolls and nothing toggles.
      const arrival = await settledGeometry(page);
      expect(mapWhollyVisible(arrival)).toEqual(MAP_WHOLLY_VISIBLE);

      // Whether the drawer is open at 900 is a layout ruling that lives in ONE
      // place. Reading the threshold back out of the sheet keeps this true from
      // either side of it instead of pinning a second copy of the number here.
      const threshold = await expandedMinHeight(page);
      await expect(timelineDisclosure(page)).toHaveAttribute(
        "aria-expanded",
        String(arrival.viewportHeight >= threshold),
      );

      // ── the case that proves the predicate can say no ──────────────────────
      // A green arrival is only a fact about the layout if the same predicate
      // returns false somewhere. 1000×640 with the drawer deliberately opened is
      // the state the review measured: the dock is taller than the room it
      // leaves above itself, so no scroll position fits the whole map.
      await page.setViewportSize({ width: 1000, height: 640 });
      const disclosure = timelineDisclosure(page);
      await expect(disclosure).toHaveAttribute("aria-expanded", "false");
      await disclosure.click();
      await expect(disclosure).toHaveAttribute("aria-expanded", "true");
      await scrollMapToTop(page);
      const buried = await settledGeometry(page);
      expect(mapWhollyVisible(buried)).not.toEqual(MAP_WHOLLY_VISIBLE);
    });
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

    // ── the ticker rides the SAME projection (Task 19.17) ────────────────────
    // The served event views are PRIVILEGED — `KillEventView` carries
    // `killer_id`, `VentEventView` carries the whole route — so a feed that
    // printed them verbatim would publish exactly what this test's other
    // assertions prove the fog withholds. Walk to the end first, because at
    // frame zero the feed is (correctly) empty and proves nothing.
    //
    // Auto-follow OFF and the end-of-replay card dismissed: both would otherwise
    // sit over the map toolbar that owns the As-agent switch. Neither is
    // incidental to the ticker — this is the pause/finale flow being driven, and
    // it still behaves exactly as Task 19.10 left it.
    await page.getByRole("button", { name: "Auto-follow on" }).click();
    await resetFocus(page);
    await page.keyboard.press("End");
    await page.getByRole("button", { name: "Dismiss the end-of-replay card" }).click();

    await expect(ticker(page)).toContainText("omniscient");
    await expect(ticker(page)).toContainText(/p-\d+ killed p-\d+/);
    const omniscientRows = await ticker(page).getByRole("listitem").allInnerTexts();
    const omniscientBeats = omniscientRows.length;
    expect(omniscientBeats).toBeGreaterThan(0);

    // No vent route may name the same room twice. On a real traversal the engine
    // repeats the SOURCE in the dive event's `to_room_id` — the destination is
    // only resolved on the exit event — so a route read off the dive renders
    // `STORAGE → STORAGE`. Unit fixtures can encode the right byte shape, but
    // only the committed corpus proves the shape; this is the guard that reads
    // it. Vacuous on a game with no vents, which is the correct behaviour.
    for (const row of omniscientRows) {
      const route = /([A-Z_]+) → ([A-Z_]+)/.exec(row);
      if (route !== null) {
        expect(route[1]).not.toBe(route[2]);
      }
    }

    await page.getByRole("button", { name: "As-agent" }).click();
    await expect(ticker(page)).toContainText(/as p-\d+ · fog/);
    // A re-projection, not a styling change: the fog feed is a SUBSET. WHICH
    // beats survive depends on which agent the switcher lands on and what it
    // happened to see, so the four exact fog cases (witnessed/unwitnessed ×
    // kill/vent) are pinned deterministically in
    // `src/components/EventTicker.test.ts`; what only a browser can show is that
    // the live switch really re-runs the projection over the real bytes.
    const foggedBeats = await ticker(page).getByRole("listitem").count();
    expect(foggedBeats).toBeLessThanOrEqual(omniscientBeats);
    // No vent ROUTE survives the fog, for any agent: a witness at one mouth of
    // the network never saw where the actor came out, so the `from → to` line
    // the Omniscient feed renders has no fogged form at all.
    await expect(ticker(page)).not.toContainText("→");

    await page.getByRole("button", { name: "Exit fog" }).click();
    await expect(ticker(page)).toContainText("omniscient");
    expect(await ticker(page).getByRole("listitem").count()).toBe(omniscientBeats);
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
