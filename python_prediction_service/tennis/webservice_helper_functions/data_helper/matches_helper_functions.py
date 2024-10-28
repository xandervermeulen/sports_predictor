import datetime

from tennis.domain.Match import Match, PastMatch
from tennis.webservice_helper_functions.formatting_helper.matches_data_converter import convert_past_matches_data
from tennis.webservice_helper_functions.managers.DataManager import dm
from tennis.webservice_helper_functions.prediction_helper.matches_predictions import do_predictions_on_upcoming_matches
from tennis.webservice_helper_functions.scraper_helper.matches_scraper import scrape_all_matches
from tennis.webservice_helper_functions.scraper_helper.tournament_scraper import scrape_tennis_tournaments_and_matches
from ufc_fights.webservice_helper_functions.managers.DatabaseManager import dbm


def convert_to_match_objects(matches_data):
    matches = []
    for index, row in matches_data.iterrows():
        match_date = datetime.datetime.strptime(row['Date'], '%d‑%b‑%Y').date()
        match = Match(row['Event'], row['player1'], row['player2'], match_date, row['Accuracy'], row['Prediction'])
        matches.append(match)
    return matches


def get_upcoming_matches_data():
    all_matches, upcoming_matches = scrape_all_matches()
    _, _, upcoming_matches, _ = scrape_tennis_tournaments_and_matches(all_matches, upcoming_matches)
    if not upcoming_matches.empty:
        upcoming_matches = do_predictions_on_upcoming_matches(upcoming_matches)
        upcoming_matches = convert_to_match_objects(upcoming_matches)
    return upcoming_matches


def get_all_past_matches():
    all_matches, _ = scrape_all_matches()
    all_matches = convert_past_matches_data(all_matches)
    all_matches = all_matches[['Date', 'Player1', 'Player2', 'Surface', 'Result', 'Tournament']]
    all_matches = convert_to_past_match_objects(all_matches)
    return all_matches


def convert_to_past_match_objects(matches_data):
    matches = []
    for index, row in matches_data.iterrows():
        match_date = datetime.datetime.strptime(row['Date'], '%d‑%b‑%Y').date()
        exists = dm.get_upcoming_match_by_players_and_tournament(row['Player1'], row['Player2'], row['Tournament'])
        if exists:
            exists.ActualOutcome = row['Result']
            dbm.commit()
        else:
            match = PastMatch(row['Tournament'], row['Player1'], row['Player2'], match_date, 0, 0, row['Result'])
            matches.append(match)
    return matches
