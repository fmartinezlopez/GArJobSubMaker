#!/bin/bash
source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh

setup ND_Production v01_05_00 -q e17:prof
setup ifdhc

${ND_PRODUCTION_DIR}/bin/copy_dune_flux --top /cvmfs/dune.osgstorage.org/pnfs/fnal.gov/usr/dune/persistent/stash/Flux/g4lbne/v3r5p4/QGSP_BERT/OptimizedEngineeredNov2017 --flavor neutrino --maxmb=2000
ls flux_files/ -alh
rm flux_*