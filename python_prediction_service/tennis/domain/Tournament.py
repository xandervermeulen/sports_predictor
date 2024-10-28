from config.db_config import db


class Tournament(db.Model):
    Name = db.Column(db.String(100), primary_key=True)
    Location = db.Column(db.String(100), primary_key=False)
    Surface = db.Column(db.String(100), primary_key=False)
    Date = db.Column(db.Date, primary_key=False)
    IsPast = db.Column(db.Boolean, primary_key=False)

    def __init__(self, Name, Location, Surface, Date, IsPast):
        self.Name = Name
        self.Location = Location
        self.Surface = Surface
        self.Date = Date
        self.IsPast = IsPast

    def serialize(self):
        return {
            'Name': self.Name,
            'Location': self.Location,
            'Surface': self.Surface,
            'Date': self.Date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),

        }
