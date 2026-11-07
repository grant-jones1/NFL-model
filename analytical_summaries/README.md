# Analytical summaries

Each summary answers one decision-focused question for a specific (hypothetical) football stakeholder, using the core NFL model and nflverse data. The goal is to translate the modeling into a recommendation the stakeholder can act on, and to be clear about how much the evidence can and can't support.

## Format

Every summary follows the same structure:

| Section | What it covers |
|---|---|
| **Question** | The single decision-focused question, in the stakeholder's terms. |
| **Context** | The stakeholder's situation, taken from the data (never assumed). |
| **Assumptions** | What is taken as given: model settings, data sources, how ambiguous terms are resolved. |
| **Scope** | Seasons, teams, and situations included, and what is deliberately left out. |
| **Methods** | A plain-language description of the approach, with the locked definitions. |
| **Results** | Tables with counts next to every rate, saved to `outputs/tables/`. |
| **Limitations** | Sample sizes, selection effects, and anything that could not be computed. |
| **Recommendations** | What the stakeholder should do, and how confident to be. |

## Folder layout

    NN_topic_audience/
      *.ipynb            the analysis notebook(s)
      definitions.py     locked definitions and settings for this summary
      outputs/tables/    CSV for every summary table (counts alongside rates)
      outputs/figures/   charts
      README.md          audience, question, how to run

Summaries import the core model from `src/nflmodel/` (Elo ratings, projections, evaluation) instead of duplicating it. Run each notebook from its own folder on the "NFL-model (.venv)" kernel so it picks up its local `definitions.py`.

## Summaries

| # | Folder | Audience | Question |
|---|---|---|---|
| 01 | [01_wp_calibration_gm](01_wp_calibration_gm/) | General manager | When the model says a team has an X% chance to win, does it win about X% of the time, and are its playoff odds trustworthy? |
| 02 | [02_fourth_down_underdog_hc](02_fourth_down_underdog_hc/) | Carolina Panthers head coach | Given that the Panthers are projected underdogs in most of their remaining 2026 games, how much fourth-down risk should the head coach take? |
