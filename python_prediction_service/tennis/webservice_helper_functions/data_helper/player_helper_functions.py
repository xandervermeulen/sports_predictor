import datetime
import os

import numpy as np
import pandas as pd

from tennis.domain.Player import Player
from tennis.webservice_helper_functions.formatting_helper.matches_data_converter import convert_past_matches_data
from tennis.webservice_helper_functions.managers.DataManager import dm
from tennis.webservice_helper_functions.scraper_helper.matches_scraper import scrape_all_matches
from tennis.webservice_helper_functions.scraper_helper.players_scraper import update_player_rankings
from ufc_fights.webservice_helper_functions.managers.DatabaseManager import dbm

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', os.getenv('DATA_DIR')))
player_file = os.getenv('PLAYER_FILE')
csv_file = os.path.join(root_dir, player_file)


def convert_to_player_objects(player_stats):
    players = []
    print(player_stats.columns)
    for index, row in player_stats.iterrows():
        player = Player(row['name'], row['nationality'],
                        datetime.datetime.strptime(row['date_of_birth'], '%Y-%m-%d').date(), row['rank'],
                        row['Dominance Ratio'], row['Ace Ratio'], row['First Serve Percentage'],
                        row['First Serve Points Won'], row['Break Points Won'],
                        'Right', row['Ranking at that time'], row['Opponent Ranking at that time'],
                        row['Double Fault Ratio'], row['Second Serve Points Won'], row['round value'],
                        row['Break Points Faced'], row['Sets Won'], row['Sets Lost'], row['Total time'])
        players.append(player)
    return players


def get_players_data():
    all_matches, _ = scrape_all_matches()
    all_matches = all_matches.drop(columns=['Location'])
    all_matches = convert_past_matches_data(all_matches)
    player_stats = convert_matches_to_player_stats(all_matches)
    players = convert_to_player_objects(player_stats)
    return players


def read_player_stats():
    # get all player stats from db.Player
    player_stats = dm.get_all_players_serialized()
    return pd.DataFrame(player_stats)


def replace_non_numeric_with_nan(df, column_name):
    for x in df[column_name].unique():
        try:
            float(x)
        except ValueError or TypeError:
            df.loc[df[column_name] == x, column_name] = np.nan
    return df


def convert_matches_to_player_stats(all_matches):
    matches_data_filtered = all_matches.drop('isWinner', axis=1)
    matches_data_filtered = matches_data_filtered.dropna()
    matches_data_filtered = replace_all_non_numeric_values(matches_data_filtered)
    matches_data_filtered = convert_all_columns_to_float(matches_data_filtered)
    player_stats = (matches_data_filtered.groupby('player').mean().reset_index())
    player_info = pd.read_csv(csv_file)
    merged_df = player_stats.merge(player_info, left_on='player', right_on='name')
    return merged_df


def replace_all_non_numeric_values(matches_data_filtered):
    columns_to_convert = ["Dominance Ratio", "Ace Ratio", 'Ranking at that time', 'Opponent Ranking at that time',
                          "Double Fault Ratio", "First Serve Percentage", "First Serve Points Won",
                          "Second Serve Points Won",
                          "Break Points Won", "Break Points Faced", "round value", "Sets Won", "Sets Lost",
                          "Total time"]
    for column in columns_to_convert:
        matches_data_filtered = replace_non_numeric_with_nan(matches_data_filtered, column)

    matches_data_filtered = matches_data_filtered.dropna()
    return matches_data_filtered


def convert_column_to_float(df, column_name):
    df[column_name] = df[column_name].astype(float)
    return df


def convert_all_columns_to_float(matches_data_filtered):
    columns_to_convert = ["Dominance Ratio", "Ace Ratio", "Double Fault Ratio", "First Serve Percentage",
                          "First Serve Points Won", "Second Serve Points Won", "Break Points Won",
                          "Break Points Faced", "round value", "Sets Won", "Sets Lost", "Total time"]
    matches_data_filtered['Ranking at that time'] = matches_data_filtered['Ranking at that time'].astype(int)
    matches_data_filtered['Opponent Ranking at that time'] = matches_data_filtered[
        'Opponent Ranking at that time'].astype(int)
    for column in columns_to_convert:
        matches_data_filtered = convert_column_to_float(matches_data_filtered, column)
    return matches_data_filtered


def update_player_personal_info():
    players = update_player_rankings()
    for index, row in players.iterrows():
        player = dm.get_player_by_name(row['name'])
        if player:
            player.Ranking = row['rank']
        else:
            player = Player(row['name'], row['nationality'],
                            datetime.datetime.strptime(row['date_of_birth'], '%Y-%m-%d').date(), row['rank'],
                            0, 0, 0, 0, 0,
                            'Right', 0, 0, 0,
                            0, 0, 0, 0, 0, 0)
            dbm.session_add(player)
    dbm.commit()
    players = dm.get_all_players()
    players = [player.serialize_to_player_info() for player in players]
    players = pd.DataFrame(players)
    players.to_csv(csv_file, index=False)
