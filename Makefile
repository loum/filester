.SILENT:
.DEFAULT_GOAL := help

MAKESTER__INCLUDES := py docker versioning docs

include makester/makefiles/makester.mk

#
# Makester overrides.
#
MAKESTER__VERSION_FILE := $(MAKESTER__PYTHON_PROJECT_ROOT)/VERSION

#
# Local Makefile targets.
#
_venv-init: py-venv-clear py-venv-init

# Build the local development environment.
init-dev: _venv-init py-install-makester
	MAKESTER__PIP_INSTALL_EXTRAS=dev $(MAKE) py-install-extras

# Streamlined production packages.
init: _venv-init
	$(MAKE) py-install

TESTS := tests
tests:
	$(MAKESTER__PYTHON) -m pytest\
 --override-ini log_cli=true\
 --override-ini junit_family=xunit2\
 --log-cli-level=INFO -svv\
 --exitfirst\
 --cov-config .coveragerc\
 --pythonwarnings ignore\
 --cov src\
 --junitxml junit.xml\
 $(TESTS)

help: makester-help
	@echo "(Makefile)\n\
  init                 Build the local Python-based virtual environment\n\
  tests                Run code test suite\n"

.PHONY: help tests docs
