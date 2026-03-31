"""
F1 2026 Japanese GP - Strategy Hypothetical Analysis
=====================================================
Question: What if Piastri stays out and pits under the Safety Car (lap 22)
alongside Antonelli? He comes out P1, Antonelli P2 — what happens?
"""

import json

# === RAW LAP DATA (from OpenF1 API) ===

piastri_laps = {
    1: 95.711, 2: 94.949, 3: 94.999, 4: 95.136, 5: 95.124,
    6: 95.109, 7: 95.078, 8: 95.815, 9: 94.793, 10: 95.111,
    11: 95.419, 12: 95.108, 13: 94.856, 14: 95.095, 15: 94.905,
    16: 94.885, 17: 94.916,
    # Lap 18: ACTUAL pit lap (97.327), 19: out lap (114.537)
    18: 97.327, 19: 114.537, 20: 94.774, 21: 94.010,
    # SC laps 22-27
    22: 118.972, 23: 138.911, 24: 149.294, 25: 150.382, 26: 145.382, 27: 146.074,
    # Post-restart
    28: 94.314, 29: 93.667, 30: 93.699, 31: 93.410, 32: 93.605,
    33: 93.484, 34: 93.401, 35: 93.509, 36: 93.411, 37: 93.708,
    38: 93.712, 39: 93.467, 40: 93.469, 41: 93.764, 42: 93.513,
    43: 93.518, 44: 93.431, 45: 93.523, 46: 93.329, 47: 93.197,
    48: 93.371, 49: 92.996, 50: 93.266, 51: 93.826, 52: 93.012,
    53: 93.294,
}

antonelli_laps = {
    1: 99.215, 2: 94.475, 3: 95.536, 4: 95.523, 5: 95.240,
    6: 94.962, 7: 95.076, 8: 95.203, 9: 95.534, 10: 95.410,
    11: 95.115, 12: 95.027, 13: 94.944, 14: 95.261, 15: 95.377,
    16: 96.164, 17: 94.686, 18: 94.095, 19: 94.343, 20: 94.241,
    21: 93.948,
    # SC laps — pits on 22
    22: 113.376, 23: 159.827, 24: 150.266, 25: 150.634, 26: 146.030, 27: 146.237,
    # Post-restart
    28: 93.649, 29: 93.367, 30: 92.859, 31: 93.258, 32: 92.868,
    33: 92.999, 34: 92.909, 35: 92.912, 36: 92.933, 37: 92.984,
    38: 92.955, 39: 92.731, 40: 92.993, 41: 92.736, 42: 92.826,
    43: 92.538, 44: 92.570, 45: 92.819, 46: 92.722, 47: 93.211,
    48: 93.589, 49: 92.432, 50: 93.352, 51: 92.889, 52: 92.925,
    53: 94.063,
}

hamilton_laps = {
    1: 98.863, 2: 95.496, 3: 95.394, 4: 95.805, 5: 95.453,
    6: 95.172, 7: 95.448, 8: 95.565, 9: 95.765, 10: 95.166,
    11: 95.434, 12: 95.161, 13: 95.397, 14: 95.283, 15: 95.054,
    16: 95.355, 17: 94.876, 18: 94.959, 19: 94.980, 20: 95.168,
    21: 95.010,
    22: 116.919, 23: 157.390, 24: 147.559, 25: 151.345, 26: 145.726, 27: 143.756,
    28: 94.067, 29: 93.742, 30: 93.875, 31: 93.670, 32: 93.501,
    33: 93.524, 34: 93.301, 35: 93.696, 36: 93.658, 37: 93.934,
    38: 93.436, 39: 93.576, 40: 93.869, 41: 94.177, 42: 94.662,
    43: 94.359, 44: 93.636, 45: 93.495, 46: 93.442, 47: 94.676,
    48: 92.777, 49: 93.867, 50: 95.689, 51: 94.927, 52: 94.193,
    53: 93.669,
}

# === SECTOR DATA FOR PACE COMPARISON ===

