# Filester: generic, file based utilities and helpers

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [(macOS Users only) upgrading GNU `make`](#macos-users-only-upgrading-gnu-make)
  - [Creating the local environment](#creating-the-local-environment)
  - [Local environment maintenance](#local-environment-maintenance)
- [Help](#help)
- [Running the Test Harness](#running-the-test-harness)

## Overview
Find yourself running the same file based operations over and over again in your projects?  Yeah, annoying. As a result, this package is a grouping of common file operation facilities which delegate the package inclusion to `pip` and PyPI. One less thing to worry about ...

See [Filester's documentation](https://loum.github.io/filester/) for more information.

[top](#filester-generic-file-based-utilities-and-helpers)

## Prerequisites
- [GNU make](https://www.gnu.org/software/make/manual/make.html)
- Python 3 Interpreter. [We recommend installing pyenv](https://github.com/pyenv/pyenv)
- [Docker](https://www.docker.com/)

[top](#filester-generic-file-based-utilities-and-helpers)

## Getting Started
[Makester](https://loum.github.io/makester/) is used as the Integrated Developer Platform.

### (macOS Users only) upgrading GNU `make`
Follow [these notes](https://loum.github.io/makester/macos/#upgrading-gnu-make-macos) to get [GNU make](https://www.gnu.org/s
oftware/make/manual/make.html).

### Creating the local environment
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
make init-dev
```

### Local environment maintenance
Keep [Makester project](https://github.com/loum/makester.git) up-to-date with:
```
git submodule update --remote --merge
```

[top](#filester-generic-file-based-utilities-and-helpers)

## Help
There should be a `make` target to get most things done. Check the help for more information:
```
make help
```

[top](#filester-generic-file-based-utilities-and-helpers)

## Running the Test Harness
We use [pytest](https://docs.pytest.org/en/latest/). To run the tests:
```
make tests
```

---
[top](#filester-generic-file-based-utilities-and-helpers)
