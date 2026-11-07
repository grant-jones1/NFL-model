"""
Rest-of-season projections: simulate remaining games from frozen Elo ratings.
Moved from notebooks/06_season_projections.ipynb (Section 2) so other notebooks can import it.
"""
import numpy as np
import pandas as pd

from nflmodel.elo import elo_diff, home_win_prob

WILD_CARDS = 3                       # per conference

DIVISIONS = {
    "AFC East":  ["BUF", "MIA", "NE", "NYJ"],
    "AFC North": ["BAL", "CIN", "CLE", "PIT"],
    "AFC South": ["HOU", "IND", "JAX", "TEN"],
    "AFC West":  ["DEN", "KC", "LAC", "LV"],
    "NFC East":  ["DAL", "NYG", "PHI", "WAS"],
    "NFC North": ["CHI", "DET", "GB", "MIN"],
    "NFC South": ["ATL", "CAR", "NO", "TB"],
    "NFC West":  ["ARI", "LA", "SEA", "SF"],
}
TEAMS = [t for teams in DIVISIONS.values() for t in teams]
COL = {team: i for i, team in enumerate(TEAMS)}   # team -> column in the simulation arrays
DIVISION_OF = {t: d for d, teams in DIVISIONS.items() for t in teams}


def team_wins(g):
    """
    Wins and games played per team (ties count as half a win).

    g: games DataFrame of played games
    """
    home = g[["home_team", "home_win"]].set_axis(["team", "win"], axis=1)
    away = g[["away_team", "home_win"]].set_axis(["team", "win"], axis=1)
    away["win"] = 1 - away["win"]
    record = pd.concat([home, away]).groupby("team")["win"].agg(["sum", "count"])
    return record.reindex(TEAMS, fill_value=0)


def project_season(games, history, season, through_week, params, n_sims, seed=0, shift=None):
    """
    Simulate the rest of a regular season from Elo ratings frozen after through_week.

    games:        games DataFrame (from read_games)
    history:      team_history(run_elo(games, params))
    season:       season to project
    through_week: last week counted as played
    params:       Elo parameter dictionary
    n_sims:       number of simulated seasons
    shift:        optional {team: Elo points} added to ratings, for what-if scenarios

    Returns (table, wins, playoff): one row per team, plus each simulation's final wins
    and playoff flags (n_sims x teams)
    """
    rng = np.random.default_rng(seed)
    reg = games[(games["season"] == season) & (games["game_type"] == "REG")]
    played = reg[reg["week"] <= through_week]
    left = reg[reg["week"] > through_week]

    # 1. Ratings after through_week, frozen for the rest of the season
    h = history[(history["season"] == season) & (history["week"] <= through_week)]
    ratings = h.sort_values("kickoff").groupby("team")["elo_post"].last()
    for t, pts in (shift or {}).items():
        ratings[t] += pts

    # 2. Win probability for every remaining game
    hfa = np.where(left["is_neutral"], params["neutral_hfa"], params["hfa"])
    d = elo_diff(ratings[left["home_team"]].values, ratings[left["away_team"]].values, hfa)
    p_home = home_win_prob(d, params["scale"])

    # 3. Simulate: one row per season, one column per game
    home_won = rng.random((n_sims, len(left))) < p_home

    # 4. Add simulated wins to current wins (one-hot maps each game to its two teams)
    home_onehot = np.zeros((len(left), len(TEAMS)))
    away_onehot = np.zeros((len(left), len(TEAMS)))
    home_onehot[np.arange(len(left)), left["home_team"].map(COL)] = 1
    away_onehot[np.arange(len(left)), left["away_team"].map(COL)] = 1
    record = team_wins(played)
    wins = record["sum"].values + home_won @ home_onehot + ~home_won @ away_onehot

    # 5. Playoffs: best record in each division, then the 3 best of the rest per conference
    score = wins + rng.random(wins.shape) * 0.1   # random tiebreak
    sim = np.arange(n_sims)
    div_win = np.zeros(wins.shape, dtype=bool)
    for teams in DIVISIONS.values():
        idx = np.array([COL[t] for t in teams])
        div_win[sim, idx[score[:, idx].argmax(axis=1)]] = True

    playoff = div_win.copy()
    for conf in ["AFC", "NFC"]:
        idx = np.array([COL[t] for d, teams in DIVISIONS.items() if d.startswith(conf) for t in teams])
        wc_score = np.where(div_win[:, idx], -np.inf, score[:, idx])
        best = np.argsort(-wc_score, axis=1)[:, :WILD_CARDS]
        playoff[sim[:, None], idx[best]] = True

    table = pd.DataFrame({
        "division": [DIVISION_OF[t] for t in TEAMS],
        "elo": ratings[TEAMS].values,
        "wins": record["sum"].values,
        "losses": record["count"].values - record["sum"].values,
        "proj_wins": wins.mean(axis=0),
        "low": np.percentile(wins, 10, axis=0),    # 80% range
        "high": np.percentile(wins, 90, axis=0),
        "division_pct": div_win.mean(axis=0),
        "playoff_pct": playoff.mean(axis=0),
    }, index=pd.Index(TEAMS, name="team"))
    return table, wins, playoff
