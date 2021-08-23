"""
pytest "fixture" providing an easy interface for running a Pyright typecheck and snapshot-testing
its output.

See test_type_ui_testing_fixture.py for examples.
"""

import os
import os.path
from typing import Optional, Set

import pytest
from pytest import FixtureRequest
from pytest_snapshot.plugin import Snapshot  # type: ignore

from tests._test_utils.typechecker import TypecheckContext

PROJECT_DEFAULT_PYRIGHT_CONFIG = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../pyproject.toml")
)

# function decorator alias for a "ui_test" marker
ui_test = pytest.mark.ui_test


class TypecheckSnapshotFixture:
    def __init__(
        self, snapshot_fixture: Snapshot, request_fixture: FixtureRequest, config_file_path: str
    ):
        self._context = TypecheckContext(config_file_path)
        self._snapshot_fixture = snapshot_fixture
        self._request_fixture = request_fixture

        self._generated_snapshots: Set[str] = set()

    def _assert_typecheck(
        self, code_snippet: str, should_pass: bool, snapshot_id: Optional[int] = None
    ):
        suffix = f"_{snapshot_id}" if snapshot_id is not None else ""
        snapshot_file_name = f"{self._request_fixture.node.name}{suffix}.txt"

        if snapshot_file_name in self._generated_snapshots:
            raise RuntimeError(
                f'attempted to overwrite already-generated snapshot "{snapshot_file_name}"'
            )
        self._generated_snapshots.add(snapshot_file_name)

        result = self._context.check_snippet(code_snippet)

        print("type check output:")
        print(result.output)

        assert result.passed == should_pass

        self._snapshot_fixture.assert_match(result.output, snapshot_file_name)

    def assert_passing_typecheck(self, code_snippet: str, snapshot_id: Optional[int] = None):
        self._assert_typecheck(code_snippet, True, snapshot_id)

    def assert_failing_typecheck(self, code_snippet: str, snapshot_id: Optional[int] = None):
        self._assert_typecheck(code_snippet, False, snapshot_id)


@pytest.fixture
def typecheck_snapshot(snapshot: Snapshot, request: FixtureRequest) -> TypecheckSnapshotFixture:
    return TypecheckSnapshotFixture(snapshot, request, PROJECT_DEFAULT_PYRIGHT_CONFIG)
