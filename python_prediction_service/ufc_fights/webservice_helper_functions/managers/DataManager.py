from flask import jsonify

from ufc_fights.domain.Event import Event
from ufc_fights.domain.Fight import PastFight, Fight
from ufc_fights.domain.Fighter import Fighter


class DataManager:
    @staticmethod
    def get_past_fights_json():
        past_fights = PastFight.query.filter(PastFight.actual_outcome.isnot(None)).all()
        past_fights = [fight.convert_to_json() for fight in past_fights]
        return past_fights

    @staticmethod
    def get_upcoming_fights_json():
        upcoming_fights = PastFight.query.filter(PastFight.actual_outcome.is_(None)).all()
        upcoming_fights = [fight.convert_to_json() for fight in upcoming_fights]
        return upcoming_fights

    @staticmethod
    def get_fighter_by_name_json(fighter_name):
        fighter = Fighter.query.filter_by(fighter=fighter_name).first()
        return fighter.to_json()

    @staticmethod
    def get_all_fighters_json():
        fighters = Fighter.query.all()
        fighters_json = [fighter.to_json() for fighter in fighters]
        return fighters_json

    @staticmethod
    def get_events(is_past):
        events = Event.query.filter_by(isPast=is_past).all()
        events = [event.to_json() for event in events]
        return jsonify(events)

    @staticmethod
    def get_all_fights():
        return Fight.query.all()

    @staticmethod
    def get_all_fights_from_event(event_name):
        fights = PastFight.query.all()
        fights_from_event = [fight.convert_to_json() for fight in fights if fight.event.rstrip() == event_name]
        return fights_from_event

    @staticmethod
    def get_all_fighters():
        return Fighter.query.all()

    @staticmethod
    def create_fighter_entity(row):
        return Fighter(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                       row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15])

    @staticmethod
    def check_duplicate_fight(event, fighter1, fighter2):
        return bool(Fight.query.filter_by(event=event, fighter1=fighter1, fighter2=fighter2).first())

    @staticmethod
    def get_fight(fight):
        return PastFight.query.filter_by(event=fight['EVENT'], fighter1=fight['fighter1'],
                                         fighter2=fight['fighter2'], actual_outcome=None).first()

    @staticmethod
    def create_past_fight(past_fight):
        # check if predicited_outcome and accuracy exists else set it to 0

        return PastFight(past_fight.event, past_fight.fighter1, past_fight.fighter2,
                         past_fight.predicted_outcome, past_fight.accuracy, past_fight.actual_outcome)

    @staticmethod
    def get_past_fight(fight):
        return PastFight.query.filter_by(event=fight['EVENT'], fighter1=fight['fighter1'],
                                         fighter2=fight['fighter2']).first()


dm = DataManager()
