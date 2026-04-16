import pandas as pd
import requests
import warnings
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore")

SKY_URL = "https://www.skysports.com/league-2-table"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def fetch_league_table():
    print("Fetching League Two from Sky Sports...")
    response = requests.get(SKY_URL, headers=HEADERS, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    rows = soup.find_all("tr", {"class": lambda x: x and "sdc-site-table__row" in x})
    if not rows:
        raise ValueError("No team rows found")

    teams = []
    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 10:
            teams.append({
                "Pos": cells[0].get_text(strip=True),
                "Team": cells[1].get_text(strip=True),
                "Played": cells[2].get_text(strip=True),
                "Won": cells[3].get_text(strip=True),
                "Drawn": cells[4].get_text(strip=True),
                "Lost": cells[5].get_text(strip=True),
                "GF": cells[6].get_text(strip=True),
                "GA": cells[7].get_text(strip=True),
                "GD": cells[8].get_text(strip=True),
                "Points": cells[9].get_text(strip=True),
            })

    if not teams:
        raise ValueError("Could not parse team data")
    return pd.DataFrame(teams)

def build_visualization(table):
    table["Points"] = table["Points"].astype(int)
    table["Played"] = table["Played"].astype(int)
    table["Pos"] = table["Pos"].astype(int)
    
    # Calculate max attainable points (46 games total)
    table["Max_Points"] = table["Points"] + (46 - table["Played"]) * 3
    
    # Calculate PPG
    table["PPG"] = table["Points"] / table["Played"]
    
    # Calculate games in hand
    max_played = table["Played"].max()
    table["Games_In_Hand"] = max_played - table["Played"]
    table["Team_Display"] = table.apply(
        lambda row: f"{row['Team']} ({-row['Games_In_Hand']})" if row["Games_In_Hand"] > 0 else row["Team"],
        axis=1
    )
    
    # Sort by current Points descending, then by Pos ascending for current positions
    table_sorted_current = table.sort_values(["Points", "Pos"], ascending=[False, True]).reset_index(drop=True)
    
    # Sort by Max_Points descending for guaranteed thresholds
    table_sorted_max = table.sort_values(["Max_Points", "Pos"], ascending=[False, True]).reset_index(drop=True)
    
    # Calculate thresholds based on maximum attainable points order
    guaranteed_champions_threshold = table_sorted_max.loc[1, "Max_Points"] + 1  # 2nd highest max + 1
    guaranteed_runners_up_threshold = table_sorted_max.loc[2, "Max_Points"] + 1  # 3rd highest max + 1
    guaranteed_promotion_threshold = table_sorted_max.loc[3, "Max_Points"] + 1  # 4th highest max + 1
    guaranteed_playoffs_threshold = table_sorted_max.loc[7, "Max_Points"] + 1  # 8th highest max + 1
    guaranteed_safety_threshold = table_sorted_max.loc[22, "Max_Points"] + 1  # 23rd highest max + 1
    
    # Sort by PPG descending for predictions
    table_sorted_ppg = table.sort_values("PPG", ascending=False).reset_index(drop=True)
    
    # Calculate Predicted points
    predicted_champions_points = round(table_sorted_ppg.loc[0, "Points"] + (46 - table_sorted_ppg.loc[0, "Played"]) * table_sorted_ppg.loc[0, "PPG"])
    predicted_runners_up_points = round(table_sorted_ppg.loc[1, "Points"] + (46 - table_sorted_ppg.loc[1, "Played"]) * table_sorted_ppg.loc[1, "PPG"])
    predicted_promotion_points = round(table_sorted_ppg.loc[2, "Points"] + (46 - table_sorted_ppg.loc[2, "Played"]) * table_sorted_ppg.loc[2, "PPG"])  # top 3
    predicted_4th_points = round(table_sorted_ppg.loc[3, "Points"] + (46 - table_sorted_ppg.loc[3, "Played"]) * table_sorted_ppg.loc[3, "PPG"])
    predicted_playoffs_points = round(table_sorted_ppg.loc[6, "Points"] + (46 - table_sorted_ppg.loc[6, "Played"]) * table_sorted_ppg.loc[6, "PPG"])  # top 7
    predicted_8th_points = round(table_sorted_ppg.loc[7, "Points"] + (46 - table_sorted_ppg.loc[7, "Played"]) * table_sorted_ppg.loc[7, "PPG"])  # 8th
    predicted_safety_points = round(table_sorted_ppg.loc[21, "Points"] + (46 - table_sorted_ppg.loc[21, "Played"]) * table_sorted_ppg.loc[21, "PPG"])  # 22nd
    predicted_relegation_points = round(table_sorted_ppg.loc[22, "Points"] + (46 - table_sorted_ppg.loc[22, "Played"]) * table_sorted_ppg.loc[22, "PPG"])  # 23rd
    
    # Build ladder rows from max attainable down to min current points
    min_pts = int(table["Points"].min())
    max_max = int(table["Max_Points"].max())
    
    ladder_rows = []
    for pts in range(max_max, min_pts - 1, -1):
        match = table[table["Points"] == pts]
        row = {"Points": pts, "Team": "", "Pos": "", "Zone": ""}
        if not match.empty:
            row["Team"] = ", ".join(match["Team_Display"].tolist())
            row["Pos"] = ", ".join(map(str, match["Pos"].tolist()))
        # Collect all applicable zones
        zone_list = []
        if pts == max_max:
            zone_list.append("Maximum")
        if pts == guaranteed_champions_threshold:
            zone_list.append("Guaranteed Champions")
        if pts == guaranteed_runners_up_threshold:
            zone_list.append("Guaranteed Runners-Up")
        if pts == guaranteed_promotion_threshold:
            zone_list.append("Guaranteed Promotion")
        if pts == guaranteed_playoffs_threshold:
            zone_list.append("Guaranteed Play-Offs")
        if pts == guaranteed_safety_threshold:
            zone_list.append("Guaranteed Safety")
        if pts == predicted_champions_points:
            zone_list.append("Predicted Champions")
        if pts == predicted_runners_up_points:
            zone_list.append("Predicted Runners-Up")
        if pts == predicted_promotion_points:
            zone_list.append("Predicted Promotion")
        if pts == predicted_4th_points:
            zone_list.append("Predicted 4th")
        if pts == predicted_playoffs_points:
            zone_list.append("Predicted Play-Offs")
        if pts == predicted_8th_points:
            zone_list.append("Predicted 8th")
        if pts == predicted_safety_points:
            zone_list.append("Predicted Safety")
        if pts == predicted_relegation_points:
            zone_list.append("Predicted Relegation")
        row["Zone"] = ", ".join(zone_list) if zone_list else ""
        ladder_rows.append(row)
    
    return pd.DataFrame(ladder_rows)

if __name__ == "__main__":
    try:
        table = fetch_league_table()
        csv_path = r"C:\Users\DemetriLoizou\OneDrive - Thermatic\Documents\league table visualisation\data\league_two_table.csv"
        table.to_csv(csv_path, index=False)

        vis_csv_path = r"C:\Users\DemetriLoizou\OneDrive - Thermatic\Documents\league table visualisation\data\league_two_visualisation.csv"
        build_visualization(table).to_csv(vis_csv_path, index=False)

        print(f"Raw data exported to {csv_path}")
        print(f"Visualization data exported to {vis_csv_path}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()