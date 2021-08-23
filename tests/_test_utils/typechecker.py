"""
Utility class which wraps the "pyright" command-line interface.

Can be used for testing the behavior of type-annotated interfaces. See test_type_ui_testing.py for
example tests and type_ui_testing_fixture.py for a pytest-specific convenience wrapper.
"""

import re
import subprocess
import textwrap
from dataclasses import dataclass
from tempfile import NamedTemporaryFile


@dataclass
class TypecheckResult:
    output: str
    passed: bool


def _extract_error_output(pyright_stdout: str) -> str:
    regex = re.compile(
        r"^Found 1 source file\n([\s\S]*)(\d+) errors?, (\d+) warnings?, (\d+) infos?", re.MULTILINE
    )
    try:
        match = next(regex.finditer(pyright_stdout))
    except StopIteration:
        print("pyright output:")
        print(textwrap.indent(pyright_stdout, prefix=" " * 4))
        raise ValueError("pyright returned unexpected output")

    (error_output, _, _, _) = match.groups()

    return error_output


def _normalize_error_output(pyright_error_output: str, file_abspath: str) -> str:
    def _normalize_newlines(val: str) -> str:
        lines = val.strip().splitlines(keepends=False)
        return "\n".join(lines)

    def _sanitize_paths(val: str) -> str:
        return val.replace(file_abspath + ":", "snippet.py:").replace(
            file_abspath + "\n", "snippet.py\n"
        )

    result = pyright_error_output
    result = _normalize_newlines(result)
    result = _sanitize_paths(result)
    return result


class TypecheckContext:
    def __init__(self, config_file_path: str):
        self.config_file_path = config_file_path

    def check_snippet(self, code_snippet: str) -> TypecheckResult:
        code_snippet = textwrap.dedent(code_snippet)

        with NamedTemporaryFile("w", prefix="snippet_", suffix=".py") as snippet_file:
            _ = snippet_file.write(code_snippet)
            snippet_file.flush()

            process = subprocess.run(
                # Not secure, don't use for foreign input
                f'pyright -p "{self.config_file_path}" "{snippet_file.name}"',
                shell=True,
                capture_output=True,
                encoding="utf8",
            )

            stdout = process.stdout
            error_text = _extract_error_output(stdout)
            normalized_error_text = _normalize_error_output(error_text, snippet_file.name)

            # stderr is discarded, pyright does not print anything useful to stderr
            return TypecheckResult(
                output=normalized_error_text,
                passed=process.returncode == 0,
            )
