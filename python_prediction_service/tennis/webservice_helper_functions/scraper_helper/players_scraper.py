import os

import pandas as pd
import requests
from bs4 import BeautifulSoup

PLAYER_URL = os.getenv("PLAYER_URL")
headers = {
    "Accept": os.getenv("HEADERS_ACCEPT"),
    "User-Agent": os.getenv("HEADERS_USER_AGENT")
}

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', os.getenv('DATA_DIR')))
player_file = os.getenv('PLAYER_FILE')
csv_file = os.path.join(root_dir, player_file)


def update_player_rankings():
    players = pd.DataFrame(columns=["rank", "player_url", "name", "nationality", "date_of_birth"])
    player_data = []
    response = requests.get(PLAYER_URL, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        player_table = soup.find("table", class_="tablesorter")
        if player_table:
            tr_player_elements = player_table.find_all("tr")
            first_row_skipped = False

            for player_elem in tr_player_elements:
                if not first_row_skipped:
                    first_row_skipped = True
                    continue
                td_elems = player_elem.find_all("td")
                if td_elems:
                    rank = td_elems[0].text.strip()
                    player_url = td_elems[1].find("a")["href"]
                    player_name = td_elems[1].text.strip().replace("\xa0", " ")
                    nationality = td_elems[2].text.strip()
                    dob = td_elems[3].text.strip()
                    player_data.append({
                        "rank": rank,
                        "player_url": player_url,
                        "name": player_name,
                        "nationality": nationality,
                        "date_of_birth": dob
                    })

    players = pd.concat([players, pd.DataFrame(player_data)], ignore_index=True)
    players = players[:500]
    players.to_csv(csv_file, index=False)
    return players
