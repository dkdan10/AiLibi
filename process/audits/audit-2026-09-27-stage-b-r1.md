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

## 2. The pre-spend, at `F` and before the first seed

Nothing in this section called a provider. Every command ran in a bare shell
(`env | grep -c '^AILIBI_'` printed 0) unless it names its own exports.
Scratch outputs lived outside the repository; every census here is count-only.

### 2.1 The preflight

- `git grep -n WAVE_ARMS_PENDING -- '*.py'` at `F`: no output, exit 1. The
  pending guard is gone.
- The declared file, read through `scripts/_declared_experiment.py`'s own
  loader at `F`: sha256 `4f0c4dd4…6d6c7` (1.2); eight fields off their default,
  the ones 1.2 names; `prompt_versions_for_set("qwen3_6_27b",
  experiment_config=...)` serves the three `.v6` stamps and the composite
  ballot stamp.
- Proof, two perturbations of the same payload: with one unknown key added,
  validation is refused (`extra_forbidden`, `('unknown_switch',)`); with
  `vent_witness_rule` removed, the fields off their default number 7.

### 2.2 The before column

At `F`, `publish_gameplay_census.py --set-dir replays/samples/9p2i
--json-stdout` exited 0 and equals the `samples/9p2i` entry of
`docs/gameplay-census.json` in 973 of 973 leaves;
`publish_process_scorecard.py --set-dir replays/samples/9p2i --json-stdout`
exited 0 and equals the shipped entry in 108 of 108. Proof: against a copy of
the shipped census whose `vent_exits_seen_from_exit_room` numerator is raised
by one, the same leaf comparison prints one difference
(`cells.vent_exits_seen_from_exit_room.numerator: set-dir=53 shipped=54`) and
exits 1. `measure_baseline.py replays/samples/9p2i --honesty --json` exited 0;
its ballot family is the before of cells 3 and 5 (1.6). The tally prints
`1694 9850930 422941 0.0` on `replays/samples/9p2i`, the anchor.

### 2.3 The fake dress rehearsal

Seeds 0-49 on the declared config, recorded with `AILIBI_LLM_PROVIDER=fake`
into a scratch directory outside the repository, from the verification
checkout at `F`:

```
AILIBI_LLM_PROVIDER=fake AILIBI_PROMPT_SET=qwen3_6_27b AILIBI_NUM_PLAYERS=9 \
AILIBI_NUM_IMPOSTORS=2 AILIBI_TASKS_PER_CREWMATE=2 AILIBI_SAMPLE_DIR=<scratch>/9p2i \
AILIBI_MANIFEST=<scratch>/9p2i/MANIFEST.md AILIBI_REFRESH_WORKERS=4 \
  bash scripts/refresh_samples.sh --full --expect-levers "" --experiment-config <scratch config copy>
```

50 of 50 seeds in 15 s, `$0.0000`, 112 meetings, the report rebuilt. The tally
prints `1414 5236031 81305 0.0`. Each instrument then exited 0 on it:

| instrument | result |
|---|---|
| `publish_gameplay_census.py --set-dir <dir> --json-stdout` | exit 0; 50 games, 112 meetings; every one of the 16 cells the declared settings force to zero reads 0 |
| `publish_process_scorecard.py --set-dir <dir> --json-stdout` | exit 0 |
| `validity_gate.py <dir> --require-zero-cost --expected-prompt-versions <the four pairs> --expected-experiment-config <config> --expected-seeds 0-49 --require-one-recording-sha` | exit 0; all ten checks PASS |
| `bash scripts/verify_samples.sh <dir>` | exit 0; "All 50 samples verified clean." |
| the golden's directory walk (`walk_directory`, count-only runner) | exit 0; 50 seeds, 112 meetings, 1,414 prompts, 0 not reproduced, 0 miscounted meetings |
| `measure_baseline.py <dir> --honesty` | exit 0; no raise |
| `scan_recording_packets.py <dir>` | exit 0 |

The sixteen forced-zero cells, all 0 on the rehearsal: `impostor_openers`,
`kills_in_grace_window_after_regroup`, `meetings_with_second_repeat_speaker`,
`own_kill_rows_breaching` (0 of 4 served), `play_resumes_with_corpse`,
`play_resumes_with_impostor_in_vent`, `rebuttals_differing_from_selector`,
`recorded_teammate_ballot_targets`, `report_corpses_older_than_last_close`,
`report_openings_with_kill_tick_handle` (0 of 105), `stale_report_meetings`,
`surfacings_before_cap_in_view` (0 of 79), `trips_longer_than_cap`,
`vent_band_resting_only_on_room_left`, `vent_entries_not_after_own_fresh_kill`
(0 of 152) and `vent_exits_seen_only_from_room_left`. A fake meeting ejects
nobody and fires no rebuttal, so the meeting arms are proved by 2.4, not here.

Proof: gated against a copy of the config without `vent_witness_rule`, the
gate exits 1 and fails `cost_and_provenance_exact` on 50 of 50 games, each line
naming the recorded `vent_witness_rule='physical'` that the declared config
lacks.

### 2.4 The scripted rehearsal

At `F`, the scripted cases the readers and ballot cards landed pass:
`tests/_helpers/test_scripted_meeting.py` (the one rebuttal),
`tests/meetings/test_ballot_arms.py` (impostor EJECTs with and without a row
pointing toward the target, the kill row, the teammate coercion) and
`tests/eval/test_recorded_arm_readers.py`, 267 passed in one run; and the
golden's `test_the_scripted_rebuttal_game_re_renders_byte_equal`, whose
perturbed half drops the recorded evidence profile and leaves the rebuttal call
unconsumed, `test_dropping_the_recorded_reset_fails_the_meeting_post_hash` and
`test_the_kill_row_gate_forced_on_fails_the_golden_at_the_kill_holders`, all
passed.

One scratch scripted game on the full declared config: the ballot card's
scripted game (`record_ballot_arms_game`, seed 26), recorded from the declared
file rather than the helper's literal, into a scratch directory. It holds 3
meetings, 2 rebuttals (one per accused meeting) and 1 ejection, and:

