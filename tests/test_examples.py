# The _test_utils/ directory includes tests which exercise all functionality of the typechecking
# utilities. The below are intended to give a sampling of the overall behavior and usage.

import pytest
from pytest_snapshot.plugin import Snapshot  # type: ignore

from tests._test_utils.typechecker import TypecheckContext
from tests._test_utils.typechecker_ui_testing import (
    PROJECT_DEFAULT_PYRIGHT_CONFIG,
    TypecheckSnapshotFixture,
    ui_test,
)


# applying a pytest "marker" allows you to filter these tests out (or run them exclusively) if
# desired
@pytest.mark.ui_test  # or, use the alias "@ui_test"
def test__manual_typechecker_invocation():
    # Given
    context = TypecheckContext(PROJECT_DEFAULT_PYRIGHT_CONFIG)
    code = """
    def foo(a: int, b: str):
        _ = a + b
    """

    # When
    result = context.check_snippet(code)

    # Then
    assert not result.passed
    # Pyright errors typically have multiple lines, and include non-breaking spaces mixed in with
    # normal ones. These make it difficult to work with in source code assertions. I recommend using
    # "snapshot tests" via external text files instead of the below.
    assert (
        'snippet.py:3:9 - error: Operator "+" not supported for types "int" and "str"'
        in result.output
    )


@ui_test
def test__manual_snapshot_test(snapshot: Snapshot, request: pytest.FixtureRequest):
    """
    This test is the same as above, but uses pytest-snapshot to validate the entirety of Pyright's
    output.
    """

    # Given
    context = TypecheckContext(PROJECT_DEFAULT_PYRIGHT_CONFIG)
    code = """
    def foo(a: int, b: str):
        _ = a + b
    """

    # When
    result = context.check_snippet(code)

    # Then
    assert not result.passed
    snapshot.assert_match(result.output, f"{request.node.name}.txt")


@ui_test
def test__basic_fixture_snapshot_test(
    typecheck_snapshot: TypecheckSnapshotFixture,
):
    """
    A further equivalent way to write the above test, now using the provided pytest "fixture".

    This is the approach I actually suggest using, rather than any of the above.
    """
    typecheck_snapshot.assert_failing_typecheck(
        """
        def foo(a: int, b: str):
            _ = a + b
        """
    )


@ui_test
def test__passing_fixture_snapshot_test(
    typecheck_snapshot: TypecheckSnapshotFixture,
):
    """
    The fixture provides both "assert_passing_typecheck" and "assert_failing_typecheck" helpers.
    """
    typecheck_snapshot.assert_passing_typecheck(
        """
        def foo(a: int, b: int):
            _ = a + b
        """
    )


@ui_test
def test__import_library_code(
    typecheck_snapshot: TypecheckSnapshotFixture,
):
    """
    The child Pyright process inherits our enclosing environment, including PYTHONPATH. So we can
    import from our project. This is the main point of these tests -- testing your own code.
    """
    typecheck_snapshot.assert_passing_typecheck(
        """
        from pyright_ui_test_poc import SampleLibraryClass
        instance = SampleLibraryClass()
        """
    )


@ui_test
def test__reveal_type(
    typecheck_snapshot: TypecheckSnapshotFixture,
):
    """
    "reveal_type" works as usual, so you can test that inferred/implied types are as intended.
    """
    typecheck_snapshot.assert_passing_typecheck(
        """
        from pyright_ui_test_poc import what_does_this_return

        value = what_does_this_return()
        reveal_type(value)
        """
    )
