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


# Calculate the form of the team before the match considering the last 5 results
#  Win = 3 points, Draw = 1 and Lose = 0
def calculate_form_points(team_id, season, match_date, results, n=5):

    previous_matches = results[
        (
            ((results["homeTeam_id"] == team_id) |
             (results["awayTeam_id"] == team_id))
            &
            (results["season"] == season)
            &
            (results["kickoff"] < match_date)
        )
    ].tail(n)

    points = 0

    for _, match in previous_matches.iterrows():

        if match["homeTeam_id"] == team_id:

            if match["homeTeam_score"] > match["awayTeam_score"]:
                points += 3

            elif match["homeTeam_score"] == match["awayTeam_score"]:
                points += 1

        else:

            if match["awayTeam_score"] > match["homeTeam_score"]:
                points += 3

            elif match["awayTeam_score"] == match["homeTeam_score"]:
                points += 1

    return points


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

# Determining the shape, columns of the table 
print(historical_team_performance.shape)
print(historical_team_performance.head())
print(historical_team_performance.columns.tolist())


# creating a new data frame for furthur feature development
historical_features = historical_team_performance.copy()

# renaming the columns name as a part of feature engineering
historical_features = historical_features.rename(columns={
    "SEASON": "previous_season",
    "TEAM_ID": "team_id",
    "TEAM_KEY": "team_key",
    "TEAM_NAME": "team_name",
    "POSITION": "previous_position",
    "POINTS": "previous_points",
    "WON": "previous_wins",
    "DRAWN": "previous_draws",
    "LOST": "previous_losses",
    "GOALS_FOR": "previous_goals_for",
    "GOALS_AGAINST": "previous_goals_against"
})


# Determining the goal difference 
historical_features["previous_goal_difference"] = (
    historical_features["previous_goals_for"]
    - historical_features["previous_goals_against"]
)

# creating a new feature previous year by subtracting the current season by 1
historical_features["season"] = (
    historical_features["previous_season"] + 1
)

# printing the top 20 results from the above developed features
print(
    historical_features[
        [
            "previous_season",
            "season",
            "team_id",
            "team_key",
            "team_name",
            "previous_position",
            "previous_points",
            "previous_goal_difference"
        ]
    ].head(20)
)

# printing the shap of the above feature created
print(historical_features.shape)


# creating new features for home results as done above
home_history = historical_features[
    [
        "season",
        "team_id",
        "previous_position",
        "previous_points",
        "previous_wins",
        "previous_draws",
        "previous_losses",
        "previous_goals_for",
        "previous_goals_against",
        "previous_goal_difference"
    ]
].copy()


# Renaming the columns for furthur ease
home_history = home_history.rename(columns={
    "team_id": "homeTeam_id",
    "previous_position": "home_previous_position",
    "previous_points": "home_previous_points",
    "previous_wins": "home_previous_wins",
    "previous_draws": "home_previous_draws",
    "previous_losses": "home_previous_losses",
    "previous_goals_for": "home_previous_goals_for",
    "previous_goals_against": "home_previous_goals_against",
    "previous_goal_difference": "home_previous_goal_difference"
})

# merging all the records based on the year for every team
# this is done since our records has multiple tables based on match location i.e home, away and overall
epl_features = epl_results.merge(
    home_history,
    on=["season", "homeTeam_id"],
    how="left"
)

away_history = historical_features[
    [
        "season",
        "team_id",
        "previous_position",
        "previous_points",
        "previous_wins",
        "previous_draws",
        "previous_losses",
        "previous_goals_for",
        "previous_goals_against",
        "previous_goal_difference"
    ]
].copy()


# creating new features for away results as done above
away_history = away_history.rename(columns={
    "team_id": "awayTeam_id",
    "previous_position": "away_previous_position",
    "previous_points": "away_previous_points",
    "previous_wins": "away_previous_wins",
    "previous_draws": "away_previous_draws",
    "previous_losses": "away_previous_losses",
    "previous_goals_for": "away_previous_goals_for",
    "previous_goals_against": "away_previous_goals_against",
    "previous_goal_difference": "away_previous_goal_difference"
})

epl_features = epl_features.merge(
    away_history,
    on=["season", "awayTeam_id"],
    how="left"
)

print(
    epl_features[
        [
            "season",
            "homeTeam_name",
            "awayTeam_name",
            "home_previous_points",
            "away_previous_points",
            "home_previous_position",
            "away_previous_position"
        ]
    ].head(20)
)


# testing if our feature is working properly or not for 2009
# commenting this part as this was done just for data testing during development
# print(
#     epl_features[
#         epl_features["season"] == 2009
#     ][
#         [
#             "season",
#             "homeTeam_name",
#             "homeTeam_id",
#             "home_previous_position",
#             "home_previous_points",
#             "home_previous_goal_difference"
#         ]
#     ].head(20)
# )


test_match = epl_results.iloc[100]

print("Match:")
print(test_match["homeTeam_name"], "vs", test_match["awayTeam_name"])



#####################################
# Calculating the team form
#####################################
home_form = calculate_form_points(
    test_match["homeTeam_id"],
    test_match["season"],
    test_match["kickoff"],
    epl_results
)

