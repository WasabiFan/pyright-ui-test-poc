from tests._test_utils.typechecker_ui_testing import TypecheckSnapshotFixture, ui_test


@ui_test
def test__typecheck_snapshot_fixture__identifies_passing_typecheck(
    typecheck_snapshot: TypecheckSnapshotFixture,
):
    typecheck_snapshot.assert_passing_typecheck(
        """
        value = 5
        _ = reveal_type(value)
        """
    )


@ui_test
def test__typecheck_snapshot_fixture__identifies_failing_typecheck(
    typecheck_snapshot: TypecheckSnapshotFixture,
):
    typecheck_snapshot.assert_failing_typecheck(
        """
        value = 5 + "notanint"
        """
    )


@ui_test
def test__typecheck_snapshot_fixture__handles_multiple_snapshots(
    typecheck_snapshot: TypecheckSnapshotFixture,
):
    typecheck_snapshot.assert_passing_typecheck(
        """
        value = 5
        _ = reveal_type(value)
        """,
        snapshot_id=1,
    )

    typecheck_snapshot.assert_passing_typecheck(
        """
        value = "foo"
        _ = reveal_type(value)
        """,
        snapshot_id=2,
    )
