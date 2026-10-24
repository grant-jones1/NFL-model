import pytest

from nflmodel.data import read_games
from nflmodel.elo import (DEFAULT_PARAMS, home_win_prob, regress_ratings,
                          run_elo, team_history)


@pytest.fixture(scope="module")
def elo():
    games = read_games()
    games = games[games["season"].between(2005, 2025)].reset_index(drop=True)
    return run_elo(games, DEFAULT_PARAMS)


def test_even_matchup_is_coin_flip():
    assert home_win_prob(0, 400) == 0.5


def test_regress_ratings():
    out = regress_ratings({"A": 1600, "B": 1400}, 1/3, 1500)
    assert out == pytest.approx({"A": 1566.67, "B": 1433.33}, abs=0.01)


def test_updates_are_zero_sum(elo):
    home_change = elo["elo_home_post"] - elo["elo_home_pre"]
    away_change = elo["elo_away_post"] - elo["elo_away_pre"]
    assert (home_change + away_change).abs().max() < 1e-9


def test_season_start_league_mean_is_base(elo):
    # Each team's first game of the season, not literally week 1: in 2017
    # MIA@TB moved out of week 1 (Hurricane Irma), so only 30 teams played.
    history = team_history(elo)
    first = history.groupby(["season", "team"]).head(1)
    season_start = first.groupby("season")["elo_pre"].mean()
    assert season_start.to_numpy() == pytest.approx(DEFAULT_PARAMS["base"])
