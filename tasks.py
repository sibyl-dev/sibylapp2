import subprocess

from invoke import task


@task
def fix_lint(context):
    """
    Fixes all linting and import sort errors. Skips init.py files for import sorts
    """

    subprocess.run(["black", "sibylapp2", "main.py"])
    subprocess.run(["isort", "--atomic", "sibylapp2", "main.py"])


@task
def lint(context):
    """
    Runs the linting and import sort process on all library files and tests and prints errors.
        Skips init.py files for import sorts
    """
    subprocess.run(["pylint", "sibylapp2", "main.py"], check=True)
    subprocess.run(["isort", "--check-only", "sibylapp2", "main.py"], check=True)
