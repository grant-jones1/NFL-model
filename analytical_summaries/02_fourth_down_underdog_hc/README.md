# 02 · Fourth-down risk for an underdog (Panthers head coach)

**Purpose:** Answer the head coach's question: with Carolina projected as the underdog in most remaining 2026 games, how much fourth-down risk should he take? The written answer is in [ANALYTICAL_SUMMARY.md](ANALYTICAL_SUMMARY.md).

**As of:** game results and Elo from games final on November 8, 2026 (Weeks 1–8 plus 9 of 15 Week 9 games, including Carolina's); fourth-down play-by-play through Week 8. The data is frozen at that point.

## How to run

Run `fourth_down_underdog_analysis.ipynb` top to bottom from this folder on the "NFL-model (.venv)" kernel. The first run saves the raw nflverse pulls to `data/` (not committed); later runs read those files instead of re-pulling.

## Files

| File | What it is |
|---|---|
| `ANALYTICAL_SUMMARY.md` | Two-page summary for the head coach |
| `fourth_down_underdog_analysis.ipynb` | Analyses A–E and the figures |
| `definitions.py` | Definitions, model inputs, and as-of dates |
| `outputs/tables/` | One CSV per table (`A_` to `E_`), plus `panthers_decisions_vs_chart.csv` |
| `outputs/figures/` | Figures and the sideline card |

## Figures

| File | What it shows |
|---|---|
| `fig1_ep_decision_chart.png` | Fourth-Down Decision Chart (6.5-inch page): GO, PUNT, FG or CALL for each yards-to-go and field position |
| `fig2_how_to_go_for_it.png` | Conversion rate by yards to go, and on 4th & 1 by play type |
| `sideline_decision_card.png` / `.pdf` | The same chart on a landscape 8.5 × 11 page for game day |
