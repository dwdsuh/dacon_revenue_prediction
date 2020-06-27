import requests
import os
import pandas as pd
import math
import yaml

class DataConfig(object):
    def __init__(self):
        pass

    def save(self, file_path):
        pass

    def load(self, file_path):
        pass



class Encoder(object):
    def __init__(self,max_year, min_year, location_map_dir):
        self.max_year = max_year
        self.min_year = min_year
        self.location_map_dir = location_map_dir
        pass
    
    @classmethod
    def from_yaml(cls, yaml_file_path):
        with open(yaml_file_path, "r", encoding = 'utf-8') as f:
            stats = yaml.load(f.read())
        return cls(**stats)
    
    @classmethod
    def from_raw_data(cls, data_path):
        df = df.read_csv(data_path)
        max_year = max(df["REG_YYMM"] // 100)
        min_year = min(df["REG_YYMM"] // 100)
        location_map_dir = os.path.join(
                    os.path.dirname(data_path,
                    "data/location_map.yaml"))
        return cls(max_year, min_year, location_map_dir)

    def encode_yd(self, yd: int):
        year  = yd // 100
        month = yd % 100
        return ( (year - self.min_year)/self.max_year,
                math.cos(2 * math.pi * (month-1) / 12),
                math.sin(2 * math.pi * (month-1) / 12))
    
    def encode_loc(self, 
                location, 
                location_map_dir = None):
        if location_map_dir == None:
            self.location_map = {}
        else:
            self.location_map = self.load_location_map(
                location_map_dir)
        
        try:
            loc = self.location_map[location]
        except KeyError:
            map_api = MapApi(
                "/Users/kakao/kakao_project/credentials/KakaoAK")
            loc = map_api.get_long_lat(location)
            # caching
            self.location_map[location] = loc
        #TODO: add noise to the loc
        return loc
    
    def load_location_map(self,
                    location_map_dir):
        with open(location_map_dir, "r", encoding = 'utf-8') as f:
            return yaml.load(f.read())

    def save_location_map(self,
                    location_map,
                    location_map_dir):
        with open(location_map_dir, "w", encoding = 'utf-8') as f:
            f.write(yaml.dump(location_map))







class MapApi(object):
    def __init__(self, app_key_path):
        self.app_key = self.get_app_key(app_key_path)
    
    def get_app_key(self, app_key_path):
        with open(app_key_path, "r", encoding = 'utf-8') as f:
            app_key = f.readline().strip()
        return app_key

    def get_long_lat(self, location):
        response = requests.get(
            url = "https://dapi.kakao.com/v2/local/search/address.json",
            params = {"query": location},
            headers = {"Authorization": "KakaoAK {}".format(self.app_key)})
        x = response.json()["documents"][0]["x"]
        y = response.json()["documents"][0]["y"]
        return (x,y)