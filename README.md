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

## Configurations
The different options needed to run the script are passes in the form of JSON files.