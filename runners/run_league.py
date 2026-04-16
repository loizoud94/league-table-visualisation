from pathlib import Path
import yaml

from scrapers.sky_table import fetch_league_table
from logic.visualisation import build_visualisation
from logic.load_fixtures import load_remaining_fixtures_from_footballwebpages


BASE_DIR = Path(__file__).resolve().parents[1]


def run_league(league_name: str):
    # ---------- Load config ----------
    config_path = BASE_DIR / "config" / f"{league_name}.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # ---------- Data directory ----------
    data_dir = BASE_DIR / "data" / league_name
    data_dir.mkdir(parents=True, exist_ok=True)

    fixtures_raw_dir = data_dir / "fixtures_raw"

    # ---------- Fetch table ----------
    table = fetch_league_table(config["sources"]["table_url"])
    table.to_csv(data_dir / "table.csv", index=False)

    # ---------- Load fixtures (optional per league) ----------
    fixtures = None
    if fixtures_raw_dir.exists():
        fixtures = load_remaining_fixtures_from_footballwebpages(fixtures_raw_dir)
        fixtures.to_csv(data_dir / "fixtures.csv", index=False)

    # ---------- Build visualisation ----------
    visualisation = build_visualisation(
        table=table,
        total_games=config["total_games"],
        guaranteed_zones=config["zones"]["guaranteed"],
        predicted_zones=config["zones"]["predicted"],
        fixtures=fixtures,
    )

    visualisation.to_csv(data_dir / "visualisation.csv", index=False)