| check | result |
|---|---|
| `verify_samples.sh <dir>` (the plain loader) | "All 1 samples verified clean." |
| census `--set-dir` | exit 0; the rebuttals counted once each: `meetings_with_repeat_speaker` 2/3, `meetings_with_second_repeat_speaker` 0/3, `rebuttals_differing_from_selector` 0/2, beneficiaries "the opener, answering a crewmate" 1 and "the opener, answering an impostor" 1; `own_kill_rows_breaching` 0/3, `own_kill_rows_cited_by_holder` 1/3; impostor EJECTs 5 of 6 ballots, 4 labelled supported; authored teammate targets 1/6 and recorded 0/6; the one ejection carried by impostor ballots alone |
| scorecard `--set-dir` | exit 0 |
| `validity_gate.py <dir> --require-zero-cost --expected-experiment-config <config> --expected-seeds 26 --require-one-recording-sha` | exit 0; ten checks PASS |
| the golden's directory walk | 40 prompts, 0 not reproduced, 0 miscounted meetings |

### 2.5 The lab attribution matrix

```
uv run python -m experiments.tactical_gameplay \
  --output audits/tactical-gameplay/stage-b-r1-frozen-head.json --split development \
  --arms baseline vent_risk vent_physical vent_look_and_wait vent_own_fresh_kill stage_b_full \
    stage_b_full_minus_look_and_wait stage_b_full_minus_own_fresh_kill \
    stage_b_full_minus_physical stage_b_full_minus_hub_with_grace
```

Run at `F` (`git_head` `f937dfaa015eebf01e440f094d125f66bc130e35`, runtime
fingerprint `source_sha256` `1677067c3b59bf53ff633ec982a8614e2d2e2c1adb866586f3e68d2e04cd5a05`,
Python 3.11.15 on macOS arm64) on development seeds 1000-1007 of both rosters,
with the lab's injected deterministic fake: no provider, no spend. **Proof:**
the `baseline` and `vent_risk` rows equal
`audits/tactical-gameplay/stage-b-development.json` in waits, exposure and
calls, and in every other field, on both rosters, so no default path moved. The
arms without `hub_with_grace` also equal the committed rows on both rosters;
the four 9p2i arms that carry it (`stage_b_full` and three minus-one arms)
differ from rows measured at `63980a00`, before the reset card's later commits,
which is where they should move.

Count-only sums over the eight 9p2i games (the 4p1i sums after the slash).
Mechanical attribution only: fake outcomes are not model-quality evidence.

| arm | meetings | vent actions | vent exits | exits a crewmate saw | seen only from the room left | trips at the cap | entries not after own fresh kill | bodies unreported after meetings | calls |
|---|---|---|---|---|---|---|---|---|---|
| `baseline` | 24/8 | 58/16 | 29/8 | 16/6 | 3/1 | 0/0 | 11/0 | 17/2 | 294/48 |
| `vent_risk` | 26/8 | 68/16 | 34/8 | 14/5 | 5/2 | 0/0 | 17/0 | 28/2 | 308/48 |
| `vent_physical` | 25/8 | 56/16 | 28/8 | 13/5 | 0/0 | 0/0 | 10/0 | 19/2 | 304/48 |
| `vent_look_and_wait` | 29/8 | 181/15 | 90/7 | 13/4 | 10/2 | 24/4 | 65/0 | 16/2 | 358/48 |
| `vent_own_fresh_kill` | 25/8 | 34/16 | 17/8 | 11/6 | 4/1 | 0/0 | 0/0 | 19/2 | 302/48 |
| `stage_b_full` | 20/8 | 45/12 | 17/4 | 2/2 | 0/0 | 6/1 | 0/0 | 0/0 | 244/48 |
| `stage_b_full_minus_look_and_wait` | 17/8 | 35/16 | 16/8 | 8/5 | 0/0 | 0/0 | 0/0 | 0/0 | 210/48 |
| `stage_b_full_minus_own_fresh_kill` | 20/8 | 67/12 | 24/4 | 3/2 | 0/0 | 6/1 | 15/0 | 0/0 | 244/48 |
| `stage_b_full_minus_physical` | 20/8 | 45/12 | 17/4 | 2/3 | 0/1 | 6/1 | 0/0 | 0/0 | 244/48 |
| `stage_b_full_minus_hub_with_grace` | 27/8 | 51/15 | 23/7 | 3/2 | 0/0 | 10/4 | 0/0 | 18/2 | 328/48 |

The columns are the lab's own counter keys: `meetings`,
`applied:IMPOSTOR:vent` (entries and exits both), `event:VentExited`,
`vent_exits_crew_witnessed`, `vent_exits_crew_source_only_witnessed`,
`vent_trips_reaching_cap`, `vent_entries_not_after_own_fresh_kill`,
`unreported_bodies_after_meetings`, and the rows' `model_calls`.

### 2.6 The dry run, in the recording checkout at P

The recording checkout is a worktree detached at P (`f1133de5`), with
`uv sync --frozen`, no `.env`, and an untracked copy of the declared file at
`replays/candidates/stage-b-r1/experiment-config.json` whose `shasum -a 256`
prints `4f0c4dd4779cd38f69194b6735221d86bf7c6944fe12769a3971e38e4e46d6c7`.
The recording shell's exports, and nothing else:

```
AILIBI_LLM_PROVIDER=featherless AILIBI_PROMPT_SET=qwen3_6_27b \
AILIBI_LLM_MEETING_MODEL=Qwen/Qwen3.6-27B AILIBI_NUM_PLAYERS=9 AILIBI_NUM_IMPOSTORS=2 \
AILIBI_TASKS_PER_CREWMATE=2 AILIBI_SAMPLE_DIR=replays/candidates/stage-b-r1/9p2i \
AILIBI_MANIFEST=replays/candidates/stage-b-r1/9p2i/MANIFEST.md \
AILIBI_REFRESH_WORKERS=2 AILIBI_SEED_MAX_ATTEMPTS=8 \
  bash scripts/refresh_samples.sh --full --expect-levers "" \
    --experiment-config replays/candidates/stage-b-r1/experiment-config.json --dry-run
```

