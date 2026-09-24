# NFL-model
A statistical model that rates every NFL team, predicts the full probability distribution for each game's margin of victory, and measures the risk of acting on those predictions. The model is benchmarked against beeing-market lines on held-out seasons and on live 2026 forecasts committed before kickoff. 

**Status:** Phase 1: data exploration and Elo baseline (in progress)

## Approach
1. **Ratings:** Elo ratings for every team since 2012, with home-field advantage and offseason regression estimated from data. 
2. **Margin model:** a regression on rating gaps, EPA efficiency, rest, and QB status that predicts a mean margin and its associated spread. Win and cover probabilites both come from that one distribution. 
3. **Evaluation:** Brier score, log loss, and calibration on 2022-2025, compared against no-vig closing-line probabilites.
4. **Risk**: Kelly-sized paper bankroll, Monte Carlo simulation of season outcomes, and stress tests on estimation error. 

## Roadmap

- [x] Project setup
- [ ] Data exploration (schedules, scores, lines)
- [ ] Elo basleine with win probabilities
- [ ] Margin model with EPA and context features
- [ ] Bnacktest and market comparison
- [ ] Bankroll risk analysis
- [ ] Weekly live forecasts for the 2026 season

## Repository structure

    config/        model settings (YAML)
    src/nflmodel/  source code
    notebooks/     exploration and analysis, one per phase
    forecasts/     weekly predictions, committed before kickoff
    LEARNING_LOG.md  dated notes on decisions and lessons

## Setup

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

## Data

Schedules, scores, betting lines, and play-by-play come from
[nflverse](https://github.com/nflverse) via `nflreadpy`.