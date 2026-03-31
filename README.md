# F1 Race Strategy Analysis

Race strategy analysis using live data from the [OpenF1 API](https://openf1.org).

## 2026 Japanese GP (Suzuka)

**Hypothetical:** What if Piastri stays out and pits under the Safety Car alongside Antonelli?

### Scripts

| Script | Purpose |
|--------|---------|
| `suzuka26/openf1.py` | OpenF1 API client (no external dependencies) |
| `suzuka26/analysis.py` | Single-race strategy analysis — gap evolution, sector breakdown, dirty air estimate |
| `suzuka26/dirty_air_multirace.py` | Multi-race dirty air calibration using Australia + China + Japan data |

### How to run

```bash
# No dependencies needed — uses Python 3.10+ stdlib only
cd suzuka26

# Run the single-race Suzuka analysis
python analysis.py

# Run the multi-race dirty air calibration (fetches data from 3 races)
python dirty_air_multirace.py
```

Both scripts pull data live from the OpenF1 API on each run. No API key required. Free tier rate limit is 3 requests/second — the client handles this automatically.

### Key findings

- Antonelli has a **+0.49s/lap** clean-air advantage over Piastri post-restart
- Dirty air at Suzuka costs **~0.53s/lap** (weighted across 3 races) for a following car
- Net advantage for Antonelli behind Piastri: **~-0.03s/lap** (effectively neutralized)
- **Piastri holds P1 with ~80% probability** if he stays out and pits under SC
- McLaren's decision to pit Piastri on lap 18 cost them the race
