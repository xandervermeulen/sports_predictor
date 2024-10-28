import pandas as pd

from config.db_config import db
from ufc_fights.domain.Event import Event
from ufc_fights.webservice_helper_functions.data_collectors.events_data_collector import get_events


def get_events_data(isPast):
    events = get_events(isPast)
    events.columns = ['event', 'URL', 'date', 'location']
    events.date = pd.to_datetime(events.date, format='%B %d, %Y')
    events.date = events.date.dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    return pd.DataFrame(events)


def check_duplicate_event(event_name):
    existing_event = Event.query.filter_by(event=event_name).first()
    return existing_event
