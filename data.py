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

    Parameters
    ----------
    name: :class:`str`
        The name of the season, e.g. "2016F-FH"

    season_num: :class:`int`
        The number of the season.

    players: List[:class:`Player`]
        A list of Player objects that participated in this season.
    """
    def __init__(self, name, season_num, players):
        self.name = name
        self.season_num = season_num
        self.players = players

    @classmethod
    def from_file(cls, file):
        """
        Opens a local data file and parses the cell values.
        Used to create Season objects through :class:`Stats`

        :param str file: The name of the file containing JSON data.
        :returns: :class:`Season` representing the input file.
        """
        with open(f'data/{file}') as f:
            values = json.load(f)['values']
        season_name = None
        season_num = None
        players = []
        num_tournaments = 0
        for i, data in enumerate(values):
            if not data:
                continue
            if i == 0:
                season_name, season_num = re.match(r'(.+) \(Season (\d+)\)', data[1]).groups()
                num_tournaments = len([x for x in data if 'Tourn' in x])
            elif i > 2:
                if len(data) < 4:
                    continue
                _, bonus_points, total_points, name, *tournament_data = data
                if total_points == '0' or total_points == '':
                    continue
                bonus_points = int(bonus_points or '0')
                total_points = float(total_points)
                placements = []
                for i in range(1, min(len(tournament_data) - 1, 2 * num_tournaments), 2):
                    tournament_name = f'Tournament {(i + 1) // 2}'
                    place = int(tournament_data[i] or 0)
                    if place == 0:
                        continue
                    points = float(tournament_data[i + 1])
                    placement = {
                    'tournament': tournament_name,
                    'place': place,
                    'points': points
                    }
                    placements.append(placement)
                player = Player(season_num, bonus_points, total_points, name, placements)
                players.append(player)
        return cls(season_name, season_num, players)

    def __repr__(self):
        return f'{len(self.players)} players'


class Player:
    """
    Player stores information about one individual player in a season.

    Parameters
    ----------
    season_num: :class:`int`
        The season number (e.g. `7` for Season 7)

    bonus_points: :class:`int`
        The number of bonus points awarded this season.

    total_points: :class:`float`
        The total number of points earned this season.

    name: :class:`str`
        The unparsed name from the raw data.

        "Doe, John" becomes "John Doe" as :attr:`name`

    placements: List[:class:`dict`]
        Contains the placements for each tournament.

        Example placement:

            >>> player.placements[1]
            {
                'tournament': 'Tournament 2',
                'place': 13,
                'points': 7.49
            }
    
    """
    def __init__(self, season_num, bonus_points, total_points, name, placements):
        self.season_num = season_num
        self.bonus_points = bonus_points
        self.total_points = total_points
        self.placements = placements

        if ',' in name:
            self.name = ' '.join(map(lambda x: x.strip(), name.split(',')))
        else:
            self.name = name.strip()

    def __repr__(self):
        return f'{self.name} ({self.total_points} pts.)'


class Stats:
    """
    Stats is a wrapper for all player and tournament data.

    Attributes
    ----------
    cur_season: :class:`str`
        The current season name.

    seasons: List[:class:`Season`]
        A collection of season objects mapped to their name.

    players: Dict[:class:`str`, :class:`dict`]
        A dictionary containing player season data, as well as their overall
        ranks for each season, mapped to player names.
        
        For example, accessing player stats in the current season:
        
            >>> players['John Doe']
            {
                '2018F': John Doe (41 pts.),
                '2018S': John Doe (30.12 pts.),
                'ranks': [8, 17]
            }

    """

    def __init__(self):
        config = self._get_config()
        self.spreadsheet_id = config.get('spreadsheet_id')
        with open('api_key.txt') as f:
            self.api_key = f.read()
        self.last_timestamp = config.get('last_timestamp')
        self.cur_season = config.get('cur_season')

        # If the time difference is greater than 1 week, retrieve data
        current_timestamp = datetime.now()
        difference = current_timestamp - datetime.strptime(self.last_timestamp, '%Y-%m-%d %H:%M:%S.%f')
        if difference.days >= 7:
            self._update_local_data(current_timestamp)
        
        # Parse all season data
        self.seasons = []
        self._parse_seasons()

        # Extrapolate player data from season data
        self.players = {}
        self._parse_players()

    @property
    def _base_uri(self):
        """The base URI for all Sheets API requests."""
        return f'https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}'

    @property
    def _api_query(self):
        """Query parameter used as a suffix to all API requests."""
        return f'?key={self.api_key}'

    def _get_config(self):
        """Reads and returns the configuration object saved locally as a JSON file."""
        config_path = 'config.json'
        with open(config_path) as f:
            data = json.load(f)
        return data

    def _update_local_data(self, timestamp):
        """Updates the local file copies of sheet data."""
        names = self._get_sheet_names()
        cur_season = names[0]

        # If sheets do not exist, cache them
        for name in names:
            path = f'data/{name}.json'
            # Always update the latest sheet
            if name == cur_season or not os.path.exists(path):
                data = self._get_sheet(name)
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

    def _get_sheet_names(self):
        """Retrieves the sheet names from the JSON data."""
        uri = self.base_uri + self.api_query
        try:
            resp = requests.get(uri).json()
            sheet_names = [name for name in [sheet['properties']['title'] for sheet in resp['sheets']] if 'test' not in name]
            return sheet_names
        except ValueError:
            print(f'Error decoding JSON from sheet list response')

    def _get_sheet(self, name):
        """Retrieves sheet data given a title."""
        uri = self.base_uri + f'/values/{name}' + self.api_query
        try:
            resp = requests.get(uri).json()
            return resp
        except ValueError:
            print(f'Error decoding JSON from sheet {name}')

    def _parse_seasons(self):
        """Parses all season files in the /data folder."""
        for file in os.listdir('data'):
            name = file.rstrip('.json')
            season = Season.from_file(file)
            self.seasons.append(season)

    def _parse_players(self):
        """Extracts player information and formats it for convenience."""
        players = defaultdict(dict)
        for season in self.seasons:
            for rank, player in enumerate(sorted(season.players, key=lambda p: p.total_points, reverse=True)):
                player.rank = rank
                players[player.name][season.name] = player
        for player_name, player_data in players.items():
            season_data = player_data.values()
            ranks = [p.rank for p in season_data]
            player_data.update({'ranks': ranks})
            self.players[player_name] = player_data

    def __repr__(self):
        return f'Seasons: {self.seasons}'