"""
Locked definitions for Summary 01: win-probability calibration for the general manager.

Every season range and setting below matches the core notebook it comes from, so the
numbers here reproduce the core model's evidence instead of recomputing it differently.
"""

# --- Elo evaluation (matches notebooks/03_elo_baseline.ipynb, Section 0) ---
FIRST_SEASON = 2005              # Elo burn-in starts here
LAST_SEASON = 2025               # last completed season
TRAIN_SEASONS = range(2013, 2022)  # seasons the Elo parameters were tuned on
TEST_SEASONS = range(2022, 2026)   # held-out seasons: the out-of-sample check

# --- Game-level calibration table (new in this summary) ---
# 10-point bins of predicted home win probability; the last bin includes 100%
PROB_BINS = [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0]
PROB_LABELS = ["0-10%", "10-20%", "20-30%", "30-40%", "40-50%",
               "50-60%", "60-70%", "70-80%", "80-90%", "90-100%"]

# --- Playoff-odds calibration and Carolina outlook (matches notebooks/06_season_projections.ipynb) ---
SEASON = 2026
THROUGH_WEEK = 7                 # frozen at Week 7 so the GM write-up stays reproducible
BACKTEST_SEASONS = range(2021, 2026)  # 5 prior seasons, all 17-game schedules
N_SIMS = 10_000
FOCUS_TEAM = "CAR"
PLAYOFF_ODDS_BINS = [-0.01, 0.1, 0.5, 0.9, 1.0]
PLAYOFF_ODDS_LABELS = ["Under 10%", "10-50%", "50-90%", "Over 90%"]
