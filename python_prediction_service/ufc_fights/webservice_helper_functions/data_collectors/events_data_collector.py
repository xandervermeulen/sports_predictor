import os

import ufc_fights.data.data_collector.scrape_ufc_stats_library as LIB
import importlib


def get_events(isPast):
    url = os.getenv('PAST_EVENTS_URL' if isPast else 'UPCOMING_EVENTS_URL')
    importlib.reload(LIB)
    soup = LIB.get_soup(url)
    return LIB.parse_event_details(soup) if isPast else LIB.parse_upcoming_events(soup)
