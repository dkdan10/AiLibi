# Stage-B candidate round 1 — the record and its assessment (2026-09-27)

Card: [`tasks/work/stage-b-record-r1.md`](../tasks/work/stage-b-record-r1.md).
Frozen head: `main` at `f937dfaa`, the merge of PR #491, the last Stage-B
implementation card. Branch `work/stage-b-record-r1`, one pull request into
`main`, merged by the owner.

This record makes one 50-seed candidate round: seeds 0-49 of the 9-player
sample roster (9 players, 2 impostors, 2 tasks per crewmate), recorded once on
featherless `Qwen/Qwen3.6-27B` with the prompt set `qwen3_6_27b`, the bare
substrate slate and one declared experiment config that turns every Stage-B
switch on, into `replays/candidates/stage-b-r1/9p2i/`. It decides nothing. It
reads the round against questions fixed before the first seed, beside the
shipped baseline-9 numbers for the same seeds, never pooled with them. The
ladder tip stands at baseline 9; the round adopts nothing, publishes nothing,
and each switch's next step is the owner's decision after reading it.

Role-correct ejection and the win split are reported beside the readings and
gate nothing (ruling D1 of
[the direction of 2026-09-19](../tasks/direction-2026-09-19-process-over-outcome.md)
section 12).

## 1. Pre-registration

This section is committed before the first seed, in the `coordination:` commit
the card calls P, and it is never rewritten. A correction lands as a dated
addendum after it, in a later section. The recording checkout is detached at P
itself, so every MANIFEST row of the round stamps P's short sha and
`git merge-base --is-ancestor P <that sha>` exits 0 (1.3).

### 1.1 The owner's confirmation, verbatim and dated

On **2026-09-27**, the owner, relayed verbatim by the orchestrator:

> Confirm the ceilings, v1 and the envelope as proposed

