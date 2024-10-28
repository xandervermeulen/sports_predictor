from config.db_config import db
from tennis.domain.Match import Match, PastMatch
from tennis.domain.Player import Player
from tennis.domain.Tournament import Tournament
from tennis.webservice_helper_functions.managers.DataManager import dm


class DatabaseManager:
    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def session_add(item):
        db.session.add(item)

    @staticmethod
    def bulk_save_object(items):
        db.session.bulk_save_objects(items)

    def delete_all_matches(self):
        db.session.query(Match).delete()
        self.commit()

    def delete_all_past_matches(self):
        past_matches = db.session.query(PastMatch).filter(PastMatch.ActualOutcome.isnot(None)).all()
        for match in past_matches:
            db.session.delete(match)
        self.commit()

    def delete_all_players(self):
        db.session.query(Player).delete()
        self.commit()

    def delete_all_tournaments(self):
        db.session.query(Tournament).delete()
        self.commit()

    def add_all_tournaments(self, tournaments):
        if tournaments:
            for tournament in tournaments:
                if tournament.Name is None or tournament.Name == 'nan':
                    continue
                existing_tournament = dm.get_tournament_by_name(tournament.Name)
                if existing_tournament is None:
                    self.session_add(tournament)
            self.commit()

    def add_players(self, players):
        if players:
            existing_players = {player.Name: player for player in dm.get_all_players()}
            new_players = []
            for player in players:
                if player.Name in existing_players:
                    existing_players[player.Name].update(player)
                    self.session_add(player)
                else:
                    new_players.append(player)
            if new_players:
                self.bulk_save_object(new_players)
        self.commit()

    def add_matches(self, matches):
        if matches:
            for match in matches:
                existing_match = dm.get_match_by_players_and_tournament(match.Player1, match.Player2,
                                                                        match.TournamentName)
                if existing_match is None:
                    self.session_add(match)
                else:
                    existing_match.Accuracy = match.Accuracy
                    existing_match.Prediction = match.Outcome
                    self.session_add(existing_match)
            self.commit()

    def add_past_matches(self, matches):
        if matches:
            for match in matches:
                existing_match = dm.get_match_by_players_and_tournament(match.Player1, match.Player2,
                                                                        match.TournamentName)
                if existing_match is None:
                    self.session_add(match)
                else:
                    existing_match.Accuracy = match.Accuracy
                    existing_match.Prediction = match.Outcome
                    existing_match.ActualOutcome = match.ActualOutcome
                    self.session_add(existing_match)
            self.commit()

    def add_prediction_to_match(self, past_matches):
        player_dict = dm.get_player_dict()
        past_matches_dict = {
            (row['player_id1'], row['player_id2'], row['TournamentName']): (row['Accuracy'], row['Prediction'])
            for _, row in past_matches.iterrows()
        }

        all_matches = dm.get_all_past_match()
        for match in all_matches:
            player_id1 = player_dict.get(match.Player1)
            player_id2 = player_dict.get(match.Player2)

            if player_id1 and player_id2:
                key = (player_id1, player_id2, match.TournamentName)
                if key in past_matches_dict:
                    match.Accuracy, match.Outcome = past_matches_dict[key]

        self.commit()


dbm = DatabaseManager()
