# Decision: visitor-facing wording, 2026-10-11

The project reached its finished state on 2026-10-10 (`audits/audit-2026-10-10-finalized-state.md`). On the same day
the owner ruled that the viewer header's attribution line goes (card `viewer-header-source-link`) and asked which other
visitor-facing wording had been set by default. The orchestrator surveyed every surface a visitor sees; the survey, with
its 25 numbered decisions and options, is kept verbatim at
[`tasks/decisions-2026-10-11-visitor-wording/survey.md`](decisions-2026-10-11-visitor-wording/survey.md) (read at
`fa213381`). On 2026-10-11 the owner answered each by number. This document records the answers verbatim, the
orchestrator's readings where an answer needs one, and the cards that carry them. The doctrine holds throughout:
role-correctness is reported and never a gate; copy carries no task or audit id, no unexplained term and no threshold
arithmetic; records are never rewritten.

## 1. The owner's answers (verbatim, 2026-10-11)

> UX decisions:
>
> 1. B
> 2. A
> 3. A
> 4. B
> 5. B
> 6. B
> 7. B
> 8. B
> 9. B
> 10. B
> 11. B
> 12. B
> 13. B
> 14. B
> 15. B
> 16. Keep the byline, but don't have to  specify what each agent did, because the roles changed throughout so less
>     might be more.
> 17. I think go with GIF / Hero Images. The Video is a lot of work for little payoff when a viewer can go right to the
>     demo page anyway. Remove the WebM
> 18. B. Plain words, focus on readability and air on brevity.
> 19. A
> 20. C
> 21. A
> 22. C
> 23. B
> 24. B
> 25. B

The letters are the survey's options for each numbered item; (a) is always "keep as is".

## 2. Readings (the orchestrator's, labelled)

- **16, the README byline.** The byline line stays. The "Who did what" passage that names what each agent did is
  replaced by one sentence that does not divide the work by agent, since the roles changed over time; nothing
  elsewhere attributes work by agent. Less is more, as the owner put it.
- **17, the README picture.** The hero still stays as the README's first image, the journey GIF is shown in the README
  below it (GitHub plays a GIF inline), and the WebM clip is removed: the file under `docs/media/`, its README link,
  its capture in the media spec, its provenance entry and its media-table row. The demo page is the moving picture.
- **18, README terms.** Option (b) with the owner's emphasis: plain words, readability first, brevity over
  completeness. Identifiers a stranger does not need move to the manifests; the doc-facts checks that pin them follow
  the new text, never weaken.
- **20, the missed-bar paragraphs.** Option (c): one plain sentence on the README with a link; the figures and verdict
  words move to `docs/history.md`, where `check_verdict_figures` keeps holding them.
- **21, the owner's voice.** Confirmed as written: the "confirm wording" marker on `docs/lessons.md` is removed and the
  text stays in the first person.
- **22, the ownership case study.** Kept, with one recent decision added from the records: the orchestrator's reading
  is the ruling of 2026-10-09 "Keep the comparison records" (decision memo 8.9), which declined the orchestrator's
  proposal that each promotion delete the previous round's candidate copy; the card writes it from the memo and the
  promotion card's Results, in the case study's existing form.
- **Everything else** takes the survey's (b) text, or keeps as is where the answer is (a): 2, 3, 19.

## 3. The cards

Three cards carry the answers; each is a house card under `tasks/work/`, implemented on its own branch with one pull
request, verified by the three lenses, and merged by the orchestrator (each merge publishes through
`.github/workflows/pages.yml`; the owner's answers above are the publication decision).

| Card | Items | Surfaces |
|---|---|---|
| `viewer-browse-wording` | 1 (the tab title and share text), 4, 5, 6, 7, 8, 9, 25 | `frontend/index.html`, navigation, the replay browser, the workspace, the endings, the local dashboard leftovers |
| `viewer-meeting-results-wording` | 3, 10, 11, 12, 13, 14, 15 | the meeting view, ballots, the inspector and belief panel, the Results tab |
| `front-door-plain-words` | 1 (the README tagline), 4 (the README link), 16, 17, 18, 20, 21, 22, 23, 24 | `README.md`, `docs/reading-guide.md`, `docs/history.md`, `docs/lessons.md`, `docs/ownership-case-study.md`, `SECURITY.md`, `CONTRIBUTING.md`, `docs/media/`, the doc-facts checks |

Order: `viewer-header-source-link` merges first (it re-captures the media the front-door card then trims). The two
viewer cards share `frontend/src/lib/copy.ts` and its test; `viewer-browse-wording` merges first and
`viewer-meeting-results-wording` merges `main` before its final review. The front-door card runs beside them and
merges last, so its stills and counts read the shown set as it is.

What stays the owner's, unchanged by this document: the three viewer halves held since the baselines memo (the local
dashboard's "gate" vocabulary and the "vote gate" badge; the belief panel's Error-layer words and the "correct /
incorrect" ballot badge; how the local dashboard reads skips).
