import os
from pathlib import Path
import json
import collections

def split_qualifier(qual):
    # Split the input string by the colon
    parts = qual.split(':')
    
    # Identify which part starts with 'e' or 'c'
    if parts[0].startswith('e') or parts[0].startswith('c'):
        compiler = parts[0]
        flag = parts[1]
    else:
        compiler = parts[1]
        flag = parts[0]
    
    return compiler, flag

class ConfigsDict(collections.UserDict):
    def __init__(self, inp=None):
        if isinstance(inp, collections.UserDict):
            super(ConfigsDict,self).__init__(inp)
        else:
            super(ConfigsDict,self).__init__()
            if isinstance(inp, (collections.Mapping, collections.Iterable)): 
                si = self.__setitem__
                for k,v in inp:
                    si(k,v)

    def __setitem__(self, k, v):
        try:
            self.__getitem__(k)
            raise ValueError("duplicate key '{0}' found".format(k))
        except KeyError:
            super(ConfigsDict,self).__setitem__(k,v)


class Configuration():
    def __init__(self, n_events, n_jobs, geometry, mail, memory, disk, lifetime, cpu, resources, enable_gevgen, enable_edepsim, enable_garsoft, outpath, defaults) -> None:

        self.n_events  = n_events           # number of events to produce
        self.n_jobs    = n_jobs             # number of jobs to divide
        self.geometry  = geometry
        self.mail      = mail
        self.memory    = memory
        self.disk      = disk
        self.lifetime  = lifetime
        self.cpu       = cpu
        self.resources = resources
        self.gevgen    = enable_gevgen      # use gevgen_fnal for the GENIE step?
        self.edepsim   = enable_edepsim     # use edep-sim for the Geant4 step?
        self.garsoft   = enable_garsoft
        self.outpath   = outpath            # path for output

        self.defaults = Path(defaults)

        if not self.outpath.startswith("/pnfs/dune/scratch"):
            raise ValueError("Are you sure you want to put your files in {}?\nCheck this please...".format(self.outpath))

    def add_genie_config(self, json):
        self.genie_config = GENIEConfiguration(**json)

    def add_edep_config(self, json):
        self.edep_config = EDEPConfiguration(**json)

    def add_gsft_config(self, json):
        self.gsft_config = GArSoftConfiguration(**json)

    def add_tar_dir_name(self, name):
        self.tar_dir_name = name

    def add_tar_path(self, path):
        self.tar_path = path

    def add_run_script_path(self, path):
        self.run_script_path = path

    def add_gsft_local_products_path(self, path):
        self.gsft_config.add_local_products_path(path)

class GENIEConfiguration():
    def __init__(self, genie, genie_xsec, genie_phyopt, geant4, ND_Production, sam_web_client, topvolume, seed) -> None:
        
        self.genie          = ProductConfiguration(**genie)
        self.genie_xsec     = ProductConfiguration(**genie_xsec)
        self.genie_phyopt   = ProductConfiguration(**genie_phyopt)
        self.geant4         = ProductConfiguration(**geant4)
        self.ND_Production  = ProductConfiguration(**ND_Production)
        self.sam_web_client = ProductConfiguration(**sam_web_client)

        self.topvolume = topvolume
        self.seed      = seed

class EDEPConfiguration():
    def __init__(self, edepsim) -> None:

        self.edepsim = ProductConfiguration(**edepsim)

class GArSoftConfiguration():
    def __init__(self, garsoft, copy_reco) -> None:

        self.garsoft = ProductConfiguration(**garsoft)
        self.copy_reco = copy_reco

    def add_local_products_path(self, path):
        self.local_products_path = path

class ProductConfiguration():
    def __init__(self, version, qualifier) -> None:
        self.version = version
        self.qualifier = qualifier

class ConfigParser:
    def __init__(self, config_dir) -> None:

        self.config_dir = config_dir

        self.configs_dict = ConfigsDict()
        self.check_and_book()

        """ if _json is not None:
            self.config_json = _json
        elif _path is not None:
            with open(_path, 'r') as config_file:
                self.config_json = json.load(config_file)
        else:
            raise ValueError("You need to provide something!") """

    def check_and_book(self):

        for file in os.scandir(self.config_dir):
            with open(file, 'r') as config_file:
                config_json = json.load(config_file)
                if '__type__' in config_json:
                    config_type = config_json['__type__']
                    del config_json['__type__']
                    self.configs_dict[config_type] = config_json

        if 'GlobalConfiguration' not in self.configs_dict:
            raise ValueError("Configuration directory doesn't contain a GlobalConfiguration!")


    def decode_configs(self) -> Configuration:

        config = Configuration(**self.configs_dict['GlobalConfiguration'])

        if 'GENIEConfiguration' in self.configs_dict:
            config.add_genie_config(self.configs_dict['GENIEConfiguration'])

        if 'EDEPConfiguration' in self.configs_dict:
            config.add_edep_config(self.configs_dict['EDEPConfiguration'])

        if 'GArSoftConfiguration' in self.configs_dict:
            config.add_gsft_config(self.configs_dict['GArSoftConfiguration'])

        return config