Exit 0, and its resolved configuration:

```
[dry-run] Experiment config: replays/candidates/stage-b-r1/experiment-config.json (sha256 4f0c4dd4779cd38f69194b6735221d86bf7c6944fe12769a3971e38e4e46d6c7)
[dry-run] Experiment config settings: meeting_reset='hub_with_grace', vent_exit_policy='look_and_wait', bounded_rebuttal_version=1, vent_witness_rule='physical', vent_entry_policy='own_fresh_kill', report_body_handle_version=1, ballot_kill_row_version=1, impostor_ballot_version=1
[dry-run] Experiment switch exports: none
[dry-run] mode: full
[dry-run] seeds: 0,1,2,...,49
[dry-run] roster: num_players=9 num_impostors=2 tasks_per_crewmate=2
[dry-run] roster descriptor: would ensure replays/candidates/stage-b-r1/9p2i/roster.json = {num_players: 9, num_impostors: 2, tasks_per_crewmate: 2} (fails loud if an existing one disagrees)
[dry-run] sample dir: replays/candidates/stage-b-r1/9p2i
[dry-run] provider: featherless
[dry-run] preflight: would require FEATHERLESS_API_KEY (hosted run; $0 provider-keyed cost)
[dry-run] meeting model: Qwen/Qwen3.6-27B
[dry-run] prompt set: qwen3_6_27b
[dry-run] substrate flags: expected levers ON = (none — the bare slate: every live toggle OFF); every other live toggle OFF; the graduated levers unconditional ON
[dry-run] seed workers: 2 parallel (each records one seed, then pulls the next available seed from the queue; Featherless: 2 units per 32B request → 4-unit cap)
[dry-run] seed crash-retry: up to 8 attempt(s) per seed on a transport/crash error (recorded parse failures are non-fatal)
[dry-run]   AILIBI_LLM_PROVIDER=featherless uv run python scripts/run_tournament.py --start-seed <seed> --num-games 1 --output-dir <stage> --num-players 9 --num-impostors 2 --tasks-per-crewmate 2 --force --experiment-config <stage-dir>/experiment-config.json
[dry-run] experiment config: would copy replays/candidates/stage-b-r1/experiment-config.json into the stage directory once, if it still reads sha256 4f0c4dd4779cd38f69194b6735221d86bf7c6944fe12769a3971e38e4e46d6c7, and pass that copy to every seed
[dry-run] manifest: replays/candidates/stage-b-r1/9p2i/MANIFEST.md
[dry-run] eval report: would rebuild replays/candidates/stage-b-r1/9p2i/tournament-eval-report.json.gz from the refreshed replays (scripts/build_sample_report.py; $0, no provider)
[dry-run] no API calls made; no files written.
Substrate slate OK: expected levers ON = (none — the bare slate: every live toggle OFF); every other live toggle OFF; the graduated levers unconditional ON.
```

The two model-coupling lines, the full-mode clean-up line and the full seed
list are elided above; the run printed them. The porcelain status read the
same one line before and after the dry run, the untracked declared copy
(`?? replays/candidates/stage-b-r1/`), and with untracked files hidden it read
0 lines: the dry run wrote nothing. The live leg runs `--seeds`, never
`--full`, because the recorder re-records any seed it is given, on disk or not.

Proof: the same dry run with a stray `AILIBI_BOUNDED_REBUTTAL=1` exported exits
1 with "Refused: the environment exports AILIBI_BOUNDED_REBUTTAL. A recording
takes its experimental switches only from a declared config file
(--experiment-config), so unset these variables before recording. Nothing was
staged."

### 2.7 The key

`FEATHERLESS_API_KEY` lives only in the main checkout's untracked `.env`. Its
one line was copied by a `grep` whose output went straight to the file and was
never printed, into a mode-0600 file in a mode-0700 directory outside every
checkout; a count-only `grep -c` on the source found 1 matching line. Every
live leg runs `uv run --env-file <that file> bash scripts/refresh_samples.sh
...`; no step reads `.env` itself. The file is deleted when the leg ends. The
recorder itself prints the key's first eight characters into its run log;
that log stays outside the repository, and every line quoted from it here
leaves that line out.

## 3. The probe, and the stop it called (2026-09-27)

### 3.1 Seed 0

Recorded alone in the recording checkout at P, with the shell of 2.6 and the
key passed by `uv run --env-file`:

```
<the 2.6 exports> uv run --env-file <key file> bash scripts/refresh_samples.sh \
  --seeds 0 --expect-levers "" --experiment-config replays/candidates/stage-b-r1/experiment-config.json
```

It opened at 2026-09-27T16:30:45Z and exited 0 at 16:44:56Z: "seed 0 done in
838s", 3 meetings, `$0.0000`, no retry and no warning in the run log, and the
recorder's post-step rebuilt the one-game report. The MANIFEST row names model
`Qwen/Qwen3.6-27B`, policy `fsm-default`, `git_sha` `f1133de5` (P) and cost
`0.0000`; the flags column is the bare slate's, as on s9. The tally prints
`39 270760 10976 0.0`, and no replay carries `deadline_default`.

### 3.2 The probe's gates

Run in the delivery checkout on its copy of the probe's bytes, in a bare shell
(0 `AILIBI_*` exports), with the declared file's sha256 re-checked
(`4f0c4dd4…6d6c7`):

| gate | result |
|---|---|
| `validity_gate.py <dir> --expected-model Qwen/Qwen3.6-27B --require-zero-cost --expected-prompt-versions <the four pairs, the composite ballot stamp> --expected-experiment-config <config> --expected-seeds 0 --require-one-recording-sha` | exit 0; all ten checks PASS |
| `bash scripts/verify_samples.sh <dir>` | exit 0; "All 1 samples verified clean." |
| the golden's directory walk | exit 0; 3 meetings, 39 prompts, 0 not reproduced, 0 miscounted meetings |
| census `--set-dir <dir> --json-stdout` | exit 0: every Conf. cell of 1.6 reads 0 |
| scorecard `--set-dir <dir> --json-stdout` | exit 0 |
| `measure_baseline.py <dir> --honesty --json` | exit 0; no raise |
| `scan_recording_packets.py <dir>` | exit 0 |

