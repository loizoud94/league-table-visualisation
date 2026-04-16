import pandas as pd


def compute_guaranteed_champions_unique(
    table: pd.DataFrame,
    total_games: int,
    fixtures: pd.DataFrame | None
) -> int | None:

    """
    Compute the minimum points total P such that
    it is impossible for two teams to both finish on >= P,
    given remaining fixtures.

    This guarantees a unique champion (identity not pre-known).
    """

    df = table.copy()

    # ✅ Derive Remaining games here (fix)
    df["Remaining"] = total_games - df["Played"]

    # Naive maximum possible per team
    df["Naive_Max"] = df["Points"] + 3 * df["Remaining"]

    P_min = int(df["Points"].max())
    P_max = int(df["Naive_Max"].max())

    teams = df["Team"].tolist()

    # Precompute remaining head-to-head fixtures
    h2h = set()
    if fixtures is not None:
        for _, fx in fixtures.iterrows():
            pair = tuple(sorted([fx["Home"], fx["Away"]]))
            h2h.add(pair)

    # Test candidate totals
    for P in range(P_min, P_max + 1):

        possible = []

        for _, team in df.iterrows():
            if team["Naive_Max"] >= P:
                possible.append(team["Team"])

        # If fewer than 2 teams can reach P, champion is unique
        if len(possible) <= 1:
            return P

        conflict = False

        for i in range(len(possible)):
            for j in range(i + 1, len(possible)):

                A = possible[i]
                B = possible[j]

                # If A and B do not play each other, both can win out
                if tuple(sorted([A, B])) not in h2h:
                    conflict = True
                    break

                A_row = df[df["Team"] == A].iloc[0]
                B_row = df[df["Team"] == B].iloc[0]

                # Case 1: A beats B
                A_best = A_row["Points"] + 3 * A_row["Remaining"]
                B_best = B_row["Points"] + 3 * (B_row["Remaining"] - 1)

                if A_best >= P and B_best >= P:
                    conflict = True
                    break

                # Case 2: B beats A
                A_best = A_row["Points"] + 3 * (A_row["Remaining"] - 1)
                B_best = B_row["Points"] + 3 * B_row["Remaining"]

                if A_best >= P and B_best >= P:
                    conflict = True
                    break

            if conflict:
                break

        if not conflict:
            return P

    return None
