import pandas as pd

from tennis.webservice_helper_functions.data_helper.matches_helper_functions import get_upcoming_matches_data, \
    convert_to_match_objects, get_all_past_matches, convert_to_past_match_objects
from tennis.webservice_helper_functions.data_helper.player_helper_functions import get_players_data, \
    convert_matches_to_player_stats, convert_to_player_objects, update_player_personal_info
from tennis.webservice_helper_functions.data_helper.tournament_helper_functions import get_tournaments_data, \
    convert_to_tournament_objects
from tennis.webservice_helper_functions.formatting_helper.matches_data_converter import convert_past_matches_data
from tennis.webservice_helper_functions.managers.DataManager import dm
from tennis.webservice_helper_functions.managers.DatabaseManager import dbm
from tennis.webservice_helper_functions.prediction_helper.matches_predictions import (
    do_predictions_on_upcoming_matches, do_predictions_on_past_matches)
from tennis.webservice_helper_functions.scraper_helper.matches_scraper import scrape_all_matches
from tennis.webservice_helper_functions.scraper_helper.tournament_scraper import scrape_tennis_tournaments_and_matches


def parse_players_to_db():
    players = get_players_data()
    dbm.add_players(players)


def parse_upcoming_matches_to_db():
    matches = get_upcoming_matches_data()
    if matches:
        dbm.add_matches(matches)


def parse_tournaments_to_db():
    all_matches, upcoming_matches = scrape_all_matches()
    tournaments = get_tournaments_data(all_matches, upcoming_matches)
    dbm.add_all_tournaments(tournaments)


def parse_matches_and_tournaments_to_db():
    update_player_personal_info()
    all_matches, upcoming_matches = scrape_all_matches()
    tournaments, past_tournaments, upcoming_matches, all_matches = \
        scrape_tennis_tournaments_and_matches(all_matches, upcoming_matches)
    if tournaments:
        tournaments = convert_to_tournament_objects(tournaments, False)
        dbm.add_all_tournaments(tournaments)
    past_tournaments = convert_to_tournament_objects(past_tournaments, True)
    if upcoming_matches:
        upcoming_matches = do_predictions_on_upcoming_matches(upcoming_matches)
        upcoming_matches = convert_to_match_objects(upcoming_matches)
        dbm.add_matches(upcoming_matches)

    all_matches = convert_past_matches_data(all_matches)
    player_stats = convert_matches_to_player_stats(all_matches)
    players = convert_to_player_objects(player_stats)
    all_matches = all_matches[['Date', 'Player1', 'Player2', 'Surface', 'Result', 'Tournament']]
    all_matches = convert_to_past_match_objects(all_matches)
    dbm.add_all_tournaments(past_tournaments)
    dbm.add_past_matches(all_matches)
    dbm.add_players(players)


def parse_past_matches_to_db():
    matches = get_all_past_matches()
    dbm.add_past_matches(matches)


def predict_past_matches():
    past_matches = dm.get_all_past_matches_serialized()
    past_matches = do_predictions_on_past_matches(pd.DataFrame(past_matches))
    dbm.add_prediction_to_match(past_matches)
    return "Added predictions and accuracy"
