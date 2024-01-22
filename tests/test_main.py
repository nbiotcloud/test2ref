#
# MIT License
#
# Copyright (c) 2024 nbiotcloud
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
"""Basic Testing."""
import logging
import sys
from pathlib import Path
from unittest.mock import patch

from pytest import mark, raises

from test2ref import (
    CONFIG,
    DEFAULT_EXCLUDES,
    DEFAULT_REF_PATH,
    DEFAULT_REF_UPDATE,
    assert_paths,
    assert_refdata,
    configure,
)

LOGGER = logging.getLogger("dummy")


def test_configure(tmp_path):
    """Configure."""
    ref_path = tmp_path / "ref"

    config = {}
    with patch.dict(CONFIG, config):
        configure(ref_path=ref_path)
        assert CONFIG["ref_path"] == ref_path

        configure(ref_update=True)
        assert CONFIG["ref_update"]

        configure(excludes=("a", "b"))
        assert CONFIG["excludes"] == ("a", "b")

    assert CONFIG["ref_path"] == DEFAULT_REF_PATH
    assert CONFIG["ref_update"] == DEFAULT_REF_UPDATE
    assert CONFIG["excludes"] == DEFAULT_EXCLUDES


def _test(tmp_path: Path):
    (tmp_path / "file.txt").write_text("Content\n")
    (tmp_path / "blob").write_bytes(bytes(range(40)))
    (tmp_path / "some" / "where" / "deep").mkdir(parents=True)
    (tmp_path / "some" / "how").mkdir(parents=True)
    print("One")
    print("Two")
    print("myerr", file=sys.stderr)
    LOGGER.info("loginfo")
    LOGGER.warning("logwarn")


@mark.parametrize("fail", (False, True))
def test_default(tmp_path: Path, fail: bool):
    """Default Behaviour."""
    _test(tmp_path)
    if fail:
        (tmp_path / "file.txt").write_text("Other Content\n")

    if fail:
        configure(ref_update=False)
        with raises(AssertionError):
            assert_refdata(test_default, tmp_path)
    else:
        configure(ref_update=True)
        assert_refdata(test_default, tmp_path)

    ref_path = Path.cwd() / "tests" / "refdata" / "tests.test_main" / "test_default"
    assert len(tuple(ref_path.glob("**/*"))) == 2
    assert (ref_path / "file.txt").read_text() == "Content\n"


@mark.parametrize("fail", (False, True))
def test_capsys(tmp_path: Path, capsys, fail: bool):
    """Use of capsys."""
    _test(tmp_path)
    if fail:
        print("addition")

    if fail:
        configure(ref_update=False)
        with raises(AssertionError):
            assert_refdata(test_capsys, tmp_path, capsys=capsys)
    else:
        configure(ref_update=True)
        assert_refdata(test_capsys, tmp_path, capsys=capsys)

    ref_path = Path.cwd() / "tests" / "refdata" / "tests.test_main" / "test_capsys"
    assert len(tuple(ref_path.glob("**/*"))) == 4
    assert (ref_path / "file.txt").read_text() == "Content\n"
    assert (ref_path / "stdout.txt").read_text() == "One\nTwo\n"
    assert (ref_path / "stderr.txt").read_text() == "myerr\n"


@mark.parametrize("fail", (False, True))
def test_caplog(tmp_path: Path, caplog, fail: bool):
    """Use of caplog."""
    _test(tmp_path)
    if fail:
        LOGGER.warning("addition")

    if fail:
        configure(ref_update=False)
        with raises(AssertionError):
            assert_refdata(test_caplog, tmp_path, caplog=caplog)
    else:
        configure(ref_update=True)
        assert_refdata(test_caplog, tmp_path, caplog=caplog)

    ref_path = Path.cwd() / "tests" / "refdata" / "tests.test_main" / "test_caplog"
    assert len(tuple(ref_path.glob("**/*"))) == 3
    assert (ref_path / "file.txt").read_text() == "Content\n"
    assert (ref_path / "logging.txt").read_text() == "INFO     dummy  loginfo\nWARNING  dummy  logwarn\n"


