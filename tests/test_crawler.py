import unittest
import os
import sys
try:
    from nbaCrawler import bball_ref_utils as b_utils
    from nbaCrawler.crawlers import PlayerCrawler, GameLogCrawler, SalaryCrawler
except:
    parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(parent_path)

    from crawlers import PlayerCrawler, GameLogCrawler, SalaryCrawler

    import bball_ref_utils as b_utils
    import models as models


class UtilsTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_current_players_names_urls(self):
        print("Testing get current players")
        names_urls_a = b_utils.get_active_player_names_urls(letters=["a"])
        # Need better assertion condition
        self.assertTrue(len(names_urls_a) > 0)

    def test_build_player_dict(self):
        print("Building player dictionary")
        names_urls = [("Alex Abrines",
                       "https://www.basketball-reference.com/players/a/abrinal01.html"),
                      ("Arron Afflalo",
                       "https://www.basketball-reference.com/players/a/afflaar01.html"),
                      ("Anthony Davis",
                       "https://www.basketball-reference.com/players/d/davisan02.html")]
        players_dict = b_utils.build_player_dictionary(names_urls)
        self.assertTrue(len(players_dict.keys()) == len(names_urls))
        for _, player in players_dict.items():
            self.assertNotIn(None, player.to_dict().values())


class CrawlerTestCase(unittest.TestCase):
    def setUp(self):
        self.p_crawler = PlayerCrawler()
        self.glog_crawler = GameLogCrawler()
        self.sal_crawler = SalaryCrawler()
        self.name = "Jared Dudley"
        self.url = "https://www.basketball-reference.com/players/d/dudleja01.html"

    def test_player_crawler_scrape(self):
        print("Testing PlayerCrawler")
        player_obj = self.p_crawler.scrape(self.name, self.url)
        self.assertNotIn(None, player_obj.to_dict().values())

    def test_get_game_log_urls(self):
        player = self.p_crawler.scrape(self.name, self.url)
        game_logs = player.season_urls
        print(game_logs)
        self.assertTrue(len(game_logs) > 0)

    def test_get_player_salaries(self):
        salaries = self.sal_crawler.scrape(self.url)
        print(salaries)
        self.assertTrue(len(salaries) > 1)

if __name__ == '__main__':
    unittest.main()
