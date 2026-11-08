"""
Locked definitions for Summary 02: fourth-down risk for an underdog (Carolina Panthers head coach).

Every rule used to label a play or a game lives here, so the notebook and any later visuals
use exactly the same definitions. Change a rule here, not in the notebook.
"""
import numpy as np
import pandas as pd

# =============================
# As of (frozen results)
# =============================
# Game results and Elo ratings: games final when the data was pulled on November 8, 2026
# (Weeks 1-8 plus 9 of the 15 Week 9 games, including Carolina's loss to Denver).
# Fourth-down play-by-play through Week 8 (Week 9 play-by-play was not yet published).
# The first run saves the raw pulls to data/ (not committed); later runs read them instead of re-pulling.
AS_OF_DATE = "2026-11-08"
RESULTS_THROUGH_WEEK = 9
PBP_THROUGH_WEEK = 8
SNAPSHOT_DIR = "data"

# =============================
# Scope
# =============================
HIST_SEASONS = list(range(2018, 2026))   # historical evidence: 2018-2025 regular seasons
CURRENT_SEASON = 2026                    # Panthers context: 2026 regular season to date
TEAM = "CAR"
MIN_SAMPLE = 30                          # groups below this are flagged; no conclusions drawn

# =============================
# Underdog / favorite (pregame)
# =============================
# Historical and played 2026 games: market win probability from the moneylines, vig removed.
# Remaining 2026 games: Elo-projected win probability from our model.
# A team is an underdog when its win probability is below 50%.
#
# Sign convention: nflverse spread_line is the HOME team's expected margin
# (positive = home favored). Team line = spread_line for the home team, -spread_line for away.
# Positive team line = favorite by that many points.
#
# Edge cases dropped from underdog/favorite comparisons: market probability exactly 50%,
# or moneyline favorite disagrees with the spread favorite.


def implied_prob(moneyline):
    """Implied win probability from an American moneyline (still includes the vig)."""
    ml = np.asarray(moneyline, dtype=float)
    favorite = ml < 0
    prob = 100 / (np.abs(ml) + 100)                      # underdog (or even) price
    prob[favorite] = -ml[favorite] / (-ml[favorite] + 100)
    return prob


def no_vig_home_prob(home_moneyline, away_moneyline):
    """Home win probability with the vig removed (both implied probabilities rescaled to sum to 1)."""
    home, away = implied_prob(home_moneyline), implied_prob(away_moneyline)
    return home / (home + away)


def spread_group(team_line):
    """
    Spread group from the team's line (positive = favored by that many points).

    Small: 1 to 3 points, Moderate: 3.5 to 7, Large: 7.5 or more, for underdogs and favorites alike.
    Market lines are already in half points. Elo-projected lines are rounded to the nearest
    half point first; anything under 1 point after rounding is labeled "Pick'em (<1)"
    (no historical game falls there).
    """
    labels = []
    for x in np.asarray(team_line, dtype=float):
        line = np.sign(x) * np.floor(abs(x) * 2 + 0.5) / 2   # nearest half point, ties away from 0
        size = abs(line)
        side = "Favorite" if line > 0 else "Underdog"
        if np.isnan(line):
            labels.append(None)
        elif size < 1:
            labels.append("Pick'em (<1)")
        elif size <= 3:
            labels.append(f"{side} small (1-3)")
        elif size <= 7:
            labels.append(f"{side} moderate (3.5-7)")
        else:
            labels.append(f"{side} large (7.5+)")
    return labels


SPREAD_GROUP_ORDER = ["Underdog large (7.5+)", "Underdog moderate (3.5-7)", "Underdog small (1-3)",
                      "Favorite small (1-3)", "Favorite moderate (3.5-7)", "Favorite large (7.5+)"]

# =============================
# Neutral situation
# =============================
NEUTRAL_QUARTERS = [1, 2, 3]
NEUTRAL_MAX_SCORE_DIFF = 8
NEUTRAL_WP_COL = "vegas_wp"          # nflverse win probability that includes the pregame spread
NEUTRAL_WP_RANGE = (0.10, 0.90)


def is_neutral(plays):
    """True for plays in quarters 1-3, score within 8, and vegas_wp between 10% and 90%."""
    lo, hi = NEUTRAL_WP_RANGE
    return (plays["qtr"].isin(NEUTRAL_QUARTERS)
            & (plays["score_differential"].abs() <= NEUTRAL_MAX_SCORE_DIFF)
            & plays[NEUTRAL_WP_COL].between(lo, hi))

