# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np

# Read in data from CSV file
url = 'https://raw.githubusercontent.com/sznajdr/teambulizwo/main/team_odds.csv'
df = pd.read_csv(url).fillna(0.00)

# Create dropdown menu to select team
teams = df[['home_team', 'away_team']].stack().unique()

# Define function to update table
def update_table(team):
    # Filter dataframe to show games where the selected team is either the home or away team
    team_games = df[(df['home_team'] == team) | (df['away_team'] == team)]
    team_data = team_games.copy()

    # Calculate median odds for selected team
    if team in team_games['home_team'].unique():
        median_odds = team_games.groupby('match_id')['home_odds'].median()
        team_odds_home = team_games.loc[team_games['home_team'] == team].groupby('match_id')['home_odds'].median()
        team_odds_away = team_games.loc[team_games['away_team'] == team].groupby('match_id')['away_odds'].median()
        team_odds_change_home = team_data.loc[team_data['home_team'] == team].groupby('match_id')['home_odds_change'].median()
        team_odds_change_away = team_data.loc[team_data['away_team'] == team].groupby('match_id')['away_odds_change'].median()
        team_odds = pd.concat([team_odds_home, team_odds_away]).sort_index()
        team_odds_change = pd.concat([team_odds_change_home, team_odds_change_away]).sort_index()
    else:
        median_odds = team_games.groupby('match_id')['away_odds'].median()
        team_odds_away = team_games.loc[team_games['away_team'] == team].groupby('match_id')['away_odds'].median()
        team_odds_home = team_games.loc[team_games['home_team'] == team].groupby('match_id')['home_odds'].median()
        team_odds_change_away = team_data.loc[team_data['away_team'] == team].groupby('match_id')['away_odds_change'].median()
        team_odds_change_home = team_data.loc[team_data['home_team'] == team].groupby('match_id')['home_odds_change'].median()
        team_odds = pd.concat([team_odds_home, team_odds_away]).sort_index()
        team_odds_change = pd.concat([team_odds_change_home, team_odds_change_away]).sort_index()

    # Combine both into one final dataframe with match_id, date, team_odds, team_odds_change
    team_odds_df = pd.DataFrame({'match_id': team_odds.index, 'team_odds': team_odds.values, 'team_odds_change': team_odds_change.values})
    team_odds_df['date'] = team_data.groupby('match_id')['date'].first().values # get the date for each game
    team_odds_df['date'] = pd.to_datetime(team_odds_df['date']) # convert date to datetime format
    team_odds_df['team_odds_change_pct'] = (team_odds_df['team_odds_change'] / team_odds_df['team_odds']) * 100
    # Plot the odds from final df by date, Team_odds on left side of y axis and team_odds_change on right side of y axis, x axis just date
    fig, ax1 = plt.subplots(figsize=(17, 9))
    ax2 = ax1.twinx()
    ax1.plot(team_odds_df['date'], team_odds_df['team_odds'], 'g-')
    ax2.plot(team_odds_df['date'], team_odds_df['team_odds_change_pct'], 'b-')
    ax1.set_ylabel('Team Odds', color='g')
    ax2.set_ylabel('Team Odds Change in %', color='b')
    ax2.axhline(y=0, color='grey', linestyle='--')


    bookmaker_list = team_games['bookmaker_name'].unique().tolist()
    bookmakers_text = "Bookmakers:\n" + "\n".join(bookmaker_list) # separate bookmaker list with newline character
    ax1.text(+1.09, +0.04, bookmakers_text, transform=ax1.transAxes, fontsize=12, bbox=dict(facecolor='white', edgecolor='black', pad=10.0)) # add text box with bookmaker list
        
    # Rotate x-axis labels
    ax1.tick_params(axis='x', rotation=90)
    plt.title(f"Odds Movement for {team}")
    st.pyplot(fig)
    plt.close()

    # Display table
    st.table(team_games[['date', 'home_team', 'away_team', 'bookmaker_name', 'home_odds', 'draw_odds', 'away_odds', 'home_odds_change', 'draw_odds_change', 'away_odds_change']].dropna())

    
team_dropdown = st.selectbox('Select Team:', teams, key='1')
update_table(team_dropdown)
