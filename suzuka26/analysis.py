"""
F1 2026 Japanese GP - Strategy Hypothetical Analysis
=====================================================
Question: What if Piastri stays out and pits under the Safety Car (lap 22)
alongside Antonelli? He comes out P1, Antonelli P2 — what happens?

Pulls all data live from the OpenF1 API.
"""

from openf1 import (
    get_session_key, get_laps, get_sectors, get_driver_pits,
    get_safety_car_laps, get_total_laps,
)

# --- Config ---
YEAR = 2026
COUNTRY = "Japan"
PIASTRI = 81
ANTONELLI = 12
HAMILTON = 44

print("Fetching 2026 Japanese GP data from OpenF1 API...")
session = get_session_key(YEAR, COUNTRY)
total_laps = get_total_laps(session)
sc_periods = get_safety_car_laps(session)

# Identify SC period
sc_start, sc_end = sc_periods[0] if sc_periods else (None, None)
restart_lap = sc_end + 1 if sc_end else None

print(f"  Session key: {session}")
print(f"  Total laps: {total_laps}")
print(f"  Safety car: laps {sc_start}-{sc_end}, restart lap {restart_lap}")

# Pull lap + sector data
pia_laps = get_laps(session, PIASTRI)
ant_laps = get_laps(session, ANTONELLI)
ham_laps = get_laps(session, HAMILTON)
pia_sectors = get_sectors(session, PIASTRI)
ant_sectors = get_sectors(session, ANTONELLI)

# Pit stop laps
pia_pit_laps = get_driver_pits(session, PIASTRI)
ant_pit_laps = get_driver_pits(session, ANTONELLI)

print(f"  Piastri pits: laps {pia_pit_laps}")
print(f"  Antonelli pits: laps {ant_pit_laps}")
print("  Data loaded.\n")

pia_actual_pit = pia_pit_laps[0] if pia_pit_laps else 18
ant_actual_pit = ant_pit_laps[0] if ant_pit_laps else 22


def avg(vals):
    return sum(vals) / len(vals) if vals else 0


def cumulative(laps_dict, start=1, end=None):
    end = end or total_laps
    total = 0
    result = {}
    for lap in range(start, end + 1):
        if lap in laps_dict:
            total += laps_dict[lap]
            result[lap] = total
    return result


# ===================================================================
# PART 1: ACTUAL RACE — Cumulative gap analysis
# ===================================================================
print("=" * 70)
print("  2026 JAPANESE GP — STRATEGY HYPOTHETICAL ANALYSIS")
print("  What if Piastri stays out and pits under Safety Car?")
print("=" * 70)

print("\n" + "=" * 70)
print("  PART 1: ACTUAL RACE — Gap Evolution (Piastri vs Antonelli)")
print("=" * 70)

pia_cum = cumulative(pia_laps)
ant_cum = cumulative(ant_laps)

print(f"\n{'Lap':>4} | {'Piastri (cum)':>14} | {'Antonelli (cum)':>15} | {'Gap (PIA-ANT)':>14} | Notes")
print("-" * 75)
for lap in range(1, total_laps + 1):
    if lap not in pia_cum or lap not in ant_cum:
        continue
    gap = pia_cum[lap] - ant_cum[lap]
    note = ""
    if lap == pia_actual_pit:
        note = "<-- PIA pits (actual)"
    elif lap == sc_start:
        note = "<-- SC + ANT pits"
    elif lap == restart_lap:
        note = "<-- Restart"
    if lap <= sc_start or lap in [restart_lap, restart_lap + 5, restart_lap + 10,
                                   restart_lap + 15, restart_lap + 20, total_laps] or note:
        print(f"{lap:4d} | {pia_cum[lap]:14.3f} | {ant_cum[lap]:15.3f} | {gap:+14.3f} | {note}")

# ===================================================================
# PART 2: HYPOTHETICAL — Piastri stays out until SC
# ===================================================================
print("\n" + "=" * 70)
print(f"  PART 2: HYPOTHETICAL — Piastri stays out, pits under SC (lap {sc_start})")
print("=" * 70)

# Estimate Piastri's pace if he stays out on old tires from his pit lap to SC
# Use his last 4 pre-pit laps as baseline, add conservative 0.1s/lap degradation
pre_pit_laps = [pia_laps[l] for l in range(max(1, pia_actual_pit - 4), pia_actual_pit)
                if l in pia_laps]