# =============================
# Fourth-down decision
# =============================
# "Went for it": run or pass on 4th down. Kneels and spikes are excluded, and plays nullified
# by penalty are excluded automatically (nflverse labels them play_type "no_play").
# Fake punts / fake field goals (run or pass from punt or field-goal formation) count as attempts.
# Aborted snaps from punt or field-goal formation are dropped from both groups (botched kicks,
# not decisions). Aborted snaps on regular offensive plays still count as attempts.
# "Kicked": punt or field-goal attempt.
# "Converted": nflverse fourth_down_converted == 1 (first down or offensive touchdown).


def decision(plays):
    """
    Label each 4th-down play "go", "kick", or None (not a decision we count).

    Also returns the fake and aborted-kick flags so the notebook can report their counts.
    """
    run_pass = plays["play_type"].isin(["run", "pass"])
    kneel_spike = (plays["qb_kneel"] == 1) | (plays["qb_spike"] == 1)
    kick_formation = plays["desc"].str.contains("punt formation|field goal formation", case=False, na=False)
    aborted_kick = run_pass & kick_formation & (plays["aborted_play"] == 1)
    fake = run_pass & kick_formation & ~aborted_kick

    # A counted attempt must have a result; a few run/pass rows with an accepted offensive
    # penalty (down replayed) have neither flag set, so they are nullified plays.
    has_result = (plays["fourth_down_converted"] == 1) | (plays["fourth_down_failed"] == 1)
    go = run_pass & ~kneel_spike & ~aborted_kick & has_result
    kick = plays["play_type"].isin(["punt", "field_goal"])
    label = pd.Series(np.select([go, kick], ["go", "kick"], ""), index=plays.index).replace("", None)
    return label, fake, aborted_kick

# =============================
# Field position and distance
# =============================
# Yards from the opponent's end zone (nflverse yardline_100). Fourth downs inside our own 20
# (yardline_100 > 80) are excluded.
ZONE_BINS = [0, 5, 20, 40, 60, 80]
ZONE_LABELS = ["Goal line (1-5)", "Red zone (6-20)", "Opponent 40-21 (21-40)",
               "Midfield (41-60)", "Own 20-40 (61-80)"]

DISTANCE_BINS = [0, 1, 3, 6, np.inf]
DISTANCE_LABELS = ["1", "2-3", "4-6", "7+"]


def field_zone(yardline_100):
    """Field-position zone; NaN for plays inside our own 20."""
    return pd.cut(yardline_100, ZONE_BINS, labels=ZONE_LABELS)


def distance_group(ydstogo):
    """Yards-to-go group: 1, 2-3, 4-6, 7+."""
    return pd.cut(ydstogo, DISTANCE_BINS, labels=DISTANCE_LABELS)

# =============================
# Play type on attempts
# =============================
# QB sneak: designed QB run (not a scramble) with 2 or fewer yards to go; QBs identified by
# season roster position. Other run: every other run. Pass: every pass play (incl. sacks, scrambles).
SNEAK_MAX_YDSTOGO = 2


def attempt_play_type(plays, qb_ids):
    """
    "QB sneak", "Other run", or "Pass" for each attempt.

    qb_ids: set of (season, gsis_id) pairs for players listed at QB on that season's roster
    """
    rusher_is_qb = pd.Series([(s, r) in qb_ids for s, r in zip(plays["season"], plays["rusher_player_id"])],
                             index=plays.index)
    designed_run = (plays["play_type"] == "run") & (plays["qb_scramble"] != 1)
    sneak = designed_run & rusher_is_qb & (plays["ydstogo"] <= SNEAK_MAX_YDSTOGO)
    return pd.Series(np.select([sneak, plays["play_type"] == "run"], ["QB sneak", "Other run"], "Pass"),
                     index=plays.index)

# =============================
# Team-game aggressiveness (Analysis C)
# =============================
# Per team-game: neutral-situation go rate on 4th and 1-3 outside own territory
# (yardline_100 <= 50). Only team-games with at least 2 qualifying plays count.
# Groups: Low = 0% go rate, Medium = above 0% and below 100%, High = 100%.
AGGR_MAX_YDSTOGO = 3
AGGR_MAX_YARDLINE = 50
AGGR_MIN_PLAYS = 2


def aggression_group(go_rate):
    """Low (0%), Medium (between), High (100%)."""
    return pd.Series(np.select([go_rate == 0, go_rate == 1], ["Low (0%)", "High (100%)"], "Medium (1-99%)"),
                     index=go_rate.index)


AGGR_ORDER = ["Low (0%)", "Medium (1-99%)", "High (100%)"]