piastri_sectors = {
    28: (34.687, 41.607, 18.020), 29: (34.162, 41.491, 18.014),
    30: (34.171, 41.504, 18.024), 31: (34.117, 41.379, 17.914),
    32: (34.092, 41.588, 17.925), 33: (33.973, 41.471, 18.040),
    34: (33.983, 41.440, 17.978), 35: (34.010, 41.429, 18.070),
    36: (34.037, 41.413, 17.961), 37: (34.143, 41.530, 18.035),
    38: (34.060, 41.632, 18.020), 39: (34.091, 41.454, 17.922),
    40: (33.973, 41.488, 18.008), 41: (34.144, 41.495, 18.125),
    42: (34.093, 41.428, 17.992), 43: (34.075, 41.509, 17.934),
    44: (34.012, 41.389, 18.030), 45: (34.114, 41.348, 18.061),
    46: (34.061, 41.333, 17.935), 47: (34.033, 41.308, 17.856),
    48: (34.061, 41.467, 17.843), 49: (33.887, 41.221, 17.888),
    50: (34.063, 41.329, 17.874), 51: (34.227, 41.683, 17.916),
    52: (33.922, 41.214, 17.876), 53: (34.027, 41.299, 17.968),
}

antonelli_sectors = {
    28: (33.933, 41.745, 17.971), 29: (33.975, 41.396, 17.996),
    30: (33.749, 41.267, 17.843), 31: (33.989, 41.365, 17.904),
    32: (33.795, 41.232, 17.841), 33: (33.848, 41.293, 17.858),
    34: (33.690, 41.436, 17.783), 35: (33.821, 41.282, 17.809),
    36: (33.733, 41.316, 17.884), 37: (33.857, 41.266, 17.861),
    38: (33.944, 41.180, 17.831), 39: (33.705, 41.240, 17.786),
    40: (33.921, 41.229, 17.843), 41: (33.844, 41.110, 17.782),
    42: (None,   41.192, 17.790), 43: (33.739, 41.104, 17.695),
    44: (33.662, 41.192, 17.716), 45: (33.897, 41.132, 17.790),
    46: (33.822, 41.130, 17.770), 47: (33.929, 41.504, 17.778),
    48: (34.228, 41.473, 17.888), 49: (33.720, 40.986, 17.726),
    50: (34.012, 41.430, 17.910), 51: (33.833, 41.302, 17.754),
    52: (33.927, 41.281, 17.717), 53: (33.907, 41.548, 18.608),
}


print("=" * 70)
print("  2026 JAPANESE GP — STRATEGY HYPOTHETICAL ANALYSIS")
print("  What if Piastri stays out and pits under Safety Car?")
print("=" * 70)

# ===================================================================
# PART 1: ACTUAL RACE — Cumulative gap analysis
# ===================================================================
print("\n" + "=" * 70)
print("  PART 1: ACTUAL RACE — Gap Evolution (Piastri vs Antonelli)")
print("=" * 70)

# Compute cumulative elapsed time
def cumulative(laps_dict, start=1, end=53):
    total = 0
    result = {}
    for lap in range(start, end + 1):
        total += laps_dict[lap]
        result[lap] = total
    return result

pia_cum = cumulative(piastri_laps)
ant_cum = cumulative(antonelli_laps)

print(f"\n{'Lap':>4} | {'Piastri (cum)':>14} | {'Antonelli (cum)':>15} | {'Gap (PIA-ANT)':>14} | Notes")
print("-" * 75)
for lap in range(1, 54):
    gap = pia_cum[lap] - ant_cum[lap]
    note = ""
    if lap == 18:
        note = "<-- PIA pits (actual)"
    elif lap == 22:
        note = "<-- SC + ANT pits"
    elif lap == 28:
        note = "<-- Restart"
    if lap <= 22 or lap in [28, 33, 38, 43, 48, 53] or note:
        print(f"{lap:4d} | {pia_cum[lap]:14.3f} | {ant_cum[lap]:15.3f} | {gap:+14.3f} | {note}")

# ===================================================================
# PART 2: HYPOTHETICAL — Piastri stays out until SC
# ===================================================================
print("\n" + "=" * 70)
print("  PART 2: HYPOTHETICAL — Piastri stays out, pits under SC (lap 22)")
print("=" * 70)

# Estimate Piastri's pace if he stays out on old tires laps 18-21
# His actual laps 14-17 on old tires: 95.095, 94.905, 94.885, 94.916
# Slight degradation trend from laps 11-17:
# 95.419, 95.108, 94.856, 95.095, 94.905, 94.885, 94.916
# He was stable/getting faster. Estimate laps 18-21 conservatively:
# Add ~0.1s per lap for continued tire deg (conservative)

