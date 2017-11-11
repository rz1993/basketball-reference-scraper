from tornado.ioloop import IOLoop
from crawlers import GameLogCrawler, PlayerCrawler

import json
import random
import numpy as np
import tornado.web
from datetime import datetime, timedelta

"""
    crawler = PlayerCrawler()
    game_crawler = GameLogCrawler()
    player = crawler.scrape("Karl-Anthony Towns",
            "https://www.basketball-reference.com/players/t/townska01.html"
        )
    season_urls = player.season_urls
    seasons = [
        game_crawler.scrape(season) for season in season_urls
    ]
"""
def gen_season_dates(games=82):
    today = datetime.today()
    season = range(0, games*2, 2)
    return map(lambda i: today+timedelta(i), season)

def gen_season(games=82):
    dates = gen_season_dates(games)
    str_dates = map(lambda d: "{}/{}/{}".format(d.month, d.day, d.year),
                    dates)
    pts = map(int, np.random.randint(5, 40, size=games))
    return dict(date_game=list(str_dates),
                pts=list(pts))
seasons = [gen_season() for i in range(5)]


class PlayerHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        super(PlayerHandler, self).set_default_headers()
        self.set_header('Access-Control-Allow-Origin', 'http://localhost:3000')
        self.set_header('Access-Control-Allow-Credentials', 'true')

    def get(self, player_name):
        df = seasons[-2]
        dates = df['date_game']
        pts = map(int, df['pts'])
        output = {
            'data': {
                'x': list(dates),
                'y': list(pts)
            }
        }
        self.write(output)


if __name__ == "__main__":
    handler_mapping = [
                       (r'/player/([a-zA-Z]+)$', PlayerHandler),
                      ]
    application = tornado.web.Application(handler_mapping)
    application.listen(8000)
    IOLoop.current().start()
