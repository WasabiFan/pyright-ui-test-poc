"""pytest test setup module, global for all tests."""

# make typecheck_snapshot fixture available globally, see here:
# https://docs.pytest.org/en/latest/reference/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files
from tests._test_utils.typechecker_ui_testing import typecheck_snapshot

# indicate to linters that the import is used
__all__ = ["typecheck_snapshot"]
