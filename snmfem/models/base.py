from abc import ABC, abstractmethod
from pathlib import Path
import json
import snmfem.conf as conf
import numpy as np

class PhysicalModel(ABC) :

    def __init__(self, e_offset, e_size, e_scale, params_dict, db_name=None) :
        self.x = self.build_energy_scale(e_offset, e_size, e_scale)
        self.params_dict = params_dict
        self.bkgd_in_G = False
        self.spectrum = np.zeros_like(self.x)
        
    @abstractmethod
    def generate_spectrum(self,elts_list) :
        pass

    @abstractmethod
    def generate_g_matr (self) :
        pass
    
    def extract_DB (self,db_name) :
        db_path = conf.DB_PATH / Path(db_name)
        with open(db_path,"r") as f :
            json_dict = json.load(f)["table"]
        return json_dict

    def build_energy_scale(self,e_offset, e_size, e_scale) :
        return np.linspace(e_offset,e_offset+e_size*e_scale,num=e_size)

