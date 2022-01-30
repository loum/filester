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
 pypi-validate\
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
	@sphinx-build -b html docsource docs

docs-live:
	cd docs; $(PYTHON) -m http.server 8889 --bind 127.0.0.1

package: WHEEL=.wheelhouse
package: APP_ENV=prod

version:
	$(info ### AssemblySemFileVer: $(RELEASE_VERSION))

deps:
	pipdeptree

lint:
	-@pylint $(MAKESTER__PROJECT_DIR)/src

pypi-build: APP_ENV=prod
pypi-build:
	$(info ### Clearing dist/*)
	rm -fr dist/*
	$(info ### Create a source archive and wheel for package "$(MAKESTER__PROJECT_NAME)")
	$(PYTHON) -m build --wheel --sdist

pypi-validate:
	$(info ### Validate package "$(MAKESTER__PROJECT_NAME)")
	twine check\
 dist/$(MAKESTER__PROJECT_NAME)-$(RELEASE_VERSION)-py3-none-any.whl\
 dist/$(MAKESTER__PROJECT_NAME)-$(RELEASE_VERSION).tar.gz

help: makester-help python-venv-help
	@echo "(Makefile)\n\
  init                 Build the local Python-based virtual environment\n\
  deps                 Display PyPI package dependency tree\n\
  lint                 Lint the code base\n\
  version              Get latest package release version\n\
  tests                Run code test suite\n\
  docs                 Generate code based docs with Sphinx\n\
  docs-live            View docs via web browser\n\
  pypi-build           Create a source archive and wheel for package \"$(MAKESTER__PROJECT_NAME)\"\n\
  pypi-validate        Validate package \"$(MAKESTER__PROJECT_NAME)\"\n"

.PHONY: help tests docs
