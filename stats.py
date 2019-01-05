from data import *
from collections import defaultdict

info = Stats()
seasons = {"2018F": 5, "2018S": 6}

def most_final_tables(season):
    season_id = seasons[season]
    players = info.seasons[season_id].players
    final_tables = {p.name: sum(0 < x['place'] < 10 for x in p.placements) for p in players}
    return final_tables

def most_top_3(season):
    season_id = seasons[season]
    players = info.seasons[season_id].players
    top3 = {p.name: sum(0 < x['place'] < 3 for x in p.placements) for p in players}
    return top3










most_final_tables("2018F")