from data import *
from collections import defaultdict

info = Stats()
def most_final_tables(season):
    players = info.seasons[season].players

    print(players[0].placements)

most_final_tables("2018F")