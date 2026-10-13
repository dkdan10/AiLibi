# Decision: the public demo carries every sample game, 2026-10-13

**Status: relayed, pending the owner's merge.** The session that implemented the change wrote this record from the
direction relayed to it; it does not quote the owner. It stands only when the owner merges the pull request that carries
it, and that merge is its confirming signature. Until then nothing is published.

**The direction, as relayed.** On 2026-10-13, in a Claude Code session, the owner directed that the public demo carry
every committed sample game of every set under `replays/samples/` (all 100) instead of the five featured ones. The
featured list stays as the opener: `FEATURED_GAMES` in `frontend/src/components/ReplayPicker.tsx` remains the picker's
Featured strip and the guided tour's first game, and the build fails if one of them has no recording to bake.

**Why this needs a record.** A push to `main` rebuilds and publishes the demo bundle (`.github/workflows/pages.yml`), so
under `AGENTS.md` a change to the featured games or the public-results payload is a publication decision
([deployment](../../docs/deployment.md)).

**What is published.** The same post-game view already served for the featured games (replay, belief frames, meetings,
per-agent memories and rendered prompts, plus each set's picker metadata, compact results and game-shape profile), now
for every game, over recordings already public in `replays/samples/`. Nothing new is recorded and no live endpoint is
added.

**The publication act.** Pull request #515, opened from the owner's GitHub account on 2026-10-13, carries the change.
Merging it to `main` is the publication act under `AGENTS.md`; declining to merge declines the publication.
