import pandas as pd
from pathlib import Path

def load_remaining_fixtures_from_footballwebpages(folder: Path) -> pd.DataFrame:
    """
    Robust loader for FootballWebPages CSVs that may contain:
    - multiple tables in one file
    - mixed headers
    - variable column counts

    A remaining fixture is identified by:
    - the presence of literal 'v'
    - two non-empty team names on either side of it
    """

    fixtures = []

    for csv_path in folder.glob("*.csv"):
        # ALWAYS read raw – no headers, no dtype coercion
        df = pd.read_csv(csv_path, header=None, dtype=str, encoding="cp1252")

        for _, row in df.iterrows():
            values = [v for v in row.values if isinstance(v, str) and v.strip()]

            # Must contain the fixture marker
            if "v" not in values:
                continue

            v_idx = values.index("v")

            # Need a team before and after
            if v_idx == 0 or v_idx == len(values) - 1:
                continue

            home = values[v_idx - 1].strip()
            away = values[v_idx + 1].strip()

            # Basic sanity filter (avoids headers / junk rows)
            if len(home) < 3 or len(away) < 3:
                continue

            fixtures.append({
                "Home": home,
                "Away": away
            })

    return (
        pd.DataFrame(fixtures)
        .drop_duplicates()
        .reset_index(drop=True)
    )
