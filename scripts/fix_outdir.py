import os
import shutil
import fnmatch
from os import walk
import re
from typing import List
from pathlib import Path

import click

def get_datafile_list(data_path: str, match_exprs: List[str] = ["*.root"]) -> List[str]:

    """ Get a list with the names of the files in a certain directory
        containing a substring from a list.

    Args:
        data_path (str): Path to directory of interest.
        match_exprs (list, optional): List of expressions to test. Defaults to ["*.root"].

    Returns:
        list: List of file names in directory with matching substring(s).
    """

    files = []
    for m in match_exprs:
        files += fnmatch.filter(next(walk(data_path), (None, None, []))[2], m)  # [] if no file

    return sorted(files, reverse=True, key=lambda f: os.path.getmtime(os.path.join(data_path, f)))

def sorted_nicely(files: List[str]) -> List[str]:

    """ Sort the given iterable in the way that humans expect.

    Args:
        files (list): List of strings to sort (typically list of file names).

    Returns:
        list: Sorted list.
    """

    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(files, key = alphanum_key)

class Job():

    def __init__(self, genie: bool, edep: bool, reco: bool, ana: bool) -> None:

        self.check = {"ghep": genie,
                      "edep": edep,
                      "reco": reco,
                      "ana": ana}

        self.ghep = None
        self.edep = None
        self.reco = None
        self.ana = None

    def set_ghep(self, file: Path) -> None:
        self.ghep = file

    def set_edep(self, file: Path) -> None:
        self.edep = file

    def set_reco(self, file: Path) -> None:
        self.reco = file

    def set_ana(self, file: Path) -> None:
        self.ana = file

    def check_and_set(self, file: Path) -> None:

        if ("genie" in file.stem) | ("ghep" in file.stem):
            self.set_ghep(file)
        elif "edep" in file.stem:
            self.set_edep(file)
        elif "reco" in file.stem:
            self.set_reco(file)
        elif "ana" in file.stem:
            self.set_ana(file)
        else:
            raise ValueError("Invalid input file!")
    
    def check_complete(self):

        if self.check["ghep"]:
            if self.ghep is not None:
                pass
            else:
                return False
        if self.check["edep"]:
            if self.edep is not None:
                pass
            else:
                return False
        if self.check["reco"]:
            if self.reco is not None:
                pass
            else:
                return False
        if self.check["ana"]:
            if self.ana is not None:
                pass
            else:
                return False
        return True

#----------------------------------------------------------------------------
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('path_to_dir', type=click.Path(exists=True))
@click.option('--name', type=str, default="ndgar_prod", show_default=True)
@click.option('--genie', is_flag=True, default=False, show_default=True)
@click.option('--edep', is_flag=True, default=False, show_default=True)
@click.option('--reco', is_flag=True, default=False, show_default=True)
@click.option('--ana', is_flag=True, default=False, show_default=True)
@click.option('--first_job', default=0, show_default=True)
def cli(path_to_dir: str, name: str, genie: bool, edep: bool, reco: bool, ana: bool, first_job: int = 0) -> None:

    path_to_dir = Path(path_to_dir)

    data_list = get_datafile_list(path_to_dir)
    data_list = sorted_nicely(data_list)
    data_list = list(map(Path, data_list))

    data_dict = {}

    for file in data_list:

        fid = [int(s) for s in re.findall(r'\d+', file.stem)]
        fid = tuple(fid)

        if fid not in data_dict:
            data_dict[fid] = Job(genie, edep, reco, ana)
            data_dict[fid].check_and_set(file)
        else:
            data_dict[fid].check_and_set(file)

    if genie:
        if os.path.exists(path_to_dir / "ghep"):
            shutil.rmtree(path_to_dir / "ghep")
        os.mkdir(path_to_dir / "ghep")
    if edep:
        if os.path.exists(path_to_dir / "edep"):
            shutil.rmtree(path_to_dir / "edep")
        os.mkdir(path_to_dir / "edep")
    if reco:
        if os.path.exists(path_to_dir / "reco"):
            shutil.rmtree(path_to_dir / "reco")
        os.mkdir(path_to_dir / "reco")
    if ana:
        if os.path.exists(path_to_dir / "ana"):
            shutil.rmtree(path_to_dir / "ana")
        os.mkdir(path_to_dir / "ana")

    ijob = first_job
    for fid, job in data_dict.items():
        if data_dict[fid].check_complete():
            print(data_dict[fid].ghep, data_dict[fid].ana)
            if genie:
                genie_name = name+"_ghep"+"_{0:05d}.root".format(ijob)
                shutil.copy(path_to_dir / data_dict[fid].ghep.name, path_to_dir / "ghep" / genie_name)
            if edep:
                edep_name = name+"_edep"+"_{0:05d}.root".format(ijob)
                shutil.copy(path_to_dir / data_dict[fid].edep.name, path_to_dir / "edep" / edep_name)
            if reco:
                reco_name = name+"_reco"+"_{0:05d}.root".format(ijob)
                shutil.copy(path_to_dir / data_dict[fid].reco.name, path_to_dir / "reco" / reco_name)
            if ana:
                ana_name = name+"_ana"+"_{0:05d}.root".format(ijob)
                shutil.copy(path_to_dir / data_dict[fid].ana.name, path_to_dir / "ana" / ana_name)

            ijob += 1

if __name__ == "__main__":

    cli()