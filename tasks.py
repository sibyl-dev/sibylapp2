from invoke import task
import subprocess


@task
def fix_lint(context):
    """
    Fixes all linting and import sort errors. Skips init.py files for import sorts
    """

    subprocess.run(["black", "sibylapp", "pages"])
    subprocess.run(["isort", "--atomic", "sibylapp", "pages"])
    subprocess.run(["pylint", "sibylapp", "pages"])


@task
def lint(context):
    """
    Runs the linting and import sort process on all library files and tests and prints errors.
        Skips init.py files for import sorts
    """
    subprocess.run(["pylint", "sibylapp", "pages"], check=True)
    subprocess.run(["isort", "--check-only", "sibylapp", "pages"], check=True)
