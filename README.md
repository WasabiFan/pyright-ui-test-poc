# pyright-ui-test-poc

A proof-of-concept demo of Pytest unit tests which evaluate Python code snippets under the Pyright
type-checker.

This concept was originally discussed here: https://github.com/microsoft/pyright/discussions/2163

The files in `tests/_test_utils/` are a self-contained library, and others should feel free to adopt
it for their own projects. Along with it, I recommend taking `tests/conftest.py` for easy
consumption of the Pytest fixture.

If others find it useful, I may consider in the future re-packaging this into a self-contained
library. However, it's a sufficiently small footprint and so far has only been exercised in a few
weeks of my own development, so for now I'm leaving it as a handful of loose-leaf files.

Please do reach out or open an issue with any questions or comments.

## Inspiration

This project takes inspiration from [`dtolnay/trybuild`](https://github.com/dtolnay/trybuild) and
similar projects in the Rust world. Although verifying the behavior of procedural macros is not
applicable to Python, I have found that there are other use-cases which deserve a similar mechanism.

## Use-case

With advanced Python type-checking tools now common and expressive syntax for generics and bounds
available, it is increasingly feasible to write Python interfaces which take advantage of static
type-checking for catching mistakes early in development.

I have recently found myself leaning heavily into patterns seen in strongly, statically-typed
languages with expressive type systems such as Rust. Typestate representations for specialized
variants of objects or partial application, measurement units, and reference frames have worked well
for me in Python. However, if I'm designing such an interface, I want to ensure two things:

- The typing does indeed enforce the conditions I expect
- My type-checker configuration will catch typing violations 

This code sample was my approach to addressing the above needs.

### Concrete example

Consider the following class used to represent a measurement in inches, mirroring the ["newtype"
pattern](https://doc.rust-lang.org/rust-by-example/generics/new_types.html) in languages like Rust:

```python
from dataclasses import dataclass

@dataclass
class Inches:
    value: int

    def __add__(self, other: 'Inches') -> 'Inches':
        return Inches(self.value + other.value)
```

This class can be used as follows:

```python
>>> a = Inches(5)
>>> # add two Inches measurements
>>> b = a + Inches(2)
>>> b
Inches(value=7)
```

If we were to accidentally add the `Inches` value to an untyped number, we'd get a runtime error:

```
>>> c = a + 2
AttributeError: 'int' object has no attribute 'value'
```

As currently written, this is good: the class has protected us from adding a value without explicit
units. However, what happens when we add `Inches` and `Centimeters`?

```python
>>> d = a + Centimeters(5)
>>> d
Inches(value=10)
```

There was no runtime error, because both classes have a `value` property. Fortunately, a
type-checker like Pyright would be able to identify this error at the usage site:

```
Operator "+" not supported for types "Inches" and "Centimeters"
```

With the type-checker, our strongly-typed wrapper class is a fairly robust safeguard against unit
confusion.

**Since I consider this type-checked behavior to be a feature of my library, I want to cover it with
automated tests documenting the functionality and protecting against regressions. The helpers in
this repo are designed to aid in that goal.**

**Footnote:**
There are potentially other ways to model similar functionality to the above, and typed wrappers
like we showed might not be to everyone's tastes. You can choose for yourself whether this
functionality is valuable to you.




## Structure and implementation

The re-usable "library" portion of this repo lives in `tests/_test_utils/`. The files are as follows:
- `typechecker.py`: A wrapper around the `pyright` command-line interface, which can invoke it and
  return its output
- `typechecker_ui_testing.py`: a Pytest "fixture" (`typecheck_snapshot`) which combines
  `typechecker.py` with the `pytest-snapshot` library to easily compare the output of Pyright
  against an expected string.
- `test_typechecker.py`: tests for `typechecker.py`
- `test_typechecker_ui_testing.py`: tests for `typechecker_ui_testing.py`
- `snapshots/`: output snapshot files for the associated tests

These (and any others of interest) can be copied into one's own project and modified as desired,
according to the license. Note that there is a hard-coded relative path to `pyproject.toml` (or
another Pyright configuration file) in `tests/_test_utils/typechecker_ui_testing.py`.

`tests/conftest.py` is Pytest configuration that makes the Pytest fixture available globally to all
tests. I recommend appropriating this file as well for your own project.

I've also provided documented examples in `tests/test_examples.py`, which are a good starting point
to get a sense of the interface.

## Usage

See `tests/test_examples.py` for an overview of the interface and its permutations.

In short, we might test the above example unit classes as follows:

```python
from tests._test_utils.typechecker_ui_testing import (
    TypecheckSnapshotFixture,
    ui_test,
)

@ui_test
def test__can_add_inches_to_inches(
    typecheck_snapshot: TypecheckSnapshotFixture,
):
    typecheck_snapshot.assert_passing_typecheck(
        """
        from my_library import Inches
        result = Inches(1) + Inches(2)
        """
    )

@ui_test
def test__adding_inches_to_centimeters_fails(
    typecheck_snapshot: TypecheckSnapshotFixture,
):
    typecheck_snapshot.assert_failing_typecheck(
        """
        from my_library import Inches, Centimeters
        result = Inches(1) + Centimeters(2)
        """
    )
```

Running `pytest --snapshot-update` would create two files describing Pyright's output in each test.
The first test would produce an empty file, while the second would include an error as discussed in
an earlier section. These files should be inspected and checked into source control. In the future,
the tests will fail if Pyright's output for those snippets changes, valid code begins to fail the
type-check, or invalid code begins to pass.

## Using this repo for testing

Feel free to clone and/or fork the repo to play with it. Pyright must be installed via npm for the
tests to be able to run it. This repo contains a Poetry project with appropriate dependencies, which
can be installed via `poetry install`. The following scripts are provided:

- `poetry run lint`: run linters
- `poetry run format`: run formatters
- `poetry run typecheck`: run Pyright on source code
- `poetry run test`: run tests
- `poetry run update-snapshots`: re-generate test snapshots
