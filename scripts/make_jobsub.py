import click

from garjobsubmaker import core

#----------------------------------------------------------------------------
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('config_path', type=click.Path(exists=True))
@click.option('--local_products', type=str, default="", show_default=True)
@click.option('--keep_dir', is_flag=True, default=False, show_default=True)
def cli(config_path: str, local_products: str, keep_dir: bool) -> None:

    jobsub = core.JobSubmission(config_path, path_to_local_product=local_products)

    jobsub.create_tar_dir()
    jobsub.create_setup_scripts()
    jobsub.add_other_files()
    jobsub.tar_and_delete(keep_dir)

    jobsub.create_run_script()
    jobsub.create_jobsub_script()

if __name__ == "__main__":

    cli()