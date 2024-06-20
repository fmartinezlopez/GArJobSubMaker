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

#----------------------------------------------------------------------------
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--path_to_ghep', type=str, default="", show_default=True)
@click.option('--path_to_ana', type=str, default="", show_default=True)
@click.option('--path_to_caf', type=str, default="", show_default=True)
@click.option('--path_to_cafmaker', type=str, default="", show_default=True)
@click.option('--out_name', type=str, default="gar_caf", show_default=True)
@click.option('--flat', is_flag=True, default=False, show_default=True)
def cli(path_to_ghep: str, path_to_ana: str, path_to_caf: str, path_to_cafmaker: str, out_name: str, flat: bool) -> None:

    ghep_list = get_datafile_list(path_to_ghep)
    ghep_list = sorted_nicely(ghep_list)

    ana_list = get_datafile_list(path_to_ana)
    ana_list = sorted_nicely(ana_list)

    n_ghep = len(ghep_list)
    n_ana = len(ana_list)

    if n_ghep == n_ana:
        n_jobs = n_ghep

        path_to_ghep = Path(path_to_ghep)
        path_to_ana = Path(path_to_ana)
        path_to_caf = Path(path_to_caf)
        path_to_cafmaker = Path(path_to_cafmaker)

        if os.path.exists(path_to_cafmaker / "cfg" / "caf_job"):
            shutil.rmtree(path_to_cafmaker / "cfg" / "caf_job")
        os.mkdir(path_to_cafmaker / "cfg" / "caf_job")
        
        for j in range(n_jobs):
            print(ghep_list[j], ana_list[j])
            fcl_path = path_to_cafmaker / "cfg" / "caf_job" / "ndcafmakerjob_{}.fcl".format(j)
            print(os.getcwd())
            shutil.copy("templates/ndcafmakerjob.fcl", fcl_path)

            os.system(r'''sed -i 's\flat_caf\{}\' {}'''.format("true" if flat else "false", fcl_path))
            os.system(r'''sed -i 's\ghep_path\"{}"\' {}'''.format(path_to_ghep / ghep_list[j], fcl_path))
            os.system(r'''sed -i 's\ndgar_reco_path\"{}"\' {}'''.format(path_to_ana / ana_list[j], fcl_path))
            os.system(r'''sed -i 's\out_path\"{}"\' {}'''.format(path_to_caf / ghep_list[j].replace('gar_genie', out_name), fcl_path))

    else:
        raise ValueError("Provided different numbers of GHEP and ana files!")

if __name__ == "__main__":

    cli()