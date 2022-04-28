
"""Main module of app2run CLI."""
import click

from app2run.commands.list_incompatible_features import list_incompatible_features

@click.group()
def cli():
    """app2run CLI."""

cli.add_command(list_incompatible_features)
