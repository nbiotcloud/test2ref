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

"""Compare generated output with learned reference data."""

import site
import subprocess
import sys
from collections.abc import Callable, Iterable
from filecmp import dircmp
from pathlib import Path
from shutil import copytree, ignore_patterns, rmtree
from tempfile import TemporaryDirectory
from typing import Any

from ._config import CONFIG, ENCODING, ENCODING_ERRORS, PRJ_PATH, Excludes, Replacements, StrReplacements
from ._replace import _replace_content, _replace_path


def assert_refdata(
    arg: Callable | Path,
    path: Path,
    capsys: Any = None,
    caplog: Any = None,
    replacements: Replacements | None = None,
    excludes: Iterable[str] | None = None,
    flavor: str = "",
    known: Path | None = None,
) -> None:
    """
    Compare Output of `arg` generated at `path` with reference.

    Use `replacements` to mention things which vary from test to test.
    `path` and the project location are already replaced by default.

    Args:
        arg: Test Function or Path to reference data
        path: Path with generated files to be compared.

    Keyword Args:
        capsys: pytest `capsys` fixture. Include `stdout`/`stderr` too.
        caplog: pytest `caplog` fixture. Include logging output too.
        replacements: pairs of things to be replaced.
        excludes: Files and directories to be excluded.
        flavor: Flavor for different variants.
        known: Path with directories and files which are known and excluded as soon as they are identical.

    !!! example "Minimal Example"

        ```python
        def test_example(tmp_path):
            (tmp_path / "file.txt").write_text("Content")
            assert_refdata(test_example, tmp_path)
        ```

    !!! example "Full Example"

        ```python
        import logging

        def test_example(tmp_path, capsys, caplog):
            (tmp_path / "file.txt").write_text("Content")

            # print on standard-output - captured by capsys
            print("Hello World")

            # logging - captured by caplog
            logging.getLogger().warning("test")

            assert_refdata(test_example, tmp_path, capsys=capsys, caplog=caplog)
        ```

    The following replacements are included automatically:

    * Python Installation Directories: `$SITE`
    * Current Working Directory: `$PRJ`
    * Argument `path`: `$GEN`
    * Home Directory: `$HOME`
    """
    ref_basepath: Path = CONFIG["ref_path"]  # type: ignore[assignment]
    if isinstance(arg, Path):
        ref_path = ref_basepath / arg
    else:
        ref_path = ref_basepath / arg.__module__ / arg.__name__
    if flavor:
        ref_path = ref_path / flavor
    ref_path.mkdir(parents=True, exist_ok=True)
    rplcs: Replacements = replacements or ()  # type: ignore[assignment]
    path_rplcs: StrReplacements = [(srch, rplc) for srch, rplc in rplcs if isinstance(srch, str)]
    sitepaths = [*site.getsitepackages(), site.getusersitepackages(), sys.prefix]
    gen_rplcs: Replacements = [
        *((Path(path) / "Lib" / "site-packages", "$SITE") for path in sitepaths),
        *((Path(path), "$SITE") for path in sitepaths),
        (PRJ_PATH, "$PRJ"),
        (path, "$GEN"),
        *rplcs,
        (Path.home(), "$HOME"),
    ]
    gen_excludes: Excludes = (*CONFIG["excludes"], *(excludes or []))

    with TemporaryDirectory() as tmp_gen_dir:
        gen_path = Path(tmp_gen_dir)

        ignore = ignore_patterns(*gen_excludes)
        copytree(path, gen_path, dirs_exist_ok=True, ignore=ignore)

        _replace_path(gen_path, path_rplcs)

        if capsys:
            captured = capsys.readouterr()
            (gen_path / "stdout.txt").write_text(captured.out, encoding=ENCODING, errors=ENCODING_ERRORS)
            (gen_path / "stderr.txt").write_text(captured.err, encoding=ENCODING, errors=ENCODING_ERRORS)

        if caplog:
            logpath = gen_path / "logging.txt"
            with logpath.open("w", encoding=ENCODING, errors=ENCODING_ERRORS) as file:
                for record in caplog.records:
                    file.write(f"{record.levelname:7s}  {record.name}  {record.message}\n")
            caplog.clear()

        _replace_content(gen_path, gen_rplcs)

        if known:
            missing = _remove_known(known, gen_path)
            if missing:
                missingpath = gen_path / "missing.txt"
                with missingpath.open("w", encoding=ENCODING, errors=ENCODING_ERRORS) as file:
                    for miss in missing:
                        file.write(f"{miss.as_posix()}\n")

        _remove_empty_dirs(gen_path)

        if CONFIG["ref_update"]:
            # Nearly atomic update of ref_path.
            with TemporaryDirectory(dir=ref_path.parent) as tmp_ref_dir:
                tmp_ref_path_new = Path(tmp_ref_dir) / "new"
                tmp_ref_path_old = Path(tmp_ref_dir) / "old"
                # Copy to the destination file system.
                copytree(gen_path, tmp_ref_path_new)
                # Swap in the new reference and remove obsolete files.
                ref_path.rename(tmp_ref_path_old)
                tmp_ref_path_new.rename(ref_path)
                rmtree(tmp_ref_path_old, ignore_errors=True)

        assert_paths(ref_path, gen_path, excludes=excludes)


def assert_paths(ref_path: Path, gen_path: Path, excludes: Iterable[str] | None = None) -> None:
    """
    Compare Output of `ref_path` with `gen_path`.

    Args:
        ref_path: Path with reference files to be compared.
        gen_path: Path with generated files to be compared.

    Keyword Args:
        excludes: Files and directories to be excluded.
    """
    diff_excludes: Excludes = (*CONFIG["excludes"], *(excludes or []))
    try:
        cmd = ["diff", "-ru", "--strip-trailing-cr", str(ref_path), str(gen_path)]
        for exclude in diff_excludes:
            cmd.extend(("--exclude", exclude))
        if CONFIG["ignore_spaces"]:
            cmd.append("-b")
        subprocess.run(cmd, check=True, capture_output=True)  # noqa: S603
    except subprocess.CalledProcessError as error:
        raise AssertionError(error.stdout.decode("utf-8")) from None


def _remove_empty_dirs(path: Path) -> None:
    """Remove Empty Directories within ``path``."""
    for sub_path in tuple(path.glob("**/*")):
        if not sub_path.exists() or not sub_path.is_dir():
            continue
        sub_dir = sub_path
        while sub_dir != path:
            is_empty = not any(sub_dir.iterdir())
            if is_empty:
                sub_dir.rmdir()
                sub_dir = sub_dir.parent
            else:
                break


def _remove_known(known: Path, path: Path, base: Path | None = None) -> list[Path]:
    missing: list[Path] = []
    base = base or Path()
    cmp = dircmp(known, path)
    for samefile in cmp.same_files:
        (path / samefile).unlink()
    missing.extend(base / left for left in sorted(cmp.left_only))
    for samedir in sorted(cmp.common_dirs):
        missing.extend(_remove_known(known / samedir, path / samedir, base=base / samedir))
    return missing