baseline_pace = avg(pre_pit_laps) if pre_pit_laps else 95.0

print(f"\nPiastri pre-pit pace (laps {pia_actual_pit-4}-{pia_actual_pit-1}): avg {baseline_pace:.3f}s")
print("Estimated staying-out pace (adding ~0.1s/lap conservative deg):")

pia_hypo = dict(pia_laps)
for i, lap in enumerate(range(pia_actual_pit, sc_start)):
    estimated = baseline_pace + (i + 1) * 0.1
    pia_hypo[lap] = estimated
    print(f"  Lap {lap}: {estimated:.1f}s  (actual: {pia_laps.get(lap, 'N/A')})")

print(f"\nFor reference, Antonelli on same old tires:")
for lap in range(pia_actual_pit, sc_start):
    if lap in ant_laps:
        print(f"  Lap {lap}: {ant_laps[lap]:.3f}s")

# SC pit lap: similar to Antonelli's
pia_hypo[sc_start] = ant_laps.get(sc_start, 113.5)

# SC laps: use Antonelli's SC pace (nose to tail)
for lap in range(sc_start + 1, restart_lap):
    if lap in ant_laps:
        pia_hypo[lap] = ant_laps[lap]

print(f"\n--- Cumulative gap: Hypothetical Piastri vs Actual Antonelli ---")
print(f"{'Lap':>4} | {'PIA hypo (cum)':>15} | {'ANT actual (cum)':>17} | {'Gap':>10} | Notes")
print("-" * 75)

pia_h_cum = 0
ant_a_cum = 0
for lap in range(1, total_laps + 1):
    if lap not in pia_hypo or lap not in ant_laps:
        continue
    pia_h_cum += pia_hypo[lap]
    ant_a_cum += ant_laps[lap]
    gap = ant_a_cum - pia_h_cum

    note = ""
    if lap == pia_actual_pit:
        note = "PIA stays out (hypo)"
    elif lap == sc_start - 1:
        note = "Pre-SC"
    elif lap == sc_start:
        note = "Both pit under SC"
    elif lap == restart_lap:
        note = f"RESTART — PIA P1, ANT P2"
    elif lap == total_laps:
        note = "CHEQUERED FLAG"

    if (lap <= sc_start or lap == restart_lap or lap % 5 == 0
            or lap == total_laps or note):
        print(f"{lap:4d} | {pia_h_cum:15.3f} | {ant_a_cum:17.3f} | {gap:+10.3f} | {note}")

# ===================================================================
# PART 3: POST-RESTART LAP-BY-LAP BATTLE
# ===================================================================
print("\n" + "=" * 70)
print(f"  PART 3: POST-RESTART LAP-BY-LAP (PIA P1 vs ANT P2)")
print("=" * 70)

print(f"\n{'Lap':>4} | {'PIA (s)':>8} | {'ANT (s)':>8} | {'Delta':>8} | {'Cum Gap':>10} | {'DRS?':>5}")
print("-" * 60)

restart_gap = 1.0
cum_gap = restart_gap

post_laps = list(range(restart_lap, total_laps + 1))
for lap in post_laps:
    if lap not in pia_laps or lap not in ant_laps:
        continue
    pia_t = pia_laps[lap]
    ant_t = ant_laps[lap]
    delta = pia_t - ant_t
    cum_gap -= delta
    drs = "YES" if cum_gap < 1.0 else "no"
    print(f"{lap:4d} | {pia_t:8.3f} | {ant_t:8.3f} | {delta:+8.3f} | {cum_gap:10.3f} | {drs}")

print(f"\nFinal gap at flag: {cum_gap:.3f}s")

# ===================================================================
# PART 4: SECTOR-BY-SECTOR ADVANTAGE
# ===================================================================
print("\n" + "=" * 70)
print("  PART 4: SECTOR-BY-SECTOR — WHERE DOES ANTONELLI GAIN?")
print("=" * 70)

s1_deltas, s2_deltas, s3_deltas = [], [], []
for lap in post_laps:
    if lap in pia_sectors and lap in ant_sectors:
        ps = pia_sectors[lap]
        an = ant_sectors[lap]
        if ps[0] and an[0]:
            s1_deltas.append(ps[0] - an[0])
        if ps[1] and an[1]:
            s2_deltas.append(ps[1] - an[1])
        if ps[2] and an[2]:
            s3_deltas.append(ps[2] - an[2])

avg_s1 = avg(s1_deltas)
avg_s2 = avg(s2_deltas)
avg_s3 = avg(s3_deltas)

