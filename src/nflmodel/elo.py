"""
Elo ratings for NFL teams: the math, the game-by-game engine, and reshaping helpers.
"""
import numpy as np
import pandas as pd

# Current model parameters.
# Tuned values (03_elo_baseline Section 6): k=20, hfa=40, season_regression=0.4
# Original untuned values:                  k=20, hfa=48, season_regression=1/3
DEFAULT_PARAMS = {
    "base": 1500,
    "scale": 400,
    "k": 20,
    "hfa": 48,
    "season_regression": 1/3,
    "use_mov": True,
    "mov_scale": 2.2,
    "mov_slope": 0.001,
    "neutral_hfa": 0,
    "include_playoffs": True,
    "spread_divisor": 25
}


# =============================
# Elo math
# =============================

def elo_diff(rating_home, rating_away, hfa):
    """
    Home team's Elo advantage, including home field

    rating_home: home team's Elo rating before the game
    rating_away: away team's Elo rating before the game
    hfa:         home-field advantage in Elo points (0 at neutral sites)
    """
    d = rating_home - rating_away + hfa
    return d

def home_win_prob(d, scale):
    """
    Probability the home team wins

    d:      home team's Elo advantage, from elo_diff
    scale:  Elo points that make 10-to-1 odds (400 by convention)
    """
    home_prob = 1 / (1 + 10 ** (-d / scale))
    return home_prob

def predicted_spread(d, spread_divisor):
    """
    Expected home margin in points

    d:              home team's Elo advantage, from elo_diff
    spread_divisor: Elo points per point of spread (25 convention)
    """
    spread = d / spread_divisor
    return spread

def mov_multiplier(margin, d_winner, use_mov, mov_scale, mov_slope):
    """
    Scales the rating update by margin of victory

    margin:         home score minus away score
    d_winner:       winner's Elo advantage(d if home won, -d if away won)
    use_mov:        True to apply the multiplier, False to return 1
    mov_scale:      constant that sets the size of the favorite correction (2.2 convention)
    mov_slope:      how strongly the winner's Elo advantage shrinks the multiplier (0.001 convention)
    """
    if margin == 0:
        return 1.0
    if not use_mov:
        return 1.0
    multiplier = np.log(abs(margin) + 1) * mov_scale / (mov_slope * d_winner + mov_scale)
    return multiplier

def rating_change(k, multiplier, outcome, expected):
    """
    Elo points the home team gains (away team loses the same amount)

    k:          base update size (20 convention)
    multiplier: margin of victory scaling, from mov_multiplier
    outcome:    home result (1 win, 0.5 tie, 0 loss)
    expected:   home win probability, from home_win_prob
    """
    change = k * multiplier * (outcome - expected)
    return change

def regress_ratings(ratings, frac, base):
    """
    Pull every rating part of the way back toward base

    ratings:    dictionary of team's Elo ratings {team: elo rating}
    frac:       fraction of the gap to close (1/3 convention)
    base:       league-average rating to pull toward (1500 convention)
    """
    new_ratings = {team: r + frac * (base - r) for team, r in ratings.items()}
    return new_ratings


# =============================
# Elo engine
# =============================

def run_elo(games, params):
    """
    Run Elo through every game in kickoff order.

    games:  games DataFrame from Section 1, sorted by kickoff and game_id
    params: model parameter dictionary from Section 0

    Returns games with added columns:
    elo_home_pre, elo_away_pre, home_prob, elo_home_post, elo_away_post
    """

    # Drop playoff games if params states this
    if not params["include_playoffs"]:
        games = games[~games["is_playoff"]]

    ratings = {}                # team -> current Elo, the engine's memory
    current_season = None       # tracks when a new season starts
    results = []                # one dict per game, turned into columns at the end

    for g in games.itertuples(index=False):

        # 1. New season -> regress (skip for the first season as all teams start at 1500)
        if g.season != current_season:
            if current_season is not None:
                ratings = regress_ratings(ratings, params["season_regression"], params["base"])
            current_season = g.season

        # 2. Look up pre-game ratings (new teams start at base)
        r_home = ratings.get(g.home_team, params["base"])
        r_away = ratings.get(g.away_team, params["base"])

        # 3. Prediction
        hfa = params["neutral_hfa"] if g.is_neutral else params["hfa"]
        d = elo_diff(r_home, r_away, hfa)
        p_home = home_win_prob(d, params["scale"])

        # 4. Update only if game has been played
        r_home_post = r_home
        r_away_post = r_away
        if not pd.isna(g.home_win):
            d_winner = d if g.home_win >= 0.5 else -d
            mult = mov_multiplier(g.result, d_winner, params["use_mov"], params["mov_scale"], params["mov_slope"])
            change = rating_change(params["k"], mult, g.home_win, p_home)
            r_home_post = r_home + change
            r_away_post = r_away - change
            ratings[g.home_team] = r_home_post
            ratings[g.away_team] = r_away_post

        # 5. Save this game's numbers
        results.append({
            "elo_home_pre": r_home,
            "elo_away_pre": r_away,
            "home_prob": p_home,
            "elo_home_post": r_home_post,
            "elo_away_post": r_away_post,
                        })
    out = pd.concat([games.reset_index(drop=True), pd.DataFrame(results)], axis=1)
    return out


# =============================
# Reshape
# =============================

def team_history(elo):
    """
    One row per team per game.

    elo: DataFrame returned by run_elo

    Returns columns: season, week, kickoff, team, opponent, elo_pre, elo_post
    """
    home = elo[["season", "week", "kickoff", "home_team", "away_team",
                "elo_home_pre", "elo_home_post"]].copy()
    home.columns = ["season", "week", "kickoff", "team", "opponent", "elo_pre", "elo_post"]

    away = elo[["season", "week", "kickoff", "away_team", "home_team",
                "elo_away_pre", "elo_away_post"]].copy()
    away.columns = ["season", "week", "kickoff", "team", "opponent", "elo_pre", "elo_post"]

    history = pd.concat([home, away]).sort_values(["team", "kickoff"]).reset_index(drop=True)
    return history


def ratings_table(history, value):
    """
    Wide table: rows are (season, week), columns are teams.

    history: DataFrame from team_history
    value:   "elo_pre" or "elo_post"
    """
    table = history.pivot(index = ["season", "week"], columns = "team", values = value)
    table = table.ffill()
    return table
