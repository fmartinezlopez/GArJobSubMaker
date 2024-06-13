import os
import shutil

from garjobsubmaker import config_reader
from garjobsubmaker import run_script
from garjobsubmaker import setup_genie
from garjobsubmaker import setup_edep

def copy_and_check_fluxes(config):
    os.system('setup ND_Production   {}       -q {} \n'.format(config.genie_config.ND_Production.version, config.genie_config.ND_Production.qualifier))
    os.system('${ND_PRODUCTION_DIR}/bin/copy_dune_flux --top /cvmfs/dune.osgstorage.org/pnfs/fnal.gov/usr/dune/persistent/stash/Flux/g4lbne/v3r5p4/QGSP_BERT/OptimizedEngineeredNov2017 --flavor neutrino --maxmb=100')
    os.system('ls flux_files/ -alh')

class JobSubmission:
    def __init__(self, path_to_config, path_to_tar_dir="./jobsubdir", path_to_tar="jobsub.tar.gz") -> None:

        self.pwd = os.path.dirname(os.path.realpath(__file__))

        parser = config_reader.ConfigParser(_path=path_to_config)
        self.config = parser.decode_config()
        self.config.add_tar_dir_name(path_to_tar_dir[2:])

        self.tar_dir = path_to_tar_dir
        self.tar     = path_to_tar

    def create_tar_dir(self) -> None:

        if os.path.exists(self.tar_dir):
            shutil.rmtree(self.tar_dir)
        os.mkdir(self.tar_dir)

    def tar_and_delete(self) -> None:

        os.system("tar czf {} {}".format(self.tar, self.tar_dir)) # tar directory
        shutil.rmtree(self.tar_dir)

    def create_setup_scripts(self):

        shutil.copy(self.pwd+"/../templates/setup_global_template.sh", self.tar_dir+"/setup_grid_global.sh")

        if self.config.gevgen:
            setup_genie.GENIESetup(script_name=self.tar_dir+"/setup_grid_genie.sh").write(self.config)

        if self.config.edepsim:
            setup_edep.EDEPSetup(script_name=self.tar_dir+"/setup_grid_edep.sh").write(self.config)

    def add_other_files(self):
        if self.config.gevgen & self.config.genie_config.copy_flux:
            copy_and_check_fluxes(self.config)
            shutil.copy(self.pwd+"/flux_files", self.tar_dir+"/flux_files")

    def create_run_script(self):
        run_script.RunScript().write(self.config)