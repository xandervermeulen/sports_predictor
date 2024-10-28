import os

import joblib
import numpy as np
import pandas as pd

def add_accuracy(model, X_scaled, data):
    y_pred_proba = model.predict_proba(X_scaled)
    probabilities = y_pred_proba / y_pred_proba.sum(axis=1)[:, np.newaxis]
    # select the last col of the probabilities
    probabilities = probabilities[:, -1]
    data['Accuracy'] = probabilities
    return data


def predict_fights(fights):
    model_name = os.getenv('UFC_NN_MODEL')
    scaler_name = os.getenv('UFC_SCALER_PATH')
    model = read_model(model_name)
    scaler = read_model(scaler_name)
    fighter_details = read_fighter_details()
    data = prepare_dataset_for_prediction(fights, fighter_details)
    if data.empty:
        return None
    X_scaled = scaler.transform(data)
    pred = model.predict(X_scaled)
    data['prediction'] = pred
    final_df = add_accuracy(model, X_scaled, data)
    final_df = prepare_data_to_return(final_df, fighter_details, fights)
    return final_df


def read_fighter_details():  # TODO change to read from db
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    csv_file = os.path.join(root_dir, os.getenv('DATA_DIR'), os.getenv('PROCESSED_DATA_DIR'),
                            os.getenv('FIGHTER_DETAILS_FILE'))

    if os.path.exists(csv_file):
        # first column is the index
        fighter_details = pd.read_csv(csv_file, sep=',', index_col=0)
        return fighter_details
    else:
        print("File not found")
        return None


def read_model(file_name):
    # with os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) as root_dir:
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    model_file = os.path.join(root_dir, os.getenv('MODELS_DIR'), file_name)
    if os.path.exists(model_file):
        model = joblib.load(model_file)
        return model
    else:
        print("File not found")
        return None


def prepare_fantasy_fight_structure(fighter1, fighter2):
    column_names = ['event', 'fighter1', 'fighter2']
    formatted_fight = pd.DataFrame(columns=column_names)
    formatted_fight = pd.concat(
        [formatted_fight, pd.DataFrame({'event': ['Fantasy Fight'], 'fighter1': [fighter1], 'fighter2': [fighter2]})])
    return formatted_fight


def format_fights(fights, events):
    merged_df = fights.merge(events, left_on='EVENT', right_on='event', how='inner')
    # Split the 'bout' column into fighter1 and fighter2 columns
    merged_df[['fighter1', 'fighter2']] = merged_df['BOUT'].str.split(' vs. ', expand=True)
    # Select the desired columns and rename them
    formatted_df = merged_df[['EVENT', 'fighter1', 'fighter2']]
    formatted_df.rename(columns={'EVENT': 'event', 'date': 'event_date', 'location': 'event_location'}, inplace=True)
    # only select the rows with a unique fighter1 and fighter2 combination
    formatted_df = formatted_df.drop_duplicates(subset=['fighter1', 'fighter2'])
    return formatted_df


def prepare_dataset_for_prediction(fights, fighter_details):
    merged_fights = pd.merge(fights, fighter_details, left_on='fighter1', right_on='FIGHTER')
    merged_fights = pd.merge(merged_fights, fighter_details, left_on='fighter2', right_on='FIGHTER',
                             suffixes=('_1', '_2'))
    # Selecting necessary columns
    merged_fights = merged_fights[[
        'fighter_index_1', 'Height_CM_1', 'Weight_KG_1', 'AVG_KD_1', 'AVG_SUB_ATT_1', 'AVG_TD_Percentage_1',
        'AVG_Significant_Strike_Percentage_1', 'AVG_TOTAL_STR_1', 'AVG_ROUND_1', 'AVG_CTRL_SECONDS_1',
        'total_wins_1', 'total_losses_1', 'total_draws_1', 'Win_Percentage_1', 'Reach_Conv_1',
        'fighter_index_2', 'Height_CM_2', 'Weight_KG_2', 'AVG_KD_2', 'AVG_SUB_ATT_2', 'AVG_TD_Percentage_2',
        'AVG_Significant_Strike_Percentage_2', 'AVG_TOTAL_STR_2', 'AVG_ROUND_2', 'AVG_CTRL_SECONDS_2',
        'total_wins_2', 'total_losses_2', 'total_draws_2', 'Win_Percentage_2', 'Reach_Conv_2'
    ]]
    merged_fights.columns = ['fighter1_index', 'height1', 'weight_kg1', 'avg_kd1', 'avg_sub_att1', 'avg_td_percentage1',
                             'avg_significant_strike_percentage1', 'avg_total_str1', 'avg_round1', 'avg_ctrl_seconds1',
                             'total_wins1', 'total_losses1', 'total_draws1', 'win_percentage1', 'reach_conv1',
                             'fighter2_index', 'height2', 'weight_kg2', 'avg_kd2', 'avg_sub_att2', 'avg_td_percentage2',
                             'avg_significant_strike_percentage2', 'avg_total_str2', 'avg_round2', 'avg_ctrl_seconds2',
                             'total_wins2', 'total_losses2', 'total_draws2', 'win_percentage2', 'reach_conv2']
    return merged_fights

def prepare_data_to_return(data, fighter_details, fights):
    data = pd.merge(data, fighter_details, left_on='fighter1_index', right_on='fighter_index')
    data = pd.merge(data, fighter_details, left_on='fighter2_index', right_on='fighter_index', suffixes=('_1', '_2'))
    # drop all rows except fighter_1, fighter_2, prediction
    data = data[['FIGHTER_1', 'FIGHTER_2', 'prediction', 'Accuracy']]
    # join data with fights so i get the event name, fighter1, fighter2, prediction
    data = pd.merge(data, fights, left_on=['FIGHTER_1', 'FIGHTER_2'], right_on=['fighter1', 'fighter2'])
    # drop all columns except event, fighter1, fighter2, prediction
    data = data[['event', 'fighter1', 'fighter2', 'prediction', 'Accuracy']]
    columns = ['event', 'fighter1', 'fighter2', 'outcome_predicted', 'W/L']
    data.columns = columns
    return data
