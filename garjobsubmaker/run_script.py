import os

#!/bin/bash

class RunScript:
    def __init__(self, script_name='./run_script.sh') -> None:
        self.script_name = script_name

    def write(self, configuration):

        with open(self.script_name, 'w') as script:
            script.write('#!/bin/bash \n\n')
            script.write('echo "Running on $(hostname) at ${GLIDEIN_Site}. GLIDEIN_DUNESite = ${GLIDEIN_DUNESite}" \n\n')

            # Set the output location for copyback
            script.write('OUTDIR={} \n\n'.format(configuration.outpath))

            # Let's rename the output file so it's unique in case we send multiple jobs
            if configuration.gevgen:
                script.write('OUTFILE_GENIE=gar_genie_${CLUSTER}_${PROCESS}_$(date -u +%Y%m%d).root \n')
            
            if configuration.edepsim:
                script.write('OUTFILE_EDEP=gar_edep_${CLUSTER}_${PROCESS}_$(date -u +%Y%m%d).root \n')

            if configuration.garsoft:
                script.write('OUTFILE_ANA=gar_ana_${CLUSTER}_${PROCESS}_$(date -u +%Y%m%d).root \n')
                if configuration.gsft_config.copy_reco:
                    script.write('OUTFILE_RECO=gar_reco_${CLUSTER}_${PROCESS}_$(date -u +%Y%m%d).root \n')

            script.write('\n')

            script.write('if [ -e ${{INPUT_TAR_DIR_LOCAL}}/{}/setup_grid_global.sh ]; then \n'.format(configuration.tar_dir_name))
            script.write('    . ${{INPUT_TAR_DIR_LOCAL}}/{}/setup_grid_global.sh \n'.format(configuration.tar_dir_name))
            script.write('else \n')
            script.write('  echo "Error, setup script not found. Exiting." \n')
            script.write('  exit 1 \n')
            script.write('fi \n\n')

            # cd back to the top-level directory since we know that's writable
            script.write('cd ${_CONDOR_JOB_IWD} \n\n')

            # Set some other very useful environment variables for xrootd and IFDH
            script.write('export IFDH_CP_MAXRETRIES=2 \n')
            script.write('export XRD_CONNECTIONRETRY=32 \n')
            script.write('export XRD_REQUESTTIMEOUT=14400 \n')
            script.write('export XRD_REDIRECTLIMIT=255 \n')
            script.write('export XRD_LOADBALANCERTTL=7200 \n')
            script.write('export XRD_STREAMTIMEOUT=14400 \n\n')

            # Make sure the output directory exists
            script.write('ifdh ls $OUTDIR 0 \n')
            # If ifdh ls failed, try to make the directory
            script.write('if [ $? -ne 0 ]; then \n')
            script.write('    ifdh mkdir_p $OUTDIR || { echo "Error creating or checking $OUTDIR"; exit 2; } \n')
            script.write('fi \n\n')

            if configuration.gevgen:

                # Run gevgen setup script
                script.write('if [ -e ${{INPUT_TAR_DIR_LOCAL}}/{}/setup_grid_genie.sh ]; then \n'.format(configuration.tar_dir_name))
                script.write('    . ${{INPUT_TAR_DIR_LOCAL}}/{}/setup_grid_genie.sh \n'.format(configuration.tar_dir_name))
                script.write('else \n')
                script.write('  echo "Error, GENIE setup script not found. Exiting." \n')
                script.write('  exit 1 \n')
                script.write('fi \n\n')

                # Put together gevgen command
                gevgen_command = ['gevgen_fnal']
                gevgen_command.append('-f ${{INPUT_TAR_DIR_LOCAL}}/{}/flux_files/gsimple*,DUNEND'.format(configuration.tar_dir_name))
                gevgen_command.append('-g ${{INPUT_TAR_DIR_LOCAL}}/{}/geometries/{}'.format(configuration.tar_dir_name, configuration.geometry))
                gevgen_command.append('-t {}'.format(configuration.genie_config.topvolume))
                gevgen_command.append('-L cm -D g_cm3')
                gevgen_command.append('-n {}'.format(configuration.n_events))
                #gevgen_command.append('--seed $(date -u +%Y%m%d%H%M%S)')
                gevgen_command.append('--seed {}${{PROCESS}}'.format(configuration.genie_config.seed))
                gevgen_command.append('-r ${RUN}')
                gevgen_command.append('-o neutrino_gar')
                gevgen_command.append('--message-thresholds ${ND_PRODUCTION_CONFIG}/Messenger_production.xml')
                gevgen_command.append('--event-record-print-level 0')
                gevgen_command.append('--cross-sections $GENIEXSECFILETOUSE --tune $GENIE_XSEC_TUNE')
                gevgen_command.append('\n')

                # Run gevgen
                gevgen_command = ' '.join(gevgen_command)
                script.write(gevgen_command)
                script.write('\n')

                # ALWAYS keep track of the exit status or your main commands!!!
                script.write('GENIE_RESULT=$? \n')
                script.write('if [ $GENIE_RESULT -ne 0 ]; then \n')
                script.write('    echo "GENIE exited with abnormal status $GENIE_RESULT. See error outputs." \n')
                script.write('    exit $GENIE_RESULT \n')
                script.write('fi \n\n')

                # Copy gevgen output
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

                # Run edep-sim setup script
                script.write('if [ -e ${{INPUT_TAR_DIR_LOCAL}}/{}/setup_grid_edep.sh ]; then \n'.format(configuration.tar_dir_name))
                script.write('    . ${{INPUT_TAR_DIR_LOCAL}}/{}/setup_grid_edep.sh \n'.format(configuration.tar_dir_name))
                script.write('else \n')
                script.write('  echo "Error, edep-sim setup script not found. Exiting." \n')
                script.write('  exit 1 \n')
                script.write('fi \n\n')

                # Put together edep-sim command
                edep_command = ['edep-sim -C']
                edep_command.append('-o ${EDEP_OUTPUT_FILE}')
                edep_command.append('-g ${{INPUT_TAR_DIR_LOCAL}}/{}/geometries/{}'.format(configuration.tar_dir_name, configuration.geometry))
                edep_command.append('-e ${NSPILL}')
                edep_command.append('dune-nd.mac')
                edep_command.append('\n')

                # Run edep-sim
                edep_command = ' '.join(edep_command)
                script.write(edep_command)
                script.write('\n')

                script.write('EDEP_RESULT=$? \n')
                script.write('if [ $EDEP_RESULT -ne 0 ]; then \n')
                script.write('    echo "edep-sim exited with abnormal status $EDEP_RESULT. See error outputs." \n')
                script.write('    exit $EDEP_RESULT \n')
                script.write('fi \n\n')

                # Copy edep-sim output
                script.write('cp neutrino_gar.10000.edep.root $OUTFILE_EDEP \n')
                script.write('ifdh cp -D $OUTFILE_EDEP $OUTDIR \n\n')

                script.write('IFDH_RESULT=$? \n')
                script.write('if [ $IFDH_RESULT -ne 0 ]; then \n')
                script.write('    echo "Error during output copyback. See output logs." \n')
                script.write('    exit $IFDH_RESULT \n')
                script.write('fi \n\n')

                script.write('rm $OUTFILE_EDEP \n')

                script.write('\n')

            if configuration.garsoft:

                # Run GArSoft setup script
                script.write('if [ -e ${{INPUT_TAR_DIR_LOCAL}}/{}/setup_grid_gsft.sh ]; then \n'.format(configuration.tar_dir_name))
                script.write('    . ${{INPUT_TAR_DIR_LOCAL}}/{}/setup_grid_gsft.sh \n'.format(configuration.tar_dir_name))
                script.write('else \n')
                script.write('  echo "Error, GArSoft setup script not found. Exiting." \n')
                script.write('  exit 1 \n')
                script.write('fi \n\n')

                if configuration.gevgen:

                    # If gevgen was used, convert its output to ART
                    script.write('cp ${{INPUT_TAR_DIR_LOCAL}}/{}/conversion_to_gsft.fcl . \n'.format(configuration.tar_dir_name))
                    script.write(r"sed -i 's\path_to_ghep\${PWD}/neutrino_gar.10000.ghep.root\' conversion_to_gsft.fcl")
                    script.write('\n')

                    if configuration.edepsim:

                        # If edep-sim was also used, convert its output to ART
                        script.write(r"sed -i 's\path_to_edep\${PWD}/neutrino_gar.10000.edep.root\' conversion_to_gsft.fcl")
                        script.write('\n')

                        convert_outname = "genie_g4"
                        fcl_subfix = "_edep"

                    else:

                        # If not, remove that bit from the fcl
                        script.write(r"sed -i 's\path_to_edep\\' conversion_to_gsft.fcl")
                        script.write('\n')

                        convert_outname = "genie"
                        fcl_subfix = ""

                    script.write('cat conversion_to_gsft.fcl \n')
                    
                    # Run conversion tool
                    script.write('art -c conversion_to_gsft.fcl -n {} -o {}.root \n'.format(configuration.n_events, convert_outname))
                    script.write('RESULT=$? \n')
                    script.write('if [ $RESULT -ne 0 ]; then \n')
                    script.write('    echo "GArSoft (conversion) exited with abnormal status $RESULT. See error outputs." \n')
                    script.write('    exit $RESULT \n')
                    script.write('fi \n\n')

                    if not configuration.edepsim:

                        # If we just ran gevgen we need to run GArG4 now on the conversion output
                        script.write('art -c rungeant4.fcl genie.root -n -1 -o genie_g4.root \n')
                        script.write('RESULT=$? \n')
                        script.write('if [ $RESULT -ne 0 ]; then \n')
                        script.write('    echo "GArSoft (GArG4) exited with abnormal status $RESULT. See error outputs." \n')
                        script.write('    exit $RESULT \n')
                        script.write('fi \n\n')

                else:

                    # If this is a standalone GArSoft job, run the default prodgenie
                    script.write('art -c prodgenie.fcl -n {} -o genie_g4.root \n'.format(configuration.n_events))
                    script.write('RESULT=$? \n')
                    script.write('if [ $RESULT -ne 0 ]; then \n')
                    script.write('    echo "GArSoft (prodgenie) exited with abnormal status $RESULT. See error outputs." \n')
                    script.write('    exit $RESULT \n')
                    script.write('fi \n\n')

                    fcl_subfix = ""

                # Run readout simulation
                script.write('art -c readoutsimjob{}.fcl genie_g4.root -n -1 -o readoutsim.root \n'.format(fcl_subfix))
                script.write('RESULT=$? \n')
                script.write('if [ $RESULT -ne 0 ]; then \n')
                script.write('    echo "GArSoft (readoutsim) exited with abnormal status $RESULT. See error outputs." \n')
                script.write('    exit $RESULT \n')
                script.write('fi \n\n')

                # Run reconstruction (with trackfit2 and trackecalassn2)
                script.write('art -c recojob_trackecalassn2{}.fcl readoutsim.root -n -1 -o reco.root \n'.format(fcl_subfix))
                script.write('RESULT=$? \n')
                script.write('if [ $RESULT -ne 0 ]; then \n')
                script.write('    echo "GArSoft (reco) exited with abnormal status $RESULT. See error outputs." \n')
                script.write('    exit $RESULT \n')
                script.write('fi \n\n')

                # Run PID algorithms
                script.write('art -c recoparticlesjob{}.fcl reco.root -n -1 -o reco2.root \n'.format(fcl_subfix))
                script.write('RESULT=$? \n')
                script.write('if [ $RESULT -ne 0 ]; then \n')
                script.write('    echo "GArSoft (recoparticles) exited with abnormal status $RESULT. See error outputs." \n')
                script.write('    exit $RESULT \n')
                script.write('fi \n\n')

                # Run analysis module (i.e. make ntuples)
                script.write('art -c anajob{}.fcl reco2.root -n -1 \n'.format(fcl_subfix))
                script.write('RESULT=$? \n')
                script.write('if [ $RESULT -ne 0 ]; then \n')
                script.write('    echo "GArSoft (anatree) exited with abnormal status $RESULT. See error outputs." \n')
                script.write('    exit $RESULT \n')
                script.write('fi \n\n')

                # Copy anatree
                script.write('cp anatree.root $OUTFILE_ANA \n')
                script.write('ifdh cp -D $OUTFILE_ANA $OUTDIR \n\n')

                script.write('IFDH_RESULT=$? \n')
                script.write('if [ $IFDH_RESULT -ne 0 ]; then \n')
                script.write('    echo "Error during output copyback. See output logs." \n')
                script.write('    exit $IFDH_RESULT \n')
                script.write('fi \n\n')

                script.write('rm $OUTFILE_ANA \n')

                if configuration.gsft_config.copy_reco:

                    # Copy reconstruction output
                    script.write('cp reco2.root $OUTFILE_RECO \n')
                    script.write('ifdh cp -D $OUTFILE_RECO $OUTDIR \n\n')

                    script.write('IFDH_RESULT=$? \n')
                    script.write('if [ $IFDH_RESULT -ne 0 ]; then \n')
                    script.write('    echo "Error during output copyback. See output logs." \n')
                    script.write('    exit $IFDH_RESULT \n')
                    script.write('fi \n\n')

                    script.write('rm $OUTFILE_RECO \n')


            script.write('echo "Completed successfully." \n')
            script.write('exit 0 \n')
            script.write('\n')