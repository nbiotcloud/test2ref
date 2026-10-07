[![PyPI Version](https://badge.fury.io/py/test2ref.svg)](https://badge.fury.io/py/test2ref)
[![Python Build](https://github.com/nbiotcloud/test2ref/actions/workflows/main.yml/badge.svg)](https://github.com/nbiotcloud/test2ref/actions/workflows/main.yml)
[![Documentation](https://readthedocs.org/projects/test2ref/badge/?version=stable)](https://test2ref.readthedocs.io/en/stable/)
[![Coverage Status](https://coveralls.io/repos/github/nbiotcloud/test2ref/badge.svg?branch=main)](https://coveralls.io/github/nbiotcloud/test2ref?branch=main)
[![python-versions](https://img.shields.io/pypi/pyversions/test2ref.svg)](https://pypi.python.org/pypi/test2ref)

# Testing Against Learned Reference Data

* [Documentation](https://test2ref.readthedocs.io/en/stable/)
* [PyPI](https://pypi.org/project/test2ref/)
* [Sources](https://github.com/nbiotcloud/test2ref)
* [Issues](https://github.com/nbiotcloud/test2ref/issues)

Installing it is pretty easy:

```bash
pip install test2ref
```

## Pytest Plugin

The pytest plugin is loaded automatically when `test2ref` and pytest are installed.
Use `--test2ref` to update reference data, or `--no-test2ref` to compare without
updating:

```bash
pytest --test2ref
pytest --no-test2ref
```

If neither option is given, the existing default is preserved: reference data is
updated when a `.test2ref` file exists in the project root.

::: test2ref
