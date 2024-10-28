from config.db_config import db
from ufc_fights.domain.Event import Event
from ufc_fights.domain.Fight import Fight, PastFight
from ufc_fights.domain.Fighter import Fighter
from ufc_fights.webservice_helper_functions.managers.DataManager import dm
from ufc_fights.webservice_helper_functions.helper_functions.image_helper import add_fighter_image


class DatabaseManager:
    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def session_add(item):
        db.session.add(item)

    def delete_all_events(self):
        Event.query.delete()
        self.commit()

    def delete_all_fights(self):
        Fight.query.delete()
        PastFight.query.delete()
        self.commit()

    def delete_all_fighters(self):
        Fighter.query.delete()
        self.commit()

    def update_fights_to_db(self, fights):
        db.session.add_all(fights)
        self.commit()

    def update_past_fights_to_db(self, fights):
        db.session.add_all(fights)
        self.commit()

    def add_default_image_to_fighters(self):
        fighters = dm.get_all_fighters()
        for fighter in fighters:
            fighter.add_image()
        db.session.commit()
        self.commit()

    def delete_all_upcoming_fights(self):
        Fight.query.delete()
        self.commit()

    def add_events_to_db(self, events):
        for event in events:
            db.session.add(event)
        self.commit()

    def add_fighters_to_db(self, fighters):
        db.session.add_all(fighters)
        self.commit()

    def refresh_fighter_images(self):
        fighters = dm.get_all_fighters()
        for fighter in fighters:
            add_fighter_image(fighter)
        self.commit()

    def delete_fight(self, past_fight):
        db.session.delete(past_fight)
        self.commit()




dbm = DatabaseManager()
