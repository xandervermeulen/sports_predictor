from flask import Blueprint

from ufc_fights.webservice_helper_functions.managers.DatabaseManager import dbm
from ufc_fights.webservice_helper_functions.data_management import parse_events_to_db, parse_fighters_to_db, \
    parse_fights_to_db, parse_upcoming_fights_to_db

ufc_data_api = Blueprint('ufc_data_api', __name__)


@ufc_data_api.route('/data/addAllPastEvents', methods=['GET'])
def refresh_past_events():
    parse_events_to_db(isPast=True)
    return 'Past events added to database'


@ufc_data_api.route('/data/addAllUpcomingEvents', methods=['GET'])
def refresh_upcoming_events():
    parse_events_to_db(isPast=False)
    return 'Upcoming events added to database'


@ufc_data_api.route('/data/addAllEvents', methods=['GET'])
def refresh_all_events():
    remove_all_events()
    parse_events_to_db(isPast=False)
    parse_events_to_db(isPast=True)
    return 'All events added to database'


@ufc_data_api.route('/data/deleteAllEvents', methods=['GET'])
def remove_all_events():
    dbm.delete_all_events()
    return 'All events deleted'


@ufc_data_api.route('/data/refreshAllFighters', methods=['GET'])
def refresh_all_fighters():
    parse_fighters_to_db()
    return 'All fighters added to database'


@ufc_data_api.route('/data/addAllPastFights', methods=['GET'])
def refresh_all_past_fights():
    parse_fights_to_db()
    return 'All fights added to database'


@ufc_data_api.route('/data/updateAllUpcomingFights', methods=['GET'])
def refresh_all_upcoming_fights():
    parse_upcoming_fights_to_db()
    return 'All fighters added to database'


@ufc_data_api.route('/data/deleteAllUpcomingFights', methods=['GET'])
def remove_all_upcoming_fights():
    dbm.delete_all_upcoming_fights()
    return 'All fights deleted'


@ufc_data_api.route('/data/deleteAllFights', methods=['GET'])
def remove_all_fights():
    dbm.delete_all_fights()
    return 'All fights deleted'


@ufc_data_api.route('/data/deleteAllFighters', methods=['GET'])
def remove_all_fighters():
    dbm.delete_all_fighters()
    return 'All fighters deleted'


@ufc_data_api.route('/data/refreshAllImages', methods=['GET'])
def refresh_all_images():
    dbm.refresh_fighter_images()
    return 'All images added'


@ufc_data_api.route('/data/addDefaultImages', methods=['GET'])
def add_fighter_images():
    dbm.add_default_image_to_fighters()
    return 'Images added'