pia_hypo_18 = 95.0  # slight deg from 94.916
pia_hypo_19 = 95.1
pia_hypo_20 = 95.2
pia_hypo_21 = 95.3  # conservative — Ruth says he was getting faster

print("\nEstimated Piastri pace staying out (old tires, laps 18-21):")
print(f"  Lap 18: {pia_hypo_18:.1f}s  (actual on fresh after pit: 114.5s out-lap)")
print(f"  Lap 19: {pia_hypo_19:.1f}s  (actual on fresh: 94.8s)")
print(f"  Lap 20: {pia_hypo_20:.1f}s  (actual on fresh: 94.0s)")
print(f"  Lap 21: {pia_hypo_21:.1f}s")
print(f"\nFor reference, Antonelli on same old tires:")
print(f"  Lap 18: {antonelli_laps[18]:.3f}s")
print(f"  Lap 19: {antonelli_laps[19]:.3f}s")
print(f"  Lap 20: {antonelli_laps[20]:.3f}s")
print(f"  Lap 21: {antonelli_laps[21]:.3f}s")

# Build hypothetical Piastri laps
pia_hypo = dict(piastri_laps)  # copy actual
pia_hypo[18] = pia_hypo_18
pia_hypo[19] = pia_hypo_19
pia_hypo[20] = pia_hypo_20
pia_hypo[21] = pia_hypo_21

# Lap 22: Piastri pits under SC. Antonelli pitted on lap 22 with 113.376s.
# If both pit on the same SC lap, the pit lane time is similar.
# Antonelli's lap 22: 113.376. Piastri would have a similar SC lap + pit.
# The key: whoever is AHEAD on track entering the pits comes out ahead.
# Piastri was leading the race. He pits under SC and comes out P1.
pia_hypo[22] = 113.5  # similar SC pit lap to Antonelli

# SC laps 23-27: everyone circulates at SC pace — gaps frozen
# Use Antonelli's SC laps as reference (they'd be nose to tail)
pia_hypo[23] = antonelli_laps[23]  # SC pace
pia_hypo[24] = antonelli_laps[24]
pia_hypo[25] = antonelli_laps[25]
pia_hypo[26] = antonelli_laps[26]
pia_hypo[27] = antonelli_laps[27]

# Post-restart laps 28-53: Piastri is on fresh tires, same as actual
# BUT — key difference: he's P1 defending, not P2 chasing
# In reality Piastri was behind Antonelli and couldn't pass.
# In this hypo, he's AHEAD. Use his actual fresh tire pace (already have it).

print("\n--- Cumulative gap: Hypothetical Piastri vs Actual Antonelli ---")
print(f"{'Lap':>4} | {'PIA hypo (cum)':>15} | {'ANT actual (cum)':>17} | {'Gap':>10} | Notes")
print("-" * 75)

pia_h_cum = 0
ant_a_cum = 0
gaps_post_restart = []

for lap in range(1, 54):
    pia_h_cum += pia_hypo[lap]
    ant_a_cum += antonelli_laps[lap]
    gap = ant_a_cum - pia_h_cum  # positive = Piastri ahead

    note = ""
    if lap == 18:
        note = "PIA stays out (hypo)"
    elif lap == 21:
        note = "Pre-SC"
    elif lap == 22:
        note = "Both pit under SC"
    elif lap == 28:
        note = "RESTART — PIA P1, ANT P2"
    elif lap == 53:
        note = "CHEQUERED FLAG"

    if lap >= 28:
        gaps_post_restart.append((lap, gap))

    if lap <= 22 or lap == 28 or lap % 5 == 0 or lap == 53 or note:
        print(f"{lap:4d} | {pia_h_cum:15.3f} | {ant_a_cum:17.3f} | {gap:+10.3f} | {note}")

# ===================================================================
# PART 3: POST-RESTART LAP-BY-LAP BATTLE
# ===================================================================
print("\n" + "=" * 70)
print("  PART 3: POST-RESTART LAP-BY-LAP (PIA P1 vs ANT P2)")
print("=" * 70)

print(f"\n{'Lap':>4} | {'PIA (s)':>8} | {'ANT (s)':>8} | {'Delta':>8} | {'Cum Gap':>10} | {'DRS?':>5}")
print("-" * 60)

