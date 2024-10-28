from flask import Blueprint

from tennis.webservice_helper_functions.data_management import (parse_tournaments_to_db,
                                                                parse_upcoming_matches_to_db,
                                                                parse_players_to_db,
                                                                parse_matches_and_tournaments_to_db,
                                                                parse_past_matches_to_db,
                                                                predict_past_matches,
                                                                )
from tennis.webservice_helper_functions.data_helper.player_helper_functions import update_player_personal_info
from tennis.webservice_helper_functions.managers.DatabaseManager import dbm

tennis_data_api = Blueprint('tennis_data_api', __name__)


@tennis_data_api.route('/data/addAllPlayers', methods=['GET'])
def refresh_all_players():
    parse_players_to_db()
    return 'All players added to database'


@tennis_data_api.route('/data/addAllUpcomingMatches', methods=['GET'])
def refresh_all_matches():
    parse_upcoming_matches_to_db()
    return 'All matches added to database'


@tennis_data_api.route('/data/addAllPastMatches', methods=['GET'])
def refresh_all_past_matches():
    parse_past_matches_to_db()
    return 'All matches added to database'


@tennis_data_api.route('/data/addAllTournaments', methods=['GET'])
def refresh_all_tournaments():
    parse_tournaments_to_db()
    return 'All tournaments added to database'


@tennis_data_api.route('/data/deleteAllPlayers', methods=['GET'])
def remove_all_players():
    dbm.delete_all_players()
    return 'All players deleted'


@tennis_data_api.route('/data/deleteAllMatches', methods=['GET'])
def remove_all_matches():
    dbm.delete_all_matches()
    return 'All matches deleted'


@tennis_data_api.route('/data/deleteAllPastMatches', methods=['GET'])
def remove_all_past_matches():
    dbm.delete_all_past_matches()
    return 'All matches deleted'


@tennis_data_api.route('/data/deleteAllTournaments', methods=['GET'])
def remove_all_tournaments():
    dbm.delete_all_tournaments()
    return 'All tournaments deleted'


@tennis_data_api.route('/data/refreshAllData', methods=['GET'])
def refresh_upcoming_matches_and_tournaments():
    parse_matches_and_tournaments_to_db()
    return 'Upcoming matches and tournaments and player stats are updated in the database'


@tennis_data_api.route('/data/refreshAllPersonalInfo', methods=['GET'])
def refresh_all_personal_info():
    update_player_personal_info()
    return 'All players personal info updated'


@tennis_data_api.route('/data/predictPastMatches', methods=['GET'])
def add_prediction_to_past_matches():
    message = predict_past_matches()
    return message
