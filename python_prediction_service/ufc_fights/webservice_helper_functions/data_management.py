from config.db_config import db
from ufc_fights.domain.Event import Event
from ufc_fights.domain.Fight import Fight
from ufc_fights.webservice_helper_functions.data_collectors.fights_data_collector import get_past_fights_results, \
    get_upcoming_fights_prediction
from ufc_fights.webservice_helper_functions.helper_functions.fights_helper import update_all_fights, \
    add_fights_to_db
from ufc_fights.webservice_helper_functions.managers.DataManager import dm
from ufc_fights.webservice_helper_functions.managers.DatabaseManager import dbm
from ufc_fights.webservice_helper_functions.helper_functions.event_helper import get_events_data, check_duplicate_event
from ufc_fights.webservice_helper_functions.data_collectors.fighter_data_collector import get_fighter_data
from ufc_fights.webservice_helper_functions.helper_functions.fighter_helper import check_duplicate_fighter
from ufc_fights.webservice_helper_functions.helper_functions.prediction_helper import predict_fights, prepare_fantasy_fight_structure


def parse_events_to_db(isPast):
    events = get_events_data(isPast)
    events.drop(columns=['URL'], inplace=True)
    for index, row in events.iterrows():
        existing_event = check_duplicate_event(row[0])
        if existing_event:  # update event
            existing_event.parameter1 = row[1]
            existing_event.parameter2 = row[2]
            existing_event.is_past = isPast
        else:
            new_event = Event(row[0], row[1], row[2], isPast)
            dbm.session_add(new_event)
    dbm.commit()


def parse_fighters_to_db():
    new_fighters = []
    """  root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    csv_file = os.path.join(root_dir, os.getenv('PROCESSED_DATA_DIR'), os.getenv('FIGHTER_DETAILS_FILE'))
    fighters = pd.read_csv(csv_file) 
"""
    fighters = get_fighter_data()
    for index, row in fighters.iterrows():
        if not check_duplicate_fighter(row[1]):
            new_fighter = dm.create_fighter_entity(row)
            new_fighters.append(new_fighter)
    dbm.add_fighters_to_db(new_fighters)


def parse_fights_to_db():
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    csv_file = os.path.join(root_dir, os.getenv('PROCESSED_DATA_DIR'), os.getenv('PAST_FIGHTS_PREDICTIONS_DIR'),
                            os.getenv('PAST_FIGHTS_PREDICTIONS_FILE'))
    predictions = pd.read_csv(csv_file)
    """
    fights, events = get_past_fights_results()
    update_all_fights(fights, events)


def parse_upcoming_fights_to_db():
    fights = get_upcoming_fights_prediction()
    add_fights_to_db(fights)


def do_fantasy_fight(fighter1, fighter2):
    formatted_fight = prepare_fantasy_fight_structure(fighter1, fighter2)
    prediction = predict_fights(formatted_fight)
    new_fight = Fight(prediction.event.values[0], prediction.fighter1.values[0],
                      prediction.fighter2.values[0], prediction.outcome_predicted.values[0],
                      prediction['W/L'].values[0])
    return new_fight