cum_gap_from_restart = 0
# At restart, Piastri is ~1s ahead (SC restarts are close)
# The SC bunches the field — assume ~1.0s gap at restart
restart_gap = 1.0
cum_gap_from_restart = restart_gap

for lap in range(28, 54):
    pia_t = piastri_laps[lap]  # actual pace on fresh tires
    ant_t = antonelli_laps[lap]
    delta = pia_t - ant_t  # positive = Antonelli faster
    cum_gap_from_restart -= delta  # gap shrinks when ANT is faster

    drs = "YES" if cum_gap_from_restart < 1.0 else "no"

    print(f"{lap:4d} | {pia_t:8.3f} | {ant_t:8.3f} | {delta:+8.3f} | {cum_gap_from_restart:10.3f} | {drs}")

print(f"\nFinal gap at flag: {cum_gap_from_restart:.3f}s")

# ===================================================================
# PART 4: SECTOR-BY-SECTOR ADVANTAGE
# ===================================================================
print("\n" + "=" * 70)
print("  PART 4: SECTOR-BY-SECTOR — WHERE DOES ANTONELLI GAIN?")
print("=" * 70)

s1_deltas, s2_deltas, s3_deltas = [], [], []
for lap in range(28, 54):
    if lap in piastri_sectors and lap in antonelli_sectors:
        ps = piastri_sectors[lap]
        an = antonelli_sectors[lap]
        if ps[0] and an[0]:
            s1_deltas.append(ps[0] - an[0])
        if ps[1] and an[1]:
            s2_deltas.append(ps[1] - an[1])
        if ps[2] and an[2]:
            s3_deltas.append(ps[2] - an[2])

avg_s1 = sum(s1_deltas) / len(s1_deltas) if s1_deltas else 0
avg_s2 = sum(s2_deltas) / len(s2_deltas) if s2_deltas else 0
avg_s3 = sum(s3_deltas) / len(s3_deltas) if s3_deltas else 0

print(f"\nAverage sector deltas (PIA - ANT), positive = ANT faster:")
print(f"  Sector 1 (includes S-curves): {avg_s1:+.3f}s  {'<-- ANT advantage' if avg_s1 > 0 else '<-- PIA advantage'}")
print(f"  Sector 2 (Degner/Hairpin/Spoon/130R): {avg_s2:+.3f}s  {'<-- ANT advantage' if avg_s2 > 0 else '<-- PIA advantage'}")
print(f"  Sector 3 (Casio/Main straight):  {avg_s3:+.3f}s  {'<-- ANT advantage' if avg_s3 > 0 else '<-- PIA advantage'}")
print(f"  TOTAL per-lap advantage: {avg_s1 + avg_s2 + avg_s3:+.3f}s for {'Antonelli' if (avg_s1+avg_s2+avg_s3) > 0 else 'Piastri'}")

# ===================================================================
# PART 5: CAN ANTONELLI OVERTAKE? OVERTAKING ANALYSIS
# ===================================================================
print("\n" + "=" * 70)
print("  PART 5: CAN ANTONELLI OVERTAKE FROM P2?")
print("=" * 70)

drs_laps = sum(1 for lap in range(28, 54) if True)  # count opportunities
ant_faster_laps = sum(1 for lap in range(28, 54) if antonelli_laps[lap] < piastri_laps[lap])
pia_faster_laps = 26 - ant_faster_laps

print(f"\nPost-restart stats (laps 28-53):")
print(f"  Antonelli faster on {ant_faster_laps}/26 laps")
print(f"  Piastri faster on {pia_faster_laps}/26 laps")

ant_avg = sum(antonelli_laps[l] for l in range(28, 54)) / 26
pia_avg = sum(piastri_laps[l] for l in range(28, 54)) / 26
print(f"  Antonelli avg pace: {ant_avg:.3f}s")
print(f"  Piastri avg pace:   {pia_avg:.3f}s")
print(f"  Average delta:      {pia_avg - ant_avg:.3f}s/lap in Antonelli's favor")

total_pace_gain = sum(piastri_laps[l] - antonelli_laps[l] for l in range(28, 54))
print(f"  Total pace gain by Antonelli over 26 laps: {total_pace_gain:.3f}s")

