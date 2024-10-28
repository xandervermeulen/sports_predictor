from config.db_config import db


class Player(db.Model):
    Name = db.Column(db.String(100), primary_key=False)
    Nationality = db.Column(db.String(100), primary_key=False)
    DateOfBirth = db.Column(db.Date, primary_key=False)
    Ranking = db.Column(db.Integer, primary_key=False)
    Dominance = db.Column(db.Float, primary_key=False)
    AceRatio = db.Column(db.Float, primary_key=False)
    FirstServePercentage = db.Column(db.Float, primary_key=False)
    FirstServePointsWon = db.Column(db.Float, primary_key=False)
    BreakPointsWon = db.Column(db.Float, primary_key=False)
    Hand = db.Column(db.String(100), primary_key=False)
    PlayerRankingAtThatTime = db.Column(db.Float, primary_key=False)
    OpponentRankingAtThatTime = db.Column(db.Float, primary_key=False)
    DoubleFaultRatio = db.Column(db.Float, primary_key=False)
    SecondServePointsWon = db.Column(db.Float, primary_key=False)
    RoundValue = db.Column(db.Float, primary_key=False)
    BreakPointsFaced = db.Column(db.Float, primary_key=False)
    SetsWon = db.Column(db.Float, primary_key=False)
    SetsLost = db.Column(db.Float, primary_key=False)
    TotalTime = db.Column(db.Float, primary_key=False)
    PlayerId = db.Column(db.Integer, primary_key=True, autoincrement=True)

    def __init__(self, Name, Nationality, DateOfBirth, Ranking, Dominance, AceRatio, FirstServePercentage,
                 FirstServePointsWon, BreakPointsWon, Hand, PlayerRankingAtThatTime,
                 OpponentRankingAtThatTime, DoubleFaultRatio, SecondServePointsWon, RoundValue, BreakPointsFaced,
                 SetsWon, SetsLost, TotalTime):
        self.Name = Name
        self.Nationality = Nationality
        self.DateOfBirth = DateOfBirth
        self.Ranking = Ranking
        self.Dominance = Dominance
        self.AceRatio = AceRatio
        self.FirstServePercentage = FirstServePercentage
        self.FirstServePointsWon = FirstServePointsWon
        self.BreakPointsWon = BreakPointsWon
        self.Hand = Hand
        self.PlayerRankingAtThatTime = PlayerRankingAtThatTime
        self.OpponentRankingAtThatTime = OpponentRankingAtThatTime
        self.DoubleFaultRatio = DoubleFaultRatio
        self.SecondServePointsWon = SecondServePointsWon
        self.RoundValue = RoundValue
        self.BreakPointsFaced = BreakPointsFaced
        self.SetsWon = SetsWon
        self.SetsLost = SetsLost
        self.TotalTime = TotalTime

    def serialize(self):
        return {
            'Name': self.Name,
            'Nationality': self.Nationality,
            'DateOfBirth': self.DateOfBirth.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'Ranking': self.Ranking,
            'Dominance': self.Dominance,
            'AceRatio': self.AceRatio,
            'FirstServePercentage': self.FirstServePercentage,
            'FirstServePointsWon': self.FirstServePointsWon,
            'BreakPointsWon': self.BreakPointsWon,
            'NumOfBreakPoints': self.BreakPointsFaced,
            'Hand': self.Hand,
        }

    def serialize_all_stats(self):
        return {
            'player': self.Name,
            'Ranking at that time': self.PlayerRankingAtThatTime,
            'Opponent Ranking at that time': self.OpponentRankingAtThatTime,
            'Dominance Ratio': self.Dominance,
            'Ace Ratio': self.AceRatio,
            'Double Fault Ratio': self.DoubleFaultRatio,
            'First Serve Percentage': self.FirstServePercentage,
            'First Serve Points Won': self.FirstServePointsWon,
            'Second Serve Points Won': self.SecondServePointsWon,
            'round value': self.RoundValue,
            'Break Points Won': self.BreakPointsWon,
            'Break Points Faced': self.BreakPointsFaced,
            'Sets Won': self.SetsWon,
            'Sets Lost': self.SetsLost,
            'Total time': self.TotalTime,
            'player_id': self.PlayerId,
            'date_of_birth': self.DateOfBirth,
        }

    def serialize_to_player_info(self):
        return {
            'rank': self.Ranking,
            'name': self.Name,
            'nationality': self.Nationality,
            'date_of_birth': self.DateOfBirth,
            'player_id': self.PlayerId
        }

    def update(self, other):
        self.Nationality = other.Nationality
        self.DateOfBirth = other.DateOfBirth
        self.Ranking = other.Ranking
        self.BreakPointsFaced = other.BreakPointsFaced
        self.BreakPointsWon = other.BreakPointsWon
        self.Dominance = other.Dominance
        self.AceRatio = other.AceRatio
        self.DoubleFaultRatio = other.DoubleFaultRatio
        self.FirstServePercentage = other.FirstServePercentage
        self.FirstServePointsWon = other.FirstServePointsWon
        self.SecondServePointsWon = other.SecondServePointsWon
        self.TotalTime = other.TotalTime
        self.SetsWon = other.SetsWon
        self.SetsLost = other.SetsLost
        self.PlayerRankingAtThatTime = other.PlayerRankingAtThatTime
        self.OpponentRankingAtThatTime = other.OpponentRankingAtThatTime
        self.RoundValue = other.RoundValue