Seed 0 held meetings and a fired rebuttal in each of its 3 meetings (3
repeat-speaker turns, each by an accused opener answering an impostor;
`rebuttals_differing_from_selector` 0/3, `meetings_with_second_repeat_speaker`
0/3), so the probe did not extend to seeds 0-3. The counts of one game are no
reading and none is drawn here.

### 3.3 The re-projection, and the stop

The rule of 1.4, applied to the one completed seed (s9's seed 0 has 3
meetings, 42 calls, 271,968 input and 10,486 output):

| limit | candidate / s9, seed 0 | projected | share of ceiling | 90% stop |
|---|---|---|---|---|
| model calls | 39 / 42 = 0.9286 | 1,573 | 56.2% | ok |
| input tokens | 270,760 / 271,968 = 0.9956 | 9,807,175 | 56.0% | ok |
| output tokens | 10,976 / 10,486 = 1.0467 | 442,705 | 59.0% | ok |
| recording wall | 838 s / 1 seed x 50 | 41,900 s = 11.64 h | 258.6% of 4.5 h | **STOP** (past 4.05 h) |
| marginal cost | every `cost_usd` is 0.0 | | | ok |

**The recording wall projects past its 90% stop, so the round stops here, at
seed 0, and reports to the owner (1.5).** Seeds 1-49 were not queued, and no
provider call was made after 16:44:56Z.

The literal rule divides by one seed recorded alone, while the rest of the leg
would run two seeds at a time, so it overstates the wall. The stop does not
rest on that: every reading of the probe's wall lands past 4.05 h.

| reading of the probe's wall | projected leg wall |
|---|---|
| the rule as written: 838 s x 50 | 11.64 h |
| two workers: 838 s x 50 / 2 | 5.82 h |
| per call, two workers: 1,573 projected calls x 21.5 s / 2 | 4.70 h |

The cause is provider latency, not the arms' traffic. The probe spent 21.5 s
per call on one worker (838 s / 39 calls). The baseline-9 leg of the same seeds
spent about 10.3 s per call on each of its two workers (8,695 s x 2 / 1,694
calls). The probe's calls, input and output all project inside their ceilings
at 56-59%, and the call ratio is below 1.

### 3.4 What stands, and what the owner decides

- The probe's bytes are the round's partial output: `replay-seed-0.jsonl`,
  `MANIFEST.md`, `roster.json` and the recorder's one-game report, checkpointed
  on `work/stage-b-record-r1` after a count-only key scan. The branch head holds
  a partial round, so the candidate test fails there until seeds 1-49 land; no
  pull request is open.
- The recording checkout stays detached at P with seed 0 on disk. A resumed leg
  records `--seeds 1,...,49` only, in a checkout detached at P, so every
  MANIFEST row keeps the one sha; seed 0 is never re-recorded.
- The key file was deleted when this sitting ended. A resumed leg copies the key
  again the same way (2.7).
- The owner's choices, none of which this record takes: raise the recording-wall
  ceiling (the 8 h window, opened by the first seed at 16:30:45Z, closes at
  00:30:45Z on 2026-09-28), with the 10-seed re-projection still binding; resume
  under the same ceiling at a time the provider answers faster, re-projecting at
  10 seeds; or end the round at seed 0.

## 4. Addendum to the pre-registration: the wall amendment (2026-09-28)

This addendum amends 1.4 and 1.5 and changes nothing else in section 1, which
stands as committed at P. It was committed and pushed before the first seed of
the second sitting.

### 4.1 The owner's ruling, verbatim and dated

On **2026-09-28**, the owner, relayed verbatim by the orchestrator:

> Raise the wall to 12h in an 18h window and resume. Make sure it allows for a pause.

It takes the first of the choices 3.4 put to the owner. As applied here:

- the recording-wall ceiling becomes **12 h** of recording time, summed over
  every sitting of the round, with its hard stop at 90%, **10.8 h** (38,880 s);
- each sitting runs inside an **18 h** elapsed window, opened by that sitting's
  first seed;
- the call, token and cost ceilings, and their stops, are unchanged.

### 4.2 The ceilings, restated

| limit | ceiling | hard stop at 90% |
|---|---|---|
| model calls | **2,800** (unchanged) | 2,520 |
| input tokens | **17,500,000** (unchanged) | 15,750,000 |
| output tokens | **750,000** (unchanged) | 675,000 |
| recording wall | **12 h** summed over sittings, each sitting inside an **18 h** elapsed window (was 4.5 h inside 8 h) | **10.8 h** summed (was 4.05 h) |
| marginal cost | **$0.00** (unchanged) | any `cost_usd` other than 0.0000 |

Recording wall is each leg's own wall as the recorder prints it ("Refresh
complete in"), summed over sittings: the probe's 838 s, then each batch's. The
time between batches, spent on gates and checkpoints, is not recording wall; it
counts against the sitting's 18 h window.

