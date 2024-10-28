import datetime

from ufc.data_collector.old_tools.ufc_stats import get_fighter, get_event, get_upcoming_events


def get_event_date(event_details):
    return event_details['date']


def is_past_event(event_details):
    # '2024-05-05'
    date_str = event_details['date']
    year = int(date_str.split('-')[0])
    month = int(date_str.split('-')[1])
    day = int(date_str.split('-')[2])
    date_obj = datetime.date(year, month, day)
    return date_obj < datetime.date.today()


events = get_upcoming_events()

print("upcoming events")
for event in events:
    try:
        print(event)
        print("Event Info:")
        print(get_event(event, is_past_event(get_event(event))))
        fights = get_event(event, False)['fights']
        for fight in fights:
            print("Fight Info:")
            print(fight)
            name_red_corner = fight['red corner']['name']
            name_blue_corner = fight['blue corner']['name']
            print("Fighter Info:")
            print(get_fighter(name_red_corner))
            print(get_fighter(name_blue_corner))
            print()
    except Exception as e:
        print("Error: ", e)
        continue
