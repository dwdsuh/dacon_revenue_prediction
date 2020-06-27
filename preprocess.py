from utils import DataConfig


from collections import namedtuple

class Preprocessor(object):
    def __init__(self, data_config, long_lat_map = None,):
        self.long_lat_map = long_lat_map
        self.config = data_config
        pass

    def ppr_single(self, sample):
        """
        sample: a vector of which length is 12
        0: year+month ex) 201901
        1,2: (store address) state, city ex) 강원 강릉시
        3: business category ex) 건강보조식품 소매업
        4,5: (owner's address) state, city
        6: age
        7: sex
        8: family category
        9: the number of customers
        10: revenue (y label)
        11: count
        """
        ym = self.ppr_ym(sample[0])
        loc = self.ppr_store_addr(sample[1:2])
        bus_cat = self.ppr_bus_cat(sample[3])
        owner_loc = self.ppr_own_addr(sample[4:5])
        age = self.ppr_age(sample)
    
