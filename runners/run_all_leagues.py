from runners.run_league import run_league

LEAGUES = [
    "national_league_north",
    "national_league_south",
    "national_league",
    "league_two",
    "league_one",
    "championship",
    "premier_league",
]

if __name__ == "__main__":
    for league in LEAGUES:
        print(f"Running {league}...")
        run_league(league)
    print("All leagues completed.")