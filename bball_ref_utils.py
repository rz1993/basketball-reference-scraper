import time
import json
import string
import pandas as pd
import logging

from difflib import SequenceMatcher
from crawlers import GameLogCrawler, Player, PlayerCrawler
from soup_utils import soup_from_url


__all__ = ['soup_from_url', 'get_active_player_names_urls',
           'build_player_dictionary', 'build_active_player_dictionary',
           'search_for_name', 'save_player_dictionary',
           'load_player_dictionary', 'gameLogs']

BASKETBALL_LOG = 'basketball.log'

logging.basicConfig(filename=BASKETBALL_LOG,
                    level=logging.DEBUG,
                    )
DOMAIN = 'http://www.basketball-reference.com/'


def get_active_player_names_urls(letters=None, suppress_output=True):

    names = []
    if not letters:
        letters = string.ascii_lowercase

    for letter in letters:
        letter_page = soup_from_url(DOMAIN + 'players/{}'.format(letter),
                                    suppress_output)

        # The players table has id="players"
        # Currently active players have <strong> tags
        player_table = letter_page.find("table", id="players")
        if player_table is None:
            continue
        current_names = player_table.findAll('strong')
        for n in current_names:
            # Children is a generator so we use next instead of 0
            name_data = next(n.children)
            try:
                names.append((name_data.contents[0],
                              DOMAIN + name_data.attrs['href']))
            except Exception as e:
                logging.debug(e)
                print(e)
        time.sleep(1)

    return names


def build_player_dictionary(names_urls):
    players = {}
    pcrawler = PlayerCrawler()
    for name, url in names_urls:
        players[name] = pcrawler.scrape(name, url)
        time.sleep(1)
    return players


def build_active_player_dictionary(suppress_output=True):
    names_urls = get_active_player_names_urls(suppress_output=suppress_output)
    players = build_player_dictionary(names_urls)
    return players


def fuzzy_ratio(name, search_string):
    """
    Calculate difflib fuzzy ratio for search query matching
    """
    return SequenceMatcher(None, search_string.lower(), name.lower()).ratio()


def search_for_name(player_dictionary, search_string, threshold=0.5):
    """
    Case insensitive partial search for player names, returns a list of strings,
    names that contained the search string.  Uses difflib for fuzzy matching.
    threshold:
    """
    players = player_dictionary.keys()
    search_string = search_string.lower()
    criteria = lambda name: name in search_string or fuzzy_ratio(name, search_string) > threshold
    matched_players = filter(criteria, players)
    return matched_players


def save_player_dict(player_dict, pathToFile):
    """
    Saves player dictionary to a JSON file
    """
    player_json = {name: player_data.to_dict() for name, player_data in player_dict.items()}
    json.dump(player_json, open(pathToFile, 'wb'), indent=0)


def load_player_dictionary(pathToFile):
    """
    Loads previously saved player dictionary from a JSON file
    """
    result = {}
    with open(pathToFile) as f:
        json_dict = json.loads(f.read())
        for name in json_dict:
            result[name] = Player(**json_dict[name])
    return json_dict


def game_log_list_to_df(gamelogs):
    """
    Functions to parse the gamelogs
    Takes a list of game log urls and returns a concatenated DataFrame
    """
    return pd.concat([game_log_to_df(g) for g in gamelogs])


def test_parse_log(url):
    crawler = GameLogCrawler()
    df = crawler.scrape(url)
    return df


def game_logs(player_dictionary, name):
    ### would be nice to put some caching logic here...
    return game_log_list_to_df(player_dictionary[name].gamelog_url_list)
