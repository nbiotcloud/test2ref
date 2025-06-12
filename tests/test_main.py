#
# MIT License
#
# Copyright (c) 2024-2025 nbiotcloud
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
import re
import site
import sys
from pathlib import Path
from unittest.mock import patch

from pytest import mark, raises

from test2ref import (
    CONFIG,
    DEFAULT_EXCLUDES,
    DEFAULT_REF_PATH,
    DEFAULT_REF_UPDATE,
    Replacements,
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

        configure(add_excludes=("c", "d"))
        assert CONFIG["excludes"] == ("a", "b", "c", "d")

        configure(rm_excludes=("b", "d"))
        assert CONFIG["excludes"] == ("a", "c")

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
    one_path = tmp_path / "one" / "de-ep"
    inside_path = one_path / "inside"
    other_path = tmp_path / "oth-er"
    altsep_path = (one_path / "alt-sep").as_posix()
    one_path_str = str(one_path)

    one_path.mkdir(parents=True)
    (one_path / "file.txt").write_text(f"""\
Something
Over Multiple Lines
With {one_path}
With {one_path}/inside
With {one_path!s}
With {one_path!s}/inside
With {one_path_str!r}
With {inside_path}
With {inside_path}/mixed
{other_path} too
{other_path}/mixed too
{altsep_path}
{altsep_path}/mixed
""")

    configure(ref_update=False)
    replacements: Replacements = [
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


def test_path_replacements(tmp_path):
    """Path Replacements."""
    replacements = [
        ("one", "two"),
        ("three", "four"),
    ]
    deep_path = tmp_path / "someone" / "has" / "three" / "dirs"
    deep_path.mkdir(parents=True)
    (deep_path / "file").touch()
    (deep_path / "empty").mkdir()
    (tmp_path / "someone" / "has" / "three.txt").touch()

    configure(ref_update=True)
    assert_refdata(test_path_replacements, tmp_path, replacements=replacements)

    assert (tmp_path / "someone" / "has" / "three" / "dirs" / "file").exists()
    assert (tmp_path / "someone" / "has" / "three.txt").exists()

    ref_path = Path.cwd() / "tests" / "refdata" / "tests.test_main" / "test_path_replacements"
    assert (ref_path / "sometwo" / "has" / "four" / "dirs" / "file").exists()
    assert (ref_path / "sometwo" / "has" / "four.txt").exists()
    assert not (ref_path / "sometwo" / "has" / "four" / "dirs" / "empty").exists()


def test_path_abs(tmp_path):
    """Explicit Absolute Path."""
    ref_path = tmp_path / "ref"
    gen_path = tmp_path / "gen"
    gen_path.mkdir()

    assert not (ref_path / "file.txt").exists()
    (gen_path / "file.txt").write_text("Content")

    configure(ref_update=True)
    assert_refdata(ref_path, gen_path)

    assert (ref_path / "file.txt").read_text() == "Content"


def test_path_rel(tmp_path):
    """Explicit Relative Path."""
    ref_path = tmp_path / "ref"
    gen_path = tmp_path / "gen"
    gen_path.mkdir()

    assert not (ref_path / "file.txt").exists()
    (gen_path / "file.txt").write_text("Content")

    configure(ref_update=True, ref_path=tmp_path)
    assert_refdata(Path("ref"), gen_path)

    assert (ref_path / "file.txt").read_text() == "Content"


def test_flavor(tmp_path):
    """Flavor."""
    ref_path = tmp_path / "ref"
    gen_path = tmp_path / "gen"
    gen_path.mkdir()

    (gen_path / "file.txt").write_text("Content")

    configure(ref_update=True)
    assert_refdata(ref_path, gen_path, flavor="one")

    assert not (ref_path / "file.txt").exists()
    assert (ref_path / "one" / "file.txt").read_text() == "Content"


def test_regex(tmp_path):
    """Regular Expression Support."""
    ref_path = tmp_path / "ref"
    gen_path = tmp_path / "gen"
    gen_path.mkdir()

    (gen_path / "file.txt").write_text("""\
Hello World 1
Hello Mars 2
Hello Venus 3
""")

    replacements = ((re.compile(r"Hello [A-z]+"), "Hello PLANET"),)

    configure(ref_update=True)
    assert_refdata(ref_path, gen_path, replacements=replacements)

    assert (
        (ref_path / "file.txt").read_text()
        == """\
Hello PLANET 1
Hello PLANET 2
Hello PLANET 3
"""
    )


def test_site_home(tmp_path):
    """SITE + HOME Replacement."""
    ref_path = tmp_path / "ref"
    gen_path = tmp_path / "gen"
    ref_path.mkdir()
    gen_path.mkdir()

    paths = (*site.getsitepackages(), site.getusersitepackages())

    def variants(base):
        return str(base), Path(base), Path(base) / "sub"

    with (gen_path / "file.txt").open("w") as file:
        for path in paths:
            for variant in variants(path):
                file.write(f"{variant}\n")
        for variant in variants(Path.home()):
            file.write(f"{variant}\n")

    with (ref_path / "file.txt").open("w") as file:
        for _ in paths:
            for variant in variants("$SITE"):
                line = variant.as_posix() if isinstance(variant, Path) else variant
                file.write(f"{line}\n")
        for variant in variants("$HOME"):
            line = variant.as_posix() if isinstance(variant, Path) else variant
            file.write(f"{line}\n")

    configure(ref_update=False, ref_path=ref_path)
    assert_refdata(ref_path, gen_path)
