import os
import re
import pandas as pd
from selenium import webdriver
from selenium.common import NoSuchDriverException, TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

from tennis.webservice_helper_functions.data_helper.tournament_helper_functions import retrieve_events_df
from tennis.webservice_helper_functions.formatting_helper.matches_formatting import (parse_match_row,
                                                                                     convert_link_to_event_name,
                                                                                     format_upcoming_tennis_matches)
from tennis.webservice_helper_functions.formatting_helper.player_formatting import add_space_before_uppercase, \
    clean_player_name

headers = {
    "Accept": os.getenv("HEADERS_ACCEPT"),
    "User-Agent": os.getenv("HEADERS_USER_AGENT")
}
MATCHES_URL = os.getenv('MATCHES_URL')


def scrape_all_matches():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', os.getenv('DATA_DIR')))
    player_file = os.getenv('PLAYER_FILE')
    csv_file = os.path.join(root_dir, player_file)

    player_urls = pd.read_csv(csv_file)
    player_urls = player_urls.drop(player_urls.columns[0], axis=1)
    all_matches = []
    upcoming_matches = []
    with ThreadPoolExecutor(max_workers=15) as executor:
        future_to_player = {executor.submit(process_player, player): player for _, player in player_urls.iterrows()}
        for future in as_completed(future_to_player):
            player_matches, player_upcoming_matches = future.result()
            if player_matches:
                all_matches.extend(player_matches)
            if player_upcoming_matches:
                upcoming_matches.extend(player_upcoming_matches)
    all_matches_df = pd.DataFrame(all_matches)
    upcoming_df = pd.DataFrame(upcoming_matches)
    all_matches_df = convert_link_to_event_name(all_matches_df)
    all_matches_df = all_matches_df.drop(columns=['Tournament_Url'])
    events_df = retrieve_events_df()
    if events_df is None:
        return all_matches_df, None
    upcoming_matches = format_upcoming_tennis_matches(upcoming_df, events_df)
    return all_matches_df, upcoming_matches


def get_html_of_page(url):
    options = Options()
    options.headless = True
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', os.getenv('CONFIG_ROOT'),
                                            os.getenv('CHROME_DRIVER_DIR'), os.getenv('CHROME_DRIVER_DIR')))
    chromedriver_path = os.path.join(root_dir, os.getenv('CHROME_DRIVER_PATH'))
    service = ChromeService(executable_path=chromedriver_path)
    try:
        with webdriver.Chrome(service=service, options=options) as browser:
            browser.get(url)
            WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, 'matches')))
            return browser.page_source
    except NoSuchDriverException:
        print("Driver not found")
        return None
    except TimeoutException:
        print("Timeout")
        return None
    except WebDriverException:
        print("Webdriver exception")
        return None
    except Exception as e:
        print("An error occurred")
        print(e)
        return None


def process_player(player):
    player_name = re.sub(r'\s', '', player['name'])
    url = MATCHES_URL.format(player_name)
    player_html = get_html_of_page(url)
    if not player_html:
        return None, None
    soup = BeautifulSoup(player_html, 'html.parser')
    table = soup.find('table', {'id': 'matches'})
    player_matches = []
    upcoming_matches = []
    if table:
        # check if table has tbody tag
        if not table.find('tbody'):
            return player_matches, upcoming_matches
        rows = table.find('tbody').find_all('tr')
        for row in rows:
            match_data = parse_match_row(row)
            result = match_data['Result']
            set_scores = match_data['Set Scores']
            full_name = add_space_before_uppercase(player_name)
            if 'd.' in result and not set_scores:
                continue
            if (set_scores == "" or set_scores == 'Live Scores') and 'vs' in result:
                upcoming_matches.append({
                    'Date': match_data['Date'],
                    'Tournament': match_data['Location'],
                    'Surface': match_data['Surface'],
                    'Results': result,
                    'player': full_name
                })
                continue
            winner, loser = map(clean_player_name, result.split("d."))
            match_data.update({'Winner': winner, 'Loser': loser, 'player_name': full_name})
            player_matches.append(match_data)
    print(f'The size of player_matches is {len(player_matches)} and the size of upcoming_matches is'
          f' {len(upcoming_matches)}')
    return player_matches, upcoming_matches
