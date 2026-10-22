"""
Load and clean NFL schedule data. 
This is the single source of game data for the project. 
"""
from pathlib import Path

import numpy as np
import pandas as pd
import nflreadpy as nfl

FRANCHISE_MAP = {"OAK": "LV", "SD": "LAC", "STL": "LA"}

RAW_COLS = ["game_id", "season", "week", "game_type", "gameday", "gametime",
            "home_team", "away_team", "location", "home_score", "away_score",
            "home_rest", "away_rest", "home_qb_id", "away_qb_id",
            "spread_line", "home_moneyline", "away_moneyline"]

CLEAN_COLS = [
    # identity and timing
    "game_id", "season", "week", "kickoff", "game_type", "is_playoff",
    # teams and venue
    "home_team", "away_team", "location", "is_neutral",
    # outcome
    "home_score", "away_score", "result", "home_win",
    # context
    "home_rest", "away_rest", "home_qb_id", "away_qb_id",
    # market
    "spread_line", "home_moneyline", "away_moneyline",
]

def load_games(first_season, last_season):
    """
    One row per game, sorted by kickoff
    
    first_season: first season to load (inclusive)
    last_season: last season to load (inclusive)
    """
    # 1. Pull the data
    seasons = list(range(first_season, last_season + 1))
    raw = nfl.load_schedules(seasons).to_pandas()
    games = raw[RAW_COLS].copy()

    #2. Franchise mapping
    games["home_team"] = games["home_team"].replace(FRANCHISE_MAP)
    games["away_team"] = games["away_team"].replace(FRANCHISE_MAP)

    # 3. Kickoff and flags
    games["kickoff"] = pd.to_datetime(games["gameday"] + " " + games["gametime"])
    games["is_playoff"] = games["game_type"] != "REG"
    games["is_neutral"] = games["location"] == "Neutral"

    # 4. Outcomes (unplayed games stay NaN)
    games["result"] = games["home_score"] - games["away_score"]
    conditions = [games["result"] > 0, games["result"] == 0, games["result"] < 0]
    choices = [1.0, 0.5, 0.0]
    games["home_win"] = np.select(conditions, choices, default=np.nan)

    # 5. Scores as nullable integers (unplayed games stay missing)
    score_cols = ["home_score", "away_score", "result"]
    games[score_cols] = games[score_cols].astype("Int64")

    # 6. Final columns and order
    games = (games[CLEAN_COLS]
             .sort_values(["kickoff", "game_id"])
             .reset_index(drop=True))

    return games


# Repo root is two folders up from this file: src/nflmodel/data.py
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
GAMES_FILE = DATA_DIR / "games_clean.parquet"


def build_games_file(first_season, last_season):
    """
    Download, clean, and save the games table. Rerun to refresh.

    first_season: first season to include (inclusive)
    last_season:  last season to include (inclusive)
    """
    games = load_games(first_season, last_season)
    DATA_DIR.mkdir(exist_ok=True)
    games.to_parquet(GAMES_FILE, index=False)
    print(f"Saved {len(games)} games ({first_season}-{last_season}) to {GAMES_FILE}")
    return games


def read_games():
    """Load the saved games table. Run build_games_file first."""
    games = pd.read_parquet(GAMES_FILE)
    return games
