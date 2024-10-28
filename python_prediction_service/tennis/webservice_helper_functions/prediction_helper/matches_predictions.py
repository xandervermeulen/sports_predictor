import os

import joblib
import numpy as np
import pandas as pd
from sklearn.neural_network import MLPClassifier

from config.db_config import db
from tennis.domain.Tournament import Tournament
from tennis.webservice_helper_functions.data_helper.player_helper_functions import read_player_stats
from tennis.webservice_helper_functions.formatting_helper.matches_formatting import process_dates, rearrange_columns, \
    format_surface
from tennis.webservice_helper_functions.formatting_helper.player_formatting import clean_player_name, \
    clean_player_stats_names
from tennis.webservice_helper_functions.managers.DataManager import dm

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
scaler_path = os.path.join(root_dir, os.getenv('MODELS_DIR'), os.getenv('TENNIS_SCALER_PATH'))
model_path = os.path.join(root_dir, os.getenv('MODELS_DIR'), os.getenv('TENNIS_NN_MODEL_PATH'))


def read_models():
    return joblib.load(model_path), joblib.load(scaler_path)


def prepare_matches(matches, is_past=False):
    player_stats = read_player_stats()
    player_stats = clean_player_stats_names(player_stats)
    matches = matches.merge(player_stats, left_on='player1', right_on='player', how='left')
    if is_past:
        matches = matches.drop(columns=['player'])
        cols = ['Surface', 'Date', 'player1', 'player2', 'ActualOutcome', 'TournamentName']
        x = 6
    else:
        # drop the player column
        matches = matches.drop(columns=['player'])
        cols = ['Surface', 'Date', 'player1', 'player2']
        x = 4

    matches.columns = (cols
                       + [col + '1' for col in matches.columns[x:]])
    matches['player1'] = matches['player1'].astype(str)
    matches['player2'] = matches['player2'].astype(str)
    matches['Date'] = matches['Date'].astype(str)
    matches['cleaned_player2'] = matches['player2'].apply(clean_player_name)
    matches = matches.merge(player_stats, left_on='cleaned_player2', right_on='cleaned_player',
                            how='left')
    # drop the player column
    matches = matches.drop(columns=['player'])
    matches.columns = (cols + ['Ranking at that time1', 'Opponent Ranking at that time1',
                               'Dominance Ratio1', 'Ace Ratio1', 'Double Fault Ratio1',
                               'First Serve Percentage1', 'First Serve Points Won1',
                               'Second Serve Points Won1', 'round value1', 'Break Points Won1',
                               'Break Points Faced1', 'Sets Won1', 'Sets Lost1', 'Total time1',
                               'player_id1', 'date_of_birth1', 'cleaned_player1', 'cleaned_player2']
                       + [col + '2' for col in matches.columns[x + 18:]])
    return matches


def prepare_upcoming_matches(upcoming_matches):
    upcoming_matches.drop(columns=['Event', 'Location'], inplace=True)
    upcoming_matches = prepare_matches(upcoming_matches)
    return upcoming_matches


def do_predictions_on_upcoming_matches(upcoming_matches):
    all_upcoming_matches = upcoming_matches.copy()
    upcoming_matches = prepare_upcoming_matches(upcoming_matches)
    upcoming_matches = process_dates(upcoming_matches)
    upcoming_matches_stats = upcoming_matches.copy()
    upcoming_matches = rearrange_columns(upcoming_matches)
    upcoming_matches = format_surface(upcoming_matches)
    upcoming_matches_with_predictions = make_predictions_on_nn(upcoming_matches, upcoming_matches_stats,
                                                               all_upcoming_matches)
    return upcoming_matches_with_predictions


def get_surface_from_event(past_matches):
    # past_matches = past_matches.drop(columns=['ActualOutcome'])
    tournaments = dm.get_all_tournaments()
    tournament_surface_map = {tournament.Name: tournament.Surface for tournament in tournaments}
    past_matches['Surface'] = past_matches['TournamentName'].map(tournament_surface_map)
    # past_matches = past_matches.drop(columns=['TournamentName'])
    past_matches = past_matches[['Surface', 'Date', 'player1', 'player2', 'ActualOutcome', 'TournamentName']]
    past_matches['Date'] = pd.to_datetime(past_matches['Date'], format='%Y-%m-%d').dt.strftime('%d-%b-%Y')

    return past_matches


