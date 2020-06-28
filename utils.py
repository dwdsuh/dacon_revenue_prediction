import requests
import os
import pandas as pd
import numpy as np
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
    def __init__(self,
                max_year, 
                min_year, 
                location_map_dir,
                ccnt_threshold,
                cnt_threshold,
                ):
        self.max_year = max_year
        self.min_year = min_year
        self.location_map_dir = location_map_dir
        self.ccnt_threshold = ccnt_threshold
        self.cnt_threshold = cnt_threshold
    
    @classmethod
    def from_yaml(cls, yaml_file_path):
        with open(yaml_file_path, "r", encoding = 'utf-8') as f:
            stats = yaml.load(f.read())
        return cls(**stats)
    
    @classmethod
    def from_raw_data(cls, data_path):
        df = pd.read_csv(data_path)
        max_year = max(df["REG_YYMM"] // 100)
        min_year = min(df["REG_YYMM"] // 100)
        location_map_dir = os.path.join(
                    os.path.dirname(data_path),
                    "location_map.yaml")
        ccnt_threshold = np.percentile(df["CSTMR_CNT"], 99)
        cnt_threshold = np.percentile(df["CNT"], 99)
        return cls(
                max_year, 
                min_year,
                location_map_dir,
                ccnt_threshold,
                cnt_threshold,)

    def encode_yd(self, yd: int):
        year  = yd // 100
        month = yd % 100
        return ( (year - self.min_year)/self.max_year,
                math.cos(2 * math.pi * (month-1) / 12),
                math.sin(2 * math.pi * (month-1) / 12))
    
    def encode_loc(self, 
                location, 
                location_map_dir = None):
        # EDA 과정에서 CCG_NM에 많은 null이 포함되어 있음을 확인
        # TODO: 그냥 null 이면 empty string으로 변환되어 이 method로 들어오도록 처리
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
                    location_map_dir):
        with open(location_map_dir, "w", encoding = 'utf-8') as f:
            f.write(yaml.dump(self.location_map))

    def encode_age(self, age):
        """
        나이의 경우 10s, 20s 이렇게 str 형태로 표시되어있음
        10s --> 0.1 로 변환
        """
        return int(age[:-1]) / 100 
    
    def encode_sex(self, sex):
        """
        1, 2 로 표시되어 있음 자료형은 numpy.int64
        """
        return sex - 1

    def encode_family_lifecycle(self, flc):
        """
        type(flc): numpy.int64
        1: 1인가구
        2: 영유아자녀가구
        3: 중고생자녀가구 
        4: 성인자녀가구
        5: 노년가구
        """
        one_hot_vector = np.array([0 for i in range(5)])
        one_hot_vector[flc-1] = 1
        return one_hot_vector

    def encode_ccnt(self, ccnt):
        # minmaxscaling vs standard scaling
        # from EDA, ccnt looks like half-normal distribution
        # but it does not really follow normal distribution
        # decided to use minmax scaling 
        # but use threshold instead of max
        if ccnt <= self.ccnt_threshold:
            return ccnt / self.ccnt_threshold
        return "outlier"
    
    def encode_cnt(self, cnt):
        if cnt <= self.cnt_threshold:
            return cnt / self.cnt_threshold
        return "outlier"

    def encode_amt(self, amt):
        raise NotImplementedError




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