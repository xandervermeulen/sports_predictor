import os

import pandas as pd
import ufc_fights.data.data_collector.scrape_ufc_stats_library as LIB
import yaml

from ufc_fights.webservice_helper_functions.helper_functions.fighter_helper import prepare_and_combine_datasets


def get_fight_result_and_stats(urls, config):
    all_fight_results_df = pd.DataFrame(columns=config['fight_results_column_names'])
    all_fight_stats_df = pd.DataFrame(columns=config['fight_stats_column_names'])
    print('Getting fight results and stats')
    for idx, url in enumerate(urls):
        soup = LIB.get_soup(url)
        fight_results_df, fight_stats_df = LIB.parse_organise_fight_results_and_stats(
            soup,
            url,
            config['fight_results_column_names'],
            config['totals_column_names'],
            config['significant_strikes_column_names']
        )
        all_fight_results_df = pd.concat([all_fight_results_df, fight_results_df])
        # Concat fight stats
        all_fight_stats_df = pd.concat([all_fight_stats_df, fight_stats_df])
        # Print progress information
        print(f"Processed {idx + 1} out of {len(urls)} URLs", end='\r')

    print('\nReturning fight results and stats')
    return all_fight_results_df, all_fight_stats_df


def get_fighter_data():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(current_dir)
    config = yaml.safe_load(open('../ufc_stats_config.yaml'))
    events_url = os.getenv('PAST_EVENTS_URL')
    soup = LIB.get_soup(events_url)
    all_event_details = LIB.parse_event_details(soup)
    # select the first 10
    list_of_event_urls = all_event_details['URL']
    print('Getting list of fight details urls')
    # create empty dataframe
    list_of_fight_details_urls = get_list_of_fight_details_urls(list_of_event_urls, config)
    results_df, stats_df = get_fight_result_and_stats(list_of_fight_details_urls, config)
    all_data = format_all_fighter_data(results_df, stats_df, config)
    return all_data


def get_list_of_fight_details_urls(event_urls, config):
    all_fight_details_df = pd.DataFrame(columns=config['fight_details_column_names'])
    for idx, url in enumerate(event_urls):
        # get soup
        soup = LIB.get_soup(url)
        # parse fight links
        fight_details_df = LIB.parse_fight_details(soup)
        # concat fight details
        all_fight_details_df = pd.concat([all_fight_details_df, fight_details_df])
        # Print progress information
        print(f"Processed {idx + 1} out of {len(event_urls)} URLs", end='\r')
    print('\nReturning list of fight details urls')
    return all_fight_details_df['URL']


def get_fighter_tott_data(config):
    list_of_alphabetical_urls = LIB.generate_alphabetical_urls()
    all_fighter_details_df = pd.DataFrame()
    print('Getting fighter tale of the tape data')
    for idx, url in enumerate(list_of_alphabetical_urls):
        print(f"Processed {idx + 1} out of {len(list_of_alphabetical_urls)} URLs", end='\r')
        # Get soup
        soup = LIB.get_soup(url)
        # Parse fighter details
        fighter_details_df = LIB.parse_fighter_details(soup, config['fighter_details_column_names'])
        # Concat fighter_details_df to all_fighter_details_df
        all_fighter_details_df = pd.concat([all_fighter_details_df, fighter_details_df])
        # Print progress information
    print('Finished getting fighter details')
    list_of_fighter_urls = list(all_fighter_details_df['URL'])
    all_fighter_tott_df = pd.DataFrame(columns=config['fighter_tott_column_names'])

    print('Getting fighter tale of the tape data 2')
    for idx, url in enumerate(list_of_fighter_urls):
        print(f"Processed {idx + 1} out of {len(list_of_fighter_urls)} URLs", end='\r')
        # Get soup
        soup = LIB.get_soup(url)
        # Parse fighter tale of the tape
        fighter_tott = LIB.parse_fighter_tott(soup)
        # Organise fighter tale of the tape
        fighter_tott_df = LIB.organise_fighter_tott(fighter_tott, config['fighter_tott_column_names'], url)
        # Concat fighter
        all_fighter_tott_df = pd.concat([all_fighter_tott_df, fighter_tott_df])
        # Print progress information

    print('\nReturning fighter tott data')
    return all_fighter_tott_df


def format_all_fighter_data(results_df, stats_df, config):
    fighter_tott = get_fighter_tott_data(config)
    all_data = prepare_and_combine_datasets(results_df, stats_df, fighter_tott)
    return all_data
