import os

import requests
from bs4 import BeautifulSoup

DEFAULT_URL = os.getenv("DEFAULT_UFC_FIGHTER_IMG")
UFC_URL = os.getenv("UFC_ATHLETE_URL")
headers = {
    'User-Agent': os.getenv("HEADERS_USER_AGENT"),
    'referer': os.getenv("UFC_BASE_URL")
}


def lookup_fighter_image(name):
    format_name = name.replace(' ', '-').lower()
    url = UFC_URL + format_name
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        image_tag = soup.find('meta', property='og:image')
        if image_tag:
            image_url = image_tag['content']
            return image_url
        return DEFAULT_URL
    return DEFAULT_URL


def add_fighter_image(fighter):
    if fighter.img_url == DEFAULT_URL or fighter.img_url is None:
        print("Has default image")
        image_url = lookup_fighter_image(fighter.fighter)
        fighter.img_url = image_url
