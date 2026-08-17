#!/usr/bin/env python3
"""Task 18.26 owner brief — a personal PDF for Daniel, not a repo artifact."""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, HRFlowable)

OUT = "/Users/danielkeinan/ailibi-campaign-1826/AiLibi-18.26-owner-brief.pdf"
styles = getSampleStyleSheet()

DARK = colors.HexColor("#1a2332")
ACCENT = colors.HexColor("#2563eb")
GOOD = colors.HexColor("#166534")
BAD = colors.HexColor("#991b1b")
GREY = colors.HexColor("#6b7280")
LIGHT = colors.HexColor("#f1f5f9")

h1 = ParagraphStyle("h1", parent=styles["Title"], fontSize=20, textColor=DARK, spaceAfter=2)
sub = ParagraphStyle("sub", parent=styles["Normal"], fontSize=10, textColor=GREY, spaceAfter=10)
h2 = ParagraphStyle("h2", parent=styles["Heading1"], fontSize=13.5, textColor=ACCENT,
                    spaceBefore=14, spaceAfter=5)
h3 = ParagraphStyle("h3", parent=styles["Heading2"], fontSize=11, textColor=DARK,
                    spaceBefore=9, spaceAfter=3)
body = ParagraphStyle("body", parent=styles["Normal"], fontSize=9.4, leading=13.2, spaceAfter=5)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=14, bulletIndent=4, spaceAfter=3)
cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=8.2, leading=10.5)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")

def T(data, widths, header=True, highlight_rows=()):
    rows = [[Paragraph(c, cellb if i == 0 and header else cell) for c in r]
            for i, r in enumerate(data)]
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        style += [("BACKGROUND", (0, 0), (-1, 0), DARK)]
        rows[0] = [Paragraph(f'<font color="white">{c}</font>', cellb) for c in data[0]]
        t = Table(rows, colWidths=widths, repeatRows=1)
    for r in highlight_rows:
        style.append(("BACKGROUND", (0, r), (-1, r), LIGHT))
    t.setStyle(TableStyle(style))
    return t

story = []
A = story.append

A(Paragraph("AiLibi — Task 18.26 Owner Brief", h1))
A(Paragraph("The real-LLM finalist eval · PR #317 merged 2026-08-01 · baseline-6 substrate · "
            "Qwen/Qwen3.6-27B via Featherless · seeds 0-49 · $0", sub))
A(HRFlowable(width="100%", thickness=1, color=ACCENT))

A(Paragraph("1 · Campaign at a glance", h2))
A(Paragraph(
    "Nine arms recorded on the real path at 50 seeds each (449 kept games; one documented exclusion): "
    "four impostor finalists, a fresh all-scripted FSM comparator, and four crew diagnostics against the "
    "frozen champion. Pre-registration (both cells, the slate, the protocol) was committed before any seed "
    "ran. Full attempt wall 105.2 h over 505 attempts at the rolling two-leg posture (12.5 min per recorded "
    "game — 2.5% over the pre-registered rate). Every measurement, split view, derived comparison cell, and "
    "duration digest is persisted in <b>training/reports/results-finalist-eval.jsonl</b> and guarded by "
    "31 pin tests; the 17.14 rows are preserved untouched. The evidence survived a 17-round automated "
    "review (~45 comments: fixed, rebutted from the ratified texts, or owner-ruled).", body))

A(Paragraph("2 · Axis 1 — the selection table", h2))
A(T([
    ["arm", "role", "win rate", "delta vs FSM", "referee", "flags (floor 1.091)", "conversion (derived floor)", "witnessed (floor 0.034)"],
    ["ea4bc955", "champion (slate 1)", "0.52", "+0.26", "FAIL", "0.936", "0.367 / 0.669", "0.152"],
    ["bfd145cb", "runner-up (slate 2)", "0.56", "+0.30", "FAIL", "0.900", "0.351 / 0.695", "0.148"],
    ["6d327dcb", "incumbent (slate 3)", "0.38", "+0.12", "FAIL", "0.969", "0.444 / 0.646", "0.223"],
    ["7f73929d", "F13 arm (slate 4) - n=49", "0.429", "+0.184 (intersection)", "FAIL", "0.828", "0.389 / 0.755", "0.220"],
    ["FSM comparator", "all-scripted", "0.26", "-", "PASS", "1.198", "0.552 / 0.523", "0.046"],
], [0.85*inch, 1.35*inch, 0.62*inch, 1.02*inch, 0.55*inch, 0.95*inch, 1.05*inch, 0.85*inch],
   highlight_rows=(5,)))
