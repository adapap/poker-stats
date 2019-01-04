import json
import os
import re
import requests
from collections import defaultdict
from datetime import datetime
from pprint import pprint

class Season:
    """
    Seasons keep track of all data for a particular season.

    """
    def __init__(self, name: str, season_num: int, players: list):
        self.name = name
        self.season_num = season_num
        self.players = players

    @classmethod
    def from_file(cls, file):
        """Opens a local data file and parses the cell values."""
        with open(f'data/{file}') as f:
            values = json.load(f)['values']
        season_name = None
        season_num = None
        players = []
        for i, data in enumerate(values):
            if not data:
                continue
            if i == 0:
                season_name, season_num = re.match(r'(.+) \(Season (\d+)\)', data[1]).groups()
            elif i > 2:
                if len(data) < 4:
                    continue
                _, bonus_points, total_points, name, *tournament_data = data
                if total_points == '0':
                    continue
                placements = []
                for i in range(1, len(tournament_data) - 1, 2):
                    tournament_name = f'Tournament {(i - 1) // 2}'
                    place = tournament_data[i]
                    points = tournament_data[i + 1]
                    placement = {
                    'tournament': tournament_name,
                    'place': place,
                    'points': points
                    }
                    if place:
                        placements.append(place)
                player = Player(season_num, bonus_points, total_points, name, placements)
                players.append(player)
        return cls(season_name, season_num, players)

    def __repr__(self):
        return f'{len(self.players)} players'


class Player:
    """
    Player stores information about one individual player in a season.
    """
    def __init__(self, season_num, bonus_points, total_points, name, placements: list):
        self.season_num = season_num
        self.bonus_points = bonus_points
        self.total_points = total_points
        self.placements = placements

        if ',' in name:
            name = name.split(',')
            self.last_name = name[0].strip()
            self.first_name = name[1].strip()
        else:
            self.first_name = name
            self.last_name = ''

    @property
    def name(self):
        return self.first_name + ' ' + self.last_name

    def __repr__(self):
        return f'{self.name}: {self.points} (S{self.season_num})'


class Stats:
    """
    Stats is a wrapper for all user and tournament data.

    :property base_uri:
    :property api_query:
    :meth get_config:
    :meth update_local_data:
    :meth get_sheet_names:
    :meth get_sheet:
        :param name:
    :meth parse_seasons:
    """

    def __init__(self):
        config = self.get_config()
        self.spreadsheet_id = config.get('spreadsheet_id')
        self.api_key = config.get('api_key')
        self.last_timestamp = config.get('last_timestamp')
        self.cur_season = config.get('cur_season')

        # If the time difference is greater than 1 week, retrieve data
        current_timestamp = datetime.now()
        difference = current_timestamp - datetime.strptime(self.last_timestamp, '%Y-%m-%d %H:%M:%S.%f')
        if difference.days >= 7:
            self.update_local_data(current_timestamp)
        
        # Parse all season data
        self.seasons = {}
        self.parse_seasons()

    @property
    def base_uri(self):
        """The base URI for all Sheets API requests."""
        return f'https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}'

    @property
    def api_query(self):
        return f'?key={self.api_key}'

    def get_config(self):
        """Returns the configuration object represented by JSON."""
        config_path = 'config.json'
        with open(config_path) as f:
            data = json.load(f)
        return data

    def update_local_data(self, timestamp):
        """Updates the local copies of sheet data."""
        names = self.get_sheet_names()
        cur_season = names[0]

        # If sheets do not exist, cache them
        for name in names:
            path = f'data/{name}.json'
            # Always update the latest sheet
            if name == cur_season or not os.path.exists(path):
                data = self.get_sheet(name)
                with open(path, 'w') as f:
                    json.dump(data, f, indent=4)

        # Update config file
        config = {
            "spreadsheet_id": self.spreadsheet_id,
            "api_key": self.api_key,
            "last_timestamp": str(timestamp),
            "cur_season": cur_season
        }
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)

    def get_sheet_names(self):
        """Retrieves the sheet names from the JSON data."""
        uri = self.base_uri + self.api_query
        try:
            resp = requests.get(uri).json()
            sheet_names = [name for name in [sheet['properties']['title'] for sheet in resp['sheets']] if 'test' not in name]
            return sheet_names
        except ValueError:
            print(f'Error decoding JSON from sheet list response')

    def get_sheet(self, name):
        """Retrieves sheet data given a title."""
        uri = self.base_uri + f'/values/{name}' + self.api_query
        try:
            resp = requests.get(uri).json()
            return resp
        except ValueError:
            print(f'Error decoding JSON from sheet {name}')

    def parse_seasons(self):
        """
        Parses all season files in the /data folder.

        :returns: dictionary of Season objects
        """
        for file in os.listdir('data'):
            name = file.rstrip('.json')
            season = Season.from_file(file)
            self.seasons[name] = season

    def __repr__(self):
        return f'Seasons: {self.seasons}'