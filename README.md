# League Table Visualisation

A Python-based football league modelling project that generates
guaranteed outcomes and predicted finishing zones across multiple leagues.

The project supports:
- Premier League
- EFL
- National League (+ North / South)

and is designed to scale purely via configuration.

---

## What this project does

Given the current league table and remaining fixtures, the model produces:

### Guaranteed zones
Mathematically guaranteed outcomes that are **independent of future results**, including:
- Guaranteed Champions (unique winner logic)
- Guaranteed Promotion / Play-Offs / Champions League (league-dependent)
- Guaranteed Safety

### Predicted zones
Trend-based projections using:
- Points-per-game
- Adjustment for points deductions
- Remaining matches

Predicted outcomes are **not guarantees** and are intended as informed projections.

---

## Key features

- Fully config-driven league rules (`config/*.yaml`)
- Fixture-aware guarantees (including correct title-race logic)
- Deduction-aware predictions (Championship-ready)
- Clean separation of:
  - data ingestion
  - modelling logic
  - presentation
- Designed to regenerate all outputs from source

---

## Project structure

``Raw fixture CSVs (`data/**/fixtures_raw/*.csv`) are treated as versioned inputs
where automatic scraping is not feasible.

---

## How to run

Create a virtual environment, install dependencies, then run:

```bash
py -m runners.run_all_leagues