from config.db_config import db


class Match(db.Model):
    MatchID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TournamentName = db.Column(db.String(100), primary_key=False)
    Player1 = db.Column(db.String(100), primary_key=False)
    Player2 = db.Column(db.String(100), primary_key=False)
    Date = db.Column(db.Date, primary_key=False)
    Accuracy = db.Column(db.Float, primary_key=False)
    Outcome = db.Column(db.String(100), primary_key=False)

    def __init__(self, TournamentName, Player1, Player2, Date, Accuracy, Outcome):
        self.TournamentName = TournamentName
        self.Player1 = Player1
        self.Player2 = Player2
        self.Date = Date
        self.Accuracy = Accuracy
        self.Outcome = Outcome

    def serialize(self):
        return {
            'TournamentName': self.TournamentName,
            'Player1': self.Player1,
            'Player2': self.Player2,
            'Date': self.Date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'Accuracy': self.Accuracy,
            'Outcome': self.Outcome
        }


class PastMatch(Match):
    ActualOutcome = db.Column(db.String(100), nullable=True, default=None)

    def __init__(self, TournamentName, Player1, Player2, Date, Accuracy, Outcome, ActualOutcome=None):
        super().__init__(TournamentName, Player1, Player2, Date, Accuracy, Outcome)
        self.ActualOutcome = ActualOutcome

    def serialize_past(self):
        return {
            'TournamentName': self.TournamentName,
            'Player1': self.Player1,
            'Player2': self.Player2,
            'Date': self.Date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'Accuracy': self.Accuracy,
            'PredictedOutcome': self.Outcome,
            'ActualOutcome': self.ActualOutcome
        }

    def serialize_for_prediction(self):
        return {
            'TournamentName': self.TournamentName,
            'player1': self.Player1,
            'player2': self.Player2,
            'Date': self.Date,
            'ActualOutcome': self.ActualOutcome
        }
