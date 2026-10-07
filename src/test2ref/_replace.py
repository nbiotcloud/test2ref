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

"""Replacement helpers for generated reference data."""

import os
import re
from collections.abc import Callable, Iterator
from pathlib import Path

from binaryornot.check import is_binary

from ._config import ENCODING, ENCODING_ERRORS, Replacements, StrReplacements


def _replace_path(path: Path, replacements: StrReplacements) -> None:
    paths = [path]
    while paths:
        path = paths.pop()
        orig = name = path.name
        for srch, rplc in replacements:
            name = name.replace(srch, rplc)
        if orig != name:
            path = path.replace(path.with_name(name))
        if path.is_dir():
            paths.extend(path.iterdir())


def _replace_content(path: Path, replacements: Replacements) -> None:
    """Replace ``replacements`` for text files in ``path``."""
    regex_funcs = tuple(_create_regex_funcs(replacements))
    for sub_path in tuple(path.glob("**/*")):
        if not sub_path.is_file() or is_binary(str(sub_path)):
            continue
        content = sub_path.read_text(encoding=ENCODING, errors=ENCODING_ERRORS)
        total = 0
        for regex, func in regex_funcs:
            content, counts = regex.subn(func, content)
            total += counts
        if total:
            sub_path.write_text(content, encoding=ENCODING, errors=ENCODING_ERRORS)


def _create_regex_funcs(replacements: Replacements) -> Iterator[tuple[re.Pattern, Callable]]:
    """Create Regular Expression for `search`."""
    for search, replace in replacements:
        if isinstance(search, re.Pattern):
            yield search, _substitute_str(replace)
        elif isinstance(search, Path):
            search_str = str(search)
            sep_esc = re.escape(os.sep)

            if os.altsep:
                doublesep = f"{os.sep}{os.sep}"

                search_repr = search_str.replace(os.sep, doublesep)
                doubleregex = rf"(?i){re.escape(search_repr)}([A-Za-z0-9\-_{sep_esc}{re.escape(os.altsep)}]*)\b"
                yield re.compile(f"{doubleregex}"), _substitute_path(replace, (doublesep, os.sep, os.altsep))

                altregex = rf"(?i){re.escape(search.as_posix())}([A-Za-z0-9\-_{sep_esc}{re.escape(os.altsep)}]*)\b"
                yield re.compile(f"{altregex}"), _substitute_path(replace, (os.sep, os.altsep))
                regex = rf"(?i){re.escape(search_str)}([A-Za-z0-9_{sep_esc}]*)\b"
            else:
                regex = rf"{re.escape(search_str)}([A-Za-z0-9_{sep_esc}]*)\b"
            yield re.compile(f"{regex}"), _substitute_path(replace, (os.sep,))
        else:
            yield re.compile(re.escape(search)), _substitute_str(replace)


def _substitute_path(replace: str, seps: tuple[str, ...] = ()):
    """Factory for Substitution Function."""

    def func(mat: re.Match) -> str:
        sub = mat.group(1)
        for sep in seps:
            sub = sub.replace(sep, "/")
        return f"{replace}{sub}"

    return func


def _substitute_str(replace: str):
    def func(mat: re.Match) -> str:
        return replace

    return func
