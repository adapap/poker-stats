from data import *
from collections import defaultdict
from collections import OrderedDict

import json

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
    count = tournament_count(season)
    result = defaultdict(int)
    player_list = info.seasons[season_id].players

    for index, p in enumerate(player_list):


        for i in range(10):
            search_result = search(p.name, p.placements, i)
            if(search_result):
                result[p.name] += search_result['place']
            else:
                result[p.name] += count['Tournament ' + str(i+1)]

    data = sorted(filter(lambda y: y[1], result.items()), key=lambda x: x[1])
    return [x for x in data]




def search(name, players, i):
    for p in players:
        if p['tournament'] == "Tournament " + str(i+1):
            return p


def get_names(name, season):
    season_id = seasons[season]

    name_list = [p.name for p in info.seasons[season_id].players if name in p.name]

    return name_list

def get_all_names(season):
    season_id = seasons[season]

    name_list = [p.name for p in info.seasons[season_id].players]

    return name_list

def get_best_placement(name, season):

    season_id = seasons[season]
    player_list = info.seasons[season_id].players
    id = 0
    for p in player_list:
        if str(name) == p.name:
            break
        else:
            id += 1


    placement_list = player_list[id].placements
    parsed_placements = {}
    for i, tournid in enumerate(placement_list):

        parsed_placements[tournid['tournament']] = tournid['place']


    min_key = min(parsed_placements, key=parsed_placements.get)
    return (min_key, parsed_placements[min_key])


def get_final_tables(name, season):
    season_id = seasons[season]
    player_list = info.seasons[season_id].players
    id = 0
    for p in player_list:
        if str(name) == p.name:
            break
        else:
            id += 1

    p = player_list[id]
    return sum(0 < x['place'] < 10 for x in p.placements)



def tournament_count(season):
    season_id = seasons[season]
    players = defaultdict(int)
    player_list = info.seasons[season_id].players

    for i, placements in enumerate(player_list):

        for index, tournaments in enumerate(placements.placements):
            players[tournaments['tournament']] += 1


    return OrderedDict(sorted(players.items(), key=lambda t: t[0]))

def print_best_sum():
    names = sum_of_placements("2018F")[0]

    for i in names:
        print(i + ": " + str(sum_of_placements("2018F")[1][i]))




#print(tournament_count("2018F"))
print(sum_of_placements("2018F"))
#print(print_best_sum())











