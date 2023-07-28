from invoke import task
import subprocess


@task
def fix_lint(context):
    """
    Fixes all linting and import sort errors. Skips init.py files for import sorts
    """

    subprocess.run(["black", "sibylapp", "pages", "1_Explore_a_Prediction.py"])
    subprocess.run(["isort", "--atomic", "sibylapp", "pages", "1_Explore_a_Prediction.py"])


@task
def lint(context):
    """
    Runs the linting and import sort process on all library files and tests and prints errors.
        Skips init.py files for import sorts
    """
    subprocess.run(["pylint", "sibylapp", "pages", "1_Explore_a_Prediction.py"], check=True)
    subprocess.run(
        ["isort", "--check-only", "sibylapp", "pages", "1_Explore_a_Prediction.py"], check=True
    )
