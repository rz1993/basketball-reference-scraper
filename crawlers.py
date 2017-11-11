from soup_utils import find_comment, parse_dollar_amounts, soup_from_url, text_pattern

from datetime import datetime
from bs4 import BeautifulSoup

import logging
import json
import pandas as pd
import re

# Get the current season's end year based on today's date
DATE = datetime.today()
CURRENT_SEASON = DATE.year+1 if DATE.month > 9 else DATE.year


class BaseCrawler(object):
    domain = "http://www.basketball-reference.com"

    def scrape(self):
        pass

    def to_object(self):
        pass


class Player:
    def __init__(self, name=None, height=None, weight=None,
                 team=None, positions=None, season_urls=None):
        self.name = name
        self.height = height
        self.weight = weight
        self.team = team
        self.positions = positions
        self.season_urls = season_urls

    def to_dict(self):
        return self.__dict__


class PlayerCrawler(BaseCrawler):

    # Define regex patterns for scraping as patterns class attribute
    patterns = {
        'position': dict(text=text_pattern(u'(Point Guard|Center|Power Forward|Shooting Guard|Small Forward)')),
        'height': dict(text=text_pattern(u'([0-9]-[0-9]{1,2})')),
        'weight': dict(text=text_pattern(u'([0-9]{2,3})lb')),
    }

    posn_pattern = u'(Point Guard|Center|Power Forward|Shooting Guard|Small Forward)'
    height_pattern = u'([0-9]-[0-9]{1,2})'
    weight_pattern = u'([0-9]{2,3})lb'
    team_href_pattern = u'teams/[A-Z]+/{}'.format(CURRENT_SEASON)

    def scrape(self, name, overview_url, verbose=False):
        # Scrape a single player overview
        if verbose:
            print(name, overview_url)

        overview_soup = soup_from_url(overview_url)
        self.overview_content = overview_soup

        try:
            info = overview_soup.findAll("div", id="info")[0]

            # Find basic information for the player in the info box
            position_text = info.find(text=re.compile(self.posn_pattern))
            height_text = info.find(text=re.compile(self.height_pattern))
            weight_text = info.find(text=re.compile(self.weight_pattern))

            team_info = info.findAll("a", href=re.compile(self.team_href_pattern))
            team_status = team_info[0].text if team_info else 'FA'
            positions = re.findall(self.posn_pattern, position_text)

            weight = re.findall(self.weight_pattern, weight_text)[0].strip()
            height = re.findall(self.height_pattern, height_text)[0].strip()
            team = team_status
            positions = [p.strip() for p in positions]

        except Exception as ex:
            if hasattr(ex, 'message'):
                logging.error(ex.message)
            else:
                logging.error(ex)
            print(ex)
            positions = []
            height = None
            weight = None
            team = None

        season_urls = None
        for li in overview_soup.find_all('li'):
            if 'Game Logs' in li.getText():
                links = li.findAll('a')
                season_urls = list(map(lambda link: self.domain + link.get('href'),
                                    links))

        return Player(name=name, height=height, weight=weight,
                      team=team, positions=positions, season_urls=season_urls)


class SalaryCrawler(BaseCrawler):
    def scrape_salaries(self, name, soup):
        salary_div = soup.find("div", id="all_all_salaries")
        # Tricky because the html comments prevent BeautifulSoup
        # from parsing all the tables; luckily there is a copy of the salary
        # table which is commented inside <div id="all_all_salaries">
        # We extract this comment's text and render it into a soup object to parse
        if salary_div:
            commented_salary_table = find_comment(salary_div)
            if commented_salary_table:
                salary_table = BeautifulSoup(commented_salary_table).find('tbody')
                seasons = salary_table.findAll("th", attrs={'data-stat': 'season'})
                salaries = salary_table.findAll("td", attrs={'data-stat': 'salary'})
                return zip([name] * len(seasons),
                            map(lambda el: el.text, seasons),
                            map(lambda el: el.get('csk'), salaries))
        return []

    def scrape_contracts(self, name, soup):
        contract_div = soup.find("div", id="all_contracts_.*")
        if contract_div:
            commented_contract_table = find_comment(contract_div)
            if contract_div:
                contract_table = BeautifulSoup(commented_contract_table)
                seasons = contract_table.findAll('th')[1:]
                contracts = contract_table.findAll('td')[1:]
                return zip([name] * len(seasons),
                    map(lambda el: el.get('data-stat'), seasons),
                    map(lambda el: parse_dollar_amounts(el.text), contracts))
        return []

    def scrape(self, name, url):
        soup = soup_from_url(url)

        try:
            salaries = list(self.scrape_salaries(name, soup))
            return salaries + self.scrape_contracts(name, soup)
        except Exception as ex:
            print(name, url)
            logging.error(ex)
            print(ex)
            return []


class GameLogCrawler(BaseCrawler):
    def __init__(self):
        pass

    def scrape(self, url):
        """
        Takes a url of a player's game log for a given year, returns a DataFrame
        """
        glsoup = soup_from_url(url)

        reg_season_table = glsoup.find('table', attrs={'id': 'pgl_basic'})
        playoff_table = glsoup.find('table', attrs={'id': 'pgl_basic_playoffs'})

        # First cell of each row is also a 'th' with 'scope' set as 'row'
        raw_headers = filter(lambda h: h.get('scope') != 'row' \
                                and h.get('data-stat') != "ranker",
                             reg_season_table.findAll('th'))
        header = []
        header_map = {}
        for th in raw_headers:
            label = th.get('data-stat')
            if label and not label in header:
                header.append(label)
                header_map[label] = th.get('aria-label')

        reg = self.table_to_df(reg_season_table, header)
        playoff = self.table_to_df(playoff_table, header)

        if reg is None:
            return playoff
        elif playoff is None:
            return reg

        return pd.concat([reg, playoff])

    def table_to_df(self, table_soup, header):
        """
        Parses the HTML/Soup table for the gamelog stats.
        Returns a pandas DataFrame
        """
        if not table_soup:
            return None
        # Remove special first row header
        rows = table_soup.findAll('tr')[1:]
        # Filter out other header rows throughout the table and empty rows
        rows = filter(lambda r: r.get('class') != 'thead' and r.find('td'), rows)
        parsed_table = [self.parse_played_game(row, header) for row in rows if self.did_play(row)]
        return pd.io.parsers.TextParser(parsed_table, names=header, parse_dates=True).get_chunk()

    def did_play(self, game_row):
        # Game status is the first 1st column after the game number 'th'
        status = game_row.find('td')
        if status.getText():
            return True

    def parse_played_game(self, game_row, header):
        parsed = [col.getText() for col in game_row.findAll('td')]
        return parsed

    def parse_missed_game(self, game_row, header):
        pass
