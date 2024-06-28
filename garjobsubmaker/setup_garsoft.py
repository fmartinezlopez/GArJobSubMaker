import os

class GArSoftSetup:
    def __init__(self, script_name='./setup_gsft_grid.sh') -> None:
        self.script_name = script_name

    def write(self, configuration):

        with open(self.script_name, 'w') as script:
            script.write('#!/bin/bash \n\n')

            if configuration.gevgen:
                script.write('unsetup ifdhc \n')
                script.write('unsetup lhapdf \n')
                script.write('unsetup genie \n')
                script.write('unsetup sam_web_client \n')

                # For some reason not doing this triggers a weird version conflict problem...
                script.write('setup edepsim {} -q {} \n'.format(configuration.edep_config.edepsim.version, configuration.edep_config.edepsim.qualifier))
                script.write('unsetup edepsim \n')

            if configuration.edepsim:
                script.write('unsetup edepsim \n')

            script.write('export MRB_PROJECT=garsoft \n')
            script.write('source ${{INPUT_TAR_DIR_LOCAL}}/{}/garsoft/localProducts*/setup-grid \n'.format(configuration.tar_dir_name))
            script.write('mrbslp \n')
            script.write('\n')
