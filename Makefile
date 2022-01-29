.SILENT:
.DEFAULT_GOAL := help

include makester/makefiles/makester.mk
include makester/makefiles/docker.mk
include makester/makefiles/python-venv.mk

export PATH := 3env/bin:$(PATH)
export PYTHONPATH := src

VARS_TARGETS := help\
 init\
 package\
 pypi-build\
 version
# Needs Docker and https://hub.docker.com/r/gittools/gitversion/
ifeq ($(MAKECMDGOALS), $(filter $(MAKECMDGOALS), $(VARS_TARGETS)))
export RELEASE_VERSION := $(shell $(DOCKER) run --rm\
 -v "$(MAKESTER__PROJECT_DIR):/$(MAKESTER__PROJECT_NAME)"\
 gittools/gitversion:latest /$(MAKESTER__PROJECT_NAME) |\
 jq .AssemblySemFileVer | sed 's/"//g')
endif

# APP_ENV is used in setup.py.
ifndef APP_ENV
export APP_ENV := local
else
export APP_ENV := $(APP_ENV)
endif

init: clear-env pip-editable

# Define the default test suit to run.
TESTS := tests
tests:
	$(PYTHON) -m pytest\
 -o log_cli=true\
 --log-cli-level=INFO -svv\
 --exitfirst --cov-config .coveragerc\
 --pythonwarnings ignore --cov src\
 -o junit_family=xunit2\
 --junitxml junit.xml $(TESTS)

docs:
	@sphinx-build -b html docs/source docs/build

package: WHEEL=.wheelhouse
package: APP_ENV=prod

version:
	$(info ### AssemblySemFileVer: $(RELEASE_VERSION))

deps:
	pipdeptree

lint:
	-@pylint $(MAKESTER__PROJECT_DIR)/src

pypi-build:
	$(PYTHON) setup.py sdist bdist_wheel

help: makester-help python-venv-help
	@echo "(Makefile)\n\
  init                 Build the local Python-based virtual environment\n\
  deps                 Display PyPI package dependency tree\n\
  lint                 Lint the code base\n\
  version              Get latest package release version\n\
  tests                Run code test suite\n\
  pypi-build           Create a source archive and wheel for package \"$(MAKESTER__PROJECT_NAME)\"\n"

.PHONY: help tests docs
