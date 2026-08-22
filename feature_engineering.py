# importing all the necessary libraries
import pandas as pd
from snowflake_connector import snowflake_connector_init


# reading all the datasets. as our datasets are in xlsx file so using read_excel functions
current_standings = pd.read_excel("datasets/current_points_table.xlsx")
historical_points = pd.read_excel("datasets/history_points_table.xlsx")
epl_results = pd.read_excel("datasets/premier_league_matches.xlsx")
player_ratings = pd.read_excel("datasets/premier_league_player_ratings.xlsx")


# Making an array of datasets
datasets = {
    "Current Standings": current_standings,
    "Historical Points": historical_points,
    "EPL Results": epl_results,
    "Player Ratings": player_ratings
}


# reading all the necessary data structures and first 3 rows of the datasets
for name, df in datasets.items():
    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    # printing the shapr of the datasets
    print("Shape:", df.shape)
    print("\nColumns:")

    # printing the column names so that it will be easier for furthur analysis
    print(df.columns.tolist())

    # printing the first 3 rows of the datasets
    print("\nFirst 3 rows:")
    print(df.head(3))

    # finding the missing values for every columns in the datasets
    print("\nMissing values:")
    print(df.isnull().sum())




###############################################################################################################
######################## All the necessary functions for the file will be added here###########################
###############################################################################################################

# As our datasets has away and home scorelines so getting the exact result value 
# 'H' --> 'Home win'
# 'A' --> 'Away win'
# 'D' --> 'Draw' 

def get_match_result(row):
    if row["homeTeam_score"] > row["awayTeam_score"]:
        return "H"
    elif row["homeTeam_score"] < row["awayTeam_score"]:
        return "A"
    else:
        return "D"


epl_results.info()
epl_results.describe(include="all")

# Passing every rows of the result dataset to get the total home win, away win and draws
epl_results["match_result"] = epl_results.apply(
    get_match_result,
    axis=1
)

# printing the first 10 rows of the updated dataframe to see if the new column is populated properly or not
print(epl_results[
    [
        "homeTeam_name",
        "homeTeam_score",
        "awayTeam_name",
        "awayTeam_score",
        "match_result"
    ]
].head(10))

# determining the total number of home wins, away wins and draws
print(epl_results["match_result"].value_counts())


# converting kickoff column data into datetime format
epl_results["kickoff"] = pd.to_datetime(
    epl_results["kickoff"],
    errors="coerce"
)

print(epl_results["kickoff"].dtype)

# Detemininf total na values in kickoff column 
print(epl_results["kickoff"].isna().sum())
epl_results = epl_results.sort_values(
    "kickoff"
).reset_index(drop=True)

# printing the first and last match of the datasets from our historical match table
print("First match:", epl_results["kickoff"].min())
print("Last match:", epl_results["kickoff"].max())

# printing the sample data for furthur analysis
print(epl_results[
    [
        "season",
        "matchWeek",
        "kickoff",
        "homeTeam_name",
        "awayTeam_name",
        "homeTeam_score",
        "awayTeam_score",
        "match_result"
    ]
].head(10))



# initializing the snowflake connection
con = snowflake_connector_init()


# query to retrieve historical data from snowflake
query = """
SELECT *
FROM HISTORICAL_TEAM_PERFORMANCE
ORDER BY SEASON, POSITION
"""

# fetching all the historical data from snowflake
historical_team_performance = con.cursor().execute(query).fetch_pandas_all()
# print(historical_team_performance)