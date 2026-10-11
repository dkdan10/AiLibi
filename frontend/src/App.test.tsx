// The shell header and the guided tour's welcome step, rendered.
//
// Both carry one link to the repository and nothing about who made what: the
// header reads the name, the tagline and a link whose text is "GitHub", and the
// welcome step keeps the same link in a sentence of its own. Each render is held
// to `HEADER_COPY` here; `lib/copy.test.ts` holds the copy tree and the two
// sources to the same words.

import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { ShellTitle } from "./App";
import { STEPS } from "./components/GuidedTour";
import { HEADER_COPY } from "./lib/copy";

/** The removed attribution line's words, the same five `lib/copy.test.ts` refuses. */
const ATTRIBUTION_WORDS = /\bdirected by|Claude Code|Codex|AI-reviewed|ownership/i;

/** Markup reduced to the text a reader sees. */
function textOf(html: string): string {
  return html
    .replace(/<[^>]*>/g, "")
    .replaceAll("&#x27;", "'")
    .replaceAll("&quot;", '"')
    .replaceAll("&lt;", "<")
    .replaceAll("&gt;", ">")
    .replaceAll("&amp;", "&");
}

/** Every link in the markup: where it points and what it says. */
function linksOf(html: string): readonly { readonly href: string | null; readonly text: string }[] {
  return [...html.matchAll(/<a\b([^>]*)>([\s\S]*?)<\/a>/g)].map((match) => ({
    href: /\bhref="([^"]*)"/.exec(match[1] ?? "")?.[1] ?? null,
    text: textOf(match[2] ?? ""),
  }));
}

/** What differs from the header the copy describes; empty when they agree. */
function titleProblems(html: string): readonly string[] {
  const problems: string[] = [];
  const heading = /<h1\b[^>]*>([\s\S]*?)<\/h1>/.exec(html)?.[1];
  if (heading === undefined || textOf(heading) !== "AiLibi") {
    problems.push(`the heading reads ${String(heading)}`);
  }
  const links = linksOf(html);
  if (
    links.length !== 1 ||
    links[0]?.text !== HEADER_COPY.sourceLinkText ||
    links[0]?.href !== HEADER_COPY.sourceUrl
  ) {
    problems.push(`the links are ${JSON.stringify(links)}`);
  }
  const text = textOf(html);
  if (text !== `AiLibi${HEADER_COPY.tagline} · ${HEADER_COPY.sourceLinkText}`) {
    problems.push(`the header reads ${text}`);
  }
  const hit = ATTRIBUTION_WORDS.exec(text);
  if (hit !== null) {
    problems.push(`the header says ${hit[0]}`);
  }
  return problems;
}

/** What differs from the welcome step the copy describes; empty when they agree. */
function welcomeProblems(html: string): readonly string[] {
  const problems: string[] = [];
  const links = linksOf(html);
  if (
    links.length !== 1 ||
    links[0]?.text !== HEADER_COPY.tourSourceLinkText ||
    links[0]?.href !== HEADER_COPY.sourceUrl
  ) {
    problems.push(`the links are ${JSON.stringify(links)}`);
  }
  const hit = ATTRIBUTION_WORDS.exec(textOf(html));
  if (hit !== null) {
    problems.push(`the step says ${hit[0]}`);
  }
  return problems;
}

function welcomeHtml(): string {
  const welcome = STEPS[0];
  if (welcome === undefined) throw new Error("the tour has no welcome step");
  return renderToStaticMarkup(<>{welcome.body}</>);
}

describe("the shell header", () => {
  const html = renderToStaticMarkup(<ShellTitle />);

  it("reads the name, the tagline and one link to the source, from the copy", () => {
    expect(titleProblems(html)).toEqual([]);
    expect(textOf(html)).toBe("AiLibiRecorded AI social deduction · GitHub");
  });

  it("names the attribution, a second link or another tagline when one returns (planted)", () => {
    const attributed = html.replace(
      HEADER_COPY.tagline,
      `${HEADER_COPY.tagline} · directed by Daniel Keinan`,
    );
    expect(attributed).not.toBe(html);
    expect(titleProblems(attributed)).toEqual([
      `the header reads AiLibi${HEADER_COPY.tagline} · directed by Daniel Keinan · GitHub`,
      "the header says directed by",
    ]);
    const twoLinks = html.replace("</p>", ' <a href="https://example.test">More</a></p>');
    expect(twoLinks).not.toBe(html);
    expect(titleProblems(twoLinks)).toHaveLength(2);
    expect(titleProblems(twoLinks)[0]).toMatch(/^the links are /);
    const linkText = html.replace(`>${HEADER_COPY.sourceLinkText}</a>`, ">Source &amp; ownership</a>");
    expect(linkText).not.toBe(html);
    expect(titleProblems(linkText)).toEqual([
      `the links are ${JSON.stringify([{ href: HEADER_COPY.sourceUrl, text: "Source & ownership" }])}`,
      `the header reads AiLibi${HEADER_COPY.tagline} · Source & ownership`,
      "the header says ownership",
    ]);
  });

  it("names the heading when its name changes or another tag carries it (planted)", () => {
    const renamed = html.replace(">AiLibi</h1>", ">AiLibi Studio</h1>");
    expect(renamed).not.toBe(html);
    expect(titleProblems(renamed)).toEqual([
      "the heading reads AiLibi Studio",
      `the header reads AiLibi Studio${HEADER_COPY.tagline} · ${HEADER_COPY.sourceLinkText}`,
    ]);
    const demoted = html.replace(/<h1\b([^>]*)>AiLibi<\/h1>/, "<h2$1>AiLibi</h2>");
    expect(demoted).not.toBe(html);
    expect(titleProblems(demoted)).toEqual(["the heading reads undefined"]);
  });
});

describe("the guided tour's welcome step", () => {
  const html = welcomeHtml();

  it("keeps one plain link to the source and says nothing about who made what", () => {
    expect(welcomeProblems(html)).toEqual([]);
    const opening = /<p\b[^>]*>([\s\S]*?)<\/p>/.exec(html)?.[1] ?? "";
    expect(textOf(opening)).toBe(
      "AiLibi asks whether AI agents can reason from what they actually saw. You are watching saved games, not making live model calls. Read the source on GitHub.",
    );
  });

  it.each(["directed by", "Claude Code", "Codex", "AI-reviewed", "ownership"])(
    "names %s wherever it returns in the step (planted)",
    (word) => {
      const planted = html.replace(
        "not making live model calls.",
        `not making live model calls. ${word}`,
      );
      expect(planted).not.toBe(html);
      expect(welcomeProblems(planted)).toEqual([`the step says ${word}`]);
    },
  );

  it("names the old sentence or the old link when either returns (planted)", () => {
    const sentence = html.replace(
      "not making live model calls.",
      "not making live model calls. Daniel Keinan directs the project; Claude Code and Codex agents write code and supporting material, with separate AI review.",
    );
    expect(sentence).not.toBe(html);
    expect(welcomeProblems(sentence)).toEqual(["the step says Claude Code"]);
    const link = html.replace(
      `>${HEADER_COPY.tourSourceLinkText}</a>`,
      ">Read the source and ownership case study.</a>",
    );
    expect(link).not.toBe(html);
    expect(welcomeProblems(link)).toEqual([
      `the links are ${JSON.stringify([{ href: HEADER_COPY.sourceUrl, text: "Read the source and ownership case study." }])}`,
      "the step says ownership",
    ]);
  });
});
