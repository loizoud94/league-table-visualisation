import requests
import pandas as pd
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def fetch_league_table(url: str) -> pd.DataFrame:
    """
    Fetch and parse a league table from Sky Sports.
    Cleans team names to remove Sky annotation (e.g. *, **).
    """

    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    rows = soup.find_all(
        "tr",
        {"class": lambda x: x and "sdc-site-table__row" in x}
    )

    teams = []
    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 10:
            teams.append({
                "Pos": int(cells[0].get_text(strip=True)),
                "Team": cells[1].get_text(strip=True),
                "Played": int(cells[2].get_text(strip=True)),
                "Won": int(cells[3].get_text(strip=True)),
                "Drawn": int(cells[4].get_text(strip=True)),
                "Lost": int(cells[5].get_text(strip=True)),
                "GF": int(cells[6].get_text(strip=True)),
                "GA": int(cells[7].get_text(strip=True)),
                "GD": int(cells[8].get_text(strip=True)),
                "Points": int(cells[9].get_text(strip=True)),
            })

    if not teams:
        raise ValueError("No team data parsed from table")

    # ✅ Create DataFrame first
    df = pd.DataFrame(teams)

    # ✅ Strip Sky deduction markers (*, **)
    df["Team"] = (
        df["Team"]
        .str.replace(r"^\*+\s*", "", regex=True)
        .str.strip()
    )

    return df