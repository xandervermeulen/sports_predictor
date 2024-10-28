import os

import numpy as np
import pandas as pd
import yaml
from pyspark.ml.feature import StringIndexer
from sklearn.impute import KNNImputer

from ufc_fights.domain.Fighter import Fighter


def format_fighter_data(data):
    data = data.iloc[:, 1:]
    data['total_wins'] = data['total_wins'].astype(int)
    data['total_losses'] = data['total_losses'].astype(int)
    data['total_draws'] = data['total_draws'].astype(int)
    return data


def check_duplicate_fighter(fighter_name):
    existing_fighter = Fighter.query.filter_by(fighter=fighter_name).first()
    if existing_fighter:
        return True
    return False


def replace_non_numeric_with_nan(df, column_name):
    for x in df[column_name].unique():
        try:
            float(x)
        except ValueError or TypeError:
            df.loc[df[column_name] == x, column_name] = np.nan
    return df


def replace_all_non_numeric_values(matches_data_filtered):
    columns_to_convert = ["KD", "SUB.ATT", "TD_Percentage", "SIG.STR. %"]
    for column in columns_to_convert:
        matches_data_filtered = replace_non_numeric_with_nan(matches_data_filtered, column)
        matches_data_filtered = convert_column_to_float(matches_data_filtered, column)
    matches_data_filtered = matches_data_filtered.dropna()
    return matches_data_filtered


def convert_column_to_float(df, column_name):
    df[column_name] = df[column_name].astype(float)
    return df


def prepare_and_combine_datasets(results_df, stats_df, fighter_tott):
    stats_df = stats_df.rename(columns={"TD %": "TD_Percentage",
                                        "SUB. ATT": "SUB_ATT",
                                        "SIG. STR %": "Significant_Strike_Percentage"})
    # Merge fighter_info and fight_stats DataFrames
    updated_fighter_info = pd.merge(fighter_tott, stats_df, on="FIGHTER", how="inner")
   # updated_fighter_info['TD %'] = updated_fighter_info['TD %'].str.rstrip('%')
   #  updated_fighter_info['SIG. STR %'] = updated_fighter_info['SIG. STR %'].str.rstrip('%')
    updated_fighter_info = replace_all_non_numeric_values(updated_fighter_info)
    # Perform SQL-like operations on Pandas DataFrames
    # TODO lamba is not correct, cant convert string to float!
    updated_fighter_info = updated_fighter_info.groupby(["FIGHTER", "HEIGHT", "WEIGHT", "REACH"]).agg({
        "KD": "mean",
        "SUB.ATT": "mean",
        "TD_Percentage": "mean",
        "SIG.STR. %": "mean"
    }).reset_index()

    # Convert fight_results DataFrame to Pandas
    fight_results = results_df["BOUT"].str.split(' vs. ', expand=True)
    fight_results.columns = ['fighter1', 'fighter2']

    # Create the outcome column based on existing data
    fight_results['outcome'] = results_df['OUTCOME']

    # Add Accuracy column to fight_results DataFrame
    fight_results['Accuracy'] = 1

    # Perform SQL-like operations on Pandas DataFrames
    win_loss_percentage = fight_results.copy()
    win_loss_percentage['wins'] = win_loss_percentage['outcome'].apply(lambda x: 1 if x == 'W/L' else 0)
    win_loss_percentage['losses'] = win_loss_percentage['outcome'].apply(lambda x: 1 if x == 'L/W' else 0)
    win_loss_percentage['draws'] = win_loss_percentage['outcome'].apply(lambda x: 1 if x == 'D' else 0)
    win_loss_percentage = win_loss_percentage.groupby('fighter1').agg({
        'wins': 'sum',
        'losses': 'sum',
        'draws': 'sum'
    }).reset_index()
    win_loss_percentage['Win_Percentage'] = win_loss_percentage['wins'] / (
            win_loss_percentage['wins'] + win_loss_percentage['losses'] + win_loss_percentage['draws']) * 100

    # Merge DataFrames
    joined_df = pd.merge(updated_fighter_info, win_loss_percentage, left_on="FIGHTER", right_on="fighter1", how="inner")

    # Perform data conversions and cleanup
    joined_df['Height_CM'] = (joined_df['HEIGHT'].str.split("'").str[0].astype(int) * 30.48 +
                              joined_df['HEIGHT'].str.split("'").str[1].str.replace('"', '').astype(int) * 2.54)
    joined_df['Reach_Conv'] = joined_df['REACH'].str.replace('"', '').astype(int)
    joined_df['Weight_KG'] = joined_df['WEIGHT'].str.replace(' lbs.', '').astype(int) * 0.453592
    joined_df = joined_df.drop(columns=["HEIGHT", "WEIGHT", "REACH", "fighter1"])
    # print the size of the DataFrame
    print(f'Joined DataFrame shape: {joined_df.shape}')
    # Impute missing values and index data
    converted_height_df_imputed = impute_all_data(joined_df)
    indexed_df = index_all_data(converted_height_df_imputed)
    return indexed_df


def impute_all_data(converted_height_df):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(current_dir)
    config = yaml.safe_load(open('../ufc_stats_config.yaml'))

    numerical_cols = config['all_fighter_stats_column_names']

    imputer = KNNImputer(n_neighbors=5)
    converted_height_df_pd_imputed = imputer.fit_transform(converted_height_df)
    converted_height_df[numerical_cols] = converted_height_df_pd_imputed
    return converted_height_df


def index_all_data(converted_height_df):
    indexer = StringIndexer(inputCol="FIGHTER", outputCol="fighter_index")
    indexed = indexer.fit(converted_height_df).transform(converted_height_df)
    return indexed
