import os

class EDEPSetup:
    def __init__(self, script_name='./setup_edep_grid.sh') -> None:
        self.script_name = script_name

    def write(self, configuration):

        with open(self.script_name, 'w') as script:
            script.write('#!/bin/bash \n\n')

            script.write('RUN=10000 \n')
            script.write('cp neutrino_gar.${RUN}.ghep.root input_file.ghep.root \n')
            script.write('gntpc -i input_file.ghep.root -f rootracker --event-record-print-level 0 --message-thresholds ${ND_PRODUCTION_CONFIG}/Messenger_production.xml \n')
            script.write('NSPILL=$(echo "std::cout << gtree->GetEntries() << std::endl;" | genie -l -b input_file.ghep.root 2>/dev/null  | tail -1) \n')
            script.write('cat ${ND_PRODUCTION_CONFIG}/dune-nd.mac > dune-nd.mac \n')
            script.write('setup edepsim {} -q {} \n'.format(configuration.edep_config.edepsim.version, configuration.edep_config.edepsim.qualifier))
            script.write('EDEP_OUTPUT_FILE=neutrino_gar.${RUN}.edep.root \n')