def test_replace(tmp_path: Path):
    """Test Replacements."""

    one_path = tmp_path / "one" / "deep"
    other_path = tmp_path / "other"

    one_path.mkdir(parents=True)
    (one_path / "file.txt").write_text(f"Something\n Over Multiple Lines\n With {one_path}/inside\n {other_path} too")

    configure(ref_update=False)
    replacements = [
        (other_path, "$OTHER_PATH"),
        ("Over", "RAINBOW"),
    ]
    assert_refdata(test_replace, one_path, replacements=replacements)


def test_default_excludes(tmp_path: Path):
    """Text Default Excludes."""

    (tmp_path / "file.txt").touch()
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "file.pyc").touch()
    (tmp_path / ".tool_cache").mkdir()
    (tmp_path / ".tool_cache" / "file.pyc").touch()
    (tmp_path / "sub" / ".tool_cache").mkdir(parents=True)
    (tmp_path / "sub" / ".tool_cache" / "file.pyc").touch()
    (tmp_path / "sub" / "__pycache__").mkdir(parents=True)
    (tmp_path / "sub" / "__pycache__" / "file.txt").touch()
    (tmp_path / "sub" / ".cache").touch()

    configure(ref_update=False)
    assert_refdata(test_default_excludes, tmp_path)

    assert (tmp_path / "file.txt").exists()
    assert (tmp_path / "__pycache__" / "file.pyc").exists()
    assert (tmp_path / ".tool_cache" / "file.pyc").exists()
    assert (tmp_path / "sub" / ".tool_cache" / "file.pyc").exists()
    assert (tmp_path / "sub" / ".cache").exists()

    ref_path = Path.cwd() / "tests" / "refdata" / "tests.test_main" / "test_default_excludes"
    assert (ref_path / "file.txt").exists()
    assert not (ref_path / "__pycache__").exists()
    assert not (ref_path / ".tool_cache").exists()
    assert not (ref_path / "sub" / ".tool_cache" / "file.pyc").exists()
    assert not (ref_path / "sub" / "__pycache__").exists()
    assert not (ref_path / "sub" / ".cache").exists()


def test_excludes(tmp_path: Path):
    """Text Excludes."""
    ref_path = Path.cwd() / "tests" / "refdata" / "tests.test_main" / "test_excludes"

    (tmp_path / "file.txt").touch()
    (tmp_path / "file.csv").touch()
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "file.pyc").touch()
    (tmp_path / ".tool_cache").mkdir()
    (tmp_path / ".tool_cache" / "file.pyc").touch()

    (ref_path / "__pycache__").mkdir(exist_ok=True)
    (ref_path / "__pycache__" / "file.pyc").touch()

    configure(ref_update=False)
    assert_refdata(test_excludes, tmp_path, excludes=("*.txt",))

    assert (tmp_path / "file.txt").exists()
    assert (tmp_path / "file.csv").exists()
    assert (tmp_path / "__pycache__" / "file.pyc").exists()
    assert (tmp_path / ".tool_cache" / "file.pyc").exists()
    assert not (ref_path / "file.txt").exists()
    assert (ref_path / "file.csv").exists()
    assert (ref_path / "__pycache__").exists()
    assert not (ref_path / ".tool_cache").exists()


def test_assert_paths(tmp_path):
    """Test Assert Paths."""
    ref_path = tmp_path / "ref"
    ref_path.mkdir()
    (ref_path / "file.txt").write_text("One\n")

    one_path = tmp_path / "one"
    one_path.mkdir()
    (one_path / "file.txt").write_text("One\n")

    other_path = tmp_path / "other"
    other_path.mkdir()
    (other_path / "file.txt").write_text("other\n")

    assert_paths(ref_path, one_path)

    with raises(AssertionError):
        assert_paths(ref_path, other_path)
