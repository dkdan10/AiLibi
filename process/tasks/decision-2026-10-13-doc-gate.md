# Decision: the doc gate checks the README's figures, 2026-10-13

**Status: relayed, pending the owner's merge.** Written from the owner's direction in a Claude Code session; it does not
quote the owner, and the merge that carries it is its signature.

**The direction.** `scripts/check_doc_facts.py` keeps only the checks that recompute the README's figures from the files
that own them: the samples paragraph, the results table, the real-report example, the prose figures, the ML page's results
table, the two `.env.example` registries and relative links.

**What went, and why.** The other checks held pages in place because the pages existed, not because a README figure
depended on them: which baseline is current, the vote-correctness docstring's numbers, the list of private words, phase
and audit-index coverage, agreement between the README and reading-guide tables, as-of dates, line citations, the
guide's narrative and featured games, the phase-21 verdict figures and close map, the review map, word budgets, the ML
corpus disclosures, row order, number style, and the 34-case wording pin, now a short pin on the README's title, byline
and two honesty phrases.

**What changed source.** The vent and proof rows read the generated gameplay census instead of hand-copied audit tables.
The win-rate and proof Before cells are frozen once in `docs/results-before.json`, pinned by its sha256. The reading guide
links the README's table instead of repeating it. Relative links moved to `scripts/check_links.py`, which reads the live
pages and the five record pages the front door sends a reader to.

**What is no longer checked.** The Before cells of the replay, citation and vent rows were held only to the reading
guide's copy of the table; with that copy gone they are unchecked text.
