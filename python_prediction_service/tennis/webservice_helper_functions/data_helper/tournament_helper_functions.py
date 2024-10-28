from datetime import datetime

from tennis.domain.Tournament import Tournament
from tennis.webservice_helper_functions.scraper_helper.tournament_scraper import (
    scrape_tennis_tournaments_and_matches,
    get_events_df)


def convert_to_tournament_objects(matches_data, isPast=True):
    tournaments = []
    for index, row in matches_data.iterrows():
        date_obj = datetime.strptime(row['Date'], "%d‑%b‑%Y").date()
        tournament = Tournament(row['Event'], row['Location'], row['Surface'], date_obj, isPast)
        tournaments.append(tournament)
    return tournaments


def get_tournaments_data(all_matches, upcoming_matches):
    tournaments, past_tournaments, _, _ = scrape_tennis_tournaments_and_matches(all_matches, upcoming_matches)
    tournaments = tournaments.dropna()
    tournaments = convert_to_tournament_objects(tournaments, False)
    past_tournaments = convert_to_tournament_objects(past_tournaments, True)
    tournaments.extend(past_tournaments)
    return tournaments


def retrieve_events_df():
    return get_events_df()
