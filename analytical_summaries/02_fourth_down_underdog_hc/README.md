# 02 · Fourth-down risk for an underdog (Panthers head coach)

**Audience:** Carolina Panthers head coach (hypothetical stakeholder)

**Question:** Given that the Carolina Panthers are projected underdogs in most of their remaining 2026 games, how much fourth-down risk should the head coach take?

**Scope:** Historical evidence from 2018–2025 regular-season play-by-play; Panthers context from the 2026 regular season to date. Remaining 2026 games use our Elo model's projections (labeled as such), not market lines.

## Files

| File | What it does |
|---|---|
| `fourth_down_underdog_analysis.ipynb` | Analyses A–D (Panthers context; where attempts succeed; go vs. kick for underdogs; Panthers' decisions vs. the evidence) and the Results Summary. No charts yet. |
| `definitions.py` | Locked definitions: underdog, spread groups, neutral situation, attempt/kick, zones, distance groups, play types, aggressiveness groups, minimum sample. |
| `outputs/tables/` | One CSV per summary table, prefixed by analysis (`A_`, `B_`, `C_`, `D_`), with counts next to every rate and an "insufficient evidence" flag on groups under 30. |
| `outputs/figures/` | Reserved for visuals. |

Data is pulled live from nflverse with `nflreadpy` each run, so 2026 numbers move as the season goes on; the Context and Results Summary text reflects the run on November 7, 2026. Elo projections use `nflmodel.data.load_games` and `nflmodel.elo` in memory and do not overwrite the core `data/games_clean.parquet`.