print(f"\nAverage sector deltas (PIA - ANT), positive = ANT faster:")
print(f"  Sector 1 (includes S-curves): {avg_s1:+.3f}s  {'<-- ANT advantage' if avg_s1 > 0 else '<-- PIA advantage'}")
print(f"  Sector 2 (Degner/Hairpin/Spoon/130R): {avg_s2:+.3f}s  {'<-- ANT advantage' if avg_s2 > 0 else '<-- PIA advantage'}")
print(f"  Sector 3 (Casio/Main straight):  {avg_s3:+.3f}s  {'<-- ANT advantage' if avg_s3 > 0 else '<-- PIA advantage'}")
print(f"  TOTAL per-lap advantage: {avg_s1 + avg_s2 + avg_s3:+.3f}s for {'Antonelli' if (avg_s1+avg_s2+avg_s3) > 0 else 'Piastri'}")

# ===================================================================
# PART 5: CAN ANTONELLI OVERTAKE?
# ===================================================================
print("\n" + "=" * 70)
print("  PART 5: CAN ANTONELLI OVERTAKE FROM P2?")
print("=" * 70)

n_post = len(post_laps)
ant_faster = sum(1 for l in post_laps if l in ant_laps and l in pia_laps and ant_laps[l] < pia_laps[l])
pia_faster = n_post - ant_faster

ant_post_avg = avg([ant_laps[l] for l in post_laps if l in ant_laps])
pia_post_avg = avg([pia_laps[l] for l in post_laps if l in pia_laps])
total_pace_gain = sum(pia_laps[l] - ant_laps[l] for l in post_laps if l in pia_laps and l in ant_laps)

print(f"\nPost-restart stats (laps {restart_lap}-{total_laps}):")
print(f"  Antonelli faster on {ant_faster}/{n_post} laps")
print(f"  Piastri faster on {pia_faster}/{n_post} laps")
print(f"  Antonelli avg pace: {ant_post_avg:.3f}s")
print(f"  Piastri avg pace:   {pia_post_avg:.3f}s")
print(f"  Average delta:      {pia_post_avg - ant_post_avg:.3f}s/lap in Antonelli's favor")
print(f"  Total pace gain by Antonelli over {n_post} laps: {total_pace_gain:.3f}s")

# ===================================================================
# PART 6: DIRTY AIR — Antonelli traffic vs clean air (same stint)
# ===================================================================
print("\n" + "=" * 70)
print("  PART 6: DIRTY AIR EFFECT — Measured from Antonelli's own data")
print("=" * 70)

# Dirty air: laps 5 to (first pit ahead - 1), excluding outliers (lap 1, lap 11 missing S1, lap 16 battling)
# Antonelli was stuck behind Russell/Leclerc in the train
# Clean air: from first car-ahead pit to his own pit or SC

# Determine when cars ahead pitted (Norris L16, Leclerc L17 → Antonelli clean from L17)
dirty_laps = [l for l in range(5, 16) if l in ant_laps and l != 11]
clean_laps_stint1 = [l for l in range(17, sc_start) if l in ant_laps]

dirty_laps_avg = avg([ant_laps[l] for l in dirty_laps])
clean_laps_avg = avg([ant_laps[l] for l in clean_laps_stint1])
dirty_air_cost = dirty_laps_avg - clean_laps_avg

dirty_s1, dirty_s2, dirty_s3 = [], [], []
clean_s1, clean_s2, clean_s3 = [], [], []

for l in dirty_laps:
    if l in ant_sectors:
        s = ant_sectors[l]
        if s[0]: dirty_s1.append(s[0])
        if s[1]: dirty_s2.append(s[1])
        if s[2]: dirty_s3.append(s[2])

for l in clean_laps_stint1:
    if l in ant_sectors:
        s = ant_sectors[l]
        if s[0]: clean_s1.append(s[0])
        if s[1]: clean_s2.append(s[1])
        if s[2]: clean_s3.append(s[2])

avg_dirty_s1, avg_dirty_s2, avg_dirty_s3 = avg(dirty_s1), avg(dirty_s2), avg(dirty_s3)
avg_clean_s1, avg_clean_s2, avg_clean_s3 = avg(clean_s1), avg(clean_s2), avg(clean_s3)

s1_cost = avg_dirty_s1 - avg_clean_s1
s2_cost = avg_dirty_s2 - avg_clean_s2
s3_cost = avg_dirty_s3 - avg_clean_s3