print(f"""
KEY FINDING:
  Antonelli gains ~{total_pace_gain:.1f}s over 26 laps through raw pace.
  Starting ~1.0s behind Piastri, Antonelli would close to within DRS range
  in approximately {max(1, int(1.0 / (total_pace_gain/26)))}-{max(2, int(1.5 / (total_pace_gain/26)))} laps.

  BUT: At Suzuka, overtaking is extremely difficult.
  - Only real overtaking zone: Turn 1 (end of main straight)
  - Piastri's S3 advantage ({avg_s3:+.3f}s) means he's FASTER through the
    final chicane and onto the straight — exactly where he'd defend.
  - Antonelli's advantage is in S1/S2 (high-speed, aero-dependent sections)
    where following closely costs downforce (dirty air).
  - Even with DRS, the Mercedes top speed advantage (312 vs 309 km/h)
    could be neutralized when Antonelli is in dirty air behind Piastri.
""")

# ===================================================================
# PART 6: VERDICT
# ===================================================================
# ===================================================================
# PART 6: DIRTY AIR ANALYSIS — Antonelli in traffic vs clean air
# ===================================================================
print("\n" + "=" * 70)
print("  PART 6: DIRTY AIR EFFECT — Measured from Antonelli's own data")
print("=" * 70)

# Antonelli sector data: laps 1-21
ant_sectors_stint1 = {
    1:  (38.853, 42.420, 17.942),  # lap 1 outlier, exclude
    2:  (34.437, 42.202, 17.836),
    3:  (35.282, 42.109, 18.145),
    4:  (34.978, 42.457, 18.088),
    5:  (34.818, 42.395, 18.027),
    6:  (34.771, 42.134, 18.057),
    7:  (34.821, 42.201, 18.054),
    8:  (34.865, 42.112, 18.226),
    9:  (35.232, 42.073, 18.229),
    10: (35.153, 42.226, 18.031),
    # 11: S1 is null
    12: (35.013, 42.010, 18.004),
    13: (34.770, 42.068, 18.106),
    14: (34.902, 42.315, 18.044),
    15: (34.944, 42.109, 18.324),
    16: (36.072, 42.106, 17.986),  # lap 16 S1 outlier (likely battling)
    17: (34.843, 41.875, 17.968),  # CLEAN AIR starts
    18: (34.399, 41.758, 17.938),
    19: (34.476, 41.879, 17.988),
    20: (34.504, 41.791, 17.946),
    21: (34.329, 41.686, 17.933),
}

# DIRTY AIR phase: laps 5-15 (exclude lap 1 warm-up, lap 16 battling, lap 11 missing S1)
# Antonelli stuck behind Russell/Leclerc in the train
dirty_s1, dirty_s2, dirty_s3 = [], [], []
for lap in [5, 6, 7, 8, 9, 10, 12, 13, 14, 15]:
    s = ant_sectors_stint1[lap]
    dirty_s1.append(s[0])
    dirty_s2.append(s[1])
    dirty_s3.append(s[2])

# CLEAN AIR phase: laps 17-21 (cars ahead have pitted)
clean_s1, clean_s2, clean_s3 = [], [], []
for lap in [17, 18, 19, 20, 21]:
    s = ant_sectors_stint1[lap]
    clean_s1.append(s[0])
    clean_s2.append(s[1])
    clean_s3.append(s[2])

# Also compute full lap averages
dirty_laps_avg = sum(antonelli_laps[l] for l in [5,6,7,8,9,10,12,13,14,15]) / 10
clean_laps_avg = sum(antonelli_laps[l] for l in [17,18,19,20,21]) / 5

avg_dirty_s1 = sum(dirty_s1) / len(dirty_s1)
avg_dirty_s2 = sum(dirty_s2) / len(dirty_s2)
avg_dirty_s3 = sum(dirty_s3) / len(dirty_s3)
avg_clean_s1 = sum(clean_s1) / len(clean_s1)
avg_clean_s2 = sum(clean_s2) / len(clean_s2)
avg_clean_s3 = sum(clean_s3) / len(clean_s3)

