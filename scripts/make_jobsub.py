import click

from garjobsubmaker import core

#----------------------------------------------------------------------------
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('config_path', type=click.Path(exists=True))
def cli(config_path: str) -> None:

    jobsub = core.JobSubmission(config_path)

    jobsub.create_tar_dir()
    jobsub.create_setup_scripts()
    jobsub.add_other_files()
    jobsub.tar_and_delete()

    jobsub.create_run_script()
    jobsub.create_jobsub_script()

if __name__ == "__main__":

    cli()