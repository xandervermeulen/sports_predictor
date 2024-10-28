import os
import re

import pandas as pd

from tennis.webservice_helper_functions.formatting_helper.tournament_formatting import format_event

headers = {
    "Accept": os.getenv("HEADERS_ACCEPT"),
    "User-Agent": os.getenv("HEADERS_USER_AGENT")
}

player_file = os.getenv('PLAYER_FILE')


def process_dates(upcoming_matches):
    upcoming_matches['Date'] = upcoming_matches['Date'].str.replace('‑', '-')
    # Convert the 'Date' column to datetime format
    upcoming_matches['Date'] = pd.to_datetime(upcoming_matches['Date'], format='%d-%b-%Y')
    upcoming_matches['date_of_birth1'] = pd.to_datetime(upcoming_matches['date_of_birth1'])
    upcoming_matches['date_of_birth2'] = pd.to_datetime(upcoming_matches['date_of_birth2'])
    upcoming_matches['age1'] = (upcoming_matches['Date'] - upcoming_matches['date_of_birth1']).dt.days
    upcoming_matches['age2'] = (upcoming_matches['Date'] - upcoming_matches['date_of_birth2']).dt.days
    upcoming_matches = upcoming_matches.drop(columns=['Date', 'date_of_birth1', 'date_of_birth2'])
    upcoming_matches = upcoming_matches.dropna()
    return upcoming_matches


def rearrange_columns(upcoming_matches, is_past=False):
    cols = []
    if is_past:
        cols = ['ActualOutcome', 'TournamentName']
    upcoming_matches = upcoming_matches[
        ['player_id1', 'age1', 'Ranking at that time1', 'Opponent Ranking at that time1', 'Double Fault Ratio1',
         'First Serve Percentage1', 'First Serve Points Won1', 'Break Points Won1', 'Sets Won1', 'Sets Lost1',
         'Total time1', 'player_id2', 'age2', 'Ranking at that time2', 'Opponent Ranking at that time2',
         'Double Fault Ratio2', 'First Serve Percentage2', 'First Serve Points Won2', 'Break Points Won2', 'Sets Won2',
         'Sets Lost2', 'Total time2', 'Surface'] + cols]
    return upcoming_matches


def format_surface(upcoming_matches):
    surfaces = upcoming_matches['Surface'].unique()
    surface_mapping = {surface: index + 1 for index, surface in enumerate(surfaces)}
    upcoming_matches['Surface'] = upcoming_matches['Surface'].map(surface_mapping)
    return upcoming_matches


def parse_match_row(row):
    cells = row.find_all('td')
    tournament_link = cells[1].find('a')['href'] if cells[1].find('a') else None
    return {
        'Date': cells[0].text.strip(),
        'Location': cells[1].text.strip(),
        'Tournament_Url': tournament_link,
        'Surface': cells[2].text.strip(),
        'Round in Tournament': cells[3].text.strip(),
        'Ranking at that time': cells[4].text.strip(),
        'Opponent Ranking at that time': cells[5].text.strip(),
        'Result': cells[6].text.strip(),
        'Set Scores': cells[7].text.strip(),
        'Dominance Ratio': cells[9].text.strip(),
        'Ace Ratio': cells[10].text.strip(),
        'Double Fault Ratio': cells[11].text.strip(),
        'First Serve Percentage': cells[12].text.strip(),
        'First Serve Points Won': cells[13].text.strip(),
        'Second Serve Points Won': cells[14].text.strip(),
        'Break Points Saved': cells[15].text.strip(),
        'Time': cells[16].text.strip()
    }


def format_upcoming_tennis_matches(upcoming_matches_info, events_df):
    upcoming_matches_info['Tournament'] = upcoming_matches_info['Tournament'].str.replace(' CH', '')
    names = upcoming_matches_info['Results'].str.split('vs')
    names = names.apply(lambda x: [re.sub(r'\[.*?]', '', re.sub(r'\(.*?\)', '', name)).strip() for name in x])
    upcoming_matches_info['player1'] = names.apply(lambda x: x[0])
    upcoming_matches_info['player2'] = names.apply(lambda x: x[1])
    upcoming_matches_info['player1'] = upcoming_matches_info['player']
    upcoming_matches_info = upcoming_matches_info.drop(columns=['player', 'Results'])
    upcoming_matches_info = upcoming_matches_info[['Tournament', 'Surface', 'Date', 'player1', 'player2']]
    upcoming_matches_info = add_event_to_matches(upcoming_matches_info, events_df)

    return upcoming_matches_info


def convert_link_to_event_name(all_matches):
    all_matches['Tournament'] = all_matches['Tournament_Url'].str.split('=').str[1]
    return all_matches


def add_event_to_matches(upcoming_matches_info, events_df):
    merged_df = upcoming_matches_info.merge(
        events_df,
        left_on=['player1', 'player2'],
        right_on=['Player 1', 'Player 2'],
        how='inner'
    )
    merged_df = merged_df.rename(columns={'Tournament': 'Location', 'Event Name': 'Event'})
    merged_df['Event'] = merged_df['Event'].astype(str)
    merged_df['Event'] = merged_df['Event'].apply(format_event)
    merged_df = merged_df.drop(columns=['Player 1', 'Player 2'])
    merged_df = merged_df.dropna()
    return merged_df