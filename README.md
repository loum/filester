# Filester: generic, file based utilities and helpers
- [Overview](#Overview)
- [Prequisites](#Prerequisites)
  - [Upgrading GNU Make (macOS)](#Upgrading-GNU-Make-(macOS))
- [Getting Started](#Getting-Started)
  - [Help](#Help)
  - [Building the Local Environment](#Building-the-Local-Environment)
    - [Local Environment Maintenance](#Local-Environment-Maintenance)
  - [Running the Test Harness](#Running-the-Test-Harness)
- [PyPI Packaging](#PyPI-Packaging)
- [Build the Documentation](#Build-the-Documentation)
- [Useful Commands](#Useful-Commands)
- [FAQs](#FAQs)

## Overview
Find yourself running the same file based operations over and over again in your projects?  Yeah, annoying.  As a result, this package is a grouping of common file operation facilities which delegate the package inclusion to `pip` and PyPI.  One less thing to worry about ...

## Prerequisites
- [GNU make](https://www.gnu.org/software/make/manual/make.html)
- Python 3 Interpreter [(we recommend installing pyenv)](https://github.com/pyenv/pyenv)
- [Docker](https://www.docker.com/)

## Getting Started

### Building the Local Environment
Get the code and change into the top level `git` project directory:
```
git clone git@github.com:loum/filester.git && cd filester
```
> **_NOTE:_** Run all commands from the top-level directory of the `git` repository.

For first-time setup, prime the [Makester project](https://github.com/loum/makester.git):
```
git submodule update --init
```
Initialise the environment:
```
make init
```
#### Local Environment Maintenance
Keep [Makester project](https://github.com/loum/makester.git) up-to-date with:
```
git submodule update --remote --merge
```
### Help
There should be a `make` target to get most things done.  Check the help for more information:
```
make help
```
### Running the Test Harness
Tests are good.  We use [pytest](https://docs.pytest.org/en/6.2.x/).  To run the tests:
```
make tests
```
## PyPI Packaging
To build a new PyPI ready package:
```
make pypi-build
```
To validate the package:
```
make pypi-validate
```

## Build the Documentation
Project documentation is self contained under the ``doc/source`` directory that is managed with [Sphinx](https://www.sphinx-doc.org/en/master/).  To build the documentation locally::
```
make docs
```
To view the docs from within your own environment::
```
make docs-live
```
> **_Note:_** The web server will block your CLI and all activity will be logged to the console.  To end serving pages, just `Ctrl-C``

With your web browser navigate to [http://localhost:8889](http://localhost:8889).

Documentation is also served from the `main` branch via GitHub pages at [https://loum.github.io/filester/](https://loum.github.io/filester/)

## Useful Commands
### `make init`
Rebuilds your local Python virtual environment and get the latest package dependencies.

### `make py`
Start the `python` interpreter in virtual environment context.  This will give you access to all of your PyPI package dependencies.

### `make lint`
Lint the code base with `pylint`.

### `make deps`
Display PyPI package dependency tree.

## FAQs
***Q. Why is the default make on macOS so old?***
Apple seems to have an issue with licensing around GNU products: more specifically to the terms of the GPLv3 license agreement. It is unlikely that Apple will provide current versions of utilities that are bound by the GPLv3 licensing constraints.

---
[top](#Filester:-generic- file based-utilities-and-helpers)
