pySMART
===========

Copyright (C) 2021-2023 [Rafael Leira](https://github.com/ralequi)\
Copyright (C) 2021 [Truenas team](https://www.truenas.com/)\
Copyright (C) 2015 Marc Herndon

Development
-----------

To run the tests, or to contribute to pySMART, you will have to set up a
development environment.

Our development environment will consist of a virtual environment, with the
installation and development dependencies installed.

See the [Python documentation] for more on creating and using virtual
environment.

This document will assume a Linux environment.

The steps are:

1. Clone this repository, go there
1. Create a virtualenv and activate it
1. Install the dependencies
1. Run the tests

- Go where you want to clone the repository, clone it, go there:

```bash
$ cd <wherever you want to clone the repository>
$ git clone https://github.com/truenas/py-SMART

Cloning into 'py-SMART'...
remote: Enumerating objects: 2243, done.
remote: Counting objects: 100% (839/839), done.
remote: Compressing objects: 100% (362/362), done.
remote: Total 2243 (delta 544), reused 743 (delta 463), pack-reused 1404
Receiving objects: 100% (2243/2243), 674.95 KiB | 2.38 MiB/s, done.
Resolving deltas: 100% (1518/1518), done.

$ cd py-SMART
```

- Create a virtualenv and activate it

    ```bash
    $ python -m venv .venv
    $ source .venv/bin/activate
    (.venv) $
    ```

    We use `.venv` for the directory name of the virtualenv by convention.
    Any other legal directory name is fine; we'll assume `.venv`.

- Update pip and setuptools

    ```bash
    $(.venv) $ python -m pip install --upgrade pip setuptools

    Requirement already satisfied: pip in <...>/.venv/lib/python3.12/site-packages (23.1)
    Collecting pip
    Using cached pip-24.0-py3-none-any.whl (2.1 MB)
    Requirement already satisfied: setuptools in <...>/.venv/lib/python3.12/site-packages (68.0.0)
    Collecting setuptools
    Downloading setuptools-69.5.1-py3-none-any.whl (894 kB)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 894.6/894.6 kB 6.1 MB/s eta 0:00:00
    Installing collected packages: setuptools, pip
    Attempting uninstall: setuptools
        Found existing installation: setuptools 68.0.0
        Uninstalling setuptools-68.0.0:
        Successfully uninstalled setuptools-68.0.0
    Attempting uninstall: pip
        Found existing installation: pip 23.1
        Uninstalling pip-23.1:
        Successfully uninstalled pip-23.1
    Successfully installed pip-24.0 setuptools-69.5.1
    ```

- Install the package including development dependencies

    ```bash
    $(.venv) $ python -m pip install --editable .[dev]
    ```

- Run the tests

    ```bash
    $(.venv) $ pytest
    =============== test session starts =====================================
    platform linux -- Python 3.12.2, pytest-8.1.1, pluggy-1.5.0
    rootdir: <...>/py-SMART
    configfile: pyproject.toml
    plugins: cov-5.0.0
    collected 184 items
    < test file names, lots and lots of dots>
    =============== 184 passed in 0.99s =====================================
    ```

**That's it -- you're ready to start developing on pySMART!**

[Python documentation]: https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#create-and-use-virtual-environments
