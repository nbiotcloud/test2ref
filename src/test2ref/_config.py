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

"""Configuration and shared types."""

import re
from collections.abc import Iterable
from pathlib import Path
from typing import TypeAlias

PRJ_PATH = Path.cwd()

Search: TypeAlias = Path | str | re.Pattern
"""
Possible Search Pattern.

File System Path, string or regular expression.
"""

Replacements: TypeAlias = Iterable[tuple[Search, str]]
"""
Replacements - Pairs of Search Pattern and Things to be Replaced.
"""

StrReplacements: TypeAlias = Iterable[tuple[str, str]]
Excludes: TypeAlias = tuple[str, ...]


DEFAULT_REF_PATH: Path = PRJ_PATH / "tests" / "refdata"
DEFAULT_REF_UPDATE: bool = (PRJ_PATH / ".test2ref").exists()
DEFAULT_EXCLUDES: Excludes = ("__pycache__", ".tool_cache", ".cache")
DEFAULT_IGNORE_SPACES: bool = False
CONFIG = {
    "ref_path": DEFAULT_REF_PATH,
    "ref_update": DEFAULT_REF_UPDATE,
    "excludes": DEFAULT_EXCLUDES,
    "ignore_spaces": DEFAULT_IGNORE_SPACES,
}
ENCODING = "utf-8"
ENCODING_ERRORS = "surrogateescape"


def configure(
    ref_path: Path | None = None,
    ref_update: bool | None = None,
    excludes: Excludes | None = None,
    add_excludes: Excludes | None = None,
    rm_excludes: Excludes | None = None,
    ignore_spaces: bool | None = False,
) -> None:
    """
    Configure.

    Keyword Args:
        ref_path: Path for reference files. "tests/refdata" by default
        ref_update: Update reference files. True by default if `.test2ref` file exists.
        excludes: Paths to be excluded in all runs.
        add_excludes: Additionally Excluded Files
        rm_excludes: Not Excluded Files
        ignore_spaces: Ignore Space Changes - `False` by default
    """
    if ref_path is not None:
        CONFIG["ref_path"] = ref_path
    if ref_update is not None:
        CONFIG["ref_update"] = ref_update
    if excludes:
        CONFIG["excludes"] = excludes
    if add_excludes:
        CONFIG["excludes"] = (*CONFIG["excludes"], *add_excludes)
    if rm_excludes:
        CONFIG["excludes"] = tuple(exclude for exclude in CONFIG["excludes"] if exclude not in rm_excludes)  # type: ignore[attr-defined]
    if ignore_spaces is not None:
        CONFIG["ignore_spaces"] = ignore_spaces
