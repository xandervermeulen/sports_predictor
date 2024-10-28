import os

import numpy as np
import pandas as pd

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', os.getenv('DATA_DIR')))
player_file = os.getenv('PLAYER_FILE')
csv_file = os.path.join(root_dir, player_file)


def convert_past_matches_data(matches_data):
    matches_data = (matches_data.rename(columns={'player_name': 'player'}).dropna()
                    .pipe(apply_round_mapping).pipe(format_percentages_columns)
                    .pipe(format_time_column).pipe(format_set_scores))
    matches_data_filtered = matches_data.drop(['Set Scores', 'Set 1', 'Set 2', 'Set 3', 'Set 4', 'Set 5'], axis=1)
    past_matches = get_correct_fighter_names(matches_data_filtered)
    past_matches = add_result_column(past_matches)
    return past_matches


def apply_round_mapping(matches_data):
    round_mapping = {
        'Q1': 1, 'Q2': 1, 'Q3': 1, 'RR': 1,
        'R128': 1.5, 'R64': 2, 'R32': 3,
        'R16': 5, 'QF': 7, 'SF': 12, 'F': 20
    }

    matches_data['round value'] = matches_data['Round in Tournament'].map(round_mapping)
    return matches_data


def format_percentages_columns(matches_data):
    percentage_cols = ['Ace Ratio', 'Double Fault Ratio', 'First Serve Percentage',
                       'First Serve Points Won', 'Second Serve Points Won']
    for col in percentage_cols:
        matches_data[col] = matches_data[col].str.replace('%', '')
    break_points = matches_data['Break Points Saved'].str.split('/', expand=True)
    break_points.columns = ['Break Points Won', 'Break Points Faced']
    matches_data = pd.concat([matches_data, break_points], axis=1)
    return matches_data


def format_time_column(matches_data):
    matches_data_filtered = matches_data[matches_data.isnull().sum(axis=1) <= 3]
    times_split = matches_data_filtered['Time'].str.split(':', expand=True)
    times_split.columns = ['Hours', 'Minutes']
    matches_data_filtered = pd.concat([matches_data_filtered, times_split], axis=1)
    matches_data_filtered['Hours'] = pd.to_numeric(matches_data_filtered['Hours'])
    matches_data_filtered['Minutes'] = pd.to_numeric(matches_data_filtered['Minutes'])
    matches_data_filtered['Total time'] = matches_data_filtered['Hours'] * 60 + matches_data_filtered['Minutes']
    matches_data_filtered = matches_data_filtered.drop(['Hours', 'Minutes'], axis=1)
    return matches_data_filtered


def format_set_scores(matches_data):
    matches_data['isWinner'] = matches_data.apply(is_winner, axis=1)
    matches_data['Set Scores'] = matches_data['Set Scores'].str.replace(r'\s*RET\s*$', '', regex=True)
    matches_data['Set Scores'] = matches_data['Set Scores'].str.replace(r'\[\d+-\d+\]', '', regex=True)
    sets = matches_data['Set Scores'].str.split(' ', expand=True)
    sets.columns = [f'Set {i + 1}' for i in range(sets.shape[1])]
    matches_data = pd.concat([matches_data, sets], axis=1)
    matches_data = calculate_points(matches_data, sets)
    return matches_data


def calculate_points(matches_data, sets):
    points_won, points_lost = [], []
    for _, row in matches_data.iterrows():
        player_won = row['isWinner']
        player_points, opponent_points = 0, 0
        for set_score in row[sets.columns]:
            if pd.notnull(set_score):
                set_score_parts = set_score.split('-')
                if len(set_score_parts) < 2:
                    continue
                set_score_parts = [part.split('(')[0] for part in set_score_parts]
                if set_score_parts[0].isdigit() and set_score_parts[1].isdigit():
                    if player_won:
                        player_points += int(set_score_parts[0])
                        opponent_points += int(set_score_parts[1])
                    else:
                        player_points += int(set_score_parts[1])
                        opponent_points += int(set_score_parts[0])
        points_won.append(player_points)
        points_lost.append(opponent_points)
    matches_data['Sets Won'] = points_won
    matches_data['Sets Lost'] = points_lost
    return matches_data


def is_winner(tennis_match):
    stripped_winner = tennis_match['Winner'].strip()
    stripped_player = tennis_match['player'].strip()
    return stripped_winner.lower() in stripped_player.lower()


def find_matching_player_name(player_name):
    players = pd.read_csv(csv_file)
    for player in players['name']:
        if all(part.lower() in player.lower() for part in player_name.split()):
            return player
    return player_name


def get_correct_fighter_names(past_matches):
    past_matches['Winner'] = past_matches['Winner'].apply(
        lambda x: find_matching_player_name(x) if pd.notnull(x) else x)
    past_matches['Loser'] = past_matches['Loser'].apply(lambda x: find_matching_player_name(x) if pd.notnull(x) else x)
    for index, row in past_matches.iterrows():
        if sum(1 for c in row['Winner'] if c.isupper()) > 1 and ' ' not in row['Winner']:
            past_matches.at[index, 'Winner'] = add_space_in_name(row['Winner'])
        if sum(1 for c in row['Loser'] if c.isupper()) > 1 and ' ' not in row['Loser']:
            past_matches.at[index, 'Loser'] = add_space_in_name(row['Loser'])
    return past_matches


def add_space_in_name(name):
    return ''.join([' ' + char if char.isupper() else char for char in name]).lstrip()


def add_result_column(past_matches):
    past_matches['Result'] = 'W'
    past_matches = past_matches.sample(frac=1, random_state=42).reset_index(drop=True)
    swap_indices = np.random.choice([True, False], size=len(past_matches))
    # rename columns Winner and Loser to Player1 and Player2
    past_matches = past_matches.rename(columns={'Winner': 'Player1', 'Loser': 'Player2'})
    past_matches.loc[swap_indices, ['Player1', 'Player2']] = past_matches.loc[
        swap_indices, ['Player2', 'Player1']].values
    past_matches.loc[swap_indices, 'Result'] = 'L'
    return past_matches
