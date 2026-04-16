from logic.guaranteed_champions import compute_guaranteed_champions_unique


def compute_guaranteed_thresholds(
    table: pd.DataFrame,
    guaranteed_zones: dict,
    total_games: int,
    fixtures: pd.DataFrame | None = None,
) -> dict:


    df = table.copy()

    by_max = df.sort_values(
        ["Max_Points", "Pos"],
        ascending=[False, True]
    ).reset_index(drop=True)

    guarantees = {}

    # ✅ Special handling for Guaranteed Champions (unique winner)
    if "Guaranteed Champions" in guaranteed_zones:
        guarantees["Guaranteed Champions"] = compute_guaranteed_champions_unique(
            table=df,
            total_games=total_games,
            fixtures=fixtures
        )

    # ✅ All other guarantees remain naive max logic
    for label, cfg in guaranteed_zones.items():
        if label == "Guaranteed Champions":
            continue

        cutoff = cfg["cutoff_position"]
        guarantees[label] = int(by_max.loc[cutoff, "Max_Points"]) + 1

    return guarantees