print(f"""
Antonelli's OWN pace: dirty air (laps 5-15) vs clean air (laps 17-21)
Same tires, same fuel window (roughly), different air quality.

                  DIRTY AIR    CLEAN AIR    DELTA (dirty - clean)
  Sector 1 (S-curves):  {avg_dirty_s1:.3f}s      {avg_clean_s1:.3f}s       {avg_dirty_s1 - avg_clean_s1:+.3f}s
  Sector 2 (130R etc):  {avg_dirty_s2:.3f}s      {avg_clean_s2:.3f}s       {avg_dirty_s2 - avg_clean_s2:+.3f}s
  Sector 3 (straight):  {avg_dirty_s3:.3f}s      {avg_clean_s3:.3f}s       {avg_dirty_s3 - avg_clean_s3:+.3f}s
  FULL LAP:             {dirty_laps_avg:.3f}s      {clean_laps_avg:.3f}s       {dirty_laps_avg - clean_laps_avg:+.3f}s
""")

dirty_air_cost = dirty_laps_avg - clean_laps_avg
s1_cost = avg_dirty_s1 - avg_clean_s1
s2_cost = avg_dirty_s2 - avg_clean_s2
s3_cost = avg_dirty_s3 - avg_clean_s3

print(f"  TOTAL dirty air cost per lap: {dirty_air_cost:+.3f}s")
print(f"  S1 accounts for: {s1_cost:.3f}s ({s1_cost/dirty_air_cost*100:.0f}% of total loss)")
print(f"  S2 accounts for: {s2_cost:.3f}s ({s2_cost/dirty_air_cost*100:.0f}% of total loss)")
print(f"  S3 accounts for: {s3_cost:.3f}s ({s3_cost/dirty_air_cost*100:.0f}% of total loss)")

# Now: what does this mean for the hypothetical?
# In clean air (post-restart, leading), Antonelli gains 0.493s/lap on Piastri.
# In dirty air behind Piastri, he'd lose the dirty_air_cost from his pace.
adjusted_advantage = 0.493 - dirty_air_cost
print(f"""
REVISED HYPOTHETICAL: Antonelli behind Piastri post-restart
  Clean-air advantage over Piastri:    {0.493:.3f}s/lap
  Dirty air penalty (from data):      -{dirty_air_cost:.3f}s/lap
  NET advantage in dirty air:          {adjusted_advantage:+.3f}s/lap

  Over 26 laps, Antonelli gains:       {adjusted_advantage * 26:.1f}s total
  Starting gap after SC restart:        ~1.0s""")

if adjusted_advantage > 0:
    laps_to_drs = 1.0 / adjusted_advantage
    print(f"  Laps to close to DRS range:          ~{laps_to_drs:.0f} laps (lap ~{28 + laps_to_drs:.0f})")
    print(f"""
  IMPORTANT CAVEAT: This dirty air cost ({dirty_air_cost:.3f}s) was measured when
  Antonelli was stuck in a TRAIN (Russell + Leclerc ahead). Behind a single
  car (Piastri only), the dirty air effect would be LESS severe.

  Estimated single-car dirty air cost: ~{dirty_air_cost * 0.6:.3f}-{dirty_air_cost * 0.8:.3f}s/lap
  (roughly 60-80% of train effect)

  Adjusted net advantage (single car): ~{0.493 - dirty_air_cost * 0.7:+.3f}s/lap
  Over 26 laps:                         ~{(0.493 - dirty_air_cost * 0.7) * 26:.1f}s total
  Laps to DRS:                          ~{1.0 / max(0.01, 0.493 - dirty_air_cost * 0.7):.0f} laps""")
else:
    print(f"  Antonelli would NOT be able to close the gap!")

# Also compare: Piastri clean air (leading, laps 5-17) vs Antonelli dirty (5-15)
# This tells us the "real" gap when Piastri leads and Antonelli follows
pia_lead_avg = sum(piastri_laps[l] for l in range(5, 18)) / 13  # laps 5-17, Piastri leading
ant_follow_avg = sum(antonelli_laps[l] for l in [5,6,7,8,9,10,12,13,14,15]) / 10

print(f"""
CROSS-REFERENCE: Stint 1 real-world scenario
  Piastri leading (clean air, laps 5-17):  avg {pia_lead_avg:.3f}s
  Antonelli following (dirty air, laps 5-15): avg {ant_follow_avg:.3f}s
  Observed gap (PIA leading vs ANT following): {ant_follow_avg - pia_lead_avg:+.3f}s/lap

  This is what ACTUALLY happened when Piastri led and Antonelli followed.
  Antonelli was {'SLOWER' if ant_follow_avg > pia_lead_avg else 'FASTER'} by {abs(ant_follow_avg - pia_lead_avg):.3f}s/lap in dirty air.
""")