**Re-projection** continues by 1.4's rule against the new wall. After 10 seeds
(the first checkpoint holding at least 10 seeds), each count is (the
candidate's total over the completed seeds / the s9 total over the same seeds)
x the s9 leg total, and the wall is the summed recording wall / the completed
seeds x 50, each compared with its 90% stop. The same figures are printed at
every batch checkpoint, and a figure past its stop at any of them stops the
round.

**The stop rules of 1.5 stand**, with 10.8 h summed in place of 4.05 h. The
probe's projected wall was 11.64 h, so 1.5 times it (17.46 h) lies past the new
ceiling, and the 10.8 h stop binds first.

### 4.3 The pause, and how the round resumes

- Seeds 1-49 record in batches of 5 (`--seeds 1,2,3,4,5`, then 6-10, and so on,
  ending with 46-49) in the recording checkout, still detached at P, so every
  MANIFEST row keeps P's short sha. Each leg names only the seeds it must
  record; seed 0 is never re-recorded.
- Before each batch the operator checks for a pause file outside the
  repository. If it exists, no batch starts: the key file is deleted, the last
  checkpoint is pushed, and the operator log names the seed reached and the
  next batch. The sitting ends there. The next sitting opens a new 18 h window,
  copies the key again as 2.7 describes, and resumes at the named batch; its
  recording wall adds to the sum.
- After each batch, in the delivery checkout and a bare shell, the probe's
  gates of 3.2 run on the set so far, with `--expected-seeds 0-N`: the validity
  gate with the declared config, `verify_samples.sh`, the golden's walk, the
  census conformance cells, the scorecard fold, `measure_baseline.py --honesty`
  (a raise is a STOP) and `scan_recording_packets.py`; then the tally, the
  re-projection and the count-only key scan. The batch's files are then
  committed on `work/stage-b-record-r1` as a `record:` checkpoint and pushed.
- A stall, 45 minutes with no completed seed, kills the batch, and the re-run
  names only the batch's seeds not on disk.

## 5. Sitting 2: seeds 1-49 (2026-09-28)

### 5.1 The resume

The addendum of section 4 was committed and pushed (`2f63e331`) before the
sitting's first seed. The recording checkout was the same worktree, still
detached at P (`f1133de5`), with seed 0 on disk byte-equal to the pushed
checkpoint and the round README restored from it; the untracked declared copy
read `4f0c4dd4…6d6c7` before every batch (the batch runner refuses a
mismatch). The key was copied again as 2.7 describes (one matching source
line, never printed) into a mode-0600 file in a mode-0700 directory outside
every checkout, and passed only by `uv run --env-file`. The recording shell's
exports were those of 2.6 and nothing else; every gate ran in a bare shell
that printed 0 `AILIBI_*` exports.

The sitting's 18 h window opened with its first seed at 09:52:00Z (it would
close at 03:52:00Z on 2026-09-29); the last seed finished at 13:25:36Z. The
pause file was checked before every batch and was absent each time, so the
sitting never paused. No leg ran pytest or `check.sh` in the recording
checkout.

### 5.2 The batches

Each leg was `uv run --env-file <key file> bash scripts/refresh_samples.sh
--seeds <the batch> --expect-levers "" --experiment-config
replays/candidates/stage-b-r1/experiment-config.json` with the 2.6 exports.
Wall is the recorder's own "Refresh complete in" figure; calls and tokens are
the tally of the batch's seeds as they stand in the committed set.

| leg | seeds | UTC | recording wall | calls | input | output | checkpoint |
|---|---|---|---|---|---|---|---|
| probe (sitting 1) | 0 | 09-27 16:30:45-16:44:56 | 838 s | 39 | 270,760 | 10,976 | `2f4cdbee` |
| batch 1 | 1-5 | 09:52:00-10:21:31 | 1,768 s | 150 | 891,848 | 44,297 | `9725ece0` |
| batch 2 | 6-10 | 10:22:28-10:39:59 | 1,027 s | 181 | 1,128,419 | 50,603 | `1a070d32` |
| batch 3 | 11-15 | 10:41:02-11:08:34 | 1,626 s | 173 | 1,021,821 | 46,160 | `ea4aa233` |
| batch 4 | 16-20 | 11:09:47-11:25:18 | 918 s | 150 | 898,821 | 43,839 | `36f7061a` |
| batch 5 | 21-25 | 11:26:24-11:43:25 | 1,002 s | 132 | 804,770 | 38,761 | `7e0d4eeb` |
| batch 6 | 26-30 | 11:44:24-12:06:25 | 1,306 s | 180 | 1,073,731 | 49,492 | `b7a287f7` |
| batch 7 | 31-35 | 12:07:21-12:21:22 | 831 s | 117 | 661,828 | 31,606 | `c2877c4c` |
| seed 31 again | 31 | 12:23:05-12:35:06 | 702 s | (in batch 7) | | | `c2877c4c` |
| batch 8 | 36-40 | 12:36:20-12:54:21 | 1,059 s | 172 | 1,033,353 | 47,424 | `d80c9e39` |
| batch 9 | 41-45 | 12:55:29-13:10:30 | 879 s | 143 | 859,962 | 39,339 | `d65b6af9` |
| batch 10 | 46-49 | 13:11:35-13:25:36 | 820 s | 119 | 699,033 | 31,163 | `b16690af` |
| **the round** | 0-49 | | **12,776 s** | **1,556** | **9,344,346** | **433,660** | |

After every batch, in the delivery checkout: the validity gate with the
declared config and `--expected-seeds 0-N`, `verify_samples.sh`, the golden's
walk, the census (every conformance cell read 0 at every checkpoint), the
scorecard fold, `measure_baseline.py --honesty` (no raise at any checkpoint),
`scan_recording_packets.py`, the tally, the re-projection and the count-only
key scan (0 at every checkpoint) all exited 0, except the one gate failure of
5.3. Every checkpoint's MANIFEST named the one sha `f1133de5`.

### 5.3 Events

1. **Seed 31: a `(deadline_default)` re-record, cause logged as it happened.**
   Batch 7 exited 0, but its post-batch gate failed `cost_and_provenance_exact`
   (`model provenance ['(deadline_default)', 'Qwen/Qwen3.6-27B'] != expected`):
   seed 31 held one `failed_call` row of type `deadline_default` in its second
   meeting, at tick 39, whose message reads "opt_in turn (turn 2) defaulted
   (validation); p-5 submitted no turn", beside one `ValidationError` row at
   the same meeting and tick (an alibi claim whose route segments overlapped).
   The opt-in turn is the one-reply slot; the model's answer failed
   validation, and the turn fell back to a default instead of model output. Every conformance cell still read 0 on it. By 1.5's failed-seed rule
   (and the baseline-9 precedent, `audits/audit-2026-09-22-process-rerecord.md`
   section 3, event 3), the husk was moved out of the set, outside the
   repository, and seed 31 alone was re-recorded at P (702 s, exit 0, no
   `failed_call` row). The husk had spent 30 calls, 164,457 input and 7,875
   output at `0.0000`; that spend is counted in 5.4 and is not in the set.
