import click

from biocsetup.create_repository import create_repository

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


@click.command()
@click.argument("project_path")
@click.option("--description", "-d", help="Project description", default="Add a short description here!")
@click.option("--license", "-l", default="MIT", help="License (default: MIT)")
@click.option("--rst", "-rst", is_flag=True, help="Use rst for documentation, defaults to using markdown!")
@click.option("--pyscaffold", "-ps", is_flag=True, help="Use pyscaffold for project initialization instead of hatchit.")
def main(project_path: str, description: str, license: str, rst: bool, pyscaffold: bool):
    """Create a new BiocPy Python package."""
    create_repository(
        project_path=project_path,
        description=description,
        license=license,
        rst=rst,
        use_pyscaffold=pyscaffold,
    )


if __name__ == "__main__":
    main()
