# 01 · Win-probability calibration (GM)

**Audience:** general manager (hypothetical stakeholder)

**Question:** When our Elo model says a team has an X% chance to win, does it win about X% of the time, and are the model's rest-of-season playoff odds just as trustworthy?

**Scope:** Game-level calibration on the held-out 2022–2025 seasons; playoff-odds calibration on projections made after Week 7 of 2021–2025. Carolina context is frozen at 2026 Week 7 (`THROUGH_WEEK = 7`).

## Files

| File | What it does |
|---|---|
| `wp_calibration_gm.ipynb` | Main notebook: Brier scores (reproduces 03), game-level calibration table with a market comparison, playoff-odds calibration (reproduces 06). Run first. |
| `carolina_outlook_gm.ipynb` | Supporting context: Carolina and NFC South outlook after Week 7 (moved from 06 Sections 6–7). Reads the backtest table written by the main notebook. |
| `definitions.py` | Locked seasons, bins, and settings (match notebooks 03 and 06). |
| `outputs/tables/` | `brier_scores_train_test.csv`, `game_calibration_by_bin_2022_2025.csv`, `elo_vs_market_brier_2022_2025.csv`, `playoff_odds_calibration_thru_wk07.csv`, `backtest_thru_wk07_2021_2025.csv`, `carolina_backtest_thru_wk07.csv`, `nfc_south_projection_thru_wk07.csv` |
| `outputs/figures/` | `2026_thru_wk07_CAR_outlook.png`, `2026_thru_wk07_CAR_point_diff.png` |

Uses `nflmodel.elo`, `nflmodel.evaluate`, and `nflmodel.projections`; nothing from the core model is re-implemented here.
