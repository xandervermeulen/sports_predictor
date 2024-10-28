from flask import jsonify

from config.db_config import db
from tennis.domain.Match import PastMatch, Match
from tennis.domain.Player import Player
from tennis.domain.Tournament import Tournament


class DataManger:
    @staticmethod
    def jsonify_elements(items):
        return jsonify(items)

    def get_all_players_json(self):
        players = db.session.query(Player).all()
        players = [player.serialize() for player in players]
        return self.jsonify_elements(players)

    @staticmethod
    def get_all_players():
        return db.session.query(Player).all()

    @staticmethod
    def get_upcoming_match_by_players_and_tournament(player1, player2, tournament_name):
        return db.session.query(PastMatch).filter_by(Player1=player1, Player2=player2, TournamentName=tournament_name, ActualOutcome=None).first()

    @staticmethod
    def get_all_tournaments():
        return db.session.query(Tournament).all()

    @staticmethod
    def get_all_past_match():
        return PastMatch.query.all()

    @staticmethod
    def get_match_by_players_and_tournament(player1, player2, tournament_name):
        return db.session.query(PastMatch).filter_by(
            Player1=player1, Player2=player2, TournamentName=tournament_name).first()

    def get_all_upcoming_matches(self):
        matches = db.session.query(PastMatch).filter(PastMatch.ActualOutcome.is_(None)).all()
        matches = [match.serialize() for match in matches]
        return self.jsonify_elements(matches)

    def get_all_tournaments_json(self):
        tournaments = db.session.query(Tournament).all()
        tournaments = [tournament.serialize() for tournament in tournaments]
        return self.jsonify_elements(tournaments)

    @staticmethod
    def get_player_by_name(player_name):
        return db.session.query(Player).filter_by(Name=player_name).first()

    @staticmethod
    def get_past_matches_dict():
        # Fetch all players and create a dictionary mapping player_id to player_name
        players = Player.query.all()
        player_dict = {player.Name: player.PlayerId for player in players}
        return player_dict

    def get_all_past_matches_json(self):
        past_matches = db.session.query(PastMatch).filter(PastMatch.ActualOutcome.isnot(None)).all()
        past_matches = [past_match.serialize_past() for past_match in past_matches]
        return self.jsonify_elements(past_matches)

    @staticmethod
    def get_all_past_matches_serialized():
        past_matches = db.session.query(PastMatch).filter(PastMatch.ActualOutcome.isnot(None)).all()
        past_matches = [match.serialize_for_prediction() for match in past_matches]
        return past_matches

    @staticmethod
    def get_all_players_serialized():
        player_stats = db.session.query(Player).all()
        player_stats = [player.serialize_all_stats() for player in player_stats]
        return player_stats

    def get_all_matches_from_events(self, tournament_name):
        matches = db.session.query(Match).filter(Match.TournamentName == tournament_name).all()
        matches = [match.serialize() for match in matches]
        return self.jsonify_elements(matches)

    def get_all_past_matches_from_events(self, tournament_name):
        past_matches = db.session.query(PastMatch).filter(PastMatch.TournamentName == tournament_name).all()
        past_matches = [past_match.serialize_past() for past_match in past_matches]
        return self.jsonify_elements(past_matches)

    def get_all_upcoming_tournaments(self):
        tournaments = db.session.query(Tournament).filter(Tournament.IsPast.is_(False)).all()
        tournaments = [tournament.serialize() for tournament in tournaments]
        return self.jsonify_elements(tournaments)

    def get_all_past_tournaments(self):
        tournaments = db.session.query(Tournament).filter(Tournament.IsPast.is_(True)).all()
        tournaments = [tournament.serialize() for tournament in tournaments]
        return self.jsonify_elements(tournaments)

    @staticmethod
    def get_tournament_by_name(tournament_name):
        tournament = db.session.query(Tournament).filter_by(Name=tournament_name).first()
        return tournament


dm = DataManger()
