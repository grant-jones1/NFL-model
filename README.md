# NFL-model
A statistical model that rates every NFL team, turns those ratings into game and season probabilities, and checks those probabilities honestly: against held-out seasons, against the betting market, and against live 2026 forecasts committed before kickoff.

The repository has two parts:

1. **The core model** (`src/nflmodel/`, `notebooks/`, `forecasts/`) builds and validates the predictions.
2. **Analytical summaries** (`analytical_summaries/`) use the model and nflverse data to answer one decision-focused question each, for a specific (hypothetical) football stakeholder.

**Status:** Elo baseline built, tuned, and validated; weekly 2026 forecasts and season projections running. Margin model and bankroll risk analysis are next.

## The core model

**What it predicts.** For every game: each team's win probability and an expected point spread. For every team: a projected final record, an 80% range of outcomes, and division and playoff odds for the rest of the season.

**How.**
1. **Ratings:** Elo ratings for every team since 2005, updated game by game with a margin-of-victory multiplier and regressed toward the league average each offseason. Home-field advantage, update size (K), and offseason regression were tuned on 2013–2021 (current values: K=21, HFA=42 Elo points, regression 0.4).
2. **Game probabilities and spreads:** the Elo gap (plus home field) converts to a win probability with the standard logistic curve and to a spread at 25 Elo points per point.
3. **Season projections:** each remaining game is simulated 10,000 times from current ratings; playoff odds use 4 division winners and 3 wild cards per conference.

**How it's validated.**
- **Held-out seasons:** parameters were tuned on 2013–2021 and scored on 2022–2025, which the tuning never saw. Brier score is 0.2188 in training and 0.2212 out of sample (11.5% better than a coin flip). On the same 2022–2025 games the no-vig betting market scores 0.2095, so the market is still the benchmark to beat.
- **Calibration:** out-of-sample win probabilities grouped into 10-point bins and compared with actual win rates (see `analytical_summaries/01_wp_calibration_gm/`).
- **Season projections:** a backtest from Week 7 of 2021–2025 misses final win totals by 1.96 wins (RMSE), against 2.51 for carrying the current win pace forward.
- **Live forecasts:** each 2026 week's forecast is saved to `forecasts/` before kickoff and graded afterward against final scores and the Vegas line.

### Roadmap

- [x] Project setup
- [x] Data exploration (schedules, scores, lines)
- [x] Elo baseline with win probabilities, tuned and validated on held-out seasons
- [x] Weekly live forecasts and rest-of-season projections for 2026 (ongoing)
- [ ] Margin model with EPA and context features (rating gaps, rest, QB status)
- [ ] Backtest and market comparison for the margin model (Brier, log loss, calibration vs. no-vig closing lines)
- [ ] Bankroll risk analysis (Kelly-sized paper bankroll, Monte Carlo, stress tests on estimation error)

## Analytical summaries

The summaries are where I practice turning technical modeling into clear, decision-ready recommendations for people who don't work with models. Each one starts from a stakeholder's real decision, frames a single question, states its assumptions and scope up front, and reports results and risk honestly: sample sizes, uncertainty, and what the evidence can't say. Each summary imports the core model (for example, Elo ratings and projections) rather than re-implementing it, and keeps its own locked definitions so the numbers can be reproduced.

| # | Audience | Question |
|---|---|---|
| 01 | General manager | Can the model's win probabilities and playoff odds be trusted? |
| 02 | Carolina Panthers head coach | As a projected underdog in most remaining 2026 games, how much fourth-down risk should the team take? |

See [analytical_summaries/README.md](analytical_summaries/README.md) for the format every summary follows.

## Repository structure

    config/        model settings (YAML)
    src/nflmodel/  core model code
      data.py         load and clean schedules into the games table
      elo.py          Elo math, engine, and reshaping helpers (DEFAULT_PARAMS)
      evaluate.py     pick accuracy and Brier scores
      projections.py  rest-of-season simulation (project_season, team_wins)
    notebooks/     core model work, one per phase
      01_data_exploration.ipynb    how raw nflverse schedules become the clean games table
      02_team_records.ipynb        each team's regular-season record by season
      03_elo_baseline.ipynb        baseline Elo ratings, tuning, and Brier scores
      04_ats_carryover.ipynb       whether beating the spread carries over to the next game
      05_forecasts.ipynb           weekly Elo forecasts and grading against final scores
      06_season_projections.ipynb  rest-of-season projections, playoff odds, and backtest
      archive/                     superseded notebooks
    analytical_summaries/  stakeholder-facing summaries built on the core model
      01_wp_calibration_gm/          win-probability calibration (GM)
      02_fourth_down_underdog_hc/    fourth-down risk for an underdog (Panthers HC)
    tests/         pytest checks for the data layer and Elo
    data/          generated games table (not committed)
    forecasts/     weekly predictions, committed before kickoff
    notes/         notes on technical material (probability, Elo, etc.)
    LEARNING_LOG.md  dated notes on decisions and lessons

## How to run

    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    pip install -e .
    python -c "from nflmodel.data import build_games_file; build_games_file(2005, 2026)"

`pip install -r requirements.txt` installs the dependencies (pandas, nflreadpy, etc.),
since `pyproject.toml` doesn't list them. Notebooks load the games table with
`nflmodel.data.read_games()` and run on the "NFL-model (.venv)" Jupyter kernel.
Summary notebooks run from their own folder (they import their local `definitions.py`).

## Data

Schedules, scores, betting lines, rosters, and play-by-play come from
[nflverse](https://github.com/nflverse) via `nflreadpy`.
