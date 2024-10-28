from flask import Blueprint, request

from ufc_fights.webservice_helper_functions.managers.DataManager import dm
from ufc_fights.webservice_helper_functions.data_management import do_fantasy_fight

ufc_api = Blueprint('ufc_api', __name__)


@ufc_api.route('/service/getUpFights', methods=['GET'])
def get_upcoming_fights():
    return dm.get_upcoming_fights_json()


@ufc_api.route('/service/getPastFights', methods=['GET'])
def get_past_fights():
    return dm.get_past_fights_json()


@ufc_api.route('/service/getFighterByName', methods=['GET'])
def get_fighter_by_name():
    fighter_name = request.args.get('name')
    return dm.get_fighter_by_name_json(fighter_name)


@ufc_api.route('/service/predictFight', methods=['GET'])
def predict_fantasy_fight():
    fighter_1_name = request.args.get('fighter1')
    fighter_2_name = request.args.get('fighter2')
    result = do_fantasy_fight(fighter_1_name, fighter_2_name)
    return result.convert_to_json()


@ufc_api.route('/service/getFighters', methods=['GET'])
def get_all_fighters():
    return dm.get_all_fighters_json()


@ufc_api.route('/service/getEvents', methods=['GET'])
def get_events():
    is_past = request.args.get('isPast', default=False).lower() == 'true'
    return dm.get_events(is_past)


@ufc_api.route('/service/getFightsFromEvent', methods=['GET'])
def get_fights_from_event():
    event_name = request.args.get('event')
    fights = dm.get_all_fights_from_event(event_name)
    return fights