2. **No stall, no pause, no retry.** No leg went 45 minutes without a completed
   seed (the longest single seed took 887 s), the pause file never existed,
   and no recorder log carries a `WARN` retry line or a refusal. Across the 50
   committed seeds there is no `failed_call` row at all.
3. **No stop fired.** Every `cost_usd` is `0.0000`, and no re-projection came
   near a stop (5.4).

### 5.4 The spend against the ceilings

The re-projection after 10 seeds (seeds 0-10, 3,633 s of summed recording
wall), by 1.4's rule against 4.2's ceilings: calls 1,551 (55.4%), input
9,325,616 (53.3%), output 433,102 (57.7%), wall 16,514 s = 4.59 h against the
10.8 h stop, every `cost_usd` 0.0. The figures printed at every later
checkpoint stayed between 53% and 65% of each count ceiling and at or below
4.6 h of projected wall.

Spent, including the seed-31 husk (the set's own tally is 1,556 calls,
9,344,346 input and 433,660 output):

| limit | sitting 1 | sitting 2 | summed | ceiling | share | 90% stop |
|---|---|---|---|---|---|---|
| model calls | 39 | 1,547 | 1,586 | 2,800 | 56.6% | 2,520 |
| input tokens | 270,760 | 9,238,043 | 9,508,803 | 17,500,000 | 54.3% | 15,750,000 |
| output tokens | 10,976 | 430,559 | 441,535 | 750,000 | 58.9% | 675,000 |
| recording wall | 838 s | 11,938 s | 12,776 s (3.55 h) | 12 h | 29.6% | 10.8 h |
| marginal cost | $0.0000 | $0.0000 | $0.0000 | $0.00 | | any non-zero |

Each sitting stayed inside its window: sitting 1 used 14 minutes of its 8 h
window, and sitting 2 ran 3 h 34 min of its 18 h window, first seed to last.
The round held 124 meetings against s9's 145 on the same seeds (0.86x),
between the planning case's 1.35x and the low case's 0.72x, at 12.55 calls and
75,358 input tokens per meeting against the planned 12.68 and 79,445.

The card's tally command prints `1556 9344346 433660 0.0` on the candidate and
`1694 9850930 422941 0.0` on `replays/samples/9p2i`. The husk's figures come
from the same tally over the husk file, kept outside the repository.

### 5.5 The gates on the whole round

In the delivery checkout, bare shell, at the recorded bytes:

| gate | result |
|---|---|
| `validity_gate.py <candidate> --expected-model Qwen/Qwen3.6-27B --require-zero-cost --expected-prompt-versions <the four pairs> --expected-experiment-config <config> --expected-seeds 0-49 --require-one-recording-sha` | exit 0, ten checks PASS: `all_games_reach_game_over` (50/50), `meeting_rate_and_resolution` (1.0; 124 resolved, 0 unresolved), `no_duplicate_meeting_rows` (0 of 124), `no_tick_1_kills` (0), `no_friendly_fire_kills` (0), `no_betrayal_ballots_or_accusations` (0 of 717), `no_railroaded_crew_ejections` (0 of 2,630), `no_dangling_primary_reason_id` (0 of 717), `cost_and_provenance_exact` (one model, four prompt versions, the declared config, seeds 0-49, one sha), `byte_identical_reconstruction` (0 drifted) |
| proof: the same gate with `--expected-seeds 0-50` | exit 1: `cost_and_provenance_exact`, "missing [50]" for the replay files and the MANIFEST rows |
| proof: `replays/samples/9p2i` against the declared config | exit 1: `cost_and_provenance_exact`, each game's recorded config ("none: historical defaults") differs from the declared one |
| `bash scripts/verify_samples.sh` (bare), then once per set directory | bare: exit 0, both sample sets and the candidate clean; `samples/9p2i`, `samples/4p1i`, `ml_corpus/9p2i` (150), `ml_corpus/4p1i` and the candidate: each exit 0, all clean |
| `build_sample_report.py --sample-dir <dir> --check`, each of the five | exit 0 each; the candidate's report gz is the recorder's post-step rebuild through `eval/report_io.py`, consistent with its 50 seeds |
| the golden's directory walk | exit 0: 50 seeds, 124 meetings, 1,556 prompts, 0 not reproduced, 0 miscounted meetings |
| census `--set-dir <candidate> --json-stdout` | exit 0: every Conf. cell reads 0 (6.2) |
| scorecard `--set-dir <candidate> --json-stdout` | exit 0 |
| `measure_baseline.py <candidate> --honesty --json` | exit 0; no raise |
| `scan_recording_packets.py <candidate>` | exit 0 |
| `grep -l deadline_default` over the 50 replays | 0 files |
| MANIFEST columns | 50 rows: model `Qwen/Qwen3.6-27B`, policy `fsm-default`, `git_sha` `f1133de5`, cost `0.0000`; the flags column equals s9's (one value on every row of each) |
| proof: s9 and the candidate pooled through the census (`fold_set` then `pool`) | each folds alone; pooled, `GameplayCensusEraError`, "two eras differ in settings; the census never pools across eras" |
| `git merge-base --is-ancestor f1133de5 f1133de5` (P against the MANIFEST's one sha) | exit 0. Proof: the head `b16690af` in place of P, exit 1 |

The freeze held: `git log --oneline f937dfaa..HEAD` and `git log --oneline
f937dfaa..origin/main` print nothing over `engine agents meetings observation
orchestrator eval api scripts llm` (`main` is still at `f937dfaa`); proof, the
same pathspec over `e886b663..f937dfaa` prints 50 commits. `git diff --stat
f937dfaa..HEAD` is empty over `replays/samples`, `replays/ml_corpus`,
`tests/fixtures`, `training`, `api`, `frontend` and the scorecard and census
documents.

## 6. The assessment

The after column is the candidate alone, computed only from 1.6's named
sources, and never pooled with the before column: the census and scorecard
`--set-dir replays/candidates/stage-b-r1/9p2i --json-stdout`,
`measure_baseline.py replays/candidates/stage-b-r1/9p2i --honesty --json` and
the validity gate's `no_betrayal_ballots_or_accusations`. Each reading is what
1.8's command, unchanged, prints:

```
python3 readings.py census-after.json honesty-after.json --after
python3 readings.py docs/gameplay-census.json s9-honesty.json          # the before column
```

Rates carry Wilson 95% intervals. The arms landed together, so an outcome delta
below is not attributable to any one of them; only the Conf. cells and the
lab's minus-one rows (2.5) attribute a mechanism to one arm.

### 6.1 The process cells

The scorecard's rows, s9 at baseline 9 before and the candidate after (the
before column is the shipped `samples/9p2i` entry, equal to its `--set-dir`
fold in all 108 leaves at `F`). They move with the game, and none is a gate.