# =============================
# Decision categories (Figure 1, sideline card, Analysis D)
# =============================
# From a cell's go-minus-kick difference in win-probability percentage points
# (0.010 vegas_wpa = 1.0 point):
#   GO FOR IT        +1.0 or more
#   CLOSE CALL       between -1.0 and +1.0
#   KICK             -1.0 or lower
#   NOT ENOUGH DATA  fewer than 30 go or 30 kick plays, OR going for it was under 10% of
#                    the cell's decisions (go + kick).
#
# Why the 10% rule: in spots where teams almost always kick, the few that went for it are a
# self-selected group (a mismatch they spotted, a fake, a desperate script). Their results say
# more about why they chose to go than about what going for it does, so even 30+ such plays are
# not treated as evidence. The difference is rounded to 0.1 before comparing with the thresholds,
# so a cell's category always matches the number printed on the chart.
DECISION_THRESHOLD_PTS = 1.0
MIN_GO_SHARE = 0.10
DECISION_ORDER = ["GO FOR IT", "CLOSE CALL", "KICK", "NOT ENOUGH DATA"]


def decision_category(diff_pts, go_plays, kick_plays):
    """GO FOR IT / CLOSE CALL / KICK / NOT ENOUGH DATA for one cell (see rules above)."""
    if go_plays < MIN_SAMPLE or kick_plays < MIN_SAMPLE:
        return "NOT ENOUGH DATA"
    if go_plays / (go_plays + kick_plays) < MIN_GO_SHARE:
        return "NOT ENOUGH DATA"
    d = round(diff_pts, 1)
    if d >= DECISION_THRESHOLD_PTS:
        return "GO FOR IT"
    if d <= -DECISION_THRESHOLD_PTS:
        return "KICK"
    return "CLOSE CALL"

# =============================
# Expected-points (EP) decision model (Section E, Figure 1, sideline card)
# =============================
# Value of each fourth-down option in expected points for the offense, from 2018-2025
# regular-season play-by-play. League-average kicking and punting; no adjustment for score
# or time (the chart applies to neutral situations).
#
# EP of a field position: average nflfastR `ep` on 1st-and-10 run/pass plays at each
#   yardline_100 (1st-and-goal inside the 10), smoothed with a centered rolling mean.
# Go:   p(convert) x EP(1st down at the line to gain) + (1 - p) x (-EP of opponent's 1st down
#       at the spot). A conversion that reaches the goal line is a touchdown, valued like a made
#       field goal: TD_POINTS - EP of the opponent after the kickoff.
#       p(convert) = logistic fit of league conversion rate on log(yards to go) (always falls with distance), all
#       situations, fourth-down attempts as defined above (kneels and spikes excluded).
# Punt: -EP of the opponent's 1st down after the league-average net punt from that spot, from a
#       smooth quadratic fit of net punt on yard line (touchbacks included). Only from the opponent's
#       35 or farther back.
# Field goal: distance = yardline_100 + 18 (how nflverse records kicks). Make rate from a logistic fit on distance.
#       make x (3 - EP of opponent after the average 2024-2025 post-kickoff start, current kickoff rules)
#       + miss x (-EP of opponent's 1st down at the spot of the kick, or their 20 if farther back).
#       Only 63 yards or shorter.
# Decision: the option with the highest EP; if it beats the second-best by less than the
# margin, the square reads COACH'S CALL.
EP_SMOOTH_WINDOW = 5                 # yard lines in the centered rolling mean
LONG_YDSTOGO = 11                    # chart row "11+" (evaluated at the median yards to go of 11+ decisions)
TD_POINTS = 7
FG_POINTS = 3
PUNT_FIT_DEGREE = 2                  # quadratic fit of net punt on yard line
PUNT_MIN_YARDLINE = 35               # punts allowed only from the opponent's 35 or farther back
FG_DISTANCE_OFFSET = 18              # kick distance = yardline_100 + 18 (nflverse convention)
FG_MAX_DISTANCE = 63                 # longest field goal allowed
FG_SPOT_BEHIND_LOS = 7               # spot of the kick, yards behind the line of scrimmage
FG_MISS_MIN_SPOT = 80                # opponent gets the ball at least at their own 20 (yardline_100 80)
KICKOFF_SEASONS = [2024, 2025]       # post-kickoff start under the current kickoff rules
DECISION_MARGIN = 0.2                # expected points; closer than this -> COACH'S CALL
MARGIN_SENSITIVITY = [0.1, 0.3]

# Chart layout: columns = field position (yardline_100) in 5-yard steps from our own 20 to the
# opponent's 1; rows = yards to go 1-10 and 11+.
CHART_YARDLINES = [80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10, 5, 1]
CHART_YDSTOGO = list(range(1, LONG_YDSTOGO + 1))   # 11 means "11+"
CHART_DECISIONS = ["GO", "PUNT", "FIELD GOAL", "COACH'S CALL"]


def yardline_label(yardline_100):
    """'Own 20' ... '50' ... 'Opp 1' for a yardline_100 value."""
    if yardline_100 > 50:
        return f"Own {100 - yardline_100:.0f}"
    if yardline_100 == 50:
        return "50"
    return f"Opp {yardline_100:.0f}"
