from config.db_config import db


class Fight(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event = db.Column(db.String(100), primary_key=False)
    fighter1 = db.Column(db.String(100), primary_key=False)
    fighter2 = db.Column(db.String(100), primary_key=False)
    predicted_outcome = db.Column(db.String(100), nullable=False)
    accuracy = db.Column(db.Float, nullable=False)

    def __init__(self, event, fighter1, fighter2, predicted_outcome, accuracy):
        self.event = event
        self.fighter1 = fighter1
        self.fighter2 = fighter2
        self.predicted_outcome = predicted_outcome
        self.accuracy = accuracy

    def convert_to_json(self):
        return {
            'Event': self.event,
            'Fighter1': self.fighter1,
            'Fighter2': self.fighter2,
            'Predicted_outcome': self.predicted_outcome,
            'Accuracy': self.accuracy
        }


class PastFight(Fight):
    actual_outcome = db.Column(db.String(100), nullable=True, default=None)

    def __init__(self, event, fighter1, fighter2, predicted_outcome, accuracy, actual_outcome=None):
        super().__init__(event, fighter1, fighter2, predicted_outcome, accuracy)
        self.actual_outcome = actual_outcome

    def convert_to_json(self):
        return {
            'Event': self.event,
            'Fighter1': self.fighter1,
            'Fighter2': self.fighter2,
            'Predicted_outcome': self.predicted_outcome,
            'Accuracy': self.accuracy,
            'Actual_outcome': self.actual_outcome
        }