print(f"""
Antonelli's OWN pace: dirty air (laps {dirty_laps[0]}-{dirty_laps[-1]}) vs clean air (laps {clean_laps_stint1[0]}-{clean_laps_stint1[-1]})
Same tires, same fuel window (roughly), different air quality.

                  DIRTY AIR    CLEAN AIR    DELTA (dirty - clean)
  Sector 1:           {avg_dirty_s1:.3f}s      {avg_clean_s1:.3f}s       {s1_cost:+.3f}s
  Sector 2:           {avg_dirty_s2:.3f}s      {avg_clean_s2:.3f}s       {s2_cost:+.3f}s
  Sector 3:           {avg_dirty_s3:.3f}s      {avg_clean_s3:.3f}s       {s3_cost:+.3f}s
  FULL LAP:           {dirty_laps_avg:.3f}s      {clean_laps_avg:.3f}s       {dirty_air_cost:+.3f}s

  TOTAL dirty air cost per lap: {dirty_air_cost:+.3f}s
  S1 accounts for: {s1_cost:.3f}s ({s1_cost/dirty_air_cost*100:.0f}% of total loss)
  S2 accounts for: {s2_cost:.3f}s ({s2_cost/dirty_air_cost*100:.0f}% of total loss)
  S3 accounts for: {s3_cost:.3f}s ({s3_cost/dirty_air_cost*100:.0f}% of total loss)
""")

# Cross-reference: Piastri leading vs Antonelli following
pia_lead_avg = avg([pia_laps[l] for l in range(5, pia_actual_pit) if l in pia_laps])
ant_follow_avg = avg([ant_laps[l] for l in dirty_laps])

print(f"CROSS-REFERENCE: Stint 1 real-world scenario")
print(f"  Piastri leading (clean air, laps 5-{pia_actual_pit-1}):  avg {pia_lead_avg:.3f}s")
print(f"  Antonelli following (dirty air, laps {dirty_laps[0]}-{dirty_laps[-1]}): avg {ant_follow_avg:.3f}s")
print(f"  Observed gap: {ant_follow_avg - pia_lead_avg:+.3f}s/lap")

# ===================================================================
# PART 7: VERDICT
# ===================================================================
print("\n" + "=" * 70)
print("  VERDICT (single-race dirty air estimate)")
print("=" * 70)

clean_adv = pia_post_avg - ant_post_avg  # Antonelli's clean-air advantage
single_car_dirty = dirty_air_cost * 0.7  # estimated single-car dirty air
net_adv = clean_adv - single_car_dirty

print(f"""
SCENARIO: Piastri stays out → pits under SC lap {sc_start} → restarts P1
          Antonelli pits under SC lap {sc_start} → restarts P2

PACE REALITY:
  - Antonelli clean-air advantage:     {clean_adv:.3f}s/lap
  - Dirty air cost (train, measured):  {dirty_air_cost:.3f}s/lap
  - Single-car estimate (x0.7):       {single_car_dirty:.3f}s/lap
  - Net advantage behind Piastri:      {net_adv:+.3f}s/lap
  - Over {n_post} laps:                      {net_adv * n_post:+.1f}s total

PROBABILITY ESTIMATE:""")

if net_adv < 0:
    print(f"  Antonelli LOSES ground ({net_adv:+.3f}s/lap) → Piastri pulls away")
    print(f"  Piastri holds P1:  ~75-80%")
    print(f"  Antonelli passes:  ~15-20%")
    print(f"  Other:             ~5%")
else:
    laps_to_drs = 1.0 / max(0.01, net_adv)
    print(f"  Antonelli closes at {net_adv:+.3f}s/lap → DRS range in ~{laps_to_drs:.0f} laps")
    if net_adv * n_post < 1.0:
        print(f"  Cannot even reach DRS in {n_post} laps → Piastri holds P1: ~85%")
    elif net_adv * n_post < 3.0:
        print(f"  1-2 overtake attempts max → Piastri holds P1: ~65-70%")
    else:
        print(f"  Repeated pressure → Piastri holds P1: ~55-60%")

print(f"""
BOTTOM LINE:
  McLaren's decision to pit Piastri on lap {pia_actual_pit} cost them the race.
  Track position at Suzuka is worth ~{dirty_air_cost:.2f}s/lap in defensive value.
  Run dirty_air_multirace.py for a 3-race calibrated estimate.
""")
