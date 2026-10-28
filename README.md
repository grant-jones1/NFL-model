# NFL-model
A statistical model that rates every NFL team, predicts the full probability distribution for each game's margin of victory, and measures the risk of acting on those predictions. The model is benchmarked against betting-market lines on held-out seasons and on live 2026 forecasts committed before kickoff. 

**Status:** Phase 1: data exploration and Elo baseline (in progress)

## Approach
1. **Ratings:** Elo ratings for every team since 2012, with home-field advantage and offseason regression estimated from data. 
2. **Margin model:** a regression on rating gaps, EPA efficiency, rest, and QB status that predicts a mean margin and its associated spread. Win and cover probabilities both come from that one distribution. 
3. **Evaluation:** Brier score, log loss, and calibration on 2022-2025, compared against no-vig closing-line probabilities.
4. **Risk**: Kelly-sized paper bankroll, Monte Carlo simulation of season outcomes, and stress tests on estimation error. 

## Roadmap

- [x] Project setup
- [ ] Data exploration (schedules, scores, lines)
- [ ] Elo baseline with win probabilities
- [ ] Margin model with EPA and context features
- [ ] Backtest and market comparison
- [ ] Bankroll risk analysis
- [ ] Weekly live forecasts for the 2026 season

## Repository structure

    config/        model settings (YAML)
    src/nflmodel/  source code
    notebooks/     exploration and analysis, one per phase
      01_data_exploration.ipynb  how raw nflverse schedules become the clean games table
      02_team_records.ipynb      each team's regular-season record by season
      03_elo_baseline.ipynb      baseline Elo ratings and pre-game win probabilities
      04_ats_carryover.ipynb     whether beating the spread carries over to the next game
      05_forecasts.ipynb         weekly Elo forecasts and grading against final scores
      06_season_projections.ipynb  rest-of-season projections, playoff odds, and backtest
      archive/                   superseded notebooks
    tests/         pytest checks for the data layer
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

## Data

Schedules, scores, betting lines, and play-by-play come from
[nflverse](https://github.com/nflverse) via `nflreadpy`.