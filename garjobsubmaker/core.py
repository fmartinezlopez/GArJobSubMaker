import os
import shutil
from pathlib import Path

from garjobsubmaker import config_reader

from garjobsubmaker import run_script

from garjobsubmaker import setup_genie
from garjobsubmaker import setup_edep

from garjobsubmaker import jobsub_command

class JobSubmission:
    def __init__(self, path_to_config, path_to_tar_dir="./jobsubdir", path_to_tar="jobsub.tar.gz") -> None:

        parser = config_reader.ConfigParser(path_to_config)
        self.config = parser.decode_configs()

        path_to_tar_dir = Path(path_to_tar_dir)
        path_to_tar = Path(path_to_tar)

        self.tar_dir = path_to_tar_dir
        self.tar     = path_to_tar

        self.config.add_tar_dir_name(path_to_tar_dir)
        self.config.add_tar_path(path_to_tar.absolute())

    def create_tar_dir(self) -> None:

        if os.path.exists(self.tar_dir):
            shutil.rmtree(self.tar_dir)
        os.mkdir(self.tar_dir)

    def tar_and_delete(self, keep_dir) -> None:

        os.system("tar czf {} {}".format(self.tar, self.tar_dir)) # tar directory
        if not keep_dir:
            shutil.rmtree(self.tar_dir)

    def create_setup_scripts(self):

        shutil.copy(self.config.defaults / "templates/setup_global_template.sh", self.tar_dir / "setup_grid_global.sh")

        if self.config.gevgen:
            setup_genie.GENIESetup(script_name=self.tar_dir / "setup_grid_genie.sh").write(self.config)

        if self.config.edepsim:
            setup_edep.EDEPSetup(script_name=self.tar_dir / "setup_grid_edep.sh").write(self.config)

    def add_other_files(self):
        if self.config.gevgen:
            os.mkdir(self.tar_dir / "flux_files")
            for file in os.listdir(self.config.defaults / "flux_files"):
                shutil.copy(self.config.defaults / "flux_files" / file, self.tar_dir / "flux_files" / file, follow_symlinks=False)

            os.mkdir(self.tar_dir / "geometries")
            for file in os.listdir(self.config.defaults / "geometries"):
                shutil.copy(self.config.defaults / "geometries" / file, self.tar_dir / "geometries" / file, follow_symlinks=False)

    def create_run_script(self):
        script = run_script.RunScript()
        script.write(self.config)

        run_script_path = Path(script.script_name)
        self.config.add_run_script_path(run_script_path.absolute())

    def create_jobsub_script(self):
        jobsub_command.JobSubScript().write(self.config)