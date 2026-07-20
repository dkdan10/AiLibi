import sys; sys.path.insert(0, "/home/user/AiLibi")
from pathlib import Path
from eval.watchability import (
    _supply_gauge_values, _reconstruct_kills, _game_facts,
)
from eval.validity import assemble_tournament_report
from eval.validity import resolve_roster_knobs, roles_by_seed
from engine.world import load_canonical_map
def derive(sample_dir):
    sd = Path(sample_dir)
    report = assemble_tournament_report(sd)
    npl, nimp, tpc = resolve_roster_knobs(sd)
    per_seed_roles = roles_by_seed(sd, num_players=npl, num_impostors=nimp, tasks_per_crewmate=tpc, game_map=load_canonical_map())
    recon = _reconstruct_kills(sd)
    kbs = {}
    for k in recon.kills: kbs.setdefault(k.seed, []).append(k)
    facts = [_game_facts(g, per_seed_roles[g.seed], [k.victim_role for k in kbs.get(g.seed, [])], integrity_ok=recon.integrity_ok) for g in report.games]
    gv = _supply_gauge_values(report, recon.kills, facts)
    print(f"=== {sd.name} ===")
    print(f"witnessed_event_rate = {gv.crew_witnessed_kills}/{gv.total_kills} = {gv.witnessed_event_rate}")
    print(f"flags_per_meeting = {gv.total_flags}/{gv.meetings_total} = {gv.flags_per_meeting}  (persisted_vent {gv.persisted_vent_flags} + rederived {gv.total_flags-gv.persisted_vent_flags})")
    print(f"testimony_backed_conversion = {gv.backed_conversion_converted}/{gv.backed_conversion_attempted} = {gv.testimony_backed_conversion}")
for d in ["replays/samples/9p2i", "replays/samples/4p1i"]:
    derive("/home/user/AiLibi/" + d)