| row | s9 before | candidate after |
|---|---|---|
| games; meetings; ballots (EJECT, SKIP) | 50; 145; 845 (496, 349) | 50; 124; 717 (387, 330) |
| 1 grounded decisions, EJECT | 494/496 = 0.996 (0.99-1.00) | 384/387 = 0.992 (0.98-1.00) |
| 1 grounded decisions, SKIP | 79/349 = 0.226 (0.19-0.27) | 54/330 = 0.164 (0.13-0.21) |
| 1 grounded decisions, all ballots | 573/845 = 0.678 (0.65-0.71) | 438/717 = 0.611 (0.57-0.65) |
| 2 EJECTs deviating from the voter's own suspicion argmax | 31/413 = 0.075 (0.05-0.10) | 67/275 = 0.244 (0.20-0.30) |
| 2 role-correct, followers vs deviators (chance) | 359/382 vs 3/31 (0.298) | 200/208 vs 5/67 (0.327) |
| 3 manufactured contradiction | 0/17, all 17 not evaluable | 0/22, all 22 not evaluable |
| 4 unexplained decisions | 5/845 = 0.006 | 7/717 = 0.010 |
| 5 evidence-quality mix over ejections | contradiction flag 2, first hand 16, hearsay 2, vent flag 70 (of 90) | contradiction flag 2, first hand 27, hearsay 1, vent flag 24 (of 54) |
| 6 rationale faithfulness (tokens) | 708/708 (137 not evaluable) | 588/588 (129 not evaluable) |
| 7 agent-authored share | 841/845 = 0.995 (typed rewrites: invalid target 3, teammate coerced 1) | 701/717 = 0.978 (typed rewrites: teammate coerced 16) |
| 8 wrong-but-believable, reported and never penalised | 119/496 = 0.240 | 178/387 = 0.460 |
| 9 role-correct ejection, reported and never a gate | 81/90 = 0.900 | 39/54 = 0.722 |

Row 7's 16 typed rewrites are the 16 impostor ballots that named a teammate
(6.2, impostor ballot); the meeting layer coerced each to a skip and labelled
it, so none was recorded.

### 6.2 Each arm: its Conf. cells, then its reading

**Every Conf. cell reads 0 as built.** The census exits non-zero on any breach;
it exited 0 on the round.

| arm | Conf. cell | s9 before | after |
|---|---|---|---|
| physical witness | exits seen only from the room left | 9/85 | **0/72** |
| physical witness | vent-band ejections resting only on them | 8/70 | **0/24** |
| look and wait | surfacings before the cap with a non-teammate in the inferred-visible set | 52/85 | **0/72** |
| look and wait | trips over the cap | 0/0 | **0/63** |
| own fresh kill | entries not after the impostor's own fresh kill | 13/105 | **0/142** |
| full reset | stale report meetings | 43/135 | **0/118** |
| full reset | reported corpses older than the last regroup | 0/0 | **0/68** |
| full reset | play resumes with an impostor in a vent | 10/107 | **0/110** |
| full reset | play resumes with a corpse | 60/107 | **0/110** |
| full reset | kills at T+1 to T+4 after a regroup | 0/0 | **0/139** |
| one reply | rebuttals the selector would not have chosen | 0/0 | **0/121** |
| one reply | meetings with a second repeat-speaker turn | 0/145 | **0/124** |
| body handle | report openings carrying the kill-tick handle | 135/135 | **0/118** |
| kill row | own-kill rows naming a teammate or held by a non-witness | 0/0 | **0/4** |
| impostor ballot | recorded teammate ballot targets | 0/210 | **0/203** |
| impostor ballot | the gate's `no_betrayal_ballots_or_accusations` | 0 | **0 of 717** |
| self-report off | impostor openers | 0/145 | **0/124** |

The two full-reset cells no named source carries (false resume perceptions,
the regroup notice) stay **not carried**: what stands behind them is the one
resume helper and the notice fold, re-rendered byte-equal by the golden's walk
over all 1,556 recorded prompts.

**Physical witness.** Conf. cells only; both read 0. Reading: as built.

**Look and wait.** Exits seen from the exit room: 53/85 = 0.624 (0.52-0.72)
before, **8/72 = 0.111 (0.06-0.20)** after. By 1.6's rule (0.30 or below),
the reading is **effective**. Beside it: exits into a room the impostor could
see a crewmate in, 31/85 before and 0/72 after. Reported: forced exits at the
cap 13/72 = 0.181 (0.11-0.28); ticks inside per surfaced trip 1 tick 51, 2
ticks 6, 3 ticks 2, 4 ticks 13 (s9: 85 at 1 tick); near-body cost, in-place
surfacings a crewmate reaches, 2/37 = 0.054; kills within 2 ticks of the
killer's surfacing 0/227 (s9 3/175).

**Own fresh kill.** Conf. cell only; 13/105 before, 0/142 after. Reading: as
built.

**Full reset.** Conf. cells all 0; regroup notice and false resume
perceptions not carried (above). Reported: skipped report meetings 55/135 =
0.407 (0.33-0.49) before, 70/118 = 0.593 (0.50-0.68) after; meetings per game
2.90 before, 2.48 after; trips closed by a regroup 46/142 = 0.324; kill-witness
button calls within 6 ticks of a regroup 0/6; trigger-tick events a regroup
dropped: `Moved` 51, `TaskProgressed` 26, `TaskCompleted` 6; meetings opening
with an impostor in a vent 29/145 = 0.200 before, 66/124 = 0.532 (0.44-0.62)
after. As pre-registered, the reset does not zero the opening cell; on this
round it rose.

