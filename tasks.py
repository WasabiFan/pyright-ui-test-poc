"""
Tasks to be invoked via "poetry run".

Any task added here must also be specified as a "script" in pyproject.toml.
"""

import os
import subprocess
import sys
from typing import List, Union

repo_root = os.path.dirname(__file__)


def _command(command: Union[List[str], str], shell: bool = False):
    command_exit_code = subprocess.call(
        command,
        cwd=repo_root,
        shell=shell,
    )

    if command_exit_code != 0:
        sys.exit(command_exit_code)


def test():
    _command(["pytest"])


# alternately, separate "test" tasks for "ui tests" and "non ui tests"
# def test():
#     _command(["pytest", "-m", "not ui_test"])


# def ui_test():
#     _command(["pytest", "-m", "ui_test"])


def update_snapshots():
    _command(["pytest", "--snapshot-update"])


def lint():
    _command(["flakehell", "lint"])


def format():
    _command(["black", "."])
    _command(["isort", "."])


def typecheck():
    # shell=True because pyright installs as scripts "pyright.cmd" and "pyright.ps1" on Windows.
    # Passing through CMD will let it implicitly add the ".cmd".
    _command(["pyright"], shell=True)
