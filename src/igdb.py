import json
import http.client
import os.path

from src.game import Game


class Igdb:
    def __init__(self, name=""):
        self.client_id = None
        self.secret_id = None
        self.access_id = None
        self.limit = 4
        self.count = 0
        self.name = name
        self.games = []

    def get_config(self):
        script_dir = os.path.dirname(__file__)
        config_path = os.path.join(script_dir, "../config.json")
        config_path = os.path.normpath(config_path)
        config_json = open(config_path, "r")
        config = json.load(config_json)
        config_json.close()

        self.client_id = config["client_id"]
        self.access_id = config["access_id"]
        self.secret_id = config["secret_id"]

    def search_game(self):
        conn = http.client.HTTPSConnection("api.igdb.com")
        payload = f"fields *; search \"{self.name}\"; limit 1;"
        headers = {
            'Client-ID': self.client_id,
            'Authorization': 'Bearer ' + self.access_id,
            'Content-Type': 'application/json',
        }
        # TODO: prevent duplicate code
        try:
            conn.request("POST", "/v4/games/", payload, headers)
            res = conn.getresponse()
            if res.status != 200:
                print(f"HTTP request failed with status code {res.status}")
                return
            data = res.read()
            try:
                data_dict = json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                print("Failed to parse JSON data")
                return
            for data in data_dict:
                game_obj = Game()
                try:
                    game_obj.parse_results(json.dumps(data))
                except (KeyError, AttributeError) as e:
                    print(f"Failed to parse game data: {e}")
                    continue
                self.games.append(game_obj)
                self.get_game_cover(game_obj)
        except Exception as e:
            print(f"HTTP request failed: {e}")

    def get_game_cover(self, game_obj):
        conn = http.client.HTTPSConnection("api.igdb.com")
        payload = f"fields *; where id={game_obj.cover};"
        headers = {
            'Client-ID': self.client_id,
            'Authorization': 'Bearer ' + self.access_id,
            'Content-Type': 'application/json',
        }
        # TODO: prevent duplicate code
        # TODO: find a way to get covers for all games in single request
        try:
            conn.request("POST", "/v4/covers", payload, headers)
            res = conn.getresponse()
            if res.status != 200:
                print(f"HTTP request failed with status code {res.status}")
                return
            data = res.read()
            try:
                data_dict = json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                print("Failed to parse JSON data")
                return
            if data_dict:
                try:
                    url = data_dict[0]["url"]
                    url = url.lstrip("//")
                    game_obj.cover_url = url
                except (KeyError, AttributeError) as e:
                    print(f"Failed to parse cover data: {e}")
        except Exception as e:
            print(f"HTTP request failed: {e}")


igdb_query = Igdb("halo")
igdb_query.get_config()
igdb_query.search_game()
print(igdb_query.games)
