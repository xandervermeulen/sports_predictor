import os
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

url = os.getenv('BASE_URL')
headers = {
    "Accept": os.getenv("HEADERS_ACCEPT"),
    "User-Agent": os.getenv("HEADERS_USER_AGENT")
}

base_url = os.getenv('HOME_URL')


def write_events_to_csv(event_data):
    df = pd.DataFrame(event_data)
    return df


def scrape_tennis_tournaments_and_matches(all_matches, upcoming_matches):
    if upcoming_matches is None:
        upcoming_tournaments = None
    else:
        upcoming_tournaments = upcoming_matches[['Event', 'Location', 'Surface', 'Date']].drop_duplicates()
    past_tournaments = all_matches[['Tournament', 'Location', 'Surface', 'Date']].drop_duplicates()
    past_tournaments = past_tournaments.rename(columns={'Tournament': 'Event'})

    return upcoming_tournaments, past_tournaments, upcoming_matches, all_matches


def get_events_df():
    soup = get_soup(base_url)
    event_data = get_current_event_data(soup)
    events = pd.DataFrame(event_data)
    events_df = events
    if events.empty:
        return None
    # if events has an Event Date
    if 'Event Date' in events.columns:
        events['Event Date'] = pd.to_datetime(events['Event Date'])
        events = events[(events['Event Date'] >= pd.Timestamp.now() - pd.DateOffset(weeks=2)) & (
                events['Event Date'] <= pd.Timestamp.now() + pd.DateOffset(weeks=1))]
    event_urls = events['Href Link'].tolist()
    events_df = get_upcoming_matches_events(event_urls)
    events_df = pd.DataFrame(events_df[1:], columns=events_df[0])
    return events_df


def get_current_event_data(html_content):
    event_data = []
    table = html_content.find('table', id='current-events')
    # find all the td elems where valign is top
    td_elems = table.find_all('td', valign='top')
    # take the second row elem
    td = td_elems[1]
    tags = td.find_all('a')
    # check if the row has a link
    if tags:
        for tag in tags:
            href = tag.get('href')
            if href:
                # check if the link contains the string 'player'
                if 'player' not in href:
                    # retrieve the name out of the url
                    # https://www.tennisabstract.com/current/2024ATPStuttgart.html -> 2024ATPStuttgart
                    name = href.split('/')[-1].split('.')[0]
                    event_data.append({'Event Name': name, 'Href Link': href})
    # for row in rows[2:]:  # skipping the header rows
    #     columns = row.find_all('td')
    #     if len(columns) >= 2:
    #         event_name = columns[1].find('a').text.strip()
    #         event_date = columns[2].text.strip()
    #         href_link = columns[1].find('a')['href']
    #         event_data.append({'Event Name': event_name, 'Event Date': event_date, 'Href Link': href_link})
    return event_data


def get_upcoming_matches_events(event_urls):
    table = [["Event Name", "Player 1", "Player 2"]]  # Initialize the table
    for event_url in event_urls:
        full_url = event_url
        response = requests.get(full_url, headers=headers)
        upcoming_singles_matches = re.findall(r"var upcomingSingles = (.*?);", response.text)
        if upcoming_singles_matches:
            pattern_match = r'(.*?)\s*<br/>'
            for match in upcoming_singles_matches:
                matches = re.findall(pattern_match, match)
                for m in matches:
                    pattern_player = r'<a href=".*?">(.*?)<\/a>'
                    player_names = re.findall(pattern_player, m)
                    if len(player_names) % 2 != 0:
                        player_names = player_names[:-1]  # Discard the last player if uneven
                    player_pairs = [(player_names[i], player_names[i + 1]) for i in range(0, len(player_names), 2)]
                    for i, pair in enumerate(player_pairs):
                        event_name = event_url.split('/')[-1].split('.')[0]
                        table.append([event_name, pair[0], pair[1]])
    return table


def get_soup(tour_url):
    response = requests.get(tour_url, headers=headers)
    response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
    return BeautifulSoup(response.text, 'html.parser')