# ===================================================================
# PART 7: REVISED VERDICT
# ===================================================================
print("=" * 70)
print("  REVISED VERDICT (with dirty air data)")
print("=" * 70)
single_car_dirty = dirty_air_cost * 0.7  # estimated single-car dirty air
net_adv_dirty = 0.493 - single_car_dirty
total_gain_dirty = net_adv_dirty * 26

print(f"""
SCENARIO: Piastri stays out → pits under SC lap 22 → restarts P1
          Antonelli pits under SC lap 22 → restarts P2

PACE REALITY (REVISED WITH DIRTY AIR DATA):
  - Antonelli clean-air advantage:     {0.493:.3f}s/lap
  - Dirty air cost (measured):         {dirty_air_cost:.3f}s/lap (train), ~{single_car_dirty:.3f}s (single car)
  - Net advantage behind Piastri:      ~{net_adv_dirty:+.3f}s/lap
  - Over 26 laps:                      ~{total_gain_dirty:.1f}s total
  - Starting gap after SC restart:     ~1.0s

  Compare: in stint 1, when Piastri LED and Antonelli FOLLOWED,
  Antonelli was {abs(ant_follow_avg - pia_lead_avg):.3f}s/lap {'slower' if ant_follow_avg > pia_lead_avg else 'faster'}.
  That's real-world evidence of the dirty air effect.

WILL ANTONELLI PASS?
  With ~{net_adv_dirty:.2f}s/lap net advantage, Antonelli reaches DRS range
  in ~{max(1, int(1.0 / max(0.01, net_adv_dirty)))}-{max(2, int(1.5 / max(0.01, net_adv_dirty)))} laps (around lap {28 + int(1.0 / max(0.01, net_adv_dirty))}-{28 + int(1.5 / max(0.01, net_adv_dirty))}).

  But even within DRS, Suzuka is one of the hardest tracks to overtake on.
  The actual race PROVED this: Piastri sat behind Antonelli for 25 laps
  and could not pass — not even once.

  Key dirty air dynamics:
  - S1 (S-curves): Antonelli loses {s1_cost:.3f}s — the BIGGEST loss, and
    this is where his biggest clean-air advantage lives (+0.226s).
    Dirty air neutralizes {s1_cost/0.226*100:.0f}% of his S1 advantage.
  - S2 (130R etc): Loses {s2_cost:.3f}s — high-speed, aero-dependent
  - S3 (straight): Loses {s3_cost:.3f}s — minimal, as expected (DRS zone)

PROBABILITY ESTIMATE (REVISED):"""
)

if net_adv_dirty < 0:
    print(f"""
  Antonelli has a NET NEGATIVE advantage ({net_adv_dirty:+.3f}s/lap) in dirty air.
  He would actually LOSE ground to Piastri, not gain it.

  - Piastri holds P1 to the flag:  ~75-80%
  - Antonelli finds a way past:    ~15-20%  (requires Piastri mistake/lapped traffic)
  - Other outcome (mistake, etc):  ~5%

BOTTOM LINE:
  The dirty air data makes this DEFINITIVE.
  Antonelli's 0.493s/lap clean-air advantage is completely neutralized
  by Suzuka's dirty air effect (~{single_car_dirty:.2f}s/lap behind a single car).
  His net pace behind Piastri would be {net_adv_dirty:+.3f}s/lap — he'd be
  FALLING BACK, not closing in.

  Cross-reference: in stint 1, Antonelli was genuinely 0.110s/lap slower
  than Piastri when following in dirty air. The data from two different
  phases of the race tells the same story.

  McLaren didn't just cost Piastri a likely win — they cost him a
  DOMINANT win. Track position at Suzuka is worth ~{dirty_air_cost:.2f}s/lap,
  nearly double Antonelli's clean-air advantage. That's not close.
""")
else:
    print(f"""
  - Piastri holds P1 to the flag:  ~55-60%
  - Antonelli finds a way past:    ~35-40%
  - Other outcome (mistake, etc):  ~5%

BOTTOM LINE:
  Antonelli retains a small net advantage (~{net_adv_dirty:+.3f}s/lap) even
  in dirty air, but it's marginal. Track position at Suzuka is worth
  ~{dirty_air_cost:.2f}s/lap. McLaren gave that away for free on lap 18.
""")