A(Spacer(1, 4))
A(Paragraph(
    "<b>The one-line story:</b> every learned arm beats the scripted baseline on wins, and every learned arm "
    "fails the referee — the comparator is the slate's only referee PASS. The evidence-supply-for-wins trade "
    "is real at slate level, and win rank inverts gauge rank (bfd145cb wins most with the worst gauges; the "
    "incumbent wins least with the best). Note the substrate cost the incumbent 14 points (0.52 at "
    "baseline-5 to 0.38 here). All validity gates PASS on the five arms above; witnessed_event_rate is "
    "UNRESOLVABLE everywhere by the pre-registered noise rule and feeds no ruling.", body))

A(Paragraph("3 · The F13 cell (champions vs runner-ups) — answered, awaiting your ruling", h2))
A(Paragraph(
    "Pre-registered hypotheses: <b>A</b> — the ES trades evidence-supply for wins and runner-ups sit one step "
    "less far along the trade (their screening-time gauge margins persist at n=50); <b>B</b> — the n&lt;=6 "
    "referee reads were noise (the gap vanishes). Measured on the common 49-seed intersection:", body))
A(T([
    ["gauge", "champion mean", "runner-up mean", "margin", "pooled-side noises", "barred from supporting A by"],
    ["witnessed_event_rate", "0.192", "0.185", "-0.0065", "0.070 / 0.060", "both sides' noise"],
    ["flags_per_meeting", "0.955", "0.863", "-0.0919", "0.180 / 0.157", "both sides' noise"],
    ["testimony_backed_conv.", "0.404", "0.369", "-0.0348", "0.066 / 0.009", "champion side's noise"],
], [1.35*inch, 0.95*inch, 0.95*inch, 0.7*inch, 1.05*inch, 1.6*inch]))
A(Spacer(1, 4))
A(Paragraph(
    "<b>No gauge supports hypothesis A</b> under the registered either-side noise rule, and all three margins "
    "point the wrong way for A (negative — champions closer to the floors, not runner-ups). The shape is "
    "hypothesis-B (screening reads were noise), with the guard that A-unsupported is not B-demonstrated. "
    "The within-lineage pair (ea4bc955 vs bfd145cb) collapses to one readable gauge (conversion, -0.022). "
    "<b>The ruling is yours in 18.27.</b>", body))

A(PageBreak())

A(Paragraph("4 · Axis 2 — the emergence picture (the campaign's strongest finding)", h2))
A(Paragraph(
    "The clause-(a) statistics (pooled two-proportion z vs the same-seed FSM comparator, |z| at or over 1.96 "
    "starred) split the instrument set cleanly along the physical/language line:", body))
A(T([
    ["registered cell", "ea4bc955", "bfd145cb", "6d327dcb", "7f73929d", "arms over bar"],
    ["crew-witnessed kill rate", "+3.37 *", "+3.27 *", "+4.89 *", "+4.77 *", "4 / 4"],
    ["co-present departure", "+4.32 *", "+4.37 *", "+6.00 *", "+5.73 *", "4 / 4"],
    ["false-vouch saw_player", "+0.76", "+1.13", "+2.45 *", "+1.32", "1"],
    ["false-vouch corroboration", "+1.55", "+1.11", "+3.81 *", "+2.77 *", "2"],
    ["frame attempts / conv. / alibi / deflection", "under bar", "under bar", "under bar", "under bar", "0"],
    ["one-hop point-biserial (Fisher)", "-0.65", "-0.68", "+2.81 *", "+0.75", "1"],
], [1.85*inch, 0.85*inch, 0.85*inch, 0.85*inch, 0.85*inch, 0.85*inch], highlight_rows=(1, 2)))
A(Spacer(1, 4))
A(Paragraph(
    "<b>Reading:</b> the ES learned <i>physical kill-craft</i>, not rhetoric. Both physical cells clear the "
    "bar on all four arms — and co-present killing is literally absent from scripted play (corpus 0/505, "
    "comparator 0/174, every learned arm 0.076-0.187). The language layer is flat except the incumbent "
    "6d327dcb, the lone deception outlier (5 cells over bar). Each star is one limb of four: the split-"
    "reproducibility views are committed per row (clause b), zero of the five campaign ablation runs are "
    "clause-(c)-complete by their own reports, and both entropy rulings are NOT-DEMONSTRATED (the variance "
    "field's routed contract never landed). <b>No full emergence claim can fire this phase</b> — what you "
    "have is strong, honest observation evidence.", body))

