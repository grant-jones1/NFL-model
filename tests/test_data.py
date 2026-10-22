import pandas as pd

import nflmodel.data as data
from nflmodel.data import build_games_file, load_games, read_games


def test_load_games_2012_2025():
    games = load_games(2012, 2025)

    assert len(games) == 3829
    assert not games["game_id"].duplicated().any()

    teams = pd.concat([games["home_team"], games["away_team"]]).unique()
    assert len(teams) == 32

    assert set(games["home_win"].unique()) <= {0.0, 0.5, 1.0}
    assert (games["home_win"] == 0.5).sum() == 13
    assert games["home_moneyline"].isna().sum() == 1


def test_build_then_read_round_trip(tmp_path, monkeypatch):
    # Point the module at a temp dir so the real data file isn't touched
    monkeypatch.setattr(data, "DATA_DIR", tmp_path)
    monkeypatch.setattr(data, "GAMES_FILE", tmp_path / "games_clean.parquet")

    build_games_file(2012, 2025)
    saved = read_games()
    expected = load_games(2012, 2025)

    assert len(saved) == len(expected)
    assert list(saved.columns) == list(expected.columns)