away_form = calculate_form_points(
    test_match["awayTeam_id"],
    test_match["season"],
    test_match["kickoff"],
    epl_results
)

print("Home form:", home_form)
print("Away form:", away_form)


# Taking the last 5 matches before the match we are predicting for home team
team_id = test_match["homeTeam_id"]
match_date = test_match["kickoff"]

previous_matches = epl_results[
    (
        (epl_results["homeTeam_id"] == team_id) |
        (epl_results["awayTeam_id"] == team_id)
    )
    &
    (epl_results["kickoff"] < match_date)
].tail(5)

print(
    previous_matches[
        [
            "kickoff",
            "homeTeam_name",
            "awayTeam_name",
            "homeTeam_score",
            "awayTeam_score",
            "match_result"
        ]
    ]
)


# Taking the last 5 matches before the match we are predicting for away team
team_id = test_match["awayTeam_id"]

previous_matches = epl_results[
    (
        (epl_results["homeTeam_id"] == team_id) |
        (epl_results["awayTeam_id"] == team_id)
    )
    &
    (epl_results["kickoff"] < test_match["kickoff"])
].tail(5)

print(
    previous_matches[
        [
            "kickoff",
            "homeTeam_name",
            "awayTeam_name",
            "homeTeam_score",
            "awayTeam_score",
            "match_result"
        ]
    ]
)




#####################################
# Calculating the team form at the start of our data frame
#####################################

first_match = epl_results.iloc[0]

print(first_match[
    [
        "kickoff",
        "homeTeam_name",
        "awayTeam_name"
    ]
])

print(
    "Home form:",
    calculate_form_points(
        first_match["homeTeam_id"],
        first_match["kickoff"],
        test_match["kickoff"],
        epl_results
    )
)

print(
    "Away form:",
    calculate_form_points(
        first_match["awayTeam_id"],
        first_match["kickoff"],
        test_match["kickoff"],
        epl_results
    )
)




#####################################
# Calculating the team form for the 3rd of our data frame
#####################################

early_match = epl_results.iloc[10]

print(
    early_match[
        [
            "kickoff",
            "homeTeam_name",
            "awayTeam_name"
        ]
    ]
)

print(
    "Home form:",
    calculate_form_points(
        early_match["homeTeam_id"],
        early_match["kickoff"],
        test_match["kickoff"],
        epl_results
    )
)

print(
    "Away form:",
    calculate_form_points(
        early_match["awayTeam_id"],
        early_match["kickoff"],
        test_match["kickoff"],
        epl_results
    )
)




#####################################
# verifying that the model doesnt use current match in consideration
#####################################

test_match = epl_results.iloc[100]

team_id = test_match["homeTeam_id"]
match_date = test_match["kickoff"]

previous_matches = epl_results[
    (
        (epl_results["homeTeam_id"] == team_id) |
        (epl_results["awayTeam_id"] == team_id)
    )
    &
    (epl_results["kickoff"] < match_date)
]

print("Current match date:", match_date)
print("Latest previous match:", previous_matches["kickoff"].max())




#####################################
# Testin the logic for model development is working correctly for 2009 
#####################################
first_2009 = epl_results[
    epl_results["season"] == 2009
].iloc[0]

print(first_2009[
    [
        "season",
        "kickoff",
        "homeTeam_name",
        "awayTeam_name"
    ]
])


team_id = first_2009["homeTeam_id"]

previous_matches = epl_results[
    (
        (epl_results["homeTeam_id"] == team_id) |
        (epl_results["awayTeam_id"] == team_id)
    )
    &
    (epl_results["kickoff"] < first_2009["kickoff"])
].tail(5)

print(
    previous_matches[
        [
            "season",
            "kickoff",
            "homeTeam_name",
            "awayTeam_name",
            "homeTeam_score",
            "awayTeam_score"
        ]
    ]
)


#####################################
# verifying that the model for 2009 starting
#####################################

first_2009 = epl_results[
    epl_results["season"] == 2009
].iloc[0]

print(
    first_2009[
        [
            "season",
            "kickoff",
            "homeTeam_name",
            "awayTeam_name"
        ]
    ]
)

home_form = calculate_form_points(
    first_2009["homeTeam_id"],
    first_2009["season"],
    first_2009["kickoff"],
    epl_results
)

away_form = calculate_form_points(
    first_2009["awayTeam_id"],
    first_2009["season"],
    first_2009["kickoff"],
    epl_results
)

print("Home form:", home_form)
print("Away form:", away_form)


test_2009 = epl_results[
    (epl_results["season"] == 2009)
].iloc[50]

print(
    test_2009[
        [
            "season",
            "kickoff",
            "homeTeam_name",
            "awayTeam_name"
        ]
    ]
)

home_form = calculate_form_points(
    test_2009["homeTeam_id"],
    test_2009["season"],
    test_2009["kickoff"],
    epl_results
)

away_form = calculate_form_points(
    test_2009["awayTeam_id"],
    test_2009["season"],
    test_2009["kickoff"],
    epl_results
)

print("Home form:", home_form)
print("Away form:", away_form)