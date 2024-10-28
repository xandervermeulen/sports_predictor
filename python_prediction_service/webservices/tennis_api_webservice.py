from flask import Blueprint, request

from tennis.webservice_helper_functions.managers.DataManager import dm

tennis_api = Blueprint('tennis_api', __name__)


@tennis_api.route('/service/getAllPlayers', methods=['GET'])
def get_all_players():
    return dm.get_all_players_json()


@tennis_api.route('/service/getAllMatches', methods=['GET'])
def get_all_matches():
    return dm.get_all_upcoming_matches()


@tennis_api.route('/service/getAllTournaments', methods=['GET'])
def get_all_tournaments():
    return dm.get_all_tournaments_json()


@tennis_api.route('/service/getAllPastMatches', methods=['GET'])
def get_all_past_matches():
    return dm.get_all_past_matches_json()


@tennis_api.route('/service/getAllMatchesFromEvent', methods=['GET'])
def get_all_matches_from_event():
    tournament_name = request.args.get('tournament_name')
    return dm.get_all_matches_from_events(tournament_name)


@tennis_api.route('/service/getAllPastMatchesFromEvent', methods=['GET'])
def get_all_past_matches_from_event():
    tournament_name = request.args.get('tournament_name')
    return dm.get_all_past_matches_from_events(tournament_name)


@tennis_api.route('/service/getAllUpcomingTournaments', methods=['GET'])
def get_all_upcoming_tournaments():
    return dm.get_all_upcoming_tournaments()


@tennis_api.route('/service/getAllPastTournaments', methods=['GET'])
def get_all_past_tournaments():
    return dm.get_all_past_tournaments()
