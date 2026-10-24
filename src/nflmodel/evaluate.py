"""
Scoring Elo predictions: pick accuracy and Brier scores.
"""


def check_rate(elo):
    """
    Adds a 'correct' column: True when the Elo favorite won.

    elo: DataFrame from run_elo
    """
    played = elo[(elo["result"] != 0) & elo["result"].notna()].copy()

    home_fav = played["home_prob"] > 0.5      # True where Elo picked the home team
    home_won = played["result"] > 0           # True where the home team won

    played["correct"] = home_fav == home_won
    return played


def brier_score(df):
    """
    Average squared error of the home-win probabilites.

    df: DataFrame with home_prob and home_win columns
    """
    played = df[df["home_win"].notna()]
    sq_err = (played["home_prob"] - played["home_win"]) ** 2
    brier = sq_err.mean()
    return brier


def brier_baselines(df):
    """
    Brier scores of two naive forecasters on the same games.

    df: DataFrame with home_win column
    """
    played = df[df["home_win"].notna()]
    o_bar = played["home_win"].mean()
    coin_flip = 0.25
    home_rate = o_bar * (1 - o_bar)
    baselines = {"coin_flip": coin_flip, "home_rate": home_rate}
    return baselines
