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
"""Tests for the optional pytest plugin."""

import pytest

pytest_plugins = ["pytester"]


@pytest.mark.parametrize(
    ("marker", "option", "expected"),
    [
        (False, (), False),
        (True, (), True),
        (False, ("--test2ref",), True),
        (True, ("--test2ref",), True),
        (False, ("--no-test2ref",), False),
        (True, ("--no-test2ref",), False),
    ],
)
def test_ref_update_option(pytester, monkeypatch, marker, option, expected):
    """The CLI overrides the marker default only when explicitly supplied."""
    if marker:
        (pytester.path / ".test2ref").touch()

    pytester.makepyfile(
        test_ref_update=f"""
from test2ref._config import CONFIG


def test_ref_update():
    assert CONFIG["ref_update"] is {expected}
"""
    )
    monkeypatch.setenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")

    result = pytester.runpytest_subprocess("-p", "test2ref._pytest_plugin", *option, "-q")

    assert result.ret == 0
