GArJobSubMaker
========================

*Python tool to generate ND-GAr jobsub commands*

## Getting started
This tool has to be run within a SL7 container in one of the `dunegpvm` machines, as it relies on UPS. First, setup the DUNE environment and Python:
```
source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
setup python v3_9_2
```

A set of particular Python packages are required to run the tool. Make sure to include them in your environment by running:
```
pip install --user -r requirements.txt
```

Then, you can install the package:
```
python setup.py install --prefix ~/.local
```

The first time you install the tool you will have to copy the DUNE flux files. You can do that by running:
```
bash scripts/copy_and_check_fluxes.sh
```

## Usage

The module contains a main script, `make_jobsub.py`, which generates the tarball, the script that will be ran in the nodes and the script with the necessary `jobsub` command. You can run it by simply doing:
```
python scripts/make_jobsub.py path_to_your_config_dir
```

Now, from an Alma9 session, setup the DUNE environmet running:
```
source /cvmfs/larsoft.opensciencegrid.org/spack-packages/setup-env.sh 
```
Then, launch the grid job by executting:
```
bash launch_job.sh
```

### Disclaimer
The aim of this tool is to automate the process of generating neutrino interaction samples in ND-GAr. It has been tested with different configurations and has provided good results in the past.

However, it is very much under development, it is not officially maintained by DUNE nor Fermilab and it may not be perfect. Therefore, **CHECK ALL THE FILES BEFORE SUBMITTING A JOB**. The authors and contributors of this repository are not liable for any misuse or damage that may result from using these tools. By using the tools in this repository, you agree to take full responsibility for your actions and any consequences that may arise.

## Configurations
The different options needed to run the script are passes in the form of JSON files.

## Contact

Francisco Martínez López ([f.martinezlopez@qmul.ac.uk](mailto:f.martinezlopez@qmul.ac.uk)), current lead author and maintainer.