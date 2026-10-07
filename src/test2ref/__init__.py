#
# MIT License
#
# Copyright (c) 2024-2026 nbiotcloud
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""
Testing Against Learned Reference Data.

# Concept

A unit test creates files in a temporary folder `tmp_path`.
:any:`assert_refdata()` is called at the end of the test.

There are two modes:

* **Testing**: Test result in `tmp_path` is compared against a known reference.
  Any deviation in the files, causes a fail.
* **Learning**: The test result in `tmp_path` is taken as reference and is copied
  to the reference folder, which should be committed to version control and kept as
  reference.

The file `.test2ref` in the project root directory selects the operation mode.
If the file exists, **Learning Mode** is selected.
If the files does **not** exists, the **Testing Mode** is selected.

Next to that, stdout, stderr and logging can be included in the reference automatically.

# Minimal Example

!!! example

    ```python
    >>> def test_something(tmp_path, capsys):
    ...     (tmp_path / "file.txt").write_text("Hello Mars")
    ...     print("Hello World")
    ...     assert_refdata(test_something, tmp_path, capsys=capsys)

    ```

# API
"""

from ._compare import assert_paths, assert_refdata
from ._config import (
    CONFIG,
    Excludes,
    Replacements,
    Search,
    StrReplacements,
    configure,
)

__all__ = [
    "CONFIG",
    "Excludes",
    "Replacements",
    "Search",
    "StrReplacements",
    "assert_paths",
    "assert_refdata",
    "configure",
]