def do_predictions_on_past_matches(past_matches):
    past_matches = get_surface_from_event(past_matches)
    past_matches = prepare_matches(past_matches, is_past=True)
    past_matches = process_dates(past_matches)
    past_matches = rearrange_columns(past_matches, is_past=True)
    past_matches = format_surface(past_matches)  # all converted data to numbers
    all_data = past_matches.copy()
    X1, y1, X2, y2, X3, y3, X4, y4 = split_up_data(all_data)
    X_train_1 = pd.concat([X2, X3, X4])
    # print all rows of X_train_1 that contain non-numeric values
    print(X_train_1[~X_train_1.applymap(np.isreal).all(1)])
    y_train_1 = pd.concat([y2, y3, y4])
    X_train_2 = pd.concat([X1, X3, X4])
    y_train_2 = pd.concat([y1, y3, y4])
    X_train_3 = pd.concat([X1, X2, X4])
    y_train_3 = pd.concat([y1, y2, y4])
    X_train_4 = pd.concat([X1, X2, X3])
    y_train_4 = pd.concat([y1, y2, y3])
    pm1 = make_prediction_with_nn_past_matches(X_train_1, y_train_1, X1, y1)
    pm2 = make_prediction_with_nn_past_matches(X_train_2, y_train_2, X2, y2)
    pm3 = make_prediction_with_nn_past_matches(X_train_3, y_train_3, X3, y3)
    pm4 = make_prediction_with_nn_past_matches(X_train_4, y_train_4, X4, y4)
    past_matches_results = pd.concat([pm1, pm2, pm3, pm4])
    return past_matches_results


def make_prediction_with_nn_past_matches(X_train, y_train, X_test, y_test):
    # past_matches has the data of the full match with tournament name etc,
    # X train / y train contain 75% of the data
    # so with X test (25% of the data) we try to make predictions
    X_test_tour = X_test
    X_test = X_test.drop(columns=['TournamentName'])
    X_train = X_train.drop(columns=['TournamentName'])
    _, scaler = read_models()
    X_train_scaled = scaler.transform(X_train)
    X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns)
    X_test_scaled = scaler.transform(X_test)
    X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns)

    model = MLPClassifier(solver='sgd', random_state=42, max_iter=2000, learning_rate_init=0.1,
                          learning_rate='adaptive', hidden_layer_sizes=(150, 100, 150), alpha=0.001, activation='tanh')
    model.fit(X_train_scaled, y_train)
    print(f'NN Model score: {model.score(X_test_scaled, y_test)}')
    y_pred = model.predict(X_test_scaled)

    proba = model.predict_proba(X_test_scaled)
    outcomes = model.classes_
    proba_df = pd.DataFrame(proba, columns=outcomes)
    y_pred_df = pd.DataFrame(y_pred, columns=['Prediction'])
    y_pred_df = pd.concat([y_pred_df, proba_df], axis=1)
    y_pred_df['Accuracy'] = y_pred_df[['L', 'W']].max(axis=1)
    y_pred_df = y_pred_df.drop(columns=['L', 'W'])
    y_pred_df['Accuracy'] = y_pred_df['Accuracy'].apply(lambda x: "{:.4}".format(x))
    # add the tournament name to the df
    past_match_data = X_test_tour[['player_id1', 'player_id2', 'TournamentName']]
    past_match_data.reset_index(drop=True, inplace=True)
    past_matches = pd.concat([y_pred_df, past_match_data], axis=1)
    # concat both datasets,
    return past_matches


def make_predictions_on_nn(X, upcoming_matches_stats, all_upcoming_matches):
    model, scaler = read_models()
    X_scaled = scaler.transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=X.columns)

    y_pred = model.predict(X_scaled)
    proba = model.predict_proba(X_scaled)

    outcomes = model.classes_
    proba_df = pd.DataFrame(proba, columns=outcomes)
    y_pred_df = pd.DataFrame(y_pred, columns=['Prediction'])
    y_pred_df = pd.concat([y_pred_df, proba_df], axis=1)
    y_pred_df['Accuracy'] = y_pred_df[['L', 'W']].max(axis=1)
    y_pred_df = y_pred_df.drop(columns=['L', 'W'])
    y_pred_df['Accuracy'] = y_pred_df['Accuracy'].apply(lambda x: "{:.4}".format(x))

    upcoming_matches_stats.reset_index(drop=True, inplace=True)
    y_pred_df = pd.concat([upcoming_matches_stats, y_pred_df], axis=1)
    y_pred_df = y_pred_df[['player1', 'player2', 'Prediction', 'Accuracy']]
    y_pred_df = y_pred_df.loc[:, ~y_pred_df.columns.duplicated()]
    all_upcoming_matches = all_upcoming_matches.merge(y_pred_df, left_on=['player1', 'player2'],
                                                      right_on=['player1', 'player2'], how='left')
    all_upcoming_matches = all_upcoming_matches.dropna()
    return all_upcoming_matches[['Event', 'player1', 'player2', 'Date', 'Prediction', 'Accuracy']]


def split_up_data(past_matches):
    # split the data in 4 equal parts
    split = len(past_matches) // 4
    X1 = past_matches.iloc[:split]
    y1 = X1['ActualOutcome']
    X2 = past_matches.iloc[split:2 * split]
    y2 = X2['ActualOutcome']
    X3 = past_matches.iloc[2 * split:3 * split]
    y3 = X3['ActualOutcome']
    X4 = past_matches.iloc[3 * split:]
    y4 = X4['ActualOutcome']
    X1 = X1.drop(columns=['ActualOutcome'])
    X2 = X2.drop(columns=['ActualOutcome'])
    X3 = X3.drop(columns=['ActualOutcome'])
    X4 = X4.drop(columns=['ActualOutcome'])
    return X1, y1, X2, y2, X3, y3, X4, y4