**One reply.** Opener rebuttals answering the charged tick with an alibi,
whereabouts or sighting: **19/19 = 1.000 (0.83-1.00)**, with 82 opener
rebuttals not evaluable (the census could not tie the charge to one tick);
rebuttals that only redirect: 17/121 = 0.140 (0.09-0.21). By 1.6's rule
(half or more answer; redirect-only below half), the reading is **effective**,
resting on the 19 evaluable of 101 opener rebuttals. Reported: an accused
opener answered in 0/125 before and 101/112 = 0.902 after; rebuttals carrying
an alibi 104/121, a whereabouts claim 104/121, a sighting 91/121; rebuttals
accusing a player who already spoke 121/121; beneficiaries: the opener
answering an impostor 71, the opener answering a crewmate 30, another impostor
answering a crewmate 17, another crewmate answering an impostor 3; reporter
ejections are the envelope's row. Ballots citing a rebuttal stay **not
carried**.

**Body handle.** Conf. cell only; 135/135 openings carried the kill-tick
handle before, 0/118 after. Reading: as built.

**Kill row.** Conf. cell 0/4. Presence: **present**, 4 own-kill rows served.
Reported, with no effect reading at this size: the holder cited its own-kill
row in 3 of 4; honesty cell 5, 4 kill holders and 3 of 4 citing the kill (s9:
4 holders, 3 of 4 citing it through a sighting).

**Impostor ballot.** Conf. cells 0. Impostor EJECTs whose only citation is a
neutral row (honesty cell 3): 1/46 before, when the rule did not exist, and
**0/107 = 0.000 (0.00-0.03)** after. By 1.6's rule (0.10 or below), **the
wording holds**. Reported: impostor EJECT share 46/210 = 0.219 before, 107/203
= 0.527 (0.46-0.59) after; EJECTs labelled supported 44/46 and 107/107;
authored teammate targets 1/210 and 16/203 (each coerced to a skip, recorded
0); ejections whose floor only impostor ballots met 0/90 and 0/54. SKIPs
labelled `none_held` stay **not carried**.

**Self-report off.** Conf. cell 0/124. As built.

### 6.3 The envelope, non-gating

| cell | s9 before | after | envelope |
|---|---|---|---|
| impostor win share | 11/50 = 0.22 (0.13-0.35) | **34/50 = 0.68 (0.54-0.79)** | **flagged above 0.60: it names the status-quo fallback for the vent exit** |
| innocent ejections | 9 of 90 | 15 of 54 | reported |
| reporters ejected per report meeting | 7/135 = 0.052 | 11/118 = 0.093 (0.05-0.16) | at or below 0.104, not flagged |
| role-correct ejections | 81/90 | 39/54 | reported (6.4) |
| meetings with vent proof | 70/145 = 0.483 | 26/124 = 0.210 (0.15-0.29) | reported |
| scorecard rows 1-9 | as published | 6.1 | reported |

The flag and the look-and-wait reading point different ways, and the audit
does not reconcile them: the vent exit now hides the impostor as built
(effective), and the side it favours now wins 68% of games. The arms landed
together, and the vent-proof meetings fell with the witnessed exits, so the
win share is not attributable to the vent exit alone; the lab's minus-one rows
(2.5) give mechanical attribution only, on fake games.

### 6.4 Role-correct ejection and the win split, gating nothing

Role-correct ejections 81/90 = 0.900 before, 39/54 = 0.722 (0.59-0.82) after.
The win split was 39 crew and 11 impostor wins before, 16 crew and 34
impostor wins after. Both are reported beside the readings and gate nothing;
a wrong ejection on believable data is the game working (scorecard row 8).

### 6.5 The decision menu, per arm

The audit gives no verdict. For each arm, the owner chooses among 1.7's
options: **adopt** through the era-keyed promotion (the path compatible with
the ML hold); **iterate** as round 2 under a new value in
`replays/candidates/stage-b-r2/`; **escalate** to hidden travel (the vent exit
only); or **fall back** to the status quo.

| arm | field and value | what the round read | the options |
|---|---|---|---|
| physical witness | `vent_witness_rule = physical` | Conf. 0 | adopt, iterate, fall back |
| look and wait | `vent_exit_policy = look_and_wait` | Conf. 0; **effective** (8/72); the envelope's flag names its status-quo fallback | adopt, iterate, escalate, fall back |
| own fresh kill | `vent_entry_policy = own_fresh_kill` | Conf. 0 | adopt, iterate, fall back |
| full reset | `meeting_reset = hub_with_grace` | Conf. 0; the opening-in-vent cell rose | adopt, iterate, fall back |
| one reply | `bounded_rebuttal_version = 1` | Conf. 0; **effective** on 19 evaluable | adopt, iterate, fall back |
| body handle | `report_body_handle_version = 1` | Conf. 0 | adopt, iterate, fall back |
| kill row | `ballot_kill_row_version = 1` | Conf. 0; **present** (4 rows) | adopt, iterate, fall back |
| impostor ballot | `impostor_ballot_version = 1` | Conf. 0; **the wording holds** (0/107) | adopt, iterate, fall back |

### 6.6 Limitations

- Hosted generation is not byte-reproducible, so a seed is re-recorded only by
  the failed-seed rule, never to change its bytes.
- The arms land together; only the Conf. cells and the lab rows attribute.
- 50 games: the kill row served 4 rows, and the one-reply reading rests on 19
  evaluable opener rebuttals of 101.
- Four pre-registered cells are not carried by any named source (false resume
  perceptions, the regroup notice, ballots citing a rebuttal, `none_held`
  SKIPs).
- Recording wall and the husk's spend come from the recorder's logs and the
  husk file, kept outside the repository; every other count reproduces from
  the committed bytes with the commands above.