As the orchestrator relays it, this confirms memo 5 items 1, 3 and 4 of
[the Stage-B decision memo](../tasks/decision-2026-09-24-stage-b-wave.md): the
ceilings of the card's Constraints table (1.4); `bounded_rebuttal_version = 1`
as it stands, the one reply going to the target of the earliest unanswered new
charge, whoever that is (a stated deviation from the literal words of the
owner's ruling 4, memo 0.2); and the pre-registered readings and the
non-gating envelope exactly as the card's table states them (1.6, 1.7). It is
the live-call authorization AGENTS.md requires. The landing (memo 5 item 2) is
the orchestrator's ruling of memo 0.3 item 1, `replays/candidates/stage-b-r1/9p2i/`
in-tree; the confirmation does not name it and has not overruled it, and the
owner merged the record-plumbing card that built the candidate family. The
pull request asks the owner to confirm it with the merge.

The owner's record ruling of 2026-09-24, verbatim (memo 0.1):

> Let's not re-record all 300 seeds each time. When it's time to record, record
> the smaller group of 50 seeds, assess if the implementations have been
> effective and resulted in desired results. Also it is understood that updating
> the vent and body reset logic will probably have a substantial effect on
> previous limits and statistics around the baseline voting results, that is
> okay.

### 1.2 The declared config

One line plus a newline, 290 bytes:

```
{"format_version": 1, "meeting_reset": "hub_with_grace", "vent_exit_policy": "look_and_wait", "vent_entry_policy": "own_fresh_kill", "vent_witness_rule": "physical", "bounded_rebuttal_version": 1, "report_body_handle_version": 1, "ballot_kill_row_version": 1, "impostor_ballot_version": 1}
```

`shasum -a 256` on those bytes prints

```
4f0c4dd4779cd38f69194b6735221d86bf7c6944fe12769a3971e38e4e46d6c7
```

which equals the card's figure. At `f937dfaa` the bytes validate as a
`RecordedExperimentConfig` whose fields off their default are exactly eight:
`meeting_reset`, `vent_exit_policy`, `bounded_rebuttal_version`,
`vent_witness_rule`, `vent_entry_policy`, `report_body_handle_version`,
`ballot_kill_row_version` and `impostor_ballot_version`. `self_report` stays
False, `contextual_self_report_version` and `evidence_reasoning_version` stay
None, and the substrate slate is bare (`--expect-levers ""`), so
`reporter_reasoning` is off. `prompt_versions_for_set("qwen3_6_27b",
experiment_config=...)` serves `accusation_round.qwen3_6_27b.v6`,
`crewmate_report.qwen3_6_27b.v6`, `impostor_report.qwen3_6_27b.v6` and
`vote_ballot.qwen3_6_27b.v8.ballot_kill_row_v1+vote_ballot.qwen3_6_27b.v8.impostor_ballot_v1`.
`git grep -n WAVE_ARMS_PENDING -- '*.py'` prints nothing at `f937dfaa`.

The file is not committed here: a round directory without its set directory
fails the candidate test. The delivery commit adds it at
`replays/candidates/stage-b-r1/experiment-config.json`, and its sha256 must
equal the line above. Until then each checkout that reads it holds an untracked
copy whose `shasum -a 256` is checked against that line before any use.

### 1.3 The frozen head and the three checkouts

`F` is `f937dfaa`. P is the commit that adds this section; its tree differs from
`F`'s only in this audit, its `audits/README.md` row and the re-derived
`audits/` row of `docs/artifacts.md`, so the code every seed runs is `F`'s.

- **Recording**: a worktree detached at P, with `uv sync --frozen` and no
  `.env`, which runs only the recorder. No pytest and no `check.sh` run there
  while a leg is live, and no commit is made there, so the recorder's one
  `git rev-parse --short HEAD` per run reads P for the probe and for seeds 1-49
  alike.
- **Verification**: a worktree at `F` for the pre-spend and the gates.
- **Delivery**: the `work/stage-b-record-r1` worktree, which receives the
  checkpoint copies after the probe, after the 10-seed re-projection and after
  the leg.

From the first seed to the merge nothing merges into `engine/`, `agents/` (the
prompt set included), `meetings/`, `observation/`, `orchestrator/`, `eval/`,
`api/`, `scripts/` or `llm/`; if `main` moves there, the record stops and asks.

### 1.4 The ceilings, and their arithmetic

The anchor is the baseline-9 leg of the same seeds
(`audits/audit-2026-09-22-process-rerecord.md` section 2): 145 meetings,
1,694 calls, 9,850,930 input and 422,941 output tokens, 2h24m55s (8,695 s),
`$0.0000`. Per meeting: 11.68 calls, 67,937 input, 2,917 output and 60 s. The
tally command (1.6) prints `1694 9850930 422941 0.0` on
`replays/samples/9p2i` at `F`, so it is the same measure as the anchor. A
rebuttal is one speech call, about 4,714 input and 363 output.

| limit | planning case | ceiling | hard stop at 90% |
|---|---|---|---|
| model calls | 196 x 12.68 = 2,485 | **2,800** | 2,520 |
| input tokens | 196 x (67,937 x 1.10 + 4,714) = 15.57M | **17,500,000** | 15,750,000 |
| output tokens | 196 x (2,917 + 363) = 642,880 | **750,000** | 675,000 |
| recording wall | 196 x 60 s x (12.68 / 11.68) x 1.1 = 14,043 s = 3.9 h | **4.5 h**, inside an **8 h** window | 4.05 h |
| marginal cost | $0 on flat-rate Featherless | **$0.00** | any `cost_usd` other than 0.0000 |

196 is 145 x 1.35, rounded, and 12.68 is 11.68 plus one rebuttal call. The
x1.35 meetings and the +10% prompt growth are unmeasured planning assumptions,
re-measured at the probe. The low case, about 0.72x the meetings with no growth,
is 104.4 meetings, about 1,320 calls and 7.6M input. The cost is `$0.00`
marginal against the flat-rate Featherless subscription, whose standing fee is
already paid and is not incurred by this run.

**Re-projection**, after the probe and after 10 seeds: each count is (the
candidate's total over the completed seeds / the s9 total over the same seeds)
x the s9 leg total, and the wall is the elapsed recording wall / the completed
seeds x 50. Each figure is compared with its 90% stop.

### 1.5 The stop rules

Stop and report to the owner, with the partial output and the last checkpoint,
on:

- any `cost_usd` other than 0.0000, or a re-projection past 90% of a ceiling;
- a leg past 1.5x the probe's projected wall, or past 4.05 h of recording wall;
- a provider refusal that survives the 8-attempt budget, or a raise from
  `measure_baseline.py --honesty` on the probe;
- any conformance breach (a "Conf." cell of 1.6 that does not read as built).
  It is a code defect, not a result: the fix lands under a new arm value, and
  the round re-records from seed 0 under a new declared config, with a dated
  addendum and the owner's clearance.

**Stalls and failed seeds.** A stall is 45 minutes with no completed seed: kill
the batch and re-run it for the seeds not on disk, or relaunch a fresh operator
from the last pushed checkpoint. A seed on disk is never re-recorded to recover
a stall. A `(deadline_default)` row marks a failed recording: remove its husk
and re-record that seed alone at P, logging the cause as it happens. No seed
re-records for any other reason.

**The probe.** Seed 0 records alone. The gate with the declared config,
`verify_samples.sh`, the golden's walk, the census conformance cells, the
scorecard fold, `measure_baseline.py --honesty` (a raise is a STOP) and
`scan_recording_packets.py` then run on it before seeds 1-49 queue. A seed 0
with no meeting or no fired rebuttal extends the probe to seeds 0-3; seeds 0-3
with a meeting but no rebuttal stop the card.

### 1.6 The before column, and each cell's after source

**Before** is s9 at baseline 9: the `samples/9p2i` entry of
`docs/gameplay-census.json` and of `docs/process-scorecard.json`, and
`measure_baseline.py replays/samples/9p2i --honesty --json` for the ballot
family. At `F`, `publish_gameplay_census.py --set-dir replays/samples/9p2i
--json-stdout` equals the shipped census entry over all 973 leaves and
`publish_process_scorecard.py --set-dir replays/samples/9p2i --json-stdout`
equals the shipped scorecard entry over all 108; a copy of the shipped census
with one numerator raised by one differs in exactly that leaf.

**After** is the candidate only, never pooled with the before column, and it
comes only from these, run on `replays/candidates/stage-b-r1/9p2i`:
`publish_gameplay_census.py --set-dir DIR --json-stdout` (every census cell
below), `publish_process_scorecard.py --set-dir DIR --json-stdout` (the process
rows), `measure_baseline.py DIR --honesty --json` (its `ballot_conduct` family:
cell 3, impostor EJECTs whose valid citations are only neutral rows, and cell 5,
witness ballots citing the kill), and the validity gate's
`no_betrayal_ballots_or_accusations` check. A cell no named source counts is
marked "not carried" and is not measured another way.

"Conf." cells must read exactly as built; a miss is a code defect that stops
the round. "Reported" cells carry no rule. Rates carry Wilson 95% intervals.
The before values below are what the command at the end of this subsection
prints at `F`; where a value differs from the card's table, the row says why.

| arm | cell (source key) | s9 before | pre-registered reading |
|---|---|---|---|
| physical witness | exits seen only from the room left (`vent_exits_seen_only_from_room_left`); vent-band ejections resting only on them (`vent_band_resting_only_on_room_left`) | 9/85; 8/70 | Conf. 0; 0 |
| look and wait | surfacings before the cap with a living non-teammate in the policy's inferred-visible set, own room plus neighbours and own room only under any sabotage (`surfacings_before_cap_in_view`); trips over the cap (`trips_longer_than_cap`) | 52/85; n/a (0/0) | Conf. 0; 0 |
| look and wait | exits seen from the exit room (`vent_exits_seen_from_exit_room`) | 53/85 = 0.624 (Wilson 0.52-0.72) | on the point share: **effective** at 0.30 or below; **not effective** at 0.52 or above, which names the hidden-travel escalation (hops capped at 1-2, no maximize-distance-from-body term); **partial** between; n/a with no vent exit |
| look and wait | forced exits (`forced_surfacings`); ticks inside per surfaced trip (table `ticks_inside_per_trip`); near-body cost, in-place surfacings a crewmate reaches before the walk-out (`in_place_surfacings_near_crew`); kills within 2 ticks of the killer's surfacing (`kills_soon_after_surfacing`) | n/a (0/0); 85 of 85 at 1 tick; n/a (0/0); 3/175 | reported |
| own fresh kill | entries not after the impostor's own fresh kill (`vent_entries_not_after_own_fresh_kill`) | 13/105 | Conf. 0 |
| full reset | stale reports (`stale_report_meetings`); reported corpses older than the last regroup (`report_corpses_older_than_last_close`); play resumes with a vented impostor (`play_resumes_with_impostor_in_vent`); with a corpse (`play_resumes_with_corpse`); kills at T+1 to T+4 after a regroup at meeting tick T (`kills_in_grace_window_after_regroup`) | 43/135; n/a; 10/107; 60/107; n/a (beside it, kills within 2 ticks of any meeting, `post_meeting_kills_soon_after`: 28/87) | Conf. 0, 0, 0, 0, 0 |
| full reset | false resume perceptions; regroup notice present | n/a; n/a | Conf. 0; present every time. **Not carried**: no named source counts either. What stands behind them is mechanism, not a count: the one resume helper and the notice fold, both run by the golden's byte-equal re-render of every recorded prompt |
| full reset | skip rate at report meetings (`skipped_report_meetings`); meetings per game (census meetings / games); trips closed by a regroup (`trips_closed_by_regroup`); kill-witness button calls within 6 ticks of a regroup (`kill_witness_button_calls_soon_after_regroup`); dropped trigger-tick events (table `trigger_tick_events_dropped_by_regroup`); meetings opening with an impostor in a vent (`meetings_opening_with_impostor_in_vent`) | 55/135; 2.90; n/a; n/a; n/a; 29/145 | reported; the reset does not zero the opening cell |
| one reply | rebuttals the selector would not have chosen (`rebuttals_differing_from_selector`); meetings with a second repeat-speaker turn (`meetings_with_second_repeat_speaker`) | 0 fired (0/0); 0/145 | Conf. 0; 0 |
| one reply | opener rebuttals answering the charged tick with an alibi, whereabouts or sighting (`opener_rebuttals_answering_charged_tick`, over its evaluable turns); rebuttals that only redirect (`rebuttals_redirect_only`, over all repeat-speaker turns) | an accused opener answered in 0/125 (`accused_opener_answers`); n/a; n/a | **effective** if half or more of the evaluable opener rebuttals answer; **not effective** below 0.2, or if redirect-only reaches half; **partial** otherwise; **conflicting**, naming both, if an effective and a not-effective condition both hold; n/a with no evaluable opener rebuttal (the not-evaluable count is printed) |
| one reply | accused openers answering (`accused_opener_answers`); beneficiary kind (table `rebuttal_beneficiaries`); reporter ejections (the envelope row); rebuttals carrying an alibi, whereabouts or sighting; rebuttal accusations against earlier speakers; ballots citing a rebuttal | 0/125; none; 7 of 135; n/a; n/a; n/a | reported; ballots citing a rebuttal are **not carried** |
| body handle | report openings carrying the kill-tick handle `body-p-N-T` (`report_openings_with_kill_tick_handle`) | 135/135 | Conf. 0 |
| kill row | own-kill rows naming a teammate or held by a non-witness (`own_kill_rows_breaching`) | n/a (0/0) | Conf. 0 |
| kill row | witness ballots citing the kill (honesty cell 5, `kill_holders` and `kill_holders_citing_the_kill`); own-kill rows their holder cited (`own_kill_rows_cited_by_holder`) | 4 holders, 3 of 4 citing the kill through a sighting; 0 kill rows served (0/0) | presence only: **present** when the census served one or more own-kill rows (`own_kill_rows_breaching`'s denominator), else **absent**; no effect reading at this size |
| impostor ballot | recorded teammate targets (`recorded_teammate_ballot_targets`); the gate's `no_betrayal_ballots_or_accusations` | 0/210; 0 | Conf. 0; 0 |
| impostor ballot | impostor EJECTs whose only citation is a neutral row (honesty cell 3, `ejects_citing_only_neutral`) | 1/46 (the rule did not exist, so this is context) | **the wording holds** at 0.10 or below; **it does not bind** above 0.25, which calls for a revision under a new value; **between the two readings** otherwise; n/a with no impostor EJECT |
| impostor ballot | EJECT share (`impostor_eject_ballots`); EJECTs labelled supported (`impostor_ejects_labelled_supported`); authored teammate targets (`authored_teammate_ballot_targets`); ejections whose floor only impostors met (`ejections_carried_only_by_impostor_ballots`); SKIPs labelled `none_held` | 46/210; 44/46; 1/210; 0/90 (pooled 0/411); 95/164 | reported; `none_held` SKIPs are **not carried** (the 95/164 is the ballot card's own count, not a named source) |
| self-report off | impostor openers (`impostor_openers`) | 0/145 | Conf. 0 |
| envelope | impostor win share (`impostor_wins`); innocent ejections (`role_correct_ejections`'s denominator less its numerator); reporters ejected per report meeting (table `innocent_opener_ejections_by_trigger` report row over table `meetings_by_trigger` report row); role-correct ejections (`role_correct_ejections`); meetings with vent proof (`meetings_with_vent_proof`); scorecard rows 1-9 | 11/50 = 0.22; 9 of 90; 7/135 = 0.052; 81/90; 70/145; as published | non-gating. A win share outside 0.20-0.60 is flagged, and one above 0.60 names the status-quo fallback for the vent exit. Reporter ejections above 0.104 per report meeting (twice 7/135) are flagged |

**Where the before column differs from the card's table**, re-measured at `F`
and changing no reading:

- The look-and-wait conformance cell reads 52/85 on s9, not 31/85. The card's
  31/85 is `vent_exits_into_visibly_occupied_room`, the exit's destination room
  alone; the conformance cell reads the whole inferred-visible set. Both are
  shipped; the after column prints both.
- Ticks inside read 85 of 85 surfaced trips at 1 tick
  (`ticks_inside_per_trip`, whose count restarts at a meeting boundary), not
  "5/85 longer".
- The kill row's before is 4 holders, 3 of 4 of whose ballots cite the kill
  through their sighting of it (either own-id slot); no kill row exists at the
  arm's default, so 0 rows were served.
- Honesty cell 3 reads 1/46 on s9, where the card has n/a; the impostor
  ballot rule did not exist then.
- The card's 28/87 is kills within 2 ticks of any meeting
  (`post_meeting_kills_soon_after`); the grace-window conformance cell is n/a on
  s9, which has no regroup.
- The card's "0 fired" rebuttals: `rebuttals_differing_from_selector` has an
  empty denominator on s9, and `meetings_with_second_repeat_speaker` reads
  0/145.

The command that prints the before table, and with `--after` computes each
reading by the rules above (count-only; `CENSUS.json` is one census section, or
`docs/gameplay-census.json`, whose `samples/9p2i` entry it then reads;
`HONESTY.json` is the honesty report):

```
python3 readings.py docs/gameplay-census.json s9-honesty.json          # before, at F
python3 readings.py census-after.json honesty-after.json --after        # after
```

Its source is quoted whole in 1.8, so the rules' code is fixed here too.

### 1.7 The order of the assessment, and the decision menu

The assessment (a later section) reads, in this order: the process cells (the
scorecard's rows, before and after); then each arm's Conf. cells and reading by
1.6's rules; then the envelope; then role-correct ejection and the win split,
which gate nothing. Only the Conf. cells and the lab's minus-one rows (a
mechanical attribution on development seeds with a fake provider) attribute an
effect to one arm: the arms land together, so an outcome delta is not
attributable to one of them.

It gives no verdict. For each arm it lists the menu the owner chooses from:

- **adopt** through the era-keyed promotion (memo 1, adoption option (b)), the
  path compatible with the ML hold;
- **iterate** as round 2 under a new value, in `replays/candidates/stage-b-r2/`;
- **escalate** to hidden travel, for the vent exit;
- **fall back** to the status quo.

### 1.8 The readings command, whole

Saved as `readings.py` and run with `python3` (standard library only). It
prints counts and rates, never a prompt.

```python
"""Print the round's pre-registered table from its named sources (count-only).

Usage: readings.py CENSUS.json HONESTY.json [--after]

CENSUS.json is one census section: `publish_gameplay_census.py --set-dir DIR
--json-stdout`, or the s9 entry of docs/gameplay-census.json (the before
column; the two are equal cell for cell at F). HONESTY.json is
`measure_baseline.py DIR --honesty --json`. With --after, each reading is
computed by the pre-registered rule; without it, values only.
"""

import json
import math
import sys


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def rate(k, n):
    if n == 0:
        return f"{k}/{n} (n/a)"
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {k / n:.3f} (Wilson {lo:.2f}-{hi:.2f})"


census = json.load(open(sys.argv[1]))
if "sets" in census:
    census = next(s for s in census["sets"] if s["label"] == "samples/9p2i")
honesty = json.load(open(sys.argv[2]))[0]["ballot_conduct"]
after = "--after" in sys.argv
cells = census["cells"]
tables = census["tables"]


def cell(key):
    c = cells[key]
    return c["numerator"], c["denominator"]


def show(label, key):
    k, n = cell(key)
    ne = cells[key]["not_evaluable"]
    extra = f"; {ne} not evaluable" if ne else ""
    print(f"  {label} [{key}]: {rate(k, n)}{extra}")
    return k, n


def conf(label, key):
    k, n = show(label, key)
    if after:
        print(f"    Conf.: {'reads 0 as built' if k == 0 else 'BREACH'}")


print(f"games {census['games']}; meetings {census['meetings']}; "
      f"meetings per game {census['meetings'] / census['games']:.2f}")
print("physical witness")
conf("exits seen only from the room left", "vent_exits_seen_only_from_room_left")
conf("vent-band ejections resting only on them", "vent_band_resting_only_on_room_left")
print("look and wait")
conf("surfacings before the cap with someone in view", "surfacings_before_cap_in_view")
conf("trips over the cap", "trips_longer_than_cap")
show("  beside: exits into a room the impostor could see a crewmate in",
     "vent_exits_into_visibly_occupied_room")
k, n = show("exits seen from the exit room", "vent_exits_seen_from_exit_room")
if after:
    if n == 0:
        print("    reading: n/a (no vent exit)")
    else:
        share = k / n
        verdict = ("effective" if share <= 0.30 else
                   "not effective (names the hidden-travel escalation)" if share >= 0.52
                   else "partial")
        print(f"    reading: {verdict}")
show("forced exits", "forced_surfacings")
print(f"  ticks inside per surfaced trip [ticks_inside_per_trip]: "
      f"{json.dumps(tables['ticks_inside_per_trip']['counts'], sort_keys=True)}")
show("near-body cost: in-place surfacings a crewmate reaches", "in_place_surfacings_near_crew")
show("kills within 2 ticks of the killer's surfacing", "kills_soon_after_surfacing")
print("own fresh kill")
conf("entries not after the impostor's own fresh kill", "vent_entries_not_after_own_fresh_kill")
print("full reset")
conf("stale report meetings", "stale_report_meetings")
conf("reported corpses older than the last regroup", "report_corpses_older_than_last_close")
conf("play resumes with an impostor in a vent", "play_resumes_with_impostor_in_vent")
conf("play resumes with a corpse", "play_resumes_with_corpse")
conf("kills in the grace window after a regroup", "kills_in_grace_window_after_regroup")
show("  beside: kills within 2 ticks of any meeting", "post_meeting_kills_soon_after")
show("skipped report meetings", "skipped_report_meetings")
show("trips closed by a regroup", "trips_closed_by_regroup")
show("kill-witness button calls within 6 ticks of a regroup",
     "kill_witness_button_calls_soon_after_regroup")
print(f"  dropped trigger-tick events [trigger_tick_events_dropped_by_regroup]: "
      f"{json.dumps(tables['trigger_tick_events_dropped_by_regroup']['counts'], sort_keys=True)}")
show("meetings opening with an impostor in a vent", "meetings_opening_with_impostor_in_vent")
print("one reply")
conf("rebuttals the selector would not have chosen", "rebuttals_differing_from_selector")
conf("meetings with two repeat-speaker turns", "meetings_with_second_repeat_speaker")
show("an accused opener answers", "accused_opener_answers")
ka, na = show("opener rebuttals answering the charged tick",
              "opener_rebuttals_answering_charged_tick")
kr, nr = show("rebuttals that only redirect", "rebuttals_redirect_only")
if after:
    effective = na > 0 and ka / na >= 0.5
    not_effective = (na > 0 and ka / na < 0.2) or (nr > 0 and kr / nr >= 0.5)
    if na == 0 and not (nr > 0 and kr / nr >= 0.5):
        print("    reading: n/a (no evaluable opener rebuttal)")
    elif effective and not_effective:
        print("    reading: conflicting (an effective and a not-effective condition both hold)")
    elif effective:
        print("    reading: effective")
    elif not_effective:
        print("    reading: not effective")
    else:
        print("    reading: partial")
show("rebuttals carrying an alibi", "rebuttals_with_alibi")
show("rebuttals carrying a whereabouts claim", "rebuttals_with_whereabouts")
show("rebuttals carrying a sighting", "rebuttals_with_sighting")
show("rebuttal accusations against players who already spoke",
     "rebuttal_accusations_against_earlier_speakers")
print(f"  beneficiaries [rebuttal_beneficiaries]: "
      f"{json.dumps(tables['rebuttal_beneficiaries']['counts'], sort_keys=True)}")
print("body handle")
conf("report openings carrying the kill-tick handle", "report_openings_with_kill_tick_handle")
print("kill row")
conf("own-kill rows naming a teammate or held by a non-witness", "own_kill_rows_breaching")
served = cell("own_kill_rows_breaching")[1]
show("own-kill rows their holder cited", "own_kill_rows_cited_by_holder")
holders = honesty["kill_holders"]
citing = honesty["kill_holders_citing_the_kill"]
print(f"  honesty cell 5: kill holders {holders}; citing the kill "
      f"{rate(citing['numerator'], citing['denominator'])}")
if after:
    print(f"    presence: {'present' if served > 0 else 'absent'} ({served} rows served)")
print("impostor ballot")
conf("recorded teammate ballot targets", "recorded_teammate_ballot_targets")
neutral = honesty["ejects_citing_only_neutral"]
print(f"  honesty cell 3: impostor EJECTs citing only a neutral row "
      f"{rate(neutral['numerator'], neutral['denominator'])}")
if after:
    if neutral["denominator"] == 0:
        print("    reading: n/a (no impostor EJECT)")
    else:
        share = neutral["numerator"] / neutral["denominator"]
        verdict = ("the wording holds" if share <= 0.10 else
                   "it does not bind (a revision under a new value)" if share > 0.25
                   else "between the two readings")
        print(f"    reading: {verdict}")
show("impostor EJECT share", "impostor_eject_ballots")
show("impostor EJECTs labelled supported", "impostor_ejects_labelled_supported")
show("authored teammate targets", "authored_teammate_ballot_targets")
show("ejections whose floor only impostors met", "ejections_carried_only_by_impostor_ballots")
print("self-report off")
conf("impostor openers", "impostor_openers")
print("envelope (non-gating)")
k, n = show("impostor win share", "impostor_wins")
if after and n:
    share = k / n
    flag = ("flagged above 0.60: names the status-quo fallback for the vent exit" if share > 0.60
            else "flagged below 0.20" if share < 0.20 else "inside 0.20-0.60")
    print(f"    envelope: {flag}")
rk, rn = cell("role_correct_ejections")
print(f"  innocent ejections: {rn - rk} of {rn} ejections")
reporters = tables["innocent_opener_ejections_by_trigger"]["counts"].get("report", 0)
report_meetings = tables["meetings_by_trigger"]["counts"].get("report", 0)
print(f"  reporters ejected per report meeting: {rate(reporters, report_meetings)}")
if after and report_meetings:
    per = reporters / report_meetings
    print(f"    envelope: {'flagged above 0.104' if per > 0.104 else 'at or below 0.104'}")
show("role-correct ejections (reported, gates nothing)", "role_correct_ejections")
show("meetings with vent proof", "meetings_with_vent_proof")
```