A(Paragraph("5 · Crew diagnostics and the kill-rate rider", h2))
A(Paragraph(
    "<b>c1 (owned-tasks lineage) plays; c2 (general base) starves.</b> c1-gen9 is the only clean crew arm "
    "(validity PASS, meeting rate 1.0, 26/50 vs the champion) but the paired same-seed read against its "
    "gen-0 control is a null: 38/49 concordant seeds, discordants split 6-5, McNemar p = 1.0 — no "
    "learning signal in either direction. c2-gen0 is total starvation (zero meetings, zero LLM calls, "
    "crew 1/50); c2-gen9 reached exactly the 0.60 floor and produced two LLM-free deterministic stalemates "
    "— meeting-triggering is the one thing that lineage partially learned. <b>The routed 18.25 rider is "
    "answered: the elevated crew-witnessed kill rate is an artifact of learned-impostor kill placement</b> "
    "(gen-9 and gen-0 within a point of each other at the same opponent; elevation present against scripted "
    "crew and in the LLM-free leg; formally inconclusive as an equivalence — no margin was pre-registered). "
    "All crew axis-2 cells read NOT-DEMONSTRABLE (your ruling: no opponent-matched scripted-crew comparator "
    "was recorded).", body))

A(Paragraph("6 · Anomalies and gotchas worth remembering", h2))
for txt in [
    "<b>Seed 35 (7f73929d) is unrecordable at this substrate:</b> 14 attempts, every one the identical "
    "validation default at the first meeting's opening turn (deterministic pre-meeting prefix = identical "
    "prompt; the model reliably emits a schema-invalid turn). Slot 4 ships at n=49 with intersection cells "
    "for every affected read. The corresponding DoD box is explicitly un-ticked in the PR.",
    "<b>witnessed_event_rate cannot be resolved at n=50</b> under the 25% noise precondition — on any arm. "
    "If a future protocol needs that gauge to rule, it needs more seeds, not a waiver.",
    "<b>The corpus JSON has a trap:</b> the subkey named baseline_cells_corpus_9p2i is a stale baseline-5 "
    "snapshot (byte-identical across both roster entries); the true baseline-6 cells are the top-level "
    "blocks. Worth a cleanup task so 18.27+ tooling never quotes the wrong block.",
    "<b>Three stuck-seed classes now documented:</b> retryable validation-defaults (sampling variance), "
    "LLM-free deterministic stalemates (unretryable by construction), and meeting-bearing robust stalemates. "
    "Classes 2 and 3 exit rc 0 — record-time retry machinery never sees them.",
    "<b>Operational:</b> a failed attempt costs the same wall as a successful one (12.5 min); the two "
    "starved c2 legs ran at engine speed (50 games in 27 seconds of summed wall for c2-gen0).",
]:
    A(Paragraph(txt, bullet, bulletText="•"))

A(PageBreak())

A(Paragraph("7 · What you must rule for continuation (the 18.27 owner checklist)", h2))
A(Paragraph(
    "18.27 is an OWNER task — these rulings are yours, then the memo + the ruled branch get implemented "
    "(this thread has full context, or dispatch the generated prompt with your rulings attached).", body))
