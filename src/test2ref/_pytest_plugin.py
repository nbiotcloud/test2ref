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
"""Optional pytest plugin for test2ref."""

from ._config import configure


def pytest_addoption(parser):
    """Add reference-update options."""
    group = parser.getgroup("test2ref")
    group.addoption(
        "--test2ref",
        action="store_true",
        dest="test2ref",
        default=None,
        help="Enforce Update of test2ref Reference Data - ignores .test2ref file",
    )
    group.addoption(
        "--no-test2ref",
        action="store_false",
        dest="test2ref",
        default=None,
        help="Enforce Compare of test2ref Reference Data - ignores .test2ref file",
    )


def pytest_configure(config):
    """Apply an explicit reference-update option."""
    ref_update = config.getoption("test2ref")
    if ref_update is not None:
        configure(ref_update=ref_update)
