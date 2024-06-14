import os

class GENIESetup:
    def __init__(self, script_name='./setup_genie_grid.sh') -> None:
        self.script_name = script_name

    def write(self, configuration):

        with open(self.script_name, 'w') as script:
            script.write('#!/bin/bash \n\n')

            script.write('setup genie           {}       -q {} \n'.format(configuration.genie_config.genie.version,         configuration.genie_config.genie.qualifier))
            script.write('setup genie_xsec      {}       -q {} \n'.format(configuration.genie_config.genie_xsec.version,    configuration.genie_config.genie_xsec.qualifier))
            script.write('setup genie_phyopt    {}       -q {} \n'.format(configuration.genie_config.genie_phyopt.version,  configuration.genie_config.genie_phyopt.qualifier))
            script.write('setup geant4          {}       -q {} \n'.format(configuration.genie_config.geant4.version,        configuration.genie_config.geant4.qualifier))
            script.write('setup ND_Production   {}       -q {} \n'.format(configuration.genie_config.ND_Production.version, configuration.genie_config.ND_Production.qualifier))
            script.write('setup jobsub_client                  \n')
            script.write('setup cigetcert                      \n')
            script.write('setup sam_web_client  {}             \n'.format(configuration.genie_config.sam_web_client.version))
            script.write('\n')



            script.write('G4_cmake_file=`find ${GEANT4_FQ_DIR}/lib64 -name "Geant4Config.cmake"` \n')
            script.write('export Geant4_DIR=`dirname $G4_cmake_file` \n')
            script.write('export PATH=$PATH:$GEANT4_FQ_DIR/bin \n\n')

            script.write('RUN=10000 \n')
            script.write('RDIR=$((${RUN} / 1000)) \n')
            script.write('if [ ${RUN} -lt 10000 ]; then \n')
            script.write('RDIR=0$((${RUN} / 1000)) \n')
            script.write('fi \n\n')

            script.write('export GXMLPATH=${PWD}:${GXMLPATH} \n')
            script.write('export GNUMIXML="GNuMIFlux.xml" \n\n')

            script.write('GENIEXSECFILETOUSE=$GENIEXSECFILE \n')
            script.write('GENIEXSECFILETOUSE=`dirname $GENIEXSECFILE`/gxspl-FNALbig.xml.gz \n\n')