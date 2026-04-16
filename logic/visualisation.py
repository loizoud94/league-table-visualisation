import pandas as pd
from logic.guaranteed_thresholds import compute_guaranteed_thresholds


def build_visualisation(
    table: pd.DataFrame,
    total_games: int,
    guaranteed_zones: dict,
    predicted_zones: dict,
    fixtures: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Build ladder-style visualisation showing:
    - guaranteed thresholds (identity-safe)
    - predicted thresholds (deduction-aware projections)
    """

    df = table.copy()

    # ------------------------------------------------------------------
    # Core derived fields
    # ------------------------------------------------------------------

    df["Remaining"] = total_games - df["Played"]
    df["Max_Points"] = df["Points"] + df["Remaining"] * 3

    # Ensure Deduction exists (0 for most leagues)
    if "Deduction" not in df.columns:
        df["Deduction"] = 0

    # Performance reality
    df["Adjusted_Points"] = df["Points"] + df["Deduction"]
    df["Adjusted_PPG"] = df["Adjusted_Points"] / df["Played"]

    # Display helper
    max_played = df["Played"].max()
    df["Games_In_Hand"] = max_played - df["Played"]
    df["Team_Display"] = df.apply(
        lambda r: f"{r['Team']} ({-r['Games_In_Hand']})"
        if r["Games_In_Hand"] > 0 else r["Team"],
        axis=1,
    )

    # ------------------------------------------------------------------
    # Ordering
    # ------------------------------------------------------------------

    by_max = df.sort_values(
        ["Max_Points", "Pos"],
        ascending=[False, True],
    ).reset_index(drop=True)

    by_adj_ppg = df.sort_values(
        ["Adjusted_PPG", "Pos"],
        ascending=[False, True],
    ).reset_index(drop=True)

    # ------------------------------------------------------------------
    # Guaranteed thresholds (unchanged logic)
    # ------------------------------------------------------------------

    guaranteed = compute_guaranteed_thresholds(
        table=by_max,
        guaranteed_zones=guaranteed_zones,
        total_games=total_games,
        fixtures=fixtures,
    )

    # ------------------------------------------------------------------
    # Predicted thresholds (Step 3 logic)
    # ------------------------------------------------------------------

    def projected_table_points(row) -> int:
        """
        Project final table points using performance reality,
        then re-apply deduction so output is in table terms.
        """
        projected_adjusted = (
            row["Adjusted_Points"]
            + row["Adjusted_PPG"] * row["Remaining"]
        )
        projected_table = projected_adjusted - row["Deduction"]
        return int(round(projected_table))

    df["Projected_Points"] = df.apply(projected_table_points, axis=1)

    by_projected = df.sort_values(
        ["Projected_Points", "Pos"],
        ascending=[False, True],
    ).reset_index(drop=True)

    predicted = {}

    for label, cfg in predicted_zones.items():
        if "position" in cfg:
            idx = cfg["position"] - 1
        elif "cutoff_position" in cfg:
            idx = cfg["cutoff_position"] - 1
        else:
            continue

        predicted[label] = int(by_projected.loc[idx, "Projected_Points"])

    # ------------------------------------------------------------------
    # Ladder construction
    # ------------------------------------------------------------------

    min_pts = int(df["Points"].min())
    max_pts = int(df["Max_Points"].max())

    ladder_rows = []

    for pts in range(max_pts, min_pts - 1, -1):
        row = {
            "Points": pts,
            "Team": "",
            "Pos": "",
            "Zone": "",
        }

        matches = df[df["Points"] == pts]
        if not matches.empty:
            row["Team"] = ", ".join(matches["Team_Display"])
            row["Pos"] = ", ".join(map(str, matches["Pos"]))

        zones = []

        if pts == max_pts:
            zones.append("Maximum")

        for label, value in guaranteed.items():
            if pts == value:
                zones.append(label)

        for label, value in predicted.items():
            if pts == value:
                zones.append(label)

        row["Zone"] = ", ".join(zones)
        ladder_rows.append(row)

    return pd.DataFrame(ladder_rows)
