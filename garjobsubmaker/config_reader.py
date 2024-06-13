import json

class Configuration:
    def __init__(self) -> None:
        pass

class GlobalConfiguration(Configuration):
    def __init__(self, n_events, gevgen, edepsim, garsoft, outpath, genie_config, edep_config) -> None:
        self.n_events = n_events        # number of events to produce
        self.gevgen   = gevgen          # use gevgen_fnal for the GENIE step?
        self.edepsim  = edepsim         # use edep-sim for the Geant4 step?
        self.garsoft  = garsoft
        self.outpath  = outpath         # path for output

        if not self.outpath.startswith("/pnfs/dune/scratch"):
            raise ValueError("Are you sure you want to put your files in {}?\nCheck this please...".format(self.outpath))

        if self.gevgen:
            self.genie_config = ConfigParser(_json=genie_config).decode_config()

        if self.gevgen:
            self.edep_config = ConfigParser(_json=edep_config).decode_config()

    def add_tar_dir_name(self, tar_dir_name):
        self.tar_dir_name = tar_dir_name

class GENIEConfiguration(Configuration):
    def __init__(self, copy_flux, genie, genie_xsec, genie_phyopt, geant4, ND_Production, sam_web_client) -> None:

        self.copy_flux = copy_flux
        
        self.genie          = ConfigParser(_json=genie).decode_config()
        self.genie_xsec     = ConfigParser(_json=genie_xsec).decode_config()
        self.genie_phyopt   = ConfigParser(_json=genie_phyopt).decode_config()
        self.geant4         = ConfigParser(_json=geant4).decode_config()
        self.ND_Production  = ConfigParser(_json=ND_Production).decode_config()
        self.sam_web_client = ConfigParser(_json=sam_web_client).decode_config()

class EDEPConfiguration(Configuration):
    def __init__(self, edepsim) -> None:

        self.edepsim = ConfigParser(_json=edepsim).decode_config()

class ProductConfiguration(Configuration):
    def __init__(self, version, qualifier) -> None:
        self.version = version
        self.qualifier = qualifier

class ConfigParser:
    def __init__(self, _path=None, _json=None) -> None:

        if _json is not None:
            self.config_json = _json
        elif _path is not None:
            with open(_path, 'r') as config_file:
                self.config_json = json.load(config_file)
        else:
            raise ValueError("You need to provide something!")

    def decode_config(self) -> Configuration:

        if '__type__' in self.config_json and self.config_json['__type__'] == 'GlobalConfiguration':
            del self.config_json['__type__']
            return GlobalConfiguration(**self.config_json)
        elif '__type__' in self.config_json and self.config_json['__type__'] == 'GENIEConfiguration':
            del self.config_json['__type__']
            return GENIEConfiguration(**self.config_json)
        elif '__type__' in self.config_json and self.config_json['__type__'] == 'EDEPConfiguration':
            del self.config_json['__type__']
            return EDEPConfiguration(**self.config_json)
        elif '__type__' in self.config_json and self.config_json['__type__'] == 'ProductConfiguration':
            del self.config_json['__type__']
            return ProductConfiguration(**self.config_json)
        else:
            raise ValueError("JSON file doesn't contain an instance of class Configuration")