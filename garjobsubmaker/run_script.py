import os

#!/bin/bash

class RunScript:
    def __init__(self, script_name='./run_script.sh') -> None:
        self.script_name = script_name

    def write(self, configuration):

        with open(self.script_name, 'w') as script:
            script.write('#!/bin/bash \n\n')
            script.write('echo "Running on $(hostname) at ${GLIDEIN_Site}. GLIDEIN_DUNESite = ${GLIDEIN_DUNESite}" \n\n')

            script.write('OUTDIR={} \n\n'.format(configuration.outpath))

            if configuration.gevgen:
                script.write('OUTFILE_GENIE=gar_genie_${CLUSTER}_${PROCESS}_$(date -u +%Y%m%d).root \n')
            
            if configuration.edepsim:
                script.write('OUTFILE_EDEP=gar_edep_${CLUSTER}_${PROCESS}_$(date -u +%Y%m%d).root \n')

            script.write('\n')

            script.write('if [ -e ${{INPUT_TAR_DIR_LOCAL}}/{}/setup_grid_global.sh ]; then \n'.format(configuration.tar_dir_name))
            script.write('    . ${{INPUT_TAR_DIR_LOCAL}}/{}/setup_grid_global.sh \n'.format(configuration.tar_dir_name))
            script.write('else \n')
            script.write('  echo "Error, setup script not found. Exiting." \n')
            script.write('  exit 1 \n')
            script.write('fi \n\n')

            script.write('cd ${_CONDOR_JOB_IWD} \n\n')

            script.write('export IFDH_CP_MAXRETRIES=2 \n')
            script.write('export XRD_CONNECTIONRETRY=32 \n')
            script.write('export XRD_REQUESTTIMEOUT=14400 \n')
            script.write('export XRD_REDIRECTLIMIT=255 \n')
            script.write('export XRD_LOADBALANCERTTL=7200 \n')
            script.write('export XRD_STREAMTIMEOUT=14400 \n\n')

            script.write('ifdh ls $OUTDIR 0 \n')
            script.write('if [ $? -ne 0 ]; then \n')
            script.write('    ifdh mkdir_p $OUTDIR || { echo "Error creating or checking $OUTDIR"; exit 2; } \n')
            script.write('fi \n\n')

            if configuration.gevgen:

                script.write('if [ -e ${{INPUT_TAR_DIR_LOCAL}}/{}/setup_grid_genie.sh ]; then \n'.format(configuration.tar_dir_name))
                script.write('    . ${{INPUT_TAR_DIR_LOCAL}}/{}/setup_grid_genie.sh \n'.format(configuration.tar_dir_name))
                script.write('else \n')
                script.write('  echo "Error, GENIE setup script not found. Exiting." \n')
                script.write('  exit 1 \n')
                script.write('fi \n\n')

                gevgen_command = ['gevgen_fnal']
                gevgen_command.append('-f ${{INPUT_TAR_DIR_LOCAL}}/{}/flux_files/gsimple*,DUNEND'.format(configuration.tar_dir_name))
                gevgen_command.append('-g ${{INPUT_TAR_DIR_LOCAL}}/{}/geometries/nd_hall_mpd_only_ECal12sides_42l_SPY_v3_wMuID.gdml'.format(configuration.tar_dir_name))
                gevgen_command.append('-t volGArTPC')
                gevgen_command.append('-L cm -D g_cm3')
                gevgen_command.append('-n {}'.format(configuration.n_events))
                gevgen_command.append('--seed $(date -u +%Y%m%d%H%M%S)')
                gevgen_command.append('-r ${RUN}')
                gevgen_command.append('-o neutrino_gar')
                gevgen_command.append('--message-thresholds ${ND_PRODUCTION_CONFIG}/Messenger_production.xml')
                gevgen_command.append('--event-record-print-level 0')
                gevgen_command.append('--cross-sections $GENIEXSECFILETOUSE --tune $GENIE_XSEC_TUNE')

                gevgen_command = ' '.join(gevgen_command)
                script.write(gevgen_command)
                script.write('\n')

                script.write('GENIE_RESULT=$? \n')
                script.write('if [ $GENIE_RESULT -ne 0 ]; then \n')
                script.write('    echo "GENIE exited with abnormal status $GENIE_RESULT. See error outputs." \n')
                script.write('    exit $GENIE_RESULT \n')
                script.write('fi \n\n')

                script.write('cp neutrino_gar.10000.ghep.root $OUTFILE_GENIE \n')
                script.write('ifdh cp -D $OUTFILE_GENIE $OUTDIR \n\n')

                script.write('IFDH_RESULT=$? \n')
                script.write('if [ $IFDH_RESULT -ne 0 ]; then \n')
                script.write('    echo "Error during output copyback. See output logs." \n')
                script.write('    exit $IFDH_RESULT \n')
                script.write('fi \n\n')

                script.write('rm $OUTFILE_GENIE \n')

                script.write('\n')

            if configuration.edepsim:

                script.write('if [ -e ${{INPUT_TAR_DIR_LOCAL}}/{}/setup_grid_edep.sh ]; then \n'.format(configuration.tar_dir_name))
                script.write('    . ${{INPUT_TAR_DIR_LOCAL}}/{}/setup_grid_edep.sh \n'.format(configuration.tar_dir_name))
                script.write('else \n')
                script.write('  echo "Error, edep-sim setup script not found. Exiting." \n')
                script.write('  exit 1 \n')
                script.write('fi \n\n')

                edep_command = ['edep-sim -C']
                edep_command.append('-o ${EDEP_OUTPUT_FILE}')
                edep_command.append('-g ${{INPUT_TAR_DIR_LOCAL}}/{}/geometries/nd_hall_mpd_only_ECal12sides_42l_SPY_v3_wMuID.gdml'.format(configuration.tar_dir_name))
                edep_command.append('-e ${NSPILL}')
                edep_command.append('dune-nd.mac')

                edep_command = ' '.join(edep_command)
                script.write(edep_command)
                script.write('\n')

                script.write('EDEP_RESULT=$? \n')
                script.write('if [ $EDEP_RESULT -ne 0 ]; then \n')
                script.write('    echo "edep-sim exited with abnormal status $EDEP_RESULT. See error outputs." \n')
                script.write('    exit $EDEP_RESULT \n')
                script.write('fi \n\n')

                script.write('cp neutrino_gar.10000.edep.root $OUTFILE_EDEP \n')
                script.write('ifdh cp -D $OUTFILE_EDEP $OUTDIR \n\n')

                script.write('IFDH_RESULT=$? \n')
                script.write('if [ $IFDH_RESULT -ne 0 ]; then \n')
                script.write('    echo "Error during output copyback. See output logs." \n')
                script.write('    exit $IFDH_RESULT \n')
                script.write('fi \n\n')

                script.write('rm $OUTFILE_EDEP \n')

                script.write('\n')

            script.write('echo "Completed successfully." \n')
            script.write('exit 0 \n')
            script.write('\n')