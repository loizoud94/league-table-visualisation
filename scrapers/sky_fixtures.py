import requests
import pandas as pd

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def fetch_remaining_fixtures(fixtures_json_url: str) -> pd.DataFrame:
    """
    Fetch remaining fixtures from Sky Sports via their JSON endpoint.
    """

    response = requests.get(fixtures_json_url, headers=HEADERS, timeout=15)
    response.raise_for_status()

    data = response.json()

    fixtures = []

    for match in data.get("matches", []):
        # Unplayed matches have no full-time result
        if match.get("status") != "fixture":
            continue

        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]

        fixtures.append({
            "Home": home,
            "Away": away
        })

    return pd.DataFrame(fixtures).drop_duplicates().reset_index(drop=True)
