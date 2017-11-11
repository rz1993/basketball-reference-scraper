from config import DB_ADDRESS

from sqlalchemy import (create_engine, Column, Integer,
                        String, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Player(Base):

    __tablename__ = 'player'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    height = Column(String(10))
    weight = Column(Integer)
    positions = Column(String(100))
    overview_url = Column(String(50))
    current_team_id = Column(Integer, ForeignKey('team.id'))

    @classmethod
    def from_object(cls, player):
        return cls(name=player.name,
                   height=player.height,
                   weight=player.weight,
                   positions=",".join(player.positions),
                   overview_url=player.overview_url)


class GameLog(Base):

    __tablename__ = "game_log"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('team.id'))
    opp_id = Column(Integer, ForeignKey('team.id'))
    player_id = Column(Integer, ForeignKey('player.id'))
