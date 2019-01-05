from data import *
from collections import defaultdict

info = Stats()
seasons = {"2018F": 5, "2018S": 6}

def most_final_tables(season):
    season_id = seasons[season]
    players = info.seasons[season_id].players
    final_tables = {p.name: sum(0 < x['place'] < 10 for x in p.placements) for p in players}
    data = sorted(filter(lambda y: y[1], final_tables.items()), key=lambda x: -x[1])
    return [x for x in data if x[1] > 1]

def most_top_3(season):
    season_id = seasons[season]
    players = info.seasons[season_id].players
    top3 = {p.name: sum(0 < x['place'] < 4 for x in p.placements) for p in players}
    data = sorted(filter(lambda y: y[1], top3.items()), key=lambda x: -x[1])
    return [x for x in data if x[1] > 0]

def sum_of_placements(season):
    season_id = seasons[season]
    players = info.seasons[season_id].players
    final_tables = {p.name: sum(x['place'] for x in p.placements) for p in players}

print(most_top_3("2018F"))