import os

class JobSubScript:
    def __init__(self, script_name='./launch_job.sh') -> None:
        self.script_name = script_name

    def write(self, configuration):

        with open(self.script_name, 'w') as script:

            script.write('#!/bin/bash \n\n')

            jobsub_command = ['jobsub_submit']
            jobsub_command.append('-G dune')

            if configuration.mail:
                jobsub_command.append('--mail_always')

            jobsub_command.append('-N {}'.format(configuration.n_jobs))
            jobsub_command.append('--memory={}'.format(configuration.memory))
            jobsub_command.append('--disk={}'.format(configuration.disk))
            jobsub_command.append('--expected-lifetime={}'.format(configuration.lifetime))
            jobsub_command.append('--cpu={}'.format(configuration.cpu))

            jobsub_command.append('--resource-provides=usage_model={}'.format(','.join(configuration.resources)))

            jobsub_command.append('--tar_file_name=dropbox://{}'.format(configuration.tar_path))

            jobsub_command.append('''-l '+SingularityImage=\"/cvmfs/singularity.opensciencegrid.org/fermilab/fnal-dev-sl7:latest\"' ''') # triple quoted :S

            jobsub_command.append("--append_condor_requirements='(TARGET.HAS_Singularity==true&&TARGET.HAS_CVMFS_dune_opensciencegrid_org==true&&TARGET.HAS_CVMFS_larsoft_opensciencegrid_org==true&&TARGET.CVMFS_dune_opensciencegrid_org_REVISION>=1105&&TARGET.HAS_CVMFS_fifeuser1_opensciencegrid_org==true&&TARGET.HAS_CVMFS_fifeuser2_opensciencegrid_org==true&&TARGET.HAS_CVMFS_fifeuser3_opensciencegrid_org==true&&TARGET.HAS_CVMFS_fifeuser4_opensciencegrid_org==true)'")

            jobsub_command.append('-e GFAL_PLUGIN_DIR=/usr/lib64/gfal2-plugins') 
            jobsub_command.append('-e GFAL_CONFIG_DIR=/etc/gfal2.d')
            jobsub_command.append('-e UPS_OVERRIDE="-H Linux64bit+3.10-2.17"')

            jobsub_command.append('file://{}'.format(configuration.run_script_path))

            jobsub_command = ' '.join(jobsub_command)
            script.write(jobsub_command)

            script.write('\n\n')

            script.write('rm *.tbz2')
