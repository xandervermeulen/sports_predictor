from config.db_config import db

from datetime import datetime


class Event(db.Model):
    event = db.Column(db.String(100), primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    isPast = db.Column(db.Boolean, nullable=False)

    def __init__(self, event, date, location, isPast=False):
        self.event = event
        self.date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        self.location = location
        self.isPast = isPast

    def to_json(self):
        return {
            'event': self.event,
            'date': self.date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'location': self.location
        }
