from bball_ref_utils import get_active_player_names_urls
from crawlers import GameLogCrawler, PlayerCrawler, SalaryCrawler
from pipeline import load_from_csv, load_from_json, save_to_csv

import json
import os


def scrape_active_players_urls(csv_file):
    print("Scraping URLS...")
    if os.path.exists('./'+csv_file):
        _, names_urls = load_from_csv(csv_file)
    else:
        names_urls = get_active_player_names_urls()
        header = ["Name", "Overview_URL"]
        save_to_csv(names_urls, header, csv_file)
    print("Finished scraping {} player URLS".format(len(names_urls)))
    return names_urls

def scrape_players_to_json(json_file, urls):
    print("Scraping player profiles...")
    if os.path.exists('./'+json_file):
        player_dicts = load_from_json(json_file)
    else:
        crawler = PlayerCrawler()
        with open(json_file, 'w') as json_out:
            player_dicts = list(map(lambda pair: crawler.scrape(*pair).to_dict(), urls))
            json.dump(player_dicts, json_out)
    print("Finished scraping {} player profiles".format(len(player_dicts)))
    return player_dicts

def scrape_active_players_salaries(csv_file, urls):
    print("Scraping player salaries...")
    if os.path.exists('./'+csv_file):
        salaries = load_from_csv(csv_file)
    else:
        salaries = []
        crawler = SalaryCrawler()
        for name, url in urls:
            salaries += crawler.scrape(name, url)
        header = ['Name', 'Season', 'Salary(USD)']
        save_to_csv(salaries, header, csv_file)
    print("Finished scraping {} player salaries".format(len(salaries)))
    return salaries


if __name__ == '__main__':
    import time

    start = time.clock()
    print("Scraping start... time: {}".format(start))
    names_urls = scrape_active_players_urls('player_overview_urls.csv')
    player_dicts = scrape_players_to_json('player_profiles.json', names_urls)
    scrape_active_players_salaries('active_player_salaries.csv', names_urls)
    print("Scraping took {:0.2f} seconds".format(time.clock() - start))
