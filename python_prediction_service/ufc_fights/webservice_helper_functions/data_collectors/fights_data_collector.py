import os

import pandas as pd
import yaml

import ufc_fights.data.data_collector.scrape_ufc_stats_library as LIB
from ufc_fights.webservice_helper_functions.helper_functions.event_helper import get_events, get_events_data
from ufc_fights.webservice_helper_functions.helper_functions.prediction_helper import predict_fights, format_fights


def get_past_fights_results():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(current_dir)
    config = yaml.safe_load(open('../ufc_stats_config.yaml'))
    events = get_events(True)
    urls = events['URL']
    list_of_fight_details_urls = get_fight_details_urls(urls)
    total_urls = len(list_of_fight_details_urls)
    all_fight_results_dfs = []
    idx = 0
    for url in list_of_fight_details_urls:
        print(f"Processing {idx + 1}/{total_urls} ({((idx + 1) / total_urls) * 100:.2f}% done)")
        soup = LIB.get_soup(url)
        fight_results_df, fight_stats_df = LIB.parse_organise_fight_results_and_stats(
            soup,
            url,
            config['fight_results_column_names'],
            config['totals_column_names'],
            config['significant_strikes_column_names']
        )
        all_fight_results_dfs.append(fight_results_df)
        idx += 1

    all_fight_results_df = pd.concat(all_fight_results_dfs)

    return all_fight_results_df, events


def get_upcoming_fights_prediction():
    event_details_df = get_events_data(isPast=False)
    combined_fight_details_df = pd.DataFrame()
    for url in event_details_df['URL']:
        soup = LIB.get_soup(url)
        fight_details_df = LIB.parse_upcoming_fight_details(soup)
        combined_fight_details_df = pd.concat([combined_fight_details_df, fight_details_df], ignore_index=True)
    formatted_fights = format_fights(combined_fight_details_df, event_details_df)
    fight_predictions = predict_fights(formatted_fights)
    return fight_predictions


def get_fight_details_urls(list_of_event_urls):
    all_fight_details_dfs = [LIB.parse_fight_details(LIB.get_soup(url)) for url in list_of_event_urls]
    all_fight_details_df = pd.concat(all_fight_details_dfs, ignore_index=True)
    return all_fight_details_df['URL'].tolist()
