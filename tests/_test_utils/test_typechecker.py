import pytest
from pytest_snapshot.plugin import Snapshot  # type: ignore

from tests._test_utils.typechecker import TypecheckContext
from tests._test_utils.typechecker_ui_testing import PROJECT_DEFAULT_PYRIGHT_CONFIG, ui_test


@ui_test
def test__check_snippet__identifies_passing_typecheck():
    # Given
    context = TypecheckContext(PROJECT_DEFAULT_PYRIGHT_CONFIG)
    code = """
    def some_function(v: int) -> int:
        return v * 2
    value: int = some_function(3)
    """

    # When
    result = context.check_snippet(code)

    # Then
    assert result.passed
    assert result.output == ""


@ui_test
def test__check_snippet__identifies_failing_typecheck(
    snapshot: Snapshot, request: pytest.FixtureRequest
):
    # Given
    context = TypecheckContext(PROJECT_DEFAULT_PYRIGHT_CONFIG)
    code = """
    def some_function(v: int) -> str:
        return v * 2
    value: int = some_function(3)
    """

    # When
    result = context.check_snippet(code)

    # Then
    assert not result.passed
    snapshot.assert_match(result.output, f"{request.node.name}.txt")


@ui_test
def test__check_snippet__imports_local_files(snapshot: Snapshot, request: pytest.FixtureRequest):
    # Given
    context = TypecheckContext(PROJECT_DEFAULT_PYRIGHT_CONFIG)
    code = """
    from pyright_ui_test_poc import SampleLibraryClass
    _ = reveal_type(SampleLibraryClass)
    """

    # When
    result = context.check_snippet(code)

    # Then
    assert result.passed
    snapshot.assert_match(result.output, f"{request.node.name}.txt")