A(T([
    ["#", "ruling", "the evidence in front of you", "branches"],
    ["1", "<b>The flip (axis 1):</b> does the champion clear the §1.3 bar?",
     "ea4bc955: win 0.52, +0.26 over the same-seed FSM row, validity PASS — but referee FAIL "
     "(flags -0.155, conversion -0.302) with the witnessed gauge excluded as UNRESOLVABLE. "
     "Read the bar's verbatim terms in audit-phase-17-close.md §1.3 against §16.a.",
     "PASS: artifact surface swap + pre-author the 18.28 selector flip (default provably not yet moved). "
     "FAIL: default provably unmoved."],
    ["2", "<b>F13:</b> hypothesis A or B?",
     "No gauge supports A (either-side noise rule + direction); B-shaped but not demonstrated. "
     "Also decide what this means for trusting small-n referee screens in future campaigns.",
     "Rule A / rule B / rule insufficient."],
    ["3", "<b>Emergence claims (axis 2):</b> what status do the physical-layer observations get?",
     "Witnessed + co-present significant on 4/4 arms vs same-seed FSM; splits committed; but zero "
     "clause-(c)-complete ablations and entropy NOT-DEMONSTRATED — the §6 conjunction cannot complete.",
     "Observations-only this phase, or route an ablation follow-up contract to complete clause (c)."],
    ["4", "<b>Crew adoption:</b> confirm none.",
     "18.25 named no finalist; 18.26 concurs (c1 null vs control, c2 starves).",
     "Confirm; optionally route the scripted-crew-vs-champion comparator arm (~10 h) if crew claims "
     "are ever wanted."],
    ["5", "<b>Follow-up contracts to route (or drop), explicitly:</b>",
     "(a) entropy-variance field plumbing (pre-req for any future entropy ruling); "
     "(b) the scripted-crew-vs-ea4bc955 comparator arm; (c) the corpus-JSON legacy-block cleanup; "
     "(d) seed-35 re-record under a future substrate if slot 4 must reach n=50.",
     "Route / drop each, in the 18.27 memo."],
    ["6", "<b>Housekeeping:</b>",
     "~/ailibi-campaign-1826/ holds the recordings, leg logs, and the only copies of the seed-35 "
     "forensics — keep until 18.27 lands, then reclaimable.",
     "Keep / archive."],
], [0.28*inch, 1.5*inch, 3.05*inch, 2.15*inch]))

A(Paragraph("8 · Open questions (non-blocking, flagged for your read)", h2))
for txt in [
    "<b>Champion identity:</b> bfd145cb out-wins the ratified champion (0.56 vs 0.52) with worse gauges. "
    "The slate ratification named ea4bc955 the champion arm; if 18.27's bar reading turns on win edge "
    "alone, does the runner-up's edge matter, or is that exactly the trade F13 warns about?",
    "<b>Off-menu is vacuous everywhere</b> (0 in ~6,600 decisions per arm, corpus included). Perfect "
    "compliance, or an instrument that can no longer trigger on this substrate? Cheap to check once, "
    "worth knowing before it is quoted as a safety result.",
    "<b>The 6d327dcb deception outlier:</b> the incumbent — trained longest under the old substrate — is "
    "the only arm with language-layer significance. Artifact of its lineage, or the earliest visible "
    "rhetoric learning? The ablation route in ruling 3 would answer it.",
]:
    A(Paragraph(txt, bullet, bulletText="•"))

A(Spacer(1, 10))
A(HRFlowable(width="100%", thickness=0.7, color=GREY))
A(Paragraph(
    "Sources: training/reports/report-finalist-eval.md Part II (§8-§17) and results-finalist-eval.jsonl "
    "at merge commit of PR #317; pins in tests/training/test_finalist_eval_pins.py. This brief is a "
    "personal summary, not a repo artifact — every number above is quoted from the committed evidence.", sub))

SimpleDocTemplate(OUT, pagesize=letter, topMargin=0.65*inch, bottomMargin=0.65*inch,
                  leftMargin=0.7*inch, rightMargin=0.7*inch,
                  title="AiLibi 18.26 Owner Brief").build(story)
print("wrote", OUT)
